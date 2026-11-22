# LORE_BOSQUE · EL BOSQUE DE LOS MIL SENDEROS (bloque 1/8)

## MUNDO, TONO Y PROTAGONISTA
**Nombre del mundo:** El Bosque de los Mil Senderos. **Moneda:** bellotas. **Tono:** aventura luminosa tipo cuento de exploradores: amistad, mapas, fogatas y deberes; peligro de criaturas, sin crueldad ni muerte.
Un gran bosque atravesado por mil senderos, con una ciudad al oeste, campos al noroeste, montañas al norte, un pantano al sur, selvas de comercio al este de la ciudad y un territorio de gigantes amistosos al este de los campos. Los **Exploradores del Roble** son un grupo de niños que viste como los bandoleros de los cuentos de arqueros del bosque: capas verdes, arcos de práctica y banderines. Parece un grupo de scouts, pero es una civilización propia, con campamentos, reglas, mapas y oficios, cuidada por mujeres adultas. Hay muchas facciones infantiles y muchas de mujeres.
**Protagonista:** Lucas (una sola palabra de nombre), `edad: niño`. Un chico de ciudad, curioso y algo asustadizo, que se pierde en el bosque. Es de **nivel 1**.
**Compañero inicial:** Yago (niño, desde el segundo uno).
**Arranque:** Lucas camina por la Senda de los Helechos cuando es atacado por un **insecto gigante hembra** (mantis) y no puede defenderse. Lo protege un grupo de exploradores y queda al cuidado del campamento del Claro del Roble Partido; de ahí parte la campaña. El niño que lo rescata es su compañero inicial.
**Estilo de nombres:** nombres de pila comunes de niños (Tobías, Lucho, Bruno…), **una sola palabra**; lugares con nombres de árboles, aves y accidentes del terreno (Roble Partido, Mirador del Halcón, Arroyo de las Piedras Lisas).
Este lore **usa todas las mecánicas** (01-99) y les da órdenes: lo que no figura aquí **no existe**; lo que figura se rige por el motor. No hay muerte (50): se arrastra a la cama o lugar de descanso más cercano.

## REPARTO: EDAD, APARIENCIA Y GRUPOS (órdenes a las mecánicas, bloque 50)
- `edades_permitidas: [niño, adulto]`. **Adultos:** apariencia **femenina** (todos los adultos son hembras, incluidas criaturas y enemigos).
- **Niños:** apariencia **masculina** (todos varones).
- **Excepciones:** los **alfas** son la única criatura de apariencia masculina (adultos).
- **Grupos separados:** las mujeres adultas y los niños **no conviven ni forman grupos juntos**; cada facción es solo de niños o solo de mujeres adultas.
- **Sin muerte:** los combates contra niños o bandas rivales son de derribo; nadie muere.
- **Seguridad (50):** ningún niño participa en contenido sexual, romántico ni de desnudez en ningún modo. Relaciones con niños: solo amistad, confianza y respeto.
- Los nombres de niños y compañeros son **una sola palabra**; los adultos usan `NPC-nnn` + palabras clave; los respawneables, `[facción o grupo]-nnn`.

## TERRITORIOS (7) Y SU POSICIÓN
Mapa de oeste a este y de sur a norte: **Pantano** en toda la punta sur; **Bosque Hondo** sobre el pantano; **Ciudad Esperanza** al oeste en el centro; **Campos** al noroeste; **Selvas del Comercio** al este de la ciudad; **Territorio Alfa** al este de los campos; **Montañas** en toda la punta norte.
| ID | Territorio | Posición | Formación vegetal | Clima | Relieve | Agua | Modificador | Niveles |
|---|---|---|---|---|---|---|---|---|
| T-BOS | El Bosque Hondo | sur (centro) | bosque cerrado | templado húmedo | colinas | arroyos | fértil | 1-8 |
| T-PAN | El Pantano del Extremo Sur | sur (punta) | humedal | templado húmedo | islas | pantano | pantanoso | 4-12 |
| T-CIU | Ciudad Esperanza | oeste (centro) | bosque abierto urbano | templado | llanura | arroyos y canales | fértil | 5-14 |
| T-CAM | Los Campos | noroeste | bosque de sabana | templado seco | llanura | arroyos | fértil | 8-18 |
| T-SEL | Las Selvas del Comercio | este (centro, al este de la ciudad) | selva | templado húmedo | colinas | río y arroyos | florecido | 12-22 |
| T-ALF | El Territorio Alfa | noreste (al este de los campos) | bosque de cañones | semiárido | cañones | arroyos secos | rocoso | 16-26 |
| T-MON | Las Montañas del Norte | norte (toda la punta) | bosque nevado | boreal | montaña | nieve y arroyos helados | nevado | 20-30 |

## CUADRO DE VARIANTES DE BOSQUE DE ESTE LORE (formación × clima × relieve, bloque 51)
| Variante | Formación | Clima | Relieve | Dónde aparece en este mapa |
|---|---|---|---|---|
| Bosque cerrado templado | bosque cerrado | templado húmedo | colinas | El Bosque Hondo (base) |
| Bosque de niebla | bosque de niebla | templado húmedo | colinas | Bosque de Niebla y hondonadas |
| Bosque pantanoso | bosque cerrado | templado húmedo | llanura | borde sur y Pantano del Extremo Sur |
| Humedal con islas de bosque | humedal | templado | islas | Pantano del Extremo Sur |
| Bosque abierto urbano | bosque abierto | templado | llanura | Ciudad Esperanza y su parque |
| Bosque de sabana | sabana arbolada | templado seco | llanura | Los Campos |
| Pradera de campos | pradera | templado | llanura | Los Campos (cultivos) |
| Selva templada | selva | templado húmedo | colinas | Las Selvas del Comercio |
| Selva de ribera | bosque de ribera | templado | valle | ríos y arroyos de la selva |
| Bosque de cañones | bosque abierto | semiárido | cañones | El Territorio Alfa |
| Bosque desértico | bosque abierto | árido | meseta | mesetas del Territorio Alfa |
| Bosque nevado | bosque cerrado | boreal | montaña | Las Montañas del Norte |
| Bosque ártico (cumbres) | bosque cerrado | ártico | glaciar | Cima Antigua |
| Roquedal nevado | roquedal | alta montaña | glaciar | cumbres |

## CRIATURAS: QUÉ TIPOS, QUÉ ESPECIES Y QUÉ FASES ESTÁN
**Temas activos y fases presentes:**
- T1 animales: fases **1, 2, 3** presentes; fases 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 **ausentes**.
- T14 alfa: fases **1, 2, 3** presentes; fases 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 **ausentes**.

**Temas ausentes (no existen en este lore):** cuernos y cuerpo robusto (T2), halo (T3), duende (T4), orco (T5), no muerta (T6), elemental (T7), vegetal (T8), mitológica (T9), artificial (T10), alienígena (T11), mutante (T12), amorfa de gran tamaño (T13; solo slimes pequeños de la fauna).

**Especies activas por territorio (pool de enemigos y fauna, IDs de los bloques 19-23, 52):**
- pool «bosque»: C-03, C-05, C-09, H-12, H-13, H-15, H-16, H-30, H-33, H-34, I-01, I-03, I-05, I-11, I-15, I-25, S-01, S-12.
- pool «pantano»: M-01, M-07, M-11, M-16, P-04, P-05, S-18, S-01, S-02, I-12, I-17.
- pool «ciudad»: C-02, C-04, H-02, H-12, I-16, I-19, S-01.
- pool «campos»: H-19, H-20, H-21, H-28, H-30, H-33, C-11, C-18, I-14, I-26, I-04.
- pool «selva»: I-23, I-24, I-27, I-28, I-26, H-43, H-44, C-05, M-17.
- pool «alfa»: C-18, C-19, H-16, H-29, H-31, I-27.
- pool «montana»: C-14, C-19, C-20, H-23, H-29, H-17, I-27, S-10.

**Todas las criaturas adultas son hembras** (apariencia femenina), incluidos los enemigos, los insectos, los lobos y los slimes. **La única excepción son los alfas.** Los animales aparecen solo en fases 1 a 3; no existen las fases 4 a 14 de animales (los humanos son niños y mujeres, fase 13). Los enemigos son fauna hostil (insectos, lobas, jabalíes, parásitos genéricos y slimes) y **bandas rivales de niños** (derribo no letal). Las variantes universales de origen sobrenatural, zombi o robótico están apagadas.

## LOS ALFAS (criatura nueva del lore, tema T14)
Los **alfas** son un tema nuevo (T14, bloque 52): criaturas independientes de los animales, emparentadas con los lobos, con su propia cadena de 14 fases. **En este lore solo existen las fases 1, 2 y 3**, y son **gigantes amistosos** al este de los campos (Territorio Alfa). Son **adultos y varones**: la única criatura de apariencia masculina del mapa.
- **Fase 1 (los más salvajes, de las alturas):** altísimos, de musculatura extrema, con mucho vello largo que rodea los músculos principales (en rulos o liso) y casi los cubre; mandíbula con dientes inferiores que sobresalen; cuerpo de orco de fantasía, aún más peludo y alto que un gorila. Viven en lugares altos y boscosos. **En este lore visten** taparrabos y prendas de piel de animal al estilo de la antigua Grecia.
- **Fase 2 (los más numerosos):** hipermusculados como un orco; vello largo y abundante *para un humano* pero escaso *para un lobo*: rodea los músculos principales sin cubrir abdominales ni pectorales, que se ven claramente; dentadura casi humana salvo los colmillos inferiores; sin garras ni colmillos superiores; cuerpo casi humanoide. **En este lore visten** ropa de estilo griego más moderna, de origen animal, mucho más trabajada y con tintes.
- **Fase 3 (los más humanos):** altos, hipermusculados pero no como un orco, con buena cantidad de grasa corporal; dientes inferiores grandes pero no sobresalientes. **Visten** ropa humana común.
**Conducta:** `[a completar por el autor]` (cordial, elegante y respetuosa en este lore). Territorio: Aldea de las Casas Grandes, Cañón de los Ecos, Meseta del Viento, Bosque Alto, Tótem de las Cumbres. Se rigen por 52 (territoriales, amistosos con quien los respeta). **No hay contenido sexual en ningún caso;** los detalles físicos de esta lista son solo de apariencia general y vestimenta.

# LORE_BOSQUE · EL BOSQUE DE LOS MIL SENDEROS (bloque 2/8)

## FACCIONES
| Facción | Tipo | Carácter | Territorio |
|---|---|---|---|
| Los Exploradores del Roble | infantil | protectores, curiosos, de reglas simples | El Bosque Hondo |
| Los Vigías del Mirador | infantil | atentos y silenciosos | El Bosque Hondo |
| La Banda del Arroyo | infantil (rival, no letal) | bravucones juguetones | El Bosque Hondo |
| Los Cartógrafos del Claro | infantil | meticulosos, soñadores | El Bosque Hondo |
| Los Rastreadores del Cañaveral | infantil | callados y resistentes | El Pantano del Extremo Sur |
| Los Constructores de la Ciudad | infantil | ingeniosos | Ciudad Esperanza |
| Los Recaderos de la Plaza | infantil | veloces y chismosos | Ciudad Esperanza |
| Los Cosechadores | infantil | trabajadores y alegres | Los Campos |
| Los Aprendices del Comercio | infantil | regateadores curiosos | Las Selvas del Comercio |
| Los Cazadores del Alba | infantil | disciplinados | Las Montañas del Norte |
| La Casa de las Hojas | mujeres adultas | cuidadoras, pacientes | El Bosque Hondo |
| Las Guardianas del Camino | mujeres adultas | justas y firmes | Todo el mapa |
| El Gremio de las Sembradoras | mujeres adultas | prácticas y generosas | Los Campos |
| Las Hermanas de la Ciudad | mujeres adultas | organizadas y diplomáticas | Ciudad Esperanza |
| La Compañía de las Mercaderas | mujeres adultas | astutas y cordiales | Las Selvas del Comercio |
| Las Curanderas del Pantano | mujeres adultas | sabias y reservadas | El Pantano del Extremo Sur |
| Los Alfas del Este | gigantes amistosos (varones, adultos) | territoriales y respetuosos | El Territorio Alfa |

