#!/usr/bin/env python3
"""Genera la narración del episodio 005 a partir de guion.md, con la voz clonada.

Voz: Qwen3-TTS 0.6B Base clonando la muestra del usuario (referencia/voz-referencia.wav + .txt).
Ejecutar con el entorno de voice_ai:
    voice_ai/.venv/bin/python episodio-005-pudu/generar_audio.py            # todo el episodio
    voice_ai/.venv/bin/python episodio-005-pudu/generar_audio.py --solo 4   # prueba de una escena (audio/prueba-escena-4.wav)

Ritmo (marcas en guion.md): `|0.5|` pausa entre cláusulas; `{lento}` cláusula más despacio y un poco más fuerte.
Cada cláusula se sintetiza por separado; de hasta 3 tomas se elige la que whisper entiende mejor y cuyo ritmo no es
exagerado. La velocidad varía un poco de una cláusula a otra (no es constante) y las pausas también.
La voz se engrosa ligeramente con rubberband (tono más grave, duración intacta, formantes desplazados).
No se aplica eco, reverb ni distorsión.
Salida en audio/: escena-N.wav/.srt, episodio-005-voz.wav/.srt y escenas.json.
"""
import argparse
import difflib
import hashlib
import json
import re
import struct
import subprocess
import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
SALIDA = AQUI / "audio"
MODELO = RAIZ / "voice_ai" / "models" / "Qwen3-TTS-12Hz-0.6B-Base"
WHISPER = RAIZ / "voice_ai" / "models" / "whisper"
REFERENCIA = AQUI / "referencia" / "voz-referencia.wav"
REFERENCIA_TEXTO = AQUI / "referencia" / "voz-referencia.txt"

FRECUENCIA = 24000  # Hz, mono, 16 bits
PAUSA_ESCENA = 0.55
PAUSA_PARRAFO = 0.38
SILENCIO_INICIAL = 0.3
UMBRAL_VOZ = 300
MARGEN_VOZ = 0.06
PICO = 0.80

# Ritmo
VEL_LENTO = 0.90          # factor de atempo (tono intacto)
VEL_BASE = (0.97, 1.04)   # variación al azar de las cláusulas normales
GAN_LENTO = +1.2          # dB: los remates un poco más fuertes
GAN_BASE = (-0.5, +0.4)
PAUSA_PUNT = {".": 0.30, "?": 0.40, "!": 0.30, "…": 0.50, ":": 0.25}
JITTER_PAUSA = 0.15
ESCALA_PAUSAS = 0.80      # acorta todas las pausas marcadas (el episodio debe quedar bajo 1:59)

# Tono: más grave solo un poco (semitonos). La escena 1 suena aguda: un poco más.
SEMITONOS = {1: -1.4}
SEMITONOS_BASE = -0.6

# Mejor toma
TOMAS_MAX = 3
CPS_MAX = 16.5            # caracteres por segundo: más rápido que esto suena atropellado
PALABRAS_CLAVE = ["pudú", "ciervo", "brotes", "cuernos", "helechos", "bolsillo", "bambi", "orgullo", "chiquito", "escurridizo"]


# ------------------------------------------------------------------ guion con marcas
def leer_guion():
    """[(titulo, [parrafo_crudo])] entre '## ESCENA' y '## Notas' (las líneas '>' son notas)."""
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


def clausulas(parrafo):
    """Devuelve ([(texto, lento, pausa_despues)], texto_limpio_para_subtitulo)."""
    if "|" in parrafo:
        trozos = re.split(r"\|\s*([0-9.]+)\s*\|", parrafo)
        items = []
        for i in range(0, len(trozos), 2):
            pausa = float(trozos[i + 1]) if i + 1 < len(trozos) else 0.0
            items.append((trozos[i].strip(), pausa))
    else:                                                    # sin marcas: oraciones con pausa por puntuación
        partes = re.findall(r".+?(?:[.?!…]+|$)\s*", parrafo)
        items = [(p.strip(), PAUSA_PUNT.get(p.strip()[-1:], 0.3)) for p in partes if p.strip()]
    out, limpio = [], []
    for texto, pausa in items:
        lento = texto.startswith("{lento}")
        texto = texto.replace("{lento}", "").strip()
        out.append((texto, lento, pausa))
        limpio.append(texto)
    return out, " ".join(limpio)


# ------------------------------------------------------------------ síntesis
def normalizar(s):
    return re.findall(r"[a-záéíóúüñ]+", s.lower())


