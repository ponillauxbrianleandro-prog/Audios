#!/usr/bin/env python3
"""Audio v10: mezcla nueva SOLO para la apertura y el cierre, y empalme con el audio de la v9 (el tramo central no se recalcula).

  python3 sonido_v10.py        -> ../video/audio/vetusodon-v10.wav
nuevo = apertura + v9[12,0 s : fin de la escena 11] + cierre   (cruces de 0,25 s en los empalmes)
"""
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from scipy.ndimage import uniform_filter1d

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "musica"))
import sonido8 as S
import musica_real as MR
import episodio as E
import world

SR = S.SR
V = S.VIDEO
OLD = V / "audio" / "central.wav"            # escenas 1–11 mezcladas con la voz nueva (sonido8.py --central)
OLD_S0 = 0.0                   # el audio central ya empieza en la escena 1
OLD_END = None                  # fin del audio central (se mide)


def ding(vol=1.0):
    n = int(1.3 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1568 * t) + 0.4 * np.sin(2 * np.pi * 3136 * t) + 0.2 * np.sin(2 * np.pi * 2349 * t)) * np.exp(-t * 5.0) * 0.17 * vol


def pop(vol=1.0):
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    f = 260 + 1100 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 20) * 0.38 * vol


def swoosh(dur=0.7, vol=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return S.hp(S.noise(n), 900) * (np.sin(np.pi * t / dur) ** 2) * (0.10 + 0.25 * (t / dur)) * vol


def tap(vol=1.0):
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    return S.bp(S.noise(n), 200, 2200) * np.exp(-t * 45) * 0.5 * vol


def _normaliza(x, nombre):
    raw = V / "audio" / f"_{nombre}.wav"
    with wave.open(str(raw), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
    out = V / "audio" / f"_{nombre}_n.wav"
    if S.V16M:
        S.loudnorm2(raw, out)
    else:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", str(SR), str(out)], check=True)
    return S.rw(out, 2)


def parte(c, plan_clima, booms, sfx_fn, nombre):
    D = c["dur"]
    n = int((D + 0.6) * SR)
    voz = np.zeros((n, 2))
    fx = np.zeros((n, 2))
    for k, (t, d, tx) in enumerate(c["lineas"]):
        f = S.VOZ / "final" / f"{c['esc']:02d}_{k}.wav"
        S.put(voz, S.rw(f)[:, 0], t)
    wm = AQUI.parent / "musica" / "wav" / f"musica_{nombre}.wav"
    MR.armar(S.TANGO, [dict(clima=plan_clima, dur=round(D, 3), booms=booms)], wm)
    mus = np.zeros((n, 2))
    m = S.rw(wm)
    S.put(mus, m[:n], 0.0)
    sfx_fn(fx, c)
    env = uniform_filter1d(np.abs(voz[:, 0]), int(0.18 * SR), mode="nearest")
    env = uniform_filter1d(np.clip(env / 0.10, 0, 1), int(0.25 * SR), mode="nearest")
    if S.V16M:
        env = S.env_duck(voz[:, 0])
        mus_d = mus * (1 - S.DUCK_MUS * env)[:, None] * 0.95
        out = voz * S.GVOZ + mus_d + fx * 0.9
        S.guardar_estudio(nombre, voz[:, 0] * S.GVOZ, (mus_d + fx * 0.9).mean(1), dict(mus=mus_d.mean(1), fx=(fx * 0.9).mean(1)))
    else:
        out = voz + mus * (1 - 0.60 * env)[:, None] * 0.95 + fx * 0.9
    f = int(0.5 * SR)
    out[-f:] *= np.linspace(1, 0, f)[:, None]
    return _normaliza(out, nombre)


def sfx_intro(fx, c):
    sh = c["shots"][0][2]
    for i, tc in enumerate(sh["cortes"]):
        S.put(fx, S.clic(), tc, 0.55)                                   # clic de cámara en cada foto
        if i % 3 == 0 and i:
            S.put(fx, tap(), tc, 0.5)                                    # cambia el cartel de la calle
    tB = sh["tB"]
    S.put(fx, S.subida(1.2), tB - 1.2, 0.7)
    S.put(fx, S.impacto(), tB, 0.8)
    for ti in sh["items_t"]:
        S.put(fx, ding(), tB + ti, 0.8)
    S.put(fx, swoosh(0.9), c["dur"] - 0.9, 0.8)                         # revelado: el documental se va aclarando


def sfx_cierre(fx, c):
    sh = c["shots"][0][2]
    for i, th in enumerate(sh["hitos_t"]):
        S.put(fx, pop(), th, 0.9)
        if i in (0, 3):
            S.put(fx, ding(), th + 0.05, 0.6)
    S.put(fx, S.impacto(), sh["hitos_t"][-1], 0.5)


def cruce(a, b, n):
    n = min(n, len(a), len(b))
    t = np.linspace(0, np.pi / 2, n)[:, None]
    return np.vstack([a[:-n], a[-n:] * np.cos(t) + b[:n] * np.sin(t), b[n:]])


def main():
    world.load()
    TL, total = E.timeline()
    c0, c15 = TL[0], TL[-1]
    assert c0["esc"] == 0 and c15["esc"] == 15
    intro = parte(c0, "rafaga", [round(c0["shots"][0][2]["tB"], 2)], sfx_intro, "intro")
    cierre = parte(c15, "ternura", [], sfx_cierre, "cierre")
    viejo = S.rw(OLD, 2)
    c1 = next(c for c in TL if c["esc"] == 1)
    c11 = next(c for c in TL if c["esc"] == 11)
    Lc = c11["t0"] + c11["dur"] - c1["t0"]                              # duración exacta del tramo central en el video
    medio = viejo[:int(round(Lc * SR))].copy()                         # escenas 1–11 con la voz nueva
    D0, D15 = c0["dur"], c15["dur"]
    T_c = D0 + Lc                                                      # inicio del cierre
    out = np.zeros((int((T_c + D15 + 0.6) * SR), 2))
    out[:len(intro)] += intro
    fi = int(0.05 * SR)
    medio[:fi] *= np.linspace(0, 1, fi)[:, None]
    i0 = int(round(D0 * SR))
    out[i0:i0 + len(medio)] += medio                                   # alineado con el video: empieza donde empieza la escena 1
    fc = int(0.4 * SR)
    cierre[:fc] *= np.linspace(0, 1, fc)[:, None]
    j0 = int(round(T_c * SR))
    out[j0:j0 + len(cierre)] += cierre[:len(out) - j0]
    bufin = out
    dest = V / "audio" / "vetusodon-v10.wav"
    with wave.open(str(dest), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(bufin, -1, 1) * 32767).astype("<i2").tobytes())
    print("audio v10:", dest, f"{len(bufin) / SR:.1f} s · apertura {c0['dur']:.2f} s · cierre {c15['dur']:.2f} s · total película {total:.2f} s")


if __name__ == "__main__":
    main()
