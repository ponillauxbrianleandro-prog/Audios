"""Objetos animados y escenas de los 5 shorts de pH."""
import math
from functools import lru_cache
from types import SimpleNamespace

import numpy as np
from PIL import Image, ImageDraw

from motor import *  # noqa: F401,F403
from motor import (AGUA, AMARILLO, AZUL, BG, BLANCO, GRIS, H, NARANJA, ROJO, ROSA, S, VERDE, VIDRIO, VIOLETA, W,
                   Capa, Lienzo, back, clamp, color_btb, color_escala, comp, cronograma, ease, ease_out, fmt, fuente,
                   lerp, mezcla, muelle, rampa, evt_color)

FX, FY, FW, FH = 540, 810, 380, 470
DX, DY, DR = 540, 1350, 250

PALABRAS_COLOR = {
    "amarillo": AMARILLO, "verde": VERDE, "azul": AZUL, "rosado": ROSA,
    "ácido": NARANJA, "ácida": NARANJA, "ácidos": NARANJA, "ácidas": NARANJA,
    "básico": AZUL, "básica": AZUL, "base": AZUL, "bases": AZUL, "neutro": VERDE, "neutras": VERDE, "neutra": VERDE,
}


# ============ geometría y líquidos ============
def geo(cx, cy, ancho, alto):
    top, base = cy - alto / 2, cy + alto / 2
    yn, cu = top + alto * 0.38, ancho * 0.30
    return SimpleNamespace(
        cx=cx, cy=cy, top=top, base=base, yn=yn, cu=cu, ancho=ancho, alto=alto,
        ysup=lambda n: lerp(base - 8, yn + 12, n),
        anch=lambda y: lerp(cu, ancho, clamp((y - yn) / (base - yn))))


def liquido(c, pts, bbox, ys, est, t):
    """Pinta un líquido: gradiente vertical + mancha de color que se expande en remolino desde la entrada."""
    x0, y0, x1, y1 = [int(v) for v in bbox]
    if x1 <= x0 or y1 <= y0:
        return
    X, Y = np.meshgrid(np.arange(x0, x1, dtype=np.float32), np.arange(y0, y1, dtype=np.float32))
    base, nuevo, prog = np.array(est["base"], np.float32), np.array(est["nuevo"], np.float32), est["prog"]
    if prog <= 0:
        col = np.broadcast_to(base, X.shape + (3,)).copy()
        mix = np.zeros_like(X)
        d = ang = None
    else:
        ex, ey = est["ex"], ys
        d = np.hypot(X - ex, Y - ey)
        ang = np.arctan2(Y - ey, X - ex)
        R = prog * max(x1 - x0, y1 - y0) * 1.7
        wob = 30 * np.sin(ang * 3 + t * 3.1) + 16 * np.sin(ang * 5 - t * 4.3)
        f = np.clip((R + wob - d) / 70, 0, 1)
        mix = f * (1 - f) * 4
        col = base * (1 - f[..., None]) + nuevo * f[..., None]
        sw = 0.5 + 0.5 * np.sin(d * 0.07 - t * 5 + ang * 2)
        col += (mix * sw * 70)[..., None]
    sh = 1.18 - 0.42 * np.clip((Y - ys) / max(1, y1 - ys), 0, 1)
    col = np.clip(col * sh[..., None], 0, 255)
    img = Image.fromarray(col.astype(np.uint8)).resize(((x1 - x0) * S, (y1 - y0) * S), Image.BILINEAR)
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).polygon([((x - x0) * S, (y - y0) * S) for x, y in pts], fill=255)
    comp(c.img, x0 * S, y0 * S, m, np.asarray(img, dtype=np.float32), 1.0)


def estado(t, c0, ev, nivel, agit=0.0):
    base, nuevo, prog, ex = evt_color(t, c0, ev)
    return {"base": base, "nuevo": nuevo, "prog": prog, "ex": ex, "nivel": nivel, "agit": agit}


def agit_de(t, intervalos):
    v = 0.0
    for a, b in intervalos:
        if a <= t <= b:
            v = max(v, 1.0)
        elif t > b:
            v = max(v, math.exp(-4 * (t - b)))
    return v


def matraz(c, g, t, est, brillo=1.0):
    cx = g.cx
    ys = g.ysup(est["nivel"])
    col_m = mezcla(est["base"], est["nuevo"], est["prog"])
    c.sombra(cx, g.base + 16, g.ancho * 0.62, 24, 0.65)
    c.glow(cx, g.base - g.alto * 0.32, g.alto * 0.9, col_m, 0.36 * brillo)
    amp = 3 + 10 * est["agit"]
    wl, n = g.anch(ys) / 2 - 9, 28
    sup = [(cx - wl + 2 * wl * i / n,
            ys + amp * math.sin(t * 3.4 + i * 0.55) * (0.35 + 0.65 * math.sin(i / n * math.pi))) for i in range(n + 1)]
    pts = sup + [(cx + g.anch(g.base) / 2 - 12, g.base - 10), (cx - g.anch(g.base) / 2 + 12, g.base - 10)]
    liquido(c, pts, (cx - g.ancho / 2, ys - 20, cx + g.ancho / 2, g.base), ys, est, t)
    c.linea(sup, mezcla(col_m, BLANCO, 0.65), 4)
    cont = [(cx - g.cu / 2, g.top), (cx - g.cu / 2, g.yn), (cx - g.ancho / 2, g.base - 12), (cx - g.ancho / 2 + 14, g.base),
            (cx + g.ancho / 2 - 14, g.base), (cx + g.ancho / 2, g.base - 12), (cx + g.cu / 2, g.yn), (cx + g.cu / 2, g.top)]
    c.poly_grad(cont, (255, 255, 255), (190, 230, 250), 0.10)
    c.linea(cont, VIDRIO, 7)
    c.linea([(cx - g.cu / 2 - 16, g.top), (cx + g.cu / 2 + 16, g.top)], VIDRIO, 9)
    c.linea([(cx - g.ancho * 0.30, g.base - g.alto * 0.14), (cx - g.ancho * 0.18, g.yn + g.alto * 0.16)],
            (235, 248, 255), 8)
    c.linea([(cx - g.cu * 0.22, g.top + 14), (cx - g.cu * 0.22, g.yn - 10)], (235, 248, 255), 5)
    return ys


def tubo(c, cx, cy, ancho, alto, t, est):
    top, base, r = cy - alto / 2, cy + alto / 2, ancho / 2
    ys = lerp(base - r, top + 40, est["nivel"])
    col_m = mezcla(est["base"], est["nuevo"], est["prog"])
    c.sombra(cx, base + 14, ancho * 1.1, 20, 0.6)
    c.glow(cx, cy + alto * 0.1, alto * 0.7, col_m, 0.30)
    amp = 3 + 8 * est["agit"]
    n = 14
    sup = [(cx - r + 7 + (2 * r - 14) * i / n, ys + amp * math.sin(t * 3.4 + i * 0.7)) for i in range(n + 1)]
    fondo = [(cx + (r - 7) * math.cos(math.radians(a)), base - r + (r - 7) * math.sin(math.radians(a)))
             for a in range(0, 181, 12)]
    pts = sup + fondo
    liquido(c, pts, (cx - r, ys - 14, cx + r, base), ys, est, t)
    c.linea(sup, mezcla(col_m, BLANCO, 0.65), 4)
    arco = [(cx - r, top)] + [(cx - r * math.cos(math.radians(a)), base - r + r * math.sin(math.radians(a)))
                              for a in range(0, 181, 12)] + [(cx + r, top)]
    c.linea(arco, VIDRIO, 7)
    c.linea([(cx - r - 12, top), (cx + r + 12, top)], VIDRIO, 9)
    c.linea([(cx - r * 0.5, top + 30), (cx - r * 0.5, base - r - 10)], (235, 248, 255), 5)
    return ys


