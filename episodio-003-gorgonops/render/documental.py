#!/usr/bin/env python3
"""Documental completo: tabla de escenas y planos, tiempos, subtítulos y render por capítulos.

  python3 documental.py --tiempos            -> duración de cada escena y total
  python3 documental.py --preview DIR        -> un fotograma por plano (revisión rápida)
  python3 documental.py --cap 0 1 2 ...      -> renderiza capítulos a ../video/master-720p/
  python3 documental.py --srt                -> escribe los .srt (uno por capítulo y el completo)
"""
import argparse
import os
import shutil
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
import world
import engine
import biomes
import creature as C
import graficos as G
import sombra

FPS = 24
AQUI = Path(__file__).resolve().parent
VIDEO = AQUI.parent / "video"
GOR, PRO, DII, PAR, THR, ANF = C.GORGONOPS, C.PROCYNOSUCHUS, C.DIICTODON, C.PAREIASAUR, C.THRINAXODON, C.ANFIBIO


# ============================================================ utilidades de cámara y actores
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

QUOTES = {
    "ang1": ("Ken Angielczyk", "Paleontólogo · Field Museum, Chicago",
             "Gorgonopsians are more closely related to mammals than they are to any other living animals.",
             "Los gorgonópsidos están más emparentados con los mamíferos que con cualquier otro animal vivo."),
    "ang2": ("Ken Angielczyk", "Paleontólogo · Field Museum, Chicago",
             "Before the time of dinosaurs, there was an age of ancient mammal relatives.",
             "Antes de la época de los dinosaurios hubo una era de antiguos parientes de los mamíferos."),
    "whitney": ("Megan Whitney", "Bióloga · Universidad de Washington (2016)",
                "Most synapsids are extinct, and we — that is, mammals — are their only living descendants.",
                "La mayoría de los sinápsidos se han extinguido, y nosotros —es decir, los mamíferos— somos sus únicos descendientes vivos."),
    "viglietti": ("Pia Viglietti", "Paleontóloga · Field Museum, Chicago",
                  "All the big top predators in the Late Permian in South Africa went extinct well before the end-Permian mass extinction.",
                  "Todos los grandes depredadores del Pérmico tardío de Sudáfrica se extinguieron bastante antes de la extinción masiva del final del Pérmico."),
    "kammerer": ("Christian Kammerer", "Paleontólogo · North Carolina Museum of Natural Sciences",
                 "Permian synapsids included our own ancestors, and not nearly enough people know about this.",
                 "Entre los sinápsidos del Pérmico estaban nuestros propios antepasados, y no hay ni de lejos suficiente gente que lo sepa."),
    "darwin": ("Charles Darwin", "El origen de las especies, 1859 · frase final",
               "…from so simple a beginning endless forms most beautiful and most wonderful have been, and are being, evolved.",
               "…a partir de un comienzo tan sencillo han evolucionado, y siguen evolucionando, infinidad de formas, las más bellas y las más maravillosas."),
}
QDUR = 12.0

CHAPTERS = ["00-prologo", "01-un-animal", "02-un-cuerpo-que-ensaya", "03-los-vecinos", "04-el-mundo-se-mueve", "05-el-giro", "06-el-legado", "07-epilogo"]


def N(t):
    return ("nar", t)


def SIL(s):
    return ("sil", s)


def Q(k):
    return ("quote", k)