Las facciones infantiles y las de mujeres adultas son **separadas**; los niños no dependen de adultos en sus facciones.

## JEFES DE TERRITORIO
| Jefe | Lugar | Especie base | Nivel | PV | Invocación |
|---|---|---|---|---|---|
| Reina Mantis | Colmena de las Mantis | I-15 | 7 | 300 | hasta 4 vivos, 3 ciclos |
| Madre del Fango | Nido de la Madre del Fango | S-13 | 12 | 500 | hasta 4 vivos, 3 ciclos |
| Matriarca de las Avispas | Nido de la Matriarca de las Avispas | I-04 | 16 | 660 | hasta 4 vivos, 3 ciclos |
| Soberana de las Selvas | Claro de la Soberana | I-26 | 22 | 900 | hasta 4 vivos, 3 ciclos |
| Gran Loba del Norte | Cima Antigua | C-18 | 30 | 1220 | hasta 4 vivos, 3 ciclos |

## UBICACIONES: EL BOSQUE HONDO
**El Bosque Hondo** · bosque cerrado · templado húmedo · colinas · arroyos · niveles 1-8.
- **Claro del Roble Partido** (segura, pueblo, 3 cuadras y 3 edificios).
  - Claro del Roble Partido, cuadra 1: Enfermería.
  - Claro del Roble Partido, cuadra 2: Mercado cubierto.
  - Claro del Roble Partido, cuadra 3: Kiosco.
- **Senda de los Helechos** (normal, exterior, nivel 1): 1 cuadra.
- **Arroyo de las Piedras Lisas** (normal, exterior, nivel 2): 1 cuadra.
- **Árbol Mayor** (segura, pueblo, 2 cuadras y 4 edificios).
  - Árbol Mayor, cuadra 1: Mercado cubierto, Enfermería.
  - Árbol Mayor, cuadra 2: Enfermería, Casa.
- **Cueva del Murmullo** (normal, interior, nivel 3): 1 cuadra.
- **Puente Colgante de la Garza** (normal, exterior, nivel 4): 1 cuadra.
- **Mirador del Halcón** (normal, exterior, nivel 4): 1 cuadra.
- **Cabaña del Ermitaño** (normal, interior, nivel 5): 1 cuadra.
- **Bosque de Niebla** (normal, exterior, nivel 6): 1 cuadra.
- **Hondonada del Zorzal** (normal, exterior, nivel 6): 1 cuadra.
- **Colmena de las Mantis** (hostil, interior, nivel 7): 1 cuadra.
- **Refugio de los Vigías** (segura, exterior, nivel 8, con cama): 1 cuadra.

## UBICACIONES: EL PANTANO DEL EXTREMO SUR
**El Pantano del Extremo Sur** · humedal · templado húmedo · islas · pantano · niveles 4-12.
- **Palafitos del Cañaveral** (segura, pueblo, 3 cuadras y 3 edificios).
  - Palafitos del Cañaveral, cuadra 1: Casa.
  - Palafitos del Cañaveral, cuadra 2: Herrería.
  - Palafitos del Cañaveral, cuadra 3: Estanco.
- **Camino de Tablones** (normal, exterior, nivel 5): 1 cuadra.
- **Laguna Turbia** (normal, exterior, nivel 6): 1 cuadra.
- **Isla de los Juncos** (normal, exterior, nivel 7): 1 cuadra.
- **Cueva del Fango** (hostil, interior, nivel 8): 1 cuadra.
- **Mirador del Cañaveral** (normal, exterior, nivel 9): 1 cuadra.
- **Puesto de los Rastreadores** (segura, exterior, nivel 10, con cama): 1 cuadra.
- **Nido de la Madre del Fango** (hostil, interior, nivel 12): 1 cuadra.

## UBICACIONES: CIUDAD ESPERANZA
**Ciudad Esperanza** · bosque abierto urbano · templado · llanura · arroyos y canales · niveles 5-14.
- **Ciudad Esperanza** (segura, ciudad grande, 19 cuadras y 48 edificios). Barrios: Plaza Mayor (3 cuadras); Barrio del Mercado (4 cuadras); Barrio de las Escuelas (3 cuadras); Barrio Viejo (3 cuadras); Barrio de los Talleres (3 cuadras); Barrio del Parque (3 cuadras).
  - Plaza Mayor, cuadra 1: Carpintería, Carpintería.
  - Plaza Mayor, cuadra 2: Escuela, Enfermería, Escuela.
  - Plaza Mayor, cuadra 3: Kiosco, Casa.
  - Barrio del Mercado, cuadra 1: Panadería, Cabaña.
  - Barrio del Mercado, cuadra 2: Cabaña, Enfermería, Heladería.
  - Barrio del Mercado, cuadra 3: Sala, Kiosco, Sala.
  - Barrio del Mercado, cuadra 4: Kiosco, Posada.
  - Barrio de las Escuelas, cuadra 1: Casa, Taller, Kiosco.
  - Barrio de las Escuelas, cuadra 2: Sala, Estanco.
  - Barrio de las Escuelas, cuadra 3: Posada, Cabaña, Enfermería.
  - Barrio Viejo, cuadra 1: Posada, Sala.
  - Barrio Viejo, cuadra 2: Kiosco, Biblioteca, Estanco.
  - Barrio Viejo, cuadra 3: Carpintería, Taller.
  - Barrio de los Talleres, cuadra 1: Biblioteca, Heladería, Escuela.
  - Barrio de los Talleres, cuadra 2: Escuela, Heladería, Mercado cubierto.
  - Barrio de los Talleres, cuadra 3: Heladería, Heladería.
  - Barrio del Parque, cuadra 1: Sala, Panadería, Almacén.
  - Barrio del Parque, cuadra 2: Almacén, Herrería.
  - Barrio del Parque, cuadra 3: Kiosco, Almacén, Heladería.
- **Muralla y Puertas** (segura, exterior, nivel 6): 1 cuadra.
- **Torre de las Campanas** (segura, interior, nivel 7): 1 cuadra.
- **Alcantarillas** (hostil, interior, nivel 8): 1 cuadra.
- **Parque de los Faroles** (normal, exterior, nivel 10): 1 cuadra.
- **Biblioteca Vieja** (normal, interior, nivel 11): 1 cuadra.
- **Taller de los Inventores** (segura, interior, nivel 12): 1 cuadra.
- **Casa de las Hojas** (segura, interior, nivel 14, con cama): 1 cuadra.

## UBICACIONES: LOS CAMPOS
**Los Campos** · bosque de sabana · templado seco · llanura · arroyos · niveles 8-18.
- **Aldea de la Cosecha** (segura, pueblo, 4 cuadras y 5 edificios).
  - Aldea de la Cosecha, cuadra 1: Taller.
  - Aldea de la Cosecha, cuadra 2: Enfermería.
  - Aldea de la Cosecha, cuadra 3: Mercado cubierto, Panadería.
  - Aldea de la Cosecha, cuadra 4: Panadería.
- **Granja de las Tres Acequias** (segura, exterior, nivel 9): 1 cuadra.
- **Molino Alto** (segura, interior, nivel 10): 1 cuadra.
- **Establo Comunal** (segura, interior, nivel 11): 1 cuadra.
- **Colinas del Trigo** (normal, exterior, nivel 13): 1 cuadra.
- **Corral Roto** (hostil, exterior, nivel 14): 1 cuadra.
- **Espantapájaros Viejo** (normal, exterior, nivel 15): 1 cuadra.
- **Nido de la Matriarca de las Avispas** (hostil, interior, nivel 16): 1 cuadra.
- **Camino de las Carretas** (normal, exterior, nivel 18): 1 cuadra.

## UBICACIONES: LAS SELVAS DEL COMERCIO
**Las Selvas del Comercio** · selva · templado húmedo · colinas · río y arroyos · niveles 12-22.
- **Mercado de las Lonas** (segura, pueblo, 4 cuadras y 8 edificios).
  - Mercado de las Lonas, cuadra 1: Taller, Panadería.
  - Mercado de las Lonas, cuadra 2: Herrería, Sala.
  - Mercado de las Lonas, cuadra 3: Enfermería, Biblioteca.
  - Mercado de las Lonas, cuadra 4: Almacén, Estanco.
- **Selva de los Mercaderes** (normal, exterior, nivel 13): 1 cuadra.
- **Sendero de las Carretas** (normal, exterior, nivel 14): 1 cuadra.
- **Posada de los Cuatro Vientos** (segura, interior, nivel 16, con cama): 1 cuadra.
- **Campamento de Caravanas** (segura, exterior, nivel 17): 1 cuadra.
- **Selva Cerrada** (hostil, exterior, nivel 19): 1 cuadra.
- **Puente del Comercio** (normal, exterior, nivel 20): 1 cuadra.
- **Claro de la Soberana** (hostil, exterior, nivel 22): 1 cuadra.

## UBICACIONES: EL TERRITORIO ALFA
**El Territorio Alfa** · bosque de cañones · semiárido · cañones · arroyos secos · niveles 16-26.
- **Aldea de las Casas Grandes** (segura, pueblo, 4 cuadras y 7 edificios).
  - Aldea de las Casas Grandes, cuadra 1: Kiosco, Carpintería.
  - Aldea de las Casas Grandes, cuadra 2: Enfermería, Posada.
  - Aldea de las Casas Grandes, cuadra 3: Escuela, Herrería.
  - Aldea de las Casas Grandes, cuadra 4: Biblioteca.
- **Cañón de los Ecos** (normal, exterior, nivel 17): 1 cuadra.
- **Meseta del Viento** (normal, exterior, nivel 19): 1 cuadra.
- **Bosque Alto** (normal, exterior, nivel 21): 1 cuadra.
- **Tótem de las Cumbres** (normal, exterior, nivel 22): 1 cuadra.
- **Paso del Eco** (normal, exterior, nivel 24): 1 cuadra.
- **Refugio de Piedra** (segura, interior, nivel 26, con cama): 1 cuadra.

## UBICACIONES: LAS MONTAÑAS DEL NORTE
**Las Montañas del Norte** · bosque nevado · boreal · montaña · nieve y arroyos helados · niveles 20-30.
- **Refugio de la Cumbre** (segura, interior, nivel 20, con cama): 1 cuadra.
- **Paso Blanco** (normal, exterior, nivel 21): 1 cuadra.
- **Aserradero Nevado** (normal, exterior, nivel 22): 1 cuadra.
- **Mirador de las Nubes** (normal, exterior, nivel 24): 1 cuadra.
- **Sendero del Cóndor** (normal, exterior, nivel 25): 1 cuadra.
- **Cueva de Hielo** (hostil, interior, nivel 27): 1 cuadra.
- **Valle Escondido** (segura, exterior, nivel 28, con cama): 1 cuadra.
- **Cima Antigua** (hostil, exterior, nivel 30): 1 cuadra.

