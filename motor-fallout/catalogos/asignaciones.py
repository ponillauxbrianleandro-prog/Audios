"""Asigna a cada NPC arquetipo de 1 a 5 misiones (azar con semilla fija) y les da nombre segun personalidad y tipo.

Es la UNICA fuente de NPC y misiones: la usan los bloques de catalogo y los constructores de mundos del simulador.
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import datos_misiones as dm  # noqa: E402
import datos_npc as dn  # noqa: E402

# tipos de mision extra por tipo de lugar (para completar hasta 5 si el rol tiene pocos)
EXTRA = {
    "REF": ["REC", "MSJ", "ENS", "INV", "HCK", "FAM"], "ASE": ["REC", "MSJ", "FIE", "NEG", "COM", "DET", "RCL"], "MIL": ["VIG", "AMN", "DEF", "ESC", "INV"],
    "TOR": ["NEG", "DET", "REC", "MSJ"], "HOS": ["AMN", "RSC", "INF", "JEF"], "CAM": ["ESC", "REC", "MSJ", "AMN", "EXP"], "ESP": ["PUZ", "ART", "INV", "REC"],
    "SUB": ["EXP", "DEF", "REC", "NEG"], "IND": ["RCL", "AMN", "DEF", "TRA", "COM"], "CIE": ["HCK", "INV", "REC", "PUZ"], "COM": ["COM", "REC", "TRA", "DET"],
    "PUE": ["ESC", "TRA", "RCL", "REC", "MSJ"],
}


def _n_misiones(rng):
    return rng.choices([1, 2, 3, 4, 5], weights=[20, 25, 25, 20, 10])[0]


def _parse(linea, ncampos):
    return [c.strip() for c in linea.split(";")][:ncampos]


def _asignar_misiones(rng, pref, idx, claves, lugar, permitidos):
    n = _n_misiones(rng)
    tipos = list(permitidos)
    rng.shuffle(tipos)
    pool = [t for t in EXTRA.get(lugar, ["REC"]) if t not in tipos]
    rng.shuffle(pool)
    tipos += pool
    tipos = tipos[:n]
    out = []
    usados = set()
    for k, t in enumerate(tipos, 1):
        nombre = dm.nombre_mision(rng, t, claves)
        while nombre in usados:
            nombre = dm.nombre_mision(rng, t, claves)
        usados.add(nombre)
        out.append(dict(id=f"{pref}-{idx:03d}-{k}", nombre=nombre, tipo=t))
    return out


def asignar(semilla=2026):
    rng = random.Random(semilla)
    adultos, resp, ninos, comps = [], [], [], []
    for i, linea in enumerate(dn.ADULTOS, 1):
        rol, claves, lugar, tipos = _parse(linea, 4)
        cl = [c.strip() for c in claves.split(",")]
        adultos.append(dict(id=f"NPC-{i:03d}", rol=rol, claves=cl, lugar=lugar, edad="adulto",
                            misiones=_asignar_misiones(rng, "QA", i, cl, lugar, tipos.split(","))))
    for i, linea in enumerate(dn.RESPAWN, 1):
        rol, claves, lugar = _parse(linea, 3)
        resp.append(dict(id=f"RSP-{i:03d}", rol=rol, claves=[c.strip() for c in claves.split(",")], lugar=lugar, edad="adulto o niño según lore", misiones=[]))
    for i, linea in enumerate(dn.NINOS, 1):
        rol, claves, lugar, tipos = _parse(linea, 4)
        cl = [c.strip() for c in claves.split(",")]
        ninos.append(dict(id=f"NIN-{i:03d}", rol=rol, claves=cl, lugar=lugar, edad="niño",
                          misiones=_asignar_misiones(rng, "QN", i, cl, lugar, tipos.split(","))))
    for i, linea in enumerate(dn.COMPANEROS, 1):
        arq, edad, pers = _parse(linea, 3)
        comps.append(dict(id=f"CMP-{i:03d}", rol=arq, edad=edad, personalidad=pers, claves=[], lugar="CAM", misiones=[]))
    return dict(adultos=adultos, resp=resp, ninos=ninos, comps=comps)


if __name__ == "__main__":
    r = asignar()
    tot = sum(len(x["misiones"]) for x in r["adultos"]) + sum(len(x["misiones"]) for x in r["ninos"])
    print({k: len(v) for k, v in r.items()}, "misiones asignadas:", tot)
    print(r["adultos"][0])
