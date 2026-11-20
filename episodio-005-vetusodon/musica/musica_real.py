#!/usr/bin/env python3
"""Música del episodio 005 armada con LA GRABACIÓN REAL del usuario (tango antiguo, sol menor, ~122,7 BPM).

Nada sintético: se detecta la grilla de pulsos/compases del audio, se mide cada compás (energía, brillo, graves), se cortan frases en
límites de pulso y se montan por escena con estiramiento de calidad (`rubberband`), cruces en pulso y filtros según el clima.
Los golpes secos (transitorios del propio audio) sirven para subrayar los momentos "boom" y los cortes.

  python3 musica_real.py <tango.mp3> <salida.wav> [--plan]   -> música de toda la película, 48 kHz estéreo
`PLAN` define, por escena: clima, duración y los instantes (s desde el inicio de la escena) de sus golpes "boom".
"""
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt
from scipy.ndimage import uniform_filter1d

SR = 48000
AQUI = Path(__file__).resolve().parent
TMP = AQUI / "wav"

CLIMAS = {      # clima -> (percentil de energía de los compases elegidos, pasa-bajos Hz o None, ganancia)
    "calma": (0.15, 5200, 0.85), "misterio": (0.30, 4200, 0.85), "ternura": (0.25, 6000, 0.9), "tension": (0.60, None, 1.0),
    "drama": (0.80, None, 1.0), "boom": (0.92, None, 1.05), "final": (0.95, None, 1.05), "rafaga": (0.85, None, 1.0),
}


def leer(path):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "s16le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.int16).astype(np.float64).reshape(-1, 2) / 32768


def escribir(path, x):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


def grilla(x):
    """Afina el tempo y el primer pulso con el flujo de energía; devuelve (bpm, t0, duración de pulso)."""
    m = x.mean(1)
    hop = 256
    n = len(m) // hop
    fr = m[:n * hop].reshape(n, hop) * np.hanning(hop)
    S = np.abs(np.fft.rfft(fr, axis=1))
    f = np.fft.rfftfreq(hop, 1 / SR)
    flux = 0
    for a, b in ((60, 250), (250, 2000), (2000, 8000)):
        e = S[:, (f >= a) & (f < b)].sum(1)
        flux = flux + np.clip(np.diff(e, prepend=e[0]), 0, None)
    flux = flux - flux.mean()
    fps = SR / hop
    best = None
    for bpm in np.arange(118, 127.01, 0.05):
        per = fps * 60 / bpm
        idx = np.arange(0, n - 1, per)
        for ph in np.arange(0, per, per / 24):
            ii = (idx + ph).astype(int)
            ii = ii[ii < n]
            s = flux[ii].sum()
            if best is None or s > best[0]:
                best = (s, bpm, ph / fps)
    return best[1], best[2], 60.0 / best[1]


def medir_compases(x, t0, beat, nb_por_frase=1):
    bar = 4 * beat
    nb = int((len(x) / SR - t0) // bar)
    m = x.mean(1)
    rows = []
    for b in range(nb):
        a = int((t0 + b * bar) * SR)
        seg = m[a:a + int(bar * SR)]
        sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        f = np.fft.rfftfreq(len(seg), 1 / SR)
        rows.append((np.sqrt((seg ** 2).mean()), (sp * f).sum() / sp.sum(), sp[(f > 60) & (f < 250)].sum() / sp.sum()))
    return np.array(rows), bar


def pasabajos(x, fc):
    sos = butter(2, fc, "low", fs=SR, output="sos")
    return np.stack([sosfilt(sos, x[:, c]) for c in range(2)], 1)


def estirar(x, factor):
    """Estira en el tiempo (factor>1 = más largo) con rubberband, sin cambiar el tono."""
    if abs(factor - 1) < 0.004:
        return x
    tmp_in, tmp_out = TMP / "_in.wav", TMP / "_out.wav"
    escribir(tmp_in, x)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(tmp_in), "-af", f"rubberband=tempo={1 / factor:.5f}:transients=crisp:pitchq=quality",
                    str(tmp_out)], check=True)
    return leer(tmp_out)


def cruce(a, b, n):
    """Une `b` a `a` con un cruce de potencia constante de n muestras."""
    n = min(n, len(a), len(b))
    t = np.linspace(0, np.pi / 2, n)[:, None]
    mid = a[-n:] * np.cos(t) + b[:n] * np.sin(t)
    return np.vstack([a[:-n], mid, b[n:]])


