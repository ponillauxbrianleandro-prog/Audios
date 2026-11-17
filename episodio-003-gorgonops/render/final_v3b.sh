#!/bin/bash
cd "$(dirname "$0")"; export MALLOC_ARENA_MAX=2
exec >> ../video/run_all.log 2>&1
echo "== rehaciendo sonido (corrección de nivel de voz)"
python3 sonido.py && python3 documental.py --assemble && python3 auditar_pausas.py
echo "== TERMINADO FINAL B"
