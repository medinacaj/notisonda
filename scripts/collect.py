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
import unicodedata
import socket
import time
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
import xml.etree.ElementTree as ET

try:
    import feedparser
except ModuleNotFoundError:
    import feedparser_compat as feedparser
import requests

from insights import trending_topics, write_feeds

# Agente identificable (convención "compatible" de lectores y buscadores) con enlace de contacto.
AGENT = "Mozilla/5.0 (compatible; RadarRSS/1.1; +https://github.com/medinacaj/radar-rss-publico)"
# Feeds de Substack y similares incluyen artículos completos y superan con frecuencia 2,5 MB.
MAX_BYTES = 8_000_000
HEADERS = {"User-Agent": AGENT,
           "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9, text/xml;q=0.9, */*;q=0.6",
           "Accept-Language": "es-CL,es;q=0.9,en;q=0.7"}
RETRY_STATUS = {429, 500, 502, 503, 504}
RETRY_WAIT_SECONDS = 4
# Prefijos del OPML que solo organizan las suscripciones. Los que informan al lector
# (SÁTIRA, OFICIAL, ANÁLISIS, etc.) se conservan a propósito.
ORGANIZATIONAL_PREFIX = re.compile(r'^\s*(?:MEDIO|REGIONAL)\s*[—–-]\s*')


def display_name(name: str) -> str:
    cleaned = ORGANIZATIONAL_PREFIX.sub('', name or '').strip()
    return cleaned or (name or '').strip()
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
    """Descarga con un reintento ante errores transitorios (429, 5xx, red)."""
    try:
        return _get_feed_once(url)
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else None
        if status not in RETRY_STATUS:
            raise
    except (requests.ConnectionError, requests.Timeout):
        pass
    time.sleep(RETRY_WAIT_SECONDS)
    return _get_feed_once(url)


def _get_feed_once(url: str) -> bytes:
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


def clean_google_news_title(title: str, credited_publisher: str) -> str:
    """Remove Google's trailing ' - Publisher' only when matching the credited outlet.

    Never strip arbitrary hyphenated headlines when source metadata is missing.
    """
    if not credited_publisher:
        return title
    expected = unicodedata.normalize('NFKC', credited_publisher).strip().casefold()
    for separator in (' - ', ' — ', ' – '):
        if separator not in title:
            continue
        heading, suffix = title.rsplit(separator, 1)
        if heading.strip() and unicodedata.normalize('NFKC', suffix).strip().casefold() == expected:
            return heading.strip()
    return title



def normalize_cached_google_titles(item: dict) -> None:
    """Clean cached Google headlines, even when the grouped lead is a direct RSS."""
    if item.get('is_radar') and isinstance(item.get('title'), str):
        item['title'] = clean_google_news_title(item['title'], str(item.get('publisher') or ''))
    for alternative in item.get('also_in') or []:
        if not isinstance(alternative, dict) or not isinstance(alternative.get('title'), str):
            continue
        # Alternative stories lack is_radar; Google links identify their origin.
        host = (urlsplit(str(alternative.get('url') or '')).hostname or '').lower()
        if host == 'news.google.com':
            alternative['title'] = clean_google_news_title(
                alternative['title'], str(alternative.get('publisher') or ''))


def make_item(entry, source: dict, now: datetime) -> dict | None:
    link = safe_web_url(entry.get('link') or '')
    title, _ = extract_html(entry.get('title') or '')
    if not link or not title:
        return None
    date = entry_date(entry)
    if date and date > now + timedelta(days=1):
        date = None  # Fecha futura incoherente: desconocida, no noticia del futuro.
    summary, _ = extract_html(entry.get('summary') or entry.get('description') or '')
    publisher = display_name(source['name'])
    if source['is_radar']:
        credited = entry.get('source') or {}
        if isinstance(credited, dict) and credited.get('title'):
            publisher = display_name(str(credited['title']))[:90]
        title = clean_google_news_title(title, publisher)
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



LATEST_COUNT=300
CHUNK_SIZE=300
MAX_ARTICLES=5000
MAX_CANDIDATES=7500
STOPWORDS=set("a al an and as at con de del el en es for from in is la las lo los no of on or para por que se su the to un una with y tras hoy ayer today latest news este esta fue hay says dijo".split())

def story_tokens(title: str) -> frozenset[str]:
    folded=''.join(c for c in unicodedata.normalize('NFKD',title.lower()) if not unicodedata.combining(c))
    return frozenset(t for t in re.findall(r'[a-z0-9]+',folded) if len(t)>2 and t not in STOPWORDS)

