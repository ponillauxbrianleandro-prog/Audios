"""Roedores del episodio 004: tuco-tuco (Ctenomys) y rata parda.

Mismo método que creature.build (cadenas de esferas sobre un esqueleto, luego mapa de profundidad), pero con
anatomía propia: tronco grueso con regiones (escápula, caja torácica, vientre, pelvis), cráneo ancho con mejillas,
patas cortas con garras de excavador, cola corta. Sistema del animal: x adelante, y arriba, z derecha, en metros
antes de multiplicar por spec["scale"].
"""
import numpy as np
from creature import Builder, _ik, SKIN, TOOTH, EYE, DARK, CLAW, MOUTH
from util import catmull, smoothstep

# Tuco-tuco: ~25 cm de cuerpo, cabeza ancha, orejas diminutas, ojos chicos, incisivos anaranjados.
TUCOTUCO = dict(
    kind="tuco", scale=0.30, speed=0.25, period=0.5, fur=dict(len=1.0, tip=0.22, ruff=1.0), fuse=4.5, soft=6.0, tooth_col=(0.98, 0.72, 0.50),
    dorsal=(0.82, 0.69, 0.60), flank=(0.95, 0.84, 0.72), ventral=(0.98, 0.94, 0.90),
    belly=1.15, girth=1.2, head=1.0, leg=1.0, tail=1.0, claw=1.0, ear=1.0, snout=1.0, tooth=1.0,
    bars=0.0, sheen=0.0, rough=0.0,
)
# Rata parda de ciudad: cuerpo largo y esbelto, hocico puntiagudo, orejas grandes, cola larga casi pelada.
RATA = dict(
    kind="rata", scale=0.30, speed=0.9, period=0.4, fur=dict(len=0.30, tip=0.20, ruff=0.0), fuse=2.0, soft=2.0, tooth_col=(0.97, 0.82, 0.66),
    dorsal=(0.68, 0.62, 0.68), flank=(0.82, 0.78, 0.82), ventral=(0.94, 0.92, 0.94),
    belly=0.62, girth=0.58, head=0.74, leg=1.25, tail=3.0, claw=0.6, ear=1.5, snout=2.3, tooth=0.55,
    bars=0.0, sheen=0.0, rough=0.0,
)


def _head_xf(spec, head_pitch, head_yaw, gape, H0, hs):
    cp, sp_ = np.cos(head_pitch), np.sin(head_pitch)
    cy, sy = np.cos(head_yaw), np.sin(head_yaw)
    sn = spec["snout"]

    def hd(p, jaw=False):
        p = np.atleast_2d(np.asarray(p, np.float64)).copy()
        p[:, 0] = np.where(p[:, 0] > 0.12, 0.12 + (p[:, 0] - 0.12) * sn, p[:, 0])
        p = p * hs
        if jaw and gape:
            jx, jy = 0.02 * hs, -0.07 * hs
            cg, sg = np.cos(gape), np.sin(gape)
            x, y = p[:, 0] - jx, p[:, 1] - jy
            p = np.column_stack([jx + x * cg + y * sg, jy - x * sg + y * cg, p[:, 2]])
        x = p[:, 0] * cp - p[:, 1] * sp_          # pitch > 0 levanta el hocico
        y = p[:, 0] * sp_ + p[:, 1] * cp
        z = p[:, 2]
        return np.column_stack([x * cy - z * sy, y, x * sy + z * cy]) + H0

    def hrest(p):
        p = np.atleast_2d(np.asarray(p, np.float64)).copy()
        p[:, 0] = np.where(p[:, 0] > 0.12, 0.12 + (p[:, 0] - 0.12) * sn, p[:, 0])
        return p * hs + np.array([0.50, 0.25, 0.0])

    return hd, hrest


