# Estado del proyecto — Radar RSS

Última actualización editorial: 2026-10-18.

## Estado operativo
- Versión pública: https://medinacaj.github.io/radar-rss-publico/
- Rama estable y publicación: `main` + `.github/workflows/deploy.yml`.
- Calidad Python/Node: `.github/workflows/ci.yml`.
- Navegadores: `.github/workflows/responsive.yml` (Chromium, Firefox, WebKit; siete anchos).
- Alertas: `.github/workflows/monitor.yml` (issue única, cierre al recuperarse).
- Historial: hasta 5.000 noticias; ventana máxima 45 días y almacenamiento no permanente.
- Tendencias: mínimo cuatro medios independientes.
- **V1.2 interactiva:** navegación Latinoamérica unificada visualmente y con filtros por país, Mi Radar para elegir categorías, búsqueda guardada y filtros cruzados, comparador cronológico, boletín personalizable.
- **Privacidad V1.2:** preferencias y búsquedas guardadas solo en este navegador; no hay perfiles ni sincronización.
- **Pruebas V1.2:** suite Python/Node y recorrido E2E en Chromium, Firefox y WebKit, siete anchos incluidos 320 px.
- **V1.3 — calidad UX:** guía no invasiva y reabrible, estadísticas de lectura únicamente locales; sin analítica central ni seguimiento.
- **V1.3 — rendimiento:** ningún listado oculto en portada/resumen; descargas históricas limitadas a tres simultáneas.
- **V1.3 — editorial:** informe orientativo en Actions sobre calidad de fuentes y coincidencias de titulares, sin bajas automáticas.
- **V1.3 — recuperación:** artefactos JSON públicos de Actions con retención de hasta 90 días y recuperación manual validada.

## Fuente de verdad
- [Issues](https://github.com/medinacaj/radar-rss-publico/issues): incidencias sin resolver.
- [Pull requests](https://github.com/medinacaj/radar-rss-publico/pulls): cambios en revisión.
- [Actions](https://github.com/medinacaj/radar-rss-publico/actions): evidencia de pruebas y despliegue.
- `docs/decisions.md`: decisiones técnicas duraderas.

## Limitaciones reconocidas
WebKit automatizado no certifica Safari en hardware iOS. La prueba de accesibilidad automatizada no sustituye pruebas con lectores de pantalla reales. Una base de datos sería necesaria para garantizar historial permanente o sincronización entre dispositivos.
