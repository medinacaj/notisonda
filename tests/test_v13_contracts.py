"""V1.3 contract checks for onboarding, offline shell and bounded history."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class V13Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=(ROOT/'web/app.js').read_text(encoding="utf8")
        cls.lib=(ROOT/'web/library.js').read_text(encoding="utf8")
        cls.html=(ROOT/'web/index.html').read_text(encoding="utf8")
        cls.sw=(ROOT/'web/sw.js').read_text(encoding="utf8")
        cls.js=(ROOT/'web/v13.js').read_text(encoding="utf8")
        cls.workflow=(ROOT/'.github/workflows/deploy.yml').read_text(encoding="utf8")

    def test_shell_order_and_cache(self):
        self.assertLess(self.html.index('v12.js?v='),self.html.index('v13.js?v='))
        self.assertIn('v13.css?v=',self.html)
        self.assertIn("'./v13.js'",self.sw)
        self.assertIn("'./v13.css'",self.sw)

    def test_onboarding_is_local_accessible_and_reopenable(self):
        for token in ["radar-v13-guide-dismissed","v13GuideTitle",
                      "v13DismissGuide","v13OpenGuide","aria-labelledby"]:
            self.assertIn(token,self.js)
        self.assertIn("localStorage.setItem",self.js)
        self.assertNotIn("fetch(",self.js)
        self.assertNotIn("sendBeacon",self.js)

    def test_history_is_bounded_and_inactive_feed_is_not_drawn(self):
        self.assertIn("Math.min(3,files.length)",self.app)
        self.assertIn("if(state.pageView==='feed')",self.app)
        self.assertIn("grid.replaceChildren();",self.app)

    def test_save_restores_keyboard_focus(self):
        self.assertIn("const restoreFocus=document.activeElement",self.lib)
        self.assertIn("button.focus({preventScroll:true})",self.lib)

    def test_card_height_fix_only_targets_grid_not_editorial_or_list(self):
        css=(ROOT/'web/v13.css').read_text(encoding='utf8')
        self.assertIn('#articleGrid.article-grid:not(.list-view)',css)
        self.assertIn('grid-auto-rows:1fr',css)
        self.assertIn('> .article-card .article-footer',css)
        self.assertNotIn('.dashboard-feature .article-card{grid-auto-rows',css)
        self.assertIn('v13.css?v=1.3.1',self.html)
        self.assertIn("radar-rss-v7",self.sw)

    def test_backup_is_retained_and_manual_recovery_checks_integrity(self):
        self.assertIn("retention-days: 90",self.workflow)
        self.assertIn("python scripts/validate_restore.py",self.workflow)
        self.assertIn('inputs.restore_run_id',self.workflow)
        self.assertIn("python scripts/audit_editorial.py",self.workflow)

if __name__=="__main__":
    unittest.main()