# LORE_BOSQUE · EL BOSQUE DE LOS MIL SENDEROS (bloque 3/8)

## DÓNDE VIVE CADA NPC (por ubicación)
**NPC adultos incluidos:** 193 arquetipos (apariencia femenina). **NPC niños incluidos:** 75 (con un solo nombre). **Respawneables incluidos:** 64 plantillas (llevan nombre de facción o grupo + número). **Compañeros:** 32. El lore **puede agregar** más NPC, respawneables y compañeros con el mismo formato.

- **Claro del Roble Partido:** adultos NPC-001, NPC-002, NPC-003, NPC-004, NPC-005, NPC-006, NPC-007, NPC-008, NPC-009, NPC-010, NPC-011, NPC-012, NPC-035, NPC-039, NPC-205, NPC-215; niños Ezequiel (NIN-001), Bautista (NIN-002), Franco (NIN-003), Mateo (NIN-004), Bastián (NIN-005), Emilio (NIN-006).
- **Ciudad Esperanza:** adultos NPC-013, NPC-014, NPC-017, NPC-018, NPC-019, NPC-020, NPC-021, NPC-022, NPC-023, NPC-025, NPC-026, NPC-027, NPC-036, NPC-037, NPC-040, NPC-043, NPC-044, NPC-045, NPC-046, NPC-047, NPC-049, NPC-051, NPC-054, NPC-056, NPC-058, NPC-127, NPC-129, NPC-130, NPC-131, NPC-132, NPC-134, NPC-135, NPC-136, NPC-137, NPC-145, NPC-146, NPC-147, NPC-148, NPC-149, NPC-150, NPC-151, NPC-154, NPC-157, NPC-162, NPC-163, NPC-168, NPC-169, NPC-170, NPC-171, NPC-174, NPC-175, NPC-177, NPC-179, NPC-180, NPC-188, NPC-189, NPC-190, NPC-197, NPC-199, NPC-201, NPC-204, NPC-209, NPC-212, NPC-223, NPC-225; niños Leo (NIN-009), Lucho (NIN-010), Yeray (NIN-012), Horacio (NIN-015), Amadeo (NIN-028), Kai (NIN-031), Lautaro (NIN-041), Ciriaco (NIN-042), Valentín (NIN-043), Nacho (NIN-048), Hugo (NIN-059), Ian (NIN-060), Manu (NIN-066), Isaías (NIN-067), Baltasar (NIN-070), Thiago (NIN-075), Jerónimo (NIN-080).
- **Casa de las Hojas:** adultos NPC-015, NPC-059; niños Noel (NIN-030).
- **Aldea de la Cosecha:** adultos NPC-016, NPC-024, NPC-042, NPC-057, NPC-172, NPC-173, NPC-178, NPC-195, NPC-207, NPC-224; niños Wenceslao (NIN-008), Kevin (NIN-011), Jonás (NIN-068), Elián (NIN-078), Ramiro (NIN-085), Nicanor (NIN-089).
- **Aldea de las Casas Grandes:** adultos NPC-029, NPC-120, NPC-123, NPC-124, NPC-125, NPC-153, NPC-166, NPC-176, NPC-200, NPC-208, NPC-216, ALF-2; niños Sebas (NIN-033), Julián (NIN-053), Facu (NIN-061), Teo (NIN-082), Uriel (NIN-083).
- **Mercado de las Lonas:** adultos NPC-031, NPC-192; niños Gerardo (NIN-077), Vicente (NIN-088).
- **Palafitos del Cañaveral:** adultos NPC-038, NPC-041, NPC-050, NPC-191, NPC-193, NPC-194, NPC-211; niños Zoilo (NIN-007), Gonza (NIN-013), Saúl (NIN-029).
- **Bosque de Niebla:** adultos NPC-048, NPC-052; niños —.
- **Árbol Mayor:** adultos NPC-053, NPC-084, NPC-086, NPC-087, NPC-091, NPC-092, NPC-093, NPC-202; niños Herminio (NIN-040), Prudencio (NIN-065).
- **Bosque Alto:** adultos NPC-055; niños —.
- **Refugio de la Cumbre:** adultos NPC-067, NPC-069, NPC-075, NPC-076, NPC-080, NPC-159, NPC-185; niños Lorenzo (NIN-024).
- **Mirador del Cañaveral:** adultos NPC-068, NPC-073, NPC-081; niños —.
- **Refugio de los Vigías:** adultos NPC-070, NPC-161, NPC-213, NPC-214; niños —.
- **Puesto de los Rastreadores:** adultos NPC-071, NPC-183; niños Nahuel (NIN-019), Tobías (NIN-056), Dante (NIN-057).
- **Mirador del Halcón:** adultos NPC-072, NPC-077, NPC-110; niños Tadeo (NIN-076).
- **Muralla y Puertas:** adultos NPC-074, NPC-078, NPC-079, NPC-082, NPC-160; niños —.
- **Torre de las Campanas:** adultos NPC-083, NPC-085, NPC-088, NPC-089, NPC-090; niños —.
- **Arroyo de las Piedras Lisas:** adultos NPC-105; niños —.
- **Meseta del Viento:** adultos NPC-109, NPC-184, NPC-217, ALF-3; niños —.
- **Laguna Turbia:** adultos NPC-111, NPC-196; niños —.
- **Puente Colgante de la Garza:** adultos NPC-112; niños Lisandro (NIN-071).
- **Selva de los Mercaderes:** adultos NPC-113; niños Camilo (NIN-050), Cristian (NIN-054).
- **Parque de los Faroles:** adultos NPC-116, NPC-203; niños Ximo (NIN-025), Ulises (NIN-073).
- **Sendero de las Carretas:** adultos NPC-117, NPC-219; niños Ciro (NIN-062).
- **Cueva del Murmullo:** adultos NPC-118, NPC-121, NPC-138, NPC-139, NPC-140, NPC-141, NPC-142, NPC-143, NPC-144; niños Walter (NIN-034), Rodri (NIN-035), Maximiliano (NIN-036), Zair (NIN-037), Simón (NIN-038), Valen (NIN-039), Demian (NIN-084).
- **Valle Escondido:** adultos NPC-119; niños —.
- **Cabaña del Ermitaño:** adultos NPC-122, NPC-198; niños —.
- **Taller de los Inventores:** adultos NPC-133; niños —.
- **Tótem de las Cumbres:** adultos NPC-152, NPC-165, ALF-1; niños —.
- **Biblioteca Vieja:** adultos NPC-158; niños Ismael (NIN-027), Octavio (NIN-058).
- **Isla de los Juncos:** adultos NPC-164; niños —.
- **Camino de las Carretas:** adultos NPC-181; niños Marcos (NIN-072).
- **Paso del Eco:** adultos NPC-182, NPC-206; niños Renzo (NIN-020), Patricio (NIN-079).
- **Camino de Tablones:** adultos NPC-186; niños Iñaki (NIN-055).
- **Senda de los Helechos:** adultos NPC-187, NPC-220; niños Benja (NIN-081).
- **Cañón de los Ecos:** adultos NPC-210; niños —.
- **Campamento de Caravanas:** adultos NPC-218; niños —.
- **Molino Alto:** adultos —; niños Urbano (NIN-014).
- **Hondonada del Zorzal:** adultos —; niños Fabián (NIN-021).
- **Colinas del Trigo:** adultos —; niños Pablo (NIN-022), Erik (NIN-023).
- **Mirador de las Nubes:** adultos —; niños Silvestre (NIN-026).
- **Refugio de Piedra:** adultos —; niños Pedro (NIN-032), Alan (NIN-069).
- **Puente del Comercio:** adultos —; niños Abel (NIN-074).

## RESPAWNEABLES (facción o grupo + número)
Cada respawneable lleva el nombre de la facción o grupo del que viene + número de serie. Ejemplos de asignación:
- RSP-001 «Guardia [facción]» → Guardia [La Casa de las Hojas]-001
- RSP-002 «Guardia de puerta [ubicación]» → Guardia de puerta [Las Guardianas del Camino]-002
- RSP-003 «Patrulla [facción]» → Patrulla [El Gremio de las Sembradoras]-003
- RSP-004 «Soldado [facción]» → Soldado [Las Hermanas de la Ciudad]-004
- RSP-005 «Explorador [grupo]» → Explorador [Los Rastreadores del Cañaveral]-005
- RSP-006 «Cazador [grupo]» → Cazador [Las Curanderas del Pantano]-006
- RSP-008 «Bandido [grupo]» → Bandido [La Casa de las Hojas]-007
- RSP-015 «Cobrador [grupo]» → Cobrador [Las Guardianas del Camino]-008
- RSP-016 «Pueblerino de [ubicación]» → Pueblerino de [El Gremio de las Sembradoras]-009
- RSP-017 «Ciudadano de [ubicación]» → Ciudadano de [Las Hermanas de la Ciudad]-010
- RSP-018 «Ocupante de [ubicación]» → Ocupante de [La Compañía de las Mercaderas]-011
- RSP-019 «Trabajador de [ubicación]» → Trabajador de [Las Curanderas del Pantano]-012
- RSP-020 «Granjero de [ubicación]» → Granjero de [La Casa de las Hojas]-013
- RSP-021 «Pastor de [ubicación]» → Pastor de [Las Guardianas del Camino]-014
- RSP-022 «Minero de [ubicación]» → Minero de [El Gremio de las Sembradoras]-015
- RSP-026 «Vendedor ambulante de [ubicación]» → Vendedor ambulante de [Las Hermanas de la Ciudad]-016
- RSP-027 «Comerciante de caravana [caravana]» → Comerciante de caravana [La Compañía de las Mercaderas]-017
- RSP-028 «Guardia de caravana [caravana]» → Guardia de caravana [Las Curanderas del Pantano]-018
- RSP-029 «Peregrino [grupo]» → Peregrino [La Casa de las Hojas]-019
- RSP-030 «Viajero [ubicación]» → Viajero [Las Guardianas del Camino]-020
- RSP-031 «Mensajero [facción]» → Mensajero [El Gremio de las Sembradoras]-021
- RSP-032 «Obrero de [ubicación]» → Obrero de [Las Hermanas de la Ciudad]-022
- RSP-033 «Técnico de [facción]» → Técnico de [La Compañía de las Mercaderas]-023
- RSP-034 «Médico de campo [facción]» → Médico de campo [Las Curanderas del Pantano]-024
- RSP-035 «Enfermero de [facción]» → Enfermero de [La Casa de las Hojas]-025
- RSP-036 «Escriba de [facción]» → Escriba de [Las Guardianas del Camino]-026
- RSP-037 «Intendente de [facción]» → Intendente de [El Gremio de las Sembradoras]-027
- RSP-038 «Vigía de [facción]» → Vigía de [Las Hermanas de la Ciudad]-028
- RSP-039 «Recluta de [facción]» → Recluta de [Los Aprendices del Comercio]-029
- RSP-040 «Veterano de [facción]» → Veterano de [Las Curanderas del Pantano]-030
- RSP-041 «Oficial de [facción]» → Oficial de [La Casa de las Hojas]-031
- RSP-042 «Aprendiz de [oficio]» → Aprendiz de [Los Vigías del Mirador]-032
- RSP-043 «Artesano de [ubicación]» → Artesano de [El Gremio de las Sembradoras]-033
- RSP-044 «Tabernero de [ubicación]» → Tabernero de [Las Hermanas de la Ciudad]-034
- RSP-045 «Cocinero de [ubicación]» → Cocinero de [La Compañía de las Mercaderas]-035
- RSP-046 «Guardia de torre [facción]» → Guardia de torre [Las Curanderas del Pantano]-036
- RSP-047 «Huésped de [torre]» → Huésped de [La Casa de las Hojas]-037
- RSP-048 «Sirviente de [torre]» → Sirviente de [Las Guardianas del Camino]-038
- RSP-049 «Excluido de [grupo]» → Excluido de [El Gremio de las Sembradoras]-039
- RSP-050 «Habitante de [comunidad subterránea]» → Habitante de [Las Hermanas de la Ciudad]-040
El resto de las plantillas incluidas se instancian igual con la facción o ubicación que corresponda.

