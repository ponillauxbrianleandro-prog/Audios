#!/usr/bin/env python3
"""Crea cualquier personaje en el estilo 80 % GTA IV pintado + 20 % realismo GTA VI a partir de una ficha JSON (ver personaje_plantilla.json).
Requiere el servidor Flux arriba (bash extra/herramientas_ia/arrancar.sh --servidor). Genera maestro + poses + expresiones y recortes (rembg).
Uso: python3 crear_personaje.py ficha.json [--solo maestro|poses|expresiones|recortes]   -> extra/personajes/<nombre>/"""
import json, os, subprocess, sys
f = json.load(open(sys.argv[1])); solo = sys.argv[sys.argv.index("--solo") + 1] if "--solo" in sys.argv else "todo"
AQUI = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(AQUI, "..", "personajes", f["nombre"]); os.makedirs(D, exist_ok=True)
m = f.get("mezcla", {"gta4": .8, "gta6": .2})
LORA = f"<lora:lora_gta4_vibe_flux:{m['gta4']}><lora:lora_gta6_loading_flux:{m['gta6']}>"
STY = "gta4art painting, GTA IV loading screen artwork by Rockstar, painterly shading with hard cool teal shadow planes, soft painted edges"
REAL = "subtle realistic skin pores and fabric texture, strong form lighting, depth of field"
BASE = f"{f['descripcion']}, {f['vestuario']}"
def gen(nombre, accion, seed):
    out = os.path.join(D, nombre + ".png")
    if not os.path.exists(out): subprocess.run([sys.executable, os.path.join(AQUI, "flux_gen.py"), out, f"{STY}, {REAL}, {BASE}, {accion}, {f.get('ambiente','')} {LORA}", "--seed", str(seed)], check=True)
if solo in ("todo", "maestro"): gen("maestro", f["accion_base"], 7)
if solo in ("todo", "poses"):
    for i, (k, v) in enumerate(f.get("poses", {}).items()): gen("pose_" + k, v, 21 + i)
if solo in ("todo", "expresiones"):
    for i, (k, v) in enumerate(f.get("expresiones", {}).items()): gen("expr_" + k, v, 31 + i)
if solo in ("todo", "recortes"):
    os.makedirs(os.path.join(D, "recortes"), exist_ok=True)
    for p in sorted(os.listdir(D)):
        if p.endswith(".png"): subprocess.run(["/root/ia/venv/bin/rembg", "i", os.path.join(D, p), os.path.join(D, "recortes", p)])
json.dump(f, open(os.path.join(D, "ficha.json"), "w"), indent=1, ensure_ascii=False); print("listo ->", D)
