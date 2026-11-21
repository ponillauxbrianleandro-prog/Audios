# 33 · SIGILO, DETECCIÓN, HURTO Y TRAMPAS

## ESTADOS DE ALERTA (tal cual)
Cada enemigo y cada NPC vigilante tiene un estado respecto al jugador:
| Estado | Significado | Efecto |
|---|---|---|
| **Inactivo/dormido** | No percibe | Ataque sorpresa ×3, ganzúa/robo +25% |
| **Oculto** | No te ve | Ataque sorpresa ×2.5 (melé silenciosa) / ×2 (distancia) |
| **Precaución** | Sospecha (oyó ruido) | Busca; ataque sorpresa ×1.5; 40% de que te encuentre si te quedas |
| **Detectado** | Te ve | Combate normal |
El jugador tiene su propio estado: Oculto / Precaución / Detectado. Se muestra en el encabezado.

## TIRADA DE DETECCIÓN (por enemigo, al aparecer y cada ronda mientras estés oculto)
`%detecta = 35 + PER_enemigo×4 + sentido_especie(0-20) + luz(0-15) + movimiento(0-10) + ruido(0-15) − distancia(0-30) − cobertura(0-20) − sigilo_jugador`
`sigilo_jugador = AGI×3 + bono_nivel + equipo(ropa oscura +5, botas silenciosas +5, armadura pesada −10, ruidosa −15) + (agachado +10, quieto +15)`
Límite 5-95. Éxito = Precaución; segundo éxito consecutivo o ruido fuerte = Detectado.
**Sentido de especie (tal cual):** caninos 15 (olfato), insectos 5, marinos blandos 0 en tierra, parásitos 10 (vibraciones), slimes 0 (ciegos), humanos 10, vigilantes entrenados +10, nocturnos +10 de noche.
**Distancia:** lejos −30, medio −15, cerca 0, adyacente +10.
**Luz:** día +15, penumbra +5, noche 0, oscuridad −10.

## RUIDO (tal cual)
Cada acción tiene un ruido 0-5. Si el ruido acumulado en el turno ≥ 3, tirada de alerta extra a enemigos a rango medio o cerca.
| Ruido | Acciones |
|---|---|
| 0 | Quedarse quieto, arma silenciada, caminar agachado |
| 1 | Moverse lento, abrir puerta con cuidado, abrir contenedor |
| 2 | Caminar normal, recoger objetos, hablar bajo |
| 3 | Forzar cerradura, correr, arma de fuego sin silenciador, golpe contundente |
| 4 | Forzar a golpes, explosión pequeña |
| 5 | Explosión grande, alarma, combate abierto |

## SIGILO EN COMBATE
- **Emboscada (ATACAR desde Oculto):** daño ×2.5 melé silencioso / ×2 distancia; +20% impacto. Si el objetivo muere, el resto sigue Oculto o en Precaución.
- **Ocultarse en combate:** requiere cobertura y que ningún enemigo tenga línea de visión directa; tirada sigilo −20.
- **Huida con sigilo:** 40% de romper contacto si ningún perseguidor está adyacente.
- **Distracciones:** lanzar objeto (cebo W-68): atrae enemigos 3 rondas; el jugador tira sigilo +20.

## DISFRACES
Usar ropa de facción cambia el estado a "Neutral" ante esa facción: detección = 15 + inspección; si se acerca un NPC con ID que conoce al jugador, falla. Los disfraces no sirven en fases 14 (puristas) frente a criaturas.

## HURTO (ROBAR)
**Robar a NPC (botón "Robar", 03):**
- Elegir 1 objeto del inventario visible del NPC (o "Colocar" un objeto en su inventario: ver abajo).
- `%éxito = 55 + AGI×3 + bono_nivel − peso_objeto×3 − valor_objeto/10 − vigilancia(0-25) − (NPC despierto y de frente: 20) + (NPC dormido: 25) + guantes +5`. Límite 5-95.
- Fallo: el NPC te detecta (pasa a Detectado). Pifia: te ataca o llama guardias. Éxito crítico: obtienes además otro objeto liviano.
- Testigos: otros NPC con visión tiran detección (09). Si ven → reputación −10, karma −10, "buscado" posible.
- No se puede robar el equipo equipado ni armas empuñadas (solo si dormido; −15%).
**Colocar objeto (plantar):** igual fórmula, el objeto va al inventario del NPC (granada activada, nota, dispositivo).
**Robar de un contenedor ajeno:** como abrir (05) + tirada de detección por testigos.
**Robar a una criatura:** solo humanoides con inventario (fases ≥ 4); animales no tienen objetos.
**Nota:** todos los personajes son adultos (08). No se roban objetos de misión de aliados sin consecuencia.

## ESCALADA DE ALERTA (lugar)
Niveles 0-3 por ubicación: 0 normal; 1 sospecha (guardias revisan); 2 alerta (refuerzos, puertas bloqueadas); 3 hostilidad total (todo el lugar ataca). Sube con delitos detectados (+1 por incidente) y baja −1 cada 12 h sin incidentes. Nivel 3 mantiene recompensa.

## ESTADO "BUSCADO"
`buscado(facción, nivel 1-3)`: reputación −20 y precios +30% (nivel 1); acceso prohibido y ataque a la vista (nivel 2); recompensa y cazadores (nivel 3). Se limpia con soborno (chapas × nivel × 100), tiempo (7 días sin incidentes) o misión.

## TRAMPAS Y MINAS
- **Detectar:** `40 + PER×4 + bono_nivel − dificultad(0-30)`. Detector (G-11) +10. Pasar de largo sin detectar: tirada de activación 60% (−AGI×2).
- **Desactivar:** `35 + INT×4 + bono_nivel − dificultad`. Fallo: se activa; pifia: efecto máximo.
- **Reutilizar:** desactivada y recogida se vuelve objeto (W-66, W-67).
- **Colocar:** 5 min; el enemigo la detecta con %50 − sigilo del colocador.
- Tipos: cepo (inmoviliza), cuerda-alarma (alerta), mina (explosión), gas, descarga, caída, fuego, ácido. Daño y alcance según lore.
- Torretas y sistemas automáticos: tienen PV propios, detectan a 20 de PER fijo; desactivar en terminal (T-09, INT).

## ACCIONES CON RUIDO Y TIEMPO (resumen)
Todas las acciones del catálogo 03 tienen ruido en esta tabla y minutos en el 03. Al ejecutar una acción con ruido ≥ 3, tirar alerta extra.
