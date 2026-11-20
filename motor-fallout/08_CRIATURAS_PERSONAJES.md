# 08 · CRIATURAS Y PERSONAJES (clasificación universal)

El lore (bloque 14) tiene prioridad. Las listas son extensibles, no cerradas. Las categorías son una escala de parecido humano, NO de poder o inteligencia.

## CATEGORÍAS
| Cat | Nombre | Descripción corta |
|---|---|---|
| I | Criatura animal | Anatomía animal, sin habla ni postura humana necesarias |
| II | Animal humanoide | Animal con rasgos humanoides (bípedo, manos, expresivo). Especie propia |
| III | Antropomórfico | Anatomía mayormente humanoide con rasgos animales integrados |
| IV | Humano con rasgos animales | Humano con orejas, cola, pelaje localizado, etc. |
| V | Humano con vestimenta animal | Humano normal con disfraz/accesorios |
| VI | Humano normal | Sin rasgos animales |

## CATEGORÍA I — subtipos (según lore)
Mamíferos herbívoros (roedores, lagomorfos, cérvidos, bovinos, équidos, caprinos, ovinos, suiformes) · Carnívoros/cánidos (lobos, zorros, perros salvajes, coyotes, hienas) · Insectos · Arácnidos · Marinos blandos (medusas, pulpos, calamares, babosas) · Parásitos (versiones pequeñas/medianas/gigantes) · Otros (anfibios, reptiles, aves, prehistóricos, ficticios). No peces ni crustáceos por defecto.
Pueden aparecer en tamaños muy superiores al natural.
Variables: tamaño, masa, fuerza, velocidad, agilidad, rastreo, manada, territorialidad, inteligencia, adaptación.

## CATEGORÍA III — variantes
Terrestre: canino, vulpino, lupino, roedor, lagomorfo, bovino, equino, ovino, caprino, insectoide, arácnido. Marino blando: medusoide, octópodo, calamariforme, anemonoide, babosa. Híbridos: centauro, extremidades extra, cola funcional, exoesqueleto, etc. No sirenas/peces por defecto.
Variables anatómicas: cabeza, rostro, orejas, extremidades (tipo/cantidad), cola, pelaje, piel, altura, masa, locomoción.

## MODIFICADORES UNIVERSALES (combinables si son compatibles)
- **Biológicos:** mutado, evolucionado, adaptado, gigante, enano, albino, simbiótico, parásito, regenerativo, bioluminiscente, blindado, cristalizado, gelatinoso, mineralizado, vegetalizado, quimérico, artificial, experimental.
- **Sobrenaturales:** demoníaco, infernal, celestial, espectral, mágico, maldito, elemental, mitológico, divino, arcano, etéreo.
- **Extraterrestres:** exobiológico, alienígena, desconocido.
- **Tecnológicos:** cibernético, robótico, mecánico, sintético, biomecánico.
- **Conductuales:** territorial, social, solitario, gregario, agresivo, defensivo, curioso, inteligente, instintivo, cooperativo, hostil, doméstico, salvaje, neutral.
- **Ambientales:** frío, calor, acuático, subterráneo, volador, arbóreo, desértico, pantanoso, urbano, nocturno, extremo.
Máx. 3-4 modificadores por entidad. Deben ser coherentes con anatomía y lore.

## EFECTO MECÁNICO DE MODIFICADORES (para que afecte al combate)
| Modificador | Efecto |
|---|---|
| Gigante | PV ×1.8, daño ×1.4, velocidad −15% |
| Enano | PV ×0.6, def +10, velocidad +10% |
| Mutado | +1 propiedad rara; PV ×1.2 |
| Blindado | reducción +3, velocidad −10% |
| Regenerativo | +2 PV/ronda |
| Veloz/volador | +10 esquiva |
| Bioluminiscente | visible de noche; −10 sigilo para él |
| Territorial | no persigue fuera de zona |
| Gregario | encuentros más numerosos (+1-2) |
| Inteligente | usa tácticas, puede negociar |
| Espectral | resistencia física 50% |
| Cibernético/robótico | inmune a veneno/sangrado, vulnerable a descarga |
Si el lore define otra cosa, usar el lore.

## GENERACIÓN
Pasos: 1) bioma + tipo de ubicación → 2) filtrar por lore → 3) elegir categoría y especie → 4) nivel de amenaza (progresión) → 5) hasta 3 modificadores → 6) comportamiento → 7) estadísticas (plantilla de nivel) → 8) ID(s) → 9) registrar.
Tabla de nivel de amenaza (según jugador nivel N): Débil N−2 · Normal N · Fuerte N+2 · Élite N+4 · Jefe N+6.

## PLANTILLAS BASE POR NIVEL DE AMENAZA (PV | daño | %base)
| Amenaza | PV | Daño | %Impacto |
|---|---|---|---|
| 1 Débil | 15 + 4×nivel | 3-6 | 45 |
| 2 Normal | 25 + 6×nivel | 5-10 | 55 |
| 3 Fuerte | 40 + 9×nivel | 8-15 | 60 |
| 4 Élite | 70 + 13×nivel | 12-22 | 65 |
| 5 Jefe | 150 + 22×nivel | 15-30 | 70 |

## FICHA DE PERSONAJE
`ID | nombre | categoría | especie | variante | modificadores | apariencia | edad | inteligencia | personalidad | comportamiento | amenaza | estado | bioma origen | ubicación | relaciones | inventario | historial`
No todo se muestra al jugador.

## IDENTIDAD
Cada entidad tiene ID permanente (N- para NPC, ENE- para enemigos). 5 criaturas iguales = 5 entidades. Nombres de personajes nombrados no cambian. Un NPC muerto se registra como muerto.

## TIPOS DE ENTIDAD A GENERAR
Individuos únicos · Grupos · Habitantes · Comerciantes · Salvajes · Hostiles · Neutrales · Especiales · Jefes.

## REGLA FINAL
No inventar especies fuera del lore. Una categoría existente no implica que aparezca. La generación depende del lore, bioma, ubicación, progresión y probabilidades.
