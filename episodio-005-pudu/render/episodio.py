#!/usr/bin/env python3
"""Episodio 005 (pudú): tabla de planos, render por multiproceso y montaje.

Se ejecuta con el entorno de voice_ai (numpy, scipy, opencv):
    voice_ai/.venv/bin/python episodio-005-pudu/render/episodio.py --tiempos
    ... --still s05a [--t 2.0]       un fotograma suelto (frames/still/)
    ... --contacto                   un fotograma por plano, hoja de contactos (frames/contacto.png)
    ... --muestra 6                  los primeros N segundos (muestra.mp4)
    ... --render                     todos los cuadros (reanudable) en frames/render/
    ... --montar                     video final con audio y subtítulos: episodio-005.mp4
"""
import argparse
import json
import os
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parent
os.environ.setdefault("GORGO_CACHE", "/tmp/pudu_cache")
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(EP))

import numpy as np
import cv2
cv2.setNumThreads(1)          # un hilo por proceso: el reparto lo hace el Pool
import world
import engine
import camaras as D
import cervido as C
import fx_andina as FX
import tomas

W, H, FPS = 720, 1280, 25
FADE = 6
PUDU, PUDU_H, CIERVO = C.PUDU, C.PUDU_H, C.CIERVO
SUN0 = np.array([-0.50, 0.62, -0.42])

# ------------------------------------------------------------------ luz (se mezcla con el wx del bioma)
# Paleta fría y pastel de lluvia suave: sol blanco-verdoso entre la bruma, sombras celestes.
LLOVIZNA = dict(light=dict(sun=(0.98, 0.97, 0.93), amb=(0.72, 0.82, 0.88), fog=(0.80, 0.88, 0.90)))
CLARO = dict(light=dict(sun=(1.0, 0.98, 0.90), amb=(0.74, 0.84, 0.90), fog=(0.84, 0.90, 0.90)), mist=0.62, rain=0.25)
TARDE = dict(light=dict(sun=(1.0, 0.92, 0.82), amb=(0.70, 0.76, 0.88), fog=(0.88, 0.86, 0.88)), mist=0.6, rain=0.30,
             zenith=(0.60, 0.68, 0.82), horizon=(0.96, 0.88, 0.86))
SUN0 = np.array([-0.50, 0.62, -0.42])


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


# ------------------------------------------------------------------ poses del cérvido (t = segundos del plano)
def p_quieto(look=0.30, pitch=0.04, oreja=0.5, **kw):
    """Vivo aun quieto: mira a los lados, las orejas giran por turnos hacia sonidos, respira."""
    def f(t, d):
        return dict(t=t, head_yaw=look * np.sin(t * 0.55 + 0.4) + 0.06 * np.sin(t * 1.9),
                    head_pitch=pitch + 0.04 * np.sin(t * 0.9),
                    ear_l=oreja * max(0.0, np.sin(t * 1.1 + 0.3)) ** 2, ear_r=oreja * max(0.0, np.sin(t * 0.8 + 2.0)) ** 2,
                    tail_amp=1.2, **kw)
    return f


def p_come(**kw):
    """Cabeza al suelo, arranca un brote y mastica; levanta la cabeza a mirar entre bocado y bocado."""
    def f(t, d):
        ciclo = (t % 3.2) / 3.2
        arriba = float(np.clip((ciclo - 0.55) / 0.12, 0, 1) * np.clip((0.92 - ciclo) / 0.12, 0, 1))
        return dict(t=t, head_pitch=lerp_(-0.55, 0.12, arriba), head_dy=lerp_(-0.20, 0.0, arriba), head_dx=lerp_(0.04, 0.0, arriba),
                    head_yaw=0.18 * np.sin(t * 0.8), chew=1.0 if arriba < 0.5 else 0.6, ear_l=0.4 * np.sin(t * 2.1) ** 2,
                    ear_r=0.5 * max(0.0, np.sin(t * 1.3)) ** 2, tail_amp=1.4, **kw)
    return f


