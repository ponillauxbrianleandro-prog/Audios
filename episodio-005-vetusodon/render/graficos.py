"""Gráfica científica sobria: Pangea, cráneo, dientes, árbol evolutivo, mandíbula->oído,
hoja fósil, huellas, títulos y citas. Todo dibujado por código (PIL), con supermuestreo."""
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter
from util import fbm, smoothstep, lerp
import engine

SS = 2
BG = (0.105, 0.125, 0.155)
INK = (232, 228, 214)
AMBER = (226, 168, 78)
RED = (205, 92, 70)
BLUE = (120, 170, 205)
_TEX = {}


def _tex(seed, beta=2.0):
    if (seed, beta) not in _TEX:
        _TEX[(seed, beta)] = fbm((540, 960), beta, seed)
    return _TEX[(seed, beta)]


def _base(W, H, col=BG, seed=3, amp=0.035):
    n = cv2.resize(_tex(seed), (W, H))
    n2 = cv2.resize(_tex(seed + 1, 1.0), (W, H))
    img = np.array(col, np.float32) * (1 + (n[..., None] - 0.5) * amp * 6) + (n2[..., None] - 0.5) * amp * 0.5
    return img.astype(np.float32)


def _canvas(W, H):
    return Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))


def _merge(img, lay, alpha=1.0):
    W, H = img.shape[1], img.shape[0]
    a = np.asarray(lay.resize((W, H), Image.LANCZOS), np.float32) / 255.0
    al = a[..., 3:4] * alpha
    return img * (1 - al) + a[..., :3] * al


def _text(d, xy, txt, size, fill=INK, weight="Medium", anchor="la", italic=False, alpha=255):
    f = engine.font(int(size * SS), weight, italic)
    d.text((xy[0] * SS, xy[1] * SS), txt, font=f, fill=tuple(fill) + (int(alpha),), anchor=anchor)


def _finish(img, t):
    H, W = img.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r2 = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
    img = img * (1 - 0.22 * r2 ** 1.2)[..., None]
    g = np.random.default_rng(int(t * 1000) + 11).normal(0, 1, (H, W)).astype(np.float32)
    g = cv2.GaussianBlur(g, (0, 0), 0.7)
    return np.clip(img + g[..., None] * 0.012, 0, 1)


def ease(x):
    x = float(np.clip(x, 0, 1))
    return x * x * (3 - 2 * x)


# ------------------------------------------------------------------ Pangea
_LAND = None


def _land():
    global _LAND
    if _LAND is None:
        h, w = 540, 960
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        x, y = xx / w, yy / h

        def ell(cx, cy, rx, ry, rot=0.0):
            c, s = np.cos(rot), np.sin(rot)
            u, v = (x - cx) * c + (y - cy) * s * 0.5625, -(x - cx) * s + (y - cy) * c * 0.5625
            return 1 - np.sqrt((u / rx) ** 2 + (v / ry) ** 2)
        f = np.maximum.reduce([ell(0.47, 0.30, 0.20, 0.085, -0.25), ell(0.60, 0.20, 0.13, 0.075, 0.3), ell(0.38, 0.40, 0.085, 0.10),
                               ell(0.43, 0.56, 0.12, 0.10), ell(0.50, 0.68, 0.19, 0.10, 0.2), ell(0.63, 0.74, 0.13, 0.065, -0.2)])
        f = np.minimum(f, -ell(0.70, 0.46, 0.17, 0.062, -0.15) * 1.2 + 0.25)
        f = f + (fbm((h, w), 2.2, 44) - 0.5) * 0.36
        _LAND = f
    return _LAND


SITES = dict(karoo=(0.485, 0.735), siberia=(0.645, 0.165))
GOND = [("Sudamérica", 0.385, 0.60), ("África", 0.475, 0.58), ("India", 0.575, 0.655), ("Antártida", 0.545, 0.80), ("Australia", 0.675, 0.745)]


