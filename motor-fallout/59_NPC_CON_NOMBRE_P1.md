# 59 · CLASIFICACIÓN DE NPC CON NOMBRE (parte 1/4)

**NPC con nombre** (por arquetipo, sin nombres originales): `NPC-nnn` + palabras clave. El **lore** les pone nombre, apariencia (50) y lugar; el arquetipo es neutro en edad adulta y en apariencia. **Cada NPC tiene de 1 a 5 misiones** (asignadas al azar con semilla fija, tal cual); el nombre de la misión sale de su personalidad y del tipo de misión (34 tipos, ver bloque de misiones base). Un NPC que cae bien o interesa muestra **relación** (09); se le puede pedir que **te siga o te acompañe** (temporal). **El lore puede agregar más NPC** y descartar los que no encajan: lo que el lore no menciona, no existe. Todo NPC adulto lleva `edad: adulto`.

## NPC adultos (arquetipos)
| ID | Arquetipo | Personalidad | Lugar típico | Misiones (n: nombre y tipo) |
|---|---|---|---|---|
| NPC-001 | supervisor/a de instalación | autoritario/a, controlador/a, secreto | refugio o instalación | 1: «Una mesa para la autoridad» (NEG) |
| NPC-002 | jefe/a médico/a de instalación | culto/a, amable, reservado/a | refugio o instalación | 1: «Pistas de la esperanza» (INV) |
| NPC-003 | guardia de seguridad de instalación | estricto/a, cansado/a, leal | refugio o instalación | 5: «Ronda por el mercado» (VIG) · «Noche de guardia» (DEF) · «Guardia contra la plaga» (AMN) · «El misterio del puesto» (INV) · «Lo que no se dijo a tiempo» (MSJ) |
| NPC-004 | maestro/a de instalación | paciente, firme, protector/a | refugio o instalación | 4: «Letras y cuentas» (ENS) · «Volver a casa» (FAM) · «Devolver el cuaderno» (REC) · «Lo que no se dijo a tiempo» (MSJ) |
| NPC-005 | cocinero/a comunal | generoso/a, mandón/a, chismoso/a | refugio o instalación | 4: «Negocio en el bosque» (COM) · «Provisión del mercado» (RCL) · «Fiesta del granero» (FIE) · «En busca del mapa» (REC) |
| NPC-006 | técnico/a de mantenimiento | obsesivo/a, ingenioso/a, impaciente | refugio o instalación | 2: «Manos a la obra» (FAB) · «Antena y cable» (CON) |
| NPC-007 | científico/a de instalación | curioso/a, distraído/a, brillante | refugio o instalación | 2: «Letras en la pared» (PUZ) · «Código de la curiosidad» (HCK) |
| NPC-008 | guía de la instalación | amable, ordenado/a, nervioso/a | refugio o instalación | 1: «El camino seguro» (ESC) |
| NPC-009 | cuidador/a de archivos | metódico/a, callado/a, curioso/a | refugio o instalación | 4: «Qué pasó en el puesto» (INV) · «Código del silencio» (HCK) · «Rastro del mapa» (REC) · «Aprender con el silencio» (ENS) |
| NPC-010 | radio operador/a de instalación | alegre, hablador/a, solitario/a | refugio o instalación | 1: «Lo que no se dijo a tiempo» (MSJ) |
| NPC-011 | intendente de instalación | ahorrativo/a, estricto/a | refugio o instalación | 2: «Lo que se llevó el orden» (REC) · «Un buen trato» (COM) |
| NPC-012 | vecino/a mayor de instalación | nostálgico/a, terco/a, protector/a | refugio o instalación | 3: «Rastro de la reliquia» (REC) · «Sin noticias» (FAM) · «El misterio del bosque» (INV) |
| NPC-013 | comisario/a de asentamiento | honesto/a, rígido/a, orgulloso/a | asentamiento | 1: «A quién creerle» (BND) |
| NPC-014 | alcalde/sa de asentamiento | pragmático/a, firme, diplomático/a | asentamiento | 1: «La muralla de la esperanza» (DEF) |
| NPC-015 | sacerdote/sa de comunidad | sereno/a, persuasivo/a, bondadoso/a | asentamiento | 2: «Antes del amanecer» (MED) · «Secreto de la bondad» (PUZ) |
| NPC-016 | médico/a de asentamiento | cansado/a, ético/a, sarcástico/a | asentamiento | 1: «Material para el cansancio» (RCL) |
| NPC-017 | comerciante de armas | charlatán/a, codicioso/a, leal | comercio | 3: «Lo que se llevó la palabra» (REC) · «Negocio en el camino» (COM) · «Carga callada» (CTR) |
| NPC-018 | comerciante de recursos generales | curioso/a, ahorrativo/a, regateador/a | comercio | 3: «Lo que se llevó la curiosidad» (REC) · «Negocio en el refugio» (COM) · «Todo lo que se junta» (RCL) |
| NPC-019 | comerciante de comida | generoso/a, mandón/a, supersticioso/a | comercio | 4: «Pedido especial» (COM) · «Fiesta del granero» (FIE) · «Todo lo que se junta» (RCL) · «Carga hasta el puente» (TRA) |
| NPC-020 | comerciante de medicinas | cauto/a, ético/a, reservado/a | comercio | 2: «Manos que sanan» (MED) · «Negocio en el viejo túnel» (COM) |
| NPC-021 | comerciante de animales de carga | bonachón/a, miedoso/a, hablador/a | comercio | 2: «Negocio en el mercado» (COM) · «Compañía para el miedo» (ESC) |
| NPC-022 | comerciante de ropa y telas | creativo/a, vanidoso/a, simpático/a | comercio | 1: «El invento de la creatividad» (FAB) |
| NPC-023 | comerciante de libros y notas | erudito/a, tranquilo/a, curioso/a | comercio | 2: «Libros que faltan» (ENS) · «En busca de la reliquia» (REC) |
| NPC-024 | mecánico/a | obsesivo/a, perfeccionista, impaciente | asentamiento | 2: «Rastro de la llave» (REC) · «Antena y cable» (CON) |
| NPC-025 | herrero/a | fuerte, orgulloso/a, paciente | asentamiento | 1: «Construir juntos» (CON) |
| NPC-026 | armero/a | meticuloso/a, desconfiado/a, hábil | asentamiento | 2: «Rastro del cuaderno» (REC) · «Reparación en el mercado» (FAB) |
| NPC-027 | curtidor/a | callado/a, trabajador/a, práctico/a | asentamiento | 4: «Todo lo que se junta» (RCL) · «Un buen trato» (COM) · «El trofeo del silencio» (CAZ) · «Rastro de la herramienta» (REC) |
| NPC-028 | tabernero/a | cálido/a, discreto/a, chismoso/a | asentamiento | 3: «Día de feria» (FIE) · «Pistas de la esperanza» (INV) · «Mercancía para la esperanza» (COM) |
| NPC-029 | posadero/a | hospitalario/a, curioso/a, cansado/a | asentamiento | 2: «Negocio en el bosque» (COM) · «Volver a casa» (FAM) |
| NPC-030 | cantinero/a de local | sarcástico/a, cordial, atento/a | asentamiento | 4: «Negocio de noche» (CTR) · «El misterio del camino» (INV) · «La sombra de la ironía» (DET) · «El concurso de la ironía» (FIE) |
| NPC-031 | animador/a de espectáculo | carismático/a, trabajador/a, risueño/a | asentamiento | 3: «Entrega urgente» (MSJ) · «Fiesta del puente» (FIE) · «En busca de la brújula» (REC) |
| NPC-032 | apostador/a profesional | astuto/a, ambicioso/a, supersticioso/a | asentamiento | 4: «Pruebas del bosque» (DET) · «Pagar con tiempo» (COB) · «Premio inesperado» (FIE) · «Un mensaje para la astucia» (MSJ) |
| NPC-033 | prestamista | frío/a, calculador/a, educado/a | asentamiento | 5: «Lo que se debe» (COB) · «Carga callada» (CTR) · «Mediación» (NEG) · «Día de feria» (FIE) · «Material para la frialdad» (RCL) |
| NPC-034 | cobrador/a de deudas | insistente, tenso/a, cumplidor/a | asentamiento | 3: «Pagar con tiempo» (COB) · «Una mesa para la esperanza» (NEG) · «La sombra de la esperanza» (DET) |
| NPC-035 | mensajero/a | nervioso/a, veloz, chismoso/a | asentamiento | 1: «Cartas sin dueño» (MSJ) |
| NPC-036 | pregonero/a | fuerte, divertido/a, dramático/a | asentamiento | 3: «Cartas sin dueño» (MSJ) · «El concurso de la esperanza» (FIE) · «Todo lo que se junta» (RCL) |
| NPC-037 | cartero/a del pueblo | puntual, amable, cansado/a | asentamiento | 3: «Sobre ruedas» (TRA) · «Lo que no se dijo a tiempo» (MSJ) · «Mercancía para el cansancio» (COM) |
| NPC-038 | bibliotecario/a | erudito/a, sereno/a, protector/a | asentamiento | 2: «Aprender con la protección» (ENS) · «Puertas que no abren» (PUZ) |
| NPC-039 | maestro/a de pueblo | paciente, firme, soñador/a | asentamiento | 2: «Fiesta del camino» (FIE) · «Aprender con la paciencia» (ENS) |
| NPC-040 | científico/a de asentamiento | distraído/a, brillante, curioso/a | asentamiento | 4: «El misterio del refugio» (INV) · «Código de la distracción» (HCK) · «Provisión del pozo» (RCL) · «Pruebas del muelle» (DET) |
| NPC-041 | inventor/a | excéntrico/a, optimista, distraído/a | asentamiento | 1: «Pieza única» (ART) |
| NPC-042 | juez/a improvisado/a | justo/a, severo/a, cansado/a | asentamiento | 4: «Una mesa para el cansancio» (NEG) · «La balanza del cansancio» (BND) · «La sombra del cansancio» (DET) · «Mercancía para el cansancio» (COM) |
| NPC-043 | abogado/a del pueblo | elocuente, escéptico/a, ocupado/a | asentamiento | 4: «Mediación» (NEG) · «¿quién fue?» (DET) · «Lo que no se dijo a tiempo» (MSJ) · «Devolver el mapa» (REC) |
| NPC-044 | periodista local | curioso/a, insistente, valiente | asentamiento | 1: «El misterio del granero» (INV) |
| NPC-045 | locutor/a de radio | carismático/a, nocturno/a, solitario/a | ciencia o radio | 1: «Un mensaje para la soledad» (MSJ) |
| NPC-046 | escritor/a del páramo | soñador/a, introvertido/a, crítico/a | asentamiento | 5: «Qué pasó en el viejo túnel» (INV) · «Letras y cuentas» (ENS) · «Un mensaje para la esperanza» (MSJ) · «Rastro de la herramienta» (REC) · «Un buen trato» (COM) |
| NPC-047 | cartógrafo/a | meticuloso/a, aventurero/a, curioso/a | asentamiento | 3: «Cruzar con cuidado» (ESC) · «Más allá del refugio» (EXP) · «Los bordes del mapa» (MAP) |
| NPC-048 | adivino/a o vidente | misterioso/a, teatral, amable | lugar especial | 3: «Qué pasó en el granero» (INV) · «Letras en la pared» (PUZ) · «Lo que brilla en el mercado» (ART) |
| NPC-049 | borracho/a del pueblo | simpático/a, llorón/a, desordenado/a | asentamiento | 1: «El camino de vuelta» (FAM) |
| NPC-050 | mendigo/a sabio/a | humilde, observador/a, bromista | asentamiento | 3: «Entrega urgente» (MSJ) · «El misterio del viejo túnel» (INV) · «Material para la esperanza» (RCL) |
| NPC-051 | guardia de puerta | estricto/a, aburrido/a, leal | asentamiento | 1: «Puesto del orden» (VIG) |
| NPC-052 | cazador/a de recompensas | callado/a, preciso/a, desconfiado/a | camino o ruina | 2: «Un favor por otro» (COB) · «Caso sin cerrar» (DET) |
| NPC-053 | escribano/a | metódico/a, tímido/a, perfeccionista | asentamiento | 1: «Cartas sin dueño» (MSJ) |
| NPC-054 | artesano/a | creativo/a, paciente, orgulloso/a | asentamiento | 1: «Mercancía para la creatividad» (COM) |
| NPC-055 | recolector/a de chatarra | ingenioso/a, ahorrativo/a, solitario/a | camino o ruina | 3: «Rastro de la reliquia» (REC) · «Mercancía para el ingenio» (COM) · «Todo lo que se junta» (RCL) |
| NPC-056 | sepulturero/a | callado/a, filósofo/a, tranquilo/a | asentamiento | 4: «El misterio del granero» (INV) · «Letras en la pared» (PUZ) · «Pruebas del mercado» (DET) · «Entrega urgente» (MSJ) |
| NPC-057 | partera o enfermero/a comunal | bondadoso/a, firme, incansable | asentamiento | 1: «Antes del amanecer» (MED) |
| NPC-058 | panadero/a | madrugador/a, generoso/a, mandón/a | asentamiento | 2: «Pedido especial» (COM) · «Material para la generosidad» (RCL) |
| NPC-059 | carnicero/a | directo/a, trabajador/a, práctico/a | asentamiento | 1: «Un buen trato» (COM) |
| NPC-060 | pescador/a | alegre, supersticioso/a, valiente | puerto o ribera | 1: «Tras la presa de la alegría» (CAZ) |
