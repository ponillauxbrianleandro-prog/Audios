# LORE_PIRATAS · EL MAR DE LAS MIL VELAS (bloque 1/7)

## MUNDO, TONO Y PROTAGONISTA
**Nombre del mundo:** El Mar de las Mil Velas. **Moneda:** doblones. **Tono:** aventura marina colorida: barcos de madera, mapas del tesoro, mareas y banderas; peligro de criaturas de agua, sin crueldad ni muerte.
Un mundo de selvas, ríos, pantanos y un mar abierto, con una ciudad de muchos barrios en el centro. Hay un **océano** (esquina inferior izquierda), un **río en forma de media luna muy delgada** que cruza el mapa desde la punta superior derecha hasta la izquierda, pasando por la ciudad, y un **pantano de islotes** (esquina inferior derecha). Ninguno de los tres se conecta directamente con otro, pero los tres tienen muelles. Cada uno tiene sus barcos: grandes navíos de madera en el mar (piratas), botes y barcazas en el río, y botes de fondo plano en el pantano. Todos los marineros, piratas y habitantes de la costa son **niños**; las **mujeres adultas** viven y trabajan en grupos separados.
**Protagonista:** Gaspar (una sola palabra de nombre), `edad: niño`. Un grumete curioso y aventurero que vive en la Casa del Farero y sueña con embarcar. Es de **nivel 1**.
**Compañero inicial:** Nicolás (niño, desde el segundo uno).
**Arranque:** Gaspar despierta en la Casa del Farero, en la ciudad. Un mensaje en una botella y el faro apagado dan comienzo a la campaña. Su compañero inicial es otro grumete del puerto.
**Estilo de nombres:** nombres de pila comunes de niños y niñas (Gaspar, Bartolo, Marinela, Estela…), **una sola palabra**; barcos y lugares con nombres de mar, astros y oficios (La Estrella Fugaz, Faro del Cabo, Puerto de las Gaviotas).
Este lore **usa todas las mecánicas** (01-99) y les da órdenes: lo que no figura aquí **no existe**; lo que figura se rige por el motor. No hay muerte (50): se arrastra a la cama o lugar de descanso más cercano.

## REPARTO: EDAD, APARIENCIA Y GRUPOS (órdenes a las mecánicas, bloque 50)
- `edades_permitidas: [niño, adulto]`. **Adultos:** apariencia **femenina** (solo mujeres adultas).
- **Niños:** apariencia **mixta** (niños y niñas).
- **Excepciones:** ninguna.
- **Grupos separados:** las mujeres adultas y los niños **no conviven ni forman grupos juntos**; cada facción es solo de niños o solo de mujeres adultas.
- **Sin muerte:** los combates contra niños o bandas rivales son de derribo; nadie muere.
- **Seguridad (50):** ningún niño participa en contenido sexual, romántico ni de desnudez en ningún modo. Relaciones con niños: solo amistad, confianza y respeto.
- Los nombres de niños y compañeros son **una sola palabra**; los adultos usan `NPC-nnn` + palabras clave; los respawneables, `[facción o grupo]-nnn`.

## TERRITORIOS (7) Y SU POSICIÓN
Mapa: **Océano** en la esquina inferior izquierda; **Pantano de los Islotes** en la inferior derecha; **Selva del Sur** entre el pantano, el mar y la ciudad; **Ciudad de los Siete Faroles** en el centro con muchos barrios; **Selva del Este** al este de la ciudad; **Selva del Norte** en la parte superior; el **Río Media Luna** atraviesa el mapa por el medio, de la punta superior derecha a la izquierda, pasando por la ciudad.
| ID | Territorio | Posición | Formación vegetal | Clima | Relieve | Agua | Modificador | Niveles |
|---|---|---|---|---|---|---|---|---|
| T-OCE | El Océano de las Mil Velas | esquina inferior izquierda | selva de islas | tropical húmedo | archipiélago | mar salado | costero | 6-16 |
| T-RIO | El Río Media Luna | franja delgada de la punta superior derecha a la izquierda, pasando por la ciudad | selva de galería | tropical húmedo | valle | río | fértil | 10-22 |
| T-PAN | El Pantano de los Islotes | esquina inferior derecha | humedal de islotes | templado húmedo | islas | pantano | pantanoso | 4-14 |
| T-SUR | La Selva del Sur | parte inferior, entre el pantano, el mar y la ciudad | selva irregular | tropical húmedo | colinas | arroyos y manglares | mixto | 1-9 |
| T-CIU | La Ciudad de los Siete Faroles | centro | selva urbana | tropical | llanura | río y canales | fértil | 1-12 |
| T-ESE | La Selva del Este | este de la ciudad | selva de sabana y cañones | tropical seco y húmedo | cañones y mesetas | arroyos | rocoso | 12-22 |
| T-NOR | La Selva del Norte | parte superior | selva con grandes irregularidades | tropical húmedo | montaña y mesetas | lagunas y cascadas | neblinoso | 18-30 |

## CUADRO DE VARIANTES DE SELVA DE ESTE LORE (formación × clima × relieve, bloque 51)
| Variante | Formación | Clima | Relieve | Dónde aparece en este mapa |
|---|---|---|---|---|
| Selva de islas | selva | tropical húmedo | archipiélago | El Océano de las Mil Velas |
| Selva de galería | bosque de ribera | tropical húmedo | valle | El Río Media Luna |
| Humedal de islotes | humedal | templado húmedo | islas | El Pantano de los Islotes |
| Manglar | manglar | tropical | costa | entradas del mar y del pantano |
| Selva irregular | selva alta y baja mezcladas | tropical húmedo | colinas | La Selva del Sur |
| Selva urbana | selva | tropical | llanura | La Ciudad de los Siete Faroles |
| Selva de sabana | selva baja | tropical seco | llanura | La Selva del Este |
| Selva de cañones | selva baja | tropical | cañones | La Selva del Este |
| Selva de montaña | selva alta | tropical húmedo | montaña | La Selva del Norte |
| Selva de niebla | selva | tropical húmedo | mesetas | Meseta de Niebla |

## CRIATURAS: QUÉ TIPOS, QUÉ ESPECIES Y QUÉ FASES ESTÁN
**Temas activos y fases presentes:**
- T1 animales: fases **1** presentes; fases 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 **ausentes**.

**Temas ausentes (no existen en este lore):** **todos los temas de criaturas** (T2-T14). No hay criaturas amistosas ni sociales: solo **enemigos** (fauna hostil de agua, pantano y selva).

**Especies activas por territorio (pool de enemigos y fauna, IDs de los bloques 19-23, 52):**
- pool «mar»: M-01, M-03, M-05, M-07, M-09, M-14, M-15, M-16, M-17, M-18.
- pool «rio»: M-02, M-04, M-08, M-13, P-04, S-02, S-18, I-17, I-12.
- pool «pantano»: P-05, P-04, S-18, S-01, S-12, M-11, I-12, I-16, I-19, H-08.
- pool «selva»: I-01, I-03, I-05, I-11, I-15, I-23, I-24, I-25, I-26, I-27, C-05, C-09, H-12, H-34, H-43.
- pool «ciudad»: C-02, H-02, I-16, I-19, S-01.

No hay criaturas de ningún tipo salvo los **enemigos**: marinos blandos agrandados (pulpos, medusas, calamares), seres de río y pantano (slimes y parásitos genéricos), insectos mutantes y animales de selva, siempre en **fase 1**. No existen las fases 2 a 14 de animales. Los humanos son niños y niñas (piratas, gente del río y del pantano, ciudadanos de aspecto medieval, comerciantes, «piratas de tierra») y mujeres adultas en grupos aparte; los combates entre humanos son de derribo, sin muerte.

## FACCIONES
| Facción | Tipo | Carácter | Territorio |
|---|---|---|---|
| Los Piratas de la Estrella Fugaz | infantil (mar) | carismáticos, aventureros; capitán bastante carismático | El Océano de las Mil Velas |
| Los Grumetes del Faro | infantil (mar) | obedientes y soñadores | El Océano de las Mil Velas |
| Los Contrabandistas de la Ensenada | infantil (mar, rival no letal) | astutos y juguetones | El Océano de las Mil Velas |
| Los Balseros de la Corriente | infantil (río) | ágiles y alegres | El Río Media Luna |
| La Hermandad del Remanso | infantil (río, estilo corsarios de río) | hábiles y leales | El Río Media Luna |
| Los Niños del Pantano | infantil (pantano) | callados y resistentes | El Pantano de los Islotes |
| Los Corsarios del Fango | infantil (pantano, estilo corsarios coloniales) | bravucones y bromistas | El Pantano de los Islotes |
| Los Piratas de Tierra | infantil (ciudad) | ingeniosos y leales | La Ciudad de los Siete Faroles |
| Los Aprendices del Puerto | infantil (ciudad) | curiosos y trabajadores | La Ciudad de los Siete Faroles |
| Los Recolectores de la Selva | infantil (selva) | ágiles y respetuosos | La Selva del Sur |
| Las Mercaderas del Puerto | mujeres adultas (ciudad) | astutas y cordiales | La Ciudad de los Siete Faroles |
| Las Curanderas de la Marea | mujeres adultas | sabias y reservadas | El Pantano de los Islotes |
| Las Patronas de los Astilleros | mujeres adultas | prácticas y estrictas | La Ciudad de los Siete Faroles |
| Las Guardianas del Muelle | mujeres adultas | justas y firmes | Todo el mapa |
| Las Cartógrafas de la Selva | mujeres adultas | meticulosas y curiosas | La Selva del Norte |

Las facciones infantiles y las de mujeres adultas son **separadas**; los niños no dependen de adultos en sus facciones.

## JEFES DE TERRITORIO
| Jefe | Lugar | Especie base | Nivel | PV | Invocación |
|---|---|---|---|---|---|
| Gran Pulpo Anciano | Gruta del Gran Pulpo | M-18 | 16 | 660 | hasta 4 vivos, 3 ciclos |
| Reina del Fango | Madriguera de la Reina del Fango | S-13 | 12 | 500 | hasta 4 vivos, 3 ciclos |
| Coloso del Río | Cueva detrás de la Cascada | M-17 | 20 | 820 | hasta 4 vivos, 3 ciclos |
| Señora de la Colmena | Ruinas del Templo | I-26 | 17 | 700 | hasta 4 vivos, 3 ciclos |
| Madre Avispa | Templo Hundido | I-04 | 25 | 1020 | hasta 4 vivos, 3 ciclos |

