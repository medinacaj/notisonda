"use strict";
// Radar RSS: interfaz pública sin autenticación y sin HTML sin sanear de fuentes externas.
const $ = (id) => document.getElementById(id);
const format = new Intl.NumberFormat('es-CL');
function storeGet(key) { try { return localStorage.getItem(key); } catch { return null; } }
function initialTheme(){
  const saved=storeGet('radar-theme');
  const flag='radar-editorial-theme-v5';
  // Versiones anteriores guardaban "system" incluso sin interacción.
  // Migrar una vez a papel claro, sin alterar selecciones explícitas oscuras.
  if(saved==='system'&&storeGet(flag)!=='migrated'){
    try{localStorage.setItem(flag,'migrated');localStorage.setItem('radar-theme','light');}catch{}
    return 'light';
  }
  try{localStorage.setItem(flag,'migrated');}catch{}
  return ['system','light','dark'].includes(saved)?saved:'light';
}
const state = {
  sources: [], categories: [], items: [], health: [], generated: null,
  pageView: 'dashboard', category: 'all', feed: '', mode: 'all', layout: storeGet('radar-layout') === 'list' ? 'list' : 'cards',
  theme: initialTheme(),
  search: '', page: 1, ready: false,
  density: storeGet('radar-density') === 'compact' ? 'compact' : 'comfortable',
  columns: ['auto','2','3','4','5','6'].includes(storeGet('radar-columns')) ? storeGet('radar-columns') : 'auto',
  pageSize: [12,24,36,60].includes(Number(storeGet('radar-page-size'))) ? Number(storeGet('radar-page-size')) : 36,
  maxAge: [0,1,7,30,90].includes(Number(storeGet('radar-max-age'))) ? Number(storeGet('radar-max-age')) : 0,
  fontSize: storeGet('radar-font') === 'large' ? 'large' : 'normal',
  showHero: storeGet('radar-show-hero') === 'true',
  showImages: storeGet('radar-show-images') !== 'false',
  showSummaries: storeGet('radar-show-summaries') !== 'false',
  hideRead: storeGet('radar-hide-read') === 'true',
  newTab: storeGet('radar-new-tab') !== 'false',
  sort: ['newest','oldest','source'].includes(storeGet('radar-sort')) ? storeGet('radar-sort') : 'newest',
  startMode: ['all','unread','saved'].includes(storeGet('radar-start-mode')) ? storeGet('radar-start-mode') : 'all',
  mutedKeywords: (storeGet('radar-keywords') || '').slice(0,600),
  hiddenSources: safeStoredSet('radar-hidden-sources'),
  saved: safeStoredSet('radar-saved'), read: safeStoredSet('radar-read')
};

const VECTOR_PATHS={
  home:'<path d="m3 10 9-7 9 7v10H5V10M9 21v-7h6v7"/>',
  newspaper:'<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 7h5v5H7zM15 8h3M15 12h3M7 16h11"/>',
  brain:'<path d="M12 5A4 4 0 0 0 5 4a5 5 0 0 0-1 8 5 5 0 0 0 6 8l2-2V5Zm0 0a4 4 0 0 1 7-1 5 5 0 0 1 1 8 5 5 0 0 1-6 8l-2-2"/>',
  cpu:'<rect x="5" y="5" width="14" height="14" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v4M15 1v4M9 19v4M15 19v4M1 9h4M1 15h4M19 9h4M19 15h4"/>',
  globe:'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c-7 6-7 12 0 18 7-6 7-12 0-18"/>',
  map:'<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
  flag:'<path d="M5 22V4m0 1c7-5 9 5 16 0v12c-7 5-9-5-16 0"/>',
  compass:'<circle cx="12" cy="12" r="9"/><path d="m16 8-3 5-5 3 3-5z"/>',
  rss:'<circle cx="5" cy="19" r="1.5" fill="currentColor" stroke="none"/><path d="M4 11a9 9 0 0 1 9 9M4 4a16 16 0 0 1 16 16"/>',
  grid:'<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
  list:'<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01" stroke-linecap="round"/>',
  clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l4 2"/>',
  settings:'<circle cx="12" cy="12" r="3"/><path d="m10 2-.5 2-2 1-2-.7L3 7l1 2-1 2v2l1 2-1 2 2.5 2.7 2-.7 2 1 .5 2h4l.5-2 2-1 2 .7L21 17l-1-2 1-2v-2l-1-2 1-2-2.5-2.7-2 .7-2-1-.5-2z"/>',
  sun:'<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5 19 19M5 19l1.5-1.5M17.5 6.5 19 5"/>',
  moon:'<path d="M20 15.5A9 9 0 0 1 8.5 4 9 9 0 1 0 20 15.5Z"/>',
  external:'<path d="M12 5H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-7M13 3h8v8M10 14 21 3"/>',
  'arrow-right':'<path d="M4 12h16m-7-7 7 7-7 7"/>',
  'arrow-up':'<path d="M12 20V4M5 11l7-7 7 7"/>',
  'arrow-down':'<path d="M12 4v16M5 13l7 7 7-7"/>',
  'chevron-down':'<path d="m6 9 6 6 6-6"/>',
  refresh:'<path d="M20 7v5h-5M4 17v-5h5M5.5 9A7.5 7.5 0 0 1 19 7l1 5M4 12l1 5a7.5 7.5 0 0 0 13.5-2"/>',
  check:'<path d="m5 12 5 5L20 7"/>',
  bookmark:'<path d="M6 4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18l-6-4-6 4z"/>',
  share:'<circle cx="18" cy="5" r="2"/><circle cx="6" cy="12" r="2"/><circle cx="18" cy="19" r="2"/><path d="m8 11 8-5M8 13l8 5"/>',
  undo:'<path d="M3 7v6h6M3 13a9 9 0 1 0 3-7"/>',
  info:'<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7h.01"/>',
  x:'<path d="M18 6 6 18M6 6l12 12"/>',
  search:'<circle cx="11" cy="11" r="7"/><path d="m16 16 5 5"/>'
};
const CATEGORY_ICONS=['brain','cpu','globe','map','flag','compass'];
function svgIcon(name){
 const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
 svg.setAttribute('viewBox','0 0 24 24');svg.setAttribute('width','20');svg.setAttribute('height','20');
 svg.setAttribute('stroke','currentColor');svg.setAttribute('fill','none');
 svg.setAttribute('stroke-width','1.8');svg.setAttribute('stroke-linecap','round');svg.setAttribute('stroke-linejoin','round');
 svg.setAttribute('aria-hidden','true');svg.classList.add('ui-icon');
 svg.innerHTML=VECTOR_PATHS[name]||VECTOR_PATHS.newspaper;
 return svg;
}
function hydrateIcons(){document.querySelectorAll('[data-icon]').forEach(node=>node.replaceChildren(svgIcon(node.dataset.icon)));}

const CATEGORY_LABELS = ['Inteligencia Artificial', 'Tecnología', 'Internacionales', 'Chile', 'Venezuela', 'Latinoamérica'];

