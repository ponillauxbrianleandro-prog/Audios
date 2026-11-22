"""Catalogo de objetos: armas, municion, armaduras, consumibles y generales (nombres genericos; el lore pone los nombres)."""

TIER_MULT = [0.7, 1.0, 1.3, 1.7, 2.2]

# (nombre, dano_lo, dano_hi, PA, rasgo, requisito)
MELE = [
    ("Puños", 3, 5, 3, "sin arma", "—"), ("Nudillera", 5, 8, 3, "+10% crítico", "FUE 3"), ("Garra potenciada", 8, 12, 4, "sangrado 25%", "FUE 4"),
    ("Cuchillo", 4, 7, 3, "sangrado 20%; emboscada ×2.5", "—"), ("Daga arrojadiza", 4, 8, 3, "arrojable, recuperable 70%", "AGI 5"),
    ("Machete", 7, 11, 4, "sangrado 25%", "FUE 4"), ("Espada corta", 8, 12, 4, "sangrado 20%", "FUE 4"), ("Espada larga", 10, 15, 5, "alcance 2", "FUE 5"),
    ("Sable", 9, 14, 4, "+5% crítico", "AGI 5"), ("Hoja curva", 11, 16, 4, "+10% crítico", "AGI 6"), ("Porra", 6, 10, 4, "aturde 15%", "FUE 4"),
    ("Garrote", 6, 10, 4, "aturde 15%", "FUE 4"), ("Bate", 7, 12, 4, "aturde 20%", "FUE 5"), ("Tubo", 6, 10, 4, "improvisada", "FUE 3"),
    ("Palanca", 7, 11, 4, "+10 al forzar", "FUE 4"), ("Martillo", 9, 14, 5, "aturde 20%", "FUE 5"), ("Maza (2 manos)", 10, 16, 6, "aturde 25%", "FUE 6"),
    ("Mazo de guerra (2 manos)", 12, 18, 6, "rompe estructuras", "FUE 7"), ("Hacha", 9, 14, 5, "sangrado 25%", "FUE 5"),
    ("Hacha doble (2 manos)", 11, 17, 6, "sangrado 30%", "FUE 6"), ("Lanza", 8, 12, 5, "alcance 2", "FUE 4"), ("Alabarda (2 manos)", 10, 16, 6, "alcance 2; golpe de barrido", "FUE 6"),
    ("Bastón", 5, 9, 4, "defensa +10%", "—"), ("Bastón largo", 6, 10, 4, "alcance 2", "AGI 4"), ("Cadena", 7, 11, 5, "enreda 15%", "FUE 5"),
    ("Látigo", 4, 8, 4, "alcance 2; enreda", "AGI 5"), ("Hoz", 6, 10, 4, "sangrado 25%", "FUE 3"), ("Pico", 8, 13, 5, "ignora 2 de RD", "FUE 5"),
    ("Pala", 6, 10, 4, "improvisada", "FUE 3"), ("Horquilla", 7, 11, 4, "alcance 2", "FUE 4"), ("Garrote de púas", 9, 13, 5, "sangrado 25%", "FUE 5"),
    ("Guantelete", 6, 10, 4, "aturde 15%", "FUE 4"), ("Escudo de golpe", 4, 8, 4, "defensa +20%", "FUE 4"), ("Remo", 6, 10, 4, "+10 en agua", "FUE 3"),
    ("Arpón", 8, 12, 5, "alcance 2; arrojable", "FUE 4"), ("Cuchillo de pesca", 4, 7, 3, "sangrado 20%", "—"), ("Tonfa de ronda", 6, 10, 3, "aturde 15%; defensa +10%", "—"),
    ("Cadena con ancla", 10, 15, 6, "enreda 20%", "FUE 6"), ("Sable de abordaje", 9, 14, 4, "+5% crítico", "AGI 5"), ("Garfio", 6, 10, 4, "sangrado 20%; ayuda a trepar", "FUE 3"),
    ("Red de combate", 0, 2, 4, "inmoviliza 30%", "AGI 4"), ("Bastón de práctica (no letal)", 3, 6, 3, "derriba, nunca mata", "—"),
    ("Espada de entrenamiento (no letal)", 3, 6, 3, "derriba, nunca mata", "—"), ("Arma de energía cuerpo a cuerpo", 12, 18, 5, "ignora 3 de RD; usa célula", "FUE 5"),
    ("Cuchilla vibrante", 11, 17, 4, "ignora 3 de RD; usa célula", "FUE 4"), ("Lanza eléctrica", 10, 16, 5, "aturde 20%; usa célula", "FUE 5"),
]

