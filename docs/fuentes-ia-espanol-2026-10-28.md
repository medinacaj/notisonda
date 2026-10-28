# IA en español: fuentes y estructura revisadas

> Registro de PR111 sobre 276 suscripciones. Posteriormente se comprobó el RSS nativo de MIT en español y los siete RSS antes pendientes; la [ampliación mundial](fuentes-cobertura-mundial-2026-10-28.md) lleva el catálogo a 311 sin bajas. Los estados antiguos permanecen como evidencia histórica, no como diagnóstico actual.

## Resultado del catálogo

Se conservaron las **248 suscripciones publicadas en main**, incluidas las 27 altas de IA/tecnología de PR102. Se integraron las **23 altas generales pendientes** y se añadieron **cinco canales temáticos de IA en español**: **276 suscripciones en ocho carpetas**, sin bajas ni cambios de URL, identificador, nombre o categoría anteriores. Este total cuenta suscripciones, no medios independientes ni artículos.

Los cinco canales nuevos son RSS válidos de **Google Noticias**, identificados como **RADAR**. El portal editorial aporta el contenido enlazado; Google es el intermediario. No se añaden como si fueran RSS nativos del editor.

## Altas de esta revisión

| Canal en Inteligencia Artificial | RSS observado | Entradas del índice | Última fecha del RSS (UTC) |
|---|---|---:|---|
| [Hipertextual | IA](https://hipertextual.com/) | [RSS](https://news.google.com/rss/search?q=site%3Ahipertextual.com+%28%22inteligencia+artificial%22+OR+%22modelos+de+IA%22+OR+%22aprendizaje+autom%C3%A1tico%22%29+when%3A30d&hl=es&gl=ES&ceid=ES%3Aes) | 53 | 2026-10-27T18:43:00Z |
| [WIRED en Español | IA](https://es.wired.com/) | [RSS](https://news.google.com/rss/search?q=site%3Aes.wired.com+%28%22inteligencia+artificial%22+OR+%22modelos+de+IA%22+OR+%22aprendizaje+autom%C3%A1tico%22%29+when%3A30d&hl=es&gl=ES&ceid=ES%3Aes) | 92 | 2026-10-27T23:35:41Z |
| [CSIC | Investigación de IA](https://www.csic.es/es/actualidad-del-csic) | [RSS](https://news.google.com/rss/search?q=site%3Acsic.es%2Fes%2Factualidad-del-csic+%28%22inteligencia+artificial%22+OR+%22aprendizaje+autom%C3%A1tico%22%29+when%3A30d&hl=es&gl=ES&ceid=ES%3Aes) | 4 | 2026-10-23T12:00:00Z |
| [Think Big / Telefónica | IA aplicada](https://blogthinkbig.com/) | [RSS](https://news.google.com/rss/search?q=site%3Ablogthinkbig.com+%28intitle%3AIA+OR+intitle%3A%22inteligencia+artificial%22%29+when%3A30d&hl=es&gl=ES&ceid=ES%3Aes) | 31 | 2026-10-27T17:32:17Z |
| [Retina | Análisis de IA](https://retinatendencias.com/) | [RSS](https://news.google.com/rss/search?q=site%3Aretinatendencias.com+%28%22inteligencia+artificial%22+OR+%22IA%22%29+when%3A30d&hl=es&gl=ES&ceid=ES%3Aes) | 5 | 2026-10-26T11:48:12Z |

Hipertextual y WIRED amplían artículos, modelos, herramientas y lanzamientos. CSIC aporta investigación institucional; Think Big es un blog corporativo de Telefónica, por lo que su análisis de IA aplicada conserva esa procedencia. Retina amplía análisis y tendencias. Las consultas priorizan el último mes; el buscador puede incluir índices, páginas institucionales o resultados relacionados indirectamente. Una fecha del índice no acredita por sí sola la fecha del artículo original.

## Fuentes solicitadas que ya existían

| Portal o cobertura | Tratamiento |
|---|---|
| Xataka, Genbeta, WWWhat’s New | Se conservan sus RSS específicos de IA, sin crear otra suscripción idéntica. |
| Hipertextual | Se conserva su RSS general en Tecnología; el nuevo canal de IA es una búsqueda temática distinta. |
| Agencia SINC | Se conservan Tecnología, Ciencia y Agenda, además del RADAR de ciencia existente. No todos esos canales son exclusivos de IA. |
| MIT Technology Review en español | Se conserva y revalida el RSS intermediado existente. La edición inglesa anterior sigue separada. |
| Papers/estudios, conferencias/congresos, modelos/herramientas | Se conservan y revalidan las tres búsquedas temáticas existentes en español. |

Se observaron respuestas HTTP200 y entradas fechadas en los cinco RSS nuevos y en los canales revalidados detallados en el registro. Las observaciones se realizaron el 28 de octubre de 2026 UTC; las primeras pruebas de esta ampliación general ocurrieron el día anterior en Chile. Las fechas precisas y hashes constan en los registros.

## RSS no confirmados y restricciones

**No se ha confirmado un RSS editorial propio de MIT Technology Review en español en esta revisión**; el canal válido incorporado es el intermediado. Esto no demuestra que el portal carezca de RSS.

La política de red de este entorno no permite consultar directamente Xataka, Genbeta, WWWhat’s New, Hipertextual o Agencia SINC. Sus siete URL ya configuradas permanecen intactas y figuran como `not_checked_network_policy`, con HTTP y número de entradas nulos. No se marcan como inválidas, vacías o inactivas. También quedan sin comprobar los RSS editoriales propios de los cinco portales nuevos: se incluyen únicamente sus RSS de Google observados. Se guardó una ampliación concreta de dominios para revisión en la configuración del entorno; guardar el borrador no habilita esos accesos.

BBVA OpenMind no se añade: la búsqueda de IA probada en Google Noticias no entregó entradas del último mes. Ese resultado no determina la validez de un posible RSS propio. No hubo evidencia suficiente para declarar que alguno de los portales solicitados **no dispone** de RSS válido.

## Cobertura y conservación

Se amplía la lectura de artículos, revistas, investigación y noticias sobre papers, congresos, nuevos modelos, herramientas y tendencias. Estos canales no descargan automáticamente papers completos ni traducen las fuentes inglesas anteriores. Las noticias sobre conferencias permanecen en IA; la Agenda pública mantiene su validación independiente de fechas y ámbito territorial.

No se cambian la normalización/deduplicación del recolector, retención de 45 días y 5000 entradas, frecuencia de publicación, fuentes existentes o preferencias locales. Se verifican las coincidencias OPML/JSON y la conservación de los registros anteriores con contratos offline. No se añade traducción, cuentas, seguimiento ni servicios de IA.

## Estructura del sitio

- Inicio tiene una estructura directa: encabezado breve, novedades condicionales, un destacado, siete titulares distintos como máximo en carrusel y cobertura/radar/tendencias.
- Se retiran los antiguos contenedores ocultos de carpetas y guardadas y sus renderizadores. No se reconstruyen listas invisibles ni se trasladan paneles al cargar la página.
- Las carpetas permanecen en el lateral; Noticias conserva el archivo completo, sus filtros y Guardadas. Agenda y Resumen mantienen sus rutas y funciones.
- Radar de noticias sigue visible después del carrusel, con Lo más cubierto y Temas en alza en superficies diferenciadas. La rejilla se apila en móvil.
- Se unifican encabezados, alineación de contadores y separación entre bloques. Se conserva el logo pequeño y los modos claro/oscuro.
- Se corrige la regresión de Texto grande: ahora aumenta los titulares incluso cuando hay un tamaño independiente guardado entre 14 y 22 px, sin cambiar ese valor ni el respaldo.

## Evidencia y límites

Registro: [`spanish-ai-verification.json`](../sources/spanish-ai-verification.json). El registro anterior de PR102 se conserva como histórico; las observaciones actuales no sobrescriben comprobaciones pasadas. El informe de las 23 altas generales es [independiente](fuentes-verificadas-2026-10-28.md).

Los metadatos RSS no verifican hechos, revisión por pares, actualidad real del texto, audiencia, condiciones editoriales o licencias de cada portal. Se conservan atribución, extractos y enlaces originales; acceso público no equivale a autorización para reproducir artículos completos. Países de los medios principalmente España/Latinoamérica; Google como intermediario. No se certifica cumplimiento legal ni accesibilidad de dispositivos físicos.
