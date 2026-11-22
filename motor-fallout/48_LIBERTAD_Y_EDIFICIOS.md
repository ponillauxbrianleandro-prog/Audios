# 48 · LIBERTAD TOTAL: EDIFICIOS, REGISTRAR Y TODO LO QUE SE PUEDE HACER

## REGLA GENERAL (tal cual)
Casi **cualquier edificio** se puede entrar y casi **cualquier cosa** se puede registrar, abrir, mover, usar o llevarse, como en los mundos abiertos clásicos. La IA nunca dice «no se puede entrar» sin una causa concreta (cerradura, derrumbe, dueño que lo impide, requisito de misión).
Cada edificio tiene: `Z-nnn | nombre | tipo | cuadra | accesos[] | habitaciones[] | contenedores[] | NPC[] | trampas[] | estado`. Accesos: **puerta**, **ventana**, **agujero**, **conducto**, **techo**, **sótano**, **escalera** (49).

## ENTRAR Y SALIR
| Acción | Condición | Detalle |
|---|---|---|
| Abrir / cerrar puerta | siempre | sin tirada si no hay cerradura |
| Forzar puerta | cerrada o atascada | FUE, ruido 3 (05, 33) |
| Abrir cerradura (ganzúa / llave / código / hackeo) | cerradura nivel 1-5 | 05 |
| Derribar / volar la puerta | explosivo o palanca | ruido 5, puede dañar el contenido |
| Entrar por ventana, agujero, conducto, techo | acceso estrecho | 49 (atasco 40-60%) |
| Llamar a la puerta | edificio habitado | el NPC abre, ignora o se asoma |
| Entrar a propiedad privada | con dueño presente | **delito** si se detecta (33); tiempo permitido por el dueño |
| Esconderse dentro | hay mueble o rincón | sigilo (33) |
| Salir | siempre | por el acceso que se quiera |

## MOVERSE DENTRO DE UN EDIFICIO
Ir a una habitación (1-3 min) · subir/bajar por **escalera** · usar **ascensor** (con energía) · subir por **escala** o **cuerda** · saltar un hueco corto (AGI) · deslizarse por un **tobogán/ducto** · cruzar una viga · agacharse para pasar bajo un obstáculo · rodear escombros.

## REGISTRAR Y TOMAR (todo lo del Fallout, por botones)
**Registrar [punto]**: piso, mueble, repisa, cajón, ropero, caja, caja fuerte, maleta, buzón, tacho, heladera, alacena, estantería, mostrador, vitrina, locker, escritorio, archivo, baúl, mochila, bolso, carro, vehículo, tumba, cadáver, nido, jaula, barril, silo, cofre.
| Acción | Detalle |
|---|---|
| Tomar uno / tomar todo / dejar | peso y carga (10) |
| Mover un cuerpo | libera paso o permite acceso; ruido 2 |
| Saquear cadáver | contenedor con ID (05) |
| Revisar bolsillos de un NPC | hurto (33) |
| Desarmar un objeto | componentes (46) |
| Esconder un objeto | contenedor propio; no lo encuentran otros |
| Colocar un objeto / trampa | 33, 46 |
| Leer una nota, libro, cartel, mapa, holograbación | XP pequeña la primera vez (lore) |
| Escuchar una grabación o radio | pistas, noticias, misiones |
| Copiar / llevarse un archivo | terminal (abajo) |

## OBJETOS INTERACTIVOS DEL MUNDO (cada uno es un botón)
- **Camas y descanso:** dormir 1/4/8 h, esperar; solo camas libres (en propiedad ajena: delito o pedir permiso).
- **Cocinas y fogatas:** cocinar, hervir agua, calentar.
- **Agua:** beber, llenar cantimplora, lavarse, purificar; fuentes y pozos pueden estar contaminados.
- **Baños y duchas:** lavarse (quita estados de suciedad), esconderse.
- **Terminales y computadoras:** leer, hackear (INT), abrir puertas, apagar torretas, copiar datos, leer registros.
- **Radios y altavoces:** sintonizar, escuchar, apagar, transmitir.
- **Mesas de trabajo y bancos:** reparar, mejorar, fabricar, desarmar (46).
- **Tiendas y mostradores:** comerciar con el vendedor presente; robar con riesgo.
- **Máquinas expendedoras y dispensadores:** comprar/abrir (cuñas o moneda del lore), romper.
- **Interruptores, palancas, válvulas, generadores, bombas:** activar, desactivar, reparar, sabotear.
- **Cámaras, torretas, robots de seguridad:** hackear, destruir, esquivar (33).
- **Espejos, vitrinas, cuadros, estatuas:** examinar, tomar (valor).
- **Instrumentos, juegos, mesas de juego:** tocar, jugar (apuesta de cuñas, 09).
- **Botiquines, farmacias:** registrar, usar.
- **Armarios de armas y vitrinas de armas:** registrar, forzar.
- **Carteles y tableros de misiones:** leer; algunos dan misiones (66).
- **Estaciones de descontaminación, camillas, mesas médicas:** curar estados.
- **Vehículos y carretas:** registrar, mover, esconderse detrás; cobertura.
- **Escaleras caídas, puentes rotos:** reparar, saltar, buscar otro paso.
- **Plantas, minas, pozos, cursos de agua:** recolectar, excavar (herramienta), pescar.
- **Trampas y minas:** detectar, desactivar, recoger, activar a propósito (33).
- **Tumbas y altares:** examinar, profanar (karma), dejar ofrendas.

## CONTENEDORES Y SUS ESTADOS (tal cual)
`cerrado | abierto | forzado | roto | vacío | agotado | trampa activada`. Un contenedor abierto no se rellena; un vacío permanece vacío (05).

## CÓMO EVITAR EL «NO SE PUEDE»
Si el jugador pide algo, la IA mapea a la acción válida más cercana y lo resuelve con tirada; si es imposible, explica la causa en una línea y ofrece 2-3 alternativas (por ejemplo, otra entrada).

## TIEMPOS BASE (tal cual)
Entrar 1-3 min · registrar un mueble 1-3 min · registrar una habitación 10-20 min · forzar 3-10 min · hackear 5-15 min · dormir 1-8 h · fabricar 10-60 min.

## RELACIÓN CON NPC Y DELITOS
Si un NPC ve al jugador entrar sin permiso, abrir contenedores ajenos o llevarse objetos, reacciona según 33 (advertencia, reclamo, pérdida de confianza, expulsión, hostilidad). El hogar del jugador y los refugios comunitarios sin dueño no son delito. Lo **abandonado** puede registrarse libremente.

## LIBERTAD Y LORE (tal cual)
Lo que existe en cada edificio lo define el lore (99). El motor garantiza que, si algo existe, **se puede interactuar con ello** por botón.
