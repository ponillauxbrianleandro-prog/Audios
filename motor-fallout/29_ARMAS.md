# 29 · ARMAS (arquetipos de Fallout 1, 2 y 3 con efectos fijos)

## REGLA (tal cual)
Los **efectos son fijos**; el **nombre, aspecto y existencia** los decide el lore (genérico). Si el lore no tiene un arquetipo (ej. energía en un mundo de fantasía), ese arquetipo se apaga o se reemplaza por otro con los mismos números. Armas con nombre propio = ficha del lore.

## TIERS DE ARMA (se aplican a cualquier arquetipo)
| Tier | Nombre | Mult. daño | %impacto | Durabilidad | Valor × |
|---|---|---|---|---|---|
| 1 | Improvisada | ×0.7 | −5 | 40 | 1 |
| 2 | Común | ×1.0 | 0 | 70 | 3 |
| 3 | Mejorada | ×1.3 | +5 | 90 | 8 |
| 4 | Militar | ×1.7 | +8 | 110 | 20 |
| 5 | Especial / única | ×2.2 | +10 | 140 | 60 |
Daño final = daño base del arquetipo × mult. de tier + bonus FUE (solo melé) − RD del objetivo (mín. 1).

## ARQUETIPOS
Columnas: ID | Arquetipo | Daño base (tier 2) | Alcance | PA | Munición (30) | Rasgo | Req. stat
### DESARMADO Y MELÉ
| ID | Arquetipo | Daño | Alc. | PA | Munic. | Rasgo | Req |
|---|---|---|---|---|---|---|---|
| W-01 | Puños | 3-5 | cuerpo | 3 | — | Sin arma, sin requisito | — |
| W-02 | Arma de puño (guante, nudillera) | 5-8 | cuerpo | 3 | — | +10% crítico | FUE 3 |
| W-03 | Garra / arma de mano potenciada | 8-12 | cuerpo | 4 | — | Sangrado 25% | FUE 4 |
| W-04 | Cuchillo | 4-7 | cuerpo | 3 | — | Sangrado 20%, sigilo +10 (emboscada ×2.5) | — |
| W-05 | Machete / hoja larga | 7-11 | cuerpo | 4 | — | Sangrado 25% | FUE 4 |
| W-06 | Porra / garrote | 6-10 | cuerpo | 4 | — | Aturde 15% | FUE 4 |
| W-07 | Bate / barra | 7-12 | cuerpo | 4 | — | Aturde 20% | FUE 5 |
| W-08 | Martillo / maza (2 manos) | 10-16 | cuerpo | 6 | — | Aturde 25%, rompe estructuras | FUE 6 |
| W-09 | Hacha (2 manos) | 11-17 | cuerpo | 6 | — | Sangrado 30% | FUE 6 |
| W-10 | Lanza | 8-12 | cuerpo/corto | 5 | — | Ataca primero al cargar | FUE 4 |
| W-11 | Arma de energía cuerpo a cuerpo | 12-18 | cuerpo | 5 | célula de energía (consumo 1/5 usos) | Ignora 3 RD | FUE 5 |
| W-12 | Arma arrojadiza (cuchillo, lanza corta) | 4-8 | corto | 3 | — (recuperable 70%) | Silenciosa | AGI 5 |
### DISTANCIA (PROYECTIL)
| ID | Arquetipo | Daño | Alc. | PA | Munic. | Rasgo | Req |
|---|---|---|---|---|---|---|---|
| W-20 | Pistola pequeña | 6-10 | corto-medio | 4 | pequeña | Cargador 8-12 | PER 3 |
| W-21 | Revólver | 9-14 | medio | 5 | mediana | Cargador 6; +10% crítico | PER 4 |
| W-22 | Pistola con silenciador | 5-9 | corto | 4 | pequeña | Silenciosa (ruido 0), sigilo +10 | PER 4 |
| W-23 | Pistola potente | 12-18 | medio | 6 | grande | Retroceso: −10% siguiente | PER 5, FUE 5 |
| W-24 | Subfusil | 4-7 ×3 ráfaga | corto | 6 | pequeña | Ráfaga 3 tiros, −15% por tiro | PER 4 |
| W-25 | Rifle de caza | 10-16 | largo | 5 | mediana | +10% impacto apuntado | PER 5 |
| W-26 | Rifle de palanca/cerrojo | 12-18 | largo | 6 | mediana | Recarga 1/ronda | PER 5 |
| W-27 | Rifle de asalto | 7-12 ×3 ráfaga | medio-largo | 7 | mediana | Ráfaga 3 | PER 5, FUE 5 |
| W-28 | Rifle de precisión (francotirador) | 18-28 | muy largo | 8 | grande | +20% apuntado; crítico +15% | PER 7 |
| W-29 | Escopeta | 14-24 (corto) | corto | 6 | cartucho | Dispersión: −% por distancia; vs. varios | FUE 5 |
| W-30 | Escopeta recortada | 18-28 (muy corto) | muy corto | 6 | cartucho | Solo adyacente, 2 cartuchos | FUE 5 |
| W-31 | Ballesta / arco | 8-14 | medio | 5 | flecha/dardo | Silenciosa, recuperable 50% | PER 4 |
### PESADAS Y ESPECIALES
| ID | Arquetipo | Daño | Alc. | PA | Munic. | Rasgo | Req |
|---|---|---|---|---|---|---|---|
| W-40 | Ametralladora pesada | 5-9 ×5 ráfaga | largo | 10 | mediana | Ráfaga 5, suprime (−15% enemigos) | FUE 6 |
| W-41 | Minigun (cañón rotativo) | 4-7 ×10 ráfaga | largo | 14 | mediana | Ráfaga 10; recalienta | FUE 8 |
| W-42 | Lanzallamas | 8-14 + quemadura | corto | 8 | combustible | Cono 2-3 objetivos; quemadura 3 rondas | FUE 6 |
| W-43 | Lanzagranadas | 15-25 (área) | medio | 8 | granada | Área 2 objetivos | PER 5 |
| W-44 | Lanzacohetes | 30-45 (área) | largo | 10 | cohete | Área 3 objetivos | FUE 6 |
| W-45 | Lanzador de misiles | 45-65 (área) | muy largo | 12 | misil | Área 4 objetivos | FUE 7 |
| W-46 | Lanzador táctico (catapulta nuclear tipo "Fat Man") | 150 (área grande) | muy largo | 15 | carga táctica (única) | Destruye zona; radiación +200; autodaño si cerca | FUE 8 |
### ENERGÍA (si el lore lo permite)
| ID | Arquetipo | Daño | Alc. | PA | Munic. | Rasgo | Req |
|---|---|---|---|---|---|---|---|
| W-50 | Pistola de energía | 8-13 | medio | 5 | célula pequeña | Ignora 2 RD | PER 4 |
| W-51 | Rifle de energía | 12-20 | largo | 6 | célula | Ignora 3 RD | PER 5 |
| W-52 | Pistola de plasma | 14-22 | medio | 6 | célula de plasma | Quemadura 2 rondas | PER 5 |
| W-53 | Rifle de plasma | 20-32 | largo | 8 | célula de plasma | Quemadura 3 rondas | PER 6 |
| W-54 | Arma de pulso (EMP) | 10-16 | medio | 6 | célula | ×2 vs. artificiales; aturde | PER 5 |
| W-55 | Arma de rayos / sónica | 10-18 | medio | 6 | célula | Aturde 20% | PER 5 |
| W-56 | Arma de congelación | 8-14 + ralentiza | medio | 6 | célula | Ralentiza 2 rondas | PER 5 |
### EXPLOSIVOS Y TRAMPAS (consumibles de combate)
| ID | Arquetipo | Daño | Alc. | PA | Rasgo |
|---|---|---|---|---|---|
| W-60 | Granada de fragmentación | 20-30 (área) | corto | 4 | Área 3 objetivos, daño por fragmentos |
| W-61 | Granada incendiaria | 10-16 + quemadura | corto | 4 | Fuego en zona 3 rondas |
| W-62 | Granada de humo | 0 | corto | 3 | −30% impacto enemigos 3 rondas |
| W-63 | Granada de pulso | 20-30 a artificiales | corto | 4 | Aturde máquinas |
| W-64 | Granada de plasma | 30-45 (área) | corto | 4 | Quemadura 2 rondas |
| W-65 | Dinamita / carga | 25-40 (área) | colocada | 5 | Mecha 1-3 rondas; rompe puertas |
| W-66 | Mina de proximidad | 20-35 (área) | colocada | 5 | Se activa al pisarla; detectable |
| W-67 | Trampa de cuerda / cepo | 8-14 + inmoviliza | colocada | 5 | Detectable PER |
| W-68 | Cebo o señuelo | 0 | colocado | 3 | Atrae enemigos 5 rondas |
| W-69 | Granada de choque | 5-10 + aturde | corto | 4 | Aturde 30% |

