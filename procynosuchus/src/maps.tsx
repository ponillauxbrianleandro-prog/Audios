import React from 'react';
import { H, INK, Pt, W, clamp, eio, eout, leaf, lerp, poly, rng, seg, smooth } from './lib';
import { Beast, anchors } from './beast';
import { Burst, Label, Sil } from './fx';
import { Rock, DRY } from './art';

const B: Pt[] = [[800, 455], [865, 550], [855, 670], [800, 790]];
const LAND: Record<string, Pt[]> = {
  na: [[520, 170], [700, 110], [880, 150], [930, 260], [905, 380], [810, 450], [660, 440], [560, 340], [500, 250]],
  eu: [[930, 150], [1100, 90], [1320, 110], [1470, 200], [1440, 330], [1300, 385], [1150, 365], [1010, 405], [935, 330]],
  sa: [[600, 480], [690, 438], ...B, [765, 870], [738, 940], [700, 885], [655, 760], [615, 640], [585, 545]],
  af: [[800, 455], [880, 415], [1010, 404], [1120, 428], [1195, 470], [1245, 522], [1175, 562], [1152, 660], [1090, 780], [1010, 860], [960, 876], [900, 852], [850, 802], [800, 790], [855, 670], [865, 550]],
  an: [[750, 905], [860, 862], [960, 882], [1090, 862], [1200, 900], [1180, 990], [1000, 1030], [820, 1000]],
  ind: [[1085, 795], [1160, 672], [1232, 700], [1250, 800], [1170, 852]],
  au: [[1212, 882], [1262, 812], [1400, 800], [1470, 880], [1400, 960], [1262, 972]],
};
export const SITE = { karoo: [925, 815] as Pt, zambia: [965, 715] as Pt, tanz: [1035, 680] as Pt, korbach: [1015, 372] as Pt };
const NAMES: Record<string, [string, number, number]> = { sa: ['SUDAMÉRICA', 715, 640], af: ['ÁFRICA', 1010, 570], an: ['ANTÁRTIDA', 975, 955], ind: ['INDIA', 1168, 770], au: ['AUSTRALIA', 1340, 890], na: ['', 0, 0], eu: ['', 0, 0] };

export const Pangea: React.FC<{ f: number; gap?: number; hi?: string[]; names?: boolean; sites?: (keyof typeof SITE)[]; arc?: number; belt?: number; label?: string }> = ({ f, gap = 0, hi = [], names, sites = [], arc = 0, belt = 0, label }) => {
  const r = rng(8);
  const a = SITE.karoo, b = SITE.korbach;
  const arcD = `M${a[0]} ${a[1]}Q${a[0] + 330} ${(a[1] + b[1]) / 2} ${b[0]} ${b[1]}`;
  return (
    <g>
      <rect x={-3000} y={-3000} width={8000} height={8000} fill="#123a6a" />
      <rect x={-3000} y={-3000} width={8000} height={8000} fill="#1f6aa8" opacity={0.6} />
      {Array.from({ length: 9 }, (_, i) => <ellipse key={i} cx={960} cy={540} rx={200 + i * 150} ry={120 + i * 90} fill="none" stroke="#7fd0f0" strokeWidth={2} opacity={0.14} />)}
      {Array.from({ length: 40 }, (_, i) => { const x = r() * W, y = r() * H; return <path key={i} d={`M${x} ${y}q14 -9 28 0q14 9 28 0`} stroke="#bfeaff" strokeWidth={2.5} fill="none" opacity={0.25 + 0.2 * Math.sin(f / 10 + i)} />; })}
      {Object.entries(LAND).map(([k, pts]) => {
        const d = smooth(pts, true, 0.75);
        const on = hi.includes(k);
        const tf = k === 'sa' && gap ? `translate(${-gap} ${gap * 0.12}) rotate(${-gap * 0.02} 700 650)` : undefined;
        const cx = pts.reduce((s, p) => s + p[0], 0) / pts.length, cy = pts.reduce((s, p) => s + p[1], 0) / pts.length;
        return (
          <g key={k} transform={tf}>
            <path d={d} fill={INK} stroke={INK} strokeWidth={9} strokeLinejoin="round" />
            <path d={d} fill={on ? '#f2c94c' : k === 'na' || k === 'eu' ? '#6fae5a' : '#8cc860'} />
            <path d={d} fill={on ? '#fff1a8' : '#c4e88a'} opacity={0.6} transform={`translate(${cx * 0.2 - 8} ${cy * 0.2 - 8}) scale(0.8)`} />
            {names && NAMES[k][0] && <Label x={NAMES[k][1]} y={NAMES[k][2]} text={NAMES[k][0]} size={22} col={INK} anchor="middle" a={on ? 1 : 0.55} />}
          </g>
        );
      })}
      {belt > 0 && (
        <g opacity={belt}>
          {Array.from({ length: 12 }, (_, i) => { const x = lerp(690, 950, i / 11), y = lerp(835, 838, i / 11) + Math.sin(i) * 8; return <path key={i} d={`M${x - 16} ${y + 12}L${x} ${y - 16}L${x + 16} ${y + 12}Z`} fill="#b06a8a" stroke={INK} strokeWidth={3} strokeLinejoin="round" />; })}
          <path d="M680 850L960 852" stroke="#ffe066" strokeWidth={5} strokeDasharray="4 12" strokeLinecap="round" opacity={0.6 + 0.4 * Math.sin(f / 3)} />
        </g>
      )}
      {arc > 0 && <path d={arcD} pathLength={1} strokeDasharray={`${arc} 1`} fill="none" stroke="#fff" strokeWidth={7} strokeLinecap="round" />}
      {arc > 0 && <path d={arcD} pathLength={1} strokeDasharray={`${arc} 1`} fill="none" stroke="#ff4f6a" strokeWidth={3.5} strokeLinecap="round" />}
      {sites.map((s) => {
        const p = SITE[s];
        const pu = (f % 24) / 24;
        return (
          <g key={s}>
            <circle cx={p[0]} cy={p[1]} r={10 + pu * 38} fill="none" stroke="#ff4f6a" strokeWidth={5 * (1 - pu)} />
            <circle cx={p[0]} cy={p[1]} r={11} fill="#ff4f6a" stroke="#fff" strokeWidth={4} />
          </g>
        );
      })}
      {label && <Label x={a[0] + 215} y={(a[1] + b[1]) / 2 + 8} text={label} size={26} bg />}
    </g>
  );
};

