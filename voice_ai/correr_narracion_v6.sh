#!/bin/bash
cd "$(dirname "$0")"; . .venv/bin/activate
for i in 1 2 3 4 5 6 7 8; do python narrar_v6.py ${HILOS:-4} ${VOZ:-d_bajo_profundo} && break; done
