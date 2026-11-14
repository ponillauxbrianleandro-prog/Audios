import React from 'react';
import { Pt, leaf, lerp, rng, smooth } from './lib';
import { FernP, Foliage, HorsetailP, LG, Mushroom, PH, PW, PaintDefs, RG, RockMass, Spiky, Trunk, dabs } from './paint';

// paleta fría y viva (referencia 1)
const TEAL = ['#05161c', '#0a3640', '#0f6e74', '#2bb8b2', '#8ee6d8'];
const GRASS = ['#08262a', '#0e4436', '#1d6a3c', '#4f9c38', '#a8cc48'];
const BUSH = ['#051a1e', '#0b3832', '#17603e', '#3f9a4c'];
const PURP = ['#180c38', '#3e2684', '#7e5ac4', '#bca8e8'];
const ROCK: [string, string, string] = ['#211830', '#54486e', '#9c90b8'];
const MOSS = ['#0c3a2c', '#1f6e36', '#5eac38', '#b6d84c'];
const HZ = 560;

const ridge = (seed: number, y: number, amp: number, step: number, flat = 0.5): Pt[] => {
  const r = rng(seed);
  const pts: Pt[] = [[-60, PH + 20]];
  let h = r();
  for (let x = -60; x <= PW + 60; x += step) { if (r() > flat) h = r(); pts.push([x, y - amp * (0.15 + h * 0.85)]); }
  pts.push([PW + 60, PH + 20]);
  return pts;
};

const Stars: React.FC = () => { const r = rng(5); return <g>{Array.from({ length: 220 }, (_, i) => <circle key={i} cx={r() * PW} cy={r() * 420} r={0.8 + r() * 2} fill="#fff" opacity={0.2 + r() * 0.6} />)}</g>; };

// ============ VALLE VIOLETA ============
const ValleSky: React.FC = () => {
  const r = rng(91);
  return (
    <g>
      <defs>
        <LG id="vs" stops={[[0, '#1e2a40'], [0.35, '#3d5270'], [0.7, '#7f96a8'], [1, '#c2cdc8']]} />
        <RG id="vm" stops={[[0, '#f2f0e6'], [0.55, '#cfd2cc'], [0.86, '#8e98a4'], [1, '#56647a']]} cx={0.36} cy={0.34} r={0.78} />
        <clipPath id="vmc"><circle cx={1480} cy={300} r={190} /></clipPath>
      </defs>
      <rect width={PW} height={HZ + 60} fill="url(#vs)" />
      {/* luna con mares, cráteres y sombra propia */}
      <circle cx={1480} cy={300} r={300} fill="#dfe6e8" opacity={0.28} filter="url(#b50)" />
      <circle cx={1480} cy={300} r={190} fill="url(#vm)" />
      <g clipPath="url(#vmc)">
        {[[1420, 250, 70, 52], [1530, 230, 44, 36], [1560, 330, 66, 60], [1430, 360, 50, 38], [1490, 300, 30, 24], [1380, 300, 36, 44]].map(([x, y, a2, b2], i) => <ellipse key={i} cx={x} cy={y} rx={a2} ry={b2} fill="#6c7888" opacity={0.42} filter="url(#b6)" transform={`rotate(${i * 37} ${x} ${y})`} />)}
        {Array.from({ length: 34 }, (_, i) => { const a2 = r() * 6.28, d = Math.sqrt(r()) * 180, x = 1480 + Math.cos(a2) * d, y = 300 + Math.sin(a2) * d, q = 4 + r() * 16; return <g key={i}><circle cx={x} cy={y} r={q} fill="#5c6878" opacity={0.5} /><circle cx={x - q * 0.25} cy={y - q * 0.25} r={q * 0.75} fill="#e6e6dc" opacity={0.5} /></g>; })}
        {[[1400, 240, 200], [1560, 330, 160], [1440, 380, 150]].map(([x, y, l], i) => Array.from({ length: 7 }, (_, k) => <path key={`${i}${k}`} d={`M${x} ${y}l${Math.cos(k * 0.9 + i) * l} ${Math.sin(k * 0.9 + i) * l}`} stroke="#f0eee2" strokeWidth={2} opacity={0.22} />))}
        <circle cx={1640} cy={400} r={230} fill="#1e2a40" opacity={0.55} filter="url(#b20)" />
      </g>
      {/* nubes pintadas: masas grises con luz arriba */}
      {Array.from({ length: 13 }, (_, i) => { const x = r() * PW, y = 60 + r() * 420, w = 260 + r() * 460; if (Math.abs(x - 1480) < 560 && y < 520) return null; return <g key={i}><ellipse cx={x} cy={y + w * 0.05} rx={w} ry={w * 0.13} fill="#3a4a62" opacity={0.75} filter="url(#b20)" /><ellipse cx={x - w * 0.1} cy={y - w * 0.03} rx={w * 0.8} ry={w * 0.1} fill="#93a4b4" opacity={0.8} filter="url(#b20)" /><ellipse cx={x - w * 0.25} cy={y - w * 0.07} rx={w * 0.45} ry={w * 0.05} fill="#e4e8e0" opacity={0.75} filter="url(#b6)" /></g>; })}
      {dabs(92, 500, (q) => { const x = q() * PW, y = 40 + q() * 480; return Math.hypot(x - 1480, y - 300) < 230 ? null : [x, y, q()]; }, ['#2c3a52', '#52687f', '#8fa2b2', '#d4dad6'], [60, 220], 0.06, 0.05, 0.12, [0.15, 0.4])}
    </g>
  );
};

