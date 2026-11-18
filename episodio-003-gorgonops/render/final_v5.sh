#!/bin/bash
# v5: re-renderiza solo lo que cambia (apertura y planos con notas), mezcla el sonido, ensambla y audita.
cd "$(dirname "$0")"; export MALLOC_ARENA_MAX=2
exec >> ../video/run_all.log 2>&1
echo "== v5: render de planos faltantes"
for intento in 1 2 3 4 5 6; do python3 documental.py --seg --jobs "${JOBS:-4}" && break; done
echo "== v5: planos listos"
python3 sonido.py 0 && echo "== muestra v5 lista (capítulo 0)"
python3 sonido.py && python3 documental.py --assemble && python3 auditar_pausas.py; python3 auditar_superposiciones.py; python3 auditar_audio.py
echo "== TERMINADO V5"
