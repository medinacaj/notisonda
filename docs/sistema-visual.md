# RadarRRS — Sistema editorial V11 · Mesa de noticias

## Objetivo de producto
RadarRRS es un **portal público de noticias** y un lector de fuentes RSS, no un panel técnico. Deben verse primero las noticias. Las herramientas avanzadas se muestran a demanda.

## Jerarquía fija

1. Inicio: mesa de noticias de DOS COLUMNAS: **En portada** (3 artículos en filas con miniatura lateral) y **Últimas publicaciones** (titulares breves al lado); luego novedades funcionales, guardadas, carpetas y radar/tendencias.
2. Listado: título, pestañas Todas / Sin leer / Guardadas, filtro por fuente, vista y **Más opciones**. El buscador permanece en la cabecera.
3. Más opciones: antigüedad, guardar búsqueda y marcar noticias visibles como leídas. El menú se expande **en flujo**, no flotando sobre los resultados.
4. Configuración > Apariencia: tema, tamaño de letra, imágenes y resúmenes como opciones principales. Columnas, espaciado, formato y panel lateral se mantienen en opciones avanzadas. No incluir controles que solo activan presentaciones promocionales.

## Sistema V11 — Rediseño ESTRUCTURAL verificable

A diferencia de V6 a V10, V11 modifica **la composición y la navegación**, no únicamente los tokens de color y tipografía:

- **Eliminado el sidebar permanente en escritorio:** el contenido usa el ancho disponible. El catálogo completo de fuentes y las herramientas de carpetas siguen en un menú desplegable mediante el botón superior; accesible con ratón, teclado, Escape, foco e indicador `aria-expanded`.
- **Navegación principal horizontal en todas las pantallas:** Inicio, Resumen, Todas y las seis categorías aparecen en una franja propia debajo de la barra superior. Permite entrar sin abrir el menú detallado.
- **Portada de tipo redacción:** `newsroom-lead` coloca en escritorio **En portada** (3 noticias en filas horizontales, fotografías pequeñas a la izquierda y titulares) junto a **Últimas publicaciones** (8 titulares tipo teletipo). En tablet/móvil se convierte en una sola columna o dos columnas de titulares, sin ventanas o copys promocionales.
- **Categorías por carpeta:** matriz de 3 columnas en escritorio, 2 en tablet y 1 en móvil. Contraste por contenido, no barras coloreadas.
- **RSS intacto:** quedan funcionales las noticias, búsqueda, fuentes, 6 carpetas, acciones de marcar leída, guardar, menús contextuales, resumen, filtros, vista lista, columnas y configuración.
- **Apariencia:** se conserva Ink & Paper V10, solo como capa visual. El cambio de identidad se valida por estructura del DOM, coordenadas de las columnas, orientación de tarjetas y menú oculto por defecto, además de colores.
- **Preferencia de ancho de menú:** disponible dentro de Configuración en escritorio; el menú ya no ocupa permanentemente parte de la portada.

Prohibido volver a introducir un sidebar fijo y una cuadrícula homogénea de tarjetas como única estructura de Inicio en una revisión que se anuncie como rediseño.

## V9.2 — Nada de encabezados promocionales en Inicio

- Eliminar el masthead “Noticias para estar al día”, su subtítulo y su sello.
- Eliminar el hero antiguo y el ajuste “Mostrar presentación de inicio” (ya estaba inoperante).
- Conservar el H1 de Inicio **solo para accesibilidad**; la navegación no debe duplicarlo.
- Empezar por las tarjetas **En portada**, sin espacio reservado para títulos de marketing.
- Reubicar “Mientras no estabas” después de la primera selección de noticias. Es una función útil, no un obstáculo previo a la lectura.
- Eliminar frases ornamentales junto a títulos autoexplicativos. Mantener aclaraciones mediante `title` o texto accesible si proporcionan una definición verificable.
- Priorizar búsqueda, filtros, noticias y enlaces funcionales. Evitar estadísticas, paneles y botones repetidos.

## Sistema V10 — Adaptación de la referencia Ramp (Ink & Paper)

La referencia visual proporcionada se adapta **al lector de noticias**, no se clona su sitio de marketing: se conserva el feed, las seis categorías, las imágenes legítimas, los filtros y la portada directa a noticias. No se replica su tipografía propietaria Laus﻿anne; se emplea Inter con alternativas del sistema, sin distribuir fuentes comerciales.

- **Lienzo**: hueso `#f4f2f0`; superficies `#ffffff`; texto tinta `#0c0a08`; secundarios `#6d6c6b`; bordes `#e5e7eb`.
- **Jerarquía**: sans serif neo-grotesca; tamaño, interlineado y separación establecen niveles. No usar grandes eslóganes, bandas publicitarias ni intersticios promocionales.
- **Tarjetas**: 16 px de radio y 1 px de borde, **sin sombra ni transformación vertical**. Mostrar fotografía real cuando exista, título y fuente; no pintar contorno según la categoría.
- **Acciones**: lima `#e4f222` únicamente para llamadas funcionales de alta prioridad como “Cargar más” y “Ver solo las nuevas”, con texto casi negro. El resto de controles es neutro o outline/ghost.
- **Categorías**: mantener sus seis matices en el icono de navegación o la etiqueta pequeña de la noticia. No convertir todo el sitio en amarillo ni introducir franjas sobre las tarjetas.
- **Navegación**: barra lateral y encabezado blancos con líneas de separación. Estado activo por superficie y peso, no por paneles de color.
- **Modo oscuro**: lienzo `#171616`, superficie `#232121`, bordes `#444240`; acciones lima con texto negro.
- **Responsive**: el mismo sistema de lectura se conserva en el cajón móvil, sin barras adicionales.
- **Motion**: interacción ligera por hover/foco, no elevación artificial, rotación decorativa ni gradientes.

