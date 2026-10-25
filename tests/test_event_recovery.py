"""Agenda recovery is independent from article retention; no network in tests."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from recover_events import restore_events
from events import extract_event, parse_timestamp


def document(stamp='2026-10-25T00:00:00Z'):
    return {'version': 1, 'generated_at': stamp, 'horizon_days': 90,
            'items': [], 'pending': [], 'sources': []}


class EventRecoveryTests(unittest.TestCase):
    def fetcher(self, events=None, adopted=True, error=None, generation=None):
        def fetch(name):
            if name == 'meta.json':
                return {'events_version': 1, 'generated_at': generation or (events or {}).get('generated_at')} if adopted else {}
            if error:
                raise error
            return events
        return fetch

    def test_first_adoption_accepts_missing_events_only_on_old_site(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            missing = HTTPError('https://example.com/events.json', 404, 'Missing', {}, None)
            self.assertFalse(restore_events(root, fetch=self.fetcher(adopted=False, error=missing)))
            self.assertFalse((root / 'events.json').exists())

    def test_existing_agenda_must_not_disappear_without_valid_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = HTTPError('https://example.com/events.json', 404, 'Missing', {}, None)
            with self.assertRaises(RuntimeError):
                restore_events(Path(directory), fetch=self.fetcher(error=missing))

    def test_bad_response_keeps_valid_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old = document()
            (root / 'events.json').write_text(json.dumps(old))
            restore_events(root, fetch=self.fetcher(events={'items': []}))
            self.assertEqual(json.loads((root / 'events.json').read_text()), old)

    def test_published_agenda_is_recovered_even_when_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertTrue(restore_events(root, fetch=self.fetcher(events=document())))
            self.assertEqual(json.loads((root / 'events.json').read_text()), document())

    def test_newer_cache_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            newer = document('2026-10-26T00:00:00Z')
            (root / 'events.json').write_text(json.dumps(newer))
            restore_events(root, fetch=self.fetcher(events=document()))
            self.assertEqual(json.loads((root / 'events.json').read_text()), newer)

    def test_generation_order_uses_instants_not_iso_string_sorting(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            newer = document('2026-10-25T00:00:00Z')
            (root / 'events.json').write_text(json.dumps(newer))
            older = document('2026-10-25T01:00:00+02:00')
            restore_events(root, fetch=self.fetcher(events=older))
            self.assertEqual(json.loads((root / 'events.json').read_text()), newer)


    def test_mismatched_published_generation_keeps_valid_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old = document()
            (root / 'events.json').write_text(json.dumps(old))
            newer = document('2026-10-25T13:00:00Z')
            restore_events(root, fetch=self.fetcher(events=newer, generation=old['generated_at']))
            self.assertEqual(json.loads((root / 'events.json').read_text()), old)

    def test_newer_empty_snapshot_preserves_active_cached_event(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old = document('2026-10-25T12:00:00Z')
            source = {'id': 'cultura', 'name': 'Cultura', 'category': '07 - Concepción',
                      'url': 'https://example.com/rss', 'website': 'https://example.com',
                      'timezone': 'America/Santiago'}
            row = extract_event({'link': 'https://example.com/concierto', 'title': 'Concierto de primavera',
                                 'ev_startdate': '2026-11-01'}, source, parse_timestamp(old['generated_at']))
            old['items'] = [row]
            (root / 'events.json').write_text(json.dumps(old))
            newer = document('2026-10-25T13:00:00Z')
            restore_events(root, fetch=self.fetcher(events=newer))
            recovered = json.loads((root / 'events.json').read_text())
            self.assertEqual([item['id'] for item in recovered['items']], [row['id']])
            self.assertEqual(recovered['generated_at'], newer['generated_at'])

    def test_mismatched_published_generation_without_cache_fails_safely(self):
        with tempfile.TemporaryDirectory() as directory:
            newer = document('2026-10-25T13:00:00Z')
            with self.assertRaises(RuntimeError):
                restore_events(Path(directory), fetch=self.fetcher(events=newer, generation='2026-10-25T12:00:00Z'))
            self.assertFalse((Path(directory) / 'events.json').exists())
