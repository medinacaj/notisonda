# Arquitectura — Radar RSS

El contenido se extrae de `sources/feeds.opml` por `scripts/collect.py`, se normaliza/agrupa y se publica como JSON estático en `web/data/`. La aplicación `web/` se sirve desde GitHub Pages. El workflow existente `deploy.yml` recopila noticias periódicamente y publica el sitio. Las pruebas Python usan `unittest`; las comprobaciones de UI incluyen Node y archivos `.cjs`. **No ejecutar recolección en la CI de PR:** depende de red externa y puede activar fuentes reales.

**Eventos:** `eventos/` contiene el recolector trasladado desde `eventos-biobio` (solo biblioteca estándar). `.github/workflows/eventos.yml` rastrea una vez al día y entrega los snapshots como artefacto; `deploy.yml` los recupera (artefacto o último publicado en Pages), ejecuta `eventos/publicar_web.py export` y publica `web/data/eventos.json`, que consume `web/eventos.js`. Ningún workflow hace commits en `main`, y un fallo de eventos no impide publicar noticias.

## Contratos a preservar
- No romper rutas públicas ni cambios de formato de datos sin actualizar consumidores y pruebas.
- Separar código de aplicación, datos, pruebas y automatización.
- Los cambios en deploy/monitorización deben verificarse con especial cuidado.
- Consultar `README.md` y el código actual como fuentes más recientes; este mapa es orientativo, no un inventario exhaustivo.
