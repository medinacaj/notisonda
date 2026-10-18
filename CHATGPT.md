# ChatGPT — guía para trabajo desde esta conversación

Esta guía está pensada para **ChatGPT Chat**, no para Codex ni Codex CLI. **No se abre automáticamente**; solicitar expresamente su lectura en el chat.

## Instrucción breve reutilizable
"Con el GitHub conectado, abre este repositorio, lee `AGENTS.md` e Issue #[N], inspecciona solo el código necesario y aplica los criterios de aceptación en una rama/PR si los permisos lo permiten. Registra resultado de CI, SHA y un handoff breve para revisar con Claude. No edites main directamente."

## Colaboración con Claude Chat
1. ChatGPT prepara el PR y resumen en GitHub.
2. En claude.ai, seleccionar `+` → `Agregar desde GitHub` y leer `AGENTS.md` y el cambio del PR.
3. Claude devuelve defectos comprobables con archivo/línea.
4. Llevar ese informe de vuelta a ChatGPT; corregir y revisar solo el diff nuevo.
5. La persona propietaria valida el resultado y autoriza integrar.

Para detalles ver `docs/agent-workflow.md`. No suponer conexión entre conversaciones ni prometer pruebas no ejecutadas.