def build():
    """Devuelve la lista de escenas: dict(cap, nombre, items, shots=[(peso, plano)])."""
    NIGHT, DUSK, NOON, RAIN = biomes.NIGHT, biomes.DUSK, biomes.NOON, biomes.RAIN
    zb = lambda x, dry=0.0: bank_z(x, dry)
    sc = []

    def scene(cap, name, items, shots):
        from guion_extra import EXTRA, SIL_MAX, VIS_MAX
        extra = sorted(EXTRA.get(name, []), key=lambda e: e[0])
        out, k, e = [], 0, 0
        while e < len(extra) and extra[e][0] == 0:
            out.append(N(extra[e][1]))
            e += 1
        for kind, val in items:
            if kind == "sil":
                val = min(val, SIL_MAX)
            elif kind == "vis" and name in VIS_MAX:
                val = min(val, VIS_MAX[name])
            out.append((kind, val))
            if kind == "nar":
                k += 1
                while e < len(extra) and extra[e][0] == k:
                    out.append(N(extra[e][1]))
                    e += 1
        sc.append(dict(cap=cap, name=name, items=out, shots=shots))

    # --- actores recurrentes en la ribera
    walk_b = actor(GOR, (-2.0, 8.6), np.arctan2(-0.28, -0.96))                 # camina por la orilla hacia la izquierda
    walk_r = actor(GOR, (-22.0, 8.2), np.arctan2(0.10, 0.99))                  # hacia la derecha
    cfwd = np.array([-0.72, 0.69]) / np.hypot(0.72, 0.69)
    cz = next(z for z in np.arange(6, 16, 0.025) if dist_at(-14.0 + cfwd[0] * 0.86, z + cfwd[1] * 0.86) < -0.10)
    drink_pos = (-14.0, cz)
    drink_ang = np.arctan2(cfwd[1], cfwd[0])
    snout = (drink_pos[0] + cfwd[0] * 0.93, drink_pos[1] + cfwd[1] * 0.93)
    rip = lambda t: [(snout[0], snout[1], t0, 0.9) for t0 in np.arange(1.9, 5.6, 0.48)]
    riplong = lambda t: [(snout[0], snout[1], t0, 0.9) for t0 in np.arange(1.9, 30, 0.48)]
    drinker = actor(GOR, drink_pos, drink_ang, speed=0, pose=p_drink())
    drinker_long = actor(GOR, drink_pos, drink_ang, speed=0, pose=p_drink(t_up=60))
    idle_b = actor(GOR, (-9.0, zb(-9.0) - 1.6), np.arctan2(0.25, -0.97), speed=0, pose=p_idle())
    DRINK_CAM = (-(-24.5 - drink_pos[0]) * 0 + 0, 0, 0)

    def drink_shot(a, f=4400, wx=None, fg=None, ripples=rip, v=0.56, u=0.54, tgt=(0.35, 0.30), biome="ribera", h=0.62, ap=0.012):
        s = track(biome, a, cam=(0, 0, h), f=f, v=v, u=u, tgt=tgt, ap=ap, wx=wx, fg=fg, ripples=ripples, pan=0.0)
        cp = np.array([-24.5, h, 8.7])
        sc_ = a.spec["scale"]

        def camf(t, W, H):
            ff = f * W / 1920
            target = np.array([drink_pos[0] + cfwd[0] * tgt[0], tgt[1], drink_pos[1] + cfwd[1] * tgt[0]])
            yaw, pitch = aim(W, H, ff, cp, target, v, u - 0.003 * t)
            sy, sp = shake(t + 11, 0.00035)
            return world.Camera(W, H, ff, cp, yaw + sy, pitch + sp)
        s["cam"] = camf
        s["focus"] = lambda t: float(np.hypot(drink_pos[0] - cp[0], drink_pos[1] - cp[2]))
        return s

    # pantano: cinodonte entre helechos, junto al tramo de río que corre al fondo
    mx = bank_x(44.0)
    cyn_a = actor(PRO, (mx - 2.2, 45.2), np.arctan2(-0.25, -0.97), stop=2.0, go=4.6, ss=2.0)
    cyn_b = actor(PRO, (mx - 5.5, 41.0), np.arctan2(0.30, 0.95), ss=2.0)
    gor_m = actor(GOR, (mx - 1.0, 52.5), np.arctan2(-0.22, -0.97))

    # bosque
    FX, FZ = -80.0, 100.0
    gor_f = actor(GOR, (FX + 6, FZ + 12), np.arctan2(-0.20, -0.98))
    par_f = actor(PAR, (FX - 4, FZ + 22), np.arctan2(0.05, 1.0), ss=1.5)
    dii = [actor(DII, (FX + 3.0 + dx, FZ + 9.0 + dz), a_, speed=0, pose=p_eat() if k % 2 else p_idle(look=0.5), ss=2.0)
           for k, (dx, dz, a_) in enumerate([(0, 0, 2.6), (0.9, 0.5, 0.4), (-0.7, 0.9, 3.6), (1.7, -0.3, 1.9), (-1.5, -0.2, 5.4)])]
    dii_run = [actor(DII, (FX + 3.0 + dx, FZ + 9.0 + dz), a_, speed=4.5, ss=2.0)
               for (dx, dz, a_) in [(0, 0, 2.2), (0.9, 0.5, 1.4), (-0.7, 0.9, 2.9), (1.7, -0.3, 0.9), (-1.5, -0.2, 3.3)]]
    stalker = actor(GOR, (FX + 10.5, FZ + 6.8), np.arctan2(0.28, -0.96), speed=0.22, pose=p_stalk(GOR))
    dasher = actor(GOR, (FX + 9.2, FZ + 7.2), np.arctan2(0.28, -0.96), speed=4.2)
    eater = actor(GOR, (FX + 2.0, FZ + 9.5), 2.2, speed=0, pose=p_eat())
    sleeper = actor(GOR, (-11.0, 6.0), np.arctan2(-0.45, -0.89), speed=0, pose=p_lie(True))
    yawner = actor(GOR, (-6.0, zb(-6.0) - 2.2), np.arctan2(-0.35, -0.94), speed=0, pose=p_yawn())
    anf = actor(ANF, (-17.5, zb(-17.5) - 0.25), np.arctan2(0.6, -0.8), speed=0, pose=p_idle(look=0.1))

    # estación seca
    DRY = biomes.BIOMES["seco"]["dry"]
    dry_walk = actor(GOR, (0.0, 9.0), np.arctan2(-0.20, -0.98), speed=0.72)
    dzb = zb(-14.0, DRY)
    away = actor(GOR, (-4.0, 7.0), np.arctan2(0.93, 0.36), speed=0.8)
    dry_idle = actor(GOR, (-8.0, 7.5), np.arctan2(0.3, -0.95), speed=0, pose=p_idle(look=0.3, pitch=-0.05))

    V1 = dict(pos=(-7, 1.35, -1), yaw=0.10, move=(0.22, 0, 0.30))               # encuadre «el valle»
    V2 = dict(pos=(-12.5, 0.34, 6.6), yaw=0.42, f=1700, pitch=-0.02, move=(0.10, 0, 0.05), zf=12.0, ap=0.004)

    # ========================================================= PRÓLOGO
    scene(0, "0 · Apertura", [("vis", 15.0)], [(1.0, gfx(sombra.intro, native=True))])

    scene(0, "1 · El valle", [SIL(9), N("Hace doscientos cincuenta y cinco millones de años, este valle no tenía nombre."), SIL(4),
                              N("No había flores. No había hierba. Ningún ave cruzaba el cielo."),
                              N("Todo eso llegará mucho después. Lo que hay aquí es más antiguo: helechos, colas de caballo, y unos árboles de hojas con forma de lengua que hoy solo conocemos como huellas en la piedra."), SIL(3)],
          [(3.2, land("ribera", **V1)),
           (2.0, land("ribera", fg=FG_REED, **V2)),
           (2.0, land("ribera", (-2, 2.2, 4), 0.28, f=4300, pitch=-0.035, move=(0.05, 0, 0), zf=300, ap=0.004, shk=0.0003)),
           (2.2, land("pantano", (mx - 6.0, 0.7, 40.0), 0.55, f=1900, pitch=0.0, move=(0.06, 0, 0.10), zf=7.0, ap=0.008, fg=FG_LR)),
           (2.0, land("bosque", (FX, 1.5, FZ - 6), 0.15, f=1500, pitch=-0.05, move=(0.0, 0.03, 0.16), zf=14, ap=0.004, fg=FG_FRAME_R))])

    scene(0, "2 · Un solo continente", [N("El mundo tampoco se parece al nuestro. Casi toda la tierra firme está unida en un solo continente, Pangea."),
                                        N("Y este valle queda en su extremo sur, lejos del ecuador, donde los inviernos son fríos y los ríos crecen y se secan con las estaciones."),
                                        N("Mucho antes, hace unos trescientos millones de años, el sur de Gondwana estuvo cubierto de hielo. Sus huellas todavía están en las rocas del Karoo."), SIL(5)],
          [(1.1, land("pantano", (mx - 9.0, 1.6, 47.0), 0.9, f=5200, pitch=-0.02, zf=9.0, ap=0.02, fg=FG_FRAME_R, shk=0.0003)),
           (2.2, gfx(G.pangea, mode="valle")),
           (1.7, track("nevado", walk_b, cam=(9.5, 2.5, 1.0), f=3400, v=0.60, ap=0.010, fg=FG_L, pan=0.6, rot="KAROO · INVIERNO (hipótesis)")),
           (1.4, land("nevado", (-7, 1.35, -1), 0.10, f=1450, pitch=0.012, zf=60, fg=FG_R)),
           (1.6, land("artico", (-7, 1.35, -1), 0.10, f=1450, pitch=0.012, move=(0.1, 0, 0.1), zf=60, rot="HACE ~300 Ma · EL VALLE BAJO EL HIELO")),
           (1.3, land("artico", (-12, 0.5, 3), 0.35, f=2600, pitch=-0.02, zf=10, ap=0.008)),
           (1.7, land("ribera", (-3, 1.5, 0), 0.16, f=1900, dyaw=0.022, wx=dict(plume=0.75), zf=200))])

    scene(0, "3 · Alguien", [SIL(3), N("Y sin embargo, alguien caminaba por aquí cada mañana."), SIL(9), ("vis", 7.5)],
          [(1.6, land("pantano", (mx - 7.5, 0.30, 44.5), 1.25, f=3000, pitch=0.0, zf=6.5, ap=0.012, fg=FG_LOW, actors=(cyn_b,), shk=0.0004)),
           (2.4, track("ribera", walk_b, cam=(9.5, 6.5, 1.0), f=3400, v=0.60, u=0.55, ap=0.012, fg=FG_L, pan=0.6)),
           (1.6, gfx(G.title))])

    # ========================================================= CAP 1
    scene(1, "4 · Presentación", [SIL(3), N("Se llama Gorgonops. El nombre es nuestro, claro, y es exagerado: significa «cara de gorgona»."),
                                  N("Mide un metro y medio, quizá dos. Pesa lo que un perro grande. Tiene el cuerpo en forma de barril, la cola corta, y una cara que parece permanentemente concentrada en una sola idea: encontrar algo que comer."),
                                  ("nota", ([("ok", "1,2–2 m de largo"), ("ok", "cráneo de 22–35 cm"), ("no", "pelo: sin evidencia")], 7.0)),
                                  SIL(6), N("Es fácil mirarlo y pensar que es un animal sencillo. Vamos a pasar los próximos veinte minutos comprobando cuánto nos equivocamos."), SIL(3)],
          [(2.2, track("ribera", walk_b, cam=(11.0, 1.5, 1.0), f=5000, u=0.47)),
           (1.5, track("ribera", walk_b, cam=(5.0, -7.0, 0.8), f=4200, v=0.60, fg=FG_R)),
           (1.8, track("ribera", walk_r, cam=(13.0, 2.0, 1.5), f=1700, v=0.62, ap=0.003, pan=0.3)),
           (1.5, track("ribera", walk_b, cam=(9.0, 4.0, 0.9), f=9500, v=0.52, u=0.45, tgt=(0.75, 0.47), ap=0.03)),
           (1.2, track("ribera", walk_b, cam=(6.0, 0.5, 0.22), f=6500, v=0.66, tgt=(0.2, 0.10), ap=0.03, fg=FG_LOW)),
           (2.0, track("ribera", walk_r, cam=(8.0, 6.0, 0.7), f=3800, v=0.6, u=0.42, ap=0.014, fg=FG_REED, through=True))])

    scene(1, "5 · La mañana", [SIL(11), N("Bebe. Olfatea. Sabemos, por las cavidades de su cráneo, que el olfato era uno de sus sentidos principales."),
                               N("Probablemente este valle era, para él, sobre todo un mapa de olores."), SIL(6)],
          [(2.6, drink_shot(drinker)),
           (1.6, drink_shot(drinker_long, f=9000, tgt=(0.80, 0.20), v=0.55, u=0.5, ripples=riplong, ap=0.02)),
           (1.6, land("ribera", (-20.0, 0.25, zb(-20.0) - 1.2), 0.85, f=2300, pitch=-0.02, zf=7, ap=0.008, fg=FG_REED, wx=dict(insects=12), life_at=(-17, 0, zb(-17) + 2))),
           (2.0, drink_shot(actor(GOR, drink_pos, drink_ang, speed=0, pose=p_drink(t_up=1.0, t_in=-3)), f=5200, fg=FG_L, ripples=None))])

    scene(1, "5b · Cómo lo sabemos", [N("Todo lo que vamos a contar sale de la piedra. El primer cráneo de Gorgonops apareció en el Karoo sudafricano, y el anatomista Richard Owen lo describió en 1876."),
                                      N("Desde entonces, esa cuenca ha entregado miles de fósiles de sus parientes: es el archivo más completo que existe sobre el origen de nuestro propio linaje."),
                                      N("Cuando en este documental digamos «sabemos», habrá un hueso detrás. Cuando digamos «creemos», le estaremos avisando de que es una deducción."), SIL(2)],
          [(2.2, gfx(G.fossil)),
           (1.6, track("ribera", idle_b, cam=(8.0, 3.5, 0.9), f=8000, v=0.5, tgt=(0.7, 0.45), ap=0.03)),
           (1.6, track("ribera", idle_b, cam=(10.0, -2.0, 1.1), f=4300, fg=FG_R))])

    scene(1, "6 · Ni reptil ni mamífero", [N("Durante mucho tiempo se llamó a los animales como él «reptiles mamiferoides». Es un nombre equivocado."),
                                           N("No es un reptil. Tampoco es un mamífero."),
                                           N("Detrás de cada ojo, su cráneo tiene una única abertura. Esa abertura define a un linaje entero, los sinápsidos. Y ese linaje se separó del de los reptiles muchísimo antes de que existiera el primer dinosaurio."),
                                           Q("ang1"),
                                           N("Dicho de otro modo: si este animal tuviera que buscar a sus parientes vivos más cercanos, no los encontraría entre los lagartos ni entre los cocodrilos. Nos encontraría a nosotros."), SIL(5)],
          [(1.4, track("ribera", idle_b, cam=(7.0, 5.0, 0.8), f=9000, v=0.5, u=0.45, tgt=(0.72, 0.46), ap=0.03)),
           (2.0, gfx(G.skull, mode="fenestra")),
           (1.6, track("ribera", walk_r, cam=(6.0, 9.0, 0.9), f=4000, v=0.6, ap=0.014, fg=FG_L)),
           (1.6, land("pantano", (mx - 4.0, 0.9, 50.0), 0.35, f=2200, zf=10, ap=0.006, fg=FG_LR, wx=dict(insects=12))),
           (2.2, track("ribera", walk_b, cam=(14.0, -3.0, 1.3), f=2300, v=0.6, ap=0.004, pan=0.2, fg=FG_FRAME_L))])

    # ========================================================= CAP 2
    scene(2, "7 · Caminar", [SIL(3), N("Mírelo caminar. Las patas de adelante se abren hacia los lados. Las de atrás, en cambio, ya trabajan más debajo del cuerpo."),
                             N("Es un cuerpo que está, por así decirlo, a mitad de una frase. Ni se arrastra ni corre como lo hará un lobo. Pero para su mundo es un caminante eficaz: puede recorrer la llanura sin detenerse a cada paso."),
                             N("En lo alto del cráneo tiene, además, un pequeño orificio. Ahí se alojaba un tercer ojo. No formaba imágenes: medía la luz. Le decía a su cuerpo cuánto duraba el día y en qué estación estaba."),
                             N("Nosotros conservamos lo que queda de ese órgano, hundido en el cerebro: la glándula pineal, la que regula nuestro sueño."),
                             N("Y eso no es lo más extraño que tiene. Lo más extraño está dentro de la boca."), SIL(2)],
          [(1.6, track("ribera", walk_b, cam=(4.0, -8.5, 0.7), f=4600, v=0.6, wx=NOON)),
           (1.4, track("ribera", walk_b, cam=(7.0, 0.0, 0.2), f=7000, v=0.7, tgt=(0.0, 0.14), ap=0.03, wx=NOON)),
           (1.6, track("ribera", walk_r, cam=(5.5, 1.0, 4.2), f=2600, v=0.55, ap=0.006, wx=NOON)),
           (1.8, track("bosque", gor_f, cam=(7.0, 5.5, 0.8), f=3600, v=0.6, ap=0.014, fg=FG_LR, through=True)),
           (1.4, track("ribera", idle_b, cam=(5.0, 4.0, 1.9), f=9500, v=0.5, tgt=(0.66, 0.52), ap=0.03, wx=NOON)),
           (1.6, track("bosque", gor_f, cam=(9.0, -1.0, 1.0), f=4400, v=0.58, ap=0.02, fg=FG_FRAME_R)),
           (1.4, track("ribera", walk_b, cam=(10.0, 3.0, 1.0), f=5200, wx=NOON, fg=FG_L))])

    scene(2, "8 · Tres clases de dientes", [N("Un cocodrilo tiene decenas de dientes, y todos son, más o menos, el mismo diente repetido."), N("Él no."),
                                            N("Adelante tiene incisivos, para sujetar y arrancar. Detrás, dos caninos como sables. Y más atrás, unos pocos dientes pequeños. Tres herramientas distintas en una misma boca."),
                                            ("nota", ([("ok", "incisivos · caninos · postcaninos"), ("ok", "reemplazo dental continuo"), ("no", "apertura > 90°: estimación")], 7.5)),
                                            SIL(4), N("Abra usted la suya frente a un espejo. Incisivos. Caninos. Muelas. El plano es el mismo."),
                                            N("Puede abrir la mandíbula más de noventa grados. No mastica: muerde, arranca y traga. Y cuando un sable se rompe, otro crece en su lugar, una y otra vez."),
                                            N("Al fondo de esa mandíbula hay, además, dos huesos pequeños. Guárdelos en la memoria. Vamos a volver a ellos."), SIL(3)],
          [(1.7, track("ribera", yawner, cam=(5.5, 4.5, 0.75), f=8200, v=0.52, u=0.5, tgt=(0.72, 0.44), ap=0.03, wx=NOON)),
           (2.4, gfx(G.skull, mode="dientes")),
           (1.6, track("ribera", yawner, cam=(8.0, 0.8, 0.9), f=5600, v=0.55, u=0.45, tgt=(0.4, 0.40), ap=0.025, wx=NOON, fg=FG_R)),
           (1.4, track("ribera", actor(GOR, (-6.0, zb(-6.0) - 2.2), np.arctan2(-0.35, -0.94), speed=0, pose=p_yawn(t0=0.4)), cam=(3.5, 6.5, 0.6), f=7500, v=0.5, tgt=(0.7, 0.42), ap=0.03, wx=NOON)),
           (1.8, gfx(G.skull, mode="huesos")),
           (1.2, track("ribera", idle_b, cam=(9.0, 1.0, 1.0), f=4800, wx=NOON, fg=FG_REED, through=True))])

    scene(2, "9 · La caza", [SIL(4), N("Sus piernas son cortas. No está hecho para persecuciones largas. Creemos que cazaba como cazan hoy muchos depredadores de emboscada: esperar, acercarse, un mordisco profundo y retirarse."),
                             ("vis", 9), N("Sus presas eran los herbívoros del valle: dicinodontes como Diictodon, que vivían en madrigueras en espiral, y quizá las crías de los enormes pareiasaurios."),
                             SIL(3), N("No hay crueldad en la escena. Hay hambre, que es otra cosa."), SIL(4)],
          [(1.6, track("bosque", dii[0], cam=(4.5, 2.0, 0.28), f=4200, v=0.62, ap=0.02, wx=DUSK, extra=dii[1:], fg=FG_LOW, through=True)),
           (1.6, track("bosque", stalker, cam=(6.0, 6.0, 0.5), f=5200, v=0.58, ap=0.025, wx=DUSK, fg=FG_LR, through=True)),
           (1.0, track("bosque", dii[1], cam=(2.2, 1.6, 0.2), f=6000, v=0.55, tgt=(0.5, 0.30), ap=0.03, wx=DUSK, extra=(dii[0],))),
           (1.3, track("bosque", dasher, cam=(11.0, -7.0, 1.0), f=2700, v=0.62, ap=0.006, wx=dict(DUSK, dust=0.5), extra=dii_run, pan=0.5, tnom=1.2)),
           (1.4, land("bosque", (FX + 14, 1.2, FZ - 2), -0.75, f=2200, zf=14, ap=0.005, wx=dict(DUSK, dust=0.9), fg=FG_FRAME_R)),
           (1.8, track("bosque", eater, cam=(7.5, -6.5, 0.8), f=4600, v=0.6, ap=0.02, wx=DUSK, fg=FG_L)),
           (1.4, track("bosque", par_f, cam=(16.0, 4.0, 1.3), f=3000, v=0.6, tgt=(0, 0.3), ap=0.008, wx=DUSK, fg=FG_FRAME_L))])

    scene(2, "10 · Lo que duele igual", [SIL(4), N("En 2016, un equipo de la Universidad de Washington cortó en láminas la mandíbula de un gorgonópsido para estudiar cómo se sujetaban sus dientes."),
                                         N("Encontraron algo que no buscaban: un odontoma, un tumor benigno hecho de dientes diminutos. Tiene doscientos cincuenta y cinco millones de años. Es el mismo tumor que hoy un dentista extrae a una persona."),
                                         N("Lo que buscaban era otra cosa, igual de reveladora. En casi todos los reptiles, el diente está soldado al hueso. En los mamíferos no: lo sostiene una trama de ligamentos, firme pero flexible. El equipo quería saber de qué lado estaba Gorgonops."),
                                         N("Hay otro fósil que habla de su cuerpo: un hueso del antebrazo con una herida que cicatrizó. El hueso nuevo creció deprisa, más parecido a como sana un mamífero que a como sana un cocodrilo."),
                                         Q("whitney"), N("Compartimos con él la forma de los dientes. Y, por lo visto, también algunas de las cosas que pueden salir mal."), SIL(6)],
          [(1.8, track("ribera", sleeper, cam=(7.0, 2.5, 0.6), f=4800, v=0.6, tgt=(0.1, 0.2), ap=0.02, wx=NIGHT, fg=FG_L)),
           (2.2, gfx(G.odontoma)),
           (1.6, land("ribera", (-9, 1.3, -2), 0.2, f=1500, pitch=-0.06, move=(0.1, 0, 0.1), wx=NIGHT, zf=80)),
           (1.6, track("ribera", sleeper, cam=(4.5, 4.5, 0.4), f=8000, v=0.55, tgt=(0.7, 0.2), ap=0.03, wx=NIGHT)),
           (1.6, land("pantano", (mx - 5.0, 0.6, 43.0), 0.6, f=2000, zf=8, ap=0.008, wx=NIGHT, fg=FG_REED)),
           (1.8, track("ribera", sleeper, cam=(11.0, 0.0, 1.4), f=2600, v=0.6, ap=0.006, wx=NIGHT, fg=FG_FRAME_L))])

    # ========================================================= CAP 3
    scene(3, "11 · El valle habitado", [SIL(4), N("Ningún animal vive solo. A su alrededor hay todo un mundo, y casi nada de él nos resultaría familiar."),
                                        N("No hay mamíferos. No hay dinosaurios: faltan más de veinte millones de años para el primero. Los grandes herbívoros son parientes suyos con pico de tortuga, o reptiles acorazados del tamaño de una vaca."),
                                        SIL(6), Q("ang2"),
                                        N("Hasta los árboles cuentan algo. Las hojas de Glossopteris aparecen fosilizadas en Sudamérica, en África, en la India, en Australia y en la Antártida."),
                                        N("Durante décadas nadie supo explicar cómo un mismo árbol había cruzado tantos océanos. No los cruzó. Los océanos todavía no estaban ahí."), SIL(3)],
          [(1.8, track("bosque", par_f, cam=(13.0, 3.0, 1.2), f=3400, v=0.6, tgt=(0, 0.3), ap=0.01, fg=FG_LR, through=True)),
           (1.3, track("bosque", dii[0], cam=(3.0, 1.5, 0.22), f=5200, v=0.6, ap=0.025, extra=dii[1:3], fg=FG_LOW)),
           (1.5, land("pantano", (mx - 2.5, 0.22, 38.0), 0.5, f=2600, pitch=-0.03, zf=6, ap=0.01, wx=dict(insects=16), fg=FG_REED, life_at=(mx + 1.5, 0, 43))),
           (1.3, track("ribera", anf, cam=(3.2, 1.2, 0.18), f=5000, v=0.6, tgt=(0.2, 0.25), ap=0.03, fg=FG_REED, through=True)),
           (1.7, land("ladera", (96, 7.5, 150), -1.15, f=1400, pitch=0.11, move=(0, 0, 0.12), zf=120, fg=FG_FRAME_L)),
           (1.6, land("bosque", (FX - 6, 1.3, FZ + 2), 0.25, f=1500, move=(0.02, 0, 0.22), zf=12, ap=0.004, fg=FG_LR)),
           (1.7, track("selva", actor(PRO, (mx - 3.0, 46.0), np.arctan2(-0.25, -0.97), ss=2.0), cam=(2.6, 2.4, 0.30), f=3600, v=0.60, ap=0.02, fg=FG_LOW + FG_L, through=True, rot="CATASIA · TRÓPICO")),
           (1.5, track("desierto", walk_b, cam=(11.0, 1.5, 1.0), f=4500, u=0.47, rot="INTERIOR DE PANGEA")),
           (1.4, land("pantano", (mx - 8.0, 1.0, 55.0), 0.8, f=2000, zf=10, ap=0.006, wx=RAIN, fg=FG_L)),
           (1.4, gfx(G.leaf_fossil)),
           (2.0, gfx(G.pangea, mode="glosso"))])

    scene(3, "12 · El pequeño", [SIL(4), N("Y entre todos ellos, hay uno que casi nadie ve."),
                                 N("Mide medio metro. Se llama Procynosuchus. Come insectos y lo que puede. Pasa buena parte de su vida escondiéndose de animales como el nuestro."),
                                 SIL(4), N("No tiene nada de especial. Todavía."), SIL(8)],
          [(1.6, track("pantano", cyn_b, cam=(2.6, 2.4, 0.16), f=4200, v=0.6, ap=0.03, fg=FG_LOW, through=True)),
           (2.4, track("pantano", cyn_a, cam=(3.0, 0.6, 0.38), f=1900, v=0.66, u=0.5, ap=0.0085, extra=(gor_m,), pan=0.0, tnom=3.0, zf=lambda t: 3.0, fg=FG_L)),
           (1.4, track("pantano", actor(PRO, (mx - 3.0, 46.0), 2.9, speed=0, pose=p_sniff(), ss=2.2), cam=(1.6, 1.5, 0.14), f=6000, v=0.52, tgt=(0.55, 0.30), ap=0.035)),
           (1.4, track("pantano", cyn_b, cam=(1.5, -3.0, 0.2), f=3600, v=0.6, ap=0.02, fg=FG_LR, through=True)),
           (2.0, land("ribera", fg=FG_REED, wx=dict(dry=1.1, cracks=0.6, mist=0.25), **V2))])

    # ========================================================= CAP 4
    scene(4, "13 · La estación seca", [SIL(6), N("Las sequías son parte de su vida. Los ríos de este valle siempre crecieron y se secaron con las estaciones."),
                                       N("Pero las capas de roca de esta región cuentan que, hacia el final de su tiempo, algo empezó a cambiar. Las sequías se hicieron más largas. Los ríos, más violentos y más breves."),
                                       SIL(5), N("Él no puede saberlo. Solo nota que hay que caminar más para encontrar agua."), SIL(5)],
          [(2.4, land("seco", **V1)),
           (1.6, land("seco", fg=FG_DRY, **V2)),
           (1.8, track("seco", dry_walk, cam=(11.0, 1.5, 1.0), f=5000, u=0.47)),
           (1.3, land("seco", (4, 1.6, 24), -0.2, f=4200, pitch=-0.06, zf=40, ap=0.008, wx=dict(leaves=60), shk=0.0004)),
           (1.6, track("seco", dry_walk, cam=(6.0, -8.0, 0.5), f=3600, v=0.62, fg=FG_DRY, ap=0.012)),
           (1.5, land("seco", (-10, 0.3, 9.5), 0.2, f=2400, pitch=0.03, zf=4, ap=0.01, fg=FG_DRY)),
           (1.8, track("seco", actor(GOR, (-14.0, dzb - 0.55), np.pi / 2 - 0.25, speed=0, pose=p_drink(t_up=60)), cam=(8.0, 4.0, 0.6), f=4600, v=0.58, ap=0.014,
                       ripples=lambda t: [(-14.0 + 0.2, dzb + 0.35, t0, 0.8) for t0 in np.arange(1.9, 30, 0.5)]))])

    scene(4, "14 · La bruma tenía dueño", [N("¿Recuerda la bruma del horizonte?"),
                                           N("Al otro lado del continente, en lo que hoy es Siberia, la Tierra se está abriendo. No un volcán: una región entera, del tamaño de Europa occidental, derramando lava durante cientos de miles de años."),
                                           N("Los gases que salen de ahí están cambiando el aire, la lluvia y la temperatura de todo el planeta."),
                                           N("Lo que viene se conoce como la extinción del final del Pérmico, la mayor que ha registrado la vida: desaparecerá la gran mayoría de las especies del mar y buena parte de las de tierra firme."),
                                           ("nota", ([("no", "≈ 252 Ma: extinción del Pérmico"), ("no", "gorgonópsidos: desaparecen"), ("ok", "cinodontes: sobreviven")], 8.0)),
                                           Q("viglietti"), N("Los grandes cazadores cayeron primero. Siempre pasa: son pocos, crecen despacio, y dependen de que todo lo que está debajo de ellos funcione."), SIL(8)],
          [(2.0, track("seco", dry_idle, cam=(12.0, -2.0, 0.9), f=1900, v=0.80, ap=0.003, wx=dict(plume=1.0), pan=0.0)),
           (2.6, gfx(G.pangea, mode="siberia")),
           (1.6, land("ladera", (98, 8.0, 160), -1.25, f=1500, pitch=0.10, wx=dict(plume=1.0, dust=0.5, plume_az=-1.2), zf=150)),
           (1.6, land("seco", (-3, 1.5, 0), 0.30, f=2600, pitch=-0.05, dyaw=0.012, wx=dict(plume=1.0), zf=200)),
           (1.6, track("seco", dry_idle, cam=(6.0, 4.0, 0.8), f=7500, v=0.5, tgt=(0.7, 0.46), ap=0.03, wx=dict(plume=1.0))),
           (1.8, land("seco", (-16, 1.2, 2), 0.5, f=1700, move=(0.1, 0, 0.05), wx=dict(plume=1.0, dust=0.9), fg=FG_DRY)),
           (1.6, track("desierto", walk_r, cam=(8.0, 6.0, 0.9), f=3600, u=0.45, wx=dict(plume=0.8), rot="INTERIOR DE PANGEA")),
           (1.4, land("desierto", (-10, 1.4, 0), 0.20, f=1700, pitch=0.01, wx=dict(plume=0.8), zf=80))])

    # ========================================================= CAP 5
    scene(5, "15 · La rama que termina", [SIL(4), N("Hasta aquí le hemos contado esta historia como si él fuera el comienzo de algo."), SIL(2), N("No lo es."), SIL(5),
                                          N("Los gorgonópsidos no dejaron descendientes. Ni uno. Su linaje entero termina en esta crisis, hace doscientos cincuenta y dos millones de años. Ningún animal vivo lleva su sangre."),
                                          SIL(6), N("El futuro estaba en otra parte. Estaba en el animal pequeño que se escondía entre los helechos."),
                                          N("Los cinodontes, su grupo, son primos de Gorgonops: comparten un antepasado. Y de todos los primos, fueron ellos los que cruzaron al otro lado. Pequeños, capaces de refugiarse bajo tierra, de comer casi cualquier cosa."),
                                          N("De ellos, decenas de millones de años después, saldrán los primeros mamíferos."),
                                          ("nota", ([("ok", "cinodontes → mamíferos"), ("no", "gorgonópsidos: sin descendientes")], 7.0)),
                                          N("En las rocas que vienen justo después de la catástrofe, en este mismo valle, los paleontólogos encuentran una y otra vez la misma escena: un cinodonte del tamaño de un gato, Thrinaxodon, fosilizado dentro de su madriguera, enroscado sobre sí mismo."),
                                          N("El mundo de arriba se había vuelto inhabitable. Ellos lo esperaron abajo."), Q("kammerer"), SIL(3)],
          [(2.6, track("seco", away, cam=(-2.0, -9.0, 1.3), f=1800, v=0.60, ap=0.003, wx=dict(plume=1.0, dust=0.7), pan=0.0, tnom=3.0)),
           (2.4, gfx(G.tree, mode="corte")),
           (1.6, land("extincion", (-7, 1.35, -1), 0.10, move=(0.1, 0, 0.12))),
           (1.8, track("pantano", cyn_a, cam=(3.0, 0.6, 0.38), f=3000, v=0.62, ap=0.012, pan=1.0, tnom=3.0, fg=FG_L)),
           (2.0, gfx(G.tree, mode="heredero")),
           (1.5, track("pantano", cyn_b, cam=(3.0, 1.0, 0.2), f=5200, v=0.58, tgt=(0.3, 0.3), ap=0.03, fg=FG_LOW, through=True)),
           (1.6, land("extincion", fg=(), **V2)),
           (2.4, gfx(G.burrow)),
           (1.6, land("extincion", (-3, 1.5, 0), 0.3, f=2400, pitch=-0.04, dyaw=0.01, zf=200)),
           (2.2, track("pantano", actor(PRO, (mx - 3.0, 46.0), 2.9, speed=0, pose=p_idle(look=0.5), ss=2.2), cam=(2.4, 1.2, 0.2), f=4200, v=0.58, ap=0.03, fg=FG_LR, through=True))])

    scene(5, "16 · Los huesos que escuchan", [N("¿Recuerda los dos huesos del fondo de la mandíbula?"),
                                              N("En Gorgonops, y en todos sus parientes, servían para articular la boca. En el linaje de los cinodontes, a lo largo de millones de años, esos huesos se fueron haciendo más pequeños. Se soltaron de la mandíbula. Y terminaron en otro lugar."),
                                              N("Hoy se llaman martillo y yunque. Están dentro de su oído. Con ellos está escuchando esta frase."), SIL(6),
                                              N("No hace falta creerlo por los fósiles. En cada embrión de mamífero, también en el nuestro, esos huesecillos empiezan a formarse pegados a la mandíbula, y solo después se separan."),
                                              N("Gorgonops no nos dio esos huesos. Pero los tenía. Mirarlo a él es mirar cómo era nuestra familia antes de que nada de esto ocurriera."), SIL(4)],
          [(0.9, gfx(G.skull, mode="huesos")),
           (5.2, gfx(G.jaw_to_ear)),
           (1.4, land("pantano", (mx - 3.0, 0.25, 41.0), 0.55, f=2600, pitch=-0.02, zf=5, ap=0.01, fg=FG_REED, wx=dict(insects=12), ripples=lambda t: [(mx + 1.2, 44.0, t0, 0.5) for t0 in (0.5, 3.2, 6.1)])),
           (2.0, track("ribera", idle_b, cam=(7.0, 5.0, 0.8), f=9000, v=0.5, u=0.45, tgt=(0.72, 0.46), ap=0.03))])

    # ========================================================= CAP 6
    scene(6, "17 · Las formas sin fin", [SIL(4), N("Doscientos cincuenta millones de años es una cifra que no se puede sentir. Probemos así: si cada año fuera un paso, habría que dar más de cuatro vueltas a la Tierra para llegar desde aquel valle hasta hoy."),
                                         N("En esos pasos, el pequeño animal de los helechos se convirtió en todo esto. En algo que vuela de noche. En algo que canta bajo el agua. En algo que mira hacia atrás y se pregunta de dónde viene."),
                                         N("Ninguno de esos pasos fue grande. Un diente un poco distinto. Un hueso un poco más pequeño. Una cría que sobrevive un invierno más."),
                                         Q("darwin"), N("Darwin escribió eso sin haber visto nunca un fósil de Gorgonops. No le hizo falta."), SIL(6)],
          [(1.6, land("ladera", (94, 9.0, 140), -1.1, f=1300, pitch=0.12, move=(0, 0, 0.2), zf=150)),
           (3.4, gfx(G.tree, mode="legado")),
           (1.4, land("bosque", (FX + 2, 1.4, FZ + 30), -0.4, f=1600, move=(0.05, 0, 0.2), zf=12, ap=0.004, fg=FG_LR)),
           (1.4, land("pantano", (mx - 6.0, 0.5, 60.0), 0.7, f=2000, zf=8, ap=0.007, wx=dict(insects=14), fg=FG_REED)),
           (2.2, gfx(G.prints)),
           (1.6, land("ribera", (-2, 2.2, 4), 0.28, f=4300, pitch=-0.035, zf=300, ap=0.004, wx=DUSK, shk=0.0003)),
           (1.4, land("selva", (mx - 7.5, 0.55, 44.0), 1.15, f=2200, pitch=0.0, zf=8.0, ap=0.012, fg=FG_LR, rot="CATASIA · TRÓPICO")),
           (1.2, land("nevado", (-7, 1.35, -1), 0.30, f=1700, pitch=0.01, zf=60, fg=FG_R, rot="KAROO · INVIERNO")),
           (1.2, land("artico", (-9, 1.2, 0), 0.60, f=1700, pitch=0.01, zf=60, rot="HIELO")),
           (2.0, land("ribera", wx=DUSK, **V1))])

    # ========================================================= EPÍLOGO
    cyn_far = actor(PRO, (-11.0, cz + 0.4 - 3.6), np.arctan2(0.05, -1.0), ss=2.0)
    leave = actor(GOR, (drink_pos[0] - 0.5, drink_pos[1] - 1.2), np.arctan2(-0.12, -0.99), speed=0.85)
    scene(7, "18 · Simplemente vivía", [SIL(12), N("Volvamos a él."),
                                        N("Ya sabemos cómo termina su historia. Sabemos que su familia no llegó al otro lado, y que el futuro pasó junto a él sin que lo notara."),
                                        N("Él no sabe nada de eso."), SIL(5),
                                        N("No sabe que su boca se parece a la nuestra. No sabe qué son los huesos del oído, ni qué es un mamífero, ni qué es el futuro. No estaba intentando llegar a ninguna parte."),
                                        N("Tenía sed, y vino al río."), SIL(6),
                                        N("A veces contamos la evolución como si fuera una carrera con una meta. No lo es. Nadie corría. Había un animal grande y un animal pequeño, cada uno ocupado en su mañana."),
                                        N("Uno de los dos resultó ser nuestro antepasado. El otro, no."),
                                        N("Ninguno lo supo nunca. Y los dos estuvieron, exactamente igual, vivos."), SIL(9),
                                        N("La vida no necesita conocer su destino para hacer cosas extraordinarias."), N("Le basta con seguir."), SIL(12), ("vis", 18)],
          [(2.0, land("ribera", **V1)),
           (2.6, drink_shot(drinker_long, ripples=riplong)),
           (1.4, drink_shot(drinker_long, f=9000, tgt=(0.80, 0.20), v=0.55, u=0.5, ripples=riplong, ap=0.02)),
           (2.2, track("ribera", drinker_long, cam=(4.0, -9.5, 0.9), f=2600, v=0.62, ap=0.006, ripples=riplong, extra=(cyn_far,), fg=FG_L, tgt=(0.3, 0.3))),
           (1.4, track("ribera", cyn_far, cam=(2.5, -4.0, 0.25), f=4200, v=0.6, ap=0.03, fg=FG_REED, through=True)),
           (2.0, drink_shot(actor(GOR, drink_pos, drink_ang, speed=0, pose=p_drink(t_up=1.0, t_in=-3)), f=5200, ripples=None)),
           (2.6, track("ribera", leave, cam=(12.0, 1.0, 1.2), f=2400, v=0.62, ap=0.005, pan=0.0, tnom=5.0)),
           (2.2, land("ribera", (-17.0, 0.25, zb(-17.0) - 1.0), 0.75, f=2600, pitch=-0.03, zf=6, ap=0.008, fg=FG_REED,
                      ripples=lambda t: [(snout[0], snout[1], t0, 0.5) for t0 in (-3.0, -1.5, 0.0)], life_at=(snout[0], 0, snout[1]))),
           (2.6, gfx(sombra.creditos, native=True))])
    return sc


