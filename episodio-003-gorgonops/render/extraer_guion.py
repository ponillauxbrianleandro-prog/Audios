#!/usr/bin/env python3
"""Vuelca la narración del documental (por capítulo, con su hueco de tiempo) a ../../voice_ai/lineas.json."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import documental as D
D.world.load(); D.engine.setup()
SC = D.build()
out = []
for s in SC:
    t = None
    pass
caps = {}
for s in SC:
    c = caps.setdefault(s["cap"], dict(t=0.0))
    t = c["t"]
    t0 = t
    for kind, val in s["items"]:
        if kind in ("sil", "vis"):
            t += val
        elif kind == "nota":
            pass
        elif kind == "quote":
            q = D.QUOTES.get(val) if isinstance(val, str) else val
            out.append(dict(cap=s["cap"], t=t + 0.5, dur=D.QDUR - 1.0, text=None, quote=repr(q)))
            t += D.QDUR
        else:
            d = sum(max(1.7, len(ch.split()) / D.WPS + 0.35) for ch in D.chunks(val)) + 0.7
            out.append(dict(cap=s["cap"], t=t, dur=d - 0.7, text=val))
            t += d
    # duración de la escena: igual que timeline()
    c["t"] = t
Path(__file__).resolve().parents[2].joinpath("voice_ai/lineas.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(len(out), "líneas;", sum(1 for o in out if o["text"]), "de narración;", sum(len(o["text"].split()) for o in out if o["text"]), "palabras")
