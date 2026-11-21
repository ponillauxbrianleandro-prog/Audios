# 00 · LÉEME (no se pega en la IA, es para vos)

## Qué es esto
Bloques de texto modulares para "información principal" de una IA (Haiku). Cada archivo se pega **solo**, como un bloque independiente (todos están bajo las 2000 palabras). Juntos forman un motor de juego estilo Fallout 1/2/3 que corre por botones y probabilidades, con nivelado 1-30, bestiario por fases y temas intercambiables.

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
| 08 | CRIATURAS_PERSONAJES (escala de 14 fases) | Regla permanente | Siempre |
| 09 | NPC_COMERCIO_RELACIONES | Regla permanente | Siempre |
| 10 | OBJETOS_INVENTARIO | Regla permanente | Siempre |
| 11 | TIEMPO_NECESIDADES_ESTADOS | Regla permanente | Siempre |
| 12 | PROGRESION (stats fijos, karma; sin habilidades ni perks) | Regla permanente | Siempre |
| 13 | MISIONES_EVENTOS_DLC | Regla permanente | Siempre |
| 14 | LORE_PLANTILLA | **Lore (lo cambiás por universo)** | Siempre, editado |
| 15 | INTERFAZ_FORMATOS | Presentación | Siempre |
| 16 | ARRANQUE_PARTIDA | Inicio | Siempre (completás tus campos) |
| 17 | GANCHOS_MODULO_EXTERNO | Interfaz vacía | Solo si usás módulo externo |
| 18 | TEMAS_DE_CRIATURAS | Regla + lore | Siempre |
| 19 | BESTIARIO_HERBIVOROS | Bestiario (tema animales) | Si el tema animales está activo |
| 20 | BESTIARIO_CANINOS | Bestiario | idem |
| 21 | BESTIARIO_INSECTOS | Bestiario | idem |
| 22 | BESTIARIO_MARINOS_BLANDOS | Bestiario | idem |
| 23 | BESTIARIO_PARASITOS_Y_SLIMES | Bestiario | idem |
| 24 | VARIANTES_UNIVERSALES | Regla permanente | Siempre |
| 25 | FASES_POR_ESPECIE | Regla permanente | Siempre |
| 26 | HUMANOS_ENEMIGOS | Regla permanente | Siempre |
| 27 | NIVELACION_Y_APARICION | Regla permanente | Siempre |
| 28 | ENCUENTROS_Y_GENERACION | Regla permanente | Siempre |
| 29 | ARMAS | Regla permanente | Siempre |
| 30 | MUNICION_Y_VARIANTES | Regla permanente | Siempre |
| 31 | CONSUMIBLES_QUIMICOS_ADICCION | Regla permanente | Siempre |
| 32 | EQUIPO_ARMADURA_HERRAMIENTAS | Regla permanente | Siempre |
| 33 | SIGILO_DETECCION_HURTO | Regla permanente | Siempre |
| 34 | REGLAS_LORE_VS_FIJO | Regla permanente | Siempre |
| 35 | CRIATURAS_FANTASIA | Bloque aparte | Solo si el lore usa fantasía |
| 36 | CRIATURAS_CIENCIA_FICCION | Bloque aparte | Solo si el lore usa ciencia ficción |
| — | `generado/BESTIARIO_GENERADO_01..34.md` | Resultado del generador | Opcional (ver abajo) |

Con `python3 ensamblar.py` se arma `MOTOR_COMPLETO.md` (bloques 01-36 juntos, sin este LÉEME) y se avisa si algún bloque pasa del límite de palabras (`--limite N` para cambiarlo, `--sin-17`, `--sin-fantasia`, `--sin-scifi` para omitir bloques).

## El bestiario generado
`python3 generar_bestiario.py --semilla 2026` asigna **1 a 3 variantes** (1d3) a cada criatura de cada fase y escribe archivos partidos de ≤1800 palabras en `generado/`, más `TABLA_DESBLOQUEO.md` (qué enemigos se suman en cada nivel). Ya dejé uno generado con semilla 2026. Opciones: `--fases 1-12`, `--apagar H-45,H-46`, `--temas animales`, `--max-palabras N`. Si no querés pegar ese resultado, la IA hace lo mismo sola siguiendo el procedimiento en texto del bloque 27.

## Cómo se decide qué es del lore y qué es fijo
Todo texto marcado **(genérico)** lo rellena el lore; **(tal cual)** se deja como está. El bloque 34 trae la tabla completa y la plantilla `CONFIG_LORE`. Ejemplos: el lore decide qué temas, especies y fases existen y cómo se llaman la comida y la medicina; lo fijo es la cantidad, los efectos, las fórmulas y los números.

## Cómo agregar cosas
- **Más lore / DLC:** copiá el formato de `14_LORE_PLANTILLA.md` o de la sección DLC del 13 y pegalo como bloque nuevo.
- **Un tema nuevo de criaturas:** usá la plantilla al final del 18 (nuevas filas con el mismo formato; el generador las toma solas si el archivo se llama `NN_*.md` y se agrega a la lista `ARCHIVOS_ESPECIES` del script).
- **Más botones:** filas nuevas en el 03.
- **Prioridad:** Lore (genérico) > reglas del motor, pero nunca sobre lo (tal cual).

## Modos de desplazamiento (elegís uno en el 16)
A Botones · B Botones + Mapa · C Mapa mundial (Fallout 1/2) · D Mapa-escena (Town of Magic) · E Refugio (Fallout Shelter).

## Contenido adulto y reglas fijas
Estos bloques **no contienen contenido sexual ni desnudez**. Los ganchos neutrales (`[VESTIMENTA_EXTRA]`, `[APARIENCIA_EXTRA]` y el 17) quedan vacíos para tu módulo externo. Todo humano o humanoide es adulto. "Femenino/masculino" describe solo cómo se ve el cuerpo.
No hay habilidades ni perks; no hay arácnidos; no hay parásitos reales (solo genéricos).

## Límite realista de Haiku
Haiku pierde detalle en contexto largo. Por eso: reglas cortas, formatos fijos, estado compacto, y el **Código de guardado** (02) cada pocos turnos.
