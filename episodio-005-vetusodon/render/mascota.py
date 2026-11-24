#!/usr/bin/env python3
"""Mascota del canal Río Puratense (v4): libro viviente gordo, LARGO como el diario real, acostado y con 4 patas. 2D pintado, sin 3D.

Cambios v4 (correcciones del usuario):
  * proporción real del libro (≈ 15 × 23 cm): largo, no cuadrado. «Gordo» = curvatura (tapas arqueadas, hojas abanicadas y
    abultadas, lomo redondeado), NO más cuadrado ni más corto.
  * vista 3/4 girada: el flanco largo (canto de hojas) se extiende; el canto inferior con los ojos mira al frente-izquierda.
    Dirección de marcha = hacia ese canto (eje largo).
  * pata peluda dorada GRANDE (ocupa casi toda la tapa, como la mano del diario).
  * las 4 patas salen de DEBAJO de la panza (el cuerpo las tapa en el arranque).
  * caminata: marcha lateral de 4 tiempos, el cuerpo sube/baja, se balancea, cabecea y se estira en la dirección de marcha;
    la tapa superior se retrasa un poco respecto del resto (overlap).
  * hoja suelta del tamaño de las hojas del cuerpo.

  python3 mascota.py HOJA.png      hoja de poses
  Mascota().frame(pose) -> PIL RGBA (lienzo 1500x1150, pensado para escalar)
"""
import math
import sys
import numpy as np
import cv2
from PIL import Image

W, H = 1500, 1150
OUT = np.array([34, 20, 16], np.float32)
V_LIT, V_MID, V_DRK = np.array([150, 58, 80.]), np.array([112, 46, 68.]), np.array([62, 30, 40.])
ROJO_DESG = np.array([170, 52, 44.])
GRIS_VERDE, GRIS_OSC = np.array([128, 134, 108.]), np.array([84, 88, 70.])
ORO_L, ORO_M, ORO_D = np.array([214, 206, 120.]), np.array([167, 162, 100.]), np.array([108, 100, 58.])
LATON_L, LATON_D = np.array([196, 168, 96.]), np.array([96, 76, 42.])
LOMO_C, LOMO_L = np.array([44, 45, 62.]), np.array([86, 86, 108.])
PAP_L, PAP_M, PAP_D = np.array([246, 234, 200.]), np.array([228, 210, 168.]), np.array([176, 154, 112.])
LINEA_PAG = np.array([150, 124, 86.])

# ---- tapa superior en pantalla: FL,FR (borde de adelante, ancho 15 cm) ; BACK = eje largo (23 cm) que se aleja hacia la derecha
FL, FR = np.array([290., 600.]), np.array([640., 648.])
BACK = np.array([590., -196.])
BL, BR = FL + BACK, FR + BACK
T_COVER, T_PAGES, T_BELLY = 32., 200., 34.
ANCHO_CM, LARGO_CM = 15., 23.
HEAD = -BACK / np.linalg.norm(BACK)                 # dirección de marcha (hacia el canto con los ojos)
LEG_LEN = 100.


def uv(x_cm, y_cm):
    return FL + (x_cm / ANCHO_CM) * (FR - FL) + (y_cm / LARGO_CM) * BACK


def spline(pts, n=14, closed=True):
    P = [np.array(p, float) for p in pts]
    m = len(P)
    out = []
    for i in (range(m) if closed else range(m - 1)):
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


def mask_line(p0, p1, w):
    m = np.zeros((H, W), np.uint8)
    cv2.line(m, (int(p0[0]), int(p0[1])), (int(p1[0]), int(p1[1])), 255, w, cv2.LINE_AA)
    return m


def mask_poly_line(pts, w):
    m = np.zeros((H, W), np.uint8)
    cv2.polylines(m, [np.round(np.array(pts)).astype(np.int32)], False, 255, w, cv2.LINE_AA)
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
        return Image.fromarray(np.dstack([np.clip(self.c, 0, 255), np.clip(self.a, 0, 1) * 255]).astype(np.uint8), "RGBA")


def degradado(c0, c1, p0, p1):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.array(p1, np.float32) - np.array(p0, np.float32)
    t = np.clip(((xx - p0[0]) * d[0] + (yy - p0[1]) * d[1]) / (d @ d), 0, 1)
    return t


