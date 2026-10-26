"""Regressions: counts in every news mode and no redundant source panel."""
from pathlib import Path
import re
import unittest
ROOT=Path(__file__).resolve().parents[1]
class ModeCountTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.html=(ROOT/'web/index.html').read_text(encoding='utf8')
  cls.app=(ROOT/'web/app.js').read_text(encoding='utf8')
  cls.lib=(ROOT/'web/library.js').read_text(encoding='utf8')
  cls.css=(ROOT/'web/radar-hybrid.css').read_text(encoding='utf8')
 def test_counters_present_in_all_modes_even_zero(self):
  for mode,id in [('all','allCount'),('unread','unreadCount'),('saved','savedCount')]:
   self.assertIn('data-mode="'+mode+'"',self.html)
   self.assertIn('class="mode-tab-count" id="'+id+'">0</span>',self.html)
   self.assertIn("'"+id+"'",self.app)
  self.assertIn('format.format(count)',self.app)
 def test_counts_use_same_filters_as_feed(self):
  self.assertIn('function applyFilters(mode=state.mode)',self.app)
  self.assertIn('applyFilters=function(mode=state.mode)',self.lib)
  for mode in ['all','unread','saved']:
   self.assertIn("applyFilters('"+mode+"')",self.app)
  self.assertIn("mode==='saved'?savedNews():state.items",self.lib)
  self.assertIn('hasHistory()',self.app)
 def test_redundant_sources_removed_without_breaking_about(self):
  self.assertNotIn('Seguimiento automático',self.html)
  self.assertNotIn('id="sidebarSources"',self.html)
  self.assertNotIn("('sidebarSources')",self.app)
  self.assertIn('id="aboutButton"',self.html)
  self.assertIn('id="refreshCycle"',self.html)
 def test_cache_changed(self):
  self.assertRegex(self.html,r'<script src="\./app\.js\?v=[^"]+" defer></script>')
  self.assertRegex(self.html,r'<link rel="stylesheet" href="\./dimension\.css\?v=[^"]+">')