const ValleFar: React.FC = () => (
  <g>
    <defs>
      <LG id="vf1" stops={[[0, '#5c6c8a'], [1, '#a8b6c0']]} /><LG id="vf2" stops={[[0, '#3e4e6a'], [1, '#8a9cac']]} /><LG id="vf3" stops={[[0, '#26344c'], [1, '#5c7488']]} />
      <LG id="vw" stops={[[0, '#b4d8d4'], [0.5, '#5aa8ac'], [1, '#2c6a80']]} />
    </defs>
    <g filter="url(#b2)">
      <path d={smooth(ridge(11, HZ - 20, 200, 150, 0.45), true, 0.35)} fill="url(#vf1)" />
      <path d={smooth(ridge(12, HZ - 6, 150, 120, 0.4), true, 0.4)} fill="url(#vf2)" />
    </g>
    <rect x={0} y={HZ - 22} width={PW} height={90} fill="url(#vw)" />
    {dabs(3, 260, (q) => [q() * PW, HZ - 18 + q() * 80, q()], ['#ffffff', '#d8fff8', '#8ff0ee'], [20, 90], 0.03, 0, 0.02, [0.3, 0.8])}
    <path d={smooth(ridge(13, HZ + 4, 105, 90, 0.35).map(([x, y]) => [x, y + (x > 1300 && x < 2000 ? 40 : 0)] as Pt), true, 0.4)} fill="url(#vf3)" />
    <rect x={0} y={HZ - 60} width={PW} height={110} fill="#c6d2d0" opacity={0.45} filter="url(#b20)" />
  </g>
);

const ValleMid: React.FC = () => {
  const r = rng(21);
  return (
    <g>
      <defs><LG id="vg1" stops={[[0, '#6fa44a'], [0.4, '#2f7a44'], [1, '#0f4a3c']]} /><LG id="vr1" x1={0} y1={0} x2={1} y2={1} stops={[[0, '#a8e8dc'], [0.5, '#2fa8b4'], [1, '#12587c']]} /></defs>
      {/* orilla lejana */}
      <path d={smooth([[-60, PH], [-60, 600], [300, 588], [700, 600], [1100, 584], [1500, 600], [1900, 590], [2400, 602], [PW + 60, 592], [PW + 60, PH]], true, 0.6)} fill="url(#vg1)" />
      {dabs(22, 900, (q) => { const x = q() * PW, y = 590 + q() * 90; return [x, y, 0.75 - Math.abs(x - 1400) / 2600 - (y - 590) / 260]; }, GRASS, [8, 20], 0.25, -Math.PI / 2, 0.6)}
      {/* río que baja del lago */}
      <path d={smooth([[1760, 584], [1560, 606], [1700, 640], [1380, 664], [1500, 700], [1640, 700], [1540, 664], [1840, 640], [1700, 610], [1840, 584]], true, 0.8)} fill="url(#vr1)" />
      {/* acantilado izquierdo con musgo */}
      <RockMass id="vc1" pts={[[90, 700], [70, 520], [160, 400], [330, 372], [520, 396], [640, 470], [690, 600], [720, 700]]} cols={ROCK} seed={3} moss={MOSS} mossT={0.22} />
      <RockMass id="vc2" pts={[[620, 700], [660, 600], [820, 566], [1060, 584], [1180, 650], [1200, 700]]} cols={['#2c2440', '#6a6088', '#b4acc8']} seed={4} moss={MOSS} mossT={0.12} />
      <RockMass id="vc3" pts={[[2500, 700], [2520, 540], [2640, 470], [2820, 480], [2960, 560], [3040, 700]]} cols={ROCK} seed={6} moss={MOSS} mossT={0.2} />
      {/* arbolitos violetas */}
      {[[150, 690, 150], [250, 700, 110], [60, 705, 90], [2380, 690, 140], [2290, 700, 100]].map(([x, y, s], i) => (
        <g key={i}>
          <Trunk id={`vlt${i}`} pts={[[x, y, 7], [x + 8, y - s * 0.5, 5], [x - 4, y - s, 3]]} cols={['#1c0f38', '#4a3478', '#8a70c0']} seed={i} />
          {[0, 1, 2].map((k) => <Foliage key={k} id={`vlf${i}${k}`} cx={x - 4 + (k - 1) * s * 0.22} cy={y - s * (0.75 + k * 0.2)} rx={s * 0.3} ry={s * 0.24} seed={i * 9 + k} cols={PURP} n={60} />)}
        </g>
      ))}
      {/* matas oscuras del fondo medio */}
      {[[1650, 640, 250, 120], [1250, 650, 150, 70], [2060, 650, 190, 90], [880, 660, 130, 60], [420, 668, 150, 60]].map(([x, y, a, b], i) => <Foliage key={i} id={`vb${i}`} cx={x} cy={y} rx={a} ry={b} seed={40 + i} cols={BUSH} n={220} leafLen={22} />)}
      {Array.from({ length: 16 }, (_, i) => <HorsetailP key={i} x={r() * PW} y={690 + r() * 16} h={70 + r() * 90} seed={i + 5} cols={['#0d4c58', '#149a9c', '#7af0e4']} />)}
    </g>
  );
};

