#!/usr/bin/env python3
"""Genera la narración del episodio a partir de guion.md.

Requiere: pip install edge-tts, y ffmpeg en el PATH.
Uso: python3 generar_audio.py
"""
import asyncio
import math
import os
import re
import struct
import subprocess
import tempfile
from pathlib import Path

import edge_tts
import edge_tts.communicate

# Detrás de un proxy con certificado propio, edge-tts solo confía en certifi;
# si el entorno define SSL_CERT_FILE, se suma ese certificado.
if os.environ.get("SSL_CERT_FILE"):
    edge_tts.communicate._SSL_CTX.load_verify_locations(os.environ["SSL_CERT_FILE"])

VOZ = "es-PY-MarioNeural"
FRECUENCIA = 24000  # Hz, mono, 16 bits
RITMO = "-10%"  # velocidad general de la voz
RITMO_APERTURA = "-40%"  # primera frase del episodio
PAUSA_PARRAFO = 0.35
PAUSA_ESCENA = 0.85
PAUSA_APERTURA = 1.2  # silencio después de la primera frase
SILENCIO_INICIAL = 0.4  # antes de la primera frase, para que no se corte
UMBRAL_VOZ = 30  # amplitud (de 32768) a partir de la cual hay voz
MARGEN_VOZ = 0.08  # segundos que se conservan antes y después de la voz

AQUI = Path(__file__).resolve().parent
SALIDA = AQUI / "audio"


def leer_guion():
    """Devuelve [(titulo, [parrafos])] con lo que hay entre '## ESCENA' y '## Fuentes'."""
    escenas = []
    for linea in (AQUI / "guion.md").read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if linea.startswith("## "):
            if not linea.startswith("## ESCENA"):
                if escenas:
                    break
                continue
            escenas.append((linea[3:], []))
        elif linea and escenas:
            escenas[-1][1].append(linea)
    return escenas


async def sintetizar(texto, destino, ritmo):
    for intento in range(4):
        try:
            await edge_tts.Communicate(texto, VOZ, rate=ritmo).save(str(destino))
            return
        except Exception:
            if intento == 3:
                raise
            await asyncio.sleep(2 ** (intento + 1))


def a_pcm(mp3):
    """Decodifica a PCM y recorta el silencio de los extremos, dejando un margen."""
    pcm = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(mp3),
         "-f", "s16le", "-ac", "1", "-ar", str(FRECUENCIA), "-"],
        check=True, capture_output=True,
    ).stdout
    muestras = struct.unpack(f"<{len(pcm) // 2}h", pcm)
    con_voz = [i for i, v in enumerate(muestras) if abs(v) > UMBRAL_VOZ]
    margen = int(FRECUENCIA * MARGEN_VOZ)
    inicio = max(0, con_voz[0] - margen)
    fin = min(len(muestras), con_voz[-1] + margen)
    return pcm[inicio * 2:fin * 2]


def silencio(segundos):
    return b"\x00\x00" * int(FRECUENCIA * segundos)


def jingle():
    """Arpegio ascendente propio para 'misión secundaria completada'."""
    notas = [(659.25, 0.11), (783.99, 0.11), (987.77, 0.11), (1318.51, 0.55)]
    muestras = []
    for frecuencia, duracion in notas:
        total = int(FRECUENCIA * duracion)
        for i in range(total):
            t = i / FRECUENCIA
            envolvente = min(1.0, i / 120) * math.exp(-3.5 * t / duracion)
            onda = math.sin(2 * math.pi * frecuencia * t) + 0.3 * math.sin(4 * math.pi * frecuencia * t)
            muestras.append(int(9000 * envolvente * onda))
    return struct.pack(f"<{len(muestras)}h", *muestras)


def guardar_mp3(pcm, destino):
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ac", "1", "-ar", str(FRECUENCIA),
         "-i", "-", "-codec:a", "libmp3lame", "-b:a", "128k", str(destino)],
        input=pcm, check=True,
    )


def marca(segundos):
    ms = round(segundos * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def guardar_srt(cues, destino):
    bloques = [
        f"{n}\n{marca(inicio)} --> {marca(fin)}\n{texto}\n"
        for n, (inicio, fin, texto) in enumerate(cues, 1)
    ]
    destino.write_text("\n".join(bloques), encoding="utf-8")


async def main():
    SALIDA.mkdir(exist_ok=True)
    escenas = leer_guion()
    completo, cues_completo = silencio(SILENCIO_INICIAL), []

    with tempfile.TemporaryDirectory() as tmp:
        for numero, (titulo, parrafos) in enumerate(escenas, 1):
            pcm, cues = b"", []
            for i, texto in enumerate(parrafos):
                mp3 = Path(tmp) / f"{numero}-{i}.mp3"
                apertura = numero == 1 and i == 0
                await sintetizar(texto, mp3, RITMO_APERTURA if apertura else RITMO)
                voz = a_pcm(mp3)
                if pcm:
                    pcm += silencio(PAUSA_APERTURA if numero == 1 and i == 1 else PAUSA_PARRAFO)
                inicio = len(pcm) / 2 / FRECUENCIA
                pcm += voz
                cues.append((inicio, len(pcm) / 2 / FRECUENCIA, texto))
            if numero == len(escenas):
                pcm += silencio(0.7) + jingle() + silencio(0.4)

            guardar_mp3(pcm, SALIDA / f"escena-{numero}.mp3")
            guardar_srt(cues, SALIDA / f"escena-{numero}.srt")

            if numero > 1:
                completo += silencio(PAUSA_ESCENA)
            base = len(completo) / 2 / FRECUENCIA
            cues_completo += [(base + a, base + b, t) for a, b, t in cues]
            completo += pcm
            print(f"{titulo}: {len(pcm) / 2 / FRECUENCIA:.1f} s")

    guardar_mp3(completo, SALIDA / "episodio-001-completo.mp3")
    guardar_srt(cues_completo, SALIDA / "episodio-001-completo.srt")
    print(f"Total: {len(completo) / 2 / FRECUENCIA:.1f} s")


if __name__ == "__main__":
    asyncio.run(main())
