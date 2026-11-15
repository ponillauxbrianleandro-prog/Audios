"""Flora del Pérmico tardío del Karoo como sprites procedurales con alfa.

- Colas de caballo (esfenófitas tipo Phyllotheca) junto al agua.
- Helechos bajos.
- Glossopteris: árbol de hojas con forma de lengua agrupadas en penachos.
- Rocas.
No hay hierba ni flores: todavía no existen.
Cada sprite: dict(rgb premultiplicado float32, a float32, ppm, kind).
"""
import numpy as np
import cv2
from util import fbm

SS = 2


def _finish(rgb, a, ppm, kind, soft=0.6, seed=0):
    h, w = a.shape
    # volumen: luz desde arriba-izquierda, interior en sombra y moteado orgánico
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dens = cv2.GaussianBlur(a, (0, 0), max(4.0, w / 14.0))
    dl = cv2.GaussianBlur(a, (0, 0), max(3.0, w / 30.0))
    sh = np.roll(dl, (int(w / 40) + 2, int(w / 40) + 2), (0, 1))          # masa hacia abajo-derecha
    lit = np.clip(1.0 + (dl - sh) * 1.6, 0.55, 1.45)
    core = 1.0 - 0.45 * np.clip(dens * 1.5 - 0.55, 0, 1)
    mot = cv2.resize(fbm((256, 256), 1.5, 900 + seed), (w, h), interpolation=cv2.INTER_LINEAR)
    k = (lit * core * (0.78 + 0.44 * mot))[..., None]
    rgb = rgb * k * np.array([0.97, 1.0, 1.03], np.float32)
    gray = rgb.mean(-1, keepdims=True)
    rgb = rgb * 0.74 + gray * 0.26
    rgb = cv2.GaussianBlur(rgb, (0, 0), soft * SS)
    a = cv2.GaussianBlur(a, (0, 0), soft * SS)
    rgb = cv2.resize(rgb, (w // SS, h // SS), interpolation=cv2.INTER_AREA)
    a = cv2.resize(a, (w // SS, h // SS), interpolation=cv2.INTER_AREA)
    return dict(rgb=rgb.astype(np.float32), a=a.astype(np.float32), ppm=ppm, kind=kind)


class Canvas:
    """Lienzo con color premultiplicado: cada trazo tapa lo anterior (orden de pintor)."""

    def __init__(self, wm, hm, ppm):
        self.ppm = ppm
        self.s = ppm * SS
        self.w, self.h = int(wm * self.s), int(hm * self.s)
        self.rgb = np.zeros((self.h, self.w, 3), np.float32)
        self.a = np.zeros((self.h, self.w), np.float32)

    def pt(self, x, y):
        return (int(round((self.w / 2 + x * self.s) * 16)), int(round((self.h - 2 - y * self.s) * 16)))

    def line(self, p0, p1, col, th):
        t = max(1, int(round(th * self.s)))
        a, b = self.pt(*p0), self.pt(*p1)
        cv2.line(self.rgb, a, b, [float(c) for c in col], t, cv2.LINE_AA, 4)
        cv2.line(self.a, a, b, 1.0, t, cv2.LINE_AA, 4)

    def poly(self, pts, col):
        p = np.array([self.pt(x, y) for x, y in pts], np.int32)
        cv2.fillPoly(self.rgb, [p], [float(c) for c in col], cv2.LINE_AA, 4)
        cv2.fillPoly(self.a, [p], 1.0, cv2.LINE_AA, 4)

    def leaf(self, x, y, ang, ln, wd, col):
        """Hoja lanceolada/lingüiforme con nervio central."""
        ca, sa = np.cos(ang), np.sin(ang)
        t = np.linspace(0, 1, 9)
        half = wd * np.sin(np.pi * t ** 0.8) ** 0.9
        px, py = x + ca * ln * t, y + sa * ln * t
        L = np.stack([px - sa * half, py + ca * half], 1)
        R = np.stack([px + sa * half, py - ca * half], 1)[::-1]
        self.poly(np.vstack([L, R]), col)


def horsetail(seed, ppm=420):
    rng = np.random.default_rng(seed)
    hm = rng.uniform(0.7, 1.45)
    c = Canvas(1.3, hm + 0.15, ppm)
    n = rng.integers(5, 15)
    stems = sorted([(rng.normal(0, 0.2), rng.uniform(0.45, 1.0) * hm, rng.uniform(0, 1)) for _ in range(n)], key=lambda s: s[2])
    for bx, ht, depth in stems:
        lean = rng.normal(0, 0.10) + bx * 0.18
        dark = 0.55 + 0.45 * depth
        base = np.array([0.20, 0.29, 0.17]) * dark * rng.uniform(0.75, 1.15)
        lite = np.array([0.40, 0.48, 0.29]) * dark * rng.uniform(0.75, 1.15)
        th = rng.uniform(0.006, 0.012)
        y, x = 0.0, bx
        seg = rng.uniform(0.045, 0.07)
        k = 0
        while y < ht:
            y2 = min(ht, y + seg)
            x2 = x + lean * seg + rng.normal(0, 0.002)
            f = y / ht
            if f > 0.22 and k % 1 == 0:
                nl = rng.integers(5, 9)
                ll = seg * rng.uniform(1.6, 2.6) * (1 - 0.55 * f)
                for j in range(nl):
                    side = -1 if j % 2 else 1
                    ang = np.pi / 2 - side * rng.uniform(0.5, 1.15)
                    lc = lite * rng.uniform(0.7, 1.1) if side < 0 else base * rng.uniform(0.9, 1.3)
                    c.line((x, y), (x + np.cos(ang) * ll, y + np.sin(ang) * ll), lc, 0.0022)
            tt = th * (1 - 0.6 * f)
            c.line((x, y), (x2, y2), base, tt)
            c.line((x - tt * 0.25, y), (x2 - tt * 0.25, y2), lite, tt * 0.45)
            c.line((x - tt * 0.6, y), (x + tt * 0.6, y), base * 0.55, 0.003)
            x, y = x2, y2
            k += 1
        if rng.uniform() < 0.3:     # estróbilo en la punta
            c.leaf(x, y, np.pi / 2, 0.03, 0.006, np.array([0.45, 0.40, 0.25]) * dark)
    return _finish(c.rgb, c.a, ppm, "horsetail")


def fern(seed, ppm=420):
    rng = np.random.default_rng(seed)
    R = rng.uniform(0.35, 0.75)
    c = Canvas(R * 2.3, R * 1.25 + 0.1, ppm)
    n = rng.integers(9, 17)
    fr = sorted([(rng.uniform(-1.25, 1.25), rng.uniform(0.6, 1.0) * R, rng.uniform(0, 1)) for _ in range(n)], key=lambda s: s[2])
    for a0, L, depth in fr:
        dark = 0.5 + 0.5 * depth
        g1 = np.array([0.16, 0.26, 0.14]) * dark * rng.uniform(0.85, 1.15)
        g2 = np.array([0.32, 0.43, 0.23]) * dark * rng.uniform(0.85, 1.15)
        m = 26
        t = np.linspace(0, 1, m)
        ang = np.pi / 2 - a0 * (0.35 + 0.9 * t ** 1.3)          # arqueo hacia afuera
        dx, dy = np.cos(ang) * L / m, np.sin(ang) * L / m
        xs, ys = np.cumsum(dx), np.cumsum(dy)
        for i in range(2, m - 1):
            pl = L * 0.20 * np.sin(np.pi * t[i] ** 0.75) ** 0.8 + 0.004
            for side in (-1, 1):
                pa = ang[i] + side * rng.uniform(1.0, 1.3)
                colr = g2 if (np.cos(pa) < 0) else g1
                c.leaf(xs[i], ys[i], pa, pl, pl * 0.16 + 0.002, colr * rng.uniform(0.85, 1.12))
        for i in range(m - 1):
            c.line((xs[i], ys[i]), (xs[i + 1], ys[i + 1]), g1 * 0.8, 0.003)
    return _finish(c.rgb, c.a, ppm, "fern")


def glossopteris(seed, ppm=90, height=None):
    rng = np.random.default_rng(seed)
    H = height or rng.uniform(4.5, 8.5)
    Wm = H * 0.95
    c = Canvas(Wm * 1.45, H * 1.12 + 0.3, ppm)
    bark = np.array([0.33, 0.29, 0.26])
    tips = []

    def branch(x, y, ang, ln, th, lvl):
        segs = 5
        for i in range(segs):
            a2 = ang + rng.normal(0, 0.10)
            x2, y2 = x + np.cos(a2) * ln / segs, y + np.sin(a2) * ln / segs
            sh = 0.75 + 0.35 * (np.cos(a2) < 0)
            c.line((x, y), (x2, y2), bark * sh * rng.uniform(0.9, 1.1), th * (1 - 0.12 * i))
            if th > 0.03:
                c.line((x - th * 0.22, y), (x2 - th * 0.22, y2), bark * 1.35, th * 0.3)
            x, y = x2, y2
            if lvl >= 2 or (lvl == 1 and i >= 2):
                tips.append((x, y, lvl))
        if lvl < 3:
            for _ in range(rng.integers(2, 4)):
                branch(x, y, ang + rng.uniform(-0.8, 0.8), ln * rng.uniform(0.5, 0.7), th * 0.55, lvl + 1)

    # tronco recto y ramas en pisos, como una conífera de hoja ancha
    trunk_top = H * 0.93
    n = 14
    px, py = 0.0, 0.0
    for i in range(n):
        f = i / n
        x2, y2 = px + rng.normal(0, 0.012 * H / 6), trunk_top * (i + 1) / n
        th = 0.045 * H * (1 - 0.85 * f) + 0.02
        c.line((px, py), (x2, y2), bark * rng.uniform(0.9, 1.05), th)
        c.line((px - th * 0.25, py), (x2 - th * 0.25, y2), bark * 1.3, th * 0.28)
        px, py = x2, y2
        if f > 0.25:
            for side in (-1, 1):
                if rng.uniform() < 0.9:
                    ln = Wm * 0.30 * (1 - f) ** 0.7 * rng.uniform(0.7, 1.05) + 0.25
                    ang = np.pi / 2 - side * rng.uniform(0.95, 1.35)
                    branch(px, py - rng.uniform(0, 0.2), ang, ln, th * 0.42, 1)
    tips.append((px, py, 3))
    # follaje: penachos de hojas lingüiformes; primero el interior oscuro, luego las hojas iluminadas
    cx_top = H * 0.6
    leaves = []
    for (x, y, lvl) in tips:
        for _ in range(rng.integers(26, 44)):
            a = rng.uniform(0, 2 * np.pi)
            ln = rng.uniform(0.11, 0.20)
            ox, oy = rng.normal(0, 0.16), rng.normal(0, 0.13)
            lightk = 0.5 + 0.5 * np.clip((y + oy - H * 0.3) / (H * 0.6), 0, 1) - 0.35 * (x + ox) / Wm + 0.25 * np.sin(a)
            leaves.append((rng.uniform() + lightk, x + ox, y + oy, a, ln, lightk))
    leaves.sort(key=lambda l: l[0])
    for _, x, y, a, ln, lk in leaves:
        lk = np.clip(lk + rng.normal(0, 0.12), 0, 1.1)
        col = np.array([0.07, 0.12, 0.08]) * (1 - lk) + np.array([0.30, 0.39, 0.20]) * lk
        if rng.uniform() < 0.04:
            col = np.array([0.50, 0.46, 0.22]) * (0.6 + 0.4 * lk)      # alguna hoja amarillenta
        c.leaf(x, y, a, ln, ln * 0.17, col)
    return _finish(c.rgb, c.a, ppm, "tree", soft=0.5)


def shrub(seed, ppm=240):
    """Glossopteris joven: mata de 1-2,5 m."""
    rng = np.random.default_rng(seed)
    H = rng.uniform(1.0, 2.4)
    c = Canvas(H * 1.1, H + 0.2, ppm)
    bark = np.array([0.30, 0.26, 0.22])
    leaves = []
    for _ in range(rng.integers(4, 8)):
        ang = np.pi / 2 + rng.normal(0, 0.45)
        L = H * rng.uniform(0.55, 0.95)
        x, y = rng.normal(0, 0.03), 0.0
        for i in range(8):
            ang += rng.normal(0, 0.09)
            x2, y2 = x + np.cos(ang) * L / 8, y + np.sin(ang) * L / 8
            c.line((x, y), (x2, y2), bark * rng.uniform(0.85, 1.15), 0.02 * (1 - i / 10))
            x, y = x2, y2
            if i >= 2:
                for _ in range(rng.integers(4, 9)):
                    a = rng.uniform(0, 2 * np.pi)
                    lk = 0.45 + 0.4 * y / H - 0.4 * x / H + 0.25 * np.sin(a)
                    leaves.append((rng.uniform() + lk, x + rng.normal(0, 0.05), y + rng.normal(0, 0.05), a, rng.uniform(0.12, 0.2), lk))
    leaves.sort(key=lambda l: l[0])
    for _, x, y, a, ln, lk in leaves:
        lk = np.clip(lk + rng.normal(0, 0.1), 0, 1.1)
        col = np.array([0.10, 0.17, 0.10]) * (1 - lk) + np.array([0.37, 0.48, 0.23]) * lk
        c.leaf(x, y, a, ln, ln * 0.18, col)
    return _finish(c.rgb, c.a, ppm, "shrub", soft=0.5)


def rock(seed, ppm=420):
    rng = np.random.default_rng(seed)
    wm = rng.uniform(0.18, 0.75)
    hm = wm * rng.uniform(0.35, 0.65)
    w, h = int(wm * ppm), int(hm * ppm)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u = (xx / w - 0.5) * 2
    v = 1 - yy / h
    n = cv2.resize(fbm((256, 256), 2.2, seed), (w, h))
    n2 = cv2.resize(fbm((256, 256), 1.4, seed + 1), (w, h))
    prof = np.sqrt(np.clip(1 - np.abs(u) ** 2.4, 0, 1)) * (0.75 + 0.5 * n)
    mask = np.clip((prof - v) * h / 2.0, 0, 1)
    dome = np.sqrt(np.clip(1 - u * u * 0.9 - (v / np.maximum(prof, 1e-3)) ** 2 * 0.8, 0, 1)) * hm / wm * 2
    dome = cv2.GaussianBlur(dome + 0.22 * n + 0.03 * n2, (0, 0), 3.5)
    gy, gx = np.gradient(dome * w * 0.5)
    nrm = np.stack([-gx, gy, np.ones_like(gx)], -1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    ndl = np.clip(nrm[..., 0] * -0.55 + nrm[..., 1] * 0.6 + nrm[..., 2] * 0.45, 0, 1)
    alb = np.array([0.50, 0.48, 0.46]) * (0.85 + 0.3 * n2[..., None]) * rng.uniform(0.8, 1.1)
    col = alb * (0.35 + 0.95 * ndl[..., None]) * (0.55 + 0.45 * np.clip(v * 3, 0, 1))[..., None]
    mask = cv2.GaussianBlur(mask, (0, 0), 0.8)
    return dict(rgb=(col * mask[..., None]).astype(np.float32), a=mask.astype(np.float32), ppm=ppm, kind="rock")


def library():
    import os, pickle
    from world import CACHE
    p = os.path.join(CACHE, "plants.pkl")
    if os.path.exists(p):
        return pickle.load(open(p, "rb"))
    lib = dict(
        horsetail=[horsetail(100 + i) for i in range(8)],
        fern=[fern(200 + i) for i in range(8)],
        tree=[glossopteris(300 + i) for i in range(8)],
        shrub=[shrub(400 + i) for i in range(6)],
        rock=[rock(500 + i) for i in range(8)],
    )
    pickle.dump(lib, open(p, "wb"))
    return lib
