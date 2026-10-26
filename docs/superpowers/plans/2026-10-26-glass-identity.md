# Identidad cristal — Implementation Plan

> For agentic workers: ejecutar con superpowers:executing-plans en el checkout actual, respetando la preferencia previa por una rama sin otro worktree. Revisión independiente al final según AGENTS.md.

**Goal:** Logo original, iconos coherentes y tarjetas con relieve, color y respuesta animada.
**Architecture:** HTML/JS estático existente, una sola capa dimension.css, activo local y shell offline actualizado. Sin cambios de datos o dependencias.
**Tech Stack:** HTML, CSS, JavaScript; Playwright para verificación.
**Spec:** docs/superpowers/specs/2026-10-26-glass-identity-design.md

## Global Constraints
- Preservar ocho categorías, contraste seleccionado>=4.5 en claro/oscuro, destinos y lector.
- Respetar reduced-motion, colores forzados y tamaños320–1440.
- No crear otra hoja de tema ni servicios/dependencias de producción.

## Review Focus
- Ratón, teclado y toque conservan activación sin capas decorativas que intercepten controles.
- Reducir movimiento también desactiva reglas nuevas situadas al final de la cascada.
- Carpetas manuales y categorías desconocidas tienen un icono de respaldo.
- El logo se sirve y recupera offline desde una ruta local sin nuevas conexiones.
- Sombras y transformaciones no crean desbordes ni alteran altura de las filas.

### Task 1: Marca e iconos
Files: web/index.html, web/app.js, web/radar-logo.png, web/favicon.svg, web/manifest.webmanifest, web/sw.js; browser_tests/dimension_regressions.py.
Interfaces: svgIcon(name) preserva su API; CATEGORY_ICONS añade las dos localidades; HTML conserva dashboardTitle/dimensionEdition.
- [x] Comprobar símbolos de las ocho carpetas y carpeta manual, cargar logo y conservar accesibilidad.
- [x] Integrar logo generado, encabezado «Actualidad», símbolos propios y recursos offline/versionados.

### Task 2: Cristal e interacción
Files: web/dimension.css; browser_tests/dimension_regressions.py.
Interfaces: usar :focus-within/:active/:hover, sin estado JS añadido.
- [x] Regresión RED de relieve y foco en tarjeta, conservar funciones de guardar/leer.
- [x] Aplicar relieve, bordes degradados, iconos con color y animaciones breves/aurora.
- [ ] Verificar GREEN, reduced-motion sin animación y colores forzados con foco/borde.
- [ ] Verificar capturas claro/oscuro390/1440, responsive y regresiones de lectura/agenda.

### Task 3: Entrega
Files: README.md, docs/architecture.md, docs/project-status.md, tests/test_dimension_theme.py.
- [ ] Actualizar documentación/cache, ejecutar251Python y suites Node pertinentes.
- [ ] Revisar diff independiente y resolver hallazgos importantes con regresión.
- [ ] PR y CI3motores, integrar con autorización vigente, verificar Pages y árbol publicado.
