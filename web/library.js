"use strict";
/* Radar RSS library v1 — local only: source folders, tags, saved metadata.
   Runs after app.js without replacing the RSS collector or changing the 5-min checker.
   Browser storage is not a cloud backup. */
(function(){
const ARCHIVE_KEY='radar-saved-archive-v1';
const FOLDER_KEY='radar-source-folders-v1';
const TAG_KEY='radar-article-tags-v1';
const LIMIT=350;
VECTOR_PATHS.folder='<path d="M3 7a2 2 0 0 1 2-2h5l2 2h7a2 2 0 0 1 2 2v10H3z"/>';
VECTOR_PATHS['folder-plus']='<path d="M3 7a2 2 0 0 1 2-2h5l2 2h7a2 2 0 0 1 2 2v10H3zM12 11v6M9 14h6"/>';
const read=(key,fallback)=>{try{return JSON.parse(localStorage.getItem(key)||'null')??fallback;}catch{return fallback;}};
const write=(key,value)=>{
  try{localStorage.setItem(key,JSON.stringify(value));return true;}
  catch(error){console.warn('Radar RSS: no se pudo guardar',key,error);return false;}
};
const snapshot=item=>{
  if(!item||typeof item.id!=='string'||!safeURL(item.url))return null;
  return {
    id:item.id.slice(0,150),url:safeURL(item.url),
    title:String(item.title||'Sin título').slice(0,250),
    image:safeURL(item.image)||null,
    summary:String(item.summary||'').slice(0,900),
    published_at:String(item.published_at||'').slice(0,40),
    first_seen_at:String(item.first_seen_at||'').slice(0,40),
    publisher:String(item.publisher||'').slice(0,90),
    source:String(item.source||'').slice(0,120),
    source_ids:Array.isArray(item.source_ids)?item.source_ids.filter(x=>typeof x==='string').slice(0,20):[],
    categories:Array.isArray(item.categories)?item.categories.filter(x=>typeof x==='string').slice(0,10):[],
    is_radar:Boolean(item.is_radar)
  };
};
const rawArchive=read(ARCHIVE_KEY,[]);
let archive=new Map((Array.isArray(rawArchive)?rawArchive:[]).slice(-LIMIT).map(snapshot).filter(Boolean).map(x=>[x.id,x]));
const rawFolders=read(FOLDER_KEY,{});
let folders=Object.create(null);
function readFolders(data){
  const result=Object.create(null);
  if(!data||typeof data!=='object'||Array.isArray(data))return result;
  for(const [name,ids] of Object.entries(data).slice(0,25)){
    if(!name.trim()||name.length>45||!Array.isArray(ids)||name==='__proto__')continue;
    result[name]=[...new Set(ids.filter(x=>typeof x==='string'&&x.length<150))].slice(0,160);
  }
  return result;
}
folders=readFolders(rawFolders);
const rawTags=read(TAG_KEY,{});
let tags=Object.create(null);
function readTags(data){
  const output=Object.create(null);
  if(!data||typeof data!=='object'||Array.isArray(data))return output;
  for(const [id,values] of Object.entries(data).slice(-3000)){
    if(!id||id.length>150||!Array.isArray(values))continue;
    output[id]=[...new Set(values.filter(x=>typeof x==='string').map(x=>x.trim()).filter(x=>x&&x.length<=30))].slice(0,8);
  }
  return output;
}
tags=readTags(rawTags);
let activeFolder=null,activeTag='';
const saveArchive=()=>write(ARCHIVE_KEY,[...archive.values()].slice(-LIMIT));
const savedNews=()=>{
  const found=new Map(state.items.filter(x=>state.saved.has(x.id)).map(x=>[x.id,x]));
  for(const [id,item] of archive)if(state.saved.has(id)&&!found.has(id))found.set(id,item);
  return [...found.values()];
};
function syncArchive(){
  let changed=false;
  for(const item of state.items){
    if(!state.saved.has(item.id))continue;
    const s=snapshot(item);
    if(!s)continue;
    const previous=archive.get(s.id);
    if(!previous||previous.title!==s.title||previous.summary!==s.summary||previous.image!==s.image){
      archive.delete(s.id);archive.set(s.id,s);changed=true;
    }
  }
  if(changed)saveArchive();
}
function toggleBookmark(item){
  if(state.saved.has(item.id)){
    state.saved.delete(item.id);archive.delete(item.id);
  }else{
    if(archive.size>=LIMIT){actionToast('Máximo de '+LIMIT+' noticias archivadas. Exporta un respaldo y libera espacio antes de seguir.');return;}
    const s=snapshot(item);
    if(!s){actionToast('La noticia no tiene enlace válido.');return;}
    archive.delete(s.id);archive.set(s.id,s);state.saved.add(s.id);
  }
  const saved=saveArchive();
  persist('radar-saved',state.saved);
  render();
  if(!saved)actionToast('Espacio local insuficiente: exporta un respaldo desde Configuración.');
  else actionToast(state.saved.has(item.id)?'Guardada en tu biblioteca local.':'Quitada de guardadas.');
}
function unread(ids){
  const sourceIds=new Set(ids);
  return state.items.reduce((acc,item)=>acc+Number(!state.read.has(item.id)&&(item.source_ids||[]).some(id=>sourceIds.has(id)&&!state.hiddenSources.has(id))),0);
}
const oldBuildNav=buildNav;
buildNav=function(){
  oldBuildNav();
  const buttons=[
    ...$('categoryNav').querySelectorAll(':scope > .nav-link'),
    ...$('libraryFolderNav').querySelectorAll('.system-folder-link')
  ];
  buttons.forEach((button,index)=>{
    if(index===0)return;
    const ids=index===1
      ? state.sources.filter(s=>!state.hiddenSources.has(s.id)).map(s=>s.id)
      : state.sources.filter(s=>s.category===state.categories[index-2]&&!state.hiddenSources.has(s.id)).map(s=>s.id);
    const count=unread(ids);
    const label=button.querySelector('.nav-count');if(label)label.textContent=String(count);
    button.title=count+' sin leer · '+ids.length+' fuentes';
  });
  renderFolderNav();
};
function renderFolderNav(){
  const nav=$('libraryFolderNav');
  // Actualiza solo las carpetas manuales; las del catálogo permanecen intactas.
  nav.querySelectorAll('.library-folder-row').forEach(row=>row.remove());
  const entries=Object.entries(folders);
  entries.forEach(([name,ids])=>{
    const wrapper=mk('div','library-folder-row');
    const b=mk('button','nav-link'+(activeFolder===name?' active':''));
    b.type='button';b.setAttribute('aria-current',activeFolder===name?'page':'false');
    const icon=mk('span','nav-glyph');icon.append(svgIcon('folder'));
    const left=mk('span','nav-left');left.append(icon,mk('span','nav-label',name));
    b.append(left,mk('span','nav-count',String(unread(ids))));
    b.title=ids.length+' fuentes · '+unread(ids)+' sin leer';
    b.addEventListener('click',()=>{window.location.hash='#carpeta/'+encodeURIComponent(name);});
    const del=mk('button','library-folder-delete','×');del.type='button';
    del.setAttribute('aria-label','Eliminar carpeta '+name);
    del.addEventListener('click',()=>{
      if(!confirm('¿Eliminar carpeta «'+name+'»? No se eliminarán las fuentes.'))return;
      delete folders[name];write(FOLDER_KEY,folders);
      if(activeFolder===name)window.location.hash='#noticias';
      else{buildNav();renderSettingsSources();}
    });
    wrapper.append(b,del);nav.append(wrapper);
  });
}
function createFolder(){
  const raw=prompt('Nombre para la carpeta de fuentes:');
  if(raw===null)return;
  const name=raw.trim().replace(/\s+/g,' ').slice(0,45);
  if(!name){actionToast('Introduce un nombre para la carpeta.');return;}
  if(Object.keys(folders).some(n=>n.toLocaleLowerCase('es')===name.toLocaleLowerCase('es'))){actionToast('La carpeta ya existe.');return;}
  if(state.categories.some(id=>categoryLabel(id).toLocaleLowerCase('es')===name.toLocaleLowerCase('es'))){
    actionToast('Esa carpeta ya existe en el catálogo de fuentes.');return;
  }
  if(Object.keys(folders).length>=25){actionToast('Máximo de 25 carpetas.');return;}
  if(name==='__proto__')return;
  folders[name]=[];
  if(!write(FOLDER_KEY,folders)){delete folders[name];actionToast('No se pudo crear la carpeta.');return;}
  buildNav();renderSettingsSources();actionToast('Carpeta creada. Asigna medios en Configuración → Mis fuentes.');
}
function decorateSources(){
  const elements=[...$('settingsSources').querySelectorAll('.settings-source-row')];
  for(const label of elements){
    if(label.closest('.library-source-row'))continue;
    const name=label.querySelector('.settings-source-name')?.textContent||'';
    const cat=label.querySelector('small')?.textContent||'';
    const source=state.sources.find(s=>s.name===name&&categoryLabel(s.category)===cat);
    if(!source)continue;
    const wrapper=mk('div','library-source-row');
    const select=mk('select','library-source-folder');
    select.setAttribute('aria-label','Carpeta de '+name);
    select.append(new Option('Sin carpeta',''));
    for(const folderName of Object.keys(folders))select.append(new Option(folderName,folderName));
    select.value=Object.entries(folders).find(([,ids])=>ids.includes(source.id))?.[0]||'';
    select.addEventListener('change',()=>{
      for(const ids of Object.values(folders)){
        const i=ids.indexOf(source.id);if(i>=0)ids.splice(i,1);
      }
      if(select.value&&folders[select.value])folders[select.value].push(source.id);
      write(FOLDER_KEY,folders);buildNav();
      if(activeFolder)render();
    });
    label.replaceWith(wrapper);wrapper.append(label,select);
  }
}
const oldSources=renderSettingsSources;
renderSettingsSources=function(){oldSources();decorateSources();};
const oldNavigate=navigateFromHash;
navigateFromHash=function(){
  const hash=decodeURIComponent(window.location.hash.slice(1));
  activeFolder=hash.startsWith('carpeta/')&&Object.prototype.hasOwnProperty.call(folders,hash.slice(8))?hash.slice(8):null;
  if(activeFolder)state.mode='all';
  oldNavigate();
  if(activeFolder){
    $('topbarSection').textContent=activeFolder;
    $('feedHeading').textContent=activeFolder;
    $('feedDescription').textContent='Noticias de los medios que agrupaste en esta carpeta.';
    $('sectionEyebrow').textContent='CARPETA PERSONAL';
  }
  buildNav();
};
const oldFillSelect=fillSelect;
fillSelect=function(){
  oldFillSelect();
  if(activeFolder){
    for(const option of [...$('sourceSelect').options].slice(1)){
      if(!folders[activeFolder]?.includes(option.value))option.remove();
    }
    if($('sourceSelect').value&&!folders[activeFolder]?.includes($('sourceSelect').value)){
      $('sourceSelect').value='';state.feed='';
    }
  }
};
const oldApplyFilters=applyFilters;
applyFilters=function(){
  // Same filter semantics, with archived saved items, tags, and source folders.
  const blocked=state.mutedKeywords.split(',').map(x=>stripAccents(x.trim())).filter(x=>x.length>1).slice(0,30);
  const query=stripAccents(state.search.trim());
  const input=state.mode==='saved'?savedNews():state.items;
  const filtered=input.filter(item=>{
    if(state.category!=='all'&&!(item.categories||[]).includes(state.category))return false;
    if(state.mode!=='saved'&&!(item.source_ids||[]).some(id=>!state.hiddenSources.has(id)))return false;
    if(activeFolder&&!(item.source_ids||[]).some(id=>(folders[activeFolder]||[]).includes(id)))return false;
    if(state.feed&&!(item.source_ids||[]).includes(state.feed))return false;
    if(state.maxAge&&state.mode!=='saved'){
      const t=new Date(item.published_at).getTime();
      if(!Number.isFinite(t)||(Date.now()-t)>state.maxAge*86400000)return false;
    }
    if(state.mode==='saved'&&!state.saved.has(item.id))return false;
    if(state.mode==='unread'&&state.read.has(item.id))return false;
    if(state.hideRead&&state.mode!=='saved'&&state.read.has(item.id))return false;
    if(activeTag&&!(tags[item.id]||[]).includes(activeTag))return false;
    const text=stripAccents([item.title,item.summary,item.publisher,item.source,...(tags[item.id]||[])].join(' '));
    return(!query||text.includes(query))&&!blocked.some(w=>text.includes(w));
  });
  if(state.sort==='oldest')filtered.sort((a,b)=>new Date(a.published_at||a.first_seen_at||0)-new Date(b.published_at||b.first_seen_at||0));
  else if(state.sort==='source')filtered.sort((a,b)=>String(a.publisher||a.source||'').localeCompare(String(b.publisher||b.source||''),'es'));
  return filtered;
};
const oldDashboard=renderDashboard;
renderDashboard=function(){
  oldDashboard();
  const panel=$('dashboardSavedPanel'),list=$('dashboardSavedList');
  const items=savedNews().sort((a,b)=>new Date(b.published_at||b.first_seen_at||0)-new Date(a.published_at||a.first_seen_at||0)).slice(0,4);
  panel.hidden=!items.length;
  list.replaceChildren(...items.map(item=>{
    const row=mk('div','dashboard-saved-item'),body=mk('div','dashboard-saved-content');
    const cover=mk('a','dashboard-saved-cover');cover.href=safeURL(item.url)||'#';cover.target='_blank';cover.rel='noopener noreferrer external';
    cover.addEventListener('click',e=>openArticleReader(item,e));
    if(safeURL(item.image)){const image=mk('img');image.loading='lazy';image.src=item.image;image.alt='';image.referrerPolicy='no-referrer';cover.append(image);}
    else cover.append(svgIcon('bookmark'));
    const a=link(item.url,item.title||'Sin título','dashboard-saved-title');a.addEventListener('click',e=>openArticleReader(item,e));
    body.append(a,mk('span','dashboard-saved-meta',item.publisher||item.source||'Fuente RSS'));row.append(cover,body);return row;
  }));
};
const oldCard=card;
card=function(item){
  const el=oldCard(item);
  const prev=el.querySelector('.article-save');
  if(prev){
    const replacement=prev.cloneNode(true);
    prev.replaceWith(replacement);
    replacement.addEventListener('click',()=>toggleBookmark(item));
  }
  return el;
};
const oldRead=markRead;
markRead=function(...args){oldRead(...args);updateUnreadCounts();};
function updateUnreadCounts(){
  const buttons=[
    ...$('categoryNav').querySelectorAll(':scope > .nav-link'),
    ...$('libraryFolderNav').querySelectorAll('.system-folder-link')
  ];
  buttons.forEach((btn,i)=>{
    if(i===0)return;
    const ids=i===1?state.sources.map(s=>s.id):state.sources.filter(s=>s.category===state.categories[i-2]).map(s=>s.id);
    const n=unread(ids);const count=btn.querySelector('.nav-count');
    if(count)count.textContent=String(n);
    btn.title=n+' noticias sin leer';
  });
  renderFolderNav();
}
const oldRender=render;
render=function(){
  syncArchive();
  oldRender();
  refreshTagFilter();
  updateUnreadCounts();
};
const oldOpen=openArticleReader;
openArticleReader=function(item,e){
  oldOpen(item,e);
  if(e&&(e.metaKey||e.ctrlKey||e.shiftKey||e.altKey||e.button!==0))return;
  $('libraryTagInput').value='';
  renderTags();
};
function allTags(){return [...new Set(Object.values(tags).flat())].sort((a,b)=>a.localeCompare(b,'es'));}
function refreshTagFilter(){
  const select=$('libraryTagFilter'),names=allTags();
  select.replaceChildren(new Option('Todas las etiquetas',''),...names.map(x=>new Option(x,x)));
  if(activeTag&&!names.includes(activeTag))activeTag='';
  select.value=activeTag;
}
function renderTags(){
  const el=$('libraryReaderTags');el.replaceChildren();
  if(!activeReaderItem)return;
  for(const name of (tags[activeReaderItem.id]||[])){
    const b=mk('button','library-tag-chip',name+' ×');b.type='button';b.title='Eliminar etiqueta '+name;
    b.addEventListener('click',()=>{
      const remaining=(tags[activeReaderItem.id]||[]).filter(x=>x!==name);
      if(remaining.length)tags[activeReaderItem.id]=remaining;else delete tags[activeReaderItem.id];
      write(TAG_KEY,tags);renderTags();refreshTagFilter();render();
    });
    el.append(b);
  }
}
function addTag(){
  if(!activeReaderItem)return;
  const input=$('libraryTagInput');
  const name=input.value.trim().replace(/\s+/g,' ').slice(0,30);
  if(!name)return;
  const current=tags[activeReaderItem.id]||[];
  if(current.some(x=>x.toLocaleLowerCase('es')===name.toLocaleLowerCase('es')))return;
  if(current.length>=8){actionToast('Máximo 8 etiquetas por noticia.');return;}
  tags[activeReaderItem.id]=[...current,name];
  if(!write(TAG_KEY,tags))actionToast('No se pudieron guardar las etiquetas.');
  input.value='';renderTags();refreshTagFilter();render();
}
function mount(){
  const foldersSection=mk('section','source-folders-section');
  foldersSection.setAttribute('aria-labelledby','sourceFoldersHeading');
  const header=mk('div','folder-group-head');
  const heading=mk('span','','CARPETAS DE FUENTES');
  heading.id='sourceFoldersHeading';header.append(heading);
  const add=mk('button');add.type='button';add.title='Crear carpeta de fuentes';add.setAttribute('aria-label','Crear carpeta de fuentes');
  add.append(svgIcon('folder-plus'));header.append(add);
  const nav=mk('nav','library-folder-nav library-system-folders');
  nav.id='libraryFolderNav';
  nav.setAttribute('aria-label','Carpetas de fuentes del catálogo y creadas por ti');
  foldersSection.append(header,nav);
  $('categoryNav').after(foldersSection);
  add.addEventListener('click',createFolder);
  const wrapper=mk('label','library-tag-filter-wrap'),filter=mk('select','library-tag-filter');
  filter.id='libraryTagFilter';filter.setAttribute('aria-label','Filtrar por etiqueta');wrapper.append(filter);
  $('sourceSelect').closest('label').after(wrapper);
  filter.addEventListener('change',()=>{activeTag=filter.value;state.page=1;render();});
  const section=mk('section','reader-organize');
  section.append(mk('strong','','Etiquetas personales'));
  const inputRow=mk('div','reader-tag-create');const input=mk('input');input.id='libraryTagInput';input.type='text';input.maxLength=30;input.placeholder='Ej.: Investigación';input.setAttribute('aria-label','Nueva etiqueta');
  const btn=mk('button','','Añadir');btn.type='button';inputRow.append(input,btn);section.append(inputRow);
  const names=mk('div','reader-tags');names.id='libraryReaderTags';section.append(names);
  section.append(mk('p','','Etiquetas disponibles en este navegador. Para conservar el artículo fuera del RSS, utiliza Guardar.'));
  $('readerNote').after(section);
  btn.addEventListener('click',addTag);
  input.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();addTag();}});
  const sourcePane=document.querySelector('[data-settings-pane="sources"]');
  const group=mk('div','folder-settings');
  group.append(mk('span','','Organiza tus fuentes en carpetas personales.'));
  const folderButton=mk('button','settings-secondary','Crear carpeta');folderButton.type='button';group.append(folderButton);
  sourcePane.querySelector('.setting-hint').after(group);folderButton.addEventListener('click',createFolder);
  // El buscador original conserva una referencia directa a renderSettingsSources.
  // Decorar después del render sin perder la escucha de búsqueda existente.
  $('settingsSourceSearch').addEventListener('input',()=>queueMicrotask(decorateSources));
  $('readerSave').addEventListener('click',e=>{
    if(!activeReaderItem)return;
    e.preventDefault();e.stopImmediatePropagation();
    toggleBookmark(activeReaderItem);syncReaderActions();
  },true);
  $('clearSaved').addEventListener('click',e=>{
    e.preventDefault();e.stopImmediatePropagation();
    if(!confirm('¿Vaciar las noticias guardadas y sus copias locales?'))return;
    state.saved.clear();archive.clear();saveArchive();persist('radar-saved',state.saved);render();updateDataCounts();$('dataNotice').textContent='Guardadas vaciadas.';
  },true);
  $('exportData').addEventListener('click',e=>{
    e.preventDefault();e.stopImmediatePropagation();syncArchive();
    const obj={format:'radar-rss-settings-v3',exported_at:new Date().toISOString(),
      preferences:{theme:state.theme,layout:state.layout,columns:state.columns,density:state.density,pageSize:state.pageSize,maxAge:state.maxAge,fontSize:state.fontSize,showHero:state.showHero,showImages:state.showImages,showSummaries:state.showSummaries,hideRead:state.hideRead,newTab:state.newTab,sort:state.sort,startMode:state.startMode,mutedKeywords:state.mutedKeywords},
      saved:[...state.saved],read:[...state.read],hiddenSources:[...state.hiddenSources],
      savedArchive:[...archive.values()],sourceFolders:folders,articleTags:tags};
    downloadText('radar-rss-respaldo-completo.json',JSON.stringify(obj,null,2),'application/json;charset=utf-8');
    $('dataNotice').textContent='Respaldo completo generado con guardadas, etiquetas y carpetas.';
  },true);
  $('importData').addEventListener('change',async e=>{
    e.stopImmediatePropagation();
    const file=e.target.files?.[0];e.target.value='';if(!file)return;
    if(file.size>5_000_000){$('dataNotice').textContent='Respaldo mayor de 5 MB.';return;}
    try{
      const d=JSON.parse(await file.text());
      if(!['radar-rss-settings-v2','radar-rss-settings-v3'].includes(d.format)||!d.preferences)throw Error('Formato incompatible');
      const p=d.preferences,choose=(key,options,def)=>options.includes(p[key])?p[key]:def;
      state.theme=choose('theme',['system','light','dark'],'light');
      state.layout=choose('layout',['cards','list'],'cards');
      state.columns=choose('columns',['auto','2','3','4','5','6'],'auto');
      state.density=choose('density',['comfortable','compact'],'comfortable');
      state.pageSize=choose('pageSize',[12,24,36,60],36);
      state.maxAge=choose('maxAge',[0,1,7,30,90],0);
      state.fontSize=choose('fontSize',['normal','large'],'normal');
      for(const key of ['showHero','showImages','showSummaries','hideRead','newTab'])if(typeof p[key]==='boolean')state[key]=p[key];
      state.sort=choose('sort',['newest','oldest','source'],'newest');
      state.startMode=choose('startMode',['all','unread','saved'],'all');
      state.mutedKeywords=typeof p.mutedKeywords==='string'?p.mutedKeywords.slice(0,600):'';
      const known=new Set(state.sources.map(s=>s.id));
      state.saved=new Set((Array.isArray(d.saved)?d.saved:[]).filter(x=>typeof x==='string'&&x.length<150).slice(-4000));
      state.read=new Set((Array.isArray(d.read)?d.read:[]).filter(x=>typeof x==='string'&&x.length<150).slice(-4000));
      state.hiddenSources=new Set((Array.isArray(d.hiddenSources)?d.hiddenSources:[]).filter(x=>known.has(x)));
      persist('radar-saved',state.saved);persist('radar-read',state.read);persist('radar-hidden-sources',state.hiddenSources);
      archive=new Map((Array.isArray(d.savedArchive)?d.savedArchive:[]).slice(-LIMIT).map(snapshot).filter(Boolean).filter(x=>state.saved.has(x.id)).map(x=>[x.id,x]));
      folders=readFolders(d.sourceFolders);tags=readTags(d.articleTags);
      saveArchive();write(FOLDER_KEY,folders);write(TAG_KEY,tags);syncArchive();
      for(const [key,value] of [['layout',state.layout],['columns',state.columns],['theme',state.theme],['density',state.density],['font',state.fontSize],['page-size',state.pageSize],['max-age',state.maxAge],['show-hero',state.showHero],['show-images',state.showImages],['show-summaries',state.showSummaries],['hide-read',state.hideRead],['new-tab',state.newTab],['sort',state.sort],['start-mode',state.startMode],['keywords',state.mutedKeywords]])savePref(key,value);
      state.mode=state.startMode;state.page=1;
      setTheme(state.theme);applyDisplaySettings();refreshFeedUI();syncSettings();selectedTab('data');
      $('dataNotice').textContent='Respaldo importado correctamente.';
    }catch(err){console.warn('Importación Radar RSS',err);$('dataNotice').textContent='Archivo inválido o incompatible.';}
  },true);
  refreshTagFilter();renderFolderNav();
}
// UI is ready: deferred script executes after DOM is parsed, before boot resolves.
mount();
})();