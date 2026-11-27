#!/usr/bin/env bash
# Deja TODO listo para generar arte GTA IV/VI por CPU en un contenedor nuevo (idempotente, reanudable).
# Uso: bash extra/herramientas_ia/arrancar.sh [--servidor]     (--servidor: ademas levanta Flux en localhost:1234)
IA=/root/ia; M=$IA/models; mkdir -p $M
# 1) Python (ruta SD1.5 + poses + recortes)
[ -d $IA/venv ] || python3 -m venv $IA/venv
if ! $IA/venv/bin/python -c "import torch,diffusers,rembg" 2>/dev/null; then
  $IA/venv/bin/pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cpu
  $IA/venv/bin/pip install -q diffusers transformers accelerate safetensors peft "rembg[cpu]" onnxruntime pillow numpy opencv-python-headless controlnet-aux
fi
# 2) stable-diffusion.cpp (motor Flux en CPU)
if [ ! -x $IA/sdcpp/build/bin/sd-server ]; then
  [ -d $IA/sdcpp ] || git clone --depth 1 --recursive https://github.com/leejet/stable-diffusion.cpp $IA/sdcpp
  (cd $IA/sdcpp && mkdir -p build && cd build && cmake .. -G Ninja -DCMAKE_BUILD_TYPE=Release >/dev/null && ninja >/dev/null)
fi
# 3) Modelos (reanudables). Todo desde Hugging Face (civitai exige login).
d(){ [ -f "$M/$2.done" ] && return; curl -sL -C - -A "Mozilla/5.0" --retry 5 -o "$M/$2" "$1" && touch "$M/$2.done"; }
d https://huggingface.co/city96/FLUX.1-schnell-gguf/resolve/main/flux1-schnell-Q4_K_S.gguf flux1-schnell-Q4_K_S.gguf
d https://huggingface.co/city96/t5-v1_1-xxl-encoder-gguf/resolve/main/t5-v1_1-xxl-encoder-Q4_K_M.gguf t5xxl-Q4_K_M.gguf
d https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors clip_l.safetensors
d https://huggingface.co/Comfy-Org/Lumina_Image_2.0_Repackaged/resolve/main/split_files/vae/ae.safetensors ae.safetensors
d https://huggingface.co/Muapi/gta-iv-vibe-l-m-panda/resolve/main/gta-iv-vibe-l-m-panda.safetensors lora_gta4_vibe_flux.safetensors
d https://huggingface.co/Muapi/gta-6-style-grand-theft-auto-vi-wallpaper-loading-screen-style-lora-flux/resolve/main/gta-6-style-grand-theft-auto-vi-wallpaper-loading-screen-style-lora-flux.safetensors lora_gta6_loading_flux.safetensors
d https://huggingface.co/Muapi/gta-vi-lora-grand-theft-auto-6-gta-v-style-flux/resolve/main/gta-vi-lora-grand-theft-auto-6-gta-v-style-flux.safetensors lora_gta6_style_flux.safetensors
# 4) Scripts del servidor
cat > $IA/servidor_flux.sh <<'S'
#!/bin/bash
M=/root/ia/models
exec /root/ia/sdcpp/build/bin/sd-server --diffusion-model $M/flux1-schnell-Q4_K_S.gguf --vae $M/ae.safetensors --clip_l $M/clip_l.safetensors --t5xxl $M/t5xxl-Q4_K_M.gguf \
  --lora-model-dir $M --cfg-scale 1.0 --sampling-method euler --steps 4 -t 4 --flash-attn on --listen-port 1234
S
chmod +x $IA/servidor_flux.sh
[ "$1" = "--servidor" ] && (pgrep -f sd-server >/dev/null || nohup $IA/servidor_flux.sh > $IA/servidor.log 2>&1 &)
echo "ARRANQUE_OK  (servidor: bash $IA/servidor_flux.sh &  |  cliente: python3 extra/herramientas_ia/flux_gen.py out.png \"prompt\")"
