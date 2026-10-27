"""Offline tests for small reader-facing improvements; no media requests."""
import os
import re
import threading
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright, expect
import responsive_smoke as fixtures


def main():
    fixtures.SOURCES[0]['name'] = 'MEDIO — Diario de prueba'
    server = ThreadingHTTPServer(('127.0.0.1', 0), fixtures.QuietHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            options = {'headless': True, 'args': ['--no-sandbox']}
            if os.environ.get('RADAR_CHROMIUM_EXECUTABLE'):
                options['executable_path'] = os.environ['RADAR_CHROMIUM_EXECUTABLE']
            browser = p.chromium.launch(**options)
            context = browser.new_context(viewport={'width':375,'height':812}, service_workers='block')
            context.route('**/*', lambda r: r.continue_() if r.request.url.startswith('http://127.0.0.1:') else r.abort())
            page = context.new_page()
            page.route('**/data/**', fixtures.make_route)
            base = f'http://127.0.0.1:{server.server_port}/'
            page.goto(base+'#noticias')
            expect(page.locator('#articleGrid .article-card').first).to_be_visible()
            expect(page.locator('#sourceSelect option[value="medio-0"]')).to_have_text('Diario de prueba (3)')
            expect(page.locator('#articleGrid .article-read-toggle').first).to_have_attribute('aria-label',re.compile('^Marcar como leída:'))
            page.evaluate("location.hash='#inicio'")
            expect(page.locator('#radarMapToggle')).to_be_visible()
            expect(page.locator('#radarMapDetails')).not_to_have_attribute('open','')
            expect(page.locator('#radarFigure')).to_be_hidden()
            page.locator('#radarMapToggle').click()
            expect(page.locator('#radarFigure')).to_be_visible()
            page.locator('#radarMapToggle').click()
            page.set_viewport_size({'width':1440,'height':900})
            expect(page.locator('#radarMapToggle')).to_be_visible()
            expect(page.locator('#radarFigure')).to_be_hidden()
            page.locator('#coveredList .covered-count').last.focus()
            page.keyboard.press('Tab')
            expect(page.locator('#radarMapToggle')).to_be_focused()
            page.keyboard.press('Enter')
            expect(page.locator('#radarFigure')).to_be_visible()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print('OK: accessible article actions, source counts, optional map in mobile/desktop Inicio')

if __name__ == '__main__':
    main()
