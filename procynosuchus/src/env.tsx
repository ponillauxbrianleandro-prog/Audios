import React, { useId, useMemo } from 'react';
import { H, W, Pt, capsule, lerp, leaf, mix, rng, scallop, smooth } from './lib';
import { Calamite, Cloud, Clump, DAY, DRY, Fern, Glosso, Mesa, Pal, Reeds, Rock, Spires, Umbrella } from './art';

type EnvProps = { f: number; px?: number; pal?: Pal; seed?: number; children?: React.ReactNode; fg?: boolean; moon?: boolean; wet?: boolean };

const X0 = -700, X1 = 3900;
const HZ = 590; // horizonte
// profundidad z: 0 = horizonte, 1 = pegado a cámara
const zy = (z: number) => HZ + 14 + Math.pow(z, 1.45) * 560;
const zk = (z: number) => 0.24 + 1.2 * Math.pow(z, 1.25);
const zp = (z: number) => 0.3 + 1.3 * z;
export const CHILD_Z = 0.54; // profundidad a la que se dibujan los animales (paralaje 1)

const hazeCache = new Map<string, Pal>();
/** lo lejano se aclara y toma el color del aire */
const hazed = (pal: Pal, key: string, t: number): Pal => {
  const k = `${key}-${t.toFixed(2)}-${pal.leafM}${pal.rock}`;
  const got = hazeCache.get(k);
  if (got) return got;
  const m = (c: string) => mix(c, pal.haze, t);
  const out: Pal = { ...pal, leafD: m(pal.leafD), leafM: m(pal.leafM), leafL: m(pal.leafL), leafH: m(pal.leafH), alt: m(pal.alt), altL: m(pal.altL), trunk: m(pal.trunk), trunkL: m(pal.trunkL), rock: m(pal.rock), rockL: m(pal.rockL), rockD: m(pal.rockD), ink: mix(pal.ink, pal.haze, t * 0.8) };
  hazeCache.set(k, out);
  return out;
};

const Sky: React.FC<{ pal: Pal; id: string; h?: number; sun?: boolean }> = ({ pal, id, h = 640, sun = true }) => (
  <>
    <defs>
      <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stopColor={pal.sky[0]} /><stop offset="0.6" stopColor={pal.sky[1]} /><stop offset="1" stopColor={pal.sky[2]} />
      </linearGradient>
      <radialGradient id={`${id}s`} cx="0.5" cy="0.5" r="0.5"><stop offset="0" stopColor="#fffbe0" stopOpacity={0.95} /><stop offset="0.18" stopColor="#fff4c0" stopOpacity={0.55} /><stop offset="1" stopColor="#fff4c0" stopOpacity={0} /></radialGradient>
    </defs>
    <rect x={0} y={0} width={W} height={h} fill={`url(#${id})`} />
    {sun && <circle cx={330} cy={150} r={520} fill={`url(#${id}s)`} />}
  </>
);

const Hills: React.FC<{ pal: Pal; seed: number; y: number; amp: number; col: string; lite?: string }> = React.memo(({ seed, y, amp, col, lite }) => {
  const r = rng(seed);
  const pts: Pt[] = [[X0, y + 80]];
  for (let x = X0; x <= X1; x += 170) pts.push([x, y - amp * (0.15 + r() * r() * 1.1)]);
  pts.push([X1, y + 80]);
  const d = smooth(pts, true, 0.7);
  return (
    <g>
      <path d={d} fill={col} />
      {lite && <path d={d} fill={lite} transform={`translate(-26 ${amp * 0.1})`} opacity={0.5} />}
      <rect x={X0} y={y + 4} width={X1 - X0} height={90} fill={col} />
    </g>
  );
});

type Item = { k: string; x: number; z: number; s: number; seed: number; alt: boolean };
const scatterZ = (seed: number, n: number, kinds: string[], z0: number, z1: number, s: number): Item[] => {
  const r = rng(seed);
  const out: Item[] = [];
  for (let i = 0; i < n; i++) out.push({ k: kinds[Math.floor(r() * kinds.length)], x: X0 + ((i + r() * 0.9) / n) * (X1 - X0), z: lerp(z0, z1, r()), s: s * (0.8 + r() * 0.45), seed: seed * 100 + i, alt: r() < 0.3 });
  return out;
};

