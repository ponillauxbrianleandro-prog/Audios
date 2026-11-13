#!/bin/bash
# Clona (o actualiza) claude-code-video-toolkit e instala sus dependencias de Python.
# Idempotente: se puede correr todas las veces que haga falta.
set -euo pipefail

cd "$(dirname "$0")"

repo=https://github.com/digitalsamba/claude-code-video-toolkit.git
dir=claude-code-video-toolkit

if [ -d "$dir/.git" ]; then
  git -C "$dir" pull --ff-only || echo "No se pudo actualizar $dir; se usa la copia existente." >&2
else
  git clone --depth 1 "$repo" "$dir"
fi

cd "$dir"
uv sync
