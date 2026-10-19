# Evaluación UI/UX — perspectiva de usuario novato

Fecha: 2026-10-19 · Base: `6349c19` (main) · Rama: `claude/website-ui-ux-evaluation-qd8pb3`

## Método y límites
- Se renderizó `web/` en Chromium (Playwright) a 1440×900 y 390×844, con el
  `sources.json` real (150 fuentes) y **90 noticias sintéticas sin fotografía**.
  El sitio publicado no era accesible desde el entorno, así que las capturas no
  reflejan fotos reales ni el volumen real de noticias.
- Recorrido: primera visita → portada → menú → «Todas» → vista previa →
  Configuración → Resumen del día. Se midieron posiciones, tamaños de controles y
  contraste de textos secundarios.
- Persona: alguien que llega por un enlace compartido, no sabe qué es RSS y quiere
  «ver las noticias de hoy» en el móvil.

## Lo que ya funciona bien
- Sin cuenta, y la privacidad se explica con claridad («solo en este navegador»).
- La vista previa tiene una acción principal inequívoca: «Abrir noticia completa · en otra pestaña».
- Guía de bienvenida descartable («Empieza con Radar RSS»).
- Los controles de solo icono tienen nombre accesible; hay atajos de teclado, tema oscuro y modo ligero.
- Contraste de los textos secundarios medido entre 4,6:1 y 5,6:1 (cumple AA).

## Hallazgos y recomendaciones (ordenados por impacto en el novato)

| # | Prioridad | Hallazgo | Recomendación |
|---|---|---|---|
| 1 | Alta | En el móvil, la **primera noticia de la portada aparece a ~1040 px**, fuera de la primera pantalla (844 px). Antes aparecen el título, la guía de 3 tarjetas y el gráfico radar. | En pantallas ≤ 720 px, mostrar 3–5 titulares de «Lo más cubierto» antes del gráfico, o mover el radar debajo de la lista o detrás de un botón «Ver mapa». |
| 2 | Alta | **El gráfico radar es difícil de leer** para un novato: los puntos no tienen etiqueta, los nombres de sector se superponen a los puntos («Tecnología») y la explicación está al pie. | Darle un papel secundario (ver n.º 1). Si se mantiene, poner la leyenda arriba en una línea («Más cerca del centro = más reciente») y separar las etiquetas de los puntos. |
| 3 | Alta | **Hay demasiados controles antes de la primera noticia en «Todas»**: 3 pestañas, Fuente (150 opciones con prefijos como «ANÁLISIS —» y «MEDIO —»), Etiquetas, Columnas, Lista, Cobertura, Antigüedad, «Guardar búsqueda», «Marcar visibles como leídas» y el texto «36 visibles · 90 sin leer con estos filtros». En el móvil, la primera tarjeta empieza a 488 px. | Dejar visibles solo Todas / Sin leer / Guardadas y un botón «Filtros (n)» que abra un panel con fuente, región, antigüedad y guardar búsqueda. Mover «Marcar visibles como leídas» al menú «⋯». Quitar los prefijos de tipo en el desplegable de fuentes o agruparlos con `<optgroup>`. |
| 4 | Alta | **Vocabulario técnico o ambiguo**: RSS, OPML, «Carpetas de fuentes», «Estado RSS», «fuentes no disponibles», «Modo ligero», «Sin evaluación editorial». La palabra **«Cobertura» tiene dos significados**: número de medios («6 medios») y selector de región. | Glosario de microcopy: «Carpetas de fuentes» → «Temas»; el selector «Cobertura» → «Región»; «6 medios» → «Publicada por 6 medios»; «Lo más cubierto» → «Lo que más medios publican». Reservar «RSS» y «OPML» para Configuración → Avanzado. |
| 5 | Media | **Las acciones de la tarjeta solo tienen icono** (✓, marcador, ⋯). El ✓ es ambiguo («¿aprobar?», «¿hecho?») y en pantallas táctiles no hay tooltip. | Añadir texto corto visible al menos en el móvil («Leída», «Guardar») o una pista la primera vez que aparecen. |
| 6 | Media | **Una tarjeta sin foto ocupa ~533 px en el móvil**, porque la cubierta tipográfica de 16:9 repite el nombre del medio que ya aparece en el pie. Solo cabe una noticia por pantalla. | En el móvil, reducir la cubierta sin foto a una franja (≈ 64 px) o eliminarla; el pie ya identifica el medio. |
| 7 | Media | En la primera visita **todas las noticias cuentan como «Sin leer» (90)**, así que el contador no informa nada y empuja a «Marcar visibles como leídas». | En la primera visita, ocultar el contador «Sin leer» o considerar leídas las noticias anteriores a esa visita. |
| 8 | Media | **El encabezado de la portada no explica qué es el sitio** («Tu panorama informativo · Noticias recientes y categorías, sin ruido visual»). | Una frase que oriente: «Titulares de 150 medios, actualizados cada ~6 h. Toca una noticia para ver un resumen». |
| 9 | Media | **Configuración → Apariencia** muestra primero el control de ancho del panel lateral, que es avanzado. «Texto grande» y «Mostrar imágenes» quedan por debajo o fuera de la vista. | Orden sugerido: Tema, Tamaño de texto, Imágenes, Resúmenes; mover el ancho del panel, las columnas y el espaciado a un bloque «Avanzado» plegable. |
| 10 | Baja | **En la cabecera móvil hay 4 iconos sin texto** (buscar, actualizar, configuración, tema), de 30–36 px. La hora «Actualizado…» se oculta en el móvil. | Llevar el tema a Configuración y subir los objetivos táctiles a 44 px; mostrar «Hace X min» junto al botón de actualizar. Cumplen WCAG 2.5.8 (24 px), pero quedan por debajo de la recomendación táctil. |
| 11 | Baja | **Nombres inconsistentes**: «Resumen» (chips) / «Resumen del día» (menú); «Todas» / «Todas las noticias». | Unificar las etiquetas. |
| 12 | Baja | **Comparador de la vista previa**: el selector «Comparar coberturas · Agrupar por medio y región» y el texto «7 publicaciones enlazadas · Sin evaluación editorial» son jerga. | «Cómo lo cuenta cada medio» basta; mover el selector a un control discreto «Agrupar: medio / región». |