## EFECTOS DE ESTADO DE ARMA (tal cual)
- **Crítico:** tirada ≤ 5 (o ≤ SUE/2): daño ×2 (×2.5 melé). **Crítico apuntado** (cabeza): +30% impacto crítico.
- **Atasco:** pifia ≥ 96: pierde la acción. Si durabilidad < 25%: atasco desde 91.
- **Daño por durabilidad:** si durabilidad < 50%, daño ×0.85; < 25% ×0.7; 0 = rota.
- **Desgaste:** cada uso −1 durabilidad (explosivos y proyectiles se consumen). Estrés por mal uso (ácido) −2.
- **Ráfaga:** cada tiro tira impacto aparte; PA como indica.
- **Dispersión (escopeta):** −10% impacto por rango de distancia; a corto rango se impacta a 2 objetivos adyacentes (tirada separada, mitad de daño).
- **Recarga:** 1 acción menor (PA 2).
- **Silenciada:** no genera ruido; si el enemigo no te vio, mantiene Oculto.
- **Cuerpo a cuerpo con arma de distancia:** −15% impacto y +PA.
- **Doble empuñadura:** dos armas de una mano: +1 ataque, −20% impacto cada una.

## MEJORAS (mods) (tal cual)
Mira (+8% impacto largo), silenciador (ruido 0, −10% daño), cargador ampliado (+50% munición), culata reforzada (−retroceso), cañón largo (+alcance), afilado (+10% daño melé), recalibrado (+5% daño, −5 durabilidad), refrigeración (minigun/energía). Máx. 2 mods por arma. Instalar: 10 min, tirada INT.

## REQUISITO DE STAT
Si el stat del jugador es menor al requerido: −5% impacto por punto de diferencia y −10% daño.

## GENERACIÓN EN BOTÍN (genérico)
Arma encontrada: arquetipo según lore y fuente; tier según nivel (tabla E0-E5 de 26); durabilidad 40-100%; munición 0-2 cargadores.
