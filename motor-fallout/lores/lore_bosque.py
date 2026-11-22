"""LORE A: «El Bosque de los Mil Senderos» (exploradores niños, adultas mujeres, alfas amistosos)."""


def S(id, nombre, clase="N", espacio="ext", lugares=(), **kw):
    return dict(id=id, nombre=nombre, kind="s", clase=clase, espacio=espacio, lugares=list(lugares), **kw)


def P(id, nombre, cuadras, clase="S", lugares=(), **kw):
    return dict(id=id, nombre=nombre, kind="p", cuadras=cuadras, clase=clase, espacio="ext", lugares=list(lugares), **kw)


def C(id, nombre, barrios, clase="S", lugares=(), **kw):
    return dict(id=id, nombre=nombre, kind="c", barrios=barrios, clase=clase, espacio="ext", lugares=list(lugares), **kw)


LORE = dict(
    id="bosque", nombre="El Bosque de los Mil Senderos", moneda="bellotas",
    tono="aventura luminosa tipo cuento de exploradores: amistad, mapas, fogatas y deberes; peligro de criaturas, sin crueldad ni muerte",
    protagonista=dict(nombre="Lucas", edad="niño", inicio="a01", stats={"FUE": 5, "PER": 6, "RES": 6, "CAR": 6, "INT": 5, "AGI": 5, "SUE": 5}),
    armas={1: ("Palo de práctica", 6, 10), 2: ("Bastón de roble", 7, 11), 3: ("Bastón reforzado", 10, 16), 4: ("Lanza de exploradores (punta roma)", 12, 18), 5: ("Cayado del Roble Mayor", 16, 26)},
    reparto=dict(adultos="femenina", ninos="masculina", excepciones=[("T14 alfa", "masculina")], grupos_separados=True, adultos_ok=True, ninos_ok=True),
    temas={"T1 animales": [1, 2, 3], "T14 alfa": [1, 2, 3]},
    excluir_adultos=["HOS", "PUE"], excluir_ninos=["HOS", "PUE"],
    excluir_roles=["esclavista", "cautivo", "cultista", "cultos", "culto", "saqueador", "bandido", "contrabandista", "mercenari", "francotirador", "prisionero", "capataz de campamento", "traficante", "pandilla", "alcohol", "apostador", "casino", "crupier", "cantinero", "tabernero", "prestamista", "cobrador"],
    rival="U-04",
    pools={
        "bosque": ["C-03", "C-05", "C-09", "H-12", "H-13", "H-15", "H-16", "H-30", "H-33", "H-34", "I-01", "I-03", "I-05", "I-11", "I-15", "I-25", "S-01", "S-12"],
        "pantano": ["M-01", "M-07", "M-11", "M-16", "P-04", "P-05", "S-18", "S-01", "S-02", "I-12", "I-17"],
        "ciudad": ["C-02", "C-04", "H-02", "H-12", "I-16", "I-19", "S-01"],
        "campos": ["H-19", "H-20", "H-21", "H-28", "H-30", "H-33", "C-11", "C-18", "I-14", "I-26", "I-04"],
        "selva": ["I-23", "I-24", "I-27", "I-28", "I-26", "H-43", "H-44", "C-05", "M-17"],
        "alfa": ["C-18", "C-19", "H-16", "H-29", "H-31", "I-27"],
        "montana": ["C-14", "C-19", "C-20", "H-23", "H-29", "H-17", "I-27", "S-10"],
    },
    edificios=[("Cabaña de exploradores", [], True), ("Kiosco", [], False), ("Almacén de barrio", [], False), ("Heladería", [], False), ("Panadería", [], False),
               ("Casa de familia", [], False), ("Taller de bicicletas", [], False), ("Biblioteca", [], False), ("Escuela de oficios", [], False), ("Enfermería", [], True),
               ("Posada", [], True), ("Mercado cubierto", [], False), ("Herrería", [], False), ("Carpintería", [], False), ("Sala de mapas", [], False), ("Estanco", [], False)],
    orden_territorios=["T-BOS", "T-PAN", "T-CIU", "T-CAM", "T-SEL", "T-ALF", "T-MON"],
    territorios=[
        dict(id="T-BOS", nombre="El Bosque Hondo", pos="sur (centro)", formacion="bosque cerrado", clima="templado húmedo", relieve="colinas", agua="arroyos", mod="fértil", nivel=(1, 8), pool="bosque",
             ubicaciones=[
                 P("a01", "Claro del Roble Partido", 3, lugares=["REF", "ASE"], cama=True),
                 S("a02", "Senda de los Helechos", lugares=["CAM"]), S("a03", "Arroyo de las Piedras Lisas", lugares=["CAM"]),
                 P("a04", "Árbol Mayor", 2, lugares=["TOR", "ASE"], cama=True), S("a05", "Cueva del Murmullo", espacio="int", lugares=["SUB", "ESP"]),
                 S("a06", "Puente Colgante de la Garza", lugares=["CAM"]), S("a07", "Mirador del Halcón", lugares=["CAM", "MIL"]),
                 S("a08", "Cabaña del Ermitaño", espacio="int", lugares=["ESP"]), S("a09", "Bosque de Niebla", lugares=["CAM", "ESP"]),
                 S("a10", "Hondonada del Zorzal", lugares=["CAM"]), S("a11", "Colmena de las Mantis", clase="H", espacio="int"),
                 S("a12", "Refugio de los Vigías", clase="S", lugares=["MIL"], cama=True)]),
        dict(id="T-PAN", nombre="El Pantano del Extremo Sur", pos="sur (punta)", formacion="humedal", clima="templado húmedo", relieve="islas", agua="pantano", mod="pantanoso", nivel=(4, 12), pool="pantano",
             ubicaciones=[
                 P("b01", "Palafitos del Cañaveral", 3, lugares=["ASE"], cama=True), S("b02", "Camino de Tablones", lugares=["CAM"]), S("b03", "Laguna Turbia", lugares=["CAM"]),
                 S("b04", "Isla de los Juncos", lugares=["CAM", "ESP"]), S("b05", "Cueva del Fango", clase="H", espacio="int"), S("b06", "Mirador del Cañaveral", lugares=["CAM", "MIL"]),
                 S("b07", "Puesto de los Rastreadores", clase="S", lugares=["MIL"], cama=True), S("b08", "Nido de la Madre del Fango", clase="H", espacio="int")]),
        dict(id="T-CIU", nombre="Ciudad Esperanza", pos="oeste (centro)", formacion="bosque abierto urbano", clima="templado", relieve="llanura", agua="arroyos y canales", mod="fértil", nivel=(5, 14), pool="ciudad",
             ubicaciones=[
                 C("c01", "Ciudad Esperanza", [("Plaza Mayor", 3), ("Barrio del Mercado", 4), ("Barrio de las Escuelas", 3), ("Barrio Viejo", 3), ("Barrio de los Talleres", 3), ("Barrio del Parque", 3)],
                   lugares=["ASE", "COM", "IND", "CIE"]),
                 S("c02", "Muralla y Puertas", clase="S", lugares=["MIL"]), S("c03", "Torre de las Campanas", clase="S", espacio="int", lugares=["TOR", "CIE"]),
                 S("c04", "Alcantarillas", clase="H", espacio="int"), S("c05", "Parque de los Faroles", lugares=["CAM", "ESP"]), S("c06", "Biblioteca Vieja", espacio="int", lugares=["ESP", "ASE"]),
                 S("c07", "Taller de los Inventores", clase="S", espacio="int", lugares=["IND", "CIE"]), S("c08", "Casa de las Hojas", clase="S", espacio="int", lugares=["ASE"], cama=True)]),
        dict(id="T-CAM", nombre="Los Campos", pos="noroeste", formacion="bosque de sabana", clima="templado seco", relieve="llanura", agua="arroyos", mod="fértil", nivel=(8, 18), pool="campos",
             ubicaciones=[
                 P("d01", "Aldea de la Cosecha", 4, lugares=["IND", "ASE"], cama=True), S("d02", "Granja de las Tres Acequias", clase="S", lugares=["IND"]), S("d03", "Molino Alto", clase="S", espacio="int", lugares=["IND"]),
                 S("d04", "Establo Comunal", clase="S", espacio="int", lugares=["IND"]), S("d05", "Colinas del Trigo", lugares=["CAM"]), S("d06", "Corral Roto", clase="H"),
                 S("d07", "Espantapájaros Viejo", lugares=["CAM"]), S("d08", "Nido de la Matriarca de las Avispas", clase="H", espacio="int"), S("d09", "Camino de las Carretas", lugares=["CAM"])]),
        dict(id="T-SEL", nombre="Las Selvas del Comercio", pos="este (centro, al este de la ciudad)", formacion="selva", clima="templado húmedo", relieve="colinas", agua="río y arroyos", mod="florecido", nivel=(12, 22), pool="selva",
             ubicaciones=[
                 P("e01", "Mercado de las Lonas", 4, lugares=["COM", "ASE"], cama=True), S("e02", "Selva de los Mercaderes", lugares=["CAM"]), S("e03", "Sendero de las Carretas", lugares=["CAM"]),
                 S("e04", "Posada de los Cuatro Vientos", clase="S", espacio="int", lugares=["COM", "ASE"], cama=True), S("e05", "Campamento de Caravanas", clase="S", lugares=["CAM", "COM"]),
                 S("e06", "Selva Cerrada", clase="H"), S("e07", "Puente del Comercio", lugares=["CAM"]), S("e08", "Claro de la Soberana", clase="H")]),
        dict(id="T-ALF", nombre="El Territorio Alfa", pos="noreste (al este de los campos)", formacion="bosque de cañones", clima="semiárido", relieve="cañones", agua="arroyos secos", mod="rocoso", nivel=(16, 26), pool="alfa",
             ubicaciones=[
                 P("f01", "Aldea de las Casas Grandes", 4, lugares=["ESP", "ASE"], cama=True), S("f02", "Cañón de los Ecos", lugares=["CAM"]), S("f03", "Meseta del Viento", lugares=["CAM", "ESP"]),
                 S("f04", "Bosque Alto", lugares=["CAM"]), S("f05", "Tótem de las Cumbres", lugares=["ESP"]), S("f06", "Paso del Eco", lugares=["CAM"]), S("f07", "Refugio de Piedra", clase="S", espacio="int", lugares=["ESP"], cama=True)]),
        dict(id="T-MON", nombre="Las Montañas del Norte", pos="norte (toda la punta)", formacion="bosque nevado", clima="boreal", relieve="montaña", agua="nieve y arroyos helados", mod="nevado", nivel=(20, 30), pool="montana",
             ubicaciones=[
                 S("g01", "Refugio de la Cumbre", clase="S", espacio="int", lugares=["ESP", "MIL"], cama=True), S("g02", "Paso Blanco", lugares=["CAM"]), S("g03", "Aserradero Nevado", lugares=["IND"]),
                 S("g04", "Mirador de las Nubes", lugares=["CAM"]), S("g05", "Sendero del Cóndor", lugares=["CAM"]), S("g06", "Cueva de Hielo", clase="H", espacio="int"),
                 S("g07", "Valle Escondido", clase="S", lugares=["ESP"], cama=True), S("g08", "Cima Antigua", clase="H")]),
    ],
    enlaces=[("a01", "b01"), ("a04", "c02"), ("a12", "b07"), ("c01", "d01"), ("c01", "e01"), ("c02", "e07"), ("d01", "f01"), ("d09", "g02"), ("f06", "g02"), ("e03", "f02"), ("a10", "e02"), ("g01", "f07")],
    jefes={
        "reina_mantis": dict(nombre="Reina Mantis", ubic="a11", especie="I-15", sub="I-15"),
        "madre_fango": dict(nombre="Madre del Fango", ubic="b08", especie="S-13", sub="S-01"),
        "matriarca_avispas": dict(nombre="Matriarca de las Avispas", ubic="d08", especie="I-04", sub="I-03"),
        "soberana_selva": dict(nombre="Soberana de las Selvas", ubic="e08", especie="I-26", sub="I-23"),
        "gran_loba": dict(nombre="Gran Loba del Norte", ubic="g08", especie="C-18", sub="C-19"),
    },
    nombres_ninos=["Tobías", "Lucho", "Bruno", "Mateo", "Joaquín", "Emilio", "Santi", "Nacho", "Gael", "Thiago", "Ciro", "León", "Bautista", "Dante", "Facu", "Ian", "Lisandro", "Octavio",
                   "Pablo", "Rodri", "Simón", "Teo", "Uriel", "Valen", "Zoilo", "Abel", "Benja", "Camilo", "Damián", "Elián", "Franco", "Gonza", "Hugo", "Isaías", "Jerónimo", "Kevin",
                   "Leo", "Manu", "Noel", "Óscar", "Pedro", "Quimey", "Ramiro", "Saúl", "Tomi", "Ulises", "Vicente", "Walter", "Ximo", "Yago", "Zair", "Alan", "Bastián", "Cristian",
                   "Dylan", "Erik", "Fabián", "Genaro", "Horacio", "Iñaki", "Julián", "Kai", "Lautaro", "Marcos", "Nahuel", "Orlando", "Patricio", "Renzo", "Sebas", "Tadeo", "Urbano",
                   "Valentín", "Wenceslao", "Yeray", "Zacarías", "Amadeo", "Baltasar", "Ciriaco", "Demian", "Ezequiel", "Fermín", "Gerardo", "Herminio", "Ismael", "Jonás", "Lorenzo",
                   "Maximiliano", "Nicanor", "Olivier", "Prudencio", "Rubén", "Silvestre"],
    nombres_adultas=["Ayelén", "Brisa", "Celeste", "Dolores", "Elena", "Fiorella", "Gala", "Irene", "Julia", "Lucía", "Mora", "Nadia", "Olivia", "Paloma", "Rocío", "Sofía", "Tamara", "Valeria",
                     "Wanda", "Ximena", "Yamila", "Zulema", "Abril", "Belén", "Carla", "Delfina", "Emma", "Federica", "Guadalupe", "Helena", "Inés", "Jazmín", "Karina", "Laura", "Marina", "Noelia"],
    facciones=[
        ("Los Exploradores del Roble", "infantil", "protectores, curiosos, de reglas simples", "El Bosque Hondo"), ("Los Vigías del Mirador", "infantil", "atentos y silenciosos", "El Bosque Hondo"),
        ("La Banda del Arroyo", "infantil (rival, no letal)", "bravucones juguetones", "El Bosque Hondo"), ("Los Cartógrafos del Claro", "infantil", "meticulosos, soñadores", "El Bosque Hondo"),
        ("Los Rastreadores del Cañaveral", "infantil", "callados y resistentes", "El Pantano del Extremo Sur"), ("Los Constructores de la Ciudad", "infantil", "ingeniosos", "Ciudad Esperanza"),
        ("Los Recaderos de la Plaza", "infantil", "veloces y chismosos", "Ciudad Esperanza"), ("Los Cosechadores", "infantil", "trabajadores y alegres", "Los Campos"),
        ("Los Aprendices del Comercio", "infantil", "regateadores curiosos", "Las Selvas del Comercio"), ("Los Cazadores del Alba", "infantil", "disciplinados", "Las Montañas del Norte"),
        ("La Casa de las Hojas", "mujeres adultas", "cuidadoras, pacientes", "El Bosque Hondo"), ("Las Guardianas del Camino", "mujeres adultas", "justas y firmes", "Todo el mapa"),
        ("El Gremio de las Sembradoras", "mujeres adultas", "prácticas y generosas", "Los Campos"), ("Las Hermanas de la Ciudad", "mujeres adultas", "organizadas y diplomáticas", "Ciudad Esperanza"),
        ("La Compañía de las Mercaderas", "mujeres adultas", "astutas y cordiales", "Las Selvas del Comercio"), ("Las Curanderas del Pantano", "mujeres adultas", "sabias y reservadas", "El Pantano del Extremo Sur"),
        ("Los Alfas del Este", "gigantes amistosos (varones, adultos)", "territoriales y respetuosos", "El Territorio Alfa"),
    ],
)

# NPC propios del lore (no vienen de los catalogos): alfas amistosos, varones adultos (unica excepcion de apariencia masculina)
LORE["npcs_extra"] = [
    dict(id="ALF-1", arq="alfa de fase 1 (gigante amistoso de las alturas)", ubic="f05", pers="territorial, solemne, respetuoso", edad="adulto", apariencia="masculina", misiones=["ESC", "PUZ"]),
    dict(id="ALF-2", arq="alfa de fase 2 (gigante amistoso de los campos del oeste)", ubic="f01", pers="sociable, protector, curioso", edad="adulto", apariencia="masculina", misiones=["NEG", "RCL", "DEF"]),
    dict(id="ALF-3", arq="alfa de fase 3 (el más humano, mediador)", ubic="f03", pers="sereno, hablador, amable", edad="adulto", apariencia="masculina", misiones=["NEG", "MSJ"]),
]
