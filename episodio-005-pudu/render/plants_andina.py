"""Flora del bosque andino-patagónico (selva valdiviana) como sprites procedurales con alfa.

- nalca (Gunnera tinctoria): hojas enormes, redondeadas y lobuladas sobre pecíolos gruesos.
- colihue (Chusquea culeou): cañas finas que arquean, con hojas lanceoladas colgantes.
- coihue: el árbol del motor (glossopteris) reteñido de verde oscuro y cubierto de musgo.
- helecho verde, helecho arborescente, tronco caído con musgo.
Cada sprite: dict(rgb, a, ppm, kind) como en plants.py.
"""
import os
import pickle
import numpy as np
import cv2
from plants import Canvas, _finish, SS, fern, glossopteris, treefern, log, mossmat, rock, mossify, recolor, hongo, stump
from util import fbm


def nalca(seed, ppm=240):
    rng = np.random.default_rng(seed)
    n = int(rng.integers(3, 7))
    W, Hh = 3.0, 2.0
    c = Canvas(W, Hh, ppm)
    leaves = sorted([(rng.uniform(-1.0, 1.0), rng.uniform(0.9, 1.7), rng.uniform(0.55, 1.15), rng.uniform(0, 1)) for _ in range(n)],
                    key=lambda s: s[3])
    for bx, hy, rw, depth in leaves:
        dark = 0.55 + 0.45 * depth
        stalk = np.array([0.30, 0.34, 0.16]) * dark
        # pecíolo grueso con espinitas
        x0, y0 = bx * 0.25, 0.0
        for i in range(16):
            f = i / 16
            xa, ya = x0 + (bx - x0) * f ** 1.3, hy * f
            xb, yb = x0 + (bx - x0) * ((i + 1) / 16) ** 1.3, hy * (i + 1) / 16
            c.line((xa, ya), (xb, yb), stalk * (0.9 + 0.2 * f), 0.045 * (1 - 0.4 * f))
            if i % 2 == 0:
                c.line((xa, ya), (xa + rng.normal(0, 0.02), ya + 0.02), stalk * 1.3, 0.006)
        # limbo: elipse achatada con lóbulos y muescas
        cx, cy = bx, hy + 0.05
        hw, hh = rw * 0.55, rw * 0.30
        th = np.linspace(0, 2 * np.pi, 120, endpoint=False)
        ph = rng.uniform(0, 6.28)
        r = 1 + 0.10 * np.cos(7 * th + ph) + 0.07 * np.cos(13 * th + 2 * ph) - 0.12 * np.clip(np.cos(7 * th + ph) - 0.7, 0, 1) * 3
        tilt = rng.uniform(-0.25, 0.25)
        pts = [(cx + np.cos(a) * rr * hw * np.cos(tilt) - np.sin(a) * rr * hh * np.sin(tilt),
                cy + np.sin(a) * rr * hh * np.cos(tilt) + np.cos(a) * rr * hw * np.sin(tilt)) for a, rr in zip(th, r)]
        g1 = np.array([0.15, 0.30, 0.12]) * dark * rng.uniform(0.9, 1.1)
        g2 = np.array([0.34, 0.52, 0.20]) * dark * rng.uniform(0.9, 1.1)
        c.poly(pts, g1)
        inner = [(cx + (p[0] - cx) * 0.80 - hw * 0.07, cy + (p[1] - cy) * 0.78 + hh * 0.10) for p in pts]
        c.poly(inner, g2)
        # nervaduras
        for a in np.linspace(0, 2 * np.pi, 15, endpoint=False):
            ex = cx + np.cos(a) * hw * 0.92
            ey = cy + np.sin(a) * hh * 0.92
            c.line((cx, cy), (ex, ey), g2 * 1.25, 0.0045)
    return _finish(c.rgb, c.a, ppm, "nalca", soft=0.6, seed=seed)


