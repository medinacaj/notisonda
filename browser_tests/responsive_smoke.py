#!/usr/bin/env python3
"""Browser-level responsive smoke tests with deterministic mock RSS data.

Run: python browser_tests/responsive_smoke.py
Only test code depends on Playwright; production has no new dependencies.
"""
from __future__ import annotations

import json
import ssl
import subprocess
import sys
import tempfile
import threading
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
REPORTS = ROOT / "test-results" / "responsive"
WIDTHS = (320, 375, 390, 430, 768, 1024, 1440)
CATEGORIES = (
    "01 - Inteligencia Artificial", "02 - Tecnología", "03 - Internacionales",
    "04 - Chile", "05 - Venezuela", "06 - Latinoamérica",
)
STAMP = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
SOURCES = [
    {"id": f"medio-{i}", "name": f"Medio de referencia {i}", "category": cat,
     "url": "https://example.com/rss", "website": "https://example.com", "is_radar": False}
    for i, cat in enumerate(CATEGORIES)
]
ITEMS = [
    {"id": f"noticia-{i}", "title": (
        "Titular de referencia con palabras extensas para verificar el ajuste "
        f"responsivo de la lectura en pantallas de diferentes dimensiones {i}"
    ), "url": f"https://example.com/noticias/{i}", "image": None,
     "summary": "Resumen informativo de ejemplo para comprobar distribución de tarjetas.",
     "published_at": STAMP, "first_seen_at": STAMP,
     "publisher": SOURCES[i % 6]["name"], "source": SOURCES[i % 6]["name"],
     "source_ids": [SOURCES[i % 6]["id"]],
     "categories": [CATEGORIES[i % 6]], "coverage": 2, "is_radar": False}
    for i in range(18)
]
RESPONSES = {
    "sources.json": {"version": 1, "sources": SOURCES, "categories": list(CATEGORIES)},
    "latest.json": {"version": 2, "generated_at": STAMP, "items": ITEMS},
    "status.json": {"version": 1, "checked_at": STAMP, "feeds": [], "errors": 0, "stale": 0},
    "meta.json": {"version": 2, "generated_at": STAMP, "total_articles": len(ITEMS),
                  "latest_count": len(ITEMS), "archive_files": []},
    "trends.json": {"version": 1, "generated_at": STAMP, "window_hours": 24,
                    "baseline_days": 7, "topics": []},
}

class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def log_message(self, *args):
        pass

def check_visible_boxes(page, selectors, label):
    findings = page.evaluate("""selectors => {
      const viewport = window.innerWidth;
      const bad = [];
      for (const selector of selectors) {
        const node = document.querySelector(selector);
        if (!node || node.hidden) continue;
        const style = getComputedStyle(node);
        if (style.display === 'none' || style.visibility !== 'visible') continue;
        const rect = node.getBoundingClientRect();
        if (rect.width < 1 || rect.height < 1) continue;
        if (rect.left < -2 || rect.right > viewport + 2) {
          bad.push({selector, left: +rect.left.toFixed(1), right: +rect.right.toFixed(1), viewport});
        }
      }
      const scrollingWidth = document.documentElement.scrollWidth;
      if (scrollingWidth > viewport + 2) bad.push({scrollingWidth, viewport});
      return bad;
    }""", selectors)
    if findings:
        raise AssertionError(f"{label}: desbordamiento detectado: {findings}")

def check_header_overlap(page, label):
    overlaps = page.evaluate("""() => {
      const selectors = ['#menuToggle', '.topbar-caption', '#searchToggle',
        '.topbar-actions', '.topbar-search'];
      const rects = selectors.map(s => document.querySelector(s)).filter(Boolean)
        .filter(el => getComputedStyle(el).display !== 'none')
        .map(el => ({name: el.id || el.className, r: el.getBoundingClientRect()}))
        .filter(x => x.r.width > 1 && x.r.height > 1);
      const bad = [];
      for (let i = 0; i < rects.length; i++)
        for (let j = i + 1; j < rects.length; j++) {
          const a = rects[i], b = rects[j];
          const x = Math.min(a.r.right,b.r.right) - Math.max(a.r.left,b.r.left);
          const y = Math.min(a.r.bottom,b.r.bottom) - Math.max(a.r.top,b.r.top);
          if (x > 3 && y > 3) bad.push([a.name,b.name]);
        }
      return bad;
    }""")
    if overlaps:
        raise AssertionError(f"{label}: controles superpuestos: {overlaps}")

def check_accessibility_contract(page, label):
    """Deterministic structural and accessible-name guard; not a full WCAG audit."""
    failures = page.evaluate("""() => {
      const issues = [];
      if (document.documentElement.lang !== 'es') issues.push('Falta idioma español');
      const ids = [...document.querySelectorAll('[id]')].map(n => n.id);
      if (ids.length !== new Set(ids).size) issues.push('IDs repetidos');
      const selectors = ['#menuToggle','#searchToggle','#settingsButton','#themeToggle',
        '#refreshNow','#loadMore','#markAllVisible'];
      for (const selector of selectors) {
        const el = document.querySelector(selector);
        if (!el) { issues.push('Control ausente ' + selector); continue; }
        const name = (el.getAttribute('aria-label') || el.getAttribute('title') ||
          el.textContent || '').trim();
        if (!name) issues.push('Control sin nombre ' + selector);
      }
      for (const id of ['dashboardTitle','briefingTitle','feedHeading']) {
        if (document.querySelector('#'+id)?.tagName !== 'H1')
          issues.push('Jerarquía sin H1: '+id);
      }
      return issues;
    }""")
    if failures:
        raise AssertionError(f"{label}: {failures}")


