// Driver: sirve el repo por HTTP, abre Chromium (SwiftShader) y guarda las pasadas del fondo.
import { createRequire } from 'module'; const { chromium } = createRequire(import.meta.url)('playwright');
import http from 'http'; import fs from 'fs'; import path from 'path'; import { fileURLToPath } from 'url';
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const [,, outDir, W = '1600', H = '1000', camJson, seed = '4'] = process.argv;
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.png': 'image/png', '.json': 'application/json' };
const srv = http.createServer((req, res) => {
  const f = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!f.startsWith(ROOT) || !fs.existsSync(f)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(res);
}).listen(0);
const port = srv.address().port;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox'] });
const page = await browser.newPage({ viewport: { width: 800, height: 600 } });
page.on('console', m => console.log('[page]', m.text())); page.on('pageerror', e => console.log('[pageerror]', e.message));
await page.goto(`http://localhost:${port}/block2-three/bg.html?w=${W}&h=${H}&seed=${seed}&cam=${encodeURIComponent(camJson)}`);
await page.waitForFunction('window.__done === true', null, { timeout: 600000 });
const out = await page.evaluate('window.__out');
fs.mkdirSync(outDir, { recursive: true });
for (const [k, v] of Object.entries(out)) fs.writeFileSync(path.join(outDir, `bg_${k}.png`), Buffer.from(v.split(',')[1], 'base64'));
await browser.close(); srv.close(); console.log('BG OK', outDir);
