# 04 · SISTEMA DE BÚSQUEDA

## PRINCIPIO
BUSCAR existe en casi todas las ubicaciones. El resultado depende del tipo de ubicación, bioma, lore, nivel de exploración y tiempo. Nunca genera nada fuera de lore, y nunca repite lo ya recogido.

## ESTADO DE EXPLORACIÓN (`explor` 0–5 por ubicación o sector)
Cada BUSCAR en el mismo lugar sube `explor` en 1 (máx. 5). Tiempo por búsqueda: 10–30 min según tamaño.
| explor antes de buscar | Hallazgo relevante | Secundarios | Nada |
|---|---|---|---|
| 0 | 55 | 25 | 20 |
| 1 | 35 | 30 | 35 |
| 2 | 20 | 35 | 45 |
| 3 | 10 | 30 | 60 |
| 4+ | 5 | 15 | 80 |
(Hallazgo relevante = contenedor, objeto bueno, recurso, documento, conexión, NPC. Secundario = chatarra, recurso menor, rastro, indicio.)

## PASO 1 — TIRADA DE RESULTADO (excluyente, suma 100)
Tirá 1d100 contra la fila de `explor`. Si sale Nada → fin del paso 1.

## PASO 2 — TIPO DE HALLAZGO (excluyente, suma 100) — tirar solo si hubo hallazgo
Ajustar por tipo de ubicación (la IA reasigna manteniendo suma 100). Base:
| Categoría | % base |
|---|---|
| A. Objeto suelto | 22 |
| B. Recurso | 20 |
| C. Contenedor / elemento interactivo nuevo | 22 |
| D. Documento / información | 10 |
| E. NPC o criatura | 8 |
| F. Nueva conexión (ruta oculta) | 8 |
| G. Ubicación desconocida (detectada) | 5 |
| H. Evento | 5 |
Ajustes sugeridos: Vivienda → C+8, D+5, B−10. Industrial → B+10 (industrial), A+3. Exterior salvaje → B+10, E+5, C−10. Comercial → C+8, A+5. Subterráneo → F+6, E+4. Asentamiento → E+10, resto proporcional.
Reglas de coherencia: una vivienda no da recursos industriales; un bosque no da tarjetas de acceso, salvo justificación de lore/ruinas.

## PASO 3 — TIRADAS INDEPENDIENTES (cada una por separado, pueden darse a la vez)
- **Peligro/emboscada:** base 10% ubicación normal, 30% hostil, 3% segura. +10% si noche, +5% si ruido, −5% si sigilo. Si ocurre → nuevo encuentro (06).
- **Elemento oculto extra:** 8% si el lugar es complejo (aumentado por PER).
- **Fallo con consecuencia (pifia, tirada ≥ 96):** ruido, herida leve, objeto dañado o alerta de testigos.

## EXCLUSIVIDAD DE DESCUBRIMIENTO DE UBICACIONES
- Categorías F y G solo si la ubicación tiene conexiones por descubrir (bloque 07). Antes de crear algo nuevo, verificar que no exista ya. No crear ubicación cada vez que se busca sin resultados.
- F: revela una conexión oculta ya definida o la crea y la registra (estado "libre" o "bloqueada" con causa).
- G: la ubicación pasa a "detectada" (indicio) o "descubierta" si se la ve claramente.

## BÚSQUEDA CON BONUS (PER y habilidad Búsqueda)
Añadir al paso 1: +1% por cada punto de PER sobre 5 al "Hallazgo relevante" (reduciendo "Nada"). Herramientas (linterna de noche, detector) suman +5%.

## PERSISTENCIA
- Lo encontrado se vuelve elemento/objeto con ID y se guarda. Lo recogido se elimina de la escena.
- No regenerar objetos por buscar de nuevo. Recursos renovables (plantas, agua) regeneran según tiempo (bloque 11).
- Registrar en LOG: `d2 15:10 | L-014 | BUSCAR explor 1→2 | hallazgo C-004 caja`.

## SALIDA DE LA BÚSQUEDA (plantilla)
```
🎲 Buscar (explor 1): tirada 28 ≤ 35 → HALLAZGO RELEVANTE
🎲 Tipo: 63 → C. Contenedor
Encuentras: [Caja metálica oxidada] (C-004) — cerrada
🎲 Peligro: 74 / ≤10 → nada
```
