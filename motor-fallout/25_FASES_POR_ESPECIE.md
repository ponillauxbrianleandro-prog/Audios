# 25 · FASES POR ESPECIE (cómo cada criatura recorre las 14 fases)

## REGLA CENTRAL (tal cual)
**Cada especie base** del bestiario (19-23, 35, 36), de cualquier tema, tiene su propia cadena de fases 1 a 14. La fase describe cuánto se parece al ser humano o cuánto se relaciona con la ropa y rasgos de esa especie (08). Los textos de cada fase están en el bloque 08; aquí se define **cómo se nombra, qué cambia en la ficha y cuáles generan versiones por especie**.
Fases 13 y 14 (humano normal / purista) NO dependen de la especie: se generan una sola vez por tema como "Humano" (bloque 26).
El lore decide qué fases aparecen (tal cual: cuántas, genérico: cuáles). Una fase puede no aparecer.

## FÓRMULA DE NOMBRE (tal cual; {E} = nombre de la especie)
| Fase | Se llama | Ejemplo con Lobo | Ejemplo con Vaca | Ejemplo con Pulpo |
|---|---|---|---|---|
| 1 | {E} | Lobo | Vaca | Pulpo |
| 2 | {E} de cuerpo semihumano | Lobo de cuerpo semihumano | Vaca de cuerpo semihumano | Pulpo de cuerpo semihumano |
| 3 | {E} erguido (pokémico) | Lobo erguido | Vaca erguida | Pulpo erguido |
| 4 | {E}-humanoide | Hombre-lobo (humanoide lobo) | Bovino humanoide | Pulpo humanoide |
| 5 | {E} quimera (mitad humano) | Hombre-lobo mitad humano | Minotauro (y variantes) | Humano-pulpo |
| 6 | Humano-{E} | Humano-lobo | Humano-toro | Humano-pulpo marino |
| 7 | Persona con rasgos de {E} | Persona con rasgos de lobo | Persona con rasgos de vaca | Persona con rasgos de pulpo |
| 8 | Persona-{E} (se considera {E}) | Persona-lobo | Persona-vaca | Persona-pulpo |
| 9 | Furry de {E} | Furry lobo | Furry vaca | Furry pulpo |
| 10 | Persona con accesorios de {E} | Persona con accesorios de lobo | ... | ... |
| 11 | Trabajador/a de espectáculo con accesorios de {E} | idem | idem | idem |
| 12 | Persona instintiva-{E} | Persona instintiva-lobo | ... | ... |
| 13 | Humano | (no depende) | (no depende) | (no depende) |
| 14 | Humano purista | (no depende) | (no depende) | (no depende) |

## TABLA DE CAMBIOS POR FASE (tal cual)
| Fase | PV× | Daño× | Habla | Manos | Equipo máx. | Comportamiento por defecto |
|---|---|---|---|---|---|---|
| 1 | 1.0 | 1.0 | No | No | Ninguno | Instinto de especie |
| 2 | 1.0 | 1.0 | No | No | Ninguno | Instinto |
| 3 | 1.1 | 1.0 | No | Patas como manos | Objetos simples | Curioso / hostil |
| 4 | 1.2 | 1.1 | **Sí** | Patas como manos | E1 | Comunica, negocia |
| 5 | 1.5 | 1.3 | Sí | Manos | E3 | Social / territorial |
| 6 | 1.3 | 1.2 | Sí | Humanas | E3 | Variable |
| 7 | 1.1 | 1.1 | Sí | Humanas | E4 | Social, tamaño humano |
| 8 | 1.1 | 1.0 | Sí | Humanas + prótesis | E3 | Imita a su especie |
| 9 | 1.0 | 1.0 | Sí | Humanas (traje) | E2 | Juguetón, pacífico |
| 10 | 1.0 | 1.0 | Sí | Humanas | E4 | Individual |
| 11 | 0.9 | 0.9 | Sí | Humanas | E1 | Servicial, trabajador |
| 12 | 1.1 | 1.1 | Sí | Humanas | E3 | Instintivo (iniciativa +10) |
| 13 | 1.0 | 1.0 | Sí | Humanas | E5 | Normal |
| 14 | 1.0 | 1.0 | Sí | Humanas | E5 | Evita / rechaza fases 1-12 |
"Equipo máx." = tier máximo (bloque 26) que puede llevar.

## SLOT Y TALLA POR FASE (tal cual)
Las formas más humanas aparecen más tarde y tienen al menos tamaño humano:
| Fase | Slot de la fase | Talla mínima |
|---|---|---|
| 1, 2, 3 | slot de la especie | la de la especie |
| 4 | slot + 1 | T2 |
| 5 | slot + 2 | T2 |
| 6 a 12 | slot + 2 | T3 |
Tope de slot: 15. Ejemplo: Ratón (slot 0, T1) → fase 4 en slot 1 (nivel 2), fase 7 en slot 2 (nivel 4) con talla T3. Las fases 13 y 14 usan los slots propios de los humanos (26). Las variantes V2 y V3 se activan 6 y 12 niveles después del slot de **esa fase** (27).

## GÉNERO CORPORAL (tal cual)
Cada fase y cada especie tiene versión femenina y masculina. Estas palabras describen solo cómo se ve el cuerpo; no significan mujer ni hombre ni fijan sexo biológico ni género. Un personaje puede tener rasgos femeninos y verse masculino, o al revés. Se elige por ID y no cambia.

## VISTA DE FASES POR TEMA (ejemplo, el lore completa)
- **Animales:** fases 1-12 por cada especie de 19-23.
- **Con cuernos y cuerpo robusto:** fase 1 = bestia; fase 5 = humanoide con cuernos y cuerpo robusto (tipo demonio); fase 13 humano.
- **Con halo:** fases 4-7 humanoides con halo.
- **Artificial:** fases 1-3 máquina animal, 4-5 androide, 6-7 cyborg, 13 humano.
- **Alienígena:** como Animales pero con variante Alienígena (24).

## GENERACIÓN DE ENTIDAD (tal cual)
1. Elegir tema → especie → fase (según lore y bioma).
2. Tirar variante del bestiario (V1-V3 según nivel, 27).
3. Tirar modificadores universales (24).
4. Si fase ≥ 4, generar nombre propio (genérico), personalidad, apariencia (femenina/masculina) y equipo (26).
5. Registrar ID y ficha.

## FICHA RESUMIDA POR ENTIDAD
`ENE-012 | tema=animales | especie=H-26 Caballo | fase=5 | variante=V2 | mods=[Gigante] | app=masc | amenaza=3`

## ESTRUCTURA PARA EL MÓDULO DE APARIENCIA (gancho vacío)
`[APARIENCIA_EXTRA]`: el módulo externo puede ampliar la descripción física de cada fase. El motor solo usa: fase, especie, apariencia (fem/masc), ropa (E0-E5).
