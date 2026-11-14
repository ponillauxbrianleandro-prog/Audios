#!/usr/bin/env python3
"""Estilo 2 — hoja de libreta de campo dibujada a lápiz.

El papel se genera (fibra, manchas, renglones). Los dibujos se hacen con grafito simulado:
contorno repasado con pulso, sombreado por tramado en varias direcciones según la luz y
grano del papel. El animal usa la misma anatomía que el estilo documental.

Uso: libreta.py salida.jpg
"""
import math
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import animal as animal_mod
from retrato import font

W, H = 1920, 1080
GRAF = np.array([52, 50, 58], dtype=np.float32)


def ruido(shape, cell, seed):
    rs = np.random.RandomState(seed)
    small = rs.rand(int(shape[0] / cell) + 3, int(shape[1] / cell) + 3)
    return np.asarray(Image.fromarray((small * 255).astype(np.uint8)).resize((shape[1], shape[0]), Image.BICUBIC), dtype=np.float32) / 255


def papel():
    rs = np.random.RandomState(1)
    p = np.zeros((H, W, 3), dtype=np.float32) + np.array([233, 223, 196])
    p *= (0.93 + ruido((H, W), 220, 2)[..., None] * 0.12)
    p += rs.normal(0, 3.2, (H, W, 1))
    fib = ruido((H, W), 3, 3) - 0.5
    p += fib[..., None] * 9
    for i in range(9):  # manchas de uso
        cx, cy, r = rs.rand() * W, rs.rand() * H, 60 + rs.rand() * 200
        yy, xx = np.mgrid[0:H, 0:W]
        m = np.exp(-(((xx - cx) / r) ** 2 + ((yy - cy) / (r * 0.7)) ** 2) * 2.2)
        p -= m[..., None] * np.array([14, 18, 26]) * (0.4 + rs.rand() * 0.7)
    for y in range(120, H - 40, 46):  # renglones tenues
        p[y:y + 2, 70:W - 50] = p[y:y + 2, 70:W - 50] * 0.9 + np.array([120, 150, 176]) * 0.1
    p[40:H - 30, 150:152] = p[40:H - 30, 150:152] * 0.75 + np.array([196, 92, 86]) * 0.25
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    p *= (1 - 0.2 * np.clip(d - 0.6, 0, 1) ** 1.4)[..., None]
    return p


class Lapiz:
    def __init__(self, base):
        self.g = np.zeros((H, W), dtype=np.float32)   # cantidad de grafito 0..1
        self.base = base
        self.rnd = random.Random(7)
        self.tooth = 0.55 + ruido((H, W), 2.2, 9) * 0.75
        self.wob = (ruido((H, W), 60, 5) - 0.5)

    def trazo(self, pts, w=2.2, a=0.6, pasadas=2, jit=1.6):
        """línea de contorno repasada, con pulso"""
        for k in range(pasadas):
            im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
            ox, oy = self.rnd.uniform(-jit, jit), self.rnd.uniform(-jit, jit)
            q = [(x + ox + self.rnd.uniform(-0.7, 0.7), y + oy + self.rnd.uniform(-0.7, 0.7)) for x, y in pts]
            d.line(q, fill=255, width=max(1, int(round(w))), joint='curve')
            self.g = np.maximum(self.g, np.asarray(im.filter(ImageFilter.GaussianBlur(0.6)), dtype=np.float32) / 255 * a * self.rnd.uniform(0.75, 1.0))

    def trama(self, oscuro, mask, niveles=((0.18, 0.5, 7.0), (0.36, -0.45, 6.0), (0.56, 1.25, 5.0), (0.74, 0.0, 4.5)), a=0.5):
        """sombreado por tramado: cada nivel de sombra suma una dirección de líneas"""
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        for (thr, ang, sep) in niveles:
            u = xx * math.sin(ang) + yy * math.cos(ang) + self.wob * 26
            line = (np.mod(u, sep) < 1.5).astype(np.float32)
            seg = (ruido((H, W), 18, int(thr * 100)) > 0.22).astype(np.float32)  # líneas que se cortan, a mano
            m = np.clip((oscuro - thr) * 6, 0, 1) * mask
            self.g = np.maximum(self.g, line * seg * m * a)

    def contorno(self, alpha, a=0.75, w=1.4):
        e = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(w)), dtype=np.float32) / 255
        sh = np.roll(np.roll(e, 2, axis=1), 1, axis=0)
        self.g = np.maximum(self.g, np.clip(e * 3.2, 0, 1) * a)
        self.g = np.maximum(self.g, np.clip(sh * 2.4, 0, 1) * a * 0.6)

    def aplicar(self):
        g = np.clip(self.g * self.tooth, 0, 1)[..., None]
        return self.base * (1 - g * 0.92) + GRAF * g * 0.92


