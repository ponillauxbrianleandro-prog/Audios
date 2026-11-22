# 03 · CATÁLOGO UNIVERSAL DE BOTONES

## REGLAS
- Mostrar SOLO botones válidos para la escena actual (según elementos existentes en [ESCENA]).
- Numerarlos cada turno. Agrupar por categoría. Máx. ~12 botones; si hay más, agrupar ("Contenedores ▸ 3").
- Cada botón tiene: Aparece si | Tiempo | Chequeo. El tiempo está en minutos de juego.
- Botones SIEMPRE disponibles (salvo incapacitado): Inventario, Estado, Mapa (muñeca), Descansar* (*si no hay enemigos), Guardar.
- Si el jugador está en combate, el menú cambia al de COMBATE (bloque 06) y los botones de exploración se ocultan.
- El jugador puede escribir texto libre: mapear a un botón válido.

## A. COMBATE DIRECTO (sin buscar antes; ver 37)
| Botón | Aparece si | Acciones | Chequeo |
|---|---|---|---|
| ⚔ ATACAR (elige enemigo) | Hay enemigo visible o presente, aunque no hayas buscado | — | abre el menú de acciones |
| Golpe sigiloso | Enemigo no te detectó y está en CORTA | 1 | Sí (fallo −20, ×3 daño) |
| Golpe normal | Enemigo en CORTA | 1 | Sí |
| Golpe rápido | Enemigo en CORTA | 1 | Sí (×0.7; retrocedés 1 paso) |
| Golpe potente | Enemigo en CORTA | 2 | Sí (×2; quedás pegado) |
| Golpe preciso | Enemigo en CORTA | 1 | Sí (cabeza/brazos/patas) |
| Defensa | Enemigo en CORTA o te atacan | 1 | Sí (bloquea 75%) |
| Empujar | Enemigo en CORTA | 1 | Sí (+1 distancia; derriba T1-T2) |
| Acercarse / Alejarse | Siempre en combate | 1 | No |
| Disparo (variantes) | Arma de distancia y munición | 1-2 | Sí (fallo +25 media / +40 lejos) |
| Recargar | Arma de distancia | 1 | No |
| Pasar · Escapar · Rendirse · Vendas | Menú de tu carta | 0-1 | Escapar: Sí |
| 🤫 Sigilo / 🏃 Evitar / 👁 Observar | Enemigo que no te detectó | 1-2 | Sí |

## B. EXPLORACIÓN GENERAL
| Botón | Aparece si | Min | Chequeo |
|---|---|---|---|
| 🔍 Explorar (BUSCAR general) | Casi siempre (excepto combate); NO sirve para abrir cajones ni cajas | 10-30 | Sí (04) |
| Registrar [piso / cajón / ropero / estantería / caja fuerte / cadáver] | Existe ese punto en la escena | 2-10 | Sí si hay cerradura (05) |
| Examinar alrededores | Siempre | 5 | No |
| Escuchar el entorno | Siempre | 3 | Sí (PER) |
| Buscar entradas / salidas | Hay estructura o terreno cerrado | 10 | Sí |
| Buscar rastros | Exterior o huellas posibles | 10 | Sí |
| Observar estructuras | Hay estructuras | 5 | No |
| Revisar puntos de interés | Hay puntos marcados en [ESCENA] | 5 | No |
| Examinar posibles caminos | Hay conexiones ocultas o desconocidas | 10 | Sí |

## C. ESTRUCTURAS
| Botón | Aparece si | Min | Chequeo |
|---|---|---|---|
| Acercarse a [estructura] | Estructura exterior no visitada | 3 | No |
| Entrar / Salir | Hay acceso libre | 2 | No |
| Abrir/Cerrar [puerta] | Existe puerta | 1 | No (si no está bloqueada) |
| Forzar [puerta] | Puerta bloqueada/atascada | 5 | Sí (FUE) |
| Abrir cerradura [puerta] | Puerta con cerradura + ganzúa/llave | 3-10 | Sí (05) |
| Examinar [puerta/ventana/pared] | Existe el elemento | 2 | No |
| Abrir / Pasar por [ventana] | Existe ventana (rota o no) | 2 | Sí si estrecha |
| Subir / Bajar | Hay escaleras/niveles | 2 | No |
| Explorar [habitación] | Hay habitaciones sin explorar | 10-20 | → 04 |
| Revisar salida secundaria | Existe | 5 | No |
| Examinar estructura dañada | Hay daño estructural | 5 | Sí |

