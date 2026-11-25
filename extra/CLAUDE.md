# Extra — memoria del proyecto visual (leer antes de hacer animaciones)

Canal "Extra". Estilo: **ilustración 2D con profundidad inspirada en el arte de GTA IV**, tirando a realista (guiño a GTA VI), nunca 3D.
Guía completa: `extra/doc/Extra_Guia_Visual_v3.pdf` (regenerar con `python3 extra/doc/generar_pdf.py`).

## Reglas
- 2D con paralaje por capas; personajes con volumen, ropa con pliegues; luz con dirección; composición diagonal/asimétrica.
- **Color selectivo**: fondo descolorido (sat 10–25 %), sujeto con color; objetos de fondo de tono afín reciben algo de color (`afin: true`).
- **Ningún plano vacío**, el suelo siempre con textura/detalle (el motor audita: `Motor.auditar()`).
- Cada pedido del usuario → **agregar más assets** al mundo (árboles, estructuras, basura, props, fondos) y commitearlos.
- Largos: intro de **silueta-dentro-de-silueta** (3–5 s). Shorts: sin intro, temas curiosos, cortes rápidos.
- Mascota: **pistola 10mm de Fallout 3** (`mascota_pistola_10mm`, rig por partes) que entra a mitad del video. Anfitrión humano ochentero: `anfitrion_extra`.
- Ilustraciones propias inspiradas, no copias de arte de Rockstar/Bethesda. Si faltan referencias, pedir links/imágenes al usuario.

## REGLA DE PESO (crítica)
**Grabar la animación, no exportar el mundo.** El MP4 final debe pesar ~100 MB para un largo (tope 400 MB); un short, pocos MB.
Si pesa GBs, se hizo mal. Siempre correr `python3 extra/mundo/herramientas/verificar_peso.py video.mp4` y reportar el resultado.

## Uso del mundo (`extra/mundo/`)
- `assets/<cat>/*.svg` + `catalogo.json` (id, cat, tags, rol fondo|sujeto, ancla). Regenerar/ampliar: `python3 herramientas/generar_assets.py` (decorador `@asset`) o `agregar_asset.py` para un SVG propio.
- Escena = JSON (ver `ejemplos/demo_intro.json`, generado por `herramientas/crear_demo.py`): capas con `paralaje`, `de/hasta`, `mascara`; items `{asset,x,y,esc,rot,sat,afin,silueta,texto_editable}`; `anim` (props x,y,esc,rot,op,flip o `parte`+`pivote` para rigs); `camara`, `temblor`, `destellos`, `fundidos`, `tema` (gta4|vice|gta6|futbol en `paletas.json`).
  Los valores de `anim` son **desplazamientos** respecto de la posición base del item (escala/opacidad multiplican).
- Editor visual: servir `extra/mundo` (`python3 -m http.server -d extra/mundo`) y abrir `/app/index.html`.
- Grabar: `node extra/mundo/herramientas/grabar.mjs <escena.json> salida.mp4 [--audio narracion.mp3] [--fps 30] [--crf 20]` (Playwright + ffmpeg por pipe).
- Los SVG se inyectan inline con ids únicos por instancia (si se agrega código nuevo, no usar ids globales fuera de `url(#...)`).

## v3 — realismo cinematográfico (leer)
- Texturas CC0 pintadas en `mundo/texturas/*.webp` (`bajar_texturas.py` las regenera; créditos en `texturas/CREDITOS.json`). En SVG se usan como `<image href="@TEX/nombre.webp">` (el motor reemplaza `@TEX/`).
- Assets HD en `herramientas/assets_hd.py` y `assets_hd2.py` (mismos ids que v1; gana el último). Personajes: `persona_hd(...)` con rig `torso, brazo_i/d > antebrazo_i/d, cabeza, ojos (animar `escy` para parpadear), cejas, boca`.
- Motor: DoF por capa (`dof`, `foco` con rack focus), `mano` (cámara en mano), `luz`, grano animado, filtro `pintado`, sombras/rim light automáticos, `mezcla` por item (`screen` para luces), anim con `ruido` (idle orgánico) y eases `elastico|rebote|parpadeo`.
- Render lento (~1,6 s/cuadro/proceso): `grabar.mjs --workers 4`; borradores `--rapido --fps 24`. El peso del MP4 sigue siendo pequeño (demo 18 s = 6 MB).
- Cada pedido nuevo: sumar assets (HD, con textura + luz) y commitear.

## ESTADO v4 (IMPORTANTE)
- v1–v3 (SVG + texturas fotográficas) fueron rechazadas por el usuario: NO se parecen a GTA IV. No usar ese estilo para videos nuevos.
- v4 en curso (`extra/estilo/`, `extra/mundo3d/`): análisis de estilo (`estilo_gta4.json`: fondo ~3–5× menos saturado que el sujeto, sombras frías, ~15 niveles tonales suaves, casi sin contorno negro) y un cantante rockabilly esculpido por SDF en un shader WebGL (`motor/cantante.frag`, render con `herramientas/foto.mjs`).
- Resultado actual: maniquí 3D tosco (ver `ESTADO_hero_prueba.png`), NO es aún arte tipo GTA IV. No presentarlo como terminado.
