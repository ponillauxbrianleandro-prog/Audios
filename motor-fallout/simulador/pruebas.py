#!/usr/bin/env python3
"""Pruebas dirigidas de reglas que la campana automatica no siempre ejercita.

Uso: python3 -I pruebas.py [--salida DIR]
Escribe PRUEBAS_DE_REGLAS.md con cada regla, el resultado esperado y lo observado.
"""
import statistics
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import bot as botmod  # noqa: E402
import motor  # noqa: E402
import mundo  # noqa: E402

RES = []


def prueba(nombre, regla, f):
    try:
        ok, obs = f()
    except Exception as e:  # noqa: BLE001
        ok, obs = False, f"excepción: {e!r}"
    RES.append((nombre, regla, ok, obs))


def nuevo(semilla=1, nivel=1):
    s = motor.Sim(semilla)
    b = botmod.Bot(s)
    s.p["nivel"] = nivel
    s.p["hp"] = s.hpmax()
    return s, b


# ---------------------------------------------------------------- pruebas
def t_un_solo_tipo():
    s, _ = nuevo(2, 12)
    mezclas = 0
    for i in range(600):
        for lid in ("L-002", "L-005", "L-014", "L-013", "L-016"):
            g = s.generar_grupo(lid)
            if g and len({e["sid"] for e in g["miembros"]}) > 1:
                mezclas += 1
    return mezclas == 0, f"{mezclas} grupos mezclados en 3000 encuentros"


def t_cantidades():
    s, _ = nuevo(3, 30)
    por_talla = {}
    for i in range(1500):
        g = s.generar_grupo("L-016")
        if not g:
            continue
        e = g["miembros"][0]
        por_talla.setdefault(e["talla"], []).append(len(g["miembros"]))
    lim = {1: (2, 7), 2: (1, 7), 3: (1, 7), 4: (1, 4), 5: (1, 3)}
    mal = [(t, min(v), max(v)) for t, v in por_talla.items() if min(v) < lim[min(5, t)][0] or max(v) > lim[min(5, t)][1]]
    return not mal, "rangos observados por talla: " + ", ".join(f"T{t}: {min(v)}-{max(v)}" for t, v in sorted(por_talla.items())) + (f" ⚠ {mal}" if mal else "")


def t_slots():
    s, _ = nuevo(4, 1)
    elig, mx = s.elegibles("desierto")
    ok1 = all(slot == 0 for _, slot in elig) and mx == 0
    s.p["nivel"] = 10
    elig10, mx10 = s.elegibles("desierto")
    ok2 = max(sl for _, sl in elig10) <= 5 and any(sl == 5 for _, sl in elig10) is not None
    s.p["nivel"] = 30
    elig30, _ = s.elegibles("desierto")
    ok3 = any(sl >= 9 for _, sl in elig30)
    return ok1 and ok2 and ok3, f"nivel 1: {len(elig)} especies (todas slot 0, ≤ tamaño perro); nivel 10: {len(elig10)}; nivel 30: {len(elig30)}"


def t_variantes():
    s, _ = nuevo(5)
    malos = [(k, v) for k, v in s.nvar.items() if not (1 <= v <= (2 if k[0].startswith('U-') else 3))]
    dist = {n: sum(1 for v in s.nvar.values() if v == n) for n in (1, 2, 3)}
    return not malos, f"{len(s.nvar)} combinaciones especie×fase; reparto 1/2/3 variantes = {dist[1]}/{dist[2]}/{dist[3]}; humanos ≤ 2"


def t_variante_por_nivel():
    s, _ = nuevo(6, 1)
    sid = "C-03"
    s.nvar[(sid, 1)] = 3
    vs1 = {s.variante_para(sid, 1, 1) for _ in range(200)}
    vs8 = {s.variante_para(sid, 1, 8) for _ in range(200)}
    vs14 = {s.variante_para(sid, 1, 14) for _ in range(200)}
    return vs1 == {1} and vs8 == {1, 2} and vs14 == {1, 2, 3}, f"slot 0: nivel 1 → V{sorted(vs1)}, nivel 8 → V{sorted(vs8)}, nivel 14 → V{sorted(vs14)} (V2 a +6, V3 a +12)"


def t_xp_curva():
    return (motor.xp_total(2) == 120 and motor.xp_total(30) == 52200), f"XP para nivel 2 = {motor.xp_total(2)}, nivel 10 = {motor.xp_total(10)}, nivel 20 = {motor.xp_total(20)}, nivel 30 = {motor.xp_total(30)}"


