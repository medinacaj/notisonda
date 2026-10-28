# Cobertura mundial — Implementation Plan

> Método nativo: superpowers:executing-plans. Mismo checkout/rama feat/cobertura-mundial; una tarea/PR. Autorización persistente para ejecutar recomendaciones/publicar; no nueva ronda de preguntas.

**Goal:** Ampliar regiones y temas en español y destacar historias internacionales recientes con más cobertura editorial real.
**Architecture:** OPML/JSON existentes, evidencia temporal separada; normalización editorial conservadora y selección de Inicio sin rediseño visual ni servicios nuevos.
**Tech Stack:** Python/JSON/XML, JavaScript estático, pruebas offline/Playwright existentes.
**Spec:** docs/superpowers/specs/2026-10-28-world-coverage-design.md.

## Global Constraints
- Base9ad49d369d6e43bd1672db6470473bc386ed6983;276fuentes previas sin cambios/8carpetas, historial y preferencias conservados.
- No nuevas dependencias/cuentas/servicios/workflows; retención45d/5000,12porfeed,3h yAgenda90d intactos.
- RSSobservado no equivale a hechos verificados ni fecha original; no se afirma cobertura universal.
- Ledger /workspace/scratch/world-coverage/progress.md; observaciones de red fuera de tests.

## Review Focus
- Registros previos/IDs/nombres/categorías exactos, intermediarios rotulados, sin duplicados de URL ni conteo doble de un mismo editor.
- RSSGoogle puede contener contexto antiguo/comercial; campos no observados permanecen nulos y el reporte limita lo afirmado.
- Dos secciones o aliases de la misma cabecera cuentan una vez; cabeceras distintas de diferentes países conservan su identidad.
- Portada: coverage válido/recencia24h/desempate; source_ids repetidos, datos no numéricos, historias antiguas/futuras o preferencias no fuerzan prioridad indebida.
- Cero/una/múltiples historias y fuentes ocultas: selección única, lector/rutas/contadores/respaldo conservados; imagen y foco no se degradan.

### Task1 — Catálogo y cobertura documentada
**Files:** sources/feeds.opml, sources/world-coverage-verification.json, web/data/sources.json, tests/test_world_catalog.py, tests/test_new_catalog.py, tests/test_spanish_ai_catalog.py, README.md, docs/project-status.md, docs/fuentes-cobertura-mundial-2026-10-28.md y nota histórica del informeIA.
**Interfaces:** consume parse_opml(Path), audit(Path); produce mismo catálogo y registro temporal sin efecto en runtime. Altas verificadas de portales/temas/regiones, MITes nativo sin retirarRADAR, revalidación de7RSSanteriores.
- [x] Investigar/refinar consultas evitando resultados irrelevantes; registrar límites reales de Google, fechas, hashes y pendientes de política; decidir conjunto final por evidencia.
- [x] RED contratos de nuevas altas/total; GREEN con OPML/JSON/evidencia; adaptar preservación histórica para excluir solo altas nuevas y conservar SHA276d9bf71a2ce407a7757574c815ffc4e783d48041d91dfe9dcaeb6316a4baa1c59.
- [x] Informe con matriz regional/temática, nombres/URLs/tipos/observación; auditoría yPython completo GREEN; commit.

### Task2 — Conteo editorial y prioridad internacional
**Files:** scripts/insights.py, tests/test_insights.py, web/app.js, tests/test_home_priority.cjs, browser_tests/dimension_regressions.py, web/index.html, web/sw.js.
**Interfaces:** independent_publishers conserva set[str] y sus nombres visibles; selectInternationalLead(items:Array,now:number=Date.now())->item|null usa storyTime y una ventana de86400000ms y el coverage entero positivo, nunca longitudsource_ids.
- [x] RED variantes de cabecera/descriptores y MITnativo+RADAR; normalizar solo identidad contada. Cabeceras LaNación de países distintos siguen diferentes y etiquetas públicas intactas. Suite GREEN.
- [x] RED selección: mayor cobertura reciente,24h/desempate, sin coverage válido, source_ids numerosos, antiguas/futuras, sin internacionales; implementar selección mínima y usarla en renderDashboard.
- [x] Regresión real de navegador: noticia internacional relevante vs más nueva poco cubierta, sin duplicado en carrusel y respeto de fuente oculta. Preservar0/1/múltiples casos existentes. Actualizar versiones de shell/caché.
- [x] Python/Node/browser pertinentes GREEN; leer diff y commit.

### Task3 — Revisión y publicación
- [ ] Revisión independiente final del diff contra9ad49d3; corregir hallazgos importantes conRED→GREEN sin re-review innecesario.
- [ ] PR/CI exacto, integrar/publicar según autorización persistente; verificar datos y web pública, árbol local equivalente y limpio.
- [ ] Informar número/canales nuevos, mejora de prioridad y límites: ninguna garantía de0omisiones o veracidad por serRSS.
