#!/usr/bin/env python3
"""Cantante rockabilly: poses (ControlNet openpose definido en poses.py) + expresiones + estilo GTA IV (LoRA propio) + identidad (IP-Adapter con imagen maestra).
Uso: venv/bin/python generar_personaje.py --pose cantando_micro --expr cantando_aah --out salida.png [--seed 7 --steps 6 --maestro maestro.png --ip 0.5 --lora ruta --lora-w 0.9]
--lista muestra poses y expresiones."""
import argparse, os, sys, time, torch
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import poses

AQUI = os.path.dirname(os.path.abspath(__file__))
PERSONAJE = ("muscular 1980s rockabilly singer, dark wayfarer sunglasses, tall black pompadour quiff piled high and swept back, short black leather jacket, "
             "sheer white t-shirt, gold chain with round gold links and a large rock medallion, black leather gloves, brown belt with black details, black pants, black boots")
EXPR = {"neutra": "calm confident face", "cantando_aah": "mouth wide open singing loudly", "cantando_ooh": "lips rounded singing a long note, eyes closed",
        "grito": "screaming into the microphone, intense", "sonrisa": "big charismatic smile showing teeth", "ceno": "angry frown, tense jaw",
        "guino": "winking with a smirk", "ojos_cerrados": "eyes closed, emotional, head tilted back"}
ESTILO = "gta4art style, digital painting, painterly flat planes, cool teal shadows, no outlines, pale desaturated city background, only the character has full color"
NEG = "photo, 3d render, cartoon, anime, blurry, deformed, extra fingers, bad hands, text, watermark, logo, lowres"

ap = argparse.ArgumentParser()
ap.add_argument("--pose", default="cantando_micro"); ap.add_argument("--expr", default="cantando_aah"); ap.add_argument("--out", default="out.png")
ap.add_argument("--seed", type=int, default=7); ap.add_argument("--steps", type=int, default=6); ap.add_argument("--maestro"); ap.add_argument("--ip", type=float, default=.5)
ap.add_argument("--lora", default=os.path.join(AQUI, "..", "estilo", "gta4_style_lora")); ap.add_argument("--lora-w", type=float, default=.9)
ap.add_argument("--cn", type=float, default=.9); ap.add_argument("--extra", default=""); ap.add_argument("--lista", action="store_true")
a = ap.parse_args()
if a.lista: print("poses:", list(poses.POSES)); print("expresiones:", list(EXPR)); sys.exit()
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, LCMScheduler
torch.set_num_threads(4)
cn = ControlNetModel.from_pretrained("lllyasviel/control_v11p_sd15_openpose", torch_dtype=torch.float32)
pipe = StableDiffusionControlNetPipeline.from_pretrained("stable-diffusion-v1-5/stable-diffusion-v1-5", controlnet=cn, torch_dtype=torch.float32, safety_checker=None)
pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
pipe.load_lora_weights("latent-consistency/lcm-lora-sdv1-5", adapter_name="lcm"); names, ws = ["lcm"], [1.0]
if os.path.exists(os.path.join(a.lora, "pytorch_lora_weights.safetensors")):
    pipe.load_lora_weights(a.lora, adapter_name="gta4"); names.append("gta4"); ws.append(a.lora_w)
pipe.set_adapters(names, ws)
kw = {}
if a.maestro:
    pipe.load_ip_adapter("h94/IP-Adapter", subfolder="models", weight_name="ip-adapter_sd15.bin"); pipe.set_ip_adapter_scale(a.ip)
    kw["ip_adapter_image"] = Image.open(a.maestro).convert("RGB")
ctrl = Image.fromarray(poses.render(a.pose))
prompt = f"{ESTILO}, {PERSONAJE}, {EXPR[a.expr]}, {a.extra}"
t = time.time()
img = pipe(prompt, image=ctrl, negative_prompt=NEG, width=512, height=768, num_inference_steps=a.steps, guidance_scale=1.3, controlnet_conditioning_scale=a.cn,
           generator=torch.Generator().manual_seed(a.seed), **kw).images[0]
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True); img.save(a.out); print("listo", a.out, round(time.time() - t, 1), "s")
