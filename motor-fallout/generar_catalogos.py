#!/usr/bin/env python3
"""Escribe los bloques de catalogo (53 en adelante): fases por tema, NPC, ninos, companeros, misiones, ubicaciones,
sucesos y objetos. Cada bloque queda por debajo del limite de palabras.

Uso: python3 -I generar_catalogos.py [--limite 1850]
"""
import sys
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
sys.path.insert(0, str(CARPETA / "catalogos"))
import asignaciones  # noqa: E402
import datos_fases as df  # noqa: E402
import datos_misiones as dm  # noqa: E402
import datos_objetos as do  # noqa: E402
import datos_ubicaciones as du  # noqa: E402

LIMITE = 1850
if "--limite" in sys.argv:
    LIMITE = int(sys.argv[sys.argv.index("--limite") + 1])
SIGUIENTE = [53]
ESCRITOS = []  # (numero, nombre de archivo, titulo, palabras)

LUGAR = {"REF": "refugio o instalación", "ASE": "asentamiento", "MIL": "orden armada", "TOR": "torre o enclave", "HOS": "zona hostil", "CAM": "camino o ruina",
         "ESP": "lugar especial", "SUB": "comunidad subterránea", "IND": "granja o industria", "CIE": "ciencia o radio", "COM": "comercio", "PUE": "puerto o ribera"}


def palabras(t):
    return len(t.split())


def escribir_grupo(slug, titulo, intro, secciones, pie=""):
    """secciones: lista de (subtitulo, cabecera_tabla(list[str]) o None, filas(list[str]), nota). Parte en bloques."""
    bloques, actual, pal = [], [], 0

    def nuevo():
        return []

    def cabecera(n, k_total):
        return f"# {n:02d} · {titulo}" + (f" (parte {{k}}/{{t}})" if k_total else "")

    cuerpo_intro = intro.strip()
    paginas = []  # lista de listas de lineas
    pag, w = [], palabras(cuerpo_intro) + 20
    for sub, cab, filas, nota in secciones:
        enc = [f"\n## {sub}"] + (list(cab) if cab else [])
        if pag and w + palabras("\n".join(enc)) + 40 > LIMITE:
            paginas.append(pag)
            pag, w = [], 20
        pag += enc
        w += palabras("\n".join(enc))
        for f in filas:
            wf = palabras(f)
            if w + wf > LIMITE:
                paginas.append(pag)
                pag, w = [f"\n## {sub} (continuación)"] + (list(cab) if cab else []), 20 + palabras("\n".join(cab or []))
            pag.append(f)
            w += wf
        if nota:
            pag.append(nota)
            w += palabras(nota)
    if pag:
        paginas.append(pag)
    total = len(paginas)
    for k, p in enumerate(paginas, 1):
        n = SIGUIENTE[0]
        SIGUIENTE[0] += 1
        enc = f"# {n:02d} · {titulo}" + (f" (parte {k}/{total})" if total > 1 else "")
        cuerpo = [enc, "", cuerpo_intro if k == 1 else f"(Continuación de «{titulo}»; mismas reglas que la parte 1.)"] + p
        if k == total and pie:
            cuerpo += ["", pie.strip()]
        texto = "\n".join(cuerpo).rstrip() + "\n"
        nombre = f"{n:02d}_{slug}{'_P' + str(k) if total > 1 else ''}.md"
        (CARPETA / nombre).write_text(texto, encoding="utf-8")
        ESCRITOS.append((n, nombre, titulo, palabras(texto)))


def tier(lo, hi):
    return " · ".join(f"T{i + 1} {max(0, round(lo * m))}-{max(0, round(hi * m))}" for i, m in enumerate(do.TIER_MULT))


