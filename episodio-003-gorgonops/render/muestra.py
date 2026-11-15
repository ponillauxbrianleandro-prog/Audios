#!/usr/bin/env python3
"""Muestra de 30 s del documental (1920x1080, 24 fps, sin audio, subtítulos incrustados).

Uso:
  python3 muestra.py                      -> ../muestra/muestra-30s.mp4 y .srt
  python3 muestra.py --still 2.0 12.5     -> fotogramas sueltos (PNG) para revisar
  python3 muestra.py --scale 0.5          -> render rápido a media resolución
Requiere: numpy, scipy, opencv-python-headless, pillow y ffmpeg.
"""
import argparse
import os
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
import world
import engine
import creature

FPS = 24
DUR = 30.0
AQUI = Path(__file__).resolve().parent
SALIDA = AQUI.parent / "muestra"

SUBS = [
    (0.9, 4.3, "Hace doscientos cincuenta y cinco millones de años,\neste valle no tenía nombre."),
    (4.7, 7.8, "No había flores. No había hierba.\nNingún ave cruzaba el cielo."),
    (8.7, 12.4, "Y sin embargo, alguien caminaba por aquí cada mañana."),
    (12.9, 16.7, "Gorgonops. Un animal ocupado, sobre todo,\nen encontrar algo que comer."),
    (17.7, 20.4, "No es un reptil. Tampoco es un mamífero."),
    (20.8, 23.6, "Es algo que el mundo todavía no sabe nombrar."),
    (24.8, 29.3, "Pero en este paisaje hay otro habitante.\nY casi nadie lo ha visto todavía."),
]

G = creature.GORGONOPS
P = creature.PROCYNOSUCHUS


def unit(x, z):
    v = np.array([x, z], float)
    return v / np.linalg.norm(v)


def shake(t, amp):
    return (amp * (np.sin(t * 0.83) + 0.6 * np.sin(t * 1.9 + 1.3) + 0.3 * np.sin(t * 3.7 + 0.4)),
            amp * (np.sin(t * 0.71 + 2.0) + 0.6 * np.sin(t * 2.3 + 0.2) + 0.3 * np.sin(t * 4.1)))


def aim(W, H, f, pos, target, vfrac, ufrac=0.5):
    """Cámara que apunta a 'target' dejándolo en (ufrac, vfrac) del cuadro."""
    dx, dz = target[0] - pos[0], target[2] - pos[2]
    yaw = np.arctan2(dx, dz) + np.arctan((0.5 - ufrac) * W / f)
    zc = np.hypot(dx, dz)
    vh = vfrac * H - f * (pos[1] - target[1]) / zc
    return yaw, np.arctan((H / 2 - vh) / f)


# ------------------------------------------------------------------ plano 1: el valle
def cam1(t, W, H):
    k = W / 1920
    sy, sp = shake(t, 0.0009)
    return world.Camera(W, H, 1450 * k, (-7 + 0.22 * t, 1.35, -1 + 0.30 * t), 0.10 + sy, 0.012 + sp)


# ------------------------------------------------------------------ plano 2: camina
B_DIR = unit(-0.96, -0.28)
B_P0 = np.array([-2.0, 0.0, 8.6])
B_CAM = (-10.0, 1.0, -3.2)


def b_pos(t):
    d = G["speed"] * t
    return B_P0 + np.array([B_DIR[0] * d, 0, B_DIR[1] * d])


def cam2(t, W, H):
    k = W / 1920
    f = 5000 * k
    tgt = b_pos(t * 0.93 + 0.2) + np.array([0, 0.36, 0])
    yaw, pitch = aim(W, H, f, B_CAM, tgt, 0.58, 0.47)
    sy, sp = shake(t + 5, 0.0004)
    return world.Camera(W, H, f, B_CAM, yaw + sy, pitch + sp)


def animals2(t):
    return [dict(spec=G, pos=b_pos(t), heading=np.arctan2(B_DIR[1], B_DIR[0]),
                 pose=dict(phase=t / G["period"] + 0.15, walk=1.0, t=t, head_yaw=0.10 * np.sin(t * 0.7),
                           head_pitch=0.10 + 0.05 * np.sin(t * 1.1), head_dy=-0.03), ss=1.7)]


# ------------------------------------------------------------------ plano 3: bebe
C_FWD = unit(-0.72, 0.69)
C_CAM = (-24.5, 0.62, 8.7)
C_POS = None


def c_setup():
    global C_POS
    x = -14.0
    zs = np.linspace(6, 16, 400)
    snout = 0.86
    d = world.river_dist(x + C_FWD[0] * snout + 0 * zs, zs + C_FWD[1] * snout)
    z = zs[np.argmax(d < -0.10)]
    C_POS = np.array([x, 0.0, z])


