import sys, time, torch, soundfile as sf
from qwen_tts import Qwen3TTSModel
torch.set_num_threads(2)
t=time.time()
m = Qwen3TTSModel.from_pretrained("models/Qwen3-TTS-12Hz-0.6B-Base", device_map="cpu", dtype=torch.float32)
print("carga", round(time.time()-t,1), flush=True)
p = m.create_voice_clone_prompt(ref_audio="referencia.wav", ref_text=None, x_vector_only_mode=True)
txt = "Hace doscientos sesenta millones de años, en el sur de Pangea, un depredador del tamaño de un león recorría una llanura junto al río."
t=time.time()
w, sr = m.generate_voice_clone(text=txt, language="Spanish", voice_clone_prompt=p)
print("gen", round(time.time()-t,1), "s para", round(len(w[0])/sr,1), "s de audio", flush=True)
sf.write("prueba_clon.wav", w[0], sr)
