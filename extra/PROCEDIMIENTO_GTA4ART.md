# Procedimiento completo: arte estilo 80 % GTA IV pintado + 20 % realismo GTA VI (sin GPU)

Este documento guarda **todo el procedimiento** seguido (qué se intentó, qué falló, qué funcionó y cómo repetirlo). No contiene imágenes de referencia.

## 0. Objetivo y reglas del canal
- Estilo: **80 % arte promocional de GTA IV** (pintura digital, planos de luz duros, sombras frías azul-verdosas, fondo lavado casi blanco con sujeto saturado, casi sin contorno negro) + **20 % realismo tipo GTA VI** (poros de piel, textura de tela, luz de sol dura, profundidad de campo). Con sensación de volumen "casi 3D".
- Personajes propios (no personajes de Rockstar salvo que el video hable de sus juegos). Mascota: pistola 10mm de Fallout 3.
- **Regla de peso:** se graba la animación; nunca se exporta el mundo. Un video largo ≈ 100 MB (tope 400 MB).

## 1. Qué NO funcionó (para no repetirlo)
| Intento | Resultado | Por qué falló |
|---|---|---|
| Ilustraciones SVG por código (v1–v3) | Vectorial, plano, "no se parece en nada" | El arte pintado de GTA IV no se puede dibujar con formas geométricas; añadir texturas fotográficas CC0 no cambia el lenguaje visual |
| Personaje esculpido con SDF + shader en WebGL (v4) | Maniquí 3D tosco | Rostro y manos convincentes por código son inviables; el 3D "de plástico" es justo lo que no se quería |
| SD1.5 + IP-Adapter con referencia | Se copia al personaje de la referencia (ip=0.7) o queda caricatura (ip=0.35) | Modelo base viejo: manos/rostro flojos |
| SD1.5 + LoRA propio + ControlNet (v6) | Estilo plano, tira a GTA V; sirve para pruebas y poses | Techo del modelo base |
**Lección:** para igualar el arte hace falta un **modelo generativo moderno + LoRA de estilo**, no dibujar por código.

## 2. Ingeniería inversa del estilo (medido)
Script `extra/estilo/analizar_referencias.py` sobre las ilustraciones de referencia:
- Saturación centro (sujeto) vs bordes (fondo): ratio medio ≈ **2,2×**, hasta 3–5× en retratos con fondo lavado → regla "fondo descolorido, sujeto con color".
- ~15 niveles tonales activos (transiciones suaves, no 3 bandas de dibujo animado).
- Densidad de borde interno baja y casi sin línea negra de contorno; los bordes los define el cambio de plano de luz.
- Sombras de tono frío (azul-verdoso) y luces cálidas; luz principal lateral dura.
- Composición: encuadres cinematográficos (contrapicado, diagonales), primer plano que enmarca, fondos urbanos (puente, escaleras de incendio, ladrillo, almacén) con perspectiva marcada.
Guardar solo las **mediciones** (`estilo_gta4.json`), no las imágenes.

## 3. Pila de herramientas (todo instalable sin GPU)
| Pieza | Para qué | Dónde |
|---|---|---|
| `stable-diffusion.cpp` (compilado con cmake/ninja) | Correr **Flux.1-schnell** cuantizado en CPU | `/root/ia/sdcpp/build/bin/{sd-cli,sd-server}` |
| Flux.1-schnell Q4_K_S + T5xxl Q4_K_M + CLIP-L + VAE `ae` | Modelo base de imagen (Apache-2.0) | `/root/ia/models` (HF: city96, comfyanonymous, Comfy-Org espejo del VAE) |
| LoRA Flux "GTA IV vibe" (80 %) + "GTA VI loading screen" (20 %) | Estilo | HF `Muapi/...` (civitai exige login: no usar) |
| `diffusers` + SD1.5 + LCM-LoRA + IP-Adapter + ControlNet openpose | Ruta rápida/pose (≈ 1,5 min/imagen) | `/root/ia/venv` |
| LoRA propio SD1.5 entrenado con las referencias | Estilo propio para la ruta SD1.5 | `extra/estilo/gta4_style_lora/` |
| `rembg` | Recortes sin fondo para animar | `/root/ia/venv/bin/rembg` |
| Playwright + ffmpeg | Grabar la animación (MP4 liviano) | `extra/mundo/herramientas/grabar.mjs` |
Instalación completa e idempotente: `bash extra/herramientas_ia/arrancar.sh [--servidor]`.