# ------------------------------------------------------------------ 1. fases por tema
def fases():
    secciones = []
    for clave, nombre, ej, p2, r6, equipo, (v2, v3), raras, incomp in df.TEMAS:
        filas = []
        for f in range(1, 15):
            desc = df.FRASES[f].format(ej=ej if f < 13 else "este tema", p2=p2, r6=r6)
            freq = "rara" if f in raras else "habitual"
            filas.append(f"| {f} | {desc} | {df.HABLA[f]} | {df.EQUIPO[f]} | {df.CONDUCTA[f]} | Común / {v2} / {v3} | {freq} |")
        sub = f"{clave} · Criaturas {nombre} (equipo típico: {equipo})"
        secciones.append((sub, ["| Fase | Cómo es | Habla · manos | Equipo máx. | Conducta | Variantes V1 / V2 / V3 | Frecuencia |", "|---|---|---|---|---|---|---|"], filas,
                          f"Compatible con las variantes universales (24) excepto: {', '.join(sorted(incomp)) or 'ninguna restricción'}. Las fases marcadas «rara» pueden quedar fuera del lore sin romper nada."))
    filas = []
    temas_cab = " | ".join(t[0] for t in df.TEMAS)
    for v in df.VARIANTES_UNIVERSALES:
        marcas = " | ".join("✗" if v in t[8] else "✓" for t in df.TEMAS)
        filas.append(f"| {v} | {marcas} |")
    secciones.append(("MATRIZ DE COMPATIBILIDAD: variantes universales × temas", [f"| Variante | {temas_cab} |", "|---|" + "---|" * len(df.TEMAS)], filas,
                      "✓ = compatible, ✗ = no aplica (a menos que el lore lo permita). Máx. 3 modificadores por entidad (24)."))
    intro = ("Cuadros de las **14 fases** (08, 25) para cada **tema** de criaturas (18). La palabra «criatura» no cambia: el tema es lo que la acompaña. "
             "Cada fila describe cómo es esa fase en ese tema, si habla, si tiene manos, qué equipo puede llevar (26), su conducta y sus variantes típicas V1/V2/V3 (27). "
             "El lore decide qué fases y temas existen; las fases «raras» se pueden descartar. Todo humano o humanoide es adulto y lleva `edad` (50). "
             "El ejemplo de especie de cada tema se reemplaza por las especies de 19-23, 35, 36 y 52.")
    escribir_grupo("FASES_POR_TEMA", "CUADROS DE LAS 14 FASES POR TEMA", intro, secciones)


# ------------------------------------------------------------------ 2. NPC
def npcs(a):
    filas = []
    for x in a["adultos"]:
        ms = " · ".join(f"«{m['nombre']}» ({m['tipo']})" for m in x["misiones"])
        filas.append(f"| {x['id']} | {x['rol']} | {', '.join(x['claves'])} | {LUGAR[x['lugar']]} | {len(x['misiones'])}: {ms} |")
    intro = ("**NPC con nombre** (por arquetipo, sin nombres originales): `NPC-nnn` + palabras clave. El **lore** les pone nombre, apariencia (50) y lugar; "
             "el arquetipo es neutro en edad adulta y en apariencia. **Cada NPC tiene de 1 a 5 misiones** (asignadas al azar con semilla fija, tal cual); el nombre de la misión sale de su "
             "personalidad y del tipo de misión (34 tipos, ver bloque de misiones base). Un NPC que cae bien o interesa muestra **relación** (09); se le puede pedir que **te siga o te acompañe** "
             "(temporal). **El lore puede agregar más NPC** y descartar los que no encajan: lo que el lore no menciona, no existe. Todo NPC adulto lleva `edad: adulto`.")
    escribir_grupo("NPC_CON_NOMBRE", "CLASIFICACIÓN DE NPC CON NOMBRE", intro,
                   [("NPC adultos (arquetipos)", ["| ID | Arquetipo | Personalidad | Lugar típico | Misiones (n: nombre y tipo) |", "|---|---|---|---|---|"], filas,
                     "Tipos de misión (REC, AMN, RSC…): ver bloque de misiones base. Los NPC muertos no existen: quedan Incapacitados (50).")])

    filas = [f"| {x['id']} | {x['rol']} | {', '.join(x['claves'])} | {LUGAR[x['lugar']]} |" for x in a["resp"]]
    intro = ("**NPC respawneables y genéricos**: se identifican por **el nombre de la facción, grupo o lugar del que vienen + un número de serie** (ej.: «Guardia [facción]-012», «Pueblerino de [ubicación]-007»). "
             "No tienen nombre propio ni misión propia salvo que el lore se las dé; pueden dar charla, rumores y comercio menor. Reaparecen según 07 (regeneración >48 h en zonas hostiles; "
             "en zonas seguras se reponen cada 24 h). **El lore puede agregar más grupos respawneables**, y descartar los que no encajen. Edad y apariencia: las fija el lore (50).")
    escribir_grupo("NPC_RESPAWNEABLES", "NPC RESPAWNEABLES Y GENÉRICOS", intro,
                   [("Respawneables (plantillas)", ["| ID | Plantilla (con facción/grupo) | Personalidad | Lugar típico |", "|---|---|---|---|"], filas, "")])

    filas = []
    for x in a["ninos"]:
        ms = " · ".join(f"«{m['nombre']}» ({m['tipo']})" for m in x["misiones"])
        filas.append(f"| {x['id']} | {x['rol']} | {', '.join(x['claves'])} | {LUGAR[x['lugar']]} | {len(x['misiones'])}: {ms} |")
    intro = ("**NPC niños**: clasificación **aparte**. Todos llevan `edad: niño` (menor de 18), tienen **un solo nombre** (el lore lo pone: sin apellido ni apodo) y pueden ser de apariencia femenina o masculina "
             "según el lore. Reglas de seguridad (50, tal cual): **nunca participan en contenido sexual, romántico ni de desnudez, en ningún modo ni con ningún interruptor**; las relaciones con ellos son **solo amistad, confianza y respeto**; "
             "**no mueren** (quedan Incapacitados); los combates contra niños son de derribo. Cada niño con misión tiene de 1 a 5. Cubren los tipos de niños de los cuatro Fallout clásicos (instalaciones, calles, puertos, comunidades aisladas) y los que el lore necesite. "
             "**El lore puede agregar más.**")
    escribir_grupo("NPC_NINOS", "CLASIFICACIÓN DE NPC NIÑOS", intro,
                   [("NPC niños (arquetipos)", ["| ID | Arquetipo | Personalidad | Lugar típico | Misiones (n: nombre y tipo) |", "|---|---|---|---|---|"], filas, "")])

    filas = [f"| {x['id']} | {x['rol']} | {x['edad']} | {x['personalidad']} |" for x in a["comps"]]
    intro = ("**Compañeros**: solo personajes **femeninos** (apariencia femenina) o **niños** (de cualquier apariencia), más animales y robots sin género definido. Cada uno tiene **un solo nombre** que el lore elige (el que mejor lo represente, "
             "sin apellido ni apodo). Se pueden usar **desde el segundo uno** (se recluta al conocerlos si el lore lo permite). Reglas (41): máximo 3 activos; PV 30 + 6×nivel; no mueren (Incapacitados); lealtad 0-100 (sube con misiones personales y buen trato). "
             "Los compañeros niños: relación solo de amistad (50). **El lore puede agregar más compañeros** y descartar los incompatibles.")
    escribir_grupo("COMPANEROS_CATALOGO", "CATÁLOGO DE COMPAÑEROS", intro,
                   [("Compañeros (personalidad extendida)", ["| ID | Arquetipo | Edad | Personalidad |", "|---|---|---|---|"], filas, "")])


