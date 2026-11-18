#!/bin/bash
cd "$(dirname "$0")"; . .venv/bin/activate
for i in 1 2 3 4 5 6; do python retomas_v3.py ${HILOS:-4} && break; done
