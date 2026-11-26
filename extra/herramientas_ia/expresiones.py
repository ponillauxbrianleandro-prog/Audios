#!/usr/bin/env python3
"""Expresiones por inpainting de la boca/mandibula sobre una imagen maestra (el resto del personaje no cambia).
Uso: venv/bin/python expresiones.py maestro.png salida_dir [--mouth x0,y0,x1,y1] [--lista] [--solo aah,sonrisa]"""
import os, sys, time, torch
from PIL import Image, ImageDraw, ImageFilter
EXPR = {"aah": "mouth wide open singing loudly, visible teeth and tongue", "ooh": "lips rounded in an O shape singing a long note", "grito": "mouth stretched wide open screaming, teeth visible, intense",
        "sonrisa": "big charismatic smile showing white teeth", "ceno": "tight lips, angry grimace, tense jaw", "sonrisa_ladeada": "confident smirk, one corner of the mouth raised",
        "neutra": "closed lips, calm face", "eee": "lips pulled wide singing an E sound, teeth visible"}
a = sys.argv[1:]
if "--lista" in a: print(list(EXPR)); sys.exit()
src, out = a[0], a[1]
box = tuple(int(v) for v in a[a.index("--mouth") + 1].split(",")) if "--mouth" in a else (196, 262, 322, 352)
solo = a[a.index("--solo") + 1].split(",") if "--solo" in a else list(EXPR)
from diffusers import StableDiffusionInpaintPipeline, LCMScheduler
torch.set_num_threads(4)
pipe = StableDiffusionInpaintPipeline.from_pretrained("stable-diffusion-v1-5/stable-diffusion-inpainting", torch_dtype=torch.float32, safety_checker=None)
pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config); pipe.load_lora_weights("latent-consistency/lcm-lora-sdv1-5")
im = Image.open(src).convert("RGB"); mask = Image.new("L", im.size, 0); ImageDraw.Draw(mask).ellipse(box, fill=255); mask = mask.filter(ImageFilter.GaussianBlur(6))
os.makedirs(out, exist_ok=True)
for k in solo:
    t = time.time()
    r = pipe(f"gta4art style, digital painting, close-up face of a man, {EXPR[k]}", negative_prompt="blurry, deformed, extra mouth, text, photo", image=im, mask_image=mask, width=im.width, height=im.height,
             num_inference_steps=8, guidance_scale=2.2, strength=1.0, padding_mask_crop=48, generator=torch.Generator().manual_seed(3)).images[0]
    r.save(os.path.join(out, f"{k}.png")); print("ok", k, round(time.time() - t, 1), "s", flush=True)
