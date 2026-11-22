# 34 · QUÉ DECIDE EL LORE Y QUÉ ES FIJO

## LEYENDA (tal cual)
En todos los bloques:
- **(genérico)** = se rellena con el lore. Es texto o selección que el lore define.
- **(tal cual)** = se deja exactamente como está. Ya está completo.
Si algo no tiene etiqueta: las tablas y fórmulas numéricas son (tal cual); los nombres propios, aspecto y listas de existencia son (genérico).

## REGLA DE ORO (tal cual)
El lore decide **qué existe y cómo se llama**. No decide **cuánto, cuántas veces ni qué efecto numérico tiene**.
Si un lore pide algo que rompa un número fijo, el motor lo ignora y avisa en el LOG.

## TABLA DE CONTROL
| Elemento | Lo decide el lore (genérico) | Es fijo (tal cual) |
|---|---|---|
| **Temas de criaturas** (18) | Cuáles están activos; palabras del tema | Lista de 13 temas disponibles, mecánica de sustitución |
| **Especies** (19-23, 35, 36) | Qué especies aparecen, nombres comunes, aspecto, jefes | Tallas T1-T5, PV/daño por talla, slots, 1-3 variantes |
| **Fases** (08, 25) | Qué fases (1-14) aparecen y en qué regiones | Definición y orden de las 14 fases, tabla de cambios, regla de adultez, regla femenina/masculina |
| **Variantes universales** (24) | Nombre y aspecto; cuáles se apagan; compatibilidades | Efectos numéricos, topes, probabilidades |
| **Humanos** (26) | Nombres de facciones, ropa, oficios | Tiers E0-E5, tabla de probabilidad de equipo, 1-2 variantes |
| **Nivelación** (27) | Eventos de hito de nivel | Curva de XP, tope 30, slots cada 2 niveles, bono_nivel |
| **Armas** (29) | Existencia de arquetipos, nombres, calibres, estética | Daño, alcance, PA, tiers, ráfagas, rasgos |
| **Munición** (30) | Nombres de calibres, envases | Familias, variantes y sus efectos, pesos |
| **Consumibles** (31) | Nombres de comida, medicina, químicos, alcohol; cuáles existen | Cantidad en botín, efecto numérico, duración, adicción |
| **Equipo** (32) | Nombres, aspecto, existencia de armadura asistida | RD por tier, pesos, efectos, herramientas |
| **Sigilo / hurto** (33) | — (casi nada) | Fórmulas, estados, ruido |
| **Mapa** (07) | Nombres de lugares, regiones, biomas, conexiones semilla | Reglas de conexión, estados, viaje rápido |
| **Misiones** (13) | Historias, dadores, recompensas temáticas | Estructura de ficha, reglas de estado |
| **Moneda y precios** (09, 10) | Nombre de la moneda | Fórmulas de precio, rangos de valor |
| **Estados** (11) | Nombres temáticos | Efectos y duraciones |
| **Interfaz** (15) | Estética | Orden y contenido de la pantalla |
| **Módulo externo** (17) | Todo el contenido del módulo | Variables, puntos de disparo, contrato |

## CONFIG_LORE (versión final y completa: bloque 99)
El bloque 99 amplía esta plantilla con reparto por edad y apariencia, territorios, NPC, misiones y facciones.

## CONFIG_LORE (plantilla corta; va al inicio del bloque 14)
```
TEMAS_ACTIVOS = [T1, T10]            # (genérico) elegir de la lista del 18
FASES_ACTIVAS = [1,2,3,4,6,7,13,14]  # (genérico) subconjunto de 1-14
ESPECIES_APAGADAS = [H-45, H-46]     # (genérico) IDs a excluir
CATEGORIAS_ACTIVAS = {armas: [W-01..W-31, W-60..W-62], municion: [A-01..A-05],                      consumibles: [CM,BB,MD,AM], quimicos: off, alcohol: on}
MODIFICADORES_APAGADOS = [Infernal]  # (genérico)
NECESIDADES = on                     # hambre/sed/fatiga
CONTAMINACION = on                   # radiación genérica
MODULO_EXTERNO = off
NOMBRES = {...}                      # (genérico) diccionario de nombres temáticos
```
Cualquier clave fuera de esta lista se ignora (tal cual).

## VALIDACIÓN (la IA debe revisar al cargar el lore) (tal cual)
1. ¿Hay al menos 1 especie T1 por tema activo? Si no, agregar una del lore.
2. ¿Cada 2 niveles hay ≥ 1 enemigo nuevo? Si no, reasignar slots (27).
3. ¿Se activó algún tema sin especies? Apagarlo.
4. ¿Alguna cantidad o efecto numérico fue alterada por el lore? Restaurar el valor fijo.
5. ¿Hay nombres reales de parásitos o arácnidos? Reemplazar por genéricos o eliminar (no existen arácnidos ni parásitos reales).
6. ¿Algún personaje humano es menor? No se generan.
7. ¿Los nombres de consumibles y munición están definidos por el lore? Si no, generar nombres coherentes (genérico).

## COMBINACIÓN DE MÚLTIPLES TEMAS (tal cual)
Un mundo puede tener 2 a 5 temas. Para evitar demasiados enemigos por zona: máx. 3 activos por región. El resto aparece por DLC o evento. El lore marca qué región usa qué tema.
Ejemplo: un mundo con criaturas con cuernos y cuerpo robusto Y con animales: ambos tienen sus propios slots; cada uno apaga las especies que el lore no quiere.

## EJEMPLO DE LORE QUE RESPETA LO FIJO
"Mundo de ceniza: temas animales y artificial. Armas sin energía. Comida: 'raciones de lata', 'carne seca'. Medicina: 'vendas', 'tónico verde' (= M-02). Munición: calibres 'pequeño', 'medio'. No hay alcohol ni químicos." → El motor mantiene todos los números, solo cambia los nombres.

## NUNCA ESTÁ PERMITIDO AL LORE (tal cual)
Alterar fórmulas; eliminar el sistema de slots o variantes; incluir menores; crear parásitos reales o arácnidos; romper la regla femenino/masculino (apariencia, no sexo); ocultar el estado del jugador.
