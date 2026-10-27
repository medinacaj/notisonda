# Cabecera mínima — Implementation Plan

> Ejecución nativa con superpowers:executing-plans; rama del checkout actual según preferencia vigente, revisión independiente final.

**Goal:** Quitar el panel grande y dejar una marca mínima en la barra existente.
**Architecture:** Mover brandHome a topbar-caption; faviconSVG24px; H1sr-only y eliminar fecha/aurora. Una capa de tema, mismos destinos y menús.
**Tech Stack:** HTML/CSS/JS estático y Playwright de prueba.
**Spec:** docs/superpowers/specs/2026-10-27-compact-header-design.md

## Global Constraints
- Barra<=64px, área de marca44px, sin desborde320–1440, sin nuevo bloque de presentación.
- Mantener IDs brandHome/dashboardTitle/topbarSection, contraste y lector; sin dependencias o datos nuevos.

## Review Focus
- Marca visible también con lateral abierto en escritorio.
-320px no envía botones a una segunda fila; enlace al inicio conserva nombre accesible sin texto visual.
- Menú móvil conserva cierre y foco al mover brandHome fuera del lateral.
- CSS de la aurora eliminado y reduced-motion de tarjetas preservado.

### Task1: simplificar y verificar
- [x] Mover marca pequeña a la barra y eliminar bloque/fecha/CSS; actualizar versiones/cache.
- [x] Ajustar verificaciones existentes al logo vectorial y a reduced-motion en tarjeta; inspeccionar capturas y smoke, lector, layout y Python/Node.
- [ ] Actualizar documentación, revisión independiente, PR/CI, integrar y verificar Pages.
