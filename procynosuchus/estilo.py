#!/usr/bin/env python3
"""Arma y pinta las imágenes de la hoja de estilo (01 valle con animal, 03 animal de cerca)."""
import subprocess, sys
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
import pintor

CROP = (540, 0, 2460, 1080)

def animal(s, ox, oy, tag):
    subprocess.run([sys.executable, 'animal.py', f'out/est/an_{tag}.png', '--s', str(s), '--ox', str(ox), '--oy', str(oy), '--mask', f'out/est/an_{tag}_m.png'], check=True)
    return Image.open(f'out/est/an_{tag}.png'), Image.open(f'out/est/an_{tag}_m.png')

def place(base, an, shadow_box, amb=(0.93, 0.98, 1.05), sprouts=None, seed=3):
    """pega el animal en la escena: sombra en el suelo, leve tinte frío y brotes por delante de las patas"""
    base = base.convert('RGB')
    sh = Image.new('L', base.size, 0)
    ImageDraw.Draw(sh).ellipse(shadow_box, fill=190)
    sh = sh.filter(ImageFilter.GaussianBlur(24))
    base = Image.composite(Image.new('RGB', base.size, (6, 18, 24)), base, sh)
    a = np.asarray(an, dtype=np.float32) / 255
    rgb = np.clip(a[..., :3] * np.array(amb), 0, 1)
    an2 = Image.fromarray((np.dstack([rgb, a[..., 3]]) * 255).astype(np.uint8), 'RGBA')
    base.paste(an2, (0, 0), an2)
    if sprouts:
        import random
        rnd = random.Random(seed)
        d = ImageDraw.Draw(base)
        cols = [(22, 96, 70), (40, 140, 90), (26, 110, 116), (90, 180, 110), (120, 96, 190), (160, 210, 180)]
        for (x0, x1, y, h) in sprouts:
            for _ in range(int((x1 - x0) / 5)):
                x = rnd.uniform(x0, x1); hh = h * rnd.uniform(0.4, 1.0); lean = rnd.uniform(-0.35, 0.35) * hh
                d.line([(x, y + rnd.uniform(-4, 8)), (x + lean * 0.5, y - hh * 0.6), (x + lean, y - hh)], fill=rnd.choice(cols), width=rnd.choice([2, 3, 3, 4]))
    return base

def run(which):
    if '01' in which:
        bg = Image.open('out/est/element-4.png').crop(CROP)
        fg = Image.open('out/est/element-5.png').crop(CROP)
        an, mk = animal(1.22, 560, 338, 'a')
        im = place(bg, an, (700, 835, 1420, 912), sprouts=[(760, 880, 868, 34), (990, 1100, 868, 40), (1250, 1330, 800, 26)])
        im.paste(fg, (0, 0), fg)
        out = pintor.paint(im, [44, 22, 11, 6, 3], mask=mk, relief=0.5)
        pintor.grade(out, 0.88, 0.0, 1.08, 0.3).save('estilo/01_valle.jpg', quality=93)
    if '03' in which:
        bg = Image.open('out/est/element-6.png').crop(CROP)
        an, mk = animal(2.3, 130, -70, 'b')
        im = place(bg, an, (480, 880, 1760, 1010))
        out = pintor.paint(im, [40, 20, 10, 6, 3], mask=mk, relief=0.5)
        pintor.grade(out, 0.9, 0.0, 1.08, 0.3).save('estilo/03_animal.jpg', quality=93)

def plantas():
    bg = Image.open('out/est2/element-4.png'); fg = Image.open('out/est2/element-5.png')
    box = (3500, 0, 5420, 1080)
    im = bg.crop(box).convert('RGB'); f = fg.crop((3500, 1080, 5420, 2160))
    out = pintor.paint(im, [34, 17, 9, 5, 3], relief=0.5)
    pintor.grade(out, 0.9, 0.0, 1.08, 0.25).save('estilo/02a_arbol.jpg', quality=93)
    box2 = (1080, 1180, 2820, 2160)
    im2 = bg.crop(box2).convert('RGB'); f2 = fg.crop(box2); im2.paste(f2, (0, 0), f2)
    im2 = im2.resize((1920, 1080), Image.LANCZOS)
    out = pintor.paint(im2, [34, 17, 9, 5, 3], relief=0.5)
    pintor.grade(out, 0.9, 0.0, 1.08, 0.25).save('estilo/02b_primer_plano.jpg', quality=93)

if __name__ == '__main__':
    if 'plantas' in sys.argv:
        plantas(); sys.exit()
    run(sys.argv[1:] or ['01', '03'])
