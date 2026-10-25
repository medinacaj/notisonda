"""Puente entre el recolector de eventos y la web estática de Radar RSS.

Subcomandos:
    recover   elige, para cada ámbito (Biobío y nacional), el snapshot más reciente
              entre el del repositorio, un directorio (artefacto del workflow) y el
              publicado en GitHub Pages, y lo deja en eventos/data/.
    export    escribe en la carpeta pública:
                - eventos.json            versión compacta que lee la interfaz
                - eventos/biobio.json     snapshot completo (continuidad del rastreo)
                - eventos/nacional.json   snapshot completo (continuidad del rastreo)

Solo usa la biblioteca estándar. No inventa datos: exporta lo que dejó actualizar.py
(y los eventos semilla verificados manualmente), sin completar campos.
"""
import argparse
import hashlib
import json
import os
import sys
from datetime import date, datetime, timedelta
from urllib.request import Request, urlopen

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
PAGES_BASE = "https://medinacaj.github.io/radar-rss-publico/data/eventos/"
LIMIT = 20_000_000
SCOPES = {
    "biobio": {"label": "Región del Biobío", "snapshot": "crawled_events.json",
               "communes": "communes.json"},
    "nacional": {"label": "Todo Chile", "snapshot": "national_events.json",
                 "communes": "chile_communes.json"},
}
PUBLIC_FIELDS = ("title", "description", "date", "end_date", "time", "end_time", "venue",
                 "address", "commune", "category", "audience", "access", "price_value",
                 "price_status", "status", "source", "official", "discovered_at", "changed_at")
MAX_TEXT = 600


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _write_json(path, data, compact=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        if compact:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        else:
            json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def valid_snapshot(doc):
    return (isinstance(doc, dict) and isinstance(doc.get("events"), list)
            and isinstance(doc.get("generated_at"), str) and isinstance(doc.get("summary"), dict))


def _fetch_published(url, timeout=25):
    req = Request(url, headers={"User-Agent": "RadarRSS-Eventos/1.0 (recuperación de estado)"})
    with urlopen(req, timeout=timeout) as res:
        content = res.read(LIMIT + 1)
    if len(content) > LIMIT:
        raise ValueError("snapshot publicado demasiado grande")
    return json.loads(content)


def recover(from_dir=None, from_url=PAGES_BASE, fetcher=_fetch_published, data_dir=DATA_DIR, log=print):
    """Deja en data_dir el snapshot más reciente de cada ámbito. Devuelve el origen elegido."""
    chosen = {}
    for scope, meta in SCOPES.items():
        local_path = os.path.join(data_dir, meta["snapshot"])
        options = []
        local = _read_json(local_path)
        if valid_snapshot(local):
            options.append(("repositorio", local))
        if from_dir:
            art = _read_json(os.path.join(from_dir, meta["snapshot"]))
            if valid_snapshot(art):
                options.append(("artefacto", art))
        if from_url:
            try:
                pub = fetcher(from_url + scope + ".json")
                if valid_snapshot(pub):
                    options.append(("pages", pub))
            except Exception as exc:  # sin red o sin publicación previa: se usa lo local
                log("No se pudo recuperar %s publicado: %s" % (scope, exc))
        if not options:
            chosen[scope] = None
            continue
        origin, doc = max(options, key=lambda o: o[1]["generated_at"])
        if origin != "repositorio":
            _write_json(local_path, doc)
        chosen[scope] = origin
        log("Eventos %s: se usa el snapshot de %s (%s)" % (scope, origin, doc["generated_at"]))
    return chosen


def _safe_url(value):
    return value if isinstance(value, str) and value.startswith(("https://", "http://")) else None


def _text(value):
    if value is None:
        return None
    value = str(value).strip()
    return value[:MAX_TEXT] if value else None


def event_id(scope, ev):
    key = "|".join([scope, ev.get("source_url") or "", ev.get("date") or "", ev.get("title") or ""])
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]


