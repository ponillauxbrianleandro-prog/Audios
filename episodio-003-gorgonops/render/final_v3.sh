#!/bin/bash
# espera las frases puente, rehace el sonido, une los capítulos y audita las pausas
cd "$(dirname "$0")"; export MALLOC_ARENA_MAX=2
exec >> ../video/run_all.log 2>&1
until python3 -c "import json,sys;L=json.load(open('../../voice_ai/lineas_v2.json'));D=json.load(open('../../voice_ai/duraciones.json'));sys.exit(0 if all(o['key'] in D for o in L) else 1)" 2>/dev/null; do sleep 10; done
echo "== puentes listos"
python3 sonido.py && python3 documental.py --assemble && python3 auditar_pausas.py
echo "== TERMINADO FINAL"
