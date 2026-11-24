// Genera las imagenes que usa el PDF: hojas de assets y fotogramas de la demo.
import fs from 'node:fs'; import path from 'node:path'; import http from 'node:http'; import { fileURLToPath } from 'node:url'; import { createRequire } from 'node:module';
const require = createRequire(import.meta.url); const { chromium } = require('playwright');
const RAIZ = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'); const OUT = path.resolve(RAIZ, '../doc/img');
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml' };
const srv = http.createServer((q, s) => { const p = path.join(RAIZ, decodeURIComponent(q.url.split('?')[0])); if (!fs.existsSync(p) || fs.statSync(p).isDirectory()) { s.writeHead(404); return s.end(); } s.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'x' }); fs.createReadStream(p).pipe(s); }).listen(0);
const base = `http://localhost:${srv.address().port}`;
const cat = JSON.parse(fs.readFileSync(path.join(RAIZ, 'catalogo.json'))).assets;
const br = await chromium.launch(); const pg = await br.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 1 });
const grupos = { exterior: ['exterior'], interior: ['interior'], naturaleza_basura: ['naturaleza', 'basura', 'suelos'], personajes_props: ['personajes', 'mascota', 'props', 'efectos'] };
for (const [nombre, cats] of Object.entries(grupos)) {
  const items = cat.filter(a => cats.includes(a.cat) && !a.id.startsWith('silueta'));
  const html = `<body style="margin:0;background:#cfd6d4;font:12px sans-serif"><div style="display:flex;flex-wrap:wrap;gap:10px;padding:12px">` +
    items.map(a => `<div style="background:#e9ecea;border:1px solid #9aa;padding:6px;width:${a.cat === 'suelos' ? 380 : 190}px;height:150px;display:flex;flex-direction:column;align-items:center;justify-content:flex-end"><img src="${base}/${a.archivo}" style="max-width:100%;max-height:118px;object-fit:contain;margin-top:auto"><div style="margin-top:4px;color:#234">${a.id}</div></div>`).join('') + '</div></body>';
  await pg.setContent(html); await pg.waitForTimeout(600);
  await pg.screenshot({ path: `${OUT}/hoja_${nombre}.png`, fullPage: true });
}
await pg.setViewport?.({ width: 1920, height: 1080 }); await pg.setViewportSize({ width: 1920, height: 1080 });
await pg.goto(`${base}/app/index.html?modo=grabar`); await pg.waitForFunction('window.__listo===true');
for (const [n, t] of [['intro', 2], ['callejon', 6], ['mascota', 10.4]]) { await pg.evaluate(t => window.renderAt(t), t); await pg.screenshot({ path: `${OUT}/demo_${n}.png` }); }
await br.close(); srv.close(); console.log('capturas listas');
