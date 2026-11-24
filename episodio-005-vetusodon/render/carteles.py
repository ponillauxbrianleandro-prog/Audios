#!/usr/bin/env python3
"""Apertura «carteles de calle» y escena de cuaderno, baratas por cuadro (sin motor 3D, sin importar sombra/engine).

  apertura(t, W, H, escenas_foto, textos, dur=None, seed=1, silueta=None) -> ndarray uint8 RGB (H, W, 3)
  cortes_apertura(dur, seed=1, lo=0.30, hi=0.80) -> lista de instantes de corte (= clics de camara; sincronizar el audio)
  cuaderno_frame(t, notas, W, H, dur=8.0) -> ndarray uint8 RGB (libreta abierta en perspectiva, trazos que se dibujan)

apertura: fondo rojo plano con poste, disco de «prohibido el paso» con la silueta del animal (procedural, o `silueta` = PIL
RGBA/L con el animal en negro), flecha ONE WAY y senal de cruce de peatones. SOLO se mueve la ventana de fotos (cambia de toma
en cada corte, 0,3-0,8 s, con destello de obturador de ~0,08 s). El marco rojo nace en la esquina inferior derecha y crece
hacia la izquierda/arriba: `textos` = [(t_inicio, "TEXTO"), ...] (queda hasta el siguiente texto).
`escenas_foto`: lista de ndarray RGB (uint8 o float 0..1) o PIL.Image.

cuaderno_frame: `notas` usa las mismas claves que render/cuaderno.py, en su lienzo de 2000x1300:
  {"k":"texto","s":"...","pos":(x,y),"size":64,"t0":..,"t1":..}   {"k":"linea"/"flecha"/"tachar"/"medida","p0":(x,y),"p1":(x,y),...}
  {"k":"circulo","c":(x,y),"r":(rx,ry),...}   {"k":"craneo"|"animal"(contorno ovalado simple),"box":(x,y,w,h),...}
"""
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
ROJO, ROJO_D, ROJO_L = (184, 35, 63), (140, 22, 49), (212, 58, 84)
NEGRO, BLANCO = (11, 11, 16), (247, 243, 234)
_F = {}


def _font(size, bold=True):
    k = (int(size), bold)
    if k not in _F:
        _F[k] = ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{'Bold' if bold else 'Medium'}.otf", max(8, int(size)))
    return _F[k]


def _arr(x):
    a = np.asarray(x)
    if a.dtype != np.uint8:
        a = (np.clip(a, 0, 1) * 255).astype(np.uint8)
    return a[..., :3]


# ------------------------------------------------------------------ cortes
def cortes_apertura(dur, seed=1, lo=0.30, hi=0.80):
    """Instantes de corte (multiplos de 1/24 s): ninguna toma dura 1 s. Cada uno lleva un clic."""
    rng = np.random.default_rng(seed)
    t, out = 0.0, []
    while t < dur - 1e-6:
        out.append(round(t * 24) / 24)
        t += float(rng.uniform(lo, hi))
    return out


# ------------------------------------------------------------------ pictogramas
def _silueta_animal(w):
    """Cinodonte estilizado (cuerpo bajo, hocico largo, cola) como mascara L de ancho w, mirando a la izquierda."""
    h = int(w * 0.55)
    im = Image.new("L", (w * 2, h * 2), 0)
    d = ImageDraw.Draw(im)
    S = lambda x, y: (x * w * 2, y * h * 2)
    d.ellipse([*S(0.30, 0.30), *S(0.82, 0.70)], fill=255)                        # tronco
    d.polygon([S(0.04, 0.48), S(0.18, 0.34), S(0.36, 0.34), S(0.36, 0.64), S(0.18, 0.62), S(0.04, 0.56)], fill=255)   # cabeza
    d.polygon([S(0.12, 0.34), S(0.15, 0.22), S(0.20, 0.34)], fill=255)           # oreja
    d.polygon([S(0.78, 0.40), S(0.97, 0.48), S(1.0, 0.56), S(0.78, 0.60)], fill=255)  # cola
    for x in (0.30, 0.40, 0.66, 0.76):                                           # patas
        d.rounded_rectangle([*S(x, 0.58), *S(x + 0.07, 0.95)], radius=int(w * 0.02), fill=255)
    return im.resize((w, h), Image.LANCZOS)


