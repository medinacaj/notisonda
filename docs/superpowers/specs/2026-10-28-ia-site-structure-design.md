# IA en español y estructura de lectura

El usuario pide ampliar RSS/Atom de IA en español, investigación, revistas, eventos y lanzamientos, conservar todas las fuentes/preferencias, informar altas y feeds no válidos, y ordenar el sitio. Autoriza ejecutar la recomendación; se mantiene el método nativo y una revisión independiente final.

## Contexto y decisión
Se integró main b71f512 (PR102–110) antes de trabajar: 248 canales y ajustes recientes de tarjetas, menús y radar. La ampliación pendiente aporta otros23:271 canales sin bajas. Xataka/Genbeta/WWWhat's New, SINC, MIT español intermediado y búsquedas científicas ya existen; no se vuelven a añadir.

Se consideró añadir todos los RSS generales de cada medio, que duplica tráfico y diluye IA; reemplazar los canales antiguos, que incumple la conservación; o añadir solo huecos temáticos y conservar lo existente. Se elige la última. Los nuevos portales españoles se incorporan mediante RSS de Google Noticias observados, rotulados RADAR; los feeds editoriales directos bloqueados por la red quedan pendientes de comprobación, nunca declarados inexistentes por ese motivo. Los índices y las fechas RSS no demuestran la fecha real ni veracidad de un artículo. Las búsquedas no proporcionan el texto completo de papers ni confirman fechas de eventos en Agenda.

## Estructura
Inicio tendrá un encabezado breve, un destacado, un carrusel sin repetir esos artículos, radar/cobertura/tendencias y novedades condicionales. Se retiran contenedores ocultos de diseños previos y sus renderizadores; las carpetas permanecen en el lateral y Guardadas en Noticias. Noticias conserva archivo, controles y filtros; Agenda y Resumen conservan sus rutas y fines. No se oculta el radar de nuevo.

La estructura se escribe directamente en HTML, sin mover paneles al arrancar. Alineación, títulos y espacios coherentes en ambas apariencias y móvil. Se corrige la regresión reproducida donde el ajuste independiente de títulos impide que Texto grande aumente los titulares de Inicio/Noticias. Se preserva el tamaño elegido y su respaldo.

## Límites y aceptación
Sin cambios al colector, deduplicación, retención, agendas, frecuencia o dependencias. Sin traducción automática ni sustitución de fuentes inglesas anteriores. Misma privacidad local, atribución y enlaces; acceso RSS no acredita licencias ni certificación legal. Medios principalmente españoles/latinoamericanos, Google como intermediario. Las 248 fuentes de main y23 pendientes conservan IDs, nombres, URLs y categorías. Feeds nuevos sin duplicados exactos, HTTP200/XML con entradas fechadas observadas, cobertura en español, registro temporal y límites explícitos. Pruebas offline, navegación/teclado/lectura/responsive y verificación de publicación antes de afirmar publicada.
