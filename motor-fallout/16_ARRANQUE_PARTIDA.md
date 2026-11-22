# 16 · ARRANQUE DE PARTIDA

## MUNDO CARGADO: «EL SALAR» (42-45)
Si se usa la campaña incluida: protagonista Nico «Chispa» Cardal, hogar El Faro Seco (L-001), misión inicial M-01, compañero inicial Rastro (41), mapa de 21 ubicaciones (43). Solo hay que completar `NOMBRE/APARIENCIA` físicos (el autor, con su módulo) y la configuración.

## INSTRUCCIÓN INICIAL (la IA ejecuta esto al empezar)
1. Cargar lore (14, con CONFIG_LORE del 34), reglas (01-13, 18, 24-34) y formato (15). Cargar bestiarios de los temas activos (19-23, 35, 36).
1b. Tirar 1d3 por criatura y fase para el número de variantes (27) o cargar el bestiario generado; calcular enemigos disponibles al nivel 1 (pool inicial T1).
2. Si el jugador pegó un CÓDIGO DE GUARDADO (02), cargarlo y continuar. Si no, crear partida nueva con los datos de abajo.
3. Generar la ubicación inicial (ficha completa con ID L-001), su escena, elementos, contenedores y NPC.
4. Mostrar la pantalla inicial (formato 15) con botones.
5. No preguntar nada más al jugador salvo la configuración inicial.

## CONFIGURACIÓN (completá estos campos antes de empezar)
```
MODO DE DESPLAZAMIENTO: [A / B / C / D / E]  (07)
DIFICULTAD: [Fácil / Normal / Difícil]
IDIOMA/ESTILO: [español rioplatense / neutro]
NECESIDADES: [on / off]
RADIACIÓN/CONTAMINACIÓN: [on / off]
MÓDULO EXTERNO (17): [off / on]
```

## PERSONAJE (fijos, los defino yo; la IA NO los cambia)
```
NOMBRE:
APARIENCIA:
EDAD FICTICIA:
TEMA / ESPECIE / FASE (08, 18):
APARIENCIA CORPORAL (femenina / masculina, solo describe el cuerpo):
HISTORIA PERSONAL (1-3 líneas):
STATS INICIALES (FUE PER RES CAR INT AGI SUE, 1-10 cada una; en El Salar: 6/5/6/5/4/5/4 = 35):
OBJETIVO PERSONAL:
```
Valores variables (nivel, equipo, relaciones, karma, etc.) los gestiona la IA después.

## ESTADO INICIAL POR DEFECTO
- Nivel 1 · XP 0 · PV = 90 + RES×10 + 5 · PA = 60 + AGI×5.
- Hambre 10 · Sed 10 · Fatiga 0 · Rad 0 · Karma 0 · Chapas 50.
- Equipo inicial: ropa básica, arma básica del lore con munición mínima, dispositivo de muñeca, mapa de papel (parcial: solo ubicación inicial y 2-3 vecinas detectadas), 1-2 consumibles.
- Ubicación inicial: del lore (por defecto, zona segura).
- Mapa conocido: ubicación inicial descubierta + 2-3 conexiones visibles (detectadas).
- Misión inicial (opcional): una principal y una secundaria disponibles.
- Hora de inicio: día 1, 08:00.

## PRIMER TURNO
Generar escena, mostrar encabezado, narración breve (3-4 líneas) y botones iniciales. Registrar en LOG: `d1 08:00 | L-001 | inicio de partida`.

## COMANDOS RÁPIDOS DEL JUGADOR (siempre reconocidos)
`GUARDAR` · `CARGAR` (con código pegado) · `ESTADO` · `INVENTARIO` · `MAPA` · `MISIONES` · `AYUDA` (lista botones) · `RESUMEN` (resumen de los últimos 10 turnos).

## SI LA PARTIDA SE VUELVE INESTABLE
Si la IA detecta que olvidó datos: emitir CÓDIGO DE GUARDADO inmediato, pedir al jugador que lo conserve, y continuar solo con lo registrado.
