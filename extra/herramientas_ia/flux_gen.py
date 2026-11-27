#!/usr/bin/env python3
"""Cliente del servidor Flux (stable-diffusion.cpp sd-server en localhost:1234). Sin dependencias (solo stdlib).
Uso: python3 flux_gen.py salida.png "prompt <lora:lora_gta4_vibe_flux:0.8>" [--w 512 --h 768 --steps 4 --seed 7]
Lanzar el servidor antes: nohup bash /root/ia/servidor_flux.sh &   (tarda ~5 min en cargar; luego ~2-8 min por imagen)"""
import base64, json, sys, time, urllib.request
a = sys.argv[1:]; out, prompt = a[0], a[1]
opt = lambda n, d: type(d)(a[a.index("--" + n) + 1]) if "--" + n in a else d
body = {"prompt": prompt, "width": opt("w", 512), "height": opt("h", 768), "steps": opt("steps", 4), "seed": opt("seed", 7), "cfg_scale": 1.0, "batch_size": 1}
t = time.time()
r = urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:1234/sdapi/v1/txt2img", json.dumps(body).encode(), {"Content-Type": "application/json"}), timeout=3600)
open(out, "wb").write(base64.b64decode(json.load(r)["images"][0])); print("listo", out, round(time.time() - t), "s")