def p_rasca(**kw):
    def f(t, d):
        return dict(t=t, head_pitch=0.05, head_yaw=0.35 * np.sin(t * 1.5), head_dy=-0.02 + 0.015 * np.sin(t * 4.0), ear_l=0.3, ear_r=0.3, **kw)
    return f


def p_alerta(**kw):
    def f(t, d):
        return dict(t=t, head_pitch=0.16, head_dy=0.02, head_yaw=0.35 * np.sin(t * 0.7) + 0.05 * np.sin(t * 2.3),
                    ear_l=0.9 * max(0.0, np.sin(t * 1.6)) ** 0.5, ear_r=0.9, tail_amp=1.0, **kw)
    return f


def p_sacude(**kw):
    """Se sacude el agua del pelaje: temblor lateral rápido que arranca y se apaga."""
    def f(t, d):
        sh = float(np.clip(1.0 - abs(t - 1.2) / 0.9, 0, 1))
        return dict(t=t, shake=0.020 * sh, head_yaw=0.55 * sh * np.sin(t * 38.0 + 1.0) * 0.5, head_pitch=0.05, ear_l=sh, ear_r=sh, **kw)
    return f


def p_camina(spec, vel=1.0, **kw):
    def f(t, d):
        return dict(phase=d / (spec["speed"] * spec["period"]) + 0.15, walk=1.0, t=t, head_yaw=0.12 * np.sin(t * 0.7),
                    head_pitch=0.02 + 0.03 * np.sin(t * 1.1), bob=1.0, ear_l=0.3 * max(0.0, np.sin(t * 1.4)),
                    ear_r=0.3 * max(0.0, np.sin(t * 0.9 + 2)), tail_amp=1.0, **kw)
    return f


def p_mira(**kw):
    def f(t, d):
        return dict(t=t, head_pitch=0.04, head_yaw=0.06 * np.sin(t * 0.5), ear_l=0.5, ear_r=0.3 + 0.2 * np.sin(t * 1.3), **kw)
    return f


def lerp_(a, b, u):
    return a + (b - a) * u


# ------------------------------------------------------------------ construcción de planos
def toma(biome, p, tg, f, v=0.55, u=0.5, mv=(0, 0, 0), dtg=(0, 0, 0), actors=(), fg=(), wx=None, zf=None,
         ap=0.0012, sun=None, sky_fx=None, fx=(), cabeza=False):
    p, tg = np.array(p, float), np.array(tg, float)
    mv, dtg = np.array(mv, float), np.array(dtg, float)

    def cam(t, W_, H_):
        pp, tt = p + mv * t, tg + dtg * t
        ff = f * W_ / 1920
        yaw, pitch = D.aim(W_, H_, ff, pp, tt, v, u)
        sy, sp = D.shake(t + p[0], 0.0003)
        return world.Camera(W_, H_, ff, pp, yaw + sy, pitch + sp)
    a0 = actors[0].pos(0.0) if actors else tg
    if actors:                                   # el origen del animal está en el tronco: apuntar hacia donde mira (cabeza + cuello)
        an = actors[0].ang
        sc_ = actors[0].spec["scale"]
        if cabeza:
            tg = np.array([tg[0], 0.60 * sc_ + 0.0, tg[2]]) + np.array([np.cos(an), 0.0, np.sin(an)]) * 0.66 * sc_
        else:
            tg = tg + np.array([np.cos(an), 0.0, np.sin(an)]) * 0.22 * sc_
    zfocus = zf if zf is not None else float(np.hypot(*(a0[[0, 2]] - p[[0, 2]])))
    s = dict(biome=biome, cam=cam, animals=lambda t: [a(t) for a in actors], focus=lambda t: zfocus, aperture=ap,
             wx=wx or {}, actors=actors, through=False, sun=sun, sky_fx=sky_fx, fg=[], life_at=a0, fx=list(fx))
    keep = []
    for t in np.linspace(0, 6, 7):
        c = cam(t, 1280, 720)
        keep.append((c.pos[0], c.pos[2], 0.5))
        for s_ in (0.6, 1.2, 2.0, 3.0):
            keep.append((c.pos[0] + np.sin(c.yaw) * s_, c.pos[2] + np.cos(c.yaw) * s_, 0.35 + 0.05 * s_))
    for a in actors:
        q = a.pos(0.0)
        keep.append((q[0], q[2], 0.45))
        for s_ in (0.3, 0.5, 0.7, 0.85):
            keep.append((p[0] + (q[0] - p[0]) * s_, p[2] + (q[2] - p[2]) * s_, 0.30))
    s["keep"] = keep
    for i, g in enumerate(fg):
        g = dict(g)
        g.setdefault("ph", 1.3 * i)
        g.setdefault("flip", bool(i % 2))
        g.setdefault("y", 0.0)
        g.setdefault("var", i)
        g.setdefault("sc", 1.0)
        s["fg"].append(g)
    return s


