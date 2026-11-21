#!/usr/bin/env python3
"""Genera el bestiario completo: a cada criatura de cada fase le toca al azar 1 a 3 variantes.

Lee las tablas de especies de los bloques 19-23, 35 y 36 (filas `| ID | Nombre | Talla | Slot | ...`)
y los arquetipos humanos del bloque 26 (filas `| U-xx | ...`). Escribe archivos
`BESTIARIO_GENERADO_01.md`, `_02.md`, ... partidos para no pasar el limite de palabras por bloque,
y `TABLA_DESBLOQUEO.md` (que enemigos se agregan en cada nivel).

Uso:
  python3 -I generar_bestiario.py [--semilla N] [--fases 1-12] [--salida DIR]
                                  [--max-palabras 1800] [--apagar H-45,H-46] [--temas animales,duende]

Reglas (bloque 27):
  - n_var = 1d3 por criatura y fase (humanos: 1d2). V1 siempre existe.
  - V1 se activa en nivel 2*slot (nivel 1 si slot 0), V2 a los 6 niveles, V3 a los 12.
  - Si el nivel pasa de 30, esa variante queda reservada a un jefe o evento.
  - Las fases 13 y 14 no dependen de la especie: se generan una vez por tema con los arquetipos humanos.
"""
import argparse
import random
import re
import sys
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
ARCHIVOS_ESPECIES = [
    "19_BESTIARIO_HERBIVOROS.md", "20_BESTIARIO_CANINOS.md", "21_BESTIARIO_INSECTOS.md",
    "22_BESTIARIO_MARINOS_BLANDOS.md", "23_BESTIARIO_PARASITOS_Y_SLIMES.md",
    "35_CRIATURAS_FANTASIA.md", "36_CRIATURAS_CIENCIA_FICCION.md",
]
ARCHIVO_HUMANOS = "26_HUMANOS_ENEMIGOS.md"
NIVEL_MAX = 30

# Formula de nombre por fase (bloque 25). {E} = nombre de la especie.
NOMBRE_FASE = {
    1: "{E}",
    2: "{E} de cuerpo semihumano",
    3: "{E} erguido",
    4: "{E} humanoide",
    5: "{E} quimera (mitad humano)",
    6: "Humano-{E}",
    7: "Persona con rasgos de {E}",
    8: "Persona-{E} (se considera {E})",
    9: "Furry de {E}",
    10: "Persona con accesorios de {E}",
    11: "Trabajador/a de espectáculo con accesorios de {E}",
    12: "Persona instintiva-{E}",
}

# Desplazamiento de slot y talla minima por fase (bloque 25): las formas humanoides aparecen mas tarde
# y tienen tamano humano como minimo.
OFFSET_SLOT = {1: 0, 2: 0, 3: 0, 4: 1, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2, 10: 2, 11: 2, 12: 2}
TALLA_MIN = {4: 2, 5: 2, 6: 3, 7: 3, 8: 3, 9: 3, 10: 3, 11: 3, 12: 3}
SLOT_MAX = 15


def talla_fase(talla, fase):
    n = int(talla.replace("T", "")) if talla.startswith("T") else 3
    return f"T{max(n, TALLA_MIN.get(fase, 1))}"


FILA = re.compile(r"^\|\s*([A-Z]{1,2}-\d+)\s*\|(.*)\|\s*$")


def parsear_fases(texto):
    fases = set()
    for parte in texto.split(","):
        parte = parte.strip()
        if "-" in parte:
            a, b = parte.split("-")
            fases.update(range(int(a), int(b) + 1))
        elif parte:
            fases.add(int(parte))
    return sorted(f for f in fases if 1 <= f <= 12)


def leer_tabla(ruta, humanos=False):
    """Devuelve lista de dicts. Respeta los encabezados '### TEMA: x'."""
    tema = "animales"
    filas = []
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^###\s*TEMA:\s*(.+)$", linea.strip(), re.IGNORECASE)
        if m:
            tema = m.group(1).strip()
            continue
        m = FILA.match(linea)
        if not m:
            continue
        id_ = m.group(1)
        if humanos != id_.startswith("U-"):
            continue
        celdas = [c.strip() for c in m.group(2).split("|")]
        try:
            if humanos:
                # Nombre | Talla | Slot | Comportamiento | V1 | V2
                nombre, talla, slot, comp = celdas[0], celdas[1], int(celdas[2]), celdas[3]
                vars_ = [v for v in celdas[4:6] if v]
            else:
                # Nombre | Talla | Slot | Comportamiento | V1 | V2 | V3
                nombre, talla, slot, comp = celdas[0], celdas[1], int(celdas[2]), celdas[3]
                vars_ = [v for v in celdas[4:7] if v]
        except (IndexError, ValueError):
            continue
        filas.append({"id": id_, "nombre": nombre, "talla": talla, "slot": slot,
                      "comp": comp, "vars": vars_, "tema": tema})
    return filas


def niveles_variantes(slot):
    base = max(1, 2 * slot)
    return [base, base + 6, base + 12]


