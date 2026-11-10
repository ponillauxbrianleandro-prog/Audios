# Audios

Generador automático de narraciones (MP3) para videos cortos, con voces
masculinas rioplatenses de [edge-tts](https://github.com/rany2/edge-tts).

edge-tts usa el servicio de voz online de Microsoft Edge: no descarga modelos
ni necesita GPU o clave de API. Solo requiere conexión a internet.

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
# Comprobar que el servicio de voz responde y que las voces existen
python narrador.py --comprobar

# Ver voces y modos disponibles
python narrador.py --listar

# Narrar todos los guiones (.txt) de GUIONES/ con la voz y el modo por defecto
python narrador.py

# Elegir voz, modo y guiones concretos (archivos o carpetas)
python narrador.py --voz mateo --modo shorts GUIONES/ejemplo_01_bienvenida.txt

# Cada guion con las dos voces, más subtítulos .srt
python narrador.py --voz todas --subtitulos

# Guion directo desde la línea de comandos
python narrador.py --texto "Hola a todos" --nombre saludo --modo energico
```

### Voces

Solo voces masculinas rioplatenses (son las únicas que ofrece el servicio):

| `--voz` | Voz | País |
|---|---|---|
| `tomas` (por defecto) | `es-AR-TomasNeural` | Argentina |
| `mateo` | `es-UY-MateoNeural` | Uruguay |
| `todas` | genera cada guion con ambas | |

### Modos de audio

| `--modo` | Uso | Velocidad | Tono | Volumen |
|---|---|---|---|---|
| `neutral` (por defecto) | narración estándar | +0% | +0Hz | +0% |
| `shorts` | ritmo ágil para Reels/Shorts/TikTok | +12% | +0Hz | +0% |
| `energico` | gancho / llamada a la acción | +18% | +4Hz | +10% |
| `pausado` | explicativo, tutorial | -10% | +0Hz | +0% |
| `grave` | documental / dramático | -6% | -8Hz | +0% |
| `suave` | relato íntimo, calmo | -8% | -2Hz | -10% |

Estas voces no tienen estilos ni emociones en el servicio; los modos combinan
velocidad, tono y volumen. Para ajustar fino, `--velocidad`, `--tono` y
`--volumen` pisan el valor del modo (p. ej. `--modo shorts --velocidad +20%`).

### Otras opciones

| Opción | Descripción |
|---|---|
| `--subtitulos` | Guarda un `.srt` sincronizado junto a cada MP3 |
| `--palabras-por-linea N` | Palabras por subtítulo (por defecto 4; 1 = palabra por palabra) |
| `--salida CARPETA` | Otra carpeta de salida |
| `--sobrescribir` | Regenera los archivos que ya existen (por defecto se omiten) |

Al terminar cada audio se informa su duración en segundos, para controlar que
entre en el largo del video. Los subtítulos no llevan signos de puntuación
(el servicio entrega las marcas de tiempo palabra por palabra).

## Organización de archivos

- Los guiones van en `GUIONES/`, un `.txt` por narración (UTF-8). Conviene
  numerarlos (`01_intro.txt`, `02_dato.txt`…) para que se procesen en orden.
- Los audios se guardan en `OUTPUT/AUDIO/` como `<guion>_<voz>.mp3` en modo
  neutral y `<guion>_<voz>_<modo>.mp3` en los demás, por ejemplo
  `ejemplo_01_bienvenida_tomas.mp3` o `ejemplo_01_bienvenida_mateo_shorts.mp3`.
  El nombre se normaliza (minúsculas, sin acentos ni espacios), así que voces
  y modos distintos nunca se pisan. El `.srt` lleva el mismo nombre.
- Los MP3 y SRT generados no se suben al repositorio (ver `.gitignore`).

## Usar la voz en Cowork

La voz elegida para el proyecto es Tomás en modo neutral (los valores por
defecto). Para pasársela a Cowork como skill:

```bash
python empaquetar_skill.py   # genera OUTPUT/voz-tomas-argentina.zip
```

Subir ese `.zip` a Cowork como skill. Incluye las instrucciones
(`cowork/voz-tomas-argentina/SKILL.md`), una copia de `narrador.py` y
`requirements.txt`. El entorno de Cowork necesita salida a internet hacia
`speech.platform.bing.com`.

## Entornos con proxy HTTPS (Claude Code Cloud)

Si el entorno define `SSL_CERT_FILE` (o `REQUESTS_CA_BUNDLE`), `narrador.py`
agrega esos certificados raíz a los de edge-tts. No hace falta configurar nada.