const ValleNear: React.FC = () => {
  const r = rng(31);
  const light = (x: number, y: number) => 0.9 - Math.hypot((x - 1420) / 1500, (y - 780) / 520) * 0.75;
  return (
    <g>
      <defs>
        <LG id="vn1" stops={[[0, '#4f8a3c'], [0.3, '#226a3c'], [1, '#082e2c']]} />
        <LG id="vr2" x1={1} y1={0} x2={0} y2={1} stops={[[0, '#a8ecdc'], [0.4, '#28a0b0'], [1, '#0e4c74']]} />
      </defs>
      <path d={smooth([[-60, PH + 20], [-60, 690], [400, 672], [900, 690], [1400, 668], [1900, 690], [2400, 676], [PW + 60, 690], [PW + 60, PH + 20]], true, 0.6)} fill="url(#vn1)" />
      {/* charco de luz y sombras laterales */}
      <ellipse cx={1420} cy={800} rx={700} ry={120} fill="#c8e04c" opacity={0.5} filter="url(#b50)" />
      <ellipse cx={200} cy={1000} rx={800} ry={260} fill="#041c22" opacity={0.75} filter="url(#b50)" />
      <ellipse cx={2800} cy={980} rx={760} ry={300} fill="#041c22" opacity={0.8} filter="url(#b50)" />
      {/* río en diagonal */}
      <path d={smooth([[1560, 684], [1180, 716], [760, 790], [300, 850], [-80, 930], [-80, 1010], [420, 930], [900, 850], [1300, 760], [1660, 700]], true, 0.8)} fill="url(#vr2)" />
      {dabs(33, 160, (q) => { const t = q(); return [lerp(1500, -40, t) + (q() - 0.5) * 120, lerp(700, 960, t) + (q() - 0.5) * 30, q()]; }, ['#ffffff', '#d4fff6', '#8ff4ea'], [18, 80], 0.04, 2.9, 0.1, [0.4, 0.9])}
      <path d={smooth([[1560, 684], [1180, 716], [760, 790], [300, 850], [-80, 930]], false, 0.8)} fill="none" stroke="#0d4c46" strokeWidth={9} opacity={0.5} />
      {/* textura de musgo: miles de pinceladas */}
      {dabs(34, 3600, (q) => { const x = q() * PW, y = 690 + Math.pow(q(), 1.2) * 400; return [x, y, light(x, y)]; }, GRASS, [10, 34], 0.22, -Math.PI / 2, 0.55, [0.5, 0.95])}
      {dabs(35, 500, (q) => { const x = q() * PW, y = 700 + q() * 380; return [x, y, q()]; }, ['#a890d8', '#6cc8c8', '#d8d47a', '#d08ab8', '#e8ece0'], [3, 7], 0.6, 0, 3, [0.5, 0.9])}
      {/* acantilado derecho con árbol colgante */}
      <RockMass id="vcr" pts={[[2260, 930], [2230, 760], [2290, 600], [2250, 470], [2330, 330], [2470, 262], [2680, 250], [2880, 300], [3060, 290], [3060, 960], [2700, 990], [2420, 960]]} cols={['#150e24', '#463c62', '#9488ac']} seed={8} moss={MOSS} mossT={0.2} />
      {dabs(36, 90, (q) => [2260 + q() * 700, 300 + q() * 260, 0.4 + q() * 0.4], MOSS, [60, 190], 0.05, Math.PI / 2, 0.12, [0.6, 0.9])}
      {/* árbol colgante: tronco retorcido y ramas a la vista, hojas una por una */}
      <Trunk id="vtt" pts={[[2600, 330, 60], [2560, 250, 44], [2470, 180, 34], [2360, 130, 26], [2220, 96, 18], [2060, 90, 11], [1930, 120, 6]]} cols={['#04080f', '#101c2c', '#3c5670']} seed={2} />
      <Trunk id="vtt2" pts={[[2500, 200, 26], [2560, 110, 18], [2660, 50, 11], [2800, 20, 6]]} cols={['#04080f', '#101c2c', '#3c5670']} seed={3} />
      <Trunk id="vtt3" pts={[[2580, 300, 34], [2720, 300, 22], [2860, 250, 13], [2990, 240, 7]]} cols={['#04080f', '#101c2c', '#3c5670']} seed={4} />
      <Trunk id="vtt4" pts={[[2380, 140, 16], [2330, 60, 10], [2240, 10, 5]]} cols={['#04080f', '#101c2c', '#3c5670']} seed={5} />
      <Trunk id="vtt5" pts={[[2240, 100, 12], [2170, 170, 8], [2080, 200, 4]]} cols={['#04080f', '#101c2c', '#3c5670']} seed={6} />
      <Trunk id="vtt6" pts={[[2600, 330, 40], [2520, 380, 26], [2420, 400, 14]]} cols={['#04080f', '#101c2c', '#3c5670']} seed={7} />
      {[[1960, 130, 150, 60], [2110, 70, 170, 60], [2290, 40, 150, 55], [2090, 210, 130, 55], [2220, 150, 110, 45], [2470, 40, 140, 50], [2650, 20, 170, 55], [2820, 30, 150, 55], [2890, 230, 140, 60], [2420, 400, 110, 45], [2750, 150, 120, 50], [1850, 180, 90, 40]].map(([x, y, a2, b2], i) => (
        <g key={i}>
          <ellipse cx={x} cy={y + b2 * 0.4} rx={a2 * 0.8} ry={b2 * 0.7} fill="#05161c" opacity={0.55} filter="url(#b6)" />
          {dabs(600 + i, 150, (q) => { const u = q(), v = q(); const px = x + (u - 0.5) * 2 * a2, py = y + (v - 0.5) * b2 * 1.4 + Math.abs(u - 0.5) * b2 * 0.6; return [px, py, 0.72 - v * 0.5 - (u - 0.4) * 0.35]; }, TEAL, [34, 84], 0.13, Math.PI / 2 + 0.12, 0.34, [0.75, 1])}
          {dabs(700 + i, 26, (q) => [x + (q() - 0.5) * 1.8 * a2, y + b2 * 0.4, 0.3 + q() * 0.3], TEAL, [90, 230], 0.035, Math.PI / 2 + 0.05, 0.1, [0.6, 0.9])}
          {dabs(800 + i, 46, (q) => [x + (q() - 0.6) * 1.7 * a2, y - b2 * 0.5 + q() * b2 * 0.7, 1], ['#bff6ea'], [26, 60], 0.11, Math.PI / 2 + 0.15, 0.3, [0.7, 1])}
        </g>
      ))}
      {/* ramas otra vez por delante, y algunas hojas encima */}
      <Trunk id="wtt" pts={[[2600, 330, 60], [2560, 250, 44], [2470, 180, 34], [2360, 130, 26], [2220, 96, 18], [2060, 90, 11], [1930, 120, 6]]} cols={['#04080f', '#101c2c', '#3c5670']} seed={2} />
      <Trunk id="wtt2" pts={[[2500, 200, 26], [2560, 110, 18], [2660, 50, 11], [2800, 20, 6]]} cols={['#04080f', '#101c2c', '#3c5670']} seed={3} />
      <Trunk id="wtt3" pts={[[2580, 300, 34], [2720, 300, 22], [2860, 250, 13], [2990, 240, 7]]} cols={['#04080f', '#101c2c', '#3c5670']} seed={4} />
      <Trunk id="wtt4" pts={[[2380, 140, 16], [2330, 60, 10], [2240, 10, 5]]} cols={['#04080f', '#101c2c', '#3c5670']} seed={5} />
      <Trunk id="wtt5" pts={[[2240, 100, 12], [2170, 170, 8], [2080, 200, 4]]} cols={['#04080f', '#101c2c', '#3c5670']} seed={6} />
      <Trunk id="wtt6" pts={[[2600, 330, 40], [2520, 380, 26], [2420, 400, 14]]} cols={['#04080f', '#101c2c', '#3c5670']} seed={7} />
      {dabs(990, 260, (q) => [1850 + q() * 1150, q() * 420, 0.5 + q() * 0.5], TEAL, [30, 70], 0.13, Math.PI / 2 + 0.12, 0.34, [0.8, 1])}
      <ellipse cx={2150} cy={930} rx={420} ry={90} fill="#06242e" opacity={0.55} filter="url(#b20)" />
      {/* fondo cercano denso: franja de plantas detrás del recorrido */}
      {Array.from({ length: 34 }, (_, i) => { const x = (i / 34) * PW + r() * 60, y = 706 + r() * 34, k = r(); const s2 = 60 + r() * 70; return k < 0.3 ? <FernP key={`a${i}`} x={x} y={y} s={s2} seed={900 + i} cols={i % 2 ? TEAL : BUSH.concat(['#7fc86a'])} n={7} /> : k < 0.5 ? <Spiky key={`a${i}`} id={`vex${i}`} x={x} y={y} s={s2 * 0.8} seed={900 + i} cols={i % 3 ? ['#0a3640', '#0f6e74', '#8ee6d8'] : ['#180c38', '#3e2684', '#bca8e8']} /> : k < 0.72 ? <HorsetailP key={`a${i}`} x={x} y={y} h={s2 * 1.8} seed={900 + i} cols={['#0a3640', '#0f6e74', '#6fd8cc']} /> : <Foliage key={`a${i}`} id={`vey${i}`} cx={x} cy={y - s2 * 0.3} rx={s2 * 0.9} ry={s2 * 0.5} seed={900 + i} cols={BUSH} n={90} leafLen={20} />; })}
      {/* mata oscura de hojas grandes */}
      <Foliage id="vbig" cx={760} cy={770} rx={250} ry={120} seed={77} cols={BUSH} n={420} leafLen={44} />
      <Foliage id="vbig2" cx={2020} cy={800} rx={200} ry={100} seed={78} cols={BUSH} n={320} leafLen={40} />
      {/* brotes claros */}
      {[[980, 800, 46], [1150, 935, 60], [1760, 950, 56], [1880, 820, 40], [620, 880, 50]].map(([x, y, h], i) => dabs(950 + i, 30, (q) => [x + (q() - 0.5) * h * 0.9, y, 0.5 + q() * 0.5], ['#5fb8a8', '#a8e8d8', '#e8fff0'], [h * 0.5, h * 1.2], 0.05, -Math.PI / 2, 0.45, [0.7, 1]))}
      {/* plantas medianas a los costados */}
      {[[330, 880, 190], [110, 790, 150], [640, 940, 150], [2060, 900, 180], [1900, 770, 110]].map(([x, y, s], i) => <FernP key={i} x={x} y={y} s={s} seed={80 + i} cols={i % 2 ? TEAL : BUSH.concat(['#9af07a'])} />)}
      {[[520, 830, 120], [2180, 840, 130], [900, 740, 70], [1800, 730, 60]].map(([x, y, s], i) => <Spiky key={i} id={`vsp${i}`} x={x} y={y} s={s} seed={90 + i} cols={i % 2 ? ['#0d4c58', '#18b0ac', '#8ffff0'] : ['#2a1260', '#7040d0', '#c8a0ff']} />)}
      {[[220, 760, 210], [270, 770, 150], [1960, 740, 190], [2010, 750, 130], [1120, 716, 90]].map(([x, y, h], i) => <HorsetailP key={i} x={x} y={y} h={h} seed={100 + i} cols={['#0d4c58', '#149a9c', '#7af0e4']} />)}
      {[[430, 900, 60], [470, 915, 40], [760, 760, 30], [1680, 742, 28], [2120, 960, 56], [1020, 730, 22], [1900, 900, 40]].map(([x, y, s], i) => <Mushroom key={i} id={`vmu${i}`} x={x} y={y} s={s} seed={110 + i} cap={i % 3 === 1 ? ['#5a1a8a', '#b050e0', '#f0b0ff'] : undefined} />)}
      {Array.from({ length: 26 }, (_, i) => { const x = r() * PW, y = 710 + r() * 330; if (x > 1050 && x < 1850 && y > 760 && y < 940) return null; return <Foliage key={i} id={`vmo${i}`} cx={x} cy={y} rx={30 + r() * 46} ry={14 + r() * 16} seed={130 + i} cols={i % 4 === 0 ? PURP : MOSS} n={40} leafLen={12} />; })}
    </g>
  );
};