# LORE_PIRATAS · EL MAR DE LAS MIL VELAS (bloque 2/7)

## UBICACIONES: EL OCÉANO DE LAS MIL VELAS
**El Océano de las Mil Velas** · selva de islas · tropical húmedo · archipiélago · mar salado · niveles 6-16.
- **Puerto de las Gaviotas** (segura, pueblo, 4 cuadras y 7 edificios).
  - Puerto de las Gaviotas, cuadra 1: Tienda, Taller.
  - Puerto de las Gaviotas, cuadra 2: Biblioteca, Sala.
  - Puerto de las Gaviotas, cuadra 3: Tienda.
  - Puerto de las Gaviotas, cuadra 4: Sala, Almacén.
- **Barco Insignia La Estrella Fugaz** (segura, interior, nivel 7, con cama): 1 cuadra.
- **Faro del Cabo** (segura, interior, nivel 8, con cama): 1 cuadra.
- **Arrecife Hundido** (normal, exterior, nivel 9): 1 cuadra.
- **Isla de la Calavera** (hostil, exterior, nivel 10): 1 cuadra.
- **Bahía de la Tormenta** (normal, exterior, nivel 11): 1 cuadra.
- **Barco Hundido** (normal, interior, nivel 12): 1 cuadra.
- **Isla Escondida** (normal, exterior, nivel 13): 1 cuadra.
- **Ensenada de los Contrabandistas** (normal, exterior, nivel 14): 1 cuadra.
- **Gruta del Gran Pulpo** (hostil, interior, nivel 16): 1 cuadra.

## UBICACIONES: EL RÍO MEDIA LUNA
**El Río Media Luna** · selva de galería · tropical húmedo · valle · río · niveles 10-22.
- **Muelle de la Corriente** (segura, pueblo, 3 cuadras y 5 edificios).
  - Muelle de la Corriente, cuadra 1: Biblioteca, Panadería.
  - Muelle de la Corriente, cuadra 2: Almacén.
  - Muelle de la Corriente, cuadra 3: Panadería, Almacén.
- **Remanso de las Balsas** (normal, exterior, nivel 11): 1 cuadra.
- **Cascada Brava** (normal, exterior, nivel 12): 1 cuadra.
- **Puente de Lianas** (normal, exterior, nivel 14): 1 cuadra.
- **Islote del Arpón** (normal, exterior, nivel 15): 1 cuadra.
- **Embarcadero del Norte** (segura, exterior, nivel 16, con cama): 1 cuadra.
- **Campamento de los Balseros** (segura, exterior, nivel 18): 1 cuadra.
- **Vado de las Piedras** (normal, exterior, nivel 19): 1 cuadra.
- **Cueva detrás de la Cascada** (hostil, interior, nivel 20): 1 cuadra.
- **Mercado Flotante** (segura, pueblo, 3 cuadras y 5 edificios).
  - Mercado Flotante, cuadra 1: Tienda, Casa del farero.
  - Mercado Flotante, cuadra 2: Astillero chico, Cabaña.
  - Mercado Flotante, cuadra 3: Tienda.

## UBICACIONES: EL PANTANO DE LOS ISLOTES
**El Pantano de los Islotes** · humedal de islotes · templado húmedo · islas · pantano · niveles 4-14.
- **Palafitos de la Gente del Pantano** (segura, pueblo, 4 cuadras y 6 edificios).
  - Palafitos de la Gente del Pantano, cuadra 1: Almacén.
  - Palafitos de la Gente del Pantano, cuadra 2: Enfermería.
  - Palafitos de la Gente del Pantano, cuadra 3: Panadería, Enfermería.
  - Palafitos de la Gente del Pantano, cuadra 4: Fonda, Cabaña.
- **Muelle del Cañizal** (segura, exterior, nivel 5): 1 cuadra.
- **Islote de los Corsarios del Fango** (hostil, exterior, nivel 6): 1 cuadra.
- **Botes de la Niebla** (normal, exterior, nivel 7): 1 cuadra.
- **Bosque Anegado** (normal, exterior, nivel 9): 1 cuadra.
- **Laguna Verde** (normal, exterior, nivel 10): 1 cuadra.
- **Cueva de los Juncos** (normal, interior, nivel 11): 1 cuadra.
- **Madriguera de la Reina del Fango** (hostil, interior, nivel 12): 1 cuadra.
- **Torre de Vigía de Juncos** (segura, exterior, nivel 14, con cama): 1 cuadra.

## UBICACIONES: LA SELVA DEL SUR
**La Selva del Sur** · selva irregular · tropical húmedo · colinas · arroyos y manglares · niveles 1-9.
- **Mirador de los Tucanes** (normal, exterior, nivel 1): 1 cuadra.
- **Selva de Lianas** (normal, exterior, nivel 2): 1 cuadra.
- **Claro del Venado** (normal, exterior, nivel 3): 1 cuadra.
- **Sendero de los Helechos** (normal, exterior, nivel 4): 1 cuadra.
- **Cañón Verde** (normal, exterior, nivel 5): 1 cuadra.
- **Choza del Curandero** (segura, interior, nivel 6, con cama): 1 cuadra.
- **Manglar de Entrada** (normal, exterior, nivel 7): 1 cuadra.
- **Selva Cerrada** (hostil, exterior, nivel 8): 1 cuadra.
- **Campamento de los Recolectores** (segura, exterior, nivel 9, con cama): 1 cuadra.

## UBICACIONES: LA CIUDAD DE LOS SIETE FAROLES
**La Ciudad de los Siete Faroles** · selva urbana · tropical · llanura · río y canales · niveles 1-12.
- **La Ciudad de los Siete Faroles** (segura, ciudad grande, 25 cuadras y 61 edificios). Barrios: Puerto Viejo (4 cuadras); Barrio de los Mercaderes (4 cuadras); Barrio de las Velas (3 cuadras); Barrio Alto (3 cuadras); Barrio de los Astilleros (3 cuadras); Barrio de las Sombras (3 cuadras); Barrio del Río (3 cuadras); Plaza del Reloj (2 cuadras).
  - Puerto Viejo, cuadra 1: Casa del farero, Almacén.
  - Puerto Viejo, cuadra 2: Cabaña, Casa del farero, Posada.
  - Puerto Viejo, cuadra 3: Posada, Casa del farero, Casa.
  - Puerto Viejo, cuadra 4: Casa del farero, Casa del farero.
  - Barrio de los Mercaderes, cuadra 1: Enfermería, Taller.
  - Barrio de los Mercaderes, cuadra 2: Astillero chico, Biblioteca.
  - Barrio de los Mercaderes, cuadra 3: Tienda, Astillero chico, Casa del farero.
  - Barrio de los Mercaderes, cuadra 4: Panadería, Biblioteca.
  - Barrio de las Velas, cuadra 1: Taller, Herrería.
  - Barrio de las Velas, cuadra 2: Astillero chico, Panadería, Carpintería.
  - Barrio de las Velas, cuadra 3: Tienda, Cabaña, Panadería.
  - Barrio Alto, cuadra 1: Casa del farero, Cabaña, Enfermería.
  - Barrio Alto, cuadra 2: Taller, Casa del farero.
  - Barrio Alto, cuadra 3: Sala, Tienda.
  - Barrio de los Astilleros, cuadra 1: Tienda, Fonda, Tienda.
  - Barrio de los Astilleros, cuadra 2: Casa del farero, Panadería.
  - Barrio de los Astilleros, cuadra 3: Biblioteca, Casa, Carpintería.
  - Barrio de las Sombras, cuadra 1: Carpintería, Herrería, Enfermería.
  - Barrio de las Sombras, cuadra 2: Posada, Biblioteca, Cabaña.
  - Barrio de las Sombras, cuadra 3: Tienda, Tienda.
  - Barrio del Río, cuadra 1: Casa del farero, Enfermería.
  - Barrio del Río, cuadra 2: Taller, Panadería, Panadería.
  - Barrio del Río, cuadra 3: Enfermería, Taller.
  - Plaza del Reloj, cuadra 1: Enfermería, Casa del farero.
  - Plaza del Reloj, cuadra 2: Carpintería, Biblioteca.
- **Casa del Farero** (segura, interior, nivel 3, con cama): 1 cuadra.
- **Muralla y Puertas** (segura, exterior, nivel 5): 1 cuadra.
- **Biblioteca de las Bitácoras** (segura, interior, nivel 7): 1 cuadra.
- **Alcantarillas del Puerto** (hostil, interior, nivel 9): 1 cuadra.
- **Jardín de las Estatuas** (normal, exterior, nivel 12): 1 cuadra.

## UBICACIONES: LA SELVA DEL ESTE
**La Selva del Este** · selva de sabana y cañones · tropical seco y húmedo · cañones y mesetas · arroyos · niveles 12-22.
- **Selva de Sabana** (normal, exterior, nivel 12): 1 cuadra.
- **Cañón de las Orquídeas** (normal, exterior, nivel 13): 1 cuadra.
- **Cascada Alta** (normal, exterior, nivel 14): 1 cuadra.
- **Poblado de las Lianas** (segura, pueblo, 3 cuadras y 4 edificios).
  - Poblado de las Lianas, cuadra 1: Casa.
  - Poblado de las Lianas, cuadra 2: Panadería, Carpintería.
  - Poblado de las Lianas, cuadra 3: Posada.
- **Ruinas del Templo** (hostil, interior, nivel 17): 1 cuadra.
- **Mirador Este** (normal, exterior, nivel 19): 1 cuadra.
- **Campamento Maderero** (segura, exterior, nivel 20, con cama): 1 cuadra.
- **Gruta Verde** (normal, interior, nivel 22): 1 cuadra.

