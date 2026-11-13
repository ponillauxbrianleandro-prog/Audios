import React, { useId, useMemo } from 'react';
import { H, W, lerp, leaf, rng, scallop, smooth, Pt } from './lib';
import { Calamite, Cloud, Clump, DAY, DRY, Fern, Glosso, Mesa, Pal, Reeds, Rock, Spires } from './art';

type EnvProps = { f: number; px?: number; pal?: Pal; seed?: number; children?: React.ReactNode; fg?: boolean; moon?: boolean; wet?: boolean };

const X0 = -700, X1 = 3900;

const Sky: React.FC<{ pal: Pal; id: string; h?: number }> = ({ pal, id, h = 640 }) => (
  <>
    <defs>
      <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stopColor={pal.sky[0]} /><stop offset="0.6" stopColor={pal.sky[1]} /><stop offset="1" stopColor={pal.sky[2]} />
      </linearGradient>
    </defs>
    <rect x={0} y={0} width={W} height={h} fill={`url(#${id})`} />
  </>
);

const Hills: React.FC<{ pal: Pal; seed: number; y: number; amp: number; col: string; lite?: string }> = React.memo(({ pal, seed, y, amp, col, lite }) => {
  const r = rng(seed);
  const pts: Pt[] = [[X0, y + 80]];
  for (let x = X0; x <= X1; x += 170) pts.push([x, y - amp * (0.15 + r() * r() * 1.1)]);
  pts.push([X1, y + 80]);
  const d = smooth(pts, true, 0.7);
  return (
    <g>
      <path d={d} fill={col} />
      {lite && <path d={d} fill={lite} transform={`translate(-14 ${amp * 0.16})`} opacity={0.45} />}
      <rect x={X0} y={y + 4} width={X1 - X0} height={90} fill={col} />
    </g>
  );
});

const TreeLine: React.FC<{ pal: Pal; seed: number; y: number; s: number; col: string; col2: string }> = React.memo(({ pal, seed, y, s, col, col2 }) => {
  const r = rng(seed);
  const out: React.ReactNode[] = [];
  let i = 0;
  for (let x = X0; x < X1; x += s * (0.5 + r() * 0.7)) {
    const hh = s * (0.7 + r() * 1.1);
    const k = r();
    if (k < 0.3) {
      out.push(<rect key={`t${i}`} x={x - 3} y={y - hh * 1.5} width={6} height={hh * 1.5} fill={col} />);
      for (let j = 1; j < 5; j++) out.push(<path key={`w${i}-${j}`} d={`M${x - s * 0.3 * (1 - j / 6)} ${y - hh * 1.5 * (j / 5) - 10}L${x} ${y - hh * 1.5 * (j / 5)}L${x + s * 0.3 * (1 - j / 6)} ${y - hh * 1.5 * (j / 5) - 10}`} stroke={col} strokeWidth={4} fill="none" />);
    } else {
      out.push(<rect key={`t${i}`} x={x - 4} y={y - hh} width={8} height={hh} fill={col} />);
      out.push(<path key={`c${i}`} d={scallop(x, y - hh, s * (0.4 + r() * 0.3), s * 0.36, 7, seed + i)} fill={col} />);
      out.push(<path key={`d${i}`} d={scallop(x - s * 0.08, y - hh - s * 0.1, s * 0.26, s * 0.2, 6, seed + i + 7)} fill={col2} opacity={0.8} />);
    }
    i++;
  }
  return <g>{out}<rect x={X0} y={y - 2} width={X1 - X0} height={40} fill={col} /></g>;
});

