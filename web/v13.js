"use strict";
/* Radar RSS V1.3: ayuda contextual y estadísticas exclusivamente locales.
   No se recopilan eventos ni se envía telemetría a terceros. */
(() => {
  const GUIDE_KEY='radar-v13-guide-dismissed';
  function seen(){
    try {return localStorage.getItem(GUIDE_KEY)==='true';} catch {return false;}
  }
  function storeSeen(done){
    try {localStorage.setItem(GUIDE_KEY,done?'true':'false');} catch {}
  }
  const root=$('dashboardView');
  const head=root?.querySelector('.dashboard-head');
  if(!head)return;
  const panel=mk('section','v13-guide');
  panel.id='v13Guide';
  panel.setAttribute('aria-labelledby','v13GuideTitle');
  const title=mk('h2','', 'Empieza con Radar RSS');
  title.id='v13GuideTitle';
  const description=mk('p','v13-guide-subtitle',
    'Tres maneras de aprovechar tu lector sin crear una cuenta.');
  const steps=mk('div','v13-guide-actions');
  function addAction(label,hint,callback){
    const button=mk('button','v13-guide-action');
    button.type='button';
    button.append(mk('strong','',label),mk('span','',hint));
    button.addEventListener('click',callback);
    steps.append(button);
  }
  addAction('Ajusta tu portada','Elige tus temas desde Configuración',()=>{
    $('settingsButton')?.click();
    selectedTab('reading');
    const target=$('v12MyRadar');
    target?.scrollIntoView({block:'nearest',behavior:'auto'});
    $('v12MineToggle')?.focus({preventScroll:true});
  });
  addAction('Combina filtros','Selecciona país, medio y antigüedad',()=>{
    goTo('all');
    // El cambio de hash es asíncrono; esperar al evento evita enfocar un control oculto.
    const focus=()=>{$('v12Geo')?.focus({preventScroll:true});};
    if(state.pageView==='feed')focus();
    else window.addEventListener('hashchange',focus,{once:true});
  });
  addAction('Compara titulares','Revisa una noticia contada por varios medios',()=>{
    const item=state.items.find(x=>Array.isArray(x.also_in)&&x.also_in.some(y=>safeURL(y.url)));
    if(item)openArticleReader(item,null,'compare');
    else {goTo('all');actionToast('Busca una noticia con el botón «medios» para comparar.');}
  });
  const dismiss=mk('button','v13-guide-dismiss','Ocultar guía');
  dismiss.type='button';dismiss.id='v13DismissGuide';
  dismiss.addEventListener('click',()=>{
    storeSeen(true);panel.hidden=true;
    open.hidden=false;open.focus({preventScroll:true});
  });
  const footer=mk('div','v13-guide-footer');
  const stats=mk('p','v13-local-stats');
  stats.id='v13LocalStats';
  footer.append(stats,dismiss);
  panel.append(title,description,steps,footer);
  const open=mk('button','v13-reopen','¿Cómo funciona Radar RSS?');
  open.type='button';open.id='v13OpenGuide';
  open.addEventListener('click',()=>{
    storeSeen(false);panel.hidden=false;open.hidden=true;
    panel.scrollIntoView({block:'nearest',behavior:'auto'});
    steps.querySelector('button')?.focus({preventScroll:true});
  });
  // La guía pertenece solo a Inicio, no al panel de configuración.
  head.after(panel);
  head.append(open);
  panel.hidden=seen();
  open.hidden=!panel.hidden;
  function updateStats(){
    if(!stats.isConnected)return;
    const saved=state.saved.size,read=state.read.size;
    stats.textContent=`${saved} guardadas · ${read} marcadas como leídas · Datos solo en este navegador`;
  }
  const previousRender=render;
  render=function(...args){
    previousRender(...args);
    updateStats();
  };
  updateStats();
})();
