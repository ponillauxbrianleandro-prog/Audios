#!/usr/bin/env python3
"""Mascota del canal Río Puratense (v3): libro viviente gordísimo, acostado, con 4 patas. ILUSTRACIÓN 2D PINTADA (sin 3D).

Orientación: acostado sobre la tapa inferior (= panza). Lomo a la IZQUIERDA (una tira oscura asoma), el canto INFERIOR de las
hojas mira al frente y lleva los 2 ojos canica; el canto derecho (hojas) se ve entero; la tapa superior (= dorso) se ve entera,
abovedada, con una pata peluda dorada en lugar de la mano del diario. 4 patas negras tipo stickman, gorditas, en las 4 esquinas
de la tapa inferior. Sin cola. El lado de atrás no se ve.
Todo se pinta por capas con curvas: degradado de luz, oclusión en los bordes (efecto «inflado»), grano, rayones, manchas, contorno
marrón. La profundidad sale del dibujo (perspectiva dibujada), no de un modelo 3D.

  python3 mascota.py HOJA.png     hoja de poses
  Mascota().frame(pose) -> PIL RGBA (lienzo 1500x1150, pensado para escalar)
"""
import math
import sys
import numpy as np
import cv2
from PIL import Image

W, H = 1500, 1150
OUT = np.array([34, 20, 16], np.float32)                       # contorno marrón cálido
V_LIT, V_MID, V_DRK = np.array([150, 58, 80.]), np.array([112, 46, 68.]), np.array([62, 30, 40.])   # vino (de las fotos, algo levantado)
ROJO_DESG = np.array([170, 52, 44.])
GRIS_VERDE, GRIS_OSC = np.array([128, 134, 108.]), np.array([84, 88, 70.])
ORO_L, ORO_M, ORO_D = np.array([214, 206, 120.]), np.array([167, 162, 100.]), np.array([108, 100, 58.])
LATON_L, LATON_D = np.array([196, 168, 96.]), np.array([96, 76, 42.])
LOMO_C, LOMO_L = np.array([44, 45, 62.]), np.array([86, 86, 108.])
PAP_L, PAP_M, PAP_D = np.array([246, 234, 200.]), np.array([228, 210, 168.]), np.array([176, 154, 112.])
LINEA_PAG = np.array([150, 124, 86.])

# ---- geometría de la tapa superior (dorso) en pantalla: FL,FR delante; BL,BR atrás (el eje «v» se aleja y sube a la derecha)
FL, FR = np.array([330., 560.]), np.array([930., 604.])
BACK = np.array([200., -272.])
BL, BR = FL + BACK, FR + BACK
T_COVER, T_PAGES, T_BELLY = 34., 250., 38.
LARGO_CM, ANCHO_CM = 23., 15.


def uv(x_cm, y_cm, dy=0.0):
    """Coordenadas de la tapa en cm (x a lo ancho 0..15, y a lo largo 0..23, hacia atrás) -> píxeles."""
    p = FL + (x_cm / ANCHO_CM) * (FR - FL) + (y_cm / LARGO_CM) * BACK
    return p + np.array([0, dy])


def spline(pts, n=14, closed=True):
    P = [np.array(p, float) for p in pts]
    m = len(P)
    out = []
    rng = range(m) if closed else range(m - 1)
    for i in rng:
        p0, p1, p2, p3 = P[(i - 1) % m], P[i], P[(i + 1) % m], P[(i + 2) % m]
        if not closed:
            p0 = P[max(i - 1, 0)]; p3 = P[min(i + 2, m - 1)]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    return np.array(out)


def mask_of(poly):
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [np.round(np.array(poly) * 16).astype(np.int32)], 255, cv2.LINE_AA, shift=4)
    return m


