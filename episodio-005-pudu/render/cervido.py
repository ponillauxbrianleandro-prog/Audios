"""Cérvidos del episodio 005: pudú (Pudu puda) y ciervo colorado (el "familiar" de la apertura).

Mismo método que creature.build (cadenas de esferas sobre un esqueleto, mapa de profundidad, luz y pelaje procedural),
pero con anatomía propia de cérvido: tronco con grupa y paleta de hombro, vientre con curvatura independiente,
cuello corto y grueso (largo en el ciervo), cabeza en cuña con hocico oscuro, orejas grandes y redondeadas con
giro propio, patas finas de dos tramos (rodilla hacia adelante en las manos, corvejón hacia atrás en las patas),
pezuñas, rabito y cuernos (púas simples en el pudú, ramificados en el ciervo).
Sistema del animal: x adelante, y arriba, z derecha, en unidades antes de multiplicar por spec["scale"].
"""
import numpy as np
from creature import Builder, _ik, SKIN, TOOTH, EYE, DARK, CLAW, MOUTH, ANTLER
from util import catmull, smoothstep, lerp

LEGS = [("LH", -1, 0.00, False), ("LF", -1, 0.25, True), ("RH", 1, 0.50, False), ("RF", 1, 0.75, True)]
STAND = dict(LH=-0.02, LF=0.03, RH=0.03, RF=-0.02)


def _paint_pudu(alb, rp, skin, ny, nl, hgt, snout):
    """Marcas del pudú: hocico y nariz oscuros, mentón claro, anillo ocular, patas bajas más oscuras, vientre y cola claros."""
    x, y = rp[:, 0], rp[:, 1]
    hocico = smoothstep(0.72, 0.80, x) * smoothstep(0.50, 0.58, y) * skin
    alb = alb * (1 - 0.55 * hocico)[:, None]
    menton = smoothstep(0.76, 0.70, x) * smoothstep(0.58, 0.54, y) * smoothstep(0.60, 0.64, x) * skin
    alb = lerp(alb, np.array([0.80, 0.72, 0.62], np.float32), (0.55 * menton)[:, None])
    patas = smoothstep(0.26, 0.10, hgt) * skin
    alb = alb * (1 - 0.30 * patas)[:, None]
    cola = smoothstep(-0.38, -0.46, x) * skin * smoothstep(0.50, 0.44, y)
    alb = lerp(alb, np.array([0.86, 0.80, 0.72], np.float32), (0.55 * cola)[:, None])
    return alb, hocico


def _paint_ciervo(alb, rp, skin, ny, nl, hgt, snout):
    x, y = rp[:, 0], rp[:, 1]
    hocico = smoothstep(0.80, 0.90, x) * smoothstep(0.68, 0.78, y) * skin
    alb = alb * (1 - 0.45 * hocico)[:, None]
    grupa = smoothstep(-0.34, -0.42, x) * skin * smoothstep(0.62, 0.50, y)
    alb = lerp(alb, np.array([0.90, 0.82, 0.68], np.float32), (0.7 * grupa)[:, None])
    patas = smoothstep(0.34, 0.12, hgt) * skin
    alb = alb * (1 - 0.30 * patas)[:, None]
    return alb, hocico


