import React from 'react';
import { INK, Pt, capsule, leaf, lerp, mix, poly, rng, scallop, smooth } from './lib';

export type Pal = {
  sky: [string, string, string];
  far: string; far2: string;
  leafD: string; leafM: string; leafL: string; leafH: string;
  alt: string; altL: string;
  trunk: string; trunkL: string;
  ground: string; groundD: string; groundL: string;
  water: string; waterL: string;
  rock: string; rockL: string; rockD: string;
  haze: string; ink: string;
};

export const DAY: Pal = {
  sky: ['#2f8fd6', '#6fc7e8', '#c9f0e4'],
  far: '#7d8fd0', far2: '#9fb4e0',
  leafD: '#0a5238', leafM: '#16a34e', leafL: '#5fe04a', leafH: '#d8ff6a',
  alt: '#087f86', altL: '#35e8d0',
  trunk: '#5a4636', trunkL: '#a08660',
  ground: '#48b83a', groundD: '#1c7038', groundL: '#b4f25a',
  water: '#12b4d8', waterL: '#b8fff4',
  rock: '#8f7fb6', rockL: '#cbbfe6', rockD: '#4b3f78',
  haze: '#d8f5ee', ink: INK,
};

export const VIOLET: Pal = {
  sky: ['#3b2a8c', '#8a6fd8', '#f0a8c8'],
  far: '#6a55b8', far2: '#9a82d8',
  leafD: '#123a52', leafM: '#1f7a70', leafL: '#45c0a0', leafH: '#b8f0d0',
  alt: '#4a2f8a', altL: '#a070e0',
  trunk: '#3a2c48', trunkL: '#7a6690',
  ground: '#3f9a58', groundD: '#1d5a52', groundL: '#9ae070',
  water: '#3f8fd8', waterL: '#c8d8ff',
  rock: '#7a68b0', rockL: '#c0b0ec', rockD: '#3a2c68',
  haze: '#e8c8f0', ink: INK,
};

export const DUSK: Pal = {
  sky: ['#140f2e', '#3a2460', '#b04a5a'],
  far: '#2c2452', far2: '#463a78',
  leafD: '#0a1f2c', leafM: '#123f48', leafL: '#1f6a60', leafH: '#4fa890',
  alt: '#1c1840', altL: '#4a3f88',
  trunk: '#1c1626', trunkL: '#4a3c58',
  ground: '#1f4a44', groundD: '#0f2a30', groundL: '#3f7a5c',
  water: '#2a3f88', waterL: '#f0a080',
  rock: '#3c3466', rockL: '#7a68a8', rockD: '#1a1436',
  haze: '#c05a70', ink: '#0a0810',
};

export const DRY: Pal = {
  sky: ['#1f6fd0', '#4fa8ec', '#bfe4f8'],
  far: '#a9b8e8', far2: '#c8d4f4',
  leafD: '#1f5a34', leafM: '#3f9a48', leafL: '#8ad058', leafH: '#d8f080',
  alt: '#5a7a34', altL: '#a8c858',
  trunk: '#6a4a34', trunkL: '#b08a5c',
  ground: '#e0b070', groundD: '#b87a4c', groundL: '#f6dca0',
  water: '#3fb0d8', waterL: '#c8f0f8',
  rock: '#c88a5c', rockL: '#f0c898', rockD: '#8a5a70',
  haze: '#f8e8d0', ink: INK,
};

const SW = 4;

/** foliage clump: black base, colour on top, light on top of that, ink ticks */
export const Clump: React.FC<{ x: number; y: number; r: number; seed: number; pal: Pal; alt?: boolean; ry?: number }> = ({ x, y, r, seed, pal, alt, ry }) => {
  const rr = rng(seed);
  const lobes = 7 + Math.floor(rr() * 4);
  const h = ry ?? r * (0.7 + rr() * 0.2);
  const cD = alt ? pal.alt : pal.leafM, cL = alt ? pal.altL : pal.leafL;
  const ticks: React.ReactNode[] = [];
  for (let i = 0; i < 4; i++) {
    const a = Math.PI * (0.15 + rr() * 0.7), d = 0.25 + rr() * 0.5;
    const tx = x + Math.cos(a) * r * d - r * 0.1, ty = y + Math.sin(a) * h * d * 0.9;
    const s = r * 0.14;
    ticks.push(<path key={i} d={`M${tx - s} ${ty}q${s} ${s * 0.9} ${s * 2} 0`} fill="none" stroke={pal.ink} strokeWidth={Math.max(1.5, r * 0.035)} strokeLinecap="round" />);
  }
  return (
    <g>
      <path d={scallop(x, y, r, h, lobes, seed)} fill={pal.leafD} stroke={pal.ink} strokeWidth={SW} strokeLinejoin="round" />
      <path d={scallop(x - r * 0.06, y - h * 0.12, r * 0.86, h * 0.8, lobes, seed + 1)} fill={cD} />
      <path d={scallop(x - r * 0.2, y - h * 0.32, r * 0.58, h * 0.5, Math.max(5, lobes - 2), seed + 2)} fill={cL} />
      <path d={scallop(x - r * 0.3, y - h * 0.5, r * 0.26, h * 0.2, 5, seed + 3)} fill={pal.leafH} opacity={0.85} />
      {ticks}
    </g>
  );
};

