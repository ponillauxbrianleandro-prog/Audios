export const FPS = 30;
export const W = 1920;
export const H = 1080;
export const INK = '#17121c';

export type Pt = [number, number];

export const rng = (seed: number) => {
  let a = (Math.imul(seed + 1, 2654435761) >>> 0) || 1;
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
};

export const clamp = (v: number, a = 0, b = 1) => Math.max(a, Math.min(b, v));
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
/** t remapped from [a,b] to [0,1], clamped */
export const seg = (t: number, a: number, b: number) => clamp((t - a) / (b - a));
export const eio = (t: number) => t * t * (3 - 2 * t);
export const eout = (t: number) => 1 - Math.pow(1 - t, 3);
export const ein = (t: number) => t * t * t;
export const eback = (t: number) => {
  const c = 1.9;
  return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2);
};
const r1 = (n: number) => Math.round(n * 10) / 10;

/** smooth Catmull-Rom path through points */
export const smooth = (pts: Pt[], closed = true, k = 1): string => {
  const n = pts.length;
  if (n < 2) return '';
  const g = (i: number) => (closed ? pts[(i + n) % n] : pts[clamp(i, 0, n - 1)]);
  let d = `M${r1(pts[0][0])} ${r1(pts[0][1])}`;
  const last = closed ? n : n - 1;
  for (let i = 0; i < last; i++) {
    const p0 = g(i - 1), p1 = g(i), p2 = g(i + 1), p3 = g(i + 2);
    const c1: Pt = [p1[0] + ((p2[0] - p0[0]) / 6) * k, p1[1] + ((p2[1] - p0[1]) / 6) * k];
    const c2: Pt = [p2[0] - ((p3[0] - p1[0]) / 6) * k, p2[1] - ((p3[1] - p1[1]) / 6) * k];
    d += `C${r1(c1[0])} ${r1(c1[1])} ${r1(c2[0])} ${r1(c2[1])} ${r1(p2[0])} ${r1(p2[1])}`;
  }
  return d + (closed ? 'Z' : '');
};

export const poly = (pts: Pt[], closed = true) =>
  pts.map((p, i) => `${i ? 'L' : 'M'}${r1(p[0])} ${r1(p[1])}`).join('') + (closed ? 'Z' : '');

/** cloud-like scalloped blob: bumps bulge outwards */
export const scallop = (cx: number, cy: number, rx: number, ry: number, lobes: number, seed: number, bulge = 1.28, a0 = 0, a1 = Math.PI * 2): string => {
  const r = rng(seed);
  const pts: Pt[] = [];
  const full = Math.abs(a1 - a0 - Math.PI * 2) < 0.01;
  const cnt = full ? lobes : lobes + 1;
  for (let i = 0; i < cnt; i++) {
    const a = a0 + ((a1 - a0) * i) / lobes + (r() - 0.5) * 0.25 * ((a1 - a0) / lobes);
    const j = 0.88 + r() * 0.2;
    pts.push([cx + Math.cos(a) * rx * j, cy + Math.sin(a) * ry * j]);
  }
  let d = `M${r1(pts[0][0])} ${r1(pts[0][1])}`;
  const m = full ? cnt : cnt - 1;
  for (let i = 0; i < m; i++) {
    const p = pts[i], q = pts[(i + 1) % cnt];
    const mx = (p[0] + q[0]) / 2, my = (p[1] + q[1]) / 2;
    const cxx = cx + (mx - cx) * bulge * 1.15, cyy = cy + (my - cy) * bulge * 1.15;
    d += `Q${r1(cxx)} ${r1(cyy)} ${r1(q[0])} ${r1(q[1])}`;
  }
  return d + 'Z';
};

/** tapered capsule between two points */
export const capsule = (a: Pt, b: Pt, ra: number, rb: number): string => {
  const dx = b[0] - a[0], dy = b[1] - a[1];
  const l = Math.hypot(dx, dy) || 1;
  const nx = -dy / l, ny = dx / l;
  return `M${r1(a[0] + nx * ra)} ${r1(a[1] + ny * ra)}L${r1(b[0] + nx * rb)} ${r1(b[1] + ny * rb)}A${r1(rb)} ${r1(rb)} 0 0 1 ${r1(b[0] - nx * rb)} ${r1(b[1] - ny * rb)}L${r1(a[0] - nx * ra)} ${r1(a[1] - ny * ra)}A${r1(ra)} ${r1(ra)} 0 0 1 ${r1(a[0] + nx * ra)} ${r1(a[1] + ny * ra)}Z`;
};

/** leaf / lens shape from a to b with width w, bent by `bend` */
export const leaf = (a: Pt, b: Pt, w: number, bend = 0, tipBias = 0.5): string => {
  const dx = b[0] - a[0], dy = b[1] - a[1];
  const l = Math.hypot(dx, dy) || 1;
  const nx = -dy / l, ny = dx / l;
  const mx = a[0] + dx * tipBias + nx * bend, my = a[1] + dy * tipBias + ny * bend;
  return `M${r1(a[0])} ${r1(a[1])}Q${r1(mx + nx * w)} ${r1(my + ny * w)} ${r1(b[0])} ${r1(b[1])}Q${r1(mx - nx * w)} ${r1(my - ny * w)} ${r1(a[0])} ${r1(a[1])}Z`;
};

export const mix = (c1: string, c2: string, t: number) => {
  const p = (c: string) => [1, 3, 5].map((i) => parseInt(c.slice(i, i + 2), 16));
  const a = p(c1), b = p(c2);
  return '#' + a.map((v, i) => Math.round(lerp(v, b[i], t)).toString(16).padStart(2, '0')).join('');
};