def golpes(x, t0, beat):
    """Transitorios fuertes del propio audio (impactos secos) para subrayar los booms: lista de fragmentos de 0,9 s."""
    m = x.mean(1)
    h = sosfilt(butter(2, 700, "high", fs=SR, output="sos"), m)
    e = uniform_filter1d(np.abs(h), int(0.01 * SR))
    thr = np.percentile(e, 99.2)
    out, last = [], -10**9
    for i in np.flatnonzero((e[1:-1] > thr) & (e[1:-1] >= e[:-2]) & (e[1:-1] > e[2:])) + 1:
        if i - last > SR * 0.8:
            a = max(0, i - int(0.01 * SR))
            seg = x[a:a + int(0.9 * SR)].copy()
            seg *= np.minimum(1, np.linspace(0, 12, len(seg)))[:, None] * (np.linspace(1, 0, len(seg)) ** 1.2)[:, None]
            out.append((e[i], seg))
            last = i
    out.sort(key=lambda p: -p[0])
    return [s for _, s in out[:12]]


def armar(tango, plan, salida):
    TMP.mkdir(exist_ok=True)
    x = leer(tango)
    bpm, t0, beat = grilla(x)
    feats, bar = medir_compases(x, t0, beat)
    nb = len(feats)
    rms = feats[:, 0]
    rank = np.argsort(np.argsort(rms)) / max(nb - 1, 1)                    # percentil de energía de cada compás
    print(f"grilla: {bpm:.2f} BPM · compás {bar:.3f} s · {nb} compases · primer pulso {t0:.3f} s")
    G = golpes(x, t0, beat)
    rng = np.random.default_rng(5)
    total = sum(p["dur"] for p in plan)
    out = np.zeros((int((total + 2) * SR), 2))
    t_esc = 0.0
    usados = set()
    for p in plan:
        pct, lp, gain = CLIMAS[p["clima"]]
        dur = p["dur"]
        # compases candidatos: los de energía más cercana al clima de la escena (sin repetir si se puede)
        cand = [b for b in np.argsort(np.abs(rank - pct)) if b + 4 <= nb]
        cand = [b for b in cand if b not in usados] or cand
        # frases de 4 compases consecutivos: se eligen arrancando en los mejores compases
        frases, need = [], dur
        k = 0
        while need > 0 and k < len(cand):
            b0 = int(cand[k])
            k += 1
            if any(abs(b0 - u) < 4 for u in usados):
                continue
            n_b = 4
            frases.append((b0, n_b))
            usados.update(range(b0, b0 + n_b))
            need -= n_b * bar * 0.95
        if need > 0:                                                         # si faltan frases, se repiten las mejores
            while need > 0:
                b0 = int(cand[len(frases) % max(1, min(len(cand), 6))])
                frases.append((b0, 4))
                need -= 4 * bar * 0.95
        buf = None
        for b0, n_b in frases:
            a = int((t0 + b0 * bar) * SR)
            seg = x[a:a + int(n_b * bar * SR)].copy()
            seg *= np.minimum(1, np.linspace(0, 20, len(seg)))[:, None]
            buf = seg if buf is None else cruce(buf, seg, int(0.35 * SR))
        # estirado suave para que calce con la duración y sin pasar de ±9 %
        f = (dur + 0.4) / (len(buf) / SR)
        f = float(np.clip(f, 0.91, 1.09))
        buf = estirar(buf, f)
        buf = buf[:int((dur + 0.4) * SR)]
        if len(buf) < int((dur + 0.4) * SR):
            buf = np.vstack([buf, np.zeros((int((dur + 0.4) * SR) - len(buf), 2))])
        if lp:
            buf = pasabajos(buf, lp)
        buf *= gain
        fi, fo = int(0.8 * SR), int(1.0 * SR)
        buf[:fi] *= np.linspace(0, 1, fi)[:, None]
        buf[-fo:] *= np.linspace(1, 0, fo)[:, None]
        for tb in p.get("booms", []):                                        # golpes reales del audio en los booms
            g = G[rng.integers(0, len(G))] if G else None
            if g is not None:
                i = int(tb * SR)
                end = min(len(buf), i + len(g))
                buf[i:end] += g[:end - i] * 0.9
        i0 = int(t_esc * SR)
        out[i0:i0 + len(buf)] += buf[:len(out) - i0]
        t_esc += dur
    pico = np.abs(out).max()
    out *= 0.9 / (pico + 1e-9)
    escribir(salida, out[:int((total + 1) * SR)])
    print("música lista:", salida, f"{total:.1f} s")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    plan = json.loads(Path(args[2]).read_text()) if len(args) > 2 else json.loads((AQUI / "plan.json").read_text())
    armar(args[0], plan, args[1])
