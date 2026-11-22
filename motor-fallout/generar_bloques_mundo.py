#!/usr/bin/env python3
"""Escribe los bloques 43 (mapa), 44 (misiones principales) y 45 (misiones secundarias)
a partir de simulador/mundo.py, que es la misma fuente que usa el simulador.

Uso: python3 -I generar_bloques_mundo.py
"""
import sys
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
sys.path.insert(0, str(CARPETA / "simulador"))
import mundo  # noqa: E402

CLASE = {"S": "Segura", "N": "Normal", "H": "Hostil"}
ITEM = {k: v[0] for k, v in mundo.OBJETOS.items()}

# Descripcion larga de los NPC que dan misiones (personalidad y situacion).
LARGO = {
    "N-01": "viejo vecino del Faro, cascarrabias y protector; recuerda cada paso que dio el mentor del protagonista y se enoja cuando alguien lo trata como a un viejo inútil, pero deja la puerta abierta a cualquiera que tenga hambre",
    "N-02": "líder de Ciudad Horno, pragmática y firme; mide a la gente por lo que cumple, no por lo que promete, y es justa incluso con quien la contradice",
    "N-03": "capitán de la Guardia del Cantil, honesto y rígido; su orgullo es el uniforme, su debilidad es no saber pedir ayuda",
    "N-04": "granjera agotada, de humor seco, que habla con sus animales más que con las personas; no suelta un reclamo hasta que se resuelve",
    "N-07": "comerciante de animales de carga, bonachón y miedoso; cuenta todo con exageración y siempre cree que lo van a robar",
    "N-08": "médica de Horno, cansada y ética; su sarcasmo es la forma que tiene de no llorar, y nunca le niega ayuda a un herido",
    "N-09": "mecánico obsesivo y perfeccionista; no repara nada sin las piezas exactas y se ofende si alguien improvisa",
    "N-10": "cazador callado y desconfiado; mide cada palabra, no falla un tiro y respeta a quien rastrea bien",
    "N-11": "científica de la Hermandad del Faro, distraída y brillante; olvida comer y recuerda cada dato, y trata a las criaturas como especímenes antes que como amenazas",
    "N-12": "mensajero nervioso, veloz y chismoso; corre todo el día y se queja de que nadie le da tiempo para respirar",
    "N-13": "anciana del barrio, nostálgica y terca; vive entre recuerdos de una casa que ya no existe y no acepta lástima, solo compañía",
    "N-14": "capataz del silo, autoritario pero justo; vive cansado de arreglar lo que otros rompen",
    "N-15": "pescadora alegre y supersticiosa; le pone nombre a cada ola y no entra al agua sin una oración corta",
    "N-16": "ex saqueador arrepentido, culposo y servicial; no se perdona lo que hizo y busca reparar cada cosa",
    "N-17": "cocinera generosa y mandona; alimenta a medio pueblo y sabe todos los chismes",
    "N-18": "inventor excéntrico y optimista; ve oportunidades donde otros ven chatarra y se distrae a mitad de una frase",
    "N-19": "líder vecinal indignada y organizada; no tiene miedo y no acepta que le digan que no se puede",
    "N-25": "borracho simpático y llorón; ordena mal sus recuerdos pero nunca olvida a un amigo",
    "N-26": "viajero educado y asustado; agradece cada gesto y se disculpa por molestar",
    "N-27": "amiga de infancia, curiosa e ingenua; sueña con dibujar el mapa de todo el Salar y confía demasiado en la gente",
    "N-29": "amiga hija de la líder de Horno; responsable y tensa, quiere demostrar que merece su apellido",
    "N-21": "mentor del protagonista, paciente, sabio y tozudo; prefiere enseñar con preguntas y no cuenta todo de golpe",
}

STEP = {
    "talk": lambda s: f"hablar con {mundo.NPCS[s[1]]['nombre']}",
    "goto": lambda s: f"viajar a {mundo.LOCS[s[1]]['nombre']}",
    "get": lambda s: f"conseguir «{'registrar el baúl del hogar' if s[2] == 'baul' else ITEM.get(s[2], s[2])}» en {mundo.LOCS[s[1]]['nombre']}",
    "search_hidden": lambda s: f"buscar la conexión oculta en {mundo.LOCS[s[1]]['nombre']} (hacia {mundo.LOCS[s[2]]['nombre']})",
    "kill": lambda s: f"derrotar {s[2]} enemigos en {mundo.LOCS[s[1]]['nombre']}",
    "kill_species": lambda s: f"derrotar {s[2]} enemigos de las especies pedidas en {mundo.LOCS[s[1]]['nombre']}",
    "boss": lambda s: f"vencer a {mundo.JEFES[s[2]]['nombre']} en {mundo.LOCS[s[1]]['nombre']}",
    "hack": lambda s: f"hackear el terminal de {mundo.LOCS[s[1]]['nombre']}",
    "give": lambda s: f"entregar «{ITEM.get(s[2], s[2])}» a {mundo.NPCS[s[1]]['nombre']}",
    "choose": lambda s: f"ELEGIR BANDO: {s[1]} o {s[2]} (el otro grupo pasa a ser hostil)",
    "recruit": lambda s: f"reclutar a {mundo.COMPANEROS[s[1]]['nombre']}",
    "craft": lambda s: f"fabricar «{s[1]}» en el banco de trabajo",
    "collect": lambda s: f"recolectar {s[3]} × {ITEM.get(s[2], s[2])} en {mundo.LOCS[s[1]]['nombre']}",
    "deliver_msg": lambda s: f"llevar el mensaje a {mundo.NPCS[s[1]]['nombre']}",
    "discover": lambda s: f"descubrir {s[1]} ubicaciones nuevas",
}


