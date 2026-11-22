# 40 · CLASIFICACIÓN DE NPC

## REGLAS (tal cual)
- Cada NPC tiene: `ID | nombre (lore) | arquetipo | personalidad (3-5 palabras) | agenda | relación | inventario | quest?`. Los nombres propios los pone el lore (42); este cuadro solo define **arquetipos**.
- Los arquetipos se basan en los tipos de habitantes de los mundos abiertos clásicos (asentamientos, caminos, ruinas, puestos militares); no se usan nombres de personajes originales.
- Los NPC pueden **caminar** de un lugar a otro según su agenda (trabajo → comida → sueño → paseo). Si no está, registrar su última posición.
- **NPC genéricos:** personas sin nombre propio: `Pueblerino de [lugar]`, `Ocupante de [lugar]`, `Ciudadano de [lugar]`, `Guardia de [lugar]`, `Vendedor ambulante de [lugar]`. Spawnean en esa ubicación, no cambian de lugar, pueden dar charla, rumores y una compra. Si el jugador los ayuda mucho, pueden recibir nombre.
- Todo NPC es adulto. Cada comerciante tiene personalidad propia aunque comparta tipo.
- Misiones: si el NPC tiene necesidad, genera misión (45). Si el conflicto es entre humanos, hay elección de bando; si es contra criaturas, no.

## COMERCIANTES (cada uno con su personalidad)
| Arquetipo | Vende / compra | Personalidades posibles |
|---|---|---|
| Comerciante de armas | armas, munición, mejoras | charlatán codicioso · veterano callado · obsesivo con la precisión |
| Comerciante de recursos generales | chatarra, componentes, herramientas | ahorradora curiosa · acaparador desconfiado · coleccionista alegre |
| Comerciante de animales de carga | transporte, cargas, comida | bonachón miedoso · bocón optimista · caravanero cansado |
| Comerciante de comida y bebida | comida, agua, alcohol | generosa mandona · gruñón con buen corazón · alegre supersticiosa |
| Médico / curandero | medicina, vendajes, tratamiento de adicción | cansada y ética · idealista joven · escéptico sarcástico |
| Mecánico / armero | reparación, mejora, planos | perfeccionista impaciente · inventor excéntrico · quejoso eficiente |
| Buhonero ambulante | un poco de todo, rumores | nervioso chismoso · misterioso sonriente · cínico simpático |
| Tabernero / posadero | cama, comida, rumores | cálido discreto · curioso entrometido · hastiado leal |
| Comprador de objetos de valor | reliquias, joyas, documentos | calculador cortés · nostálgico coleccionista |
| Cambista / prestamista | cuñas, deudas, avales | frío puntual · amable peligroso |

## NPC DE SERVICIO Y ORDEN
| Arquetipo | Función | Personalidad típica |
|---|---|---|
| Líder de asentamiento | decide acceso y alianzas | pragmática firme · carismática agotada · autoritaria justa |
| Capitán / guardia | vigila, cobra peajes | honesto rígido · cínico cansado · joven orgulloso |
| Centinela / vigía | alerta, detecta | callado atento · nervioso preciso |
| Cazador / rastreador | misiones de caza, rumores | callado desconfiado · alegre fanfarrón |
| Científico / técnico | terminales, planos, muestras | distraída brillante · obsesivo secreto |
| Mensajero | reparte noticias | nervioso veloz chismoso |
| Granjero / ganadero | comida, animales | cansada humor seco · terco generoso |
| Pescadora / recolector | recursos | alegre supersticiosa · silencioso paciente |
| Obrero / fundidor | trabajo, rumores | resignado trabajador · orgulloso del oficio |
| Capataz | organiza trabajos | autoritario justo · estricto agotado |
| Cocinero | comida, rumores | generoso mandón · gruñón talentoso |
| Maestro / consejero | enseñanza, pistas | paciente tozudo · irónico sabio |
| Sacerdote / predicador | rumores, sermones | sereno persuasivo · fanático amable |

## NPC DE CAMINO Y MUNDO
| Arquetipo | Comportamiento | Personalidad típica |
|---|---|---|
| Viajero / peregrino | camina entre asentamientos; puede pedir escolta | educado asustado · valiente agotado |
| Vagabundo | pide, roba poco, cuenta historias | simpático borracho · desconfiado hambriento |
| Caminante solitario | rumores, eventos | misterioso cálido · cínico solitario |
| Caravana | transporte con guardias | bonachón y guardias profesionales |
| Superviviente atrapado | misión de rescate | agradecido educado · terco orgulloso |
| Ex saqueador arrepentido | misiones de reparación | culposo servicial |
| Borracho perdido | misiones de búsqueda | llorón simpático |
| Anciano / anciana | memoria del lugar, pistas | cascarrabias protector · nostálgica terca |
| Amigo de infancia | relación personal | curiosa ingenua · bravucón leal · responsable tensa |

## NPC HOSTILES O AMBIGUOS (humanos)
| Arquetipo | Comportamiento |
|---|---|
| Esclavista / cobrador | captura, intimida, cobra deudas; hostil; liderazgo cruel calculador |
| Ladrón / carterista | roba y huye; hostil o negociable |
| Saqueador | grupo agresivo con código propio; puede aliarse si se elige su bando |
| Bandido de camino | emboscada por peaje |
| Mercenario | pelea por cuñas; negociable |
| Soldado de facción | patrulla, disciplina |
| Francotirador | oculto, distancia |
| Cultista | fanático, no huye |
| Capataz de facción hostil | jefe local con escolta |
| Infiltrado | se hace pasar por civil |

## COMPORTAMIENTO GENERAL DE NPC (tal cual)
- Saludan según relación (09), reaccionan a delitos con testigos (33), venden según su stock.
- Pueden ser atacados por criaturas y defenderse con armas del lore.
- Los NPC de misión **no mueren** salvo evento escrito en la misión; si caen, quedan Incapacitados y se recuperan.
- Los comerciantes tienen caja limitada y reposición de stock cada 72 h.

## NPC DEL SALAR (resumen; detalle de misiones en 44-45 y de compañeros en 41)
Ciudad Horno: líder, comerciantes de armas / recursos, médica, mecánico, cocinera, inventor, líder vecinal, amigos de infancia. Puesto del Cantil: capitán y cazador. Granja Quebracho: granjera. Mercado del Silo: capataz y mensajero. Barrio Ceniza: líder de saqueadores y ex saqueador. Hipermercado: borracho perdido. Metro: viajero atrapado. Laguna: pescadora. Casas del Eco: anciana. Campamento Tasador: mentor cautivo y capataz esclavista. Torre: capataz de la Concesión.