def c_pose(t):
    e = float(np.clip((t - 0.3) / 1.6, 0, 1))
    e = e * e * (3 - 2 * e)
    up = float(np.clip((t - 5.6) / 1.2, 0, 1))
    up = up * up * (3 - 2 * up)
    d = e * (1 - 0.75 * up)
    lap = (t > 1.9) * (1 - up)
    return dict(phase=0.0, walk=0.0, t=t, drop=0.075 * d, head_dy=-0.165 * d, head_dx=0.02 * d,
                head_pitch=0.05 + 0.60 * d, head_yaw=0.05 + 0.22 * up,
                gape=float(0.05 * lap * (0.5 + 0.5 * np.sin(t * 2 * np.pi * 2.1))), tail_amp=0.8)


def c_snout():
    return C_POS + np.array([C_FWD[0] * 0.93, 0, C_FWD[1] * 0.93])


def cam3(t, W, H):
    k = W / 1920
    f = 4400 * k
    tgt = C_POS + np.array([C_FWD[0] * 0.35, 0.30, C_FWD[1] * 0.35])
    yaw, pitch = aim(W, H, f, C_CAM, tgt, 0.56, 0.54 - 0.004 * t)
    sy, sp = shake(t + 11, 0.00035)
    return world.Camera(W, H, f, C_CAM, yaw + sy, pitch + sp)


def animals3(t):
    return [dict(spec=G, pos=C_POS, heading=np.arctan2(C_FWD[1], C_FWD[0]), pose=c_pose(t), ss=1.7)]


def ripples3(t):
    s = c_snout()
    return [(s[0], s[2], t0, 0.9) for t0 in np.arange(1.9, 5.6, 0.48)]


# ------------------------------------------------------------------ plano 4: el otro habitante
D_CAM = np.array([9.0, 0.40, 1.5])
D_YAW = 0.30
D_RIGHT = np.array([np.cos(D_YAW), 0, -np.sin(D_YAW)])
D_FWDV = np.array([np.sin(D_YAW), 0, np.cos(D_YAW)])
D_DIR = unit(-0.97, -0.10)
D_GP0 = None


def d_setup():
    global D_GP0
    best = None
    for dist in np.arange(30, 60, 1.0):
        for off in np.arange(-6, 6, 1.0):
            p = D_CAM + D_FWDV * dist + D_RIGHT * off
            if all(world.river_dist(p[0] - s, p[2]) > 2.5 for s in (0, 2, 4)):
                best = p
                break
        if best is not None:
            break
    D_GP0 = np.array([best[0], 0.0, best[2]])


def d_cyn(t):
    """Distancia recorrida y cuánto camina: entra, se detiene a olfatear, sigue."""
    v = P["speed"]
    def w(tt):
        return float(np.clip((2.0 - tt) / 0.35, 0, 1) + np.clip((tt - 4.5) / 0.35, 0, 1))
    ts = np.linspace(0, t, max(2, int(t * 60)))
    d = np.trapezoid([w(x) for x in ts], ts) * v if t > 0 else 0.0
    return d, min(1.0, w(t))


def animals4(t):
    d, wk = d_cyn(t)
    start = D_CAM * [1, 0, 1] + D_FWDV * 3.0 + D_RIGHT * 1.0
    pos = start + np.array([D_DIR[0] * d, 0, D_DIR[1] * d])
    sniff = 1 - wk
    cyn = dict(spec=P, pos=pos, heading=np.arctan2(D_DIR[1], D_DIR[0]),
               pose=dict(phase=d / (P["speed"] * P["period"]), walk=wk, t=t,
                         head_dy=0.07 * sniff, head_pitch=-0.28 * sniff + 0.05 * sniff * np.sin(t * 9),
                         head_yaw=0.35 * sniff * np.sin(t * 1.6)), ss=2.0)
    gd = unit(-0.97, -0.24)
    gp = D_CAM * [1, 0, 1] + D_FWDV * 8.4 + D_RIGHT * 2.6 + np.array([gd[0], 0, gd[1]]) * G["speed"] * t
    gor = dict(spec=G, pos=gp, heading=np.arctan2(gd[1], gd[0]),
               pose=dict(phase=t / G["period"], walk=1.0, t=t, head_pitch=0.1), ss=2.0)
    return [gor, cyn]


def cam4(t, W, H):
    k = W / 1920
    sy, sp = shake(t + 20, 0.0008)
    return world.Camera(W, H, 1750 * k, D_CAM + D_FWDV * 0.02 * t, D_YAW + sy - 0.004 * t, 0.045 + sp)


