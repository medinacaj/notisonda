# Identidad Radar-RSS

El sistema vuelve a llamarse **Radar-RSS** por indicación del usuario. Se actualizan cabecera, pie, pestaña, preferencias, descripción, metadatos sociales, aplicación instalada, textos, resúmenes, archivos descargados y nombre de los RSS generados.

GitHub confirma que el repositorio actual es `medinacaj/radar-rss`. La dirección vigente es **https://medinacaj.github.io/radar-rss/**: tanto la página como `data/meta.json` respondieron 200. Las rutas anteriores de `/notisonda/` respondieron 404. `scripts/site_config.py` alinea recuperación de noticias, agenda y monitor con la ruta vigente; la comprobación real de salud con esa configuración terminó correctamente. Esa comprobación no significa que el cambio de código ya esté publicado.

Se recupera el símbolo RSS anterior bajo `radar-favicon.svg` y `radar-icon-maskable.svg`, copiado sin modificar de la revisión `afc1785`. Se reutilizan los PNG históricos `icon-192.png`, `icon-512.png`, `icon-maskable-512.png` y `social-card.png`. El icono Apple declara sus 192 píxeles reales. La tarjeta social conserva su diseño anterior, donde la marca se escribe visualmente «Radar RSS»; el nombre canónico de HTML y manifest es «Radar-RSS». Los SVG y PNG de Notisonda permanecen en el repositorio.

Las claves de almacenamiento, el formato `radar-rss-settings-v3`, los GUID de noticias y los UID `@agenda.radar-rss` se conservan. Los respaldos v2/v3 anteriores siguen aceptándose. Los archivos nuevos usan el prefijo `radar-rss-`. La caché se renueva a `radar-rss-v56`, conservando la limpieza de las cachés anteriores de ambas marcas, la lectura sin conexión y la exigencia de red al actualizar manualmente.

`web/data/sources.json` conserva exactamente sus bytes anteriores: 311 fuentes en ocho carpetas. El cambio del OPML se limita a su título. Los PR #120 y #121 de fuentes siguen separados, en borrador y pendientes de publicación por indicación del usuario.

La URL anterior de una aplicación instalada o un marcador seguirá apuntando a una ruta que ya devuelve 404. El acceso vigente debe abrirse desde `/radar-rss/`; las claves de almacenamiento se mantienen en el mismo origen. No se puede crear una redirección desde el proyecto GitHub Pages cuyo nombre anterior dejó de publicarse mediante este cambio de aplicación.

## Verificación

- 292 pruebas Python aprobadas, incluidas recuperación, monitor, títulos RSS, atribución y conservación de activos anteriores.
- Auditoría OPML: 311 fuentes, ocho carpetas, cero problemas; catálogo JSON idéntico byte a byte.
- Sintaxis de los scripts modificados y pruebas Node de migración de caché, lectura offline, actualización manual y herramientas de fuentes aprobadas.
- 42 regresiones de interfaz y 12 de herramientas de agenda aprobadas; el calendario conserva su UID y exporta con el nombre y PRODID de Radar-RSS.
- Comprobación de navegador con los `app.js` y `library.js` exactos de la versión anterior: actualización con lectura, guardados, fuentes ocultas y carpetas conservadas; importación del respaldo anterior de Notisonda y exportación nueva con el mismo esquema.
- Cabecera, metadatos, manifest, enlaces y ambos temas comprobados a 390 y 1440 píxeles, sin desbordamiento horizontal.

La revisión final encontró un texto antiguo en el pie y la versión anterior en la URL del script de agenda. Ambos se corrigieron con regresiones que fallaron antes del ajuste y pasaron después. La comprobación del navegador reprodujo una respuesta anterior de `agenda.js?v=1.1.1` que exportaba `notisonda-agenda.ics`; la referencia nueva `v=1.1.2` evita esa copia y exporta con el nombre actual, conservando el UID del evento.

Las pruebas locales y los cambios preparados no equivalen a una publicación. La revisión y CI del PR documentan el estado del commit propuesto.
