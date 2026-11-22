#!/usr/bin/env python3
"""Genera voces candidatas (VoiceDesign) más graves y gruesas; no clona a nadie."""
import sys, numpy as np, soundfile as sf, torch
from pathlib import Path
from qwen_tts import Qwen3TTSModel
AQUI = Path(__file__).resolve().parent
torch.set_num_threads(4)
TEXTO = (AQUI / "cache_v8" / "ref" / "ref.txt").read_text()
BASE = ("Sonido de estudio profesional, sin ruido ni reverberación, dicción clara. Español rioplatense de Buenos Aires, con yeísmo rehilado: la 'll' y la 'y' suenan como 'sh'. ")
INS = {
 "A": BASE + "Hombre de unos 50 años, voz muy grave, ronca y gruesa, con mucho pecho y cuerpo, tono bajo de barítono profundo, hablando con voz plena y firme, nada susurrada ni aireada, narrador veterano de documental de naturaleza, serio y cálido, ritmo pausado, sin tonada de locutor comercial.",
 "B": BASE + "Hombre mayor de 55 años, voz de bajo-barítono, áspera y robusta, resonancia de pecho muy marcada, volumen firme y proyectado, aire mínimo, como un narrador de documentales con autoridad tranquila; entonación natural y sobria, nunca de publicidad.",
 "C": BASE + "Hombre de 45 a 50 años, barítono grave, voz densa y plena, con textura de pecho y un poco de gravilla, hablada en voz alta y segura, nada de susurro; narrador de documental neutro, cercano, humano, pausado.",
}
m = Qwen3TTSModel.from_pretrained(str(AQUI / "models/Qwen3-TTS-12Hz-1.7B-VoiceDesign"), device_map="cpu", dtype=torch.float32)
for k, ins in INS.items():
    for seed in (7, 21):
        f = AQUI / "candidatas" / f"{k}{seed}.wav"
        if f.exists(): continue
        torch.manual_seed(seed)
        w, sr = m.generate_voice_design(text=TEXTO, language="Spanish", instruct=ins, max_new_tokens=900)
        sf.write(str(f), w[0].astype(np.float32), sr, subtype="FLOAT")
        print("listo", f.name, flush=True)
print("== CANDIDATAS LISTAS", flush=True)