# ------------------------------------------------------------------ 3. misiones base
def misiones():
    tipos = [f"| {k} | {v[0]} | {v[2]} |" for k, v in dm.TIPOS.items()]
    prin = [f"| {i} | {n} | {t} | {idea} | {r} |" for i, n, t, idea, r in dm.PRINCIPALES]
    sec = [f"| {i} | {n} | {t} | {idea} | {r} |" for i, n, t, idea, r in dm.SECUNDARIAS]
    intro = ("**Misiones base**: 15 principales y 45 secundarias (60 en total, como el juego base de referencia, que trae 59), expresadas como **plantillas** con tipo y ramas. "
             "El lore las **instancia** (pone dador, lugares y nombres), puede **descartar** las que no encajan y **agregar** otras. Además, **cada NPC con misión recibe de 1 a 5 misiones propias** (ver los catálogos de NPC). "
             "Las misiones se generan **automáticamente** por personalidad, situación, lugar y enemigos cercanos (45). Si el conflicto es entre humanos hay **elección de bando**; si es contra criaturas, no. "
             "Los pasos de cada tipo son botones (03). Ningún niño muere en misiones; los derrotados quedan Incapacitados (50).")
    escribir_grupo("MISIONES_BASE", "MISIONES BASE Y TIPOS DE MISIÓN", intro, [
        ("Misiones principales (15)", ["| ID | Nombre genérico | Tipo | Idea | Ramas |", "|---|---|---|---|---|"], prin, "El lore instancia M-01 como la misión inicial y M-15 como el epílogo."),
        ("Misiones secundarias (45)", ["| ID | Nombre genérico | Tipo | Idea | Ramas |", "|---|---|---|---|---|"], sec, ""),
        ("Tipos de misión (34)", ["| Código | Tipo | Pasos (botones) |", "|---|---|---|"], tipos,
         "Recompensa: XP según nivel (60-250 secundarias, 150-2500 principales, 27) y un objeto del lore. Las misiones de elegir bando generan un grupo rival persistente."),
    ])