def pangea(t, W, H, mode="valle", dur=10.0):
    z = 1.0 + 0.06 * t / dur
    f = cv2.resize(_land(), (W, H), interpolation=cv2.INTER_CUBIC)
    M = np.array([[z, 0, W / 2 * (1 - z)], [0, z, H / 2 * (1 - z)]], np.float32)
    f = cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    land = smoothstep(-0.01, 0.012, f)
    n = cv2.warpAffine(cv2.resize(_tex(9, 1.7), (W, H)), M, (W, H), borderMode=cv2.BORDER_REFLECT)
    sea = _base(W, H, (0.085, 0.125, 0.175), 5, 0.03) * (1 - 0.25 * smoothstep(-0.25, 0.0, f)[..., None]) + 0.05 * smoothstep(-0.10, 0.0, f)[..., None]
    gy, gx = np.gradient(cv2.GaussianBlur(n, (0, 0), W / 400) * W / 14)
    lc = lerp(np.array([0.42, 0.40, 0.34], np.float32), np.array([0.60, 0.56, 0.47], np.float32), n[..., None]) * np.clip(0.95 + 0.35 * (-gx - gy), 0.6, 1.4)[..., None]
    lat = cv2.warpAffine(np.abs((np.mgrid[0:H, 0:W][0] / H) - 0.5).astype(np.float32), M, (W, H), borderMode=cv2.BORDER_REPLICATE)
    lc = lerp(lc, np.array([0.40, 0.46, 0.38], np.float32), (smoothstep(0.10, 0.30, lat) * 0.45)[..., None])
    img = lerp(sea, lc, land[..., None])
    edge = smoothstep(0.03, 0.0, np.abs(f))
    img = img * (1 - 0.35 * edge[..., None])
    lay = _canvas(W, H)
    d = ImageDraw.Draw(lay)
    P = lambda x, y: ((W / 2 + (x * W - W / 2) * z), (H / 2 + (y * H - H / 2) * z))
    k = W / 1920
    for i in range(1, 6):                          # paralelos
        y = P(0, i / 6)[1] * SS
        d.line([(0, y), (W * SS, y)], fill=INK + (22,), width=SS)
    a_in = ease(t / 1.5)
    _text(d, (W * 0.06, H * 0.08), "PANGEA", 54 * k, weight="SemiBold", alpha=235 * a_in)
    _text(d, (W * 0.06, H * 0.08 + 66 * k), "hace 255 millones de años", 30 * k, weight="Regular", alpha=190 * a_in)
    if mode in ("valle", "siberia"):
        x, y = P(*SITES["karoo"])
        pul = 0.5 + 0.5 * np.sin(t * 3.0)
        r = (9 + 7 * pul) * k * SS
        d.ellipse([x * SS - r, y * SS - r, x * SS + r, y * SS + r], outline=AMBER + (int(200 * (1 - pul * 0.6)),), width=2 * SS)
        r = 6 * k * SS
        d.ellipse([x * SS - r, y * SS - r, x * SS + r, y * SS + r], fill=AMBER + (255,))
        _text(d, (x + 20 * k, y - 16 * k), "Cuenca del Karoo", 30 * k, AMBER, alpha=255 * ease((t - 1.5) / 1.2))
    if mode == "siberia":
        x, y = P(*SITES["siberia"])
        g = ease((t - 1.0) / (dur * 0.7))
        blot = np.exp(-(((np.mgrid[0:H, 0:W][1] - x) / (W * 0.085 * (0.25 + g))) ** 2 + ((np.mgrid[0:H, 0:W][0] - y) / (H * 0.10 * (0.25 + g))) ** 2))
        blot = blot * (0.6 + 0.8 * n) * land
        img = lerp(img, np.array([0.80, 0.30, 0.16], np.float32), np.clip(blot * 1.3 * g, 0, 0.85)[..., None])
        haze = np.exp(-(((np.mgrid[0:H, 0:W][1] - x) / (W * 0.40 * g + 1)) ** 2 + ((np.mgrid[0:H, 0:W][0] - y) / (H * 0.55 * g + 1)) ** 2))
        img = lerp(img, np.array([0.50, 0.44, 0.40], np.float32), (haze * 0.30 * g)[..., None])
        _text(d, (x + 30 * k, y - 60 * k), "Trampas Siberianas", 30 * k, RED, alpha=255 * ease((t - 2.0) / 1.2))
    if mode == "glosso":
        for i, (nm, gx_, gy_) in enumerate(GOND):
            a = ease((t - 1.0 - i * 0.7) / 1.0)
            x, y = P(gx_, gy_)
            _leaf_icon(d, x * SS, y * SS, 26 * k * SS, int(255 * a))
            _text(d, (x + 22 * k, y - 14 * k), nm, 26 * k, alpha=235 * a)
        _text(d, (W * 0.06, H * 0.86), "Glossopteris: la misma hoja en cinco continentes", 32 * k, AMBER, alpha=255 * ease((t - 4.5) / 1.2))
    return _finish(_merge(img, lay), t)


def _leaf_icon(d, x, y, L, alpha, col=AMBER):
    pts = []
    for u in np.linspace(0, 1, 12):
        pts.append((x + (u - 0.5) * L, y - np.sin(np.pi * u ** 0.8) * L * 0.2))
    for u in np.linspace(1, 0, 12):
        pts.append((x + (u - 0.5) * L, y + np.sin(np.pi * u ** 0.8) * L * 0.2))
    d.polygon(pts, fill=col + (int(alpha * 0.85),))
    d.line([(x - L / 2, y), (x + L / 2, y)], fill=(40, 30, 20, alpha), width=max(1, int(L * 0.03)))


# ------------------------------------------------------------------ cráneo
G_UP = [(0.00, 0.13), (0.01, 0.27), (0.12, 0.345), (0.30, 0.37), (0.52, 0.345), (0.78, 0.30), (0.95, 0.24), (1.00, 0.17), (1.00, 0.085),
        (0.86, 0.075), (0.62, 0.065), (0.40, 0.035), (0.22, 0.01), (0.10, 0.00), (0.03, 0.04)]
G_LO = [(0.07, -0.015), (0.30, -0.03), (0.60, -0.025), (0.90, -0.015), (0.975, -0.06), (0.955, -0.165), (0.86, -0.19), (0.60, -0.14),
        (0.32, -0.115), (0.12, -0.075), (0.05, -0.045)]
