#!/usr/bin/env python3
"""Anima los fotogramas elegidos en 2.5D y arma el video con el audio.

    voice_ai/.venv/bin/python episodio-004-tuco-tuco/animar.py [--muestra SEGUNDOS] [--sin-subtitulos]

Entrada: frames/elegidas/<id>.png, audio/escenas.json, audio/episodio-004-final.mp3 y audio/episodio-004-voz.srt.
Salida: episodio-004.mp4 (720x1280, 25 fps).

Técnica por toma (sin modelos 3D):
- profundidad estimada con Depth-Anything-V2-Small (se guarda en frames/profundidad/<id>.npy);
- cámara: zoom y desplazamiento con parallax (lo cercano se mueve más que lo lejano);
- viento en el pasto del primer plano, respiración del animal y partículas de polvo con luz;
- fundido corto entre tomas y viñeta suave.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import tomas  # noqa: E402

W, H, FPS = 720, 1280, 25
FUNDIDO = 6  # cuadros de fundido entre tomas
DEPTH_MODEL = AQUI.parent / "voice_ai" / "models" / "depth-anything-v2-small"


def cargar_profundidad(id_, img):
    ruta = AQUI / "frames" / "profundidad" / f"{id_}.npy"
    if ruta.exists():
        return np.load(ruta)
    from PIL import Image
    from transformers import pipeline

    ruta.parent.mkdir(parents=True, exist_ok=True)
    pipe = pipeline("depth-estimation", model=str(DEPTH_MODEL), device=-1)
    d = np.array(pipe(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))["depth"], dtype=np.float32)
    d = cv2.resize(d, (W, H), interpolation=cv2.INTER_CUBIC)
    lo, hi = np.percentile(d, 1), np.percentile(d, 99)
    d = np.clip((d - lo) / max(1e-6, hi - lo), 0, 1)  # 1 = cerca
    d = cv2.GaussianBlur(d, (0, 0), 3)  # evita bordes duros al desplazar
    np.save(ruta, d)
    return d


class Toma:
    def __init__(self, t, inicio, fin):
        self.t, self.inicio, self.fin = t, inicio, fin
        bgr = cv2.imread(str(AQUI / "frames" / "elegidas" / f"{t['id']}.png"))
        self.img = cv2.resize(bgr, (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32)
        self.depth = cargar_profundidad(t["id"], self.img.astype(np.uint8))
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        self.xx, self.yy = xx, yy
        cx, cy = t["centro"][0] * W, t["centro"][1] * H
        self.cx, self.cy = cx, cy
        # máscara gaussiana alrededor del pecho del animal, para la respiración
        self.masc_resp = np.exp(-(((xx - cx) / (0.22 * W)) ** 2 + ((yy - cy) / (0.16 * H)) ** 2))
        # el viento afecta la franja inferior (primer plano de pasto)
        s = np.clip((yy / H - 0.55) / 0.3, 0, 1)
        self.masc_viento = s * s * (3 - 2 * s) * (0.35 + 0.65 * self.depth)
        rng = np.random.default_rng(abs(hash(t["id"])) % 2**32)
        n = int(60 * t["polvo"]) + 6
        self.p = dict(x=rng.uniform(0, W, n), y=rng.uniform(0, H, n), z=rng.uniform(0.2, 1.0, n),
                      fase=rng.uniform(0, 6.28, n))
        self.vign = self._viñeta()

    @staticmethod
    def _viñeta():
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        return (1 - 0.28 * np.clip(r - 0.55, 0, 1) ** 1.5)[..., None]

    def camara(self, u):
        """u en [0,1]: zoom y desplazamiento horizontal/vertical (en píxeles) de la cámara."""
        m = self.t["move"]
        e = u * u * (3 - 2 * u)
        z, dx, dy = 1.10, 0.0, 0.0
        if m == "push_in":
            z = 1.06 + 0.16 * e
        elif m == "pull_out":
            z = 1.22 - 0.16 * e
        elif m == "pan_left":
            z, dx = 1.12, 26 * (0.5 - e)
        elif m == "pan_right":
            z, dx = 1.12, 26 * (e - 0.5)
        elif m == "tilt_down":
            z, dy = 1.12, 30 * (0.5 - e)
        elif m == "tilt_up":
            z, dy = 1.12, 30 * (e - 0.5)
        else:  # breath: casi quieta, leve deriva
            z, dx = 1.08 + 0.02 * e, 6 * np.sin(u * 3.0)
        return z, dx, dy

    def cuadro(self, tseg):
        dur = max(1e-3, self.fin - self.inicio)
        u = float(np.clip((tseg - self.inicio) / dur, 0, 1))
        z, dx, dy = self.camara(u)
        t = tseg
        d = self.depth
        # parallax: lo cercano se desplaza más que lo lejano
        px = dx * (d - 0.35) * 2.6
        py = dy * (d - 0.35) * 2.6
        mx = (self.xx - W / 2) / z + W / 2 + px
        my = (self.yy - H / 2) / z + H / 2 + py
        # viento en el pasto del primer plano
        mx += self.masc_viento * (2.8 * np.sin(1.3 * t + self.xx * 0.018 + self.yy * 0.006)
                                  + 1.2 * np.sin(2.9 * t + self.xx * 0.041))
        # respiración del animal: leve expansión radial del pecho
        resp = 0.007 * np.sin(2 * np.pi * t / 3.1)
        mx += (self.xx - self.cx) * resp * self.masc_resp
        my += (self.yy - self.cy) * resp * self.masc_resp
        out = cv2.remap(self.img, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR,
                        borderMode=cv2.BORDER_REFLECT)
        # partículas de polvo con luz (más grandes y rápidas las cercanas)
        p = self.p
        capa = np.zeros((H, W, 3), np.float32)
        px_ = (p["x"] + (12 + 30 * p["z"]) * t + 14 * np.sin(0.8 * t + p["fase"])) % W
        py_ = (p["y"] - (6 + 14 * p["z"]) * t + 8 * np.sin(0.6 * t + 2 * p["fase"])) % H
        for x, y, zz in zip(px_, py_, p["z"]):
            cv2.circle(capa, (int(x), int(y)), int(1 + 3.2 * zz), (0.55 * zz, 0.8 * zz, 1.0 * zz), -1, cv2.LINE_AA)
        capa = cv2.GaussianBlur(capa, (0, 0), 1.6)
        out = out + 70 * capa
        out = out * self.vign
        return np.clip(out, 0, 255).astype(np.uint8)


def armar_tomas(escenas, total):
    tiempos = {e["escena"]: (0.0 if i == 0 else e["inicio"],
                             escenas[i + 1]["inicio"] if i + 1 < len(escenas) else total)
               for i, e in enumerate(escenas)}
    tomas_ = []
    for n, (a, b) in tiempos.items():
        grupo = [t for t in tomas.TOMAS if t["escena"] == n]
        suma = sum(t["peso"] for t in grupo)
        cur = a
        for t in grupo:
            fin = cur + (b - a) * t["peso"] / suma
            tomas_.append((t, cur, fin))
            cur = fin
    return tomas_


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--muestra", type=float, default=0, help="renderiza solo los primeros N segundos")
    ap.add_argument("--sin-subtitulos", action="store_true")
    args = ap.parse_args()

    audio = AQUI / "audio" / "episodio-004-final.mp3"
    escenas = json.loads((AQUI / "audio" / "escenas.json").read_text())
    total = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(audio)],
        capture_output=True, text=True, check=True).stdout)
    lista = [(Toma(t, a, b), a, b) for t, a, b in armar_tomas(escenas, total)]
    dur = args.muestra or total
    nframes = int(dur * FPS)

    sin_sub = AQUI / "frames" / "sin-subtitulos.mp4"
    ff = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-i", str(audio), "-t", f"{dur:.3f}", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", str(sin_sub)],
        stdin=subprocess.PIPE)
    idx = 0
    for f in range(nframes):
        t = f / FPS
        while idx + 1 < len(lista) and t >= lista[idx][2]:
            idx += 1
        toma, a, b = lista[idx]
        fr = toma.cuadro(t)
        if idx > 0 and t - a < FUNDIDO / FPS:  # fundido con el final de la toma anterior
            al = (t - a) * FPS / FUNDIDO
            prev = lista[idx - 1][0].cuadro(t)
            fr = cv2.addWeighted(prev, 1 - al, fr, al, 0)
        ff.stdin.write(fr.tobytes())
        if f % 250 == 0:
            print(f"{f}/{nframes}", flush=True)
    ff.stdin.close()
    ff.wait()

    destino = AQUI / ("muestra.mp4" if args.muestra else "episodio-004.mp4")
    if args.sin_subtitulos:
        sin_sub.replace(destino)
    else:
        estilo = ("FontName=Inter,FontSize=9,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00302020,"
                  "BorderStyle=1,Outline=2,Alignment=2,MarginV=30")
        srt = str(AQUI / "audio" / "episodio-004-voz.srt").replace(":", r"\:")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(sin_sub), "-vf",
                        f"subtitles='{srt}':force_style='{estilo}'", "-c:v", "libx264", "-crf", "18",
                        "-c:a", "copy", str(destino)], check=True)
    print("Listo:", destino)


if __name__ == "__main__":
    main()