# ------------------------------------------------------------------ 4. ubicaciones y sucesos
def ubicaciones():
    filas = []
    for i, l in enumerate(du.UBICACIONES, 1):
        nom, clase, esp, claves, cont, gente = [c.strip() for c in l.split(";")]
        cl = {"S": "Segura", "N": "Normal", "H": "Hostil"}[clase]
        filas.append(f"| UB-{i:03d} | {nom} | {cl} | {esp} | {claves} | {cont} | {gente} |")
    intro = ("**Catálogo de ubicaciones** (arquetipos de mapa de un mundo abierto clásico, neutralizados). El lore elige cuáles existen, les pone **nombre propio permanente**, las reparte en sus **territorios** (51) y las divide en **cuadras** (47). "
             "Cada una trae clase (segura/normal/hostil), espacio, palabras clave, contenedores típicos y habitantes típicos. Lo que no esté en el lore, no existe. Una ciudad o un pueblo son ubicaciones con muchas cuadras. "
             "Los mapas del lore deben incluir al menos una ubicación de descanso (cama) segura por territorio.")
    escribir_grupo("UBICACIONES_CATALOGO", "CATÁLOGO DE UBICACIONES", intro,
                   [("Arquetipos de ubicación", ["| ID | Arquetipo | Clase | Espacio | Palabras clave | Contenedores típicos | Gente o criaturas típicas |", "|---|---|---|---|---|---|---|"], filas, "")])
    filas = []
    for i, l in enumerate(du.SUCESOS, 1):
        cat, suc, det = [c.strip() for c in l.split(";")]
        filas.append(f"| SC-{i:03d} | {cat} | {suc} | {det} |")
    intro = ("**Sucesos y cosas que hacer en un lugar** (botones que la IA ofrece según lo que realmente existe en la cuadra o el edificio, 03, 47, 48). "
             "Cubren descanso, exploración, registro, trato social, combate, técnica, comercio, criaturas, mundo, viaje, hogar y moral. "
             "Ningún suceso involucra a menores en contenido sexual, romántico ni de desnudez (50).")
    escribir_grupo("SUCESOS_CATALOGO", "CATÁLOGO DE SUCESOS Y ACCIONES POR LUGAR", intro,
                   [("Sucesos", ["| ID | Categoría | Suceso | Detalle |", "|---|---|---|---|"], filas, "")])


