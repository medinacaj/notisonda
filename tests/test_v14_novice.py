import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class V14NoviceTests(unittest.TestCase):
    """Contratos de la capa V1.4 orientada a quien llega por primera vez."""

    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / 'web/index.html').read_text(encoding='utf8')
        cls.script = (ROOT / 'web/v14.js').read_text(encoding='utf8')
        cls.css = (ROOT / 'web/v14.css').read_text(encoding='utf8')

    def test_assets_load_last_and_are_cached(self):
        self.assertLess(self.html.index('v13.js?v='), self.html.index('v14.js?v='))
        self.assertLess(self.html.index('v13.css?v='), self.html.index('v14.css?v='))
        sw = (ROOT / 'web/sw.js').read_text(encoding='utf8')
        self.assertIn("'./v14.js'", sw)
        self.assertIn("'./v14.css'", sw)

    def test_filters_live_behind_one_disclosure(self):
        self.assertIn("toggle.setAttribute('aria-controls','filtersPanel')", self.script)
        self.assertIn("panel.append(regional)", self.script)
        self.assertIn("actions.append(markAll)", self.script)
        self.assertIn('.v14-filters-panel[hidden]{display:none}', self.css)
        # La guía «Combina filtros» abre el panel antes de enfocar el selector.
        self.assertIn('window.RadarFilters?.open()', (ROOT / 'web/v13.js').read_text(encoding='utf8'))

    def test_mobile_home_shows_list_before_optional_map(self):
        self.assertIn("mapToggle.setAttribute('aria-expanded','false')", self.script)
        mobile = self.css[self.css.index('@media(max-width:720px)'):]
        self.assertIn('.covered-list{order:1}', mobile)
        self.assertIn('.radar-figure{order:3;display:none}', mobile)

    def test_plain_language(self):
        self.assertIn('Lo que más medios publican', self.html)
        self.assertIn('<b>Ahorro de datos</b>', self.html)
        self.assertNotIn('Sin evaluación editorial', (ROOT / 'web/v12.js').read_text(encoding='utf8'))
        self.assertIn("'TEMAS'", (ROOT / 'web/library.js').read_text(encoding='utf8'))
        self.assertIn("label:'Resumen del día'", (ROOT / 'web/app.js').read_text(encoding='utf8'))

    def test_advanced_appearance_is_folded(self):
        start = self.html.index('id="settingsAdvancedLayout"')
        end = self.html.index('</details>', start)
        advanced = self.html[start:end]
        for control in ('settingLayout', 'settingColumns', 'settingDensity', 'settingSidebarWidth', 'settingHero'):
            self.assertIn(f'id="{control}"', advanced)
        for control in ('settingTheme', 'settingFont', 'settingImages', 'settingLite'):
            self.assertNotIn(f'id="{control}"', advanced)
        self.assertEqual(len(re.findall(r'id="settingFont"', self.html)), 1)

    def test_card_hint_and_fresh_state_are_local(self):
        self.assertIn("HINT_KEY='radar-v14-card-hint-dismissed'", self.script)
        self.assertIn("state.read.size===0", self.script)
        self.assertNotIn('fetch(', self.script)


if __name__ == '__main__':
    unittest.main()
