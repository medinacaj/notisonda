#!/usr/bin/env python3
"""Verify the public GitHub Pages artifact after deployment (no RSS crawling)."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
import sys
import time
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen


def download(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "RadarRSS-DeployCheck/1.0", "Cache-Control": "no-cache"})
    with urlopen(request, timeout=15) as response:
        return response.read(8_000_000)


def verify(base_url: str, fetch=download, *, now: datetime | None = None, expected_generation: str | None = None) -> dict:
    """Confirm rendered shell and mutually consistent, recently generated public data."""
    base_url = base_url.rstrip("/") + "/"
    parsed = urlsplit(base_url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("La dirección de Pages debe usar HTTPS y no incluir credenciales")
    index = fetch(urljoin(base_url, "./")).decode("utf-8")
    if 'id="dashboardView"' not in index or "styles.css?v=" not in index:
        raise ValueError("La portada pública no contiene la aplicación esperada")
    data = {}
    for filename in ("sources.json", "latest.json", "meta.json", "status.json"):
        payload = json.loads(fetch(urljoin(base_url, "data/" + filename)).decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"{filename} no es un objeto JSON")
        data[filename] = payload
    sources = data["sources.json"].get("sources")
    categories = data["sources.json"].get("categories")
    latest = data["latest.json"].get("items")
    meta = data["meta.json"]
    status = data["status.json"]
    if not isinstance(sources, list) or len(sources) < 100:
        raise ValueError("Catálogo público vacío o incompleto")
    if (not isinstance(categories, list) or not categories
            or any(not isinstance(category, str) or not category.strip() for category in categories)
            or len({category.strip() for category in categories}) != len(categories)):
        raise ValueError("Las carpetas OPML deben tener nombres válidos, únicos y no estar vacías")
    if not isinstance(latest, list) or not 1 <= len(latest) <= 300:
        raise ValueError("No hay noticias recientes publicadas")
    if not isinstance(status.get("feeds"), list) or len(status["feeds"]) != len(sources):
        raise ValueError("Estado RSS inconsistente con el catálogo")
    generated = meta.get("generated_at")
    if generated != data["latest.json"].get("generated_at") or generated != status.get("checked_at"):
        raise ValueError("Los archivos públicos pertenecen a generaciones diferentes")
    if expected_generation is not None and generated != expected_generation:
        raise ValueError("La generación pública no coincide con la esperada")
    if not isinstance(meta.get("total_articles"), int) or meta["total_articles"] < len(latest):
        raise ValueError("El manifiesto de noticias es inconsistente")
    if meta.get("latest_count") != len(latest):
        raise ValueError("La cantidad de noticias recientes no coincide")
    try:
        timestamp = datetime.fromisoformat(generated.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as error:
        raise ValueError("Fecha de generación inválida") from error
    if timestamp.tzinfo is None:
        raise ValueError("Fecha de generación sin zona horaria")
    current = now or datetime.now(timezone.utc)
    age = current - timestamp
    if age > timedelta(hours=24) or age < -timedelta(minutes=10):
        raise ValueError(f"El portal está desactualizado: última generación {generated}")
    agenda_count = upcoming_count = pending_count = source_ok = source_total = None
    if meta.get('events_version') == 1:
        from events import is_upcoming, validate_document
        agenda = validate_document(json.loads(fetch(urljoin(base_url, 'data/events.json')).decode('utf-8')))
        if agenda['generated_at'] != generated:
            raise ValueError('La agenda pública pertenece a otra generación')
        agenda_count = len(agenda['items'])
        upcoming_count = sum(is_upcoming(item, current) for item in agenda['items'])
        pending_count = len(agenda['pending'])
        source_ok = sum(source['status'] == 'ok' for source in agenda['sources'])
        source_total = len(agenda['sources'])
    return {"events": agenda_count, "events_upcoming": upcoming_count, "events_pending": pending_count,
            "event_sources_ok": source_ok, "event_sources_total": source_total,
            "sources": len(sources), "news": len(latest), "total": meta["total_articles"],
            "generated_at": generated, "age_minutes": round(age.total_seconds() / 60)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Verificar archivos públicos tras desplegar Pages")
    parser.add_argument("url", help="Dirección HTTPS de GitHub Pages")
    parser.add_argument("--attempts", type=int, default=6)
    parser.add_argument("--delay", type=float, default=12)
    parser.add_argument("--expected-generation", help="Generación exacta del artefacto construido")
    args = parser.parse_args()
    if not 1 <= args.attempts <= 10 or not 0 <= args.delay <= 60:
        parser.error("Argumentos de reintento fuera de rango")
    last_error = None
    for attempt in range(1, args.attempts + 1):
        try:
            result = verify(args.url, expected_generation=args.expected_generation)
            serialized = json.dumps(result, ensure_ascii=False)
            print("Pages verificado: " + serialized)
            if os.environ.get('GITHUB_ACTIONS') == 'true':
                escaped = serialized.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')
                print('::notice title=Publicación verificada::' + escaped)
            summary = os.environ.get("GITHUB_STEP_SUMMARY")
            if summary:
                with open(summary, "a", encoding="utf-8") as report:
                    report.write(f"### RadarRRS · verificación pública correcta\n"
                                 f"- Fuentes: **{result['sources']}** · noticias recientes: **{result['news']}**\n"
                                 f"- Generación: **{result['generated_at']}**\n")
            return 0
        except Exception as error:
            last_error = error
            print(f"Intento {attempt}/{args.attempts}: {error}", file=sys.stderr, flush=True)
            if attempt < args.attempts:
                time.sleep(args.delay)
    print(f"ERROR: la publicación no pudo verificarse: {last_error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
