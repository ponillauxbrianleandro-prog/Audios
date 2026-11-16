#!/usr/bin/env python3
"""Mezcla la narración (voice_ai/cache/NNN.wav) con el ambiente + tango de sonido.py.

Salidas (../video/):
  audio_sin_voz/NN-nombre.wav   copia del ambiente+tango original
  audio/NN-nombre.wav           ambiente + tango con ducking + voz (lo que usa documental.py --assemble)
  srt_voz/NN-nombre.srt         subtítulos re-temporizados con la duración real de la voz
Uso: python3 voz.py  (después de sonido.py)
"""
import json, shutil, subprocess, sys, wave
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly, butter, sosfilt, sosfiltfilt

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import documental as D
VIDEO = AQUI.parent / "video"
VOZ = AQUI.parents[1] / "voice_ai"
SR = 48000
LEAD = 0.15


def leer_wav(p):
    with wave.open(str(p)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float32).reshape(-1, w.getnchannels()) / 32768
    return x


def voz_linea(i, ratio_max=1.25, hueco=None):
    sr, x = wavfile.read(str(VOZ / "cache" / f"{i:03d}.wav"))
    x = x.astype(np.float32) / (32768.0 if x.dtype == np.int16 else 1.0)
    if x.ndim > 1:
        x = x.mean(1)
    x = resample_poly(x, SR, sr).astype(np.float32)
    # recorta silencios de los extremos
    e = np.abs(x) > 0.01
    if e.any():
        a, b = np.argmax(e), len(e) - np.argmax(e[::-1])
        x = x[max(0, a - 480):min(len(x), b + 960)]
    d = len(x) / SR
    if hueco and d > hueco:
        r = min(d / hueco, ratio_max)
        tmp_in, tmp_out = VOZ / "cache" / "_in.wav", VOZ / "cache" / "_out.wav"
        wavfile.write(str(tmp_in), SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp_in), "-filter:a", f"atempo={r:.4f}", str(tmp_out)], check=True)
        _, x = wavfile.read(str(tmp_out))
        x = x.astype(np.float32) / 32768.0
    # voz algo más presente: realce suave de claridad y compresión ligera
    sos = butter(2, [2200, 5500], btype="band", fs=SR, output="sos")
    x = x + 0.18 * sosfilt(sos, x)
    pk = np.abs(x).max() + 1e-9
    x = np.tanh(x / pk * 1.6) / np.tanh(1.6) * 0.88
    return x.astype(np.float32)


def ts(x):
    h, m, s = int(x // 3600), int(x % 3600 // 60), x % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)) % 1000:03d}"


def main():
    D.world.load()
    D.engine.setup()
    tl = D.timeline(D.build())
    lines = json.loads((VOZ / "lineas.json").read_text())
    (VIDEO / "audio_sin_voz").mkdir(exist_ok=True)
    (VIDEO / "srt_voz").mkdir(exist_ok=True)
    por_cap = {}
    for i, o in enumerate(lines):
        por_cap.setdefault(o["cap"], []).append((i, o))
    for cap in sorted(tl):
        name = D.CHAPTERS[cap]
        bed_p = VIDEO / "audio" / f"{name}.wav"
        sin = VIDEO / "audio_sin_voz" / f"{name}.wav"
        if not sin.exists():
            shutil.copy(bed_p, sin)
        bed_p.parent.mkdir(exist_ok=True)
        bed = leer_wav(sin)
        n = len(bed)
        voz = np.zeros(n, np.float32)
        subs_old = tl[cap]["subs"]
        nuevos = []
        items = por_cap.get(cap, [])
        for k, (i, o) in enumerate(items):
            sig = items[k + 1][1]["t"] if k + 1 < len(items) else n / SR
            hueco = max(1.5, min(o["dur"] + 0.6, sig - o["t"] - 0.35))
            x = voz_linea(i, hueco=hueco)
            s0 = int((o["t"] + LEAD) * SR)
            e0 = min(n, s0 + len(x))
            voz[s0:e0] += x[:e0 - s0]
            dv = len(x) / SR
            if o["text"]:                                   # re-temporiza los subtítulos de este párrafo
                trozos = [s for s in subs_old if o["t"] - 0.01 <= s[0] < o["t"] + o["dur"] + 0.7]
                pal = np.array([max(1, len(s[2].split())) for s in trozos], float)
                if len(trozos):
                    cum = np.concatenate([[0], np.cumsum(pal) / pal.sum()])
                    for j, s in enumerate(trozos):
                        a = o["t"] + LEAD + cum[j] * dv
                        b = o["t"] + LEAD + cum[j + 1] * dv + (0.25 if j == len(trozos) - 1 else 0)
                        nuevos.append((a, b, s[2]))
        # ducking: la música baja ~45 % mientras habla
        env = np.abs(voz)
        sos = butter(2, 6.0, btype="low", fs=SR, output="sos")
        env = np.clip(sosfiltfilt(sos, env) * 7.0, 0, 1)
        duck = (1.0 - 0.45 * env)[:, None]
        mix = bed * 0.9 * duck + np.stack([voz, voz], 1) * 1.0
        pico = np.abs(mix).max()
        if pico > 0.92:
            mix *= 0.92 / pico
        with wave.open(str(bed_p), "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((np.clip(mix, -1, 1) * 32767).astype("<i2").tobytes())
        # subtítulos: nuevos para la narración, y las citas/otros tal como estaban
        with open(VIDEO / "srt_voz" / f"{name}.srt", "w", encoding="utf-8") as fh:
            for n_, (a, b, t) in enumerate(sorted(nuevos), 1):
                fh.write(f"{n_}\n{ts(a)} --> {ts(b)}\n{t}\n\n")
        print(name, f"{n / SR:.0f} s", f"pico {np.abs(mix).max():.2f}", f"{len(nuevos)} subtítulos", flush=True)


if __name__ == "__main__":
    main()
