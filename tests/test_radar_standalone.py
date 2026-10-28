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
    def handle_starttag(self,tag,attrs):
        attr=dict(attrs)
        if tag not in ('br','img','input','link','meta','hr','source','area','wbr'):
            self.stack.append((tag,attr))
        if attr.get('id') in ('radarStage','radarCaption','radarFigure','coveredList','radarTitle','coveredTitle'):
            self.ancestors[attr['id']]=[a[1].get('class','') for a in self.stack if a[0]=='section']
    def handle_endtag(self,tag):
        if self.stack and self.stack[-1][0]==tag:self.stack.pop()


class RadarStandaloneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=(ROOT/'web/index.html').read_text(encoding='utf-8')
        cls.home=(ROOT/'web/homepage.js').read_text(encoding='utf-8')
        cls.css=(ROOT/'web/dimension.css').read_text(encoding='utf-8')

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

    def test_homepage_preserves_cards_without_reparenting_contents(self):
        self.assertIn("radarPanel.classList.add('radar-standalone-card')",self.home)
        self.assertIn("coveredPanel.classList.add('covered-standalone-card')",self.home)
        self.assertIn("tools.append(aside)",self.home)

    def test_theme_has_isolated_surfaces_and_stacked_mobile_layout(self):
        self.assertIn('#coverageTools .radar-standalone-card',self.css)
        self.assertIn('#coverageTools .covered-standalone-card',self.css)
        self.assertIn('grid-template-columns:minmax(0,0.9fr) minmax(0,1.1fr)',self.css)
        self.assertIn('grid-template-columns:minmax(0,1fr);gap:14px',self.css)
        self.assertIn('background:var(--surface);box-shadow:var(--glass-shadow)',self.css)
        self.assertIn('#coverageTools .radar-standalone-card .radar-caption',self.css)


if __name__=='__main__':
    unittest.main()
