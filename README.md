# Audios
Repositorio para audios rioplatenses masculinos

- [`ANIMALES_USADOS.md`](ANIMALES_USADOS.md): animales de los Shorts que ya se hicieron. Leerlo (y revisar `git branch -r`) antes de elegir uno nuevo, y agregar el nuevo al terminar.
- [`episodio-005-pudu/`](episodio-005-pudu/guion.md): short del pudú (guion, fuentes, voz clonada, tango y video 2D/2.5D de selva andina lluviosa).
- [`ESTILO_ARTISTICO.md`](ESTILO_ARTISTICO.md): Documento Maestro de dirección artística 2D. Fuente única de estilo.

## Herramientas de video en cualquier sesión

Las sesiones de este repo instalan solas las skills de Remotion, el
[claude-code-video-toolkit](https://github.com/digitalsamba/claude-code-video-toolkit)
(`/video`, `/setup`, etc.) y el marketplace `anthropics/skills`.

Para tenerlas en una sesión de otro repo, pegá esto en el chat:

> Ejecutá: `curl -fsSL https://raw.githubusercontent.com/ponillauxbrianleandro-prog/Audios/main/video_toolkit/install_global.sh | bash`
