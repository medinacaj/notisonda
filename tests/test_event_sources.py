"""Official direct calendars use the same validated agenda and bounded transport."""
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import events
if importlib.util.find_spec('event_sources'):
    import event_sources
else:
    event_sources = None

NOW = datetime(2026, 10, 26, 12, tzinfo=timezone.utc)
SOURCE = {'id': 'direct-venue', 'name': 'Teatro', 'category': '07 - Concepción',
          'url': 'https://venue.example/agenda/', 'website': 'https://venue.example/',
          'timezone': 'America/Santiago', 'hosts': ['venue.example'], 'max_pages': 4,
          'preference_source_id': 'rss-parent'}


def jsonld(objects):
    return '<script type="application/ld+json">' + json.dumps(objects) + '</script>'


def activity(**updates):
    return {'@type': 'MusicEvent', 'name': 'Concierto de otoño',
            'url': 'https://venue.example/concierto', 'startDate': '2026-11-01', **updates}


def calendar(*lines):
    return '\r\n'.join(['BEGIN:VCALENDAR', 'VERSION:2.0', 'BEGIN:VEVENT',
                        'UID:stable-concert@example', 'SUMMARY:Concierto', *lines,
                        'END:VEVENT', 'END:VCALENDAR'])


class DirectParserTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(event_sources, 'Direct source parser must exist')

    def parse(self, text, kind='text/html'):
        return event_sources.parse_document(text, kind, SOURCE['url'], SOURCE, NOW)

    def test_jsonld_listing_keeps_each_own_event_and_explicit_evidence(self):
        rows = self.parse(jsonld({'@graph': [activity(), activity(url='/segundo', name='Obra teatral',
                                **{'@type': 'TheaterEvent', 'startDate': '2026-11-02'})]}))
        self.assertEqual([row['start_date'] for row in rows], ['2026-11-01', '2026-11-02'])
        self.assertEqual(rows[1]['event_type'], 'Teatro')
        self.assertEqual(rows[0]['date_evidence']['url'], 'https://venue.example/agenda/')
        self.assertEqual(rows[0]['preference_source_id'], 'rss-parent')
        events.validate_document(events.merge_events(None, rows, [], NOW))

    def test_news_embedded_events_and_unregistered_urls_do_not_become_activities(self):
        page = jsonld({'@type': 'NewsArticle', 'datePublished': '2026-11-01',
                       'mainEntity': activity()}) + jsonld(activity(url='https://other.example/concierto'))
        self.assertEqual(self.parse(page), [])

    def test_conflicting_dates_on_same_detail_page_are_pending(self):
        rows = self.parse(jsonld([activity(), activity(startDate='2026-11-03')]))
        self.assertEqual(len(rows), 1)
        self.assertIsNone(rows[0]['start_date'])
        self.assertIsNone(rows[0]['date_evidence'])

    def test_yearless_dates_and_pubdate_never_confirm(self):
        row = self.parse(jsonld(activity(startDate='11-01', datePublished='2026-11-01')))[0]
        self.assertIsNone(row['start_date'])
        self.assertEqual(row['reason'], 'date_unverified')

    def test_explicit_calendar_link_is_discovered_only_on_registered_hosts(self):
        links = event_sources.discover_links(
            '<a href="/concierto">Concierto</a><link rel="alternate" type="text/calendar" href="/agenda.ics">'
            '<a href="https://other.example/agenda.ics">Agenda</a><a href="/privacy">Privacidad</a>',
            SOURCE['url'], SOURCE)
        self.assertEqual(links, ['https://venue.example/concierto', 'https://venue.example/agenda.ics'])

    def test_ics_tzid_and_utc_convert_to_source_local_day(self):
        for value in ('DTSTART;TZID=Pacific/Kiritimati:20261101T003000', 'DTSTART:20261101T010000Z'):
            with self.subTest(value=value):
                row = self.parse(calendar(value), 'text/calendar')[0]
                self.assertEqual(row['start_date'], '2026-10-31')
                self.assertEqual(row['date_evidence']['kind'], 'calendar')

    def test_ics_all_day_end_is_exclusive_and_remains_active_until_local_end(self):
        row = self.parse(calendar('DTSTART;VALUE=DATE:20261101', 'DTEND;VALUE=DATE:20261104'), 'text/calendar')[0]
        self.assertEqual((row['start_date'], row['end_date']), ('2026-11-01', '2026-11-03'))
        self.assertTrue(events.is_upcoming(row, datetime(2026, 11, 4, 2, 59, tzinfo=timezone.utc)))
        self.assertFalse(events.is_upcoming(row, datetime(2026, 11, 4, 3, 0, tzinfo=timezone.utc)))

    def test_ics_uid_survives_reschedule_title_change_and_cancellation(self):
        first = self.parse(calendar('DTSTART;VALUE=DATE:20261101'), 'text/calendar')[0]
        changed = self.parse(calendar('DTSTART;VALUE=DATE:20261102', 'STATUS:CANCELLED'), 'text/calendar')[0]
        self.assertEqual(first['id'], changed['id'])
        self.assertEqual(changed['status'], 'cancelled')
        previous = events.merge_events(None, [first], [], NOW)
        merged = events.merge_events(previous, [changed], [], NOW)
        self.assertEqual(len(merged['items']), 1)
        self.assertFalse(events.is_upcoming(merged['items'][0], NOW))

    def test_timed_calendar_end_at_midnight_does_not_add_an_activity_day(self):
        row=self.parse(calendar('DTSTART;TZID=America/Santiago:20261101T200000',
                                'DTEND;TZID=America/Santiago:20261102T000000'),'text/calendar')[0]
        self.assertEqual(row['end_date'],'2026-11-01')
        self.assertFalse(events.is_upcoming(row,datetime(2026,11,2,15,tzinfo=timezone.utc)))
        invalid=self.parse(calendar('DTSTART:20261101T200000Z','DTEND:20261101T190000Z'),'text/calendar')[0]
        self.assertIsNone(invalid['start_date'])

    def test_uid_only_cancellation_updates_cached_event_without_inventing_title(self):
        first=self.parse(calendar('DTSTART;VALUE=DATE:20261101','URL:https://venue.example/concierto'),'text/calendar')
        previous=events.merge_events(None,first,[],NOW)
        update=self.parse(calendar('STATUS:CANCELLED').replace('SUMMARY:Concierto\r\n',''),'text/calendar')
        merged=events.merge_events(previous,update,[],NOW)
        row=(merged['items']+merged['pending'])[0]
        self.assertEqual(row['status'],'cancelled')
        self.assertEqual(row['title'],first[0]['title'])
        self.assertEqual(row['url'],first[0]['url'])
        self.assertFalse(events.merge_events(None,update,[],NOW)['pending'])

    def test_ics_bad_date_unknown_zone_and_unsupported_recurrence_stay_pending(self):
        for lines in [('DTSTART;VALUE=DATE:20260230',), ('DTSTART;TZID=Wrong/Zone:20261101T100000',),
                      ('DTSTART;VALUE=DATE:20261101', 'RRULE:FREQ=WEEKLY;COUNT=4')]:
            with self.subTest(lines=lines):
                row = self.parse(calendar(*lines), 'text/calendar')[0]
                self.assertIsNone(row['start_date'])
                self.assertIsNone(row['date_evidence'])

    def test_tribe_calendar_normalizes_all_day_and_cancelled(self):
        data = {'events': [{'id': 99, 'title': 'Concierto de cámara', 'url': 'https://venue.example/concierto',
                            'start_date': '2026-11-01 00:00:00', 'end_date': '2026-11-03 23:59:59',
                            'all_day': True, 'event_status': 'cancelled',
                            'venue': {'venue': 'Teatro', 'city': 'Concepción'}, 'cost': 'Gratis'}]}
        row = self.parse(json.dumps(data), 'application/json')[0]
        self.assertEqual((row['start_date'], row['end_date']), ('2026-11-01', '2026-11-03'))
        self.assertEqual(row['status'], 'cancelled')
        self.assertEqual(row['locality'], 'Concepción')
        self.assertIs(row['is_free'], True)