def noise(scale, seed):
    r = np.random.RandomState(seed)
    g = r.rand(max(2, H // scale), max(2, W // scale)).astype(np.float32)
    return cv2.resize(g, (W, H), interpolation=cv2.INTER_CUBIC)


class Lienzo:
    def __init__(self):
        self.c = np.zeros((H, W, 3), np.float32)
        self.a = np.zeros((H, W), np.float32)

    def pegar(self, mask, color, outline=5):
        m = mask.astype(np.float32) / 255
        if outline:
            o = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (outline * 2 + 1, outline * 2 + 1))).astype(np.float32) / 255
            self.c = self.c * (1 - o[..., None]) + OUT * o[..., None]
            self.a = np.maximum(self.a, o)
        self.c = self.c * (1 - m[..., None]) + color * m[..., None]
        self.a = np.maximum(self.a, m)

    def sobre(self, mask, color, alpha=1.0):
        m = (mask.astype(np.float32) / 255 * alpha)[..., None]
        self.c = self.c * (1 - m) + color * m
        self.a = np.maximum(self.a, m[..., 0])

    def imagen(self):
        rgba = np.dstack([np.clip(self.c, 0, 255), np.clip(self.a, 0, 1) * 255]).astype(np.uint8)
        return Image.fromarray(rgba, "RGBA")


def degradado(mask, c0, c1, p0, p1):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.array(p1, np.float32) - np.array(p0, np.float32)
    t = np.clip(((xx - p0[0]) * d[0] + (yy - p0[1]) * d[1]) / (d @ d), 0, 1)[..., None]
    return c0 * (1 - t) + c1 * t


def inflado(mask, base_dark, base_lit, radio=46, grano=10, seed=1, extra_luz=None):
    """Color con efecto «inflado»: más claro lejos de los bordes (volumen), con grano."""
    dist = cv2.distanceTransform((mask > 127).astype(np.uint8), cv2.DIST_L2, 5)
    t = np.clip(dist / radio, 0, 1)[..., None]
    t = t * t * (3 - 2 * t)
    col = base_dark * (1 - t) + base_lit * t
    if extra_luz is not None:
        col = col * extra_luz[..., None]
    g = (noise(3, seed) - 0.5) * grano + (noise(18, seed + 7) - 0.5) * grano * 1.4
    return col + g[..., None]


