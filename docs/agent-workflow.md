# Flujo multiagente nivel 2 — Claude + Codex

## Etapas
1. **Issue:** objetivo observable, criterios de aceptación, riesgos y archivos o módulos afectados. No enviar el repositorio entero como prompt.
2. **Implementador (habitualmente Codex):** crear rama, leer `AGENTS.md`, inspeccionar únicamente los archivos relevantes, modificar y probar. Abrir PR enlazado al issue.
3. **CI:** comprobar el resultado del workflow sobre el SHA actual. Un chequeo pendiente o no ejecutado no equivale a éxito.
4. **Revisor independiente (habitualmente Claude Code):** recibir URL/número del PR y SHA; analizar primero su diff, tests y dependencias directas. Publicar hallazgos en el PR. La revisión NO es automática por tener `CLAUDE.md`.
5. **Corrección:** el implementador aborda P0/P1 y P2 justificados. El revisor vuelve a revisar únicamente el diff incremental y los hallazgos abiertos.
6. **Integración:** una persona confirma que están satisfechos los criterios y controles, y fusiona. Actualizar el issue.

## Traspaso mínimo (copiar al PR)
- Issue / objetivo:
- Commit SHA y archivos afectados:
- Qué cambió (3 líneas):
- Pruebas (comando → resultado comprobado):
- Riesgos / pendientes:
- Revisión: agente/modelo, fecha, commit revisado y hallazgos:

## Prompts reutilizables
**Para implementar:** "Lee AGENTS.md e issue #N. Identifica archivos mínimos, implementa criterios, ejecuta las pruebas adecuadas y deja PR con traspaso conciso. No toques main ni módulos fuera del alcance."

**Para revisar:** "Lee AGENTS.md y revisa PR #N en commit SHA. Prioriza diff, tests y archivos dependientes; señala solo defectos reproducibles con P0–P3 y archivo:línea. No modifiques código ni vuelvas a auditar todo el proyecto."

## Economía de contexto y tokens
- La conversación entre herramientas no es una fuente fiable de verdad; usar Issue + PR + commit como memoria durable.
- Abrir primero `git diff`, manifest y 1–3 archivos vinculados; solo ampliar si existe una causa concreta.
- Mantener instrucciones compartidas en `AGENTS.md` y especialidades en `CLAUDE.md`, sin copiar información dos veces.
- No solicitar dos auditorías generales para el mismo SHA. Segunda pasada solo si cambia el código.
- Priorizar CI determinista para sintaxis, unit tests y formato; usar modelos de razonamiento intensivo en incidencias complejas.
- Evitar copiar logs completos al agente: adjuntar error, stacktrace mínimo, comando y SHA.
- Cuando se registren costes, usar datos reales de cada proveedor (no estimaciones como si fueran mediciones).

## Medición por PR (opcional)
En el PR registrar: agente implementador, agente revisor, modelo, tokens de entrada/salida o coste **solo si la plataforma lo informa**, número de ciclos de revisión y pruebas fallidas. No publicar datos sensibles. Comparar calidad, coste y tiempo; optimizar a partir de resultados, no de supuestos.

## Límites
Este protocolo no habilita automáticamente Claude Code, Codex, revisores en GitHub, tokens API ni protección de ramas. Requieren conexiones/permisos externos. No conceder permisos de escritura a un revisor si solo necesita lectura.
