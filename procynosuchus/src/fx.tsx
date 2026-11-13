import React, { useId } from 'react';
import { H, INK, W, capsule, leaf, rng } from './lib';

export const Cam: React.FC<{ zoom?: number; cx?: number; cy?: number; rot?: number; shake?: number; f?: number; children: React.ReactNode }> = ({ zoom = 1, cx = W / 2, cy = H / 2, rot = 0, shake = 0, f = 0, children }) => {
  const r = rng(f * 7 + 3);
  const sx = (r() - 0.5) * shake, sy = (r() - 0.5) * shake;
  return <g transform={`translate(${(W / 2 + sx).toFixed(1)} ${(H / 2 + sy).toFixed(1)}) rotate(${rot.toFixed(2)}) scale(${zoom.toFixed(4)}) translate(${(-cx).toFixed(1)} ${(-cy).toFixed(1)})`}>{children}</g>;
};

export const Flash: React.FC<{ a: number; col?: string }> = ({ a, col = '#fff' }) => (a > 0.01 ? <rect width={W} height={H} fill={col} opacity={a} /> : null);

export const Vignette: React.FC<{ a?: number }> = ({ a = 0.45 }) => {
  const id = useId().replace(/:/g, '');
  return (
    <>
      <defs><radialGradient id={id} cx="50%" cy="50%" r="72%"><stop offset="0.55" stopColor="#000" stopOpacity={0} /><stop offset="1" stopColor="#05030a" stopOpacity={a} /></radialGradient></defs>
      <rect width={W} height={H} fill={`url(#${id})`} />
    </>
  );
};

/** horizontal speed streaks */
export const Speed: React.FC<{ f: number; a?: number; n?: number; col?: string }> = ({ f, a = 0.5, n = 26, col = '#fff' }) => {
  const r = rng(99);
  return (
    <g opacity={a}>
      {Array.from({ length: n }, (_, i) => {
        const y = r() * H, w = 200 + r() * 700, sp = 60 + r() * 90, x0 = r() * (W + 900);
        const x = W + 450 - ((x0 + f * sp) % (W + 900));
        return <rect key={i} x={x} y={y} width={w} height={2 + r() * 5} rx={3} fill={col} />;
      })}
    </g>
  );
};

/** radial burst for "boom" moments */
export const Burst: React.FC<{ x: number; y: number; t: number; col?: string; n?: number }> = ({ x, y, t, col = '#fff', n = 28 }) => {
  if (t <= 0 || t >= 1) return null;
  const r = rng(5);
  return (
    <g opacity={1 - t}>
      {Array.from({ length: n }, (_, i) => {
        const a = (i / n) * Math.PI * 2 + r() * 0.2, r0 = 80 + t * 500 + r() * 80, r1 = r0 + 160 + r() * 380;
        return <path key={i} d={leaf([x + Math.cos(a) * r0, y + Math.sin(a) * r0], [x + Math.cos(a) * r1, y + Math.sin(a) * r1], 9 + r() * 12)} fill={col} />;
      })}
      <circle cx={x} cy={y} r={60 + t * 620} fill="none" stroke={col} strokeWidth={22 * (1 - t)} />
    </g>
  );
};

const wrap = (text: string, max = 62): string[] => {
  const words = text.split(' ');
  const lines: string[] = [];
  let cur = '';
  for (const w of words) {
    if ((cur + ' ' + w).trim().length > max) { lines.push(cur.trim()); cur = w; } else cur += ' ' + w;
  }
  if (cur.trim()) lines.push(cur.trim());
  return lines;
};

/** small temporary guide subtitle (will be removed once the voice exists) */
export const Sub: React.FC<{ text: string }> = ({ text }) => {
  if (!text) return null;
  const lines = wrap(text);
  const lh = 38, w = Math.max(...lines.map((l) => l.length)) * 15.2 + 44, h = lines.length * lh + 18;
  const y0 = H - 56 - h;
  return (
    <g>
      <rect x={W / 2 - w / 2} y={y0} width={w} height={h} rx={10} fill="#07050c" opacity={0.6} />
      {lines.map((l, i) => <text key={i} x={W / 2} y={y0 + 37 + i * lh} textAnchor="middle" fontFamily="Inter, 'Liberation Sans', sans-serif" fontWeight={500} fontSize={28} fill="#fff">{l}</text>)}
    </g>
  );
};

export const Label: React.FC<{ x: number; y: number; text: string; size?: number; col?: string; anchor?: 'start' | 'middle' | 'end'; a?: number; bg?: boolean; weight?: number; ls?: number }> = ({ x, y, text, size = 30, col = '#fff', anchor = 'start', a = 1, bg, weight = 700, ls = 1 }) => {
  const w = text.length * size * 0.6 + 28;
  const bx = anchor === 'middle' ? x - w / 2 : anchor === 'end' ? x - w + 14 : x - 14;
  return (
    <g opacity={a}>
      {bg && <rect x={bx} y={y - size * 1.05} width={w} height={size * 1.5} rx={8} fill="#07050c" opacity={0.7} />}
      <text x={x} y={y} textAnchor={anchor} fontFamily="Inter, 'Liberation Sans', sans-serif" fontWeight={weight} fontSize={size} fill={col} letterSpacing={ls}>{text}</text>
    </g>
  );
};

