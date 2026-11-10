---
name: voz-tomas-argentina
description: Genera narraciones en MP3 con la voz masculina argentina de Tomás (es-AR-TomasNeural, tono neutral) a partir de cualquier texto o guion. Usar cuando el usuario pida narrar, locutar, grabar o "pasar a audio" un texto o guion, o mencione "la voz de Tomás", "la voz argentina", "la voz rioplatense" o "la voz del proyecto", incluso si no nombra este skill.
---

# Voz de Tomás (argentina, neutral)

Esta es la voz elegida por el usuario para sus videos cortos. No es un archivo
de audio: es la voz `es-AR-TomasNeural` del servicio online de Microsoft Edge,
que se invoca con el script incluido. Cada texto que se le pasa devuelve un MP3
con esa misma voz.

## Preparación (una vez por sesión)

```bash
pip install -r requirements.txt        # instala edge-tts; no descarga modelos
python scripts/narrador.py --comprobar # verifica la conexión con el servicio
```

Las rutas son relativas a la carpeta de este skill.

## Generar una narración

Pasar siempre `--salida` con la carpeta donde el usuario espera sus archivos
(si no, el audio queda dentro de la carpeta del skill).

```bash
# Desde un texto
python scripts/narrador.py --salida CARPETA --nombre NOMBRE --texto "Texto a narrar"

# Desde uno o varios archivos .txt, o una carpeta de guiones
python scripts/narrador.py --salida CARPETA guion1.txt guion2.txt
python scripts/narrador.py --salida CARPETA carpeta_de_guiones/
```

El resultado es `CARPETA/<nombre>_tomas.mp3`. El script informa la duración de
cada audio; entregar el archivo al usuario y mencionar la duración.

## La voz no se toca

El usuario eligió esta configuración exacta después de comparar variantes:

- Voz: `tomas` (`es-AR-TomasNeural`), que ya es la opción por defecto.
- Modo: `neutral` (velocidad +0%, tono +0Hz, volumen +0%), también por defecto.

Por eso, no pasar `--voz`, `--modo`, `--velocidad`, `--tono` ni `--volumen`
salvo que el usuario lo pida explícitamente. Tampoco aplicar filtros ni
masterizado al MP3: prefirió la versión sin retoques.

## Opciones a pedido

| Pedido del usuario | Opción |
|---|---|
| Subtítulos sincronizados | `--subtitulos` (guarda un `.srt` junto al MP3; `--palabras-por-linea N`, por defecto 4) |
| Otro ritmo o carácter | `--modo shorts`, `energico`, `pausado`, `grave` o `suave` (ver `--listar`) |
| Regenerar un audio que ya existe | `--sobrescribir` (por defecto se omite) |

## Texto para que suene bien

La entonación sale de la puntuación, así que conviene cuidarla antes de narrar:
comas y puntos donde haya pausas, signos de pregunta y exclamación de apertura
y cierre, y números o siglas escritos como deben leerse si la lectura es
ambigua. No reescribir el contenido del guion del usuario; solo proponer estos
ajustes si el resultado suena mal.

## Si algo falla

El script necesita salida a internet hacia `speech.platform.bing.com`. Si
`--comprobar` o la generación fallan, informar al usuario el error tal cual y
que hay que habilitar ese host en la red del entorno. No sustituir por otra voz
ni por otro motor de voz, y no entregar un audio que no sea de Tomás.