## COMPAÑEROS (solo femeninos o niños; el lore puede agregar más)
Se pueden usar desde el segundo uno. Máximo 3 activos (41). Personalidades extendidas: bloque de compañeros (catálogo).
| ID | Nombre (una sola palabra) | Arquetipo | Edad | Dónde se encuentra |
|---|---|---|---|---|
| K-1 | Yamila | perra leal de guardia (apariencia hembra) | neutro | Ciudad Esperanza |
| K-2 | Carla | cazadora de la región, veterana | adulto | Árbol Mayor |
| K-3 | Marina | guardia de caravana, bebedora de buen humor | adulto | Aldea de las Casas Grandes |
| K-4 | Helena | chica de la facción científica, curiosa | adulto | Ciudad Esperanza |
| K-5 | Wanda | guerrera de orden, disciplinada | adulto | Claro del Roble Partido |
| K-6 | Irene | exploradora de frontera | adulto | Ciudad Esperanza |
| K-7 | Inés | médica ambulante | adulto | Aldea de las Casas Grandes |
| K-8 | Olivia | mecánica de campo, ingeniosa | adulto | Ciudad Esperanza |
| K-9 | Julia | guía de supervivencia, mayor | adulto | Palafitos del Cañaveral |
| K-10 | Lucía | domadora de criaturas | adulto | Aldea de la Cosecha |
| K-11 | Valeria | cantante errante | adulto | Ciudad Esperanza |
| K-12 | Fiorella | ex contrabandista, astuta | adulto | Mercado de las Lonas |
| K-13 | Celeste | sacerdotisa viajera | adulto | Mercado de las Lonas |
| K-14 | Ximena | cartógrafa valiente | adulto | Ciudad Esperanza |
| K-15 | Zulema | ex guardia de torre | adulto | Aldea de la Cosecha |
| K-16 | Abril | ladrona arrepentida | adulto | Mercado de las Lonas |
| K-17 | Gala | robot de apoyo (apariencia a elección del lore) | neutro | Ciudad Esperanza |
| K-18 | Dolores | comerciante viajera, pragmática | adulto | Ciudad Esperanza |
| K-19 | Belén | campeona de torneos, humilde | adulto | Ciudad Esperanza |
| K-20 | Yago | niño amigo de la infancia, leal | niño | Claro del Roble Partido |
| K-21 | Rubén | niño explorador, entusiasta | niño | Ciudad Esperanza |
| K-22 | Gael | niño rastreador, callado | niño | Árbol Mayor |
| K-23 | Genaro | niño inventor, distraído | niño | Aldea de la Cosecha |
| K-24 | Joaquín | niño sanador, amable | niño | Claro del Roble Partido |
| K-25 | Olivier | niño recadero, veloz | niño | Ciudad Esperanza |
| K-26 | Santi | niño líder de grupo, carismático | niño | Mercado de las Lonas |
| K-27 | Damián | niño navegante, soñador | niño | Aldea de las Casas Grandes |
| K-28 | Orlando | niño grumete, obediente | niño | Ciudad Esperanza |
| K-29 | Fermín | niña estudiosa, brillante | niño | Árbol Mayor |
| K-30 | León | niña arquera, concentrada | niño | Ciudad Esperanza |
| K-31 | Tomi | niña pastora, protectora | niño | Mercado de las Lonas |
| K-32 | Quimey | niña mecánica de botes, ingeniosa | niño | Ciudad Esperanza |

# LORE_BOSQUE · EL BOSQUE DE LOS MIL SENDEROS (bloque 4/8)

## MISIONES PRINCIPALES (15)
Cada una instancia una misión base de MISIONES BASE. Orden por territorios: T-BOS → T-PAN → T-CIU → T-CAM → T-SEL → T-ALF → T-MON.
| ID | Nombre | Tipo | Nivel | Dador | Lugar | Recompensa |
|---|---|---|---|---|---|---|
| MP-01 | Perdido entre los helechos | ESC | 1 | NPC-110 | Mirador del Halcón | 290 XP |
| MP-02 | Rastros de la tía | FAM | 3 | NPC-093 | Árbol Mayor | 570 XP |
| MP-03 | La voz de la torre de señales | HCK | 5 | NPC-143 | Cueva del Murmullo | 850 XP |
| MP-04 | El saber de la biblioteca vieja | INV | 7 | Iñaki | Camino de Tablones | 1130 XP |
| MP-05 | El mapa que se mueve | PUZ | 9 | Zoilo | Palafitos del Cañaveral | 1410 XP |
| MP-06 | Las aguas del claro | ART | 11 | NPC-037 | Ciudad Esperanza | 1690 XP |
| MP-07 | Retomar el rastro hacia los campos | INV | 13 | NPC-019 | Ciudad Esperanza | 1970 XP |
| MP-08 | Rescate en las alturas | JEF | 15 | NPC-172 | Aldea de la Cosecha | 2250 XP |
| MP-09 | La semilla del Roble Mayor | ART | 17 | NPC-207 | Aldea de la Cosecha | 2530 XP |
| MP-10 | Las dos hermandades | BND | 19 | NPC-117 | Sendero de las Carretas | 2810 XP |
| MP-11 | Hasta la cima antigua | LMP | 21 | NPC-219 | Sendero de las Carretas | 3090 XP |
| MP-12 | El camino hacia el Roble Mayor | ESC | 23 | Sebas | Aldea de las Casas Grandes | 3370 XP |
| MP-13 | Tres tareas para despertarlo | HCK | 25 | NPC-184 | Meseta del Viento | 3650 XP |
| MP-14 | La decisión del bosque | BND | 27 | Lorenzo | Refugio de la Cumbre | 3930 XP |
| MP-15 | Después del bosque | EXP | 30 | NPC-067 | Refugio de la Cumbre | 4350 XP |

## MISIONES SECUNDARIAS BASE Y DE JEFE (todas incluidas)
Las 45 misiones secundarias base y una misión por jefe de territorio están **incluidas** en este lore.
| ID | Nombre | Tipo | Nivel |
|---|---|---|---|
| MS-01 | La bomba del pueblo | BND | 4 |
| MS-02 | Los de las jaulas | RSC | 5 |
| MS-03 | La torre y los excluidos | BND | 8 |
| MS-04 | Las páginas del guía | MAP | 14 |
| MS-05 | El robot que quería sentir | ENS | 16 |
| MS-06 | La comunidad con reglas propias | NEG | 20 |
| MS-07 | El culto del artefacto | INV | 6 |
| MS-08 | La cura prometida | CUR | 4 |
| MS-09 | Lo que vive en la mina | JEF | 5 |
| MS-10 | El pozo envenenado | INV | 10 |
| MS-11 | La caravana atrapada | ESC | 13 |
| MS-12 | El mercado de lo oculto | CTR | 16 |
| MS-13 | El concurso del pueblo | FIE | 24 |
| MS-14 | El juicio | DET | 6 |
| MS-15 | El fantasma del edificio | PUZ | 4 |
| MS-16 | Una voz sin cuerpo | HCK | 5 |
| MS-17 | La biblioteca que se cae | REC | 8 |
| MS-18 | El jardinero del páramo | RCL | 14 |
| MS-19 | Cacería para el trofeo | CAZ | 16 |
| MS-20 | El mensajero que no llegó | MSJ | 20 |
| MS-21 | Cuentas pendientes | COB | 3 |
| MS-22 | El vecino que no sale | FAM | 7 |
| MS-23 | El taller del inventor | FAB | 5 |
| MS-24 | La torreta rebelde | SAB | 8 |
| MS-25 | El mapa roto | ART | 12 |
| MS-26 | Las ofrendas | PUZ | 16 |
| MS-27 | La antena caída | CON | 28 |
| MS-28 | El rastro del ladrón | DET | 8 |
| MS-29 | La mascota perdida | DOM | 4 |
| MS-30 | El campamento sin agua | TRA | 5 |
| MS-31 | La enfermera sola | MED | 8 |
| MS-32 | Reunión de vecinos | NEG | 12 |
| MS-33 | El archivo cerrado | HCK | 17 |
| MS-34 | Plaga en el granero | AMN | 20 |
| MS-35 | El puente caído | CON | 1 |
| MS-36 | El duelo de cazadores | FIE | 4 |
| MS-37 | El traidor del puesto | DET | 5 |
| MS-38 | El regalo imposible | ART | 8 |
| MS-39 | La banda de la ruta | AMN | 14 |
| MS-40 | El refugio sin llave | REC | 26 |
| MS-41 | Voluntarios para la ronda | VIG | 20 |
| MS-42 | El dormitorio de los ruidos | LMP | 1 |
| MS-43 | Cruzar el desfiladero | ESC | 4 |
| MS-44 | El inventario del almacén | COM | 5 |
| MS-45 | Fuego en el barrio | DEF | 8 |
| MJ-01 | Cuidado con Reina Mantis | JEF | 7 |
| MJ-02 | Cuidado con Madre del Fango | JEF | 12 |
| MJ-03 | Cuidado con Matriarca de las Avispas | JEF | 16 |
| MJ-04 | Cuidado con Soberana de las Selvas | JEF | 22 |
| MJ-05 | Cuidado con Gran Loba del Norte | JEF | 30 |

# LORE_BOSQUE · EL BOSQUE DE LOS MIL SENDEROS (bloque 5/8)

