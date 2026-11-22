# 47 · CUADRAS Y UBICACIONES (escala del mundo)

## JERARQUÍA (tal cual)
**Territorio › Ubicación › Cuadra › Edificio o sector.**
- **Territorio:** región grande con una variante de bioma propia (51). Ej.: «el sur pantanoso», «las montañas del norte».
- **Ubicación:** un lugar con nombre que se visita como un todo: ciudad, pueblo, campamento, instalación, muelle, granja. Una ubicación puede ser **segura, normal u hostil** (07).
- **Cuadra:** *todo lo que se ve alrededor y es accesible a pie sin desplazarse de verdad.* Es una manzana, una plaza, un tramo de calle con sus frentes, un claro con sus cabañas, un muelle con sus puestos. Una ubicación grande tiene **muchas cuadras**; un campamento pequeño, una o dos.
- **Edificio o sector:** lo que se abre desde una cuadra con un botón (casa, kiosco, tienda, taller, sótano, torre, bote). Es un interior con sus habitaciones, contenedores y personajes.

## QUÉ ES UNA CUADRA (definición operativa, tal cual)
Una cuadra incluye todos los puntos de interés que están **a la vista y a pocos pasos**: lo que tenés enfrente, a los costados y atrás. Ejemplo: parado frente a una heladería y un estanco, con dos kioscos a los lados, otro estanco detrás y una casa al fondo, **todo eso es una misma cuadra**: se puede entrar a cualquiera con un solo botón y sin viajar. Lo que está en otro lado (la plaza de enfrente, un supermercado, otra manzana) es **otra cuadra**: hay que desplazarse hasta ahí.
Reglas:
- Un lugar grande por sí solo (plaza, supermercado, estación, mercado, fábrica) **es una cuadra propia**.
- Una cuadra tiene **de 2 a 10 puntos de interés** (edificios entrables, puestos, puntos para registrar) y de **2 a 4 cuadras vecinas** (calles, pasajes, esquinas).
- Las cuadras tienen nombre propio (lo genera el lore, bloque 99) y no lo cambian.

## FICHA DE CUADRA (tal cual)
`Q-nnn | nombre | ubicación | tipo (calle, plaza, mercado, muelle, claro, campo, ruina…) | puntos de interés[] | vecinas[] | NPC presentes[] | enemigos[] | contenedores exteriores[] | pasos estrechos[] | estado`
Los puntos de interés se generan según el lore y la clase de ubicación; cada uno es un **edificio/sector** con su propia ficha (ver 48).

## CÓMO SE MUEVE UNO (botones)
| Movimiento | Botón | Tiempo | Riesgo |
|---|---|---|---|
| Entrar a un edificio de la cuadra | `Entrar a [edificio]` | 1-3 min | ninguno |
| Pasar a una cuadra vecina | `Ir a [cuadra vecina]` (con flecha de dirección) | 3-8 min | solo en ubicaciones hostiles: 5% de encuentro |
| Marcar una cuadra cercana | **Mapa de muñeca**: tocar la cuadra y `Ir` | 3-8 min | **ninguno, el mapa de muñeca no te deja vulnerable** |
| Ir a otra ubicación conectada | `Ir a [ubicación]` | 20-60 min | encuentro en ruta 10-30% (28) |
| Viaje rápido a un lugar ya descubierto | **Mapa grande** → tocar el lugar | según distancia | abrir el mapa te deja vulnerable: 8/18/35% según zona, **+20% si viajás** (39) |
| Salir de un edificio | `Salir` (puerta) o por ventana/agujero (49) | 1-3 min | atasco solo en pasos estrechos |
Al llegar por viaje rápido, el jugador cae en la **cuadra de entrada** del lugar (o la última visitada).

## MAPAS
- **Mapa de muñeca (Brazalete):** muestra la cuadra actual y las vecinas conocidas (en interior: el plano del edificio). No viaja a otras ubicaciones, no tiene viaje rápido, no genera vulnerabilidad. Marcar una cuadra cercana equivale a pulsar su botón.
- **Mapa grande (papel):** muestra territorios y ubicaciones descubiertas; permite viaje rápido; **vulnerable** (39).
- Una cuadra se marca **descubierta** al pasar por ella o verla desde una vecina; los interiores se descubren al entrar.

## ESCENA DE UNA CUADRA (se genera o se recupera al llegar)
Orden fijo: 1) tipo de cuadra y clima; 2) puntos de interés visibles (2-10); 3) personas y criaturas presentes (según hora y agenda); 4) contenedores exteriores (buzones, tachos, cajones de carga, vehículos, tumbas); 5) pasos estrechos (vallas rotas, huecos, desagües); 6) cuadras vecinas con dirección; 7) sucesos posibles (72).
Todo punto registrado, puerta abierta y cuerpo caído se conserva (02).

## TAMAÑOS RECOMENDADOS (tal cual)
| Ubicación | Cuadras | Edificios por cuadra |
|---|---|---|
| Ciudad grande | 20-40 en barrios de 3-5 cuadras | 3-8 |
| Pueblo | 4-10 | 2-5 |
| Aldea / campamento | 1-3 | 2-4 |
| Instalación (refugio, base, depósito) | 1 cuadra de acceso + sectores interiores | — |
| Camino / claro / ruina abierta | 1-4 | 0-3 |
Los barrios son agrupaciones de cuadras con el mismo carácter (comercial, residencial, portuario, mercado).

## CUADRAS Y PROBABILIDADES (tal cual)
- Cuadra de ubicación **segura**: 3% de encuentro por hora; **normal**: 10%; **hostil**: población fija persistente (28).
- Los enemigos persisten en su cuadra: no desaparecen hasta morir (37). Los grupos de **especies distintas** que comparten cuadra se atacan entre sí.
- Una cuadra despejada en ubicación hostil se repuebla pasadas 48 h (07).
- Los **NPC caminan** entre cuadras según su agenda (40, 61): de noche en la casa, de día en su puesto.

## RELACIÓN CON EL RESTO DEL MOTOR
Cada vez que 03/04/05/07/28 hablan de «ubicación», se lee **cuadra actual** para búsquedas, encuentros y contenedores. `explor` (04) se lleva **por cuadra**. El hogar es una ubicación con 1-2 cuadras y 2 edificios (casa y patio).