# ------------------------------------------------------------------ 5. objetos
def objetos():
    nota_nombres = "Los **nombres** los pone el lore (genérico); **daño, PA, rasgos y requisitos** son fijos (tal cual). Tiers: T1 Improvisada ×0.7 · T2 Común ×1.0 · T3 Mejorada ×1.3 · T4 Militar ×1.7 · T5 Especial ×2.2 (29)."
    filas = [f"| WM-{i:03d} | {n} | {lo}-{hi} | {tier(lo, hi)} | {pa} | {r} | {q} |" for i, (n, lo, hi, pa, r, q) in enumerate(do.MELE, 1)]
    escribir_grupo("ARMAS_CUERPO_A_CUERPO", "CATÁLOGO DE ARMAS: DESARMADO Y CUERPO A CUERPO",
                   nota_nombres + " Las armas «no letales» sirven para menores y para campañas sin muerte: derriban, nunca matan (50).",
                   [("Cuerpo a cuerpo", ["| ID | Arma | Daño T2 | Daño por tier | PA | Rasgo | Requisito |", "|---|---|---|---|---|---|---|"], filas, "")])
    filas = [f"| WD-{i:03d} | {n} | {lo}-{hi} | {tier(lo, hi)} | {al} | {pa} | {m} | {r} | {q} |" for i, (n, lo, hi, al, pa, m, r, q) in enumerate(do.DISTANCIA, 1)]
    escribir_grupo("ARMAS_DISTANCIA", "CATÁLOGO DE ARMAS: DISTANCIA Y PROYECTILES",
                   nota_nombres + " Fuera de distancia CORTA fallan casi siempre (37). Munición: familias A-01 a A-13 (30).",
                   [("Armas de fuego, arcos y proyectiles", ["| ID | Arma | Daño T2 | Daño por tier | Alcance | PA | Munición | Rasgo | Requisito |", "|---|---|---|---|---|---|---|---|---|"], filas, "")])
    filas = [f"| WX-{i:03d} | {n} | {lo}-{hi} | {tier(lo, hi)} | {al} | {pa} | {m} | {r} | {q} |" for i, (n, lo, hi, al, pa, m, r, q) in enumerate(do.ENERGIA, 1)]
    unicas = [f"| WU-{i:03d} | arma única basada en «{b}» | {p} |" for i, (b, p) in enumerate(do.UNICAS, 1)]
    escribir_grupo("ARMAS_ENERGIA_PESADAS_EXPLOSIVOS", "CATÁLOGO DE ARMAS: ENERGÍA, PESADAS, EXPLOSIVOS Y ÚNICAS",
                   nota_nombres + " Los explosivos y trampas son consumibles de combate. Las **únicas** son arquetipos que el lore convierte en objetos con nombre y origen (uno por jefe o misión clave); su propiedad es fija.",
                   [("Energía, pesadas, explosivos y trampas", ["| ID | Arma | Daño T2 | Daño por tier | Alcance | PA | Munición | Rasgo | Requisito |", "|---|---|---|---|---|---|---|---|---|"], filas, ""),
                    ("Armas únicas (arquetipos)", ["| ID | Arquetipo | Propiedad especial |", "|---|---|---|"], unicas, "")])
    filas = [f"| MV-{i:03d} | {n} | {e} | {fam} | ×{v} | {r} |" for i, (n, e, fam, v, r) in enumerate(do.MUNICION_VARIANTES, 1)]
    pieza = [f"| AR-{i:03d} | {n} | {' / '.join(str(x) for x in rd)} | {pe} |" for i, (n, rd, pe) in enumerate(do.ARMADURAS_PIEZAS, 1)]
    esp = [f"| AE-{i:03d} | {n} | {e} | {t} |" for i, (n, e, t) in enumerate(do.ARMADURAS_ESPECIALES, 1)]
    escribir_grupo("MUNICION_ARMADURAS_CATALOGO", "CATÁLOGO DE MUNICIÓN, ARMADURAS Y ROPA",
                   "Variantes de munición por familia (30) y piezas de protección por tier de equipo E0-E5 (32). Efectos y valores fijos; nombres de marcas, calibres y materiales: los pone el lore. "
                   "Materiales típicos por tier: E1 tela o lona · E2 cuero o lona reforzada · E3 malla · E4 placas · E5 aleación, compuesto o asistida. RD = reducción de daño.",
                   [("Variantes de munición", ["| ID | Variante | Efecto | Familias | Valor | Rareza |", "|---|---|---|---|---|---|"], filas, ""),
                    ("Piezas de protección: RD de E0 a E5", ["| ID | Pieza | RD E0 / E1 / E2 / E3 / E4 / E5 | Peso |", "|---|---|---|---|"], pieza, ""),
                    ("Ropa y protecciones especiales", ["| ID | Prenda | Efecto | Tiers |", "|---|---|---|---|"], esp,
                     "Durabilidad 40-140; pierde 1-3 por golpe fuerte (daño > 12). Los niños usan ropa ligera sin armadura pesada (E1-E2).")])
    # consumibles
    comida = [f"| XF-{i:03d} | {n} | hambre −{h} | {e} |" for i, (n, h, e) in enumerate(do.COMIDAS, 1)]
    beb = [f"| XB-{i:03d} | {n} | sed −{s} | contaminación +{c} |" for i, (n, s, c) in enumerate(do.BEBIDAS, 1)]
    alc = [f"| XA-{i:03d} | {n} | {e} | adicción {a} |" for i, (n, e, a) in enumerate(do.ALCOHOLES, 1)]
    escribir_grupo("COMIDA_BEBIDA_CATALOGO", "CATÁLOGO DE COMIDA, BEBIDA Y ALCOHOL",
                   "Comida (hambre −N, 0-100), bebidas (sed −N) y alcohol. **Cantidad que se encuentra, efectos y duración: fijos (tal cual)**; los **nombres** de platos y bebidas los pone el lore (31). "
                   "**Los niños no beben alcohol ni usan químicos**: esas filas no existen para ellos (50).",
                   [("Comida", ["| ID | Alimento | Efecto en hambre | Otros efectos |", "|---|---|---|---|"], comida, ""),
                    ("Bebidas", ["| ID | Bebida | Efecto en sed | Riesgo |", "|---|---|---|---|"], beb, ""),
                    ("Alcohol (solo adultos)", ["| ID | Bebida | Efecto 1 h | Adicción |", "|---|---|---|---|"], alc, "")])
    med = [f"| XM-{i:03d} | {n} | {e} | {v} |" for i, (n, e, v) in enumerate(do.MEDICINAS, 1)]
    qui = [f"| XQ-{i:03d} | {n} | {e} | adicción {a} · abstinencia −1 a la característica afectada |" for i, (n, e, a) in enumerate(do.QUIMICOS, 1)]
    amb = [f"| XE-{i:03d} | {n} | {e} |" for i, (n, e) in enumerate(do.AMBIENTALES, 1)]
    escribir_grupo("MEDICINAS_QUIMICOS_CATALOGO", "CATÁLOGO DE MEDICINAS, QUÍMICOS Y AMBIENTALES",
                   "Medicinas y vendas (valor en cuñas o la moneda del lore), químicos de combate con adicción y abstinencia (31) y consumibles ambientales y de supervivencia. Efectos fijos; nombres del lore. "
                   "Químicos y alcohol: solo adultos (50).",
                   [("Medicinas", ["| ID | Medicina | Efecto | Valor |", "|---|---|---|---|"], med, ""),
                    ("Químicos de combate (solo adultos)", ["| ID | Químico | Efecto | Riesgo |", "|---|---|---|---|"], qui, ""),
                    ("Ambientales y de supervivencia", ["| ID | Objeto | Efecto |", "|---|---|---|"], amb, "")])
    import random
    rng = random.Random(77)
    gj = [f"| GJ-{i:03d} | {n} | {rng.randint(1, 8)} | {round(rng.uniform(0.05, 1.5), 2)} |" for i, n in enumerate(do.CHATARRA, 1)]
    gh = [f"| GH-{i:03d} | {n} | {rng.randint(3, 60)} | {round(rng.uniform(0.2, 4), 1)} |" for i, n in enumerate(do.HERRAMIENTAS, 1)]
    gk = [f"| GK-{i:03d} | {n} | clave, dato o acceso |" for i, n in enumerate(do.LLAVES_DATOS, 1)]
    gd = [f"| GD-{i:03d} | {n} | lectura (XP pequeña la primera vez) |" for i, n in enumerate(do.DOCUMENTOS, 1)]
    gm = [f"| GM-{i:03d} | {n} | {e} |" for i, (n, e) in enumerate(do.MEJORAS, 1)]
    gv = [f"| GV-{i:03d} | {n} | {rng.randint(5, 200)} | {round(rng.uniform(0.1, 2), 1)} |" for i, n in enumerate(do.VALOR, 1)]
    escribir_grupo("OBJETOS_GENERALES_CATALOGO", "CATÁLOGO DE OBJETOS GENERALES, HERRAMIENTAS Y MEJORAS",
                   "Chatarra y componentes, herramientas, llaves, documentos, mejoras de arma y armadura, y objetos de valor o de entretenimiento. Valores y pesos orientativos (tal cual); nombres del lore. "
                   "Aun lo que parece inútil puede servir para comercio, fabricación o misiones (10, 46). Los objetos de misión se generan con ID propio y no se venden.",
                   [("Chatarra y componentes", ["| ID | Objeto | Valor | Peso |", "|---|---|---|---|"], gj, ""),
                    ("Herramientas", ["| ID | Herramienta | Valor | Peso |", "|---|---|---|---|"], gh, ""),
                    ("Llaves, accesos y datos", ["| ID | Objeto | Función |", "|---|---|---|"], gk, ""),
                    ("Libros y documentos", ["| ID | Documento | Uso |", "|---|---|---|"], gd, ""),
                    ("Mejoras de arma y armadura", ["| ID | Mejora | Efecto |", "|---|---|---|"], gm, "Máximo 2 mejoras por objeto (29)."),
                    ("Objetos de valor y entretenimiento", ["| ID | Objeto | Valor | Peso |", "|---|---|---|---|"], gv, "")])


def main():
    for viejo in CARPETA.glob("[5-9][0-9]_*.md"):
        if viejo.name[:2] != "99" and int(viejo.name[:2]) >= 53:
            viejo.unlink()
    a = asignaciones.asignar()
    fases()
    npcs(a)
    misiones()
    ubicaciones()
    objetos()
    print(f"{len(ESCRITOS)} bloques ({ESCRITOS[0][0]}..{ESCRITOS[-1][0]}):")
    for n, nombre, titulo, pal in ESCRITOS:
        print(f"  {nombre:50s} {pal:5d} palabras")
    if SIGUIENTE[0] > 99:
        sys.exit("ERROR: se pasa del bloque 98 (99 queda para Dependencia del lore)")


if __name__ == "__main__":
    main()
