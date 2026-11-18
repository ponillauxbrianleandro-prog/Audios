#!/usr/bin/env python3
"""Mezcla la narración con el tango (cuarteto de stems) del episodio 004.

Sin eco, sin reverberación y sin distorsión: solo ganancias por instrumento y escena, la música que baja sola
mientras habla la voz (envolvente de la voz, no un efecto) y normalización de volumen.

Requiere: musica/stems/{bandoneon,violin,piano,contrabajo}.mp3 (python3 musica/generar_tango.py --corto)
y audio/episodio-004-voz.wav + audio/escenas.json (generar_audio.py).
Salida: audio/episodio-004-final.mp3 (voz + tango) y audio/tango-fondo.mp3 (solo la música con su dinámica).
Uso: python3 musica.py
"""
import json
import subprocess
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
AUDIO = AQUI / "audio"
STEMS = AQUI / "musica" / "stems"
SR = 44100
INSTR = ["bandoneon", "violin", "piano", "contrabajo"]

# Ganancia por escena (0 a 1): fuerte y completo al abrir y cerrar, íntimo en el nombre y la soledad,
# casi solo bandoneón en la refutación.
GANANCIA = {
    1: (1.00, 0.85, 1.00, 1.00),
    2: (1.00, 0.65, 1.00, 1.00),
    3: (0.85, 0.70, 1.00, 1.00),
    4: (0.65, 0.45, 0.85, 0.95),
    5: (1.00, 0.80, 1.00, 1.00),
    6: (0.55, 0.00, 0.70, 0.85),
    7: (0.45, 0.35, 0.65, 0.75),
    8: (0.85, 0.65, 0.95, 0.95),
    9: (0.90, 0.50, 0.30, 0.20),
    10: (1.00, 1.00, 1.00, 1.00),
}
NIVEL_MUSICA = 0.72        # nivel base de la música respecto de la voz
PROFUNDIDAD_DUCK = 0.55    # cuánto baja la música mientras habla la voz
FUNDIDO = 1.0              # s de transición entre escenas


def leer(path, canales):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", str(canales), "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32)
    return x.reshape(-1, canales) if canales > 1 else x


def ajustar_tempo(x, factor):
    """Cambia la duración sin cambiar el tono (atempo de ffmpeg; factor = velocidad)."""
    if abs(factor - 1.0) < 0.002:
        return x
    raw = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-i", "-", "-af", f"atempo={factor:.5f}",
                          "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], input=x.astype(np.float32).tobytes(), capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)


def curva_ganancia(escenas, n, idx):
    """Ganancia de un instrumento a lo largo del tiempo, con fundidos suaves entre escenas."""
    g = np.zeros(n, np.float32)
    puntos_t, puntos_g = [0.0], [GANANCIA[escenas[0]["escena"]][idx]]
    for e in escenas:
        v = GANANCIA[e["escena"]][idx]
        puntos_t += [max(0.0, e["inicio"] - FUNDIDO / 2), e["inicio"] + FUNDIDO / 2]
        puntos_g += [puntos_g[-1], v]
    puntos_t.append(n / SR)
    puntos_g.append(puntos_g[-1])
    return np.interp(np.arange(n) / SR, puntos_t, puntos_g).astype(np.float32)


def envolvente_voz(v):
    """Nivel suave de la voz (0 a 1): ataque rápido, caída lenta."""
    a = np.abs(v)
    paso = SR // 100
    m = np.maximum.reduceat(a, np.arange(0, len(a), paso))
    env = np.zeros_like(m)
    for i in range(len(m)):
        prev = env[i - 1] if i else 0.0
        env[i] = m[i] if m[i] > prev else prev * 0.965 + m[i] * 0.035
    env = np.clip(env / max(1e-6, np.percentile(env, 95)), 0, 1)
    return np.interp(np.arange(len(a)), np.arange(len(m)) * paso, env).astype(np.float32)


def main():
    escenas = json.loads((AUDIO / "escenas.json").read_text())
    voz = leer(AUDIO / "episodio-004-voz.wav", 1)
    n = len(voz)
    T = n / SR
    stems = {i: leer(STEMS / f"{i}.mp3", 2) for i in INSTR}
    largo = max(len(s) for s in stems.values()) / SR
    factor = float(np.clip(largo / T, 0.92, 1.08))          # el acorde final cae al final del video
    print(f"tango {largo:.1f} s, voz {T:.1f} s, tempo x{factor:.3f}")
    musica = np.zeros((n, 2), np.float32)
    for k, inst in enumerate(INSTR):
        s = ajustar_tempo(stems[inst], factor)
        s = np.pad(s, ((0, max(0, n - len(s))), (0, 0)))[:n]
        musica += s * curva_ganancia(escenas, n, k)[:, None]
    musica /= max(1e-6, np.abs(musica).max())
    # fundido de salida corto sobre el último acorde (evita el corte brusco)
    fo = int(0.9 * SR)
    musica[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)[:, None]
    solo = musica.copy()
    duck = 1.0 - PROFUNDIDAD_DUCK * envolvente_voz(voz)
    mezcla = musica * NIVEL_MUSICA * duck[:, None] + np.repeat(voz[:, None], 2, 1) * 0.9

    def guardar(x, destino, normalizar):
        filtro = "loudnorm=I=-16:TP=-1.5:LRA=11" if normalizar else "alimiter=limit=0.9"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-i", "-", "-af", filtro,
                        "-codec:a", "libmp3lame", "-b:a", "192k", str(destino)], input=x.astype(np.float32).tobytes(), check=True)

    guardar(mezcla, AUDIO / "episodio-004-final.mp3", True)
    guardar(solo * 0.8, AUDIO / "tango-fondo.mp3", False)
    print("Listo:", AUDIO / "episodio-004-final.mp3")


if __name__ == "__main__":
    main()
