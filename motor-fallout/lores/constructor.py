"""Construye un mundo jugable (para el simulador) a partir de la definicion de un lore y de los catalogos.

Entrada: dict LORE (ver lore_bosque.py / lore_piratas.py). Salida: dict con las mismas claves que el modulo
simulador/mundo.py (LOCS, NPCS, COMPANEROS, QUESTS, JEFES, POOLS, OBJETOS, ARMAS, ...), mas metadatos para los bloques de texto.
"""
import copy
import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "catalogos"))
import asignaciones  # noqa: E402
sys.path.insert(0, str(RAIZ))
import generar_bestiario as gb  # noqa: E402

SLOT = {}
for _n in gb.ARCHIVOS_ESPECIES:
    for _e in gb.leer_tabla(RAIZ / _n):
        SLOT[_e["id"]] = _e["slot"]
import datos_misiones as dm  # noqa: E402

OBJ_BASE = {
    "venda": ("Venda", "consumible", 3), "venda_reforzada": ("Venda reforzada", "consumible", 8), "lata": ("Vianda", "consumible", 4),
    "agua": ("Agua limpia", "consumible", 3), "agua_turbia": ("Agua turbia", "consumible", 1), "medicina": ("Ungüento de hierbas", "consumible", 25),
    "ganzua": ("Ganzúa", "herramienta", 5), "herramientas": ("Caja de herramientas", "herramienta", 15), "kit_reparacion": ("Kit de remiendo", "herramienta", 30),
    "chatarra": ("Chatarra", "general", 1), "circuito": ("Circuito", "general", 6), "piezas": ("Piezas", "general", 5), "cuerda": ("Cuerda", "general", 2),
    "recurso_bio": ("Recurso natural", "recurso", 6), "carne": ("Carne fresca", "consumible", 4), "radio": ("Radio reparada", "mision", 0),
    "artefacto": ("Artefacto", "mision", 0), "dulce": ("Dulce casero", "consumible", 2),
}
ARMADURAS = {0: 0, 1: 1, 2: 3, 3: 6, 4: 10, 5: 16}
TIPOS_CONT = ["cajón", "alacena", "baúl", "mochila", "estantería", "ropero", "caja", "mostrador", "escritorio", "heladera", "barril", "cofre"]
LOOT = ["venda", "lata", "agua", "chatarra", "circuito", "piezas", "cuerda", "dulce", "venda_reforzada", "medicina", "herramientas", "kit_reparacion", "ganzua", "recurso_bio"]


