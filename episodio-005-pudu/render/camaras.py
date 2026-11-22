"""Ayudas de cámara y actores (extraídas de documental.py del ep. Gorgonops)."""
import numpy as np
import world


def unit(a):
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
    return f


# ---- planos
def land(biome, pos, yaw, f=1450, pitch=0.012, move=(0, 0, 0), dyaw=0.0, dpitch=0.0, zf=60.0, ap=0.0015, wx=None, fg=None, rot=None,
         shk=0.0009, actors=(), ripples=None, through=True, life_at=None):
    pos = np.array(pos, float)
    if not any(move) and dyaw == 0.0:            # nunca una cámara quieta: deriva lenta
        move, dyaw = (0.07, 0.0, 0.09), 0.006

    def cam(t, W, H):
        sy, sp = shake(t + pos[0], shk)
        return world.Camera(W, H, f * W / 1920, pos + np.array(move) * t, yaw + dyaw * t + sy, pitch + dpitch * t + sp)
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
        cpt = cp + np.array([S[0], 0.0, S[1]]) * 0.10 * (t - tnom) + np.array([D[0], 0.0, D[1]]) * 0.06 * (t - tnom)   # dolly lento
        yaw, pitch = aim(W, H, ff, cpt, target, v, u)
        sy, sp = shake(t + cp[0], shk)
        return world.Camera(W, H, ff, cpt, yaw + sy, pitch + sp)
    s = dict(biome=biome, cam=camf, animals=lambda t: [x(t) for x in extra] + [a(t)],
             focus=zf or (lambda t: float(np.hypot(*(a.pos(t)[[0, 2]] - cp[[0, 2]])))), aperture=ap, wx=wx or {}, fg_spec=fg or (),
             through=through, actors=(a,) + tuple(extra), life_at=pm, rot=rot)
    if ripples:
        s["ripples"] = ripples
    return s

