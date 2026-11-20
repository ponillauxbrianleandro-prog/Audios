# 07 · MAPA, UBICACIONES Y DESPLAZAMIENTO

## ESTRUCTURA
Mundo = red finita de nodos (ubicaciones L-xxx) y conexiones (rutas). El jugador siempre está en una ubicación. Red irregular: ramas, desvíos, bucles, terminales, conexiones ocultas/bloqueadas. Nunca lineal ni cuadrícula perfecta.

## CONEXIONES
- Mínimo habitual 2, habitual 2-3, máximo habitual 4. Más solo si la geografía lo justifica (ciudad, cruce). Terminales: 1. Aisladas: 0 hasta cumplir requisito.
- Solo se conectan lugares con geografía coherente.
- Mostrar todas las rutas **conocidas y accesibles** desde la ubicación actual (tope 4 salvo geografía especial). Las 2 más cercanas son el mínimo visible.
- Estado de conexión: `libre | oculta | bloqueada(causa, req, cumplido)`. Causas: puerta cerrada, derrumbe, inundación, llave, mecanismo, amenaza, misión (excepcional), organización.
- Una conexión desbloqueada no se vuelve a bloquear salvo evento justificado.

## ESTADOS DE UBICACIÓN
`desconocida` (existe, no sabes) → `detectada` (indicios) → `descubierta` (en el mapa) → `accesible` (puedes ir). Descubierta ≠ accesible. Registrar requisito de acceso: objeto / exploración / ambiental / misión / interacción.

## CLASES DE UBICACIÓN
- **Normal:** exploración general.
- **Hostil:** amenaza permanente. Al abandonarla se inicia contador; **> 48 h de juego** → regenera población nueva compatible (nueva configuración, no copia). Jefes/únicos con regla propia.
- **Segura:** descanso, comercio, relaciones; encuentros hostiles 3%.
Espacios: interior / exterior / especial. Cada ubicación tiene 4-6 palabras clave que guían la generación (ej. "residencial, abandonado, destruido, exploración").

## GENERAR NUEVA UBICACIÓN (al descubrirla)
Ficha: `L-id | nombre propio (lore+función+geografía, permanente) | región | bioma | clase | espacio | palabras clave | descripción | conexiones | accesibilidad | ambiente | habitantes posibles | recursos posibles | historial`.
No duplicar. No crear nada por búsquedas sin resultado. Debe engancharse a la red existente con conexiones coherentes.

## REGIONES Y BIOMAS
Una región = un bioma predominante, con variaciones locales. Los encuentros, recursos y criaturas siguen al bioma (08 + lore).

## DOS MAPAS
- **📟 Dispositivo de muñeca:** solo informa (ubicación actual, descubiertas, visitadas, regiones, caminos registrados, marcadores, estado de misiones). No selecciona destino ni viaja.
- **🗺 Mapa de papel:** herramienta de navegación. Permite seleccionar destinos, elegir rutas, marcar dirección, ver sectores, viaje rápido. No muestra desconocidas; regiones sin explorar solo con geografía parcial.
No mostrar nunca información que el personaje desconoce.

## VULNERABILIDAD AL ABRIR EL MAPA DE PAPEL
Abrir el mapa **no detiene el mundo**. Cada vez que se abre:
- Tirada de interrupción: riesgo = 5% (segura) / 12% (normal) / 25% (hostil). +10% noche. −5% si sigilo.
- Si ocurre: encuentro, aproximación enemiga, cambio ambiental o evento (según zona).
- Si hay enemigos cercanos que no te detectaron: 30% de que te detecten por la distracción.
La tirada se resuelve al abrir el mapa; si hay interrupción, ocurre antes de que el jugador elija destino.

## DESPLAZAMIENTO NORMAL (a ubicación conectada)
1. Validar accesibilidad y ruta. 2. Tiempo = distancia × 20-60 min (según terreno, carga, estado). 3. Tirada de eventos en ruta. 4. Actualizar necesidades/clima. 5. ¿Llega o se interrumpe? 6. Actualizar ubicación y generar/recuperar escena. 7. Narrar.
Eventos en ruta (independientes): encuentro (según bioma, 10-30%), descubrimiento menor (10%), obstáculo (5-10%).

## VIAJE RÁPIDO
Solo a ubicaciones descubiertas con ruta válida. Nunca a desconocidas.
Tirada de resultado (suma 100, ajustar por peligro y distancia):
| Resultado | Base |
|---|---|
| Llegada normal | 55 |
| Llegada con retraso (+25-50% tiempo) | 15 |
| Encuentro en el trayecto | 18 |
| Desvío a otra ubicación conectada | 5 |
| Interrupción temporal (condición/clima) | 5 |
| Imposible completar | 2 |
Distancia larga: −10 normal, +10 encuentro. Zona hostil: −15 normal, +10 encuentro, +5 retraso. Ruta segura conocida: +15 normal.
Si el encuentro ocurre: el jugador queda en una ubicación intermedia (nodo "tramo" sin nombre permanente o la más cercana).

## BÚSQUEDA DE NUEVAS UBICACIONES
Ver 04 (categorías F y G). Una búsqueda puede revelar una conexión oculta o detectar una ubicación; no todas lo hacen.

## MODOS DE DESPLAZAMIENTO (elegido en 16)
- **A · Botones (Insect Prison):** destino = botón de ruta; todo automático. Por defecto.
- **B · Botones + Mapa:** A + mapa de papel y viaje rápido con vulnerabilidad.
- **C · Mapa mundial (Fallout 1/2):** el jugador marca un punto del mapa (visible o no); el personaje camina por tramos; cada tramo tira encuentros del bioma cruzado; puede detenerse en puntos de interés; ubicaciones nuevas se encuentran al pasar por terreno desconocido. Hasta llegar, el punto avanza por "pasos" de 1-4 h.
- **D · Mapa-escena (Town of Magic):** el jugador solo se mueve abriendo el mapa. Cada llegada = escena con fondo, NPC clickeables (botón por NPC), evento aleatorio previo a la acción. Desbloqueo de ubicaciones por misiones. Mapa acotado.
- **E · Refugio (Fallout Shelter):** hay una base segura central con botones de gestión (descanso, cocina, taller, almacén). Las salidas son expediciones a ubicaciones con tiempo de ida y vuelta.
Todos usan las mismas reglas de escena, búsqueda y combate. El modo cambia solo cómo se elige a dónde ir.

## PERSISTENCIA
Guardar siempre: descubiertas, visitadas, desconocidas registradas, rutas descubiertas/bloqueadas/desbloqueadas/ocultas, cambios geográficos, estado de cada ubicación, habitantes conocidos, recursos agotados, eventos completados.
