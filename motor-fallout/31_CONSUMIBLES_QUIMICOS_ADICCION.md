# 31 · CONSUMIBLES, QUÍMICOS, ALCOHOL, RADIACIÓN Y ADICCIÓN

## REGLA (tal cual)
La **cantidad que se encuentra, el efecto numérico y la duración** son fijos. Los **nombres** (comida, medicina, químicos) los decide el lore (genérico). Si el lore no tiene químicos o alcohol, esa sección se apaga.
Formato: `ID | Arquetipo | Efecto | Duración | Peso | Valor | Rasgo`.

## COMIDA (hambre baja; puede dar PV; cruda/caducada riesgo)
| ID | Arquetipo | Hambre − | PV | Notas |
|---|---|---|---|---|
| CM-01 | Ración cruda (carne, verdura) | −15 | 0 | Cruda: 15% de Enfermo |
| CM-02 | Comida cocinada | −30 | +8 | Requiere fuego |
| CM-03 | Comida enlatada | −25 | +5 | Sin riesgo |
| CM-04 | Comida preservada/seca | −20 | +3 | Dura 30 días |
| CM-05 | Comida de calidad (banquete) | −50 | +15 | Estado Descansado 4 h |
| CM-06 | Comida caducada | −10 | 0 | 30% Enfermo |
| CM-07 | Comida contaminada | −20 | 0 | +20 rad |
| CM-08 | Golosina / barra | −8 | +2 | +5% PA 30 min |
| CM-09 | Sopa / guiso | −35 | +10 | Calienta (frío −) |
| CM-10 | Comida de criatura (carne de especie) | −20 | +4 | Según especie; mutada +10 rad |
## AGUA Y BEBIDAS (sed baja)
| ID | Arquetipo | Sed − | Rad | Notas |
|---|---|---|---|---|
| BB-01 | Agua limpia | −35 | 0 | |
| BB-02 | Agua purificada | −40 | 0 | −10 rad |
| BB-03 | Agua sucia / turbia | −30 | +30 | Enfermo 10% |
| BB-04 | Agua de río/pozo | −30 | +10 | Enfermo 5% |
| BB-05 | Bebida azucarada | −20 | 0 | −8 fatiga 1 h |
| BB-06 | Bebida energética | −15 | 0 | +PA 20% 1 h; luego +10 fatiga |
| BB-07 | Té / infusión | −20 | 0 | +5 CAR 1 h |
## ALCOHOL (si el lore lo permite)
| ID | Arquetipo | Efecto (1 h) | Adicción | Notas |
|---|---|---|---|---|
| AL-01 | Cerveza | +1 CAR, −1 PER | 2% | Sed −10 |
| AL-02 | Vino | +1 CAR, −1 AGI | 2% | |
| AL-03 | Licor fuerte | +2 FUE, −2 PER, −1 AGI | 5% | Calor |
| AL-04 | Destilado casero | +2 RES, −2 INT, −2 PER | 8% | Veneno leve 5% |
| AL-05 | Licor raro | +1 todos, −1 PER | 3% | Raro |
## MEDICINA
| ID | Arquetipo | Efecto | Duración | Notas |
|---|---|---|---|---|
| MD-01 | Vendaje | Quita Sangrando; +10 PV | — | Max 2 por combate |
| MD-02 | Estimulante curativo (jeringa) | +30 PV | instantáneo | Valor 25; adictivo 0 |
| MD-03 | Estimulante curativo mayor | +60 PV | instantáneo | Raro |
| MD-04 | Kit médico | +40 PV, cura 1 estado | 5 min | Requiere INT 4 |
| MD-05 | Antibiótico | Quita Enfermo | — | |
| MD-06 | Antídoto | Quita Envenenado | — | |
| MD-07 | Anti-radiación (dosis) | −150 rad | — | Efecto secundario: −1 PER 1 h |
| MD-08 | Protector de radiación | +40% resistencia rad | 4 h | |
| MD-09 | Analgésico | Ignora estado Herido 2 h | 2 h | Adicción 4% |
| MD-10 | Suero de reanimación | Revive de Derrotado con 30% PV | — | Raro; 1 uso |
| MD-11 | Inyector de calma | Quita Asustado/Confundido | — | |
| MD-12 | Vendaje reforzado | +20 PV, quita sangrado y Herido | — | |
## QUÍMICOS DE COMBATE (si el lore los permite; nombres genéricos)
| ID | Arquetipo | Efecto | Duración | Adicción | Abstinencia |
|---|---|---|---|---|---|
| QU-01 | Estimulante de reflejos | +20% iniciativa, +3 PA | 2 h | 15% | −1 AGI |
| QU-02 | Estimulante de fuerza | +3 FUE | 1 h | 15% | −1 FUE |
| QU-03 | Estimulante de percepción | +3 PER | 1 h | 15% | −1 PER |
| QU-04 | Estimulante de resistencia | +3 RES, +20 PV temporales | 1 h | 15% | −1 RES |
| QU-05 | Furia química | +25% daño, −15% defensa | 10 rondas | 20% | −1 INT |
| QU-06 | Concentración | +10% impacto, +1 INT | 1 h | 12% | −1 INT |
| QU-07 | Velocidad | +5 PA, +50% movimiento | 20 min | 18% | Fatiga +20 |
| QU-08 | Bloqueador de dolor | −25% daño recibido | 5 rondas | 12% | Herido +10 |
| QU-09 | Estimulante de carisma | +3 CAR | 1 h | 10% | −1 CAR |
| QU-10 | Estimulante de suerte | +2 SUE | 1 h | 10% | −1 SUE |
| QU-11 | Mezcla militar | +2 FUE, +2 RES, −1 INT | 1 h | 25% | −2 todos |
Adicción en %: tirada por cada uso; si ocurre, aparece estado **Adicto (nombre del químico)**.

