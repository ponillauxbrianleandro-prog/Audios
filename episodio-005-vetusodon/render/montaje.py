"""Montaje «carteles de calle» (episodio 005).

Estética de señalética: fondo rojo plano, disco de «prohibido el paso» con la silueta negra del animal, flecha ONE WAY y
semáforo peatonal. SOLO una zona se mueve: la ventana de fotos, que cambia de toma en menos de un segundo con un clic de cámara.
Todo lo demás queda quieto. Un marco rojo nace en la esquina inferior derecha y se expande hacia la izquierda y un poco hacia
arriba; ahí aparece el texto corto con el dato (después de que la voz lo dijo).

  montaje(t, W, H, dur, tomas, cortes, textos, seed)      -> fotograma float32 RGB [0,1]
  cortes_de(dur, seed, lo, hi)                           -> instantes de corte (para sincronizar el clic de cámara)
"""
import numpy as np
import cv2
from PIL import Image, ImageDraw

import sombra as S

RED = tuple(c / 255 for c in S.RED)
RED_D = tuple(c / 255 for c in S.RED_D)
INK = tuple(c / 255 for c in S.BLACK)
PAPER = tuple(c / 255 for c in S.WHITE)

_BASE = {}


def cortes_de(dur, seed=1, lo=0.28, hi=0.78):
    """Instantes de corte: ninguna toma dura 1 s (entre `lo` y `hi` s, ritmo irregular)."""
    rng = np.random.default_rng(seed)
    t, out = 0.0, []
    while t < dur - 1e-6:
        out.append(round(t * 24) / 24)
        t += float(rng.uniform(lo, hi))
    return out


def _disco(d, cx, cy, r):
    d.ellipse([cx - r - r * 0.07, cy - r - r * 0.07, cx + r + r * 0.07, cy + r + r * 0.07], fill=S.WHITE)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=S.RED_L)
    d.rectangle([cx - r * 0.82, cy - r * 0.17, cx + r * 0.82, cy + r * 0.17], fill=S.WHITE)


def _flecha(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=S.BLACK, outline=S.WHITE, width=max(2, int(h * 0.04)))
    pts = [(x + w * 0.06, y + h * 0.5), (x + w * 0.30, y + h * 0.15), (x + w * 0.30, y + h * 0.38), (x + w * 0.92, y + h * 0.38),
           (x + w * 0.92, y + h * 0.62), (x + w * 0.30, y + h * 0.62), (x + w * 0.30, y + h * 0.85)]
    d.polygon(pts, fill=S.WHITE)
    f = S.F(int(h * 0.20), 1.0, "Bold")
    d.text((x + w * 0.60, y + h * 0.08), "ONE WAY", font=f, fill=S.WHITE, anchor="mm")


def _semaforo(d, x, y, w, h):
    d.rounded_rectangle([x, y, x + w, y + h], radius=int(w * 0.10), fill=S.BLACK, outline=(220, 170, 60), width=max(3, int(w * 0.05)))
    cx, cy = x + w * 0.5, y + h * 0.5
    d.ellipse([cx - w * 0.11, cy - h * 0.34, cx + w * 0.11, cy - h * 0.14], fill=S.WHITE)
    d.line([(cx, cy - h * 0.14), (cx - w * 0.02, cy + h * 0.10)], fill=S.WHITE, width=max(3, int(w * 0.07)))
    d.line([(cx - w * 0.02, cy + h * 0.10), (cx - w * 0.16, cy + h * 0.32)], fill=S.WHITE, width=max(3, int(w * 0.07)))
    d.line([(cx - w * 0.02, cy + h * 0.10), (cx + w * 0.12, cy + h * 0.32)], fill=S.WHITE, width=max(3, int(w * 0.07)))
    d.line([(cx, cy - h * 0.08), (cx - w * 0.17, cy + h * 0.04)], fill=S.WHITE, width=max(3, int(w * 0.06)))
    d.line([(cx, cy - h * 0.08), (cx + w * 0.17, cy - h * 0.00)], fill=S.WHITE, width=max(3, int(w * 0.06)))


