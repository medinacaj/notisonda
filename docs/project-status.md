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

## Fuente de verdad
- [Issues](https://github.com/medinacaj/radar-rss-publico/issues): incidencias sin resolver.
- [Pull requests](https://github.com/medinacaj/radar-rss-publico/pulls): cambios en revisión.
- [Actions](https://github.com/medinacaj/radar-rss-publico/actions): evidencia de pruebas y despliegue.
- `docs/decisions.md`: decisiones técnicas duraderas.

## Limitaciones reconocidas
WebKit automatizado no certifica Safari en hardware iOS. La prueba de accesibilidad automatizada no sustituye pruebas con lectores de pantalla reales. Una base de datos sería necesaria para garantizar historial permanente o sincronización entre dispositivos.