# (nombre, lo, hi, alcance, PA, municion, rasgo, requisito)
DISTANCIA = [
    ("Pistola pequeña", 6, 10, "corto-medio", 4, "A-01", "cargador 8-12", "PER 3"), ("Pistola de bolsillo", 4, 8, "corto", 3, "A-01", "cargador 6; oculta", "PER 2"),
    ("Pistola silenciada", 5, 9, "corto", 4, "A-01", "silenciosa; emboscada ×2", "PER 4"), ("Revólver", 9, 14, "medio", 5, "A-02", "cargador 6; +10% crítico", "PER 4"),
    ("Revólver pesado", 12, 18, "medio", 6, "A-03", "retroceso", "PER 5 FUE 5"), ("Pistola pesada", 12, 18, "medio", 6, "A-03", "retroceso −10%", "PER 5 FUE 5"),
    ("Pistola de duelo", 10, 15, "corto", 5, "A-02", "1 disparo, +15% impacto", "PER 5"), ("Pistola de bengalas", 2, 5, "medio", 4, "A-13", "ilumina; quemadura", "—"),
    ("Subfusil", 4, 7, "corto", 6, "A-01", "ráfaga ×3", "PER 4"), ("Subfusil compacto", 3, 6, "corto", 5, "A-01", "ráfaga ×3; ligero", "PER 3"),
    ("Rifle de caza", 10, 16, "largo", 5, "A-02", "+10% apuntado", "PER 5"), ("Rifle de palanca", 12, 18, "largo", 6, "A-02", "recarga 1/ronda", "PER 5"),
    ("Rifle de cerrojo", 14, 20, "largo", 6, "A-02", "+15% apuntado", "PER 6"), ("Rifle automático", 8, 13, "medio-largo", 7, "A-02", "ráfaga ×3", "PER 5 FUE 5"),
    ("Rifle de asalto", 7, 12, "medio-largo", 7, "A-02", "ráfaga ×3", "PER 5 FUE 5"), ("Carabina", 8, 13, "medio", 5, "A-02", "ligera", "PER 4"),
    ("Rifle de precisión", 18, 28, "muy largo", 8, "A-03", "+20% apuntado; crítico +15%", "PER 7"), ("Rifle antimaterial", 25, 38, "muy largo", 9, "A-03", "ignora 5 de RD", "PER 7 FUE 7"),
    ("Escopeta de corredera", 14, 24, "corto", 6, "A-04", "dispersión", "FUE 5"), ("Escopeta de doble caño", 16, 26, "corto", 6, "A-04", "2 cartuchos", "FUE 5"),
    ("Escopeta recortada", 18, 28, "muy corto", 6, "A-04", "solo adyacente", "FUE 5"), ("Escopeta de combate", 15, 25, "corto", 7, "A-04", "cargador 8", "FUE 6"),
    ("Escopeta automática", 12, 22, "corto", 8, "A-04", "ráfaga ×2", "FUE 6"), ("Arco corto", 7, 12, "medio", 5, "A-05", "silencioso; recuperable 50%", "PER 3"),
    ("Arco largo", 9, 15, "largo", 5, "A-05", "silencioso", "PER 4 FUE 4"), ("Arco compuesto", 10, 16, "largo", 5, "A-05", "silencioso; +5% impacto", "PER 5"),
    ("Ballesta", 8, 14, "medio", 5, "A-05", "silenciosa", "PER 4"), ("Ballesta de mano", 6, 10, "corto", 4, "A-05", "silenciosa; oculta", "PER 3"),
    ("Ballesta de repetición", 7, 12, "medio", 6, "A-05", "ráfaga ×2", "PER 5"), ("Honda", 3, 7, "medio", 4, "A-13", "no letal con piedras de goma", "—"),
    ("Cerbatana", 1, 3, "corto", 3, "A-05", "dardos con efecto", "PER 3"), ("Lanzaarpones", 12, 18, "medio", 6, "A-05", "arpón recuperable", "FUE 5"),
    ("Pistola de dardos sedantes", 1, 3, "medio", 4, "A-05", "inmoviliza 25-40%", "PER 4"), ("Rifle de dardos", 1, 3, "largo", 5, "A-05", "inmoviliza 25-40%", "PER 5"),
    ("Lanzagarfios", 2, 5, "medio", 4, "A-05", "ayuda a trepar o enredar", "AGI 5"), ("Pistola de red", 0, 2, "corto", 4, "A-13", "inmoviliza 35%", "PER 3"),
    ("Arco de práctica (no letal)", 2, 5, "medio", 4, "A-13", "derriba, nunca mata", "—"), ("Ballesta de práctica (no letal)", 2, 5, "medio", 4, "A-13", "derriba, nunca mata", "—"),
]