# -------------------------------------------------------------------------------------------- cuerpo
def cuerpo(flip=False):
    L = Lienzo()
    F = (lambda p: np.array([1500 - p[0], p[1]])) if flip else (lambda p: np.array(p, float))
    # --- sombra de contacto
    # (se dibuja aparte en frame())
    # --- tapa inferior (panza): costado frontal + derecho, abultada hacia abajo
    def panza_poly():
        a = FL + np.array([-14, T_COVER + T_PAGES - 4]); b = FR + np.array([14, T_COVER + T_PAGES - 4])
        c = BR + np.array([14, T_COVER + T_PAGES - 4]);
        pts = [a, (a + b) / 2 + [0, 0], b, c,
               c + [12, 12], b + [18, T_BELLY + 6], (a + b) / 2 + [10, T_BELLY + 44], a + [-4, T_BELLY + 12]]
        return [F(p) for p in spline(pts, 10)]
    pan = mask_of(panza_poly())
    col = inflado(pan, GRIS_OSC * 0.8, GRIS_VERDE, radio=30, seed=3) if not flip else inflado(pan, V_DRK, V_MID, radio=30, seed=3)
    L.pegar(pan, col, 6)

    # --- lomo (tira oscura que asoma a la izquierda), convexo, con nervaduras
    lomo_pts = [FL + [4, T_COVER - 8], FL + [-40, T_COVER + 14], FL + [-48, T_COVER + 120], FL + [-44, T_COVER + T_PAGES - 20],
                FL + [-14, T_COVER + T_PAGES + 6], FL + [4, T_COVER + T_PAGES]]
    lm = mask_of([F(p) for p in spline(lomo_pts, 8)])
    colm = inflado(lm, LOMO_C * 0.7, LOMO_L, radio=22, seed=5)
    for yb in (0.18, 0.42, 0.66, 0.86):                                       # nervaduras
        y = FL[1] + T_COVER + yb * T_PAGES
        cv2.line(lm := lm, (0, 0), (0, 0), 0)
    L.pegar(lm, colm, 5)
    for yb in (0.2, 0.45, 0.7, 0.9):
        y = FL[1] + T_COVER + yb * T_PAGES
        p0, p1 = F([FL[0] - 46, y]), F([FL[0] + 2, y + 6])
        L.sobre(mask_line(p0, p1, 5), LOMO_L * 1.15, 0.8)

    # --- hojas: cara frontal (canto inferior del libro) abultada como barril
    def parche(A, B, C, D, bx, by, fn):
        def P(u, v):
            base = (1 - v) * ((1 - u) * A + u * B) + v * ((1 - u) * D + u * C)
            return base + np.array([bx * (u - .5) * 2 * math.sin(math.pi * v) ** .8, by * math.sin(math.pi * u) ** .6 * v ** 1.3])
        return P
    A = FL + [0, T_COVER]; B = FR + [0, T_COVER]; C = FR + [0, T_COVER + T_PAGES]; D = FL + [0, T_COVER + T_PAGES]
    Pf = parche(A, B, C, D, 30, 26, None)
    contorno = [Pf(u, 0) for u in np.linspace(0, 1, 18)] + [Pf(1, v) for v in np.linspace(0, 1, 18)] + [Pf(u, 1) for u in np.linspace(1, 0, 18)] + [Pf(0, v) for v in np.linspace(1, 0, 18)]
    fm = mask_of([F(p) for p in contorno])
    luz = 0.84 + 0.2 * np.clip((degradado(fm, np.array([0.]), np.array([1.]), (FL[0], FL[1] + 380), (FL[0] + 150, FL[1] + 60)))[..., 0], 0, 1)
    colf = inflado(fm, PAP_D, PAP_L, radio=70, seed=9, extra_luz=luz)
    L.pegar(fm, colf, 5)
    # líneas de hojas siguiendo el abultado
    n = 30
    for k in range(1, n):
        v = k / n
        pts = np.array([F(Pf(u, v)) for u in np.linspace(0, 1, 30)])
        tono = LINEA_PAG * (0.9 + 0.2 * ((k * 37) % 5) / 5)
        L.sobre(mask_poly_line(pts, 2 if k % 3 else 3), tono, 0.45 if k % 3 else 0.6)
    # sombra bajo la tapa superior sobre las hojas (oclusión)
    ocl = np.zeros((H, W), np.uint8)
    pts = np.array([F(Pf(u, 0.0)) for u in np.linspace(0, 1, 30)] + [F(Pf(u, 0.16)) for u in np.linspace(1, 0, 30)])
    cv2.fillPoly(ocl, [np.round(pts).astype(np.int32)], 255, cv2.LINE_AA)
    ocl = cv2.GaussianBlur(ocl, (0, 0), 9) * (fm > 127)
    L.sobre(ocl, np.array([60, 36, 44.]), 0.55)

    # --- hojas: cara derecha (canto de las hojas del frente de la tapa)
    A2, B2 = FR + [0, T_COVER], BR + [0, T_COVER]
    C2, D2 = BR + [0, T_COVER + T_PAGES], FR + [0, T_COVER + T_PAGES]
    def Pr(u, v):
        base = (1 - v) * ((1 - u) * A2 + u * B2) + v * ((1 - u) * D2 + u * C2)
        return base + np.array([26 * math.sin(math.pi * u) ** .6 * math.sin(math.pi * v) ** .6, 22 * math.sin(math.pi * u) ** .6 * v ** 1.3])
    cont = [Pr(u, 0) for u in np.linspace(0, 1, 18)] + [Pr(1, v) for v in np.linspace(0, 1, 18)] + [Pr(u, 1) for u in np.linspace(1, 0, 18)] + [Pr(0, v) for v in np.linspace(1, 0, 18)]
    rm = mask_of([F(p) for p in cont])
    colr = inflado(rm, PAP_D * 0.78, PAP_M * 0.96, radio=60, seed=11)
    L.pegar(rm, colr, 5)
    for k in range(1, n):
        v = k / n
        pts = np.array([F(Pr(u, v)) for u in np.linspace(0, 1, 30)])
        L.sobre(mask_poly_line(pts, 2), LINEA_PAG * 0.85, 0.45)
    ocl = np.zeros((H, W), np.uint8)
    pts = np.array([F(Pr(u, 0.0)) for u in np.linspace(0, 1, 30)] + [F(Pr(u, 0.15)) for u in np.linspace(1, 0, 30)])
    cv2.fillPoly(ocl, [np.round(pts).astype(np.int32)], 255, cv2.LINE_AA)
    L.sobre(cv2.GaussianBlur(ocl, (0, 0), 9) * (rm > 127), np.array([60, 36, 44.]), 0.5)

    # --- canto de la tapa superior (grosor) frontal y derecho
    rim_f = [FL, FR, FR + [0, T_COVER], FL + [0, T_COVER]]
    rim_r = [FR, BR, BR + [0, T_COVER], FR + [0, T_COVER]]
    for poly, seed in ((rim_f, 13), (rim_r, 14)):
        mm = mask_of([F(p) for p in poly])
        L.pegar(mm, inflado(mm, V_DRK * 0.8, V_MID * 0.95, radio=10, seed=seed), 4)

    # --- tapa superior (dorso abovedado)
    esq = [FL, FR, BR, BL]
    mid = lambda a, b, o: (a + b) / 2 + np.array(o)
    cover_pts = [FL + [-4, 2], mid(FL, FR, [0, 10]), FR + [4, 4], mid(FR, BR, [10, 0]), BR + [4, -3], mid(BR, BL, [0, -10]), BL + [-4, -3], mid(BL, FL, [-10, 0])]
    cm = mask_of([F(p) for p in spline(cover_pts, 10)])
    luz = 0.86 + 0.22 * np.clip(degradado(cm, np.array([0.]), np.array([1.]), (BL[0] + 600, BL[1] + 500), (BL[0] - 40, BL[1] - 20))[..., 0], 0, 1)
    base_d, base_l = (V_DRK, V_LIT) if not flip else (GRIS_OSC * 0.85, GRIS_VERDE * 1.05)
    colc = inflado(cm, base_d, base_l, radio=120, seed=17, grano=12, extra_luz=luz)
    # desgaste rojo en esquinas delanteras + rayones
    n1 = noise(40, 21); n2 = noise(10, 22)
    desg = np.clip((n1 - 0.55) * 4, 0, 1) * np.clip((n2 - 0.35) * 2.2, 0, 1)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cerca = np.exp(-(((xx - FL[0]) ** 2 + (yy - FL[1]) ** 2) / (2 * 190 ** 2))) + np.exp(-(((xx - FR[0]) ** 2 + (yy - FR[1]) ** 2) / (2 * 220 ** 2)))
    if not flip:
        colc = colc * (1 - (desg * cerca)[..., None] * 0.7) + ROJO_DESG * (desg * cerca)[..., None] * 0.7
    L.pegar(cm, colc, 6)
    rs = np.random.RandomState(4)
    scr = np.zeros((H, W), np.uint8)
    for _ in range(46):
        x0, y0 = rs.uniform(FL[0], FR[0] + 200), rs.uniform(BL[1], FL[1])
        a = rs.uniform(-0.6, 0.6); ln = rs.uniform(20, 90)
        cv2.line(scr, (int(x0), int(y0)), (int(x0 + math.cos(a) * ln), int(y0 + math.sin(a) * ln)), 255, 1, cv2.LINE_AA)
    L.sobre(scr * (cm > 127), np.array([220, 150, 150.]) if not flip else np.array([210, 215, 190.]), 0.16)
    # borde de luz (arriba/izquierda)
    edge = cv2.morphologyEx(cm, cv2.MORPH_GRADIENT, np.ones((5, 5), np.uint8))
    L.sobre(edge * (cm > 127), np.array([232, 140, 150.]), 0.28)

    # --- decoración de la tapa: pata peluda dorada + esquinas de latón (en el plano de la tapa) ---------------
    def pl(pts_cm):
        return [F(uv(x, y)) for x, y in pts_cm]
    def elipse(cx, cy, rx, ry, n=30, rot=0.0):
        t = np.linspace(0, 2 * math.pi, n, endpoint=False)
        px = rx * np.cos(t); py = ry * np.sin(t)
        c, s = math.cos(rot), math.sin(rot)
        return [(cx + px[i] * c - py[i] * s, cy + px[i] * s + py[i] * c) for i in range(n)]
    def pelos(pts, k=2.2, seed=0):
        r = np.random.RandomState(seed)
        out = []
        c = np.mean(pts, 0)
        for i, p in enumerate(pts):
            d = (np.array(p) - c); d = d / (np.linalg.norm(d) + 1e-6)
            if i % 3 == 0:
                out.append(np.array(p) + d * k * r.uniform(0.8, 1.6))
            else:
                out.append(np.array(p))
        return out
    if not flip:
        partes = [(elipse(7.5, 8.4, 3.6, 3.0), 31)]                                    # almohadilla
        for (tx, ty, r_) in ((3.2, 12.4, 1.5), (5.6, 14.6, 1.7), (9.4, 14.6, 1.7), (11.8, 12.4, 1.5)):   # 4 deditos
            partes.append((elipse(tx + (0 if True else 0), ty, r_, r_ * 1.15), 32))
        for pts, sd in partes:
            pp = pl(pts)
            sp = spline(pp, 3) if False else np.array(pp)
            mk = mask_of(sp)
            L.pegar(mk, inflado(mk, ORO_D, ORO_L, radio=24, seed=sd, grano=14), 3)
        # rayones del metal
        scr2 = np.zeros((H, W), np.uint8)
        rr = np.random.RandomState(8)
        for _ in range(60):
            x0, y0 = rr.uniform(2, 13), rr.uniform(5, 16)
            a = rr.uniform(0.3, 1.1); ln = rr.uniform(0.5, 2.2)
            p0, p1 = F(uv(x0, y0)), F(uv(x0 + math.cos(a) * ln, y0 + math.sin(a) * ln))
            cv2.line(scr2, (int(p0[0]), int(p0[1])), (int(p1[0]), int(p1[1])), 255, 1, cv2.LINE_AA)
        L.sobre(scr2 * (cm > 127), np.array([240, 235, 170.]), 0.35)
        # almohadilla interna (sombra)
        pm = mask_of(pl(elipse(7.5, 8.0, 1.9, 1.5)))
        L.sobre(pm, ORO_D * 0.8, 0.55)
    # esquinas de latón: triángulo con hipotenusa cóncava y remache
    def esquina(cx, cy, dx, dy, k=4.6):
        a, b = (cx + dx * k, cy), (cx, cy + dy * k)
        ctrl = (cx + dx * k * 0.52, cy + dy * k * 0.52)
        pts = [(cx, cy), a]
        for t in np.linspace(0, 1, 12):
            q = ((1 - t) ** 2 * np.array(a) + 2 * (1 - t) * t * np.array(ctrl) + t ** 2 * np.array(b))
            pts.append(tuple(q))
        pts.append(b)
        return pts, ctrl
    for (cx, cy, dx, dy) in ((0, 0, 1, 1), (15, 0, -1, 1), (0, 23, 1, -1), (15, 23, -1, -1)):
        pts, ctrl = esquina(cx, cy, dx, dy)
        mk = mask_of(pl(pts))
        L.pegar(mk, inflado(mk, LATON_D, LATON_L, radio=18, seed=cx + cy + 40, grano=16), 3)
        c = F(uv(cx + dx * 1.15, cy + dy * 1.15))
        rm_ = np.zeros((H, W), np.uint8)
        cv2.circle(rm_, (int(c[0]), int(c[1])), 9, 255, -1, cv2.LINE_AA)
        L.pegar(rm_, np.array([224, 200, 140.]), 2)
        hl = np.zeros((H, W), np.uint8); cv2.circle(hl, (int(c[0]) - 3, int(c[1]) - 3), 3, 255, -1, cv2.LINE_AA)
        L.sobre(hl, np.array([255, 250, 230.]), 0.9)
    return L