def _disco(im, cx, cy, r, sil):
    d = ImageDraw.Draw(im)
    d.ellipse([cx - r * 1.08, cy - r * 1.08, cx + r * 1.08, cy + r * 1.08], fill=BLANCO)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ROJO_L)
    d.ellipse([cx - r * 0.86, cy - r * 0.86, cx + r * 0.86, cy + r * 0.86], fill=BLANCO)
    d.ellipse([cx - r * 0.78, cy - r * 0.78, cx + r * 0.78, cy + r * 0.78], fill=(238, 232, 220))
    s = sil.resize((int(r * 1.4), max(2, int(r * 1.4 * sil.height / sil.width))), Image.LANCZOS)
    blk = Image.new("RGB", s.size, NEGRO)
    im.paste(blk, (int(cx - s.width / 2), int(cy - s.height / 2)), s)
    d = ImageDraw.Draw(im)
    d.line([cx - r * 0.72, cy + r * 0.72, cx + r * 0.72, cy - r * 0.72], fill=ROJO_L, width=max(4, int(r * 0.17)))   # barra de prohibido


def _flecha(d, x, y, w, h):
    d.rounded_rectangle([x, y, x + w, y + h], radius=int(h * 0.1), fill=NEGRO, outline=BLANCO, width=max(2, int(h * 0.04)))
    pts = [(x + w * .06, y + h * .5), (x + w * .30, y + h * .15), (x + w * .30, y + h * .38), (x + w * .92, y + h * .38),
           (x + w * .92, y + h * .62), (x + w * .30, y + h * .62), (x + w * .30, y + h * .85)]
    d.polygon(pts, fill=BLANCO)
    d.text((x + w * .60, y + h * .50), "ONE WAY", font=_font(h * .19), fill=NEGRO, anchor="mm")


def _cruce(d, x, y, s):
    """Senal de cruce de peatones: triangulo/cuadrado azul-negro con figura y cebra."""
    d.rounded_rectangle([x, y, x + s, y + s], radius=int(s * .08), fill=NEGRO, outline=BLANCO, width=max(3, int(s * .04)))
    cx = x + s * .5
    d.ellipse([cx - s * .08, y + s * .12, cx + s * .08, y + s * .28], fill=BLANCO)
    lw = max(3, int(s * .07))
    d.line([(cx, y + s * .30), (cx - s * .03, y + s * .52)], fill=BLANCO, width=lw)
    d.line([(cx - s * .03, y + s * .52), (cx - s * .14, y + s * .72)], fill=BLANCO, width=lw)
    d.line([(cx - s * .03, y + s * .52), (cx + s * .11, y + s * .72)], fill=BLANCO, width=lw)
    d.line([(cx, y + s * .36), (cx - s * .15, y + s * .47)], fill=BLANCO, width=lw)
    d.line([(cx, y + s * .36), (cx + s * .16, y + s * .43)], fill=BLANCO, width=lw)
    for i in range(5):
        d.rectangle([x + s * (.08 + i * .18), y + s * .82, x + s * (.18 + i * .18), y + s * .94], fill=BLANCO)


_BASE = {}


