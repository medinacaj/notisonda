#!/usr/bin/env python3
"""Recopila RSS/Atom públicos, genera JSON estático para GitHub Pages.

Sin base de datos ni claves. No incorpora feeds enviados por visitantes.
Las URL autorizadas proceden exclusivamente de sources/feeds.opml.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from hashlib import sha256
from html.parser import HTMLParser
import ipaddress
import json
from pathlib import Path
import re
import socket
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
import xml.etree.ElementTree as ET

try:
    import feedparser
except ModuleNotFoundError:
    import feedparser_compat as feedparser
import requests

AGENT = "RadarRSS/1.0 (+public static news aggregation; RSS reader)"
MAX_BYTES = 2_500_000
HEADERS = {"User-Agent": AGENT, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*;q=0.6"}
NOW = lambda: datetime.now(timezone.utc)


def iso(dt: datetime | None) -> str | None:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z') if dt else None


def parse_opml(path: str | Path) -> list[dict]:
    root = ET.parse(path).getroot()
    if root.tag.lower() != 'opml':
        raise ValueError('El archivo no tiene un elemento OPML.')
    body = root.find('body')
    if body is None:
        raise ValueError('Falta body en el archivo OPML.')
    out = []
    urls = set()
    for folder in body.findall('outline'):
        category = folder.get('text') or folder.get('title') or 'Otros'
        for node in folder.iter('outline'):
            url = (node.get('xmlUrl') or '').strip()
            if not url:
                continue
            if not urlsplit(url).scheme in ('http', 'https'):
                continue
            if url in urls:
                continue
            urls.add(url)
            name = node.get('title') or node.get('text') or urlsplit(url).hostname or 'RSS'
            website = safe_web_url(node.get('htmlUrl', '')) or ''
            out.append({
                'id': sha256(url.encode()).hexdigest()[:16],
                'name': name,
                'category': category,
                'url': url,
                'website': website,
                'is_radar': (urlsplit(url).hostname or '').lower() == 'news.google.com',
            })
    return out


def safe_web_url(url: str) -> str | None:
    try:
        p = urlsplit((url or '').strip())
        if p.scheme.lower() not in ('http', 'https') or not p.hostname or p.username or p.password:
            return None
        return url
    except ValueError:
        return None


def is_public_host(host: str) -> bool:
    """Bloquea accesos locales/privados en el colector, incluidos redireccionamientos.
    No sustituye un proxy anti-SSRF si se aceptan URL de terceros en el futuro.
    """
    if not host or host.lower() in ('localhost', 'localhost.localdomain') or host.lower().endswith(('.local', '.internal')):
        return False
    try:
        addresses = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
        if not addresses:
            return False
        return all(ipaddress.ip_address(row[4][0]).is_global for row in addresses)
    except (OSError, ValueError):
        return False


def get_feed(url: str) -> bytes:
    target = url
    for _ in range(5):
        parsed = urlsplit(target)
        if parsed.scheme not in ('https', 'http') or not parsed.hostname or not is_public_host(parsed.hostname):
            raise ValueError('Destino RSS no público / no autorizado')
        response = requests.get(target, headers=HEADERS, stream=True, timeout=(5, 14), allow_redirects=False)
        try:
            if response.status_code in (301, 302, 303, 307, 308):
                redirect = response.headers.get('Location')
                if not redirect:
                    raise ValueError('Redirección sin destino')
                from urllib.parse import urljoin
                target = urljoin(target, redirect)
                continue
            response.raise_for_status()
            parts = []
            total = 0
            for part in response.iter_content(chunk_size=32_768):
                total += len(part)
                if total > MAX_BYTES:
                    raise ValueError('Documento RSS demasiado grande')
                parts.append(part)
            return b''.join(parts)
        finally:
            response.close()
    raise ValueError('Demasiadas redirecciones')


class ExtractText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text = []
        self.image = None
        self.ignore = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.ignore += 1
        if tag == 'img' and not self.image:
            for key, value in attrs:
                if key in ('src', 'data-src') and safe_web_url(value or ''):
                    self.image = value
                    break

    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.ignore:
            self.ignore -= 1

    def handle_data(self, data):
        if not self.ignore:
            self.text.append(data)


def extract_html(html: str) -> tuple[str, str | None]:
    obj = ExtractText()
    try:
        obj.feed(html or '')
        return re.sub(r'\s+', ' ', ' '.join(obj.text)).strip()[:290], obj.image
    except Exception:
        return '', None


def entry_date(entry) -> datetime | None:
    for key in ('published_parsed', 'updated_parsed', 'created_parsed'):
        val = entry.get(key)
        if val:
            try:
                from calendar import timegm
                return datetime.fromtimestamp(timegm(val), timezone.utc)
            except (ValueError, OverflowError, TypeError):
                pass
    for key in ('published', 'updated'):
        if entry.get(key):
            try:
                dt = parsedate_to_datetime(entry[key])
                return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)
            except (TypeError, ValueError, IndexError):
                pass
    return None


def strip_tracking(link: str) -> str:
    p = urlsplit(link)
    params = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
              if not (k.lower().startswith('utm_') or k.lower() in ('fbclid', 'gclid'))]
    return urlunsplit((p.scheme, p.netloc.lower(), p.path.rstrip('/') or '/', urlencode(params), ''))


def find_image(entry) -> str | None:
    for key in ('media_content', 'media_thumbnail', 'links'):
        for item in entry.get(key, []) or []:
            image = item.get('url') or item.get('href')
            if not safe_web_url(image or ''):
                continue
            mediatype = item.get('type', '')
            if key != 'links' or mediatype.startswith('image/'):
                return image
    _, embedded = extract_html(entry.get('summary') or entry.get('description') or '')
    return embedded


def make_item(entry, source: dict, now: datetime) -> dict | None:
    link = safe_web_url(entry.get('link') or '')
    title, _ = extract_html(entry.get('title') or '')
    if not link or not title:
        return None
    date = entry_date(entry)
    if date and date > now + timedelta(days=1):
        date = None  # Fecha futura incoherente: desconocida, no noticia del futuro.
    summary, _ = extract_html(entry.get('summary') or entry.get('description') or '')
    publisher = source['name']
    if source['is_radar']:
        credited = entry.get('source') or {}
        if isinstance(credited, dict) and credited.get('title'):
            publisher = str(credited['title'])[:90]
    clean_link = strip_tracking(link)
    return {
        'id': sha256(clean_link.encode('utf-8')).hexdigest()[:20],
        'title': title[:250],
        'url': link,
        'image': find_image(entry),
        'summary': summary,
        'published_at': iso(date),
        'first_seen_at': iso(now),
        'publisher': publisher[:90],
        'source': source['name'],
        'source_ids': [source['id']],
        'categories': [source['category']],
        'is_radar': source['is_radar'],
    }


def get_one(source: dict, now: datetime, per_feed: int) -> tuple[list[dict], dict]:
    status = {'id': source['id'], 'name': source['name'], 'category': source['category'], 'state': 'error',
              'count': 0, 'last_published_at': None, 'last_success_at': None, 'error': None}
    try:
        raw = get_feed(source['url'])
        parsed = feedparser.parse(raw)
        if parsed.get('bozo') and not parsed.entries:
            raise ValueError('RSS/Atom no válido o sin datos interpretables')
        entries = list(parsed.entries[:per_feed])
        items = [r for e in entries if (r := make_item(e, source, now)) is not None]
        dates = [entry_date(e) for e in parsed.entries if entry_date(e)]
        last = max(dates) if dates else None
        status.update(state='ok' if items else 'empty', count=len(items),
                      last_published_at=iso(last), last_success_at=iso(now))
        if last and last < now - timedelta(days=365):
            status['state'] = 'stale'  # Revisión humana: no eliminar automáticamente.
        return items, status
    except Exception as exc:
        # Mostrar la causa resumida sin exponer datos de entorno ni claves.
        status['error'] = f'{type(exc).__name__}: {str(exc)[:160]}'
        return [], status


def load_json(path: Path, fallback: dict) -> dict:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return fallback


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    tmp.replace(path)


def collect(opml: Path, out: Path, days: int, workers: int, max_per_feed: int) -> dict:
    now = NOW()
    sources = parse_opml(opml)
    if not sources:
        raise ValueError('El OPML no contiene feeds utilizables.')
    prior_articles = load_json(out / 'articles.json', {}).get('items', [])
    prior_status = {x['id']: x for x in load_json(out / 'status.json', {}).get('feeds', []) if x.get('id')}
    current_items: list[dict] = []
    fresh_status: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pending = {pool.submit(get_one, feed, now, max_per_feed): feed for feed in sources}
        for future in as_completed(pending):
            feed = pending[future]
            items, st = future.result()
            old = prior_status.get(feed['id'], {})
            if not st['last_success_at']:
                st['last_success_at'] = old.get('last_success_at')
            if not st['last_published_at']:
                st['last_published_at'] = old.get('last_published_at')
            fresh_status[feed['id']] = st
            current_items.extend(items)
            print(f"[{st['state']:>5}] {feed['name'][:57]} ({st['count']})", flush=True)

    merged = {}
    cutoff = now - timedelta(days=days)
    valid_ids = {x['id'] for x in sources}
    for item in prior_articles + current_items:
        date_txt = item.get('published_at') or item.get('first_seen_at')
        try:
            dt = datetime.fromisoformat(date_txt.replace('Z', '+00:00'))
            if dt < cutoff:
                continue
        except (ValueError, AttributeError):
            continue
        item['source_ids'] = [sid for sid in item.get('source_ids', []) if sid in valid_ids]
        if not item['source_ids']:
            continue
        key = item.get('id')
        if not key:
            continue
        if key in merged:
            previous = merged[key]
            item['source_ids'] = list(dict.fromkeys(previous['source_ids'] + item['source_ids']))
            item['categories'] = list(dict.fromkeys(previous['categories'] + item['categories']))
            if not item.get('published_at') and previous.get('published_at'):
                item['published_at'] = previous['published_at']
            if not item.get('image') and previous.get('image'):
                item['image'] = previous['image']
            if not item.get('summary') and previous.get('summary'):
                item['summary'] = previous['summary']
            item['first_seen_at'] = previous.get('first_seen_at', item['first_seen_at'])
        merged[key] = item

    articles = sorted(merged.values(), key=lambda i: (i.get('published_at') or i.get('first_seen_at') or ''), reverse=True)[:2300]
    states = [fresh_status[x['id']] for x in sources]
    write_json(out / 'sources.json', {'version': 1, 'sources': sources,
                                      'categories': list(dict.fromkeys(s['category'] for s in sources))})
    write_json(out / 'articles.json', {'version': 1, 'generated_at': iso(now),
                                       'total_sources': len(sources), 'items': articles})
    write_json(out / 'status.json', {'version': 1, 'checked_at': iso(now),
                                     'feeds': states, 'errors': sum(s['state'] == 'error' for s in states),
                                     'stale': sum(s['state'] == 'stale' for s in states)})
    result = {'sources': len(sources), 'articles': len(articles), 'ok': sum(s['state'] == 'ok' for s in states),
              'error': sum(s['state'] == 'error' for s in states), 'stale': sum(s['state'] == 'stale' for s in states)}
    print('RESULTADO', result, flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--opml', type=Path, default=Path('sources/feeds.opml'))
    parser.add_argument('--out', type=Path, default=Path('web/data'))
    parser.add_argument('--days', type=int, default=45)
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--max-per-feed', type=int, default=12)
    opts = parser.parse_args()
    collect(opts.opml, opts.out, min(max(opts.days, 1), 365), min(max(opts.workers, 1), 12),
            min(max(opts.max_per_feed, 1), 50))