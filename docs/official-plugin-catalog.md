# Colección oficial de plugins para el flujo multiagente

**Origen vigente:** [openai/plugins](https://github.com/openai/plugins).
El antiguo repositorio [openai/skills](https://github.com/openai/skills) está marcado como **deprecated**. No hacer una copia masiva de todas las skills ni habilitar plugins sin examinarlos.

## Instalación en Codex (equipo personal)

El repositorio GitHub **no instala** plugins en el ordenador ni en la cuenta ChatGPT. En un equipo con Codex CLI:

```sh
bash scripts/setup-official-agent-plugins.sh
```

El instalador registra el catálogo `openai-curated` de OpenAI y solicita únicamente estos plugins:

| Plugin | Uso |
| --- | --- |
| `github` | Issues, PR, comentarios, estado CI |
| `build-web-apps` | Desarrollo web, pruebas y despliegues |
| `superpowers` | Planificación, depuración, revisión y TDD |

La publicación del catálogo es independiente de la instalación de cada plugin. La autenticación de GitHub u otras aplicaciones puede requerir autorización del usuario.

### Instalación manual

```sh
codex plugin marketplace add openai/plugins --ref main --sparse .agents/plugins --sparse plugins
codex plugin marketplace list
codex plugin add github@openai-curated
codex plugin add build-web-apps@openai-curated
codex plugin add superpowers@openai-curated
```

Si alguno ya existe, no instalarlo de nuevo. Revisar el catálogo y confirmar que cada plugin se encuentra disponible y habilitado antes de utilizarlo.

## Claude Code y ChatGPT

- Para **Claude Code** se mantiene la skill propia `.claude/skills/coordinating-claude-codex/SKILL.md` y el archivo `CLAUDE.md`. Añadir plugins de Codex **no instala nada en Claude**.
- En **ChatGPT**, instalar plugins requiere la acción explícita del usuario en el directorio. No hay instalación automática a partir de commits de GitHub.
- El plugin **Superpowers** puede estar instalado en un entorno y no en otro; verificar por separado.
- Una skill de coordinación **no ejecuta dos modelos** ni establece conexión entre sus servicios. Revisiones cruzadas reales necesitan agentes configurados y autorizados.

## Seguridad y eficiencia

- Preferir la selección anterior a instalar indiscriminadamente el catálogo, ya que algunos plugins requieren credenciales, permisos o dependencias.
- Mantener `AGENTS.md` como fuente común e incluir en Issues/PR solo la información necesaria.
- Examinar nuevos plugins, comandos y permisos antes de habilitarlos, especialmente si pueden escribir en GitHub o desplegar sitios.
- Los comandos de instalación requieren Codex CLI y pueden evolucionar; comprobar la documentación oficial si fallan.