## 4. Cómo generar (ruta recomendada: Flux)
1. `bash extra/herramientas_ia/arrancar.sh --servidor` (primera vez ~20–40 min de compilación y descargas; el servidor carga en ~5 min y mantiene los modelos en RAM).
2. `python3 extra/herramientas_ia/flux_gen.py salida.png "<prompt> <lora:lora_gta4_vibe_flux:0.8><lora:lora_gta6_loading_flux:0.2>" --seed 7`
3. Tiempos medidos (4 CPU, 512×768, 4 pasos): carga ~5 min (solo la primera vez en el servidor), muestreo ≈ 7 min, decodificación VAE ≈ 50 s → **≈ 8 min por imagen**. Por eso se generan lotes en segundo plano (`lote_flux.py`, reanudable) y se monitorean.
4. Ficha de personaje → todo: `python3 extra/herramientas_ia/crear_personaje.py ficha.json` (plantilla en `personaje_plantilla.json`).

## 5. Anatomía del prompt (plantilla que funcionó)
```
[ESTILO]  gta4art painting, GTA IV loading screen artwork by Rockstar, painterly shading with hard cool teal shadow planes, soft painted edges, desaturated pale city background
[REALISMO 20 %]  subtle realistic skin pores and fabric texture, strong form lighting, depth of field
[PERSONAJE]  <edad/complexión/peinado/accesorios> + <vestuario prenda por prenda con color y material>
[ACCIÓN/POSE/EXPRESIÓN]  <qué hace, ángulo de cámara, expresión>
[LoRA]  <lora:lora_gta4_vibe_flux:0.8><lora:lora_gta6_loading_flux:0.2>
```
Biblioteca de detalles que controlan el estilo:
- **Rostro:** "hard shadow planes under the brow and cheekbone", "strong jaw", "intense gaze". **Manos:** nombrar los guantes y qué sostienen; si salen mal, regenerar con otra semilla o inpainting.
- **Ropa:** material + color + "painted folds"; translúcido: "sheer white t-shirt".
- **Fondo lavado:** "desaturated pale grey-white background, only the character has full color"; atardecer: "pink-orange sunset sky, river reflections".
- **Luz:** fría en sombras ("cool teal shadows"), cálida en luces ("warm key light"), "rim light".
- **Cámara:** "extreme low angle", "wide angle lens perspective", "waist-up medium shot", "extreme close-up portrait".
- **Ojo de pez / perspectiva exagerada:** "fisheye lens distortion" (o aplicarlo después en la animación).

## 6. Poses y expresiones
- Ruta Flux: se describen en el prompt (cantando, puño arriba, brazos abiertos, señalando, perfil, contrapicado, rodilla, de espaldas; expresiones: grito, sonrisa, ceño, guiño, "ooh"). La identidad se mantiene repitiendo la descripción exacta y la semilla base.
- Ruta SD1.5 (rápida): poses OpenPose definidas por código (`poses.py`) + ControlNet; expresiones por inpainting de la boca (`expresiones.py`); identidad con IP-Adapter y una imagen maestra.

## 7. LoRA propio (aprender el estilo)
`extra/herramientas_ia/entrenar_lora.py`: SD1.5, rango 16, 384 px, 400 pasos, lr 1e-4, ≈ 4–5,5 s/paso en CPU. Dataset: 8 ilustraciones con 2–3 recortes cuadrados cada una + espejo (48 muestras) y captions que empiezan con el disparador `gta4art style`. Guarda `estado.pt` cada 20 pasos y **reanuda solo** (el contenedor se reinicia y mata procesos). Salida 12 MB. Se ve el efecto con A/B sobre el mismo prompt/semilla.

## 8. Animación (después de generar)
Recortar con `rembg`, componer por capas con paralaje (motor en `extra/mundo/app`), cámara con FOV/ojo de pez, expresiones intercambiando versiones de la boca/cara, y **grabar a MP4** con `grabar.mjs` (`--workers`, `--rapido`). Verificar peso con `verificar_peso.py`.

## 9. Errores típicos y arreglos
- El contenedor se reinicia y mata procesos en segundo plano → scripts reanudables (`curl -C -`, `estado.pt`, lotes que saltan lo existente) y monitores.
- `sleep` encadenado está bloqueado → usar monitores (`until ...; do sleep; done`) o `run_in_background`.
- civitai devuelve HTML al descargar (requiere login) → usar espejos de Hugging Face.
- `ae.safetensors` oficial es gated → espejo `Comfy-Org/Lumina_Image_2.0_Repackaged`.
- Modo offline de diffusers exige `weight_name` explícito.
- `bash -c "while pgrep -f x ..."` se detecta a sí mismo → usar un PID o un archivo marcador.

## 10. Honestidad / límites
Sin GPU: ≈ 8 min por imagen Flux. El "3D" es sugerencia por luz y volumen. Igualar un artwork pintado a mano por Rockstar no está garantizado: siempre comparar lado a lado con las referencias y iterar (semillas, pesos de LoRA 0,6–1,0, prompts). Para saltar de nivel: GPU o API de imágenes.
