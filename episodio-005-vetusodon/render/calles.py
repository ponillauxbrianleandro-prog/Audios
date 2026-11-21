"""Carteles de calle (v10): apertura con muchas más fotos, placa de datos, revelado y cierre.

Composiciones dibujadas por código: muro de ladrillo, poste, cartel ONE WAY, semáforo peatonal ámbar con figura blanca, disco de
«prohibido el paso», PARE, cruce peatonal, límite de velocidad y cartel azul. Sin logos reales (formas genéricas).

  montaje_calle(t, W, H, tomas, cortes, seed)   -> ráfaga de fotos pegadas en el muro (cortes de 0,45–0,75 s, SIN destellos)
  placa_datos(t, W, H, items)                   -> solo datos (fechas a. C., km², etc.), aparecen en secuencia
  intro(t, W, H, dur, tomas, tB, items)         -> montaje hasta tB y placa de datos después (la placa dura ≤ 4 s)
  revelado(img, t, dur)                         -> panel oscuro que se abre y aclara sobre el documental
  cierre(t, W, H, dur, hitos)                   -> carteles de suscripción, like, más videos, miembros, gracias, adiós
"""
import numpy as np
import cv2
from PIL import Image, ImageDraw

import engine

NEGRO = (14, 14, 18)
BLANCO = (247, 243, 234)
ROJO = (200, 38, 58)
ROJO_D = (122, 20, 38)
AMBAR = (214, 158, 44)
AZUL = (24, 78, 168)
AMARILLO = (240, 196, 36)


def F(size, w="Bold"):
    return engine.font(max(8, int(size)), w)


def ease(x):
    x = float(np.clip(x, 0, 1))
    return x * x * (3 - 2 * x)


def pop(x):
    """Entrada con leve rebote."""
    x = float(np.clip(x, 0, 1))
    return 1 - (1 - x) ** 3 * np.cos(x * 6.0) * (1 - x) if x < 1 else 1.0


# ------------------------------------------------------------------ pictogramas
def figura(d, cx, cy, h, col=BLANCO, paso=0):
    """Peatón caminando (semáforo). paso 0/1 alterna las piernas."""
    s = h / 100.0
    d.ellipse([cx - 9 * s, cy - 48 * s, cx + 9 * s, cy - 30 * s], fill=col)
    d.line([(cx, cy - 28 * s), (cx - 3 * s, cy + 6 * s)], fill=col, width=int(11 * s))
    a = 16 * s if paso == 0 else -16 * s
    d.line([(cx - 3 * s, cy + 6 * s), (cx - 3 * s + a, cy + 44 * s)], fill=col, width=int(9 * s))
    d.line([(cx - 3 * s, cy + 6 * s), (cx - 3 * s - a, cy + 44 * s)], fill=col, width=int(9 * s))
    d.line([(cx - 1 * s, cy - 24 * s), (cx - 20 * s * (1 if paso == 0 else -1), cy - 2 * s)], fill=col, width=int(8 * s))
    d.line([(cx - 1 * s, cy - 24 * s), (cx + 18 * s * (1 if paso == 0 else -1), cy - 4 * s)], fill=col, width=int(8 * s))


def semaforo(d, x, y, w, h, paso=0):
    d.rounded_rectangle([x, y, x + w, y + h], radius=int(w * 0.08), fill=AMBAR, outline=(150, 105, 24), width=max(3, int(w * 0.03)))
    pad = w * 0.12
    d.rounded_rectangle([x + pad, y + pad, x + w - pad, y + h - pad], radius=int(w * 0.05), fill=NEGRO)
    figura(d, x + w / 2, y + h / 2 + h * 0.02, h * 0.58, BLANCO, paso)


