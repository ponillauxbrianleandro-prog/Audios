"""Cinematografía del episodio 005: cámaras (land/track), actores, poses y plantas de primer plano.
Extraído de documental.py del episodio 003 (mismo motor), con cámaras más dinámicas (v7)."""
import sys
from pathlib import Path
import numpy as np
import cv2
sys.path.insert(0, str(Path(__file__).resolve().parent))
import world
import engine
import biomes
import creature as C

FPS = 24
GOR, PRO, DII, PAR, THR, ANF, VET, LYS = C.GORGONOPS, C.PROCYNOSUCHUS, C.DIICTODON, C.PAREIASAUR, C.THRINAXODON, C.ANFIBIO, C.VETUSODON, C.LYSTRO
def unit(a):
    return np.array([np.cos(a), np.sin(a)])


    return np.array([np.cos(a), np.sin(a)])


def shake(t, amp):
    return (amp * (np.sin(t * 0.83) + 0.6 * np.sin(t * 1.9 + 1.3) + 0.3 * np.sin(t * 3.7 + 0.4)),
            amp * (np.sin(t * 0.71 + 2.0) + 0.6 * np.sin(t * 2.3 + 0.2) + 0.3 * np.sin(t * 4.1)))


def aim(W, H, f, pos, target, vfrac, ufrac=0.5):
    dx, dz = target[0] - pos[0], target[2] - pos[2]
    yaw = np.arctan2(dx, dz) + np.arctan((0.5 - ufrac) * W / f)
    zc = np.hypot(dx, dz)
    vh = vfrac * H - f * (pos[1] - target[1]) / zc
    return yaw, np.arctan((H / 2 - vh) / f)


def sm(x):
    x = float(np.clip(x, 0, 1))
    return x * x * (3 - 2 * x)


def dist_at(x, z, dry=0.0):
    m = world.MAPS[0]
    tx = int(np.clip((x - world.GX0) / world.GRES, 0, m.shape[1] - 1))
    tz = int(np.clip((z - world.GZ0) / world.GRES, 0, m.shape[0] - 1))
    return float(m[tz, tx, 3] + dry * (1.0 + 2.2 * m[tz, tx, 2]))


def bank_z(x, dry=0.0, margin=0.15):
    """Orilla cercana del tramo de río que cruza de lado a lado."""
    for z in np.arange(3.0, 40.0, 0.05):
        if dist_at(x, z, dry) < margin:
            return z
    return 14.0


def bank_x(z, margin=0.15):
    """Orilla oeste del tramo de río que corre hacia el fondo (pantano)."""
    for x in np.arange(14.0, 60.0, 0.05):
        if dist_at(x, z) < margin:
            return x
    return 30.0


# ---- poses
def p_walk(spec, speed=1.0, **kw):
    def f(t, d):
        return dict(phase=d / (spec["speed"] * spec["period"]) + 0.15, walk=1.0, t=t, head_yaw=0.10 * np.sin(t * 0.7),
                    head_pitch=0.10 + 0.05 * np.sin(t * 1.1), head_dy=-0.03, bob=min(2.2, 0.6 + 0.6 * speed), **kw)
    return f


def p_idle(look=0.25, pitch=0.05, **kw):
    def f(t, d):
        return dict(phase=0.0, walk=0.0, t=t, head_yaw=look * np.sin(t * 0.55 + 0.4) + 0.08 * np.sin(t * 1.7),
                    head_pitch=pitch + 0.04 * np.sin(t * 0.9), tail_amp=0.8, **kw)
    return f


def p_sniff(**kw):
    def f(t, d):
        return dict(phase=0.0, walk=0.0, t=t, head_dy=0.06, head_pitch=-0.26 + 0.05 * np.sin(t * 9), head_yaw=0.35 * np.sin(t * 1.6), **kw)
    return f


def p_drink(t_up=5.6, t_in=0.3):
    def f(t, d):
        e = sm((t - t_in) / 1.6)
        up = sm((t - t_up) / 1.2)
        dd = e * (1 - 0.75 * up)
        lap = (t > t_in + 1.6) * (1 - up)
        return dict(phase=0.0, walk=0.0, t=t, drop=0.075 * dd, head_dy=-0.165 * dd, head_dx=0.02 * dd, head_pitch=0.05 + 0.60 * dd,
                    head_yaw=0.05 + 0.22 * up, gape=float(0.05 * lap * (0.5 + 0.5 * np.sin(t * 2 * np.pi * 2.1))), tail_amp=0.8)
    return f


