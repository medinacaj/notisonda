"use strict";
/* Sidebar width, Radar RSS V7.6
   One browser-local preference shared by drag handle, keyboard and settings.
   Uses no inline stylesheets, outside services or injected third-party content.
   At <=950px the mobile layout owns the navigation; stored desktop width survives.
*/
(() => {
  const KEY='radar-sidebar-width';
  const DEFAULT_WIDTH=310;
  const MIN_WIDTH=240;
  const MAX_WIDTH=480;
  const BREAKPOINT=950;
  const CONTENT_MIN=540;
  const handle=document.getElementById('sidebarResizeHandle');
  const slider=document.getElementById('settingSidebarWidth');
  const output=document.getElementById('sidebarWidthValue');
  const reset=document.getElementById('resetSidebarWidth');
  const help=document.getElementById('sidebarWidthHelp');
  if(!handle||!slider||!output||!reset)return;

  const fromStorage=()=>{
    try{
      const raw=localStorage.getItem(KEY),n=raw===null?DEFAULT_WIDTH:Number(raw);
      return Number.isFinite(n)&&n>=MIN_WIDTH&&n<=MAX_WIDTH?n:DEFAULT_WIDTH;
    }catch{return DEFAULT_WIDTH;}
  };
  let desiredWidth=fromStorage();
  let active=null;
  const isDesktop=()=>window.innerWidth>BREAKPOINT&&document.body.classList.contains('radar-hybrid');
  const upperBound=()=>Math.max(MIN_WIDTH,Math.min(MAX_WIDTH,window.innerWidth-CONTENT_MIN));
  const clamp=x=>Math.max(MIN_WIDTH,Math.min(upperBound(),Math.round(x)));
  const persist=()=>{
    try{localStorage.setItem(KEY,String(desiredWidth));}catch(error){
      console.warn('No se pudo guardar el ancho lateral de Radar RSS.',error);
    }
  };
  function paint(){
    const desktop=isDesktop();
    const actual=desktop?clamp(desiredWidth):desiredWidth;
    document.documentElement.style.setProperty('--radar-sidebar-width',actual+'px');
    handle.setAttribute('aria-valuemax',String(desktop?upperBound():MAX_WIDTH));
    handle.setAttribute('aria-valuenow',String(actual));
    handle.setAttribute('aria-valuetext',actual+' píxeles');
    slider.max=String(desktop?upperBound():MAX_WIDTH);
    slider.value=String(actual);
    slider.disabled=!desktop;
    handle.tabIndex=desktop&&!document.body.classList.contains('sidebar-collapsed')?0:-1;
    output.textContent=actual+' px';
    help.textContent=desktop
      ?'Ajusta el ancho del panel lateral aquí. El valor se guarda solo en este navegador.'
      :'En pantallas pequeñas el menú se adapta automáticamente; el ancho elegido se conserva para el escritorio.';
  }
  function setWidth(raw,save=true){
    if(!Number.isFinite(Number(raw)))return;
    desiredWidth=clamp(Number(raw));
    paint();
    if(save)persist();
  }
  function resetWidth(){
    desiredWidth=DEFAULT_WIDTH;
    paint();
    try{localStorage.removeItem(KEY);}catch{}
  }
  function stopDrag(commit){
    if(!active)return;
    const old=active;
    active=null;
    document.body.classList.remove('sidebar-is-resizing');
    try{handle.releasePointerCapture(old.pointerId);}catch{}
    if(commit)persist();
    else {desiredWidth=old.previous;paint();}
  }
  handle.addEventListener('pointerdown',event=>{
    if(!isDesktop()||event.button!==0||active)return;
    event.preventDefault();
    active={pointerId:event.pointerId,startX:event.clientX,startWidth:clamp(desiredWidth),previous:desiredWidth};
    try{handle.setPointerCapture(event.pointerId);}catch{}
    document.body.classList.add('sidebar-is-resizing');
  });
  handle.addEventListener('pointermove',event=>{
    if(!active||active.pointerId!==event.pointerId)return;
    setWidth(active.startWidth+(event.clientX-active.startX),false);
  });
  handle.addEventListener('pointerup',event=>{
    if(active?.pointerId===event.pointerId)stopDrag(true);
  });
  handle.addEventListener('pointercancel',event=>{
    if(active?.pointerId===event.pointerId)stopDrag(false);
  });
  handle.addEventListener('lostpointercapture',()=>{if(active)stopDrag(true);});
  handle.addEventListener('dblclick',event=>{if(isDesktop()){event.preventDefault();resetWidth();}});
  handle.addEventListener('keydown',event=>{
    if(!isDesktop())return;
    const step=event.shiftKey?32:16;
    let next=null;
    switch(event.key){
      case 'ArrowLeft':next=clamp(desiredWidth)-step;break;
      case 'ArrowRight':next=clamp(desiredWidth)+step;break;
      case 'Home':next=MIN_WIDTH;break;
      case 'End':next=upperBound();break;
    }
    if(next!==null){event.preventDefault();setWidth(next);}
  });
  slider.addEventListener('input',()=>{if(isDesktop())setWidth(slider.value);});
  reset.addEventListener('click',resetWidth);
  window.addEventListener('resize',()=>{if(active)stopDrag(true);paint();},{passive:true});
  window.addEventListener('storage',event=>{if(event.key===KEY){desiredWidth=fromStorage();paint();}});
  window.addEventListener('radar-sidebar-visibility-change',paint);
  window.addEventListener('radar-sidebar-pref-sync',()=>{desiredWidth=fromStorage();paint();});
  paint();
})();