/** Glossopteris: irregular trunk, lumpy crown, hanging tongue leaves */
export const Glosso: React.FC<{ x: number; y: number; h: number; seed: number; pal: Pal; alt?: boolean }> = React.memo(({ x, y, h, seed, pal, alt }) => {
  const r = rng(seed);
  const lean = (r() - 0.5) * h * 0.25;
  const tw = h * (0.055 + r() * 0.025);
  const top: Pt = [x + lean, y - h * 0.62];
  const midp: Pt = [x + lean * 0.35 + (r() - 0.5) * tw * 2, y - h * 0.32];
  const trunk = smooth([
    [x - tw * 1.9, y + 4], [x - tw * 1.05, y - h * 0.07], [midp[0] - tw * 0.8, midp[1]], [top[0] - tw * 0.55, top[1]],
    [top[0] + tw * 0.55, top[1]], [midp[0] + tw * 0.8, midp[1]], [x + tw * 1.05, y - h * 0.07], [x + tw * 2.1, y + 4],
  ], true, 0.9);
  const hi = smooth([[x - tw * 0.9, y - h * 0.05], [midp[0] - tw * 0.55, midp[1]], [top[0] - tw * 0.3, top[1]], [top[0], top[1]], [midp[0] - tw * 0.1, midp[1]], [x - tw * 0.2, y - h * 0.05]], true, 0.9);
  const cr = h * 0.2;
  const clumps: { x: number; y: number; r: number; s: number }[] = [];
  const n = 5 + Math.floor(r() * 3);
  for (let i = 0; i < n; i++) {
    const a = Math.PI + (Math.PI * (i + 0.5)) / n + (r() - 0.5) * 0.3;
    const d = cr * (0.9 + r() * 0.7);
    clumps.push({ x: top[0] + Math.cos(a) * d * 1.25, y: top[1] - cr * 0.3 + Math.sin(a) * d * 0.8, r: cr * (0.75 + r() * 0.5), s: seed * 31 + i });
  }
  clumps.push({ x: top[0] + (r() - 0.5) * cr, y: top[1] - cr * 0.1, r: cr * 1.1, s: seed * 31 + 99 });
  clumps.sort((a, b) => a.y - b.y);
  // branches
  const br: React.ReactNode[] = [];
  clumps.slice(0, 3).forEach((c, i) => {
    br.push(<path key={i} d={`M${top[0]} ${top[1] + h * 0.06}Q${lerp(top[0], c.x, 0.4)} ${top[1] - 4} ${c.x} ${c.y}`} stroke={pal.ink} strokeWidth={tw * 0.9} fill="none" strokeLinecap="round" />);
  });
  // tongue leaves hanging under the crown
  const tongues: React.ReactNode[] = [];
  for (let i = 0; i < 12; i++) {
    const c = clumps[Math.floor(r() * clumps.length)];
    const lx = c.x + (r() - 0.5) * c.r * 1.7, ly = c.y + c.r * (0.45 + r() * 0.2);
    const len = cr * (0.45 + r() * 0.4), ang = Math.PI / 2 + (r() - 0.5) * 0.9;
    const b: Pt = [lx + Math.cos(ang) * len, ly + Math.sin(ang) * len];
    tongues.push(<path key={i} d={leaf([lx, ly], b, len * 0.22, len * 0.08, 0.6)} fill={i % 3 ? pal.leafM : pal.leafL} stroke={pal.ink} strokeWidth={2.5} strokeLinejoin="round" />);
  }
  const marks: React.ReactNode[] = [];
  for (let i = 0; i < 5; i++) {
    const t = 0.1 + r() * 0.75;
    const px = lerp(x, top[0], t) + (r() - 0.3) * tw * 0.6, py = lerp(y, top[1], t);
    marks.push(<path key={i} d={`M${px} ${py}l${(r() - 0.5) * 6} ${-h * 0.035}`} stroke={pal.ink} strokeWidth={2.5} strokeLinecap="round" />);
  }
  return (
    <g>
      {br}
      <path d={trunk} fill={pal.trunk} stroke={pal.ink} strokeWidth={SW + 1} strokeLinejoin="round" />
      <path d={hi} fill={pal.trunkL} opacity={0.9} />
      <path d={hi} fill={pal.ink} opacity={0.3} transform={`translate(${tw * 1.05} 0)`} />
      {marks}
      {tongues}
      {clumps.map((c, i) => <Clump key={i} x={c.x} y={c.y} r={c.r} seed={c.s} pal={pal} alt={alt} />)}
    </g>
  );
});

