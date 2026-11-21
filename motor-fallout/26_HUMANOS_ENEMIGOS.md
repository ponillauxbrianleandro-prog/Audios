# 26 · HUMANOS Y HUMANOIDES COMO ENEMIGOS Y NPC

## REGLAS (tal cual)
- Los humanos (fase 13) y los humanoides de fases 4-12 y 14 usan este bloque. Todos son adultos.
- **Tienen pocas variantes: 1 o 2** (V1 Común, V2 Veterano), porque su peso real lo da el **equipamiento**, que se genera con un sistema aparte (nivel de equipo E0-E5) y no cuenta como variante.
- La variante V2 (Veterano) se activa 6 niveles después de su slot.

## NIVEL DE EQUIPO (E0-E5) — INDEPENDIENTE DE LA VARIANTE
| Tier | Equipo | Arma típica (29) | RD total | Notas |
|---|---|---|---|---|
| E0 | Sin equipo especial; ropa mínima o ninguna ropa especial. **La variante de vestimenta la define el módulo externo `[VESTIMENTA_EXTRA]`** | Puños o improvisada | 0 | Inicio del juego |
| E1 | Ropa básica y arma improvisada | Tier 1 (improvisada) | 1 | Civiles y saqueadores pobres |
| E2 | Ropa reforzada, arma común | Tier 2 | 3 | |
| E3 | Armadura ligera, arma mejorada | Tier 3 | 6 | |
| E4 | Armadura media/militar, arma militar | Tier 4 | 10 | |
| E5 | Armadura pesada o asistida, arma especial | Tier 5 | 16 | Élite |
**Probabilidad de tier según nivel del jugador (tirada independiente por humano):**
| Nivel | E0 | E1 | E2 | E3 | E4 | E5 |
|---|---|---|---|---|---|---|
| 1-4 | 55 | 35 | 10 | 0 | 0 | 0 |
| 5-8 | 25 | 40 | 30 | 5 | 0 | 0 |
| 9-12 | 10 | 25 | 40 | 22 | 3 | 0 |
| 13-18 | 3 | 12 | 30 | 38 | 15 | 2 |
| 19-24 | 0 | 5 | 20 | 35 | 32 | 8 |
| 25-30 | 0 | 2 | 10 | 28 | 40 | 20 |
Ajustes: facciones organizadas +1 tier, mendigos/civiles −1, jefes de grupo +1. Un E0 no lleva cargador de repuesto ni objetos valiosos.
**El tier de equipo de un humano NO escala con el slot de aparición ni con la variante** (se tira aparte).

## ARQUETIPOS (nombres propios los pone el lore) (genérico)
| ID | Arquetipo | Talla | Slot | Comportamiento | V1 | V2 |
|---|---|---|---|---|---|---|
| U-01 | Civil | T3 | 0 | pacífico, huye 60% | Común | Veterano (pelea) |
| U-02 | Superviviente | T3 | 0 | defensivo | Común | Veterano |
| U-03 | Vagabundo | T3 | 0 | neutro, pide/roba | Común | Veterano |
| U-04 | Saqueador | T3 | 0 | agresivo, grupo 2-4 | Común | Veterano |
| U-05 | Bandido | T3 | 1 | emboscada, grupo 2-5 | Común | Veterano |
| U-06 | Cazador | T3 | 2 | rastrea, distancia | Común | Veterano |
| U-07 | Mercenario | T3 | 3 | disciplinado, grupo 2-3 | Común | Veterano |
| U-08 | Guardia | T3 | 3 | defensivo, vigila | Común | Veterano |
| U-09 | Esclavista | T3 | 5 | captura (inmoviliza), grupo 3-5 | Común | Veterano |
| U-10 | Cultista | T3 | 5 | fanático, no huye | Común | Veterano |
| U-11 | Soldado | T3 | 7 | táctico, cobertura | Común | Veterano |
| U-12 | Francotirador | T3 | 8 | distancia, oculto | Común | Veterano |
| U-13 | Líder de grupo | T3 | 9 | da órdenes (aliados +10%) | Común | Veterano |
| U-14 | Científico | T3 | 4 | débil, usa dispositivos | Común | Veterano |
| U-15 | Médico | T3 | 4 | cura aliados | Común | Veterano |
| U-16 | Mecánico | T3 | 4 | repara, torretas | Común | Veterano |
| U-17 | Comerciante | T3 | 0 | neutral, defiende caravana | Común | Veterano |
| U-18 | Mensajero | T3 | 0 | evita combate | Común | Veterano |
| U-19 | Élite | T3 | 12 | armas pesadas, E4-E5 | Común | Veterano |
| U-20 | Comandante | T3 | 14 | jefe de facción | Común | Veterano |
Talla T3 = PV 80 | daño 8-15 | impacto 58 (bloque 19). Humanos de otras fases usan la tabla del 25.

## HUMANOS PURISTAS (fase 14)
Rechazan todo lo que no sea humano. Si el jugador va con una criatura de fases 1-12 o con rasgos no humanos: precios +30%, acceso restringido, diálogo hostil, reputación −10 por encuentro. Si la criatura es inofensiva, igual la evitan.

## FASES 6-12 Y SU EQUIPO
Humanos de fases 6-12 pueden usar E0-E5 según tabla; fase 9 usa traje completo (E2), fase 11 uniforme/accesorios de trabajo (E1), fase 8 prótesis integradas (+5 RD sin armadura).

## COMPORTAMIENTO EN COMBATE (tal cual)
Cobardes huyen al 30% PV; fanáticos nunca; disciplinados usan cobertura; grupos con líder siguen su órden; distancias: francotirador evita cuerpo a cuerpo. Rendición: 20% si el grupo pierde a su líder.

## RECOMPENSA
Botín según tier (E0: casi nada; E5: arma y armadura de ese tier, con 40% de durabilidad menor al 100%). Humanos mueren como contenedor (05) con ID.

## GANCHO NEUTRO
`[VESTIMENTA_EXTRA]`: lo usa el módulo externo (17) para modificar vestimenta. Si está desactivado, se usan las descripciones estándar.
