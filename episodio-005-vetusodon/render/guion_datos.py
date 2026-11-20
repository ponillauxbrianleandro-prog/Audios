"""Texto de la narración (episodio 005, guion v2 de documental) por escena, citas y ortografía rioplatense para el sintetizador.

LINEAS[escena] = lista de frases (una por toma de voz; nunca se solapan). ORDEN = orden de las escenas en la película.
sheismo(texto): «ll» y «y» consonánticas -> «sh» (llanura -> shanura, yo -> sho, playa -> plasha); la «y» suelta
(conjunción) y la «y» final (hoy, muy, hay) se conservan.

Estado de cada afirmación en ../fuentes.md: [C] confirmado en la literatura, [I] inferencia / reconstrucción.
"""
import re

ORDEN = [0, 1, 2, 3, 4, 12, 5, 6, 13, 7, 8, 9, 14, 10, 11]
GAP_ESC = {0: 0.30, 5: 0.30}          # silencio entre frases (s); por defecto 0,85

LINEAS = {
    # 0 · apertura: solo números y el nombre (ráfaga de fotos < 1 s por toma)
    0: ["Doscientos cincuenta y dos millones de años antes de Cristo.",
        "Dieciocho centímetros de cráneo. Cuatro fósiles.",
        "Vetusodon elikhulu. Nuestro ancestro."],
    # 1 · el animal
    1: ["Vetusodon elikhulu: «el grande», en zulú.",
        "Con un cráneo de dieciocho centímetros, es el mayor cinodonte conocido del Pérmico tardío.",
        "Se lo conoce por cuatro ejemplares, todos de la cuenca del Karoo, en Sudáfrica.",
        "Fue descrito en dos mil diecinueve. Es el grupo hermano de los eucinodontes, el linaje que lleva a los mamíferos."],
    # 2 · el valle
    2: ["Karoo, Sudáfrica, Pérmico tardío. Un valle de ríos estacionales, sin hierba ni flores.",
        "Crecen helechos con semillas, colas de caballo y glossopteris, árboles de hojas en forma de lengua.",
        "Dominan los dicinodontes: Diictodon, Dicynodon, Daptocephalus.",
        "Entre los insectos hay libélulas primitivas, escarabajos y cucarachas.",
        "Y en lo más alto de la cadena alimentaria, los gorgonopsios."],
    # 3 · cuaderno: el hallazgo y los científicos
    3: ["Los paleontólogos miden, dibujan y comparan: hocico corto y ancho, y una región temporal que ocupa el sesenta por ciento del cráneo.",
        "Christian Kammerer, paleontólogo, dice: «Entre los sinápsidos del Pérmico estaban nuestros propios antepasados, y no hay ni de lejos suficiente gente que lo sepa.»",
        "Y Ken Angielczyk, del Field Museum: «Antes de la época de los dinosaurios hubo una era de antiguos parientes de los mamíferos.»"],
    # 4 · una mañana: comportamiento
    4: ["Amanecer en el Karoo. El Vetusodon rastrea el suelo con el hocico.",
        "Come lo que hay: raíces, semillas, larvas e insectos. Es una inferencia a partir de su dentadura, con incisivos, caninos y postcaninos.",
        "Patas abiertas y garras largas: según la reconstrucción, un cuerpo hecho para cavar.",
        "Ningún fósil conserva su piel. El pelaje es una inferencia, por su cercanía con los mamíferos.",
        "El agua manda: el río sube y baja con las estaciones, y cada charco se defiende."],
    # 12 · pelea (BOOM 1, reconstrucción)
    12: ["Reconstrucción, no registro fósil: dos adultos se disputan un Diictodon muerto, un dicinodonte de cuarenta y cinco centímetros.",
         "Dieciocho centímetros de cráneo y dientes de tres tipos: cada mordida es un arma.",
         "En este valle, una carroña puede decidir quién llega a la estación seca."],
    # 5 · montaje de datos
    5: ["Sinápsidos: más de trescientos millones de años de historia. Cinodontes: mandíbula y dientes de mamífero."],
    # 6 · el vecino: gorgonopsios (BOOM 3)
    6: ["Los gorgonopsios son los depredadores más grandes del valle: caninos de sable y una mandíbula que se abre como una tijera.",
        "Cazan por emboscada, y un cinodonte es presa posible.",
        "Hasta dos metros de largo y un cráneo de treinta y cinco centímetros: casi el doble que el del Vetusodon.",
        "El Vetusodon no tiene colmillos de sable ni garras de cazador. Su defensa es la fuga, y la madriguera."],
    # 13 · conflicto de grupo + Aristóteles (BOOM 2)
    13: ["Reconstrucción: un grupo de Vetusodon cierra filas ante el gorgonopsio, y el depredador duda.",
         "Aristóteles, trescientos cincuenta años antes de Cristo, sobre el estudio de los animales: «En todas las cosas de la naturaleza hay algo maravilloso.»"],
    # 7 · cuaderno: los huesos del oído
    7: ["Un detalle anatómico cambió la ciencia. En los cinodontes, la mandíbula inferior tiene varios huesos.",
        "Dos de ellos, el articular y el cuadrado, forman la articulación de la mandíbula.",
        "En los mamíferos, esos mismos huesos son el martillo y el yunque del oído medio. Es una de las pruebas más sólidas de la evolución."],
    # 8 · Trampas Siberianas (BOOM 4)
    8: ["Hace unos doscientos cincuenta y dos millones de años, en lo que hoy es Siberia, empiezan las erupciones de las Trampas Siberianas.",
        "Lava durante cientos de miles de años, y una cantidad enorme de dióxido de carbono.",
        "El planeta se calienta. En el Karoo, el río se achica y las plantas se secan."],
    # 9 · la nube y la extinción (BOOM 5-6)
    9: ["Llegan las cenizas y los gases ácidos, y empieza a caer la lluvia que quema.",
        "Pia Viglietti, del Field Museum: «Todos los grandes depredadores del Pérmico tardío de Sudáfrica se extinguieron bastante antes de la extinción masiva del final del Pérmico.»",
        "Los gorgonopsios no llegan al peor momento. Desaparecen primero.",
        "Después, el final del Pérmico: desaparece alrededor del ochenta y uno por ciento de las especies marinas y el setenta por ciento de los vertebrados terrestres.",
        "Es la mayor extinción de la historia de la Tierra."],
    # 14 · Lystrosaurus: la especie invasora (BOOM 7)
    14: ["Entre los sobrevivientes aparece un dicinodonte: Lystrosaurus.",
         "En el Karoo pasa de representar el cincuenta y cuatro por ciento de los fósiles de vertebrados a representar el setenta por ciento.",
         "Sus restos aparecen también en la Antártida y en la India: coloniza un supercontinente."],
    # 10 · el refugio (BOOM 8, parte 1)
    10: ["Los cinodontes sobreviven. Entre los pequeños, Thrinaxodon cava madrigueras: sus fósiles aparecen enroscados dentro de una.",
         "El Vetusodon no llega al Triásico. Su linaje, sí.",
         "Los eucinodontes aparecen pocos millones de años después, y de ellos salen los mamíferos."],
    # 11 · tu pariente + Darwin (cierre épico)
    11: ["Doscientos cincuenta millones de años después, esos huesos de la mandíbula están dentro de tu oído.",
         "Charles Darwin, mil ochocientos cincuenta y nueve: «…a partir de un comienzo tan sencillo han evolucionado, y siguen evolucionando, infinidad de formas, las más bellas y las más maravillosas.»",
         "Vetusodon elikhulu. Tu ancestro."],
}

