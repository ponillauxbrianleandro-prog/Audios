#!/usr/bin/env python3
"""Episodio 005 · VETUSODON — escenas, planos, tiempos (según la voz real), subtítulos, render y ensamblado.

  python3 episodio.py --tiempos                  duración de cada escena y total
  python3 episodio.py --preview DIR [--only N..] un fotograma por plano (revisión rápida)
  python3 episodio.py --tomas                    prepara las fotos del montaje (cache)
  python3 episodio.py --seg [--jobs N]           renderiza todos los planos (reanudable) a ../video/segmentos
  python3 episodio.py --srt                      escribe los subtítulos
  python3 episodio.py --assemble                 une planos, mezcla el audio (si existe) y codifica ≤ 480 MB
"""
import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
import world
import engine
import biomes
import cine as K
from cine import (actor, track, land, finalize, FPS, VET, GOR, PRO, DII, ANF, PAR, LYS, p_idle, p_sniff, p_stalk, p_walk, p_eat, p_lie, p_fight, p_alerta, bank_z,
                  FG_L, FG_R, FG_LR, FG_REED, FG_BRANCH, FG_BRANCH_R, FG_LOW, FG_FRAME_R, FG_FRAME_L, FG_DRY)
import montaje
import cuaderno
import guion_datos as GD
import graficos as G

AQUI = Path(__file__).resolve().parent
VIDEO = AQUI.parent / "video"
VOZ_DIR = AQUI.parents[1] / "voice_ai" / "cache_v9"
GAP = 0.85          # silencio entre frases (la voz nunca se solapa)
LEAD = 1.0          # silencio al comienzo de cada escena


def zb(x, dry=0.0):
    return bank_z(x, dry)


def voz_dur():
    """Duración real de cada línea (segundos) si ya existe la voz; si no, una estimación por palabras."""
    f = VOZ_DIR / "durs.json"
    d = json.loads(f.read_text()) if f.exists() else {}
    out = {}
    for esc, i, t in GD.todas():
        out[(esc, i)] = d.get(f"{esc:02d}_{i}") or max(1.2, len(t.split()) * 0.42 + 0.3)
    return out


# ---------------------------------------------------------------- notas del cuaderno (coordenadas del libro abierto 2000x1300)
def nb_hallazgo(d, ls):
    a0, a1, a2 = ls[0][0], ls[1][0], ls[2][0]
    return [dict(k="texto", s="Karoo, Sudáfrica", pos=(190, 110), size=76, t0=0.4, t1=1.6, rot=-1.0),
            dict(k="craneo", box=(150, 250, 760, 500), t0=a0 + 0.2, t1=a0 + 4.2),
            dict(k="medida", p0=(150, 790), p1=(910, 790), t0=a0 + 4.2, t1=a0 + 5.0),
            dict(k="texto", s="cráneo ≈ 18 cm", pos=(210, 810), size=90, t0=a0 + 5.0, t1=a0 + 6.2, rot=-2),
            dict(k="texto", s="región temporal: 60 %", pos=(190, 940), size=64, t0=a0 + 6.2, t1=a0 + 7.6, rot=-1),
            dict(k="texto", s="hocico corto y ancho", pos=(190, 1030), size=64, t0=a0 + 7.6, t1=a0 + 8.8, rot=-1),
            dict(k="animal", box=(1040, 420, 860, 440), frame=6, t0=a0 + 1.0, t1=a0 + 9.0),
            dict(k="texto", s="Kammerer:", pos=(1070, 120), size=84, t0=a1, t1=a1 + 1.0, rot=1.5),
            dict(k="texto", s="«…nuestros propios", pos=(1070, 215), size=72, t0=a1 + 1.2, t1=a1 + 3.6, rot=1.2),
            dict(k="texto", s="antepasados»", pos=(1070, 295), size=72, t0=a1 + 3.8, t1=a1 + 5.4, rot=1.0),
            dict(k="flecha", p0=(1480, 330), p1=(1430, 450), t0=a1 + 6.0, t1=a1 + 6.6),
            dict(k="texto", s="Angielczyk:", pos=(1070, 905), size=76, t0=a2, t1=a2 + 1.0, rot=1.5),
            dict(k="texto", s="«…una era de antiguos", pos=(1070, 990), size=66, t0=a2 + 1.2, t1=a2 + 3.2, rot=1.0),
            dict(k="texto", s="parientes de los mamíferos»", pos=(1070, 1070), size=66, t0=a2 + 3.4, t1=a2 + 5.6, rot=1.0),
            dict(k="circulo", c=(1450, 1085), r=(480, 70), t0=a2 + 6.0, t1=a2 + 6.8)]