def fondo(W, H, variante=0):
    """Cartel estático: disco con silueta, flecha y semáforo. Se calcula una vez por tamaño."""
    key = (W, H, variante)
    if key in _BASE:
        return _BASE[key]
    k = W / 1920.0
    im = Image.new("RGB", (W, H), S.RED)
    d = ImageDraw.Draw(im)
    # franjas de pared / asfalto y desgaste de pintura
    d.rectangle([0, int(H * 0.86), W, H], fill=S.RED_D)
    rng = np.random.default_rng(7 + variante)
    for _ in range(90):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        d.ellipse([x, y, x + rng.uniform(2, 9) * k, y + rng.uniform(2, 6) * k], fill=S.RED_L)
    # poste
    d.rectangle([int(W * 0.115), int(H * 0.50), int(W * 0.135), H], fill=(70, 70, 78))
    cx, cy, r = int(W * 0.125), int(H * 0.30), int(H * 0.22)
    _disco(d, cx, cy, r)
    sil_img, sil_mask = S._sil_img("vetusodon", 4, int(r * 1.35))
    im.paste(sil_img, (int(cx - sil_img.size[0] * 0.5), int(cy + r * 0.30 - sil_img.size[1] * 0.5)), sil_mask)
    d = ImageDraw.Draw(im)
    if variante % 2 == 0:
        _flecha(d, int(W * 0.035), int(H * 0.62), int(W * 0.19), int(H * 0.115))
    _semaforo(d, int(W * 0.905), int(H * 0.08), int(W * 0.065), int(H * 0.19))
    arr = np.asarray(im, np.float32) / 255.0
    _BASE[key] = arr
    return arr


def _foto(arr, w, h):
    ih, iw = arr.shape[:2]
    s = max(w / iw, h / ih)
    r = cv2.resize(arr, (int(iw * s) + 1, int(ih * s) + 1), interpolation=cv2.INTER_AREA)
    y0, x0 = (r.shape[0] - h) // 2, (r.shape[1] - w) // 2
    return r[y0:y0 + h, x0:x0 + w]


def _marco(img, t, dur_in, texto, W, H, compacto=False):
    """Marco rojo que nace en la esquina inferior derecha y se expande hacia la izquierda y un poco hacia arriba."""
    if t <= 0 or not texto:
        return img
    u = float(np.clip(t / dur_in, 0, 1))
    u = 1 - (1 - u) ** 3
    xr, yb = W * 0.965, H * 0.94
    xl = W * (0.50 if compacto else 0.12)
    x0 = xr - (xr - xl) * u                            # crece hacia la izquierda
    ytl = yb - (yb - H * (0.78 if compacto else 0.66)) * u     # esquina superior izquierda
    ytr = yb - (yb - H * (0.68 if compacto else 0.55)) * u     # esquina superior derecha más alta (inclinada hacia arriba)
    pts = [(x0, ytl), (xr, ytr), (xr, yb), (x0, yb)]
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(im, "RGBA")
    sh = [(x + 8, y + 10) for x, y in pts]
    d.polygon(sh, fill=(0, 0, 0, 90))
    d.polygon(pts, fill=S.RED + (255,))
    d.line(pts + [pts[0]], fill=S.WHITE + (255,), width=max(3, int(W * 0.004)), joint="curve")
    if u > 0.55:
        a = int(255 * np.clip((u - 0.55) / 0.35, 0, 1))
        size = int(H * (0.040 if compacto else 0.062) * (1.0 if len(texto) < 28 else 0.82))
        f = S.F(size, 1.0, "Bold")
        cx, cy = (x0 + xr) / 2, (min(ytl, ytr) + yb) / 2 + H * 0.01
        d.text((cx, cy), texto, font=f, fill=S.WHITE + (a,), anchor="mm")
    return np.asarray(im, np.float32) / 255.0


