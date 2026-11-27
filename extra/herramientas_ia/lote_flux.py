#!/usr/bin/env python3
"""Lote reanudable de imagenes del cantante con Flux: salta las que ya existen. Uso: python3 lote_flux.py <carpeta_salida> [--fase ab|poses|expr]"""
import os, subprocess, sys
D = sys.argv[1]; fase = sys.argv[sys.argv.index("--fase") + 1] if "--fase" in sys.argv else "ab"
os.makedirs(D, exist_ok=True)
CHAR = ("a muscular 1980s rockabilly singer, tall black pompadour quiff piled high and swept back, dark wayfarer sunglasses, short black leather jacket, sheer white t-shirt, "
        "thick gold chain with round gold links and a large medallion with rock symbols, black leather gloves, brown belt with black details, black pants, black boots")
STY = "gta4art painting, GTA IV loading screen artwork by Rockstar, painterly shading with hard cool teal shadow planes, soft painted edges, desaturated pale city background"
L_IV = "<lora:lora_gta4_vibe_flux:0.8>"; L_MIX = "<lora:lora_gta4_vibe_flux:0.8><lora:lora_gta6_loading_flux:0.2>"
REAL = "subtle realistic skin pores and fabric texture, strong form lighting, depth of field"
POSES = {"cantando": "singing into a vintage microphone on a stand", "puno_arriba": "raising his right fist high in the air, shouting", "brazos_abiertos": "arms spread wide, head tilted back, singing",
         "senalando": "pointing at the viewer with a smirk", "perfil": "side profile view singing, microphone near his lips", "contrapicado": "extreme low angle shot looking up at him, wide angle lens perspective, singing",
         "rodilla": "kneeling on one knee at the edge of a stage, reaching out a hand while singing", "espalda": "seen from behind and slightly to the side, looking over his shoulder"}
EXPR = {"grito": "extreme close-up portrait, screaming into the microphone, intense", "sonrisa": "extreme close-up portrait, big charismatic smile showing teeth", "ceno": "extreme close-up portrait, angry frown, tense jaw",
        "guino": "extreme close-up portrait, smirking confidently, chin up", "ooh": "extreme close-up portrait, lips rounded singing a long note, eyes hidden behind sunglasses"}
jobs = []
if fase == "ab":
    jobs = [("ab_iv_solo", f"{STY}, {CHAR}, singing into a vintage microphone {L_IV}", 11), ("ab_mezcla_80_20", f"{STY}, {REAL}, {CHAR}, singing into a vintage microphone {L_MIX}", 11)]
elif fase == "poses":
    jobs = [(f"pose_{k}", f"{STY}, {REAL}, {CHAR}, {v} {L_MIX}", 21) for k, v in POSES.items()]
else:
    jobs = [(f"expr_{k}", f"{STY}, {REAL}, {CHAR}, {v} {L_MIX}", 31) for k, v in EXPR.items()]
for nombre, prompt, seed in jobs:
    out = os.path.join(D, nombre + ".png")
    if os.path.exists(out): continue
    h = "768"
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "flux_gen.py"), out, prompt, "--seed", str(seed), "--h", h], check=True)