def vaso(c, cx, cy, ancho, alto, t, est):
    top, base = cy - alto / 2, cy + alto / 2
    wb = ancho * 0.74
    ys = lerp(base - 8, top + 24, est["nivel"])
    wa = lambda y: lerp(wb, ancho, (y - base) / (top - base))
    col_m = mezcla(est["base"], est["nuevo"], est["prog"])
    c.sombra(cx, base + 14, ancho * 0.7, 22, 0.6)
    c.glow(cx, cy + alto * 0.1, alto * 0.9, col_m, 0.3)
    amp = 3 + 10 * est["agit"]
    n = 20
    sup = [(cx - wa(ys) / 2 + 8 + (wa(ys) - 16) * i / n, ys + amp * math.sin(t * 3.4 + i * 0.6)) for i in range(n + 1)]
    pts = sup + [(cx + wb / 2 - 6, base - 8), (cx - wb / 2 + 6, base - 8)]
    liquido(c, pts, (cx - ancho / 2, ys - 16, cx + ancho / 2, base), ys, est, t)
    c.linea(sup, mezcla(col_m, BLANCO, 0.65), 4)
    cont = [(cx - ancho / 2, top), (cx - wb / 2, base), (cx + wb / 2, base), (cx + ancho / 2, top)]
    c.poly_grad(cont, (255, 255, 255), (190, 230, 250), 0.10)
    c.linea(cont, VIDRIO, 7)
    c.linea([(cx - ancho * 0.36, top + 40), (cx - wb * 0.36, base - 30)], (235, 248, 255), 7)
    return ys


def iones(c, g, ys, t, n, tipo, fase=0.0):
    col = NARANJA if tipo == "h" else AZUL
    txt = "H⁺" if tipo == "h" else "OH⁻"
    for i in range(int(math.ceil(n))):
        a = clamp(n - i)
        r1, r2, r3 = (i * 0.618 + fase) % 1, (i * 0.7549 + fase * 2) % 1, (i * 0.5698) % 1
        y = lerp(ys + 40, g.base - 44, 0.5 + 0.5 * math.sin(t * (0.8 + r2 * 0.9) + r1 * 6.28))
        hw = max(0, g.anch(y) / 2 - 36)
        x = g.cx + hw * math.sin(t * (0.6 + r3 * 0.8) + r2 * 6.28)
        rad = (20 if tipo == "h" else 23) * ease(a)
        if rad < 6:
            continue
        c.circ(x, y, rad + 5, mezcla(col, (255, 255, 255), 0.25))
        c.circ(x, y, rad, col)
        c.circ(x - rad * 0.3, y - rad * 0.35, rad * 0.28, mezcla(col, (255, 255, 255), 0.6))
        c.d.text((c.X(x), c.Y(y + 1)), txt, font=fuente("ExtraBold", rad * 0.92), fill=(255, 255, 255), anchor="mm")


def ions_ph(c, g, ys, t, ph, k=1.0):
    nh = clamp((7 - ph) * 2.1, 0, 14) + 2 * math.exp(-abs(ph - 7) * 2)
    no = clamp((ph - 7) * 1.7, 0, 14) + 2 * math.exp(-abs(ph - 7) * 2)
    iones(c, g, ys, t, nh * k, "h")
    iones(c, g, ys, t, no * k, "oh", 0.37)


# ============ gotas, chorros, salpicaduras ============
def gota(c, x, y, tam, color):
    c.circ(x, y, tam, color)
    c.poly([(x - tam * 0.92, y - tam * 0.3), (x + tam * 0.92, y - tam * 0.3), (x, y - tam * 2.2)], color)
    c.circ(x - tam * 0.3, y - tam * 0.1, tam * 0.25, mezcla(color, (255, 255, 255), 0.55))


def salpicadura(c, x, y, tt, color):
    if tt < 0 or tt > 0.8:
        return
    for k, r0 in enumerate((0.0, 0.18)):
        p = (tt - r0) / 0.6
        if 0 < p < 1:
            rad = 16 + 120 * ease_out(p)
            c.d.ellipse([c.X(x - rad), c.Y(y - rad * 0.16), c.X(x + rad), c.Y(y + rad * 0.16)],
                        outline=mezcla(color, (255, 255, 255), 0.6), width=int(max(1, 5 * (1 - p)) * S))
    for i in range(7):
        vx, vy = (i - 3) * 48, -300 - (i % 3) * 70
        px_, py_ = x + vx * tt, y + vy * tt + 900 * tt * tt
        c.circ(px_, py_, 7 * (1 - tt / 0.8) + 1, mezcla(color, (255, 255, 255), 0.35))


def chorro(c, p0, p1, color, grosor, cabeza=1.0, cola=0.0, t=0.0):
    pts = []
    n = 26
    for i in range(n + 1):
        u = lerp(cola, cabeza, i / n)
        pts.append((lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u * u)))
    if len(pts) > 1 and cabeza > cola:
        g = grosor * (0.9 + 0.1 * math.sin(t * 28))
        c.linea(pts, color, g)
        c.linea(pts, mezcla(color, (255, 255, 255), 0.5), g * 0.32)


def gotas_cayendo(c, x, y0, y1, t, t_ini, t_fin, color, periodo=0.45, tam=13, sal=True):
    if t < t_ini:
        return
    k_hi = int((min(t, t_fin) - t_ini) / periodo)
    for k in range(max(0, k_hi - 2), k_hi + 1):
        tk = t_ini + k * periodo
        if tk > t_fin:
            continue
        f = (t - tk) / 0.4
        if 0 <= f < 1:
            gota(c, x + 6 * math.sin(k * 2.1), lerp(y0, y1, f * f), tam, color)
        elif f >= 1 and sal:
            salpicadura(c, x + 6 * math.sin(k * 2.1), y1, (t - tk - 0.4), color)


# ============ sprites ============
@lru_cache(maxsize=None)
def sprite_botella(kind, tapa=True):
    cuerpos = {"acido": ((214, 72, 78), (120, 28, 34), "ÁCIDO", ROJO), "base": ((62, 112, 232), (28, 48, 130), "BASE", AZUL),
               "detergente": ((70, 195, 205), (255, 255, 255), "detergente", (20, 120, 130)),
               "vinagre": ((214, 150, 80), (70, 40, 20), "vinagre", (110, 60, 20))}
    w, h = 200, 340
    s = Capa(w, h)
    if kind == "soda":
        s.rect(-80, -h / 2 + 70, 80, h / 2 - 8, (232, 240, 245), r=26)
        s.rect(-80, h / 2 - 70, 80, h / 2 - 8, (200, 214, 222), r=26)
        s.rect(-92, -h / 2 + 22, 92, -h / 2 + 76, (214, 40, 48), r=12)
        s.rect(-62, -h / 2 + 100, 62, h / 2 - 90, (255, 255, 255), r=12)
        s.d.text((s.X(0), s.Y(-5)), "NaOH", font=fuente("ExtraBold", 40), fill=(180, 30, 40), anchor="mm")
        s.d.text((s.X(0), s.Y(40)), "soda cáustica", font=fuente("Bold", 17), fill=(90, 90, 100), anchor="mm")
        s.rect(-64, -h / 2 + 90, -48, h / 2 - 20, (255, 255, 255), r=8)
        return s
    col, ct, et, cet = cuerpos[kind]
    s.rect(-78, -h / 2 + 84, 78, h / 2 - 6, col, r=34)
    s.rect(-78, h / 2 - 60, 78, h / 2 - 6, mezcla(col, (0, 0, 0), 0.25), r=30)
    s.rect(-34, -h / 2 + 40, 34, -h / 2 + 100, col)
    s.rect(-34, -h / 2 + 40, 34, -h / 2 + 52, mezcla(col, (255, 255, 255), 0.3))
    if tapa:
        s.rect(-40, -h / 2 + 8, 40, -h / 2 + 52, ct, r=8)
    s.rect(-60, -h / 2 + 140, 60, h / 2 - 80, (250, 250, 250), r=14)
    s.d.text((s.X(0), s.Y(-h / 2 + 140 + (h / 2 - 80 + h / 2 - 140) / 2 - 8 + 0)), et,
             font=fuente("ExtraBold", 34 if len(et) <= 5 else (27 if len(et) <= 7 else 21)), fill=cet, anchor="mm")
    s.rect(-70, -h / 2 + 100, -56, h / 2 - 20, mezcla(col, (255, 255, 255), 0.45), r=7)
    return s