def p_yawn(t0=1.5):
    def f(t, d):
        g = sm((t - t0) / 1.3) * (1 - sm((t - t0 - 3.4) / 1.2))
        return dict(phase=0.0, walk=0.0, t=t, gape=1.05 * g, head_pitch=0.03 - 0.30 * g, head_dy=0.03 * g, head_yaw=0.06 * np.sin(t * 0.6))
    return f


def p_lie(sleep=False):
    def f(t, d):
        return dict(phase=0.0, walk=0.0, t=t, crouch=1.0, head_dy=-0.20 - (0.03 if sleep else 0), head_pitch=0.14,
                    head_yaw=0.0 if sleep else 0.18 * np.sin(t * 0.4), tail_amp=0.3)
    return f


def p_eat():
    def f(t, d):
        j = max(0.0, np.sin(t * 2.6)) ** 6
        return dict(phase=0.0, walk=0.0, t=t, drop=0.07, head_dy=-0.17 + 0.05 * j, head_pitch=0.55 - 0.25 * j, head_yaw=0.15 * np.sin(t * 1.3),
                    gape=0.10 + 0.25 * j, tail_amp=1.2)
    return f


def p_stalk(spec):
    def f(t, d):
        return dict(phase=d / (spec["speed"] * spec["period"]), walk=1.0, t=t, crouch=0.32, head_dy=-0.10, head_pitch=0.12, bob=0.4, tail_amp=0.4)
    return f


def p_fight(spec, ph=0.0, ritmo=1.7):
    """Pelea reconstruida: embestidas con la cabeza adelantada y la boca abierta, retroceso y vuelta al acecho."""
    def f(t, d):
        c = ((t + ph) % ritmo) / ritmo
        lunge = float(np.sin(np.pi * c / 0.34)) if c < 0.34 else 0.0
        return dict(phase=0.0, walk=0.0, t=t, crouch=0.10 + 0.10 * lunge, head_dx=0.30 * lunge - 0.04, head_pitch=0.22 - 0.30 * lunge,
                    head_yaw=0.16 * np.sin(t * 3.1 + ph), gape=1.05 * lunge, tail_amp=1.8, bob=1.4)
    return f


def p_alerta(spec, mira=0.0):
    """Quieto y atento: cabeza alta, mirando al frente con leves giros."""
    def f(t, d):
        return dict(phase=0.0, walk=0.0, t=t, head_pitch=-0.05, head_dy=0.04, head_yaw=mira + 0.10 * np.sin(t * 0.9), tail_amp=1.0)
    return f


def actor(spec, p0, ang, speed=1.0, pose=None, start=0.0, ss=1.7, stop=None, go=None):
    """Actor que avanza en línea recta. stop/go = segundos entre los que se detiene."""
    D = unit(ang)
    pose = pose or (p_walk(spec, speed) if speed > 0 else p_idle())

    def moving(t):
        w = 1.0
        if stop is not None:
            w = float(np.clip((stop - t) / 0.4, 0, 1) + (np.clip((t - go) / 0.4, 0, 1) if go is not None else 0))
        return min(1.0, w)

    def dist(t):
        if stop is None:
            return spec["speed"] * speed * (t + start)
        ts = np.linspace(0, max(t, 1e-3), max(2, int(t * 30)))
        return float(np.trapezoid([moving(x) for x in ts], ts)) * spec["speed"] * speed + spec["speed"] * speed * start

    def f(t):
        d = dist(t)
        ps = dict(pose(t, d))
        if stop is not None:
            w = moving(t)
            ps["walk"] = ps.get("walk", 1.0) * w
            if w < 1:
                sn = p_sniff()(t, d)
                for k_ in ("head_dy", "head_pitch", "head_yaw"):
                    ps[k_] = ps.get(k_, 0.0) * w + sn[k_] * (1 - w)
        return dict(spec=spec, pos=np.array([p0[0] + D[0] * d, 0.0, p0[1] + D[1] * d]), heading=ang, pose=ps, ss=ss)
    f.pos = lambda t: np.array([p0[0] + D[0] * dist(t), 0.0, p0[1] + D[1] * dist(t)])
    f.spec, f.ang = spec, ang
    f.vel = spec["speed"] * speed if speed > 0 else 0.0
    return f


