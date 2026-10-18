"""Señales editoriales calculadas en cada recolección, sin servicios externos.

- trending_topics: palabras y pares de palabras cuyo uso en titulares crece frente
  a los días anteriores ("temas en alza").
- write_feeds: RSS de salida por carpeta y de "Lo más cubierto".
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
import math
from pathlib import Path
import re
import unicodedata
from xml.sax.saxutils import escape

SITE_URL = 'https://medinacaj.github.io/radar-rss-publico/'

# Palabras demasiado frecuentes o genéricas para describir un tema.
TREND_STOPWORDS = set('''
a al ante antes aqui asi aun bajo cada casi como con contra cual cuando de del desde donde dos durante el ella ellos en entre era es esa ese eso esta este esto estos fue fueron ha han hasta hay hoy la las le les lo los mas me mientras muy ni no nos nueva nuevas nuevo nuevos o otra otro para pero por porque que quien se segun ser si sin sobre son su sus tambien tan tras tres un una uno unos y ya
ano anos dia dias semana mes meses hora horas minuto vez veces parte caso casos forma tiempo mundo pais paises
dice dicen dijo afirma asegura anuncia anuncio revela explica advierte confirma pide busca llega deja tiene hace puede podria sera seria estan esta
gobierno presidente ministro nacional general nuevo nueva mayor primer primera ultimo ultima ultimas ultimos claves clave todo todos toda todas mejor mejores
noticias noticia video fotos foto minuto directo vivo hoy ayer manana
sabe analisis opinion columna editorial entrevista resumen claves cronica reportaje especial exclusiva
chile venezuela latinoamerica america internacional tecnologia inteligencia artificial
the a an and are as at be by for from has have how in into is it its new of on or that the this to was what when why will with you your
'''.split())
TOKEN = re.compile(r'[a-z0-9ñ]+')


def fold(text: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFKD', text.lower()) if not unicodedata.combining(c))


def _words(title: str) -> list[tuple[str, str]]:
    """Pares (forma plegada, forma original) de las palabras útiles de un titular."""
    out = []
    for raw in re.findall(r"[\wÀ-ÿ]+", title or ''):
        key = fold(raw)
        if len(key) < 4 or key.isdigit() or key in TREND_STOPWORDS:
            out.append(('', ''))  # corta los pares de palabras
            continue
        out.append((key, raw))
    return out


def _instant(item: dict) -> datetime | None:
    raw = item.get('published_at') or item.get('first_seen_at')
    try:
        return datetime.fromisoformat(str(raw).replace('Z', '+00:00'))
    except (TypeError, ValueError):
        return None


def trending_topics(articles: list[dict], now: datetime, limit: int = 10) -> dict:
    """Temas cuyo número de historias en 24 h supera claramente su promedio diario previo."""
    window_start = now - timedelta(hours=24)
    base_start = now - timedelta(days=8)
    current: Counter = Counter()
    baseline: Counter = Counter()
    sources: dict[str, set] = defaultdict(set)
    samples: dict[str, list] = defaultdict(list)
    surfaces: dict[str, Counter] = defaultdict(Counter)
    positions: dict[str, list] = defaultdict(list)  # las primeras palabras de un titular suelen nombrar el tema
    for item in articles:
        when = _instant(item)
        if not when or when < base_start or when > now + timedelta(hours=1):
            continue
        words = _words(str(item.get('title') or ''))
        terms = {k for k, _ in words if k}
        first_at = {}
        for i, (k, _) in enumerate(words):
            if k:
                first_at.setdefault(k, i)
        for i, ((a, ra), (b, rb)) in enumerate(zip(words, words[1:])):
            if a and b:
                terms.add(f'{a} {b}')
                first_at.setdefault(f'{a} {b}', i)
                surfaces[f'{a} {b}'][f'{ra} {rb}'] += 1
        for k, raw in words:
            if k:
                surfaces[k][raw] += 1
        for term in terms:
            if when >= window_start:
                current[term] += 1
                positions[term].append(first_at.get(term, 9))
                sources[term].update(item.get('source_ids') or [])
                if len(samples[term]) < 3:
                    samples[term].append(item.get('id'))
            else:
                baseline[term] += 1
    scored = []
    for term, count in current.items():
        if count < 3 or len(sources[term]) < 3:
            continue
        daily = baseline[term] / 7
        score = (count - daily) / math.sqrt(daily + 1)
        if ' ' in term:
            score *= 1.25  # un par de palabras describe mejor un tema que una sola
        if score >= 2:
            avg_position = sum(positions[term]) / max(1, len(positions[term]))
            scored.append((round(score, 6), -avg_position, term))
    scored.sort(reverse=True)
    chosen: list[dict] = []
    covered: set[str] = set()
    for score, _, term in scored:
        words = set(term.split())
        if words & covered:
            continue
        label = surfaces[term].most_common(1)[0][0] if surfaces[term] else term
        daily = baseline[term] / 7
        chosen.append({
            'term': term, 'label': label, 'stories': current[term], 'sources': len(sources[term]),
            'previous_daily': round(daily, 1), 'is_new': baseline[term] == 0, 'sample_ids': samples[term],
        })
        covered |= words
        if len(chosen) >= limit:
            break
    return {'version': 1, 'generated_at': now.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'window_hours': 24, 'baseline_days': 7, 'topics': chosen}


def _rss(title: str, description: str, link: str, items: list[dict], now: datetime) -> str:
    rows = []
    for item in items:
        when = _instant(item)
        pub = f'<pubDate>{format_datetime(when)}</pubDate>' if when else ''
        coverage = item.get('coverage') or 1
        extra = f' · Cubierta por {coverage} medios' if coverage > 1 else ''
        rows.append(
            '<item>'
            f'<title>{escape(str(item.get("title") or "Sin título"))}</title>'
            f'<link>{escape(str(item.get("url") or ""))}</link>'
            f'<guid isPermaLink="false">radar-{escape(str(item.get("id") or ""))}</guid>'
            f'<description>{escape(str(item.get("summary") or "") + extra)}</description>'
            f'<source url="{escape(SITE_URL)}">{escape(str(item.get("publisher") or item.get("source") or ""))}</source>'
            f'{pub}</item>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
            f'<title>{escape(title)}</title><link>{escape(link)}</link>'
            f'<description>{escape(description)}</description><language>es</language>'
            f'<lastBuildDate>{format_datetime(now)}</lastBuildDate><ttl>360</ttl>'
            + ''.join(rows) + '</channel></rss>\n')


def feed_slug(category: str) -> str:
    text = fold(re.sub(r'^\d+\s*-\s*', '', category or 'otros'))
    return re.sub(r'[^a-z0-9]+', '-', text).strip('-') or 'otros'


def write_feeds(folder: Path, articles: list[dict], sources: list[dict], now: datetime) -> list[str]:
    """RSS de salida: una selección curada que otros lectores pueden seguir."""
    folder.mkdir(parents=True, exist_ok=True)
    written = []
    recent = [a for a in articles if (_instant(a) or now) >= now - timedelta(hours=48)]
    top = sorted(recent, key=lambda a: ((a.get('coverage') or 1), str(a.get('published_at') or '')), reverse=True)
    top = [a for a in top if (a.get('coverage') or 1) >= 2][:30]
    files = {'mas-cubierto.xml': _rss('Radar RSS · Lo más cubierto',
                                      'Historias publicadas por más medios en las últimas 48 horas.',
                                      SITE_URL, top, now)}
    for category in dict.fromkeys(s['category'] for s in sources):
        items = [a for a in articles if category in (a.get('categories') or [])][:50]
        name = re.sub(r'^\d+\s*-\s*', '', category)
        files[f'{feed_slug(category)}.xml'] = _rss(f'Radar RSS · {name}', f'Noticias recientes de {name}.',
                                                   SITE_URL + '#categoria/' + category.replace(' ', '%20'), items, now)
    for name, body in files.items():
        tmp = folder / (name + '.tmp')
        tmp.write_text(body, encoding='utf-8')
        tmp.replace(folder / name)
        written.append(name)
    return written
