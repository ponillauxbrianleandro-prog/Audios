import { flatten } from './src/timeline';
import { FPS } from './src/lib';
const { cuts, total } = flatten();
let bad = 0;
const mx = Math.max(...cuts.map((c) => c.dur / FPS));
cuts.forEach((c, i) => { const s = c.dur / FPS; if (s > 8 || (c.start / FPS < 23 && s > 2.5)) { bad++; console.log('LARGO', i, s.toFixed(2), c.txt); } });
console.log('cortes', cuts.length, 'total s', (total / FPS).toFixed(1), 'max s', mx.toFixed(2), 'promedio s', (total / FPS / cuts.length).toFixed(2), 'fuera de regla', bad);
console.log('MID ' + cuts.map((c) => Math.floor(c.start + c.dur * 0.55)).join(','));
