"""Source tools run in existing CI without requiring a new workflow/dependency."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]

class SourceManagement(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'), 'Node no disponible')
    def test_source_tools_behavior(self):
        result=subprocess.run(['node','tests/test_source_tools.cjs'],cwd=ROOT,capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
