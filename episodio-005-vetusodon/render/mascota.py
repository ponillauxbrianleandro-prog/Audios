#!/usr/bin/env python3
"""Mascota del canal Río Puratense: un libro viviente extremadamente gordo, acostado, con 4 patas.  (v2: construcción 3D)

El libro es una malla 3D real (tamaño libro, ≈ 1 : 0,66 : 0,55) proyectada con perspectiva y sombreada como ilustración 2D:
  * cámara elevada en tres cuartos: se ve TODA la tapa superior (con la pata peluda), el canto de las hojas de frente (ojos)
    y el de la derecha, y un poco de la panza (tapa inferior abultada) con las patas; el lomo queda atrás, oculto.
  * bloque de páginas «almohadillado» (abultado en el medio) y tapas abombadas arriba y abajo: se nota que está lleno de hojas.
  * 4 patas negras tipo stickman (gorditas), 2 ojos tipo canica integrados en el canto de las hojas, sin cola.

  python3 mascota.py HOJA.png      hoja de poses
  draw(pose, size) -> imagen RGBA
"""
import math
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SS = 2
GRANATE = np.array([128, 38, 54.]); ORO = np.array([205, 176, 78.]); ORO_OSC = np.array([128, 100, 38.])
PAPEL = np.array([240, 226, 188.]); PAPEL2 = np.array([222, 205, 164.]); LINEA = (132, 108, 76)
NEGRO = (22, 18, 22); SOMBRA = np.array([52, 24, 60.])
LX, LY, LZ = -0.42, 0.78, 0.46                                   # luz (cámara: x der., y arriba, z hacia el espectador)
LL = math.sqrt(LX * LX + LY * LY + LZ * LZ)
LX, LY, LZ = LX / LL, LY / LL, LZ / LL

L_, D_, T_ = 1.0, 0.66, 0.55                                     # largo (canto frontal), ancho (lomo→canto), grosor de páginas
CT = 0.045                                                       # grosor de tapa
DOME_T, DOME_B = 0.12, 0.15                                    # abombado de las tapas (la inferior es la panza)
BF, BE = 0.13, 0.10                                             # abultado de las hojas: canto frontal / cantos de los extremos
OV = 0.03                                                        # tapas sobresalen del bloque


def Rx(a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a)); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def Ry(a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a)); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def Rz(a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a)); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def _shade(base, n, spec=0.0):
    d = max(0.0, n[0] * LX + n[1] * LY + n[2] * LZ)
    k = 0.50 + 0.62 * d
    c = base * k + SOMBRA * (1 - min(1, k)) * 0.35               # sombras hacia violeta, no hacia negro
    if spec:
        c = c + 255 * spec * max(0.0, d - 0.75) * 2.2
    return tuple(int(max(0, min(255, v))) for v in c)


class _Cam:
    def __init__(self, W, H, pitch, dist=3.1, f=1.0):
        self.W, self.H, self.pitch, self.dist = W, H, pitch, dist
        self.f = f * W * 1.18 * dist / 3.1
        self.R = Rx(pitch)                                       # mira hacia abajo `pitch` grados

    def cam(self, p):
        return self.R @ p

    def proj(self, pc):
        k = self.f * 1.0 / (self.dist - pc[2])
        return (self.W / 2 + pc[0] * k, self.H * 0.54 - pc[1] * k)

    def scale(self, pc):
        return self.f / (self.dist - pc[2])


