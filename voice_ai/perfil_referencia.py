#!/usr/bin/env python3
"""Perfil tonal de referencia (episodio 005, voz v12).

Mide el espectro promedio (tercios de octava) de la grabación de referencia del usuario y el de la voz sintética ya "masculinizada"
suavemente, y guarda la curva de ecualización que lleva a la segunda hacia el BALANCE de graves/medios/agudos de la primera.
Solo copia el balance tonal (ecualización); no el timbre, la identidad ni la entonación del hablante.

  python perfil_referencia.py <grabacion.mp3>   ->  perfil_referencia.json
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import parselmouth
import soundfile as sf
from parselmouth.praat import call
from scipy.signal import welch

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "episodio-005-vetusodon" / "render"))
SR = 24000
CENTROS = [100 * 2 ** (k / 3) for k in range(0, 19)]          # 100 Hz ... ~6,4 kHz
FUERZA = 0.70
LIMITE_DB = 8.0


def ltas(x, sr):
    fr = int(0.05 * sr)
    n = len(x) // fr
    E = np.array([np.sqrt((x[i * fr:(i + 1) * fr] ** 2).mean()) for i in range(n)])
    keep = np.concatenate([x[i * fr:(i + 1) * fr] for i in range(n) if E[i] > np.percentile(E, 40)])
    f, P = welch(keep, sr, nperseg=4096)
    L = np.array([10 * np.log10(P[(f >= c / 2 ** (1 / 6)) & (f < c * 2 ** (1 / 6))].sum() + 1e-20) for c in CENTROS])
    return L - L[min(range(len(CENTROS)), key=lambda i: abs(CENTROS[i] - 1000))]


def f0_stats(x, sr):
    p = parselmouth.Sound(x, sr).to_pitch(pitch_floor=60, pitch_ceiling=350).selected_array["frequency"]
    p = p[p > 0]
    return [float(np.median(p)), float(np.percentile(p, 10)), float(np.percentile(p, 90))]


def main(ref, cache="cache_v9", gen=True, salida="perfil_referencia.json"):
    tmp = AQUI / "cache_v9" / "_ref24.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", ref, "-ac", "1", "-ar", str(SR), str(tmp)], check=True)
    x, sr = sf.read(str(tmp))
    L_ref = ltas(x, sr)
    stats = f0_stats(x, sr)
    proc = []
    for f in sorted((AQUI / cache / "raw").glob("*.wav")):
        if "tmp" in f.name:
            continue
        y, s2 = sf.read(str(f))
        y = y.mean(1) if y.ndim > 1 else y
        z = call(parselmouth.Sound(y.astype(float), s2), "Change gender", 70, 300, 0.95, 124, 1.6, 1.0).values[0] if gen else y.astype(float)
        if s2 != SR:
            z = np.interp(np.linspace(0, len(z) - 1, int(len(z) * SR / s2)), np.arange(len(z)), z)
        proc.append(z)
    L_tts = ltas(np.concatenate(proc), SR)
    dif = L_ref - L_tts
    sm = np.convolve(np.pad(dif, 1, mode="edge"), np.ones(3) / 3, mode="valid")           # suavizado de 3 bandas
    corr = np.clip(sm * FUERZA, -LIMITE_DB, LIMITE_DB)
    out = dict(centros=CENTROS, corr_db=[round(float(c), 2) for c in corr], ref_ltas=[round(float(v), 2) for v in L_ref],
               tts_ltas=[round(float(v), 2) for v in L_tts], f0_ref=stats)
    (AQUI / salida).write_text(json.dumps(out, indent=1))
    print("banda Hz   ref    TTS(sin EQ)  corrección dB")
    for c, a, b, d in zip(CENTROS, L_ref, L_tts, corr):
        print(f"{c:7.0f} {a:6.1f} {b:9.1f} {d:9.1f}")
    print("F0 de la grabación (mediana, p10, p90):", [round(v) for v in stats])


if __name__ == "__main__":
    main(sys.argv[1], *( [sys.argv[2], sys.argv[3] != "nogender", sys.argv[4]] if len(sys.argv) > 4 else [] ))
