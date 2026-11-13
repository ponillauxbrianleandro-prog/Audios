import React from 'react';
import { INK, Pt, clamp, lerp, mix, rng, smooth } from './lib';

/**
 * Animales construidos "como en 3D": un esqueleto de esferas (x adelante, y arriba, l lateral)
 * que se proyecta a 2D con un giro (yaw). Se dibuja en tres pasadas: silueta oscura, masa de
 * color corrida hacia la luz y lomo/brillos. Nunca se usa de perfil puro.
 */
export type Kind = 'procy' | 'gorgon' | 'dicyn' | 'pareia';
type V3 = [number, number, number];
type Col = { sh: string; lit: string; top?: string; bot?: string };
type Sph = { p: V3; r: number; c: Col; blot?: number; tick?: boolean; knob?: boolean };
type Spec = {
  L: number; R: number; hipR: number; shR: number; cy: number; neck: number; neckR: number;
  headL: number; r0: number; r1: number; jawR: number; tailL: number; tailR: number;
  l1: number; l2: number; legW: number; sprawl: number; stride: number; lift: number; fang: number; teeth: boolean;
  col: { base: string; back: string; blot: string; belly: string; leg: string; eye: string };
};

export const SPEC: Record<Kind, Spec> = {
  procy: { L: 215, R: 54, hipR: 44, shR: 50, cy: 60, neck: 30, neckR: 42, headL: 168, r0: 50, r1: 40, jawR: 24, tailL: 300, tailR: 31,
    l1: 50, l2: 46, legW: 20, sprawl: 46, stride: 92, lift: 24, fang: 24, teeth: true,
    col: { base: '#a39448', back: '#c9645e', blot: '#6a2a66', belly: '#e4d48a', leg: '#8d8240', eye: '#ffd23a' } },
  gorgon: { L: 400, R: 96, hipR: 80, shR: 96, cy: 205, neck: 60, neckR: 76, headL: 280, r0: 84, r1: 70, jawR: 36, tailL: 330, tailR: 52,
    l1: 122, l2: 116, legW: 38, sprawl: 34, stride: 240, lift: 60, fang: 84, teeth: true,
    col: { base: '#666070', back: '#3f384e', blot: '#d8922e', belly: '#a8a098', leg: '#575062', eye: '#ff5030' } },
  dicyn: { L: 270, R: 112, hipR: 96, shR: 104, cy: 132, neck: 24, neckR: 82, headL: 140, r0: 72, r1: 46, jawR: 26, tailL: 90, tailR: 30,
    l1: 72, l2: 62, legW: 34, sprawl: 50, stride: 110, lift: 26, fang: 34, teeth: false,
    col: { base: '#7fae7a', back: '#4f7f6c', blot: '#2f5a58', belly: '#d0dca8', leg: '#6c9668', eye: '#f6eca0' } },
  pareia: { L: 330, R: 132, hipR: 110, shR: 122, cy: 150, neck: 22, neckR: 88, headL: 126, r0: 68, r1: 52, jawR: 28, tailL: 150, tailR: 44,
    l1: 80, l2: 66, legW: 44, sprawl: 62, stride: 120, lift: 24, fang: 0, teeth: false,
    col: { base: '#b48a58', back: '#855a40', blot: '#5a3828', belly: '#dcc090', leg: '#9c7448', eye: '#f6eca0' } },
};

export const cycleLen = (kind: Kind, s = 1, run = false) => (SPEC[kind].stride * (run ? 1.7 : 1) * s) / 0.6;

export type BeastProps = {
  kind?: Kind; x: number; y: number; s?: number; flip?: boolean; yaw?: number; turn?: number;
  phase?: number; run?: boolean; head?: number; jaw?: number; crouch?: number; f?: number;
  blink?: number; sil?: string; eyeGlow?: boolean; shadow?: boolean; tailAmp?: number; look?: number; drift?: number;
};

const PITCH = 0.3; // la cámara mira un poco desde arriba
const DIST = 1500;
const D2R = Math.PI / 180;

