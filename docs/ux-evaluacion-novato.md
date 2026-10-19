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

## Corregido en esta rama
1. **Hacer clic en una cubierta sin foto no hacía nada** (la foto real sí abría la
   vista previa). Ahora la cubierta tipográfica también abre la vista previa
   (`web/app.js`, `web/v13.css`).
2. **El filtro «Todas las etiquetas» aparecía vacío** si la persona no había creado
   etiquetas: era un control sin opciones. Ahora se oculta hasta que existe al menos
   una etiqueta (`web/library.js`, `web/library.css`).
3. **En «Por carpeta», los títulos se cortaban a mitad de palabra**
   («Internacionale/s», «Latinoaméric/a») y «Ver todo» se partía. Ahora el título
   conserva las palabras completas y el pulso y «Ver todo» bajan de línea si no
   caben (`web/features.css`).

Además se actualizaron las versiones de los recursos en `web/index.html` y las dos pruebas que las fijan.

## Validación pendiente
- Repetir el recorrido con los datos reales publicados (fotos, volumen y errores RSS reales).
- Hacer una prueba corta con 3–5 personas no técnicas, con tareas como «encuentra una noticia de Chile de hoy», «guárdala» y «compártela por WhatsApp».
