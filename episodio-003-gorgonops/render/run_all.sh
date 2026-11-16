#!/bin/bash
# Renderiza todo el documental (reanudable), arma el sonido y une los capítulos.
cd "$(dirname "$0")"
export MALLOC_ARENA_MAX=2
for intento in 1 2 3 4 5 6 7 8; do
  echo "== renderizando (intento $intento)"
  python3 documental.py --seg --jobs "${JOBS:-4}" && break
done
python3 sonido.py
python3 documental.py --assemble
echo "== TERMINADO"
