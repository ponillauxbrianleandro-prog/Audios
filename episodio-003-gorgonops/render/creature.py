"""Animales como sprites de relieve (2.5D): sin polígonos.

El cuerpo se describe con cadenas de esferas a lo largo de un esqueleto animado
(columna, cráneo, mandíbula, cuatro patas con cinemática inversa, cola). Cada cuadro se
proyecta a un mapa de profundidad 2D, del que salen las normales, la luz y la piel.

Anatomía de Gorgonops torvus: cráneo ~30 cm alto y estrecho, sínfisis mandibular profunda,
caninos de sable, ojo pequeño, tronco en barril, patas delanteras semiextendidas,
traseras más erguidas, pies semiplantígrados, cola corta. Piel desnuda: no hay evidencia
de pelo en gorgonópsidos.
"""
import numpy as np
import cv2
from scipy.ndimage import map_coordinates
from util import smoothstep, lerp
import world

SKIN, TOOTH, EYE, DARK, CLAW, MOUTH = 0, 1, 2, 3, 4, 5

_NOISE = None


def noise3():
    global _NOISE
    if _NOISE is None:
        n = 64
        rng = np.random.default_rng(7)
        f = np.fft.fftfreq(n) * n
        fx, fy, fz = np.meshgrid(f, f, f, indexing="ij")
        k = np.sqrt(fx * fx + fy * fy + fz * fz)
        k[0, 0, 0] = 1
        spec = (k ** -1.6) * np.exp(1j * rng.uniform(0, 2 * np.pi, k.shape))
        spec[0, 0, 0] = 0
        v = np.real(np.fft.ifftn(spec))
        lo, hi = np.percentile(v, [1, 99])
        _NOISE = np.clip((v - lo) / (hi - lo), 0, 1).astype(np.float32)
    return _NOISE


def n3(p, freq):
    q = (p * freq * 64.0).T
    return map_coordinates(noise3(), q, order=1, mode="wrap")


GORGONOPS = dict(
    scale=1.0, speed=0.55, period=1.28, canine=True, tail=1.0,
    dorsal=(0.27, 0.235, 0.195), flank=(0.52, 0.455, 0.375), ventral=(0.80, 0.75, 0.65),
    bars=0.07, sheen=0.11, leg=1.0, head=1.15, girth=1.0, sprawl=1.0,
)
# Procynosuchus: cinodonte basal de ~60 cm, cuerpo largo, patas cortas, cola larga.
PROCYNOSUCHUS = dict(
    scale=0.40, speed=0.42, period=0.62, canine=False, tail=1.55,
    dorsal=(0.30, 0.24, 0.18), flank=(0.43, 0.35, 0.26), ventral=(0.68, 0.61, 0.50),
    bars=0.05, sheen=0.05, leg=0.70, head=0.80, girth=0.86, sprawl=1.25, low=0.10,
)


# Diictodon: dicinodonte excavador de ~45 cm, pico córneo y dos colmillos pequeños.
DIICTODON = dict(
    scale=0.30, speed=0.30, period=0.55, canine=True, tail=0.45, noincisors=True,
    dorsal=(0.33, 0.27, 0.20), flank=(0.50, 0.42, 0.32), ventral=(0.74, 0.68, 0.58),
    bars=0.03, sheen=0.05, leg=0.62, head=1.2, girth=1.12, sprawl=1.3, low=0.12, snout=0.62,
)
# Pareiasaurio: herbívoro acorazado de ~2,5 m.
PAREIASAUR = dict(
    scale=1.45, speed=0.35, period=2.0, canine=False, tail=0.6,
    dorsal=(0.30, 0.28, 0.25), flank=(0.47, 0.44, 0.39), ventral=(0.66, 0.63, 0.57),
    bars=0.02, sheen=0.04, leg=0.85, head=0.72, girth=1.32, sprawl=1.35, low=0.06, snout=0.7, rough=3.0,
)
# Thrinaxodon: cinodonte del Triásico temprano, del tamaño de un gato.
THRINAXODON = dict(
    scale=0.30, speed=0.40, period=0.55, canine=False, tail=1.15,
    dorsal=(0.33, 0.28, 0.23), flank=(0.47, 0.40, 0.32), ventral=(0.70, 0.64, 0.55),
    bars=0.04, sheen=0.05, leg=0.70, head=0.85, girth=0.88, sprawl=1.2, low=0.10,
)
# Anfibio temnospóndilo de orilla.
ANFIBIO = dict(
    scale=0.55, speed=0.2, period=1.4, canine=False, tail=1.4,
    dorsal=(0.17, 0.18, 0.14), flank=(0.31, 0.31, 0.24), ventral=(0.62, 0.61, 0.52),
    bars=0.10, sheen=0.30, leg=0.50, head=1.1, girth=0.80, sprawl=1.7, low=0.17,
)


