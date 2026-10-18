"""Dialog scrolling layout and tab behavior regression checks."""
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class ModalLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css=(ROOT/'web/modal-layout.css').read_text(encoding='utf-8')
        cls.html=(ROOT/'web/index.html').read_text(encoding='utf-8')
        cls.app=(ROOT/'web/app.js').read_text(encoding='utf-8')

    def rule(self, selector):
        match=re.search(re.escape(selector)+r'\s*\{([^{}]*)\}',self.css)
        self.assertIsNotNone(match,'Missing CSS rule: '+selector)
        return match.group(1)

    def test_dialog_scrolling_and_sticky_regions(self):
        settings=self.rule('.settings-dialog[open]')
        self.assertIn('grid-template-rows:auto minmax(0,1fr) auto',settings)
        self.assertIn('height:min(830px,calc(100dvh - 32px))',settings)
        body=self.rule('.settings-dialog .settings-body')
        self.assertIn('grid-template-rows:minmax(0,1fr)',body)
        self.assertIn('min-height:0',body)
        pages=self.rule('.settings-dialog .settings-pages')
        self.assertIn('overflow-y:auto',pages)
        self.assertIn('min-height:0',pages)
        self.assertIn('max-height:none',pages)
        self.assertIn('scrollbar-gutter:stable',pages)
        footer=self.rule('.settings-dialog .settings-footer')
        self.assertIn('background:var(--surface2)',footer)

    def test_mobile_tab_row_and_short_viewport(self):
        self.assertIn('@media(max-width:710px)',self.css)
        self.assertIn('grid-template-rows:auto minmax(0,1fr)',self.css)
        self.assertIn('overflow-x:auto',self.css)
        self.assertIn('@media(max-height:520px)',self.css)
        self.assertIn('height:calc(100dvh - 12px)',self.css)

    def test_all_dialogs_scroll_reliably(self):
        for selector,region in (('.article-reader-dialog[open]','.article-reader-dialog .reader-scroll'),
                                ('.feed-health-dialog[open]','.feed-health-dialog .feed-health-body')):
            self.assertIn('grid-template-rows:auto minmax(0,1fr) auto',self.rule(selector))
            self.assertIn('overflow-y:auto',self.rule(region))
        self.assertIn('.about-dialog[open]',self.css)
        self.assertIn('.folder-manage-dialog[open]',self.css)

    def test_tab_change_and_open_reset_scroll(self):
        self.assertIn('id="settingsPages"',self.html)
        self.assertIn('tabindex="0"',self.html)
        self.assertIn("const scroll=$('settingsPages')",self.app)
        self.assertIn("scroll.scrollTop=0",self.app)
        self.assertIn("$('settingsPages').scrollTop=0",self.app)

    def test_asset_order_and_version(self):
        self.assertIn('modal-layout.css?v=1.0.0',self.html)
        self.assertIn('app.js?v=7.8.0',self.html)
        self.assertLess(self.html.index('sidebar-layout.css?v='),self.html.index('modal-layout.css?v='))
        self.assertLess(self.html.index('modal-layout.css?v='),self.html.index('</head>'))
