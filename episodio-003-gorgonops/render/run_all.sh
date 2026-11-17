#!/bin/bash
# v3: espera la narración, renderiza todo (reanudable), mezcla el sonido, une los capítulos y audita las pausas.
cd "$(dirname "$0")"
export MALLOC_ARENA_MAX=2
LOG=../video/run_all.log
exec >> "$LOG" 2>&1
until grep -q "NARRACION TERMINADA" ../../voice_ai/narracion_v2.log 2>/dev/null; do sleep 20; done
for intento in 1 2 3 4 5 6 7 8; do
  echo "== renderizando (intento $intento)"
  python3 documental.py --seg --jobs "${JOBS:-4}" && break
done
python3 sonido.py && python3 documental.py --assemble && python3 auditar_pausas.py
echo "== TERMINADO"
