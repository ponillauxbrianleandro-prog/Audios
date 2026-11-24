#!/usr/bin/env python3
"""Pista de audio SIN VOZ para el documental «Vetusodon» (4 partes de ~5:00), generada desde escenas.json.

  python3 render/audio_doc.py --parte 2 [--escenas guion/escenas.json]
  python3 render/audio_doc.py --todo
  python3 render/audio_doc.py --prueba            # 30 s con escenas_prueba + informe de nivel/clipping/espectro

Capas (todas sintetizadas con numpy/scipy, vectorizado):
  1 musica   tango de musica/tango_v8.py (sol menor, 120 BPM) con automatizacion por escena: ganancia por instrumento,
             oscurecimiento (paso bajo), pad en sol menor / racimo disonante, latido grave en tension.
  2 ambiente por escena y paleta: viento, colas de caballo, insectos, agua, calor, ceniza, lluvia, bruma, truenos;
             estereo decorrelado, panoramica lenta, EQ por paleta y reverb Schroeder (combs + allpass) como envio.
  3 efectos  sincronizados con animales/acciones (pasos, olfateo, escarbar, comer, rugido, aleteo, respiracion...),
             mascota (pasos, ladrido, jadeo), Owen (lapiz, papel), clic de camara.
  4 mezcla   bolsillo EQ fijo para la voz (duck_db), ducking dinamico opcional si se pasa --voz, -16 LUFS, limitador.
"""
import argparse
import json
import re
import sys
import time
import unicodedata
import wave
import zlib
from pathlib import Path

import numpy as np
from scipy.ndimage import uniform_filter1d, minimum_filter1d
from scipy.signal import butter, sosfilt, lfilter, oaconvolve, resample_poly

SR = 44100
AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "musica"))
import tango_v8 as TG  # noqa: E402

F32 = np.float32


# ----------------------------------------------------------------------------- utilidades de DSP
def norm(s):
    s = unicodedata.normalize("NFD", str(s or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def seed_de(*a):
    return zlib.crc32("|".join(map(str, a)).encode()) & 0xFFFFFFFF


def ruido(n, rng):
    return rng.standard_normal(int(n))


def lp(x, fc, o=2):
    return sosfilt(butter(o, min(fc, SR * .45), "low", fs=SR, output="sos"), x)


def hp(x, fc, o=2):
    return sosfilt(butter(o, fc, "high", fs=SR, output="sos"), x)


def bp(x, a, b, o=2):
    return sosfilt(butter(o, [a, min(b, SR * .45)], "band", fs=SR, output="sos"), x)


def peaking(f0, gdb, q=0.8):
    A = 10 ** (gdb / 40)
    w = 2 * np.pi * f0 / SR
    al = np.sin(w) / (2 * q)
    b = np.array([1 + al * A, -2 * np.cos(w), 1 - al * A])
    a = np.array([1 + al / A, -2 * np.cos(w), 1 - al / A])
    return np.r_[b / a[0], 1, a[1] / a[0], a[2] / a[0]][None, :]


def lowshelf(f0, gdb, q=0.7):
    A = 10 ** (gdb / 40)
    w = 2 * np.pi * f0 / SR
    cw, al = np.cos(w), np.sin(w) / (2 * q)
    sq = 2 * np.sqrt(A) * al
    b0 = A * ((A + 1) - (A - 1) * cw + sq)
    b1 = 2 * A * ((A - 1) - (A + 1) * cw)
    b2 = A * ((A + 1) - (A - 1) * cw - sq)
    a0 = (A + 1) + (A - 1) * cw + sq
    a1 = -2 * ((A - 1) + (A + 1) * cw)
    a2 = (A + 1) + (A - 1) * cw - sq
    return np.array([[b0 / a0, b1 / a0, b2 / a0, 1, a1 / a0, a2 / a0]])


def suave(n, rng, hz, lo=0.0, hi=1.0, curva=1.0):
    """Envolvente aleatoria lenta (n muestras) entre lo y hi, ritmo aproximado hz."""
    pts = int(n / SR * hz) + 4
    v = rng.random(pts)
    x = np.interp(np.linspace(0, pts - 1, n), np.arange(pts), v)
    x = uniform_filter1d(x, max(3, int(SR / hz / 3)))
    x = (x - x.min()) / (np.ptp(x) + 1e-9)
    return lo + (hi - lo) * x ** curva


def pan_gains(p):
    p = float(np.clip(p, -1, 1))
    a = (p + 1) * np.pi / 4
    return np.cos(a), np.sin(a)


def est(x, pan=0.0):
    """mono -> estereo (n,2) con panoramica potencia constante."""
    l, r = pan_gains(pan)
    return np.stack([x * l, x * r], 1)


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(np.square(x, dtype=np.float64))) + 1e-12)


# ----------------------------------------------------------------------------- reverb Schroeder
def ir_schroeder(decay, seed, combs=(1557, 1617, 1491, 1422, 1277, 1356, 1188, 1116), ap=(556, 441, 341, 225), pre=0.012, dur=None):
    """Respuesta al impulso: 8 combs paralelos (con amortiguacion) + 4 allpass en serie; estereo por distinto juego de retardos."""
    dur = dur or decay * 1.25
    n = int(dur * SR)
    out = []
    for ch in range(2):
        rng = np.random.default_rng(seed + ch)
        imp = np.zeros(n)
        imp[0] = 1
        acc = np.zeros(n)
        for d in combs:
            d = int(d * (1 + 0.012 * ch + rng.uniform(-0.02, 0.02)) * SR / 44100)
            g = 10 ** (-3 * d / SR / decay)
            b = np.zeros(d + 1)
            b[d] = 1
            y = lfilter(b, [1] + [0] * (d - 1) + [-g], imp)
            acc += lp(y, 5500, 1) if False else y
        y = acc / len(combs)
        for d in ap:
            d = int(d * (1 + 0.01 * ch) * SR / 44100)
            b = np.zeros(d + 1)
            b[0] = -0.7
            b[d] = 1
            a = np.zeros(d + 1)
            a[0] = 1
            a[d] = -0.7
            y = lfilter(b, a, y)
        y = lp(y, 6500, 1) * np.exp(-np.arange(n) / SR * 0.2)           # aire absorbe agudos
        sh = int(pre * SR)
        y = np.r_[np.zeros(sh), y[:n - sh]]
        # reflexiones tempranas
        for k in range(6):
            i = int(rng.uniform(0.006, 0.06) * SR)
            y[i] += rng.uniform(0.2, 0.5) * (1 if rng.random() > .3 else -1)
        out.append(y)
    ir = np.stack(out, 1)
    return (ir / np.sqrt((ir ** 2).sum(0).max())).astype(F32) * 0.7


_IR = {}


def reverb(x2, kind, wet=1.0):
    """x2 (n,2) -> cola reverberada (n,2). kind: 'sala' (1.1 s) o 'valle' (3.2 s)."""
    if kind not in _IR:
        _IR[kind] = ir_schroeder(1.1 if kind == "sala" else 3.2, 11 if kind == "sala" else 23)
    ir = _IR[kind]
    n = len(x2)
    return np.stack([oaconvolve(x2[:, c], ir[:, c])[:n] for c in range(2)], 1).astype(F32) * wet


# ----------------------------------------------------------------------------- perfiles
# nivel de cada capa de ambiente 0..1, EQ (hicut Hz, locut Hz, bump (Hz, dB)), modo musical por defecto, reverb
PERFIL = {
    "ambar":   dict(viento=.35, colas=.55, insectos=.55, agua=0.0, calor=.15, ceniza=0, grave=.10, noche=False, hicut=9500, locut=60, bump=(2800, 1.5), rev=.30, modo="calma"),
    "violeta": dict(viento=.30, colas=.30, insectos=.50, agua=.15, calor=0.0, ceniza=0, grave=.25, noche=True, hicut=6500, locut=70, bump=(450, 2.0), rev=.45, modo="misterio"),
    "verde":   dict(viento=.22, colas=.75, insectos=.95, agua=.35, calor=0.0, ceniza=0, grave=.05, noche=False, hicut=10500, locut=70, bump=(4200, 2.0), rev=.30, modo="vivo"),
    "azul":    dict(viento=.55, colas=.15, insectos=.10, agua=.75, calor=0.0, ceniza=0, grave=.20, noche=False, hicut=7500, locut=90, bump=(1800, 1.5), rev=.50, modo="frio"),
    "rojo":    dict(viento=.50, colas=.05, insectos=.15, agua=0.0, calor=.85, ceniza=.15, grave=.40, noche=False, hicut=8000, locut=55, bump=(120, 3.0), rev=.35, modo="peligro"),
    "ocre":    dict(viento=.60, colas=.10, insectos=.30, agua=0.0, calor=.65, ceniza=0, grave=.10, noche=False, hicut=9000, locut=80, bump=(3500, 1.0), rev=.22, modo="marcha"),
    "ceniza":  dict(viento=.50, colas=0.0, insectos=0.0, agua=0.0, calor=0.0, ceniza=.85, grave=.70, noche=False, hicut=5200, locut=45, bump=(90, 3.0), rev=.55, modo="tension"),
}
PERFIL_DEF = PERFIL["ambar"]

