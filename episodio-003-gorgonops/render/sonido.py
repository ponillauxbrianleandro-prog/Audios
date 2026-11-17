#!/usr/bin/env python3
"""Banda sonora v3: ambiente + tango arreglado por clima + voz (limpia, sin saturación).

- El tango NO es un bucle: cada escena tiene un «clima» que cambia (calma, intriga, tensión, revelación, ternura, clímax, final).
  Se montan fragmentos de 6–13 s del cuarteto (alineados a compás), con instrumentos distintos en cada uno, entradas/salidas
  irregulares (semilla por escena), pequeños silencios musicales cubiertos por el ambiente, y golpes en las revelaciones.
- La música baja bajo la voz (ducking) y sube en los huecos.
Salidas (../video/): audio_sin_voz/NN-nombre.wav (ambiente+música) y audio/NN-nombre.wav (con voz).
Uso: python3 sonido.py   (requiere ../musica/wav y ../../voice_ai/cache_v2 + duraciones.json)
"""
import sys
import wave
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, sosfiltfilt, resample_poly

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
SR = 48000
MUS = AQUI.parent / "musica" / "wav"
VIDEO = AQUI.parent / "video"
VOZ = AQUI.parents[1] / "voice_ai" / "cache_v2"
BAR = 4 * 60.0 / 118.0

# (inicio, fin) en compases del tango: intro 0-2, A 2-10, A 10-18, B 18-26, A 26-34, C 34-42, A 42-50, A-tutti 50-58
CLIMAS = {
    "calma": dict(src=[(2, 10), (10, 18), (0, 2)], sets=[("piano", "contrabajo"), ("contrabajo", "violin"), ("piano",), ("bandoneon", "piano")], gain=0.40),
    "intriga": dict(src=[(18, 26), (0, 2), (2, 10)], sets=[("contrabajo", "bandoneon"), ("contrabajo", "piano", "bandoneon"), ("piano", "violin")], gain=0.46),
    "tension": dict(src=[(34, 42), (18, 26)], sets=[("contrabajo", "piano", "bandoneon"), ("contrabajo", "violin", "piano"), ("bandoneon", "piano")], gain=0.56),
    "revelacion": dict(src=[(34, 42), (50, 58), (26, 34)], sets=[("bandoneon", "violin", "piano", "contrabajo"), ("violin", "piano", "contrabajo")], gain=0.70),
    "ternura": dict(src=[(26, 34), (42, 50), (10, 18)], sets=[("violin", "piano"), ("violin", "bandoneon"), ("violin", "piano", "contrabajo")], gain=0.46),
    "climax": dict(src=[(50, 58), (34, 42)], sets=[("bandoneon", "violin", "piano", "contrabajo")], gain=0.76),
    "final": dict(src=[(42, 50), (26, 34)], sets=[("violin", "bandoneon"), ("violin", "piano")], gain=0.52),
}
# clima por escena: lista de (fracción de la escena en que empieza, clima)
MOOD = {
    "0 · Apertura": [(0, "revelacion")],
    "1 · El valle": [(0, "calma"), (0.65, "intriga")],
    "2 · Un solo continente": [(0, "calma"), (0.6, "ternura")],
    "3 · Alguien": [(0, "intriga")],
    "4 · Presentación": [(0, "ternura"), (0.55, "intriga")],
    "5 · La mañana": [(0, "calma"), (0.6, "ternura")],
    "5b · Cómo lo sabemos": [(0, "intriga")],
    "6 · Ni reptil ni mamífero": [(0, "intriga"), (0.5, "tension")],
    "7 · Caminar": [(0, "calma"), (0.6, "intriga")],
    "8 · Tres clases de dientes": [(0, "tension"), (0.65, "revelacion")],
    "9 · La caza": [(0, "tension"), (0.7, "intriga")],
    "10 · Lo que duele igual": [(0, "ternura"), (0.6, "revelacion")],
    "11 · El valle habitado": [(0, "calma"), (0.5, "intriga")],
    "12 · El pequeño": [(0, "ternura")],
    "13 · La estación seca": [(0, "intriga"), (0.5, "tension")],
    "14 · La bruma tenía dueño": [(0, "tension"), (0.6, "climax")],
    "15 · La rama que termina": [(0, "climax"), (0.55, "ternura")],
    "16 · Los huesos que escuchan": [(0, "ternura"), (0.6, "revelacion")],
    "17 · Las formas sin fin": [(0, "revelacion"), (0.6, "climax")],
    "18 · Simplemente vivía": [(0, "ternura"), (0.6, "final")],
}
# golpes de orquesta en las revelaciones: frase que los dispara -> (intensidad)
ACENTOS = {
    "Tampoco es un mamífero": 0.7,
    "Tres herramientas distintas": 0.7,
    "odontoma": 0.65,
    "la mayor que ha registrado la vida": 0.8,
    "No lo es.": 0.8,
    "Los gorgonópsidos no dejaron descendientes": 0.9,
    "martillo y yunque": 0.8,
    "Y los dos estuvieron": 0.7,
}