def figura_animal(L, s, ox, oy):
    A = animal_mod.build(W, H, (ox, oy, s))
    lum = np.clip(A.rgb, 0, 1).mean(axis=2)
    al = np.clip(A.alpha, 0, 1)
    osc = np.clip(1.0 - lum * 1.55, 0, 1)
    L.trama(osc, (al > 0.5).astype(np.float32))
    L.contorno(al)
    # sombra en el piso, tramada
    yy, xx = np.mgrid[0:H, 0:W]
    xs = np.nonzero(al.max(axis=0) > 0.5)[0]; by = np.nonzero(al.max(axis=1) > 0.5)[0].max()
    sh = np.exp(-(((xx - (xs.min() + xs.max()) / 2) / ((xs.max() - xs.min()) * 0.45)) ** 2 + ((yy - by + 4) / 16.0) ** 2) * 2)
    L.trama(sh * 0.7, (al < 0.5).astype(np.float32), niveles=((0.2, 1.57, 5.0), (0.45, 1.3, 4.5)), a=0.42)
    return A


def poly(pts, n=10):
    return animal_mod.spline(pts, n, True) + [animal_mod.spline(pts, n, True)[0]]


def craneo(L, x, y, s):
    T = lambda pts: [(x + px * s, y + py * s) for px, py in pts]
    sk = [(0, 40), (10, 14), (44, 0), (96, 2), (140, 14), (172, 30), (180, 52), (170, 66), (120, 70), (70, 74), (30, 78), (4, 66)]
    L.trazo(T(poly(sk)), 2.6, 0.72)
    L.trazo(T(poly([(58, 18), (76, 14), (88, 24), (80, 38), (62, 38), (54, 28)])), 2.0, 0.7)          # órbita
    L.trazo(T(poly([(14, 26), (36, 20), (46, 34), (38, 50), (18, 52)])), 2.0, 0.6)                  # fosa temporal
    L.trazo(T(poly([(162, 30), (169, 28), (171, 34), (165, 37)], 6)), 1.6, 0.7)                     # narina
    jw = [(6, 74), (40, 84), (100, 82), (150, 76), (172, 72), (176, 84), (150, 100), (90, 106), (30, 102), (2, 92)]
    L.trazo(T(poly(jw)), 2.6, 0.72)
    L.trazo(T([(8, 88), (60, 94), (120, 90)]), 1.4, 0.4)
    for i in range(5):   # incisivos
        tx = 172 - i * 7; L.trazo(T([(tx - 3, 66), (tx, 77), (tx + 3, 66)]), 1.5, 0.75, 1)
    L.trazo(T([(132, 68), (135, 88), (140, 68)]), 1.8, 0.8, 1)                                        # colmillo
    for i in range(7):   # postcaninos con varias puntas
        tx = 118 - i * 12
        L.trazo(T([(tx - 5, 70), (tx - 3, 76), (tx - 1, 73), (tx + 1, 80), (tx + 3, 73), (tx + 5, 76), (tx + 6, 70)]), 1.4, 0.75, 1)
    # tramado de volumen
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon(T(animal_mod.spline(sk, 10)), fill=255)
    ma = np.asarray(m, dtype=np.float32) / 255
    yy, xx = np.mgrid[0:H, 0:W]
    osc = np.clip(((yy - y) / (80 * s)) * 0.75 + 0.05, 0, 1)
    L.trama(osc, ma, niveles=((0.25, 0.6, 6.5), (0.5, -0.5, 5.5)), a=0.36)
    return T


def hoja(L, x, y, ln, rot):
    c, s = math.cos(rot), math.sin(rot)
    R = lambda px, py: (x + px * c - py * s, y + px * s + py * c)
    top = [R(ln * t, -math.sin(math.pi * t ** 0.85) * ln * 0.17) for t in np.linspace(0, 1, 26)]
    bot = [R(ln * t, math.sin(math.pi * t ** 0.85) * ln * 0.17) for t in np.linspace(1, 0, 26)]
    L.trazo(top + bot + [top[0]], 2.4, 0.7)
    L.trazo([R(-ln * 0.12, 0), R(ln, 0)], 2.2, 0.7)
    for i in range(1, 17):
        t = i / 17; w = math.sin(math.pi * t ** 0.85) * ln * 0.16
        for sg in (-1, 1):
            L.trazo([R(ln * t - ln * 0.04, 0), R(ln * t, sg * w * 0.55), R(ln * t + ln * 0.035, sg * w * 0.96)], 1.1, 0.42, 1)