const grow = (t: number) => ({ pathLength: 1, strokeDasharray: `${clamp(t)} 1` });

/** tree of life: sauropsids (blue) vs synapsids (orange) */
export const TreeDiagram: React.FC<{ f: number; t: number; stage: number }> = ({ f, t, stage }) => {
  // stage 0 trunk+split, 1 blue grows, 2 orange grows, 3 mammals, 4 therapsid/cynodont labels, 5 procy twig
  const g = (s: number) => (stage > s ? 1 : stage === s ? eout(t) : 0);
  const blue = '#5fb4ff', or = '#ff9a3c';
  return (
    <g>
      <rect x={-3000} y={-3000} width={8000} height={8000} fill="#0b0f22" />
      {Array.from({ length: 60 }, (_, i) => { const r = rng(i + 30); return <circle key={i} cx={r() * W} cy={r() * H} r={1 + r() * 2} fill="#fff" opacity={0.1 + 0.2 * Math.abs(Math.sin(f / 20 + i))} />; })}
      <path d="M960 1040L960 800" stroke="#e8e4f0" strokeWidth={14} strokeLinecap="round" {...grow(g(0) * 2)} />
      <path d="M960 800C960 650 700 640 560 470" fill="none" stroke={blue} strokeWidth={12} strokeLinecap="round" {...grow(g(0) * 2 - 1)} />
      <path d="M960 800C960 650 1220 640 1360 470" fill="none" stroke={or} strokeWidth={12} strokeLinecap="round" {...grow(g(0) * 2 - 1)} />
      {/* blue side */}
      <path d="M560 470C500 390 380 380 300 300" fill="none" stroke={blue} strokeWidth={9} strokeLinecap="round" {...grow(g(1) * 1.5)} />
      <path d="M560 470C560 370 540 300 560 200" fill="none" stroke={blue} strokeWidth={9} strokeLinecap="round" {...grow(g(1) * 1.5 - 0.2)} />
      <path d="M560 470C640 400 740 360 790 260" fill="none" stroke={blue} strokeWidth={9} strokeLinecap="round" {...grow(g(1) * 1.5 - 0.4)} />
      <g opacity={seg(g(1), 0.3, 0.6)}><Sil kind="lizard" x={250} y={290} s={0.55} col={blue} f={f} /></g>
      <g opacity={seg(g(1), 0.5, 0.8)}><Sil kind="dino" x={560} y={190} s={0.42} col={blue} f={f} /></g>
      <g opacity={seg(g(1), 0.7, 1)}><Sil kind="bird" x={820} y={220} s={0.7} col={blue} f={f} /></g>
      {stage >= 1 && <Label x={330} y={520} text="SAURÓPSIDOS" size={26} col={blue} a={g(1)} />}
      {/* orange side */}
      <path d="M1360 470C1380 380 1420 330 1500 250" fill="none" stroke={or} strokeWidth={10} strokeLinecap="round" {...grow(g(2) * 1.3)} />
      {stage >= 2 && <Label x={1400} y={520} text="SINÁPSIDOS" size={26} col={or} a={g(2)} />}
      <path d="M1500 250C1560 200 1620 190 1700 130" fill="none" stroke={or} strokeWidth={10} strokeLinecap="round" {...grow(g(3) * 1.3)} />
      <g opacity={g(3)}>
        <circle cx={1700} cy={130} r={70 + Math.sin(f / 5) * 6} fill={or} opacity={0.2} />
        <Sil kind="dog" x={1700} y={170} s={0.42} col="#fff" f={f} />
        <Label x={1700} y={52} text="MAMÍFEROS" size={26} col="#fff" anchor="middle" />
      </g>
      <g opacity={g(4)}>
        <circle cx={1432} cy={330} r={13} fill={or} stroke="#fff" strokeWidth={4} />
        <Label x={1250} y={338} text="TERÁPSIDOS" size={22} col="#ffd9b0" anchor="end" />
        <path d="M1255 330L1410 330" stroke="#ffd9b0" strokeWidth={2} />
        <circle cx={1500} cy={250} r={13} fill={or} stroke="#fff" strokeWidth={4} />
        <Label x={1330} y={258} text="CINODONTOS" size={22} col="#fff" anchor="end" />
        <path d="M1335 250L1480 250" stroke="#fff" strokeWidth={2} />
      </g>
      <path d="M1500 250C1470 200 1420 170 1360 150" fill="none" stroke="#ffe066" strokeWidth={8} strokeLinecap="round" {...grow(g(5) * 1.3)} />
      <g opacity={seg(g(5), 0.5, 1)}>
        <circle cx={1280} cy={130} r={86} fill="#ffe066" opacity={0.16 + 0.06 * Math.sin(f / 4)} />
        <Beast x={1290} y={160} s={0.26} f={f} shadow={false} />
        <Label x={1280} y={56} text="PROCYNOSUCHUS" size={22} col="#ffe066" anchor="middle" />
      </g>
    </g>
  );
};