def draw(pose=None, size=(640, 480)):
    """pose: turn (giro del cuerpo, ° ; 0 = de frente), pitch (elevación de cámara), lean (+ hocico abajo), roll (180 = patas arriba),
    bob (alto, unidades ≈ 1 = largo del libro), leg (fase 0..1 | None), spread, look (-1..1,-1..1), blink, mad 0..1, flutter 0..1,
    squash (1 = normal), dx/dy (desplazamiento en pantalla, px)."""
    p = dict(turn=-32, pitch=34, lean=0, roll=0, bob=0, leg=None, spread=0, look=(0, 0), blink=0, mad=0, flutter=0, squash=1.0,
             dx=0, dy=0, scale=1.0)
    p.update(pose or {})
    W, H = size[0] * SS, size[1] * SS
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cam = _Cam(W, H, p["pitch"], f=p["scale"])
    Rb = Ry(p["turn"]) @ Rz(p["roll"]) @ Rx(p["lean"])
    sq = p["squash"]
    off = np.array([0.0, p["bob"], 0.0])

    def B2C(q):                                                  # cuerpo -> cámara
        q = np.array(q, float); q = q * np.array([1, sq, 1])
        return cam.cam(Rb @ q + off)
    ctr = B2C((0, 0, 0))

    items = []                                                   # (profundidad, tipo, datos)

    def quad(a, b, c, d, base, spec=0.0, edge=None, line=None):
        P = [B2C(x) for x in (a, b, c, d)]
        n = np.cross(P[1] - P[0], P[3] - P[0]) + np.cross(P[2] - P[1], P[3] - P[1]) * 0
        m = sum(P) / 4
        nn = np.linalg.norm(n)
        if nn < 1e-12:
            return
        n = n / nn
        if np.dot(n, m - ctr) < 0:                               # normal hacia afuera del cuerpo
            n = -n
        if np.dot(n, np.array([0, 0, cam.dist]) - m) <= 0:       # cara de espaldas
            return
        col = _shade(base, n, spec)
        items.append((m[2], "q", ([cam.proj(x) for x in P], col, edge, line)))

    def grid(fn, nu, nv):
        return [[np.array(fn(i / nu, j / nv)) for j in range(nv + 1)] for i in range(nu + 1)]

    # ---------- bloque de hojas «almohadillado» (4 caras) ----------
    def bulge(u, v, B):
        return B * (math.sin(math.pi * u) ** 0.6) * (math.sin(math.pi * v) ** 0.7)

    def y_of(v):
        return -T_ / 2 + T_ * v

    sides = {
        "front": lambda u, v: ((u - 0.5) * L_, y_of(v), D_ / 2 + bulge(u, v, BF)),
        "right": lambda u, v: (L_ / 2 + bulge(u, v, BE), y_of(v), (0.5 - u) * D_),
        "left": lambda u, v: (-L_ / 2 - bulge(u, v, BE), y_of(v), (u - 0.5) * D_),
        "back": lambda u, v: ((0.5 - u) * L_, y_of(v), -D_ / 2 - bulge(u, v, 0.03)),
    }
    NV = 22
    for name, fn in sides.items():
        g = grid(fn, 22, NV)
        for i in range(22):
            for j in range(NV):
                v = (j + 0.5) / NV
                base = (PAPEL if j % 2 == 0 else PAPEL2) if name != "back" else GRANATE * 0.95
                ao = 0.55 + 0.45 * min(1, math.sin(math.pi * v) * 2.2)      # oclusión junto a las tapas
                quad(g[i][j], g[i + 1][j], g[i + 1][j + 1], g[i][j + 1], base * ao,
                     line=(LINEA if name != "back" else None) if j % 2 == 0 and name != "back" else None)

    # ---------- tapas abombadas ----------
    xo, zf, zb = L_ / 2 + OV, D_ / 2 + OV, -D_ / 2

    def cover(sign, dome, emblem):
        def surf(u, v):
            x = (u - 0.5) * 2 * xo; z = zb + v * (zf - zb)
            xn = x / xo; zn = (z - (zf + zb) / 2) / ((zf - zb) / 2)
            e = max(0.0, (1 - xn * xn)) * max(0.0, (1 - zn * zn))
            return (x, sign * (T_ / 2 + CT + dome * e ** 0.8), z)
        g = grid(surf, 24, 18)
        for i in range(24):
            for j in range(18):
                quad(g[i][j], g[i + 1][j], g[i + 1][j + 1], g[i][j + 1], GRANATE, spec=0.5)
        # cantos (grosor visible) alrededor
        def rim(a, b):
            quad(a, b, (b[0], sign * T_ / 2, b[2]), (a[0], sign * T_ / 2, a[2]), GRANATE * 0.78)
        for i in range(24):
            rim(g[i][18], g[i + 1][18]); rim(g[i + 1][0], g[i][0])
        for j in range(18):
            rim(g[0][j + 1], g[0][j]); rim(g[24][j], g[24][j + 1])
        # esquinas metálicas + pata peluda
        top_fn = lambda x, z: np.array(surf((x / xo + 1) / 2, (z - zb) / (zf - zb))) + np.array([0, sign * 0.006, 0])
        def decor(poly_xz, col, lift=0.006):
            pts3 = [np.array(surf((x / xo + 1) / 2, (z - zb) / (zf - zb))) + np.array([0, sign * lift, 0]) for x, z in poly_xz]
            P = [B2C(q) for q in pts3]
            m = sum(P) / len(P)
            nrm = np.cross(P[1] - P[0], P[2] - P[0])
            if np.linalg.norm(nrm) < 1e-12: return
            nrm = nrm / np.linalg.norm(nrm)
            if np.dot(nrm, m - ctr) < 0: nrm = -nrm
            if np.dot(nrm, np.array([0, 0, cam.dist]) - m) <= 0: return
            items.append((m[2] + 1e-4, "q", ([cam.proj(x) for x in P], _shade(col, nrm, 0.6), None, None)))
        k = 0.17
        for sx, sz in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            cx, cz = sx * xo, (zf if sz > 0 else zb)
            decor([(cx, cz), (cx - sx * k, cz), (cx, cz - sz * k * 0.8)], ORO)
        if emblem:
            def ell(cx, cz, rx, rz, n=18):
                return [(cx + rx * math.cos(2 * math.pi * t / n), cz + rz * math.sin(2 * math.pi * t / n)) for t in range(n)]
            c0 = (0.0, 0.02)
            decor(ell(c0[0], c0[1] + 0.045, 0.115, 0.082), ORO)                 # almohadilla
            for tx, tz, r in ((-0.17, -0.02, 0.05), (-0.058, -0.095, 0.052), (0.058, -0.095, 0.052), (0.17, -0.02, 0.05)):
                decor(ell(c0[0] + tx, c0[1] + tz, r, r * 0.95, 12), ORO)       # deditos
            decor(ell(c0[0], c0[1] + 0.06, 0.06, 0.04, 12), ORO_OSC, 0.009)    # brillo interno

    cover(+1, DOME_T, True)
    cover(-1, DOME_B, False)

    # ---------- patas (4, stickman gorditas, bajo la panza) ----------
    ground = []
    legs = []
    for k, (lx, lz, ph) in enumerate(((-0.36, 0.2, 0.0), (0.36, 0.2, 0.5), (-0.36, -0.2, 0.5), (0.36, -0.2, 0.0))):
        xn, zn = lx / xo, (lz - (zf + zb) / 2) / ((zf - zb) / 2)
        e = max(0.0, 1 - xn * xn) * max(0.0, 1 - zn * zn)
        hip = np.array([lx * 1.05, -(T_ / 2 + CT + DOME_B * e ** 0.8) + 0.02, lz])
        sw = lift = 0.0
        if p["leg"] is not None:
            s = math.sin((p["leg"] + ph) * 2 * math.pi)
            sw, lift = 0.10 * s, 0.07 * max(0.0, math.cos((p["leg"] + ph) * 2 * math.pi) * -1 + 0)
            lift = 0.07 * max(0.0, math.sin((p["leg"] + ph) * 2 * math.pi + math.pi / 2))
        sp = p["spread"] * 0.14 * (1 if lx > 0 else -1)
        knee = hip + np.array([lx * 0.18 + sp * 0.5, -0.12, sw * 0.5 + 0.04])
        foot = hip + np.array([lx * 0.12 + sp, -0.25 + lift, sw])
        legs.append((hip, knee, foot, lz < 0))

    # sombra en el suelo (plano horizontal del mundo bajo el punto más bajo)
    wp = lambda q: Rb @ (np.array(q, float) * np.array([1, sq, 1])) + off
    feet_w = [wp(f_) for _, _, f_, _ in legs]
    gy = min(q[1] for q in feet_w + [wp((0, -T_ / 2 - CT - DOME_B, 0))]) - 0.015
    cxw = sum(q[0] for q in feet_w) / 4; czw = sum(q[2] for q in feet_w) / 4
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pts = [cam.proj(cam.cam(np.array([cxw + 0.72 * math.cos(t), gy, czw + 0.5 * math.sin(t)]))) for t in np.linspace(0, 2 * math.pi, 40)]
    ImageDraw.Draw(sh).polygon(pts, fill=(10, 4, 20, 120))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10 * SS)))

    for hip, knee, foot, back in legs:
        a, b, c = B2C(hip), B2C(knee), B2C(foot)
        dep = (a[2] + c[2]) / 2 - (0.4 if back else -0.05)
        items.append((dep - 0.5 if back else dep - 0.12, "leg", (a, b, c, back)))

    items.sort(key=lambda t: t[0])
    d = ImageDraw.Draw(img)
    for dep, kind, data in items:
        if kind == "q":
            poly, col, edge, line = data
            d.polygon(poly, fill=col)
            if line:
                d.line([poly[3], poly[2]], fill=line, width=max(1, SS))
        else:
            a, b, c, back = data
            col = (52, 44, 54) if back else NEGRO
            wd = max(2, int(0.125 * cam.scale(b) * (0.8 if back else 1.0)))
            pa, pb, pc = cam.proj(a), cam.proj(b), cam.proj(c)
            d.line([pa, pb, pc], fill=col, width=wd, joint="curve")
            r = wd * 0.5
            for q in (pa, pb, pc):
                d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=col)
            fw = wd * 0.8
            d.ellipse([pc[0] - fw, pc[1] - fw * 0.55, pc[0] + fw, pc[1] + fw * 0.55], fill=col)   # pie redondo
            if not back:
                d.line([(pa[0] - wd * 0.15, pa[1]), (pb[0] - wd * 0.15, pb[1])], fill=(70, 62, 74), width=max(1, wd // 5))

    # ---------- ojos (canicas en el canto frontal de las hojas) ----------
    fc = B2C((0, 0, D_ / 2 + BF))
    nrm = Rb @ np.array([0, 0, 1.0]); nrm = cam.R @ nrm
    if nrm[2] > 0.05:
        lx_, ly_ = p["look"]
        eyes = []
        for ex in (-0.20, 0.14):
            q = (ex * L_, 0.02, D_ / 2 + bulge(ex + 0.5, 0.5, BF) + 0.004)
            c = B2C(q); eyes.append((cam.proj(c), cam.scale(c)))
        r0 = 0.058
        d = ImageDraw.Draw(img)
        for (sx, sy), k in eyes:
            r = r0 * k
            soc = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(soc).ellipse([sx - r * 1.45, sy - r * 1.2, sx + r * 1.45, sy + r * 1.55], fill=(110, 74, 40, 120))
            img.alpha_composite(soc.filter(ImageFilter.GaussianBlur(3 * SS)))
            d = ImageDraw.Draw(img)
            ry = r * (1 - 0.92 * p["blink"])
            d.ellipse([sx - r, sy - ry, sx + r, sy + ry], fill=NEGRO)
            if p["blink"] < 0.6:
                hx, hy = sx + lx_ * r * 0.2 - r * 0.34, sy + ly_ * r * 0.18 - ry * 0.4
                d.ellipse([hx - r * 0.27, hy - r * 0.27, hx + r * 0.27, hy + r * 0.27], fill=(255, 255, 255))
                d.ellipse([sx + r * 0.25, sy + ry * 0.35, sx + r * 0.6, sy + ry * 0.7], fill=(70, 66, 90))
        if p["mad"] > 0:                                          # ceño
            (xa, ya), ka = min(eyes, key=lambda e: e[0][0]); (xb, yb), kb = max(eyes, key=lambda e: e[0][0])
            r = r0 * ka
            d.line([(xa - r * 1.4, ya - r * 2.0), (xa + r * 1.3, ya - r * 1.05)], fill=NEGRO, width=int(r * 0.5))
            d.line([(xb + r * 1.4, yb - r * 2.0), (xb - r * 1.3, yb - r * 1.05)], fill=NEGRO, width=int(r * 0.5))

    img = img.resize(size, Image.LANCZOS)
    if p["dx"] or p["dy"]:
        out = Image.new("RGBA", size, (0, 0, 0, 0)); out.alpha_composite(img, (int(p["dx"]), int(p["dy"]))) if p["dx"] >= 0 and p["dy"] >= 0 else out.paste(img, (int(p["dx"]), int(p["dy"])))
        img = out
    return img


POSES = [
    ("sentado mirando", dict(lean=-9, look=(0.7, 0.3))),
    ("olfatea", dict(lean=10, look=(0.8, 0.9), turn=-44)),
    ("camina A", dict(leg=0.0, bob=0.0, turn=-55)),
    ("camina B", dict(leg=0.5, bob=0.02, turn=-55)),
    ("salta", dict(lean=-16, bob=0.35, spread=1.0, look=(0, -1), turn=-25)),
    ("de espaldas", dict(roll=180, spread=1.0, blink=0.7, bob=0.0, pitch=30)),
    ("enojado", dict(mad=1, lean=5, turn=-20)),
    ("parpadea", dict(blink=1, lean=-4, turn=-36)),
]


def sheet(path):
    cols = 4
    cw, ch = 560, 440
    S = Image.new("RGB", (cols * cw, 2 * ch), (64, 90, 74))
    for i, (n, pz) in enumerate(POSES):
        im = draw(pz, (cw, ch))
        S.paste(im, ((i % cols) * cw, (i // cols) * ch), im)
        ImageDraw.Draw(S).text(((i % cols) * cw + 10, (i // cols) * ch + 8), n, fill=(255, 255, 255))
    S.save(path)


if __name__ == "__main__":
    sheet(sys.argv[1] if len(sys.argv) > 1 else "mascota_hoja.png")
