"use strict";
/* Homepage headlines remain real articles and follow the reader's source preferences. */
(() => {
  const recent=$('dashboardRecent'),columns=$('newsroomColumns');
  const panel=recent?.closest('.newsroom-lead-latest');
  if(!recent||!panel||!columns)return;
  panel.classList.add('homepage-latest');
  const lead=$('dashboardFeature').closest('.dashboard-feature-panel');
  columns.hidden=true;
  columns.before(lead,panel);
  $('dashboardRecentTitle').textContent='En un vistazo';
  const notice=$('sinceVisit');lead.before(notice);
  recent.setAttribute('role','region');recent.setAttribute('aria-roledescription','carrusel');
  recent.setAttribute('aria-label','Últimas noticias de distintas secciones');recent.tabIndex=0;
  const controls=mk('div','latest-carousel-controls');
  const previous=mk('button','','Anterior'),next=mk('button','','Siguiente');
  previous.id='latestCarouselPrevious';next.id='latestCarouselNext';
  for(const button of [previous,next]){button.type='button';button.setAttribute('aria-controls','dashboardRecent');}
  previous.setAttribute('aria-label','Ver noticias anteriores del carrusel');next.setAttribute('aria-label','Ver siguientes noticias del carrusel');
  controls.append(previous,next);panel.querySelector('.dashboard-panel-head').append(controls);
  const sync=()=>{
    previous.disabled=recent.scrollLeft<=2;
    next.disabled=recent.scrollLeft+recent.clientWidth>=recent.scrollWidth-2;
  };
  const move=direction=>recent.scrollBy({left:direction*(recent.clientWidth+14),behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});
  previous.addEventListener('click',()=>move(-1));next.addEventListener('click',()=>move(1));
  recent.addEventListener('scroll',sync,{passive:true});window.addEventListener('resize',sync);
  if('ResizeObserver' in window)new ResizeObserver(sync).observe(recent);
  recent.addEventListener('keydown',event=>{
    if(event.target!==recent||!['ArrowLeft','ArrowRight'].includes(event.key))return;
    event.preventDefault();move(event.key==='ArrowRight'?1:-1);
  });
  const aside=columns.querySelector('.newsroom-discovery-aside');
  if(aside){
    const tools=document.createElement('section');tools.id='coverageTools';tools.className='coverage-tools';
    tools.setAttribute('aria-label','Cobertura y temas');
    for(const child of aside.children)child.classList.add('home-insight-card');
    aside.querySelector('.radar-panel .dashboard-panel-head').append(mk('span','insight-window','24 h'));
    const secondary=aside.parentElement;
    panel.after(tools);tools.append(aside);
    if(secondary&&!secondary.children.length)secondary.hidden=true;
  }
  function latestCard(item){
    const row=headlineRow(item);row.classList.add('dashboard-latest-card');
    const topic=state.categories.indexOf((item.categories||[])[0]);
    if(topic>=0)row.dataset.topic=String(topic+1);
    const category=mk('span','latest-category',categoryLabel((item.categories||[])[0]||''));
    row.prepend(category);
    const summary=String(item.summary||'').replace(/\s+/g,' ').trim();
    if(state.showSummaries&&summary&&summary!==String(item.title||'').trim()){
      const excerpt=mk('p','latest-summary',summary.length>150?summary.slice(0,147)+'…':summary);
      row.querySelector('.dashboard-recent-title').after(excerpt);
    }
    return row;
  }
  const dashboardBase=renderDashboard;
  renderDashboard=function(...args){
    const result=dashboardBase(...args);
    const items=dashboardEligible(), chosen=[],seenCategories=new Set();
    // Reserve an international slot only among eligible articles.
    for(const prefix of ['03']){
      const story=items.find(item=>(item.categories||[]).some(cat=>cat.startsWith(prefix+' -'))&&!chosen.some(row=>row.id===item.id));
      if(story){chosen.push(story);seenCategories.add((story.categories||[])[0]);}
    }
    for(const item of items){
      const category=(item.categories||[])[0]||'';
      if(chosen.some(row=>row.id===item.id)||seenCategories.has(category))continue;
      chosen.push(item);seenCategories.add(category);
      if(chosen.length>=8)break;
    }
    for(const item of items){
      if(chosen.length>=8)break;
      if(!chosen.some(row=>row.id===item.id))chosen.push(item);
    }
    const feature=$('dashboardFeature');
    panel.hidden=chosen.length<2;
    if(chosen.length){feature.replaceChildren(card(chosen[0]));recent.replaceChildren(...chosen.slice(1).map(latestCard));}
    else{feature.replaceChildren(mk('p','dashboard-empty','No hay noticias con tus preferencias actuales.'));recent.replaceChildren();}
    recent.scrollLeft=0;requestAnimationFrame(sync);
    return result;
  };
  if(state.ready)renderDashboard();
})();
