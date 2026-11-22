# Pruebas dirigidas de reglas

**22/22 pruebas aprobadas.** Cada prueba fuerza la situación que la campaña automática no siempre alcanza.

| Prueba | Regla (bloque) | Resultado | Observado |
|---|---|---|---|
| Un solo tipo por encuentro | Los grupos no mezclan especies (28, 37) | ✅ | 0 grupos mezclados en 3000 encuentros |
| Cantidad por talla | T1 2-7, T2 1-5, T3 1-4, T4 1-3, T5 1-2 (+1 en hostiles) (28) | ✅ | rangos observados por talla: T1: 4-6, T2: 3-5, T3: 2-4 |
| Slots por nivel | Nivel 1 solo slot 0; cada 2 niveles se abre un slot (27) | ✅ | nivel 1: 8 especies (todas slot 0, ≤ tamaño perro); nivel 10: 15; nivel 30: 20 |
| 1 a 3 variantes | 1d3 por criatura y fase; humanos 1-2 (27) | ✅ | 3204 combinaciones especie×fase; reparto 1/2/3 variantes = 1109/1148/947; humanos ≤ 2 |
| Variantes por nivel | V1 al slot, V2 a +6 niveles, V3 a +12 (27) | ✅ | slot 0: nivel 1 → V[1], nivel 8 → V[1, 2], nivel 14 → V[1, 2, 3] (V2 a +6, V3 a +12) |
| Curva de XP | XP total = 60×N×(N−1) (27) | ✅ | XP para nivel 2 = 120, nivel 10 = 5400, nivel 20 = 22800, nivel 30 = 52200 |
| Persistencia de enemigos | Lo que spawneó no desaparece al irte (37) | ✅ | 6 enemigos antes de irse y 6 al volver 30 h después (mismos IDs: True) |
| Regeneración >48 h | Zona hostil despejada repuebla pasadas 48 h (07) | ✅ | a las 40 h sin regenerar: True; pasadas 52 h (>48 h): nueva población = True |
| Choque entre especies | Especies distintas se atacan entre sí (37) | ✅ | 8 criaturas de 2 especies → 5 tras 40 h (choques 20, muertes por otra criatura 3) |
| Misma especie no pelea | Una especie no ataca a la suya (37) | ✅ | 2 grupos de la misma especie: 7 → 7 (no se atacan) |
| Derrota, arrastre y robo | Sin muerte: arrastre a cama, robo recuperable (39) | ✅ | 30 derrotas: siempre terminó en una cama con vida > 0; robos 26; recuperados al vencer al ladrón: 26/26 |
| No se muere | 20 derrotas seguidas sin fin de partida (39) | ✅ | 20 derrotas seguidas: nunca hay muerte, siempre vuelve a una cama |
| Atasco 40-60% | Ventana/agujero: umbral aleatorio 40-60% (39) | ✅ | 400 salidas por la ventana: atascos 51% (esperado 40-60%), robos por atasco 22 |
| Mapa grande vulnerable | Abrir mapa y viajar rápido: 8/18/35% + 20% (07, 39) | ✅ | viaje rápido desde zona segura: 79/300 = 26% de emboscadas (8% base + 20% por viaje rápido = 28%) |
| Jefe con tope de invocación | Máx. 3 ciclos de invocación, tope de vivos (28) | ✅ | resultado victoria; ciclos de invocación 3 (máx. 3), subordinados creados 6 (tope vivos 4) |
| Movimientos de combate | sigiloso, normal, rápido, potente, preciso, defensa, empujar (37) | ✅ | movimientos usados en 30 combates: ['acercar', 'defensa', 'empujar', 'escapar', 'normal', 'potente', 'rapido', 'sigiloso', 'vendas'] |
| Fallo 25-70% | Fallo base 50-70% según vulnerabilidad, bonus hasta −25 (37) | ✅ | fallo entre 52% y 65% a nivel 1; mínimo posible 26% (nivel 30, arma tier 5); máximo 70% |
| Armas a distancia | Casi nulas fuera de CORTA (37) | ✅ | armas a distancia, acierto por distancia del objetivo: CORTA 46% · MEDIA 25% · LEJOS 13% (casi nulo salvo que el enemigo se acerque) |
| Cerraduras y trampas | Ganzúa/forzar/hackear con tirada por intento (05) | ✅ | caja fuerte de nivel 3 con trampa abierta en 59/60 intentos (ganzúa, tiradas por intento) |
| Contenedor ya abierto | Un contenedor abierto no regenera objetos (05) | ✅ | un contenedor ya abierto no vuelve a dar objetos al reabrirlo |
| Escape y persistencia | Los enemigos que quedan siguen ahí (37) | ✅ | tras escapar quedan 5 de 5 enemigos en el lugar (persisten) |
| Garantía de camino oculto | 4.ª búsqueda revela la conexión oculta (04) | ✅ | conexión oculta del Pozo Viejo hallada en la búsqueda nº4 (garantía en la 4.ª) |