def pasos(q):
    return "; ".join(f"{i + 1}) {STEP[p[0]](p)}" for i, p in enumerate(mundo.QUESTS[q]["steps"]))


def rec(q):
    out = []
    for it in mundo.QUESTS[q].get("rec", []):
        out.append(f"{it[5:]} cuñas" if it.startswith("cuñas") else ITEM.get(it, it))
    return ", ".join(out) or "—"


def bloque_43():
    L = ["# 43 · MAPA Y UBICACIONES DE «EL SALAR»", "",
         "Red de 21 ubicaciones (tal cual). IDs y conexiones son fijos; la IA genera los detalles de escena con 04, 05 y 28. "
         "Clase: Segura / Normal / Hostil. **Cama** = sirve como destino de arrastre tras una derrota (39). "
         "**Nivel** = nivel base de la zona (los enemigos hostiles usan max(nivel de zona, nivel del jugador − 2)).", "",
         "Conexiones libres salvo indicación. Abrir el mapa grande permite viaje rápido solo a ubicaciones descubiertas con ruta válida; "
         "el mapa pequeño de muñeca solo muestra y marca ubicaciones cercanas.", "",
         "| ID | Nombre | Clase | Espacio | Región | Nivel | Conexiones | Cama | Contenedores (cerradura) | Notas |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for lid, d in mundo.LOCS.items():
        cont = ", ".join(f"{c[0]} {c[1]} ({c[2]})" for c in d["cont"])
        notas = []
        if d.get("oculta"):
            notas.append("conexión oculta a " + ", ".join(f"{t} ({v})" for t, v in d["oculta"]))
        if d.get("bloqueada"):
            notas.append("acceso requiere: " + ITEM.get(d["bloqueada"][0], d["bloqueada"][0]) if d["bloqueada"][0] in ITEM else "acceso requiere: Purificador encendido")
        if d.get("jefe"):
            notas.append("jefe: " + mundo.JEFES[d["jefe"]]["nombre"])
        if d.get("terminal"):
            notas.append("terminal hackeable")
        if d.get("ventana"):
            notas.append("hogar: salida por ventana (atasco 40-60%)")
        npc = ", ".join(mundo.NPCS[n]["nombre"] for n in d["npc"][:3])
        if npc:
            notas.append("NPC: " + npc + ("…" if len(d["npc"]) > 3 else ""))
        L.append(f"| {lid} | {d['nombre']} | {CLASE[d['clase']]} | {'Interior' if d['espacio'] == 'int' else 'Exterior'} | {d['region']} | {d['nivel']} | "
                 f"{', '.join(d['conn'])} | {'sí' if d['cama'] else 'no'} | {cont or '—'} | {'; '.join(notas) or '—'} |")
    L += ["", "## DESCRIPCIONES BREVES (base de la escena)"]
    for lid, d in mundo.LOCS.items():
        L.append(f"- **{lid} {d['nombre']}** ({d['bioma']}): {d['desc']}")
    L += ["", "## POBLACIONES POR ZONA (pool de especies; filtro por nivel, bloque 27)",
          "desierto/matorral: caninos, herbívoros pequeños y medianos · insectos: insectos mutantes · marino: marinos blandos, parásitos de agua, slimes · "
          "subterráneo: parásitos genéricos y slimes · robots: artificiales (36) · saqueadores / tasadores: humanos y perros de guerra · ganado: animales de granja · "
          "civil: sin enemigos fijos (3% de eventos).",
          "", "## REGLAS DE ESTA RED (tal cual)",
          "- El hogar (L-001) es el punto de partida y siempre una ubicación segura con cama, baúl, alacena y banco de trabajo (39).",
          "- Cada ubicación nueva se descubre al llegar a una vecina; las conexiones ocultas se hallan con BUSCAR (garantía en la 4.ª búsqueda, 04).",
          "- Oasis Verde (L-021) solo aparece cuando el Purificador de la Torre vuelve a funcionar (M-08)."]
    return "\n".join(L) + "\n"


def bloque_44():
    L = ["# 44 · MISIONES PRINCIPALES: «EL FARO Y EL PURIFICADOR»", "",
         "Campaña principal de ocho misiones (tal cual). Se aceptan hablando con el dador. Una misión completada no se reinicia (13). "
         "Los pasos son ejecutables por botones. Las recompensas de XP son fijas (27); el lore pone nombres. "
         "Después de la última misión el mundo sigue abierto: los hostiles se regeneran, hay comercio y se puede seguir explorando.", ""]
    for q, d in mundo.QUESTS.items():
        if d["tipo"] != "principal":
            continue
        L += [f"## {q} · {d['nombre']}", f"- **Dador:** {mundo.NPCS[d['giver']]['nombre']} ({LARGO.get(d['giver'], mundo.NPCS[d['giver']]['pers'])}).",
              f"- **Nivel sugerido:** {d['nivel']}. **Historia:** {d['desc']}", f"- **Pasos:** {pasos(q)}.",
              f"- **Recompensa:** {d['xp']} XP; {rec(q)}.", ""]
    L += ["## ELECCIÓN DE BANDO (M-05)",
          "Ciudad Horno (fundidores, comercio) y la Guardia del Cantil (milicia de caminos) se disputan el Purificador. Elegir uno deja al otro como **hostil**: "
          "aparece una patrulla rival persistente (humanos) en la Ruta de Sal y los comerciantes del bando perdedor suben sus precios 30%. "
          "La decisión no existe cuando el enemigo es una criatura (no humano). Se registra en [FLAGS] `bando_M-05`.",
          "", "## JEFES (tal cual)",
          "| Jefe | Lugar | Nivel | PV | Daño | Invocación |", "|---|---|---|---|---|---|"]
    for k, j in mundo.JEFES.items():
        L.append(f"| {j['nombre']} | {mundo.LOCS[j['loc']]['nombre']} | {j['nivel']} | {j['pv']} | {j['dano'][0]}-{j['dano'][1]} | hasta {j['sub_max']} vivos, 3 ciclos, cooldown 3 rondas |")
    L += ["", "## ORDEN Y REQUISITOS", "Cada principal requiere la anterior hecha. M-05 pide nivel 9. En 10 simulaciones con semillas distintas la campaña completa (8 principales y 20 secundarias) terminó entre los días 111 y 187 de juego (promedio 151) a nivel 19."]
    return "\n".join(L) + "\n"


def bloque_45():
    L = ["# 45 · MISIONES SECUNDARIAS Y GENERADOR AUTOMÁTICO", "",
         "Veinte misiones secundarias fijas (tal cual) y una regla para generar nuevas sin intervención. "
         "Los dadores y su personalidad son del lore; los pasos, XP y recompensas son fijos.", ""]
    for q, d in mundo.QUESTS.items():
        if d["tipo"] != "secundaria":
            continue
        comp = f" **Compañero:** {mundo.COMPANEROS[d['comp']]['nombre']}." if d.get("comp") else ""
        L += [f"- **{q} · {d['nombre']}** (nivel {d['nivel']}) — {mundo.NPCS[d['giver']]['nombre']} en {mundo.LOCS[mundo.NPCS[d['giver']]['loc']]['nombre']}, "
              f"{LARGO.get(d['giver'], mundo.NPCS[d['giver']]['pers'])}. {d['desc']} *Pasos:* {pasos(q)}. *Recompensa:* {d['xp']} XP; {rec(q)}.{comp}"]
    L += ["", "## GENERADOR AUTOMÁTICO DE MISIONES (tal cual)",
          "Cada NPC con `necesidad` genera una misión radiante al hablar con él por tercera vez, según: **personalidad**, **situación**, **lugar** y **enemigos cercanos**.",
          "| Situación del NPC | Tipo de misión | Pasos tipo |", "|---|---|---|",
          "| Perdió un objeto | Recuperar | ir al lugar, registrar contenedores, volver |",
          "| Amenazado por criaturas | Despejar | derrotar N grupos de la especie que merodea, volver |",
          "| Falta un recurso | Recolectar | recolectar o cazar, entregar |",
          "| Conflicto entre grupos humanos | Elegir bando | hablar con ambos, elegir, derrotar al otro |",
          "| Familiar o amigo atrapado | Rescatar | llegar, despejar, hablar |",
          "| Necesita mensajes o viajes | Repartir | visitar N ubicaciones |",
          "| Necesita una máquina | Reparar / hackear | conseguir piezas, fabricar o hackear |",
          "Reglas: la misión usa **solo elementos ya existentes** (ubicaciones, NPC, contenedores); recompensa = XP según nivel (60-250) + objeto del lore; si el enemigo es **criatura no humana** no hay elección de bando; "
          "si es **humano**, siempre se puede elegir bando. Máximo 3 misiones radiantes activas."]
    return "\n".join(L) + "\n"


def main():
    for nombre, f in (("43_MAPA_Y_UBICACIONES.md", bloque_43), ("44_MISIONES_PRINCIPALES.md", bloque_44),
                      ("45_MISIONES_SECUNDARIAS.md", bloque_45)):
        texto = f()
        (CARPETA / nombre).write_text(texto, encoding="utf-8")
        print(f"{nombre}: {len(texto.split())} palabras")


if __name__ == "__main__":
    main()
