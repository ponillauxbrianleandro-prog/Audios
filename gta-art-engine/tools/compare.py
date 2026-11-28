"""Contacto lado a lado: resultado vs imágenes de referencia, para revisión visual.
Uso: python tools/compare.py out/vaquero-posing.png ref1.jpg [ref2.jpg ...] -o work/compare.png"""
import sys, argparse
from PIL import Image
ap = argparse.ArgumentParser(); ap.add_argument("result"); ap.add_argument("refs", nargs="*"); ap.add_argument("-o", default="work/compare.png")
a = ap.parse_args()
ims = [Image.open(p).convert("RGB") for p in [a.result] + a.refs]
h = 800
ims = [i.resize((int(i.width * h / i.height), h)) for i in ims]
sheet = Image.new("RGB", (sum(i.width for i in ims), h), (20, 20, 20))
x = 0
for i in ims: sheet.paste(i, (x, 0)); x += i.width
sheet.save(a.o); print("OK", a.o)
