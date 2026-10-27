# Identidad y lectura cómoda — Implementation Plan

> Ejecución nativa con superpowers:executing-plans; rama del checkout actual, revisión independiente final según AGENTS.md.

**Goal:** Sustituir la marca ambigua y facilitar la lectura con color, contraste, tipografía y efectos moderados.
**Architecture:** Tokens y componentes en la única capa dimension.css; preferencias existentes de app.js/library.js; activos de marca e index/manifest/SW sincronizados.
**Tech Stack:** HTML/CSS/JS estático, Python/Node y Playwright.
**Spec:** docs/superpowers/specs/2026-10-27-reading-comfort-design.md

## Global Constraints
- Logo único24px/cabecera mínima; cuatro destinos y ocho colores de categoría.
- Sin dependencias, servicios, preferencias nuevas, recolector ni fuentes nuevas.
- Auto mínimo280px/320px con texto grande; conservar columnas elegidas; entradas móviles16px y acciones44px.
- Texto normal>=4.5:1 y principal>=7:1; reduced-motion/forced-colors; sin promesa médica.

## Review Focus
- Preferencias/respaldo anteriores con columnas explícitas siguen respetándose; restablecer vuelve a Auto.
- Texto grande funciona en cada ruta, incluido lector/Agenda con botones y títulos largos.
- Tarjetas leídas, tintes de categorías, metadatos y placeholders mantienen contraste en claro y oscuro.
- Sidebar abierto, redimensionado o cerrado: Auto responde al contenedor; ancho320 no produce desbordes.
- Foco visible no se recorta y los controles siguen accesibles con teclado/reduced-motion/forced-colors.

### Task1: marca y comodidad de lectura

**Files:** web/dimension.css, app.js, library.js, index.html, favicon.svg, radar-logo.png, manifest.webmanifest, sw.js; pruebas existentes de Dimension/layout/smoke/contratos y docs.
**Interfaces:** consume preferencias theme/font/columns existentes y clases de módulos; produce los mismos valores/API, con Auto como fallback y tipografía compartida.

- [x] Ajustar regresiones funcionales para Auto respetando elección guardada, restablecer/importar, Texto grande en rutas, controles móviles, lector y contraste. Observar RED antes de implementación. Las variaciones puramente estéticas se inspeccionan con capturas.
- [x] Generar marca RSS simple; implementar SVG equivalente y reemplazar PNG/PWA sin editar la imagen con Python. Actualizar tokens, tipografía y efectos en dimension.css sin añadir otra capa.
- [x] Unificar fallback Auto en estado, restauración y HTML; conservar selecciones explícitas. Ejecutar las regresiones pertinentes y observar GREEN.
- [x] Revisar capturas claro/oscuro, móvil/escritorio, entradas y controles; ejecutar Python/Node, lector, smoke y suites de navegador afectadas.
- [ ] Sincronizar versiones/caché/documentación. Revisar diff, commit y revisión independiente. Resolver hallazgos importantes con RED→GREEN, completar CI3motores, PR, integración y Pages.
