"""Jugador automatico: sigue las reglas de los bloques y juega toda la campana."""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import motor  # noqa: E402

mundo = motor.mundo

PRINCIPALES = getattr(mundo, "PRINCIPALES", ["M-01", "M-02", "M-03", "M-04", "M-05", "M-06", "M-07", "M-08"])
TIENDAS = getattr(mundo, "TIENDAS", ("L-007", "L-010", "L-011"))
TIENDA_ARMAS = getattr(mundo, "TIENDA_ARMAS", "L-007")
BANCOS = getattr(mundo, "BANCOS", ("L-001", "L-007"))
ZONA_CARNE = getattr(mundo, "ZONA_CARNE", "L-012")
ZONAS_RECURSO = getattr(mundo, "ZONAS_RECURSO", ("L-015", "L-016"))
TERMINALES = getattr(mundo, "TERMINALES", {"L-011": 1, "L-019": 3, "L-020": 4})
COMP_AL_DESPEJAR = getattr(mundo, "COMP_AL_DESPEJAR", {"L-009": "K-5"})
COMPANERO_INICIAL = getattr(mundo, "COMPANERO_INICIAL", "K-1")
POSTJUEGO = getattr(mundo, "POSTJUEGO", ("L-021", "C-034"))
HOGAR = mundo.PROTAGONISTA["hogar"]


