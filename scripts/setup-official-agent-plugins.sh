#!/usr/bin/env bash
# Instala una selección acotada del catálogo oficial de plugins para Codex.
# Ejecutar en el ordenador donde está instalada la CLI de Codex.
set -euo pipefail

if ! command -v codex >/dev/null 2>&1; then
  echo "ERROR: Codex CLI no está instalada. Este script no instala Codex ni altera ChatGPT." >&2
  exit 1
fi

echo "Revisando catálogos instalados..."
if ! codex plugin marketplace list | grep -Fq "openai-curated"; then
  codex plugin marketplace add openai/plugins --ref main \
    --sparse .agents/plugins --sparse plugins
else
  echo "El catálogo oficial openai-curated ya está configurado."
fi

echo "Instalando solo los plugins apropiados para este proyecto..."
for plugin in github build-web-apps superpowers; do
  echo "Plugin: ${plugin}@openai-curated"
  # Si ya está instalado, Codex puede devolver un error benigno de duplicado.
  # No se ignoran otros errores; verificarlos manualmente.
  if ! codex plugin add "${plugin}@openai-curated"; then
    echo "ATENCIÓN: no se confirmó la instalación de ${plugin}; comprueba si ya estaba instalado." >&2
  fi
done

echo "Catálogo configurado. Comprueba el estado de cada plugin en Codex."
echo "Las integraciones externas pueden requerir autenticación adicional."