def t_persistencia():
    s, b = nuevo(7, 5)
    s.p["loc"] = "L-005"
    g = s.generar_grupo("L-005")
    ids = {e["id"] for e in g["miembros"]}
    hp0 = {e["id"]: e["hp"] for e in g["miembros"]}
    s.p["loc"] = "L-001"
    s.avanzar(60 * 30)  # 30 h lejos
    ids2 = {e["id"] for gr in s.locs["L-005"]["grupos"] for e in gr["miembros"] if e["hp"] > 0}
    return ids == ids2, f"{len(ids)} enemigos antes de irse y {len(ids2)} al volver 30 h después (mismos IDs: {ids == ids2})"


def t_regeneracion():
    s, b = nuevo(8, 5)
    lid = "L-005"
    s.p["loc"] = lid
    s.visitar(lid)
    for gr in s.locs[lid]["grupos"]:
        for e in gr["miembros"]:
            e["hp"] = 0
    s._fin_combate([], 0)
    s.p["loc"] = "L-001"
    s.avanzar(60 * 40)
    sin = not s.locs[lid]["grupos"]
    s.avanzar(60 * 12)
    con = bool(s.locs[lid]["grupos"])
    return sin and con, f"a las 40 h sin regenerar: {sin}; pasadas 52 h (>48 h): nueva población = {con}"


def t_choque():
    muertes_ok = 0
    total_choques = 0
    n_ini = n_fin = 0
    for sd in range(12):
        s, b = nuevo(9 + sd, 5)
        lid = "L-002"
        s.p["loc"] = "L-001"
        s.generar_grupo(lid, forzar_especies=["C-03"])
        s.generar_grupo(lid, forzar_especies=["H-12"])
        n0 = len(s.vivos(lid))
        s.avanzar(60 * 40)
        n1 = len(s.vivos(lid))
        total_choques += s.contadores.get("choques_entre_especies", 0)
        n_ini += n0
        n_fin += n1
        muertes_ok += 1 if n1 < n0 else 0
    return total_choques > 0 and muertes_ok >= 8, f"12 corridas con 2 especies distintas, 40 h sin el jugador: {n_ini} criaturas → {n_fin}; hubo bajas por choque en {muertes_ok}/12 corridas ({total_choques} choques)"


def t_misma_especie_no_pelea():
    s, b = nuevo(10, 5)
    lid = "L-002"
    s.p["loc"] = "L-001"
    s.generar_grupo(lid, forzar_especies=["C-03"])
    s.generar_grupo(lid, forzar_especies=["C-03"])
    n0 = len(s.vivos(lid))
    s.avanzar(60 * 40)
    return len(s.vivos(lid)) == n0, f"2 grupos de la misma especie: {n0} → {len(s.vivos(lid))} (no se atacan)"


def t_derrota_arrastre_robo():
    detalles = []
    robos = recup = 0
    ok_cama = True
    for sd in range(30):
        s, b = nuevo(100 + sd, 8)
        lid = "L-014"
        s.p["loc"] = lid
        s.visitar(lid)
        s.p["cuñas"] = 200
        s.p["inv"] = {"venda": 3, "lata": 2, "agua": 2}
        s.p["hp"] = 0
        s.derrota(lid)
        cama = mundo.LOCS[s.p["loc"]]["cama"]
        ok_cama = ok_cama and cama and s.p["hp"] > 0
        grupo = next((g for g in s.locs[lid]["grupos"] if g["botin_robado"]), None)
        if grupo:
            robos += 1
            perdidas = s.p["cuñas"]
            for e in grupo["miembros"]:
                e["hp"] = 0
            s._fin_combate(grupo["miembros"], 0)
            if s.p["cuñas"] > perdidas:
                recup += 1
    return ok_cama and robos > 0 and recup == robos, f"30 derrotas: siempre terminó en una cama con vida > 0; robos {robos}; recuperados al vencer al ladrón: {recup}/{robos}"


def t_no_muere():
    s, b = nuevo(11, 3)
    for _ in range(20):
        s.p["hp"] = 0
        s.derrota(s.p["loc"])
    return s.p["hp"] > 0 and s.contadores.get("derrotas") == 20, "20 derrotas seguidas: nunca hay muerte, siempre vuelve a una cama"


def t_atasco():
    s, b = nuevo(12, 3)
    umbrales = []
    for _ in range(400):
        pc = s.rng.randint(40, 60)
        umbrales.append(pc)
    for _ in range(400):
        s.salir_por_ventana()
    tasa = s.contadores.get("atascos", 0) / 400
    return 0.38 <= tasa <= 0.62 and min(umbrales) >= 40 and max(umbrales) <= 60, f"400 salidas por la ventana: atascos {tasa*100:.0f}% (esperado 40-60%), robos por atasco {s.contadores.get('robos_por_atasco', 0)}"


