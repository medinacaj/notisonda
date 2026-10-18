#!/usr/bin/env python3
"""Validate a downloaded public-data backup before manual recovery.

Never trust downloaded artifact content simply because it originated in Actions.
The deploy workflow copies only validated articles.json and status.json.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

MAX_ITEMS=5000

def validate(folder: Path) -> dict:
    files={}
    for name in ("articles.json","status.json"):
        file=folder/name
        if not file.is_file() or file.stat().st_size>25_000_000:
            raise ValueError("Respaldo ausente o excesivo: "+name)
        doc=json.loads(file.read_text(encoding="utf-8"))
        if not isinstance(doc,dict):
            raise ValueError("Estructura inválida: "+name)
        files[name]=doc
    articles=files["articles.json"].get("items")
    feeds=files["status.json"].get("feeds")
    if not isinstance(articles,list) or not 50<=len(articles)<=MAX_ITEMS:
        raise ValueError("Cantidad de noticias fuera del rango esperado")
    ids=[item.get("id") for item in articles if isinstance(item,dict)]
    if len(ids)!=len(articles) or any(not isinstance(i,str) or not i for i in ids) or len(set(ids))!=len(ids):
        raise ValueError("Noticias con identificadores inválidos o duplicados")
    if not isinstance(feeds,list) or len(feeds)<2:
        raise ValueError("El respaldo no contiene suficientes estados RSS")
    if not isinstance(files["articles.json"].get("generated_at"),str):
        raise ValueError("Fecha de generación inexistente")
    return {"articles":len(articles),"feeds":len(feeds)}

if __name__=="__main__":
    if len(sys.argv)!=2:
        sys.exit("Uso: python scripts/validate_restore.py CARPETA")
    try:
        print("Respaldo validado:",validate(Path(sys.argv[1])))
    except Exception as error:
        sys.exit("Respaldo rechazado: "+str(error))
