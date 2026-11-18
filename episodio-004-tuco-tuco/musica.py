#!/usr/bin/env python3
"""Sintetiza un tango limpio y lo mezcla con la voz.

Sin eco, sin reverb y sin distorsión: solo ondas sintéticas con envolventes suaves.
La energía cambia por escena (INTENSIDAD) para que el fondo sea irregular según lo que se muestra.
La música baja sola cuando habla la voz (sidechaincompress, que no agrega ningún efecto al sonido).

Uso: python3 musica.py   (requiere audio/episodio-004-voz.wav y audio/escenas.json)
Salida: audio/musica.wav, audio/episodio-004-final.mp3
"""
import json
import subprocess
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
SALIDA = AQUI / "audio"
SR = 44100
BPM = 116
# Progresión en re menor, un compás por acorde (fundamental, tercera, quinta, y bajo en Hz).
ACORDES = [
    ("Dm", [293.66, 349.23, 440.00], 73.42),
    ("A7", [277.18, 392.00, 440.00], 55.00),
    ("Dm", [293.66, 349.23, 440.00], 73.42),
    ("Gm", [293.66, 349.23, 466.16], 98.00),
    ("A7", [277.18, 392.00, 440.00], 55.00),
    ("Dm", [293.66, 349.23, 440.00], 73.42),
]
# Melodía de bandoneón (nota Hz, duración en pulsos) que acompaña cada acorde.
MELODIA = [
    [(587.33, 1.5), (523.25, 0.5), (440.00, 2)],
    [(554.37, 1), (587.33, 1), (659.25, 2)],
    [(698.46, 1.5), (659.25, 0.5), (587.33, 2)],
    [(466.16, 1), (587.33, 1), (698.46, 2)],
    [(659.25, 1), (554.37, 1), (440.00, 2)],
    [(587.33, 3), (440.00, 1)],
]
# Por escena: (bajo, acordes, melodía), niveles 0 a 1. Alto al inicio, más calmo en 8.
INTENSIDAD = {
    1: (1.0, 1.0, 1.0),   # insulto: tango fuerte de golpe
    2: (0.9, 0.9, 0.8),
    3: (1.0, 0.9, 0.7),
    4: (0.5, 0.6, 0.5),
    5: (0.9, 1.0, 0.8),
    6: (0.3, 0.4, 0.4),   # el nombre: baja
    7: (0.4, 0.5, 0.3),
    8: (0.7, 0.8, 0.6),
    9: (0.0, 0.1, 0.45),  # refutación: casi solo bandoneón
    10: (1.0, 1.0, 1.0),  # cierre
}


def envolvente(n, ataque, caida):
    t = np.arange(n) / SR
    return np.minimum(1, t / ataque) * np.exp(-t / caida)


def nota_bajo(f, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    onda = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t)
    return onda * envolvente(n, 0.005, 0.30)


def acorde_seco(freqs, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    onda = sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t) for f in freqs)
    return onda * envolvente(n, 0.004, 0.11) / len(freqs)


def nota_bandoneon(f, dur):
    """Diente de sierra suave (armónicos hasta el 8) con vibrato leve y envolvente de fuelle."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    fase = 2 * np.pi * f * t + 0.012 * np.sin(2 * np.pi * 5.5 * t)
    onda = sum(np.sin(k * fase) / k for k in range(1, 9))
    sube = np.minimum(1, t / 0.05)
    baja = np.minimum(1, (dur - t) / 0.08)
    return onda * sube * np.clip(baja, 0, 1) * (0.8 + 0.2 * np.sin(2 * np.pi * 2 * t))


def poner(destino, sonido, inicio, ganancia):
    i = int(inicio * SR)
    if i >= len(destino):
        return
    corte = min(len(sonido), len(destino) - i)
    destino[i:i + corte] += sonido[:corte] * ganancia


def sintetizar(duracion, escenas):
    pulso = 60 / BPM
    compas = 4 * pulso
    pista = np.zeros(int(duracion * SR))

    def nivel(t, capa):
        for e in escenas:
            if e["inicio"] - 0.3 <= t < e["fin"] + 0.3:
                return INTENSIDAD[e["escena"]][capa]
        return INTENSIDAD[escenas[-1]["escena"]][capa]

    c = 0
    while c * compas < duracion:
        _, freqs, bajo = ACORDES[c % len(ACORDES)]
        base = c * compas
        for b in range(4):  # marcato: bajo en 1 y 3, acordes secos en 2 y 4
            t = base + b * pulso
            if b in (0, 2):
                poner(pista, nota_bajo(bajo, pulso * 1.8), t, 0.55 * nivel(t, 0))
            else:
                poner(pista, acorde_seco(freqs, pulso), t, 0.45 * nivel(t, 1))
        t = base
        for f, p in MELODIA[c % len(MELODIA)]:
            poner(pista, nota_bandoneon(f, p * pulso * 0.95), t, 0.22 * nivel(t, 2))
            t += p * pulso
        c += 1

    pista /= max(1e-9, np.abs(pista).max())
    return (pista * 0.8 * 32767).astype("<i2")


def main():
    escenas = json.loads((SALIDA / "escenas.json").read_text())
    voz = SALIDA / "episodio-004-voz.wav"
    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(voz)],
        capture_output=True, text=True, check=True).stdout)
    pista = sintetizar(dur, escenas)
    musica = SALIDA / "musica.wav"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ac", "1", "-ar", str(SR), "-i", "-", str(musica)],
        input=pista.tobytes(), check=True)
    # La música a -14 dB y se agacha otros ~10 dB cuando habla la voz; luego loudnorm sin clipping.
    filtro = (
        "[0:a]aresample=44100,asplit=2[v][vsc];"
        "[1:a]volume=-14dB[m];"
        "[m][vsc]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=300[md];"
        "[v][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[o]"
    )
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(voz), "-i", str(musica),
         "-filter_complex", filtro, "-map", "[o]", "-codec:a", "libmp3lame", "-b:a", "192k",
         str(SALIDA / "episodio-004-final.mp3")],
        check=True)
    print("Listo:", SALIDA / "episodio-004-final.mp3")


if __name__ == "__main__":
    main()
