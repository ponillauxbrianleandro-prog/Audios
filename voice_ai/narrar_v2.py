#!/usr/bin/env python3
"""Narración v3: Qwen3-TTS 0.6B-Base clonando referencia_v2.wav (limpia), cada línea limpiada (sin eco ni distorsión).
Genera cache_v2/<clave>.wav y duraciones.json (clave -> segundos). Reanudable. Uso: python narrar_v2.py [hilos]
"""
import json, re, sys, time
from pathlib import Path
import numpy as np, soundfile as sf, torch
from qwen_tts import Qwen3TTSModel
import limpiar as L

AQUI = Path(__file__).resolve().parent
CACHE = AQUI / "cache_v2"; CACHE.mkdir(exist_ok=True)
torch.set_num_threads(int(sys.argv[1]) if len(sys.argv) > 1 else 4)
lines = json.loads((AQUI / "lineas_v2.json").read_text())
SR_OUT = 24000
OBJ_RMS = 10 ** (-21 / 20)          # nivel objetivo de la voz


def frases(t):
    ps = re.split(r"(?<=[.!?…])\s+", t.strip())
    out, cur = [], ""
    for p in ps:
        if cur and len((cur + " " + p).split()) > 30:
            out.append(cur); cur = p
        else:
            cur = (cur + " " + p).strip()
    return out + ([cur] if cur else [])


def guardar_duraciones():
    d = {}
    for o in lines:
        f = CACHE / f"{o['key']}.wav"
        if f.exists():
            x, sr = sf.read(str(f))
            d[o["key"]] = round(len(x) / sr, 3)
    (AQUI / "duraciones.json").write_text(json.dumps(d))
    return len(d)


m = Qwen3TTSModel.from_pretrained(str(AQUI / "models/Qwen3-TTS-12Hz-0.6B-Base"), device_map="cpu", dtype=torch.float32)
prompt = m.create_voice_clone_prompt(ref_audio=str(AQUI / "referencia_v2.wav"), ref_text=None, x_vector_only_mode=True)
t_all = time.time()
for i, o in enumerate(lines):
    f = CACHE / f"{o['key']}.wav"
    if f.exists():
        continue
    parts, sr = [], SR_OUT
    for fr in frases(o["text"]):
        nw = len(fr.split())
        for intento in range(3):                       # tope de duración: evita las generaciones que no terminan
            w, sr = m.generate_voice_clone(text=fr, language="Spanish", voice_clone_prompt=prompt, max_new_tokens=int(nw * 9 + 48))
            if len(w[0]) / sr <= nw * 0.75 + 1.5:
                break
            print(f"  reintento ({len(w[0]) / sr:.1f} s para {nw} palabras)", flush=True)
        parts += [w[0].astype(np.float32), np.zeros(int(0.22 * sr), np.float32)]
    x = np.concatenate(parts[:-1])
    x = L.limpiar(x, sr, rt60=0.35, reverb=True, ruido=False)         # sin eco; sin saturación
    rms = np.sqrt((x ** 2).mean()) + 1e-9
    x = x * min(OBJ_RMS / rms, 0.9 / (np.abs(x).max() + 1e-9))        # nivelación lineal, sin recortes
    sf.write(str(f.with_suffix(".tmp.wav")), x.astype(np.float32), sr, subtype="PCM_24")
    f.with_suffix(".tmp.wav").rename(f)
    print(f"{i + 1}/{len(lines)} cap{o['cap']} {len(x) / sr:5.1f}s · {(time.time() - t_all) / 60:.1f} min", flush=True)
    if (i + 1) % 10 == 0:
        guardar_duraciones()
n = guardar_duraciones()
print(f"== NARRACION TERMINADA ({n} líneas)", flush=True)
