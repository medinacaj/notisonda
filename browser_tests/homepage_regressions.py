"""Offline tests for the homepage carousel and secondary coverage tools."""
import os
from copy import deepcopy
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import responsive_smoke as fixtures


def main():
    # Nine sections all have stories; culture is older than the other sections.
    # It must still receive one visible editorial slot without bypassing preferences.
    fixtures.CATEGORIES = (*fixtures.CATEGORIES, '08 - Monagas', '09 - Cultura')
    for index in (7, 8):
        category = fixtures.CATEGORIES[index]
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
                assert page.locator('#dashboardRecent .dashboard-recent-row').first.get_attribute('data-topic') == '3'
                assert page.locator('#dashboardRecent .dashboard-recent-row').nth(1).get_attribute('data-topic') == '9'
                assert page.locator('#dashboardRecent .dashboard-recent-row[data-topic="4"]').count() >= 1
                expect(page.locator('#dashboardRecent .latest-news-image').first).to_have_js_property('naturalWidth', 400)
                dims = page.locator('#dashboardRecent').evaluate('n => ({width:n.clientWidth,card:n.firstElementChild.getBoundingClientRect().width})')
                visible = round(dims['width']/dims['card'])
                assert visible == (3 if width == 1440 else 1), dims
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 2")
                assert page.evaluate("document.querySelector('.newsroom-primary-column').getBoundingClientRect().width >= document.getElementById('newsroomColumns').clientWidth - 2")
                expect(page.locator('.newsroom-secondary-column')).to_be_hidden()
                expect(page.locator('#latestCarouselNext')).to_be_enabled()
                page.locator('#latestCarouselNext').click()
                page.wait_for_function("() => document.getElementById('dashboardRecent').scrollLeft > 0")
                page.locator('#latestCarouselPrevious').click()
                page.wait_for_function("() => document.getElementById('dashboardRecent').scrollLeft < 2")
                expect(page.locator('#coverageTools')).not_to_have_attribute('open', '')
                page.locator('#coverageTools > summary').click()
                expect(page.locator('#radarMapDetails')).to_be_attached()
                assert page.locator('#radarFigure').count() == 1
                page.locator('#coverageTools > summary').click()
                page.evaluate('window.scrollTo(0,0)')
                page.screenshot(path=str(screenshots / f'homepage-{width}.png'), full_page=True)
                # Hiding a source wins over editorial placement.
                page.evaluate("localStorage.setItem('radar-hidden-sources', JSON.stringify(['medio-8']))")
                page.reload()
                expect(page.locator('#dashboardRecent .dashboard-recent-row').first).to_be_visible()
                assert page.locator('#dashboardRecent .dashboard-recent-row[data-topic="9"]').count() == 0
                # An explicit personal homepage also wins over international/culture placement.
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
    print('OK: homepage carousel, three desktop cards, mobile swipe, international and Chile, secondary tools')

if __name__ == '__main__':
    main()