## MISIONES PROPIAS DE CADA NPC
**Misiones propias de cada NPC (1 a 5 por NPC con misión):** 703 en total. Formato: NPC → «nombre» (tipo, nivel).
- NPC-001 [NPC-001]: «Una mesa para la autoridad» (NEG, n1)
- NPC-002 [NPC-002]: «Pistas de la esperanza» (INV, n2)
- NPC-003 [NPC-003]: «Ronda por el mercado» (VIG, n3) · «Noche de guardia» (DEF, n2) · «Guardia contra la plaga» (AMN, n2) · «El misterio del puesto» (INV, n1) · «Lo que no se dijo a tiempo» (MSJ, n1)
- NPC-004 [NPC-004]: «Letras y cuentas» (ENS, n1) · «Volver a casa» (FAM, n2) · «Devolver el cuaderno» (REC, n1) · «Lo que no se dijo a tiempo» (MSJ, n1)
- NPC-005 [NPC-005]: «Negocio en el bosque» (COM, n1) · «Provisión del mercado» (RCL, n2) · «Fiesta del granero» (FIE, n1) · «En busca del mapa» (REC, n3)
- NPC-006 [NPC-006]: «Manos a la obra» (FAB, n3) · «Antena y cable» (CON, n3)
- NPC-007 [NPC-007]: «Letras en la pared» (PUZ, n1) · «Código de la curiosidad» (HCK, n1)
- NPC-008 [NPC-008]: «El camino seguro» (ESC, n2)
- NPC-009 [NPC-009]: «Qué pasó en el puesto» (INV, n3) · «Código del silencio» (HCK, n1) · «Rastro del mapa» (REC, n1) · «Aprender con el silencio» (ENS, n3)
- NPC-010 [NPC-010]: «Lo que no se dijo a tiempo» (MSJ, n1)
- NPC-011 [NPC-011]: «Lo que se llevó el orden» (REC, n2) · «Un buen trato» (COM, n1)
- NPC-012 [NPC-012]: «Rastro de la reliquia» (REC, n1) · «Sin noticias» (FAM, n3) · «El misterio del bosque» (INV, n2)
- NPC-013 [NPC-013]: «A quién creerle» (BND, n5)
- NPC-014 [NPC-014]: «La muralla de la esperanza» (DEF, n7)
- NPC-015 [NPC-015]: «Antes del amanecer» (MED, n14) · «Secreto de la bondad» (PUZ, n15)
- NPC-016 [NPC-016]: «Material para el cansancio» (RCL, n8)
- NPC-017 [NPC-017]: «Lo que se llevó la palabra» (REC, n7) · «Negocio en el camino» (COM, n5) · «Carga callada» (CTR, n7)
- NPC-018 [NPC-018]: «Lo que se llevó la curiosidad» (REC, n5) · «Negocio en el refugio» (COM, n5) · «Todo lo que se junta» (RCL, n6)
- NPC-019 [NPC-019]: «Pedido especial» (COM, n6) · «Fiesta del granero» (FIE, n5) · «Todo lo que se junta» (RCL, n5) · «Carga hasta el puente» (TRA, n5)
- NPC-020 [NPC-020]: «Manos que sanan» (MED, n7) · «Negocio en el viejo túnel» (COM, n5)
- NPC-021 [NPC-021]: «Negocio en el mercado» (COM, n6) · «Compañía para el miedo» (ESC, n5)
- NPC-022 [NPC-022]: «El invento de la creatividad» (FAB, n7)
- NPC-023 [NPC-023]: «Libros que faltan» (ENS, n5) · «En busca de la reliquia» (REC, n7)
- NPC-024 [NPC-024]: «Rastro de la llave» (REC, n10) · «Antena y cable» (CON, n8)
- NPC-025 [NPC-025]: «Construir juntos» (CON, n5)
- NPC-026 [NPC-026]: «Rastro del cuaderno» (REC, n7) · «Reparación en el mercado» (FAB, n6)
- NPC-027 [NPC-027]: «Todo lo que se junta» (RCL, n7) · «Un buen trato» (COM, n6) · «El trofeo del silencio» (CAZ, n7) · «Rastro de la herramienta» (REC, n5)
- NPC-029 [NPC-029]: «Negocio en el bosque» (COM, n18) · «Volver a casa» (FAM, n17)
- NPC-031 [NPC-031]: «Entrega urgente» (MSJ, n14) · «Fiesta del puente» (FIE, n12) · «En busca de la brújula» (REC, n12)
- NPC-035 [NPC-035]: «Cartas sin dueño» (MSJ, n2)
- NPC-036 [NPC-036]: «Cartas sin dueño» (MSJ, n5) · «El concurso de la esperanza» (FIE, n5) · «Todo lo que se junta» (RCL, n6)
- NPC-037 [NPC-037]: «Sobre ruedas» (TRA, n6) · «Lo que no se dijo a tiempo» (MSJ, n5) · «Mercancía para el cansancio» (COM, n5)
- NPC-038 [NPC-038]: «Aprender con la protección» (ENS, n5) · «Puertas que no abren» (PUZ, n5)
- NPC-039 [NPC-039]: «Fiesta del camino» (FIE, n1) · «Aprender con la paciencia» (ENS, n2)
- NPC-040 [NPC-040]: «El misterio del refugio» (INV, n5) · «Código de la distracción» (HCK, n7) · «Provisión del pozo» (RCL, n7) · «Pruebas del muelle» (DET, n6)
- NPC-041 [NPC-041]: «Pieza única» (ART, n4)
- NPC-042 [NPC-042]: «Una mesa para el cansancio» (NEG, n8) · «La balanza del cansancio» (BND, n10) · «La sombra del cansancio» (DET, n10) · «Mercancía para el cansancio» (COM, n8)
- NPC-043 [NPC-043]: «Mediación» (NEG, n5) · «¿quién fue?» (DET, n7) · «Lo que no se dijo a tiempo» (MSJ, n5) · «Devolver el mapa» (REC, n6)
- NPC-044 [NPC-044]: «El misterio del granero» (INV, n6)
- NPC-045 [NPC-045]: «Un mensaje para la soledad» (MSJ, n5)
- NPC-046 [NPC-046]: «Qué pasó en el viejo túnel» (INV, n6) · «Letras y cuentas» (ENS, n5) · «Un mensaje para la esperanza» (MSJ, n6) · «Rastro de la herramienta» (REC, n6) · «Un buen trato» (COM, n6)
- NPC-047 [NPC-047]: «Cruzar con cuidado» (ESC, n7) · «Más allá del refugio» (EXP, n5) · «Los bordes del mapa» (MAP, n6)
- NPC-048 [NPC-048]: «Qué pasó en el granero» (INV, n7) · «Letras en la pared» (PUZ, n8) · «Lo que brilla en el mercado» (ART, n8)
- NPC-049 [NPC-049]: «El camino de vuelta» (FAM, n7)
- NPC-050 [NPC-050]: «Entrega urgente» (MSJ, n4) · «El misterio del viejo túnel» (INV, n5) · «Material para la esperanza» (RCL, n5)
- NPC-051 [NPC-051]: «Puesto del orden» (VIG, n7)
- NPC-052 [NPC-052]: «Un favor por otro» (COB, n8) · «Caso sin cerrar» (DET, n6)
- NPC-053 [NPC-053]: «Cartas sin dueño» (MSJ, n2)
- NPC-054 [NPC-054]: «Mercancía para la creatividad» (COM, n7)
- NPC-055 [NPC-055]: «Rastro de la reliquia» (REC, n23) · «Mercancía para el ingenio» (COM, n23) · «Todo lo que se junta» (RCL, n23)
- NPC-056 [NPC-056]: «El misterio del granero» (INV, n5) · «Letras en la pared» (PUZ, n7) · «Pruebas del mercado» (DET, n5) · «Entrega urgente» (MSJ, n6)
- NPC-057 [NPC-057]: «Antes del amanecer» (MED, n9)
- NPC-058 [NPC-058]: «Pedido especial» (COM, n6) · «Material para la generosidad» (RCL, n6)
- NPC-059 [NPC-059]: «Un buen trato» (COM, n15)
- NPC-067 [NPC-067]: «A quién creerle» (BND, n22) · «Resistir en el taller» (DEF, n22)
- NPC-068 [NPC-068]: «El camino seguro» (ESC, n11) · «Cuando no alcanza el orgullo» (AMN, n9)
- NPC-069 [NPC-069]: «Qué pasó en el taller» (INV, n22) · «Reiniciar el viejo túnel» (HCK, n21)
- NPC-070 [NPC-070]: «Defender lo propio» (DEF, n8) · «El jefe del viejo túnel» (JEF, n8) · «Guardia contra los saqueadores» (AMN, n9) · «Qué pasó en el puesto» (INV, n10)
- NPC-071 [NPC-071]: «Un buen trato» (COM, n12) · «Rastro del cuaderno» (REC, n10)
- NPC-072 [NPC-072]: «En busca del cuaderno» (REC, n6) · «Algo que funcione» (FAB, n4) · «Escolta hasta el camino» (ESC, n4) · «Noche de guardia» (DEF, n4)
- NPC-073 [NPC-073]: «Puesto de la esperanza» (VIG, n10) · «Rutas nuevas» (EXP, n11) · «Cruzar con cuidado» (ESC, n9)
- NPC-074 [NPC-074]: «Palabras en el puente» (NEG, n7) · «Atrapado por los intrusos» (RSC, n7) · «Defender lo propio» (DEF, n6) · «Turno de noche» (VIG, n7)
- NPC-075 [NPC-075]: «Remedio para el cansancio» (MED, n21) · «Contra el veneno» (CUR, n21) · «Cuando no alcanza el cansancio» (AMN, n21)
- NPC-076 [NPC-076]: «La balanza de la frialdad» (BND, n22) · «Noche de guardia» (DEF, n20) · «Ronda por el puente» (VIG, n22) · «Qué pasó en el viejo túnel» (INV, n21) · «El camino seguro» (ESC, n20)
- NPC-077 [NPC-077]: «Puesto del silencio» (VIG, n4) · «Cuando no alcanza el silencio» (AMN, n6) · «La muralla del silencio» (DEF, n5)
- NPC-078 [NPC-078]: «Puesto de la esperanza» (VIG, n6) · «Letras y cuentas» (ENS, n7) · «Cruzar con cuidado» (ESC, n8) · «Defender lo propio» (DEF, n7)
- NPC-079 [NPC-079]: «Construir juntos» (CON, n6) · «Voz del mercado» (HCK, n8)
- NPC-080 [NPC-080]: «Tinta y senderos» (MAP, n21) · «Mapa del taller» (EXP, n21) · «El misterio del refugio» (INV, n22) · «Compañía para la valentía» (ESC, n21) · «Limpiar el refugio» (AMN, n20)
- NPC-081 [NPC-081]: «Última guardia» (JEF, n11) · «Cacería en el bosque» (CAZ, n11) · «Paz para el pueblo» (AMN, n10) · «La muralla del silencio» (DEF, n10)
- NPC-082 [NPC-082]: «Devolver el mapa» (REC, n7) · «Ruido en la noche» (INV, n8) · «Cuando no alcanza el silencio» (AMN, n7) · «Ojos abiertos» (VIG, n8) · «Defender lo propio» (DEF, n6)
- NPC-083 [NPC-083]: «A quién creerle» (BND, n7)
- NPC-084 [NPC-084]: «Lo que se llevó los nervios» (REC, n3) · «Pruebas del puente» (DET, n4)
- NPC-085 [NPC-085]: «Pistas de la esperanza» (INV, n9)
- NPC-086 [NPC-086]: «Día de feria» (FIE, n4) · «Faltan materiales» (RCL, n2) · «Un mensaje para la creatividad» (MSJ, n3) · «Rastro de la medalla» (REC, n4)
- NPC-087 [NPC-087]: «Turno de noche» (VIG, n2) · «Guardia contra los ladrones de camino» (AMN, n4) · «Palabras en el mercado» (NEG, n3) · «Cartas sin dueño» (MSJ, n3) · «Lo que se llevó el orden» (REC, n2)
- NPC-088 [NPC-088]: «Lo que brilla en el granero» (ART, n9) · «Pedido especial» (COM, n7) · «Entrega urgente» (MSJ, n8) · «En busca del cuaderno» (REC, n9) · «Pruebas del puente» (DET, n8)
- NPC-089 [NPC-089]: «Con unos o con otros» (BND, n8) · «Mediación» (NEG, n8) · «La sombra de la valentía» (DET, n9)
- NPC-090 [NPC-090]: «Con unos o con otros» (BND, n7) · «Palabras en el refugio» (NEG, n8) · «En busca del cuaderno» (REC, n7) · «La sombra de la terquedad» (DET, n8)
- NPC-091 [NPC-091]: «Respirar de nuevo» (CUR, n2) · «Antes del amanecer» (MED, n4)
- NPC-092 [NPC-092]: «La sombra de la esperanza» (DET, n3) · «Cartas sin dueño» (MSJ, n4) · «En busca de la reliquia» (REC, n3) · «Paz a medias» (NEG, n4)
- NPC-093 [NPC-093]: «Mediación» (NEG, n2) · «La sombra de la frialdad» (DET, n2) · «Lo que se llevó la frialdad» (REC, n2)
- NPC-105 [NPC-105]: «Pruebas del granero» (DET, n2) · «En busca de la herramienta» (REC, n4) · «Sin ser vistos» (INF, n2) · «Limpiar el pozo» (AMN, n3)
- NPC-109 [NPC-109]: «Carga hasta el camino» (TRA, n20) · «Escolta hasta el taller» (ESC, n20) · «Negocio de noche» (CTR, n20) · «Guardia contra los saqueadores» (AMN, n19)
- NPC-110 [NPC-110]: «Escolta hasta el camino» (ESC, n4) · «Defender lo propio» (DEF, n4) · «Rastro de la brújula» (REC, n6) · «Paz para el pueblo» (AMN, n5) · «Más allá del muelle» (EXP, n4)
- NPC-111 [NPC-111]: «Mercancía para los nervios» (COM, n6) · «Lo que no se dijo a tiempo» (MSJ, n7) · «El misterio del viejo túnel» (INV, n6) · «Mapa del viejo túnel» (EXP, n6) · «Devolver el cuaderno» (REC, n6)
- NPC-112 [NPC-112]: «El camino seguro» (ESC, n6) · «La salida del bosque» (RSC, n5) · «Cartas sin dueño» (MSJ, n6)
- NPC-113 [NPC-113]: «El misterio del camino» (INV, n14) · «Atrapado por los saqueadores» (RSC, n13) · «Guardia contra los intrusos» (AMN, n13)
- NPC-116 [NPC-116]: «Lo que no se dijo a tiempo» (MSJ, n11) · «No dejar a nadie atrás» (RSC, n11) · «Rutas nuevas» (EXP, n11) · «Cuando no alcanza la valentía» (AMN, n12)

