#!/usr/bin/env python3
"""Recover the published agenda, allowing a single migration from the old site."""
import json
from pathlib import Path
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from events import merge_events, parse_timestamp, validate_document

BASE = 'https://medinacaj.github.io/radar-rss-publico/data/'
LIMIT = 10_000_000


def download(name):
    request = Request(BASE + name, headers={'User-Agent': 'RadarRSS-AgendaRecovery/1.0'})
    with urlopen(request, timeout=25) as response:
        content = response.read(LIMIT + 1)
    if len(content) > LIMIT:
        raise ValueError('Agenda document too large')
    return json.loads(content)


def restore_events(root, fetch=download):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    path = root / 'events.json'
    old = None
    try:
        old = validate_document(json.loads(path.read_text(encoding='utf-8')))
    except (OSError, ValueError, TypeError):
        pass
    try:
        current = validate_document(fetch('events.json'))
        meta = fetch('meta.json')
        if not isinstance(meta, dict) or meta.get('events_version') != 1 or meta.get('generated_at') != current['generated_at']:
            raise ValueError('Published agenda generation does not match manifest')
        if old is None or parse_timestamp(current['generated_at']) > parse_timestamp(old['generated_at']):
            if old is not None:
                current = merge_events(old, current['items'] + current['pending'], current['sources'], parse_timestamp(current['generated_at']))
            temporary = path.with_suffix('.json.tmp')
            temporary.write_text(json.dumps(current, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
            temporary.replace(path)
        print('Agenda history recovered', flush=True)
        return True
    except Exception as error:
        if old is not None:
            print('Using validated agenda cache:', type(error).__name__, flush=True)
            return True
        if isinstance(error, HTTPError) and error.code in (404, 410):
            # A 404 alone cannot establish first adoption: consult the published manifest.
            try:
                meta = fetch('meta.json')
                if isinstance(meta, dict) and 'events_version' not in meta:
                    print('First agenda adoption: previous site has no agenda', flush=True)
                    return False
            except Exception:
                pass
        raise RuntimeError('Agenda history unavailable; refusing to reset it') from error


if __name__ == '__main__':
    restore_events(Path(sys.argv[1] if len(sys.argv) > 1 else 'web/data'))
