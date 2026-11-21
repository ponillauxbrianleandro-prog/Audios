# 06 · COMBATE Y ENCUENTROS

## DISPARO DEL COMBATE
- Enemigo hostil presente que te detecta → combate automático.
- Enemigo visible que NO te detectó → botones: ⚔ ATACAR (emboscada, bonus), SIGILO, EVITAR, OBSERVAR. **Atacar no requiere buscar antes.**
- Atacar a un NPC no hostil → pasa a hostil (09, consecuencias).

## CANTIDAD DE ENEMIGOS
La cantidad por talla y la construcción del encuentro están en el bloque 28 (T1: 2-7, T2: 1-5, T3: 1-4, T4: 1-3, T5: 1-2; jefes con séquito y tope, ver abajo). Enemigos repetidos comparten plantilla de especie y tienen ID propio: `ENE-001, ENE-002...` con PV, estado y posición independientes. Nunca mostrar 3 enemigos como uno solo.

## FICHA DE ENEMIGO (generada con 08, 19-23, 25, 26 y variantes de 24 y 27)
`ENE-001 | tema | especie | fase | variante | mods | plantilla/talla | nivel | PV/PVmax | def | ataque{nombre, daño min-max, %base} | resist{} | estados[] | pos(frente/medio/fondo) | intención | botín`
Niveles de amenaza: 1 Débil | 2 Normal | 3 Fuerte | 4 Élite | 5 Jefe. Variante (modificadores 08) modifica PV, daño y comportamiento.

## ESTADÍSTICAS Y FÓRMULAS
- **PV jugador:** 90 + RES×10 + nivel×5. **PA (energía de acción):** 60 + AGI×5.
- **Iniciativa:** AGI + PER + 1d10. Orden fijo por ronda; se recalcula si cambia el grupo.
- **%Impacto** = base_arma + bono_nivel − (def_enemigo) + bonus_stat(PER para distancia / FUE para melé) + situación (emboscada +20, apuntado +15, cobertura enemigo −15, oscuridad −10) − penalización_estados. Límite 5–95.
- **Daño** = rango arma + bonus FUE (melé) − reducción_armadura. Mínimo 1. Crítico (tirada ≤ 5, o ≤ SUE/2): ×2.
- **Defensa/Reducción:** valor abstracto de armadura (bloque 10) resta daño; no anula.
- **Pifia (≥ 96):** arma atascada (pierde acción) o ataque a aliado.

## ACCIONES EN COMBATE (1 acción principal por turno + 1 menor)
| Botón | Efecto | Chequeo |
|---|---|---|
| ⚔ Atacar | Ataque básico a objetivo | %Impacto |
| 🎯 Apuntar (parte del cuerpo) | −2 PA extra, +15% y efecto de miembro: cabeza (+daño/aturdir), brazos (−daño enemigo), piernas (−huida/inmoviliza), torso (estándar) | %Impacto |
| 🛡 Defender | Reduce daño 50% hasta tu próximo turno | No |
| 👟 Empujar | Aleja/derriba enemigo; 100% se intenta, éxito 60%+FUE×3−peso; fallo: el enemigo puede agarrarte o **tumbarte** | Sí |
| 🧱 Cubrirse | +15% def. si hay cobertura | No |
| 🔫 Recargar / cambiar arma | Consume turno | No |
| 🩹 Usar objeto | Medicina/granada/comida | Según objeto |
| ✨ Acción especial de arma | Solo si el arma lo define (ráfaga, golpe potente, lanzar) | Sí |
| 🤫 Sigilo (ocultarse) | Si hay cobertura o escape; rompe contacto | Sí |
| 🗣 Intimidar / rendición | Si enemigo racional: 20%+CAR×4 | Sí |
| 🏃 Huir | %huir = 50 + AGI×3 − velocidad_enemigo ± terreno | Sí |
| Cambiar de objetivo / posición | Menor, 1 vez por turno | No |
Reglas: acciones consumen PA. Si PA=0, solo Defender o Huir.

## IA ENEMIGA (decisión simple, sin inventar)
Cada ENE decide por su comportamiento (08): agresivo ataca, defensivo guarda posición, manada flanquea, cobarde huye bajo 25% PV, territorial no persigue fuera de zona. Objetivo por defecto: jugador (o compañero con menor defensa si es manada).

## ESTADOS DE COMBATE (duración en rondas)
Herido (sangrado: −3 PV/ronda, 4 rondas), Aturdido (pierde acción, 1), Asustado (−15% impacto, 3), Derribado/Tumbado (no actúa 1 ronda, enemigos +20% contra ti; levantarse cuesta acción), Inmovilizado (no se mueve/huye hasta liberarte, tirada FUE), Cegado (−30%), Envenenado (−2 PV/ronda, 5), Confuso (objetivo aleatorio, 2), Incapacitado (PV ≤ 0 sin morir; ver derrota).
Cada estado tiene nombre, efecto, duración y forma de terminar.

## DERROTA DEL JUGADOR (neutral)
PV ≤ 0 → estado **Derrotado**. Si hay enemigos vivos, se ejecuta la tirada de DESENLACE:
| Resultado | % base | Efecto |
|---|---|---|
| Despiertas más tarde, perdiste objetos | 30 | −% chapas, 1-2 objetos al azar, tiempo +3 h, ubic cercana |
| Escapas herido | 20 | Con 1 PV, +1 h, marcado como objetivo |
| Capturado | 20 | Se activa evento de captura según lore (bloque 17 si está activo) |
| Rescate (NPC aliado) | 10 | Si hay aliados cerca |
| Muerte permanente | 20 (0 en modo fácil, 40 en difícil) | Fin; ofrecer cargar guardado |
Registrar: `FLAGS: contador_derrotas +1`. Si el módulo externo (17) está activo, entregarle el control en `[PUNTO_DERROTA]`.

## JEFES E INVOCACIONES
- Todo jefe define: `invoca: tipo, cantidad por invocación (1-3), cooldown (rondas), tope vivos (ej. 6), condición de corte (matar al jefe/destruir fuente), PV de fuente`.
- Prohibido invocar sin tope. Si el tope se alcanza, el jefe cambia de acción.
- Efectos de entorno (trampas, mecanismos) tienen tirada y duración definidas.

## VICTORIA Y BOTÍN
XP por enemigo según talla, variante y nivel: ver bloque 27. Botín desde `botín` del enemigo según lore. Cadáveres = contenedores (05) con ID. Ubicación hostil despejada → `despejada=sí`, contador de regeneración inicia (07).

## SEPARACIÓN
Mecánica (tiradas, deltas) se muestra primero en formato corto; luego narración breve. Plantilla en el bloque 15.
