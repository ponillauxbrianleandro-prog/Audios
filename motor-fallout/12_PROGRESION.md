# 12 · STATS FIJOS, KARMA Y REPUTACIÓN

(El nivelado, la curva de XP y la aparición de enemigos están en el bloque 27.)

## NO EXISTEN HABILIDADES NI PERKS (tal cual)
Este motor no usa árbol de habilidades ni perks: son genéricos. El jugador no reparte puntos. Los chequeos usan solo: stats fijos, `bono_nivel`, equipo y estados.

## STATS FIJOS (1-10, los define el autor en el bloque 16; la IA no los cambia)
FUE (daño cuerpo a cuerpo, carga, forzar) · PER (puntería, detectar, buscar) · RES (PV, resistencias) · CAR (diálogo, precios) · INT (hackeo, reparación, fabricación) · AGI (PA, sigilo, ganzúa, huida, iniciativa) · SUE (críticos, rareza de botín).
`bonus_stat = stat − 5`. Fórmula general: `%éxito = base + bonus_stat×3 + bono_nivel + equipo − dificultad − estados`.

## QUÉ DA SUBIR DE NIVEL (resumen; detalle en 27)
Sube PV y PA, sube `bono_nivel` (= nivel) y se desbloquean más enemigos y variantes. Nada más: sin puntos que repartir.

## KARMA Y REPUTACIÓN
- **Karma** (−1000..+1000): + por ayudar, salvar, cumplir; − por robar, matar inocentes, traicionar. Etiquetas: Malvado / Maldad / Neutral / Bondad / Santo. Afecta diálogos y compañeros.
- **Reputación por facción/región** (−100..+100): precios, acceso, hostilidad. Se guarda en [FLAGS].
- Matar a un NPC pacífico −50; ayuda importante +30; robar sin ser visto −2; con testigos −10.
- Fase 14 (rechazo a lo no humano): sus facciones bajan reputación si el jugador va con criaturas de fases 1-12.

## DIFICULTAD (tal cual)
Fácil (muerte 0%, −10% daño recibido) · Normal · Difícil (muerte 40%, +15% daño enemigo, −25% botín). Se fija en 16.
