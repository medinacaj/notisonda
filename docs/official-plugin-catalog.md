# Plugins y acceso a GitHub desde ChatGPT y Claude (sin CLI)

Este proyecto se mantiene desde **interfaces de chat**, no desde Codex CLI. **No ejecutar** scripts de instalación de Codex ni copiar el catálogo completo de plugins al repositorio.

## ChatGPT
- Usar el acceso a GitHub disponible en esta conversación para inspeccionar Issue, archivos y PR. Algunas conexiones GitHub son solo lectura; confirmar permisos antes de prometer cambios.
- Instalar o conectar plugins únicamente desde **Configuración → Plugins**, con acción y autorización del usuario. Un archivo de GitHub no instala plugins en ChatGPT.
- Las habilidades de Superpowers pueden estar disponibles como plugin, pero su instalación en una cuenta/chat no implica que el repositorio las tenga activadas.
- `CHATGPT.md` proporciona contexto para **pedir que se lea**, no instrucciones que ChatGPT descubra automáticamente.

## Claude en navegador
- En claude.ai, pulsar `+` → `Agregar desde GitHub` y seleccionar el repositorio y los archivos necesarios.
- `CLAUDE.md` importa `AGENTS.md` automáticamente **solo en entornos que soportan ese mecanismo (por ejemplo Claude Code)**; la conversación normal de Claude requiere seleccionar los archivos relevantes.
- No usar repositorio entero como contexto si basta con Issue, diff y 2–3 archivos.

## Sobre colecciones y skills
- [OpenAI Plugins](https://github.com/openai/plugins) es un catálogo para entornos compatibles; no hay una operación desde un chat para instalar todos sus elementos como una única skill.
- La skill `.agents/skills/coordinating-chatgpt-claude/SKILL.md` permanece como procedimiento portable, **no como instalación activa en ChatGPT Chat**.
- Evitar plugins externos innecesarios, API keys y cambios automáticos de repositorio.

## Fuentes de ayuda
- [ChatGPT + GitHub](https://help.openai.com/es-419/articles/11145903-connecting-github-to-chatgpt)
- [Claude + GitHub](https://support.claude.com/es/articles/10167454-usar-la-integracion-de-github)
