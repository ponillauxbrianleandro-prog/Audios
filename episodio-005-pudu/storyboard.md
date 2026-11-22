# Storyboard — Episodio 005: Pudú

Imagen 100 % generada por código (motor 2.5D por relieve de `render/`, sin modelos de imagen ni fotos). Vertical 720×1280, 25 fps. Cada toma está en `render/episodio.py` (`build_shots`); sus tiempos salen de la narración (`audio/escenas.json` y `tomas.py`).

Animales: pudú (`render/cervido.py`, `PUDU`) y ciervo colorado de apertura (`CIERVO`), mismo constructor de cérvido con anatomía propia (patas de dos tramos con rodilla/corvejón, orejas grandes con giro, cuernos simples o ramificados) y el pelaje procedural de `fur.py`. Bioma `selva_andina` (`biomes.py`): coihues con musgo, nalcas, colihue, helechos, troncos y rocas musgosas, suelo de musgo, bruma y llovizna.

## Las cinco capas (todas las tomas)
1. **Pegada a cámara**: hojas desenfocadas que reciben una gota, se doblan, la sueltan y rebotan (`fx_andina.hoja_con_gota`).
2. **Delante del animal, un poco más lejos**: nalcas, helechos y colihue de la lista `fg` de cada toma (parcialmente tapándolo).
3. **Alrededor**: vegetación del bioma a los lados, que se mece con el viento.
4. **Detrás**: troncos de coihue, nalcas, colihue y rocas.
5. **Fondo**: bosque en bruma, cordillera lejana y rayos de sol (`fx_andina.rayos`).
Más goteo con ondas y salpicaduras en el suelo (`fx_andina.goteo`) y llovizna fina del motor.

| Toma | Escena | Qué pasa |
|---|---|---|
| s01a, s01b | 1 Familiar | Ciervo colorado de cuernos enormes en un claro; primer plano de cuernos y mirada |
| s02a–c | 2 Presentación | El ciervo gira; el pudú asoma sacudiéndose el agua; tres cuartos; bajo con hoja cruzando |
| s03a–c | 3 Comida | Brote tierno a ras de suelo, plano elevado, general lateral; cabeza que sube a mirar entre bocados |
| s04a–b | 4 Cuernitos | Primer plano de las púas; se rasca contra el tronco |
| s05a–b | 5 Escondite | Quieto con las orejas girando; sale disparado entre helechos con seguimiento |
| s06a–b | 6 Soledad | Cruza un claro en bruma con rayos; contrapicado desde el helecho |
| s07a–b | 7 Lo chiquito | Ojo y oreja; retroceso junto a un tronco para ver la escala |
| s08a–b | 8 Refutación | Mira desde debajo de una nalca mientras pasa el ciervo; luz cálida de tarde |
| s09a–b | 9 Cierre | General con rayos; mira a cámara y vuelve al sotobosque |

## Control de calidad (sección 30 del documento maestro)
Ver el reporte en la respuesta final.
