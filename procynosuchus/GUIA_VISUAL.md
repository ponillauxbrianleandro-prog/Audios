# Guía visual del canal

Cuatro lenguajes, cada uno con una función. No se mezclan al azar: cada cambio de estilo responde a lo que se está contando.

| | Estilo | Se usa para | Frecuencia | Se genera con |
|---|---|---|---|---|
| 1 | Retrato en cuadro | Científicos fallecidos, frases célebres, hitos históricos | Escaso | `retrato.py` |
| 2 | Libreta a lápiz | Presentar al animal, anatomía, otros animales, científicos vivos, hallazgos | Medio | `libreta.py` |
| 3 | Personajes gráficos | Personas, comportamientos, comparaciones, muchos individuos, edits rápidos | Alto en explicaciones | `src/Personajes.tsx` |
| 4 | Óleo documental | El animal, su ecosistema, paisajes | El principal | `particulas.py` |

Orden habitual: intro con fechas y lugares (3) → presentación del animal (2) → documental (4) → explicaciones intercaladas (3 y 2) → retrato cuando habla un científico histórico (1).

Lo que los une: la paleta base (noche azul-verdosa, turquesa, malva, ocre, crema), el fondo oscuro azulado de las láminas y la misma tipografía.

## Estilo 4 — óleo documental por partículas

- Nada se dibuja como forma geométrica. Árbol, planta, roca, nube y animal son acumulaciones de manchas.
- La mancha es redondeada y orgánica. No hay trazos rectangulares, largos ni en punta.
- Cada mancha varía en tamaño, tono y orientación; no hay cuadrículas ni repetición visible.
- El volumen sale de la luz por mancha: arriba a la izquierda claro, abajo a la derecha oscuro.
- Tres planos separados por bruma: lejos chico, frío y de poco contraste; cerca grande y saturado.
- El cielo es un degradé limpio, sin textura. Solo las nubes y la luna se pintan, con manchas redondas sobre una base de sombra.
- Plantas especiales: pocas por escena. Su color se derrama alrededor en manchas cada vez más chicas y transparentes. Sin contorno luminoso.
- El animal conserva su anatomía (`animal.py`); solo su superficie está hecha de manchas, más chicas en la cabeza.
- Árbol: esqueleto de ramas hecho de manchas oscuras, hojas en racimos e hilos colgantes en las puntas.

## Estilo 1 — retrato en cuadro

- Figura repintada al óleo sobre una fotografía de dominio público; cara más trabajada que ropa y fondo.
- Composición de retrato clásico de la India: ventana con arco lobulado, fondo plano de color profundo, cenefa con hojas de Glossopteris y huesos, cartela con nombre y fechas.
- No se anima: solo movimiento lento de cámara sobre el cuadro, con la cita al costado.

## Estilo 2 — libreta a lápiz

- Papel de cuaderno de campo con fibra, manchas y renglones tenues.
- Contorno repasado con pulso, sombreado por tramado en varias direcciones, grano de papel.
- Anotaciones breves junto al dibujo. Los científicos vivos se dibujan acá, no en cuadro.
- Para un científico vivo concreto hace falta una foto elegida por el canal; la figura de la lámina es genérica.

## Estilo 3 — personajes gráficos

- Figura de señal de tránsito: cabeza redonda separada, torso compacto, brazos y piernas gruesos. No es un muñeco de palitos.
- Una sola figura articulada; cada pose son ángulos en `POSES`. Agregar una pose es agregar una línea.
- Colores vivos y planos. Soportes: rombo amarillo, círculo rojo, semáforo peatonal, placa de texto.
- Animales y plantas en el mismo lenguaje: silueta negra.

## Datos verificados del animal

*Procynosuchus delaharpeae*, cinodonto del Pérmico tardío (≈ 255 millones de años).

Fósiles documentados:
- **Sudáfrica** — cuenca del Karoo, donde es más abundante.
- **Zambia** — valle del Luangwa; de ahí sale el esqueleto casi completo estudiado por Kemp.
- **Tanzania** — cuenca del Ruhuhu; ejemplar hallado en 2007 cerca del monte Kingori.
- **Alemania** — fisura de Korbach.

No hay registro en Rusia, América del Norte ni Sudamérica. Argentina se muestra unida a África en Pangea, sin fósiles hallados, como pregunta abierta. La falta de fósiles en una región no prueba que el animal no haya vivido ahí: depende de que existan rocas de la edad justa y de cuánto se haya excavado.
