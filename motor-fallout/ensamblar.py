#!/usr/bin/env python3
"""Concatena los bloques numerados en MOTOR_COMPLETO.md y lista el tamaño de cada uno.

Uso: python3 ensamblar.py [--sin-17]   (el 00_LEEME nunca se incluye)
"""
import sys
from pathlib import Path

carpeta = Path(__file__).resolve().parent
salida = carpeta / "MOTOR_COMPLETO.md"
omitir = {"00_"}  # el LEEME es para el usuario, no para la IA
if "--sin-17" in sys.argv:
    omitir.add("17_")

bloques = sorted(
    p for p in carpeta.glob("[0-9][0-9]_*.md") if not any(p.name.startswith(o) for o in omitir)
)

total = 0
partes = []
for p in bloques:
    texto = p.read_text(encoding="utf-8").strip()
    partes.append(f"\n\n<!-- ===== BLOQUE {p.stem} ===== -->\n\n{texto}")
    print(f"{p.name:45s} {len(texto):>7d} caracteres")
    total += len(texto)

salida.write_text("".join(partes).lstrip() + "\n", encoding="utf-8")
print(f"{'TOTAL':45s} {total:>7d} caracteres -> {salida.name}")