def cervido(spec, x, z, ang, pose, speed=0.0, ss=1.5, **kw):
    return D.actor(spec, (x, z), ang, speed=speed, pose=pose, ss=ss, **kw)


def nalca(x, z, sc=0.8, var=0):
    return dict(kind="nalca", x=x, z=z, sc=sc, var=var)


def helecho(x, z, sc=0.8, var=0):
    return dict(kind="fern_verde", x=x, z=z, sc=sc, var=var)


def colihue(x, z, sc=0.8, var=0):
    return dict(kind="colihue", x=x, z=z, sc=sc, var=var)


def piedra(x, z, sc=0.3, var=0):
    return dict(kind="rock_musgo", x=x, z=z, sc=sc, var=var)


def hojas(*specs, goteo_n=8, rayos_n=0, seed=0):
    """Capa 1 (pegada a la cámara): hojas que reciben la gota y la dejan caer, más goteo del plano medio y rayos."""
    out = []
    if rayos_n:
        out.append(FX.rayos(rayos_n, 0.11, seed))
    out.append(FX.goteo(goteo_n, seed=seed))
    for i, sp in enumerate(specs):
        out.append(FX.hoja_con_gota(**sp, fase=0.31 * i + 0.13 * seed, T=2.9 + 0.5 * i))
    return out


# hojas de primer plano reusables: esquina inferior izquierda/derecha y borde superior
HI = dict(base=(-0.04, 1.02), ang=48, largo=0.52, ancho=0.20, sigma=3.2)        # abajo-izquierda hacia arriba-derecha
HD = dict(base=(1.05, 0.98), ang=135, largo=0.50, ancho=0.20, sigma=3.0, flip=True)   # abajo-derecha
HS = dict(base=(0.88, -0.04), ang=-125, largo=0.42, ancho=0.17, sigma=2.4)       # arriba-derecha hacia abajo
HS2 = dict(base=(0.10, -0.05), ang=-55, largo=0.38, ancho=0.16, sigma=2.2)       # arriba-izquierda


