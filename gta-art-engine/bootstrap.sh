#!/usr/bin/env bash
# Instala TODO lo necesario para el motor de arte (idempotente). Un chat nuevo solo corre:  ./gta-art-engine/bootstrap.sh
set -e
cd "$(dirname "$0")"
echo "[1/4] Python venv + Blender (bpy) + NumPy/SciPy/scikit-image/Pillow/OpenEXR"
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q bpy numpy scipy scikit-image pillow OpenEXR
echo "[2/4] Three.js + PixiJS (npm)"
npm install --silent
echo "[3/4] Playwright/Chromium (render WebGL headless por software)"
if ! NODE_PATH=$(npm root -g) node -e "require('playwright')" 2>/dev/null; then
  npm install -g playwright >/dev/null 2>&1 || true
  npx playwright install chromium >/dev/null 2>&1 || true
fi
echo "[4/4] Verificación"
.venv/bin/python -c "import bpy,skimage,scipy;print('bpy',bpy.app.version_string)"
NODE_PATH=$(npm root -g) node -e "require('playwright');console.log('playwright ok')"
node -e "console.log('three', require('./node_modules/three/package.json').version, '| pixi.js', require('./node_modules/pixi.js/package.json').version)"
mkdir -p work out
echo "LISTO. Probá:  make posing   (o: tools/run_pose.sh posing 1600 1000 16 0.005)"
