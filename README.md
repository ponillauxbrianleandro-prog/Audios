# Audios

Generador automático de narraciones (MP3) para videos cortos, con voces
masculinas en español de [edge-tts](https://github.com/rany2/edge-tts).

edge-tts usa el servicio de voz online de Microsoft Edge: no descarga modelos
ni necesita GPU o clave de API. Solo requiere conexión a internet.

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
# 1. Comprobar que el servicio de voz responde y que las voces existen
python narrador.py --comprobar

# 2. Narrar todos los guiones (.txt) de GUIONES/ con la voz por defecto
python narrador.py

# 3. Elegir otra voz, y archivos o carpetas concretos
python narrador.py --voz tomas GUIONES/ejemplo_01_bienvenida.txt
python narrador.py --voz gonzalo GUIONES/ otra_carpeta/

# 4. Guion directo desde la línea de comandos
python narrador.py --texto "Hola a todos" --nombre saludo
```

### Voces

| Alias (`--voz`) | Voz | Acento |
|---|---|---|
| `jorge` (por defecto) | `es-MX-JorgeNeural` | México |
| `gonzalo` | `es-CO-GonzaloNeural` | Colombia |
| `tomas` | `es-AR-TomasNeural` | Argentina |

También se acepta el nombre completo de cualquier otra voz de edge-tts.

### Opciones

| Opción | Descripción |
|---|---|
| `--velocidad +10%` | Más rápido / más lento (`-10%`) |
| `--tono +5Hz` | Más agudo / más grave |
| `--volumen +20%` | Volumen |
| `--salida CARPETA` | Otra carpeta de salida |
| `--sobrescribir` | Regenera los MP3 que ya existen (por defecto se omiten) |

## Organización de archivos

- Los guiones van en `GUIONES/`, un `.txt` por narración (UTF-8). Conviene
  numerarlos (`01_intro.txt`, `02_dato.txt`…) para que se procesen en orden.
- Los audios se guardan en `OUTPUT/AUDIO/` como `<guion>_<voz>.mp3`, por
  ejemplo `ejemplo_01_bienvenida_jorge.mp3`. El nombre se normaliza
  (minúsculas, sin acentos ni espacios) y el mismo guion en distintas voces
  no se pisa.
- Los MP3 generados no se suben al repositorio (ver `.gitignore`).

## Entornos con proxy HTTPS (Claude Code Cloud)

Si el entorno define `SSL_CERT_FILE` (o `REQUESTS_CA_BUNDLE`), `narrador.py`
agrega esos certificados raíz a los de edge-tts. No hace falta configurar nada.