def build_cervido(spec, phase=0.0, walk=0.0, t=0.0, head_pitch=0.0, head_yaw=0.0, head_dx=0.0, head_dy=0.0,
                  gape=0.0, chew=0.0, ear=0.0, ear_l=0.0, ear_r=0.0, tail_amp=1.0, bob=1.0, shake=0.0, low=0.0, **_):
    b = Builder()
    g = spec["girth"]
    nk = spec["neck"]
    lg = spec["leg"]
    tw = 2 * np.pi * phase
    br = 1 + 0.020 * np.sin(2 * np.pi * t / 3.0)                      # respiración
    sh = shake * np.sin(t * 38.0)                                     # sacudida de agua del pelaje (lateral y rápida)
    yb = lg - 1.0                                                     # altura extra del tronco (ciervo de patas largas)
    body_y = 0.43 + 0.30 * yb * 0.5 + 0.10 * yb
    # ---- columna: (x, y, radio). Grupa, lomo, caja torácica, cruz
    sp = np.array([
        (-0.43, 0.44, 0.095), (-0.33, 0.475, 0.130), (-0.17, 0.495, 0.140), (0.01, 0.505, 0.148),
        (0.17, 0.52, 0.132), (0.29, 0.535, 0.108),
    ], np.float64)
    sp[:, 1] += (body_y - 0.43) - low
    rest = np.stack([sp[:, 0], sp[:, 1] + low, np.zeros(len(sp))], 1)
    pts = sp[:, :3].copy()
    pts[:, 2] = sh * (0.4 - pts[:, 0])                                 # la sacudida se nota más atrás
    pts[:, 1] += 0.004 * bob * np.sin(2 * tw + 0.5) * walk
    rad = sp[:, 2] * g
    rad[1:5] *= br
    P = catmull(np.column_stack([pts, rad, rest]), 26)
    b.chain(P[:, :3], P[:, 3], P[:, 4:7])
    dy = (body_y - 0.43) - low
    bel = [(-0.22, 0.385 + dy, 0.105), (0.00, 0.350 + dy, 0.140), (0.18, 0.375 + dy, 0.110)]
    b.chain(np.array([(x, y, 0.0) for x, y, r in bel]), np.array([r for *_, r in bel]) * g * br,
            np.array([(x, y + low, 0.0) for x, y, r in bel]))
    for s in (-1, 1):
        b.ball(np.array([-0.34, 0.455 + dy, s * 0.045 * g]), 0.082 * g, np.array([-0.34, 0.455 + dy + low, s * 0.045 * g]))   # grupa
        b.ball(np.array([0.19, 0.455 + dy, s * 0.040 * g]), 0.078 * g, np.array([0.19, 0.455 + dy + low, s * 0.040 * g]))     # paleta
        b.ball(np.array([0.00, 0.445 + dy, s * 0.050 * g]), 0.100 * g * br, np.array([0.00, 0.445 + dy + low, s * 0.050 * g]))  # costillar

    # ---- cuello y cabeza
    hs = spec["head"]
    bx, by = 0.30 + 0.20 * nk, 0.545 + dy + 0.085 * nk
    H0 = np.array([bx + head_dx, by + head_dy, 0.0])
    shd = np.array([0.30, 0.535 + dy, 0.0])
    H0r = np.array([bx, by + low, 0.0])
    mid = (shd + H0) / 2 + np.array([0.0, 0.015 * nk, 0.0])
    neck = catmull(np.array([shd, mid, H0]), 7)
    neck[:, 2] += sh * 0.1
    b.chain(neck, np.linspace(0.115 * g * (1 + 0.15 * (nk - 1)), 0.070 * hs, 7),
            catmull(np.array([shd + [0, low, 0], (shd + H0r) / 2, H0r]), 7))
    cp, sp_ = np.cos(head_pitch), np.sin(head_pitch)
    cy, sy = np.cos(head_yaw), np.sin(head_yaw)
    gp = gape + 0.11 * chew * (0.5 + 0.5 * np.sin(t * 8.0))

    def hd(p, jaw=False):
        p = np.atleast_2d(np.asarray(p, np.float64)).copy() * hs
        if jaw and gp:
            jx, jy = 0.02 * hs, -0.06 * hs
            cg, sg = np.cos(gp), np.sin(gp)
            x, y = p[:, 0] - jx, p[:, 1] - jy
            p = np.column_stack([jx + x * cg + y * sg, jy - x * sg + y * cg, p[:, 2]])
        x = p[:, 0] * cp - p[:, 1] * sp_                                 # pitch > 0 levanta el hocico
        y = p[:, 0] * sp_ + p[:, 1] * cp
        z = p[:, 2]
        return np.column_stack([x * cy - z * sy, y, x * sy + z * cy]) + H0

    def hrest(p):
        return np.atleast_2d(np.asarray(p, np.float64)) * hs + H0r

    def hchain(p, r, cid=SKIN, jaw=False, k=0.42):
        p = np.asarray(p, np.float64)
        b.chain(hd(p, jaw), np.asarray(r, np.float64) * hs, hrest(p), cid, k)

    def hball(p, r, cid=SKIN, jaw=False):
        b.ball(hd(p, jaw)[0], r * hs, hrest(p)[0], cid)

    # bóveda craneal, frente, hocico en cuña
    hchain([(-0.03, 0.020, 0), (0.05, 0.030, 0), (0.12, 0.020, 0)], [0.068, 0.070, 0.062])
    hchain([(0.12, 0.012, 0), (0.20, -0.012, 0), (0.28, -0.030, 0)], [0.058, 0.046, 0.034])
    for s in (-1, 1):
        hchain([(0.04, 0.026, s * 0.040), (0.13, 0.014, s * 0.030)], [0.050, 0.040])               # frente / arco de la ceja
        hball((0.07, -0.030, s * 0.052), 0.050)                                                     # mejilla con volumen propio
        hball((0.22, -0.034, s * 0.022), 0.034)                                                     # hocico lateral
        hball((0.125, 0.032, s * 0.055), 0.019, EYE)                                                # ojo integrado al cráneo
        hball((0.092, 0.050, s * 0.058), 0.018)                                                     # párpado superior
        # oreja grande y redondeada: base, medio y punta; gira hacia afuera/adelante con ear
        e = (ear_l if s < 0 else ear_r) + ear
        base = np.array([0.000, 0.060, s * 0.040])
        midp = np.array([-0.020 + 0.030 * e, 0.115, s * (0.085 + 0.035 * e)])
        tip = np.array([-0.045 + 0.060 * e, 0.178 - 0.02 * e, s * (0.130 + 0.060 * e)])
        hchain([base, midp, tip], [0.026, 0.044 * spec["ear"], 0.030 * spec["ear"]], k=0.36)
        if spec["antlers"] == "spike":                                                              # púas simples, curvadas hacia atrás
            hchain([(0.010, 0.070, s * 0.034), (0.000, 0.105, s * 0.040), (-0.022, 0.152, s * 0.046), (-0.050, 0.188, s * 0.050)],
                   [0.017, 0.013, 0.010, 0.004], ANTLER, k=0.34)
        elif spec["antlers"] == "branched":                                                         # candelabro: viga + puntas
            beam = [(0.010, 0.070, s * 0.034), (-0.020, 0.180, s * 0.075), (-0.075, 0.330, s * 0.100), (-0.060, 0.470, s * 0.110),
                    (0.010, 0.560, s * 0.105), (0.080, 0.600, s * 0.100)]
            hchain(beam, [0.026, 0.022, 0.019, 0.016, 0.012, 0.005], ANTLER, k=0.34)
            for f0, ln in ((1, 0.17), (2, 0.20), (3, 0.17)):
                q = np.array(beam[f0])
                hchain([q, q + [0.07, 0.07, s * 0.02], q + [0.12 * ln / 0.17, 0.13 * ln / 0.17, s * 0.03]], [0.014, 0.010, 0.004], ANTLER, k=0.34)
            q = np.array(beam[4])
            hchain([q, q + [0.0, 0.07, s * 0.04], q + [-0.03, 0.15, s * 0.07]], [0.012, 0.009, 0.004], ANTLER, k=0.34)
    hball((0.288, -0.030, 0), 0.020, DARK)                                                          # nariz
    # mandíbula inferior
    hchain([(0.02, -0.075, 0), (0.14, -0.080, 0), (0.25, -0.066, 0)], [0.040, 0.036, 0.026], jaw=True)
    if gp > 0.10:
        hchain([(0.06, -0.040, 0), (0.17, -0.045, 0), (0.26, -0.044, 0)], [0.034, 0.030, 0.022], MOUTH)

    # ---- patas
    sc_ = spec["scale"]
    beta = 0.62
    Lst = spec["speed"] / sc_ * beta * spec["period"]
    for name, side, off, fore in LEGS:
        if fore:
            J = np.array([0.20, 0.415 + dy - low, side * 0.075 * g])
            x0, zf = 0.265, side * 0.082 * g
            l1, l2 = 0.205 * lg, 0.215 * lg
            pole = np.array([0.9, 0.15, side * 0.20])                         # rodilla hacia adelante
            r = [0.062, 0.040, 0.034, 0.026]
        else:
            J = np.array([-0.31, 0.425 + dy - low, side * 0.075 * g])
            x0, zf = -0.30, side * 0.082 * g
            l1, l2 = 0.215 * lg, 0.215 * lg
            pole = np.array([-0.9, 0.10, side * 0.20])                        # corvejón hacia atrás
            r = [0.075, 0.046, 0.034, 0.026]
        Jr = J + np.array([0, low, 0])
        p = (phase + off) % 1.0
        if p < beta:
            s = p / beta
            fx = x0 + Lst / 2 - Lst * s
            ay = 0.050 + 0.020 * smoothstep(0.75, 1.0, s)
        else:
            s = (p - beta) / (1 - beta)
            e = s * s * (3 - 2 * s)
            fx = x0 - Lst / 2 + Lst * e
            ay = 0.050 + 0.075 * np.sin(np.pi * s) + 0.03 * (1 - s) ** 2
        fx = fx * walk + (x0 + STAND[name]) * (1 - walk)
        ay = ay * walk + 0.050 * (1 - walk)
        A = np.array([fx, ay, zf])
        K, A = _ik(J, A, l1, l2, pole)
        Ar = np.array([x0, 0.050, zf])
        Kr = (Jr + Ar) / 2 + pole * 0.05
        Mr = Kr + (Ar - Kr) * 0.5
        b.chain([J, (J + K) / 2, K, K + (A - K) * 0.5, A], [r[0] * g, r[1] * g, r[1] * 0.85, r[2], r[3]],
                [Jr, (Jr + Kr) / 2, Kr, Mr, Ar])
        # pezuña: dos medias lunas oscuras
        T = np.array([A[0] + 0.030, max(0.014, A[1] - 0.030), A[2]])
        b.chain([A, T], [0.030, 0.026], [Ar, Ar + [0.03, -0.035, 0]], k=0.5)
        b.ball(T + np.array([0.012, -0.004, 0]), 0.020, Ar + [0.045, -0.04, 0], CLAW)

    # ---- rabito
    tf = 0.020 * tail_amp * np.sin(t * 2.2)
    tp = catmull(np.array([(-0.45, 0.47 + dy - low, 0), (-0.50, 0.485 + dy - low, tf), (-0.535, 0.495 + dy - low, tf * 1.5)]), 6)
    b.chain(tp, np.linspace(0.040, 0.020, 6), np.column_stack([tp[:, 0], tp[:, 1] + low, np.zeros(len(tp))]))
    c, r_, rest_, cid = b.done()
    s = spec["scale"]
    return c * s, r_ * s, rest_, cid