class Builder:
    def __init__(self):
        self.c, self.r, self.rest, self.cid = [], [], [], []

    def chain(self, pts, rad, rest=None, cid=SKIN, k=0.42):
        pts = np.asarray(pts, np.float64)
        rad = np.asarray(rad, np.float64)
        rest = pts if rest is None else np.asarray(rest, np.float64)
        for i in range(len(pts) - 1):
            L = np.linalg.norm(pts[i + 1] - pts[i])
            n = max(1, int(np.ceil(L / (k * max(1e-4, min(rad[i], rad[i + 1]))))))
            t = np.linspace(0, 1, n, endpoint=False)[:, None]
            self.c.append(pts[i] + (pts[i + 1] - pts[i]) * t)
            self.rest.append(rest[i] + (rest[i + 1] - rest[i]) * t)
            self.r.append(rad[i] + (rad[i + 1] - rad[i]) * t[:, 0])
            self.cid.append(np.full(n, cid))
        self.ball(pts[-1], rad[-1], rest[-1], cid)

    def ball(self, p, r, rest=None, cid=SKIN):
        self.c.append(np.asarray(p, np.float64)[None])
        self.rest.append(np.asarray(p if rest is None else rest, np.float64)[None])
        self.r.append(np.array([r], np.float64))
        self.cid.append(np.array([cid]))

    def done(self):
        return (np.vstack(self.c), np.concatenate(self.r), np.vstack(self.rest), np.concatenate(self.cid))


def _ik(J, T, l1, l2, pole):
    d = T - J
    L = np.linalg.norm(d)
    L = min(L, (l1 + l2) * 0.985)
    u = d / (np.linalg.norm(d) + 1e-9)
    a = (l1 * l1 - l2 * l2 + L * L) / (2 * L)
    h = np.sqrt(max(l1 * l1 - a * a, 1e-8))
    p = pole - u * np.dot(pole, u)
    p /= np.linalg.norm(p) + 1e-9
    return J + u * a + p * h, J + u * L


# puntos de la columna en reposo: (x, y, radio)
_SPINE = np.array([
    (-0.86, 0.15, 0.012), (-0.74, 0.20, 0.030), (-0.62, 0.275, 0.052), (-0.50, 0.36, 0.082),
    (-0.40, 0.42, 0.118), (-0.22, 0.43, 0.150), (0.00, 0.42, 0.165), (0.20, 0.425, 0.172),
    (0.34, 0.445, 0.160), (0.44, 0.46, 0.135),
])
XH, XS = -0.38, 0.34
LEGS = [("LH", -1, 0.00, False), ("LF", -1, 0.25, True), ("RH", 1, 0.50, False), ("RF", 1, 0.75, True)]
STAND = dict(LH=-0.05, LF=0.07, RH=0.06, RF=-0.06)