const River: React.FC<{ pal: Pal; y: number; h: number; f: number }> = ({ pal, y, h, f }) => {
  const dashes = useMemo(() => {
    const r = rng(77);
    return Array.from({ length: 70 }, () => ({ x: X0 + r() * (X1 - X0), y: r(), w: 40 + r() * 140, p: r() * 6 }));
  }, []);
  return (
    <g>
      <rect x={X0} y={y} width={X1 - X0} height={h} fill={pal.water} />
      <rect x={X0} y={y} width={X1 - X0} height={h * 0.25} fill={pal.ink} opacity={0.18} />
      {dashes.map((d, i) => {
        const xx = X0 + ((d.x - X0 + f * (0.5 + d.y)) % (X1 - X0));
        const op = 0.35 + 0.45 * Math.sin(f / 9 + d.p);
        return <rect key={i} x={xx} y={y + 6 + d.y * (h - 12)} width={d.w * (0.5 + d.y)} height={2.5 + d.y * 3} rx={2} fill={pal.waterL} opacity={Math.max(0.05, op)} />;
      })}
    </g>
  );
};

const GroundBand: React.FC<{ pal: Pal; seed: number; y: number; dry?: boolean }> = React.memo(({ pal, seed, y, dry }) => {
  const r = rng(seed);
  const pts: Pt[] = [[X0, H + 200]];
  for (let x = X0; x <= X1; x += 230) pts.push([x, y + (r() - 0.5) * 26]);
  pts.push([X1, H + 200]);
  const d = smooth(pts, true, 0.6);
  const bits: React.ReactNode[] = [];
  for (let i = 0; i < 90; i++) {
    const bx = X0 + r() * (X1 - X0), by = y + 30 + Math.pow(r(), 1.3) * (H - y - 10);
    const sc = 0.5 + ((by - y) / (H - y)) * 1.3;
    const k = r();
    if (k < 0.45) bits.push(<ellipse key={i} cx={bx} cy={by} rx={(60 + r() * 150) * sc} ry={(7 + r() * 9) * sc} fill={r() < 0.5 ? pal.groundD : pal.groundL} opacity={0.5} />);
    else if (k < 0.75) bits.push(<path key={i} d={`M${bx} ${by}q${6 * sc} ${-16 * sc} ${2 * sc} ${-26 * sc}M${bx + 8 * sc} ${by}q${10 * sc} ${-10 * sc} ${14 * sc} ${-20 * sc}M${bx - 7 * sc} ${by}q${-8 * sc} ${-9 * sc} ${-10 * sc} ${-18 * sc}`} stroke={dry ? pal.groundD : pal.leafD} strokeWidth={2.6 * sc} fill="none" strokeLinecap="round" />);
    else bits.push(<g key={i}><ellipse cx={bx} cy={by} rx={11 * sc} ry={6 * sc} fill={pal.rock} stroke={pal.ink} strokeWidth={2.2} /><ellipse cx={bx - 3 * sc} cy={by - 2 * sc} rx={5 * sc} ry={2 * sc} fill={pal.rockL} /></g>);
  }
  return (
    <g>
      <path d={d} fill={pal.ground} stroke={pal.ink} strokeWidth={dry ? 0 : 4} />
      {bits}
    </g>
  );
});

type Item = { k: string; x: number; y: number; s: number; seed: number; alt: boolean };
const scatter = (seed: number, n: number, kinds: string[], y0: number, y1: number, s0: number, s1: number): Item[] => {
  const r = rng(seed);
  const out: Item[] = [];
  for (let i = 0; i < n; i++) {
    const t = r();
    out.push({ k: kinds[Math.floor(r() * kinds.length)], x: X0 + ((i + r() * 0.9) / n) * (X1 - X0), y: lerp(y0, y1, t), s: lerp(s0, s1, t) * (0.8 + r() * 0.4), seed: seed * 100 + i, alt: r() < 0.3 });
  }
  return out.sort((a, b) => a.y - b.y);
};