# ============================================================ tiempos y subtítulos
WPS = 1.95          # palabras por segundo de la narración prevista


def chunks(text, maxc=84):
    """Parte una narración en subtítulos de hasta dos líneas."""
    import re
    parts = re.split(r"(?<=[.?!:])\s+", text.strip())
    out = []
    for p in parts:
        while len(p) > maxc:
            cut = max(p.rfind(", ", 0, maxc), p.rfind("; ", 0, maxc))
            if cut < 30:
                cut = p.rfind(" ", 0, maxc)
            out.append(p[:cut + 1].strip())
            p = p[cut + 1:].strip()
        if out and len(out[-1]) + len(p) + 1 <= 56 and not out[-1].endswith((".", "?", "!")):
            out[-1] += " " + p
        else:
            out.append(p)
    return out


def two_lines(s, maxl=46):
    if len(s) <= maxl:
        return s
    mid = len(s) // 2
    cands = [i for i, ch in enumerate(s) if ch == " "]
    i = min(cands, key=lambda i: abs(i - mid))
    return s[:i] + "\n" + s[i + 1:]


VOZ_JSON = Path(__file__).resolve().parents[2] / "voice_ai" / "duraciones.json"
GAP_VOZ = 0.55          # respiro tras cada párrafo
LEAD_VOZ = 0.15