def build(spec, phase=0.0, walk=1.0, t=0.0, head_pitch=0.0, head_yaw=0.0, head_dx=0.0, head_dy=0.0,
          drop=0.0, gape=0.0, tail_amp=1.0, crouch=0.0, curl=0.0, bob=1.0):
    """Devuelve esferas en el sistema del animal (x adelante, y arriba, z derecha)."""
    b = Builder()
    tw = 2 * np.pi * phase
    sp = _SPINE.copy()
    tl = spec["tail"]
    sp[:4, 0] = XH - 0.02 + (sp[:4, 0] - (XH - 0.02)) * tl
    g = spec["girth"]
    rest = np.stack([sp[:, 0], sp[:, 1], np.zeros(len(sp))], 1)

    def zoff(x):
        f = (x - XH) / (XS - XH)
        trunk = 0.022 * np.cos(np.pi * np.clip(f, -0.3, 1.3)) * np.sin(tw) * walk * spec["sprawl"]
        tf = np.clip((XH - x) / (0.62 * tl), 0, 1)
        tail = (0.10 * tf ** 1.4) * (np.sin(tw - 2.4 * tf + 0.6) * walk + 0.55 * np.sin(t * 0.9 - 2.0 * tf) * (1 - 0.6 * walk)) * tail_amp
        return trunk + tail + curl * 0.9 * (x - 0.0) ** 2 * np.sign(x)

    def yoff(x):
        f = np.clip((x - XH) / (XS - XH), -0.2, 1.4)
        return 0.006 * bob * np.sin(2 * tw + 0.5) * walk - drop * f - spec.get("low", 0.0) - 0.235 * crouch

    breath = 1 + 0.014 * np.sin(2 * np.pi * t / 3.4)
    pts = rest.copy()
    pts[:, 2] = zoff(pts[:, 0])
    pts[:, 1] += yoff(pts[:, 0])
    rad = sp[:, 2] * g
    rad[4:9] *= breath
    # columna suavizada
    from util import catmull
    n = 40
    P = catmull(np.column_stack([pts, rad, rest]), n)
    b.chain(P[:, :3], P[:, 3], P[:, 4:7])
    # vientre/pecho: da profundidad al tórax
    bel = [(-0.20, 0.36, 0.125), (0.02, 0.335, 0.150), (0.22, 0.33, 0.150), (0.36, 0.36, 0.120)]
    bp = np.array([(x, y + yoff(x), zoff(x)) for x, y, r in bel])
    b.chain(bp, np.array([r for *_, r in bel]) * g * breath, np.array([(x, y, 0) for x, y, r in bel]))

    # --- cuello y cabeza
    hs = spec["head"]
    sh = np.array([0.44, 0.46 + yoff(0.44), zoff(0.44)])
    H0 = np.array([0.60 + head_dx, 0.49 + yoff(0.44) * 0.6 + head_dy, zoff(0.44) * 0.5 + 0.12 * np.sin(head_yaw)])
    mid = (sh + H0) / 2 + np.array([0, 0.012 - 0.15 * min(head_dy, 0) * 0.3, 0])
    neck = catmull(np.array([sh, mid, H0]), 8)
    b.chain(neck, np.linspace(0.135 * g, 0.088 * hs, 8), catmull(np.array([[0.44, 0.46, 0], [0.52, 0.48, 0], [0.60, 0.49, 0]]), 8))
    cp, sp_ = np.cos(head_pitch), np.sin(head_pitch)
    cy, sy = np.cos(head_yaw), np.sin(head_yaw)

    def hd(p, jaw=False):
        p = np.atleast_2d(np.asarray(p, np.float64)).copy()
        p[:, 0] = np.where(p[:, 0] > 0.08, 0.08 + (p[:, 0] - 0.08) * spec.get('snout', 1.0), p[:, 0])
        p = p * hs
        if jaw and gape:
            jx, jy = 0.015 * hs, -0.062 * hs
            cg, sg = np.cos(gape), np.sin(gape)
            x, y = p[:, 0] - jx, p[:, 1] - jy
            p = np.column_stack([jx + x * cg + y * sg, jy - x * sg + y * cg, p[:, 2]])
        x = p[:, 0] * cp + p[:, 1] * sp_
        y = -p[:, 0] * sp_ + p[:, 1] * cp
        z = p[:, 2]
        return np.column_stack([x * cy - z * sy, y, x * sy + z * cy]) + H0

    def hrest(p):
        return np.atleast_2d(np.asarray(p, np.float64)) * hs + np.array([0.60, 0.49, 0])

    def hchain(p, r, cid=SKIN, jaw=False, k=0.42):
        b.chain(hd(p, jaw), np.asarray(r) * hs, hrest(p), cid, k)

    # bóveda craneal y hocico alto y estrecho
    hchain([(0.00, 0.000, 0), (0.08, 0.010, 0), (0.16, 0.004, 0), (0.24, -0.004, 0), (0.295, -0.014, 0)],
           [0.085, 0.076, 0.062, 0.052, 0.042])
    hchain([(0.05, -0.030, 0), (0.16, -0.036, 0), (0.265, -0.040, 0)], [0.072, 0.058, 0.044])
    for s in (-1, 1):
        hchain([(0.005, -0.012, s * 0.048), (0.075, -0.024, s * 0.050), (0.13, -0.034, s * 0.034)], [0.058, 0.047, 0.042])
        hchain([(0.10, -0.045, s * 0.024), (0.20, -0.052, s * 0.022), (0.285, -0.050, s * 0.015)], [0.046, 0.042, 0.034])
        hchain([(0.07, -0.018, s * 0.030), (0.18, -0.026, s * 0.026), (0.27, -0.032, s * 0.017)], [0.062, 0.050, 0.039])
        hchain([(0.060, 0.048, s * 0.044), (0.105, 0.044, s * 0.038)], [0.019, 0.015])
        b.ball(hd((0.086, 0.026, s * 0.064))[0], 0.0125 * hs, hrest((0.086, 0.026, s * 0.064))[0], EYE)
        b.ball(hd((0.303, -0.006, s * 0.020))[0], 0.0070 * hs, hrest((0.303, -0.006, s * 0.020))[0], DARK)
        hchain([(0.015, -0.070, s * 0.046), (0.11, -0.096, s * 0.034), (0.21, -0.106, s * 0.020), (0.265, -0.110, s * 0.010)],
               [0.027, 0.028, 0.028, 0.030], jaw=True)
        if spec["canine"]:
            hchain([(0.232, -0.072, s * 0.040), (0.236, -0.105, s * 0.040), (0.242, -0.143, s * 0.038)],
                   [0.0105, 0.0078, 0.0025], TOOTH, k=0.3)
            for ix in (() if spec.get('noincisors') else (0.262, 0.277, 0.290)):
                hchain([(ix, -0.074, s * 0.021), (ix + 0.002, -0.094, s * 0.020)], [0.0055, 0.002], TOOTH, k=0.3)
    hchain([(0.256, -0.130, 0), (0.270, -0.116, 0)], [0.026, 0.030], jaw=True)

    if gape > 0.12:      # interior de la boca y dientes inferiores, visibles al abrir
        hchain([(0.05, -0.050, 0), (0.15, -0.058, 0), (0.25, -0.062, 0)], [0.036, 0.032, 0.024], MOUTH)
        hchain([(0.04, -0.078, 0), (0.14, -0.094, 0), (0.235, -0.100, 0)], [0.030, 0.027, 0.020], MOUTH, jaw=True)
        for s in (-1, 1):
            for ix in (0.125, 0.150, 0.175):
                hchain([(ix, -0.078, s * 0.030), (ix, -0.064, s * 0.030)], [0.0045, 0.0018], TOOTH, jaw=True, k=0.3)
                hchain([(ix, -0.072, s * 0.036), (ix, -0.086, s * 0.036)], [0.0045, 0.0018], TOOTH, k=0.3)
            if spec["canine"] and not spec.get('noincisors'):
                hchain([(0.212, -0.088, s * 0.026), (0.214, -0.058, s * 0.027)], [0.007, 0.002], TOOTH, jaw=True, k=0.3)
                for ix in (0.240, 0.252, 0.263):
                    hchain([(ix, -0.094, s * 0.014), (ix, -0.078, s * 0.014)], [0.0045, 0.0018], TOOTH, jaw=True, k=0.3)

    # --- patas
    lg = spec["leg"]
    spw = spec["sprawl"]
    beta = 0.68
    Lst = spec["speed"] / spec["scale"] * beta * spec["period"]
    contacts = []
    for name, side, off, fore in LEGS:
        if fore:
            J = np.array([XS + 0.02, 0.33, side * 0.125])
            x0, zf, l1, l2 = 0.40, side * 0.205 * spw, 0.215 * lg, 0.195 * lg
            pole = np.array([-0.75, 0.25, side * 0.75 * spw])
            r = [0.078, 0.062, 0.058, 0.046, 0.040]
        else:
            J = np.array([XH, 0.35, side * 0.115])
            x0, zf, l1, l2 = -0.40, side * 0.175 * spw, 0.245 * lg, 0.215 * lg
            pole = np.array([0.85, 0.15, side * 0.50 * spw])
            r = [0.098, 0.078, 0.066, 0.050, 0.042]
        Jr = J.copy()
        J = J + np.array([0, yoff(J[0]), zoff(J[0])])
        p = (phase + off) % 1.0
        if p < beta:
            s = p / beta
            fx = x0 + Lst / 2 - Lst * s
            heel = 0.055 * smoothstep(0.72, 1.0, s)
            ay, ty = 0.05 + heel, 0.0
        else:
            s = (p - beta) / (1 - beta)
            e = s * s * (3 - 2 * s)
            fx = x0 - Lst / 2 + Lst * e
            lift = 0.065 * np.sin(np.pi * s)
            ay = 0.05 + lift + 0.055 * (1 - s) ** 2
            ty = lift * 0.75 + 0.012 * np.sin(np.pi * s)
        fxs = x0 + STAND[name] * 0.8
        fx = lerp(fxs, fx, walk)
        ay = lerp(0.05, ay, walk)
        ty = ty * walk
        A = np.array([fx, ay * lg, zf])
        K, A = _ik(J, A, l1, l2, pole)
        Ar = np.array([x0, 0.05, zf])
        Kr = (Jr + Ar) / 2 + pole * 0.06
        M1, M2 = J + (K - J) * 0.5, K + (A - K) * 0.28
        b.chain([J, M1, K, M2, A], [r[0] * g, r[0] * 0.80 * g, r[2] * 0.86, r[2] * 1.02, r[3] * 0.80],
                [Jr, (Jr + Kr) / 2, Kr, Kr + (Ar - Kr) * 0.28, Ar])
        b.ball(J + np.array([0, 0.02, -side * 0.035]), r[0] * 1.0 * g, Jr)
        # pie semiplantígrado, cinco dedos con garra
        T = np.array([A[0] + 0.068, ty + 0.028, zf + side * 0.008])
        b.chain([A, T], [r[4], 0.036], [Ar, Ar + [0.075, -0.03, 0]])
        for j in range(5):
            a = side * (-0.50 + 0.30 * j)
            ln = 0.046 + 0.010 * np.sin(np.pi * (j + 0.5) / 5)
            d = np.array([np.cos(a), 0, np.sin(a)])
            t0 = T + d * 0.012
            t1 = T + d * ln + np.array([0, -0.008, 0])
            t1[1] = max(t1[1], ty + 0.013)
            b.chain([t0, t1], [0.018, 0.0125], [Ar + [0.08, 0, 0], Ar + [0.13, 0, 0]], k=0.5)
            b.chain([t1, t1 + d * 0.022 + np.array([0, -0.006, 0])], [0.006, 0.002], None, CLAW, k=0.4)
        contacts.append((T[0], T[2], ty))
    c, r, rest_, cid = b.done()
    s = spec["scale"]
    return c * s, r * s, rest_, cid