El bloque V10 al final de `web/v13.css` es la fuente de la presentación; `web/radar-hybrid.css` mantiene los tokens base. Al modificar estilos, comprobar valores computados de fondo, borde, radio, ausencia de sombra y contraste del botón lima en los tres navegadores.

## Sistema V9 — Contraste editorial por función, no monocromía

El fallo principal de las versiones anteriores era asignar un único color a toda la interfaz. En V9, se mantienen superficies neutras y se distingue **la función visual**, no se colorea cada panel.

- **Neutros**: fondo `#f8f9fb`, tarjetas blancas, tinta `#232831` y bordes suaves `#e2e6ec`.
- **Acciones y foco**: coral `#ad4b58`.
- **Últimas publicaciones y radar**: azul editorial `#326a9b`.
- **Temas, notas y noticias sin leer**: violeta `#7354a2`.
- **Guardadas y tendencias**: ámbar `#99631f`.
- **Categorías OPML**: IA violeta, tecnología azul, internacionales ámbar, Chile rojo, Venezuela cobre y Latinoamérica turquesa. La pertenencia se indica con iconos de carpeta y pequeñas etiquetas textuales de noticia, **nunca con líneas de color en los bordes de las tarjetas ni bandas superiores de las carpetas**.
- **Modo oscuro**: fondo grafito `#191d26`, superficie `#262c38`, tonos funcionales aclarados para legibilidad.
- **Semántica estable**: las seis categorías asignan `data-topic="1"…data-topic="6"` en navegación, tarjetas y carpeta de portada, por el orden de `state.categories`. No depender de coincidencias parciales de nombres.
- **Sin guía en Inicio**: “Empieza con Radar RSS” permanece fuera de portada; las herramientas están en Configuración → Lectura y filtros.

Regla V9.1: no añadir bordes cromáticos decorativos, barras coloreadas superiores ni puntos antes de los títulos de las secciones. Usar tipografía, fotografía y aire para jerarquizar.\n\nAl implementar nuevas características, reutilizar el rol semántico correspondiente y comprobar en navegador los seis colores calculados. Evitar variar el fondo de todas las secciones o reemplazar la identidad completa por un solo tono.

## Reglas visuales

- Tarjetas autónomas, proporcionadas, sin una primera tarjeta gigante ni contenedores duplicados.
- Imágenes de noticias **reales**. Si falta una fotografía, usar la cubierta tipográfica existente; nunca sustituirla por una fotografía ajena.
- Titulares legibles, extractos breves, metadatos secundarios y acciones en la parte inferior.
- Retícula fluida: tres columnas de portada en escritorio, dos en tabletas y una en móviles. Las tarjetas se igualan **por fila**, no mediante una altura global para todo el feed.
- Sombras discretas; la diferenciación entre leídas y no leídas debe seguir siendo perceptible.
- Mantener listas, tarjetas, fuente, fecha, búsqueda, carpetas, preferencias locales, guardadas, lectura, accesos táctiles y teclado.
- No utilizar la ocultación permanente de contenido para simular que las funciones no existen. Los controles secundarios deben tener un acceso claro y accesible.
- No añadir nuevos paneles, estadísticas, chips, ornamentos, degradados ni botones duplicados sin una necesidad de uso demostrable.
- Respetar claro/oscuro, alto contraste y `prefers-reduced-motion`.

## Propiedad de los estilos

El proyecto tiene CSS modular. **No fusionar todos los archivos en uno**: los módulos de características tienen responsabilidades propias.

| Archivo | Responsabilidad |
|---|---|
| `styles.css` | Tokens originales, componentes base y ajustes de compatibilidad. |
| `editorial.css` | Base tipográfica y superficie editorial. |
| `radar-hybrid.css` | Identidad de RadarRRS, barra lateral, cabecera y adaptaciones generales. |
| `ux.css` | Utilidades de interacción y navegación. No definir tamaños especiales de tarjetas de portada. |
| `features.css` | Radar informativo, tendencias, historial y herramientas específicas. |
| `v13.css` | **Definición final** de tarjetas uniformes, identidad visual V9 por rol y categoría, controles avanzados y portada responsive. |

Antes de añadir un selector, buscarlo en las hojas cargadas **después** del módulo actual. Modificar su regla canónica, en vez de crear más reglas al final de otro archivo. Evitar `!important` salvo una corrección de compatibilidad justificada.

## Contrato de verificación

Para publicar cualquier cambio visual:
- Ejecutar pruebas Python y JavaScript.
- Ejecutar `browser_tests/responsive_smoke.py` en Chromium, Firefox y WebKit, con anchos 320, 375, 390, 430, 768, 1024 y 1440 px.
- Verificar que Inicio muestra **En portada antes que el radar**, masthead neutro, sidebar claro y tarjetas de alturas uniformes por fila.
- Confirmar que `Más opciones` abre y cierra por ratón, teclado y Escape; que fecha, guardar búsqueda y marcar visibles funcionan y no tapan el listado.
- Confirmar la reversibilidad Lista ↔ Tarjetas también en móvil.
- Verificar Apariencia básica y su bloque avanzado, sin pérdida de preferencias.
- Revisar con datos reales del sitio publicado cuando esté accesible; las pruebas con datos sintéticos no sustituyen esta última comprobación.

Esta norma conserva el estilo editorial actual y evita la acumulación de revisiones visuales contradictorias.
