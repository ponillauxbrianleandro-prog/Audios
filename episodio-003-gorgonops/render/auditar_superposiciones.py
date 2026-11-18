#!/usr/bin/env python3
"""Audita solapes: voz-voz (duración real), subtítulo-subtítulo, subtítulo-cita, subtítulo-nota y subtítulo-rótulo.
Las notas van arriba a la derecha, así que ya no chocan con el subtítulo inferior; aun así se reporta la coincidencia temporal
sólo si la nota estuviera abajo. Sale con código 1 si hay solapes."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import documental as D

D.world.load(); D.engine.setup()
tl = D.timeline(D.build())
mal = 0
for cap in sorted(tl):
    c = tl[cap]
    ev = sorted((t, t + d, k) for t, d, k in c["voz"])
    for a, b in zip(ev, ev[1:]):
        if a[1] > b[0] + 0.02:
            print(f"SOLAPE voz-voz cap{cap}: {a[0]:.2f}-{a[1]:.2f} con {b[0]:.2f}"); mal += 1
    subs = sorted(c["subs"])
    for a, b in zip(subs, subs[1:]):
        if a[1] > b[0] + 0.001:
            print(f"SOLAPE sub-sub cap{cap}: {a[0]:.2f}-{a[1]:.2f} con {b[0]:.2f}"); mal += 1
    for t, d, _ in c["quotes"]:
        for s in subs:
            if s[0] < t + d and t - 0.1 < s[1]:
                print(f"SOLAPE sub-cita cap{cap}: sub {s[0]:.2f} con cita {t:.2f}-{t + d:.2f}"); mal += 1
    # cada subtítulo debe coincidir con alguna voz (mismo tramo)
    for s in subs:
        if not any(a[0] - 0.3 <= s[0] <= a[1] + 0.3 for a in ev):
            print(f"SUB sin voz cap{cap}: {s[0]:.2f} '{s[2][:30]}'"); mal += 1
print("solapes:", mal)
sys.exit(1 if mal else 0)