def inflado(mask, dark, lit, radio=46, grano=10, seed=1, luz=None):
    dist = cv2.distanceTransform((mask > 127).astype(np.uint8), cv2.DIST_L2, 5)
    t = np.clip(dist / radio, 0, 1)[..., None]
    t = t * t * (3 - 2 * t)
    col = dark * (1 - t) + lit * t
    if luz is not None:
        col = col * luz[..., None]
    g = (noise(3, seed) - 0.5) * grano + (noise(18, seed + 7) - 0.5) * grano * 1.4
    return col + g[..., None]


def parche(A, B, C, D, bx, by, bu=0.6):
    """Parche bilineal con abultado de barril: u a lo largo del borde AB, v hacia abajo."""
    def P(u, v):
        base = (1 - v) * ((1 - u) * A + u * B) + v * ((1 - u) * D + u * C)
        return base + np.array([bx * (u - .5) * 2 * math.sin(math.pi * v) ** .8 if bu is None else bx * math.sin(math.pi * u) ** bu * math.sin(math.pi * v) ** .6,
                                by * math.sin(math.pi * u) ** .6 * v ** 1.3])
    return P


def contorno(P, n=24):
    return ([P(u, 0) for u in np.linspace(0, 1, n)] + [P(1, v) for v in np.linspace(0, 1, n)] +
            [P(u, 1) for u in np.linspace(1, 0, n)] + [P(0, v) for v in np.linspace(1, 0, n)])


ANCLAS = {}


