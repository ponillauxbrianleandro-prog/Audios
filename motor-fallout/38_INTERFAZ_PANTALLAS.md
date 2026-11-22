# 38 · INTERFAZ DE PANTALLAS (todo con botones)

## PRINCIPIO (tal cual)
La IA siempre presenta **una pantalla** con elementos fijos y **botones con ícono + etiqueta**. Cada botón tiene una **acción única**. La IA elige un botón y el motor resuelve todo (cinemática corta + efectos). Si la plataforma muestra imágenes, el fondo es la escena del lugar; si no, se describe en 1-2 líneas. Los botones se numeran para elegir por número.
Se muestran SOLO los botones válidos (03). Las pantallas de abajo definen **dónde va cada cosa**.

## ELEMENTOS FIJOS DE CUALQUIER PANTALLA
| Posición | Elemento |
|---|---|
| Arriba al centro | Nombre del día (Lunes…Domingo) con una barra de 10 segmentos = momento del día (cada segmento consumido es avance de tiempo) |
| Arriba a la derecha | Botón **Mapa** (ícono de pergamino con brújula) y, más abajo, botón **Menú** (☰) |
| Abajo a la izquierda | **Carta del personaje**: retrato, nombre y dos barras verticales: **PV** (cruz) y **Aguante** (corazón: ánimo y energía) |
| Centro y bordes | Botones de acción del lugar, colocados sobre el elemento al que se refieren (cama = Dormir, mesa = Beber té) |

## PANTALLA 1 · INTERIOR (ejemplo: dormitorio del hogar)
Fondo: cuarto con ventanas, sofá, mesa baja con té, cama.
| Botón | Aparece si | Acción |
|---|---|---|
| Recordar | siempre en el hogar | Abre el diario: resumen de escenas, notas y misiones |
| Tomar té | hay té | Aguante +10, sed −10, 10 min |
| Dormir | hay cama y no hay enemigos | Descansa 1/4/8 h (11) |
| Salir | hay salida | Abre la salida; si hay ventana: “Salir por la ventana” (atasco 40-60%, 39) |
Más botones según el lugar: Examinar ventana, Registrar mueble, Abrir cajón, Buscar.

## PANTALLA 2 · INTERIOR CON TRES FUNCIONES (cocina del hogar)
| Botón | Aparece si | Acción |
|---|---|---|
| Al dormitorio | conexión interna | Cambia de sector (no es viaje) |
| Banco de trabajo | hay taller | Abre fabricación, mejora y reparación (46) |
| Comer | hay comida | Consume hambre −30 |
| Salir | siempre | Sale a la ubicación exterior |

## PANTALLA 3 · EXTERIOR (ejemplo: bosque/camino)
| Botón | Aparece si | Acción |
|---|---|---|
| Explorar (lupa) | siempre en exterior | BUSCAR general (04): hallar objetos, rastros, conexiones, enemigos |
| Ir a [destino] (flechas ▲ ◀ ▶) | ruta conocida | Viaja a esa ubicación conectada |
| Registrar [punto] | punto de interés visible | Abre ese contenedor/mueble |
| Mapa | siempre | Abre el mapa grande (vulnerable) |
Cada botón de ruta lleva la **flecha en la dirección de la ruta** (izquierda, derecha, arriba) y el nombre del destino. “BUSCAR” es **solo para buscar en general**; registrar puntos concretos usa sus propios botones (04).

## PANTALLA 4 · COMBATE (ver 37)
Arriba: `Turno N` y `Acciones: 3`. Izquierda: personaje de cuerpo entero, con **3 círculos de acción** debajo (● ● ●). Centro y derecha: **cartas de enemigos** en tres alturas = tres distancias: **LEJOS** (arriba, al fondo), **MEDIA** (centro) y **CORTA** (abajo, frente al jugador). Cada carta lleva: imagen, nombre, barra de PV, ícono de ataque (tachado si no puede atacar) y estados. Abajo: carta del personaje y botón **Repetir último**.
Un enemigo marcado (borde de color) es el objetivo actual.

## PANTALLA 5 · ELEGIR ACCIÓN SOBRE UN ENEMIGO (tocar su carta)
Ventana con botones: **Cancelar · Golpe normal · Defensa · Empujar · Golpe potente · Golpe preciso**. Con arma de distancia: Disparo normal, Disparo potente, Disparo preciso, Defensa, Empujar, Recargar. Otros botones aparecen con stats altos o por arma (barrido, golpe múltiple). Si el enemigo está en MEDIA o LEJOS, los golpes cuerpo a cuerpo se reemplazan por **Acercarse**.

## PANTALLA 6 · ACCIONES SOBRE VOS (tocar tu carta, en combate)
Ventana con botones: **Cancelar · Pasar · Escapar · Rendirse · Vendas ×N** (más consumibles equipados, Cambiar arma). Los íconos: reloj de arena (Pasar), corredor (Escapar), bandera (Rendirse), rollo de vendas con cantidad.

## PANTALLA 7 · ACCIONES SOBRE VOS FUERA DE COMBATE (tocar tu carta)
Ventana con botones: **Volver · Estado · Información · Inventario · Equipo**. Debajo una barra con la moneda: `0 cuñas`. Desde acá se abre cada ficha.

