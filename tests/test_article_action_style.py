"""Controls for article actions: no circular permanent buttons."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ArticleActionVisualTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css=(ROOT/'web/dimension.css').read_text(encoding='utf-8')
        cls.app=(ROOT/'web/app.js').read_text(encoding='utf-8')

    def test_actions_use_flat_rectangular_buttons_with_accessible_hit_areas(self):
        self.assertIn('/* Acciones de noticia: iconos compactos sin círculos ni rellenos permanentes. */',self.css)
        segment=self.css.split('/* Acciones de noticia: iconos compactos sin círculos ni rellenos permanentes. */',1)[1]
        self.assertIn('border-radius:9px',segment)
        self.assertIn('min-width:44px;min-height:44px',segment)
        self.assertIn('background:transparent;color:var(--muted)',segment)
        self.assertIn(':focus-visible',segment)
        self.assertIn('.article-more[aria-expanded="true"]',segment)

    def test_existing_article_action_behavior_unchanged(self):
        for token in ("article-action article-save","article-action article-more",
                      "article-action article-read-toggle","aria-pressed",
                      "aria-haspopup","aria-expanded"):
            self.assertIn(token,self.app)


if __name__ == '__main__':
    unittest.main()