@lru_cache(maxsize=None)
def sprite_limon(cara=False):
    s = Capa(380, 280)
    L = (255, 214, 64)
    s.elip(-150, -105, 150, 105, L)
    s.poly([(130, -28), (178, -42), (138, 22)], L)
    s.poly([(-130, 28), (-178, 42), (-138, -22)], L)
    s.elip(-150, 10, 150, 105, (240, 190, 40))
    s.elip(-120, -92, 90, 40, L)
    s.elip(-110, -80, -30, -50, (255, 238, 150))
    s.elip(20, -140, 100, -92, VERDE)
    s.elip(36, -132, 90, -112, (110, 215, 160))
    if cara:
        o = (95, 60, 0)
        for sx in (-1, 1):
            x = sx * 54
            s.linea([(x - 24 * sx, -34), (x + 8 * sx, -18), (x - 24 * sx, -2)], o, 11)
        s.linea([(-44 + 88 * i / 8, 42 + 11 * math.sin(i * 1.6)) for i in range(9)], o, 11)
    return s


@lru_cache(maxsize=None)
def sprite_gotero(color):
    s = Capa(110, 380)
    s.elip(-38, -190, 38, -80, (170, 40, 52))
    s.elip(-26, -178, -4, -130, (225, 110, 120))
    s.rect(-30, -92, 30, -60, (60, 70, 80), r=6)
    s.poly([(-20, -62), (20, -62), (6, 176), (-6, 176)], (214, 238, 248))
    s.poly([(-12, -30), (12, -30), (4, 150), (-4, 150)], color)
    s.linea([(-15, -56), (-5, 140)], (255, 255, 255), 4)
    return s


# ============ animaciones compuestas ============
def gotero(c, t, t0, color, g, ys, n=2):
    """Gotero que entra, forma gotas, las deja caer (impacto del 1.º a t0+1.3) y se va."""
    ytip = g.top - 70
    t_fin = t0 + 0.4 + 0.7 * (n - 1) + 1.1
    if t < t0 - 0.05 or t > t_fin + 0.7:
        return
    ent = ease((t - t0) / 0.5)
    sal = ease((t - (t_fin - 0.1)) / 0.6)
    off = -330 * (1 - ent) - 330 * sal
    c.pegar(sprite_gotero(color), g.cx, ytip - 176 * 0.62 + off, sx=0.62, sy=0.62)
    for k in range(n):
        tk = t0 + 0.4 + 0.7 * k
        f = (t - tk) / 0.5
        if 0 <= f < 1:
            gota(c, g.cx, ytip + off + 4, 16 * ease(f), color)
        elif 0.5 <= (t - tk) / 0.5 and (t - tk) < 0.9:
            ff = (t - tk - 0.5) / 0.4
            gota(c, g.cx, lerp(ytip + 4, ys, ff * ff), 15, color)
        elif (t - tk) >= 0.9:
            salpicadura(c, g.cx, ys, t - tk - 0.9, color)


def vertido(c, t, t0, dur, kind, rest, g, ys, lado, color, grosor=15, alfa=1.0):
    """Botella que se inclina y vuelca un chorro curvo dentro del matraz. lado=+1: botella a la izquierda."""
    a = ease((t - t0) / 0.7) * (1 - ease((t - (t0 + dur - 0.7)) / 0.7))
    th = 118 * a
    Lh = 170 - 14
    tip_t = (g.cx - lado * 55, g.top - 62)
    cxp = tip_t[0] - lado * Lh * math.sin(math.radians(118))
    cyp = tip_t[1] + Lh * math.cos(math.radians(118))
    pos = (lerp(rest[0], cxp, a), lerp(rest[1], cyp, a))
    c.pegar(sprite_botella(kind, a < 0.03), pos[0], pos[1], rot=-lado * th, alfa=alfa)
    tip = (pos[0] + lado * Lh * math.sin(math.radians(th)), pos[1] - Lh * math.cos(math.radians(th)))
    cab = ease((t - (t0 + 0.6)) / 0.3)
    col = ease((t - (t0 + dur - 0.8)) / 0.3)
    fuerza = cab * (1 - col)
    if fuerza > 0.02:
        chorro(c, tip, (g.cx, ys), color, grosor * fuerza, cabeza=cab, cola=col, t=t)
        if cab >= 1 and col < 0.95:
            salpicadura(c, g.cx, ys, (t * 1.0) % 0.55, color)
    return fuerza



def botella_vertiendo(c, t, kind, rest, pours, g, ys, lado, color, alfa=1.0):
    """Botella en reposo salvo en los intervalos de vertido: pours = [(t0, dur, grosor)]."""
    for t0, dur, gr in pours:
        if t0 <= t < t0 + dur:
            return vertido(c, t, t0, dur, kind, rest, g, ys, lado, color, gr, alfa)
    c.pegar(sprite_botella(kind), rest[0], rest[1], alfa=alfa)
    return 0.0


def limon_exprimido(c, t, t0, t1, rest, g, ys, alfa=1.0, cara=False):
    ida = ease((t - t0) / 0.7)
    vuelta = ease((t - t1) / 0.7)
    a = ida * (1 - vuelta)
    x = lerp(rest[0], g.cx, a)
    y = lerp(rest[1], g.top - 125, a)
    pul = 0.5 + 0.5 * math.sin((t - t0) * 7.5)
    sq = pul if (t0 + 0.7 < t < t1) else 0
    sx, sy = 0.74 * (1 + 0.14 * sq), 0.74 * (1 - 0.22 * sq)
    if cara:
        w = 0.07 * math.sin(t * 9)
        sx, sy = 0.9 + w, 0.9 - w
    c.pegar(sprite_limon(cara), x, y, rot=-12 * a, sx=sx, sy=sy, alfa=alfa)
    if t0 + 0.9 < t < t1:
        gotas_cayendo(c, g.cx, y + 70, ys, t, t0 + 0.9, t1 - 0.3, (255, 232, 130), 0.4)