def one_way(d, x, y, w, h, texto="ONE WAY", dir=-1):
    d.rounded_rectangle([x, y, x + w, y + h], radius=int(h * 0.08), fill=NEGRO, outline=BLANCO, width=max(3, int(h * 0.04)))
    m = h * 0.14
    if dir < 0:
        pts = [(x + m, y + h / 2), (x + w * 0.20, y + m * 1.2), (x + w * 0.20, y + h * 0.30), (x + w - m, y + h * 0.30),
               (x + w - m, y + h * 0.70), (x + w * 0.20, y + h * 0.70), (x + w * 0.20, y + h - m * 1.2)]
    else:
        pts = [(x + w - m, y + h / 2), (x + w * 0.80, y + m * 1.2), (x + w * 0.80, y + h * 0.30), (x + m, y + h * 0.30),
               (x + m, y + h * 0.70), (x + w * 0.80, y + h * 0.70), (x + w * 0.80, y + h - m * 1.2)]
    d.polygon(pts, fill=BLANCO)
    d.text((x + w * (0.60 if dir < 0 else 0.40), y + h / 2), texto, font=F(h * 0.30), fill=NEGRO, anchor="mm")


def disco_prohibido(d, cx, cy, r):
    d.ellipse([cx - r * 1.07, cy - r * 1.07, cx + r * 1.07, cy + r * 1.07], fill=BLANCO)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ROJO)
    d.rectangle([cx - r * 0.80, cy - r * 0.17, cx + r * 0.80, cy + r * 0.17], fill=BLANCO)


def pare(d, cx, cy, r, texto="PARE"):
    pts = [(cx + r * np.cos(np.pi / 8 + k * np.pi / 4), cy + r * np.sin(np.pi / 8 + k * np.pi / 4)) for k in range(8)]
    d.polygon(pts, fill=BLANCO)
    pts2 = [(cx + r * 0.92 * np.cos(np.pi / 8 + k * np.pi / 4), cy + r * 0.92 * np.sin(np.pi / 8 + k * np.pi / 4)) for k in range(8)]
    d.polygon(pts2, fill=ROJO)
    d.text((cx, cy), texto, font=F(r * 0.55), fill=BLANCO, anchor="mm")


def rombo(d, cx, cy, r, paso=0):
    d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=NEGRO)
    d.polygon([(cx, cy - r * 0.93), (cx + r * 0.93, cy), (cx, cy + r * 0.93), (cx - r * 0.93, cy)], fill=AMARILLO)
    figura(d, cx, cy + r * 0.05, r * 0.95, NEGRO, paso)


def limite(d, cx, cy, r, texto="252"):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ROJO)
    d.ellipse([cx - r * 0.78, cy - r * 0.78, cx + r * 0.78, cy + r * 0.78], fill=BLANCO)
    d.text((cx, cy), texto, font=F(r * 0.78), fill=NEGRO, anchor="mm")


def cartel_azul(d, x, y, w, h, texto, dir=1):
    d.rounded_rectangle([x, y, x + w, y + h], radius=int(h * 0.1), fill=AZUL, outline=BLANCO, width=max(3, int(h * 0.04)))
    d.text((x + w * 0.45, y + h / 2), texto, font=F(h * 0.38), fill=BLANCO, anchor="mm")
    ax = x + w * 0.88
    d.polygon([(ax - h * 0.18, y + h * 0.30), (ax + h * 0.18, y + h / 2), (ax - h * 0.18, y + h * 0.70)], fill=BLANCO)


def poste(d, x, y0, y1, w):
    d.rectangle([x, y0, x + w, y1], fill=(110, 112, 118))
    d.rectangle([x, y0, x + w * 0.25, y1], fill=(150, 152, 158))
    d.rectangle([x + w * 0.80, y0, x + w, y1], fill=(70, 72, 78))
    for yy in np.linspace(y0 + (y1 - y0) * 0.15, y1 - (y1 - y0) * 0.1, 3):
        d.rectangle([x - 3, yy, x + w + 3, yy + w * 0.14], fill=(86, 88, 94))


# ------------------------------------------------------------------ fondos
_BG = {}
TINTE = [(1.0, 1.0, 1.0), (1.25, 0.8, 0.75), (0.75, 0.9, 1.25), (0.8, 1.15, 0.85), (1.15, 1.0, 0.8), (1.0, 0.85, 1.15)]


