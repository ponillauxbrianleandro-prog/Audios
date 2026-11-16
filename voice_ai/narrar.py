#!/usr/bin/env python3
"""Narración del documental con Qwen3-TTS (0.6B-Base) clonando la voz de referencia.
Lee lineas.json (render/extraer_guion.py), genera una pista por línea en cache/NNN.wav (reanudable).
Uso: .venv/bin/python narrar.py [hilos]
"""
import json, re, sys, time, ast
from pathlib import Path
import numpy as np, soundfile as sf, torch
from qwen_tts import Qwen3TTSModel

AQUI = Path(__file__).resolve().parent
CACHE = AQUI / "cache"; CACHE.mkdir(exist_ok=True)
torch.set_num_threads(int(sys.argv[1]) if len(sys.argv) > 1 else 2)
lines = json.loads((AQUI / "lineas.json").read_text())


def texto(o):
    if o["text"]:
        return o["text"]
    a, rol, _en, es = ast.literal_eval(o["quote"])
    return f"{a}, {rol.split('·')[0].strip().lower()}, dice: {es}"


def frases(t):
    ps = re.split(r"(?<=[.!?…])\s+", t.strip())
    out, cur = [], ""
    for p in ps:
        if cur and len((cur + " " + p).split()) > 34:
            out.append(cur); cur = p
        else:
            cur = (cur + " " + p).strip()
    return out + ([cur] if cur else [])


m = Qwen3TTSModel.from_pretrained(str(AQUI / "models/Qwen3-TTS-12Hz-0.6B-Base"), device_map="cpu", dtype=torch.float32)
prompt = m.create_voice_clone_prompt(ref_audio=str(AQUI / "referencia.wav"), ref_text=None, x_vector_only_mode=True)
t_all = time.time()
for i, o in enumerate(lines):
    f = CACHE / f"{i:03d}.wav"
    if f.exists():
        continue
    parts, sr = [], 24000
    for fr in frases(texto(o)):
        w, sr = m.generate_voice_clone(text=fr, language="Spanish", voice_clone_prompt=prompt)
        parts += [w[0].astype(np.float32), np.zeros(int(0.22 * sr), np.float32)]
    x = np.concatenate(parts[:-1])
    sf.write(str(f.with_suffix(".tmp.wav")), x, sr)
    f.with_suffix(".tmp.wav").rename(f)
    print(f"{i + 1}/{len(lines)} cap{o['cap']} {len(x) / sr:5.1f}s (hueco {o['dur']:5.1f}s) · {(time.time() - t_all) / 60:.1f} min", flush=True)
print("== NARRACION TERMINADA", flush=True)