const Plant: React.FC<{ it: Item; pal: Pal; f: number; sway?: number }> = ({ it, pal, f, sway = 0.7 }) => {
  const a = Math.sin(f / 38 + it.seed) * sway + Math.sin(f / 13 + it.seed * 2) * sway * 0.3;
  let el: React.ReactNode = null;
  if (it.k === 'g') el = <Glosso x={it.x} y={it.y} h={it.s} seed={it.seed} pal={pal} alt={it.alt} />;
  else if (it.k === 'c') el = <Calamite x={it.x} y={it.y} h={it.s * 0.9} seed={it.seed} pal={pal} />;
  else if (it.k === 'f') el = <Fern x={it.x} y={it.y} s={it.s * 0.3} seed={it.seed} pal={pal} alt={it.alt} />;
  else if (it.k === 'r') el = <Reeds x={it.x} y={it.y} s={it.s * 0.22} seed={it.seed} pal={pal} />;
  else if (it.k === 'k') el = <Rock x={it.x} y={it.y} w={it.s * 0.3} h={it.s * 0.13} seed={it.seed} pal={pal} moss />;
  else if (it.k === 'b') el = <Clump x={it.x} y={it.y - it.s * 0.07} r={it.s * 0.12} seed={it.seed} pal={pal} alt={it.alt} />;
  return <g transform={`rotate(${a.toFixed(2)} ${it.x} ${it.y})`}>{el}</g>;
};

const Layer: React.FC<{ px: number; k: number; children: React.ReactNode }> = ({ px, k, children }) => <g transform={`translate(${(-px * k).toFixed(1)} 0)`}>{children}</g>;

/** lush river bank: dense Glossopteris forest, river, mossy ground */
export const Riverbank: React.FC<EnvProps> = ({ f, px = 0, pal = DAY, seed = 1, children, fg = true, moon }) => {
  const id = useId().replace(/:/g, '');
  const mid = useMemo(() => scatter(seed * 7 + 1, 26, ['g', 'g', 'c', 'g', 'c'], 650, 700, 430, 620), [seed]);
  const under = useMemo(() => scatter(seed * 7 + 2, 46, ['f', 'r', 'b', 'f', 'k', 'r'], 690, 770, 330, 520), [seed]);
  const front = useMemo(() => scatter(seed * 7 + 3, 12, ['f', 'r', 'f', 'k'], 990, 1060, 520, 760), [seed]);
  const fore = useMemo(() => scatter(seed * 7 + 4, 7, ['f', 'f', 'r'], 1150, 1200, 1000, 1300), [seed]);
  return (
    <g>
      <Sky pal={pal} id={`sky${id}`} />
      {moon && <g><circle cx={1380} cy={210} r={120} fill={pal.far2} opacity={0.55} /><circle cx={1340} cy={180} r={30} fill={pal.haze} opacity={0.25} /><circle cx={1420} cy={250} r={18} fill={pal.haze} opacity={0.2} /><circle cx={620} cy={300} r={34} fill="#f4eefc" opacity={0.9} /></g>}
      <Layer px={px} k={0.04}><Cloud x={500} y={200} s={70} seed={seed + 3} shade={pal.far2} /><Cloud x={1500} y={130} s={50} seed={seed + 4} shade={pal.far2} /><Cloud x={2300} y={240} s={80} seed={seed + 5} shade={pal.far2} /></Layer>
      <Layer px={px} k={0.08}><Hills pal={pal} seed={seed + 10} y={520} amp={230} col={pal.far2} /></Layer>
      <Layer px={px} k={0.14}><Hills pal={pal} seed={seed + 11} y={545} amp={150} col={pal.far} lite={pal.far2} /></Layer>
      <rect x={0} y={420} width={W} height={160} fill={pal.haze} opacity={0.28} />
      <Layer px={px} k={0.24}><TreeLine pal={pal} seed={seed + 12} y={568} s={90} col={pal.leafD} col2={pal.leafM} /></Layer>
      <Layer px={px} k={0.4}>
        <River pal={pal} y={575} h={95} f={f} />
      </Layer>
      <Layer px={px} k={0.62}>
        <GroundBand pal={pal} seed={seed + 20} y={660} />
        {mid.map((it, i) => <Plant key={i} it={it} pal={pal} f={f} sway={0.5} />)}
      </Layer>
      <Layer px={px} k={1}>
        <GroundBand pal={pal} seed={seed + 21} y={730} />
        {under.map((it, i) => <Plant key={i} it={it} pal={pal} f={f} sway={1} />)}
        {children}
        {front.map((it, i) => <Plant key={i} it={it} pal={pal} f={f} sway={1.2} />)}
      </Layer>
      {fg && <Layer px={px} k={1.7}><g opacity={1}>{fore.map((it, i) => <Plant key={i} it={{ ...it, x: it.x * 1.5 }} pal={{ ...pal, leafM: pal.leafD, leafL: pal.leafM, alt: pal.leafD, altL: pal.alt }} f={f} sway={1.6} />)}</g></Layer>}
    </g>
  );
};

