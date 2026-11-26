#!/bin/bash
cd "$(dirname "$0")"
for n in jupiter saturno neptuno marte; do python3 make_video.py $n --out salida; done
