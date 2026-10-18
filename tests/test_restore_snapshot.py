"""Safe offline recovery checks for public Radar RSS snapshots."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from validate_restore import validate

class SnapshotRecoveryTests(unittest.TestCase):
    def make(self,folder,duplicate=False):
        articles=[{"id":f"art-{i}","title":f"Titular {i}"} for i in range(50)]
        if duplicate:articles[-1]["id"]=articles[0]["id"]
        (folder/"articles.json").write_text(json.dumps({"generated_at":"2026-10-18T00:00:00Z","items":articles}))
        (folder/"status.json").write_text(json.dumps({"feeds":[{"state":"ok"},{"state":"ok"}]}))
    def test_accepts_valid_snapshot(self):
        with tempfile.TemporaryDirectory() as d:
            self.make(Path(d))
            self.assertEqual(validate(Path(d))["articles"],50)
    def test_rejects_repeated_ids(self):
        with tempfile.TemporaryDirectory() as d:
            self.make(Path(d),duplicate=True)
            with self.assertRaises(ValueError):validate(Path(d))
    def test_rejects_missing_file(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):validate(Path(d))
if __name__=="__main__":unittest.main()