# ============ medidor (dial) ============
def dial(c, v, t, resalte=None, etiqueta=None):
    cx, cy, r = DX, DY, DR
    c.sombra(cx, cy + 30, r * 0.95, 34, 0.55)
    disco = [(cx + (r + 8) * math.cos(math.radians(a)), cy + (r + 8) * math.sin(math.radians(a))) for a in range(180, 361, 6)]
    c.poly_grad(disco + [(cx + r + 8, cy + 56), (cx - r - 8, cy + 56)], (36, 72, 94), (12, 30, 42))
    c.linea(disco, (90, 140, 165), 3)
    N = 70
    for i in range(N):
        a0, a1 = 180 + 180 * i / N, 180 + 180 * (i + 1) / N + 0.8
        col = color_escala(14 * (i + 0.5) / N)
        if resalte and not (resalte[0] <= 14 * (i + 0.5) / N <= resalte[1]):
            col = mezcla(col, (20, 40, 54), 0.62)
        c.arco_grueso(cx, cy, r - 62, r - 16, a0, a1, col)
    if resalte:
        pulso = 0.5 + 0.5 * math.sin(t * 5)
        a0, a1 = 180 + 180 * resalte[0] / 14, 180 + 180 * resalte[1] / 14
        c.arco_grueso(cx, cy, r - 72, r - 66, a0, a1, mezcla((255, 255, 255), (160, 210, 240), pulso))
        c.arco_grueso(cx, cy, r - 12, r - 6, a0, a1, mezcla((255, 255, 255), (160, 210, 240), pulso))
    for n in range(0, 15, 1):
        a = math.radians(180 + 180 * n / 14)
        mayor = n % 7 == 0
        if n % 2 == 0 or n == 7:
            rx, ry = cx + (r - 92) * math.cos(a), cy + (r - 92) * math.sin(a)
            c.d.text((c.X(rx), c.Y(ry)), str(n), font=fuente("ExtraBold" if n == 7 else "Bold", 30 if n == 7 else 25),
                     fill=BLANCO if n == 7 else GRIS, anchor="mm")
        c.linea([(cx + (r - 16) * math.cos(a), cy + (r - 16) * math.sin(a)),
                 (cx + (r - 16 - (14 if mayor else 8)) * math.cos(a), cy + (r - 16 - (14 if mayor else 8)) * math.sin(a))],
                BLANCO, 3)
    ang = math.radians(180 + 180 * clamp(v, -0.4, 14.4) / 14)
    tip = (cx + (r - 24) * math.cos(ang), cy + (r - 24) * math.sin(ang))
    c.glow(tip[0], tip[1], 70, color_escala(clamp(v, 0, 14)), 0.7)
    px_, py_ = -math.sin(ang), math.cos(ang)
    c.poly([(cx + px_ * 3 + 9 * px_ * 0, cy), (tip[0], tip[1]), (cx - px_ * 0, cy)], (255, 255, 255))
    c.poly([(cx + px_ * 11, cy + py_ * 11), tip, (cx - px_ * 11, cy - py_ * 11)], (245, 250, 252))
    c.circ(cx, cy, 30, (230, 240, 246))
    c.circ(cx, cy, 20, (30, 60, 80))
    c.circ(cx, cy, 8, color_escala(clamp(v, 0, 14)))
    c.texto(cx, cy + 112, f"pH {fmt(clamp(v, -0.4, 14.4))}", 82, color_escala(clamp(v, 0, 14)), sombra=True)
    if etiqueta:
        c.texto(cx, cy - r - 26, etiqueta, 32, BLANCO, "Bold", alfa=0.95)


# ============ otros elementos ============
def cartel(c, y, texto, color, t_in, tam=50, x=540, alfa=1.0):
    k = back(t_in / 0.4) * alfa
    if k <= 0.02:
        return
    w = c.ancho_texto(texto, tam) + 80
    h = tam + 46
    s = clamp(k, 0, 1.1)
    c.rr_grad(x - w / 2 * s, y - h / 2 * s, x + w / 2 * s, y + h / 2 * s, mezcla(BG, color, 0.38), mezcla(BG, color, 0.16),
              0.95, r=h / 2 * s)
    c.rect(x - w / 2 * s, y - h / 2 * s, x + w / 2 * s, y + h / 2 * s, None, r=h / 2 * s, outline=color, ancho=3)
    if k > 0.6:
        c.texto(x, y, texto, tam, color, alfa=clamp((k - 0.6) / 0.4))


def x_roja(c, cx, cy, r, prog=1.0):
    k = ease(prog)
    if k <= 0:
        return
    c.linea([(cx - r, cy - r), (cx - r + 2 * r * k, cy - r + 2 * r * k)], ROJO, 13)
    if k > 0.5:
        k2 = (k - 0.5) * 2
        c.linea([(cx + r, cy - r), (cx + r - 2 * r * k2, cy - r + 2 * r * k2)], ROJO, 13)


def burbujas_jabon(c, x0, x1, y0, y1, t, t_ini, n=9):
    for i in range(n):
        f = ((t - t_ini) * 0.33 + i / n) % 1.0
        if t < t_ini + i * 0.15:
            continue
        x = lerp(x0, x1, (i * 0.618) % 1.0) + 26 * math.sin(t * 2 + i)
        y = lerp(y0, y1, f)
        r = 22 + 24 * ((i * 7) % 5) / 4
        c.circ(x, y, r, None, (210, 240, 250), 4)
        c.circ(x, y, r - 5, None, mezcla(BG, (210, 240, 250), 0.25), 2)
        c.circ(x - r * 0.35, y - r * 0.35, r * 0.18, (255, 255, 255))


def ola(c, y, amp, fase, c_top, c_bot, periodo=330, y_fin=1100):
    pts = [(x, y + amp * math.sin(x / periodo * 2 * math.pi + fase)) for x in range(-20, W + 40, 30)]
    c.poly_grad(pts + [(W + 20, y_fin), (-20, y_fin)], c_top, c_bot)
    c.linea(pts, mezcla(c_top, BLANCO, 0.55), 4)


def coral(c, cx, cy, tam, color):
    for a, l in [(-0.6, 0.85), (-0.28, 1.12), (0.0, 1.3), (0.3, 1.08), (0.58, 0.82)]:
        x, y = cx + math.sin(a) * tam * l, cy - math.cos(a) * tam * l
        c.linea([(cx, cy), (x, y)], color, 22)
        c.circ(x, y, 15, color)
        mx, my = lerp(cx, x, 0.55), lerp(cy, y, 0.55)
        c.linea([(mx, my), (mx + 44 * (1 if a >= 0 else -1), my - 32)], color, 15)
        c.circ(mx + 44 * (1 if a >= 0 else -1), my - 32, 11, color)
    c.elip(cx - tam * 0.5, cy - 14, cx + tam * 0.5, cy + 26, mezcla(color, (0, 0, 0), 0.35))


def bokeh(c, t):
    for i in range(16):
        r1, r2, r3 = (i * 0.618) % 1, (i * 0.755) % 1, (i * 0.57) % 1
        x = (r1 * W + 50 * math.sin(t * (0.2 + r3 * 0.3) + i)) % W
        y = (r2 * H - t * (8 + 14 * r3)) % H
        c.glow(x, y, 40 + 55 * r3, (120, 190, 230), 0.07 + 0.05 * r1)


def cabecera(c, n, titulo, t):
    c.rr_grad(60, 92, 400, 156, (40, 86, 112), (24, 56, 76), 0.9, r=32)
    c.texto(230, 124, f"pH  ·  SHORT {n}/5", 30, BLANCO, "Bold")
    for i in range(5):
        c.circ(920 + i * 28, 124, 11 if i + 1 == n else 8, AMARILLO if i + 1 == n else (56, 100, 124))
    k = ease_out(t / 0.6)
    tam = 78
    while c.ancho_texto(titulo, tam) > 960:
        tam -= 2
    c.texto(540, 240 - (1 - k) * 28, titulo, tam, BLANCO, alfa=k, sombra=True)
    c.rr_grad(540 - 70 * k, 292, 540 + 70 * k, 300, AMARILLO, (255, 150, 40), 1.0, r=4)


def pie(c, tm):
    tam, max_w = 58, 900
    palabras = tm.texto.split()
    lineas, act = [], []
    for i, p in enumerate(palabras):
        if act and c.ancho_texto(" ".join(palabras[j] for j in act + [i]), tam) > max_w:
            lineas.append(act)
            act = [i]
        else:
            act.append(i)
    lineas.append(act)
    n = len(palabras)
    fin = max(1.0, 0.62 * tm.dbeat)
    cy = 1655
    alto = len(lineas) * 76 + 58
    ancho = max(c.ancho_texto(" ".join(palabras[j] for j in ln), tam) for ln in lineas) + 100
    x0, y0 = 540 - ancho / 2, cy - alto / 2
    c.rr_grad(x0, y0, x0 + ancho, y0 + alto, (6, 20, 30), (3, 11, 18), 0.72, r=46)
    c.rect(x0, y0, x0 + ancho, y0 + alto, None, r=46, outline=(70, 118, 145), ancho=2)
    for li, ln in enumerate(lineas):
        total = c.ancho_texto(" ".join(palabras[j] for j in ln), tam)
        x = 540 - total / 2
        for j in ln:
            ti = 0.12 + j * (fin - 0.12) / n
            a = ease((tm.bt - ti) / 0.2)
            col = PALABRAS_COLOR.get(palabras[j].strip(".,:;¿?¡!").lower(), BLANCO)
            if a > 0.01:
                c.d.text((c.X(x), c.Y(y0 + 29 + li * 76 + 38 + (1 - a) * 14)), palabras[j], font=fuente("ExtraBold", tam),
                         fill=mezcla((6, 20, 30), col, a), anchor="lm")
            x += c.ancho_texto(palabras[j] + " ", tam)


