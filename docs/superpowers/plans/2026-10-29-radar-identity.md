# Radar-RSS — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans, ejecución nativa y una revisión final independiente.

**Goal:** Restaurar Radar-RSS como identidad pública y alinear la recuperación y salud con la URL real renombrada.
**Architecture:** Identidad central de scripts en `site_config.py`; cambios de texto y referencias de activos del frontend estático. Reutilizar activos RSS históricos y actualizar caché, conservando formatos e IDs.
**Tech Stack:** Python, JavaScript y activos estáticos existentes, sin dependencias nuevas.
**Spec:** `docs/superpowers/specs/2026-10-29-radar-identity-design.md`.

## Global Constraints

- Catálogo de 311 fuentes y ocho carpetas intacto; PR #120/#121 separados y sin fusionar/publicar.
- Nombre público Radar-RSS y URL observada `https://medinacaj.github.io/radar-rss/`.
- Conservar almacenamiento, formato de respaldo, GUID de noticias y UID de calendarios.
- Conservar estilos y los activos gráficos existentes; reutilizar RSS sin redibujar.
- No modificar workflows ni programación, retención o comportamiento de actualización.

## Review Focus

- URL de recuperación y monitor distinta de la marca visible, validada con respuestas reales.
- PWA, Apple y metadatos con PNG existentes de dimensiones declaradas correctas.
- Marca coherente en descargas, resúmenes, calendario y RSS sin cambiar identidades de datos.
- Cachés de ambas marcas migradas sin romper lectura offline ni actualización manual.
- Fuentes y preferencias intactas, con los PR de fuentes pendientes conservados.

### Task 1: Identidad y compatibilidad

**Files:** `scripts/site_config.py`, URL del proyecto en el User-Agent de `scripts/collect.py`, `web/index.html`, `manifest.webmanifest`, scripts con textos públicos, `web/sw.js`, SVG RSS recuperados bajo nombres nuevos, `README.md`, cabecera OPML; pruebas de publicación/activos, exportaciones y navegador pertinentes.
**Interfaces:** `SITE_NAME` cambia a Radar-RSS, `SITE_URL` a la ruta comprobada; esquemas, GUID y UID permanecen idénticos. El HTML y manifest referencian los archivos RSS históricos; no se sobrescriben los originales de Notisonda.

- [x] Actualizar pruebas de límites HTTP, identidad/PNG y exportaciones al resultado solicitado; observar fallos antes del cambio.
- [x] Actualizar identidad activa y enlaces de publicación sin reemplazar formatos ni IDs técnicos.
- [x] Verificar pruebas, caché, catálogo intacto, importación de respaldos antiguos y ambos temas en navegador.
- [ ] Revisión independiente, PR con CI del commit exacto; dejar publicación pendiente.
