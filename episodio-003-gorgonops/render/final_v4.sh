#!/bin/bash
# v4 (audio): espera la narración cruda, procesa la voz, mezcla, ensambla y audita.
cd "$(dirname "$0")"; export MALLOC_ARENA_MAX=2
exec >> ../video/run_all.log 2>&1
until grep -q "NARRACION CRUDA TERMINADA" ../../voice_ai/narracion_v3.log 2>/dev/null; do sleep 10; done
echo "== narración cruda lista"
( cd ../../voice_ai && . .venv/bin/activate && python procesar_voz.py ) || { echo "== ERROR procesar_voz"; exit 1; }
echo "== voz procesada"
python3 sonido.py 0 && echo "== muestra lista (capítulo 0)"
python3 sonido.py && python3 documental.py --assemble && python3 auditar_pausas.py; python3 auditar_audio.py
echo "== TERMINADO V4"
