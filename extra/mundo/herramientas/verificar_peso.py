#!/usr/bin/env python3
"""Verifica que un video grabado respete la regla de peso de Extra.
Uso: python3 verificar_peso.py video.mp4
Referencia: ~100 MB para un video largo normal; tope duro 400 MB. Si MB por minuto es muy alto,
casi seguro se exporto el mundo en vez de grabar la animacion."""
import os, subprocess, sys

if len(sys.argv) < 2:
    sys.exit(__doc__)
f = sys.argv[1]
mb = os.path.getsize(f) / 1048576
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]).decode())
mpm = mb / (dur / 60)
print(f"{f}: {mb:.1f} MB, {dur:.1f}s, {mpm:.1f} MB/min")
if mb > 400:
    sys.exit("RECHAZADO: supera el tope de 400 MB (¿se exporto el mundo completo?)")
if mpm > 60 or mb > 100 and dur < 600:
    print("ADVERTENCIA: peso alto para esta duracion (patron ~100 MB por video largo). Revisar bitrate/CRF.")
else:
    print("OK: peso dentro del patron.")
