# Actualización manual y estilo — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Dar una respuesta útil al actualizar noticias y modernizar los controles en ambos temas.

**Architecture:** Mantener la aplicación estática y el estado actual. Diferenciar comprobaciones manuales de automáticas en `app.js`; exigir red en el service worker cuando la petición usa `no-store`. Consolidar tokens y controles en la capa activa `dimension.css`.

**Tech Stack:** JavaScript y CSS sin dependencias nuevas; Node, unittest y Playwright existentes.

**Spec:** `docs/superpowers/specs/2026-10-29-actualizacion-estilo-design.md`.

## Global Constraints

- Conservar las 311 fuentes, las 8 carpetas y las preferencias/formatos existentes.
- Automática cada 15 minutos; recopilación cada tres horas, sin cambiar workflows.
- Tiempo máximo de comprobación 15 segundos; mantener filtros, lector y posición.
- Conservar la marca pequeña, alineación común y controles de artículo de 44 px.
- Sin fuentes remotas, servicios ni dependencias nuevas.

## Review Focus

- Carga inicial fallida: el botón debe recuperar un lote coherente sin recargar la página.
- Sin conexión con caché: no anunciar una comprobación exitosa de datos antiguos.
- Publicación pendiente y fallo posterior: conservar el lote válido y la lectura actual.
- Red que no responde o clics repetidos: liberar el botón sin duplicar peticiones.
- Temas, selección y lateral estrecho: contraste legible y sin desbordamiento.

### Task 1: Corregir actualización manual

**Files:** `web/app.js`, `web/index.html`, `web/sw.js`, `tests/test_reading_state.cjs`, `tests/test_cache_migration.cjs`, `browser_tests/dimension_regressions.py`.

**Interfaces:** `refreshPublishedData({manual=false}={})`, `dataFetch(path,{signal,fresh}={})`; `refreshStatus` anuncia resultado, `refreshNow` expone progreso. La llamada automática sin argumentos conserva la publicación pendiente.

- [x] Reproducir en navegador y escribir pruebas: aplicación manual inmediata; resultado sin novedades; error/reintento; carga inicial fallida; lote pendiente; tiempo de espera; caché manual sin red.
- [x] Ejecutar las nuevas pruebas y comprobar fallos por los comportamientos descritos.
- [x] Implementar intención manual, progreso/resultado accesibles, cancelación por tiempo y validación coherente. Mantener la automática y sus contratos.
- [x] Ejecutar pruebas Node y comprobar clic real con publicaciones simuladas, sin consultar medios externos.
- [x] Guardar versiones de assets/caché y commit de la corrección.

### Task 2: Renovar colores y botones

**Files:** `web/dimension.css`, `web/index.html`, `web/sw.js`, `browser_tests/dimension_regressions.py`.

**Interfaces:** Tokens existentes `--bg`, `--surface`, `--text`, `--accent`, `--action-lime`, `--action-ink`; mismos IDs y clases funcionales. El control de actualización de Task 1 usa esta apariencia.

- [x] Capturar estado anterior. Consolidar paleta marfil/grafito/violeta y sustituir colores fijos del lateral por tokens del tema.
- [x] Simplificar botones principales/secundarios/iconos, selección y foco; preservar controles de artículo y bordes discretos de tarjetas.
- [x] Comprobar contraste de controles y categorías en ambos temas, teclado, movimiento reducido y alineaciones existentes; inspeccionar capturas de escritorio y móvil.
- [ ] Ejecutar batería Python/Node y navegadores pertinentes. Revisión independiente final del diff completo, corregir hallazgos importantes y ejecutar sus regresiones.
- [ ] Crear PR, comprobar CI del commit exacto e integrar/publicar dentro de la autorización persistente; verificar assets, clic manual y catálogo en la web pública.