function safeStoredSet(key) {
  try {
    const data = JSON.parse(storeGet(key) || '[]');
    return new Set(Array.isArray(data) ? data.filter(x => typeof x === 'string').slice(-4000) : []);
  } catch { return new Set(); }
}
function persist(key, values) {
  try { localStorage.setItem(key, JSON.stringify([...values].slice(-4000))); } catch { /* modo privado o almacenamiento bloqueado */ }
}
function safeURL(raw) {
  try { const u = new URL(raw); return ['https:', 'http:'].includes(u.protocol) ? u.href : null; }
  catch { return null; }
}
function mk(tag, className, value) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (value !== undefined && value !== null) node.textContent = value;
  return node;
}
function link(url, label, className = '') {
  const node = mk('a', className, label);
  node.href = safeURL(url) || '#';
  node.target = '_blank';
  node.rel = 'noopener noreferrer external';
  node.referrerPolicy = 'no-referrer';
  return node;
}
function ageDate(input) {
  if (!input) return 'Fecha no disponible';
  const dt = new Date(input);
  if (Number.isNaN(dt.getTime())) return 'Fecha no disponible';
  const days = Math.max(0, (Date.now() - dt.getTime()) / 86400000);
  if (days < 1) return 'Hoy';
  if (days < 2) return 'Ayer';
  if (days < 7) return `Hace ${Math.floor(days)} días`;
  return new Intl.DateTimeFormat('es-CL', { day: '2-digit', month: 'short', year: 'numeric' }).format(dt);
}
function shortDate(input) {
  if (!input) return '—';
  const date = new Date(input);
  if (Number.isNaN(date.getTime())) return '—';
  return new Intl.DateTimeFormat('es-CL', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }).format(date);
}
function stripAccents(s) { return String(s ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase(); }
function categoryLabel(cat) {
  const idx = state.categories.indexOf(cat);
  return idx >= 0 ? (CATEGORY_LABELS[idx] || cat.replace(/^\d+\s*-\s*/, '')) : String(cat || 'Noticias');
}
const browserTheme = window.matchMedia?.('(prefers-color-scheme: light)');
function setTheme(theme) {
  state.theme = ['light','dark','system'].includes(theme) ? theme : 'system';
  const light=state.theme==='light' || (state.theme==='system' && Boolean(browserTheme?.matches));
  document.body.classList.toggle('light',light);
  $('themeGlyph').replaceChildren(svgIcon(light?'moon':'sun'));
  try{localStorage.setItem('radar-theme',state.theme);}catch{}
}
function setColumns(value){
  state.columns=['auto','2','3','4','5','6'].includes(value)?value:'auto';
  savePref('columns',state.columns);
  applyDisplaySettings();
  $('settingColumns').value=state.columns;
}
function syncColumnsControl(){
  $('columnsCurrent').textContent=state.columns==='auto'?'Auto':state.columns;
  $('columnsSelect').value=state.columns;
  $('cardsColumnsControl').title=state.columns==='auto'?'Tarjetas · columnas automáticas':'Tarjetas · '+state.columns+' columnas';
}
function applyDisplaySettings() {
  document.body.classList.toggle('compact',state.density==='compact');
  document.body.classList.toggle('font-large',state.fontSize==='large');
  document.body.classList.toggle('show-hero',state.showHero);
  document.body.classList.toggle('hide-images',!state.showImages);
  document.body.classList.toggle('hide-summaries',!state.showSummaries);
  document.body.dataset.columns=state.columns;
  document.body.classList.toggle('layout-list',state.layout==='list');
  syncColumnsControl();
}
function downloadText(name,body,mime) {
  const obj=URL.createObjectURL(new Blob([body],{type:mime}));
  const a=document.createElement('a');a.href=obj;a.download=name;document.body.append(a);a.click();a.remove();
  setTimeout(()=>URL.revokeObjectURL(obj),2000);
}
function escapeXML(value){return String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));}
function savePref(key,value) {try{localStorage.setItem('radar-'+key,String(value));}catch{}}
function selectedTab(name) {
  document.querySelectorAll('[data-settings-tab]').forEach(x=>{
    const active=x.dataset.settingsTab===name;x.classList.toggle('active',active);x.setAttribute('aria-selected',String(active));
  });
  document.querySelectorAll('[data-settings-pane]').forEach(x=>{const active=x.dataset.settingsPane===name;x.classList.toggle('active',active);x.hidden=!active;});
  if(name==='health')renderFeedHealth();
  if(name==='data')updateDataCounts();
}
function updateDataCounts(){
  $('dataSavedCount').textContent=state.saved.size;
  $('dataReadCount').textContent=state.read.size;
  $('dataMutedCount').textContent=state.hiddenSources.size;
}
function renderFeedHealth(){
  const total=state.health.length,ok=state.health.filter(x=>x.state==='ok').length,
    empty=state.health.filter(x=>x.state==='empty').length,
    broken=state.health.filter(x=>x.state==='error').length,
    stale=state.health.filter(x=>x.state==='stale').length;
  $('healthSummary').textContent=`${total} fuentes comprobadas · ${ok} correctas · ${empty} sin artículos · ${broken} con error · ${stale} antiguas`;
  const list=$('healthFeedList');list.replaceChildren();
  const issues=state.health.filter(x=>x.state!=='ok');
  if(!issues.length){list.append(mk('p','setting-hint',total?'Sin incidencias detectadas en la última actualización.':'Aún no hay un diagnóstico disponible.'));return;}
  for(const source of issues){
    const row=mk('div','health-row');
    const heading=mk('strong','',source.name||'Fuente');
    const meta=mk('small','',source.state==='error'?'Error de lectura':source.state==='stale'?'Sin publicar desde hace más de un año':'Feed sin artículos');
    const detail=mk('span','',source.error|| (source.last_published_at ? 'Último artículo: '+shortDate(source.last_published_at):'Sin fecha de publicación detectada'));
    row.append(heading,meta,detail);list.append(row);
  }
}
function renderCategoryToggles(){
  const area=$('settingsCategories');area.replaceChildren();
  for(const category of state.categories){
    const sources=state.sources.filter(x=>x.category===category);
    const visible=sources.filter(x=>!state.hiddenSources.has(x.id)).length;
    const btn=mk('button','settings-category-toggle',`${categoryLabel(category)} · ${visible}/${sources.length}`);
    btn.type='button';btn.setAttribute('aria-label',`Alternar categoría ${categoryLabel(category)}`);
    btn.addEventListener('click',()=>{
      if(visible===sources.length) sources.forEach(x=>state.hiddenSources.add(x.id));
      else sources.forEach(x=>state.hiddenSources.delete(x.id));
      persist('radar-hidden-sources',state.hiddenSources);
      state.page=1;refreshFeedUI();renderSettingsSources();
    });area.append(btn);
  }
}
function refreshFeedUI() {
  if (state.feed && state.hiddenSources.has(state.feed)) state.feed='';
  fillSelect(); buildNav(); render();
}
function syncSettings() {
  $('settingTheme').value=state.theme;
  $('settingLayout').value=state.layout;
  $('settingColumns').value=state.columns;
  $('settingDensity').value=state.density;
  $('settingPageSize').value=String(state.pageSize);
  $('settingAge').value=String(state.maxAge);
  $('settingFont').value=state.fontSize;
  $('settingHero').checked=state.showHero;
  $('settingImages').checked=state.showImages;
  $('settingSummaries').checked=state.showSummaries;
  $('settingSort').value=state.sort;
  $('settingStartMode').value=state.startMode;
  $('settingHideRead').checked=state.hideRead;
  $('settingNewTab').checked=state.newTab;
  $('settingKeywords').value=state.mutedKeywords;
  renderSettingsSources();
  updateDataCounts();
  selectedTab('appearance');
}
function renderSettingsSources() {
  const search=stripAccents($('settingsSourceSearch').value.trim());
  const list=$('settingsSources'); list.replaceChildren();
  const ordered=state.sources.slice().sort((a,b)=>a.category.localeCompare(b.category,'es') || a.name.localeCompare(b.name,'es'));
  let displayed=0;
  for (const source of ordered) {
    if (search && !stripAccents(source.name + ' ' + categoryLabel(source.category)).includes(search)) continue;
    displayed++;
    const label=mk('label','settings-source-row');
    const checkbox=document.createElement('input'); checkbox.type='checkbox'; checkbox.checked=!state.hiddenSources.has(source.id);
    checkbox.setAttribute('aria-label','Mostrar '+source.name);
    const line=mk('span','settings-source-details'); line.append(mk('span','settings-source-name',source.name),mk('small','',categoryLabel(source.category)));
    label.append(checkbox,line); list.append(label);
    checkbox.addEventListener('change',()=>{
      if (checkbox.checked) state.hiddenSources.delete(source.id); else state.hiddenSources.add(source.id);
      persist('radar-hidden-sources',state.hiddenSources);
      state.page=1; refreshFeedUI();
      updateSettingsSourceCount(displayed);
    });
  }
  updateSettingsSourceCount(displayed);
  renderCategoryToggles();
}
function updateSettingsSourceCount(visibleInSearch) {
  const visible=state.sources.filter(x=>!state.hiddenSources.has(x.id)).length;
  $('settingsSourceCount').textContent=`${visible} de ${state.sources.length} fuentes activas en este navegador · ${visibleInSearch} en esta búsqueda`;
  $('sidebarSources').textContent=`${visible} de ${state.sources.length} fuentes · ${state.categories.length} categorías`;
}
function initSettingsHandlers(){
  const dialog=$('settingsDialog');
  $('settingsButton').addEventListener('click',()=>{syncSettings();dialog.showModal();});
  $('closeSettings').addEventListener('click',()=>dialog.close());
  $('settingsDone').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});
  document.querySelectorAll('[data-settings-tab]').forEach(el=>el.addEventListener('click',()=>selectedTab(el.dataset.settingsTab)));
  $('settingTheme').addEventListener('change',e=>setTheme(e.target.value));
  browserTheme?.addEventListener?.('change',()=>{if(state.theme==='system')setTheme('system');});
  $('settingLayout').addEventListener('change',e=>{state.layout=e.target.value;savePref('layout',state.layout);state.page=1;applyDisplaySettings();render();});
  $('settingColumns').addEventListener('change',e=>setColumns(e.target.value));
  $('settingDensity').addEventListener('change',e=>{state.density=e.target.value;savePref('density',state.density);applyDisplaySettings();});
  $('settingFont').addEventListener('change',e=>{state.fontSize=e.target.value;savePref('font',state.fontSize);applyDisplaySettings();});
  $('settingPageSize').addEventListener('change',e=>{state.pageSize=Number(e.target.value);savePref('page-size',state.pageSize);state.page=1;render();});
  $('settingAge').addEventListener('change',e=>{state.maxAge=Number(e.target.value);savePref('max-age',state.maxAge);state.page=1;render();});
  for(const [id,key,field] of [['settingHero','show-hero','showHero'],['settingImages','show-images','showImages'],['settingSummaries','show-summaries','showSummaries']]){
    $(id).addEventListener('change',e=>{state[field]=e.target.checked;savePref(key,state[field]);applyDisplaySettings();});
  }
  $('settingHideRead').addEventListener('change',e=>{state.hideRead=e.target.checked;savePref('hide-read',state.hideRead);state.page=1;render();});
  $('settingNewTab').addEventListener('change',e=>{state.newTab=e.target.checked;savePref('new-tab',state.newTab);render();});
  $('settingSort').addEventListener('change',e=>{state.sort=e.target.value;savePref('sort',state.sort);state.page=1;render();});
  $('settingStartMode').addEventListener('change',e=>{state.startMode=e.target.value;savePref('start-mode',state.startMode);state.mode=state.startMode;state.page=1;render();});
  $('settingKeywords').addEventListener('input',e=>{state.mutedKeywords=e.target.value.slice(0,600);savePref('keywords',state.mutedKeywords);state.page=1;render();});
  $('settingsSourceSearch').addEventListener('input',renderSettingsSources);
  $('showAllSources').addEventListener('click',()=>{state.hiddenSources.clear();persist('radar-hidden-sources',state.hiddenSources);state.page=1;refreshFeedUI();renderSettingsSources();});
  $('exportOPML').addEventListener('click',()=>{
    let lines=['<?xml version="1.0" encoding="UTF-8"?>','<opml version="2.0"><head><title>Mis fuentes Radar RSS</title></head><body>'];
    for(const category of state.categories){
      lines.push(`<outline text="${escapeXML(category)}">`);
      for(const f of state.sources.filter(x=>x.category===category&&!state.hiddenSources.has(x.id))){
        lines.push(`<outline type="rss" text="${escapeXML(f.name)}" title="${escapeXML(f.name)}" xmlUrl="${escapeXML(f.url)}" htmlUrl="${escapeXML(f.website||'')}"/>`);
      }lines.push('</outline>');
    }lines.push('</body></opml>');downloadText('radar-rss-mis-fuentes.opml',lines.join('\n'),'application/xml;charset=utf-8');
  });
  $('exportData').addEventListener('click',()=>{
    const data={format:'radar-rss-settings-v2',exported_at:new Date().toISOString(),preferences:{theme:state.theme,layout:state.layout,columns:state.columns,density:state.density,pageSize:state.pageSize,maxAge:state.maxAge,fontSize:state.fontSize,showHero:state.showHero,showImages:state.showImages,showSummaries:state.showSummaries,hideRead:state.hideRead,newTab:state.newTab,sort:state.sort,startMode:state.startMode,mutedKeywords:state.mutedKeywords},hiddenSources:[...state.hiddenSources],saved:[...state.saved],read:[...state.read]};
    downloadText('radar-rss-preferencias.json',JSON.stringify(data,null,2),'application/json;charset=utf-8');
    $('dataNotice').textContent='Archivo de respaldo generado.';
  });
  $('importData').addEventListener('change',async e=>{
    const file=e.target.files?.[0];e.target.value='';if(!file)return;
    if(file.size>1_000_000){$('dataNotice').textContent='El archivo supera el límite de 1 MB.';return;}
    try{
      const data=JSON.parse(await file.text());if(data.format!=='radar-rss-settings-v2'||typeof data.preferences!=='object')throw Error('Formato incompatible');
      const p=data.preferences,select=(key,allowed,def)=>allowed.includes(p[key])?p[key]:def;
      state.theme=select('theme',['system','light','dark'],'system');state.layout=select('layout',['cards','list'],'cards');state.columns=select('columns',['auto','2','3','4','5','6'],'auto');state.density=select('density',['comfortable','compact'],'comfortable');
      state.pageSize=select('pageSize',[12,24,36,60],36);state.maxAge=select('maxAge',[0,1,7,30,90],0);state.fontSize=select('fontSize',['normal','large'],'normal');
      for(const field of ['showHero','showImages','showSummaries','hideRead','newTab'])if(typeof p[field]==='boolean')state[field]=p[field];
      state.sort=select('sort',['newest','oldest','source'],'newest');state.startMode=select('startMode',['all','unread','saved'],'all');state.mutedKeywords=typeof p.mutedKeywords==='string'?p.mutedKeywords.slice(0,600):'';
      const valid=new Set(state.sources.map(x=>x.id));
      for(const [k,key,onlyValid] of [['hiddenSources','radar-hidden-sources',true],['saved','radar-saved',false],['read','radar-read',false]]){
        state[k]=new Set((Array.isArray(data[k])?data[k]:[]).filter(x=>typeof x==='string'&&x.length<150&&(!onlyValid||valid.has(x))).slice(-4000));persist(key,state[k]);
      }
      for(const [key,value] of [['layout',state.layout],['columns',state.columns],['theme',state.theme],['density',state.density],['font',state.fontSize],['page-size',state.pageSize],['max-age',state.maxAge],['show-hero',state.showHero],['show-images',state.showImages],['show-summaries',state.showSummaries],['hide-read',state.hideRead],['new-tab',state.newTab],['sort',state.sort],['start-mode',state.startMode],['keywords',state.mutedKeywords]])savePref(key,value);
      state.mode=state.startMode;state.page=1;setTheme(state.theme);applyDisplaySettings();refreshFeedUI();syncSettings();selectedTab('data');$('dataNotice').textContent='Preferencias y datos importados correctamente.';
    }catch{$('dataNotice').textContent='No se pudo importar. Utiliza un respaldo JSON generado por Radar RSS.';}
  });
  $('clearRead').addEventListener('click',()=>{if(confirm('¿Borrar el historial de lectura de este navegador?')){state.read.clear();persist('radar-read',state.read);state.page=1;render();updateDataCounts();$('dataNotice').textContent='Historial borrado.';}});
  $('clearSaved').addEventListener('click',()=>{if(confirm('¿Vaciar los artículos guardados en este navegador?')){state.saved.clear();persist('radar-saved',state.saved);state.page=1;render();updateDataCounts();$('dataNotice').textContent='Guardadas vaciadas.';}});
  $('resetSettings').addEventListener('click',()=>{
    if(!confirm('¿Restablecer las preferencias? Tus artículos leídos y guardados no se borrarán.'))return;
    for(const key of ['layout','columns','theme','density','font','page-size','max-age','show-hero','show-images','show-summaries','hide-read','new-tab','sort','start-mode','keywords','hidden-sources']){try{localStorage.removeItem('radar-'+key);}catch{}}
    state.theme='system';state.layout='cards';state.columns='auto';state.density='comfortable';state.fontSize='normal';state.pageSize=36;state.maxAge=0;
    state.showHero=false;state.showImages=true;state.showSummaries=true;state.hideRead=false;state.newTab=true;state.sort='newest';state.startMode='all';state.mode='all';state.mutedKeywords='';state.hiddenSources.clear();state.page=1;
    setTheme('system');applyDisplaySettings();$('settingsSourceSearch').value='';refreshFeedUI();syncSettings();selectedTab('data');$('dataNotice').textContent='Preferencias restablecidas.';
  });
}
function buildNav() {
  const nav = $('categoryNav'); nav.replaceChildren();
  const choices = [{id:'home', label:'Inicio'}, {id:'all', label:'Todas las noticias'}, ...state.categories.map(x => ({id:x, label:categoryLabel(x)}))];
  choices.forEach((cat, i) => {
    const active=cat.id==='home' ? state.pageView==='dashboard' : state.pageView==='feed' && state.category===cat.id;
    const button=mk('button', 'nav-link'+(active?' active':''));
    button.type='button'; button.setAttribute('aria-current',active?'page':'false');
    const symbol=mk('span','nav-glyph');symbol.append(svgIcon(i===0?'home':i===1?'newspaper':CATEGORY_ICONS[i-2]));
    const left=mk('span','nav-left');left.append(symbol,mk('span','nav-label',cat.label));
    const count=cat.id==='home' ? '' : (cat.id==='all' ? state.sources.filter(x=>!state.hiddenSources.has(x.id)).length : state.sources.filter(x=>x.category===cat.id&&!state.hiddenSources.has(x.id)).length);
    button.append(left,mk('span','nav-count',String(count)));
    button.addEventListener('click',()=>goTo(cat.id));
    nav.append(button);
  });
  renderTopicRail();
}
function renderTopicRail(){
 const rail=$('topicRail');rail.replaceChildren();
 const entries=[{id:'all',label:'Todos los temas',icon:'newspaper'},...state.categories.map((id,i)=>({id,label:categoryLabel(id),icon:CATEGORY_ICONS[i]||'grid'}))];
 entries.forEach(entry=>{
  const active=state.pageView==='feed'&&state.category===entry.id;
  const button=mk('button','topic-chip'+(active?' active':''));button.type='button';
  button.setAttribute('aria-pressed',String(active));button.append(svgIcon(entry.icon),mk('span','',entry.label));
  button.addEventListener('click',()=>goTo(entry.id));rail.append(button);
 });
}
function goTo(target){
  const hash=target==='home'?'#inicio':target==='all'?'#noticias':'#categoria/'+encodeURIComponent(target);
  if(window.location.hash===hash)navigateFromHash();
  else window.location.hash=hash;
}
function navigateFromHash(){
  const hash=decodeURIComponent(window.location.hash.slice(1));
  state.pageView=(!hash||hash==='inicio')?'dashboard':'feed';
  state.category=hash.startsWith('categoria/')&&state.categories.includes(hash.slice(10))?hash.slice(10):'all';
  state.feed='';
  state.page=1;progressiveLoads=0;
  updateHeader();buildNav();fillSelect();
  $('dashboardView').hidden=state.pageView!=='dashboard';
  $('feedView').hidden=state.pageView!=='feed';
  document.body.classList.toggle('on-dashboard',state.pageView==='dashboard');
  render();
}
function fillSelect() {
  const select = $('sourceSelect'); const old = state.feed; select.replaceChildren();
  const defaultOpt = document.createElement('option'); defaultOpt.value=''; defaultOpt.textContent='Todas las fuentes'; select.append(defaultOpt);
  state.sources.filter(x => !state.hiddenSources.has(x.id) && (state.category === 'all' || x.category === state.category))
    .sort((a,b) => a.name.localeCompare(b.name,'es'))
    .forEach(x => { const option=document.createElement('option'); option.value=x.id; option.textContent=x.name; select.append(option); });
  select.value = old && [...select.options].some(x => x.value === old) ? old : '';
  state.feed = select.value;
}
function updateHeader() {
  const name = state.category === 'all' ? 'Todas las noticias' : categoryLabel(state.category);
  $('feedHeading').textContent = name;
  $('topbarSection').textContent = state.pageView === 'dashboard' ? 'Inicio' : name;
  $('sectionEyebrow').textContent = state.category === 'all' ? 'SELECCIÓN EDITORIAL' : 'EXPLORAR CATEGORÍA';
  $('feedDescription').textContent = state.category === 'all' ? 'Titulares y novedades de todas las fuentes.' : `Publicaciones seleccionadas de ${name.toLowerCase()}.`;
}
// Avisos discretos y descartables. La preferencia solo es local a este navegador.
function openFeedHealth() {
  const modal=$('feedHealthDialog');
  const list=$('feedHealthIssues');
  const issues=state.health.filter(x=>x.state!=='ok');
  const ok=state.health.filter(x=>x.state==='ok').length;
  const errors=issues.filter(x=>x.state==='error').length;
  const empty=issues.filter(x=>x.state==='empty').length;
  const stale=issues.filter(x=>x.state==='stale').length;
  $('feedHealthOverview').textContent=state.health.length
    ? `${state.health.length} fuentes revisadas · ${ok} correctas · ${errors} con error · ${empty} sin artículos · ${stale} desactualizadas`
    : 'Todavía no hay datos del último diagnóstico de RSS.';
  list.replaceChildren();
  if(!issues.length){
    list.append(mk('p','feed-health-empty',state.health.length?'No hay incidencias pendientes.':'El diagnóstico estará disponible después de recopilar los feeds.'));
  }else{
    for(const source of issues){
      const row=mk('article','feed-health-item');
      const head=mk('div','feed-health-item-head');
      const label=source.state==='error'?'Error de lectura':source.state==='stale'?'Última publicación antigua':'Sin artículos recientes';
      head.append(mk('strong','',source.name||'Fuente RSS'),mk('span','feed-health-status',label));
      const detail=source.error || (source.last_published_at
        ? 'Último artículo publicado: '+shortDate(source.last_published_at)
        : 'No se dispone de información adicional sobre esta incidencia.');
      row.append(head,mk('p','feed-health-error',detail));
      const original=safeURL(source.url||source.xmlUrl||source.xml_url||'');
      if(original){
        const a=link(original,'Consultar fuente RSS','feed-health-source-link');a.append(svgIcon('external'));
        row.append(a);
      }
      list.append(row);
    }
  }
  if(!modal.open)modal.showModal();
}
function showFeedNotice(message, signature, details) {
  const banner=$('statusBanner');
  $('statusMessage').textContent=message;
  $('statusDetails').hidden=!details;
  banner.dataset.signature=signature;
  banner.hidden=Boolean(signature && storeGet('radar-dismissed-health-notice-v1')===signature);
}
function statusSummary() {
  const banner=$('statusBanner');
  const indicator=$('feedHealthIndicator');
  banner.hidden=true;
  indicator.hidden=true;
  if (!state.ready) {
    showFeedNotice('No se pudieron cargar las noticias. Comprueba GitHub Pages y vuelve a intentarlo.', 'load-error', false);
    return;
  }
  if (!state.generated && !state.items.length) {
    showFeedNotice('Sin noticias todavía: falta completar la primera recopilación.', 'awaiting-first-run', false);
    return;
  }
  const issues=state.health.filter(x=>x.state==='error'||x.state==='stale');
  if (!issues.length) return;
  const errors=issues.filter(x=>x.state==='error').length;
  const stale=issues.length-errors;
  const labels=[];
  if(errors)labels.push(`${errors} ${errors===1?'fuente con error de lectura':'fuentes con error de lectura'}`);
  if(stale)labels.push(`${stale} ${stale===1?'fuente desactualizada':'fuentes desactualizadas'}`);
  // Sin marcas temporales: un refresco normal no vuelve a mostrar el aviso ya cerrado.
  // Si cambia la lista de feeds afectados, aparece de nuevo.
  const signature=JSON.stringify(issues.map(x=>[String(x.id||x.url||x.name||''),x.state]).sort((a,b)=>a[0].localeCompare(b[0])||a[1].localeCompare(b[1])));
  $('feedHealthCount').textContent=String(issues.length);
  indicator.setAttribute('aria-label',`${issues.length} fuentes RSS requieren revisión. Abrir diagnóstico`);
  indicator.title=labels.join(' · ')+'. Abrir diagnóstico RSS.';
  indicator.hidden=false;
  showFeedNotice(labels.join(' · ')+'.',signature,true);
}
function applyFilters() {
  const query=stripAccents(state.search.trim());
  const blocked=state.mutedKeywords.split(',').map(w=>stripAccents(w.trim())).filter(w=>w.length>1).slice(0,30);
  const filtered=state.items.filter(item=>{
    if(state.category!=='all'&&!(item.categories||[]).includes(state.category))return false;
    if(!(item.source_ids||[]).some(id=>!state.hiddenSources.has(id)))return false;
    if(state.feed&&!(item.source_ids||[]).includes(state.feed))return false;
    if(state.maxAge){const t=new Date(item.published_at).getTime();if(!Number.isFinite(t)||(Date.now()-t)>state.maxAge*86400000)return false;}
    if(state.mode==='saved'&&!state.saved.has(item.id))return false;
    if(state.mode==='unread'&&state.read.has(item.id))return false;
    if(state.hideRead&&state.mode!=='saved'&&state.read.has(item.id))return false;
    const haystack=stripAccents([item.title,item.summary,item.publisher,item.source].join(' '));
    if(query&&!haystack.includes(query))return false;
    if(blocked.some(x=>haystack.includes(x)))return false;
    return true;
  });
  if(state.sort==='oldest')filtered.sort((a,b)=>new Date(a.published_at||a.first_seen_at)-new Date(b.published_at||b.first_seen_at));
  else if(state.sort==='source')filtered.sort((a,b)=>String(a.publisher||a.source||'').localeCompare(String(b.publisher||b.source||''),'es'));
  return filtered;
}

