# 00 · LÉEME (no se pega en la IA, es para vos)

## Qué es esto
Bloques de texto modulares para "información principal" de una IA (Haiku). Cada archivo se pega **solo**, como un bloque independiente. Juntos forman un motor de juego estilo Fallout 3 que corre por botones y probabilidades.

## Orden de pegado
| # | Bloque | Tipo | Se pega |
|---|---|---|---|
| 01 | NUCLEO_MOTOR | Regla permanente | Siempre |
| 02 | ESTADO_Y_GUARDADO | Regla permanente | Siempre |
| 03 | BOTONES | Regla permanente | Siempre |
| 04 | BUSQUEDA | Regla permanente | Siempre |
| 05 | CONTENEDORES_CERRADURAS | Regla permanente | Siempre |
| 06 | COMBATE | Regla permanente | Siempre |
| 07 | MAPA_DESPLAZAMIENTO | Regla permanente | Siempre |
| 08 | CRIATURAS_PERSONAJES | Regla permanente | Siempre |
| 09 | NPC_COMERCIO_RELACIONES | Regla permanente | Siempre |
| 10 | OBJETOS_INVENTARIO | Regla permanente | Siempre |
| 11 | TIEMPO_NECESIDADES_ESTADOS | Regla permanente | Siempre |
| 12 | PROGRESION | Regla permanente | Siempre |
| 13 | MISIONES_EVENTOS_DLC | Regla permanente | Siempre |
| 14 | LORE_PLANTILLA | **Lore (lo cambiás por universo)** | Siempre, editado |
| 15 | INTERFAZ_FORMATOS | Presentación | Siempre |
| 16 | ARRANQUE_PARTIDA | Inicio | Siempre (completás tus campos) |
| 17 | GANCHOS_MODULO_EXTERNO | Interfaz vacía | Solo si usás módulo externo |

Si la plataforma tiene límite por bloque, pegá un archivo por bloque. Si no, usá `python3 ensamblar.py` para generar `MOTOR_COMPLETO.md` y pegá todo junto.

## Cómo agregar cosas
- **Más lore / DLC:** copiá el formato de `14_LORE_PLANTILLA.md` o `13_MISIONES_EVENTOS_DLC.md` (sección DLC) y pegalo como bloque nuevo. Los DLC **suman**, nunca reemplazan reglas del motor.
- **Más botones:** agregá filas a `03_BOTONES.md` con el mismo formato (Botón | Aparece si | Tiempo | Chequeo).
- **Más enemigos/biomas/objetos:** agregalos a las tablas del lore (14). El motor no se toca.
- **Regla de prioridad:** Lore > Reglas del motor > Narración libre. Si dos bloques chocan, manda el de numeración más baja salvo que el lore diga otra cosa.

## Modos de desplazamiento (elegís uno en el 16)
- **A · Botones:** estilo Insect Prison. Rutas como botones. (Por defecto.)
- **B · Botones + Mapa:** A más mapa de papel con viaje rápido y vulnerabilidad.
- **C · Mapa mundial:** estilo Fallout 1/2, punto que se mueve, encuentros en ruta.
- **D · Mapa-escena:** estilo Town of Magic, solo se sale abriendo el mapa.
- **E · Refugio:** estilo Fallout Shelter, base + salidas.

## Contenido adulto
Estos bloques **no contienen contenido sexual**. El 17 es una interfaz neutral (variables y puntos de disparo) para que conectes tu propio módulo externo. "Tumbado/Derrotado" es un estado mecánico neutro.

## Límite realista de Haiku
Haiku pierde detalle en contexto largo. Por eso: reglas cortas, formatos fijos, estado compacto, y el **Código de guardado** (bloque 02) cada pocos turnos. Si la IA empieza a olvidar, pegá el último código de guardado.