/** árbol alto de copa chata (como paraguas): tronco cilíndrico con raíces y copa en racimos */
export const Umbrella: React.FC<{ x: number; y: number; h: number; seed: number; pal: Pal }> = React.memo(({ x, y, h, seed, pal }) => {
  const r = rng(seed);
  const lean = (r() - 0.5) * h * 0.12;
  const tw = h * 0.028;
  const top: Pt = [x + lean, y - h * 0.82];
  const mid: Pt = [x + lean * 0.3 + (r() - 0.5) * tw * 3, y - h * 0.42];
  const trunk = smooth([[x - tw * 3.2, y + 4], [x - tw * 1.2, y - h * 0.06], [mid[0] - tw * 0.8, mid[1]], [top[0] - tw * 0.9, top[1]], [top[0] - tw * 3.4, top[1] - h * 0.07], [top[0] + tw * 3.4, top[1] - h * 0.07], [top[0] + tw * 0.9, top[1]], [mid[0] + tw * 0.8, mid[1]], [x + tw * 1.2, y - h * 0.06], [x + tw * 3.4, y + 4]], true, 0.75);
  const cw = h * (0.2 + r() * 0.07), ch = h * 0.075;
  const cy = top[1] - h * 0.08;
  const clumps = Array.from({ length: 7 }, (_, i) => ({ cx: top[0] + (i / 6 - 0.5) * cw * 1.75 + (r() - 0.5) * cw * 0.1, cy: cy - ch * (0.5 + Math.sin((i / 6) * Math.PI) * 0.7) + (r() - 0.5) * ch * 0.3, rr: cw * (0.26 + r() * 0.1), s: seed * 17 + i }));
  return (
    <g>
      <path d={trunk} fill={pal.trunk} stroke={pal.ink} strokeWidth={SW} strokeLinejoin="round" />
      <path d={smooth([[x - tw * 0.9, y - h * 0.05], [mid[0] - tw * 0.6, mid[1]], [top[0] - tw * 0.7, top[1]], [top[0] - tw * 0.1, top[1]], [mid[0] - tw * 0.05, mid[1]], [x - tw * 0.1, y - h * 0.05]], true, 0.75)} fill={pal.trunkL} />
      <path d={smooth([[x + tw * 1.1, y - h * 0.05], [mid[0] + tw * 0.75, mid[1]], [top[0] + tw * 0.85, top[1]], [top[0] + tw * 0.35, top[1]], [mid[0] + tw * 0.3, mid[1]], [x + tw * 0.5, y - h * 0.05]], true, 0.75)} fill={pal.ink} opacity={0.35} />
      <path d={scallop(top[0], cy + ch * 0.25, cw, ch * 0.75, 12, seed + 5)} fill={pal.leafD} stroke={pal.ink} strokeWidth={SW} strokeLinejoin="round" />
      {[-0.7, -0.35, 0, 0.35, 0.7].map((k, i) => <path key={i} d={`M${top[0] + k * tw * 3} ${top[1] - h * 0.06}Q${top[0] + k * cw * 0.6} ${cy + ch * 0.5} ${top[0] + k * cw * 1.05} ${cy + ch * 0.1}`} stroke={pal.ink} strokeWidth={2.2} fill="none" opacity={0.5} />)}
      {clumps.sort((a, b) => a.cy - b.cy).map((c, i) => <Clump key={i} x={c.cx} y={c.cy} r={c.rr} ry={c.rr * 0.62} seed={c.s} pal={pal} />)}
    </g>
  );
});

