#!/usr/bin/env node
// Graba una escena del mundo a MP4 sin guardar frames en disco (pipe -> ffmpeg).
// Uso: node grabar.mjs <escena.json relativo a mundo/> <salida.mp4> [--fps 30] [--ancho 1920] [--crf 20] [--audio audio.mp3]
// El MP4 contiene solo pixeles: pesa MB, no GB. Los assets/escenas viven aparte.
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path'; import { spawn } from 'node:child_process'; import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const RAIZ = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const a = process.argv.slice(2);
const escena = a[0], salida = path.resolve(a[1] || 'salida.mp4');
const opt = (n, d) => { const i = a.indexOf('--' + n); return i > -1 ? a[i + 1] : d; };
const crf = opt('crf', '20'), audio = opt('audio', null);
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml' };
const srv = http.createServer((req, res) => {
  const p = path.join(RAIZ, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(RAIZ) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' }); fs.createReadStream(p).pipe(res);
}).listen(0);
const port = srv.address().port;
const br = await chromium.launch(); const pg = await br.newPage({ viewport: { width: 1920, height: 1080 } });
pg.on('pageerror', e => console.error('ERROR PAGINA', e.message));
await pg.goto(`http://localhost:${port}/app/index.html?modo=grabar&escena=${encodeURIComponent(escena)}`);
await pg.waitForFunction('window.__listo === true');
const dur = await pg.evaluate('window.__duracion'), fps = +opt('fps', await pg.evaluate('window.__fps'));
const aud = await pg.evaluate('window.__auditoria');
aud.forEach(w => console.warn('AUDITORIA: ' + w));
const total = Math.round(dur * fps);
const args = ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-'];
if (audio) args.push('-i', path.resolve(audio));
args.push('-c:v', 'libx264', '-preset', 'slow', '-crf', crf, '-pix_fmt', 'yuv420p', '-movflags', '+faststart');
if (audio) args.push('-c:a', 'aac', '-b:a', '160k', '-shortest');
args.push(salida);
const ff = spawn('ffmpeg', args, { stdio: ['pipe', 'inherit', 'inherit'] });
for (let i = 0; i < total; i++) {
  await pg.evaluate(t => window.renderAt(t), i / fps);
  const buf = await pg.screenshot({ type: 'jpeg', quality: 95 });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % 60 === 0) process.stdout.write(`\r${i}/${total}`);
}
ff.stdin.end(); await new Promise(r => ff.on('close', r));
await br.close(); srv.close();
const mb = fs.statSync(salida).size / 1048576;
console.log(`\nlisto: ${salida} · ${dur}s · ${mb.toFixed(2)} MB · ${(mb / (dur / 60)).toFixed(1)} MB/min`);
