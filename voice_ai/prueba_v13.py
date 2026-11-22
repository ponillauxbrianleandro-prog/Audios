import sys, numpy as np, soundfile as sf, torch
from pathlib import Path
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "episodio-005-vetusodon" / "render"))
from guion_datos import todas, sheismo
from qwen_tts import Qwen3TTSModel
torch.set_num_threads(4)
L = [(e, i, t) for e, i, t in todas() if len(t.split()) >= 14][:2]
m = Qwen3TTSModel.from_pretrained(str(AQUI / "models/Qwen3-TTS-12Hz-1.7B-Base"), device_map="cpu", dtype=torch.float32)
def recorta(x, sr):
    e = np.abs(x) > 0.02
    a, b = np.argmax(e), len(e) - np.argmax(e[::-1])
    return x[max(0, a - int(0.05 * sr)):min(len(x), b + int(0.14 * sr))]
for n in (0, 1, 2):
    r = AQUI / "cache_v13" / "ref"
    p = m.create_voice_clone_prompt(ref_audio=str(r / f"ref{n}.wav"), ref_text=(r / f"ref{n}.txt").read_text(), x_vector_only_mode=False)
    for e, i, t in L:
        tx = sheismo(t); nw = len(tx.split())
        torch.manual_seed(100)
        w, sr = m.generate_voice_clone(text=tx, language="Spanish", voice_clone_prompt=p, max_new_tokens=int(nw * 9 + 48), temperature=0.62, top_k=30, subtalker_temperature=0.62)
        sf.write(str(AQUI / "cache_v13" / "prueba" / f"r{n}_{e:02d}_{i}.wav"), recorta(w[0].astype(np.float32), sr), sr, subtype="FLOAT")
        print("listo", n, e, i, flush=True)
print("== PRUEBA LISTA", flush=True)
