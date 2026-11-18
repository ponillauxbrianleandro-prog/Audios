# Traspaso — Documental «Gorgonops torvus» (v6)

## Qué es
Documental científico 2D «realista» de ~20,9 min sobre *Gorgonops torvus* (Pérmico tardío, Karoo). Giro honesto: los gorgonópsidos son parientes de los mamíferos y su linaje se extinguió ~252 Ma; los herederos fueron cinodontes pequeños (*Procynosuchus*). 1920×1080, 24 fps, subtítulos, tango instrumental, voz de narrador. Apertura y créditos con diseño plano «Sombra» (fondo rojo azulado, siluetas negras, texto blanco, libreta y lapicera).

## Estado actual
- 124 planos renderizados (`video/segmentos/`, no versionados), 8 capítulos, voz diseñada (no clonada de ninguna persona real), sincronía auditada (±0,12 s por capítulo), −16 LUFS, sin solapes.
- Pausa conocida: 3 pausas de 2,9 s en la última escena (intencionales, con música).
- El usuario no confirmó aún que le guste la voz v6 (más/menos grave, más cálida, más rápida: se puede ajustar).

## Ver sin los videos pesados
`previa/hoja-contactos.jpg` (48 cuadros con tiempo), `previa/gorgonops-previa-360p.mp4`, `previa/gorgonops-completo.srt`, `guion.md`, `fuentes.md`.

## Mapa
- `render/documental.py`: tabla de escenas `build()`, `timeline()`, `--seg/--assemble/--tiempos/--srt/--preview`.
- `render/{engine,world,plants,biomes,creature,sombra,guion_extra}.py`: motor 2D, flora, biomas, criatura, diseño Sombra, narración extra e intro.
- `render/sonido.py`: arreglista de tango + mezcla + −16 LUFS; `render/ajustar_voz.py`; `render/auditar_*.py`.
- `voice_ai/`: TTS Qwen3 (`narrar_v6.py`, `procesar_voz.py`, `diseno_voz.py`, `limpiar.py`), `duraciones*.json`, `planos_congelados.json`, `objetivos_T.json`, `cache_activa.txt` (modelos y caches no versionados).
- `musica/`: generador de tango.

## Regenerar
1. Voz: `voice_ai/narrar_v6.py` → `procesar_voz.py` (con `CONGELAR=1`) → `render/ajustar_voz.py`.
2. Audio: `render/final_v6b.sh` (sonido → assemble → auditorías).
3. Video: `python render/documental.py --seg` (reanudable) y `--assemble`.

## Reglas acordadas
- No clonar ni imitar voces de personas reales sin su permiso (se rechazó clonar a Héctor Rossi y a otros).
- Usuario: español rioplatense; modo plan siempre activo; subtítulos pequeños y abajo; nunca pausas largas; voz estable con variación mínima.
- Commit/push solo a `claude/paleozoic-documentary-2d-l51hrn`; sin PR salvo pedido; no incluir datos personales en servicios externos.

## Entornos / trampas
Contenedor se reinicia y mata procesos de fondo (los scripts son reanudables); disco ajustado (~4 GB libres; borrar con rutas explícitas); TTS en CPU ~1,6 min por línea; `ffmpeg -ss` antes de `-i` con subtítulos no muestra texto.
