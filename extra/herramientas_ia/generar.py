#!/usr/bin/env python3
"""Genera imagenes con SD1.5 + LCM-LoRA + IP-Adapter (estilo por imagen de referencia) en CPU.
Uso: /root/ia/venv/bin/python generar.py salida.png "prompt" ref1.jpg [ref2.jpg ...] [--w 512 --h 640 --steps 5 --seed 1 --ip 0.7]"""
import sys, time, torch
from PIL import Image
from diffusers import StableDiffusionPipeline, LCMScheduler
a = sys.argv[1:]; out, prompt = a[0], a[1]
refs = [x for x in a[2:] if not x.startswith("--") and x.lower().endswith((".jpg", ".png", ".jpeg"))]
opt = lambda n, d: type(d)(a[a.index("--" + n) + 1]) if "--" + n in a else d
W, H, steps, seed, ip = opt("w", 512), opt("h", 640), opt("steps", 5), opt("seed", 1), opt("ip", .7)
torch.set_num_threads(4)
pipe = StableDiffusionPipeline.from_pretrained("stable-diffusion-v1-5/stable-diffusion-v1-5", torch_dtype=torch.float32, safety_checker=None)
pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
pipe.load_lora_weights("latent-consistency/lcm-lora-sdv1-5")
kw = {}
if refs:
    pipe.load_ip_adapter("h94/IP-Adapter", subfolder="models", weight_name="ip-adapter_sd15.bin"); pipe.set_ip_adapter_scale(ip)
    kw["ip_adapter_image"] = [Image.open(r).convert("RGB") for r in refs][0] if len(refs) == 1 else Image.open(refs[0]).convert("RGB")
t = time.time()
img = pipe(prompt, negative_prompt="photo, 3d render, cartoon, anime, blurry, deformed, extra fingers, text, watermark", width=W, height=H, num_inference_steps=steps, guidance_scale=1.2,
           generator=torch.Generator().manual_seed(seed), **kw).images[0]
img.save(out); print("listo", out, round(time.time() - t, 1), "s")
