#!/usr/bin/env python3
"""Audita el audio final: LUFS integrado, true-peak, muestras a escala completa y la irregularidad de la voz.
Sale con código 1 si algo no cumple (−16 ± 1,5 LUFS, true-peak ≤ −1,0 dBTP, 0 muestras ≥ 0,99)."""
import json, re, subprocess, sys
from pathlib import Path
import numpy as np
from scipy.io import wavfile

VIDEO = Path(__file__).resolve().parents[1] / "video"
VOZ = Path(__file__).resolve().parents[2] / "voice_ai" / "cache_v3" / "final"
mal = 0
for carpeta in ("audio", "audio_sin_voz"):
    files = sorted((VIDEO / carpeta).glob("*.wav"))
    if not files:
        continue
    lst = VIDEO / "_lista_audit.txt"
    lst.write_text("".join(f"file '{f}'\n" for f in files))
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-f", "concat", "-safe", "0", "-i", str(lst), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    L = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1]); TP = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)[-1])
    lst.unlink()
    llenos = 0
    for f in files:
        sr, x = wavfile.read(str(f)); x = x.astype(np.float32) / (2147483648.0 if x.dtype == np.int32 else 32768.0)
        llenos += int((np.abs(x) >= 0.99).sum())
    ok = abs(L + 16) <= 1.5 and TP <= -1.0 and llenos == 0
    print(f"{carpeta}: {L:.1f} LUFS · true-peak {TP:.1f} dBTP · muestras a escala completa {llenos} -> {'OK' if ok else 'FALLA'}")
    mal += 0 if ok else 1
metas = [json.loads(p.read_text()) for p in VOZ.glob("*.json")]
if metas:
    from collections import Counter
    c = Counter(m["perfil"] for m in metas)
    print("perfiles de voz:", dict(c), "· f0 objetivo (Hz) mín/máx:", min(m["f0_obj"] for m in metas), max(m["f0_obj"] for m in metas),
          "· ganancia dB mín/máx:", min(m["gain_db"] for m in metas), max(m["gain_db"] for m in metas))
sys.exit(1 if mal else 0)
