"use strict";
/* Radar RSS — feedback on newly PUBLISHED stories only.
   No network requests, polling, long-running animations or artificial numbers. */
(() => {
  const timers=new WeakMap();
  const findCounts=items=>{
    const countByFolder=new Map();
    for(const row of document.querySelectorAll('#libraryFolderNav .folder-entry')){
      let sourceIds=[];
      try{
        const decoded=JSON.parse(row.dataset.radarSourceIds||'[]');
        if(Array.isArray(decoded))sourceIds=decoded;
      }catch{}
      if(!sourceIds.length)continue;
      const sources=new Set(sourceIds);
      const count=items.filter(item=>Array.isArray(item.source_ids)&&item.source_ids.some(id=>sources.has(id))).length;
      if(count)countByFolder.set(row,count);
    }
    return countByFolder;
  };
  function decorate(element,kind,count,ttl){
    if(!element||!count)return;
    const current=timers.get(element);
    if(current)window.clearTimeout(current);
    element.classList.remove(kind);
    // Restart a single 1.8s animation on a subsequent real publication.
    void element.offsetWidth;
    element.dataset.radarNew='+'+count;
    element.classList.add(kind);
    const timer=window.setTimeout(()=>{
      element.classList.remove(kind);
      delete element.dataset.radarNew;
      timers.delete(element);
    },ttl);
    timers.set(element,timer);
  }
  function displayNewsEffect(event){
    const items=event.detail?.items;
    if(!Array.isArray(items)||!items.length)return;
    const prefersReducedMotion=window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
    if(prefersReducedMotion)return;
    const ids=new Set(items.map(item=>item.id).filter(Boolean));
    let index=0;
    for(const node of document.querySelectorAll('.article-card[data-article-id]')){
      if(!ids.has(node.dataset.articleId))continue;
      if(index++>=10)break;
      node.style.setProperty('--radar-news-delay',Math.min(index*65,390)+'ms');
      decorate(node,'radar-news-arrived',1,2100);
    }
    for(const [row,count] of findCounts(items)){
      decorate(row,'radar-folder-arrived',count,2300);
    }
    const all=document.querySelector('#categoryNav > .nav-link:nth-child(2)');
    decorate(all,'radar-all-arrived',items.length,1900);
    const header=document.getElementById('refreshCycle');
    decorate(header,'radar-refresh-arrived',1,1400);
  }
  window.addEventListener('radar:news-added',displayNewsEffect);
})();
