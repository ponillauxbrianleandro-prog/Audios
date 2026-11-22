# LORE_BOSQUE · EL BOSQUE DE LOS MIL SENDEROS (bloque 8/8)

## CONFIG_LORE FINAL
```
LORE = El Bosque de los Mil Senderos
MONEDA = bellotas
NECESIDADES = on    CONTAMINACION = off    MODULO_EXTERNO = off    NIVEL_MAX = 30

TERRITORIOS = [El Bosque Hondo, El Pantano del Extremo Sur, Ciudad Esperanza, Los Campos, Las Selvas del Comercio, El Territorio Alfa, Las Montañas del Norte]
UBICACIONES = 60 (con 39 cuadras y 78 edificios)

REPARTO = {
  edades_permitidas: [niño, adulto], apariencia_adultos: femenina, apariencia_niños: masculina,
  excepciones: [{T14 alfa: masculina}], grupos_separados: [[adultos, niños]], sin_muerte: true }

CRIATURAS = { temas_activos: [T1 animales, T14 alfa],
  fases_activas: {T1 animales: [1, 2, 3], T14 alfa: [1, 2, 3]},
  modificadores_apagados: [Infernal, Demoníaca, Celestial, Zombi, Robótica, Alienígena], fases_ausentes: todas las demás }

NPC = { incluidos: 193 adultos + 75 niños, agregados: [] }
COMPANEROS = 32 (nombre de una sola palabra)
RESPAWNEABLES = 64 plantillas con facción o grupo
MISIONES = { principales: 15, secundarias_base: 45, de_jefe: 5, propias_de_npc: 703 }
JEFES = [Reina Mantis, Madre del Fango, Matriarca de las Avispas, Soberana de las Selvas, Gran Loba del Norte]
ARRANQUE = { protagonista: Lucas (niño), ubicación_inicial: Claro del Roble Partido, misión_inicial: MP-01 }
```
