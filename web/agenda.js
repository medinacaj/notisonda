"use strict";
/* Activity dates are local calendar days. Publication time is attribution only. */
(() => {
  const section=$('agendaSection'), list=$('agendaList'), status=$('agendaStatus');
  if(!section||!list||!status)return;
  const pending=$('agendaPending'), pendingList=$('agendaPendingList'), retry=$('agendaRetry');
  let documentData=null, horizon=90, phase='loading', requestedGeneration=null, requestNumber=0;
  const zones=new Map();
  const renderedRows=new WeakMap();
  const text=(value,limit=1000)=>typeof value==='string'&&value.trim().length>0&&value.length<=limit;
  const object=value=>value!==null&&typeof value==='object'&&!Array.isArray(value);
  const day=value=>{
    if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(value)||value.slice(0,4)==='0000')return false;
    const date=new Date(value+'T00:00:00Z');
    return Number.isFinite(date.getTime())&&date.toISOString().slice(0,10)===value;
  };
  const stamp=value=>{
    if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.test(value))return false;
    return day(value.slice(0,10))&&Number.isFinite(Date.parse(value))&&+value.slice(11,13)<24&&+value.slice(14,16)<60&&+value.slice(17,19)<60;
  };
  const zone=value=>{
    if(!text(value,100))return false;
    try{
      if(!zones.has(value))zones.set(value,new Intl.DateTimeFormat('en-CA',{timeZone:value,year:'numeric',month:'2-digit',day:'2-digit'}));
      return true;
    }catch{return false;}
  };
  const url=value=>{
    if(!text(value,4000)||!safeURL(value))return false;
    const parsed=new URL(value);
    return !parsed.username&&!parsed.password;
  };
  function validate(data){
    const require=condition=>{if(!condition)throw new Error('Agenda inválida');};
    require(object(data)&&data.version===1&&data.horizon_days===90&&stamp(data.generated_at));
    require(['items','pending','sources'].every(key=>Array.isArray(data[key])));
    require(data.items.length+data.pending.length<=20000&&data.sources.length<=1000);
    require(new TextEncoder().encode(JSON.stringify(data)).length<=8000000);
    const ids=new Set();
    for(const key of ['items','pending'])for(const row of data[key]){
      require(object(row));
      require([['id',128],['title',500],['source_id',128],['source_name',500],['category',500]].every(([name,limit])=>text(row[name],limit)));
      require(!ids.has(row.id)&&url(row.url));ids.add(row.id);
      require(['scheduled','cancelled','postponed'].includes(row.status));
      require(stamp(row.first_seen_at)&&stamp(row.last_seen_at)&&Date.parse(row.first_seen_at)<=Date.parse(row.last_seen_at)&&Date.parse(row.last_seen_at)<=Date.parse(data.generated_at));
      require(row.announced_at===null||stamp(row.announced_at));
      require(row.location===null||text(row.location,500));
      if(key==='items'){
        require(zone(row.timezone)&&day(row.start_date));
        require(row.end_date===null||(day(row.end_date)&&row.end_date>=row.start_date));
        require(row.status!=='postponed');
        require(object(row.date_evidence)&&['rss','jsonld','text'].includes(row.date_evidence.kind)&&text(row.date_evidence.value,1000)&&url(row.date_evidence.url));
      }else{
        require(row.start_date===null&&row.end_date===null&&row.date_evidence===null);
        require(row.timezone===null||zone(row.timezone));
        require(['date_unverified','timezone_missing','postponed'].includes(row.reason));
      }
    }
    const sourceIds=new Set();
    for(const source of data.sources){
      require(object(source)&&text(source.source_id,128)&&!sourceIds.has(source.source_id));sourceIds.add(source.source_id);
      require(text(source.source_name,1000)&&url(source.url)&&zone(source.timezone));
      require(stamp(source.checked_at)&&Date.parse(source.checked_at)<=Date.parse(data.generated_at));
      require(['ok','error'].includes(source.status)&&(source.status==='ok'?source.error===null:text(source.error,1000)));
    }
    return data;
  }
  const localDay=(timezone,now)=>{
    const parts=zones.get(timezone).formatToParts(now), part=kind=>parts.find(p=>p.type===kind).value;
    return `${part('year')}-${part('month')}-${part('day')}`;
  };
  const addDays=(value,count)=>{
    const date=new Date(value+'T00:00:00Z');date.setUTCDate(date.getUTCDate()+count);
    return date.toISOString().slice(0,10);
  };
  const dateLabel=value=>new Intl.DateTimeFormat('es',{timeZone:'UTC',day:'numeric',month:'long',year:'numeric'}).format(new Date(value+'T00:00:00Z'));
  function eligible(row){
    if(state.hiddenSources.has(row.source_id))return false;
    if(window.RadarV12&&!window.RadarV12.dashboardMatch({categories:[row.category]}))return false;
    const haystack=stripAccents([row.title,row.source_name,row.location||''].join(' '));
    const query=stripAccents(state.search.trim());
    if(query&&!haystack.includes(query))return false;
    return !state.mutedKeywords.split(',').map(word=>stripAccents(word.trim())).filter(word=>word.length>1).slice(0,30).some(word=>haystack.includes(word));
  }
  function eventRow(row,unconfirmed=false){
    const item=mk('li','agenda-item');item.dataset.eventId=row.id;
    if(unconfirmed){
      item.append(mk('p','agenda-date',row.status==='cancelled'?'Cancelada':row.status==='postponed'||row.reason==='postponed'?'Aplazada · nueva fecha por confirmar':'Fecha por confirmar'));
    }else{
      const dates=mk('p','agenda-date');
      const start=mk('time','',dateLabel(row.start_date));start.dateTime=row.start_date;dates.append(start);
      if(row.end_date&&row.end_date!==row.start_date){
        const end=mk('time','',dateLabel(row.end_date));end.dateTime=row.end_date;
        dates.append(document.createTextNode(' — '),end);
      }
      item.append(dates);
    }
    const heading=mk('h3','agenda-item-title'), anchor=mk('a','',row.title);
    anchor.href=safeURL(row.url);anchor.target='_blank';anchor.rel='noopener noreferrer external';anchor.referrerPolicy='no-referrer';
    heading.append(anchor);item.append(heading);
    item.append(mk('p','agenda-meta',`${row.source_name} · ${categoryLabel(row.category)}`));
    item.append(mk('p','agenda-place',(row.location||'Lugar por confirmar')+(row.timezone?' · Zona horaria: '+row.timezone:'')));
    if(row.announced_at){
      const announcement=mk('p','agenda-announced','Anunciado: '), time=mk('time','',new Intl.DateTimeFormat('es',{timeZone:row.timezone||'UTC',day:'numeric',month:'long',year:'numeric'}).format(new Date(row.announced_at)));
      time.dateTime=row.announced_at;announcement.append(time);item.append(announcement);
    }
    return item;
  }
  function reconcile(target,rows,unconfirmed=false){
    const previous=new Map([...target.children].map(node=>[node.dataset.eventId,node]));
    const active=target.contains(document.activeElement)?document.activeElement.closest('[data-event-id]')?.dataset.eventId:null;
    const next=rows.map(row=>{
      const signature=JSON.stringify(row), old=previous.get(row.id);
      if(old&&renderedRows.get(old)===signature)return old;
      const node=eventRow(row,unconfirmed);renderedRows.set(node,signature);return node;
    });
    if(next.length===target.children.length&&next.every((node,index)=>node===target.children[index]))return;
    target.replaceChildren(...next);
    if(active)next.find(node=>node.dataset.eventId===active)?.querySelector('a')?.focus({preventScroll:true});
  }
  function paint(){
    section.setAttribute('aria-busy',String(phase==='loading'));
    retry.hidden=phase!=='error';
    const sameGeneration=!state.generated||documentData?.generated_at===state.generated;
    if(phase!=='ready'&&!(phase==='loading'&&documentData&&sameGeneration)){
      list.replaceChildren();pendingList.replaceChildren();pending.hidden=true;
      status.textContent=phase==='loading'?'Cargando actividades…':'No se pudo cargar la agenda. Vuelve a intentarlo.';
      return;
    }
    const now=new Date(), todayByZone=new Map();
    const today=row=>{
      if(!todayByZone.has(row.timezone))todayByZone.set(row.timezone,localDay(row.timezone,now));
      return todayByZone.get(row.timezone);
    };
    const rows=documentData.items.filter(row=>eligible(row)&&row.status==='scheduled'&&(row.end_date||row.start_date)>=today(row)&&row.start_date<=addDays(today(row),horizon))
      .sort((a,b)=>a.start_date.localeCompare(b.start_date)||a.title.localeCompare(b.title,'es')||a.id.localeCompare(b.id));
    const announcements=[...documentData.pending.filter(row=>Date.parse(row.last_seen_at)>=now.getTime()-90*86400000),
      ...documentData.items.filter(row=>row.status==='cancelled'&&(row.end_date||row.start_date)>=today(row)&&row.start_date<=addDays(today(row),horizon))].filter(eligible);
    reconcile(list,rows);
    reconcile(pendingList,announcements,true);
    pending.hidden=!announcements.length;
    $('agendaPendingTitle').textContent=`Fechas por confirmar y cambios (${announcements.length})`;
    status.textContent=phase==='loading'?'Actualizando actividades…':rows.length?`${rows.length} ${rows.length===1?'actividad':'actividades'} · ${horizon===0?'Hoy':'Hasta '+horizon+' días'}`:'No hay actividades confirmadas para este período con tus preferencias.';
  }
  async function refresh(){
    const number=++requestNumber;
    requestedGeneration=state.generated||'';phase='loading';paint();
    try{
      const data=validate(await dataFetch('./data/events.json?check='+Date.now()));
      if(number!==requestNumber)return;
      if(state.generated&&data.generated_at!==state.generated)throw new Error('Generación de agenda diferente');
      requestedGeneration=state.generated||'';
      documentData=data;phase='ready';
    }catch{
      if(number!==requestNumber)return;
      documentData=null;phase='error';
    }
    paint();
  }
  function sync(){
    if(state.ready&&phase!=='loading'&&requestedGeneration!==(state.generated||''))void refresh();
    else paint();
  }
  for(const button of section.querySelectorAll('[data-agenda-days]'))button.addEventListener('click',()=>{
    horizon=Number(button.dataset.agendaDays);
    for(const control of section.querySelectorAll('[data-agenda-days]'))control.setAttribute('aria-pressed',String(control===button));
    paint();
  });
  retry.addEventListener('click',()=>{void refresh();});
  const renderBase=render;
  render=function(...args){const result=renderBase(...args);sync();return result;};
  document.addEventListener('visibilitychange',()=>{if(!document.hidden)sync();});
  window.addEventListener('focus',sync);
  window.setInterval(()=>{if(!document.hidden)sync();},30000);
  window.RadarAgenda=Object.freeze({refresh});
  // Agenda can load even if an unrelated news resource prevents boot().
  void refresh();
})();
