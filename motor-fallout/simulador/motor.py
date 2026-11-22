"""Motor de reglas en codigo: aplica los bloques 03-39 sobre el mundo de mundo.py.

No es el juego para la IA (ese es el texto de los bloques). Es una implementacion de referencia
para PROBAR que las reglas cierran: combate por distancias, busqueda, contenedores, persistencia
de enemigos, niveles, derrota sin muerte, atasco, mapa vulnerable, comercio y misiones.
"""
import math
import random
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent))

import importlib  # noqa: E402
import os  # noqa: E402

mundo = importlib.import_module(os.environ.get("MUNDO", "mundo"))  # noqa: E402
import generar_bestiario as gb  # noqa: E402

NIVEL_MAX = 30
CLASE = {'S': 'segura', 'N': 'normal', 'H': 'hostil'}
# --- Tablas de reglas (bloques 27, 28, 37) ------------------------------------------------
TALLA = {1: dict(pv=20, dano=(3, 6), imp=50, rd=0, xp=8, grupo=(2, 7, (3, 5))),
         2: dict(pv=40, dano=(5, 10), imp=55, rd=0, xp=18, grupo=(1, 5, (2, 4))),
         3: dict(pv=80, dano=(8, 15), imp=58, rd=1, xp=40, grupo=(1, 4, (1, 3))),
         4: dict(pv=160, dano=(12, 22), imp=62, rd=3, xp=80, grupo=(1, 3, (1, 2))),
         5: dict(pv=300, dano=(18, 32), imp=66, rd=5, xp=160, grupo=(1, 2, (1, 1)))}
# Escalado por nivel del enemigo (calibrado con el simulador, ver bloque 27)
ESC_PV = 0.10
ESC_DANO = 0.085
VAR_MULT = {1: (1.0, 1.0, 1.0), 2: (1.4, 1.25, 1.5), 3: (1.9, 1.6, 2.2)}
# Fases (bloque 25): PV x, dano x
FASE_MULT = {1: (1.0, 1.0), 2: (1.0, 1.0), 3: (1.1, 1.0), 4: (1.2, 1.1), 5: (1.5, 1.3), 6: (1.3, 1.2),
             7: (1.1, 1.1), 8: (1.1, 1.0), 9: (1.0, 1.0), 10: (1.0, 1.0), 11: (0.9, 0.9), 12: (1.1, 1.1)}
FASES_LORE = [1, 3, 4, 5, 7]  # fases activas del lore del Salar (CONFIG_LORE)
XP_BASE = 60
DANO_NIVEL = 1.3  # dano del jugador por nivel (bloque 27)
# Equipo de humanos E0-E5 (bloque 26): multiplicadores de PV y dano, RD
EQUIPO_HUM = {0: (0.55, 0.6, 0), 1: (0.65, 0.7, 1), 2: (0.8, 0.85, 3), 3: (1.0, 1.0, 6), 4: (1.2, 1.2, 10), 5: (1.5, 1.5, 16)}
PROB_EQUIPO = [(4, (55, 35, 10, 0, 0, 0)), (8, (25, 40, 30, 5, 0, 0)), (12, (10, 25, 40, 22, 3, 0)),
               (18, (3, 12, 30, 38, 15, 2)), (24, (0, 5, 20, 35, 32, 8)), (30, (0, 2, 10, 28, 40, 20))]
  # xp_total(N) = XP_BASE * N * (N-1)  (bloque 27)


def xp_total(n):
    return XP_BASE * n * (n - 1)


def talla_n(txt):
    return int(txt.replace("T", ""))


