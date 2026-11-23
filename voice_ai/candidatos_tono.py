#!/usr/bin/env python3
"""Compara 3 formas de hacer la voz más grave/gruesa sobre frases crudas del clon, midiendo contra la grabación de referencia."""
import glob, subprocess, sys, tempfile, os
import numpy as np, soundfile as sf, parselmouth, scipy.signal as ss
from parselmouth.praat import call
import json
from pathlib import Path
AQUI = Path(__file__).resolve().parent


def met(x, s):
    sn = parselmouth.Sound(x.astype(float), s)
    pp = call(sn, "To PointProcess (periodic, cc)", 75, 350)
    jit = call(pp, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3) * 100
    shi = call([sn, pp], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6) * 100
    p = sn.to_pitch(time_step=0.01, pitch_floor=75, pitch_ceiling=350).selected_array["frequency"]
    v = p > 0; par = v[1:] & v[:-1]
    c = 1200 * np.abs(np.log2(p[1:][par] / p[:-1][par]))
    f = p[v]
    it = sn.to_intensity(minimum_pitch=75, time_step=0.01).values[0]
    pk, _ = ss.find_peaks(it, prominence=3, distance=8)
    iv = np.diff(pk) * 0.01
    fm = sn.to_formant_burg(max_number_of_formants=5, maximum_formant=5000)
    f2 = np.nanmedian([fm.get_value_at_time(2, t) for t in np.arange(0.1, sn.duration - 0.1, 0.05)])
    xx = x if s == 24000 else ss.resample_poly(x, 24000, s)
    fr, P = ss.welch(xx, 24000, nperseg=2048)
    return dict(f0=float(np.median(f)), jit=jit, shi=shi, sd=float(np.std(12 * np.log2(f / np.median(f)))), paso=float(np.median(c)),
                s200=float(100 * np.mean(c > 200)), cv=float(iv.std() / iv.mean()) if len(iv) > 5 else float("nan"),
                hnr=float(np.median(call(sn.to_harmonicity_cc(), "Get mean", 0, 0))), f2=float(f2), centroide=float((fr * P).sum() / P.sum()))


def c1(x, s, formantes=0.93, mediana=128.0):
    return call(parselmouth.Sound(x.astype(float), s), "Change gender", 75, 350, formantes, mediana, 1.0, 1.0).values[0]


def c3(x, s):
    with tempfile.TemporaryDirectory() as d:
        a, b = os.path.join(d, "a.wav"), os.path.join(d, "b.wav")
        sf.write(a, x.astype(np.float32), s)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", a, "-af", "rubberband=pitch=0.84:pitchq=quality:formant=preserved:transients=smooth", b], check=True)
        return sf.read(b)[0]


if __name__ == "__main__":
    x, s = sf.read(str(AQUI / "cache_v13/ref/completo24.wav"))
    R = [met(x[i * s * 20:(i + 1) * s * 20], s) for i in range(1, 10)]
    ref = {k: float(np.mean([r[k] for r in R])) for k in R[0]}
    files = [f for f in sorted(glob.glob(str(AQUI / "cache_v13/raw/*.wav")) + glob.glob(str(AQUI / "cache_v14/raw/*.wav"))) if "tmp" not in f]
    sel = []
    for f in files:
        y, s2 = sf.read(f)
        if len(y) / s2 > 3.5: sel.append(f)
    sel = sel[::max(1, len(sel) // 8)][:8]
    out = {"GRABACIÓN": ref}
    for nom, fn in [("crudo", lambda a, b: a), ("C1 formantes .93", c1), ("C2 formantes 1.0", lambda a, b: c1(a, b, 1.0)), ("C3 rubberband .84", c3)]:
        M = [met(fn(*sf.read(f)[:2]) if nom != "crudo" else sf.read(f)[0], sf.read(f)[1]) for f in sel]
        out[nom] = {k: float(np.nanmean([m[k] for m in M])) for k in M[0]}
    print("%-20s %6s %5s %6s %5s %6s %6s %5s %5s %6s %7s" % ("", "F0", "jit", "shim", "sd", "paso", ">200c", "cv", "hnr", "F2", "centr"))
    for k, v in out.items():
        print("%-20s %6.0f %5.2f %6.2f %5.2f %6.1f %6.2f %5.2f %5.1f %6.0f %7.0f" % (k, v["f0"], v["jit"], v["shi"], v["sd"], v["paso"], v["s200"], v["cv"], v["hnr"], v["f2"], v["centroide"]))
    json.dump(out, open(AQUI / "cache_v14/candidatos_tono.json", "w"))