## Aplicado en esta rama

Primera tanda (correcciones rápidas):
- La cubierta sin foto abre la vista previa al hacer clic, igual que una foto (`app.js`, `v13.css`).
- El filtro «Todas las etiquetas» se oculta mientras no haya etiquetas (`library.js`, `library.css`).
- Los títulos de «Por carpeta» ya no se cortan a mitad de palabra (`features.css`).

Segunda tanda: las 12 recomendaciones. Casi todo vive en una capa nueva,
`web/v14.js` + `web/v14.css`, que se carga después de v13. El resto son cambios de texto en los archivos existentes.

| # | Estado | Qué cambió |
|---|---|---|
| 1 | Hecho | En ≤ 720 px, la lista numerada va antes que el mapa. La primera historia pasa de ~1040 px a ~600 px en 390×844. La guía de bienvenida se compacta a tres botones de una línea. |
| 2 | Hecho | El mapa se abre con «Ver mapa de las últimas 24 horas» en el móvil. La leyenda queda arriba, en una línea corta, y las etiquetas de sector se dibujan sobre los puntos, con halo. |
| 3 | Hecho | Botón «Filtros (n)» con panel plegable (fuente, etiqueta, región, antigüedad, guardar búsqueda, «Quitar filtros» y «Marcar visibles como leídas»). El panel arranca cerrado y recuerda su estado. Las fuentes se muestran sin prefijos («ABC \| Última hora», «OpenAI News (oficial)») y ordenadas alfabéticamente. «Combina filtros» de la guía abre el panel. El resumen ahora dice «Mostrando 36 de 90 · 90 sin leer». |
| 4 | Hecho | «Carpetas de fuentes» → «Temas»; el selector «Cobertura» → «Región»; la etiqueta de las tarjetas «6 medios» → «Publicada en 6 medios»; «Lo más cubierto» → «Lo que más medios publican»; «Modo ligero» → «Ahorro de datos»; «Estado RSS» → «Estado de las fuentes». OPML solo aparece en el botón de exportar, con una explicación. |
| 5 | Hecho | Pista descartable sobre la lista: «En cada noticia: ✓ márcala como leída · 🔖 guárdala para después · ⋯ más opciones». Los botones siguen siendo solo icono, como exige el contrato v13. |
| 6 | Parcial | En ≤ 720 px las cubiertas pasan de 16:9 a 5:2 (de ~533 a ~475 px por tarjeta). No se redujo a una franja: el contrato de alturas uniformes (`grid-auto-rows:1fr`) iguala cada tarjeta a la más alta, así que una franja solo dejaría espacio vacío. |
| 7 | Hecho | Sin historial de lectura, la pestaña «Sin leer» no muestra el número. El número sigue en el DOM y reaparece con la primera noticia leída. |
| 8 | Hecho | La portada dice «Titulares de N fuentes, actualizados cada ~6 horas. Abre una noticia para ver un resumen antes de ir al sitio del medio». También se ve en el móvil. |
| 9 | Hecho | Apariencia muestra Tema, Tamaño del texto, Imágenes, Resúmenes y Ahorro de datos. Formato, columnas, espaciado, ancho del panel y presentación de inicio quedan en «Más opciones de diseño». |
| 10 | Parcial | En el móvil, el botón de tema se oculta (sigue en Configuración) y los botones de la cabecera miden 44 px en pantallas táctiles. «Actualizado…» sigue oculto en el móvil: no cabe a 320–390 px. |
| 11 | Hecho | Los chips dicen «Resumen del día» y «Todas las noticias», igual que el menú. |
| 12 | Hecho | El comparador muestra «Ordenar: Por medio / Por hora de publicación» y «N versiones de esta noticia». |

Pruebas: se actualizaron las aserciones que fijaban los textos antiguos, se añadió
`tests/test_v14_novice.py` y `browser_tests/responsive_smoke.py` ahora comprueba
el panel de filtros, la pista y el mapa en el móvil.

## Validación pendiente
- Repetir el recorrido con los datos reales publicados (fotos, volumen y errores RSS reales).
- Hacer una prueba corta con 3–5 personas no técnicas, con tareas como «encuentra una noticia de Chile de hoy», «guárdala» y «compártela por WhatsApp».
