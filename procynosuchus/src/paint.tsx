import React from 'react';
import { Pt, leaf, lerp, mix, rng, smooth } from './lib';

/** Pintura: masas con degradé + pinceladas, sin tinta. Las capas se pintan una vez y se guardan como imagen. */
export const PW = 3000, PH = 1080;

export const PaintDefs: React.FC = () => (
  <defs>
    <filter id="rough" x="-2%" y="-2%" width="104%" height="104%">
      <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves={3} seed={4} result="n" />
      <feDisplacementMap in="SourceGraphic" in2="n" scale={13} xChannelSelector="R" yChannelSelector="G" result="d" />
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={9} result="g" />
      <feColorMatrix in="g" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0.4 0 0 0 -0.16" result="ga" />
      <feComposite in="ga" in2="d" operator="in" result="gi" />
      <feBlend in="d" in2="gi" mode="soft-light" />
    </filter>
    <filter id="rough2" x="-2%" y="-2%" width="104%" height="104%">
      <feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves={3} seed={2} result="n" />
      <feDisplacementMap in="SourceGraphic" in2="n" scale={30} xChannelSelector="R" yChannelSelector="G" />
    </filter>
    <filter id="b2"><feGaussianBlur stdDeviation={2} /></filter>
    <filter id="b6" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation={6} /></filter>
    <filter id="b20" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation={20} /></filter>
    <filter id="b50" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation={50} /></filter>
  </defs>
);

export const LG: React.FC<{ id: string; stops: [number, string, number?][]; x1?: number; y1?: number; x2?: number; y2?: number }> = ({ id, stops, x1 = 0, y1 = 0, x2 = 0, y2 = 1 }) => (
  <linearGradient id={id} x1={x1} y1={y1} x2={x2} y2={y2}>{stops.map(([o, c, a], i) => <stop key={i} offset={o} stopColor={c} stopOpacity={a ?? 1} />)}</linearGradient>
);
export const RG: React.FC<{ id: string; stops: [number, string, number?][]; cx?: number; cy?: number; r?: number }> = ({ id, stops, cx = 0.35, cy = 0.3, r = 0.75 }) => (
  <radialGradient id={id} cx={cx} cy={cy} r={r}>{stops.map(([o, c, a], i) => <stop key={i} offset={o} stopColor={c} stopOpacity={a ?? 1} />)}</radialGradient>
);

/** pinceladas cortas; `at` devuelve posición y un valor de luz 0..1 que elige el color */
export const dabs = (seed: number, n: number, at: (r: () => number) => [number, number, number] | null, cols: string[], len: [number, number], wid: number, ang: number, jit = 0.5, op: [number, number] = [0.55, 0.95]): React.ReactNode[] => {
  const r = rng(seed);
  const out: React.ReactNode[] = [];
  for (let i = 0; i < n; i++) {
    const p = at(r);
    if (!p) continue;
    const l = lerp(len[0], len[1], r()), a = ang + (r() - 0.5) * jit * 2;
    const ci = Math.max(0, Math.min(cols.length - 1, Math.floor((p[2] + (r() - 0.5) * 0.35) * cols.length)));
    out.push(<path key={i} d={leaf([p[0], p[1]], [p[0] + Math.cos(a) * l, p[1] + Math.sin(a) * l], l * wid, (r() - 0.5) * l * 0.3)} fill={cols[ci]} opacity={lerp(op[0], op[1], r())} />);
  }
  return out;
};

