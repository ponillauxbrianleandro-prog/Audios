# 32 · EQUIPO, ARMADURA, HERRAMIENTAS Y OBJETOS GENERALES

## REGLA (tal cual)
Efectos, pesos y cantidades son fijos. Nombres y aspecto los pone el lore (genérico). Formato `ID | Arquetipo | Valor | Peso | Efecto`.

## ROPA Y ARMADURA POR SLOT (RD = reducción de daño)
Tiers de equipo E0-E5 (coinciden con 26):
| Tier | Torso RD | Piernas RD | Cabeza RD | Pies RD | Peso total | Valor |
|---|---|---|---|---|---|---|
| E0 Ropa mínima | 0 | 0 | 0 | 0 | 1-3 | 1 |
| E1 Ropa básica | 1 | 0 | 0 | 0 | 4 | 5 |
| E2 Reforzada | 2 | 1 | 1 | 0 | 8 | 20 |
| E3 Ligera | 3 | 2 | 1 | 0 | 12 | 60 |
| E4 Militar | 5 | 3 | 2 | 1 | 20 | 180 |
| E5 Pesada / asistida | 8 | 5 | 3 | 2 | 30-60 | 500+ |
Durabilidad 40-140 según tier; pierde 1-3 por golpe fuerte (daño > 12). Reparar: kit + chatarra, tirada INT.
**Armadura asistida (E5+):** requiere "núcleo de energía" (consumible, 8 h) y FUE ≥ 7. Da +RD 8-14, +FUE 2, −AGI 1, +carga 40; velocidad −10%; sin núcleo es inmovilizante. Solo piezas completas.
**Resistencias adicionales (tal cual):** radiación, frío, calor, ácido, energía (cada una 0-40% según pieza; se suman hasta 60%).
**Efectos de vestimenta temática:** ropa de facción (disfraz), ropa con accesorios de animal (fases 9-11, neutral, afecta reputación con fase 14), trajes completos (E2, −10% velocidad). Los detalles estéticos los define el lore o el módulo externo.

## ACCESORIOS Y MOCHILAS
| ID | Arquetipo | Efecto |
|---|---|---|
| G-01 | Mochila pequeña | +10 carga |
| G-02 | Mochila grande | +25 carga, −5% sigilo |
| G-03 | Cinturón de herramientas | +3 espacios rápidos |
| G-04 | Gafas / visor | +5 PER visual; protege polvo |
| G-05 | Linterna | Luz 4 h por pila; −sigilo |
| G-06 | Casco con luz | +1 RD cabeza, luz |
| G-07 | Máscara respiratoria | Resiste gas, esporas, +10% rad |
| G-08 | Guantes | +5 forzar, protege |
| G-09 | Botas reforzadas | +1 RD pies, −ruido |
| G-10 | Radio | Recibe señales, eventos de región |
| G-11 | Detector (metal, radiación, movimiento) | +10 PER para su tipo |
| G-12 | Cámara / grabador | Registra eventos (misiones) |
| G-13 | Dispositivo de muñeca | Mapa informativo (07); siempre equipado, no se pierde |

## HERRAMIENTAS
| ID | Arquetipo | Efecto | Uso |
|---|---|---|---|
| T-01 | Ganzúa | +cerraduras, se rompe 10% | consumible |
| T-02 | Palanca | +10 forzar | 100 usos |
| T-03 | Kit de reparación | +40% durabilidad arma/armadura | 3 usos |
| T-04 | Kit de herramientas | Habilita reparar/fabricar | no se agota |
| T-05 | Soplete / cortador | Abre cerraduras metálicas (nivel 3) | combustible |
| T-06 | Cuerda y garfio | Escalar/descender | 1 uso por obstáculo |
| T-07 | Cizalla | Corta cadenas/vallas | 50 usos |
| T-08 | Multiherramienta | −5 min en tareas técnicas | no se agota |
| T-09 | Terminal portátil | Hackeo remoto (INT) | batería 2 h |
| T-10 | Kit de supervivencia | Fuego, refugio, filtrar agua | 5 usos |
| T-11 | Kit de cocina | Cocinar con mejoras | no se agota |
| T-12 | Banco de trabajo (ubicación) | Fabricar/mejorar armas | fijo |

## LLAVES, ACCESOS, DATOS
| ID | Arquetipo | Efecto |
|---|---|---|
| K-01 | Llave | Abre una cerradura concreta (por ID) |
| K-02 | Tarjeta de acceso | Abre puertas/terminales de nivel dado |
| K-03 | Código | Texto/nota con código (por ID) |
| K-04 | Holocinta / dato grabado | Información, misiones, historia |
| K-05 | Nota / documento | Pista, mapa parcial, objetivo |
| K-06 | Mapa de papel | Habilita mapa general (07) |
| K-07 | Plano | Habilita fabricar objeto (por ID) |
| K-08 | Libro | Lore, bonus de comercio o fabricación del lore |
Terminales (T-09): requieren INT; pueden dar mapas, desbloquear puertas, desactivar torretas, leer registros. Fallo 3 veces = bloqueo 24 h.

## CHATARRA Y COMPONENTES (objetos generales; ver 10)
| ID | Arquetipo | Valor | Peso | Uso |
|---|---|---|---|---|
| J-01 | Chatarra metálica | 1 | 0.5 | Reparar, fabricar, vender |
| J-02 | Tuercas y tornillos | 1 | 0.1 | Reparar, mods |
| J-03 | Cableado | 2 | 0.2 | Terminal, mods |
| J-04 | Circuito | 6 | 0.1 | Mods, dispositivos |
| J-05 | Pegamento / cinta | 2 | 0.1 | Reparar |
| J-06 | Tela / cuero | 2 | 0.3 | Armaduras, mochilas |
| J-07 | Químicos base | 4 | 0.2 | Munición, medicina |
| J-08 | Combustible | 3 | 1 | Lanzallamas, encendido |
| J-09 | Batería / célula | 5 | 0.3 | Dispositivos |
| J-10 | Piezas mecánicas | 5 | 0.5 | Reparar, torretas |
| J-11 | Madera / material de construcción | 1 | 1 | Refugio, barricadas |
| J-12 | Objeto de valor (joya, reliquia) | 20-200 | 0.1 | Vender; misión |
| J-13 | Objeto personal / coleccionable | 5-60 | 0.2 | Misión/comercio |
| J-14 | Basura | 0.5 | 0.3 | Vender barato |

## FABRICACIÓN Y MEJORA
`Planos + componentes + estación`; tirada 50 + INT×4 + bono_nivel. Éxito: objeto con durabilidad 100%. Fallo: se pierde 50% de componentes. Éxito crítico (≤5): tier +1 en una mejora.

## BOTÍN POR TIER Y NIVEL
Contenedor común: 0-2 objetos generales, 0-1 equipo/herramienta (tier ≤ nivel/6 + 1). Contenedor raro: tier +1. Jefes: objeto único del lore.

## PESOS Y LÍMITE
Carga máx = 50 + FUE×10 + 5×nivel (12). Equipo equipado pesa 50%.

## DEVOLUCIÓN Y VENTA
Venta: 40-70% del valor (09). Objetos de misión no se venden.
