#!/usr/bin/env python3
"""Tango único para «Vetusodon» — sol menor, 120 BPM (tonalidad y pulso tomados del tango de referencia del usuario).

Sin violín. Protagonistas: bandoneón y acordeón (fuelle con swell y lengüetas desafinadas), piano, contrabajo y guitarra.
Melodías originales (no copian el tema de referencia); de la grabación de referencia solo se recuperan sonidos:
los golpes secos del marcato (transitorios de percusión) se extraen y se mezclan en los tiempos fuertes.

  python3 tango_v8.py            -> stems/<instrumento>.wav (44,1 kHz, estéreo), tango.mid, partitura en memoria
Secciones y compases quedan en SECCIONES (para que el mezclador corte fragmentos en compás).
"""
import struct
import subprocess
import wave
from pathlib import Path

import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt

SR = 44100
BPM = 120.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
AQUI = Path(__file__).resolve().parent
N = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}


def m(name):
    return 12 * (int(name[-1]) + 1) + N[name[:-1]]


CH = {  # acorde: (bajo, quinta, voces de piano/guitarra)
    "Gm": ("G2", "D3", ["Bb3", "D4", "G4"]), "Cm": ("C2", "G2", ["Eb4", "G4", "C5"]),
    "D7": ("D2", "A2", ["F#3", "A3", "C4", "D4"]), "Am7b5": ("A2", "Eb3", ["C4", "Eb4", "G4"]),
    "Bb": ("Bb2", "F3", ["F3", "Bb3", "D4"]), "F7": ("F2", "C3", ["A3", "C4", "Eb4"]),
    "G7": ("G2", "D3", ["F3", "B3", "D4"]), "G": ("G2", "D3", ["B3", "D4", "G4"]), "Am": ("A2", "E3", ["C4", "E4", "A4"]),
    "Eb": ("Eb2", "Bb2", ["G3", "Bb3", "Eb4"]),
}

A1 = [
    [(None, .5), ("D5", .5), ("G5", .5), ("Bb5", .5), ("A5", .5), ("G5", .5), ("D5", 1)],
    [("Bb5", 1.5), ("A5", .5), ("G5", 1), (None, 1)],
    [(None, .5), ("Eb5", .5), ("G5", .5), ("C6", .5), ("Bb5", .5), ("G5", .5), ("Eb5", 1)],
    [("D5", 1.5), ("G5", .5), ("Bb5", 2)],
    [(None, .5), ("C6", .5), ("A5", .5), ("Eb5", .5), ("C6", .5), ("A5", .5), ("Eb5", 1)],
    [("D5", .5), ("F#5", .5), ("A5", .5), ("C6", .5), ("Bb5", .5), ("A5", .5), ("F#5", 1)],
    [("G5", 1), ("Bb5", .5), ("D6", 1.5), ("C6", .5), ("Bb5", .5)],
]
A_OPEN = A1 + [[("A5", 1.5), ("F#5", .5), ("D5", 2)]]
A_CLOSE = A1 + [[("G5", 3), (None, 1)]]
A_CH = ["Gm", "Gm", "Cm", "Gm", "Am7b5", "D7", "Gm", "D7"]
A_CH_CLOSE = ["Gm", "Gm", "Cm", "Gm", "Am7b5", "D7", "D7", "Gm"]
A_CLOSE[6] = [("A5", 1), ("C6", .5), ("F#5", 1.5), ("A5", .5), ("F#5", .5)]
B = [
    [("F5", 2), ("D5", 1), ("F5", 1)], [("Eb5", 1.5), ("F5", .5), ("A5", 2)],
    [("Bb5", 2), ("D6", 1), ("C6", .5), ("Bb5", .5)], [("B5", 3), ("G5", 1)],
    [("G5", 1.5), ("Bb5", .5), ("D6", 2)], [("C6", 1), ("Eb6", 1), ("D6", 1), ("C6", 1)],
    [("A5", 1), ("C6", 1), ("D6", 2)], [("D6", 2), ("A5", 1), ("F#5", 1)],
]
B_CH = ["Bb", "F7", "Bb", "G7", "Cm", "Gm", "D7", "D7"]
C = [
    [("B5", .5), ("D6", .5), ("G6", 1), ("D6", .5), ("B5", .5), ("G5", 1)], [("B5", 1.5), ("A5", .5), ("G5", 2)],
    [("A5", .5), ("C6", .5), ("F#6", 1), ("C6", .5), ("A5", .5), ("F#5", 1)], [("A5", 1.5), ("B5", .5), ("C6", 2)],
    [("C6", 1), ("E6", 1), ("A5", 2)], [("C6", 1), ("A5", 1), ("F#5", 2)],
    [("G5", .5), ("B5", .5), ("D6", .5), ("G6", .5), ("B6", 2)], [("A6", 1), ("F#6", 1), ("D6", 2)],
]
C_CH = ["G", "G", "D7", "D7", "Am", "D7", "G", "D7"]

