"""Hoja de contactos de todas las especies + escena de prueba en capas.
Uso:  python3 hoja_plantas.py [salida_dir] [paleta_escena]"""
import os
import sys
import time
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paletas
import plantas
import terreno
import variar

SALIDA = "/tmp/claude-0/-home-user-Audios/67bd3ee9-eab2-5673-a100-ae0a6af8a7c1/scratchpad"


def hoja(salida=SALIDA, nvar=5, celda=(300, 200)):
    cw, ch = celda
    esp = [e for e in plantas.ESPECIES]
    lab = 150
    img = Image.new('RGBA', (lab + nvar * cw, len(esp) * ch), (96, 96, 98, 255))
    d = ImageDraw.Draw(img)
    rg = np.random.default_rng(5)
    tiempos = {}
    for r, nom in enumerate(esp):
        d.text((8, r * ch + 8), nom, fill=(255, 255, 255, 255))
        for c in range(nvar):
            pal = paletas.PALETAS[paletas.NOMBRES[(r + c) % 7]] if c else paletas.PALETAS['verde']
            t = time.time()
            p = plantas.generar(nom, 100 + c * 7 + r, 380, pal)
            tiempos.setdefault(nom, []).append(time.time() - t)
            if c >= 2:
                p = variar.variante(p, rg, pal, .3)
            k = min((ch - 14) / p.height, (cw - 10) / p.width)
            p = variar.escala(p, k)
            bgc = Image.new('RGBA', (cw, ch), tuple(int(v) for v in pal['cielo'][1]) + (255,))
            bgc = Image.alpha_composite(bgc, Image.new('RGBA', (cw, ch), (0, 0, 0, 40)))
            img.alpha_composite(bgc, (lab + c * cw, r * ch))
            variar.pegar(img, p, lab + c * cw + cw / 2, r * ch + ch - 6)
    ruta = os.path.join(salida, "hoja_plantas.png")
    img.convert('RGB').save(ruta)
    return ruta, tiempos


def _biblioteca(pal, seed, nvar=4, h=520):
    lib = {}
    for nom in plantas.ESPECIES:
        lib[nom] = [plantas.generar(nom, seed * 1000 + i * 13 + len(nom), h, pal) for i in range(nvar)]
    return lib


