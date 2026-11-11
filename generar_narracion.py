#!/usr/bin/env python3
"""Genera la narración completa de «Los gordos peluzones» (Escenas 1, 2 y 3).

Requisitos: pip install edge-tts, y ffmpeg/ffprobe en el PATH.
Uso: python3 generar_narracion.py
"""
import asyncio
import os
import subprocess
import tempfile

import certifi

# En sesiones cloud con proxy TLS hay que confiar en su CA; fuera de ahí no cambia nada.
_CA = os.environ.get("SSL_CERT_FILE")
if _CA and os.path.exists(_CA):
    certifi.where = lambda: _CA

import edge_tts  # noqa: E402  (debe importarse después de ajustar certifi)

VOZ = "es-PY-MarioNeural"  # Mario básico, sin modificar tono ni velocidad
SALIDA = "gordos_peluzones_narracion.mp3"
PAUSA_FRASE = 0.6   # segundos entre frases de un mismo bloque
PAUSA_BLOQUE = 1.2  # segundos entre bloques / escenas

# Cada lista interna es un bloque del guion. Solo líneas del NARRADOR.
BLOQUES = [
    # ESCENA 1. El pingüino y su primo extravagante
    [
        "Seguramente ya conocés al pingüino. Un gordo rechoncho, con cara de pelotudo "
        "y un elegante traje blanco y negro.",
        "Un auténtico gordo peluzón.",
        "Pero seguramente también conozcas a este carismático amigo.",
        "Es bastante parecido al anterior, aunque tiene un poquito más de pelusa... "
        "y una cara de enojado.",
        "Parece que nuestro amigo tiene algunos problemas de personalidad.",
        "Pero no te dejes engañar por su apariencia. Este pequeño señor tiene bastante "
        "más para ofrecer que un peinado extravagante.",
    ],
    # ESCENA 2. El pingüino que quería surfear
    [
        "Estos pequeños gordos peluzones tienen una alimentación bastante particular. "
        "Como otros pingüinos, se alimentan principalmente de animales marinos, "
        "entre ellos peces, kril y calamares.",
        "Y para conseguir su comida tienen que salir a buscarla. Se meten al agua, "
        "nadan, bucean y persiguen a sus presas.",
        "Aunque, viendo sus expresiones, uno podría pensar que están bastante "
        "orgullosos de sus capturas.",
        "Imaginate recorrer todo el glaciar buscando a otro pingüino para demostrarle "
        "que vos sí sabés cazar.",
        "Y todo esto con esa cara de enojado, como si el pescado le debiera plata.",
        "Aunque, tarde o temprano, el hambre termina ganando. Y nuestro pequeño "
        "presumido recuerda que, después de todo, había salido a buscar comida.",
    ],
    [
        "Y seguramente, si conocés a estos pequeños amigos, también habrás visto "
        "aquella hermosa película en la que un pingüino intenta convertirse en un "
        "surfista profesional.",
        "Una película bastante divertida, aunque...",
    ],
    [
        "Oh, no.",
        "No, no, no, no, no. No hagas eso. No hagas eso. No aquí, no ahora, no así.",
        "¡Mirate! ¡Parecés una bola de pelusa!",
    ],
    # (La línea del camarógrafo va como texto en pantalla: no se narra ni se deja hueco.)
    [
        "Y sí, y sí... ¿¡cómo te vamos a dejar hacer eso!? ¡No, sos un desubicado! "
        "¡Acordate de que te podés lastimar!",
        "Bueno, encima se va enojado.",
    ],
    # ESCENA 3. Los gordos peluzones también tienen corazón
    [  # Secuencia 1 — La guardería
        "Pero no todo es pelear con el primo y robar tablas de surf.",
        "Mientras los grandes salen a pescar, los pichones se quedan todos juntos en "
        "una especie de guardería. Y mirá lo que son: gordos peluzones de fábrica. "
        "Ni peinado tienen todavía.",
        "Ese se durmió parado. Ese otro lo empujó. Nadie hizo nada. "
        "Así funciona la guardería.",
    ],
    [  # Secuencia 2 — El regreso del padre
        "Y cuando papá vuelve con la comida, no hay mucho lío: llama, y entre miles "
        "de pelusas iguales, su hijo le reconoce la voz.",
        "Ahí viene. Tropezándose con todos, pidiendo permiso a nadie.",
        "Y sí, lo alimenta pasándole la comida de pico a pico. Un poco asqueroso, "
        "bastante tierno, y el pibe queda todavía más redondo.",
    ],
    [  # Secuencia 3 — La pareja
        "Y estos dos son pareja. Muchos macaroni vuelven cada año a encontrarse con "
        "la misma pareja y al mismo nido.",
        "Mirá cómo se saludan: reverencia, cabeceo y un grito al cielo. Puro romance.",
        "Con cara de enojados, eso sí. Pero es amor. Te lo juro que es amor.",
    ],
    [  # Secuencia 4 — El primer plano final
        "¿Todavía te parezco un tonto gordo peluzón?",
        "Pensalo bien.",
        "Gordo, capaz. Tonto, jamás.",
    ],
]


def run(*cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def duracion(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        check=True, capture_output=True, text=True).stdout
    return float(out)


async def main():
    # (texto, pausa que le sigue)
    frases = []
    for bloque in BLOQUES:
        for i, texto in enumerate(bloque):
            frases.append((texto, PAUSA_FRASE if i < len(bloque) - 1 else PAUSA_BLOQUE))
    frases[-1] = (frases[-1][0], 0.0)

    with tempfile.TemporaryDirectory() as tmp:
        mp3s = [os.path.join(tmp, f"f{i:02d}.mp3") for i in range(len(frases))]
        limite = asyncio.Semaphore(6)

        async def sintetizar(texto, destino):
            async with limite:
                await edge_tts.Communicate(texto, VOZ).save(destino)

        await asyncio.gather(*(sintetizar(t, p) for (t, _), p in zip(frases, mp3s)))

        silencios = {}
        for p in (PAUSA_FRASE, PAUSA_BLOQUE):
            silencios[p] = os.path.join(tmp, f"sil_{p}.wav")
            run("ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                "-t", str(p), silencios[p])

        lista = os.path.join(tmp, "lista.txt")
        recorte = "silenceremove=start_periods=1:start_threshold=-50dB"
        with open(lista, "w") as f:
            for p, (_, pausa) in zip(mp3s, frases):
                # A WAV, recortando el silencio que edge-tts deja al principio y al final.
                w = p.replace(".mp3", ".wav")
                run("ffmpeg", "-y", "-i", p, "-af",
                    f"{recorte},areverse,{recorte},areverse", "-ar", "24000", "-ac", "1", w)
                f.write(f"file '{w}'\n")
                if pausa:
                    f.write(f"file '{silencios[pausa]}'\n")

        run("ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lista,
            "-c:a", "libmp3lame", "-b:a", "128k", SALIDA)

    print(f"{SALIDA}: {duracion(SALIDA):.1f}s, {len(frases)} frases")


if __name__ == "__main__":
    asyncio.run(main())
