#!/usr/bin/env python3
"""Registra un SVG propio en el catalogo del mundo.
Uso: python3 agregar_asset.py archivo.svg --id mi_asset --cat basura --desc "..." [--tags a,b] [--rol fondo|sujeto] [--ancla base|centro]
Copia el SVG a assets/<cat>/ y actualiza catalogo.json (reemplaza si el id ya existe)."""
import argparse, json, os, re, shutil

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = argparse.ArgumentParser()
p.add_argument("svg"); p.add_argument("--id", required=True); p.add_argument("--cat", required=True)
p.add_argument("--desc", default=""); p.add_argument("--tags", default=""); p.add_argument("--rol", default="fondo"); p.add_argument("--ancla", default="base")
a = p.parse_args()
txt = open(a.svg, encoding="utf-8").read()
m = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"', txt)
if not m:
    raise SystemExit("el SVG necesita viewBox")
w, h = int(float(m[1])), int(float(m[2]))
dest = os.path.join(RAIZ, "assets", a.cat); os.makedirs(dest, exist_ok=True)
shutil.copy(a.svg, os.path.join(dest, a.id + ".svg"))
cp = os.path.join(RAIZ, "catalogo.json"); cat = json.load(open(cp, encoding="utf-8"))
cat["assets"] = [x for x in cat["assets"] if x["id"] != a.id]
cat["assets"].append(dict(id=a.id, cat=a.cat, w=w, h=h, desc=a.desc, rol=a.rol, ancla=a.ancla, tags=[t for t in a.tags.split(",") if t], archivo=f"assets/{a.cat}/{a.id}.svg"))
json.dump(cat, open(cp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"asset {a.id} agregado ({len(cat['assets'])} en total). Nota: generar_assets.py NO lo pisa si no esta registrado alli; hacer commit.")
