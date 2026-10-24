/* Reaprovecha la diferencia de altura entre el mosaico y la lista lateral. */
(() => {
  const lead = document.getElementById('newsroomLead');
  const stories = lead?.querySelector('.newsroom-lead-stories');
  const latest = lead?.querySelector('.newsroom-lead-latest');
  const discovery = document.getElementById('newsroomDiscovery');
  const folders = discovery?.querySelector('.newsroom-discovery-categories');
  const sinceVisit = document.getElementById('sinceVisit');
  const saved = document.getElementById('dashboardSavedPanel');
  if (!lead || !stories || !latest || !folders) return;
  let scheduled = false;
  const update = () => {
    scheduled = false;
    const enabled = window.matchMedia('(min-width: 1251px)').matches
      && (sinceVisit?.hidden ?? true) && (saved?.hidden ?? true);
    const difference = enabled
      ? Math.max(0, Math.round(latest.getBoundingClientRect().bottom - stories.getBoundingClientRect().bottom))
      : 0;
    folders.style.setProperty('--lead-free-space', difference + 'px');
  };
  const schedule = () => {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(update);
  };
  if ('ResizeObserver' in window) {
    const observer = new ResizeObserver(schedule);
    observer.observe(stories);
    observer.observe(latest);
  }
  if ('MutationObserver' in window) {
    const observer = new MutationObserver(schedule);
    observer.observe(lead, {childList:true,subtree:true,attributes:true,attributeFilter:['hidden','class']});
    if (sinceVisit) observer.observe(sinceVisit,{attributes:true,attributeFilter:['hidden']});
    if (saved) observer.observe(saved,{attributes:true,attributeFilter:['hidden']});
  }
  window.addEventListener('resize', schedule, {passive:true});
  schedule();
})();
