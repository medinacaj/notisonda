"use strict";
/* Homepage headlines remain real articles and follow the reader's source preferences. */
(() => {
  const recent=$('dashboardRecent');
  const panel=recent?.closest('.newsroom-lead-latest');
  if(!recent||!panel)return;
  panel.classList.add('homepage-latest');
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
  // HTML already owns the order; rendering only replaces the carousel's items.
  if('MutationObserver' in window)new MutationObserver(()=>{
    recent.scrollLeft=0;requestAnimationFrame(sync);
  }).observe(recent,{childList:true});
  requestAnimationFrame(sync);
})();
