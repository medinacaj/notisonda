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

    def test_valid_generated_pages(self):
        result = verify(self.BASE, fetcher(payloads()), now=NOW)
        self.assertEqual(result["sources"], 178)
        self.assertEqual(result["news"], 8)

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
