#!/usr/bin/env python3
"""Gag de suscripción de la mascota (escena aparte, ≈17,5 s, 1920x1080, 24 fps) -> MP4 con sonido sintetizado.

Camina hacia el botón rojo, salta, cae de espaldas y se golpea con el botón (rojo -> gris, sonido de suscripción), se le cae una
hoja de su propio cuerpo que cae en la campanita y la activa; se endereza, se enoja, le ladra un poco y se va.
Animación 2D por capas con poses pre-dibujadas y cacheadas (nada de 3D): ~0,3 s por cuadro con 4 procesos.

  python3 gag_suscripcion.py SALIDA.mp4 [--frames A:B]
"""
import math
import subprocess
import sys
import wave
from functools import lru_cache
from multiprocessing import Pool
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mascota as MA

W, H, FPS = 1920, 1080, 24
DUR = 17.5
GROUND = 880                                    # y de los pies en pantalla
SC = 0.80                                       # escala del sprite (lienzo 1500 px -> pantalla)
FOOT = 1010                                     # y de los pies en el lienzo del sprite
BTN = (1170, 722, 1700, 862)                    # botón (x0,y0,x1,y1)
BELL = (1812, 790)                              # centro de la campana
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
T_JUMP0, T_JUMP1, T_HIT = 6.0, 7.0, 7.1
T_LEAF0, T_LEAF1 = 9.6, 11.6


def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def seg(t, a, b):
    return max(0.0, min(1.0, (t - a) / (b - a)))


# ------------------------------------------------------------------------------------------ fondo
def fondo():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    top, bot = np.array([34, 58, 74.]), np.array([14, 30, 44.])
    t = np.clip(yy / 860, 0, 1)[..., None]
    img = top * (1 - t) + bot * t
    glow = np.exp(-(((xx - 1250) / 760) ** 2 + ((yy - 560) / 420) ** 2))[..., None]
    img = img + glow * np.array([70, 48, 26.])
    # suelo: tablones en perspectiva
    piso = (yy > GROUND - 24)
    d = np.clip((yy - (GROUND - 24)) / (H - GROUND + 24), 0, 1)
    base = np.array([58, 38, 34.]) * (1 - d[..., None] * 0.55) + glow * np.array([36, 18, 8.])
    img = np.where(piso[..., None], base, img)
    for k in range(-14, 15):
        x0 = 960 + k * 150; x1 = 960 + k * 420
        pts = np.array([[x0, GROUND - 24], [x1, H]], np.int32)
        cv2.line(img, tuple(pts[0]), tuple(pts[1]), (30, 18, 18), 2, cv2.LINE_AA)
    cv2.line(img, (0, GROUND - 24), (W, GROUND - 24), (24, 14, 14), 4, cv2.LINE_AA)
    r = np.random.RandomState(3)
    img += (r.rand(H, W, 1).astype(np.float32) - 0.5) * 7
    v = np.clip(1 - (((xx - W / 2) / 1250) ** 2 + ((yy - H / 2) / 800) ** 2), 0, 1)[..., None] ** 0.6
    return np.clip(img * (0.55 + 0.45 * v), 0, 255).astype(np.uint8)


