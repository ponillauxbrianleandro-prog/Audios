#!/usr/bin/env node
// Graba una escena del mundo a MP4 sin guardar frames en disco (pipe -> ffmpeg).
// Uso: node grabar.mjs <escena.json relativo a mundo/> <salida.mp4> [--fps 30] [--ancho 1920] [--crf 20] [--audio audio.mp3] [--workers 3] [--rapido  (borrador: sin filtro pintado ni sombras, mucho mas veloz)]
// El MP4 contiene solo pixeles: pesa MB, no GB. Los assets/escenas viven aparte.
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path'; import { spawn } from 'node:child_process'; import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const RAIZ = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const a = process.argv.slice(2);
const escena = a[0], salida = path.resolve(a[1] || 'salida.mp4');
const opt = (n, d) => { const i = a.indexOf('--' + n); return i > -1 ? a[i + 1] : d; };
const crf = opt('crf', '21'), audio = opt('audio', null), workers = Math.max(1, +opt('workers', '3'));
import os from 'node:os';
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml' };
const srv = http.createServer((req, res) => {
  const p = path.join(RAIZ, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(RAIZ) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' }); fs.createReadStream(p).pipe(res);
}).listen(0);
const port = srv.address().port;
const br = await chromium.launch();
const url = `http://localhost:${port}/app/index.html?modo=grabar&escena=${encodeURIComponent(escena)}${a.includes('--rapido') ? '&rapido=1' : ''}`;
async function abrir() { const pg = await br.newPage({ viewport: { width: 1920, height: 1080 } }); pg.on('pageerror', e => console.error('ERROR PAGINA', e.message)); await pg.goto(url); await pg.waitForFunction('window.__listo === true'); return pg; }
const pg0 = await abrir();
const dur = await pg0.evaluate('window.__duracion'), fps = +opt('fps', await pg0.evaluate('window.__fps'));
(await pg0.evaluate('window.__auditoria')).forEach(w => console.warn('AUDITORIA: ' + w));
const total = Math.round(dur * fps);
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'extra-'));
const trozo = Math.ceil(total / workers);
let hechos = 0;
async function worker(k, pg) {   // cada worker graba un tramo a un mp4 temporal (los fotogramas pasan por pipe, nunca a disco)
  const a0 = k * trozo, a1 = Math.min(total, a0 + trozo); if (a0 >= a1) return null;
  const out = path.join(tmp, `seg${String(k).padStart(3, '0')}.mp4`);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', crf, '-pix_fmt', 'yuv420p', '-g', String(fps * 2), out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = a0; i < a1; i++) {
    await pg.evaluate(t => window.renderAt(t), i / fps);
    const buf = await pg.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (++hechos % 30 === 0) process.stdout.write(`\r${hechos}/${total}`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); return out;
}
const pages = [pg0]; for (let k = 1; k < workers; k++) pages.push(await abrir());
const segs = (await Promise.all(pages.map((pg, k) => worker(k, pg)))).filter(Boolean);
await br.close(); srv.close();
fs.writeFileSync(path.join(tmp, 'lista.txt'), segs.map(f => `file '${f}'`).join('\n'));
const cat = ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', path.join(tmp, 'lista.txt')];
if (audio) cat.push('-i', path.resolve(audio));
cat.push('-c:v', 'copy'); if (audio) cat.push('-c:a', 'aac', '-b:a', '160k', '-shortest'); cat.push('-movflags', '+faststart', salida);
await new Promise((res, rej) => spawn('ffmpeg', cat, { stdio: 'inherit' }).on('close', c => c ? rej(new Error('ffmpeg concat ' + c)) : res()));
fs.rmSync(tmp, { recursive: true, force: true });
const mb = fs.statSync(salida).size / 1048576;
console.log(`\nlisto: ${salida} · ${dur}s · ${mb.toFixed(2)} MB · ${(mb / (dur / 60)).toFixed(1)} MB/min`);