def ffmpeg_pcm(pcm, sr_in, sr_out, filtro=None):
    cmd = ["ffmpeg", "-v", "error", "-f", "s16le", "-ac", "1", "-ar", str(sr_in), "-i", "-"]
    if filtro:
        cmd += ["-af", filtro]
    cmd += ["-f", "s16le", "-ac", "1", "-ar", str(sr_out), "-"]
    return subprocess.run(cmd, input=pcm, check=True, capture_output=True).stdout


class Voz:
    def __init__(self):
        import torch
        from faster_whisper import WhisperModel
        from qwen_tts import Qwen3TTSModel

        torch.set_num_threads(4)
        self.modelo = Qwen3TTSModel.from_pretrained(str(MODELO), device_map="cpu", dtype=torch.float32)
        texto = REFERENCIA_TEXTO.read_text(encoding="utf-8").strip() if REFERENCIA_TEXTO.exists() else None
        self.prompt = self.modelo.create_voice_clone_prompt(
            ref_audio=str(REFERENCIA), ref_text=texto, x_vector_only_mode=texto is None)
        self.asr = WhisperModel("small", device="cpu", compute_type="int8", download_root=str(WHISPER))

    def sintetizar(self, texto):
        wavs, sr = self.modelo.generate_voice_clone(
            text=texto, language="Spanish", voice_clone_prompt=self.prompt,
            max_new_tokens=int(len(texto) / 15 * 12 * 2) + 24)
        x = np.asarray(wavs[0], dtype=np.float32)
        pcm = (np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()
        return pcm if sr == FRECUENCIA else ffmpeg_pcm(pcm, sr, FRECUENCIA)

    def oir(self, pcm):
        x = np.frombuffer(ffmpeg_pcm(pcm, FRECUENCIA, 16000), np.int16).astype(np.float32) / 32768
        segs, _ = self.asr.transcribe(x, language="es", condition_on_previous_text=False, beam_size=3)
        return " ".join(s.text.strip() for s in segs)

    def mejor_toma(self, texto, lento):
        """Hasta TOMAS_MAX tomas; devuelve (pcm_crudo, puntaje, oido)."""
        esperadas = normalizar(texto)
        claves = [c for c in PALABRAS_CLAVE if any(difflib.SequenceMatcher(None, c, w).ratio() > 0.8 for w in esperadas)]
        mejor = None
        for k in range(TOMAS_MAX):
            pcm = self.sintetizar(texto)
            oido = self.oir(pcm)
            heard = normalizar(oido)
            ratio = difflib.SequenceMatcher(None, esperadas, heard).ratio()
            claves_ok = all(any(difflib.SequenceMatcher(None, c, w).ratio() > 0.78 for w in heard) for c in claves)
            dur = max(0.3, len(pcm) / 2 / FRECUENCIA - 0.15)
            cps = len(texto) / dur
            puntaje = ratio + (0.15 if claves_ok else -0.15) - max(0.0, cps - CPS_MAX) * 0.03
            if mejor is None or puntaje > mejor[1]:
                mejor = (pcm, puntaje, oido)
            if ratio >= 0.97 and claves_ok and cps <= CPS_MAX:
                break
        return mejor


def recortar(pcm):
    muestras = np.frombuffer(pcm, "<i2")
    idx = np.nonzero(np.abs(muestras) > UMBRAL_VOZ)[0]
    margen = int(FRECUENCIA * MARGEN_VOZ)
    a, b = max(0, idx[0] - margen), min(len(muestras), idx[-1] + margen)
    return muestras[a:b].astype("<i2").tobytes()


def dar_forma(pcm, velocidad, semitonos, ganancia_db):
    """Velocidad (atempo, tono intacto) + tono más grave (rubberband, duración intacta) + ganancia + pico."""
    filtros = []
    if abs(velocidad - 1.0) > 0.003:
        filtros.append(f"atempo={velocidad:.4f}")
    if semitonos:
        filtros.append(f"rubberband=pitch={2 ** (semitonos / 12):.5f}:formant=shifted:pitchq=quality")
    if filtros:
        pcm = ffmpeg_pcm(pcm, FRECUENCIA, FRECUENCIA, ",".join(filtros))
    x = np.frombuffer(pcm, "<i2").astype(np.float32)
    x = x / max(1.0, np.abs(x).max()) * PICO * (10 ** (ganancia_db / 20))
    return (np.clip(x, -0.98, 0.98) * 32767).astype("<i2").tobytes()


def silencio(segundos):
    return b"\x00\x00" * int(FRECUENCIA * segundos)


def guardar_wav(pcm, destino):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ac", "1", "-ar", str(FRECUENCIA), "-i", "-", str(destino)],
                   input=pcm, check=True)


