#!/usr/bin/env python3
"""Tango distorsionado + efectos + mezcla con la narración (episodio 003).

Requiere haber corrido generar_audio.py (usa audio/timeline.json). Solo numpy y ffmpeg.
Salida: audio/episodio-003-mezcla.mp3  (voz + música + efectos)
"""
import subprocess

import numpy as np

from comun import AQUI, SFX, TEMPOS, cargar

SR = 44100
SALIDA = AQUI / "audio"
RNG = np.random.default_rng(3)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def t_(n):
    return np.arange(n) / SR


def saw(freq, n, vib=0.0, det=0.0):
    t = t_(n)
    f = freq * (1 + det) * (1 + vib * np.sin(2 * np.pi * 5.6 * t))
    return 2 * ((np.cumsum(f) / SR) % 1) - 1


def decay(n, tau, ataque=0.004):
    t = t_(n)
    return np.minimum(1, t / ataque) * np.exp(-t / tau)


def suave(x, k):
    """Pasabajos barato: media móvil de k muestras."""
    if k <= 1:
        return x
    return np.convolve(x, np.ones(k) / k, mode="same")


def poner(buf, x, t0, ganancia=1.0):
    i = int(t0 * SR)
    if i >= len(buf):
        return
    x = x[: len(buf) - i]
    buf[i:i + len(x)] += x * ganancia


# ---------- instrumentos ----------
def bajo(f, dur):
    n = int(dur * SR)
    return np.tanh(1.6 * (np.sin(2 * np.pi * f * t_(n)) + 0.4 * saw(f, n))) * decay(n, dur * 0.7)


def bandoneon(notas, dur, tau=0.16, trem=0.0):
    n = int(dur * SR)
    x = sum(saw(midi(m), n, 0.004, 0.003) + saw(midi(m), n, 0.0, -0.004) for m in notas) / len(notas)
    x = suave(x, 5)
    if trem:
        x = x * (1 - trem + trem * np.sin(2 * np.pi * 7 * t_(n)))
    return np.tanh(2.6 * x) * decay(n, tau)


def lead(m, dur, vib=0.012, tau=0.5):
    n = int(dur * SR)
    x = suave(saw(midi(m), n, vib) + 0.5 * saw(midi(m) * 2, n, vib), 3)
    return np.tanh(3.2 * x) * decay(n, tau, 0.012) * np.minimum(1, (dur - t_(n)) / 0.03 + 0.0).clip(0, 1)


def bombo(): 
    n = int(0.28 * SR)
    t = t_(n)
    f = 45 + 90 * np.exp(-t / 0.035)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.09)


def redoble():
    n = int(0.16 * SR)
    r = RNG.standard_normal(n)
    return (r - suave(r, 12)) * decay(n, 0.045, 0.001)


def tic():
    n = int(0.05 * SR)
    r = RNG.standard_normal(n)
    return (r - suave(r, 4)) * decay(n, 0.012, 0.0005)


# ---------- música ----------
ACORDES = {  # nombre: (bajo midi, notas del acorde)
    "Am": (45, (57, 60, 64)), "Dm": (50, (62, 65, 69)), "E": (52, (56, 59, 62)),
    "A": (45, (57, 61, 64)), "F": (41, (60, 65, 69)),
}
ESCALA = [0, 2, 3, 5, 7, 8, 11, 12, 14, 15]  # la menor armónica desde A4
PROG = ["Am", "Dm", "E", "Am"]
PROG_SUSPENSO = ["Am", "E", "Am", "E"]
# (densidad de melodía, golpes de hi-hat, tremolo del acorde, octava)
CARACTER = {
    1: (0.95, 1, 0.0, 0), 2: (0.85, 1, 0.0, 0), 3: (0.9, 1, 0.0, 0), 4: (0.6, 0, 0.0, 0),
    5: (0.3, 0, 0.5, -1), 6: (0.8, 0, 0.0, 1), 7: (0.6, 1, 0.0, 0), 8: (0.85, 1, 0.0, 0),
    9: (0.45, 0, 0.3, 0), 10: (1.0, 1, 0.0, 0),
}
RITMOS = [
    [(0, 1), (1, .5), (1.5, 1.5), (3, 1)], [(0, .5), (.5, .5), (1, 1), (2, .5), (2.5, .5), (3, 1)],
    [(0, 1.5), (1.5, 1.5), (3, 1)], [(0, 2), (2, 1), (3, .5), (3.5, .5)],
]


