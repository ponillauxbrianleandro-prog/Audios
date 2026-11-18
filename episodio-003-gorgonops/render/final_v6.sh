#!/bin/bash
# v6: espera la narración con la voz diseñada, la procesa, reajusta el video a la voz, mezcla, ensambla y audita (incluye sincronía).
cd "$(dirname "$0")"; export MALLOC_ARENA_MAX=2
exec >> ../video/run_all.log 2>&1
until grep -q "NARRACION V6 TERMINADA" ../../voice_ai/narracion_v6.log 2>/dev/null; do sleep 15; done
echo "== v6: narración lista"
echo cache_v6 > ../../voice_ai/cache_activa.txt
( cd ../../voice_ai && . .venv/bin/activate && python procesar_voz.py ) || { echo "== ERROR procesar_voz"; exit 1; }
echo "== v6: voz procesada"
python3 retimear.py --jobs 2 || { echo "== ERROR retimear"; exit 1; }
echo "== v6: video reajustado"
export SEG_DIR=segmentos_r
python3 sonido.py 0 && echo "== muestra v6 lista (capítulo 0)"
python3 sonido.py && python3 documental.py --assemble && python3 auditar_pausas.py; python3 auditar_superposiciones.py; python3 auditar_sincronia.py; python3 auditar_audio.py
echo "== TERMINADO V6"
