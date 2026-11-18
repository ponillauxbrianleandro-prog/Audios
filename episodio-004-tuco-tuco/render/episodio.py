#!/usr/bin/env python3
"""Episodio 004 (tuco-tuco): tabla de planos, render por multiproceso y montaje.

Se ejecuta con el entorno de voice_ai (numpy, scipy, opencv):
    voice_ai/.venv/bin/python episodio-004-tuco-tuco/render/episodio.py --tiempos
    ... --still s05a [--t 2.0]       un fotograma suelto (frames/still/)
    ... --contacto                   un fotograma por plano, hoja de contactos (frames/contacto.png)
    ... --muestra 6                  los primeros N segundos (muestra.mp4)
    ... --render                     todos los cuadros (reanudable) en frames/render/
    ... --montar                     video final con audio y subtítulos: episodio-004.mp4
"""
import argparse
import json
import os
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parent
os.environ.setdefault("GORGO_CACHE", "/tmp/tuco_cache")
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(EP))

import numpy as np
import cv2
cv2.setNumThreads(1)          # un hilo por proceso: el reparto lo hace el Pool
import world
import engine
import camaras as D
import rodent as R
import tomas

W, H, FPS = 720, 1280, 25
FADE = 6
TUCO, RATA = R.TUCOTUCO, R.RATA
SUN0 = np.array([-0.50, 0.62, -0.42])

# ------------------------------------------------------------------ luz (se mezcla con el wx del bioma)
AMANECER = dict(light=dict(sun=(1.0, 0.78, 0.55), amb=(0.52, 0.54, 0.66), fog=(0.95, 0.78, 0.62)),
                zenith=(0.42, 0.54, 0.80), horizon=(0.98, 0.78, 0.58))
TARDE = dict(light=dict(sun=(1.0, 0.86, 0.62), amb=(0.58, 0.58, 0.66), fog=(0.92, 0.80, 0.66)))
ATARDECER = dict(light=dict(sun=(1.0, 0.66, 0.40), amb=(0.50, 0.46, 0.58), fog=(0.96, 0.66, 0.50)),
                 zenith=(0.34, 0.38, 0.66), horizon=(1.0, 0.60, 0.36))
CUEVA = dict(light=dict(sun=(0.95, 0.62, 0.34), amb=(0.34, 0.28, 0.24), fog=(0.30, 0.22, 0.17)),
             zenith=(0.10, 0.08, 0.08), horizon=(0.42, 0.26, 0.15), mist=0.1)


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


# ------------------------------------------------------------------ poses del roedor (t = segundos del plano)
def p_idle(look=0.22, pitch=0.04, **kw):
    def f(t, d):
        return dict(t=t, head_yaw=look * np.sin(t * 0.5 + 0.4) + 0.05 * np.sin(t * 1.7),
                    head_pitch=pitch + 0.03 * np.sin(t * 0.9), tail_amp=0.8, **kw)
    return f


def p_eat(chew=1.0, **kw):
    def f(t, d):
        return dict(t=t, head_pitch=-0.30 + 0.03 * np.sin(t * 2.0), head_yaw=0.10 * np.sin(t * 0.7), head_dy=-0.03,
                    chew=chew, crouch=0.2, **kw)
    return f


def p_dig(**kw):
    def f(t, d):
        return dict(t=t, dig=1.0, head_pitch=-0.20 + 0.04 * np.sin(t * 5.0), head_dy=-0.02, crouch=0.5, **kw)
    return f


def p_alert(**kw):
    def f(t, d):
        return dict(t=t, head_pitch=0.14, head_yaw=0.55 * np.sin(t * 0.8) + 0.08 * np.sin(t * 2.3), head_dy=0.02, **kw)
    return f


def p_asoma(**kw):
    def f(t, d):
        return dict(t=t, crouch=1.0, head_pitch=0.08 + 0.02 * np.sin(t * 1.1), head_yaw=0.15 * np.sin(t * 0.6), **kw)
    return f


def p_mira(**kw):
    def f(t, d):
        return dict(t=t, head_pitch=0.03, head_yaw=0.05 * np.sin(t * 0.5), **kw)
    return f


def p_boca(gape=0.20, **kw):
    def f(t, d):
        return dict(t=t, head_pitch=0.0, head_yaw=0.12 * np.sin(t * 0.8), gape=gape * (0.6 + 0.4 * np.sin(t * 2.2)), **kw)
    return f