const ValleFg: React.FC = () => {
  const r = rng(71);
  return (
    <g>
      <Trunk id="vfl" pts={[[-80, 1050, 78], [300, 1004, 70], [640, 960, 54], [900, 996, 36], [1060, 1040, 18]]} cols={['#03050b', '#0f1526', '#35425e']} seed={7} />
      <Trunk id="vfl2" pts={[[420, 1000, 22], [520, 900, 14], [640, 850, 8], [700, 790, 4]]} cols={['#03050b', '#0f1526', '#35425e']} seed={8} />
      {dabs(7, 260, (q) => [q() * 980, 935 + q() * 80, 0.4 + q() * 0.6], MOSS, [10, 30], 0.3, -Math.PI / 2, 0.6)}
      <Mushroom id="fm1" x={250} y={1030} s={210} seed={1} cap={['#12145c', '#3438b0', '#8088e8']} />
      <Mushroom id="fm2" x={90} y={1090} s={150} seed={2} cap={['#12145c', '#3438b0', '#8088e8']} />
      <Mushroom id="fm3" x={560} y={1000} s={100} seed={3} cap={['#12145c', '#3438b0', '#8088e8']} />
      <Mushroom id="fm4" x={690} y={1000} s={64} seed={4} cap={['#12145c', '#3438b0', '#8088e8']} />
      <Mushroom id="fm5" x={800} y={1030} s={46} seed={5} cap={['#12145c', '#3438b0', '#8088e8']} />
      {Array.from({ length: 22 }, (_, i) => { const x = 1000 + r() * 2000, y = 1040 + r() * 110, s2 = 150 + r() * 260, k = r(); return k < 0.5 ? <FernP key={i} x={x} y={y} s={s2} seed={i + 20} cols={i % 2 ? TEAL : ['#051a1e', '#0b3832', '#17603e', '#3f9a4c', '#9ad87a']} n={10} /> : <Spiky key={i} id={`vfs${i}`} x={x} y={y} s={s2 * 0.8} seed={i + 20} cols={i % 3 ? ['#120a30', '#3e2684', '#9a78d8'] : ['#06222a', '#0f6e74', '#6fd8cc']} />; })}
      <FernP x={2700} y={1000} s={360} seed={5} cols={TEAL} n={12} />
      <Spiky id="fsp1" x={2940} y={1010} s={380} seed={7} cols={['#120a30', '#3e2684', '#9a78d8']} />
      {dabs(72, 60, (q) => [2300 + q() * 500, 1000 + q() * 60, 0.6 + q() * 0.4], ['#2a8a7a', '#6fd8c0', '#d8fff0'], [20, 46], 0.3, -Math.PI / 2, 0.3, [0.8, 1])}
      <rect x={0} y={980} width={PW} height={110} fill="#020a10" opacity={0.5} filter="url(#b20)" />
    </g>
  );
};