def mask_line(p0, p1, w):
    m = np.zeros((H, W), np.uint8)
    cv2.line(m, (int(p0[0]), int(p0[1])), (int(p1[0]), int(p1[1])), 255, w, cv2.LINE_AA)
    return m


def mask_poly_line(pts, w):
    m = np.zeros((H, W), np.uint8)
    cv2.polylines(m, [np.round(np.array(pts)).astype(np.int32)], False, 255, w, cv2.LINE_AA)
    return m


# -------------------------------------------------------------------------------------------- patas, ojos, cuadro
def pata(L, hip, knee, foot, w=40):
    for a, b in ((hip, knee), (knee, foot)):
        m = np.zeros((H, W), np.uint8)
        cv2.line(m, tuple(int(v) for v in a), tuple(int(v) for v in b), 255, int(w), cv2.LINE_AA)
        cv2.circle(m, tuple(int(v) for v in b), int(w / 2), 255, -1, cv2.LINE_AA)
        L.pegar(m, np.array([30, 26, 32.]), 0)
        hl = np.zeros((H, W), np.uint8)
        off = np.array([-w * 0.22, 0])
        cv2.line(hl, tuple(int(v) for v in (a + off)), tuple(int(v) for v in (b + off)), 255, max(2, int(w * 0.16)), cv2.LINE_AA)
        L.sobre(hl, np.array([96, 90, 110.]), 0.6)
    fm = np.zeros((H, W), np.uint8)
    cv2.ellipse(fm, (int(foot[0] + 8), int(foot[1] + 4)), (int(w * 0.95), int(w * 0.5)), 0, 0, 360, 255, -1, cv2.LINE_AA)
    L.pegar(fm, np.array([30, 26, 32.]), 0)