def persona(L, x, y, s):
    """paleontólogo genérico de campo, agachado con un pincel; no retrata a nadie"""
    T = lambda pts: [(x + px * s, y + py * s) for px, py in pts]
    partes = [
        [(-64, -168), (-10, -180), (44, -170), (50, -162), (-8, -158), (-66, -160)],                 # ala del sombrero
        [(-30, -172), (-24, -198), (10, -202), (26, -176)],                                         # copa
        [(-22, -160), (16, -162), (24, -138), (10, -118), (-14, -120), (-26, -140)],                # cabeza
        [(-34, -118), (22, -122), (52, -70), (40, -8), (-22, -6), (-46, -60)],                      # torso inclinado
        [(30, -100), (70, -70), (96, -30), (86, -20), (58, -52), (24, -76)],                        # brazo
        [(84, -30), (100, -20), (112, 8), (104, 12)],                                               # pincel
        [(-30, -14), (36, -16), (78, -4), (84, 30), (40, 34), (-10, 22)],                           # muslo
        [(38, 22), (84, 22), (88, 78), (60, 80), (44, 50)],                                         # pierna apoyada
        [(-24, 8), (10, 20), (-10, 70), (-56, 78), (-70, 62), (-36, 50)],                           # pierna doblada
        [(52, 76), (104, 76), (110, 92), (50, 92)],                                                 # bota
    ]
    yy, xx = np.mgrid[0:H, 0:W]
    for i, p in enumerate(partes):
        pts = T(animal_mod.spline(p, 8))
        L.trazo(pts + [pts[0]], 2.0, 0.68)
        m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon(pts, fill=255)
        ma = np.asarray(m, dtype=np.float32) / 255
        xs = [q[0] for q in pts]
        osc = np.clip((xx - min(xs)) / max(1, (max(xs) - min(xs))) * 0.8 + (0.25 if i in (0, 3, 6, 9) else 0.05), 0, 1)
        L.trama(osc, ma, niveles=((0.3, 0.7, 6.0), (0.55, -0.5, 5.0), (0.78, 1.3, 4.5)), a=0.4)
    L.trazo(T([(-90, 94), (150, 94)]), 1.6, 0.5)
    L.trazo(T([(96, 86), (120, 78), (146, 88), (126, 94)]), 1.6, 0.6)   # hueso que asoma


def nota(d, xy, txt, size=26, rot=0, fill=(62, 58, 70), serif=True):
    f = font(size, serif=serif)
    if not rot:
        d.text(xy, txt, font=f, fill=fill); return
    w = int(d.textlength(txt, font=f)) + 12
    t = Image.new('RGBA', (w, size + 16), (0, 0, 0, 0)); ImageDraw.Draw(t).text((4, 4), txt, font=f, fill=fill + (255,))
    t = t.rotate(rot, expand=True, resample=Image.BICUBIC)
    d._image.paste(t, (int(xy[0]), int(xy[1])), t)


if __name__ == '__main__':
    dst = sys.argv[1] if len(sys.argv) > 1 else 'estilo/E2_libreta.jpg'
    L = Lapiz(papel())
    figura_animal(L, 1.5, 150, 110)
    T = craneo(L, 1330, 150, 2.6)
    hoja(L, 1300, 600, 360, -0.2)
    persona(L, 1690, 930, 0.78)
    rnd = L.rnd
    # líneas de llamada
    for a, b in [((1330 + 172 * 2.6, 150 + 80 * 2.6), (1810, 420)), ((1330 + 136 * 2.6, 150 + 90 * 2.6), (1740, 462)), ((1330 + 70 * 2.6, 150 + 80 * 2.6), (1470, 448)), ((1330 + 72 * 2.6, 150 + 26 * 2.6), (1480, 120))]:
        L.trazo([a, b], 1.2, 0.45, 1)
    L.trazo([(190, 762), (1235, 762)], 1.4, 0.5, 1); L.trazo([(190, 750), (190, 774)], 1.4, 0.5, 1); L.trazo([(1235, 750), (1235, 774)], 1.4, 0.5, 1)
    im = Image.fromarray(np.clip(L.aplicar(), 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    nota(d, (180, 64), 'Procynosuchus delaharpeae', 46, 1.2)
    nota(d, (184, 124), 'cinodonto · Pérmico tardío · ≈ 255 Ma', 26)
    nota(d, (640, 776), '≈ 60 cm', 28)
    nota(d, (200, 836), 'cola larga, casi la mitad del cuerpo — ¿nadaba? (Kemp, 1980)', 25, 0.6)
    nota(d, (200, 884), 'patas abiertas hacia los costados; boca cerrada, asoma el colmillo', 25, -0.4)
    nota(d, (200, 932), 'fósiles: Sudáfrica · Zambia · Tanzania · Alemania', 25, 0.3)
    nota(d, (1790, 424), 'incisivos', 23); nota(d, (1700, 466), 'colmillo', 23); nota(d, (1340, 452), 'muelas con varias puntas', 23)
    nota(d, (1440, 84), 'órbita', 23); nota(d, (1330, 100), 'cráneo', 30, 1.5)
    nota(d, (1290, 662), 'Glossopteris — hoja en forma de lengua', 24, -0.8)
    nota(d, (1340, 960), 'trabajo de campo', 24, 0.8)
    nota(d, (60, 1030), 'ESTILO 2 · LIBRETA A LÁPIZ', 20, 0, (120, 110, 100), serif=False)
    im.save(dst, quality=94)
    print('ok', dst)
