# 27 · NIVELACIÓN HASTA 30 Y APARICIÓN DE ENEMIGOS

## NIVELACIÓN (tal cual)
- Nivel 1 al 30 (tope; los DLC pueden ampliarlo). No hay habilidades ni perks ni puntos que repartir.
- **XP total para estar en nivel N** = `50 × N × (N − 1)`. Ejemplos: N2 = 100, N3 = 300, N5 = 1000, N10 = 4500, N20 = 19000, N30 = 43500.
- Fuentes de XP:
| Fuente | XP |
|---|---|
| Enemigo T1 | 8 |
| Enemigo T2 | 18 |
| Enemigo T3 | 40 |
| Enemigo T4 | 80 |
| Enemigo T5 / jefe | 160 / 300+ |
| Variante V2 / V3 | ×1.5 / ×2.2 |
| Modificador universal (24) | +10% cada uno |
| Descubrir ubicación | 15 |
| Misión secundaria / principal | 60-150 / 200-500 |
| Abrir cerradura difícil, hackear, trampa desactivada | 10-30 |
| Evento especial resuelto | 20-60 |
XP final por enemigo = base × `clamp(nivel_enemigo / nivel_jugador, 0.5, 2)`.
- **Efecto de subir un nivel:** PV máx = 90 + RES×10 + 5×nivel · PA = 60 + AGI×5 + nivel · `bono_nivel = nivel` · carga máx +5 por nivel · curación completa de PV al subir.
- Hitos: niveles 5, 10, 15, 20, 25, 30 → anuncio y evento de región (el lore decide el contenido).
- La subida es **automática**: al alcanzar XP, la IA aplica y registra (`d3 11:20 | nivel 4→5`).

## SISTEMA 1 — QUÉ ENEMIGOS PUEDEN APARECER (desbloqueo por SLOTS)
- Cada especie del bestiario tiene un **slot** (0 a 15). Una especie aparece si `slot ≤ floor(nivel_jugador / 2)`.
- **Nivel 1 (slot 0): pool inicial** = todo lo que no supera el tamaño de un perro (T1): caninos pequeños, herbívoros pequeños agrandados, insectos mutantes, parásitos genéricos, slimes pequeños, animales marinos blandos agrandados, y humanos normales de fase 13 en E0 (bloque 26). Siempre en su **primera variante (V1)**, sin modificador especial, solo "el animal y ya".
- **Cada 2 niveles se desbloquea un slot:** nivel 2 → slot 1, nivel 4 → slot 2, nivel 6 → slot 3 … nivel 30 → slot 15. Un slot puede desbloquear **una o varias** especies (lo indica el bestiario). Mínimo 1 enemigo nuevo por slot.
- Si el lore reasigna slots debe mantener: ≥ 1 enemigo nuevo cada 2 niveles y T1 solo en slot 0.
- **Peso de aparición** entre especies disponibles del bioma: slot actual y el anterior ×2; resto ×1; slot 0 baja a ×0.5 desde nivel 10 (los básicos se vuelven raros pero no desaparecen).
- **Tallas por nivel:** T1 slot 0 · T2 slots 1-4 · T3 slots 5-8 · T4 slots 9-12 · T5 slots 13-15.
- Fases (08/25) y temas (18) siguen el mismo gating: una fase aparece cuando el lore la habilita y su especie ya fue desbloqueada. Cada fase suma un desplazamiento de slot (fase 4: +1, fases 5-12: +2; ver 25) y tiene talla humana como mínimo desde la fase 6.

## SISTEMA 2 — QUÉ VARIANTES APARECEN (1 a 3 por criatura y fase)
- Al **iniciar la partida** (o al activar el tema), por **cada criatura de cada fase activa** se tira **1d3**: ese es el número de variantes que tendrá (sin contar jefes). Se guarda en [FLAGS] como `n_var{ID:fase}=1..3`.
  - 1 → solo V1 (Común). 2 → V1 y V2. 3 → V1, V2 y V3.
- **Activación por nivel:** V1 aparece al desbloquear la especie (slot). **V2 a los 6 niveles de ese desbloqueo**, **V3 a los 12 niveles**. Si el nivel resultante supera 30, esa variante se reserva a un jefe o evento.
- Efectos de variantes (tal cual): V1 ×1 · V2 PV×1.4, daño×1.25 y su rasgo · V3 PV×1.9, daño×1.6 y su rasgo + rasgo V2.
- **Humanos:** solo 1-2 variantes (V1 Común, V2 Veterano). El equipo se tira aparte (26).
- **Jefes** son independientes de este sistema: tienen su propia ficha, nivel mínimo, invocación con tope y recompensa (13 y 06).

## PROCEDIMIENTO ALEATORIO EN TEXTO (para que la IA lo ejecute sin código)
```
AL INICIAR PARTIDA:
1. Leer temas activos (18) y fases activas (08).
2. Para cada especie activa y cada fase activa (1-12; las 13-14 una vez por tema):
     tirar 1d3 -> n_var; guardar en FLAGS.
3. Asignar nivel de activación: V1 = 2*slot (nivel 1 si slot 0); V2 = V1+6; V3 = V1+12.
4. Generar la tabla "ENEMIGOS DISPONIBLES AL NIVEL N" (filtrando por slot, bioma, fases, lore).
5. Al subir de nivel, recalcular: nuevas especies (slot ≤ nivel/2) y nuevas variantes.
EN CADA ENCUENTRO: elegir especie por peso, fase por tabla del lore, variante entre las activas
   (50% la más nueva, 50% al azar entre las demás), tirar modificadores (24) y equipo (26).
```
También existe el código `generar_bestiario.py` que hace lo mismo y deja los resultados escritos en archivos.

## TABLA DE DESBLOQUEO (resumen por slot, ejemplo; el bestiario manda)
| Slot | Nivel | Qué se agrega |
|---|---|---|
| 0 | 1 | Todo T1: caninos pequeños, herbívoros pequeños, insectos mutantes, parásitos genéricos, slimes pequeños, marinos blandos, humanos E0 |
| 1 | 2 | Primeros T2: dingo, cabra, oveja, castor, hormiga de fuego, mantis, hidra pequeña, slime negro |
| 2 | 4 | Capibara, corzo, poni, cerdo, perro de caza, perro pastor, parásito de roca (slot 1), slime ácido (slot 1) |
| 3 | 6 | Husky, licaón, pecarí, escarabajo rinoceronte, wombat, slime de roca |
| 4 | 8 | Lobo, hormiga gigante, avispón gigante, parásito controlador |
| 5-8 | 10-16 | T3: ciervo, jabalí, mastín, hiena, mantis gigante, calamar gigante, cubo gelatinoso |
| 9-12 | 18-24 | T4: vaca, toro, bisonte, caballo, escarabajo colosal, pulpo colosal, slime rey |
| 13-15 | 26-30 | T5: jirafa, rinoceronte, hipopótamo, elefante |
(Los slots exactos de cada especie están en las tablas 19-23 y 35-36.)

## RESUMEN PARA EL JUGADOR (opcional)
La IA puede mostrar "Nivel 6 · Nuevos enemigos: ...". No muestra variantes futuras.
