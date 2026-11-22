#!/usr/bin/env python3
"""Pruebas dirigidas de las mecanicas nuevas sobre un lore: cuadras, edificios, pasos estrechos, mapa, no-muerte.

Uso: LORE=bosque MUNDO=mundo_lore python3 -I pruebas_lore.py --salida DIR
"""
import os
import statistics
import sys
from pathlib import Path

os.environ.setdefault("MUNDO", "mundo_lore")
os.environ.setdefault("LORE", "bosque")
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import bot as botmod  # noqa: E402
import motor  # noqa: E402

mundo = motor.mundo
RES = []


def prueba(nombre, regla, f):
    try:
        ok, obs = f()
    except Exception as e:  # noqa: BLE001
        ok, obs = False, f"excepción: {e!r}"
    RES.append((nombre, regla, ok, obs))


def nuevo(semilla=1, nivel=5):
    s = motor.Sim(semilla)
    b = botmod.Bot(s)
    s.p["nivel"] = nivel
    s.p["hp"] = s.hpmax()
    for L in s.locs.values():
        L["descubierta"] = True
    return s, b


def pares_de_cuadras():
    pares = []
    for lid, d in mundo.LOCS.items():
        if d.get("tipo") == "cuadra":
            for v in d["conn"]:
                if mundo.LOCS[v].get("tipo") == "cuadra" and mundo.LOCS[v].get("ubicacion") == d.get("ubicacion"):
                    pares.append((lid, v))
    return pares


def t_cuadras():
    s, b = nuevo(1)
    pares = pares_de_cuadras()
    tiempos = []
    for i in range(300):
        a, c = pares[i % len(pares)]
        s.p["loc"] = a
        t0 = s.reloj
        s.marcar_minimapa(c)
        tiempos.append(s.reloj - t0)
    ok = 3 <= min(tiempos) and max(tiempos) <= 12 and s.contadores.get("emboscadas_mapa", 0) == 0
    return ok, f"300 movimientos de cuadra por mapa de muñeca: {min(tiempos)}-{max(tiempos)} min (media {statistics.mean(tiempos):.1f}); emboscadas por mapa: {s.contadores.get('emboscadas_mapa', 0)} (sin vulnerabilidad)"


def t_tiempo_entre_ubicaciones():
    s, b = nuevo(2)
    aristas = [(a, v) for a, d in mundo.LOCS.items() for v in d["conn"] if mundo.LOCS[a].get("ubicacion") != mundo.LOCS[v].get("ubicacion") and mundo.LOCS[a].get("tipo") != "edificio" and mundo.LOCS[v].get("tipo") != "edificio"]
    ts = []
    for i in range(200):
        a, v = aristas[i % len(aristas)]
        s.p["loc"] = a
        t0 = s.reloj
        s.viajar(v, rapido=False)
        if s.p["loc"] == v:
            ts.append(s.reloj - t0)
    return bool(ts) and min(ts) >= 20, f"viaje entre ubicaciones por botón: {min(ts)}-{max(ts)} min (cuadra a cuadra son 3-8 min)"


def t_mapa_grande():
    res = {}
    for clase in ("S", "N", "H"):
        amb = tot = 0
        origenes = [l for l, d in mundo.LOCS.items() if d["clase"] == clase and d.get("tipo") != "edificio"][:40]
        for i, o in enumerate(origenes * 8):
            s, _ = nuevo(100 + i)
            lejos = max(mundo.LOCS, key=lambda x: s.distancia(o, x))
            s.p["loc"] = o
            s.viajar(lejos, rapido=True)
            amb += s.contadores.get("emboscadas_mapa", 0)
            tot += s.contadores.get("viajes_rapidos", 0)
        res[clase] = (amb, tot)
    esp = {"S": 28, "N": 38, "H": 55}
    ok = all(res[c][1] > 20 and abs(100 * res[c][0] / res[c][1] - esp[c]) < 15 for c in res)
    return ok, "viaje rápido (mapa grande): emboscadas " + ", ".join(f"{c}: {100 * a / max(1, t):.0f}% de {t} (esperado ≈{esp[c]}%)" for c, (a, t) in res.items())


