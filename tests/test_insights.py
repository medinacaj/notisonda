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

    def test_feed_slug(self):
        self.assertEqual(insights.feed_slug('01 - Inteligencia Artificial'), 'inteligencia-artificial')
        self.assertEqual(insights.feed_slug('06 - Latinoamérica'), 'latinoamerica')


if __name__ == '__main__':
    unittest.main()
