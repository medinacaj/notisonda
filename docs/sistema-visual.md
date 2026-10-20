# RadarRRS — Sistema editorial V6 · Nueva identidad

## Objetivo de producto
RadarRRS es un **portal público de noticias** y un lector de fuentes RSS, no un panel técnico. Deben verse primero las noticias. Las herramientas avanzadas se muestran a demanda.

## Jerarquía fija

1. Inicio: encabezado breve, noticias **En portada**, **Últimas publicaciones**, guardadas si las hay, las seis carpetas OPML y luego el radar y las tendencias como análisis secundario.
2. Listado: título, pestañas Todas / Sin leer / Guardadas, filtro por fuente, vista y **Más opciones**. El buscador permanece en la cabecera.
3. Más opciones: antigüedad, guardar búsqueda y marcar noticias visibles como leídas. El menú se expande **en flujo**, no flotando sobre los resultados.
4. Configuración > Apariencia: tema, tamaño de letra, imágenes y resúmenes como opciones principales. Columnas, espaciado, formato, panel lateral e inicio decorativo se encuentran en un bloque plegable.

## Identidad nueva y verificable

Este rediseño sustituye la apariencia naranja/gris y el fondo blanco uniforme de V5.4.

- **Barra de navegación:** azul noche `#102641`, con selección verde agua `#67decc`.
- **Marca RSS:** fondo azul noche y símbolo verde agua.
- **Superficie general:** azul hielo `#f2f6fb`, tarjetas blancas independientes y sombra suave.
- **Titulares:** tipografía editorial serif y jerarquía diferenciada.
- **Encabezado de portada:** banda azul con titular y texto breve, sin ilustración ni gráficos adicionales.
- **Modo oscuro:** azul profundo `#0b1525` con superficies azul pizarra `#14243b`.
- **Densidad:** imágenes de feed hasta 148 px, compacto 96 px, cubiertas sin foto 70 px; ningún resultado desaparece por falta de imagen.
- **Mantener:** mismas seis carpetas OPML, filtros, guardadas, búsqueda, menú contextual, lista, cuadrícula y personalización del panel.

El nuevo diseño vive en las variables de `radar-hybrid.css` y en la capa canónica `v13.css`. No deben añadirse más temas paralelos ni reutilizar los colores naranjas anteriores.

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
| `v13.css` | **Definición final** de tarjetas uniformes, identidad visual V6, controles avanzados y portada responsive. |

Antes de añadir un selector, buscarlo en las hojas cargadas **después** del módulo actual. Modificar su regla canónica, en vez de crear más reglas al final de otro archivo. Evitar `!important` salvo una corrección de compatibilidad justificada.

## Contrato de verificación

Para publicar cualquier cambio visual:
- Ejecutar pruebas Python y JavaScript.
- Ejecutar `browser_tests/responsive_smoke.py` en Chromium, Firefox y WebKit, con anchos 320, 375, 390, 430, 768, 1024 y 1440 px.
- Verificar que Inicio muestra **En portada antes que el radar**, masthead azul, sidebar azul noche y tarjetas de alturas uniformes por fila.
- Confirmar que `Más opciones` abre y cierra por ratón, teclado y Escape; que fecha, guardar búsqueda y marcar visibles funcionan y no tapan el listado.
- Confirmar la reversibilidad Lista ↔ Tarjetas también en móvil.
- Verificar Apariencia básica y su bloque avanzado, sin pérdida de preferencias.
- Revisar con datos reales del sitio publicado cuando esté accesible; las pruebas con datos sintéticos no sustituyen esta última comprobación.

Esta norma conserva el estilo editorial actual y evita la acumulación de revisiones visuales contradictorias.