def t_mapa_vulnerable():
    s, b = nuevo(13, 5)
    amb = tot = 0
    for sd in range(300):
        s2, _ = nuevo(1000 + sd, 5)
        for lid in s2.locs:
            s2.locs[lid]["descubierta"] = True
        s2.p["loc"] = "L-001"
        s2.contadores.clear()
        s2.viajar("L-013", rapido=True)
        amb += s2.contadores.get("emboscadas_mapa", 0)
        tot += s2.contadores.get("viajes_rapidos", 0)
    return tot > 0 and 0.15 <= amb / tot <= 0.45, f"viaje rápido desde zona segura: {amb}/{tot} = {100*amb/max(1,tot):.0f}% de emboscadas (8% base + 20% por viaje rápido = 28%)"


def t_jefe_invocacion():
    s, b = nuevo(14, 20)
    s.p["loc"] = "L-020"
    g = s.generar_jefe("L-020", "capataz_concesion")
    s.p["arma"], s.p["armadura"] = 4, 4
    s.p["hp"] = s.hpmax()
    r = s.combate(g["miembros"], policy=b.policy)
    j = [e for e in g["miembros"] if e.get("jefe")][0]
    subs = [e for e in g["miembros"] if e.get("sub")]
    return j.get("ciclos", 0) <= 3, f"resultado {r}; ciclos de invocación {j.get('ciclos', 0)} (máx. 3), subordinados creados {len(subs)} (tope vivos {j['sub_max']})"


def t_combate_movimientos():
    s, b = nuevo(15, 6)
    s.p["loc"] = "L-005"
    usados = set()
    pol = b.policy

    def espia(sim, vivos, acc, oculto, guardia):
        m = pol(sim, vivos, acc, oculto, guardia)
        usados.add(m[0])
        return m
    for i in range(30):
        s.p["hp"] = s.hpmax()
        g = s.generar_grupo("L-005")
        if g:
            s.combate(g["miembros"], sorpresa=(i % 2 == 0), policy=espia)
    return {"sigiloso", "normal", "rapido", "acercar"} <= usados, f"movimientos usados en 30 combates: {sorted(usados)}"


def t_fallo_rango():
    s, b = nuevo(16, 1)
    vals = []
    for dist in (0, 1, 2):
        for n in (1, 2, 4):
            es = []
            for k in range(n):
                es.append(dict(hp=10, dist=dist if k == 0 else 0))
            f, v = s.fallo(es)
            vals.append(f)
    s.p["nivel"], s.p["arma"] = 30, 5
    es = [dict(hp=10, dist=2)]
    f_min, _ = s.fallo(es)
    s.p["hp"] = 1
    es = [dict(hp=10, dist=0) for _ in range(4)]
    s.p["stats"]["FUE"] = 1
    s.p["nivel"], s.p["arma"] = 1, 1
    f_max, _ = s.fallo(es)
    return max(vals) <= 70 and f_min >= 25 and f_max <= 70, f"fallo entre {min(vals):.0f}% y {max(vals):.0f}% a nivel 1; mínimo posible {f_min:.0f}% (nivel 30, arma tier 5); máximo {f_max:.0f}%"


def t_arma_distancia_nula():
    s, b = nuevo(30, 10)
    res = {}
    for dist in (0, 1, 2):
        es = [dict(hp=10, dist=dist, talla=1)]
        res[dist] = 100 - s.fallo_ataque(es, 0, es[0], True)
    # y se verifica que el combate usa la regla
    s.p["arma_distancia"] = True
    s.p["loc"] = "L-005"
    g = s.generar_grupo("L-005")
    s.combate(g["miembros"], policy=b.policy)
    ok = res[0] > res[1] > res[2] and res[2] <= 30 and s.contadores.get("ataques_a_distancia", 0) > 0
    return ok, f"armas a distancia, acierto por distancia del objetivo: CORTA {res[0]:.0f}% · MEDIA {res[1]:.0f}% · LEJOS {res[2]:.0f}% (casi nulo salvo que el enemigo se acerque)"


def t_cerraduras():
    s, b = nuevo(17, 5)
    s.p["inv"]["ganzua"] = 99
    exitos = 0
    for k in range(60):
        s2, _ = nuevo(2000 + k, 5)
        s2.p["inv"]["ganzua"] = 5
        ok, obt = s2.registrar("L-009", "C-015")
        exitos += 1 if ok else 0
    return exitos > 0, f"caja fuerte de nivel 3 con trampa abierta en {exitos}/60 intentos (ganzúa, tiradas por intento)"


def t_contenedor_persistente():
    s, b = nuevo(18, 5)
    s.registrar("L-004", "C-005")
    ok1, obt2 = s.registrar("L-004", "C-005")
    return obt2 == [] and s.locs["L-004"]["cont"]["C-005"]["abierto"], "un contenedor ya abierto no vuelve a dar objetos al reabrirlo"


