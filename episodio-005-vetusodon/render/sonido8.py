#!/usr/bin/env python3
"""Mezcla de sonido del episodio 005: voz (sin solapes), tango arreglado por escena, ambiente y efectos sintetizados.

  python3 sonido8.py --voz        procesa la narración cruda -> voice_ai/cache_v8/final + durs.json
  python3 sonido8.py --mezcla     mezcla todo y escribe ../video/audio/vetusodon.wav (48 kHz estéreo, -16 LUFS)
Efectos (todos sintetizados): clic de cámara (cada corte del montaje), pasos con material según el suelo, agua, viento, insectos que salen
de la tierra y que vuelan, lluvia, ceniza, respiración, latido, lápiz y papel del cuaderno, rugido grave del gorgonopsio.
"""
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
SR = 48000
import os
VOZ = AQUI.parents[1] / "voice_ai" / os.environ.get("VOZ_CACHE", "cache_v9")
MUS = AQUI.parent / "musica" / "wav"
TANGO = Path("/root/.claude/uploads/206e7cfb-ffe4-542d-b71e-f006d55357a5/a873ee74-VoztypeRecorderVoiceMP3_160K.mp3")
VIDEO = AQUI.parent / "video"
rng = np.random.default_rng(8)


def lp(x, fc, o=2):
    return sosfilt(butter(o, fc, "low", fs=SR, output="sos"), x)


def hp(x, fc, o=2):
    return sosfilt(butter(o, fc, "high", fs=SR, output="sos"), x)


def bp(x, a, b, o=2):
    return sosfilt(butter(o, [a, b], "band", fs=SR, output="sos"), x)


def noise(n):
    return rng.standard_normal(n)


def rw(path, ch=None):
    """Lee un WAV (también float32) como float64 [n, canales] a 48 kHz, vía ffmpeg."""
    ch = ch or (2 if "musica" in str(path) else 1)
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "s16le", "-ac", str(ch), "-ar", str(SR), "-"], capture_output=True, check=True)
    x = np.frombuffer(r.stdout, np.int16).astype(np.float64) / 32768
    return x.reshape(-1, ch)


def put(buf, x, t, gain=1.0):
    i = int(round(t * SR))
    if i >= len(buf) or i + len(x) <= 0:
        return
    a, b = max(0, -i), min(len(x), len(buf) - i)
    if x.ndim == 1 and buf.ndim == 2:
        x = np.stack([x, x], 1)
    buf[i + a:i + b] += x[a:b] * gain


# ------------------------------------------------------------------ voz
GANANCIA = float(os.environ.get("GANANCIA", "5.0"))
RANGO13 = float(os.environ.get("RANGO13", "0.72"))                    # factor del rango de entonación de la voz v13 (1,0 = sin cambio)


