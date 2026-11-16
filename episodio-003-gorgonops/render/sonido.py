#!/usr/bin/env python3
"""Banda sonora por capítulo: ambiente sintetizado (viento, agua, insectos) + tango por instrumentos.

Sin narración: la voz se graba después y se mezcla encima.
Uso: python3 sonido.py   -> ../video/audio/NN-nombre.wav (48 kHz estéreo)
Requiere los WAV de ../musica/wav/ (los crea musica/generar_tango.py).
"""
import sys
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

sys.path.insert(0, str(Path(__file__).resolve().parent))
SR = 48000
AQUI = Path(__file__).resolve().parent
MUS = AQUI.parent / "musica" / "wav"
OUT = AQUI.parent / "video" / "audio"


def load(name):
    with wave.open(str(MUS / f"{name}.wav")) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float32).reshape(-1, 2) / 32768
        sr = w.getframerate()
    n = int(len(x) * SR / sr)
    idx = np.linspace(0, len(x) - 1, n)
    return np.stack([np.interp(idx, np.arange(len(x)), x[:, c]) for c in (0, 1)], 1).astype(np.float32)


def band(x, lo, hi):
    sos = butter(2, [lo, hi], btype="band", fs=SR, output="sos")
    return sosfilt(sos, x, axis=0)


def lfo(n, rate, seed, lo=0.3, hi=1.0):
    r = np.random.default_rng(seed)
    k = max(4, int(n / SR * rate) + 4)
    pts = r.uniform(lo, hi, k)
    return np.interp(np.linspace(0, k - 1, n), np.arange(k), pts).astype(np.float32)


def ambience(n, seed, wind=1.0, water=1.0, insects=1.0):
    r = np.random.default_rng(seed)
    out = np.zeros((n, 2), np.float32)
    for c in (0, 1):
        w = band(r.normal(0, 1, n), 90, 700) * lfo(n, 0.12, seed + c, 0.25, 1.0) * 0.050 * wind
        w += band(r.normal(0, 1, n), 600, 2200) * lfo(n, 0.3, seed + 5 + c, 0.0, 1.0) ** 2 * 0.010 * wind
        ag = band(r.normal(0, 1, n), 700, 3500) * (0.5 + 0.5 * lfo(n, 6.0, seed + 9 + c, 0.2, 1.0)) * 0.012 * water
        ins = band(r.normal(0, 1, n), 4200, 7500) * lfo(n, 1.5, seed + 13 + c, 0.0, 1.0) ** 4 * 0.006 * insects
        out[:, c] = w + ag + ins
    return out


def fade(x, a=2.0, b=3.0):
    n = len(x)
    e = np.ones(n, np.float32)
    na, nb = int(a * SR), int(b * SR)
    e[:na] = np.linspace(0, 1, na) ** 2
    e[n - nb:] = np.linspace(1, 0, nb) ** 2
    return x * e[:, None]


def music(n, stems, parts, start=0.0, gain=1.0, t_in=4.0, t_out=5.0, offset=0.0):
    """Tango en bucle con los instrumentos pedidos, entre 'start' y el final."""
    out = np.zeros((n, 2), np.float32)
    mix = sum(stems[p] for p in parts)
    L = len(mix)
    i0 = int(start * SR)
    seg = n - i0
    if seg <= 0:
        return out
    idx = (np.arange(seg) + int(offset * SR)) % L
    out[i0:] = fade(mix[idx], t_in, t_out) * gain
    return out


# capítulo: (viento, agua, insectos), lista de entradas de música (instrumentos, inicio s, ganancia, desplazamiento en el tango)
PLAN = {
    0: ((1.0, 1.0, 0.8), [(("contrabajo",), 50.0, 0.9, 4.0)]),
    1: ((0.8, 1.0, 1.0), [(("bandoneon", "contrabajo"), 3.0, 0.55, 4.0)]),
    2: ((0.9, 0.5, 0.8), [(("piano", "contrabajo"), 2.0, 0.50, 4.0), (("violin",), 216.0, 0.6, 36.0)]),
    3: ((0.7, 0.9, 1.3), [(("bandoneon", "violin", "piano", "contrabajo"), 2.0, 0.42, 4.0)]),
    4: ((1.6, 0.2, 0.3), [(("contrabajo", "piano"), 2.0, 0.40, 36.0)]),
    5: ((1.2, 0.3, 0.4), [(("violin", "bandoneon"), 50.0, 0.50, 36.0)]),
    6: ((0.8, 0.7, 1.0), [(("bandoneon", "violin", "piano", "contrabajo"), 2.0, 0.50, 69.0)]),
    7: ((0.9, 1.1, 0.9), [(("bandoneon",), 70.0, 0.40, 4.0)]),
}


def main():
    import documental as D
    D.world.load()
    D.engine.setup()
    tl = D.timeline(D.build())
    stems = {k: load(k) for k in ("bandoneon", "violin", "piano", "contrabajo")}
    coda = load("tango")[-int(5.2 * SR):]
    OUT.mkdir(parents=True, exist_ok=True)
    for cap in sorted(tl):
        n = int(round(tl[cap]["t"] * 24) / 24 * SR)
        (w, a, i), cues = PLAN[cap]
        x = fade(ambience(n, 100 + cap, w, a, i), 1.5, 1.5)
        for parts, start, gain, off in cues:
            x += music(n, stems, parts, start, gain * 0.55, offset=off)
        if cap == 7:                     # coda: chan-chan antes de los créditos
            i0 = n - int(21.0 * SR)
            x[i0:i0 + len(coda)] += coda[:n - i0] * 0.5
        # las citas bajan la música un poco (hay texto en pantalla)
        peak = np.abs(x).max()
        x = x / max(peak, 1e-6) * min(peak, 0.5)
        with wave.open(str(OUT / f"{D.CHAPTERS[cap]}.wav"), "wb") as wv:
            wv.setnchannels(2)
            wv.setsampwidth(2)
            wv.setframerate(SR)
            wv.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
        print(D.CHAPTERS[cap], f"{n / SR:.1f} s", f"pico {np.abs(x).max():.2f}")


if __name__ == "__main__":
    main()
