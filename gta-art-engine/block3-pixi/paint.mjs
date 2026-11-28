// Driver del pintor: node paint.mjs <dir_pasadas_rel> <pose> <dir_bg_rel> <W> <H> <salida.png>
import { createRequire } from 'module'; const { chromium } = createRequire(import.meta.url)('playwright');
import http from 'http'; import fs from 'fs'; import path from 'path'; import { fileURLToPath } from 'url';
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const [,, dir, pose, bg, W, H, out] = process.argv;
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.png': 'image/png', '.json': 'application/json' };
const srv = http.createServer((req, res) => {
  const f = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(res);
}).listen(0);
const port = srv.address().port;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox'] });
const page = await browser.newPage({ viewport: { width: 800, height: 600 } });
page.on('console', m => { const t = m.text(); if (!t.includes('GL Driver')) console.log('[page]', t); }); page.on('pageerror', e => console.log('[pageerror]', e.message));
await page.goto(`http://localhost:${port}/block3-pixi/painter.html?w=${W}&h=${H}&dir=${encodeURIComponent(dir)}&pose=${pose}&bg=${encodeURIComponent(bg)}&dbg=${process.env.DBG||0}`);
await page.waitForFunction('window.__done === true', null, { timeout: 600000 });
const png = await page.evaluate(process.env.ALT ? 'window.__png2' : 'window.__png');
fs.mkdirSync(path.dirname(out), { recursive: true });
fs.writeFileSync(out, Buffer.from(png.split(',')[1], 'base64'));
await browser.close(); srv.close(); console.log('PAINT OK', out);
