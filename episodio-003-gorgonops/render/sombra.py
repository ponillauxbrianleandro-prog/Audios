"""Diseño «Sombra»: el lenguaje plano del canal.

Rojo ligeramente azulado de fondo, siluetas negras (animales y plantas sacados del propio rig),
blanco para texto y líneas, verde+negro para lo positivo y rojo claro+negro para lo negativo.
Se usa en la apertura, en los créditos y en insertos sobre el documental (libreta y lapicera).
Todas las funciones devuelven un fotograma float32 (H, W, 3) en [0, 1] y trabajan en «unidades de
diseño» de 1280×720 (se escalan solas a cualquier resolución).
"""
import os
import pickle

import cv2
import numpy as np
from PIL import Image, ImageDraw

import creature as C
import engine
import graficos as G
import plants
import world

SS = 2
RED = (184, 35, 63)          # fondo: más rojo que azul
RED_D = (140, 22, 49)        # rojo oscuro: marcos, fondos secundarios, plantas lejanas
RED_L = (212, 58, 84)
BLACK = (11, 11, 16)
WHITE = (247, 243, 234)
GREEN = (47, 178, 107)       # positivo
LRED = (255, 106, 92)        # negativo (rojo claro, sin azul)
ease = G.ease


# ------------------------------------------------------------------ siluetas del rig
_SIL = {}


def silueta(name, n=32):
    """Ciclo de marcha del animal como máscara plana: 0 = vacío, 1 = negro, 2 = blanco (diente, ojo).
    Se calcula una vez desde creature.render y se guarda en caché."""
    if name in _SIL:
        return _SIL[name]
    spec = dict(gorgonops=C.GORGONOPS, procynosuchus=C.PROCYNOSUCHUS, diictodon=C.DIICTODON, pareiasaur=C.PAREIASAUR)[name]
    path = os.path.join(world.CACHE, f"sil_{name}.pkl")
    if os.path.exists(path):
        _SIL[name] = pickle.load(open(path, "rb"))
        return _SIL[name]
    world.load()
    cam = world.Camera(1280, 720, 3000, (0, 0.9, 0), 0.0, 0.0)
    z = 5.5 / (1.0 if spec["scale"] >= 0.9 else 2.2)
    spr = []
    for i in range(n):
        pose = dict(phase=i / n, walk=1.0, t=1.0, head_pitch=0.08, head_dy=-0.02, bob=0.8)
        spr.append(C.render(spec, cam, (0, 0, z), -0.08 * np.pi, pose, ss=2.0))
    x0 = int(min(s["x0"] for s in spr))
    y0 = int(min(s["y0"] for s in spr))
    x1 = int(max(s["x0"] + s["a"].shape[1] for s in spr)) + 1
    y1 = int(max(s["y0"] + s["a"].shape[0] for s in spr)) + 1
    frames = np.zeros((n, y1 - y0, x1 - x0), np.uint8)
    for i, s in enumerate(spr):
        a = cv2.GaussianBlur(s["a"], (0, 0), 1.3) > 0.5                 # redondea: forma plana, sin detalle fino
        a = cv2.morphologyEx(a.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) > 0
        k = s["kind"]
        white = a & ((k == C.TOOTH) | (k == C.EYE))
        fr = np.zeros(a.shape, np.uint8)
        fr[a] = 1
        fr[white] = 2
        ox, oy = int(s["x0"]) - x0, int(s["y0"]) - y0
        frames[i, oy:oy + fr.shape[0], ox:ox + fr.shape[1]] = fr
    out = dict(frames=frames, n=n, pxm=cam.f / z, speed=spec["speed"], period=spec["period"])
    pickle.dump(out, open(path, "wb"))
    _SIL[name] = out
    return out


_SCALED = {}


