#!/usr/bin/env python3
"""Arma el skill de Cowork con la voz de Tomás: OUTPUT/voz-tomas-argentina.zip.

El zip incluye una copia del narrador.py actual, así el skill no duplica código
en el repositorio. Volver a ejecutarlo después de cambiar narrador.py.
"""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

RAIZ = Path(__file__).resolve().parent
NOMBRE = "voz-tomas-argentina"
DESTINO = RAIZ / "OUTPUT" / f"{NOMBRE}.zip"

CONTENIDO = {
    "SKILL.md": RAIZ / "cowork" / NOMBRE / "SKILL.md",
    "scripts/narrador.py": RAIZ / "narrador.py",
    "requirements.txt": RAIZ / "requirements.txt",
}


def main() -> None:
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(DESTINO, "w", ZIP_DEFLATED) as paquete:
        for ruta_en_zip, origen in CONTENIDO.items():
            paquete.write(origen, f"{NOMBRE}/{ruta_en_zip}")
    print(f"Skill empaquetado en {DESTINO.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
