#!/usr/bin/env python3
"""Ajusta cada plano ya renderizado (video/segmentos) a la duración que le corresponde en la línea de tiempo actual
(la que dicta la voz), con mezcla de cuadros (sin volver a renderizar). Salida: video/segmentos_r/ (reanudable).
Uso: python3 retimear.py [--jobs 2]"""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import documental as D

os.environ.pop("SEG_DIR", None)
VIDEO = D.VIDEO
SRC, DST = VIDEO / "segmentos", VIDEO / "segmentos_r"
DST.mkdir(exist_ok=True)
jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 2


def frames(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", str(f)],
                       capture_output=True, text=True).stdout.strip()
    return int(r)


def tarea(a):
    cap, j, nf_new = a
    src, dst = SRC / f"c{cap:02d}_s{j:03d}.mp4", DST / f"c{cap:02d}_s{j:03d}.mp4"
    if dst.exists():
        return a, 1.0, "ya estaba"
    nf_old = frames(src)
    r = nf_new / nf_old
    tmp = dst.with_suffix(".part.mp4")
    if nf_new == nf_old:
        subprocess.run(["cp", str(src), str(tmp)], check=True)
    else:
        vf = f"setpts=PTS*{r:.6f},framerate=fps=24,tpad=stop_mode=clone:stop=6,trim=end_frame={nf_new},setpts=N/24/TB"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vf", vf, "-r", "24", "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "16",
                        "-threads", "2", "-pix_fmt", "yuv420p", str(tmp)], check=True)
    tmp.rename(dst)
    src.unlink()                                    # el plano viejo ya no sirve (ahorra disco)
    return a, r, "ok"


def main():
    D.world.load(); D.engine.setup()
    tl = D.timeline(D.build())
    todo = []
    for cap in sorted(tl):
        for j, (ts, d, sh, nm) in enumerate(tl[cap]["shots"]):
            todo.append((cap, j, int(round(d * D.FPS))))
    print(len(todo), "planos", flush=True)
    rs = []
    with ThreadPoolExecutor(jobs) as ex:
        for i, (a, r, est) in enumerate(ex.map(tarea, todo)):
            rs.append(r)
            if (i + 1) % 10 == 0:
                print(f"{i + 1}/{len(todo)} · factor medio {sum(rs) / len(rs):.3f}", flush=True)
    import numpy as np
    rs = np.array(rs)
    print(f"factores de reajuste: min {rs.min():.3f} · mediana {np.median(rs):.3f} · máx {rs.max():.3f} · fuera de ±10 %: {(abs(rs - 1) > 0.10).sum()}", flush=True)
    print("== RETIMEO TERMINADO", flush=True)


if __name__ == "__main__":
    main()
