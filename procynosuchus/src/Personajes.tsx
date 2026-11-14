import React from 'react';
import { H, Pt, W, capsule, leaf } from './lib';
import { Beast } from './beast';

/**
 * Estilo 3 — personajes gráficos tipo señal de tránsito.
 * Cabeza redonda separada, torso compacto, brazos y piernas gruesos integrados al cuerpo.
 * Cada pose son ángulos (grados desde la vertical hacia abajo; positivo = hacia adelante).
 */
export type Pose = { lean?: number; armF: [number, number]; armB: [number, number]; legF: [number, number]; legB: [number, number]; dy?: number; head?: number };

export const POSES: Record<string, Pose> = {
  parado: { armF: [10, 6], armB: [-10, -6], legF: [7, 2], legB: [-7, -2] },
  caminando: { lean: 4, armF: [34, 58], armB: [-30, -14], legF: [30, 10], legB: [-24, -46] },
  corriendo: { lean: 16, armF: [58, 128], armB: [-62, -128], legF: [66, 14], legB: [-34, -104] },
  señalando: { armF: [84, 90], armB: [-8, -4], legF: [8, 2], legB: [-8, -2] },
  excavando: { lean: 44, armF: [38, 30], armB: [20, 34], legF: [84, -6], legB: [22, -92], dy: 62 },
  sosteniendo: { lean: -4, armF: [62, 132], armB: [48, 124], legF: [9, 2], legB: [-9, -2] },
  entregando: { lean: 8, armF: [72, 84], armB: [-14, -6], legF: [16, 4], legB: [-14, -22] },
  recibiendo: { lean: 6, armF: [64, 96], armB: [50, 92], legF: [14, 4], legB: [-12, -16] },
  sentado: { lean: -6, armF: [30, 80], armB: [10, 60], legF: [86, 4], legB: [80, 0], dy: 70 },
};

const rad = (d: number) => (d * Math.PI) / 180;
const seg = (p: Pt, a: number, l: number): Pt => [p[0] + Math.sin(rad(a)) * l, p[1] + Math.cos(rad(a)) * l];

