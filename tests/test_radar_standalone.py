"""Radar RSS: el gráfico circular y la clasificación tienen fichas distintas."""
from pathlib import Path
from html.parser import HTMLParser
import unittest

ROOT=Path(__file__).resolve().parents[1]


class Panels(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack=[]
        self.ancestors={}
        self.visible_containers={}
    def handle_starttag(self,tag,attrs):
        attr=dict(attrs)
        if tag not in ('br','img','input','link','meta','hr','source','area','wbr'):
            self.stack.append((tag,attr))
        if attr.get('id') in ('radarStage','radarCaption','radarFigure','coveredList','radarTitle','coveredTitle'):
            self.ancestors[attr['id']]=[a[1].get('class','') for a in self.stack if a[0]=='section']
        if attr.get('id')=='coverageTools':
            self.visible_containers['coverageTools']=[a[1] for a in self.stack]
    def handle_endtag(self,tag):
        if self.stack and self.stack[-1][0]==tag:self.stack.pop()


class RadarStandaloneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=(ROOT/'web/index.html').read_text(encoding='utf-8')
        cls.home=(ROOT/'web/homepage.js').read_text(encoding='utf-8')
        cls.css=(ROOT/'web/dimension.css').read_text(encoding='utf-8')
        cls.usability=(ROOT/'web/usability.js').read_text(encoding='utf-8')
        cls.usability_css=(ROOT/'web/usability.css').read_text(encoding='utf-8')

    def test_radar_and_coverage_are_separate_semantic_cards(self):
        parser=Panels()
        parser.feed(self.html)
        self.assertEqual(self.html.count('id="radarStage"'),1)
        self.assertEqual(self.html.count('id="coveredList"'),1)
        self.assertIn('radar-panel',parser.ancestors['radarStage'][-1])
        self.assertIn('radar-panel',parser.ancestors['radarCaption'][-1])
        self.assertIn('covered-panel',parser.ancestors['coveredList'][-1])
        self.assertNotEqual(parser.ancestors['radarStage'][-1],parser.ancestors['coveredList'][-1])
        self.assertIn('id="radarTitle"',self.html)
        self.assertIn('id="coveredTitle"',self.html)

    def test_radar_visible_without_dynamic_reparenting(self):
        parser=Panels()
        parser.feed(self.html)
        ancestors=parser.visible_containers['coverageTools']
        self.assertTrue(any(a.get('id')=='dashboardView' for a in ancestors))
        self.assertFalse(any(a.get('id')=='newsroomColumns' for a in ancestors))
        self.assertFalse(any('hidden' in a and a.get('id')!='dashboardView' for a in ancestors))
        self.assertIn('id="coverageTools"',self.html)
        self.assertIn('class="dashboard-panel radar-panel radar-standalone-card"',self.html)
        self.assertIn('class="dashboard-panel covered-panel covered-standalone-card"',self.html)
        self.assertNotIn('panel.after(tools)',self.home)
        self.assertNotIn('columns.before(',self.home)
        self.assertNotIn("if(tools)lead.after(tools)",self.home)
        self.assertNotIn("tools.append(aside)",self.home)
        # Antes estaba bajo #newsroomColumns[hidden]: ahora es su hermano dentro de Inicio.
        start=self.html.index('<section class="coverage-tools" id="coverageTools"')
        news=self.html.index('id="homeLatest"')
        close=self.html.index('<section id="agendaView"')
        self.assertGreater(start,news)
        self.assertLess(start,close)
        self.assertEqual(self.html.count('id="coverageTools"'),1)
        self.assertNotIn('id="coverageTools" hidden',self.html)

    def test_radar_never_wrapped_in_collapsed_details(self):
        self.assertIn('id="radarFigure"',self.html)
        self.assertIn('id="radarStage"',self.html)
        self.assertNotIn("document.createElement('details');details.id='radarMapDetails'",self.usability)
        self.assertNotIn('radarMapToggle',self.usability)
        self.assertNotIn('radarMapDetails',self.usability_css)
        self.assertNotIn('radar-map-details',self.usability_css)
        self.assertIn('#coverageTools .radar-figure{display:block',self.usability_css)

    def test_theme_has_isolated_surfaces_and_stacked_mobile_layout(self):
        self.assertIn('#coverageTools .radar-standalone-card',self.css)
        self.assertIn('#coverageTools .covered-standalone-card',self.css)
        self.assertIn('grid-template-columns:minmax(0,0.9fr) minmax(0,1.1fr)',self.css)
        self.assertIn('grid-template-columns:minmax(0,1fr);grid-template-areas:"radar" "covered" "trends";gap:14px',self.css)
        self.assertIn('background:var(--surface);box-shadow:var(--glass-shadow)',self.css)
        self.assertIn('#coverageTools .radar-standalone-card .radar-caption',self.css)


if __name__=='__main__':
    unittest.main()