def build_shots():
    S = {}
    W_ = LLOVIZNA
    # ---- 1. EL FAMILIAR: ciervo colorado majestuoso
    S["s01a"] = toma("selva_andina", (0, 0.9, -0.3), (0.2, 0.7, 4.4), 4300, v=0.50, mv=(0, 0, 0.12), ap=0.0010, wx=W_,
                     actors=[cervido(CIERVO, 0.2, 4.4, -2.0, p_quieto(0.25, 0.10))],
                     fg=[helecho(-0.9, 1.1, 1.0, 2), nalca(1.5, 1.6, 0.8, 1), colihue(-1.4, 2.4, 1.0, 3)],
                     fx=hojas(HI, HS, seed=1))
    S["s01b"] = toma("selva_andina", (0.0, 1.55, 1.0), (0.1, 1.5, 4.3), 7600, v=0.55, mv=(0.03, 0, 0.0), ap=0.0014, wx=W_, zf=3.3,
                     actors=[cervido(CIERVO, 0.1, 4.3, -1.75, p_quieto(0.12, 0.12))],
                     fg=[helecho(-0.4, 1.6, 0.9, 5), nalca(0.8, 1.9, 0.8, 3)], fx=hojas(HD, HS2, seed=2))
    # ---- 2. LA PRESENTACIÓN
    S["s02a"] = toma("selva_andina", (0.3, 0.55, -0.4), (0.0, 0.4, 3.0), 2500, v=0.60, mv=(0, 0, 0.30), ap=0.0009, wx=CLARO,
                     actors=[cervido(CIERVO, 1.2, 4.0, -1.0, p_alerta()), cervido(PUDU, -0.2, 2.8, -1.9, p_sacude())],
                     fg=[nalca(-0.6, 1.0, 1.0, 4), helecho(0.7, 1.1, 0.9, 6), colihue(1.4, 1.8, 1.0, 5)],
                     fx=hojas(HI, HD, rayos_n=4, seed=3))
    S["s02b"] = toma("selva_andina", (0.15, 0.22, 0.0), (0.0, 0.2, 1.6), 2900, mv=(0.05, 0, 0.03), wx=CLARO,
                     actors=[cervido(PUDU, 0.0, 1.4, -2.25, p_sacude())],
                     fg=[nalca(-0.45, 0.85, 0.9, 1), helecho(0.55, 0.8, 0.8, 8), colihue(0.9, 1.7, 1.0, 2)],
                     fx=hojas(HI, HS, rayos_n=3, seed=4))
    S["s02c"] = toma("selva_andina", (0.4, 0.14, 0.3), (-0.05, 0.25, 1.5), 3800, mv=(-0.08, 0, 0), zf=1.3, wx=CLARO,
                     actors=[cervido(PUDU, -0.05, 1.5, -1.8, p_quieto(0.4, 0.05))],
                     fg=[nalca(0.35, 0.65, 0.8, 5), helecho(-0.3, 0.7, 0.8, 3)], fx=hojas(HD, HS2, seed=5))
    # ---- 3. LA COMIDA
    S["s03a"] = toma("selva_andina", (0.1, 0.13, 0.0), (0.05, 0.25, 1.3), 3000, v=0.58, mv=(0, 0, 0.04), wx=W_,
                     actors=[cervido(PUDU, 0.1, 1.3, -2.1, p_come())],
                     fg=[helecho(-0.35, 0.6, 0.7, 2), nalca(0.6, 0.9, 0.8, 6)], fx=hojas(HI, HD, seed=6))
    S["s03b"] = toma("selva_andina", (0.3, 0.55, 0.15), (0.1, 0.2, 1.3), 2300, mv=(0, -0.02, 0.02), wx=W_,
                     actors=[cervido(PUDU, 0.1, 1.3, -2.6, p_come())],
                     fg=[helecho(-0.5, 0.7, 0.8, 4)], fx=hojas(HS, HI, seed=7))
    S["s03c"] = toma("selva_andina", (-0.7, 0.35, -0.2), (0.7, 0.2, 2.2), 2800, mv=(0.12, 0, 0.08), wx=W_,
                     actors=[cervido(PUDU, 0.7, 2.3, -2.6, p_come())],
                     fg=[nalca(-0.3, 0.9, 1.0, 2), colihue(1.4, 1.6, 1.1, 1), helecho(1.1, 1.2, 0.9, 5)], fx=hojas(HD, HS2, rayos_n=3, seed=8))
    # ---- 4. LOS CUERNITOS
    S["s04a"] = toma("selva_andina", (0.55, 0.26, 0.25), (0.1, 0.2, 1.1), 3900, mv=(-0.04, 0, 0.02), wx=CLARO, cabeza=True,
                     actors=[cervido(PUDU, 0.1, 1.1, -2.75, p_quieto(0.18, 0.08))],
                     fg=[helecho(-0.3, 0.55, 0.7, 1), nalca(0.5, 0.8, 0.7, 2)], fx=hojas(HI, HD, seed=9))
    S["s04b"] = toma("selva_andina", (0.5, 0.2, 0.2), (0.0, 0.25, 1.4), 2900, mv=(-0.05, 0, 0.02), wx=CLARO,
                     actors=[cervido(PUDU, 0.0, 1.4, -2.5, p_rasca())],
                     fg=[colihue(0.5, 0.9, 0.9, 4), helecho(-0.4, 0.8, 0.8, 7)], fx=hojas(HS, HI, seed=10),)
    # ---- 5. EL ESCONDITE
    S["s05a"] = toma("selva_andina", (0.0, 0.2, 0.0), (0.0, 0.25, 1.5), 3000, mv=(0, 0, 0.03), wx=W_,
                     actors=[cervido(PUDU, 0.0, 1.5, -2.0, p_alerta())],
                     fg=[helecho(-0.3, 0.55, 0.9, 9), nalca(0.45, 0.8, 0.9, 7), helecho(0.2, 0.5, 0.6, 3)], fx=hojas(HI, HD, seed=11))
    S["s05b"] = toma("selva_andina", (1.4, 0.25, 0.6), (-0.2, 0.2, 2.2), 3600, mv=(-0.20, 0, 0.10), wx=W_,
                     actors=[cervido(PUDU, 1.6, 2.2, 3.14159, p_camina(PUDU), speed=2.2)],
                     fg=[helecho(0.8, 0.9, 0.8, 5), nalca(-0.2, 1.2, 1.0, 8), colihue(1.0, 1.5, 1.1, 6)], fx=hojas(HD, HS2, seed=12))
    # ---- 6. LA SOLEDAD
    S["s06a"] = toma("selva_andina", (-0.6, 0.45, -0.3), (0.5, 0.25, 3.0), 3100, mv=(0.12, 0, 0.10), wx=CLARO,
                     actors=[cervido(PUDU, -0.8, 3.0, 0.0, p_camina(PUDU), speed=1.0)],
                     fg=[nalca(-0.2, 1.1, 1.0, 3), helecho(0.9, 1.3, 1.0, 4), colihue(-1.2, 1.8, 1.1, 8)], fx=hojas(HI, HS, rayos_n=5, seed=13))
    S["s06b"] = toma("selva_andina", (0.0, 0.05, 0.4), (0.0, 0.25, 1.9), 3100, mv=(0, 0, 0.02), wx=CLARO, zf=1.6,
                     actors=[cervido(PUDU, 0.0, 1.9, -2.0, p_mira())],
                     fg=[helecho(-0.35, 0.9, 0.9, 6), helecho(0.45, 0.8, 0.9, 7), nalca(0.0, 0.6, 0.5, 5)], fx=hojas(HI, HD, seed=14))
    # ---- 7. LO CHIQUITO
    S["s07a"] = toma("selva_andina", (0.5, 0.26, 0.3), (0.05, 0.22, 1.0), 4700, wx=W_, cabeza=True,
                     actors=[cervido(PUDU, 0.05, 1.0, -2.7, p_quieto(0.15, 0.06))],
                     fg=[helecho(-0.25, 0.5, 0.6, 2), nalca(0.4, 0.7, 0.7, 4)], fx=hojas(HI, HD, seed=15))
    S["s07b"] = toma("selva_andina", (0.1, 0.30, 0.2), (0.1, 0.22, 1.5), 3300, mv=(0, 0.01, -0.07), wx=W_,
                     actors=[cervido(PUDU, 0.1, 1.5, -2.0, p_quieto())],
                     fg=[dict(kind="log_musgo", x=0.55, z=1.6, sc=0.6, var=1), helecho(-0.5, 0.9, 0.8, 1)], fx=hojas(HS, HI, seed=16))
    # ---- 8. LA REFUTACIÓN
    S["s08a"] = toma("selva_andina", (0.0, 0.18, 0.0), (0.0, 0.25, 1.4), 2900, wx=CLARO,
                     actors=[cervido(PUDU, 0.0, 1.4, -2.0, p_mira()), cervido(CIERVO, 1.6, 4.6, 3.14159, p_camina(CIERVO), speed=0.5)],
                     fg=[nalca(0.0, 0.7, 1.0, 1), nalca(-0.7, 0.9, 1.0, 3), helecho(0.6, 0.8, 0.8, 8)], fx=hojas(HI, HD, seed=17))
    S["s08b"] = toma("selva_andina", (0.1, 0.9, -0.6), (0.2, 0.15, 2.4), 3000, mv=(0, 0, 0.12), wx=TARDE,
                     actors=[cervido(PUDU, 0.2, 2.4, -2.2, p_quieto(0.3, 0.10))],
                     fg=[dict(kind="log_musgo", x=-0.6, z=1.6, sc=0.8, var=2), helecho(0.9, 1.2, 0.9, 2)],
                     fx=hojas(HD, HS2, rayos_n=4, seed=18))
    # ---- 9. CIERRE
    S["s09a"] = toma("selva_andina", (0, 0.6, -0.4), (0.0, 0.25, 2.6), 3300, mv=(0, 0.02, -0.06), wx=TARDE,
                     actors=[cervido(PUDU, 0.0, 2.6, -2.2, p_quieto())],
                     fg=[nalca(-0.8, 1.0, 1.1, 5), helecho(0.9, 1.2, 1.0, 9), colihue(1.3, 2.0, 1.1, 2)], fx=hojas(HI, HS, rayos_n=5, seed=19))
    S["s09b"] = toma("selva_andina", (0, 0.2, 0.2), (0.05, 0.25, 1.5), 3700, wx=TARDE, sun=(-0.3, 0.45, 0.8),
                     actors=[cervido(PUDU, 0.05, 1.5, -1.9, p_mira())],
                     fg=[helecho(-0.35, 0.6, 0.8, 4), nalca(0.5, 0.8, 0.8, 7)], fx=hojas(HI, HD, rayos_n=3, seed=20))
    return S