class _Response:
    def __init__(self, body=b'', kind='text/html', status=200):
        self.status_code=status;self.headers={'Content-Type':kind};self.encoding='utf-8';self.body=body;self.closed=False

    def iter_content(self, chunk_size):
        for position in range(0,len(self.body),chunk_size):yield self.body[position:position+chunk_size]

    def close(self):self.closed=True


class DirectCollectionTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(callable(getattr(event_sources,'collect_sources',None)), 'Bounded direct collection must exist')

    def test_one_failed_source_preserves_active_cache_and_other_source_results(self):
        import requests
        other={**SOURCE,'id':'other','url':'https://venue.example/other'}
        old=event_sources.parse_document(jsonld(activity()),'text/html',SOURCE['url'],SOURCE,NOW)[0]
        previous=events.merge_events(None,[old],[],NOW)
        def fetch(url,source):
            if source['id']==SOURCE['id']:raise requests.Timeout('offline')
            return 'text/html',jsonld(activity(url='/new',startDate='2026-11-05'))
        rows,states=event_sources.collect_sources([SOURCE,other],NOW,fetcher=fetch)
        doc=events.merge_events(previous,rows,states,NOW)
        self.assertEqual([s['status'] for s in doc['sources']],['error','ok'])
        self.assertEqual([x['start_date'] for x in doc['items']],['2026-11-01','2026-11-05'])

    def test_page_budget_bounds_discovery_and_marks_unattempted_source_error(self):
        other={**SOURCE,'id':'other','url':'https://venue.example/other'}
        def fetch(url,source):
            return 'text/html',jsonld(activity(url=url))+'<a href="/concierto-dos">Concierto</a>'
        rows,states=event_sources.collect_sources([SOURCE,other],NOW,fetcher=fetch,max_requests=1)
        self.assertEqual(len(rows),1)
        self.assertEqual([s['status'] for s in states],['ok','error'])
        self.assertIn('budget',states[1]['error'].lower())

    def test_discovered_ics_is_merged_instead_of_creating_second_document(self):
        def fetch(url,source):
            if url.endswith('agenda.ics'):return 'text/calendar',calendar('DTSTART;VALUE=DATE:20261101')
            return 'text/html','<link rel="alternate" type="text/calendar" href="/agenda.ics">'
        rows,states=event_sources.collect_sources([SOURCE],NOW,fetcher=fetch)
        doc=events.merge_events(None,rows,states,NOW)
        self.assertEqual(len(doc['items']),1)
        self.assertEqual(doc['items'][0]['date_evidence']['kind'],'calendar')
        self.assertEqual(doc['sources'][0]['status'],'ok')

    def test_fetch_rejects_private_robots_redirects_and_oversize(self):
        from unittest.mock import patch
        with patch('event_sources.collect.is_public_host',return_value=False):
            with self.assertRaises(ValueError):event_sources.fetch_document(SOURCE['url'],SOURCE)
        with patch('event_sources.collect.is_public_host',return_value=True), patch('event_sources.collect.page_image_allowed',return_value=False):
            with self.assertRaises(ValueError):event_sources.fetch_document(SOURCE['url'],SOURCE)
        for response in (_Response(status=302),_Response(body=b'x'*500001)):
            def get(url,**kwargs):
                if kwargs.get('allow_redirects') is not False:raise AssertionError('Network redirects must be disabled')
                return response
            with patch('event_sources.collect.is_public_host',return_value=True), patch('event_sources.collect.page_image_allowed',return_value=True),patch('event_sources.requests.get',side_effect=get):
                with self.assertRaises(ValueError):event_sources.fetch_document(SOURCE['url'],SOURCE)
            self.assertTrue(response.closed)

    def test_fetch_reading_real_response_produces_parsed_event(self):
        from unittest.mock import patch
        response=_Response(jsonld(activity()).encode())
        with patch('event_sources.collect.is_public_host',return_value=True), patch('event_sources.collect.page_image_allowed',return_value=True),patch('event_sources.requests.get',return_value=response):
            rows,states=event_sources.collect_sources([SOURCE],NOW)
        self.assertEqual(rows[0]['start_date'],'2026-11-01')
        self.assertEqual(states[0]['status'],'ok')
        self.assertTrue(response.closed)

    def test_config_rejects_unregistered_hosts_and_preserves_rss_preference_parent(self):
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'direct.json'
            config={'version':1,'sources':[{**SOURCE,'enabled':True,'official':True,
                    'preference_feed_url':'https://www.radioudec.cl/feed/'}]}
            path.write_text(json.dumps(config))
            sources=event_sources.load_sources(path,ROOT/'sources/feeds.opml')
            self.assertEqual(sources[0]['preference_source_id'],'4480e9b923e47f61')
            config['sources'][0]['hosts']=['other.example']
            path.write_text(json.dumps(config))
            with self.assertRaises(ValueError):event_sources.load_sources(path,ROOT/'sources/feeds.opml')


