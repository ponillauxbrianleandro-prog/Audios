#!/usr/bin/env python3
"""Voz del episodio 005: referencia DISEÑADA (Qwen3-TTS VoiceDesign, no clonada de nadie) + narración con el modelo Base 0.6B.
Español rioplatense con yeísmo rehilado ('ll'/'y' -> 'sh'); tono de narrador, sobrio, con poca tonada de locutor comercial.
Salida: cache_v8/raw/<escena>_<n>.wav  (reanudable)."""
import json, re, sys, time
from pathlib import Path
import numpy as np, soundfile as sf, torch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "episodio-005-vetusodon" / "render"))
from guion_datos import todas, sheismo
from qwen_tts import Qwen3TTSModel

AQUI = Path(__file__).resolve().parent
RAW = AQUI / "cache_v8" / "raw"; RAW.mkdir(parents=True, exist_ok=True)
DIS = AQUI / "cache_v8" / "ref"; DIS.mkdir(parents=True, exist_ok=True)
torch.set_num_threads(int(sys.argv[1]) if len(sys.argv) > 1 else 4)
SOLO_REF = len(sys.argv) > 2 and sys.argv[2] == "ref"

INSTRUCCION = ("Sonido de estudio profesional, sin ruido ni reverberación, dicción clara. Español rioplatense de Buenos Aires, con yeísmo rehilado: "
               "la 'll' y la 'y' suenan como 'sh'. Voz masculina adulta de narrador de documental de naturaleza: grave-media, cálida, natural y cercana, "
               "ritmo pausado y fluido; entonación sobria con matices, SIN tonada de locutor comercial ni de radio, sin impostar, sin cantar las frases.")
TEXTO_REF = ("Hace doscientos cincuenta millones de años, este vashe no tenía nombre. No había flores. No había pasto. Ningún pájaro cruzaba el cielo. "
             "Lo que había acá era más antiguo: helechos, colas de cabasho, y un animal que caminaba cada mañana hasta el río.")


def recorta(x, sr):
    e = np.abs(x) > 0.02
    if not e.any():
        return x
    a, b = np.argmax(e), len(e) - np.argmax(e[::-1])
    return x[max(0, a - int(0.05 * sr)):min(len(x), b + int(0.14 * sr))]


ref = DIS / "ref.wav"
if not ref.exists():
    print("diseñando voz de referencia…", flush=True)
    m = Qwen3TTSModel.from_pretrained(str(AQUI / "models/Qwen3-TTS-12Hz-1.7B-VoiceDesign"), device_map="cpu", dtype=torch.float32)
    torch.manual_seed(7)
    w, sr = m.generate_voice_design(text=TEXTO_REF, language="Spanish", instruct=INSTRUCCION, max_new_tokens=900)
    sf.write(str(ref), w[0].astype(np.float32), sr, subtype="FLOAT"); (DIS / "ref.txt").write_text(TEXTO_REF)
    del m
    print(f"referencia lista: {len(w[0]) / sr:.1f} s", flush=True)
if SOLO_REF:
    sys.exit(0)

m = Qwen3TTSModel.from_pretrained(str(AQUI / "models/Qwen3-TTS-12Hz-0.6B-Base"), device_map="cpu", dtype=torch.float32)
prompt = m.create_voice_clone_prompt(ref_audio=str(ref), ref_text=TEXTO_REF, x_vector_only_mode=False)
t_all = time.time()
L = todas()
for n, (esc, i, texto) in enumerate(L):
    fo = RAW / f"{esc:02d}_{i}.wav"
    if fo.exists():
        continue
    tx = sheismo(texto)
    nw = len(tx.split())
    mejor = None
    for toma in range(3):
        torch.manual_seed(100 + 13 * n + toma)
        w, sr = m.generate_voice_clone(text=tx, language="Spanish", voice_clone_prompt=prompt, max_new_tokens=int(nw * 9 + 48),
                                       temperature=0.7, top_k=30, subtalker_temperature=0.7)
        x = recorta(w[0].astype(np.float32), sr)
        dur = len(x) / sr
        if int((np.abs(x) > 0.99).sum()) == 0 and 0.22 * nw <= dur <= 0.75 * nw + 1.5:
            mejor = x
            break
        mejor = x if mejor is None else mejor
    sf.write(str(fo.with_suffix(".tmp.wav")), mejor, sr, subtype="FLOAT"); fo.with_suffix(".tmp.wav").rename(fo)
    print(f"{n + 1}/{len(L)} esc{esc} {len(mejor) / sr:5.1f}s · {(time.time() - t_all) / 60:.1f} min", flush=True)
print("== NARRACION V8 TERMINADA", flush=True)
