#!/usr/bin/env bash
# Instalación automática de Qwen3-TTS: inspección del sistema, entorno Python,
# clon del repositorio y descarga de modelos desde Hugging Face.
#
# Uso:
#   ./setup_qwen3_tts.sh               # modelos 0.6B; los 1.7B solo si hay GPU >= 8 GB VRAM
#   ./setup_qwen3_tts.sh --with-large  # fuerza la descarga de los modelos 1.7B
#   ./setup_qwen3_tts.sh --no-large    # nunca descarga los modelos 1.7B
#
# Es idempotente: se puede volver a ejecutar y solo completa lo que falte.
set -euo pipefail

LARGE=auto
for arg in "$@"; do
  case "$arg" in
    --with-large) LARGE=yes ;;
    --no-large) LARGE=no ;;
    *) echo "Opción desconocida: $arg" >&2; exit 2 ;;
  esac
done

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

BASE_MODELS=(
  Qwen3-TTS-Tokenizer-12Hz
  Qwen3-TTS-12Hz-0.6B-CustomVoice
  Qwen3-TTS-12Hz-0.6B-Base
)
LARGE_MODELS=(
  Qwen3-TTS-12Hz-1.7B-CustomVoice
  Qwen3-TTS-12Hz-1.7B-VoiceDesign
)

step() { printf '\n==> %s\n' "$*"; }

# ---------------------------------------------------------------- 1. Sistema
step "Inspección del sistema"
OS_NAME="$(. /etc/os-release 2>/dev/null && echo "$PRETTY_NAME" || uname -s)"
RAM_GB=$(awk '/MemTotal/ {printf "%d", $2/1024/1024}' /proc/meminfo 2>/dev/null || echo 0)
DISK_GB=$(df -Pk "$ROOT" | awk 'NR==2 {printf "%d", $4/1024/1024}')
GPU_NAME="ninguna"
VRAM_MB=0
if command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi >/dev/null 2>&1; then
  GPU_NAME="$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)"
  VRAM_MB="$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | sort -nr | head -1)"
fi
echo "SO:      $OS_NAME ($(uname -m))"
echo "Python:  $(python3 --version 2>&1)"
echo "Git:     $(git --version)"
echo "CPU:     $(nproc) núcleos"
echo "RAM:     ${RAM_GB} GB"
echo "GPU:     ${GPU_NAME} (${VRAM_MB} MB VRAM)"
echo "Disco:   ${DISK_GB} GB libres en $ROOT"

if [ "$LARGE" = auto ]; then
  if [ "$VRAM_MB" -ge 8000 ]; then LARGE=yes; else LARGE=no; fi
fi
NEED_GB=10
[ "$LARGE" = yes ] && NEED_GB=20
echo "Modelos 1.7B: $LARGE"
if [ "$DISK_GB" -lt "$NEED_GB" ]; then
  echo "ERROR: hacen falta ~${NEED_GB} GB libres y hay ${DISK_GB} GB." >&2
  exit 1
fi

# ------------------------------------------------------- 2. Paquetes sistema
if ! command -v sox >/dev/null 2>&1; then
  step "Instalando sox"
  SUDO=""
  [ "$(id -u)" -ne 0 ] && SUDO="sudo"
  if command -v apt-get >/dev/null 2>&1; then
    { $SUDO apt-get update -qq || true; $SUDO apt-get install -y sox; } || echo "AVISO: no se pudo instalar sox; instálalo a mano."
  else
    echo "AVISO: instala sox con el gestor de paquetes de tu sistema."
  fi
fi

# ------------------------------------------------------------ 3. Entorno venv
step "Entorno Python (.venv)"
if [ ! -x .venv/bin/python ]; then
  if command -v uv >/dev/null 2>&1; then
    uv venv --python 3.12 --seed .venv
  elif command -v python3.12 >/dev/null 2>&1; then
    python3.12 -m venv .venv
  else
    python3 -m venv .venv
  fi
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python --version
python -m pip install -q -U pip

# ------------------------------------------------------------ 4. Repositorio
step "Repositorio Qwen3-TTS"
if [ -d Qwen3-TTS/.git ]; then
  git -C Qwen3-TTS pull --ff-only || echo "AVISO: no se pudo actualizar el clon."
else
  git clone https://github.com/QwenLM/Qwen3-TTS.git
fi

# ------------------------------------------------------------ 5. Paquetes pip
step "Paquetes Python"
if [ "$VRAM_MB" -gt 0 ]; then
  python -m pip install -U torch torchaudio
else
  # Sin GPU: ruedas solo-CPU, mucho más livianas que las de CUDA.
  python -m pip install -U torch torchaudio --index-url https://download.pytorch.org/whl/cpu
fi
python -m pip install -U qwen-tts
# qwen-tts fija transformers 4.57.x, que exige huggingface_hub < 1.0.
python -m pip install -U "huggingface_hub>=0.34,<1.0"

# ---------------------------------------------------------------- 6. Modelos
step "Descarga de modelos"
mkdir -p models
MODELS=("${BASE_MODELS[@]}")
[ "$LARGE" = yes ] && MODELS+=("${LARGE_MODELS[@]}")
for m in "${MODELS[@]}"; do
  echo "--- Qwen/$m"
  hf download "Qwen/$m" --local-dir "models/$m"
done

step "Listo"
du -sh models/* 2>/dev/null || true
echo "Activa el entorno con: source $ROOT/.venv/bin/activate"
