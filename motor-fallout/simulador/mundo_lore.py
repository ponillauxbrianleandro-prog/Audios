"""Mundo generado a partir de un lore (variable de entorno LORE=bosque|piratas).

Se usa con:  MUNDO=mundo_lore LORE=bosque python3 -I ejecutar.py
"""
import importlib
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "lores"))
sys.path.insert(0, str(RAIZ / "catalogos"))

import constructor  # noqa: E402

_lore_nombre = os.environ.get("LORE", "bosque")
_mod = importlib.import_module(f"lore_{_lore_nombre}")
LORE = _mod.LORE
_mundo, CONSTRUCTOR = constructor.construir(LORE, int(os.environ.get("SEMILLA_MUNDO", "2026")))
globals().update(_mundo)