const build = (pr: BeastProps) => {
  const kind = pr.kind ?? 'procy';
  const P = SPEC[kind];
  const { phase, run, head = 0, jaw = 0, crouch = 0, f = 0, tailAmp = 1, turn = 0 } = pr;
  const yaw = (pr.yaw ?? 32) * D2R;
  const sil = pr.sil;
  const cs = Math.cos(yaw), sn = Math.sin(yaw), cp = Math.cos(PITCH), sp = Math.sin(PITCH);
  const proj = (p: V3) => {
    const xw = p[0] * cs - p[2] * sn, zw = p[0] * sn + p[2] * cs;
    const d = zw * cp + p[1] * sp;
    const k = 1 + d / DIST;
    return { x: xw * k, y: (-p[1] * cp + zw * sp) * k, d, k };
  };
  const moving = phase !== undefined;
  const ph = phase ?? 0;
  const breath = Math.sin(f / 14);
  const bob = moving ? Math.sin(ph * Math.PI * 4) * (run ? 6 : 2.5) : breath * 0.8;
  const cy = P.cy * (1 - crouch * 0.38) + bob;
  const C = P.col;
  const c = (base: string, top?: string, bot?: string): Col => (sil ? { sh: sil, lit: sil } : { sh: mix(base, '#1c1030', 0.42), lit: base, top, bot });
  const bodyC = c(C.base, C.back, C.belly), legC = c(C.leg), headC = c(C.base, C.back), jawC = c(C.belly);

  // ---- columna, cola y cuello
  const body: Sph[] = [];
  const und = (t: number) => (moving ? Math.sin(ph * Math.PI * 2 + t * Math.PI) * P.R * 0.1 : 0);
  const NS = 26;
  for (let i = 0; i <= NS; i++) {
    const t = i / NS;
    const r = t < 0.45 ? lerp(P.hipR, P.R, Math.sin((t / 0.45) * Math.PI / 2)) : lerp(P.R, P.shR, (t - 0.45) / 0.55);
    body.push({ p: [-P.L / 2 + t * P.L, cy - Math.sin(Math.PI * t) * P.R * 0.07, und(t)], r, c: bodyC, blot: i % 3 === 1 ? i : undefined, tick: i % 2 === 0, knob: kind === 'pareia' && i % 3 === 0 });
  }
  const TN = 26;
  let tp: V3 = [-P.L / 2 - P.hipR * 0.3, cy, und(0)];
  let ang = Math.PI, drop = 0;
  for (let i = 0; i <= TN; i++) {
    const t = i / TN;
    const r = P.tailR * Math.pow(1 - t, 0.8) + 2.5;
    const wave = Math.sin((moving ? ph * Math.PI * 2 : f / 24) - t * 4.2) * 0.5 * t * tailAmp * (run ? 1.5 : 1);
    ang = Math.PI + wave;
    drop = Math.max(r, lerp(cy, r + 2, Math.min(1, t * 1.5)));
    tp = [tp[0] + (Math.cos(ang) * P.tailL) / TN, drop, tp[2] + (Math.sin(ang) * P.tailL) / TN];
    body.push({ p: tp, r, c: bodyC, blot: i % 4 === 2 ? 100 + i : undefined });
  }
  const sh0: V3 = [P.L / 2, cy, und(1)];
  const N: V3 = [P.L / 2 + P.neck, cy + P.R * 0.12 - crouch * 6, und(1) * 0.6];
  for (let i = 1; i <= 5; i++) {
    const t = i / 5;
    body.push({ p: [lerp(sh0[0], N[0], t), lerp(sh0[1], N[1], t), lerp(sh0[2], N[2], t)], r: lerp(P.shR * 0.92, P.neckR, t), c: bodyC, blot: i === 3 ? 60 : undefined });
  }

  // ---- cabeza (coordenadas locales: x adelante, y arriba, l lateral)
  const hp = (head + (moving ? Math.sin(ph * Math.PI * 4 + 0.5) * 2 : Math.sin(f / 31) * 1.5)) * D2R;
  const ht = turn * D2R;
  const hloc = (x: number, y: number, l: number): V3 => {
    const x1 = x * Math.cos(hp) + y * Math.sin(hp), y1 = -x * Math.sin(hp) + y * Math.cos(hp);
    const x2 = x1 * Math.cos(ht) - l * Math.sin(ht), l2 = x1 * Math.sin(ht) + l * Math.cos(ht);
    return [N[0] + x2, N[1] + y1, N[2] + l2];
  };
  const HL = P.headL, r0 = P.r0, r1 = P.r1;
  const skR = (t: number) => lerp(r0, r1, Math.pow(t, 1.4));
  const skX = (t: number) => t * (HL - r1 * 0.9);
  const skY = (t: number) => r0 * 0.12 - t * r0 * 0.1;
  const skull: Sph[] = [];
  for (let i = 0; i <= 12; i++) { const t = i / 12; skull.push({ p: hloc(skX(t), skY(t), 0), r: skR(t), c: headC, blot: i === 2 || i === 5 ? 200 + i : undefined }); }
  // ceja ósea
  const eyeT = 0.4;
  const eyeL = skR(eyeT) * 0.62;
  for (const sgn of [1, -1]) skull.push({ p: hloc(skX(eyeT) - 4, skY(eyeT) + skR(eyeT) * 0.58, sgn * eyeL * 0.86), r: skR(eyeT) * 0.42, c: headC });
  const ja = jaw * D2R;
  const hinge: [number, number] = [HL * 0.04, -r0 * 0.5];
  const jloc = (x: number, y: number, l: number): V3 => {
    const dx = x - hinge[0], dy = y - hinge[1];
    return hloc(hinge[0] + dx * Math.cos(ja) + dy * Math.sin(ja), hinge[1] - dx * Math.sin(ja) + dy * Math.cos(ja), l);
  };
  const jawS: Sph[] = [];
  const jwY = (t: number) => lerp(-r0 * 0.62, -r1 * 0.74, t);
  const jwX = (t: number) => hinge[0] + t * (HL * 0.9 - hinge[0]);
  for (let i = 0; i <= 11; i++) { const t = i / 11; jawS.push({ p: jloc(jwX(t), jwY(t), 0), r: lerp(P.jawR * 1.25, P.jawR * 0.78, t), c: jawC }); }

  // ---- patas
  const S = P.stride * (run ? 1.7 : 1), lift = P.lift * (run ? 1.5 : 1);
  const footX = (off: number, rest: number): { x: number; y: number } => {
    if (!moving) return { x: rest, y: 0 };
    const u = (((ph + off) % 1) + 1) % 1;
    if (u < 0.6) return { x: rest * 0.5 + S / 2 - S * (u / 0.6), y: 0 };
    const k = (u - 0.6) / 0.4, e = k * k * (3 - 2 * k);
    return { x: rest * 0.5 - S / 2 + S * e, y: Math.sin(Math.PI * k) * lift };
  };
  const leg = (front: boolean, side: number, off: number, rest: number): { sph: Sph[]; claws: [V3, V3][] } => {
    const jx = front ? P.L / 2 - 6 : -P.L / 2 + 10;
    const jr = front ? P.shR : P.hipR;
    const J: V3 = [jx, cy - jr * 0.15, side * jr * 0.72 + und(front ? 1 : 0)];
    const ft = footX(off, rest);
    const A: V3 = [jx + ft.x, P.legW * 0.55 + ft.y, side * (jr * 0.72 + P.sprawl)];
    let dx = A[0] - J[0], dy = A[1] - J[1], dz = A[2] - J[2];
    let d = Math.hypot(dx, dy, dz);
    const mx = P.l1 + P.l2 - 0.5;
    if (d > mx) { const q = mx / d; dx *= q; dy *= q; dz *= q; d = mx; }
    const dir: V3 = [dx / d, dy / d, dz / d];
    const a = (P.l1 * P.l1 - P.l2 * P.l2 + d * d) / (2 * d);
    const h = Math.sqrt(Math.max(0, P.l1 * P.l1 - a * a));
    const pole: V3 = [front ? -0.55 : 0.6, 0.55, side * 1];
    const dot = pole[0] * dir[0] + pole[1] * dir[1] + pole[2] * dir[2];
    let pv: V3 = [pole[0] - dot * dir[0], pole[1] - dot * dir[1], pole[2] - dot * dir[2]];
    const pl = Math.hypot(...pv) || 1;
    pv = [pv[0] / pl, pv[1] / pl, pv[2] / pl];
    const K: V3 = [J[0] + dir[0] * a + pv[0] * h, J[1] + dir[1] * a + pv[1] * h, J[2] + dir[2] * a + pv[2] * h];
    const E: V3 = [J[0] + dx, J[1] + dy, J[2] + dz];
    const sph: Sph[] = [];
    const w = P.legW;
    for (let i = 0; i <= 6; i++) { const t = i / 6; sph.push({ p: [lerp(J[0], K[0], t), lerp(J[1], K[1], t), lerp(J[2], K[2], t)], r: lerp(w * 1.25, w * 0.95, t), c: legC }); }
    for (let i = 1; i <= 6; i++) { const t = i / 6; sph.push({ p: [lerp(K[0], E[0], t), lerp(K[1], E[1], t), lerp(K[2], E[2], t)], r: lerp(w * 0.95, w * 0.72, t), c: legC }); }
    // mano ancha de cinco dedos con garras
    const claws: [V3, V3][] = [];
    const up = ft.y;
    for (let k = 0; k < 5; k++) {
      const a2 = (-0.25 + k * 0.33) * side + (front ? 0 : 0.1 * side);
      const len = w * (1.25 + (k === 2 || k === 1 ? 0.3 : 0));
      const tip: V3 = [E[0] + Math.cos(a2) * len, w * 0.3 + up * 0.7, E[2] + Math.sin(a2) * len];
      for (let i = 1; i <= 3; i++) { const t = i / 3; sph.push({ p: [lerp(E[0], tip[0], t), lerp(E[1] - w * 0.15, tip[1], t), lerp(E[2], tip[2], t)], r: lerp(w * 0.5, w * 0.3, t), c: legC }); }
      claws.push([tip, [tip[0] + Math.cos(a2) * w * 0.55, Math.max(0, up * 0.7 - 1), tip[2] + Math.sin(a2) * w * 0.55]]);
    }
    return { sph, claws };
  };
  const legs = [
    { key: 'nf', near: true, ...leg(true, 1, 0, P.l1 * 0.2 + 8) },
    { key: 'nh', near: true, ...leg(false, 1, 0.5, -P.l1 * 0.1 + 10) },
    { key: 'ff', near: false, ...leg(true, -1, 0.5, P.l1 * 0.2 - 8) },
    { key: 'fh', near: false, ...leg(false, -1, 0, -P.l1 * 0.1 - 10) },
  ];

  // ---- dientes y ojos
  const teethUp: { a: V3; len: number; near: boolean; big?: boolean }[] = [];
  const teethLo: { a: V3; len: number }[] = [];
  if (P.teeth) {
    for (const sgn of [1, -1]) {
      for (let i = 0; i < 9; i++) {
        const t = 0.4 + i * 0.062;
        teethUp.push({ a: hloc(skX(t) + skR(t) * 0.25, skY(t) - skR(t) * 0.8, sgn * skR(t) * 0.52), len: r1 * 0.24, near: sgn > 0 });
      }
      for (let i = 0; i < 8; i++) { const t = 0.42 + i * 0.07; teethLo.push({ a: jloc(jwX(t), jwY(t) + P.jawR * 0.8, sgn * P.jawR * 0.9), len: -r1 * 0.2 }); }
    }
    for (let i = 0; i < 5; i++) { const l = (i - 2) * r1 * 0.2; teethUp.push({ a: hloc(HL - r1 * 0.32 - Math.abs(i - 2) * 3, skY(1) - r1 * 0.78, l), len: r1 * 0.26, near: true }); }
  }
  if (P.fang > 0) for (const sgn of [1, -1]) { const t = 0.74; teethUp.push({ a: hloc(skX(t) + skR(t) * 0.2, skY(t) - skR(t) * 0.7, sgn * skR(t) * 0.6), len: P.fang, near: sgn > 0, big: true }); }
  const eyes = [1, -1].map((sgn) => ({ p: hloc(skX(eyeT) + 6, skY(eyeT) + skR(eyeT) * 0.34, sgn * eyeL * 1.12), near: sgn > 0 }));
  const nostrils = [1, -1].map((sgn) => ({ p: hloc(HL - r1 * 0.3, skY(1) + r1 * 0.42, sgn * r1 * 0.45), near: sgn > 0 }));
  const mouth = [hloc(hinge[0] + 6, hinge[1] + 4, r0 * 0.5), hloc(HL * 0.5, skY(0.5) - skR(0.5) * 0.6, skR(0.5) * 0.55), hloc(HL - r1 * 0.5, skY(1) - r1 * 0.6, r1 * 0.3), jloc(HL * 0.86, jwY(1) + P.jawR * 0.3, P.jawR * 0.4), jloc(HL * 0.5, jwY(0.5) + P.jawR * 0.5, P.jawR * 0.8)];
  const beak = kind === 'dicyn' ? [hloc(HL - r1 * 0.9, skY(1) + r1 * 0.2, 0), hloc(HL + r1 * 0.1, skY(1) - r1 * 0.2, 0), hloc(HL - r1 * 0.5, skY(1) - r1 * 1.1, 0), hloc(HL - r1 * 1.3, skY(1) - r1 * 0.7, 0)] : null;
  return { P, proj, body, skull, jawS, legs, teethUp, teethLo, eyes, nostrils, mouth, beak, N, cy, kind, yawDeg: pr.yaw ?? 32, headPt: hloc(HL * 0.5, 0, 0), shoulder: sh0, skR, eyeR: skR(eyeT) };
};