// La portada utiliza las noticias realmente recopiladas. No inventa puntuaciones
// de popularidad ni presenta la recencia como una clasificación editorial.
function dashboardEligible(){
  const words=state.mutedKeywords.split(',').map(w=>stripAccents(w.trim())).filter(w=>w.length>1).slice(0,30);
  return state.items.filter(item=>{
    if(!(item.source_ids||[]).some(id=>!state.hiddenSources.has(id)))return false;
    if(state.maxAge){
      const date=new Date(item.published_at).getTime();
      if(!Number.isFinite(date)||(Date.now()-date)>state.maxAge*86400000)return false;
    }
    const text=stripAccents([item.title,item.summary,item.publisher,item.source].join(' '));
    return !words.some(word=>text.includes(word));
  }).sort((a,b)=>new Date(b.published_at||b.first_seen_at||0)-new Date(a.published_at||a.first_seen_at||0));
}
function renderDashboard(){
  const feature=$('dashboardFeature');
  const recent=$('dashboardRecent');
  const categories=$('dashboardCategories');
  if(!feature||!recent||!categories)return;
  const items=dashboardEligible();
  const top=[],seen=new Set();
  for(const item of items){
    const primary=(item.categories||[])[0]||'';
    if(!seen.has(primary)){top.push(item);seen.add(primary);}
    if(top.length>=3)break;
  }
  for(const item of items){if(top.length>=3)break;if(!top.some(x=>x.id===item.id))top.push(item);}
  if(top.length)feature.replaceChildren(...top.map(card));
  else feature.replaceChildren(mk('p','dashboard-empty','No hay artículos disponibles con las preferencias actuales.'));
  const savedPanel=$('dashboardSavedPanel'), savedList=$('dashboardSavedList');
  const savedNews=items.filter(x=>state.saved.has(x.id)).slice(0,4);
  savedPanel.hidden=!savedNews.length;
  savedList.replaceChildren(...savedNews.map(story=>{
   const row=mk('div','dashboard-saved-item'),content=mk('div','dashboard-saved-content');
   const image=mk('a','dashboard-saved-cover');image.href=safeURL(story.url)||'#';
   image.target='_blank';image.rel='noopener noreferrer external';
   image.addEventListener('click',event=>openArticleReader(story,event));
   if(safeURL(story.image)){const img=mk('img');img.src=story.image;img.alt='';img.loading='lazy';img.referrerPolicy='no-referrer';image.append(img);}
   else image.append(svgIcon('bookmark'));
   const title=link(story.url,story.title||'Sin título','dashboard-saved-title');title.target='_blank';title.addEventListener('click',event=>openArticleReader(story,event));
   content.append(title,mk('span','dashboard-saved-meta',story.publisher||story.source||'Fuente RSS'));row.append(image,content);return row;
  }));
  const categoryNodes=state.categories.map((cat,i)=>{
    const shown=state.sources.filter(s=>s.category===cat&&!state.hiddenSources.has(s.id));
    const count=items.filter(item=>(item.categories||[]).includes(cat)).length;
    const button=mk('button','dashboard-category');
    button.type='button'; button.disabled=shown.length===0;
    const label=mk('span','dashboard-category-label',categoryLabel(cat));
    const countText=mk('span','dashboard-category-meta',format.format(count)+' noticias · '+shown.length+' fuentes');
    const symbol=mk('span','dashboard-category-icon');symbol.append(svgIcon(CATEGORY_ICONS[i]||'grid'));
    const arrow=mk('span','dashboard-category-arrow');arrow.append(svgIcon('arrow-right'));
    button.append(symbol,label,countText,arrow);
    button.addEventListener('click',()=>goTo(cat));
    return button;
  });
  categories.replaceChildren(...categoryNodes);
  const topIds=new Set(top.map(x=>x.id));
  const last=items.filter(x=>!topIds.has(x.id)).slice(0,6);
  if(!last.length)recent.replaceChildren(mk('p','dashboard-empty','Todavía no hay más publicaciones.'));
  else recent.replaceChildren(...last.map(item=>{
    const row=mk('div','dashboard-recent-row');
    const title=link(item.url,item.title||'Sin título','dashboard-recent-title');
    title.target='_blank';
    title.addEventListener('click',event=>openArticleReader(item,event));
    const info=mk('span','dashboard-recent-meta',(item.publisher||item.source||'Fuente RSS')+' · '+ageDate(item.published_at));
    row.append(title,info);
    return row;
  }));
  const errors=state.health.filter(s=>s.state==='error').length;
  const empty=state.health.filter(s=>s.state==='empty').length;
  const stale=state.health.filter(s=>s.state==='stale').length;
  const ok=state.health.filter(s=>s.state==='ok').length;
  $('dashboardHealthText').textContent=state.health.length
    ? `${ok} fuentes operativas · ${errors} con error · ${empty} sin artículos · ${stale} desactualizadas. Diagnóstico de la última recopilación.`
    : 'Aún no hay datos de diagnóstico del recolector.';
}