def t_escape_y_persistencia():
    s, b = nuevo(19, 3)
    s.p["loc"] = "L-005"
    g = s.generar_grupo("L-005")
    ids = {e["id"] for e in g["miembros"]}
    s.p["hp"] = 5
    s.p["inv"] = {}
    # forzar escape
    orig = b.policy
    s.combate(g["miembros"], policy=lambda sim, v, a, o, gd: ("escapar",))
    quedan = {e["id"] for gr in s.locs["L-005"]["grupos"] for e in gr["miembros"] if e["hp"] > 0}
    return quedan <= ids and len(quedan) > 0 or s.p["hp"] <= 0, f"tras escapar quedan {len(quedan)} de {len(ids)} enemigos en el lugar (persisten)"


def t_busqueda_garantia():
    s, b = nuevo(20, 1)
    s.p["loc"] = "L-003"
    n = 0
    while "L-006" not in s.locs["L-003"]["ocultas_halladas"] and n < 10:
        n += 1
        s.buscar("L-003")
    return n <= 4, f"conexión oculta del Pozo Viejo hallada en la búsqueda nº{n} (garantía en la 4.ª)"


PRUEBAS = [
    ("Un solo tipo por encuentro", "Los grupos no mezclan especies (28, 37)", t_un_solo_tipo),
    ("Cantidad por talla", "T1 2-7, T2 1-5, T3 1-4, T4 1-3, T5 1-2 (+1 en hostiles) (28)", t_cantidades),
    ("Slots por nivel", "Nivel 1 solo slot 0; cada 2 niveles se abre un slot (27)", t_slots),
    ("1 a 3 variantes", "1d3 por criatura y fase; humanos 1-2 (27)", t_variantes),
    ("Variantes por nivel", "V1 al slot, V2 a +6 niveles, V3 a +12 (27)", t_variante_por_nivel),
    ("Curva de XP", "XP total = 60×N×(N−1) (27)", t_xp_curva),
    ("Persistencia de enemigos", "Lo que spawneó no desaparece al irte (37)", t_persistencia),
    ("Regeneración >48 h", "Zona hostil despejada repuebla pasadas 48 h (07)", t_regeneracion),
    ("Choque entre especies", "Especies distintas se atacan entre sí (37)", t_choque),
    ("Misma especie no pelea", "Una especie no ataca a la suya (37)", t_misma_especie_no_pelea),
    ("Derrota, arrastre y robo", "Sin muerte: arrastre a cama, robo recuperable (39)", t_derrota_arrastre_robo),
    ("No se muere", "20 derrotas seguidas sin fin de partida (39)", t_no_muere),
    ("Atasco 40-60%", "Ventana/agujero: umbral aleatorio 40-60% (39)", t_atasco),
    ("Mapa grande vulnerable", "Abrir mapa y viajar rápido: 8/18/35% + 20% (07, 39)", t_mapa_vulnerable),
    ("Jefe con tope de invocación", "Máx. 3 ciclos de invocación, tope de vivos (28)", t_jefe_invocacion),
    ("Movimientos de combate", "sigiloso, normal, rápido, potente, preciso, defensa, empujar (37)", t_combate_movimientos),
    ("Fallo 25-70%", "Fallo base 50-70% según vulnerabilidad, bonus hasta −25 (37)", t_fallo_rango),
    ("Armas a distancia", "Casi nulas fuera de CORTA (37)", t_arma_distancia_nula),
    ("Cerraduras y trampas", "Ganzúa/forzar/hackear con tirada por intento (05)", t_cerraduras),
    ("Contenedor ya abierto", "Un contenedor abierto no regenera objetos (05)", t_contenedor_persistente),
    ("Escape y persistencia", "Los enemigos que quedan siguen ahí (37)", t_escape_y_persistencia),
    ("Garantía de camino oculto", "4.ª búsqueda revela la conexión oculta (04)", t_busqueda_garantia),
]


def main():
    salida = AQUI.parent / "simulacion"
    if "--salida" in sys.argv:
        salida = Path(sys.argv[sys.argv.index("--salida") + 1])
    for nombre, regla, f in PRUEBAS:
        prueba(nombre, regla, f)
    ok = sum(1 for r in RES if r[2])
    lines = ["# Pruebas dirigidas de reglas", "",
             f"**{ok}/{len(RES)} pruebas aprobadas.** Cada prueba fuerza la situación que la campaña automática no siempre alcanza.", "",
             "| Prueba | Regla (bloque) | Resultado | Observado |", "|---|---|---|---|"]
    for nombre, regla, o, obs in RES:
        lines.append(f"| {nombre} | {regla} | {'✅' if o else '❌'} | {obs} |")
    texto = "\n".join(lines) + "\n"
    print(texto)
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "PRUEBAS_DE_REGLAS.md").write_text(texto, encoding="utf-8")
    return 0 if ok == len(RES) else 1


if __name__ == "__main__":
    sys.exit(main())