def _sil_img(name, idx, width_px, flip=False):
    S = silueta(name)
    key = (name, idx % S["n"], int(width_px), flip)
    if key in _SCALED:
        return _SCALED[key]
    fr = S["frames"][idx % S["n"]]
    h, w = fr.shape
    tw = max(2, int(width_px))
    th = max(2, int(round(h * tw / w)))
    ma = cv2.resize((fr > 0).astype(np.float32), (tw, th), interpolation=cv2.INTER_AREA)
    mw = cv2.resize((fr == 2).astype(np.float32), (tw, th), interpolation=cv2.INTER_AREA)
    wf = np.clip(mw / np.maximum(ma, 1e-3), 0, 1)[..., None]
    rgb = (np.array(BLACK, np.float32) * (1 - wf) + np.array(WHITE, np.float32) * wf).astype(np.uint8)
    if flip:
        rgb, ma = rgb[:, ::-1], ma[:, ::-1]
    img = Image.fromarray(np.ascontiguousarray(rgb), "RGB")
    msk = Image.fromarray(np.ascontiguousarray((ma * 255).astype(np.uint8)), "L")
    _SCALED[key] = (img, msk)
    return _SCALED[key]


def _paste_sil(im, name, idx, cx, base_y, width_d, k, flip=False):
    """Pega la silueta centrada en cx, con los pies en base_y (unidades de diseño)."""
    img, msk = _sil_img(name, idx, width_d * k, flip)
    im.paste(img, (int(cx * k - img.width / 2), int(base_y * k - img.height)), msk)
    return img.height / k


_PL = {}
_LIB = None


def _plant_sil(kind, var, height_px, tone):
    global _LIB
    key = (kind, var, int(height_px), tone)
    if key in _PL:
        return _PL[key]
    if _LIB is None:
        _LIB = plants.library()
    sp = _LIB[kind][var % len(_LIB[kind])]
    a = sp["a"].astype(np.float32) / 255.0
    h, w = a.shape
    th = max(2, int(height_px))
    tw = max(2, int(round(w * th / h)))
    m = cv2.resize(a, (tw, th), interpolation=cv2.INTER_AREA)
    m = np.clip((cv2.GaussianBlur(m, (0, 0), 0.8) - 0.30) * 3.0, 0, 1)
    img = Image.new("RGB", (tw, th), tone)
    msk = Image.fromarray((m * 255).astype(np.uint8), "L")
    _PL[key] = (img, msk)
    return _PL[key]


def _paste_plant(im, kind, var, cx, base_y, height_d, k, tone=BLACK):
    img, msk = _plant_sil(kind, var, height_d * k, tone)
    im.paste(img, (int(cx * k - img.width / 2), int(base_y * k - img.height)), msk)


# ------------------------------------------------------------------ piezas de interfaz
def _canvas(W, H, col=RED):
    im = Image.new("RGB", (W * SS, H * SS), col)
    return im, ImageDraw.Draw(im)


def _out(im, W, H):
    return np.asarray(im.resize((W, H), Image.LANCZOS), np.float32) / 255.0


def F(size, k, weight="SemiBold", italic=False):
    return engine.font(max(6, int(size * k)), weight, italic)


def text(d, k, x, y, s, size, fill=WHITE, weight="SemiBold", anchor="la", shadow=0, italic=False):
    f = F(size, k, weight, italic)
    if shadow:
        d.text(((x + shadow) * k, (y + shadow) * k), s, font=f, fill=BLACK, anchor=anchor)
    d.text((x * k, y * k), s, font=f, fill=fill, anchor=anchor)
    return d.textlength(s, font=f) / k


def pill(d, k, x, y, s, size=22, bg=BLACK, fg=WHITE, weight="Bold", pad=(14, 7), anchor="l"):
    f = F(size, k, weight)
    w = d.textlength(s, font=f) / k + pad[0] * 2
    h = size * 1.15 + pad[1] * 2
    x0 = x if anchor == "l" else x - w / 2
    d.rounded_rectangle([x0 * k, y * k, (x0 + w) * k, (y + h) * k], radius=h * 0.5 * k, fill=bg)
    d.text(((x0 + pad[0]) * k, (y + pad[1]) * k), s, font=f, fill=fg)
    return x0 + w, y + h