const Plant: React.FC<{ it: Item; pal: Pal; f: number; px: number; sway?: number; dark?: boolean }> = ({ it, pal, f, px, sway = 0.8 }) => {
  const y = zy(it.z), k = zk(it.z), x = it.x - px * zp(it.z);
  if (x < -700 * k - 300 || x > W + 700 * k + 300) return null;
  const tier = Math.round(Math.max(0, 0.5 - it.z) * 8) / 8;
  const p = tier > 0 ? hazed(pal, 'h', tier * 1.1) : pal;
  const a = (Math.sin(f / 38 + it.seed) * sway + Math.sin(f / 13 + it.seed * 2) * sway * 0.3) * (0.5 + it.z);
  const s = it.s * k;
  let el: React.ReactNode = null, shw = s * 0.2;
  if (it.k === 'g') { el = <Glosso x={0} y={0} h={s} seed={it.seed} pal={p} alt={it.alt} />; shw = s * 0.34; }
  else if (it.k === 'u') { el = <Umbrella x={0} y={0} h={s * 1.5} seed={it.seed} pal={p} />; shw = s * 0.3; }
  else if (it.k === 'c') { el = <Calamite x={0} y={0} h={s * 0.9} seed={it.seed} pal={p} />; shw = s * 0.12; }
  else if (it.k === 'f') { el = <Fern x={0} y={0} s={s * 0.3} seed={it.seed} pal={p} alt={it.alt} />; shw = s * 0.3; }
  else if (it.k === 'r') { el = <Reeds x={0} y={0} s={s * 0.22} seed={it.seed} pal={p} />; shw = s * 0.12; }
  else if (it.k === 'k') { el = <Rock x={0} y={0} w={s * 0.3} h={s * 0.13} seed={it.seed} pal={p} moss />; shw = s * 0.2; }
  else if (it.k === 'b') { el = <Clump x={0} y={-s * 0.07} r={s * 0.12} seed={it.seed} pal={p} alt={it.alt} />; shw = s * 0.16; }
  return (
    <g transform={`translate(${x.toFixed(1)} ${y.toFixed(1)})`}>
      <ellipse cx={shw * 0.75} cy={shw * 0.06} rx={shw * 1.25} ry={shw * 0.2 + 3} fill="#0a0620" opacity={0.26} />
      <g transform={`rotate(${a.toFixed(2)})`}>{el}</g>
    </g>
  );
};

const Layer: React.FC<{ px: number; k: number; children: React.ReactNode }> = ({ px, k, children }) => <g transform={`translate(${(-px * k).toFixed(1)} 0)`}>{children}</g>;

/** franja diagonal sobre el suelo (río, sendero): puntos [x, z, ancho] */
const Strip: React.FC<{ pts: [number, number, number][]; px: number; fill: string; edge?: string; inner?: string; f?: number; spark?: string }> = ({ pts, px, fill, edge, inner, f = 0, spark }) => {
  const L: Pt[] = [], R: Pt[] = [], C: Pt[] = [];
  pts.forEach(([x, z, w]) => { const sx = x - px * zp(z), y = zy(z), ww = (w * zk(z)) / 2; L.push([sx - ww, y]); R.unshift([sx + ww, y]); C.push([sx, y]); });
  const d = smooth([...L, ...R], true, 0.8);
  const r = rng(31);
  return (
    <g>
      <path d={d} fill={fill} stroke={edge} strokeWidth={edge ? 5 : 0} strokeLinejoin="round" />
      {inner && <path d={smooth(C, false, 0.8)} fill="none" stroke={inner} strokeWidth={26} strokeLinecap="round" opacity={0.45} />}
      {spark && C.slice(0, -1).map((c, i) => Array.from({ length: 5 }, (_, j) => {
        const t = (r() + f * 0.006 * (1 + i * 0.3)) % 1, n = C[i + 1];
        const w = Math.abs(R[R.length - 1 - i][0] - L[i][0]);
        const xx = lerp(c[0], n[0], t) + (r() - 0.5) * w * 0.7, yy = lerp(c[1], n[1], t);
        return <rect key={`${i}-${j}`} x={xx} y={yy} width={8 + w * 0.08} height={2 + i * 0.7} rx={2} fill={spark} opacity={0.25 + 0.5 * Math.abs(Math.sin(f / 9 + i * 3 + j))} />;
      }))}
    </g>
  );
};

