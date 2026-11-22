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