def render(spec, cam, pos, heading, pose, ss=1.6, fogk=1.0):
    """Sprite del animal. Devuelve dict(rgb premult, a, x0, y0, zc, shadow_pts)."""
    c, r, rest, cid = build(spec, **pose)
    ch, shh = np.cos(heading), np.sin(heading)
    # animal -> mundo (x adelante gira hacia 'heading' medido desde +X hacia +Z)
    Wd = np.column_stack([c[:, 0] * ch - c[:, 2] * shh, c[:, 1], c[:, 0] * shh + c[:, 2] * ch]) + np.asarray(pos)
    rel = Wd - cam.pos
    xc = rel[:, 0] * cam.c - rel[:, 2] * cam.s
    yc = rel[:, 1]
    zc = rel[:, 0] * cam.s + rel[:, 2] * cam.c
    z0 = float(np.median(zc))
    if z0 < 0.45:
        return None
    sc = cam.f / z0 * ss                         # px por metro (perspectiva débil)
    sci = cam.f / np.maximum(zc, 0.2) * ss
    px = xc * sci
    py = -yc * sci
    pr = r * sci
    x_min, x_max = int(np.floor((px - pr).min())) - 4, int(np.ceil((px + pr).max())) + 4
    y_min, y_max = int(np.floor((py - pr).min())) - 4, int(np.ceil((py + pr).max())) + 4
    w, h = x_max - x_min, y_max - y_min
    D = np.full((h, w), np.inf, np.float32)
    I = np.zeros((h, w), np.int32)
    order = np.argsort(-pr)
    for i in order:
        R = pr[i]
        cx, cy = px[i] - x_min, py[i] - y_min
        xa, xb = max(0, int(cx - R)), min(w, int(cx + R) + 2)
        ya, yb = max(0, int(cy - R)), min(h, int(cy + R) + 2)
        if xa >= xb or ya >= yb:
            continue
        dx = np.arange(xa, xb, dtype=np.float32) - cx
        dy = np.arange(ya, yb, dtype=np.float32) - cy
        d2 = dx[None, :] ** 2 + dy[:, None] ** 2
        m = d2 < R * R
        z = zc[i] - np.sqrt(np.maximum(R * R - d2, 0)) / sci[i]
        sub = D[ya:yb, xa:xb]
        m &= z < sub
        sub[m] = z[m]
        I[ya:yb, xa:xb][m] = i
    mask = np.isfinite(D)
    a = mask.astype(np.float32)
    zfar = float(D[mask].max()) + 0.02
    Df = np.where(mask, D, zfar).astype(np.float32)
    ext = cv2.GaussianBlur(Df * a, (0, 0), 2.5 * ss) / np.maximum(cv2.GaussianBlur(a, (0, 0), 2.5 * ss), 1e-4)
    Df = np.where(mask, D, np.where(ext > 0, ext + 0.012 * spec['scale'], zfar)).astype(np.float32)
    # posición en reposo de cada píxel (para que la piel no resbale)
    yy, xx = np.nonzero(mask)
    ii = I[yy, xx]
    off_cam = np.column_stack([(xx + x_min) / sc - xc[ii], -(yy + y_min) / sc - yc[ii], D[yy, xx] - zc[ii]])
    # cámara -> mundo -> animal
    ow = np.column_stack([off_cam[:, 0] * cam.c + off_cam[:, 2] * cam.s, off_cam[:, 1], -off_cam[:, 0] * cam.s + off_cam[:, 2] * cam.c])
    oa = np.column_stack([ow[:, 0] * ch + ow[:, 2] * shh, ow[:, 1], -ow[:, 0] * shh + ow[:, 2] * ch]) / spec["scale"]
    rp = rest[ii] + oa
    kind = cid[ii]
    skin = kind == SKIN
    # relieve fino de la piel: pliegues verticales y poro
    nl = n3(rp, 0.9)
    nm = n3(rp * np.array([1.0, 0.55, 0.55]), 3.7)
    nf = n3(rp, 21.0)
    nw = n3(rp * np.array([1.0, 0.25, 1.0]), 11.0)
    disp = np.zeros((h, w), np.float32)
    disp[yy, xx] = spec.get('rough', 1.0) * ((nm - 0.5) * 0.0030 + (nw - 0.5) * 0.0022 + (nf - 0.5) * 0.0014) * skin * spec["scale"]
    kr = max(1, int(round(0.011 * spec['scale'] * sc)))
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * kr + 1, 2 * kr + 1))
    Dop = cv2.dilate(cv2.erode(Df, ker), ker)                 # rellena surcos estrechos: une volúmenes
    Dop = np.minimum(Df, Dop + 0.004 * spec['scale'])
    Df = np.where(mask, Dop, Df)
    Ds = cv2.GaussianBlur(Df, (0, 0), 1.3 * ss) + disp
    gx = cv2.Sobel(Ds, cv2.CV_32F, 1, 0, ksize=3) / 8.0 * sc
    gy = cv2.Sobel(Ds, cv2.CV_32F, 0, 1, ksize=3) / 8.0 * sc
    nrm = np.stack([gx, -gy, -np.ones_like(gx)], -1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    Lc = cam.to_cam(world.SUN)
    N = nrm[yy, xx]
    ndl = N @ Lc
    ny = N[:, 1]
    # oclusión: hendiduras y partes hundidas tras otras
    def mblur(sig):
        return cv2.GaussianBlur(Df * a, (0, 0), sig) / np.maximum(cv2.GaussianBlur(a, (0, 0), sig), 1e-3)
    ao1 = np.clip(1 - (Df - mblur(0.018 * sc)) / (0.035 * spec["scale"]), 0.35, 1.0)
    ao2 = np.clip(1 - (Df - mblur(0.07 * sc)) / (0.30 * spec["scale"]), 0.62, 1.0)
    ao = (ao1 * ao2)[yy, xx]
    hgt = (rel[ii, 1] + cam.pos[1] + oa[:, 1] * spec["scale"]) / spec["scale"]      # altura sobre el suelo
    ao = ao * (0.62 + 0.38 * smoothstep(0.0, 0.30, hgt + 0.25 * (ny + 1)))
    # --- albedo
    dorsal, flank, ventral = (np.array(spec[k], np.float32) for k in ("dorsal", "flank", "ventral"))
    tv = smoothstep(-0.30, 0.60, ny + 0.5 * (nl - 0.5) + 0.25 * (nm - 0.5))
    tb = smoothstep(0.05, -0.70, ny + 0.4 * (nl - 0.5))
    alb = lerp(flank, dorsal, tv[:, None])
    alb = lerp(alb, ventral, tb[:, None])
    bars = smoothstep(0.50, 0.78, n3(rp * np.array([1.0, 0.12, 0.3]), 2.6)) * (1 - tb) * (rp[:, 0] < 0.5) * (rp[:, 1] > 0.2)
    alb = alb * (1 - spec["bars"] * bars[:, None])
    alb = alb * (0.80 + 0.40 * nl[:, None]) * (0.90 + 0.20 * nf[:, None])
    low = smoothstep(0.16, 0.02, hgt)                         # pies y manos polvorientos y oscuros
    alb = lerp(alb, flank * 0.62, (low * 0.7)[:, None])
    snout = smoothstep(0.80, 0.88, rp[:, 0]) * (rp[:, 1] > 0.43)
    alb = alb * (1 - 0.35 * snout[:, None])
    tooth = np.array([0.66, 0.61, 0.50], np.float32) * (0.8 + 0.3 * nf[:, None])
    alb = np.where((kind == TOOTH)[:, None], tooth, alb)
    alb = np.where((kind == MOUTH)[:, None], np.array([0.42, 0.17, 0.16], np.float32) * (0.8 + 0.3 * nf[:, None]), alb)
    alb = np.where((kind == CLAW)[:, None], np.array([0.16, 0.14, 0.13], np.float32), alb)
    alb = np.where((kind == DARK)[:, None], np.array([0.07, 0.06, 0.06], np.float32), alb)
    alb = np.where((kind == EYE)[:, None], np.array([0.085, 0.055, 0.03], np.float32), alb)
    # --- luz
    wrap = np.clip((ndl + 0.25) / 1.25, 0, 1)
    sky = world.SKY_AMB * (0.50 + 0.38 * ny)[:, None]
    bounce = np.array([0.42, 0.37, 0.31], np.float32) * (np.clip(-ny, 0, 1) * 0.42)[:, None]
    rim = (1 - np.clip(-N[:, 2], 0, 1)) ** 2.5
    light = world.SUN_COL * (wrap * 1.15)[:, None] * ao2[yy, xx][:, None] + (sky + bounce) + world.SKY_AMB * (0.55 * rim)[:, None]
    col = alb * light * ao[:, None]
    Hh = Lc + np.array([0, 0, -1.0])
    Hh /= np.linalg.norm(Hh)
    ndh = np.clip(N @ Hh, 0, 1)
    spec_k = np.where(kind == EYE, 0.9, np.where(kind == TOOTH, 0.25, spec["sheen"] * (1 + 2.5 * snout)))
    spec_p = np.where(kind == EYE, 90.0, 22.0)
    col = col + (ndh ** spec_p * spec_k)[:, None] * world.SUN_COL
    rgb = np.zeros((h, w, 3), np.float32)
    rgb[yy, xx] = col
    idm = np.full((h, w), 255, np.uint8)
    idm[yy, xx] = kind
    # antialias: bajar de la resolución de trabajo
    asoft = cv2.GaussianBlur(a, (0, 0), 0.55 * ss)
    rgb = cv2.GaussianBlur(rgb, (0, 0), 0.45 * ss) / np.maximum(cv2.GaussianBlur(a, (0, 0), 0.45 * ss), 1e-3)[..., None]
    asoft = np.clip((asoft - 0.5) * 2.2 + 0.5, 0, 1)
    ow_, oh_ = max(1, int(round(w / ss))), max(1, int(round(h / ss)))
    rgb = cv2.resize(rgb * asoft[..., None], (ow_, oh_), interpolation=cv2.INTER_AREA)
    asoft = cv2.resize(asoft, (ow_, oh_), interpolation=cv2.INTER_AREA)
    idm = cv2.resize(idm, (ow_, oh_), interpolation=cv2.INTER_NEAREST)
    u0, v0, _ = cam.project(np.array([cam.pos[0], cam.pos[1], cam.pos[2]]) + 0)   # sin uso; ancla abajo
    # ancla: el centro de proyección débil corresponde a (xc=0,yc=0) -> píxel (W/2, vh)
    X0 = cam.W / 2 + x_min / ss
    Y0 = cam.vh + y_min / ss
    sel = (r > 0.012 * spec["scale"])
    return dict(rgb=rgb, a=asoft, kind=idm, x0=X0, y0=Y0, zc=z0, shadow=(Wd[sel][::2], r[sel][::2]),
                base_y=cam.vh + cam.f * cam.pos[1] / z0)
