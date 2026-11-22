# Hallazgos de la simulación y correcciones aplicadas

La simulación (código en `simulador/`) aplica las reglas de los bloques con un jugador automático. Cada punto de abajo es un problema real que apareció al correrla; se corrigió **primero en los bloques** y después en el código.

## Problemas encontrados y cómo se resolvieron
| # | Qué pasó en la simulación | Corrección | Dónde |
|---|---|---|---|
| 1 | La conexión oculta del Pozo Viejo no aparecía tras 20 búsquedas: la misión principal M-02 quedaba bloqueada | Tirada independiente de 12% por BUSCAR y **garantía en la 4.ª búsqueda** | 04 |
| 2 | Un jefe con invocación sin límite generó 987 subordinados: se podía farmear XP infinita | **Máximo 3 ciclos de invocación por combate** y tope de vivos | 28, 27 |
| 3 | El conteo de enemigos no cerraba (aparecían muertes de más): muertos por otra criatura se contaban otra vez; subordinados duplicados en el grupo | Cada enemigo se cobra una sola vez (flag); sin duplicados al invocar. Ahora **creados = muertos por el jugador + por otra criatura + vivos** en las 10 corridas | motor, 37 |
| 4 | Con la XP original se llegaba a nivel 27 en 69 días | Curva `60×N×(N−1)`; la campaña termina hacia nivel 19 y el 30 exige seguir jugando | 27 |
| 5 | Faltaba la tabla de PV y daño por nivel | PV enemigo × (1+0.10×(nivel−1)); daño × (1+0.085×(nivel−1)); daño del jugador +1.3 por nivel; tablas de jefes | 27 |
| 6 | Humanos de talla T3 a nivel 1 ganaban el 50% de los combates | Multiplicadores por **equipo E0-E5** (E0 ×0.55 PV / ×0.6 daño …) con la tabla de probabilidad por nivel | 26, 27 |
| 7 | El jefe final tenía 1800 PV y no se podía vencer | Jefes recalibrados (200 / 330 / 520 / 900 PV) | 27, 44 |
| 8 | El daño del jugador no crecía y los combates del nivel 20+ se perdían | `+floor(1.3 × nivel)` de daño | 27, 12 |
| 9 | La regeneración de población >48 h se contaba cientos de veces y no creaba nadie | Ocurre **una vez** al pasar 48 h con la zona despejada, y crea una población nueva | 07, motor |
| 10 | La IA no podía ir a un destino todavía desconocido (la ruta exigía descubrirlo antes) | Se explora **salto a salto** por las conexiones visibles | 07, bot |
| 11 | La cerradura de nivel 5 no tenía llave definida | Requiere la llave específica (en El Salar, la Llave de la Torre) | 05 |
| 12 | Faltaba la Radio en el catálogo de objetos (error al robar un objeto fabricado) | Agregada | mundo |
| 13 | BUSCAR servía para todo: abrir cajones, cajas y mirar el piso | **BUSCAR es solo exploración general**; los puntos concretos usan **Registrar [punto]** | 03, 04 |
| 14 | El bot iba a pelear con poca vida | Se cura antes de entrar (vendas, medicina) y descansa en cama | bot |
| 15 | Las armas de distancia no tenían modelo | Fallo +25% media / +40% lejos; acierto 46/25/13% según distancia | 37, motor |

## Lo que la simulación sí comprueba (22 pruebas dirigidas + 10 campañas)
Un solo tipo de enemigo por encuentro · cantidades por talla · slots por nivel · 1-3 variantes y sus niveles · curva de XP · persistencia de enemigos · regeneración >48 h · choque entre especies · derrota sin muerte, arrastre a la cama, robo y recuperación · atasco 40-60% · mapa grande vulnerable con viaje rápido · tope de invocación de jefes · movimientos de combate · fallo 25-70% · cerraduras y trampas · contenedores que no se rellenan · escape · garantía de camino oculto.
Resultado: **10/10 campañas completas (8 principales + 20 secundarias), persistencia correcta en 10/10, 22/22 pruebas.**

## Lo que NO comprueba (te lo digo claro)
- **No es un juego jugado por una IA con texto.** Es una implementación en código de las reglas; no mide cómo Haiku interpreta los bloques ni qué tan bien narra.
- Los **diálogos** se simulan como un contador de conversaciones y de relación: no se prueba el texto de los diálogos ni las opciones de respuesta.
- El **comercio** está modelado con las fórmulas de precio, pero el bot compra y vende poco (37 compras y 3 ventas por campaña): no se probó a fondo la negociación ni el stock.
- El **sigilo** se aplica solo al inicio del combate y los **compañeros** son un bonus simple; no se probó su lealtad ni sus rechazos.
- Las **adicciones y los químicos**, la fabricación avanzada, los terminales de varios niveles y las fases 4-7 con diálogo no se ejercitan en profundidad.
- No hay DLC todavía (como pediste: primero la base).
- Las derrotas son raras en campaña (≈1 por partida); por eso hay pruebas dirigidas para el arrastre, el robo y el atasco.