const Ground: React.FC<{ pal: Pal; seed: number; id: string; dry?: boolean }> = React.memo(({ pal, seed, id, dry }) => {
  const r = rng(seed);
  const bits: React.ReactNode[] = [];
  for (let i = 0; i < 120; i++) {
    const z = Math.pow(r(), 0.8), y = zy(z) + 6, k = zk(z), bx = r() * (W + 400) - 200;
    const q = r();
    if (q < 0.5) bits.push(<ellipse key={i} cx={bx} cy={y} rx={(70 + r() * 200) * k} ry={(6 + r() * 9) * k} fill={r() < 0.5 ? pal.groundD : pal.groundL} opacity={0.42} transform={`skewX(-28)`} style={{ transformOrigin: `${bx}px ${y}px` }} />);
    else if (q < 0.82) bits.push(<path key={i} d={`M${bx} ${y}q${6 * k} ${-16 * k} ${2 * k} ${-28 * k}M${bx + 8 * k} ${y}q${10 * k} ${-10 * k} ${14 * k} ${-22 * k}M${bx - 7 * k} ${y}q${-8 * k} ${-9 * k} ${-10 * k} ${-18 * k}`} stroke={dry ? pal.groundD : pal.leafD} strokeWidth={Math.max(1.2, 2.8 * k)} fill="none" strokeLinecap="round" opacity={0.5 + z * 0.5} />);
    else bits.push(<g key={i}><ellipse cx={bx + 7 * k} cy={y + 3 * k} rx={14 * k} ry={4 * k} fill="#0a0620" opacity={0.25} /><ellipse cx={bx} cy={y} rx={11 * k} ry={6.5 * k} fill={pal.rock} stroke={pal.ink} strokeWidth={Math.max(1, 2.2 * k)} /><ellipse cx={bx - 3 * k} cy={y - 2 * k} rx={5 * k} ry={2 * k} fill={pal.rockL} /></g>);
  }
  return (
    <g>
      <defs><linearGradient id={id} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={mix(pal.groundL, pal.haze, 0.45)} /><stop offset="0.25" stopColor={pal.ground} /><stop offset="1" stopColor={mix(pal.ground, pal.groundD, 0.55)} /></linearGradient></defs>
      <rect x={-200} y={HZ} width={W + 400} height={H - HZ + 200} fill={`url(#${id})`} />
      {/* manchas de sol en diagonal */}
      {[0, 1, 2, 3].map((i) => <path key={i} d={`M${-300 + i * 560} ${HZ + 20}L${60 + i * 560} ${HZ + 20}L${900 + i * 760} ${H + 40}L${200 + i * 760} ${H + 40}Z`} fill={pal.groundL} opacity={0.22} />)}
      {bits}
    </g>
  );
});

const Rays: React.FC<{ id: string; a?: number; col?: string }> = ({ id, a = 0.16, col = '#fff8d0' }) => (
  <g opacity={a}>
    <defs><linearGradient id={id} x1="0" y1="0" x2="0.6" y2="1"><stop offset="0" stopColor={col} stopOpacity={1} /><stop offset="1" stopColor={col} stopOpacity={0} /></linearGradient></defs>
    {[0, 1, 2, 3, 4].map((i) => <path key={i} d={`M${-100 + i * 150} -40L${40 + i * 170} -40L${1050 + i * 330} ${H}L${650 + i * 330} ${H}Z`} fill={`url(#${id})`} />)}
  </g>
);

