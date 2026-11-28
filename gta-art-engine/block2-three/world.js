// Bloque 2 — Three.js: mundo procedural (ciudad costera con puente, palmeras, agua, gente, autos).
// Construye en coordenadas "Blender" (Z arriba, cámara mira +Y) dentro de un grupo rotado a Y-up de Three.
import * as THREE from 'three';

function rng(seed) { let s = seed >>> 0; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }

function windowTex(rand, cols, rows, tone, warm) {
  const c = document.createElement('canvas'); c.width = 128; c.height = 256;
  const g = c.getContext('2d');
  g.fillStyle = tone; g.fillRect(0, 0, 128, 256);
  const cw = 128 / cols, rh = 256 / rows;
  for (let y = 0; y < rows; y++) for (let x = 0; x < cols; x++) {
    const lit = rand() < warm;
    g.fillStyle = lit ? `rgb(${220 + rand() * 30 | 0},${190 + rand() * 40 | 0},${120 + rand() * 40 | 0})`
                      : `rgb(${40 + rand() * 40 | 0},${60 + rand() * 40 | 0},${80 + rand() * 40 | 0})`;
    g.fillRect(x * cw + cw * 0.18, y * rh + rh * 0.2, cw * 0.64, rh * 0.6);
  }
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8; return t;
}

function building(rand, w, d, h, tones) {
  const g = new THREE.Group();
  const tone = tones[rand() * tones.length | 0];
  const cols = 4 + (rand() * 6 | 0), rows = Math.max(6, h / 3.6 | 0);
  const tex = windowTex(rand, cols, 16, tone, 0.22);
  tex.repeat.set(Math.max(1, w / 10 | 0), Math.max(1, h / 52));
  const m = new THREE.MeshStandardMaterial({ map: tex, roughness: 0.85, metalness: 0.0 });
  const box = new THREE.Mesh(new THREE.BoxGeometry(w, d, h), m);
  box.position.z = h / 2; box.castShadow = box.receiveShadow = true; g.add(box);
  // coronación escalonada / tanque de agua / antena
  const kind = rand();
  const cap = new THREE.MeshStandardMaterial({ color: new THREE.Color(tone).multiplyScalar(0.8), roughness: 0.9 });
  if (kind < 0.45) {
    const s = new THREE.Mesh(new THREE.BoxGeometry(w * 0.7, d * 0.7, h * 0.08), cap); s.position.z = h + h * 0.04; g.add(s);
    const s2 = new THREE.Mesh(new THREE.BoxGeometry(w * 0.4, d * 0.4, h * 0.08), cap); s2.position.z = h + h * 0.12; g.add(s2);
  } else if (kind < 0.7) {
    const sp = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.4, h * 0.25, 6), cap); sp.rotation.x = Math.PI / 2; sp.position.z = h + h * 0.12; g.add(sp);
  } else if (kind < 0.85) {
    const tank = new THREE.Mesh(new THREE.CylinderGeometry(w * 0.12, w * 0.12, w * 0.2, 12), new THREE.MeshStandardMaterial({ color: 0x6b4a32 }));
    tank.rotation.x = Math.PI / 2; tank.position.set(w * 0.2, 0, h + w * 0.14); g.add(tank);
  }
  return g;
}