def procesar_voz():
    import soundfile as sf
    raw, fin = VOZ / "raw", VOZ / "final"
    fin.mkdir(exist_ok=True)
    durs = {}
    import voz_proceso as VP
    TIEMPOS = json.loads((VOZ / "tiempos_lineas.json").read_text())
    DURS11 = json.loads((VOZ / "durs_v11.json").read_text())
    DER = VP.Derivas()
    V13 = os.environ.get("VOZ_CACHE") == "cache_v13"                    # voz «Quebracho v3»: clonada de la grabación del autor, solo se neutraliza la entonación
    V14 = os.environ.get("VOZ_CACHE") == "cache_v14"                    # voz «Quebracho v4»: sin resíntesis de tono ni saturación; neutralidad elegida en la generación
    NUEVA = V13 or V14 or os.environ.get("VOZ_CACHE") == "cache_v12"    # sin cambio de formantes
    for f in sorted(raw.glob("*.wav")):
        if f.name.endswith(".tmp.wav"):
            continue
        x, sr = sf.read(str(f))
        x = x.astype(np.float64)
        if x.ndim > 1:
            x = x.mean(1)
        import voz_proceso as VP
        T0 = TIEMPOS.get(f.stem, 0.0)
        if V14:
            pass                                                        # la voz se deja tal cual salió del clon
        elif V13:
            x = VP.neutralizar(x, sr, RANGO13)                          # menos exaltada: baja el rango de entonación; timbre y formantes intactos
        elif not NUEVA:
            x = VP.gender(x, sr)                                        # voz anterior: formantes x0,95, mediana 124 Hz, rango x1,6
        if sr != SR:
            x = np.interp(np.linspace(0, len(x) - 1, int(len(x) * SR / sr)), np.arange(len(x)), x)
        if not V14:
            x = VP.deriva_tono(x, SR, T0, DER)                          # deriva de tono <= 1 % (sube de a poco, vuelve a neutral)
        x = VP.eq_fir(x, SR, 1.0, 2.0, 500.0) if V14 else VP.eq_fir(x, SR, 1.0, 4.0) if V13 else VP.eq_fir(x, SR)     # balance tonal de la grabación de referencia (v13: suave, ±3 dB)
        x = VP.deriva_bandas(x, SR, T0, DER)
        if V14:
            x = VP.deriva_ganancia(x, SR, T0, DER)                      # ±0,3 dB lentos, irregulares
        x = hp(x, 70)
        e = np.abs(x) > 0.015
        if e.any():
            a, b = np.argmax(e), len(e) - np.argmax(e[::-1])
            x = x[max(0, a - int(0.04 * SR)):min(len(x), b + int(0.10 * SR))]
        act = x[np.abs(x) > 0.02]
        rms = np.sqrt((act ** 2).mean()) if len(act) else 0.1
        x = x * (10 ** (-17 / 20) / (rms + 1e-9))
        x = x if V14 else np.tanh(x * 1.25) / 1.25 if V13 else np.tanh(x * 2.0) / 2.0   # v14: sin saturación (el limitador final alcanza)
        x[:int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))
        x[-int(0.03 * SR):] *= np.linspace(1, 0, int(0.03 * SR))
        tmp = fin / "_tmp.wav"
        sf.write(str(tmp), x.astype(np.float32), SR, subtype="FLOAT")
        if V14:
            cadena = ("highpass=f=55,equalizer=f=150:t=q:w=1.0:g=2,acompressor=threshold=-22dB:ratio=1.6:attack=20:release=250:makeup=%s,"
                      "alimiter=limit=0.89:level=disabled" % GANANCIA)
            lim = (0.92, 1.40) if f.name.startswith("00_") else (0.92, 1.12)
            tempo = min(lim[1], max(lim[0], (len(x) / SR) / DURS11[f.stem])) if f.stem in DURS11 else 1.0
            if abs(tempo - 1) > 0.02:
                cadena = "rubberband=tempo=%.4f:pitchq=quality:formant=preserved:transients=smooth," % tempo + cadena
        elif NUEVA:
            cadena = ("highpass=f=75,acompressor=threshold=-24dB:ratio=%s:attack=8:release=160:makeup=%s,alimiter=limit=0.89:level=disabled" % (2 if V13 else 3, GANANCIA))
            tempo = min(1.35, max(0.85, (len(x) / SR) / DURS11[f.stem])) if f.stem in DURS11 else 1.0
            if abs(tempo - 1) > 0.01:
                cadena = "rubberband=tempo=%.4f:pitchq=quality," % tempo + cadena
        else:
            cadena = ("highpass=f=75,equalizer=f=170:t=q:w=1.0:g=1,equalizer=f=420:t=q:w=1.2:g=2.5,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=2900:t=q:w=1.0:g=-2.5,equalizer=f=5500:t=q:w=1.2:g=-3,"
                      "acompressor=threshold=-24dB:ratio=3:attack=8:release=160:makeup=%s,alimiter=limit=0.89:level=disabled" % GANANCIA)
            if f.name.startswith("00_"):
                cadena = "rubberband=tempo=1.28:pitchq=quality," + cadena
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(tmp), "-af", cadena, "-ar", str(SR), "-c:a", "pcm_s16le", str(fin / f.name)], check=True)
        y = rw(fin / f.name)[:, 0]
        if f.stem in DURS11:                                            # congela la duración de la v11: subtítulos y tarjetas siguen alineados
            n = int(round(DURS11[f.stem] * SR))
            if len(y) > n:
                y = y[:n].copy()
                y[-int(0.03 * SR):] *= np.linspace(1, 0, int(0.03 * SR))
            else:
                y = np.pad(y, (0, n - len(y)))
            with wave.open(str(fin / f.name), "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
                w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
        x = y
        durs[f.stem] = len(x) / SR
    (VOZ / "durs.json").write_text(json.dumps(durs))
    print(len(durs), "frases procesadas")


# ------------------------------------------------------------------ efectos
def clic(vol=1.0):
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    a = bp(noise(n), 1800, 7500) * np.exp(-t * 90)                       # obturador: golpe seco y agudo
    b = lp(noise(n), 400) * np.exp(-t * 60) * 0.6
    c = np.zeros(n)
    k = int(0.035 * SR)
    c[k:] = bp(noise(n - k), 900, 4200) * np.exp(-t[:n - k] * 70) * 0.7  # segunda cortina
    return (a + b + c) * vol * 0.9


def paso(mat="arcilla", pesado=0.6):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    base = lp(noise(n), 260 + 300 * (1 - pesado)) * np.exp(-t * 22) * 1.0
    thump = np.sin(2 * np.pi * (65 + 30 * (1 - pesado)) * t) * np.exp(-t * 28) * pesado
    if mat == "arena":
        tex = bp(noise(n), 1200, 5000) * np.exp(-t * 14) * 0.5
    elif mat == "ceniza":
        tex = bp(noise(n), 600, 3200) * np.exp(-t * 11) * 0.6
    elif mat == "barro":
        tex = lp(noise(n), 900) * np.exp(-t * 8) * 0.7
        base = base * 0.7
    else:
        tex = bp(noise(n), 700, 3600) * np.exp(-t * 26) * 0.35
    return (base + thump + tex) * 0.8


def viento(dur, fuerza=0.5):
    n = int(dur * SR)
    x = lp(noise(n), 420 + 500 * fuerza)
    t = np.arange(n) / SR
    mod = 0.55 + 0.45 * np.sin(2 * np.pi * (0.07 + 0.05 * fuerza) * t + rng.uniform(0, 6)) * np.sin(2 * np.pi * 0.19 * t + rng.uniform(0, 6))
    return x * mod * (0.16 + 0.28 * fuerza)


def agua(dur, caudal=0.5):
    n = int(dur * SR)
    x = bp(noise(n), 500, 4200)
    t = np.arange(n) / SR
    x *= 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * (0.9 + 0.8 * caudal) * t + rng.uniform(0, 6)) * np.sin(2 * np.pi * 0.37 * t))
    gotas = np.zeros(n)
    for _ in range(int(dur * 1.4)):
        f = rng.uniform(600, 2400)
        tt = np.arange(int(0.07 * SR)) / SR
        g = np.sin(2 * np.pi * f * (1 + 3 * tt) * tt) * np.exp(-tt * 60)
        i = rng.integers(0, max(1, n - len(g)))
        gotas[i:i + len(g)] += g * rng.uniform(0.04, 0.12)
    return x * 0.10 * (0.4 + caudal) + gotas


