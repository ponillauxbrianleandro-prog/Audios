#!/usr/bin/env python3
"""Procynosuchus realista, punto por punto.

Cada parte del cuerpo es una silueta dibujada a mano (según la reconstrucción de referencia,
vista en tres cuartos). A cada silueta se le calcula un volumen ("inflado"), se le suma relieve
de escamas y arrugas, y cada píxel recibe su color (lomo rosado-malva con manchas violáceas,
flancos pardo-oliva, vientre oscuro) y su luz. Sale un PNG con transparencia.

Uso: animal.py salida.png [--w 1920 --h 1080] [--mask mascara.png]
"""
import argparse

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SS = 2  # supermuestreo


def spline(pts, n=14, closed=True):
    P = np.array(pts, dtype=np.float64)
    m = len(P)
    out = []
    rng = range(m) if closed else range(m - 1)
    for i in rng:
        p0, p1, p2, p3 = P[(i - 1) % m], P[i], P[(i + 1) % m], P[(i + 2) % m]
        if not closed:
            p0 = P[max(0, i - 1)]; p3 = P[min(m - 1, i + 2)]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    return [tuple(q) for q in out]


def noise(shape, cell, seed, octaves=3):
    """ruido de valor suave en 0..1"""
    H, W = shape
    rs = np.random.RandomState(seed)
    acc = np.zeros(shape, dtype=np.float32); amp = 1.0; tot = 0.0
    for o in range(octaves):
        c = max(2, cell / (2 ** o))
        small = rs.rand(int(H / c) + 3, int(W / c) + 3).astype(np.float32)
        im = Image.fromarray((small * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
        acc += np.asarray(im, dtype=np.float32) / 255 * amp; tot += amp; amp *= 0.5
    return acc / tot


def gblur(a, r):
    im = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), dtype=np.float32) / 255