def nb_oido(d, ls):
    l0, l1, l2 = ls[0][0], ls[1][0], ls[2][0]
    return [dict(k="texto", s="mandíbula", pos=(190, 110), size=84, t0=0.5, t1=1.7, rot=-1.0),
            dict(k="craneo", box=(150, 230, 800, 530), t0=l0, t1=l0 + 5.0),
            dict(k="texto", s="varios huesos", pos=(190, 820), size=84, t0=l0 + 5.0, t1=l0 + 6.4, rot=-2),
            dict(k="flecha", p0=(760, 700), p1=(560, 640), t0=l1, t1=l1 + 0.7),
            dict(k="texto", s="articular + cuadrado", pos=(190, 930), size=78, t0=l1 + 0.8, t1=l1 + 2.8, rot=-1.5),
            dict(k="texto", s="= articulación de la mandíbula", pos=(190, 1020), size=64, t0=l1 + 3.0, t1=l1 + 5.0, rot=-1),
            dict(k="animal", box=(1060, 420, 820, 500), frame=14, t0=l2, t1=l2 + 6.0),
            dict(k="texto", s="en los mamíferos:", pos=(1070, 130), size=84, t0=l2 + 0.5, t1=l2 + 2.2, rot=1.5),
            dict(k="texto", s="martillo + yunque", pos=(1070, 230), size=90, t0=l2 + 2.4, t1=l2 + 4.4, rot=1.0),
            dict(k="texto", s="del oído medio", pos=(1070, 330), size=70, t0=l2 + 4.6, t1=l2 + 6.0, rot=1.0),
            dict(k="circulo", c=(1450, 255), r=(420, 70), t0=l2 + 6.4, t1=l2 + 7.2),
            dict(k="tachar", p0=(190, 1035), p1=(960, 1050), t0=l2 + 7.6, t1=l2 + 8.4)]


def cabeza(bio, a, side=1.5, fwd=1.7, h=0.5, f=2300, fg=None, extra=()):
    """Primer plano de la cara: animal quieto, cámara por delante y de costado, enfoque en la cabeza."""
    return track(bio, a, cam=(side, fwd, h), f=f, v=0.55, u=0.5, tgt=(0.78, 0.46), ap=0.0025, fg=fg or FG_L, extra=extra, pan=0.0)


def quieto(spec, x, ang, pose=None, dz=1.9, dry=0.0):
    return actor(spec, (x, zb(x, dry) - dz), ang, speed=0.0, pose=pose or p_idle(look=0.45))


def nb_shot(items, seed):
    """Plano de cuaderno + ventanas de tiempo de cada trazo (para el sonido de lápiz)."""
    sh = K.gfx(cuaderno.cuaderno, native=False, items=items, seed=seed)
    sh["nb_audio"] = [(it["t0"], it["t1"]) for it in items]
    return sh


