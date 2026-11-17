#!/usr/bin/env python3
"""Vuelca los textos a locutar (narración y citas leídas) a ../../voice_ai/lineas_v2.json, con clave estable por texto."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import documental as D

D.world.load(); D.engine.setup()
SC = D.build()
vistos, out = set(), []
for s in SC:
    for kind, val in s["items"]:
        if kind == "nar":
            txt = val
        elif kind == "quote":
            txt = D.texto_cita(val)
        else:
            continue
        k = D.clave_voz(txt)
        if k in vistos:
            continue
        vistos.add(k)
        out.append(dict(key=k, cap=s["cap"], escena=s["name"], text=txt))
from guion_extra import BRIDGES
for snip, txt in BRIDGES:
    k = D.clave_voz(txt)
    if k not in vistos:
        vistos.add(k)
        out.append(dict(key=k, cap=-1, escena="puente", text=txt))
Path(__file__).resolve().parents[2].joinpath("voice_ai/lineas_v2.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(len(out), "líneas;", sum(len(o["text"].split()) for o in out), "palabras")