def cuerpo(flip=False):
    """Devuelve (base, top): base = hojas/panza/lomo; top = tapa (dorso) con la pata, esquinas y cantos."""
    B, T = Lienzo(), Lienzo()
    nL = 34
    # ---- panza (tapa inferior abultada hacia abajo), costado frontal + flanco
    a = FL + [-8, T_COVER + T_PAGES - 10]; b = FR + [6, T_COVER + T_PAGES - 8]; c = BR + [6, T_COVER + T_PAGES - 8]
    pts = [a, (a + b) / 2, b, (b + c) / 2 + [4, 2], c, c + [6, T_BELLY - 10], (b + c) / 2 + [6, T_BELLY + 10], b + [6, T_BELLY + 8],
           (a + b) / 2 + [6, T_BELLY + 30], a + [-6, T_BELLY + 8]]
    pm = mask_of(spline(pts, 8))
    col = inflado(pm, GRIS_OSC * 0.8, GRIS_VERDE, radio=34, seed=3) if not flip else inflado(pm, V_DRK, V_MID, radio=34, seed=3)
    B.pegar(pm, col, 6)
    # ---- lomo redondeado (tira oscura que asoma a la izquierda del canto frontal)
    lomo = [FL + [6, T_COVER - 10], FL + [-34, T_COVER + 8], FL + [-52, T_COVER + 90], FL + [-46, T_COVER + T_PAGES - 24],
            FL + [-16, T_COVER + T_PAGES + 6], FL + [6, T_COVER + T_PAGES]]
    if not flip:
        lm = mask_of(spline(lomo, 8))
        B.pegar(lm, inflado(lm, LOMO_C * 0.7, LOMO_L, radio=24, seed=5), 5)
        for yb in (0.2, 0.45, 0.7, 0.9):
            y = FL[1] + T_COVER + yb * T_PAGES
            B.sobre(mask_line((FL[0] - 50, y), (FL[0] + 4, y + 6), 5), LOMO_L * 1.15, 0.8)
    # ---- hojas: canto frontal (con los ojos), abultado como barril
    Af, Bf = FL + [0, T_COVER], FR + [0, T_COVER]
    Cf, Df = FR + [0, T_COVER + T_PAGES], FL + [0, T_COVER + T_PAGES]
    Pf = parche(Af, Bf, Cf, Df, 58, 40, bu=None)
    fm = mask_of(contorno(Pf))
    luz = 0.84 + 0.22 * np.clip(degradado(0, 1, (FL[0], FL[1] + 400), (FL[0] + 160, FL[1] + 40)), 0, 1)
    B.pegar(fm, inflado(fm, PAP_D, PAP_L, radio=70, seed=9, luz=luz), 5)
    for k in range(1, nL):
        pts = np.array([Pf(u, k / nL) for u in np.linspace(0, 1, 30)])
        B.sobre(mask_poly_line(pts, 2 if k % 3 else 3), LINEA_PAG * (0.9 + 0.2 * ((k * 37) % 5) / 5), 0.45 if k % 3 else 0.6)
    ANCLAS["ojos"] = [np.array(Pf(0.27, 0.56)), np.array(Pf(0.73, 0.58))]
    ANCLAS["ceno"] = [(np.array(Pf(0.05, 0.40)), np.array(Pf(0.46, 0.50))), (np.array(Pf(0.96, 0.42)), np.array(Pf(0.52, 0.50)))]
    # sombra bajo la tapa
    ocl = np.zeros((H, W), np.uint8)
    pts = np.array([Pf(u, 0.0) for u in np.linspace(0, 1, 30)] + [Pf(u, 0.17) for u in np.linspace(1, 0, 30)])
    cv2.fillPoly(ocl, [np.round(pts).astype(np.int32)], 255, cv2.LINE_AA)
    B.sobre(cv2.GaussianBlur(ocl, (0, 0), 9) * (fm > 127), np.array([60, 36, 44.]), 0.55)
    # ---- hojas: flanco largo (canto de las hojas), abanicado y abultado
    Ar, Br = FR + [0, T_COVER], BR + [0, T_COVER]
    Cr, Dr = BR + [0, T_COVER + T_PAGES], FR + [0, T_COVER + T_PAGES]
    Pr = parche(Ar, Br, Cr, Dr, 34, 44, bu=0.6)
    rm = mask_of(contorno(Pr, 40))
    B.pegar(rm, inflado(rm, PAP_D * 0.78, PAP_M * 0.97, radio=70, seed=11, luz=0.92 + 0.1 * np.clip(degradado(0, 1, (FR[0] + 500, FR[1]), (FR[0], FR[1] - 100)), 0, 1)), 5)
    for k in range(1, nL):
        pts = np.array([Pr(u, k / nL) for u in np.linspace(0, 1, 50)])
        B.sobre(mask_poly_line(pts, 2), LINEA_PAG * 0.85, 0.45)
    ocl = np.zeros((H, W), np.uint8)
    pts = np.array([Pr(u, 0.0) for u in np.linspace(0, 1, 40)] + [Pr(u, 0.15) for u in np.linspace(1, 0, 40)])
    cv2.fillPoly(ocl, [np.round(pts).astype(np.int32)], 255, cv2.LINE_AA)
    B.sobre(cv2.GaussianBlur(ocl, (0, 0), 9) * (rm > 127), np.array([60, 36, 44.]), 0.5)
    # arrugas de hojas sueltas que asoman por el flanco (llenas de hojas)
    rs = np.random.RandomState(12)
    for _ in range(9):
        u = rs.uniform(0.1, 0.9); v = rs.uniform(0.3, 0.9)
        p = np.array(Pr(u, v)); ln = rs.uniform(40, 90)
        B.sobre(mask_line(p, p + [ln, -ln * 0.33], 3), PAP_L, 0.35)

    # ---- TOP: cantos de la tapa (grosor) + tapa arqueada
    for poly, seed in (([FL, FR, FR + [0, T_COVER], FL + [0, T_COVER]], 13), ([FR, BR, BR + [0, T_COVER], FR + [0, T_COVER]], 14)):
        mm = mask_of(poly)
        T.pegar(mm, inflado(mm, V_DRK * 0.8, V_MID * 0.95, radio=10, seed=seed), 4)
    mid = lambda p, q, o: (p + q) / 2 + np.array(o)
    cover_pts = [FL + [-8, 4], mid(FL, FR, [0, 20]), FR + [8, 8], mid(FR, BR, [8, 14]), BR + [8, -4], mid(BR, BL, [0, -34]), BL + [-8, -6], mid(BL, FL, [-10, -22])]
    cm = mask_of(spline(cover_pts, 12))
    luz = 0.86 + 0.22 * np.clip(degradado(0, 1, (BL[0] + 500, BL[1] + 400), (BL[0] - 80, BL[1] - 40)), 0, 1)
    base_d, base_l = (V_DRK, V_LIT) if not flip else (GRIS_OSC * 0.85, GRIS_VERDE * 1.05)
    colc = inflado(cm, base_d, base_l, radio=95, seed=17, grano=12, luz=luz)
    n1, n2 = noise(40, 21), noise(10, 22)
    desg = np.clip((n1 - 0.55) * 4, 0, 1) * np.clip((n2 - 0.35) * 2.2, 0, 1)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cerca = np.exp(-(((xx - FL[0]) ** 2 + (yy - FL[1]) ** 2) / (2 * 200 ** 2))) + np.exp(-(((xx - FR[0]) ** 2 + (yy - FR[1]) ** 2) / (2 * 220 ** 2)))
    if not flip:
        colc = colc * (1 - (desg * cerca)[..., None] * 0.7) + ROJO_DESG * (desg * cerca)[..., None] * 0.7
    T.pegar(cm, colc, 6)
    rr = np.random.RandomState(4)
    scr = np.zeros((H, W), np.uint8)
    for _ in range(50):
        x0, y0 = rr.uniform(FL[0], BR[0]), rr.uniform(BR[1], FR[1])
        an = rr.uniform(-0.6, 0.6); ln = rr.uniform(20, 90)
        cv2.line(scr, (int(x0), int(y0)), (int(x0 + math.cos(an) * ln), int(y0 + math.sin(an) * ln)), 255, 1, cv2.LINE_AA)
    T.sobre(scr * (cm > 127), np.array([220, 150, 150.]) if not flip else np.array([210, 215, 190.]), 0.16)
    edge = cv2.morphologyEx(cm, cv2.MORPH_GRADIENT, np.ones((5, 5), np.uint8))
    T.sobre(edge * (cm > 127), np.array([232, 140, 150.]), 0.28)

    def pl(pts_cm):
        return [uv(x, y) for x, y in pts_cm]

    def elipse(cx, cy, rx, ry, n=40, rot=0.0):
        t = np.linspace(0, 2 * math.pi, n, endpoint=False)
        px, py = rx * np.cos(t), ry * np.sin(t)
        co, si = math.cos(rot), math.sin(rot)
        return [(cx + px[i] * co - py[i] * si, cy + px[i] * si + py[i] * co) for i in range(n)]

    def peludo(pts, k=0.20, seed=0):
        r = np.random.RandomState(seed)
        c0 = np.mean(pts, 0)
        out = []
        for i, p in enumerate(pts):
            d = np.array(p) - c0; d = d / (np.linalg.norm(d) + 1e-6)
            out.append(np.array(p) + (d * k * r.uniform(0.5, 1.6) if i % 2 == 0 else d * k * 0.15))
        return out

    if not flip:
        # pata peluda dorada GRANDE (ocupa casi toda la tapa): almohadilla + 4 deditos gordos que apuntan hacia el fondo del libro
        partes = [(elipse(7.5, 8.2, 4.7, 4.1), 31), (elipse(2.7, 13.6, 2.15, 2.6, rot=0.35), 32), (elipse(5.7, 16.9, 2.35, 2.9, rot=0.12), 33),
                  (elipse(9.3, 16.9, 2.35, 2.9, rot=-0.12), 34), (elipse(12.3, 13.6, 2.15, 2.6, rot=-0.35), 35)]
        for pts, sd in partes:
            mk = mask_of(pl(peludo(pts, 0.26, sd)))
            T.pegar(mk, inflado(mk, ORO_D, ORO_L, radio=34, seed=sd, grano=14), 3)
        # rayones del metal
        scr2 = np.zeros((H, W), np.uint8)
        rr = np.random.RandomState(8)
        for _ in range(90):
            x0, y0 = rr.uniform(1.5, 13.5), rr.uniform(4, 19)
            an = rr.uniform(0.3, 1.1); ln = rr.uniform(0.5, 2.4)
            p0, p1 = uv(x0, y0), uv(x0 + math.cos(an) * ln, y0 + math.sin(an) * ln)
            cv2.line(scr2, (int(p0[0]), int(p0[1])), (int(p1[0]), int(p1[1])), 255, 1, cv2.LINE_AA)
        T.sobre(scr2 * (cm > 127), np.array([240, 235, 170.]), 0.35)
        # almohadillas internas (más oscuras) y pelitos finos
        for (cx, cy, rx, ry) in ((7.5, 7.4, 2.6, 2.1), (2.8, 13.1, 0.9, 1.1), (5.8, 16.3, 1.0, 1.2), (9.2, 16.3, 1.0, 1.2), (12.2, 13.1, 0.9, 1.1)):
            T.sobre(mask_of(pl(elipse(cx, cy, rx, ry))), ORO_D * 0.82, 0.5)
        pelo = np.zeros((H, W), np.uint8)
        for _ in range(140):
            x0, y0 = rr.uniform(1.2, 13.8), rr.uniform(3.8, 19.2)
            p0, p1 = uv(x0, y0), uv(x0 + rr.uniform(-0.25, 0.25), y0 + rr.uniform(0.25, 0.7))
            cv2.line(pelo, (int(p0[0]), int(p0[1])), (int(p1[0]), int(p1[1])), 255, 1, cv2.LINE_AA)
        pm_all = np.zeros((H, W), np.uint8)
        for pts, sd in partes:
            pm_all = np.maximum(pm_all, mask_of(pl(pts)))
        T.sobre(pelo * (pm_all > 127), np.array([250, 244, 190.]), 0.4)

    def esquina(cx, cy, dx, dy, k=4.8):
        a_, b_ = (cx + dx * k, cy), (cx, cy + dy * k * 0.9)
        ctrl = (cx + dx * k * 0.5, cy + dy * k * 0.45)
        pts = [(cx, cy), a_]
        for t in np.linspace(0, 1, 12):
            q = (1 - t) ** 2 * np.array(a_) + 2 * (1 - t) * t * np.array(ctrl) + t ** 2 * np.array(b_)
            pts.append(tuple(q))
        pts.append(b_)
        return pts
    for (cx, cy, dx, dy) in ((0, 0, 1, 1), (15, 0, -1, 1), (0, 23, 1, -1), (15, 23, -1, -1)):
        mk = mask_of(pl(esquina(cx, cy, dx, dy)))
        T.pegar(mk, inflado(mk, LATON_D, LATON_L, radio=20, seed=cx + cy + 40, grano=16), 3)
        c0 = uv(cx + dx * 1.25, cy + dy * 1.25)
        rm_ = np.zeros((H, W), np.uint8); cv2.circle(rm_, (int(c0[0]), int(c0[1])), 9, 255, -1, cv2.LINE_AA)
        T.pegar(rm_, np.array([224, 200, 140.]), 2)
        hl = np.zeros((H, W), np.uint8); cv2.circle(hl, (int(c0[0]) - 3, int(c0[1]) - 3), 3, 255, -1, cv2.LINE_AA)
        T.sobre(hl, np.array([255, 250, 230.]), 0.9)
    return B, T


