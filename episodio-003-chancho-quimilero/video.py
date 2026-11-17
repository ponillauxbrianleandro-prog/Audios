#!/usr/bin/env python3
"""Render del video del episodio 003 (1080x1920 se logra reescalando; se dibuja a 720x1280, 30 fps).

Requiere generar_audio.py y musica.py ya corridos. Uso:
  python3 video.py                 # video completo -> episodio-003.mp4
  python3 video.py --frames 3 12 40  # guarda fotogramas sueltos (segundos) en preview/
"""
import json
import math
import re
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageOps

import sprites as SPR
from comun import AQUI, TEMPOS, cargar

W, H, FPS = 720, 1280, 30
HORIZONTE = 770
SP = None
D = None
FONDOS = {}
CAPTIONS = []
CACHE_TXT = {}

PALETAS = {  # cielo arriba, cielo abajo, colinas (lejos→cerca), suelo arriba, suelo abajo
    1: ((255, 205, 215), (255, 238, 210), [(255, 214, 224), (250, 200, 214), (240, 190, 210)], (255, 226, 200), (240, 190, 175)),
    2: ((190, 230, 255), (255, 244, 220), [(200, 238, 220), (170, 225, 200), (150, 210, 185)], (190, 225, 160), (150, 200, 130)),
    3: ((255, 214, 170), (255, 240, 200), [(245, 215, 190), (232, 200, 170), (215, 185, 150)], (242, 218, 170), (222, 190, 140)),
    4: ((255, 226, 180), (255, 244, 214), [(240, 220, 185), (228, 205, 165), (205, 190, 140)], (245, 222, 175), (225, 195, 145)),
    5: ((196, 190, 224), (226, 220, 238), [(205, 200, 226), (186, 180, 212), (166, 160, 196)], (206, 200, 222), (172, 166, 198)),
    6: ((200, 236, 205), (240, 250, 215), [(205, 235, 200), (185, 222, 185), (160, 205, 170)], (214, 232, 170), (180, 210, 140)),
    7: ((255, 196, 160), (255, 232, 190), [(255, 214, 180), (245, 195, 160), (230, 175, 150)], (250, 215, 165), (225, 180, 135)),
    8: ((150, 170, 225), (255, 205, 200), [(190, 180, 225), (165, 160, 210), (140, 140, 190)], (200, 190, 220), (150, 150, 190)),
    9: ((255, 175, 190), (255, 232, 160), [(255, 205, 185), (250, 185, 175), (235, 165, 170)], (255, 218, 170), (240, 185, 150)),
    10: ((255, 200, 120), (255, 238, 190), [(255, 214, 160), (248, 195, 150), (235, 175, 145)], (255, 222, 160), (240, 190, 130)),
}


def ease_back(u):
    u = min(1.0, max(0.0, u))
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (u - 1) ** 3 + c1 * (u - 1) ** 2


def ease_out(u):
    u = min(1.0, max(0.0, u))
    return 1 - (1 - u) ** 3


def pop(t, t0, dur=0.38):
    return 0.0 if t < t0 else ease_back((t - t0) / dur)