// ============ MAR DE VEGETACIÓN CON AGUJAS ============
const Clouds: React.FC<{ seed: number; y0: number; y1: number; n: number }> = ({ seed, y0, y1, n }) => {
  const r = rng(seed);
  return <g>{Array.from({ length: n }, (_, i) => { const x = r() * PW, y = lerp(y0, y1, r()), w = 160 + r() * 260; return <g key={i}><ellipse cx={x} cy={y} rx={w} ry={w * 0.16} fill="#ffffff" opacity={0.85} filter="url(#b6)" /><ellipse cx={x - w * 0.2} cy={y - w * 0.1} rx={w * 0.5} ry={w * 0.16} fill="#ffffff" filter="url(#b6)" /><ellipse cx={x + w * 0.1} cy={y + w * 0.08} rx={w * 0.8} ry={w * 0.08} fill="#b8b0f0" opacity={0.6} filter="url(#b6)" /></g>; })}</g>;
};
const SpireSky: React.FC = () => (
  <g>
    <defs><LG id="ss" stops={[[0, '#2a2a98'], [0.4, '#3f7fd0'], [0.75, '#4fd0c8'], [1, '#d8f8e8']]} /><LG id="sf" stops={[[0, '#c890e0'], [1, '#e8c8f0']]} /></defs>
    <rect width={PW} height={700} fill="url(#ss)" />
    <circle cx={2300} cy={260} r={300} fill="#d8c8ff" opacity={0.5} filter="url(#b50)" /><circle cx={2300} cy={260} r={120} fill="#e8dcff" opacity={0.9} />
    <Clouds seed={3} y0={90} y1={420} n={9} />
    <g filter="url(#b2)"><path d={smooth(ridge(41, 600, 120, 130, 0.5), true, 0.5)} fill="url(#sf)" /></g>
    <rect y={588} width={PW} height={60} fill="#5fd8d8" /><rect y={560} width={PW} height={70} fill="#e8fff8" opacity={0.45} filter="url(#b20)" />
  </g>
);
const spire = (cx: number, base: number, w: number, h: number): Pt[] => [[cx - w, base], [cx - w * 0.9, base - h * 0.5], [cx - w * 0.5, base - h * 0.92], [cx, base - h], [cx + w * 0.45, base - h * 0.85], [cx + w * 0.8, base - h * 0.4], [cx + w, base]];
const veg = (seed: number, y0: number, y1: number, n: number, s0: number, s1: number) => {
  const r = rng(seed);
  return Array.from({ length: n }, (_, i) => { const t = r(); return { x: r() * PW, y: lerp(y0, y1, t), s: lerp(s0, s1, t) * (0.8 + r() * 0.5), k: r(), i }; }).sort((a, b) => a.y - b.y);
};
const SpireBack: React.FC = () => {
  const r = rng(44);
  const sp = Array.from({ length: 11 }, (_, i) => { const t = i / 10; return { cx: 1500 + (t - 0.5) * 880 + (r() - 0.5) * 50, h: 130 + 300 * Math.sin(Math.PI * t) * (0.6 + r() * 0.4), w: 62 + r() * 40, i }; }).sort((a, b) => b.h - a.h);
  return (
    <g>
      {sp.map((s) => <RockMass key={s.i} id={`sp${s.i}`} pts={spire(s.cx, 650, s.w, s.h)} cols={['#3a2470', '#8a6cd8', '#d8c4ff']} seed={s.i + 3} moss={['#3a9a44', '#9ae040', '#e8f85a']} mossT={0.05} k={0.3} />)}
      {[[420, 640, 150, 170], [560, 648, 90, 110], [2650, 644, 130, 140]].map(([x, b, w, h], i) => <RockMass key={i} id={`sq${i}`} pts={spire(x, b, w * 0.5, h)} cols={['#4a348a', '#9a80e0', '#e0d0ff']} seed={i + 20} moss={['#3a9a44', '#9ae040', '#e8f85a']} mossT={0.05} k={0.3} />)}
      {veg(45, 630, 790, 150, 60, 120).map((v) => <Foliage key={v.i} id={`sv${v.i}`} cx={v.x} cy={v.y} rx={v.s} ry={v.s * 0.6} seed={v.i + 300} cols={v.k < 0.25 ? TEAL : v.k < 0.4 ? ['#0b3a40', '#2fa648', '#c8e83c', '#f8ff7a'] : GRASS} n={50} leafLen={v.s * 0.2} />)}
    </g>
  );
};
const SpireFront: React.FC = () => (
  <g>
    {veg(46, 800, 1120, 120, 120, 230).map((v) => <Foliage key={v.i} id={`sw${v.i}`} cx={v.x} cy={v.y} rx={v.s} ry={v.s * 0.6} seed={v.i + 600} cols={v.k < 0.25 ? TEAL : v.k < 0.36 ? PURP : v.k < 0.5 ? ['#0b3a40', '#2fa648', '#c8e83c', '#f8ff7a'] : GRASS} n={90} leafLen={v.s * 0.2} />)}
    <rect y={980} width={PW} height={120} fill="#04121c" opacity={0.5} filter="url(#b20)" />
  </g>
);