def clave_voz(texto):
    import hashlib
    return hashlib.sha1(texto.encode("utf-8")).hexdigest()[:12]


def texto_cita(k):
    a, rol, _en, es = QUOTES[k]
    return f"{a}, {rol.split('·')[0].strip().lower()}, dice: {es}"


def cargar_voz():
    import json
    try:
        return json.loads(VOZ_JSON.read_text())
    except Exception:
        return {}


def timeline(scenes):
    """Asigna tiempos: escenas, planos, subtítulos y citas. Tiempos relativos al capítulo.
    Si hay duraciones reales de voz (voice_ai/duraciones.json), la película se arma a partir de ellas."""
    voz = cargar_voz()
    caps = {}
    for s in scenes:
        c = caps.setdefault(s["cap"], dict(t=0.0, shots=[], subs=[], quotes=[], notes=[], scenes=[], voz=[]))
        t0 = c["t"]
        t = t0
        for kind, val in s["items"]:
            if kind in ("sil", "vis"):
                t += val
            elif kind == "nota":
                c["notes"].append((t + 0.3, val[1], val[0]))
            elif kind == "quote":
                v = voz.get(clave_voz(texto_cita(val)))
                qd = (v + 1.4) if v else QDUR
                c["quotes"].append((t + 0.4, qd - 0.8, val))
                if v:
                    c["voz"].append((t + 0.4 + LEAD_VOZ, v, clave_voz(texto_cita(val))))
                t += qd
            else:
                v = voz.get(clave_voz(val))
                if v:
                    ch = chunks(val)
                    pal = [max(1, len(x.split())) for x in ch]
                    tot = float(sum(pal))
                    a = t + LEAD_VOZ
                    for x, p in zip(ch, pal):
                        b = a + v * p / tot
                        c["subs"].append((a, b - 0.04, two_lines(x)))
                        a = b
                    c["voz"].append((t + LEAD_VOZ, v, clave_voz(val)))
                    t += LEAD_VOZ + v + GAP_VOZ
                else:
                    for ch in chunks(val):
                        d = max(1.7, len(ch.split()) / WPS + 0.35)
                        c["subs"].append((t, t + d - 0.15, two_lines(ch)))
                        t += d
                    t += 0.7
        dur = t - t0
        wsum = sum(w for w, _ in s["shots"])
        ts = t0
        for w, shot in s["shots"]:
            d = round(dur * w / wsum * FPS) / FPS
            c["shots"].append((ts, d, shot, s["name"]))
            ts += d
        c["t"] = ts
        c["scenes"].append((s["name"], t0, ts - t0))
    return caps


