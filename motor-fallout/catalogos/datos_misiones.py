"""Tipos de mision, misiones base (principales y secundarias) y generador de nombres.

Los pasos usan un mini-lenguaje que el constructor de mundos convierte en pasos ejecutables:
  talk:G  get:L:I  give:G:I  kill:L:n  kill_sp:L:n  boss:L  hack:L  collect:L:n  deliver:O  choose:L
  craft:I  discover:n  goto:L  recruit:K   (G=quien da la mision, O=otro NPC, L=lugar, I=objeto, K=companero)
"""

# codigo: (nombre, pasos, descripcion de los pasos, patrones de nombre, objetos tipicos)
TIPOS = {
    "REC": ("Recuperar un objeto perdido", "talk:G; get:L:I; give:G:I", "hablar, buscar el objeto en un lugar, devolverlo",
            ["Devolver {obj}", "Rastro de {obj}", "Lo que se llevó {sust}", "En busca de {obj}"], ["la llave", "la herramienta", "la carta", "la reliquia", "la medalla", "la brújula", "el cuaderno", "el mapa"]),
    "AMN": ("Eliminar una amenaza", "talk:G; kill:L:3; talk:G", "hablar, derrotar un grupo, avisar", ["Limpiar el {lug}", "Cuando no alcanza {sust}", "Guardia contra {amen}", "Paz para el {lug}"], ["nido", "manada", "enjambre", "banda"]),
    "RSC": ("Rescate", "talk:G; goto:L; kill:L:2; talk:G", "hablar, ir al lugar, despejar y volver", ["Rescate en el {lug}", "Atrapado por {amen}", "La salida del {lug}", "No dejar a nadie atrás"], ["persona atrapada"]),
    "ESC": ("Escolta", "talk:G; goto:L; kill:L:2", "hablar, acompañar hasta el destino, defender", ["Escolta hasta el {lug}", "El camino seguro", "Compañía para {sust}", "Cruzar con cuidado"], ["caravana", "viajero"]),
    "MSJ": ("Mensajería", "talk:G; deliver:O; talk:G", "hablar, llevar el mensaje, volver", ["Entrega urgente", "Un mensaje para {sust}", "Cartas sin dueño", "Lo que no se dijo a tiempo"], ["carta", "paquete"]),
    "INV": ("Investigar", "talk:G; get:L:I; talk:G", "hablar, hallar la pista, informar", ["El misterio del {lug}", "Pistas de {sust}", "Qué pasó en el {lug}", "Ruido en la noche"], ["pista", "registro", "huella"]),
    "HCK": ("Reactivar o hackear un sistema", "talk:G; hack:L", "hablar, hackear el terminal", ["Voz del {lug}", "La máquina que no responde", "Reiniciar el {lug}", "Código de {sust}"], ["terminal", "bomba", "radio"]),
    "RCL": ("Recolectar recursos", "talk:G; collect:L:3; give:G:R", "hablar, recolectar, entregar", ["Material para {sust}", "Provisión del {lug}", "Todo lo que se junta", "Faltan {obj}"], ["recursos", "materiales", "provisiones"]),
    "CAZ": ("Cazar una especie", "talk:G; kill_sp:L:3; talk:G", "hablar, cazar la especie, volver", ["Cacería en el {lug}", "Tras la presa de {sust}", "El trofeo de {sust}", "La presa del {lug}"], ["presa", "trofeo"]),
    "BND": ("Elegir bando", "talk:G; choose:L; kill:L:2", "hablar, elegir con quién ir, derrotar al otro grupo", ["Dos caminos en el {lug}", "A quién creerle", "La balanza de {sust}", "Con unos o con otros"], ["acuerdo", "disputa"]),
    "FAB": ("Fabricar o reparar", "talk:G; craft:I; give:G:I", "hablar, fabricar, entregar", ["El invento de {sust}", "Reparación en el {lug}", "Manos a la obra", "Algo que funcione"], ["artefacto", "radio", "repuesto"]),
    "EXP": ("Explorar y descubrir", "talk:G; discover:4; talk:G", "hablar, descubrir lugares, informar", ["Mapa del {lug}", "Más allá del {lug}", "Rutas nuevas", "Curiosidad de {sust}"], ["mapa"]),
    "JEF": ("Vencer a un jefe", "talk:G; boss:L; talk:G", "hablar, vencer al jefe, volver", ["El jefe del {lug}", "Sombra sobre el {lug}", "Lo que vive en el {lug}", "Última guardia"], ["jefe"]),
    "INF": ("Infiltrarse y sigilo", "talk:G; get:L:I; talk:G", "hablar, entrar sin ser visto, tomar el objeto", ["Sin ser vistos", "Entrar por la ventana", "El cofre del {lug}", "En silencio"], ["documento", "llave", "cofre"]),
    "NEG": ("Negociar y mediar", "talk:G; talk:O; talk:G", "hablar con las dos partes", ["Palabras en el {lug}", "Una mesa para {sust}", "Mediación", "Paz a medias"], ["acuerdo"]),
    "DEF": ("Defender un lugar", "talk:G; kill:L:4; talk:G", "hablar, resistir oleadas, volver", ["Resistir en el {lug}", "Noche de guardia", "La muralla de {sust}", "Defender lo propio"], ["oleada"]),
    "LMP": ("Limpiar un edificio", "talk:G; kill:L:3; get:L:I", "hablar, despejar y registrar", ["Casa vacía", "Desalojo del {lug}", "Limpieza total", "Lo que quedó adentro"], ["llave"]),
    "PUZ": ("Acertijo o secreto", "talk:G; get:L:I; hack:L", "hablar, hallar pista, resolver el mecanismo", ["El acertijo del {lug}", "Puertas que no abren", "Secreto de {sust}", "Letras en la pared"], ["pista", "código"]),
    "COM": ("Encargo de comercio", "talk:G; get:L:I; give:G:I", "hablar, conseguir la mercancía, entregar", ["Pedido especial", "Mercancía para {sust}", "Negocio en el {lug}", "Un buen trato"], ["mercancía", "carga"]),
    "MED": ("Curar o tratar", "talk:G; collect:L:3; give:G:R", "hablar, conseguir ingredientes, entregar", ["Remedio para {sust}", "Cura en el {lug}", "Manos que sanan", "Antes del amanecer"], ["recurso biológico", "medicina"]),
    "DOM": ("Ayudar a una criatura", "talk:G; goto:L; talk:G", "hablar, encontrar a la criatura, calmarla", ["Compañero perdido", "Criatura herida", "Confianza en el {lug}", "Mirada de {sust}"], ["mascota"]),
    "CON": ("Construir o mejorar", "talk:G; craft:I; give:G:I", "hablar, fabricar la pieza, entregarla", ["Una mano para el {lug}", "Piezas para {sust}", "Construir juntos", "Antena y cable"], ["pieza", "marco", "antena"]),
    "SAB": ("Sabotear", "talk:G; hack:L; get:L:I", "hablar, desactivar el sistema, tomar la pieza", ["Apagón en el {lug}", "Cortar la señal", "Lo que sostiene a {sust}", "Fuera de servicio"], ["pieza"]),
    "VIG": ("Patrullar y vigilar", "talk:G; goto:L; kill:L:2", "hablar, recorrer el puesto, expulsar intrusos", ["Ronda por el {lug}", "Ojos abiertos", "Puesto de {sust}", "Turno de noche"], ["ronda"]),
    "FIE": ("Evento o concurso", "talk:G; get:L:I; give:G:I", "hablar, reunir lo pedido, participar", ["Fiesta del {lug}", "El concurso de {sust}", "Día de feria", "Premio inesperado"], ["premio", "ingrediente"]),
    "ENS": ("Enseñar o aprender", "talk:G; get:L:I; talk:G", "hablar, conseguir un libro, leerlo con quien enseña", ["Lección en el {lug}", "Libros que faltan", "Aprender con {sust}", "Letras y cuentas"], ["libro"]),
    "CTR": ("Contrabando", "talk:G; get:L:I; give:O:I", "hablar, mover la carga sin ser visto, entregarla", ["Carga callada", "Negocio de noche", "Lo que no se declara", "Cruce discreto"], ["carga"]),
    "DET": ("Descubrir al culpable", "talk:G; get:L:I; talk:O", "hablar, juntar pruebas, confrontar", ["¿Quién fue?", "Pruebas del {lug}", "La sombra de {sust}", "Caso sin cerrar"], ["prueba"]),
    "FAM": ("Reunir o buscar a alguien", "talk:G; goto:L; kill:L:2; talk:G", "hablar, buscar, proteger y reunir", ["Volver a casa", "Buscando a alguien", "Sin noticias", "El camino de vuelta"], ["persona"]),
    "COB": ("Deudas", "talk:G; get:L:I; give:O:I", "hablar, conseguir el pago, entregar", ["Cuentas pendientes", "Lo que se debe", "Pagar con tiempo", "Un favor por otro"], ["pago"]),
    "TRA": ("Transportar una carga", "talk:G; get:L:I; deliver:O", "hablar, recoger la carga, entregarla", ["Carga hasta el {lug}", "Sobre ruedas", "Entrega pesada", "Camino largo"], ["carga"]),
    "CUR": ("Antídoto o cura", "talk:G; collect:L:3; give:G:R", "hablar, recolectar, entregar la cura", ["Contra el veneno", "Una dosis a tiempo", "Fiebre en el {lug}", "Respirar de nuevo"], ["antídoto"]),
    "MAP": ("Cartografiar", "talk:G; discover:3; talk:G", "hablar, recorrer y anotar", ["Hoja en blanco", "Los bordes del mapa", "Dibujar el {lug}", "Tinta y senderos"], ["mapa"]),
    "ART": ("Hallar un artefacto único", "talk:G; get:L:I; give:G:I", "hablar, descubrir y traer el artefacto", ["Lo que brilla en el {lug}", "Artefacto de {sust}", "Pieza única", "Tesoro con condición"], ["artefacto"]),
}

