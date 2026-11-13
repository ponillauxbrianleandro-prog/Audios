import React, { useId } from 'react';
import { INK, Pt, capsule, clamp, leaf, lerp, poly, smooth } from './lib';

export type Kind = 'procy' | 'gorgon' | 'dicyn' | 'pareia';
type Spec = {
  L: number; bh: number; stand: number; l1: number; l2: number; legW: number; tailL: number; tailW: number;
  headL: number; headH: number; neck: number; fang: number; stride: number; lift: number; teeth: boolean;
  col: { base: string; back: string; band: string; belly: string; leg: string; far: string; eye: string };
};

export const SPEC: Record<Kind, Spec> = {
  procy: { L: 250, bh: 86, stand: 74, l1: 41, l2: 38, legW: 20, tailL: 310, tailW: 30, headL: 150, headH: 70, neck: 36, fang: 19, stride: 92, lift: 26, teeth: true,
    col: { base: '#9a8c52', back: '#bf6f62', band: '#63294c', belly: '#d8c98c', leg: '#857a48', far: '#514a32', eye: '#f6c531' } },
  gorgon: { L: 430, bh: 170, stand: 205, l1: 104, l2: 98, legW: 40, tailL: 330, tailW: 52, headL: 250, headH: 132, neck: 60, fang: 62, stride: 250, lift: 60, teeth: true,
    col: { base: '#5b5666', back: '#3a3448', band: '#c48a3a', belly: '#9a938c', leg: '#4c4756', far: '#27242f', eye: '#ff5a3a' } },
  dicyn: { L: 300, bh: 190, stand: 110, l1: 50, l2: 46, legW: 34, tailL: 90, tailW: 34, headL: 130, headH: 112, neck: 30, fang: 26, stride: 110, lift: 26, teeth: false,
    col: { base: '#7fa07a', back: '#587a6c', band: '#3d5a58', belly: '#c2d0a4', leg: '#6a8a68', far: '#3c5648', eye: '#f2e9a0' } },
  pareia: { L: 380, bh: 240, stand: 130, l1: 56, l2: 50, legW: 46, tailL: 150, tailW: 50, headL: 130, headH: 110, neck: 26, fang: 0, stride: 120, lift: 24, teeth: false,
    col: { base: '#a8845e', back: '#7c5a46', band: '#4f3830', belly: '#d0b890', leg: '#8f6e50', far: '#4a382c', eye: '#f2e9a0' } },
};

/** distance travelled in one full walk cycle */
export const cycleLen = (kind: Kind, s = 1, run = false) => (SPEC[kind].stride * (run ? 1.7 : 1) * s) / 0.6;

export type BeastProps = {
  kind?: Kind; x: number; y: number; s?: number; flip?: boolean;
  phase?: number; run?: boolean; head?: number; jaw?: number; crouch?: number; f?: number;
  blink?: number; sil?: string; eyeGlow?: boolean; shadow?: boolean; tailAmp?: number; look?: number;
};

const ik = (r: Pt, t: Pt, l1: number, l2: number, dir: number): Pt => {
  let dx = t[0] - r[0], dy = t[1] - r[1];
  let d = Math.hypot(dx, dy);
  const mx = l1 + l2 - 0.5;
  if (d > mx) { dx *= mx / d; dy *= mx / d; d = mx; }
  const a = Math.acos(clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1));
  const b = Math.atan2(dy, dx) + a * dir;
  return [r[0] + Math.cos(b) * l1, r[1] + Math.sin(b) * l1];
};

type Shape = { d: string; fill: string; tf?: string };
const TwoPass: React.FC<{ shapes: Shape[]; sw: number; ink: string; children?: React.ReactNode }> = ({ shapes, sw, ink, children }) => (
  <g>
    {shapes.map((s, i) => <path key={`o${i}`} d={s.d} transform={s.tf} fill={ink} stroke={ink} strokeWidth={sw * 2} strokeLinejoin="round" />)}
    {shapes.map((s, i) => <path key={`f${i}`} d={s.d} transform={s.tf} fill={s.fill} />)}
    {children}
  </g>
);