# ---- planos
def land(biome, pos, yaw, f=1450, pitch=0.012, move=(0, 0, 0), dyaw=0.0, dpitch=0.0, zf=60.0, ap=0.0015, wx=None, fg=None, rot=None,
         shk=0.0009, actors=(), ripples=None, through=True, life_at=None):
    pos = np.array(pos, float)
    if not any(move) and dyaw == 0.0:            # nunca una cámara quieta: travelling + giro suave
        move, dyaw = (0.32, 0.015, 0.50), 0.020
    else:                                        # v7: movimientos más amplios que en la v6
        move, dyaw, dpitch = tuple(np.array(move) * 1.9), dyaw * 1.8, dpitch * 1.5
    ph = (pos[0] * 0.37 + pos[2] * 0.11) % 6.28

    def cam(t, W, H):
        sy, sp = shake(t + pos[0], max(shk, 0.0011))
        sway = 0.0045 * np.sin(0.55 * t + ph)                      # respiración de cámara en el plano lateral
        bob = 0.035 * np.sin(0.9 * t + ph * 1.7)
        zoom = 1.0 + 0.018 * t                                      # empuje progresivo
        return world.Camera(W, H, min(f * 1.28, f * zoom) * W / 1920, pos + np.array(move) * t + np.array([0, bob, 0]),
                            yaw + dyaw * t + sy + sway, pitch + dpitch * t + sp)
    s = dict(biome=biome, cam=cam, animals=lambda t: [a(t) for a in actors], focus=(zf if callable(zf) else (lambda t: zf)), aperture=ap,
             wx=wx or {}, fg_spec=fg or (), through=through, actors=actors, rot=rot)
    if ripples:
        s["ripples"] = ripples
    if life_at is not None:
        s["life_at"] = life_at
    return s


def track(biome, a, cam=(5, -9, 1.0), f=5000, v=0.58, u=0.5, tgt=(0.0, 0.36), ap=0.02, wx=None, fg=None, extra=(), pan=1.0, rot=None,
          tnom=4.0, shk=0.0004, through=False, ripples=None, zf=None):
    """Cámara fija en un trípode que sigue (pan) al actor 'a'. cam = (lado, adelante, altura) respecto del animal."""
    D = unit(a.ang)
    S = np.array([D[1], -D[0]])
    pm = a.pos(tnom)
    cp = np.array([pm[0] + S[0] * cam[0] + D[0] * cam[1], cam[2], pm[2] + S[1] * cam[0] + D[1] * cam[1]])
    sc = a.spec["scale"]

    def camf(t, W, H):
        ff = f * W / 1920
        p = a.pos(tnom + (t - tnom) * pan)
        target = p + np.array([D[0] * tgt[0] * sc, tgt[1] * sc, D[1] * tgt[0] * sc])
        tt = t - tnom
        orb = 0.55 * np.sin(0.42 * tt)                                                       # órbita lateral suave alrededor del animal
        cpt = (cp + np.array([S[0], 0.0, S[1]]) * (0.30 * tt + orb) + np.array([D[0], 0.0, D[1]]) * 0.22 * tt
               + np.array([0.0, 0.06 * np.sin(0.7 * tt), 0.0]))                              # dolly + órbita + leve grúa
        ff = ff * float(np.clip(1.0 + 0.030 * tt, 0.85, 1.35))                              # empuje de lente
        yaw, pitch = aim(W, H, ff, cpt, target, v, u)
        sy, sp = shake(t + cp[0], shk)
        return world.Camera(W, H, ff, cpt, yaw + sy, pitch + sp)
    s = dict(biome=biome, cam=camf, animals=lambda t: [x(t) for x in extra] + [a(t)],
             focus=zf or (lambda t: float(np.hypot(*(a.pos(t)[[0, 2]] - cp[[0, 2]])))), aperture=ap, wx=wx or {}, fg_spec=fg or (),
             through=through, actors=(a,) + tuple(extra), life_at=pm, rot=rot)
    if ripples:
        s["ripples"] = ripples
    return s


