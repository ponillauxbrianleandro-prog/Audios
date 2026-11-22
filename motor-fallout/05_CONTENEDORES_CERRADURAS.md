# 05 · CONTENEDORES, CERRADURAS Y TRAMPAS

## FICHA DE CONTENEDOR
`C-004 | tipo | ubic L-014 | estado | cerradura | trampa | contenido[] | inspeccionado | dueño`
Estados: `cerrado | abierto | forzado | roto | vacío | agotado`.
Tipos: cajón, armario, caja, cofre, taquilla, estantería, maleta, bolso, mochila, caja fuerte, recipiente, contenedor industrial, buzón, compartimento, depósito, almacén, terminal-cofre, cadáver (botín).

## GENERACIÓN DE CONTENIDO (al crear el contenedor, no al abrir)
1. Determinar tamaño: pequeño 0–2 objetos, mediano 1–4, grande 2–6, caja fuerte 2–5 (mejor calidad).
2. Cada hueco: tirar 1d100 → Nada 35 / Común 40 / Útil 18 / Raro 6 / Excepcional 1. (Caja fuerte: 5/25/40/25/5.)
3. Tipo de objeto según tipo de contenedor + ubicación + lore (ej: cajón de cocina → cubiertos, comida enlatada; taquilla de fábrica → herramientas).
4. Guardar contenido con IDs ANTES de que el jugador abra. Así es consistente aunque cierre y vuelva.
Regla: Un contenedor vacío permanece vacío. Un contenedor abierto permanece abierto.

## CERRADURAS
Niveles: 0 Sin cerradura | 1 Simple | 2 Media | 3 Difícil | 4 Muy difícil | 5 Imposible (solo llave/código).
Métodos y %éxito base (`nivel_cerr` = nivel de la cerradura; se suma bono_nivel del jugador; sin habilidades):
| Método | Requiere | %base | Fallo |
|---|---|---|---|
| Abrir normal | Sin cerradura | 100 | — |
| Llave correcta | Llave en inventario | 100 | — |
| Ganzúa | Ganzúa (consumible) | 70 − 12×nivel_cerr + AGI×3 + bono_nivel | Si tirada ≥ 90 → ganzúa se rompe |
| Forzar | Palanca o FUE | 60 − 10×nivel_cerr + FUE×3 + bono_nivel | Ruido; si ≥ 95 daña el contenido (−1 objeto frágil) |
| Hackear (cerradura electrónica) | Terminal | 70 − 12×nivel_cerr + INT×3 + bono_nivel | Tres fallos → bloqueo por 24 h |
| Código | Conocerlo | 100 | Código incorrecto: alarma posible |
Límite 5–95. Nivel 5 solo con la llave o el código específico (en El Salar: la Llave de la Torre).
Intentos: cada intento fallido cuesta tiempo. Tras 3 fallos seguidos con el mismo método, ese método ya no se puede intentar con esa cerradura hasta subir de nivel o conseguir mejor herramienta.

## TRAMPAS
`trampa: ninguna | tipo | detectada(sí/no) | desarmada`
Probabilidad de que exista: normal 5%, caja fuerte/ubicación hostil 20%, depósito militar 25%. Tipos según lore: mecánica, gas, descarga, alarma, explosiva.
- **Examinar trampa:** tirada 40 + PER×4 + bono_nivel; si éxito → detectada.
- **Desactivar:** tirada 35 + INT×4 + bono_nivel; fallo → se activa (daño o alarma). Pifia = efecto máximo.
- Si no se detectó, al abrir tirada de activación 60% (reducido por AGI).

## PROPIEDAD Y TESTIGOS
Contenedor con `dueño` ≠ jugador → abrirlo es acción no autorizada: tirada de detección por NPC cercano (09). Visible = más probabilidad.

## ACCIONES Y EFECTO
- **Registrar contenido:** muestra la lista, marca `inspeccionado=sí`. Revisar de nuevo: 8% de objeto oculto (solo la primera vez que se revisa de nuevo).
- **Tomar:** pasa a inventario (chequear carga). Elimina del contenedor.
- **Dejar:** el objeto queda registrado en el contenedor con su ID.
- **Cerrar:** el estado pasa a cerrado pero el contenido persiste.

## RECARGA
Solo contenedores especiales (comercios, depósitos) pueden recibir objetos nuevos por evento con justificación y tiempo (≥ 72 h de juego). El resto nunca se recarga.

## PLANTILLA DE SALIDA
```
📦 Caja fuerte (C-009) — cerrada, cerradura nivel 3
🎲 Hackear: tirada 41 / ≤48 → ÉXITO
Contiene: Chapas ×60, Pistola reparada (O-0071), Documento (O-0072)
```
