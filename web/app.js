"use strict";
// Radar RSS: interfaz pública sin autenticación y sin HTML sin sanear de fuentes externas.
const $ = (id) => document.getElementById(id);
const format = new Intl.NumberFormat('es-CL');
function storeGet(key) { try { return localStorage.getItem(key); } catch { return null; } }
const state = {
  sources: [], categories: [], items: [], health: [], generated: null,
  category: 'all', feed: '', mode: 'all', layout: storeGet('radar-layout') === 'list' ? 'list' : 'cards',
  theme: ['system','light','dark'].includes(storeGet('radar-theme')) ? storeGet('radar-theme') : 'system',
  search: '', page: 1, ready: false,
  density: storeGet('radar-density') === 'compact' ? 'compact' : 'comfortable',
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
const ICONS = ['✧', '⌘', '◉', '♧', '◈', '◎'];
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
  $('themeGlyph').textContent=light?'☾':'☀';
  try{localStorage.setItem('radar-theme',state.theme);}catch{}
}
function applyDisplaySettings() {
  document.body.classList.toggle('compact',state.density==='compact');
  document.body.classList.toggle('font-large',state.fontSize==='large');
  document.body.classList.toggle('show-hero',state.showHero);
  document.body.classList.toggle('hide-images',!state.showImages);
  document.body.classList.toggle('hide-summaries',!state.showSummaries);
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
  $('settingLayout').addEventListener('change',e=>{state.layout=e.target.value;savePref('layout',state.layout);state.page=1;render();});
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
    const data={format:'radar-rss-settings-v2',exported_at:new Date().toISOString(),preferences:{theme:state.theme,layout:state.layout,density:state.density,pageSize:state.pageSize,maxAge:state.maxAge,fontSize:state.fontSize,showHero:state.showHero,showImages:state.showImages,showSummaries:state.showSummaries,hideRead:state.hideRead,newTab:state.newTab,sort:state.sort,startMode:state.startMode,mutedKeywords:state.mutedKeywords},hiddenSources:[...state.hiddenSources],saved:[...state.saved],read:[...state.read]};
    downloadText('radar-rss-preferencias.json',JSON.stringify(data,null,2),'application/json;charset=utf-8');
    $('dataNotice').textContent='Archivo de respaldo generado.';
  });
  $('importData').addEventListener('change',async e=>{
    const file=e.target.files?.[0];e.target.value='';if(!file)return;
    if(file.size>1_000_000){$('dataNotice').textContent='El archivo supera el límite de 1 MB.';return;}
    try{
      const data=JSON.parse(await file.text());if(data.format!=='radar-rss-settings-v2'||typeof data.preferences!=='object')throw Error('Formato incompatible');
      const p=data.preferences,select=(key,allowed,def)=>allowed.includes(p[key])?p[key]:def;
      state.theme=select('theme',['system','light','dark'],'system');state.layout=select('layout',['cards','list'],'cards');state.density=select('density',['comfortable','compact'],'comfortable');
      state.pageSize=select('pageSize',[12,24,36,60],36);state.maxAge=select('maxAge',[0,1,7,30,90],0);state.fontSize=select('fontSize',['normal','large'],'normal');
      for(const field of ['showHero','showImages','showSummaries','hideRead','newTab'])if(typeof p[field]==='boolean')state[field]=p[field];
      state.sort=select('sort',['newest','oldest','source'],'newest');state.startMode=select('startMode',['all','unread','saved'],'all');state.mutedKeywords=typeof p.mutedKeywords==='string'?p.mutedKeywords.slice(0,600):'';
      const valid=new Set(state.sources.map(x=>x.id));
      for(const [k,key,onlyValid] of [['hiddenSources','radar-hidden-sources',true],['saved','radar-saved',false],['read','radar-read',false]]){
        state[k]=new Set((Array.isArray(data[k])?data[k]:[]).filter(x=>typeof x==='string'&&x.length<150&&(!onlyValid||valid.has(x))).slice(-4000));persist(key,state[k]);
      }
      for(const [key,value] of [['layout',state.layout],['theme',state.theme],['density',state.density],['font',state.fontSize],['page-size',state.pageSize],['max-age',state.maxAge],['show-hero',state.showHero],['show-images',state.showImages],['show-summaries',state.showSummaries],['hide-read',state.hideRead],['new-tab',state.newTab],['sort',state.sort],['start-mode',state.startMode],['keywords',state.mutedKeywords]])savePref(key,value);
      state.mode=state.startMode;state.page=1;setTheme(state.theme);applyDisplaySettings();refreshFeedUI();syncSettings();selectedTab('data');$('dataNotice').textContent='Preferencias y datos importados correctamente.';
    }catch{$('dataNotice').textContent='No se pudo importar. Utiliza un respaldo JSON generado por Radar RSS.';}
  });
  $('clearRead').addEventListener('click',()=>{if(confirm('¿Borrar el historial de lectura de este navegador?')){state.read.clear();persist('radar-read',state.read);state.page=1;render();updateDataCounts();$('dataNotice').textContent='Historial borrado.';}});
  $('clearSaved').addEventListener('click',()=>{if(confirm('¿Vaciar los artículos guardados en este navegador?')){state.saved.clear();persist('radar-saved',state.saved);state.page=1;render();updateDataCounts();$('dataNotice').textContent='Guardadas vaciadas.';}});
  $('resetSettings').addEventListener('click',()=>{
    if(!confirm('¿Restablecer las preferencias? Tus artículos leídos y guardados no se borrarán.'))return;
    for(const key of ['layout','theme','density','font','page-size','max-age','show-hero','show-images','show-summaries','hide-read','new-tab','sort','start-mode','keywords','hidden-sources']){try{localStorage.removeItem('radar-'+key);}catch{}}
    state.theme='system';state.layout='cards';state.density='comfortable';state.fontSize='normal';state.pageSize=36;state.maxAge=0;
    state.showHero=false;state.showImages=true;state.showSummaries=true;state.hideRead=false;state.newTab=true;state.sort='newest';state.startMode='all';state.mode='all';state.mutedKeywords='';state.hiddenSources.clear();state.page=1;
    setTheme('system');applyDisplaySettings();$('settingsSourceSearch').value='';refreshFeedUI();syncSettings();selectedTab('data');$('dataNotice').textContent='Preferencias restablecidas.';
  });
}
function buildNav() {
  const nav = $('categoryNav'); nav.replaceChildren();
  const choices = [{id:'all', label:'Todas las noticias'}, ...state.categories.map(x => ({id:x, label:categoryLabel(x)}))];
  choices.forEach((cat, i) => {
    const button = mk('button', `nav-link ${state.category === cat.id ? 'active' : ''}`);
    button.type='button'; button.setAttribute('aria-current', state.category === cat.id ? 'page' : 'false');
    const left = mk('span', 'nav-left'); left.append(mk('span','nav-glyph',i === 0 ? '▦' : ICONS[i-1]),mk('span','nav-label',cat.label));
    const count = i === 0 ? state.sources.filter(x=>!state.hiddenSources.has(x.id)).length : state.sources.filter(x => x.category === cat.id && !state.hiddenSources.has(x.id)).length;
    button.append(left,mk('span','nav-count',String(count)));
    button.addEventListener('click', () => { state.category = cat.id; state.feed=''; $('sourceSelect').value=''; state.page=1; updateHeader(); buildNav(); fillSelect(); render(); });
    nav.append(button);
  });
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
  $('topbarSection').textContent = name;
  $('sectionEyebrow').textContent = state.category === 'all' ? 'SELECCIÓN EDITORIAL' : 'EXPLORAR CATEGORÍA';
  $('feedDescription').textContent = state.category === 'all' ? 'Titulares y novedades de todas las fuentes.' : `Publicaciones seleccionadas de ${name.toLowerCase()}.`;
}
function statusSummary() {
  const status = $('statusBanner'); status.hidden=true;
  if (!state.ready) { status.hidden=false; status.textContent='No fue posible cargar los archivos de noticias. Verifica la publicación de GitHub Pages y vuelve a intentarlo.'; return; }
  if (!state.generated && !state.items.length) { status.hidden=false; status.textContent='La aplicación está lista, pero la primera recopilación de noticias todavía no se ha ejecutado. En GitHub, abre Actions y ejecuta “Actualizar noticias y publicar”.'; return; }
  const errors = state.health.filter(x => x.state === 'error').length;
  const stale = state.health.filter(x => x.state === 'stale').length;
  if (errors || stale) { status.hidden=false; status.textContent=`Revisión de fuentes: ${errors} con error de lectura y ${stale} con últimas fechas anteriores a 12 meses. No se eliminan automáticamente; se recomienda revisar sus RSS y el sitio editorial.`; }
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
function emptyState(filtered) {
  const isEmpty = !state.items.length;
  const el = mk('div','empty-state');
  el.append(mk('div','empty-icon',isEmpty ? '◌' : '⌕'),
    mk('h3','',isEmpty ? 'Esperando las primeras noticias' : 'No hay noticias con estos filtros'),
    mk('p','',isEmpty ? 'El diseño y las 150 fuentes están preparados. La recopilación debe ejecutarse desde GitHub Actions después de publicar el proyecto.' : 'Prueba otra categoría o fuente, desmarca tus filtros o busca con otros términos.'));
  return el;
}
function card(item) {
  const el=mk('article','article-card'+(state.read.has(item.id) ? ' read-article':'')); el.dataset.articleId=item.id;
  const cover=mk('a','cover'); cover.href=safeURL(item.url) || '#'; cover.target=state.newTab?'_blank':'_self'; cover.rel='noopener noreferrer external'; cover.referrerPolicy='no-referrer';
  cover.addEventListener('click',() => markRead(item.id, true));
  if (safeURL(item.image)) {
    const img=document.createElement('img'); img.src=item.image; img.alt=''; img.loading='lazy'; img.referrerPolicy='no-referrer';
    img.addEventListener('error',() => { img.remove(); cover.prepend(mk('div','cover-fallback','RADAR')); },{once:true}); cover.append(img);
  } else { cover.append(mk('div','cover-fallback', 'RADAR')); }
  const category=(item.categories || [])[0] || '';
  cover.append(mk('span','cover-badge',categoryLabel(category)));
  const content=mk('div','article-content');
  const meta=mk('div','article-meta'); meta.append(mk('span','publisher',item.publisher || item.source || 'Fuente RSS'),mk('time','',ageDate(item.published_at)));
  const title=mk('h3','article-title'); const titleLink=link(item.url,item.title || 'Sin título'); titleLink.target=state.newTab?'_blank':'_self'; titleLink.addEventListener('click',() => markRead(item.id,true)); title.append(titleLink);
  const excerpt=mk('p','article-excerpt',item.summary || 'Accede a la noticia original para leer el contenido completo.');
  const bottom=mk('div','article-bottom'); const open=link(item.url,'Leer original ↗','read-link'); open.target=state.newTab?'_blank':'_self'; open.addEventListener('click',()=>markRead(item.id,true));
  const save=mk('button','save-btn'+(state.saved.has(item.id) ? ' saved' : ''),state.saved.has(item.id)?'★':'☆'); save.type='button'; save.title=state.saved.has(item.id) ? 'Quitar de guardadas' : 'Guardar noticia'; save.setAttribute('aria-label',save.title); save.setAttribute('aria-pressed',String(state.saved.has(item.id)));
  save.addEventListener('click',() => {if(state.saved.has(item.id))state.saved.delete(item.id);else state.saved.add(item.id);persist('radar-saved',state.saved);render();});
  bottom.append(open,save); content.append(meta,title,excerpt,bottom); el.append(cover,content); return el;
}
function markRead(id, value) {
  if (value) state.read.add(id); else state.read.delete(id);
  persist('radar-read',state.read);
  if (state.mode === 'unread') render();
  else document.querySelectorAll('.article-card').forEach(el => { if(el.dataset.articleId===id) el.classList.add('read-article'); });
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
  buildNav(); fillSelect(); updateHeader(); statusSummary(); render();
}
function initHandlers() {
  document.querySelectorAll('.mode-tab').forEach(button=>button.addEventListener('click',()=>{state.mode=button.dataset.mode;state.page=1;render();}));
  document.querySelectorAll('.view-button').forEach(button=>button.addEventListener('click',()=>{state.layout=button.dataset.view;state.page=1;try{localStorage.setItem('radar-layout',state.layout);}catch{}render();}));
  $('sourceSelect').addEventListener('change',e=>{state.feed=e.target.value;state.page=1;render();});
  $('searchInput').addEventListener('input',e=>{state.search=e.target.value;state.page=1;render();});
  $('loadMore').addEventListener('click',()=>{state.page+=1;render();});
  $('themeToggle').addEventListener('click',()=>setTheme(document.body.classList.contains('light')?'dark':'light'));
  $('markAllVisible').addEventListener('click',()=>{const visible=applyFilters().slice(0,state.page*state.pageSize);for(const item of visible)state.read.add(item.id);persist('radar-read',state.read);render();});
  const dialog=$('aboutDialog');
  const open=e=>{if(e)e.preventDefault();dialog.showModal();};
  $('aboutButton').addEventListener('click',open); $('footerInfo').addEventListener('click',open);
  $('closeAbout').addEventListener('click',()=>dialog.close()); $('dialogAccept').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',e=>{if(e.target === dialog) dialog.close();});
  initSettingsHandlers();
  document.addEventListener('keydown',e=>{if(e.key==='/' && !['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName) && !dialog.open && !$('settingsDialog').open){e.preventDefault();$('searchInput').focus();}});
}
initHandlers(); boot();