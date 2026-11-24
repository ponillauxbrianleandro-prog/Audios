#!/usr/bin/env python3
"""Richard Owen (personaje 2D pintado, estilizado, NO copia ningun retrato concreto).

Paleontologo victoriano con cabeza grande y expresiva: frente amplia y alta, entrecejo severo, nariz de aguila, patillas
(«mutton chops») plateadas, cuello alto de pajarita, levita negra, chaleco granate con cadena de reloj y monoculo.
Vista 3/4 (la cara mira hacia la derecha del cuadro). Ilustracion pintada por capas (contorno marron calido, degradado
«inflado» con luz lateral, grano), igual que render/mascota.py: sin modelo 3D.

API
  owen(expresion, pose="busto", fase=0.0, pal="ambar", h_px=700, habla=0.0) -> PIL RGBA (recortado, h_px de alto)
      expresion: neutral | severo | indignado | orgulloso | sorprendido | pensativo | burlon | anotando
      pose:      "busto" o "cuerpo" (+ "_gesto"): reposo (por defecto) | dedo | monoculo | anotando
                 ej.: "busto_dedo", "cuerpo_anotando", "busto_monoculo"
      fase:      0..1 ciclica (periodo 1 = un ciclo de ~2,4 s): respiracion, parpadeo (a fase ~0.80-0.88), deriva de la
                 mirada, ritmo del gesto (dedo que se mueve, lapiz que escribe, monoculo que se ajusta)
      pal:       nombre o dict de biblioteca/paletas.py (tine luz/sombra y el contorno)
      habla:     0..1 apertura extra de la boca (para sincronizar con la voz; opcional)
  ciclo_anotando(n, pal="ambar", h_px=600, pose="busto") -> lista de n PIL RGBA (loop perfecto: escribe en la libreta)
  libreta(h_px=300, fase=0.0, pal="ambar", abierta=True, texto=None) -> PIL RGBA (libreta + lapiz; el lapiz escribe con fase)
  hoja_expresiones(path, ...)  /  python3 owen.py HOJA.png  -> hoja de contactos

Tiempo: ~0.15 s por cuadro (busto, h_px 700) con la parte estatica en cache; la primera llamada tarda ~1 s.
"""
import math
import os
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paletas import obtener  # noqa: E402

CW, CH = 1100, 1560
OUTC = np.array([40, 22, 16], np.float32)
FUENTE = Path(__file__).resolve().parent.parent / "render" / "fuentes" / "Caveat.ttf"

# ---- colores base (se modulan luego con la paleta)
PIEL_L, PIEL_M, PIEL_D = np.array([246, 206, 176.]), np.array([222, 168, 138.]), np.array([158, 98, 88.])
PELO_L, PELO_D = np.array([236, 232, 224.]), np.array([120, 116, 128.])
CEJA_C = np.array([104, 94, 90.])
ABRIGO_L, ABRIGO_D = np.array([78, 76, 92.]), np.array([22, 20, 30.])
CHAL_L, CHAL_D = np.array([158, 58, 66.]), np.array([70, 24, 36.])
CAMISA_L, CAMISA_D = np.array([252, 246, 232.]), np.array([186, 172, 160.])
ORO_L, ORO_D = np.array([236, 204, 110.]), np.array([128, 92, 40.])
CUERO_L, CUERO_D = np.array([140, 84, 48.]), np.array([62, 34, 22.])
PAPEL_L, PAPEL_D = np.array([246, 234, 200.]), np.array([196, 174, 130.])


# ------------------------------------------------------------------------------------------------ utilidades
def spl(pts, n=10, closed=True):
    P = [np.array(p, float) for p in pts]
    m = len(P)
    out = []
    for i in range(m if closed else m - 1):
        p0, p1, p2, p3 = P[(i - 1) % m], P[i], P[(i + 1) % m], P[(i + 2) % m]
        if not closed:
            p0 = P[max(i - 1, 0)]
            p3 = P[min(i + 2, m - 1)]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    if not closed:
        out.append(P[-1])
    return np.array(out)


def bez(p0, p1, p2, n=14):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 2 * np.array(p0, float) + 2 * (1 - t) * t * np.array(p1, float) + t ** 2 * np.array(p2, float)


def cap(p0, p1, r0, r1, n=10):
    """Capsula (tubo con radios distintos) como poligono."""
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = p1 - p0
    L = np.linalg.norm(d) + 1e-6
    a = math.atan2(d[1], d[0])
    pts = []
    for t in np.linspace(a + math.pi / 2, a + 3 * math.pi / 2, n):
        pts.append(p0 + r0 * np.array([math.cos(t), math.sin(t)]))
    for t in np.linspace(a - math.pi / 2, a + math.pi / 2, n):
        pts.append(p1 + r1 * np.array([math.cos(t), math.sin(t)]))
    return np.array(pts)


def elip(c, rx, ry, ang=0.0, n=28):
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    x, y = rx * np.cos(t), ry * np.sin(t)
    ca, sa = math.cos(ang), math.sin(ang)
    return np.stack([c[0] + x * ca - y * sa, c[1] + x * sa + y * ca], 1)


def tubo(pts, w0, w1, n=8):
    """Tubo con anchura variable a lo largo de una curva (poligono)."""
    c = spl(pts, n, closed=False)
    m = len(c)
    ws = np.linspace(w0, w1, m)
    d = np.gradient(c, axis=0)
    d /= (np.linalg.norm(d, axis=1, keepdims=True) + 1e-6)
    nr = np.stack([-d[:, 1], d[:, 0]], 1)
    L = c + nr * ws[:, None] / 2
    R = c - nr * ws[:, None] / 2
    return np.vstack([L, R[::-1]])


_RUIDO = {}