# modo musical: ganancia por instrumento, pad, latido, oscurecimiento, tension (mezcla del pad disonante), nivel dB
MODOS = {
    "calma":    dict(bandoneon=.25, acordeon=.75, piano=.80, contrabajo=.55, guitarra=.80, pad=.50, latido=0, dark=.15, ten=0.0, db=0),
    "vivo":     dict(bandoneon=.60, acordeon=.70, piano=.80, contrabajo=.80, guitarra=.85, pad=.15, latido=0, dark=0.0, ten=0.0, db=0),
    "marcha":   dict(bandoneon=.70, acordeon=.50, piano=.80, contrabajo=1.0, guitarra=.70, pad=.10, latido=0, dark=0.05, ten=0.1, db=0),
    "misterio": dict(bandoneon=.35, acordeon=.45, piano=.60, contrabajo=.50, guitarra=.30, pad=.80, latido=.2, dark=.35, ten=.3, db=-1),
    "frio":     dict(bandoneon=.00, acordeon=.55, piano=.85, contrabajo=.40, guitarra=.50, pad=.60, latido=0, dark=.40, ten=.1, db=-1),
    "tension":  dict(bandoneon=.15, acordeon=.30, piano=.45, contrabajo=.75, guitarra=.00, pad=1.0, latido=.80, dark=.55, ten=1.0, db=0),
    "peligro":  dict(bandoneon=.55, acordeon=.30, piano=.75, contrabajo=1.0, guitarra=.00, pad=.70, latido=1.0, dark=.25, ten=.8, db=0),
    "calido":   dict(bandoneon=.80, acordeon=.90, piano=.90, contrabajo=.70, guitarra=.90, pad=.40, latido=0, dark=0.0, ten=0.0, db=0),
}
CLAVES_MODO = [  # (palabras en titulo/id, modo) - tienen prioridad sobre la paleta
    (("amanec", "alba", "madrug", "calma", "nace"), "calma"),
    (("siberia", "trampa", "volcan", "ceniza", "extincion", "lluvia acida", "muerte", "agoniz"), "tension"),
    (("gorgon", "deprad", "persec", "acech", "peligro"), "peligro"),
    (("pelo", "final", "epilog", "sobrevi", "herencia", "hoy", "legado"), "calido"),
    (("madriguera", "noche", "luna"), "misterio"),
]


def modo_de(esc):
    txt = norm(f"{esc.get('titulo', '')} {esc.get('id', '')} {esc.get('modo_musica', '')}")
    if esc.get("modo_musica") in MODOS:
        return esc["modo_musica"]
    for claves, m in CLAVES_MODO:
        if any(c in txt for c in claves):
            return m
    if any("gorgon" in norm(a.get("especie")) for a in esc.get("animales") or []):
        return "peligro"
    return perfil(esc)["modo"]


def perfil(esc):
    return PERFIL.get(norm(esc.get("paleta")), PERFIL_DEF)


# ----------------------------------------------------------------------------- escenas
def escenas_prueba():
    """30 s: amanecer ambar (insectos + viento), gorgonopsio en rojo, ceniza (Siberia). Esquema igual al de escenas.json."""
    return [
        dict(id="p01_apertura", parte=0, titulo="Apertura amanecer", paleta="ambar", dur=10, suelo="tierra",
             clima=dict(bruma=.3, particulas="polen", rayos=0),
             clics=[0.0, .7, 1.3, 1.9, 2.4],
             animales=[dict(especie="vetusodon", accion="olfatear", t0=3, t1=5), dict(especie="vetusodon", accion="caminar", t0=5, t1=9.5),
                       dict(especie="insecto", accion="aletear", t0=6.5, t1=8.5)],
             mascota=dict(accion="caminar", t0=4, t1=8, ladra=[8.6]), owen=dict(accion="escribir", t0=1, t1=3.5)),
        dict(id="p02_gorgon", parte=0, titulo="El gorgonopsio vigila", paleta="rojo", dur=10, suelo="arena",
             clima=dict(bruma=.15, particulas="polvo", rayos=0),
             animales=[dict(especie="gorgonopsio", accion="caminar", t0=0.5, t1=4), dict(especie="gorgonopsio", accion="rugir", t0=4.5, t1=6.5),
                       dict(especie="vetusodon", accion="quieto", t0=0, t1=5), dict(especie="vetusodon", accion="escarbar", t0=6.5, t1=9),
                       dict(especie="anfibio", accion="huir", t0=4.6, t1=6)]),
        dict(id="p03_siberia", parte=0, titulo="Trampas Siberianas", paleta="ceniza", dur=10, suelo="ceniza",
             clima=dict(bruma=.7, particulas="ceniza", rayos=1),
             animales=[dict(especie="vetusodon", accion="comer", t0=1, t1=3.5), dict(especie="vetusodon", accion="caminar", t0=5, t1=9)],
             owen=dict(accion="pasar_pagina", t0=6, t1=7)),
    ]


def cargar_escenas(ruta, parte):
    if ruta:
        ruta = Path(ruta)
    else:   # primero guion/escenas.json (ruta acordada), luego escenas.json en la raiz del episodio
        ruta = next((c for c in (RAIZ / "guion" / "escenas.json", RAIZ / "escenas.json") if c.exists()), RAIZ / "guion" / "escenas.json")
    if ruta.exists():
        d = json.loads(ruta.read_text())
        lst = d["escenas"] if isinstance(d, dict) and "escenas" in d else d
        sel = [e for e in lst if int(e.get("parte", 0)) == parte]
        if sel:
            return sel
        print(f"[aviso] {ruta} no tiene escenas de la parte {parte}; uso escenas_prueba repetidas", file=sys.stderr)
    else:
        print(f"[aviso] no existe {ruta}; uso escenas_prueba repetidas", file=sys.stderr)
    base = escenas_prueba()
    return [dict(b, id=f"{b['id']}_{k}", parte=parte) for k in range(10) for b in base]


# ----------------------------------------------------------------------------- AMBIENTES
def gust(n, rng, hz=.12, prof=1.0):
    return suave(n, rng, hz, 1 - prof, 1.0, 1.4)


def a_viento(n, rng, fz):
    out = np.zeros((n, 2))
    g = gust(n, rng, .10 + .1 * fz, .85)
    for c in range(2):
        x = lp(ruido(n, rng), 280 + 700 * fz * g.mean(), 2)
        x = x * (0.25 + .75 * g)
        sil = bp(ruido(n, rng), 650, 1300) * g ** 3 * .12 * fz                   # silbido en rachas
        out[:, c] = (x + sil) * (0.16 + 0.4 * fz)
    return out


def a_colas(n, rng, fz):
    """viento entre colas de caballo: susurro de cañas, rafagas de alta frecuencia con flameo."""
    g = gust(n, rng, .15, .9)
    out = np.zeros((n, 2))
    for c in range(2):
        flame = np.clip(lp(ruido(n, rng), 14, 1) * 6 + .6, 0, 1.4) ** 1.2
        x = bp(ruido(n, rng), 2200, 7800) * flame * g ** 1.5
        x += bp(ruido(n, rng), 600, 1800) * g ** 2 * .35
        out[:, c] = x * .09 * fz * 2
    # crujidos secos de tallos
    for _ in range(int(n / SR * 1.2 * fz) + 1):
        i = rng.integers(0, n - 800)
        k = np.arange(800) / SR
        s = bp(ruido(800, rng), 1500, 6000) * np.exp(-k * 600) * rng.uniform(.03, .09)
        p = rng.uniform(-1, 1)
        l, r = pan_gains(p)
        out[i:i + 800, 0] += s * l
        out[i:i + 800, 1] += s * r
    return out


def a_insectos(n, rng, fz, noche):
    out = np.zeros((n, 2))
    k = int(n / SR * .55 * fz) + 1
    for _ in range(k):
        f = rng.uniform(3000, 4300) if noche else rng.uniform(2600, 6300)
        L = rng.uniform(1.2, 4.5)
        m = int(L * SR)
        if rng.random() < .55:     # grillo: grupos de pulsos
            r = rng.uniform(26, 38) if not noche else rng.uniform(14, 22)
            t = np.arange(m) / SR
            gate = np.clip(np.sin(2 * np.pi * r * t), 0, 1) ** .6 * (np.sin(2 * np.pi * rng.uniform(1.2, 2.2) * t) > -.2)
            x = np.sin(2 * np.pi * f * t + 3 * np.sin(2 * np.pi * 7 * t)) * gate
        else:                      # cigarra / zumbido continuo con AM
            t = np.arange(m) / SR
            x = np.sin(2 * np.pi * f * t) * (.6 + .4 * np.sin(2 * np.pi * rng.uniform(80, 150) * t)) * (.7 + .3 * np.sin(2 * np.pi * .8 * t))
        x = x * np.sin(np.pi * np.arange(m) / m) ** 2 * rng.uniform(.01, .04)
        i = rng.integers(0, max(1, n - m))
        d = rng.uniform(0, 1)
        if d > .5:
            x = lp(x, 7000 - 3500 * d, 1)
        p = rng.uniform(-1, 1)
        l, r = pan_gains(p)
        out[i:i + m, 0] += x[:n - i] * l * (1 - .4 * d)
        out[i:i + m, 1] += x[:n - i] * r * (1 - .4 * d)
    return out