class Constructor:
    def __init__(self, lore, semilla=2026):
        self.L = lore
        self.rng = random.Random(semilla)
        self.a = asignaciones.asignar()
        self.nodos = {}
        self.n_l = self.n_q = self.n_z = self.n_c = 0
        self.ubic = {}            # id lore -> info (id principal, nodos, territorio)
        self.por_lugar = {}       # codigo de lugar -> lista de ids de nodo donde puede vivir un NPC
        self.objetos = copy.deepcopy(OBJ_BASE)
        self.quests = {}
        self.npcs = {}
        self.companeros = {}
        self.jefes = {}
        self.items_mision = {}
        self.terr_nodos = {}

    # ------------------------------------------------------------------ nodos
    def _id(self, pref):
        if pref == "L":
            self.n_l += 1
            return f"L-{self.n_l:03d}"
        if pref == "Q":
            self.n_q += 1
            return f"Q-{self.n_q:03d}"
        self.n_z += 1
        return f"Z-{self.n_z:03d}"

    def _contenedores(self, n, cerr_max=1, extra=None):
        out = []
        for _ in range(n):
            self.n_c += 1
            cid = f"C-{self.n_c:04d}"
            tipo = self.rng.choice(TIPOS_CONT)
            cerr = self.rng.choice([0, 0, 0, 1, 2][: cerr_max + 3])
            items = self.rng.sample(LOOT, self.rng.randint(1, 3))
            if self.rng.random() < 0.3:
                items.append(f"cuñas{self.rng.randint(5, 40)}")
            out.append([cid, tipo, cerr, False, items])
        if extra:
            out[0][4].append(extra)
        return out

    def _nodo(self, pref, nombre, clase, espacio, terr, nivel, pool, **kw):
        nid = self._id(pref)
        d = dict(nombre=nombre, clase=clase, espacio=espacio, region=terr["nombre"], bioma=terr["formacion"], cama=False, nivel=nivel, pool=pool,
                 conn=[], cont=[], npc=[], desc=kw.pop("desc", ""), ubicacion=None, tipo="ubicacion")
        d.update(kw)
        self.nodos[nid] = d
        self.terr_nodos.setdefault(terr["id"], []).append(nid)
        return nid

    def _conectar(self, a, b):
        if b not in self.nodos[a]["conn"] and a != b:
            self.nodos[a]["conn"].append(b)

    # ------------------------------------------------------------------ ubicaciones
    def construir_ubicaciones(self):
        L = self.L
        for terr in L["territorios"]:
            lo, hi = terr["nivel"]
            n = len(terr["ubicaciones"])
            principales = []
            for k, u in enumerate(terr["ubicaciones"]):
                nivel = u.get("nivel") or int(lo + (hi - lo) * k / max(1, n - 1))
                pool = u.get("pool") or terr["pool"]
                if u["clase"] == "S" and not u.get("pool"):
                    pool = "civil"
                kind = u["kind"]
                if kind == "s":
                    nid = self._nodo("L", u["nombre"], u["clase"], u["espacio"], terr, nivel, pool, desc=u.get("desc", ""), cama=u.get("cama", False), terminal=u.get("terminal", False))
                    self.nodos[nid]["cont"] = self._contenedores(self.rng.randint(2, 4), extra=u.get("item"))
                    nodos = [nid]
                    entrada = nid
                elif kind == "p":
                    nodos = []
                    for q in range(u["cuadras"]):
                        qid = self._nodo("Q", f"{u['nombre']}, cuadra {q + 1}", u["clase"], "ext", terr, nivel, pool, ubicacion=u["nombre"], tipo="cuadra", cama=False)
                        self.nodos[qid]["cont"] = self._contenedores(1)
                        nodos.append(qid)
                        if q:
                            self._conectar(nodos[q - 1], qid)
                            self._conectar(qid, nodos[q - 1])
                    for qid in list(nodos):
                        for _ in range(self.rng.randint(1, 2)):
                            self._edificio(qid, u, terr, nivel, pool, nodos)
                    entrada = nodos[0]
                else:  # ciudad
                    nodos = []
                    prev_barrio = None
                    for (bnombre, nc) in u["barrios"]:
                        bq = []
                        for q in range(nc):
                            qid = self._nodo("Q", f"{bnombre}, cuadra {q + 1}", u["clase"], "ext", terr, nivel, pool, ubicacion=u["nombre"], tipo="cuadra")
                            self.nodos[qid]["cont"] = self._contenedores(1)
                            bq.append(qid)
                            nodos.append(qid)
                            if q:
                                self._conectar(bq[q - 1], qid)
                                self._conectar(qid, bq[q - 1])
                        if prev_barrio:
                            self._conectar(prev_barrio[-1], bq[0])
                            self._conectar(bq[0], prev_barrio[-1])
                            if len(prev_barrio) > 1 and len(bq) > 1:
                                self._conectar(prev_barrio[0], bq[-1])
                                self._conectar(bq[-1], prev_barrio[0])
                        prev_barrio = bq
                        for qid in bq:
                            for _ in range(self.rng.randint(2, 3)):
                                self._edificio(qid, u, terr, nivel, pool, nodos)
                    entrada = nodos[0]
                self.ubic[u["id"]] = dict(nodos=nodos, entrada=entrada, terr=terr["id"], clase=u["clase"], nombre=u["nombre"])
                principales.append(u["id"])
                for lug in u.get("lugares", []):
                    self.por_lugar.setdefault(lug, []).extend([x for x in nodos if self.nodos[x]["tipo"] != "edificio"] or nodos)
            # cadena y atajos dentro del territorio
            for i in range(len(principales) - 1):
                a, b = self.ubic[principales[i]]["entrada"], self.ubic[principales[i + 1]]["entrada"]
                self._conectar(a, b)
                self._conectar(b, a)
            for _ in range(max(1, n // 3)):
                a, b = self.rng.sample(principales, 2)
                ea, eb = self.ubic[a]["entrada"], self.ubic[b]["entrada"]
                self._conectar(ea, eb)
                self._conectar(eb, ea)
        for a, b in L["enlaces"]:
            ea, eb = self.ubic[a]["entrada"], self.ubic[b]["entrada"]
            self._conectar(ea, eb)
            self._conectar(eb, ea)

    def _edificio(self, qid, u, terr, nivel, pool, nodos):
        nombre_e, tipos, cama = self.rng.choice(self.L["edificios"])
        zid = self._nodo("Z", f"{nombre_e} de {self.nodos[qid]['nombre'].split(',')[0]}", u["clase"], "int", terr, nivel, pool, ubicacion=u["nombre"], tipo="edificio", cama=bool(cama and u["clase"] == "S"))
        acc = {"puerta": self.rng.choice([0, 0, 0, 1, 2]) if u["clase"] != "S" else self.rng.choice([0, 0, 0, 1]),
               "ventana": self.rng.random() < 0.7, "agujero": self.rng.random() < 0.25, "conducto": self.rng.random() < 0.1}
        self.nodos[zid]["accesos"] = acc
        self.nodos[zid]["cont"] = self._contenedores(self.rng.randint(1, 3), cerr_max=2)
        self._conectar(qid, zid)
        self._conectar(zid, qid)
        nodos.append(zid)

    # ------------------------------------------------------------------ gente
    def _lugar_nodos(self, lugar):
        c = self.por_lugar.get(lugar)
        if not c:
            c = [n for n, d in self.nodos.items() if d["clase"] == "S" and d["tipo"] != "edificio"] or list(self.nodos)
        return c

    def construir_gente(self):
        L = self.L
        ex_ad = set(L.get("excluir_adultos", []))
        ex_ni = set(L.get("excluir_ninos", []))
        nombres_n = list(L["nombres_ninos"])
        self.rng.shuffle(nombres_n)
        nombres_a = list(L["nombres_adultas"])
        self.rng.shuffle(nombres_a)
        usados_n = 0
        incl = dict(adultos=[], ninos=[], resp=[], comps=[])
        for x in self.a["adultos"]:
            if x["lugar"] in ex_ad or any(k in x["rol"] for k in L.get("excluir_roles", [])):
                continue
            nodo = self.rng.choice(self._lugar_nodos(x["lugar"]))
            self.nodos[nodo]["npc"].append(x["id"])
            self.npcs[x["id"]] = dict(nombre=x["id"], arq=x["rol"], loc=nodo, pers=", ".join(x["claves"]), edad="adulto", apariencia=L["reparto"]["adultos"])
            incl["adultos"].append(x["id"])
        for x in self.a["ninos"]:
            if x["lugar"] in ex_ni:
                continue
            nodo = self.rng.choice(self._lugar_nodos(x["lugar"]))
            nombre = nombres_n[usados_n % len(nombres_n)]
            usados_n += 1
            self.nodos[nodo]["npc"].append(x["id"])
            self.npcs[x["id"]] = dict(nombre=nombre, arq=x["rol"], loc=nodo, pers=", ".join(x["claves"]), edad="niño", apariencia=L["reparto"]["ninos"])
            incl["ninos"].append(x["id"])
        for x in self.a["resp"]:
            if x["lugar"] in ex_ad or any(k in x["rol"] for k in L.get("excluir_roles", [])):
                continue
            incl["resp"].append(x["id"])
        for x in L.get("npcs_extra", []):
            nodo = self.ubic[x["ubic"]]["entrada"]
            self.nodos[nodo]["npc"].append(x["id"])
            self.npcs[x["id"]] = dict(nombre=x["id"], arq=x["arq"], loc=nodo, pers=x["pers"], edad=x["edad"], apariencia=x["apariencia"])
            incl["adultos"].append(x["id"])
            self.extras_misiones = getattr(self, "extras_misiones", [])
            self.extras_misiones.append(x)
        # companeros: filtro por tipo de reparto
        for i, x in enumerate(self.a["comps"]):
            if x["rol"].startswith("niño") or x["rol"].startswith("niña"):
                edad = "niño"
            elif x["edad"] == "adulto":
                edad = "adulto"
            else:
                edad = "neutro"
            if edad == "niño" and not L["reparto"].get("ninos_ok", True):
                continue
            if edad == "adulto" and not L["reparto"].get("adultos_ok", True):
                continue
            nombre = (nombres_n[usados_n % len(nombres_n)] if edad == "niño" else nombres_a[i % len(nombres_a)])
            if edad == "niño":
                usados_n += 1
            kid = f"K-{len(self.companeros) + 1}"
            self.companeros[kid] = dict(nombre=nombre, especie="U-02", fase=13, loc=None, aporte="+bonificación de compañero (41)", quest=None, ref=x["id"], edad=edad, personalidad=x["personalidad"], rol=x["rol"])
            incl["comps"].append(x["id"])
        self.incl = incl

    # ------------------------------------------------------------------ misiones
    def _nodo_con(self, terr_id, clase=None, tipo=None, tiene_cont=True):
        cand = [n for n in self.terr_nodos[terr_id] if (not clase or self.nodos[n]["clase"] == clase) and (not tipo or self.nodos[n]["tipo"] == tipo)
                and (not tiene_cont or self.nodos[n]["cont"])]
        return self.rng.choice(cand) if cand else self.rng.choice(self.terr_nodos[terr_id])

    def _objeto_mision(self, nombre, nodo):
        iid = f"obj_{len(self.items_mision) + 1}"
        self.items_mision[iid] = nombre
        self.objetos[iid] = (nombre, "mision", 0)
        cont = self.nodos[nodo]["cont"][self.rng.randrange(len(self.nodos[nodo]["cont"]))]
        cont[4].append(iid)
        return iid

    def _pasos(self, tipo, giver, terr_id, nivel):
        """Convierte el mini-lenguaje de pasos de un tipo en pasos ejecutables."""
        pasos = []
        plantilla = dm.TIPOS[tipo][1]
        hostiles = [n for n in self.terr_nodos[terr_id] if self.nodos[n]["clase"] == "H" and not self.nodos[n].get("jefe")]
        normales = [n for n in self.terr_nodos[terr_id] if self.nodos[n]["clase"] == "N" and self.nodos[n]["pool"] != "civil" and not self.nodos[n].get("jefe")]
        node_hostil = self.rng.choice(hostiles or normales or self.terr_nodos[terr_id])
        node_obj = self._nodo_con(terr_id)
        item = None
        otro = self.rng.choice([n for n in self.npcs if n != giver] or [giver])
        for tok in [t.strip() for t in plantilla.split(";")]:
            partes = tok.split(":")
            op = partes[0]
            if op == "talk":
                pasos.append(("talk", giver if partes[1] == "G" else otro))
            elif op == "get":
                if item is None:
                    item = self._objeto_mision(f"objeto de {self.npcs[giver]['arq']}", node_obj)
                pasos.append(("get", node_obj, item))
            elif op == "give":
                tgt = giver if partes[1] == "G" else otro
                it = item or ("recurso_bio" if partes[2] == "R" else "artefacto")
                pasos.append(("give", tgt, it))
            elif op == "kill":
                pasos.append(("kill", node_hostil, int(partes[2])))
            elif op == "kill_sp":
                pool = self.L["pools"].get(self.nodos[node_hostil]["pool"], [])
                pool = sorted(pool, key=lambda s: SLOT.get(s, 0))
                pasos.append(("kill_species", node_hostil, int(partes[2]), pool[:3] or ["C-03"]))
            elif op == "boss":
                pasos.append(("kill", node_hostil, 3))
            elif op == "hack":
                nodo_t = self._nodo_con(terr_id)
                self.nodos[nodo_t]["terminal"] = True
                pasos.append(("hack", nodo_t))
            elif op == "collect":
                pasos.append(("collect", node_hostil, "recurso_bio", int(partes[2])))
            elif op == "deliver":
                pasos.append(("deliver_msg", otro))
            elif op == "choose":
                pasos.append(("choose", "un bando", "el otro", node_hostil, self.L.get("rival", "U-04")))
            elif op == "craft":
                pasos.append(("craft", "artefacto"))
            elif op == "discover":
                pasos.append(("discover", int(partes[1])))
            elif op == "goto":
                pasos.append(("goto", node_hostil))
        return pasos

    def construir_misiones(self):
        L = self.L
        orden = L["orden_territorios"]
        # jefes de territorio
        for clave, j in L["jefes"].items():
            nodo = self.ubic[j["ubic"]]["entrada"]
            nivel = max(1, self.nodos[nodo]["nivel"])
            self.jefes[clave] = dict(nombre=j["nombre"], loc=nodo, especie=j["especie"], talla="T3", nivel=nivel, pv=40 * nivel + 20,
                                     dano=(int(1.2 * nivel + 6), int(1.8 * nivel + 10)), sub=j["sub"], sub_max=4)
            self.nodos[nodo]["jefe"] = clave
            self.nodos[nodo]["clase"] = "H"
            if self.nodos[nodo]["pool"] == "civil":
                self.nodos[nodo]["pool"] = j.get("pool", self.L["territorios"][0]["pool"])
        # 1) misiones propias de cada NPC (1 a 5)
        incl_ad = set(self.incl["adultos"])
        incl_ni = set(self.incl["ninos"])
        for x in self.a["adultos"] + self.a["ninos"]:
            if x["id"] not in incl_ad and x["id"] not in incl_ni:
                continue
            nodo = self.npcs[x["id"]]["loc"]
            terr_id = next(t for t, ns in self.terr_nodos.items() if nodo in ns)
            nivel = max(1, self.nodos[nodo]["nivel"])
            for m in x["misiones"]:
                qid = f"Q{m['id'][1:]}"
                pasos = self._pasos(m["tipo"], x["id"], terr_id, nivel)
                nivel_q = max(1, min(30, nivel + self.rng.randint(0, 2)))
                self.quests[qid] = dict(nombre=m["nombre"], tipo="secundaria", giver=x["id"], nivel=nivel_q, desc=dm.TIPOS[m["tipo"]][0], steps=pasos,
                                        xp=60 + 14 * nivel_q, rec=[self.rng.choice(["venda", "lata", "agua", "cuñas30", "cuñas50", "medicina"])], tq=m["tipo"])
        for x in getattr(self, "extras_misiones", []):
            nodo = self.npcs[x["id"]]["loc"]
            terr_id = next(t for t, ns in self.terr_nodos.items() if nodo in ns)
            nivel = max(1, self.nodos[nodo]["nivel"])
            for k, tq in enumerate(x["misiones"], 1):
                nombre = dm.nombre_mision(self.rng, tq, [x["pers"].split(",")[0]])
                self.quests[f"Q{x['id']}-{k}"] = dict(nombre=nombre, tipo="secundaria", giver=x["id"], nivel=nivel, desc=dm.TIPOS[tq][0], steps=self._pasos(tq, x["id"], terr_id, nivel),
                                                      xp=60 + 14 * nivel, rec=["venda_reforzada"], tq=tq)
        # 2) misiones base secundarias (45) y principales (15) instanciadas
        givers = [n for n in self.npcs]
        for i, (mid, nombre, tipo, idea, ramas) in enumerate(dm.SECUNDARIAS, 1):
            terr_id = orden[i % len(orden)]
            g = self.rng.choice([n for n in givers if self.npcs[n]["loc"] in self.terr_nodos[terr_id]] or givers)
            nivel = max(1, self.nodos[self.npcs[g]["loc"]]["nivel"])
            self.quests[mid] = dict(nombre=nombre, tipo="secundaria", giver=g, nivel=nivel, desc=idea, steps=self._pasos(tipo, g, terr_id, nivel),
                                    xp=60 + 14 * nivel, rec=["medicina"], tq=tipo)
        self.principales = []
        n_t = len(orden)
        for i, (mid, nombre, tipo, idea, ramas) in enumerate(dm.PRINCIPALES):
            terr_id = orden[min(n_t - 1, i * n_t // len(dm.PRINCIPALES))]
            g = self.rng.choice([n for n in givers if self.npcs[n]["loc"] in self.terr_nodos[terr_id]] or givers)
            lo, hi = next(t["nivel"] for t in L["territorios"] if t["id"] == terr_id)
            nivel = max(1, min(30, lo + (hi - lo) * (i % max(1, 15 // n_t + 1)) // max(1, 15 // n_t + 1)))
            nivel = max(1, min(30, int(1 + 29 * i / 14)))
            nivel = max(lo, min(hi, nivel)) if i not in (0,) else 1
            pasos = self._pasos(tipo, g, terr_id, nivel)
            self.quests[mid] = dict(nombre=nombre, tipo="principal", giver=g, nivel=nivel, desc=idea, steps=pasos, xp=150 + 140 * nivel, rec=["medicina"], tq=tipo)
            self.principales.append(mid)
        # el primer giver de la principal 1 es el companero inicial / vecino del inicio
        # misiones de jefe: cada jefe se vuelve una mision secundaria con paso boss
        for k, (clave, j) in enumerate(self.jefes.items(), 1):
            g = self.rng.choice(list(self.npcs))
            self.quests[f"MJ-{k:02d}"] = dict(nombre=f"Cuidado con {j['nombre']}", tipo="secundaria", giver=g, nivel=j["nivel"], desc="Vencer a un jefe de territorio",
                                              steps=[("talk", g), ("boss", j["loc"], clave), ("talk", g)], xp=200 + 20 * j["nivel"], rec=["venda_reforzada"], tq="JEF")

    # ------------------------------------------------------------------ exportar
    def exportar(self):
        L = self.L
        ini = self.ubic[L["protagonista"]["inicio"]]
        hogar = ini["entrada"]
        self.nodos[hogar]["cama"] = True
        self.nodos[hogar]["ventana"] = True
        self.nodos[hogar]["clase"] = "S"
        self.nodos[hogar]["pool"] = "civil"
        # camas: al menos una por territorio
        for tid, ns in self.terr_nodos.items():
            if not any(self.nodos[n]["cama"] for n in ns):
                seguros = [n for n in ns if self.nodos[n]["clase"] == "S"] or ns
                self.nodos[seguros[0]]["cama"] = True
        # companeros: los ponemos en nodos seguros
        comp_ini_id = next((k for k, c in self.companeros.items() if c["edad"] == "niño"), None)
        seguros_ub = [n for n, d in self.nodos.items() if d["clase"] == "S" and d["tipo"] == "cuadra"] or [n for n, d in self.nodos.items() if d["clase"] == "S"]
        for kid, c in self.companeros.items():
            c["loc"] = hogar if kid == comp_ini_id else self.rng.choice(seguros_ub)
        for tier, valor in ((2, 30), (3, 80), (4, 200), (5, 600)):
            self.objetos[f"arma_t{tier}"] = (L["armas"][tier][0], "arma", valor)
        self.objetos["armadura_e2"] = ("Chaleco reforzado de lona", "equipo", 20)
        self.objetos["armadura_e4"] = ("Armadura ligera de explorador", "equipo", 180)
        self.objetos["armadura_e5"] = ("Armadura del guardián", "equipo", 500)
        pools = dict(self.L["pools"])
        pools["civil"] = []
        armas = L["armas"]
        nombres = {k: v[0] for k, v in armas.items()}
        principales = self.principales
        quests = self.quests
        # companero inicial
        comp_ini = None
        for kid, c in self.companeros.items():
            if c["edad"] == "niño":
                comp_ini = kid
                break
        tiendas = tuple(n for n, d in self.nodos.items() if d["clase"] == "S" and d["tipo"] != "edificio")[:8]
        return dict(
            MONEDA=L["moneda"], PROTAGONISTA=dict(nombre=L["protagonista"]["nombre"], hogar=hogar, edad=L["protagonista"]["edad"], stats=L["protagonista"]["stats"]),
            POOLS=pools, LOCS=self.nodos, NPCS=self.npcs, COMPANEROS=self.companeros, QUESTS=quests, JEFES=self.jefes, OBJETOS=self.objetos,
            ARMAS=armas, ARMADURAS=ARMADURAS, PRINCIPALES=principales, TIENDAS=tiendas, TIENDA_ARMAS=tiendas[0] if tiendas else hogar,
            BANCOS=(hogar,), ZONA_CARNE=hogar, ZONAS_RECURSO=(hogar,), TERMINALES={}, COMP_AL_DESPEJAR={}, COMPANERO_INICIAL=comp_ini, POSTJUEGO=None,
        )


def construir(lore, semilla=2026):
    c = Constructor(lore, semilla)
    c.construir_ubicaciones()
    c.construir_gente()
    c.construir_misiones()
    mundo = c.exportar()
    return mundo, c
