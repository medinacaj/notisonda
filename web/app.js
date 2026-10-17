"use strict";
// Radar RSS: interfaz pública sin autenticación y sin HTML sin sanear de fuentes externas.
const $ = (id) => document.getElementById(id);
const format = new Intl.NumberFormat('es-CL');
function storeGet(key) { try { return localStorage.getItem(key); } catch { return null; } }
const state = {
  sources: [], categories: [], items: [], health: [], generated: null,
  category: 'all', feed: '', mode: 'all', layout: storeGet('radar-layout') === 'list' ? 'list' : 'cards',
  theme: storeGet('radar-theme') === 'light' ? 'light' : 'dark',
  search: '', page: 1, ready: false,
  saved: safeStoredSet('radar-saved'), read: safeStoredSet('radar-read')
};
const PAGE_SIZE = 36;
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
function setTheme(theme) {
  state.theme = theme;
  document.body.classList.toggle('light', theme === 'light');
  $('themeGlyph').textContent = theme === 'light' ? '☾' : '☀';
  try { localStorage.setItem('radar-theme', theme); } catch {}
}
function buildNav() {
  const nav = $('categoryNav'); nav.replaceChildren();
  const choices = [{id:'all', label:'Todas las noticias'}, ...state.categories.map(x => ({id:x, label:categoryLabel(x)}))];
  choices.forEach((cat, i) => {
    const button = mk('button', `nav-link ${state.category === cat.id ? 'active' : ''}`);
    button.type='button'; button.setAttribute('aria-current', state.category === cat.id ? 'page' : 'false');
    const left = mk('span', 'nav-left'); left.append(mk('span','nav-glyph',i === 0 ? '▦' : ICONS[i-1]),mk('span','nav-label',cat.label));
    const count = i === 0 ? state.sources.length : state.sources.filter(x => x.category === cat.id).length;
    button.append(left,mk('span','nav-count',String(count)));
    button.addEventListener('click', () => { state.category = cat.id; state.feed=''; $('sourceSelect').value=''; state.page=1; updateHeader(); buildNav(); fillSelect(); render(); });
    nav.append(button);
  });
}
function fillSelect() {
  const select = $('sourceSelect'); const old = state.feed; select.replaceChildren();
  const defaultOpt = document.createElement('option'); defaultOpt.value=''; defaultOpt.textContent='Todas las fuentes'; select.append(defaultOpt);
  state.sources.filter(x => state.category === 'all' || x.category === state.category)
    .sort((a,b) => a.name.localeCompare(b.name,'es'))
    .forEach(x => { const option=document.createElement('option'); option.value=x.id; option.textContent=x.name; select.append(option); });
  select.value = old && [...select.options].some(x => x.value === old) ? old : '';
  state.feed = select.value;
}
function updateHeader() {
  const name = state.category === 'all' ? 'Todas las noticias' : categoryLabel(state.category);
  $('feedHeading').textContent = name;
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
  const query = stripAccents(state.search.trim());
  return state.items.filter(item => {
    if (state.category !== 'all' && !(item.categories || []).includes(state.category)) return false;
    if (state.feed && !(item.source_ids || []).includes(state.feed)) return false;
    if (state.mode === 'saved' && !state.saved.has(item.id)) return false;
    if (state.mode === 'unread' && state.read.has(item.id)) return false;
    if (query && !stripAccents([item.title,item.summary,item.publisher,item.source].join(' ')).includes(query)) return false;
    return true;
  });
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
  const cover=mk('a','cover'); cover.href=safeURL(item.url) || '#'; cover.target='_blank'; cover.rel='noopener noreferrer external'; cover.referrerPolicy='no-referrer';
  cover.addEventListener('click',() => markRead(item.id, true));
  if (safeURL(item.image)) {
    const img=document.createElement('img'); img.src=item.image; img.alt=''; img.loading='lazy'; img.referrerPolicy='no-referrer';
    img.addEventListener('error',() => { img.remove(); cover.prepend(mk('div','cover-fallback','RADAR')); },{once:true}); cover.append(img);
  } else { cover.append(mk('div','cover-fallback', 'RADAR')); }
  const category=(item.categories || [])[0] || '';
  cover.append(mk('span','cover-badge',categoryLabel(category)));
  const content=mk('div','article-content');
  const meta=mk('div','article-meta'); meta.append(mk('span','publisher',item.publisher || item.source || 'Fuente RSS'),mk('time','',ageDate(item.published_at)));
  const title=mk('h3','article-title'); const titleLink=link(item.url,item.title || 'Sin título'); titleLink.addEventListener('click',() => markRead(item.id,true)); title.append(titleLink);
  const excerpt=mk('p','article-excerpt',item.summary || 'Accede a la noticia original para leer el contenido completo.');
  const bottom=mk('div','article-bottom'); const open=link(item.url,'Leer original ↗','read-link'); open.addEventListener('click',()=>markRead(item.id,true));
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
  const filtered=applyFilters(), visible=filtered.slice(0,state.page*PAGE_SIZE);
  $('visibleCount').textContent=`${format.format(filtered.length)} ARTÍCULOS`;
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
  $('themeToggle').addEventListener('click',()=>setTheme(state.theme === 'dark' ? 'light' : 'dark'));
  const dialog=$('aboutDialog');
  const open=e=>{if(e)e.preventDefault();dialog.showModal();};
  $('aboutButton').addEventListener('click',open); $('footerInfo').addEventListener('click',open);
  $('closeAbout').addEventListener('click',()=>dialog.close()); $('dialogAccept').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',e=>{if(e.target === dialog) dialog.close();});
  // Editar githubLink en index.html una vez publicado el repositorio.
  document.addEventListener('keydown',e=>{if(e.key==='/' && !['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName) && !dialog.open){e.preventDefault();$('searchInput').focus();}});
}
initHandlers(); boot();