def a_agua(n, rng, fz):
    out = np.zeros((n, 2))
    t = np.arange(n) / SR
    for c in range(2):
        x = bp(ruido(n, rng), 350, 2600)
        burb = lp(ruido(n, rng), 11, 1)
        burb = np.clip(burb / (burb.std() + 1e-9) * .5 + .8, .2, 1.8)
        x = x * burb * suave(n, rng, .3, .6, 1)
        x += lp(ruido(n, rng), 160) * 1.2
        out[:, c] = x * .09 * (.3 + fz)
    for _ in range(int(n / SR * 3.5 * fz) + 1):             # gotas
        f = rng.uniform(500, 2600)
        m = int(.08 * SR)
        tt = np.arange(m) / SR
        s = np.sin(2 * np.pi * f * (1 + 4 * tt) * tt) * np.exp(-tt * 55) * rng.uniform(.02, .09)
        i = rng.integers(0, max(1, n - m))
        l, r = pan_gains(rng.uniform(-1, 1))
        out[i:i + m, 0] += s[:n - i] * l
        out[i:i + m, 1] += s[:n - i] * r
    return out


def a_calor(n, rng, fz):
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    for c in range(2):
        sh = bp(ruido(n, rng), 5200, 9800) * (.4 + .6 * suave(n, rng, .25))
        hu = lp(ruido(n, rng), 140) * .8
        cig = np.sin(2 * np.pi * (4700 + 300 * c) * t + 4 * np.sin(2 * np.pi * .5 * t)) * (.5 + .5 * np.sin(2 * np.pi * 95 * t)) * suave(n, rng, .12, 0, 1, 2)
        out[:, c] = (sh * .05 + hu * .08 + cig * .02) * fz
    return out


def a_ceniza(n, rng, fz):
    out = np.zeros((n, 2))
    t = np.arange(n) / SR
    for c in range(2):
        s = bp(ruido(n, rng), 700, 3300) * suave(n, rng, .2, .4, 1) * .05
        ru = lp(ruido(n, rng), 70, 2) * 3.0
        ru += (np.sin(2 * np.pi * 38 * t) + np.sin(2 * np.pi * (41.5 + c * .4) * t)) * .15
        ru *= suave(n, rng, .09, .35, 1)
        out[:, c] = (s + ru * .09) * fz
    for _ in range(int(n / SR * 7 * fz) + 1):               # brasas
        m = int(.02 * SR)
        k = np.arange(m) / SR
        s = hp(ruido(m, rng), 2000, 1) * np.exp(-k * 280) * rng.uniform(.02, .10)
        i = rng.integers(0, max(1, n - m))
        l, r = pan_gains(rng.uniform(-1, 1))
        out[i:i + m, 0] += s[:n - i] * l
        out[i:i + m, 1] += s[:n - i] * r
    for _ in range(int(n / SR / 14 * fz) + 1):              # retumbo lejano
        m = int(rng.uniform(4, 7) * SR)
        if m >= n:
            continue
        k = np.arange(m) / SR
        s = lp(ruido(m, rng), 95, 2) * 8 * np.minimum(1, k / 1.2) * np.exp(-k * .6) * .12
        i = rng.integers(0, n - m)
        out[i:i + m] += s[:, None] * np.array([.9, .9])
    return out


def a_lluvia(n, rng, fz, acida):
    out = np.zeros((n, 2))
    for c in range(2):
        x = hp(ruido(n, rng), 1400) * (.6 + .4 * suave(n, rng, .3)) * .045 * fz
        x += bp(ruido(n, rng), 300, 900) * .02 * fz
        if acida:
            x += bp(ruido(n, rng), 4500, 10000) * (np.clip(lp(ruido(n, rng), 30, 1) * 8, 0, 1)) * .035 * fz   # chisporroteo
        out[:, c] = x
    return out


def a_trueno(n, rng, cnt):
    out = np.zeros((n, 2))
    for _ in range(cnt):
        m = int(rng.uniform(3, 5) * SR)
        if m >= n:
            continue
        k = np.arange(m) / SR
        x = lp(ruido(m, rng), 140) * 5 * (np.exp(-k * .9) * (.6 + .4 * np.abs(np.sin(k * 9 + rng.uniform(0, 6)))))
        x[:int(.05 * SR)] += bp(ruido(int(.05 * SR), rng), 800, 4500) * .8 * np.exp(-np.arange(int(.05 * SR)) / SR * 80)
        x *= np.minimum(1, k / .02) * .22
        i = rng.integers(0, n - m)
        out[i:i + m] += np.stack([x, x * rng.uniform(.7, 1)], 1)
    return out


def a_aire(n, rng, nivel, grave):
    """tono de sala: nunca silencio absoluto; colchon grave y aire."""
    out = np.zeros((n, 2))
    t = np.arange(n) / SR
    for c in range(2):
        x = lp(ruido(n, rng), 220) * .5 + bp(ruido(n, rng), 200, 900) * .12 * nivel
        x += np.sin(2 * np.pi * (47 + c * .6) * t) * .07 * grave
        out[:, c] = x * .05
    return out


def ambiente(esc, dur, xf, rng):
    """Sintetiza el ambiente de una escena con xf s de margen a cada lado. Devuelve (n,2)."""
    p = perfil(esc)
    cl = esc.get("clima") or {}
    bruma = float(cl.get("bruma") or 0) if not isinstance(cl.get("bruma"), bool) else (.6 if cl.get("bruma") else 0)
    part = norm(cl.get("particulas")) if not isinstance(cl.get("particulas"), (int, float)) else ("polvo" if cl.get("particulas") else "")
    suelo = norm(esc.get("suelo"))
    rayos = cl.get("rayos") or 0
    n = int((dur + 2 * xf) * SR)
    lv = {k: p[k] for k in ("viento", "colas", "insectos", "agua", "calor", "ceniza", "grave")}
    if any(w in suelo for w in ("agua", "rio", "lago", "orilla", "pantano", "barro")):
        lv["agua"] = max(lv["agua"], .55)
    if any(w in suelo for w in ("arena", "desierto", "duna")):
        lv["calor"] = max(lv["calor"], .4)
        lv["viento"] = max(lv["viento"], .5)
    if any(w in suelo for w in ("ceniza", "lava", "volcan")):
        lv["ceniza"] = max(lv["ceniza"], .6)
    if "ceniza" in part:
        lv["ceniza"] = max(lv["ceniza"], .85)
    lluvia = "lluvia" in part
    acida = lluvia and (norm(p.get("modo")) in ("tension", "peligro") or "acid" in norm(esc.get("titulo")) or "acid" in part)
    x = a_aire(n, rng, 1, lv["grave"] + .3 * bruma)
    if lv["viento"] > .02:
        x += a_viento(n, rng, lv["viento"] * (1 + .3 * (rayos > 0)))
    if lv["colas"] > .02:
        x += a_colas(n, rng, lv["colas"])
    if lv["insectos"] > .02:
        x += a_insectos(n, rng, lv["insectos"] * (1 - .5 * bruma), p["noche"])
    if lv["agua"] > .02:
        x += a_agua(n, rng, lv["agua"])
    if lv["calor"] > .02:
        x += a_calor(n, rng, lv["calor"])
    if lv["ceniza"] > .02:
        x += a_ceniza(n, rng, lv["ceniza"])
    if lluvia:
        x += a_lluvia(n, rng, 1.0, acida)
    if rayos:
        x += a_trueno(n, rng, max(1, int(dur / 9 * min(2, float(rayos)))))
    # EQ por paleta; la bruma amortigua los agudos y aleja
    hic = p["hicut"] * (1 - .55 * bruma)
    f, g = p["bump"]
    sos = np.vstack([butter(2, p["locut"], "high", fs=SR, output="sos"), butter(2, hic, "low", fs=SR, output="sos"), peaking(f, g, .7)])
    x = sosfilt(sos, x, axis=0)
    # panoramica y profundidad: el campo estereo rota muy lento (m/s para ensanchar)
    mid, side = (x[:, 0] + x[:, 1]) / 2, (x[:, 0] - x[:, 1]) / 2
    wid = 1.15 + .3 * suave(n, rng, .05)
    x = np.stack([mid + side * wid, mid - side * wid], 1)
    return x.astype(F32)


# ----------------------------------------------------------------------------- EFECTOS
def _p(x):
    return x / (np.abs(x).max() + 1e-9)


def f_paso(rng, pesado=.5, mat="tierra"):
    n = int(.38 * SR)
    t = np.arange(n) / SR
    c = 180 + 360 * (1 - pesado) * rng.uniform(.8, 1.2)
    base = lp(ruido(n, rng), c) * np.exp(-t * (20 + 8 * (1 - pesado)))
    cuerpo = np.sin(2 * np.pi * (55 + 45 * (1 - pesado)) * rng.uniform(.9, 1.1) * t) * np.exp(-t * 24) * pesado
    if "arena" in mat or "polvo" in mat:
        tex = bp(ruido(n, rng), 1200, 5200) * np.exp(-t * 13) * .55
    elif "ceniza" in mat:
        tex = bp(ruido(n, rng), 500, 3000) * np.exp(-t * 10) * .65
    elif "barro" in mat or "agua" in mat:
        tex = lp(ruido(n, rng), 900) * np.exp(-t * 7) * .8
        tex += bp(ruido(n, rng), 1000, 3500) * np.exp(-t * 18) * .25 * (np.sin(2 * np.pi * 30 * t) > 0)
    elif "roca" in mat or "piedra" in mat:
        tex = bp(ruido(n, rng), 1500, 6000) * np.exp(-t * 40) * .5
    else:  # tierra / helecho / hojarasca
        tex = bp(ruido(n, rng), 800, 3800) * np.exp(-t * 24) * .38
        tex += bp(ruido(n, rng), 3000, 8000) * np.exp(-t * 60) * .12 * rng.random()
    return _p((base + cuerpo + tex) * np.minimum(1, t / .003)) * .55


