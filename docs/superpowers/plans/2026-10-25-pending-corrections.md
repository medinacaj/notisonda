# Correcciones pendientes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolver defectos confirmados de recuperación, lectura masiva y datos visibles del proyecto.

**Architecture:** Conservar los módulos actuales. Recuperación compara fechas conscientes de zona en UTC; lectura masiva reutiliza la carga de historial y su verificación. Sin cambios de servicios ni arquitectura.

**Tech Stack:** Python 3.12/unittest, JavaScript estático, Playwright HTTPS local y Actions.

**Spec:** docs/superpowers/specs/2026-10-25-pending-corrections-design.md

## Global Constraints

- Retención de 45 días y máximo5000 sin cambios; catálogo221/ocho carpetas.
- Sin dependencias/servicios nuevos ni red real en tests; preferencias locales.
- No modificar deploy.yml; trabajar en rama y revisar antes de integrar.
- No certificar pruebas físicas, cobertura exhaustiva ni licencias.

## Review Focus

- Instantes iguales con representaciones diferentes conservan la copia existente.
- Fechas sin zona, tipos incorrectos y extremos que desbordan UTC no validan un respaldo.
- Red caída conserva copia válida y falla si ninguna copia es verificable.
- Metadatos ausentes o historial de otra generación impiden marcas masivas parciales.
- Una carpeta seleccionada antes de completar el archivo incluye sus artículos archivados.

### Task 1: Recuperación cronológica segura

**Files:** scripts/recover_history.py; tests/test_history_recovery.py.
**Interfaces:** restore(Path) conserva su interfaz; entrada/salida articles.json y status.json.

- [ ] Crear pruebas de archivos reales con transporte HTTP simulado: offsets en ambos sentidos, equivalencias, fecha inválida con/sin caché, caché inválida recuperable y red caída.
- [ ] Ejecutar unittest dirigido. Expected: los casos de orden/validación nuevos fallan por selección incorrecta.
- [ ] Comparar fechas UTC conscientes de zona y validar caché/publicación; preservar fallo seguro sin copia verificable.
- [ ] Ejecutar suite Python completa. Expected: todas correctas.
- [ ] Commit de implementación y pruebas; registrar evidencia.

### Task 2: Marcas de lectura y coherencia del catálogo

**Files:** web/library.js, app.js, index.html, sw.js; browser_tests/count_regressions.py; sources/feeds.opml; GUIA_PUBLICACION.md; docs/project-status.md; pruebas existentes de versión de caché.
**Interfaces:** hasHistory/loadHistory/newsCountsComplete existentes; acción global y de carpeta esperan verificación antes de persistir radar-read.

- [ ] Añadir regresiones HTTPS de lectura masiva: metadata ausente sin cambios, recuperación seguida de lectura global completa, carpeta retenida hasta cargar sus artículos archivados.
- [ ] Ejecutar esas regresiones antes del cambio. Expected: marcas parciales300/38, distintas de cero.
- [ ] Reutilizar un guard de historial verificado en ambas acciones; carpeta conserva IDs seleccionados. Corregir aviso a tres horas.
- [ ] Aplicar título221/8 del PR92 y comprobar igualdad del cuerpo OPML. Actualizar documentación de estado y frecuencia sin certificar pendientes externos.
- [ ] Incrementar versiones de scripts/caché, adaptar aserciones existentes de caché.
- [ ] Ejecutar Python, Node, sintaxis, suite HTTPS de contadores y smoke Chromium; Expected: todos correctos.
- [ ] Commit y revisión independiente del diff completo. Corregir hallazgos importantes con RED→GREEN.
- [ ] Crear PR, verificar CI del head exacto, integrar bajo autorización vigente y verificar despliegue público.