def colihue(seed, ppm=150):
    rng = np.random.default_rng(seed)
    H = rng.uniform(2.4, 4.2)
    c = Canvas(H * 1.0, H * 1.08 + 0.2, ppm)
    n = int(rng.integers(10, 22))
    canes = sorted([(rng.normal(0, 0.18), rng.uniform(0.6, 1.0) * H, rng.uniform(-1, 1), rng.uniform(0, 1)) for _ in range(n)], key=lambda s: s[3])
    for bx, ht, lean, depth in canes:
        dark = 0.55 + 0.45 * depth
        cane = np.array([0.40, 0.46, 0.20]) * dark
        leafc = np.array([0.26, 0.40, 0.16]) * dark
        leafl = np.array([0.46, 0.60, 0.28]) * dark
        m = 24
        x, y = bx, 0.0
        for i in range(m):
            f = i / m
            x2 = x + lean * 0.20 * (0.4 + f * 1.8) * ht / m * 3.0 * (f + 0.25)
            y2 = ht * (i + 1) / m * (1 - 0.18 * f * f)
            c.line((x, y), (x2, y2), cane * (1.0 - 0.15 * f), 0.011 * (1 - 0.6 * f))
            c.line((x - 0.003, y), (x2 - 0.003, y2), cane * 1.35, 0.004)
            if i % 3 == 0:
                c.line((x - 0.008, y), (x2 + 0.008, y), cane * 0.6, 0.0035)
            if f > 0.35 and i % 2 == 0:
                for side in (-1, 1):
                    ang = np.pi / 2 + side * rng.uniform(0.7, 1.5) - 0.35 * lean * side
                    ln = rng.uniform(0.10, 0.19) * (1.0 - 0.3 * f)
                    c.leaf(x2, y2, ang, ln, 0.012, leafl if np.cos(ang) < 0 else leafc)
            x, y = x2, y2
        c.leaf(x, y, np.pi / 2 + 0.2 * lean, 0.12, 0.010, leafl)
    return _finish(c.rgb, c.a, ppm, "colihue", soft=0.5, seed=seed)


def coihue_musgo(sp, seed):
    """Árbol oscuro de hojas chicas: reteñido de verde profundo y con musgo en el tronco."""
    sp = recolor(sp, (0.62, 0.86, 0.66), 0.30, (0.17, 0.30, 0.18))
    return mossify(sp, 0.9, seed, 0.9)


def library():
    from world import CACHE
    p = os.path.join(CACHE, "plants_andina1.pkl")
    if os.path.exists(p):
        return pickle.load(open(p, "rb"))
    base_tree = [glossopteris(300 + i) for i in range(8)]
    base_hi = [glossopteris(350 + i, ppm=130) for i in range(3)]
    lib = dict(
        nalca=[nalca(3000 + i) for i in range(8)],
        colihue=[colihue(3100 + i) for i in range(8)],
        tree_coihue=[coihue_musgo(s_, j) for j, s_ in enumerate(base_tree)],
        tree_coihue_hi=[coihue_musgo(s_, 20 + j) for j, s_ in enumerate(base_hi)],
        fern_verde=[recolor(fern(3200 + i), (0.95, 1.12, 0.92), 0.25, (0.20, 0.36, 0.18)) for i in range(10)],
        treefern_verde=[recolor(treefern(3300 + i), (0.95, 1.10, 0.92), 0.25, (0.20, 0.36, 0.18)) for i in range(6)],
        log_musgo=[mossify(log(3400 + i), 1.1, 40 + i, 0.9) for i in range(5)],
        rock_musgo=[mossify(rock(3500 + i), 1.1, 60 + i, 0.9) for i in range(6)],
        mossmat_verde=[recolor(mossmat(3600 + i), (0.95, 1.12, 0.90), 0.35, (0.20, 0.38, 0.16)) for i in range(8)],
        hongo=[hongo(3700 + i) for i in range(5)],
        tocon_musgo=[mossify(stump(3800 + i), 1.1, 80 + i, 0.9) for i in range(4)],
    )
    for k in lib:
        for sp in lib[k]:
            sp["rgb"] = (np.clip(sp["rgb"], 0, 1) * 255 + 0.5).astype(np.uint8) if sp["rgb"].dtype != np.uint8 else sp["rgb"]
            sp["a"] = (np.clip(sp["a"], 0, 1) * 255 + 0.5).astype(np.uint8) if sp["a"].dtype != np.uint8 else sp["a"]
    pickle.dump(lib, open(p, "wb"))
    return lib