class Sim:
    def __init__(self, semilla=1, detalle=False):
        self.rng = random.Random(semilla)
        self.semilla = semilla
        self.log = []
        self.detalle = detalle
        self.contadores = {}
        self.violaciones = []
        self.arreglos = []
        self._cargar_especies()
        self._tirar_variantes()
        self._iniciar_mundo()
        self._iniciar_jugador()

    # ----------------------------------------------------------------- carga
    def _cargar_especies(self):
        self.esp = {}
        for nombre in gb.ARCHIVOS_ESPECIES:
            for e in gb.leer_tabla(AQUI.parent / nombre):
                self.esp[e["id"]] = e
        for h in gb.leer_tabla(AQUI.parent / gb.ARCHIVO_HUMANOS, humanos=True):
            self.esp[h["id"]] = h
        # comandante y capataz usados por jefes
        self.esp.setdefault("U-20", dict(id="U-20", nombre="Comandante", talla="T3", slot=14, vars=["Común", "Veterano"], tema="humanos", comp=""))

    def _tirar_variantes(self):
        self.nvar = {}
        for sid, e in self.esp.items():
            maxv = 2 if sid.startswith("U-") else 3
            for f in range(1, 13):
                self.nvar[(sid, f)] = self.rng.randint(1, maxv)

    def _iniciar_mundo(self):
        self.locs = {}
        for lid, d in mundo.LOCS.items():
            self.locs[lid] = dict(
                explor=0, limpio_desde=None, grupos=[], visitada=False, descubierta=False, ult_visita=0, despejada=False,
                cont={c[0]: dict(tipo=c[1], cerr=c[2], trampa=c[3], items=list(c[4]), abierto=False,
                                 inspeccionado=False, cuñas=0) for c in d["cont"]},
                ocultas_halladas=set(), terminal_ok=False, term_fallos=0, term_bloq=0, recursos=3)
            for cid, st in self.locs[lid]["cont"].items():
                for it in list(st["items"]):
                    if it.startswith("cuñas"):
                        st["cuñas"] += int(it[5:])
                        st["items"].remove(it)
        self.reloj = 8 * 60  # minutos desde dia 1 00:00
        self.npc_estado = {nid: dict(rel=0, hablado=0) for nid in mundo.NPCS}
        self.next_id = 1
        self.kills_loc = {}
        self.kills_esp = {}
        self.stock = {}  # stock de comerciantes: se regenera cada 72 h

    def _iniciar_jugador(self):
        st = dict(mundo.PROTAGONISTA["stats"])
        self.p = dict(nombre=mundo.PROTAGONISTA["nombre"], nivel=1, xp=0, stats=st,
                      hp=0, arma=1, dur=70, armadura=0, cuñas=30,
                      inv={"venda": 3, "lata": 2, "agua": 2, "ganzua": 1}, loc=mundo.PROTAGONISTA["hogar"], hambre=10, sed=10, fatiga=0,
                      edad=mundo.PROTAGONISTA.get("edad", "adulto"), atascado=False,
                      comps=[], estados=set(), karma=0, sigilo=False)
        self.p["hp"] = self.hpmax()
        self.fl = dict(bando=None, purificador=False, llave_silo=False)
        self.quests = {q: "disponible" for q in mundo.QUESTS}
        self.qpaso = {q: 0 for q in mundo.QUESTS}
        self.hist_niv = []
        hogar = mundo.PROTAGONISTA["hogar"]
        self.locs[hogar]["descubierta"] = True
        for c in mundo.LOCS[hogar]["conn"]:
            self.locs[c]["descubierta"] = True
        self.contar("dias_max", 1)

    # ----------------------------------------------------------------- utilidades
    def contar(self, k, n=1):
        self.contadores[k] = self.contadores.get(k, 0) + n

    def dia(self):
        return self.reloj // 1440 + 1

    def hora(self):
        m = self.reloj % 1440
        return f"{m // 60:02d}:{m % 60:02d}"

    def say(self, texto, fuerte=True):
        if fuerte or self.detalle:
            self.log.append(f"d{self.dia()} {self.hora()} | {self.p['loc']} | {texto}")

    def nuevo_id(self, pref):
        n = self.next_id
        self.next_id += 1
        return f"{pref}-{n:03d}"

    def t(self, rng=None):
        return self.rng.random() * 100 if rng is None else self.rng.randint(*rng)

    def pct(self, x):
        return self.rng.random() * 100 < x

    def avanzar(self, minutos):
        antes = self.reloj
        self.reloj += minutos
        horas = minutos / 60.0
        p = self.p
        p["hambre"] = min(100, p["hambre"] + 4 * horas)
        p["sed"] = min(100, p["sed"] + 6 * horas)
        p["fatiga"] = min(100, p["fatiga"] + 3 * horas)
        if p["hambre"] >= 100 or p["sed"] >= 100:
            p["hp"] = max(1, p["hp"] - int(3 * horas))
        # regeneracion natural leve
        if p["hp"] < self.hpmax():
            p["hp"] = min(self.hpmax(), p["hp"] + int(self.hpmax() * 0.02 * horas) + (1 if minutos >= 10 else 0))
        # choque entre especies cada 2 h
        h0, h1 = antes // 120, self.reloj // 120
        for _ in range(h1 - h0):
            for lid, L in self.locs.items():
                self._choque(lid, L)
        # recuperacion de enemigos 10% por hora
        for L in self.locs.values():
            for g in L["grupos"]:
                for e in g["miembros"]:
                    if e["hp"] > 0 and e["hp"] < e["hpmax"] and not e.get("veneno"):
                        e["hp"] = min(e["hpmax"], e["hp"] + int(e["hpmax"] * 0.10 * horas))
        # regeneracion de poblacion hostil: >48 h despues de despejada y sin el jugador (bloque 07)
        for lid, L in self.locs.items():
            d = mundo.LOCS[lid]
            if d["clase"] == "H" and L.get("limpio_desde") is not None and lid != self.p["loc"]:
                if not L["grupos"] and self.reloj - L["limpio_desde"] > 48 * 60:
                    L["limpio_desde"] = None
                    L["despejada"] = False
                    self.contar("regeneraciones")
                    g = self.generar_grupo(lid)
                    self.say(f"{d['nombre']}: pasaron >48 h, la población se regenera ({g['miembros'][0]['nombre'] if g else '-'})", fuerte=False)
        # reposicion de stock cada 72 h
        if self.reloj // (72 * 60) != antes // (72 * 60):
            self.stock = {}

    def _choque(self, lid, L):
        vivos = [g for g in L["grupos"] if any(e["hp"] > 0 for e in g["miembros"])]
        especies = {g["especie"] for g in vivos}
        if len(vivos) < 2 or len(especies) < 2 or lid == self.p["loc"]:
            return
        a, b = self.rng.sample(vivos, 2)
        if a["especie"] == b["especie"]:
            return
        for x, y in ((a, b), (b, a)):
            if self.pct(50):
                vivos_x = [e for e in x["miembros"] if e["hp"] > 0]
                vivos_y = [e for e in y["miembros"] if e["hp"] > 0]
                if vivos_x and vivos_y:
                    dm = sum((e["dano"][0] + e["dano"][1]) / 2 for e in vivos_x) * 0.3
                    objetivo = self.rng.choice(vivos_y)
                    objetivo["hp"] -= int(dm)
        self.contar("choques_entre_especies")
        for g in (a, b):
            for e in g["miembros"]:
                if e["hp"] <= 0 and not e.get("muerto") and not e.get("cobrado"):
                    e["muerto"] = True
                    e["cobrado"] = True
                    self.contar("muertes_por_otra_criatura")
                    self.say(f"{e['nombre']} {e['id']} murió peleando con otra especie", fuerte=False)
        L["grupos"] = [g for g in L["grupos"] if any(e["hp"] > 0 for e in g["miembros"])]

    # ----------------------------------------------------------------- jugador
    def hpmax(self):
        return 90 + self.p["stats"]["RES"] * 10 + 5 * self.p["nivel"]

    def bonus_stat(self, s):
        return self.p["stats"][s] - 5

    def rd(self):
        return mundo.ARMADURAS[self.p["armadura"]]

    def defensa_pct(self):
        return 2 * self.rd()

    def dano_jugador(self, mult=1.0):
        lo, hi = mundo.ARMAS[self.p["arma"]][1:]
        base = self.rng.randint(lo, hi)
        dur = self.p["dur"]
        dm = 1.0 if dur >= 50 else (0.85 if dur >= 25 else (0.7 if dur > 0 else 0.4))
        return max(1, int((base * dm * mult) + self.bonus_stat("FUE") + math.floor(self.p["nivel"] * DANO_NIVEL)))

    def dano_nominal(self):
        lo, hi = mundo.ARMAS[self.p["arma"]][1:]
        return (lo + hi) / 2 + self.bonus_stat("FUE") + math.floor(self.p["nivel"] * DANO_NIVEL)

    def ganar_xp(self, xp, motivo=""):
        p = self.p
        if p["nivel"] >= NIVEL_MAX:
            self.contar("xp_post_tope", int(xp))
            return
        p["xp"] += int(xp)
        self.contar("xp_total", int(xp))
        while p["nivel"] < NIVEL_MAX and p["xp"] >= xp_total(p["nivel"] + 1):
            p["nivel"] += 1
            p["hp"] = self.hpmax()
            self.hist_niv.append((p["nivel"], self.dia(), int(self.contadores.get("kills", 0))))
            self.say(f"SUBE A NIVEL {p['nivel']} (PV máx {self.hpmax()}, daño nominal {self.dano_nominal():.0f})")

    # ----------------------------------------------------------------- enemigos
    def slot_fase(self, e, fase):
        return min(gb.SLOT_MAX, e["slot"] + gb.OFFSET_SLOT.get(fase, 0))

    def elegibles(self, pool_nombre, fase=1):
        slot_max = self.p["nivel"] // 2
        out = []
        for sid in mundo.POOLS.get(pool_nombre, []):
            e = self.esp.get(sid)
            if not e:
                continue
            s = self.slot_fase(e, fase) if not sid.startswith("U-") else e["slot"]
            if s <= slot_max:
                out.append((sid, s))
        return out, slot_max

    def elegir_fase(self):
        n = self.p["nivel"]
        pesos = {1: 70, 3: 0, 4: 0, 5: 0, 7: 0}
        if n >= 4:
            pesos.update({3: 15})
        if n >= 6:
            pesos.update({4: 12})
        if n >= 10:
            pesos.update({5: 8, 7: 6})
        pesos = {k: v for k, v in pesos.items() if v and k in FASES_LORE}
        return self.rng.choices(list(pesos), weights=list(pesos.values()))[0]

    def nivel_enemigo(self, lid):
        d = mundo.LOCS[lid]
        if d["clase"] == "H":
            return max(1, min(NIVEL_MAX, max(d["nivel"], self.p["nivel"] - 2)))
        return max(1, min(d["nivel"] + 1, self.p["nivel"] + 1))

    def variante_para(self, sid, fase, nivel_jug):
        e = self.esp[sid]
        n = self.nvar[(sid, fase)]
        base = max(1, 2 * self.slot_fase(e, fase)) if not sid.startswith("U-") else max(1, 2 * e["slot"])
        activas = [i + 1 for i in range(n) if base + 6 * i <= nivel_jug]
        if not activas:
            activas = [1]
        # 50% la mas nueva, 50% al azar
        return activas[-1] if self.pct(50) else self.rng.choice(activas)

    def crear_enemigo(self, sid, fase, nl, loc, jefe=None, cantidad_mod=0):
        e = self.esp[sid]
        talla = max(talla_n(e["talla"]), gb.TALLA_MIN.get(fase, 1)) if not sid.startswith("U-") else talla_n(e["talla"])
        T = TALLA[min(5, talla)]
        var = self.variante_para(sid, fase, self.p["nivel"])
        vm = VAR_MULT[var]
        fm = FASE_MULT.get(fase, (1.0, 1.0))
        pv = T["pv"] * (1 + ESC_PV * (nl - 1)) * vm[0] * fm[0]
        d0, d1 = T["dano"]
        mul = (1 + ESC_DANO * (nl - 1)) * vm[1] * fm[1]
        ent = dict(id=self.nuevo_id("ENE"), sid=sid, especie=sid, fase=fase, nombre=gb.NOMBRE_FASE.get(fase, "{E}").format(E=e["nombre"]),
                   talla=talla, var=var, nivel=nl, hp=int(pv), hpmax=int(pv), dano=(max(1, int(d0 * mul)), max(2, int(d1 * mul))),
                   imp=T["imp"], rd=T["rd"], dist=2, loc=loc, xp=int(T["xp"] * vm[2]), loot_cuñas=self.rng.randint(0, 3 + talla * 2))
        if sid.startswith("U-") and not jefe:
            tier = self.tirar_equipo()
            mp, md, rdh = EQUIPO_HUM[tier]
            ent["hp"] = ent["hpmax"] = max(1, int(ent["hpmax"] * mp))
            ent["dano"] = (max(1, int(ent["dano"][0] * md)), max(2, int(ent["dano"][1] * md)))
            ent["rd"] = rdh
            ent["tier"] = tier
        self.contar('enemigos_creados')
        if jefe:
            ent.update(nombre=jefe["nombre"], hp=jefe["pv"], hpmax=jefe["pv"], dano=jefe["dano"], xp=300 + jefe["nivel"] * 40,
                       jefe=True, talla=talla_n(jefe["talla"]), rd=3 if jefe["nivel"] < 15 else 6)
        return ent

    def tirar_equipo(self):
        n = self.p["nivel"]
        for tope, pesos in PROB_EQUIPO:
            if n <= tope:
                return self.rng.choices(range(6), weights=pesos)[0]
        return 5

    def generar_grupo(self, lid, forzar_especies=None, jefe=None):
        d = mundo.LOCS[lid]
        L = self.locs[lid]
        fase = 1
        if forzar_especies:
            sid = self.rng.choice(forzar_especies)
        else:
            fase = self.elegir_fase()
            elig, slot_max = self.elegibles(d["pool"], fase)
            if not elig:
                fase = 1
                elig, slot_max = self.elegibles(d["pool"], 1)
            if not elig:
                return None
            pesos = []
            for sid, s in elig:
                w = 2.0 if s >= slot_max - 1 and slot_max > 0 else 1.0
                if s == 0 and self.p["nivel"] >= 10:
                    w = 0.5
                pesos.append(w)
            sid = self.rng.choices([x[0] for x in elig], weights=pesos)[0]
        e = self.esp[sid]
        talla = talla_n(e["talla"]) if sid.startswith("U-") else max(talla_n(e["talla"]), gb.TALLA_MIN.get(fase, 1))
        lo, hi, hab = TALLA[min(5, talla)]["grupo"]
        cant = self.rng.randint(hab[0], hab[1])
        if d["clase"] == "H":
            cant = min(7, cant + 1)
        cant = max(lo, min(hi, cant))
        nl = self.nivel_enemigo(lid)
        miembros = [self.crear_enemigo(sid, fase, nl, lid) for _ in range(cant)]
        g = dict(especie=sid, miembros=miembros, botin_robado=[], id=self.nuevo_id("G"))
        L["grupos"].append(g)
        self.contar("grupos_creados")
        return g

    def generar_jefe(self, lid, clave):
        j = mundo.JEFES[clave]
        e = self.crear_enemigo(j["especie"], 1, j["nivel"], lid, jefe=j)
        g = dict(especie="JEFE:" + clave, miembros=[e], botin_robado=[], id=self.nuevo_id("G"))
        e.update(sub_sid=j["sub"], sub_max=j["sub_max"], grupo=g["id"], clave=clave)
        self.locs[lid]["grupos"].append(g)
        self.fl["jefe_" + clave] = "vivo"
        return g

    def vivos(self, lid):
        return [e for g in self.locs[lid]["grupos"] for e in g["miembros"] if e["hp"] > 0]

    # ----------------------------------------------------------------- combate (bloque 37)
    def vulnerabilidad(self, enemigos, extra=0):
        p = self.p
        vivos = [e for e in enemigos if e["hp"] > 0]
        if not vivos:
            return 0
        mind = min(e["dist"] for e in vivos)
        v = {0: 40, 1: 20, 2: 5}[mind]
        cortos = sum(1 for e in vivos if e["dist"] == 0)
        v += min(30, 10 * max(0, cortos - 1))
        if p["hp"] < self.hpmax() * 0.5:
            v += 15
        if p["estados"] & {"herido", "cansado", "aturdido"}:
            v += 10
        if self.p["armadura"] >= 4:
            v -= 10
        if p["comps"] and cortos:
            v -= 10
        if p.get("atascado"):
            v += 25  # bloque 49: vulnerabilidad maxima mientras estas atascado
        return max(0, min(100, v + extra))

    def fallo(self, enemigos, mod=0, extra_v=0):
        v = self.vulnerabilidad(enemigos, extra_v)
        base = 50 + 0.2 * v
        bonus = min(25, 2 * self.bonus_stat("FUE") + self.p["nivel"] // 2 + (self.p["arma"] - 2) * 3)
        return max(25, min(70, base - bonus + mod)), v

    def fallo_ataque(self, vivos, mod, objetivo, a_distancia):
        f, _ = self.fallo(vivos, mod)
        if a_distancia:
            f = min(95, f + {0: 0, 1: 25, 2: 40}[objetivo["dist"]])  # bloque 37: casi nulas fuera de CORTA
        return f

    def combate(self, enemigos, emboscada_enemiga=False, sorpresa=False, policy=None, ctx="", atascado=False):
        """Devuelve 'victoria', 'derrota' o 'escape'. Mutan los enemigos (persisten)."""
        p = self.p
        for e in enemigos:
            e["dist"] = 2 if e["dist"] not in (0, 1, 2) else e["dist"]
        turno, rondas = 0, 0
        vivos0 = [e for e in enemigos if e["hp"] > 0]
        nombres = f"{len(vivos0)}× {vivos0[0]['nombre']}" if vivos0 else "-"
        hp_ini = p["hp"]
        self.say(f"COMBATE vs {nombres} (nv{vivos0[0]['nivel']}, var V{vivos0[0]['var']}, PV c/u {vivos0[0]['hpmax']}) "
                 f"{'[emboscada enemiga]' if emboscada_enemiga else ''}{'[sorpresa]' if sorpresa else ''}")
        p["atascado"] = atascado
        comp_hp = {c: 30 + 6 * p["nivel"] for c in p["comps"]}
        oculto = sorpresa
        while True:
            turno += 1
            vivos = [e for e in enemigos if e["hp"] > 0]
            if not vivos:
                break
            acciones = 3
            if p.get("atascado") and self.pct(40 + 4 * max(p["stats"]["FUE"], p["stats"]["AGI"])):
                p["atascado"] = False
                self.contar("liberado_en_combate")
            if emboscada_enemiga and turno == 1:
                acciones = 0
            guardia = None
            potente_hecho = False
            while acciones > 0 and vivos:
                vivos = [e for e in enemigos if e["hp"] > 0]
                if not vivos:
                    break
                mov = policy(self, vivos, acciones, oculto, guardia) if policy else ("normal",)
                tipo = mov[0]
                if tipo == "escapar" and p.get("atascado"):
                    acciones -= 1  # atascado: no se puede escapar (bloque 49)
                    continue
                if tipo == "escapar":
                    ex = 60 + 3 * p["stats"]["AGI"] - 15 * sum(1 for e in vivos if e["dist"] == 0)
                    ok = self.pct(max(10, min(90, ex)))
                    self.contar("escapes_intentados")
                    if ok:
                        self.say(f"ESCAPÓ del combate (los enemigos quedan: {len(vivos)} persistentes)")
                        self.contar("escapes")
                        self._fin_combate(enemigos, turno)
                        return "escape"
                    acciones = 0
                    continue
                if tipo == "vendas":
                    if p["inv"].get("venda_reforzada", 0):
                        p["inv"]["venda_reforzada"] -= 1
                        p["hp"] = min(self.hpmax(), p["hp"] + 20)
                    elif p["inv"].get("medicina", 0):
                        p["inv"]["medicina"] -= 1
                        p["hp"] = min(self.hpmax(), p["hp"] + 30 + p["nivel"])
                    elif p["inv"].get("venda", 0):
                        p["inv"]["venda"] -= 1
                        p["hp"] = min(self.hpmax(), p["hp"] + 10)
                    acciones -= 1
                    continue
                if tipo == "esperar":
                    acciones = 0
                    continue
                if tipo == "defensa":
                    cerca = [e for e in vivos if e["dist"] == 0]
                    f, _ = self.fallo(vivos)
                    guardia = 0.75 if self.pct(100 - f) else 0.25
                    if not cerca:
                        for e in vivos:
                            pass
                    acciones -= 1
                    continue
                if tipo == "acercar":
                    for e in vivos:
                        pass
                    # el jugador avanza hacia el mas cercano: baja 1 la distancia de todos
                    for e in vivos:
                        e["dist"] = max(0, e["dist"] - 1)
                    acciones -= 1
                    continue
                if tipo == "empujar":
                    objetivo = min(vivos, key=lambda e: e["dist"])
                    if objetivo["dist"] > 0:
                        acciones -= 1
                        continue
                    f, _ = self.fallo(vivos)
                    if self.pct(100 - f):
                        objetivo["dist"] = min(2, objetivo["dist"] + 1)
                        if objetivo["talla"] <= 2:
                            objetivo["aturdido"] = 1
                    acciones -= 1
                    continue
                # ataques cuerpo a cuerpo: objetivo indicado o el mas cercano
                objetivo = mov[1] if len(mov) > 1 and mov[1] in vivos else min(vivos, key=lambda e: (e["dist"], e["hp"]))
                costo = 2 if tipo == "potente" else 1
                if acciones < costo:
                    acciones = 0
                    continue
                a_distancia = bool(p.get("arma_distancia"))
                if objetivo["dist"] > 0 and not a_distancia:
                    # no se puede golpear cuerpo a cuerpo: se acerca
                    for e in vivos:
                        e["dist"] = max(0, e["dist"] - 1)
                    acciones -= 1
                    continue
                mods = {"sigiloso": -20, "normal": 0, "rapido": -5, "potente": 5, "preciso": 5}
                mult = {"sigiloso": 3.0, "normal": 1.0, "rapido": 0.7, "potente": 2.0, "preciso": 1.0}[tipo]
                if tipo == "sigiloso" and not oculto:
                    tipo, mult = "normal", 1.0
                f = self.fallo_ataque(vivos, mods[tipo], objetivo, a_distancia)
                if a_distancia:
                    self.contar("ataques_a_distancia")
                self.contar("ataques")
                if self.pct(100 - f):
                    dm = self.dano_jugador(mult)
                    crit = self.rng.randint(1, 100) <= 5 + p["stats"]["SUE"] // 2 + (15 if tipo == "preciso" else 0)
                    if crit:
                        dm *= 2
                        self.contar("criticos")
                    dm = max(1, dm - objetivo["rd"])
                    objetivo["hp"] -= dm
                    self.contar("aciertos")
                    self.p["dur"] = max(0, self.p["dur"] - 0.3)
                    if tipo == "potente" and self.pct(20):
                        objetivo["aturdido"] = 1
                    if objetivo["hp"] <= 0:
                        objetivo["muerto"] = True
                else:
                    self.contar("fallos")
                if tipo == "rapido":
                    objetivo["dist"] = min(2, objetivo["dist"] + 1)
                    self.p.setdefault("_retro", 0)
                oculto = False
                acciones -= costo
                if tipo == "potente":
                    potente_hecho = True
            # compañeros atacan
            vivos = [e for e in enemigos if e["hp"] > 0]
            for c in p["comps"]:
                if vivos and comp_hp.get(c, 0) > 0:
                    t_ = self.rng.choice(vivos)
                    t_["hp"] -= max(1, 3 + p["nivel"] // 2 - t_["rd"])
            vivos = [e for e in enemigos if e["hp"] > 0]
            # enemigos actuan
            for e in vivos:
                if e.get("aturdido"):
                    e["aturdido"] = 0
                    continue
                if e["dist"] > 0:
                    e["dist"] -= 1
                    continue
                if comp_hp and self.pct(25):
                    c = self.rng.choice(list(comp_hp))
                    if comp_hp[c] > 0:
                        comp_hp[c] -= self.rng.randint(*e["dano"])
                        continue
                if self.pct(max(10, min(90, e["imp"] - self.defensa_pct()))):
                    dm = self.rng.randint(*e["dano"]) - self.rd()
                    dm = max(1, dm)
                    if guardia is not None:
                        dm = max(1, int(dm * (1 - guardia)))
                    p["hp"] -= dm
                    self.contar("danos_recibidos", dm)
            # jefes invocan subordinados (bloque 28: max 3 por ciclo, tope vivos, cooldown 3 rondas)
            jefes = [e for e in enemigos if e.get("jefe") and e["hp"] > 0]
            if jefes and rondas % 3 == 2 and jefes[0].get("ciclos", 0) < 3:
                j = jefes[0]
                subs = [e for e in enemigos if e.get("sub") and e["hp"] > 0]
                tope = j["sub_max"]
                faltan = max(0, min(3, tope - len(subs)))
                for _ in range(faltan):
                    n = self.crear_enemigo(j["sub_sid"], 1, max(1, j["nivel"] - 1), j["loc"])
                    n["sub"] = True
                    n["dist"] = 1
                    if all(x is not n for x in enemigos):
                        enemigos.append(n)
                    for g in self.locs[j["loc"]]["grupos"]:
                        if g["id"] == j["grupo"] and all(x is not n for x in g["miembros"]):
                            g["miembros"].append(n)
                if faltan:
                    j["ciclos"] = j.get("ciclos", 0) + 1
                    self.contar("invocaciones")
            rondas += 1
            self.avanzar(1)
            if p["hp"] <= 0:
                self.contar("combates_perdidos")
                self._fin_combate(enemigos, rondas)
                return "derrota"
            if rondas > 400:
                self.violaciones.append("combate sin fin (>400 rondas)")
                self._fin_combate(enemigos, rondas)
                return "escape"
        # victoria
        self.contar("combates_ganados")
        self.contar("rondas_total", rondas)
        self._fin_combate(enemigos, rondas)
        self.say(f"VICTORIA en {rondas} rondas (PV {hp_ini}→{p['hp']}/{self.hpmax()})")
        return "victoria"

    def _cobrar(self, enemigos):
        p = self.p
        for e in enemigos:
            if e["hp"] <= 0 and not e.get("cobrado"):
                e["cobrado"] = True
                ratio = max(0.5, min(2.0, e["nivel"] / p["nivel"]))
                self.ganar_xp(e["xp"] * ratio)
                self.contar("kills")
                self.kills_loc[e["loc"]] = self.kills_loc.get(e["loc"], 0) + 1
                self.kills_esp[e["sid"]] = self.kills_esp.get(e["sid"], 0) + 1
                p["cuñas"] += e["loot_cuñas"]
                sid = e["sid"]
                if sid.startswith("H-") and self.pct(50):
                    p["inv"]["carne"] = p["inv"].get("carne", 0) + 1
                if sid[0] in "MPSI" and self.pct(40):
                    p["inv"]["recurso_bio"] = p["inv"].get("recurso_bio", 0) + 1
                if sid.startswith("U-") and self.pct(35):
                    p["inv"]["venda"] = p["inv"].get("venda", 0) + 1
                if sid.startswith("X-") and self.pct(40):
                    it = self.rng.choice(["circuito", "piezas", "chatarra"])
                    p["inv"][it] = p["inv"].get(it, 0) + 1

    def _fin_combate(self, enemigos, rondas):
        self._cobrar(enemigos)
        for lid, g_loc in self.locs.items():
            nuevos = []
            for g in g_loc["grupos"]:
                if all(e["hp"] <= 0 for e in g["miembros"]):
                    if g["botin_robado"]:
                        self.recuperar_robo(g)
                    continue
                nuevos.append(g)
            g_loc["grupos"] = nuevos
        for lid, g_loc in self.locs.items():
            if mundo.LOCS[lid]["clase"] == "H" and not g_loc["grupos"] and g_loc["visitada"]:
                if not g_loc["despejada"]:
                    g_loc["limpio_desde"] = self.reloj
                g_loc["despejada"] = True

    # ----------------------------------------------------------------- derrota (bloque 39)
    def derrota(self, lid):
        p = self.p
        self.contar("derrotas")
        grupo = None
        for g in self.locs[lid]["grupos"]:
            if any(e["hp"] > 0 for e in g["miembros"]):
                grupo = g
                break
        robo = []
        manipula = grupo and (grupo["especie"].startswith("U-") or grupo["especie"].startswith("FA-18"))
        if grupo and self.pct(60 if manipula else 0):
            perdida = int(p["cuñas"] * self.rng.uniform(0.10, 0.30))
            p["cuñas"] -= perdida
            robo.append(("cuñas", perdida))
            for _ in range(self.rng.randint(0, 2)):
                its = [k for k, v in p["inv"].items() if v > 0 and mundo.OBJETOS.get(k, ("", "mision", 0))[1] in ("consumible", "recurso", "general")]
                if its:
                    k = self.rng.choice(its)
                    p["inv"][k] -= 1
                    robo.append((k, 1))
            grupo["botin_robado"] = robo
            self.contar("robos_sufridos")
        camas = [l for l, d in mundo.LOCS.items() if d["cama"] and self.locs[l]["descubierta"]]
        dest = min(camas, key=lambda l: self.distancia(lid, l))
        mins = 20 + 20 * self.distancia(lid, dest)
        pasos = mins // 30
        for _ in range(pasos):
            if self.pct(20):
                perd = int(p["cuñas"] * self.rng.uniform(0.05, 0.10))
                p["cuñas"] -= perd
                self.contar("robos_en_arrastre")
                if grupo is not None:
                    grupo["botin_robado"] = grupo["botin_robado"] + [("cuñas", perd)]
        self.avanzar(mins)
        p["loc"] = dest
        p["hp"] = max(1, int(self.hpmax() * 0.25))
        p["estados"] |= {"herido", "cansado"}
        self.say(f"DERROTADO en {mundo.LOCS[lid]['nombre']}: arrastre a {mundo.LOCS[dest]['nombre']} ({mins} min), robo {robo or 'ninguno'}")
        self.visitar(dest)

    def distancia(self, a, b):
        from collections import deque
        if a == b:
            return 0
        vistos, cola = {a}, deque([(a, 0)])
        while cola:
            x, d = cola.popleft()
            for y in mundo.LOCS[x]["conn"] + [k for k, v in mundo.LOCS.items() if x in v["conn"]]:
                if y not in vistos:
                    if y == b:
                        return d + 1
                    vistos.add(y)
                    cola.append((y, d + 1))
        return 9

    def recuperar_robo(self, grupo):
        for k, n in grupo["botin_robado"]:
            if k == "cuñas":
                self.p["cuñas"] += n
            else:
                self.p["inv"][k] = self.p["inv"].get(k, 0) + n
        if grupo["botin_robado"]:
            self.contar("robos_recuperados")
            self.say(f"RECUPERA lo robado: {grupo['botin_robado']}")
        grupo["botin_robado"] = []

    # ----------------------------------------------------------------- mapa y viaje (bloque 07)
    def vecinos(self, lid):
        d = mundo.LOCS[lid]
        out = [c for c in d["conn"]]
        for k, v in mundo.LOCS.items():
            if lid in v["conn"] and k not in out:
                out.append(k)
        for to, _ in d.get("oculta", []):
            if to in self.locs[lid]["ocultas_halladas"]:
                out.append(to)
        for k, v in mundo.LOCS.items():
            for to, _ in v.get("oculta", []):
                if to == lid and k in self.locs[lid]["ocultas_halladas"]:
                    pass
        # oculta inversa: si L-006 fue hallada desde L-003, tambien se vuelve de L-006 a L-003
        for k, v in mundo.LOCS.items():
            for to, _ in v.get("oculta", []):
                if k == lid:
                    continue
                if to == lid and to in self.locs[k]["ocultas_halladas"] and k not in out:
                    out.append(k)
        return out

    def puede_entrar(self, lid):
        d = mundo.LOCS[lid]
        req = d.get("bloqueada")
        if not req:
            return True
        r = req[0]
        return bool(self.p["inv"].get(r, 0) or self.fl.get(r))

    def visitar(self, lid, primera_vez_log=True):
        L = self.locs[lid]
        d = mundo.LOCS[lid]
        primera = not L["visitada"]
        L["visitada"] = True
        L["descubierta"] = True
        L["ult_visita"] = self.reloj
        for v in self.vecinos(lid):
            if not self.locs[v]["descubierta"]:
                self.locs[v]["descubierta"] = True
                self.contar("ubicaciones_descubiertas")
                self.say(f"detecta/descubre: {mundo.LOCS[v]['nombre']}", fuerte=False)
        if primera:
            self.say(f"LLEGA por primera vez a {d['nombre']} [{CLASE[d['clase']]}]")
            if d["clase"] == "H" and not L["grupos"]:
                self.generar_grupo(lid)
                if self.pct(30):
                    self.generar_grupo(lid)
        else:
            if d["clase"] == "H" and not L["grupos"] and not L["despejada"]:
                self.generar_grupo(lid)
        # encuentro de llegada en zonas normales
        if d["clase"] == "N" and self.pct(20) and d["pool"] != "civil" and len(self.vivos(lid)) < 7:
            self.generar_grupo(lid)
        if d["clase"] == "S" and self.pct(3) and d["pool"] != "civil":
            pass

    def viajar(self, destino, rapido=False):
        """Un tramo (conexion) o viaje rapido (varios). Devuelve True si llego."""
        p = self.p
        origen = p["loc"]
        if not self.puede_entrar(destino):
            return False
        ruta = self.ruta(origen, destino)
        if not ruta:
            return False
        if rapido and len(ruta) >= 3:
            self.contar("viajes_rapidos")
            clase = mundo.LOCS[origen]["clase"]
            prob = {"S": 8, "N": 18, "H": 35}[clase] + 20
            if self.pct(prob):
                self.contar("emboscadas_mapa")
                self.say(f"MAPA GRANDE: viaje rápido interrumpido (vulnerable, {prob}%)")
                lid_i = ruta[len(ruta) // 2]
                p["loc"] = lid_i
                self.visitar(lid_i)
                g = self.generar_grupo(lid_i)
                if g:
                    res = self.combate(g["miembros"], emboscada_enemiga=True, policy=self.policy, ctx="mapa")
                    if res == "derrota":
                        self.derrota(lid_i)
                        return False
                    if res == "escape":
                        return False
                ruta = self.ruta(p["loc"], destino) or []
        for paso in ruta:
            if not self.puede_entrar(paso):
                self.say(f"ruta bloqueada hacia {mundo.LOCS[paso]['nombre']}")
                return False
            prev = p["loc"]
            Dp, Do = mundo.LOCS[paso], mundo.LOCS[prev]
            interno = bool(Dp.get("ubicacion")) and Dp.get("ubicacion") == Do.get("ubicacion")
            if Dp.get("tipo") == "edificio" or Do.get("tipo") == "edificio":
                mins = self.rng.randint(1, 3)
                self.contar("cruces_de_umbral")
                if not self._umbral(prev, paso):
                    return False
                if p["loc"] != prev:   # una derrota durante el cruce nos movio
                    return False
            elif interno:
                mins = self.rng.randint(3, 8)       # de cuadra a cuadra (47)
                self.contar("movimientos_de_cuadra")
            else:
                mins = self.rng.randint(20, 60)
            self.avanzar(mins)
            # evento en ruta (entre ubicaciones) o 5% en cuadras hostiles
            clase = mundo.LOCS[paso]["clase"]
            prob_ev = (5 if clase == "H" else 0) if (interno or Dp.get("tipo") == "edificio") else 10 + (10 if clase != "S" else 0)
            if mundo.LOCS[paso]["pool"] != "civil" and prob_ev and self.pct(prob_ev):
                lid_t = p["loc"]
                g = self.generar_grupo(paso)
                if g and clase != "S":
                    p["loc"] = paso
                    self.say(f"encuentro en ruta hacia {mundo.LOCS[paso]['nombre']}", fuerte=False)
                    res = self.combate(g["miembros"], policy=self.policy, sorpresa=self.pct(30))
                    if res == "derrota":
                        self.derrota(paso)
                        return False
                    if res == "escape":
                        p["loc"] = paso
                        self.visitar(paso)
                        return False
            p["loc"] = paso
            self.visitar(paso)
            self.contar("tramos")
        return True

    def camino_real(self, a, b):
        """Camino por conexiones visibles/halladas aunque el destino aun no este descubierto (exploracion)."""
        from collections import deque
        if a == b:
            return []
        prev, cola, vistos = {}, deque([a]), {a}
        while cola:
            x = cola.popleft()
            for y in self.vecinos(x):
                if y not in vistos:
                    vistos.add(y)
                    prev[y] = x
                    if y == b:
                        out, c = [], b
                        while c != a:
                            out.append(c)
                            c = prev[c]
                        return list(reversed(out))
                    cola.append(y)
        return None

    def ruta(self, a, b):
        from collections import deque
        if a == b:
            return []
        prev, cola, vistos = {}, deque([a]), {a}
        while cola:
            x = cola.popleft()
            for y in self.vecinos(x):
                if y not in vistos and self.locs[y]["descubierta"]:
                    vistos.add(y)
                    prev[y] = x
                    if y == b:
                        out, c = [], b
                        while c != a:
                            out.append(c)
                            c = prev[c]
                        return list(reversed(out))
                    cola.append(y)
        return None

    # ----------------------------------------------------------------- busqueda y contenedores (bloques 04, 05)
    POR_EXPLOR = {0: (55, 25), 1: (35, 30), 2: (20, 35), 3: (10, 30), 4: (5, 15)}

    def buscar(self, lid):
        """BUSCAR general (no registra puntos concretos). Devuelve texto del hallazgo."""
        L, d, p = self.locs[lid], mundo.LOCS[lid], self.p
        ex = min(4, L["explor"])
        rel, sec = self.POR_EXPLOR[ex]
        rel += max(0, p["stats"]["PER"] - 5) + 0.5 * p["nivel"]
        L["explor"] = min(5, L["explor"] + 1)
        self.avanzar(self.rng.randint(10, 30))
        self.contar("busquedas")
        r = self.rng.random() * 100
        res = "nada"
        if r < rel:
            cat = self.rng.choices(["objeto", "recurso", "conexion", "ubicacion", "evento", "documento"],
                                   weights=[30, 25, 12, 8, 10, 15])[0]
            if cat == "conexion" or cat == "ubicacion":
                oc = [to for to, _ in d.get("oculta", []) if to not in L["ocultas_halladas"]]
                if oc:
                    L["ocultas_halladas"].add(oc[0])
                    self.locs[oc[0]]["descubierta"] = True
                    self.contar("conexiones_ocultas")
                    res = f"CONEXIÓN OCULTA → {mundo.LOCS[oc[0]]['nombre']}"
                else:
                    cat = "objeto"
            if cat == "objeto":
                it = self.rng.choice(["chatarra", "venda", "lata", "agua", "circuito", "piezas"])
                p["inv"][it] = p["inv"].get(it, 0) + 1
                res = f"encuentra {mundo.OBJETOS[it][0]}"
            elif cat == "recurso":
                p["inv"]["chatarra"] = p["inv"].get("chatarra", 0) + 2
                if d["bioma"] in ("laguna", "cueva"):
                    p["inv"]["recurso_bio"] = p["inv"].get("recurso_bio", 0) + 1
                res = "recurso"
            elif cat == "documento":
                res = "documento sin mayor importancia"
            elif cat == "evento":
                res = "evento menor"
        elif r < rel + sec:
            p["inv"]["chatarra"] = p["inv"].get("chatarra", 0) + 1
            res = "chatarra"
        # conexion oculta: tirada independiente 12% y garantia desde la 4.ª busqueda (bloque 04, "garantia de camino")
        oc = [to for to, _ in d.get("oculta", []) if to not in L["ocultas_halladas"]]
        if oc and (L["explor"] >= 4 or self.pct(12)):
            L["ocultas_halladas"].add(oc[0])
            self.locs[oc[0]]["descubierta"] = True
            self.contar("conexiones_ocultas")
            res += f" + CONEXIÓN OCULTA → {mundo.LOCS[oc[0]]['nombre']}"
        # peligro (independiente)
        peligro = {"S": 3, "N": 10, "H": 30}[d["clase"]]
        if d["pool"] != "civil" and self.pct(peligro):
            g = self.generar_grupo(lid)
            if g:
                res += " + PELIGRO: aparece un grupo"
        self.say(f"BUSCAR (explor {ex}→{L['explor']}): {res}", fuerte=False)
        return res

    def registrar(self, lid, cid, via="abrir"):
        """Abrir un contenedor concreto (REGISTRAR). Devuelve (ok, items_obtenidos)."""
        L, p = self.locs[lid], self.p
        c = L["cont"][cid]
        if c["abierto"]:
            return True, []
        cerr = c["cerr"]
        if cerr > 0:
            intentos = 0
            while True:
                intentos += 1
                if intentos > 6:
                    return False, []
                if cerr == 5 and not p["inv"].get("llave_torre", 0):
                    return False, []
                if p["inv"].get("ganzua", 0) > 0:
                    pc = 70 - 12 * cerr + p["stats"]["AGI"] * 3 + p["nivel"]
                    metodo = "ganzúa"
                else:
                    pc = 60 - 10 * cerr + p["stats"]["FUE"] * 3 + p["nivel"]
                    metodo = "forzar"
                if cerr >= 3 and "terminal" in str(c["tipo"]):
                    pc = 70 - 12 * cerr + p["stats"]["INT"] * 3 + p["nivel"]
                    metodo = "hackear"
                pc = max(5, min(95, pc))
                self.avanzar(self.rng.randint(3, 10))
                tir = self.rng.randint(1, 100)
                if tir <= pc:
                    self.say(f"{cid} {c['tipo']}: {metodo} ({tir}≤{int(pc)}) ÉXITO", fuerte=False)
                    break
                if metodo == "ganzúa" and tir >= 90:
                    p["inv"]["ganzua"] -= 1
                    self.contar("ganzuas_rotas")
        if c["trampa"] and self.pct(40):
            dm = 8 + 2 * self.p["nivel"]
            p["hp"] = max(1, p["hp"] - dm)
            self.contar("trampas_activadas")
            self.say(f"{cid}: TRAMPA activada (−{dm} PV)", fuerte=False)
        c["abierto"] = True
        c["inspeccionado"] = True
        self.avanzar(2)
        obt = []
        for it in c["items"]:
            if it.startswith("armadura_e"):
                tier = int(it[-1])
                if tier > p["armadura"]:
                    p["armadura"] = tier
                    obt.append(it)
                continue
            if it.startswith("arma_t"):
                tier = int(it[-1])
                if tier > p["arma"]:
                    p["arma"] = tier
                    p["dur"] = 100
                obt.append(it)
                continue
            p["inv"][it] = p["inv"].get(it, 0) + 1
            obt.append(it)
        if c["cuñas"]:
            p["cuñas"] += c["cuñas"]
            obt.append(f"cuñas{c['cuñas']}")
        c["items"] = []
        c["cuñas"] = 0
        self.contar("contenedores_abiertos")
        self.say(f"REGISTRA {cid} ({c['tipo']}): {obt or 'vacío'}")
        return True, obt

    def terminal(self, lid, dificultad=2):
        L, p = self.locs[lid], self.p
        if L["terminal_ok"]:
            return True
        if L["term_bloq"] > self.reloj:
            return False
        for _ in range(3):
            pc = max(5, min(95, 70 - 12 * dificultad + p["stats"]["INT"] * 3 + p["nivel"]))
            self.avanzar(self.rng.randint(5, 15))
            if self.rng.randint(1, 100) <= pc:
                L["terminal_ok"] = True
                self.contar("hackeos_ok")
                self.say(f"HACKEO de terminal en {mundo.LOCS[lid]['nombre']} ÉXITO ({int(pc)}%)")
                return True
        L["term_bloq"] = self.reloj + 24 * 60
        self.contar("hackeos_fallidos")
        self.say(f"HACKEO fallido x3: terminal bloqueado 24 h")
        return False

    # ----------------------------------------------------------------- atasco (bloque 39)
    def pasar_estrecho(self, tipo="ventana", lid=None, ajuste=0):
        """Paso estrecho (bloque 49): umbral de atasco aleatorio 40-60%. Si hay atasco: ataques mientras estas atascado."""
        p = self.p
        lid = lid or p["loc"]
        umbral = max(40, min(60, self.rng.randint(40, 60) + ajuste))  # limites duros 40-60
        self.contar("atascos_tiradas")
        self.contar("estrechos_" + tipo)
        if self.rng.randint(1, 100) > umbral:
            self.say(f"pasa por {tipo} sin atascarse (umbral {umbral}%)", fuerte=False)
            return True
        self.contar("atascos")
        p["atascado"] = True
        minutos = 0
        while p["atascado"] and minutos < 60:
            self.avanzar(10)
            minutos += 10
            d = mundo.LOCS[lid]
            aqui = self.vivos(lid)
            prob = 60 if aqui else {"S": 3, "N": 12, "H": 25}[d["clase"]]
            if self.pct(prob):
                g = next((g for g in self.locs[lid]["grupos"] if any(e["hp"] > 0 for e in g["miembros"])), None)
                if g is None and d["pool"] != "civil":
                    g = self.generar_grupo(lid)
                if g:
                    self.contar("ataques_mientras_atascado")
                    self.say(f"ATASCADO en {tipo} ({umbral}%): lo atacan (vulnerable)")
                    res = self.combate(g["miembros"], emboscada_enemiga=True, policy=self.policy, atascado=True)
                    if res == "derrota":
                        p["atascado"] = False
                        self.derrota(lid)
                        return False
            if p["atascado"] and self.pct(40 + 4 * max(p["stats"]["FUE"], p["stats"]["AGI"])):
                p["atascado"] = False
        p["atascado"] = False
        if minutos >= 60 or minutos > 30:
            if self.pct(30):
                perd = int(p["cuñas"] * self.rng.uniform(0.05, 0.15))
                p["cuñas"] -= perd
                self.contar("robos_por_atasco")
                self.say(f"ATASCADO en {tipo} ({umbral}%): robo por estructura −{perd}")
                return False
        self.say(f"ATASCADO en {tipo} ({umbral}%): se libera tras {minutos} min", fuerte=False)
        return False

    def salir_por_ventana(self):
        return self.pasar_estrecho("ventana")

    def marcar_minimapa(self, destino):
        """Mapa de muñeca: marcar una cuadra cercana y avanzar. Sin viaje rapido y sin vulnerabilidad (bloque 47)."""
        self.contar("marcas_minimapa")
        return self.viajar(destino, rapido=False)

    def _umbral(self, a, b):
        """Cruce entre cuadra y edificio: puerta (cerradura) o paso estrecho (bloque 48-49). True si se puede pasar."""
        D = mundo.LOCS
        edif = b if D[b].get("tipo") == "edificio" else (a if D[a].get("tipo") == "edificio" else None)
        if edif is None:
            return True
        acc = D[edif].get("accesos") or {}
        puerta = acc.get("puerta", 0)
        estrechos = [t for t in ("ventana", "agujero", "conducto") if acc.get(t)]
        abierta = self.locs[edif].setdefault("puerta_abierta", False)
        if abierta and not (estrechos and self.pct(8)):
            return True
        if estrechos and self.pct(10):
            return self.pasar_estrecho(self.rng.choice(estrechos), lid=a, ajuste=0) or self.p["loc"] == a
        if puerta == 0:
            self.locs[edif]["puerta_abierta"] = True
            return True
        for _ in range(3):
            pc = (70 - 12 * puerta + self.p["stats"]["AGI"] * 3 + self.p["nivel"]) if self.p["inv"].get("ganzua", 0) else (60 - 10 * puerta + self.p["stats"]["FUE"] * 3 + self.p["nivel"])
            self.avanzar(self.rng.randint(3, 8))
            if self.rng.randint(1, 100) <= max(5, min(95, pc)):
                self.locs[edif]["puerta_abierta"] = True
                self.contar("puertas_abiertas")
                return True
        if estrechos:
            self.contar("entradas_por_estrecho")
            return self.pasar_estrecho(self.rng.choice(estrechos), lid=a) or self.p["loc"] == a
        self.contar("puertas_imposibles")
        return False

    # ----------------------------------------------------------------- comercio (bloque 09)
    def precio_compra(self, valor):
        return max(1, int(valor * max(0.8, 1.4 - self.p["stats"]["CAR"] * 0.02)))

    def precio_venta(self, valor):
        return max(1, int(valor * min(0.7, 0.4 + self.p["stats"]["CAR"] * 0.02)))

    def vender(self, item, n=1):
        p = self.p
        if p["inv"].get(item, 0) < n:
            return False
        v = mundo.OBJETOS[item][2]
        p["inv"][item] -= n
        p["cuñas"] += self.precio_venta(v) * n
        self.contar("ventas", n)
        return True

    def comprar(self, item, n=1):
        v = mundo.OBJETOS[item][2]
        c = self.precio_compra(v) * n
        if self.p["cuñas"] < c:
            return False
        self.p["cuñas"] -= c
        self.p["inv"][item] = self.p["inv"].get(item, 0) + n
        self.contar("compras", n)
        return True

    def policy(self, sim, vivos, acciones, oculto, guardia):  # reemplazada por el bot
        return ("normal",)