# mamífero generalizado (misma cantidad de puntos, para interpolar)
M_UP = [(0.00, 0.14), (0.00, 0.33), (0.12, 0.44), (0.32, 0.46), (0.52, 0.38), (0.76, 0.27), (0.94, 0.21), (1.00, 0.15), (1.00, 0.085),
        (0.86, 0.075), (0.62, 0.065), (0.42, 0.045), (0.26, 0.03), (0.14, 0.04), (0.04, 0.07)]
M_LO = [(0.12, 0.06), (0.30, -0.02), (0.60, -0.025), (0.90, -0.015), (0.965, -0.045), (0.94, -0.10), (0.86, -0.115), (0.60, -0.11),
        (0.32, -0.10), (0.16, -0.085), (0.10, 0.00)]


def _skull_layer(W, H, m=0.0, hl=None, labels=True, alpha=1.0, t=0.0, cx=0.5, cy=0.52, size=0.62):
    """m: 0 = gorgonópsido, 1 = mamífero. hl: 'fenestra' | 'dientes' | 'huesos' | None."""
    lay = _canvas(W, H)
    d = ImageDraw.Draw(lay)
    k = W / 1920
    L = W * size
    ox, oy = W * cx - L / 2, H * cy + L * 0.10
    P = lambda p: ((ox + p[0] * L) * SS, (oy - p[1] * L) * SS)
    up = [tuple(np.array(a) + (np.array(b) - np.array(a)) * m) for a, b in zip(G_UP, M_UP)]
    lo = [tuple(np.array(a) + (np.array(b) - np.array(a)) * m) for a, b in zip(G_LO, M_LO)]
    A = int(255 * alpha)
    bone = (196, 188, 168, int(70 * alpha))
    d.polygon([P(p) for p in lo], fill=bone)
    d.polygon([P(p) for p in up], fill=bone)
    lw = int(3.2 * k * SS) + 1
    d.line([P(p) for p in lo + lo[:1]], fill=INK + (A,), width=lw, joint="curve")
    d.line([P(p) for p in up + up[:1]], fill=INK + (A,), width=lw, joint="curve")

    def ell(c, rx, ry, **kw):
        x, y = P(c)
        d.ellipse([x - rx * L * SS, y - ry * L * SS, x + rx * L * SS, y + ry * L * SS], **kw)
    orb = (0.36 + 0.02 * m, 0.245 + 0.01 * m)
    ell(orb, 0.052, 0.050, fill=(18, 22, 28, int(220 * alpha)), outline=INK + (A,), width=lw)
    fen = (0.165 + 0.02 * m, 0.19 + 0.04 * m)
    glow = hl == "fenestra"
    pul = 0.6 + 0.4 * np.sin(t * 2.4)
    ell(fen, 0.085 * (1 + 0.35 * m), 0.058 * (1 + 0.5 * m), fill=(AMBER + (int(150 * pul * alpha),)) if glow else (18, 22, 28, int(200 * alpha)),
        outline=(AMBER if glow else INK) + (A,), width=lw)
    ell((0.955, 0.175), 0.016, 0.011, fill=(18, 22, 28, int(220 * alpha)))
    # dientes
    cols = dict(i=BLUE, c=AMBER, p=RED) if hl == "dientes" else dict(i=INK, c=INK, p=INK)

    def tooth(x, y0, ln, wd, col, up_=True):
        sgn = -1 if up_ else 1
        pts = [P((x - wd, y0)), P((x + wd, y0)), P((x + wd * 0.2, y0 + sgn * ln))]
        d.polygon(pts, fill=col + (A,))
    can = 0.215 * (1 - 0.72 * m)
    for x in (0.985, 0.955, 0.925, 0.895):
        tooth(x, 0.082, 0.045, 0.012, cols["i"])
    tooth(0.80, 0.075, can, 0.026, cols["c"])
    for x in (0.70, 0.655, 0.61, 0.565) + ((0.52, 0.475) if m > 0.5 else ()):
        tooth(x, 0.068, 0.022 + 0.02 * m, 0.011 + 0.008 * m, cols["p"])
    for x in (0.955, 0.93, 0.905):
        tooth(x, -0.02, 0.035, 0.010, cols["i"], False)
    tooth(0.865, -0.022, 0.06 * (1 - 0.4 * m), 0.015, cols["c"], False)
    for x in (0.70, 0.655, 0.61) + ((0.565, 0.52) if m > 0.5 else ()):
        tooth(x, -0.027, 0.02 + 0.015 * m, 0.010 + 0.008 * m, cols["p"], False)
    # huesos de la articulación: cuadrado (arriba) y articular (abajo)
    hb = hl in ("huesos", "oido")
    q0, a0 = np.array([0.085, 0.035]), np.array([0.105, -0.03])
    q1, a1 = np.array([0.150, 0.150]), np.array([0.175, 0.128])
    e = ease(m)
    q, a_ = q0 + (q1 - q0) * e, a0 + (a1 - a0) * e
    sz = 1 - 0.62 * e
    bc = (AMBER if hb else INK)
    fa = int((235 if hb else 90) * alpha)
    ell(tuple(q), 0.030 * sz, 0.040 * sz, fill=bc + (fa,), outline=INK + (A,), width=max(1, lw // 2))
    ell(tuple(a_), 0.040 * sz, 0.028 * sz, fill=(RED if hb else INK) + (fa,), outline=INK + (A,), width=max(1, lw // 2))
    if labels and hl == "fenestra":
        x, y = P(fen)
        _text(d, (x / SS - 40 * k, y / SS - L * 0.17), "abertura temporal: la marca de los sinápsidos", 30 * k, AMBER, alpha=A * ease((t - 1.0) / 1.0))
    if labels and hl == "dientes":
        for i, (txt, col, xx_) in enumerate((("incisivos", BLUE, 0.94), ("caninos", AMBER, 0.80), ("postcaninos", RED, 0.63))):
            x, y = P((xx_, 0.0))
            _text(d, (x / SS, oy + L * 0.27), txt, 30 * k, col, anchor="ma", alpha=A * ease((t - 0.8 - i * 0.9) / 0.8))
    return lay, (P(tuple(q)), P(tuple(a_)))


def skull(t, W, H, mode="fenestra", dur=10.0):
    img = _base(W, H)
    z = 0.60 + 0.03 * t / dur
    lay, _ = _skull_layer(W, H, 0.0, mode, True, ease(t / 1.2), t, size=z)
    lay2 = _canvas(W, H)
    _text(ImageDraw.Draw(lay2), (W * 0.06, H * 0.08), "Gorgonops torvus · cráneo, vista lateral", 30 * W / 1920, weight="Regular", italic=False, alpha=170)
    return _finish(_merge(_merge(img, lay), lay2), t)


STAGES = [(0.0, "Terápsido del Pérmico", "255 Ma"), (0.34, "Cinodonte temprano", "250 Ma"), (0.68, "Cinodonte avanzado", "225 Ma"), (1.0, "Mamífero", "hoy")]


def jaw_to_ear(t, W, H, dur=40.0):
    img = _base(W, H)
    u = np.clip((t - 3.0) / (dur - 12.0), 0, 1)
    m = ease(u)
    lay, (q, a) = _skull_layer(W, H, m, "oido", False, 1.0, t, size=0.58)
    d = ImageDraw.Draw(lay)
    k = W / 1920
    i = int(np.argmin([abs(m - s[0]) for s in STAGES]))
    _text(d, (W * 0.06, H * 0.08), STAGES[i][1], 44 * k, weight="SemiBold")
    _text(d, (W * 0.06, H * 0.08 + 56 * k), STAGES[i][2], 30 * k, weight="Regular", alpha=190)
    x0, x1, y = W * 0.06, W * 0.94, H * 0.90
    d.line([(x0 * SS, y * SS), (x1 * SS, y * SS)], fill=INK + (90,), width=SS)
    xm = x0 + (x1 - x0) * m
    d.ellipse([(xm - 7 * k) * SS, (y - 7 * k) * SS, (xm + 7 * k) * SS, (y + 7 * k) * SS], fill=AMBER + (255,))
    fa = 255 * ease((t - (dur - 8.0)) / 1.5)
    if fa > 0:
        _text(d, (q[0] / SS + 26 * k, q[1] / SS - 46 * k), "yunque", 30 * k, AMBER, alpha=fa)
        _text(d, (a[0] / SS + 30 * k, a[1] / SS + 8 * k), "martillo", 30 * k, RED, alpha=fa)
        _text(d, (W * 0.5, H * 0.80), "los huesos de la mandíbula, dentro del oído", 32 * k, anchor="ma", alpha=fa)
    return _finish(_merge(img, lay), t)


# ------------------------------------------------------------------ árbol evolutivo
def tree(t, W, H, mode="corte", dur=14.0):
    img = _base(W, H)
    lay = _canvas(W, H)
    d = ImageDraw.Draw(lay)
    k = W / 1920
    X = lambda ma: (W * 0.08 + (310 - ma) / 310 * W * 0.80) * SS
    Y = lambda f: (H * (0.20 + 0.62 * f)) * SS
    lw = int(4 * k * SS)
    T = 310 - 60 * 0 - (310 - (0 if mode == "legado" else 150)) * ease(t / (dur * 0.55))      # frente de dibujo (Ma)
    for ma in (300, 250, 200, 150, 100, 50, 0):
        if mode != "legado" and ma < 150:
            continue
        d.line([(X(ma), Y(-0.08)), (X(ma), Y(1.06))], fill=INK + (26,), width=SS)
        _text(d, (X(ma) / SS, H * 0.92), f"{ma} Ma" if ma else "hoy", 22 * k, anchor="ma", alpha=120)
    xe = X(252)
    d.line([(xe, Y(-0.08)), (xe, Y(1.06))], fill=RED + (150,), width=2 * SS)
    _text(d, (xe / SS + 10 * k, H * 0.115), "extinción del final del Pérmico", 24 * k, RED, alpha=220)

    def seg(ma0, ma1, f0, f1, col=INK, a=255, w=lw):
        if T >= ma0:
            return
        e1 = max(ma1, T)
        fr = (ma0 - e1) / max(ma0 - ma1, 1e-6)
        d.line([(X(ma0), Y(f0)), (X(e1), Y(f0 + (f1 - f0) * min(1, fr * 1.6)))], fill=col + (a,), width=w)
        return e1 <= ma1 + 1e-6

    seg(308, 272, 0.50, 0.50)
    _text(d, (X(308) / SS, Y(0.50) / SS - 34 * k), "sinápsidos", 26 * k, alpha=210)
    seg(272, 262, 0.50, 0.20)
    seg(262, 201, 0.20, 0.20, a=150)
    _text(d, (X(262) / SS + 8 * k, Y(0.20) / SS - 32 * k), "dicinodontes", 24 * k, alpha=150 * (T < 262))
    seg(272, 265, 0.50, 0.42)
    hot = mode in ("corte", "heredero")
    done = seg(265, 252, 0.42, 0.42, col=RED if hot else INK)
    _text(d, (X(266) / SS, Y(0.42) / SS - 34 * k), "gorgonópsidos", 26 * k, RED if hot else INK, alpha=235 * (T < 265))
    if done:
        x, y = X(252), Y(0.42)
        r = 13 * k * SS
        d.line([(x - r, y - r), (x + r, y + r)], fill=RED + (255,), width=lw)
        d.line([(x - r, y + r), (x + r, y - r)], fill=RED + (255,), width=lw)
    seg(272, 262, 0.50, 0.62)
    seg(262, 245, 0.62, 0.62, a=150)
    _text(d, (X(262) / SS + 8 * k, Y(0.62) / SS + 6 * k), "terocéfalos", 24 * k, alpha=150 * (T < 262))
    hc = AMBER if mode in ("heredero", "legado") else INK
    seg(272, 260, 0.50, 0.80, col=hc)
    seg(260, 150 if mode != "legado" else 205, 0.80, 0.80, col=hc)
    _text(d, (X(259) / SS, Y(0.80) / SS + 8 * k), "cinodontes", 26 * k, hc, alpha=235 * (T < 260))
    if mode == "legado":
        groups = ["monotremas", "marsupiales", "armadillos y perezosos", "elefantes y manatíes", "roedores", "conejos", "primates",
                  "musarañas y topos", "murciélagos", "carnívoros", "caballos y rinocerontes", "ciervos y vacas", "ballenas y delfines"]
        _text(d, (X(204) / SS, Y(0.80) / SS + 8 * k), "mamíferos", 26 * k, AMBER, alpha=235 * (T < 205))
        for i, g in enumerate(groups):
            f1 = -0.04 + 1.08 * i / (len(groups) - 1)
            st = 205 - 8 * abs(i - 6)
            seg(205, st, 0.80, 0.80, col=AMBER, w=max(SS, lw // 2))
            if seg(st, 0, 0.80, f1, col=AMBER, w=max(SS, lw // 2)):
                pass
            _text(d, (X(0) / SS + 12 * k, Y(f1) / SS - 13 * k), g, 21 * k, alpha=230 * (T < 12))
    return _finish(_merge(img, lay), t)


# ------------------------------------------------------------------ láminas sobre roca
def fossil(t, W, H, dur=9.0):
    """Cráneo fósil en la roca del Karoo (cómo lo sabemos)."""
    rock = _base(W, H, (0.36, 0.34, 0.32), 21, 0.06)
    n = cv2.resize(_tex(22, 1.3), (W, H))
    gy, gx = np.gradient(cv2.GaussianBlur(n, (0, 0), W / 500) * W / 30)
    rock = rock * np.clip(0.95 + 0.4 * (-gx - gy), 0.6, 1.4)[..., None]
    lay, _ = _skull_layer(W, H, 0.0, None, False, 1.0, t, size=0.60 + 0.04 * t / dur)
    a = np.asarray(lay.resize((W, H), Image.LANCZOS), np.float32) / 255.0
    m = cv2.GaussianBlur(a[..., 3], (0, 0), 2.0)
    bone = np.array([0.66, 0.60, 0.50], np.float32) * (0.7 + 0.6 * n[..., None])
    sh = np.roll(m, (4, 4), (0, 1))
    img = rock * (1 - 0.35 * np.clip(sh - m, 0, 1))[..., None]
    img = lerp(img, bone, (np.clip(m * 1.6, 0, 1) * 0.85)[..., None])
    lay2 = _canvas(W, H)
    k = W / 1920
    d = ImageDraw.Draw(lay2)
    _text(d, (W * 0.06, H * 0.84), "Gorgonops torvus", 40 * k, italic=True, alpha=255 * ease((t - 1.5) / 1.2))
    _text(d, (W * 0.06, H * 0.84 + 50 * k), "descrito por Richard Owen, 1876 · cuenca del Karoo, Sudáfrica", 26 * k, weight="Regular", alpha=200 * ease((t - 2.2) / 1.2))
    return _finish(_merge(img, lay2), t)


def leaf_fossil(t, W, H, dur=7.0):
    rock = _base(W, H, (0.40, 0.37, 0.33), 31, 0.06)
    n = cv2.resize(_tex(32, 1.3), (W, H))
    lay = Image.new("L", (W * SS, H * SS), 0)
    d = ImageDraw.Draw(lay)
    cx, cy, L = W * 0.5 * SS, H * 0.5 * SS, W * 0.50 * SS * (1 + 0.04 * t / dur)
    ang = -0.35
    ca, sa = np.cos(ang), np.sin(ang)
    Pt = lambda u, v: (cx + (u - 0.5) * L * ca - v * L * sa, cy + (u - 0.5) * L * sa + v * L * ca)
    us = np.linspace(0, 1, 40)
    hw = 0.115 * np.sin(np.pi * us ** 0.75) ** 0.85
    d.polygon([Pt(u, -h) for u, h in zip(us, hw)] + [Pt(u, h) for u, h in zip(us[::-1], hw[::-1])], fill=150)
    d.line([Pt(-0.08, 0), Pt(1.0, 0)], fill=255, width=int(5 * SS))
    for u in np.linspace(0.04, 0.96, 46):       # nervadura reticulada característica
        h = 0.115 * np.sin(np.pi * u ** 0.75) ** 0.85
        for sgn in (-1, 1):
            d.line([Pt(u, 0), Pt(u + 0.035, sgn * h * 0.55), Pt(u + 0.085, sgn * h)], fill=215, width=SS)
    m = np.asarray(lay.resize((W, H), Image.LANCZOS), np.float32) / 255.0
    gy, gx = np.gradient(cv2.GaussianBlur(m, (0, 0), 1.2) * 10 + cv2.GaussianBlur(n, (0, 0), W / 500) * W / 30)
    img = rock * np.clip(0.95 + 0.4 * (-gx - gy), 0.55, 1.45)[..., None]
    img = lerp(img, np.array([0.27, 0.22, 0.17], np.float32), (m * 0.55)[..., None])
    lay2 = _canvas(W, H)
    _text(ImageDraw.Draw(lay2), (W * 0.06, H * 0.86), "hoja fósil de Glossopteris", 30 * W / 1920, weight="Regular", alpha=210 * ease((t - 1.0) / 1.0))
    return _finish(_merge(img, lay2), t)


def prints(t, W, H, dur=12.0):
    """Huella de cinco dedos en el barro que se funde con una mano humana."""
    mud = _base(W, H, (0.37, 0.33, 0.29), 41, 0.05)
    n = cv2.resize(_tex(42, 1.4), (W, H))

    def mask(kind):
        lay = Image.new("L", (W * SS, H * SS), 0)
        d = ImageDraw.Draw(lay)
        cx, cy, s = W * 0.5 * SS, H * 0.56 * SS, H * 0.26 * SS

        def cap(x0, y0, x1, y1, r):
            d.line([(cx + x0 * s, cy + y0 * s), (cx + x1 * s, cy + y1 * s)], fill=255, width=int(2 * r * s))
            for (x, y) in ((x0, y0), (x1, y1)):
                d.ellipse([cx + (x - r) * s, cy + (y - r) * s, cx + (x + r) * s, cy + (y + r) * s], fill=255)
        if kind == "pata":
            d.ellipse([cx - 0.55 * s, cy - 0.35 * s, cx + 0.55 * s, cy + 0.65 * s], fill=255)
            for i, a in enumerate(np.linspace(-0.85, 0.85, 5)):
                ln = 0.62 + 0.14 * np.cos(a * 1.4)
                cap(np.sin(a) * 0.45, -np.cos(a) * 0.40, np.sin(a) * (0.45 + ln * 0.75), -np.cos(a) * (0.40 + ln * 0.75), 0.13)
                cap(np.sin(a) * (0.55 + ln * 0.85), -np.cos(a) * (0.50 + ln * 0.85), np.sin(a) * (0.60 + ln * 0.98), -np.cos(a) * (0.55 + ln * 0.98), 0.04)
        else:
            d.rounded_rectangle([cx - 0.55 * s, cy - 0.30 * s, cx + 0.50 * s, cy + 0.80 * s], radius=int(0.3 * s), fill=255)
            for x, ln in ((-0.42, 0.85), (-0.14, 1.05), (0.14, 1.12), (0.40, 0.98)):
                cap(x, -0.25, x * 1.12, -0.25 - ln, 0.12)
            cap(-0.50, 0.25, -1.02, -0.22, 0.13)
        return cv2.GaussianBlur(np.asarray(lay.resize((W, H), Image.LANCZOS), np.float32) / 255.0, (0, 0), 3.0)
    key = ("prints", W)
    if key not in _TEX:
        _TEX[key] = (mask("pata"), mask("mano"))
    a, b = _TEX[key]
    u = ease((t - dur * 0.38) / (dur * 0.25))
    m = a * (1 - u) + b * u
    gy, gx = np.gradient(-m * 26 + cv2.GaussianBlur(n, (0, 0), W / 500) * W / 34)
    img = mud * np.clip(0.92 + 0.5 * (-gx - gy), 0.5, 1.5)[..., None] * (1 - 0.30 * m)[..., None]
    lay2 = _canvas(W, H)
    d = ImageDraw.Draw(lay2)
    k = W / 1920
    _text(d, (W * 0.5, H * 0.88), "cinco dedos" , 32 * k, anchor="ma", alpha=220 * ease((t - 1.0) / 1.0))
    return _finish(_merge(img, lay2), t)


# ------------------------------------------------------------------ títulos, citas, créditos
def title(t, W, H, dur=8.0, main="GORGONOPS", sub="lo que el barro recuerda"):
    img = np.zeros((H, W, 3), np.float32) + np.array(BG, np.float32) * 0.35
    lay = _canvas(W, H)
    d = ImageDraw.Draw(lay)
    k = W / 1920
    a = ease(t / 1.6) * ease((dur - t) / 1.2)
    f = engine.font(int(120 * k * SS), "SemiBold")
    d.text((W / 2 * SS, H * 0.44 * SS), "  ".join(main), font=f, fill=INK + (int(255 * a),), anchor="mm")
    _text(d, (W / 2, H * 0.58), sub, 44 * k, weight="Regular", italic=True, anchor="mm", alpha=220 * a)
    return _finish(_merge(img, lay), t)


def credits(t, W, H, dur=16.0):
    img = np.zeros((H, W, 3), np.float32) + np.array(BG, np.float32) * 0.30
    lay = _canvas(W, H)
    d = ImageDraw.Draw(lay)
    k = W / 1920
    a = ease(t / 1.5) * ease((dur - t) / 1.5)
    rows = [("GORGONOPS · lo que el barro recuerda", 44, "SemiBold"), ("", 20, "Regular"),
            ("Imagen, animación y música generadas por código", 28, "Regular"), ("", 14, "Regular"),
            ("Citas: K. Angielczyk (Field Museum) · M. Whitney (Univ. de Washington)", 26, "Regular"),
            ("P. Viglietti (Field Museum) · C. Kammerer (N.C. Museum of Natural Sciences)", 26, "Regular"),
            ("C. Darwin, On the Origin of Species, 1859", 26, "Regular"), ("", 14, "Regular"),
            ("Kammerer et al. 2023, Current Biology · Matamales-Andreu et al. 2024, Nature Communications", 22, "Regular"),
            ("Whitney, Mose y Sidor 2016, JAMA Oncology", 22, "Regular"), ("", 14, "Regular"),
            ("Música: «Lo que el barro recuerda», tango original", 26, "Regular"),
            ("Las reconstrucciones de color, piel y conducta son hipótesis", 24, "Regular")]
    y = H * 0.20
    for txt, sz, wt in rows:
        if txt:
            _text(d, (W / 2, y), txt, sz * k, weight=wt, anchor="ma", alpha=(245 if wt == "SemiBold" else 205) * a)
        y += sz * k * 1.75
    return _finish(_merge(img, lay), t)


def quote_overlay(img, t, dur, name, role, en, es):
    """Cita compuesta sobre la imagen viva (oscurecida y desenfocada). img float (H,W,3)."""
    H, W = img.shape[:2]
    k = W / 1920
    a = ease(t / 1.0) * ease((dur - t) / 1.0)
    if a <= 0:
        return img
    dim = cv2.GaussianBlur(img, (0, 0), 9 * k) * 0.42
    img = img * (1 - a) + dim * a
    lay = _canvas(W, H)
    d = ImageDraw.Draw(lay)

    def wrap(txt, f, maxw):
        out, cur = [], ""
        for w_ in txt.split():
            if d.textlength((cur + " " + w_).strip(), font=f) > maxw:
                out.append(cur)
                cur = w_
            else:
                cur = (cur + " " + w_).strip()
        return out + [cur]
    f1 = engine.font(int(50 * k * SS), "Medium", True)
    f2 = engine.font(int(34 * k * SS), "Regular")
    y = H * 0.25 * SS
    for ln in wrap("«" + en + "»", f1, W * 0.74 * SS):
        d.text((W * 0.13 * SS, y), ln, font=f1, fill=INK + (int(255 * a),))
        y += 66 * k * SS
    y += 18 * k * SS
    for ln in wrap(es, f2, W * 0.74 * SS):
        d.text((W * 0.13 * SS, y), ln, font=f2, fill=INK + (int(200 * a),))
        y += 46 * k * SS
    y += 30 * k * SS
    d.line([(W * 0.13 * SS, y), (W * 0.19 * SS, y)], fill=AMBER + (int(255 * a),), width=int(3 * SS))
    y += 22 * k * SS
    d.text((W * 0.13 * SS, y), name, font=engine.font(int(36 * k * SS), "SemiBold"), fill=AMBER + (int(255 * a),))
    d.text((W * 0.13 * SS, y + 48 * k * SS), role, font=engine.font(int(28 * k * SS), "Regular"), fill=INK + (int(190 * a),))
    return _merge(img, lay)


def odontoma(t, W, H, dur=12.0):
    """Esquema de un corte delgado: raíz del canino rodeada de dientecillos (odontoma compuesto)."""
    img = _base(W, H, (0.07, 0.075, 0.085), 51, 0.03)
    n = cv2.resize(_tex(52, 1.5), (W, H))
    z = 1.0 + 0.07 * t / dur
    lay = _canvas(W, H)
    d = ImageDraw.Draw(lay)
    k = W / 1920
    cx, cy = W * 0.46 * SS, H * 0.50 * SS

    def ring(x, y, r, pulp=0.38, a=255, col=(214, 200, 168)):
        d.ellipse([x - r, y - r, x + r, y + r], fill=col + (a,))
        for q in (0.86, 0.72, 0.58):
            d.ellipse([x - r * q, y - r * q, x + r * q, y + r * q], outline=(150, 132, 100, int(a * 0.5)), width=max(1, int(SS * k)))
        d.ellipse([x - r * pulp, y - r * pulp, x + r * pulp, y + r * pulp], fill=(40, 30, 28, a))
    R = H * 0.30 * SS * z
    d.ellipse([cx - R * 2.3, cy - R * 1.55, cx + R * 2.3, cy + R * 1.55], fill=(120, 104, 84, 150))       # hueso de la mandíbula
    ring(cx - R * 0.35, cy, R)
    rs = np.random.default_rng(4)
    for i in range(9):
        a = ease((t - 1.5 - i * 0.35) / 0.8)
        ang = -0.9 + i * 0.26 + rs.normal(0, 0.05)
        rr = R * (1.38 + 0.22 * rs.uniform())
        ring(cx - R * 0.35 + np.cos(ang) * rr, cy + np.sin(ang) * rr * 0.9, R * rs.uniform(0.10, 0.17), 0.3, int(255 * a), (232, 205, 150))
    _text(d, (W * 0.06, H * 0.08), "Odontoma compuesto", 44 * k, weight="SemiBold")
    _text(d, (W * 0.06, H * 0.08 + 56 * k), "gorgonópsido de Tanzania · 255 Ma · esquema de un corte delgado", 28 * k, weight="Regular", alpha=190)
    _text(d, (W * 0.70, H * 0.36), "dientecillos", 30 * k, AMBER, alpha=255 * ease((t - 4.5) / 1.0))
    _text(d, (W * 0.30, H * 0.80), "raíz del canino", 30 * k, alpha=220 * ease((t - 1.0) / 1.0))
    img = _merge(img, lay) * (0.9 + 0.2 * n[..., None])
    return _finish(img, t)


def burrow(t, W, H, dur=16.0):
    """Madriguera en corte: Thrinaxodon enroscado bajo tierra tras la extinción."""
    import world
    import creature as C
    n = cv2.resize(_tex(61, 1.6), (W, H))
    n2 = cv2.resize(_tex(62, 2.4), (W, H))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    surf = H * (0.20 + 0.02 * (n2[0:1, :] - 0.5))
    strata = 0.5 + 0.5 * np.sin((yy + 60 * n2) / H * 38)
    earth = lerp(np.array([0.30, 0.25, 0.21], np.float32), np.array([0.43, 0.37, 0.31], np.float32), (0.55 * n + 0.45 * strata)[..., None])
    sky = np.array([0.80, 0.78, 0.74], np.float32) * (0.9 + 0.1 * (1 - yy / (H * 0.2)))[..., None]
    img = np.where((yy < surf)[..., None], sky, earth * (1 - 0.35 * np.clip((yy - surf) / H, 0, 1))[..., None])
    # túnel y cámara
    lay = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(lay)
    pts = [(W * (0.86 - 0.34 * u), H * (0.19 + 0.47 * u ** 0.8) + H * 0.03 * np.sin(u * 5)) for u in np.linspace(0, 1, 24)]
    d.line(pts, fill=255, width=int(H * 0.085), joint="curve")
    cx, cy = W * 0.44, H * 0.70
    d.ellipse([cx - W * 0.17, cy - H * 0.115, cx + W * 0.17, cy + H * 0.115], fill=255)
    hole = cv2.GaussianBlur(np.asarray(lay, np.float32) / 255.0, (0, 0), 2.5)
    img = lerp(img, np.array([0.085, 0.07, 0.06], np.float32) * (0.8 + 0.5 * n[..., None]), hole[..., None])
    cam = world.Camera(W, H, W * 1.75, (0, 0.20, 0), 0.0, 0.0)
    world.SUN_COL = np.array([0.55, 0.50, 0.44], np.float32)
    world.SKY_AMB = np.array([0.36, 0.33, 0.30], np.float32)
    spr = C.render(C.THRINAXODON, cam, (0, 0, 3.0), np.pi * 0.93, dict(phase=0, walk=0.0, t=t, crouch=0.95, curl=0.35, head_dy=-0.16, head_pitch=0.2, tail_amp=0.2), ss=2.0)
    h, w = spr["a"].shape
    x0, y0 = int(cx - w / 2), int(cy + H * 0.10 - h)
    engine._put(img, spr["rgb"], spr["a"], x0, y0)
    lay2 = _canvas(W, H)
    k = W / 1920
    dd = ImageDraw.Draw(lay2)
    _text(dd, (W * 0.06, H * 0.86), "Thrinaxodon", 40 * k, italic=True, alpha=255 * ease((t - 1.5) / 1.2))
    _text(dd, (W * 0.06, H * 0.86 + 50 * k), "Triásico temprano · cuenca del Karoo", 26 * k, weight="Regular", alpha=200 * ease((t - 2.2) / 1.2))
    return _finish(_merge(img, lay2), t)