def gfx(fn, native=False, **kw):
    return dict(gfx=lambda t, W, H, dur: fn(t, W, H, dur=dur, **kw), native=native)


_SEED = 0


def finalize(shot, dur):
    """Calcula despejes de vegetación y coloca las plantas de primer plano."""
    if "gfx" in shot or "keep" in shot:
        return
    global _SEED
    _SEED += 1
    shot.setdefault("seed", _SEED)
    W, H = 1280, 720
    keep = []
    c0 = shot["cam"](0.0, W, H)
    for t in np.linspace(0, dur, 7):
        c = shot["cam"](t, W, H)
        keep.append((c.pos[0], c.pos[2], 0.5 if shot["through"] else 1.1))
        for s_ in (2.0, 4.5, 7.0, 10.0, 14.0):                      # pasillo despejado frente a la cámara
            keep.append((c.pos[0] + np.sin(c.yaw) * s_, c.pos[2] + np.cos(c.yaw) * s_, 0.9 + 0.06 * s_))
        for i, a in enumerate(shot.get("actors", ())):
            p = a.pos(t)
            keep.append((p[0], p[2], 0.35 + 0.75 * a.spec["scale"] ** 0.6))
            if i == 0 and not shot["through"]:
                for s in (0.15, 0.3, 0.45, 0.6, 0.75, 0.88):
                    keep.append((c.pos[0] + (p[0] - c.pos[0]) * s, c.pos[2] + (p[2] - c.pos[2]) * s, 0.9))
    shot["keep"] = keep
    fg = []
    for i, (kind, var, ub, vb, d, hf) in enumerate(shot.get("fg_spec", ())):
        sp = engine.LIB[kind][var % len(engine.LIB[kind])]
        hm = sp["a"].shape[0] / sp["ppm"]
        xc = (ub - 0.5) * W / c0.f * d
        fg.append(dict(kind=kind, var=var, x=c0.pos[0] + np.cos(c0.yaw) * xc + np.sin(c0.yaw) * d, z=c0.pos[2] - np.sin(c0.yaw) * xc + np.cos(c0.yaw) * d,
                       y=c0.pos[1] - (vb * H - c0.vh) / c0.f * d, sc=hf * H * d / (c0.f * hm), ph=1.7 * i, flip=bool(i % 2)))
    shot["fg"] = fg


# plantas pegadas a la cámara: (tipo, variante, u, v de la base, distancia m, alto en fracción de cuadro)
FG_L = [("fern", 1, 0.06, 1.18, 0.9, 0.80), ("horsetail", 2, 0.16, 1.10, 1.3, 0.75)]
FG_R = [("fern", 3, 0.95, 1.20, 0.9, 0.85), ("lycopsid", 2, 0.84, 1.08, 1.2, 0.5)]
FG_LR = FG_L + FG_R
FG_REED = [("horsetail", 1, 0.05, 1.05, 1.0, 1.0), ("horsetail", 4, 0.93, 1.08, 1.1, 1.05), ("horsetail", 6, 0.78, 1.12, 1.6, 0.8)]
FG_BRANCH = [("branch", 0, 0.20, 0.42, 0.8, 0.55), ("branch", 2, 0.90, 0.30, 0.9, 0.5)]
FG_BRANCH_R = [("branch", 1, 0.86, 0.38, 0.8, 0.6)]
FG_LOW = [("lycopsid", 1, 0.12, 1.10, 0.8, 0.45), ("fern", 5, 0.88, 1.22, 1.0, 0.7), ("lycopsid", 4, 0.55, 1.16, 0.7, 0.3)]
FG_FRAME_R = [("outcrop", 1, 0.97, 1.10, 5.0, 0.60), ("rama_alta", 0, 0.80, 0.30, 0.8, 0.55), ("hongo", 2, 0.12, 1.12, 0.45, 0.16)]
FG_FRAME_L = [("outcrop", 3, 0.03, 1.10, 5.5, 0.58), ("rama_alta", 2, 0.22, 0.28, 0.8, 0.5), ("hongo", 4, 0.88, 1.12, 0.45, 0.14)]
FG_DRY = [("horsetail_dry", 1, 0.07, 1.06, 1.0, 0.9), ("fern_dry", 2, 0.93, 1.2, 0.9, 0.7)]