// ============ MESETAS ============
const mesa = (cx: number, base: number, w: number, h: number, seed: number): Pt[] => {
  const r = rng(seed);
  const tw = w * (0.5 + r() * 0.15);
  return [[cx - w, base], [cx - w * 0.78, base - h * 0.3], [cx - tw * 1.05, base - h * 0.7], [cx - tw, base - h * 0.96], [cx - tw * 0.4, base - h], [cx + tw * 0.5, base - h * 0.98], [cx + tw, base - h * 0.9], [cx + tw * 1.1, base - h * 0.55], [cx + w * 0.85, base - h * 0.2], [cx + w, base]];
};
const MesaSky: React.FC = () => (
  <g>
    <defs><LG id="ms" stops={[[0, '#2438b0'], [0.5, '#5a7ae8'], [0.85, '#a8c4f8'], [1, '#e0e4ff']]} /><LG id="mf" stops={[[0, '#a898e8'], [1, '#d0d4f8']]} /></defs>
    <rect width={PW} height={720} fill="url(#ms)" />
    <circle cx={500} cy={170} r={340} fill="#fff6e0" opacity={0.6} filter="url(#b50)" /><circle cx={500} cy={170} r={60} fill="#fffdf0" filter="url(#b6)" />
    <Clouds seed={8} y0={80} y1={380} n={10} />
    <g filter="url(#b2)">{[300, 800, 1250, 1900, 2350, 2800].map((x, i) => <path key={i} d={smooth(mesa(x, 640, 150 + (i % 3) * 50, 170 + (i % 4) * 60, i + 50), true, 0.45)} fill="url(#mf)" />)}</g>
    <rect y={560} width={PW} height={110} fill="#f0f0ff" opacity={0.5} filter="url(#b20)" />
  </g>
);
const MesaMid: React.FC = () => (
  <g>
    {[[420, 690, 260, 470], [1250, 690, 220, 380], [2050, 690, 250, 520], [2750, 690, 200, 360]].map(([x, b, w, h], i) => (
      <g key={i}>
        <RockMass id={`mm${i}`} pts={mesa(x, b, w, h, i + 7)} cols={['#4a2a6a', '#b07ab8', '#f4c8e0']} seed={i + 30} moss={['#12583c', '#2fa64a', '#7fe850', '#d8f86a']} mossT={0.1} k={0.4} />
        {/* laderas verdes al pie */}
        <Foliage id={`ml${i}`} cx={x} cy={b - 6} rx={w * 1.25} ry={52} seed={i + 70} cols={GRASS} n={260} leafLen={16} />
        <Foliage id={`mk${i}`} cx={x - w * 0.5} cy={b - h * 0.52} rx={w * 0.34} ry={22} seed={i + 80} cols={MOSS} n={50} leafLen={12} />
        <Foliage id={`mj${i}`} cx={x + w * 0.2} cy={b - h * 1.0} rx={w * 0.5} ry={26} seed={i + 90} cols={TEAL} n={70} leafLen={14} />
      </g>
    ))}
  </g>
);
const MesaGround: React.FC = () => {
  const r = rng(52);
  return (
    <g>
      <defs><LG id="mg" stops={[[0, '#e8d8f8'], [0.3, '#c0a8ec'], [1, '#6a56b8']]} /></defs>
      <path d={smooth([[-60, PH + 20], [-60, 690], [500, 676], [1100, 690], [1700, 672], [2300, 688], [PW + 60, 680], [PW + 60, PH + 20]], true, 0.6)} fill="url(#mg)" />
      <ellipse cx={1300} cy={800} rx={800} ry={130} fill="#fff4e8" opacity={0.5} filter="url(#b50)" />
      {dabs(53, 1600, (q) => { const x = q() * PW, y = 690 + Math.pow(q(), 1.2) * 400; return [x, y, 0.85 - (y - 690) / 520 - Math.abs(x - 1300) / 3600]; }, ['#4a3a98', '#7a66c8', '#b09ae8', '#e0d0f8', '#fff4f0'], [20, 90], 0.06, 0, 0.12, [0.3, 0.7])}
      {Array.from({ length: 46 }, (_, i) => { const x = r() * PW, y = 705 + r() * 340; if (x > 1050 && x < 1850 && y > 770 && y < 930) return null; const s = 40 + r() * 90; return <Foliage key={i} id={`mo${i}`} cx={x} cy={y} rx={s} ry={s * 0.3} seed={i + 400} cols={i % 5 === 0 ? TEAL : MOSS} n={70} leafLen={13} />; })}
      {dabs(54, 400, (q) => [q() * PW, 700 + q() * 380, q()], ['#7ff0f0', '#f4f08a', '#ff9ad8', '#ffffff', '#b890ff'], [4, 9], 0.6, 0, 3, [0.6, 1])}
      {[[260, 880, 170], [600, 800, 110], [2100, 890, 180], [2400, 780, 120]].map(([x, y, s], i) => <FernP key={i} x={x} y={y} s={s} seed={i + 9} cols={i % 2 ? TEAL : BUSH.concat(['#9af07a'])} />)}
      {[[450, 860, 110], [2260, 850, 120], [1950, 750, 60]].map(([x, y, s], i) => <Spiky key={i} id={`msp${i}`} x={x} y={y} s={s} seed={i + 4} cols={i % 2 ? ['#0d4c58', '#18b0ac', '#8ffff0'] : ['#2a1260', '#7040d0', '#c8a0ff']} />)}
      {[[160, 770, 190], [2520, 760, 170], [930, 730, 80]].map(([x, y, h], i) => <HorsetailP key={i} x={x} y={y} h={h} seed={i + 30} cols={['#0d4c58', '#149a9c', '#7af0e4']} />)}
      {[[700, 900, 44], [2000, 930, 50], [1000, 745, 24]].map(([x, y, s], i) => <Mushroom key={i} id={`mmu${i}`} x={x} y={y} s={s} seed={i + 5} />)}
    </g>
  );
};
const MesaFg: React.FC = () => (
  <g>
    <RockMass id="mfa" pts={[[-80, 1100], [-80, 120], [120, 60], [330, 200], [420, 520], [360, 800], [520, 1100]]} cols={['#160c2c', '#3c2a5c', '#8a6aa0']} seed={3} moss={MOSS} mossT={0.08} />
    <RockMass id="mfb" pts={[[2560, 1100], [2700, 760], [2640, 420], [2800, 160], [3080, 100], [3080, 1100]]} cols={['#160c2c', '#3c2a5c', '#8a6aa0']} seed={5} moss={MOSS} mossT={0.08} />
    <FernP x={620} y={1130} s={300} seed={5} cols={TEAL} /><FernP x={2420} y={1140} s={320} seed={6} cols={BUSH.concat(['#9af07a'])} />
    <Mushroom id="mfm" x={900} y={1080} s={110} seed={2} />
  </g>
);

