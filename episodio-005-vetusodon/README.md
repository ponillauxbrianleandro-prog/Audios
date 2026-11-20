# Episodio 005 · VETUSODON «El grande» (≈ 9 min 22 s)

Documental 2D con aspecto 3D: un color dominante por escena, plantas exóticas del Pérmico, *Vetusodon elikhulu* con pelaje [inferencia],
montaje de carteles de calle (cortes < 1 s con clic de cámara y marco rojo que se expande), cuaderno del científico animado,
voz narradora diseñada (no clonada), tango original sin violín (sol menor, 120 BPM, acordeón y bandoneón) y efectos sintetizados.

| Carpeta | Contenido |
|---|---|
| `guion.md`, `fuentes.md` | guion y estado de cada afirmación ([C]onfirmado / [I]nferencia) |
| `render/` | motor 2.5D: `episodio.py` (escenas), `montaje.py`, `cuaderno.py`, `plants.py`, `biomes.py`, `creature.py`, `sonido8.py` |
| `musica/tango_v8.py` | tango por código; recupera golpes secos de la grabación de referencia |
| `previa/` | previa 360p y hoja de contactos (el 1080p pesa ≈ 470 MiB y no se versiona) |

## Regenerar
```
pip install numpy scipy pillow opencv-python-headless
python3 musica/tango_v8.py <tango_de_referencia.wav>        # stems en musica/wav
(cd ../voice_ai && python v8_voz.py 4)                       # voz (Qwen3-TTS, CPU, ~1 h)
python3 render/sonido8.py --voz                              # procesa la voz y escribe durs.json
./render/run_v8a.sh                                          # planos (reanudable); ESC="0 1 5 11" JOBS=1 ./render/run_v8a.sh en paralelo
python3 render/sonido8.py --mezcla                           # audio final -16 LUFS
./render/ensamblar.sh                                        # 2 pasadas, tope de tamaño (MAXMB=470 por defecto)
```
