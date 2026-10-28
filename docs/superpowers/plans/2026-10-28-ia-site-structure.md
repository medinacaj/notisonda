# Ampliar IA en español y ordenar el sitio

Diseño: docs/superpowers/specs/2026-10-28-ia-site-structure-design.md. Método nativo, checkout existente/rama feat/fuentes-verificadas-espanol/PR111. El usuario autoriza continuar; no se reinicia una ronda de diseño. Ledger: /workspace/scratch/ai-structure/progress.md.

## Task1 — Catálogo y evidencia
- Integrar main b71f512 conservando27altas remotas y23pendientes; no modificar la configuración antigua para obtener nuevas IDs.
- Seleccionar huecos observados en español: Hipertextual IA, WIRED español IA, CSIC investigación IA, Think Big IA y Retina análisis. No duplicar Xataka, Genbeta, WWWhat's New, SINC ni las4búsquedas temáticas existentes.
- Registrar fecha/HTTP/hash/formato/entradas/muestras de RSS observados y fuentes existentes revalidadas; distinguir la restricción de red de RSS inválido/vacío.
- OPML, JSON y documentación concuerdan; contratos offline conservan original248/221/211 y registran los nuevos sin duplicados.
- Verificación: auditoría sin problemas y contratos de catálogo GREEN.

## Task2 — Estructura directa y lectura
- HTML de Inicio: encabezado corto, novedades, destacado, carrusel, cobertura/radar/tendencias; eliminar wrappers y paneles ocultos obsoletos.
- app.js renderiza una sola selección de1+7; homepage.js controla únicamente carrusel, sin reparenting. Eliminar renderizadores de paneles retirados en library/v12 y listeners asociados. Mantener rutas/preferencias, elegibilidad por fuentes/tema y radar visible.
- Retocar dimension.css existente (sin otra hoja de tema) para jerarquía y alineación; corregir interacción de Texto grande y tamaño independiente de titulares sin cambiar el valor guardado. Actualizar caché/versiones de recursos.
- Actualizar contratos estructurales anteriores para el nuevo HTML y verificar en navegador orden directo sin JS de traslado, selección única, sin estados vacíos duplicados, rutas/menú/lector, fuentes ocultas y preferencias, tamaños320–1440/temas/texto grande.
- Verificación: Python completo/Node y suites de navegador pertinentes. Reproducir primero regresiones funcionales y verificar RED→GREEN.

## Task3 — Integración y publicación
- Revisión independiente del diff final contra main b71f512 (la revisión inicial de23altas está registrada por separado).
- Resolver hallazgos importantes con prueba funcional RED→GREEN; CI del SHA final; integrar conservando posibles cambios remotos; publicar y verificar el snapshot generado.
- Informar altas reales, canales ya existentes, intermediarios y límites pendientes de acceso sin confundirlos con RSS inválidos.

## Review Focus
- Conservación de cada fuente y preferencia previa;271→total exacto/IDs originales sin duplicar feeds ni carpetas.
- RSS observado no equivale a artículo verificado; campos no comprobados permanecen nulos; XML/fecha/idioma/publisher frente a índices o autorías.
- Inicio funciona con0/1/múltiples artículos y filtros; no depende de contenedores retirados ni crea duplicados en destacado/carrusel.
- Texto grande aumenta titulares con tamaños independientes14–22, se conserva al recargar/importar; sin desbordamiento móvil ni pérdida del foco.
- Radar sigue visible, cobertura/tendencias en Inicio, noticias y actividades mantienen rutas y fechas separadas.