/** jaw bones -> ear bones. t 0..1 */
export const JawEar: React.FC<{ f: number; t: number; travel?: boolean }> = ({ f, t, travel = true }) => {
  const BP = { x: 400, y: 740, s: 2.1, yaw: 40, jaw: 8 };
  const an = anchors(BP);
  const hinge: Pt = [BP.x + an.hinge[0] * BP.s + 30, BP.y + an.hinge[1] * BP.s - 10], ear: Pt = [1490, 520];
  const mth: Pt = [BP.x + an.mouth[0] * BP.s, BP.y + an.mouth[1] * BP.s + 20];
  const k = travel ? eio(seg(t, 0.35, 0.8)) : 0;
  const pos = (o: number): Pt => {
    const kk = clamp(k - o * 0.06);
    return [lerp(hinge[0], ear[0], kk) + o * 18 * (1 - kk), lerp(hinge[1], ear[1], kk) - Math.sin(Math.PI * kk) * 330 + o * 10 * kk];
  };
  const p1 = pos(0), p2 = pos(1);
  const glow = 0.6 + 0.4 * Math.sin(f / 3);
  const sc = lerp(1, 0.45, k);
  const head = smooth([[1560, 800], [1650, 530], [1500, 290], [1335, 360], [1302, 440], [1292, 470], [1246, 522], [1286, 546], [1276, 576], [1290, 592], [1280, 612], [1302, 672], [1385, 704], [1400, 800]], true, 0.8);
  const boom = seg(t, 0.8, 1);
  return (
    <g>
      <rect x={-3000} y={-3000} width={8000} height={8000} fill="#0d1026" />
      <circle cx={520} cy={560} r={420} fill="#23306a" opacity={0.5} />
      <circle cx={1460} cy={540} r={380} fill="#3a2360" opacity={lerp(0.25, 0.7, k)} />
      <Beast {...BP} f={f} shadow={false} />
      <rect width={960} height={H} fill="#0d1026" opacity={0.45} />
      {/* dentary highlight */}
      <path d={leaf([hinge[0] + 30, hinge[1] + 26], [mth[0], mth[1] + 10], 40, 10)} fill="none" stroke="#9fd0ff" strokeWidth={4} strokeDasharray="10 8" opacity={seg(t, 0.05, 0.2)} />
      <path d={head} fill="#1b1436" stroke="#b9a8ff" strokeWidth={5} opacity={lerp(0.35, 1, k)} />
      <path d={`M${ear[0] - 30} ${ear[1] - 55}q70 -20 60 50q-6 50 -40 60q-20 -10 -10 -40q14 -30 -10 -70z`} fill="#2a1f52" stroke="#b9a8ff" strokeWidth={4} opacity={lerp(0.35, 1, k)} />
      <path d={`M${hinge[0]} ${hinge[1]}Q${(hinge[0] + ear[0]) / 2} ${hinge[1] - 560} ${ear[0]} ${ear[1]}`} fill="none" stroke="#ffb040" strokeWidth={4} strokeDasharray="3 14" strokeLinecap="round" opacity={0.55 * seg(t, 0.3, 0.45) * (1 - boom)} />
      {[p1, p2].map((p, i) => (
        <g key={i} transform={`translate(${p[0]} ${p[1]}) scale(${sc})`}>
          <circle r={46} fill="#ffb040" opacity={0.25 * glow} />
          <path d={i ? leaf([-20, -6], [22, 8], 16, 5) : smooth([[-18, -14], [6, -20], [20, -4], [8, 16], [-14, 12]], true)} fill="#ffcf5a" stroke="#fff" strokeWidth={4} strokeLinejoin="round" />
        </g>
      ))}
      <g opacity={seg(t, 0.05, 0.2) * (1 - seg(t, 0.35, 0.5))}><Label x={hinge[0] - 60} y={hinge[1] + 110} text="huesos de la mandíbula" size={26} col="#ffcf5a" /></g>
      <g opacity={boom}><Label x={ear[0]} y={ear[1] + 150} text="martillo y yunque" size={26} col="#ffcf5a" anchor="middle" /></g>
      <Burst x={ear[0]} y={ear[1]} t={seg(t, 0.78, 1)} col="#ffe9a8" />
    </g>
  );
};

