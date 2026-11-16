#!/usr/bin/env python3
"""Muestra 2 (30 s, 1920x1080, 24 fps, sin audio): 15 s de diseño plano «Sombra» con los datos del animal
y 15 s de documental con los biomas nuevos (selva, ribera en capas, nevado, desierto) y más vida.

  python3 muestra2.py                  -> ../muestra/muestra-30s-v2.mp4 y .srt
  python3 muestra2.py --still 5 17 24  -> fotogramas sueltos
  python3 muestra2.py --scale 0.5      -> render rápido
"""
import argparse
import os
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import biomes
import documental as D
import engine
import sombra
import world
from graficos import ease

FPS = 24
DUR = 30.0
T_WIPE = 14.4          # el documental empieza a asomar bajo el rojo
AQUI = Path(__file__).resolve().parent
SALIDA = AQUI.parent / "muestra"

EV = dict(ev_first=1.2)
SUBS = [
    (15.0, 18.2, "Selvas húmedas en el trópico del Pérmico."),
    (18.7, 22.0, "Llanuras y ríos en el sur de Pangea."),
    (22.5, 25.8, "Inviernos fríos, quizá con nieve."),
    (26.3, 29.4, "Y desiertos en el interior del continente."),
]
ROTULOS = ["CATASIA · TRÓPICO", "KAROO · SUDÁFRICA", "KAROO · INVIERNO (hipótesis)", "INTERIOR DE PANGEA"]

_SHOTS = None


def shots():
    global _SHOTS
    if _SHOTS is None:
        mx = D.bank_x(44.0)
        cyn = D.actor(D.PRO, (mx - 3.0, 46.0), np.arctan2(-0.25, -0.97), ss=2.0)
        walk_b = D.actor(D.GOR, (-2.0, 8.6), np.arctan2(-0.28, -0.96))
        walk_n = D.actor(D.GOR, (-2.0, 8.6), np.arctan2(-0.28, -0.96))
        walk_d = D.actor(D.GOR, (-2.0, 8.6), np.arctan2(-0.28, -0.96))
        _SHOTS = [
            D.track("selva", cyn, cam=(2.6, 2.4, 0.30), f=3600, v=0.60, ap=0.02, fg=D.FG_LOW + D.FG_L, through=True, wx=EV),
            D.track("ribera", walk_b, cam=(7.0, 4.5, 0.55), f=3800, v=0.60, ap=0.014, fg=D.FG_REED, through=True, wx=dict(EV, leaves=8)),
            D.track("nevado", walk_n, cam=(9.5, 2.5, 1.0), f=3400, v=0.60, ap=0.010, fg=D.FG_L, pan=0.6, wx=EV),
            D.track("desierto", walk_d, cam=(11.0, 1.5, 1.0), f=4500, u=0.47, wx=dict(EV, dust=1.0)),
        ]
        edges = np.linspace(T_WIPE, DUR, 5)
        for i, s in enumerate(_SHOTS):
            s["t0"], s["t1"] = float(edges[i]), float(edges[i + 1])
            D.finalize(s, s["t1"] - s["t0"])
    return _SHOTS


def init():
    cv2.setNumThreads(1)
    world.load()
    engine.setup()
    sombra.silueta("gorgonops")
    shots()


def doc_frame(t, W, H):
    """Fotograma del documental en el instante t (segundos del video)."""
    for i, s in enumerate(shots()):
        if t < s["t1"] or i == len(shots()) - 1:
            break
    dw, dh = int(W * 2 / 3) // 2 * 2, int(H * 2 / 3) // 2 * 2          # el documental se renderiza a 2/3 y se amplía
    img = engine.frame(s, max(0.0, t - s["t0"]), dw, dh)
    img = np.clip(cv2.resize(img, (W, H), interpolation=cv2.INTER_CUBIC), 0, 1)
    return sombra.rotulo(img, max(0.0, t - s["t0"]), s["t1"] - s["t0"], ROTULOS[i])


def render_frame(args):
    i, W, H = args
    t = i / FPS
    if t < 15.0:
        img = sombra.intro(t, W, H)
        if t >= T_WIPE:                                   # el rojo se retira hacia la izquierda y deja ver el documental
            s = ease((t - T_WIPE) / (15.0 - T_WIPE))
            doc = doc_frame(t, W, H)
            xs = np.arange(W)[None, :, None]
            edge = W * (1.0 - s)
            img = np.where(xs >= edge, doc, img)
            bar = (xs >= edge - 0.012 * W) & (xs < edge)
            img = np.where(bar, np.array(sombra.BLACK, np.float32) / 255.0, img)
    else:
        img = doc_frame(t, W, H)
    fade = min(1.0, (DUR - t) / 0.6)
    out = (np.clip(img * max(fade, 0.0), 0, 1) * 255 + 0.5).astype(np.uint8)
    for a, b, txt in SUBS:
        if a <= t <= b:
            out = engine.subtitle(out, txt, float(min(1, (t - a) / 0.3, (b - t) / 0.3)))
    return out.tobytes()


def write_srt(path):
    def ts(x):
        h, m, s = int(x // 3600), int(x % 3600 // 60), x % 60
        return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)) % 1000:03d}"
    with open(path, "w", encoding="utf-8") as fh:
        for n, (a, b, txt) in enumerate(SUBS, 1):
            fh.write(f"{n}\n{ts(a)} --> {ts(b)}\n{txt}\n\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--still", type=float, nargs="*")
    ap.add_argument("--out", default=str(SALIDA / "muestra-30s-v2.mp4"))
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    W, H = int(1920 * a.scale) // 2 * 2, int(1080 * a.scale) // 2 * 2
    if a.still is not None:
        init()
        for t in a.still:
            buf = render_frame((int(round(t * FPS)), W, H))
            img = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
            p = f"{a.out}.{t:05.2f}.jpg"
            cv2.imwrite(p, img[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 92])
            print(p, flush=True)
        return
    SALIDA.mkdir(exist_ok=True)
    write_srt(Path(a.out).with_suffix(".srt"))
    n = int(DUR * FPS)
    tmp = a.out + ".part.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
                           "-movflags", "+faststart", tmp], stdin=subprocess.PIPE)
    with Pool(a.jobs, initializer=init) as pool:
        for i, buf in enumerate(pool.imap(render_frame, [(i, W, H) for i in range(n)], chunksize=1)):
            ff.stdin.write(buf)
            if i % 24 == 0:
                print(f"{i}/{n}", flush=True)
    ff.stdin.close()
    ff.wait()
    os.replace(tmp, a.out)
    print("listo:", a.out, flush=True)


if __name__ == "__main__":
    main()