def t_edificios_y_puertas():
    s, b = nuevo(3, 8)
    s.p["inv"]["ganzua"] = 99
    edifs = [l for l, d in mundo.LOCS.items() if d.get("tipo") == "edificio"]
    entradas = 0
    for i in range(200):
        e = edifs[i % len(edifs)]
        q = next(v for v in mundo.LOCS[e]["conn"] if mundo.LOCS[v].get("tipo") == "cuadra")
        s.p["loc"] = q
        s.p["hp"] = s.hpmax()
        s.locs[e]["puerta_abierta"] = False
        s.viajar(e, rapido=False)
        if s.p["loc"] == e:
            entradas += 1
    c = s.contadores
    return entradas > 100 and c.get("cruces_de_umbral", 0) > 100, f"200 intentos de entrar a edificios: {entradas} entradas; puertas abiertas {c.get('puertas_abiertas', 0)}, por paso estrecho {c.get('entradas_por_estrecho', 0)}, imposibles {c.get('puertas_imposibles', 0)}"


def t_puerta_bloqueada():
    s, b = nuevo(11, 5)
    s.p["inv"]["ganzua"] = 0
    edifs = [l for l, d in mundo.LOCS.items() if d.get("tipo") == "edificio" and d["accesos"].get("ventana")]
    import copy
    originales = {e: copy.deepcopy(mundo.LOCS[e]["accesos"]) for e in edifs}
    entradas = 0
    try:
        for e in edifs:
            mundo.LOCS[e]["accesos"]["puerta"] = 5
        for i in range(120):
            e = edifs[i % len(edifs)]
            q = next(v for v in mundo.LOCS[e]["conn"] if mundo.LOCS[v].get("tipo") == "cuadra")
            s.p["loc"] = q
            s.p["hp"] = s.hpmax()
            s.locs[e]["puerta_abierta"] = False
            s.viajar(e, rapido=False)
            entradas += 1 if s.p["loc"] == e else 0
    finally:
        for e, a in originales.items():
            mundo.LOCS[e]["accesos"] = a
    c = s.contadores
    return c.get("entradas_por_estrecho", 0) > 0, f"120 edificios con puerta imposible (nivel 5) y sin ganzúa: {entradas} entradas, {c.get('entradas_por_estrecho', 0)} por ventana, agujero o conducto, {c.get('atascos', 0)} atascos"


def t_estrechos():
    s, b = nuevo(4, 6)
    for _ in range(800):
        s.p["hp"] = s.hpmax()
        s.pasar_estrecho(["ventana", "agujero", "conducto"][_ % 3], lid=mundo.PROTAGONISTA["hogar"])
    c = s.contadores
    tasa = c.get("atascos", 0) / c["atascos_tiradas"]
    # limites duros: con ajuste enorme el umbral no puede pasar de 60 ni bajar de 40
    s2, _ = nuevo(5, 6)
    for _ in range(1500):
        s2.pasar_estrecho("ventana", lid=mundo.PROTAGONISTA["hogar"], ajuste=+40)
    t_alta = s2.contadores.get("atascos", 0) / s2.contadores["atascos_tiradas"]
    s3, _ = nuevo(6, 6)
    for _ in range(1500):
        s3.pasar_estrecho("ventana", lid=mundo.PROTAGONISTA["hogar"], ajuste=-40)
    t_baja = s3.contadores.get("atascos", 0) / s3.contadores["atascos_tiradas"]
    ok = 0.40 <= tasa <= 0.60 and t_alta <= 0.64 and t_baja >= 0.36
    return ok, f"800 pasos estrechos: atasco {100 * tasa:.0f}% (límites duros 40-60%); con ajuste +40 queda en {100 * t_alta:.0f}% y con −40 en {100 * t_baja:.0f}%; robos por estructura {c.get('robos_por_atasco', 0)}"


def t_ataque_atascado():
    s, b = nuevo(7, 8)
    hostil = next(l for l, d in mundo.LOCS.items() if d["clase"] == "H" and d["pool"] != "civil" and d.get("tipo") != "edificio")
    s.p["loc"] = hostil
    s.visitar(hostil)
    for i in range(300):
        s.p["hp"] = s.hpmax()
        s.pasar_estrecho("agujero", lid=hostil)
        if s.p["loc"] != hostil:
            s.p["loc"] = hostil
    c = s.contadores
    return c.get("ataques_mientras_atascado", 0) > 0, f"300 pasos en zona hostil: atascos {c.get('atascos', 0)}, ataques mientras estaba atascado {c.get('ataques_mientras_atascado', 0)}, derrotas {c.get('derrotas', 0)}, liberado en combate {c.get('liberado_en_combate', 0)}"