def build_roedor(spec, phase=0.0, walk=0.0, t=0.0, head_pitch=0.0, head_yaw=0.0, head_dx=0.0, head_dy=0.0,
                 gape=0.0, crouch=0.0, dig=0.0, chew=0.0, tail_amp=1.0, bob=1.0, **_):
    b = Builder()
    g = spec["girth"]
    br = 1 + 0.022 * np.sin(2 * np.pi * t / 3.1)            # respiración
    rata = spec["kind"] == "rata"
    low = 0.045 * crouch - (0.075 if rata else 0.0)          # la rata va erguida sobre patas largas
    L = 1.15 if rata else 1.0                               # largo relativo del tronco
    # ---- columna: (x, y, radio). Regiones: pelvis, lomo, caja torácica, escápula
    sp = np.array([
        (-0.52 * L, 0.17, 0.085), (-0.42 * L, 0.20, 0.145), (-0.28 * L, 0.225, 0.185), (-0.08, 0.235, 0.205),
        (0.12, 0.24, 0.205), (0.28, 0.235, 0.190), (0.38, 0.235, 0.165),
    ], np.float64)
    sp[:, 1] -= low
    rest = np.stack([sp[:, 0], sp[:, 1] + low, np.zeros(len(sp))], 1)
    pts = sp[:, :3].copy()
    pts[:, 2] = 0.0
    pts[:, 1] += 0.004 * bob * np.sin(2 * np.pi * t / 3.1) * np.array([0, 0, 0.5, 1, 1, 0.5, 0])
    rad = sp[:, 2] * g
    rad[2:6] *= br
    P = catmull(np.column_stack([pts, rad, rest]), 30)
    b.chain(P[:, :3], P[:, 3], P[:, 4:7])
    # vientre propio (curvatura distinta del lomo) y pecho
    bw = spec["belly"]
    bel = [(-0.22 * L, 0.175 - low, 0.140 * bw), (-0.02, 0.165 - low, 0.175 * bw), (0.18, 0.170 - low, 0.165 * bw),
           (0.32, 0.185 - low, 0.130)]
    b.chain(np.array([(x, y, 0.0) for x, y, r in bel]), np.array([r for *_, r in bel]) * g * br,
            np.array([(x, y + low, 0.0) for x, y, r in bel]))
    # flancos: costillar a cada lado (da la forma de barril con regiones, no un cilindro liso)
    for s in (-1, 1):
        b.ball(np.array([-0.02, 0.215 - low, s * 0.095 * g]), 0.135 * g * br, np.array([-0.02, 0.215, s * 0.095 * g]))
        b.ball(np.array([0.28, 0.255 - low, s * 0.075 * g]), 0.115 * g, np.array([0.28, 0.255, s * 0.075 * g]))   # escápula
        b.ball(np.array([-0.34 * L, 0.205 - low, s * 0.085 * g]), 0.105 * g, np.array([-0.34 * L, 0.205, s * 0.085 * g]))  # cadera

    # ---- cuello y cabeza
    hs = spec["head"]
    H0 = np.array([0.50 + head_dx, 0.25 + head_dy - low * 0.6, 0.0])
    sh = np.array([0.36, 0.235 - low, 0.0])
    mid = (sh + H0) / 2
    neck = catmull(np.array([sh, mid, H0]), 6)
    b.chain(neck, np.linspace(0.165 * g, 0.12 * hs, 6), catmull(np.array([[0.36, 0.235, 0], [0.43, 0.24, 0], [0.50, 0.25, 0]]), 6))
    hd, hrest = _head_xf(spec, head_pitch, head_yaw + 0.0, gape + 0.10 * chew * (0.5 + 0.5 * np.sin(t * 9.0)), H0, hs)

    def hchain(p, r, cid=SKIN, jaw=False, k=0.42):
        p = np.asarray(p, np.float64)
        b.chain(hd(p, jaw), np.asarray(r, np.float64) * hs, hrest(p), cid, k)

    def hball(p, r, cid=SKIN, jaw=False):
        b.ball(hd(p, jaw)[0], r * hs, hrest(p)[0], cid)

    wd = 1.0 if not rata else 0.72                           # ancho del cráneo
    # bóveda craneal ancha, mejillas con volumen propio, hocico romo
    hchain([(-0.12, 0.02, 0), (-0.04, 0.04, 0), (0.06, 0.02, 0)], [0.125 * wd + 0.015, 0.135 * wd + 0.015, 0.125 * wd + 0.015])
    for s in (-1, 1):
        hchain([(-0.02, 0.035, s * 0.060 * wd), (0.09, 0.040, s * 0.062 * wd)], [0.085 * wd + 0.015, 0.078 * wd + 0.015])   # frente y ceja (más estrecha)
        hball((0.06, -0.050, s * 0.100 * wd), 0.088 * wd + 0.005)                       # mejilla con volumen propio
        hball((0.17, -0.050, s * 0.062 * wd), 0.072 * wd + 0.005)                       # almohadilla de bigotes
        hball((-0.07, 0.10, s * 0.095 * wd), 0.030 * spec["ear"] ** 0.5)                # oreja (diminuta en el tuco-tuco)
        if rata:
            hchain([(-0.09, 0.13, s * 0.085), (-0.105, 0.20, s * 0.098)], [0.040, 0.056])
        hball((0.165, 0.031, s * 0.106 * wd), 0.0185, EYE)                              # ojo pequeño integrado en el cráneo
    hchain([(0.10, 0.0, 0), (0.22, -0.020, 0), (0.33, -0.040, 0)], [0.092 * wd + 0.012, 0.074, 0.056])          # hocico
    hball((0.372 if not rata else 0.356, -0.030, 0), 0.020, DARK)               # nariz
    # incisivos: grandes y a la vista en el tuco-tuco
    ts = spec["tooth"]
    for s in (-1, 1):
        hchain([(0.345, -0.062, s * 0.017), (0.352, -0.062 - 0.075 * ts, s * 0.017)], [0.0155, 0.0105], TOOTH, k=0.3)
    # mandíbula inferior
    hchain([(0.02, -0.12, 0), (0.14, -0.125, 0), (0.28, -0.115, 0)], [0.075 * wd + 0.01, 0.068, 0.048], jaw=True)
    for s in (-1, 1):
        hchain([(0.30, -0.106, s * 0.016), (0.305, -0.106 + 0.040 * ts, s * 0.016)], [0.0085, 0.006], TOOTH, jaw=True, k=0.3)
    if gape + 0.10 * chew > 0.10:
        hchain([(0.06, -0.065, 0), (0.18, -0.07, 0), (0.30, -0.075, 0)], [0.05, 0.045, 0.034], MOUTH)

    # ---- patas
    lg = spec["leg"]
    ground = 0.0
    legs = [("RF", 1, True), ("LF", -1, True), ("RH", 1, False), ("LH", -1, False)]
    for name, side, fore in legs:
        if fore:
            J = np.array([0.27, 0.160 - low, side * 0.125 * g])
            Ar = np.array([0.36, 0.045, side * 0.150 * g])
            l1, l2 = 0.135 * lg, 0.125 * lg
            pole = np.array([-0.8, 0.35, side * 0.55])
            r = [0.085, 0.066, 0.058, 0.047]
        else:
            J = np.array([-0.30 * L, 0.185 - low, side * 0.125 * g])
            Ar = np.array([-0.26 * L, 0.042, side * 0.150 * g])
            l1, l2 = 0.150 * lg, 0.135 * lg
            pole = np.array([0.85, 0.25, side * 0.40])
            r = [0.098, 0.075, 0.060, 0.048]
        A = Ar.copy()
        lift = 0.0
        if fore and dig > 0:                                  # excavar: las manos rascan alternadas hacia atrás
            w = 2 * np.pi * 2.4 * t + (0.0 if side > 0 else np.pi)
            s_ = np.sin(w)
            A = Ar + np.array([0.05 * s_, 0.075 * max(0.0, np.cos(w)), 0.0]) * dig
            lift = 0.075 * max(0.0, np.cos(w)) * dig
        K, A = _ik(J, A, l1, l2, pole)
        Jr = J + np.array([0, low, 0])
        Kr = (Jr + Ar) / 2 + pole * 0.05
        lr = 0.55 if rata else 1.0                                   # patas finas en la rata
        b.chain([J, (J + K) / 2, K, K + (A - K) * 0.5, A], [r[0] * g * (0.8 if rata else 1.0), r[1] * g * lr, r[2] * lr, r[2] * 0.95 * lr, r[3] * lr],
                [Jr, (Jr + Kr) / 2, Kr, Kr + (Ar - Kr) * 0.5, Ar])
        # mano/pie con cuatro dedos y garras (largas en el excavador)
        T = np.array([A[0] + (0.060 if fore else 0.085), max(0.026, A[1] - 0.012), A[2] + side * 0.004])
        b.chain([A, T], [r[3], 0.034], [Ar, Ar + [0.065, -0.02, 0]])
        cl = spec["claw"] * (1.0 if fore else 0.6)
        for j in range(4):
            a = side * (-0.38 + 0.25 * j)
            d = np.array([np.cos(a), 0, np.sin(a)])
            t0 = T + d * 0.010
            t1 = T + d * 0.040 + np.array([0, -0.004, 0])
            t1[1] = max(t1[1], 0.014 + lift)
            b.chain([t0, t1], [0.016, 0.012], [Ar + [0.07, 0, 0], Ar + [0.11, 0, 0]], k=0.5)
            b.chain([t1, t1 + d * 0.050 * cl + np.array([0, -0.010 * cl, 0])], [0.0075, 0.0022], None, CLAW, k=0.4)

    # ---- cola
    tl = spec["tail"]
    sway = 0.03 * tail_amp * np.sin(t * 1.3)
    tp = catmull(np.array([(-0.50 * L, 0.18 - low, 0), (-0.58 * L - 0.05 * tl, 0.16 - low, sway * 0.5),
                           (-0.62 * L - 0.12 * tl, 0.13 - low, sway), (-0.64 * L - 0.20 * tl, 0.09 - low, sway * 1.4)]), 12)
    tr = np.linspace(0.060 if not rata else 0.030, 0.016 if not rata else 0.008, 12)
    b.chain(tp, tr, np.column_stack([tp[:, 0], tp[:, 1] + low, np.zeros(len(tp))]))
    c, r_, rest_, cid = b.done()
    s = spec["scale"]
    return c * s, r_ * s, rest_, cid


TUCOTUCO["builder"] = build_roedor
RATA["builder"] = build_roedor
