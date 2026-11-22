# 42 · MUNDO ÚNICO «EL SALAR» Y PROTAGONISTA (lore cargado)

Este bloque reemplaza al ejemplo del 14: es el lore real de la campaña. Todo lo (genérico) del motor se resuelve con lo que figura acá.

## EL MUNDO
**El Salar** fue un mar interior que se evaporó dejando una planicie de sal blanca, cañadas secas y ruinas de ciudades que dependían del agua. Hace 140 años "El Cierre" apagó las bombas y los acueductos: quien controlaba el agua controlaba todo. Los sobrevivientes se agruparon alrededor de hornos, pozos y silos. Una compañía, **La Concesión**, construyó un **Purificador** en lo alto de su Torre y después se encerró con él; desde entonces el agua limpia es un recuerdo. El **Faro Seco** (una casa-faro sin mar) es el hogar del protagonista, a la orilla de la Barranca.
**Tono:** supervivencia con humor seco, calidez entre vecinos, amenaza constante pero no desesperanza. Cielo despejado, polvo, sal en los labios.

## FACCIONES (genérico → resuelto)
- **Los Hornos** (Ciudad Horno): fundidores y comerciantes. Pragmáticos, justos con quien cumple.
- **La Guardia del Cantil** (Puesto del Cantil): milicia que cuida los caminos. Honestos y rígidos.
- **Hermandad del Faro**: técnicos que conservan máquinas antiguas. Neutrales y curiosos.
- **Los Tasadores**: esclavistas y cobradores de deudas. Hostiles. Capataz: Rufino Hierro.
- **La Concesión**: la compañía que retiene el Purificador. Hostil. Capataz: Elías Sal.
- **Saqueadores del Barrio Ceniza**: bandas sin jefe único, con código propio. Hostiles o aliados según elección (S-07).

## ESTILO DE NOMBRES (genérico)
Nombre de pila rioplatense/italo-español + apellido de **mineral, roca o terreno** (Basalto, Yesares, Cantera, Quebracho, Esquisto, Cuarzo, Pirita, Arcilla, Lutita, Sedimento, Greda, Hollín, Arenal, Salinas, Mármol, Ónix, Granito). Apodos cortos. Lugares: oficio, objeto o accidente del terreno (Faro Seco, Pozo Viejo, Cantera Chica, Ruta de Sal, Casas del Eco).
Ejemplos válidos: Dolores Cantera, Ezequiel Yeso, Renata Pizarra. No usar nombres fuera de este estilo.

## CONFIG_LORE (completado) (tal cual el formato del 34)
```
TEMAS_ACTIVOS = [T1 animales, T10 artificial]
FASES_ACTIVAS = [1, 3, 4, 5, 7, 13, 14]
ESPECIES_APAGADAS = [H-45, H-46, H-47, H-48, X-14]        # sin T5 de herbívoros ni colosal mecánico
CATEGORIAS_ACTIVAS = {armas: [W-01..W-12, W-20..W-31, W-60..W-62], municion: [A-01..A-05, A-13],
                      consumibles: [CM, BB, MD, AM], quimicos: on, alcohol: on}
MODIFICADORES_APAGADOS = [Infernal, Demoníaca, Celestial, Elemental]
NECESIDADES = on                 # hambre, sed, fatiga
CONTAMINACION = off              # sin radiación; el agua sucia solo enferma
MODULO_EXTERNO = off
NIVEL_MAX = 30
```
**Moneda:** las **cuñas** (barras de sal prensada con sello de horno).
**Humanos:** fase 13 y 14; los de fases 4-7 son comunidades nómadas de caninos y bovinos humanizados que comercian en la Ruta de Sal.

## NOMBRES DE OBJETOS DEL LORE (genérico → resuelto; efectos fijos en 29-32)
| Arquetipo | Nombre en el Salar |
|---|---|
| MD-01 vendaje | Venda · reforzada: Venda de lienzo grueso |
| MD-02 estimulante curativo | Inyector verde |
| QU-xx estimulante de reflejos | Tónico de brío |
| CM-03 comida enlatada | Lata de guiso · CM-04 seca: tasajo |
| BB-01 agua limpia | Agua de pozo hervida · BB-03 sucia: agua turbia |
| W-05 machete / T2 | Machete de Horno · W-08 martillo / T3: Maza de fragua · W-05 / T4: Espada de fundición · T5: Hoja de la Concesión |
| W-21 revólver | Revólver del Cantil · W-25 rifle: Rifle de caza del Salar |
| A-01..A-03 munición | Cartucho chico / mediano / grande |
| T-01 ganzúa | Ganzúa · T-03 kit: Kit de remiendo |
| G-13 dispositivo de muñeca | Brazalete del Faro (mapa de muñeca) |
| K-06 mapa de papel | Mapa del Salar |

## EL PROTAGONISTA: **NICO CARDAL, «CHISPA»**
- **Identidad (tal cual en lo mecánico, genérico en lo físico):** el autor define apariencia, edad y cuerpo con su módulo (`[APARIENCIA_EXTRA]` en 17). Adulto. Categoría fase 13, humano.
- **Stats fijos:** FUE 6 · PER 5 · RES 6 · CAR 5 · INT 4 · AGI 5 · SUE 4 (suma 35).
- **Personalidad:** carismático y de buen humor, dice lo que piensa con una sonrisa, improvisa soluciones con lo que tiene en las manos y no deja a nadie atrás. Es testarudo con las causas justas, algo imprudente con las peleas chicas, y tiene un oído especial para las radios viejas (de ahí el apodo "Chispa").
- **Historia:** criado en el Faro Seco por **Teodoro Greda**, mentor y casi familia, que enseñó a leer rastros, arreglar equipos y desconfiar de los que prometen agua. Hace una semana Teodoro salió a buscar la fuente de una señal de radio y no volvió.
- **Motivación:** encontrar al mentor, restaurar el agua y que Ciudad Horno y el Cantil dejen de pelearse por ella.
- **Hogar:** El Faro Seco (L-001): dormitorio (cama, sofá, té) y cocina con banco de trabajo. Ubicación segura, puede ser atacada de noche (39), salida por ventana con atasco.
- **Tono al hablar:** cálido, bromista, respetuoso con los mayores, directo con los matones.

## AMIGOS DEL HOGAR (no reclutables, dan misiones y charla)
Ver 40 y 41: Evaristo Basalto, Pía Sondeo, Matías Rebote y Aurora Yesares.

## REGLAS DE LORE (tal cual)
No hay magia, extraterrestres ni radiación. Las máquinas son restos de La Concesión. Las criaturas son animales agrandados y mutados por el desequilibrio del agua. Los humanos de fases 4-7 son comunidades antiguas y respetadas. Sin menores de edad en ninguna escena.