class Bot:
    def __init__(self, sim):
        self.s = sim
        sim.policy = self.policy
        self.paso_ctx = {}
        self.fin_campana = False
        self.sin_progreso = 0

    # ------------------------------------------------------------------ combate
    def policy(self, sim, vivos, acciones, oculto, guardia):
        p = sim.p
        hpf = p["hp"] / sim.hpmax()
        cerca = [e for e in vivos if e["dist"] == 0]
        curas = p["inv"].get("venda", 0) + p["inv"].get("venda_reforzada", 0) + p["inv"].get("medicina", 0)
        if hpf < 0.30 and curas:
            return ("vendas",)
        if hpf < 0.18 and cerca and sim.pct(60):
            return ("escapar",)
        if not cerca:
            return ("acercar",)
        obj = min(cerca, key=lambda e: e["hp"])
        if oculto:
            return ("sigiloso", obj)
        if len(cerca) >= 3 and hpf < 0.5 and guardia is None:
            return ("defensa",)
        if len(cerca) >= 2 and hpf < 0.75 and acciones >= 1 and not getattr(self, "_empujo", False):
            self._empujo = True
            return ("empujar",)
        self._empujo = False
        if hpf < 0.6:
            return ("rapido", obj)
        if obj.get("jefe") or obj["talla"] >= 4:
            return ("preciso", obj)
        if acciones >= 2 and obj["hp"] > sim.dano_nominal() * 2.5:
            return ("potente", obj)
        return ("normal", obj)

    # ------------------------------------------------------------------ utilidades
    def en_ciudad(self):
        return mundo.LOCS[self.s.p["loc"]]["clase"] == "S"

    def ir(self, destino, permitir_rapido=True):
        s = self.s
        if s.p["loc"] == destino:
            return True
        if s.p["loc"] == HOGAR and mundo.LOCS[HOGAR].get("ventana") and (s.vivos(HOGAR) or s.pct(30)):
            s.salir_por_ventana()  # el hogar tiene ventana: atasco 40-60% (bloque 39)
        # fisico: no se puede ir si hay enemigos persistentes cerca? se puede (huir)
        ruta = s.ruta(s.p["loc"], destino)
        if ruta is None:
            # destino aun desconocido: se explora salto a salto por las conexiones visibles
            camino = s.camino_real(s.p["loc"], destino)
            if camino is None:
                return False
            for paso in camino:
                if not s.puede_entrar(paso):
                    return False
                if not s.viajar(paso, rapido=False) or s.p["loc"] != paso:
                    return False
            return s.p["loc"] == destino
        cruces, prev = 0, s.p["loc"]
        for hop in ruta:
            ua, ub = mundo.LOCS[prev].get("ubicacion"), mundo.LOCS[hop].get("ubicacion")
            if not ua or not ub or ua != ub:
                cruces += 1
            prev = hop
        if cruces == 0 and any(mundo.LOCS[x].get("ubicacion") for x in ruta):
            ok = s.marcar_minimapa(destino)      # mapa de muñeca: de cuadra a cuadra, sin vulnerabilidad
        else:
            ok = s.viajar(destino, rapido=permitir_rapido and cruces >= 3)
        if ok and s.p["loc"] != destino:
            return False
        return ok and s.p["loc"] == destino

    def limpiar_lugar(self, lid):
        """Explora a fondo un lugar: pelea lo que haya, registra todos los puntos y busca (bloques 04-05)."""
        s, p = self.s, self.s.p
        if p["loc"] != lid or s.locs[lid].get("limpiado"):
            return
        if mundo.LOCS[lid]["clase"] == "H" and p["nivel"] < mundo.LOCS[lid]["nivel"] - 3:
            return  # demasiado peligroso por ahora
        if s.vivos(lid) and self.pelear_en(lid) < 0:
            return
        self.registrar_todo(lid)
        self.explorar(lid, hasta=4)
        if not s.vivos(lid):
            s.locs[lid]["limpiado"] = True
            s.contar("lugares_explorados_a_fondo")

    def mantenimiento(self):
        s, p = self.s, self.s.p
        # necesidades
        if p["hambre"] >= 45:
            for it in ("lata", "carne"):
                if p["inv"].get(it, 0) > 0:
                    p["inv"][it] -= 1
                    p["hambre"] = max(0, p["hambre"] - 30)
                    break
        if p["sed"] >= 45:
            for it in ("agua", "agua_turbia"):
                if p["inv"].get(it, 0) > 0:
                    p["inv"][it] -= 1
                    p["sed"] = max(0, p["sed"] - 35)
                    break
        # curar si estamos en ciudad
        if self.en_ciudad() and p["hp"] < s.hpmax() * 0.7:
            self.descansar_en_cama(8 if p["hp"] < s.hpmax() * 0.4 else 4)
        # comercio en ciudad
        if p["loc"] in TIENDAS:
            self.comerciar()

    def descansar_en_cama(self, horas):
        s, p = self.s, self.s.p
        lid = p["loc"]
        if not mundo.LOCS[lid]["cama"]:
            camas = [l for l, d in mundo.LOCS.items() if d["cama"] and s.locs[l]["descubierta"] and mundo.LOCS[l]["clase"] != "H"]
            destino = min(camas, key=lambda l: s.distancia(lid, l))
            if not self.ir(destino):
                return
        s.avanzar(horas * 60)
        p["hp"] = min(s.hpmax(), p["hp"] + int(s.hpmax() * 0.125 * horas))
        p["fatiga"] = max(0, p["fatiga"] - 10 * horas)
        p["estados"].clear()
        s.contar("descansos")
        if horas >= 8 or p["hp"] >= s.hpmax():
            p["hp"] = s.hpmax() if horas >= 8 else p["hp"]
        s.say(f"DESCANSA {horas} h en cama → PV {p['hp']}/{s.hpmax()}", fuerte=False)
        # el hogar puede ser atacado de noche (bloque 39)
        if p["loc"] == HOGAR and s.pct(6):
            s.contar("ataques_al_hogar")
            self.pelear_en(HOGAR, forzar=True)

    def curar_fuera_de_combate(self):
        """Usa vendas/medicina antes de entrar a pelear si la vida esta baja (como haria un jugador)."""
        s, p = self.s, self.s.p
        while p["hp"] < s.hpmax() * 0.75:
            for it, cura in (("venda", 10), ("venda_reforzada", 20), ("medicina", 30 + p["nivel"])):
                if p["inv"].get(it, 0) > 0:
                    p["inv"][it] -= 1
                    p["hp"] = min(s.hpmax(), p["hp"] + cura)
                    s.avanzar(1)
                    s.contar("curaciones_fuera_de_combate")
                    break
            else:
                break

    def comerciar(self):
        s, p = self.s, self.s.p
        # vender basura
        for it in ("chatarra", "cubiertos", "cuerda", "piezas", "circuito", "agua_turbia", "herramientas"):
            n = p["inv"].get(it, 0)
            keep = {"chatarra": 3, "piezas": 2, "circuito": 2}.get(it, 0)
            if n > keep and not self.necesita(it):
                s.vender(it, n - keep)
        # comprar suministros
        for it, objetivo in (("venda", 6), ("lata", 3), ("agua", 3), ("medicina", 2)):
            while p["inv"].get(it, 0) < objetivo and p["cuñas"] > s.precio_compra(mundo.OBJETOS[it][2]) + 20:
                if not s.comprar(it):
                    break
        # mejorar arma / armadura
        if p["loc"] == TIENDA_ARMAS:
            tier_obj = min(5, 1 + p["nivel"] // 5)
            for t in range(tier_obj, p["arma"], -1):
                key = f"arma_t{t}"
                if key in mundo.OBJETOS and p["cuñas"] > s.precio_compra(mundo.OBJETOS[key][2]) + 30:
                    s.comprar(key)
                    p["inv"][key] -= 1
                    p["arma"], p["dur"] = t, 100
                    s.contar("armas_compradas")
                    s.say(f"compra {mundo.OBJETOS[key][0]} (tier {t})")
                    break
            for key, tier in (("armadura_e4", 4), ("armadura_e2", 2)):
                if tier > p["armadura"] and p["nivel"] >= (8 if tier == 4 else 1) and p["cuñas"] > s.precio_compra(mundo.OBJETOS[key][2]) + 30:
                    s.comprar(key)
                    p["inv"][key] -= 1
                    p["armadura"] = tier
                    s.contar("armaduras_compradas")
                    s.say(f"compra {mundo.OBJETOS[key][0]} (tier {tier})")
                    break
            # reparar arma
            if p["dur"] < 45 and p["cuñas"] >= 20:
                p["cuñas"] -= 20
                p["dur"] = 100
                s.contar("reparaciones")
                s.say("repara el arma con el mecánico (20 cuñas)", fuerte=False)
        if p["dur"] < 45 and p["inv"].get("kit_reparacion", 0):
            p["inv"]["kit_reparacion"] -= 1
            p["dur"] = min(100, p["dur"] + 40)
            s.contar("reparaciones")

    def necesita(self, it):
        for q, est in self.s.quests.items():
            if est == "activa":
                for paso in mundo.QUESTS[q]["steps"]:
                    if paso[0] in ("get", "give", "craft") and paso[-1] == it:
                        return True
                    if paso[0] == "collect" and paso[2] == it:
                        return True
        return it in ("circuito", "piezas", "chatarra")

    # ------------------------------------------------------------------ combate en un lugar
    def detectado(self, grupo_n):
        s, p = self.s, self.s.p
        pc = 55 - (p["stats"]["AGI"] * 3 + p["nivel"]) + 5 * (grupo_n - 1)
        return s.pct(max(5, min(90, pc)))

    def pelear_en(self, lid, forzar=False, solo_especies=None, max_kills=None):
        """Pelea los grupos vivos del lugar. Devuelve cantidad de bajas o -1 si hubo derrota."""
        s, p = self.s, self.s.p
        bajas = 0
        intentos = 0
        while True:
            vivos = s.vivos(lid)
            if solo_especies:
                vivos_f = [e for e in vivos if e["sid"] in solo_especies]
            else:
                vivos_f = vivos
            if not vivos_f or (max_kills is not None and bajas >= max_kills):
                break
            intentos += 1
            if intentos > 40:
                break
            # elegir un grupo
            grupo = None
            for g in s.locs[lid]["grupos"]:
                if any(e["hp"] > 0 and (not solo_especies or e["sid"] in solo_especies) for e in g["miembros"]):
                    grupo = g
                    break
            if not grupo:
                break
            miembros = [e for e in grupo["miembros"] if e["hp"] > 0]
            self.curar_fuera_de_combate()
            if p["hp"] < s.hpmax() * 0.5:
                if self.en_ciudad() or mundo.LOCS[lid]["cama"]:
                    self.descansar_en_cama(4)
                elif p["inv"].get("venda", 0) + p["inv"].get("medicina", 0) >= 2:
                    pass
                else:
                    return bajas  # se retira a curarse
            sorp = not self.detectado(len(miembros))
            for e in miembros:
                e["dist"] = 2
            kills0 = s.contadores.get("kills", 0)
            res = s.combate(grupo["miembros"], sorpresa=sorp, policy=self.policy)
            bajas += s.contadores.get("kills", 0) - kills0
            if res == "derrota":
                s.derrota(lid)
                return -1
            if res == "escape":
                return bajas
        return bajas

    # ------------------------------------------------------------------ registrar / explorar
    def registrar_todo(self, lid, objetivo=None):
        s, p = self.s, self.s.p
        for cid, st in s.locs[lid]["cont"].items():
            if st["abierto"]:
                continue
            if self.s.vivos(lid):
                if self.pelear_en(lid) < 0:
                    return False
            ok, obt = s.registrar(lid, cid)
            if objetivo and p["inv"].get(objetivo, 0):
                return True
        return True

    def explorar(self, lid, hasta=3):
        s = self.s
        L = s.locs[lid]
        n = 0
        while L["explor"] < hasta and n < 6:
            n += 1
            antes = len(s.vivos(lid))
            s.buscar(lid)
            if len(s.vivos(lid)) > antes:
                if self.pelear_en(lid) < 0:
                    return False
        return True

    # ------------------------------------------------------------------ misiones
    def disponible(self, q):
        s = self.s
        d = mundo.QUESTS[q]
        if s.quests[q] in ("hecha", "fallida"):
            return False
        if q in PRINCIPALES:
            i = PRINCIPALES.index(q)
            if i > 0 and s.quests[PRINCIPALES[i - 1]] != "hecha":
                return False
        return s.p["nivel"] >= d.get("nivel_min", d["nivel"] - 2)

    def elegir_quest(self):
        s = self.s
        activas = [q for q, e in s.quests.items() if e == "activa"]
        cand = [q for q in activas if self.disponible(q)]
        if cand:
            return sorted(cand, key=lambda q: (0 if q in PRINCIPALES else 1, q))[0]
        for q in PRINCIPALES:
            if s.quests[q] == "disponible" and self.disponible(q):
                return q
        sec = [q for q, e in s.quests.items() if e == "disponible" and q not in PRINCIPALES and self.disponible(q)]
        if sec:
            return sorted(sec, key=lambda q: (mundo.QUESTS[q]["nivel"], q))[0]
        return None

    def paso_actual(self, q):
        return mundo.QUESTS[q]["steps"][self.s.qpaso[q]]

    def avanzar_quest(self, q):
        s, p = self.s, self.s.p
        d = mundo.QUESTS[q]
        if s.quests[q] == "disponible":
            if not self.ir(mundo.NPCS[d["giver"]]["loc"]):
                return False
            self.hablar(d["giver"])
            s.quests[q] = "activa"
            s.say(f"MISIÓN ACEPTADA {q} «{d['nombre']}» ({d['tipo']})")
        while s.qpaso[q] < len(d["steps"]):
            paso = self.paso_actual(q)
            r = self.ejecutar_paso(q, paso)
            if r == "ok":
                s.qpaso[q] += 1
                self.paso_ctx.pop(q, None)
                continue
            return False
        # completada
        s.quests[q] = "hecha"
        s.ganar_xp(d["xp"])
        for it in d.get("rec", []):
            self.dar_recompensa(it)
        s.contar("misiones_" + d["tipo"])
        s.say(f"MISIÓN COMPLETADA {q} «{d['nombre']}» +{d['xp']} XP")
        if d.get("comp"):
            self.reclutar(d["comp"])
        if q == "M-08":
            s.fl["purificador"] = True
            s.say("EL PURIFICADOR VUELVE A FUNCIONAR: aparece el Oasis Verde")
        return True

    def dar_recompensa(self, it):
        s, p = self.s, self.s.p
        if it.startswith("cuñas"):
            p["cuñas"] += int(it[5:])
        elif it.startswith("arma_t"):
            t = int(it[-1])
            if t > p["arma"]:
                p["arma"], p["dur"] = t, 100
        elif it.startswith("armadura_e"):
            t = int(it[-1])
            if t > p["armadura"]:
                p["armadura"] = t
        else:
            p["inv"][it] = p["inv"].get(it, 0) + 1

    def reclutar(self, kid):
        s, p = self.s, self.s.p
        if kid in p["comps"]:
            return
        if len(p["comps"]) >= 3:
            p["comps"].pop(0)
        p["comps"].append(kid)
        s.contar("companeros")
        c = mundo.COMPANEROS.get(kid, {"nombre": kid, "aporte": ""})
        s.say(f"RECLUTA a {c['nombre']} ({c['aporte']})")

    def hablar(self, nid):
        s = self.s
        n = mundo.NPCS[nid]
        if s.p["loc"] != n["loc"]:
            self.ir(n["loc"])
        s.avanzar(5)
        st = s.npc_estado[nid]
        st["hablado"] += 1
        st["rel"] = min(100, st["rel"] + 3)
        s.contar("conversaciones")
        s.say(f"HABLA con {n['nombre']} ({n['arq']}; {n['pers']}) rel={st['rel']}", fuerte=False)

    def ejecutar_paso(self, q, paso):
        s, p = self.s, self.s.p
        tipo = paso[0]
        ctx = self.paso_ctx.setdefault(q, {})
        ctx["intentos"] = ctx.get("intentos", 0) + 1
        if ctx["intentos"] > 60:
            s.violaciones.append(f"{q} paso {paso} no se puede completar tras 60 intentos")
            ctx["intentos"] = 0
            return "bloqueado"
        if tipo == "talk":
            if not self.ir(mundo.NPCS[paso[1]]["loc"]):
                return "bloqueado"
            self.hablar(paso[1])
            return "ok"
        if tipo == "deliver_msg":
            if not self.ir(mundo.NPCS[paso[1]]["loc"]):
                return "bloqueado"
            self.hablar(paso[1])
            return "ok"
        if tipo == "goto":
            return "ok" if self.ir(paso[1]) else "bloqueado"
        if tipo == "get":
            loc, item = paso[1], paso[2]
            if not self.ir(loc):
                return "bloqueado"
            if item == "baul":
                st = s.locs[loc]["cont"]["C-001"]
                s.registrar(loc, "C-001")
                return "ok"
            if p["inv"].get(item, 0):
                return "ok"
            if s.vivos(loc) and self.pelear_en(loc) < 0:
                return "bloqueado"
            self.registrar_todo(loc, item)
            if p["inv"].get(item, 0):
                return "ok"
            self.explorar(loc, hasta=ctx.get("explor", 3))
            ctx["explor"] = ctx.get("explor", 3) + 1
            # si todo abierto y sin item: se genera por busqueda profunda (regla 04: elementos de mision garantizados)
            if all(c["abierto"] for c in s.locs[loc]["cont"].values()) and ctx["intentos"] > 8:
                s.violaciones.append(f"{q}: objeto de misión {item} no estaba en ningún contenedor de {loc}")
                p["inv"][item] = 1
            return "pendiente" if not p["inv"].get(item, 0) else "ok"
        if tipo == "search_hidden":
            loc, target = paso[1], paso[2]
            if not self.ir(loc):
                return "bloqueado"
            while target not in s.locs[loc]["ocultas_halladas"] and ctx.get("busq", 0) < 20:
                ctx["busq"] = ctx.get("busq", 0) + 1
                antes = len(s.vivos(loc))
                s.buscar(loc)
                if len(s.vivos(loc)) > antes and self.pelear_en(loc) < 0:
                    return "bloqueado"
            if target not in s.locs[loc]["ocultas_halladas"]:
                s.violaciones.append(f"{q}: conexión oculta no hallada en 20 búsquedas")
                s.locs[loc]["ocultas_halladas"].add(target)
                s.locs[target]["descubierta"] = True
            return "ok"
        if tipo in ("kill", "kill_species"):
            loc = paso[1]
            n = paso[2]
            especies = paso[3] if tipo == "kill_species" else None
            if not self.ir(loc):
                return "bloqueado"
            base = ctx.setdefault("base", s.kills_loc.get(loc, 0) if especies is None else sum(s.kills_esp.get(x, 0) for x in especies))
            def hechas():
                if especies is None:
                    return s.kills_loc.get(loc, 0) - base
                return sum(s.kills_esp.get(x, 0) for x in especies) - base
            while hechas() < n:
                vivos = s.vivos(loc) if especies is None else [e for e in s.vivos(loc) if e["sid"] in especies]
                if not vivos:
                    if mundo.LOCS[loc]["clase"] == "S" or mundo.LOCS[loc]["pool"] == "civil":
                        # zonas seguras: la mision pide enemigos que ya rondan la zona
                        s.generar_grupo("L-002", forzar_especies=especies) if False else None
                    s.buscar(loc)
                    vivos = s.vivos(loc) if especies is None else [e for e in s.vivos(loc) if e["sid"] in especies]
                    if not vivos and ctx["intentos"] % 4 == 0:
                        s.generar_grupo(loc, forzar_especies=especies)
                        s.contar("spawns_de_mision")
                if self.pelear_en(loc, solo_especies=especies) < 0:
                    return "bloqueado"
                ctx["intentos"] += 1
                if ctx["intentos"] > 55:
                    break
                if p["hp"] < s.hpmax() * 0.4:
                    self.descansar_en_cama(8)
                    if not self.ir(loc):
                        return "bloqueado"
            return "ok" if hechas() >= n else "pendiente"
        if tipo == "boss":
            loc, clave = paso[1], paso[2]
            if not self.ir(loc):
                return "bloqueado"
            if s.fl.get("jefe_" + clave) != "muerto":
                if s.fl.get("jefe_" + clave) is None:
                    s.generar_jefe(loc, clave)
                    s.say(f"JEFE: {mundo.JEFES[clave]['nombre']} aparece")
                # limpiar escolta antes
                for _ in range(8):
                    if not [e for e in s.vivos(loc) if e.get("jefe")]:
                        break
                    if p["hp"] < s.hpmax() * 0.6:
                        self.descansar_en_cama(8)
                        if not self.ir(loc):
                            return "bloqueado"
                    if self.pelear_en(loc) < 0:
                        return "bloqueado"
                if not [e for e in s.vivos(loc) if e.get("jefe")] and any(
                        e.get("jefe") and e["hp"] <= 0 for g in [] for e in g):
                    pass
                if [e for e in s.vivos(loc) if e.get("jefe")]:
                    return "pendiente"
                s.fl["jefe_" + clave] = "muerto"
                s.contar("jefes_derrotados")
                s.say(f"JEFE DERROTADO: {mundo.JEFES[clave]['nombre']}")
            return "ok"
        if tipo == "hack":
            loc = paso[1]
            if not self.ir(loc):
                return "bloqueado"
            if s.vivos(loc) and self.pelear_en(loc) < 0:
                return "bloqueado"
            dif = TERMINALES.get(loc, 2)
            if s.terminal(loc, dif):
                return "ok"
            s.avanzar(24 * 60)
            return "pendiente"
        if tipo == "give":
            npc, item = paso[1], paso[2]
            if not p["inv"].get(item, 0):
                self.conseguir(item)
                if not p["inv"].get(item, 0):
                    return "pendiente"
            if not self.ir(mundo.NPCS[npc]["loc"]):
                return "bloqueado"
            self.hablar(npc)
            p["inv"][item] -= 1
            s.say(f"ENTREGA {mundo.OBJETOS.get(item, (item,))[0]} a {mundo.NPCS[npc]['nombre']}", fuerte=False)
            return "ok"
        if tipo == "collect":
            loc, rec, n = paso[1], paso[2], paso[3]
            if not self.ir(loc):
                return "bloqueado"
            base = ctx.setdefault("base", p["inv"].get(rec, 0))
            for _ in range(10):
                if p["inv"].get(rec, 0) - base >= n:
                    break
                s.avanzar(10)
                if s.pct(60):
                    p["inv"][rec] = p["inv"].get(rec, 0) + 1
                    s.contar("recolecciones")
                if s.vivos(loc) and self.pelear_en(loc) < 0:
                    return "bloqueado"
            return "ok" if p["inv"].get(rec, 0) - base >= n else "pendiente"
        if tipo == "choose":
            a, b = paso[1], paso[2]
            eleg = a if s.rng.random() < 0.5 else b
            s.fl[f"bando_{q}"] = eleg
            otro = b if eleg == a else a
            s.say(f"ELIGE BANDO en {q}: {eleg} (el grupo «{otro}» pasa a ser hostil)")
            s.contar("bandos_elegidos")
            lugar = paso[3] if len(paso) > 3 else ("L-010" if q == "M-05" else "L-014")
            sp = paso[4] if len(paso) > 4 else ("U-11" if q == "M-05" else "U-04")
            g = s.generar_grupo(lugar, forzar_especies=[sp])
            if g:
                s.contar("grupos_rivales")
            return "ok"
        if tipo == "recruit":
            self.reclutar(paso[1])
            return "ok"
        if tipo == "craft":
            return self.fabricar(paso[1])
        if tipo == "discover":
            n = paso[1]
            while sum(1 for L in s.locs.values() if L["descubierta"]) < n + 3:
                vecinos = [v for v in s.vecinos(p["loc"]) if not s.locs[v]["visitada"]]
                if not vecinos:
                    break
                if not self.ir(vecinos[0]):
                    break
            return "ok"
        return "ok"

    def conseguir(self, item):
        s, p = self.s, self.s.p
        if item == "carne":
            for _ in range(4):
                if p["inv"].get("carne", 0):
                    return
                self.ir(ZONA_CARNE)
                self.pelear_en(ZONA_CARNE)
                s.buscar(ZONA_CARNE)
                s.generar_grupo(ZONA_CARNE)
                self.pelear_en(ZONA_CARNE)
        elif item == "recurso_bio":
            for lid in ZONAS_RECURSO:
                if p["inv"].get("recurso_bio", 0):
                    return
                self.ir(lid)
                for _ in range(4):
                    s.avanzar(10)
                    if s.pct(60):
                        p["inv"]["recurso_bio"] = p["inv"].get("recurso_bio", 0) + 1
                        break
        elif item in ("circuito", "piezas"):
            if self.ir(TIENDA_ARMAS):
                s.comprar(item)

    def fabricar(self, item):
        s, p = self.s, self.s.p
        receta = {"radio": {"circuito": 1, "chatarra": 2}, "artefacto": {"piezas": 2, "circuito": 1}}[item]
        if p["loc"] not in BANCOS:
            self.ir(BANCOS[0])
        for k, n in receta.items():
            while p["inv"].get(k, 0) < n:
                if p["loc"] != TIENDA_ARMAS:
                    self.ir(TIENDA_ARMAS)
                if not s.comprar(k):
                    s.violaciones.append(f"no alcanza el dinero para fabricar {item}")
                    p["cuñas"] += 20
        for k, n in receta.items():
            p["inv"][k] -= n
        s.avanzar(30)
        tir = s.rng.randint(1, 100)
        pc = 50 + p["stats"]["INT"] * 4 + p["nivel"]
        if tir > pc:
            for k, n in receta.items():
                p["inv"][k] = p["inv"].get(k, 0) + n // 2
            s.say(f"FABRICAR {item}: falla ({tir}>{pc}), pierde la mitad de los componentes")
            return "pendiente"
        p["inv"][item] = p["inv"].get(item, 0) + 1
        s.contar("fabricaciones")
        s.say(f"FABRICA {item} ({tir}≤{pc})")
        return "ok"

    # ------------------------------------------------------------------ explorar libre / grind
    def zona_grind(self):
        s, p = self.s, self.s.p
        cand = []
        for lid, d in mundo.LOCS.items():
            if d["clase"] == "H" and s.locs[lid]["visitada"] and s.puede_entrar(lid):
                cand.append((abs(d["nivel"] - p["nivel"] - 2), lid))
        if not cand:
            for lid, d in mundo.LOCS.items():
                if d["clase"] in ("H", "N") and d["pool"] != "civil" and s.locs[lid]["descubierta"] and s.puede_entrar(lid):
                    cand.append((abs(d["nivel"] - p["nivel"] - 1), lid))
        return min(cand)[1] if cand else HOGAR

    def grind(self):
        s, p = self.s, self.s.p
        lid = self.zona_grind()
        if p["hp"] < s.hpmax() * 0.6:
            self.descansar_en_cama(8)
        if not self.ir(lid):
            s.avanzar(60)
            return
        if not s.vivos(lid):
            s.buscar(lid)
            if not s.vivos(lid) and mundo.LOCS[lid]["clase"] == "H" and s.locs[lid]["despejada"]:
                self.registrar_todo(lid)
                # esperar la regeneracion de la poblacion (>48 h) descansando en una cama
                self.descansar_en_cama(8)
                s.avanzar(24 * 60)
                return
        if s.vivos(lid):
            self.pelear_en(lid)
        else:
            self.registrar_todo(lid)

    def paso_de_juego(self):
        s, p = self.s, self.s.p
        self.mantenimiento()
        if mundo.LOCS[p["loc"]]["clase"] != "S" or mundo.LOCS[p["loc"]]["cont"]:
            self.limpiar_lugar(p["loc"])
        q = self.elegir_quest()
        if q:
            ok = self.avanzar_quest(q)
            if not ok:
                self.sin_progreso += 1
                if self.sin_progreso % 3 == 0:
                    self.grind()
                if self.sin_progreso > 400:
                    s.violaciones.append(f"{q} bloqueada: se aborta")
                    s.quests[q] = "fallida"
                    self.sin_progreso = 0
            else:
                self.sin_progreso = 0
        else:
            todas = all(e == "hecha" for q2, e in s.quests.items())
            if todas:
                self.fin_campana = True
            else:
                self.grind()

    def jugar(self, max_dias=700, post_dias=60):
        s = self.s
        # compañero inicial
        if COMPANERO_INICIAL:
            self.reclutar(COMPANERO_INICIAL)
        dia_fin = None
        iteraciones = 0
        while s.dia() < max_dias and iteraciones < 20000:
            iteraciones += 1
            t0 = s.reloj
            self.paso_de_juego()
            if s.reloj == t0:
                s.avanzar(30)  # garantia: toda iteracion consume tiempo (evita bucles sin avance)
            # recluta a Tuerca al despejar el Deposito 9
            for kid_c, cc in mundo.COMPANEROS.items():
                if cc.get("loc") == s.p["loc"] and kid_c not in s.p["comps"] and not s.fl.get("rec_" + kid_c) and len(s.p["comps"]) < 3 and "edad" in cc and cc["edad"] != "neutro":
                    s.fl["rec_" + kid_c] = True
                    self.reclutar(kid_c)
            for lid_c, kid in COMP_AL_DESPEJAR.items():
                if s.locs[lid_c]["despejada"] and kid not in s.p["comps"] and not s.fl.get("rec_" + kid):
                    s.fl["rec_" + kid] = True
                    self.reclutar(kid)
            if self.fin_campana and dia_fin is None:
                dia_fin = s.dia()
                self.nivel_fin = s.p["nivel"]
                s.say(f"CAMPAÑA COMPLETA al día {dia_fin}, nivel {s.p['nivel']}")
            if dia_fin is not None and s.dia() >= dia_fin + post_dias:
                break
            if dia_fin is not None:
                self.post_juego()
        return dia_fin

    def post_juego(self):
        """Despues de completar todo: seguir jugando (enemigos regeneran, comercio, oasis)."""
        s, p = self.s, self.s.p
        s.contar("turnos_post_juego")
        if POSTJUEGO and s.fl.get("purificador") and not s.fl.get("oasis_visitado"):
            if self.ir(POSTJUEGO[0]):
                s.fl["oasis_visitado"] = True
                s.registrar(POSTJUEGO[0], POSTJUEGO[1])
                s.say("visita el lugar nuevo que aparece al terminar la campaña (cama y alacena)")
        if p["nivel"] < motor.NIVEL_MAX or s.contadores.get("turnos_post_juego", 0) % 3 == 0:
            self.grind()
        else:
            self.mantenimiento()
            self.descansar_en_cama(8)
            s.avanzar(12 * 60)
