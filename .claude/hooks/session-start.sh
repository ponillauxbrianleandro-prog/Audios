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

# Video toolkit, skills de Remotion y marketplace a nivel usuario: mismo criterio de hashes.
hashes=video_toolkit/.session-start.sha256
if [ ! -d /opt/claude-code-video-toolkit/.venv ] || ! sha256sum --check --status "$hashes" 2>/dev/null; then
  rm -f "$hashes"
  if bash video_toolkit/install_global.sh >&2; then
    sha256sum .claude/hooks/session-start.sh video_toolkit/install_global.sh > "$hashes" || rm -f "$hashes"
  else
    echo "install_global.sh falló; la sesión sigue sin el video toolkit." >&2
  fi
fi