def insectos(dur, densidad=1.0, noche=False):
    n = int(dur * SR)
    out = np.zeros(n)
    for _ in range(int(dur * 0.45 * densidad) + 1):
        f0 = rng.uniform(3200, 6500) if noche else rng.uniform(2600, 5200)
        L = rng.uniform(0.6, 3.0)
        tt = np.arange(int(L * SR)) / SR
        pulso = (np.sin(2 * np.pi * rng.uniform(14, 30) * tt) > 0.2).astype(float)
        x = np.sin(2 * np.pi * f0 * tt) * pulso * np.sin(np.pi * tt / L) ** 2
        i = rng.integers(0, max(1, n - len(x)))
        out[i:i + len(x)] += x * rng.uniform(0.012, 0.032)
    return out


def zumbido(vuelo=1.8):
    """Insecto que pasa volando: aleteo grave que sube y baja (Doppler)."""
    n = int(vuelo * SR)
    t = np.arange(n) / SR
    f = 230 + 80 * np.sin(np.pi * t / vuelo) + rng.normal(0, 3, 1)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sin(ph) + 0.6 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph)) * (0.5 + 0.5 * np.sin(2 * np.pi * 38 * t))
    return bp(x, 150, 2200) * np.sin(np.pi * t / vuelo) ** 2 * 0.07


