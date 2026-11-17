"""Datos compartidos entre musica.py y video.py (línea de tiempo del episodio 003)."""
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
TIMELINE = AQUI / "audio" / "timeline.json"

# bpm por escena: el tango acelera y frena según lo que se muestra
TEMPOS = [128, 118, 124, 112, 96, 132, 120, 126, 100, 116]

# (escena 1-10, segundos desde el inicio de la escena, efecto)
SFX = [
    (1, 0.00, "boing"), (1, 0.55, "whoosh"), (1, 1.60, "pop"), (1, 2.40, "whoosh"), (1, 3.60, "pop"),
    (1, 4.50, "whoosh"),
    (2, 0.00, "swish"), (2, 1.20, "splash"), (2, 3.00, "gruñido"), (2, 4.30, "splash"), (2, 6.10, "pop"),
    (2, 8.00, "whoosh"),
    (3, 0.00, "swish"), (3, 0.50, "pop"), (3, 1.00, "tada"), (3, 3.20, "pop"), (3, 5.00, "whoosh"),
    (4, 0.30, "crunch"), (4, 0.70, "crunch"), (4, 1.10, "crunch"), (4, 1.50, "crunch"), (4, 1.90, "crunch"),
    (4, 3.00, "crunch"), (4, 3.40, "crunch"), (4, 3.80, "crunch"), (4, 6.00, "pop"), (4, 7.50, "pop"),
    (4, 9.00, "crunch"), (4, 9.40, "crunch"), (4, 11.0, "crunch"), (4, 11.4, "crunch"),
    (5, 0.00, "swish"), (5, 0.60, "stamp"), (5, 3.50, "pop"), (5, 6.50, "pop"), (5, 8.80, "crunch"),
    (6, 0.30, "pffff"), (6, 1.80, "pop"), (6, 3.30, "pffff"),
    (7, 0.00, "swish"), (7, 1.00, "pop"), (7, 2.00, "pop"), (7, 3.00, "pop"), (7, 5.40, "crunch"),
    (7, 5.80, "crunch"), (7, 6.30, "pop"),
    (8, 0.30, "pop"), (8, 1.00, "pop"), (8, 1.60, "pop"), (8, 4.20, "whoosh"), (8, 6.50, "pop"),
    (9, 0.00, "crack"), (9, 0.60, "sparkle"), (9, 2.00, "sparkle"), (9, 3.40, "pop"),
    (10, 0.00, "swish"), (10, 1.00, "sparkle"), (10, 4.50, "pop"), (10, 6.80, "tada"),
]


def cargar():
    d = json.loads(TIMELINE.read_text(encoding="utf-8"))
    esc = d["escenas"]
    for i, e in enumerate(esc):
        e["ini_v"] = 0.0 if i == 0 else e["inicio"]
        e["fin_v"] = esc[i + 1]["inicio"] if i + 1 < len(esc) else d["total"]
    return d
