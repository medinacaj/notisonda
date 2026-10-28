# Configuración y gestión de fuentes

## Objetivo y decisiones
Corregir discordancias comprobadas en Configuración y hacer útil el catálogo como gestor RSS: direcciones visibles, búsqueda, diagnóstico, carpetas personales y portabilidad OPML. El usuario delegó anteriormente ejecutar las recomendaciones; se continúa con JavaScript estático y almacenamiento local, sin volver a pedir aprobación de diseño.

Se consideró mostrar solo enlaces en el diálogo existente (no resuelve búsqueda/carpetas/exportación), ampliar el gestor actual (elegido por el implementador) o añadir un servicio de suscripciones/sincronización (requiere nueva arquitectura y queda fuera). Feedly es referencia funcional; no se integra su API ni se promete paridad con todos sus planes.

## Hechos de partida
- Las 311 fuentes ya contienen `url` y `website`; la lista solo muestra nombre/categoría y esconde enlaces en un diálogo sin affordance evidente.
- `decorateSources` identifica por nombre/categoría en vez de ID; nombres coincidentes pueden gestionar el registro equivocado.
- Los botones de categoría capturan un conteo antiguo tras cambiar una casilla y desconocen carpetas personales; OPML exporta categorías originales, no la organización personal.
- Carpetas guardadas se truncan a 160 fuentes al recargar aunque la UI permita más; restablecer preferencias omite el modo ligero.

## Resultado esperado
- Lista accesible con nombre, carpeta actual/original, tipo RSS directo o RADAR Google, estado del último chequeo, URL RSS y web legibles/enlazadas y copiar RSS. Los RSS largos muestran hasta tres líneas, con dirección completa en destino, tooltip, Detalles y copia; la categoría original se muestra en lista cuando difiere de su carpeta, evitando repetición. IDs estables; enlaces nunca cambian la casilla.
- Búsqueda por nombre, categoría, carpeta, dominio y URL; filtros combinables de visibilidad, estado y tipo. Vacío explícito. Totales distinguen visibles, catálogo y resultados, no confunden ocultación personal con fallo del servidor.
- Botones por carpeta actual con conteos actualizados. Selector de movimiento funciona incluso con nombres iguales. Detalles y acceso a noticias de una fuente.
- Exportación OPML de fuentes visibles con nombres y pertenencias personales, incluyendo sin carpeta; CSV del catálogo completo con URL/ID/tipo/carpeta/visibilidad/estado. Valores CSV se neutralizan contra fórmulas.
- Importación OPML local con previa, límites (1 MB/1000 entradas/25 carpetas/45 caracteres), sin DTD ni entidades. Empareja URL exacta normalizada (sin fragmento, sin reordenar parámetros ni cambiar http/https), nunca solo dominio/nombre; duplicados se cuentan y no se añaden de nuevo. Restaura carpetas/activa fuentes reconocidas al confirmar, conserva organización y suscripciones restantes. Desconocidas/URL inseguras se informan; no se convierten en falsas suscripciones ni se consultan sitios arbitrarios. Se puede descargar informe. Cancelar no cambia datos. Un fallo de almacenamiento no deja estado parcial.
- Corregir pérdida de >160 fuentes por carpeta y reinicio de modo ligero. Aclarar alcance local, archivo disponible (45 días/hasta 5000) y preferencias de lectura sin borrar guardadas/leídas/etiquetas.
- Mantener claro/oscuro, texto grande, teclado, foco y 320 px sin desbordamiento. Versionar assets/caché.

## Límites y controles
No cambiar las 311 fuentes, recopilación, deduplicación, rutas, datos publicados, retención ni workflows. Sin dependencias, cuentas, sincronización, telemetría ni IA remota. El estado procede del último JSON publicado, no de una comprobación en vivo. Noticias/corpus no equivalen a completitud ni veracidad. OPML/CSV/JSON los descarga voluntariamente el lector; importación no envía archivos a terceros. Enlaces http(s) sin credenciales, `noopener noreferrer`, texto por DOM. Se mantienen atribución y extractos; no se afirma cumplimiento legal ni licencias nuevas. Contexto público internacional/Chile/Venezuela; preferencias locales, sin nueva jurisdicción/proveedor.
