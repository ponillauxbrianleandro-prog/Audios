#!/usr/bin/env python3
"""Genera la narración de cada short a partir de guion.md.

Requiere: pip install edge-tts, y ffmpeg en el PATH.
Salida: audio/short-N.mp3, audio/short-N.srt y audio/short-N.json (tiempos de cada línea).
"""
import asyncio
import json
import os
import struct
import subprocess
import tempfile
from pathlib import Path

import edge_tts
import edge_tts.communicate

if os.environ.get("SSL_CERT_FILE"):
    edge_tts.communicate._SSL_CTX.load_verify_locations(os.environ["SSL_CERT_FILE"])

VOZ = "es-AR-TomasNeural"
RITMO = "-5%"
FRECUENCIA = 24000
PAUSA = 0.28
SILENCIO_INICIAL = 0.5
SILENCIO_FINAL = 0.7
UMBRAL_VOZ = 30
MARGEN_VOZ = 0.06

AQUI = Path(__file__).resolve().parent
SALIDA = AQUI / "audio"


def leer_guion():
    shorts = []
    for linea in (AQUI / "guion.md").read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if linea.startswith("## SHORT"):
            shorts.append((linea[3:], []))
        elif linea and not linea.startswith("#") and shorts:
            shorts[-1][1].append(linea)
    return shorts


async def sintetizar(texto, destino):
    for intento in range(4):
        try:
            await edge_tts.Communicate(texto, VOZ, rate=RITMO).save(str(destino))
            return
        except Exception:
            if intento == 3:
                raise
            await asyncio.sleep(2 ** (intento + 1))


def a_pcm(mp3):
    pcm = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(mp3), "-f", "s16le", "-ac", "1", "-ar", str(FRECUENCIA), "-"],
        check=True, capture_output=True,
    ).stdout
    m = struct.unpack(f"<{len(pcm) // 2}h", pcm)
    voz = [i for i, v in enumerate(m) if abs(v) > UMBRAL_VOZ]
    margen = int(FRECUENCIA * MARGEN_VOZ)
    return pcm[max(0, voz[0] - margen) * 2:min(len(m), voz[-1] + margen) * 2]


def silencio(s):
    return b"\x00\x00" * int(FRECUENCIA * s)


def marca(s):
    ms = round(s * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


async def main():
    SALIDA.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for n, (titulo, lineas) in enumerate(leer_guion(), 1):
            pcm, cues = silencio(SILENCIO_INICIAL), []
            for i, texto in enumerate(lineas):
                mp3 = Path(tmp) / f"{n}-{i}.mp3"
                await sintetizar(texto, mp3)
                if i:
                    pcm += silencio(PAUSA)
                ini = len(pcm) / 2 / FRECUENCIA
                pcm += a_pcm(mp3)
                cues.append({"inicio": ini, "fin": len(pcm) / 2 / FRECUENCIA, "texto": texto})
            pcm += silencio(SILENCIO_FINAL)
            subprocess.run(
                ["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ac", "1", "-ar", str(FRECUENCIA), "-i", "-",
                 "-codec:a", "libmp3lame", "-b:a", "128k", str(SALIDA / f"short-{n}.mp3")],
                input=pcm, check=True)
            dur = len(pcm) / 2 / FRECUENCIA
            (SALIDA / f"short-{n}.json").write_text(
                json.dumps({"titulo": titulo, "duracion": dur, "cues": cues}, ensure_ascii=False, indent=1),
                encoding="utf-8")
            (SALIDA / f"short-{n}.srt").write_text("\n".join(
                f"{k}\n{marca(c['inicio'])} --> {marca(c['fin'])}\n{c['texto']}\n" for k, c in enumerate(cues, 1)),
                encoding="utf-8")
            print(f"{titulo}: {dur:.1f} s")


if __name__ == "__main__":
    asyncio.run(main())
