"""Procesado de voz v12: voz de narrador adulto, neutral y humana.

 1. `Change gender` suave (formantes x0,95, mediana 124 Hz, rango x1,6; duración sin cambios).
 2. Ecualización de fase lineal con la curva de balance tonal de la grabación de referencia (perfil_referencia.json).
 3. Humanización mínima y continua: derivas lentas (<= 1 %) de tono, graves y agudos. Cada deriva sube de a poquito
    (incrementos de 0,01–0,07 %) hasta un tope de 0,3–1,0 %, baja igual hasta el punto neutral y arranca otro ciclo (±).
Las derivas se calculan sobre el TIEMPO GLOBAL de la película, así que son continuas entre frases.
"""
import json
from pathlib import Path

import numpy as np
from scipy.signal import firwin2, fftconvolve, butter, sosfiltfilt

import os
PERFIL = Path(__file__).resolve().parents[2] / "voice_ai" / os.environ.get("PERFIL_JSON", "perfil_referencia.json")
_P = {}


def perfil():
    if "p" not in _P:
        _P["p"] = json.loads(PERFIL.read_text())
    return _P["p"]


QUEBRACHO = dict(nombre="Quebracho", formantes=0.90, mediana_hz=112.0, rango=2.5, graves_conservados=0.5,
                 cuerpo_db=[("170", 1.0), ("420", 1.5)], rms_dbfs=-14.0)


def gender(x, sr, ratio=QUEBRACHO["formantes"], med=QUEBRACHO["mediana_hz"], rango=QUEBRACHO["rango"]):
    import parselmouth
    from parselmouth.praat import call
    return call(parselmouth.Sound(x, sr), "Change gender", 70, 300, ratio, med, rango, 1.0).values[0].astype(np.float64)


def ciclos(total, seed, paso=0.5, tope=(0.30, 1.00), inc=(0.01, 0.07)):
    """Serie p(t) como fracción (0,01 = 1 %): sube con incrementos de 0,01–0,07 % por paso hasta el tope, baja igual hasta 0 y reinicia."""
    rng = np.random.default_rng(seed)
    n = int(total / paso) + 4
    p = np.zeros(n)
    i, v = 0, 0.0
    while i < n:
        s = rng.choice([-1.0, 1.0])
        top = rng.uniform(*tope)
        while abs(v) < top and i < n:
            v += s * rng.uniform(*inc)
            p[i] = v
            i += 1
        while v * s > 0 and i < n:
            v -= s * rng.uniform(*inc)
            if v * s < 0:
                v = 0.0
            p[i] = v
            i += 1
        for _ in range(int(rng.integers(0, 4))):             # unos pasos en el punto neutral antes del próximo ciclo
            if i < n:
                p[i] = 0.0
                i += 1
    return np.arange(n) * paso, p / 100.0


class Derivas:
    def __init__(self, total=900.0):
        self.tono = ciclos(total, 101)
        self.graves = ciclos(total, 202, tope=(0.30, 1.00))
        self.agudos = ciclos(total, 303, tope=(0.30, 1.00))
        self.ganancia = ciclos(total, 404, tope=(0.30, 1.00))

    @staticmethod
    def f(par, t):
        return np.interp(t, par[0], par[1])

    def tono_en(self, t):
        return float(self.f(self.tono, t))


def deriva_tono(x, sr, T0, D):
    import parselmouth
    from parselmouth.praat import call
    snd = parselmouth.Sound(x, sr)
    man = call(snd, "To Manipulation", 0.01, 70, 300)
    pt = call(man, "Extract pitch tier")
    n = int(call(pt, "Get number of points"))
    if n < 3:
        return x
    new = call("Create PitchTier", "d", 0, snd.duration)
    for i in range(1, n + 1):
        t = call(pt, "Get time from index", i)
        v = call(pt, "Get value at index", i)
        call(new, "Add point", t, v * (1 + D.tono_en(T0 + t)))
    call([man, new], "Replace pitch tier")
    y = call(man, "Get resynthesis (overlap-add)").values[0].astype(np.float64)
    return y[:len(x)] if len(y) >= len(x) else np.pad(y, (0, len(x) - len(y)))


def neutralizar(x, sr, rango=0.72):
    """Baja el rango de entonación (voz menos exaltada) sin tocar formantes ni mediana de tono ni duración."""
    import parselmouth
    from parselmouth.praat import call
    return call(parselmouth.Sound(x, sr), "Change gender", 75, 350, 1.0, 0, rango, 1.0).values[0].astype(np.float64)


def eq_fir(x, sr, fuerza=1.0, tope=None, desde=None):
    pf = perfil()
    c = list(pf["centros"])
    g = [max(-9.0, min(8.0, v*1.15*(QUEBRACHO["graves_conservados"] if c_ < 320 else 1.0))) for c_, v in zip(c, pf["corr_db"])]
    f = [0.0] + c + [sr / 2]
    gg = [g[0]] + g + [g[-1]]
    if tope is not None:
        g = [max(-tope, min(tope, v)) for v in g]
        gg = [g[0]] + g + [g[-1]]
    if desde is not None:                                               # sin corregir por debajo de «desde» Hz: se conserva el tono profundo
        g = [v if c_ >= desde else 0.0 for c_, v in zip(c, g)]
        gg = [g[0]] + g + [g[-1]]
    h = firwin2(2049, f, 10 ** (np.array(gg) * fuerza / 20), fs=sr)
    return fftconvolve(x, h, mode="same")


def deriva_bandas(x, sr, T0, D):
    t = np.arange(len(x)) / sr + T0
    lo = sosfiltfilt(butter(2, 220, "low", fs=sr, output="sos"), x)
    hi = sosfiltfilt(butter(2, 3200, "high", fs=sr, output="sos"), x)
    return x + lo * D.f(D.graves, t) * 3.0 + hi * D.f(D.agudos, t) * 3.0         # ±1 % de deriva ≈ ±3 % de ganancia de banda (≈ ±0,26 dB)


def deriva_ganancia(x, sr, T0, D):
    t = np.arange(len(x)) / sr + T0
    return x * (1.0 + D.f(D.ganancia, t) * 3.5)                               # ±1 % de deriva ≈ ±0,3 dB de ganancia


def grave(x, sr, T0, D, factor=0.84, formantes=0.93):
    """Voz más grave y gruesa en UN solo paso de Praat (PSOLA): mediana de la frase x0,84 (con la microderiva lenta de ±1 %), formantes x0,93,
    rango de entonación SIN cambio (no se aplana) y sin segunda resíntesis. La mediana de cada frase se conserva relativa, así que la variedad
    natural entre frases se mantiene."""
    import parselmouth
    from parselmouth.praat import call
    s = parselmouth.Sound(x, sr)
    p = s.to_pitch(pitch_floor=75, pitch_ceiling=350).selected_array["frequency"]
    p = p[p > 0]
    if len(p) < 10:
        return x
    nuevo = float(np.median(p)) * factor * (1.0 + D.tono_en(T0))
    return call(s, "Change gender", 75, 350, formantes, nuevo, 1.0, 1.0).values[0].astype(np.float64)
