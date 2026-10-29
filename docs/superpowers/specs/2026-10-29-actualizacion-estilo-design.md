# Actualización manual y estilo de Notisonda

El usuario pide corregir el botón de actualizar noticias y reemplazar los colores y botones por un estilo moderno. Ha delegado las decisiones de diseño durante esta sesión; se continúa sin otra ronda de aprobación.

La comprobación actual comparte la ruta automática: no informa cuando no hay novedades o falla la red, prepara una publicación sin aplicarla y no permite recuperar una carga inicial fallida. La página es estática: el botón consulta lo ya publicado, mientras la recopilación de medios conserva su intervalo de tres horas.

## Decisión

Separar la intención manual de la automática. Al pulsar Actualizar, mostrar progreso, aplicar un lote nuevo coherente, anunciar el resultado y permitir reintentar tras fallos o un tiempo de espera de 15 segundos. Una petición manual debe exigir red, sin presentar una copia sin conexión como una comprobación reciente. La automática conserva el aviso Mostrar noticias y no interrumpe la lectura.

Se consideraron conservar la respuesta silenciosa, recargar toda la página o actualizar el estado existente. Se elige actualizar el estado para mantener filtros, preferencias, lector y posición. No se añaden servicios, credenciales ni acceso directo a los RSS desde el navegador.

La elección visual del implementador es marfil en claro, grafito en oscuro y violeta para las acciones principales. Navegación y lectura comparten el tema; se elimina el lateral azul fijo. Botones de esquinas suaves, sombras discretas, controles secundarios neutros y selección/foco reconocibles. Se conservan los ocho colores de categoría, la marca pequeña, las alineaciones y los tamaños de texto existentes. Se comprueba contraste, teclado, movimiento reducido y anchuras de 320 a 2560 px.

Fuentes, carpetas, datos, identificadores de respaldo y calendario, y automatización de publicación quedan preservados. No se certifican dispositivos físicos ni vistas previas de redes sociales.