/** Calamites-like giant horsetail: segmented stem with whorls */
export const Calamite: React.FC<{ x: number; y: number; h: number; seed: number; pal: Pal }> = React.memo(({ x, y, h, seed, pal }) => {
  const r = rng(seed);
  const segs = Math.max(4, Math.round(h / 55));
  const lean = (r() - 0.5) * h * 0.12;
  const w = Math.max(5, h * 0.022);
  const out: React.ReactNode[] = [];
  for (let i = segs - 1; i >= 0; i--) {
    const t0 = i / segs, t1 = (i + 1) / segs;
    const a: Pt = [x + lean * t0 * t0, y - h * t0], b: Pt = [x + lean * t1 * t1, y - h * t1];
    const ww = w * (1 - t0 * 0.6);
    if (i > 0) {
      const nl = 7;
      const len = h * 0.16 * (1 - t0 * 0.45) * (0.8 + r() * 0.4);
      for (let k = 0; k < nl; k++) {
        const ang = -Math.PI * (0.08 + (0.84 * k) / (nl - 1));
        const e: Pt = [a[0] + Math.cos(ang) * len, a[1] + Math.sin(ang) * len * 0.75 - len * 0.1];
        out.push(<path key={`l${i}-${k}`} d={leaf(a, e, len * 0.09, len * 0.12 * (k < nl / 2 ? 1 : -1))} fill={k % 2 ? pal.alt : pal.altL} stroke={pal.ink} strokeWidth={2} strokeLinejoin="round" />);
      }
    }
    out.push(<path key={`s${i}`} d={capsule(a, b, ww, ww * 0.85)} fill={pal.alt} stroke={pal.ink} strokeWidth={3} />);
    out.push(<path key={`h${i}`} d={capsule([a[0] - ww * 0.35, a[1] - 4], [b[0] - ww * 0.3, b[1] + 4], ww * 0.3, ww * 0.25)} fill={pal.altL} />);
  }
  return <g>{out}</g>;
});

/** rosette of bold tongue/fern fronds */
export const Fern: React.FC<{ x: number; y: number; s: number; seed: number; pal: Pal; alt?: boolean }> = React.memo(({ x, y, s, seed, pal, alt }) => {
  const r = rng(seed);
  const n = 7 + Math.floor(r() * 5);
  const fr: { a: number; len: number; k: number }[] = [];
  for (let i = 0; i < n; i++) fr.push({ a: -Math.PI * (0.06 + (0.88 * i) / (n - 1)) + (r() - 0.5) * 0.15, len: s * (0.7 + r() * 0.5), k: i });
  fr.sort((p, q) => Math.abs(Math.cos(q.a)) - Math.abs(Math.cos(p.a)));
  const cM = alt ? pal.alt : pal.leafM, cL = alt ? pal.altL : pal.leafL;
  return (
    <g>
      {fr.map((f, i) => {
        const side = Math.cos(f.a) > 0 ? 1 : -1;
        const droop = f.len * 0.35 * Math.abs(Math.cos(f.a));
        const e: Pt = [x + Math.cos(f.a) * f.len, y + Math.sin(f.a) * f.len + droop];
        const bend = -side * f.len * 0.28 * Math.abs(Math.cos(f.a));
        const w = f.len * 0.13;
        const mid: Pt = [(x + e[0]) / 2 - (-(e[1] - y) / f.len) * bend * 0.5, (y + e[1]) / 2 - ((e[0] - x) / f.len) * bend * 0.5];
        return (
          <g key={i}>
            <path d={leaf([x, y], e, w, bend)} fill={pal.leafD} stroke={pal.ink} strokeWidth={3.5} strokeLinejoin="round" />
            <path d={leaf([lerp(x, e[0], 0.08), lerp(y, e[1], 0.08) - 2], [lerp(x, e[0], 0.95), lerp(y, e[1], 0.95)], w * 0.62, bend * 1.08)} fill={i % 2 ? cM : cL} />
            <path d={`M${x} ${y}Q${mid[0]} ${mid[1]} ${e[0]} ${e[1]}`} fill="none" stroke={pal.ink} strokeWidth={1.6} opacity={0.6} />
          </g>
        );
      })}
    </g>
  );
});

