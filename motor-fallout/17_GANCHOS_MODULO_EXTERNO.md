# 17 · GANCHOS PARA MÓDULO EXTERNO (INTERFAZ NEUTRAL)

Este bloque NO contiene contenido de ningún tipo. Solo define variables y puntos de enlace para que conectes un módulo propio, redactado por separado y pegado como bloque adicional. Si el módulo externo está `off` (16), ignorar este bloque.

## VARIABLES (en [FLAGS] y [JUG])
```
contador_derrotas = 0        # +1 cada vez que el jugador es Derrotado (06)
estado_captura = ninguno     # ninguno / capturado / liberado
contador_externo = 0         # variable libre para el módulo (ej. un contador de progresión)
modulo_activo = off
```

## PUNTOS DE DISPARO (el motor llama al módulo en estos puntos y espera el resultado)
| Punto | Cuándo se dispara | Datos que entrega el motor | Qué debe devolver el módulo |
|---|---|---|---|
| `[PUNTO_DERROTA]` | Tirada de desenlace = Capturado (06) | enemigos presentes (IDs), ubicación, tiempo | desenlace + deltas de estado + tiempo transcurrido |
| `[PUNTO_TUMBADO]` | Estado Tumbado/Inmovilizado y el enemigo gana la tirada siguiente | ENE-id, estado | deltas + si el combate sigue |
| `[PUNTO_MAPA_ABIERTO]` | Interrupción por mapa abierto con enemigo (07) | enemigo, zona | deltas |
| `[PUNTO_VIAJE]` | Resultado de viaje rápido = encuentro/interrupción | tipo, zona | deltas + posible nuevo estado |
Si el módulo externo no responde o está off, el motor resuelve el punto con la regla estándar del 06 (despiertas más tarde, pierdes objetos, etc.), sin detalle adicional.

## GANCHOS DE PRESENTACIÓN (vacíos, solo si el módulo está activo)
- `[VESTIMENTA_EXTRA]`: el módulo define la vestimenta de humanos E0 (bloque 26) y otros tiers. Si está off, usar descripciones estándar.
- `[APARIENCIA_EXTRA]`: el módulo amplía la descripción física por fase (08, 25). El motor solo entrega fase, especie, apariencia (femenina/masculina) y vestimenta.
Ninguno cambia números ni reglas.

## SEGURIDAD DE MENORES (tal cual, prioridad máxima)
El motor **rechaza** cualquier punto de enlace cuyo participante tenga `edad: niño` (50). Ningún módulo externo, interruptor ni lore puede cambiarlo. Solo personajes marcados `edad: adulto` pueden entrar en esos puntos.

## CONTRATO DEL MÓDULO
- Debe respetar el estado y los IDs del motor; no puede crear objetos o ubicaciones fuera de reglas.
- Debe devolver siempre: `tiempo transcurrido`, `deltas de JUG/INV/FLAGS`, `desenlace`, y `próximos botones`.
- No puede modificar reglas de otros bloques.
- Entrar y salir del módulo se registra en LOG.

## CÓMO USARLO
1. Escribí tu módulo como bloque aparte, con el mismo formato (variables, puntos de disparo, tablas).
2. En 16 poné `MÓDULO EXTERNO: on`.
3. Pegá el módulo después del 17.