## UBICACIONES: LA SELVA DEL NORTE
**La Selva del Norte** · selva con grandes irregularidades · tropical húmedo · montaña y mesetas · lagunas y cascadas · niveles 18-30.
- **Fuerte del Norte** (segura, interior, nivel 18, con cama): 1 cuadra.
- **Selva Alta** (normal, exterior, nivel 19): 1 cuadra.
- **Meseta de Niebla** (normal, exterior, nivel 21): 1 cuadra.
- **Laguna de las Garzas** (normal, exterior, nivel 22): 1 cuadra.
- **Aserradero** (normal, exterior, nivel 24): 1 cuadra.
- **Templo Hundido** (hostil, interior, nivel 25): 1 cuadra.
- **Camino del Norte** (normal, exterior, nivel 27): 1 cuadra.
- **Aldea de los Cartógrafos** (segura, pueblo, 3 cuadras y 5 edificios).
  - Aldea de los Cartógrafos, cuadra 1: Tienda.
  - Aldea de los Cartógrafos, cuadra 2: Tienda, Fonda.
  - Aldea de los Cartógrafos, cuadra 3: Posada, Sala.
- **Cima de las Nubes** (hostil, exterior, nivel 30): 1 cuadra.

# LORE_PIRATAS · EL MAR DE LAS MIL VELAS (bloque 3/7)

## DÓNDE VIVE CADA NPC (por ubicación)
**NPC adultos incluidos:** 158 arquetipos (apariencia femenina). **NPC niños incluidos:** 75 (con un solo nombre). **Respawneables incluidos:** 64 plantillas (llevan nombre de facción o grupo + número). **Compañeros:** 32. El lore **puede agregar** más NPC, respawneables y compañeros con el mismo formato.

- **Puerto de las Gaviotas:** adultos NPC-013, NPC-014, NPC-019, NPC-025, NPC-041, NPC-044, NPC-168, NPC-180; niños Eva (NIN-010), Lisandro (NIN-030), Corina (NIN-049), Cosme (NIN-051), Marinela (NIN-059), Bartolo (NIN-065), Abril (NIN-077), Yesica (NIN-078), Sira (NIN-087), Nereo (NIN-090).
- **Muelle de la Corriente:** adultos NPC-015, NPC-017, NPC-046, NPC-059, NPC-188, NPC-205, NPC-208, NPC-211, NPC-225; niños Xenón (NIN-028), Ismael (NIN-068), Isa (NIN-070), Greta (NIN-086).
- **Palafitos de la Gente del Pantano:** adultos NPC-016, NPC-024, NPC-037, NPC-039, NPC-053, NPC-056, NPC-132, NPC-133, NPC-176, NPC-189, NPC-193, NPC-221; niños Mara (NIN-014), Tina (NIN-048).
- **La Ciudad de los Siete Faroles:** adultos NPC-018, NPC-020, NPC-021, NPC-022, NPC-027, NPC-029, NPC-036, NPC-038, NPC-040, NPC-042, NPC-047, NPC-049, NPC-050, NPC-051, NPC-054, NPC-057, NPC-061, NPC-062, NPC-063, NPC-069, NPC-071, NPC-072, NPC-073, NPC-076, NPC-077, NPC-078, NPC-079, NPC-080, NPC-081, NPC-082, NPC-114, NPC-127, NPC-130, NPC-131, NPC-134, NPC-135, NPC-136, NPC-137, NPC-157, NPC-158, NPC-159, NPC-160, NPC-161, NPC-162, NPC-163, NPC-169, NPC-170, NPC-171, NPC-175, NPC-178, NPC-179, NPC-183, NPC-190, NPC-191, NPC-192, NPC-194, NPC-197, NPC-201, NPC-202, NPC-204, NPC-207, NPC-209, NPC-222, NPC-223; niños Hilario (NIN-008), Vera (NIN-009), Dalila (NIN-011), Yerai (NIN-012), Mauro (NIN-013), Cayetano (NIN-017), Pía (NIN-018), Ofelia (NIN-024), Rita (NIN-031), Beto (NIN-040), Candela (NIN-041), Olmo (NIN-042), Urko (NIN-043), Yara (NIN-044), Zaira (NIN-045), Maia (NIN-046), Ubaldo (NIN-047), Sixto (NIN-052), Dora (NIN-053), Luna (NIN-056), Yago (NIN-057), Noa (NIN-058), Vasco (NIN-060), Telmo (NIN-075), Zeno (NIN-082), Olga (NIN-083), Remo (NIN-085), Flor (NIN-088), Perla (NIN-089).
- **Mercado Flotante:** adultos NPC-023, NPC-066, NPC-154, NPC-212; niños —.
- **Aldea de los Cartógrafos:** adultos NPC-026, NPC-043, NPC-120, NPC-121, NPC-122, NPC-125; niños Ximena (NIN-061), Edgar (NIN-064), Rafa (NIN-073), Jacinto (NIN-080).
- **Biblioteca de las Bitácoras:** adultos NPC-031, NPC-048, NPC-058, NPC-119, NPC-172, NPC-173, NPC-216; niños —.
- **Fuerte del Norte:** adultos NPC-035, NPC-074, NPC-195, NPC-213, NPC-214, NPC-224; niños Gaspar (NIN-027).
- **Ensenada de los Contrabandistas:** adultos NPC-052; niños Selene (NIN-026).
- **Mirador de los Tucanes:** adultos NPC-055, NPC-220; niños —.
- **Remanso de las Balsas:** adultos NPC-060; niños —.
- **Bahía de la Tormenta:** adultos NPC-064, NPC-167; niños —.
- **Barco Hundido:** adultos NPC-065; niños —.
- **Mirador Este:** adultos NPC-075; niños Anselmo (NIN-019), Ignacio (NIN-055).
- **Meseta de Niebla:** adultos NPC-105, NPC-111; niños —.
- **Cañón de las Orquídeas:** adultos NPC-109, NPC-186, NPC-217; niños Salvador (NIN-022).
- **Manglar de Entrada:** adultos NPC-110; niños —.
- **Campamento de los Recolectores:** adultos NPC-112; niños Valerio (NIN-063).
- **Vado de las Piedras:** adultos NPC-113; niños Aitor (NIN-021), Quico (NIN-062), Estela (NIN-079).
- **Puente de Lianas:** adultos NPC-116; niños Violeta (NIN-076).
- **Cañón Verde:** adultos NPC-117; niños —.
- **Isla Escondida:** adultos NPC-118, NPC-185, NPC-200; niños Fausto (NIN-033).
- **Cueva de los Juncos:** adultos NPC-123, NPC-124; niños —.
- **Aserradero:** adultos NPC-129; niños Hebe (NIN-015).
- **Claro del Venado:** adultos NPC-152, NPC-206; niños —.
- **Laguna Verde:** adultos NPC-153, NPC-166, NPC-182, NPC-184, NPC-196; niños —.
- **Selva Alta:** adultos NPC-164; niños Jimena (NIN-054).
- **Jardín de las Estatuas:** adultos NPC-165; niños Mariano (NIN-023), Glauco (NIN-072).
- **Poblado de las Lianas:** adultos NPC-174, NPC-177; niños Julieta (NIN-007), Iris (NIN-029).
- **Selva de Sabana:** adultos NPC-181; niños Rómulo (NIN-025).
- **Cascada Brava:** adultos NPC-187; niños —.
- **Faro del Cabo:** adultos NPC-198; niños Orión (NIN-032).
- **Sendero de los Helechos:** adultos NPC-203; niños —.
- **Cascada Alta:** adultos NPC-210; niños —.
- **Botes de la Niebla:** adultos NPC-218; niños —.
- **Bosque Anegado:** adultos NPC-219; niños Eloy (NIN-020), Uma (NIN-050), Romina (NIN-081).
- **Embarcadero del Norte:** adultos —; niños Tano (NIN-016).
- **Gruta Verde:** adultos —; niños Gala (NIN-069).
- **Camino del Norte:** adultos —; niños Dionisio (NIN-071).
- **Selva de Lianas:** adultos —; niños Fiona (NIN-074).

## RESPAWNEABLES (facción o grupo + número)
Cada respawneable lleva el nombre de la facción o grupo del que viene + número de serie. Ejemplos de asignación:
- RSP-001 «Guardia [facción]» → Guardia [Las Mercaderas del Puerto]-001
- RSP-002 «Guardia de puerta [ubicación]» → Guardia de puerta [Las Curanderas de la Marea]-002
- RSP-003 «Patrulla [facción]» → Patrulla [Las Patronas de los Astilleros]-003
- RSP-004 «Soldado [facción]» → Soldado [Las Guardianas del Muelle]-004
- RSP-005 «Explorador [grupo]» → Explorador [La Hermandad del Remanso]-005
- RSP-006 «Cazador [grupo]» → Cazador [Las Mercaderas del Puerto]-006
- RSP-008 «Bandido [grupo]» → Bandido [Las Curanderas de la Marea]-007
- RSP-015 «Cobrador [grupo]» → Cobrador [Las Patronas de los Astilleros]-008
- RSP-016 «Pueblerino de [ubicación]» → Pueblerino de [Las Guardianas del Muelle]-009
- RSP-017 «Ciudadano de [ubicación]» → Ciudadano de [Las Cartógrafas de la Selva]-010
- RSP-018 «Ocupante de [ubicación]» → Ocupante de [Las Mercaderas del Puerto]-011
- RSP-019 «Trabajador de [ubicación]» → Trabajador de [Las Curanderas de la Marea]-012
- RSP-020 «Granjero de [ubicación]» → Granjero de [Las Patronas de los Astilleros]-013
- RSP-021 «Pastor de [ubicación]» → Pastor de [Las Guardianas del Muelle]-014
- RSP-022 «Minero de [ubicación]» → Minero de [Las Cartógrafas de la Selva]-015
- RSP-023 «Pescador de [ubicación]» → Pescador de [Las Mercaderas del Puerto]-016
- RSP-024 «Marinero de [ubicación]» → Marinero de [Las Curanderas de la Marea]-017
- RSP-025 «Estibador de [ubicación]» → Estibador de [Las Patronas de los Astilleros]-018
- RSP-026 «Vendedor ambulante de [ubicación]» → Vendedor ambulante de [Las Guardianas del Muelle]-019
- RSP-027 «Comerciante de caravana [caravana]» → Comerciante de caravana [Las Cartógrafas de la Selva]-020
- RSP-028 «Guardia de caravana [caravana]» → Guardia de caravana [Las Mercaderas del Puerto]-021
- RSP-029 «Peregrino [grupo]» → Peregrino [Las Curanderas de la Marea]-022
- RSP-030 «Viajero [ubicación]» → Viajero [Las Patronas de los Astilleros]-023
- RSP-031 «Mensajero [facción]» → Mensajero [Las Guardianas del Muelle]-024
- RSP-032 «Obrero de [ubicación]» → Obrero de [Las Cartógrafas de la Selva]-025
- RSP-033 «Técnico de [facción]» → Técnico de [Las Mercaderas del Puerto]-026
- RSP-034 «Médico de campo [facción]» → Médico de campo [Las Curanderas de la Marea]-027
- RSP-035 «Enfermero de [facción]» → Enfermero de [Las Patronas de los Astilleros]-028
- RSP-036 «Escriba de [facción]» → Escriba de [Las Guardianas del Muelle]-029
- RSP-037 «Intendente de [facción]» → Intendente de [Las Cartógrafas de la Selva]-030
- RSP-038 «Vigía de [facción]» → Vigía de [Las Mercaderas del Puerto]-031
- RSP-039 «Recluta de [facción]» → Recluta de [Los Grumetes del Faro]-032
- RSP-040 «Veterano de [facción]» → Veterano de [Las Patronas de los Astilleros]-033
- RSP-041 «Oficial de [facción]» → Oficial de [Las Guardianas del Muelle]-034
- RSP-042 «Aprendiz de [oficio]» → Aprendiz de [La Hermandad del Remanso]-035
- RSP-043 «Artesano de [ubicación]» → Artesano de [Las Mercaderas del Puerto]-036
- RSP-044 «Tabernero de [ubicación]» → Tabernero de [Las Curanderas de la Marea]-037
- RSP-045 «Cocinero de [ubicación]» → Cocinero de [Las Patronas de los Astilleros]-038
- RSP-053 «Robot de seguridad de [lugar]» → Robot de seguridad de [Las Guardianas del Muelle]-039
- RSP-054 «Robot servicial de [lugar]» → Robot servicial de [Las Cartógrafas de la Selva]-040
El resto de las plantillas incluidas se instancian igual con la facción o ubicación que corresponda.