def fondo(W, H, silueta=None):
    key = (W, H, id(silueta))
    if key in _BASE:
        return _BASE[key]
    k = W / 1920.0
    im = Image.new("RGB", (W, H), ROJO)
    d = ImageDraw.Draw(im)
    d.rectangle([0, int(H * .86), W, H], fill=ROJO_D)
    rng = np.random.default_rng(7)
    for _ in range(90):                                                      # desgaste de pintura
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        d.ellipse([x, y, x + rng.uniform(2, 9) * k, y + rng.uniform(2, 6) * k], fill=ROJO_L)
    d.rectangle([int(W * .14), int(H * .50), int(W * .16), H], fill=(70, 70, 78))
    sil = silueta if silueta is not None else _silueta_animal(600)
    if silueta is not None and sil.mode == "RGBA":
        sil = sil.split()[3]
    _disco(im, int(W * .15), int(H * .30), int(H * .22), sil.convert("L"))
    d = ImageDraw.Draw(im)
    _flecha(d, int(W * .035), int(H * .62), int(W * .19), int(H * .115))
    _cruce(d, int(W * .905), int(H * .06), int(W * .07))
    a = np.asarray(im, np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a *= (0.92 - 0.25 * (((xx / W - .5) ** 2 + (yy / H - .45) ** 2) * 2))[..., None]
    a += cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), 1.2)[..., None] * 3
    _BASE[key] = np.clip(a, 0, 255)
    return _BASE[key]


def _foto(arr, w, h, zoom=1.0, dx=0.0):
    ih, iw = arr.shape[:2]
    s = max(w / iw, h / ih) * zoom
    r = cv2.resize(arr, (max(w, int(iw * s) + 1), max(h, int(ih * s) + 1)), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR)
    y0, x0 = (r.shape[0] - h) // 2, int((r.shape[1] - w) // 2 + dx * (r.shape[1] - w) / 2)
    return r[y0:y0 + h, x0:x0 + w]


def _marco(img, t, texto, W, H, dur_in=0.55):
    """Marco rojo: nace en la esquina inferior derecha, crece hacia la izquierda y un poco hacia arriba; el texto aparece al final."""
    if t <= 0 or not texto:
        return img
    u = float(np.clip(t / dur_in, 0, 1))
    u = 1 - (1 - u) ** 3
    xr, yb = W * .965, H * .94
    xl = W * .12
    x0 = xr - (xr - xl) * u
    ytl = yb - (yb - H * .66) * u
    ytr = yb - (yb - H * .55) * u
    pts = [(x0, ytl), (xr, ytr), (xr, yb), (x0, yb)]
    im = Image.fromarray(img)
    d = ImageDraw.Draw(im, "RGBA")
    d.polygon([(x + 8, y + 10) for x, y in pts], fill=(0, 0, 0, 90))
    d.polygon(pts, fill=ROJO + (255,))
    d.line(pts + [pts[0]], fill=BLANCO + (255,), width=max(3, int(W * .004)), joint="curve")
    if u > .55:
        a = int(255 * np.clip((u - .55) / .35, 0, 1))
        size = H * .062 * (1.0 if len(texto) < 22 else .8 if len(texto) < 30 else .64)
        d.text(((x0 + xr) / 2, (min(ytl, ytr) + yb) / 2 + H * .01), texto, font=_font(size), fill=BLANCO + (a,), anchor="mm")
    return np.asarray(im)