class DirectAgendaIntegrationTests(unittest.TestCase):
    def test_cli_opt_in_combines_rss_monagas_and_direct_sources_in_one_generation(self):
        import collect_events
        import tempfile
        from unittest.mock import patch
        generation='2026-10-26T12:00:00Z'
        rss=b'<rss version="2.0"><channel><item><title>Concierto de Monagas</title><link>https://laverdaddemonagas.com/concierto</link><description>El concierto se realizar\xc3\xa1 el 2 de noviembre de 2026.</description></item></channel></rss>'
        direct={**SOURCE,'enabled':True,'official':True}
        with tempfile.TemporaryDirectory() as folder:
            config=Path(folder)/'direct.json';config.write_text(json.dumps({'version':1,'sources':[direct]}))
            path=Path(folder)/'events.json'
            args=['--catalog',str(ROOT/'sources/feeds.opml'),'--config',str(ROOT/'sources/events.json'),
                  '--out',str(path),'--generation',generation]
            with patch('collect_events.fetch_feed',return_value=rss),patch('collect_events.fetch_event_page',return_value=None):
                with patch('event_sources.fetch_document',return_value=('text/html',jsonld(activity()))):
                    try:result=collect_events.main(args+['--direct-config',str(config)])
                    except SystemExit:self.fail('CLI must accept --direct-config')
                self.assertEqual(result,0)
                doc=json.loads(path.read_text())
                events.validate_document(doc)
                self.assertEqual(doc['generated_at'],generation)
                self.assertEqual(len(doc['sources']),11)
                self.assertTrue(any(row['timezone']=='America/Caracas' for row in doc['items']))
                self.assertTrue(any(row['source_id']=='direct-venue' for row in doc['items']))
                # Legacy CLI stays RSS-only and retains validated direct cache.
                def unexpected(*args,**kwargs):raise AssertionError('Direct fetch must be opt-in')
                with patch('event_sources.fetch_document',side_effect=unexpected):
                    self.assertEqual(collect_events.main(args),0)
                doc=json.loads(path.read_text())
                self.assertEqual(len(doc['sources']),10)
                self.assertTrue(any(row['source_id']=='direct-venue' for row in doc['items']))