## COMPAÑEROS (solo femeninos o niños; el lore puede agregar más)
Se pueden usar desde el segundo uno. Máximo 3 activos (41). Personalidades extendidas: bloque de compañeros (catálogo).
| ID | Nombre (una sola palabra) | Arquetipo | Edad | Dónde se encuentra |
|---|---|---|---|---|
| K-1 | Magdalena | perra leal de guardia (apariencia hembra) | neutro | La Ciudad de los Siete Faroles |
| K-2 | Piedad | cazadora de la región, veterana | adulto | La Ciudad de los Siete Faroles |
| K-3 | Asunción | guardia de caravana, bebedora de buen humor | adulto | La Ciudad de los Siete Faroles |
| K-4 | Gloria | chica de la facción científica, curiosa | adulto | La Ciudad de los Siete Faroles |
| K-5 | Pilar | guerrera de orden, disciplinada | adulto | La Ciudad de los Siete Faroles |
| K-6 | Soledad | exploradora de frontera | adulto | Palafitos de la Gente del Pantano |
| K-7 | Guadalupe | médica ambulante | adulto | La Ciudad de los Siete Faroles |
| K-8 | Consuelo | mecánica de campo, ingeniosa | adulto | La Ciudad de los Siete Faroles |
| K-9 | Purificación | guía de supervivencia, mayor | adulto | Puerto de las Gaviotas |
| K-10 | Esperanza | domadora de criaturas | adulto | Poblado de las Lianas |
| K-11 | Luz | cantante errante | adulto | La Ciudad de los Siete Faroles |
| K-12 | Marina | ex contrabandista, astuta | adulto | La Ciudad de los Siete Faroles |
| K-13 | Dolores | sacerdotisa viajera | adulto | Muelle de la Corriente |
| K-14 | Natividad | cartógrafa valiente | adulto | Puerto de las Gaviotas |
| K-15 | Candelaria | ex guardia de torre | adulto | Aldea de los Cartógrafos |
| K-16 | Brisa | ladrona arrepentida | adulto | La Ciudad de los Siete Faroles |
| K-17 | Socorro | robot de apoyo (apariencia a elección del lore) | neutro | La Ciudad de los Siete Faroles |
| K-18 | Amparo | comerciante viajera, pragmática | adulto | Aldea de los Cartógrafos |
| K-19 | Remedios | campeona de torneos, humilde | adulto | La Ciudad de los Siete Faroles |
| K-20 | Nicolás | niño amigo de la infancia, leal | niño | Casa del Farero |
| K-21 | Plácido | niño explorador, entusiasta | niño | Poblado de las Lianas |
| K-22 | Lola | niño rastreador, callado | niño | La Ciudad de los Siete Faroles |
| K-23 | Pancho | niño inventor, distraído | niño | La Ciudad de los Siete Faroles |
| K-24 | Darío | niño sanador, amable | niño | Palafitos de la Gente del Pantano |
| K-25 | Kiara | niño recadero, veloz | niño | La Ciudad de los Siete Faroles |
| K-26 | Nina | niño líder de grupo, carismático | niño | La Ciudad de los Siete Faroles |
| K-27 | Tamara | niño navegante, soñador | niño | La Ciudad de los Siete Faroles |
| K-28 | Tadeo | niño grumete, obediente | niño | La Ciudad de los Siete Faroles |
| K-29 | Bruno | niña estudiosa, brillante | niño | La Ciudad de los Siete Faroles |
| K-30 | Wendy | niña arquera, concentrada | niño | Puerto de las Gaviotas |
| K-31 | Brenda | niña pastora, protectora | niño | Puerto de las Gaviotas |
| K-32 | Xavi | niña mecánica de botes, ingeniosa | niño | Poblado de las Lianas |

# LORE_PIRATAS · EL MAR DE LAS MIL VELAS (bloque 4/7)

## MISIONES PRINCIPALES (15)
Cada una instancia una misión base de MISIONES BASE. Orden por territorios: T-CIU → T-SUR → T-OCE → T-PAN → T-RIO → T-ESE → T-NOR.
| ID | Nombre | Tipo | Nivel | Dador | Lugar | Recompensa |
|---|---|---|---|---|---|---|
| MP-01 | La bitácora de Gaspar | ESC | 1 | NPC-162 | La Ciudad de los Siete Faroles | 290 XP |
| MP-02 | Un mensaje en una botella | FAM | 3 | Rita | La Ciudad de los Siete Faroles | 570 XP |
| MP-03 | El faro apagado | HCK | 5 | NPC-179 | La Ciudad de los Siete Faroles | 850 XP |
| MP-04 | El mapa del almirante | INV | 7 | NPC-152 | Claro del Venado | 1130 XP |
| MP-05 | El acertijo del templo hundido | PUZ | 9 | Fiona | Selva de Lianas | 1410 XP |
| MP-06 | La perla de la marea | ART | 11 | Orión | Faro del Cabo | 1690 XP |
| MP-07 | Tras la estela de la Estrella Fugaz | INV | 13 | NPC-019 | Puerto de las Gaviotas | 1970 XP |
| MP-08 | El rescate del capitán | JEF | 14 | NPC-053 | Palafitos de la Gente del Pantano | 2110 XP |
| MP-09 | La brújula del tesoro | ART | 14 | NPC-196 | Laguna Verde | 2110 XP |
| MP-10 | Entre mar, río y pantano | BND | 19 | Xenón | Muelle de la Corriente | 2810 XP |
| MP-11 | La isla de la calavera | LMP | 21 | NPC-023 | Mercado Flotante | 3090 XP |
| MP-12 | Rumbo al tesoro | ESC | 22 | NPC-075 | Mirador Este | 3230 XP |
| MP-13 | Tres llaves para el cofre | HCK | 22 | NPC-186 | Cañón de las Orquídeas | 3230 XP |
| MP-14 | Quién gobierna los puertos | BND | 27 | Gaspar | Fuerte del Norte | 3930 XP |
| MP-15 | Después de la tormenta | EXP | 30 | Rafa | Aldea de los Cartógrafos | 4350 XP |

## MISIONES SECUNDARIAS BASE Y DE JEFE (todas incluidas)
Las 45 misiones secundarias base y una misión por jefe de territorio están **incluidas** en este lore.
| ID | Nombre | Tipo | Nivel |
|---|---|---|---|
| MS-01 | La bomba del pueblo | BND | 7 |
| MS-02 | Los de las jaulas | RSC | 6 |
| MS-03 | La torre y los excluidos | BND | 9 |
| MS-04 | Las páginas del guía | MAP | 16 |
| MS-05 | El robot que quería sentir | ENS | 12 |
| MS-06 | La comunidad con reglas propias | NEG | 18 |
| MS-07 | El culto del artefacto | INV | 1 |
| MS-08 | La cura prometida | CUR | 1 |
| MS-09 | Lo que vive en la mina | JEF | 13 |
| MS-10 | El pozo envenenado | INV | 4 |
| MS-11 | La caravana atrapada | ESC | 10 |
| MS-12 | El mercado de lo oculto | CTR | 13 |
| MS-13 | El concurso del pueblo | FIE | 21 |
| MS-14 | El juicio | DET | 1 |
| MS-15 | El fantasma del edificio | PUZ | 4 |
| MS-16 | Una voz sin cuerpo | HCK | 6 |
| MS-17 | La biblioteca que se cae | REC | 10 |
| MS-18 | El jardinero del páramo | RCL | 10 |
| MS-19 | Cacería para el trofeo | CAZ | 22 |
| MS-20 | El mensajero que no llegó | MSJ | 24 |
| MS-21 | Cuentas pendientes | COB | 1 |
| MS-22 | El vecino que no sale | FAM | 4 |
| MS-23 | El taller del inventor | FAB | 6 |
| MS-24 | La torreta rebelde | SAB | 4 |
| MS-25 | El mapa roto | ART | 10 |
| MS-26 | Las ofrendas | PUZ | 16 |
| MS-27 | La antena caída | CON | 18 |
| MS-28 | El rastro del ladrón | DET | 1 |
| MS-29 | La mascota perdida | DOM | 7 |
| MS-30 | El campamento sin agua | TRA | 6 |
| MS-31 | La enfermera sola | MED | 11 |
| MS-32 | Reunión de vecinos | NEG | 10 |
| MS-33 | El archivo cerrado | HCK | 13 |
| MS-34 | Plaga en el granero | AMN | 28 |
| MS-35 | El puente caído | CON | 1 |
| MS-36 | El duelo de cazadores | FIE | 2 |
| MS-37 | El traidor del puesto | DET | 13 |
| MS-38 | El regalo imposible | ART | 4 |
| MS-39 | La banda de la ruta | AMN | 22 |
| MS-40 | El refugio sin llave | REC | 16 |
| MS-41 | Voluntarios para la ronda | VIG | 28 |
| MS-42 | El dormitorio de los ruidos | LMP | 1 |
| MS-43 | Cruzar el desfiladero | ESC | 9 |
| MS-44 | El inventario del almacén | COM | 6 |
| MS-45 | Fuego en el barrio | DEF | 4 |
| MJ-01 | Cuidado con Gran Pulpo Anciano | JEF | 16 |
| MJ-02 | Cuidado con Reina del Fango | JEF | 12 |
| MJ-03 | Cuidado con Coloso del Río | JEF | 20 |
| MJ-04 | Cuidado con Señora de la Colmena | JEF | 17 |
| MJ-05 | Cuidado con Madre Avispa | JEF | 25 |