# citas con tarjeta épica sobre la acción: clave -> (autor, rol, texto original, español)
QUOTES = {
    "aristoteles": ("Aristóteles", "Partes de los animales · hacia 350 a. C.",
                    "In all natural things there is something of the marvellous.",
                    "En todas las cosas de la naturaleza hay algo maravilloso."),
    "viglietti": ("Pia Viglietti", "Paleontóloga · Field Museum, Chicago",
                  "All the big top predators in the Late Permian in South Africa went extinct well before the end-Permian mass extinction.",
                  "Todos los grandes depredadores del Pérmico tardío de Sudáfrica se extinguieron bastante antes de la extinción masiva del final del Pérmico."),
    "darwin": ("Charles Darwin", "El origen de las especies · 1859",
               "…from so simple a beginning endless forms most beautiful and most wonderful have been, and are being, evolved.",
               "…a partir de un comienzo tan sencillo han evolucionado, y siguen evolucionando, infinidad de formas, las más bellas y las más maravillosas."),
}
# (escena, índice de la frase, retardo tras empezar la frase, clave, duración s): la tarjeta cubre la imagen mientras la voz dice la cita
CARDS = [(13, 1, 0.3, "aristoteles", 8.5), (9, 1, 0.3, "viglietti", 11.5), (11, 1, 0.3, "darwin", 12.0)]

_V = "aeiouáéíóúüAEIOUÁÉÍÓÚÜ"


def sheismo(t):
    def palabra(m):
        w = m.group(0)
        if len(w) == 1:
            return w
        w = re.sub(r"ll", "sh", w)
        w = re.sub(r"LL", "SH", w)
        w = re.sub(r"Ll", "Sh", w)
        w = re.sub(r"(?<=[^\W\d_])y(?=[%s])" % _V, "sh", w)       # y entre letras y antes de vocal (mayor, playa, ayuda)
        w = re.sub(r"^y(?=[%s])" % _V, "sh", w)                    # y inicial (yo, ya, yunque)
        w = re.sub(r"^Y(?=[%s])" % _V, "Sh", w)
        return w
    return re.sub(r"[A-Za-zÁÉÍÓÚáéíóúÜüÑñ]+", palabra, t)


def todas():
    return [(e, i, t) for e in ORDEN for i, t in enumerate(LINEAS[e])]


if __name__ == "__main__":
    n = sum(len(t.split()) for _, _, t in todas())
    print(len(todas()), "líneas", n, "palabras ·", round(n / 2.6), "s de voz aprox.")