# Pudú: ~40 cm a la cruz, ~10 kg. Pelaje áspero y tupido pardo rojizo, vientre más claro, hocico oscuro, púas de ~10 cm.
PUDU = dict(
    kind="pudu", scale=0.70, speed=0.35, period=0.80, fur=dict(len=1.05, tip=0.32, ruff=1.0), fuse=6.0, soft=6.5, dark_col=(0.10, 0.08, 0.09),
    dorsal=(0.42, 0.28, 0.20), flank=(0.56, 0.38, 0.27), ventral=(0.78, 0.66, 0.54),
    girth=1.14, head=1.18, leg=0.86, neck=1.0, ear=0.85, antlers="spike", antler_col=(0.20, 0.17, 0.15),
    bars=0.0, sheen=0.0, rough=0.4, paint=_paint_pudu, seed=11,
    fur_flow=dict(nose=(0.80, 0.56, 0.0), ancho_cabeza=0.50, back=(-1.0, -0.22, 0.0), down=0.75, vy=(0.40, 0.30)),
)
# Pudú hembra: sin púas.
PUDU_H = dict(PUDU, antlers="none", seed=13)
# Ciervo colorado: ~1,2 m a la cruz, cuernos ramificados; solo aparece de fondo/apertura.
CIERVO = dict(
    kind="ciervo", scale=1.35, speed=0.70, period=1.3, fur=dict(len=0.85, tip=0.22, ruff=0.8), fuse=5.0, soft=5.5, dark_col=(0.10, 0.08, 0.09),
    dorsal=(0.48, 0.32, 0.22), flank=(0.66, 0.46, 0.31), ventral=(0.84, 0.74, 0.60),
    girth=1.05, head=1.05, leg=1.40, neck=2.0, ear=0.95, antlers="branched", antler_col=(0.40, 0.33, 0.27),
    bars=0.0, sheen=0.02, rough=0.4, paint=_paint_ciervo, seed=17,
    fur_flow=dict(nose=(0.96, 0.78, 0.0), ancho_cabeza=0.62, back=(-1.0, -0.22, 0.0), down=0.75, vy=(0.55, 0.40)),
)
for _s in (PUDU, PUDU_H, CIERVO):
    _s["builder"] = build_cervido
