#!/usr/bin/env python3
"""Animación de INICIO de la mascota (≈22 s, loop): sentada/quieta mirando lo que ocurre, respira, parpadea, mira alrededor,
huele el suelo (cabeceo + resoplidos), ladea el cuerpo con curiosidad y da un pasito. 1920x1080, 24 fps.
Sale en MP4 (con escenario) y en WebM con transparencia (solo la mascota y su sombra) para superponer en el editor.

  python3 anim_inicio.py SALIDA.mp4 [--alpha]
"""
import math
import subprocess
import sys
import wave
from functools import partial
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gag_suscripcion as G

W, H, FPS = G.W, G.H, G.FPS
DUR = 22.0
X0 = 1180.0
BLINKS = (2.5, 6.8, 11.2, 15.0, 19.5)
SNIFF = ((8.0, 10.6), (16.6, 18.6))


def estado(t):
    s = dict(x=X0, dy=0.0, pose={}, flipx=False)
    resp = 1 + 0.012 * math.sin(2 * math.pi * t / 3.2)
    p = dict(squash=resp, tilt=-1.5 + 0.6 * math.sin(2 * math.pi * t / 3.2), look=(-0.9, 0.2), auto=True)
    # mira alrededor: izquierda (la acción), arriba, derecha un instante, de vuelta
    if 5.0 <= t < 7.0:
        p["look"] = (-0.4, -1.0)
    elif 12.0 <= t < 13.0:
        p["look"] = (0.6, 0.1)
    elif 13.0 <= t < 15.5:                                      # ladea el cuerpo con curiosidad
        k = math.sin(math.pi * min(1, (t - 13.0) / 2.5))
        p["tilt"] += -5.0 * k
        p["look"] = (-0.2, -0.3)
    for (a, b) in SNIFF:                                        # huele el suelo: cabeceo hacia adelante + resoplidos rápidos
        if a <= t < b:
            k = math.sin(math.pi * (t - a) / (b - a))
            pulso = 1 if int((t - a) * 7) % 2 == 0 else 0
            p["tilt"] += 6.5 * k + 1.2 * pulso * k
            p["bob"] = 10 * k + 3 * pulso * k
            p["look"] = (-0.8, 0.9)
    if 10.6 <= t < 12.0:                                        # da un pasito hacia adelante
        k = (t - 10.6) / 1.4
        p["leg"] = (k * 0.9) % 1.0
        s["x"] = X0 - 55 * math.sin(math.pi * min(1, k) / 2)
    elif t >= 12.0:
        s["x"] = X0 - 55 * (1 - 0.0) if t < 20.5 else X0 - 55 * (1 - (t - 20.5) / 1.5)
    for tb in BLINKS:
        if 0 <= t - tb < 0.2:
            p["blink"] = math.sin(math.pi * (t - tb) / 0.2)
    s["pose"] = p
    return s


def frame(i, transparente=False):
    t = i / FPS
    s = estado(t)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)) if transparente else G._BG.copy()
    spr = G._sprite(G._key(s["pose"]), False)
    ox, oy = s["x"] - spr.width / 2, G.GROUND + s["dy"] - G.FOOT_CANVAS_Y * G.SC
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([s["x"] - 470, G.GROUND - 34, s["x"] + 470, G.GROUND + 40], fill=(0, 0, 0, 120))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    img.alpha_composite(spr, (int(ox), int(oy)))
    return img.tobytes() if transparente else np.asarray(img.convert("RGB")).tobytes()


def audio():
    SR = G.SR
    n = int(DUR * SR)
    y = np.zeros(n, np.float32)
    rng = np.random.RandomState(11)

    def add(t0, x, g=1.0):
        i = int(t0 * SR); j = min(n, i + len(x))
        if 0 <= i < n:
            y[i:j] += (x[:j - i] * g).astype(np.float32)
    for k in np.arange(0.6, DUR - 1, 3.2):                      # respiración: roce de páginas suave
        m = int(SR * 1.2)
        add(k, G._bp(rng.randn(m), 3200, 0.7) * np.sin(np.pi * np.arange(m) / m) ** 2 * 0.045)
    for (a, b) in SNIFF:                                        # resoplidos al oler
        for q in np.arange(a, b, 1 / 7):
            m = int(SR * 0.09)
            add(q, G._bp(rng.randn(m), 2400, 1.0) * G._env(m, 0.004, 0.03) * 0.28)
    for tb in BLINKS:                                           # parpadeo: tic de papel
        add(tb, G._bp(rng.randn(int(SR * 0.05)), 5200, 1.4) * G._env(int(SR * 0.05), 0.001, 0.01) * 0.16)
    for q in np.arange(10.6, 12.0, CICLO_P := 0.35):            # pasito
        add(q, G._bp(rng.randn(int(SR * 0.25)), 150, 1.0) * G._env(int(SR * 0.25), 0.004, 0.05) * 0.9)
        add(q, G._bp(rng.randn(int(SR * 0.1)), 2600, 1.2) * G._env(int(SR * 0.1), 0.003, 0.03) * 0.25)
    add(13.2, G._bp(rng.randn(int(SR * 0.4)), 3000, 0.8) * np.sin(np.pi * np.arange(int(SR * 0.4)) / int(SR * 0.4)) ** 2 * 0.12)   # ladea: crujido
    y += G._lp(rng.randn(n), 120, 1).astype(np.float32) * 0.012
    st = G._reverb(y, 0.2)
    st = np.tanh(st * 1.3)
    st = st / max(1e-6, np.abs(st).max()) * 0.8
    return (st * 32767).astype(np.int16)


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "inicio.mp4")
    alpha = "--alpha" in sys.argv
    n = int(DUR * FPS)
    wav = out.with_suffix(".wav")
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(G.SR); w.writeframes(audio().tobytes())
    if alpha:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(wav),
               "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "24", "-auto-alt-ref", "0", "-c:a", "libopus", "-b:a", "160k", str(out)]
    else:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(wav),
               "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(4, initializer=G._init) as pool:
        for k, b in enumerate(pool.imap(partial(frame, transparente=alpha), range(n), chunksize=2)):
            ff.stdin.write(b)
            if k % 48 == 0:
                print("cuadro", k, "/", n, flush=True)
    ff.stdin.close(); ff.wait()
    wav.unlink(missing_ok=True)
    print("listo", out)


if __name__ == "__main__":
    main()