/** small horsetail shoots / reeds */
export const Reeds: React.FC<{ x: number; y: number; s: number; seed: number; pal: Pal }> = React.memo(({ x, y, s, seed, pal }) => {
  const r = rng(seed);
  const n = 4 + Math.floor(r() * 5);
  const out: React.ReactNode[] = [];
  for (let i = 0; i < n; i++) {
    const bx = x + (r() - 0.5) * s * 0.9, hh = s * (0.5 + r() * 0.7), lean = (r() - 0.5) * hh * 0.25;
    const tip: Pt = [bx + lean, y - hh];
    out.push(<path key={`a${i}`} d={capsule([bx, y], tip, 4.5, 2)} fill={i % 2 ? pal.alt : pal.leafM} stroke={pal.ink} strokeWidth={2.5} />);
    const nodes = Math.floor(hh / 16);
    for (let k = 1; k < nodes; k++) {
      const t = k / nodes;
      const px = lerp(bx, tip[0], t), py = lerp(y, tip[1], t), l = 11 * (1 - t * 0.5);
      out.push(<path key={`n${i}-${k}`} d={`M${px - l} ${py - l * 0.5}L${px} ${py}L${px + l} ${py - l * 0.5}`} fill="none" stroke={pal.altL} strokeWidth={2.2} strokeLinecap="round" />);
    }
    out.push(<path key={`c${i}`} d={leaf([tip[0], tip[1] + 4], [tip[0] + lean * 0.1, tip[1] - 16], 5)} fill={pal.trunkL} stroke={pal.ink} strokeWidth={2} />);
  }
  return <g>{out}</g>;
});

/** angular rock with flat shading planes */
export const Rock: React.FC<{ x: number; y: number; w: number; h: number; seed: number; pal: Pal; moss?: boolean }> = React.memo(({ x, y, w, h, seed, pal, moss }) => {
  const r = rng(seed);
  const n = 8;
  const pts: Pt[] = [];
  for (let i = 0; i <= n; i++) {
    const a = Math.PI + (Math.PI * i) / n;
    const j = 0.78 + r() * 0.3;
    pts.push([x + Math.cos(a) * w * 0.5 * j, y + Math.sin(a) * h * j]);
  }
  pts[0] = [x - w * 0.52, y]; pts[n] = [x + w * 0.52, y];
  const d = poly(pts);
  const id = `rk${seed}-${Math.round(x)}-${Math.round(w)}`;
  const sx = x + w * (0.02 + r() * 0.1);
  return (
    <g>
      <clipPath id={id}><path d={d} /></clipPath>
      <path d={d} fill={pal.rock} stroke={pal.ink} strokeWidth={SW + 1} strokeLinejoin="round" />
      <g clipPath={`url(#${id})`}>
        <path d={poly([[sx, y - h * 1.2], [sx + w * 0.12, y - h * 0.55], [sx - w * 0.04, y - h * 0.3], [sx + w * 0.1, y + 5], [x + w, y + 5], [x + w, y - h * 1.2]])} fill={pal.rockD} />
        <path d={poly([[x - w * 0.6, y - h * 1.2], [sx - w * 0.1, y - h * 1.2], [sx - w * 0.22, y - h * 0.62], [x - w * 0.6, y - h * 0.5]])} fill={pal.rockL} />
        {moss && <path d={scallop(x, y - h * 1.02, w * 0.5, h * 0.22, 9, seed)} fill={pal.leafL} stroke={pal.ink} strokeWidth={3} />}
        <path d={`M${sx - w * 0.2} ${y - h * 0.5}l${w * 0.08} ${h * 0.2}l${-w * 0.05} ${h * 0.18}`} stroke={pal.ink} strokeWidth={2.5} fill="none" strokeLinecap="round" />
        <path d={`M${sx + w * 0.2} ${y - h * 0.7}l${-w * 0.03} ${h * 0.25}`} stroke={pal.ink} strokeWidth={2.5} fill="none" strokeLinecap="round" opacity={0.7} />
      </g>
    </g>
  );
});

