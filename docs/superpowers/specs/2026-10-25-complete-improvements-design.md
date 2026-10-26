# Completar lectura y agenda

Petición autorizada: completar las mejoras/correcciones pendientes de Claude sobre el main vigente b320d0a; el usuario delegó las decisiones de implementación y publicación. Se adapta el código útil de PR78/88 a este main, conservando las mejoras publicadas.

## Lectura
Filtros activos eliminables y panel móvil; limpiar filtros conserva preferencias globales. Estados vacíos permiten recuperarse sin afirmar ausencia de resultados si falla el archivo. Lector Anterior/Siguiente, no leída, teclado y retorno de foco/posición. Marcas masivas mantienen el guard de archivo completo y ofrecen Deshacer durante8s sin borrar acciones posteriores. Nuevas publicaciones quedan preparadas y se aplican con Mostrar noticias; actualizar metadata de misma generación sigue reparando cargas fallidas. Se conservan exclusión/abort de historial, generación y conteos estrictos.

## Agenda única
Conservar events.json v1, fechas explícitas, días locales hasta fin, pending separado, conservación independiente de noticias, cache/backup/generación y CL/VE. Recuperar fuentes y capacidad HTML/JSON-LD/ICS del PR88 mediante adaptador seguro y acotado con configuración opt-in; no importar seeds vencidos ni snapshots sin evidencia. UI lista/calendario mensual, filtros de zona/búsqueda/localidad/tipo/precio conocidos, guardadas locales vigentes, compartir y .ics sin inventar fechas. Metadata opcional legacy compatible: locality/event_type/price_text string<=200|null, is_free boolean|null, preference_source_id string<=128|null; evidence.kind admite calendar. Ocultamiento considera ID y parent. Preferencias agenda locales {version:1,saved:[IDs<=128 hasta1000],view:list|calendar}, exportables/restaurables por API validada.

## Límites y responsabilidades
Root posee lector, integración, index/cache/workflows, respaldo y documentación. Agente backend posee scripts/events.py, collect_events.py, event_sources.py, sources/events-direct.json y pruebas backend. Agente UI posee agenda.js/css y agenda_tools_regressions.py. Sin ediciones de archivos compartidos ni commits de agentes. Sin servicios/dependencias nuevas ni eliminación de repositorios/ramas. Fuentes públicas oficiales justificadas por agenda; consultas de producción sólo con HTTPS público, robots/hosts/tamaño/tiempo/presupuestos y atribución. No afirmar licencias, disponibilidad futura o pruebas físicas. Retención noticias45d/5000 y catálogo221/ocho carpetas se conservan.

## Verificación
TDD de comportamientos con JSON/HTML/ICS controlados; suites Python/Node; browser HTTPS en tres motores y375/1440, smoke siete anchos; respaldo v2/v3, filtros, foco, deshacer, publicaciones preparadas e historial antiguo, cancelados/pendientes/calendario/ICS. Revisión independiente del diff final; CI head exacto, merge autorizado y verificación pública. Validación física/curación requieren evidencia real, no se simulan como hechas.