# energia, pesadas y explosivos: (nombre, lo, hi, alcance, PA, municion, rasgo, requisito)
ENERGIA = [
    ("Pistola de energía", 8, 13, "medio", 5, "A-06", "ignora 2 de RD", "PER 4"), ("Rifle de energía", 12, 20, "largo", 6, "A-06", "ignora 3 de RD", "PER 5"),
    ("Escopeta de energía", 14, 24, "corto", 6, "A-06", "dispersión; ignora 2 de RD", "FUE 5"), ("Ametralladora de energía", 6, 10, "medio", 9, "A-06", "ráfaga ×5", "FUE 6"),
    ("Pistola de plasma", 14, 22, "medio", 6, "A-07", "quemadura 2 rondas", "PER 5"), ("Rifle de plasma", 20, 32, "largo", 8, "A-07", "quemadura 3 rondas", "PER 6"),
    ("Arma de pulso", 10, 16, "medio", 6, "A-06", "×2 vs artificiales; aturde", "PER 5"), ("Arma de rayos", 10, 18, "medio", 6, "A-06", "aturde 20%", "PER 5"),
    ("Arma sónica", 8, 14, "corto", 5, "A-06", "aturde 25%", "PER 4"), ("Arma de congelación", 8, 14, "medio", 6, "A-06", "ralentiza 2 rondas", "PER 5"),
    ("Arma de microondas", 6, 12, "corto", 5, "A-06", "daño continuo 3 rondas", "PER 4"), ("Cañón de luz", 15, 25, "largo", 8, "A-07", "ciega 20%", "PER 6"),
    ("Ametralladora pesada", 5, 9, "largo", 10, "A-02", "ráfaga ×5; suprime", "FUE 6"), ("Minigun", 4, 7, "largo", 14, "A-02", "ráfaga ×10; recalienta", "FUE 8"),
    ("Lanzallamas", 8, 14, "corto", 8, "A-08", "cono; quemadura 3 rondas", "FUE 6"), ("Lanzagranadas", 15, 25, "medio", 8, "A-09", "área 2", "PER 5"),
    ("Lanzacohetes", 30, 45, "largo", 10, "A-10", "área 3", "FUE 6"), ("Lanzamisiles", 45, 65, "muy largo", 12, "A-11", "área 4", "FUE 7"),
    ("Lanzador táctico", 150, 150, "muy largo", 15, "A-12", "destruye zona; autodaño si hay cerca", "FUE 8"), ("Cañón de mano", 20, 30, "medio", 9, "A-03", "retroceso fuerte", "FUE 7"),
    ("Lanzador de redes", 0, 3, "medio", 6, "A-13", "inmoviliza grupo 2", "PER 4"), ("Lanzador de bengalas", 2, 6, "largo", 5, "A-13", "ilumina; quemadura", "—"),
    ("Granada de fragmentación", 20, 30, "corto", 4, "consumible", "área 3", "—"), ("Granada incendiaria", 10, 16, "corto", 4, "consumible", "fuego en zona 3 rondas", "—"),
    ("Granada de humo", 0, 0, "corto", 3, "consumible", "−30% impacto enemigo 3 rondas", "—"), ("Granada de pulso", 20, 30, "corto", 4, "consumible", "aturde máquinas", "—"),
    ("Granada de plasma", 30, 45, "corto", 4, "consumible", "área; quemadura", "—"), ("Granada de choque", 5, 10, "corto", 4, "consumible", "aturde 30%", "—"),
    ("Granada de gas", 3, 8, "corto", 4, "consumible", "veneno 3 rondas", "—"), ("Granada de luz", 0, 2, "corto", 3, "consumible", "ciega 30% a todos", "—"),
    ("Señuelo", 0, 0, "colocado", 3, "consumible", "atrae 5 rondas", "—"), ("Dinamita o carga", 25, 40, "colocada", 5, "consumible", "mecha 1-3 rondas; rompe puertas", "—"),
    ("Mina de proximidad", 20, 35, "colocada", 5, "consumible", "área; detectable", "—"), ("Mina de choque", 6, 12, "colocada", 5, "consumible", "aturde 40%", "—"),
    ("Mina de gas", 4, 10, "colocada", 5, "consumible", "veneno 4 rondas", "—"), ("Mina de pulso", 20, 30, "colocada", 5, "consumible", "aturde máquinas", "—"),
    ("Cepo", 8, 14, "colocado", 5, "consumible", "inmoviliza", "—"), ("Trampa de cuerda", 4, 8, "colocada", 4, "consumible", "alarma + derriba", "—"),
    ("Trampa de red (no letal)", 0, 2, "colocada", 4, "consumible", "inmoviliza 50%", "—"), ("Bomba casera", 15, 25, "colocada", 6, "consumible", "mecha larga; área 2", "—"),
]