def public_event(scope, ev, places, origin="crawl"):
    out = {k: _text(ev.get(k)) if isinstance(ev.get(k), str) else ev.get(k) for k in PUBLIC_FIELDS}
    out["id"] = event_id(scope, ev)
    out["scope"] = scope
    out["origin"] = origin
    out["official"] = bool(ev.get("official"))
    out["source_url"] = _safe_url(ev.get("source_url"))
    out["image_url"] = _safe_url(ev.get("image_url"))
    place = places.get(ev.get("commune")) or {}
    out["province"] = place.get("province")
    out["region"] = ev.get("region") or place.get("region") or ("Biobío" if scope == "biobio" else None)
    out["tags"] = [str(t) for t in (ev.get("tags") or [])][:8]
    out["sources"] = [{"name": _text(s.get("name")), "url": _safe_url(s.get("url"))}
                      for s in (ev.get("sources") or []) if _safe_url(s.get("url"))][:12]
    out["changes"] = [{k: _text(c.get(k)) for k in ("field", "old_value", "new_value", "source", "changed_at")}
                      for c in (ev.get("changes") or [])][:20]
    return out


def _is_current(ev, today):
    last = ev.get("end_date") or ev.get("date") or ""
    return last >= today


def export(out_dir, data_dir=DATA_DIR, config_dir=CONFIG_DIR, today=None, now=None):
    """Escribe eventos.json (compacto) y los snapshots completos. Devuelve el resumen."""
    today = today or (date.today() - timedelta(days=1)).isoformat()
    payload = {"version": 1, "generated_at": now or datetime.now().replace(microsecond=0).isoformat(),
               "scopes": {}, "communes": {}, "events": []}
    seen = set()
    for scope, meta in SCOPES.items():
        cfg = _read_json(os.path.join(config_dir, meta["communes"])) or {}
        communes = cfg.get("communes") or []
        places = {c["name"]: c for c in communes if c.get("name")}
        if scope == "biobio":
            payload["communes"]["biobio"] = [{"name": c["name"], "province": c.get("province")}
                                             for c in communes]
        snap = _read_json(os.path.join(data_dir, meta["snapshot"]))
        events = []
        if valid_snapshot(snap):
            _write_json(os.path.join(out_dir, "eventos", scope + ".json"), snap, compact=True)
            events = [public_event(scope, ev, places) for ev in snap["events"] if _is_current(ev, today)]
            summary = snap["summary"]
            payload["scopes"][scope] = {
                "label": meta["label"], "generated_at": snap["generated_at"],
                "sources_attempted": summary.get("sources_attempted"),
                "sources_ok": summary.get("sources_ok"), "sources_failed": summary.get("sources_failed")}
        else:
            payload["scopes"][scope] = {"label": meta["label"], "generated_at": None}
        if scope == "biobio":
            seed = _read_json(os.path.join(data_dir, "seed_events.json")) or {}
            events += [public_event(scope, ev, places, origin="seed")
                       for ev in seed.get("events", []) if _is_current(ev, today)]
        for ev in events:
            key = (scope, (ev["title"] or "").casefold(), ev["date"])
            if key in seen or not ev["title"] or not ev["date"]:
                continue
            seen.add(key)
            payload["events"].append(ev)
        payload["scopes"][scope]["events"] = sum(1 for e in payload["events"] if e["scope"] == scope)
    payload["events"].sort(key=lambda e: (e["date"], e.get("time") or "99", e["title"]))
    _write_json(os.path.join(out_dir, "eventos.json"), payload, compact=True)
    return {scope: info["events"] for scope, info in payload["scopes"].items()}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    rec = sub.add_parser("recover", help="recupera el snapshot más reciente de cada ámbito")
    rec.add_argument("--from-dir", help="directorio con snapshots (p. ej. artefacto del workflow)")
    rec.add_argument("--no-pages", action="store_true", help="no consultar GitHub Pages")
    exp = sub.add_parser("export", help="escribe los JSON públicos")
    exp.add_argument("--out", required=True, help="carpeta pública, p. ej. web/data")
    args = ap.parse_args(argv)
    if args.cmd == "recover":
        recover(from_dir=args.from_dir, from_url=None if args.no_pages else PAGES_BASE)
        return 0
    counts = export(args.out)
    print("Eventos publicados: " + ", ".join("%s %d" % kv for kv in counts.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