def escena(buf_b, buf_c, buf_m, buf_p, num, t0, t1):
    bpm = TEMPOS[num - 1]
    beat = 60 / bpm
    dens, hat, trem, octv = CARACTER[num]
    rng = np.random.default_rng(num)
    prog = PROG_SUSPENSO if num == 5 else PROG
    nbarras = int(np.ceil((t1 - t0) / (4 * beat)))
    grado = 4
    for b in range(nbarras):
        tb = t0 + b * 4 * beat
        nombre = prog[b % 4]
        if num == 10 and b == nbarras - 1:
            nombre = "A"
        raiz, acorde = ACORDES[nombre]
        resto = t1 - tb
        # bajo: marcato en 1 y 3, relleno en 2 y 4
        for k, (pos, fuerte) in enumerate([(0, 1), (1, .5), (2, .9), (3, .5)]):
            if pos * beat < resto:
                f = midi(raiz if fuerte > .6 else raiz + (7 if k == 1 else 12))
                poner(buf_b, bajo(f, beat * 0.9), tb + pos * beat, .55 * fuerte)
        # acordes en síncopa 3-3-2
        pos_acorde = (0, 1.5, 3) if num != 5 else (0, 2)
        for pos in pos_acorde:
            if pos * beat < resto:
                poner(buf_c, bandoneon(acorde, beat * (1.2 if num != 5 else 2.0), 0.14 if num != 5 else 0.7, trem),
                      tb + pos * beat, .38)
        # percusión
        for pos in (0, 2):
            if pos * beat < resto:
                poner(buf_p, bombo(), tb + pos * beat, .9 if num != 5 else .6)
        if num != 5:
            for pos in (1, 3):
                if pos * beat < resto:
                    poner(buf_p, redoble(), tb + pos * beat, .35)
        else:
            for pos in (1, 3):
                poner(buf_p, tic(), tb + pos * beat, .5)
        if hat:
            for k in range(8):
                if k * beat / 2 < resto:
                    poner(buf_p, tic(), tb + k * beat / 2, .12 if k % 2 else .2)
        # melodía
        for pos, largo in RITMOS[rng.integers(len(RITMOS))]:
            if pos * beat >= resto or rng.random() > dens:
                continue
            grado = int(np.clip(grado + rng.integers(-2, 3), 0, len(ESCALA) - 1))
            if pos == 0:
                grado = min(range(len(ESCALA)), key=lambda g: min(abs((69 + ESCALA[g]) % 12 - m % 12) for m in acorde) + abs(g - grado) * .3)
            nota = 69 + ESCALA[grado] + 12 * octv
            if num == 10 and b >= nbarras - 1:
                nota = 69 + 12 + (0 if pos == 0 else 4)
            dur = largo * beat * (0.95 if num != 6 else 0.4)
            poner(buf_m, lead(nota, dur, 0.012 if num != 6 else 0.03), tb + pos * beat, .42)


def espectro_pasabajos(x, corte=5200):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / corte) ** 6)
    return np.fft.irfft(X, len(x))


# ---------- efectos ----------
def ruido_filtrado(dur, k):
    n = int(dur * SR)
    return suave(RNG.standard_normal(n), k)


