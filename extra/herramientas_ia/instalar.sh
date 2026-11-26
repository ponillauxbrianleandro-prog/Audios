#!/usr/bin/env bash
# Instala TODO lo necesario para generar arte estilo GTA IV por CPU (idempotente). Uso: bash extra/herramientas_ia/instalar.sh [--modelos]
set -e
IA=/root/ia; mkdir -p $IA
[ -d $IA/venv ] || python3 -m venv $IA/venv
. $IA/venv/bin/activate
if ! python -c "import torch,diffusers,rembg,controlnet_aux" 2>/dev/null; then
  pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cpu
  pip install -q diffusers transformers accelerate safetensors peft "rembg[cpu]" onnxruntime pillow numpy opencv-python-headless controlnet-aux
fi
export HF_HOME=$IA/hf
if [ "$1" = "--modelos" ]; then   # descarga ~8 GB de modelos desde Hugging Face (solo si se piden)
  python - <<'PY'
from huggingface_hub import snapshot_download as d
for r, kw in [("stable-diffusion-v1-5/stable-diffusion-v1-5", dict(allow_patterns=["*.json","*.txt","unet/diffusion_pytorch_model.safetensors","vae/diffusion_pytorch_model.safetensors","text_encoder/model.safetensors","tokenizer/*"])),
              ("latent-consistency/lcm-lora-sdv1-5", {}), ("h94/IP-Adapter", dict(allow_patterns=["models/ip-adapter_sd15.bin","models/image_encoder/*"])),
              ("lllyasviel/control_v11p_sd15_openpose", dict(allow_patterns=["*.json","diffusion_pytorch_model.safetensors"]))]:
    d(r, **kw)
PY
fi
echo "listo. Usar: $IA/venv/bin/python extra/herramientas_ia/generar_personaje.py --help"