# ============ barra numérica (short 1) ============
BX0, BX1, BY, BH = 90, 990, 960, 62


def px(v):
    return BX0 + (BX1 - BX0) * v / 14


def barra(c, reveal):
    if reveal <= 0:
        return
    fin = BX0 + (BX1 - BX0) * ease(reveal)
    c.sombra(540, BY + BH + 20, 470, 26, 0.5)
    for i in range(0, 900, 5):
        x = BX0 + i
        if x > fin:
            break
        c.rect(x, BY, min(x + 6, fin), BY + BH, color_escala(14 * i / 900))
    c.circ(BX0 + 2, BY + BH / 2, BH / 2 - 1, color_escala(0))
    if reveal >= 0.99:
        c.circ(BX1 - 2, BY + BH / 2, BH / 2 - 1, color_escala(14))
    c.rect(BX0, BY + 3, fin, BY + 12, mezcla((255, 255, 255), BG, 0.0), r=4) if False else None
    for v in range(15):
        if px(v) <= fin:
            c.d.text((c.X(px(v)), c.Y(BY + BH + 42)), str(v), font=fuente("ExtraBold" if v == 7 else "Bold", 38 if v == 7 else 31),
                     fill=BLANCO if v == 7 else GRIS, anchor="mm")


def zona(c, a, b, col, alfa=1.0, texto=None):
    c.rr_grad(px(a) - 4, BY - 16, px(b) + 4, BY + BH + 16, mezcla(col, (255, 255, 255), 0.0), col, 0.0, r=14)
    c.rect(px(a) - 4, BY - 14, px(b) + 4, BY + BH + 14, None, r=16, outline=mezcla(BG, col, alfa), ancho=6)
    c.glow((px(a) + px(b)) / 2, BY + BH / 2, (px(b) - px(a)) * 0.6, col, 0.22 * alfa)
    if texto:
        c.texto((px(a) + px(b)) / 2, BY + BH + 120, texto, 44, col, alfa=alfa)


def bola(c, x, y, v):
    c.sombra(x, BY + BH * 0.5 + 8, 44, 10, 0.5)
    c.glow(x, y, 80, (255, 255, 255), 0.25)
    c.circ(x, y, 38, (225, 235, 242))
    c.circ(x, y - 3, 34, (252, 254, 255))
    c.circ(x - 11, y - 14, 9, (255, 255, 255))
    c.d.text((c.X(x), c.Y(y + 2)), str(int(round(v))), font=fuente("ExtraBold", 38), fill=(20, 50, 70), anchor="mm")


def flotantes(c, x0, x1, y0, y1, t, t_ini, tipo, n=7):
    col = NARANJA if tipo == "h" else AZUL
    txt = "H⁺" if tipo == "h" else "OH⁻"
    for i in range(n):
        a = ease((t - t_ini - i * 0.12) / 0.4)
        if a <= 0.02:
            continue
        x = lerp(x0, x1, ((i * 0.618) % 1.0)) + 18 * math.sin(t * 1.4 + i)
        y = lerp(y0, y1, 0.5 + 0.5 * math.sin(t * (0.7 + 0.1 * i) + i * 2))
        r = (24 if tipo == "h" else 27) * a
        c.circ(x, y, r + 5, mezcla(col, (255, 255, 255), 0.2))
        c.circ(x, y, r, col)
        c.circ(x - r * 0.3, y - r * 0.35, r * 0.26, mezcla(col, (255, 255, 255), 0.6))
        c.d.text((c.X(x), c.Y(y + 1)), txt, font=fuente("ExtraBold", r * 0.9), fill=(255, 255, 255), anchor="mm")


# ============ ESCENAS ============
def short1(c, tm):
    t, I, D = tm.t, tm.I, tm.D
    # vaso con agua + gota → "pH"
    if t < I[3]:
        yo = ease((t - I[1] - 0.3) / 0.9) * 800
        if yo < 790:
            imp = 1.05
            ag = agit_de(t, [(imp, imp + 0.4)])
            vaso(c, 540, 1040 + yo, 380, 310, t, {"base": (110, 190, 232), "nuevo": (110, 190, 232), "prog": 0, "ex": 540,
                                                   "nivel": 0.62, "agit": ag})
            f = (t - 0.3) / 0.75
            if 0 <= f < 1:
                gota(c, 540, lerp(420, 1040 - 155 + 8, f * f) + yo, 24, (150, 210, 245))
            salpicadura(c, 540, 1040 - 155 + 8 + yo, t - imp, (150, 210, 245))
    sc = back((t - 1.0) / 0.7) if t >= 1.0 else 0
    ypH = rampa(t, 590, [(I[1], 560)], 0.9)
    tam = rampa(t, 400, [(I[1], 250)], 0.9) * clamp(sc, 0, 1.12)
    c.glow(540, ypH, 330, AMARILLO, 0.22 * clamp(sc, 0, 1))
    c.texto(540, ypH, "pH", tam, AMARILLO, sombra=True)
    if I[1] <= t < I[3]:
        c.texto(540, 700, "potencial de hidrógeno", 50, BLANCO, "Bold", alfa=ease((t - I[1] - 0.4) / 0.5) * (1 - ease((t - I[3] + 0.5) / 0.4)))
    # termómetro de acidez
    if I[2] <= t < I[3] + 0.9:
        e = ease((t - I[2]) / 0.7) * (1 - ease((t - I[3]) / 0.8))
        yy = 1000 + (1 - e) * 600
        nivel = 0.5 + 0.42 * math.sin((t - I[2]) * 1.9 - 1.57)
        col = color_escala(nivel * 14)
        c.sombra(540, yy + 190, 90, 18, 0.5)
        c.rr_grad(500, yy - 190, 580, yy + 170, (230, 245, 252), (170, 205, 222), 0.22, r=40)
        c.rect(500, yy - 190, 580, yy + 170, None, r=40, outline=VIDRIO, ancho=6)
        c.glow(540, yy + 190, 160, col, 0.4)
        c.rect(525, lerp(yy + 150, yy - 160, nivel), 555, yy + 170, col, r=12)
        c.circ(540, yy + 195, 62, VIDRIO)
        c.circ(540, yy + 195, 52, col)
        c.circ(522, yy + 175, 12, mezcla(col, (255, 255, 255), 0.6))
        c.texto(700, yy - 150, "más básico", 36, AZUL, "Bold", alfa=e)
        c.texto(700, yy + 120, "más ácido", 36, NARANJA, "Bold", alfa=e)
    # recta numérica
    if t >= I[3]:
        rev = clamp((t - I[3]) / 2.0)
        barra(c, rev)
        bt4 = t - I[4]
        if I[5] <= t:
            zs = {5: (0, 7, NARANJA, "ÁCIDO · menor a 7"), 6: (7, 14, AZUL, "BÁSICO · mayor a 7"),
                  7: (6.2, 7.8, VERDE, "NEUTRO · 7")}
            zk = tm.beat if tm.beat in zs else (7 if tm.beat == 8 else None)
            if zk:
                a, b, col, txt = zs[zk]
                zona(c, a, b, col, 0.65 + 0.35 * math.sin(t * 5), txt)
        ev = [(I[4] + 0.1, 0), (I[4] + 1.0, 7), (I[4] + 2.0, 14), (I[5] + 0.05, 3), (I[6] + 0.05, 11), (I[7] + 0.05, 7)]
        v = 14 * ease(rev) if t < I[3] + 2.0 else None
        if v is None:
            v, prev, ts_last = 14, 14, I[3] + 2.0
            for ts, val in ev:
                if t < ts:
                    break
                v = lerp(prev, val, ease((t - ts) / 0.95))
                hop_p = clamp((t - ts) / 0.95)
                prev, ts_last = val, ts
            hop = 100 * math.sin(math.pi * clamp((t - ts_last) / 0.95)) if ts_last > I[3] + 2.0 else 0
        else:
            hop = 55 * abs(math.sin((t - I[3]) * 6))
        bola(c, px(v), BY - 52 - hop, v)
        if tm.beat == 5:
            flotantes(c, px(0.7), px(6.3), 740, 880, t, I[5] + 0.2, "h", 8)
        if tm.beat == 6:
            flotantes(c, px(7.7), px(13.3), 740, 880, t, I[6] + 0.2, "oh", 7)
        if tm.beat == 7:
            flotantes(c, px(6.0), px(8.0), 790, 880, t, I[7] + 0.2, "h", 2)
            flotantes(c, px(6.4), px(7.6), 790, 880, t, I[7] + 0.3, "oh", 2)
        if tm.beat == 4:
            if t > I[4] + 1.0:
                cartel(c, 1180, "0 a 7", GRIS, t - I[4] - 1.0, 54)
                x_roja(c, 540, 1180, 74, (t - I[4] - 1.5) / 0.4)
            if t > I[4] + 2.1:
                cartel(c, 1290, "0 a 14", VERDE, t - I[4] - 2.1, 60)
        if tm.beat == 8:
            ang = 0.5 + 0.5 * math.sin(t * 5)
            c.texto(540, 1210, "neutro = 7", 84, VERDE, alfa=ease((t - I[8]) / 0.5), sombra=True)
            c.circ(px(7), BY + BH / 2, 60 + 30 * ((t * 1.1) % 1), None, mezcla(BG, VERDE, 1 - ((t * 1.1) % 1)), 5)
            if t > I[8] + 1.2:
                cartel(c, 1330, "14", GRIS, t - I[8] - 1.2, 54)
                x_roja(c, 540, 1330, 52, (t - I[8] - 1.6) / 0.4)


