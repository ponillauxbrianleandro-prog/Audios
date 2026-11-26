# Generación de imágenes por CPU (reinstalar en un chat nuevo)
Entorno verificado: sin GPU, 4 CPU, 15 GB RAM. ~50–60 s por imagen 512×640 (SD1.5 + LCM-LoRA, 5–6 pasos).
```
python3 -m venv /root/ia/venv && . /root/ia/venv/bin/activate
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install diffusers transformers accelerate safetensors peft "rembg[cpu]" onnxruntime pillow numpy opencv-python-headless
export HF_HOME=/root/ia/hf     # los modelos (~6.5 GB) se bajan solos de Hugging Face la primera vez
/root/ia/venv/bin/python extra/herramientas_ia/generar.py salida.png "prompt" referencia.jpg --ip 0.5 --seed 7 --steps 6
```
- `--ip` = fuerza del estilo de la referencia (0.7 copia demasiado al personaje de la referencia; 0.35–0.5 es lo útil).
- Modelos: SD1.5 + LCM-LoRA + IP-Adapter (h94/IP-Adapter). Recortes: `rembg`.
- Mejor calidad: GPU o API de imágenes (SDXL/Flux + LoRA de estilo); este flujo en CPU da estilo pero poca fidelidad fina (manos, rostro).
- Herramientas candidatas (links): ver `/root/.claude/plans/` o el historial: diffusers, stable-diffusion.cpp, ComfyUI, IP-Adapter, ControlNet, kohya sd-scripts, rembg, LayerDiffuse, SAM, three.js, pixijs.

## v6 — pipeline completo
- `instalar.sh [--modelos]` instala todo (también está como setup script del entorno del usuario; corre solo en contenedores nuevos). Los modelos se bajan solos de Hugging Face al primer uso (~8 GB).
- `entrenar_lora.py`: LoRA de estilo GTA IV en CPU (~5,5 s/paso, 400 pasos). Guarda `estado.pt` cada 20 pasos y **reanuda solo** si el contenedor se reinicia (los reinicios matan procesos en segundo plano). Captions en `extra/estilo/captions.json`; las imágenes de referencia no se guardan en el repo.
- `generar_personaje.py --lista` / `--pose X --expr Y`: poses (`poses.py`, OpenPose por código) + expresiones + LoRA de estilo + IP-Adapter.
- Limpiar fondo: `rembg` (`/root/ia/venv/bin/rembg i in.png out.png`).
