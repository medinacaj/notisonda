# RadarRRS — Sistema editorial V7 · Neutro

## Objetivo de producto
RadarRRS es un **portal público de noticias** y un lector de fuentes RSS, no un panel técnico. Deben verse primero las noticias. Las herramientas avanzadas se muestran a demanda.

## Jerarquía fija

1. Inicio: encabezado breve, noticias **En portada**, **Últimas publicaciones**, guardadas si las hay, las seis carpetas OPML y luego el radar y las tendencias como análisis secundario.
2. Listado: título, pestañas Todas / Sin leer / Guardadas, filtro por fuente, vista y **Más opciones**. El buscador permanece en la cabecera.
3. Más opciones: antigüedad, guardar búsqueda y marcar noticias visibles como leídas. El menú se expande **en flujo**, no flotando sobre los resultados.
4. Configuración > Apariencia: tema, tamaño de letra, imágenes y resúmenes como opciones principales. Columnas, espaciado, formato, panel lateral e inicio decorativo se encuentran en un bloque plegable.

## Sistema V7 — Editorial neutro de bajo cansancio visual

Se elimina la identidad de bloques azul noche y cian de V6. La interfaz debe producir contraste con la **tipografía, tamaños, espacios y fotografías**, no con fondos fuertes.

- **Paleta clara**: fondo `#f7f7f5`, superficies `#fff`, texto principal `#1f2424`, secundarios `#646d6b`, líneas `#e1e5e1`.
- **Acento único y moderado**: petróleo `#1f5e5b`, reservado para enlaces, controles activos, navegación seleccionada y estados de foco.
- **Oscuro accesible**: fondo `#181c1a`, superficie `#242a27`, texto `#f0f2ef`, acento `#87ccba`.
- **Navegación**: superficie gris humo claro, sin bloque de color; elemento activo blanco, borde fino y línea lateral petróleo.
- **Cabecera**: blanca, con buscador suave y controles secundarios discretos.
- **Portada**: encabezado sin color de fondo ni gradiente; título editorial de tinta oscura y divisor fuerte.
- **Tarjetas**: superficie blanca, sombra fina, fotografía protagonista y título editorial legible. Las leídas y no leídas se distinguen sin recurrir a grandes masas cromáticas.
- **Contraste visual**: cambios de peso, alineación y densidad; no repetir el color de acento en cada contenedor.
- **Móvil**: sidebar tipo cajón, una columna y controles avanzados plegados. Se conservan carpeta, búsqueda, fecha, vista lista, lectura y preferencias.

No restaurar la banda azul saturada, ni cambiar de nuevo toda la interfaz a un único color llamativo. Los acentos deben permanecer localizados.

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
| `v13.css` | **Definición final** de tarjetas uniformes, identidad visual V7 neutra, controles avanzados y portada responsive. |

Antes de añadir un selector, buscarlo en las hojas cargadas **después** del módulo actual. Modificar su regla canónica, en vez de crear más reglas al final de otro archivo. Evitar `!important` salvo una corrección de compatibilidad justificada.

## Contrato de verificación

Para publicar cualquier cambio visual:
- Ejecutar pruebas Python y JavaScript.
- Ejecutar `browser_tests/responsive_smoke.py` en Chromium, Firefox y WebKit, con anchos 320, 375, 390, 430, 768, 1024 y 1440 px.
- Verificar que Inicio muestra **En portada antes que el radar**, masthead neutro, sidebar gris claro y tarjetas de alturas uniformes por fila.
- Confirmar que `Más opciones` abre y cierra por ratón, teclado y Escape; que fecha, guardar búsqueda y marcar visibles funcionan y no tapan el listado.
- Confirmar la reversibilidad Lista ↔ Tarjetas también en móvil.
- Verificar Apariencia básica y su bloque avanzado, sin pérdida de preferencias.
- Revisar con datos reales del sitio publicado cuando esté accesible; las pruebas con datos sintéticos no sustituyen esta última comprobación.

Esta norma conserva el estilo editorial actual y evita la acumulación de revisiones visuales contradictorias.