/** tall mesa / butte with streaked sides and green cap */
export const Mesa: React.FC<{ x: number; y: number; w: number; h: number; seed: number; pal: Pal; cap?: boolean; flat?: boolean }> = React.memo(({ x, y, w, h, seed, pal, cap = true, flat }) => {
  const r = rng(seed);
  const tw = w * (0.5 + r() * 0.2);
  const L: Pt[] = [], R: Pt[] = [];
  const steps = 5;
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const ww = lerp(w, tw, Math.pow(t, 0.55)) / 2 + (r() - 0.5) * w * 0.06;
    L.push([x - ww, y - h * t]);
    R.unshift([x + ww * (0.9 + r() * 0.2), y - h * t]);
  }
  const top: Pt[] = [[x - tw * 0.3, y - h * 1.08], [x + tw * 0.1, y - h * 1.1], [x + tw * 0.38, y - h * 1.04]];
  const d = smooth([...L, ...top, ...R], true, 0.8);
  const id = `ms${seed}-${Math.round(x)}`;
  const streaks: React.ReactNode[] = [];
  if (!flat) for (let i = 0; i < 9; i++) {
    const sx = x + (r() - 0.5) * w * 0.8, sy = y - h * (0.15 + r() * 0.75), len = h * (0.1 + r() * 0.22);
    streaks.push(<path key={i} d={`M${sx} ${sy}q${(r() - 0.5) * 10} ${len * 0.5} ${(r() - 0.5) * 8} ${len}`} stroke={pal.rockD} strokeWidth={3 + r() * 4} fill="none" strokeLinecap="round" opacity={0.55} />);
  }
  return (
    <g>
      <clipPath id={id}><path d={d} /></clipPath>
      <path d={d} fill={pal.rock} stroke={flat ? 'none' : pal.ink} strokeWidth={SW + 1} strokeLinejoin="round" />
      {!flat && (
        <g clipPath={`url(#${id})`}>
          <path d={smooth([[x + w * 0.05, y - h * 1.2], [x + w * 0.14, y - h * 0.6], [x + w * 0.02, y - h * 0.3], [x + w * 0.2, y + 10], [x + w, y + 10], [x + w, y - h * 1.2]], true, 0.6)} fill={pal.rockD} opacity={0.75} />
          <path d={smooth([[x - w, y - h * 1.2], [x - tw * 0.2, y - h * 1.2], [x - tw * 0.36, y - h * 0.5], [x - w * 0.4, y - h * 0.1], [x - w, y]], true, 0.6)} fill={pal.rockL} opacity={0.8} />
          {streaks}
        </g>
      )}
      {cap && !flat && (
        <g>
          <path d={scallop(x + tw * 0.03, y - h * 1.07, tw * 0.52, h * 0.07 + 8, 8, seed + 5)} fill={pal.leafD} stroke={pal.ink} strokeWidth={3.5} />
          <path d={scallop(x, y - h * 1.085, tw * 0.44, h * 0.045 + 6, 7, seed + 6)} fill={pal.leafL} />
          <Clump x={x - tw * 0.15} y={y - h * 1.13} r={tw * 0.14} seed={seed + 8} pal={pal} />
          <Clump x={x + tw * 0.2} y={y - h * 1.12} r={tw * 0.1} seed={seed + 9} pal={pal} />
        </g>
      )}
    </g>
  );
});