/** masa de follaje: sombra con degradé y muchas hojas pintadas, más claras hacia la luz (arriba-izquierda) */
export const Foliage: React.FC<{ id: string; cx: number; cy: number; rx: number; ry: number; seed: number; cols: string[]; droop?: number; n?: number; leafLen?: number }> = ({ id, cx, cy, rx, ry, seed, cols, droop = 0, n = 150, leafLen }) => {
  const r = rng(seed);
  const pts: Pt[] = [];
  const m = 14;
  for (let i = 0; i < m; i++) { const a = (i / m) * Math.PI * 2, j = 0.75 + r() * 0.4; pts.push([cx + Math.cos(a) * rx * j, cy + Math.sin(a) * ry * j * (Math.sin(a) > 0 ? 1 + droop * 0.5 : 1)]); }
  const L = leafLen ?? Math.min(rx, ry) * 0.3;
  const at = (q: () => number): [number, number, number] => {
    const a = q() * Math.PI * 2, d = Math.sqrt(q());
    const x = cx + Math.cos(a) * rx * d, y = cy + Math.sin(a) * ry * d * (Math.sin(a) > 0 ? 1 + droop * 0.4 : 1);
    const light = 0.5 - ((x - cx) / rx) * 0.3 - ((y - cy) / ry) * 0.42;
    return [x, y, light];
  };
  return (
    <g>
      <defs><RG id={id} stops={[[0, cols[Math.min(2, cols.length - 1)]], [0.55, cols[1]], [1, cols[0]]]} cx={0.32} cy={0.25} r={0.8} /></defs>
      <path d={smooth(pts, true, 1)} fill={`url(#${id})`} />
      {dabs(seed + 1, n, at, cols, [L * 0.6, L * 1.3], 0.2, Math.PI / 2 * (0.4 + droop * 0.6), 0.9 - droop * 0.45)}
      {dabs(seed + 2, Math.round(n * 0.35), (q) => { const p = at(q); return p[2] > 0.55 ? [p[0], p[1], 1] : null; }, [cols[cols.length - 1]], [L * 0.5, L], 0.18, Math.PI / 2 * (0.4 + droop * 0.6), 0.8, [0.7, 1])}
    </g>
  );
};

/** tronco curvo afinado con degradé a lo ancho y vetas */
export const Trunk: React.FC<{ id: string; pts: [number, number, number][]; cols: [string, string, string]; seed: number }> = ({ id, pts, cols, seed }) => {
  const L: Pt[] = [], R: Pt[] = [];
  pts.forEach((p, i) => {
    const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)];
    const l = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1, nx = -(b[1] - a[1]) / l, ny = (b[0] - a[0]) / l;
    L.push([p[0] + nx * p[2], p[1] + ny * p[2]]); R.unshift([p[0] - nx * p[2], p[1] - ny * p[2]]);
  });
  const r = rng(seed);
  return (
    <g>
      <defs><LG id={id} x1={0} y1={0} x2={1} y2={0} stops={[[0, cols[2]], [0.3, cols[1]], [1, cols[0]]]} /><clipPath id={`${id}c`}><path d={smooth([...L, ...R], true, 0.8)} /></clipPath></defs>
      <path d={smooth([...L, ...R], true, 0.8)} fill={`url(#${id})`} />
      <g clipPath={`url(#${id}c)`}>
        {pts.slice(0, -1).map((p, i) => Array.from({ length: 5 }, (_, k) => { const q = pts[i + 1], t = r(); const x = lerp(p[0], q[0], t) + (r() - 0.5) * p[2] * 1.6, y = lerp(p[1], q[1], t); return <path key={`${i}-${k}`} d={leaf([x, y], [x + (q[0] - p[0]) * 0.3, y + (q[1] - p[1]) * 0.3], 2 + r() * 3)} fill={r() < 0.5 ? cols[0] : cols[2]} opacity={0.5} />; }))}
      </g>
    </g>
  );
};

/** roca con planos de luz y sombra, vetas y musgo arriba */
export const RockMass: React.FC<{ id: string; pts: Pt[]; cols: [string, string, string]; seed: number; moss?: string[]; mossT?: number; k?: number }> = ({ id, pts, cols, seed, moss, mossT = 0.2, k = 0.45 }) => {
  const r = rng(seed);
  const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]);
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys), w = x1 - x0, h = y1 - y0;
  const d = smooth(pts, true, k);
  const facets: React.ReactNode[] = [];
  for (let i = 0; i < 26; i++) {
    const fx = x0 + r() * w, fy = y0 + r() * h, fw = w * (0.06 + r() * 0.14), fh = h * (0.08 + r() * 0.2);
    const lightSide = (fx - x0) / w < 0.5;
    facets.push(<path key={i} d={smooth([[fx, fy], [fx + fw, fy + fh * 0.2], [fx + fw * 0.8, fy + fh], [fx - fw * 0.2, fy + fh * 0.8]], true, 0.3)} fill={r() < (lightSide ? 0.65 : 0.25) ? cols[2] : cols[0]} opacity={0.3 + r() * 0.35} />);
  }
  for (let i = 0; i < 14; i++) { const fx = x0 + r() * w, fy = y0 + r() * h * 0.8; facets.push(<path key={`c${i}`} d={`M${fx} ${fy}l${(r() - 0.5) * 30} ${h * 0.08}l${(r() - 0.5) * 30} ${h * 0.07}`} stroke={cols[0]} strokeWidth={2 + r() * 3} fill="none" opacity={0.5} strokeLinecap="round" />); }
  return (
    <g>
      <defs><LG id={id} x1={0} y1={0} x2={1} y2={0.6} stops={[[0, cols[2]], [0.45, cols[1]], [1, cols[0]]]} /><clipPath id={`${id}c`}><path d={d} /></clipPath></defs>
      <path d={d} fill={`url(#${id})`} />
      <g clipPath={`url(#${id}c)`}>
        {facets}
        {moss && dabs(seed + 5, 420, (q) => { const x = x0 + q() * w, y = y0 + Math.pow(q(), 2.2) * h * (mossT + 0.25); return [x, y, 0.75 - ((x - x0) / w) * 0.5 - ((y - y0) / (h * mossT + 1)) * 0.25]; }, moss, [14, 34], 0.3, Math.PI / 2, 0.5)}
        {moss && dabs(seed + 6, 60, (q) => { const x = x0 + q() * w, y = y0 + q() * h * mossT * 2.4; return [x, y, 0.4]; }, moss, [50, 130], 0.07, Math.PI / 2, 0.15, [0.5, 0.8])}
      </g>
    </g>
  );
};