def leer(p):
    sr, x = wavfile.read(str(p))
    x = x.astype(np.float32) / (32768.0 if x.dtype == np.int16 else 8388608.0 if x.dtype == np.int32 else 1.0)
    return sr, x


def load(name):
    sr, x = leer(MUS / f"{name}.wav")
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    g = np.gcd(SR, sr)
    return np.stack([resample_poly(x[:, c], SR // g, sr // g) for c in (0, 1)], 1).astype(np.float32)


def band(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], btype="band", fs=SR, output="sos"), x, axis=0)


def lfo(n, rate, seed, lo=0.3, hi=1.0):
    r = np.random.default_rng(seed)
    k = max(4, int(n / SR * rate) + 4)
    return np.interp(np.linspace(0, k - 1, n), np.arange(k), r.uniform(lo, hi, k)).astype(np.float32)


def ambience(n, seed, wind=1.0, water=1.0, insects=1.0):
    r = np.random.default_rng(seed)
    out = np.zeros((n, 2), np.float32)
    for c in (0, 1):
        w = band(r.normal(0, 1, n), 90, 700) * lfo(n, 0.12, seed + c, 0.25, 1.0) * 0.050 * wind
        w += band(r.normal(0, 1, n), 600, 2200) * lfo(n, 0.3, seed + 5 + c, 0.0, 1.0) ** 2 * 0.010 * wind
        ag = band(r.normal(0, 1, n), 700, 3500) * (0.5 + 0.5 * lfo(n, 6.0, seed + 9 + c, 0.2, 1.0)) * 0.012 * water
        ins = band(r.normal(0, 1, n), 4200, 7500) * lfo(n, 1.5, seed + 13 + c, 0.0, 1.0) ** 4 * 0.006 * insects
        out[:, c] = w + ag + ins
    return out


def fade_env(m, a, b):
    e = np.ones(m, np.float32)
    na, nb = min(int(a * SR), m // 2), min(int(b * SR), m // 2)
    e[:na] = np.linspace(0, 1, na) ** 1.5
    e[m - nb:] = np.linspace(1, 0, nb) ** 1.5
    return e


def musica(n, escenas, stems, coda, voz_lineas, seed):
    """Arreglo irregular para un capítulo. escenas: [(nombre, t0, dur)]; voz_lineas: [(t, dur, texto)]."""
    out = np.zeros((n, 2), np.float32)
    rng = np.random.default_rng(seed)
    for nombre, t0, dur in escenas:
        plan = MOOD.get(nombre, [(0, "calma")])
        for j, (fr, clima) in enumerate(plan):
            a = t0 + fr * dur
            b = t0 + (plan[j + 1][0] * dur if j + 1 < len(plan) else dur)
            cfg = CLIMAS[clima]
            t = a
            while t < b - 1.0:
                seg = float(rng.uniform(6.0, 13.0))
                seg = min(seg, b - t + 1.5)
                s0, s1 = cfg["src"][int(rng.integers(len(cfg["src"])))]
                bar0 = int(rng.integers(s0, max(s0 + 1, s1 - int(seg / BAR) - 1)))
                src0 = int(bar0 * BAR * SR)
                m = int(seg * SR)
                inst = cfg["sets"][int(rng.integers(len(cfg["sets"])))]
                mix = sum(st[src0:src0 + m] for st in (stems[p] for p in inst))
                if len(mix) < m:
                    mix = np.pad(mix, ((0, m - len(mix)), (0, 0)))
                g = cfg["gain"] * float(rng.uniform(0.85, 1.12))
                seg_audio = mix * fade_env(m, float(rng.uniform(1.2, 2.4)), float(rng.uniform(1.8, 3.2)))[:, None] * g
                i0 = int(t * SR)
                i1 = min(n, i0 + m)
                if i1 > i0:
                    out[i0:i1] += seg_audio[:i1 - i0]
                # solape irregular + pequeño silencio musical ocasional (el ambiente lo cubre)
                t += seg - float(rng.uniform(1.0, 2.2)) + (float(rng.uniform(0.6, 1.8)) if rng.uniform() < 0.25 else 0.0)
    # golpes en las revelaciones
    for (tv, dv, texto) in voz_lineas:
        for frase, inten in ACENTOS.items():
            if frase in texto:
                k = texto.index(frase) / max(len(texto), 1)
                ta = tv + k * dv - 0.15
                i0 = int(max(0.0, ta) * SR)
                hit = coda[: int(1.4 * SR)] * inten * 0.75
                hit = hit * fade_env(len(hit), 0.01, 0.9)[:, None]
                i1 = min(n, i0 + len(hit))
                if i1 > i0:
                    # caída previa: se baja la música 0,6 s antes del golpe
                    dip = np.ones(n, np.float32)
                    j0 = max(0, i0 - int(0.6 * SR))
                    dip[j0:i0] = np.linspace(1.0, 0.25, i0 - j0)
                    dip[i0:min(n, i0 + int(0.5 * SR))] = 0.25
                    out *= dip[:, None]
                    out[i0:i1] += hit[:i1 - i0]
    return out


def voz_pista(n, voz_lineas_keys):
    v = np.zeros(n, np.float32)
    for tv, dv, key in voz_lineas_keys:
        f = VOZ / f"{key}.wav"
        if not f.exists():
            continue
        sr, x = leer(f)
        if x.ndim > 1:
            x = x.mean(1)
        g = np.gcd(SR, sr)
        x = resample_poly(x, SR // g, sr // g).astype(np.float32)
        i0 = int(tv * SR)
        i1 = min(n, i0 + len(x))
        if i1 > i0:
            v[i0:i1] += x[:i1 - i0]
    return v


def main():
    import documental as D
    D.world.load()
    D.engine.setup()
    SC = D.build()
    tl = D.timeline(SC)
    stems = {k: load(k) for k in ("bandoneon", "violin", "piano", "contrabajo")}
    coda = load("tango")[-int(5.2 * SR):]
    (VIDEO / "audio").mkdir(parents=True, exist_ok=True)
    (VIDEO / "audio_sin_voz").mkdir(parents=True, exist_ok=True)
    # texto por clave para localizar los golpes
    textos = {D.clave_voz(it[1]): it[1] for s in SC for it in s["items"] if it[0] == "nar"}
    for s in SC:
        for it in s["items"]:
            if it[0] == "quote":
                textos[D.clave_voz(D.texto_cita(it[1]))] = D.texto_cita(it[1])
    for cap in ([int(a) for a in sys.argv[1:]] or sorted(tl)):
        c = tl[cap]
        n = int(round(c["t"] * 24) / 24 * SR)
        escenas = c["scenes"]
        amb = {0: (1.0, 1.0, 0.8), 1: (0.8, 1.0, 1.0), 2: (0.9, 0.5, 0.8), 3: (0.7, 0.9, 1.3), 4: (1.6, 0.2, 0.3), 5: (1.2, 0.3, 0.4), 6: (0.8, 0.7, 1.0), 7: (0.9, 1.1, 0.9)}[cap]
        bed = ambience(n, 100 + cap, *amb) * 1.15
        vl = [(t, d, textos.get(k, "")) for (t, d, k) in c["voz"]]
        bed += musica(n, escenas, stems, coda, vl, 4000 + cap)
        voz = voz_pista(n, c["voz"])
        # ducking: la música/ambiente bajan ~9 dB mientras habla y suben en los huecos
        env = np.abs(voz)
        env = np.clip(sosfiltfilt(butter(2, 5.0, btype="low", fs=SR, output="sos"), env) * 9.0, 0, 1)
        duck = (1.0 - 0.65 * env)[:, None]
        bed_s = bed.copy()
        pk = np.abs(bed_s).max()
        if pk > 0.9:
            bed_s *= 0.9 / pk
        mezcla = bed * duck + np.stack([voz, voz], 1)
        pk = np.abs(mezcla).max()
        if pk > 0.89:                                   # limitador lineal: sin recortes ni saturación
            mezcla *= 0.89 / pk
        for path, x in ((VIDEO / "audio_sin_voz" / f"{D.CHAPTERS[cap]}.wav", bed_s), (VIDEO / "audio" / f"{D.CHAPTERS[cap]}.wav", mezcla)):
            with wave.open(str(path), "wb") as wv:
                wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR)
                wv.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
        print(D.CHAPTERS[cap], f"{n / SR:.1f} s", f"pico {np.abs(mezcla).max():.2f}", flush=True)


if __name__ == "__main__":
    main()