class Animal:
    def __init__(self, W, H, tx):
        self.W, self.H, self.tx = W, H, tx
        self.rgb = np.zeros((H, W, 3), dtype=np.float32)
        self.alpha = np.zeros((H, W), dtype=np.float32)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        self.xx, self.yy = xx, yy
        s = tx[2]
        self.s = s
        # texturas compartidas
        self.n_big = noise((H, W), 150 * s, 1)
        self.n_mid = noise((H, W), 46 * s, 2)
        self.n_fine = noise((H, W), 9 * s, 3, 2)
        self.n_warp = noise((H, W), 60 * s, 4)
        self.n_warp2 = noise((H, W), 60 * s, 5)

    def P(self, pts):
        ox, oy, s = self.tx
        return [(ox + x * s, oy + y * s) for x, y in pts]

    def mask(self, pts, closed=True, n=14):
        im = Image.new('L', (self.W * SS, self.H * SS), 0)
        ImageDraw.Draw(im).polygon([(x * SS, y * SS) for x, y in spline(self.P(pts), n, closed)], fill=255)
        return np.asarray(im.resize((self.W, self.H), Image.LANCZOS), dtype=np.float32) / 255

    def scales(self, freq, ang, strength=1.0):
        """relieve de escamas: rejilla deformada por ruido"""
        s = self.s
        u = self.xx * np.cos(ang) + self.yy * np.sin(ang) + (self.n_warp - 0.5) * 90 * s + (self.n_mid - 0.5) * 22 * s
        v = -self.xx * np.sin(ang) + self.yy * np.cos(ang) + (self.n_warp2 - 0.5) * 90 * s + (self.n_fine - 0.5) * 5 * s
        f = freq / s * (0.8 + self.n_big * 0.5)
        cell = np.abs(np.sin(u * f) * np.sin(v * f + np.floor(u * f / np.pi) * 1.57))
        return (cell ** 0.6) * strength

    def part(self, pts, thick, color_fn, depth=1.0, scale_f=0.42, scale_ang=0.3, scale_k=1.0, wrinkle=0.0, n=14, shade_k=1.0, fade=0.0):
        """pinta una parte: silueta -> volumen -> relieve -> color y luz por píxel"""
        m = self.mask(pts, n=n)
        if m.max() <= 0:
            return m
        s = self.s
        t = thick * s
        h = (gblur(m, t * 0.18) * 0.45 + gblur(m, t * 0.42) * 0.9 + gblur(m, t * 0.9) * 1.1) * m
        h = h * t * 1.25 * depth
        bump = self.scales(scale_f, scale_ang) * 0.6 * s * scale_k
        bump += (self.n_fine - 0.5) * 2.6 * s
        if wrinkle:
            wr = np.sin((self.xx * 0.9 + self.yy * 0.35) / (5.5 * s) + self.n_mid * 9) * (self.n_big - 0.3)
            bump += wr * wrinkle * 2.2 * s
        hh = h + bump * m
        gy, gx = np.gradient(hh)
        nz = np.ones_like(gx) * 1.0
        ln = np.sqrt(gx * gx + gy * gy + nz * nz)
        nx, ny, nzz = -gx / ln, -gy / ln, nz / ln
        L = np.array([-0.52, -0.66, 0.54]); L = L / np.linalg.norm(L)
        dif = np.clip(nx * L[0] + ny * L[1] + nzz * L[2], 0, 1)
        rim = np.clip(nx * 0.55 + ny * 0.62 + nzz * 0.1, 0, 1) ** 2  # luz fría de rebote, abajo a la derecha
        hv = np.array([-0.3, -0.45, 0.84])
        spec = np.clip(nx * hv[0] + ny * hv[1] + nzz * hv[2], 0, 1) ** 26
        col = color_fn(m)
        shade = (0.5 + 0.78 * dif) * shade_k
        out = col * shade[..., None]
        out *= (1 + (dif[..., None] - 0.5) * np.array([-0.05, 0.0, 0.07]))  # la luz de luna enfría las zonas iluminadas
        out += rim[..., None] * np.array([0.10, 0.22, 0.13]) * 0.6          # reflejo verdoso del musgo
        out += spec[..., None] * np.array([0.9, 0.95, 1.0]) * 0.05
        # oclusión en el borde: la silueta se oscurece hacia adentro
        edge = np.clip(gblur(m, t * 0.07) * 1.9 - 0.9, 0, 1)
        out *= (0.86 + 0.14 * edge)[..., None]
        a = m
        if fade:
            a = m * np.clip(self.vparam(m) / fade, 0, 1) ** 1.3  # se funde con el tronco arriba
        self.rgb = self.rgb * (1 - a[..., None]) + out * a[..., None]
        self.alpha = np.maximum(self.alpha, a)
        return m

    def vparam(self, m):
        """0 arriba, 1 abajo, dentro de la silueta (por columna)"""
        inside = m > 0.5
        top = np.where(inside.any(axis=0), inside.argmax(axis=0), 0).astype(np.float32)
        bot = np.where(inside.any(axis=0), self.H - 1 - inside[::-1].argmax(axis=0), 1).astype(np.float32)
        return np.clip((self.yy - top[None, :]) / np.maximum(1, (bot - top)[None, :]), 0, 1)

    # ---- colores (0..1) según la reconstrucción
    OLIVE = np.array([0.50, 0.45, 0.28]); OLIVE_D = np.array([0.34, 0.31, 0.21]); YEL = np.array([0.68, 0.58, 0.33])
    MAUVE = np.array([0.60, 0.41, 0.43]); PINK = np.array([0.74, 0.53, 0.50]); PURP = np.array([0.36, 0.23, 0.35]); BELLY = np.array([0.44, 0.40, 0.30])

    def body_col(self, split=0.52, blot=0.5):
        def fn(m):
            v = self.vparam(m)
            v = v + (self.n_mid - 0.5) * 0.22
            c = np.empty((self.H, self.W, 3), dtype=np.float32)
            dors = np.clip((split - v) / 0.16, 0, 1)[..., None]
            bel = np.clip((v - 0.8) / 0.15, 0, 1)[..., None]
            flank = self.OLIVE + (self.YEL - self.OLIVE) * np.clip((self.n_big - 0.45) * 3, 0, 1)[..., None]
            back = self.MAUVE + (self.PINK - self.MAUVE) * np.clip((self.n_mid - 0.4) * 2.5, 0, 1)[..., None]
            c = flank * (1 - dors) + back * dors
            c = c * (1 - bel) + self.BELLY * bel
            # manchas violáceas irregulares en el lomo, que bajan en bandas por el flanco
            bands = np.sin(self.xx / (21 * self.s) + self.n_big * 7) * 0.5 + 0.5
            bl = np.clip((self.n_mid * 0.75 + bands * 0.4 - (0.6 + v * 0.62) * (1.15 - blot)) * 5, 0, 1)[..., None]
            c = c * (1 - bl * 0.62) + self.PURP * bl * 0.62
            c *= (0.88 + self.n_fine * 0.26)[..., None]
            return c
        return fn

    def leg_col(self, dark=0.0):
        def fn(m):
            c = self.OLIVE + (self.YEL - self.OLIVE) * np.clip((self.n_mid - 0.5) * 2, 0, 1)[..., None] * 0.6
            bands = np.clip(np.sin(self.yy / (9 * self.s) + self.n_big * 8) * 2 - 1.1, 0, 1)[..., None]
            c = c * (1 - bands * 0.45) + self.OLIVE_D * bands * 0.45
            c = c * (0.85 + self.n_fine * 0.3)[..., None] * (1 - dark)
            return c
        return fn

    def flat(self, col):
        return lambda m: np.ones((self.H, self.W, 3), dtype=np.float32) * np.array(col) * (0.85 + self.n_fine * 0.3)[..., None]

    def blob(self, pts, col, a=1.0, blur=0.0, n=10):
        m = self.mask(pts, n=n)
        if blur:
            m = gblur(m, blur * self.s)
        m = m * a
        self.rgb = self.rgb * (1 - m[..., None]) + np.array(col, dtype=np.float32) * m[..., None]
        self.alpha = np.maximum(self.alpha, m * (1 if a >= 1 else 0))