/** helecho: frondas curvas con pinnas pintadas */
export const FernP: React.FC<{ x: number; y: number; s: number; seed: number; cols: string[]; n?: number }> = ({ x, y, s, seed, cols, n = 9 }) => {
  const r = rng(seed);
  const out: React.ReactNode[] = [];
  for (let i = 0; i < n; i++) {
    const a0 = -Math.PI * (0.1 + (0.8 * i) / (n - 1)) + (r() - 0.5) * 0.2, len = s * (0.7 + r() * 0.5);
    const side = Math.cos(a0) > 0 ? 1 : -1;
    const light = 0.75 - (i / n) * 0.5;
    const steps = 12;
    let px = x, py = y, a = a0;
    for (let k = 0; k < steps; k++) {
      const t = k / steps;
      a += side * 0.085 * (1 + t * 1.5);
      const nx = px + (Math.cos(a) * len) / steps, ny = py + (Math.sin(a) * len) / steps;
      const pl = len * 0.3 * Math.sin(Math.PI * Math.min(1, t * 1.1 + 0.12));
      const c = cols[Math.max(0, Math.min(cols.length - 1, Math.floor((light + (r() - 0.5) * 0.3) * cols.length)))];
      out.push(<path key={`${i}-${k}a`} d={leaf([nx, ny], [nx + Math.cos(a + 1.25) * pl, ny + Math.sin(a + 1.25) * pl], pl * 0.26)} fill={c} />);
      out.push(<path key={`${i}-${k}b`} d={leaf([nx, ny], [nx + Math.cos(a - 1.25) * pl, ny + Math.sin(a - 1.25) * pl], pl * 0.26)} fill={mix(c, cols[0], 0.35)} />);
      out.push(<path key={`${i}-${k}s`} d={`M${px.toFixed(1)} ${py.toFixed(1)}L${nx.toFixed(1)} ${ny.toFixed(1)}`} stroke={cols[0]} strokeWidth={Math.max(1, s * 0.012 * (1 - t))} />);
      px = nx; py = ny;
    }
  }
  return <g>{out}</g>;
};

