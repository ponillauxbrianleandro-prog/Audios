import { BEATS } from './src/timeline';
let out = '# Procynosuchus v5 — texto usado en los primeros minutos\n\nGenerado desde `src/timeline.tsx`. El gancho (primeras 7 líneas) está adaptado; el resto es el guion original sin cambios. `(sin voz)` marca tramos solo de imagen.\n\n';
BEATS.forEach((b) => { out += (b.txt || '(sin voz)') + '\n\n'; });
require('fs').writeFileSync('guion_v5_primeros_minutos.md', out);