def formato_variantes(vars_, n, slot):
    niveles = niveles_variantes(slot)
    partes = []
    for i in range(n):
        nombre = vars_[i] if i < len(vars_) else f"V{i + 1}"
        nv = niveles[i]
        partes.append(f"{nombre}@{nv}" if nv <= NIVEL_MAX else f"{nombre}@jefe")
    return " · ".join(partes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semilla", type=int, default=None)
    ap.add_argument("--fases", default="1-12")
    ap.add_argument("--salida", default=str(CARPETA / "generado"))
    ap.add_argument("--max-palabras", type=int, default=1800)
    ap.add_argument("--apagar", default="")
    ap.add_argument("--temas", default="")
    args = ap.parse_args()

    rng = random.Random(args.semilla)
    fases = parsear_fases(args.fases)
    apagadas = {x.strip() for x in args.apagar.split(",") if x.strip()}
    temas_ok = {x.strip().lower() for x in args.temas.split(",") if x.strip()}
    salida = Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)

    especies = []
    for nombre in ARCHIVOS_ESPECIES:
        ruta = CARPETA / nombre
        if ruta.exists():
            especies += leer_tabla(ruta)
    especies = [e for e in especies if e["id"] not in apagadas
                and (not temas_ok or e["tema"].lower() in temas_ok)]
    humanos = []
    ruta_h = CARPETA / ARCHIVO_HUMANOS
    if ruta_h.exists():
        humanos = leer_tabla(ruta_h, humanos=True)
    if not especies:
        sys.exit("No se encontraron especies.")

    # Armar bloques de texto agrupados por tema.
    lineas = [f"# BESTIARIO GENERADO (semilla {args.semilla})",
              "Formato: `ID.Ffase | nombre en esa fase | talla | slot | n variantes | variantes@nivel de activacion`. "
              "Cada criatura y fase tiene 1 a 3 variantes (1d3). V1 siempre es la Comun. @jefe = reservada a jefe/evento.", ""]
    por_tema = {}
    for e in especies:
        por_tema.setdefault(e["tema"], []).append(e)
    total_filas = 0
    for tema, lista in por_tema.items():
        lineas.append(f"## TEMA: {tema}")
        for e in lista:
            for f in fases:
                n = rng.randint(1, 3)
                nombre = NOMBRE_FASE[f].format(E=e["nombre"])
                slot_f = min(SLOT_MAX, e["slot"] + OFFSET_SLOT[f])
                lineas.append(f"- {e['id']}.F{f} | {nombre} | {talla_fase(e['talla'], f)} | s{slot_f} | n={n} | "
                              f"{formato_variantes(e['vars'], n, slot_f)}")
                total_filas += 1
        if humanos:
            lineas.append(f"### Humanos del tema {tema} (fases 13 y 14, una vez por tema)")
            for h in humanos:
                for f in (13, 14):
                    n = rng.randint(1, 2)
                    nom = h["nombre"] if f == 13 else f"{h['nombre']} purista"
                    lineas.append(f"- {h['id']}.F{f} | {nom} | {h['talla']} | s{h['slot']} | n={n} | "
                                  f"{formato_variantes(h['vars'], n, h['slot'])}")
                    total_filas += 1
        lineas.append("")

    # Partir en archivos por limite de palabras (en limites de linea).
    partes, actual, palabras = [], [], 0
    for ln in lineas:
        w = len(ln.split())
        if actual and palabras + w > args.max_palabras:
            partes.append(actual)
            actual, palabras = [], 0
        actual.append(ln)
        palabras += w
    if actual:
        partes.append(actual)
    for viejo in salida.glob("BESTIARIO_GENERADO_*.md"):
        viejo.unlink()
    for i, p in enumerate(partes, 1):
        enc = f"<!-- BESTIARIO GENERADO parte {i}/{len(partes)} -->\n"
        (salida / f"BESTIARIO_GENERADO_{i:02d}.md").write_text(enc + "\n".join(p) + "\n", encoding="utf-8")

    # Tabla de desbloqueo por nivel (solo fase 1 y humanos).
    por_nivel = {}
    for e in especies:
        por_nivel.setdefault(max(1, 2 * e["slot"]), []).append(f"{e['nombre']} ({e['id']})")
    for h in humanos:
        por_nivel.setdefault(max(1, 2 * h["slot"]), []).append(f"{h['nombre']} ({h['id']})")
    tabla = ["# TABLA DE DESBLOQUEO POR NIVEL (sistema 1, bloque 27)", "",
             "Cada 2 niveles se agrega un slot. Nivel 1 = pool inicial (todo lo T1).", ""]
    for nivel in sorted(por_nivel):
        tabla.append(f"## Nivel {nivel}")
        tabla.append(", ".join(sorted(por_nivel[nivel])))
        tabla.append("")
    (salida / "TABLA_DESBLOQUEO.md").write_text("\n".join(tabla), encoding="utf-8")

    print(f"{len(especies)} especies, {len(humanos)} arquetipos humanos, fases {fases[0]}-{fases[-1]}")
    print(f"{total_filas} filas en {len(partes)} archivos de <= {args.max_palabras} palabras -> {salida}")


if __name__ == "__main__":
    main()