# armas unicas (arquetipos): (base, propiedad)
UNICAS = [
    ("espada larga", "no se rompe y brilla de noche"), ("hacha doble", "aturde 40% y no pierde filo"), ("pistola pequeña", "cargador infinito de A-01"),
    ("revólver", "crítico ×3 al apuntar a la cabeza"), ("rifle de caza", "munición que se recupera 50% del tiempo"), ("rifle de precisión", "ignora cobertura"),
    ("escopeta de doble caño", "dispersión en cono más amplio"), ("arco largo", "flechas que regresan 70% de las veces"), ("ballesta", "dispara dos flechas por acción"),
    ("lanzallamas", "no consume combustible fuera de combate"), ("arma de plasma", "quemadura +2 rondas"), ("arma de pulso", "afecta a toda la cuadra de máquinas"),
    ("lanza", "alcance 3"), ("mazo de guerra", "derriba incluso talla T4"), ("bastón", "defensa +40%; cura 2 PV por ronda"), ("látigo", "enreda 50%"),
    ("cuchillo", "emboscada ×4"), ("daga arrojadiza", "vuelve a la mano"), ("garrote de púas", "sangrado 50%"), ("cadena", "inmoviliza 40%"),
    ("sable", "+20% impacto"), ("red de combate", "inmoviliza hasta 3 a la vez"), ("honda", "piedras que aturden 50%"), ("remo", "+30 en agua y empuja botes"),
    ("arpón", "recuperable siempre"), ("sable de abordaje", "aturde al enemigo cercano"), ("garfio", "alcance 3 y trepa sin tirada"), ("espada de entrenamiento", "otorga +20% XP"),
    ("pistola de dardos sedantes", "dardos ilimitados"), ("arco de práctica", "acierto +15% y XP extra"), ("cañón de mano", "retroceso nulo"), ("pico", "ignora toda la RD"),
    ("martillo", "repara armas del grupo al golpear"), ("hoz", "recolecta recursos al golpear"), ("tonfa", "contraataque automático"), ("escudo de golpe", "bloqueo 90%"),
    ("lanzaarpones", "inmoviliza criaturas grandes"), ("lanzagarfios", "ata a un enemigo al suelo"), ("carabina", "ligera: 0 de PA extra"), ("pistola de duelo", "no falla el primer disparo"),
]