def apertura(t, W, H, escenas_foto, textos=(), dur=None, seed=1, silueta=None, cortes=None):
    """Cuadro de la apertura en el instante t (s). Devuelve uint8 RGB."""
    cortes = cortes or cortes_apertura(dur or max(t + 1, 60), seed)
    k = max(int(np.searchsorted(cortes, t + 1e-6, side="right") - 1), 0)
    t_in = t - cortes[k]
    rng = np.random.default_rng(seed * 131 + k)
    img = fondo(W, H, silueta).copy()
    foto = _arr(escenas_foto[(k * 7 + seed) % len(escenas_foto)] if not isinstance(escenas_foto[0], Image.Image) else np.asarray(escenas_foto[(k * 7 + seed) % len(escenas_foto)].convert("RGB")))
    ww, hh = int(W * .60), int(H * .68)
    ph = _foto(foto, ww, hh, 1.0 + .10 * t_in / .6, float(rng.uniform(-1, 1)) * .3).astype(np.float32)
    pad = int(W * .011)
    card = np.empty((hh + 2 * pad + int(H * .05), ww + 2 * pad, 3), np.float32)
    card[:] = BLANCO
    card[pad:pad + hh, pad:pad + ww] = ph
    ang = float(rng.uniform(-2.2, 2.2))
    ch, cw = card.shape[:2]
    s = int(max(ch, cw) * 1.3)
    big = np.zeros((s, s, 4), np.float32)
    oy, ox = (s - ch) // 2, (s - cw) // 2
    big[oy:oy + ch, ox:ox + cw, :3] = card
    big[oy:oy + ch, ox:ox + cw, 3] = 1
    big = cv2.warpAffine(big, cv2.getRotationMatrix2D((s / 2, s / 2), ang, 1.0), (s, s), flags=cv2.INTER_LINEAR)
    cx, cy = int(W * .60), int(H * .44)
    y0, x0 = cy - s // 2, cx - s // 2
    ya, xa, yb, xb = max(0, y0), max(0, x0), min(H, y0 + s), min(W, x0 + s)
    sub = big[ya - y0:yb - y0, xa - x0:xb - x0]
    sh = cv2.GaussianBlur(sub[..., 3], (0, 0), W * .006)[..., None] * .35
    img[ya:yb, xa:xb] = img[ya:yb, xa:xb] * (1 - sh)
    img[ya:yb, xa:xb] = img[ya:yb, xa:xb] * (1 - sub[..., 3:4]) + sub[..., :3] * sub[..., 3:4]
    if t_in < .08:                                                           # destello de obturador
        img = img + (255 - img) * (.55 * (1 - t_in / .08))
    out = np.clip(img, 0, 255).astype(np.uint8)
    texto, tt = "", 0.0
    for t0, tx in textos:
        if t >= t0:
            texto, tt = tx, t - t0
    return _marco(out, tt, texto, W, H)


# ================================================================== cuaderno barato
CW, CH = 2000, 1300
K = 0.6                                  # lienzo interno = 1200 x 780
IW, IH = int(CW * K), int(CH * K)
_C = {}
_CAV = {}


def _papel():
    if "p" in _C:
        return _C["p"]
    rng = np.random.default_rng(3)
    b = np.zeros((IH, IW, 3), np.float32)
    b[:] = (.93, .89, .77)
    b += (cv2.GaussianBlur(rng.standard_normal((IH, IW)).astype(np.float32), (0, 0), .8) * .02 +
          cv2.GaussianBlur(rng.standard_normal((IH, IW)).astype(np.float32), (0, 0), 9) * .06)[..., None]
    for y in range(int(150 * K), IH - 40, int(54 * K)):
        b[y:y + 2, 36:IW - 36] *= np.array([.80, .86, .96], np.float32)
    mid = IW // 2
    for x0 in (int(170 * K), int(1170 * K)):
        b[:, x0:x0 + 2] *= np.array([1, .62, .62], np.float32)
    xs = np.arange(IW, dtype=np.float32)
    b *= ((1 - .34 * np.exp(-((xs - mid) / 50) ** 2) - .10 * np.exp(-((xs - mid) / 200) ** 2)) * (1 - .18 * np.exp(-(xs / 42) ** 2) - .18 * np.exp(-((IW - xs) / 42) ** 2)))[None, :, None]
    _C["p"] = np.clip(b, 0, 1)
    return _C["p"]


