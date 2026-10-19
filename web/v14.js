"use strict";
/* Radar RSS V1.4: interfaz pensada para quien llega por primera vez.
   Filtros plegados, mapa opcional en el móvil, pista de acciones y nombres
   de fuentes legibles. Solo guarda preferencias en este navegador. */
(() => {
  const FILTERS_KEY='radar-v14-filters-open', HINT_KEY='radar-v14-card-hint-dismissed';
  const readPref=key=>{try{return localStorage.getItem(key);}catch{return null;}};
  const writePref=(key,value)=>{try{localStorage.setItem(key,value);}catch{}};

  /* ---------- Filtros en un panel plegable ---------- */
  // Las pestañas Todas / Sin leer / Guardadas quedan a la vista; fuente, etiqueta,
  // región, antigüedad y acciones masivas viven detrás de un único botón «Filtros».
  const bar=document.querySelector('#feedView .filter-bar');
  const controls=bar?.querySelector('.filter-controls');
  const toggle=mk('button','v14-filters-toggle');
  const badge=mk('span','v14-filters-count');
  const panel=mk('div','v14-filters-panel');
  function setFiltersOpen(open,remember=true){
    panel.hidden=!open;
    toggle.setAttribute('aria-expanded',String(open));
    toggle.classList.toggle('active',open);
    if(remember)writePref(FILTERS_KEY,open?'true':'false');
  }
  function activeFilters(){
    let count=0;
    if($('sourceSelect')?.value)count++;
    if($('libraryTagFilter')?.value)count++;
    const geo=$('v12Geo');
    if(geo&&!geo.disabled&&geo.value!=='all')count++;
    if(Number(state.maxAge)>0)count++;
    return count;
  }
  function updateFilters(){
    if(!toggle.isConnected)return;
    const count=activeFilters();
    badge.textContent=String(count);badge.hidden=!count;
    toggle.setAttribute('aria-label',count?`Filtros: ${count} activos`:'Filtros');
  }
  if(bar&&controls){
    toggle.type='button';toggle.id='filtersToggle';
    toggle.setAttribute('aria-controls','filtersPanel');
    toggle.append(mk('span','v14-filters-label','Filtros'),badge);
    panel.id='filtersPanel';
    panel.setAttribute('role','group');panel.setAttribute('aria-label','Filtros de noticias');
    const fields=mk('div','v14-filters-fields');
    const source=controls.querySelector('.source-filter');
    const sourceCaption=source?.querySelector('.sr-only');
    if(sourceCaption){sourceCaption.className='v12-control-label';sourceCaption.textContent='Fuente';}
    const tag=controls.querySelector('.library-tag-filter-wrap');
    if(tag&&!tag.querySelector('.v12-control-label'))tag.prepend(mk('span','v12-control-label','Etiqueta'));
    fields.append(...[source,tag].filter(Boolean));
    panel.append(fields);
    const regional=$('v12FilterBar');
    if(regional)panel.append(regional);
    const actions=mk('div','v14-filters-actions');
    const clear=mk('button','settings-secondary','Quitar filtros');
    clear.type='button';clear.id='clearFilters';
    clear.addEventListener('click',()=>{
      const reset=(id,value)=>{
        const el=$(id);
        if(el&&!el.disabled&&el.value!==value){el.value=value;el.dispatchEvent(new Event('change',{bubbles:true}));}
      };
      reset('sourceSelect','');reset('libraryTagFilter','');reset('v12Date','0');reset('v12Geo','all');
      actionToast('Filtros quitados.');
    });
    actions.append(clear);
    const markAll=$('markAllVisible');
    if(markAll)actions.append(markAll);
    panel.append(actions);
    bar.after(panel);
    controls.prepend(toggle);
    toggle.addEventListener('click',()=>setFiltersOpen(panel.hidden));
    setFiltersOpen(readPref(FILTERS_KEY)==='true',false);
  }
  window.RadarFilters={open:()=>setFiltersOpen(true)};

  /* ---------- Nombres de fuentes legibles ---------- */
  // El OPML usa prefijos como «MEDIO —» o «ANÁLISIS —»; en el selector se muestra
  // el nombre limpio y, si informa al lector, el tipo entre paréntesis.
  const baseFillSelect=fillSelect;
  fillSelect=function(...args){
    baseFillSelect(...args);
    const select=$('sourceSelect');
    if(!select)return;
    const byId=new Map(state.sources.map(src=>[src.id,src]));
    const options=[...select.options].slice(1);
    for(const option of options){
      const src=byId.get(option.value);
      if(!src)continue;
      const kind=sourceKind(src.name);
      option.textContent=sourceLabel(src.name)+(kind?` (${kind.label.toLocaleLowerCase('es')})`:'');
    }
    options.sort((a,b)=>a.textContent.localeCompare(b.textContent,'es')).forEach(option=>select.append(option));
  };
  if(state.sources.length)fillSelect();

  /* ---------- Pista de acciones de la tarjeta ---------- */
  // Los botones de la tarjeta son iconos; la primera vez se explica qué hace cada uno.
  const grid=$('articleGrid');
  const hint=mk('div','v14-card-hint');
  if(grid&&readPref(HINT_KEY)!=='true'){
    hint.id='cardHint';hint.setAttribute('role','note');
    const item=(icon,text)=>{const node=mk('span','v14-hint-item');node.append(svgIcon(icon),mk('span','',text));return node;};
    const close=mk('button','v14-hint-close');
    close.type='button';close.setAttribute('aria-label','Entendido, ocultar esta ayuda');close.title='Entendido';
    close.append(svgIcon('x'));
    close.addEventListener('click',()=>{writePref(HINT_KEY,'true');hint.remove();});
    hint.append(mk('strong','','En cada noticia:'),item('check','márcala como leída'),
      item('bookmark','guárdala para después'),item('more','más opciones'),close);
    ($('feedListTitle')||grid).before(hint);
  }
  function updateHint(){
    if(hint.isConnected)hint.hidden=!grid.querySelector('.article-card');
  }

  /* ---------- Mapa radar opcional en el móvil ---------- */
  // En pantallas estrechas la lista numerada va primero y el mapa se abre a pedido.
  const layout=document.querySelector('#dashboardView .radar-layout');
  if(layout&&$('radarFigure')){
    const MAP_CLOSED='Ver mapa de las últimas 24 horas';
    const mapToggle=mk('button','v14-map-toggle',MAP_CLOSED);
    mapToggle.type='button';mapToggle.id='radarMapToggle';
    mapToggle.setAttribute('aria-controls','radarFigure');mapToggle.setAttribute('aria-expanded','false');
    mapToggle.addEventListener('click',()=>{
      const open=!layout.classList.contains('v14-map-open');
      layout.classList.toggle('v14-map-open',open);
      mapToggle.setAttribute('aria-expanded',String(open));
      mapToggle.textContent=open?'Ocultar mapa':MAP_CLOSED;
    });
    layout.append(mapToggle);
  }

  /* ---------- Portada: qué es Radar RSS en una frase ---------- */
  function updateIntro(){
    const intro=$('dashboardIntro');
    const count=state.sources.filter(src=>!state.hiddenSources.has(src.id)).length;
    if(intro&&count)intro.textContent=`Titulares de ${format.format(count)} fuentes, actualizados cada ~6 horas. Abre una noticia para ver un resumen antes de ir al sitio del medio.`;
  }

  const baseRender=render;
  render=function(...args){
    baseRender(...args);
    updateFilters();updateHint();updateIntro();
    // Sin historial de lectura, «Sin leer» coincide con «Todas»: el número no informa.
    document.body.classList.toggle('v14-fresh',state.read.size===0);
  };
  updateFilters();updateIntro();
  document.body.classList.toggle('v14-fresh',state.read.size===0);
})();