def build(W=1920, H=1080, tx=(40.0, -150.0, 2.5)):
    A = Animal(W, H, tx)
    hand = lambda x, y, sp, ln: [[(x + sp * (k - 2) * 0.9 - 5, y - 8), (x + sp * (k - 2) * 1.4 - 4 + ln * 0.2, y + ln * 0.45), (x + sp * (k - 2) * 1.8 + ln * 0.3, y + ln * 0.8), (x + sp * (k - 2) * 1.8 + ln * 0.3 + 9, y + ln * 0.8), (x + sp * (k - 2) * 1.4 + 11, y + ln * 0.3), (x + sp * (k - 2) * 0.9 + 9, y - 8)] for k in range(5)]
    claw = lambda x, y, sp, ln: [[(x + sp * (k - 2) * 1.8 + ln * 0.3 + 4, y + ln * 0.8 - 4), (x + sp * (k - 2) * 1.8 + ln * 0.3 + 12, y + ln * 0.8 + 3), (x + sp * (k - 2) * 1.8 + ln * 0.3 + 7, y + ln * 0.8 + 2), (x + sp * (k - 2) * 1.8 + ln * 0.3 + 4, y + ln * 0.8 + 2)] for k in range(5)]
    HORN = (0.22, 0.19, 0.17)

    # --- patas del lado lejano (un poco más apagadas)
    A.part([(505, 266), (556, 268), (596, 302), (608, 342), (618, 362), (594, 370), (566, 362), (572, 340), (540, 316), (505, 300)], 34, A.leg_col(0.22), scale_f=0.5, fade=0.3)
    for t in hand(594, 362, 5.5, 12): A.part(t, 7, A.leg_col(0.22), scale_k=0.3, n=6)
    for c in claw(594, 362, 5.5, 12): A.blob(c, HORN, n=4)
    A.part([(262, 298), (300, 294), (312, 320), (300, 344), (270, 350), (252, 328)], 26, A.leg_col(0.28), scale_f=0.5, fade=0.4)
    # --- cola: gruesa en la base, apoyada, con una ondulación
    A.part([(18, 332), (48, 306), (98, 284), (168, 250), (250, 214), (290, 246), (284, 300), (224, 312), (164, 318), (108, 336), (56, 346), (24, 342)], 62, A.body_col(0.5, 0.5), scale_ang=0.15, wrinkle=0.4)
    # --- tronco en barril, lomo con curva suave
    A.part([(230, 214), (300, 198), (372, 193), (440, 199), (492, 213), (522, 246), (522, 300), (490, 340), (430, 358), (350, 362), (280, 350), (240, 324), (224, 274)], 150, A.body_col(0.5, 0.52), scale_ang=0.25, wrinkle=0.6)
    # --- cadera y pata trasera cercana (se funde con el tronco arriba)
    A.part([(204, 258), (262, 246), (302, 282), (298, 330), (264, 350), (248, 366), (216, 376), (186, 370), (198, 350), (208, 326), (196, 292)], 62, A.leg_col(), scale_f=0.48, wrinkle=0.4, fade=0.34)
    for t in hand(198, 364, 6.5, 14): A.part(t, 8, A.leg_col(), scale_k=0.3, n=6)
    for c in claw(198, 364, 6.5, 14): A.blob(c, HORN, n=4)
    # --- cuello: más angosto que la cabeza y que los hombros
    A.part([(470, 208), (510, 194), (548, 189), (568, 222), (558, 268), (516, 292), (476, 280)], 74, A.body_col(0.46, 0.45), scale_ang=0.6, wrinkle=0.9)
    # --- hombro, codo hacia afuera, antebrazo y mano ancha
    A.part([(364, 272), (426, 264), (460, 304), (452, 350), (432, 386), (440, 410), (424, 424), (392, 426), (362, 420), (372, 400), (378, 378), (352, 358), (338, 320)], 76, A.leg_col(), scale_f=0.46, wrinkle=0.5, fade=0.3)
    for t in hand(396, 418, 9.0, 18): A.part(t, 11, A.leg_col(), scale_k=0.3, n=6)
    for c in claw(396, 418, 9.0, 18): A.blob(c, HORN, n=4)
    # --- mandíbula inferior, cerrada
    A.part([(540, 236), (590, 243), (640, 241), (668, 236), (673, 246), (652, 257), (600, 262), (556, 258)], 30, A.flat((0.60, 0.55, 0.37)), scale_f=0.6, scale_k=0.6)
    # --- cráneo: ancho atrás, hocico que se afina y termina redondeado
    A.head = A.part([(533, 199), (556, 180), (600, 171), (640, 175), (668, 187), (681, 205), (679, 224), (665, 237), (620, 241), (578, 245), (548, 247), (531, 233)], 80, A.body_col(0.44, 0.36), scale_f=0.56, scale_ang=0.1, wrinkle=0.4)
    # punta del colmillo asomando bajo el labio
    A.blob([(634, 240), (637.4, 249.5), (640.4, 240)], (0.86, 0.83, 0.70), n=3)
    # línea de la boca: suave, apenas curva hacia arriba atrás
    A.blob([(550, 243.5), (585, 245.5), (630, 241.5), (670, 236.5), (671, 239.5), (630, 244.5), (585, 248.5), (550, 247)], (0.20, 0.15, 0.14), a=0.6, blur=0.9, n=8)
    # ojo con párpado: mirada tranquila
    A.blob([(588, 197), (601, 189), (614, 197), (601, 206)], (0.24, 0.17, 0.18), a=0.55, blur=2.6, n=8)
    A.blob([(594, 197), (601, 192), (608, 197), (601, 202)], (0.50, 0.40, 0.24), n=8)
    A.blob([(596.5, 197), (601, 193.4), (605.5, 197), (601, 200.6)], (0.05, 0.04, 0.05), n=8)
    A.blob([(598.6, 195.4), (600, 194.6), (601.2, 195.6), (599.8, 196.6)], (0.85, 0.9, 0.95), a=0.85, n=6)
    A.blob([(592, 194.5), (601, 189.5), (610, 194.5), (601, 192.2)], (0.50, 0.36, 0.37), a=0.9, blur=0.5, n=8)  # párpado
    A.blob([(584, 189), (601, 183), (616, 189), (601, 186.5)], (0.30, 0.20, 0.22), a=0.4, blur=1.8, n=8)       # ceja
    A.blob([(668, 197), (672.5, 195), (675, 199), (670.5, 201.5)], (0.12, 0.09, 0.09), a=0.85, blur=0.7, n=6)  # narina
    return A


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('dst')
    ap.add_argument('--w', type=int, default=1920); ap.add_argument('--h', type=int, default=1080)
    ap.add_argument('--ox', type=float, default=40); ap.add_argument('--oy', type=float, default=-150); ap.add_argument('--s', type=float, default=2.5)
    ap.add_argument('--mask', default=None)
    a = ap.parse_args()
    A = build(a.w, a.h, (a.ox, a.oy, a.s))
    rgba = np.dstack([np.clip(A.rgb, 0, 1), np.clip(A.alpha, 0, 1)])
    Image.fromarray((rgba * 255).astype(np.uint8), 'RGBA').save(a.dst)
    if a.mask:
        Image.fromarray((np.clip(A.head, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10)).save(a.mask)
    print('ok', a.dst)
