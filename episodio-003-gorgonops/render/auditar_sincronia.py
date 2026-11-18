#!/usr/bin/env python3
"""Audita que el video ensamblado dure lo mismo que la línea de tiempo (voz y subtítulos): por plano y por capítulo."""
import os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import documental as D

D.world.load(); D.engine.setup()
tl = D.timeline(D.build())
mal = 0
for cap in sorted(tl):
    c = tl[cap]
    tot = 0.0
    for j, (ts, d, sh, nm) in enumerate(c["shots"]):
        f = D.seg_path(cap, j)
        n = int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", str(f)],
                               capture_output=True, text=True).stdout.strip())
        tot += n / D.FPS
        if abs(n - round(d * D.FPS)) > 6:
            print(f"DESFASE cap{cap} plano {j}: video {n} cuadros, línea de tiempo {round(d * D.FPS)}"); mal += 1
    print(f"cap{cap}: video {tot:.2f} s · línea de tiempo {c['t']:.2f} s · diferencia {tot - c['t']:+.2f} s")
    if abs(tot - c["t"]) > 0.25:
        mal += 1
print("desfases:", mal)
sys.exit(1 if mal else 0)
