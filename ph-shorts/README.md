# Shorts de pH (azul de bromotimol)

5 videos verticales (1080×1920, 30 fps, 32–36 s) basados en la guía "Indicador de pH" de Química de los Procesos (6°2°).

| Short | Tema |
|---|---|
| 1 | ¿Qué es el pH? Escala 0–14, neutro = 7 |
| 2 | Azul de bromotimol: amarillo / verde / azul, viraje pH 6–7,6 |
| 3 | Ácidos de la cocina: limón y vinagre → amarillo |
| 4 | Bases: detergente y soda cáustica → azul; el rosado es de la fenolftaleína |
| 5 | Agua de mar (pH 8,5): ligeramente básica + repaso |

Videos en `salida/`. Para regenerar: `python3 generar_audio.py` (edge-tts + ffmpeg) y luego `python3 render.py [N ...]` (Pillow).
Guion en `guion.md`: cada línea es una frase y un "beat" de la animación (en `animar.py`).
