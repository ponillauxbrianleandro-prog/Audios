"""Cuadros de las 14 fases por tema (bloque 18) y compatibilidad de variantes universales (bloque 24)."""

# clave, nombre del tema (palabra que acompana a Criatura), ejemplo, partes de la fase 2, rasgos de la fase 6, equipo tipico,
# variantes V2/V3, fases raras, variantes incompatibles
TEMAS = [
    ("T1", "animales", "lobo, vaca, pulpo, mantis o slime pequeño", "rostro y torso", "pelaje, garras, dientes, patas", "pieles, cuerdas y herramientas simples",
     ("Rabioso", "Alfa de grupo"), {13, 14}, {"Robótica"}),
    ("T2", "con cuernos y cuerpo robusto", "bestia cornuda (dragón, demonio o bestia de garra)", "rostro y hombros", "cuernos, cola, escamas, piel gruesa", "placas y adornos de hueso",
     ("Acorazado", "Señor del linaje"), set(), {"Celestial"}),
    ("T3", "con halo", "guardián, mensajero o sanador con aro luminoso", "rostro y postura", "halo luminoso, alas, brillo", "túnicas y armadura de luz",
     ("Resplandeciente", "Guía"), set(), {"Demoníaca", "Infernal", "Zombi", "Corrupta"}),
    ("T4", "duende", "duende, trasgo, gnomo, kobold o hada", "orejas y manos", "orejas puntiagudas, talla pequeña, agilidad", "chalecos, bolsillos y herramientas chicas",
     ("Travieso", "Rey de duendes"), set(), {"Robótica", "Alienígena"}),
    ("T5", "orco", "orco, ogro, troll o gigante", "mandíbula y torso", "mandíbula fuerte, piel gruesa, talla grande", "armaduras toscas y mazas",
     ("Guerrero", "Caudillo"), set(), {"Robótica"}),
    ("T6", "no muerta", "zombi, necrófago, esqueleto o espectro", "rostro y postura", "piel marchita, huesos, aura fría", "restos de ropa y armas oxidadas",
     ("Rápido", "Horda"), {10, 11, 9}, {"Celestial", "Regenerativa"}),
    ("T7", "elemental", "chispa, gota, terrón, soplo o cristal de hielo", "silueta y extremidades", "cuerpo de fuego, agua, tierra o aire", "adornos naturales",
     ("Furioso", "Primigenio"), {8, 9, 10, 11, 12, 13, 14}, {"Zombi", "Parasitada", "Controlada", "Robótica"}),
    ("T8", "vegetal", "brote, hongo, enredadera, árbol o planta carnívora", "ramas y rostro", "corteza, raíces, esporas, ramas", "fibras y tejidos naturales",
     ("Espinoso", "Anciano"), {8, 9, 10, 11, 12}, {"Robótica", "Zombi"}),
    ("T9", "mitológica", "grifo, quimera, unicornio, fénix o hipogrifo", "rostro y postura", "alas, cuernos, plumaje, cola", "adornos rituales",
     ("Ancestral", "Primigenio"), set(), {"Robótica"}),
    ("T10", "artificial", "dron, robot, androide o cyborg", "chasis y rostro", "chasis, sensores, articulaciones", "módulos y blindaje",
     ("Blindado", "Prototipo"), {9, 10, 11, 12}, {"Zombi", "Parasitada", "Demoníaca", "Celestial", "Regenerativa", "Vegetalizada"}),
    ("T11", "alienígena", "criatura de otro mundo", "rostro y proporciones", "piel extraña, órganos ajenos, brillo", "dispositivos extraños",
     ("Adaptado", "Anciano"), set(), {"Celestial", "Demoníaca"}),
    ("T12", "mutante", "humano mutado o experimento de laboratorio", "rostro y cuerpo", "deformidades, regeneración, tamaño", "ropa remendada",
     ("Brutal", "Prototipo"), set(), set()),
    ("T13", "amorfa", "slime, gelatina o masa", "silueta y superficie", "cuerpo gelatinoso, divisible", "ninguno; objetos absorbidos",
     ("Corrosivo", "Rey"), {8, 9, 10, 11, 12, 13, 14}, {"Robótica", "Blindada"}),
    ("T14", "alfa", "alfa (emparentado con los lobos)", "rostro y torso", "musculatura extrema, vello largo, dientes inferiores", "pieles, telas y ropa humana según lore",
     ("Veterano", "Guardián del territorio"), set(), {"Robótica"}),
]

VARIANTES_UNIVERSALES = [
    "Demoníaca", "Infernal", "Celestial", "Corrupta", "Zombi", "Parasitada", "Controlada", "Alienígena", "Robótica", "Biomecánica", "Experimental", "Quimérica",
    "Mutada", "Radiactiva", "Domesticada", "Anciana", "Rabiosa", "Alfa/Líder", "Gigante", "Enana", "Blindada", "Regenerativa", "Veloz", "Bioluminiscente",
    "Albina", "Cristalizada", "Gelatinosa", "Vegetalizada", "Mineralizada", "Espectral", "Fantasmal", "Elemental",
]

FRASES = {
    1: "{ej} sin ningún rasgo humano; actúa por instinto.",
    2: "{ej} con {p2} que recuerdan a lo humano; conserva su estructura propia y no tiene manos.",
    3: "{ej} erguido que usa sus miembros delanteros como manos; todavía no habla.",
    4: "{ej} de cuerpo humanoide completo y erguido; **desde esta fase se comunica**.",
    5: "Mitad {ej}, mitad humano en un mismo cuerpo (quimera); habla y vive en sociedad.",
    6: "Humano con anatomía de {ej}: {r6}; altura y tamaño notables; manos humanas.",
    7: "Persona de aspecto muy humano con rasgos sutiles de {ej}; personalidad bien formada.",
    8: "Persona que se considera {ej}; usa prótesis o accesorios permanentes que reemplazan partes del cuerpo.",
    9: "Persona con traje o disfraz completo de {ej}; quiere sentirse un ser tierno e inocente.",
    10: "Persona con accesorios de {ej} por identidad o gusto; no deja de verse humana.",
    11: "Trabajador/a con accesorios de {ej} por obligación laboral (espectáculo o atención al público).",
    12: "Persona con instintos marcados de {ej}, sin rasgos físicos.",
    13: "Humano normal y funcional, sin rasgos de {ej}.",
    14: "Humano que rechaza todo lo que no parece humano; evita a las criaturas de este tema.",
}
HABLA = {1: "No · —", 2: "No · —", 3: "No · patas-mano", 4: "Sí · patas-mano", 5: "Sí · manos", 6: "Sí · humanas", 7: "Sí · humanas", 8: "Sí · humanas + prótesis",
         9: "Sí · humanas (traje)", 10: "Sí · humanas", 11: "Sí · humanas", 12: "Sí · humanas", 13: "Sí · humanas", 14: "Sí · humanas"}
EQUIPO = {1: "ninguno", 2: "ninguno", 3: "objetos simples", 4: "E1", 5: "E3", 6: "E3", 7: "E4", 8: "E3", 9: "E2", 10: "E4", 11: "E1", 12: "E3", 13: "E5", 14: "E5"}
CONDUCTA = {1: "instinto", 2: "instinto, observa", 3: "curiosa o recelosa", 4: "negocia, cuida su territorio", 5: "social o territorial", 6: "variable, impone respeto",
            7: "sociable", 8: "imita a su tipo", 9: "juguetona, pacífica", 10: "individual", 11: "servicial", 12: "instintiva, iniciativa +10", 13: "normal", 14: "evita y rechaza"}