# ------------------------------------------------------------------ fx de cielo
def sky_aves(bg, cam, t):
    h, w = bg.shape[:2]
    for i in range(4):
        x = ((i * 0.31 + 0.1) * w + 38 * t * (0.7 + 0.2 * i)) % (w + 120) - 60
        y = cam.vh * (0.30 + 0.12 * i) + 12 * np.sin(t * 0.8 + i)
        s = 11 + 4 * i
        flap = np.sin(t * 7.0 + i * 1.7)
        pts = np.array([[x - s, y + s * 0.15 * flap - s * 0.3], [x - s * 0.5, y - s * 0.15 * flap], [x, y],
                        [x + s * 0.5, y - s * 0.15 * flap], [x + s, y + s * 0.15 * flap - s * 0.3]], np.float32)
        cv2.polylines(bg, [pts.astype(np.int32).reshape(-1, 1, 2)], False, (0.16, 0.14, 0.15), 2)


def sky_ciudad(bg, cam, t):
    h, w = bg.shape[:2]
    rng = np.random.default_rng(11)
    lay = np.zeros_like(bg)
    x = -10
    while x < w:
        bw = int(rng.integers(40, 110))
        bh = int(rng.integers(60, 230))
        top = int(cam.vh - bh)
        cv2.rectangle(lay, (x, top), (x + bw, int(cam.vh) + 4), (0.10, 0.11, 0.20), -1)
        for wy in range(top + 8, int(cam.vh) - 6, 14):
            for wx_ in range(x + 6, x + bw - 6, 12):
                if rng.random() < 0.28:
                    cv2.rectangle(lay, (wx_, wy), (wx_ + 4, wy + 6), (0.95, 0.78, 0.40), -1)
        x += bw + int(rng.integers(0, 10))
    mask = (lay.sum(-1, keepdims=True) > 0).astype(np.float32)
    bg[:] = bg * (1 - 0.92 * mask) + lay * mask * 0.92
    bok = np.zeros_like(bg)
    for _ in range(26):
        cx, cy = rng.uniform(0, w), cam.vh + rng.uniform(-30, 25)
        col = [(1.0, 0.72, 0.35), (1.0, 0.45, 0.30), (0.95, 0.90, 0.60)][int(rng.integers(0, 3))]
        cv2.circle(bok, (int(cx), int(cy)), int(rng.integers(8, 20)), col, -1)
    bok = cv2.GaussianBlur(bok, (0, 0), 3.0)
    bg[:] = np.minimum(1.5, bg + 0.35 * bok)


# ------------------------------------------------------------------ construcción de planos
def toma(biome, p, tg, f, v=0.55, u=0.5, mv=(0, 0, 0), dtg=(0, 0, 0), actors=(), fg=(), wx=None, zf=None,
         ap=0.0012, sun=None, sky_fx=None):
    p, tg = np.array(p, float), np.array(tg, float)
    mv, dtg = np.array(mv, float), np.array(dtg, float)

    def cam(t, W_, H_):
        pp, tt = p + mv * t, tg + dtg * t
        ff = f * W_ / 1920
        yaw, pitch = D.aim(W_, H_, ff, pp, tt, v, u)
        sy, sp = D.shake(t + p[0], 0.0003)
        return world.Camera(W_, H_, ff, pp, yaw + sy, pitch + sp)
    a0 = actors[0].pos(0.0) if actors else tg
    zfocus = zf if zf is not None else float(np.hypot(*(a0[[0, 2]] - p[[0, 2]])))
    s = dict(biome=biome, cam=cam, animals=lambda t: [a(t) for a in actors], focus=lambda t: zfocus, aperture=ap,
             wx=wx or {}, actors=actors, through=False, sun=sun, sky_fx=sky_fx, fg=[], life_at=a0)
    keep = []
    for t in np.linspace(0, 6, 7):
        c = cam(t, 1280, 720)
        keep.append((c.pos[0], c.pos[2], 0.5))
        for s_ in (0.6, 1.2, 2.0, 3.0):
            keep.append((c.pos[0] + np.sin(c.yaw) * s_, c.pos[2] + np.cos(c.yaw) * s_, 0.35 + 0.05 * s_))
    for a in actors:
        q = a.pos(0.0)
        keep.append((q[0], q[2], 0.45))
        for s_ in (0.3, 0.5, 0.7, 0.85):
            keep.append((p[0] + (q[0] - p[0]) * s_, p[2] + (q[2] - p[2]) * s_, 0.30))
    s["keep"] = keep
    for i, g in enumerate(fg):
        g = dict(g)
        g.setdefault("ph", 1.3 * i)
        g.setdefault("flip", bool(i % 2))
        g.setdefault("y", 0.0)
        g.setdefault("var", i)
        g.setdefault("sc", 1.0)
        s["fg"].append(g)
    return s


