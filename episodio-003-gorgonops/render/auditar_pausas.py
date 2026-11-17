#!/usr/bin/env python3
"""Audita que nunca haya una pausa larga sin que se diga o pase algo.

1) Huecos entre voces (línea de tiempo): máximo permitido GAP_MAX segundos, salvo las secuencias con acción gráfica propia (apertura y créditos).
2) Silencios reales en la mezcla final (ffmpeg silencedetect, -45 dB, >= 1,2 s).
Sale con código 1 si hay fallas.
"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import documental as D

GAP_MAX = 1.6
EXENTAS = {"0 · Apertura"}          # gráficos con acción (diseño Sombra) y créditos
D.world.load(); D.engine.setup()
tl = D.timeline(D.build())
fallas = 0
for cap in sorted(tl):
    c = tl[cap]
    ev = sorted([(t, t + d) for t, d, _ in c["voz"]])
    esc = {n: (t0, t0 + d) for n, t0, d in c["scenes"]}
    prev = 0.0
    for a, b in ev + [(c["t"], c["t"])]:
        gap = a - prev
        if gap > GAP_MAX:
            nom = next((n for n, (x, y) in esc.items() if x <= prev + 0.01 < y), "?")
            if nom not in EXENTAS and not (cap == 7 and prev > c["t"] - 20):
                print(f"FALLA cap{cap} {nom}: hueco sin voz de {gap:.1f} s en t={prev:.1f}")
                fallas += 1
        prev = max(prev, b)
    wav = Path(__file__).resolve().parents[1] / "video" / "audio" / f"{D.CHAPTERS[cap]}.wav"
    if wav.exists():
        r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(wav), "-af", "silencedetect=n=-45dB:d=1.2", "-f", "null", "-"], capture_output=True, text=True).stderr
        n = r.count("silence_end")
        if n:
            print(f"FALLA cap{cap}: {n} silencios de audio >= 1,2 s")
            fallas += n
print("pausas largas:", fallas)
sys.exit(1 if fallas else 0)
