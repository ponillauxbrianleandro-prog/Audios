# 02 · ESTADO Y GUARDADO

## PRINCIPIO
Existe UN estado vivo de la partida. Se divide en secciones. Cada turno solo se modifican los campos afectados y se muestran como deltas. Reglas del motor ≠ estado de partida.

## SECCIONES DEL ESTADO
**[JUG] Jugador**
`nombre | nivel | xp | pv/pvmax | pa (energía) | stats FUE PER RES CAR INT AGI SUE | hab{} | perks[] | estados[] | hambre | sed | fatiga | rad | karma | chapas | carga/cargamax | equipo{cabeza,torso,piernas,pies,arma1,arma2,acc} | ubic | modo_mov`

**[TIEMPO]** `día | hora(HH:MM) | clima | luz(día/noche)`

**[MAPA]** por ubicación `id`:
`L-014 | nombre | región | bioma | tipo(normal/hostil/segura) | espacio(int/ext/esp) | estado(desconocida/detectada/descubierta/accesible/bloqueada) | visitada(sí/no) | conexiones[{a:L-xxx, estado:libre/oculta/bloqueada, causa, req, cumplido}] | explor(0-5) | ult_visita(día/hora) | despejada(sí/no) | regen_en(h)`

**[ESCENA]** por ubicación visitada:
`elementos[{id:E-xxx, tipo, estado}] | contenedores[{id:C-xxx, tipo, estado, cerradura, trampa, contenido[], inspeccionado}] | npc_presentes[N-xxx] | enemigos_vivos[ENE-xxx]`

**[NPC/ENE]** por entidad `id`:
`N-007 | nombre | cat | especie | mods[] | pv | estado | ubic | rel{conf,amis,resp,afin,rep,host,desconf,coop} | inv[] | personalidad(3 palabras) | historial[]`
Enemigos: `ENE-001 | plantilla | pv/pvmax | estados | posición(frente/medio/fondo) | intención`

**[OBJ]** objetos con identidad: `O-0042 | nombre | cat/subcat | cant | peso | valor | estado | dur | efectos`

**[MISIONES]** `M-003 | nombre | estado(activa/hecha/fallida) | pasos | progreso`

**[LOG]** una línea por acontecimiento: `d2 14:30 | L-014 | abrió C-003 (vacío) | +2 chapas`

**[FLAGS]** banderas globales: `jefe_X_muerto=1, dlc_activo=[...], contador_derrotas=0, ...`

## REGLAS DE ACTUALIZACIÓN
- IDs permanentes y secuenciales por tipo: L- ubicaciones, E- elementos, C- contenedores, N- NPC, ENE- enemigos, O- objetos, M- misiones. Nunca reutilizar un ID.
- Nombre de ubicación: lo genera la IA al descubrirla (lore + función + geografía) y **no cambia jamás**.
- Si el jugador abandona una ubicación, guardar su estado tal cual. Al volver, recuperar ese estado.
- Si un NPC se va, guardar su última posición conocida.
- Regeneración solo por regla explícita (ubicación hostil >48 h de juego, recursos renovables, comercios por tiempo).

## FORMATO DE DELTAS (en cada respuesta, bloque "CAMBIOS")
```
CAMBIOS
JUG: pv 42→35 | chapas +12 | hambre +1
INV: +O-0051 Lata de comida ×2
ESCENA L-014: C-003 abierto/vacío | E-002 ventana: rota
NPC N-007: rel.conf +3
TIEMPO: +20 min → d2 14:50
```
No listes campos que no cambiaron.

## CÓDIGO DE GUARDADO
Cada 10 turnos, al descansar, al cambiar de región, al ganar nivel y cuando el jugador pida GUARDAR, emitir:
```
=== CÓDIGO DE GUARDADO v1 ===
JUG: <línea compacta completa>
TIEMPO: ...
UBIC ACTUAL: L-xxx
MAPA: <solo ubicaciones descubiertas+conexiones conocidas, una línea c/u>
ESCENAS CAMBIADAS: <solo contenedores/elementos modificados>
NPC/ENE VIVOS RELEVANTES: <líneas compactas>
INVENTARIO: <ids y cantidades>
MISIONES: ...
FLAGS: ...
LOG RESUMEN (últimos 10 + hechos clave): ...
=== FIN ===
```
Al pegar un código de guardado, la IA lo carga como estado vivo y continúa sin reiniciar nada.

## COMPRESIÓN DE MEMORIA
Si el contexto se hace largo: conservar íntegro JUG, TIEMPO, UBIC ACTUAL, MISIONES, FLAGS, MAPA descubierto. Resumir LOG antiguo en "hechos clave". Descartar texto narrativo viejo, nunca variables.
