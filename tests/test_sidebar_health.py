"""RSS diagnostics live in sidebar footer, never in the topbar."""
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class SidebarHealthTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.html=(ROOT/'web/index.html').read_text(encoding='utf-8')
  cls.js=(ROOT/'web/app.js').read_text(encoding='utf-8')
  cls.css=(ROOT/'web/sidebar-health.css').read_text(encoding='utf-8')

 def test_single_indicator_only_in_sidebar_footer(self):
  html=self.html
  self.assertEqual(html.count('id="feedHealthIndicator"'),1)
  self.assertEqual(html.count('id="feedHealthCount"'),1)
  self.assertEqual(html.count('id="sidebarFeedHealth"'),1)
  self.assertLess(html.index('id="sidebarFeedHealth"'),html.index('</aside>'))
  self.assertLess(html.index('id="feedHealthIndicator"'),html.index('</aside>'))
  self.assertNotIn('id="feedHealthIndicator"',html[html.index('<header class="topbar">'):html.index('</header>')])
  self.assertIn('fuentes no disponibles',html)
  self.assertIn('id="aboutButton"',html)

 def test_scrollable_navigation_and_persistent_footer(self):
  html=self.html
  self.assertLess(html.index('id="sidebarNavigation"'),html.index('id="sidebarFeedHealth"'))
  self.assertIn('body.radar-hybrid .sidebar-navigation{',self.css)
  self.assertIn('overflow-y:auto',self.css)
  self.assertIn('overscroll-behavior:contain',self.css)
  self.assertIn('body.radar-hybrid .sidebar-bottom{',self.css)
  self.assertIn('flex:0 0 auto',self.css)
  self.assertIn('@media(max-width:950px)',self.css)
  self.assertIn('body.radar-hybrid .sidebar-feed-status[hidden]{display:none!important}',self.css)

 def test_state_changes_visibility_and_preserves_diagnostics(self):
  self.assertIn("const section=$('sidebarFeedHealth')",self.js)
  self.assertIn('section.hidden=true',self.js)
  self.assertIn('section.hidden=false',self.js)
  self.assertIn("('feedHealthIndicator').addEventListener('click',openFeedHealth)",self.js)
  self.assertIn("('feedHealthCount').textContent=String(issues.length)",self.js)
  self.assertIn("state.health.filter(x=>x.state==='error'||x.state==='stale')",self.js)

 def test_assets(self):
  self.assertIn('sidebar-health.css?v=1.0.0',self.html)
  self.assertRegex(self.html,r'app\.js\?v=\d+\.\d+\.\d+')
