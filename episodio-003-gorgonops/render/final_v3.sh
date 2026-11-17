#!/bin/bash
# espera las frases puente, rehace el sonido, une los capítulos y audita las pausas
cd "$(dirname "$0")"; export MALLOC_ARENA_MAX=2
exec >> ../video/run_all.log 2>&1
until grep -q "TERMINADA (116" ../../voice_ai/narracion_v2.log 2>/dev/null; do sleep 10; done
echo "== puentes listos"
python3 sonido.py && python3 documental.py --assemble && python3 auditar_pausas.py
echo "== TERMINADO FINAL"
