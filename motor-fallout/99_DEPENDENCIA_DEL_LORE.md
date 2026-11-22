# 99 · DEPENDENCIA DEL LORE (qué manda el lore y plantilla CONFIG_LORE final)

## PRINCIPIO (tal cual)
Las **mecánicas** (bloques 01-98) son un catálogo completo de todo lo que puede existir. El **lore** es un texto aparte que **da órdenes** a las mecánicas: elige, descarta, agrega y renombra. **Lo que el lore no menciona, no existe en esa partida.** Lo que el lore agrega se rige por las mecánicas. La IA que juega usa las mecánicas completas **más** el lore, y no necesita otro bloque: sus ajustes los hace al jugar.

## QUÉ MANDA EL LORE (genérico → lo decide el lore)
| Elemento | Qué decide el lore | Catálogo donde está el menú |
|---|---|---|
| Territorios y mapa | cuántos (típicamente 7), posición, formación vegetal, clima, relieve, agua (51) | 51 |
| Ubicaciones y cuadras | cuáles existen, nombre propio permanente, cuántas cuadras, edificios | 47, UBICACIONES_CATALOGO |
| Temas de criaturas | cuáles están activos y cuáles no (18, 52) | 18, 52 |
| Fases de cada tema | cuáles aparecen y cuáles no (por territorio si quiere) | CUADROS 14 FASES |
| Especies | cuáles existen, cuáles se apagan, cuáles se agregan | 19-23, 35, 36 |
| Variantes universales | cuáles se apagan (24) | 24, MATRIZ |
| NPC con nombre | cuáles arquetipos existen, su apariencia y nombre; los niños y compañeros con **un solo nombre** | NPC_CON_NOMBRE, NPC_NINOS, COMPANEROS |
| NPC respawneables | cuáles grupos y facciones; **puede agregar más** | NPC_RESPAWNEABLES |
| Misiones | cuáles de las base y de las asignadas a cada NPC entran; **puede descartar y agregar** | MISIONES_BASE + asignadas |
| Facciones y grupos | cuáles existen, su carácter, si son infantiles o de adultos | lore |
| Objetos | qué armas, municiones, ropas, comidas, medicinas y mejoras existen y cómo se llaman | catálogos de objetos |
| Edad y apariencia | quién es niño o adulto, qué apariencia tiene cada grupo (50) | 50 |
| Moneda, tono, estilo de nombres | todo | lore |
| Reglas locales | modo sin muerte, grupos separados de adultos y niños, restricciones de género | 50 |

## QUÉ NO PUEDE CAMBIAR EL LORE (tal cual)
Fórmulas de combate, PV/daño/XP por nivel, slots, 1-3 variantes, 40-60% de atasco, probabilidades de mapa y encuentros, persistencia, el máximo de 3 compañeros, las **reglas de seguridad de menores (50)**, la regla de no morir de niños, y el tope de 5 misiones por NPC. Si el lore pide alterarlos, se ignora y se anota en el LOG.

## CÓMO USA LA IA UN LORE (procedimiento al cargar)
1. Leer `CONFIG_LORE`. 2. Filtrar cada catálogo: conservar solo lo que el lore lista. 3. Instanciar lo conservado: nombres propios, lugares, apariencia, edad. 4. Asignar NPC a cuadras y edificios según su «lugar típico». 5. Instanciar misiones: por cada NPC con misión, tomar las que el lore no descartó; crear los objetos y lugares de cada misión. 6. Validar (50): edades, grupos, apariencia, no-muerte. 7. Generar la cuadra inicial y mostrar la pantalla (38).
Si el lore **agrega** algo fuera de los catálogos (una facción, un NPC, una ubicación, una especie), la IA lo clasifica con el arquetipo más cercano y lo registra con ID.

## CONFIG_LORE FINAL (plantilla, tal cual)
```
LORE = nombre
TONO = ...
MONEDA = ...
NECESIDADES = on|off          CONTAMINACION = on|off
MODULO_EXTERNO = off          NIVEL_MAX = 30

TERRITORIOS = [
  {nombre, posicion, formacion, clima, relieve, agua, modificador, ubicaciones[], criaturas{temas, fases}, facciones[]}
]
UBICACIONES = [ {id, nombre, arquetipo (UB-nnn), territorio, cuadras, edificios, clase} ]

REPARTO = {
  edades_permitidas: [niño, adulto],
  apariencia_adultos: femenina|masculina|mixta,
  apariencia_niños:   femenina|masculina|mixta,
  excepciones: [{tema o especie, apariencia}],
  grupos_separados: [[adultos, niños]],
  sin_muerte: true
}

CRIATURAS = {
  temas_activos: [T1, T14, ...],
  fases_activas: {T1: [..], T14: [..]},
  especies_activas: [IDs], especies_apagadas: [IDs],
  modificadores_apagados: [...],
  genero_criaturas: ...                # si el lore lo restringe
}

NPC = { incluidos: [NPC-nnn...], descartados: [...], agregados: [...] }
NINOS = [ {id NIN-nnn, nombre (una sola palabra), grupo, apariencia} ]
COMPANEROS = [ {id CMP-nnn, nombre (una sola palabra)} ]
RESPAWNEABLES = { incluidos: [RSP-nnn...], con_facciones: {RSP-nnn: nombre_de_facción}, agregados: [...] }
MISIONES = { principales: [MP-nn...], secundarias: [MS-nn...], por_npc: {NPC-nnn: [nombres]}, descartadas: [...] }
FACCIONES = [ {nombre, tipo (infantil|adultas|mixta separada), carácter, territorio} ]
OBJETOS = { armas: [...], municion: [...], ropa: [...], comida: [...], medicinas: [...], descartados: [...] }
NOMBRES = { estilo, ejemplos }
ARRANQUE = { protagonista (edad, personalidad), ubicación inicial, misión inicial, compañero inicial }
```
La IA **valida** este bloque con las reglas del 50 antes de empezar.

## EJEMPLOS DE ÓRDENES DEL LORE (tal cual)
- «Todos los adultos son femeninos» → toda criatura, NPC y enemigo adulto generado usa apariencia femenina, salvo las excepciones nombradas.
- «Solo existen niños y mujeres, en grupos separados» → no se crean grupos mixtos; los niños no se mezclan en facciones de adultos.
- «Sin criaturas, solo enemigos» → los temas se apagan salvo las especies hostiles listadas.
- «Los alfas son gigantes amistosos al este de los campos, fases 1-3» → tema T14 activo con fases [1,2,3] y su territorio.
- «No hay torres ni refugios» → los arquetipos «torre habitada» e «instalación subterránea» se descartan, y los NPC y misiones ligados a ellos desaparecen.

## CUANDO EL LORE QUITA ALGO
Las misiones o NPC dependientes de lo descartado se descartan con ello; si una misión principal queda sin camino, la IA la reemplaza por la plantilla equivalente de MISIONES_BASE o la omite sin dejar la campaña sin final.
