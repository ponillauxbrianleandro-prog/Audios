#!/usr/bin/env python3
"""Narración v4: Qwen3-TTS 0.6B-Base clonando referencia_v3.wav (la voz propia del usuario, solo pasa-altos y ruido suave).
Guarda la salida CRUDA (sin de-reverberación, sin limitadores) en cache_v3/raw/<clave>.wav y la mejor de hasta 2 tomas por línea
según métricas objetivas (recortes, energía espuria de alta frecuencia, duración razonable). Reanudable.
Uso: python narrar_v3.py [hilos]
"""
import json, re, sys, time
from pathlib import Path
import numpy as np, soundfile as sf, torch
from scipy.signal import welch
from qwen_tts import Qwen3TTSModel

AQUI = Path(__file__).resolve().parent
RAW = AQUI / "cache_v3" / "raw"; RAW.mkdir(parents=True, exist_ok=True)
torch.set_num_threads(int(sys.argv[1]) if len(sys.argv) > 1 else 4)
lines = json.loads((AQUI / "lineas_v3.json").read_text())


def frases(t):
    ps = re.split(r"(?<=[.!?…])\s+", t.strip())
    out, cur = [], ""
    for p in ps:
        if cur and len((cur + " " + p).split()) > 30:
            out.append(cur); cur = p
        else:
            cur = (cur + " " + p).strip()
    return out + ([cur] if cur else [])


def metricas(x, sr, nw):
    f, p = welch(x, sr, nperseg=2048)
    lo = p[(f > 100) & (f < 4000)].sum() + 1e-12
    hf = p[(f > 6000) & (f < 10000)].sum()
    return dict(clip=int((np.abs(x) > 0.99).sum()), hf=float(hf / lo), spw=len(x) / sr / max(nw, 1))


def sintetizar(m, prompt, texto):
    parts, sr = [], 24000
    for fr in frases(texto):
        nw = len(fr.split())
        for intento in range(3):
            w, sr = m.generate_voice_clone(text=fr, language="Spanish", voice_clone_prompt=prompt, max_new_tokens=int(nw * 9 + 48))
            if len(w[0]) / sr <= nw * 0.75 + 1.5:
                break
        parts += [w[0].astype(np.float32), np.zeros(int(0.22 * sr), np.float32)]
    return np.concatenate(parts[:-1]), sr


m = Qwen3TTSModel.from_pretrained(str(AQUI / "models/Qwen3-TTS-12Hz-0.6B-Base"), device_map="cpu", dtype=torch.float32)
prompt = m.create_voice_clone_prompt(ref_audio=str(AQUI / "referencia_v3.wav"), ref_text=None, x_vector_only_mode=True)
hist, t_all = [], time.time()
for i, o in enumerate(lines):
    f = RAW / f"{o['key']}.wav"
    if f.exists():
        continue
    nw = len(o["text"].split())
    mejor, mm, ntom = None, None, 0
    for toma in range(2):
        torch.manual_seed(1000 * i + toma)
        x, sr = sintetizar(m, prompt, o["text"])
        mt = metricas(x, sr, nw)
        ntom += 1
        med = float(np.median(hist)) if len(hist) >= 8 else None
        malo = mt["clip"] > 0 or not (0.25 <= mt["spw"] <= 0.80) or (med is not None and mt["hf"] > 2.5 * med)
        if mejor is None or (not malo) or mt["hf"] < mm["hf"]:
            mejor, mm = x, mt
        if not malo:
            break
    hist.append(mm["hf"])
    sf.write(str(f.with_suffix(".tmp.wav")), mejor, sr, subtype="FLOAT")
    f.with_suffix(".tmp.wav").rename(f)
    print(f"{i + 1}/{len(lines)} cap{o['cap']} {len(mejor) / sr:5.1f}s tomas={ntom} hf={mm['hf']:.4f} · {(time.time() - t_all) / 60:.1f} min", flush=True)
print("== NARRACION CRUDA TERMINADA", flush=True)
