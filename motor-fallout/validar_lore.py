#!/usr/bin/env python3
"""Valida que los dos lores cumplan las reglas de las mecanicas (bloques 50 y 99) y que los bloques generados sean seguros.

Uso: python3 -I validar_lore.py
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "lores"))
sys.path.insert(0, str(RAIZ / "catalogos"))
sys.path.insert(0, str(RAIZ))
import asignaciones  # noqa: E402
import constructor  # noqa: E402
import generar_bestiario as gb  # noqa: E402
import lore_bosque  # noqa: E402
import lore_piratas  # noqa: E402

RES = []


def chk(nombre, ok, detalle=""):
    RES.append((nombre, ok, detalle))


PROHIBIDAS_SIEMPRE = re.compile(r"genital|pez[oó]n|pezones|er[oó]tic|orgasm|violaci|fetich|lascivi|lujuria|pornogr", re.I)
PERMITE_NEGADA = re.compile(r"sexual|desnud|rom[aá]ntic|sexo\b", re.I)
NEGACION = re.compile(r"ning[uú]n|nunca|sin |no hay|no participa|rechaza|solo para adultos|solo pueden|no existe|no lo|prohib|fuera de|no deben|ni |omit|no fija|eliminar|¿|solo amistad|se ignora", re.I)


def escanear(ruta):
    malos = []
    for i, ln in enumerate(ruta.read_text(encoding="utf-8").splitlines(), 1):
        if PROHIBIDAS_SIEMPRE.search(ln):
            malos.append((i, ln[:90]))
        elif PERMITE_NEGADA.search(ln) and not NEGACION.search(ln):
            malos.append((i, ln[:90]))
    return malos


def validar_lore(L, nombre):
    mundo, c = constructor.construir(L)
    esp = {}
    for n in gb.ARCHIVOS_ESPECIES:
        for e in gb.leer_tabla(RAIZ / n):
            esp[e["id"]] = e
    r = L["reparto"]
    # 1 edad y apariencia
    sin_edad = [k for k, v in mundo["NPCS"].items() if v["edad"] not in ("niño", "adulto")]
    chk(f"{nombre}: todo NPC tiene edad marcada", not sin_edad, f"{len(mundo['NPCS'])} NPC")
    mal_ap = [k for k, v in mundo["NPCS"].items() if (v["edad"] == "adulto" and v["apariencia"] != r["adultos"] and k[:3] != "ALF") or (v["edad"] == "niño" and v["apariencia"] != r["ninos"])]
    chk(f"{nombre}: apariencia coincide con REPARTO", not mal_ap, f"adultos {r['adultos']}, niños {r['ninos']}")
    alf = [k for k in mundo["NPCS"] if k.startswith("ALF")]
    chk(f"{nombre}: solo los alfas son excepción masculina", all(mundo["NPCS"][k]["apariencia"] == "masculina" for k in alf) and (bool(alf) == (nombre == "BOSQUE")), f"{len(alf)} alfas")
    # 2 nombres de una palabra
    mal_n = [v["nombre"] for k, v in mundo["NPCS"].items() if v["edad"] == "niño" and (" " in v["nombre"])]
    mal_c = [v["nombre"] for v in mundo["COMPANEROS"].values() if " " in v["nombre"]]
    chk(f"{nombre}: niños y compañeros con un solo nombre", not mal_n and not mal_c, f"{sum(1 for v in mundo['NPCS'].values() if v['edad'] == 'niño')} niños, {len(mundo['COMPANEROS'])} compañeros")
    # 3 misiones 1..5 por NPC
    cuentas = {}
    for qid, q in mundo["QUESTS"].items():
        if qid.startswith("Q"):
            cuentas[q["giver"]] = cuentas.get(q["giver"], 0) + 1
    chk(f"{nombre}: cada NPC con misión tiene de 1 a 5", all(1 <= v <= 5 for v in cuentas.values()), f"{len(cuentas)} NPC con misión, {sum(cuentas.values())} misiones")
    # 4 territorios y camas
    chk(f"{nombre}: 7 territorios", len(L["territorios"]) == 7)
    sin_cama = [t["nombre"] for t in L["territorios"] if not any(mundo["LOCS"][n]["cama"] for n in c.terr_nodos[t["id"]])]
    chk(f"{nombre}: todo territorio tiene lugar de descanso", not sin_cama, "camas: " + str(sum(1 for d in mundo["LOCS"].values() if d["cama"])))
    # 5 fases y temas
    if nombre == "BOSQUE":
        chk(f"{nombre}: alfas solo en fases 1-3", L["temas"].get("T14 alfa") == [1, 2, 3])
        chk(f"{nombre}: animales solo en fases 1-3", L["temas"].get("T1 animales") == [1, 2, 3])
    else:
        chk(f"{nombre}: sin alfas ni más temas", set(L["temas"]) == {"T1 animales"})
        chk(f"{nombre}: criaturas solo en fase 1 (enemigos)", L["temas"]["T1 animales"] == [1])
    # 6 pools validos
    malos = [(p, s) for p, ids in L["pools"].items() for s in ids if s not in esp]
    chk(f"{nombre}: todas las especies de los pools existen en los bestiarios", not malos, str(malos[:3]))
    prohibidos = [s for ids in L["pools"].values() for s in ids if s.startswith(("FA-", "X-", "AL-"))]
    chk(f"{nombre}: pools sin temas apagados", not prohibidos, str(prohibidos[:3]))
    # 7 facciones separadas
    chk(f"{nombre}: facciones sin grupos mixtos adulto-niño", all("mixta" not in f[1] for f in L["facciones"]), f"{len(L['facciones'])} facciones")
    # 8 roles excluidos
    rol_mal = [v["arq"] for v in mundo["NPCS"].values() if any(k in v["arq"] for k in ("esclavista", "cultista", "saqueador", "traficante"))]
    chk(f"{nombre}: sin NPC de roles excluidos", not rol_mal, str(rol_mal[:3]))
    # 9 misiones validas
    malas = []
    for qid, q in mundo["QUESTS"].items():
        for p in q["steps"]:
            for a in p[1:3]:
                if isinstance(a, str) and (a.startswith(("L-", "Q-", "Z-"))) and a not in mundo["LOCS"]:
                    malas.append((qid, a))
            if p[0] == "get" and p[2] not in mundo["OBJETOS"]:
                malas.append((qid, p[2]))
            if p[0] == "talk" and p[1] not in mundo["NPCS"]:
                malas.append((qid, p[1]))
    chk(f"{nombre}: todos los pasos de misión apuntan a lugares, objetos y NPC que existen", not malas, str(malas[:3]))
    items = {it for d in mundo["LOCS"].values() for cc in d["cont"] for it in cc[4]}
    faltan = [p[2] for q in mundo["QUESTS"].values() for p in q["steps"] if p[0] == "get" and p[2] not in items and not p[2].endswith(("baul",))]
    chk(f"{nombre}: todo objeto de misión está en algún contenedor", not faltan, str(faltan[:3]))
    # 10 conexiones
    alcanzables = set()
    pila = [mundo["PROTAGONISTA"]["hogar"]]
    while pila:
        x = pila.pop()
        if x in alcanzables:
            continue
        alcanzables.add(x)
        for y, d in mundo["LOCS"].items():
            if x in d["conn"] or y in mundo["LOCS"][x]["conn"]:
                pila.append(y)
    chk(f"{nombre}: todo el mapa es alcanzable desde el hogar", len(alcanzables) == len(mundo["LOCS"]), f"{len(alcanzables)}/{len(mundo['LOCS'])} nodos")
    return mundo, c


def main():
    validar_lore(lore_bosque.LORE, "BOSQUE")
    validar_lore(lore_piratas.LORE, "PIRATAS")
    # catalogos
    a = asignaciones.asignar()
    chk("catálogos: NPC adultos, niños, respawneables y compañeros presentes", all(len(a[k]) for k in a), str({k: len(v) for k, v in a.items()}))
    chk("catálogos: ningún niño con rol hostil adulto", not any(x["lugar"] == "HOS" and "niño" in x["rol"] and "atrapado" not in x["rol"] and "liberado" not in x["rol"] for x in a["ninos"]))
    # seguridad en textos
    archivos = sorted(list(RAIZ.glob("[5-9][0-9]_*.md")) + list((RAIZ / "lores").glob("*/*.md")))
    malos = {}
    for f in archivos:
        m = escanear(f)
        if m:
            malos[f.name] = m[:2]
    chk(f"seguridad: sin contenido explícito en {len(archivos)} bloques nuevos (53-99 y lores)", not malos, str(list(malos.items())[:2]))
    # tamano
    grandes = [(f.name, len(f.read_text(encoding='utf-8').split())) for f in archivos if len(f.read_text(encoding='utf-8').split()) > 2000]
    chk("tamaño: ningún bloque supera 2000 palabras", not grandes, str(grandes[:3]))
    ok = sum(1 for r in RES if r[1])
    print(f"{ok}/{len(RES)} validaciones aprobadas")
    for n, o, d in RES:
        print(("✅ " if o else "❌ ") + n + (f" — {d}" if d else ""))
    lines = [f"# Validación de los lores y catálogos", "", f"**{ok}/{len(RES)} validaciones aprobadas.**", "", "| Validación | Resultado | Detalle |", "|---|---|---|"]
    for n, o, d in RES:
        lines.append(f"| {n} | {'✅' if o else '❌'} | {d} |")
    out = RAIZ / "simulacion"
    out.mkdir(exist_ok=True)
    (out / "VALIDACION_DE_LORES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if ok == len(RES) else 1


if __name__ == "__main__":
    sys.exit(main())
