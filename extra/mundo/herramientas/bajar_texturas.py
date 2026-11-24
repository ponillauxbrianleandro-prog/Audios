#!/usr/bin/env python3
"""Descarga texturas CC0 de ambientCG y las 'pinta' (paint-over estilo GTA IV) -> mundo/texturas/*.webp
Uso: python3 bajar_texturas.py   (idempotente; guarda creditos en texturas/CREDITOS.json)"""
import io, json, os, re, urllib.parse, urllib.request, zipfile
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(RAIZ, "texturas")
os.makedirs(OUT, exist_ok=True)
# nombre local -> (busqueda ambientCG, saturacion final)
MATERIALES = {
    "ladrillo": ("Bricks059", .75), "piedra": ("Bricks075A", .8), "asfalto": ("Asphalt031", .6), "concreto": ("Concrete034", .6),
    "vereda": ("PavingStones070", .6), "madera": ("WoodFloor064", .75), "metal_oxidado": ("Rust004", .8), "chapa_pintada": ("CorrugatedSteel005", .8),
    "cuero": ("Leather011", .8), "tela": ("Fabric026", .75), "hojas": ("Ground037", .85), "tierra": ("Ground054", .7), "pasto": ("Grass005", .8),
    "revoque": ("Plaster003", .6), "baldosa_damero": ("Tiles074", .65), "carton": ("Cardboard004", .8), "goma": ("Rubber004", .5), "vidrio_sucio": ("Facade001", .5),
}


UA = {"User-Agent": "Mozilla/5.0"}


def get(u, t=90):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t).read()


def api(q):
    u = f"https://ambientcg.com/api/v2/full_json?type=Material&q={urllib.parse.quote(q)}&limit=1&sort=popular"
    return json.loads(get(u, 30))["foundAssets"][0]["assetId"]


def pintar(im, sat, size=768):
    im = im.convert("RGB"); w, h = im.size; s = min(w, h)
    im = im.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2)).resize((size, size), Image.LANCZOS)
    im = im.filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.UnsharpMask(radius=3, percent=70, threshold=2))  # pinceladas
    a = np.asarray(im).astype(np.float32) / 255
    a = np.clip((a - .5) * 1.12 + .5, 0, 1)                      # contraste
    a[..., 0] *= .97; a[..., 2] *= 1.04                          # leve grading frio
    im = Image.fromarray((a * 255).astype(np.uint8))
    return ImageEnhance.Color(im).enhance(sat)


def main():
    cred = {}
    for nombre, (q, sat) in MATERIALES.items():
        dest = os.path.join(OUT, nombre + ".webp")
        if os.path.exists(dest): continue
        try:
            aid = q if re.match(r"^[A-Z][A-Za-z]+\d+", q) else api(q)
            data = get(f"https://ambientcg.com/get?file={aid}_1K-JPG.zip")
            z = zipfile.ZipFile(io.BytesIO(data))
            f = [n for n in z.namelist() if n.endswith("_Color.jpg")][0]
            pintar(Image.open(io.BytesIO(z.read(f))), sat).save(dest, "WEBP", quality=80)
            cred[nombre] = f"ambientCG {aid} (CC0)"
            print("ok", nombre, aid, os.path.getsize(dest) // 1024, "KB")
        except Exception as e:
            print("fallo", nombre, e)
    cp = os.path.join(OUT, "CREDITOS.json")
    old = json.load(open(cp)) if os.path.exists(cp) else {}
    old.update(cred); json.dump(old, open(cp, "w"), indent=1)


if __name__ == "__main__":
    main()
