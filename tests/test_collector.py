import sys
from pathlib import Path
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import collect

class ReaderTests(unittest.TestCase):
    def test_opml_has_150_unique_feeds(self):
        feeds = collect.parse_opml(ROOT / 'sources' / 'feeds.opml')
        self.assertEqual(len(feeds), 150)
        self.assertEqual(len(set(x['url'] for x in feeds)), 150)
        self.assertEqual(len(set(x['category'] for x in feeds)), 6)

    def test_reject_unsafe_article_links(self):
        self.assertIsNone(collect.safe_web_url('javascript:alert(1)'))
        self.assertIsNone(collect.safe_web_url('file:///etc/passwd'))
        self.assertIsNone(collect.safe_web_url('https://user:pass@website.com/'))

    def test_preview_sanitizes_markup_and_script(self):
        text, image = collect.extract_html('<script>bad()</script><p>Hola <b>mundo</b></p><img src="https://example.com/a.jpg">')
        self.assertEqual(text, 'Hola mundo')
        self.assertEqual(image, 'https://example.com/a.jpg')

    def test_article_entry_data(self):
        source = {'id':'abc', 'name':'Fuente', 'category':'01 - Inteligencia Artificial', 'is_radar':False}
        entry = {'link':'https://example.com/item?utm_source=example','title':'Titular','summary':'Resumen'}
        result = collect.make_item(entry, source, datetime(2026,10,17,tzinfo=timezone.utc))
        self.assertEqual(result['title'], 'Titular')
        self.assertEqual(result['categories'], ['01 - Inteligencia Artificial'])
        self.assertIsNone(result['published_at'])


    def test_rss_xml_parser_without_network(self):
        xml = b"""<?xml version='1.0'?><rss version='2.0'><channel><title>Test</title>
        <item><title>Ultima noticia</title><link>https://example.net/post</link>
        <description>Breve resumen</description><pubDate>Sat, 17 Oct 2026 13:00:00 GMT</pubDate>
        </item></channel></rss>"""
        parsed = collect.feedparser.parse(xml)
        self.assertEqual(len(parsed.entries), 1)
        self.assertEqual(parsed.entries[0]['title'], 'Ultima noticia')
        self.assertIsNotNone(collect.entry_date(parsed.entries[0]))

    def test_atom_xml_parser_without_network(self):
        xml = b"""<?xml version='1.0'?><feed xmlns='http://www.w3.org/2005/Atom'>
        <title>Prueba</title><entry><title>Evento</title>
        <link rel='alternate' href='https://example.net/atom-item' />
        <updated>2026-10-17T10:00:00Z</updated><summary>Texto de prueba</summary>
        </entry></feed>"""
        parsed = collect.feedparser.parse(xml)
        self.assertEqual(len(parsed.entries), 1)
        self.assertEqual(parsed.entries[0]['link'], 'https://example.net/atom-item')


    def test_collect_generates_deduplicated_static_data(self):
        import json
        import tempfile
        from unittest.mock import patch
        sample = b"""<rss version='2.0'><channel><title>Test</title><item>
        <title>Noticia compartida</title><link>https://example.net/item</link>
        <description>Contenido breve</description>
        <pubDate>Sat, 17 Oct 2026 13:00:00 GMT</pubDate>
        </item></channel></rss>"""
        opml = """<opml version='1.0'><body><outline text='01 - IA'>
        <outline type='rss' title='A' xmlUrl='https://a.example.net/rss' />
        <outline type='rss' title='B' xmlUrl='https://b.example.net/rss' />
        </outline></body></opml>"""
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            src = base / 'feeds.opml'; src.write_text(opml, encoding='utf-8')
            with patch.object(collect, 'get_feed', return_value=sample):
                result = collect.collect(src, base / 'webdata', days=45, workers=2, max_per_feed=5)
            self.assertEqual(result['sources'], 2)
            self.assertEqual(result['articles'], 1)
            items = json.loads((base / 'webdata' / 'articles.json').read_text())['items']
            self.assertEqual(len(items[0]['source_ids']), 2)

if __name__ == '__main__':
    unittest.main()