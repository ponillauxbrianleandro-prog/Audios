#!/bin/bash
# hoja de contacto: un cuadro (al 55 %) de cada corte
export PATH=/opt/node22/bin:$PATH
rm -rf out/c out/seq; mkdir -p out/c
npx remotion render src/index.ts Sheet out/seq --sequence --image-format=jpeg --scale=0.5 --log=error 2>&1 | grep -v "emory\|^$\|docker" | tail -5
ffmpeg -v error -pattern_type glob -i 'out/seq/*.jpeg' -vf "scale=480:270,tile=5x5" out/c/sheet%d.jpg; ls out/c
