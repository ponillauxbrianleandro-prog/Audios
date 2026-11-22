#!/usr/bin/env python3
"""Escribe los textos de los dos lores (carpeta lores/BOSQUE y lores/PIRATAS) en bloques de <= 1850 palabras.

Los textos salen de los mismos datos que usa el simulador (lores/lore_*.py + constructor), asi que todo es consistente.
Uso: python3 -I generar_lores.py
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "lores"))
sys.path.insert(0, str(RAIZ / "catalogos"))
import constructor  # noqa: E402
import lore_bosque  # noqa: E402
import lore_piratas  # noqa: E402
import datos_misiones as dm  # noqa: E402

LIMITE = 1850
CL = {"S": "segura", "N": "normal", "H": "hostil"}
NOMBRES_MP = {
    "bosque": ["Perdido entre los helechos", "Rastros de la tía", "La voz de la torre de señales", "El saber de la biblioteca vieja", "El mapa que se mueve",
               "Las aguas del claro", "Retomar el rastro hacia los campos", "Rescate en las alturas", "La semilla del Roble Mayor", "Las dos hermandades",
               "Hasta la cima antigua", "El camino hacia el Roble Mayor", "Tres tareas para despertarlo", "La decisión del bosque", "Después del bosque"],
    "piratas": ["La bitácora de Gaspar", "Un mensaje en una botella", "El faro apagado", "El mapa del almirante", "El acertijo del templo hundido",
                "La perla de la marea", "Tras la estela de la Estrella Fugaz", "El rescate del capitán", "La brújula del tesoro", "Entre mar, río y pantano",
                "La isla de la calavera", "Rumbo al tesoro", "Tres llaves para el cofre", "Quién gobierna los puertos", "Después de la tormenta"],
}


def pal(t):
    return len(t.split())


def escribir(carpeta, prefijo, titulo_lore, secciones):
    """secciones: [(titulo, [lineas])]. Cada seccion puede partirse en varios bloques."""
    carpeta.mkdir(parents=True, exist_ok=True)
    for v in carpeta.glob(f"{prefijo}_*.md"):
        v.unlink()
    paginas = []
    for tit, lineas in secciones:
        pag, w = [], 15
        for ln in lineas:
            wl = pal(ln)
            if pag and w + wl > LIMITE:
                paginas.append((tit, pag))
                pag, w = [], 15
            pag.append(ln)
            w += wl
        if pag:
            paginas.append((tit, pag))
    # agrupar secciones chicas en el mismo bloque cuando entran
    bloques, actual, w = [], [], 0
    for tit, pag in paginas:
        wp = sum(pal(x) for x in pag) + 12
        if actual and w + wp > LIMITE:
            bloques.append(actual)
            actual, w = [], 0
        actual.append((tit, pag))
        w += wp
    if actual:
        bloques.append(actual)
    total = len(bloques)
    out = []
    for i, b in enumerate(bloques, 1):
        cuerpo = [f"# {prefijo} · {titulo_lore} (bloque {i}/{total})", ""]
        for tit, pag in b:
            cuerpo += [f"## {tit}"] + pag + [""]
        texto = "\n".join(cuerpo).rstrip() + "\n"
        nombre = f"{prefijo}_{i:02d}.md"
        (carpeta / nombre).write_text(texto, encoding="utf-8")
        out.append((nombre, pal(texto)))
    return out


def tabla(cab, filas):
    return ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)] + ["| " + " | ".join(str(c) for c in f) + " |" for f in filas]


def generar(lore, c, mundo, extra):
    L = lore
    id_ = L["id"]
    S = []
    # ---------------- mundo
    S.append(("MUNDO, TONO Y PROTAGONISTA", [
        f"**Nombre del mundo:** {L['nombre']}. **Moneda:** {L['moneda']}. **Tono:** {L['tono']}.",
        extra["historia"],
        f"**Protagonista:** {L['protagonista']['nombre']} (una sola palabra de nombre), `edad: niño`. {extra['protagonista']}",
        f"**Compañero inicial:** {mundo['COMPANEROS'][mundo['COMPANERO_INICIAL']]['nombre']} (niño, desde el segundo uno).",
        f"**Arranque:** {extra['arranque']}",
        "**Estilo de nombres:** " + extra["nombres"],
        "Este lore **usa todas las mecánicas** (01-99) y les da órdenes: lo que no figura aquí **no existe**; lo que figura se rige por el motor. No hay muerte (50): se arrastra a la cama o lugar de descanso más cercano.",
    ]))
    r = L["reparto"]
    S.append(("REPARTO: EDAD, APARIENCIA Y GRUPOS (órdenes a las mecánicas, bloque 50)", [
        f"- `edades_permitidas: [niño, adulto]`. **Adultos:** apariencia **{r['adultos']}** (todos los adultos son hembras, incluidas criaturas y enemigos)." if id_ == "bosque" else
        f"- `edades_permitidas: [niño, adulto]`. **Adultos:** apariencia **{r['adultos']}** (solo mujeres adultas).",
        f"- **Niños:** apariencia **{r['ninos']}**" + (" (todos varones)." if id_ == "bosque" else " (niños y niñas)."),
        "- **Excepciones:** " + ("los **alfas** son la única criatura de apariencia masculina (adultos)." if id_ == "bosque" else "ninguna."),
        "- **Grupos separados:** las mujeres adultas y los niños **no conviven ni forman grupos juntos**; cada facción es solo de niños o solo de mujeres adultas.",
        "- **Sin muerte:** los combates contra niños o bandas rivales son de derribo; nadie muere.",
        "- **Seguridad (50):** ningún niño participa en contenido sexual, romántico ni de desnudez en ningún modo. Relaciones con niños: solo amistad, confianza y respeto.",
        "- Los nombres de niños y compañeros son **una sola palabra**; los adultos usan `NPC-nnn` + palabras clave; los respawneables, `[facción o grupo]-nnn`.",
    ]))
    # ---------------- territorios y biomas
    filas = [(t["id"], t["nombre"], t["pos"], t["formacion"], t["clima"], t["relieve"], t["agua"], t["mod"], f"{t['nivel'][0]}-{t['nivel'][1]}") for t in L["territorios"]]
    S.append(("TERRITORIOS (7) Y SU POSICIÓN", [extra["mapa_texto"]] + tabla(["ID", "Territorio", "Posición", "Formación vegetal", "Clima", "Relieve", "Agua", "Modificador", "Niveles"], filas)))
    S.append(("CUADRO DE VARIANTES DE " + ("BOSQUE" if id_ == "bosque" else "SELVA") + " DE ESTE LORE (formación × clima × relieve, bloque 51)", extra["variantes"]))
    # ---------------- criaturas
    crea = [f"**Temas activos y fases presentes:**"]
    for tema, fases in L["temas"].items():
        crea.append(f"- {tema}: fases **{', '.join(str(f) for f in fases)}** presentes; fases {', '.join(str(f) for f in range(1, 15) if f not in fases)} **ausentes**.")
    crea += ["", "**Temas ausentes (no existen en este lore):** " + extra["temas_ausentes"], "",
             "**Especies activas por territorio (pool de enemigos y fauna, IDs de los bloques 19-23, 52):**"]
    for nombre, ids in L["pools"].items():
        crea.append(f"- pool «{nombre}»: {', '.join(ids)}.")
    crea += ["", extra["criaturas_reglas"]]
    S.append(("CRIATURAS: QUÉ TIPOS, QUÉ ESPECIES Y QUÉ FASES ESTÁN", crea))
    if extra.get("alfas"):
        S.append(("LOS ALFAS (criatura nueva del lore, tema T14)", extra["alfas"]))
    # ---------------- facciones
    S.append(("FACCIONES", tabla(["Facción", "Tipo", "Carácter", "Territorio"], L["facciones"]) +
              ["", "Las facciones infantiles y las de mujeres adultas son **separadas**; los niños no dependen de adultos en sus facciones."]))
    # ---------------- jefes
    S.append(("JEFES DE TERRITORIO", tabla(["Jefe", "Lugar", "Especie base", "Nivel", "PV", "Invocación"],
                                           [(j["nombre"], mundo["LOCS"][j["loc"]]["nombre"], j["especie"], j["nivel"], j["pv"], f"hasta {j['sub_max']} vivos, 3 ciclos") for j in mundo["JEFES"].values()])))
    # ---------------- ubicaciones
    for t in L["territorios"]:
        lineas = [f"**{t['nombre']}** · {t['formacion']} · {t['clima']} · {t['relieve']} · {t['agua']} · niveles {t['nivel'][0]}-{t['nivel'][1]}."]
        for u in t["ubicaciones"]:
            info = c.ubic[u["id"]]
            ns = info["nodos"]
            cuadras = [n for n in ns if mundo["LOCS"][n]["tipo"] == "cuadra"]
            edifs = [n for n in ns if mundo["LOCS"][n]["tipo"] == "edificio"]
            if u["kind"] == "s":
                lineas.append(f"- **{u['nombre']}** ({CL[u['clase']]}, {'interior' if u['espacio'] == 'int' else 'exterior'}, nivel {mundo['LOCS'][ns[0]]['nivel']}{', con cama' if mundo['LOCS'][ns[0]]['cama'] else ''}): 1 cuadra.")
            else:
                if u["kind"] == "c":
                    bar = "; ".join(f"{b} ({n} cuadras)" for b, n in u["barrios"])
                    lineas.append(f"- **{u['nombre']}** ({CL[u['clase']]}, ciudad grande, {len(cuadras)} cuadras y {len(edifs)} edificios). Barrios: {bar}.")
                else:
                    lineas.append(f"- **{u['nombre']}** ({CL[u['clase']]}, pueblo, {len(cuadras)} cuadras y {len(edifs)} edificios).")
                for q in cuadras:
                    es = [mundo["LOCS"][z]["nombre"].split(" de ")[0] for z in mundo["LOCS"][q]["conn"] if mundo["LOCS"][z]["tipo"] == "edificio"]
                    lineas.append(f"  - {mundo['LOCS'][q]['nombre']}: {', '.join(es)}.")
        S.append((f"UBICACIONES: {t['nombre'].upper()}", lineas))
    # ---------------- NPC
    por_ub = {}
    for nid, n in mundo["NPCS"].items():
        por_ub.setdefault(n["loc"], []).append(nid)
    nombre_ub = {}
    for uid, info in c.ubic.items():
        for n in info["nodos"]:
            nombre_ub[n] = info["nombre"]
    cuenta = {}
    for nid, n in mundo["NPCS"].items():
        cuenta.setdefault(nombre_ub.get(n["loc"], "?"), []).append(nid)
    lineas = [f"**NPC adultos incluidos:** {len(c.incl['adultos'])} arquetipos (apariencia {r['adultos']}). **NPC niños incluidos:** {len(c.incl['ninos'])} (con un solo nombre). "
              f"**Respawneables incluidos:** {len(c.incl['resp'])} plantillas (llevan nombre de facción o grupo + número). **Compañeros:** {len(mundo['COMPANEROS'])}. "
              "El lore **puede agregar** más NPC, respawneables y compañeros con el mismo formato.", ""]
    for ub, ids in cuenta.items():
        ad = [i for i in ids if i.startswith(("NPC", "ALF"))]
        ni = [f"{mundo['NPCS'][i]['nombre']} ({i})" for i in ids if i.startswith("NIN")]
        lineas.append(f"- **{ub}:** adultos {', '.join(ad) or '—'}; niños {', '.join(ni) or '—'}.")
    S.append(("DÓNDE VIVE CADA NPC (por ubicación)", lineas))
    # respawneables con facciones
    facs_inf = [f[0] for f in L["facciones"] if "infantil" in f[1]]
    facs_adu = [f[0] for f in L["facciones"] if "mujeres" in f[1] or "alfa" in f[1].lower()]
    res_l = ["Cada respawneable lleva el nombre de la facción o grupo del que viene + número de serie. Ejemplos de asignación:"]
    for i, rid in enumerate(c.incl["resp"][:40]):
        rol = next(x for x in c.a["resp"] if x["id"] == rid)["rol"]
        grupo = (facs_inf if any(k in rol.lower() for k in ("aprendiz", "recluta", "explorador", "voluntario")) else facs_adu)[i % max(1, len(facs_inf if any(k in rol.lower() for k in ("aprendiz", "recluta", "explorador", "voluntario")) else facs_adu))]
        res_l.append(f"- {rid} «{rol}» → {rol.split('[')[0].strip()} [{grupo}]-{i + 1:03d}")
    res_l.append("El resto de las plantillas incluidas se instancian igual con la facción o ubicación que corresponda.")
    S.append(("RESPAWNEABLES (facción o grupo + número)", res_l))
    # compañeros
    comp = tabla(["ID", "Nombre (una sola palabra)", "Arquetipo", "Edad", "Dónde se encuentra"],
                 [(k, v["nombre"], v["rol"], v["edad"], nombre_ub.get(v["loc"], "?")) for k, v in mundo["COMPANEROS"].items()])
    S.append(("COMPAÑEROS (solo femeninos o niños; el lore puede agregar más)", ["Se pueden usar desde el segundo uno. Máximo 3 activos (41). Personalidades extendidas: bloque de compañeros (catálogo)."] + comp))
    # misiones
    mp = []
    nombres_mp = NOMBRES_MP[id_]
    for i, qid in enumerate(c.principales):
        q = mundo["QUESTS"][qid]
        tgt = mundo["NPCS"][q["giver"]]
        mp.append((qid, nombres_mp[i], q["tq"], q["nivel"], tgt["nombre"] if tgt["edad"] == "niño" else q["giver"], nombre_ub.get(tgt["loc"], "?"), f"{q['xp']} XP"))
    S.append(("MISIONES PRINCIPALES (15)", ["Cada una instancia una misión base de MISIONES BASE. Orden por territorios: " + " → ".join(L["orden_territorios"]) + "."] +
              tabla(["ID", "Nombre", "Tipo", "Nivel", "Dador", "Lugar", "Recompensa"], mp)))
    sec_base = [(qid, mundo["QUESTS"][qid]["nombre"], mundo["QUESTS"][qid]["tq"], mundo["QUESTS"][qid]["nivel"]) for qid in mundo["QUESTS"] if qid.startswith(("MS-", "MJ-"))]
    S.append(("MISIONES SECUNDARIAS BASE Y DE JEFE (todas incluidas)", ["Las 45 misiones secundarias base y una misión por jefe de territorio están **incluidas** en este lore."] +
              tabla(["ID", "Nombre", "Tipo", "Nivel"], sec_base)))
    por_npc = {}
    for qid, q in mundo["QUESTS"].items():
        if qid.startswith("Q"):
            por_npc.setdefault(q["giver"], []).append(q)
    lineas = [f"**Misiones propias de cada NPC (1 a 5 por NPC con misión):** {sum(len(v) for v in por_npc.values())} en total. Formato: NPC → «nombre» (tipo, nivel)."]
    for nid, qs in por_npc.items():
        n = mundo["NPCS"][nid]
        etq = n["nombre"] if n["edad"] == "niño" else nid
        lineas.append(f"- {etq} [{nid}]: " + " · ".join(f"«{q['nombre']}» ({q['tq']}, n{q['nivel']})" for q in qs))
    S.append(("MISIONES PROPIAS DE CADA NPC", lineas))
    S.append(("MISIONES DESCARTADAS POR EL LORE", [extra["descartadas"]]))
    # objetos
    S.append(("OBJETOS DEL LORE", extra["objetos"]))
    # config
    cfg = [
        "```", f"LORE = {L['nombre']}", f"MONEDA = {L['moneda']}", "NECESIDADES = on    CONTAMINACION = off    MODULO_EXTERNO = off    NIVEL_MAX = 30", "",
        "TERRITORIOS = [" + ", ".join(t["nombre"] for t in L["territorios"]) + "]", f"UBICACIONES = {len(c.ubic)} (con {sum(1 for d in mundo['LOCS'].values() if d['tipo'] == 'cuadra')} cuadras y {sum(1 for d in mundo['LOCS'].values() if d['tipo'] == 'edificio')} edificios)", "",
        "REPARTO = {", f"  edades_permitidas: [niño, adulto], apariencia_adultos: {r['adultos']}, apariencia_niños: {r['ninos']},",
        "  excepciones: " + ("[{T14 alfa: masculina}]" if id_ == "bosque" else "[]") + ", grupos_separados: [[adultos, niños]], sin_muerte: true }", "",
        "CRIATURAS = { temas_activos: [" + ", ".join(L["temas"]) + "],", "  fases_activas: {" + ", ".join(f"{k}: {v}" for k, v in L["temas"].items()) + "},",
        "  modificadores_apagados: [Infernal, Demoníaca, Celestial, Zombi, Robótica, Alienígena], fases_ausentes: todas las demás }", "",
        f"NPC = {{ incluidos: {len(c.incl['adultos'])} adultos + {len(c.incl['ninos'])} niños, agregados: [] }}",
        f"COMPANEROS = {len(mundo['COMPANEROS'])} (nombre de una sola palabra)", f"RESPAWNEABLES = {len(c.incl['resp'])} plantillas con facción o grupo",
        f"MISIONES = {{ principales: 15, secundarias_base: 45, de_jefe: {len(mundo['JEFES'])}, propias_de_npc: {sum(len(v) for v in por_npc.values())} }}",
        f"JEFES = [" + ", ".join(j["nombre"] for j in mundo["JEFES"].values()) + "]",
        "ARRANQUE = { protagonista: " + f"{L['protagonista']['nombre']} (niño), ubicación_inicial: {c.ubic[L['protagonista']['inicio']]['nombre']}, misión_inicial: MP-01" + " }", "```",
    ]
    S.append(("CONFIG_LORE FINAL", cfg))
    return S


# ---------------------------------------------------------------- textos propios de cada lore
VAR_BOSQUE = tabla(["Variante", "Formación", "Clima", "Relieve", "Dónde aparece en este mapa"], [
    ("Bosque cerrado templado", "bosque cerrado", "templado húmedo", "colinas", "El Bosque Hondo (base)"),
    ("Bosque de niebla", "bosque de niebla", "templado húmedo", "colinas", "Bosque de Niebla y hondonadas"),
    ("Bosque pantanoso", "bosque cerrado", "templado húmedo", "llanura", "borde sur y Pantano del Extremo Sur"),
    ("Humedal con islas de bosque", "humedal", "templado", "islas", "Pantano del Extremo Sur"),
    ("Bosque abierto urbano", "bosque abierto", "templado", "llanura", "Ciudad Esperanza y su parque"),
    ("Bosque de sabana", "sabana arbolada", "templado seco", "llanura", "Los Campos"),
    ("Pradera de campos", "pradera", "templado", "llanura", "Los Campos (cultivos)"),
    ("Selva templada", "selva", "templado húmedo", "colinas", "Las Selvas del Comercio"),
    ("Selva de ribera", "bosque de ribera", "templado", "valle", "ríos y arroyos de la selva"),
    ("Bosque de cañones", "bosque abierto", "semiárido", "cañones", "El Territorio Alfa"),
    ("Bosque desértico", "bosque abierto", "árido", "meseta", "mesetas del Territorio Alfa"),
    ("Bosque nevado", "bosque cerrado", "boreal", "montaña", "Las Montañas del Norte"),
    ("Bosque ártico (cumbres)", "bosque cerrado", "ártico", "glaciar", "Cima Antigua"),
    ("Roquedal nevado", "roquedal", "alta montaña", "glaciar", "cumbres"),
])
VAR_SELVA = tabla(["Variante", "Formación", "Clima", "Relieve", "Dónde aparece en este mapa"], [
    ("Selva de islas", "selva", "tropical húmedo", "archipiélago", "El Océano de las Mil Velas"),
    ("Selva de galería", "bosque de ribera", "tropical húmedo", "valle", "El Río Media Luna"),
    ("Humedal de islotes", "humedal", "templado húmedo", "islas", "El Pantano de los Islotes"),
    ("Manglar", "manglar", "tropical", "costa", "entradas del mar y del pantano"),
    ("Selva irregular", "selva alta y baja mezcladas", "tropical húmedo", "colinas", "La Selva del Sur"),
    ("Selva urbana", "selva", "tropical", "llanura", "La Ciudad de los Siete Faroles"),
    ("Selva de sabana", "selva baja", "tropical seco", "llanura", "La Selva del Este"),
    ("Selva de cañones", "selva baja", "tropical", "cañones", "La Selva del Este"),
    ("Selva de montaña", "selva alta", "tropical húmedo", "montaña", "La Selva del Norte"),
    ("Selva de niebla", "selva", "tropical húmedo", "mesetas", "Meseta de Niebla"),
])

EXTRA_A = dict(
    historia="Un gran bosque atravesado por mil senderos, con una ciudad al oeste, campos al noroeste, montañas al norte, un pantano al sur, selvas de comercio al este de la ciudad y un territorio de gigantes amistosos al este de los campos. Los **Exploradores del Roble** son un grupo de niños que viste como los bandoleros de los cuentos de arqueros del bosque: capas verdes, arcos de práctica y banderines. Parece un grupo de scouts, pero es una civilización propia, con campamentos, reglas, mapas y oficios, cuidada por mujeres adultas. Hay muchas facciones infantiles y muchas de mujeres.",
    protagonista="Un chico de ciudad, curioso y algo asustadizo, que se pierde en el bosque. Es de **nivel 1**.",
    arranque="Lucas camina por la Senda de los Helechos cuando es atacado por un **insecto gigante hembra** (mantis) y no puede defenderse. Lo protege un grupo de exploradores y queda al cuidado del campamento del Claro del Roble Partido; de ahí parte la campaña. El niño que lo rescata es su compañero inicial.",
    nombres="nombres de pila comunes de niños (Tobías, Lucho, Bruno…), **una sola palabra**; lugares con nombres de árboles, aves y accidentes del terreno (Roble Partido, Mirador del Halcón, Arroyo de las Piedras Lisas).",
    mapa_texto="Mapa de oeste a este y de sur a norte: **Pantano** en toda la punta sur; **Bosque Hondo** sobre el pantano; **Ciudad Esperanza** al oeste en el centro; **Campos** al noroeste; **Selvas del Comercio** al este de la ciudad; **Territorio Alfa** al este de los campos; **Montañas** en toda la punta norte.",
    variantes=VAR_BOSQUE,
    temas_ausentes="cuernos y cuerpo robusto (T2), halo (T3), duende (T4), orco (T5), no muerta (T6), elemental (T7), vegetal (T8), mitológica (T9), artificial (T10), alienígena (T11), mutante (T12), amorfa de gran tamaño (T13; solo slimes pequeños de la fauna).",
    criaturas_reglas="**Todas las criaturas adultas son hembras** (apariencia femenina), incluidos los enemigos, los insectos, los lobos y los slimes. **La única excepción son los alfas.** Los animales aparecen solo en fases 1 a 3; no existen las fases 4 a 14 de animales (los humanos son niños y mujeres, fase 13). Los enemigos son fauna hostil (insectos, lobas, jabalíes, parásitos genéricos y slimes) y **bandas rivales de niños** (derribo no letal). Las variantes universales de origen sobrenatural, zombi o robótico están apagadas.",
    alfas=[
        "Los **alfas** son un tema nuevo (T14, bloque 52): criaturas independientes de los animales, emparentadas con los lobos, con su propia cadena de 14 fases. **En este lore solo existen las fases 1, 2 y 3**, y son **gigantes amistosos** al este de los campos (Territorio Alfa). Son **adultos y varones**: la única criatura de apariencia masculina del mapa.",
        "- **Fase 1 (los más salvajes, de las alturas):** altísimos, de musculatura extrema, con mucho vello largo que rodea los músculos principales (en rulos o liso) y casi los cubre; mandíbula con dientes inferiores que sobresalen; cuerpo de orco de fantasía, aún más peludo y alto que un gorila. Viven en lugares altos y boscosos. **En este lore visten** taparrabos y prendas de piel de animal al estilo de la antigua Grecia.",
        "- **Fase 2 (los más numerosos):** hipermusculados como un orco; vello largo y abundante *para un humano* pero escaso *para un lobo*: rodea los músculos principales sin cubrir abdominales ni pectorales, que se ven claramente; dentadura casi humana salvo los colmillos inferiores; sin garras ni colmillos superiores; cuerpo casi humanoide. **En este lore visten** ropa de estilo griego más moderna, de origen animal, mucho más trabajada y con tintes.",
        "- **Fase 3 (los más humanos):** altos, hipermusculados pero no como un orco, con buena cantidad de grasa corporal; dientes inferiores grandes pero no sobresalientes. **Visten** ropa humana común.",
        "**Conducta:** `[a completar por el autor]` (cordial, elegante y respetuosa en este lore). Territorio: Aldea de las Casas Grandes, Cañón de los Ecos, Meseta del Viento, Bosque Alto, Tótem de las Cumbres. Se rigen por 52 (territoriales, amistosos con quien los respeta). **No hay contenido sexual en ningún caso;** los detalles físicos de esta lista son solo de apariencia general y vestimenta.",
    ],
    descartadas="Se descartan: toda misión con esclavistas, cultos, saqueadores adultos, contrabando o mercenarios; todo NPC de lugares hostiles de adultos y de puerto; alcohol, apuestas, casino y préstamos; los temas T2-T13; las fases 4-14 de animales; la fase 14 de humanos. Las misiones que dependían de esos NPC no aparecen.",
    objetos=["- **Armas (no letales para personas):** Palo de práctica, Bastón de roble, Bastón reforzado, Lanza de exploradores (punta roma), Cayado del Roble Mayor; arcos y hondas de práctica, redes y trampas de red (bloques de armas, solo no letales).",
             "- **Comida y bebida:** viandas, frutas del bosque, miel, pan de campo, guisos, té de hierbas, agua de arroyo hervida. **Sin alcohol ni químicos.**",
             "- **Medicina:** vendas, ungüentos de hierbas, tinturas, compresas, férulas. **Ropa:** capas verdes, chalecos de lona, botas de exploración; armaduras ligeras de explorador (E1-E4), Armadura del guardián (E5).",
             "- **Objetos generales:** mapas, brújulas, catalejos, cuerdas, cuadernos, linternas, banderines, silbatos, instrumentos. **Moneda:** bellotas."],
)
EXTRA_B = dict(
    historia="Un mundo de selvas, ríos, pantanos y un mar abierto, con una ciudad de muchos barrios en el centro. Hay un **océano** (esquina inferior izquierda), un **río en forma de media luna muy delgada** que cruza el mapa desde la punta superior derecha hasta la izquierda, pasando por la ciudad, y un **pantano de islotes** (esquina inferior derecha). Ninguno de los tres se conecta directamente con otro, pero los tres tienen muelles. Cada uno tiene sus barcos: grandes navíos de madera en el mar (piratas), botes y barcazas en el río, y botes de fondo plano en el pantano. Todos los marineros, piratas y habitantes de la costa son **niños**; las **mujeres adultas** viven y trabajan en grupos separados.",
    protagonista="Un grumete curioso y aventurero que vive en la Casa del Farero y sueña con embarcar. Es de **nivel 1**.",
    arranque="Gaspar despierta en la Casa del Farero, en la ciudad. Un mensaje en una botella y el faro apagado dan comienzo a la campaña. Su compañero inicial es otro grumete del puerto.",
    nombres="nombres de pila comunes de niños y niñas (Gaspar, Bartolo, Marinela, Estela…), **una sola palabra**; barcos y lugares con nombres de mar, astros y oficios (La Estrella Fugaz, Faro del Cabo, Puerto de las Gaviotas).",
    mapa_texto="Mapa: **Océano** en la esquina inferior izquierda; **Pantano de los Islotes** en la inferior derecha; **Selva del Sur** entre el pantano, el mar y la ciudad; **Ciudad de los Siete Faroles** en el centro con muchos barrios; **Selva del Este** al este de la ciudad; **Selva del Norte** en la parte superior; el **Río Media Luna** atraviesa el mapa por el medio, de la punta superior derecha a la izquierda, pasando por la ciudad.",
    variantes=VAR_SELVA,
    temas_ausentes="**todos los temas de criaturas** (T2-T14). No hay criaturas amistosas ni sociales: solo **enemigos** (fauna hostil de agua, pantano y selva).",
    criaturas_reglas="No hay criaturas de ningún tipo salvo los **enemigos**: marinos blandos agrandados (pulpos, medusas, calamares), seres de río y pantano (slimes y parásitos genéricos), insectos mutantes y animales de selva, siempre en **fase 1**. No existen las fases 2 a 14 de animales. Los humanos son niños y niñas (piratas, gente del río y del pantano, ciudadanos de aspecto medieval, comerciantes, «piratas de tierra») y mujeres adultas en grupos aparte; los combates entre humanos son de derribo, sin muerte.",
    alfas=None,
    descartadas="Se descartan: todo lo subterráneo, de ciencia o radio, torres, órdenes armadas y refugios; esclavistas, cultos, saqueadores adultos y mercenarios; alcohol, apuestas, casino y préstamos; los temas de criaturas T2-T14 y las fases 2-14 de animales. Las misiones que dependían de esos NPC no aparecen.",
    objetos=["- **Armas (no letales para personas):** Remo de práctica, Sable de madera, Sable de abordaje (embotado), Arpón de pesca (punta roma), Sable del Capitán; hondas, redes y garfios de práctica.",
             "- **Comida y bebida:** pescado asado, galletas de barco, frutas de la selva, guisos, caldos, agua de lluvia, té. **Sin alcohol ni químicos.**",
             "- **Medicina:** vendas, ungüentos, tinturas, compresas, férulas. **Ropa:** ropa de pirata, chalecos salvavidas, capas impermeables; armaduras ligeras (E1-E4), Armadura del almirante (E5).",
             "- **Objetos generales:** mapas, brújulas, catalejos, cuerdas, redes, velas, bitácoras, botellas con mensajes, anclas pequeñas. **Moneda:** doblones. Barcos y botes: nodos de muelle y tramos de agua."],
)


def main():
    resumen = []
    for lore, extra, carpeta, pref, titulo in ((lore_bosque.LORE, EXTRA_A, RAIZ / "lores" / "BOSQUE", "LORE_BOSQUE", "EL BOSQUE DE LOS MIL SENDEROS"),
                                               (lore_piratas.LORE, EXTRA_B, RAIZ / "lores" / "PIRATAS", "LORE_PIRATAS", "EL MAR DE LAS MIL VELAS")):
        mundo, c = constructor.construir(lore)
        S = generar(lore, c, mundo, extra)
        out = escribir(carpeta, pref, titulo, S)
        resumen.append((pref, out))
    for pref, out in resumen:
        print(f"{pref}: {len(out)} bloques, {sum(p for _, p in out)} palabras")
        for n, p in out:
            print(f"   {n:24s} {p:5d}")


if __name__ == "__main__":
    main()