class Mascota:
    def __init__(self):
        self.cache = {}

    def _cuerpo(self, flip):
        if flip not in self.cache:
            self.cache[flip] = cuerpo(flip)
        return self.cache[flip]

    def frame(self, pose=None):
        p = dict(leg=None, bob=0, tilt=0, squash=1.0, blink=0, mad=0, look=(0, 0), flip=False, spread=0, lean=0)
        p.update(pose or {})
        flip = p["flip"]
        base = self._cuerpo(flip)
        out = Lienzo()
        # sombra de contacto
        sh = np.zeros((H, W), np.uint8)
        cv2.ellipse(sh, (760, 1000), (560, 78), 0, 0, 360, 255, -1, cv2.LINE_AA)
        sh = cv2.GaussianBlur(sh, (0, 0), 22)
        out.sobre(sh, np.array([16, 8, 28.]), 0.45)
        # patas
        def fase(i):
            return 0.0 if p["leg"] is None else math.sin((p["leg"] + (0.5 if i in (1, 2) else 0.0)) * 2 * math.pi)
        G = 1010
        hips = [FL + [90, T_COVER + T_PAGES + 40], FR + [-30, T_COVER + T_PAGES + 52], BR + [-20, T_COVER + T_PAGES + 30], FL + [200, T_COVER + T_PAGES - 80]]
        ground = [G, G + 12, 880, 830]
        order = (3, 2, 0, 1)
        dibujar_patas = lambda idx: [self._pata(out, i, hips[i], ground[i], fase(i), p, flip) for i in idx]
        if flip:
            dibujar_patas((3, 2))
        else:
            dibujar_patas((3, 2))
        # cuerpo (con transformación: rebote, inclinación, aplastado)
        img = np.dstack([base.c, base.a[..., None] * 255]).astype(np.float32)
        M = cv2.getRotationMatrix2D((760, 900), p["tilt"], 1.0)
        M[1, 2] += p["bob"] - (1 - p["squash"]) * 0
        sy = p["squash"]
        M = np.vstack([M, [0, 0, 1]]) @ np.array([[1, 0, 0], [0, sy, 900 * (1 - sy)], [0, 0, 1]])
        warped = cv2.warpAffine(img, M[:2], (W, H), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
        a = warped[..., 3:4] / 255
        out.c = out.c * (1 - a) + warped[..., :3] * a
        out.a = np.maximum(out.a, a[..., 0])
        if not flip:
            dibujar_patas((0, 1))
        else:
            dibujar_patas((3, 2, 0, 1))
        self._ojos(out, p, M, flip)
        return out.imagen()

    def _pata(self, L, i, hip, ground, ph, p, flip):
        sw = 34 * ph
        lift = 26 * max(0.0, math.cos(2 * math.pi * 0) * ph) if p["leg"] is not None else 0
        sp = p["spread"] * 50 * (1 if hip[0] > 700 else -1)
        if flip:
            cm = ((2.6, 3.0), (12.4, 3.0), (12.4, 20.0), (2.6, 20.0))[i]
            q = uv(*cm); hip = np.array([1500 - q[0], q[1]])
            side = 1 if hip[0] > 750 else -1
            foot = hip + np.array([side * 20 + sp * 0.8 + sw * 0.6, -200 - sw * 0.5])
            knee = hip + np.array([side * 30 + sp * 0.3, -105])
        else:
            foot = np.array([hip[0] + sw * 0.9 + sp, ground - max(0, ph) * 22 * (1 if p["leg"] is not None else 0) + p["bob"] * 0])
            knee = (hip + foot) / 2 + np.array([(16 if hip[0] > 700 else -16) + sp * 0.2, 6])
        pata(L, hip + [0, p["bob"]], knee + [0, p["bob"] * 0.6], foot, 58 if i < 2 else 48)

    def _ojos(self, L, p, M, flip):
        for ex, ey in ((470, 735), (760, 756)):
            if flip:
                ex = 1500 - ex
            pt = (M @ np.array([ex, ey, 1]))[:2]
            if flip:
                pt = np.array([pt[0], pt[1]])
            r = 33
            soc = np.zeros((H, W), np.uint8)
            cv2.ellipse(soc, (int(pt[0]), int(pt[1] + 4)), (int(r * 1.45), int(r * 1.3)), 0, 0, 360, 255, -1, cv2.LINE_AA)
            soc = cv2.GaussianBlur(soc, (0, 0), 7)
            L.sobre(soc, np.array([120, 84, 52.]), 0.5)
            ry = max(2, int(r * (1 - 0.92 * p["blink"])))
            ob = np.zeros((H, W), np.uint8)
            cv2.ellipse(ob, (int(pt[0]), int(pt[1])), (r, ry), 0, 0, 360, 255, -1, cv2.LINE_AA)
            L.pegar(ob, np.array([18, 14, 20.]), 2)
            if p["blink"] < 0.6:
                lx, ly = p["look"]
                hl = np.zeros((H, W), np.uint8)
                cv2.circle(hl, (int(pt[0] - 10 + lx * 6), int(pt[1] - 11 + ly * 5)), 9, 255, -1, cv2.LINE_AA)
                L.sobre(hl, np.array([255, 255, 255.]), 0.95)
                hl2 = np.zeros((H, W), np.uint8)
                cv2.circle(hl2, (int(pt[0] + 11), int(pt[1] + 11)), 5, 255, -1, cv2.LINE_AA)
                L.sobre(hl2, np.array([120, 116, 150.]), 0.6)
        if p["mad"] > 0:
            for (x0, y0, x1, y1) in ((395, 672, 520, 706), (830, 692, 715, 706)):
                a, b = (M @ np.array([x0, y0, 1]))[:2], (M @ np.array([x1, y1, 1]))[:2]
                m = mask_line(a, b, 12)
                L.pegar(m, np.array([30, 20, 20.]), 0)


POSES = [
    ("sentado mirando", dict(tilt=-3, look=(0.6, 0.2))),
    ("camina A", dict(leg=0.0, bob=-8)),
    ("camina B", dict(leg=0.5, bob=6)),
    ("olfatea", dict(tilt=4, look=(0.8, 0.9), bob=14)),
    ("salta", dict(tilt=-6, bob=-120, spread=1, look=(0, -1))),
    ("de espaldas", dict(flip=True, spread=1, blink=0.6)),
    ("enojado", dict(mad=1, tilt=2)),
    ("parpadea", dict(blink=1)),
]


def hoja(path):
    M = Mascota()
    cols, cw, ch = 4, 560, 520
    S = Image.new("RGB", (cols * cw, 2 * ch), (70, 94, 78))
    for i, (n, pz) in enumerate(POSES):
        im = M.frame(pz).crop((150, 20, 1300, 1090)).resize((cw, int(cw * 1070 / 1150)), Image.LANCZOS)
        S.paste(im, ((i % cols) * cw, (i // cols) * ch), im)
    S.save(path)


if __name__ == "__main__":
    hoja(sys.argv[1] if len(sys.argv) > 1 else "mascota_hoja.png")
