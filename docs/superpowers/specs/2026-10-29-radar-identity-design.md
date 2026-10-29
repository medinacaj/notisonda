# Volver a Radar-RSS

El usuario devuelve el nombre del sistema a **Radar-RSS**. La identidad debe ser coherente en cabecera, título, metadatos, aplicación instalada, textos, resúmenes y descargas. El repositorio ya fue renombrado externamente a `medinacaj/radar-rss`: GitHub y solicitudes HTTP confirman `/radar-rss/` como ruta vigente y 404 en `/notisonda/`. La recuperación y el monitor deben usar la ruta vigente.

Se mantienen fuentes, IDs, carpetas, preferencias, guardados, claves de almacenamiento, formato de respaldos y UID de calendarios. No se cambian estilos ni funciones del lector. Los PR #120 y #121 de fuentes quedan separados y sin publicar según la indicación del usuario.

Se reutilizan los PNG históricos de RSS y se recuperan los SVG RSS anteriores bajo nombres nuevos, sin redibujar ni modificar las imágenes existentes. Los SVG y PNG de Notisonda se conservan. El PNG social histórico conserva su composición; el nombre canónico en HTML y manifest es Radar-RSS. El icono Apple reutiliza el PNG RSS de 192 píxeles, con su tamaño real declarado.

Se consideran un reemplazo de texto indiscriminado, rediseñar marca y sitio o cambiar únicamente identidad activa y URL comprobada. Se elige la última opción: evita modificar esquemas e historia, restaura RSS reconocible y mantiene el estilo actual. El service worker renueva su caché conservando migración y comportamiento offline/manual.
