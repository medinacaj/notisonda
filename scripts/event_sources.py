#!/usr/bin/env python3
"""Official direct calendars adapted to Radar's single events-v1 agenda.

Selective adaptation of medinacaj/eventos-biobio@f6d9eef (PR88): explicit
JSON-LD/ICS/Tribe facts only; no imported seeds, snapshots or inferred years.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit
from zoneinfo import ZoneInfo

import requests
import collect
import events

MAX_PAGE_BYTES = 500_000
MAX_EVENTS_PER_PAGE = 100
MAX_REQUESTS = 60
MAX_PAGES_PER_SOURCE = 4
EVENT_HINT = re.compile(r'evento|event|agenda|cartelera|actividad|concierto|obra|festival|feria|taller|espectaculo|programacion|calendar|\.ics(?:\?|$)', re.I)


def registered_url(value, source, base=None):
    """Only HTTPS URLs on explicitly registered publisher hosts, never credentials."""
    if not isinstance(value,str) or len(value)>4000:return None
    value=urljoin(base or source['url'],value)
    try:
        parts=urlsplit(value)
        allowed=source.get('hosts') or [urlsplit(source['url']).hostname]
        if (parts.scheme!='https' or parts.username or parts.password or parts.port not in (None,443)
                or not parts.hostname or parts.hostname.lower() not in allowed):return None
        if not collect.page_image_host(value):return None
        return collect.strip_tracking(value)
    except ValueError:return None


class _Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links=[];self.title=[];self.heading=[];self._capture=None;self._anchor=None

    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='a' and attrs.get('href'):self._anchor=[attrs['href'],[]]
        if tag=='link' and attrs.get('href') and 'text/calendar' in attrs.get('type',''):
            self.links.append((attrs['href'],'calendar'))
        if tag=='title':self._capture=self.title
        elif tag=='h1' and not self.heading:self._capture=self.heading

    def handle_endtag(self,tag):
        if tag=='a' and self._anchor:
            self.links.append((self._anchor[0],''.join(self._anchor[1])));self._anchor=None
        if tag in ('title','h1'):self._capture=None

    def handle_data(self,data):
        if self._capture is not None:self._capture.append(data)
        if self._anchor:self._anchor[1].append(data)


def discover_links(text, page_url, source):
    page=_Page();page.feed(text)
    links=[]
    for raw,label in page.links:
        target=registered_url(raw,source,page_url)
        if target and target!=collect.strip_tracking(page_url) and EVENT_HINT.search(raw+' '+label):
            if target not in links:links.append(target)
    # A visible Tribe marker identifies an official structured calendar endpoint.
    if 'tribe-events' in text.lower():
        root='https://'+urlsplit(page_url).netloc
        target=registered_url(root+'/wp-json/tribe/events/v1/events?per_page=50',source)
        if target and target not in links:links.insert(0,target)
    return links[:MAX_PAGES_PER_SOURCE*3]


def _structured_row(objects, target, page_url, source, now, kind='jsonld'):
    title=next((obj.get('name') for obj in objects if isinstance(obj.get('name'),str)),None)
    if not title:return None
    entry={'title':title,'link':target}
    payload=json.dumps(objects,ensure_ascii=False).replace('<','\\u003c')
    html='<script type="application/ld+json">'+payload+'</script>'
    row=events.extract_event(entry,source,now,html=html)
    if row and row['date_evidence']:
        row['date_evidence']['url']=page_url
        row['date_evidence']['kind']=kind
    return row


def _jsonld_rows(text, page_url, source, now):
    page=events._html(text);objects=[]
    for block in page.json_blocks:
        try:objects.extend(events._jsonld_events(json.loads(block)))
        except (ValueError,TypeError,RecursionError):continue
    grouped=defaultdict(list)
    for obj in objects[:MAX_EVENTS_PER_PAGE]:
        raw=obj.get('url') or obj.get('@id')
        if raw is None and len(objects)==1:raw=page_url
        target=registered_url(raw,source,page_url)
        if not target:continue
        obj=dict(obj)
        for key in ('url','@id','mainEntityOfPage'):
            identity=obj.get(key)
            if isinstance(identity,str):obj[key]=urljoin(page_url,identity)
            elif isinstance(identity,dict):
                obj[key]={name:urljoin(page_url,value) if name in ('url','@id') and isinstance(value,str) else value
                          for name,value in identity.items()}
        # Preserve explicit identities so conflicting identities cannot be rescued.
        if obj not in grouped[target]:grouped[target].append(obj)
    rows=[]
    for target,group in grouped.items():
        row=_structured_row(group,target,page_url,source,now)
        if row:rows.append(row)
    if not objects and collect.strip_tracking(page_url)!=collect.strip_tracking(source['url']):
        parsed=_Page();parsed.feed(text)
        title=' '.join(parsed.heading or parsed.title).strip()[:500]
        row=events.extract_event({'title':title,'link':page_url},source,now)
        if row:rows.append(row)  # unstructured detail remains undated pending
    return rows


def _ics_text(value):
    return re.sub(r'\\([nN,;\\])',lambda match:'\n' if match[1] in 'nN' else match[1],value)


def _ics_date(value, params, source_zone):
    if params.get('VALUE')=='DATE' or re.fullmatch(r'\d{8}',value):
        if not re.fullmatch(r'\d{8}',value):raise ValueError('Invalid all-day calendar date')
        return datetime.strptime(value,'%Y%m%d').date().isoformat(),True
    if not re.fullmatch(r'\d{8}T\d{6}Z?',value):raise ValueError('Invalid calendar date')
    moment=datetime.strptime(value.rstrip('Z'),'%Y%m%dT%H%M%S')
    zone=timezone.utc if value.endswith('Z') else ZoneInfo(params.get('TZID') or source_zone)
    return moment.replace(tzinfo=zone).astimezone(ZoneInfo(source_zone)).isoformat(),False


def _ics_rows(text, page_url, source, now):
    if 'BEGIN:VCALENDAR' not in text[:2000]:return []
    unfolded=re.sub(r'\r?\n[ \t]','',text)
    rows=[]
    for block in unfolded.split('BEGIN:VEVENT')[1:MAX_EVENTS_PER_PAGE+1]:
        if 'END:VEVENT' not in block:continue
        fields={}
        for line in block.split('END:VEVENT',1)[0].splitlines():
            key,separator,value=line.partition(':')
            if not separator:continue
            bits=key.split(';');params={}
            for bit in bits[1:]:
                name,_,param=bit.partition('=');params[name.upper()]=param.strip('"')
            fields.setdefault(bits[0].upper(),(_ics_text(value.strip()),params))
        uid=fields.get('UID',('',{}))[0];title=fields.get('SUMMARY',('',{}))[0]
        status=fields.get('STATUS',('',{}))[0].upper()
        title_missing=not title
        if not uid or len(uid)>1000 or (title_missing and status!='CANCELLED'):continue
        target=registered_url(fields.get('URL',(page_url,{}))[0],source,page_url)
        if not target:continue
        obj={'@type':'Event','name':title or 'Actividad cancelada','url':target}
        if status=='CANCELLED':obj['eventStatus']='https://schema.org/EventCancelled'
        location=fields.get('LOCATION',('',{}))[0]
        if location:obj['location']={'name':location[:500]}
        raw_start=fields.get('DTSTART',('',{}))
        try:
            if any(key in fields for key in ('RRULE','RDATE','EXDATE')):raise ValueError('Recurring calendar requires expansion')
            start,all_day=_ics_date(*raw_start,source['timezone']);obj['startDate']=start
            if 'DTEND' in fields:
                end,end_all_day=_ics_date(*fields['DTEND'],source['timezone'])
                if all_day!=end_all_day:raise ValueError('Mixed calendar date types')
                if end_all_day:end=(datetime.fromisoformat(end).date()-timedelta(days=1)).isoformat()
                else:
                    if datetime.fromisoformat(end)<=datetime.fromisoformat(start):raise ValueError('Reversed calendar times')
                    end=(datetime.fromisoformat(end)-timedelta(microseconds=1)).isoformat()
                if events.local_date(end,ZoneInfo(source['timezone']))<events.local_date(start,ZoneInfo(source['timezone'])):
                    raise ValueError('Reversed calendar dates')
                obj['endDate']=end
        except (ValueError,KeyError,OverflowError):
            obj.pop('startDate',None);obj.pop('endDate',None)
        row=_structured_row([obj],target,page_url,source,now,'calendar')
        if row:
            recurrence=fields.get('RECURRENCE-ID',('',{}))[0]
            row['id']=sha256((source['id']+'\nics:'+uid+'\n'+recurrence).encode()).hexdigest()[:24]
            row['calendar_uid']=uid
            if title_missing:row['_title_missing']=True
            if 'URL' not in fields:row['_calendar_url_missing']=True
            if row['date_evidence']:row['date_evidence']['value']=('DTSTART:'+raw_start[0])[:1000]
            rows.append(row)
    return rows


def _tribe_rows(text, page_url, source, now):
    data=json.loads(text)
    if not isinstance(data,dict) or not isinstance(data.get('events'),list):return []
    rows=[]
    for obj in data['events'][:MAX_EVENTS_PER_PAGE]:
        if not isinstance(obj,dict):continue
        target=registered_url(obj.get('url'),source,page_url)
        if not target:continue
        item={'@type':'Event','name':obj.get('title'),'url':target}
        for original,dest in (('start_date','startDate'),('end_date','endDate')):
            raw=obj.get(original)
            if isinstance(raw,str):item[dest]=raw[:10] if obj.get('all_day') is True else raw.replace(' ','T',1)
        venue=obj.get('venue')
        if isinstance(venue,dict):item['location']={'name':venue.get('venue'),'address':{'addressLocality':venue.get('city')}}
        status=str(obj.get('event_status') or obj.get('status') or '').lower()
        if status in ('cancelled','canceled'):item['eventStatus']='https://schema.org/EventCancelled'
        elif status=='postponed':item['eventStatus']='https://schema.org/EventPostponed'
        elif status=='rescheduled':item['eventStatus']='https://schema.org/EventRescheduled'
        cost=obj.get('cost')
        if isinstance(cost,str) and cost.strip().casefold() in ('gratis','gratuito','free','0','$0'):
            item['isAccessibleForFree']=True
        row=_structured_row([item],target,page_url,source,now,'calendar')
        if row:
            if isinstance(cost,str) and cost.strip():row['price_text']=' '.join(events._html(cost).text).strip()[:200] or None
            rows.append(row)
    return rows


def parse_document(text, content_type, page_url, source, now):
    """Pure bounded parsing. Activity dates must be explicit structured facts."""
    if not isinstance(text,str) or len(text.encode())>MAX_PAGE_BYTES:raise ValueError('Calendar document too large')
    if not registered_url(page_url,source):raise ValueError('Unregistered calendar document')
    if 'BEGIN:VCALENDAR' in text[:2000]:return _ics_rows(text,page_url,source,now)
    if content_type in ('application/json','application/ld+json'):
        if content_type=='application/ld+json':return _jsonld_rows('<script type="application/ld+json">'+text+'</script>',page_url,source,now)
        return _tribe_rows(text,page_url,source,now)
    if content_type in ('text/html','application/xhtml+xml'):return _jsonld_rows(text,page_url,source,now)
    return []


def fetch_document(url, source):
    """Existing publisher policy, with calendar MIME types and a strict byte limit."""
    target=registered_url(url,source)
    if not target:raise ValueError('Unregistered HTTPS calendar URL')
    host=urlsplit(target).hostname
    if not collect.is_public_host(host):raise ValueError('Calendar host is not public')
    if not collect.page_image_allowed(target,host):raise ValueError('Calendar disallowed or unknown robots.txt')
    if not collect.is_public_host(host):raise ValueError('Calendar host is no longer public')
    response=requests.get(target,headers={**collect.HEADERS,
        'Accept':'text/html, application/xhtml+xml, text/calendar, application/json, application/ld+json'},
        stream=True,timeout=(2.5,4.5),allow_redirects=False)
    try:
        if response.status_code!=200:raise ValueError('Calendar HTTP '+str(response.status_code))
        kind=response.headers.get('Content-Type','').split(';')[0].strip().lower()
        if kind not in ('text/html','application/xhtml+xml','application/json','application/ld+json',
                        'text/calendar','application/ics','text/plain'):
            raise ValueError('Unsupported calendar content type')
        parts=[];total=0
        for part in response.iter_content(chunk_size=8192):
            total+=len(part)
            if total>MAX_PAGE_BYTES:raise ValueError('Calendar document too large')
            parts.append(part)
        return kind,b''.join(parts).decode(response.encoding or 'utf-8','replace')
    finally:response.close()


def load_sources(path, catalog=None):
    config=json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(config,dict) or config.get('version')!=1 or not isinstance(config.get('sources'),list):
        raise ValueError('Invalid direct agenda source configuration')
    if len(config['sources'])>100:raise ValueError('Too many direct agenda sources')
    feeds=collect.parse_opml(catalog) if catalog else []
    parents={row['url']:row['id'] for row in feeds if not row['is_radar']}
    selected=[];ids=set();urls=set()
    for raw in config['sources']:
        if not isinstance(raw,dict) or type(raw.get('enabled')) is not bool:raise ValueError('Invalid direct source')
        if not raw['enabled']:continue
        source=dict(raw)
        for key,limit in (('id',128),('name',500),('category',500),('url',4000)):
            value=source.get(key)
            if not isinstance(value,str) or not value.strip() or len(value)>limit:raise ValueError('Invalid direct source '+key)
        if source.get('official') is not True:raise ValueError('Direct agenda requires an official source')
        try:ZoneInfo(source.get('timezone',''))
        except (ValueError,KeyError,TypeError) as exc:raise ValueError('Explicit direct-source timezone required') from exc
        hosts=source.get('hosts')
        if not isinstance(hosts,list) or not hosts or len(hosts)>4:raise ValueError('Registered source hosts required')
        for host in hosts:
            if (not isinstance(host,str) or host!=host.lower() or not re.fullmatch(r'[a-z0-9.-]+',host)
                    or host in ('localhost','localhost.localdomain') or host.endswith(('.local','.internal'))
                    or not collect.page_image_host('https://'+host+'/')):raise ValueError('Invalid registered source host')
        target=registered_url(source['url'],source)
        if not target or source['id'] in ids or target in urls:raise ValueError('Duplicate or unregistered direct source')
        pages=source.get('max_pages',MAX_PAGES_PER_SOURCE)
        if type(pages) is not int or not 1<=pages<=MAX_PAGES_PER_SOURCE:raise ValueError('Invalid direct-source page budget')
        parent=source.get('preference_feed_url')
        if parent:
            if parent not in parents:raise ValueError('Unknown RSS preference parent')
            source['preference_source_id']=parents[parent]
        elif feeds:
            hostname=urlsplit(target).hostname.removeprefix('www.')
            matches=[row for row in feeds if not row['is_radar'] and urlsplit(row['url']).hostname.removeprefix('www.')==hostname]
            if matches:source['preference_source_id']=matches[0]['id']
        if source.get('preference_source_id') is not None and (not isinstance(source['preference_source_id'],str) or not 1<=len(source['preference_source_id'])<=128):
            raise ValueError('Invalid RSS preference parent ID')
        source['max_pages']=pages
        ids.add(source['id']);urls.add(target);selected.append(source)
    return selected


def collect_sources(sources, now, *, fetcher=None, max_requests=MAX_REQUESTS):
    """Collect bounded direct facts and source states; callers perform the one merge."""
    fetcher=fetcher or fetch_document
    incoming=[];states=[];requests_used=0
    for source in sources:
        state={'source_id':source['id'],'source_name':source['name'],'url':source['url'],
               'timezone':source['timezone'],'checked_at':events.iso(now),'status':'ok','error':None}
        queue=[source['url']];seen=set();pages=0
        try:
            if requests_used>=max_requests:raise ValueError('Direct calendar request budget exhausted')
            while queue and pages<min(source.get('max_pages',MAX_PAGES_PER_SOURCE),MAX_PAGES_PER_SOURCE) and requests_used<max_requests:
                url=queue.pop(0)
                if url in seen:continue
                seen.add(url);requests_used+=1;pages+=1
                kind,text=fetcher(url,source)
                incoming.extend(parse_document(text,kind,url,source,now))
                if kind in ('text/html','application/xhtml+xml'):
                    queue.extend(target for target in discover_links(text,url,source) if target not in seen)
        except (requests.RequestException,ValueError,TypeError,OSError,KeyError,RecursionError) as exc:
            state['status']='error';state['error']=type(exc).__name__+': '+str(exc)[:300]
        states.append(state)
    # One official detail can be advertised as both JSON-LD and ICS. Prefer
    # the calendar's stable UID without creating a second agenda activity.
    unique=[];positions={};priority={'scheduled':0,'postponed':1,'cancelled':2}
    for row in incoming:
        key=(row['source_id'],row['url'])
        position=positions.get(key)
        old=unique[position] if position is not None else None
        old_calendar=old is not None and bool(old.get('calendar_uid'))
        new_calendar=bool(row.get('calendar_uid'))
        if old is not None and old_calendar!=new_calendar:
            chosen=dict(row if new_calendar else old)
            chosen['status']=max((old['status'],row['status']),key=priority.get)
            reschedules=[item for item in (old,row) if item.get('status_explicit') is True and item.get('start_date')]
            if chosen['status']=='scheduled' and reschedules:
                if len({item['start_date'] for item in reschedules})>1:chosen['status']='postponed'
                else:
                    for field in ('start_date','end_date','date_evidence','status_explicit'):
                        chosen[field]=reschedules[0][field]
            if chosen['status']=='postponed':
                chosen.update(start_date=None,end_date=None,date_evidence=None,reason='postponed',status_explicit=False)
            for field in events.OPTIONAL_DETAILS:
                if field in ('is_free','price_text') and chosen.get('_price_observed'):continue
                if chosen.get(field) is None:chosen[field]=row.get(field) if old_calendar else old.get(field)
            if old.get('_price_observed') or row.get('_price_observed'):chosen['_price_observed']=True
            unique[position]=chosen
        else:
            positions[key]=len(unique);unique.append(row)
    return unique,states