# sustantivos asociados a rasgos de personalidad (para nombres de mision)
SUST = {
    "autoritari": "la autoridad", "cansad": "el cansancio", "curios": "la curiosidad", "codici": "la codicia", "charlat": "la palabra",
    "miedos": "el miedo", "valien": "la valentía", "terc": "la terquedad", "nostálgic": "el recuerdo", "generos": "la generosidad",
    "manda": "el mando", "astut": "la astucia", "paciente": "la paciencia", "orgullos": "el orgullo", "sarcást": "la ironía",
    "ingenios": "el ingenio", "obsesiv": "la obsesión", "distraíd": "la distracción", "brillant": "el genio", "culposo": "la culpa",
    "protector": "la protección", "alegre": "la alegría", "supersticios": "la superstición", "bravuc": "la bravuconería", "cruel": "la crueldad",
    "leal": "la lealtad", "fanátic": "la fe", "callad": "el silencio", "desconfi": "la desconfianza", "sabi": "la sabiduría",
    "ingenu": "la ingenuidad", "nervios": "los nervios", "solitari": "la soledad", "creativ": "la creatividad", "frío": "la frialdad",
    "dulce": "la ternura", "tímid": "la timidez", "ambicios": "la ambición", "estricto": "el orden", "bondados": "la bondad",
}
LUGARES = ["pueblo", "camino", "refugio", "taller", "mercado", "puente", "bosque", "pozo", "muelle", "puesto", "granero", "viejo túnel"]
AMEN = ["los intrusos", "los saqueadores", "las alimañas", "la plaga", "las sombras", "los ladrones de camino"]