function palm(rand, h, lean) {
  const g = new THREE.Group();
  const tm = new THREE.MeshStandardMaterial({ color: 0x8a7050, roughness: 0.95 });
  const pts = [];
  for (let i = 0; i <= 12; i++) { const t = i / 12; pts.push(new THREE.Vector3(lean * t * t * h * 0.25, 0, t * h)); }
  const curve = new THREE.CatmullRomCurve3(pts);
  const trunk = new THREE.Mesh(new THREE.TubeGeometry(curve, 24, h * 0.022, 8, false), tm); trunk.castShadow = true; g.add(trunk);
  const top = pts[pts.length - 1];
  const lm = new THREE.MeshStandardMaterial({ color: 0x3f6a34, roughness: 0.8, side: THREE.DoubleSide });
  const lm2 = new THREE.MeshStandardMaterial({ color: 0x57843c, roughness: 0.8, side: THREE.DoubleSide });
  const nF = 13;
  for (let k = 0; k < nF; k++) {
    const a = k / nF * Math.PI * 2 + rand() * 0.3;
    const L = h * (0.38 + rand() * 0.12);
    const shape = new THREE.PlaneGeometry(L, h * 0.10, 12, 1);
    const pos = shape.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i) + L / 2, s = x / L;
      pos.setZ(i, -s * s * L * 0.55 + (pos.getY(i) * pos.getY(i)) * 0.0);
      pos.setY(i, pos.getY(i) * Math.max(0, Math.sin(Math.PI * (0.1 + 0.9 * s))) ** 0.7);
      pos.setX(i, x);
    }
    shape.computeVertexNormals();
    const leaf = new THREE.Mesh(shape, rand() < 0.5 ? lm : lm2);
    leaf.position.copy(top); leaf.rotation.z = a; leaf.rotation.y = -0.25 - rand() * 0.25; leaf.castShadow = true;
    g.add(leaf);
  }
  for (let k = 0; k < 4; k++) {
    const c = new THREE.Mesh(new THREE.SphereGeometry(h * 0.018, 8, 6), new THREE.MeshStandardMaterial({ color: 0x5a3b1c }));
    c.position.set(top.x + (rand() - 0.5) * h * 0.04, (rand() - 0.5) * h * 0.04, top.z - h * 0.02); g.add(c);
  }
  return g;
}

function person(rand, h = 1.75) {
  const g = new THREE.Group();
  const col = new THREE.Color().setHSL(rand(), 0.25 + rand() * 0.3, 0.25 + rand() * 0.35);
  const skin = new THREE.Color().setHSL(0.07, 0.4, 0.3 + rand() * 0.3);
  const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.2, h * 0.38, 4, 8), new THREE.MeshStandardMaterial({ color: col, roughness: 0.9 }));
  body.rotation.x = Math.PI / 2; body.position.z = h * 0.62; g.add(body);
  const legs = new THREE.Mesh(new THREE.CapsuleGeometry(0.15, h * 0.34, 4, 8), new THREE.MeshStandardMaterial({ color: new THREE.Color().setHSL(0.6, 0.3, 0.15 + rand() * 0.2) }));
  legs.rotation.x = Math.PI / 2; legs.position.z = h * 0.28; g.add(legs);
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.115, 12, 10), new THREE.MeshStandardMaterial({ color: skin, roughness: 0.7 }));
  head.position.z = h * 0.93; g.add(head);
  g.children.forEach(c => c.castShadow = true);
  return g;
}

function car(rand) {
  const g = new THREE.Group();
  const col = new THREE.Color().setHSL(rand(), rand() < 0.4 ? 0.0 : 0.5, 0.2 + rand() * 0.5);
  const m = new THREE.MeshStandardMaterial({ color: col, roughness: 0.35, metalness: 0.5 });
  const b = new THREE.Mesh(new THREE.BoxGeometry(4.4, 1.8, 0.7), m); b.position.z = 0.6; g.add(b);
  const c = new THREE.Mesh(new THREE.BoxGeometry(2.3, 1.6, 0.55), new THREE.MeshStandardMaterial({ color: 0x1a2630, roughness: 0.2, metalness: 0.7 })); c.position.set(-0.2, 0, 1.2); g.add(c);
  for (const sx of [-1.4, 1.4]) for (const sy of [-0.9, 0.9]) {
    const w = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.34, 0.25, 14), new THREE.MeshStandardMaterial({ color: 0x111111 }));
    w.rotation.x = Math.PI / 2; w.position.set(sx, sy, 0.34); g.add(w);
  }
  g.children.forEach(x => x.castShadow = true);
  return g;
}