def make_route(route):
    name = Path(urlsplit(route.request.url).path).name
    payload = RESPONSES.get(name)
    if payload is None:
        route.continue_()
    else:
        route.fulfill(status=200, content_type="application/json; charset=utf-8",
                      body=json.dumps(payload, ensure_ascii=False))

def main():
    browser_name = sys.argv[1] if len(sys.argv) > 1 else "chromium"
    if browser_name not in ("chromium", "firefox", "webkit"):
        raise ValueError(f"Unsupported engine: {browser_name}")
    output = REPORTS / browser_name
    output.mkdir(parents=True, exist_ok=True)
    # Run over HTTPS like GitHub Pages; WebKit enforces upgrade-insecure-requests
    # and will otherwise attempt TLS against a plain HTTP test server.
    tls = tempfile.TemporaryDirectory()
    cert_dir = Path(tls.name)
    cert = cert_dir / "cert.pem"
    key = cert_dir / "key.pem"
    subprocess.run([
        "openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
        "-keyout", str(key), "-out", str(cert), "-days", "1",
        "-subj", "/CN=localhost", "-addext", "subjectAltName=IP:127.0.0.1,DNS:localhost",
    ], check=True, capture_output=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    tls_context.load_cert_chain(certfile=str(cert), keyfile=str(key))
    server.socket = tls_context.wrap_socket(server.socket, server_side=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"https://127.0.0.1:{server.server_port}/"
    try:
        with sync_playwright() as p:
            engine = getattr(p, browser_name)
            browser = engine.launch(headless=True, args=["--no-sandbox"] if browser_name == "chromium" else [])
            try:
                for width in WIDTHS:
                    mobile = width <= 768
                    context = browser.new_context(
                        viewport={"width": width, "height": 812 if mobile else 900},
                        is_mobile=mobile and browser_name != "firefox",
                        has_touch=mobile, device_scale_factor=1,
                        service_workers="block", ignore_https_errors=True,
                    )
                    page = context.new_page()
                    javascript_errors = []
                    page.on("pageerror", lambda error: javascript_errors.append(str(error)))
                    page.on("console", lambda msg: javascript_errors.append("console: " + msg.text) if msg.type == "error" else None)
                    page.route("**/data/**", make_route)
                    try:
                        page.goto(base + "#inicio", wait_until="load")
                        page.locator("#dashboardView:not([hidden])").wait_for(timeout=15000)
                        page.locator("#dashboardFeature .article-card").first.wait_for(timeout=15000)
                        check_visible_boxes(page, [".topbar", ".topbar-caption", ".topbar-actions",
                            "#dashboardView", ".dashboard-panel-head", "#dashboardFeature",
                            "#dashboardFeature .article-card"], f"portada {width}px")
                        check_header_overlap(page, f"{browser_name} barra superior {width}px")
                        check_accessibility_contract(page, f"{browser_name} portada {width}px")
                        if width in (320, 768, 1440):
                            page.screenshot(path=str(output / f"portada-{width}.png"), full_page=False)

                        page.evaluate("location.hash = '#noticias'")
                        page.locator("#feedView:not([hidden])").wait_for(timeout=10000)
                        page.locator("#articleGrid .article-card").first.wait_for(timeout=10000)
                        check_visible_boxes(page, [".topbar", ".topbar-actions", ".filter-bar",
                            ".filter-controls", ".mode-tabs", "#articleGrid",
                            "#articleGrid .article-card"], f"listado {width}px")
                        if width <= 950:
                            page.locator("#menuToggle").click()
                            page.locator("body.nav-open").wait_for(timeout=2000)
                            page.keyboard.press("Escape")
                            page.locator("body:not(.nav-open)").wait_for(timeout=2000)
                        if width <= 710:
                            page.locator("#searchToggle").click()
                            page.locator("#topbarSearch").wait_for(state="visible", timeout=2000)
                            check_visible_boxes(page, ["#topbarSearch", "#searchInput"],
                                                f"búsqueda {width}px")
                            page.locator("#searchToggle").click()

                        page.locator("#settingsButton").click()
                        page.locator("#settingsDialog[open]").wait_for(timeout=3000)
                        check_visible_boxes(page, ["#settingsDialog", ".settings-top",
                            ".settings-body", ".settings-footer"], f"configuración {width}px")
                        page.locator("#closeSettings").click()

                        page.evaluate("location.hash = '#resumen'")
                        page.locator("#briefingView:not([hidden])").wait_for(timeout=10000)
                        check_visible_boxes(page, [".briefing-head", ".briefing-actions",
                            ".briefing-sections"], f"resumen {width}px")
                        print(f"OK [{browser_name}]: {width}px, portada, listado, navegación, búsqueda, configuración, resumen", flush=True)
                    except Exception:
                        print(f"DEBUG [{browser_name}] {width}px: JS={javascript_errors}", flush=True)
                        print("DEBUG document:", page.evaluate("() => ({hash: location.hash, ready: document.readyState, dashboardHidden: document.querySelector('#dashboardView')?.hidden, bodyClass: document.body.className, cardCount: document.querySelectorAll('#dashboardFeature .article-card').length})"), flush=True)
                        page.screenshot(path=str(output / f"fallo-{width}.png"), full_page=False)
                        raise
                    finally:
                        context.close()
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        tls.cleanup()

if __name__ == "__main__":
    main()