def _flask_scene_common(c, tm, g, est, ph, k_ion=1.0):
    ys = matraz(c, g, tm.t, est)
    ions_ph(c, g, ys, tm.t, ph, k_ion)
    return ys


def short2(c, tm):
    t, I, D, b = tm.t, tm.I, tm.D, tm.beat
    yo = ease((t - I[8]) / 0.9) * 900
    g = geo(FX, FY + yo, FW, FH)
    ev = [(I[0] + 1.6, VERDE, 1.9, FX), (I[3] + 0.95, AMARILLO, 1.8, FX - 50), (I[4] + 0.95, VERDE, 1.8, FX),
          (I[5] + 0.95, AZUL, 1.8, FX + 50), (I[6] + 0.3, VERDE, 2.8, FX), (I[7] + 0.4, AMARILLO, 0.8, FX),
          (I[7] + 1.5, VERDE, 0.8, FX), (I[7] + 2.6, AZUL, 0.8, FX)]
    nivel = rampa(t, 0.42, [(I[0] + 1.6, 0.5), (I[3] + 1.0, 0.56), (I[4] + 1.0, 0.6), (I[5] + 1.0, 0.65)], 1.0)
    ph = muelle(t, 7, [(I[3] + 1.4, 3), (I[4] + 1.4, 7), (I[5] + 1.4, 11), (I[6] + 0.8, 7), (I[7] + 0.7, 5.2),
                       (I[7] + 1.8, 7), (I[7] + 2.9, 9)])
    ag = agit_de(t, [(I[0] + 1.6, I[0] + 2.0), (I[3] + 0.7, I[3] + 1.8), (I[4] + 0.7, I[4] + 1.8),
                     (I[5] + 0.7, I[5] + 1.8)])
    if yo < 850:
        est = estado(t, AGUA, ev, nivel, ag)
        ys = matraz(c, g, t, est)
        ions_ph(c, g, ys, t, ph, ease((t - I[1]) / 1.0))
        gotero(c, t, I[0] + 0.3, AZUL, g, ys, 2)
        ent = ease((t - I[2]) / 0.8)
        acid_rest, base_rest = (165 - (1 - ent) * 300, 650), (915 + (1 - ent) * 300, 650)
        if t >= I[2]:
            botella_vertiendo(c, t, "acido", acid_rest, [(I[3], D[3], 15), (I[4], D[4], 9)], g, ys, +1, (240, 120, 110))
            botella_vertiendo(c, t, "base", base_rest, [(I[4], D[4], 9), (I[5], D[5], 15)], g, ys, -1, (110, 150, 245))
    if b in (0, 1):
        cartel(c, 420, "azul de bromotimol", AZUL, t - 0.3 if b == 0 else 1.0, 40, 300)
    if b == 1:
        cartel(c, 500, "indicador ácido-base", BLANCO, t - I[1] - 0.2, 36, 790)
    if b == 3:
        cartel(c, 352, "ÁCIDO  →  amarillo", AMARILLO, t - I[3] - 0.9, 48)
    if b == 4:
        cartel(c, 352, "NEUTRO  →  verde", VERDE, t - I[4] - 0.9, 48)
    if b == 5:
        cartel(c, 352, "BÁSICO  →  azul", AZUL, t - I[5] - 0.9, 48)
    if b == 6:
        cartel(c, 352, "verde = neutro", VERDE, t - I[6] - 0.3, 48)
    if b == 7:
        cartel(c, 352, "no es incoloro", GRIS, t - I[7] - 0.2, 44, 290)
        x_roja(c, 290, 352, 30, (t - I[7] - 0.8) / 0.4)
        cartel(c, 352, "ni rosado", ROSA, t - I[7] - 0.4, 44, 800)
        x_roja(c, 800, 352, 30, (t - I[7] - 1.0) / 0.4)
    if b == 8:
        for i, (col, nom) in enumerate([(AMARILLO, "ácido"), (VERDE, "neutro"), (AZUL, "básico")]):
            e = ease((t - I[8] - 0.15 * i) / 0.8)
            x = 210 + i * 330
            niv = rampa(t, 0.0, [(I[8] + 0.6 + 0.25 * i, 0.75)], 1.2)
            est = {"base": col, "nuevo": col, "prog": 0, "ex": x, "nivel": niv, "agit": 0}
            tubo(c, x, 790 + (1 - e) * 500, 130, 400, t, est)
            c.texto(x, 1050 + (1 - e) * 500, nom, 46, col, alfa=e, sombra=True)
    dial(c, ph, t, (6, 7.6) if b == 7 else None, "viraje 6 – 7,6" if b == 7 else None)


