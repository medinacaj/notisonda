"""Regresiones offline: imágenes RSS, metadatos OG y límites del enriquecimiento."""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch, Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import collect


class ImageRecoveryTests(unittest.TestCase):
    def test_rss_media_and_enclosure_are_preferred(self):
        entry = {
            'media_content': [
                {'url': 'https://medio.test/video.mp4', 'type': 'video/mp4'},
                {'url': 'https://medio.test/portada.webp', 'medium': 'image'}],
            'enclosures': [{'href': 'https://medio.test/audio.mp3', 'type': 'audio/mpeg'}],
            'summary': '<img src="https://medio.test/otra.jpg">'
        }
        self.assertEqual(collect.find_image(entry), 'https://medio.test/portada.webp')

    def test_rss_html_and_atom_content_have_valid_fallback(self):
        entry = {'summary': 'Sin imagen',
                 'content': [{'value': '<p>Texto</p><img src="https://medio.test/foto.jpg">'}]}
        self.assertEqual(collect.find_image(entry), 'https://medio.test/foto.jpg')
        self.assertIsNone(collect.find_image({'summary':'Solo texto'}))

    def test_og_is_preferred_and_relative_url_is_resolved(self):
        html = ('<meta property="og:image" content="/img/noticia.jpg">'
                '<meta name="twitter:image" content="https://medio.test/twitter.webp">')
        self.assertEqual(collect.find_page_image(html, 'https://medio.test/articulo/123'),
                         'https://medio.test/img/noticia.jpg')

    def test_og_secure_url_precedes_og_image(self):
        html = ('<meta property="og:image" content="http://medio.test/cover.jpg">'
                '<meta property="og:image:secure_url" content="https://medio.test/correcta.jpg">')
        self.assertEqual(collect.find_page_image(html, 'https://medio.test/post'),
                         'https://medio.test/correcta.jpg')

    def test_metadata_rejects_unsafe_protocols(self):
        self.assertIsNone(collect.find_page_image(
            '<meta property="og:image" content="javascript:alert(1)">',
            'https://medio.test/articulo'))

    def test_restrict_metadata_lookup_hosts(self):
        for url in ('http://medio.test/post', 'https://127.0.0.1/private',
                    'https://news.google.com/articles/abc', 'https://medio.test:9000/a',
                    'http://localhost/news'):
            self.assertIsNone(collect.page_image_host(url))
        self.assertEqual(collect.page_image_host('https://www.medio.test/post'),
                         'www.medio.test')

    def test_robots_prohibits_page_fetch_and_does_not_follow_redirects(self):
        def response(status, body):
            r = Mock()
            r.status_code = status
            r.iter_content.return_value = [body.encode('utf-8')]
            return r

        robots = 'User-agent: RadarRSS\nDisallow: /privado\nAllow: /publico\n'
        with patch.object(collect, 'is_public_host', return_value=True), patch.object(
            collect.requests, 'get', return_value=response(200, robots)) as req:
            self.assertFalse(collect.page_image_allowed('https://medio.test/privado/post','medio.test'))
            self.assertTrue(collect.page_image_allowed('https://medio.test/publico/post','medio.test'))
            self.assertTrue(all(call.kwargs.get('allow_redirects') is False for call in req.call_args_list))
        with patch.object(collect,'is_public_host',return_value=True), patch.object(
            collect.requests, 'get', return_value=response(403, '')): 
            self.assertFalse(collect.page_image_allowed('https://medio.test/a','medio.test'))
        with patch.object(collect,'is_public_host',return_value=True), patch.object(
            collect.requests, 'get', return_value=response(404, '')):
            self.assertTrue(collect.page_image_allowed('https://medio.test/a','medio.test'))

    def test_fetch_has_body_size_and_content_type_limits(self):
        valid=Mock(status_code=200, headers={'Content-Type':'text/html'}, encoding='utf-8')
        valid.iter_content.return_value=[b'<meta property="og:image" content="/foto.jpg">']
        with patch.object(collect.requests,'get', return_value=valid) as mock_get:
            got=collect.read_bounded_response('https://medio.test/post',accept='text/html',limit=1024)
            self.assertIn('og:image',got[1])
            self.assertFalse(mock_get.call_args.kwargs['allow_redirects'])
        wrong=Mock(status_code=200, headers={'Content-Type':'application/pdf'})
        with patch.object(collect.requests,'get', return_value=wrong):
            self.assertIsNone(collect.read_bounded_response('https://medio.test/pdf',
                                                            accept='text/html',limit=1024))

    def test_lookup_is_denied_without_robots_permission(self):
        with patch.object(collect,'page_image_allowed',return_value=False), patch.object(
            collect,'is_public_host',return_value=True), patch.object(
            collect,'read_bounded_response') as fetch:
            self.assertIsNone(collect.lookup_original_image('https://medio.test/post'))
            fetch.assert_not_called()

    def test_recovers_only_registered_recent_hosts_and_does_not_hammer(self):
        now=datetime(2026,10,19,tzinfo=timezone.utc)
        iso=collect.iso(now)
        articles = [
            {'id':str(i),'url':f'https://medio.test/post/{i}','first_seen_at':iso,
             'source_ids':['publisher'],'image':None} for i in range(6)]
        articles.append({'id':'unknown','url':'https://unregistered.test/news',
                         'first_seen_at':iso,'source_ids':['publisher'],'image':None})
        sources=[{'id':'publisher','website':'https://www.medio.test',
                  'url':'https://medio.test/rss'}]
        with patch.object(collect,'lookup_original_image',
                          side_effect=lambda url: 'https://medio.test/foto.jpg') as fake:
            result=collect.recover_missing_images(articles,now,sources)
        self.assertEqual(result,{'checked':2,'recovered':2})
        self.assertEqual(fake.call_count,2)
        self.assertEqual(sum(bool(x.get('image')) for x in articles),2)
        # The latest failed/checked entries must not be retried in the next run.
        with patch.object(collect,'lookup_original_image') as fake:
            self.assertEqual(collect.recover_missing_images(articles,now,sources)['checked'],2)
            self.assertEqual(fake.call_count,2)

    def test_cached_failed_lookup_not_retried_before_36_hours(self):
        now=datetime(2026,10,19,tzinfo=timezone.utc)
        article={'id':'1','url':'https://medio.test/a',
                 'first_seen_at':collect.iso(now),'source_ids':['pub'],
                 'image_checked_at':collect.iso(now-timedelta(hours=1))}
        with patch.object(collect,'lookup_original_image') as mocked:
            result=collect.recover_missing_images([article],now,
                [{'id':'pub','website':'https://medio.test','url':'https://medio.test/rss'}])
            self.assertEqual(result['checked'],0)
            mocked.assert_not_called()

if __name__ == '__main__':
    unittest.main()
