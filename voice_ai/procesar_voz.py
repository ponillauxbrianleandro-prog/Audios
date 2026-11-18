#!/usr/bin/env python3
"""Voz estable y apenas más viva (Praat/PSOLA vía parselmouth), sin saturación ni cambios de timbre.

1) Todas las frases se llevan al mismo tono objetivo (mediana de las tomas − 0,3 st), con correcciones pequeñas.
2) Encima, una variación MUY lenta y continua en el tiempo del documental (viveza v(t) ∈ [0,1]):
   tono ±0,4 st, ritmo hasta 3 % más lento, entonación ×1,00–1,10, ganancia ±1 dB. Frases vecinas casi idénticas.
Entrada: cache_v3/raw/<clave>.wav · Salida: cache_v3/final/<clave>.wav y .json, y duraciones.json.
"""
import json, sys
from pathlib import Path
import numpy as np, soundfile as sf, parselmouth
from parselmouth.praat import call
from scipy.signal import butter, sosfiltfilt, lfilter

AQUI = Path(__file__).resolve().parent
RAW, FIN = AQUI / "cache_v3" / "raw", AQUI / "cache_v3" / "final"
FIN.mkdir(parents=True, exist_ok=True)


def mediana_f0(x, sr):
    p = parselmouth.Sound(x.astype(np.float64), sr).to_pitch(pitch_floor=70, pitch_ceiling=350).selected_array["frequency"]
    p = p[p > 0]
    return float(np.median(p)) if len(p) else None


def viveza(t):
    """Curva lenta y continua (períodos de 91 y 150 s) en [0, 1]."""
    return float(np.clip(0.5 + 0.30 * np.sin(2 * np.pi * t / 150 + 0.7) + 0.20 * np.sin(2 * np.pi * t / 91 + 2.1), 0, 1))


def shelf_grave(x, sr, f0=180.0, db=1.0):
    A = 10 ** (db / 40); w0 = 2 * np.pi * f0 / sr; al = np.sin(w0) / 2 * np.sqrt(2); c = np.cos(w0)
    b0 = A * ((A + 1) - (A - 1) * c + 2 * np.sqrt(A) * al); b1 = 2 * A * ((A - 1) - (A + 1) * c)
    b2 = A * ((A + 1) - (A - 1) * c - 2 * np.sqrt(A) * al)
    a0 = (A + 1) + (A - 1) * c + 2 * np.sqrt(A) * al; a1 = -2 * ((A - 1) + (A + 1) * c); a2 = (A + 1) + (A - 1) * c - 2 * np.sqrt(A) * al
    return lfilter([b0 / a0, b1 / a0, b2 / a0], [1, a1 / a0, a2 / a0], x).astype(np.float32)


def de_esser(x, sr, lo=5500, hi=9500, umbral=0.035, ratio=2.5):
    b = sosfiltfilt(butter(2, [lo, hi], btype="band", fs=sr, output="sos"), x)
    env = np.maximum(sosfiltfilt(butter(2, 60, btype="low", fs=sr, output="sos"), np.abs(b)), 1e-6)
    g = np.where(env > umbral, (umbral / env) ** (1 - 1 / ratio), 1.0)
    return (x - b + b * g).astype(np.float32)


def procesar(x, sr, f0_obj, v):
    f0 = mediana_f0(x, sr) or f0_obj
    pitch_var = (v - 0.5) * 0.8                    # ±0,4 st
    destino = f0_obj * 2 ** (pitch_var / 12)
    dur = 1.0 + 0.03 * (1 - v)                     # 1,00–1,03 (como mucho 3 % más lento)
    rango = 1.0 + 0.10 * v
    snd = parselmouth.Sound(x.astype(np.float64), sr)
    out = call(snd, "Change gender", 70, 350, 1.0, float(destino), float(rango), float(dur))     # sin cambio de formantes
    y = np.asarray(out.values[0], dtype=np.float32)
    y = de_esser(shelf_grave(y, sr, 180.0, 1.0), sr)
    g_db = (v - 0.5) * 2.0
    y = y * 10 ** (g_db / 20)
    return y, dict(f0_in=round(f0, 1), f0_obj=round(float(destino), 1), v=round(v, 3), dur=round(dur, 3), rango=round(rango, 3), gain_db=round(g_db, 2),
                   dev_in_st=round(12 * np.log2(f0 / f0_obj), 2))


def main():
    lines = json.loads((AQUI / "lineas_v3.json").read_text())
    f0s = []
    for o in lines:
        f = RAW / f"{o['key']}.wav"
        if f.exists():
            x, sr = sf.read(str(f)); f0s.append(mediana_f0(x.astype(np.float32), sr))
    base = float(np.median([v for v in f0s if v]))
    objetivo = base * 2 ** (-0.3 / 12)
    print(f"tono objetivo {objetivo:.1f} Hz (mediana {base:.1f})", flush=True)
    (AQUI / "cache_v3" / "objetivo_f0.json").write_text(json.dumps(dict(objetivo=objetivo, base=base)))
    for i, o in enumerate(lines):
        f_in, f_out = RAW / f"{o['key']}.wav", FIN / f"{o['key']}.wav"
        if not f_in.exists() or f_out.exists():
            continue
        x, sr = sf.read(str(f_in)); x = x.astype(np.float32)
        y, m = procesar(x, sr, objetivo, viveza(float(o.get("t_film", 0.0))))
        pk = float(np.abs(y).max())
        if pk > 0.95:
            y *= 0.95 / pk
        sf.write(str(f_out), y, sr, subtype="FLOAT")
        (FIN / f"{o['key']}.json").write_text(json.dumps(m))
        print(i + 1, o["key"], m, flush=True)
    d = {}
    for o in lines:
        f = FIN / f"{o['key']}.wav"
        if f.exists():
            x, sr = sf.read(str(f)); d[o["key"]] = round(len(x) / sr, 3)
    (AQUI / "duraciones.json").write_text(json.dumps(d))
    print("duraciones:", len(d), "de", len(lines))


if __name__ == "__main__":
    main()
