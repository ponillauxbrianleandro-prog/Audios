# 18 · TEMAS DE CRIATURAS (cambia la palabra que acompaña a "Criatura")

## IDEA CENTRAL (tal cual)
"Criatura" es siempre el nombre base. El **TEMA** es la palabra que lo acompaña y que reemplaza a "animal" en toda la escala de 14 fases (08, 25). Con el tema *Animales*, la fase 4 es "criatura animal de cuerpo humanoide". Con el tema *Duendes*, la misma fase 4 es "criatura duende de cuerpo humanoide". Las fases, las reglas y las fórmulas NO cambian; solo cambia la palabra y la lista de especies base.

## CÓMO SE APLICA (tal cual)
1. El lore activa uno o más temas (CONFIG_LORE, bloque 34).
2. Cada tema trae su lista de **especies base** (bloques 19-23, 35, 36).
3. Cada especie base recibe su cadena de fases 1-14 (bloque 25).
4. Al sustituir el tema, las frases de las fases se leen con el tema nuevo: "Fase 7: humano con rasgos de [especie del tema]". "Fase 14: humano que rechaza todo lo que no parece humano" no cambia (no depende de especie).
5. Un mundo puede mezclar 2, 3 o más temas. Recomendado: 1 a 3 temas activos. Más temas = demasiados enemigos; se reparten por DLC (bloque 13) o por región.
6. El lore puede apagar especies concretas, fases concretas o recortar la cantidad de cada tema.

## LISTA DE TEMAS DISPONIBLES (tal cual, el lore elige)
| Nº | Tema (palabra que acompaña a Criatura) | Qué abarca | Especies en bloque |
|---|---|---|---|
| T1 | animales | Herbívoros, caninos, insectos mutantes, marinos blandos agrandados, parásitos genéricos, slimes | 19-23 |
| T2 | con cuernos y cuerpo robusto | Dragones, demonios, behemots, bestias de garra y cuerpo blindado de tipo "garra letal" de Fallout, diablillos | 35 |
| T3 | con halo | Ángeles y cualquier ser con aro luminoso sobre la cabeza | 35 |
| T4 | duende | Duendes, trasgos, gnomos, hadas, espíritus del bosque | 35 |
| T5 | orco | Orcos, ogros, trolls, gigantes | 35 |
| T6 | no muerta | Zombis, necrófagos (tipo "ghoul"), esqueletos, espectros, vampiros | 35 |
| T7 | elemental | Fuego, agua, tierra, aire, rayo, hielo | 35 |
| T8 | vegetal | Árboles vivientes, plantas gigantes, hongos | 35 |
| T9 | mitológica | Grifos, quimeras, unicornios, fénix, pegasos | 35 |
| T10 | artificial | Robots, androides, torretas, drones, cyborgs | 36 |
| T11 | alienígena | Seres no terrestres, "variante alienígena" de cualquier otro tema | 36 |
| T12 | mutante | Humanos mutados tipo "súper mutante", experimentos de laboratorio | 36 |
| T13 | amorfa | Slimes, gelatinas, masas vivas | 23 |
Nota: "con cuernos y cuerpo robusto" reemplaza nombres literales (dragón, demonio, garra letal) para que sirva a cualquier lore: son la misma clase con rasgos mínimos distintos. "Con halo" reemplaza solo "ángel" para cubrir cualquier ser con aro luminoso.

## QUÉ DECIDE EL LORE Y QUÉ NO (resumen; detalle en 34)
- (genérico) Qué temas están activos, qué especies y fases aparecen, nombres propios de cada especie, nombres de facciones, aspecto exacto.
- (tal cual) Escala de 14 fases, tallas T1-T5, número de variantes (1 a 3 por especie y fase), reglas de desbloqueo por nivel (27), fórmulas de combate, efectos de variantes (24).

## PLANTILLA PARA CREAR UN TEMA NUEVO (el lore puede agregar los suyos)
```
### TEMA: [palabra que acompaña a Criatura]
| ID | Nombre común | Talla | Slot | Comportamiento | V1 | V2 | V3 |
| X-01 | [especie] | T1-T5 | 0-15 | [conducta en pocas palabras] | Común | [rasgo] | [rasgo] |
```
Reglas del tema nuevo: al menos 6 especies; talla T1 para el pool inicial; slots repartidos de 0 a 15; 1 jefe por cada 5 slots.

## COMBINACIÓN DE TEMAS (tal cual)
- Cada encuentro usa UN tema principal (según bioma y región). Un tema secundario solo si el lore define alianza o convivencia.
- Cada tema mantiene su propio contador de slots, pero todos comparten el nivel del jugador.
- Si dos temas activos comparten bioma, el reparto por defecto es 70% tema principal / 30% secundario.
- Si el mundo tiene más de 3 temas, usar uno por región.

## ESTADO DE TEMAS (se guarda en [FLAGS])
`temas_activos=[T1,T10] | fases_activas=[1,2,3,4,6,7,13,14] | especies_apagadas=[...] | n_variantes{ID:fase}=1-3`
