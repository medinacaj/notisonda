# Completar mejoras de lectura y agenda

Base b320d0a; rama feat/completar-lectura-y-eventos. Spec: ../specs/2026-10-25-complete-improvements-design.md. Ejecución coordinada: root implementa lector/integración; dispatching-parallel-agents para backend/UI de agenda con archivos exclusivos; una revisión final independiente.

- [x] Root: portar regresiones del lector, observar RED de ausencia de filtros/navegación/undo/staging; adaptar módulos y callbacks al main actual sin perder conteos/guards.
- [x] Backend: tests RED/GREEN de opcionales/ICS/direct HTML, seguridad/robots/presupuestos, opt-in CLI y preservación de cache.
- [x] UI agenda: pruebas HTTPS RED/GREEN de calendario/filtros/guardadas/ICS, opcionales y generación, manteniendo contratos existentes.
- [x] Root: unir APIs de preferencias al respaldo validado y reset; index/cache/versiones, workflow y documentación.
- [x] Ejecutar Python/Node y browsers HTTPS, revisar diffs independientes y corregir hallazgos con regresión.
- [ ] PR/CI del head exacto, integrar/publicar y verificar generación pública. Cerrar propuestas sólo cuando su capacidad útil esté incorporada y probada.

Riesgos: publicaciones mezcladas y descargas antiguas, foco móvil, undo tras importación/reset, zona/fin ICS, source parent oculto, datos opcionales inválidos, fuentes sin datos y fallos parciales. No generar eventos ficticios ni trasladar snapshots ambiguos como confirmados.

## Evidencia local y revisión independiente (2026-10-26)

256 pruebas Python pasan sin fuentes reales. Node: sidebar, efectos RSS, chips/filtros, 14 casos de lector y 13 de publicación/Deshacer/histórico. Chromium HTTPS: smoke de siete anchos320–1440, lector en cuatro anchos, 14 regresiones de contadores, 12 de agenda y nueve de respaldo/importación. Firefox/WebKit se verifican en la matriz CI; la política de este entorno bloquea sus descargas y no se declara ejecución local.

Revisión independiente backend y frontend detectó siete P2: fin ICS exclusivo con hora, cancelación UID sin título, precio contradictorio recuperado como gratis (incluida recuperación desde snapshot), identidades JSON-LD relativas, reprogramación descartada al conservar UID, pérdida de clic al cerrar detalles en pointerdown y bloqueo del reset por cuota de almacenamiento. Reproducciones RED observadas antes de corregir, regresiones GREEN después; revisión dirigida corrobora las correcciones. Se conserva la identidad de distintos UID y la antigüedad de datos sólo cuando no contradice evidencia nueva.

Datos: preferencias locales sin nuevos terceros ni sincronización; exportación/borrado manual y compatibilidad v2/v3. Fuentes públicas CL/VE con atribución y hosts registrados; no se afirman licencias, disponibilidad exhaustiva ni certificación legal. Riesgo → evidencia → control → prueba → responsable → estado: fechas/precios erróneos → contradicciones entre formatos/caché → precedencia conservadora/fechas locales/evidencia explícita → regresiones85+recuperación → implementador/revisión independiente → cubierto localmente; disponibilidad real de fuentes y despliegue se comprueban tras CI.
