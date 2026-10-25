"use strict";
/* Homepage headlines remain real articles and follow the reader's source preferences. */
(() => {
  const recent=$('dashboardRecent'),columns=$('newsroomColumns');
  const panel=recent?.closest('.newsroom-lead-latest');
  if(!recent||!panel||!columns)return;
  panel.classList.add('homepage-latest');
  const agenda=$('agendaSection');
  if(agenda)agenda.before(panel);else columns.before(panel);
  $('dashboardRecentTitle').textContent='Últimas noticias';
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
    const tools=document.createElement('details');tools.id='coverageTools';tools.className='coverage-tools';
    tools.append(mk('summary','','Explorar cobertura y tendencias'));
    const secondary=aside.parentElement;
    columns.after(tools);tools.append(aside);
    if(secondary&&!secondary.children.length)secondary.hidden=true;
  }
  function latestCard(item){
    const row=headlineRow(item);row.classList.add('dashboard-latest-card');
    const topic=state.categories.indexOf((item.categories||[])[0]);
    if(topic>=0)row.dataset.topic=String(topic+1);
    const category=mk('span','latest-category',categoryLabel((item.categories||[])[0]||''));
    row.prepend(category);
    if(!state.lite&&state.showImages&&safeURL(item.image)){
      const image=mk('img','latest-news-image');image.src=item.image;image.alt='';image.loading='lazy';image.referrerPolicy='no-referrer';
      image.addEventListener('error',()=>{image.replaceWith(mk('span','latest-photo-note','Sin fotografía disponible'));},{once:true});
      row.prepend(image);
    }else if(!state.lite&&state.showImages)row.prepend(mk('span','latest-photo-note','Sin fotografía disponible'));
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
    if(chosen.length)recent.replaceChildren(...chosen.map(latestCard));
    recent.scrollLeft=0;requestAnimationFrame(sync);
    return result;
  };
  if(state.ready)renderDashboard();
})();