SC = None
TL = None


def init():
    global SC, TL
    cv2.setNumThreads(1)
    engine.setup()
    SC = build()
    TL = timeline(SC)
    for c in TL.values():
        for ts, d, shot, _ in c["shots"]:
            finalize(shot, d)


def render_frame(args):
    cap, i, W, H = args
    c = TL[cap]
    t = i / FPS
    total = c["t"]
    for ts, d, shot, _ in c["shots"]:
        if ts <= t < ts + d + 1e-6:
            break
    lt = t - ts
    if "gfx" in shot:
        img = shot["gfx"](lt, W, H, d)
    else:
        img = engine.frame(shot, lt, W, H)
    if not ("gfx" in shot) and shot.get("rot"):
        img = sombra.rotulo(img, lt, d, shot["rot"])
    for nt, nd, lines in c["notes"]:
        if nt <= t < nt + nd:
            img = sombra.nota_overlay(img, t - nt, nd, lines)
    for qt, qd, key in c["quotes"]:
        if qt <= t < qt + qd:
            img = G.quote_overlay(img, t - qt, qd, *QUOTES[key])
    fade = min(1.0, t / 1.0, (total - t) / 1.0)
    return (np.clip(img * max(fade, 0), 0, 1) * 255 + 0.5).astype(np.uint8).tobytes()


