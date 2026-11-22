#!/usr/bin/env python3
"""Voz «Quebracho v4»: mismo clon (referencia de cache_v13/ref) pero SIN postproceso de tono.
Neutralidad por generación: temperatura baja y 4 tomas por frase; se elige la que mejor combina duración, rango de entonación objetivo
(≈62 Hz; cada 4-8 frases ≈74 Hz, apenas más exaltada) y calidad (sin saltos de tono, sin recorte). Reanudable."""
import json, sys, time
from pathlib import Path
import numpy as np, soundfile as sf, torch, parselmouth
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "episodio-005-vetusodon" / "render"))
from guion_datos import todas, sheismo
from qwen_tts import Qwen3TTSModel

AQUI = Path(__file__).resolve().parent
C = AQUI / "cache_v14"; RAW = C / "raw"; RAW.mkdir(exist_ok=True)
REF = AQUI / "cache_v13" / "ref"
torch.set_num_threads(4)
D = json.loads((C / "durs_v11.json").read_text())
TEMP = 0.45
RANGO_NEUTRO, RANGO_ALTO = 62.0, 74.0
NTOMAS = 4


def recorta(x, sr):
    e = np.abs(x) > 0.02
    if not e.any():
        return x
    a, b = np.argmax(e), len(e) - np.argmax(e[::-1])
    return x[max(0, a - int(0.05 * sr)):min(len(x), b + int(0.14 * sr))]


def medidas(x, sr):
    s = parselmouth.Sound(x.astype(np.float64), sr)
    p = s.to_pitch(time_step=0.01, pitch_floor=75, pitch_ceiling=350).selected_array["frequency"]
    v = p > 0
    par = v[1:] & v[:-1]
    c = 1200 * np.abs(np.log2(p[1:][par] / p[:-1][par])) if par.any() else np.array([0.0])
    f = p[v]
    h = s.to_harmonicity_cc().values
    h = h[h > -200]
    return dict(voz=int(v.sum()), rango=float(np.percentile(f, 90) - np.percentile(f, 10)) if len(f) > 10 else None,
                salto200=float(100 * np.mean(c > 200)), paso=float(np.median(c)), hnr=float(np.median(h)) if len(h) else 0.0, f0=float(np.median(f)) if len(f) else 0.0)


def plan_exaltadas(n, seed=14):
    rng = np.random.default_rng(seed)
    out, i = set(), int(rng.integers(3, 7))
    while i < n:
        out.add(i)
        i += int(rng.integers(4, 9))
    return out


m = Qwen3TTSModel.from_pretrained(str(AQUI / "models/Qwen3-TTS-12Hz-1.7B-Base"), device_map="cpu", dtype=torch.float32)
prompt = m.create_voice_clone_prompt(ref_audio=str(REF / "ref.wav"), ref_text=(REF / "ref.txt").read_text(), x_vector_only_mode=False)
L = todas()
ALTAS = plan_exaltadas(len(L))
sel_f = C / "seleccion.json"
SEL = json.loads(sel_f.read_text()) if sel_f.exists() else {}
t_all = time.time()
for n, (esc, i, texto) in enumerate(L):
    k = f"{esc:02d}_{i}"
    fo = RAW / f"{k}.wav"
    if fo.exists():
        continue
    tx = sheismo(texto); nw = len(tx.split())
    objetivo = D[k] * (1.28 if esc == 0 else 1.0)
    rg_obj = RANGO_ALTO if n in ALTAS else RANGO_NEUTRO
    mejor = None
    for toma in range(NTOMAS):
        torch.manual_seed(500 + 19 * n + toma)
        w, sr = m.generate_voice_clone(text=tx, language="Spanish", voice_clone_prompt=prompt, max_new_tokens=int(nw * 9 + 48),
                                       temperature=TEMP, top_k=20, subtalker_temperature=TEMP)
        x = recorta(w[0].astype(np.float32), sr)
        r = len(x) / sr / objetivo
        q = medidas(x, sr)
        sc = 6 * max(0.0, abs(r - 1) - 0.10) + abs(r - 1)
        if q["rango"] is not None and q["voz"] >= 80:
            sc += abs(q["rango"] - rg_obj) / 25.0
        if q["salto200"] > 1.5: sc += 2.0
        if q["paso"] < 24 and q["voz"] >= 80: sc += 1.0
        if q["hnr"] < 9: sc += 1.0
        if int((np.abs(x) > 0.99).sum()) > 0: sc += 5.0
        if mejor is None or sc < mejor[1]:
            mejor = (x, sc, sr, dict(q, ratio=round(r, 3), objetivo_rango=rg_obj, toma=toma, puntaje=round(sc, 3)))
        if sc < 0.30:
            break
    x, _, sr, info = mejor
    sf.write(str(fo.with_suffix(".tmp.wav")), x, sr, subtype="FLOAT"); fo.with_suffix(".tmp.wav").rename(fo)
    SEL[k] = info; sel_f.write_text(json.dumps(SEL))
    print(f"{n + 1}/{len(L)} {k} {len(x) / sr:5.1f}s (obj {objetivo:4.1f}s) rango {info['rango'] or 0:4.0f} (obj {rg_obj:.0f}) · {(time.time() - t_all) / 60:.1f} min", flush=True)
print("== NARRACION V14 TERMINADA", flush=True)