def montaje(t, W, H, dur, tomas, cortes=None, textos=(), seed=1, variante=0, **_):
    """tomas: lista de imágenes float RGB [0,1]; textos: [(t_inicio, texto)] (el marco abre en ese instante)."""
    img = fondo(W, H, variante).copy()
    cortes = cortes or cortes_de(dur, seed)
    k = int(np.searchsorted(cortes, t + 1e-6, side="right") - 1)
    k = max(k, 0)
    t_in = t - cortes[k]
    rng = np.random.default_rng(seed * 131 + k)
    foto = tomas[(k * 7 + seed) % len(tomas)]
    # ventana de fotos (lo único que se mueve), con inclinación leve y borde blanco tipo polaroid
    ww, hh = int(W * 0.60), int(H * 0.68)
    ph = _foto(foto, ww, hh)
    zoom = 1.0 + 0.10 * (t_in / 0.6)                                # empuje corto dentro de la toma
    M = cv2.getRotationMatrix2D((ww / 2, hh / 2), 0.0, zoom)
    ph = cv2.warpAffine(ph, M, (ww, hh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    pad = int(W * 0.011)
    card = np.ones((hh + 2 * pad + int(H * 0.05), ww + 2 * pad, 3), np.float32) * np.array(PAPER, np.float32)
    card[pad:pad + hh, pad:pad + ww] = ph
    ang = float(rng.uniform(-2.2, 2.2))
    ch, cw = card.shape[:2]
    big = np.zeros((int(max(ch, cw) * 1.3),) * 2 + (4,), np.float32)
    oy, ox = (big.shape[0] - ch) // 2, (big.shape[1] - cw) // 2
    big[oy:oy + ch, ox:ox + cw, :3] = card
    big[oy:oy + ch, ox:ox + cw, 3] = 1
    R = cv2.getRotationMatrix2D((big.shape[1] / 2, big.shape[0] / 2), ang, 1.0)
    big = cv2.warpAffine(big, R, big.shape[1::-1], flags=cv2.INTER_LINEAR)
    cx, cy = int(W * 0.60), int(H * 0.44)
    y0, x0 = cy - big.shape[0] // 2, cx - big.shape[1] // 2
    ya, xa, yb, xb = max(0, y0), max(0, x0), min(H, y0 + big.shape[0]), min(W, x0 + big.shape[1])
    sub = big[ya - y0:yb - y0, xa - x0:xb - x0]
    shadow = cv2.GaussianBlur(sub[..., 3], (0, 0), W * 0.006)[..., None] * 0.35
    img[ya:yb, xa:xb] = img[ya:yb, xa:xb] * (1 - shadow) * 1.0
    img[ya:yb, xa:xb] = img[ya:yb, xa:xb] * (1 - sub[..., 3:4]) + sub[..., :3] * sub[..., 3:4]
    # destello blanco en el instante exacto de cada corte (obturador)
    if t_in < 0.09:
        img = img + (1 - img) * (0.55 * (1 - t_in / 0.09))
    # marco rojo con el dato: abre en el instante indicado y queda hasta el final del bloque
    texto, tt = "", 0.0
    for t0, tx in textos:
        if t >= t0:
            texto, tt = tx, t - t0
    img = _marco(img, tt, 0.55, texto, W, H)
    return np.clip(img, 0, 1)


def marco_overlay(img, t, texto, W, H):
    """Marco rojo compacto para planos de naturaleza: nace en la esquina inferior derecha y se expande."""
    return _marco(img, t, 0.55, texto, W, H, compacto=True)


def cartel(t, W, H, dur, texto="ESTE CAMINO LLEVA A VOS", variante=1, **_):
    """Cartel final: flecha ONE WAY, semáforo peatonal y el texto en el marco rojo."""
    img = fondo(W, H, variante).copy()
    img = _marco(img, t - 0.4, 0.7, texto, W, H)
    if t < 0.12:
        img = img + (1 - img) * (0.5 * (1 - t / 0.12))
    return np.clip(img, 0, 1)
