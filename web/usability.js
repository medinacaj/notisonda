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

  // El radar permanece visible en Inicio en todos los tamaños de pantalla.
  // No trasladar #radarFigure a un <details>: un desplegable cerrado
  // ocultaba el SVG y la leyenda, incluso con su ficha visible.
})();