# LORE_PIRATAS · EL MAR DE LAS MIL VELAS (bloque 5/7)

## MISIONES PROPIAS DE CADA NPC
**Misiones propias de cada NPC (1 a 5 por NPC con misión):** 601 en total. Formato: NPC → «nombre» (tipo, nivel).
- NPC-013 [NPC-013]: «A quién creerle» (BND, n6)
- NPC-014 [NPC-014]: «La muralla de la esperanza» (DEF, n7)
- NPC-015 [NPC-015]: «Antes del amanecer» (MED, n10) · «Secreto de la bondad» (PUZ, n10)
- NPC-016 [NPC-016]: «Material para el cansancio» (RCL, n5)
- NPC-017 [NPC-017]: «Lo que se llevó la palabra» (REC, n12) · «Negocio en el camino» (COM, n11) · «Carga callada» (CTR, n10)
- NPC-018 [NPC-018]: «Lo que se llevó la curiosidad» (REC, n2) · «Negocio en el refugio» (COM, n2) · «Todo lo que se junta» (RCL, n1)
- NPC-019 [NPC-019]: «Pedido especial» (COM, n6) · «Fiesta del granero» (FIE, n7) · «Todo lo que se junta» (RCL, n8) · «Carga hasta el puente» (TRA, n6)
- NPC-020 [NPC-020]: «Manos que sanan» (MED, n2) · «Negocio en el viejo túnel» (COM, n3)
- NPC-021 [NPC-021]: «Negocio en el mercado» (COM, n3) · «Compañía para el miedo» (ESC, n2)
- NPC-022 [NPC-022]: «El invento de la creatividad» (FAB, n2)
- NPC-023 [NPC-023]: «Libros que faltan» (ENS, n24) · «En busca de la reliquia» (REC, n23)
- NPC-024 [NPC-024]: «Rastro de la llave» (REC, n4) · «Antena y cable» (CON, n5)
- NPC-025 [NPC-025]: «Construir juntos» (CON, n7)
- NPC-026 [NPC-026]: «Rastro del cuaderno» (REC, n29) · «Reparación en el mercado» (FAB, n28)
- NPC-027 [NPC-027]: «Todo lo que se junta» (RCL, n1) · «Un buen trato» (COM, n2) · «El trofeo del silencio» (CAZ, n3) · «Rastro de la herramienta» (REC, n1)
- NPC-029 [NPC-029]: «Negocio en el bosque» (COM, n2) · «Volver a casa» (FAM, n2)
- NPC-031 [NPC-031]: «Entrega urgente» (MSJ, n8) · «Fiesta del puente» (FIE, n7) · «En busca de la brújula» (REC, n8)
- NPC-035 [NPC-035]: «Cartas sin dueño» (MSJ, n19)
- NPC-036 [NPC-036]: «Cartas sin dueño» (MSJ, n1) · «El concurso de la esperanza» (FIE, n1) · «Todo lo que se junta» (RCL, n2)
- NPC-037 [NPC-037]: «Sobre ruedas» (TRA, n5) · «Lo que no se dijo a tiempo» (MSJ, n5) · «Mercancía para el cansancio» (COM, n5)
- NPC-038 [NPC-038]: «Aprender con la protección» (ENS, n2) · «Puertas que no abren» (PUZ, n1)
- NPC-039 [NPC-039]: «Fiesta del camino» (FIE, n6) · «Aprender con la paciencia» (ENS, n5)
- NPC-040 [NPC-040]: «El misterio del refugio» (INV, n1) · «Código de la distracción» (HCK, n3) · «Provisión del pozo» (RCL, n2) · «Pruebas del muelle» (DET, n3)
- NPC-041 [NPC-041]: «Pieza única» (ART, n8)
- NPC-042 [NPC-042]: «Una mesa para el cansancio» (NEG, n2) · «La balanza del cansancio» (BND, n3) · «La sombra del cansancio» (DET, n3) · «Mercancía para el cansancio» (COM, n1)
- NPC-043 [NPC-043]: «Mediación» (NEG, n29) · «¿quién fue?» (DET, n28) · «Lo que no se dijo a tiempo» (MSJ, n29) · «Devolver el mapa» (REC, n29)
- NPC-044 [NPC-044]: «El misterio del granero» (INV, n8)
- NPC-046 [NPC-046]: «Qué pasó en el viejo túnel» (INV, n12) · «Letras y cuentas» (ENS, n11) · «Un mensaje para la esperanza» (MSJ, n11) · «Rastro de la herramienta» (REC, n11) · «Un buen trato» (COM, n12)
- NPC-047 [NPC-047]: «Cruzar con cuidado» (ESC, n1) · «Más allá del refugio» (EXP, n3) · «Los bordes del mapa» (MAP, n1)
- NPC-048 [NPC-048]: «Qué pasó en el granero» (INV, n8) · «Letras en la pared» (PUZ, n9) · «Lo que brilla en el mercado» (ART, n9)
- NPC-049 [NPC-049]: «El camino de vuelta» (FAM, n1)
- NPC-050 [NPC-050]: «Entrega urgente» (MSJ, n3) · «El misterio del viejo túnel» (INV, n2) · «Material para la esperanza» (RCL, n1)
- NPC-051 [NPC-051]: «Puesto del orden» (VIG, n3)
- NPC-052 [NPC-052]: «Un favor por otro» (COB, n15) · «Caso sin cerrar» (DET, n15)
- NPC-053 [NPC-053]: «Cartas sin dueño» (MSJ, n4)
- NPC-054 [NPC-054]: «Mercancía para la creatividad» (COM, n3)
- NPC-055 [NPC-055]: «Rastro de la reliquia» (REC, n2) · «Mercancía para el ingenio» (COM, n1) · «Todo lo que se junta» (RCL, n1)
- NPC-056 [NPC-056]: «El misterio del granero» (INV, n5) · «Letras en la pared» (PUZ, n5) · «Pruebas del mercado» (DET, n6) · «Entrega urgente» (MSJ, n5)
- NPC-057 [NPC-057]: «Antes del amanecer» (MED, n1)
- NPC-058 [NPC-058]: «Pedido especial» (COM, n8) · «Material para la generosidad» (RCL, n9)
- NPC-059 [NPC-059]: «Un buen trato» (COM, n10)
- NPC-060 [NPC-060]: «Tras la presa de la alegría» (CAZ, n13)
- NPC-061 [NPC-061]: «Escolta hasta el pueblo» (ESC, n1)
- NPC-062 [NPC-062]: «Ronda por el granero» (VIG, n2)
- NPC-063 [NPC-063]: «Lo que no se declara» (CTR, n1) · «Entrar por la ventana» (INF, n3)
- NPC-064 [NPC-064]: «Escolta hasta el refugio» (ESC, n11)
- NPC-065 [NPC-065]: «Entrega urgente» (MSJ, n13) · «Pistas de la soledad» (INV, n14) · «Escolta hasta el puesto» (ESC, n13)
- NPC-066 [NPC-066]: «Caso sin cerrar» (DET, n22)
- NPC-069 [NPC-069]: «Qué pasó en el taller» (INV, n3) · «Reiniciar el viejo túnel» (HCK, n2)
- NPC-071 [NPC-071]: «Un buen trato» (COM, n1) · «Rastro del cuaderno» (REC, n2)
- NPC-072 [NPC-072]: «En busca del cuaderno» (REC, n2) · «Algo que funcione» (FAB, n1) · «Escolta hasta el camino» (ESC, n2) · «Noche de guardia» (DEF, n1)
- NPC-073 [NPC-073]: «Puesto de la esperanza» (VIG, n1) · «Rutas nuevas» (EXP, n3) · «Cruzar con cuidado» (ESC, n2)
- NPC-074 [NPC-074]: «Palabras en el puente» (NEG, n20) · «Atrapado por los intrusos» (RSC, n18) · «Defender lo propio» (DEF, n20) · «Turno de noche» (VIG, n19)
- NPC-075 [NPC-075]: «Remedio para el cansancio» (MED, n19) · «Contra el veneno» (CUR, n19) · «Cuando no alcanza el cansancio» (AMN, n19)
- NPC-076 [NPC-076]: «La balanza de la frialdad» (BND, n1) · «Noche de guardia» (DEF, n3) · «Ronda por el puente» (VIG, n3) · «Qué pasó en el viejo túnel» (INV, n3) · «El camino seguro» (ESC, n3)
- NPC-077 [NPC-077]: «Puesto del silencio» (VIG, n1) · «Cuando no alcanza el silencio» (AMN, n2) · «La muralla del silencio» (DEF, n3)
- NPC-078 [NPC-078]: «Puesto de la esperanza» (VIG, n1) · «Letras y cuentas» (ENS, n1) · «Cruzar con cuidado» (ESC, n2) · «Defender lo propio» (DEF, n2)
- NPC-079 [NPC-079]: «Construir juntos» (CON, n2) · «Voz del mercado» (HCK, n1)
- NPC-080 [NPC-080]: «Tinta y senderos» (MAP, n2) · «Mapa del taller» (EXP, n3) · «El misterio del refugio» (INV, n1) · «Compañía para la valentía» (ESC, n2) · «Limpiar el refugio» (AMN, n3)
- NPC-081 [NPC-081]: «Última guardia» (JEF, n3) · «Cacería en el bosque» (CAZ, n3) · «Paz para el pueblo» (AMN, n3) · «La muralla del silencio» (DEF, n1)
- NPC-082 [NPC-082]: «Devolver el mapa» (REC, n2) · «Ruido en la noche» (INV, n1) · «Cuando no alcanza el silencio» (AMN, n1) · «Ojos abiertos» (VIG, n3) · «Defender lo propio» (DEF, n2)
- NPC-105 [NPC-105]: «Pruebas del granero» (DET, n21) · «En busca de la herramienta» (REC, n22) · «Sin ser vistos» (INF, n21) · «Limpiar el pozo» (AMN, n23)
- NPC-109 [NPC-109]: «Carga hasta el camino» (TRA, n15) · «Escolta hasta el taller» (ESC, n14) · «Negocio de noche» (CTR, n13) · «Guardia contra los saqueadores» (AMN, n15)
- NPC-110 [NPC-110]: «Escolta hasta el camino» (ESC, n9) · «Defender lo propio» (DEF, n7) · «Rastro de la brújula» (REC, n7) · «Paz para el pueblo» (AMN, n9) · «Más allá del muelle» (EXP, n8)
- NPC-111 [NPC-111]: «Mercancía para los nervios» (COM, n21) · «Lo que no se dijo a tiempo» (MSJ, n23) · «El misterio del viejo túnel» (INV, n23) · «Mapa del viejo túnel» (EXP, n22) · «Devolver el cuaderno» (REC, n23)
- NPC-112 [NPC-112]: «El camino seguro» (ESC, n9) · «La salida del bosque» (RSC, n10) · «Cartas sin dueño» (MSJ, n10)
- NPC-113 [NPC-113]: «El misterio del camino» (INV, n19) · «Atrapado por los saqueadores» (RSC, n20) · «Guardia contra los intrusos» (AMN, n20)
- NPC-114 [NPC-114]: «Volver a casa» (FAM, n1) · «La salida del muelle» (RSC, n1)
- NPC-116 [NPC-116]: «Lo que no se dijo a tiempo» (MSJ, n15) · «No dejar a nadie atrás» (RSC, n16) · «Rutas nuevas» (EXP, n15) · «Cuando no alcanza la valentía» (AMN, n15)
- NPC-117 [NPC-117]: «Cruzar con cuidado» (ESC, n5) · «Puertas que no abren» (PUZ, n5) · «Paz para el bosque» (AMN, n7)
- NPC-118 [NPC-118]: «El acertijo del puesto» (PUZ, n15) · «Ruido en la noche» (INV, n15)
- NPC-119 [NPC-119]: «Sin noticias» (FAM, n7) · «Letras en la pared» (PUZ, n7)
- NPC-120 [NPC-120]: «Código del silencio» (HCK, n29) · «Letras en la pared» (PUZ, n29)
- NPC-121 [NPC-121]: «Pieza única» (ART, n28)
- NPC-122 [NPC-122]: «Mercancía para la ambición» (COM, n30) · «Artefacto de la ambición» (ART, n30)
- NPC-123 [NPC-123]: «Letras y cuentas» (ENS, n12) · «Dibujar el pozo» (MAP, n11) · «Puertas que no abren» (PUZ, n11) · «Ruido en la noche» (INV, n12) · «Tesoro con condición» (ART, n11)
- NPC-124 [NPC-124]: «Material para la curiosidad» (RCL, n13) · «Antes del amanecer» (MED, n11)
- NPC-125 [NPC-125]: «Cacería en el granero» (CAZ, n28)
- NPC-127 [NPC-127]: «La presa del puesto» (CAZ, n2)
- NPC-129 [NPC-129]: «Provisión del muelle» (RCL, n24) · «Lo que brilla en el taller» (ART, n26) · «Carga hasta el viejo túnel» (TRA, n24)
- NPC-130 [NPC-130]: «El invento del ingenio» (FAB, n2) · «Una mano para el puesto» (CON, n2) · «Defender lo propio» (DEF, n1) · «Carga hasta el granero» (TRA, n3)
- NPC-131 [NPC-131]: «Limpiar el mercado» (AMN, n3) · «Confianza en el puente» (DOM, n3) · «Mercancía para el silencio» (COM, n2) · «Faltan recursos» (RCL, n3)
- NPC-132 [NPC-132]: «Una mano para el mercado» (CON, n4)
- NPC-133 [NPC-133]: «Entrega pesada» (TRA, n6) · «Contra el veneno» (CUR, n4) · «La muralla del cansancio» (DEF, n6)
- NPC-134 [NPC-134]: «Material para la superstición» (RCL, n3) · «Lo que vive en el muelle» (JEF, n3) · «Noche de guardia» (DEF, n3)
- NPC-135 [NPC-135]: «Voz del camino» (HCK, n1) · «Lo que se llevó la autoridad» (REC, n3) · «Paz para el puente» (AMN, n1) · «La muralla de la autoridad» (DEF, n2) · «Provisión del granero» (RCL, n2)
- NPC-136 [NPC-136]: «La muralla de la esperanza» (DEF, n2)
- NPC-137 [NPC-137]: «Día de feria» (FIE, n2)
- NPC-152 [NPC-152]: «Manos a la obra» (FAB, n3)
- NPC-153 [NPC-153]: «Puertas que no abren» (PUZ, n12)
- NPC-154 [NPC-154]: «Negocio en el viejo túnel» (COM, n24)
- NPC-157 [NPC-157]: «Día de feria» (FIE, n3) · «Lo que no se dijo a tiempo» (MSJ, n3)
- NPC-158 [NPC-158]: «Dos caminos en el muelle» (BND, n3)
- NPC-159 [NPC-159]: «Puesto del cansancio» (VIG, n1) · «Defender lo propio» (DEF, n1) · «Paz para el refugio» (AMN, n3)
- NPC-160 [NPC-160]: «Tras la presa de la lealtad» (CAZ, n1) · «Escolta hasta el refugio» (ESC, n2) · «Puesto de la lealtad» (VIG, n1)

