#!/usr/bin/env python3
"""Entrena un LoRA de ESTILO (arte GTA IV) sobre SD1.5 en CPU. Aprende de ilustraciones de referencia; no guarda las imagenes.
Uso: venv/bin/python entrenar_lora.py <carpeta_imagenes> <captions.json> <salida_dir> [--steps 400 --res 384 --rank 16 --lr 1e-4]
captions.json: {"archivo.jpg": "descripcion", ...}   (todas las descripciones empiezan con el disparador 'gta4art style')"""
import json, os, random, sys, time, torch
from PIL import Image
import numpy as np
from diffusers import StableDiffusionPipeline, DDPMScheduler
from diffusers.utils import convert_state_dict_to_diffusers
from peft import LoraConfig, get_peft_model_state_dict, set_peft_model_state_dict

a = sys.argv[1:]; carpeta, capj, out = a[0], a[1], a[2]
opt = lambda n, d: type(d)(a[a.index("--" + n) + 1]) if "--" + n in a else d
STEPS, RES, RANK, LR = opt("steps", 400), opt("res", 384), opt("rank", 16), opt("lr", 1e-4)
torch.set_num_threads(4); torch.manual_seed(0); random.seed(0)
pipe = StableDiffusionPipeline.from_pretrained("stable-diffusion-v1-5/stable-diffusion-v1-5", torch_dtype=torch.float32, safety_checker=None)
vae, unet, te, tok = pipe.vae.eval(), pipe.unet, pipe.text_encoder.eval(), pipe.tokenizer
sched = DDPMScheduler.from_config(pipe.scheduler.config)
for m in (vae, te): m.requires_grad_(False)
unet.requires_grad_(False)
unet.add_adapter(LoraConfig(r=RANK, lora_alpha=RANK, init_lora_weights="gaussian", target_modules=["to_k", "to_q", "to_v", "to_out.0"]))
params = [p for p in unet.parameters() if p.requires_grad]
for p in params: p.data = p.data.float()
caps = json.load(open(capj))
# dataset: 2-3 recortes cuadrados por imagen (cubre composicion) + espejo
muestras = []
for f, c in caps.items():
    im = Image.open(os.path.join(carpeta, f)).convert("RGB"); w, h = im.size; s = min(w, h)
    pos = [(0, 0), (w - s, h - s), ((w - s) // 2, (h - s) // 2)] if w != h else [(0, 0)]
    for (x, y) in pos:
        cr = im.crop((x, y, x + s, y + s)).resize((RES, RES), Image.LANCZOS)
        for fl in (False, True):
            t = cr.transpose(Image.FLIP_LEFT_RIGHT) if fl else cr
            muestras.append((torch.from_numpy(np.asarray(t)).permute(2, 0, 1).float() / 127.5 - 1, c))
print("muestras", len(muestras), flush=True)
with torch.no_grad():
    lat = [vae.encode(x[None]).latent_dist.sample() * vae.config.scaling_factor for x, _ in muestras]
    emb = [te(tok(c, padding="max_length", max_length=tok.model_max_length, truncation=True, return_tensors="pt").input_ids)[0] for _, c in muestras]
opt_ = torch.optim.AdamW(params, lr=LR, weight_decay=1e-2)
ck = os.path.join(out, "estado.pt"); inicio = 1
if os.path.exists(ck):   # reanudar tras un reinicio del contenedor
    st = torch.load(ck); set_peft_model_state_dict(unet, st["lora"]); opt_.load_state_dict(st["opt"]); inicio = st["step"] + 1; print("reanudando desde", inicio, flush=True)
unet.train(); t0 = time.time(); ema = None
for step in range(inicio, STEPS + 1):
    i = random.randrange(len(muestras)); l = lat[i]; n = torch.randn_like(l)
    t = torch.randint(0, sched.config.num_train_timesteps, (1,))
    pred = unet(sched.add_noise(l, n, t), t, emb[i]).sample
    loss = torch.nn.functional.mse_loss(pred, n)
    loss.backward(); torch.nn.utils.clip_grad_norm_(params, 1.0); opt_.step(); opt_.zero_grad()
    ema = loss.item() if ema is None else .95 * ema + .05 * loss.item()
    if step % 10 == 0: print(f"{step}/{STEPS} loss {ema:.4f} {(time.time()-t0)/(step-inicio+1):.1f}s/paso", flush=True)
    if step % 20 == 0:
        os.makedirs(out, exist_ok=True); torch.save({"lora": get_peft_model_state_dict(unet), "opt": opt_.state_dict(), "step": step}, ck + ".tmp"); os.replace(ck + ".tmp", ck)
    if step % 100 == 0 or step == STEPS:
        os.makedirs(out, exist_ok=True)
        StableDiffusionPipeline.save_lora_weights(out, unet_lora_layers=convert_state_dict_to_diffusers(get_peft_model_state_dict(unet)), safe_serialization=True)
print("LoRA guardado en", out)