def sustantivo(claves):
    for c in claves:
        for k, v in SUST.items():
            if k in c:
                return v
    return "la esperanza"


def nombre_mision(rng, tipo, claves):
    pats = TIPOS[tipo][3]
    objs = TIPOS[tipo][4]
    p = rng.choice(pats)
    return (p.replace("{obj}", rng.choice(objs)).replace("{sust}", sustantivo(claves)).replace("{lug}", rng.choice(LUGARES))
            .replace("{amen}", rng.choice(AMEN))).strip().replace(" de el ", " del ").replace(" a el ", " al ").capitalize()


# ---------------------------------------------------------------- misiones base
# (id, nombre generico, tipo, idea, ramas)
PRINCIPALES = [
    ("MP-01", "Salir del hogar", "ESC", "El protagonista debe dejar su lugar seguro por una situación que lo obliga; aprende lo básico y sale al exterior.", "—"),
    ("MP-02", "Tras el rastro de un familiar", "FAM", "Un familiar desapareció dejando huellas; seguirlas hasta el primer gran asentamiento.", "—"),
    ("MP-03", "La voz de la radio", "HCK", "Una emisora comunitaria necesita ayuda; reactivarla abre contactos con toda la región.", "ayudar o ignorar al emisor"),
    ("MP-04", "El conocimiento perdido", "INV", "Buscar a quien sabía del proyecto del familiar; reunir tres pistas.", "—"),
    ("MP-05", "Un lugar dentro de la máquina", "PUZ", "Entrar en un sistema o mundo simulado y resolver su acertijo para obtener el dato clave.", "—"),
    ("MP-06", "Las aguas de la vida", "ART", "Hallar el componente de un purificador o fuente de vida para que todos tengan agua limpia.", "—"),
    ("MP-07", "Retomar el rastro", "INV", "Con el dato, seguir la pista del familiar hasta un campamento.", "—"),
    ("MP-08", "Rescate del familiar", "JEF", "Rescatar al familiar de un campamento hostil venciendo a su jefe.", "pelear o negociar"),
    ("MP-09", "La semilla del jardín", "ART", "Recuperar un dispositivo para crear vida y fertilidad.", "—"),
    ("MP-10", "La orden y la elección", "BND", "Una facción organizada pide ayuda; hay que elegir con quién ir.", "dos facciones"),
    ("MP-11", "Hasta la instalación", "LMP", "Abrirse paso en una instalación que guarda el siguiente paso.", "—"),
    ("MP-12", "El camino a la fuente", "ESC", "Escoltar el aparato y a quienes lo necesitan hasta el lugar final.", "—"),
    ("MP-13", "Tres tareas para encenderla", "HCK", "Despejar, hackear y reunir la pieza para reactivar la fuente.", "—"),
    ("MP-14", "La decisión final", "BND", "Quién controla la fuente: hay que elegir a quién ayudar y cómo terminar sin que nadie caiga.", "tres desenlaces"),
    ("MP-15", "Después de todo", "EXP", "Epílogo: el mundo cambia según las decisiones; se desbloquean lugares y el mundo sigue abierto.", "—"),
]

