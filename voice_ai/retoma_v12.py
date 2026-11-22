import sys, json, numpy as np, soundfile as sf, torch
from pathlib import Path
sys.argv = [sys.argv[0], "4"]
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[0] / "episodio-005-vetusodon" / "render"))
from guion_datos import todas, sheismo
from qwen_tts import Qwen3TTSModel
torch.set_num_threads(4)
D = json.loads((AQUI / "cache_v12" / "durs_v11.json").read_text())
m = Qwen3TTSModel.from_pretrained(str(AQUI / "models/Qwen3-TTS-12Hz-1.7B-Base"), device_map="cpu", dtype=torch.float32)
ref = AQUI / "cache_v12" / "ref"
prompt = m.create_voice_clone_prompt(ref_audio=str(ref / "ref.wav"), ref_text=(ref / "ref.txt").read_text(), x_vector_only_mode=False)
def recorta(x, sr):
    e = np.abs(x) > 0.02
    a, b = np.argmax(e), len(e) - np.argmax(e[::-1])
    return x[max(0, a - int(0.05 * sr)):min(len(x), b + int(0.14 * sr))]
for esc, i, texto in todas():
    k = f"{esc:02d}_{i}"
    if k != "02_3": continue
    tx = sheismo(texto); nw = len(tx.split()); print(k, nw, "palabras · objetivo", D[k], "s", flush=True)
    best = None
    for seed in (1, 2, 3, 4):
        torch.manual_seed(seed)
        w, sr = m.generate_voice_clone(text=tx, language="Spanish", voice_clone_prompt=prompt, max_new_tokens=int(nw * 9 + 48), temperature=0.62, top_k=30, subtalker_temperature=0.62)
        x = recorta(w[0].astype(np.float32), sr); r = len(x) / sr / D[k]
        print(" semilla", seed, round(len(x) / sr, 2), "s ratio", round(r, 2), flush=True)
        if best is None or abs(r - 1) < abs(best[1] - 1): best = (x, r, sr)
        if abs(r - 1) < 0.1: break
    sf.write(str(AQUI / "cache_v12" / "raw" / f"{k}.wav"), best[0], best[2], subtype="FLOAT"); print("elegida ratio", round(best[1], 2))