WX = dict(plume=0.30, mist=0.55)
SHOTS = [
    (0.0, 8.0, dict(cam=cam1, animals=lambda t: [], focus=lambda t: 70.0, aperture=0.0012, weather=WX)),
    (8.0, 17.0, dict(cam=cam2, animals=animals2, focus=lambda t: float(np.hypot(*(b_pos(t)[[0, 2]] - np.array(B_CAM)[[0, 2]]))),
                     aperture=0.020, weather=WX)),
    (17.0, 24.0, dict(cam=cam3, animals=animals3, focus=lambda t: float(np.hypot(*(C_POS[[0, 2]] - np.array(C_CAM)[[0, 2]]))),
                      aperture=0.012, weather=WX, ripples=ripples3)),
    (24.0, 30.0, dict(cam=cam4, animals=animals4, focus=lambda t: 3.0, aperture=0.0085,
                      weather=dict(plume=0.85, mist=0.5, plume_az=0.44))),
]


def keepouts():
    ko = [(-5, 1, 2.5), (B_CAM[0], B_CAM[2], 3.0), (C_CAM[0], C_CAM[2], 2.2), (D_CAM[0], D_CAM[2], 2.4)]
    for t in np.linspace(-1, 10, 24):
        p = b_pos(t)
        ko.append((p[0], p[2], 1.3))
        for s in (0.25, 0.5, 0.75):
            ko.append((B_CAM[0] + (p[0] - B_CAM[0]) * s, B_CAM[2] + (p[2] - B_CAM[2]) * s, 1.1))
    for s in np.linspace(0.1, 1.15, 12):
        ko.append((C_CAM[0] + (C_POS[0] - C_CAM[0]) * s, C_CAM[2] + (C_POS[2] - C_CAM[2]) * s, 1.25))
    ko.append((C_POS[0], C_POS[2], 1.8))
    for s in np.linspace(0, 6, 10):
        c = D_CAM + D_FWDV * s
        ko.append((c[0], c[2], 0.9 + 0.12 * s))
    for t in np.linspace(0, 7, 8):
        g = D_CAM + D_FWDV * 8.4 + D_RIGHT * (2.6 - 0.6 * t)
        ko.append((g[0], g[2] - 0.14 * t, 1.5))
    return ko


def init():
    cv2.setNumThreads(1)
    world.load()
    c_setup()
    d_setup()
    engine.setup(keepouts())


def sub_at(t):
    for a, b, txt in SUBS:
        if a <= t <= b:
            return txt, float(min(1, (t - a) / 0.3, (b - t) / 0.3))
    return None, 0


def render_frame(args):
    i, W, H = args
    t = i / FPS
    for a, b, shot in SHOTS:
        if a <= t < b:
            img = engine.frame(shot, t - a, W, H)
            break
    fade = min(1.0, t / 0.7, (DUR - t) / 0.6)
    img8 = (np.clip(img * max(fade, 0), 0, 1) * 255 + 0.5).astype(np.uint8)
    txt, al = sub_at(t)
    return engine.subtitle(img8, txt, al * fade).tobytes()


def write_srt(path):
    def ts(x):
        h, m, s = int(x // 3600), int(x % 3600 // 60), x % 60
        return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"
    with open(path, "w", encoding="utf-8") as fh:
        for n, (a, b, txt) in enumerate(SUBS, 1):
            fh.write(f"{n}\n{ts(a)} --> {ts(b)}\n{txt}\n\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--still", type=float, nargs="*")
    ap.add_argument("--out", default=str(SALIDA / "muestra-30s.mp4"))
    ap.add_argument("--jobs", type=int, default=os.cpu_count())
    a = ap.parse_args()
    W, H = int(1920 * a.scale) // 2 * 2, int(1080 * a.scale) // 2 * 2
    if a.still is not None:
        init()
        for t in a.still:
            buf = render_frame((int(round(t * FPS)), W, H))
            img = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
            p = f"{a.out}.{t:05.2f}.jpg"
            cv2.imwrite(p, img[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 93])
            print(p)
        return
    SALIDA.mkdir(exist_ok=True)
    write_srt(Path(a.out).with_suffix(".srt"))
    n = int(DUR * FPS)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                           "-pix_fmt", "yuv420p", "-movflags", "+faststart", a.out], stdin=subprocess.PIPE)
    with Pool(a.jobs, initializer=init) as pool:
        for i, buf in enumerate(pool.imap(render_frame, [(i, W, H) for i in range(n)], chunksize=2)):
            ff.stdin.write(buf)
            if i % 24 == 0:
                print(f"{i}/{n}", flush=True)
    ff.stdin.close()
    ff.wait()
    print("listo:", a.out)


if __name__ == "__main__":
    main()
