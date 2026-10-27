# Arquitectura — Radar RSS

El contenido se extrae de `sources/feeds.opml` por `scripts/collect.py`, se normaliza/agrupa y se publica como JSON estático en `web/data/`. La aplicación `web/` se sirve desde GitHub Pages. El workflow existente `deploy.yml` recopila noticias periódicamente y publica el sitio. Las pruebas Python usan `unittest`; las comprobaciones de UI incluyen Node y archivos `.cjs`. **No ejecutar recolección en la CI de PR:** depende de red externa y puede activar fuentes reales.

## Contratos a preservar
- No romper rutas públicas ni cambios de formato de datos sin actualizar consumidores y pruebas.
- Separar código de aplicación, datos, pruebas y automatización.
- Los cambios en deploy/monitorización deben verificarse con especial cuidado.
- Consultar `README.md` y el código actual como fuentes más recientes; este mapa es orientativo, no un inventario exhaustivo.

## Agenda y lectura (octubre 2026)

`collect_events.py` reúne RSS de `sources/events.json` y, con `--direct-config sources/events-direct.json`, calendarios oficiales mediante `event_sources.py`. Los hechos explícitos se normalizan y fusionan por `events.py` en un único `events.json` v1; ICS conserva UID y TZID y reduce el final exclusivo al último día local ocupado. La publicación usa la misma generación de noticias. La caché conserva futuras actividades aunque la fuente falle; `agenda.js` valida generación y datos antes de filtrar el horizonte de 90 días. Los opcionales de localidad/tipo/precio no invalidan documentos antiguos. No se importa el stack, workflow ni snapshots de PR88.

`feed-ux.js` y `reader-ux.js` se cargan tras los módulos actuales y extienden sus filtros y lector. `app.js` prepara nuevas publicaciones sin sustituir el estado hasta aplicar; al hacerlo cancela el histórico anterior y conserva su exclusión hasta que se asienten los trabajadores. Los contadores requieren archivo y manifiesto completos. El respaldo v3 incluye el módulo validado `agendaPreferences`; su ausencia en respaldos antiguos conserva los datos locales. Ningún guardado añade servicios ni sincronización.

## Sistema visual Dimension

`dimension.css` es la única capa activa de tema. Sus superficies comparten tokens de relieve y bordes degradados; hover con ratón, foco y pulsación muestran el halo sin añadir estado JS ni capas que intercepten clics. La aurora CSS y transiciones se desactivan con reduced-motion. `radar-logo.png` es el activo original local reutilizado en lateral, portada e instalación; `favicon.svg` conserva una versión vectorial compacta del símbolo. `svgIcon()` mantiene su API con ocho símbolos de categoría y un icono propio para carpetas manuales. `styles.css` y las hojas de módulos conservan estructura/controles, y sus colores se resuelven con tokens del tema. Index y el shellSWv41 retiran las siete referencias visuales históricas; `?preview=` deja de conmutar estilos anteriores. `app.js` añade la ruta `#agenda` con una vista independiente; los contadores de biblioteca se asocian mediante `data-destination`, no por posición. `homepage.js` conserva un único destacado y un carrusel sin IDs repetidos, sin fotografías decorativas. Las herramientas de cobertura/tendencias pertenecen a Resumen y se actualizan también al entrar directamente en esa ruta.
