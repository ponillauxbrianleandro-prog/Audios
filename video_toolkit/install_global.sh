#!/bin/bash
# Instala a nivel usuario (sirve en cualquier repo): skills de Remotion, claude-code-video-toolkit
# con sus skills y comandos (/video, /setup, ...) y el marketplace anthropics/skills.
# Idempotente. Uso desde cualquier sesión:
#   curl -fsSL https://raw.githubusercontent.com/ponillauxbrianleandro-prog/Audios/main/video_toolkit/install_global.sh | bash
set -uo pipefail

export PATH="$HOME/.local/bin:/opt/node22/bin:$PATH"
T=/opt/claude-code-video-toolkit
C="$HOME/.claude"
mkdir -p "$C/skills" "$C/commands"

npx -y skills add remotion-dev/skills -g -y -a claude-code

if [ -d "$T/.git" ]; then
  git -C "$T" pull --ff-only || echo "No se pudo actualizar $T; se usa la copia existente." >&2
else
  git clone --depth 1 https://github.com/digitalsamba/claude-code-video-toolkit.git "$T"
fi
(cd "$T" && uv sync)

for s in "$T"/.claude/skills/*/; do
  ln -sfn "${s%/}" "$C/skills/$(basename "$s")"
done

NOTE="> Toolkit root: $T. Relative paths such as tools/, templates/, brands/, lib/ and docs/"
NOTE="$NOTE refer to it; run its tools with: uv run --project $T python $T/tools/NAME.py."
NOTE="$NOTE Create video projects under projects/ in the session's own repository."
for c in "$T"/.claude/commands/*.md; do
  { cat "$c"; printf '\n\n%s\n' "$NOTE"; } > "$C/commands/$(basename "$c")"
done

claude plugin marketplace add anthropics/skills

[ -d "$T/.venv" ] && [ -f "$C/commands/video.md" ]
