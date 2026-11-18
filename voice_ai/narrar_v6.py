#!/usr/bin/env python3
"""Narración v6: voz DISEÑADA (VoiceDesign) como referencia limpia + clonación completa (con transcripción) con el modelo Base 0.6B.
Hasta 3 tomas por línea; se elige la de tono más cercano al de la referencia. Salida cruda en cache_v6/raw. Reanudable."""
import json, re, sys, time
from pathlib import Path
import numpy as np, soundfile as sf, torch, parselmouth
from scipy.signal import welch
from qwen_tts import Qwen3TTSModel

AQUI = Path(__file__).resolve().parent
VOZ = sys.argv[2] if len(sys.argv) > 2 else "d_bajo_profundo"
RAW = AQUI / "cache_v6" / "raw"; RAW.mkdir(parents=True, exist_ok=True)
torch.set_num_threads(int(sys.argv[1]) if len(sys.argv) > 1 else 4)
lines = json.loads((AQUI / "lineas_v3.json").read_text())
ref = AQUI / "diseno" / f"{VOZ}.wav"; ref_text = (AQUI / "diseno" / f"{VOZ}.txt").read_text()


def f0(x, sr):
    p = parselmouth.Sound(x.astype(np.float64), sr).to_pitch(pitch_floor=60, pitch_ceiling=350).selected_array["frequency"]
    p = p[p > 0]
    return float(np.median(p)) if len(p) else None


def frases(t):
    ps = re.split(r"(?<=[.!?…])\s+", t.strip())
    out, cur = [], ""
    for p in ps:
        if cur and len((cur + " " + p).split()) > 30:
            out.append(cur); cur = p
        else:
            cur = (cur + " " + p).strip()
    return out + ([cur] if cur else [])


def recorta(x, sr):
    e = np.abs(x) > 0.02
    if not e.any():
        return x
    a, b = np.argmax(e), len(e) - np.argmax(e[::-1])
    return x[max(0, a - int(0.05 * sr)):min(len(x), b + int(0.12 * sr))]


xr, srr = sf.read(str(ref)); OBJ = f0(xr.astype(np.float32), srr)
print(f"voz {VOZ}: F0 de referencia {OBJ:.1f} Hz", flush=True)
dev = lambda v: abs(12 * np.log2(v / OBJ)) if v else 99.0
m = Qwen3TTSModel.from_pretrained(str(AQUI / "models/Qwen3-TTS-12Hz-0.6B-Base"), device_map="cpu", dtype=torch.float32)
prompt = m.create_voice_clone_prompt(ref_audio=str(ref), ref_text=ref_text, x_vector_only_mode=False)


def sintetizar(texto, seed):
    torch.manual_seed(seed)
    parts, sr = [], 24000
    for fr in frases(texto):
        nw = len(fr.split())
        for _ in range(3):
            w, sr = m.generate_voice_clone(text=fr, language="Spanish", voice_clone_prompt=prompt, max_new_tokens=int(nw * 9 + 48),
                                           temperature=0.7, top_k=30, subtalker_temperature=0.7)
            if len(w[0]) / sr <= nw * 0.75 + 1.5:
                break
        parts += [recorta(w[0].astype(np.float32), sr), np.zeros(int(0.22 * sr), np.float32)]
    return np.concatenate(parts[:-1]), sr


t_all = time.time()
for n, o in enumerate(lines):
    k = o["key"]; fo = RAW / f"{k}.wav"
    if fo.exists():
        continue
    nw = len(o["text"].split())
    mejor, mdev, mf = None, 99.0, None
    for toma in range(3):
        x, sr = sintetizar(o["text"], 100 + 13 * n + toma)
        ff = f0(x, sr); dv = dev(ff)
        ok = int((np.abs(x) > 0.99).sum()) == 0 and 0.2 <= len(x) / sr / nw <= 0.9 + 1.0 / nw
        if ok and dv < mdev:
            mejor, mdev, mf = x, dv, ff
        if ok and dv <= 0.6:
            break
    if mejor is None:
        mejor, mf, mdev = x, ff, dv
    sf.write(str(fo.with_suffix(".tmp.wav")), mejor, sr, subtype="FLOAT"); fo.with_suffix(".tmp.wav").rename(fo)
    print(f"{n + 1}/{len(lines)} cap{o['cap']} {len(mejor) / sr:5.1f}s desvío {mdev:.2f} st · {(time.time() - t_all) / 60:.1f} min", flush=True)
print("== NARRACION V6 TERMINADA", flush=True)
