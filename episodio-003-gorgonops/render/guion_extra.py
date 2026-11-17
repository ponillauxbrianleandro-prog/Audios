"""Narración añadida en la v3 (para que siempre se esté diciendo o pasando algo).

EXTRA[nombre de escena] = [(k, texto), ...]: el texto se inserta después de la k-ésima narración de la escena (0 = al comienzo).
Todo lo afirmado aquí es de consenso o va con «probablemente»/«algunos estudios» (ver fuentes.md, sección 7).
"""
EXTRA = {
    "1 · El valle": [
        (3, "No se oye ningún canto de pájaro. Lo que se oye es el agua, el viento entre las colas de caballo y el zumbido de insectos que ya volaban desde mucho antes que cualquier vertebrado."),
    ],
    "2 · Un solo continente": [
        (3, "Pangea es tan grande que su interior casi no recibe lluvia. La vida se acomoda a ese ritmo: crece cuando hay agua, y espera cuando no la hay."),
    ],
    "3 · Alguien": [
        (1, "No ha dejado una sola huella que podamos señalar. Lo conocemos por sus huesos, y los huesos hablan despacio. Pero si uno aprende a escucharlos, cuentan una historia sorprendente."),
    ],
    "4 · Presentación": [
        (2, "Sus ojos miran bastante hacia adelante, lo que probablemente le daba visión en profundidad. De qué color era, en cambio, no lo sabemos: no hay piel fosilizada. Lo que ve en pantalla es una reconstrucción prudente, no una fotografía."),
    ],
    "5 · La mañana": [
        (1, "El agua es el centro de todo. Aquí beben los herbívoros, aquí se acercan los cazadores, y aquí las huellas se hunden en el barro y, a veces, se conservan millones de años."),
        (2, "Un depredador que vive junto a un río de estaciones aprende a leer el calendario: el nivel del agua, la sombra, el olor de la tierra mojada."),
    ],
    "5b · Cómo lo sabemos": [
        (1, "Los paleontólogos que recorren el Karoo caminan sobre el fondo de antiguos ríos. Los huesos aparecen dentro de nódulos de roca, y hay que abrirlos con cuidado, a veces durante muchas horas, para llegar a ellos."),
    ],
    "6 · Ni reptil ni mamífero": [
        (2, "Es otra cosa, y esa otra cosa tuvo su propio mundo: durante decenas de millones de años, los sinápsidos fueron los animales dominantes de la tierra."),
    ],
    "7 · Caminar": [
        (5, "La forma de su pecho y de sus huesos sugiere un cuerpo más activo que el de un lagarto. Cuánto más, es una de las preguntas abiertas de la paleontología."),
    ],
    "8 · Tres clases de dientes": [
        (3, "En los gorgonópsidos más grandes, los caninos pueden superar los diez centímetros. Son largos y aplanados, con el borde a menudo finamente aserrado: sirven más para sujetar y desgarrar que para triturar."),
    ],
    "9 · La caza": [
        (2, "Los dicinodontes eran una presa habitual: numerosos, con dos colmillos y pico córneo. Diictodon cavaba madrigueras en espiral, y esas galerías todavía se encuentran en la roca."),
        (3, "Probablemente no persiguiera nada que no valiera la pena. Para un animal que come poco y espera mucho, cada gesto cuesta."),
    ],
    "10 · Lo que duele igual": [
        (5, "Comer, curarse, envejecer: en lo esencial, un cuerpo de hace doscientos cincuenta millones de años se parece más al nuestro de lo que parece."),
    ],
    "11 · El valle habitado": [
        (2, "Están los pareiasaurios, enormes y acorazados, que mastican hojas. Están los terocéfalos, parientes lejanos, más pequeños y ágiles. Y están los dicinodontes, que van del tamaño de una rata al de un buey."),
    ],
    "12 · El pequeño": [
        (3, "Su paladar ya separa la boca de la nariz, lo que permite respirar mientras se mastica: una pista técnica, pero una de las que lo ponen del lado de los futuros mamíferos. Y algunos investigadores creen que nadaba bien."),
    ],
    "13 · La estación seca": [
        (2, "En la roca se leen los años secos: grietas de barro, bancos de arena, ríos que cambian de cauce. Es un archivo del clima, escrito en capas."),
    ],
    "14 · La bruma tenía dueño": [
        (4, "Y no fue una explosión. Fue un proceso con pulsos, y el golpe más duro se concentra en unas pocas decenas de miles de años: poco para la geología, muchísimo para quien vive dentro."),
    ],
    "15 · La rama que termina": [
        (4, "Sobreviven los que pueden esperar: los que comen poco, los que cavan, los que se reproducen deprisa. No es una cuestión de fuerza."),
        (8, "También cruza al otro lado Lystrosaurus, un dicinodonte pequeño y robusto. Durante un tiempo, en algunas rocas del Triásico temprano, casi todos los fósiles son suyos."),
    ],
    "16 · Los huesos que escuchan": [
        (2, "El camino fue gradual y quedó escrito en fósiles intermedios: huesos de la mandíbula cada vez más pequeños, y una segunda articulación, nueva, que se va formando por delante."),
    ],
    "17 · Las formas sin fin": [
        (1, "Los primeros mamíferos aparecen hace más de doscientos millones de años: pequeños, probablemente nocturnos, del tamaño de un ratón. Durante mucho tiempo vivieron a la sombra de los dinosaurios."),
    ],
    "18 · Simplemente vivía": [
        (2, "Mientras tanto, el sol sube. Las colas de caballo se mueven con el viento y el agua sigue su camino hacia el mar. Es una mañana corriente, y es la única que tiene."),
    ],
}
SIL_MAX = 1.2          # ninguna pausa sin voz supera esto
VIS_MAX = {"3 · Alguien": 3.0}   # «vis» = plano sin voz; los gráficos con acción (apertura, créditos) no se tocan

# Frases puente (solo audio): rellenan los huecos de transición sin tocar la imagen ni los tiempos de los planos.
# (fragmento de la frase que las precede, texto del puente)
BRIDGES = [
    ("espera cuando no la hay", "Un mundo inmenso y callado."),
    ("cuentan una historia sorprendente", "Esta es su historia."),
    ("comprobando cuánto nos equivocamos", "Empecemos por una mañana cualquiera."),
    ("Vamos a volver a ellos", "¿Y cómo la usa?"),
    ("un mordisco profundo y retirarse", "Imaginemos la escena: una espera larga, un instante de velocidad. Y probablemente, muchas veces, gana el hambre."),
    ("cada gesto cuesta", "Veamos su mandíbula por dentro."),
    ("Los océanos todavía no estaban ahí", "Volvamos a los animales."),
    ("Le basta con seguir", "Este documental es una reconstrucción animada. Los datos, las citas y las fuentes están en la descripción."),
]