def ts_srt(x):
    h, m, s = int(x // 3600), int(x % 3600 // 60), x % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)) % 1000:03d}"


def shift_srt(t, off):
    h, m, rest = t.split(":")
    s, ms = rest.split(",")
    return ts_srt(int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000 + off)


def write_srt():
    VIDEO.mkdir(exist_ok=True)
    (VIDEO / "capitulos").mkdir(exist_ok=True)
    off, n = 0.0, 1
    full = open(VIDEO / "gorgonops-completo.srt", "w", encoding="utf-8")
    for cap in sorted(TL):
        c = TL[cap]
        with open(VIDEO / "capitulos" / f"{CHAPTERS[cap]}.srt", "w", encoding="utf-8") as fh:
            for k, (a, b, txt) in enumerate(c["subs"], 1):
                fh.write(f"{k}\n{ts_srt(a)} --> {ts_srt(b)}\n{txt}\n\n")
                full.write(f"{n}\n{ts_srt(a + off)} --> {ts_srt(b + off)}\n{txt}\n\n")
                n += 1
        off += round(c["t"] * FPS) / FPS
    full.close()


def seg_path(cap, j):
    return VIDEO / "segmentos" / f"c{cap:02d}_s{j:03d}.mp4"


def render_segment(args):
    """Renderiza un plano completo a un MP4 de 1080p (reanudable: si el archivo existe, no hace nada)."""
    import time
    cap, j = args
    out = seg_path(cap, j)
    if out.exists():
        return str(out), 0.0
    ts, dd, shot, nm = TL[cap]["shots"][j]
    native = bool(shot.get("native"))
    W, H = (1920, 1080) if native else (1280, 720)
    f0, nf = int(round(ts * FPS)), int(round(dd * FPS))
    tmp = out.with_suffix(".part.mp4")
    vf = [] if native else ["-vf", "scale=1920:1080:flags=lanczos"]
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
                          + vf + ["-an", "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-threads", "2", "-pix_fmt", "yuv420p", str(tmp)], stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(f0, f0 + nf):
        ff.stdin.write(render_frame((cap, i, W, H)))
    ff.stdin.close()
    ff.wait()
    tmp.rename(out)
    return str(out), time.time() - t0


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-1500:])
        raise SystemExit(1)


