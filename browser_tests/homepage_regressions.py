"""Offline tests for the homepage carousel and visible coverage tools."""
import os
from copy import deepcopy
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import responsive_smoke as fixtures


def main():
    # Spanish culture sources share International; no separate ninth folder.
    fixtures.CATEGORIES = (*fixtures.CATEGORIES, '08 - Monagas')
    for index in (7, 8):
        category = fixtures.CATEGORIES[7 if index == 7 else 2]
        fixtures.SOURCES.append({'id': f'medio-{index}', 'name': f'Medio de referencia {index}',
                                 'category': category, 'url': 'https://example.com/rss',
                                 'website': 'https://example.com', 'is_radar': False})
        story = deepcopy(fixtures.ITEMS[1])
        story.update(id=f'noticia-extra-{index}', title=f'Noticia de {category}',
                     source_ids=[f'medio-{index}'], categories=[category],
                     publisher=f'Medio de referencia {index}', source=f'Medio de referencia {index}')
        if index == 8:
            story['published_at'] = '2026-10-23T00:00:00Z'
        fixtures.ITEMS.append(story)
    fixtures.RESPONSES['sources.json']['categories'] = list(fixtures.CATEGORIES)
    fixtures.RESPONSES['meta.json']['total_articles'] = len(fixtures.ITEMS)
    fixtures.RESPONSES['meta.json']['latest_count'] = len(fixtures.ITEMS)
    fixtures.RESPONSES['trends.json']['topics'] = [{'label':'Inteligencia artificial','stories':9,'sources':4,'is_new':True},{'label':'Tecnología','stories':6,'sources':3,'previous_daily':2},{'label':'Concepción y Biobío','stories':4,'sources':3,'is_new':True}]
    server = ThreadingHTTPServer(('127.0.0.1', 0), fixtures.QuietHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    screenshots = Path(os.environ.get('RADAR_SCREENSHOTS', '/tmp/radar-homepage'))
    screenshots.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as p:
            options = {'headless': True, 'args': ['--no-sandbox']}
            if os.environ.get('RADAR_CHROMIUM_EXECUTABLE'):
                options['executable_path'] = os.environ['RADAR_CHROMIUM_EXECUTABLE']
            browser = p.chromium.launch(**options)
            for width in (375, 1440):
                context = browser.new_context(viewport={'width': width, 'height': 900}, service_workers='block', reduced_motion='reduce')
                context.route('**/*', lambda r: r.continue_() if r.request.url.startswith('http://127.0.0.1:') else r.abort())
                page = context.new_page()
                page.route('**/data/**', fixtures.make_route)
                page.route('https://example.com/radar-fixture-cover.svg', lambda r: r.fulfill(status=200,content_type='image/svg+xml',body='<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200"><rect width="400" height="200" fill="#cfded9"/></svg>'))
                page.goto(f'http://127.0.0.1:{server.server_port}/#inicio')
                expect(page.locator('#dashboardRecent .dashboard-recent-row').first).to_be_visible()
                expect(page.locator('#latestCarouselNext')).to_be_visible()
                assert page.locator('#dashboardRecent .dashboard-recent-row').count() >= 3
                assert page.locator('#libraryFolderNav .system-folder-link').count() == 8
                assert page.locator('#libraryFolderNav [data-topic="9"]').count() == 0
                assert page.locator('#dashboardRecent .dashboard-recent-row[data-topic="4"]').count() >= 1
                expect(page.locator('#dashboardFeature > .article-card')).to_have_count(1)
                assert page.locator('#dashboardFeature .article-card').get_attribute('data-topic') == '3'
                dims = page.locator('#dashboardRecent').evaluate('n => ({width:n.clientWidth,card:n.firstElementChild.getBoundingClientRect().width})')
                visible = round(dims['width']/dims['card'])
                assert visible == (3 if width == 1440 else 1), dims
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 2")
                expect(page.locator('#newsroomColumns')).to_be_hidden()
                expect(page.locator('.newsroom-secondary-column')).to_be_hidden()
                expect(page.locator('#latestCarouselNext')).to_be_enabled()
                page.locator('#latestCarouselNext').click()
                page.wait_for_function("() => document.getElementById('dashboardRecent').scrollLeft > 0")
                page.locator('#latestCarouselPrevious').click()
                page.wait_for_function("() => document.getElementById('dashboardRecent').scrollLeft < 2")
                expect(page.locator('#dashboardView #coverageTools')).to_be_visible()
                # La ficha se mantiene después del carrusel «En un vistazo».
                order=page.evaluate("""() => {
                    const feature=document.querySelector('.dashboard-feature-panel');
                    const latest=document.querySelector('.homepage-latest');
                    const radar=document.querySelector('#coverageTools');
                    return [feature,latest,radar].map(node=>[...node.parentNode.children].indexOf(node));
                }""")
                assert order[0]<order[1]<order[2],order
                assert page.locator('#radarFigure').is_visible()
                expect(page.locator('#trendsPanel')).to_be_visible()
                fixtures.check_visible_boxes(page,['#coverageTools','.home-insight-card','#trendChips .trend-chip'],f'cobertura {width}px')
                expect(page.locator('#coveredList .covered-item').first).to_be_visible()
                expect(page.locator('#radarFigure')).to_be_visible()
                expect(page.locator('#radarStage svg')).to_be_visible()
                expect(page.locator('#radarCaption')).to_be_visible()
                assert page.locator('#radarMapDetails, #radarMapToggle').count() == 0
                page.evaluate("goTo('briefing')")
                expect(page.locator('#coverageTools')).to_be_hidden()
                assert page.locator('#radarFigure').count() == 1
                page.evaluate("goTo('home')")
                page.wait_for_function("() => state.pageView==='dashboard'")
                page.evaluate('window.scrollTo(0,0)')
                page.screenshot(path=str(screenshots / f'homepage-{width}.png'), full_page=True)
                page.evaluate("goTo('03 - Internacionales')")
                expect(page.locator('#articleGrid [data-article-id="noticia-extra-8"]')).to_be_visible()
                # Hiding a source wins over editorial placement.
                page.evaluate("localStorage.setItem('radar-hidden-sources', JSON.stringify(['medio-8']))")
                page.reload()
                expect(page.locator('#articleGrid .article-card').first).to_be_visible()
                assert page.locator('#articleGrid [data-article-id="noticia-extra-8"]').count() == 0
                page.evaluate("location.hash = '#inicio'")
                # An explicit personal homepage also wins over editorial placement.
                page.evaluate("localStorage.setItem('radar-v12-preferences', JSON.stringify({mine:true,categories:['04 - Chile'],briefing:'mine'}))")
                page.reload()
                expect(page.locator('#dashboardRecent .dashboard-recent-row').first).to_be_visible()
                topics=page.locator('#dashboardRecent .dashboard-recent-row').evaluate_all("nodes => nodes.map(n=>n.dataset.topic)")
                assert topics and set(topics) == {'4'}, topics
                context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print('OK: homepage carousel, three desktop cards, mobile swipe, international and Chile, homepage coverage tools')

if __name__ == '__main__':
    main()