# forma: (sección, melodía, acordes, quién lleva la voz)
FORMA = [("intro", None, ["Gm", "D7"], None),
         ("A", A_OPEN, A_CH, "bando"), ("A", A_CLOSE, A_CH_CLOSE, "acord"),
         ("B", B, B_CH, "piano+acord"),
         ("A", A_CLOSE, A_CH_CLOSE, "bando"),
         ("C", C, C_CH, "tutti"),
         ("A", A_OPEN, A_CH, "acord"), ("A", A_CLOSE, A_CH_CLOSE, "tutti")]
SINCOPA = {2, 5}
INSTR = ["bandoneon", "acordeon", "piano", "contrabajo", "guitarra"]


def score(vueltas=4):
    """{instrumento: [(midi, inicio_s, dur_s, vel)]}, duración total y lista de secciones (nombre, compás de inicio, compases)."""
    ev = {k: [] for k in INSTR}
    secs = []
    bar = 0

    def add(inst, note, beat, dur, vel):
        ev[inst].append((m(note) if isinstance(note, str) else note, (bar * 4 + beat) * BEAT, dur * BEAT, vel))

    for rep in range(vueltas):
        for name, mel, chords, lead in FORMA:
            if rep == 0 and False:
                pass
            secs.append((name + (f"{rep}" if name != "intro" else ""), bar, len(chords), lead))
            for i, ch in enumerate(chords):
                root, fifth, voic = CH[ch]
                nxt = CH[chords[(i + 1) % len(chords)]][0]
                if name == "intro":
                    for b in range(4):
                        for v in voic:
                            add("piano", v, b, .3, 78 if b % 2 == 0 else 62)
                        add("contrabajo", root if b % 2 == 0 else fifth, b, .8, 84)
                        add("acordeon", voic[-1], b, .45, 56)
                        add("guitarra", voic[1], b + .5, .3, 60)
                elif i in SINCOPA:
                    for b, d, v in ((0, .45, 96), (1.5, .45, 84), (3, .5, 90)):          # síncopa 3-3-2
                        for x in voic:
                            add("piano", x, b, d, v - 12)
                            add("guitarra", x, b, d * 1.2, v - 22)
                        add("piano", m(root) + 12, b, d, v - 6)
                        add("contrabajo", root if b != 1.5 else fifth, b, 1.0, v)
                else:
                    for b in range(4):                                                    # marcato en cuatro
                        acc = 92 if b in (0, 2) else 74
                        for x in voic:
                            add("piano", x, b, .28, acc - 14)
                        add("guitarra", voic[(b + i) % len(voic)], b + .5, .35, acc - 24)
                        add("piano", m(root if b % 2 == 0 else fifth) + 12, b, .3, acc - 8)
                        bn = root if b == 0 else fifth if b == 2 else (root if b == 1 else None)
                        if b == 3:
                            bn = m(nxt) - 1 if m(nxt) > m(root) else m(nxt) + 2
                        add("contrabajo", bn, b, .85, acc)
                if mel is not None:
                    t = 0.0
                    for note, d in mel[i]:
                        if note:
                            stac = d <= .5
                            dd = d * (.62 if stac else .95)
                            if lead in ("bando", "tutti"):
                                add("bandoneon", note, t, dd, 96 if t % 2 == 0 else 84)
                                if lead == "tutti":
                                    add("bandoneon", m(note) - 12, t, dd, 66)
                            if lead in ("acord", "tutti"):
                                add("acordeon", note, t, d * .98, 92)
                                if lead == "tutti" and not stac:
                                    add("acordeon", m(note) + 7, t, d * .98, 58)
                            if lead == "piano+acord":
                                add("piano", m(note) + 12, t, d * .9, 82)
                                add("acordeon", note, t, d * .98, 78)
                            if lead == "bando" and not stac:
                                add("acordeon", CH[ch][2][1], t, d * .9, 46)
                        t += d
                bar += 1
    root, fifth, voic = CH["D7"]                                                          # coda: chan-chan
    for v in voic:
        add("piano", v, 0, .5, 108)
        add("bandoneon", v, 0, .5, 104)
        add("acordeon", v, 0, .5, 96)
    add("contrabajo", root, 0, .6, 108)
    root, fifth, voic = CH["Gm"]
    for v in voic:
        add("piano", v, 1, 1.4, 70)
        add("bandoneon", v, 1, 1.4, 62)
        add("acordeon", v, 1, 1.4, 58)
        add("guitarra", v, 1, 1.4, 60)
    add("contrabajo", root, 1, 1.6, 74)
    bar += 1
    secs.append(("coda", bar - 1, 1, None))
    return ev, bar * BAR + 2.5, secs


