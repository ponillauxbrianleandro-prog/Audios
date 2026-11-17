import time, torch, numpy as np, soundfile as sf
from qwen_tts import Qwen3TTSModel
import limpiar as L
torch.set_num_threads(4)
m = Qwen3TTSModel.from_pretrained("models/Qwen3-TTS-12Hz-0.6B-Base", device_map="cpu", dtype=torch.float32)
p = m.create_voice_clone_prompt(ref_audio="referencia_v2.wav", ref_text=None, x_vector_only_mode=True)
txt = ["Hace doscientos cincuenta y cinco millones de años, este valle no tenía nombre.", "Un animal del tamaño de un león caminaba entre las colas de caballo, y nadie lo estaba mirando."]
parts=[]
t=time.time()
for s in txt:
    w, sr = m.generate_voice_clone(text=s, language="Spanish", voice_clone_prompt=p)
    parts += [w[0].astype(np.float32), np.zeros(int(0.25*sr), np.float32)]
x=np.concatenate(parts); print('gen',round(time.time()-t),'s para',round(len(x)/sr,1),'s')
sf.write('prueba_v2_cruda.wav', x, sr)
y=L.limpiar(x, sr, rt60=0.35, reverb=True, ruido=False)
sf.write('prueba_v2_limpia.wav', y, sr); print('pico',abs(y).max(),'recortes',(abs(y)>0.99).sum())