// ============ BAJO EL AGUA ============
const WaterBg: React.FC = () => {
  const r = rng(61);
  return (
    <g>
      <defs><LG id="wb" stops={[[0, '#9ff4ec'], [0.25, '#3fb8d8'], [0.6, '#2a5fb8'], [1, '#20146a']]} /><LG id="wr" stops={[[0, '#ffffff', 0.5], [1, '#ffffff', 0]]} /></defs>
      <rect width={PW} height={PH} fill="url(#wb)" />
      {Array.from({ length: 12 }, (_, i) => { const x = r() * PW; return <path key={i} d={`M${x} -20L${x + 90 + r() * 120} -20L${x + 500 + r() * 300} ${PH}L${x + 250} ${PH}Z`} fill="url(#wr)" opacity={0.35} filter="url(#b20)" />; })}
      <g filter="url(#b6)" opacity={0.6}>
        {[[300, 900, 340, 420], [1000, 960, 260, 300], [1900, 930, 380, 460], [2700, 950, 300, 380]].map(([x, b, w, h], i) => <path key={i} d={smooth(mesa(x, b + 200, w, h, i + 3), true, 0.6)} fill="#2a3f9a" />)}
        {Array.from({ length: 14 }, (_, i) => <FernP key={i} x={r() * PW} y={760 + r() * 200} s={120 + r() * 120} seed={i + 2} cols={['#2a3f9a', '#3a58b8', '#4a78c8']} n={6} />)}
      </g>
    </g>
  );
};
const WaterFg: React.FC = () => {
  const r = rng(62);
  return (
    <g>
      <RockMass id="wf1" pts={[[-80, 1100], [-80, 820], [300, 760], [760, 860], [1300, 940], [1900, 900], [2400, 800], [3080, 760], [3080, 1100]]} cols={['#141048', '#3a3a98', '#8f9ae8']} seed={9} moss={['#126a5a', '#2fb89a', '#9af0b0', '#f0ff9a']} mossT={0.3} k={0.6} />
      {/* lirios de mar: tallo con corona de plumas */}
      {[[380, 800, 420], [700, 870, 300], [2300, 820, 460], [2700, 790, 340], [1750, 910, 240]].map(([x, y, h], i) => (
        <g key={i}>
          <path d={`M${x} ${y}Q${x + 60} ${y - h * 0.5} ${x + 20} ${y - h}`} stroke="#5a2a5a" strokeWidth={10} fill="none" strokeLinecap="round" />
          <g transform={`rotate(180 ${x + 20} ${y - h})`}><FernP x={x + 20} y={y - h} s={h * 0.36} seed={i + 40} cols={['#6a1a4a', '#c03a7a', '#ff7ab0', '#ffd0e0']} n={10} /></g>
        </g>
      ))}
      {Array.from({ length: 18 }, (_, i) => { const x = r() * PW, y = 840 + r() * 180, s = 50 + r() * 90; return i % 3 === 0 ? <Spiky key={i} id={`wsp${i}`} x={x} y={y} s={s} seed={i} cols={['#0d4c58', '#18b0ac', '#8ffff0']} /> : <Foliage key={i} id={`wfo${i}`} cx={x} cy={y} rx={s} ry={s * 0.6} seed={i + 700} cols={i % 3 === 1 ? ['#5a3a10', '#c88a20', '#ffd84a', '#fff8a0'] : ['#3a1a6a', '#8a4ad8', '#d09aff', '#f4dcff']} n={70} leafLen={s * 0.22} />; })}
      <rect y={900} width={PW} height={200} fill="#0c0838" opacity={0.5} filter="url(#b20)" />
    </g>
  );
};