def _mesa(W, H):
    k = ("m", W, H)
    if k not in _C:
        rng = np.random.default_rng(11)
        v = cv2.resize(cv2.GaussianBlur(rng.standard_normal((H // 8, W // 2)).astype(np.float32), (0, 0), 6), (W, H)) * .2
        m = np.zeros((H, W, 3), np.float32)
        m[:] = (.20, .12, .08)
        m += v[..., None] * np.array([.28, .18, .12], np.float32)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        m *= (.45 + .9 * np.exp(-(((xx - W * .45) / (W * .65)) ** 2 + ((yy - H * .4) / (H * .65)) ** 2)))[..., None]
        vig = 1 - .30 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.2
        _C[k] = np.clip(m, 0, 1)
        _C[("v", W, H)] = vig.astype(np.float32)
    return _C[k]


def _fuente(size):
    k = ("f", size)
    if k not in _C:
        _C[k] = ImageFont.truetype(str(AQUI / "fuentes" / "Caveat.ttf"), max(8, int(size * K)))
    return _C[k]


def _texto(s, size, rot=-1.5):
    k = (s, size, rot)
    if k not in _CAV:
        f = _fuente(size)
        bb = f.getbbox(s)
        w, h = bb[2] + 12, bb[3] + 14
        im = Image.new("L", (w, h), 0)
        ImageDraw.Draw(im).text((5, 2), s, font=f, fill=255)
        a = np.asarray(im, np.float32) / 255
        _CAV[k] = cv2.warpAffine(a, cv2.getRotationMatrix2D((w / 2, h / 2), -rot, 1), (w, h))
    return _CAV[k]


def _elementos(notas):
    """Cada elemento: lista de polilineas (en px internos) con ventana temporal, o texto."""
    out = []
    rng = np.random.default_rng(5)
    for it in notas:
        k, t0, t1 = it["k"], it["t0"], it["t1"]
        if k == "texto":
            out.append(dict(tx=it["s"], pos=(int(it["pos"][0] * K), int(it["pos"][1] * K)), size=it.get("size", 64), rot=it.get("rot", -1.5), a=t0, b=t1,
                            col=it.get("col", (.12, .12, .22))))
        elif k in ("linea", "flecha", "medida"):
            (x0, y0), (x1, y1) = it["p0"], it["p1"]
            P = np.array([(x0, y0), ((x0 + x1) / 2 + (y1 - y0) * .08, (y0 + y1) / 2 - (x1 - x0) * .08), (x1, y1)], np.float32) * K
            Q = np.stack([np.interp(np.linspace(0, 2, 24), [0, 1, 2], P[:, j]) for j in range(2)], 1)
            out.append(dict(P=Q + rng.normal(0, .5, Q.shape), a=t0, b=t1, w=2.0, al=.72))
            if k == "flecha":
                ang = math.atan2(Q[-1, 1] - Q[-3, 1], Q[-1, 0] - Q[-3, 0])
                for sg in (-1, 1):
                    out.append(dict(P=np.array([Q[-1], Q[-1] - 18 * np.array([math.cos(ang + sg * .45), math.sin(ang + sg * .45)])]), a=t1 - .05, b=t1 + .1, w=2.0, al=.72))
        elif k == "tachar":
            (x0, y0), (x1, y1) = it["p0"], it["p1"]
            for j in range(3):
                P = np.array([(x0, y0 + j * 14), (x1, y1 + j * 14 + (j % 2) * 6)], np.float32) * K
                out.append(dict(P=np.stack([np.linspace(P[0, i], P[1, i], 8) for i in range(2)], 1), a=t0 + j * .08, b=t0 + j * .08 + .18, w=2.2, al=.6))
        elif k == "circulo":
            cx, cy = it["c"]
            rx, ry = it["r"]
            th = np.linspace(-.3, 2 * math.pi + .5, 50)
            P = np.stack([cx + rx * np.cos(th) * (1 + .05 * np.sin(th * 2)), cy + ry * np.sin(th)], 1) * K
            out.append(dict(P=P.astype(np.float32), a=t0, b=t1, w=2.4, al=.75))
        elif k in ("craneo", "animal"):
            x, y, w, h = it["box"]
            # silueta simplificada de craneo/cuerpo: contorno ovalado con hocico + detalles
            u = np.linspace(0, 1, 60)
            pol = np.stack([.5 + .48 * np.cos(2 * math.pi * u) * (1 + .15 * np.cos(2 * math.pi * u)), .5 + .32 * np.sin(2 * math.pi * u)], 1)
            P = (pol * [w, h] + [x, y]) * K
            n = 3
            for r in range(n):
                out.append(dict(P=(P + rng.normal(0, 1.2, P.shape)).astype(np.float32), a=t0 + r * .3 * (t1 - t0), b=t0 + (.55 + r * .22) * (t1 - t0), w=2.0 + r * .3, al=.55))
            for i in range(5):
                xx = x + w * (.62 + .07 * i)
                out.append(dict(P=np.array([(xx, y + h * .66), (xx + 4, y + h * .80)], np.float32) * K, a=t0 + (t1 - t0) * (.7 + .05 * i), b=t0 + (t1 - t0) * (.76 + .05 * i), w=2.0, al=.6))
            out.append(dict(P=np.array([(x + w * .66, y + h * .30), (x + w * .74, y + h * .22), (x + w * .80, y + h * .34), (x + w * .70, y + h * .40), (x + w * .66, y + h * .30)], np.float32) * K,
                            a=t0 + (t1 - t0) * .5, b=t0 + (t1 - t0) * .7, w=2.0, al=.6))
    return out


def _trazar(gr, P, f, w, al):
    P = np.asarray(P, np.float32)
    seg = np.hypot(*np.diff(P, axis=0).T)
    cum = np.concatenate([[0], np.cumsum(seg)])
    lim = cum[-1] * min(f, 1.0)
    i = int(np.searchsorted(cum, lim, side="right"))
    Q = P[:i].copy()
    if i < len(P):
        a = (lim - cum[i - 1]) / max(seg[i - 1], 1e-6)
        Q = np.vstack([Q, P[i - 1] + (P[i] - P[i - 1]) * a])
    if len(Q) < 2:
        return
    pad = int(w) + 3
    x0, y0 = max(0, int(Q[:, 0].min()) - pad), max(0, int(Q[:, 1].min()) - pad)
    x1, y1 = min(IW, int(Q[:, 0].max()) + pad), min(IH, int(Q[:, 1].max()) + pad)
    if x1 <= x0 or y1 <= y0:
        return
    tmp = np.zeros((y1 - y0, x1 - x0), np.float32)
    cv2.polylines(tmp, [np.round((Q - [x0, y0]) * 16).astype(np.int32).reshape(-1, 1, 2)], False, 1.0, max(1, int(round(w))), cv2.LINE_AA, 4)
    roi = gr[y0:y1, x0:x1]
    roi[:] = 1 - (1 - roi) * (1 - tmp * al)


def cuaderno_frame(t, notas, W, H, dur=8.0, seed=1):
    """Libreta abierta con perspectiva; la camara se acerca y se endereza. ~25-40 ms por cuadro a 1280x720."""
    els = notas.get("_els") if isinstance(notas, dict) else None
    key = ("els", id(notas))
    if key not in _C:
        _C[key] = _elementos(notas)
    els = _C[key]
    cv = _papel().copy()
    gr = np.zeros((IH, IW), np.float32)
    for e in els:
        f = float(np.clip((t - e["a"]) / max(e["b"] - e["a"], 1e-3), 0, 1))
        if f <= 0:
            continue
        if "tx" in e:
            a = _texto(e["tx"], e["size"], e["rot"])
            h, w = a.shape
            x, y = e["pos"]
            xr = int(w * f)
            if xr < 2:
                continue
            ya, xa, yb, xb = max(0, y), max(0, x), min(IH, y + h), min(IW, x + xr)
            if yb > ya and xb > xa:
                sub = a[ya - y:yb - y, xa - x:xb - x]
                cv[ya:yb, xa:xb] = cv[ya:yb, xa:xb] * (1 - sub[..., None] * .92) + np.array(e["col"], np.float32) * sub[..., None] * .92
        else:
            _trazar(gr, e["P"], f, e["w"], e["al"])
    cv = cv * (1 - gr[..., None]) + np.array((.17, .16, .19), np.float32) * gr[..., None]
    u = float(np.clip(t / max(dur, 1e-3), 0, 1))
    u = u * u * (3 - 2 * u)
    esc = .60 + .34 * u
    pitch = (1 - u) * .14 + .03
    roll = (-1.8 + 1.6 * u + .5 * math.sin(t * .6)) * math.pi / 180
    cx, cy = W * (.50 + .02 * (1 - u)), H * (.52 + .05 * (1 - u))
    w, h = W * esc * 1.30, H * esc * 1.30 * (CH / CW) * 1.55
    top, bot = 1 - pitch, 1 + pitch * .9
    quad = []
    for sx, sy, kk in ((-.5, -.5, top), (.5, -.5, top), (.5, .5, bot), (-.5, .5, bot)):
        x, y = sx * w * kk, sy * h * (.8 + .2 * kk)
        quad.append([cx + x * math.cos(roll) - y * math.sin(roll), cy + x * math.sin(roll) + y * math.cos(roll)])
    src = np.float32([[0, 0], [IW, 0], [IW, IH], [0, IH]])
    Mh = cv2.getPerspectiveTransform(src, np.float32(quad))
    desk = _mesa(W, H).copy()
    ones = np.ones((IH // 4, IW // 4), np.float32)
    S4 = np.diag([4., 4., 1.])
    Mo = Mh @ S4
    alpha = cv2.warpPerspective(np.ones((IH, IW), np.float32), Mh, (W, H), flags=cv2.INTER_LINEAR)
    sombra = cv2.GaussianBlur(cv2.warpPerspective(np.ones((IH, IW), np.float32), Mh + np.array([[0, 0, 22], [0, 0, 28], [0, 0, 0]], np.float64), (W, H)), (0, 0), W * .012)
    desk *= (1 - .55 * sombra)[..., None]
    page = cv2.warpPerspective(cv, Mh, (W, H), flags=cv2.INTER_AREA if esc < .75 else cv2.INTER_LINEAR)
    img = desk * (1 - alpha[..., None]) + page * alpha[..., None]
    ylap = int(H * .93)
    cv2.line(img, (int(W * .06), ylap), (int(W * .30), ylap - int(H * .04)), (.85, .65, .20), max(3, int(H * .012)), cv2.LINE_AA)
    cv2.line(img, (int(W * .06), ylap), (int(W * .075), ylap - 2), (.2, .2, .22), max(3, int(H * .012)), cv2.LINE_AA)
    img *= _C[("v", W, H)][..., None]
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    rng = np.random.default_rng(1)
    fotos = []
    for i in range(4):
        g = cv2.GaussianBlur(rng.random((72, 128, 3)).astype(np.float32), (0, 0), 3)
        g = cv2.resize(g, (1280, 720))
        g = g / g.max() * np.array([.9, .7, .4]) if i % 2 else g / g.max() * np.array([.5, .7, .4])
        fotos.append((g * 255).astype(np.uint8))
    Image.fromarray(apertura(7.0, 1280, 720, fotos, [(4.0, "KAROO, SUDÁFRICA")], dur=30)).save(out + "/apertura.png")
    notas = [dict(k="texto", s="Vetusodon elikhulu", pos=(200, 200), t0=.2, t1=2.0, size=80), dict(k="craneo", box=(240, 330, 560, 380), t0=1.0, t1=5.0),
             dict(k="flecha", p0=(1000, 500), p1=(820, 640), t0=3.5, t1=4.2), dict(k="texto", s="cráneo ~18 cm", pos=(1100, 440), t0=3.0, t1=4.6, size=64),
             dict(k="circulo", c=(1500, 300), r=(180, 70), t0=4, t1=5)]
    Image.fromarray(cuaderno_frame(4.0, notas, 1280, 720, dur=8)).save(out + "/cuaderno.png")
