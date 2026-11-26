# Shorts de pH (azul de bromotimol)

5 videos verticales (1080×1920, 30 fps, ~36 s), sin voz: solo animación y subtítulos. Basados en la guía "Indicador de pH" de Química de los Procesos (6°2°).

| Short | Tema |
|---|---|
| 1 | ¿Qué es el pH? Escala 0–14, neutro = 7 |
| 2 | Azul de bromotimol: amarillo / verde / azul, viraje pH 6–7,6 |
| 3 | Ácidos de la cocina: limón y vinagre → amarillo |
| 4 | Bases: detergente y soda cáustica → azul; el rosado es de la fenolftaleína |
| 5 | Agua de mar (pH 8,5): ligeramente básica + repaso |

Videos en `salida/`. Regenerar: `python3 render.py [N ...]` (Pillow, numpy, ffmpeg).
`guion.md` tiene el texto de los subtítulos (una línea = un momento de la animación); `animar.py` las escenas y `motor.py` el dibujo.