def fx(nombre):
    if nombre == "boing":
        n = int(0.55 * SR); t = t_(n)
        f = 330 + 260 * np.sin(2 * np.pi * 3.2 * t) * np.exp(-t / 0.3)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.25)
    if nombre == "pop":
        n = int(0.14 * SR); t = t_(n)
        return np.sin(2 * np.pi * np.cumsum(700 * np.exp(-t / 0.03) + 180) / SR) * np.exp(-t / 0.04)
    if nombre in ("whoosh", "swish"):
        dur, k = (0.55, 40) if nombre == "whoosh" else (0.3, 14)
        x = ruido_filtrado(dur, k); x *= np.sin(np.linspace(0, np.pi, len(x))) ** 2
        return x / (np.abs(x).max() + 1e-9)
    if nombre == "splash":
        n = int(0.45 * SR); r = RNG.standard_normal(n)
        x = (r - suave(r, 6)) * np.exp(-t_(n) / 0.12)
        return x / (np.abs(x).max() + 1e-9) * .8
    if nombre == "gruñido":
        n = int(0.55 * SR); t = t_(n)
        x = suave(saw(95 - 30 * t, n, 0.04), 20) * (0.6 + 0.4 * np.sin(2 * np.pi * 28 * t)) * np.exp(-t / 0.3)
        return np.tanh(3 * x)
    if nombre == "tada":
        out = np.zeros(int(0.9 * SR))
        for i, m in enumerate((72, 76, 79, 84)):
            poner(out, np.tanh(2 * suave(saw(midi(m), int(0.5 * SR)), 3)) * decay(int(0.5 * SR), 0.2), i * 0.09, .5)
        return out
    if nombre == "crunch":
        out = np.zeros(int(0.3 * SR))
        for i in range(3):
            n = int(0.03 * SR); r = RNG.standard_normal(n)
            poner(out, suave(r, 3) * np.exp(-t_(n) / 0.008), i * 0.045, 1.0)
        return out
    if nombre == "stamp":
        n = int(0.5 * SR); t = t_(n); r = RNG.standard_normal(n)
        return np.sin(2 * np.pi * np.cumsum(120 * np.exp(-t / 0.08) + 40) / SR) * np.exp(-t / 0.15) + .5 * suave(r, 6) * np.exp(-t / 0.02)
    if nombre == "pffff":
        n = int(0.7 * SR); t = t_(n)
        x = suave(saw(75, n, 0.15), 16) * np.exp(-t / 0.4) * (0.6 + 0.4 * np.sin(2 * np.pi * 40 * t))
        return np.tanh(2.5 * x)
    if nombre == "crack":
        n = int(0.6 * SR); t = t_(n); r = RNG.standard_normal(n)
        return (r - suave(r, 3)) * np.exp(-t / 0.05) * .8 + np.sin(2 * np.pi * np.cumsum(90 * np.exp(-t / 0.2) + 35) / SR) * np.exp(-t / 0.25)
    if nombre == "sparkle":
        out = np.zeros(int(0.9 * SR))
        for i in range(7):
            f = RNG.choice([2093, 2637, 3136, 3520, 4186])
            n = int(0.3 * SR)
            poner(out, np.sin(2 * np.pi * f * t_(n)) * np.exp(-t_(n) / 0.08), i * 0.07 + RNG.random() * .03, .35)
        return out
    raise ValueError(nombre)


def main():
    d = cargar()
    mp3 = SALIDA / "episodio-003-completo.mp3"
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp3), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         check=True, capture_output=True).stdout
    voz = np.frombuffer(pcm, dtype=np.float32).astype(np.float64)
    N = len(voz)
    bb, cc, mm, pp = (np.zeros(N) for _ in range(4))
    for i, e in enumerate(d["escenas"], 1):
        escena(bb, cc, mm, pp, i, e["ini_v"], e["fin_v"])
    # la música de una escena no se corta de golpe: el límite lo marca el siguiente compás
    musica = espectro_pasabajos(0.9 * bb + 0.8 * cc + 0.9 * mm) + 0.7 * pp
    musica /= np.abs(musica).max()

    # ducking: la música baja cuando habla la voz y sube en los huecos
    env = suave(np.abs(voz), int(0.03 * SR))
    gate = np.clip(env / (np.percentile(env, 95) * 0.5 + 1e-9), 0, 1)
    gate = suave(gate, int(0.12 * SR))
    musica *= (0.62 - 0.42 * gate)

    sfx = np.zeros(N)
    for esc, off, nombre in SFX:
        e = d["escenas"][esc - 1]
        poner(sfx, fx(nombre), e["ini_v"] + off, 0.30)

    mezcla = voz * 1.0 + musica * 0.55 + sfx
    mezcla = np.tanh(mezcla * 1.1) / np.tanh(1.1)
    mezcla *= 0.89 / np.abs(mezcla).max()
    salida = SALIDA / "episodio-003-mezcla.mp3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ac", "1", "-ar", str(SR), "-i", "-",
                    "-codec:a", "libmp3lame", "-b:a", "160k", str(salida)],
                   input=(mezcla * 32767).astype("<i2").tobytes(), check=True)
    print(f"{salida.name}: {N / SR:.1f} s")


if __name__ == "__main__":
    main()