/** fossil find: skull fragment and two mandibles on a slab */
export const Dig: React.FC<{ f: number; t: number; close?: boolean }> = ({ f, t, close }) => {
  const r = rng(12);
  const bone = '#efe2c0', boneD = '#b89f74';
  const jawD = (y: number, s: number, fl: number) => `translate(${960 + fl * 40} ${y}) scale(${s * fl} ${s})`;
  const mand = smooth([[-150, -10], [-60, -24], [60, -30], [150, -22], [170, 0], [140, 24], [40, 30], [-80, 34], [-160, 22]], true, 0.8);
  const sweep = Math.sin(f / 4) * 60;
  return (
    <g>
      <rect width={W} height={H} fill="#d9a868" />
      {Array.from({ length: 40 }, (_, i) => <ellipse key={i} cx={r() * W} cy={r() * H} rx={40 + r() * 160} ry={8 + r() * 14} fill={r() < 0.5 ? '#c08a50' : '#f0cc90'} opacity={0.5} />)}
      <path d={smooth([[330, 880], [300, 620], [470, 380], [820, 300], [1250, 330], [1560, 470], [1640, 760], [1500, 930], [900, 980]], true, 0.5)} fill="#b08a70" stroke={INK} strokeWidth={8} strokeLinejoin="round" /><path d={smooth([[360, 860], [330, 630], [480, 410], [820, 330], [1230, 360], [1300, 600], [900, 760], [600, 900]], true, 0.5)} fill="#d2b090" /><path d="M1300 380l-60 180l90 130M520 520l110 60" stroke={INK} strokeWidth={5} fill="none" strokeLinecap="round" opacity={0.6} />
      <g transform={`translate(${close ? -160 : 0} ${close ? -60 : 0})`}>
        <g transform="translate(900 520) rotate(-8)">
          <path d={smooth([[-170, 20], [-150, -60], [-40, -100], [90, -80], [170, -30], [150, 30], [60, 20], [0, 50], [-90, 40]], true, 0.7)} fill={bone} stroke={INK} strokeWidth={6} strokeLinejoin="round" />
          <ellipse cx={-40} cy={-30} rx={34} ry={26} fill={boneD} stroke={INK} strokeWidth={4} />
          <path d="M60 -60l20 40l-30 30M-110 -20l30 10" stroke={INK} strokeWidth={3.5} fill="none" strokeLinecap="round" />
          {[0, 1, 2, 3, 4].map((i) => <path key={i} d={`M${70 + i * 18} 22l6 22l8 -22z`} fill={bone} stroke={INK} strokeWidth={3} strokeLinejoin="round" />)}
        </g>
        {[[690, 1, -6], [760, -1, 5]].map(([y, fl, rot], i) => (
          <g key={i} transform={`${jawD(y, 1, fl)} rotate(${rot})`}>
            <path d={mand} fill={bone} stroke={INK} strokeWidth={6} strokeLinejoin="round" />
            <path d="M-120 12q120 14 250 -8" stroke={boneD} strokeWidth={8} fill="none" strokeLinecap="round" />
            {[0, 1, 2, 3, 4, 5, 6].map((k) => <path key={k} d={`M${-40 + k * 26} -28l8 -22l8 22z`} fill={bone} stroke={INK} strokeWidth={3} strokeLinejoin="round" />)}
          </g>
        ))}
      </g>
      {/* brush */}
      <g transform={`translate(${1250 + sweep} ${420 + Math.cos(f / 4) * 20}) rotate(${28 + sweep * 0.1})`}>
        <rect x={-18} y={-330} width={36} height={250} rx={16} fill="#8a4a2c" stroke={INK} strokeWidth={5} />
        <rect x={-30} y={-90} width={60} height={40} fill="#c8c8d0" stroke={INK} strokeWidth={5} />
        <path d="M-32 -50L-44 60L44 60L32 -50Z" fill="#f0d898" stroke={INK} strokeWidth={5} strokeLinejoin="round" />
      </g>
      {Array.from({ length: 26 }, (_, i) => { const p = ((f * 0.04 + r()) % 1); return <circle key={i} cx={1150 + sweep + (r() - 0.5) * 300 + p * 120} cy={520 - p * 200 + r() * 120} r={6 + r() * 16} fill="#f6e2b8" opacity={0.5 * (1 - p)} />; })}
      <Label x={110} y={130} text="2007 · TANZANIA" size={34} bg a={seg(t, 0, 0.15)} />
    </g>
  );
};