function sky(top, mid, hor, sun) {
  const geo = new THREE.SphereGeometry(4000, 32, 16);
  const mat = new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false,
    uniforms: { top: { value: new THREE.Color(top) }, mid: { value: new THREE.Color(mid) }, hor: { value: new THREE.Color(hor) }, sunDir: { value: sun.clone().normalize() } },
    vertexShader: 'varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }',
    fragmentShader: `varying vec3 vP; uniform vec3 top,mid,hor,sunDir;
      void main(){ float h = clamp(vP.y,0.,1.); vec3 c = mix(hor, mid, smoothstep(0.0,0.25,h)); c = mix(c, top, smoothstep(0.2,0.9,h));
        float s = max(dot(normalize(vP), sunDir),0.); c += vec3(1.0,0.72,0.5)*pow(s,24.)*0.55 + vec3(1.0,0.8,0.6)*pow(s,300.)*1.6;
        gl_FragColor = vec4(c,1.); }`,
  });
  return new THREE.Mesh(geo, mat);
}

function cloudSprites(rand, n) {
  const g = new THREE.Group();
  for (let i = 0; i < n; i++) {
    const c = document.createElement('canvas'); c.width = 256; c.height = 96; const x = c.getContext('2d');
    for (let k = 0; k < 26; k++) {
      const px = 40 + rand() * 176, py = 30 + rand() * 40, r = 14 + rand() * 30;
      const gr = x.createRadialGradient(px, py, 0, px, py, r); gr.addColorStop(0, 'rgba(255,225,215,0.55)'); gr.addColorStop(1, 'rgba(255,200,200,0)');
      x.fillStyle = gr; x.beginPath(); x.arc(px, py, r, 0, 7); x.fill();
    }
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: t, transparent: true, depthWrite: false, fog: false }));
    s.scale.set(900 + rand() * 900, 280 + rand() * 200, 1);
    s.position.set(-2200 + rand() * 4400, 3000 + rand() * 600, 500 + rand() * 900); g.add(s);
  }
  return g;
}