def escena(pal, seed=1, w=1920, h=1080):
    rg = np.random.default_rng(seed)
    t0 = time.time()
    pal = paletas.obtener(pal)
    lib = _biblioteca(pal, seed)
    print("biblioteca", round(time.time() - t0, 1), "s")
    can = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    hor = int(h * .52)
    can.alpha_composite(terreno.cielo(w, hor + 40, pal, seed))
    can.alpha_composite(terreno.montanas(w, int(h * .45), pal, seed + 1, 3), (0, hor - int(h * .36)))
    # franja lejana
    tipo = {'ocre': 'arena', 'rojo': 'arcilla', 'ambar': 'arcilla', 'verde': 'barro', 'azul': 'lecho',
            'violeta': 'barro', 'ceniza': 'lecho'}[pal['nombre'].split('+')[0]]
    can.alpha_composite(terreno.suelo(w, int(h * .2), pal, seed + 2, tipo, piedras=10), (0, hor - 6))
    can.alpha_composite(terreno.rio(w, int(h * .1), pal, seed + 5), (0, int(h * .6)))

    def poner(nom, x, yb, alto, bruma=0., tinte=.0, blur=0., espejar=True, k=1.0):
        base = lib[nom][int(rg.integers(0, len(lib[nom])))]
        im = variar.escala(base, alto / base.height * rg.uniform(.9, 1.1), alto / base.height * rg.uniform(.9, 1.1))
        im = variar.variante(im, rg, pal, tinte, espejar, curv=.18, matiz_g=10)
        if bruma:
            im = variar.bruma(im, pal['bruma'], bruma, .85 - bruma * .3, .9 - bruma * .5)
        if k != 1.0:
            im = variar.brillo(im, k)
        if blur:
            im = variar.desenfoque(im, blur)
        variar.pegar(can, im, x, yb)

    arb = ['lepidodendron', 'sigillaria', 'cordaites', 'glossopteris', 'dicroidium', 'psaronius', 'cyathea', 'calamites']
    # capa 1 lejana (muy brumosa)
    for _ in range(170):
        yb = rg.uniform(hor + 8, hor + 70)
        nom = arb[int(rg.integers(0, len(arb)))]
        poner(nom, rg.uniform(-40, w + 40), yb, rg.uniform(50, 130) * (yb / hor), .6, .3)
    can.alpha_composite(terreno.suelo(w, int(h * .26), pal, seed + 3, tipo, piedras=14), (0, int(h * .64)))
    # capa 2 media
    medio = arb + ['equisetum', 'cicada', 'mata_seca', 'suculenta', 'welwitschia', 'prototaxites', 'helecho_suelo', 'roca_musgosa']
    puestos = sorted([(rg.uniform(int(h * .68), int(h * .86)), rg.uniform(-60, w + 60)) for _ in range(150)])
    for yb, x in puestos:
        nom = medio[int(rg.integers(0, len(medio)))]
        f = (yb - h * .6) / (h * .4)
        alto = rg.uniform(110, 300) * (.55 + f)
        if nom in ('helecho_suelo', 'roca_musgosa', 'mata_seca', 'welwitschia', 'suculenta'):
            alto *= .45
        poner(nom, x, yb, alto, .3 - f * .2, .22)
    can.alpha_composite(terreno.suelo(w, int(h * .24), pal, seed + 4, tipo, piedras=16), (0, int(h * .80)))
    # capa 3 cercana / sotobosque
    cerca = ['helecho_suelo', 'helecho_suelo', 'musgo', 'roca_musgosa', 'hongos', 'equisetum', 'tronco_caido',
             'liquen', 'mata_seca', 'calamites', 'piedra']
    puestos = sorted([(rg.uniform(int(h * .86), h + 20), rg.uniform(-80, w + 80)) for _ in range(80)])
    for yb, x in puestos:
        nom = cerca[int(rg.integers(0, len(cerca)))]
        f = (yb - h * .84) / (h * .2)
        alto = rg.uniform(60, 170) * (.8 + f * 1.1)
        if nom in ('tronco_caido',):
            alto *= .7
        poner(nom, x, yb, alto, 0, .12, 0, k=.92)
    # primer plano desenfocado en los bordes
    for sd, xr in ((0, (-60, w * .25)), (1, (w * .72, w + 60))):
        for _ in range(3):
            nom = ['helecho_suelo', 'cyathea', 'psaronius', 'equisetum', 'cordaites'][int(rg.integers(0, 5))]
            poner(nom, rg.uniform(*xr), h + rg.uniform(10, 120), rg.uniform(380, 650), 0, .1, rg.uniform(4, 8), k=.7)
    # viñeta y grano final
    a = np.asarray(can.convert('RGB'), np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    v = 1 - .35 * (((xx - w / 2) / (w / 2)) ** 2 * .6 + ((yy - h / 2) / (h / 2)) ** 2 * .6)
    a *= v[..., None]
    print("escena", round(time.time() - t0, 1), "s")
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


if __name__ == "__main__":
    sal = sys.argv[1] if len(sys.argv) > 1 else SALIDA
    os.makedirs(sal, exist_ok=True)
    pal = sys.argv[2] if len(sys.argv) > 2 else 'verde'
    ruta, tiempos = hoja(sal)
    print(ruta)
    for k, v in tiempos.items():
        print(f"{k:16s} {np.mean(v):.2f}s (max {np.max(v):.2f})")
    e = escena(pal)
    e.save(os.path.join(sal, f"escena_prueba_{pal}.png"))