# ------------------------------------------------------------------------------------------ botón y campana
def boton(estado, presion):
    """estado 0 = rojo, 1 = gris (suscripto). presion 0..1."""
    x0, y0, x1, y1 = BTN
    w, h = x1 - x0, y1 - y0
    L = Image.new("RGBA", (w + 80, h + 90), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    dy = int(14 * presion)
    sh = Image.new("RGBA", L.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([40, 56 - dy // 2, 40 + w, 56 + h - dy // 2 + 6], 36, fill=(0, 0, 0, 120))
    L.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    base, lite, dark = ((205, 24, 30), (246, 86, 78), (110, 8, 14)) if estado == 0 else ((104, 108, 116), (150, 154, 162), (52, 54, 60))
    d.rounded_rectangle([40, 40 + dy, 40 + w, 40 + h + dy - 16 * (1 - presion) + 0], 36, fill=dark, outline=(24, 14, 14), width=5)       # grosor
    d.rounded_rectangle([40, 30 + dy, 40 + w, 30 + h + dy - 14], 36, fill=base, outline=(24, 14, 14), width=5)
    d.rounded_rectangle([54, 40 + dy, 40 + w - 14, 40 + dy + h // 3], 28, fill=lite + (120,))                                          # brillo
    f = ImageFont.truetype(FONT, 56)
    txt = "SUSCRIBIRSE" if estado == 0 else "SUSCRITO"
    tw = d.textlength(txt, font=f)
    d.text((40 + (w - tw) / 2 + 2, 30 + dy + (h - 14) / 2 - 26 + 3), txt, font=f, fill=(0, 0, 0, 90))
    d.text((40 + (w - tw) / 2, 30 + dy + (h - 14) / 2 - 26), txt, font=f, fill=(255, 255, 255, 255))
    return L, (x0 - 40, y0 - 30)


def campana(ang, activa, brillo):
    S = 260
    L = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    cx = S // 2
    col, lite, dark = ((226, 184, 54), (255, 234, 140), (130, 92, 20)) if activa else ((118, 122, 132), (170, 174, 184), (60, 62, 70))
    pts = [(cx - 20, 34), (cx + 20, 34), (cx + 34, 70), (cx + 52, 128), (cx + 78, 170), (cx + 78, 188), (cx - 78, 188), (cx - 78, 170), (cx - 52, 128), (cx - 34, 70)]
    d.line([(cx, 12), (cx, 36)], fill=(24, 14, 14), width=10)
    d.polygon(pts, fill=col, outline=(24, 14, 14))
    d.line(pts + [pts[0]], fill=(24, 14, 14), width=6, joint="curve")
    d.polygon([(cx - 14, 50), (cx - 30, 74), (cx - 44, 130), (cx - 66, 170), (cx - 40, 170), (cx - 26, 130), (cx - 14, 74)], fill=lite)
    d.ellipse([cx - 22, 182, cx + 22, 214], fill=dark, outline=(24, 14, 14), width=5)
    L = L.rotate(ang, resample=Image.BICUBIC, center=(cx, 14))
    return L


def hoja_sprite():
    L = Image.new("RGBA", (96, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    d.rounded_rectangle([10, 8, 82, 108], 6, fill=(244, 232, 196), outline=(34, 20, 16), width=4)
    for y in range(22, 100, 9):
        d.line([(18, y), (74, y)], fill=(170, 146, 104), width=2)
    d.polygon([(82, 108), (60, 108), (82, 86)], fill=(214, 194, 150), outline=(34, 20, 16))
    return L


# ------------------------------------------------------------------------------------------ guion de movimiento
def estado(t):
    """Devuelve dict con la posición de la mascota (centro del lienzo en pantalla), pose y objetos."""
    s = dict(x=-420.0, dy=0.0, pose={}, flipx=False, boton=0, presion=0.0, campana=(0.0, False, 0.0), hoja=None, guau=0.0, aire=0.0)
    ground_x = lambda x: x
    # 0.8–5.0 camina hacia el botón
    if t < 5.0:
        k = seg(t, 0.8, 5.0)
        s["x"] = -560 + ease(k * 0.15 + k * 0.85) * 890
        if t > 0.8:
            s["pose"] = dict(leg=(t * 1.45) % 1.0, bob=-10 * abs(math.sin(t * 1.45 * math.pi * 2)), tilt=1.5 * math.sin(t * 1.45 * 2 * math.pi))
            if t < 4.6:
                s["pose"]["look"] = (0.9, 0.0)
        s["x"] = min(s["x"], 330)
    elif t < T_JUMP0:                                  # mira el botón y se agacha
        s["x"] = 330
        k = seg(t, 5.0, T_JUMP0)
        s["pose"] = dict(look=(1, -0.2), squash=1 - 0.10 * math.sin(math.pi * min(1, k * 1.6)) if k < 0.62 else 1.0, tilt=-2 * k)
    elif t < T_JUMP1:                                  # salta
        k = seg(t, T_JUMP0, T_JUMP1)
        s["x"] = 330 + 390 * ease(k)
        s["dy"] = -230 * 4 * k * (1 - k)
        s["pose"] = dict(spread=1.0, tilt=-10 * math.sin(k * math.pi) - 40 * ease(max(0, k - 0.6) / 0.4), look=(1, -1))
        s["aire"] = k
    elif t < 10.0:                                     # cae de espaldas y queda patas arriba
        s["x"] = 720
        k = seg(t, T_JUMP1, T_JUMP1 + 0.35)
        if t < T_JUMP1 + 0.18:
            s["pose"] = dict(tilt=-70 - 20 * k)
        else:
            rebote = max(0.0, math.exp(-(t - T_HIT) * 5) * math.sin((t - T_HIT) * 18))
            s["dy"] = -42 * rebote
            s["pose"] = dict(flip=True, spread=1.0, leg=((t - 7.3) * 2.2) % 1.0, blink=0.5 if int(t * 4) % 6 == 0 else 0, tilt=3 * math.sin(t * 9))
    elif t < 11.1:                                     # se endereza
        k = seg(t, 10.0, 11.1)
        s["x"] = 720
        s["pose"] = dict(flip=True, spread=1.0 - k, tilt=-60 * ease(k / 0.5) if k < 0.5 else 0) if k < 0.5 else dict(tilt=40 * (1 - ease((k - 0.5) / 0.5)), squash=1 - 0.08 * math.sin(math.pi * (k - 0.5) * 2))
        if k >= 0.5 and k > 0.95:
            s["pose"]["tilt"] = 0
    elif t < 13.6:                                     # enojada: tiembla y ladra 3 veces
        s["x"] = 720
        k = t - 11.1
        tiembla = 3.0 * math.sin(t * 60)
        ladrido = 0.0
        for tb in (11.7, 12.35, 13.0):
            if 0 <= t - tb < 0.28:
                ladrido = math.sin((t - tb) / 0.28 * math.pi)
        s["guau"] = ladrido
        s["pose"] = dict(mad=1, tilt=tiembla * 0.4 + 3 * ladrido, bob=-26 * ladrido, squash=1 + 0.05 * ladrido, look=(1, 0))
        s["dy"] = 0
    else:                                              # se va hacia la izquierda caminando (vista espejada)
        k = seg(t, 13.6, 17.4)
        s["x"] = 720 - ease(k * 0.3 + k * 0.7) * 1500
        s["flipx"] = True
        s["pose"] = dict(leg=(t * 1.5) % 1.0, bob=-10 * abs(math.sin(t * 1.5 * math.pi * 2)), mad=1 if k < 0.35 else 0)
    # botón: se aprieta al golpe
    if t >= T_HIT:
        s["boton"] = 1
        s["presion"] = max(0.0, 1 - (t - T_HIT) / 0.35) if t < T_HIT + 0.35 else 0.0
    else:
        s["presion"] = 0.0
    if T_HIT - 0.05 < t < T_HIT + 0.35:
        s["presion"] = ease(seg(t, T_HIT - 0.05, T_HIT + 0.05)) * (1 - ease(seg(t, T_HIT + 0.08, T_HIT + 0.35)))
    # hoja: sale del cuerpo y cae a la campana
    if t >= T_LEAF0:
        k = seg(t, T_LEAF0, T_LEAF1)
        x0, y0 = 800, 540
        x = x0 + (BELL[0] - 6 - x0) * ease(k) + 40 * math.sin(k * 6.0) * (1 - k)
        y = y0 + (BELL[1] - 10 - y0) * k * k * 0.55 + (BELL[1] - 40 - y0) * 0.45 * k + 28 * math.sin(k * 9)
        s["hoja"] = (x, y, 40 * math.sin(k * 7) + 25 * k)
    # campana
    if t >= T_LEAF1:
        u = t - T_LEAF1
        s["campana"] = (22 * math.exp(-u * 1.7) * math.sin(u * 14), True, min(1.0, u * 3) * math.exp(-max(0, u - 1.2) * 0.6))
    return s


# ------------------------------------------------------------------------------------------ render
_M = None
_BG = None


def _init():
    global _M, _BG
    _M = MA.Mascota()
    _M.frame({})
    _M.frame({"flip": True})
    _BG = Image.fromarray(fondo(), "RGB").convert("RGBA")


@lru_cache(maxsize=256)
def _sprite(pose_key, flipx):
    pose = dict(pose_key)
    img = _M.frame(pose).crop((150, 20, 1300, 1090))
    img = img.resize((int(img.width * SC), int(img.height * SC)), Image.LANCZOS)
    if flipx:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    return img


def _key(pose):
    q = {}
    for k, v in pose.items():
        if k == "look":
            q[k] = (round(v[0], 1), round(v[1], 1))
        elif k == "leg":
            q[k] = round(v * 16) / 16 % 1.0
        elif k in ("tilt",):
            q[k] = round(v / 2) * 2
        elif k in ("bob",):
            q[k] = round(v / 4) * 4
        elif isinstance(v, float):
            q[k] = round(v, 2)
        else:
            q[k] = v
    return tuple(sorted(q.items()))


def frame(i):
    t = i / FPS
    s = estado(t)
    img = _BG.copy()
    bl, pos = boton(s["boton"], s["presion"])
    img.alpha_composite(bl, (int(pos[0]), int(pos[1])))
    ang, act, br = s["campana"]
    bell = campana(ang, act, br)
    if br > 0.02:
        glow = Image.new("RGBA", (520, 520), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([60, 60, 460, 460], fill=(255, 214, 90, int(120 * br)))
        img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40)), (BELL[0] - 260, BELL[1] - 250))
        d = ImageDraw.Draw(img)
        for r_ in (120, 170):
            d.arc([BELL[0] - r_, BELL[1] - r_ + 20, BELL[0] + r_, BELL[1] + r_ + 20], -50, 50, fill=(255, 226, 120, int(200 * br)), width=6)
            d.arc([BELL[0] - r_, BELL[1] - r_ + 20, BELL[0] + r_, BELL[1] + r_ + 20], 130, 230, fill=(255, 226, 120, int(200 * br)), width=6)
    img.alpha_composite(bell, (BELL[0] - 130, BELL[1] - 190))
    spr = _sprite(_key(s["pose"]), s["flipx"])
    ox, oy = s["x"] - spr.width / 2, GROUND + s["dy"] - (FOOT - 20) * SC
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    esc = 1 - min(0.5, abs(s["dy"]) / 700)
    ImageDraw.Draw(sh).ellipse([s["x"] - 440 * esc, GROUND - 22, s["x"] + 440 * esc, GROUND + 38], fill=(0, 0, 0, int(120 * esc)))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    img.alpha_composite(spr, (int(ox), int(oy)))
    if s["hoja"]:
        x, y, a = s["hoja"]
        h = hoja_sprite().rotate(a, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(h, (int(x - h.width / 2), int(y - h.height / 2)))
    if s["guau"] > 0.05:
        d = ImageDraw.Draw(img)
        f = ImageFont.truetype(FONT, int(54 + 30 * s["guau"]))
        cx, cy = s["x"] + 300, GROUND - 640 - 40 * s["guau"]
        for a in range(-2, 3):
            ang = math.radians(-70 + a * 26); r1, r2 = 110, 110 + 70 * s["guau"]
            d.line([(cx + math.cos(ang) * r1, cy + 70 + math.sin(ang) * r1), (cx + math.cos(ang) * r2, cy + 70 + math.sin(ang) * r2)], fill=(255, 236, 160, 255), width=8)
        d.text((cx - 90, cy), "¡GUAU!", font=f, fill=(255, 246, 214, 255), stroke_width=7, stroke_fill=(34, 20, 16, 255))
    return np.asarray(img.convert("RGB")).tobytes()


# ------------------------------------------------------------------------------------------ sonido
SR = 44100


def _env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(t / max(a, 1e-4), 1) * np.exp(-t / d)


def audio():
    n = int(DUR * SR)
    y = np.zeros(n, np.float32)

    def add(t0, x, g=1.0):
        i = int(t0 * SR)
        j = min(n, i + len(x))
        if i < n:
            y[i:j] += (x[:j - i] * g).astype(np.float32)

    rng = np.random.RandomState(1)
    def thump(f=120, d=0.09, g=1.0):
        m = int(SR * 0.25); t = np.arange(m) / SR
        return np.sin(2 * math.pi * f * t * (1 - 0.35 * t / 0.25)) * _env(m, 0.002, d) * g + rng.randn(m) * 0.05 * _env(m, 0.001, 0.015)
    for cyc_t in list(np.arange(0.8, 5.0, 1 / 1.45 / 2)) + list(np.arange(13.7, 17.4, 1 / 1.5 / 2)):         # pasitos (2 por ciclo)
        add(cyc_t, thump(150 + rng.randint(-20, 20), 0.05, 0.35))
    m = int(SR * 0.5); t = np.arange(m) / SR                                                                   # salto: boing
    add(T_JUMP0, np.sin(2 * math.pi * np.cumsum(260 + 520 * t / 0.5) / SR) * _env(m, 0.005, 0.18) * 0.5)
    add(T_HIT, thump(70, 0.22, 1.2))                                                                           # golpe contra el botón
    add(T_HIT + 0.02, rng.randn(int(SR * 0.2)) * _env(int(SR * 0.2), 0.001, 0.03) * 0.25)
    m = int(SR * 0.9); t = np.arange(m) / SR                                                                   # «pop-ding» de suscripción
    pop = np.sin(2 * math.pi * 480 * t) * _env(m, 0.002, 0.05) + (np.sin(2 * math.pi * 880 * t) + 0.5 * np.sin(2 * math.pi * 1320 * t)) * _env(m, 0.005, 0.28) * 0.6
    add(T_HIT + 0.12, pop, 0.5)
    m = int(SR * 1.6); t = np.arange(m) / SR                                                                   # hoja: susurro
    add(T_LEAF0, rng.randn(m) * np.sin(np.pi * np.minimum(t / 1.6, 1)) ** 2 * 0.05 * (0.5 + 0.5 * np.sin(t * 22)))
    m = int(SR * 3.0); t = np.arange(m) / SR                                                                   # campanita
    camp = sum(np.sin(2 * math.pi * f * t) * a for f, a in ((1180, 1.0), (2380, 0.6), (3320, 0.35), (4710, 0.2))) * _env(m, 0.002, 0.7)
    add(T_LEAF1, camp, 0.28)
    for tb in (11.7, 12.35, 13.0):                                                                             # ladridos
        m = int(SR * 0.28); t = np.arange(m) / SR
        f0 = 520 - 260 * t / 0.28
        ph = np.cumsum(f0) / SR * 2 * math.pi
        src = sum(np.sin(ph * h) / h for h in range(1, 9))
        formant = np.sin(2 * math.pi * 900 * t) * 0.4 + 1.0
        b = src * formant * _env(m, 0.01, 0.12) + rng.randn(m) * 0.15 * _env(m, 0.005, 0.05)
        add(tb, b, 0.35)
    y = np.tanh(y * 1.2)
    y = y / max(1e-6, np.abs(y).max()) * 0.8
    return (y * 32767).astype(np.int16)


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "gag.mp4")
    rango = None
    if "--frames" in sys.argv:
        a, b = sys.argv[sys.argv.index("--frames") + 1].split(":"); rango = (int(a), int(b))
    n = int(DUR * FPS)
    idx = range(*rango) if rango else range(n)
    wav = out.with_suffix(".wav")
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(audio().tobytes())
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", str(wav), "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                           "-shortest", "-movflags", "+faststart", str(out)], stdin=subprocess.PIPE)
    with Pool(4, initializer=_init) as pool:
        for k, b in enumerate(pool.imap(frame, idx, chunksize=2)):
            ff.stdin.write(b)
            if k % 48 == 0:
                print("cuadro", k, "/", len(idx), flush=True)
    ff.stdin.close(); ff.wait()
    print("listo", out)


if __name__ == "__main__":
    main()
