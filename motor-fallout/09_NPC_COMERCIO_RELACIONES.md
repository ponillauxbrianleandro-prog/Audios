# 09 · NPC, RELACIONES, COMERCIO Y DELITOS

## FICHA NPC
`N-007 | nombre | cat/especie | personalidad (3 palabras) | rol (comerciante/guardia/habitante/...) | estado | ubic | agenda (dónde está según hora) | rel{} | inv[] | stock[] | secretos | historial[]`
Agenda: los NPC se mueven según hora (trabajo, comida, sueño). Si no está, registrar última posición.

## RELACIONES (rango −100 a +100, se guardan por NPC)
Variables: Confianza, Amistad, Respeto, Afinidad, Reputación (local), Hostilidad, Desconfianza, Cooperación.
Reglas:
- Un NPC NO se vuelve amigo solo por hablar varias veces. Cada ganancia depende de personalidad, intereses e historia.
- Máx. +5 por conversación normal; favores, regalos adecuados y misiones dan más.
- Primera impresión según Reputación de facción y Karma.
- Decaen lentamente sin contacto (−1 cada 7 días si > 50).
- Umbrales: ≤ −50 hostil · −49..−10 desconfiado · −9..+9 neutral · +10..+49 amistoso · ≥ +50 aliado.
- Efectos: precios, información disponible, misiones, ayuda en combate, acceso.

## CONVERSACIÓN
Botones de diálogo: opciones generadas por contexto (3-5). Temas: lugares, personas, hechos, rumores, misiones, comercio. Chequeo social con CAR: `%éxito = 30 + CAR×5 + Habla/2 + bonus_rel − dificultad`. Cada NPC guarda qué le dijiste para no repetir ni contradecir.

## COMERCIO
Aparece si NPC es comerciante y relación ≥ neutral.
- **Precio de compra** = valor × (1.4 − CAR×0.02 − bonus_rel/500), mínimo valor×0.8.
- **Precio de venta** = valor × (0.4 + CAR×0.02 + bonus_rel/500), máximo valor×0.7.
- Estado/durabilidad modifican valor (roto ×0.3).
- Stock del comerciante persiste. Lo que vendes queda en su stock. Reposición cada 72 h con tirada y según lore (+/−20% variación de stock).
- Chapas del comerciante limitadas (`caja`); si no alcanza, ofrecer trueque.
- Botones: Ver mercancía, Comprar, Vender, Intercambiar, Consultar precios/existencias, Negociar (tirada CAR; éxito −10% precio; fallo −5 afinidad).

## DELITOS Y TESTIGOS (acciones no autorizadas)
Acciones: robar, abrir contenedor ajeno, entrar a propiedad privada/zona restringida, manipular pertenencias, atacar.
Tirada de detección por cada NPC con línea de visión:
`%detectado = 30 + visibilidad(0-30) + seguridad_lugar(0-20) + tiempo_empleado/2 − sigilo(AGI×3 + hab. Sigilo/2) − oscuridad(10)`.
Sin testigos, no hay detección (pero queda rastro: contenedor forzado/robado).
Consecuencias (escalonadas): advertencia → reclamo → pérdida de confianza → expulsión → restricción de acceso → hostilidad/guardias → recompensa. Reputación de facción cae. Registrar en LOG y en FLAGS.
Si el NPC es aliado y la acción es menor: puede perdonarse con tirada CAR.

## COMPAÑEROS
Reclutables si rel ≥ +40 y afinidad con tu karma. Máx. 2. Tienen ficha propia, inventario, PV, IA de combate, comentarios. Pueden abandonarte por conductas contra sus valores. Seguir/Esperar/Alejarse/Proteger botones.

## INTERACCIONES FÍSICAS NO SOCIALES
Seguir, pedir que acompañe, esperar, alejarse, ayudar, proteger, pedir protección, cooperar, intercambiar. Respetar voluntad, capacidad y personalidad del NPC. Si el NPC se niega, debe tener razón registrada.

## MUERTE DE NPC
Marcar muerto. Su inventario pasa a cadáver (contenedor). Misiones vinculadas se actualizan. Familiares/facción pueden reaccionar según lore.