export type LayerDef = { name: string; el: React.ReactNode; rough?: boolean; k: number };
export const LAYERS: LayerDef[] = [
  { name: 'valle-0', el: <ValleSky />, k: 0.03 },
  { name: 'valle-1', el: <ValleFar />, rough: true, k: 0.1 },
  { name: 'valle-2', el: <ValleMid />, rough: true, k: 0.38 },
  { name: 'valle-3', el: <ValleNear />, rough: true, k: 1 },
  { name: 'valle-4', el: <ValleFg />, rough: true, k: 1.7 },
  { name: 'agujas-0', el: <SpireSky />, k: 0.04 },
  { name: 'agujas-1', el: <SpireBack />, rough: true, k: 0.4 },
  { name: 'agujas-2', el: <SpireFront />, rough: true, k: 1.1 },
  { name: 'mesetas-0', el: <MesaSky />, k: 0.05 },
  { name: 'mesetas-1', el: <MesaMid />, rough: true, k: 0.35 },
  { name: 'mesetas-2', el: <MesaGround />, rough: true, k: 1 },
  { name: 'mesetas-3', el: <MesaFg />, rough: true, k: 1.7 },
  { name: 'agua-0', el: <WaterBg />, k: 0.15 },
  { name: 'agua-1', el: <WaterFg />, rough: true, k: 1.2 },
];

/** composición que pinta una capa por cuadro (se guarda como PNG con transparencia) */
export const LayerSheet: React.FC<{ i: number }> = ({ i }) => {
  const L = LAYERS[i];
  return (
    <svg viewBox={`0 0 ${PW} ${PH}`} width={PW} height={PH}>
      <PaintDefs />
      <g filter={L.rough ? 'url(#rough)' : undefined}>{L.el}</g>
    </svg>
  );
};

/** todas las capas de un bioma apiladas (vista previa) */
export const BiomePreview: React.FC<{ name: string }> = ({ name }) => (
  <svg viewBox={`0 0 ${PW} ${PH}`} width={PW} height={PH}>
    <PaintDefs />
    {LAYERS.filter((l) => l.name.startsWith(name)).map((L) => <g key={L.name} filter={L.rough ? 'url(#rough)' : undefined}>{L.el}</g>)}
  </svg>
);