def marca(segundos):
    ms = round(segundos * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def guardar_srt(cues, destino):
    bloques = [f"{n}\n{marca(a)} --> {marca(b)}\n{t}\n" for n, (a, b, t) in enumerate(cues, 1)]
    destino.write_text("\n".join(bloques), encoding="utf-8")


def cargar_cache():
    p = SALIDA / "cache" / "tomas.json"
    return json.loads(p.read_text()) if p.exists() else {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", type=int, help="genera solo esa escena (prueba), sin tocar el resultado final")
    args = ap.parse_args()
    SALIDA.mkdir(exist_ok=True)
    (SALIDA / "cache").mkdir(exist_ok=True)
    voz = Voz()
    info = cargar_cache()
    completo, cues_completo, tiempos = silencio(SILENCIO_INICIAL), [], []

    for numero, (titulo, parrafos) in enumerate(leer_guion(), 1):
        if args.solo and numero != args.solo:
            continue
        pcm, cues = b"", []
        st = SEMITONOS.get(numero, SEMITONOS_BASE)
        for parrafo in parrafos:
            cl, subtitulo = clausulas(parrafo)
            if pcm:
                pcm += silencio(PAUSA_PARRAFO)
            inicio = len(pcm) / 2 / FRECUENCIA
            for texto, lento, pausa in cl:
                clave = hashlib.sha1(texto.encode()).hexdigest()[:16]
                ruta = SALIDA / "cache" / f"{clave}.raw.pcm"
                if ruta.exists():
                    crudo = ruta.read_bytes()
                else:
                    crudo, puntaje, oido = voz.mejor_toma(texto, lento)
                    ruta.write_bytes(crudo)
                    info[clave] = dict(texto=texto, puntaje=round(float(puntaje), 3), oido=oido)
                    (SALIDA / "cache" / "tomas.json").write_text(json.dumps(info, ensure_ascii=False, indent=1))
                rng = np.random.default_rng(int(clave[:8], 16))
                vel = VEL_LENTO if lento else float(rng.uniform(*VEL_BASE))
                gan = GAN_LENTO if lento else float(rng.uniform(*GAN_BASE))
                frase = dar_forma(recortar(crudo), vel, st, gan)
                dur = len(frase) / 2 / FRECUENCIA
                pcm += frase
                pcm += silencio(pausa * ESCALA_PAUSAS * float(rng.uniform(1 - JITTER_PAUSA, 1 + JITTER_PAUSA)))
                tag = "lento" if lento else f"x{vel:.2f}"
                print(f"  · {dur:4.1f} s {tag:6} {texto[:56]}", flush=True)
            fin = len(pcm.rstrip(b"\x00")) / 2 / FRECUENCIA     # sin la pausa final
            pcm = pcm[: int(fin * FRECUENCIA) * 2]
            cues.append((inicio, fin, subtitulo))

        if args.solo:
            guardar_wav(pcm, SALIDA / f"prueba-escena-{numero}.wav")
            print(f"{titulo}: {len(pcm) / 2 / FRECUENCIA:.1f} s -> prueba-escena-{numero}.wav")
            return
        guardar_wav(pcm, SALIDA / f"escena-{numero}.wav")
        guardar_srt(cues, SALIDA / f"escena-{numero}.srt")
        if numero > 1:
            completo += silencio(PAUSA_ESCENA)
        base = len(completo) / 2 / FRECUENCIA
        cues_completo += [(base + a, base + b, t) for a, b, t in cues]
        completo += pcm
        tiempos.append({"escena": numero, "titulo": titulo, "inicio": base, "fin": base + len(pcm) / 2 / FRECUENCIA})
        print(f"{titulo}: {len(pcm) / 2 / FRECUENCIA:.1f} s", flush=True)

    completo += silencio(0.5)
    guardar_wav(completo, SALIDA / "episodio-005-voz.wav")
    guardar_srt(cues_completo, SALIDA / "episodio-005-voz.srt")
    (SALIDA / "escenas.json").write_text(json.dumps(tiempos, ensure_ascii=False, indent=2))
    print(f"Total: {len(completo) / 2 / FRECUENCIA:.1f} s")


if __name__ == "__main__":
    main()