/** cluster of pointed spires */
export const Spires: React.FC<{ x: number; y: number; w: number; h: number; seed: number; pal: Pal }> = React.memo(({ x, y, w, h, seed, pal }) => {
  const r = rng(seed);
  const n = 11;
  const sp: { cx: number; hh: number; ww: number; z: number }[] = [];
  for (let i = 0; i < n; i++) {
    const t = i / (n - 1);
    const cx = x + (t - 0.5) * w + (r() - 0.5) * w * 0.06;
    const hh = h * (0.35 + 0.65 * Math.sin(Math.PI * t) * (0.6 + r() * 0.4));
    sp.push({ cx, hh, ww: w * (0.1 + r() * 0.06), z: r() });
  }
  sp.sort((a, b) => b.hh - a.hh);
  return (
    <g>
      {sp.map((s, i) => {
        const d = poly([[s.cx - s.ww, y], [s.cx - s.ww * 0.85, y - s.hh * 0.55], [s.cx - s.ww * 0.35, y - s.hh * 0.95], [s.cx + s.ww * 0.05, y - s.hh], [s.cx + s.ww * 0.5, y - s.hh * 0.82], [s.cx + s.ww * 0.8, y - s.hh * 0.4], [s.cx + s.ww, y]]);
        const sh = poly([[s.cx + s.ww * 0.05, y - s.hh], [s.cx + s.ww * 0.5, y - s.hh * 0.82], [s.cx + s.ww * 0.8, y - s.hh * 0.4], [s.cx + s.ww, y], [s.cx + s.ww * 0.2, y], [s.cx + s.ww * 0.3, y - s.hh * 0.5]]);
        const ms = poly([[s.cx - s.ww * 0.5, y - s.hh * 0.86], [s.cx - s.ww * 0.35, y - s.hh * 0.95], [s.cx + s.ww * 0.05, y - s.hh], [s.cx + s.ww * 0.3, y - s.hh * 0.9], [s.cx + s.ww * 0.05, y - s.hh * 0.84], [s.cx - s.ww * 0.2, y - s.hh * 0.8]]);
        return (
          <g key={i}>
            <path d={d} fill={pal.rock} stroke={pal.ink} strokeWidth={SW} strokeLinejoin="round" />
            <path d={sh} fill={pal.rockD} />
            <path d={poly([[s.cx - s.ww * 0.8, y - s.hh * 0.5], [s.cx - s.ww * 0.35, y - s.hh * 0.9], [s.cx - s.ww * 0.25, y - s.hh * 0.5], [s.cx - s.ww * 0.6, y - s.hh * 0.2]])} fill={pal.rockL} opacity={0.8} />
            <path d={ms} fill={pal.leafH} stroke={pal.ink} strokeWidth={2} strokeLinejoin="round" />
            {i % 3 === 0 && <path d={leaf([s.cx - s.ww * 0.2, y], [s.cx - s.ww * 0.1, y - s.hh * 0.3], s.ww * 0.3)} fill={pal.ink} />}
          </g>
        );
      })}
    </g>
  );
});

export const Cloud: React.FC<{ x: number; y: number; s: number; seed: number; shade?: string; col?: string }> = React.memo(({ x, y, s, seed, shade = '#bfe0f4', col = '#ffffff' }) => {
  const r = rng(seed);
  const w = s * (1.6 + r() * 1.2);
  const top = scallop(x, y, w, s * 0.75, 7, seed, 1.35, Math.PI, Math.PI * 2);
  return (
    <g>
      <path d={top} fill={col} />
      <path d={scallop(x + w * 0.08, y, w * 0.85, s * 0.3, 6, seed + 1, 1.3, Math.PI, Math.PI * 2)} fill={shade} opacity={0.75} />
      <rect x={x - w * 0.9} y={y - 2} width={w * 1.8} height={s * 0.09 + 3} rx={s * 0.05} fill={col} />
    </g>
  );
});

/** one big Glossopteris tongue leaf with veins (detail shot) */
export const BigLeaf: React.FC<{ x: number; y: number; len: number; rot: number; pal: Pal }> = ({ x, y, len, rot, pal }) => {
  const a: Pt = [0, 0], b: Pt = [len, 0];
  const veins: React.ReactNode[] = [];
  for (let i = 1; i < 16; i++) {
    const t = i / 16, px = len * t, w = Math.sin(Math.PI * Math.pow(t, 0.8)) * len * 0.15;
    veins.push(<path key={i} d={`M${px - len * 0.05} 0Q${px} ${-w * 0.5} ${px + len * 0.04} ${-w}M${px - len * 0.05} 0Q${px} ${w * 0.5} ${px + len * 0.04} ${w}`} stroke={pal.leafD} strokeWidth={len * 0.006} fill="none" opacity={0.7} />);
  }
  return (
    <g transform={`translate(${x} ${y}) rotate(${rot})`}>
      <path d={leaf(a, b, len * 0.34, 0, 0.55)} fill={pal.leafD} stroke={pal.ink} strokeWidth={len * 0.014} strokeLinejoin="round" />
      <path d={leaf([len * 0.03, -len * 0.01], [len * 0.97, -len * 0.004], len * 0.28, -len * 0.012, 0.55)} fill={pal.leafM} />
      <path d={leaf([len * 0.1, -len * 0.03], [len * 0.9, -len * 0.02], len * 0.12, -len * 0.05, 0.5)} fill={pal.leafL} />
      {veins}
      <path d={`M0 0L${len} 0`} stroke={pal.ink} strokeWidth={len * 0.012} strokeLinecap="round" />
      <path d={`M${-len * 0.12} 0L0 0`} stroke={pal.ink} strokeWidth={len * 0.022} strokeLinecap="round" />
    </g>
  );
};

export { mix };