function emptyState(filtered) {
  const isEmpty = !state.items.length;
  const el = mk('div','empty-state');
  const symbol=mk('div','empty-icon');symbol.append(svgIcon(isEmpty?'rss':'search'));
  el.append(symbol,
    mk('h3','',isEmpty ? 'Esperando las primeras noticias' : 'No hay noticias con estos filtros'),
    mk('p','',isEmpty ? 'El diseño y las 150 fuentes están preparados. La recopilación debe ejecutarse desde GitHub Actions después de publicar el proyecto.' : 'Prueba otra categoría o fuente, desmarca tus filtros o busca con otros términos.'));
  return el;
}
let actionToastTimer;
function actionToast(message){
  const toast=$('actionToast');
  toast.textContent=message;
  toast.hidden=false;
  window.clearTimeout(actionToastTimer);
  actionToastTimer=window.setTimeout(()=>{toast.hidden=true;},3200);
}
async function shareArticle(item) {
  const url=safeURL(item.url);
  if(!url){actionToast('Esta noticia no tiene un enlace válido.');return;}
  if(typeof navigator.share==='function'){
    try{
      await navigator.share({title:item.title||'Noticia',url});
      return;
    }catch(error){
      if(error?.name==='AbortError')return; // El usuario canceló el panel nativo.
    }
  }
  try{
    if(navigator.clipboard?.writeText) await navigator.clipboard.writeText(url);
    else {
      const input=document.createElement('textarea');
      input.value=url;input.readOnly=true;input.style.position='fixed';input.style.opacity='0';
      document.body.append(input);input.select();
      const copied=document.execCommand('copy');input.remove();
      if(!copied)throw new Error('No se pudo copiar automáticamente');
    }
    actionToast('Enlace de la noticia copiado. Ya puedes compartirlo.');
  }catch {
    // Fallback visible para navegadores que bloquean el portapapeles.
    window.prompt('Copia el enlace de la noticia:',url);
  }
}
function articleAction(iconName,label,extraClass=''){
 const button=mk('button','article-action'+(extraClass?' '+extraClass:''));button.type='button';
 button.title=label;button.setAttribute('aria-label',label);
 const symbol=mk('span','article-action-icon');symbol.setAttribute('aria-hidden','true');symbol.append(svgIcon(iconName));
 button.append(symbol,mk('span','article-action-label',label));return button;
}