export const Beast: React.FC<BeastProps> = ({ kind = 'procy', x, y, s = 1, flip, phase, run, head = 0, jaw = 0, crouch = 0, f = 0, blink = 0, sil, eyeGlow, shadow = true, tailAmp = 1, look = 0 }) => {
  const P = SPEC[kind];
  const uid = useId().replace(/:/g, '');
  const C = sil ? { base: sil, back: sil, band: sil, belly: sil, leg: sil, far: sil, eye: P.col.eye } : P.col;
  const ink = sil ?? INK;
  const sw = Math.max(2.2, 3.2 / Math.sqrt(s));
  const moving = phase !== undefined;
  const ph = phase ?? 0;
  const breath = Math.sin(f / 14) * 1.5;
  const bob = moving ? Math.sin(ph * Math.PI * 4) * (run ? 7 : 3) : breath * 0.6;
  const pitch = moving && run ? Math.sin(ph * Math.PI * 2) * 5 : 0;
  const stand = P.stand * (1 - crouch * 0.45);
  const hip: Pt = [-P.L / 2 + 8, -stand + bob - pitch];
  const sh: Pt = [P.L / 2 - 8, -stand - bob * 0.6 + pitch];
  const bh = P.bh;
  const hc = hip[1] - bh * 0.18, sc = sh[1] - bh * 0.18, mc = (hc + sc) / 2;
  const nRaise = -bh * 0.1 - crouch * 4;
  const N: Pt = [P.L / 2 + P.neck, sc + nRaise];
  const sag = bh * 0.06 + (moving ? Math.sin(ph * Math.PI * 4 + 1) * 2 : breath);
  const torso = smooth([
    [-P.L / 2 - bh * 0.5, hc - bh * 0.12], [-P.L / 2 - bh * 0.05, hc - bh * 0.5], [-P.L * 0.1, mc - bh * 0.56], [P.L / 2 - bh * 0.15, sc - bh * 0.52],
    [N[0] - 4, N[1] - bh * 0.3], [N[0] + 16, N[1] + 2], [N[0] - 6, N[1] + bh * 0.34], [P.L / 2 - 4, sc + bh * 0.46],
    [0, mc + bh * 0.5 + sag], [-P.L / 2 + 6, hc + bh * 0.44], [-P.L / 2 - bh * 0.42, hc + bh * 0.24],
  ], true, 0.9);

  // tail
  const n = 8;
  const T0: Pt = [-P.L / 2 - bh * 0.34, hc + bh * 0.04];
  const chain: Pt[] = [T0];
  let th0 = 0;
  for (let i = 0; i < n; i++) {
    const wave = Math.sin((moving ? ph * Math.PI * 2 : f / 22) - i * 0.75) * 0.16 * (i / n + 0.25) * tailAmp * (run ? 1.8 : 1);
    const th = Math.PI - 0.28 + 0.085 * i + wave - crouch * 0.05 * i;
    if (i === 0) th0 = th;
    const p = chain[i];
    chain.push([p[0] + (Math.cos(th) * P.tailL) / n, p[1] + (Math.sin(th) * P.tailL) / n]);
  }
  void th0;
  const tw = (i: number) => P.tailW * Math.pow(1 - i / (n + 0.4), 0.85) + 1.5;
  const tl: Pt[] = [], tr: Pt[] = [];
  for (let i = 0; i <= n; i++) {
    const a = chain[Math.max(0, i - 1)], b = chain[Math.min(n, i + 1)];
    const l = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1;
    const nx = -(b[1] - a[1]) / l, ny = (b[0] - a[0]) / l;
    tl.push([chain[i][0] + nx * tw(i), chain[i][1] + ny * tw(i)]);
    tr.unshift([chain[i][0] - nx * tw(i), chain[i][1] - ny * tw(i)]);
  }
  const tail = smooth([[T0[0] + bh * 0.3, T0[1]], ...tl, ...tr], true, 0.8);

  // legs
  const S = P.stride * (run ? 1.7 : 1), lift = P.lift * (run ? 1.5 : 1);
  const foot = (off: number, jx: number, rest: number): { p: Pt; tilt: number } => {
    if (!moving) return { p: [jx + rest, -P.legW * 0.42], tilt: 0 };
    const u = (((ph + off) % 1) + 1) % 1;
    if (u < 0.6) { const k = u / 0.6; return { p: [jx + rest * 0.5 + S / 2 - S * k, -P.legW * 0.42], tilt: 0 }; }
    const k = (u - 0.6) / 0.4;
    const e = k * k * (3 - 2 * k);
    return { p: [jx + rest * 0.5 - S / 2 + S * e, -P.legW * 0.42 - Math.sin(Math.PI * k) * lift], tilt: Math.sin(Math.PI * k) * 28 };
  };
  const leg = (joint: Pt, off: number, rest: number, dir: number, far: boolean): Shape[] => {
    const ft = foot(off, joint[0], rest);
    const knee = ik(joint, ft.p, P.l1, P.l2, dir);
    const c1 = far ? C.far : C.leg, w = P.legW;
    const fw = w * 1.9, fh = w * 0.42;
    const [ax, ay] = ft.p;
    const footD = capsule([ax - fw * 0.12, ay], [ax + fw * 0.7, ay + fh * 0.35], w * 0.5, w * 0.34);
    return [
      { d: capsule(joint, knee, w * 1.08, w * 0.8), fill: c1 },
      { d: capsule(knee, ft.p, w * 0.78, w * 0.56), fill: c1 },
      { d: footD, fill: c1, tf: `rotate(${ft.tilt.toFixed(1)} ${ax.toFixed(1)} ${ay.toFixed(1)})` },
    ];
  };
  const fJ: Pt = [sh[0], sh[1] + bh * 0.12], hJ: Pt = [hip[0], hip[1] + bh * 0.12];
  const farOff: Pt = [P.L * 0.05, -3];
  const farLegs = [...leg([fJ[0] + farOff[0], fJ[1] + farOff[1]], 0.5, P.l1 * 0.2 - 10, 1, true), ...leg([hJ[0] + farOff[0], hJ[1] + farOff[1]], 0, -P.l1 * 0.1 - 12, -1, true)];
  const nearLegs = [...leg(fJ, 0, P.l1 * 0.2 + 12, 1, false), ...leg(hJ, 0.5, -P.l1 * 0.1 + 12, -1, false)];

  // head (template 150 x 70)
  const hx = P.headL / 150, hy = P.headH / 70;
  const hp = (pts: Pt[]) => pts.map(([a, b]) => [a * hx, b * hy] as Pt);
  const skull = smooth(hp([[-20, 26], [-24, -8], [-10, -34], [30, -46], [78, -42], [118, -31], [146, -21], [157, -7], [153, 7], [120, 10], [70, 12], [18, 15]]), true, 0.85);
  const jawD = smooth(hp([[4, 9], [70, 10], [130, 8], [149, 8], [147, 18], [128, 26], [70, 32], [20, 35], [-12, 30], [-16, 14]]), true, 0.85);
  const jp: Pt = [6 * hx, 14 * hy];
  const jawTf = `rotate(${jaw.toFixed(1)} ${jp[0].toFixed(1)} ${jp[1].toFixed(1)})`;
  const jr = (jaw * Math.PI) / 180;
  const jt: Pt = [jp[0] + Math.cos(jr) * 142 * hx, jp[1] + Math.sin(jr) * 142 * hx - 4];
  const inside = poly([[4 * hx, 10 * hy], [150 * hx, 6 * hy], jt, [jp[0] + Math.cos(jr) * 40 * hx, jp[1] + Math.sin(jr) * 40 * hx + 6]]);
  const peg = (px: number, py: number, w: number, len: number, cusp = false) => cusp
    ? `M${px - w} ${py}L${px - w * 0.6} ${py + len * 0.55}L${px - w * 0.3} ${py + len * 0.3}L${px} ${py + len}L${px + w * 0.3} ${py + len * 0.3}L${px + w * 0.6} ${py + len * 0.55}L${px + w} ${py}Z`
    : `M${px - w} ${py}L${px} ${py + len}L${px + w} ${py}Z`;
  const up: string[] = [], lo: string[] = [];
  if (P.teeth) {
    for (let i = 0; i < 5; i++) up.push(peg((150 - i * 5.5) * hx, (6.5 + i * 0.3) * hy, 2.6 * hx, 7 * hy));
    for (let i = 0; i < 3; i++) up.push(peg((120 - i * 4) * hx - 14 * hx, 10 * hy, 1.8 * hx, 4 * hy));
    for (let i = 0; i < 7; i++) up.push(peg((92 - i * 9) * hx, (10.5 + i * 0.3) * hy, 4 * hx, 6.5 * hy, true));
    for (let i = 0; i < 4; i++) lo.push(peg((146 - i * 5.5) * hx, 9 * hy, 2.4 * hx, -6.5 * hy));
    lo.push(peg(120 * hx, 9 * hy, 4 * hx, -P.fang * 0.55));
    for (let i = 0; i < 7; i++) lo.push(peg((96 - i * 9) * hx, 10 * hy, 4 * hx, -6 * hy, true));
  }
  const fx = 116 * hx, fy = 8 * hy, fg = P.fang;
  const fang = `M${fx - 5.5 * hx} ${fy}Q${fx - 5 * hx} ${fy + fg * 0.7} ${fx - 7 * hx} ${fy + fg}Q${fx + 5 * hx} ${fy + fg * 0.55} ${fx + 6.5 * hx} ${fy}Z`;
  const ex = 84 * hx + look * 2, ey = -21 * hy;
  const er = Math.min(hx, hy) * (kind === 'gorgon' ? 0.75 : 1);
  const headRot = head + (moving ? Math.sin(ph * Math.PI * 4 + 0.5) * 2 : Math.sin(f / 31) * 1.2);
  const headTf = `translate(${N[0].toFixed(1)} ${N[1].toFixed(1)}) rotate(${headRot.toFixed(1)})`;

  const bands: React.ReactNode[] = [];
  const nb = Math.round(P.L / 38);
  for (let i = 0; i < nb; i++) {
    const bx = lerp(-P.L / 2 - bh * 0.2, P.L / 2 + P.neck * 0.3, i / (nb - 1));
    bands.push(<path key={i} d={leaf([bx + 6, mc - bh * 0.7], [bx - 10 + (i % 2) * 8, mc + bh * (0.02 + (i % 3) * 0.08)], bh * 0.085, 4)} fill={C.band} />);
  }
  const tailBands: React.ReactNode[] = [];
  for (let i = 0; i < n; i++) {
    const a = chain[i], b = chain[i + 1];
    const m: Pt = [lerp(a[0], b[0], 0.5), lerp(a[1], b[1], 0.5)];
    const l = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1;
    const nx = -(b[1] - a[1]) / l, ny = (b[0] - a[0]) / l;
    tailBands.push(<path key={i} d={leaf([m[0] + nx * tw(i) * 1.3, m[1] + ny * tw(i) * 1.3], [m[0] - nx * tw(i) * 0.1 + 4, m[1] - ny * tw(i) * 0.1], P.tailL / n * 0.2)} fill={C.band} />);
  }
  const knobs: React.ReactNode[] = [];
  if (kind === 'pareia' && !sil) for (let i = 0; i < 9; i++) knobs.push(<circle key={i} cx={lerp(-P.L / 2, P.L / 2, i / 8)} cy={mc - bh * (0.5 + 0.06 * Math.sin(i * 1.3)) + 6} r={bh * 0.045} fill={C.belly} stroke={ink} strokeWidth={2} />);

  const bodyShapes: Shape[] = [
    { d: tail, fill: C.base }, { d: torso, fill: C.base },
    ...(jaw > 0.5 ? [{ d: inside, fill: sil ?? '#5a1530', tf: headTf }] : []),
  ];

  return (
    <g transform={`translate(${x.toFixed(1)} ${y.toFixed(1)}) scale(${flip ? -s : s} ${s})`}>
      {shadow && !sil && <ellipse cx={0} cy={3} rx={P.L * 0.85} ry={P.stand * 0.16 + 6} fill="#0a0814" opacity={0.28} />}
      <TwoPass shapes={farLegs} sw={sw} ink={ink} />
      <TwoPass shapes={bodyShapes} sw={sw} ink={ink}>
        {!sil && (
          <>
            <clipPath id={`t${uid}`}><path d={torso} /></clipPath>
            <clipPath id={`l${uid}`}><path d={tail} /></clipPath>
            <g clipPath={`url(#l${uid})`}>
              <path d={smooth([...tl, ...chain.slice().reverse()], true, 0.8)} fill={C.back} />
              {tailBands}
            </g>
            <g clipPath={`url(#t${uid})`}>
              <rect x={-P.L} y={mc - bh} width={P.L * 2.4} height={bh * 0.86} fill={C.back} />
              <rect x={-P.L} y={mc + bh * 0.2} width={P.L * 2.4} height={bh} fill={C.belly} />
              {bands}
              <path d={leaf([-P.L / 2, mc - bh * 0.44], [P.L / 2, mc - bh * 0.42], bh * 0.07, -bh * 0.05)} fill="#ffffff" opacity={0.22} />
              <rect x={-P.L} y={mc + bh * 0.32} width={P.L * 2.4} height={bh} fill="#1a0f24" opacity={0.28} />
            </g>
            {knobs}
          </>
        )}
      </TwoPass>
      {/* head */}
      <g transform={headTf}>
        {jaw > 0.5 && P.teeth && !sil && (
          <>
            {up.map((d, i) => <path key={`u${i}`} d={d} fill="#fdf8e6" stroke={INK} strokeWidth={0.9} strokeLinejoin="round" />)}
            <g transform={jawTf}>{lo.map((d, i) => <path key={`l${i}`} d={d} fill="#fdf8e6" stroke={INK} strokeWidth={0.9} strokeLinejoin="round" />)}</g>
          </>
        )}
        <path d={jawD} transform={jawTf} fill={ink} stroke={ink} strokeWidth={sw * 2} strokeLinejoin="round" />
        <path d={skull} fill={ink} stroke={ink} strokeWidth={sw * 2} strokeLinejoin="round" />
        {/* cover the neck seam */}
        <path d={capsule([-30 * hx, -4 * hy], [10 * hx, -4 * hy], 24 * hy, 26 * hy)} fill={C.base} />
        <path d={jawD} transform={jawTf} fill={sil ?? C.belly} />
        <path d={skull} fill={C.base} />
        {!sil && (
          <>
            <clipPath id={`s${uid}`}><path d={skull} /></clipPath>
            <g clipPath={`url(#s${uid})`}>
              <path d={smooth(hp([[-30, -50], [160, -50], [160, -16], [120, -22], [70, -30], [20, -24], [-30, -14]]), true, 0.7)} fill={C.back} />
              <path d={leaf([36 * hx, -52 * hy], [28 * hx, -16 * hy], 7 * hx, 3)} fill={C.band} />
              <path d={leaf([8 * hx, -50 * hy], [0, -10 * hy], 7 * hx, 3)} fill={C.band} />
              <path d={leaf([112 * hx, -40 * hy], [108 * hx, -18 * hy], 5 * hx, 2)} fill={C.band} />
              <path d={leaf([10 * hx, -38 * hy], [120 * hx, -30 * hy], 4 * hy, -3)} fill="#ffffff" opacity={0.25} />
            </g>
            <path d={smooth(hp([[152, 7], [120, 10], [70, 12], [22, 14], [10, 10]]), false)} fill="none" stroke={INK} strokeWidth={sw * 0.8} strokeLinecap="round" />
            {jaw > 3 && <path d={smooth(hp([[6, 10], [70, 10], [130, 8], [148, 8]]), false)} transform={jawTf} fill="none" stroke={INK} strokeWidth={sw * 0.8} strokeLinecap="round" />}
            <path d={`M${ex - 17 * er} ${ey - 13 * er}Q${ex} ${ey - 19 * er} ${ex + 19 * er} ${ey - 9 * er}`} fill="none" stroke={INK} strokeWidth={sw * 1.25} strokeLinecap="round" />
            <ellipse cx={ex} cy={ey} rx={11 * er} ry={9 * er * Math.max(0.08, 1 - blink)} fill={C.eye} stroke={INK} strokeWidth={sw * 0.75} />
            <ellipse cx={ex + look * 2} cy={ey} rx={4.6 * er} ry={6.6 * er * Math.max(0.08, 1 - blink)} fill="#0b0810" />
            {blink < 0.5 && <circle cx={ex - 3 * er + look * 2} cy={ey - 3.2 * er} r={2.3 * er} fill="#fff" />}
            <ellipse cx={147 * hx} cy={-10 * hy} rx={3.4 * hx} ry={2 * hy} fill={INK} transform={`rotate(-30 ${147 * hx} ${-10 * hy})`} />
            {kind === 'procy' && [[128, -2], [135, 2], [121, 2], [128, 5]].map(([a, b], i) => <circle key={i} cx={a * hx} cy={b * hy - 4} r={1.3} fill={INK} opacity={0.55} />)}
            <path d={`M${40 * hx} ${6 * hy}q${10 * hx} ${6 * hy} ${4 * hx} ${16 * hy}`} fill="none" stroke={INK} strokeWidth={sw * 0.6} strokeLinecap="round" opacity={0.6} />
          </>
        )}
        {sil && eyeGlow && <ellipse cx={ex} cy={ey} rx={9 * er} ry={5 * er} fill={P.col.eye} />}
        {fg > 0 && <path d={fang} fill={sil && !eyeGlow ? sil : '#fdf8e6'} stroke={ink} strokeWidth={sw * 0.7} strokeLinejoin="round" />}
        {kind === 'dicyn' && !sil && <path d={poly(hp([[150, -8], [162, 4], [150, 14], [136, 8]]))} fill="#3a3440" stroke={INK} strokeWidth={sw * 0.7} strokeLinejoin="round" />}
      </g>
      <TwoPass shapes={nearLegs} sw={sw} ink={ink} />
    </g>
  );
};
