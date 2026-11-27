# Guía de estilo: ilustración 2D que parece 3D (look GTA IV)

Referencias en `referencias/`. La idea: dibujo plano, pintado a mano, con volumen suficiente como para que el personaje "salga" de la pantalla, sobre un fondo apagado que casi desaparece.

## 1. Los 7 rasgos del estilo

1. **Contraste de saturación.** Fondo casi monocromo (grises, blanco sucio, algún celeste lavado) y personaje con colores terrosos y saturados (marrón cuero, mostaza, verde oliva, piel cálida). El ojo va solo al personaje.
2. **Cel-shading pintado, no vectorial.** 3 tonos por material: luz, base, sombra (a veces un 4.º de reflejo). Los bordes entre tonos son duros pero algo irregulares, como pintura digital.
3. **Luz dura y direccional.** Una sola fuente clara (arriba y a un costado). Sombras proyectadas con forma definida (cuello bajo el mentón, pliegues de la campera, mano sobre el brazo).
4. **Contorno casi invisible.** Sin línea negra gruesa de cómic: el borde lo da el cambio de valor. Si hay línea, es fina, oscura-cálida y varía de grosor (más gruesa en la sombra, desaparece en la luz).
5. **Cámara dramática.** Contrapicado (desde abajo) o plano cerrado desde un ángulo incómodo (ref. 3: por la ventanilla). Anatomía algo exagerada: hombros anchos, manos grandes.
6. **Profundidad por capas.** Primer plano nítido y saturado → plano medio (puente, edificios) en gris medio → fondo en gris muy claro, casi blanco, con niebla. Cuanto más lejos, menos contraste y menos detalle.
7. **Textura sutil.** Poros, pliegues, trama de tela y brillo de metal pintados con pinceladas chicas, sin ruido fotográfico.

## 2. Cómo lograr la ilusión de 3D en una imagen plana

| Truco | Cómo se hace |
|---|---|
| Volumen | Sombra de forma (core shadow) en el lado opuesto a la luz y luz de rebote tenue en el borde de esa sombra. |
| Separación | Rim light fino y frío (celeste/blanco) en el contorno del lado de la sombra. |
| Oclusión | Oscurecer zonas de contacto: bajo el mentón, entre dedos, cuello de la campera. |
| Perspectiva | Líneas del fondo convergentes (el puente en ref. 1), horizonte bajo. |
| Atmósfera | Degradé a blanco hacia el fondo; el primer plano nunca se lava. |
| Escala | Elemento grande cortado por el borde del cuadro (volante y mano en ref. 3). |
| Superposición | Que el personaje tape y se solape con la arquitectura de fondo. |

## 3. Paleta base

- Fondo: `#F2F2F0`, `#D9DAD8`, `#A9ABAA`, `#6F7273` (grises ligeramente cálidos).
- Piel: luz `#E3A878`, base `#C47F55`, sombra `#7A4632`.
- Cuero / tela marrón: luz `#A5703A`, base `#6B4426`, sombra `#2E1D12`.
- Acento mostaza: `#C9A24B`. Verde oliva apagado: `#8A8F6B`. Azul noche (ropa deportiva): `#1F3248`.
- Regla: máximo 1 color saturado fuerte por imagen; el resto, tierra o gris.

## 4. Flujo de trabajo (pintura digital o generador)

1. Boceto de silueta fuerte, ángulo bajo y pose con gesto (señalar, ajustarse un guante).
2. Fondo primero: capas grises, luego niebla/blanco hacia atrás.
3. Base plana de color del personaje.
4. Una capa de sombras duras (multiplicar) con la luz decidida de antemano.
5. Una capa de luces y rim light (aditiva o `screen`).
6. Detalles: pliegues, costuras, brillos de metal, pelo mechón por mechón agrupado.
7. Contorno suave solo donde haga falta; ruido/grano mínimo al final.

## 5. Prompts base para generadores de imagen

**Positivo**
> stylized 2D digital painting, Grand Theft Auto IV loading screen art style, cel-shaded with hard-edged shadows, painterly texture, no heavy black outlines, saturated warm earthy character in the foreground, desaturated gray-white city background fading into fog, low-angle dramatic camera, single hard directional light, subtle cool rim light, strong silhouette, 16:9

**Negativo**
> photorealistic, 3D render, glossy plastic, thick black comic outlines, flat vector, anime, neon colors, busy colorful background, blurry face, extra fingers

Variantes: agregar `bridge at low angle` (ref. 1), `close-up through car window, badge in hand` (ref. 3) o `muscular arm flex, white t-shirt, gold chain` (ref. 2). Para el canal: reemplazar el personaje por los de RíoPuratense manteniendo luz, paleta y fondo desaturado.

## 6. Checklist antes de dar por terminada una imagen

- [ ] ¿El personaje es lo único con color fuerte?
- [ ] ¿Hay una sola dirección de luz coherente en todo el cuadro?
- [ ] ¿Las sombras tienen borde duro y 2–3 tonos como máximo?
- [ ] ¿El fondo se aclara y pierde detalle con la distancia?
- [ ] ¿Hay rim light o separación entre personaje y fondo?
- [ ] ¿Se lee la silueta en miniatura (64 px)?
- [ ] ¿No hay contorno negro grueso ni brillo "plástico"?

## 7. Errores comunes

- Degradés suaves en todo → se ve como render 3D barato. Usar bordes duros.
- Fondo con color y detalle → compite con el personaje.
- Varias fuentes de luz → se pierde el volumen.
- Línea negra uniforme → se ve cómic, no GTA IV.
- Piel anaranjada plana → sumar un tono de sombra marrón rojizo y un reflejo claro.