def hz(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def _bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], btype="band", fs=SR, output="sos"), x)


def tone(inst, note, dur, vel, rng):
    f = hz(note)
    g = (vel / 127.0) ** 1.6
    if inst == "piano":
        n = int((dur + 1.4) * SR)
        t = np.arange(n) / SR
        out = np.zeros(n)
        for k in range(1, 14):
            fk = f * k * np.sqrt(1 + 0.0004 * k * k)
            if fk > SR / 2.2:
                break
            out += np.sin(2 * np.pi * fk * t + k) * (1.0 / k ** 1.25) * np.exp(-t * (2.2 + 0.9 * k) * (0.6 + f / 500))
        env = np.minimum(1, t / 0.004) * np.where(t > dur, np.exp(-(t - dur) * 14), 1)
        return out * env * g * 0.36
    if inst == "contrabajo":
        n = int((dur + 0.5) * SR)
        t = np.arange(n) / SR
        out = sum(np.sin(2 * np.pi * f * k * t) * a for k, a in ((1, 1), (2, .55), (3, .28), (4, .12), (5, .06)))
        env = np.minimum(1, t / 0.012) * np.exp(-t * 2.6) * np.where(t > dur, np.exp(-(t - dur) * 18), 1)
        thump = np.exp(-t * 90) * np.sin(2 * np.pi * 95 * t) * 0.35
        return (out * env + thump) * g * 0.80
    if inst == "guitarra":        # Karplus-Strong de cuerda de nailon
        n = int((dur + 0.9) * SR)
        L = max(2, int(SR / f))
        buf = rng.uniform(-1, 1, L)
        buf = np.convolve(buf, np.ones(3) / 3, mode="same")
        out = np.zeros(n)
        for i in range(n):
            j = i % L
            out[i] = buf[j]
            buf[j] = 0.4985 * (buf[j] + buf[(j + 1) % L])
        env = np.minimum(1, np.arange(n) / (SR * 0.003)) * np.where(np.arange(n) / SR > dur, np.exp(-(np.arange(n) / SR - dur) * 9), 1)
        return out * env * g * 0.55
    if inst == "acordeon":        # tres lengüetas desafinadas (musette) + octava, fuelle con swell y temblor suave
        n = int((dur + 0.22) * SR)
        t = np.arange(n) / SR
        out = np.zeros(n)
        trem = 1 + 0.045 * np.sin(2 * np.pi * 5.8 * t + rng.uniform(0, 6)) * np.minimum(1, t / 0.4)
        for cents, lvl in ((-9, 0.8), (0, 1.0), (9, 0.8)):
            ff = f * 2 ** (cents / 1200)
            for k in range(1, 30):
                if ff * k > SR / 2.3:
                    break
                out += np.sin(2 * np.pi * ff * k * t + 0.9 * k) * lvl * (1.0 if k % 2 else 0.5) / k ** 0.80 * np.exp(-ff * k / 6800)
        out += 0.35 * np.sin(2 * np.pi * f * 2 * t)
        swell = (np.minimum(1, t / 0.05) ** 0.6) * (0.78 + 0.22 * np.sin(np.pi * np.minimum(t / max(dur, .15), 1)))
        env = swell * np.where(t > dur, np.exp(-(t - dur) * 28), 1)
        return out * env * trem * g * 0.16
    n = int((dur + 0.18) * SR)   # bandoneón: dos lengüetas, ataque de fuelle, sonido más seco y rasposo que el acordeón
    t = np.arange(n) / SR
    out = np.zeros(n)
    for det, octv, lvl in ((1.000, 1, 1.0), (1.003, 2, 0.55)):
        ff = f * octv * det
        for k in range(1, 26):
            if ff * k > SR / 2.3:
                break
            out += np.sin(2 * np.pi * ff * k * t + 0.7 * k) * lvl * (1.0 if k % 2 else 0.6) / k ** 0.95 * np.exp(-ff * k / 5200)
    env = (np.minimum(1, t / 0.018) ** 0.7) * (1 + 0.35 * np.exp(-t * 22)) * np.where(t > dur, np.exp(-(t - dur) * 40), 1)
    return out * env * g * 0.27


