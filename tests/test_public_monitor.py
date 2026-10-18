"""Offline regression tests for the Pages health monitor."""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_public_health import assess, MAX_ERRORS, STALE_HOURS

NOW = datetime(2026, 10, 18, 13, tzinfo=timezone.utc)
def docs(age=1, errors=0):
    stamp = (NOW - timedelta(hours=age)).isoformat().replace("+00:00", "Z")
    return ({"generated_at": stamp, "total_articles": 2300},
            {"checked_at": stamp,
             "feeds": [{"state": "error" if i < errors else "ok"} for i in range(150)]})

class MonitorTests(unittest.TestCase):
    def test_accepts_normal_publication(self):
        self.assertEqual(assess(*docs(), NOW, "success"), [])
        self.assertEqual(assess(*docs(errors=MAX_ERRORS - 1), NOW), [])

    def test_alerts_for_staleness_and_errors(self):
        reports = assess(*docs(age=STALE_HOURS + 1, errors=MAX_ERRORS), NOW)
        self.assertTrue(any("sin actualizar" in x for x in reports), reports)
        self.assertTrue(any("fuentes RSS" in x for x in reports), reports)

    def test_alerts_when_latest_deploy_fails(self):
        self.assertTrue(any("failure" in x for x in assess(*docs(), NOW, "failure")))

    def test_rejects_missing_or_inconsistent_metadata(self):
        meta, status = docs()
        del meta["generated_at"]
        self.assertTrue(assess(meta, status, NOW))
        meta, status = docs()
        status["feeds"] = []
        self.assertTrue(assess(meta, status, NOW))

if __name__ == "__main__":
    unittest.main()