def tierra_que_cae(vol=1.0):
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    x = bp(noise(n), 300, 3200) * np.exp(-t * 5) * (0.5 + 0.5 * np.abs(noise(n)).clip(0, 1))
    pops = np.zeros(n)
    for _ in range(14):
        i = rng.integers(0, int(0.5 * SR))
        k = int(0.012 * SR)
        pops[i:i + k] += bp(noise(k), 500, 4000) * np.hanning(k)
    return (x * 0.5 + pops * 0.6) * vol


def lluvia(dur, fuerza=0.6, acida=False):
    n = int(dur * SR)
    x = hp(noise(n), 1500) * 0.07 * fuerza + bp(noise(n), 500, 1400) * 0.05 * fuerza
    if acida:
        t = np.arange(n) / SR
        x += hp(noise(n), 4000) * 0.03 * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * t + 1.3))      # chisporroteo
    return x


def retumbar(dur, nivel=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = lp(noise(n), 70 + 40 * nivel, 3) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t + rng.uniform(0, 6)) ** 2)
    return x * (0.6 + 0.9 * nivel)


def respirar(vol=1.0, pesado=0.5):
    n = int(1.4 * SR)
    t = np.arange(n) / SR
    env = np.sin(np.pi * np.clip(t / 0.9, 0, 1)) ** 2 * (t < 0.9)
    return bp(noise(n), 200, 1600) * env * 0.12 * vol + lp(noise(n), 160) * env * 0.08 * vol * pesado


def latido(vol=1.0):
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    a = np.sin(2 * np.pi * 52 * t) * np.exp(-t * 22)
    b = np.zeros(n)
    k = int(0.17 * SR)
    b[k:] = (np.sin(2 * np.pi * 46 * t[:n - k]) * np.exp(-t[:n - k] * 26)) * 0.7
    return (a + b) * vol * 0.55


def rugido(vol=1.0):
    n = int(2.2 * SR)
    t = np.arange(n) / SR
    f = 62 + 18 * np.sin(2 * np.pi * 1.7 * t) + 40 * np.exp(-t * 2)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = sum(np.sin(k * ph) / k ** 0.8 for k in range(1, 12))
    x = bp(x * (1 + 0.5 * noise(n) * 0.2), 50, 1400) * np.sin(np.pi * t / 2.2) ** 0.8
    return x * 0.25 * vol


def impacto(vol=1.0):
    """Golpe grave de cine: caída de tono, ruido y cola."""
    n = int(2.2 * SR)
    t = np.arange(n) / SR
    f = 38 + 90 * np.exp(-t * 7)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * 2.6) * 0.95 + lp(noise(n), 900) * np.exp(-t * 7) * 0.5 + hp(noise(n), 3000) * np.exp(-t * 18) * 0.25
    return x * vol * 0.8


