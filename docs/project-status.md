# Estado del proyecto — Radar RSS

Actualizado el 25 de octubre de 2026. Este archivo distingue código implementado de verificaciones que necesitan evidencia externa. La versión publicada y los resultados más recientes se consultan en GitHub Actions.

## Estado del código

- Web pública: https://medinacaj.github.io/radar-rss-publico/; rama estable `main`.
- Publicación: `.github/workflows/deploy.yml`, cada tres horas UTC (`17 */3 * * *`), con posibles demoras de GitHub. El navegador comprueba nuevas publicaciones cada 15 minutos.
- Catálogo: **221 suscripciones en ocho carpetas**. Concepción mantiene 33 canales (21 directos/12 consultas); Maturín/Monagas seis; los cuatro canales culturales en español están dentro de Internacionales.
- Noticias: archivo de hasta 5000 entradas y 45 días, listado paginado de 36 por defecto. Los contadores completan el archivo en segundo plano, respetan filtros/lectura y anuncian carga o total no disponible si no pueden verificarlo. Hasta tres descargas históricas simultáneas, canceladas al fallar o cambiar generación.
- Agenda: recopilación independiente, horizonte de 90 días y fecha local de la actividad. Conserva actividades vigentes hasta acabar su último día, separa anuncios pendientes y excluye cancelados de próximos eventos. No deduce la fecha de actividad de la publicación. No garantiza cobertura exhaustiva.
- Interfaz: lateral visible/ocultable en escritorio, menú accesible móvil, portada con un carrusel de noticias y agenda separada del listado, tema del sistema y firma LinkedIn.
- Lectura y respaldo: guardadas, marcas, búsquedas y preferencias locales; respaldo v3 compatible con v2. Las marcas masivas globales/de carpeta esperan el archivo completo y no se aplican si falta metadata válida o falla su verificación.
- Recuperación: Pages y caché se comparan por instantes UTC; fechas inválidas o sin zona no validan un respaldo. Si no hay copia verificable se detiene la recuperación. Artefactos con retención limitada, sin garantía de almacenamiento permanente.
- Privacidad: preferencias sólo en este navegador, sin cuentas, sincronización ni analítica central.

## Evidencia publicada y regresiones

- PR89: auditoría, respaldo Concepción, navegación y personalización; PR90: eliminación de carpeta cultural independiente y selección en español.
- PR91: separación de noticias/agenda de 90 días y preservación de actividades independiente del límite de noticias.
- PR93: contadores reales, estados de error/reintento y cambio de generación; publicación verificada sobre `ebd1b157169e9189553bdb4ddd9a1a0c17d8dd23`.
- Referencias: [PR publicados](https://github.com/medinacaj/radar-rss-publico/pulls?q=is%3Apr+is%3Amerged), [Actions](https://github.com/medinacaj/radar-rss-publico/actions) e [incidencias abiertas](https://github.com/medinacaj/radar-rss-publico/issues).
- Calidad: suite Python/Node sin red real. Pruebas de navegador con fixtures RSS y HTTPS local en Chromium, Firefox y WebKit, siete anchos de 320–1440 px. Las nuevas regresiones de lectura masiva y recuperación acompañan el código; sus resultados de CI constan en cada PR.
- Verificador público: contrasta la generación esperada del build y valida datos/noticias/agenda. La anotación «Publicación verificada» informa cantidades observadas sin inventar artículos ni actividades.

## Revisión de propuestas anteriores

| Referencia | Situación en este código |
|---|---|
| PR76 | Se recupera la corrección de cronología y se añaden regresiones de offsets, equivalencias, fechas inválidas y fallo de red. |
| PR92 | Encabezado OPML corregido a 221 fuentes/ocho carpetas; cuerpo, fuentes y URL conservados. |
| PR77 | Contadores resueltos por PR93. No se adoptan de esa rama los cambios a 9000 noticias/90 días ni el contador global que ignora filtros. |
| PR78 | Paginación rehabilitada por PR93; frecuencia corregida a tres horas. El resto amplía la experiencia de lectura y no se ha fusionado como paquete sobre el diseño actual. |
| PR88 | Propone una integración adicional de eventos Biobío/Chile; permanece separada de la agenda de 90 días publicada y requiere revisar su convivencia antes de incorporarla. |
| PR96 | La consulta de ese número en este repositorio devuelve 404. No se ha aplicado un PR supuesto; hace falta una referencia accesible. |

## Verificaciones pendientes y límites

- [Issue #31](https://github.com/medinacaj/radar-rss-publico/issues/31): pruebas físicas Safari/iPhone con VoiceOver, Android con TalkBack, tabletas, teclado, zoom y orientación. WebKit automatizado no sustituye esos dispositivos; no se declara realizado ese trabajo.
- [Issue #32](https://github.com/medinacaj/radar-rss-publico/issues/32): curación manual de coincidencias de titulares, enlaces, fechas y atribución. Los informes son heurísticos; no se retiran fuentes ni se cambia el deduplicador automáticamente.
- Disponibilidad de nuevas fuentes: el registro `sources/discovery-verification.json` conserva las observaciones originales pendientes. No equivale a comprobar el estado actual de cada medio. La evidencia de Concepción del 24 de octubre está en `sources/concepcion-verification.json`.
- Respaldos durables externos y sincronización entre dispositivos siguen fuera de la arquitectura estática. Caché y artefactos caducan; el archivo público no es permanente.
- La inclusión de una fuente, un HTTP correcto o una prueba automatizada no certifica licencias, derechos de reproducción ni cumplimiento legal. Se mantienen atribución, extractos y enlaces originales.

## Fuente de verdad

GitHub Issues/PR/Actions contienen incidencias, diffs y evidencia de integración. `docs/decisions.md` recoge decisiones duraderas; los planes de `docs/superpowers/` explican cambios acotados, sin sustituir la evidencia de CI o de dispositivos reales.
