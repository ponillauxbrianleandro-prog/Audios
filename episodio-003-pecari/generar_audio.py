#!/usr/bin/env python3
"""Genera la narración del episodio 003 a partir de guion.md, con la voz clonada.

Voz: Qwen3-TTS 0.6B Base clonando el audio de referencia (REFERENCIA).
Se ejecuta con el entorno de voice_ai:
    voice_ai/.venv/bin/python episodio-003-pecari/generar_audio.py [--rapido]
Salida en audio/: escena-N.wav/.srt, episodio-003-voz.wav/.srt y escenas.json (tiempos por escena).
La voz queda limpia: solo se recortan silencios, se acelera un poco (atempo) y se normaliza el pico.
No se aplica eco, reverb ni distorsión.
"""
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
SALIDA = AQUI / "audio"
MODELO = RAIZ / "voice_ai" / "models" / "Qwen3-TTS-12Hz-0.6B-Base"
REFERENCIA = AQUI / "referencia" / "voz-referencia.wav"  # 24 kHz mono, convertido del .opus original

FRECUENCIA = 24000  # Hz, mono, 16 bits
VELOCIDAD = 1.04 # atempo: más energía sin cambiar el tono
PAUSA_PARRAFO = 0.30
PAUSA_ESCENA = 0.60
SILENCIO_INICIAL = 0.3
UMBRAL_VOZ = 300  # amplitud (de 32768) a partir de la cual hay voz
MARGEN_VOZ = 0.06
PICO = 0.85  # pico máximo normalizado (sin clipping)


def leer_guion():
    """Devuelve [(titulo, [parrafos])] con la narración entre '## ESCENA' y '## Notas'.

    Las líneas que empiezan con '>' son notas de producción y se ignoran.
    """
    escenas = []
    for linea in (AQUI / "guion.md").read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if linea.startswith("## "):
            if not linea.startswith("## ESCENA"):
                if escenas:
                    break
                continue
            escenas.append((linea[3:], []))
        elif linea and not linea.startswith(">") and escenas:
            escenas[-1][1].append(linea)
    return escenas


class Voz:
    def __init__(self):
        import torch
        from qwen_tts import Qwen3TTSModel

        torch.set_num_threads(4)
        self.modelo = Qwen3TTSModel.from_pretrained(
            str(MODELO), device_map="cpu", dtype=torch.float32
        )
        self.prompt = self.modelo.create_voice_clone_prompt(
            ref_audio=str(REFERENCIA), ref_text=None, x_vector_only_mode=True
        )

    def sintetizar(self, texto):
        """Devuelve PCM s16le mono a FRECUENCIA Hz."""
        import numpy as np

        # El códec va a 12 tokens/s y se habla ~15 caracteres/s: tope = 2x lo esperado, para que
        # una frase que no emite el fin de audio no corra 170 s (el tope por defecto es 2048).
        tope = int(len(texto) / 15 * 12 * 2) + 24
        mejor = None
        for _ in range(3):
            wavs, sr = self.modelo.generate_voice_clone(
                text=texto, language="Spanish", voice_clone_prompt=self.prompt, max_new_tokens=tope
            )
            x = np.asarray(wavs[0], dtype=np.float32)
            if mejor is None or len(x) < len(mejor):
                mejor = x
            if len(x) / sr < tope / 12 * 0.9:  # terminó solo, sin chocar con el tope
                break
        x = mejor
        pcm = (np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()
        if sr != FRECUENCIA:
            pcm = ffmpeg_pcm(pcm, sr, FRECUENCIA)
        return pcm


def ffmpeg_pcm(pcm, sr_in, sr_out, filtro=None):
    cmd = ["ffmpeg", "-v", "error", "-f", "s16le", "-ac", "1", "-ar", str(sr_in), "-i", "-"]
    if filtro:
        cmd += ["-af", filtro]
    cmd += ["-f", "s16le", "-ac", "1", "-ar", str(sr_out), "-"]
    return subprocess.run(cmd, input=pcm, check=True, capture_output=True).stdout


def limpiar(pcm):
    """Acelera apenas, recorta silencios de los extremos y normaliza el pico."""
    pcm = ffmpeg_pcm(pcm, FRECUENCIA, FRECUENCIA, f"atempo={VELOCIDAD}")
    muestras = struct.unpack(f"<{len(pcm) // 2}h", pcm)
    con_voz = [i for i, v in enumerate(muestras) if abs(v) > UMBRAL_VOZ]
    margen = int(FRECUENCIA * MARGEN_VOZ)
    inicio = max(0, con_voz[0] - margen)
    fin = min(len(muestras), con_voz[-1] + margen)
    tramo = muestras[inicio:fin]
    pico = max(1, max(abs(v) for v in tramo))
    ganancia = PICO * 32767 / pico
    return struct.pack(f"<{len(tramo)}h", *(int(v * ganancia) for v in tramo))


def silencio(segundos):
    return b"\x00\x00" * int(FRECUENCIA * segundos)


def guardar_wav(pcm, destino):
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ac", "1", "-ar", str(FRECUENCIA),
         "-i", "-", str(destino)],
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


def main():
    SALIDA.mkdir(exist_ok=True)
    voz = Voz()
    completo, cues_completo, tiempos = silencio(SILENCIO_INICIAL), [], []

    for numero, (titulo, parrafos) in enumerate(leer_guion(), 1):
        pcm, cues = b"", []
        for texto in parrafos:
            # Caché por texto: si el guion no cambió esa frase, no se vuelve a sintetizar.
            clave = SALIDA / "cache" / (hashlib.sha1(texto.encode()).hexdigest()[:16] + ".pcm")
            if clave.exists():
                frase = clave.read_bytes()
            else:
                frase = limpiar(voz.sintetizar(texto))
                clave.parent.mkdir(exist_ok=True)
                clave.write_bytes(frase)
            print(f"  · {len(frase) / 2 / FRECUENCIA:.1f} s  {texto[:40]}", flush=True)
            if pcm:
                pcm += silencio(PAUSA_PARRAFO)
            inicio = len(pcm) / 2 / FRECUENCIA
            pcm += frase
            cues.append((inicio, len(pcm) / 2 / FRECUENCIA, texto))

        guardar_wav(pcm, SALIDA / f"escena-{numero}.wav")
        guardar_srt(cues, SALIDA / f"escena-{numero}.srt")

        if numero > 1:
            completo += silencio(PAUSA_ESCENA)
        base = len(completo) / 2 / FRECUENCIA
        cues_completo += [(base + a, base + b, t) for a, b, t in cues]
        completo += pcm
        tiempos.append({"escena": numero, "titulo": titulo, "inicio": base,
                        "fin": base + len(pcm) / 2 / FRECUENCIA})
        print(f"{titulo}: {len(pcm) / 2 / FRECUENCIA:.1f} s", flush=True)

    completo += silencio(0.5)
    guardar_wav(completo, SALIDA / "episodio-003-voz.wav")
    guardar_srt(cues_completo, SALIDA / "episodio-003-voz.srt")
    (SALIDA / "escenas.json").write_text(json.dumps(tiempos, ensure_ascii=False, indent=2))
    print(f"Total: {len(completo) / 2 / FRECUENCIA:.1f} s")


if __name__ == "__main__":
    main()
