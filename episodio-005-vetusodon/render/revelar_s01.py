#!/usr/bin/env python3
"""Revelado de la apertura: a las primeras ~2,2 s del plano 0 de la escena 1 se les aplica el panel oscuro que se abre y aclara.
Toma el plano ya renderizado (copia de seguridad en video/v9-final/segmentos_v9/) y solo modifica esos fotogramas; el resto se copia."""
import subprocess, sys, shutil
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import calles

V = Path(__file__).resolve().parents[1] / "video"
SEG = V / "segmentos" / "s01_00.mp4"
BAK = V / "v9-final" / "segmentos_v9"
W, H, FPS = 1920, 1080, 24


def main():
    BAK.mkdir(parents=True, exist_ok=True)
    src = BAK / "s01_00.mp4"
    if not src.exists():
        shutil.copy2(SEG, src)                                    # copia de seguridad del plano de la v9
    tmp = SEG.with_suffix(".rev.mp4")
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(src), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-pix_fmt", "yuv420p", str(tmp)], stdin=subprocess.PIPE)
    i, fsz = 0, W * H * 3
    while True:
        buf = dec.stdout.read(fsz)
        if len(buf) < fsz:
            break
        t = i / FPS
        if t < 2.3:
            img = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32) / 255.0
            img = calles.revelado(img, t, 2.2)
            buf = (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes()
        enc.stdin.write(buf)
        i += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    tmp.replace(SEG)
    print("revelado listo:", i, "fotogramas")

if __name__ == "__main__":
    main()
