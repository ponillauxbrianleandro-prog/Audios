#!/bin/bash
# Regenera la locución con la voz Mario (edge-tts) en tono energético.
# Requiere: pip install edge-tts
cd "$(dirname "$0")"
edge-tts --voice es-PY-MarioNeural --rate=+12% --pitch=+4Hz \
  --file locucion.txt --write-media audio.mp3 --write-subtitles audio.srt
