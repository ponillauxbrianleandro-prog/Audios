# Audios
Repositorio para audios rioplatenses masculinos

## Estructura
- `episodio-00N-*/` — cada episodio: `guion.md`, `generar_audio.py` y `audio/` (mp3 por escena, completo y subtítulos `.srt`).
- `estilo-2d-3d/` — guía de estilo para ilustraciones 2D que parecen 3D (tipo GTA IV) y sus imágenes de referencia.

## Uso en cualquier sesión
El hook `.claude/hooks/session-start.sh` instala `ffmpeg` y las dependencias de `requirements.txt` (`edge-tts`) al iniciar una sesión en la nube.
Fuera de ahí: `pip install -r requirements.txt`, tener `ffmpeg` en el PATH y correr:

```
python3 episodio-002-pinguinos/generar_audio.py
```

Todo lo generado (audios y subtítulos) se guarda en el repo.
