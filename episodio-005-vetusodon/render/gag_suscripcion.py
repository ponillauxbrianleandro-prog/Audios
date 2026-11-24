#!/usr/bin/env python3
"""Animación FINAL de la mascota: gag de suscripción (≈18 s, 1920x1080, 24 fps) -> MP4 con sonido y WebM con transparencia.

Botón «SUSCRIBIRSE» y campanita a la IZQUIERDA. La mascota entra desde la derecha caminando hacia la izquierda (el cuerpo sube, baja,
se balancea y cabecea en la dirección de marcha), salta, cae de espaldas girando sobre su eje largo y se golpea con el botón
(rojo -> gris, sonido de suscripción). Se le cae una hoja de su propio cuerpo (del tamaño de las hojas del libro) que cae en la
campanita y la activa; se endereza, se enoja, le ladra y se va caminando (vista espejada).

  python3 gag_suscripcion.py SALIDA.mp4 [--frames A:B] [--alpha]
"""
import math
import subprocess
import sys
import wave
from functools import lru_cache
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import signal

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mascota as MA

W, H, FPS = 1920, 1080, 24
DUR = 18.2
GROUND = 905
SC = 0.70
CROP = (200, 330, 1400, 1130)
FOOT_CANVAS_Y = 1075 - CROP[1]                     # y de los pies dentro del recorte
BTN = (300, 742, 840, 882)
BELL = (150, 800)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
T_WALK0, T_WALK1 = 0.4, 5.6
X_WALK0, X_STOP = 2340.0, 1440.0
T_JUMP0, T_JUMP1 = 6.6, 7.5
X_LAND = 1170.0
T_HIT = 7.55
T_UP0, T_UP1 = 10.2, 11.2
T_LEAF0, T_LEAF1 = 9.4, 11.8
BARKS = (11.9, 12.55, 13.2)
T_LEAVE0, T_LEAVE1 = 13.9, 17.9
CICLO = 0.70                                        # segundos por ciclo de caminata


def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def seg(t, a, b):
    return max(0.0, min(1.0, (t - a) / (b - a)))


# ------------------------------------------------------------------------------------------ fondo, botón, campana
def fondo():
    import cv2
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = np.clip(yy / 860, 0, 1)[..., None]
    img = np.array([34, 58, 74.]) * (1 - t) + np.array([14, 30, 44.]) * t
    glow = np.exp(-(((xx - 640) / 760) ** 2 + ((yy - 560) / 420) ** 2))[..., None]
    img = img + glow * np.array([70, 48, 26.])
    piso = (yy > GROUND - 40)[..., None]
    d = np.clip((yy - (GROUND - 40)) / (H - GROUND + 40), 0, 1)[..., None]
    img = np.where(piso, np.array([58, 38, 34.]) * (1 - d * 0.55) + glow * np.array([36, 18, 8.]), img)
    for k in range(-14, 15):
        cv2.line(img, (960 + k * 150, GROUND - 40), (960 + k * 420, H), (30, 18, 18), 2, cv2.LINE_AA)
    cv2.line(img, (0, GROUND - 40), (W, GROUND - 40), (24, 14, 14), 4, cv2.LINE_AA)
    img += (np.random.RandomState(3).rand(H, W, 1).astype(np.float32) - 0.5) * 7
    v = np.clip(1 - (((xx - W / 2) / 1250) ** 2 + ((yy - H / 2) / 800) ** 2), 0, 1)[..., None] ** 0.6
    return np.clip(img * (0.55 + 0.45 * v), 0, 255).astype(np.uint8)


