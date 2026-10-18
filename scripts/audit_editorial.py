#!/usr/bin/env python3
"""Non-destructive editorial quality signals from existing published JSON.

No requests to article sites; items are *candidates for human review*, not errors
or claims of factual inaccuracy. Reuses existing RSS metadata only.
"""
from __future__ import annotations
import argparse
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit

MAX_EXAMPLES = 15

def fold(text: object) -> str:
    norm=unicodedata.normalize("NFKD",str(text or "")).casefold()
    norm="".join(c for c in norm if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+"," ",norm).strip()

def inspect(sources: list[dict], feeds: list[dict], articles: list[dict]) -> dict:
    by_id={s["id"]:s for s in sources if isinstance(s,dict) and isinstance(s.get("id"),str)}
    urls=defaultdict(list)
    for s in sources:
        if not isinstance(s,dict):continue
        url=s.get("url")
        if isinstance(url,str):
            parsed=urlsplit(url)
            # Only exact normalized RSS URLs are duplicates. Do not conflate
            # publisher domains: several valid feeds can belong to one outlet.
            key=(parsed.scheme.lower(),parsed.netloc.lower(),parsed.path.rstrip("/"),parsed.query)
            urls[key].append(str(s.get("name") or s.get("id") or ""))
    duplicate_feeds=[names for names in urls.values() if len(names)>1]
    unresolved=[{"name":str(f.get("name") or f.get("source_id") or f.get("id") or "")[:90],
                 "state":str(f.get("state") or "")[:30]}
                for f in feeds if isinstance(f,dict) and f.get("state") in ("error","stale")]
    duplicated_titles=defaultdict(list)
    orphaned=0
    uncredited=0
    for article in articles:
        if not isinstance(article,dict):continue
        source_ids=[x for x in (article.get("source_ids") or []) if isinstance(x,str)]
        if any(x not in by_id for x in source_ids):orphaned+=1
        if article.get("is_radar") and not str(article.get("publisher") or "").strip():uncredited+=1
        title=fold(article.get("title"))
        if title and len(title)>25:
            duplicated_titles[title].append(article)
    review=[]
    for group in duplicated_titles.values():
        ids={x.get("id") for x in group}
        if len(ids)<2:continue
        outlets=sorted({str(x.get("publisher") or x.get("source") or "Otro") for x in group})
        review.append({"title":str(group[0].get("title") or "")[:180],
                       "stories":len(ids),"outlets":outlets[:6]})
    review.sort(key=lambda v:(-v["stories"],v["title"]))
    return {"sources":len(sources),"articles":len(articles),
            "duplicate_feed_urls":duplicate_feeds[:MAX_EXAMPLES],
            "unavailable_feeds":unresolved[:MAX_EXAMPLES],
            "unavailable_total":len(unresolved),
            "orphaned_article_sources":orphaned,
            "radar_without_credit":uncredited,
            "possible_duplicate_headlines":review[:MAX_EXAMPLES],
            "possible_duplicate_total":len(review)}

def safe_markdown(value: object) -> str:
    """Escape untrusted headlines/outlet names before GitHub renders them."""
    text=" ".join(str(value or "").split())[:180]
    special=set(chr(92)+"`*_{}[]()#+.!|<>-")
    return "".join(chr(92)+char if char in special else char for char in text)

def markdown(result: dict) -> str:
    lines=["## Revisión editorial orientativa de Radar RSS","",
           "Sin consultas externas. Las coincidencias requieren revisión humana;",
           "no constituyen prueba de error, plagio, desinformación o fallo de un medio.","",
           f"- Fuentes registradas: {result['sources']}",
           f"- Noticias almacenadas: {result['articles']}",
           f"- Fuentes con estado error/antigüedad: {result['unavailable_total']}",
           f"- Direcciones RSS exactamente duplicadas: {len(result['duplicate_feed_urls'])}",
           f"- Artículos con identificadores de fuente fuera del catálogo vigente: {result['orphaned_article_sources']}",
           f"- Noticias provenientes de radar sin atribución explícita: {result['radar_without_credit']}",
           f"- Titulares idénticos entre IDs distintos (candidatos): {result['possible_duplicate_total']}",""]
    if result["possible_duplicate_headlines"]:
        lines.append("### Coincidencias a revisar")
        for row in result["possible_duplicate_headlines"]:
            title=safe_markdown(row["title"])
            lines.append(f"- {row['stories']} notas · {title} · medios: {', '.join(safe_markdown(outlet) for outlet in row['outlets'])}")
    if result["unavailable_feeds"]:
        lines.append("\n### Feeds a comprobar (sin bajas automáticas)")
        for feed in result["unavailable_feeds"]:
            lines.append(f"- {safe_markdown(feed['name'])} ({safe_markdown(feed['state'])})")
    return "\n".join(lines)+"\n"

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data",type=Path,help="Directorio web/data tras recopilación")
    parser.add_argument("--report",type=Path,default=None)
    args=parser.parse_args()
    def load(name: str,key: str) -> list[dict]:
        doc=json.loads((args.data/name).read_text(encoding="utf-8"))
        value=doc.get(key)
        if not isinstance(value,list):raise ValueError(name+": estructura inesperada")
        return value
    result=inspect(load("sources.json","sources"),load("status.json","feeds"),
                   load("articles.json","items"))
    text=markdown(result)
    print(text)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(text,encoding="utf-8")

if __name__=="__main__":
    main()