/** dry plain with buttes: few plants, personality from the rocks and the sky */
export const DryPlain: React.FC<EnvProps> = ({ f, px = 0, pal = DRY, seed = 1, children, fg = true }) => {
  const id = useId().replace(/:/g, '');
  const r = rng(seed * 13);
  const mesas = useMemo(() => Array.from({ length: 9 }, (_, i) => ({ x: X0 + 250 + i * 520 + r() * 200, w: 220 + r() * 220, h: 260 + r() * 300, s: seed * 50 + i })), [seed]);
  const far = useMemo(() => Array.from({ length: 12 }, (_, i) => ({ x: X0 + i * 400 + r() * 200, w: 160 + r() * 200, h: 120 + r() * 200, s: seed * 60 + i })), [seed]);
  const under = useMemo(() => scatter(seed * 9 + 2, 22, ['k', 'r', 'k', 'f', 'b'], 720, 800, 300, 520), [seed]);
  const front = useMemo(() => scatter(seed * 9 + 3, 7, ['k', 'r', 'f'], 1000, 1060, 520, 700), [seed]);
  return (
    <g>
      <Sky pal={pal} id={`sky${id}`} h={720} />
      <Layer px={px - f * 0.25} k={0.05}><Cloud x={300} y={170} s={85} seed={seed + 1} /><Cloud x={1100} y={90} s={55} seed={seed + 2} /><Cloud x={1750} y={220} s={100} seed={seed + 3} /><Cloud x={2500} y={130} s={70} seed={seed + 4} /></Layer>
      <Layer px={px} k={0.1}>{far.map((m, i) => <Mesa key={i} x={m.x} y={690} w={m.w} h={m.h} seed={m.s} pal={{ ...pal, rock: i % 2 ? pal.far : pal.far2 }} flat />)}</Layer>
      <rect x={0} y={560} width={W} height={150} fill={pal.haze} opacity={0.3} />
      <Layer px={px} k={0.35}>{mesas.map((m, i) => <Mesa key={i} x={m.x} y={705} w={m.w} h={m.h} seed={m.s} pal={pal} />)}</Layer>
      <Layer px={px} k={1}>
        <GroundBand pal={pal} seed={seed + 21} y={700} dry />
        {under.map((it, i) => <Plant key={i} it={it} pal={pal} f={f} sway={0.8} />)}
        {children}
        {front.map((it, i) => <Plant key={i} it={it} pal={pal} f={f} sway={1} />)}
      </Layer>
      {fg && <Layer px={px} k={1.6}><Mesa x={-120} y={1150} w={620} h={980} seed={seed + 70} pal={pal} cap={false} /><Mesa x={3150} y={1150} w={560} h={900} seed={seed + 71} pal={pal} cap={false} /></Layer>}
    </g>
  );
};

