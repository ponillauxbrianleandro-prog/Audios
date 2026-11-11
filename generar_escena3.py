#!/usr/bin/env python3
"""Genera la narración de la Escena 3: «Los gordos peluzones también tienen corazón».

Requisitos: pip install edge-tts, y ffmpeg/ffprobe en el PATH.
Uso: python3 generar_escena3.py
"""
import asyncio
import os
import subprocess
import sys
import tempfile

import certifi

# En sesiones cloud con proxy TLS hay que confiar en su CA; fuera de ahí no cambia nada.
_CA = os.environ.get("SSL_CERT_FILE")
if _CA and os.path.exists(_CA):
    certifi.where = lambda: _CA

import edge_tts  # noqa: E402  (debe importarse después de ajustar certifi)

VOZ = "es-PY-MarioNeural"  # Mario básico, sin modificar tono ni velocidad
SALIDA = "escena3_peluzones_narracion.mp3"
OBJETIVO_S = 124.0          # duración buscada
MIN_S, MAX_S = 120.0, 160.0  # más de 2:00, menos de 2:40

# (frase, peso de la pausa que le sigue). El peso se escala para llegar a OBJETIVO_S.
FRASES = [
    # Secuencia 1 — La guardería
    ("Pero no todo es pelear con el primo y robar tablas de surf.", 1.0),
    ("Mientras los grandes salen a pescar, los pichones se quedan todos juntos en una "
     "especie de guardería. Y mirá lo que son: gordos peluzones de fábrica. "
     "Ni peinado tienen todavía.", 1.0),
    ("Ese se durmió parado. Ese otro lo empujó. Nadie hizo nada. "
     "Así funciona la guardería.", 2.5),
    # Secuencia 2 — El regreso del padre
    ("Y cuando papá vuelve con la comida, no hay mucho lío: llama, y entre miles de "
     "pelusas iguales, su hijo le reconoce la voz.", 1.0),
    ("Ahí viene. Tropezándose con todos, pidiendo permiso a nadie.", 1.0),
    ("Y sí, lo alimenta pasándole la comida de pico a pico. Un poco asqueroso, "
     "bastante tierno, y el pibe queda todavía más redondo.", 2.5),
    # Secuencia 3 — La pareja
    ("Y estos dos son pareja. Muchos macaroni vuelven cada año a encontrarse con la "
     "misma pareja y al mismo nido.", 1.0),
    ("Mirá cómo se saludan: reverencia, cabeceo y un grito al cielo. Puro romance.", 1.0),
    # La pausa siguiente incluye el «...» con que abre la Secuencia 4.
    ("Con cara de enojados, eso sí. Pero es amor. Te lo juro que es amor.", 4.5),
    # Secuencia 4 — El primer plano final
    ("¿Todavía te parezco un tonto gordo peluzón?", 1.5),
    ("Pensalo bien.", 1.5),
    ("Gordo, capaz. Tonto, jamás.", 0.0),
]


def run(*cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def duracion(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        check=True, capture_output=True, text=True).stdout
    return float(out)


async def sintetizar(texto, destino):
    await edge_tts.Communicate(texto, VOZ).save(destino)


async def main():
    with tempfile.TemporaryDirectory() as tmp:
        mp3s = [os.path.join(tmp, f"f{i:02d}.mp3") for i in range(len(FRASES))]
        await asyncio.gather(*(sintetizar(t, p) for (t, _), p in zip(FRASES, mp3s)))

        # A WAV, recortando el silencio que edge-tts deja al principio y al final.
        wavs = []
        for p in mp3s:
            w = p.replace(".mp3", ".wav")
            recorte = "silenceremove=start_periods=1:start_threshold=-50dB"
            run("ffmpeg", "-y", "-i", p, "-af",
                f"{recorte},areverse,{recorte},areverse", "-ar", "24000", "-ac", "1", w)
            wavs.append(w)

        voz_total = sum(duracion(w) for w in wavs)
        unidad = (OBJETIVO_S - voz_total) / sum(peso for _, peso in FRASES)
        if not 0.8 <= unidad <= 4.5:
            sys.exit(f"Pausa base de {unidad:.2f}s fuera de rango; ajustar OBJETIVO_S.")

        lista = os.path.join(tmp, "lista.txt")
        with open(lista, "w") as f:
            for i, (w, (_, peso)) in enumerate(zip(wavs, FRASES)):
                f.write(f"file '{w}'\n")
                if peso:
                    s = os.path.join(tmp, f"s{i:02d}.wav")
                    run("ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                        "-t", f"{peso * unidad:.3f}", s)
                    f.write(f"file '{s}'\n")

        run("ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lista,
            "-c:a", "libmp3lame", "-b:a", "128k", SALIDA)

    total = duracion(SALIDA)
    print(f"{SALIDA}: {total:.1f}s (voz {voz_total:.1f}s, pausa base {unidad:.2f}s)")
    if not MIN_S < total < MAX_S:
        sys.exit("Duración fuera del rango 2:00–2:40.")


if __name__ == "__main__":
    asyncio.run(main())
