# 49 · PASOS ESTRECHOS: VENTANAS, AGUJEROS, CONDUCTOS Y ATASCO

## QUÉ SON (tal cual)
Accesos que no son una puerta: **ventana, agujero en pared o suelo, conducto/ducto, tubería, reja rota, hueco entre escombros, claraboya, techo, desagüe**. Sirven para entrar o salir de un edificio, pasar por una cuadra bloqueada, escapar de enemigos o esquivar una cerradura. Están disponibles en casi todo edificio y se muestran como botones: `Entrar por la ventana`, `Pasar por el agujero`, `Agacharse y pasar`, `Trepar por…`, `Salir por la ventana`.

## ACCIONES DEL JUGADOR
| Botón | Cuándo aparece | Efecto |
|---|---|---|
| Examinar acceso | siempre | revela tamaño, estado y si hay vidrio, filo o trampa |
| Agacharse y pasar | acceso bajo | tirada de atasco |
| Trepar / subirse | acceso alto (ventana, techo, muro) | AGI; falla = cae (daño 2-6) o no sube |
| Pasar por el agujero | hueco o conducto | tirada de atasco |
| Romper el vidrio / ensanchar | ventana cerrada | ruido 3; riesgo de cortes (−3 PV) pero reduce el atasco en −10 puntos |
| Empujar con ayuda | hay compañero o NPC | −15 puntos de atasco |
| Dejar la mochila afuera | acceso muy estrecho | −10 puntos, pero queda afuera |

## ATASCO (tal cual)
Cada vez que se cruza un paso estrecho:
1. **Tirá el porcentaje de atasco:** un número **aleatorio entre 40% y 60%** (1d21 + 39).
2. Tirá 1d100. Si es **menor o igual** al porcentaje, **quedás atascado**. Si no, **pasás limpio**.
3. Hay pasos que nunca atascan (puertas, escaleras, escalas, cornisas anchas): no tiran.
Ajustes al porcentaje (se aplican **antes** de tirar, siempre dentro de 40-60%): equipo pesado +5 · carga > 75% +5 · compañero ayudando −5 · cuerpo pequeño (talla T1-T2) −5 · vidrio roto −5 (pero con riesgo de corte).

## ESTAR ATASCADO
Mientras estás atascado:
- No podés moverte ni usar el mapa grande; solo **Forcejear**, **Pedir ayuda**, **Defender** y vendas.
- **Liberarse (cada 10 min):** tirada `40 + 4 × mayor(FUE, AGI)` %; con ayuda +20. Pasada **1 hora**, siempre salís.
- **Vulnerabilidad máxima (+25 en 37):** si un enemigo te ataca, **perdés las 3 acciones del primer turno** y no podés escapar hasta liberarte.
- **Ataque mientras estás atascado:** cada 10 min hay **12% (zona normal), 25% (hostil), 3% (segura)** de que una criatura o grupo cercano te encuentre. Si el grupo ya está en la cuadra o en el interior donde entrás, la probabilidad sube a **60%**.
- **Robo por estructura:** si pasa 1 hora o te rescatan tarde, 30% de que te roben 5-15% de las monedas o un recurso (no equipo, no objetos de misión).
- **Rescate:** un compañero o NPC aliado presente te libera en 5 min.

## DESPUÉS DE LIBERARTE
Quedás en el lado que intentabas, con estado `Cansado` 30 min y −2 PV por rasguños. El acceso queda **ensanchado** (−10 al porcentaje la próxima vez) si te atascaste.

## PASOS ESTRECHOS Y ENEMIGOS (tal cual)
- Los enemigos **no** se atascan en pasos estrechos que ya conocen.
- Cruzar un paso estrecho con enemigos **detrás** da +10 al porcentaje (apuro).
- Huir por un paso estrecho: tirada de atasco, y si pasás limpio los enemigos de talla T3 o mayor **no pueden seguirte** por ahí (se quedan en el lado de origen y buscan otro camino, 10 min).
- Un enemigo atascado por la **vulnerabilidad** del jugador no existe: solo el jugador y compañeros se atascan.

## ATASCO EN EL HOGAR
El hogar tiene siempre al menos una ventana. Es la salida de emergencia si lo asaltan (39). Los edificios comunitarios (refugios, escuelas, cabañas del grupo) tienen ventanas con porcentaje fijo 40%.

## REGISTRO
`LOG: d3 15:30 | Z-014 | ventana: umbral 47%, tirada 31 → ATASCADO | +10 min ataque de ENE-112 (vulnerable) | liberado a los 40 min`
`FLAGS: atascos +1, ensanchados[Z-014:ventana]`

## ESTADÍSTICAS
Se muestran en la pantalla de estadísticas (38): atascos, rescates, robos por estructura.

## REGLA DEL 40-60 (tal cual)
El 40% y el 60% son los **límites duros**: ninguna regla, lore ni equipo puede hacer que el porcentaje salga de ese rango.