/** marco oscuro en primer plano: roca con musgo, tronco caído y helechos */
const Frame: React.FC<{ pal: Pal; seed: number; f: number; side: number }> = React.memo(({ pal, seed, side }) => {
  const dk: Pal = { ...pal, leafM: pal.leafD, leafL: pal.leafM, leafD: mix(pal.leafD, '#06040c', 0.5), alt: mix(pal.alt, '#06040c', 0.4), altL: pal.alt, rock: pal.rockD, rockL: pal.rock, rockD: mix(pal.rockD, '#06040c', 0.5), trunk: mix(pal.trunk, '#06040c', 0.4) };
  const x = side > 0 ? 1650 : 270;
  return (
    <g>
      <path d={capsule([x - side * 700, 1130], [x + side * 420, 985], 70, 46)} fill={dk.trunk} stroke={pal.ink} strokeWidth={6} />
      <path d={capsule([x - side * 640, 1096], [x + side * 400, 962], 14, 9)} fill={pal.trunkL} opacity={0.75} />
      <Rock x={x + side * 120} y={1130} w={620} h={250} seed={seed} pal={dk} moss />
      <path d={scallop(x + side * 110, 890, 250, 46, 11, seed + 3)} fill="none" stroke={pal.leafH} strokeWidth={5} opacity={0.7} strokeDasharray="60 500" />
      <Fern x={x - side * 190} y={1110} s={330} seed={seed + 1} pal={dk} />
      <Fern x={x + side * 330} y={1120} s={280} seed={seed + 2} pal={dk} alt />
      <Reeds x={x + side * 20} y={900} s={170} seed={seed + 4} pal={dk} />
    </g>
  );
});

/** ribera frondosa con profundidad: río en diagonal, bosque que se aleja, marco en primer plano */
export const Riverbank: React.FC<EnvProps> = ({ f, px = 0, pal = DAY, seed = 1, children, fg = true, moon }) => {
  const id = useId().replace(/:/g, '');
  const items = useMemo(() => [
    ...scatterZ(seed * 7 + 1, 46, ['g', 'u', 'g', 'c', 'u', 'g'], 0.03, 0.2, 560),
    ...scatterZ(seed * 7 + 5, 28, ['g', 'u', 'c', 'g', 'u'], 0.2, 0.46, 620),
    ...scatterZ(seed * 7 + 2, 80, ['f', 'r', 'b', 'f', 'k', 'r', 'b'], 0.08, 0.5, 420),
    ...scatterZ(seed * 7 + 3, 9, ['f', 'r', 'k', 'f', 'b'], 0.8, 0.96, 420),
  ].sort((a, b) => a.z - b.z), [seed]);
  const flip = seed % 2 === 0;
  const river: [number, number, number][] = [[2500, 0.0, 200], [1700, 0.06, 330], [2050, 0.14, 420], [1150, 0.23, 520], [1500, 0.33, 640], [500, 0.42, 800], [-900, 0.5, 1000]];
  const back = items.filter((i) => i.z <= CHILD_Z + 0.06), front = items.filter((i) => i.z > CHILD_Z + 0.06);
  return (
    <g>
      <Sky pal={pal} id={`sky${id}`} sun={!moon} />
      {moon && <g><circle cx={1380} cy={210} r={150} fill={pal.far2} opacity={0.6} /><circle cx={1340} cy={170} r={150} fill={pal.haze} opacity={0.18} /><circle cx={1330} cy={180} r={30} fill={pal.haze} opacity={0.25} /><circle cx={1430} cy={260} r={18} fill={pal.haze} opacity={0.2} /><circle cx={560} cy={280} r={40} fill="#f8f2ff" /><circle cx={560} cy={280} r={90} fill="#f8f2ff" opacity={0.18} /></g>}
      <Layer px={px} k={0.04}><Cloud x={700} y={200} s={70} seed={seed + 3} shade={pal.far2} /><Cloud x={1500} y={130} s={50} seed={seed + 4} shade={pal.far2} /><Cloud x={2300} y={240} s={80} seed={seed + 5} shade={pal.far2} /></Layer>
      <Layer px={px} k={0.07}><Hills pal={pal} seed={seed + 10} y={HZ - 40} amp={260} col={mix(pal.far2, pal.haze, 0.35)} /></Layer>
      <Layer px={px} k={0.13}><Hills pal={pal} seed={seed + 11} y={HZ - 8} amp={170} col={pal.far} lite={pal.far2} /></Layer>
      <rect x={0} y={HZ - 150} width={W} height={170} fill={pal.haze} opacity={0.3} />
      <rect x={0} y={HZ - 6} width={W} height={26} fill={pal.water} />
      <rect x={0} y={HZ - 6} width={W} height={5} fill={pal.waterL} opacity={0.7} />
      <Ground pal={pal} seed={seed + 20} id={`gr${id}`} />
      <Strip pts={river} px={px} fill={pal.water} edge={pal.ink} inner={pal.waterL} f={f} spark={pal.waterL} />
      {back.map((it, i) => <Plant key={i} it={it} pal={pal} f={f} px={px} />)}
      <Layer px={px} k={1}>{children}</Layer>
      {front.map((it, i) => <Plant key={i} it={it} pal={pal} f={f} px={px} sway={1.3} />)}
      <Rays id={`ry${id}`} a={moon ? 0.1 : 0.17} col={moon ? '#e8d8ff' : '#fff8d0'} />
      {fg && <Layer px={px} k={1.9}>{[0, 1, 2, 3].map((i) => <g key={i} transform={`translate(${-900 + i * 2300 + (flip ? 900 : 0)} 0)`}><Frame pal={pal} seed={seed + 40 + i} f={f} side={i % 2 ? 1 : -1} /></g>)}</Layer>}
    </g>
  );
};