# LORE_BOSQUE · EL BOSQUE DE LOS MIL SENDEROS (bloque 6/8)

## MISIONES PROPIAS DE CADA NPC
- NPC-117 [NPC-117]: «Cruzar con cuidado» (ESC, n16) · «Puertas que no abren» (PUZ, n15) · «Paz para el bosque» (AMN, n14)
- NPC-118 [NPC-118]: «El acertijo del puesto» (PUZ, n3) · «Ruido en la noche» (INV, n4)
- NPC-119 [NPC-119]: «Sin noticias» (FAM, n28) · «Letras en la pared» (PUZ, n28)
- NPC-120 [NPC-120]: «Código del silencio» (HCK, n17) · «Letras en la pared» (PUZ, n17)
- NPC-121 [NPC-121]: «Pieza única» (ART, n4)
- NPC-122 [NPC-122]: «Mercancía para la ambición» (COM, n7) · «Artefacto de la ambición» (ART, n6)
- NPC-123 [NPC-123]: «Letras y cuentas» (ENS, n18) · «Dibujar el pozo» (MAP, n16) · «Puertas que no abren» (PUZ, n17) · «Ruido en la noche» (INV, n16) · «Tesoro con condición» (ART, n17)
- NPC-124 [NPC-124]: «Material para la curiosidad» (RCL, n17) · «Antes del amanecer» (MED, n18)
- NPC-125 [NPC-125]: «Cacería en el granero» (CAZ, n16)
- NPC-127 [NPC-127]: «La presa del puesto» (CAZ, n5)
- NPC-129 [NPC-129]: «Provisión del muelle» (RCL, n7) · «Lo que brilla en el taller» (ART, n6) · «Carga hasta el viejo túnel» (TRA, n5)
- NPC-130 [NPC-130]: «El invento del ingenio» (FAB, n7) · «Una mano para el puesto» (CON, n5) · «Defender lo propio» (DEF, n6) · «Carga hasta el granero» (TRA, n6)
- NPC-131 [NPC-131]: «Limpiar el mercado» (AMN, n6) · «Confianza en el puente» (DOM, n6) · «Mercancía para el silencio» (COM, n7) · «Faltan recursos» (RCL, n7)
- NPC-132 [NPC-132]: «Una mano para el mercado» (CON, n6)
- NPC-133 [NPC-133]: «Entrega pesada» (TRA, n14) · «Contra el veneno» (CUR, n12) · «La muralla del cansancio» (DEF, n14)
- NPC-134 [NPC-134]: «Material para la superstición» (RCL, n7) · «Lo que vive en el muelle» (JEF, n7) · «Noche de guardia» (DEF, n7)
- NPC-135 [NPC-135]: «Voz del camino» (HCK, n6) · «Lo que se llevó la autoridad» (REC, n5) · «Paz para el puente» (AMN, n7) · «La muralla de la autoridad» (DEF, n5) · «Provisión del granero» (RCL, n5)
- NPC-136 [NPC-136]: «La muralla de la esperanza» (DEF, n7)
- NPC-137 [NPC-137]: «Día de feria» (FIE, n7)
- NPC-138 [NPC-138]: «Una mesa para la protección» (NEG, n3) · «Defender lo propio» (DEF, n4) · «La balanza de la protección» (BND, n3) · «Curiosidad de la protección» (EXP, n4)
- NPC-139 [NPC-139]: «Palabras en el puente» (NEG, n5) · «La muralla del ingenio» (DEF, n3) · «Rutas nuevas» (EXP, n3)
- NPC-140 [NPC-140]: «Cura en el pueblo» (MED, n3) · «Fiebre en el camino» (CUR, n3)
- NPC-141 [NPC-141]: «Compañía para el silencio» (ESC, n3) · «Curiosidad del silencio» (EXP, n4)
- NPC-142 [NPC-142]: «Resistir en el taller» (DEF, n5) · «Ronda por el mercado» (VIG, n3) · «Paz a medias» (NEG, n4)
- NPC-143 [NPC-143]: «Pedido especial» (COM, n3) · «Lo que se llevó el orden» (REC, n5) · «Resistir en el granero» (DEF, n4)
- NPC-144 [NPC-144]: «El acertijo del taller» (PUZ, n3) · «Aprender con la sabiduría» (ENS, n4)
- NPC-145 [NPC-145]: «Lo que no se dijo a tiempo» (MSJ, n7) · «Voz del refugio» (HCK, n5) · «Lo que se llevó la soledad» (REC, n5) · «El misterio del refugio» (INV, n7) · «Puertas que no abren» (PUZ, n7)
- NPC-146 [NPC-146]: «Antena y cable» (CON, n6)
- NPC-147 [NPC-147]: «Qué pasó en el puesto» (INV, n5) · «Faltan provisiones» (RCL, n6) · «Respirar de nuevo» (CUR, n7)
- NPC-148 [NPC-148]: «Reiniciar el mercado» (HCK, n7) · «Pistas del silencio» (INV, n5)
- NPC-149 [NPC-149]: «Voz del muelle» (HCK, n7) · «Letras en la pared» (PUZ, n7) · «Ruido en la noche» (INV, n6)
- NPC-150 [NPC-150]: «Construir juntos» (CON, n7) · «Lo que sostiene a la esperanza» (SAB, n7) · «El acertijo del puesto» (PUZ, n6) · «En busca de la carta» (REC, n5)
- NPC-151 [NPC-151]: «Reiniciar el puente» (HCK, n5)
- NPC-152 [NPC-152]: «Manos a la obra» (FAB, n23)
- NPC-153 [NPC-153]: «Puertas que no abren» (PUZ, n18)
- NPC-154 [NPC-154]: «Negocio en el viejo túnel» (COM, n5)
- NPC-157 [NPC-157]: «Día de feria» (FIE, n5) · «Lo que no se dijo a tiempo» (MSJ, n7)
- NPC-158 [NPC-158]: «Dos caminos en el muelle» (BND, n12)
- NPC-159 [NPC-159]: «Puesto del cansancio» (VIG, n22) · «Defender lo propio» (DEF, n22) · «Paz para el refugio» (AMN, n21)
- NPC-160 [NPC-160]: «Tras la presa de la lealtad» (CAZ, n6) · «Escolta hasta el refugio» (ESC, n8) · «Puesto de la lealtad» (VIG, n7)
- NPC-161 [NPC-161]: «Fiebre en el muelle» (CUR, n9) · «Manos que sanan» (MED, n8) · «Qué pasó en el camino» (INV, n10)
- NPC-162 [NPC-162]: «Cruce discreto» (CTR, n7) · «Negocio en el puente» (COM, n5) · «Sobre ruedas» (TRA, n6)
- NPC-163 [NPC-163]: «Día de feria» (FIE, n7) · «Libros que faltan» (ENS, n6) · «Todo lo que se junta» (RCL, n6)
- NPC-164 [NPC-164]: «Provisión del puente» (RCL, n9) · «Mercancía para la alegría» (COM, n7) · «El concurso de la alegría» (FIE, n9) · «Lo que se llevó la alegría» (REC, n7)
- NPC-165 [NPC-165]: «Provisión del muelle» (RCL, n24)
- NPC-166 [NPC-166]: «Contra el veneno» (CUR, n16) · «Letras en la pared» (PUZ, n16) · «Artefacto de la esperanza» (ART, n16)
- NPC-168 [NPC-168]: «Lo que no se dijo a tiempo» (MSJ, n6) · «Premio inesperado» (FIE, n6) · «Material para la esperanza» (RCL, n6) · «En busca de la carta» (REC, n7)
- NPC-169 [NPC-169]: «Mercancía para la esperanza» (COM, n5) · «Caso sin cerrar» (DET, n6)
- NPC-170 [NPC-170]: «Ronda por el granero» (VIG, n6)
- NPC-171 [NPC-171]: «Qué pasó en el bosque» (INV, n5)
- NPC-172 [NPC-172]: «Fiesta del muelle» (FIE, n10) · «Provisión del taller» (RCL, n9) · «¿quién fue?» (DET, n8) · «Devolver la reliquia» (REC, n8)
- NPC-173 [NPC-173]: «Faltan materiales» (RCL, n9) · «La presa del muelle» (CAZ, n8)
- NPC-174 [NPC-174]: «Buscando a alguien» (FAM, n6) · «Lo que no se dijo a tiempo» (MSJ, n7) · «Premio inesperado» (FIE, n6)
- NPC-175 [NPC-175]: «Manos a la obra» (FAB, n5) · «Libros que faltan» (ENS, n7)
- NPC-176 [NPC-176]: «La balanza de la esperanza» (BND, n17) · «Palabras en el muelle» (NEG, n18) · «El concurso de la esperanza» (FIE, n16)
- NPC-177 [NPC-177]: «Guardia contra los intrusos» (AMN, n5)
- NPC-178 [NPC-178]: «Una mano para el taller» (CON, n10) · «Defender lo propio» (DEF, n10)
- NPC-179 [NPC-179]: «Algo que funcione» (FAB, n5) · «Pieza única» (ART, n5) · «En busca de la llave» (REC, n7) · «Provisión del granero» (RCL, n5)
- NPC-180 [NPC-180]: «Ruido en la noche» (INV, n5) · «Premio inesperado» (FIE, n5)
- NPC-181 [NPC-181]: «Sin noticias» (FAM, n18) · «Cartas sin dueño» (MSJ, n18) · «Cuando no alcanza el recuerdo» (AMN, n18)
- NPC-182 [NPC-182]: «Puesto de la esperanza» (VIG, n25) · «Una mano para el mercado» (CON, n24) · «Devolver la medalla» (REC, n24) · «Mapa del muelle» (EXP, n24) · «Cruzar con cuidado» (ESC, n25)
- NPC-183 [NPC-183]: «Aprender con la paciencia» (ENS, n10) · «Premio inesperado» (FIE, n10)
- NPC-184 [NPC-184]: «Puertas que no abren» (PUZ, n19) · «Remedio para la bondad» (MED, n21) · «Ruido en la noche» (INV, n21) · «Artefacto de la bondad» (ART, n19) · «Lo que se llevó la bondad» (REC, n19)
- NPC-185 [NPC-185]: «Confianza en el camino» (DOM, n21)
- NPC-186 [NPC-186]: «Rutas nuevas» (EXP, n6) · «Artefacto de la obsesión» (ART, n7)
- NPC-187 [NPC-187]: «Cuando no alcanza el silencio» (AMN, n1)
- NPC-188 [NPC-188]: «Un buen trato» (COM, n6) · «Reparación en el puesto» (FAB, n5)
- NPC-189 [NPC-189]: «Todo lo que se junta» (RCL, n6) · «Reparación en el refugio» (FAB, n6)
- NPC-190 [NPC-190]: «Piezas para la esperanza» (CON, n7) · «Algo que funcione» (FAB, n6) · «Faltan provisiones» (RCL, n7)
- NPC-191 [NPC-191]: «Resistir en el pueblo» (DEF, n4) · «Construir juntos» (CON, n6) · «Palabras en el taller» (NEG, n4)
- NPC-192 [NPC-192]: «Entrega pesada» (TRA, n13) · «Respirar de nuevo» (CUR, n13) · «Fiesta del mercado» (FIE, n13) · «Pruebas del bosque» (DET, n12)
- NPC-193 [NPC-193]: «Ruido en la noche» (INV, n4)
- NPC-194 [NPC-194]: «Libros que faltan» (ENS, n4)
- NPC-195 [NPC-195]: «Lección en el bosque» (ENS, n10) · «Buscando a alguien» (FAM, n9) · «Provisión del granero» (RCL, n10)
- NPC-196 [NPC-196]: «Carga hasta el refugio» (TRA, n8)
- NPC-197 [NPC-197]: «Cuando no alcanza el silencio» (AMN, n7) · «Lección en el pueblo» (ENS, n5) · «Día de feria» (FIE, n5) · «Mercancía para el silencio» (COM, n6)
- NPC-198 [NPC-198]: «Paz para el camino» (AMN, n5)
- NPC-199 [NPC-199]: «Secreto del genio» (PUZ, n6) · «Código del genio» (HCK, n7) · «Qué pasó en el pueblo» (INV, n7) · «Lo que se llevó el genio» (REC, n5)
- NPC-200 [NPC-200]: «Mirada de la protección» (DOM, n17) · «Todo lo que se junta» (RCL, n18) · «Qué pasó en el pozo» (INV, n18) · «Lo que brilla en el camino» (ART, n17)
- NPC-201 [NPC-201]: «Mediación» (NEG, n7) · «La balanza de la ambición» (BND, n6) · «Defender lo propio» (DEF, n7) · «La sombra de la ambición» (DET, n6)
- NPC-202 [NPC-202]: «Palabras en el pozo» (NEG, n4) · «Entrega urgente» (MSJ, n2)
- NPC-203 [NPC-203]: «Compañía para el orden» (ESC, n10) · «Entrega pesada» (TRA, n12)
- NPC-204 [NPC-204]: «Resistir en el granero» (DEF, n5)
- NPC-205 [NPC-205]: «Caso sin cerrar» (DET, n2) · «Pagar con tiempo» (COB, n1)
- NPC-206 [NPC-206]: «Provisión del puente» (RCL, n26) · «El camino seguro» (ESC, n25) · «Limpiar el muelle» (AMN, n26)
- NPC-207 [NPC-207]: «Limpiar el puente» (AMN, n10) · «Pruebas del puesto» (DET, n8)
- NPC-208 [NPC-208]: «La sombra de la ironía» (DET, n16)
- NPC-209 [NPC-209]: «Libros que faltan» (ENS, n5) · «Devolver la llave» (REC, n6)
- NPC-210 [NPC-210]: «Camino largo» (TRA, n17) · «Mirada de la paciencia» (DOM, n19) · «Devolver la reliquia» (REC, n18) · «Paz para el viejo túnel» (AMN, n18)
- NPC-211 [NPC-211]: «Antes del amanecer» (MED, n5) · «Una dosis a tiempo» (CUR, n6) · «Pedido especial» (COM, n4)
- NPC-212 [NPC-212]: «Fiesta del pueblo» (FIE, n7) · «Una mesa para la esperanza» (NEG, n6) · «Negocio en el puesto» (COM, n5) · «Entrega pesada» (TRA, n6)
- NPC-213 [NPC-213]: «Rutas nuevas» (EXP, n9) · «Una mano para el viejo túnel» (CON, n8) · «Resistir en el puesto» (DEF, n8) · «Puesto de la paciencia» (VIG, n9) · «Guardia contra las alimañas» (AMN, n8)
- NPC-214 [NPC-214]: «Cruzar con cuidado» (ESC, n9)
- NPC-215 [NPC-215]: «Pistas del silencio» (INV, n3) · «Lo que se llevó el silencio» (REC, n1) · «La máquina que no responde» (HCK, n2) · «Lo que no se dijo a tiempo» (MSJ, n3)
- NPC-216 [NPC-216]: «Secreto de la esperanza» (PUZ, n18) · «El misterio del pozo» (INV, n18)
- NPC-217 [NPC-217]: «Fiebre en el muelle» (CUR, n21) · «Secreto de la protección» (PUZ, n20)

