# Fuentes reconocidas en español — Implementation Plan

> Alcance inicial sobre la base de 221, ampliado posteriormente tras integrar PR102–110 y la nueva solicitud del usuario. El [plan de IA y estructura](../plans/2026-10-28-ia-site-structure.md) define el alcance final y el total de 276. Las observaciones de esta selección se conservan como históricas.

> Ejecución nativa con superpowers:executing-plans; una rama/PR del checkout actual y revisión independiente final según AGENTS.md. Se conserva la delegación previa de decisiones y ejecución.

**Goal:** Añadir23 canales con disponibilidad observada y ampliar diversidad de medios/territorios.
**Architecture:** Configuración OPML y catálogo estático existente; evidencia separada de investigación y registro histórico conservado. Sin modificar el recolector ni la interfaz.
**Tech Stack:** XML, JSON, Markdown; parse_opml/audit_feeds y pruebas offline Python/Node existentes.
**Spec:** docs/superpowers/specs/2026-10-28-reliable-sources-design.md

## Global Constraints
- 244 suscripciones/8 carpetas;221 anteriores idénticas por URL/ID/nombre/categoría.
-1 RSS directo y 22 RADAR en español, cultura dentro de Internacionales.
- No nuevas dependencias ni cambios de UI, recolector, datos personales o workflows.
- No convertir disponibilidad técnica en garantía editorial, audiencia medida o licencia.

## Review Focus
-RSS observado con200pero índices/autor/fecha antigua no constituye un artículo verificado.
-Consultas generales deben corresponder al medio; las de Monagas deben restringirse al territorio y títulos.
-Fuentes previas/IDs y respaldos siguen válidos; no se eliminan ni reclasifican.
-El total244 es de canales, no244 medios independientes; catálogos/README/evidencia deben coincidir.
-Preservar historia pendiente del 24 de octubre y diferenciarla de la revalidación actual.

### Task1: catálogo, evidencia y publicación

**Files:** sources/feeds.opml, sources/reliable-expansion-verification.json, web/data/sources.json, tests/test_new_catalog.py, README.md, docs/project-status.md, docs/fuentes-ampliadas.md y docs/fuentes-verificadas-2026-10-28.md.
**Interfaces:** consume parse_opml(Path)->list[dict] y audit(Path)->dict; produce el mismo formato de catálogo con IDs estables y un registro documental sin efecto sobre ejecución.

- [x] Investigar candidatos/revalidar diez canales previos fuera de tests; guardar respuestas/sumas/metadatos en scratch.
- [x] Adaptar contratos offline de integridad/preservación y añadir correspondencia entre altas y evidencia; observar RED contra catálogo anterior.
- [x] Añadir solo los23 canales seleccionados; generar catálogo offline y documentación exacta con pendientes/limitaciones.
- [x] Ejecutar auditoría, Python/Node y comprobaciones pertinentes; observar GREEN y revisar diff.
- [ ] Revisión independiente, resolver hallazgos importantes con pruebas, PR/CI, integrar y verificar Pages.
