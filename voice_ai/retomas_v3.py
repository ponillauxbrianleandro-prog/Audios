#!/usr/bin/env python3
"""Consistencia de tono: regenera (hasta 4 tomas, temperatura baja) las líneas cuyo F0 se aleja > 1,2 st de la mediana
y las nuevas de la apertura; se queda con la toma más cercana al objetivo. Reanudable (hecho.json)."""
import json, re, sys, time
from pathlib import Path
import numpy as np, soundfile as sf, torch, parselmouth
from scipy.signal import welch
from qwen_tts import Qwen3TTSModel

AQUI = Path(__file__).resolve().parent
RAW, FIN = AQUI / "cache_v3" / "raw", AQUI / "cache_v3" / "final"
torch.set_num_threads(int(sys.argv[1]) if len(sys.argv) > 1 else 4)
lines = json.loads((AQUI / "lineas_v3.json").read_text())
HECHO = AQUI / "cache_v3" / "retomas_hecho.json"
hecho = set(json.loads(HECHO.read_text())) if HECHO.exists() else set()


def f0(x, sr):
    p = parselmouth.Sound(x.astype(np.float64), sr).to_pitch(pitch_floor=70, pitch_ceiling=350).selected_array["frequency"]
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


def metr(x, sr, nw):
    fq, p = welch(x, sr, nperseg=2048)
    return dict(clip=int((np.abs(x) > 0.99).sum()), hf=float(p[(fq > 6000) & (fq < 10000)].sum() / (p[(fq > 100) & (fq < 4000)].sum() + 1e-12)), spw=len(x) / sr / max(nw, 1))


# 1) objetivo de tono = mediana de las líneas existentes
exist = {}
for o in lines:
    f = RAW / f"{o['key']}.wav"
    if f.exists():
        x, sr = sf.read(str(f))
        exist[o["key"]] = f0(x.astype(np.float32), sr)
vals = [v for v in exist.values() if v]
OBJ = float(np.median(vals))
dev = lambda v: abs(12 * np.log2(v / OBJ)) if v else 99.0
print(f"objetivo F0 = {OBJ:.1f} Hz", flush=True)
nuevas = [o for o in lines if o["key"] not in exist]
lejos = sorted([o for o in lines if o["key"] in exist and dev(exist[o["key"]]) > 1.2], key=lambda o: -dev(exist[o["key"]]))
cola = nuevas + lejos
print(f"{len(nuevas)} nuevas, {len(lejos)} lejanas > 1,2 st", flush=True)

m = Qwen3TTSModel.from_pretrained(str(AQUI / "models/Qwen3-TTS-12Hz-0.6B-Base"), device_map="cpu", dtype=torch.float32)
prompt = m.create_voice_clone_prompt(ref_audio=str(AQUI / "referencia_v3.wav"), ref_text=None, x_vector_only_mode=True)


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
        parts += [w[0].astype(np.float32), np.zeros(int(0.22 * sr), np.float32)]
    return np.concatenate(parts[:-1]), sr


t_all = time.time()
for n, o in enumerate(cola):
    k = o["key"]
    if k in hecho:
        continue
    nw = len(o["text"].split())
    mejor, mf, mdev = None, None, exist.get(k) and dev(exist[k]) or 99.0
    for toma in range(4):
        x, sr = sintetizar(o["text"], 5000 + 17 * n + toma)
        mt = metr(x, sr, nw); ff = f0(x, sr); dv = dev(ff)
        ok = mt["clip"] == 0 and 0.25 <= mt["spw"] <= 0.80 + 1.0 / max(nw, 1)
        if ok and dv < mdev:
            mejor, mf, mdev = x, ff, dv
        if ok and dv <= 0.8:
            break
    if mejor is not None:
        sf.write(str(RAW / f"{k}.tmp.wav"), mejor, sr, subtype="FLOAT")
        (RAW / f"{k}.tmp.wav").rename(RAW / f"{k}.wav")
        for ext in (".wav", ".json"):
            (FIN / f"{k}{ext}").unlink(missing_ok=True)                 # se reprocesa
    if mejor is not None or k in exist:
        hecho.add(k); HECHO.write_text(json.dumps(sorted(hecho)))
    print(f"{n + 1}/{len(cola)} cap{o['cap']} desvío -> {mdev:.2f} st (f0 {mf if mf else exist.get(k)}) · {(time.time() - t_all) / 60:.1f} min", flush=True)
print("== RETOMAS TERMINADAS", flush=True)