let activeReaderItem=null;
function syncReaderActions(){
  if(!activeReaderItem)return;
  const saved=state.saved.has(activeReaderItem.id);
  $('readerSaveLabel').textContent=saved?'Quitar guardado':'Guardar';
  $('readerSave').classList.toggle('is-saved',saved);
  $('readerSave').setAttribute('aria-pressed',String(saved));
}
function openArticleReader(item,event){
  if(event){
    // Ctrl/Cmd/middle-click still opens the original source using native browser behavior.
    if(event.metaKey||event.ctrlKey||event.shiftKey||event.altKey||event.button!==0)return;
    event.preventDefault();
  }
  const dialog=$('articleReaderDialog');
  activeReaderItem=item;
  $('readerTitle').textContent=item.title||'Noticia sin título';
  $('readerCategory').textContent=categoryLabel((item.categories||[])[0]||'');
  const meta=$('readerMeta');meta.replaceChildren(
    mk('strong','',item.publisher||item.source||'Fuente RSS'),
    mk('span','',ageDate(item.published_at))
  );
  const cover=$('readerCover');cover.replaceChildren();cover.hidden=!state.showImages||!safeURL(item.image);
  if(!cover.hidden){
    const image=mk('img');image.src=item.image;image.alt='Imagen ilustrativa de la noticia';
    image.referrerPolicy='no-referrer';
    image.addEventListener('error',()=>{cover.hidden=true;},{once:true});
    cover.append(image);
  }
  const summary=$('readerSummary');summary.replaceChildren();
  const description=String(item.summary||'').trim();
  summary.append(mk('p','',description||'Esta fuente solo publica un titular o un extracto breve. Abre el medio original para leer la noticia completa.'));
  const url=safeURL(item.url);
  const source=$('readerOpenOriginal');source.href=url||'#';
  source.setAttribute('aria-disabled',String(!url));
  source.tabIndex=url?0:-1;
  source.target=state.newTab?'_blank':'_self';
  $('readerOpenOriginal').querySelector('.reader-open-hint').textContent=state.newTab?'en otra pestaña':'en esta pestaña';
  syncReaderActions();
  if(!dialog.open)dialog.showModal();
  markRead(item.id,true);
}
function initArticleReader(){
  const dialog=$('articleReaderDialog');
  $('readerClose').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',event=>{if(event.target===dialog)dialog.close();});
  dialog.addEventListener('close',()=>{activeReaderItem=null;});
  $('readerSave').addEventListener('click',()=>{
    if(!activeReaderItem)return;
    const id=activeReaderItem.id;
    if(state.saved.has(id))state.saved.delete(id);else state.saved.add(id);
    persist('radar-saved',state.saved);
    syncReaderActions();
    render();
    actionToast(state.saved.has(id)?'Noticia guardada':'Noticia retirada de guardadas');
  });
  $('readerShare').addEventListener('click',()=>{if(activeReaderItem)void shareArticle(activeReaderItem);});
  $('readerOpenOriginal').addEventListener('click',event=>{
    if(!activeReaderItem||!safeURL(activeReaderItem.url)){event.preventDefault();return;}
    markRead(activeReaderItem.id,true);
  });
}
function card(item) {
  const isRead=state.read.has(item.id);
  const el=mk('article','article-card'+(isRead?' read-article':''));el.dataset.articleId=item.id;
  const cover=mk('a','cover'); cover.href=safeURL(item.url)||'#';cover.target=state.newTab?'_blank':'_self';cover.rel='noopener noreferrer external';cover.referrerPolicy='no-referrer';
  cover.setAttribute('aria-label','Vista previa: '+(item.title||'Noticia'));
  cover.addEventListener('click',event=>openArticleReader(item,event));
  if(safeURL(item.image)){
    const img=document.createElement('img');img.src=item.image;img.alt='';img.loading='lazy';img.referrerPolicy='no-referrer';
    img.addEventListener('error',()=>{img.remove();cover.prepend(mk('div','cover-fallback','RADAR'));},{once:true});cover.append(img);
  }else{cover.append(mk('div','cover-fallback','RADAR'));}
  const category=(item.categories||[])[0]||'';
  const content=mk('div','article-content');
  const meta=mk('div','article-meta');
  meta.append(mk('span','publisher',item.publisher||item.source||'Fuente RSS'),mk('time','',ageDate(item.published_at)));
  const title=mk('h3','article-title');
  const titleLink=link(item.url,item.title||'Sin título');
  titleLink.target='_blank';titleLink.addEventListener('click',event=>openArticleReader(item,event));
  title.append(titleLink);
  const excerpt=mk('p','article-excerpt',item.summary||'Accede a la noticia original para leer el contenido completo.');
  const actions=mk('div','article-actions');
  actions.setAttribute('role','group');actions.setAttribute('aria-label','Acciones de esta noticia');
  const read=link(item.url,'','article-action article-open');
  read.target='_blank';read.title='Abrir vista previa';read.setAttribute('aria-label','Leer vista previa de la noticia');
  const symbol=mk('span','article-action-icon');symbol.setAttribute('aria-hidden','true');symbol.append(svgIcon('external'));
  read.append(symbol,mk('span','article-action-label','Leer'));
  read.addEventListener('click',event=>openArticleReader(item,event));
  const share=articleAction('share','Compartir','article-share');
  share.addEventListener('click',()=>{void shareArticle(item);});
  const saved=state.saved.has(item.id);
  const save=articleAction('bookmark',saved?'Quitar de guardadas':'Guardar','article-save'+(saved?' saved':''));
  save.setAttribute('aria-pressed',String(saved));
  save.addEventListener('click',()=>{
    if(state.saved.has(item.id))state.saved.delete(item.id);else state.saved.add(item.id);
    persist('radar-saved',state.saved);
    render();
    actionToast(state.saved.has(item.id)?'Noticia guardada.':'Noticia quitada de guardadas.');
  });
  const mark=articleAction(isRead?'undo':'check',isRead?'Marcar no leída':'Marcar leída','article-read-toggle');
  mark.setAttribute('aria-pressed',String(isRead));
  mark.addEventListener('click',()=>markRead(item.id,!state.read.has(item.id)));
  actions.append(read,share,save,mark);
  content.append(mk('span','article-category',categoryLabel(category)),meta,title,excerpt,actions);
  el.append(cover,content);return el;
}
function markRead(id,value){
  if(value)state.read.add(id);else state.read.delete(id);
  persist('radar-read',state.read);
  if(state.mode==='unread'||state.hideRead){render();return;}
  document.querySelectorAll('.article-card').forEach(el=>{
    if(el.dataset.articleId!==id)return;
    el.classList.toggle('read-article',value);
    const button=el.querySelector('.article-read-toggle');
    if(!button)return;
    const label=value?'Marcar no leída':'Marcar leída';
    button.title=label;button.setAttribute('aria-label',label);button.setAttribute('aria-pressed',String(value));
    button.querySelector('.article-action-icon').replaceChildren(svgIcon(value?'undo':'check'));
    button.querySelector('.article-action-label').textContent=label;
  });
  $('filterSummary').textContent=`${format.format(applyFilters().slice(0,state.page*state.pageSize).length)} visibles · ${format.format(state.read.size)} leídas`;
}
function render() {
  const filtered=applyFilters(), visible=filtered.slice(0,state.page*state.pageSize);
  $('visibleCount').textContent=`${format.format(filtered.length)} ARTÍCULOS`;
  $('filterSummary').textContent=`${format.format(visible.length)} visibles · ${format.format(state.read.size)} leídas`; 
  $('savedCount').textContent=state.saved.size ? String(state.saved.size) : '';
  const grid=$('articleGrid'); grid.className='article-grid'+(state.layout === 'list'?' list-view':'');
  if (!visible.length) grid.replaceChildren(emptyState(filtered));
  else grid.replaceChildren(...visible.map(card));
  $('loadMore').hidden=visible.length>=filtered.length;
  document.querySelectorAll('.mode-tab').forEach(button=>button.classList.toggle('active',button.dataset.mode === state.mode));
  document.querySelectorAll('.view-button').forEach(button=>button.classList.toggle('active',button.dataset.view === state.layout));
  document.body.classList.toggle('layout-list',state.layout==='list');
  syncColumnsControl();
  if(state.pageView==='dashboard')renderDashboard();
}
// Comprobación LOCAL de publicaciones nuevas: cada 5 min.
// La recopilación de RSS de origen sigue cada seis horas por GitHub Actions.
const CHECK_INTERVAL_MS=5*60*1000;
let nextCheckAt=Date.now()+CHECK_INTERVAL_MS;
let checkStartedAt=Date.now();
let checkTimer=null;
let feedRefreshBusy=false;
function updateScheduleProgress(){
  const now=Date.now();
  const elapsed=Math.max(0,now-checkStartedAt);
  const progress=Math.min(100,100*elapsed/CHECK_INTERVAL_MS);
  const remaining=Math.max(0,Math.ceil((nextCheckAt-now)/1000));
  const minute=Math.floor(remaining/60);
  const second=String(remaining%60).padStart(2,'0');
  const label=feedRefreshBusy?'Comprobando novedades…':`Próxima comprobación en ${minute}:${second}`;
  $('refreshCycleTime').textContent=label;
  $('refreshCycleTime').removeAttribute('datetime');
  $('refreshCycleFill').style.width=progress.toFixed(1)+'%';
  $('refreshCycleProgress').setAttribute('aria-valuenow',String(Math.round(progress)));
  $('refreshCycleProgress').setAttribute('aria-valuetext',label+'. Se comprueban datos ya publicados; el origen RSS se recopila aproximadamente cada seis horas.');
  $('refreshNow').disabled=feedRefreshBusy;
}
function scheduleNextCheck(){
  window.clearTimeout(checkTimer);
  checkStartedAt=Date.now();
  nextCheckAt=checkStartedAt+CHECK_INTERVAL_MS;
  checkTimer=window.setTimeout(()=>{void refreshPublishedData();},CHECK_INTERVAL_MS);
  updateScheduleProgress();
}
// Comprueba si GitHub Pages publicó datos nuevos, sin descargar directamente las fuentes.
async function refreshPublishedData(){
  if(feedRefreshBusy)return;
  if(!state.ready||document.hidden){scheduleNextCheck();return;}
  feedRefreshBusy=true;
  updateScheduleProgress();
  try{
    const latestStatus=await dataFetch('./data/status.json?check='+Date.now());
    const availableAt=Date.parse(latestStatus.checked_at||'');
    const loadedAt=Date.parse(state.generated||'');
    if(!Number.isFinite(availableAt)|| (Number.isFinite(loadedAt)&&availableAt<=loadedAt))return;
    const [sources,articles]=await Promise.all([
      dataFetch('./data/sources.json?check='+Date.now()),
      dataFetch('./data/articles.json?check='+Date.now())
    ]);
    const actualAt=Date.parse(articles.generated_at||'');
    if(!Number.isFinite(actualAt)|| (Number.isFinite(loadedAt)&&actualAt<=loadedAt))return;
    state.sources=Array.isArray(sources.sources)?sources.sources:state.sources;
    state.categories=Array.isArray(sources.categories)?sources.categories:state.categories;
    state.items=Array.isArray(articles.items)?articles.items:state.items;
    state.health=Array.isArray(latestStatus.feeds)?latestStatus.feeds:state.health;
    state.generated=articles.generated_at;
    $('statArticles').textContent=format.format(state.items.length);
    $('statSources').textContent=format.format(state.sources.length);
    $('statCategories').textContent=state.categories.length;
    $('statUpdated').textContent=shortDate(state.generated);
    $('lastUpdate').textContent='Actualizado: '+shortDate(state.generated);
    buildNav();fillSelect();updateHeader();statusSummary();render();
  }catch(error){
    // Una comprobación fallida no debe interrumpir la lectura actual.
    console.warn('Comprobación automática RSS:',error);
  }finally{
    feedRefreshBusy=false;
    scheduleNextCheck();
  }
}

