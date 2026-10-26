"""Published history is selected by UTC instant, without external requests."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import recover_history


class HistoryRecoveryTests(unittest.TestCase):
    @staticmethod
    def documents(stamp, marker):
        return {
            'articles.json': {'version': 2, 'generated_at': stamp, 'marker': marker,
                              'items': [{'id': f'article-{i}', 'title': f'Titular {i}'} for i in range(50)]},
            'status.json': {'version': 1, 'checked_at': stamp, 'marker': marker,
                            'feeds': [{'id': 'medio-a', 'state': 'ok', 'articles': 50}]},
        }

    def recover(self, cached_stamp, remote_stamp, *, cached=True, error=None):
        old = self.documents(cached_stamp, 'cached')
        published = self.documents(remote_stamp, 'published')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            if cached:
                for name, doc in old.items():
                    (root / name).write_text(json.dumps(doc), encoding='utf8')

            def fetch(request, timeout):
                if error:
                    raise error
                name = request.full_url.rsplit('/', 1)[-1]
                return io.BytesIO(json.dumps(published[name]).encode())

            with patch.object(recover_history, 'urlopen', fetch), redirect_stdout(io.StringIO()):
                recover_history.restore(root)
            return {name: json.loads((root / name).read_text()) for name in old}

    def assert_markers(self, docs, expected):
        self.assertEqual({name: doc['marker'] for name, doc in docs.items()},
                         {'articles.json': expected, 'status.json': expected})

    def test_older_remote_offset_does_not_replace_newer_cache(self):
        self.assert_markers(self.recover('2026-10-25T00:00:00Z', '2026-10-25T01:00:00+02:00'), 'cached')

    def test_newer_remote_utc_replaces_lexically_later_offset_cache(self):
        self.assert_markers(self.recover('2026-10-25T02:00:00+03:00', '2026-10-25T00:00:00Z'), 'published')

    def test_equal_instants_keep_existing_snapshot(self):
        self.assert_markers(self.recover('2026-10-24T23:00:00Z', '2026-10-25T01:00:00+02:00'), 'cached')

    def test_invalid_remote_timestamps_keep_valid_cache(self):
        for stamp in [None, True, 123, 'not-a-date', '2026-10-25T12:00:00',
                      '9999-12-31T23:59:59-23:59']:
            with self.subTest(stamp=stamp):
                self.assert_markers(self.recover('2026-10-24T00:00:00Z', stamp), 'cached')

    def test_invalid_remote_without_cache_refuses_archive_reset(self):
        for stamp in [None, 'not-a-date', '2026-10-25T12:00:00']:
            with self.subTest(stamp=stamp), self.assertRaisesRegex(RuntimeError, 'refusing to reset'):
                self.recover(None, stamp, cached=False)

    def test_valid_remote_repairs_invalid_cached_timestamp(self):
        self.assert_markers(self.recover('not-a-date', '2026-10-25T00:00:00Z'), 'published')

    def test_network_error_preserves_valid_cache(self):
        self.assert_markers(self.recover('2026-10-25T00:00:00Z', None, error=URLError('offline')), 'cached')

    def test_network_error_with_invalid_cache_fails_safely(self):
        with self.assertRaisesRegex(RuntimeError, 'refusing to reset'):
            self.recover('not-a-date', None, error=URLError('offline'))

    def test_network_error_without_cache_fails_safely(self):
        with self.assertRaisesRegex(RuntimeError, 'refusing to reset'):
            self.recover(None, None, cached=False, error=URLError('offline'))

    def test_first_valid_publication_is_recovered(self):
        self.assert_markers(self.recover(None, '2026-10-25T00:00:00Z', cached=False), 'published')


if __name__ == '__main__':
    unittest.main()