/** posición proyectada (sin escala) de puntos clave, para encuadrar primeros planos */
export const anchors = (pr: BeastProps) => {
  const b = build(pr);
  const e = b.proj(b.eyes[0].p), m = b.proj(b.mouth[2]), h = b.proj(b.headPt), fg = b.teethUp.find((t) => t.big && t.near);
  const fp = fg ? b.proj(fg.a) : m;
  const sgn = pr.flip ? -1 : 1;
  const hg = b.proj(b.mouth[0]), tl = b.proj(b.body[40].p);
  return { eye: [e.x * sgn, e.y] as Pt, mouth: [m.x * sgn, m.y] as Pt, head: [h.x * sgn, h.y] as Pt, fang: [fp.x * sgn, fp.y] as Pt, hinge: [hg.x * sgn, hg.y] as Pt, tail: [tl.x * sgn, tl.y] as Pt };
};

export const Beast: React.FC<BeastProps> = (pr) => {
  const { x, y, s = 1, flip, f = 0, blink = 0, sil, eyeGlow, shadow = true, look = 0, jaw = 0 } = pr;
  const b = build(pr);
  const { P, proj, kind } = b;
  const ink = sil ?? INK;
  const sw = Math.max(2, 3 / Math.sqrt(s));
  const lx = flip ? 0.55 : -0.55, ly = -0.82; // luz desde arriba a la izquierda en pantalla
  const yawR = b.yawDeg * D2R;
  // deriva en profundidad al caminar
  const trav = pr.phase !== undefined ? pr.phase * cycleLen(kind, 1, pr.run) * (pr.drift ?? 1) : 0;
  const dy = trav * Math.sin(yawR) * 0.3 * s;
  const sc = s * (1 + dy / 2600);

  const group = (sph: Sph[], key: string, deco = false): React.ReactNode => {
    const q = sph.map((sp) => ({ ...sp, q: proj(sp.p) })).sort((a, b2) => a.q.d - b2.q.d);
    const out: React.ReactNode[] = [];
    q.forEach((o, i) => out.push(<circle key={`o${i}`} cx={o.q.x.toFixed(1)} cy={o.q.y.toFixed(1)} r={(o.r * o.q.k + sw).toFixed(1)} fill={ink} />));
    const each = (fn: (o: (typeof q)[number], i: number, r: number, cx: number, cy: number) => void) => q.forEach((o, i) => fn(o, i, o.r * o.q.k, o.q.x, o.q.y));
    each((o, i, r, cx, cy) => out.push(<circle key={`s${i}`} cx={cx.toFixed(1)} cy={cy.toFixed(1)} r={r.toFixed(1)} fill={o.c.sh} />));
    if (!sil) {
      each((o, i, r, cx, cy) => { if (o.c.bot) out.push(<circle key={`b${i}`} cx={(cx + lx * r * 0.04).toFixed(1)} cy={(cy + r * 0.16).toFixed(1)} r={(r * 0.78).toFixed(1)} fill={mix(o.c.bot, '#1c1030', 0.22)} />); });
      each((o, i, r, cx, cy) => out.push(<circle key={`l${i}`} cx={(cx + lx * r * 0.14).toFixed(1)} cy={(cy + ly * r * (o.c.bot ? 0.3 : 0.14)).toFixed(1)} r={(r * (o.c.bot ? 0.7 : 0.85)).toFixed(1)} fill={o.c.lit} />));
      each((o, i, r, cx, cy) => { if (o.c.top) out.push(<circle key={`t${i}`} cx={(cx + lx * r * 0.2).toFixed(1)} cy={(cy - r * 0.42).toFixed(1)} r={(r * 0.56).toFixed(1)} fill={o.c.top} />); });
      each((o, i, r, cx, cy) => { if (o.c.top && r > 24) out.push(<circle key={`h${i}`} cx={(cx + lx * r * 0.4).toFixed(1)} cy={(cy - r * 0.66).toFixed(1)} r={(r * 0.2).toFixed(1)} fill={mix(o.c.top, '#ffffff', 0.38)} />); });
      each((o, i, r, cx, cy) => {
        if (deco && o.blot !== undefined) {
          const rr = rng(o.blot + 7);
          const bx = cx + (rr() - 0.5) * r * 0.4 + lx * r * 0.1, by = cy - r * (0.2 + rr() * 0.3);
          const d = smooth([[bx - r * 0.22, by - r * 0.5], [bx + r * 0.2, by - r * 0.55], [bx + r * 0.3, by - r * 0.1], [bx + r * 0.1, by + r * (0.25 + rr() * 0.35)], [bx - r * 0.12, by + r * 0.1], [bx - r * 0.3, by - r * 0.15]], true, 1);
          out.push(<path key={`p${i}`} d={d} fill={P.col.blot} opacity={0.92} />);
          out.push(<circle key={`pp${i}`} cx={(bx + r * 0.46).toFixed(1)} cy={(by + r * 0.2).toFixed(1)} r={(r * 0.09).toFixed(1)} fill={P.col.blot} />);
          out.push(<circle key={`pq${i}`} cx={(bx - r * 0.4).toFixed(1)} cy={(by + r * 0.34).toFixed(1)} r={(r * 0.06).toFixed(1)} fill={P.col.blot} />);
        }
        if (deco && o.tick && r > 14) {
          const rr = rng(i * 13 + 3);
          const tx = cx + (rr() - 0.4) * r * 0.5, ty = cy + r * (0.05 + rr() * 0.3), q2 = r * 0.13;
          out.push(<path key={`k${i}`} d={`M${(tx - q2).toFixed(1)} ${ty.toFixed(1)}q${q2.toFixed(1)} ${(q2 * 0.9).toFixed(1)} ${(q2 * 2).toFixed(1)} 0`} fill="none" stroke={INK} strokeWidth={sw * 0.5} strokeLinecap="round" opacity={0.45} />);
          out.push(<circle key={`w${i}`} cx={(tx + r * 0.2).toFixed(1)} cy={(ty - r * 0.5).toFixed(1)} r={(r * 0.05).toFixed(1)} fill={mix(o.c.lit, '#ffffff', 0.45)} />);
        }
        if (o.knob) out.push(<circle key={`n${i}`} cx={cx.toFixed(1)} cy={(cy - r * 0.92).toFixed(1)} r={(r * 0.13).toFixed(1)} fill={mix(P.col.belly, '#ffffff', 0.2)} stroke={INK} strokeWidth={sw * 0.6} />);
      });
    }
    return <g key={key}>{out}</g>;
  };

  const tooth = (t: { a: V3; len: number; big?: boolean }, i: number, key: string) => {
    const q = proj(t.a);
    const w = (t.big ? P.fang * 0.2 : Math.abs(t.len) * 0.42) * q.k, L2 = t.len * q.k;
    const d = t.big
      ? `M${(q.x - w).toFixed(1)} ${q.y.toFixed(1)}Q${(q.x - w * 0.9).toFixed(1)} ${(q.y + L2 * 0.7).toFixed(1)} ${(q.x - w * 1.3).toFixed(1)} ${(q.y + L2).toFixed(1)}Q${(q.x + w * 0.9).toFixed(1)} ${(q.y + L2 * 0.55).toFixed(1)} ${(q.x + w).toFixed(1)} ${q.y.toFixed(1)}Z`
      : `M${(q.x - w).toFixed(1)} ${q.y.toFixed(1)}L${q.x.toFixed(1)} ${(q.y + L2).toFixed(1)}L${(q.x + w).toFixed(1)} ${q.y.toFixed(1)}Z`;
    return <path key={`${key}${i}`} d={d} fill={sil && !eyeGlow ? sil : '#fff8e2'} stroke={ink} strokeWidth={t.big ? sw * 0.7 : sw * 0.35} strokeLinejoin="round" />;
  };

  const legG = (lg: (typeof b.legs)[number]) => (
    <g key={lg.key}>
      {group(lg.near || sil ? lg.sph : lg.sph.map((o) => ({ ...o, c: { sh: mix(o.c.sh, '#140c20', 0.35), lit: mix(o.c.lit, '#140c20', 0.4) } })), lg.key)}
      {!sil && lg.claws.map(([a, t], i) => { const pa = proj(a), pt = proj(t); const nx = -(pt.y - pa.y), ny = pt.x - pa.x; const l = Math.hypot(nx, ny) || 1; const w = P.legW * 0.2; return <path key={i} d={`M${(pa.x + (nx / l) * w).toFixed(1)} ${(pa.y + (ny / l) * w).toFixed(1)}L${pt.x.toFixed(1)} ${(pt.y + 2).toFixed(1)}L${(pa.x - (nx / l) * w).toFixed(1)} ${(pa.y - (ny / l) * w).toFixed(1)}Z`} fill="#2a2030" stroke={INK} strokeWidth={sw * 0.4} strokeLinejoin="round" />; })}
    </g>
  );

  const eye = (e: { p: V3; near: boolean }, i: number) => {
    const q = proj(e.p);
    const er = b.eyeR * 0.15 * q.k * (kind === 'gorgon' ? 0.8 : 1);
    if (sil) return eyeGlow ? <ellipse key={i} cx={q.x} cy={q.y} rx={er * 1.3} ry={er * 0.8} fill={P.col.eye} /> : null;
    const op = Math.max(0.08, 1 - blink);
    return (
      <g key={i}>
        <ellipse cx={q.x} cy={q.y + er * 0.2} rx={er * 1.9} ry={er * 1.6} fill="#2a1830" opacity={0.55} />
        <ellipse cx={q.x} cy={q.y} rx={er * 1.25} ry={er * 1.1 * op} fill={P.col.eye} stroke={INK} strokeWidth={sw * 0.7} />
        <ellipse cx={q.x + look * er * 0.3} cy={q.y} rx={er * 0.5} ry={er * 0.85 * op} fill="#0b0810" />
        {blink < 0.5 && <circle cx={q.x - er * 0.4 + look * er * 0.3} cy={q.y - er * 0.4} r={er * 0.3} fill="#fff" />}
        <path d={`M${q.x - er * 2.3} ${q.y - er * 1.2}Q${q.x} ${q.y - er * 2.6} ${q.x + er * 2.5} ${q.y - er * 0.9}`} fill="none" stroke={INK} strokeWidth={sw * 1.15} strokeLinecap="round" />
      </g>
    );
  };

  const hd = proj(b.headPt).d, sd = proj(b.shoulder).d;
  const headFront = hd >= sd - 20;
  const showFar = Math.sin(yawR) > 0.55;
  const mp = b.mouth.map((m) => proj(m));
  const headG = (
    <g key="head">
      {b.teethUp.filter((t) => !t.near).map((t, i) => tooth(t, i, 'fu'))}
      {group(b.jawS, 'jaw')}
      {jaw > 2 && <path d={`M${mp.map((m) => `${m.x.toFixed(1)} ${m.y.toFixed(1)}`).join('L')}Z`} fill={sil ?? '#5a1232'} stroke={ink} strokeWidth={sw * 0.6} strokeLinejoin="round" />}
      {jaw > 2 && !sil && b.teethLo.map((t, i) => tooth(t, i, 'lo'))}
      {group(b.skull, 'skull', true)}
      {!sil && b.beak && <path d={smooth(b.beak.map((p) => { const q = proj(p); return [q.x, q.y] as Pt; }), true, 0.6)} fill="#3a3444" stroke={INK} strokeWidth={sw * 0.7} />}
      {b.teethUp.filter((t) => t.near).map((t, i) => tooth(t, i, 'nu'))}
      {!sil && <path d={`M${mp[0].x.toFixed(1)} ${mp[0].y.toFixed(1)}Q${mp[1].x.toFixed(1)} ${(mp[1].y + 3).toFixed(1)} ${mp[2].x.toFixed(1)} ${mp[2].y.toFixed(1)}`} fill="none" stroke={INK} strokeWidth={sw * 0.8} strokeLinecap="round" opacity={0.85} />}
      {b.eyes.filter((e) => e.near || showFar).sort((a, c2) => (a.near ? 1 : 0) - (c2.near ? 1 : 0)).map(eye)}
      {!sil && b.nostrils.filter((n) => n.near || showFar).map((n, i) => { const q = proj(n.p); return <ellipse key={i} cx={q.x} cy={q.y} rx={P.r1 * 0.1 * q.k} ry={P.r1 * 0.06 * q.k} fill={INK} transform={`rotate(-25 ${q.x.toFixed(1)} ${q.y.toFixed(1)})`} />; })}
    </g>
  );
  const near = b.legs.filter((l) => l.near), far = b.legs.filter((l) => !l.near);
  const byDepth = (a: (typeof b.legs)[number], c2: (typeof b.legs)[number]) => proj(a.sph[0].p).d - proj(c2.sph[0].p).d;
  // sombra proyectada
  const shPts: Pt[] = [];
  for (let i = 0; i < 14; i++) { const a = (i / 14) * Math.PI * 2; const q = proj([Math.cos(a) * (P.L * 0.72 + P.headL * 0.3) + P.headL * 0.2, 0, Math.sin(a) * (P.R * 1.3 + P.sprawl * 0.8)]); shPts.push([q.x - lx * 26, q.y + 6]); }
  return (
    <g transform={`translate(${x.toFixed(1)} ${(y + dy).toFixed(1)}) scale(${(flip ? -sc : sc).toFixed(4)} ${sc.toFixed(4)})`}>
      {shadow && !sil && <path d={smooth(shPts, true, 0.9)} fill="#0c0718" opacity={0.3} />}
      {far.sort(byDepth).map(legG)}
      {!headFront && headG}
      {group(b.body, 'body', true)}
      {headFront && headG}
      {near.sort(byDepth).map(legG)}
    </g>
  );
};
void clamp;
