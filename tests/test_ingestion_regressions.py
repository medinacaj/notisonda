"""Offline ingestion regressions: preserve attribution and count editorial outlets."""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from xml.sax.saxutils import escape, quoteattr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import collect


class IngestionRegressionTests(unittest.TestCase):
    def run_collection(self, source_specs, entries, cached=None):
        """Exercise parsing, merging, grouping and public outputs; stub only RSS I/O."""
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            opml = base / 'feeds.opml'
            outlines = ''.join(
                f'<outline title={quoteattr(name)} xmlUrl={quoteattr(url)} />'
                for name, url in source_specs)
            opml.write_text('<opml><body><outline text="04 - Chile">' + outlines + '</outline></body></opml>')
            out = base / 'data'
            if cached:
                sources = collect.parse_opml(opml)
                collect.write_json(out / 'articles.json', {'items': cached(sources)})
            def rss(url):
                rows = ''.join('<item><title>' + escape(title) + '</title><link>' + escape(link) +
                               '</link><source>' + escape(publisher) + '</source></item>'
                               for title, link, publisher in entries.get(url, []))
                return ('<rss version="2.0"><channel><title>Fixture</title>' + rows + '</channel></rss>').encode()
            with patch.object(collect, 'get_feed', side_effect=rss):
                collect.collect(opml, out, days=45, workers=1, max_per_feed=100)
            return (json.loads((out / 'articles.json').read_text())['items'],
                    (base / 'feeds/mas-cubierto.xml').read_text())

    def test_refresh_preserves_unique_valid_alternatives_and_first_seen(self):
        specs = [('MEDIO — Diario A', 'https://a.example/rss'),
                 ('MEDIO — Diario B', 'https://b.example/rss')]
        first_seen = collect.iso(datetime.now(timezone.utc) - timedelta(days=2))
        def cached(sources):
            lead = collect.make_item({'title': 'Noticia principal', 'link': 'https://a.example/story'},
                                     sources[0], datetime.now(timezone.utc))
            lead['first_seen_at'] = first_seen
            lead['source_ids'].append(sources[1]['id'])
            alternative = {'id': 'other', 'url': 'https://b.example/story', 'source_id': sources[1]['id'],
                           'publisher': 'Diario B', 'title': 'La cobertura del segundo medio',
                           'category': '04 - Chile'}
            lead['also_in'] = [alternative, dict(alternative),
                               {'url': lead['url'], 'source_id': sources[0]['id'], 'publisher': 'Diario A'},
                               {'url': 'https://removed.example/story', 'source_id': 'removed', 'publisher': 'Retirado'}]
            return [lead]
        items, _ = self.run_collection(specs, {specs[0][1]: [('Noticia actualizada', 'https://a.example/story', '')]}, cached)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['title'], 'Noticia actualizada')
        self.assertEqual(items[0]['first_seen_at'], first_seen)
        self.assertEqual([x['url'] for x in items[0].get('also_in', [])], ['https://b.example/story'])
        self.assertEqual(items[0]['also_in'][0]['publisher'], 'Diario B')
        self.assertEqual(items[0]['coverage'], 2)

    def test_removed_source_alternatives_are_not_kept_without_a_refresh(self):
        specs = [('MEDIO — Diario A', 'https://a.example/rss')]
        def cached(sources):
            lead = collect.make_item({'title': 'Noticia principal', 'link': 'https://a.example/story'},
                                     sources[0], datetime.now(timezone.utc))
            lead['source_ids'].append('removed')
            lead['also_in'] = [{'id': 'removed-story', 'url': 'https://removed.example/story',
                                'source_id': 'removed', 'publisher': 'Retirado'}]
            return [lead]
        items, _ = self.run_collection(specs, {}, cached)
        self.assertEqual(items[0].get('also_in', []), [])
        self.assertEqual(items[0]['coverage'], 1)

    def test_two_google_queries_for_one_outlet_are_not_two_media(self):
        specs = [('RADAR — Consulta A', 'https://news.google.com/rss/search?q=a'),
                 ('RADAR — Consulta B', 'https://news.google.com/rss/search?q=b')]
        story = ('Noticia compartida - Diario Único', 'https://news.google.com/rss/articles/same', 'Diario Único')
        items, rss = self.run_collection(specs, {url: [story] for _, url in specs})
        self.assertEqual(len(items), 1)
        self.assertEqual(len(items[0]['source_ids']), 2)
        self.assertEqual(items[0]['coverage'], 1)
        self.assertNotIn('<item>', rss)
        self.assertNotIn('Cubierta por 2 medios', rss)

    def test_retired_lead_is_replaced_by_a_registered_alternative(self):
        specs = [('MEDIO — Diario B', 'https://b.example/rss')]
        def cached(sources):
            return [{'id': 'retired-lead', 'title': 'Titular del editor retirado',
                     'url': 'https://removed.example/story', 'publisher': 'Retirado',
                     'source_ids': ['removed', sources[0]['id']], 'categories': ['05 - Venezuela', '04 - Chile'],
                     'first_seen_at': collect.iso(datetime.now(timezone.utc)),
                     'summary': 'Extracto del editor retirado', 'image': 'https://removed.example/image.jpg',
                     'also_in': [{'id': 'valid-alternative', 'url': 'https://b.example/story',
                                  'title': 'Titular del editor registrado', 'publisher': 'Diario B',
                                  'source_id': sources[0]['id'], 'category': '04 - Chile'}]}]
        items, _ = self.run_collection(specs, {}, cached)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['url'], 'https://b.example/story')
        self.assertEqual(items[0]['id'], 'valid-alternative')
        self.assertEqual(items[0]['publisher'], 'Diario B')
        self.assertEqual(items[0]['categories'], ['04 - Chile'])
        self.assertEqual(items[0]['summary'], '')
        self.assertIsNone(items[0]['image'])
        self.assertEqual(items[0].get('also_in', []), [])
        self.assertEqual(items[0]['coverage'], 1)

    def test_distinct_direct_outlets_still_count_as_two_media(self):
        specs = [('MEDIO — Diario A', 'https://a.example/rss'),
                 ('MEDIO — Diario B', 'https://b.example/rss')]
        title = 'Codelco anuncia nuevo plan de inversión en mina para 2027'
        items, rss = self.run_collection(specs, {
            specs[0][1]: [(title, 'https://a.example/story', '')],
            specs[1][1]: [(title, 'https://b.example/story', '')]})
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['coverage'], 2)
        self.assertEqual(len(items[0]['also_in']), 1)
        self.assertIn('Cubierta por 2 medios', rss)


if __name__ == '__main__':
    unittest.main()
