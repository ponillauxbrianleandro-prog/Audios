#!/usr/bin/env python3
"""Escribe voice_ai/cache_v9/tiempos_lineas.json: instante global (s) en que empieza cada frase de la película."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import world, episodio as E

world.load()
TL, _ = E.timeline()
out = {f"{c['esc']:02d}_{k}": round(c["t0"] + t, 3) for c in TL for k, (t, d, tx) in enumerate(c["lineas"])}
p = Path(__file__).resolve().parents[2] / "voice_ai" / "cache_v9" / "tiempos_lineas.json"
p.write_text(json.dumps(out))
print(len(out), "frases · última en", max(out.values()), "s")
