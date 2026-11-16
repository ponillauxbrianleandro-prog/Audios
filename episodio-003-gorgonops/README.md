# Episodio 003 — Gorgonops: lo que el barro recuerda

Documental paleontológico en 2D por capas (sin modelos de imagen ni fotos: todo se genera por código).

| Carpeta / archivo | Qué es |
|---|---|
| `guion.md` | Guion completo (~23 min 30 s) con imagen, cámara, sonido, narración, citas e intriga |
| `fuentes.md` | Ficha científica (confirmado / hipótesis) y citas con su fuente |
| `muestra/muestra-30s.mp4` | Muestra 1 de 30 s (1920×1080, 24 fps, sin audio, subtítulos incrustados) |
| `muestra/muestra-30s-v2.mp4` | Muestra 2: 15 s de diseño plano «Sombra» con los datos del animal + 15 s del documental con los biomas nuevos |
| `render/` | Motor: `world.py` (suelo, río, cielo, cordillera, nieve, hielo), `plants.py` (flora y variantes nevadas), `creature.py` (animales), `biomes.py` (biomas y capas de plantas), `engine.py` (composición, óptica y vida ambiental), `sombra.py` (diseño plano del canal), `graficos.py` (láminas científicas), `documental.py` (tabla de planos, tiempos y render por planos), `sonido.py` (ambiente y tango por capítulo), `muestra.py` / `muestra2.py` (muestras) |
| `video/` | Salida del documental completo: `capitulos/` (con subtítulos y audio), `master/` (copia limpia sin audio ni subtítulos, para mezclar la voz) |
| `musica/` | Tango instrumental original: `tango.mid`, `tango.mp3`, `stems/` y `generar_tango.py` |

```
pip install numpy scipy pillow opencv-python-headless
python3 render/muestra2.py                # muestra 2, ~15 min en 4 núcleos
render/run_all.sh                        # documental completo (reanudable, varias horas)
python3 render/muestra.py --still 12 21   # fotogramas sueltos
python3 musica/generar_tango.py
```
