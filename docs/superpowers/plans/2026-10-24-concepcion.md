# Concepción RSS Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** añadir una carpeta pública Concepción con fuentes verificadas.
**Architecture:** extender OPML y categorías existentes, sin backend ni dependencias nuevas. Separar comprobaciones en vivo de tests deterministas.
**Tech Stack:** Python 3.12, JavaScript estático, RSS/OPML, GitHub Pages.
**Spec:** ../specs/2026-10-24-concepcion-design.md

## Global Constraints
- Categoría 07 - Concepción, Concepción Chile/Gran Concepción.
- Conservar las seis carpetas y URL/IDs/asignaciones de las 178 fuentes actuales.
- No cambiar .github/workflows/deploy.yml; no merge ni producción.
- Sin dependencias nuevas ni red durante tests.

## Review Focus
- Las categorías son dinámicas: aceptar cualquier cantidad positiva; rechazar listas vacías, duplicados y nombres inválidos, sin imponer seis ni siete.
- Concepción se encuentra dentro de Chile y Latinoamérica.
- La séptima carpeta filtra sus artículos sin mezclar categorías.
- Las suscripciones originales conservan IDs y asignaciones.
- Fuentes nuevas verificables, sin duplicar URL ni etiquetar RSS inferidos como comprobados.

## Task 1: compatibilidad de categorías
- [ ] Prueba RED: check_pages acepta una, cinco, siete y más categorías; filtros/boletín incluyen Concepción en Chile/Latam.
- [ ] Implementar mínimo en scripts/check_pages.py y web/app.js/features.js/v12.js según dependencias efectivas.
- [ ] Extender fixture/recorrido browser_tests/responsive_smoke.py a nueva carpeta, sin red externa.
- [ ] GREEN: suite Python/Node y comprobación dirigida de carpeta en navegador.

## Task 2: catálogo documentado
- [ ] Investigar y validar feeds directos, alternativamente radares verificados; inventariar descartes y fechas.
- [ ] Añadir 07 - Concepción a sources/feeds.opml; regenerar web/data/sources.json desde parse_opml, sin recopilar artículos.
- [ ] Actualizar README y docs de fuentes; validar IDs/URL/asignaciones originales, categorías y salida RSS.
- [ ] Ejecutar auditoría OPML, suite completa y revisión independiente del diff.
- [ ] Abrir PR desde SHA base actual, comprobar CI y reportar limitaciones.