# ------------------------------------------------------------------ línea de tiempo
def linea_tiempo():
    escenas = json.loads((EP / "audio" / "escenas.json").read_text())
    total = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
         str(EP / "audio" / "episodio-005-final.mp3")], capture_output=True, text=True, check=True).stdout)
    tiempos = {e["escena"]: (0.0 if i == 0 else e["inicio"], escenas[i + 1]["inicio"] if i + 1 < len(escenas) else total)
               for i, e in enumerate(escenas)}
    out = []
    for n, (a, b) in tiempos.items():
        grupo = [t for t in tomas.TOMAS if t["escena"] == n]
        suma = sum(t["peso"] for t in grupo)
        cur = a
        for t in grupo:
            fin = cur + (b - a) * t["peso"] / suma
            out.append((t["id"], cur, fin))
            cur = fin
    return out, total


_SH = None
_TL = None


def _init():
    global _SH, _TL
    if _SH is None:
        _SH = build_shots()
        _TL = linea_tiempo()[0]
        engine.setup()


def _frame(shot, t, w=W, h=H):
    world.SUN = unit(shot["sun"] if shot.get("sun") is not None else SUN0)
    img = engine.frame(shot, t, w, h)
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)


def frame_global(fi, w=W, h=H):
    _init()
    T = fi / FPS
    idx = next((i for i, (_, a, b) in enumerate(_TL) if a <= T < b), len(_TL) - 1)
    sid, a, b = _TL[idx]
    img = _frame(_SH[sid], T - a, w, h)
    if idx > 0 and T - a < FADE / FPS:
        pid, pa, pb = _TL[idx - 1]
        prev = _frame(_SH[pid], T - pa, w, h)
        al = (T - a) * FPS / FADE
        img = cv2.addWeighted(prev, 1 - al, img, al, 0)
    return img


