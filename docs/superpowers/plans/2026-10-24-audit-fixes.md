# Correcciones de auditoría y Concepción

Objetivo autorizado: integrar el respaldo Concepción y corregir los ocho defectos reproducidos en la auditoría del 24 de octubre. Mantener arquitectura estática, preferencias locales y diseño editorial actual. Recuperar selectivamente mejoras útiles V1.4; no sustituir main por una rama antigua.

Criterios de aceptación: 211 fuentes con las 178 originales intactas; selecciones parciales de Mi Radar completan el grupo; búsquedas restauran exactamente su ámbito; respaldo restaura preferencias y búsquedas sin recarga; fragmentos inválidos no interrumpen navegación; retención conserva alternativas; cobertura cuenta editores; verificación pública compara generación esperada; reset usa default consistente.

Archivos: catálogo/documentación/tests del ZIP; app/library/v12/features para interacción y persistencia; collect/insights para integridad editorial; check_pages/deploy para generación esperada; tests y smoke browser para regresiones.

- [x] Aplicar el ZIP en rama separada del main.
- [x] Tests de regresión fallan con comportamiento auditado y pasan con correcciones.
- [x] Corregir ingesta, backup/navegación, selección/restauración regional y verificador.
- [x] Recuperar cubierta clicable, filtros vacíos ocultos, ayuda de acciones, nombres legibles y mapa opcional sin duplicar controles existentes.
- [x] Ejecutar suite Python/Node y Chromium completo y dirigido; revisión independiente del diff.
- [x] Guardar evidencia y commit local; no desplegar ni fusionar main.

Riesgos a comprobar: respaldos v2/v3 y entradas malformadas, categorías solapadas, varias consultas mismo editor, actualización parcial de feeds y generación pública anterior. No añadir dependencias de producción ni consultar RSS reales en pruebas. Chile es el ámbito de las fuentes Concepción; disponibilidad y licencias individuales no quedan certificadas por esta implementación.
