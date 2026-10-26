"""Contrato del tema índigo-violeta de Radar RSS sin cambiar la navegación editorial."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class CosmicThemeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css=(ROOT/'web/cosmic-theme.css').read_text(encoding='utf8')
        cls.html=(ROOT/'web/index.html').read_text(encoding='utf8')
        cls.app=(ROOT/'web/app.js').read_text(encoding='utf8')
        cls.sw=(ROOT/'web/sw.js').read_text(encoding='utf8')

    def test_css_loaded_after_layout_overrides(self):
        self.assertLess(self.html.index('home-editorial.css?v='),self.html.index('cosmic-theme.css?v='))
        self.assertIn("'./cosmic-theme.css'",self.sw)
        self.assertIn('radar-rss-v37',self.sw)

    def test_cosmic_palette_and_primary_action(self):
        for token in ('--bg:#0e0f2d','--accent:#5865f2','--text:#ffffff',
                      '--muted:#babcd9','--surface:#1b1f40','--card:#202446'):
            self.assertIn(token,self.css)
        self.assertIn('.load-more',self.css)
        self.assertIn('.reader-primary',self.css)
        self.assertIn('prefers-reduced-motion:reduce',self.css)

    def test_iaadc_system_default_with_manual_theme_modes(self):
        initial=self.app[self.app.index('function initialTheme()'):self.app.index('const state =')]
        self.assertIn("return 'system';",initial)
        self.assertIn('THEME_EXPLICIT_KEY',initial)
        self.assertIn("'system','light','dark'",initial)
        self.assertIn('body.radar-hybrid.light',self.css)
        self.assertIn('id="themeToggle"',self.html)
        self.assertIn('id="settingTheme"',self.html)
        self.assertIn('<body class="radar-hybrid"',self.html)

    def test_editorial_structure_not_replaced(self):
        for id_ in ('dashboardFeature','dashboardFolders','articleGrid',
                    'newsroomColumns','categoryNav','settingsDialog'):
            self.assertIn(f'id="{id_}"',self.html)
        self.assertNotIn('hero',self.css)
        self.assertNotIn('@import',self.css)

if __name__=='__main__':
    unittest.main()
