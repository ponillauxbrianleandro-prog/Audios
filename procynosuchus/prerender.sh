#!/bin/bash
# pinta cada capa de fondo una sola vez y la guarda en public/layers/<nombre>.png
set -e
export PATH=/opt/node22/bin:$PATH
rm -rf out/layers; mkdir -p public/layers
npx remotion render src/index.ts Layers out/layers --sequence --image-format=png --concurrency=1 --log=error 2>&1 | grep -v "emory\|^$\|docker\|ower" | tail -5 || true
i=0
for n in $(npx tsx names.tsx); do
  cp "$(ls out/layers/*.png | sed -n "$((i+1))p")" "public/layers/$n.png"; i=$((i+1))
done
ls -la public/layers
