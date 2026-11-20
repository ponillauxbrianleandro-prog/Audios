#!/bin/bash
# Escenas que no dependen de la duración de la voz (reanudable). Luego se renderizan 0, 1, 5 y 11.
cd "$(dirname "$0")"
export MALLOC_ARENA_MAX=2
for intento in $(seq 1 10); do
  python3 episodio.py --seg --jobs "${JOBS:-3}" --esc ${ESC:-2 3 4 6 7 8 9 10} && break
  echo "reintento $intento"
done
echo "== ESCENAS LISTAS: ${ESC:-2 3 4 6 7 8 9 10}"
