# voice_ai

Entorno local de síntesis de voz con [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS).

## Instalación

```bash
cd voice_ai
./setup_qwen3_tts.sh
```

El script inspecciona el sistema, crea un venv con Python 3.12, clona el repositorio, instala `qwen-tts` y `huggingface_hub`, y descarga los modelos. Se puede volver a ejecutar: solo completa lo que falte.

| Opción | Efecto |
|---|---|
| *(ninguna)* | Modelos 0.6B; los 1.7B solo si hay GPU NVIDIA con 8 GB de VRAM o más |
| `--with-large` | Fuerza la descarga de los modelos 1.7B (unos 9 GB más) |
| `--no-large` | Nunca descarga los modelos 1.7B |

Nada de lo descargado se versiona (`Qwen3-TTS/`, `models/`, `.venv/` y `outputs/` están en `.gitignore`).

## Modelos

| Modelo | Tamaño | Se descarga |
|---|---|---|
| `Qwen3-TTS-Tokenizer-12Hz` | 0.7 GB | siempre |
| `Qwen3-TTS-12Hz-0.6B-CustomVoice` | 2.5 GB | siempre |
| `Qwen3-TTS-12Hz-0.6B-Base` (clonación de voz) | 2.5 GB | siempre |
| `Qwen3-TTS-12Hz-1.7B-CustomVoice` | 4.5 GB | con GPU o `--with-large` |
| `Qwen3-TTS-12Hz-1.7B-VoiceDesign` | 4.5 GB | con GPU o `--with-large` |

## Uso

```bash
source .venv/bin/activate
```

```python
import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

model = Qwen3TTSModel.from_pretrained(
    "models/Qwen3-TTS-12Hz-0.6B-CustomVoice",
    device_map="cpu",          # "cuda:0" si hay GPU
    dtype=torch.float32,       # torch.bfloat16 en GPU
)
wavs, sr = model.generate_custom_voice(
    text="Hola, che. Esta es una prueba de voz.",
    language="Spanish",
    speaker="Ryan",
)
sf.write("outputs/prueba.wav", wavs[0], sr)
```

Voces de CustomVoice: `aiden`, `dylan`, `eric`, `ono_anna`, `ryan`, `serena`, `sohee`, `uncle_fu`, `vivian`.

## Notas

- `huggingface_hub` se instala en la rama 0.x: `qwen-tts` fija `transformers==4.57.3`, que no admite la 1.x.
- Sin GPU se instala PyTorch solo-CPU. En 4 núcleos, el modelo 0.6B tarda unos 14 s en generar 3.6 s de audio.
- Requisitos de disco: unos 10 GB para los modelos 0.6B más el entorno, 20 GB con los 1.7B.