def short3(c, tm):
    t, I, D, b = tm.t, tm.I, tm.D, tm.beat
    g = geo(FX, FY, FW, FH)
    JUGO, TINTE_V = (238, 232, 176), (226, 192, 142)
    ev = [(I[1] + 1.3, JUGO, 1.8, FX), (I[3] + 1.4, AMARILLO, 1.8, FX), (I[4] + 0.2, AGUA, 1.6, FX),
          (I[4] + 2.35, TINTE_V, 1.6, FX - 50), (I[6] + 1.4, AMARILLO, 1.8, FX)]
    nivel = rampa(t, 0.42, [(I[1] + 1.3, 0.52), (I[4] + 2.2, 0.58), (I[3] + 1.4, 0.55)], 1.0) if False else \
        rampa(t, 0.42, [(I[1] + 1.3, 0.52), (I[4] + 2.2, 0.60)], 1.2)
    ph = muelle(t, 7, [(I[1] + 1.6, 2), (I[4] + 0.4, 7), (I[4] + 2.7, 2.5)])
    ag = agit_de(t, [(I[1] + 1.0, I[2] + D[2] * 0.7), (I[3] + 1.3, I[3] + 2.2), (I[4] + 2.2, I[5] + 2.0),
                     (I[6] + 1.3, I[6] + 2.2)])
    est = estado(t, AGUA, ev, nivel, ag)
    ys = matraz(c, g, t, est)
    ions_ph(c, g, ys, t, ph, ease((t - I[1] - 1.0) / 1.0))
    # limón
    ent = ease((t - 0.0) / 0.7)
    lim_rest = (250, 480)
    lim_alfa = 0.45 if I[4] <= t < I[7] else 1.0
    if t < I[1]:
        c.pegar(sprite_limon(False), lim_rest[0], lim_rest[1], sx=0.74 * clamp(back(t / 0.7), 0, 1.1),
                sy=0.74 * clamp(back(t / 0.7), 0, 1.1))
    elif t < I[8]:
        limon_exprimido(c, t, I[1] + 0.1, I[2] + D[2] * 0.7, lim_rest, g, ys, lim_alfa)
    else:
        limon_exprimido(c, t, 1e9, 1e9, (250, 520), g, ys, 1.0, cara=True)
    # vinagre
    vin_rest = (905, 650)
    if t < 0.7:
        k = clamp(back(t / 0.7), 0, 1.1)
        c.pegar(sprite_botella("vinagre"), *vin_rest, sx=k, sy=k)
    else:
        botella_vertiendo(c, t, "vinagre", vin_rest, [(I[4] + 1.4, 2.6, 15)], g, ys, -1, (225, 175, 110))
    gotero(c, t, I[3] + 0.1, AZUL, g, ys, 2)
    gotero(c, t, I[6] + 0.1, AZUL, g, ys, 2)
    if b == 2:
        cartel(c, 352, "ácido cítrico", AMARILLO, t - I[2] - 0.2, 50)
    if b == 3:
        cartel(c, 352, "amarillo  ·  NO verde", AMARILLO, t - I[3] - 1.4, 48)
    if b == 5:
        cartel(c, 352, "ácido acético", NARANJA, t - I[5] - 0.2, 50)
    if b == 6:
        cartel(c, 352, "amarillo  ·  NO rosado", AMARILLO, t - I[6] - 1.4, 48)
    if b == 7:
        cartel(c, 352, "amarillo = ácido  ·  pH < 7", AMARILLO, t - I[7] - 0.1, 46)
    if b == 8:
        cartel(c, 352, "¡ácido!", NARANJA, t - I[8] - 0.2, 60)
    dial(c, ph, t, (0, 7) if b == 7 else None, "limón ≈ 2  ·  vinagre ≈ 2,5" if b >= 4 and b < 7 else (
        "limón ≈ 2" if 1 <= b < 4 else None))


def short4(c, tm):
    t, I, D, b = tm.t, tm.I, tm.D, tm.beat
    yo = ease((t - I[6]) / 0.9) * 900
    g = geo(FX, FY + yo, FW, FH)
    DET, SODA = (140, 224, 230), (236, 242, 248)
    ev = [(I[1] + 1.05, DET, 1.8, FX - 55), (I[2] + 1.4, AZUL, 1.8, FX), (I[4] + 0.2, AGUA, 1.6, FX),
          (I[4] + 2.15, SODA, 1.6, FX - 55), (I[5] + 1.4, AZUL, 1.8, FX)]
    nivel = rampa(t, 0.42, [(I[1] + 1.0, 0.54), (I[4] + 2.1, 0.58)], 1.4)
    ph = muelle(t, 7, [(I[1] + 1.5, 10.5), (I[4] + 0.4, 7), (I[4] + 2.6, 14)])
    ag = agit_de(t, [(I[1] + 0.8, I[1] + 2.0), (I[2] + 1.4, I[2] + 2.2), (I[4] + 1.9, I[4] + 3.0), (I[5] + 1.4, I[5] + 2.2)])
    det_rest, soda_rest = (165, 650), (915, 650)
    if yo < 850:
        est = estado(t, AGUA, ev, nivel, ag)
        ys = matraz(c, g, t, est)
        ions_ph(c, g, ys, t, ph, ease((t - I[1] - 1.0) / 1.0))
        if t < 0.7:
            k = clamp(back(t / 0.7), 0, 1.1)
            c.pegar(sprite_botella("detergente"), *det_rest, sx=k, sy=k)
            c.pegar(sprite_botella("soda"), *soda_rest, sx=k, sy=k)
        else:
            botella_vertiendo(c, t, "detergente", det_rest, [(I[1] + 0.1, 2.8, 15)], g, ys, +1, (130, 220, 228),
                              alfa=0.55 if t >= I[4] else 1.0)
            botella_vertiendo(c, t, "soda", soda_rest, [(I[4] + 1.2, 2.8, 11)], g, ys, -1, (240, 245, 250))
        gotero(c, t, I[2] + 0.1, AZUL, g, ys, 2)
        gotero(c, t, I[5] + 0.2, AZUL, g, ys, 2)
        if b == 3:
            burbujas_jabon(c, FX - 80, FX + 80, g.top - 10, 400, t, I[3])
        if b == 5:
            k = 0.5 + 0.5 * math.sin(t * 6)
            hz = ease((t - I[5]) / 0.5)
            c.glow(870, 470, 150 * hz, AMARILLO, 0.3 + 0.2 * k)
            c.poly([(870, 400), (870 - 80 * hz, 400 + 138 * hz), (870 + 80 * hz, 400 + 138 * hz)], AMARILLO)
            c.poly([(870, 420), (870 - 62 * hz, 420 + 108 * hz), (870 + 62 * hz, 420 + 108 * hz)], (255, 218, 110))
            if hz > 0.7:
                c.texto(870, 494, "!", 74, (120, 70, 0))
    if b == 1:
        cartel(c, 352, "detergente  ·  pH 10 a 11", (130, 220, 228), t - I[1] - 0.3, 44)
    if b == 2:
        cartel(c, 352, "azul", AZUL, t - I[2] - 1.4, 50, 300)
        cartel(c, 352, "no rosado", ROSA, t - I[2] - 1.5, 44, 770)
        x_roja(c, 770, 352, 28, (t - I[2] - 2.0) / 0.4)
    if b == 3:
        cartel(c, 352, "resbaloso = base", (130, 220, 228), t - I[3] - 0.2, 46)
    if b == 4:
        cartel(c, 352, "soda cáustica  ·  pH 14", BLANCO, t - I[4] - 1.0, 46)
    if b == 5:
        cartel(c, 352, "base muy fuerte", AZUL, t - I[5] - 0.1, 48, 400)
    if b >= 6:
        e = ease((t - I[6] - 0.2) / 0.9)
        ent = (1 - e) * 600
        ev1 = [(I[6] + 1.4, VERDE, 1.2, 340), (I[6] + 2.8, AZUL, 1.2, 340)]
        est1 = estado(t, AMARILLO, ev1, 0.72)
        tubo(c, 330, 750 + ent, 130, 390, t, est1)
        c.texto(330, 985 + ent, "azul de", 38, BLANCO, "Bold", alfa=e)
        c.texto(330, 1027 + ent, "bromotimol", 38, BLANCO, "Bold", alfa=e)
        if b == 6:
            cartel(c, 352, "no es incoloro", GRIS, t - I[6] - 0.5, 44, 330)
            x_roja(c, 330, 352, 28, (t - I[6] - 1.0) / 0.4)
        if b >= 7:
            e2 = ease((t - I[7]) / 0.8)
            ev2 = [(I[7] + 1.0, ROSA, 1.6, 750)]
            est2 = estado(t, (212, 234, 242), ev2, 0.72)
            tubo(c, 750, 750 + (1 - e2) * 600, 130, 390, t, est2)
            c.texto(750, 985 + (1 - e2) * 600, "fenolftaleína", 38, ROSA, "Bold", alfa=e2)
            c.texto(750, 1030 + (1 - e2) * 600, "incoloro → rosado", 30, GRIS, "Bold", alfa=e2)
        if b == 8:
            cartel(c, 352, "azul = base  ·  pH > 7", AZUL, t - I[8] - 0.1, 50)
    dial(c, ph, t, (7, 14) if b == 8 else None,
         "detergente ≈ 10 – 11" if b in (1, 2, 3) else ("soda cáustica = 14" if 4 <= b <= 5 else None))


