#!/usr/bin/env python3
"""Estilo 4 — óleo documental construido con partículas.

Nada se dibuja como forma geométrica: cada árbol, planta, roca, nube y el propio animal son
acumulaciones de manchas redondeadas, cada una con su tamaño, tono y posición. El cielo es un
degradé limpio (sin efecto de óleo); solo las nubes y la luna se pintan.

Uso: particulas.py salida.jpg [--detalle detalle.jpg]
"""
import math
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import animal as animal_mod

W, H, SS = 1920, 1080, 2


def hx(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


TEAL = [hx(c) for c in ('#05161c', '#0a3640', '#0f6e74', '#2bb8b2', '#8ee6d8', '#c8fbee')]
GRASS = [hx(c) for c in ('#08262a', '#0e4436', '#1d6a3c', '#4f9c38', '#a8cc48', '#dcee70')]
BUSH = [hx(c) for c in ('#051a1e', '#0b3832', '#17603e', '#3f9a4c', '#86c868')]
PURP = [hx(c) for c in ('#180c38', '#3e2684', '#7e5ac4', '#bca8e8', '#e8dcff')]
ROCK = [hx(c) for c in ('#1c1528', '#3c3252', '#6a5e88', '#9c90b8', '#c8c0dc')]
MOSS = [hx(c) for c in ('#0c3a2c', '#1f6e36', '#5eac38', '#b6d84c')]
BARK = [hx(c) for c in ('#04080f', '#0c1624', '#1e3044', '#3c5670', '#6c88a0')]
BLUE = [hx(c) for c in ('#0c0e48', '#2428a0', '#5058d8', '#98a0f8', '#dce0ff')]
HAZE = hx('#aebcc0')


class Lienzo:
    def __init__(self, fondo):
        self.im = fondo.resize((W * SS, H * SS), Image.BICUBIC).convert('RGB')
        self.d = ImageDraw.Draw(self.im, 'RGBA')
        self.rnd = random.Random(11)
        self.n = 0

    def mancha(self, x, y, r, col, a=1.0, jit=10):
        """una mancha redondeada, orgánica, con su propio tono; si es grande, lleva una luz arriba"""
        rnd = self.rnd
        if r < 0.6:
            return
        x *= SS; y *= SS; r *= SS
        c = tuple(int(max(0, min(255, col[i] + (rnd.random() - 0.5) * 2 * jit))) for i in range(3))
        k = 9 if r < 9 * SS else 15
        rot = rnd.random() * 6.28; asp = 0.72 + rnd.random() * 0.28
        cr, sr = math.cos(rot), math.sin(rot)
        pts = []
        for i in range(k):
            an = i * 6.2832 / k + (rnd.random() - 0.5) * (0.4 if k == 9 else 0.2)
            rr = r * (0.84 + rnd.random() * 0.22)
            px, py = math.cos(an) * rr, math.sin(an) * rr * asp
            pts.append((x + px * cr - py * sr, y + px * sr + py * cr))
        self.d.polygon(pts, fill=c + (int(255 * a),))
        if r > 7 * SS and a > 0.6:
            q = r * 0.5
            hl = tuple(min(255, int(v * 1.14 + 8)) for v in c)
            self.d.ellipse((x - r * 0.3 - q, y - r * 0.34 - q * 0.8, x - r * 0.3 + q, y - r * 0.34 + q * 0.8), fill=hl + (int(150 * a),))
        self.n += 1

    def velo(self, y0, y1, col, a0, a1):
        """bruma entre planos: separa lo lejano de lo cercano"""
        ov = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
        arr = np.zeros((H * SS, W * SS, 4), dtype=np.uint8)
        ys = np.arange(H * SS) / SS
        t = np.clip((ys - y0) / max(1, (y1 - y0)), 0, 1)
        al = (a0 + (a1 - a0) * t) * ((ys >= y0) & (ys <= y1))
        arr[..., 0], arr[..., 1], arr[..., 2] = col
        arr[..., 3] = (al * 255).astype(np.uint8)[:, None]
        self.im.paste(Image.fromarray(arr, 'RGBA'), (0, 0), Image.fromarray(arr[..., 3]))
        self.d = ImageDraw.Draw(self.im, 'RGBA')

    def final(self):
        return self.im.resize((W, H), Image.LANCZOS)


def tono(pal, t, rnd, sp=0.16):
    t = max(0.0, min(0.999, t + (rnd.random() - 0.5) * 2 * sp))
    f = t * (len(pal) - 1); i = int(f)
    return mix(pal[i], pal[min(len(pal) - 1, i + 1)], f - i)


# ---------------- cielo: degradé limpio, sin óleo ----------------
def cielo():
    ys = np.linspace(0, 1, H)[:, None]
    stops = [(0.0, hx('#141e34')), (0.3, hx('#2a3f5c')), (0.5, hx('#6f8aa0')), (0.57, hx('#b9c8c4')), (1.0, hx('#b9c8c4'))]
    arr = np.zeros((H, W, 3), dtype=np.float32)
    for (t0, c0), (t1, c1) in zip(stops[:-1], stops[1:]):
        m = ((ys >= t0) & (ys <= t1)).astype(np.float32)
        k = np.clip((ys - t0) / (t1 - t0), 0, 1)
        arr = arr * (1 - m[..., None]) + (np.array(c0) + (np.array(c1) - np.array(c0)) * k[..., None]) * m[..., None]
    arr = np.broadcast_to(arr, (H, W, 3)).copy()
    yy, xx = np.mgrid[0:H, 0:W]
    glow = np.exp(-(((xx - 940) / 420.0) ** 2 + ((yy - 300) / 420.0) ** 2))
    arr = arr + glow[..., None] * np.array([52, 60, 62])
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def luna(L, cx=940, cy=300, R=186):
    rnd = L.rnd
    mares = [(cx - 60, cy - 50, 70), (cx + 50, cy - 70, 44), (cx + 80, cy + 30, 66), (cx - 50, cy + 60, 50), (cx - 100, cy, 40)]
    for i in range(12000):
        a = rnd.random() * 6.2832; d = math.sqrt(rnd.random()) * (R - 3)
        x, y = cx + math.cos(a) * d, cy + math.sin(a) * d
        nx, ny = (x - cx) / R, (y - cy) / R
        lit = 0.62 - nx * 0.42 - ny * 0.34 - (d / R) ** 3 * 0.25
        for (mx, my, mr) in mares:
            lit -= 0.26 * math.exp(-((x - mx) ** 2 + (y - my) ** 2) / (mr * mr * 0.5))
        col = mix(hx('#39485e'), hx('#f2f0e4'), max(0, min(1, lit)))
        L.mancha(x, y, 2.5 + rnd.random() * 4.5, col, 0.95, 6)
    for i in range(26):  # cráteres: una mancha oscura y una clara
        a = rnd.random() * 6.2832; d = math.sqrt(rnd.random()) * R * 0.9
        x, y = cx + math.cos(a) * d, cy + math.sin(a) * d; q = 3 + rnd.random() * 7
        L.mancha(x + q * 0.25, y + q * 0.25, q, hx('#667488'), 0.6, 5); L.mancha(x - q * 0.2, y - q * 0.2, q * 0.55, hx('#e6e6da'), 0.6, 5)


def nubes(L):
    rnd = L.rnd
    for (cx, cy, w) in [(250, 250, 300), (640, 120, 260), (1380, 170, 320), (1700, 330, 260), (380, 430, 340), (1250, 440, 260), (90, 90, 220), (1620, 60, 240)]:
        if abs(cx - 940) < 330 and abs(cy - 300) < 230:
            continue
        h = w * 0.2
        for capa, (col, n, r0, r1, dy, a) in enumerate([(hx('#2b3a52'), 260, 9, 20, 0.35, 0.8), (hx('#5d7288'), 320, 7, 16, 0.0, 0.85), (hx('#a9b8c2'), 280, 5, 12, -0.3, 0.9), (hx('#e8ece6'), 170, 4, 9, -0.6, 0.92)]):
            for i in range(n):
                u = rnd.gauss(0, 0.42); v = rnd.gauss(0, 0.5)
                x = cx + u * w + (capa - 1.5) * -14; y = cy + dy * h + v * h * (1 - abs(u) * 0.6)
                L.mancha(x, y, r0 + rnd.random() * (r1 - r0), col, a, 9)


# ---------------- planos lejanos ----------------
def sierra(L, seed, base, amp, col_top, col_bot, r0, r1, n):
    rs = random.Random(seed); rnd = L.rnd
    pts = [rs.random() for _ in range(24)]
    def hgt(x):
        f = x / W * 14; i = int(f); t = f - i; t = t * t * (3 - 2 * t)
        return base - amp * (0.2 + 0.8 * (pts[i % 24] * (1 - t) + pts[(i + 1) % 24] * t))
    for i in range(n):
        x = rnd.random() * (W + 80) - 40; top = hgt(x)
        y = top + (rnd.random() ** 1.3) * (base + 40 - top)
        t = (y - top) / max(1, base + 40 - top)
        col = mix(col_top, col_bot, t)
        col = mix(col, (255, 255, 255), max(0, 0.12 - t * 0.2) if (x * 0.01 + y * 0.02) % 1 < 0.5 else 0)
        L.mancha(x, y, r0 + rnd.random() * (r1 - r0), col, 0.95, 6)


def agua(L, y0, y1, n, r):
    rnd = L.rnd
    for i in range(n):
        x = rnd.random() * W; y = y0 + rnd.random() * (y1 - y0)
        L.mancha(x, y, r * (0.6 + rnd.random()), tono([hx('#2c6a80'), hx('#5aa8ac'), hx('#b4d8d4'), hx('#eef8f2')], rnd.random() ** 1.6, rnd, 0.1), 0.9, 6)


def monte(L, cx, cy, rx, ry, pal, n, r0, r1, haze=0.0):
    """mata o loma de vegetación: nube de hojas con luz arriba a la izquierda"""
    rnd = L.rnd
    ps = []
    for i in range(n):
        a = rnd.random() * 6.2832; d = rnd.random() ** 0.6
        u, v = math.cos(a) * d, math.sin(a) * d
        if v > 0.25 and rnd.random() < 0.6:
            continue
        ps.append((v, u))
    ps.sort()
    for v, u in ps:
        x, y = cx + u * rx * (1 + (rnd.random() - 0.5) * 0.2), cy + v * ry
        lit = 0.5 - u * 0.3 - v * 0.42
        col = tono(pal, lit, rnd, 0.2)
        if haze:
            col = mix(col, HAZE, haze)
        L.mancha(x, y, r0 + rnd.random() * (r1 - r0), col, 0.96, 9)


def suelo(L, n, y0=600):
    rnd = L.rnd
    ps = []
    for i in range(n):
        t = rnd.random() ** 0.8
        ps.append((y0 + t ** 1.35 * (H - y0 + 30), rnd.random() * (W + 60) - 30, t))
    ps.sort()
    for y, x, t in ps:
        lit = 0.74 - math.hypot((x - 880) / 900.0, (y - 800) / 300.0) * 0.6
        lit -= 0.25 * max(0, (y - 940) / 140.0)
        if x > 1500:
            lit -= 0.22 * min(1, (x - 1500) / 300.0)
        col = tono(GRASS, lit, rnd, 0.13)
        col = mix(col, HAZE, max(0, 0.35 - t * 1.4))
        L.mancha(x, y, 2.2 + t * 9 + rnd.random() * 2.5, col, 0.97, 8)


def rio(L, pts, n):
    rnd = L.rnd
    for i in range(n):
        t = rnd.random(); f = t * (len(pts) - 1); k = int(f); u = f - k
        a, b = pts[k], pts[min(len(pts) - 1, k + 1)]
        x = a[0] + (b[0] - a[0]) * u; y = a[1] + (b[1] - a[1]) * u; w = a[2] + (b[2] - a[2]) * u
        v = rnd.gauss(0, 0.36)
        if abs(v) > 0.9:
            continue
        col = tono([hx('#0e4c74'), hx('#1d86a0'), hx('#44c0c0'), hx('#a8ecdc'), hx('#effff8')], 0.55 - abs(v) * 0.5 + (rnd.random() ** 3) * 0.5, rnd, 0.1)
        L.mancha(x + v * w * 0.2, y + v * w * 0.42, 2.5 + w * 0.035 * (0.6 + rnd.random()), col, 0.95, 6)


# ---------------- roca: partículas que siguen un volumen ----------------
def roca(L, poly, pal, n, r0, r1, musgo=0.2, seed=1):
    rnd = L.rnd
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon(poly, fill=255)
    ma = np.asarray(m, dtype=np.float32) / 255
    h = (np.asarray(m.filter(ImageFilter.GaussianBlur(26)), dtype=np.float32) + np.asarray(m.filter(ImageFilter.GaussianBlur(70)), dtype=np.float32)) * ma
    rs = np.random.RandomState(seed)
    h = h + np.asarray(Image.fromarray((rs.rand(H // 34 + 2, W // 34 + 2) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), dtype=np.float32) * 0.5
    gy, gx = np.gradient(h)
    xs, ys = np.nonzero(ma.T > 0.5)
    y_top = {}
    for x in range(0, W):
        col = np.nonzero(ma[:, x] > 0.5)[0]
        if len(col):
            y_top[x] = col[0]
    idx = [rnd.randrange(len(xs)) for _ in range(n)]
    ps = sorted((ys[i], xs[i]) for i in idx)
    for y, x in ps:
        lit = 0.46 - gx[y, x] * 0.05 - gy[y, x] * 0.05
        col = tono(pal, lit, rnd, 0.14)
        d_top = y - y_top.get(x, y)
        if musgo and d_top < (40 + 80 * rnd.random()) * musgo * 5 and rnd.random() < 0.8:
            col = tono(MOSS, 0.75 - d_top / 220.0 - (x % 200) / 600.0, rnd, 0.2)
        L.mancha(x, y, r0 + rnd.random() * (r1 - r0), col, 0.97, 8)


# ---------------- árbol: esqueleto que crece + partículas ----------------
def rama(L, pts, w0, w1, pal=BARK):
    rnd = L.rnd
    segs = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        steps = max(2, int(ln / 3))
        for k in range(steps):
            t = (i + k / steps) / (len(pts) - 1)
            x = a[0] + (b[0] - a[0]) * k / steps; y = a[1] + (b[1] - a[1]) * k / steps
            w = w0 + (w1 - w0) * t
            nx, ny = -(b[1] - a[1]) / ln, (b[0] - a[0]) / ln
            for _ in range(max(1, int(w / 5))):
                o = rnd.uniform(-1, 1)
                side = o * (1 if nx * -0.6 + ny * -0.8 > 0 else -1)
                lit = 0.34 + side * 0.34
                L.mancha(x + nx * o * w * 0.5 + rnd.uniform(-1.5, 1.5), y + ny * o * w * 0.5 + rnd.uniform(-1.5, 1.5), max(1.6, w * 0.24 * (0.7 + rnd.random() * 0.6)), tono(pal, lit, rnd, 0.14), 0.98, 7)
            segs.append((x, y, t))
    return segs


def follaje(L, x, y, sx, sy, n_hojas, n_hilos, pal=TEAL, r=(5, 10), largo=(8, 26)):
    """racimo de hojas colgantes: cada hoja es una mancha, los hilos son cadenas de manchas"""
    rnd = L.rnd
    for i in range(n_hojas):
        u, v = rnd.gauss(0, 1), rnd.gauss(0, 1)
        px, py = x + u * sx, y + v * sy + abs(u) * sy * 0.5
        L.mancha(px, py, rnd.uniform(*r), tono(pal, 0.5 - u * 0.2 - v * 0.26, rnd, 0.2), 0.96, 9)
    for i in range(n_hilos):
        px = x + rnd.gauss(0, 1) * sx; py = y + rnd.uniform(-0.3, 0.7) * sy
        k = rnd.randint(*largo); dx = rnd.uniform(-0.9, 0.9); lit = rnd.uniform(0.3, 0.85)
        for j in range(k):
            px += dx + rnd.uniform(-1.6, 1.6); py += rnd.uniform(6, 9.5)
            t = j / k
            L.mancha(px, py, max(2.2, (r[0] + (r[1] - r[0]) * rnd.random()) * (1 - t * 0.5)), tono(pal, lit - t * 0.25 + (0.25 if j % 5 == 0 else 0), rnd, 0.16), 0.95, 9)


def arbol_colgante(L):
    rnd = L.rnd
    ramas = [
        ([(1930, 345), (1880, 250), (1790, 185), (1670, 135), (1540, 105), (1410, 112), (1310, 150)], 54, 7),
        ([(1870, 225), (1920, 120), (1985, 45)], 24, 7),
        ([(1810, 195), (1755, 100), (1690, 30)], 20, 5),
        ([(1560, 108), (1500, 190), (1425, 232)], 14, 4),
        ([(1945, 335), (1860, 392), (1775, 412)], 30, 8),
        ([(1680, 138), (1640, 70), (1570, 20)], 14, 4),
        ([(1420, 112), (1360, 70), (1290, 60)], 9, 3),
    ]
    puntas = []
    for pts, w0, w1 in ramas:
        segs = rama(L, pts, w0, w1)
        puntas += [(x, y) for (x, y, t) in segs if t > 0.3 and rnd.random() < 0.06]
        puntas.append(pts[-1])
        # ramitas que salen hacia afuera
        for (x, y, t) in segs[::40]:
            if t > 0.25:
                a = rnd.uniform(-2.6, -0.5); ln = rnd.uniform(40, 90)
                e = (x + math.cos(a) * ln, y + math.sin(a) * ln * 0.7)
                rama(L, [(x, y), ((x + e[0]) / 2 + rnd.uniform(-10, 10), (y + e[1]) / 2 - 8), e], 5, 2)
                puntas.append(e)
    puntas.sort(key=lambda p: p[1])
    for (x, y) in puntas:
        follaje(L, x, y + 10, rnd.uniform(36, 70), rnd.uniform(16, 28), rnd.randint(60, 110), rnd.randint(7, 14))
    # ramas otra vez por delante, finas, para que se lean entre las hojas
    for pts, w0, w1 in ramas[:3]:
        rama(L, pts, w0 * 0.35, w1 * 0.4)


def arbolito(L, x, y, h, pal, haze=0.0):
    rnd = L.rnd
    top = (x + rnd.uniform(-0.15, 0.15) * h, y - h)
    rama(L, [(x, y), ((x + top[0]) / 2 + rnd.uniform(-8, 8), y - h * 0.5), top], h * 0.07, h * 0.025, [mix(c, HAZE, haze) for c in BARK])
    for i in range(3):
        cx, cy = top[0] + rnd.uniform(-0.25, 0.25) * h, top[1] + rnd.uniform(-0.05, 0.25) * h
        monte(L, cx, cy, h * 0.3, h * 0.2, pal, int(120 + h * 0.6), h * 0.03, h * 0.06, haze)


# ---------------- plantas ----------------
def helecho(L, x, y, s, pal, n=9, glow=None):
    rnd = L.rnd
    fr = sorted([(-math.pi * (0.1 + 0.8 * i / (n - 1)) + rnd.uniform(-0.1, 0.1), s * rnd.uniform(0.7, 1.2)) for i in range(n)], key=lambda f: -abs(math.cos(f[0])))
    for a0, ln in fr:
        side = 1 if math.cos(a0) > 0 else -1
        px, py, a = x, y, a0
        lit = rnd.uniform(0.35, 0.8)
        steps = max(8, int(ln / 7))
        for k in range(steps):
            t = k / steps
            a += side * 0.028 * (1 + t * 1.4)
            px += math.cos(a) * ln / steps; py += math.sin(a) * ln / steps
            pl = ln * 0.24 * math.sin(math.pi * min(1, t * 1.1 + 0.1))
            L.mancha(px, py, max(1.5, s * 0.02 * (1 - t)), tono(pal, 0.15, rnd, 0.08), 0.95, 5)
            for sg in (1, -1):
                for q in (0.45, 0.9):
                    L.mancha(px + math.cos(a + 1.3 * sg) * pl * q, py + math.sin(a + 1.3 * sg) * pl * q, max(1.6, pl * 0.3 * (1.15 - q * 0.5)), tono(pal, lit + (0.12 if sg < 0 else -0.08) - q * 0.06, rnd, 0.14), 0.96, 8)


def roseta(L, x, y, s, pal, n=11):
    rnd = L.rnd
    fr = sorted([(-math.pi * (0.08 + 0.84 * i / (n - 1)) + rnd.uniform(-0.1, 0.1), s * rnd.uniform(0.6, 1.1)) for i in range(n)], key=lambda f: -abs(math.cos(f[0])))
    for a0, ln in fr:
        side = 1 if math.cos(a0) > 0 else -1
        px, py, a = x, y, a0
        lit = rnd.uniform(0.3, 0.75)
        steps = max(6, int(ln / 5))
        for k in range(steps):
            t = k / steps
            a += side * 0.05 * (1 + t)
            px += math.cos(a) * ln / steps; py += math.sin(a) * ln / steps
            w = s * 0.07 * math.sin(math.pi * min(1, t * 0.9 + 0.12)) + 1.5
            L.mancha(px, py, w, tono(pal, lit + t * 0.25, rnd, 0.14), 0.96, 8)
            if k % 2 == 0:
                L.mancha(px - 1.5, py - w * 0.4, w * 0.45, tono(pal, min(0.95, lit + 0.3 + t * 0.2), rnd, 0.1), 0.9, 6)


def cola_caballo(L, x, y, h, pal=TEAL):
    rnd = L.rnd
    lean = rnd.uniform(-0.12, 0.12) * h
    steps = int(h / 4)
    for k in range(steps):
        t = k / steps
        px, py = x + lean * t * t, y - h * t
        L.mancha(px, py, max(1.6, h * 0.016 * (1 - t * 0.6)), tono(pal, 0.35 + (0.2 if k % 6 < 3 else 0), rnd, 0.1), 0.97, 6)
        if k % 6 == 0 and k > 0:
            l = h * 0.13 * (1 - t * 0.5)
            for j in range(9):
                a = -math.pi * (0.05 + 0.9 * j / 8)
                for q in (0.35, 0.7, 1.0):
                    L.mancha(px + math.cos(a) * l * q, py + math.sin(a) * l * q * 0.55 - l * 0.12 * q, max(1.3, 2.6 * (1.2 - q)), tono(pal, 0.5 + q * 0.2, rnd, 0.14), 0.95, 7)


def hongo(L, x, y, s, pal=BLUE):
    rnd = L.rnd
    lean = rnd.uniform(-0.25, 0.25) * s; h = s * rnd.uniform(0.85, 1.25); w = s * rnd.uniform(0.75, 1.05)
    tx, ty = x + lean, y - h
    for k in range(int(h / 3)):
        t = k / (h / 3)
        px = x + lean * t; py = y - h * t
        for o in (-0.5, 0, 0.5):
            L.mancha(px + o * s * 0.12, py, max(1.5, s * 0.055), mix(hx('#4a3c88'), hx('#e6dcff'), 0.55 - o * 0.7), 0.97, 6)
    n = int(60 + s * 2.2)
    ps = []
    for i in range(n):
        a = rnd.uniform(0, math.pi); d = rnd.random() ** 0.55
        ps.append((-math.sin(a) * d, -math.cos(a) * d))
    for v, u in sorted(ps):
        px, py = tx + u * w, ty + v * w * 0.62 + w * 0.06
        lit = 0.42 - u * 0.36 - v * 0.5 - 0.3
        L.mancha(px, py, max(1.8, s * 0.075 * (0.7 + rnd.random() * 0.6)), tono(pal, lit + 0.3, rnd, 0.12), 0.97, 7)
    for i in range(int(6 + s * 0.08)):
        a = rnd.uniform(0.2, math.pi - 0.2); d = rnd.random() * 0.75
        L.mancha(tx - math.cos(a) * w * d, ty - math.sin(a) * w * 0.55 * d, max(1.5, s * 0.04), pal[-1], 0.9, 5)


def brotes(L, x, y, h, n, pal):
    rnd = L.rnd
    for i in range(n):
        px = x + rnd.gauss(0, 1) * h * 0.5; hh = h * rnd.uniform(0.4, 1.0); lean = rnd.uniform(-0.3, 0.3) * hh
        steps = max(3, int(hh / 4))
        for k in range(steps):
            t = k / steps
            L.mancha(px + lean * t, y - hh * t, max(1.4, 3.2 * (1 - t * 0.6)), tono(pal, 0.4 + t * 0.5, rnd, 0.12), 0.95, 7)


def derrame(L, x, y, radio, col, n=260):
    """el color de una planta especial se difunde: manchas cada vez más chicas y transparentes"""
    rnd = L.rnd
    for i in range(n):
        a = rnd.random() * 6.2832; d = abs(rnd.gauss(0, 0.45))
        if d > 1.3:
            continue
        px, py = x + math.cos(a) * d * radio, y + math.sin(a) * d * radio * 0.55
        k = max(0, 1 - d / 1.3)
        L.mancha(px, py, 2 + k * 7 * rnd.random() + 1.5, col, 0.08 + 0.3 * k * k, 14)


# ---------------- animal: la anatomía aprobada, hecha de manchas ----------------
def animal(L, s, ox, oy, n=26000, r=(3.2, 8.5)):
    rnd = L.rnd
    A = animal_mod.build(W, H, (ox, oy, s))
    rgb = np.clip(A.rgb, 0, 1) * np.array([0.93, 0.98, 1.05]) * 255
    al = A.alpha; head = A.head
    xs, ys = np.nonzero(al.T > 0.55)
    # sombra en el suelo
    bx0, bx1, by1 = xs.min(), xs.max(), ys.max()
    cxs, rxs = (bx0 + bx1) / 2 + 20, (bx1 - bx0) * 0.42
    for i in range(1700):
        a = rnd.random() * 6.2832; d = abs(rnd.gauss(0, 0.5))
        if d > 1.15:
            continue
        L.mancha(cxs + math.cos(a) * d * rxs, by1 - 30 + math.sin(a) * d * 34, rnd.uniform(5, 11), hx('#06161c'), 0.3 * (1 - d / 1.2), 4)
    for capa, (kn, k0, k1) in enumerate([(0.4, 1.5, 1.9), (0.6, 0.9, 1.15)]):
        idx = [rnd.randrange(len(xs)) for _ in range(int(n * kn))]
        ps = sorted((ys[i], xs[i]) for i in idx)
        for y, x in ps:
            f = 0.48 if head[y, x] > 0.5 else 1.0
            if capa == 0 and f < 1:
                f = 0.7
            c = rgb[y, x]
            L.mancha(x + rnd.uniform(-1, 1), y + rnd.uniform(-1, 1), rnd.uniform(r[0], r[1]) * f * rnd.uniform(k0, k1) * (s / 1.22) ** 0.7, tuple(c), 0.97, 9)
    return A


# ---------------- escena ----------------
def escena(an_s=1.22, an_ox=560, an_oy=338):
    L = Lienzo(cielo())
    rnd = L.rnd
    luna(L); nubes(L)
    sierra(L, 3, 560, 190, hx('#566684'), hx('#a4b2bc'), 2.5, 5, 9000)
    sierra(L, 5, 572, 130, hx('#3a4a66'), hx('#8898a8'), 2.5, 5.5, 8000)
    agua(L, 548, 600, 2600, 3.2)
    sierra(L, 8, 590, 70, hx('#243248'), hx('#55697c'), 2.5, 5, 5000)
    L.velo(470, 610, HAZE, 0.0, 0.42)
    # plano medio: lomas y matas, arbolitos
    for (cx, cy, rx, ry) in [(340, 640, 150, 60), (710, 636, 170, 76), (1110, 622, 270, 124), (1520, 640, 200, 92), (60, 650, 120, 60)]:
        monte(L, cx, cy, rx, ry, BUSH, int(rx * ry / 9), 3, 6.5, 0.22)
    for (x, y, h, pal) in [(150, 668, 150, PURP), (250, 676, 110, PURP), (1840 - 540 + 300, 670, 130, PURP), (560, 672, 120, TEAL), (880, 668, 100, BUSH), (1380, 670, 120, TEAL)]:
        arbolito(L, x, y, h, pal, 0.2)
    L.velo(560, 700, HAZE, 0.2, 0.0)
    suelo(L, 52000)
    rio(L, [(1040, 668, 60), (760, 720, 150), (360, 800, 260), (-60, 900, 400)], 9000)
    # rocas
    roca(L, [(-40, 705), (-40, 470), (60, 398), (112, 440), (150, 600), (186, 705)], ROCK, 5200, 3.5, 8, 0.2, 2)
    roca(L, [(1720, 940), (1692, 760), (1752, 600), (1712, 470), (1792, 332), (1930, 262), (2000, 250), (2000, 1010)], ROCK, 15000, 4, 10, 0.22, 4)
    for i in range(140):  # enredaderas colgando del peñasco
        px = rnd.uniform(1730, 1920); py = rnd.uniform(300, 520); k = rnd.randint(8, 30)
        for j in range(k):
            px += rnd.uniform(-1.5, 1.5); py += rnd.uniform(5, 8)
            L.mancha(px, py, rnd.uniform(2.2, 4.5), tono(MOSS, 0.35 + rnd.random() * 0.5, rnd), 0.94, 8)
    arbol_colgante(L)
    # fondo cercano: franja de plantas detrás del recorrido
    for i in range(46):
        x = i / 46 * W + rnd.uniform(-20, 20); y = 704 + rnd.uniform(0, 34); k = rnd.random(); s2 = rnd.uniform(50, 100)
        if k < 0.3: helecho(L, x, y, s2, TEAL if i % 2 else BUSH, 7)
        elif k < 0.5: roseta(L, x, y, s2 * 0.8, PURP if i % 3 == 0 else TEAL)
        elif k < 0.72: cola_caballo(L, x, y, s2 * 1.8)
        else: monte(L, x, y - s2 * 0.3, s2 * 0.9, s2 * 0.5, BUSH, 260, 3, 6)
    monte(L, 220, 770, 250, 120, BUSH, 3600, 4.5, 10)
    monte(L, 1480, 800, 200, 100, BUSH, 2600, 4.5, 10)
    # plantas especiales: su color se derrama
    derrame(L, 420, 838, 190, hx('#3fe0d0'), 380); helecho(L, 420, 860, 150, [hx('#0a3640'), hx('#149a9c'), hx('#3fe6de'), hx('#b4fff2'), hx('#eafffa')], 10)
    derrame(L, 1585, 880, 170, hx('#b070ff'), 340); roseta(L, 1585, 905, 130, [hx('#2a1260'), hx('#7040d0'), hx('#b890ff'), hx('#ecd8ff')])
    # costados
    for (x, y, s2, pal) in [(110, 830, 150, BUSH), (640, 940, 130, TEAL), (1520, 940, 150, BUSH), (1660, 860, 120, TEAL)]:
        helecho(L, x, y, s2, pal)
    for (x, y, h) in [(60, 760, 200), (110, 772, 150), (1440, 742, 190), (1490, 752, 130)]:
        cola_caballo(L, x, y, h)
    for (x, y, s2) in [(300, 900, 46), (340, 912, 30), (1140, 742, 24), (1580, 960, 44), (1360, 900, 30)]:
        hongo(L, x, y, s2)
    # animal
    A = animal(L, an_s, an_ox, an_oy)
    # brotes y musgo por delante de las patas
    for (x, y, h, n) in [(820, 876, 30, 26), (1045, 880, 36, 30), (1290, 806, 22, 14), (930, 884, 20, 14)]:
        brotes(L, x, y, h, n, GRASS)
    for (x, y, h) in [(700, 950, 60), (1215, 930, 56)]:
        brotes(L, x, y, h, 26, [hx('#2a8a7a'), hx('#6fd8c0'), hx('#d8fff0')])
    derrame(L, 1050, 962, 120, hx('#e060c8'), 240)
    for (x, y, s2) in [(1030, 968, 40), (1075, 978, 28), (1000, 982, 22)]:
        hongo(L, x, y, s2, [hx('#4a1070'), hx('#a040c8'), hx('#e88ae8'), hx('#ffd8fa')])
    # primer plano: tronco caído, hongos grandes, plantas que tapan parte del cuadro
    rama(L, [(-80, 1050), (130, 1012), (330, 978), (450, 968), (560, 1010)], 150, 60, [hx('#03050b'), hx('#0b1220'), hx('#1c2a40'), hx('#35425e')])
    for i in range(700):
        L.mancha(rnd.uniform(-20, 520), rnd.uniform(930, 1010), rnd.uniform(3, 7), tono(MOSS, rnd.random() * 0.9, rnd), 0.95, 9)
    for (x, y, s2) in [(-10, 1090, 150), (140, 1030, 205), (360, 1000, 100), (440, 1000, 62)]:
        hongo(L, x, y, s2)
    for i in range(24):
        x = 470 + rnd.random() * 1500; y = 1045 + rnd.random() * 100; s2 = rnd.uniform(140, 300)
        dk = lambda pal: [mix(c, (4, 10, 16), 0.35) for c in pal]
        (helecho if rnd.random() < 0.55 else roseta)(L, x, y, s2 if rnd.random() < 0.55 else s2 * 0.75, dk(TEAL if i % 3 else PURP if i % 3 == 1 else BUSH))
    helecho(L, 1820, 1010, 330, [mix(c, (4, 10, 16), 0.25) for c in TEAL], 12)
    return L, A


def acabado(im):
    """ajuste final: contraste, saturación contenida, viñeta suave; el cielo no recibe textura"""
    a = np.asarray(im, dtype=np.float32) / 255
    g = a.mean(axis=2, keepdims=True)
    a = g + (a - g) * 0.94
    a = (a - 0.5) * 1.06 + 0.5
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    a = a * (1 - 0.26 * np.clip(d - 0.6, 0, 1)[..., None] ** 1.5 * 1.6)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


if __name__ == '__main__':
    dst = sys.argv[1] if len(sys.argv) > 1 else 'estilo/E4_oleo_particulas.jpg'
    L, A = escena()
    big = L.im
    out = acabado(L.final())
    out.save(dst, quality=94)
    print('manchas:', L.n)
    if '--detalle' in sys.argv:
        d = sys.argv[sys.argv.index('--detalle') + 1]
        # tres recortes al doble de tamaño: árbol, planta especial, animal
        cr = [(1300, 40, 1780, 310), (1420, 760, 1900, 1030), (1150, 560, 1470, 740)]
        tiles = [big.crop((x0 * SS, y0 * SS, x1 * SS, y1 * SS)) for (x0, y0, x1, y1) in cr]
        tiles[2] = tiles[2].resize((960, 540), Image.LANCZOS)
        sheet = Image.new('RGB', (1920, 1080), (10, 14, 20))
        sheet.paste(tiles[0], (0, 0)); sheet.paste(tiles[1], (960, 0)); sheet.paste(tiles[2], (480, 540))
        sheet.save(d, quality=94)