SECUNDARIAS = [
    ("MS-01", "La bomba del pueblo", "BND", "Un artefacto amenaza el pueblo: desactivarlo o dejar que se use.", "desactivar / detonar"),
    ("MS-02", "Los de las jaulas", "RSC", "Liberar a cautivos de un campamento hostil.", "—"),
    ("MS-03", "La torre y los excluidos", "BND", "Una torre aristocrática rechaza a un grupo; elegir bando.", "torre / excluidos"),
    ("MS-04", "Las páginas del guía", "MAP", "Reunir las páginas de un manual de supervivencia dispersas por el mapa.", "—"),
    ("MS-05", "El robot que quería sentir", "ENS", "Un robot desea comprender a las personas; enseñarle.", "—"),
    ("MS-06", "La comunidad con reglas propias", "NEG", "Una comunidad aislada con sus propias normas pide mediación.", "ayudar o retirarse"),
    ("MS-07", "El culto del artefacto", "INV", "Un grupo venera un objeto; descubrir qué es.", "revelar o proteger"),
    ("MS-08", "La cura prometida", "CUR", "Conseguir ingredientes para una cura que un curandero promete.", "—"),
    ("MS-09", "Lo que vive en la mina", "JEF", "Una criatura grande bloquea una mina.", "—"),
    ("MS-10", "El pozo envenenado", "INV", "Descubrir el origen de la contaminación del pozo.", "culpables distintos"),
    ("MS-11", "La caravana atrapada", "ESC", "Escoltar a una caravana varada.", "—"),
    ("MS-12", "El mercado de lo oculto", "CTR", "Mover mercancía discreta entre dos puntos.", "ayudar o delatar"),
    ("MS-13", "El concurso del pueblo", "FIE", "Participar en el concurso anual.", "—"),
    ("MS-14", "El juicio", "DET", "Reunir pruebas para un juicio improvisado.", "culpable o inocente"),
    ("MS-15", "El fantasma del edificio", "PUZ", "Ruidos y luces en un edificio vacío.", "—"),
    ("MS-16", "Una voz sin cuerpo", "HCK", "Un sistema de voz pide ser reactivado.", "—"),
    ("MS-17", "La biblioteca que se cae", "REC", "Salvar libros de una biblioteca en ruinas.", "—"),
    ("MS-18", "El jardinero del páramo", "RCL", "Ayudar a cultivar plantas en tierra difícil.", "—"),
    ("MS-19", "Cacería para el trofeo", "CAZ", "Cazar una presa específica.", "—"),
    ("MS-20", "El mensajero que no llegó", "MSJ", "Entregar el último mensaje de alguien.", "—"),
    ("MS-21", "Cuentas pendientes", "COB", "Ayudar a pagar o cobrar una deuda.", "perdonar / cobrar"),
    ("MS-22", "El vecino que no sale", "FAM", "Convencer a alguien de volver a su casa.", "—"),
    ("MS-23", "El taller del inventor", "FAB", "Construir un invento extravagante.", "—"),
    ("MS-24", "La torreta rebelde", "SAB", "Una defensa automática ataca a todos.", "reparar / destruir"),
    ("MS-25", "El mapa roto", "ART", "Hallar las piezas de un mapa del tesoro.", "—"),
    ("MS-26", "Las ofrendas", "PUZ", "Un altar pide objetos en cierto orden.", "—"),
    ("MS-27", "La antena caída", "CON", "Levantar una antena de comunicaciones.", "—"),
    ("MS-28", "El rastro del ladrón", "DET", "Seguir a quien robó en el mercado.", "perdonar / entregar"),
    ("MS-29", "La mascota perdida", "DOM", "Encontrar a una criatura querida.", "—"),
    ("MS-30", "El campamento sin agua", "TRA", "Llevar agua a un campamento.", "—"),
    ("MS-31", "La enfermera sola", "MED", "Abastecer una enfermería aislada.", "—"),
    ("MS-32", "Reunión de vecinos", "NEG", "Arreglar un conflicto entre vecinos.", "dos bandos"),
    ("MS-33", "El archivo cerrado", "HCK", "Abrir un archivo con información sensible.", "publicar / guardar"),
    ("MS-34", "Plaga en el granero", "AMN", "Echar a una plaga del almacén.", "—"),
    ("MS-35", "El puente caído", "CON", "Reparar un puente clave.", "—"),
    ("MS-36", "El duelo de cazadores", "FIE", "Competir con otro cazador.", "—"),
    ("MS-37", "El traidor del puesto", "DET", "Descubrir quién filtra información.", "acusar / encubrir"),
    ("MS-38", "El regalo imposible", "ART", "Conseguir un objeto raro como obsequio.", "—"),
    ("MS-39", "La banda de la ruta", "AMN", "Detener a una banda que cobra peaje.", "pelear / negociar"),
    ("MS-40", "El refugio sin llave", "REC", "Encontrar la llave de un refugio olvidado.", "—"),
    ("MS-41", "Voluntarios para la ronda", "VIG", "Sumarse a una patrulla.", "—"),
    ("MS-42", "El dormitorio de los ruidos", "LMP", "Despejar un edificio con ruidos extraños.", "—"),
    ("MS-43", "Cruzar el desfiladero", "ESC", "Guiar a alguien por un paso difícil.", "—"),
    ("MS-44", "El inventario del almacén", "COM", "Contar y reponer un almacén.", "—"),
    ("MS-45", "Fuego en el barrio", "DEF", "Ayudar a apagar un incendio y proteger a la gente.", "—"),
]