# variantes de municion: (nombre, efecto, familias, valor x, rareza)
MUNICION_VARIANTES = [
    ("Estándar", "sin cambios", "A-01..A-04", "1", "Común"), ("Perforante", "ignora 50% de RD; daño ×0.85", "A-01..A-04", "1.8", "Útil"),
    ("Expansiva", "daño ×1.25; la RD cuenta ×1.5", "A-01..A-04", "1.6", "Útil"), ("Incendiaria", "+4 fuego; quemadura 3 rondas 25%", "A-01..A-04, A-05", "2.5", "Raro"),
    ("De choque", "aturde 15%", "A-01..A-05", "2.2", "Raro"), ("Trazadora", "+5% impacto; revela al tirador", "A-01..A-04", "1.5", "Útil"),
    ("Subsónica", "silenciosa; daño ×0.9", "A-01..A-03", "1.8", "Útil"), ("Explosiva", "+6 de área", "A-01..A-04", "3", "Raro"),
    ("De precisión", "+10% apuntado; daño ×1.05", "A-01..A-03", "2.2", "Raro"), ("Antiblindaje", "ignora toda la RD vs blindados", "A-02..A-03", "3", "Raro"),
    ("De baja potencia", "daño ×0.75; atasco +5%", "A-01..A-04", "0.5", "Común"), ("Envenenada", "veneno 2/ronda 4 rondas", "A-01..A-05", "2.5", "Raro"),
    ("De dispersión", "área mayor; daño ×0.8; 3 objetivos", "A-04", "1.4", "Común"), ("Postas", "daño ×1.2 corto; ×0.7 largo", "A-04", "1.3", "Común"),
    ("Dragón", "+5 fuego; quemadura", "A-04", "2.8", "Raro"), ("De goma", "daño ×0.3; aturde 30% (no letal)", "A-01, A-04", "1.2", "Útil"),
    ("De sal", "daño ×0.4; ralentiza a insectos 3 rondas", "A-04", "1.1", "Común"), ("De red", "inmoviliza 25% (no letal)", "A-04, A-13", "2", "Raro"),
    ("De práctica", "daño ×0.2; derriba, nunca mata", "A-01..A-05", "0.3", "Común"), ("Sedante", "inmoviliza 25-40%", "A-05", "2.5", "Raro"),
    ("Hueca", "daño ×1.15; RD ×1.25", "A-01..A-02", "1.4", "Común"), ("Ácida", "−2 RD durante 3 rondas", "A-01..A-04", "2.6", "Raro"),
    ("Criogénica", "ralentiza 2 rondas", "A-01..A-03", "2.7", "Raro"), ("Sobrecarga (célula)", "+30% daño; la célula dura 3 usos", "A-06, A-07", "2", "Raro"),
    ("De pulso (célula)", "aturde máquinas", "A-06", "2", "Raro"), ("Eficiente (célula)", "+50% usos; −10% daño", "A-06, A-07", "1.5", "Útil"),
    ("Recargable (célula)", "se recarga en estación en 8 h", "A-06, A-07", "3", "Raro"), ("Combustible gelificado", "quemadura 5 rondas", "A-08", "2", "Raro"),
    ("Combustible ácido", "−2 RD 3 rondas", "A-08", "2.2", "Raro"), ("Granada de fragmentación (lanzador)", "área 3", "A-09", "1", "Útil"),
    ("Cohete penetrante", "ignora 5 de RD", "A-10", "2", "Raro"), ("Flecha de práctica", "no letal", "A-05", "0.3", "Común"),
    ("Flecha de señal", "ilumina y alerta a aliados", "A-05", "1.2", "Útil"), ("Flecha con cuerda", "ata a un paso o enemigo", "A-05", "1.5", "Útil"),
    ("Piedra de honda pulida", "+5% impacto", "A-13", "0.6", "Común"), ("Perdigón de sal", "daño ×0.3; molesta", "A-13", "0.4", "Común"),
]

# armaduras: piezas y su RD por tier E0..E5 (E0 sin proteccion)
ARMADURAS_PIEZAS = [
    ("Casco o gorro", [0, 0, 1, 1, 2, 3], 1), ("Torso (camisa/chaleco/coraza)", [0, 1, 2, 3, 5, 8], 4), ("Piernas (pantalón/grebas)", [0, 0, 1, 2, 3, 5], 3),
    ("Pies (botas/calzado)", [0, 0, 0, 0, 1, 2], 2), ("Guantes", [0, 0, 0, 1, 1, 2], 1), ("Capa o abrigo", [0, 1, 1, 2, 3, 4], 3),
    ("Mochila reforzada", [0, 0, 1, 1, 2, 3], 3), ("Hombreras", [0, 0, 1, 1, 2, 3], 2), ("Cinturón de herramientas", [0, 0, 0, 0, 1, 1], 1),
]
ARMADURAS_MATERIALES = ["tela", "cuero", "lona", "malla", "placas", "aleación", "compuesto", "asistida"]
ARMADURAS_ESPECIALES = [
    ("Ropa de abrigo", "resiste frío 40%; −5 sigilo", "E1-E3"), ("Ropa de calor", "resiste calor 40%", "E1-E3"), ("Impermeable", "resiste lluvia y agua sucia 30%", "E1-E3"),
    ("Traje de sigilo", "+10 sigilo; RD baja", "E2-E3"), ("Traje de explorador", "+5 sigilo; +10 carga", "E1-E3"), ("Uniforme de facción", "sirve de disfraz (33)", "E1-E4"),
    ("Ropa de lujo", "+10% precios a favor; sin RD", "E1"), ("Ropa de pirata", "+5 carisma ante marineros; RD 1", "E1-E2"), ("Traje de buceo", "respira bajo el agua 10 min", "E2-E3"),
    ("Chaleco salvavidas", "no te hundís; −1 sigilo", "E1"), ("Armadura de torneo", "RD alto, ruidosa", "E3"), ("Armadura pesada", "RD alto; velocidad −10%", "E4"),
    ("Armadura asistida", "RD muy alto; +FUE; necesita núcleo", "E5"), ("Ropa de niño explorador", "ligera; sin RD; para menores", "E1"), ("Capa de camuflaje", "+10 en bosque o selva", "E1-E2"),
    ("Máscara respiratoria", "resiste gas y esporas", "E2"), ("Gafas de visión", "+5 PER visual; protege polvo", "E1"), ("Casco con luz", "ilumina; +1 RD cabeza", "E2"),
]

