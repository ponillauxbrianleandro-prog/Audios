"""Cuaderno del científico (episodio 005).

Cuaderno abierto visto de frente, con perspectiva real: la cámara se inclina hacia él y se acerca. Sobre las hojas se dibuja a lápiz
con errores humanos: trazos repasados, rayones, correcciones y manchas de grafito; el texto es manuscrito (Caveat) y se va
escribiendo. El animal se dibuja a partir de su propio contorno (silueta del rig) y se sombrea con rayado.

  cuaderno(t, W, H, dur, items, vista=0)   -> fotograma float32 RGB [0,1]
Coordenadas de `items` en el lienzo del libro abierto: 2000 x 1300 (izquierda: x<1000, derecha: x>=1000).
"""
import numpy as np
import cv2
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

import sombra as S

AQUI = Path(__file__).resolve().parent
CW, CH = 2000, 1300
_FONT = {}
_PAPEL = {}
_ESCRITO = {}


def font(size):
    if size not in _FONT:
        _FONT[size] = ImageFont.truetype(str(AQUI / "fuentes" / "Caveat.ttf"), size)
    return _FONT[size]


def papel():
    """Hojas amarillentas con renglones tenues, margen rojo, encuadernación y sombra de pliegue."""
    if "p" in _PAPEL:
        return _PAPEL["p"]
    rng = np.random.default_rng(3)
    base = np.zeros((CH, CW, 3), np.float32)
    base[:] = (0.93, 0.89, 0.77)
    grano = cv2.GaussianBlur(rng.standard_normal((CH, CW)).astype(np.float32), (0, 0), 1.1) * 0.020
    fibra = cv2.GaussianBlur(rng.standard_normal((CH, CW)).astype(np.float32), (0, 0), 14) * 0.060
    base += (grano + fibra)[..., None]
    for y in range(150, CH - 60, 54):                                  # renglones azulados
        base[y:y + 2, 60:CW - 60] *= np.array([0.80, 0.86, 0.96], np.float32)
    base[:, 1000 - 5:1000 + 5] *= 0.80
    for x0 in (170, 1170):                                              # margen rojo de cada hoja
        base[:, x0:x0 + 2] *= np.array([1.0, 0.62, 0.62], np.float32)
    xs = np.arange(CW, dtype=np.float32)
    pliegue = 1.0 - 0.34 * np.exp(-((xs - 1000) / 85.0) ** 2) - 0.10 * np.exp(-((xs - 1000) / 330.0) ** 2)
    borde = 1.0 - 0.18 * np.exp(-(xs / 70.0) ** 2) - 0.18 * np.exp(-((CW - xs) / 70.0) ** 2)
    base *= (pliegue * borde)[None, :, None]
    yy = np.arange(CH, dtype=np.float32)
    base *= (1.0 - 0.10 * np.exp(-(yy / 80.0) ** 2) - 0.12 * np.exp(-((CH - yy) / 90.0) ** 2))[:, None, None]
    _PAPEL["p"] = np.clip(base, 0, 1)
    return _PAPEL["p"]


