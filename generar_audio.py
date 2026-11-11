#!/usr/bin/env python3
"""Genera el audio del guión "Gato del pajonal" con la voz Mario (edge-tts).

Requiere: pip install edge-tts, y ffmpeg/ffprobe en el PATH.
Uso: python3 generar_audio.py
"""
import asyncio
import math
import os
import subprocess
import tempfile
from pathlib import Path

import edge_tts

# Si el entorno usa un proxy HTTPS con su propia CA (SSL_CERT_FILE), se la
# agregamos al contexto TLS de edge-tts, que por defecto solo usa certifi.
if os.environ.get("SSL_CERT_FILE"):
    edge_tts.communicate._SSL_CTX.load_verify_locations(os.environ["SSL_CERT_FILE"])
PROXY = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")

VOZ = "es-PY-MarioNeural"
SALIDA = Path(__file__).with_name("gato_del_pajonal_mario.mp3")
DURACION_TOTAL = 95.0  # 1:35
MARGEN = 0.4  # silencio mínimo entre bloques (s)
RATE_MAX = 25  # no acelerar más que +25 %

# (inicio en segundos, texto hablado)
BLOQUES = [
    (0, "Eres un gato callejero. Gordo, despeinado y con cara de que te echaron "
        "de una casa. ¿Que no? Sentate, que te explico."),
    (8, "Arranquemos por la panza, gordo. Pesás más o menos lo que un gato de casa "
        "bien comido, pero vos no comés de un plato. "
        "¿Tu menú? Cuises, tuco-tucos, ratones de campo. Si se puede, una perdiz o "
        "unos huevos, y algún lagarto de postre. "
        "Cazás al atardecer y de noche, agazapado entre los pastos, quieto, quieto… "
        "y ¡zas! "
        "Y no, gordo: a vos no te sirve nadie la comida."),
    (30, "¿Y ese pelo? ¡Pelusón salvaje! "
         "No es para hacerte el lindo. En la estepa el viento te corta la cara y el "
         "frío no perdona, así que ese pelo largo y tupido es tu campera. "
         "El color gris pardo te hace desaparecer en los pajonales. De ahí viene tu "
         "nombre. "
         "Encima tenés rayas oscuras en las patas, anillos en la cola y líneas en "
         "los cachetes. "
         "Sos de la familia de los felinos, del grupo Leopardus. Tus primos son el "
         "gato montés, el gato andino, el ocelote y la huiña. "
         "Hay quien te dice lince chubutense, pero ni ahí: en Sudamérica no hay "
         "linces. Vos sos otra cosa."),
    (58, "Y lo mejor es que casi nadie te vio nunca. Hay gente que vive toda la "
         "vida en la Patagonia sin cruzarse con uno. "
         "Andás solo y en silencio, y los científicos te siguen con cámaras "
         "escondidas. "
         "Pero estás casi amenazado: se achica tu hábitat, y te persiguen los "
         "perros y los autos."),
    (75, "¿Gato callejero? Nunca tuviste calle, tenés toda la estepa. "
         "¿Despeinado? Es tu abrigo contra el viento patagónico. "
         "¿Gordo? Ese peluchón es puro cazador. "
         "¿Todavía querés decirme gato callejero? Pensalo bien. "
         "Eres un gato del pajonal: salvaje, patagónico… y nadie, nunca, te puso "
         "un collar."),
]


def duracion(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout
    return float(out)


async def sintetizar(texto: str, rate: int, destino: Path) -> float:
    crudo = destino.with_suffix(".crudo.mp3")
    await edge_tts.Communicate(texto, VOZ, rate=f"{rate:+d}%",
                               proxy=PROXY).save(str(crudo))
    # Recorta el silencio que edge-tts deja al principio y al final.
    recorte = "silenceremove=start_periods=1:start_threshold=-45dB"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(crudo), "-af",
         f"{recorte},areverse,{recorte},areverse", str(destino)],
        check=True,
    )
    return duracion(destino)


async def bloque_ajustado(texto: str, ventana: float, destino: Path):
    """Sintetiza y acelera lo justo para que el bloque entre en su ventana."""
    rate = 0
    dur = await sintetizar(texto, rate, destino)
    for _ in range(3):
        if dur <= ventana or rate >= RATE_MAX:
            break
        rate = min(RATE_MAX, math.ceil(((1 + rate / 100) * dur / ventana - 1) * 100) + 1)
        dur = await sintetizar(texto, rate, destino)
    return rate, dur


async def main():
    tmp = Path(tempfile.mkdtemp(prefix="gato_"))
    inicios = [b[0] for b in BLOQUES] + [DURACION_TOTAL]
    piezas = []  # (inicio real, archivo)
    cursor = 0.0
    for i, (marca, texto) in enumerate(BLOQUES):
        ventana = inicios[i + 1] - marca - MARGEN
        archivo = tmp / f"bloque{i}.wav"
        rate, dur = await bloque_ajustado(texto, ventana, archivo)
        inicio = max(float(marca), cursor)
        cursor = inicio + dur + MARGEN
        piezas.append((inicio, archivo))
        print(f"bloque {i}: marca {marca:>2}s  inicio {inicio:6.2f}s  "
              f"dura {dur:5.2f}s (ventana {ventana:.1f}s)  rate {rate:+d}%")

    cmd = ["ffmpeg", "-y", "-v", "error"]
    for _, archivo in piezas:
        cmd += ["-i", str(archivo)]
    filtros = [f"[{i}:a]adelay={int(ini * 1000)}:all=1[a{i}]"
               for i, (ini, _) in enumerate(piezas)]
    etiquetas = "".join(f"[a{i}]" for i in range(len(piezas)))
    filtros.append(f"{etiquetas}amix=inputs={len(piezas)}:normalize=0[out]")
    cmd += ["-filter_complex", ";".join(filtros), "-map", "[out]",
            "-ar", "44100", "-ac", "1", "-b:a", "128k", str(SALIDA)]
    subprocess.run(cmd, check=True)
    print(f"listo: {SALIDA.name}  ({duracion(SALIDA):.2f}s)")


if __name__ == "__main__":
    asyncio.run(main())
