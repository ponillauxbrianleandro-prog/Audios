#!/bin/bash
# Instala Qwen3-TTS y descarga sus modelos al iniciar una sesión en la nube.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}"

# Solo se reinstala si cambió alguno de estos archivos desde la última instalación correcta.
hashes=voice_ai/.venv/.session-start.sha256
if ! sha256sum --check --status "$hashes" 2>/dev/null; then
  rm -f "$hashes"
  bash voice_ai/setup_qwen3_tts.sh >&2
  sha256sum .claude/hooks/session-start.sh voice_ai/setup_qwen3_tts.sh > "$hashes" || rm -f "$hashes"
fi