# LORE_PIRATAS · EL MAR DE LAS MIL VELAS (bloque 6/7)

## MISIONES PROPIAS DE CADA NPC
- NPC-161 [NPC-161]: «Fiebre en el muelle» (CUR, n1) · «Manos que sanan» (MED, n2) · «Qué pasó en el camino» (INV, n1)
- NPC-162 [NPC-162]: «Cruce discreto» (CTR, n3) · «Negocio en el puente» (COM, n3) · «Sobre ruedas» (TRA, n2)
- NPC-163 [NPC-163]: «Día de feria» (FIE, n1) · «Libros que faltan» (ENS, n2) · «Todo lo que se junta» (RCL, n2)
- NPC-164 [NPC-164]: «Provisión del puente» (RCL, n20) · «Mercancía para la alegría» (COM, n19) · «El concurso de la alegría» (FIE, n20) · «Lo que se llevó la alegría» (REC, n19)
- NPC-165 [NPC-165]: «Provisión del muelle» (RCL, n14)
- NPC-166 [NPC-166]: «Contra el veneno» (CUR, n12) · «Letras en la pared» (PUZ, n11) · «Artefacto de la esperanza» (ART, n10)
- NPC-167 [NPC-167]: «Ruido en la noche» (INV, n11) · «Entrega urgente» (MSJ, n12) · «En busca del cuaderno» (REC, n12) · «Todo lo que se junta» (RCL, n12)
- NPC-168 [NPC-168]: «Lo que no se dijo a tiempo» (MSJ, n8) · «Premio inesperado» (FIE, n7) · «Material para la esperanza» (RCL, n7) · «En busca de la carta» (REC, n8)
- NPC-169 [NPC-169]: «Mercancía para la esperanza» (COM, n2) · «Caso sin cerrar» (DET, n2)
- NPC-170 [NPC-170]: «Ronda por el granero» (VIG, n2)
- NPC-171 [NPC-171]: «Qué pasó en el bosque» (INV, n2)
- NPC-172 [NPC-172]: «Fiesta del muelle» (FIE, n7) · «Provisión del taller» (RCL, n7) · «¿quién fue?» (DET, n9) · «Devolver la reliquia» (REC, n9)
- NPC-173 [NPC-173]: «Faltan materiales» (RCL, n9) · «La presa del muelle» (CAZ, n9)
- NPC-174 [NPC-174]: «Buscando a alguien» (FAM, n18) · «Lo que no se dijo a tiempo» (MSJ, n18) · «Premio inesperado» (FIE, n18)
- NPC-175 [NPC-175]: «Manos a la obra» (FAB, n2) · «Libros que faltan» (ENS, n2)
- NPC-176 [NPC-176]: «La balanza de la esperanza» (BND, n5) · «Palabras en el muelle» (NEG, n4) · «El concurso de la esperanza» (FIE, n5)
- NPC-177 [NPC-177]: «Guardia contra los intrusos» (AMN, n18)
- NPC-178 [NPC-178]: «Una mano para el taller» (CON, n2) · «Defender lo propio» (DEF, n2)
- NPC-179 [NPC-179]: «Algo que funcione» (FAB, n3) · «Pieza única» (ART, n2) · «En busca de la llave» (REC, n1) · «Provisión del granero» (RCL, n3)
- NPC-180 [NPC-180]: «Ruido en la noche» (INV, n7) · «Premio inesperado» (FIE, n7)
- NPC-181 [NPC-181]: «Sin noticias» (FAM, n12) · «Cartas sin dueño» (MSJ, n14) · «Cuando no alcanza el recuerdo» (AMN, n13)
- NPC-182 [NPC-182]: «Puesto de la esperanza» (VIG, n11) · «Una mano para el mercado» (CON, n11) · «Devolver la medalla» (REC, n11) · «Mapa del muelle» (EXP, n10) · «Cruzar con cuidado» (ESC, n12)
- NPC-183 [NPC-183]: «Aprender con la paciencia» (ENS, n1) · «Premio inesperado» (FIE, n2)
- NPC-184 [NPC-184]: «Puertas que no abren» (PUZ, n10) · «Remedio para la bondad» (MED, n11) · «Ruido en la noche» (INV, n12) · «Artefacto de la bondad» (ART, n10) · «Lo que se llevó la bondad» (REC, n10)
- NPC-185 [NPC-185]: «Confianza en el camino» (DOM, n14)
- NPC-186 [NPC-186]: «Rutas nuevas» (EXP, n15) · «Artefacto de la obsesión» (ART, n14)
- NPC-187 [NPC-187]: «Cuando no alcanza el silencio» (AMN, n12)
- NPC-188 [NPC-188]: «Un buen trato» (COM, n12) · «Reparación en el puesto» (FAB, n10)
- NPC-189 [NPC-189]: «Todo lo que se junta» (RCL, n5) · «Reparación en el refugio» (FAB, n5)
- NPC-190 [NPC-190]: «Piezas para la esperanza» (CON, n3) · «Algo que funcione» (FAB, n3) · «Faltan provisiones» (RCL, n3)
- NPC-191 [NPC-191]: «Resistir en el pueblo» (DEF, n1) · «Construir juntos» (CON, n1) · «Palabras en el taller» (NEG, n2)
- NPC-192 [NPC-192]: «Entrega pesada» (TRA, n3) · «Respirar de nuevo» (CUR, n3) · «Fiesta del mercado» (FIE, n2) · «Pruebas del bosque» (DET, n1)
- NPC-193 [NPC-193]: «Ruido en la noche» (INV, n5)
- NPC-194 [NPC-194]: «Libros que faltan» (ENS, n3)
- NPC-195 [NPC-195]: «Lección en el bosque» (ENS, n18) · «Buscando a alguien» (FAM, n18) · «Provisión del granero» (RCL, n19)
- NPC-196 [NPC-196]: «Carga hasta el refugio» (TRA, n11)
- NPC-197 [NPC-197]: «Cuando no alcanza el silencio» (AMN, n3) · «Lección en el pueblo» (ENS, n1) · «Día de feria» (FIE, n2) · «Mercancía para el silencio» (COM, n3)
- NPC-198 [NPC-198]: «Paz para el camino» (AMN, n10)
- NPC-200 [NPC-200]: «Mirada de la protección» (DOM, n14) · «Todo lo que se junta» (RCL, n15) · «Qué pasó en el pozo» (INV, n13) · «Lo que brilla en el camino» (ART, n13)
- NPC-201 [NPC-201]: «Mediación» (NEG, n1) · «La balanza de la ambición» (BND, n3) · «Defender lo propio» (DEF, n2) · «La sombra de la ambición» (DET, n1)
- NPC-202 [NPC-202]: «Palabras en el pozo» (NEG, n1) · «Entrega urgente» (MSJ, n1)
- NPC-203 [NPC-203]: «Compañía para el orden» (ESC, n6) · «Entrega pesada» (TRA, n5)
- NPC-204 [NPC-204]: «Resistir en el granero» (DEF, n1)
- NPC-205 [NPC-205]: «Caso sin cerrar» (DET, n10) · «Pagar con tiempo» (COB, n11)
- NPC-206 [NPC-206]: «Provisión del puente» (RCL, n3) · «El camino seguro» (ESC, n4) · «Limpiar el muelle» (AMN, n4)
- NPC-207 [NPC-207]: «Limpiar el puente» (AMN, n3) · «Pruebas del puesto» (DET, n3)
- NPC-208 [NPC-208]: «La sombra de la ironía» (DET, n11)
- NPC-209 [NPC-209]: «Libros que faltan» (ENS, n3) · «Devolver la llave» (REC, n2)
- NPC-210 [NPC-210]: «Camino largo» (TRA, n14) · «Mirada de la paciencia» (DOM, n15) · «Devolver la reliquia» (REC, n16) · «Paz para el viejo túnel» (AMN, n14)
- NPC-211 [NPC-211]: «Antes del amanecer» (MED, n11) · «Una dosis a tiempo» (CUR, n10) · «Pedido especial» (COM, n10)
- NPC-212 [NPC-212]: «Fiesta del pueblo» (FIE, n24) · «Una mesa para la esperanza» (NEG, n22) · «Negocio en el puesto» (COM, n22) · «Entrega pesada» (TRA, n22)
- NPC-213 [NPC-213]: «Rutas nuevas» (EXP, n20) · «Una mano para el viejo túnel» (CON, n18) · «Resistir en el puesto» (DEF, n19) · «Puesto de la paciencia» (VIG, n18) · «Guardia contra las alimañas» (AMN, n19)
- NPC-214 [NPC-214]: «Cruzar con cuidado» (ESC, n18)
- NPC-216 [NPC-216]: «Secreto de la esperanza» (PUZ, n9) · «El misterio del pozo» (INV, n7)
- NPC-217 [NPC-217]: «Fiebre en el muelle» (CUR, n13) · «Secreto de la protección» (PUZ, n15)
- NPC-218 [NPC-218]: «Un buen trato» (COM, n9) · «Material para la alegría» (RCL, n8) · «Premio inesperado» (FIE, n9) · «Lo que no se dijo a tiempo» (MSJ, n9) · «Cruzar con cuidado» (ESC, n9)
- NPC-219 [NPC-219]: «Cuando no alcanza el silencio» (AMN, n9) · «Confianza en el muelle» (DOM, n9) · «El trofeo del silencio» (CAZ, n10)
- NPC-220 [NPC-220]: «El camino seguro» (ESC, n2) · «Más allá del pueblo» (EXP, n2) · «Guardia contra los intrusos» (AMN, n3) · «Lo que no se dijo a tiempo» (MSJ, n3)
- NPC-221 [NPC-221]: «El invento de la paciencia» (FAB, n6) · «Un buen trato» (COM, n6) · «Provisión del viejo túnel» (RCL, n6)
- NPC-222 [NPC-222]: «Letras y cuentas» (ENS, n3) · «Dibujar el muelle» (MAP, n3) · «Compañía para la esperanza» (ESC, n1) · «Provisión del taller» (RCL, n1)
- NPC-223 [NPC-223]: «La sombra de la astucia» (DET, n3) · «El cofre del puesto» (INF, n1) · «Lo que no se declara» (CTR, n1) · «Sobre ruedas» (TRA, n2)
- NPC-224 [NPC-224]: «Voz del bosque» (HCK, n19) · «El invento de la timidez» (FAB, n18) · «Lo que se llevó la timidez» (REC, n20) · «Día de feria» (FIE, n20) · «¿quién fue?» (DET, n18)
- NPC-225 [NPC-225]: «Remedio para la sabiduría» (MED, n11) · «Provisión del puesto» (RCL, n12) · «Contra el veneno» (CUR, n10) · «Cartas sin dueño» (MSJ, n11) · «Fiesta del mercado» (FIE, n11)
- Julieta [NIN-007]: «Antes del amanecer» (MED, n18) · «Material para la valentía» (RCL, n18) · «Cartas sin dueño» (MSJ, n17) · «Día de feria» (FIE, n17) · «Caso sin cerrar» (DET, n17)
- Hilario [NIN-008]: «Cartas sin dueño» (MSJ, n2) · «Camino largo» (TRA, n1) · «Pedido especial» (COM, n3) · «Provisión del pozo» (RCL, n1) · «Premio inesperado» (FIE, n3)
- Vera [NIN-009]: «Pistas de la esperanza» (INV, n1) · «Lo que no se dijo a tiempo» (MSJ, n3) · «Fiesta del refugio» (FIE, n2) · «Devolver el cuaderno» (REC, n3)
- Eva [NIN-010]: «Rastro del mapa» (REC, n8) · «Pruebas del puesto» (DET, n6)
- Dalila [NIN-011]: «Rastro del cuaderno» (REC, n3) · «En silencio» (INF, n2) · «Mediación» (NEG, n1)
- Yerai [NIN-012]: «Buscando a alguien» (FAM, n3) · «Devolver la reliquia» (REC, n3) · «¿quién fue?» (DET, n1)
- Mauro [NIN-013]: «Faltan provisiones» (RCL, n3) · «Día de feria» (FIE, n3) · «Pruebas del granero» (DET, n3)
- Mara [NIN-014]: «Confianza en el muelle» (DOM, n4) · «Cuando no alcanza el silencio» (AMN, n6) · «Negocio en el taller» (COM, n5) · «Noche de guardia» (DEF, n6)
- Hebe [NIN-015]: «Faltan recursos» (RCL, n25) · «Resistir en el pozo» (DEF, n25) · «Entrega pesada» (TRA, n24)
- Tano [NIN-016]: «Compañía para la alegría» (ESC, n17)
- Cayetano [NIN-017]: «Mapa del camino» (EXP, n1) · «Cartas sin dueño» (MSJ, n1) · «Faltan recursos» (RCL, n1)
- Pía [NIN-018]: «Más allá del viejo túnel» (EXP, n2)
- Anselmo [NIN-019]: «Puesto del silencio» (VIG, n21) · «Cartas sin dueño» (MSJ, n20)
- Eloy [NIN-020]: «Hoja en blanco» (MAP, n10)
- Aitor [NIN-021]: «La sombra de la paciencia» (DET, n19) · «Tras la presa de la paciencia» (CAZ, n20)
- Salvador [NIN-022]: «Resistir en el refugio» (DEF, n15) · «Tras la presa del orgullo» (CAZ, n15) · «Compañía para el orgullo» (ESC, n14) · «Un mensaje para el orgullo» (MSJ, n15)
- Mariano [NIN-023]: «Los bordes del mapa» (MAP, n13) · «Rutas nuevas» (EXP, n13) · «Paz para el muelle» (AMN, n14) · «Cartas sin dueño» (MSJ, n12)
- Ofelia [NIN-024]: «La muralla de la lealtad» (DEF, n2) · «Puesto de la lealtad» (VIG, n3) · «El camino seguro» (ESC, n2)
- Rómulo [NIN-025]: «Mediación» (NEG, n13) · «Compañía para la valentía» (ESC, n12)
- Selene [NIN-026]: «Cartas sin dueño» (MSJ, n15) · «Carga hasta el taller» (TRA, n16) · «Cuando no alcanza los nervios» (AMN, n15)
- Gaspar [NIN-027]: «Remedio para la esperanza» (MED, n19) · «Una dosis a tiempo» (CUR, n20) · «Mediación» (NEG, n19) · «Cartas sin dueño» (MSJ, n18)
- Xenón [NIN-028]: «Reparación en el pueblo» (FAB, n11) · «Tesoro con condición» (ART, n12) · «Construir juntos» (CON, n11) · «La sombra de la distracción» (DET, n12)
- Iris [NIN-029]: «Lección en el camino» (ENS, n17) · «Rastro de la carta» (REC, n17)
- Lisandro [NIN-030]: «Ruido en la noche» (INV, n6) · «El concurso de la esperanza» (FIE, n8) · «Caso sin cerrar» (DET, n7) · «En busca del cuaderno» (REC, n7)
- Rita [NIN-031]: «Día de feria» (FIE, n1)
- Orión [NIN-032]: «Confianza en el bosque» (DOM, n8) · «La presa del pozo» (CAZ, n8)

