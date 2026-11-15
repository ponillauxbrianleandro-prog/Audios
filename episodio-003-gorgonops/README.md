# Episodio 003 — Gorgonops: lo que el barro recuerda

Documental paleontológico en 2D por capas (sin modelos de imagen ni fotos: todo se genera por código).

| Carpeta / archivo | Qué es |
|---|---|
| `guion.md` | Guion completo (~23 min 30 s) con imagen, cámara, sonido, narración, citas e intriga |
| `fuentes.md` | Ficha científica (confirmado / hipótesis) y citas con su fuente |
| `muestra/muestra-30s.mp4` | Muestra de 30 s, 1920×1080, 24 fps, sin audio, subtítulos incrustados (+ `.srt`) |
| `render/` | Motor: `world.py` (suelo, río, cielo, cordillera), `plants.py` (flora), `creature.py` (animales), `engine.py` (composición y óptica), `muestra.py` (planos) |
| `musica/` | Tango instrumental original: `tango.mid`, `tango.mp3`, `stems/` y `generar_tango.py` |

```
pip install numpy scipy pillow opencv-python-headless
python3 render/muestra.py                 # ~35 min en 4 núcleos
python3 render/muestra.py --still 12 21   # fotogramas sueltos
python3 musica/generar_tango.py
```
