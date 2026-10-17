"""Parser RSS/Atom básico sin dependencias para pruebas fuera de línea.

Si está instalado `feedparser`, collect.py utiliza la implementación más robusta.
"""
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from time import struct_time
import xml.etree.ElementTree as ET


def name(tag):
    return tag.split('}', 1)[-1].lower()


def children(el, *tags):
    wanted = set(tags)
    return [x for x in list(el) if name(x.tag) in wanted]


def get_text(el, *tags):
    for child in children(el, *tags):
        if child.text and child.text.strip():
            return child.text.strip()
        # RSS description HTML may be wrapped in embedded markup
        if list(child):
            return ''.join(ET.tostring(e, encoding='unicode') for e in list(child))
    return ''


def parse_date(s):
    if not s:
        return None
    try:
        dt = parsedate_to_datetime(s)
    except (ValueError, TypeError, IndexError):
        try: dt = datetime.fromisoformat(s.strip().replace('Z', '+00:00'))
        except ValueError: return None
    if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).timetuple()


def parse(payload):
    class Result(dict):
        @property
        def entries(self): return self['entries']
    try: root = ET.fromstring(payload)
    except ET.ParseError:
        return Result(bozo=True, entries=[])
    root_name = name(root.tag)
    entries = []
    if root_name == 'feed':
        nodes = children(root, 'entry')
        mode = 'atom'
    elif root_name in ('rss','rdf'):
        channel = (children(root, 'channel') or [root])[0]
        nodes = children(channel, 'item')
        if not nodes and channel is not root:
            nodes = children(root, 'item')
        mode = 'rss'
    else:
        return Result(bozo=True, entries=[])
    for el in nodes:
        link = get_text(el,'link') if mode == 'rss' else ''
        if not link:
            for anchor in children(el,'link'):
                if anchor.attrib.get('rel','alternate') == 'alternate' and anchor.attrib.get('href'):
                    link = anchor.attrib['href']; break
        raw_date = get_text(el,'pubdate','published','updated','date','modified')
        entry = {
            'title':get_text(el,'title'),
            'link':link,
            'summary':get_text(el,'summary','description','encoded','content'),
            'published':raw_date,
            'published_parsed':parse_date(raw_date),
            'media_content':[], 'media_thumbnail':[], 'links':[],
        }
        for media in children(el,'thumbnail'):
            if media.attrib.get('url'):
                entry['media_thumbnail'].append({'url':media.attrib['url']})
        for media in children(el,'content'):
            if media.attrib.get('url'):
                entry['media_content'].append({'url':media.attrib['url']})
        for media in children(el,'enclosure'):
            entry['links'].append({'href':media.attrib.get('url'),'type':media.attrib.get('type','')})
        entries.append(entry)
    return Result(bozo=False, entries=entries)