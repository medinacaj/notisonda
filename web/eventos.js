"use strict";
/* Radar RSS · Eventos: agenda pública del Biobío y del resto de Chile.
   Integra el antiguo proyecto eventos-biobio como una sección estática más.
   Lee data/eventos.json (lo genera eventos/publicar_web.py), arma el DOM con
   nodos de texto (nunca cadenas HTML) y guarda los favoritos solo en este navegador. */
(() => {
  const view = $('eventsView');
  if (!view) return;
  VECTOR_PATHS.calendar = '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>';

  const SAVED_KEY = 'radar-eventos-guardados';
  const MONTH_FMT = new Intl.DateTimeFormat('es-CL', { month: 'long', year: 'numeric' });
  const DAY_FMT = new Intl.DateTimeFormat('es-CL', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
  const SHORT_FMT = new Intl.DateTimeFormat('es-CL', { weekday: 'short', day: 'numeric', month: 'short' });
  const STAMP_FMT = new Intl.DateTimeFormat('es-CL', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
  const WEEKDAYS = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
  const FIELD_LABELS = { title: 'Título', date: 'Fecha', end_date: 'Fecha de término', time: 'Horario',
    venue: 'Lugar', price_value: 'Precio', price_status: 'Estado del precio', status: 'Estado' };

  const ev = { data: null, loading: null, scope: 'biobio', view: 'agenda', calMonth: null, calSelected: null,
    filters: { q: '', place: '', category: '', price: '', from: '', to: '' }, active: null };

  const iso = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  const todayISO = () => iso(new Date());
  const parseISO = s => { const [y, m, d] = String(s).split('-').map(Number); return new Date(y, m - 1, d); };
  const cap = s => s.charAt(0).toUpperCase() + s.slice(1);
  const fmtDay = s => cap(DAY_FMT.format(parseISO(s)));
  const fmtShort = s => cap(SHORT_FMT.format(parseISO(s)));
  const lastDay = e => e.end_date && e.end_date > e.date ? e.end_date : e.date;
  ev.filters.from = todayISO();

  /* ---------- Guardados (solo este navegador) ---------- */
  function readSaved() {
    try { const data = JSON.parse(localStorage.getItem(SAVED_KEY) || '{}'); return data && typeof data === 'object' ? data : {}; }
    catch { return {}; }
  }
  function writeSaved(data) { try { localStorage.setItem(SAVED_KEY, JSON.stringify(data)); } catch { /* modo privado */ } }
  const isSaved = id => Boolean(readSaved()[id]);
  function toggleSaved(item) {
    const data = readSaved();
    if (data[item.id]) delete data[item.id];
    else data[item.id] = { id: item.id, title: item.title, date: item.date, scope: item.scope, saved_at: new Date().toISOString() };
    writeSaved(data);
    updateCounts();
    return Boolean(data[item.id]);
  }

  /* ---------- Datos ---------- */
  function load() {
    if (ev.loading) return ev.loading;
    ev.loading = fetch('./data/eventos.json', { cache: 'no-cache' })
      .then(res => { if (!res.ok) throw new Error('HTTP ' + res.status); return res.json(); })
      .then(data => {
        if (!data || !Array.isArray(data.events)) throw new Error('formato no válido');
        ev.data = data;
        fillPlaces(); updateCounts(); renderAll(); buildNav();
      })
      .catch(() => {
        ev.data = { events: [], scopes: {}, communes: {} };
        $('eventsStatus').textContent = 'Aún no hay eventos publicados o no se pudieron cargar. Vuelve a intentarlo más tarde.';
        renderAll();
      });
    return ev.loading;
  }
  const events = () => (ev.data?.events || []).filter(e => e.scope === ev.scope);

  function matches(e, { ignoreDates = false, ignorePlace = false } = {}) {
    const f = ev.filters;
    if (!ignorePlace && f.place && (ev.scope === 'biobio' ? e.commune : e.region) !== f.place) return false;
    if (f.category && e.category !== f.category) return false;
    if (f.price && (e.price_status || 'pending') !== f.price) return false;
    if (!ignoreDates) {
      if (f.from && lastDay(e) < f.from) return false;
      if (f.to && e.date > f.to) return false;
    }
    if (f.q) {
      const hay = stripAccents([e.title, e.venue, e.commune, e.region, e.source, e.description].filter(Boolean).join(' '));
      if (!stripAccents(f.q).split(/\s+/).filter(Boolean).every(w => hay.includes(w))) return false;
    }
    return true;
  }
  const filtered = () => events().filter(e => matches(e));

  /* ---------- Piezas de la interfaz ---------- */
  function price(e) {
    if (e.price_status === 'free') return 'Gratis';
    if (e.price_status === 'paid') return e.price_value != null ? `Desde $${Number(e.price_value).toLocaleString('es-CL')}` : 'Pagado (monto por confirmar)';
    return 'Precio por confirmar';
  }
  function badges(e) {
    const box = mk('div', 'event-badges');
    const add = (cls, text, title) => { const b = mk('span', 'event-badge ' + cls, text); if (title) b.title = title; box.append(b); };
    if (e.category) add('cat', e.category);
    if (e.official) add('official', 'Oficial', 'Publicado por el organizador o una institución oficial');
    if (e.price_status === 'free') add('free', 'Gratis');
    if (e.status === 'Cancelado') add('cancelled', 'Cancelado');
    else if (e.status && e.status !== 'Confirmado') add('pending', e.status, 'La fuente no publicó todos los datos: confirma con el organizador');
    if (e.origin === 'seed') add('seed', 'Verificado a mano', 'Evento semilla comprobado manualmente por búsqueda web');
    if (e.changed_at && (Date.now() - new Date(e.changed_at)) / 864e5 < 7) add('updated', 'Actualizado');
    return box;
  }
  function placeText(e) {
    return [e.venue, e.commune, ev.scope === 'nacional' ? e.region : null].filter(Boolean).join(' · ') || 'Lugar por confirmar';
  }
  function saveButton(e) {
    const on = isSaved(e.id);
    const b = mk('button', 'event-save', on ? '★' : '☆');
    b.type = 'button';
    b.setAttribute('aria-pressed', String(on));
    b.setAttribute('aria-label', (on ? 'Quitar de guardados: ' : 'Guardar evento: ') + e.title);
    b.title = on ? 'Quitar de guardados' : 'Guardar';
    b.addEventListener('click', () => {
      const now = toggleSaved(e);
      b.textContent = now ? '★' : '☆';
      b.setAttribute('aria-pressed', String(now));
      b.setAttribute('aria-label', (now ? 'Quitar de guardados: ' : 'Guardar evento: ') + e.title);
      if (ev.view === 'saved') renderSaved();
    });
    return b;
  }
  function row(e, groupDay) {
    const item = mk('article', 'event-row' + (e.status === 'Cancelado' ? ' is-cancelled' : ''));
    item.dataset.eventId = e.id;
    const time = mk('div', 'event-time');
    time.append(mk('strong', '', e.time || '—'), mk('small', '', e.time ? (e.end_time ? 'a ' + e.end_time : '') : 'Hora por confirmar'));
    const body = mk('div', 'event-body');
    const open = mk('button', 'event-open', e.title);
    open.type = 'button';
    open.addEventListener('click', () => openEvent(e));
    const meta = [placeText(e)];
    if (groupDay && e.date < groupDay) meta.push('En curso desde ' + fmtShort(e.date));
    if (e.end_date && e.end_date !== e.date) meta.push('hasta ' + fmtShort(e.end_date));
    body.append(mk('h3', 'event-title'), mk('p', 'event-meta', meta.join(' · ')), badges(e), mk('p', 'event-source', e.source || ''));
    body.firstChild.append(open);
    item.append(time, body, saveButton(e));
    return item;
  }
  function empty(text) { return mk('p', 'events-empty', text); }
  function listByDay(list, from) {
    const frag = document.createDocumentFragment();
    const groups = new Map();
    for (const e of list) {
      const day = from && e.date < from ? from : e.date; // un evento en curso aparece desde hoy
      if (!groups.has(day)) groups.set(day, []);
      groups.get(day).push(e);
    }
    for (const day of [...groups.keys()].sort()) {
      const group = mk('section', 'event-day');
      const items = groups.get(day);
      const head = mk('h2', 'event-day-head');
      head.append(mk('span', '', fmtDay(day)), mk('span', 'event-day-count', `${items.length} evento${items.length === 1 ? '' : 's'}`));
      group.append(head, ...items.map(e => row(e, day)));
      frag.append(group);
    }
    return frag;
  }

  /* ---------- Vistas ---------- */
  function renderAgenda() {
    const list = filtered();
    $('eventsCount').textContent = `${format.format(list.length)} evento${list.length === 1 ? '' : 's'} con estos filtros`;
    const root = $('eventsAgenda');
    root.replaceChildren(list.length ? listByDay(list, ev.filters.from) :
      empty(events().length ? 'No hay eventos con estos filtros. Amplía las fechas o quita filtros.' :
        'Todavía no hay eventos publicados para esta zona.'));
  }
  function renderCalendar() {
    if (!ev.calMonth) { const t = new Date(); ev.calMonth = new Date(t.getFullYear(), t.getMonth(), 1); }
    const m = ev.calMonth;
    const first = new Date(m.getFullYear(), m.getMonth(), 1), last = new Date(m.getFullYear(), m.getMonth() + 1, 0);
    $('eventsCalTitle').textContent = cap(MONTH_FMT.format(first));
    const month = events().filter(e => matches(e, { ignoreDates: true }) && lastDay(e) >= iso(first) && e.date <= iso(last));
    const counts = {};
    for (const e of month) {
      const d = e.date < iso(first) ? new Date(first) : parseISO(e.date);
      for (; iso(d) <= lastDay(e) && d <= last; d.setDate(d.getDate() + 1)) counts[iso(d)] = (counts[iso(d)] || 0) + 1;
    }
    const grid = $('eventsCalGrid');
    grid.replaceChildren(...WEEKDAYS.map(w => mk('span', 'events-cal-head', w)));
    const offset = (first.getDay() + 6) % 7;
    for (let i = 0; i < offset; i++) grid.append(mk('span', 'events-cal-blank'));
    const today = todayISO();
    for (let day = 1; day <= last.getDate(); day++) {
      const key = iso(new Date(m.getFullYear(), m.getMonth(), day));
      const n = counts[key] || 0;
      const b = mk('button', 'events-cal-day' + (key === today ? ' is-today' : '') + (key === ev.calSelected ? ' is-selected' : '') + (n ? ' has-events' : ''));
      b.type = 'button';
      b.setAttribute('aria-label', `${fmtDay(key)}: ${n} evento${n === 1 ? '' : 's'}`);
      b.setAttribute('aria-pressed', String(key === ev.calSelected));
      b.append(mk('span', 'events-cal-num', String(day)));
      if (n) b.append(mk('span', 'events-cal-count', String(n)));
      b.addEventListener('click', () => { ev.calSelected = key; renderCalendar(); });
      grid.append(b);
    }
    const dayRoot = $('eventsCalDay');
    if (!ev.calSelected) { dayRoot.replaceChildren(empty('Elige un día para ver sus eventos.')); return; }
    const sel = ev.calSelected;
    const list = month.filter(e => e.date <= sel && lastDay(e) >= sel);
    dayRoot.replaceChildren(list.length ? listByDay(list, sel) : empty('No hay eventos cargados para este día.'));
  }
  function placeNames() {
    if (ev.scope === 'biobio') return (ev.data?.communes?.biobio || []).map(c => c.name);
    return [...new Set(events().map(e => e.region).filter(Boolean))].sort((a, b) => a.localeCompare(b, 'es'));
  }
  function renderPlaces() {
    const counts = {};
    for (const e of events()) if (matches(e, { ignorePlace: true })) {
      const key = ev.scope === 'biobio' ? e.commune : e.region;
      counts[key] = (counts[key] || 0) + 1;
    }
    const names = placeNames();
    const grid = mk('div', 'events-places-grid');
    for (const name of names.sort((a, b) => (counts[b] || 0) - (counts[a] || 0) || a.localeCompare(b, 'es'))) {
      const n = counts[name] || 0;
      const b = mk('button', 'events-place' + (n ? '' : ' is-empty'));
      b.type = 'button';
      b.append(mk('strong', '', name), mk('span', '', n ? `${n} evento${n === 1 ? '' : 's'}` : 'Sin eventos cargados'));
      b.addEventListener('click', () => { ev.filters.place = name; $('eventsPlace').value = name; setView('agenda'); });
      grid.append(b);
    }
    const intro = mk('p', 'events-places-intro', ev.scope === 'biobio' ?
      'Las 33 comunas de la Región del Biobío. «Sin eventos cargados» significa que ninguna fuente publicó eventos vigentes, no que no existan.' :
      'Regiones con eventos publicados por las fuentes nacionales.');
    $('eventsPlaces').replaceChildren(intro, names.length ? grid : empty('Todavía no hay datos.'));
    $('eventsCount').textContent = '';
  }
  function renderSaved() {
    const saved = Object.values(readSaved()).sort((a, b) => String(a.date).localeCompare(String(b.date)));
    const byId = new Map((ev.data?.events || []).map(e => [e.id, e]));
    $('eventsCount').textContent = `${saved.length} evento${saved.length === 1 ? '' : 's'} guardado${saved.length === 1 ? '' : 's'}`;
    if (!saved.length) { $('eventsSaved').replaceChildren(empty('Aún no guardas eventos. Usa ☆ en la agenda.')); return; }
    const live = saved.map(s => byId.get(s.id)).filter(Boolean);
    const gone = saved.filter(s => !byId.has(s.id));
    const frag = document.createDocumentFragment();
    if (live.length) frag.append(listByDay(live));
    if (gone.length) {
      const old = mk('section', 'event-day');
      old.append(mk('h2', 'event-day-head', 'Ya no están en la agenda'));
      for (const s of gone) {
        const item = mk('div', 'event-row is-gone');
        const remove = mk('button', 'events-reset', 'Quitar');
        remove.type = 'button';
        remove.addEventListener('click', () => { const d = readSaved(); delete d[s.id]; writeSaved(d); updateCounts(); renderSaved(); });
        item.append(mk('div', 'event-time', s.date ? fmtShort(s.date) : ''), mk('p', 'event-title', s.title || 'Evento'), remove);
        old.append(item);
      }
      frag.append(old);
    }
    $('eventsSaved').replaceChildren(frag);
  }
  function renderAll() {
    if (!ev.data) return;
    renderStatus();
    const panels = { agenda: 'eventsAgenda', calendar: 'eventsCalendar', places: 'eventsPlaces', saved: 'eventsSaved' };
    for (const [name, id] of Object.entries(panels)) $(id).hidden = name !== ev.view;
    $('eventsFilters').hidden = ev.view === 'saved';
    if (ev.view === 'agenda') renderAgenda();
    else if (ev.view === 'calendar') { renderCalendar(); $('eventsCount').textContent = ''; }
    else if (ev.view === 'places') renderPlaces();
    else renderSaved();
  }
  function renderStatus() {
    const info = ev.data?.scopes?.[ev.scope];
    if (!info || !info.generated_at) {
      $('eventsStatus').textContent = 'Todavía no hay un rastreo publicado para esta zona.';
      return;
    }
    const when = STAMP_FMT.format(new Date(info.generated_at));
    $('eventsStatus').textContent = `Último rastreo: ${when} · respondieron ${info.sources_ok ?? '—'} de ${info.sources_attempted ?? '—'} fuentes · ${info.events ?? 0} eventos vigentes`;
  }
  function updateCounts() {
    const all = ev.data?.events || [];
    $('eventsCountBiobio').textContent = String(all.filter(e => e.scope === 'biobio').length);
    $('eventsCountNacional').textContent = String(all.filter(e => e.scope === 'nacional').length);
    $('eventsSavedCount').textContent = String(Object.keys(readSaved()).length);
  }
  function fillPlaces() {
    const select = $('eventsPlace');
    select.replaceChildren(new Option(ev.scope === 'biobio' ? 'Todas las comunas' : 'Todas las regiones', ''));
    $('eventsPlaceLabel').textContent = ev.scope === 'biobio' ? 'Comuna' : 'Región';
    if (ev.scope === 'biobio') {
      const byProv = new Map();
      for (const c of ev.data?.communes?.biobio || []) {
        if (!byProv.has(c.province)) byProv.set(c.province, []);
        byProv.get(c.province).push(c.name);
      }
      for (const [prov, names] of byProv) {
        const group = document.createElement('optgroup');
        group.label = 'Provincia de ' + prov;
        names.forEach(n => group.append(new Option(n, n)));
        select.append(group);
      }
    } else {
      placeNames().forEach(n => select.append(new Option(n, n)));
    }
    if (![...select.options].some(o => o.value === ev.filters.place)) ev.filters.place = '';
    select.value = ev.filters.place;
  }
  function setView(name) {
    ev.view = name;
    view.querySelectorAll('.events-tab').forEach(t => {
      const on = t.dataset.eventsView === name;
      t.classList.toggle('active', on);
      t.setAttribute('aria-current', on ? 'page' : 'false');
    });
    renderAll();
  }
  function setScope(scope) {
    ev.scope = scope === 'nacional' ? 'nacional' : 'biobio';
    view.querySelectorAll('.events-scope-btn').forEach(b => {
      const on = b.dataset.scope === ev.scope;
      b.classList.toggle('active', on);
      b.setAttribute('aria-pressed', String(on));
    });
    ev.filters.place = '';
    view.querySelector('[data-events-view="places"]').textContent = ev.scope === 'biobio' ? 'Por comuna' : 'Por región';
    if (ev.data) fillPlaces();
    renderAll();
  }

  /* ---------- Ficha del evento ---------- */
  function openEvent(e) {
    ev.active = e;
    const dlg = $('eventDialog');
    $('eventDialogKicker').textContent = fmtDay(e.date) + (e.end_date && e.end_date !== e.date ? ' al ' + fmtDay(e.end_date) : '');
    $('eventDialogTitle').textContent = e.title;
    $('eventDialogBadges').replaceWith(Object.assign(badges(e), { id: 'eventDialogBadges' }));
    const body = $('eventDialogBody');
    const facts = mk('dl', 'event-facts');
    const fact = (label, value) => { if (value) facts.append(mk('dt', '', label), mk('dd', '', value)); };
    fact('Horario', e.time ? e.time + (e.end_time ? ' a ' + e.end_time : '') : 'Por confirmar');
    fact('Lugar', e.venue || 'Por confirmar');
    fact('Dirección', e.address);
    fact('Comuna', [e.commune, e.province ? 'Provincia de ' + e.province : null, e.region ? 'Región ' + e.region : null].filter(Boolean).join(' · '));
    fact('Precio', price(e));
    fact('Acceso', e.access);
    fact('Público', e.audience);
    fact('Estado', e.status);
    fact('Origen', e.origin === 'seed' ? 'Verificado manualmente por búsqueda web' : 'Rastreo automático de ' + (e.source || 'la fuente'));
    const parts = [facts];
    if (safeURL(e.image_url) && state.showImages && !state.lite) {
      const img = document.createElement('img');
      img.src = e.image_url; img.alt = ''; img.loading = 'lazy'; img.referrerPolicy = 'no-referrer'; img.className = 'event-image';
      img.addEventListener('error', () => img.remove(), { once: true });
      parts.unshift(img);
    }
    if (e.description) parts.push(mk('p', 'event-description', e.description));
    parts.push(mk('h3', '', 'Fuentes'));
    const sources = mk('ul', 'event-sources');
    for (const s of e.sources?.length ? e.sources : [{ name: e.source, url: e.source_url }]) {
      const li = mk('li');
      if (safeURL(s.url)) li.append(link(s.url, s.name || s.url)); else li.textContent = s.name || 'Fuente sin enlace';
      sources.append(li);
    }
    parts.push(sources);
    if (e.changes?.length) {
      parts.push(mk('h3', '', 'Historial de cambios'));
      const hist = mk('ul', 'event-history');
      for (const c of e.changes) hist.append(mk('li', '', `${FIELD_LABELS[c.field] || c.field}: ${c.old_value ?? '—'} → ${c.new_value ?? '—'} (${(c.changed_at || '').slice(0, 10)})`));
      parts.push(hist);
    }
    parts.push(mk('p', 'event-disclaimer', 'Datos tomados de la fuente citada, sin completarse a mano. Confirma horario, lugar y precio con el organizador.'));
    body.replaceChildren(...parts);
    $('eventSave').textContent = isSaved(e.id) ? '★ Guardado' : '☆ Guardar';
    const source = $('eventSource');
    source.hidden = !safeURL(e.source_url);
    source.href = safeURL(e.source_url) || '#';
    if (!dlg.open) dlg.showModal();
  }
  function icsEscape(s) { return String(s || '').replace(/[\\;,]/g, c => '\\' + c).replace(/\n/g, '\\n'); }
  function downloadICS(e) {
    const d = e.date.replace(/-/g, '');
    let start, end;
    if (e.time) {
      start = `DTSTART:${d}T${e.time.replace(':', '')}00`;
      end = e.end_time ? `DTEND:${d}T${e.end_time.replace(':', '')}00` : '';
    } else {
      const after = parseISO(lastDay(e)); after.setDate(after.getDate() + 1);
      start = `DTSTART;VALUE=DATE:${d}`;
      end = `DTEND;VALUE=DATE:${iso(after).replace(/-/g, '')}`;
    }
    const lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Radar RSS//Eventos//ES', 'BEGIN:VEVENT',
      `UID:evento-${e.id}@radar-rss`, `DTSTAMP:${new Date().toISOString().replace(/[-:]/g, '').slice(0, 15)}Z`,
      start, end, `SUMMARY:${icsEscape(e.title)}`, `LOCATION:${icsEscape([e.venue, e.commune].filter(Boolean).join(', '))}`,
      `DESCRIPTION:${icsEscape((e.description || '') + (e.source_url ? '\nFuente: ' + e.source_url : ''))}`,
      'END:VEVENT', 'END:VCALENDAR'].filter(Boolean);
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([lines.join('\r\n')], { type: 'text/calendar' }));
    a.download = `evento-${e.id}.ics`;
    document.body.append(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  }
  async function shareEvent(e) {
    const text = `${e.title} — ${fmtDay(e.date)}${e.time ? ' ' + e.time : ''}, ${e.commune || ''}`;
    const url = safeURL(e.source_url) || location.href;
    try {
      if (navigator.share) { await navigator.share({ title: e.title, text, url }); return; }
      await navigator.clipboard.writeText(`${text}\n${url}`);
      actionToast('Evento copiado al portapapeles.');
    } catch { /* el usuario canceló o el navegador lo impidió */ }
  }

  /* ---------- Integración con la navegación de Radar ---------- */
  function onEvents() {
    const hash = decodeURIComponent(location.hash.slice(1));
    return hash === 'eventos' || hash.startsWith('eventos/');
  }
  const baseGoTo = goTo;
  goTo = function (target, ...rest) {
    if (target === 'events') { if (location.hash === '#eventos') navigateFromHash(); else location.hash = '#eventos'; return; }
    return baseGoTo(target, ...rest);
  };
  const baseNavigate = navigateFromHash;
  navigateFromHash = function (...args) {
    const active = onEvents();
    if (active) state.pageView = 'events';
    baseNavigate(...args);
    view.hidden = !active;
    document.body.classList.toggle('on-events', active);
    if (!active) return;
    const scope = decodeURIComponent(location.hash.slice(1)).split('/')[1];
    if (scope && scope !== ev.scope) setScope(scope);
    state.pageView = 'events';
    $('dashboardView').hidden = true; $('feedView').hidden = true; $('briefingView').hidden = true;
    document.body.classList.remove('on-dashboard', 'on-briefing');
    $('topbarSection').textContent = 'Eventos';
    buildNav();
    load();
  };
  const baseBuildNav = buildNav;
  buildNav = function (...args) {
    baseBuildNav(...args);
    const nav = $('categoryNav');
    const active = state.pageView === 'events';
    const button = mk('button', 'nav-link nav-events' + (active ? ' active' : ''));
    button.type = 'button';
    button.title = 'Eventos';
    button.setAttribute('aria-current', active ? 'page' : 'false');
    const left = mk('span', 'nav-left'), glyph = mk('span', 'nav-glyph');
    glyph.append(svgIcon('calendar'));
    left.append(glyph, mk('span', 'nav-label', 'Eventos'));
    button.append(left, mk('span', 'nav-count', ev.data ? String(ev.data.events.length) : ''));
    button.addEventListener('click', () => goTo('events'));
    const core = nav.querySelectorAll(':scope > .nav-link');
    if (core[1]) core[1].after(button); else nav.append(button);
    if (active) nav.querySelectorAll(':scope > .nav-link:not(.nav-events)').forEach(n => { n.classList.remove('active'); n.setAttribute('aria-current', 'false'); });
  };
  const baseRail = renderTopicRail;
  renderTopicRail = function (...args) {
    baseRail(...args);
    const rail = $('topicRail');
    const active = state.pageView === 'events';
    const chip = mk('button', 'topic-chip events-chip' + (active ? ' active' : ''), 'Eventos');
    chip.type = 'button';
    chip.setAttribute('aria-current', active ? 'page' : 'false');
    chip.addEventListener('click', () => goTo('events'));
    const chips = rail.querySelectorAll('.topic-chip');
    if (chips[2]) chips[2].after(chip); else rail.append(chip);
    if (active) {
      rail.querySelectorAll('.topic-chip:not(.events-chip)').forEach(c => { c.classList.remove('active'); c.setAttribute('aria-current', 'false'); });
      requestAnimationFrame(() => { rail.scrollLeft = Math.max(0, chip.offsetLeft - rail.offsetLeft - 16); });
    }
  };

  /* ---------- Eventos de la interfaz ---------- */
  view.querySelectorAll('.events-scope-btn').forEach(b => b.addEventListener('click', () => setScope(b.dataset.scope)));
  view.querySelectorAll('.events-tab').forEach(t => t.addEventListener('click', () => setView(t.dataset.eventsView)));
  const form = $('eventsFilters');
  let typing = null;
  const bind = (id, key, eventName = 'change') => $(id).addEventListener(eventName, e => {
    ev.filters[key] = e.target.value;
    clearTimeout(typing);
    typing = setTimeout(renderAll, eventName === 'input' ? 200 : 0);
  });
  bind('eventsQuery', 'q', 'input'); bind('eventsPlace', 'place'); bind('eventsCategory', 'category');
  bind('eventsPrice', 'price'); bind('eventsFrom', 'from'); bind('eventsTo', 'to');
  $('eventsFrom').value = ev.filters.from;
  form.addEventListener('submit', e => e.preventDefault());
  form.addEventListener('reset', e => {
    e.preventDefault();
    ev.filters = { q: '', place: '', category: '', price: '', from: todayISO(), to: '' };
    $('eventsQuery').value = ''; $('eventsPlace').value = ''; $('eventsCategory').value = '';
    $('eventsPrice').value = ''; $('eventsFrom').value = ev.filters.from; $('eventsTo').value = '';
    renderAll();
  });
  $('eventsCalPrev').addEventListener('click', () => { const m = ev.calMonth; ev.calMonth = new Date(m.getFullYear(), m.getMonth() - 1, 1); ev.calSelected = null; renderCalendar(); });
  $('eventsCalNext').addEventListener('click', () => { const m = ev.calMonth; ev.calMonth = new Date(m.getFullYear(), m.getMonth() + 1, 1); ev.calSelected = null; renderCalendar(); });
  $('eventsCalToday').addEventListener('click', () => { const t = new Date(); ev.calMonth = new Date(t.getFullYear(), t.getMonth(), 1); ev.calSelected = todayISO(); renderCalendar(); });
  const dlg = $('eventDialog');
  $('eventDialogClose').addEventListener('click', () => dlg.close());
  dlg.addEventListener('click', e => { if (e.target === dlg) dlg.close(); });
  $('eventSave').addEventListener('click', () => {
    if (!ev.active) return;
    const on = toggleSaved(ev.active);
    $('eventSave').textContent = on ? '★ Guardado' : '☆ Guardar';
    renderAll();
  });
  $('eventIcs').addEventListener('click', () => { if (ev.active) downloadICS(ev.active); });
  $('eventShare').addEventListener('click', () => { if (ev.active) void shareEvent(ev.active); });

  updateCounts();
  if (onEvents()) navigateFromHash(); else buildNav();
  // Contador del menú sin bloquear la portada: se carga cuando el navegador queda libre.
  (window.requestIdleCallback || (fn => setTimeout(fn, 1500)))(() => load());
})();