export const Fig: React.FC<{ x: number; y: number; s?: number; pose?: Pose | keyof typeof POSES; col?: string; flip?: boolean; children?: React.ReactNode }> = ({ x, y, s = 1, pose = 'parado', col = '#101014', flip, children }) => {
  const P = typeof pose === 'string' ? POSES[pose] : pose;
  const lean = P.lean ?? 0;
  const hipY = -86 + (P.dy ?? 0);
  const limb = (p0: Pt, a: [number, number], l1: number, l2: number, w0: number, w1: number, k: string) => {
    const p1 = seg(p0, a[0], l1), p2 = seg(p1, a[1], l2);
    return <g key={k}><path d={capsule(p0, p1, w0, (w0 + w1) / 2)} /><path d={capsule(p1, p2, (w0 + w1) / 2, w1)} /></g>;
  };
  const hand = (a: [number, number]): Pt => { const sh: Pt = [0, -64]; const p1 = seg(sh, a[0] - lean, 46); return seg(p1, a[1] - lean, 44); };
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s})`} fill={col}>
      {limb([-9, hipY], P.legB, 44, 46, 13, 10.5, 'lb')}
      {limb([9, hipY], P.legF, 44, 46, 13, 10.5, 'lf')}
      <g transform={`translate(0 ${hipY}) rotate(${lean})`}>
        {limb([-4, -64], [P.armB[0] - lean, P.armB[1] - lean], 46, 44, 10.5, 8.5, 'ab')}
        <path d="M-27 -70Q-30 -84 -14 -86L14 -86Q30 -84 27 -70L20 -4Q18 10 0 10Q-18 10 -20 -4Z" />
        <circle cx={3} cy={-112 + (P.head ?? 0)} r={22} />
        {limb([4, -64], [P.armF[0] - lean, P.armF[1] - lean], 46, 44, 10.5, 8.5, 'af')}
        {children && <g transform={`translate(${hand(P.armF)[0]} ${hand(P.armF)[1]})`}>{children}</g>}
      </g>
    </g>
  );
};

const Bone: React.FC<{ col?: string; s?: number }> = ({ col = '#101014', s = 1 }) => (
  <g transform={`scale(${s}) rotate(-20)`} fill={col}><rect x={-26} y={-5} width={52} height={10} rx={5} /><circle cx={-27} cy={-6} r={8} /><circle cx={-27} cy={6} r={8} /><circle cx={27} cy={-6} r={8} /><circle cx={27} cy={6} r={8} /></g>
);
const Plant: React.FC<{ x: number; y: number; s?: number; col?: string }> = ({ x, y, s = 1, col = '#101014' }) => (
  <g transform={`translate(${x} ${y}) scale(${s})`} fill={col}>
    <path d={capsule([0, 0], [0, -120], 7, 5)} />
    {[[-1, -30, 150], [1, -52, 30], [-1, -78, 140], [1, -98, 40], [-1, -116, 120], [1, -122, 62]].map(([sd, yy, a], i) => { const e: Pt = [Math.cos(rad(a)) * 62, yy - Math.sin(rad(a)) * 44]; return <path key={i} d={leaf([0, yy], e, 13, sd * 6)} />; })}
  </g>
);

const Diamond: React.FC<{ x: number; y: number; s: number; children: React.ReactNode }> = ({ x, y, s, children }) => (
  <g transform={`translate(${x} ${y})`}>
    <rect x={-10} y={0} width={20} height={s * 1.5} fill="#1a1c22" />
    <g transform="rotate(45)"><rect x={-s * 0.7} y={-s * 0.7} width={s * 1.4} height={s * 1.4} rx={s * 0.1} fill="#101014" /><rect x={-s * 0.66} y={-s * 0.66} width={s * 1.32} height={s * 1.32} rx={s * 0.09} fill="#ffcf10" /><rect x={-s * 0.6} y={-s * 0.6} width={s * 1.2} height={s * 1.2} rx={s * 0.07} fill="none" stroke="#101014" strokeWidth={s * 0.03} /></g>
    {children}
  </g>
);
const Disc: React.FC<{ x: number; y: number; r: number; children: React.ReactNode }> = ({ x, y, r, children }) => (
  <g transform={`translate(${x} ${y})`}><circle r={r} fill="#e8eaec" /><circle r={r * 0.94} fill="#e41c2c" /><circle r={r * 0.76} fill="#f6f1e4" />{children}</g>
);
const Signal: React.FC<{ x: number; y: number; s: number; children: React.ReactNode }> = ({ x, y, s, children }) => (
  <g transform={`translate(${x} ${y})`}><rect x={-s * 0.62} y={-s * 0.62} width={s * 1.24} height={s * 1.24} rx={s * 0.1} fill="#f0a818" /><rect x={-s * 0.52} y={-s * 0.52} width={s * 1.04} height={s * 1.04} rx={s * 0.05} fill="#0c0c10" />
    <defs><pattern id="dots" width={7} height={7} patternUnits="userSpaceOnUse"><circle cx={3.5} cy={3.5} r={2.4} fill="#f4f6f8" /></pattern></defs>{children}</g>
);
const Tile: React.FC<{ x: number; y: number; w: number; h: number; col: string; label: string; children: React.ReactNode }> = ({ x, y, w, h, col, label, children }) => (
  <g transform={`translate(${x} ${y})`}>
    <rect width={w} height={h} rx={18} fill={col} />
    {children}
    <text x={w / 2} y={h - 16} textAnchor="middle" fontFamily="Inter, sans-serif" fontWeight={800} fontSize={20} fill="#101014" letterSpacing={2}>{label.toUpperCase()}</text>
  </g>
);

const COLS = ['#ffcf10', '#2fd6c8', '#ff7a1f', '#b48cff', '#a8e03c', '#ff5c8a', '#5cc8ff'];

export const LaminaPersonajes: React.FC = () => {
  const names = ['parado', 'caminando', 'corriendo', 'señalando', 'excavando', 'sosteniendo', 'sentado'] as const;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} width={W} height={H}>
      <rect width={W} height={H} fill="#121a26" />
      <text x={60} y={66} fontFamily="Inter, sans-serif" fontWeight={900} fontSize={34} fill="#f6f1e4" letterSpacing={4}>ESTILO 3 · PERSONAJES GRÁFICOS</text>
      <text x={60} y={100} fontFamily="Inter, sans-serif" fontWeight={500} fontSize={20} fill="#8fa0b4">Una figura articulada por código: mismas piezas, cualquier pose. Para edits rápidos, comparaciones y escenas con muchos individuos.</text>
      {/* soportes */}
      <Diamond x={210} y={300} s={150}><Fig x={0} y={96} s={0.86} pose="caminando" /></Diamond>
      <Disc x={520} y={300} r={140}><Beast x={-10} y={56} s={0.36} yaw={22} sil="#101014" shadow={false} drift={0} /></Disc>
      <Signal x={830} y={300} s={220}><g fill="url(#dots)"><Fig x={0} y={102} s={0.92} pose="caminando" col="url(#dots)" /></g></Signal>
      <Diamond x={1140} y={300} s={150}><Plant x={0} y={84} s={1.05} /></Diamond>
      <Disc x={1450} y={300} r={140}><Beast kind="gorgon" x={-14} y={66} s={0.2} yaw={22} jaw={14} sil="#101014" shadow={false} drift={0} /></Disc>
      <g transform="translate(1640 190)"><rect width={230} height={84} rx={10} fill="#101014" /><rect x={5} y={5} width={220} height={74} rx={7} fill="#ffcf10" /><text x={115} y={57} textAnchor="middle" fontFamily="Inter, sans-serif" fontWeight={900} fontSize={38} fill="#101014" letterSpacing={3}>PÉRMICO</text><rect y={104} width={230} height={84} rx={10} fill="#101014" /><rect x={5} y={109} width={220} height={74} rx={7} fill="#f6f1e4" /><text x={115} y={160} textAnchor="middle" fontFamily="Inter, sans-serif" fontWeight={900} fontSize={34} fill="#101014" letterSpacing={2}>255 Ma</text></g>
      {/* hoja de poses */}
      {names.map((n, i) => (
        <Tile key={n} x={60 + i * 258} y={490} w={240} h={284} col={COLS[i]} label={n}>
          <Fig x={120 - (n === 'corriendo' ? 14 : 0)} y={n === 'excavando' ? 170 : n === 'sentado' ? 160 : 212} s={n === 'excavando' || n === 'sentado' ? 0.86 : 0.9} pose={n}>{n === 'sosteniendo' ? <g transform="translate(-6 -18)"><Bone /></g> : n === 'excavando' ? <g transform="rotate(30)"><rect x={-5} y={0} width={10} height={46} rx={4} fill="#101014" /><path d="M-14 44L14 44L8 66L-8 66Z" fill="#101014" /></g> : null}</Fig>
        </Tile>
      ))}
      {/* interacciones y animales */}
      <Tile x={60} y={792} w={470} h={250} col="#f6f1e4" label="dos individuos">
        <Fig x={150} y={196} s={0.88} pose="entregando"><g transform="translate(22 -4)"><Bone s={0.9} /></g></Fig><Fig x={330} y={196} s={0.88} pose="recibiendo" flip />
      </Tile>
      <Tile x={550} y={792} w={420} h={250} col="#2fd6c8" label="el animal">
        <Beast x={196} y={172} s={0.5} yaw={24} sil="#101014" shadow={false} drift={0} phase={0.2} />
      </Tile>
      <Tile x={990} y={792} w={420} h={250} col="#ff5c8a" label="depredador y presa">
        <Beast kind="gorgon" x={120} y={180} s={0.26} yaw={22} jaw={16} sil="#101014" shadow={false} drift={0} phase={0.4} /><Beast x={350} y={186} s={0.2} yaw={22} sil="#101014" shadow={false} drift={0} phase={0.1} run />
      </Tile>
      <Tile x={1430} y={792} w={430} h={250} col="#a8e03c" label="muchos a la vez">
        {Array.from({ length: 9 }, (_, i) => <Fig key={i} x={48 + i * 42} y={186 - (i % 2) * 14} s={0.48} pose={(['parado', 'caminando', 'señalando', 'caminando', 'sosteniendo', 'parado', 'corriendo', 'caminando', 'parado'] as const)[i]} flip={i % 3 === 0} />)}
      </Tile>
    </svg>
  );
};
