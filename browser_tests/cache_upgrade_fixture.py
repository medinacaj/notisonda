"""Exercise real service-worker updates with local, deterministic failures."""
import json
import re
import socket
import threading
from urllib.parse import urlsplit

from playwright.sync_api import expect
import responsive_smoke as fixtures


def check_failed_upgrade(browser):
    source = (fixtures.WEB / 'sw.js').read_text()
    legacy = re.sub(r"const CACHE = '[^']+';", "const CACHE = 'notisonda-v4';", source, count=1)

    for failed_path, failure in (('/app.js', 'http'), ('/data/latest.json', 'network')):
        state = {'upgrade': False, 'failure': failure, 'offline': False, 'offline_attempts': 0}

        class Handler(fixtures.QuietHandler):
            def do_GET(self):
                try:
                    self.respond()
                except (BrokenPipeError, ConnectionResetError):
                    # addAll cancels outstanding requests when one download fails.
                    pass

            def respond(self):
                path = urlsplit(self.path).path
                if state['offline']:
                    state['offline_attempts'] += 1
                    self.connection.shutdown(socket.SHUT_RDWR)
                    self.connection.close()
                    return
                if state['upgrade'] and state['failure'] and path == failed_path:
                    if state['failure'] == 'network':
                        self.connection.shutdown(socket.SHUT_RDWR)
                        self.connection.close()
                    else:
                        self.send_error(503, 'Upgrade fixture: temporarily unavailable')
                    return
                if path == '/sw.js':
                    body = (source if state['upgrade'] else legacy).encode()
                    content_type = 'text/javascript'
                elif path.startswith('/data/') and path.rsplit('/', 1)[-1] in fixtures.RESPONSES:
                    body = json.dumps(fixtures.RESPONSES[path.rsplit('/', 1)[-1]]).encode()
                    content_type = 'application/json'
                else:
                    return super().do_GET()
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(len(body)))
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                self.wfile.write(body)

        server = fixtures.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        base = f'http://127.0.0.1:{server.server_port}/'
        threading.Thread(target=server.serve_forever, daemon=True).start()
        context = browser.new_context(service_workers='allow')
        context.route(re.compile(r'^https?://(?!127\.0\.0\.1:)'), lambda route: route.abort())
        page = context.new_page()

        def update():
            return page.evaluate("""async () => {
                const registration = await navigator.serviceWorker.getRegistration();
                const finished = new Promise(resolve => {
                    registration.addEventListener('updatefound', () => {
                        const worker = registration.installing;
                        worker.addEventListener('statechange', () => {
                            if (['activated','redundant'].includes(worker.state)) resolve(worker.state);
                        });
                    }, {once:true});
                });
                await registration.update();
                return Promise.race([finished, new Promise((_, reject) => {
                    setTimeout(() => reject(new Error('Worker update did not settle')), 15000);
                })]);
            }""")

        def offline_reload():
            # Drop every connection at the server: all engines exercise actual
            # fetch failures, without browser automation disabling SW navigation.
            attempts = state['offline_attempts']
            state['offline'] = True
            try:
                page.reload(wait_until='domcontentloaded')
                page.wait_for_function('() => typeof state !== "undefined" && state.ready')
                assert page.evaluate('state.items.length') == len(fixtures.ITEMS), (failed_path, 'offline news lost')
                expect(page.locator('#dashboardTitle')).to_have_text('Inicio')
                assert page.locator('.topbar').evaluate('node => getComputedStyle(node).display') == 'flex'
                assert state['offline_attempts'] > attempts, (failed_path, 'network failure not exercised')
            finally:
                state['offline'] = False

        try:
            page.goto(base)
            page.wait_for_function('() => typeof state !== "undefined" && state.ready')
            page.wait_for_function('() => !!navigator.serviceWorker.controller')
            page.wait_for_function("async () => (await caches.keys()).includes('notisonda-v4')")
            state['upgrade'] = True
            assert update() == 'redundant', (failed_path, 'incomplete worker replaced the working reader')
            assert page.evaluate("async () => (await caches.keys()).includes('notisonda-v4')"), failed_path
            offline_reload()
            state['failure'] = None
            assert update() == 'activated', (failed_path, 'complete upgrade failed')
            page.wait_for_function("async () => !(await caches.keys()).includes('notisonda-v4')")
            offline_reload()
        finally:
            context.close()
            server.shutdown()
            server.server_close()