## D. CONTENEDORES (ver 05)
| Botón | Aparece si | Min | Chequeo |
|---|---|---|---|
| Examinar contenedor | Existe contenedor | 1 | No |
| Abrir | Contenedor cerrado sin cerradura | 1 | No |
| Forzar | Contenedor cerrado/atascado | 3 | Sí (FUE) |
| Usar ganzúa / llave | Cerradura + herramienta/llave | 3-10 | Sí |
| Hackear terminal | Cerradura electrónica + terminal | 5-15 | Sí (INT) |
| Examinar cerradura / trampa | Contenedor cerrado | 2 | Sí (PER) |
| Desactivar trampa | Trampa detectada | 3 | Sí |
| Registrar contenido | Abierto y no inspeccionado | 2 | No |
| Tomar todo / Tomar uno | Contiene objetos | 1 | No |
| Dejar objeto | Abierto | 1 | No |
| Revisar de nuevo | Ya registrado | 2 | Sí (puede haber oculto) |
| Cerrar | Abierto | 1 | No |

## E. OBJETOS
| Botón | Aparece si | Min | Chequeo |
|---|---|---|---|
| Examinar | Objeto visible o en inventario | 1 | No |
| Recoger | Objeto suelto, carga suficiente | 1 | No |
| Equipar / Quitar | Objeto en inventario y equipable | 1 | No |
| Usar | Consumible/dispositivo usable | 1 | Según objeto |
| Leer | Documento/libro/nota | 2-10 | No |
| Reparar | Dañado + herramienta/componentes | 10 | Sí |
| Activar / Desactivar / Encender / Apagar | Dispositivo con interruptor | 1 | No |
| Soltar / Dejar en otro lugar | En inventario | 1 | No |
| Entregar | NPC presente y objeto adecuado | 1 | No |
| Comparar | 2 objetos del mismo tipo | 1 | No |
| Desarmar / Fabricar | Taller o herramientas + planos | 10-60 | Sí |

## F. TERRENO
| Botón | Aparece si | Min | Chequeo |
|---|---|---|---|
| Examinar suelo / vegetación / rocas / agua | Existe en exterior | 3-5 | No |
| Recolectar recursos naturales | Recurso disponible | 10 | Sí (PER) |
| Beber / Recoger agua | Fuente de agua (ver rad.) | 2 | No |
| Buscar acceso oculto | Terreno complejo | 15 | Sí |
| Inspeccionar zona elevada / Escalar | Hay elevación | 5-15 | Sí (AGI) |
| Inspeccionar obstáculos | Hay obstáculo | 3 | No |

## G. NPC (ver 09)
| Botón | Aparece si | Min | Chequeo |
|---|---|---|---|
| Hablar | NPC presente y no hostil | 3 | No |
| Preguntar (lugares / personas / hechos / rumores) | En conversación | 3 | No |
| Negociar | Hay objeto/precio/favor | 5 | Sí (CAR) |
| Comerciar | NPC comerciante y relación ≥ neutral | 5 | No |
| Pedir ayuda / Ofrecer ayuda | Hay misión o necesidad | 3 | No |
| Reclutar / Seguir / Esperar | NPC compañero posible | 1 | Según relación |
| Intimidar / Persuadir / Engañar | NPC presente | 3 | Sí |
| Robar | NPC o contenedor ajeno cercano | 2 | Sí (AGI, vis.) |
| Atacar | NPC no hostil → se vuelve hostil | 1 | Sí |
| Despedirse | En conversación | 0 | No |

## H. MAPA Y VIAJE (ver 07)
| Botón | Aparece si | Min | Chequeo |
|---|---|---|---|
| 📟 Consultar muñeca | Siempre | 0 | No (solo info) |
| 🗺 Abrir mapa de papel | Tiene mapa | 1 | Riesgo de interrupción (07) |
| ➡ Ir a [ubicación conectada] | Ruta libre y accesible | según dist. | Eventos en ruta |
| ⚡ Viaje rápido | Ubicación descubierta con ruta válida | según dist. | Riesgo (07) |
| Marcar dirección aproximada | Mapa abierto | 0 | No |
| Examinar conexión bloqueada | Hay conexión bloqueada | 3 | No |

## I. SUPERVIVENCIA Y SISTEMA
| Botón | Aparece si | Min | Chequeo |
|---|---|---|---|
| 💤 Descansar (1/4/8 h) | Sin enemigos; mejor en ubicación segura/cama | 60-480 | Riesgo de encuentro según tipo |
| Comer / Beber / Curar / Usar medicina | Consumible en inventario | 1-5 | No |
| Cocinar / Purificar | Fuego/estación + ingredientes | 10 | No |
| Montar refugio | Material + exterior | 30 | Sí (INT) |
| Inventario | Siempre | 0 | No |
| Estado / Ficha personaje | Siempre | 0 | No |
| Misiones | Siempre | 0 | No |
| Subir de nivel (automático, ver 27) | XP suficiente | 0 | No |
| Guardar (código) | Siempre | 0 | No |

## EXPANSIÓN
Para agregar un botón: fila nueva en la categoría correcta con Aparece si / Min / Chequeo. Para un DLC con botones propios: crear categoría "J. [Nombre DLC]" en un bloque aparte.