def tuco(x, z, ang, pose, spec=TUCO):
    return D.actor(spec, (x, z), ang, speed=0.0, pose=pose, ss=1.6)


def cueva(x, z, sc=1.0, var=0):
    return dict(kind="cueva", x=x, z=z, sc=sc, var=var)


def coiron(x, z, sc=0.8, var=0):
    return dict(kind="coiron", x=x, z=z, sc=sc, var=var)


def build_shots():
    S = {}
    S["s01a"] = toma("calle", (0, 0.14, 0), (0.1, 0.06, 1.1), 5200, v=0.55, mv=(0, 0, 0.05),
                     actors=[tuco(0.1, 1.1, -2.2, p_idle(0.3), RATA)], sky_fx=sky_ciudad)
    S["s01b"] = toma("calle", (0.0, 0.10, 0.0), (0.12, 0.075, 1.0), 6500, mv=(0.02, 0, 0.02),
                     actors=[tuco(0.12, 1.0, -1.9, p_idle(0.15, 0.0), RATA)], sky_fx=sky_ciudad)
    S["s02a"] = toma("estepa", (0, 0.40, -0.4), (0.8, 0.10, 2.6), 2300, v=0.60, mv=(0, 0, 0.30), ap=0.0008,
                     actors=[tuco(0.8, 2.6, -2.3, p_idle())], wx=AMANECER, sky_fx=sky_aves)
    S["s02b"] = toma("estepa", (0, 0.14, 0), (0.15, 0.08, 1.15), 5600, mv=(0.05, 0, 0.03),
                     actors=[tuco(0.15, 1.2, -2.2, p_idle())], fg=[cueva(0.4, 1.4)], wx=AMANECER)
    S["s02c"] = toma("estepa", (0.25, 0.07, 0.25), (-0.1, 0.09, 1.4), 8000, mv=(-0.08, 0, 0), zf=0.6,
                     actors=[tuco(-0.1, 1.5, -1.8, p_idle())], fg=[coiron(0.35, 0.75, 0.8, 3), coiron(-0.2, 0.65, 0.7, 5)],
                     wx=AMANECER)
    S["s03a"] = toma("estepa", (0.1, 0.07, 0.0), (0.12, 0.08, 1.0), 4600, v=0.6, mv=(0, 0, 0.04),
                     actors=[tuco(0.15, 1.0, -2.0, p_eat())], wx=TARDE)
    S["s03b"] = toma("estepa", (0.2, 0.55, 0.20), (0.15, 0.03, 1.05), 4000, mv=(0, -0.03, 0.02),
                     actors=[tuco(0.15, 1.05, -1.4, p_eat())], wx=TARDE)
    S["s03c"] = toma("estepa", (-0.6, 0.25, -0.2), (0.7, 0.08, 2.0), 2600, mv=(0.10, 0, 0.08),
                     actors=[tuco(0.7, 2.2, -2.5, p_eat())], wx=TARDE, sky_fx=sky_aves)
    S["s04a"] = toma("estepa", (-0.1, 0.12, 0.0), (0.05, 0.07, 1.05), 4400, mv=(0.06, 0, 0),
                     actors=[tuco(0.15, 1.05, -0.9, p_idle(0.3, -0.15))], wx=TARDE)
    S["s04b"] = toma("estepa", (0.05, 0.10, 0.2), (0.12, 0.07, 1.0), 6500, mv=(0, 0, 0.04),
                     actors=[tuco(0.12, 1.0, -1.75, p_eat(0.0))], wx=TARDE)
    S["s04c"] = toma("estepa", (0.3, 0.10, 0.3), (0.0, 0.08, 1.4), 6500, zf=0.8, mv=(-0.05, 0, 0),
                     actors=[tuco(0.0, 1.4, -1.9, p_idle())], fg=[coiron(0.2, 0.9, 0.7, 7)], wx=TARDE)
    S["s05a"] = toma("estepa", (0.0, 0.09, 0.05), (0.12, 0.075, 1.0), 6500, mv=(0, 0, 0.03),
                     actors=[tuco(0.12, 1.0, -1.62, p_boca())], wx=TARDE)
    S["s05b"] = toma("estepa", (0.15, 0.50, 0.1), (0.15, 0.03, 1.0), 4000,
                     actors=[tuco(0.15, 1.0, -2.2, p_dig())], wx=TARDE)
    S["s05c"] = toma("estepa", (0.1, 0.05, 0.2), (0.22, 0.05, 1.05), 6000,
                     actors=[tuco(0.2, 1.05, -2.0, p_dig())], wx=TARDE)
    S["s06a"] = toma("estepa", (0, 0.10, 0.2), (0, 0.07, 1.2), 5600, mv=(0, 0, 0.04),
                     actors=[tuco(0.0, 1.2, -1.6, p_asoma())], fg=[cueva(0.0, 1.34, 0.75)], wx=TARDE)
    S["s06b"] = toma("estepa", (0, 0.06, 0.0), (0.0, 0.05, 1.3), 5000, mv=(0, 0, -0.05), zf=1.35,
                     actors=[tuco(0.0, 1.35, -1.6, p_asoma())], fg=[cueva(0.0, 1.50, 0.9)], wx=TARDE)
    S["s07a"] = toma("estepa", (-0.6, 0.25, -0.2), (0.8, 0.1, 2.2), 2700, mv=(0.10, 0, 0.04),
                     actors=[tuco(0.4, 1.7, -2.3, p_idle()), tuco(1.5, 2.3, -1.0, p_idle(0.3)), tuco(-0.5, 2.8, -1.9, p_alert())],
                     fg=[cueva(0.4, 1.85, 0.5), cueva(1.5, 2.45, 0.5), cueva(-0.5, 2.95, 0.5)], wx=TARDE)
    S["s07b"] = toma("estepa", (0, 0.03, 0.3), (0.0, 0.09, 1.5), 3800, mv=(0, 0, 0.03), sun=(-0.3, 0.35, 0.9),
                     actors=[tuco(0.0, 1.3, -1.6, p_idle())], wx=ATARDECER)
    S["s07c"] = toma("estepa", (0.1, 0.12, 0), (0.1, 0.075, 1.1), 5400,
                     actors=[tuco(0.1, 1.1, -2.1, p_alert())], wx=TARDE, sky_fx=sky_aves)
    S["s08a"] = toma("estepa", (0.0, 0.10, 0.0), (0.12, 0.085, 1.0), 9000,
                     actors=[tuco(0.12, 1.0, -1.9, p_idle(0.1))], wx=TARDE)
    S["s08b"] = toma("estepa", (0.1, 0.18, 0.2), (0.1, 0.07, 1.1), 4500, mv=(0, 0.01, -0.06),
                     actors=[tuco(0.1, 1.1, -2.0, p_idle())], fg=[dict(kind="rock", x=0.32, z=1.0, sc=0.12, var=2)], wx=TARDE)
    S["s09a"] = toma("estepa", (0, 0.07, 0.6), (0, 0.06, 1.4), 4000, mv=(0, 0.004, 0), sun=(0.55, 0.38, 0.22),
                     actors=[tuco(0.0, 1.45, -1.6, p_asoma())], wx=CUEVA)
    S["s09b"] = toma("estepa", (0, 0.06, 0.4), (0, 0.06, 1.2), 5500, mv=(0, 0, -0.04), sun=(0.55, 0.38, 0.22),
                     actors=[tuco(0.0, 1.25, -1.6, p_mira())], wx=CUEVA)
    S["s09c"] = toma("calle", (0, 0.14, -0.6), (0.2, 0.05, 3.5), 3300, mv=(0, 0, -0.15),
                     actors=[tuco(0.2, 3.2, 1.57, p_idle(0.1), RATA)], sky_fx=sky_ciudad)
    S["s10a"] = toma("estepa", (0, 0.22, -0.3), (0.3, 0.1, 2.0), 2800, mv=(0, 0.02, -0.05),
                     actors=[tuco(0.3, 2.0, -2.3, p_idle())], wx=ATARDECER, sky_fx=sky_aves)
    S["s10b"] = toma("estepa", (0, 0.10, 0.2), (0.05, 0.08, 1.1), 6000,
                     actors=[tuco(0.05, 1.1, -1.62, p_mira())], wx=ATARDECER)
    return S