export type SilKind = 'dog' | 'whale' | 'bat' | 'horse' | 'human' | 'bird' | 'dino' | 'croc' | 'lizard';
/** simple silhouettes built from capsules */
export const Sil: React.FC<{ kind: SilKind; x: number; y: number; s?: number; col?: string; flip?: boolean; f?: number }> = ({ kind, x, y, s = 1, col = INK, flip, f = 0 }) => {
  const c = (a: [number, number], b: [number, number], ra: number, rb: number, k: number) => <path key={k} d={capsule(a, b, ra, rb)} />;
  let el: React.ReactNode[] = [];
  const w = Math.sin(f / 4) * 8;
  if (kind === 'dog') el = [c([-90, -110], [70, -115], 38, 34, 0), c([70, -125], [120, -175], 26, 24, 1), c([120, -180], [185, -168], 26, 13, 2), <path key={3} d="M108 -200L118 -250L140 -205Z" />, c([-80, -90], [-92, -6], 16, 10, 4), c([-50, -90], [-40, -6], 16, 10, 5), c([55, -95], [50, -6], 15, 10, 6), c([85, -95], [96, -6], 15, 10, 7), c([-120, -125], [-175, -185 + w], 12, 5, 8)];
  else if (kind === 'horse') el = [c([-110, -230], [80, -235], 52, 50, 0), c([80, -250], [150, -350], 34, 26, 1), c([150, -360], [225, -320], 28, 16, 2), <path key={3} d="M140 -385L150 -430L166 -384Z" />, <path key={9} d={leaf([70, -270], [150, -380], 26, -30)} />, c([-120, -200], [-130, -100], 20, 11, 4), c([-130, -100], [-120, -6], 11, 9, 14), c([-80, -200], [-70, -6], 19, 9, 5), c([60, -200], [55, -100], 18, 10, 6), c([55, -100], [62, -6], 10, 9, 16), c([95, -200], [108, -6], 18, 9, 7), <path key={8} d={leaf([-150, -250], [-200 + w, -90], 26, 20)} />];
  else if (kind === 'whale') el = [<path key={0} d={leaf([-330, -20], [300, 0], 150, -40, 0.62)} />, <path key={1} d={`M-300 -22L-400 ${-110 + w}L-350 -22L-405 ${50 + w}Z`} />, <path key={2} d={leaf([90, 60], [20, 170], 34, 10)} />, <path key={3} d="M-60 -98L-100 -150L-10 -100Z" />];
  else if (kind === 'bat') el = [c([0, -30], [0, 40], 22, 14, 0), <circle key={1} cx={0} cy={-52} r={22} />, <path key={2} d="M-18 -66L-22 -100L-4 -72ZM18 -66L22 -100L4 -72Z" />, <path key={3} d={`M0 -20L-120 ${-110 + w * 3}L-300 ${-60 + w * 4}L-240 ${10 + w * 3}Q-200 -20 -170 30Q-130 -10 -90 40Q-50 0 0 30Z`} />, <path key={4} d={`M0 -20L120 ${-110 + w * 3}L300 ${-60 + w * 4}L240 ${10 + w * 3}Q200 -20 170 30Q130 -10 90 40Q50 0 0 30Z`} />];
  else if (kind === 'human') el = [<circle key={0} cx={0} cy={-480} r={42} />, c([0, -420], [0, -250], 50, 40, 1), c([-48, -410], [-66, -230], 17, 13, 2), c([48, -410], [66, -230], 17, 13, 3), c([-22, -250], [-28, -8], 26, 15, 4), c([22, -250], [28, -8], 26, 15, 5)];
  else if (kind === 'bird') el = [<path key={0} d={leaf([-70, 0], [80, -10], 34)} />, <path key={1} d={`M-10 -5L-60 ${-150 + w * 5}L50 ${-90 + w * 4}L60 -8Z`} />, <path key={2} d="M70 -14L118 -8L74 6Z" />, <path key={3} d="M-66 0L-130 -24L-124 20Z" />];
  else if (kind === 'dino') el = [<path key={0} d={leaf([-170, -200], [150, -210], 110, -10)} />, c([120, -230], [250, -430], 40, 22, 1), c([250, -436], [310, -430], 24, 15, 2), <path key={3} d={leaf([-140, -210], [-430, -90 + w], 44, -40, 0.3)} />, c([-90, -160], [-96, -8], 34, 26, 4), c([-40, -160], [-30, -8], 34, 26, 5), c([70, -170], [66, -8], 32, 25, 6), c([110, -170], [124, -8], 32, 25, 7)];
  else if (kind === 'croc') el = [<path key={0} d={leaf([-200, -40], [170, -44], 52, -6)} />, <path key={1} d={leaf([-170, -44], [-470, -20 + w], 30, -14, 0.3)} />, <path key={2} d={leaf([120, -52], [380, -40], 26, -2, 0.3)} />, c([-110, -30], [-140, -4], 14, 10, 3), c([90, -30], [120, -4], 14, 10, 4), <path key={5} d="M-150 -76l14 -18l14 18l14 -18l14 18l14 -18l14 18l14 -18l14 18Z" />];
  else if (kind === 'lizard') el = [<path key={0} d={leaf([-120, -30], [110, -34], 34, -4)} />, <path key={1} d={leaf([-100, -32], [-330, -10 + w], 18, -14, 0.3)} />, <path key={2} d={leaf([80, -40], [190, -36], 22, -2, 0.4)} />, c([-70, -24], [-100, -2], 9, 6, 3), c([60, -24], [90, -2], 9, 6, 4)];
  return <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s})`} fill={col}>{el}</g>;
};