async function dataFetch(path, fallback) {
  const response = await fetch(path,{cache:'no-cache'});
  if (!response.ok) throw new Error(`HTTP ${response.status} al abrir ${path}`);
  return response.json();
}
async function boot() {
  setTheme(state.theme);
  applyDisplaySettings();
  state.mode=state.startMode;
  try {
    const [sources, articles, status] = await Promise.all([
      dataFetch('./data/sources.json'), dataFetch('./data/articles.json'), dataFetch('./data/status.json')
    ]);
    state.sources=Array.isArray(sources.sources)?sources.sources:[];
    state.categories=Array.isArray(sources.categories)?sources.categories:[];
    state.items=Array.isArray(articles.items)?articles.items:[];
    state.health=Array.isArray(status.feeds)?status.feeds:[];
    state.generated=articles.generated_at;
    state.ready=true;
    $('statArticles').textContent=format.format(state.items.length);
    $('statSources').textContent=format.format(state.sources.length);
    $('statCategories').textContent=state.categories.length;
    $('statUpdated').textContent=state.generated ? shortDate(state.generated) : '—';
    $('lastUpdate').textContent=state.generated ? `Actualizado: ${shortDate(state.generated)}` : 'Sin sincronizar';
    $('sidebarSources').textContent=`${state.sources.length} fuentes · ${state.categories.length} categorías`; 
  } catch(err) {
    state.ready=false;
    console.error('Carga de fuentes:',err);
  }
  statusSummary(); navigateFromHash();
}
let progressiveLoads=0;
function initSocialNavigation(){
 $('dashboardSavedAll').addEventListener('click',()=>{state.mode='saved';goTo('all');});
 const back=$('backTop');back.addEventListener('click',()=>window.scrollTo({top:0,behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'}));
 window.addEventListener('scroll',()=>{back.hidden=window.scrollY<600;},{passive:true});
 if('IntersectionObserver' in window){
  const observer=new IntersectionObserver(entries=>{
   if(!entries.some(entry=>entry.isIntersecting)||state.pageView!=='feed'||window.scrollY<350||progressiveLoads>=3||$('loadMore').hidden)return;
   progressiveLoads++;state.page+=1;render();
  },{rootMargin:'250px 0px'});
  observer.observe($('loadMore'));
 }
}
function initHandlers() {
 initSocialNavigation();
 initArticleReader();
  window.setInterval(updateScheduleProgress,10_000);
  scheduleNextCheck();
  $('refreshNow').addEventListener('click',()=>{void refreshPublishedData();});
  window.addEventListener('focus',()=>{if(document.visibilityState==='visible'&&Date.now()>=nextCheckAt){void refreshPublishedData();}});
  document.addEventListener('visibilitychange',()=>{if(!document.hidden){if(Date.now()>=nextCheckAt){void refreshPublishedData();}else{updateScheduleProgress();}}});
  window.addEventListener('hashchange',navigateFromHash);
  $('feedHealthIndicator').addEventListener('click',openFeedHealth);
  $('statusDetails').addEventListener('click',openFeedHealth);
  $('statusDismiss').addEventListener('click',()=>{
    const banner=$('statusBanner');
    try{localStorage.setItem('radar-dismissed-health-notice-v1',banner.dataset.signature||'');}catch{}
    banner.hidden=true;
  });
  $('dashboardHealthButton').addEventListener('click',openFeedHealth);
  const feedHealthDialog=$('feedHealthDialog');
  $('closeFeedHealth').addEventListener('click',()=>feedHealthDialog.close());
  $('doneFeedHealth').addEventListener('click',()=>feedHealthDialog.close());
  feedHealthDialog.addEventListener('click',e=>{if(e.target===feedHealthDialog)feedHealthDialog.close();});
  document.querySelectorAll('.mode-tab').forEach(button=>button.addEventListener('click',()=>{state.mode=button.dataset.mode;state.page=1;progressiveLoads=0;render();}));
  $('columnsSelect').addEventListener('change',event=>{
    if(state.layout!=='cards'){
      state.layout='cards';state.page=1;progressiveLoads=0;
      savePref('layout',state.layout);
    }
    setColumns(event.target.value);render();
  });
  document.querySelector('.view-button[data-view="list"]').addEventListener('click',()=>{
    state.layout='list';state.page=1;progressiveLoads=0;
    savePref('layout',state.layout);applyDisplaySettings();render();
  });
  $('sourceSelect').addEventListener('change',e=>{state.feed=e.target.value;state.page=1;progressiveLoads=0;render();});
  $('searchInput').addEventListener('input',e=>{state.search=e.target.value;state.page=1;progressiveLoads=0;render();});
  $('loadMore').addEventListener('click',()=>{state.page+=1;render();});
  $('themeToggle').addEventListener('click',()=>setTheme(document.body.classList.contains('light')?'dark':'light'));
  $('markAllVisible').addEventListener('click',()=>{const visible=applyFilters().slice(0,state.page*state.pageSize);for(const item of visible)state.read.add(item.id);persist('radar-read',state.read);render();});
  const dialog=$('aboutDialog');
  const open=e=>{if(e)e.preventDefault();dialog.showModal();};
  $('aboutButton').addEventListener('click',open); $('footerInfo').addEventListener('click',open);
  $('closeAbout').addEventListener('click',()=>dialog.close()); $('dialogAccept').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',e=>{if(e.target === dialog) dialog.close();});
  initSettingsHandlers();
  document.addEventListener('keydown',e=>{if(e.key==='/' && !['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName) && !dialog.open && !$('settingsDialog').open && !$('feedHealthDialog').open){e.preventDefault();$('searchInput').focus();}});
}
hydrateIcons(); initHandlers(); updateScheduleProgress(); boot();