# 11 · TIEMPO, NECESIDADES Y ESTADOS

## RELOJ
Estado `[TIEMPO]: día, hora, clima, luz`. Toda acción tiene duración en minutos (catálogo 03). Después de cada acción: sumar minutos, recalcular día/hora, aplicar necesidades, revisar eventos por paso del tiempo.
Duraciones guía: examinar objeto 1-2 · abrir contenedor 1-3 · registrar habitación 10-20 · buscar 10-30 · explorar edificio 30-90 · viaje 20-60 por tramo · descanso 1-8 h.

## DÍA/NOCHE Y CLIMA
Luz: 06:00-19:59 día · 20:00-05:59 noche. Noche: +10% peligro, −10% impacto sin luz, +10% sigilo. Clima (tirada por día, según bioma/lore): despejado, nublado, lluvia, tormenta, niebla, calor, frío. Modifica viaje, visibilidad, necesidades.

## NECESIDADES (0 = bien, 100 = crítico)
| Necesidad | Sube cada | Efecto en 50 | Efecto en 80 | Efecto en 100 |
|---|---|---|---|---|
| Hambre | +4 por hora | −5% acciones | Debilitado (−10%) | −2 PV/hora |
| Sed | +6 por hora | −5% | Deshidratado (−15%) | −4 PV/hora |
| Fatiga | +3 por hora despierto | −5% | Cansado (−15%) | Exhausto, se desmaya |
Comer/beber reduce según objeto. Dormir reduce fatiga (8 h → −80). En lore sin necesidades, se pueden desactivar en el 14.

## RADIACIÓN / CONTAMINACIÓN (genérica, activa solo si el lore la usa)
`rad` 0-1000. Fuentes: agua sucia, comida contaminada, zonas. Niveles: 0-199 sin efecto, 200-399 Envenenado leve (−1 RES), 400-699 (−2 RES, −10% PV), 700+ grave (−4 RES, −2 PV/hora). Se reduce con medicina/descontaminación. Reemplazable por contaminación específica del lore.

## DESCANSO
- **Segura:** sin riesgo, recupera 100% PV en 8 h. Si hay cama: +10% recuperación.
- **Normal:** riesgo de encuentro (12% por cada 4 h). Recupera 50% en 8 h.
- **Hostil:** descansar bloqueado salvo que esté despejada.
Descansar 1 h = +10% PV y −10 fatiga. Despertarse por encuentro: ventaja para enemigo (−20% jugador la primera ronda).

## ESTADOS (tabla universal)
| Estado | Aparece por | Efecto | Duración | Termina |
|---|---|---|---|---|
| Herido | Daño por debajo del 40% PV | −10% acciones | Hasta curar | Medicina/descanso |
| Cansado / Exhausto | Fatiga 80/100 | −15% / −30% | — | Dormir |
| Asustado | Evento/enemigo | −15% impacto | 3 rondas | Tiempo |
| Confundido | Veneno/golpe | Acciones al azar | 2 rondas | Tiempo |
| Desorientado | Niebla/ceguera | Viaje: +25% interrupción | 1-2 h | Despejar |
| Incapacitado | PV ≤ 0 | No actúa | Hasta desenlace | 06 |
| Inmovilizado | Agarrón/trampa | No mueve | Hasta liberarse | Tirada FUE |
| Tumbado | Empujón/golpe | −20% def | 1 ronda | Acción |
| Enfermo | Contaminación | −10% todo, no cura natural | 24 h | Medicina |
| Recuperándose | Tras curación | +pv/hora | 4 h | Tiempo |
| Descansado | Dormir 8 h seguro | +5% acciones | 12 h | Tiempo |
| Envenenado | Veneno | −2 PV/ronda (comb.), −1/10 min fuera | 5 rondas / 2 h | Antídoto |
| Sangrando | Herida | −3 PV/ronda | 4 rondas | Vendaje |
Cada estado tiene: nombre, descripción, duración, efectos, condición de aparición y de eliminación. Los estados modifican probabilidades y botones disponibles.

## PASO DEL TIEMPO (eventos)
Cada hora de juego, revisar: movimiento de NPC según agenda, cambios de disponibilidad, regeneración (hostiles >48 h, recursos renovables, stock 72 h), clima, eventos programados, misiones con tiempo límite.

## CURACIÓN Y MUERTE
Curar con objetos o descanso. PV ≤ 0 → Derrotado (06). Muerte permanente según desenlace/dificultad.