# LORE_BOSQUE · EL BOSQUE DE LOS MIL SENDEROS (bloque 7/8)

## MISIONES PROPIAS DE CADA NPC
- NPC-218 [NPC-218]: «Un buen trato» (COM, n18) · «Material para la alegría» (RCL, n19) · «Premio inesperado» (FIE, n18) · «Lo que no se dijo a tiempo» (MSJ, n18) · «Cruzar con cuidado» (ESC, n18)
- NPC-219 [NPC-219]: «Cuando no alcanza el silencio» (AMN, n15) · «Confianza en el muelle» (DOM, n16) · «El trofeo del silencio» (CAZ, n16)
- NPC-220 [NPC-220]: «El camino seguro» (ESC, n2) · «Más allá del pueblo» (EXP, n3) · «Guardia contra los intrusos» (AMN, n3) · «Lo que no se dijo a tiempo» (MSJ, n1)
- NPC-223 [NPC-223]: «La sombra de la astucia» (DET, n7) · «El cofre del puesto» (INF, n6) · «Lo que no se declara» (CTR, n6) · «Sobre ruedas» (TRA, n7)
- NPC-224 [NPC-224]: «Voz del bosque» (HCK, n10) · «El invento de la timidez» (FAB, n8) · «Lo que se llevó la timidez» (REC, n9) · «Día de feria» (FIE, n9) · «¿quién fue?» (DET, n8)
- NPC-225 [NPC-225]: «Remedio para la sabiduría» (MED, n7) · «Provisión del puesto» (RCL, n5) · «Contra el veneno» (CUR, n7) · «Cartas sin dueño» (MSJ, n5) · «Fiesta del mercado» (FIE, n5)
- Ezequiel [NIN-001]: «El camino de vuelta» (FAM, n2)
- Bautista [NIN-002]: «Cruzar con cuidado» (ESC, n1) · «Buscando a alguien» (FAM, n3) · «Lo que se llevó la lealtad» (REC, n2) · «El misterio del puente» (INV, n1) · «Voz del puente» (HCK, n3)
- Franco [NIN-003]: «Resistir en el puente» (DEF, n2) · «Guardia contra las alimañas» (AMN, n3)
- Mateo [NIN-004]: «Escolta hasta el refugio» (ESC, n2)
- Bastián [NIN-005]: «Aprender con el genio» (ENS, n2)
- Emilio [NIN-006]: «El invento del ingenio» (FAB, n2)
- Zoilo [NIN-007]: «Antes del amanecer» (MED, n4) · «Material para la valentía» (RCL, n4) · «Cartas sin dueño» (MSJ, n6) · «Día de feria» (FIE, n5) · «Caso sin cerrar» (DET, n5)
- Wenceslao [NIN-008]: «Cartas sin dueño» (MSJ, n8) · «Camino largo» (TRA, n8) · «Pedido especial» (COM, n8) · «Provisión del pozo» (RCL, n9) · «Premio inesperado» (FIE, n8)
- Leo [NIN-009]: «Pistas de la esperanza» (INV, n7) · «Lo que no se dijo a tiempo» (MSJ, n6) · «Fiesta del refugio» (FIE, n7) · «Devolver el cuaderno» (REC, n6)
- Lucho [NIN-010]: «Rastro del mapa» (REC, n6) · «Pruebas del puesto» (DET, n6)
- Kevin [NIN-011]: «Rastro del cuaderno» (REC, n8) · «En silencio» (INF, n10) · «Mediación» (NEG, n8)
- Yeray [NIN-012]: «Buscando a alguien» (FAM, n7) · «Devolver la reliquia» (REC, n7) · «¿quién fue?» (DET, n5)
- Gonza [NIN-013]: «Faltan provisiones» (RCL, n6) · «Día de feria» (FIE, n6) · «Pruebas del granero» (DET, n6)
- Urbano [NIN-014]: «Confianza en el muelle» (DOM, n11) · «Cuando no alcanza el silencio» (AMN, n10) · «Negocio en el taller» (COM, n10) · «Noche de guardia» (DEF, n11)
- Horacio [NIN-015]: «Faltan recursos» (RCL, n5) · «Resistir en el pozo» (DEF, n6) · «Entrega pesada» (TRA, n7)
- Nahuel [NIN-019]: «Puesto del silencio» (VIG, n11) · «Cartas sin dueño» (MSJ, n10)
- Renzo [NIN-020]: «Hoja en blanco» (MAP, n24)
- Fabián [NIN-021]: «La sombra de la paciencia» (DET, n7) · «Tras la presa de la paciencia» (CAZ, n6)
- Pablo [NIN-022]: «Resistir en el refugio» (DEF, n13) · «Tras la presa del orgullo» (CAZ, n13) · «Compañía para el orgullo» (ESC, n14) · «Un mensaje para el orgullo» (MSJ, n15)
- Erik [NIN-023]: «Los bordes del mapa» (MAP, n14) · «Rutas nuevas» (EXP, n14) · «Paz para el muelle» (AMN, n15) · «Cartas sin dueño» (MSJ, n14)
- Lorenzo [NIN-024]: «La muralla de la lealtad» (DEF, n22) · «Puesto de la lealtad» (VIG, n22) · «El camino seguro» (ESC, n20)
- Ximo [NIN-025]: «Mediación» (NEG, n10) · «Compañía para la valentía» (ESC, n10)
- Silvestre [NIN-026]: «Cartas sin dueño» (MSJ, n25) · «Carga hasta el taller» (TRA, n24) · «Cuando no alcanza los nervios» (AMN, n24)
- Ismael [NIN-027]: «Remedio para la esperanza» (MED, n11) · «Una dosis a tiempo» (CUR, n11) · «Mediación» (NEG, n13) · «Cartas sin dueño» (MSJ, n11)
- Amadeo [NIN-028]: «Reparación en el pueblo» (FAB, n6) · «Tesoro con condición» (ART, n6) · «Construir juntos» (CON, n6) · «La sombra de la distracción» (DET, n5)
- Saúl [NIN-029]: «Lección en el camino» (ENS, n6) · «Rastro de la carta» (REC, n6)
- Noel [NIN-030]: «Ruido en la noche» (INV, n16) · «El concurso de la esperanza» (FIE, n16) · «Caso sin cerrar» (DET, n14) · «En busca del cuaderno» (REC, n16)
- Kai [NIN-031]: «Día de feria» (FIE, n6)
- Pedro [NIN-032]: «Confianza en el bosque» (DOM, n28) · «La presa del pozo» (CAZ, n26)
- Sebas [NIN-033]: «Material para la paciencia» (RCL, n18) · «Criatura herida» (DOM, n16) · «Lo que brilla en el taller» (ART, n18) · «Secreto de la paciencia» (PUZ, n17)
- Walter [NIN-034]: «Cartas sin dueño» (MSJ, n3) · «Una mesa para la desconfianza» (NEG, n3)
- Rodri [NIN-035]: «A quién creerle» (BND, n5) · «Una mesa para el ingenio» (NEG, n4) · «Resistir en el granero» (DEF, n4) · «Curiosidad del ingenio» (EXP, n5) · «Rastro de la llave» (REC, n4)
- Maximiliano [NIN-036]: «Defender lo propio» (DEF, n3) · «Puesto del orden» (VIG, n5)
- Zair [NIN-037]: «Más allá del mercado» (EXP, n3) · «Cruzar con cuidado» (ESC, n5) · «La muralla del silencio» (DEF, n4) · «Palabras en el granero» (NEG, n3)
- Simón [NIN-038]: «El misterio del refugio» (INV, n3) · «Cartas sin dueño» (MSJ, n4) · «Noche de guardia» (DEF, n3)
- Valen [NIN-039]: «Lo que se llevó la curiosidad» (REC, n3) · «Pieza única» (ART, n4) · «Noche de guardia» (DEF, n4) · «Más allá del taller» (EXP, n5)
- Herminio [NIN-040]: «Cuando no alcanza la lealtad» (AMN, n3) · «Sin noticias» (FAM, n3)
- Lautaro [NIN-041]: «Premio inesperado» (FIE, n7)
- Ciriaco [NIN-042]: «El concurso de la esperanza» (FIE, n5)
- Valentín [NIN-043]: «Confianza en el puesto» (DOM, n7) · «El camino de vuelta» (FAM, n5)
- Nacho [NIN-048]: «La balanza de la bravuconería» (BND, n6) · «En silencio» (INF, n6)
- Camilo [NIN-050]: «El trofeo del silencio» (CAZ, n14) · «Faltan recursos» (RCL, n13) · «Cartas sin dueño» (MSJ, n14)
- Julián [NIN-053]: «Manos a la obra» (FAB, n16) · «Aprender con la curiosidad» (ENS, n16)
- Cristian [NIN-054]: «Sobre ruedas» (TRA, n13) · «Cartas sin dueño» (MSJ, n14) · «En busca de la medalla» (REC, n13)
- Iñaki [NIN-055]: «Escolta hasta el pueblo» (ESC, n5)
- Tobías [NIN-056]: «Respirar de nuevo» (CUR, n10) · «Remedio para la esperanza» (MED, n11) · «Compañía para la esperanza» (ESC, n11)
- Dante [NIN-057]: «Pistas de la timidez» (INV, n10)
- Octavio [NIN-058]: «Día de feria» (FIE, n13) · «Todo lo que se junta» (RCL, n11) · «Palabras en el bosque» (NEG, n11) · «Lo que se llevó la alegría» (REC, n11)
- Hugo [NIN-059]: «Cartas sin dueño» (MSJ, n7) · «Ruido en la noche» (INV, n7)
- Ian [NIN-060]: «Entrega pesada» (TRA, n6)
- Facu [NIN-061]: «En busca de la brújula» (REC, n16) · «Noche de guardia» (DEF, n17) · «Negocio en el refugio» (COM, n18)
- Ciro [NIN-062]: «Sin noticias» (FAM, n15) · «La salida del granero» (RSC, n16) · «Limpiar el refugio» (AMN, n14)
- Prudencio [NIN-065]: «El camino seguro» (ESC, n2) · «Buscando a alguien» (FAM, n3) · «Premio inesperado» (FIE, n4)
- Manu [NIN-066]: «El misterio del camino» (INV, n6) · «Reiniciar el puesto» (HCK, n7)
- Isaías [NIN-067]: «Entrega urgente» (MSJ, n5) · «Código de la esperanza» (HCK, n5)
- Jonás [NIN-068]: «Dibujar el camino» (MAP, n10)
- Alan [NIN-069]: «Lección en el bosque» (ENS, n27) · «La máquina que no responde» (HCK, n27) · «Pieza única» (ART, n26)
- Baltasar [NIN-070]: «Mercancía para la creatividad» (COM, n5) · «Algo que funcione» (FAB, n5) · «La sombra de la creatividad» (DET, n6)
- Lisandro [NIN-071]: «Compañía para la valentía» (ESC, n5) · «Defender lo propio» (DEF, n4) · «Más allá del puesto» (EXP, n6) · «Devolver la herramienta» (REC, n5)
- Marcos [NIN-072]: «Puesto de la esperanza» (VIG, n20)
- Ulises [NIN-073]: «Todo lo que se junta» (RCL, n10)
- Abel [NIN-074]: «El trofeo de la esperanza» (CAZ, n20) · «Más allá del bosque» (EXP, n22) · «Devolver la brújula» (REC, n22) · «Cartas sin dueño» (MSJ, n20)
- Thiago [NIN-075]: «Faltan recursos» (RCL, n6) · «Paz para el pozo» (AMN, n7) · «Entrega pesada» (TRA, n6) · «Un buen trato» (COM, n5) · «Noche de guardia» (DEF, n5)
- Tadeo [NIN-076]: «Cacería en el puesto» (CAZ, n4)
- Gerardo [NIN-077]: «Algo que funcione» (FAB, n14) · «Lo que se llevó el ingenio» (REC, n12) · «Pruebas del pozo» (DET, n13)
- Elián [NIN-078]: «Lección en el taller» (ENS, n9)
- Patricio [NIN-079]: «La salida del muelle» (RSC, n24) · «Cura en el muelle» (MED, n24)
- Jerónimo [NIN-080]: «Premio inesperado» (FIE, n5)
- Benja [NIN-081]: «Cartas sin dueño» (MSJ, n1)
- Teo [NIN-082]: «Material para la protección» (RCL, n17) · «La muralla de la protección» (DEF, n17) · «Un buen trato» (COM, n16) · «Caso sin cerrar» (DET, n18) · «En busca del mapa» (REC, n17)
- Uriel [NIN-083]: «Premio inesperado» (FIE, n17)
- Demian [NIN-084]: «Curiosidad de la curiosidad» (EXP, n5)
- Ramiro [NIN-085]: «Libros que faltan» (ENS, n8)
- Vicente [NIN-088]: «En silencio» (INF, n12)
- Nicanor [NIN-089]: «A quién creerle» (BND, n9) · «Resistir en el pozo» (DEF, n9) · «Caso sin cerrar» (DET, n9) · «Palabras en el muelle» (NEG, n9) · «Premio inesperado» (FIE, n9)
- ALF-1 [ALF-1]: «Cruzar con cuidado» (ESC, n22) · «El acertijo del puesto» (PUZ, n22)
- ALF-2 [ALF-2]: «Paz a medias» (NEG, n16) · «Provisión del puente» (RCL, n16) · «La muralla de la esperanza» (DEF, n16)
- ALF-3 [ALF-3]: «Paz a medias» (NEG, n19) · «Cartas sin dueño» (MSJ, n19)

