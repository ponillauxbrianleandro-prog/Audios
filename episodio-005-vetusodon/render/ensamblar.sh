#!/bin/bash
# Une los 53 planos, quema los subtítulos, agrega el audio y codifica a 1080p en 2 pasadas con tope de tamaño (por defecto ≈ 470 MB).
set -e
cd "$(dirname "$0")"
V=../video
MAXMB=${MAXMB:-470}
python3 episodio.py --srt
N=$(ls $V/segmentos/s*.mp4 | grep -vc part)
[ "$N" -eq 53 ] || { echo "faltan planos: $N/53"; exit 1; }
ls $V/segmentos/s*.mp4 | grep -v part | sort | sed "s#^#file '$(cd $V && pwd)/#; s#segmentos/#segmentos/#; s#\$#'#" | sed "s#file '$(cd $V && pwd)/\.\./video/#file '$(cd $V && pwd)/#" > $V/lista.txt
sed -i "s#file '\(.*\)/\.\./video/#file '\1/#" $V/lista.txt
DUR=$(python3 - <<PY
import subprocess
d=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0","$V/audio/vetusodon.wav"],capture_output=True,text=True).stdout)
print(d)
PY
)
VB=$(python3 -c "print(int(($MAXMB*8*1024*1024/$DUR - 192000)/1000))")
echo "duración $DUR s · video a ${VB} kb/s para ≤ ${MAXMB} MB"
STYLE="FontName=Inter,Fontsize=16,PrimaryColour=&HF2F3F7&,OutlineColour=&H000000&,BorderStyle=1,Outline=1.0,Shadow=0,MarginV=14,Alignment=2"
VF="subtitles=$V/vetusodon.srt:original_size=1920x1080:force_style='$STYLE'"
IN="-f concat -safe 0 -i $V/lista.txt -i $V/audio/vetusodon.wav"
ffmpeg -y -loglevel error $IN -vf "$VF" -c:v libx264 -preset medium -b:v ${VB}k -pass 1 -passlogfile $V/x264 -an -f null /dev/null
ffmpeg -y -loglevel error $IN -vf "$VF" -c:v libx264 -preset medium -b:v ${VB}k -pass 2 -passlogfile $V/x264 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart $V/vetusodon.mp4
ls -la $V/vetusodon.mp4
