# 08 · CRIATURAS Y PERSONAJES — ESCALA DE 14 FASES

## NOMBRE BASE Y TEMA
Todo ser vivo se llama **CRIATURA**. Lo que cambia es el **TEMA** que la acompaña (bloque 18): *Criaturas animales*, *Criaturas con cuernos y cuerpo robusto*, *Criaturas con halo*, *Criaturas duende*, *Criaturas artificiales*, etc. La escala de 14 fases es **la misma para todos los temas**: al cambiar de tema solo cambia la palabra (donde dice "animal" se lee el tema activo: duende, orco, etc.).
Cada especie base del bestiario (19-23, 35, 36) tiene su propia cadena de fases 1 a 14 (bloque 25). El lore decide qué fases y temas aparecen. Lo marcado (tal cual) no se cambia; lo marcado (genérico) lo completa el lore.

## REGLA DE ADULTEZ (tal cual)
Todo personaje humano o humanoide generado es adulto. No generar menores.

## REGLA DE APARIENCIA FEMENINA/MASCULINA (tal cual)
Cada fase, cada clasificación y cada característica tiene una **versión femenina** y una **versión masculina**. "Femenino" y "masculino" describen únicamente cómo se ve el cuerpo; no significan mujer ni hombre ni fijan sexo biológico ni género. Un personaje puede tener rasgos femeninos y verse masculino o al revés. No se nombran sexos en las fichas: se elige la apariencia por ID de personaje y se mantiene.

## LAS 14 FASES (tal cual)
**Fase 1 · Criatura normal.** El animal (o ser del tema) sin ningún rasgo humano. Cuatro patas o anatomía propia de la especie. No habla. Actúa por instinto. En los tamaños pequeños se usa la versión agrandada (ver 27 y bestiarios).
**Fase 2 · Criatura con cuerpo ligeramente humanoide.** Sigue siendo un animal: mismas patas, sin manos, sin postura erguida. Pero ciertas partes del cuerpo (rostro, torso, hombros, proporciones) recuerdan a las humanas. No habla. (Las precisiones de apariencia se completan con el módulo externo de apariencia.)
**Fase 3 · Criatura pokémica.** Camina sobre dos patas, erguida, y usa sus patas delanteras **como manos** (siguen siendo patas, pero agarran y manipulan). Cuerpo aún claramente animal. Expresiva, pero no se comunica en idioma humano.
**Fase 4 · Criatura de cuerpo humanoide.** Cuerpo humanoide completo: dos patas que funcionan como piernas, dos patas que funcionan como manos, siempre erguida. **Desde esta fase se comunica** (habla o idioma comprensible).
**Fase 5 · Criatura mitad humana (quimera).** Partes del cuerpo de animal y partes de humano en un mismo cuerpo (ejemplo: minotauro y variantes de minotauro). No hay sirenas ni peces. Habla, piensa, vive en sociedad.
**Fase 6 · Humano con anatomía animal.** Ya es un humano, con casi ningún rastro animal general, pero puede conservar patas en la parte inferior o rasgos marcados: pelaje, garras, dientes y otras partes de cualquier animal clasificado. Altura y tamaño absurdos posibles. Manos humanas. Es variable: puede aparecer o no (lo decide el lore).
**Fase 7 · Humano con rasgos animales.** Mucho más humano. Puede tener pelaje, rasgos y características de los animales y una personalidad bien formada. Altura alta pero humana.
**Fase 8 · Humano que se considera animal.** Humano que se identifica como animal: usa prótesis animales mecánicas o accesorios que reemplazan o se unen a partes del cuerpo para no quitárselos nunca, y busca comportarse, actuar y vivir como animal.
**Fase 9 · Furry.** Usa trajes o disfraces completos de animal. Puede considerarse animal o no; el propósito es sentirse un ser peludo, tierno e inocente.
**Fase 10 · Humano con accesorios por identidad.** Usa accesorios o ropa de animales porque forma parte de su personalidad o por disfrute personal. No quiere ser ni sentirse animal, no se deshumaniza. La ropa no es de cuerpo completo; si lo es, deja partes del cuerpo expuestas para que se vea que hay un humano dentro. No es furry (9) ni fase 11.
**Fase 11 · Humano con accesorios por obligación.** Usa accesorios de animal por exigencia de su trabajo, no por personalidad. Se clasifica como trabajador de espectáculo o atención al público (bailarines, animadores, anfitriones y similares), con accesorios de conejo u otros por el estilo. Sin contenido sexual en este bloque.
**Fase 12 · Humano con instintos animales.** Humano que actúa de forma bastante animal, con instintos animales, pero es humano.
**Fase 13 · Humano normal.** Humano completamente normal y funcional. Con personalidad y características propias, sin rasgos animales.
**Fase 14 · Humano que rechaza lo no humano.** Detesta cualquier cosa que no se parezca lo suficiente a un humano: detecta mutaciones y rasgos "poco humanos". Suele ser de clase alta, pero no solo; puede venir de religión, de educación familiar o escolar. Evita todo contacto y actividad con esas criaturas, aunque sean inofensivas o amigables. Impacto: precios, acceso y diálogos con criaturas de fases 1-12.

## USO DE LAS FASES EN EL JUEGO (tal cual)
- Fase 1-3: criaturas sin lenguaje. Se generan como enemigos o fauna (bloque 28).
- Fase 4-5: pueden ser NPC, comerciantes, aliados o enemigos con diálogo.
- Fase 6-14: NPC y enemigos humanos o casi humanos (bloque 26).
- Una fase puede estar ausente del lore. Una especie puede no tener todas las fases.
- Cada entidad guarda: `ID | tema | especie | fase | variante | modificadores | apariencia(femenina/masculina) | amenaza | estado`.

## MODIFICADORES Y VARIANTES
Las variantes universales (demoníaca, zombi, parasitaria, controlada, alienígena, robótica, etc.) están en el bloque 24 y se aplican a cualquier especie en cualquier fase. Máx. 3 modificadores por entidad.

## IDENTIDAD E IDs (tal cual)
Cada entidad tiene ID permanente (N- NPC, ENE- enemigo). 5 criaturas iguales = 5 entidades con estado propio. Nombres de personajes nombrados no cambian. Un NPC muerto se registra como muerto.

## FICHA DE PERSONAJE (tal cual)
`ID | nombre | tema | especie | fase | variante | modificadores | apariencia | edad (adulta) | inteligencia | personalidad | comportamiento | amenaza | estado | bioma origen | ubicación | relaciones | inventario | historial`

## REGLA FINAL
La existencia de una fase o tema no obliga a que aparezca. La generación depende del lore, bioma, ubicación, nivel del jugador (27) y probabilidades (28).