def _job(fi):
    out = EP / "frames" / "render" / f"{fi:05d}.jpg"
    if out.exists():
        return fi
    img = frame_global(fi)
    cv2.imwrite(str(out), img[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 95])
    return fi


def _job_small(fi):
    return frame_global(fi, 360, 640)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tiempos", action="store_true")
    ap.add_argument("--still")
    ap.add_argument("--t", type=float, default=1.0)
    ap.add_argument("--contacto", action="store_true")
    ap.add_argument("--muestra", type=float, default=0)
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--montar", action="store_true")
    ap.add_argument("--procs", type=int, default=4)
    args = ap.parse_args()
    (EP / "frames" / "render").mkdir(parents=True, exist_ok=True)
    if args.still and not (args.tiempos or args.contacto or args.render or args.muestra or args.montar):
        tl, total, nfr = [], 0.0, 0
    else:
        tl, total = linea_tiempo()
        nfr = int(total * FPS)

    if args.tiempos:
        for sid, a, b in tl:
            print(f"{sid}: {a:6.2f}–{b:6.2f}  ({b - a:4.1f} s)")
        print(f"total {total:.1f} s, {nfr} cuadros")
    if args.still:
        global _SH
        _SH = build_shots()
        engine.setup()
        (EP / "frames" / "still").mkdir(exist_ok=True)
        img = _frame(_SH[args.still], args.t)
        cv2.imwrite(str(EP / "frames" / "still" / f"{args.still}.png"), img[..., ::-1])
    if args.contacto:
        mids = [int((a + b) / 2 * FPS) for _, a, b in tl]
        with Pool(args.procs) as pool:
            imgs = pool.map(_job_small, mids)
        cols = 7
        rows = (len(imgs) + cols - 1) // cols
        sheet = np.full((rows * 640, cols * 360, 3), 255, np.uint8)
        for k, im in enumerate(imgs):
            r, c = divmod(k, cols)
            sheet[r * 640:(r + 1) * 640, c * 360:(c + 1) * 360] = im
            cv2.putText(sheet, tl[k][0], (c * 360 + 8, r * 640 + 26), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.imwrite(str(EP / "frames" / "contacto.png"), sheet[..., ::-1])
    if args.render or args.muestra:
        n = int(args.muestra * FPS) if args.muestra else nfr
        with Pool(args.procs) as pool:
            for k, _ in enumerate(pool.imap(_job, range(n), chunksize=1)):
                if k % 50 == 0:
                    print(f"{k}/{n}", flush=True)
        if args.muestra:
            montar(n, EP / "muestra.mp4", con_subs=False)
    if args.montar:
        montar(nfr, EP / "episodio-005.mp4", con_subs=True)


def montar(n, destino, con_subs=True):
    audio = EP / "audio" / "episodio-005-final.mp3"
    tmp = EP / "frames" / "sin-subtitulos.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(EP / "frames" / "render" / "%05d.jpg"),
                    "-i", str(audio), "-frames:v", str(n), "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", str(tmp)], check=True)
    if not con_subs:
        tmp.replace(destino)
        return
    estilo = ("FontName=Inter,FontSize=9,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00302020,"
              "BorderStyle=1,Outline=2,Alignment=2,MarginV=30")
    srt = str(EP / "audio" / "episodio-005-voz.srt").replace(":", r"\:")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-vf", f"subtitles='{srt}':force_style='{estilo}'",
                    "-c:v", "libx264", "-crf", "17", "-c:a", "copy", str(destino)], check=True)
    print("Listo:", destino)


if __name__ == "__main__":
    main()