class DirectRobustnessTests(unittest.TestCase):
    def test_shipped_catalog_collects_chile_and_biobio_without_touching_rss(self):
        path=ROOT/'sources/events-direct.json'
        self.assertTrue(path.exists(), 'Official direct catalog must be provided')
        sources=event_sources.load_sources(path,ROOT/'sources/feeds.opml')
        def fetch(url,source):
            target=source['url'].rstrip('/')+'/concierto'
            return 'text/html',jsonld(activity(url=target))
        rows,states=event_sources.collect_sources(sources,NOW,fetcher=fetch)
        doc=events.merge_events(None,rows,states,NOW)
        self.assertEqual({row['category'] for row in doc['items']},{'04 - Chile','07 - Concepción'})
        self.assertTrue(all(state['status']=='ok' for state in states))
        self.assertEqual(len({row['id'] for row in doc['items']}),len(doc['items']))

    def test_script_end_in_structured_title_is_plain_data(self):
        text=jsonld(activity(name='Concierto </script><b>anual</b>')).replace('</script><b>','\\u003c/script>\\u003cb>')
        # The publisher escapes '<' in its valid JSON-LD block.
        row=event_sources.parse_document(text,'text/html',SOURCE['url'],SOURCE,NOW)[0]
        self.assertEqual(row['start_date'],'2026-11-01')
        self.assertNotIn('<b>',row['title'])

    def test_truncated_ics_and_short_date_do_not_confirm_an_event(self):
        for text in (calendar('DTSTART;VALUE=DATE:2026111'),
                     calendar('DTSTART;VALUE=DATE:20261101').replace('END:VEVENT','')):
            rows=event_sources.parse_document(text,'text/calendar',SOURCE['url'],SOURCE,NOW)
            self.assertFalse(any(row['start_date'] for row in rows))


    def test_itemlist_events_are_extracted_without_promoting_embedded_news(self):
        text=jsonld({'@type':'ItemList','itemListElement':[{'@type':'ListItem','item':activity()},
                     {'@type':'ListItem','item':{'@type':'NewsArticle','mainEntity':activity(url='/other')}}]})
        rows=event_sources.parse_document(text,'text/html',SOURCE['url'],SOURCE,NOW)
        self.assertEqual([row['url'] for row in rows],['https://venue.example/concierto'])

    def test_same_detail_from_ics_and_jsonld_is_published_once(self):
        def fetch(url,source):
            if url.endswith('agenda.ics'):
                return 'text/calendar',calendar('DTSTART;VALUE=DATE:20261101','URL:https://venue.example/concierto')
            return 'text/html',jsonld(activity())+'<link rel="alternate" type="text/calendar" href="/agenda.ics">'
        rows,states=event_sources.collect_sources([SOURCE],NOW,fetcher=fetch)
        doc=events.merge_events(None,rows,states,NOW)
        self.assertEqual(len(doc['items']),1)
        self.assertEqual(doc['items'][0]['date_evidence']['kind'],'calendar')

    def test_relative_jsonld_identity_is_resolved_against_publisher_page(self):
        rows=event_sources.parse_document(jsonld(activity(url='events/concierto')),'text/html',SOURCE['url'],SOURCE,NOW)
        self.assertEqual(rows[0]['url'],'https://venue.example/agenda/events/concierto')
        self.assertEqual(rows[0]['start_date'],'2026-11-01')

    def test_explicit_jsonld_reschedule_keeps_date_and_calendar_identity(self):
        def fetch(url,source):
            if url.endswith('agenda.ics'):
                return 'text/calendar',calendar('DTSTART;VALUE=DATE:20261101','URL:https://venue.example/concierto')
            return 'text/html',jsonld(activity(startDate='2026-11-12',eventStatus='https://schema.org/EventRescheduled'))+'<link type="text/calendar" href="/agenda.ics">'
        rows,states=event_sources.collect_sources([SOURCE],NOW,fetcher=fetch)
        doc=events.merge_events(None,rows,states,NOW)
        self.assertEqual(len(doc['items']),1)
        self.assertEqual(doc['items'][0]['start_date'],'2026-11-12')
        self.assertEqual(doc['items'][0]['calendar_uid'],'stable-concert@example')

    def test_calendar_uid_absorbs_url_identity_and_survives_missing_calendar_feed(self):
        initial=event_sources.parse_document(jsonld(activity()),'text/html',SOURCE['url'],SOURCE,NOW)
        previous=events.merge_events(None,initial,[],NOW)
        ics=event_sources.parse_document(calendar('DTSTART;VALUE=DATE:20261101','URL:https://venue.example/concierto'),
                                         'text/calendar','https://venue.example/agenda.ics',SOURCE,NOW)
        merged=events.merge_events(previous,ics,[],NOW)
        self.assertEqual(len(merged['items']),1)
        self.assertEqual(merged['items'][0]['id'],ics[0]['id'])
        fallback=events.merge_events(merged,initial,[],NOW)
        self.assertEqual(len(fallback['items']),1)
        self.assertEqual(fallback['items'][0]['id'],ics[0]['id'])
        self.assertEqual(fallback['items'][0].get('calendar_uid'),'stable-concert@example')

    def test_undated_ics_cancellation_overrules_dated_jsonld_same_detail(self):
        def fetch(url,source):
            if url.endswith('agenda.ics'):
                return 'text/calendar',calendar('STATUS:CANCELLED','URL:https://venue.example/concierto')
            return 'text/html',jsonld(activity())+'<link rel="alternate" type="text/calendar" href="/agenda.ics">'
        rows,states=event_sources.collect_sources([SOURCE],NOW,fetcher=fetch)
        doc=events.merge_events(None,rows,states,NOW)
        self.assertEqual(doc['items'],[])
        self.assertEqual(len(doc['pending']),1)
        self.assertEqual(doc['pending'][0]['status'],'cancelled')

    def test_postponement_wins_conflicting_formats_without_retaining_active_date(self):
        def fetch(url,source):
            if url.endswith('agenda.ics'):
                return 'text/calendar',calendar('DTSTART;VALUE=DATE:20261101','URL:https://venue.example/concierto')
            return 'text/html',jsonld(activity(eventStatus='https://schema.org/EventPostponed'))+'<link rel="alternate" type="text/calendar" href="/agenda.ics">'
        rows,states=event_sources.collect_sources([SOURCE],NOW,fetcher=fetch)
        try:doc=events.merge_events(None,rows,states,NOW)
        except ValueError:self.fail('Conflicting formats must produce a valid postponed announcement')
        self.assertEqual(doc['items'],[])
        self.assertEqual(doc['pending'][0]['status'],'postponed')
        self.assertIsNone(doc['pending'][0]['date_evidence'])