def boton(estado, presion):
    x0, y0, x1, y1 = BTN
    w, h = x1 - x0, y1 - y0
    L = Image.new("RGBA", (w + 80, h + 90), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    dy = int(14 * presion)
    sh = Image.new("RGBA", L.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([40, 56 - dy // 2, 40 + w, 56 + h - dy // 2 + 6], 36, fill=(0, 0, 0, 120))
    L.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    base, lite, dark = ((205, 24, 30), (246, 86, 78), (110, 8, 14)) if estado == 0 else ((104, 108, 116), (150, 154, 162), (52, 54, 60))
    d.rounded_rectangle([40, 40 + dy, 40 + w, 40 + h + dy - 16 * (1 - presion)], 36, fill=dark, outline=(24, 14, 14), width=5)
    d.rounded_rectangle([40, 30 + dy, 40 + w, 30 + h + dy - 14], 36, fill=base, outline=(24, 14, 14), width=5)
    d.rounded_rectangle([54, 40 + dy, 40 + w - 14, 40 + dy + h // 3], 28, fill=lite + (120,))
    f = ImageFont.truetype(FONT, 56)
    txt = "SUSCRIBIRSE" if estado == 0 else "SUSCRITO"
    tw = d.textlength(txt, font=f)
    d.text((40 + (w - tw) / 2 + 2, 30 + dy + (h - 14) / 2 - 26 + 3), txt, font=f, fill=(0, 0, 0, 90))
    d.text((40 + (w - tw) / 2, 30 + dy + (h - 14) / 2 - 26), txt, font=f, fill=(255, 255, 255, 255))
    return L, (x0 - 40, y0 - 30)


def campana(ang, activa):
    S = 260
    L = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    cx = S // 2
    col, lite, dark = ((226, 184, 54), (255, 234, 140), (130, 92, 20)) if activa else ((118, 122, 132), (170, 174, 184), (60, 62, 70))
    pts = [(cx - 20, 34), (cx + 20, 34), (cx + 34, 70), (cx + 52, 128), (cx + 78, 170), (cx + 78, 188), (cx - 78, 188), (cx - 78, 170), (cx - 52, 128), (cx - 34, 70)]
    d.line([(cx, 12), (cx, 36)], fill=(24, 14, 14), width=10)
    d.polygon(pts, fill=col)
    d.line(pts + [pts[0]], fill=(24, 14, 14), width=6, joint="curve")
    d.polygon([(cx - 14, 50), (cx - 30, 74), (cx - 44, 130), (cx - 66, 170), (cx - 40, 170), (cx - 26, 130), (cx - 14, 74)], fill=lite)
    d.ellipse([cx - 22, 182, cx + 22, 214], fill=dark, outline=(24, 14, 14), width=5)
    return L.rotate(ang, resample=Image.BICUBIC, center=(cx, 14))


# ------------------------------------------------------------------------------------------ guion de movimiento
def estado(t):
    s = dict(x=3000.0, dy=0.0, pose={}, flipx=False, boton=0, presion=0.0, campana=(0.0, False, 0.0), hoja=None, guau=0.0, roll=None)
    if t < T_WALK1:                                          # camina hacia la izquierda
        k = seg(t, T_WALK0, T_WALK1)
        s["x"] = X_WALK0 + (X_STOP - X_WALK0) * (0.88 * k + 0.12 * ease(k))
        if t >= T_WALK0:
            fin = ease(seg(t, T_WALK1 - 0.6, T_WALK1))
            s["pose"] = dict(leg=((t - T_WALK0) / CICLO) % 1.0, look=(-0.9, 0.0))
    elif t < T_JUMP0:                                        # se frena, mira el botón y se agacha
        s["x"] = X_STOP
        k = seg(t, T_WALK1, T_JUMP0)
        s["pose"] = dict(look=(-1, -0.2), squash=1 - 0.12 * math.sin(math.pi * seg(t, 6.15, T_JUMP0)), tilt=-2 * k + 4 * seg(t, 6.15, T_JUMP0))
    elif t < T_JUMP1:                                        # salta hacia la izquierda
        k = seg(t, T_JUMP0, T_JUMP1)
        s["x"] = X_STOP + (X_LAND - X_STOP) * ease(k)
        s["dy"] = -250 * 4 * k * (1 - k)
        s["pose"] = dict(spread=1.0, tilt=5 - 16 * k, look=(-1, -1))
    elif t < T_UP0:                                          # cae de espaldas: gira sobre su eje largo y queda patas arriba
        s["x"] = X_LAND
        if t < T_HIT:
            k = seg(t, T_JUMP1, T_HIT)
            s["roll"] = (0, k)
            s["pose"] = dict(spread=1.0, tilt=-10)
        else:
            rebote = max(0.0, math.exp(-(t - T_HIT) * 5) * math.sin((t - T_HIT) * 18))
            s["dy"] = -46 * rebote
            s["roll"] = (1, 1.0)
            s["pose"] = dict(flip=True, spread=1.0, leg=((t - 7.9) / 0.5) % 1.0, blink=0.5 if int(t * 4) % 6 == 0 else 0, auto=False, tilt=2.5 * math.sin(t * 9))
    elif t < T_UP1:                                          # se endereza girando de vuelta
        s["x"] = X_LAND
        k = seg(t, T_UP0, T_UP1)
        s["roll"] = (1, 1.0 - k) if k < 0.5 else (0, (k - 0.5) * 2)
        s["roll"] = ("up", k)
        s["pose"] = dict(spread=1.0 - k, tilt=-3 * math.sin(k * math.pi))
    elif t < T_LEAVE0:                                       # enojada: tiembla y ladra
        s["x"] = X_LAND
        lad = 0.0
        for tb in BARKS:
            if 0 <= t - tb < 0.28:
                lad = math.sin((t - tb) / 0.28 * math.pi)
        s["guau"] = lad
        s["pose"] = dict(mad=1, tilt=1.2 * math.sin(t * 60) + 4 * lad, bob=-26 * lad, squash=1 + 0.05 * lad, look=(-1, 0))
    else:                                                    # se va hacia la derecha (vista espejada)
        k = seg(t, T_LEAVE0, T_LEAVE1)
        s["x"] = X_LAND + (2500 - X_LAND) * (0.1 * ease(k) + 0.9 * k)
        s["flipx"] = True
        s["pose"] = dict(leg=((t - T_LEAVE0) / CICLO) % 1.0, mad=1 if t < T_LEAVE0 + 0.7 else 0, look=(-1, 0))
    if t >= T_HIT:
        s["boton"] = 1
        s["presion"] = ease(seg(t, T_HIT - 0.05, T_HIT + 0.05)) * (1 - ease(seg(t, T_HIT + 0.08, T_HIT + 0.35)))
    if t >= T_LEAF0:                                         # la hoja sale del cuerpo y va hasta la campana
        k = seg(t, T_LEAF0, T_LEAF1)
        x0, y0 = X_LAND - 60, 560
        xb, yb = BELL[0] + 4, BELL[1] - 150
        x = x0 + (xb - x0) * ease(k) + 70 * math.sin(k * 7.5) * (1 - k)
        y = y0 + (yb - y0) * (k ** 1.6) + 36 * math.sin(k * 11) * (1 - k) - 120 * math.sin(math.pi * min(1, k * 1.6)) * (1 - k)
        s["hoja"] = (x, y, 50 * math.sin(k * 8) + 30 * k, abs(math.cos(k * 9.0)) * 0.7 + 0.3, k)
        if t >= T_LEAF1 + 0.25:                              # después de activar la campana, la hoja resbala y queda en el piso
            q = ease(seg(t, T_LEAF1 + 0.25, T_LEAF1 + 1.0))
            s["hoja"] = (xb + 215 * q, yb + (GROUND - 40 - yb) * q, 30 + 40 * q, 0.7 + 0.3 * q, 1.0)
    if t >= T_LEAF1:
        u = t - T_LEAF1
        s["campana"] = (22 * math.exp(-u * 1.7) * math.sin(u * 14), True, min(1.0, u * 3) * math.exp(-max(0, u - 1.2) * 0.6))
    return s


# ------------------------------------------------------------------------------------------ render
_M = _BG = _HOJA = None


def _init():
    global _M, _BG, _HOJA
    _M = MA.Mascota()
    _M.frame({}); _M.frame({"flip": True})
    _BG = Image.fromarray(fondo(), "RGB").convert("RGBA")
    _HOJA = MA.hoja_grande(330, 440)


def _key(pose):
    q = {}
    for k, v in pose.items():
        if k == "look":
            q[k] = (round(v[0], 1), round(v[1], 1))
        elif k == "leg":
            q[k] = round(v * 24) / 24 % 1.0
        elif k in ("tilt", "bob", "sway", "lag"):
            q[k] = round(v)
        elif isinstance(v, float):
            q[k] = round(v, 2)
        else:
            q[k] = v
    return tuple(sorted(q.items()))


@lru_cache(maxsize=400)
def _sprite(pose_key, flipx):
    img = _M.frame(dict(pose_key)).crop(CROP)
    img = img.resize((int(img.width * SC), int(img.height * SC)), Image.LANCZOS)
    return img.transpose(Image.FLIP_LEFT_RIGHT) if flipx else img


def frame(i, transparente=False):
    t = i / FPS
    s = estado(t)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)) if transparente else _BG.copy()
    bl, pos = boton(s["boton"], s["presion"])
    img.alpha_composite(bl, (int(pos[0]), int(pos[1])))
    ang, act, br = s["campana"]
    if br > 0.02:
        glow = Image.new("RGBA", (520, 520), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([60, 60, 460, 460], fill=(255, 214, 90, int(120 * br)))
        img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40)), (BELL[0] - 260, BELL[1] - 250))
        d = ImageDraw.Draw(img)
        for r_ in (120, 170):
            d.arc([BELL[0] - r_, BELL[1] - r_ + 20, BELL[0] + r_, BELL[1] + r_ + 20], -50, 50, fill=(255, 226, 120, int(200 * br)), width=6)
            d.arc([BELL[0] - r_, BELL[1] - r_ + 20, BELL[0] + r_, BELL[1] + r_ + 20], 130, 230, fill=(255, 226, 120, int(200 * br)), width=6)
    img.alpha_composite(campana(ang, act), (BELL[0] - 130, BELL[1] - 190))
    # mascota (con giro sobre el eje largo: aplastado vertical al pasar de pie a patas arriba)
    pose = dict(s["pose"])
    roll = s["roll"]
    sqy = 1.0
    if roll is not None:
        a, k = roll
        if a == 0:                                 # de pie -> de canto
            pose["flip"] = False; sqy = max(0.38, math.cos(k * math.pi / 2))
        elif a == 1:                               # de canto -> patas arriba
            pose["flip"] = True; sqy = 1.0
        else:                                      # "up": patas arriba -> de pie
            kk = k
            if kk < 0.5:
                pose["flip"] = True; sqy = max(0.38, math.cos(kk * math.pi))
            else:
                pose["flip"] = False; sqy = max(0.38, math.cos((1 - kk) * math.pi))
        if a == 0 and k >= 0.5:
            pose["flip"] = True; sqy = max(0.38, math.cos((1 - k) * math.pi))
    spr = _sprite(_key(pose), s["flipx"])
    if sqy < 0.999:
        spr = spr.resize((spr.width, max(2, int(spr.height * sqy))), Image.BILINEAR)
    base_y = GROUND + s["dy"] - (FOOT_CANVAS_Y * SC)
    oy = base_y + (FOOT_CANVAS_Y * SC) - spr.height * 0.98 if sqy < 0.999 else base_y
    ox = s["x"] - spr.width / 2
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    esc = 1 - min(0.5, abs(s["dy"]) / 700)
    ImageDraw.Draw(sh).ellipse([s["x"] - 470 * esc, GROUND - 34, s["x"] + 470 * esc, GROUND + 40], fill=(0, 0, 0, int(120 * esc)))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    img.alpha_composite(spr, (int(ox), int(oy)))
    if s["hoja"]:
        x, y, a, sx, k = s["hoja"]
        h = _HOJA.resize((max(8, int(_HOJA.width * SC * sx)), int(_HOJA.height * SC)), Image.BILINEAR).rotate(a, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(h, (int(x - h.width / 2), int(y - h.height / 2)))
    if s["guau"] > 0.05:
        d = ImageDraw.Draw(img)
        f = ImageFont.truetype(FONT, int(54 + 30 * s["guau"]))
        cx, cy = s["x"] - 330, GROUND - 640 - 40 * s["guau"]
        for a in range(-2, 3):
            ang = math.radians(250 + a * 26); r1, r2 = 110, 110 + 70 * s["guau"]
            d.line([(cx + math.cos(ang) * r1, cy + 70 + math.sin(ang) * r1), (cx + math.cos(ang) * r2, cy + 70 + math.sin(ang) * r2)], fill=(255, 236, 160, 255), width=8)
        d.text((cx - 90, cy), "¡GUAU!", font=f, fill=(255, 246, 214, 255), stroke_width=7, stroke_fill=(34, 20, 16, 255))
    return img.tobytes() if transparente else np.asarray(img.convert("RGB")).tobytes()


# ------------------------------------------------------------------------------------------ sonido en capas
SR = 44100


def _env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(t / max(a, 1e-4), 1) * np.exp(-t / d)


def _bp(x, f0, q=4.0):
    b, a = signal.iirpeak(f0 / (SR / 2), q)
    return signal.lfilter(b, a, x)


def _lp(x, fc, o=2):
    b, a = signal.butter(o, fc / (SR / 2)); return signal.lfilter(b, a, x)


def _hp(x, fc, o=2):
    b, a = signal.butter(o, fc / (SR / 2), "high"); return signal.lfilter(b, a, x)


def _reverb(x, mezcla=0.2):
    out = []
    for lado in (0, 1):
        y = np.zeros_like(x)
        for d_ms, g in ((29.7, 0.78), (37.1, 0.76), (41.1, 0.74), (43.7, 0.72)):
            d = int(SR * (d_ms + 2.3 * lado) / 1000)
            b = np.zeros(d + 1); b[0] = 1; a = np.zeros(d + 1); a[0] = 1; a[d] = -g
            y += signal.lfilter(b, a, x)
        for d_ms, g in ((5.0, 0.7), (1.7, 0.7)):
            d = int(SR * d_ms / 1000)
            b = np.zeros(d + 1); b[0] = -g; b[d] = 1; a = np.zeros(d + 1); a[0] = 1; a[d] = -g
            y = signal.lfilter(b, a, y)
        out.append(x * (1 - mezcla) + y * mezcla * 0.4)
    return np.stack(out, 1)


def audio():
    n = int(DUR * SR)
    y = np.zeros(n, np.float32)
    rng = np.random.RandomState(7)

    def add(t0, x, g=1.0):
        i = int(t0 * SR); j = min(n, i + len(x))
        if 0 <= i < n:
            y[i:j] += (x[:j - i] * g).astype(np.float32)

    def paso(g=1.0, f=110):
        m = int(SR * 0.3); t = np.arange(m) / SR
        thud = np.sin(2 * math.pi * f * t * (1 - 0.3 * t / 0.3)) * _env(m, 0.003, 0.06)
        roce = _bp(rng.randn(m), rng.uniform(1800, 3200), 1.2) * _env(m, 0.004, 0.035) * 0.6          # roce de hojas/papel
        scuff = _lp(rng.randn(m), 700) * _env(m, 0.01, 0.05) * 0.5
        return (thud * 0.9 + roce + scuff) * g
    # pasos: 4 apoyos por ciclo (marcha lateral), con variación
    for (a, b, dirc) in ((T_WALK0, T_WALK1, 1), (T_LEAVE0, T_LEAVE1, 1)):
        ncy = int((b - a) / CICLO) + 1
        for c in range(ncy):
            for k, ph in enumerate((0.0, 0.25, 0.5, 0.75)):
                tc = a + (c + ph + 0.02) * CICLO
                if tc < b - 0.4:
                    add(tc, paso(rng.uniform(0.5, 0.85) * (1 if k % 2 else 0.8), rng.uniform(90, 130)))
        for c in np.arange(a, b - 0.3, CICLO / 2):                                                     # roce continuo de páginas con el balanceo
            m = int(SR * 0.25)
            add(c, _bp(rng.randn(m), 3600, 0.8) * np.sin(np.pi * np.arange(m) / m) ** 2 * 0.07)
    m = int(SR * 0.6); t = np.arange(m) / SR                                                           # salto: impulso + whoosh
    add(T_JUMP0 - 0.05, np.sin(2 * math.pi * np.cumsum(180 + 300 * t / 0.6) / SR) * _env(m, 0.01, 0.12) * 0.35)
    add(T_JUMP0 + 0.1, _bp(rng.randn(m), 900, 0.7) * np.sin(np.pi * t / 0.6) * 0.35)
    m = int(SR * 0.5)                                                                                  # giro en el aire
    add(T_JUMP1, _hp(rng.randn(m), 1200) * np.sin(np.pi * np.arange(m) / m) ** 2 * 0.18)
    add(T_HIT, paso(2.0, 55)); add(T_HIT + 0.01, _lp(rng.randn(int(SR * 0.35)), 400) * _env(int(SR * 0.35), 0.002, 0.09) * 1.2)       # golpe seco
    for q in range(7):                                                                                 # hojas que se sacuden
        add(T_HIT + 0.06 + q * 0.045, _bp(rng.randn(int(SR * 0.08)), rng.uniform(2500, 5200), 1.0) * _env(int(SR * 0.08), 0.002, 0.03) * 0.35)
    for tw in np.arange(7.9, 9.9, 0.25):                                                               # patas pataleando en el aire
        add(tw, _bp(rng.randn(int(SR * 0.1)), 2100, 1.5) * _env(int(SR * 0.1), 0.003, 0.03) * 0.12)
    # botón: clic mecánico + notificación (dos tonos con armónicos) con reverb
    add(T_HIT + 0.03, _hp(rng.randn(int(SR * 0.03)), 3000) * _env(int(SR * 0.03), 0.0005, 0.006) * 0.8)
    m = int(SR * 1.1); t = np.arange(m) / SR
    chime = (np.sin(2 * math.pi * 660 * t) + 0.4 * np.sin(2 * math.pi * 1320 * t)) * _env(m, 0.004, 0.16) \
        + np.roll((np.sin(2 * math.pi * 990 * t) + 0.4 * np.sin(2 * math.pi * 1980 * t)) * _env(m, 0.004, 0.22), int(0.09 * SR))
    add(T_HIT + 0.1, chime, 0.42)
    m = int(SR * 2.4); t = np.arange(m) / SR                                                           # hoja: aire + roce
    add(T_LEAF0, _bp(rng.randn(m), 1400, 0.5) * np.sin(np.pi * np.minimum(t / 2.4, 1)) ** 2 * 0.07 * (0.5 + 0.5 * np.sin(t * 15)))
    add(T_LEAF1 - 0.06, _bp(rng.randn(int(SR * 0.1)), 4200, 1.2) * _env(int(SR * 0.1), 0.001, 0.025) * 0.3)
    m = int(SR * 3.5); t = np.arange(m) / SR                                                           # campanita: parciales inarmónicos
    camp = sum(np.sin(2 * math.pi * 1180 * f * t) * a * np.exp(-t / d) for f, a, d in ((1, 1.0, 1.4), (2.76, 0.55, 0.9), (5.4, 0.3, 0.5), (8.93, 0.16, 0.3)))
    camp *= 1 + 0.12 * np.sin(2 * math.pi * 5.5 * t)
    add(T_LEAF1, camp * np.minimum(t / 0.002, 1), 0.3)
    for k_, tb in enumerate(BARKS):                                                                    # ladridos: pulso glotal + formantes
        m = int(SR * 0.3); t = np.arange(m) / SR
        f0 = (410 - 190 * np.minimum(t / 0.22, 1)) * (1 + 0.07 * (k_ - 1))
        ph = np.cumsum(f0) / SR * 2 * math.pi
        src = sum(np.sin(ph * h) / h ** 0.9 for h in range(1, 14)) + rng.randn(m) * 0.08
        voz = (_bp(src, 780 - 150 * k_, 3) + 0.7 * _bp(src, 1350, 3) + 0.3 * _bp(src, 2600, 3)) * _env(m, 0.006, 0.1)
        add(tb, voz * np.minimum(1, (m - np.arange(m)) / (0.04 * SR)), 0.5)
    y += _lp(rng.randn(n), 120, 1).astype(np.float32) * 0.01                                          # tono de cuarto
    st = _reverb(y, 0.22)
    st = np.tanh(st * 1.3)
    st = st / max(1e-6, np.abs(st).max()) * 0.85
    return (st * 32767).astype(np.int16)


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "gag.mp4")
    alpha = "--alpha" in sys.argv
    rango = None
    if "--frames" in sys.argv:
        a, b = sys.argv[sys.argv.index("--frames") + 1].split(":"); rango = (int(a), int(b))
    n = int(DUR * FPS)
    idx = range(*rango) if rango else range(n)
    wav = out.with_suffix(".wav")
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(audio().tobytes())
    if alpha:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(wav),
               "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "24", "-auto-alt-ref", "0", "-c:a", "libopus", "-b:a", "160k", str(out)]
    else:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(wav),
               "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    from functools import partial
    with Pool(4, initializer=_init) as pool:
        for k, b in enumerate(pool.imap(partial(frame, transparente=alpha), idx, chunksize=2)):
            ff.stdin.write(b)
            if k % 48 == 0:
                print("cuadro", k, "/", len(idx), flush=True)
    ff.stdin.close(); ff.wait()
    wav.unlink(missing_ok=True)
    print("listo", out)


if __name__ == "__main__":
    main()