def f_olfateo(rng, dur):
    n = int(dur * SR)
    x = np.zeros(n)
    k = max(2, int(dur / .17))
    pos = np.cumsum(rng.uniform(.11, .2, k))
    for i, tt in enumerate(pos):
        j = int(tt * SR)
        m = int(.09 * SR)
        if j + m >= n:
            break
        s = bp(ruido(m, rng), 1400 + 200 * i, 5800) * np.sin(np.pi * np.arange(m) / m) ** 1.5
        x[j:j + m] += s * (.7 + .3 * rng.random())
    return _p(x) * .22 if np.abs(x).max() > 0 else x


def f_escarbar(rng, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    r = rng.uniform(5.5, 7.5)
    gate = np.clip(np.sin(2 * np.pi * r * t) ** 3, 0, 1) * (.7 + .3 * rng.random(n // 800 + 2).repeat(800)[:n])
    x = bp(ruido(n, rng), 500, 4200) * gate
    x += bp(ruido(n, rng), 120, 600) * gate * .6
    gr = lp(ruido(n, rng), 1500) * (np.clip(lp(ruido(n, rng), 9, 1) * 5, 0, 1)) * .25     # tierra que cae
    x = (x + gr) * np.minimum(1, t / .08) * np.minimum(1, (dur - t) / .12)
    return x / (np.abs(x).max() + 1e-9) * .3


def f_comer(rng, dur):
    n = int(dur * SR)
    x = np.zeros(n)
    tt = 0.05
    while tt < dur - .15:
        m = int(rng.uniform(.04, .09) * SR)
        j = int(tt * SR)
        k = np.arange(m) / SR
        s = bp(ruido(m, rng), 900, 3800) * np.exp(-k * rng.uniform(55, 110)) * rng.uniform(.4, 1)
        s += lp(ruido(m, rng), 380) * np.exp(-k * 40) * .5
        if rng.random() < .35:
            s += bp(ruido(m, rng), 2500, 7000) * np.exp(-k * 160) * .7        # crujido
        x[j:j + m] += s[:n - j]
        tt += rng.uniform(.17, .36)
    return _p(x) * .3 if np.abs(x).max() > 0 else x


def f_rugido(rng, dur=2.0, f0=72.0, tipo="rugido"):
    """Gorgonopsio: fundamental grave con subarmonico, rattle (AM 25-35 Hz), formantes abiertos, saturacion suave."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    env = np.minimum(1, t / (.12 if tipo == "rugido" else .3)) * np.exp(-np.maximum(0, t - dur * .45) * (1.6 if tipo == "rugido" else 2.2)) * (.85 + .15 * np.sin(2 * np.pi * 3.4 * t))
    f = f0 * (1.35 - .35 * (t / dur)) * (1 + .035 * np.sin(2 * np.pi * 5.2 * t) + .02 * lp(ruido(n, rng), 20, 1) * 4)
    ph = 2 * np.pi * np.cumsum(f) / SR
    src = sum(np.sin(k * ph + .3 * k) / k ** .8 for k in range(1, 14)) + .55 * np.sin(ph / 2)
    rat = .55 + .45 * np.clip(np.sin(2 * np.pi * rng.uniform(26, 34) * t), -1, 1)
    src = src * rat + lp(ruido(n, rng), 1800, 1) * .7 * rat
    if tipo == "rugido":
        form = bp(src, 260, 520) * 1.0 + bp(src, 650, 1100) * .8 + bp(src, 1700, 2600) * .3
    else:
        form = bp(src, 180, 380) * 1.0 + bp(src, 520, 900) * .5
    x = np.tanh(1.8 * form / (np.abs(form).max() + 1e-9)) * env
    x += lp(ruido(n, rng), 300) * np.exp(-t * 7) * .25                                           # golpe de aire grave
    x = lp(x, 2800, 2)
    return _p(x) * .75


def f_aleteo(rng, dur):
    """insecto: zumbido 190-320 Hz con vibrato, AM de alas, acercamiento y alejamiento."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = rng.uniform(180, 320) * (1 + .12 * np.sin(2 * np.pi * rng.uniform(.8, 2) * t) + .05 * lp(ruido(n, rng), 15, 1) * 4)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = sum(np.sin(k * ph) / k ** 1.1 for k in range(1, 12)) * (.6 + .4 * np.sin(2 * np.pi * f * .5 * t))
    x += bp(ruido(n, rng), 2500, 7000) * .15
    env = np.sin(np.pi * t / dur) ** 1.5
    return _p(x * env) * .09


def f_respira(rng, dur, grave=1.0):
    n = int(dur * SR)
    x = np.zeros(n)
    tt = rng.uniform(0, .6)
    while tt < dur - 1.0:
        m = int(rng.uniform(.7, 1.1) * SR)
        j = int(tt * SR)
        k = np.arange(m)
        s = bp(ruido(m, rng), 220 / grave, 1400 / grave) * np.sin(np.pi * k / m) ** 2
        x[j:j + m] += s[:n - j]
        tt += rng.uniform(1.9, 2.8)
    return _p(x) * .12 if np.abs(x).max() > 0 else x


def f_vegetacion(rng, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    flame = np.clip(lp(ruido(n, rng), 18, 1) * 7 + .7, 0, 1.5)
    x = bp(ruido(n, rng), 1800, 7000) * flame * np.minimum(1, t / .05) * np.minimum(1, (dur - t) / .1)
    for _ in range(int(dur * 8)):
        m = int(.012 * SR)
        j = rng.integers(0, max(1, n - m))
        x[j:j + m] += bp(ruido(m, rng), 1200, 5000) * np.exp(-np.arange(m) / SR * 500) * 1.8
    return _p(x) * .28


def f_sacudir(rng):
    n = int(.55 * SR)
    t = np.arange(n) / SR
    x = bp(ruido(n, rng), 700, 4500) * (.5 + .5 * np.sin(2 * np.pi * 15 * t)) * np.exp(-t * 4)
    return _p(x) * .2


def f_tierra(rng, vol=1.0):
    n = int(1.1 * SR)
    t = np.arange(n) / SR
    x = lp(ruido(n, rng), 1100) * np.exp(-t * 4.5) * np.clip(lp(ruido(n, rng), 22, 1) * 6, 0, 1)
    x += bp(ruido(n, rng), 1500, 5000) * np.exp(-t * 14) * .3
    return _p(x) * .3 * vol


def f_clic(rng):
    n = int(.1 * SR)
    t = np.arange(n) / SR
    a = bp(ruido(n, rng), 1800, 7800) * np.exp(-t * 95)
    b = lp(ruido(n, rng), 420) * np.exp(-t * 60) * .6
    k = int(.036 * SR)
    c = np.zeros(n)
    c[k:] = bp(ruido(n - k, rng), 900, 4300) * np.exp(-t[:n - k] * 75) * .7
    d = np.sin(2 * np.pi * 2300 * t) * np.exp(-t * 400) * .2             # tintineo del muelle
    return _p(a + b + c + d) * .5


def f_paso_chico(rng, mat="tierra"):                # mascota: patitas rapidas con uñas
    n = int(.12 * SR)
    t = np.arange(n) / SR
    x = lp(ruido(n, rng), 600) * np.exp(-t * 55) * .6 + hp(ruido(n, rng), 3200, 1) * np.exp(-t * 200) * .5
    x += np.sin(2 * np.pi * 110 * t) * np.exp(-t * 60) * .3
    return _p(x) * .28


def f_ladrido(rng, f0=330.0, dur=.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * (1.15 - .45 * t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    src = sum(np.sin(k * ph) / k ** .9 for k in range(1, 16)) + .4 * lp(ruido(n, rng), 3000, 1)
    x = bp(src, 500, 900) + .8 * bp(src, 1100, 1900) + .3 * bp(src, 2600, 3600)
    env = np.minimum(1, t / .008) * np.exp(-t * 11) * np.minimum(1, (dur - t) / .03)
    return _p(np.tanh(1.5 * x / (np.abs(x).max() + 1e-9)) * env) * .55


def f_jadeo(rng, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = bp(ruido(n, rng), 1200, 5000) * np.clip(np.sin(2 * np.pi * 3.3 * t), 0, 1) ** 1.5
    return _p(x) * .09 if n > 10 else x


def f_lapiz(rng, dur):
    """trazos de lapiz: ruido 1.8-7.5k con modulacion de velocidad del trazo, ataques cada cambio de direccion."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    vel = np.abs(np.sin(2 * np.pi * rng.uniform(3, 6) * t + .3)) ** .7 * (.5 + .5 * suave(n, rng, 2.5))
    x = bp(ruido(n, rng), 1800, 7500) * vel + bp(ruido(n, rng), 300, 1200) * vel * .25
    x *= np.minimum(1, t / .04) * np.minimum(1, (dur - t) / .06)
    for _ in range(int(dur * 1.5)):                       # ligeros golpes de punta
        m = int(.008 * SR)
        j = rng.integers(0, max(1, n - m))
        x[j:j + m] += bp(ruido(m, rng), 900, 4000) * np.exp(-np.arange(m) / SR * 600) * 1.5
    return _p(x) * .14


def f_papel(rng):
    n = int(.8 * SR)
    t = np.arange(n) / SR
    env = np.exp(-t * 3.5) * (.45 + .55 * np.abs(np.sin(t * 35 + rng.uniform(0, 3))))
    x = bp(ruido(n, rng), 900, 6800) * env * np.minimum(1, t / .02) + bp(ruido(n, rng), 200, 700) * np.exp(-t * 9) * .3
    return _p(x) * .26


def f_marco(rng):
    """marco rojo que entra: barrido de ruido ascendente + golpe suave al asentarse."""
    n = int(.7 * SR)
    t = np.arange(n) / SR
    x = ruido(n, rng)
    out = np.zeros(n)
    for i, (a, b) in enumerate(((300, 900), (800, 2200), (2000, 5200))):
        seg = slice(int(i * .06 * SR), None)
        out[seg] += bp(x, a, b)[seg] * (np.sin(np.pi * np.clip((t[seg] - i * .06) / (.6 - i * .06), 0, 1)) ** 2)
    out += np.sin(2 * np.pi * 70 * t) * np.exp(-np.maximum(0, t - .45) * 30) * (t > .45) * .8
    return _p(out) * .3


def f_trueno_unico(rng):
    m = int(3.5 * SR)
    k = np.arange(m) / SR
    return _p(lp(ruido(m, rng), 150) * np.exp(-k * 1.0) * np.minimum(1, k / .03)) * .7


def f_impacto(rng):
    n = int(.9 * SR)
    t = np.arange(n) / SR
    return _p(np.sin(2 * np.pi * 52 * (1 - .4 * t) * t) * np.exp(-t * 6) + lp(ruido(n, rng), 600) * np.exp(-t * 14) * .5) * .65


def f_latido(rng):
    n = int(.6 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 52 * t) * np.exp(-t * 14)
    j = int(.22 * SR)
    x[j:] += np.sin(2 * np.pi * 46 * t[:n - j]) * np.exp(-t[:n - j] * 16) * .7
    return _p(x) * .4


class Pista:
    """Acumulador estereo con panoramica, retardo interaural, distancia (paso bajo + envio a reverb)."""

    def __init__(self, n):
        self.dry = np.zeros((n, 2), F32)
        self.send = np.zeros((n, 2), F32)
        self.n = n
        self._cache = {}

    def add(self, x, t, pan=0.0, gain=1.0, dist=0.2, send=1.0):
        i = int(t * SR)
        if i < 0 or i >= self.n or len(x) == 0:
            return
        if dist > .3:
            key = (id(x), round(dist, 1))
            if key not in self._cache:
                self._cache[key] = lp(x, 9000 * (1 - dist) ** 1.5 + 900, 1)
            x = self._cache[key]
        m = min(len(x), self.n - i)
        l, r = pan_gains(pan)
        g = gain * (1 - .55 * dist)
        itd = int(abs(pan) * .0005 * SR)
        xl, xr = x[:m] * l * g, x[:m] * r * g
        dl, dr = (itd, 0) if pan > 0 else (0, itd)
        for ch, xx, d in ((0, xl, dl), (1, xr, dr)):
            e = min(m, self.n - i - d)
            if e > 0:
                self.dry[i + d:i + d + e, ch] += xx[:e]
        s = (.12 + .55 * dist) * send * g
        e = m
        self.send[i:i + e, 0] += x[:e] * l * s
        self.send[i:i + e, 1] += x[:e] * r * s


ESPECIES = [  # (subcadena, familia, pesado, f0 voz, dist por defecto)
    ("gorgon", "gran", .95, 62.0, .25), ("vetus", "prota", .38, 150.0, .1), ("dicinod", "chico", .3, 190.0, .25),
    ("diictodon", "chico", .25, 210.0, .25), ("cinod", "chico", .3, 190.0, .2), ("cynos", "chico", .3, 190.0, .2),
    ("anfib", "anfibio", .25, 200.0, .3), ("insect", "insecto", .02, 0, .3), ("libel", "insecto", .02, 0, .3),
    ("meganeur", "insecto", .02, 0, .3), ("escorpi", "insecto", .05, 0, .2), ("escarab", "insecto", .05, 0, .2),
    ("larva", "insecto", .02, 0, .2), ("cucarach", "insecto", .05, 0, .2), ("lystro", "chico", .4, 170.0, .25), ("bicho", "insecto", .03, 0, .25), ("milpi", "insecto", .03, 0, .25),
]
ACCIONES = [  # (subcadenas, tipo)
    (("olfat", "huel", "husme"), "olfato"), (("escarb", "cav", "desenterr", "excav", "rasc"), "escarbar"),
    (("com", "mastic", "roer", "mord", "devor", "alimen"), "comer"), (("rug", "ruge"), "rugido"),
    (("gru", "amenaz", "gem", "bram"), "gruñido"), (("alete", "vola", "vuel", "zumb", "aterr", "revolot"), "aleteo"),
    (("correr", "corre", "huir", "huye", "persec", "carrera", "escap", "galop", "trot"), "correr"),
    (("camin", "avanz", "pase", "andar", "anda", "mueve", "marcha", "cruza", "sigue"), "caminar"),
    (("sacud",), "sacudir"), (("pele", "lucha", "forceje", "pugna", "ria"), "pelea"), (("salt", "brinc"), "salto"), (("esconde", "madriguera", "entra", "oculta", "emerg", "sale"), "esconder"),
    (("quiet", "inmov", "vigil", "acech", "observ", "espera", "oreja", "descans", "dorm", "respir", "mira", "alert", "echad", "sentad", "idle", "repos"), "quieto"),
]


def clasifica(especie):
    e = norm(especie)
    for sub, fam, pes, f0, dist in ESPECIES:
        if sub in e:
            return fam, pes, f0, dist
    return "medio", .5, 120.0, .25


def tipo_accion(a):
    a = norm(a)
    for subs, tipo in ACCIONES:
        if any(a.startswith(s) or (" " + s) in a or s in a for s in subs):
            return tipo
    return "quieto"


def _lista(v, dur):
    """mascota/owen pueden ser bool, dict o lista de dicts."""
    if not v:
        return []
    if v is True:
        return [dict(t0=0, t1=dur)]
    if isinstance(v, dict):
        return [v]
    if isinstance(v, list):
        return [x if isinstance(x, dict) else dict(accion=str(x), t0=0, t1=dur) for x in v]
    return [dict(t0=0, t1=dur)]


def efectos_escena(esc, t0e, pista, rng):
    """Dispara los efectos de la escena (que empieza en t0e s del tiempo de la parte)."""
    dur = float(esc["dur"])
    suelo = norm(esc.get("suelo")) + " " + norm((esc.get("clima") or {}).get("particulas") if isinstance((esc.get("clima") or {}).get("particulas"), str) else "")
    sid = esc.get("id", "")

    def sal(t, x, pan=0, g=1, d=.2, send=1):
        pista.add(x, t0e + t, pan, g, d, send)

    for ia, an in enumerate(esc.get("animales") or []):
        fam, pes, f0, dist = clasifica(an.get("especie"))
        tipo = tipo_accion(an.get("accion"))
        a, b = float(an.get("t0", 0)), float(an.get("t1", dur))
        b = min(b, dur)
        if b <= a:
            continue
        r = np.random.default_rng(seed_de(sid, ia, an.get("especie"), an.get("accion")))
        p0 = an.get("pan", None)
        xa = an.get("x0", an.get("x"))
        if p0 is None and xa is not None and 0 <= xa <= 1:
            p0 = xa * 2 - 1
        if p0 is None:
            p0 = r.uniform(-.65, .65)
        p1 = an.get("pan1", None)
        if p1 is None and an.get("x1") is not None and 0 <= an["x1"] <= 1:
            p1 = an["x1"] * 2 - 1
        if p1 is None:
            p1 = p0 + (r.uniform(-.4, .4) if an.get("x1") is None else 0)
        d = float(an.get("dist", dist))
        vol = float(an.get("vol", 1.0))
        pn = lambda t: np.clip(p0 + (p1 - p0) * (t - a) / max(b - a, .1), -.95, .95)

        if fam == "insecto":
            if tipo == "aleteo" or tipo == "correr" or any(w in norm(an.get("especie")) for w in ("libel", "meganeur")):
                sal(a, f_aleteo(r, b - a), pn(a), .8 * vol, d)
            elif tipo == "esconder":
                sal(a, f_tierra(r, .8), pn(a), vol, d)
                sal(a + .5, f_clic(r), pn(a), .35 * vol, d)
            else:
                t = a
                while t < b:
                    for _ in range(r.integers(2, 4)):
                        m = int(.015 * SR)
                        s = bp(ruido(m, r), 2500, 9000) * np.exp(-np.arange(m) / SR * 450) * .05
                        sal(t, s, pn(t), vol, d)
                        t += r.uniform(.03, .06)
                    t += r.uniform(.12, .35)
            continue
        if tipo in ("caminar", "correr"):
            ev = {"caminar": .46, "correr": .21}[tipo] * (1 + .5 * pes if fam == "gran" else 1) * (.8 if fam in ("chico", "anfibio") and tipo == "caminar" else 1)
            t = a + r.uniform(0, ev)
            lado = 0
            while t < b:
                tm = "agua" if fam == "anfibio" else suelo
                x = f_paso(r, min(1, pes * (1.2 if tipo == "correr" else 1)), tm)
                sal(t, x, pn(t) + (.04 if lado else -.04), vol * r.uniform(.65, 1.15), d)
                lado ^= 1
                t += ev * r.uniform(.88, 1.14) * (1 if lado else 1.05)
            if tipo == "correr":
                sal(a, f_vegetacion(r, b - a), pn(a), .7 * vol, d)
            elif r.random() < .6:
                sal(a, f_vegetacion(r, b - a), pn(a), .12 * vol, d)
        elif tipo == "olfato":
            t = a
            while t < b - .25:
                dd = min(b - t, r.uniform(.6, 1.1))
                sal(t, f_olfateo(r, dd), pn(t), vol, d)
                t += dd + r.uniform(.4, 1.0)
        elif tipo == "escarbar":
            sal(a, f_escarbar(r, b - a), pn(a), vol, d)
            sal(b - .3, f_tierra(r, .5), pn(b), .6 * vol, d)
        elif tipo == "comer":
            sal(a, f_comer(r, b - a), pn(a), vol, d)
        elif tipo in ("rugido", "gruñido"):
            tp = "rugido" if tipo == "rugido" else "gruñido"
            x = f_rugido(r, dur=min(b - a, 2.4 if tp == "rugido" else 1.6) if fam == "gran" else min(b - a, 1.0), f0=f0 * (1.0 if fam == "gran" else 1.0), tipo=tp)
            sal(a, x, pn(a), vol * (1.0 if fam == "gran" else .45), d, send=1.6)
        elif tipo == "aleteo":
            sal(a, f_aleteo(r, b - a), pn(a), .6 * vol, d)
        elif tipo == "sacudir":
            sal(a, f_sacudir(r), pn(a), vol, d)
        elif tipo == "pelea":
            t = a
            while t < b - .3:
                q = r.random()
                if q < .45:
                    sal(t, f_rugido(r, r.uniform(.5, .9), f0 * 1.5, "gruñido"), pn(t), .55 * vol, d)
                elif q < .75:
                    sal(t, f_sacudir(r), pn(t), vol, d)
                else:
                    sal(t, f_paso(r, pes + .25, suelo), pn(t), 1.2 * vol, d)
                    sal(t + .05, f_vegetacion(r, .5), pn(t), .5 * vol, d)
                t += r.uniform(.35, .8)
        elif tipo == "salto":
            sal(a, f_paso(r, pes + .2, suelo), pn(a), 1.1 * vol, d)
            sal(a + .22, f_paso(r, pes, suelo), pn(a), .9 * vol, d)
        elif tipo == "esconder":
            sal(a, f_vegetacion(r, min(1.2, b - a)), pn(a), .6 * vol, d)
            sal(a + .3, f_tierra(r, .7), pn(a), vol, d)
        else:  # quieto
            sal(a, f_respira(r, b - a, 1.6 if fam == "gran" else 1.0), pn(a), vol * (1.3 if fam == "gran" else 1.0), d)
        if fam == "gran" and tipo in ("caminar", "quieto") and r.random() < .5:       # gruñido bajo ocasional
            tg = a + r.uniform(0, max(.1, b - a - 1.2))
            sal(tg, f_rugido(r, 1.3, f0 * 1.05, "gruñido"), pn(tg), .38 * vol, d, send=1.6)

    # mascota
    for k, m in enumerate(_lista(esc.get("mascota"), dur)):
        a, b = float(m.get("t0", 0)), min(float(m.get("t1", dur)), dur)
        tipo = tipo_accion(m.get("accion", "caminar")) if m.get("accion") else "caminar"
        r = np.random.default_rng(seed_de(sid, "mascota", k))
        p0 = float(m.get("pan", (m["x"] * 2 - 1) if isinstance(m.get("x"), (int, float)) and 0 <= m["x"] <= 1 else r.uniform(-.5, .5)))
        if tipo in ("caminar", "correr") and b > a:
            ev = .17 if tipo == "correr" else .27
            t = a
            while t < b:
                sal(t, f_paso_chico(r), np.clip(p0 + .15 * np.sin(t), -.9, .9), r.uniform(.6, 1.1), .12)
                t += ev * r.uniform(.8, 1.2) * (.4 if r.random() < .22 else 1)       # a veces doble pisada
        elif tipo == "olfato" and b > a:
            t = a
            while t < b - .3:
                dd = min(b - t, r.uniform(.5, .9))
                sal(t, f_olfateo(r, dd), p0 + .1 * np.sin(t), .8, .12)
                t += dd + r.uniform(.8, 2.0)
        elif b > a + 1:
            sal(a, f_jadeo(r, b - a), p0, 1, .1)
        ladra = m.get("ladra", m.get("ladridos", []))
        if ladra is True:
            ladra = [a + (b - a) / 2]
        for tl in ladra or []:
            for q in range(2 if r.random() < .5 else 1):
                sal(float(tl) + q * .27, f_ladrido(r, 300 + r.uniform(-30, 40)), p0, 1.0, .12, send=1.3)
        if tipo == "ladrar" or "ladr" in norm(m.get("accion")):
            for q in range(3):
                sal(a + q * .3, f_ladrido(r, 300 + r.uniform(-20, 40)), p0, 1.0, .12, send=1.3)

    # Owen: libreta (lapiz continuo solo si la escena es de la libreta/cuaderno)
    libreta = any(w in norm(esc.get("titulo")) for w in ("libreta", "cuaderno", "apunt")) or bool(esc.get("cuaderno"))
    for k, m in enumerate(_lista(esc.get("owen"), dur)):
        a, b = float(m.get("t0", 0)), min(float(m.get("t1", dur)), dur)
        ac = norm(m.get("accion", "escribir"))
        r = np.random.default_rng(seed_de(sid, "owen", k))
        if "pagin" in ac or "hoja" in ac or "papel" in ac or "pasa" in ac:
            sal(a, f_papel(r), .1, 1.0, .1)
        elif "camin" in ac or "avanz" in ac:
            t = a
            while t < b:
                sal(t, f_paso(r, .6, suelo), -.1, .8, .1)
                t += .52 * r.uniform(.9, 1.1)
        elif not m.get("accion") and not libreta:       # Owen hablando: solo un roce de papel al entrar
            sal(a, f_papel(r), .1, .35, .1)
        elif b > a:
            t = a
            while t < b - .2:
                dd = min(b - t, r.uniform(.5, 1.6))
                sal(t, f_lapiz(r, dd), .1 + .05 * r.uniform(-1, 1), 1.0, .1, send=.5)
                t += dd + r.uniform(.15, .5)
            if b - a > 3:
                sal(b - .1, f_papel(r), .1, .5, .1)
        if m.get("tap") or m.get("golpecitos"):
            for q in range(3):
                m2 = int(.01 * SR)
                sal(a + q * .15, bp(ruido(m2, r), 900, 3500) * np.exp(-np.arange(m2) / SR * 400) * .2, .1, 1, .1)

    ca = esc.get("cartel")
    for k, c in enumerate(ca if isinstance(ca, list) else [ca] if isinstance(ca, dict) else []):
        r = np.random.default_rng(seed_de(sid, "cartel", k))
        sal(float(c.get("t0", 0)) - .1, f_marco(r), .3, .8, .05, send=.8)
    # clic de camara (apertura/montaje) y efectos genericos
    clics = esc.get("clics") or esc.get("cortes")
    tt = norm(esc.get("titulo")) + " " + norm(sid)
    if esc.get("clic") is True:
        clics = [0.0]
    if clics is None and any(w in tt for w in ("apertura", "montaje", "carteles", "calle", "rafaga")):
        clics, t = [], 0.0
        r = np.random.default_rng(seed_de(sid, "clic"))
        while t < min(dur, 8):
            clics.append(t)
            t += r.uniform(.45, .9)
    for k, c in enumerate(clics or []):
        r = np.random.default_rng(seed_de(sid, "c", k))
        sal(float(c), f_clic(r), r.uniform(-.1, .1), r.uniform(.8, 1.1), .05, send=.6)
    GEN = dict(clic=f_clic, tierra=f_tierra, impacto=f_impacto, trueno=f_trueno_unico, latido=f_latido, papel=f_papel,
               paso=lambda r: f_paso(r, .6, suelo), ladrido=lambda r: f_ladrido(r))
    for k, e in enumerate(esc.get("sfx") or esc.get("efectos") or []):
        nm = norm(e.get("tipo", ""))
        fn = next((v for kk, v in GEN.items() if kk in nm), None)
        if fn:
            r = np.random.default_rng(seed_de(sid, "sfx", k))
            sal(float(e.get("t", 0)), fn(r), float(e.get("pan", 0)), float(e.get("vol", 1)), float(e.get("dist", .2)))


# ----------------------------------------------------------------------------- MUSICA
_TONE_CACHE = {}


def guitarra_tone(note, dur, vel):
    f = TG.hz(note)
    n = int((dur + .8) * SR)
    t = np.arange(n) / SR
    out = sum(np.sin(2 * np.pi * f * k * np.sqrt(1 + .0002 * k * k) * t + k) * np.exp(-t * (3.0 + 1.6 * k)) / k ** 1.1 for k in range(1, 9))
    out += bp(np.random.default_rng(int(note)).standard_normal(n), 1500, 4500) * np.exp(-t * 90) * .1
    env = np.minimum(1, t / .003) * np.where(t > dur, np.exp(-(t - dur) * 9), 1)
    return out * env * (vel / 127.0) ** 1.6 * .5


def tono(inst, note, dur, vel):
    k = (inst, int(note), round(dur, 3), int(vel) // 4)
    if k not in _TONE_CACHE:
        if inst == "guitarra":
            _TONE_CACHE[k] = guitarra_tone(note, dur, vel).astype(F32)
        else:
            _TONE_CACHE[k] = TG.tone(inst, note, dur, vel, np.random.default_rng(5)).astype(F32)
    return _TONE_CACHE[k]


def stems_tango(total):
    """Stems mono (n,) por instrumento para al menos `total` s; en cache en disco."""
    vueltas = max(1, int(np.ceil((total + 6) / 116.0)))
    cache = AQUI / "audio" / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    f = cache / f"tango_v{vueltas}.npz"
    if f.exists():
        z = np.load(f)
        return {k: z[k] for k in z.files}
    ev, tot, _ = TG.score(vueltas)
    n = int(tot * SR)
    rng = np.random.default_rng(3)
    st = {}
    for inst, notes in ev.items():
        buf = np.zeros(n + 3 * SR, F32)
        for note, t0, dur, vel in notes:
            x = tono(inst, note, dur, vel * rng.uniform(.94, 1.04))
            i = max(0, int((t0 + rng.normal(0, .006)) * SR))
            e = min(len(x), len(buf) - i)
            buf[i:i + e] += x[:e]
        st[inst] = buf[:n]
    np.savez(f, **st)
    return st


def pad_drone(n, rng, disonante):
    """Pad de lengüetas lentas. Se genera a SR/4 (armonicos < 1.3 kHz) y se sobremuestrea: 4x mas rapido."""
    sr4 = SR // 4
    m = n // 4 + 8
    t = (np.arange(m) / sr4).astype(np.float32)
    notas = [49.0, 98.0, 146.83, 233.08] if not disonante else [49.0, 51.9, 73.4, 138.6]    # Gm / racimo G Ab D Db
    out = np.zeros((m, 2), np.float32)
    for i, f in enumerate(notas):
        mod = [(.55 + .45 * np.sin(2 * np.pi * (.05 + .02 * i) * t + i + c)) * (.5 if i else 1) for c in range(2)]
        for c in range(2):
            for det in (-.0035, .0035):
                ff = f * (1 + det + .0007 * c)
                x = sum(np.sin(2 * np.pi * ff * k * t + c + i) / k ** 1.5 for k in range(1, 6) if ff * k < sr4 * .45)
                out[:, c] += x * mod[c]
    out = resample_poly(out, 4, 1, axis=0)[:n]
    return (out / 8).astype(np.float32)


def curva(escs, starts, total, clave, cr=50, xf=2.5):
    """Curva de control (cr Hz) con valor por escena, suavizada, interpolada a SR."""
    v = np.zeros(int(total * cr) + cr)
    for e, s in zip(escs, starts):
        v[int(s * cr):int((s + e["dur"]) * cr)] = clave(e)
    last = escs[-1]
    v[int((starts[-1] + last["dur"]) * cr):] = clave(last)
    v = uniform_filter1d(v, int(xf * cr)) if xf > 0 else v
    return v


def musica(escs, starts, total, rng):
    st = stems_tango(total)
    n = int(total * SR)

    def fit(x):
        if len(x) >= n:
            return x[:n]
        reps = int(np.ceil(n / len(x)))
        return np.tile(x, reps)[:n]

    cr = 50
    gt = np.arange(n) / SR * cr

    def env(c):
        return np.interp(gt, np.arange(len(c)), c).astype(F32)

    ms = [modo_de(e) for e in escs]
    L = np.zeros(n, F32)
    R = np.zeros(n, F32)
    pan = {"bandoneon": -.30, "acordeon": .30, "piano": .12, "contrabajo": -.04, "guitarra": .45}
    for inst in ("bandoneon", "acordeon", "piano", "contrabajo", "guitarra"):
        g = env(curva(escs, starts, total, lambda e, inst=inst: MODOS[modo_de(e)][inst], cr))
        x = fit(st[inst]) * g
        l, r = pan_gains(pan[inst])
        L += x * l * 1.41
        R += x * r * 1.41
    # pad (calido en sol menor / racimo disonante) y latido
    pg = env(curva(escs, starts, total, lambda e: MODOS[modo_de(e)]["pad"], cr, 3.5))
    tg = env(curva(escs, starts, total, lambda e: MODOS[modo_de(e)]["ten"], cr, 3.5))
    P1, P2 = pad_drone(n, rng, False), pad_drone(n, rng, True)
    pad = (P1 * (1 - tg)[:, None] + P2 * tg[:, None]) * pg[:, None] * .5
    L += pad[:, 0].astype(F32)
    R += pad[:, 1].astype(F32)
    lg = curva(escs, starts, total, lambda e: MODOS[modo_de(e)]["latido"], cr, 3.0)
    lat = np.zeros(n, F32)
    lb = f_latido(rng).astype(F32)
    per = 60 / 52.0
    for k in range(int(total / per)):
        i = int(k * per * SR)
        g = lg[min(len(lg) - 1, int(k * per * cr))]
        if g > .02:
            e = min(len(lb), n - i)
            lat[i:i + e] += lb[:e] * g * 1.2
    L += lat
    R += lat
    M = np.stack([L, R], 1)
    # oscurecimiento: mezcla con version filtrada (paso bajo 1.6 kHz)
    dk = env(curva(escs, starts, total, lambda e: MODOS[modo_de(e)]["dark"], cr, 3.0))[:, None]
    Md = sosfilt(butter(2, 1600, "low", fs=SR, output="sos"), M, axis=0).astype(F32)
    M = M * (1 - dk) + Md * dk
    M += reverb(M, "sala", .22)
    db = env(curva(escs, starts, total, lambda e: MODOS[modo_de(e)]["db"], cr, 2.5))[:, None]
    return M * (10 ** (db / 20)).astype(F32)


# ----------------------------------------------------------------------------- MEZCLA
def lufs(x):
    """Sonoridad integrada ITU-R BS.1770-4 (K-weighting + compuerta) de un array (n,2) a SR."""
    def kw(x):
        f0, Q, G = 1681.974450955533, .7071752369554196, 3.999843853973347
        K = np.tan(np.pi * f0 / SR); Vh = 10 ** (G / 20); Vb = Vh ** .4996667741545416
        a0 = 1 + K / Q + K * K
        b = [(Vh + Vb * K / Q + K * K) / a0, 2 * (K * K - Vh) / a0, (Vh - Vb * K / Q + K * K) / a0]
        a = [1, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0]
        y = lfilter(b, a, x, axis=0)
        f0, Q = 38.13547087602444, .5003270373238773
        K = np.tan(np.pi * f0 / SR); a0 = 1 + K / Q + K * K
        return lfilter([1, -2, 1], [1, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0], y, axis=0)
    y = kw(x.astype(np.float64)) ** 2
    blk, hop = int(.4 * SR), int(.1 * SR)
    cs = np.cumsum(np.vstack([np.zeros((1, 2)), y]), axis=0)
    idx = np.arange(0, len(y) - blk, hop)
    if len(idx) == 0:
        return -70.0
    z = (cs[idx + blk] - cs[idx]) / blk
    l = -.691 + 10 * np.log10(z.sum(1) + 1e-12)
    g1 = l > -70
    if not g1.any():
        return -70.0
    rel = -.691 + 10 * np.log10(z[g1].sum(1).mean() + 1e-12) - 10
    g2 = l > max(-70, rel)
    return float(-.691 + 10 * np.log10(z[g2].sum(1).mean() + 1e-12))


def limitador(x, techo_db=-1.5, look=.006):
    techo = 10 ** (techo_db / 20)
    pk = np.abs(x).max(1)
    need = np.minimum(1, techo / np.maximum(pk, 1e-9))
    w = int(look * SR) | 1
    g = minimum_filter1d(need, w * 2 + 1)
    g = uniform_filter1d(g, w * 2 + 1)      # minimo + media: ataque anticipado, liberacion de ~12 ms
    out = x * g[:, None]
    return np.clip(out, -techo * 1.0005, techo * 1.0005)


def guardar(path, x):
    path.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(1)
    d = (rng.random(x.shape) - rng.random(x.shape)) / 32768
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x + d, -1, 1) * 32767).round().astype("<i2").tobytes())


def leer_voz(path, n):
    with wave.open(str(path)) as w:
        sr, ch = w.getframerate(), w.getnchannels()
        x = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float32) / 32768
    x = x.reshape(-1, ch).mean(1)
    if sr != SR:
        x = resample_poly(x, SR, sr)
    return np.pad(x, (0, max(0, n - len(x))))[:n]


def ducking(voz, duck_db, ataque=.08, rel=.6):
    e = np.sqrt(uniform_filter1d(voz ** 2, int(.05 * SR)))
    a = (e > 10 ** (-42 / 20)).astype(float)
    a = uniform_filter1d(np.maximum.accumulate(a[::-1])[::-1] * 0 + a, int(ataque * SR))
    s = lfilter([1 - np.exp(-1 / (rel * SR))], [1, -np.exp(-1 / (rel * SR))], a)
    s = np.maximum(a, s)
    return 10 ** (-duck_db * np.clip(s, 0, 1) / 20)


# ----------------------------------------------------------------------------- RENDER
def render(escs, parametros, nombre=""):
    t0 = time.time()
    P = parametros
    starts = np.cumsum([0] + [float(e["dur"]) for e in escs])[:-1]
    total = float(sum(e["dur"] for e in escs))
    n = int(total * SR)
    xf = 1.5
    # capa 2: ambiente por escena con fundido cruzado
    amb = np.zeros((n, 2), F32)
    send_amb = np.zeros((n, 2), F32)
    for k, (e, s) in enumerate(zip(escs, starts)):
        rng = np.random.default_rng(seed_de(e.get("id", k), "amb"))
        seg = ambiente(e, float(e["dur"]), xf, rng)
        m = len(seg)
        w = np.ones(m, F32)
        fi, fo = int(xf * 2 * SR), int(xf * 2 * SR)
        w[:fi] = np.sin(np.linspace(0, np.pi / 2, fi)) ** 2
        w[-fo:] = np.cos(np.linspace(0, np.pi / 2, fo)) ** 2
        i0 = int((s - xf) * SR)
        a0, b0 = max(0, i0), min(n, i0 + m)
        seg = seg[a0 - i0:b0 - i0] * w[a0 - i0:b0 - i0, None]
        amb[a0:b0] += seg
        send_amb[a0:b0] += seg * perfil(e)["rev"]
    amb += reverb(send_amb, "valle", .9)
    print(f"  ambiente {time.time() - t0:.1f}s", file=sys.stderr)
    # capa 3: efectos
    pista = Pista(n)
    for e, s in zip(escs, starts):
        efectos_escena(e, float(s), pista, None)
    fx = pista.dry + reverb(pista.send, "valle", .6)
    print(f"  efectos {time.time() - t0:.1f}s", file=sys.stderr)
    # capa 1: musica
    mus = musica(escs, starts, total, np.random.default_rng(9))
    print(f"  musica {time.time() - t0:.1f}s", file=sys.stderr)
    # niveles: cada capa se calibra a su sonoridad objetivo (dB rel.) antes de sumar
    mus = mus * 10 ** ((P["musica_db"] - rms_db(mus)) / 20)
    amb = amb * 10 ** ((P["amb_db"] - rms_db(amb)) / 20)
    fx = fx * P["fx_gain"]
    # recorte de graves (cama limpia para voz): la sala/ambiente no deben dominar < 120 Hz
    mus = sosfilt(np.vstack([butter(2, 58, "high", fs=SR, output="sos"), lowshelf(170, -5)]), mus, axis=0).astype(F32)
    amb = sosfilt(lowshelf(220, -4), amb, axis=0).astype(F32)
    # bolsillo de voz: EQ fijo en musica y ambiente (cede 250-4000 Hz); duck_db controla la profundidad
    if P["duck_db"] > 0:
        d = P["duck_db"]
        pocket = np.vstack([peaking(500, -d * .6, .7), peaking(1400, -d, .8), peaking(3000, -d * .7, .8)])
        mus = sosfilt(pocket, mus, axis=0).astype(F32)
        amb = sosfilt(pocket, amb, axis=0).astype(F32)
    bed = mus + amb
    voz = None
    if P.get("voz"):
        voz = leer_voz(P["voz"], n)
        bed = bed * ducking(voz, P["duck_dinamico_db"])[:, None]
    mix = bed + fx
    # fundidos de la parte
    fi, fo = int(1.5 * SR), int(4.0 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)[:, None]
    mix[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
    if voz is not None:
        mix = mix + np.stack([voz, voz], 1) * 10 ** (P["voz_db"] / 20)
    mix = hp(mix, 25, 1) if False else sosfilt(butter(2, 28, "high", fs=SR, output="sos"), mix, axis=0)
    # -16 LUFS aprox. y limitador
    cur = lufs(mix)
    mix = mix * 10 ** ((P["lufs"] - cur) / 20)
    for _ in range(2):
        mix = limitador(mix, P["techo_db"])
        c2 = lufs(mix)
        if abs(c2 - P["lufs"]) < .3:
            break
        mix = mix * 10 ** ((P["lufs"] - c2) / 20)
    mix = limitador(mix, P["techo_db"])
    print(f"  mezcla {time.time() - t0:.1f}s ({total:.1f}s de audio)", file=sys.stderr)
    return mix.astype(np.float32), dict(escs=len(escs), total=total, capas=dict(musica=mus, ambiente=amb, efectos=fx))


def informe(x, capas=None, starts=None, escs=None):
    L = lufs(x)
    pk = np.abs(x).max()
    print(f"nivel: {L:.2f} LUFS integrados · pico muestra {20 * np.log10(pk):.2f} dBFS · clipping (|x|>=0.999): {int((np.abs(x) >= .999).sum())} muestras")
    m = x.mean(1)
    n = len(m)
    w = np.hanning(8192)
    ps = np.mean([np.abs(np.fft.rfft(m[i:i + 8192] * w)) ** 2 for i in range(0, n - 8192, 4096)], axis=0)
    fr = np.fft.rfftfreq(8192, 1 / SR)
    tot = ps.sum()
    bands = [(20, 60), (60, 120), (120, 250), (250, 500), (500, 1000), (1000, 2000), (2000, 4000), (4000, 8000), (8000, 16000)]
    print("espectro (energia por banda):  " + "  ".join(f"{a}-{b}Hz {10 * np.log10(ps[(fr >= a) & (fr < b)].sum() / tot + 1e-12):.1f}dB" for a, b in bands))
    if capas:
        print("RMS por capa (antes de normalizar): " + "  ".join(f"{k} {rms_db(v):.1f} dBFS" for k, v in capas.items()))
    if starts is not None:
        for e, s in zip(escs, starts):
            seg = x[int(s * SR):int((s + e["dur"]) * SR)]
            print(f"  escena {str(e['id']):<22} {e['paleta']:<8} modo {modo_de(e):<9} RMS {rms_db(seg):6.1f} dBFS  pico {20 * np.log10(np.abs(seg).max() + 1e-9):6.1f} dBFS")


def parser():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--parte", type=int)
    ap.add_argument("--todo", action="store_true")
    ap.add_argument("--prueba", action="store_true", help="30 s con escenas_prueba -> render/audio/prueba.wav + informe")
    ap.add_argument("--escenas", help="ruta de escenas.json (def. guion/escenas.json)")
    ap.add_argument("--salida", help="directorio de salida (def. render/audio)")
    ap.add_argument("--lufs", type=float, default=-16.0, help="sonoridad objetivo (def. -16; con voz encima usa ~ -24 o pasa --voz)")
    ap.add_argument("--techo_db", type=float, default=-1.5)
    ap.add_argument("--duck_db", type=float, default=5.0, help="profundidad del bolsillo EQ fijo para la voz (dB, 0 = off)")
    ap.add_argument("--musica_db", type=float, default=-24.0, help="RMS objetivo de la musica antes de mezclar")
    ap.add_argument("--amb_db", type=float, default=-27.0)
    ap.add_argument("--fx_gain", type=float, default=.55)
    ap.add_argument("--voz", help="wav de voz opcional: ducking dinamico y se suma a la mezcla")
    ap.add_argument("--duck_dinamico_db", type=float, default=7.0)
    ap.add_argument("--voz_db", type=float, default=0.0)
    return ap


def main():
    a = parser().parse_args()
    P = dict(lufs=a.lufs, techo_db=a.techo_db, duck_db=a.duck_db, musica_db=a.musica_db, amb_db=a.amb_db, fx_gain=a.fx_gain,
             voz=a.voz, duck_dinamico_db=a.duck_dinamico_db, voz_db=a.voz_db)
    out = Path(a.salida) if a.salida else AQUI / "audio"
    if a.prueba:
        escs = escenas_prueba()
        mix, info = render(escs, P)
        guardar(out / "prueba.wav", mix)
        informe(mix, info["capas"], np.cumsum([0] + [e["dur"] for e in escs])[:-1], escs)
        return
    partes = [1, 2, 3, 4] if a.todo else [a.parte]
    if partes == [None]:
        parser().error("usa --parte N, --todo o --prueba")
    for p in partes:
        t = time.time()
        escs = cargar_escenas(a.escenas, p)
        mix, info = render(escs, P)
        guardar(out / f"parte{p}.wav", mix)
        print(f"parte {p}: {info['total']:.1f} s, {info['escs']} escenas -> {out / f'parte{p}.wav'} ({time.time() - t:.0f} s)")
        informe(mix)


if __name__ == "__main__":
    main()