COMIDAS = [
    ("Fruta fresca", 12, "+3 PV"), ("Verdura cruda", 12, "ninguno"), ("Hongo comestible", 10, "ninguno"), ("Carne cruda", 15, "15% Enfermo"), ("Carne cocida", 30, "+8 PV"),
    ("Pescado crudo", 12, "10% Enfermo"), ("Pescado asado", 28, "+7 PV"), ("Guiso", 35, "+10 PV; calienta"), ("Sopa", 30, "+8 PV; calienta"), ("Pan", 20, "—"),
    ("Galleta o barra", 8, "+2 PV; +5% PA 30 min"), ("Tasajo (carne seca)", 22, "dura 30 días"), ("Lata de guiso", 25, "+5 PV"), ("Lata de verduras", 20, "+3 PV"),
    ("Lata de fruta", 18, "+3 PV"), ("Lata de pescado", 22, "+5 PV"), ("Ración de viaje", 40, "+6 PV; 3 usos"), ("Queso", 20, "+4 PV"), ("Miel", 10, "+5 PV; antiséptico leve"),
    ("Huevos cocidos", 20, "+5 PV"), ("Papas asadas", 25, "+6 PV"), ("Maíz", 18, "+3 PV"), ("Cereal tostado", 15, "—"), ("Dulce casero", 8, "+3 PV; +5 ánimo"),
    ("Banquete", 50, "+15 PV; Descansado 4 h"), ("Comida de criatura (carne de especie)", 20, "+4 PV; según especie"), ("Comida caducada", 10, "30% Enfermo"),
    ("Comida contaminada", 20, "+20 contaminación"), ("Pastel de fiesta", 20, "+8 PV; +10 ánimo"), ("Fruta del bosque", 10, "+2 PV; riesgo bajo"),
    ("Raíz hervida", 22, "+4 PV"), ("Insecto asado", 12, "+3 PV (lore)"), ("Algas secas", 14, "+3 PV (costa o pantano)"), ("Caracoles de pantano guisados", 22, "+5 PV (pantano)"),
]
BEBIDAS = [
    ("Agua limpia", 35, 0), ("Agua purificada", 40, 0), ("Agua turbia", 30, 30), ("Agua de río o pozo", 30, 10), ("Agua de lluvia", 30, 0), ("Leche", 25, 0),
    ("Jugo de fruta", 25, 0), ("Té o infusión", 20, 0), ("Café de cereal", 18, 0), ("Refresco", 20, 0), ("Bebida energética", 15, 0), ("Agua con sal", 25, 0),
    ("Caldo", 25, 0), ("Agua helada de manantial", 40, 0), ("Hidromiel sin alcohol", 20, 0),
]
ALCOHOLES = [
    ("Cerveza", "+1 CAR −1 PER", "2%"), ("Vino", "+1 CAR −1 AGI", "2%"), ("Licor fuerte", "+2 FUE −2 PER −1 AGI", "5%"), ("Destilado casero", "+2 RES −2 INT −2 PER", "8%"),
    ("Hidromiel", "+1 CAR", "2%"), ("Sidra", "+1 CAR −1 PER", "2%"), ("Ron de ribera", "+2 FUE −1 PER", "5%"), ("Licor de hierbas", "+1 todos −1 PER", "3%"),
    ("Aguardiente", "+2 RES −2 PER", "6%"), ("Cerveza negra", "+1 FUE", "2%"), ("Vino espeso", "+1 CAR −1 INT", "3%"), ("Cóctel de la casa", "+1 CAR +1 SUE −1 PER", "3%"),
]
MEDICINAS = [
    ("Vendaje", "+10 PV; quita Sangrando", 3), ("Vendaje reforzado", "+20 PV; quita Sangrando y Herido", 8), ("Inyector curativo", "+30 PV", 25), ("Inyector curativo mayor", "+60 PV", 60),
    ("Kit médico", "+40 PV; cura 1 estado", 40), ("Antibiótico", "quita Enfermo", 15), ("Antídoto", "quita Envenenado", 15), ("Antiveneno de criatura", "quita veneno de insectos y marinos blandos", 20),
    ("Anti-contaminación", "−150 contaminación; −1 PER 1 h", 30), ("Protector de contaminación", "+40% resistencia 4 h", 20), ("Analgésico", "ignora Herido 2 h", 10),
    ("Suero de reanimación", "levanta a un Incapacitado con 30% PV", 80), ("Inyector de calma", "quita Asustado/Confundido", 15), ("Ungüento de hierbas", "+8 PV; ayuda a cicatrizar", 6),
    ("Tintura para la fiebre", "baja fiebre en 1 h", 8), ("Parche de frío", "resiste frío 2 h", 5), ("Pomada para quemaduras", "quita Quemadura", 8), ("Jarabe para la tos", "quita Tos", 5),
    ("Compresa", "+5 PV; quita golpe", 3), ("Té de hierbas curativas", "+6 PV; calma", 4), ("Sales para el desmayo", "despierta de aturdimiento", 4), ("Férula", "cura Herido de pierna", 10),
    ("Vacuna contra la plaga", "inmunidad a Enfermo 24 h", 40), ("Desintoxicante", "quita Adicto en 3 días", 50), ("Repelente de insectos", "−50% encuentros de insectos 4 h", 8),
    ("Filtro de agua", "purifica 3 litros", 12), ("Manta térmica", "descanso en frío sin penalidad", 10), ("Pastilla de sal", "recupera sed leve", 3), ("Gotas para los ojos", "quita Cegado", 6),
]
QUIMICOS = [
    ("Estimulante de reflejos", "+20% iniciativa, +3 PA, 2 h", "15%"), ("Estimulante de fuerza", "+3 FUE, 1 h", "15%"), ("Estimulante de percepción", "+3 PER, 1 h", "15%"),
    ("Estimulante de resistencia", "+3 RES, +20 PV temporales, 1 h", "15%"), ("Furia química", "+25% daño −15% defensa, 10 rondas", "20%"), ("Concentración", "+10% impacto +1 INT, 1 h", "12%"),
    ("Velocidad", "+5 PA, movimiento +50%, 20 min", "18%"), ("Bloqueador de dolor", "−25% daño recibido, 5 rondas", "12%"), ("Estimulante de carisma", "+3 CAR, 1 h", "10%"),
    ("Estimulante de suerte", "+2 SUE, 1 h", "10%"), ("Mezcla militar", "+2 FUE +2 RES −1 INT, 1 h", "25%"), ("Tónico de brío", "+1 AGI y +5 PA, 30 min", "8%"),
    ("Tónico nocturno", "visión en oscuridad, 1 h", "6%"), ("Tónico de calma", "−15% Asustado, 1 h", "6%"), ("Tónico de agallas", "+10 PV temporales, 1 h", "8%"),
]
AMBIENTALES = [
    ("Antorcha", "luz 1 h"), ("Bengala", "luz 1 h; revela"), ("Repelente", "−50% encuentros de insectos o animales 4 h"), ("Filtro de aire", "inmune a gas 30 min"),
    ("Cantimplora llena", "3 usos de agua"), ("Yesca y combustible", "enciende fuego"), ("Manta o saco", "descanso exterior −5% riesgo"), ("Cebo de comida", "atrae criaturas T1-T3"),
    ("Gas lacrimógeno", "−30% impacto enemigo"), ("Ración de viaje (pack)", "hambre −40, sed −20, 3 usos"), ("Kit de primeros auxilios", "3 vendajes + 1 antídoto"),
    ("Carpa", "descanso seguro en exterior (normal)"), ("Hamaca", "descanso en árbol o barco"), ("Linterna a pila", "luz 4 h"), ("Cuerda", "trepar o atar"),
    ("Red de pesca", "pesca 2 comidas/hora"), ("Caña de pescar", "pesca 1 comida/hora"), ("Trampa para animales", "caza 1 pieza/6 h"), ("Cantimplora grande", "6 usos"),
    ("Odre de vino", "3 usos de alcohol"), ("Mapa del terreno", "revela cuadras de un territorio"), ("Brújula", "evita el desvío en viaje"), ("Catalejo", "+10 PER para detectar"),
]

