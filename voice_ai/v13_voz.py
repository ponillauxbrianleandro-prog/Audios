#!/usr/bin/env python3
"""Voz del episodio 005 v13 «Quebracho v3»: clonación (Qwen3-TTS Base 1.7B) desde el tramo de referencia elegido de la grabación del autor.
Elige entre varias tomas la que mejor encaja con la duración que tenía cada frase en el video (cache_v13/durs_v11.json). Reanudable."""
import json, sys, time
from pathlib import Path
import numpy as np, soundfile as sf, torch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "episodio-005-vetusodon" / "render"))
from guion_datos import todas, sheismo
from qwen_tts import Qwen3TTSModel

AQUI = Path(__file__).resolve().parent
C = AQUI / "cache_v13"; RAW = C / "raw"; RAW.mkdir(exist_ok=True)
torch.set_num_threads(4)
D = json.loads((C / "durs_v11.json").read_text())


def recorta(x, sr):
    e = np.abs(x) > 0.02
    if not e.any():
        return x
    a, b = np.argmax(e), len(e) - np.argmax(e[::-1])
    return x[max(0, a - int(0.05 * sr)):min(len(x), b + int(0.14 * sr))]


m = Qwen3TTSModel.from_pretrained(str(AQUI / "models/Qwen3-TTS-12Hz-1.7B-Base"), device_map="cpu", dtype=torch.float32)
prompt = m.create_voice_clone_prompt(ref_audio=str(C / "ref" / "ref.wav"), ref_text=(C / "ref" / "ref.txt").read_text(), x_vector_only_mode=False)
t_all = time.time()
L = todas()
for n, (esc, i, texto) in enumerate(L):
    k = f"{esc:02d}_{i}"
    fo = RAW / f"{k}.wav"
    if fo.exists():
        continue
    tx = sheismo(texto); nw = len(tx.split())
    objetivo = D[k] * (1.28 if esc == 0 else 1.0)                       # las frases de la apertura se aceleran 1,28 después
    mejor = None
    for toma in range(3):
        torch.manual_seed(300 + 17 * n + toma)
        w, sr = m.generate_voice_clone(text=tx, language="Spanish", voice_clone_prompt=prompt, max_new_tokens=int(nw * 9 + 48),
                                       temperature=0.62, top_k=30, subtalker_temperature=0.62)
        x = recorta(w[0].astype(np.float32), sr)
        r = len(x) / sr / objetivo
        ok = int((np.abs(x) > 0.99).sum()) == 0
        score = abs(r - 1) if ok else 9.0
        if mejor is None or score < mejor[1]:
            mejor = (x, score, sr)
        if ok and 0.92 <= r <= 1.12:
            break
    x, _, sr = mejor
    sf.write(str(fo.with_suffix(".tmp.wav")), x, sr, subtype="FLOAT"); fo.with_suffix(".tmp.wav").rename(fo)
    print(f"{n + 1}/{len(L)} {k} {len(x) / sr:5.1f}s (objetivo {objetivo:4.1f}s) · {(time.time() - t_all) / 60:.1f} min", flush=True)
print("== NARRACION V13 TERMINADA", flush=True)