# ------------------------------------------------------------------ línea de tiempo
def linea_tiempo():
    escenas = json.loads((EP / "audio" / "escenas.json").read_text())
    total = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
         str(EP / "audio" / "episodio-004-final.mp3")], capture_output=True, text=True, check=True).stdout)
    tiempos = {e["escena"]: (0.0 if i == 0 else e["inicio"], escenas[i + 1]["inicio"] if i + 1 < len(escenas) else total)
               for i, e in enumerate(escenas)}
    out = []
    for n, (a, b) in tiempos.items():
        grupo = [t for t in tomas.TOMAS if t["escena"] == n]
        suma = sum(t["peso"] for t in grupo)
        cur = a
        for t in grupo:
            fin = cur + (b - a) * t["peso"] / suma
            out.append((t["id"], cur, fin))
            cur = fin
    return out, total


_SH = None
_TL = None


def _init():
    global _SH, _TL
    if _SH is None:
        _SH = build_shots()
        _TL = linea_tiempo()[0]
        engine.setup()


def _frame(shot, t, w=W, h=H):
    world.SUN = unit(shot["sun"] if shot.get("sun") is not None else SUN0)
    img = engine.frame(shot, t, w, h)
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)


def frame_global(fi, w=W, h=H):
    _init()
    T = fi / FPS
    idx = next((i for i, (_, a, b) in enumerate(_TL) if a <= T < b), len(_TL) - 1)
    sid, a, b = _TL[idx]
    img = _frame(_SH[sid], T - a, w, h)
    if idx > 0 and T - a < FADE / FPS:
        pid, pa, pb = _TL[idx - 1]
        prev = _frame(_SH[pid], T - pa, w, h)
        al = (T - a) * FPS / FADE
        img = cv2.addWeighted(prev, 1 - al, img, al, 0)
    return img