def ruido(escala, seed):
    k = (escala, seed)
    if k not in _RUIDO:
        r = np.random.RandomState(seed)
        g = r.rand(max(2, 1700 // escala), max(2, 1700 // escala)).astype(np.float32)
        _RUIDO[k] = cv2.resize(g, (1700, 1700), interpolation=cv2.INTER_CUBIC)
    return _RUIDO[k]


class Cv:
    """Lienzo RGB+alfa con origen (ox, oy): todas las operaciones usan coordenadas absolutas y solo tocan su caja."""

    def __init__(self, w, h, ox=0, oy=0):
        self.w, self.h, self.ox, self.oy = int(w), int(h), ox, oy
        self.c = np.zeros((self.h, self.w, 3), np.float32)
        self.a = np.zeros((self.h, self.w), np.float32)

    def copia(self):
        o = Cv(self.w, self.h, self.ox, self.oy)
        o.c, o.a = self.c.copy(), self.a.copy()
        return o

    # --- mascara de una forma (poligono, lista de poligonos)
    def forma(self, shapes, pad=3):
        if isinstance(shapes, np.ndarray) or (len(shapes) and np.ndim(shapes[0]) == 1):
            shapes = [shapes]
        shapes = [np.asarray(s, np.float32) - [self.ox, self.oy] for s in shapes]
        P = np.vstack(shapes)
        x0, y0 = max(0, int(math.floor(P[:, 0].min())) - pad), max(0, int(math.floor(P[:, 1].min())) - pad)
        x1, y1 = min(self.w, int(math.ceil(P[:, 0].max())) + pad + 1), min(self.h, int(math.ceil(P[:, 1].max())) + pad + 1)
        if x1 <= x0 or y1 <= y0:
            return None
        m = np.zeros((y1 - y0, x1 - x0), np.uint8)
        for s in shapes:
            cv2.fillPoly(m, [np.round((s - [x0, y0]) * 16).astype(np.int32)], 255, cv2.LINE_AA, 4)
        return m, (x0, y0, x1, y1)

    def pegar(self, shapes, dark, lit, radio=40, outline=6, grano=7, seed=1, luz=(-0.55, -0.83), kluz=0.5, ocol=None,
              oalpha=1.0, mult=1.0):
        r = self.forma(shapes, pad=outline + 3)
        if r is None:
            return None
        m, (x0, y0, x1, y1) = r
        mb = (m > 127).astype(np.uint8)
        dist = cv2.distanceTransform(mb, cv2.DIST_L2, 3)
        t = np.clip(dist / radio, 0, 1)
        t = t * t * (3 - 2 * t)
        hg = cv2.GaussianBlur(np.minimum(dist, radio * 1.3), (0, 0), max(1.5, radio * 0.35))
        gx = cv2.Sobel(hg, cv2.CV_32F, 1, 0, ksize=3) / 8.0
        gy = cv2.Sobel(hg, cv2.CV_32F, 0, 1, ksize=3) / 8.0
        li = np.clip(-(gx * luz[0] + gy * luz[1]) / max(radio * 0.06, 0.4), -1, 1)
        col = np.array(dark, np.float32) * (1 - t[..., None]) + np.array(lit, np.float32) * t[..., None]
        col = col * (1 + kluz * li[..., None] * 0.55)
        gr = (ruido(3, seed)[y0 + self.oy:y1 + self.oy, x0 + self.ox:x1 + self.ox] - 0.5) * grano \
            + (ruido(19, seed + 5)[y0 + self.oy:y1 + self.oy, x0 + self.ox:x1 + self.ox] - 0.5) * grano * 1.3
        col = (col + gr[..., None]) * mult
        mf = m.astype(np.float32) / 255
        if outline:
            ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (outline * 2 + 1, outline * 2 + 1))
            o = cv2.dilate(m, ker).astype(np.float32) / 255 * oalpha
            oc = OUTC if ocol is None else np.array(ocol, np.float32)
            roi = self.c[y0:y1, x0:x1]
            roi[:] = roi * (1 - o[..., None]) + oc * o[..., None]
            self.a[y0:y1, x0:x1] = np.maximum(self.a[y0:y1, x0:x1], o)
        roi = self.c[y0:y1, x0:x1]
        roi[:] = roi * (1 - mf[..., None]) + col * mf[..., None]
        self.a[y0:y1, x0:x1] = np.maximum(self.a[y0:y1, x0:x1], mf)
        return mf, (x0, y0, x1, y1)

    def ref(self, shapes, pad=2):
        r = self.forma(shapes, pad=pad)
        return None if r is None else (r[0].astype(np.float32) / 255, r[1])

    def sobre(self, ref, shapes, color, alpha=1.0, blur=0, w=0):
        """Pinta `shapes` (poligono relleno, o polilinea si w>0) recortado por la forma `ref` (None = sin recorte)."""
        if ref is None:
            return
        mf, (x0, y0, x1, y1) = ref
        loc = np.zeros((y1 - y0, x1 - x0), np.uint8)
        if isinstance(shapes, np.ndarray) or (len(shapes) and np.ndim(shapes[0]) == 1):
            shapes = [shapes]
        for s in shapes:
            P = (np.asarray(s, np.float32) - [self.ox + x0, self.oy + y0])
            P = np.round(P * 16).astype(np.int32)
            if w > 0:
                cv2.polylines(loc, [P], False, 255, int(max(1, round(w))), cv2.LINE_AA, 4)
            else:
                cv2.fillPoly(loc, [P], 255, cv2.LINE_AA, 4)
        a = loc.astype(np.float32) / 255
        if blur > 0:
            a = cv2.GaussianBlur(a, (0, 0), blur)
        a = a * mf * alpha
        roi = self.c[y0:y1, x0:x1]
        roi[:] = roi * (1 - a[..., None]) + np.array(color, np.float32) * a[..., None]
        self.a[y0:y1, x0:x1] = np.maximum(self.a[y0:y1, x0:x1], a)

    def trazo(self, pts, w, color, alpha=1.0, blur=0):
        """Trazo libre (sin recorte)."""
        P = np.asarray(pts, np.float32) - [self.ox, self.oy]
        pad = int(w) + 4 + int(blur * 3)
        x0, y0 = max(0, int(P[:, 0].min()) - pad), max(0, int(P[:, 1].min()) - pad)
        x1, y1 = min(self.w, int(P[:, 0].max()) + pad), min(self.h, int(P[:, 1].max()) + pad)
        if x1 <= x0 or y1 <= y0:
            return
        loc = np.zeros((y1 - y0, x1 - x0), np.uint8)
        cv2.polylines(loc, [np.round((P - [x0, y0]) * 16).astype(np.int32)], False, 255, int(max(1, round(w))), cv2.LINE_AA, 4)
        a = loc.astype(np.float32) / 255 * alpha
        if blur > 0:
            a = cv2.GaussianBlur(a, (0, 0), blur)
        roi = self.c[y0:y1, x0:x1]
        roi[:] = roi * (1 - a[..., None]) + np.array(color, np.float32) * a[..., None]
        self.a[y0:y1, x0:x1] = np.maximum(self.a[y0:y1, x0:x1], a if alpha >= 0.95 else 0)

    def mancha(self, c, rx, ry, color, alpha, ang=0.0, blur=18):
        """Mancha suave (elipse difusa), sin recorte."""
        self.trazo_elipse(c, rx, ry, color, alpha, ang, blur)

    def trazo_elipse(self, c, rx, ry, color, alpha, ang=0.0, blur=18):
        pad = int(max(rx, ry) + blur * 3 + 4)
        cx, cy = c[0] - self.ox, c[1] - self.oy
        x0, y0 = max(0, int(cx) - pad), max(0, int(cy) - pad)
        x1, y1 = min(self.w, int(cx) + pad), min(self.h, int(cy) + pad)
        if x1 <= x0 or y1 <= y0:
            return
        loc = np.zeros((y1 - y0, x1 - x0), np.uint8)
        cv2.ellipse(loc, (int(cx - x0), int(cy - y0)), (int(rx), int(ry)), math.degrees(ang), 0, 360, 255, -1, cv2.LINE_AA)
        a = cv2.GaussianBlur(loc.astype(np.float32) / 255, (0, 0), blur) * alpha
        roi = self.c[y0:y1, x0:x1]
        roi[:] = roi * (1 - a[..., None]) + np.array(color, np.float32) * a[..., None]

    def sobre_cv(self, o, dx=0, dy=0):
        """Compone otro Cv (con su origen) sobre este."""
        x0, y0 = int(o.ox + dx - self.ox), int(o.oy + dy - self.oy)
        xa, ya = max(0, x0), max(0, y0)
        xb, yb = min(self.w, x0 + o.w), min(self.h, y0 + o.h)
        if xb <= xa or yb <= ya:
            return
        sub = (slice(ya - y0, yb - y0), slice(xa - x0, xb - x0))
        a = o.a[sub][..., None]
        roi = self.c[ya:yb, xa:xb]
        roi[:] = roi * (1 - a) + o.c[sub] * a
        self.a[ya:yb, xa:xb] = np.maximum(self.a[ya:yb, xa:xb], o.a[sub])


def mezcla(a, b, t):
    return np.array(a, np.float32) * (1 - t) + np.array(b, np.float32) * t


# ------------------------------------------------------------------------------------------------ geometria de la cabeza
CARA = [(528, 112), (610, 128), (672, 178), (702, 258), (708, 330), (692, 396), (656, 448), (606, 494), (552, 518), (494, 512),
        (436, 486), (386, 438), (346, 372), (333, 292), (342, 214), (384, 150), (450, 116)]
OJO_N = dict(c=(447, 290), w=56, h=37, d=1)        # ojo cercano (izquierda del cuadro)
OJO_F = dict(c=(616, 294), w=46, h=34, d=-1)       # ojo lejano
BOCA = (572, 456)

# expresiones: cejas (inner_dy, outer_dy, arco) por ceja cercana/lejana, parpado, mirada, boca, cabeza
EXPR = {
    "neutral": dict(cn=(6, 2, 4), cf=(6, 0, 4), ap=0.82, corte=0, bajo=0.0, mir=(0.45, 0.0), boca=dict(w=1.0, curva=-0.10, abre=0.0, sesgo=0.0, dientes=0),
                    cab=(0, 0, 0), rubor=0.0, arrugas=0.2),
    "severo": dict(cn=(22, -6, 2), cf=(22, -8, 2), ap=0.62, corte=9, bajo=0.35, mir=(0.5, 0.0), boca=dict(w=0.9, curva=-0.55, abre=0.0, sesgo=0.0, dientes=0),
                   cab=(-1.5, -10, 6), rubor=0.1, arrugas=0.9),
    "indignado": dict(cn=(30, -14, -2), cf=(30, -16, -2), ap=0.95, corte=11, bajo=0.0, mir=(0.5, 0.0), boca=dict(w=1.15, curva=-0.6, abre=0.85, sesgo=0.0, dientes=2),
                      cab=(2, 6, -4), rubor=0.75, arrugas=1.0),
    "orgulloso": dict(cn=(-16, -4, 12), cf=(-14, -2, 12), ap=0.5, corte=0, bajo=0.0, mir=(0.4, -0.1), boca=dict(w=0.85, curva=0.5, abre=0.0, sesgo=0.25, dientes=0),
                      cab=(-3, -16, 6), rubor=0.25, arrugas=0.15),
    "sorprendido": dict(cn=(-30, -22, 20), cf=(-30, -22, 20), ap=1.35, corte=0, bajo=0.0, mir=(0.5, 0.0), boca=dict(w=0.62, curva=0.0, abre=1.0, sesgo=0.0, dientes=1, redonda=1),
                        cab=(0, 6, -6), rubor=0.1, arrugas=1.0, frente=1.0),
    "pensativo": dict(cn=(4, -4, 4), cf=(-22, -18, 16), ap=0.8, corte=0, bajo=0.1, mir=(0.7, -0.8), boca=dict(w=0.6, curva=-0.2, abre=0.0, sesgo=-0.35, dientes=0),
                      cab=(5, -4, -4), rubor=0.0, arrugas=0.45),
    "burlon": dict(cn=(10, 8, 0), cf=(-28, -10, 22), ap=0.58, corte=3, bajo=0.15, mir=(0.6, 0.15), boca=dict(w=1.0, curva=0.45, abre=0.22, sesgo=0.55, dientes=1),
                   cab=(-5, -6, 2), rubor=0.15, arrugas=0.5),
    "anotando": dict(cn=(10, 2, 3), cf=(8, 0, 3), ap=0.62, corte=2, bajo=0.15, mir=(0.35, 0.95), boca=dict(w=0.7, curva=-0.2, abre=0.0, sesgo=0.2, dientes=0),
                     cab=(0, -2, 0), rubor=0.0, arrugas=0.3),
}
NOMBRES = list(EXPR)


# ------------------------------------------------------------------------------------------------ cabeza (parte estatica)
_CACHE = {}


def cabeza_estatica(rojo=0):
    if ("cab", rojo) in _CACHE:
        return _CACHE[("cab", rojo)]
    L = Cv(660, 660, 220, 0)
    rng = np.random.RandomState(7)
    # --- pelo trasero (volumen plateado ondulado que baja por detras de las orejas)
    back = [(324, 300), (308, 215), (326, 146), (382, 92), (470, 64), (574, 66), (652, 98), (708, 160), (728, 240), (722, 326),
            (706, 380), (690, 412), (664, 400), (650, 360), (420, 340), (396, 396), (376, 420), (352, 412), (328, 380)]
    mb = L.pegar(spl(back, 8), PELO_D * 0.9, PELO_L * 0.96, radio=40, outline=7, seed=3, grano=9)
    for _ in range(46):                                             # mechas ondulantes
        x0, y0 = rng.uniform(330, 740), rng.uniform(50, 330)
        a = rng.uniform(1.2, 2.0)
        pts = [(x0 + k * 16 * math.cos(a) + 5 * math.sin(k * 1.2), y0 + k * 16 * math.sin(a)) for k in range(7)]
        L.sobre(mb, np.array(pts), PELO_D * (1.0 if rng.rand() < .6 else 1.2), 0.30, w=3)
    # --- oreja cercana
    L.pegar(elip((343, 322), 31, 62, 0.08), PIEL_D * 1.15, PIEL_M * 1.05, radio=22, outline=6, seed=11)
    # --- cuello
    # --- cara
    cara = spl(CARA, 9)
    mf = L.pegar(cara, PIEL_D, PIEL_L, radio=130, outline=7, seed=21, grano=7, kluz=0.9)
    # rubor y modelado
    if rojo:
        L.sobre(mf, elip((520, 330), 200, 190), np.array([226, 62, 62.]), 0.55, blur=40)
    L.sobre(mf, elip((402, 392), 56, 46), np.array([226, 120, 110.]), 0.28, blur=26)
    L.sobre(mf, elip((650, 396), 40, 40), np.array([226, 120, 110.]), 0.22, blur=24)
    L.sobre(mf, elip((520, 120), 110, 60), PIEL_L * 1.04, 0.5, blur=30)           # luz en la frente
    L.sobre(mf, [(560, 520), (700, 440), (720, 560), (560, 560)], PIEL_D * 0.5, 0.45, blur=24)    # sombra mandibula lejana
    L.sobre(mf, [(330, 380), (440, 500), (420, 560), (320, 520)], PIEL_D * 0.55, 0.5, blur=22)    # mandibula cercana
    # pomulos hundidos (cara de viejo): sombras bajo los pomulos
    L.sobre(mf, bez((372, 376), (400, 430), (468, 464), 12), PIEL_D * 0.7, 0.30, blur=8, w=22)
    L.sobre(mf, bez((676, 372), (664, 420), (628, 446), 12), PIEL_D * 0.7, 0.28, blur=8, w=18)
    # --- cuencas de los ojos
    for o in (OJO_N, OJO_F):
        cx, cy = o["c"]
        L.sobre(mf, elip((cx, cy - 4), o["w"] * 1.55, o["h"] * 1.9), PIEL_D * 0.62, 0.45, blur=15)
    # bolsas bajo los ojos (lineas)
    L.sobre(mf, bez((402, 330), (448, 352), (500, 334), 12), PIEL_D * 0.6, 0.65, blur=1, w=4)
    L.sobre(mf, bez((580, 334), (616, 350), (652, 336), 12), PIEL_D * 0.6, 0.55, blur=1, w=4)
    # --- nariz de aguila (forma propia con volumen)
    nariz = [(548, 262), (574, 262), (596, 306), (618, 346), (640, 384), (640, 410), (606, 424), (572, 420), (548, 408), (536, 380),
             (538, 330)]
    mn = L.pegar(spl(nariz, 7), PIEL_D * 1.05, PIEL_L * 1.02, radio=32, outline=5, seed=31, ocol=np.array([100, 56, 52.]), oalpha=0.85, kluz=1.0)
    L.sobre(mn, [(606, 330), (640, 400), (660, 420), (680, 330)], PIEL_D * 0.55, 0.55, blur=7)     # lado lejano en sombra
    L.sobre(mn, bez((556, 280), (572, 340), (600, 392), 10), np.array([255, 232, 210.]), 0.55, blur=3, w=7)   # brillo del puente
    L.sobre(mn, elip((588, 416), 30, 12), np.array([60, 20, 24.]), 0.85, blur=2)                    # fosa nasal
    L.sobre(mn, [(544, 394), (528, 410), (556, 428), (566, 410)], PIEL_D * 0.45, 0.6, blur=3)       # ala de la nariz
    L.trazo(bez((542, 398), (550, 424), (584, 432), 10), 4, np.array([96, 50, 48.]), 0.8)
    # sombra de la nariz sobre la mejilla/labio
    L.sobre(mf, [(560, 420), (640, 410), (664, 470), (590, 470)], PIEL_D * 0.5, 0.35, blur=12)
    # --- surcos nasogenianos y barbilla
    L.sobre(mf, bez((530, 424), (512, 460), (518, 492), 10), PIEL_D * 0.55, 0.6, blur=1, w=4)
    L.sobre(mf, bez((652, 430), (654, 462), (640, 484), 10), PIEL_D * 0.55, 0.5, blur=1, w=3)
    L.sobre(mf, elip((560, 492), 34, 14), PIEL_D * 0.7, 0.30, blur=8)
    L.sobre(mf, elip((556, 502), 24, 8), PIEL_L * 1.05, 0.35, blur=5)                    # luz en la barbilla
    # --- patillas plateadas (cercana y lejana)
    pn = [(344, 210), (386, 240), (398, 322), (420, 400), (470, 456), (452, 492), (400, 486), (352, 424), (330, 330)]
    mp = L.pegar(spl(pn, 8), PELO_D, PELO_L, radio=26, outline=6, seed=41, grano=9)
    pf = [(692, 232), (664, 262), (672, 332), (660, 398), (638, 444), (672, 452), (710, 392), (722, 310)]
    mp2 = L.pegar(spl(pf, 8), PELO_D * 0.9, PELO_L * 0.95, radio=22, outline=6, seed=42, grano=9)
    for ref, base, n_, a0 in ((mp, (360, 250), 30, 1.35), (mp2, (690, 260), 22, 1.62)):
        for _ in range(n_):
            x0 = base[0] + rng.uniform(-20, 40) * (1 if ref is mp else -0.4)
            y0 = base[1] + rng.uniform(0, 210)
            pts = [(x0 + k * 7 * math.cos(a0 + 0.35 * math.sin(k)) , y0 + k * 12) for k in range(6)]
            L.sobre(ref, np.array(pts), PELO_D * 0.85, 0.30, w=3)
        for _ in range(14):
            x0 = base[0] + rng.uniform(-10, 40) * (1 if ref is mp else -0.4)
            y0 = base[1] + rng.uniform(0, 210)
            L.sobre(ref, np.array([(x0, y0), (x0 + 6, y0 + 22)]), np.array([255, 252, 246.]), 0.4, w=3)
    # --- pelo frontal (peinado hacia atras, entradas profundas: frente amplia)
    ext = [(334, 214), (330, 156), (360, 104), (432, 70), (526, 58), (616, 70), (682, 106), (712, 164), (708, 238), (688, 236)]
    inte = [(668, 214), (642, 172), (590, 150), (528, 144), (470, 150), (420, 174), (388, 214), (372, 250), (346, 250)]
    fr = spl(ext, 8, closed=False)
    fr = np.vstack([fr, spl(inte, 8, closed=False)])
    mh = L.pegar(fr, PELO_D, PELO_L * 1.02, radio=30, outline=7, seed=51, grano=9)
    for k in range(60):                                                 # mechas peinadas hacia atras (curvas hacia arriba-izquierda)
        u = rng.uniform(0, 1)
        x0 = 380 + u * 310
        y0 = 190 - 40 * math.sin(u * math.pi) + rng.uniform(-6, 12)
        ang = math.pi * 1.12 + (u - 0.5) * 0.9
        pts = [(x0 + j * 22 * math.cos(ang + 0.10 * j), y0 + j * 22 * math.sin(ang + 0.10 * j) - j * j * 1.3) for j in range(7)]
        L.sobre(mh, np.array(pts), PELO_D * (0.9 if k % 3 else 1.2), 0.34 if k % 2 else 0.18, w=3 if k % 3 else 4)
    for k in range(18):
        u = rng.uniform(0, 1)
        x0 = 400 + u * 290
        y0 = 170 - 34 * math.sin(u * math.pi)
        ang = math.pi * 1.12 + (u - 0.5) * 0.9
        pts = [(x0 + j * 22 * math.cos(ang + 0.10 * j), y0 + j * 22 * math.sin(ang + 0.10 * j) - j * j * 1.3) for j in range(6)]
        L.sobre(mh, np.array(pts), np.array([255, 253, 246.]), 0.5, w=3)
    L.sobre(mf, [(380, 214), (528, 150), (690, 214), (690, 130), (380, 130)], np.array([70, 40, 46.]), 0.0)
    # sombra del pelo sobre la frente
    mfa = L.forma(spl(CARA, 9), pad=2)
    if mfa:
        mm = (mfa[0].astype(np.float32) / 255, mfa[1])
        L.sobre(mm, [(380, 190), (470, 160), (560, 150), (650, 170), (700, 236), (700, 190), (560, 120), (380, 130)], PIEL_D * 0.55, 0.0)
    _CACHE[("cab", rojo)] = L
    return L


# ------------------------------------------------------------------------------------------------ rasgos dinamicos
def _ojo(L, o, ap, corte, bajo, mir, parp, sombra_c=PIEL_D):
    """Ojo animable. ap: apertura (0..1.4), corte: pixeles que baja el parpado en la esquina interna (ceno fruncido)."""
    cx, cy = o["c"]
    w, h, d = o["w"], o["h"], o["d"]
    ap = max(0.0, ap * (1 - parp))
    u = np.linspace(0, 1, 16)
    xs = cx - d * w + d * 2 * w * u
    top = cy - h * ap * np.sin(np.pi * u) ** 0.75 + corte * (u ** 1.5) * (0.4 + 0.6 * ap) + 3 * (1 - u) * (1 - ap) * 0
    low = cy + h * (0.55 + 0.25 * ap) * (1 - bajo * 0.55) * np.sin(np.pi * u) ** 0.9 - bajo * h * 0.25 * np.sin(np.pi * u)
    low = np.maximum(low, top + 1.5)
    poly = np.vstack([np.stack([xs, top], 1), np.stack([xs[::-1], low[::-1]], 1)])
    blanco = L.pegar(poly, np.array([196, 176, 170.]), np.array([252, 246, 238.]), radio=18, outline=0, seed=61, grano=3)
    if blanco is None:
        return
    if ap > 0.12:
        # iris con mirada
        gx, gy = mir
        r = min(h * ap * 0.92 + 4, w * 0.50)
        ix = cx + (gx - 0.5) * w * 0.9
        iy = cy + gy * h * 0.42 - (1 - ap) * 2
        ic = elip((ix, iy), r, r)
        L.sobre(blanco, ic, np.array([46, 66, 86.]), 1.0)                                  # anillo oscuro
        L.sobre(blanco, elip((ix, iy + 1), r * 0.84, r * 0.84), np.array([96, 134, 156.]), 1.0)
        L.sobre(blanco, elip((ix, iy + r * 0.32), r * 0.62, r * 0.46), np.array([150, 188, 196.]), 0.7, blur=2)
        pr = r * (0.50 if ap < 1.2 else 0.36)
        L.sobre(blanco, elip((ix, iy), pr, pr), np.array([10, 10, 16.]), 1.0)
        L.sobre(blanco, elip((ix - r * 0.32, iy - r * 0.34), r * 0.20, r * 0.20), np.array([255, 255, 255.]), 0.95)
        L.sobre(blanco, elip((ix + r * 0.30, iy + r * 0.34), r * 0.09, r * 0.09), np.array([230, 244, 255.]), 0.7)
        # sombra del parpado superior sobre el globo
        L.sobre(blanco, np.vstack([np.stack([xs, top - 2], 1), np.stack([xs[::-1], (top + h * 0.5 * (1 - bajo * 0.4))[::-1]], 1)]),
                np.array([60, 40, 50.]), 0.38, blur=5)
        # sombra lateral (globo redondo)
        L.sobre(blanco, elip((cx - d * w * 1.0, cy), w * 0.35, h * 1.3), np.array([150, 120, 120.]), 0.35, blur=6)
    # parpado superior: piel + linea gruesa de pestanas
    pts = np.stack([xs, top], 1)
    # pliegue (piel del parpado) sobre el ojo
    pl = np.stack([xs, top - h * 0.65 * (0.35 + 0.65 * (1 - parp)) - corte * 0.2 * u], 1)
    L.trazo(pl, 4, np.array([112, 62, 58.]), 0.65, blur=0.6)
    L.trazo(pts, 7, np.array([32, 18, 18.]), 1.0)
    # pestanas: remate en la esquina externa
    ex, ey = pts[0]
    L.trazo(np.array([(ex, ey), (ex - d * 12, ey + 3), (ex - d * 20, ey + 12)]), 6, np.array([32, 18, 18.]), 1.0)
    # linea inferior (suave)
    lo = np.stack([xs, low], 1)
    L.trazo(lo[2:-2], 3, np.array([110, 60, 56.]), 0.8, blur=0.5)
    # parpado cerrado: si casi no hay apertura, una curva
    if ap <= 0.12:
        L.trazo(np.stack([xs, cy + 4 + 5 * np.sin(np.pi * u)], 1), 7, np.array([32, 18, 18.]), 1.0)
        L.trazo(np.stack([xs[2:-2], cy + 14 + 4 * np.sin(np.pi * u[2:-2])], 1), 3, np.array([110, 60, 56.]), 0.6, blur=0.5)


def _ceja(L, d, inner, outer, arco, x_in, x_out, y0, grosor=26, mid_dy=0, seed=0):
    """Ceja gruesa y peluda de x_out (exterior) a x_in (interior). dy negativo = sube."""
    rng = np.random.RandomState(seed)
    u = np.linspace(0, 1, 7)
    xs = x_out + (x_in - x_out) * u
    ys = y0 + outer * (1 - u) + inner * u - arco * np.sin(np.pi * u) ** 0.9 + mid_dy * np.sin(np.pi * u)
    cen = np.stack([xs, ys], 1)
    gr = (grosor * (0.52 + 0.48 * np.sin(np.pi * np.clip(u * 0.85 + 0.12, 0, 1)) ** 0.7)) * np.linspace(0.78, 1.12, 7)
    c = spl(cen, 6, closed=False)
    ws = np.interp(np.linspace(0, 1, len(c)), np.linspace(0, 1, 7), gr)
    dd = np.gradient(c, axis=0)
    dd /= (np.linalg.norm(dd, axis=1, keepdims=True) + 1e-6)
    nr = np.stack([-dd[:, 1], dd[:, 0]], 1)
    sg = -np.sign(nr[:, 1].mean() + 1e-6)
    top = c + nr * ws[:, None] * 0.55 * sg
    bot = c - nr * ws[:, None] * 0.45 * sg
    poly = np.vstack([top, bot[::-1]])
    m = L.pegar(poly, CEJA_C * 0.62, CEJA_C * 1.15, radio=12, outline=5, seed=71 + seed, grano=6)
    if m is None:
        return
    for _ in range(26):                                            # pelos peinados hacia arriba y afuera
        k = rng.randint(0, len(c) - 1)
        p = c[k] + nr[k] * rng.uniform(-0.4, 0.4) * ws[k] * sg
        a = math.atan2(dd[k, 1], dd[k, 0]) + (math.pi if d > 0 else 0) + rng.uniform(-0.5, 0.2)
        ln = rng.uniform(10, 26)
        q = p + ln * np.array([math.cos(a), math.sin(a)]) * (-1)
        L.trazo(np.array([p, q]), 2.2, CEJA_C * rng.uniform(0.55, 1.35), 0.8)
    L.sobre(m, c + nr * 0, np.array([160, 150, 148.]), 0.35, w=3)


def _boca(L, bo, habla):
    mx, my = BOCA
    w = 78 * bo["w"]
    curva = bo["curva"]
    ab = min(1.0, bo.get("abre", 0.0) + habla * 0.55)
    ses = bo.get("sesgo", 0.0)
    redonda = bo.get("redonda", 0)
    Lp = np.array([mx - w, my - curva * 16 - ses * 10])
    Rp = np.array([mx + w * 0.82, my - curva * 16 + ses * 22 * (1 if ses > 0 else 0.7) - ses * 4])
    if ses > 0:       # sonrisa torcida: sube la comisura lejana
        Rp = np.array([mx + w * 0.82, my - curva * 16 - ses * 22])
        Lp = np.array([mx - w, my - curva * 16 + ses * 4])
    if ses < 0:       # boca de lado, pensativa
        Lp = np.array([mx - w, my - curva * 16 + ses * -4])
        Rp = np.array([mx + w * 0.82, my - curva * 16 + ses * 6])
    lab = np.array([166, 92, 90.])
    labo = np.array([120, 58, 62.])
    if ab < 0.05:
        up = bez(Lp, (mx, my - 6 - curva * 4), Rp, 14)
        lo = bez(Lp, (mx, my + 14 - curva * 6), Rp, 14)
        poly = np.vstack([up, lo[::-1]])
        m = L.pegar(poly, labo, lab, radio=7, outline=4, seed=81, grano=3)
        L.trazo(bez(Lp, (mx, my + 1 - curva * 4), Rp, 16), 4, np.array([60, 22, 28.]), 1.0)
        if m is not None:
            L.sobre(m, bez(Lp + [6, 5], (mx, my + 8), Rp + [-4, 5], 12), np.array([230, 160, 150.]), 0.45, blur=2, w=5)
        L.trazo(np.array([Lp + [-6, curva * 4 - 2], Lp + [2, 0]]), 4, np.array([90, 40, 42.]), 0.9)
        return
    H_ = 14 + ab * 52
    if redonda:
        cen = (mx + 6, my + 12)
        ex = elip(cen, 30 * bo["w"] + 8, H_ * 0.8 + 6)
        m = L.pegar(ex, labo, lab, radio=8, outline=5, seed=82, grano=3)
        L.sobre(m, elip((cen[0], cen[1] + 4), 24 * bo["w"] + 4, H_ * 0.65), np.array([60, 18, 26.]), 1.0)
        L.sobre(m, elip((cen[0] + 2, cen[1] + H_ * 0.45), 16, 9), np.array([190, 84, 90.]), 0.9, blur=1)
        L.sobre(m, [(cen[0] - 22, cen[1] - H_ * 0.62), (cen[0] + 22, cen[1] - H_ * 0.62), (cen[0] + 18, cen[1] - H_ * 0.2), (cen[0] - 18, cen[1] - H_ * 0.2)],
                np.array([240, 232, 218.]), 0.95, blur=0.7)
        return
    up = bez(Lp, (mx, my - 12 - curva * 4), Rp, 14)
    lo = bez(Lp + [4, 4], (mx + 4, my + H_ + 8 - curva * 6), Rp + [-4, 4], 14)
    poly = np.vstack([up, lo[::-1]])
    m = L.pegar(poly, labo, lab, radio=10, outline=5, seed=83, grano=3)
    if m is None:
        return
    inter = np.vstack([bez(Lp + [6, 4], (mx, my - 4 - curva * 4), Rp + [-6, 4], 14), bez(Lp + [10, 6], (mx + 3, my + H_ - 4), Rp + [-10, 6], 14)[::-1]])
    L.sobre(m, inter, np.array([54, 14, 24.]), 1.0)
    if bo.get("dientes", 0) >= 1:
        if bo["dientes"] >= 2:                                                # grito: dientes superiores e inferiores
            L.sobre(m, [(mx - w * 0.78, my - 8), (mx + w * 0.7, my - 8), (mx + w * 0.7, my + 14 + ab * 8), (mx - w * 0.78, my + 12 + ab * 8)],
                    np.array([246, 238, 222.]), 1.0, blur=0.5)
            for k in range(1, 8):
                x = mx - w * 0.78 + (w * 1.48) * k / 8
                L.sobre(m, np.array([(x, my - 8), (x, my + 14 + ab * 8)]), np.array([150, 120, 110.]), 0.7, w=2)
            L.sobre(m, [(mx - w * 0.6, my + H_ - 4), (mx + w * 0.5, my + H_ - 4), (mx + w * 0.4, my + H_ - 22), (mx - w * 0.5, my + H_ - 22)],
                    np.array([236, 228, 210.]), 0.95, blur=0.5)
        else:
            L.sobre(m, [(mx - w * 0.62, my - 8), (mx + w * 0.55, my - 8), (mx + w * 0.55, my + 8 + ab * 10), (mx - w * 0.62, my + 8 + ab * 10)],
                    np.array([246, 238, 222.]), 1.0, blur=0.5)
    L.sobre(m, elip((mx + 6, my + H_ * 0.85), w * 0.46, H_ * 0.34), np.array([196, 92, 96.]), 0.95, blur=1.5)   # lengua
    L.trazo(up, 4, np.array([70, 28, 32.]), 0.9)
    L.trazo(lo[2:-2], 3, np.array([90, 40, 44.]), 0.8)
    L.trazo(np.array([Lp + [-6, curva * 4 - 3], Lp + [2, 0]]), 4, np.array([90, 40, 42.]), 0.9)


def _arrugas(L, expr, par):
    """Arrugas de la frente y entrecejo segun la expresion y la altura de cejas."""
    k = expr.get("arrugas", 0.3)
    fr = expr.get("frente", 0.0)
    avg_inner = (par["cn"][0] + par["cf"][0]) / 2
    sube = max(0, -(par["cn"][2] + par["cf"][2]) / 2 - avg_inner * 0.0 + (-avg_inner) * 0.4)
    col = np.array([140, 84, 80.])
    n = 3
    for i in range(n):
        y = 176 + i * 17 - sube * 0.35 + fr * -6
        a = 0.17 + 0.20 * (k if fr == 0 else 1.0)
        pts = bez((410, y + 4 + i), (524, y - 8 - fr * 6), (664, y + 6), 12)
        L.trazo(pts, 3, col, a, blur=0.8)
    # entrecejo: dos surcos verticales cuando se frunce
    if avg_inner > 12:
        f = min(1.0, (avg_inner - 8) / 22)
        L.trazo(np.array([(540, 246), (538, 270)]), 5, col, 0.55 * f, blur=1.2)
        L.trazo(np.array([(558, 248), (562, 268)]), 4, col, 0.45 * f, blur=1.2)
    # patas de gallo cuando se arruga
    return


def cabeza(expr, fase, hab=0.0, parp_forzado=None):
    ex = EXPR[expr]
    base = cabeza_estatica(0)
    L = base.copia()
    if ex["rubor"] > 0.05:
        k = min(1.0, ex["rubor"])
        L.c = L.c * (1 - k) + cabeza_estatica(1).c * k
    # parpadeo
    ph = fase % 1.0
    parp = 0.0
    if 0.80 <= ph <= 0.88:
        u = (ph - 0.80) / 0.08
        parp = math.sin(u * math.pi) ** 0.8
    if parp_forzado is not None:
        parp = parp_forzado
    # microderiva de la mirada
    mx, my = ex["mir"]
    mx += 0.07 * math.sin(2 * math.pi * fase * 1.0 + 1.0)
    my += 0.05 * math.sin(2 * math.pi * fase * 2.0)
    # cejas: respiran un poco
    wob = 1.5 * math.sin(2 * math.pi * fase + 0.6)
    par = dict(cn=ex["cn"], cf=ex["cf"])
    ap = ex["ap"]
    # ojos
    _ojo(L, OJO_N, ap * 1.02, ex["corte"], ex["bajo"], (mx, my), parp)
    _ojo(L, OJO_F, ap * 0.98, ex["corte"] * 0.9, ex["bajo"], (mx, my), parp)
    # cejas
    cn, cf = ex["cn"], ex["cf"]
    _ceja(L, 1, cn[0] * 1.4 + wob * 0.5, cn[1] * 1.4 + wob, cn[2] * 1.3, 514, 362, 238, grosor=40, seed=1)
    _ceja(L, -1, cf[0] * 1.4 + wob * 0.5, cf[1] * 1.4 + wob, cf[2] * 1.3, 568, 680, 244, grosor=34, seed=2)
    _arrugas(L, ex, par)
    # rubor extra (indignado)
    # boca
    _boca(L, ex["boca"], hab)
    # monoculo en el ojo cercano (siempre): aro, cristal, reflejo, cadena
    return L


def monoculo(L, dy=0.0, dx=0.0, alpha=1.0):
    cx, cy = OJO_N["c"]
    c = (cx + dx, cy + dy + 2)
    aro = elip(c, 62, 62)
    aroi = elip(c, 52, 52)
    L.trazo(np.vstack([aro, aro[:1]]), 11, np.array([46, 34, 22.]), 1.0)
    L.trazo(np.vstack([aro, aro[:1]]), 7, ORO_L * 0.98, 1.0)
    L.trazo(np.vstack([aroi, aroi[:1]]), 3, ORO_D, 0.9)
    m = L.forma(aroi, pad=3)
    if m:
        mf = (m[0].astype(np.float32) / 255, m[1])
        L.sobre(mf, aroi, np.array([200, 230, 255.]), 0.13)
        L.sobre(mf, [(c[0] - 40, c[1] - 14), (c[0] - 18, c[1] - 40), (c[0] - 8, c[1] - 34), (c[0] - 34, c[1] - 4)], np.array([255, 255, 255.]), 0.55, blur=1)
        L.sobre(mf, bez((c[0] + 20, c[1] + 40), (c[0] + 40, c[1] + 24), (c[0] + 46, c[1] + 4), 8), np.array([255, 255, 255.]), 0.4, blur=1, w=5)
    # cadenita
    cad = spl([(c[0] - 40, c[1] + 52), (c[0] - 74, c[1] + 130), (c[0] - 120, c[1] + 230), (c[0] - 90, c[1] + 330), (c[0] - 30, c[1] + 330)], 8, closed=False)
    L.trazo(cad, 4, np.array([46, 34, 22.]), 0.9)
    L.trazo(cad, 2, ORO_L, 0.95)


# ------------------------------------------------------------------------------------------------ cuerpo
def cuerpo(vista):
    if ("cuerpo", vista) in _CACHE:
        return _CACHE[("cuerpo", vista)]
    L = Cv(CW, CH)
    full = vista == "cuerpo"
    if full:
        # --- piernas y botas
        pn = [(440, 1060), (560, 1060), (548, 1300), (540, 1470), (420, 1470), (430, 1300)]
        pf = [(560, 1060), (690, 1060), (690, 1300), (700, 1468), (584, 1470), (572, 1300)]
        for pts, sd in ((pf, 90), (pn, 91)):
            L.pegar(spl(pts, 6), np.array([14, 12, 20.]), np.array([66, 64, 80.]), radio=48, outline=6, seed=sd, kluz=0.7)
        for (x0, x1, y1) in ((404, 548, 1536), (578, 724, 1536)):
            bota = [(x0 + 14, 1450), (x1 - 10, 1450), (x1 - 4, 1520), (x1 + 34, 1536), (x1 + 30, 1550), (x0 - 6, 1552), (x0 - 12, 1500)]
            mb = L.pegar(spl(bota, 6), np.array([8, 8, 12.]), np.array([70, 68, 84.]), radio=26, outline=6, seed=93, kluz=1.0)
            L.sobre(mb, bez((x0 + 20, 1510), (x0 + 70, 1500), (x1 - 10, 1520), 10), np.array([220, 224, 240.]), 0.45, blur=2, w=6)
    # --- faldones de la levita (solo cuerpo entero)
    if full:
        fal = [(270, 1000), (440, 1040), (660, 1040), (830, 1000), (868, 1100), (860, 1210), (800, 1240), (560, 1224), (340, 1240), (262, 1212), (250, 1100)]
        mf = L.pegar(spl(fal, 7), ABRIGO_D * 0.9, ABRIGO_L * 0.7, radio=90, outline=7, seed=95, kluz=0.9)
        L.sobre(mf, [(520, 1040), (560, 1040), (590, 1240), (540, 1240)], np.array([8, 6, 12.]), 0.6, blur=8)
        L.sobre(mf, bez((330, 1080), (345, 1150), (352, 1220), 10), np.array([140, 140, 170.]), 0.25, blur=3, w=6)
    # --- cuello (piel) bajo el cuello alto
    cuello = [(446, 470), (652, 462), (668, 560), (664, 640), (448, 640), (436, 560)]
    mc = L.pegar(spl(cuello, 6), PIEL_D * 0.9, PIEL_M, radio=60, outline=6, seed=12)
    L.sobre(mc, [(420, 468), (700, 450), (700, 570), (560, 530), (420, 570)], PIEL_D * 0.5, 0.75, blur=14)
    # --- torso (levita)
    tor = [(330, 630), (420, 598), (560, 590), (700, 596), (780, 628), (826, 704), (836, 860), (820, 1020), (560, 1060), (286, 1020), (262, 860), (272, 704)]
    mt = L.pegar(spl(tor, 7), ABRIGO_D * 0.85, ABRIGO_L * 0.85, radio=110, outline=7, seed=100, kluz=1.0)
    L.sobre(mt, [(780, 600), (880, 700), (880, 1060), (800, 1060)], np.array([6, 4, 12.]), 0.45, blur=16)
    L.sobre(mt, bez((330, 640), (270, 700), (252, 820), 12), np.array([160, 160, 196.]), 0.35, blur=5, w=14)    # luz en hombro
    # --- chaleco (V desplazada: vista 3/4)
    chal = [(486, 640), (640, 636), (668, 760), (648, 940), (570, 1030), (500, 960), (474, 800)]
    mc = L.pegar(spl(chal, 7), CHAL_D, CHAL_L, radio=60, outline=6, seed=110, kluz=0.8)
    for i in range(0, 7):                                                   # estampado
        yy = 690 + i * 44
        for xx in range(496, 660, 34):
            L.sobre(mc, elip((xx + (i % 2) * 17, yy), 7, 5), CHAL_L * 1.15, 0.35)
    for i, (bx, by) in enumerate(((600, 800), (592, 868), (584, 936))):
        L.pegar(elip((bx, by), 12, 12), ORO_D, ORO_L, radio=8, outline=3, seed=120 + i)
    L.sobre(mc, [(486, 640), (520, 650), (540, 1000), (500, 960)], np.array([30, 8, 18.]), 0.45, blur=8)
    # --- camisa y solapas
    cam = [(486, 634), (560, 612), (640, 630), (610, 720), (540, 780)]
    L.pegar(spl(cam, 6), CAMISA_D, CAMISA_L, radio=24, outline=5, seed=130)
    sol_n = [(400, 596), (486, 626), (560, 800), (560, 940), (462, 760), (396, 700)]            # solapa grande (cercana)
    ms = L.pegar(spl(sol_n, 6), ABRIGO_D * 0.9, ABRIGO_L * 0.95, radio=36, outline=6, seed=131, kluz=1.0)
    L.sobre(ms, bez((416, 620), (470, 700), (540, 860), 12), np.array([170, 170, 205.]), 0.28, blur=3, w=5)
    sol_f = [(700, 600), (650, 636), (642, 760), (666, 700), (740, 690)]
    L.pegar(spl(sol_f, 6), ABRIGO_D * 0.9, ABRIGO_L * 0.8, radio=22, outline=6, seed=132)
    # --- cadena de reloj
    cad = spl([(562, 806), (480, 850), (420, 830), (396, 800)], 8, closed=False)
    L.trazo(cad, 6, np.array([46, 34, 22.]), 1.0)
    L.trazo(cad, 3, ORO_L, 1.0)
    L.pegar(elip((396, 800), 11, 11), ORO_D, ORO_L, radio=7, outline=3, seed=140)
    _CACHE[("cuerpo", vista)] = L
    return L


def cuello_alto(L):
    """Cuello alto con puntas y corbata negra (se pinta DESPUES de la cabeza)."""
    col = [(450, 546), (500, 574), (560, 580), (620, 576), (670, 544), (692, 592), (642, 634), (560, 646), (480, 642), (430, 596)]
    mco = L.pegar(spl(col, 6), CAMISA_D, CAMISA_L, radio=28, outline=6, seed=150, kluz=0.9)
    L.sobre(mco, [(440, 560), (560, 590), (680, 560), (680, 660), (440, 660)], np.array([120, 100, 100.]), 0.20, blur=10)
    L.pegar(spl([(500, 596), (566, 608), (634, 596), (640, 660), (566, 672), (496, 660)], 6), np.array([8, 8, 14.]), np.array([70, 70, 94.]), radio=22, outline=5, seed=151)
    L.pegar(spl([(540, 606), (592, 604), (598, 650), (548, 656)], 6), np.array([8, 8, 14.]), np.array([100, 100, 130.]), radio=10, outline=4, seed=152)


# ---- manos (formas propias, simplificadas)
def mano(L, c, ang, esc, tipo, fase=0.0):
    """Mano pintada. c: muneca, ang: direccion de los dedos (rad, 0 = derecha, pi/2 = abajo)."""
    ca, sa = math.cos(ang), math.sin(ang)
    R = lambda x, y: (c[0] + (x * ca - y * sa) * esc, c[1] + (x * sa + y * ca) * esc)
    pal_ = [R(0, 0), R(70, 0)]
    shapes = []
    pasto = PIEL_D, PIEL_L
    # manguito de la camisa en la muneca
    L.pegar(cap(R(-24, 0), R(2, 0), 34 * esc, 32 * esc), CAMISA_D, CAMISA_L, radio=14 * esc, outline=int(5), seed=160)
    palma = [elip(R(46, 0), 46 * esc, 38 * esc, ang)]
    deds = []
    if tipo == "indice":                                   # puno con el indice extendido
        palma = [elip(R(40, 4), 40 * esc, 37 * esc, ang)]
        deds.append(cap(R(60, -10), R(150 + 6 * math.sin(fase * 2 * math.pi), -12), 14 * esc, 10 * esc))     # indice
        for k, (y, l) in enumerate(((2, 66), (18, 62), (32, 54))):
            deds.append(cap(R(48, y), R(l + 24, y + 6), 13 * esc, 12 * esc))
        deds.append(cap(R(30, -28), R(62, -42), 13 * esc, 11 * esc))                                        # pulgar
    elif tipo == "pinza":                                  # pinza: indice y pulgar sostienen el monoculo
        palma = [elip(R(40, 0), 36 * esc, 36 * esc, ang)]
        deds.append(cap(R(60, -14), R(106, -22), 14 * esc, 11 * esc))
        deds.append(cap(R(60, 12), R(104, 20), 14 * esc, 11 * esc))
        for y in (26, 38, 50):
            deds.append(cap(R(40, y), R(70, y + 8), 11 * esc, 10 * esc))
    elif tipo == "lapiz":                                  # puno sosteniendo el lapiz
        palma = [elip(R(40, 0), 40 * esc, 38 * esc, ang)]
        for y in (-18, -2, 14, 30):
            deds.append(cap(R(54, y), R(84, y + 3), 13 * esc, 12 * esc))
        deds.append(cap(R(28, -34), R(78, -26), 14 * esc, 12 * esc))
    elif tipo == "sostiene":                               # mano que sostiene la libreta por abajo (pulgar arriba)
        palma = [elip(R(40, 0), 44 * esc, 36 * esc, ang)]
        for y in (-14, 2, 18, 34):
            deds.append(cap(R(60, y), R(100, y + 4), 13 * esc, 12 * esc))
        deds.append(cap(R(30, -34), R(86, -48), 15 * esc, 12 * esc))
    elif tipo == "solapa":                                 # mano metida en la solapa
        palma = [elip(R(40, 0), 42 * esc, 36 * esc, ang)]
        for y in (-18, -2, 14):
            deds.append(cap(R(58, y), R(98, y + 2), 13 * esc, 11 * esc))
        deds.append(cap(R(26, 26), R(66, 36), 14 * esc, 11 * esc))
    else:                                                  # reposo
        palma = [elip(R(40, 0), 40 * esc, 36 * esc, ang)]
        for y in (-18, -2, 14, 30):
            deds.append(cap(R(60, y), R(94, y + 10), 12 * esc, 11 * esc))
        deds.append(cap(R(30, -30), R(70, -26), 13 * esc, 11 * esc))
    m = L.pegar(palma + deds, PIEL_D * 0.95, PIEL_L * 1.0, radio=24 * esc, outline=6, seed=170, kluz=0.9)
    # dobleces de los nudillos
    if m is not None:
        for d_ in deds[:4]:
            pass
        L.sobre(m, bez(R(46, -24), R(56, 0), R(48, 24), 8), PIEL_D * 0.55, 0.55, w=3)
        L.sobre(m, [R(10, 20), R(60, 40), R(60, 50), R(10, 40)], PIEL_D * 0.5, 0.25, blur=6)
    return m


def manga(L, pts, w0, w1, seed=200):
    shp = [tubo(pts, w0, w1, 9), elip(pts[0], w0 * 0.5, w0 * 0.5)]
    m = L.pegar(shp, ABRIGO_D * 0.85, ABRIGO_L * 0.9, radio=min(w0, w1) * 0.5, outline=7, seed=seed, kluz=1.1)
    # arrugas del codo
    if m is not None:
        c = spl(pts, 8, closed=False)
        k = len(c) // 2
        for j in (-2, 0, 2):
            p = c[k + j]
            L.sobre(m, np.array([p + [-w0 * 0.3, -6], p + [w0 * 0.3, 6]]), np.array([6, 6, 12.]), 0.35, w=4)
        L.sobre(m, c + [-w0 * 0.22, -w0 * 0.1], np.array([170, 170, 205.]), 0.28, w=6, blur=0)
    return m


def libreta_pintada(L, c, ang, esc, fase, escribir):
    """Libreta de tapa de cuero con borde de hojas, en perspectiva simple; se ve su cubierta (el la mira de frente)."""
    ca, sa = math.cos(ang), math.sin(ang)
    R = lambda x, y: (c[0] + (x * ca - y * sa) * esc, c[1] + (x * sa + y * ca) * esc)
    pts = [R(-120, -86), R(120, -92), R(130, 88), R(-110, 94)]
    # pagina asomando
    L.pegar([R(-112, -100), R(112, -106), R(122, 70), R(-102, 78)], PAPEL_D, PAPEL_L, radio=18, outline=4, seed=210)
    m = L.pegar(spl(pts, 4), CUERO_D, CUERO_L, radio=40 * esc, outline=7, seed=211, kluz=1.0)
    L.sobre(m, [R(-120, -86), R(-96, -86), R(-86, 94), R(-110, 94)], np.array([30, 16, 10.]), 0.55)
    L.sobre(m, [R(-104, -70), R(104, -76), R(112, 74), R(-96, 80)], CUERO_L * 1.2, 0.0)
    L.sobre(m, bez(R(-70, -70), R(0, -78), R(110, -70), 10), np.array([220, 180, 120.]), 0.35, w=3)
    L.sobre(m, bez(R(-70, 70), R(0, 84), R(110, 76), 10), np.array([220, 180, 120.]), 0.35, w=3)
    L.sobre(m, [R(40, -30), R(100, -34), R(100, 30), R(40, 34)], np.array([232, 214, 160.]), 0.9)
    L.sobre(m, bez(R(48, -10), R(70, -18), R(94, -10), 8), np.array([60, 36, 24.]), 0.8, w=3)
    L.sobre(m, bez(R(48, 10), R(70, 2), R(94, 10), 8), np.array([60, 36, 24.]), 0.8, w=3)
    L.sobre(m, elip(R(-30, -36), 80 * esc, 22 * esc, ang), np.array([255, 220, 160.]), 0.20, blur=14)
    return m


def lapiz(L, a, b, w=11):
    L.trazo(np.array([a, b]), w + 6, OUTC, 1.0)
    L.trazo(np.array([a, b]), w, np.array([226, 176, 52.]), 1.0)
    d = (np.array(b) - np.array(a)); d = d / (np.linalg.norm(d) + 1e-6)
    L.trazo(np.array([np.array(a) + d * 6 + [-2, -3], np.array(b) - d * 10 + [-2, -3]]), 3, np.array([255, 238, 150.]), 0.8)
    pt = np.array(b)
    tip = pt + d * 30
    L.pegar([pt + [-d[1] * 7, d[0] * 7], tip, pt + [d[1] * 7, -d[0] * 7]], np.array([180, 130, 90.]), np.array([240, 214, 170.]), radio=5, outline=3, seed=230)
    L.pegar([tip - d * 8 + [-d[1] * 3, d[0] * 3], tip + d * 6, tip - d * 8 + [d[1] * 3, -d[0] * 3]], np.array([20, 20, 24.]), np.array([60, 60, 70.]), radio=3, outline=2, seed=231)
    return tip


def brazos(L, gesto, fase, vista):
    """Brazos y manos segun el gesto. Devuelve funcion opcional para dibujar algo tras la cabeza."""
    ph = 2 * math.pi * fase
    post = None
    if gesto == "reposo":
        manga(L, [(262, 676), (222, 800), (238, 960), (262, 1060)], 118, 98, seed=201)
        mano(L, (264, 1066), math.pi / 2 + 0.2, 0.9, "reposo")
        manga(L, [(818, 680), (858, 800), (840, 950), (790, 1040)], 112, 94, seed=202)
        mano(L, (786, 1048), math.pi / 2 - 0.4, 0.88, "solapa" if False else "reposo")
    elif gesto == "dedo":
        # brazo lejano levantado, indice hacia arriba (con vaiven); el cercano en la solapa
        manga(L, [(262, 676), (222, 800), (300, 900), (450, 840)], 118, 98, seed=203)
        mano(L, (456, 838), -0.35, 0.82, "solapa")
        sw = math.sin(ph) * 0.10
        manga(L, [(818, 680), (910, 770), (944, 650), (900, 540 + 10 * math.sin(ph))], 112, 90, seed=204)
        mano(L, (900, 542 + 10 * math.sin(ph)), -math.pi / 2 - 0.55 + sw, 1.0, "indice", fase)
    elif gesto == "monoculo":
        manga(L, [(818, 680), (858, 800), (840, 950), (790, 1040)], 112, 94, seed=205)
        mano(L, (786, 1048), math.pi / 2 - 0.4, 0.88, "reposo")
        manga(L, [(262, 676), (186, 640), (190, 480), (276, 400)], 118, 96, seed=206)

        def post(Lh):
            d = 3 * math.sin(ph)
            mano(Lh, (292, 388 + d), -0.45, 0.92, "pinza")
        return post
    elif gesto == "anotando":
        # libreta sostenida con el brazo cercano; el lejano escribe
        manga(L, [(262, 676), (218, 800), (262, 930), (400, 960)], 118, 98, seed=207)
        libreta_pintada(L, (440, 830), -0.12, 1.12, fase, True)
        mano(L, (330, 990), -0.2, 0.88, "sostiene")
        wx = 5 * math.sin(ph * 3.0)
        wy = 3 * math.sin(ph * 6.0 + 0.5)
        manga(L, [(818, 680), (870, 820), (840, 930), (700, 880)], 112, 94, seed=208)
        mano(L, (680 + wx, 868 + wy), math.pi + 0.55, 0.86, "lapiz")
        lapiz(L, (676 + wx, 870 + wy), (610 + wx, 906 + wy))
    return post


# ------------------------------------------------------------------------------------------------ API
def _grade(rgb, a, pal):
    luz = np.array(pal["luz"], np.float32)
    som = np.array(pal["sombra"], np.float32)
    gn = luz / max(luz.max(), 1)
    lum = rgb.mean(-1, keepdims=True) / 255.0
    rgb = rgb * (0.80 + 0.20 * gn) + som * 0.16 * (1 - lum) ** 2 + luz * 0.05 * lum ** 2
    return np.clip(rgb, 0, 255)


def _rim(rgb, a, pal, lado=1):
    luz = np.array(pal["luz"], np.float32)
    k = 9
    sh = np.roll(a, -lado * k, axis=1)
    rim = np.clip(a - sh, 0, 1)
    rim = cv2.GaussianBlur(rim, (0, 0), 2.2) * a
    return rgb * (1 - rim[..., None] * 0.55) + luz * rim[..., None] * 0.55


def _parse_pose(pose):
    p = (pose or "busto").split("_")
    vista = p[0] if p[0] in ("busto", "cuerpo") else "busto"
    gesto = p[1] if len(p) > 1 else "reposo"
    return vista, gesto


def owen(expresion="neutral", pose="busto", fase=0.0, pal="ambar", h_px=700, habla=0.0):
    pal = obtener(pal)
    vista, gesto = _parse_pose(pose)
    if expresion not in EXPR:
        raise ValueError(f"expresion {expresion!r}: usar {NOMBRES}")
    if gesto == "anotando" and expresion == "neutral":
        expresion = "anotando"
    ex = EXPR[expresion]
    fase = fase % 1.0
    ph = 2 * math.pi * fase
    out = Cv(CW, CH)
    # sombra de contacto (cuerpo entero)
    if vista == "cuerpo":
        out.trazo_elipse((580, 1540), 360, 30, (14, 8, 20), 0.5, blur=18)
    base = cuerpo(vista)
    resp = 4 * math.sin(ph)                                                # respiracion
    out.sobre_cv(base, 0, 0)
    # (el torso respira: pequeño desplazamiento de la cabeza)
    L2 = Cv(CW, CH)
    post = brazos(L2, gesto, fase, vista)
    out.sobre_cv(L2)
    # cabeza con inclinacion / asentimiento
    cab = cabeza(expresion, fase, habla)
    if not (gesto == "monoculo"):
        monoculo(cab)
    else:
        monoculo(cab, dy=-6 - 3 * math.sin(ph), dx=-3)
    tilt, nod, turn = ex["cab"]
    tilt = tilt + 1.3 * math.sin(ph + 0.8)
    M = cv2.getRotationMatrix2D((560, 540), -tilt, 1.10)
    M[0, 2] += turn * 0.4 - 220 + 220
    M[1, 2] += nod * 0.5 + resp + 22
    # warp del Cv de la cabeza (origen 220,0) a coordenadas de lienzo
    T = np.array([[1, 0, cab.ox], [0, 1, cab.oy], [0, 0, 1]], np.float64)
    Mf = np.vstack([M, [0, 0, 1]]) @ np.linalg.inv(T)
    Mf = (np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], np.float64) @ Mf)
    # queremos: p_canvas' = M(p_canvas); p_canvas = p_local + origin -> p_local -> M·(T·p_local)
    Mfull = (np.vstack([M, [0, 0, 1]]) @ T)[:2]
    img4 = np.dstack([cab.c * cab.a[..., None], cab.a])
    wp = cv2.warpAffine(img4, Mfull, (CW, CH), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    a = wp[..., 3:4]
    out.c = out.c * (1 - a) + wp[..., :3]
    out.a = np.maximum(out.a, a[..., 0])
    cuello_alto(out)
    if post:
        post(out)
    # recorte
    if vista == "busto":
        y0, y1, x0, x1 = 10, 1030, 90, 1010
    else:
        y0, y1, x0, x1 = 10, 1566, 60, 1040
    rgb = out.c[y0:y1, x0:x1]
    al = np.clip(out.a[y0:y1, x0:x1], 0, 1)
    rgb = _grade(rgb, al, pal)
    rgb = _rim(rgb, al, pal)
    # contorno de la paleta en el borde exterior
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    sc = h_px / rgb.shape[0]
    nw = max(2, int(round(rgb.shape[1] * sc)))
    pm = np.dstack([rgb * al[..., None], al])
    pm = cv2.resize(pm, (nw, int(h_px)), interpolation=cv2.INTER_AREA if sc < 1 else cv2.INTER_LINEAR)
    aa = pm[..., 3:4]
    col = pm[..., :3] / np.maximum(aa, 1e-3)
    res = np.dstack([np.clip(col, 0, 255), np.clip(aa[..., 0], 0, 1) * 255]).astype(np.uint8)
    return Image.fromarray(res, "RGBA")


def ciclo_anotando(n=48, pal="ambar", h_px=600, pose="busto"):
    """Loop de n cuadros (perfecto: fase 0..1) de Owen escribiendo en su libreta, mirando a la pagina y levantando la vista."""
    vista, _ = _parse_pose(pose)
    return [owen("anotando", f"{vista}_anotando", i / n, pal, h_px) for i in range(n)]


def libreta(h_px=300, fase=0.0, pal="ambar", abierta=True, texto=None):
    """Sprite de la libreta (abierta, con renglones y texto manuscrito) y un lapiz que se mueve con `fase`."""
    pal = obtener(pal)
    Wc, Hc = 900, 640
    L = Cv(Wc, Hc)
    if abierta:
        # tapas
        L.pegar(spl([(30, 70), (450, 52), (870, 70), (880, 580), (450, 600), (20, 580)], 5), CUERO_D, CUERO_L, radio=30, outline=8, seed=300)
        for sgn, x0, x1 in ((0, 56, 440), (1, 460, 846)):
            pts = [(x0, 96), (x1, 90 if sgn else 88), (x1, 560 if sgn else 566), (x0, 566 if not sgn else 560)]
            if sgn == 0:
                pts = [(56, 90), (440, 100), (440, 566), (56, 556)]
            else:
                pts = [(460, 100), (846, 90), (846, 556), (460, 566)]
            m = L.pegar(spl(pts, 4), PAPEL_D, PAPEL_L, radio=60, outline=4, seed=301 + sgn, kluz=0.4)
            for y in range(140, 540, 36):
                L.sobre(m, np.array([(x0 + 24, y), (x1 - 20, y + (4 if sgn else -4))]), np.array([120, 150, 190.]), 0.35, w=2)
            L.sobre(m, [(x0 + 70, 96), (x0 + 74, 96), (x0 + 74, 566), (x0 + 70, 566)], np.array([200, 80, 80.]), 0.4)
        L.sobre(L.ref([(430, 90), (470, 90), (470, 570), (430, 570)]),
                [(430, 90), (470, 90), (470, 570), (430, 570)], np.array([60, 36, 24.]), 0.55, blur=12)
        im = Image.fromarray(np.clip(L.c, 0, 255).astype(np.uint8))
        al = (np.clip(L.a, 0, 1) * 255).astype(np.uint8)
        rgba = Image.merge("RGBA", (*im.split(), Image.fromarray(al)))
        if texto:
            d = ImageDraw.Draw(rgba)
            f = ImageFont.truetype(str(FUENTE), 44)
            for i, ln in enumerate(texto if isinstance(texto, (list, tuple)) else [texto]):
                d.text((150, 126 + 36 * i), ln, font=f, fill=(40, 40, 70, 255))
        px, py = 560 + 90 * math.sin(2 * math.pi * fase * 2), 460 + 12 * math.sin(2 * math.pi * fase * 6)
        L2 = Cv(Wc, Hc)
        lapiz(L2, (px + 120, py - 90), (px, py), 14)
        im2 = Image.fromarray(np.clip(L2.c, 0, 255).astype(np.uint8))
        al2 = (np.clip(L2.a, 0, 1) * 255).astype(np.uint8)
        lap = Image.merge("RGBA", (*im2.split(), Image.fromarray(al2)))
        rgba = Image.alpha_composite(rgba, lap)
    else:
        m = L.pegar(spl([(200, 80), (700, 70), (720, 560), (190, 570)], 5), CUERO_D, CUERO_L, radio=50, outline=8, seed=310)
        L.sobre(m, [(200, 80), (250, 78), (240, 570), (190, 570)], np.array([30, 16, 10.]), 0.5)
        L.sobre(m, [(330, 160), (640, 150), (640, 260), (330, 270)], np.array([220, 190, 130.]), 0.55)
        im = Image.fromarray(np.clip(L.c, 0, 255).astype(np.uint8))
        al = (np.clip(L.a, 0, 1) * 255).astype(np.uint8)
        rgba = Image.merge("RGBA", (*im.split(), Image.fromarray(al)))
        d = ImageDraw.Draw(rgba)
        d.text((485, 205), "Notas", font=ImageFont.truetype(str(FUENTE), 62), fill=(60, 30, 20, 255), anchor="mm")
    bb = rgba.getbbox()
    rgba = rgba.crop(bb)
    w = int(rgba.width * h_px / rgba.height)
    return rgba.resize((w, int(h_px)), Image.LANCZOS)


def hoja_expresiones(path, pose="busto", h_px=520, pal="ambar"):
    cols = 4
    rows = (len(NOMBRES) + cols - 1) // cols
    pw = int(h_px * 0.95)
    S = Image.new("RGB", (cols * pw, rows * (h_px + 40)), (70, 94, 78))
    d = ImageDraw.Draw(S)
    f = ImageFont.truetype(str(FUENTE), 36)
    for i, n in enumerate(NOMBRES):
        im = owen(n, pose if n != "anotando" else pose + "_anotando", 0.3, pal, h_px)
        x, y = (i % cols) * pw, (i // cols) * (h_px + 40)
        S.paste(im, (x + (pw - im.width) // 2, y + 40), im)
        d.text((x + 14, y + 4), n, font=f, fill=(250, 244, 230))
    S.save(path)


if __name__ == "__main__":
    hoja_expresiones(sys.argv[1] if len(sys.argv) > 1 else "hoja_owen.png")
