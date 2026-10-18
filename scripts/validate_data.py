#!/usr/bin/env python3
"""Validate article consistency before publishing on GitHub Pages."""
import json
import sys
from pathlib import Path

MAX_FAILED_SHARE=0.4

def check(root):
    def load(name):
        d=json.loads((root/name).read_text(encoding='utf8'))
        if not isinstance(d,dict):
            raise ValueError('Invalid document: '+name)
        return d
    full=load('articles.json')
    meta=load('meta.json')
    latest=load('latest.json')
    ids=[x.get('id') for x in full.get('items',[]) if isinstance(x,dict)]
    if not 50<=len(ids)<=2300 or len(ids)!=len(set(ids)):
        raise ValueError('History empty, duplicate, or oversized')
    joined=list(latest.get('items',[]))
    names=meta.get('archive_files')
    if not isinstance(names,list) or len(joined)>300:
        raise ValueError('Invalid latest or manifest')
    for name in names:
        if not isinstance(name,str) or not name.startswith('archive-') or not name.endswith('.json'):
            raise ValueError('Unsafe manifest path')
        part=load(name)
        if part.get('generated_at')!=meta.get('generated_at') or not isinstance(part.get('items'),list) or len(part['items'])>300:
            raise ValueError('Bad shard: '+name)
        joined.extend(part['items'])
    if [x.get('id') for x in joined]!=ids or len(ids)!=meta.get('total_articles'):
        raise ValueError('Shard content differs from archive')
    if full.get('generated_at')!=meta.get('generated_at') or latest.get('generated_at')!=meta.get('generated_at'):
        raise ValueError('Timestamps do not match')
    trends=load('trends.json')
    if not isinstance(trends.get('topics'),list):
        raise ValueError('trends.json without topics list')
    feed_dir=root.parent/'feeds'
    if not (feed_dir/'mas-cubierto.xml').is_file():
        raise ValueError('Output RSS feeds missing')
    feeds=load('status.json').get('feeds')
    if not load('sources.json').get('sources') or not feeds:
        raise ValueError('RSS status or sources absent')
    failed=sum(1 for x in feeds if isinstance(x,dict) and x.get('state')=='error')
    if failed/len(feeds)>MAX_FAILED_SHARE:
        # Una caída masiva suele ser un problema de red de GitHub, no de los medios:
        # se conserva la publicación anterior en vez de mostrar un estado alarmante.
        raise ValueError(f'Too many RSS errors: {failed}/{len(feeds)}; keeping previous deploy')
    print('JSON validated:',len(ids),'articles',len(names),'archive shards',failed,'RSS errors')

if __name__=='__main__':
    check(Path(sys.argv[1] if len(sys.argv)>1 else 'web/data'))
