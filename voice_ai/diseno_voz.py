#!/usr/bin/env python3
"""Voces diseñadas (no clonadas de nadie) con Qwen3-TTS VoiceDesign: genera variantes de una referencia limpia.
Salida: diseno/<variante>.wav + diseno/<variante>.txt (transcripción exacta) y métricas."""
import json, sys, time
from pathlib import Path
import numpy as np, soundfile as sf, torch, parselmouth
from qwen_tts import Qwen3TTSModel

AQUI = Path(__file__).resolve().parent
OUT = AQUI / "diseno"; OUT.mkdir(exist_ok=True)
torch.set_num_threads(4)
TEXTO = ("Hace doscientos cincuenta y cinco millones de años, este valle no tenía nombre. No había flores. No había hierba. "
         "Ningún pájaro cruzaba el cielo. Lo que había aquí era más antiguo: helechos, colas de caballo, "
         "y un animal que caminaba cada mañana hasta el río.")
BASE = "Sonido de estudio profesional, sin ruido ni reverberación, dicción clara, español rioplatense neutro. "
VARIANTES = {
    "a_grave_calida": BASE + "Voz masculina adulta de narrador de documental, grave y gruesa, cálida, con cuerpo, ritmo pausado pero vivo, entonación natural y expresiva.",
    "b_baritono": BASE + "Voz masculina de barítono profundo y resonante, textura gruesa, seria pero cercana, narración de documental de naturaleza, ritmo medio, entonación con matices.",
    "d_bajo_profundo": BASE + "Voz de hombre maduro, muy grave: un bajo profundo, tono muy bajo y grueso, pecho resonante, narrador de documental, ritmo calmado pero con vida, entonación natural.",
    "e_locutor_grave": BASE + "Locutor masculino de radio con voz extremadamente grave y aterciopelada, tono muy bajo, voz gruesa y cálida con mucha resonancia de pecho, ritmo medio, expresivo.",
    "c_media_viva": BASE + "Voz masculina media-grave, firme y gruesa, con energía contenida y curiosidad, narrador de documental científico, ritmo ágil sin apuro, entonación viva y natural.",
}
sel = sys.argv[1:] or list(VARIANTES)
m = Qwen3TTSModel.from_pretrained(str(AQUI / "models/Qwen3-TTS-12Hz-1.7B-VoiceDesign"), device_map="cpu", dtype=torch.float32)
for k in sel:
    f = OUT / f"{k}.wav"
    if f.exists():
        continue
    t = time.time()
    torch.manual_seed(7)
    w, sr = m.generate_voice_design(text=TEXTO, language="Spanish", instruct=VARIANTES[k], max_new_tokens=900)
    x = w[0].astype(np.float32)
    sf.write(str(f), x, sr, subtype="FLOAT"); (OUT / f"{k}.txt").write_text(TEXTO)
    p = parselmouth.Sound(x.astype(np.float64), sr).to_pitch(pitch_floor=60, pitch_ceiling=350).selected_array["frequency"]; p = p[p > 0]
    fr = x[:len(x) // 480 * 480].reshape(-1, 480); e = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)
    print(f"{k}: {len(x) / sr:.1f} s · F0 {np.median(p):.0f} Hz · piso de ruido {np.percentile(e, 10):.0f} dB · pico {np.abs(x).max():.2f} · recortes {(np.abs(x) > 0.99).sum()} · {(time.time() - t) / 60:.1f} min", flush=True)
print("== DISEÑO TERMINADO", flush=True)
