#!/usr/bin/env python3
"""Genera los fotogramas clave con SDXL-Turbo en CPU (bf16, AMX).

    voice_ai/.venv/bin/python episodio-004-tuco-tuco/generar_imagenes.py [--candidatos 2] [id ...]

Salida: frames/candidatos/<id>_<n>.png (576x1024 se escala luego a 720x1280).
Con ids como argumento solo se regeneran esas tomas. Semilla fija por toma y candidato.
Los prompts salen de tomas.py. Tras mirar los candidatos, se copia el elegido a frames/elegidas/<id>.png.
"""
import argparse
import sys
import time
from pathlib import Path

import torch
from diffusers import AutoPipelineForText2Image

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import tomas  # noqa: E402

MODELO = AQUI.parent / "voice_ai" / "models" / "sdxl-turbo"
ANCHO, ALTO = 640, 1152  # 9:16 en múltiplos de 64; luego se escala a 720x1280


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--candidatos", type=int, default=2)
    ap.add_argument("--pasos", type=int, default=4)
    args = ap.parse_args()

    salida = AQUI / "frames" / "candidatos"
    salida.mkdir(parents=True, exist_ok=True)
    pipe = AutoPipelineForText2Image.from_pretrained(MODELO, torch_dtype=torch.bfloat16, variant="fp16")
    pipe.set_progress_bar_config(disable=True)
    torch.set_num_threads(4)

    for i, t in enumerate(tomas.TOMAS):
        if args.ids and t["id"] not in args.ids:
            continue
        neg = tomas.NEGATIVO_RATA if t["animal"] == "rata" else tomas.NEGATIVO
        for n in range(1, args.candidatos + 1):
            destino = salida / f"{t['id']}_{n}.png"
            if destino.exists() and not args.ids:
                continue
            ini = time.time()
            img = pipe(tomas.prompt_completo(t), negative_prompt=neg, width=ANCHO, height=ALTO,
                       num_inference_steps=args.pasos, guidance_scale=0.0,
                       generator=torch.Generator().manual_seed(1000 + i * 10 + n)).images[0]
            img.save(destino)
            print(f"{t['id']}_{n}: {time.time() - ini:.0f} s", flush=True)


if __name__ == "__main__":
    main()