def story_instant(item: dict) -> datetime | None:
    raw=item.get('published_at') or item.get('first_seen_at')
    if not isinstance(raw,str):
        return None
    try:
        return datetime.fromisoformat(raw.replace('Z','+00:00'))
    except ValueError:
        return None

def group_related_articles(items: list[dict]) -> list[dict]:
    """Conservative similarity within 24 h and across independent feed sources."""
    groups=[]
    tokens_by_group=[]
    dates=[]
    inverted={}
    for original in items:
        item=dict(original)
        tokens=story_tokens(str(item.get('title') or ''))
        stamp=story_instant(item)
        best=None
        if len(tokens)>=5 and stamp:
            candidates=set()
            for token in tokens:
                candidates.update(inverted.get(token,()))
            for idx in sorted(candidates,reverse=True):
                old=tokens_by_group[idx]
                previous=dates[idx]
                if previous is None or abs((stamp-previous).total_seconds())>86400:
                    continue
                if set(item.get('source_ids',())) & set(groups[idx].get('source_ids',())):
                    continue
                intersection=len(tokens&old)
                if intersection>=5 and intersection / max(1,len(tokens|old)) >= .72:
                    best=idx
                    break
        if best is None:
            groups.append(item)
            tokens_by_group.append(tokens)
            dates.append(stamp)
            if len(tokens)>=5 and stamp:
                idx=len(groups)-1
                for token in tokens:
                    inverted.setdefault(token,[]).append(idx)
        else:
            lead=groups[best]
            for name in ('source_ids','categories'):
                lead[name]=list(dict.fromkeys([*lead.get(name,[]),*item.get(name,[])]))
            others=list(lead.get('also_in') or [])
            seen={x.get('url') for x in others}
            # Titular y origen de cada medio: permiten comparar cómo cuenta la historia cada uno.
            candidates=[{'id':item.get('id'),'url':item.get('url'),
                         'publisher':str(item.get('publisher') or item.get('source') or 'Otro medio')[:90],
                         'title':str(item.get('title') or '')[:250],
                         'source_id':(item.get('source_ids') or [None])[0],
                         'category':(item.get('categories') or [None])[0],
                         'published_at':item.get('published_at')}]
            candidates += [x for x in item.get('also_in',[]) if isinstance(x,dict)]
            for alt in candidates:
                url=alt.get('url')
                if safe_web_url(url or '') and url!=lead.get('url') and url not in seen:
                    others.append(alt)
                    seen.add(url)
            lead['also_in']=others[:12]
            if not lead.get('image') and item.get('image'):
                lead['image']=item['image']
            if not lead.get('summary') and item.get('summary'):
                lead['summary']=item['summary']
    return groups

def publish_partitioned(out: Path, articles: list[dict], generated: str) -> None:
    latest=articles[:LATEST_COUNT]
    tail=articles[LATEST_COUNT:]
    filenames=[]
    for idx,start in enumerate(range(0,len(tail),CHUNK_SIZE),1):
        name=f'archive-{idx:02d}.json'
        filenames.append(name)
        write_json(out/name,{'version':2,'generated_at':generated,'items':tail[start:start+CHUNK_SIZE]})
    write_json(out/'latest.json',{'version':2,'generated_at':generated,'items':latest})
    write_json(out/'meta.json',{'version':2,'generated_at':generated,
                               'total_articles':len(articles),'latest_count':len(latest),
                               'archive_files':filenames})

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
        # Reprocess old Google News titles, including alternatives under a direct RSS lead.
        normalize_cached_google_titles(item)
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

    ordered = sorted(merged.values(), key=lambda i: (i.get('published_at') or i.get('first_seen_at') or ''), reverse=True)
    articles = group_related_articles(ordered[:MAX_CANDIDATES])[:MAX_ARTICLES]
    for article in articles:
        # Cobertura: cuántas fuentes distintas publicaron la misma historia.
        article['coverage'] = max(1, len(set(article.get('source_ids') or [])))
    states = [fresh_status[x['id']] for x in sources]
    write_json(out / 'sources.json', {'version': 1, 'sources': sources,
                                      'categories': list(dict.fromkeys(s['category'] for s in sources))})
    write_json(out / 'articles.json', {'version': 2, 'generated_at': iso(now),
                                       'total_sources': len(sources), 'items': articles})
    publish_partitioned(out, articles, iso(now))
    write_json(out / 'trends.json', trending_topics(articles, now))
    write_feeds(out.parent / 'feeds', articles, sources, now)
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