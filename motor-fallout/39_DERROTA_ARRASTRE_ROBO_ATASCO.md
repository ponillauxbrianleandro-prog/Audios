# 39 · DERROTA, ARRASTRE, ROBO Y ATASCO (sin contenido sexual)

## NO SE MUERE (tal cual)
(Los menores nunca mueren ni participan en contenido sexual, romántico o de desnudez: ver bloque 50. Los pasos estrechos y el atasco se detallan en el 49; las cuadras en el 47.)
El protagonista **no muere**. Con PV 0 queda **Derrotado** y la partida continúa por este bloque. (El 06 menciona "Muerte permanente": en esta campaña está desactivada.) Los compañeros tampoco mueren: quedan Incapacitados hasta descansar.

## SECUENCIA DE DERROTA (tal cual)
1. **Derrotado:** el combate termina. Los enemigos no se van: quedan en su posición con su PV actual (persistencia, 37).
2. **Robo en el lugar (tirada):** 60% de que los enemigos humanos o ladrones te roben; 25% con criaturas que roban (duendes, ardillas ladronas); 0% con bestias que no manipulan objetos. Qué se roba: 10-30% de las monedas + 0-2 recursos o consumibles al azar (no equipo equipado, no objetos de misión, no el dispositivo de muñeca). Se guarda en la ficha del ladrón: `botín_robado[]`.
3. **Arrastre:** animación de tu personaje arrastrándose hasta la **cama más cercana** (hogar, posada, enfermería, refugio: lista de camas en el mapa 43). Duración 20-120 min según distancia.
4. **Robo en el camino:** por cada 30 min de arrastre, tirada 20% de que alguien (criatura/humano de la zona) te robe un poco: 5-10% monedas o 1 recurso. Solo el 25% de las veces el ladrón es un enemigo nuevo; el resto reutiliza uno persistente de la zona.
5. **Despertar:** en la cama, con 25% de PV, tiempo avanzado, estados Herido y Cansado 2 h. Sin penalización permanente.

## RECUPERAR LO ROBADO (tal cual)
Lo robado está en el ladrón (`botín_robado`). Si **volvés a la zona** y lo derrotás, recuperás todo, con +10% de bonus de XP. Si otra criatura lo mata, el botín queda en su cuerpo (contenedor). No hay límite de tiempo para recuperarlo. Si el ladrón es un NPC humano con nombre, puede venderte de vuelta (50%).
El estado `Derrotado` se registra: `contador_derrotas +1`.

## VULNERABILIDAD MIENTRAS TE ARRASTRÁS (tal cual)
Estás vulnerable: no podés usar el mapa de papel ni objetos salvo vendas. Si aparece un encuentro, solo ves Escapar o Pasar.

## ATASCO EN ESTRUCTURAS (tal cual)
Cuando usás una vía no estándar (ventana, hueco, agujero, conducto) para entrar o salir de un lugar:
- Tirada de **atasco: porcentaje aleatorio entre 40% y 60%** (tirás 1d21+39 para fijar el %, luego 1d100).
- **Pasa limpio:** sin consecuencia.
- **Atascado:** quedás inmovilizado; cada hora hay 30% de que una criatura o humano te encuentre (vulnerabilidad máxima) y te robe monedas o recursos (5-15%). Escapás con una tirada de FUE o AGI (40% + stat×4), cada 10 min; después de 1 hora, siempre salís.
- Tipos de atasco: ventana, agujero, tubería, reja rota, derrumbe, hueco entre rocas.
- Las salidas por **puerta** o conexión normal no tienen atasco.
- Está disponible desde el hogar como "Salir por la ventana" (útil si hay enemigos adentro).

## ATAQUE AL HOGAR (tal cual)
El hogar (L-001) es **ubicación segura** (3% de encuentro) pero **puede ser atacado**: cada noche 6% de que un grupo del tema activo asalte la casa (nivel del grupo según 27). Respuestas: pelear, salir por la ventana (atasco) o escapar por la puerta trasera. Si perdés: Derrotado en tu propia cama (sin arrastre), robo de recursos solo de lo almacenado en el baúl (no se pierde equipo ni lo equipado).

## SISTEMA DE ROBO POR MAPA ABIERTO (tal cual)
Abrir el mapa grande te deja vulnerable (07). Probabilidad de robo/ataque de oportunidad al abrirlo: 8% en seguras, 18% en normales, 35% en hostiles. **Si hacés viaje rápido: +20%** (los porcentajes anteriores se suman). Si se activa: aparece el encuentro de la zona con ventaja para el enemigo (el jugador pierde las 3 primeras acciones del primer turno).
El mapa **pequeño de muñeca** no genera vulnerabilidad.

## REGISTRO
`LOG: d4 12:10 | derrota en L-014 | robo -22 monedas, 1 recurso → ladrón ENE-031 | arrastre a L-007 (cama)`
`FLAGS: robos_pendientes=[ENE-031]`
Cuando recuperás: `robos_pendientes` se vacía y se agrega `robos_recuperados +1`.

## ESTADÍSTICAS ASOCIADAS (se muestran en 38)
Derrotas, robos sufridos, objetos recuperados, atascos, monedas perdidas y recuperadas.

## GANCHO NEUTRO (17)
`[PUNTO_DERROTA]` se dispara en el paso 2 si el módulo externo está activo; si está apagado, se resuelve con las reglas de este bloque.
