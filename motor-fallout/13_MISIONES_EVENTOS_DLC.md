# 13 · MISIONES, EVENTOS ALEATORIOS Y DLC

## FICHA DE MISIÓN
`M-003 | nombre | tipo(principal/secundaria/radiante) | dador N-xxx | objetivo | pasos[] | requisitos | recompensa | tiempo límite | estado | progreso | ramas`
Estados: `disponible → activa → hecha | fallida | abandonada`. Una misión completada nunca se reinicia. Registrar cada paso en LOG.
- Cada misión debe poder resolverse de al menos 2 formas (combate / sigilo / diálogo / objeto).
- El jugador puede ignorar la misión principal indefinidamente.
- **Misiones radiantes:** generadas por la IA a partir de lo ya existente en el mundo (NPC con necesidad, ubicación hostil, objeto perdido). No inventar elementos sin crearlos y registrarlos.
- Misiones de acceso (07): solo cuando la existencia o acceso del lugar está ligada a ella.

## EVENTOS ALEATORIOS (1d100, se tiran al llegar a ubicación nueva antes de actuar, o por paso del tiempo)
Probabilidad de que ocurra evento: segura 10%, normal 20%, hostil 30%. Resultado:
| 1d100 | Evento |
|---|---|
| 1-20 | Encuentro hostil (06) acorde a bioma |
| 21-35 | Viajero/NPC neutral con oferta o información |
| 36-50 | Hallazgo menor (objeto/recurso visible) |
| 51-60 | Rastros / indicio de ubicación detectada |
| 61-70 | Peligro ambiental (derrumbe, clima, gas, trampa) |
| 71-80 | Escena del pasado (cadáver con nota, lugar saqueado, mensaje) |
| 81-90 | Evento de facción (patrulla, control, cobro) |
| 91-97 | Evento raro del lore (criatura única, fenómeno) |
| 98-100 | Evento excepcional (aliado, tesoro con condición, jefe móvil) |
Un evento irrepetible ocurre solo una vez y se registra.
Si ya fue resuelto, no vuelve a salir.

## EVENTOS POR TIEMPO
Cada 24 h de juego: tirada de evento mundial (clima extremo, mercado, movimiento de facciones). Consecuencias persistentes registradas en FLAGS.

## DLC / EXPANSIONES
Un DLC es un bloque de texto que se pega aparte y SUMA al mundo. Formato:
```
=== DLC: [Nombre] ===
ACTIVACIÓN: [cómo se desbloquea: nivel, misión, ubicación, objeto]
REGIÓN NUEVA: bioma, ubicaciones (L- nuevos con conexión a la red actual), clima
LORE ADICIONAL: facciones, historia, reglas propias
NUEVAS CRIATURAS: especies, plantillas, jefes
NUEVOS OBJETOS: armas, equipo, consumibles, planos
NUEVAS MISIONES: M- nuevos con fichas
NUEVOS BOTONES / REGLAS: (solo si hacen falta, formato del bloque 03)
NIVEL SUGERIDO: rango
RECOMPENSA FINAL
=== FIN DLC ===
```
Reglas:
- El DLC no puede romper las reglas del motor; las extiende.
- Al activarlo se añade a [FLAGS] `dlc_activo=[nombre]` y sus ubicaciones se incorporan al mapa respetando continuidad geográfica.
- El nivel de amenaza del DLC puede superar al de la región base.
- Puede haber límite de nivel mayor (ampliar tope en 12).

## FINALES Y CONSECUENCIAS
Decisiones importantes se guardan en FLAGS y alteran NPC, facciones, mapas y misiones. No deshacer salvo por regla explícita.