def _job(fi):
    out = EP / "frames" / "render" / f"{fi:05d}.jpg"
    if out.exists():
        return fi
    img = frame_global(fi)
    cv2.imwrite(str(out), img[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 95])
    return fi


def _job_small(fi):
    return frame_global(fi, 360, 640)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tiempos", action="store_true")
    ap.add_argument("--still")
    ap.add_argument("--t", type=float, default=1.0)
    ap.add_argument("--contacto", action="store_true")
    ap.add_argument("--muestra", type=float, default=0)
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--montar", action="store_true")
    ap.add_argument("--procs", type=int, default=4)
    args = ap.parse_args()
    (EP / "frames" / "render").mkdir(parents=True, exist_ok=True)
    tl, total = linea_tiempo()
    nfr = int(total * FPS)

    if args.tiempos:
        for sid, a, b in tl:
            print(f"{sid}: {a:6.2f}–{b:6.2f}  ({b - a:4.1f} s)")
        print(f"total {total:.1f} s, {nfr} cuadros")
    if args.still:
        _init()
        (EP / "frames" / "still").mkdir(exist_ok=True)
        img = _frame(_SH[args.still], args.t)
        cv2.imwrite(str(EP / "frames" / "still" / f"{args.still}.png"), img[..., ::-1])
    if args.contacto:
        mids = [int((a + b) / 2 * FPS) for _, a, b in tl]
        with Pool(args.procs) as pool:
            imgs = pool.map(_job_small, mids)
        cols = 7
        rows = (len(imgs) + cols - 1) // cols
        sheet = np.full((rows * 640, cols * 360, 3), 255, np.uint8)
        for k, im in enumerate(imgs):
            r, c = divmod(k, cols)
            sheet[r * 640:(r + 1) * 640, c * 360:(c + 1) * 360] = im
            cv2.putText(sheet, tl[k][0], (c * 360 + 8, r * 640 + 26), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.imwrite(str(EP / "frames" / "contacto.png"), sheet[..., ::-1])
    if args.render or args.muestra:
        n = int(args.muestra * FPS) if args.muestra else nfr
        with Pool(args.procs) as pool:
            for k, _ in enumerate(pool.imap(_job, range(n), chunksize=1)):
                if k % 50 == 0:
                    print(f"{k}/{n}", flush=True)
        if args.muestra:
            montar(n, EP / "muestra.mp4", con_subs=False)
    if args.montar:
        montar(nfr, EP / "episodio-004.mp4", con_subs=True)


def montar(n, destino, con_subs=True):
    audio = EP / "audio" / "episodio-004-final.mp3"
    tmp = EP / "frames" / "sin-subtitulos.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(EP / "frames" / "render" / "%05d.jpg"),
                    "-i", str(audio), "-frames:v", str(n), "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", str(tmp)], check=True)
    if not con_subs:
        tmp.replace(destino)
        return
    estilo = ("FontName=Inter,FontSize=9,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00302020,"
              "BorderStyle=1,Outline=2,Alignment=2,MarginV=30")
    srt = str(EP / "audio" / "episodio-004-voz.srt").replace(":", r"\:")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-vf", f"subtitles='{srt}':force_style='{estilo}'",
                    "-c:v", "libx264", "-crf", "17", "-c:a", "copy", str(destino)], check=True)
    print("Listo:", destino)


if __name__ == "__main__":
    main()
