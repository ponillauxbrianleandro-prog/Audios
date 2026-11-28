# GTA Art Engine — arte "GTA IV" por código (Blender + Three.js + PixiJS)

> **Para cualquier chat/agente que abra esta rama:** corré `./gta-art-engine/bootstrap.sh` y listo.
> **Prohibido** usar generadores de imagen por IA (Local Dream, Stable Diffusion, etc.). Todo se produce por código:
> modelo proxy → pasadas de render → pintor GLSL. El resultado es determinista y reproducible.

## Idea
No es 3D "de verdad" ni 2D plano: se esculpe un **modelo proxy** con la forma general (volumen real para que músculo,
pliegues y ropa den sombra y profundidad), se renderiza en **pasadas** (beauty, albedo, normal, profundidad, ID, AO) y un
**pintor** (PixiJS/GLSL) lo convierte en arte pintado: luz en bandas con borde de aerógrafo + salpicado de spray, textura
de piel (poros, vello, barba, rubor), textura de tela (trama/denim/cuero), contorno oscuro cálido (no negro),
luz de recorte cálida, perspectiva atmosférica, grano de lienzo y gradación estilo Rockstar.

## Los 3 bloques
| Bloque | Carpeta | Qué hace |
|---|---|---|
| 1. Blender + Python | `block1-blender/` | `sdf.py` (escultura por campos de distancia + marching cubes, fusión orgánica), `lib.py` (helpers bpy), `render_passes.py` (Cycles CPU, pasadas por override de material + meta de cámara) |
| 2. Three.js | `block2-three/` | `world.js` mundo procedural (skyline en capas, puente colgante, malecón, palmeras, gente, autos, botes, nubes, cielo de atardecer), `bg.js` pasadas del fondo (beauty/albedo/normal/profundidad log 16-bit), `render_bg.mjs` driver headless |
| 3. PixiJS | `block3-pixi/` | `painter.js` filtro GLSL: pinta fondo + personaje, compone, sombra de contacto/proyectada, gradación y grano. `paint.mjs` driver |

Personajes: `characters/<nombre>/` (`build.py` = modelo + poses + cámaras, `body_sdf.py` = anatomía/ropa SDF, `spec.json`).

## Uso
```bash
./gta-art-engine/bootstrap.sh              # instala bpy, three, pixi, playwright (1 vez)
cd gta-art-engine
make draft                                  # borrador ~1 min por pose
make all                                    # finales 3200x2000 -> out/vaquero-posing.png, out/vaquero-aiming.png
tools/run_pose.sh <pose> <W> <H> <samples> <voxel> <dir_trabajo>
python tools/compare.py out/vaquero-posing.png ref1.jpg -o work/compare.png   # revisión lado a lado
```
`voxel` = tamaño de voxel de la escultura SDF en metros (0.003 final, 0.005 borrador). Más chico = más detalle y más RAM/tiempo.

## Crear un personaje nuevo
1. Copiá `characters/vaquero-exotico/` → `characters/<nuevo>/`.
2. En `build.py`: editá `POSES` (articulaciones), materiales, accesorios (sombrero/arma por `revolve`, `rbox`, `ell`) y `CAMERAS`.
3. En `body_sdf.py`: la anatomía son primitivas SDF (`capsule`, `ellipsoid`, `ecapsule`, `box`, `custom`) con fusión suave `k`
   y modo `"sub"` para surcos. La ropa es una **cáscara** del volumen (`abs(d) - espesor`) con cortes (`"sub"`) y pliegues (`displace` ANTES de la cáscara).
4. `tools/run_pose.sh <pose> ...` y revisar visualmente.

Objetos/edificios/props: usar `lib.py` (`ell`, `rbox`, `revolve`, `mesh_from`, `skin`) o SDF; entornos: `block2-three/world.js`.
Si no hace falta 3D (fondos planos), usar capas 2D con profundidad en Pixi (mismo `painter.js`, pasando `depth`).

## Animación
Mismo pipeline por cuadro: variar `POSES` (o interpolar articulaciones) → `render_passes.py` → `paint.mjs`. El pintor usa ruido de
pantalla con semilla fija (`uSeed`); para animar sin "temblor" mantener la semilla y/o anclar ruido a UV de objeto.
Salida recomendada: sprite sheets + atlas JSON por pose/ciclo (pendiente de implementar: ver Roadmap).

## Checklist de calidad (no entregar sin cumplirlo)
- [ ] Sin look IA: manos/dedos coherentes, bordes limpios, nada "derretido".
- [ ] Volumen muscular legible (pectoral/abdomen/oblicuos/delts) con luz de recorte.
- [ ] Texturas visibles: piel (poros/vello/barba), tela (trama, estampado), denim, cuero.
- [ ] Fondo vivo con profundidad: capas, bruma, gente, autos, vegetación.
- [ ] Comparado lado a lado con las referencias de Rockstar (`tools/compare.py`).

## Lecciones técnicas (para no repetir errores)
- `Field.ecapsule` necesita tapas elipsoidales (sin ellas queda un cilindro infinito recortado por la caja = "losa").
- Cáscara de tela: espesor ≥ 1.15·voxel y aplicar `displace` antes de `abs(d)-espesor`, o se rompe en astillas.
- Cortes con modo `"sub"`: el SDF debe ser **negativo adentro** de la zona a quitar.
- Pixi v8: texturas con `PIXI.ImageSource`; el UV del filtro hay que corregirlo con `uv = vTextureCoord * uInputSize.xy / uOutputFrame.zw` (el pool es potencia de 2).
- Blender 5: no existe `OPEN_EXR_MULTILAYER`; las pasadas se renderizan por override de material (emisión) a PNG 16 bit.

## Roadmap
- Sprite sheets/atlas y ciclos de animación (idle, caminar, apuntar).
- Más personajes/props/edificios con el mismo SDF; paleta por escena (campo/desierto/ciudad).
- Cara más detallada (ojos/boca esculpidos) y manos con dedos articulados.