def golpes_de_referencia(ruta):
    """Recupera los golpes secos (transitorios) de la grabación de referencia: devuelve lista de fragmentos cortos de audio mono."""
    try:
        w = wave.open(str(ruta))
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
        sr = w.getframerate()
    except Exception:
        return []
    h = _hp(x, sr)
    env = np.abs(h)
    k = int(sr * 0.01)
    e = np.convolve(env, np.ones(k) / k, "same")
    thr = np.percentile(e, 97)
    picos, last = [], -10**9
    for i in np.flatnonzero((e[1:-1] > thr) & (e[1:-1] >= e[:-2]) & (e[1:-1] > e[2:])) + 1:
        if i - last > sr * 0.25:
            picos.append(i)
            last = i
    out = []
    for i in picos[:24]:
        seg = x[max(0, i - int(sr * 0.004)):i + int(sr * 0.14)]
        seg = seg * np.hanning(len(seg) * 2)[len(seg):] ** 0.3                       # decae suave
        if len(seg) > 100:
            out.append((seg / (np.abs(seg).max() + 1e-9)).astype(np.float64))
    return out, sr


def _hp(x, sr):
    return sosfilt(butter(2, 900, btype="high", fs=sr, output="sos"), x)


def render(ev, total, golpes=None):
    n = int(total * SR)
    stems = {}
    rng = np.random.default_rng(3)
    for inst, notes in ev.items():
        buf = np.zeros(n + SR * 3)
        for note, t0, dur, vel in notes:
            human = rng.normal(0, 0.006)
            x = tone(inst, note, dur, vel * rng.uniform(0.94, 1.04), rng)
            i = max(0, int((t0 + human) * SR))
            buf[i:i + len(x)] += x[:len(buf) - i]
        stems[inst] = buf[:n]
    if golpes:      # sonidos recuperados de la grabación del usuario: marcato real en los tiempos fuertes
        frag, sr0 = golpes
        buf = np.zeros(n + SR)
        for bar in range(int(total / BAR)):
            for b, gain in ((0, 0.55), (2, 0.42)):
                s = frag[(bar * 2 + b) % len(frag)]
                s = np.interp(np.linspace(0, len(s) - 1, int(len(s) * SR / sr0)), np.arange(len(s)), s)
                i = int((bar * 4 + b) * BEAT * SR)
                buf[i:i + len(s)] += s * gain * 0.35
        stems["golpes"] = buf[:n]
    t = np.arange(int(1.5 * SR)) / SR
    ir = [rng.normal(0, 1, len(t)) * np.exp(-t * 3.8) for _ in range(2)]
    pan = {"bandoneon": -0.30, "acordeon": 0.30, "piano": 0.12, "contrabajo": -0.04, "guitarra": 0.45, "golpes": 0.0}
    out = {}
    for inst, x in stems.items():
        p = pan.get(inst, 0.0)
        L, R = x * np.sqrt(0.5 * (1 - p)), x * np.sqrt(0.5 * (1 + p))
        wet = 0.020 if inst not in ("contrabajo", "golpes") else 0.006
        L = L + fftconvolve(x, ir[0])[:n] * wet
        R = R + fftconvolve(x, ir[1])[:n] * wet
        out[inst] = np.stack([L, R], 1)
    mix = sum(out.values())
    k = 0.89 / np.abs(mix).max()
    return {i: v * k for i, v in out.items()}, mix * k


def write_wav(path, x):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


def main(ref=None):
    ev, total, secs = score()
    golpes = golpes_de_referencia(ref) if ref else None
    stems, mix = render(ev, total, golpes if golpes else None)
    (AQUI / "wav").mkdir(exist_ok=True)
    for inst, x in stems.items():
        write_wav(AQUI / "wav" / f"{inst}.wav", x)
    write_wav(AQUI / "wav" / "mezcla.wav", mix)
    import json
    (AQUI / "wav" / "secciones.json").write_text(json.dumps(dict(bpm=BPM, bar=BAR, total=total, secciones=secs)))
    print(f"tango: {total:.1f} s · {len(secs)} secciones · golpes recuperados: {len(golpes[0]) if golpes else 0}")


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else None)
