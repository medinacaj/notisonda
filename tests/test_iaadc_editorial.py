"""Radar Editorial: contrato visual IAADC, integridad del lector y PWA."""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT/"web"

class IAADCEditorialThemeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css=(WEB/"iaadc-editorial.css").read_text(encoding="utf-8")
        cls.html=(WEB/"index.html").read_text(encoding="utf-8")
        cls.app=(WEB/"app.js").read_text(encoding="utf-8")
        cls.sw=(WEB/"sw.js").read_text(encoding="utf-8")

    def test_theme_is_last_stylesheet_and_cached(self):
        self.assertLess(self.html.index('cosmic-theme.css?v='),self.html.index('iaadc-editorial.css?v='))
        self.assertIn("'./iaadc-editorial.css'",self.sw)
        self.assertIn("const CACHE = 'radar-rss-v35'",self.sw)

    def test_iaadc_exact_light_palette_and_font(self):
        for value in (
            "--bg:#f4f6f6", "--surface:#ffffff", "--line:#e2e8e9",
            "--text:#26343f", "--muted:#63737d", "--accent:#3a8c83",
            "--iaadc-sidebar:#192934",'"Avenir Next"'
        ):
            with self.subTest(value=value):
                self.assertIn(value,self.css)
        self.assertIn("body.radar-hybrid:not(.light)",self.css)
        self.assertIn("color-scheme:dark",self.css)

    def test_controls_cards_and_accessibility(self):
        for selector in (
            ".article-read-toggle", ".article-card.unread-card",
            ".article-card.read-article", ".card-menu", ".columns-menu-popup",
            ".filter-bar", ".sidebar .nav-link.active", ".topic-chip.active",
            ".settings-dialog", ".article-reader-dialog", ".dashboard-folder",
            "prefers-reduced-motion:reduce", "forced-colors:active"
        ):
            with self.subTest(selector=selector):
                self.assertIn(selector,self.css)
        self.assertIn("--iaadc-shadow-unread",self.css)
        self.assertIn("--iaadc-shadow-hover",self.css)
        self.assertNotIn("!important",self.css)

    def test_no_functionality_removed(self):
        for component_id in (
            "articleGrid", "dashboardFeature", "dashboardFolders",
            "categoryNav", "settingsDialog", "cardMenu", "themeToggle",
            "sidebarResizeHandle"
        ):
            with self.subTest(component=component_id):
                self.assertIn(f'id="{component_id}"',self.html)
        self.assertRegex(self.html,r'<body class="radar-hybrid"')
        self.assertIn('data-card-action="read"',self.html)
        self.assertIn('data-card-action="share"',self.html)

    def test_respect_manual_theme_and_system_default(self):
        start=self.app.index("function initialTheme()")
        end=self.app.index("const state =",start)
        initial=self.app[start:end]
        self.assertIn("return 'system';",initial)
        self.assertIn("THEME_EXPLICIT_KEY",initial)
        self.assertIn("['system','light','dark']",initial)

if __name__=="__main__":
    unittest.main()