def short5(c, tm):
    t, I, D, b = tm.t, tm.I, tm.D, tm.beat
    for i, (y, a, f, ct, cb) in enumerate([(930, 16, 1.4, (30, 108, 150), (14, 60, 92)), (962, 12, 1.1, (22, 88, 128),
                                                                                     (10, 46, 76))]):
        ola(c, y, a, t * f + i * 2, ct, cb, y_fin=1085)
    yo = ease((t - I[8]) / 0.8) * 800
    gl, gr = geo(300, 770 + yo, 310, 400), geo(780, 770 + yo, 310, 400)
    MAR = (66, 140, 172)
    evl = [(I[1] + 1.8, VERDE, 1.8, 300)]
    evr = [(I[5] + 1.5, AZUL, 1.8, 780)]
    nl = rampa(t, 0.0, [(I[1], 0.56)], 1.3)
    nr = rampa(t, 0.0, [(I[2], 0.56)], 1.3)
    ph = muelle(t, 0, [(I[1] + 0.2, 7), (I[2] + 1.0, 8.5), (I[6] + 1.0, 8.2), (I[8] + 0.3, 3), (I[8] + 1.5, 7), (I[8] + 2.7, 11)])
    if b == 0:
        c.glow(540, 560, 260, AMARILLO, 0.2)
        c.texto(540, 560 + 14 * math.sin(t * 2), "?", 400 * clamp(back(t / 0.8), 0, 1.1), AMARILLO, sombra=True)
    if yo < 780:
        if t >= I[1]:
            e = clamp(back((t - I[1]) / 0.7), 0, 1.06)
            if e > 0.05:
                g1 = geo(300, 770 + yo, 310 * e, 400 * e)
                est = estado(t, AGUA, evl, nl, agit_de(t, [(I[1] + 1.8, I[1] + 2.4)]))
                ys = matraz(c, g1, t, est)
                ions_ph(c, g1, ys, t, 7, ease((t - I[1] - 2.4) / 1.0))
                gotero(c, t, I[1] + 0.5, AZUL, g1, ys, 2)
                c.texto(300, 1010 + yo, "agua pura · pH 7", 36, VERDE, alfa=ease((t - I[1] - 0.5) / 0.5), sombra=True)
        if t >= I[2]:
            e = clamp(back((t - I[2]) / 0.7), 0, 1.06)
            if e > 0.05:
                g2 = geo(780, 770 + yo, 310 * e, 400 * e)
                est = estado(t, MAR, evr, nr, agit_de(t, [(I[5] + 1.5, I[5] + 2.2)]))
                ys = matraz(c, g2, t, est)
                ions_ph(c, g2, ys, t, 8.5 if t < I[6] + 1 else 8.2, ease((t - I[2] - 1.2) / 1.0))
                if b == 6 and t > I[6] + 1.2:
                    iones(c, g2, ys, t, 3 * ease((t - I[6] - 1.2) / 1.5), "h", 0.2)
                gotero(c, t, I[5] + 0.2, AZUL, g2, ys, 2)
                c.texto(780, 1010 + yo, "agua de mar · pH 8,5", 36, AZUL, alfa=ease((t - I[2] - 0.8) / 0.5), sombra=True)
                if b == 4:
                    for i in range(16):
                        tk = I[4] + 0.2 + 0.17 * i
                        f = (t - tk) / 0.55
                        x = 780 + 36 * math.sin(i * 2.3)
                        if 0 <= f < 1:
                            y = lerp(g2.top - 40, ys, f * f)
                            c.rect(x - 7, y - 7, x + 7, y + 7, (250, 250, 252), r=2)
                        elif 1 <= f < 1.5:
                            salpicadura(c, x, ys, (f - 1) * 0.55, (240, 244, 250))
                if b == 6:
                    for i in range(7):
                        tk = I[6] + 0.15 + 0.4 * i
                        f = (t - tk) / 0.9
                        x = 780 + 44 * math.sin(i * 1.9)
                        if 0 <= f < 1:
                            y = lerp(g2.top - 230, ys, f * f * 0.9 + 0.1 * f)
                            c.circ(x, y, 25, mezcla(BG, (210, 225, 235), 0.28), (200, 220, 232), 3)
                            c.d.text((c.X(x), c.Y(y + 1)), "CO₂", font=fuente("ExtraBold", 21), fill=(235, 245, 250), anchor="mm")
                        elif 1 <= f < 1.4:
                            salpicadura(c, x, ys, (f - 1) * 0.8, (210, 225, 235))
    if b == 3:
        cartel(c, 352, "mayor a 7  →  básica", AZUL, t - I[3] - 0.2, 48)
    if b == 4:
        cartel(c, 352, "sales disueltas", BLANCO, t - I[4] - 0.2, 48)
    if b == 5:
        cartel(c, 352, "azul · pasó el 7,6", AZUL, t - I[5] - 1.5, 48)
    if b == 6:
        cartel(c, 352, "CO₂ disuelto  →  pH baja", NARANJA, t - I[6] - 0.2, 46)
    if b == 7:
        e = ease((t - I[7]) / 0.6)
        gris = ease((t - I[7] - 0.5) / 2.0)
        coral(c, 540, 540, 100 * (1 - 0.18 * gris) * e, mezcla(ROSA, (140, 146, 150), gris))
        c.texto(540, 640, "corales y conchas", 40, BLANCO, "Bold", alfa=e, sombra=True)
    if b == 8:
        for i, (txt, sub, col) in enumerate([("menor a 7", "ÁCIDO", NARANJA), ("igual a 7", "NEUTRO", VERDE), ("mayor a 7", "BÁSICO", AZUL)]):
            k = back((t - I[8] - 0.3 - 1.2 * i) / 0.5)
            y = 470 + i * 215
            if k > 0.02:
                kk = clamp(k, 0, 1.06)
                c.sombra(540, y + 90, 400, 28, 0.5)
                c.rr_grad(110, y - 85 * kk, 970, y + 85 * kk, mezcla(BG, col, 0.42), mezcla(BG, col, 0.16), 0.97, r=44)
                c.rect(110, y - 85 * kk, 970, y + 85 * kk, None, r=44, outline=col, ancho=4)
                if k > 0.7:
                    c.texto(290, y, sub, 54, col)
                    c.texto(740, y, txt, 54, BLANCO, "Bold")
    if t >= I[1]:
        dial(c, ph, t, (7, 14) if b == 3 else None)


ESCENAS = {1: short1, 2: short2, 3: short3, 4: short4, 5: short5}


def fotograma(n, t):
    cr = cronograma(n)
    ini = cr["ini"]
    beat = max(i for i, s in enumerate(ini) if s <= t)
    tm = SimpleNamespace(t=t, I=ini, D=cr["dur"], beat=beat, bt=t - ini[beat], dbeat=cr["dur"][beat],
                         texto=cr["textos"][beat])
    c = Lienzo()
    bokeh(c, t)
    cabecera(c, n, cr["titulo"], t)
    ESCENAS[n](c, tm)
    if n == 5 and t < ini[1]:
        pass
    pie(c, tm)
    c.rect(0, 1890, W * clamp(t / cr["total"]), 1900, AMARILLO)
    return c.final()
