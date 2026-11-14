#!/usr/bin/env python3
"""Pintor por código: repinta una imagen base con miles de pinceladas.

Cada pincelada sigue el contorno de la forma, toma el color de la base con una variación
propia y se dibuja como un haz de cerdas (deja marca). Al final se agrega relieve de
pintura y textura de lienzo. Con la misma semilla, la misma base da las mismas pinceladas.

Uso: pintor.py base.png salida.jpg [--sizes 44,22,11,6,3] [--sat 0.9] [--dark 0.0]
                                   [--mask detalle.png] [--seed 7] [--relief 0.5]
"""
import argparse
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def blur(img, r):
    return img.filter(ImageFilter.GaussianBlur(r)) if r > 0 else img


def paint(src, sizes, seed=7, mask=None, relief=0.5, under=0.35, thr=(0, 36, 36, 40, 46, 50), jitter=0.07):
    rnd = random.Random(seed)
    W, H = src.size
    # imprimación: versión borrosa y oscura de la base (no quedan huecos)
    base = np.asarray(blur(src, 26), dtype=np.float32)
    tone = np.array([38, 30, 34], dtype=np.float32)
    canvas = Image.fromarray(np.clip(base * (1 - under) + tone * under, 0, 255).astype(np.uint8))
    height = Image.new('L', (W, H), 110)
    mk = np.asarray(mask.convert('L').resize((W, H)), dtype=np.float32) / 255 if mask is not None else None

    for li, R in enumerate(sizes):
        ref_img = blur(src, R * 0.45)
        ref = np.asarray(ref_img, dtype=np.float32)
        lum = np.asarray(blur(src, max(1.5, R * 0.7)).convert('L'), dtype=np.float32)
        gy, gx = np.gradient(lum)
        cur = np.asarray(canvas, dtype=np.float32)
        err = np.abs(cur - ref).sum(axis=2)
        t = thr[min(li, len(thr) - 1)]
        g = max(2, int(R * 0.85))
        pts = []
        for y0 in range(0, H, g):
            for x0 in range(0, W, g):
                x = min(W - 1, x0 + rnd.randrange(g)); y = min(H - 1, y0 + rnd.randrange(g))
                e = err[y, x]
                tt = t
                if mk is not None and R <= 6:
                    tt = t * (1.6 - 1.2 * mk[y, x])  # más detalle donde la máscara es clara
                if li == 0 or e > tt:
                    pts.append((x, y))
        rnd.shuffle(pts)
        dc = ImageDraw.Draw(canvas, 'RGBA')
        dh = ImageDraw.Draw(height)
        nb = int(max(3, min(11, R * 0.8)))
        bw = max(1, int(round(2 * R / nb * 1.25)))
        for (x, y) in pts:
            col = ref[y, x]
            v = 1 + (rnd.random() - 0.5) * 2 * jitter
            tint = [(rnd.random() - 0.5) * 14 for _ in range(3)]
            col = np.clip(col * v + tint, 0, 255)
            ang = math.atan2(gy[y, x], gx[y, x]) + math.pi / 2
            if abs(gx[y, x]) + abs(gy[y, x]) < 0.6:
                ang = -0.5 + (rnd.random() - 0.5) * 1.2  # zonas lisas: dirección de mano
            L = R * (1.6 + rnd.random() * 2.4)
            # trayecto curvo que sigue el contorno y frena en los bordes
            path = [(x, y)]
            for sgn in (1, -1):
                px, py, a = float(x), float(y), ang
                seg = []
                for _ in range(3):
                    nx, ny = px + math.cos(a) * L / 6 * sgn, py + math.sin(a) * L / 6 * sgn
                    ix, iy = int(nx), int(ny)
                    if ix < 0 or iy < 0 or ix >= W or iy >= H:
                        break
                    if np.abs(ref[iy, ix] - ref[y, x]).sum() > 70:
                        break
                    na = math.atan2(gy[iy, ix], gx[iy, ix]) + math.pi / 2
                    if math.cos(na - a) < 0:
                        na += math.pi
                    a = a * 0.5 + na * 0.5 if abs(gx[iy, ix]) + abs(gy[iy, ix]) > 0.6 else a
                    px, py = nx, ny
                    seg.append((px, py))
                path = (seg[::-1] + path) if sgn < 0 else (path + seg)
            if len(path) < 2:
                path.append((x + math.cos(ang) * R * 0.6, y + math.sin(ang) * R * 0.6))
            nxp, nyp = -math.sin(ang), math.cos(ang)
            for b in range(nb):
                if rnd.random() < 0.1:
                    continue  # pincel seco: se ve lo de abajo
                o = (b / (nb - 1) - 0.5) * 2 * R * 0.9
                bv = 1 + (rnd.random() - 0.5) * 0.16
                c = tuple(int(max(0, min(255, k * bv))) for k in col) + (rnd.randrange(190, 256),)
                cut0, cut1 = rnd.random() * 0.18, rnd.random() * 0.18
                pp = [(px + nxp * o, py + nyp * o) for (px, py) in path]
                if len(pp) > 2:
                    a0, a1 = pp[0], pp[1]; pp[0] = (a0[0] + (a1[0] - a0[0]) * cut0 * 3, a0[1] + (a1[1] - a0[1]) * cut0 * 3)
                    z0, z1 = pp[-1], pp[-2]; pp[-1] = (z0[0] + (z1[0] - z0[0]) * cut1 * 3, z0[1] + (z1[1] - z0[1]) * cut1 * 3)
                dc.line(pp, fill=c, width=bw, joint='curve')
                dh.line(pp, fill=rnd.randrange(60, 230), width=bw)
        del dc, dh

    out = np.asarray(canvas, dtype=np.float32)
    if relief > 0:
        hm = np.asarray(blur(height, 0.8), dtype=np.float32)
        hy, hx = np.gradient(hm)
        rel = (-hx * 0.6 - hy * 0.8) / 255.0 * 0.5
        out = out * (1 + np.clip(rel, -0.5, 0.5)[..., None] * relief * 2.2)
        # trama de lienzo
        rs = np.random.RandomState(seed)
        weave = (np.sin(np.arange(W)[None, :] * 1.9) + np.sin(np.arange(H)[:, None] * 1.9)) * 0.012 + rs.normal(0, 0.012, (H, W))
        out = out * (1 + weave[..., None] * relief * 2)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def grade(img, sat=0.9, dark=0.0, contrast=1.08, vignette=0.28):
    a = np.asarray(img, dtype=np.float32) / 255
    g = a.mean(axis=2, keepdims=True)
    a = g + (a - g) * sat
    a = (a - 0.5) * contrast + 0.5 - dark
    H, W = a.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    a = a * (1 - vignette * np.clip(d - 0.55, 0, 1)[..., None] ** 1.5 * 1.6)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('dst')
    ap.add_argument('--sizes', default='44,22,11,6,3')
    ap.add_argument('--sat', type=float, default=0.9)
    ap.add_argument('--dark', type=float, default=0.0)
    ap.add_argument('--contrast', type=float, default=1.08)
    ap.add_argument('--vignette', type=float, default=0.28)
    ap.add_argument('--relief', type=float, default=0.5)
    ap.add_argument('--mask', default=None)
    ap.add_argument('--seed', type=int, default=7)
    ap.add_argument('--crop', default=None, help='x,y,w,h antes de pintar')
    ap.add_argument('--scale', type=float, default=1.0)
    a = ap.parse_args()
    im = Image.open(a.src).convert('RGB')
    if a.crop:
        x, y, w, h = [int(v) for v in a.crop.split(',')]
        im = im.crop((x, y, x + w, y + h))
    if a.scale != 1.0:
        im = im.resize((int(im.width * a.scale), int(im.height * a.scale)), Image.LANCZOS)
    mk = Image.open(a.mask) if a.mask else None
    if mk is not None and a.crop:
        x, y, w, h = [int(v) for v in a.crop.split(',')]
        mk = mk.crop((x, y, x + w, y + h))
    out = paint(im, [int(s) for s in a.sizes.split(',')], seed=a.seed, mask=mk, relief=a.relief)
    out = grade(out, a.sat, a.dark, a.contrast, a.vignette)
    out.save(a.dst, quality=93)
    print('ok', a.dst, out.size)
