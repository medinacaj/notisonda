"""Mejoras de la prueba de usuario: menú móvil, buscador global, tarjetas y accesibilidad."""
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def js_function(source, name):
    """Extrae una función de nivel superior de app.js para probarla aislada en Node."""
    start = source.index(f'function {name}(')
    depth, i = 0, source.index('{', start)
    while True:
        if source[i] == '{':
            depth += 1
        elif source[i] == '}':
            depth -= 1
            if depth == 0:
                return source[start:i + 1]
        i += 1


class UxReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / 'web/index.html').read_text(encoding='utf-8')
        cls.app = (ROOT / 'web/app.js').read_text(encoding='utf-8')
        cls.css = (ROOT / 'web/ux.css').read_text(encoding='utf-8')

    def test_mobile_drawer(self):
        self.assertIn('id="menuToggle"', self.html)
        self.assertIn('aria-controls="appSidebar"', self.html)
        self.assertIn('id="sidebarBackdrop"', self.html)
        self.assertIn('id="menuClose"', self.html)
        self.assertIn("matchMedia('(max-width: 950px)')", self.app)
        self.assertIn('sidebar.inert=mobile&&!next', self.app)
        self.assertIn('page.inert=next', self.app)
        self.assertIn('body.radar-hybrid.nav-open .sidebar', self.css)

    def test_resize_handle_inside_landmark(self):
        aside = self.html[self.html.index('<aside'):self.html.index('</aside>')]
        self.assertIn('id="sidebarResizeHandle"', aside)

    def test_search_lives_in_topbar(self):
        header = self.html[self.html.index('<header class="topbar">'):self.html.index('</header>')]
        self.assertIn('id="searchInput"', header)
        self.assertIn('role="search"', header)
        self.assertEqual(self.html.count('id="searchInput"'), 1)
        self.assertIn("if(state.search.trim()&&state.pageView!=='feed'){goTo('all');return;}", self.app)
        # La búsqueda carga el archivo completo y no reintenta en bucle si falla.
        self.assertIn('query.length>=3&&hasHistory()&&!state.historyLoading&&!state.historyFailed', self.app)

    def test_cards_without_filler(self):
        self.assertNotIn('Accede a la noticia original', self.app)
        self.assertNotIn("cover-fallback','RADAR'", self.app)
        self.assertIn("' no-cover'", self.app)
        self.assertIn('id="cardMenu"', self.html)
        self.assertIn('role="menu"', self.html)
        # library.js reemplaza este botón para archivar guardadas: la clase debe mantenerse.
        self.assertIn("'article-action article-save'", self.app)

    def test_status_not_over_news(self):
        self.assertNotIn('dashboardHealthText', self.html)
        self.assertNotIn("showFeedNotice(labels.join", self.app)
        main = self.html[self.html.index('<main'):self.html.index('</main>')]
        self.assertIn('id="statusBanner"', main)
        self.assertLess(main.index('id="statusBanner"'), main.index('id="dashboardView"'))

    def test_theme_follows_system_by_default(self):
        self.assertIn("THEME_EXPLICIT_KEY='radar-theme-explicit'", self.app)
        self.assertIn("return 'system';", js_function(self.app, 'initialTheme'))

    def test_neutral_editorial_brand_colors(self):
        hybrid = (ROOT / 'web/radar-hybrid.css').read_text(encoding='utf-8')
        self.assertNotIn('--accent:#1167b7', hybrid)
        self.assertIn('--accent:#1f5e5b', hybrid)
        self.assertIn('--bg:#f7f7f5', hybrid)
        self.assertIn('--bg:#181c1a', hybrid)
        newsroom = (ROOT / 'web/v13.css').read_text(encoding='utf-8')
        self.assertIn('background:var(--surface2);color:var(--text)', newsroom)
        self.assertIn('border-bottom:2px solid var(--text)', newsroom)
        self.assertNotIn('background:#102641', newsroom)

    def test_section_titles_have_clear_hierarchy(self):
        features = (ROOT / 'web/features.css').read_text(encoding='utf-8')
        # Portada: título de sección con peso, tipografía y guía visual distintos
        # de los titulares editoriales; el color sigue el tema elegido.
        self.assertRegex(features, r'(?s)body\.radar-hybrid \.dashboard-panel-head h2\{[^}]*font:760[^}]*var\(--font-ui\)')
        self.assertIn('border-inline-start:3px solid var(--accent)', features)
        self.assertRegex(features, r'(?s)body\.radar-hybrid \.briefing-section-head h2\{[^}]*font:750')
        self.assertRegex(features, r'(?s)body\.radar-hybrid \.dashboard-folder-head h3\{[^}]*font:750')
        self.assertIn('body.radar-hybrid .section-heading h1{', features)
        self.assertIn('@media(max-width:720px)', features)
        self.assertIn('body.radar-hybrid .dashboard-panel-head h2{font-size:22px}', features)
        self.assertIn('./features.css?v=1.2.1', self.html)
        for title in ('Lo más cubierto', 'Temas en alza', 'En portada', 'Últimas publicaciones', 'Por carpeta'):
            self.assertRegex(self.html, fr'<h2[^>]*>{re.escape(title)}</h2>')

    def test_history_manifest_is_not_silently_truncated(self):
        self.assertIn('.slice(0,32)', self.app)
        self.assertIn('function historyFiles()', self.app)

    def test_feed_has_level_one_heading(self):
        self.assertIn('<h1 id="feedHeading">', self.html)

    @unittest.skipUnless(shutil.which('node'), 'Node no disponible')
    def test_relative_dates_and_plain_language(self):
        script = '\n'.join([
            "const mk=()=>({});",
            js_function(self.app, 'ageDate'),
            js_function(self.app, 'friendlyFeedProblem'),
            "const now=Date.now(),ago=m=>new Date(now-m*60000).toISOString();",
            "console.log(JSON.stringify({",
            " m:ageDate(ago(25)),h:ageDate(ago(185)),y:ageDate(ago(60*30)),none:ageDate(null),",
            " forbidden:friendlyFeedProblem({state:'error',error:'HTTPError: 403 Client Error: Forbidden'}),",
            " big:friendlyFeedProblem({state:'error',error:'ValueError: Documento RSS demasiado grande'}),",
            " stale:friendlyFeedProblem({state:'stale'})}));",
        ])
        out = json.loads(subprocess.run(['node', '-e', script], capture_output=True, text=True, check=True).stdout)
        self.assertEqual(out['m'], 'Hace 25 min')
        self.assertEqual(out['h'], 'Hace 3 h')
        self.assertEqual(out['y'], 'Ayer')
        self.assertEqual(out['none'], 'Sin fecha')
        self.assertEqual(out['forbidden'], 'El medio no permite la lectura automática de su RSS.')
        self.assertEqual(out['big'], 'El RSS es demasiado pesado para procesarlo.')
        self.assertIn('más de un año', out['stale'])
        for text in out.values():
            self.assertFalse(re.search(r'HTTPError|ValueError', text))


if __name__ == '__main__':
    unittest.main()