/** llanura seca con mesetas: profundidad por cauce seco en diagonal, bruma y sombras largas */
export const DryPlain: React.FC<EnvProps> = ({ f, px = 0, pal = DRY, seed = 1, children, fg = true }) => {
  const id = useId().replace(/:/g, '');
  const mesas = useMemo(() => { const r = rng(seed * 13); return Array.from({ length: 9 }, (_, i) => ({ x: X0 + 250 + i * 520 + r() * 200, w: 220 + r() * 220, h: 260 + r() * 300, s: seed * 50 + i })); }, [seed]);
  const far = useMemo(() => { const r = rng(seed * 17); return Array.from({ length: 12 }, (_, i) => ({ x: X0 + i * 400 + r() * 200, w: 160 + r() * 200, h: 120 + r() * 200, s: seed * 60 + i })); }, [seed]);
  const items = useMemo(() => [
    ...scatterZ(seed * 9 + 2, 30, ['k', 'r', 'k', 'f', 'b', 'k'], 0.05, 0.5, 430),
    ...scatterZ(seed * 9 + 3, 6, ['k', 'r', 'f'], 0.8, 0.96, 430),
    ...scatterZ(seed * 9 + 4, 7, ['c', 'u'], 0.1, 0.4, 420),
  ].sort((a, b) => a.z - b.z), [seed]);
  const bed: [number, number, number][] = [[300, 0.0, 50], [900, 0.1, 120], [600, 0.2, 200], [1300, 0.32, 300], [1000, 0.44, 420], [2100, 0.56, 600]];
  const back = items.filter((i) => i.z <= CHILD_Z + 0.06), front = items.filter((i) => i.z > CHILD_Z + 0.06);
  return (
    <g>
      <Sky pal={pal} id={`sky${id}`} h={720} />
      <Layer px={px - f * 0.25} k={0.05}><Cloud x={500} y={170} s={85} seed={seed + 1} /><Cloud x={1100} y={90} s={55} seed={seed + 2} /><Cloud x={1750} y={220} s={100} seed={seed + 3} /><Cloud x={2500} y={130} s={70} seed={seed + 4} /></Layer>
      <Layer px={px} k={0.1}>{far.map((m, i) => <Mesa key={i} x={m.x} y={HZ + 10} w={m.w} h={m.h} seed={m.s} pal={{ ...pal, rock: i % 2 ? pal.far : pal.far2 }} flat />)}</Layer>
      <rect x={0} y={HZ - 130} width={W} height={150} fill={pal.haze} opacity={0.34} />
      <Layer px={px} k={0.3}>{mesas.map((m, i) => <g key={i}><path d={`M${m.x - m.w * 0.5} ${HZ + 22}L${m.x + m.w * 0.5} ${HZ + 22}L${m.x + m.w * 1.5} ${HZ + 70}L${m.x + m.w * 0.2} ${HZ + 70}Z`} fill="#3a1f48" opacity={0.2} /><Mesa x={m.x} y={HZ + 24} w={m.w} h={m.h} seed={m.s} pal={pal} /></g>)}</Layer>
      <g transform={`translate(0 0)`}><Ground pal={pal} seed={seed + 21} id={`gr${id}`} dry /></g>
      <Strip pts={bed} px={px} fill={pal.groundD} inner={pal.rockD} />
      {back.map((it, i) => <Plant key={i} it={it} pal={pal} f={f} px={px} />)}
      <Layer px={px} k={1}>{children}</Layer>
      {front.map((it, i) => <Plant key={i} it={it} pal={pal} f={f} px={px} />)}
      <Rays id={`ry${id}`} a={0.12} />
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
