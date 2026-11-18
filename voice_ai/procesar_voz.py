#!/usr/bin/env python3
"""Voz más gruesa e irregular (Praat/PSOLA vía parselmouth), sin saturación.

Entrada: cache_v3/raw/<clave>.wav (TTS crudo). Salida: cache_v3/final/<clave>.wav (float32, 24 kHz) y duraciones.json.
Cada frase recibe un perfil (profunda / neutra / viva) según el clima de su escena, más una deriva suave de tono dentro de la frase.
Uso: python procesar_voz.py [--prueba clave]
"""
import json, sys
from pathlib import Path
import numpy as np, soundfile as sf, parselmouth
from parselmouth.praat import call
from scipy.signal import butter, sosfilt, sosfiltfilt

AQUI = Path(__file__).resolve().parent
RAW, FIN = AQUI / "cache_v3" / "raw", AQUI / "cache_v3" / "final"
FIN.mkdir(parents=True, exist_ok=True)

# perfil: (semitonos respecto de la voz original, razón de formantes, factor de duración, ganancia dB, factor de rango de entonación)
PERFILES = {
    "profunda": (-2.5, 0.94, 1.04, +1.5, 1.10),
    "neutra":   (-1.0, 0.97, 1.00, 0.0, 1.00),
    "viva":     (+0.8, 0.99, 0.96, +1.2, 1.25),
}
PESOS = {   # probabilidades (profunda, neutra, viva) por clima
    "alto": (0.50, 0.40, 0.10), "medio": (0.30, 0.45, 0.25), "suave": (0.20, 0.55, 0.25), "intro": (0.0, 0.2, 0.8),
}
CLIMA = {"revelacion": "alto", "climax": "alto", "tension": "alto", "intriga": "medio", "calma": "suave", "ternura": "suave", "final": "suave"}


def mediana_f0(x, sr):
    p = parselmouth.Sound(x, sr).to_pitch(pitch_floor=70, pitch_ceiling=350)
    f = p.selected_array["frequency"]
    f = f[f > 0]
    return float(np.median(f)) if len(f) else 120.0


def shelf_grave(x, sr, f0=180.0, db=2.5):
    A = 10 ** (db / 40); w0 = 2 * np.pi * f0 / sr; al = np.sin(w0) / 2 * np.sqrt(2)
    c = np.cos(w0)
    b0 = A * ((A + 1) - (A - 1) * c + 2 * np.sqrt(A) * al); b1 = 2 * A * ((A - 1) - (A + 1) * c)
    b2 = A * ((A + 1) - (A - 1) * c - 2 * np.sqrt(A) * al)
    a0 = (A + 1) + (A - 1) * c + 2 * np.sqrt(A) * al; a1 = -2 * ((A - 1) + (A + 1) * c); a2 = (A + 1) + (A - 1) * c - 2 * np.sqrt(A) * al
    from scipy.signal import lfilter
    return lfilter([b0 / a0, b1 / a0, b2 / a0], [1, a1 / a0, a2 / a0], x).astype(np.float32)


def de_esser(x, sr, lo=5500, hi=9500, umbral=0.035, ratio=3.0):
    sos = butter(2, [lo, hi], btype="band", fs=sr, output="sos")
    b = sosfiltfilt(sos, x)
    env = np.maximum(sosfiltfilt(butter(2, 60, btype="low", fs=sr, output="sos"), np.abs(b)), 1e-6)
    g = np.where(env > umbral, (umbral / env) ** (1 - 1 / ratio), 1.0)
    return (x - b + b * g).astype(np.float32)


def procesar(x, sr, perfil, rng):
    st, fr, dur, gdb, rng_f = PERFILES[perfil]
    f0 = mediana_f0(x, sr)
    nuevo = f0 * 2 ** (st / 12)
    snd = parselmouth.Sound(x.astype(np.float64), sr)
    out = call(snd, "Change gender", 70, 350, fr, nuevo, rng_f, dur)
    # deriva suave de tono dentro de la frase: ±0,9 st, un punto cada ~0,35 s
    T = out.xmax
    manip = call(out, "To Manipulation", 0.01, 60, 330)
    pt = call(manip, "Extract pitch tier")
    pasos = np.arange(0, T, 0.35)
    amp = float(rng.uniform(0.5, 0.95))
    walk = np.cumsum(rng.normal(0, 0.45, len(pasos)))
    walk = (walk - walk.mean()) / (np.abs(walk).max() + 1e-9) * amp           # en semitonos, acotado
    for k, t0 in enumerate(pasos):
        t1 = min(T, t0 + 0.35)
        call(pt, "Multiply frequencies", t0, t1, float(2 ** (walk[k] / 12)))
    call([pt, manip], "Replace pitch tier")
    res = call(manip, "Get resynthesis (overlap-add)")
    y = np.asarray(res.values[0], dtype=np.float32)
    y = shelf_grave(y, sr, 180.0, 2.5 + (1.0 if perfil == "profunda" else 0.0))
    y = de_esser(y, sr)
    y = y * 10 ** (gdb / 20)
    return y, dict(perfil=perfil, f0_in=round(f0, 1), f0_obj=round(nuevo, 1), deriva_st=round(amp, 2), gain_db=gdb)


def clima_de(o):
    esc = o.get("escena", "")
    if esc == "puente":
        return "medio"
    try:
        import sonido
        plan = sonido.MOOD.get(esc, [(0, "calma")])
        return CLIMA[plan[-1][1]]
    except Exception:
        return "medio"


def main():
    lines = json.loads((AQUI / "lineas_v3.json").read_text())
    intro = {l["text"] for l in lines if l.get("escena") == "puente" and l["text"][:9] in ("Gorgonops", "Doscienta", "Setecient", "Un rango ")}
    meta = {}
    for i, o in enumerate(lines):
        f_in, f_out = RAW / f"{o['key']}.wav", FIN / f"{o['key']}.wav"
        if not f_in.exists():
            continue
        rng = np.random.default_rng(7000 + i)
        if f_out.exists():
            continue
        x, sr = sf.read(str(f_in)); x = x.astype(np.float32)
        clima = "intro" if o["text"] in intro else clima_de(o)
        perfil = rng.choice(list(PERFILES), p=PESOS[clima])
        y, m = procesar(x, sr, str(perfil), rng)
        pk = float(np.abs(y).max())
        if pk > 0.95:
            y *= 0.95 / pk                                                      # lineal, sin saturar
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