## MISIONES DESCARTADAS POR EL LORE
Se descartan: toda misión con esclavistas, cultos, saqueadores adultos, contrabando o mercenarios; todo NPC de lugares hostiles de adultos y de puerto; alcohol, apuestas, casino y préstamos; los temas T2-T13; las fases 4-14 de animales; la fase 14 de humanos. Las misiones que dependían de esos NPC no aparecen.

## OBJETOS DEL LORE
- **Armas (no letales para personas):** Palo de práctica, Bastón de roble, Bastón reforzado, Lanza de exploradores (punta roma), Cayado del Roble Mayor; arcos y hondas de práctica, redes y trampas de red (bloques de armas, solo no letales).
- **Comida y bebida:** viandas, frutas del bosque, miel, pan de campo, guisos, té de hierbas, agua de arroyo hervida. **Sin alcohol ni químicos.**
- **Medicina:** vendas, ungüentos de hierbas, tinturas, compresas, férulas. **Ropa:** capas verdes, chalecos de lona, botas de exploración; armaduras ligeras de explorador (E1-E4), Armadura del guardián (E5).
- **Objetos generales:** mapas, brújulas, catalejos, cuerdas, cuadernos, linternas, banderines, silbatos, instrumentos. **Moneda:** bellotas.

# LORE_BOSQUE · EL BOSQUE DE LOS MIL SENDEROS (bloque 8/8)

## CONFIG_LORE FINAL
```
LORE = El Bosque de los Mil Senderos
MONEDA = bellotas
NECESIDADES = on    CONTAMINACION = off    MODULO_EXTERNO = off    NIVEL_MAX = 30

TERRITORIOS = [El Bosque Hondo, El Pantano del Extremo Sur, Ciudad Esperanza, Los Campos, Las Selvas del Comercio, El Territorio Alfa, Las Montañas del Norte]
UBICACIONES = 60 (con 39 cuadras y 78 edificios)

REPARTO = {
  edades_permitidas: [niño, adulto], apariencia_adultos: femenina, apariencia_niños: masculina,
  excepciones: [{T14 alfa: masculina}], grupos_separados: [[adultos, niños]], sin_muerte: true }

CRIATURAS = { temas_activos: [T1 animales, T14 alfa],
  fases_activas: {T1 animales: [1, 2, 3], T14 alfa: [1, 2, 3]},
  modificadores_apagados: [Infernal, Demoníaca, Celestial, Zombi, Robótica, Alienígena], fases_ausentes: todas las demás }

NPC = { incluidos: 193 adultos + 75 niños, agregados: [] }
COMPANEROS = 32 (nombre de una sola palabra)
RESPAWNEABLES = 64 plantillas con facción o grupo
MISIONES = { principales: 15, secundarias_base: 45, de_jefe: 5, propias_de_npc: 703 }
JEFES = [Reina Mantis, Madre del Fango, Matriarca de las Avispas, Soberana de las Selvas, Gran Loba del Norte]
ARRANQUE = { protagonista: Lucas (niño), ubicación_inicial: Claro del Roble Partido, misión_inicial: MP-01 }
```
