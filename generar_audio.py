#!/usr/bin/env python3
"""Genera un MP3 narrado a partir de un guion de texto usando edge-tts.

Uso: python generar_audio.py guiones/pulpo_colorado.txt audios/salida.mp3 [--rate=+0%] [--voz es-PY-MarioNeural]

El guion se divide en bloques separados por líneas en blanco. Entre bloques se
inserta un silencio (--pausa). Un bloque "[pausa N]" fija el silencio siguiente en N segundos.
Requiere: pip install edge-tts, y ffmpeg en el PATH.
"""
import argparse
import asyncio
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import edge_tts
import edge_tts.communicate

# edge-tts solo confía en certifi; si el entorno define un CA propio (proxy corporativo), se suma.
if os.environ.get("SSL_CERT_FILE"):
    edge_tts.communicate._SSL_CTX.load_verify_locations(os.environ["SSL_CERT_FILE"])


async def sintetizar(texto, voz, rate, destino):
    """Sintetiza un bloque y devuelve cuántas palabras pronunció el motor."""
    com = edge_tts.Communicate(texto, voz, rate=rate, boundary="WordBoundary",
                               proxy=os.environ.get("HTTPS_PROXY"))
    palabras = 0
    with open(destino, "wb") as f:
        async for chunk in com.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                palabras += 1
    return palabras


def duracion(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("guion")
    ap.add_argument("salida")
    ap.add_argument("--voz", default="es-PY-MarioNeural")
    ap.add_argument("--rate", default="+0%")
    ap.add_argument("--pausa", type=float, default=0.6)
    args = ap.parse_args()

    bloques = [b.strip() for b in re.split(r"\n\s*\n", Path(args.guion).read_text("utf-8")) if b.strip()]
    partes = []  # ("voz", texto) | ("pausa", segundos)
    for b in bloques:
        m = re.fullmatch(r"\[pausa ([\d.]+)\]", b)
        if m:
            partes.append(("pausa", float(m.group(1))))
        else:
            if partes and partes[-1][0] == "voz":
                partes.append(("pausa", args.pausa))
            partes.append(("voz", b))

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        entradas, filtros, total_pal, total_voz = [], [], 0, 0.0
        for i, (tipo, val) in enumerate(partes):
            if tipo == "voz":
                mp3 = tmp / f"{i:02d}.mp3"
                n = asyncio.run(sintetizar(val, args.voz, args.rate, mp3))
                esperadas = len(re.findall(r"\w+", val))
                d = duracion(mp3)
                total_pal += esperadas
                total_voz += d
                print(f"bloque {i:02d}: {d:5.1f}s  palabras guion={esperadas} motor={n}  «{val[:40]}…»")
                if d < 0.3:
                    sys.exit(f"bloque {i} vacío")
                entradas += ["-i", str(mp3)]
                # recorta solo el silencio final que deja edge-tts para controlar las pausas
                filtros.append(f"[{len(filtros)}:a]aresample=48000,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse[a{len(filtros)}]")
            else:
                entradas += ["-f", "lavfi", "-t", str(val), "-i", "anullsrc=r=48000:cl=mono"]
                filtros.append(f"[{len(filtros)}:a]anull[a{len(filtros)}]")
        n = len(filtros)
        grafo = ";".join(filtros) + ";" + "".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1[out]"
        Path(args.salida).parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-v", "error", *entradas, "-filter_complex", grafo,
                        "-map", "[out]", "-ac", "1", "-ar", "48000", "-b:a", "128k", args.salida], check=True)

    total = duracion(args.salida)
    print(f"\n{args.salida}: {int(total // 60)}:{total % 60:04.1f}  |  {total_pal} palabras  |  "
          f"{total_pal / total_voz * 60:.0f} palabras/min (solo voz)")


if __name__ == "__main__":
    main()