# ---------------------------------------------------------------- escenas
def build(vd):
    """Devuelve las escenas con duración real: dict(nombre, dur, shots=[(peso, plano)], lineas=[(t, dur, texto)], marcos=[(t, texto)], amb)."""
    B = biomes.BIOMES
    out = []

    def ctx_lines(esc):
        gap = GD.GAP_ESC.get(esc, GAP)
        t, ls = (0.25 if esc in GD.GAP_ESC else LEAD), []
        for i, tx in enumerate(GD.LINEAS[esc]):
            d = vd[(esc, i)]
            ls.append((t, d, tx))
            t += d + gap
        return ls, t - gap + (0.6 if esc in GD.GAP_ESC else 1.2)

    def escena(esc, nombre, plan, shots_fn, marcos=(), amb="", sfx=(), clima="calma", booms=None):
        ls, necesario = ctx_lines(esc) if esc in GD.LINEAS else ([], 0.0)
        dur = max(plan, necesario)
        dur = round(dur * FPS) / FPS
        c = dict(esc=esc, nombre=nombre, dur=dur, lineas=ls, amb=amb, sfx=list(sfx))
        c["marcos"] = [(ls[i][0] + ls[i][1] + dly, tx) for (i, dly, tx) in marcos]
        c["shots_fn"] = shots_fn
        c["ctx"] = dict(lineas=ls, dur=dur)
        c["clima"] = clima
        c["booms"] = list(booms) if booms is not None else [t for t, _ in c["marcos"]]
        c["cards"] = [(ls[i][0] + dly, key, dd) for (e, i, dly, key, dd) in GD.CARDS if e == esc]
        out.append(c)

    # ---------- 0 · APERTURA: ráfaga de fotos estilo carteles de calle
    def s0(ctx):
        cortes = montaje.cortes_de(ctx["dur"], seed=3, lo=0.20, hi=0.45)
        textos = [(t, tx) for t, tx in ctx["marcos"]]
        sh = K.gfx(montaje.montaje, native=False, tomas=None, cortes=cortes, textos=textos, seed=3, variante=0)
        sh["tomas_lazy"] = True
        sh["cortes"] = cortes
        return [(1.0, sh)]
    escena(0, "0 · Apertura", 12.0, s0, marcos=[(0, 0.05, "252.000.000 a. C."), (1, 0.05, "CRÁNEO 18 cm · 4 FÓSILES"), (2, 0.05, "VETUSODON ELIKHULU")], amb="calle",
           sfx=["clic"], clima="rafaga")

    # ---------- 1 · EL NOMBRE (ámbar)
    def s1(ctx):
        v = actor(VET, (-4.0, zb(-4.0) - 1.9), np.arctan2(-0.20, -0.98), speed=0.8)
        v2 = actor(VET, (-24.0, zb(-24.0) - 2.0), np.arctan2(0.12, 0.99), speed=0.8)
        return [(5, track("v_ambar", v, cam=(2.6, -4.2, 0.55), f=3000, v=0.58, u=0.55, tgt=(0.1, 0.40), ap=0.010, fg=FG_LR)),
                (4, cabeza("v_ambar", quieto(VET, -6.0, np.arctan2(-0.15, -0.99), p_sniff()), side=1.6, fwd=1.9, f=2300)),
                (5, land("v_ambar", (-12.0, 1.6, 4.0), 0.12, f=1250, pitch=0.02, move=(0.3, 0.0, 0.5), actors=(v2,), fg=FG_LOW)),
                (5, track("v_ambar", v2, cam=(4.0, -6.0, 0.9), f=4600, v=0.57, u=0.52, ap=0.016, fg=FG_FRAME_R)),
                (4, track("v_ambar", v, cam=(1.3, -3.2, 0.40), f=2800, v=0.58, u=0.50, tgt=(-0.30, 0.30), ap=0.003, fg=FG_LOW))]
    escena(1, "1 · El nombre", 30.0, s1, marcos=[(1, 0.3, "CRÁNEO ≈ 18 cm"), (3, 0.4, "GRUPO HERMANO DE EUCYNODONTIA")], amb="amanecer", clima="calma")

    # ---------- 2 · EL VALLE (violeta)
    def s2(ctx):
        a = actor(DII, (-9.0, zb(-9.0) - 2.4), np.arctan2(0.1, 0.99), speed=0.9)
        b = actor(ANF, (-14.0, zb(-14.0) - 0.9), np.arctan2(-0.3, -0.95), speed=0.5)
        v = actor(VET, (-30.0, zb(-30.0) - 2.2), np.arctan2(0.05, 1.0), speed=0.7)
        v2 = actor(VET, (-14.0, zb(-14.0) - 2.4), np.arctan2(-0.08, -0.99), speed=0.6)
        return [(7, land("v_violeta", (-44.0, 1.5, 2.6), 0.22, f=1100, pitch=0.02, move=(1.1, 0.0, 0.2), dyaw=-0.006, actors=(v,), fg=FG_LOW)),
                (5, track("v_violeta", a, cam=(2.2, -3.4, 0.45), f=2600, v=0.58, u=0.55, ap=0.004, fg=FG_LR, extra=(b,))),
                (6, track("v_violeta", v, cam=(3.0, -4.2, 0.6), f=2700, v=0.58, u=0.5, ap=0.004, fg=FG_REED)),
                (5, land("v_violeta", (-22.0, 2.2, 1.4), 0.50, f=1000, pitch=0.12, move=(0.0, 0.4, 0.6), actors=(v2,), fg=FG_BRANCH)),
                (6, track("v_violeta", v2, cam=(2.0, -3.0, 0.5), f=2900, v=0.58, u=0.5, ap=0.004, fg=FG_FRAME_L))]
    escena(2, "2 · El valle", 48.0, s2, amb="valle", clima="misterio")

    # ---------- 3 · CUADERNO 1: EL HALLAZGO
    def s3(ctx):
        d = ctx["dur"]
        n1 = nb_shot(nb_hallazgo(d, ctx["lineas"]), 1)
        v = actor(VET, (-5.0, zb(-5.0) - 2.0), np.arctan2(-0.1, -0.99), speed=0.0, pose=p_sniff())
        roca = land("v_oxido", (-12.0, 1.4, 3.0), 0.8, f=2100, pitch=0.05, move=(0.2, 0.0, 0.2), actors=(), fg=FG_FRAME_R)
        return [(20, n1), (5, roca), (5, track("v_oxido", v, cam=(1.9, -3.0, 0.5), f=3200, v=0.58, u=0.5, ap=0.010, fg=FG_L))]
    escena(3, "3 · Cuaderno: el hallazgo", 40.0, s3, amb="cuaderno", sfx=["lapiz", "papel"], clima="calma", booms=[])

    # ---------- 4 · UNA MAÑANA (ámbar)
    def s4(ctx):
        v = quieto(VET, -7.0, np.arctan2(-0.15, -0.99), p_sniff())
        w = actor(VET, (-2.0, zb(-2.0) - 2.2), np.arctan2(-0.25, -0.97), speed=0.9)
        e = quieto(VET, -16.0, 0.0, p_eat())
        return [(5, cabeza("v_esmeralda", v, side=1.6, fwd=1.9, f=2300)),
                (6, track("v_esmeralda", w, cam=(3.0, -4.5, 0.7), f=3200, v=0.58, u=0.5, ap=0.004, fg=FG_LR)),
                (5, track("v_esmeralda", e, cam=(2.4, 0.8, 0.5), f=2500, v=0.58, u=0.55, tgt=(0.5, 0.40), ap=0.004, fg=FG_FRAME_L, pan=0.0)),
                (6, track("v_esmeralda", w, cam=(1.2, -3.4, 0.45), f=2600, v=0.57, u=0.5, ap=0.004, fg=FG_LOW)),
                (5, land("v_esmeralda", (-22.0, 2.2, 5.0), 0.05, f=1100, pitch=0.06, move=(0.5, 0.0, 0.0), actors=(w,), fg=FG_BRANCH_R)),
                (5, cabeza("v_esmeralda", e, side=1.4, fwd=1.5, h=0.4, f=2500, fg=FG_LOW)),
                (5, track("v_esmeralda", w, cam=(5.0, -3.0, 1.4), f=3800, v=0.56, u=0.5, ap=0.004, fg=FG_FRAME_R))]
    escena(4, "4 · Una mañana", 60.0, s4, amb="mañana", sfx=["pasos"], clima="ternura", booms=[])

    # ---------- 5 · MONTAJE: ¿qué es un cinodonte?
    def s5(ctx):
        cortes = montaje.cortes_de(ctx["dur"], seed=9, lo=0.22, hi=0.50)
        textos = [(t, tx) for t, tx in ctx["marcos"]]
        sh = K.gfx(montaje.montaje, native=False, tomas=None, cortes=cortes, textos=textos, seed=9, variante=1)
        sh["tomas_lazy"] = True
        sh["cortes"] = cortes
        return [(1.0, sh)]
    escena(5, "5 · Montaje: cinodonte", 7.0, s5, marcos=[(0, 0.2, "SINÁPSIDOS > 300 Ma")], amb="calle", sfx=["clic"], clima="rafaga")

    # ---------- 6 · EL VECINO (óxido)
    def s6(ctx):
        g = actor(GOR, (-12.0, zb(-12.0) - 4.0), np.arctan2(0.1, 0.99), speed=0.5, pose=p_stalk(GOR))
        v = quieto(VET, -6.0, np.arctan2(-0.1, -0.99), p_idle(look=0.5))
        run = actor(VET, (-26.0, zb(-26.0) - 2.2), np.arctan2(0.05, 1.0), speed=2.4)
        chase = actor(GOR, (-31.0, zb(-31.0) - 2.4), np.arctan2(0.05, 1.0), speed=2.1)
        return [(6, track("v_azul", g, cam=(3.0, -5.0, 0.8), f=3200, v=0.58, u=0.5, ap=0.004, fg=FG_DRY)),
                (5, cabeza("v_azul", v, side=1.5, fwd=1.8, f=2300, fg=FG_LOW)),
                (7, land("v_azul", (-4.0, 1.5, 2.0), 0.15, f=1200, pitch=0.03, move=(0.2, 0.0, 0.2), actors=(v, g), fg=FG_FRAME_L)),
                (6, track("v_azul", run, cam=(3.4, -3.8, 0.7), f=2800, v=0.58, u=0.5, ap=0.004, extra=(chase,), fg=FG_DRY, tnom=3.0)),
                (5, track("v_azul", chase, cam=(2.4, -2.8, 0.5), f=2400, v=0.58, u=0.5, ap=0.004, fg=FG_LOW, tnom=3.0)),
                (5, land("v_azul", (-20.0, 0.5, 3.0), 0.45, f=1500, pitch=0.0, move=(0.5, 0.0, 0.3), actors=(run, chase), fg=FG_DRY)),
                (5, track("v_azul", run, cam=(1.4, -2.6, 0.4), f=2500, v=0.60, u=0.5, ap=0.003, fg=FG_LOW, tnom=3.0))]
    escena(6, "6 · El vecino", 72.0, s6, amb="tension", sfx=["pasos", "respira"], clima="tension", booms=[22.0, 38.0, 52.0])

    # ---------- 7 · CUADERNO 2: LOS HUESOS DEL OÍDO
    def s7(ctx):
        n2 = nb_shot(nb_oido(ctx["dur"], ctx["lineas"]), 2)
        p = actor(PRO, (-8.0, zb(-8.0) - 1.6), np.arctan2(-0.1, -0.99), speed=0.0, pose=p_idle(look=0.5))
        return [(24, n2), (8, cabeza("v_azul", p, side=0.9, fwd=0.9, h=0.25, f=2400)),
                (20, nb_shot(nb_oido(ctx["dur"], ctx["lineas"]), 4))]
    escena(7, "7 · Cuaderno: el oído", 44.0, s7, amb="cuaderno", sfx=["lapiz", "papel"], clima="misterio", booms=[])

    # ---------- 8 · LA SEQUÍA (óxido, río retirado)
    def s8(ctx):
        v = actor(VET, (-10.0, zb(-10.0, 1.4) - 1.5), np.arctan2(-0.1, -0.99), speed=0.6, ss=1.7)
        d = actor(DII, (-3.0, zb(-3.0, 1.4) - 2.0), np.arctan2(0.1, 0.99), speed=0.3)
        return [(6, land("v_oxido", (-40.0, 1.8, 3.0), 0.25, f=1000, pitch=0.03, move=(0.7, 0.0, 0.1), fg=FG_DRY)),
                (6, track("v_oxido", v, cam=(2.4, -3.8, 0.55), f=3200, v=0.58, u=0.5, ap=0.010, fg=FG_DRY)),
                (5, land("v_oxido", (-14.0, 0.45, 2.0), 0.4, f=1700, pitch=0.0, move=(0.1, 0.0, 0.3), fg=FG_DRY)),
                (7, track("v_oxido", d, cam=(1.4, -2.0, 0.35), f=3600, v=0.58, u=0.5, ap=0.009, fg=FG_LOW)),
                (7, land("v_oxido", (-8.0, 2.0, 1.0), 1.1, f=1000, pitch=0.18, move=(0.0, 0.0, 0.5), dpitch=-0.01, fg=FG_DRY))]
    escena(8, "8 · La sequía", 46.0, s8, amb="sequia", sfx=["pasos"], clima="tension", booms=[6.0, 22.0])

    # ---------- 9 · LA NUBE (ceniza)
    def s9(ctx):
        v = actor(VET, (-12.0, zb(-12.0, 1.0) - 1.8), np.arctan2(-0.1, -0.99), speed=1.4)
        g = actor(GOR, (-16.0, zb(-16.0, 1.0) - 3.0), np.arctan2(0.0, 1.0), speed=1.0)
        return [(6, land("v_ceniza", (-30.0, 2.0, 2.0), 0.2, f=900, pitch=0.12, move=(0.3, 0.0, 0.3), fg=FG_DRY)),
                (6, track("v_ceniza", v, cam=(2.4, -4.0, 0.7), f=3200, v=0.58, u=0.5, ap=0.012, fg=FG_DRY)),
                (7, land("v_ceniza", (-8.0, 1.2, 3.0), 0.55, f=1200, pitch=0.03, move=(0.3, 0.0, 0.3), actors=(g,), fg=FG_FRAME_R)),
                (7, track("v_ceniza_selva", g, cam=(3.0, -4.5, 0.8), f=3200, v=0.58, u=0.5, ap=0.014, fg=FG_L)),
                (6, land("v_ceniza", (-20.0, 1.6, 0.5), 0.0, f=800, pitch=0.2, move=(0.0, 0.2, 0.9), dpitch=-0.02, fg=FG_BRANCH)),
                (6, track("v_ceniza", v, cam=(1.6, -3.0, 0.5), f=2600, v=0.58, u=0.5, ap=0.004, fg=FG_LOW))]
    escena(9, "9 · La nube", 56.0, s9, amb="ceniza", sfx=["pasos"], clima="drama", booms=[3.0, 13.0, 30.0, 44.0])

    # ---------- 10 · EL REFUGIO (noche azul)
    def s10(ctx):
        v = actor(VET, (-6.0, zb(-6.0) - 1.9), np.arctan2(-0.2, -0.98), speed=0.0, pose=p_idle(look=0.4))
        p = actor(PRO, (-7.4, zb(-7.4) - 1.7), np.arctan2(-0.15, -0.99), speed=0.0, pose=p_idle(look=0.6))
        w = actor(VET, (-1.0, zb(-1.0) - 2.0), np.arctan2(-0.1, -0.99), speed=0.5)
        return [(6, land("v_noche", (-22.0, 1.5, 2.0), 0.3, f=1000, pitch=0.04, move=(0.4, 0.0, 0.1), actors=(w,), fg=FG_LOW)),
                (7, cabeza("v_noche", v, side=1.5, fwd=1.7, h=0.45, f=2300, extra=(p,))),
                (7, track("v_noche", v, cam=(2.4, -1.8, 0.5), f=2900, v=0.58, u=0.5, ap=0.010, extra=(p,), fg=FG_FRAME_L)),
                (7, track("v_noche", w, cam=(2.6, -4.0, 0.7), f=3400, v=0.58, u=0.5, ap=0.012, fg=FG_LR)),
                (6, land("v_noche", (-10.0, 0.4, 3.0), 0.5, f=1600, pitch=0.0, move=(0.1, 0.0, 0.3), fg=FG_REED))]
    escena(10, "10 · El refugio", 50.0, s10, amb="noche", sfx=["respira"], clima="ternura", booms=[])

    # ---------- 11 · TU PARIENTE (ámbar suave) + cartel final
    def s11(ctx):
        v = actor(VET, (-4.0, zb(-4.0) - 1.9), np.arctan2(-0.15, -0.99), speed=0.5)
        q = quieto(VET, -9.0, np.arctan2(-0.1, -0.99), p_idle(look=0.35))
        cart = K.gfx(montaje.cartel, native=False, texto="ESTE CAMINO LLEVA A VOS", variante=1)
        return [(7, track("v_ambar", v, cam=(2.4, -4.0, 0.55), f=3000, v=0.58, u=0.5, ap=0.004, fg=FG_LR)),
                (7, cabeza("v_ambar", q, side=1.7, fwd=2.0, f=2500)),
                (6, land("v_ambar", (-14.0, 1.5, 4.0), 0.1, f=1200, pitch=0.03, move=(0.3, 0.0, 0.4), actors=(q,), fg=FG_FRAME_R)),
                (6, cabeza("v_ambar", q, side=0.8, fwd=2.2, h=0.4, f=2900, fg=FG_LOW)),
                (5, cart)]
    escena(11, "11 · Tu pariente", 40.0, s11, marcos=[(2, 0.3, "VETUSODON ELIKHULU · 2019")], amb="final", clima="final", booms=[6.0, 18.0, 30.0])

    # ---------- 12 · PELEA (BOOM 1, reconstrucción)
    def s12(ctx):
        z = zb(-7.0) - 2.0
        a = actor(VET, (-8.0, z), 0.0, speed=0.0, pose=p_fight(VET, 0.0))
        b = actor(VET, (-6.0, z), np.pi, speed=0.0, pose=p_fight(VET, 0.85))
        carc = actor(DII, (-7.0, z + 0.9), 0.4, speed=0.0, pose=p_lie(sleep=True))
        ex = (b, carc)
        return [(6, track("v_oxido", a, cam=(3.2, -0.4, 0.55), f=2100, v=0.58, u=0.5, tgt=(1.0, 0.42), ap=0.004, extra=ex, pan=0.0, fg=FG_LOW)),
                (5, track("v_oxido", a, cam=(-3.2, 0.6, 0.55), f=2100, v=0.58, u=0.5, tgt=(1.0, 0.42), ap=0.004, extra=ex, pan=0.0, fg=FG_DRY)),
                (5, track("v_oxido", a, cam=(1.9, 1.5, 0.5), f=1800, v=0.56, u=0.5, tgt=(0.95, 0.44), ap=0.003, extra=ex, pan=0.0, zf=lambda t: 2.0, fg=FG_L)),
                (5, track("v_oxido", a, cam=(4.5, -1.5, 1.4), f=1500, v=0.58, u=0.5, tgt=(1.0, 0.40), ap=0.004, extra=ex, pan=0.0, fg=FG_FRAME_R)),
                (5, track("v_oxido", a, cam=(2.4, 0.4, 0.22), f=2200, v=0.60, u=0.5, tgt=(1.0, 0.40), ap=0.004, extra=ex, pan=0.0, fg=FG_LOW))]
    escena(12, "12 · La pelea", 32.0, s12, amb="tension", sfx=["respira", "pelea"], clima="boom", booms=[3.2, 7.0, 11.0, 16.0, 21.0])

    # ---------- 13 · CONFLICTO DE GRUPO + ARISTÓTELES (BOOM 2, reconstrucción)
    def s13(ctx):
        z = zb(-14.0) - 2.2
        v1 = actor(VET, (-14.0, z), np.pi, speed=0.0, pose=p_alerta(VET, 0.1))
        v2 = actor(VET, (-14.9, z - 0.7), np.pi, speed=0.0, pose=p_alerta(VET, -0.1))
        v3 = actor(VET, (-13.3, z - 1.2), np.pi, speed=0.0, pose=p_alerta(VET, 0.2))
        g = actor(GOR, (-21.0, z - 0.3), 0.0, speed=0.45, pose=p_stalk(GOR))
        ex = (v2, v3, g)
        return [(7, land("v_violeta", (-17.5, 1.3, z - 4.5), 0.0, f=1000, pitch=0.03, move=(0.1, 0.0, 0.1), actors=(v1, v2, v3, g), fg=FG_LOW)),
                (6, track("v_violeta", v1, cam=(2.8, -2.8, 0.6), f=2500, v=0.58, u=0.5, ap=0.004, extra=ex, pan=0.0, fg=FG_L)),
                (6, track("v_violeta", g, cam=(2.6, 2.4, 0.6), f=2800, v=0.58, u=0.5, ap=0.004, extra=(v1, v2, v3), tgt=(0.6, 0.45), fg=FG_REED)),
                (6, cabeza("v_violeta", v1, side=1.4, fwd=1.8, f=2300, extra=ex)),
                (6, track("v_violeta", v3, cam=(-3.0, 0.5, 0.7), f=2000, v=0.58, u=0.5, ap=0.004, extra=(v1, v2, g), pan=0.0, fg=FG_FRAME_L))]
    escena(13, "13 · El grupo", 34.0, s13, amb="tension", sfx=["respira"], clima="drama", booms=[6.0, 16.0, 24.0])

    # ---------- 14 · LYSTROSAURUS: LA ESPECIE INVASORA (BOOM 7)
    def s14(ctx):
        zr = zb(-24.0, 1.0)
        herd = [actor(LYS, (-31.0 + 1.5 * (i % 4) + 0.9 * (i // 4), zr - 2.3 - 0.9 * (i % 3) - 0.7 * (i // 4)),
                      np.arctan2(0.03 * (i % 3 - 1), 1.0), speed=1.0 + 0.08 * (i % 3)) for i in range(10)]
        lead = herd[1]
        otros = lambda a: tuple(h for h in herd if h is not a)
        return [(7, land("v_oxido", (-28.0, 1.8, zr - 9.5), 0.0, f=800, pitch=0.05, move=(0.12, 0.0, 0.05), actors=tuple(herd), fg=FG_DRY)),
                (6, track("v_oxido", lead, cam=(3.0, -2.5, 0.55), f=2300, v=0.58, u=0.5, ap=0.004, extra=otros(lead), fg=FG_DRY, tnom=3.0)),
                (6, track("v_oxido", lead, cam=(1.4, 2.4, 0.40), f=2400, v=0.58, u=0.5, ap=0.004, extra=otros(lead), tgt=(0.5, 0.30), fg=FG_LOW, tnom=3.0)),
                (6, land("v_oxido", (-28.0, 4.2, zr - 7.5), 0.0, f=800, pitch=0.28, move=(0.3, 0.0, 0.2), actors=tuple(herd), fg=FG_BRANCH)),
                (6, track("v_oxido", herd[4], cam=(2.2, -2.0, 0.5), f=2400, v=0.58, u=0.5, ap=0.004, extra=otros(herd[4]), fg=FG_FRAME_L, tnom=3.0))]
    escena(14, "14 · Lystrosaurus", 40.0, s14, amb="sequia", sfx=["pasos"], clima="boom", booms=[4.0, 16.0, 28.0])

    out.sort(key=lambda c: GD.ORDEN.index(c["esc"]))
    return out


# ---------------------------------------------------------------- línea de tiempo
TL = None
TOMAS = None


def timeline():
    world.load()
    vd = voz_dur()
    esc = build(vd)
    t0 = 0.0
    for c in esc:
        shots = c["shots_fn"](dict(c["ctx"], marcos=c["marcos"]))
        wsum = sum(w for w, _ in shots)
        ts, lst, acc = 0.0, [], 0
        for k, (w, sh) in enumerate(shots):
            n = round(c["dur"] * FPS * w / wsum) if k < len(shots) - 1 else round(c["dur"] * FPS) - acc
            n = max(n, 12)
            acc += n
            lst.append((ts, n / FPS, sh))
            ts += n / FPS
        for _, _, sh in lst:
            if "aperture" in sh:
                sh["aperture"] = min(sh["aperture"], 0.004)      # menos desenfoque: el animal siempre nítido
        c["shots"], c["dur"] = lst, ts
        c["t0"] = t0
        t0 += ts
    return esc, t0


def init():
    global TL
    cv2.setNumThreads(1)
    world.load()
    engine.setup()
    TL, _ = timeline()
    for c in TL:
        for ts, d, sh in c["shots"]:
            finalize(sh, d)


def tomas_cache():
    """Fotos del montaje: 640x360, de plantas, tierra, insectos y el animal. Se guardan en el cache."""
    d = Path(world.CACHE) / "tomas"
    d.mkdir(exist_ok=True)
    return d


def hacer_tomas():
    world.load()
    engine.setup()
    d = tomas_cache()
    v = actor(VET, (-5.0, zb(-5.0) - 1.9), np.arctan2(-0.2, -0.98), speed=0.8)
    g = actor(GOR, (-20.0, zb(-20.0) - 3.0), np.arctan2(0.0, 1.0), speed=0.8)
    p = actor(PRO, (-9.0, zb(-9.0) - 1.6), np.arctan2(-0.1, -0.99), speed=0.5)
    S = [("v_ambar", track("v_ambar", v, cam=(1.0, -2.2, 0.35), f=5200, v=0.6, u=0.5, tgt=(-0.55, 0.30), ap=0.008, fg=FG_LOW)),      # cola anillada
         ("v_ambar", track("v_ambar", v, cam=(0.9, 1.7, 0.40), f=6400, v=0.56, u=0.5, tgt=(0.7, 0.40), ap=0.006, fg=FG_L)),          # cara
         ("v_violeta", land("v_violeta", (-30, 0.5, 5), 0.3, f=2400, pitch=0.0, fg=FG_REED)),
         ("v_azul", land("v_azul", (-22, 0.4, 4), 0.2, f=2600, pitch=0.02, fg=FG_LOW)),
         ("v_oxido", land("v_oxido", (-12, 0.3, 2.5), 0.5, f=3000, pitch=0.0, fg=FG_DRY)),
         ("v_ambar", land("v_ambar", (-14, 1.0, 3.0), 0.1, f=2200, pitch=0.2, fg=FG_BRANCH)),
         ("v_esmeralda", land("v_esmeralda", (-35, 0.5, 5), 0.0, f=2400, pitch=0.0, fg=FG_L)),
         ("v_ceniza", land("v_ceniza", (-8, 0.4, 2.5), 0.4, f=2800, pitch=0.0, fg=FG_DRY)),
         ("v_noche", track("v_noche", p, cam=(0.8, 1.0, 0.28), f=5200, v=0.58, u=0.5, tgt=(0.4, 0.2), ap=0.007, fg=FG_L)),
         ("v_oxido", track("v_oxido", g, cam=(1.5, 2.0, 0.6), f=4200, v=0.58, u=0.5, tgt=(0.6, 0.5), ap=0.008, fg=FG_LOW)),             # gorgonopsio, colmillos
         ("v_violeta", land("v_violeta", (-45, 1.4, 6), 0.6, f=1500, pitch=0.1, fg=FG_FRAME_R)),
         ("v_azul", land("v_azul", (-18, 3.0, 2), 0.1, f=1500, pitch=0.35, fg=FG_BRANCH_R)),
         ("v_ambar", track("v_ambar", v, cam=(0.6, -1.2, 0.25), f=7000, v=0.62, u=0.5, tgt=(-0.1, 0.12), ap=0.006, fg=FG_LOW)),           # patas
         ("v_violeta", land("v_violeta", (-26, 0.35, 3), 0.7, f=3200, pitch=0.0, fg=FG_L))]
    for i, (_, sh) in enumerate(S):
        f = d / f"t{i:02d}.png"
        if f.exists():
            continue
        finalize(sh, 3.0)
        img = engine.frame(sh, 1.2 + 0.1 * i, 960, 540)
        cv2.imwrite(str(f), cv2.cvtColor((np.clip(img, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
        print("toma", i, flush=True)


def cargar_tomas():
    global TOMAS
    if TOMAS is None:
        d = tomas_cache()
        fs = sorted(d.glob("t*.png"))
        if not fs:
            hacer_tomas()
            fs = sorted(d.glob("t*.png"))
        TOMAS = [cv2.cvtColor(cv2.imread(str(f)), cv2.COLOR_BGR2RGB).astype(np.float32) / 255 for f in fs]
    return TOMAS


# ---------------------------------------------------------------- fotogramas
def escena_en(t):
    for c in TL:
        if c["t0"] <= t < c["t0"] + c["dur"] - 1e-9:
            return c
    return TL[-1]


def render_frame(i, W, H):
    t = i / FPS
    c = escena_en(t)
    lt = t - c["t0"]
    for ts, d, sh in c["shots"]:
        if ts <= lt < ts + d + 1e-6:
            break
    ls = lt - ts
    if "gfx" in sh:
        kw = {}
        if sh.get("tomas_lazy"):
            kw["tomas"] = cargar_tomas()
        # el reloj del montaje es el de la escena (no el del plano) para que los cortes y el marco coincidan con la voz
        img = sh["gfx"](lt if sh.get("tomas_lazy") else ls, W, H, c["dur"] if sh.get("tomas_lazy") else d, **kw) if not kw else \
            montaje.montaje(lt, W, H, c["dur"], tomas=kw["tomas"], cortes=sh["cortes"], textos=[(a, b) for a, b in c["marcos"]],
                            seed=3 if c["esc"] == 0 else 9, variante=0 if c["esc"] == 0 else 1)
    else:
        img = engine.frame(sh, ls, W, H)
        for tm, tx in c["marcos"]:
            if c["esc"] not in (0, 5, 11) and tm <= lt < tm + 5.5:
                img = montaje.marco_overlay(img, lt - tm, tx, W, H)
        for tc, key, dd in c["cards"]:
            if tc <= lt < tc + dd:
                au, ro, en, es = GD.QUOTES[key]
                img = G.quote_overlay(img, lt - tc, dd, au, ro, es, en)          # español grande, original pequeño
    total = TL[-1]["t0"] + TL[-1]["dur"]
    fade = min(1.0, t / 0.6, (total - t) / 1.2)
    return (np.clip(img * max(fade, 0), 0, 1) * 255 + 0.5).astype(np.uint8)


def seg_path(c, j):
    return VIDEO / "segmentos" / f"s{c['esc']:02d}_{j:02d}.mp4"


def render_segment(args):
    import time
    ci, j = args
    c = TL[ci]
    out = seg_path(c, j)
    if out.exists():
        return str(out), 0.0
    ts, dd, sh = c["shots"][j]
    W, H = 1280, 720
    f0, nf = int(round((c["t0"] + ts) * FPS)), int(round(dd * FPS))
    tmp = out.with_suffix(".part.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-vf", "scale=1920:1080:flags=lanczos", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-threads", "2",
                           "-pix_fmt", "yuv420p", str(tmp)], stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(f0, f0 + nf):
        ff.stdin.write(render_frame(i, W, H).tobytes())
    ff.stdin.close()
    ff.wait()
    tmp.rename(out)
    return str(out), time.time() - t0


# ---------------------------------------------------------------- subtítulos
def partir(tx, maxc=34):
    pal, out, cur = tx.split(), [], ""
    for p in pal:
        if cur and len(cur) + 1 + len(p) > maxc:
            out.append(cur)
            cur = p
        else:
            cur = (cur + " " + p).strip()
    return out + ([cur] if cur else [])


def ts_srt(x):
    h, m, s = int(x // 3600), int(x % 3600 // 60), x % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)) % 1000:03d}"


def write_srt(path):
    n = 1
    with open(path, "w", encoding="utf-8") as fh:
        for c in TL:
            for t, d, tx in c["lineas"]:
                lines = partir(tx)
                bloques = [lines[i:i + 2] for i in range(0, len(lines), 2)]
                tot = sum(len(" ".join(b)) for b in bloques) or 1
                a = c["t0"] + t
                for b in bloques:
                    dd = d * len(" ".join(b)) / tot
                    fh.write(f"{n}\n{ts_srt(a)} --> {ts_srt(a + dd - 0.05)}\n" + "\n".join(b) + "\n\n")
                    a += dd
                    n += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tiempos", action="store_true")
    ap.add_argument("--preview")
    ap.add_argument("--only", type=int, nargs="*")
    ap.add_argument("--tomas", action="store_true")
    ap.add_argument("--seg", action="store_true")
    ap.add_argument("--srt", action="store_true")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--esc", type=int, nargs="*", help="solo estas escenas (con --seg)")
    a = ap.parse_args()
    global TL
    if a.tomas:
        hacer_tomas()
        return
    if a.tiempos or a.srt:
        TL, tot = timeline()
        for c in TL:
            print(f"{c['nombre']:34s} {c['t0'] / 60:5.2f} min  {c['dur']:6.1f} s  {len(c['shots'])} planos  {len(c['lineas'])} frases")
        print(f"TOTAL {tot / 60:.2f} min, {sum(len(c['shots']) for c in TL)} planos")
        if a.srt:
            VIDEO.mkdir(exist_ok=True)
            write_srt(VIDEO / "vetusodon.srt")
        return
    if a.preview:
        import time
        init()
        os.makedirs(a.preview, exist_ok=True)
        k = 0
        for c in TL:
            for j, (ts, dd, sh) in enumerate(c["shots"]):
                k += 1
                if a.only and k not in a.only:
                    continue
                t0 = time.time()
                f = int(round((c["t0"] + ts + min(dd * 0.4, 2.0)) * FPS))
                img = render_frame(f, 960, 540)
                cv2.imwrite(f"{a.preview}/{k:03d}_{c['esc']:02d}_{j}.jpg", cv2.cvtColor(img, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 90])
                print(f"{k:03d} {c['nombre']:28s} plano {j}  {time.time() - t0:5.1f}s", flush=True)
        return
    if a.seg:
        import time
        init()
        pend = [(ci, j) for ci, c in enumerate(TL) if not a.esc or c["esc"] in a.esc for j in range(len(c["shots"])) if not seg_path(c, j).exists()]
        nf = sum(int(round(TL[ci]["shots"][j][1] * FPS)) for ci, j in pend)
        print(f"{len(pend)} planos pendientes, {nf} fotogramas", flush=True)
        done, t0 = 0, time.time()
        import multiprocessing as mp
        with ProcessPoolExecutor(max_workers=a.jobs, mp_context=mp.get_context("fork"), initializer=cv2.setNumThreads, initargs=(1,)) as ex:
            futs = [ex.submit(render_segment, p) for p in pend]
            for f in futs:
                path, sec = f.result()
                done += 1
                msg = f"[{done}/{len(pend)}] {Path(path).name} {sec:5.0f}s · transcurrido {(time.time() - t0) / 60:5.1f} min"
                print(msg, flush=True)
                (VIDEO / "progreso.txt").write_text(msg + "\n")
        return
    ap.print_help()


if __name__ == "__main__":
    main()
