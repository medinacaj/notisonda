"""Public event details come only from structured evidence, never headlines."""
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import events

NOW = datetime(2026, 10, 26, 12, tzinfo=timezone.utc)
SOURCE = {'id': 'venue', 'name': 'Teatro', 'category': '07 - Concepción',
          'url': 'https://venue.example/', 'timezone': 'America/Santiago',
          'preference_source_id': 'rss-parent'}
ENTRY = {'link': 'https://venue.example/concierto', 'title': 'Concierto gratuito en Santiago'}


def extracted(**updates):
    obj = {'@type': 'MusicEvent', 'name': ENTRY['title'], 'url': ENTRY['link'],
           'startDate': '2026-11-01', **updates}
    html = '<script type="application/ld+json">' + json.dumps(obj) + '</script>'
    return events.extract_event(ENTRY, SOURCE, NOW, html=html)


class EventDetailTests(unittest.TestCase):
    def test_explicit_location_type_and_price_are_normalized(self):
        row = extracted(location={'name': 'Sala principal', 'address': {'addressLocality': 'Concepción'}},
                        offers={'price': '1500', 'priceCurrency': 'CLP'})
        self.assertEqual(row.get('locality'), 'Concepción')
        self.assertEqual(row.get('event_type'), 'Música')
        self.assertEqual(row.get('price_text'), '1500 CLP')
        self.assertIs(row.get('is_free'), False)
        self.assertEqual(row.get('preference_source_id'), 'rss-parent')

    def test_free_label_does_not_confirm_price_without_explicit_offer(self):
        self.assertIsNone(extracted().get('is_free'))
        self.assertIsNone(extracted().get('locality'))
        self.assertIsNone(extracted().get('price_text'))
        self.assertIs(extracted(isAccessibleForFree=True).get('is_free'), True)
        self.assertIs(extracted(offers=[{'price': 0}, {'price': '0.00'}]).get('is_free'), True)
        self.assertIsNone(extracted(offers=[{'price': 0}, {'price': 500}]).get('is_free'))

    def test_incomplete_repeat_preserves_verified_optional_details(self):
        row = extracted(location={'address': {'addressLocality': 'Concepción'}}, isAccessibleForFree=True)
        previous = events.merge_events(None, [row], [], NOW)
        repeat = events.extract_event({**ENTRY, 'ev_startdate': '2026-11-01'}, SOURCE, NOW)
        merged = events.merge_events(previous, [repeat], [], NOW)
        self.assertEqual(merged['items'][0].get('locality'), 'Concepción')
        self.assertIs(merged['items'][0].get('is_free'), True)

    def test_optional_fields_reject_wrong_types_and_overlong_values(self):
        document = events.merge_events(None, [extracted()], [], NOW)
        for name, value in [('locality', 'x' * 201), ('event_type', []), ('price_text', 0),
                            ('is_free', 1), ('preference_source_id', 'x' * 129)]:
            with self.subTest(field=name):
                invalid = copy.deepcopy(document)
                invalid['items'][0][name] = value
                with self.assertRaises(ValueError):
                    events.validate_document(invalid)

    def test_calendar_evidence_is_valid_and_can_confirm_reschedule(self):
        row = extracted()
        row['status'] = 'cancelled'
        previous = events.merge_events(None, [row], [], NOW)
        replacement = extracted(startDate='2026-11-02')
        replacement['date_evidence']['kind'] = 'calendar'
        merged = events.merge_events(previous, [replacement], [], NOW)
        self.assertEqual(merged['items'][0]['status'], 'scheduled')
        self.assertEqual(merged['items'][0]['start_date'], '2026-11-02')

    def test_offer_beyond_normalization_limit_cannot_make_mixed_prices_free(self):
        row=extracted(offers=[{'price':0}]*30+[{'price':500}])
        self.assertIsNone(row.get('is_free'))

    def test_conflicting_free_flag_and_mixed_or_paid_offers_stay_unknown(self):
        for updates in ({'isAccessibleForFree':True,'offers':[{'price':0},{'price':500}]},
                        {'isAccessibleForFree':True,'offers':{'price':500}},
                        {'isAccessibleForFree':False,'offers':{'price':0}}):
            with self.subTest(updates=updates):self.assertIsNone(extracted(**updates).get('is_free'))

    def test_new_conflicting_price_clears_cached_free_classification(self):
        previous=events.merge_events(None,[extracted(isAccessibleForFree=True)],[],NOW)
        for offers in ({'price':500}, [{'price':0},{'price':500}]):
            with self.subTest(offers=offers):
                update=extracted(isAccessibleForFree=True,offers=offers)
                document=events.merge_events(previous,[update],[],NOW)
                self.assertIsNone(document['items'][0]['is_free'])
                self.assertNotIn('_price_observed',document['items'][0])
