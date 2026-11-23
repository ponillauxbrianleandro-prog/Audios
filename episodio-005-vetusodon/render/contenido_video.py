#!/usr/bin/env python3
"""Escribe video/contenido.txt: capítulos y tiempos del documental completo (para comprobar que está entero)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import world, episodio as E
world.load()
TL, total = E.timeline()
m = lambda t: f"{int(t // 60)}:{t % 60:04.1f}"
filas = ["DOCUMENTAL COMPLETO · VETUSODON — EL GRANDE", f"Duración total: {m(total)} ({total:.1f} s) · {len(TL)} escenas", ""]
for c in TL:
    tx = c["lineas"][0][2] if c.get("lineas") else ""
    filas.append(f"{m(c['t0'])} – {m(c['t0'] + c['dur'])}  escena {c['esc']:02d}  {tx[:70]}")
(Path(__file__).resolve().parents[1] / "video" / "contenido.txt").write_text("\n".join(filas), encoding="utf-8")
print("\n".join(filas))