export function buildWorld(opts = {}) {
  const rand = rng(opts.seed ?? 4);
  const world = new THREE.Group();   // coordenadas Blender (Z arriba)
  const tones = ['#8d8478', '#7b7f86', '#9a8a78', '#6f7a80', '#a0948a', '#837a70', '#6a6f76'];

  // suelo (promenade de tablones) + agua
  const deckTex = (() => { const c = document.createElement('canvas'); c.width = c.height = 256; const g = c.getContext('2d');
    for (let i = 0; i < 8; i++) { g.fillStyle = `rgb(${120 + rand() * 25 | 0},${88 + rand() * 18 | 0},${60 + rand() * 14 | 0})`; g.fillRect(0, i * 32, 256, 30); }
    g.fillStyle = 'rgba(0,0,0,.35)'; for (let i = 0; i < 8; i++) g.fillRect(0, i * 32 + 30, 256, 2);
    const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(30, 6); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; })();
  const deck = new THREE.Mesh(new THREE.PlaneGeometry(200, 14), new THREE.MeshStandardMaterial({ map: deckTex, roughness: 0.8 }));
  deck.position.set(0, -4, 0); deck.receiveShadow = true; world.add(deck);
  const wg = new THREE.PlaneGeometry(9000, 3000, 1, 60);
  { const pos = wg.attributes.position, col = []; const near = new THREE.Color(0x35566a), far = new THREE.Color(0xe0a590), cc = new THREE.Color();
    for (let i = 0; i < pos.count; i++) { const t = Math.pow((pos.getY(i) + 1500) / 3000, 0.45); cc.copy(near).lerp(far, t); col.push(cc.r, cc.g, cc.b); }
    wg.setAttribute('color', new THREE.Float32BufferAttribute(col, 3)); }
  const water = new THREE.Mesh(wg, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.35, metalness: 0.0 }));
  water.position.set(0, 1500 + 3, -2.2); water.receiveShadow = true; world.add(water);
  // baranda
  const rm = new THREE.MeshStandardMaterial({ color: 0x5b4632, roughness: 0.7 });
  const rail = new THREE.Mesh(new THREE.BoxGeometry(200, 0.16, 0.12), rm); rail.position.set(0, 3, 1.05); rail.castShadow = true; world.add(rail);
  for (let x = -100; x <= 100; x += 1.6) { const p = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.12, 1.05), rm); p.position.set(x, 3, 0.52); p.castShadow = true; world.add(p); }
  // pilotes
  for (let x = -90; x <= 90; x += 6) { const p = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.32, 5, 8), rm); p.rotation.x = Math.PI / 2; p.position.set(x, 3.4, -2.2); world.add(p); }

  // malecón de la costa opuesta + skyline en capas
  const quay = new THREE.Mesh(new THREE.PlaneGeometry(6000, 60), new THREE.MeshStandardMaterial({ color: 0x8a8378, roughness: 0.9 }));
  quay.position.set(0, 850, -1.5); quay.receiveShadow = true; world.add(quay);
  const layers = [[900, 1200, 70, 170, 80], [1250, 1900, 100, 300, 100], [1950, 2800, 120, 480, 140]];
  for (const [y0, y1, nb, hmax, spread] of layers) {
    for (let i = 0; i < nb; i++) {
      const w = 22 + rand() * 40, d = 22 + rand() * 40, h = 40 + Math.pow(rand(), 1.5) * hmax;
      const b = building(rand, w, d, h, tones);
      b.position.set(-2200 + (i / nb) * 4400 + (rand() - 0.5) * spread, y0 + rand() * (y1 - y0) * 0.5, -2); world.add(b);
    }
  }
  // puente colgante diagonal
  const steel = new THREE.MeshStandardMaterial({ color: 0x8c8f92, roughness: 0.6, metalness: 0.5 });
  const bridge = new THREE.Group();
  const span = 900, deckH = 38;
  const dk = new THREE.Mesh(new THREE.BoxGeometry(span, 22, 3), steel); dk.position.set(0, 0, deckH); bridge.add(dk);
  const truss = new THREE.Mesh(new THREE.BoxGeometry(span, 22, 1.2), steel); truss.position.set(0, 0, deckH - 6); bridge.add(truss);
  for (const tx of [-300, 300]) {
    for (const ty of [-9, 9]) {
      const leg = new THREE.Mesh(new THREE.BoxGeometry(5, 4, 170), steel); leg.position.set(tx, ty, 85 - 2); bridge.add(leg);
    }
    for (let z = 20; z < 170; z += 26) { const x = new THREE.Mesh(new THREE.BoxGeometry(4, 22, 3), steel); x.position.set(tx, 0, z); bridge.add(x);
      const diag = new THREE.Mesh(new THREE.BoxGeometry(2.4, 2.4, 30), steel); diag.rotation.x = 0.7; diag.position.set(tx, 0, z + 13); bridge.add(diag); }
    const cap = new THREE.Mesh(new THREE.BoxGeometry(8, 22, 10), steel); cap.position.set(tx, 0, 172); bridge.add(cap);
  }
  for (const ty of [-10, 10]) {
    const pts = [];
    for (let i = 0; i <= 60; i++) { const t = i / 60 * 2 - 1; const x = t * span * 0.5; let z;
      if (Math.abs(x) <= 300) { z = 170 - (1 - (x / 300) ** 2) * 135; } else { const u = (Math.abs(x) - 300) / (span * 0.5 - 300); z = 170 - u * 132; }
      pts.push(new THREE.Vector3(x, ty, z)); }
    const cb = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 120, 1.3, 6), steel); bridge.add(cb);
    for (let i = 2; i < 59; i += 1) { const p = pts[i]; const h = p.z - deckH; if (h < 3) continue;
      const h2 = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, h, 4), steel); h2.rotation.x = Math.PI / 2; h2.position.set(p.x, ty, deckH + h / 2); bridge.add(h2); }
  }
  bridge.position.set(220, 720, 0); bridge.rotation.z = -0.10; bridge.scale.set(0.8, 0.8, 0.8); world.add(bridge);

  // palmeras (primer plano y plano medio), farolas, bancos, gente, autos
  const mkPalm = (x, y, h, lean) => { const p = palm(rand, h, lean); p.position.set(x, y, 0); p.rotation.z = rand() * 6; world.add(p); };
  mkPalm(-6.2, -2.4, 11, -0.6); mkPalm(7.6, 0.8, 9.5, 0.7); mkPalm(-11.5, 1.5, 12, 0.3); mkPalm(14, -1.5, 10.5, -0.4);
  for (let i = 0; i < 40; i++) mkPalm(-500 + i * 26 + rand() * 8, 835 + rand() * 20, 10 + rand() * 6, rand() - 0.5);
  for (let i = 0; i < 16; i++) mkPalm(-90 + i * 12 + rand() * 6, 28 + rand() * 18, 9 + rand() * 5, rand() - 0.5);
  for (const lx of [-3.5, 9.5, -17, 20, 35, -35]) {
    const m = new THREE.MeshStandardMaterial({ color: 0x2c3036, roughness: 0.5, metalness: 0.5 });
    const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.1, 5.2, 8), m); pole.rotation.x = Math.PI / 2; pole.position.set(lx, 2.5, 2.6); pole.castShadow = true; world.add(pole);
    const arm = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.07, 0.07), m); arm.position.set(lx + 0.6, 2.5, 5.1); world.add(arm);
    const lamp = new THREE.Mesh(new THREE.SphereGeometry(0.22, 10, 8), new THREE.MeshStandardMaterial({ color: 0xfff1c8, emissive: 0xffe2a0, emissiveIntensity: 0.9 })); lamp.position.set(lx + 1.25, 2.5, 5.0); world.add(lamp);
  }
  for (const bx of [-9, 4.4, 17]) {
    const m = new THREE.MeshStandardMaterial({ color: 0x6b4a2c, roughness: 0.7 });
    const seat = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.5, 0.08), m); seat.position.set(bx, 1.7, 0.5); seat.castShadow = true; world.add(seat);
    const back = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.08, 0.5), m); back.position.set(bx, 1.95, 0.8); world.add(back);
  }
  for (let i = 0; i < 40; i++) { const p = person(rand, 1.62 + rand() * 0.25); p.position.set(-40 + rand() * 80, -1.0 + rand() * 3.2, 0); if (Math.abs(p.position.x) < 2.4) p.position.x += (p.position.x < 0 ? -3 : 3); p.rotation.z = rand() * 6; world.add(p); }
  // avenida con autos y edificios del borde (detrás del agua: costa del frente cercana)
  for (let i = 0; i < 24; i++) { const c = car(rand); c.position.set(-500 + i * 42 + rand() * 12, 860 + (i % 2) * 8, -1.5); c.rotation.z = (i % 2) ? Math.PI : 0; world.add(c); }
  // botes
  for (let i = 0; i < 14; i++) {
    const b = new THREE.Group(); const hull = new THREE.Mesh(new THREE.BoxGeometry(8 + rand() * 20, 3 + rand() * 3, 2), new THREE.MeshStandardMaterial({ color: new THREE.Color().setHSL(rand(), 0.1, 0.65) }));
    hull.position.z = 0.4; b.add(hull); const cab = new THREE.Mesh(new THREE.BoxGeometry(5, 2.5, 2.4), new THREE.MeshStandardMaterial({ color: 0xe6e2da })); cab.position.set(-1, 0, 2); b.add(cab);
    b.position.set(-120 + rand() * 300, 25 + rand() * 440, -1.8); b.rotation.z = rand() * 0.6; b.children.forEach(c => c.castShadow = true); world.add(b);
  }
  // aves (V) y nubes
  for (let i = 0; i < 18; i++) {
    const g = new THREE.BufferGeometry(); const s = 1.2 + rand() * 1.2;
    g.setAttribute('position', new THREE.Float32BufferAttribute([-s, 0, 0, 0, 0.15, 0.3, s, 0, 0, 0, 0.15, 0.3, 0, 0, 0, -s, 0, 0], 3)); g.setIndex([0, 1, 2, 3, 4, 5]);
    const m = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ color: 0x2a2a30, side: THREE.DoubleSide })); m.position.set(-60 + rand() * 120, 60 + rand() * 80, 30 + rand() * 40); m.rotation.z = rand() * 6; world.add(m);
  }
  return world;
}

export function buildSky(mode) {
  const sun = new THREE.Vector3(-0.55, 0.65, 0.22);  // Blender coords: sol a la izquierda, bajo, hacia el fondo
  const s = sky(0x56628a, 0xb98a94, 0xf5b58a, new THREE.Vector3(sun.x, sun.z, -sun.y));
  const c = cloudSprites(rng(9), 14);
  return { sky: s, clouds: c, sun };
}
