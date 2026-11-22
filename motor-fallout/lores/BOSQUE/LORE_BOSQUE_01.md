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
