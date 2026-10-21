# Estado del proyecto — Radar RSS

Última actualización editorial: 2026-10-21.

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

- **Frecuencia programada:** cada tres horas UTC (GitHub Actions puede demorar la ejecución); antes era cada seis horas.

## Fuente de verdad
- [Issues](https://github.com/medinacaj/radar-rss-publico/issues): incidencias sin resolver.
- [Pull requests](https://github.com/medinacaj/radar-rss-publico/pulls): cambios en revisión.
- [Actions](https://github.com/medinacaj/radar-rss-publico/actions): evidencia de pruebas y despliegue.
- `docs/decisions.md`: decisiones técnicas duraderas.

## Plan de estabilización posterior a la auditoría (2026-10-21)
- P0: estudiar respaldo durable externo y restauración verificable; no eliminar recuperación actual hasta demostrar equivalencia.
- P1: consolidar progresivamente estilos V9–V11.1 sin alterar navegación, seis carpetas ni controles de lectura; establecer pruebas de regresión visual con datos representativos.
- P1: validar integridad del historial y detección de feeds obsoletos; medir cobertura efectiva de los 178 feeds y dependencia de Google Noticias.
- P1: resolver validación física pendiente (issue #31) y curación editorial (issue #32); no declarar completadas pruebas físicas sin dispositivos.
- P2: optimizar tamaño de CSS/JS y renderizado mediante mediciones antes/después.
- Criterio de aceptación: CI y pruebas responsivas verdes, despliegue y monitor correctos, y ausencia de regresiones de navegación.

## Limitaciones reconocidas
WebKit automatizado no certifica Safari en hardware iOS. La prueba de accesibilidad automatizada no sustituye pruebas con lectores de pantalla reales. Una base de datos sería necesaria para garantizar historial permanente o sincronización entre dispositivos.
