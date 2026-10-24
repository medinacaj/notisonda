"""Run category/geography JavaScript contracts in the standard offline suite."""
from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CategoryBehaviorTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node no disponible")
    def test_local_folder_filters_and_regional_briefings(self):
        result = subprocess.run(["node", str(ROOT / "tests/test_category_behavior.cjs")],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
