#!/bin/bash
# v6b: voz estirada a cada escena YA renderizada (sin reajustar el video): mezcla, ensamblado y auditorías
cd "$(dirname "$0")"; export MALLOC_ARENA_MAX=2
exec >> ../video/run_all.log 2>&1
echo "== v6b: mezcla"
python3 sonido.py 0 && echo "== muestra v6b lista (capítulo 0)"
python3 sonido.py && python3 documental.py --assemble && python3 auditar_pausas.py; python3 auditar_superposiciones.py; python3 auditar_sincronia.py; python3 auditar_audio.py
echo "== TERMINADO V6B"
