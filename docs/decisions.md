# Decisiones técnicas duraderas

## ADR-001 — GitHub como memoria compartida
**Fecha:** 2026-10-18. **Estado:** propuesta en revisión hasta fusionar el PR.

**Decisión:** Issues describen objetivos; PR contienen el diff, pruebas, revisiones y handoff; commits fijan la versión analizada. No replicar todo en chats separados.

**Motivo:** Claude y Codex no comparten automáticamente memoria entre productos. El repositorio mantiene trazabilidad y reduce contexto repetido.

## ADR-002 — Instrucciones únicas
**Fecha:** 2026-10-18. **Estado:** propuesta en revisión hasta fusionar el PR.

**Decisión:** `AGENTS.md` gobierna las instrucciones comunes y `CLAUDE.md` lo importa para Claude Code. La documentación extensa se consulta bajo demanda.

**Motivo:** evitar reglas contradictorias y consumo innecesario de contexto.

## ADR-003 — Revisión cruzada bajo demanda
**Fecha:** 2026-10-18. **Estado:** propuesta en revisión hasta fusionar el PR.

**Decisión:** implementación y auditoría separadas; CI verifica lo mecánico. Claude no queda conectado automáticamente por añadir archivos de instrucciones. La fusión requiere comprobación humana.
