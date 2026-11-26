#!/usr/bin/env python3
"""Renderiza salida/short-N.mp4 (1080x1920, 30 fps, sin audio). Uso: python3 render.py [N ...]"""
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

import animar
from motor import cronograma

FPS = 30
AQUI = Path(__file__).resolve().parent


def _frame(args):
    n, i = args
    return animar.fotograma(n, i / FPS).tobytes()


def render(n, pool):
    total = int(cronograma(n)["total"] * FPS)
    destino = AQUI / "salida" / f"short-{n}.mp4"
    destino.parent.mkdir(exist_ok=True)
    ff = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", str(FPS),
         "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "medium",
         "-movflags", "+faststart", str(destino)],
        stdin=subprocess.PIPE)
    for fr in pool.imap(_frame, [(n, i) for i in range(total)], chunksize=3):
        ff.stdin.write(fr)
    ff.stdin.close()
    ff.wait()
    print(f"short-{n}.mp4: {total / FPS:.1f} s", flush=True)


if __name__ == "__main__":
    numeros = [int(a) for a in sys.argv[1:]] or [1, 2, 3, 4, 5]
    with Pool() as pool:
        for n in numeros:
            render(n, pool)
