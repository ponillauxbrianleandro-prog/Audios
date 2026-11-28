#!/usr/bin/env bash
# Uso: tools/run_pose.sh <pose> <ancho> <alto> <samples> <voxel> [outdir]
# Pipeline completo: Blender (pasadas) + Three.js (fondo) + PixiJS (pintor) -> out/vaquero-<pose>.png
set -e
cd "$(dirname "$0")/.."
POSE=${1:-posing}; W=${2:-2400}; H=${3:-1500}; S=${4:-40}; VOX=${5:-0.0032}; WD=${6:-work/$POSE}
export NODE_PATH=$(npm root -g)
mkdir -p "$WD" out
[ -f work/palm_print.png ] || .venv/bin/python block1-blender/make_palm_texture.py work/palm_print.png
VOXEL=$VOX .venv/bin/python block1-blender/render_passes.py characters/vaquero-exotico "$POSE" "$WD" "$W" "$H" "$S" 2>&1 | grep -E "SDF|META|OK|Error|Trace|line " || true
CAM=$(.venv/bin/python -c "
import sys,json; sys.path.insert(0,'characters/vaquero-exotico')
src=open('characters/vaquero-exotico/build.py').read(); i=src.index('CAMERAS = {'); ns={}; exec(src[i:],{},ns)
c=ns['CAMERAS']['$POSE']; print(json.dumps(dict(lens=c['lens'],loc=c['loc'],look=c['look'])))")
node block2-three/render_bg.mjs "$WD" "$W" "$H" "$CAM" 2>&1 | grep -v "GL Driver" | tail -1
node block3-pixi/paint.mjs "/$WD" "$POSE" "/$WD" "$W" "$H" "out/vaquero-$POSE.png" 2>&1 | grep -v Warn | tail -1