def escritorio(W, H):
    key = ("d", W, H)
    if key in _PAPEL:
        return _PAPEL[key]
    rng = np.random.default_rng(11)
    v = cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), (3.0, 90.0)[0])
    v = cv2.resize(cv2.GaussianBlur(rng.standard_normal((H // 8, W // 2)).astype(np.float32), (0, 0), 6), (W, H)) * 0.4
    madera = np.zeros((H, W, 3), np.float32)
    madera[:] = (0.20, 0.12, 0.08)
    madera += v[..., None] * np.array([0.28, 0.18, 0.12], np.float32) * 0.5
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    luz = np.exp(-(((xx - W * 0.45) / (W * 0.65)) ** 2 + ((yy - H * 0.40) / (H * 0.65)) ** 2))      # lámpara cálida
    madera *= (0.45 + 0.9 * luz)[..., None]
    _PAPEL[key] = np.clip(madera, 0, 1)
    return _PAPEL[key]


# ------------------------------------------------------------------ trazos
def _jit(pts, rng, amp):
    pts = np.asarray(pts, np.float32)
    n = len(pts)
    ruido = cv2.GaussianBlur(rng.standard_normal((n, 2)).astype(np.float32), (0, 0), 1.0) * amp if n > 2 else 0
    return pts + ruido


def _stroke(gr, pts, f, w=2.4, alpha=0.62):
    """Acumula en la capa de grafito `gr` la fracción f (0..1) de la polilínea `pts` (solo en su caja, para ir rápido)."""
    pts = np.asarray(pts, np.float32)
    if len(pts) < 2 or f <= 0:
        return
    seg = np.hypot(*np.diff(pts, axis=0).T)
    cum = np.concatenate([[0], np.cumsum(seg)])
    lim = cum[-1] * min(f, 1.0)
    k = int(np.searchsorted(cum, lim, side="right"))
    P = pts[:k].copy()
    if k < len(pts):
        a = (lim - cum[k - 1]) / max(seg[k - 1], 1e-6)
        P = np.vstack([P, pts[k - 1] + (pts[k] - pts[k - 1]) * a])
    if len(P) < 2:
        return
    pad = int(w) + 3
    x0, y0 = max(0, int(P[:, 0].min()) - pad), max(0, int(P[:, 1].min()) - pad)
    x1, y1 = min(CW, int(P[:, 0].max()) + pad), min(CH, int(P[:, 1].max()) + pad)
    if x1 <= x0 or y1 <= y0:
        return
    tmp = np.zeros((y1 - y0, x1 - x0), np.float32)
    cv2.polylines(tmp, [np.round((P - [x0, y0]) * 16).astype(np.int32).reshape(-1, 1, 2)], False, 1.0, max(1, int(round(w))), cv2.LINE_AA, 4)
    roi = gr[y0:y1, x0:x1]
    roi[:] = 1 - (1 - roi) * (1 - tmp * alpha)


def _contorno(frame_idx, box, nombre="vetusodon"):
    """Contorno (polilíneas) del animal en la caja dada (x, y, w, h) a partir de la silueta del rig, y máscara para rayar."""
    sil = S.silueta(nombre)
    fr = sil["frames"][frame_idx % sil["n"]] > 0
    ys, xs = np.nonzero(fr)
    fr = fr[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8)
    x, y, w, h = box
    s = min(w / fr.shape[1], h / fr.shape[0])
    m = cv2.resize(fr, (int(fr.shape[1] * s), int(fr.shape[0] * s)), interpolation=cv2.INTER_AREA)
    m = (cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.5) > 0.5).astype(np.uint8)
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cs = sorted(cs, key=lambda c: -len(c))[:2]
    out = [np.asarray(cv2.approxPolyDP(c, 1.2, True), np.float32).reshape(-1, 2) + [x, y] for c in cs]
    return out, m, (x, y)


def _rayado(m, org, ang=58.0, paso=11, rng=None):
    """Rayado diagonal dentro de la máscara (solo la mitad inferior, como sombra)."""
    h, w = m.shape
    rng = rng or np.random.default_rng(1)
    out = []
    th = np.deg2rad(ang)
    d = np.array([np.cos(th), -np.sin(th)])
    for c in np.arange(-h, w + h, paso):
        p0 = np.array([c, h], np.float32)
        ts = np.arange(0, h * 1.5, 2.0)
        P = p0[None, :] + ts[:, None] * d[None, :]
        ix, iy = P[:, 0].astype(int), P[:, 1].astype(int)
        ok = (ix >= 0) & (ix < w) & (iy >= 0) & (iy < h)
        ins = np.zeros(len(P), bool)
        ins[ok] = m[iy[ok], ix[ok]] > 0
        ins &= (P[:, 1] > h * (0.48 + 0.10 * np.sin(P[:, 0] * 0.03)))
        i = 0
        while i < len(P):
            if ins[i]:
                j = i
                while j < len(P) and ins[j]:
                    j += 1
                if j - i > 3:
                    q = P[i:j:3] + [org[0], org[1]]
                    out.append(_jit(q, rng, 0.5))
                i = j
            else:
                i += 1
    return out


_CRANEO = [  # perfil lateral de cráneo de cinodonte (0..1 en una caja de 3:2)
    [(0.02, 0.62), (0.10, 0.50), (0.28, 0.42), (0.50, 0.30), (0.66, 0.22), (0.80, 0.24), (0.90, 0.30), (0.97, 0.38), (0.98, 0.50)],   # perfil dorsal
    [(0.98, 0.50), (0.93, 0.56), (0.80, 0.60), (0.62, 0.64), (0.46, 0.74), (0.30, 0.80), (0.14, 0.80), (0.04, 0.72), (0.02, 0.62)],  # mandíbula
    [(0.50, 0.30), (0.58, 0.40), (0.60, 0.52), (0.52, 0.62)],                               # arco cigomático
    [(0.60, 0.26), (0.72, 0.28), (0.74, 0.40), (0.62, 0.42), (0.60, 0.26)],                 # órbita
    [(0.20, 0.50), (0.30, 0.44), (0.40, 0.48), (0.38, 0.60), (0.24, 0.62), (0.20, 0.50)],   # fenestra temporal
    [(0.86, 0.54), (0.87, 0.64)], [(0.82, 0.56), (0.83, 0.62)], [(0.78, 0.58), (0.79, 0.62)], [(0.92, 0.50), (0.935, 0.66)],     # dientes y colmillo
]


def _elementos(items, rng):
    """Convierte la descripción en trazos con su ventana de tiempo."""
    out = []
    for it in items:
        k = it["k"]
        t0, t1 = it["t0"], it["t1"]
        if k == "craneo":
            x, y, w, h = it["box"]
            n = len(_CRANEO)
            for i, ln in enumerate(_CRANEO):
                P = np.array(ln, np.float32) * [w, h] + [x, y]
                a = t0 + (t1 - t0) * i / n
                b = t0 + (t1 - t0) * (i + 1.2) / n
                from scipy.interpolate import splprep, splev
                try:
                    tck, _ = splprep([P[:, 0], P[:, 1]], s=len(P) * 1.5, k=min(3, len(P) - 1))
                    u = np.linspace(0, 1, 40)
                    P = np.stack(splev(u, tck), 1).astype(np.float32)
                except Exception:
                    pass
                for r in range(3):                                           # repasado: tres pasadas con desvío
                    out.append(dict(P=_jit(P, rng, 1.6), a=a + r * 0.18 * (b - a), b=b + r * 0.12 * (b - a), w=2.2 + 0.4 * r, al=0.50 + 0.1 * (r == 0)))
        elif k == "animal":
            cs, m, org = _contorno(it.get("frame", 6), it["box"])
            for c in cs:
                for r in range(2):
                    out.append(dict(P=_jit(c, rng, 1.2), a=t0 + r * 0.35, b=t1 * 0.62 + t0 * 0.38 + r * 0.25, w=2.6, al=0.62))
            if it.get("rayado", True):
                for i, ln in enumerate(_rayado(m, org, rng=rng)):
                    a = t0 + (t1 - t0) * (0.50 + 0.45 * rng.random())
                    out.append(dict(P=ln, a=a, b=a + 0.25, w=1.4, al=0.34))
        elif k == "flecha":
            (x0, y0), (x1, y1) = it["p0"], it["p1"]
            mid = ((x0 + x1) / 2 + (y1 - y0) * 0.12, (y0 + y1) / 2 - (x1 - x0) * 0.12)
            P = np.array([(x0, y0), mid, (x1, y1)], np.float32)
            Q = np.stack([np.interp(np.linspace(0, 2, 24), [0, 1, 2], P[:, j]) for j in range(2)], 1)
            ang = np.arctan2(Q[-1, 1] - Q[-3, 1], Q[-1, 0] - Q[-3, 0])
            out.append(dict(P=Q, a=t0, b=t1, w=2.8, al=0.7))
            for sg in (-1, 1):
                out.append(dict(P=np.array([(x1, y1), (x1 - 28 * np.cos(ang + sg * 0.45), y1 - 28 * np.sin(ang + sg * 0.45))], np.float32), a=t1 - 0.05, b=t1 + 0.1, w=2.8, al=0.7))
        elif k == "circulo":
            cx, cy = it["c"]
            rx, ry = it["r"]
            th = np.linspace(-0.3, 2 * np.pi + 0.5, 60)
            P = np.stack([cx + rx * np.cos(th) * (1 + 0.05 * np.sin(th * 2)), cy + ry * np.sin(th) * (1 + 0.04 * np.cos(th * 3))], 1).astype(np.float32)
            out.append(dict(P=_jit(P, rng, 1.5), a=t0, b=t1, w=3.0, al=0.75))
        elif k == "tachar":
            (x0, y0), (x1, y1) = it["p0"], it["p1"]
            for j in range(4):
                P = np.array([(x0, y0 + j * 14), (x1, y1 + j * 14 + (j % 2) * 6)], np.float32)
                out.append(dict(P=_jit(np.stack([np.linspace(P[0, i], P[1, i], 12) for i in range(2)], 1), rng, 2.0), a=t0 + j * 0.08, b=t0 + j * 0.08 + 0.18, w=3.0, al=0.6))
        elif k == "medida":
            (x0, y0), (x1, y1) = it["p0"], it["p1"]
            out.append(dict(P=np.array([(x0, y0), (x1, y1)], np.float32), a=t0, b=t1, w=2.2, al=0.7))
            for (x, y) in ((x0, y0), (x1, y1)):
                out.append(dict(P=np.array([(x, y - 14), (x, y + 14)], np.float32), a=t0, b=t0 + 0.1, w=2.2, al=0.7))
        elif k == "texto":
            out.append(dict(texto=it["s"], pos=it["pos"], size=it.get("size", 64), a=t0, b=t1, rot=it.get("rot", -1.5), col=it.get("col", (0.12, 0.12, 0.22))))
    return out


def _texto_layer(el):
    key = (el["texto"], el["size"], el["rot"])
    if key in _ESCRITO:
        return _ESCRITO[key]
    f = font(el["size"])
    box = f.getbbox(el["texto"])
    w, h = box[2] + 20, box[3] + 24
    im = Image.new("L", (w, h), 0)
    ImageDraw.Draw(im).text((8, 4), el["texto"], font=f, fill=255)
    a = np.asarray(im, np.float32) / 255.0
    M = cv2.getRotationMatrix2D((w / 2, h / 2), -el["rot"], 1.0)
    a = cv2.warpAffine(a, M, (w, h), flags=cv2.INTER_LINEAR)
    _ESCRITO[key] = a
    return a


def libro(t, items, seed=1):
    """Lienzo del libro abierto en el instante t (segundos desde el inicio de la escena)."""
    rng = np.random.default_rng(seed)
    cv = papel().copy()
    els = _elementos(items, rng)
    smudge = np.zeros((CH, CW), np.float32)
    gr = np.zeros((CH, CW), np.float32)
    for e in els:
        if "texto" in e:
            if t <= e["a"]:
                continue
            f = float(np.clip((t - e["a"]) / max(e["b"] - e["a"], 1e-3), 0, 1))
            a = _texto_layer(e)
            h, w = a.shape
            x, y = e["pos"]
            xr = int(w * f)
            if xr < 2:
                continue
            ya, xa, yb, xb = max(0, y), max(0, x), min(CH, y + h), min(CW, x + xr)
            if yb <= ya or xb <= xa:
                continue
            sub = a[ya - y:yb - y, xa - x:xb - x]
            col = np.array(e["col"], np.float32)
            cv[ya:yb, xa:xb] = cv[ya:yb, xa:xb] * (1 - sub[..., None] * 0.92) + col * sub[..., None] * 0.92
            continue
        f = float(np.clip((t - e["a"]) / max(e["b"] - e["a"], 1e-3), 0, 1))
        if f > 0:
            _stroke(gr, e["P"], f, w=e["w"], alpha=e["al"])
            if f >= 1 and e["w"] > 2.5:
                P = e["P"].astype(int)
                smudge[np.clip(P[:, 1], 0, CH - 1), np.clip(P[:, 0], 0, CW - 1)] = 1.0
    sm = cv2.GaussianBlur(smudge, (0, 0), 7) * 3.0                          # mancha de grafito alrededor de lo ya dibujado
    cv *= (1 - np.clip(sm, 0, 0.10))[..., None]
    cv = cv * (1 - gr[..., None]) + np.array((0.17, 0.16, 0.19), np.float32) * gr[..., None]
    return cv


def cuaderno(t, W, H, dur, items, vista=0, seed=1, **_):
    cvs = libro(t, items, seed)
    u = float(np.clip(t / max(dur, 1e-3), 0, 1))
    u = u * u * (3 - 2 * u)
    esc = 0.60 + 0.34 * u                                                    # acercamiento (nos inclinamos sobre el cuaderno)
    pitch = (1 - u) * 0.14 + 0.03                                            # al inicio más inclinado: perspectiva marcada
    roll = (-1.8 + 1.6 * u + 0.5 * np.sin(t * 0.6)) * np.pi / 180
    cx, cy = W * (0.50 + 0.02 * (1 - u)), H * (0.52 + 0.05 * (1 - u))
    w, h = W * esc * 1.30, H * esc * 1.30 * (CH / CW) * 1.55
    src = np.float32([[0, 0], [CW, 0], [CW, CH], [0, CH]])
    top, bot = 1.0 - pitch, 1.0 + pitch * 0.9                                # borde superior más lejano
    quad = []
    for sx, sy, k in ((-0.5, -0.5, top), (0.5, -0.5, top), (0.5, 0.5, bot), (-0.5, 0.5, bot)):
        x, y = sx * w * k, sy * h * (0.80 + 0.2 * k)
        quad.append([cx + x * np.cos(roll) - y * np.sin(roll), cy + x * np.sin(roll) + y * np.cos(roll)])
    dst = np.float32(quad)
    Mh = cv2.getPerspectiveTransform(src, dst)
    desk = escritorio(W, H).copy()
    alpha = cv2.warpPerspective(np.ones((CH, CW), np.float32), Mh, (W, H), flags=cv2.INTER_LINEAR)
    sombra = cv2.GaussianBlur(cv2.warpPerspective(np.ones((CH, CW), np.float32), Mh + np.array([[0, 0, 22], [0, 0, 28], [0, 0, 0]], np.float64), (W, H)), (0, 0), W * 0.012)
    desk *= (1 - 0.55 * sombra)[..., None]
    page = cv2.warpPerspective(cvs, Mh, (W, H), flags=cv2.INTER_AREA if esc < 0.75 else cv2.INTER_LINEAR)
    img = desk * (1 - alpha[..., None]) + page * alpha[..., None]
    # lápiz sobre el escritorio y luz de lámpara
    ylap = int(H * 0.93)
    cv2.line(img, (int(W * 0.06), ylap), (int(W * 0.30), ylap - int(H * 0.04)), (0.85, 0.65, 0.20), max(3, int(H * 0.012)), cv2.LINE_AA)
    cv2.line(img, (int(W * 0.06), ylap), (int(W * 0.075), ylap - 2), (0.2, 0.2, 0.22), max(3, int(H * 0.012)), cv2.LINE_AA)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vig = 1 - 0.30 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.2
    return np.clip(img * vig[..., None], 0, 1)