# LORE_PIRATAS · EL MAR DE LAS MIL VELAS (bloque 7/7)

## MISIONES PROPIAS DE CADA NPC
- Fausto [NIN-033]: «Material para la paciencia» (RCL, n15) · «Criatura herida» (DOM, n13) · «Lo que brilla en el taller» (ART, n13) · «Secreto de la paciencia» (PUZ, n14)
- Beto [NIN-040]: «Cuando no alcanza la lealtad» (AMN, n1) · «Sin noticias» (FAM, n3)
- Candela [NIN-041]: «Premio inesperado» (FIE, n2)
- Olmo [NIN-042]: «El concurso de la esperanza» (FIE, n1)
- Urko [NIN-043]: «Confianza en el puesto» (DOM, n1) · «El camino de vuelta» (FAM, n1)
- Yara [NIN-044]: «Una mano para el taller» (CON, n1) · «Reparación en el bosque» (FAB, n1) · «Cruzar con cuidado» (ESC, n3) · «Lo que se llevó la esperanza» (REC, n2)
- Zaira [NIN-045]: «Cruzar con cuidado» (ESC, n2) · «Mapa del refugio» (EXP, n2) · «Un mensaje para el orgullo» (MSJ, n1) · «Rastro del mapa» (REC, n2) · «Entrega pesada» (TRA, n2)
- Maia [NIN-046]: «Sombra sobre el pozo» (JEF, n3) · «La balanza de la valentía» (BND, n3)
- Ubaldo [NIN-047]: «Tinta y senderos» (MAP, n1) · «Rutas nuevas» (EXP, n3) · «Sobre ruedas» (TRA, n3)
- Tina [NIN-048]: «La balanza de la bravuconería» (BND, n5) · «En silencio» (INF, n6)
- Corina [NIN-049]: «Carga callada» (CTR, n6) · «Sin ser vistos» (INF, n8)
- Uma [NIN-050]: «El trofeo del silencio» (CAZ, n10) · «Faltan recursos» (RCL, n10) · «Cartas sin dueño» (MSJ, n9)
- Cosme [NIN-051]: «Camino largo» (TRA, n6)
- Sixto [NIN-052]: «Rastro de la carta» (REC, n1) · «Entrar por la ventana» (INF, n2) · «Camino largo» (TRA, n3)
- Dora [NIN-053]: «Manos a la obra» (FAB, n2) · «Aprender con la curiosidad» (ENS, n1)
- Jimena [NIN-054]: «Sobre ruedas» (TRA, n21) · «Cartas sin dueño» (MSJ, n20) · «En busca de la medalla» (REC, n19)
- Ignacio [NIN-055]: «Escolta hasta el pueblo» (ESC, n20)
- Luna [NIN-056]: «Respirar de nuevo» (CUR, n1) · «Remedio para la esperanza» (MED, n3) · «Compañía para la esperanza» (ESC, n3)
- Yago [NIN-057]: «Pistas de la timidez» (INV, n2)
- Noa [NIN-058]: «Día de feria» (FIE, n3) · «Todo lo que se junta» (RCL, n1) · «Palabras en el bosque» (NEG, n1) · «Lo que se llevó la alegría» (REC, n2)
- Marinela [NIN-059]: «Cartas sin dueño» (MSJ, n6) · «Ruido en la noche» (INV, n7)
- Vasco [NIN-060]: «Entrega pesada» (TRA, n2)
- Ximena [NIN-061]: «En busca de la brújula» (REC, n28) · «Noche de guardia» (DEF, n30) · «Negocio en el refugio» (COM, n30)
- Quico [NIN-062]: «Sin noticias» (FAM, n20) · «La salida del granero» (RSC, n19) · «Limpiar el refugio» (AMN, n21)
- Valerio [NIN-063]: «No dejar a nadie atrás» (RSC, n11) · «Paz para el viejo túnel» (AMN, n9) · «Lo que vive en el viejo túnel» (JEF, n10)
- Edgar [NIN-064]: «Buscando a alguien» (FAM, n30)
- Bartolo [NIN-065]: «El camino seguro» (ESC, n7) · «Buscando a alguien» (FAM, n7) · «Premio inesperado» (FIE, n8)
- Ismael [NIN-068]: «Dibujar el camino» (MAP, n11)
- Gala [NIN-069]: «Lección en el bosque» (ENS, n24) · «La máquina que no responde» (HCK, n24) · «Pieza única» (ART, n24)
- Isa [NIN-070]: «Mercancía para la creatividad» (COM, n10) · «Algo que funcione» (FAB, n12) · «La sombra de la creatividad» (DET, n10)
- Dionisio [NIN-071]: «Compañía para la valentía» (ESC, n29) · «Defender lo propio» (DEF, n27) · «Más allá del puesto» (EXP, n27) · «Devolver la herramienta» (REC, n27)
- Glauco [NIN-072]: «Puesto de la esperanza» (VIG, n12)
- Rafa [NIN-073]: «Todo lo que se junta» (RCL, n30)
- Fiona [NIN-074]: «El trofeo de la esperanza» (CAZ, n2) · «Más allá del bosque» (EXP, n4) · «Devolver la brújula» (REC, n3) · «Cartas sin dueño» (MSJ, n3)
- Telmo [NIN-075]: «Faltan recursos» (RCL, n1) · «Paz para el pozo» (AMN, n1) · «Entrega pesada» (TRA, n3) · «Un buen trato» (COM, n3) · «Noche de guardia» (DEF, n2)
- Violeta [NIN-076]: «Cacería en el puesto» (CAZ, n14)
- Abril [NIN-077]: «Algo que funcione» (FAB, n6) · «Lo que se llevó el ingenio» (REC, n6) · «Pruebas del pozo» (DET, n6)
- Yesica [NIN-078]: «Lección en el taller» (ENS, n7)
- Estela [NIN-079]: «La salida del muelle» (RSC, n19) · «Cura en el muelle» (MED, n21)
- Jacinto [NIN-080]: «Premio inesperado» (FIE, n29)
- Romina [NIN-081]: «Cartas sin dueño» (MSJ, n9)
- Zeno [NIN-082]: «Material para la protección» (RCL, n3) · «La muralla de la protección» (DEF, n3) · «Un buen trato» (COM, n2) · «Caso sin cerrar» (DET, n1) · «En busca del mapa» (REC, n1)
- Olga [NIN-083]: «Premio inesperado» (FIE, n1)
- Remo [NIN-085]: «Libros que faltan» (ENS, n2)
- Greta [NIN-086]: «Entrega pesada» (TRA, n11) · «Material para el silencio» (RCL, n10) · «Cruzar con cuidado» (ESC, n11) · «Lo que se llevó el silencio» (REC, n10)
- Sira [NIN-087]: «Puesto de la lealtad» (VIG, n8)
- Flor [NIN-088]: «En silencio» (INF, n2)
- Perla [NIN-089]: «A quién creerle» (BND, n1) · «Resistir en el pozo» (DEF, n2) · «Caso sin cerrar» (DET, n2) · «Palabras en el muelle» (NEG, n1) · «Premio inesperado» (FIE, n1)
- Nereo [NIN-090]: «Todo lo que se junta» (RCL, n6) · «El camino seguro» (ESC, n8) · «En busca de la reliquia» (REC, n7)

