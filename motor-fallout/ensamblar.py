#!/usr/bin/env python3
"""Concatena los bloques numerados en MOTOR_COMPLETO.md y lista palabras por bloque.

Uso: python3 -I ensamblar.py [--sin-17] [--sin-fantasia] [--sin-scifi] [--limite 2000]
  - El 00_LEEME nunca se incluye (es para el autor).
  - Avisa si un bloque supera el limite de palabras (por defecto 2000).
  - No incluye la carpeta generado/ (el bestiario generado se pega por separado).
"""
import sys
from pathlib import Path

carpeta = Path(__file__).resolve().parent
salida = carpeta / "MOTOR_COMPLETO.md"
omitir = {"00_"}
if "--sin-17" in sys.argv:
    omitir.add("17_")
if "--sin-fantasia" in sys.argv:
    omitir.add("35_")
if "--sin-scifi" in sys.argv:
    omitir.add("36_")
limite = 2000
if "--limite" in sys.argv:
    limite = int(sys.argv[sys.argv.index("--limite") + 1])

bloques = sorted(
    p for p in carpeta.glob("[0-9][0-9]_*.md") if not any(p.name.startswith(o) for o in omitir)
)

total = 0
partes = []
for p in bloques:
    texto = p.read_text(encoding="utf-8").strip()
    palabras = len(texto.split())
    aviso = "  <-- SUPERA EL LIMITE" if palabras > limite else ""
    partes.append(f"\n\n<!-- ===== BLOQUE {p.stem} ===== -->\n\n{texto}")
    print(f"{p.name:45s} {palabras:>6d} palabras{aviso}")
    total += palabras

salida.write_text("".join(partes).lstrip() + "\n", encoding="utf-8")
print(f"{'TOTAL':45s} {total:>6d} palabras -> {salida.name}")
