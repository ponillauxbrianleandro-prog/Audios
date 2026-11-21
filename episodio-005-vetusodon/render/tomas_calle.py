#!/usr/bin/env python3
"""Fotos para el montaje de apertura: un fotograma por plano ya renderizado (sin volver a usar el motor). Cache en $GORGO_CACHE/tomas_calle."""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np, cv2
import world, episodio as E

def main():
    world.load()
    TL, _ = E.timeline()
    d = Path(world.CACHE) / "tomas_calle"; d.mkdir(exist_ok=True)
    n = 0
    for c in TL:
        if c["esc"] in (0, 5, 15):
            continue
        for j, (ts, dd, sh) in enumerate(c["shots"]):
            p = E.seg_path(c, j)
            if not p.exists() or dd < 2.0:
                continue
            off = 1.4 if c["esc"] not in (3, 7) else dd * 0.7
            t_esc = ts + off
            if any(tc <= t_esc < tc + dur + 0.3 for tc, _k, dur in c.get("cards", [])):
                continue
            out = d / f"c{c['esc']:02d}_{j}.png"
            if not out.exists():
                subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{off:.2f}", "-i", str(p), "-frames:v", "1", "-vf", "scale=960:540", str(out)], check=True)
            n += 1
    print(n, "fotos en", d)

if __name__ == "__main__":
    main()