## SISTEMA DE ADICCIÓN Y ABSTINENCIA (tal cual)
- **Adicto:** estado persistente. Si pasan 24 h sin consumirlo: **abstinencia** (aplica la penalización de la tabla, sube cada 24 h hasta −3, máx.).
- Quitar adicción: Medicina específica (MD-xx "desintoxicante"), descanso en lugar seguro 3 días con medicina, o paciente (7 días sin consumir, tirada RES 60%+RES×3).
- Consumir el químico durante abstinencia la alivia 1 h y reinicia el contador.
- Un NPC médico o aliado puede ofrecer tratamiento (comercio, 09).
- Registrar: `adicciones=[QU-05: d3, abstinencia 0]`.

## RADIACIÓN Y ANTÍDOTOS (mecánica de 11)
`rad` 0-1000; fuentes: agua, comida, zona, criaturas, slimes radiactivos, armas (W-46). Reducción: MD-07, filtros, descontaminación. Protección: MD-08, trajes sellados (32). El lore puede renombrar "radiación" a otra contaminación; la mecánica se mantiene.

## CONSUMIBLES AMBIENTALES Y DE SUPERVIVENCIA
| ID | Arquetipo | Efecto |
|---|---|---|
| AM-01 | Bengala / antorcha | Luz 1 h; revela; atrae |
| AM-02 | Repelente | −50% encuentros insectos/animales 4 h |
| AM-03 | Filtro de aire/máscara | Inmune a gas/esporas 30 min |
| AM-04 | Cantimplora llena | 3 usos de agua |
| AM-05 | Yesca / combustible | Encender fuego (cocinar, calor) |
| AM-06 | Manta / saco | Dormir en exterior: riesgo −5% |
| AM-07 | Cebo de comida | Atrae/distrae a criaturas T1-T3 |
| AM-08 | Gas lacrimógeno / humo | −30% impacto enemigos |
| AM-09 | Raciones de viaje (pack) | Hambre −40, sed −20, 3 usos |
| AM-10 | Kit de primeros auxilios | 3 vendajes + 1 antídoto |

## EFECTOS PASIVOS DE LAS COMIDAS Y BEBIDAS
Efectos de estado temporales (Descansado, Caliente, Estimulado) duran lo indicado; no se acumulan del mismo tipo (se renueva el tiempo).

## CANTIDADES EN BOTÍN (tal cual)
Contenedor común: 0-2 comestibles, 0-1 bebida. Cocina: 1-4 comestibles. Médico: 1-3 medicinas. Caja de químicos: 1-3 dosis. Enemigo T1: 0-1 consumible; humano E0: 0-1.
