# Trabajo multiagente desde chats: ChatGPT + Claude

Este protocolo funciona **sin Codex CLI y sin terminal**. GitHub es la fuente de verdad. No hay un orquestador automático entre las dos conversaciones.

## Preparación
- **ChatGPT:** acceder al repositorio con el plugin/conector GitHub disponible; pedir expresamente `AGENTS.md` y el Issue. Según permisos y modalidad del conector, algunas acciones pueden ser de solo lectura.
- **Claude (claude.ai):** en el chat pulsar `+` → `Agregar desde GitHub`; seleccionar `AGENTS.md`, los archivos pertinentes y, cuando proceda, el PR/diff. En Projects también puede añadir GitHub como fuente.
- `AGENTS.md`, `CHATGPT.md`, `CLAUDE.md` y los archivos `SKILL.md` en el repositorio **no se cargan automáticamente en una conversación web**. Deben seleccionarse, compartirse o solicitarse de forma explícita.

## Flujo recomendado
1. Abrir Issue en GitHub con objetivo, criterios de aceptación, límites y referencias. Solo leer los archivos relacionados.
2. Trabajar desde **ChatGPT en este chat** para analizar e implementar el cambio si el conector de GitHub permite escribir; si no lo permite, preparar parche/PR para aplicar mediante un medio autorizado. Crear rama y PR; nunca editar `main` directamente.
3. Verificar pruebas en GitHub Actions para el SHA exacto del PR; no atribuir pruebas no ejecutadas.
4. En **Claude Chat**, agregar desde GitHub el contexto mínimo necesario y pedir revisión del diff y del SHA actual. Claude no queda conectado ni recibe notificaciones automáticamente; compartir manualmente la URL del PR y archivos si hace falta.
5. Volver a **ChatGPT** con las observaciones de Claude o con un comentario del PR; abordar problemas demostrables.
6. Tras cambios, revisar únicamente las diferencias nuevas. Validar CI y fusionar con aprobación humana.

## Handoff de menos de 200 palabras
- Repositorio, Issue y PR:
- SHA revisado:
- Archivos y cambio:
- Pruebas ejecutadas (comando, resultado):
- Hallazgos abiertos, gravedad, archivo/línea:
- Próxima acción:

## Peticiones reutilizables

**En ChatGPT:**
> Revisa [repo] e Issue #[n]. Lee AGENTS.md y solo los archivos relevantes. Implementa los criterios en una rama y abre PR si tus permisos lo permiten. Verifica las pruebas; prepara un resumen para revisión por Claude con SHA, diff, riesgos y resultados. No edites main directamente.

**En Claude Chat:**
> Con la integración GitHub, revisa [repo], AGENTS.md y PR #[n] en el SHA [sha]. Busca defectos reales de lógica, seguridad y regresiones. Devuelve hallazgos P0–P3 con archivo:línea y reproducción. No repitas auditorías del repositorio completo. No supongas que puedes editar el PR.

## Optimizar tokens
- Issue y PR sustituyen transcripciones largas.
- Primero diff, después tests; leer arquitectura únicamente si es pertinente.
- No reanalizar todo tras cada corrección; revisar solo deltas y defectos abiertos.
- No atribuir ahorro medido de tokens sin cifras reportadas por los proveedores.
- Si un chat no puede abrir enlaces PR, adjuntar/copiar únicamente el diff necesario.

## Límites
No hay comunicación automática ChatGPT↔Claude ni instalación de plugins mediante commits. Las integraciones GitHub son permisos separados que el usuario autoriza en cada servicio.
