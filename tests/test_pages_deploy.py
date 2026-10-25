import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import unittest
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_pages import verify


NOW = datetime(2026, 10, 20, 11, 0, tzinfo=timezone.utc)
STAMP = "2026-10-20T10:00:00Z"


def payloads(stamp=STAMP):
    sources = [{"id": f"source-{i}"} for i in range(178)]
    return {
        "": '<html><head><link href="styles.css?v=5.3"></head><body><section id="dashboardView"></section></body></html>',
        "data/sources.json": {"sources": sources, "categories": [f"folder-{i}" for i in range(6)]},
        "data/latest.json": {"generated_at": stamp, "items": [{"id": f"story-{i}"} for i in range(8)]},
        "data/meta.json": {"generated_at": stamp, "total_articles": 160, "latest_count": 8},
        "data/status.json": {"checked_at": stamp, "feeds": [{"id": f"source-{i}"} for i in range(178)]},
    }


def fetcher(files):
    def get(url):
        path = urlsplit(url).path.split("/radar-rss-publico/")[-1]
        value = files[path]
        if isinstance(value, str):
            return value.encode("utf-8")
        return json.dumps(value).encode("utf-8")
    return get


class DeploymentTests(unittest.TestCase):
    BASE = "https://example.github.io/radar-rss-publico/"

    def test_previous_generation_rejected_even_when_recent(self):
        with self.assertRaisesRegex(ValueError, "esperada"):
            verify(self.BASE, fetcher(payloads()), now=NOW,
                   expected_generation="2026-10-20T10:30:00Z")

    def test_expected_generation_accepted(self):
        result = verify(self.BASE, fetcher(payloads()), now=NOW, expected_generation=STAMP)
        self.assertEqual(result["generated_at"], STAMP)

    def test_agenda_generation_must_match_the_published_news(self):
        files = payloads()
        files['data/meta.json']['events_version'] = 1
        files['data/events.json'] = {'version': 1, 'generated_at': STAMP, 'horizon_days': 90,
                                     'items': [], 'pending': [], 'sources': []}
        self.assertEqual(verify(self.BASE, fetcher(files), now=NOW)['events'], 0)
        files['data/events.json']['generated_at'] = '2026-10-19T10:00:00Z'
        with self.assertRaisesRegex(ValueError, 'agenda|Agenda'):
            verify(self.BASE, fetcher(files), now=NOW)

    def test_advertised_agenda_cannot_be_missing(self):
        files = payloads()
        files['data/meta.json']['events_version'] = 1
        with self.assertRaises((ValueError, KeyError)):
            verify(self.BASE, fetcher(files), now=NOW)

    def test_valid_generated_pages(self):
        result = verify(self.BASE, fetcher(payloads()), now=NOW)
        self.assertEqual(result["sources"], 178)
        self.assertEqual(result["news"], 8)
        for key in ('events','events_upcoming','events_pending','event_sources_ok','event_sources_total'):
            self.assertIsNone(result[key])

    def test_agenda_counts_distinguish_current_upcoming_pending_and_source_health(self):
        files=payloads()
        files['data/meta.json']['events_version']=1
        row={'id':'today','title':'Concierto','url':'https://cultura.example/concierto',
             'source_id':'src1','source_name':'Cultura','category':'07 - Concepción',
             'timezone':'America/Santiago','start_date':'2026-10-21','end_date':None,
             'status':'scheduled','location':None,'announced_at':None,
             'first_seen_at':STAMP,'last_seen_at':STAMP,
             'date_evidence':{'kind':'rss','value':'2026-10-21','url':'https://cultura.example/concierto'}}
        files['data/events.json']={'version':1,'generated_at':STAMP,'horizon_days':90,
            'items':[row,dict(row,id='expired',start_date='2026-10-20'),
                     dict(row,id='ongoing',start_date='2026-10-19',end_date='2026-10-21'),
                     dict(row,id='horizon',start_date='2027-01-19'),
                     dict(row,id='distant',start_date='2027-01-20'),
                     dict(row,id='cancelled',status='cancelled')],
            'pending':[dict(row,id='pending',start_date=None,date_evidence=None,reason='date_unverified')],
            'sources':[{'source_id':'src1','source_name':'Cultura','url':'https://cultura.example/feed/',
                        'timezone':'America/Santiago','checked_at':STAMP,'status':'ok','error':None},
                       {'source_id':'src2','source_name':'Agenda','url':'https://agenda.example/feed/',
                        'timezone':'America/Caracas','checked_at':STAMP,'status':'error','error':'offline'}]}
        current=datetime(2026,10,21,4,tzinfo=timezone.utc)
        result=verify(self.BASE,fetcher(files),now=current)
        self.assertEqual(result['events'],6)
        self.assertEqual(result['events_upcoming'],3)
        self.assertEqual(result['events_pending'],1)
        self.assertEqual(result['event_sources_ok'],1)
        self.assertEqual(result['event_sources_total'],2)

    def test_additional_opml_folders_are_accepted(self):
        for count in (1, 5, 7, 8):
            with self.subTest(categories=count):
                files = payloads()
                files["data/sources.json"]["categories"] = [f"folder-{i}" for i in range(count)]
                self.assertEqual(verify(self.BASE, fetcher(files), now=NOW)["sources"], 178)

    def test_duplicate_folders_are_rejected(self):
        files = payloads()
        files["data/sources.json"]["categories"][-1] = "folder-0"
        with self.assertRaisesRegex(ValueError, "carpetas OPML"):
            verify(self.BASE, fetcher(files), now=NOW)

    def test_empty_or_invalid_folders_are_rejected(self):
        for categories in ([], None, "folder-0",
                           ["folder-0", "folder-1", "folder-2", "folder-3", "folder-4", ""],
                           ["folder-0", "folder-1", "folder-2", "folder-3", "folder-4", None]):
            with self.subTest(categories=categories):
                files = payloads()
                files["data/sources.json"]["categories"] = categories
                with self.assertRaisesRegex(ValueError, "carpetas OPML"):
                    verify(self.BASE, fetcher(files), now=NOW)

    def test_inconsistent_generation_rejected(self):
        files = payloads()
        files["data/status.json"]["checked_at"] = "2026-10-19T10:00:00Z"
        with self.assertRaisesRegex(ValueError, "generaciones diferentes"):
            verify(self.BASE, fetcher(files), now=NOW)

    def test_missing_sources_rejected(self):
        files = payloads()
        files["data/sources.json"]["sources"] = []
        with self.assertRaisesRegex(ValueError, "Catálogo público"):
            verify(self.BASE, fetcher(files), now=NOW)

    def test_stale_deployment_rejected(self):
        old = (NOW - timedelta(days=2)).isoformat()
        with self.assertRaisesRegex(ValueError, "desactualizado"):
            verify(self.BASE, fetcher(payloads(old)), now=NOW)

    def test_non_https_url_rejected(self):
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            verify("http://example.github.io/radar-rss-publico/", fetcher(payloads()), now=NOW)


if __name__ == "__main__":
    unittest.main()
