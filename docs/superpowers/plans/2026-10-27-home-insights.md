# Cobertura en Inicio — Implementation Plan

> Ejecución nativa con superpowers:executing-plans; rama del checkout actual, revisión independiente final según AGENTS.md.

**Goal:** Mostrar cobertura y tendencias en Inicio con contenido útil y compacto.
**Architecture:** Reubicar sección única desde homepage.js, renderizar features en dashboard, mapa details opcional en usability.js y tokens de dimension.css. Sin cambios a recolector o datos.
**Tech Stack:** HTML/CSS/JS estático; Playwright de prueba.
**Spec:** docs/superpowers/specs/2026-10-27-home-insights-design.md

## Global Constraints
- Una instancia de cobertura/tendencias en Inicio, sin banner nuevo, ni otro listado general o fuentes nuevas.
- Conservar ranking24h, preferencias, logo24px, acceso a lector y temas, sin desbordes320–1440.

## Review Focus
- Entrada directa a Inicio carga datos sin pasar por Resumen.
- Respuesta asíncrona no requiere que el usuario permanezca en la ruta original.
- Filtros de fuente/personales actualizan el ranking, sin lista anterior residual.
- Al cerrar lector/comparación de ranking, foco y posición vuelven a ese bloque.
- Mapa permanece bajo control del usuario también al cambiar ancho; si tendencias vacías, no hay columna vacía.

### Task1: ruta, interacción y presentación
- [x] Adaptar tests existentes: Inicio visible/Resumen oculto, tendencias asíncronas, filtro de fuentes, búsqueda, lector/foco y mapa opcional. Observar RED.
- [x] Trasladar sección y renderizado; identificar filas para lector; plegar mapa en todos los tamaños. Comprobar GREEN.
- [x] Aplicar dos columnas condicionales/una móvil, inspeccionar capturas y ejecutar regresiones adecuadas.
- [ ] Actualizar docs/versiones/cache; revisión independiente, PR/CI3motores, integrar y verificar Pages.
