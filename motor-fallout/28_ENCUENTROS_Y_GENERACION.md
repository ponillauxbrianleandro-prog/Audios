# 28 · ENCUENTROS Y GENERACIÓN DE ENEMIGOS

## CUÁNDO SE TIRA UN ENCUENTRO (tal cual)
Tirada independiente de encuentro en cada una de estas situaciones:
| Situación | Prob. base | Ajustes |
|---|---|---|
| Al llegar a ubicación normal (primera vez) | 20% | +10 noche, +10 hostil |
| Al llegar a ubicación hostil (siempre hay grupo) | 100% (no se tira: ya existe la población) | regenera >48 h (07) |
| Al llegar a ubicación segura | 3% | solo eventos neutros |
| Al BUSCAR (04, paso 3) | 10% normal / 30% hostil / 3% segura | +10 noche, +5 ruido |
| Durante un tramo de viaje (07) | 10-30% según bioma y distancia | +10 noche, −10 ruta segura |
| Al abrir el mapa de papel (07) | 5% / 12% / 25% | +10 noche |
| Al descansar (11) | 12% por cada 4 h (normal) | hostil: bloqueado |
| Al hacer ruido (forzar, combate cercano, disparo sin silenciador) | 15% | −5 sigilo |
| Evento aleatorio (13) resultado 1-20 | — | encuentro hostil |

## CONSTRUCCIÓN DEL ENCUENTRO (orden fijo)
1. **Tema y especie:** filtrar por bioma, región, lore y temas activos (18). Elegir según pesos del bloque 27 (especies con `slot ≤ nivel/2`).
2. **Fase:** tomar la tabla de fases del lore. Por defecto: fases 1-3 en entornos salvajes, fases 4-7 cerca de asentamientos, 13 en civilización, 14 solo en zonas de élite.
3. **Variante:** entre las activas de esa criatura y fase (27). 50% la más nueva.
4. **Modificadores universales (24):** prob. según nivel; 0-2 por entidad.
5. **Equipo (humanoides, 26):** tirada de tier E0-E5.
6. **Cantidad (tal cual):**
| Talla | Cantidad mín-máx | Habitual |
|---|---|---|
| T1 | 2-7 | 3-5 |
| T2 | 1-5 | 2-4 |
| T3 | 1-4 | 1-3 |
| T4 | 1-3 | 1-2 |
| T5 | 1-2 | 1 |
Ajustar por tipo de encuentro: ubicación hostil +1-2 (hasta 7 en habitual), búsqueda/viaje −1, jefe: ver abajo. "Gregaria" +1-2, "Cobarde" −1.
7. **IDs y fichas:** crear `ENE-xxx` por entidad con PV propios. Clones comparten plantilla pero no estado.
8. **Posición:** frente / medio / fondo según rol (distancia al fondo, jefe al fondo).
9. **Estado de alerta:** Oculto / Precaución / Detectado (33).

## MEZCLA DE ESPECIES
Una especie por encuentro, salvo:
- manadas de especie principal + líder alfa (misma especie);
- grupos de humanos con criaturas controladas o domesticadas;
- jefes con subordinados de su propio tema;
- colmenas con reina + obreras;
- lore que defina alianza entre especies.

## ENCUENTROS ESPECIALES (tirada 1d100 al construir un encuentro de nivel ≥ 3)
| 1d100 | Encuentro |
|---|---|
| 1-3 | Escena única irrepetible (caravana atacada, viajero herido, ruina intacta) |
| 4-8 | NPC neutral con oferta (comercio, información, misión) |
| 9-12 | Grupo en pelea entre sí (el jugador puede ayudar o aprovechar) |
| 13-15 | Criatura herida o domesticable (acción "Calmar", CAR) |
| 16-18 | Trampa del terreno / peligro ambiental sin enemigos |
| 19-100 | Encuentro normal |
Cada encuentro especial único se registra y no vuelve a salir.

## JEFES (tal cual)
- Un jefe por zona clave o hito de nivel. Nivel mínimo en la ficha. **No cuenta para el sistema de variantes** (27).
- Subordinados: máx. 3 por invocación, tope de vivos (4-6; 10 en jefes de nivel 20+), cooldown 3 rondas, **máximo 3 ciclos de invocación por combate** (después el jefe pelea con lo que quede), **condición de corte** (matar al jefe, destruir fuente, vencer tiempo).
- Si el jefe no muere, la invocación continúa hasta el tope. Si el jugador mata a todos los subordinados, el jefe puede re-invocar 1 vez.
- Jefes tienen fases (ej. 100-60% PV normal, 60-30% invoca, 30-0% furia: +25% daño).
- Recompensa: objeto único, XP 300+, evento de mapa.

## REGENERACIÓN DE POBLACIÓN (07)
Ubicación hostil sin presencia del jugador durante > 48 h de juego: nueva población con el pool **actual** del nivel del jugador (no el de la visita anterior). Jefes y únicos: reglas propias.

## DETECCIÓN Y PERSECUCIÓN (resumen; detalle en 33)
- Al aparecer, cada enemigo tira detección contra el jugador. Si no detecta: estado Oculto/Precaución y el jugador puede ATACAR (emboscada), sigilo o evitar.
- Persecución: si el jugador huye, enemigos veloces o rastreadores lo siguen hasta 2 rondas más; luego tirada de pérdida (60% si hay cobertura).

## MUERTE Y LIMPIEZA
Al morir el último enemigo: ubicación pasa a despejada, cadáveres como contenedores (05), XP según tabla (27). Los enemigos huidos conservan su ID y pueden volver en 1-24 h.

## BALANCE DE EMERGENCIA
Si el jugador ha perdido 3 combates seguidos (contador_derrotas), el siguiente encuentro baja 1 slot de talla y −1 enemigo (salvo jefes).
