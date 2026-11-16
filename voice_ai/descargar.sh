#!/bin/bash
cd "$(dirname "$0")"; . .venv/bin/activate
for m in Qwen3-TTS-Tokenizer-12Hz Qwen3-TTS-12Hz-0.6B-CustomVoice Qwen3-TTS-12Hz-0.6B-Base Qwen3-TTS-12Hz-1.7B-CustomVoice Qwen3-TTS-12Hz-1.7B-VoiceDesign; do
  hf download Qwen/$m --local-dir models/$m && echo "LISTO $m"
done
echo "== DESCARGAS TERMINADAS"