def seg(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def lerp(a, b, u):
    return a + (b - a) * u


# ---------- fondos ----------
def degradado(c0, c1, y0, y1):
    ys = np.linspace(0, 1, y1 - y0)[:, None, None]
    arr = (np.array(c0)[None, None, :] * (1 - ys) + np.array(c1)[None, None, :] * ys)
    arr = np.repeat(arr, W, axis=1)
    return Image.fromarray(arr.astype("uint8"), "RGB")


def colinas(col, base, amp, seed, arbustos=None, tw=1440):
    rnd = np.random.default_rng(seed)
    img = Image.new("RGBA", (tw, 440), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fases = rnd.random(3)
    xs = np.arange(0, tw, 6)
    ys = [base - amp * (0.6 * math.sin(2 * math.pi * (2 * x / tw + fases[0])) + 0.3 * math.sin(2 * math.pi * (5 * x / tw + fases[1]))
                         + 0.2 * math.sin(2 * math.pi * (9 * x / tw + fases[2]))) for x in xs]
    d.polygon([(0, 440)] + list(zip(xs, ys)) + [(tw, 440)], fill=col)
    if arbustos:
        for _ in range(26):
            i = int(rnd.integers(len(xs)))
            x, y = xs[i], ys[i]
            r = rnd.integers(14, 30)
            c = SPR.mix(col, arbustos, rnd.random() * .5 + .2)
            for dx in (-r * .7, 0, r * .7):
                d.ellipse([x + dx - r, y - r * 1.1, x + dx + r, y + r * .5], fill=c)
    return img


def primer_plano(paleta, tw=2160):
    L = SPR.Lienzo(tw, 300)
    rnd = np.random.default_rng(5)
    v = SPR.dark(paleta[3], 0.35)
    for _ in range(18):
        x = rnd.integers(0, tw)
        for k in range(-3, 4):
            L.poly([(x + k * 14, 300), (x + k * 14 + 10, 300 - rnd.integers(80, 190)), (x + k * 14 + 22, 300)], SPR.mix(v, (150, 205, 160), rnd.random() * .6))
    return L.fin(blur=3.5)


def construir_fondos():
    for i, (c0, c1, hills, g0, g1) in PALETAS.items():
        cielo = degradado(c0, c1, 0, HORIZONTE + 20)
        suelo = degradado(g0, g1, HORIZONTE, H)
        caps = [colinas(hills[k], 330 - k * 20, 60 + k * 20, i * 10 + k, (150, 190, 150) if k == 2 else None) for k in range(3)]
        FONDOS[i] = dict(cielo=cielo, suelo=suelo, caps=caps, fg=primer_plano(PALETAS[i]))


def pintar_fondo(fr, i, t_abs, cam):
    f = FONDOS[i]
    fr.paste(f["cielo"], (0, 0))
    ys = (HORIZONTE - 310, HORIZONTE - 320, HORIZONTE - 330)
    vel = (5, 12, 24)
    for k in range(3):
        off = int((t_abs * vel[k] + cam * (k + 1) * 14) % 1440)
        for x in (-off, 1440 - off):
            if x < W:
                fr.paste(f["caps"][k], (x, ys[k] - 20), f["caps"][k])
    fr.paste(f["suelo"], (0, HORIZONTE))


def pintar_primer_plano(fr, i, t_abs):
    fg = FONDOS[i]["fg"]
    off = int(t_abs * 70 % 2160)
    for x in (-off, 2160 - off):
        if x < W:
            fr.paste(fg, (x, H - 190), fg)


# ---------- dibujo de entidades ----------
class Ctx:
    def __init__(self):
        self.ents = []
        self.over = []

    def e(self, key, x, y, s=1.0, **kw):
        if s <= 0.01:
            return
        self.ents.append(dict(key=key, x=x, y=y, s=s, **kw))

    def o(self, key, x, y, s=1.0, **kw):
        if s > 0.01:
            self.over.append(dict(key=key, x=x, y=y, s=s, **kw))


def blit(fr, im, x, y, s=1.0, sx=1.0, sy=1.0, rot=0.0, alpha=1.0, flip=False, ax=0.5, ay=1.0, **_):
    w, h = im.size
    nw, nh = max(2, int(w * s * sx)), max(2, int(h * s * sy))
    if (nw, nh) != (w, h):
        im = im.resize((nw, nh), Image.BILINEAR)
    if flip:
        im = ImageOps.mirror(im)
        ax = 1 - ax
    px, py = ax * nw, ay * nh
    if rot:
        th = math.radians(rot)
        dx, dy = px - nw / 2, py - nh / 2
        rx, ry = dx * math.cos(th) + dy * math.sin(th), -dx * math.sin(th) + dy * math.cos(th)
        im = im.rotate(rot, resample=Image.BILINEAR, expand=True)
        x0, y0 = x - rx - im.width / 2, y - ry - im.height / 2
    else:
        x0, y0 = x - px, y - py
    if alpha < 1:
        a = im.getchannel("A").point(lambda v: int(v * alpha))
        im = im.copy()
        im.putalpha(a)
    if x0 > W or y0 > H or x0 + im.width < 0 or y0 + im.height < 0:
        return
    fr.paste(im, (int(x0), int(y0)), im)


def dibujar(fr, ctx):
    for en in sorted(ctx.ents, key=lambda e: e.get("z", e["y"])):
        if en.get("sombra", False):
            w = en["sombra"] * en["s"]
            blit(fr, SP["sombra"], en["x"], en["y"] + 12, s=w, sy=0.9, alpha=0.9)
        blit(fr, SP[en["key"]], **{k: v for k, v in en.items() if k != "key"})


def pulso(t_abs):
    """1 en el golpe del compás y decae: sirve para rebotar al ritmo del tango."""
    for i, e in enumerate(D["escenas"]):
        if e["ini_v"] <= t_abs < e["fin_v"]:
            beat = 60 / TEMPOS[i]
            return math.exp(-((t_abs - e["ini_v"]) % beat) / beat * 4.2)
    return 0.0


def parpadeo(t, fase=0.0):
    return ((t + fase) % 3.1) < 0.13


def animal(ctx, base, x, y, s, t, t_abs, fase=0.0, rebote=1.0, rot=0.0, **kw):
    p = pulso(t_abs) * rebote
    resp = math.sin(t * 3 + fase) * 0.012
    key = base + ("_c" if parpadeo(t, fase) else "")
    ctx.e(key, x, y - p * 12 * s, s, sx=1 - 0.035 * p - resp, sy=1 + 0.05 * p + resp, rot=rot, sombra=1.1, **kw)


# ---------- escenas ----------
def cruzar(t, t0, t1, xa, xb, ya, yb=None, arco=0):
    u = seg(t, t0, t1)
    if u <= 0 or u >= 1:
        return None
    yb = ya if yb is None else yb
    return lerp(xa, xb, u), lerp(ya, yb, u) - math.sin(u * math.pi) * arco


def pajaro(ctx, t, t0, t1, xa, xb, y0, y1=None, s=0.6):
    p = cruzar(t, t0, t1, xa, xb, y0, y1, 30)
    if p:
        ctx.e("paj%d" % (int(t * 9) % 2), p[0], p[1], s, flip=xb < xa, z=300)


def escena1(c, t, ta):
    ctx = c
    s = pop(t, 0.0, 0.5)
    animal(ctx, "pig", 360, 950, 1.0 * s, t, ta, rot=math.sin(t * 4) * 2.5 * seg(t, .5, 1))
    ctx.e("sol", 600, 215, 0.55, rot=t * 12, ax=.5, ay=.5, z=-20)
    for i, (a, b, y, s_) in enumerate(((0.3, 2.6, 330, .55), (1.4, 3.6, 440, .5), (2.4, 4.9, 250, .6), (3.6, 6.2, 380, .5), (4.5, 6.4, 300, .45))):
        pajaro(ctx, t, a, b, -100 if i % 2 == 0 else 820, 820 if i % 2 == 0 else -100, y, y - 40, s_)
    x = 740 - 160 * ease_out(seg(t, 1.7, 2.3)) + 200 * ease_out(seg(t, 5.2, 6.0))
    ctx.e("gaucho", x, 905 + math.sin(t * 8) * 4, 0.58, rot=math.sin(t * 6) * 7, sombra=1.3, z=900)
    for k in range(2):
        if t > 2.4:
            ctx.e("mari", 360 + math.cos(t * 2.3 + k * 3) * 230, 600 + math.sin(t * 3.1 + k * 2) * 90, .7 * abs(math.cos(t * 14)) * .5 + .45, z=1500)
    nx = lerp(780, -300, seg(t, 0, 6.5))
    ctx.e("nube_c", nx, 330, 0.8, ay=.5, z=-5)
    ctx.e("nube", lerp(-200, 900, seg(t, 0.5, 8)), 500, 0.6, ay=.5, z=-5)
    if t < 1.5:
        ctx.o("t_vos", 360, 250 + math.sin(t * 20) * 3, pop(t, 0.1) * (1 + .06 * math.sin(t * 16)), ay=.5, rot=-5)
    elif t > 1.7:
        ctx.o("t_chancho", 360, 250, pop(t, 1.7) * (1 + .05 * math.sin(t * 16)), ay=.5, rot=4 * math.sin(t * 9))


def escena2(c, t, ta):
    x = 360 - 700 * ease_out(seg(t, 7.6, 9.4))
    wob = math.sin(t * 22) * 4
    animal(c, "pig", x, 940, 1.1, t, ta, rot=wob, rebote=.5)
    c.e("charco", x + 10, 1010, 1.1, sombra=0, z=1000)
    for i in range(10):
        u = seg(t, 0.8 + i * .75, 1.6 + i * .75)
        if 0 < u < 1:
            a = i * 2.4
            c.o("cora", x - 120 + (i % 4) * 80, 780 - u * 260, .7 * math.sin(u * math.pi) + .2, ay=.5)
    for i in range(6):
        u = (t * 1.6 + i / 6) % 1
        if 1.0 < t < 7.8:
            c.o("estr2", x + math.cos(i * 1.05 + t) * 260 * u, 900 - 160 * u + math.sin(i * 3 + t * 5) * 20, .28, ay=.5)
    p = cruzar(t, 1.5, 5.2, -150, 860, 880, 870, 20)
    if p:
        c.e("pato", p[0], p[1], .55, z=700); c.e("pollo", p[0] + 4, p[1] - 70 + math.sin(t * 10) * 4, .55, z=701)
    p = cruzar(t, 5.8, 9.5, 880, -150, 850, 860, 20)
    if p:
        c.e("pato", p[0], p[1], .5, flip=True, z=700); c.e("pollo", p[0], p[1] - 62 + math.sin(t * 10) * 4, .5, z=701)
    c.e("nube_c", lerp(900, -300, seg(t, 0, 10.5)), 280, .7, ay=.5, z=-5)
    c.e("sol", 120, 210, .5, rot=-t * 10, ax=.5, ay=.5, z=-20)
    u = pop(t, 8.4, .5)
    c.e("cactus", 600, 940, 0.8 * u, z=800)
    for i in range(7):
        u = (t * 2.2 + i * .4) % 1.5
        if 0.8 < t < 7.8 and u < 1.0:
            ang = i * 1.7
            c.o("estr", x + 20 + math.cos(ang) * 120 * u, 960 - 220 * u * (1 - u * .3), .12, ay=.5, alpha=1 - u)


def escena3(c, t, ta):
    c.e("cactus", 360, 905, 1.35 * pop(t, 0.0, .5), sombra=1.7, z=500)
    u = pop(t, 1.0, .6)
    c.e("tag", 360, 980 + (1 - ease_out(seg(t, 1.0, 1.7))) * 60, 1.0 * u, sx=1 + .04 * pulso(ta), sy=1 - .03 * pulso(ta) + (.03 if parpadeo(t) else 0),
        sombra=1.1, rot=math.sin(t * 5) * 2 * seg(t, 1.8, 3), z=900) if u > 0 else None
    if t > 1.3:
        c.o("c_nombre", 360, 190 + math.sin(t * 3) * 5, pop(t, 1.3), ay=.5, rot=-2 * math.sin(t * 4))
        c.o("c_tagua", 360, 275, pop(t, 2.0, .3), ay=.5, rot=2 * math.sin(t * 4))
    c.e("viz", 120, 1000 + 120 * (1 - ease_out(seg(t, 3.0, 3.6))), .6, sombra=1.2, rot=math.sin(t * 5) * 5, z=950)
    c.e("paj%d" % (int(t * 9) % 2), 600, 420 + math.sin(t * 5) * 8, .75 * pop(t, 3.4), z=300)
    if t > 3.7:
        c.o("g_tero", 560, 340, pop(t, 3.7, .3) * .8, ay=1.0, rot=-3 * math.sin(t * 8))
    c.e("nube", lerp(-200, 900, seg(t, 0, 8)), 480, .6, ay=.5, z=-5)
    for i in range(8):
        u = (t * 1.1 + i / 8) % 1
        if t > 1.2:
            c.o("estr", 360 + math.cos(i * .8 + t) * 270, 640 + math.sin(i * 1.3) * 160 - u * 60, .22, ay=.5, alpha=1 - u)


def escena4(c, t, ta):
    ch = math.sin(t * 15)
    animal(c, "tag", 360, 990, 1.05, t, ta, rebote=.3)
    c.ents[-1]["sx"] += .03 * ch; c.ents[-1]["sy"] -= .03 * ch
    tun_s = max(0.0, 1 - seg(t, 0.2, 2.8)) if t < 3 else max(0.0, 1 - seg(t, 3.0, 6.0)) if t < 6.2 else max(0.0, 1 - seg(t, 9.0, 12.0)) if 8.8 < t < 12.2 else 0
    if tun_s > 0:
        c.o("tuna", 360, 985 + ch * 4, 1.1 * tun_s, ay=.5)
    for i in range(7):
        if t > 0.3 and tun_s > 0:
            u = (t * 3 + i / 7) % 1
            c.o("estr", 360 + math.cos(i * 2.1) * 140 * u, 920 - 110 * u + 160 * u * u, .1, ay=.5, alpha=1 - u)
    for k, (cx, cy, s_, t0) in enumerate(((120, 930, .7, 2.0), (610, 930, .7, 3.5), (60, 800, .5, 5.5), (670, 810, .5, 7.0),
                                           (210, 850, .45, 9.5), (530, 850, .45, 11.0), (360, 800, .35, 12.5))):
        c.e("cactus_s", cx, cy, s_ * pop(t, t0, .5), z=cy - 100)
    if t > 3.0:
        c.o("c_menu", 190, 260, pop(t, 3.0) * .95, ay=.5, rot=-5 * math.sin(t * 3))
    if 9.0 < t < 13.5:
        c.o("g_agua", 360, 600, pop(t, 9.0, .3) * .95, ay=1.0)
    c.e("nube", lerp(-200, 900, seg(t, 0, 15.3)), 400, .6, ay=.5, z=-5)


def escena5(c, t, ta):
    sh = (math.sin(t * 90) * 10 * math.exp(-(t - 0.6) * 6)) if t > 0.6 else 0
    c.e("tag", 360 + sh, 905, 0.55, sx=1 + .08 * math.sin(t * 15) * 0, sy=1 + .03 * math.sin(t * 15), z=400, sombra=1.1)
    c.e("cala", 150, 960 + math.sin(t * 6) * 3, .7 * pop(t, 2.5, .5), rot=math.sin(t * 3) * 6, sombra=1.2, z=950)
    cx = 560 + 200 * ease_out(seg(t, 8.5, 10.4))
    c.e("cient", cx, 960 + math.sin(t * 7) * 4, .78 * pop(t, 3.4, .5), rot=math.sin(t * 5) * 4, sombra=1.1, z=960)
    c.e("lupa", cx - 70, 790 + math.sin(t * 5) * 6, .7 * pop(t, 3.6, .4), rot=-15, z=961)
    if t > 0.5:
        s_ = 1 + 2.2 * (1 - ease_out(seg(t, 0.45, 0.7))) if t < 0.7 else 1 + .03 * math.sin(t * 7)
        c.o("sello", 360 + sh, 610 + sh * .5, s_, ay=.5, rot=-8, alpha=min(1, (t - .45) * 6))
    c.o("c_1930", 600, 240, pop(t, 5.0), ay=.5, rot=5 * math.sin(t * 3))
    c.e("nube", lerp(900, -300, seg(t, 0, 11)), 360, .7, ay=.5, z=-5)


def escena6(c, t, ta):
    animal(c, "tag", 360, 990, 1.1, t, ta, rebote=.6)
    for i in range(8):
        u = (t * 1.3 + i / 8) % 1
        c.o("hedor", 360 + math.sin(u * 8 + i) * 50 + (i - 4) * 14, 700 - u * 300, (.5 + u) * .9, ay=.5, alpha=1 - u * .7)
    c.e("viz", 130, 1000, .75 * pop(t, 0.3), rot=math.sin(t * 14) * 8, sombra=1.2, z=950)
    c.e("gaucho", 600, 960, .8 * pop(t, 0.5), rot=math.sin(t * 7) * 10, sombra=1.1, z=960)
    for i in range(3):
        c.o("mosca", 360 + math.cos(t * 6 + i * 2.1) * (180 + i * 30), 720 + math.sin(t * 7 + i) * 90, 1, ay=.5)
    if 0.4 < t < 3.0:
        c.o("t_pfff", 360, 300, pop(t, .4) * (1 + .05 * math.sin(t * 18)), ay=.5, rot=-5 * math.sin(t * 9))


def escena7(c, t, ta):
    animal(c, "tag", 330, 900, .85, t, ta, rebote=.4)
    c.ents[-1]["sx"] += .03 * math.sin(t * 15) * (t > 5)
    c.e("mesa", 360, 1090, 1.1, sombra=0, z=1000)
    for k, (key, lab, x, t0) in enumerate((("tuna", "c_tuna", 190, 1.0), ("raiz", "c_raiz", 360, 2.0), ("brom", "c_brom", 530, 3.0))):
        c.e(key, x, 1030, (.9 if key != "tuna" else 1.0) * pop(t, t0), z=1010)
        if t > t0:
            c.o(lab, x, 790 + math.sin(t * 4 + k) * 4, pop(t, t0 + .1) * .75, ay=.5)
    c.e("emp", 120, 1035, .6 * pop(t, 4.0), z=1011)
    n = int(max(0, t - 5.2) / .45)
    for i in range(min(n, 5)):
        c.e("plato_l" if i == 4 else "plato", 360 + 150 * (1 if i % 2 else -1) * .4, 1140 - i * 26, .9, z=1100 + i)
    if t > 5.4:
        c.o("g_repetir", 560, 620, pop(t, 5.4, .3) * .9, ay=1.0)
    c.e("nube", lerp(-200, 900, seg(t, 0, 8)), 340, .7, ay=.5, z=-5)
    for i in range(5):
        u = (t * .9 + i / 5) % 1
        c.o("estr2", 120 + i * 120, 600 - u * 120, .2, ay=.5, alpha=1 - u)


def escena8(c, t, ta):
    if t < 4.3:
        u = pop(t, 0.0, .5)
        c.e("pata", 360, 960, 1.15 * u, sy=1 + .03 * pulso(ta), sombra=1.8, z=900)
        c.o("c_3", 360, 260, pop(t, .5) * (1 + .04 * math.sin(t * 10)), ay=.5, rot=-3)
        for i in range(3):
            if t > .8 + i * .5:
                c.o("estr", 360 + (i - 1) * 100 * 1.15, 720, .3 * pop(t, .8 + i * .5), ay=.5, rot=t * 90)
    n = 6
    for i in range(n):
        x = lerp(1100 + i * 180, -700 + i * 180, seg(t, 4.0, 10.0)) if t > 3.8 else 2000
        s_ = .46 + .07 * (i % 3)
        y = 880 + (i % 3) * 36
        c.e("tag" + ("_c" if parpadeo(t, i * .4) else ""), x, y - pulso(ta) * 10 * s_ - abs(math.sin(t * 6 + i)) * 6, s_,
            sx=1 + .03 * pulso(ta), sy=1 - .03 * pulso(ta), sombra=1.1, z=y)
    if t > 4.3:
        c.o("c_manada", 360, 240, pop(t, 4.3), ay=.5, rot=2 * math.sin(t * 3))
    c.e("nube", lerp(900, -300, seg(t, 0, 10)), 420, .6, ay=.5, z=-5)


def escena9(c, t, ta):
    sx = 1.0
    c.e("sol", 360, lerp(1000, 520, ease_out(seg(t, 0, 2.5))), 1.5, rot=t * 6, ax=.5, ay=.5, alpha=.9, z=-20)
    if t > 0.2:
        for k, s_i in enumerate(("sello_i", "sello_d")):
            sg = -1 if k == 0 else 1
            u = seg(t, 0.0, 1.4)
            c.o(s_i, 360 + sg * (55 + 220 * u), 560 + 700 * u * u, 1.0, rot=sg * 40 * u, ay=.5, ax=.5 if k else .5, alpha=1 - u * .7)
    if t < 1.4:
        c.o("sello", 360, 560, 1.0, ay=.5, rot=-8, alpha=max(0, 1 - t * 8) * 0) if False else None
    animal(c, "tag", 360, 960, 1.15 * pop(t, 0.8, .6), t, ta, rebote=1.2)
    for i in range(36):
        u = (t * .55 + i * .173) % 1
        if t > 1.0:
            cx = (i * 97) % 720
            c.o("estr" if i % 2 else "estr2", cx + math.sin(u * 9 + i) * 30, -40 + u * 1360, .16 + (i % 3) * .05, ay=.5, rot=u * 360 * (1 if i % 2 else -1))
    if t > 2.5:
        c.o("c_70", 360, 250, pop(t, 2.5) * (1 + .03 * math.sin(t * 9)), ay=.5, rot=3 * math.sin(t * 4))


def escena10(c, t, ta, T):
    s = 1.05 + .12 * seg(t, 3.0, 8.5)
    animal(c, "tag", 360, 985, s, t, ta, rebote=1.4)
    c.e("sol", 360, 640, 2.1, rot=t * 8, ax=.5, ay=.5, alpha=.5, z=-20)
    c.e("pig", 105, 960, .42 * pop(t, 1.2), sx=1, sy=1 + .06 * pulso(ta), sombra=1.1, z=950)
    c.e("gaucho", 620, 960, .72 * pop(t, 1.6), rot=math.sin(t * 12) * 8, sombra=1.1, z=960)
    c.e("viz", 185, 1030, .5 * pop(t, 2.0), sy=1 + .1 * pulso(ta), sombra=1.2, z=1010)
    c.e("cient", 540, 1040, .45 * pop(t, 2.4), sy=1 + .1 * pulso(ta), sombra=1.2, z=1040)
    for i in range(30):
        u = (t * .6 + i * .211) % 1
        if t > 0.6:
            c.o("estr" if i % 2 else "estr2", (i * 83) % 720 + math.sin(u * 8 + i) * 30, -30 + u * 1330, .16 + (i % 3) * .05, ay=.5, rot=u * 400)
    if t > T - 2.7:
        c.o("t_orgullo", 360, 245, pop(t, T - 2.7, .4) * (1 + .05 * math.sin(t * 14)), ay=.5, rot=3 * math.sin(t * 6))
    if t > T - 4.6 and t < T - 2.7:
        c.o("c_obt", 360, 330, pop(t, T - 4.6, .4) * .75, ay=.5)


# ---------- subtítulos ----------
RESALTAR = {"chancho", "gordo", "panzón", "peludo", "orgullo", "extinto", "cactus", "tuna", "taguá", "vivo", "vos", "quimilero"}


def armar_captions():
    out = []
    for ini, fin, txt in D["cues"]:
        piezas = [p for p in re.findall(r"[^.,?!…]+[.,?!…]*\s*", txt) if p.strip()]
        trozos, act = [], ""
        for p in piezas:
            if act and len((act + p).strip()) > 30:
                trozos.append(act.strip()); act = p
            else:
                act += p
        if act.strip():
            trozos.append(act.strip())
        total = sum(len(z) + 4 for z in trozos)
        a = ini
        for z in trozos:
            b = a + (fin - ini) * (len(z) + 4) / total
            out.append((a, b, z))
            a = b
    return out


def caption_img(txt):
    if txt in CACHE_TXT:
        return CACHE_TXT[txt]
    fuente = SPR.fuente(60)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    palabras, lineas, act = txt.split(), [], ""
    for p in palabras:
        prueba = (act + " " + p).strip()
        if probe.textlength(prueba, font=fuente) > 620 and act:
            lineas.append(act); act = p
        else:
            act = prueba
    lineas.append(act)
    h = 78 * len(lineas) + 30
    im = Image.new("RGBA", (680, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for n, ln in enumerate(lineas):
        ws = [probe.textlength(w + " ", font=fuente) for w in ln.split()]
        x = (680 - sum(ws) + probe.textlength(" ", font=fuente)) / 2
        for w, wd in zip(ln.split(), ws):
            limpio = re.sub(r"[^\wáéíóúñü]", "", w.lower())
            col = (255, 226, 110) if limpio in RESALTAR else (255, 255, 255)
            d.text((x, 10 + n * 78 + 6), w, font=fuente, fill=(70, 40, 80), stroke_width=11, stroke_fill=(70, 40, 80))
            d.text((x, 10 + n * 78), w, font=fuente, fill=col, stroke_width=9, stroke_fill=(90, 50, 100))
            x += wd
    CACHE_TXT[txt] = im
    return im


def pintar_caption(fr, ta):
    for a, b, z in CAPTIONS:
        if a <= ta < b + 0.05:
            im = caption_img(z)
            s = 0.88 + 0.12 * ease_back((ta - a) / 0.16)
            blit(fr, im, 360, 1150 - (0 if im.height < 200 else 30), s=s, ay=1.0)
            return


# ---------- fotograma ----------
ESCENAS = [escena1, escena2, escena3, escena4, escena5, escena6, escena7, escena8, escena9, escena10]


def escena_en(ta):
    for i, e in enumerate(D["escenas"]):
        if ta < e["fin_v"] or i == len(D["escenas"]) - 1:
            return i, e
    return 0, D["escenas"][0]


def fotograma(n):
    ta = n / FPS
    i, e = escena_en(ta)
    t = ta - e["ini_v"]
    T = e["fin_v"] - e["ini_v"]
    fr = Image.new("RGB", (W, H))
    ctx = Ctx()
    f = ESCENAS[i]
    f(ctx, t, ta, T) if i == 9 else f(ctx, t, ta)
    pintar_fondo(fr, i + 1, ta, 0)
    dibujar(fr, ctx)
    pintar_primer_plano(fr, i + 1, ta)
    for o in sorted(ctx.over, key=lambda e: 0):
        blit(fr, SP[o["key"]], **{k: v for k, v in o.items() if k != "key"})
    # golpe de cámara al cambiar de escena
    if t < 0.3:
        z = 1 + 0.06 * (1 - t / 0.3) ** 2
        w2, h2 = int(W / z), int(H / z)
        fr = fr.crop(((W - w2) // 2, (H - h2) // 2, (W - w2) // 2 + w2, (H - h2) // 2 + h2)).resize((W, H), Image.BILINEAR)
        if t < 0.1:
            fr = Image.blend(fr, Image.new("RGB", (W, H), (255, 255, 255)), 0.45 * (1 - t / 0.1))
    pintar_caption(fr, ta)
    if ta > D["total"] - 0.5:
        fr = Image.blend(fr, Image.new("RGB", (W, H), (255, 245, 235)), min(1, (ta - (D["total"] - 0.5)) / 0.5))
    return fr


def iniciar():
    global SP, D, CAPTIONS
    D = cargar()
    SP = SPR.construir()
    construir_fondos()
    CAPTIONS = armar_captions()


def render(n):
    return fotograma(n).tobytes()


def main():
    iniciar()
    if "--frames" in sys.argv:
        out = AQUI / "preview"
        out.mkdir(exist_ok=True)
        for s in sys.argv[sys.argv.index("--frames") + 1:]:
            fotograma(int(float(s) * FPS)).save(out / f"f{float(s):06.2f}.png")
        return
    total = int(D["total"] * FPS)
    audio = AQUI / "audio" / "episodio-003-mezcla.mp3"
    destino = AQUI / "episodio-003.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-i", str(audio), "-vf", "scale=1080:1920:flags=lanczos", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", str(destino)],
                          stdin=subprocess.PIPE)
    with Pool(4, initializer=iniciar) as pool:
        for k, raw in enumerate(pool.imap(render, range(total), chunksize=6)):
            ff.stdin.write(raw)
            if k % 150 == 0:
                print(f"{k}/{total}", flush=True)
    ff.stdin.close()
    ff.wait()
    print("listo", destino)


if __name__ == "__main__":
    main()