## MISIONES DESCARTADAS POR EL LORE
Se descartan: todo lo subterráneo, de ciencia o radio, torres, órdenes armadas y refugios; esclavistas, cultos, saqueadores adultos y mercenarios; alcohol, apuestas, casino y préstamos; los temas de criaturas T2-T14 y las fases 2-14 de animales. Las misiones que dependían de esos NPC no aparecen.

## OBJETOS DEL LORE
- **Armas (no letales para personas):** Remo de práctica, Sable de madera, Sable de abordaje (embotado), Arpón de pesca (punta roma), Sable del Capitán; hondas, redes y garfios de práctica.
- **Comida y bebida:** pescado asado, galletas de barco, frutas de la selva, guisos, caldos, agua de lluvia, té. **Sin alcohol ni químicos.**
- **Medicina:** vendas, ungüentos, tinturas, compresas, férulas. **Ropa:** ropa de pirata, chalecos salvavidas, capas impermeables; armaduras ligeras (E1-E4), Armadura del almirante (E5).
- **Objetos generales:** mapas, brújulas, catalejos, cuerdas, redes, velas, bitácoras, botellas con mensajes, anclas pequeñas. **Moneda:** doblones. Barcos y botes: nodos de muelle y tramos de agua.

## CONFIG_LORE FINAL
```
LORE = El Mar de las Mil Velas
MONEDA = doblones
NECESIDADES = on    CONTAMINACION = off    MODULO_EXTERNO = off    NIVEL_MAX = 30

TERRITORIOS = [El Océano de las Mil Velas, El Río Media Luna, El Pantano de los Islotes, La Selva del Sur, La Ciudad de los Siete Faroles, La Selva del Este, La Selva del Norte]
UBICACIONES = 61 (con 45 cuadras y 93 edificios)

REPARTO = {
  edades_permitidas: [niño, adulto], apariencia_adultos: femenina, apariencia_niños: mixta,
  excepciones: [], grupos_separados: [[adultos, niños]], sin_muerte: true }

CRIATURAS = { temas_activos: [T1 animales],
  fases_activas: {T1 animales: [1]},
  modificadores_apagados: [Infernal, Demoníaca, Celestial, Zombi, Robótica, Alienígena], fases_ausentes: todas las demás }

NPC = { incluidos: 158 adultos + 75 niños, agregados: [] }
COMPANEROS = 32 (nombre de una sola palabra)
RESPAWNEABLES = 64 plantillas con facción o grupo
MISIONES = { principales: 15, secundarias_base: 45, de_jefe: 5, propias_de_npc: 601 }
JEFES = [Gran Pulpo Anciano, Reina del Fango, Coloso del Río, Señora de la Colmena, Madre Avispa]
ARRANQUE = { protagonista: Gaspar (niño), ubicación_inicial: Casa del Farero, misión_inicial: MP-01 }
```
