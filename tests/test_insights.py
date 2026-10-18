"""Señales editoriales del recolector: cobertura, temas en alza y feeds de salida."""
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import collect  # noqa: E402
import insights  # noqa: E402

NOW = datetime(2026, 10, 18, 12, tzinfo=timezone.utc)


def story(i, title, hours_ago, source, category='04 - Chile'):
    when = NOW - timedelta(hours=hours_ago)
    return {'id': f'id{i}', 'title': title, 'url': f'https://example.com/{i}', 'summary': 'Resumen',
            'published_at': collect.iso(when), 'first_seen_at': collect.iso(when), 'publisher': source,
            'source': source, 'source_ids': [source], 'categories': [category]}


class InsightsTests(unittest.TestCase):
    def test_grouped_story_keeps_each_outlet_headline(self):
        a = story(1, 'Codelco anuncia nuevo plan de inversión en la mina El Teniente para 2027', 1, 'medio-a')
        b = story(2, 'Codelco anuncia nuevo plan de inversión en la mina El Teniente para 2027 y más', 2, 'medio-b', '05 - Venezuela')
        grouped = collect.group_related_articles([a, b])
        self.assertEqual(len(grouped), 1)
        alt = grouped[0]['also_in'][0]
        self.assertEqual(alt['title'], b['title'])
        self.assertEqual(alt['source_id'], 'medio-b')
        self.assertEqual(alt['category'], '05 - Venezuela')
        self.assertEqual(len(set(grouped[0]['source_ids'])), 2)

    def test_trending_detects_rising_term_and_ignores_constant_one(self):
        items = []
        n = 0
        for day in range(1, 8):  # «pensiones» aparece todos los días: no está en alza
            for k in range(3):
                n += 1
                items.append(story(n, f'Debate sobre pensiones en el Congreso {n}', 24 * day + k, f'fuente{k}'))
        for k in range(6):  # «apagón» aparece de golpe hoy, en seis fuentes
            n += 1
            items.append(story(n, f'Apagón masivo afecta a varias regiones {n}', k + 1, f'fuente{k}'))
            n += 1
            items.append(story(n, f'Debate sobre pensiones en el Congreso {n}', k + 1, f'fuente{k}'))
        result = insights.trending_topics(items, NOW)
        terms = [t['term'] for t in result['topics']]
        self.assertTrue(any('apagon' in t for t in terms), terms)
        top = result['topics'][0]
        self.assertIn('apagon', top['term'])
        self.assertTrue(top['is_new'])
        self.assertEqual(top['label'].split()[0], 'Apagón')  # conserva tildes y mayúsculas
        self.assertFalse(any(t == 'pensiones' for t in terms[:1]))

    def test_trending_requires_several_sources(self):
        items = [story(i, f'Rumor exclusivo sobre fichaje estelar {i}', 1, 'una-sola-fuente') for i in range(8)]
        self.assertEqual(insights.trending_topics(items, NOW)['topics'], [])

    def test_output_feeds_are_valid_rss(self):
        items = [story(i, f'Titular <con> & símbolos {i}', i, f'f{i}') for i in range(5)]
        items[0]['coverage'] = 4
        items[1]['coverage'] = 2
        sources = [{'category': '04 - Chile'}, {'category': '05 - Venezuela'}]
        with tempfile.TemporaryDirectory() as tmp:
            written = insights.write_feeds(Path(tmp), items, sources, NOW)
            self.assertIn('mas-cubierto.xml', written)
            self.assertIn('chile.xml', written)
            top = ET.parse(Path(tmp) / 'mas-cubierto.xml').getroot()
            titles = [x.text for x in top.iter('title')]
            self.assertIn('Titular <con> & símbolos 0', titles)
            self.assertEqual(len(top.findall('.//item')), 2)  # solo historias con 2+ medios
            self.assertEqual(len(ET.parse(Path(tmp) / 'chile.xml').getroot().findall('.//item')), 5)
            self.assertEqual(len(ET.parse(Path(tmp) / 'venezuela.xml').getroot().findall('.//item')), 0)


    def test_trending_rejects_calendar_words_and_generic_sports_words(self):
        # Eight distinct RSS sources mention different stories on a Monday in October.
        blocked = ('Lunes', 'Octubre', 'Resultados', 'Partidos', 'Fútbol', 'Jornada',
                   'Martes', 'Enero', 'Goles')
        items = [story(i, f'{blocked[i % len(blocked)]} cobertura regional sobre mercados y inversiones {i}',
                       i % 10 + 1, f'distinct-{i}') for i in range(12)]
        topics = insights.trending_topics(items, NOW, limit=30)['topics']
        terms = [term for topic in topics for term in topic['term'].split()]
        for word in blocked:
            self.assertNotIn(insights.fold(word), terms)

    def test_trending_requires_four_distinct_sources_not_four_articles(self):
        title = 'Apagón eléctrico masivo afecta a la región del sur'
        three = [story(i, title, i + 1, f'medio-{i % 3}') for i in range(12)]
        self.assertEqual(insights.trending_topics(three, NOW)['topics'], [])
        four = [story(i, title, i + 1, f'medio-{i % 4}') for i in range(12)]
        topics = insights.trending_topics(four, NOW)['topics']
        self.assertTrue(any(t['term'] == 'apagon' for t in topics), topics)
        self.assertTrue(all(t['sources'] >= 4 for t in topics), topics)

    def test_google_news_suffix_and_hyphenated_headlines(self):
        item = story(1, 'Informe de Chile - Diario Concepción', 1, 'Diario Concepción')
        original = item['title']
        self.assertEqual(collect.clean_google_news_title(original, 'Diario Concepción'), 'Informe de Chile')
        self.assertEqual(collect.clean_google_news_title('Gobierno - nueva política - EL UNIVERSAL', 'EL UNIVERSAL'),
                         'Gobierno - nueva política')
        self.assertEqual(collect.clean_google_news_title('Valparaíso - informe de transporte', 'El Otro Diario'),
                         'Valparaíso - informe de transporte')
        self.assertEqual(collect.clean_google_news_title('Chile - Valparaíso', ''), 'Chile - Valparaíso')
        feed = {'id': 'id-feed', 'name': 'RADAR — Venezuela', 'is_radar': True,
                'category': '05 - Venezuela'}
        entry = {'link': 'https://news.google.com/articles/abc123',
                 'title': 'Nueva inversión regional abre oportunidades - EL UNIVERSAL',
                 'source': {'title': 'EL UNIVERSAL'}}
        normalized = collect.make_item(entry, feed, NOW)
        self.assertEqual(normalized['title'], 'Nueva inversión regional abre oportunidades')
        self.assertEqual(normalized['publisher'], 'EL UNIVERSAL')

    def test_identical_google_headlines_group_after_suffix_cleanup(self):
        feed_a = {'id': 'a', 'name': 'RADAR — Noticias', 'is_radar': True, 'category': '05 - Venezuela'}
        feed_b = {'id': 'b', 'name': 'RADAR — Noticias', 'is_radar': True, 'category': '05 - Venezuela'}
        base = {'title': 'Gobierno anuncia nuevas medidas para fortalecer la economía nacional',
                'published': '2026-10-18T10:00:00Z'}
        entries = [{**base, 'title': base['title'] + ' - EL UNIVERSAL',
                    'link': 'https://example.com/a', 'source': {'title': 'EL UNIVERSAL'}},
                   {**base, 'title': base['title'] + ' - Diario Concepción',
                    'link': 'https://example.com/b', 'source': {'title': 'Diario Concepción'}}]
        grouped = collect.group_related_articles(
            [collect.make_item(entries[0], feed_a, NOW),
             collect.make_item(entries[1], feed_b, NOW)])
        self.assertEqual(len(grouped), 1)
        self.assertEqual(len(grouped[0]['also_in']), 1)
        self.assertEqual(grouped[0]['also_in'][0]['publisher'], 'Diario Concepción')

    def test_public_feeds_remove_internal_media_prefix(self):
        items = [story(1, 'Noticias locales', 1, 'MEDIO — Infobae'),
                 story(2, 'Informe regional', 2, 'REGIONAL — El Pitazo'),
                 story(3, 'Informe institucional', 3, 'OFICIAL — Banco Central')]
        items[1]['publisher'] = ''
        with tempfile.TemporaryDirectory() as tmp:
            insights.write_feeds(Path(tmp), items, [{'category': '04 - Chile'}], NOW)
            feed = ET.parse(Path(tmp) / 'chile.xml').getroot()
            names = [x.text for x in feed.findall('.//item/source')]
            self.assertEqual(names, ['Infobae', 'El Pitazo', 'OFICIAL — Banco Central'])

    def test_cocuyo_uses_google_news_rss_and_still_targets_venezuela(self):
        from urllib.parse import parse_qs, urlsplit
        sources = collect.parse_opml(ROOT / 'sources/feeds.opml')
        news = [s for s in sources if 'Efecto Cocuyo' in s['name']]
        self.assertEqual(len(news), 1)
        feed = news[0]
        self.assertEqual(urlsplit(feed['url']).hostname, 'news.google.com')
        self.assertEqual(feed['website'], 'https://efectococuyo.com/')
        self.assertEqual(feed['category'], '05 - Venezuela')
        self.assertTrue(feed['is_radar'])
        self.assertIn('site:efectococuyo.com', parse_qs(urlsplit(feed['url']).query)['q'][0])

    def test_feed_slug(self):
        self.assertEqual(insights.feed_slug('01 - Inteligencia Artificial'), 'inteligencia-artificial')
        self.assertEqual(insights.feed_slug('06 - Latinoamérica'), 'latinoamerica')


if __name__ == '__main__':
    unittest.main()
