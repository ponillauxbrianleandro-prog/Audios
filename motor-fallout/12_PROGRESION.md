# 12 · PROGRESIÓN: STATS, HABILIDADES, NIVEL, PERKS, KARMA

## STATS (1-10, se reparten al inicio; los define el jugador/16)
FUE (daño melé, carga, forzar) · PER (puntería, detectar, buscar) · RES (PV, resistencias) · CAR (diálogo, precios) · INT (puntos de habilidad, ciencia) · AGI (PA, sigilo, huida, iniciativa) · SUE (críticos, rareza de botín).
Bonus_stat = (stat − 5). Se usa en las fórmulas de 04/05/06/09.

## HABILIDADES (0-100)
Armas de fuego/distancia · Armas cuerpo a cuerpo · Desarmado · Sigilo · Cerraduras · Ciencia/Hackeo · Reparar · Medicina · Habla · Supervivencia · Trueque · Búsqueda.
Inicio: `15 + 2×stat relacionada` (+ 3 por etiquetadas). El lore puede cambiar nombres y agregar (magia, entrenamiento, captura...).

## NIVEL Y XP
XP necesaria para nivel N+1: `100 × N`. Nivel máx. 30 (ampliable por DLC).
Fuentes de XP: derrotar enemigo (06), completar misión (50-300), descubrir ubicación (15), abrir cerradura difícil (10-30), hackear (10-30), curar/reparar (5-15), diálogo clave (10-40).
Al subir: +PV (RES/2 + 5), +10 + INT puntos de habilidad a repartir (máx. 100 cada una), cada 2 niveles un perk.

## PERKS (se eligen al subir; lore aporta lista final)
Formato: `Nombre | requisito | efecto`. Ejemplos genéricos: Ojo de lince (PER 6: +10% impacto distancia) · Manos de seda (AGI 6: +15% cerraduras) · Regateador (CAR 5: precios −10%) · Cuerpo de acero (RES 6: +20 PV) · Rastreador (PER 5, Superv. 40: +15% buscar rastros) · Ladrón (Sigilo 50: −20% detección) · Cirujano (Medicina 50: curación ×1.5) · Carga extra (FUE 5: +30 carga).
Un perk no se repite salvo que diga "apilable".

## KARMA Y REPUTACIÓN
- **Karma** (−1000..+1000): + por ayudar, salvar, cumplir; − por robar, matar inocentes, traicionar. Se muestra como: Malvado/Maldad/Neutral/Bondad/Santo. Afecta diálogos y compañeros.
- **Reputación por facción/región** (−100..+100): afecta precios, acceso, hostilidad. Se guarda en [FLAGS].
- Conducta: matar a un NPC pacífico −50 karma; ayuda importante +30; robar sin ser visto −2; con testigos −10.

## CRECIMIENTO DE ENEMIGOS
El nivel de amenaza escala con el nivel del jugador (08) por regiones (cada región tiene rango mínimo/máximo). Zonas avanzadas aumentan la dificultad base.

## DIFICULTAD
Fácil (muerte 0%, −10% daño recibido) · Normal · Difícil (muerte 40%, +15% daño enemigo, −25% botín). Se fija en 16.