/** hongo de sombrero azul-violeta con brillo */
export const Mushroom: React.FC<{ id: string; x: number; y: number; s: number; seed: number; cap?: [string, string, string]; glow?: boolean }> = ({ id, x, y, s, seed, cap = ['#1c1f8a', '#4a4fe0', '#9aa2ff'], glow = true }) => {
  const r = rng(seed);
  const lean = (r() - 0.5) * s * 0.3, h = s * (0.8 + r() * 0.5), w = s * (0.75 + r() * 0.35);
  const top: Pt = [x + lean, y - h];
  return (
    <g>
      <defs><RG id={id} stops={[[0, cap[2]], [0.45, cap[1]], [1, cap[0]]]} cx={0.35} cy={0.2} r={0.85} /><LG id={`${id}s`} x1={0} x2={1} y2={0} stops={[[0, '#e6dcff'], [0.5, '#a89ad8'], [1, '#4a3c88']]} /></defs>
      {glow && <ellipse cx={top[0]} cy={top[1]} rx={w * 1.2} ry={w * 0.8} fill={cap[2]} opacity={0.35} filter="url(#b20)" />}
      <path d={smooth([[x - s * 0.09, y], [x + lean * 0.5 - s * 0.07, y - h * 0.5], [top[0] - s * 0.06, top[1]], [top[0] + s * 0.06, top[1]], [x + lean * 0.5 + s * 0.08, y - h * 0.5], [x + s * 0.11, y]], true, 0.8)} fill={`url(#${id}s)`} />
      <ellipse cx={top[0]} cy={top[1] + w * 0.07} rx={w * 0.92} ry={w * 0.14} fill="#151040" />
      <path d={`M${top[0] - w} ${top[1] + w * 0.08}Q${top[0] - w * 0.9} ${top[1] - w * 0.62} ${top[0]} ${top[1] - w * 0.66}Q${top[0] + w * 0.9} ${top[1] - w * 0.62} ${top[0] + w} ${top[1] + w * 0.08}Q${top[0]} ${top[1] + w * 0.24} ${top[0] - w} ${top[1] + w * 0.08}Z`} fill={`url(#${id})`} />
      {Array.from({ length: 9 }, (_, i) => { const a = r() * Math.PI, d2 = r() * 0.8; return <ellipse key={i} cx={top[0] - Math.cos(a) * w * d2} cy={top[1] - Math.sin(a) * w * 0.5 * d2 - w * 0.05} rx={w * (0.04 + r() * 0.06)} ry={w * (0.025 + r() * 0.03)} fill="#d8dcff" opacity={0.75} />; })}
      <path d={`M${top[0] - w * 0.7} ${top[1] - w * 0.3}Q${top[0] - w * 0.4} ${top[1] - w * 0.58} ${top[0] - w * 0.05} ${top[1] - w * 0.6}`} stroke="#ffffff" strokeWidth={w * 0.05} fill="none" opacity={0.55} strokeLinecap="round" />
    </g>
  );
};

/** roseta de hojas en punta (violeta o turquesa) */
export const Spiky: React.FC<{ id: string; x: number; y: number; s: number; seed: number; cols: [string, string, string] }> = ({ id, x, y, s, seed, cols }) => {
  const r = rng(seed);
  const n = 11;
  const fr = Array.from({ length: n }, (_, i) => ({ a: -Math.PI * (0.08 + (0.84 * i) / (n - 1)) + (r() - 0.5) * 0.14, l: s * (0.6 + r() * 0.5), i })).sort((p, q) => Math.abs(Math.cos(q.a)) - Math.abs(Math.cos(p.a)));
  return (
    <g>
      <defs><LG id={id} x1={0} y1={1} x2={0.3} y2={0} stops={[[0, cols[0]], [0.6, cols[1]], [1, cols[2]]]} /></defs>
      {fr.map((f, k) => { const e: Pt = [x + Math.cos(f.a) * f.l, y + Math.sin(f.a) * f.l + f.l * 0.3 * Math.abs(Math.cos(f.a))]; const bend = -(Math.cos(f.a) > 0 ? 1 : -1) * f.l * 0.22 * Math.abs(Math.cos(f.a)); return <g key={k}><path d={leaf([x, y], e, f.l * 0.1, bend)} fill={`url(#${id})`} /><path d={leaf([x, y], e, f.l * 0.025, bend * 1.25)} fill={cols[2]} opacity={0.7} /></g>; })}
    </g>
  );
};

/** cola de caballo: tallo segmentado con verticilos */
export const HorsetailP: React.FC<{ x: number; y: number; h: number; seed: number; cols: [string, string, string] }> = ({ x, y, h, seed, cols }) => {
  const r = rng(seed);
  const lean = (r() - 0.5) * h * 0.15, segs = Math.max(5, Math.round(h / 34));
  const out: React.ReactNode[] = [];
  for (let i = 0; i < segs; i++) {
    const t = i / segs, px = x + lean * t * t, py = y - h * t, w = Math.max(2, h * 0.016 * (1 - t * 0.7));
    out.push(<rect key={`s${i}`} x={px - w} y={py - h / segs - 1} width={w * 2} height={h / segs + 1} fill={i % 2 ? cols[1] : cols[0]} />);
    out.push(<rect key={`h${i}`} x={px - w} y={py - h / segs - 1} width={w * 0.7} height={h / segs + 1} fill={cols[2]} opacity={0.7} />);
    if (i > 0) for (let k = 0; k < 8; k++) { const a = -Math.PI * (0.05 + (0.9 * k) / 7), l = h * 0.13 * (1 - t * 0.5); out.push(<path key={`l${i}-${k}`} d={leaf([px, py], [px + Math.cos(a) * l, py + Math.sin(a) * l * 0.6 - l * 0.15], l * 0.05, l * 0.1 * (k < 4 ? 1 : -1))} fill={k % 2 ? cols[1] : cols[2]} />); }
  }
  return <g>{out}</g>;
};