CHATARRA = [
    "Chatarra metálica", "Tuercas y tornillos", "Cableado", "Circuito", "Pegamento o cinta", "Tela", "Cuero", "Químicos base", "Combustible", "Batería o célula",
    "Piezas mecánicas", "Madera", "Cuerda", "Resorte", "Engranaje", "Lámina de aluminio", "Tubería", "Vidrio", "Plástico duro", "Cable de acero", "Imán", "Bombilla",
    "Cristal de cuarzo", "Mecha", "Pólvora", "Tinta", "Papel", "Hueso", "Pluma", "Escama", "Piel curtida", "Seda silvestre", "Resina", "Cera", "Sal", "Carbón", "Hierro en bruto",
    "Cobre", "Plomo", "Azufre", "Cuarzo pulido", "Cuerno", "Hilo", "Aguja", "Remache", "Soldadura", "Pantalla rota", "Motor pequeño", "Bomba de agua", "Válvula",
    "Altavoz", "Micrófono", "Lente", "Sensor", "Antena", "Chip de memoria", "Cinta de grabación", "Pila vieja", "Rueda", "Cadena de bicicleta", "Ancla", "Vela de barco",
]
HERRAMIENTAS = [
    "Ganzúa", "Palanca", "Kit de reparación", "Kit de herramientas", "Soplete", "Cuerda y garfio", "Cizalla", "Multiherramienta", "Terminal portátil", "Kit de supervivencia",
    "Kit de cocina", "Pico y pala", "Hacha de leñador", "Sierra", "Martillo de trabajo", "Destornilladores", "Llave inglesa", "Linterna", "Detector de metales", "Detector de movimiento",
    "Radio portátil", "Cámara de fotos", "Lupa", "Brújula", "Compás de navegación", "Sextante", "Catalejo", "Mapa vacío", "Pluma y tinta", "Cuaderno",
    "Banco de trabajo plegable", "Yunque pequeño", "Fuelle", "Caña de pescar", "Red", "Trampa", "Cantimplora", "Carpa", "Hamaca", "Escalera plegable",
]
LLAVES_DATOS = [
    "Llave de puerta", "Llave de caja fuerte", "Llave maestra", "Tarjeta de acceso nivel 1", "Tarjeta de acceso nivel 3", "Tarjeta de acceso nivel 5", "Código escrito", "Combinación de caja",
    "Holocinta", "Disco de datos", "Nota", "Carta", "Diario", "Mapa de papel", "Plano de fabricación", "Libro", "Revista", "Partitura", "Fotografía", "Medallón",
]
DOCUMENTOS = [
    "Manual de supervivencia", "Libro de cocina", "Libro de herramientas", "Libro de medicina de campo", "Libro de mapas", "Libro de historia local", "Libro de cuentos",
    "Libro de oficios", "Libro de criaturas", "Libro de plantas", "Libro de navegación", "Libro de química básica", "Revista de inventos", "Revista de aventuras",
    "Registro de un guardia", "Registro de un capataz", "Carta de despedida", "Orden de captura", "Contrato", "Testamento",
]
MEJORAS = [
    ("Mira", "+8% impacto largo"), ("Silenciador", "ruido 0; −10% daño"), ("Cargador ampliado", "+50% munición"), ("Culata reforzada", "−retroceso"),
    ("Cañón largo", "+alcance"), ("Afilado", "+10% daño cuerpo a cuerpo"), ("Recalibrado", "+5% daño; −5 durabilidad"), ("Refrigeración", "evita recalentar"),
    ("Empuñadura", "+5% impacto"), ("Contrapeso", "−1 PA"), ("Hoja serrada", "sangrado +10%"), ("Mango reforzado", "+10 durabilidad"),
    ("Linterna acoplada", "ilumina"), ("Láser de apuntado", "+5% impacto"), ("Bayoneta", "ataque cuerpo a cuerpo con arma larga"), ("Culata plegable", "−2 peso"),
    ("Forro térmico", "resistencia al frío"), ("Placa extra", "+1 RD torso"), ("Refuerzo de rodillas", "+1 RD piernas"), ("Bolsillos extra", "+5 carga"),
    ("Almohadillas silenciosas", "+3 sigilo"), ("Capucha", "+2 sigilo en bosque"), ("Sellado hermético", "resiste gas"), ("Filtro cambiable", "extiende la máscara"),
]
VALOR = [
    "Anillo", "Collar", "Reloj", "Brújula antigua", "Medalla", "Moneda antigua", "Cuadro", "Estatuilla", "Cubiertos de plata", "Botella rara", "Joya del bosque",
    "Perla", "Coral", "Concha rara", "Piedra tallada", "Máscara ceremonial", "Instrumento musical", "Libro raro", "Mapa del tesoro", "Cofre pequeño",
    "Juguete antiguo", "Muñeca de trapo", "Peonza", "Cometa", "Tablero de juego", "Cartas de juego", "Dados", "Pelota", "Silbato", "Flauta de caña",
]
