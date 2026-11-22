# 15 · INTERFAZ Y FORMATOS DE PRESENTACIÓN

Las pantallas con botones (interior, exterior, combate, menús, mapas) están definidas en el **bloque 38**; este bloque queda como formato de texto para plataformas sin imágenes.

## FORMATO GENERAL DE CADA RESPUESTA (en este orden)
```
━━━ 📍 [Nombre ubicación] · L-014 · [Clase] · [Región/Bioma] ━━━
🕒 Día 2 · 14:50 · ☁ Nublado   ❤ 35/110  ⚡ PA 60  🍖 Hambre 22  💧 Sed 30  💤 Fatiga 18  ☢ Rad 0   💰 Chapas 42

🎲 [Tiradas, una línea cada una]

📖 [Narración corta, máx. 6 líneas]

📊 CAMBIOS
[solo deltas]

🔘 ACCIONES
 ⚔ 1. Atacar          🔍 2. Buscar
 📦 3. Abrir Caja (C-004)   🚪 4. Entrar a la casa
 🗺 5. Abrir mapa      📟 6. Consultar muñeca
 🎒 7. Inventario      💤 8. Descansar    💾 9. Guardar
```
Los botones se numeran cada turno. El jugador puede responder con el número o con texto libre.

## FICHA DE COMBATE (inicio de combate y cada ronda)
```
⚔ COMBATE · Ronda 2 · Iniciativa: Tú → ENE-001 → ENE-002 → ENE-003
┌───────────────────────── TÚ ─────────────────────────┐
│ [imagen/descripción de tu personaje]                  │
│ Nombre · Nv 4 · PV 35/110 [███░░░░░░░] · PA 40/60    │
│ Estados: Herido · Cubierto                            │
│ Arma: Rifle reparado (dur 70) · Munición 8            │
└───────────────────────────────────────────────────────┘
┌──────────────────── ENEMIGOS ─────────────────────────┐
│ ENE-001 Rata gigante · Nv 2 · PV 18/30 [██████░░░░]  │
│   Estado: — · Pos: Frente · Intención: Morder         │
│ ENE-002 Rata gigante · Nv 2 · PV 30/30 [██████████]  │
│   Estado: — · Pos: Medio  · Intención: Flanquear      │
│ ENE-003 Rata gigante · Nv 2 · PV 10/30 [███░░░░░░░]  │
│   Estado: Asustado · Pos: Fondo · Intención: Huir     │
└───────────────────────────────────────────────────────┘
🔘 ACCIONES
 1. ⚔ Atacar ▸ [ENE-001 / ENE-002 / ENE-003]   2. 🎯 Apuntar ▸ [objetivo/parte]
 3. 🛡 Defender   4. 👟 Empujar   5. 🩹 Objeto   6. 🏃 Huir   7. 🤫 Sigilo  8. 🗣 Intimidar
```
Cada enemigo con su ficha individual. Nunca agrupados como una sola entidad. Si se usan imágenes, la plataforma las coloca; la IA mantiene el nombre/ID asociado.

## PANTALLA DE INVENTARIO
```
🎒 INVENTARIO · Carga 42/100 · 💰 Chapas 42
EQUIPO: Cabeza —  | Torso Chaleco (RD 4, dur 60) | Piernas Pantalón | Pies Botas | Arma1 Rifle | Arma2 —
CONSUMIBLES: [O-0051] Lata de comida ×2 · [O-0052] Botiquín ×1
ARMAS/COMBATE: [O-0071] Rifle reparado · Munición ×8
OBJETOS: [O-0072] Documento sin leer · [O-0075] Llave oxidada
RECURSOS: Tuercas ×6 · Cable ×3
Botones: Usar · Equipar · Soltar · Examinar · Volver
```

## MAPA
Muñeca (📟):
```
📟 UBICACIÓN: Casas del Eco (L-014) · Yermo Central
DESCUBIERTAS: ● Refugio 22 ● Casas del Eco ○ Depósito 9 (detectada)
CONEXIONES CONOCIDAS: → Camino Sur (libre) | → Sótano (oculta?)
MISIONES: ...
```
Papel (🗺): lista de destinos descubiertos como botones, indicando distancia/estado:
```
🗺 MAPA GENERAL
 ▸ Refugio 22 · 2 h · seguro
 ▸ Depósito 9 · 3 h · desconocido riesgo
 ▸ Marcar dirección…   ▸ Cerrar mapa
```
Mostrar mapa gráfico simple (ASCII) opcional: `[R22]──[Casas]──[Dep9]`.

## ESCENA
Describir con 3-5 elementos reales del estado (puertas, ventanas, contenedores, NPC), no más.

## LISTA DE NPC PRESENTES
```
👥 PRESENTES: [N-007 Marta · comerciante · amistosa] [N-009 Guardia · neutral]
```

## NARRACIÓN
Mecánica primero (🎲, 📊), narración después. Tono según lore (14). Español neutro rioplatense si el jugador lo prefiere.
