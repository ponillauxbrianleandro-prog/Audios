#!/bin/bash
# Une los planos EN EL ORDEN DE LA PELÍCULA, quema los subtítulos, agrega el audio y codifica a 1080p en 2 pasadas con tope de tamaño (≈470 MB).
set -e
cd "$(dirname "$0")"
V=../video
MAXMB=${MAXMB:-470}
SALIDA=${SALIDA:-vetusodon-v9.mp4}
/usr/local/bin/python3 episodio.py --srt
/usr/local/bin/python3 - <<PY
import sys; sys.path.insert(0, '.')
import episodio as E
TL, _ = E.timeline()
falta = [E.seg_path(c, j).name for c in TL for j in range(len(c['shots'])) if not E.seg_path(c, j).exists()]
assert not falta, f"faltan planos: {falta[:5]}"
open('$V/lista.txt', 'w').write(''.join(f"file '{E.seg_path(c, j).resolve()}'\n" for c in TL for j in range(len(c['shots']))))
print(sum(len(c['shots']) for c in TL), 'planos en orden')
PY
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $V/audio/vetusodon.wav)
VB=$(python3 -c "print(int(($MAXMB*8*1024*1024/$DUR - 192000)/1000))")
echo "duración $DUR s · video a ${VB} kb/s para ≤ ${MAXMB} MB"
STYLE="FontName=Inter,Fontsize=16,PrimaryColour=&HF2F3F7&,OutlineColour=&H000000&,BorderStyle=1,Outline=1.0,Shadow=0,MarginV=14,Alignment=2"
VF="subtitles=$V/vetusodon.srt:original_size=1920x1080:force_style='$STYLE'"
IN="-f concat -safe 0 -i $V/lista.txt -i $V/audio/vetusodon.wav"
ffmpeg -y -loglevel error $IN -vf "$VF" -c:v libx264 -preset medium -b:v ${VB}k -pass 1 -passlogfile $V/x264 -an -f null /dev/null
ffmpeg -y -loglevel error $IN -vf "$VF" -c:v libx264 -preset medium -b:v ${VB}k -pass 2 -passlogfile $V/x264 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart $V/$SALIDA
ls -la $V/$SALIDA