export const TitleCard: React.FC<{ f: number; t: number }> = ({ f, t }) => {
  const k = eout(seg(t, 0, 0.25));
  return (
    <g>
      <rect width={W} height={H} fill="#07050c" />
      <circle cx={960} cy={500} r={lerp(200, 520, k)} fill="#ff7a3c" opacity={0.9} />
      <circle cx={960} cy={500} r={lerp(120, 400, k)} fill="#ffd060" />
      <Beast x={900} y={640} s={lerp(2.2, 1.8, k)} yaw={30} drift={0} phase={f / 26} f={f} sil="#07050c" shadow={false} />
      <rect x={0} y={735} width={W} height={400} fill="#07050c" />
      <text x={960} y={850} textAnchor="middle" fontFamily="Inter, sans-serif" fontWeight={900} fontSize={104} fill="#fff" letterSpacing={lerp(40, 14, k)} opacity={k}>PROCYNOSUCHUS</text>
      <text x={960} y={915} textAnchor="middle" fontFamily="Inter, sans-serif" fontWeight={500} fontSize={30} fill="#ffd060" letterSpacing={12} opacity={seg(t, 0.25, 0.5)}>UN ANIMAL CHIQUITO · UN MUNDO GIGANTE</text>
    </g>
  );
};

/** flat colour card with a silhouette (fast montage) */
export const Card: React.FC<{ bg: string; bg2: string; children: React.ReactNode; t: number }> = ({ bg, bg2, children, t }) => (
  <g>
    <rect width={W} height={H} fill={bg} />
    <path d={poly([[0, H], [W, H * 0.45], [W, H], [0, H]])} fill={bg2} />
    <circle cx={960} cy={560} r={330 + t * 60} fill={bg2} opacity={0.7} />
    {children}
  </g>
);

/** measuring ruler under the animal */
export const Ruler: React.FC<{ x0: number; x1: number; y: number; t: number; text: string }> = ({ x0, x1, y, t, text }) => {
  const xe = lerp(x0, x1, eout(t));
  return (
    <g>
      <path d={`M${x0} ${y}L${xe} ${y}M${x0} ${y - 18}L${x0} ${y + 18}M${xe} ${y - 18}L${xe} ${y + 18}`} stroke={INK} strokeWidth={7} strokeLinecap="round" />
      {Array.from({ length: 13 }, (_, i) => { const x = lerp(x0, x1, i / 12); return x <= xe ? <path key={i} d={`M${x} ${y}l0 ${i % 2 ? 10 : 16}`} stroke={INK} strokeWidth={4} /> : null; })}
      <Label x={(x0 + x1) / 2} y={y + 62} text={text} size={34} col={INK} anchor="middle" a={seg(t, 0.5, 0.8)} />
    </g>
  );
};