def assemble(caps):
    """Une los planos de cada capítulo: copia limpia (sin audio ni subtítulos) y versión final con audio y subtítulos."""
    (VIDEO / "master").mkdir(exist_ok=True)
    (VIDEO / "capitulos").mkdir(exist_ok=True)
    finals = []
    for cap in caps:
        n = len(TL[cap]["shots"])
        files = [seg_path(cap, j) for j in range(n)]
        miss = [f.name for f in files if not f.exists()]
        if miss:
            print(f"capítulo {cap}: faltan {len(miss)} planos ({miss[:3]}…)")
            continue
        lst = VIDEO / "master" / f"{CHAPTERS[cap]}.txt"
        lst.write_text("".join(f"file '{f.resolve()}'\n" for f in files))
        master = VIDEO / "master" / f"{CHAPTERS[cap]}.mp4"
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(master)])
        wav = VIDEO / "audio" / f"{CHAPTERS[cap]}.wav"
        srt = VIDEO / "capitulos" / f"{CHAPTERS[cap]}.srt"
        out = VIDEO / "capitulos" / f"{CHAPTERS[cap]}.mp4"
        style = "FontName=Inter,Fontsize=14,PrimaryColour=&HF2F3F7&,OutlineColour=&H000000&,BorderStyle=1,Outline=1.0,Shadow=0,MarginV=2,Alignment=2"
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(master)]
        if wav.exists():
            cmd += ["-i", str(wav)]
        cmd += ["-vf", f"subtitles={srt}:original_size=1920x1080:force_style='{style}'", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p"]
        cmd += (["-c:a", "aac", "-b:a", "256k", "-shortest"] if wav.exists() else ["-an"]) + [str(out)]
        run(cmd)
        finals.append(out)
        print("listo:", out, flush=True)
    return finals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tiempos", action="store_true")
    ap.add_argument("--srt", action="store_true")
    ap.add_argument("--preview")
    ap.add_argument("--only", type=int, nargs="*")
    ap.add_argument("--seg", type=int, nargs="*", help="renderiza los planos de estos capítulos (sin argumentos: todos)")
    ap.add_argument("--assemble", type=int, nargs="*", help="une capítulos ya renderizados (sin argumentos: todos)")
    ap.add_argument("--scale", type=float, default=1280 / 1920)
    ap.add_argument("--jobs", type=int, default=3)
    a = ap.parse_args()
    W, H = int(1920 * a.scale) // 2 * 2, int(1080 * a.scale) // 2 * 2
    global SC, TL
    if a.tiempos or a.srt or a.assemble is not None:
        world.load()
        engine.setup()
        SC = build()
        TL = timeline(SC)
        if a.tiempos or a.srt:
            tot = 0
            for cap in sorted(TL):
                c = TL[cap]
                print(f"{CHAPTERS[cap]:28s} {c['t'] / 60:5.2f} min  {len(c['shots'])} planos")
                for nm, t0, dd in c["scenes"]:
                    print(f"    {nm:38s} {t0 / 60:5.2f} -> {dd:6.1f} s")
                tot += c["t"]
            print(f"TOTAL {tot / 60:.2f} min, {sum(len(c['shots']) for c in TL.values())} planos")
            if a.srt:
                write_srt()
            return
        write_srt()
        assemble(a.assemble or sorted(TL))
        return
    if a.preview:
        init()
        os.makedirs(a.preview, exist_ok=True)
        k = 0
        import time
        for cap in sorted(TL):
            for j, (ts, dd, shot, nm) in enumerate(TL[cap]["shots"]):
                k += 1
                if a.only and k not in a.only:
                    continue
                t0 = time.time()
                try:
                    buf = render_frame((cap, int((ts + dd * 0.5) * FPS), W, H))
                    img = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
                    cv2.imwrite(f"{a.preview}/{k:03d}_c{cap}_{j:02d}.jpg", img[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 88])
                    print(f"{k:03d} c{cap} {nm[:24]:24s} {dd:5.1f}s  {time.time() - t0:5.1f}s", flush=True)
                except Exception as e:
                    import traceback
                    print(f"{k:03d} c{cap} {nm} ERROR {e!r}", flush=True)
                    traceback.print_exc()
        return
    import time
    world.load()
    engine.setup()
    SC = build()
    TL = timeline(SC)
    (VIDEO / "segmentos").mkdir(parents=True, exist_ok=True)
    caps = a.seg if a.seg else sorted(TL)
    tasks = [(cap, j) for cap in caps for j in range(len(TL[cap]["shots"])) if not seg_path(cap, j).exists()]
    total = sum(round(TL[c]["shots"][j][1] * FPS) for c, j in tasks)
    print(f"{len(tasks)} planos pendientes, {total} fotogramas", flush=True)
    t0, done, frames_done = time.time(), 0, 0
    import multiprocessing as mp
    from concurrent.futures import ProcessPoolExecutor, as_completed
    # Si un proceso muere (p. ej. por memoria) el pool se rompe y el script termina con error: run_all.sh lo relanza
    # y los planos ya terminados se saltan.
    with ProcessPoolExecutor(max_workers=a.jobs, mp_context=mp.get_context("spawn"), initializer=init, max_tasks_per_child=8) as ex:
        futs = {ex.submit(render_segment, tk): tk for tk in tasks}
        for f in as_completed(futs):
            path, sec = f.result()
            cap, j = futs[f]
            done += 1
            frames_done += round(TL[cap]["shots"][j][1] * FPS)
            el = time.time() - t0
            eta = el / max(frames_done, 1) * (total - frames_done)
            msg = f"[{done}/{len(tasks)}] {Path(path).name} {sec:5.0f}s · {frames_done}/{total} fotogramas · transcurrido {el / 60:5.1f} min · faltan ~{eta / 60:5.1f} min"
            print(msg, flush=True)
            (VIDEO / "progreso.txt").write_text(msg + "\n")

if __name__ == "__main__":
    main()