def pared(W, H, v):
    rng = np.random.default_rng(100 + v)
    im = Image.new("RGB", (W, H), (46, 28, 28))
    d = ImageDraw.Draw(im)
    bh, bw = int(H * 0.055), int(W * 0.095)
    for r in range(H // bh + 2):
        off = (r % 2) * bw // 2
        for c in range(-1, W // bw + 2):
            t = int(rng.integers(-16, 17))
            col = (int(np.clip(76 + t, 0, 255)), int(np.clip(40 + t // 2, 0, 255)), int(np.clip(40 + t // 2, 0, 255)))
            d.rectangle([c * bw + off + 3, r * bh + 3, c * bw + off + bw - 3, r * bh + bh - 3], fill=col)
    a = np.asarray(im).astype(np.float32) / 255.0 * np.array(TINTE[v % 6], np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a *= (0.90 - 0.30 * ((xx / W - 0.5) ** 2 + (yy / H - 0.45) ** 2) * 2.2)[..., None]
    a += cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), 1.2)[..., None] * 0.02
    return np.clip(a, 0, 1)


_PARED = {}


def fondo_pared(W, H, v):
    """Solo el muro de ladrillo (para placas y carteles que van al frente)."""
    key = (W, H, v)
    if key not in _PARED:
        _PARED[key] = pared(W, H, v)
    return _PARED[key]


def fondo_calle(W, H, v):
    """Composición de calle nº v (0..5). Devuelve (imagen float, rectángulo del cartel de fotos (x,y,w,h))."""
    key = (W, H, v)
    if key in _BG:
        return _BG[key]
    base = pared(W, H, v)
    im = Image.fromarray((base * 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    if v == 0:      # réplica de la referencia: ONE WAY arriba, poste, semáforo peatonal
        one_way(d, W * 0.03, H * 0.05, W * 0.37, H * 0.15)
        poste(d, W * 0.20, H * 0.20, H, W * 0.035)
        semaforo(d, W * 0.76, H * 0.60, W * 0.17, H * 0.36)
        slot = (W * 0.43, H * 0.10, W * 0.46, H * 0.46)
    elif v == 1:
        disco_prohibido(d, W * 0.15, H * 0.30, H * 0.20)
        poste(d, W * 0.15 - W * 0.0175, H * 0.50, H, W * 0.035)
        one_way(d, W * 0.04, H * 0.76, W * 0.30, H * 0.14, dir=1)
        slot = (W * 0.40, H * 0.14, W * 0.50, H * 0.50)
    elif v == 2:
        pare(d, W * 0.14, H * 0.22, H * 0.17)
        poste(d, W * 0.14 - W * 0.0175, H * 0.38, H, W * 0.035)
        semaforo(d, W * 0.07, H * 0.62, W * 0.14, H * 0.32)
        slot = (W * 0.34, H * 0.12, W * 0.55, H * 0.52)
    elif v == 3:
        rombo(d, W * 0.86, H * 0.24, H * 0.20)
        poste(d, W * 0.86 - W * 0.0175, H * 0.44, H, W * 0.035)
        one_way(d, W * 0.05, H * 0.78, W * 0.32, H * 0.13)
        slot = (W * 0.08, H * 0.10, W * 0.62, H * 0.58)
    elif v == 4:
        limite(d, W * 0.14, H * 0.24, H * 0.17, "252")
        poste(d, W * 0.14 - W * 0.0175, H * 0.41, H, W * 0.035)
        cartel_azul(d, W * 0.34, H * 0.78, W * 0.40, H * 0.14, "KAROO")
        slot = (W * 0.36, H * 0.10, W * 0.56, H * 0.52)
    else:
        one_way(d, W * 0.30, H * 0.04, W * 0.40, H * 0.14, dir=1)
        poste(d, W * 0.50 - W * 0.0175, H * 0.18, H, W * 0.035)
        semaforo(d, W * 0.78, H * 0.58, W * 0.16, H * 0.34)
        slot = (W * 0.05, H * 0.22, W * 0.40, H * 0.50)
    arr = np.asarray(im, np.float32) / 255.0
    _BG[key] = (arr, tuple(int(x) for x in slot))
    return _BG[key]


def _foto(arr, w, h, zoom):
    ih, iw = arr.shape[:2]
    s = max(w / iw, h / ih) * zoom
    r = cv2.resize(arr, (max(w, int(iw * s)), max(h, int(ih * s))), interpolation=cv2.INTER_AREA)
    y0, x0 = (r.shape[0] - h) // 2, (r.shape[1] - w) // 2
    return r[y0:y0 + h, x0:x0 + w]


def pegar_foto(img, foto, slot, zoom, ang):
    x, y, w, h = slot
    pad = max(6, int(w * 0.018))
    ph = _foto(foto, w - 2 * pad, h - 2 * pad, zoom)
    card = np.ones((h, w, 3), np.float32) * np.array(BLANCO, np.float32) / 255.0
    card[pad:h - pad, pad:w - pad] = ph
    big = np.zeros((int(h * 1.25), int(w * 1.25), 4), np.float32)
    oy, ox = (big.shape[0] - h) // 2, (big.shape[1] - w) // 2
    big[oy:oy + h, ox:ox + w, :3] = card
    big[oy:oy + h, ox:ox + w, 3] = 1
    R = cv2.getRotationMatrix2D((big.shape[1] / 2, big.shape[0] / 2), ang, 1.0)
    big = cv2.warpAffine(big, R, big.shape[1::-1], flags=cv2.INTER_LINEAR)
    cx, cy = x + w // 2, y + h // 2
    y0, x0 = cy - big.shape[0] // 2, cx - big.shape[1] // 2
    H, W = img.shape[:2]
    ya, xa, yb, xb = max(0, y0), max(0, x0), min(H, y0 + big.shape[0]), min(W, x0 + big.shape[1])
    sub = big[ya - y0:yb - y0, xa - x0:xb - x0]
    sh = cv2.GaussianBlur(sub[..., 3], (0, 0), W * 0.006)[..., None] * 0.45
    img[ya:yb, xa:xb] = img[ya:yb, xa:xb] * (1 - sh) * 1.0
    img[ya:yb, xa:xb] = img[ya:yb, xa:xb] * (1 - sub[..., 3:4]) + sub[..., :3] * sub[..., 3:4]
    return img


def cortes_calle(dur, seed=4, lo=0.45, hi=0.72):
    rng = np.random.default_rng(seed)
    t, out = 0.0, []
    while t < dur - 0.2:
        out.append(round(t * 24) / 24)
        t += float(rng.uniform(lo, hi))
    return out


def montaje_calle(t, W, H, tomas, cortes, seed=4, cada=3):
    """Ráfaga de fotos (una distinta en cada corte) sobre composiciones de calle que cambian cada `cada` cortes. Sin destellos."""
    k = max(0, int(np.searchsorted(cortes, t + 1e-6, side="right") - 1))
    t_in = t - cortes[k]
    v = (k // cada + seed) % 6
    fondo, slot = fondo_calle(W, H, v)
    img = fondo.copy()
    rng = np.random.default_rng(seed * 97 + k)
    foto = tomas[(k * 5 + seed * 3) % len(tomas)]
    zoom = 1.0 + 0.08 * min(t_in / 0.6, 1.0)
    img = pegar_foto(img, foto, slot, zoom, float(rng.uniform(-2.5, 2.5)))
    return np.clip(img, 0, 1)


# ------------------------------------------------------------------ placa de datos (≤ 4 s)
def placa_datos(t, W, H, items):
    """items: [(t_inicio, texto, color)]; cada placa entra deslizando desde la derecha. Solo datos."""
    fondo = fondo_pared(W, H, 0)
    img = fondo.copy() * 0.80
    im = Image.fromarray((img * 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    n = len(items)
    ph = H * 0.17
    gap = H * 0.035
    y0 = (H - (n * ph + (n - 1) * gap)) / 2
    for i, (ti, texto, col) in enumerate(items):
        u = ease((t - ti) / 0.22)
        if u <= 0:
            continue
        x = W * 0.05 + (1 - u) * W * 0.9
        y = y0 + i * (ph + gap)
        w = W * 0.66
        d.rounded_rectangle([x + 6, y + 8, x + w + 6, y + ph + 8], radius=int(ph * 0.12), fill=(8, 6, 8))
        d.rounded_rectangle([x, y, x + w, y + ph], radius=int(ph * 0.12), fill=col, outline=BLANCO, width=max(3, int(ph * 0.05)))
        d.text((x + w / 2, y + ph / 2), texto, font=F(ph * (0.42 if len(texto) < 22 else 0.33)), fill=BLANCO, anchor="mm")
    semaforo(d, W * 0.76, H * 0.30, W * 0.17, H * 0.40, paso=int(t * 4) % 2)
    return np.asarray(im, np.float32) / 255.0


def intro(t, W, H, dur, tomas, tB, items, seed=4, cortes=None):
    cortes = cortes or cortes_calle(tB, seed)
    if t < tB:
        return montaje_calle(t, W, H, tomas, cortes, seed)
    return placa_datos(t - tB, W, H, [(ti, tx, col) for ti, tx, col in items])


# ------------------------------------------------------------------ revelado
def revelado(img, t, dur=2.2, n=12):
    """Persianas oscuras que se abren (con la imagen aclarándose desde casi negro): el documental se va revelando."""
    if t >= dur:
        return img
    H, W = img.shape[:2]
    u = ease(t / dur)
    bright = 0.18 + 0.82 * u
    out = img * bright
    h = H / n
    base = np.array((26, 8, 14), np.float32) / 255.0
    for i in range(n):
        li = ease((t - 0.05 * (i % 6) - 0.10 * (i // 6)) / (dur * 0.85))        # cada persiana abre a su ritmo
        top, bot = int(i * h), int((i + 1) * h)
        cover = int((bot - top) * (1 - li))
        if cover > 0:
            mid = (top + bot) // 2
            y0, y1 = mid - cover // 2, mid + cover // 2
            out[y0:y1] = base * (0.9 + 0.1 * np.sin(i))
    return np.clip(out, 0, 1)


# ------------------------------------------------------------------ cierre
def icono(d, tipo, cx, cy, s, col=BLANCO):
    k = s / 100.0
    P = lambda pts: [(cx + (x - 50) * k, cy + (y - 50) * k) for x, y in pts]
    if tipo == "campana":
        d.polygon(P([(50, 8), (60, 14), (68, 32), (70, 58), (80, 70), (80, 78), (20, 78), (20, 70), (30, 58), (32, 32), (40, 14)]), fill=col)
        d.ellipse([cx - 8 * k, cy + 30 * k, cx + 8 * k, cy + 46 * k], fill=col)
    elif tipo == "like":
        d.polygon(P([(34, 46), (46, 46), (54, 18), (62, 10), (70, 17), (68, 38), (90, 38), (95, 46), (91, 56), (93, 64), (87, 72), (89, 80), (80, 90), (36, 90), (34, 84)]), fill=col)
        d.rectangle([cx + (8 - 50) * k, cy + (46 - 50) * k, cx + (28 - 50) * k, cy + (90 - 50) * k], fill=col)
    elif tipo == "estrella":
        pts = [(50 + 46 * np.cos(-np.pi / 2 + j * np.pi / 5) * (1 if j % 2 == 0 else 0.42), 52 + 46 * np.sin(-np.pi / 2 + j * np.pi / 5) * (1 if j % 2 == 0 else 0.42)) for j in range(10)]
        d.polygon(P(pts), fill=col)
    elif tipo == "play":
        d.polygon(P([(30, 18), (30, 82), (84, 50)]), fill=col)
    elif tipo == "lupa":
        d.ellipse([cx + (14 - 50) * k, cy + (10 - 50) * k, cx + (66 - 50) * k, cy + (62 - 50) * k], outline=col, width=max(3, int(9 * k)))
        d.line([(cx + (58 - 50) * k, cy + (58 - 50) * k), (cx + (88 - 50) * k, cy + (88 - 50) * k)], fill=col, width=max(4, int(11 * k)))


def placa(d, cx, cy, w, h, texto, col=NEGRO, tam=0.42):
    d.rounded_rectangle([cx - w / 2 + 6, cy - h / 2 + 8, cx + w / 2 + 6, cy + h / 2 + 8], radius=int(h * 0.14), fill=(8, 6, 8))
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=int(h * 0.14), fill=col, outline=BLANCO, width=max(3, int(h * 0.05)))
    d.text((cx, cy), texto, font=F(h * tam), fill=BLANCO, anchor="mm")


def cartel_cierre(t_in, W, H, tipo, texto):
    fondo = fondo_pared(W, H, {"suscribite": 1, "like": 2, "videos": 0, "miembros": 3, "gracias": 4, "chau": 5}.get(tipo, 0))
    im = Image.fromarray((fondo * 0.70 * 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    s = float(np.clip(0.80 + 0.20 * pop(t_in / 0.22), 0.5, 1.05))
    cx, cy = W / 2, H * 0.40
    R = H * 0.27 * s
    if tipo == "suscribite":
        d.ellipse([cx - R * 1.06, cy - R * 1.06, cx + R * 1.06, cy + R * 1.06], fill=BLANCO)
        d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=ROJO)
        icono(d, "campana", cx, cy, R * 1.3)
    elif tipo == "like":
        d.ellipse([cx - R * 1.06, cy - R * 1.06, cx + R * 1.06, cy + R * 1.06], fill=BLANCO)
        d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=AZUL)
        icono(d, "like", cx, cy, R * 1.3)
    elif tipo == "videos":
        bw, bh = W * 0.56 * s, H * 0.34 * s
        d.rounded_rectangle([cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2], radius=int(bh * 0.1), fill=NEGRO, outline=BLANCO, width=8)
        icono(d, "play", cx - bw * 0.18, cy, bh * 0.78, BLANCO)
        icono(d, "lupa", cx + bw * 0.20, cy, bh * 0.70, BLANCO)
    elif tipo == "miembros":
        rombo(d, cx, cy, R * 1.12, 0)
        icono(d, "estrella", cx, cy + R * 0.02, R * 1.0, NEGRO)
    elif tipo == "gracias":
        d.rounded_rectangle([W * 0.08, H * 0.22, W * 0.92, H * 0.60], radius=int(H * 0.04), fill=ROJO, outline=BLANCO, width=8)
        d.text((W / 2, H * 0.41), "¡MUCHAS GRACIAS!", font=F(H * 0.105 * s), fill=BLANCO, anchor="mm")
    elif tipo == "chau":
        semaforo(d, cx - W * 0.085, H * 0.06, W * 0.17, H * 0.42, paso=int(t_in * 4) % 2)
    if tipo == "chau":
        placa(d, W / 2, H * 0.62, W * 0.70, H * 0.12, "NOS VEMOS DENTRO DE", NEGRO, 0.46)
        placa(d, W / 2, H * 0.76, W * 0.78, H * 0.14, "252.000.000 DE AÑOS", ROJO, 0.52)
        placa(d, W / 2, H * 0.90, W * 0.30, H * 0.10, "ADIÓS", NEGRO, 0.55)
    elif tipo != "gracias":
        placa(d, W / 2, H * 0.80, W * 0.80, H * 0.17, texto, NEGRO if tipo != "suscribite" else ROJO_D, 0.40 if len(texto) < 26 else 0.30)
    return np.asarray(im, np.float32) / 255.0


def cierre(t, W, H, dur, hitos):
    """hitos: [(t_inicio, tipo, texto)] en orden; se muestra el último cuyo inicio ya pasó."""
    k = 0
    for i, (ti, _, _) in enumerate(hitos):
        if t >= ti:
            k = i
    ti, tipo, texto = hitos[k]
    img = cartel_cierre(t - ti, W, H, tipo, texto)
    if k == len(hitos) - 1:                                  # fundido a negro final
        img = img * float(np.clip((dur - t) / 1.2, 0, 1))
    return np.clip(img, 0, 1)
