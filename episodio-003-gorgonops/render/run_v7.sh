#!/bin/bash
# v7: renderiza todos los planos (reanudable) con paleta selectiva, volumen y cámara nuevos; luego ensambla.
cd "$(dirname "$0")"
export MALLOC_ARENA_MAX=2
for intento in $(seq 1 12); do
  echo "== renderizando (intento $intento)"
  python3 documental.py --seg --jobs "${JOBS:-4}" && break
done
echo "== SEGMENTOS LISTOS"