# -------------------------------------------------------------------------------------------- hoja suelta (tamaño real de las hojas)
def hoja_grande(w=330, h=440, rizo=0.0):
    """Hoja del libro pintada: cartulina crema con renglones, borde irregular y una esquina doblada."""
    S = 2
    img = np.zeros((h * S, w * S, 3), np.float32)
    a = np.zeros((h * S, w * S), np.uint8)
    r = np.random.RandomState(5)
    pts = [(14, 14), (w * .5, 8 + rizo * 6), (w - 14, 16), (w - 8, h * .5), (w - 16, h - 14 - rizo * 10), (w * .5, h - 8), (14, h - 16), (8, h * .5)]
    sp = spline([(x * S, y * S) for x, y in pts], 12)
    cv2.fillPoly(a, [np.round(sp * 16).astype(np.int32)], 255, cv2.LINE_AA, shift=4)
    yy, xx = np.mgrid[0:h * S, 0:w * S].astype(np.float32)
    t = np.clip((yy / (h * S) * 0.7 + xx / (w * S) * 0.3), 0, 1)[..., None]
    base = PAP_L * (1 - t) + PAP_D * t
    g = cv2.resize(r.rand(h // 3, w // 3).astype(np.float32), (w * S, h * S), interpolation=cv2.INTER_CUBIC)
    img[:] = base + (g[..., None] - 0.5) * 16
    for yv in range(70, h - 30, 26):
        cv2.line(img, (int(30 * S), yv * S), (int((w - 34) * S), (yv + int(rizo * 6)) * S), tuple(float(v) for v in LINEA_PAG), 2, cv2.LINE_AA)
    cv2.line(img, (int(48 * S), 60 * S), (int(48 * S), (h - 30) * S), (190., 120., 120.), 2, cv2.LINE_AA)
    # esquina doblada
    tri = np.array([[w - 120, h - 8], [w - 8, h - 120], [w - 8, h - 8]]) * S
    ca = np.zeros_like(a); cv2.fillPoly(ca, [tri.astype(np.int32)], 255, cv2.LINE_AA)
    img = img * (1 - ca[..., None] / 255 * 0.6) + np.array([206, 186, 146.]) * (ca[..., None] / 255 * 0.6)
    edge = cv2.morphologyEx(a, cv2.MORPH_GRADIENT, np.ones((7, 7), np.uint8))
    out = np.zeros((h * S, w * S, 4), np.uint8)
    o = cv2.dilate(a, np.ones((9, 9), np.uint8))
    out[..., :3] = np.where(o[..., None] > 0, OUT, 0).astype(np.uint8)
    m = (a > 127)
    out[..., :3][m] = np.clip(img, 0, 255).astype(np.uint8)[m]
    out[..., 3] = o
    return Image.fromarray(out, "RGBA").resize((w, h), Image.LANCZOS)


# -------------------------------------------------------------------------------------------- patas y animación
def pata(L, hip, knee, foot, w=52, cuerpo_col=np.array([30, 26, 32.])):
    for a, b, ww in ((hip, knee, w), (knee, foot, w * 0.86)):
        m = np.zeros((H, W), np.uint8)
        cv2.line(m, tuple(int(v) for v in a), tuple(int(v) for v in b), 255, int(ww), cv2.LINE_AA)
        cv2.circle(m, tuple(int(v) for v in b), int(ww / 2), 255, -1, cv2.LINE_AA)
        L.pegar(m, cuerpo_col, 0)
        hl = np.zeros((H, W), np.uint8)
        off = np.array([-ww * 0.22, 0])
        cv2.line(hl, tuple(int(v) for v in (a + off)), tuple(int(v) for v in (b + off)), 255, max(2, int(ww * 0.16)), cv2.LINE_AA)
        L.sobre(hl, np.array([96, 90, 110.]), 0.6)
    fm = np.zeros((H, W), np.uint8)
    cv2.ellipse(fm, (int(foot[0] + 6), int(foot[1] + 4)), (int(w * 0.92), int(w * 0.46)), 0, 0, 360, 255, -1, cv2.LINE_AA)
    L.pegar(fm, cuerpo_col, 0)


# patas: A = delantera lejana (bajo FL), B = delantera cercana (bajo FR), C = trasera cercana (bajo BR), D = trasera lejana (bajo BL)
def _caderas():
    yb = T_COVER + T_PAGES + T_BELLY - 4
    return {"A": FL + [80, yb + 18], "B": FR + [-50, yb + 36], "C": BR + [-80, yb - 8], "D": BL + [40, yb - 26]}


FASE = {"C": 0.0, "B": 0.25, "D": 0.5, "A": 0.75}                 # marcha lateral de 4 tiempos


def mov_cuerpo(leg):
    """Movimiento del cuerpo para una fase de caminata 0..1 (peso, balanceo, cabeceo en la dirección de marcha)."""
    ph = leg % 1.0
    bob = 9 * math.cos(4 * math.pi * ph + 0.4)                       # sube/baja 2 veces por ciclo
    sway = 11 * math.sin(2 * math.pi * ph)                           # el peso pasa de lado a lado
    roll = 1.8 * math.sin(2 * math.pi * ph)
    pitch = 2.4 + 1.6 * math.sin(4 * math.pi * ph)                   # cabecea hacia donde camina
    sq = 1 + 0.014 * math.sin(4 * math.pi * ph + 1.1)
    lag = 6 * math.sin(2 * math.pi * ph - 0.9)                       # la tapa llega un poco después
    return dict(bob=bob, sway=sway, tilt=roll + pitch, squash=sq, lag=lag)


class Mascota:
    def __init__(self):
        self.cache = {}

    def _cuerpo(self, flip):
        if flip not in self.cache:
            self.cache[flip] = cuerpo(flip)
        return self.cache[flip]

    def frame(self, pose=None):
        p = dict(leg=None, bob=0.0, sway=0.0, tilt=0.0, squash=1.0, lag=0.0, blink=0.0, mad=0.0, look=(0, 0), flip=False, spread=0.0, auto=True)
        p.update(pose or {})
        if p["leg"] is not None and p["auto"]:
            m = mov_cuerpo(p["leg"])
            for k in ("bob", "sway", "tilt", "lag"):
                p[k] += m[k]
            p["squash"] *= m["squash"]
        flip = p["flip"]
        base, top = self._cuerpo(flip)
        out = Lienzo()
        G = 1040
        # transformación del cuerpo: rebote + balanceo + cabeceo + aplastado, anclada al suelo
        cx, cy = 780, 760
        Rm = cv2.getRotationMatrix2D((cx, cy), p["tilt"], 1.0)
        M = np.vstack([Rm, [0, 0, 1]]) @ np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], float)
        sy = p["squash"]
        M = np.array([[1, 0, p["sway"]], [0, sy, p["bob"] + cy * (1 - sy)], [0, 0, 1]]) @ M
        Mt = np.array([[1, 0, -p["lag"] * HEAD[0] * 0.8], [0, 1, -p["lag"] * HEAD[1] * 0.8 + 0.4 * p["lag"]], [0, 0, 1]]) @ M

        def warp(L, Mx):
            img = np.dstack([L.c, L.a[..., None] * 255]).astype(np.float32)
            w_ = cv2.warpAffine(img, Mx[:2], (W, H), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
            return w_
        # sombra de contacto
        sh = np.zeros((H, W), np.uint8)
        cv2.ellipse(sh, (800 + int(p["sway"] * 0.3), G - 36), (580, 82), -8, 0, 360, 255, -1, cv2.LINE_AA)
        out.sobre(cv2.GaussianBlur(sh, (0, 0), 24), np.array([16, 8, 28.]), 0.45)

        cad = _caderas()
        patas = {}
        swing = 56.0
        for k, hip in cad.items():
            hip_m = (M @ np.array([hip[0], hip[1], 1]))[:2]
            suelo_y = hip[1] + LEG_LEN + (14 if k == "B" else 0)
            if flip:
                continue
            if p["leg"] is None:
                u, lift, off = 0.0, 0.0, 0.0
            else:
                u = (p["leg"] + FASE[k]) % 1.0
                if u < 0.62:                                           # apoyo: el pie va hacia atrás respecto del cuerpo
                    off = swing * (1 - 2 * (u / 0.62)) * 0.5
                    lift = 0.0
                else:                                                  # vuelo: se levanta y va hacia adelante
                    q = (u - 0.62) / 0.38
                    off = swing * (-0.5 + q) * 1.0
                    lift = 40 * math.sin(math.pi * q)
            foot = np.array([hip[0] + p["spread"] * (60 if hip[0] > 700 else -60) + off * HEAD[0] * -1 * -1, suelo_y - lift])
            foot[0] = hip[0] + off * (-1 if HEAD[0] < 0 else 1) * -1
            foot[0] += p["spread"] * (60 if hip[0] > 700 else -60)
            knee = (hip_m + foot) / 2 + np.array([-12 if HEAD[0] < 0 else 12, 4]) + np.array([0, -6 * (lift / 40)])
            patas[k] = (hip_m + [0, 6], knee, foot)
        if not flip:
            for k in ("D", "C", "A", "B"):
                if k in patas:
                    pata(out, *patas[k], w=58 if k in "DC" else 68)
        wb = warp(base, M)
        a_ = wb[..., 3:4] / 255
        out.c = out.c * (1 - a_) + wb[..., :3] * a_
        out.a = np.maximum(out.a, a_[..., 0])
        wt = warp(top, Mt)
        a_ = wt[..., 3:4] / 255
        out.c = out.c * (1 - a_) + wt[..., :3] * a_
        out.a = np.maximum(out.a, a_[..., 0])
        if flip:                                                       # patas al aire, saliendo de la tapa (que ahora es la panza)
            for i, (cmx, cmy) in enumerate(((2.8, 3.2), (12.2, 3.2), (12.2, 20.0), (2.8, 20.0))):
                hip = (Mt @ np.array([*uv(cmx, cmy), 1]))[:2]
                side = 1 if cmx > 7.5 else -1
                sw_ = 30 * math.sin((p["leg"] or 0) * 2 * math.pi + i) if p["leg"] is not None else 0
                foot = hip + np.array([side * 30 + sw_, -190 - 12 * math.sin(i * 1.7)]) + np.array([p["spread"] * side * 25, 0])
                knee = hip + np.array([side * 34, -100])
                pata(out, hip, knee, foot, w=50)
        self._ojos(out, p, M, flip)
        return out.imagen()

    def _ojos(self, L, p, M, flip):
        anclas = ANCLAS.get("ojos")
        if anclas is None:
            return
        r = 31
        for e in anclas:
            pt = (M @ np.array([e[0], e[1], 1]))[:2]
            soc = np.zeros((H, W), np.uint8)
            cv2.ellipse(soc, (int(pt[0]), int(pt[1] + 4)), (int(r * 1.45), int(r * 1.3)), 0, 0, 360, 255, -1, cv2.LINE_AA)
            L.sobre(cv2.GaussianBlur(soc, (0, 0), 7), np.array([120, 84, 52.]), 0.5)
            ry = max(2, int(r * (1 - 0.92 * p["blink"])))
            ob = np.zeros((H, W), np.uint8)
            cv2.ellipse(ob, (int(pt[0]), int(pt[1])), (r, ry), 0, 0, 360, 255, -1, cv2.LINE_AA)
            L.pegar(ob, np.array([18, 14, 20.]), 2)
            if p["blink"] < 0.6:
                lx, ly = p["look"]
                hl = np.zeros((H, W), np.uint8)
                cv2.circle(hl, (int(pt[0] - 8 + lx * 5), int(pt[1] - 9 + ly * 4)), 7, 255, -1, cv2.LINE_AA)
                L.sobre(hl, np.array([255, 255, 255.]), 0.95)
                h2 = np.zeros((H, W), np.uint8)
                cv2.circle(h2, (int(pt[0] + 9), int(pt[1] + 9)), 4, 255, -1, cv2.LINE_AA)
                L.sobre(h2, np.array([120, 116, 150.]), 0.6)
        if p["mad"] > 0:
            for a, b in ANCLAS["ceno"]:
                a_, b_ = (M @ np.array([a[0], a[1] - 54, 1]))[:2], (M @ np.array([b[0], b[1] - 34, 1]))[:2]
                L.pegar(mask_line(a_, b_, 11), np.array([30, 20, 20.]), 0)


POSES = [
    ("sentado mirando", dict(tilt=-2, look=(-0.6, 0.2))),
    ("camina A", dict(leg=0.0)),
    ("camina B", dict(leg=0.25)),
    ("camina C", dict(leg=0.5)),
    ("olfatea", dict(tilt=5, look=(-0.8, 0.9), bob=14)),
    ("salta", dict(tilt=4, bob=-130, spread=1, look=(-1, -1))),
    ("de espaldas", dict(flip=True, spread=1, blink=0.6)),
    ("enojado", dict(mad=1, tilt=-2)),
]


def hoja(path):
    M = Mascota()
    cols, cw, ch = 4, 560, 460
    S = Image.new("RGB", (cols * cw, 2 * ch), (70, 94, 78))
    for i, (n, pz) in enumerate(POSES):
        im = M.frame(pz).crop((200, 330, 1400, 1130)).resize((cw, int(cw * 800 / 1200)), Image.LANCZOS)
        S.paste(im, ((i % cols) * cw, (i // cols) * ch), im)
    S.save(path)


if __name__ == "__main__":
    hoja(sys.argv[1] if len(sys.argv) > 1 else "mascota_hoja.png")