def subida(dur=2.0, vol=1.0):
    """Tensión que crece antes de un golpe: ruido filtrado que sube de volumen y de brillo."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = bp(noise(n), 300, 3000) * (t / dur) ** 2.2 * 0.22 + np.sin(2 * np.pi * np.cumsum(60 + 120 * (t / dur) ** 2) / SR) * (t / dur) ** 2 * 0.15
    return x * vol


def mordida(vol=1.0):
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    x = lp(noise(n), 1600) * np.exp(-t * 20) * 0.9 + bp(noise(n), 1200, 5000) * np.exp(-t * 35) * 0.4
    return x * vol * 0.7


def gruñido(vol=1.0, grave=1.0):
    n = int(1.1 * SR)
    t = np.arange(n) / SR
    f = (95 + 25 * np.sin(2 * np.pi * 8 * t) + 20 * np.sin(2 * np.pi * 3.1 * t)) / grave
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = sum(np.sin(k * ph) / k ** 0.7 for k in range(1, 10))
    return bp(x * (0.7 + 0.3 * noise(n) * 0.2), 70, 1300) * np.sin(np.pi * np.clip(t / 1.1, 0, 1)) ** 0.8 * 0.22 * vol


def lapiz(dur, vol=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    mod = 0.55 + 0.45 * np.abs(np.sin(2 * np.pi * rng.uniform(5, 9) * t + 0.3)) ** 0.7
    return bp(noise(n), 1800, 7500) * mod * 0.045 * vol * np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 0.05)


def papel(vol=1.0):
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    return bp(noise(n), 900, 6500) * (np.exp(-t * 4) * (0.5 + 0.5 * np.abs(np.sin(t * 40)))) * 0.10 * vol


def tinta_ambiente(tipo, dur, mat):
    """Capa de ambiente continua por escena."""
    n = int(dur * SR)
    z = np.zeros(n)
    if tipo in ("calle",):
        return z
    if tipo == "cuaderno":
        return lp(noise(n), 300) * 0.012 + viento(dur, 0.1) * 0.15
    if tipo in ("amanecer", "valle", "mañana", "final"):
        return viento(dur, 0.25) + agua(dur, 0.5) * 0.9 + insectos(dur, 1.2)
    if tipo == "tension":
        return viento(dur, 0.35) + retumbar(dur, 0.25) * 0.35 + insectos(dur, 0.4) * 0.5
    if tipo == "sequia":
        return viento(dur, 0.55) + insectos(dur, 0.3) * 0.5 + retumbar(dur, 0.15) * 0.2
    if tipo == "ceniza":
        return viento(dur, 0.6) + retumbar(dur, 0.7) + lluvia(dur, 0.5, True)
    if tipo == "noche":
        return viento(dur, 0.2) * 0.8 + insectos(dur, 1.1, True) + retumbar(dur, 0.1) * 0.2
    return viento(dur, 0.3)


MATERIAL = dict(amanecer="arcilla", valle="barro", mañana="arcilla", tension="arena", sequia="arena", ceniza="ceniza", noche="ceniza", final="barro")


# ------------------------------------------------------------------ mezcla
MOOD = {0: "rafaga", 1: "calma", 2: "calma", 3: "misterio", 4: "ternura", 5: "rafaga", 6: "tension", 7: "misterio", 8: "tension_suave",
        9: "drama", 10: "ternura", 11: "final"}
GAINS = dict(
    rafaga=dict(piano=.8, contrabajo=.9, guitarra=.6, acordeon=.5, bandoneon=1.0, golpes=1.0),
    calma=dict(piano=.8, contrabajo=.6, guitarra=.8, acordeon=.55, bandoneon=.0, golpes=.25),
    misterio=dict(piano=.6, contrabajo=.5, guitarra=.5, acordeon=.65, bandoneon=.35, golpes=.1),
    ternura=dict(piano=.55, contrabajo=.35, guitarra=.9, acordeon=1.0, bandoneon=.0, golpes=.0),
    tension=dict(piano=.9, contrabajo=1.0, guitarra=.4, acordeon=.3, bandoneon=1.0, golpes=.9),
    tension_suave=dict(piano=.6, contrabajo=.7, guitarra=.3, acordeon=.5, bandoneon=.6, golpes=.4),
    drama=dict(piano=1.0, contrabajo=1.0, guitarra=.5, acordeon=.7, bandoneon=1.0, golpes=1.0),
    final=dict(piano=.9, contrabajo=.8, guitarra=.8, acordeon=1.0, bandoneon=.8, golpes=.4),
)


def plan_musica(TL):
    """Plan de la música: por escena, clima, duración y momentos boom (s desde el inicio de la escena)."""
    return [dict(clima=c["clima"], dur=round(c["dur"], 3), booms=[round(b, 2) for b in c["booms"] if b < c["dur"] - 0.5]) for c in TL]


def mezclar(central=False):
    """central=True: solo las escenas 1–11 (sin apertura ni cierre), con tiempos relativos al inicio de la escena 1 → video/audio/central.wav"""
    import episodio as E
    from cuaderno import _elementos
    TL, total = E.timeline()
    base = 0.0
    if central:
        TL = [c for c in TL if c["esc"] not in (0, 15)]
        base = TL[0]["t0"]
        total = TL[-1]["t0"] + TL[-1]["dur"] - base
    n = int((total + 2.0) * SR)
    voz = np.zeros((n, 2))
    fx = np.zeros((n, 2))
    amb = np.zeros((n, 2))
    mus = np.zeros((n, 2))
    wavm = MUS / "musica_v9.wav"
    if not wavm.exists() and not central:
        plan = plan_musica(TL)
        (AQUI.parent / "musica" / "plan.json").write_text(json.dumps(plan))
        subprocess.run([sys.executable, str(AQUI.parent / "musica" / "musica_real.py"), str(TANGO), str(wavm), str(AQUI.parent / "musica" / "plan.json")], check=True)
    mus_full = rw(wavm)
    put(mus, (mus_full[int(12.0 * SR):] if central else mus_full)[:n], 0.0, 1.0)
    for c in TL:
        t0 = (c["t0"] - base)
        # voz: cada frase en su instante; nunca se solapa (el tiempo de escena ya las separa)
        for k, (t, d, tx) in enumerate(c["lineas"]):
            f = VOZ / "final" / f"{c['esc']:02d}_{k}.wav"
            if f.exists():
                put(voz, rw(f)[:, 0], t0 + t)
        # música
        # ambiente
        a = tinta_ambiente(c["amb"], c["dur"], MATERIAL.get(c["amb"], "arcilla"))
        f = int(0.8 * SR)
        a[:f] *= np.linspace(0, 1, f)
        a[-f:] *= np.linspace(1, 0, f)
        put(amb, a, t0, 1.0)
        # efectos por plano
        for shot_idx, (ts, d, sh) in enumerate(c["shots"]):
            T = t0 + ts
            if sh.get("tomas_lazy"):                                                # cortes del montaje = clic de cámara
                for tc in sh["cortes"]:
                    put(fx, clic(), t0 + tc, 0.85)
                continue
            for el in sh.get("nb_audio", []):                                          # cuaderno: lápiz y papel
                put(fx, lapiz(max(0.2, el[1] - el[0])), T + el[0], 1.0)
            if sh.get("nb_audio"):
                put(fx, papel(), T + 0.1, 0.8)
                put(fx, papel(), T + d - 1.0, 0.7)
            acts = sh.get("actors", ())
            vel = max([getattr(a, "vel", 0.0) for a in acts] or [0.0])
            mov = sum(1 for a in acts if getattr(a, "vel", 0.0) > 0.05)
            esc = c["esc"]
            if vel > 0.05 and "pasos" in c["sfx"]:
                spec = acts[0].spec
                step = spec["period"] / 4.0 / max(vel / spec["speed"], 0.4)
                tt, j = 0.1, 0
                mat = MATERIAL.get(c["amb"], "arcilla")
                while tt < d - 0.1:
                    for q in range(min(mov, 4)):
                        put(fx, paso(mat, 0.35 + 0.5 * min(1.0, spec["scale"])), T + tt + rng.normal(0, 0.03) + 0.07 * q, (0.7 / (1 + 0.4 * q)) * (0.8 + 0.2 * (j % 2)))
                    tt += step * rng.uniform(0.92, 1.08)
                    j += 1
            if "respira" in c["sfx"]:
                for tt in np.arange(0.5, d - 1.2, 3.2):
                    put(fx, respirar(0.8, 0.5), T + tt, 0.8)
            if esc == 10:
                for tt in np.arange(0.8, d, 1.0):
                    put(fx, latido(0.7), T + tt, 0.5)
            if esc == 12:
                for tb in c["booms"]:
                    if ts <= tb < ts + d:
                        put(fx, mordida(), t0 + tb, 0.9)
                        put(fx, gruñido(1.0, 1.0 + 0.2 * (tb % 3)), t0 + tb - 0.2, 0.7)
                        put(fx, gruñido(0.8, 1.4), t0 + tb + 0.5, 0.6)
            if esc in (13, 14, 6) and shot_idx == 0:
                for tt in np.arange(2.0, c["dur"] - 2, 5.5):
                    put(fx, gruñido(0.7, 1.5), t0 + tt, 0.5)
            if esc == 6 and len(acts) >= 2:
                put(fx, rugido(), T + min(1.0, d * 0.3), 0.9)
    for c in TL:                                                            # momentos boom: tensión creciente y golpe grave
        for tb in c["booms"]:
            if c["esc"] == 12:
                continue
            put(fx, subida(1.8), (c["t0"] - base) + tb - 1.8, 0.8)
            put(fx, impacto(), (c["t0"] - base) + tb, 0.9)
        for tc, key, dd in c.get("cards", []):                               # tarjeta de cita: golpe y cola
            put(fx, impacto(), (c["t0"] - base) + tc, 0.8)
    # insectos que pasan volando y que salen de la tierra en escenas vivas
    for c in TL:
        if c["esc"] in (1, 2, 4, 11, 10, 13):
            for tt in np.arange(3.0, c["dur"] - 3, 5.5):
                put(fx, zumbido(rng.uniform(1.4, 2.4)), (c["t0"] - base) + tt + rng.uniform(-0.8, 0.8), 0.8)
            for tt in np.arange(6.0, c["dur"] - 3, 13.0):
                put(fx, tierra_que_cae(), (c["t0"] - base) + tt, 0.8)
    # bajar la música y el ambiente bajo la voz
    from scipy.ndimage import uniform_filter1d
    env = uniform_filter1d(np.abs(voz[:, 0]), int(0.18 * SR), mode="nearest")
    env = np.clip(env / 0.10, 0, 1)
    env = uniform_filter1d(env, int(0.25 * SR), mode="nearest")
    duck = 1 - 0.70 * env
    out = voz * 1.0 + mus * duck[:, None] * 0.95 + amb * (1 - 0.35 * env)[:, None] * 1.0 + fx * 0.9
    out *= 0.9 / (np.abs(out).max() + 1e-9)
    (VIDEO / "audio").mkdir(parents=True, exist_ok=True)
    raw = VIDEO / "audio" / ("central_crudo.wav" if central else "vetusodon_crudo.wav")
    with wave.open(str(raw), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(out, -1, 1) * 32767).astype("<i2").tobytes())
    fin = VIDEO / "audio" / ("central.wav" if central else "vetusodon.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", str(fin)], check=True)
    print("audio listo:", fin, f"{len(out) / SR:.1f} s")


if __name__ == "__main__":
    if "--voz" in sys.argv:
        procesar_voz()
    elif "--central" in sys.argv:
        mezclar(central=True)
    elif "--mezcla" in sys.argv:
        mezclar()
    else:
        print(__doc__)
