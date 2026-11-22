# 37 · COMBATE CUERPO A CUERPO, DISTANCIAS Y ESCENA DE BATALLA

## BASE (tal cual)
Este bloque reemplaza el menú de acciones del 06. Las armas cuerpo a cuerpo tienen todos los movimientos; **las armas de fuego y de distancia usan los mismos movimientos derivados** (ver abajo). Fórmulas de daño, PV y XP: bloques 06, 27, 29.

## ESCENA (tal cual)
- Tu personaje se ve de cuerpo entero a la izquierda ("tercera persona"), con su carta abajo a la izquierda (retrato, barra de PV, barra de estado, nombre) y 3 círculos de acción (●●●) sobre ella.
- Cada enemigo aparece **sobre su carta** (imagen del enemigo, nombre, barra de PV, íconos de estado) a una de tres distancias: **LEJOS** (fondo), **MEDIA** (medio) y **CORTA** (pegado al jugador). Sobre cada carta hay un ícono de ataque tachado cuando ese enemigo no puede atacar ahora (lejos o aturdido).
- Arriba: `Turno: N` y `Acciones: 3`. Botón `Repetir último` junto a tu carta.
- **Tocar la carta de un enemigo** abre sus acciones sobre ese enemigo. **Tocar tu carta** abre las acciones sobre vos (defensa, objetos, esperar, escapar, rendirse). Los botones disponibles dependen de tus estadísticas y arma (ver 38).

## TURNO (tal cual)
1. Tenés **3 acciones** por turno. Cada movimiento cuesta 1 o 2 acciones (ver tabla).
2. Al gastar las 3 (o al elegir `Pasar`), actúan los enemigos: los que están en CORTA atacan; los de MEDIA o LEJOS avanzan un paso (los veloces, dos); los de distancia atacan desde MEDIA o LEJOS con −30% impacto.
3. Se aplican estados y se avanza el reloj (1 turno = 1 minuto de juego).

## MOVIMIENTOS CUERPO A CUERPO (solo en distancia CORTA)
| Botón | Acciones | Daño | Efecto en distancia | Notas |
|---|---|---|---|---|
| Golpe sigiloso | 1 | ×3 | queda corta | Solo si el objetivo no te detectó (Oculto/Precaución). Fallo −20 |
| Golpe normal | 1 | ×1 | queda corta | Base de comparación |
| Golpe rápido | 1 | ×0.7 | **retrocedés 1 paso** (corta→media) | Menos vulnerable: fallo −5 |
| Golpe potente | 2 | ×2 | quedás pegado, **sin poder retroceder** este turno | Fallo +5; aturde 20% |
| Golpe preciso | 1 | ×1 | queda corta | Fallo +5; apuntás: cabeza (+30% crítico), brazos (−25% daño enemigo 2 turnos), patas (−1 paso de velocidad) |
| Defensa (bloqueo) | 1 | — | pegado | Reduce 75% el daño de todo ataque hasta tu próximo turno; si **falla la tirada**, solo 25% |
| Empujar | 1 | 0-2 | enemigo +1 paso de distancia | Derriba a criaturas T1-T2 (pierden su próxima acción) |
| Moverse (acercarte / alejarte) | 1 | — | ±1 paso | Alejarte te hace menos vulnerable |
Aparecen más opciones según arma (ej. golpe de barrido, golpe múltiple) o stats altos.

## PROBABILIDAD DE FALLO POR VULNERABILIDAD (tal cual)
**Vulnerabilidad V (0-100):**
- Distancia del enemigo más cercano: CORTA 40 · MEDIA 20 · LEJOS 5.
- +10 por cada enemigo extra en CORTA (máx. +30).
- +15 si PV < 50%. +10 si estás Herido, Cansado o Aturdido. +10 en oscuridad/niebla.
- −15 con cobertura. −10 con compañero en CORTA. −10 con armadura E4 o superior.
Se limita a 0-100.
**Fallo base = 50% + 0.2 × V** → entre **50% y 70%**.
**Bonus del jugador** = (bonus_stat de FUE o PER ×2) + nivel/2 + bonus de arma (tier −2)×3 + modificador del movimiento. Máx. 25.
**Fallo final = fallo base − bonus**, entre 25% y 70%. Éxito = 100 − fallo.
Modificadores de movimiento: sigiloso −20, rápido −5, potente +5, preciso +5, defensa 0 (el éxito es el bloqueo).
Si el movimiento falla: no hay daño. En defensa fallida, el bloqueo es parcial (25%).

## ARMAS DE FUEGO Y DE DISTANCIA (tal cual)
- Usan los mismos movimientos con estos nombres: **Disparo sigiloso, Disparo normal, Disparo rápido, Disparo potente (2 acciones, +50% daño, retroceso), Disparo preciso, Defensa, Empujar con el arma, Recargar** (1 acción).
- **Casi nulos a distancia:** si el objetivo está en MEDIA, fallo +25; en LEJOS, fallo +40 (se sigue limitando a 70%+ de fallo; mínimo de acierto 5%). En CORTA, fallo normal.
- Sin munición o recarga pendiente: solo defensa, empujar o moverse.
- Armas de energía, explosivos y lanzadores: mismo esquema (los explosivos afectan área).

## ENEMIGOS: ATAQUE Y CONDUCTA (tal cual)
- %impacto del enemigo = base de su talla (27) − defensa del jugador (2 × RD, mínimo 10%, máximo 90%). El daño sí se reduce por RD. Si el jugador defendió: primero se tira el bloqueo.
- Los enemigos en CORTA eligen entre atacar (80%) y moverse (20% si son cobardes o huyen).
- Criaturas **de especies distintas se atacan entre sí** (ver abajo) y atacan al jugador solo si no están peleando entre ellas.
- Un encuentro tiene **una sola especie** (repetida típicamente 3 veces, 2-7 por talla, bloque 28). Nunca aparecen mezclados en el mismo grupo.

## ENEMIGOS PERSISTENTES (tal cual)
- Un enemigo que spawneó **no desaparece** hasta morir: te lo podés cruzar al volver, con el PV que le quedó (se recupera 10% por hora de juego si no está herido por veneno).
- Si te vas del combate (Escapar), siguen donde estaban, al estado actual.
- Pueden morir por **otra criatura de otra especie** mientras no estás, o delante tuyo.
- En ubicaciones hostiles, después de >48 h sin presencia del jugador se **regenera la población** (no la del jugador cercano).

## CHOQUE ENTRE ESPECIES (tal cual)
Cada 2 horas de juego en una ubicación con 2 grupos de especies distintas: cada grupo hace daño a otro (daño medio de su talla ×1.0 ×cantidad ×0.3, tirada de 50%). Si estás presente en la escena, podés mirar, intervenir de un lado, o aprovechar para golpe sigiloso. Las criaturas de la misma especie no se atacan.

## ACCIONES SOBRE VOS (tocar tu carta)
Defensa · Esperar/Pasar · Usar objeto (vendas, comida, estimulante) · Cambiar de arma · Escapar · Rendirse · Revisar estado.
- **Escapar:** %éxito = 60 + AGI×3 − 15×(enemigos en CORTA) − velocidad enemiga; si falla, perdés el turno.
- **Rendirse:** termina el combate; pasa a DERROTA (39) con robo reducido a la mitad.

## DERROTA (resumen; detalle en 39)
PV 0 = Derrotado; no hay muerte. Te arrastrás a la cama más cercana.

## FINAL DE COMBATE
XP según 27, botín (05) en los cuerpos, regeneración natural fuera del combate (11), registro en LOG.
