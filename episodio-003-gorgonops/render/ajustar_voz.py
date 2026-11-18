#!/usr/bin/env python3
"""Calcula, para cada frase, la duración objetivo T que hace que la voz llene exactamente cada escena YA renderizada.
Entradas: voice_ai/planos_congelados.json (cuadros reales de cada plano), duraciones_v6_naturales.json.
Salida: voice_ai/objetivos_T.json {clave: segundos}. procesar_voz.py estira cada frase hasta su T con Praat (PSOLA)."""
import json, sys
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import documental as D

VA = Path(__file__).resolve().parents[2] / "voice_ai"
fro = json.loads((VA / "planos_congelados.json").read_text())
nat = json.loads((VA / "duraciones_v6_naturales.json").read_text())
D.world.load(); D.engine.setup()
SC = D.build()
T, fs, esc, relleno = {}, [], [], {}
shots_i = {}
for s in SC:
    cap = s["cap"]
    j0 = shots_i.get(cap, 0)
    n = len(s["shots"])
    S = sum(fro[str(cap)][j0:j0 + n]) / D.FPS
    shots_i[cap] = j0 + n
    fixed, voice, claves = 0.0, 0.0, []
    for kind, val in s["items"]:
        if kind in ("sil", "vis"):
            fixed += val
        elif kind == "quote":
            k = D.clave_voz(D.texto_cita(val)); fixed += 1.4
            if k in nat: voice += nat[k]; claves.append(k)
        elif kind == "nar":
            k = D.clave_voz(val); fixed += D.LEAD_VOZ + D.GAP_VOZ
            if k in nat: voice += nat[k]; claves.append(k)
    if not claves or s["name"].startswith("0 ·"):
        continue
    esc.append((s["name"], (S - fixed) / voice, voice, claves, fixed))
# suavizado: escenas vecinas con ritmos casi iguales (nunca más lento de lo que cabe; lo que sobra se reparte como pausa)
need = np.array([e[1] for e in esc])
ker = np.convolve(np.pad(need, 1, mode="edge"), np.ones(3) / 3, mode="valid")
for (name, fn, voice, claves, fixed), sm in zip(esc, ker):
    f = float(min(fn, sm, 1.30))
    fs.append((name, round(f, 3)))
    for k in claves:
        T[k] = round(nat[k] * f, 3)
    pad = (fn - f) * voice
    if pad > 0.05:
        relleno[name] = round(pad, 2)
(VA / "relleno_escena.json").write_text(json.dumps(relleno))
# frases sin escena (apertura y puentes): se conservan naturales; la apertura se ajusta a su ventana en timeline()
from guion_extra import INTRO
intro_k = {D.clave_voz(t) for t in INTRO}
fp = float(np.median([f for _, f in fs]))
for k, v in nat.items():
    T.setdefault(k, v if k in intro_k else round(v * fp, 3))      # puentes al mismo ritmo que el resto; la apertura va rápida
(VA / "objetivos_T.json").write_text(json.dumps(T))
print("factor de estiramiento de la voz por escena (1,00 = ritmo natural) y pausa añadida:")
for n_, f_ in fs:
    print(f"  {n_[:34]:34s} {f_:.3f}   +{relleno.get(n_, 0):.1f} s de pausa repartida")
import numpy as np
v = np.array([f for _, f in fs]); print(f"mín {v.min():.2f} · mediana {np.median(v):.2f} · máx {v.max():.2f}")
