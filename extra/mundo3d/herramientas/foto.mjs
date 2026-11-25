// Renderiza una o varias vistas del cantante a PNG. Uso: node foto.mjs salida.png ancho alto '{"uJaw":.6,...}'
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url'; import { createRequire } from 'node:module';
const require = createRequire(import.meta.url); const { chromium } = require('playwright');
const RAIZ = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.frag': 'text/plain', '.json': 'application/json' };
const srv = http.createServer((q, s) => { const p = path.join(RAIZ, decodeURIComponent(q.url.split('?')[0])); if (!fs.existsSync(p) || fs.statSync(p).isDirectory()) { s.writeHead(404); return s.end(); } s.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'x' }); fs.createReadStream(p).pipe(s); }).listen(0);
const [out, W, H, P] = [process.argv[2], +process.argv[3], +process.argv[4], JSON.parse(process.argv[5] || '{}')];
const br = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const pg = await br.newPage({ viewport: { width: W, height: H } }); pg.on('pageerror', e => console.error('ERR', e.message)); pg.on('console', m => m.type() === 'error' && console.error(m.text()));
await pg.goto(`http://localhost:${srv.address().port}/motor/cantante.html`);
const t0 = Date.now(); await pg.evaluate(async ([W, H, P]) => { await iniciar(W, H); dibujar(P); }, [W, H, P]);
console.log('render ms', Date.now() - t0); await pg.locator('#c').screenshot({ path: out }); await br.close(); srv.close();
