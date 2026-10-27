"use strict";
/* Small reading aids, keeping the current editorial layout and local preferences. */
(() => {
  const hintKey='radar-card-hint-dismissed';
  const hint=mk('p','card-action-hint');hint.id='cardActionHint';
  hint.append(document.createTextNode('✓ Marcar como leída · 🔖 Guardar · ⋯ Más acciones '));
  const dismiss=mk('button','', 'Entendido');dismiss.id='dismissCardActionHint';dismiss.type='button';
  dismiss.setAttribute('aria-label','Ocultar ayuda de acciones de noticias');
  dismiss.addEventListener('click',()=>{
    try{localStorage.setItem(hintKey,'true');}catch{}
    hint.remove();
  });
  hint.append(dismiss);
  if(storeGet(hintKey)!=='true')document.querySelector('#feedView .section-heading > div')?.append(hint);
  const renderBase=render;
  render=function(...args){
    const result=renderBase(...args);
    hint.hidden=!$('articleGrid')?.querySelector('.article-card');
    return result;
  };
  hint.hidden=!$('articleGrid')?.querySelector('.article-card');

  const figure=$('radarFigure'),layout=figure?.parentElement;
  if(figure&&layout){
    const details=document.createElement('details');details.id='radarMapDetails';details.className='radar-map-details';
    const summary=mk('summary','','Ver mapa de las últimas 24 horas');summary.id='radarMapToggle';
    details.append(summary);figure.before(details);details.append(figure);
    layout.append(details); // Match keyboard order to the visible list-then-map order.
    // Keep the map optional in every viewport; resizing preserves the user's choice.
    details.open=false;
  }
})();