## PANTALLA 8 · ESTADO (primera página)
Retrato de cuerpo entero y lista:
| Estadística | Qué significa |
|---|---|
| Salud (%) | PV actuales sobre PV máximos (11, 27) |
| Aguante (%) | energía y ánimo: baja con fatiga, sube al descansar |
| Daño | daño promedio de tu arma + FUE + 1.3×nivel (27) |
| Defensa (%) | 2 × RD de la armadura (06) |
| Días | días pasados y día de la semana |
| Botón Siguiente | página 2 |

## PANTALLA 9 · ESTADÍSTICAS (segunda página)
| Estadística | Qué significa |
|---|---|
| Nivel y XP | nivel actual y XP para el siguiente (27) |
| Derrotas | veces que quedaste Derrotado (39) |
| Robos sufridos | veces que te robaron |
| Objetos recuperados | veces que recuperaste lo robado |
| Enemigos derrotados | total, por especie |
| Ubicaciones | descubiertas / visitadas |
| Reputación | por facción (12) |
Se omiten estadísticas de contenido adulto; el módulo externo puede agregar las suyas.

## PANTALLA 10 · ESTADÍSTICAS DE COMBATE (borde estilo ventana, con descripción de cada una)
Inspirada en el combate por turnos de ese tipo de juegos; aquí **no sexuales**:
| Atributo | Descripción (tal cual) |
|---|---|
| Salud 53/53 | PV: llegar a 0 es Derrotado (no hay muerte, 39) |
| Aguante 25/25 | energía para movimientos potentes; baja con golpes potentes y esfuerzo |
| Fuerza | bonus de daño cuerpo a cuerpo, carga y forzar |
| Percepción | detección, puntería y búsqueda |
| Resistencia | PV y resistencia a estados |
| Carisma / Presencia | precio de comercio y probabilidad de que un enemigo dude (+x% de fallo enemigo) |
| Inteligencia | hackeo, reparación y fabricación |
| Agilidad | iniciativa, sigilo y escape |
| Suerte | críticos y rareza del botín |
Pestañas: **Atributos | Relaciones** (lealtad de compañeros y relación con NPC). Panel derecho: **Hechizos/Objetos** → aquí **Armas/Objetos** (cuadrícula 3×4). Botones de equipo: anillo y colgante → **Accesorios** (3 espacios). Botones laterales: **Equipo, Habilidades (no existen aquí: se omite), Alquimia → Fabricar, Misiones**. Abajo: **Esperar, Escapar**. Arriba a la derecha: **Nivel, moneda y hora**.

## PANTALLA 11 · MAPA GRANDE (de papel)
Fondo: silueta del Salar con relieve. Cada **ubicación descubierta** es un **botón** con su nombre; las **detectadas** llevan un “?” amarillo; las **no descubiertas** no aparecen. Botón ✖ arriba a la derecha.
- Tocar una ubicación = **viaje rápido** (07, 39): riesgo de emboscada o robo mientras el mapa está abierto: 8/18/35% según zona **+20% si viajás**.
- Abrir el mapa **te deja vulnerable en todo momento** (el motor tira el riesgo al abrirlo).
- Las ubicaciones bloqueadas aparecen atenuadas.

## PANTALLA 12 · MAPA PEQUEÑO DE MUÑECA (Brazalete del Faro)
No se puede apretar nada salvo **marcar una ubicación cercana** para ir ahí. **No hay viaje rápido** y **no genera vulnerabilidad**.
- **Interior:** plano de las habitaciones del lugar con un punto en tu sector y marcas en puertas y salidas. Marcar una salida → “Ir hacia la salida”.
- **Exterior:** círculo con tu ubicación en el centro y las ubicaciones conectadas alrededor, con la dirección de cada ruta. Marcar una → “Ir a [destino]” (viaja por botones, tramo a tramo).
- Muestra solo lo que el personaje conoce (07).

## PANTALLA 13 · INVENTARIO Y EQUIPO
Cinco pestañas: Consumibles · Equipo · Armas · Objetos · Recursos; moneda y carga (peso/máx). Botones por objeto: Examinar, Usar, Equipar, Soltar, Entregar. Equipo: casillas Cabeza, Torso, Piernas, Pies, Arma 1, Arma 2, Accesorios ×3.

## PANTALLA 14 · COMERCIO, DIÁLOGO Y MISIONES
- **Comercio:** dos columnas (tu inventario / stock del comerciante), botones Comprar, Vender, Negociar, Cerrar; precios según 09.
- **Diálogo:** retrato del NPC, texto breve y 3-5 botones de respuesta; botones fijos: Preguntar, Negociar, Pedir ayuda, Despedirse.
- **Misiones:** lista Activas/Completadas con el paso actual.

## PANTALLA 15 · DERROTA Y ARRASTRE (39)
Pantalla oscura con texto: “Quedás Derrotado”. Animación: el personaje se arrastra hacia la cama más cercana. Si hay robo: mensaje del ladrón y cuánto se llevó. Botón **Continuar**.

## NOTA SOBRE LAS IMÁGENES
Los íconos (lupa, flechas, cama, té, mapa, menú, escudo, bandera, corredor) son referencias; la plataforma puede usar los suyos. El módulo externo puede reemplazar retratos y fondos.