/** violet spires over a sea of vegetation (wide establishing shot) */
export const SpireVista: React.FC<EnvProps> = ({ f, px = 0, pal = DAY, seed = 1, children }) => {
  const id = useId().replace(/:/g, '');
  const rows = useMemo(() => {
    const r = rng(seed * 5);
    return Array.from({ length: 6 }, (_, j) => Array.from({ length: 34 - j * 3 }, (_, i) => ({ x: X0 + i * (140 + j * 26) + r() * 80, y: 700 + j * 72 + r() * 24, r: 60 + j * 22 + r() * 30, s: seed * 99 + j * 40 + i, alt: r() < 0.25, hi: r() < 0.3 })));
  }, [seed]);
  return (
    <g>
      <Sky pal={{ ...pal, sky: [pal.sky[0], '#4fc0c8', '#e4f4d8'] as [string, string, string] }} id={`sky${id}`} h={760} />
      <Layer px={px - f * 0.3} k={0.05}><Cloud x={260} y={150} s={80} seed={seed + 1} /><Cloud x={1250} y={230} s={60} seed={seed + 2} /><Cloud x={1700} y={110} s={95} seed={seed + 3} /><Cloud x={2500} y={200} s={70} seed={seed + 4} /></Layer>
      <Layer px={px} k={0.1}><Hills pal={pal} seed={seed + 3} y={650} amp={90} col="#e8a8c8" /></Layer>
      <rect x={0} y={640} width={W} height={50} fill={pal.water} opacity={0.7} />
      <Layer px={px} k={0.3}><Spires x={1050} y={700} w={860} h={420} seed={seed + 9} pal={pal} /><Spires x={2600} y={700} w={500} h={240} seed={seed + 19} pal={pal} /></Layer>
      {rows.map((row, j) => (
        <Layer key={j} px={px} k={0.45 + j * 0.2}>
          <rect x={X0} y={720 + j * 72} width={X1 - X0} height={500} fill={pal.leafD} />
          {row.map((c, i) => <Clump key={i} x={c.x} y={c.y} r={c.r} seed={c.s} pal={c.hi ? { ...pal, leafM: pal.leafL, leafL: pal.leafH } : pal} alt={c.alt} />)}
          {j === 3 && children}
        </Layer>
      ))}
    </g>
  );
};

/** drifting dust, a few leaves, optional insects */
export const Air: React.FC<{ f: number; pal: Pal; dust?: number; leaves?: number; wind?: number; bugs?: number }> = ({ f, pal, dust = 40, leaves = 4, wind = 1, bugs = 0 }) => {
  const ps = useMemo(() => { const r = rng(4242); return Array.from({ length: 120 }, () => ({ x: r() * W, y: r() * H, s: r(), p: r() * 10 })); }, []);
  return (
    <g>
      {ps.slice(0, dust).map((p, i) => {
        const x = (p.x + f * (0.6 + p.s * 2.2) * wind) % (W + 40) - 20;
        const y = p.y + Math.sin(f / 30 + p.p) * 18;
        return <circle key={i} cx={x} cy={y} r={1.5 + p.s * 3.5} fill="#fffbe0" opacity={0.12 + 0.3 * p.s * (0.5 + 0.5 * Math.sin(f / 11 + p.p))} />;
      })}
      {ps.slice(60, 60 + leaves).map((p, i) => {
        const sp = (5 + p.s * 6) * wind;
        const x = (p.x + f * sp) % (W + 300) - 150;
        const y = 200 + p.y * 0.55 + Math.sin(f / 17 + p.p) * 70 + ((f * 0.8) % 300) * 0.3;
        const rot = f * (5 + p.s * 9) + p.p * 40;
        return <g key={i} transform={`translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${rot.toFixed(1)}) scale(1 ${Math.cos(f / 6 + p.p).toFixed(2)})`}><path d={leaf([-18, 0], [18, 0], 9)} fill={i % 2 ? pal.leafL : pal.leafH} stroke={pal.ink} strokeWidth={2.5} /><path d="M-18 0L18 0" stroke={pal.ink} strokeWidth={1.3} /></g>;
      })}
      {ps.slice(80, 80 + bugs).map((p, i) => {
        const x = p.x + Math.sin(f / 23 + p.p) * 260 + Math.sin(f / 5 + p.p) * 20;
        const y = 300 + p.y * 0.4 + Math.cos(f / 19 + p.p * 2) * 120 + Math.sin(f / 4 + p.p) * 10;
        const wv = Math.sin(f * 2.4 + i) * 9;
        return <g key={i} transform={`translate(${x.toFixed(1)} ${y.toFixed(1)})`}><path d={`M-12 0L12 0`} stroke={pal.ink} strokeWidth={4} strokeLinecap="round" /><path d={leaf([0, 0], [-4, -16 - wv], 5)} fill="#ffffff" opacity={0.8} /><path d={leaf([0, 0], [6, -16 + wv], 5)} fill="#ffffff" opacity={0.8} /></g>;
      })}
    </g>
  );
};
