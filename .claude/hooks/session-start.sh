#!/bin/bash
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}"

# ffmpeg (lo usa generar_audio.py) solo si falta
if ! command -v ffmpeg >/dev/null; then
  apt-get update
  apt-get install -y ffmpeg
fi

# Dependencias de Python, con su propio chequeo de hash en el directorio de paquetes
pyhashes="$(python3 -I -c 'import sysconfig; print(sysconfig.get_path("purelib"))')/.session-start.sha256"
if ! sha256sum --check --status "$pyhashes" 2>/dev/null; then
  rm -f "$pyhashes"
  python3 -m pip install -r requirements.txt
  sha256sum .claude/hooks/session-start.sh requirements.txt > "$pyhashes" || rm -f "$pyhashes"
fi