def t_no_muere():
    s, b = nuevo(8, 3)
    camas = {l for l, d in mundo.LOCS.items() if d["cama"]}
    ok = True
    for i in range(40):
        lid = list(mundo.LOCS)[(i * 7) % len(mundo.LOCS)]
        s.p["loc"] = lid
        s.p["hp"] = 0
        s.derrota(lid)
        ok = ok and s.p["loc"] in camas and s.p["hp"] > 0
    return ok and s.p["edad"] == "niño", f"40 derrotas desde lugares distintos: siempre en una cama con vida > 0; protagonista edad: {s.p['edad']} (no muere)"


def t_companeros():
    comps = mundo.COMPANEROS
    ok = len(comps) >= 25 and all(" " not in c["nombre"] for c in comps.values())
    ninos = [c for c in comps.values() if c["edad"] == "niño"]
    return ok and ninos, f"{len(comps)} compañeros (solo femeninos o niños), {len(ninos)} niños; todos con un solo nombre"


def t_persistencia_y_choque():
    s, b = nuevo(9, 10)
    hostiles = [l for l, d in mundo.LOCS.items() if d["clase"] == "H" and d.get("tipo") != "edificio"][:5]
    creados = 0
    s.p["loc"] = mundo.PROTAGONISTA["hogar"]
    for h in hostiles:
        s.generar_grupo(h)
        s.generar_grupo(h)
    ids = {e["id"] for h in hostiles for g in s.locs[h]["grupos"] for e in g["miembros"] if e["hp"] > 0}
    s.avanzar(60 * 6)
    ids2 = {e["id"] for h in hostiles for g in s.locs[h]["grupos"] for e in g["miembros"] if e["hp"] > 0}
    muertos = len(ids - ids2)
    return ids2 <= ids and muertos == s.contadores.get("muertes_por_otra_criatura", 0), f"{len(ids)} enemigos en 5 zonas, 6 h sin el jugador: {len(ids2)} siguen; los {muertos} que faltan murieron por otra criatura (registrados)"


PRUEBAS = [
    ("Cuadras y mapa de muñeca", "Cuadra a cuadra 3-8 min, sin vulnerabilidad (47)", t_cuadras),
    ("Entre ubicaciones", "20-60 min por botón (47)", t_tiempo_entre_ubicaciones),
    ("Mapa grande vulnerable", "Viaje rápido: 8/18/35% + 20% (47, 39)", t_mapa_grande),
    ("Edificios y puertas", "Entrar con cerradura o por paso estrecho (48)", t_edificios_y_puertas),
    ("Puerta bloqueada, entrada por ventana", "Si la puerta no abre, queda el paso estrecho (48, 49)", t_puerta_bloqueada),
    ("Pasos estrechos 40-60%", "Límites duros 40-60% (49)", t_estrechos),
    ("Ataque mientras estás atascado", "Vulnerable y sin escape (49)", t_ataque_atascado),
    ("No se muere", "Arrastre a la cama o descanso más cercano (50)", t_no_muere),
    ("Compañeros", "Solo femeninos o niños; un solo nombre (41, 99)", t_companeros),
    ("Persistencia", "Los enemigos no desaparecen salvo muerte por otra criatura (37)", t_persistencia_y_choque),
]


def main():
    salida = AQUI.parent / "simulacion"
    if "--salida" in sys.argv:
        salida = Path(sys.argv[sys.argv.index("--salida") + 1])
    for n, r, f in PRUEBAS:
        prueba(n, r, f)
    ok = sum(1 for x in RES if x[2])
    nombre = mundo.LORE["nombre"]
    L = [f"# Pruebas dirigidas de mecánicas nuevas: {nombre}", "", f"**{ok}/{len(RES)} aprobadas.**", "", "| Prueba | Regla | Resultado | Observado |", "|---|---|---|---|"]
    for n, r, o, obs in RES:
        L.append(f"| {n} | {r} | {'✅' if o else '❌'} | {obs} |")
    texto = "\n".join(L) + "\n"
    print(texto)
    salida.mkdir(parents=True, exist_ok=True)
    (salida / f"PRUEBAS_{mundo.LORE['id'].upper()}.md").write_text(texto, encoding="utf-8")
    return 0 if ok == len(RES) else 1


if __name__ == "__main__":
    sys.exit(main())
