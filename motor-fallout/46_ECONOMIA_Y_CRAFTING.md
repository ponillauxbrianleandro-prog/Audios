# 46 · ECONOMÍA, COMERCIO, REPARACIÓN Y FABRICACIÓN

## MONEDA Y VALORES (tal cual)
Moneda: cuñas (42). Valores base (antes de precio): venda 3 · lata 4 · agua 3 · inyector verde 25 · tónico 20 · ganzúa 5 · kit de reparación 30 · chatarra 1 · circuito 6 · piezas 5 · recurso biológico 6 · Machete T2 30 · Maza T3 80 · Espada T4 200 · Hoja T5 600 · Chaleco E2 20 · Armadura E4 180 · Asistida E5 500.
Botín en cuñas por enemigo: 0 a 3 + 2×talla.

## COMPRAR Y VENDER (tal cual; fórmula de 09)
- **Compra** = valor × (1.4 − CAR×0.02), mínimo valor × 0.8. **Venta** = valor × (0.4 + CAR×0.02), máximo valor × 0.7.
- Con CAR 5: compra ×1.3, venta ×0.5. Relación alta con el comerciante: −10% compra, +10% venta.
- Estado/durabilidad: roto ×0.3, <50% ×0.6.
- El comerciante tiene **caja** (cuñas) limitada y **stock** que persiste y se renueva cada 72 h (±20%). Lo vendido queda en su stock.
- Botón Negociar: tirada `30 + CAR×5 + nivel − dificultad`; éxito −10% precio; fallo −5 relación.
- **Qué vende cada comerciante** (40): armas → armas y munición; recursos → chatarra, circuitos, piezas, herramientas; médica → vendas, inyectores, antídotos, tratamiento de adicción; mecánico → reparación y mejoras; cocinera → comida; animal de carga → cargas y rumores.
- Un comerciante hostil por el bando perdido (M-05) sube precios 30%.

## PROGRESIÓN DE EQUIPO (guía, tal cual)
| Nivel del jugador | Arma recomendada | Armadura |
|---|---|---|
| 1-4 | T1-T2 | E1-E2 |
| 5-9 | T2-T3 | E2 |
| 10-14 | T3 | E4 (a partir del nivel 8, 180 cuñas) |
| 15-19 | T4 | E4 |
| 20+ | T5 (recompensa de M-08) | E5 (caja de la Torre) |

## REPARACIÓN (tal cual)
- Cada golpe dado: −0.3 de durabilidad. Cada golpe recibido fuerte (daño > 12): −1 de armadura.
- Con kit: +40% durabilidad (30 cuñas). Con mecánico: 20 cuñas, 100% (tirada fija: éxito).
- Arma <50%: daño ×0.85; <25%: ×0.7; 0: ×0.4. Atasco desde el 91 si <25%.

## FABRICACIÓN Y MEJORA (tal cual)
Tirada `50 + INT×4 + nivel`. Éxito: objeto con 100% de durabilidad. Fallo: se pierde la mitad de los componentes. Éxito crítico (≤5): +1 tier en una mejora.
| Receta | Componentes | Estación | Resultado |
|---|---|---|---|
| Radio | 1 circuito + 2 chatarra | banco | arregla la radio (M-01) |
| Artefacto de inventor | 2 piezas + 1 circuito | banco | misión S-15 |
| Venda de lienzo grueso | 2 tela + 1 chatarra | cocina | +20 PV |
| Kit de remiendo | 3 chatarra + 2 piezas | banco | +40% durabilidad, 3 usos |
| Cartucho mediano | 1 chatarra + 1 químico base | banco | 4 cartuchos |
| Mejora de arma (+1 tier hasta T4) | 3 piezas + 2 circuitos + kit | banco del mecánico | sube el tier del arma una vez |
| Mejora de armadura (+1 RD) | 3 tela/cuero + 2 piezas | banco | +1 RD en una pieza |
| Trampa (cepo) | 2 chatarra + 1 cuerda | banco | W-67 |
Las recetas con efectos de armas y objetos usan los números de 29-32.

## BANCO DE TRABAJO
Hay uno en el hogar (cocina) y otro en Ciudad Horno (taller del mecánico). Botones: Fabricar, Mejorar arma, Mejorar armadura, Reparar, Desarmar (objeto → componentes).

## ECONOMÍA DEL MUNDO (tal cual)
- Ingresos típicos por nivel: nivel 1-5: 20-80 cuñas por misión; 6-12: 60-200; 13-20: 150-500; 21+: 300-1000.
- Gastos recurrentes: comida y agua (≈10 cuñas por día), vendas (3 cuñas c/u), reparaciones.
- El hogar es gratis. Las camas de posada cuestan 10 cuñas. Las camas del Cantil y de la Granja son gratis con buena relación.

## ANTI-DUPLICACIÓN (tal cual)
Todo objeto comprado/vendido/fabricado se registra con ID y cantidad. Un comerciante no vende lo que ya no tiene.