def badge(d, k, cx, cy, r, ok=True):
    """Círculo verde con tilde negra o rojo claro con cruz negra (se dibujan como trazos)."""
    d.ellipse([(cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k], fill=GREEN if ok else LRED)
    w = max(2, int(r * 0.26 * k))
    if ok:
        d.line([((cx - 0.48 * r) * k, (cy + 0.02 * r) * k), ((cx - 0.12 * r) * k, (cy + 0.40 * r) * k),
                ((cx + 0.52 * r) * k, (cy - 0.38 * r) * k)], fill=BLACK, width=w, joint="curve")
    else:
        for sx in (-1, 1):
            d.line([((cx - 0.40 * r) * k, (cy - 0.40 * sx * r) * k), ((cx + 0.40 * r) * k, (cy + 0.40 * sx * r) * k)], fill=BLACK, width=w)


def slide(t, a, b, enter=0.55, exit_=0.4):
    """(alfa, desplazamiento) de una tarjeta visible entre a y b."""
    if t < a or t > b:
        return 0.0, 0.0
    e = ease((t - a) / enter)
    x = ease((b - t) / exit_)
    off = (1 - e) * 70 - (1 - x) * 70
    return min(e, x), off


def dashed(d, k, pts, color=WHITE, width=3, dash=14, gap=9, phase=0.0):
    """Línea punteada por una polilínea (unidades de diseño)."""
    P = np.array(pts, float)
    seg = np.hypot(*np.diff(P, axis=0).T)
    L = np.concatenate([[0], np.cumsum(seg)])
    tot = L[-1]
    s = -phase % (dash + gap) - (dash + gap)
    while s < tot:
        a, b = max(s, 0), min(s + dash, tot)
        if b > a:
            pa = np.array([np.interp(a, L, P[:, 0]), np.interp(a, L, P[:, 1])])
            pb = np.array([np.interp(b, L, P[:, 0]), np.interp(b, L, P[:, 1])])
            d.line([tuple(pa * k), tuple(pb * k)], fill=color, width=int(width * k))
        s += dash + gap


# ------------------------------------------------------------------ libreta y lapicera
def _pen(d, k, tx, ty, ang=0.62):
    """Lapicera plana, blanca con punta roja; la punta en (tx, ty)."""
    L, wd = 120, 12
    ca, sa = np.cos(ang), np.sin(ang)
    P = lambda u, v: ((tx + (u * ca - v * sa)) * k, (ty - (u * sa + v * ca)) * k)
    d.polygon([P(0, 0), P(22, wd * 0.45), P(L, wd * 0.5), P(L, -wd * 0.5), P(22, -wd * 0.45)], fill=WHITE, outline=BLACK)
    d.polygon([P(0, 0), P(22, wd * 0.45), P(22, -wd * 0.45)], fill=LRED, outline=BLACK)
    d.polygon([P(40, wd * 0.5), P(52, wd * 0.5), P(52, -wd * 0.5), P(40, -wd * 0.5)], fill=BLACK)
    d.line([P(60, wd * 0.2), P(L - 6, wd * 0.2)], fill=(200, 196, 188), width=max(1, int(2 * k)))


def libreta(im, d, k, x, y, w, h, lines, tw, size=26):
    """Libreta con marco rojo, hoja negra con renglones blancos; las anotaciones se escriben con la lapicera.
    lines = [(tipo, texto)], tipo = 'ok' (verde), 'no' (rojo claro) o 'txt'. tw = segundos desde que empieza a escribir."""
    fr = 12
    d.rounded_rectangle([(x - fr) * k, (y - fr) * k, (x + w + fr) * k, (y + h + fr) * k], radius=26 * k, fill=RED_D)
    d.rounded_rectangle([x * k, y * k, (x + w) * k, (y + h) * k], radius=16 * k, fill=BLACK)
    for i in range(1, 7):                                           # renglones
        yy = y + 62 * i * h / 420
        if yy < y + h - 12:
            d.line([((x + 70) * k, yy * k), ((x + w - 24) * k, yy * k)], fill=(70, 70, 78), width=max(1, int(1.6 * k)))
    d.line([((x + 62) * k, (y + 12) * k), ((x + 62) * k, (y + h - 12) * k)], fill=(150, 40, 60), width=max(1, int(2 * k)))
    for i in range(7):                                              # espiral
        cy = y + 40 + i * (h - 70) / 6
        d.ellipse([(x - 12) * k, (cy - 9) * k, (x + 16) * k, (cy + 9) * k], fill=WHITE, outline=BLACK, width=max(1, int(2 * k)))
    f = F(size, k, "Medium", True)
    step, rev = 1.05, 0.95
    tip = None
    for i, (kind, s) in enumerate(lines):
        t0 = i * step + 0.2
        p = ease((tw - t0) / rev)
        if p <= 0:
            continue
        ly = y + 62 * (i + 1) * h / 420 - size * 0.95
        if kind in ("ok", "no"):
            badge(d, k, x + 34, ly + size * 0.62, 15, kind == "ok")
        tx0 = x + 78
        tl = d.textlength(s, font=f)
        layer = Image.new("RGBA", (int(tl) + 8, int(size * k * 1.5)), (0, 0, 0, 0))
        ImageDraw.Draw(layer).text((2, 0), s, font=f, fill=WHITE if kind != "ok" else (214, 248, 228))
        cw = max(1, int((tl + 4) * p))
        im.paste(layer.crop((0, 0, cw, layer.height)), (int(tx0 * k), int(ly * k)), layer.crop((0, 0, cw, layer.height)))
        if p < 1:
            tip = (tx0 + cw / k, ly + size * 0.9)
    if tip is None and tw < len(lines) * step + 0.3:
        tip = (x + 120, y + 70)
    if tip is not None:
        _pen(d, k, tip[0] + 4, tip[1] - 3)


def nota_overlay(img, t, dur, lines, corner="br", width=0.40):
    """Libreta sobre el documental (esquina). Entra deslizando, escribe y se va. img float (H, W, 3)."""
    H, W = img.shape[:2]
    a, off = slide(t, 0, dur, 0.7, 0.6)
    if a <= 0:
        return img
    k = W / 1280 * SS
    nw = width * 1280
    nh = 96 * len(lines) + 70
    x = 1280 - nw - 46 if "r" in corner else 46
    y = 720 - nh - 50 if "b" in corner else 50
    dx = off / 70.0 * (nw + 80) * (1 if "r" in corner else -1)
    im = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    libreta(im, d, k, x + dx, y, nw, nh, lines, max(0.0, t - 0.5), size=int(22 * nw / 512))
    lay = np.asarray(im.resize((W, H), Image.LANCZOS), np.float32) / 255.0
    al = lay[..., 3:4] * a
    return img * (1 - al) + lay[..., :3] * al


# ------------------------------------------------------------------ fondo, suelo y plantas
_FAR = [("treefern", 1, 0.07, 128), ("conifer", 2, 0.16, 330), ("horsetail", 4, 0.24, 120), ("tree", 3, 0.33, 285),
        ("fern", 2, 0.41, 78), ("treefern", 4, 0.50, 120), ("conifer", 5, 0.58, 300), ("tree", 5, 0.66, 260),
        ("horsetail", 7, 0.74, 150), ("conifer", 0, 0.82, 340), ("treefern", 2, 0.90, 140), ("tree", 1, 0.97, 240)]
_NEAR = [("fern", 3, 0.03, 120), ("horsetail", 2, 0.08, 190), ("fern", 5, 0.95, 130), ("horsetail", 6, 0.99, 210), ("lycopsid", 3, 0.90, 70)]


def fondo(im, d, W, H, k, t, ground_y=0.80, sway=1.0):
    """Fondo rojo con bandas suaves, plantas lejanas en rojo oscuro y suelo negro."""
    gy = ground_y * 720
    for i, (cx, wd) in enumerate(((0.18, 0.55), (0.62, 0.40), (0.95, 0.35))):                   # bandas diagonales
        d.polygon([((cx * 1280 - wd * 460) * k, 0), ((cx * 1280 + wd * 120) * k, 0), ((cx * 1280 + wd * 120 - 260) * k, 720 * k), ((cx * 1280 - wd * 460 - 260) * k, 720 * k)],
                  fill=tuple(int(c * (0.96 - 0.03 * i)) for c in RED))
    for kind, var, fx, h in _FAR:
        _paste_plant(im, kind, var, fx * 1280 + 3 * np.sin(t * 0.7 + var) * sway, gy + 6, h, k, RED_D)
    xs = np.linspace(0, 1280, 90)
    ys = gy + 5 * np.sin(xs / 85.0) + 3 * np.sin(xs / 31.0 + 1.0)
    d.polygon([(0, 720 * k)] + [(x * k, y * k) for x, y in zip(xs, ys)] + [(1280 * k, 720 * k)], fill=BLACK)


def primer_plano(im, d, k, t):
    for kind, var, fx, h in _NEAR:
        _paste_plant(im, kind, var, fx * 1280 + 4 * np.sin(t * 0.9 + var), 735, h, k, BLACK)


def _walker_x(t, t0, x0, width_d, name="gorgonops"):
    S = silueta(name)
    sw = S["frames"].shape[2]
    pxm_d = width_d * S["pxm"] / sw
    v = S["speed"] * pxm_d
    return x0 + v * max(0.0, t - t0), v


# ------------------------------------------------------------------ mapa esquemático
_MAP = {}
CROP = (0.24, 0.06, 0.82, 0.86)
SITIOS = dict(karoo=(0.485, 0.735), este=(0.527, 0.625), rusia=(0.560, 0.215), china=(0.700, 0.300), mallorca=(0.440, 0.335))


def _mapa(wd, hd, k):
    key = (int(wd * k), int(hd * k))
    if key not in _MAP:
        f = G._land()
        x0, y0, x1, y1 = CROP
        sub = f[int(y0 * 540):int(y1 * 540), int(x0 * 960):int(x1 * 960)]
        sub = cv2.resize(sub, key, interpolation=cv2.INTER_CUBIC)
        m = (cv2.GaussianBlur(sub, (0, 0), 1.5 * k) > 0.0).astype(np.uint8) * 255
        _MAP[key] = Image.fromarray(m, "L")
    return _MAP[key]


def _pt(name, mx, my, mw, mh):
    fx, fy = SITIOS[name]
    x0, y0, x1, y1 = CROP
    return mx + (fx - x0) / (x1 - x0) * mw, my + (fy - y0) / (y1 - y0) * mh


# ------------------------------------------------------------------ apertura (15 s)
def intro(t, W, H, dur=15.0, starts=None, total=None):
    # las tarjetas siguen a las frases de la voz: se deforma el tiempo para que cada una aparezca cuando empieza su frase
    if starts is not None and total:
        real = [0.0, max(0.5, starts[1] - 0.25), max(1.0, starts[2] - 0.25), max(1.5, starts[3] - 0.25), float(total)]
        t = float(np.interp(t, real, [0.0, 2.6, 6.8, 11.2, 15.0]))
    k = W / 1280 * SS
    im, d = _canvas(W, H)
    fondo(im, d, W, H, k, t, 0.81)
    GY = 0.81 * 720

    # --- silueta protagonista: grande en el título, luego camina por el suelo
    S = silueta("gorgonops")
    t_hero, t_small = 2.1, 3.0
    e = ease((t - t_hero) / (t_small - t_hero))
    w_big, w_small = 640, 232
    wd = w_big + (w_small - w_big) * e
    x_start, _ = _walker_x(t, t_small, 150, w_small)
    cx = 930 + (x_start - 930) * e
    if t < t_hero:
        frame = 0
    else:
        frame = int(((t - t_hero) / S["period"]) * S["n"])
    base = GY + 4 + 0 * e
    ah = 1 + 0 * e

    # --- tarjetas
    def card(a, b, fn):
        al, off = slide(t, a, b)
        if al > 0:
            fn(off, al)

    def titulo(off, al):
        text(d, k, 70 - off * 3, 96, "DOCUMENTAL", 22, WHITE, "Bold", shadow=0)
        d.line([((70 - off * 3) * k, 128 * k), ((200 - off * 3) * k, 128 * k)], fill=WHITE, width=int(4 * k))
        text(d, k, 66 - off * 3, 152, "GORGONOPS", 150, WHITE, "Black", shadow=7)
        text(d, k, 72 - off * 3, 330, "Gorgonops torvus · Pérmico tardío", 34, WHITE, "SemiBold")
        pill(d, k, 72 - off * 3, 384, "lo que el barro recuerda", 24, BLACK, WHITE, "Medium")

    def cuando(off, al):
        o = off * 3
        pill(d, k, 70 + o, 54, "CUÁNDO", 24)
        text(d, k, 70 + o, 98, "260–254", 124, WHITE, "Black", shadow=6)
        text(d, k, 74 + o, 232, "millones de años · la especie", 30, WHITE, "SemiBold")
        text(d, k, 700 + o, 98, "≥ 18", 124, WHITE, "Black", shadow=6)
        text(d, k, 704 + o, 232, "millones de años · el linaje", 30, WHITE, "SemiBold")
        x0, x1 = 70 + o, 1210 + o
        X = lambda ma: x0 + (300 - ma) / 50.0 * (x1 - x0)
        y = 452
        p = ease((t - 3.4) / 1.2)
        d.line([(x0 * k, y * k), (x1 * k, y * k)], fill=WHITE, width=int(3 * k))
        for ma in range(300, 249, -10):
            d.line([(X(ma) * k, (y - 7) * k), (X(ma) * k, (y + 7) * k)], fill=WHITE, width=int(3 * k))
            text(d, k, X(ma), y + 12, f"{ma}", 19, WHITE, "Medium", anchor="ma")
        text(d, k, x1, y + 38, "millones de años atrás", 17, WHITE, "Regular", anchor="ra")
        gx0, gx1 = X(270), X(270) + (X(252) - X(270)) * p                           # linaje
        d.rounded_rectangle([gx0 * k, (y - 52) * k, gx1 * k, (y - 34) * k], radius=9 * k, outline=WHITE, width=int(3 * k))
        text(d, k, X(270), y - 82, "Gorgonopsia · ~270 → 252", 21, WHITE, "SemiBold")
        sx0, sx1 = X(260), X(260) + (X(254) - X(260)) * ease((t - 3.9) / 0.9)       # especie
        d.rounded_rectangle([sx0 * k, (y - 26) * k, sx1 * k, (y - 8) * k], radius=9 * k, fill=WHITE)
        text(d, k, X(257), y - 28 + 38 + 4, "", 1)
        text(d, k, X(257), y + 62, "G. torvus", 21, WHITE, "SemiBold", anchor="ma")
        if t > 4.8:
            pr = ease((t - 4.8) / 0.5)
            ex = X(252)
            d.line([(ex * k, (y - 98) * k), (ex * k, (y + 18) * k)], fill=LRED, width=int(4 * k))
            pill(d, k, ex + 14, y - 118 - 6, "extinción del Pérmico", 19, LRED, BLACK, "Bold")
            badge(d, k, ex, y - 100, 14 * pr, False)

    def donde(off, al):
        o = off * 3
        pill(d, k, 70 + o, 54, "DÓNDE", 24)
        mx, my, mw, mh = 60 + o, 100, 490, 354
        d.rounded_rectangle([(mx - 10) * k, (my - 10) * k, (mx + mw + 10) * k, (my + mh + 10) * k], radius=24 * k, fill=RED_D)
        m = _mapa(mw, mh, k)
        im.paste(Image.new("RGB", m.size, BLACK), (int(mx * k), int(my * k)), m)
        pts = {n: _pt(n, mx, my, mw, mh) for n in SITIOS}
        # arco Karoo → Rusia
        a, b = np.array(pts["karoo"]), np.array(pts["rusia"])
        c = (a + b) / 2 + np.array([-70, 0])
        pr = ease((t - 8.2) / 1.1)
        curve = [tuple((1 - u) ** 2 * a + 2 * u * (1 - u) * c + u * u * b) for u in np.linspace(0, pr, 50)]
        if len(curve) > 2:
            dashed(d, k, curve, WHITE, 3, 12, 8, phase=t * 30)
        mid = (1 - 0.5) ** 2 * a + 2 * 0.25 * c + 0.25 * b
        if pr > 0.8:
            pill(d, k, mid[0] - 10, mid[1] - 6, "≈ 11 300 km", 21, WHITE, BLACK, "Bold", anchor="c")
        for n, lab, dx, dy, an, big in (("karoo", "Cuenca del Karoo", 14, 6, "la", True), ("este", "Tanzania · Zambia · Malawi", 14, -4, "la", False),
                                        ("rusia", "Rusia", 12, -26, "la", False), ("china", "China", -8, -30, "ma", False), ("mallorca", "Mallorca", -12, -28, "ra", False)):
            p0 = ease((t - 7.0 - 0.18 * list(SITIOS).index(n)) / 0.4)
            if p0 <= 0:
                continue
            x, y = pts[n]
            r = (11 if big else 7) * p0
            if big:
                pu = (t * 1.4) % 1.0
                rr = (15 + 24 * pu) * p0
                d.ellipse([(x - rr) * k, (y - rr) * k, (x + rr) * k, (y + rr) * k], outline=WHITE, width=max(1, int(3 * k * (1 - pu))))
            d.ellipse([(x - r) * k, (y - r) * k, (x + r) * k, (y + r) * k], fill=WHITE, outline=BLACK, width=int(2 * k))
            text(d, k, x + dx, y + dy, lab, 19 if big else 17, WHITE, "Bold", anchor=an)
        text(d, k, mx + mw / 2, my + mh + 20, "mapa esquemático · Pangea", 15, WHITE, "Regular", anchor="ma")
        # cifras
        rx = 590 + o
        text(d, k, rx, 96, "≈ 700 000 km²", 78, WHITE, "Black", shadow=5)
        text(d, k, rx + 3, 188, "cuenca del Karoo (Sudáfrica): el único lugar", 23, WHITE, "SemiBold")
        text(d, k, rx + 3, 216, "donde se conoce Gorgonops torvus", 23, WHITE, "SemiBold")
        pill(d, k, rx + 3, 262, "radio equivalente ≈ 470 km", 22, BLACK, WHITE, "Bold")
        text(d, k, rx + 3, 316, "≈ 2,3 veces la provincia de Buenos Aires", 20, WHITE, "Medium")
        text(d, k, rx, 372, "≈ 11 300 km", 66, WHITE, "Black", shadow=5)
        text(d, k, rx + 3, 450, "del Karoo a Rusia: lo que abarca el grupo,", 21, WHITE, "SemiBold")
        text(d, k, rx + 3, 476, "no lo que caminaba un animal", 21, WHITE, "SemiBold")

    def explica(off, al):
        o = off * 3
        pill(d, k, 70 + o, 40, "UN RANGO NO ES UN RECORRIDO", 24)
        lib = [("ok", "huesos hallados = lugares conocidos"),
               ("txt", "Σ lugares  →  ≈ 700 000 km²"),
               ("no", "cuánto caminaba cada uno: se infiere")]
        libreta(im, d, k, 130 + o, 102, 1020, 388, lib, max(0.0, t - 11.9), size=44)

    card(0.0, 3.0, titulo)
    card(2.6, 7.2, cuando)
    card(6.8, 11.6, donde)
    card(11.2, 14.9, explica)

    # --- silueta y plantas del primer plano
    _paste_sil(im, "gorgonops", frame, cx, base, wd, k)
    primer_plano(im, d, k, t)
    return _out(im, W, H)


# ------------------------------------------------------------------ créditos
def creditos(t, W, H, dur=18.0):
    k = W / 1280 * SS
    im, d = _canvas(W, H)
    fondo(im, d, W, H, k, t, 0.84)
    GY = 0.84 * 720
    S = silueta("gorgonops")
    cx, _ = _walker_x(t, 0, -120, 210)
    _paste_sil(im, "gorgonops", int(t / S["period"] * S["n"]), cx, GY + 4, 210, k)
    S2 = silueta("procynosuchus")
    _paste_sil(im, "procynosuchus", int(t / S2["period"] * S2["n"]), 1450 - 55 * t, GY + 5, 112, k, flip=True)

    def card(a, b, fn):
        al, off = slide(t, a, b, 0.7, 0.6)
        if al > 0:
            fn(off * 3)

    def c1(o):
        text(d, k, 640, 150 + 0 * o, "GORGONOPS", 130, WHITE, "Black", anchor="ma", shadow=6)
        pill(d, k, 640 - o * 0.3, 318, "lo que el barro recuerda", 28, BLACK, WHITE, "Medium", anchor="c")
        text(d, k, 640, 392, "Imagen, animación y música generadas por código", 24, WHITE, "SemiBold", anchor="ma")

    def c2(o):
        pill(d, k, 640, 70, "CITAS", 24, BLACK, WHITE, "Bold", anchor="c")
        rows = [("Ken Angielczyk", "Field Museum"), ("Megan Whitney", "Universidad de Washington"), ("Pia Viglietti", "Field Museum"),
                ("Christian Kammerer", "North Carolina Museum of Natural Sciences"), ("Charles Darwin", "El origen de las especies, 1859")]
        for i, (a, b) in enumerate(rows):
            y = 140 + i * 64
            text(d, k, 640 - 8, y, a, 34, WHITE, "Bold", anchor="ra", shadow=3)
            text(d, k, 640 + 8, y + 7, b, 24, WHITE, "Medium", anchor="la")

    def c3(o):
        pill(d, k, 640, 70, "FUENTES", 24, BLACK, WHITE, "Bold", anchor="c")
        for i, s in enumerate(["Kammerer et al. 2023 · Current Biology", "Matamales-Andreu et al. 2024 · Nature Communications",
                               "Whitney, Mose y Sidor 2016 · JAMA Oncology", "Datos de rango: cuenca del Karoo ≈ 700 000 km²"]):
            text(d, k, 640, 140 + i * 48, s, 27, WHITE, "SemiBold", anchor="ma")
        badge(d, k, 470, 372, 20, True)
        text(d, k, 502, 354, "confirmado por fósiles", 28, WHITE, "Bold")
        badge(d, k, 470, 430, 20, False)
        text(d, k, 502, 412, "hipótesis (color, piel, conducta)", 28, WHITE, "Bold")

    card(0.4, 6.4, c1)
    card(6.2, 12.2, c2)
    card(12.0, 17.6, c3)
    primer_plano(im, d, k, t)
    out = _out(im, W, H)
    return out * min(1.0, t / 0.6, (dur - t) / 0.8)



def rotulo(img, t, dur, lugar, detalle=""):
    """Rótulo de lugar en Sombra (abajo a la izquierda): etiqueta roja con texto blanco. img float (H, W, 3)."""
    H, W = img.shape[:2]
    a, off = slide(t, 0.6, dur - 0.2, 0.6, 0.5)
    if a <= 0:
        return img
    k = W / 1280 * SS
    im = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x, y = 46 - off * 3, 40
    d.rounded_rectangle([(x - 10) * k, (y - 8) * k, (x + 20 + max(d.textlength(lugar, font=F(30, k, "Bold")), d.textlength(detalle, font=F(19, k, "Medium"))) / k + 10) * k,
                         (y + (82 if detalle else 52)) * k], radius=14 * k, fill=RED + (255,))
    d.text(((x + 8) * k, y * k), lugar, font=F(30, k, "Bold"), fill=WHITE)
    if detalle:
        d.text(((x + 8) * k, (y + 44) * k), detalle, font=F(19, k, "Medium"), fill=WHITE)
    lay = np.asarray(im.resize((W, H), Image.LANCZOS), np.float32) / 255.0
    al = lay[..., 3:4] * a
    return img * (1 - al) + lay[..., :3] * al
