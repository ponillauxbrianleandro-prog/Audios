#!/usr/bin/env python3
"""Arma cache_v16/raw eligiendo, por frase, entre la toma viva (cache_v13, T0,62) y la sobria (cache_v14, T0,45) con un patrón irregular
(rachas de 2-5 frases, ≈40 % vivas); si la elegida se pasa de su hueco >12 % y la otra no, se usa la otra."""
import json, shutil
from pathlib import Path
import numpy as np, soundfile as sf
AQUI = Path(__file__).resolve().parent
O = AQUI / "cache_v16"; (O / "raw").mkdir(parents=True, exist_ok=True)
for f in ("durs_v11.json", "tiempos_lineas.json"):
    shutil.copy(AQUI / "cache_v14" / f, O / f)
D = json.loads((O / "durs_v11.json").read_text()); T = json.loads((O / "tiempos_lineas.json").read_text())
claves = sorted(D, key=lambda k: T[k])
rng = np.random.default_rng(16)
vivas, i, vivo = [], 0, bool(rng.integers(0, 2))
while i < len(claves):
    n = int(rng.integers(2, 6))
    if vivo is False and rng.random() < 0.25: n += 1                       # las sobrias duran un poco más: ≈40 % vivas
    vivas += [vivo] * n; i += n; vivo = not vivo
sel = {}
for k, v in zip(claves, vivas):
    a, b = AQUI / "cache_v13/raw" / f"{k}.wav", AQUI / "cache_v14/raw" / f"{k}.wav"
    pri, sec = (a, b) if v else (b, a)
    d = lambda p: sf.info(str(p)).duration / D[k]
    if d(pri) > 1.12 and d(sec) <= 1.12:
        pri, sec = sec, pri
    shutil.copy(pri, O / "raw" / f"{k}.wav")
    sel[k] = "viva(T0,62)" if pri == a else "sobria(T0,45)"
json.dump(sel, open(O / "seleccion.json", "w"), ensure_ascii=False)
print(len(sel), "frases;", sum(v.startswith("viva") for v in sel.values()), "vivas")
print("rachas:", "".join("V" if s.startswith("viva") else "s" for s in sel.values()))
