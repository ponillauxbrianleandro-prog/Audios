import React from 'react';
import { FPS, H, INK, Pt, W, clamp, eio, ein, eout, leaf, lerp, seg } from './lib';
import { BigLeaf, Calamite, DAY, DRY, DUSK, Fern, Glosso, Pal, Reeds, VIOLET } from './art';
import { Air, DryPlain, Riverbank, SpireVista } from './env';
import { Beast, BeastProps, Kind, anchors, cycleLen } from './beast';
import { Burst, Cam, Flash, Label, Sil, SilKind, Speed } from './fx';
import { Card, Dig, JawEar, Pangea, Ruler, TitleCard, TreeDiagram } from './maps';

export type CutFn = (t: number, f: number, d: number) => React.ReactNode;
export type Beat = { txt: string; dur?: number; edit?: boolean; cuts: [number, CutFn][] };

type KFn = (t: number, f: number, px: number) => React.ReactNode;
type SO = {
  env?: 'r' | 'd' | 'v'; pal?: Pal; seed?: number; px?: [number, number]; z?: [number, number]; c?: Pt | [Pt, Pt];
  moon?: boolean; k?: KFn; over?: KFn; shake?: number; rot?: [number, number]; fg?: boolean; speed?: number;
  air?: { dust?: number; leaves?: number; wind?: number; bugs?: number }; ez?: (t: number) => number; dark?: number; tint?: [string, number];
};

/** generic environment shot */
const S = (o: SO): CutFn => (t, f) => {
  const e = (o.ez ?? eio)(t);
  const px = o.px ? lerp(o.px[0], o.px[1], e) : 0;
  const z = o.z ? lerp(o.z[0], o.z[1], e) : 1;
  const c0 = o.c ? (Array.isArray(o.c[0]) ? (o.c as [Pt, Pt])[0] : (o.c as Pt)) : ([W / 2, H / 2] as Pt);
  const c1 = o.c ? (Array.isArray(o.c[0]) ? (o.c as [Pt, Pt])[1] : (o.c as Pt)) : ([W / 2, H / 2] as Pt);
  const E = o.env === 'd' ? DryPlain : o.env === 'v' ? SpireVista : Riverbank;
  const pal = o.pal ?? (o.env === 'd' ? DRY : DAY);
  return (
    <g>
      <Cam zoom={z} cx={lerp(c0[0], c1[0], e)} cy={lerp(c0[1], c1[1], e)} rot={o.rot ? lerp(o.rot[0], o.rot[1], e) : 0} shake={o.shake} f={f}>
        <E f={f} px={px} pal={pal} seed={o.seed ?? 1} moon={o.moon} fg={o.fg}>{o.k?.(t, f, px)}</E>
        <Air f={f} pal={pal} {...(o.air ?? {})} />
      </Cam>
      {o.tint && <rect width={W} height={H} fill={o.tint[0]} opacity={o.tint[1]} />}
      {o.speed ? <Speed f={f} a={o.speed} /> : null}
      {o.dark ? <rect width={W} height={H} fill="#05030a" opacity={o.dark} /> : null}
      {o.over?.(t, f, px)}
    </g>
  );
};

/** walking helper: distance and phase after f frames at v px/s */
const wk = (f: number, v: number, kind: Kind = 'procy', s = 1, run = false) => ({ dx: (v * f) / FPS, phase: (Math.abs(v) * f) / FPS / cycleLen(kind, s, run) });
const B = (p: BeastProps) => <Beast {...p} />;
const blinkAt = (f: number, at = 20) => clamp(1 - Math.abs(f - at) / 3);

type AKey = 'eye' | 'fang' | 'mouth' | 'head' | 'tail' | 'hinge';
/** primer plano centrado en un punto del animal (ojo, colmillo, boca, cabeza, cola) */
const face = (key: AKey, s0: number, s1: number, bg: [string, string], extra?: Partial<BeastProps> | ((t: number, f: number) => Partial<BeastProps>), ez: (t: number) => number = eout, at: Pt = [960, 540]): CutFn => (t, f) => {
  const s = lerp(s0, s1, ez(t));
  const ex = typeof extra === 'function' ? extra(t, f) : extra ?? {};
  const pr: BeastProps = { x: 0, y: 0, yaw: 46, f, shadow: false, drift: 0, blink: blinkAt(f, 9), ...ex };
  const a = anchors({ ...pr, f: 0, phase: undefined })[key];
  return (
    <g>
      <rect width={W} height={H} fill={bg[0]} />
      <circle cx={960} cy={540} r={700} fill={bg[1]} />
      <circle cx={700} cy={300} r={420} fill="#ffffff" opacity={0.12} />
      <Beast {...pr} x={at[0] - a[0] * s} y={at[1] - a[1] * s} s={s} />
    </g>
  );
};
const eyeShot = (s0: number, s1: number, bg: [string, string], extra?: Partial<BeastProps>, ez = eout): CutFn => face('eye', s0, s1, bg, extra, ez);

const silCard = (kind: SilKind, bg: string, bg2: string, s: number, y: number, col = INK, cross = false): CutFn => (t, f) => (
  <Card bg={bg} bg2={bg2} t={t}>
    <Sil kind={kind} x={960} y={y} s={s * (1 + t * 0.06)} col={col} f={f} />
    {cross && <g opacity={seg(t, 0.35, 0.5)}><path d="M620 250L1300 850M1300 250L620 850" stroke="#ff3050" strokeWidth={46} strokeLinecap="round" /></g>}
  </Card>
);

const mapShot = (p: (t: number, f: number) => Omit<React.ComponentProps<typeof Pangea>, 'f'>, z: [number, number] = [1, 1], c: [Pt, Pt] = [[960, 540], [960, 540]], shake?: (t: number) => number): CutFn => (t, f) => {
  const e = eio(t);
  return <Cam zoom={lerp(z[0], z[1], e)} cx={lerp(c[0][0], c[1][0], e)} cy={lerp(c[0][1], c[1][1], e)} shake={shake?.(t)} f={f}><Pangea {...p(t, f)} f={f} /></Cam>;
};

const tree = (stage: number, z: [number, number] = [1, 1], c: [Pt, Pt] = [[960, 540], [960, 540]]): CutFn => (t, f) => {
  const e = eio(t);
  return <Cam zoom={lerp(z[0], z[1], e)} cx={lerp(c[0][0], c[1][0], e)} cy={lerp(c[0][1], c[1][1], e)}><TreeDiagram f={f} t={t} stage={stage} /></Cam>;
};

const teeth = (key: AKey, sc: number, bg: [string, string], yaw = 40): CutFn => face(key, sc, sc * 1.08, bg, (t) => ({ yaw, jaw: lerp(8, 30, eout(seg(t, 0, 0.35))), blink: 0 }), (x) => x, [1000, 600]);

// ---------- chase shots (dusk) ----------
const chase = (kind: 'prey' | 'legs' | 'eye' | 'jaws' | 'wide' | 'river' | 'leap' | 'splash'): CutFn => (t, f, d) => {
  const v = 1500;
  if (kind === 'eye') return eyeShot(6, 7.2, ['#1a1030', '#4a2050'], { look: -1.5, yaw: 58 }, (x) => x)(t, f, d);
  if (kind === 'splash') return (
    <g>
      <rect width={W} height={H} fill="#2a3f88" />
      <rect y={lerp(700, 200, eout(t))} width={W} height={H} fill="#3f6fc8" />
      {Array.from({ length: 34 }, (_, i) => { const a = -Math.PI * (0.1 + (0.8 * i) / 33), r = (300 + (i % 5) * 160) * eout(t); return <circle key={i} cx={960 + Math.cos(a) * r} cy={700 + Math.sin(a) * r + t * t * 500} r={14 + (i % 4) * 9} fill="#dfe9ff" />; })}
      <Burst x={960} y={700} t={t * 0.9 + 0.05} col="#dfe9ff" />
      <Flash a={1 - seg(t, 0, 0.3)} />
    </g>
  );
  const w = wk(f, v, 'procy', 1, true);
  const base = 900;
  const px = base + w.dx;
  const shots: Record<string, React.ReactNode> = {
    prey: <Cam zoom={1.5} cx={1050} cy={760} shake={10} f={f}><Riverbank f={f} px={px} pal={DUSK} seed={2}>{B({ drift: 0, yaw: 26, x: px + 1000, y: 880, s: 1.15, phase: w.phase, run: true, f, look: -1 })}</Riverbank></Cam>,
    legs: <Cam zoom={1.9} cx={900} cy={840} shake={22} f={f}><Riverbank f={f} px={px} pal={DUSK} seed={2} fg={false}>{B({ drift: 0, yaw: 26, kind: 'gorgon', x: px + 760, y: 930, s: 1.5, phase: (f / FPS) * 2.6, run: true, f, jaw: 14 })}</Riverbank></Cam>,
    jaws: <Cam zoom={2.3} cx={1250} cy={560} shake={26} f={f}><Riverbank f={f} px={px} pal={DUSK} seed={2} fg={false}>{B({ drift: 0, yaw: 26, kind: 'gorgon', x: px + 760, y: 930, s: 1.5, phase: (f / FPS) * 2.6, run: true, f, jaw: 26 + Math.sin(f) * 6 })}</Riverbank></Cam>,
    wide: <Cam zoom={1.05} cx={960} cy={600} shake={8} f={f}><Riverbank f={f} px={px} pal={DUSK} seed={2}>{B({ drift: 0, yaw: 26, kind: 'gorgon', x: px + lerp(260, 520, t), y: 900, s: 1.05, phase: (f / FPS) * 2.6, run: true, f, jaw: 20 })}{B({ drift: 0, yaw: 26, x: px + 1350, y: 900, s: 1, phase: w.phase, run: true, f })}</Riverbank></Cam>,
    river: <Cam zoom={lerp(1.2, 2.2, ein(t))} cx={1100} cy={620} shake={14} f={f}><Riverbank f={f} px={px * 0.3} pal={DUSK} seed={5} fg={false} /></Cam>,
    leap: <Cam zoom={1.6} cx={1000} cy={640} shake={12} f={f}><Riverbank f={f} px={px} pal={DUSK} seed={2} fg={false}>{B({ drift: 0, yaw: 26, x: px + 900 + t * 260, y: 880 - Math.sin(Math.PI * t * 0.9) * 260, s: 1.1, phase: 0.7, run: true, f, head: -18 + t * 50 })}</Riverbank></Cam>,
  };
  return <g>{shots[kind]}<Speed f={f} a={kind === 'river' ? 0.25 : 0.45} col="#ffd0c0" /></g>;
};

const BG = { warm: ['#ffe6b0', '#ffcf70'] as [string, string], cool: ['#bfeee0', '#8fe0c8'] as [string, string], night: ['#1a1030', '#3a2460'] as [string, string] };

export const BEATS: Beat[] = [
  // ===================== PARTE 0 · GANCHO =====================
  { txt: '255 millones de años. Ni uno menos.', dur: 2.7, edit: true, cuts: [
    [1.0, eyeShot(11, 3.2, BG.warm)],
    [0.8, S({ env: 'v', px: [0, 260], z: [1.5, 1.05], c: [1050, 520], ez: eout })],
    [0.9, S({ pal: VIOLET, seed: 4, moon: true, px: [700, 820], z: [1, 1.25], c: [1000, 700], k: (t, f, px) => B({ yaw: 50, x: 1500 + wk(f, 190).dx, y: 880, s: 1.2, phase: wk(f, 190, 'procy', 1.2).phase, f }) })],
  ] },
  { txt: 'Sesenta centímetros. Casi la mitad, cola.', dur: 2.7, edit: true, cuts: [
    [1.2, (t, f) => <g><rect width={W} height={H} fill="#bfeee0" /><rect y={720} width={W} height={400} fill="#8fd8b8" /><Beast x={1010} y={720} s={2} f={f} phase={f / 30} /><Ruler x0={330} x1={1640} y={800} t={seg(t, 0, 0.6)} text="60 cm" /></g>],
    [0.6, face('tail', 2.6, 3, BG.warm, (t, f) => ({ yaw: -38, f: f * 4, tailAmp: 2.2 }), (x) => x)],
    [0.9, S({ seed: 3, px: [500, 560], z: [1.9, 1.7], c: [1000, 800], air: { bugs: 2 }, k: (t, f) => <g><BigLeaf x={1250} y={905} len={330} rot={-14} pal={DAY} />{B({ yaw: 30, x: 1500 + wk(f, 160).dx, y: 890, s: 0.9, phase: wk(f, 160, 'procy', 0.9).phase, f })}</g> })],
  ] },
  { txt: '9.413 kilómetros entre los dos lugares donde dejó sus huesos.', dur: 3.2, edit: true, cuts: [
    [0.8, mapShot(() => ({ sites: ['karoo'] }), [3.4, 2.6], [[925, 815], [925, 800]])],
    [1.4, mapShot((t) => ({ sites: ['karoo', 'korbach'], arc: eout(seg(t, 0, 0.8)) }), [2.4, 2.0], [[940, 790], [1010, 420]])],
    [1.0, mapShot((t) => ({ sites: ['karoo', 'korbach'], arc: 1, label: '9.413 km' }), [1.25, 1.4], [[980, 600], [990, 600]])],
  ] },
  { txt: 'Y ni un océano en el medio: Sudamérica y África eran una sola tierra.', dur: 3.5, edit: true, cuts: [
    [1.4, mapShot((t) => ({ gap: 230 * (1 - ein(seg(t, 0.1, 0.62))), hi: t > 0.62 ? ['sa', 'af'] : [], names: true }), [1.5, 1.7], [[800, 660], [820, 660]], (t) => (t > 0.62 ? 40 * (1 - seg(t, 0.62, 1)) : 0))],
    [0.9, mapShot(() => ({ hi: ['sa', 'af'], belt: 1, sites: ['karoo'] }), [2.6, 3.1], [[830, 830], [830, 835]])],
    [1.2, S({ env: 'd', seed: 2, px: [200, 700], z: [1.1, 1.1], speed: 0.25, k: (t, f, px) => B({ yaw: 44, x: px + 900, y: 880, s: 1.25, run: true, phase: wk(f, 900, 'procy', 1.25, true).phase, f }) })],
  ] },
  { txt: '2007. Tanzania. Un pedazo de cráneo y dos mandíbulas.', dur: 3.0, edit: true, cuts: [
    [0.9, S({ env: 'd', seed: 6, px: [900, 1000], z: [1, 1.2], over: () => <Label x={110} y={130} text="2007 · TANZANIA" size={34} bg /> })],
    [1.1, (t, f) => <Cam zoom={lerp(1, 1.25, t)} cx={940} cy={600}><Dig f={f} t={t} /></Cam>],
    [1.0, (t, f) => <g>{teeth('mouth', 3.6, BG.warm, 34)(t, f, 1)}<Flash a={1 - seg(t, 0, 0.35)} col="#efe2c0" /></g>],
  ] },
  { txt: 'Este animal había estado en todas partes.', dur: 2.3, edit: true, cuts: [
    [1, S({ seed: 5, px: [300, 380], z: [1.3, 1.3], c: [1000, 760], k: (t, f, px) => B({ yaw: -32, x: px + 900 + wk(f, 300).dx, y: 880, s: 1.2, phase: wk(f, 300, 'procy', 1.2).phase, f }) })],
    [1, S({ env: 'd', seed: 3, px: [600, 680], z: [1.3, 1.3], c: [1000, 760], k: (t, f, px) => B({ yaw: 58, x: px + 1000 - wk(f, 300).dx, y: 880, s: 1.2, flip: true, phase: wk(f, 300, 'procy', 1.2).phase, f }) })],
    [1, S({ pal: VIOLET, seed: 7, moon: true, px: [900, 980], z: [1.3, 1.3], c: [1000, 760], k: (t, f, px) => B({ yaw: 34, x: px + 900 + wk(f, 300).dx, y: 880, s: 1.2, phase: wk(f, 300, 'procy', 1.2).phase, f }) })],
    [1, S({ pal: DUSK, seed: 2, px: [300, 380], z: [1.3, 1.3], c: [1000, 760], k: (t, f, px) => B({ yaw: 48, x: px + 1000 - wk(f, 300).dx, y: 880, s: 1.2, flip: true, phase: wk(f, 300, 'procy', 1.2).phase, f }) })],
  ] },
  { txt: 'Un animal chiquito, en un mundo gigante.', dur: 2.8, edit: true, cuts: [
    [1.3, S({ pal: DUSK, seed: 3, px: [400, 430], z: [1.25, 1.35], c: [960, 700], shake: 0, k: (t, f, px) => <g>{B({ yaw: -36, kind: 'gorgon', x: px + 520 + wk(f, 260, 'gorgon', 1.5).dx, y: 960, s: 1.5, phase: wk(f, 260, 'gorgon', 1.5).phase, f })}{B({ yaw: 40, x: px + 1380, y: 890, s: 0.75, crouch: 0.7, flip: true, f, head: -14 })}</g> })],
    [1.5, S({ env: 'd', seed: 2, px: [300, 300], z: [2.4, 1], c: [[1000, 860], [960, 540]], ez: eout, fg: false, k: (t, f, px) => B({ x: px + 1000, y: 880, s: 0.5, yaw: 40, f, turn: 20 }) })],
  ] },
  { txt: '', dur: 1.7, edit: true, cuts: [[1, (t, f) => <TitleCard f={f} t={t} />]] },

  // ===================== PARTE 1 · EL NOMBRE =====================
  { txt: 'Se llama Procynosuchus delaharpeae.', cuts: [
    [1.3, S({ seed: 1, px: [150, 330], z: [1.15, 1.3], c: [1000, 720], air: { bugs: 2 }, k: (t, f) => B({ yaw: 28, x: 900 + wk(f, 170).dx, y: 880, s: 1.3, phase: wk(f, 170, 'procy', 1.3).phase, f }) })],
    [1, eyeShot(3.4, 4, BG.cool, { head: -6 }, eio)],
  ] },
  { txt: 'Procynosuchus. «Antes del cocodrilo-perro».', cuts: [
    [1, silCard('croc', '#bfe8a0', '#8fd070', 2.1, 620)],
    [1, silCard('dog', '#ffd9a0', '#ffb860', 2.3, 800)],
    [1.2, S({ seed: 6, px: [500, 540], z: [1.7, 1.9], c: [1050, 760], k: (t, f, px) => B({ yaw: 36, x: px + 900, y: 880, s: 1.3, f, head: -10 + Math.sin(f / 6) * 6, blink: blinkAt(f, 14) }) })],
  ] },
  { txt: 'Un nombre raro para un animal que no era ni cocodrilo ni perro.', cuts: [
    [1, silCard('croc', '#bfe8a0', '#8fd070', 2.1, 620, INK, true)],
    [1, silCard('dog', '#ffd9a0', '#ffb860', 2.3, 800, INK, true)],
    [1.6, S({ env: 'd', seed: 4, px: [300, 520], z: [1.2, 1.2], c: [1000, 740], k: (t, f, px) => B({ yaw: 50, x: px + 880, y: 880, s: 1.3, phase: wk(f, 230, 'procy', 1.3).phase, f }) })],
  ] },
  { txt: 'Era un cinodonto. Uno de los primeros.', cuts: [
    [1, S({ pal: VIOLET, seed: 9, moon: true, px: [500, 560], z: [1.5, 1.25], c: [1020, 720], ez: eout, k: (t, f, px) => B({ yaw: 30, x: px + 940, y: 880, s: 1.4, f, head: -12, jaw: 6 }) })],
    [1, eyeShot(2.2, 2.6, BG.night, { head: -8, jaw: 14 }, eio)],
  ] },
  { txt: 'Y para entender por qué eso importa, hay que entender en qué rama del árbol de la vida estaba parado.', cuts: [
    [1, S({ seed: 8, px: [200, 600], z: [1.1, 1.1], k: (t, f, px) => B({ yaw: 44, x: px + 850, y: 885, s: 1.15, phase: wk(f, 240, 'procy', 1.15).phase, f, head: 14 + Math.sin(f / 4) * 4 }) })],
    [0.9, S({ seed: 8, px: [900, 900], z: [1.3, 1.9], c: [[960, 600], [1000, 260]], fg: false })],
    [0.9, tree(0, [1.6, 1], [[960, 860], [960, 540]])],
  ] },
  { txt: 'Hace más de 300 millones de años, los animales con cuatro patas que ponían huevos en tierra firme se dividieron en dos grandes familias.', cuts: [
    [1.1, S({ env: 'd', seed: 8, px: [400, 520], z: [1.5, 1.35], c: [1000, 800], k: (t, f, px) => <g>{[0, 1, 2, 3].map((i) => <ellipse key={i} cx={px + 1180 + i * 46 - (i % 2) * 10} cy={892 - (i % 2) * 14} rx={24} ry={30} fill="#fbf4e0" stroke={INK} strokeWidth={5} />)}<Sil kind="lizard" x={px + 800 + wk(f, 80).dx} y={900} s={0.9} col="#3a5a3c" f={f} /></g> })],
    [0.8, (t, f) => <g><rect width={W} height={H} fill="#ffe6b0" /><rect y={780} width={W} height={300} fill="#f0c070" />{[0, 1, 2].map((i) => <g key={i} transform={`translate(${700 + i * 260} ${760}) rotate(${Math.sin(f / 3 + i) * (t > 0.4 ? 7 : 2)})`}><ellipse rx={90} ry={116} fill="#fbf4e0" stroke={INK} strokeWidth={8} />{t > 0.5 && <path d="M-60 -20l30 30l26 -34l30 36l34 -30" stroke={INK} strokeWidth={7} fill="none" />}</g>)}</g>],
    [1.1, tree(0, [1.5, 1.25], [[960, 780], [960, 660]])],
  ] },
  { txt: 'Una terminaría dando reptiles, dinosaurios y aves.', cuts: [[1, tree(1, [1.25, 1.35], [[640, 460], [600, 430]])]] },
  { txt: 'La otra, los sinápsidos, terminaría dando algo que todavía no existía:', cuts: [[1, tree(2, [1.5, 1.7], [[1300, 520], [1420, 380]])]] },
  { txt: 'mamíferos.', dur: 1.3, cuts: [[1, (t, f) => <g>{tree(3, [2.4, 2.0], [[1640, 180], [1640, 180]])(t, f, 1)}<Burst x={1100} y={500} t={t} col="#ffb060" /><Flash a={0.8 * (1 - seg(t, 0, 0.25))} col="#ffb060" /></g>]] },
  { txt: 'Perros. Ballenas. Murciélagos. Caballos.', dur: 2.6, edit: true, cuts: [
    [1, silCard('dog', '#ffd9a0', '#ffb860', 2.3, 800)],
    [1, silCard('whale', '#a8e0ff', '#60b8f0', 1.5, 560)],
    [1, silCard('bat', '#d8c0ff', '#a888f0', 1.9, 560)],
    [1, silCard('horse', '#c8f0a0', '#90d868', 1.5, 830)],
  ] },
  { txt: 'Vos.', dur: 1.5, cuts: [[1, (t, f) => <g>{silCard('human', '#ffc0b0', '#ff8f80', 1.15, 880)(t, f, 1)}<Flash a={0.6 * (1 - seg(t, 0, 0.2))} /></g>]] },
  { txt: 'Dentro de esa rama aparecieron los terápsidos. Y dentro de los terápsidos, un grupo chico, discreto, casi invisible al lado de los gigantes de su época: los cinodontos.', cuts: [
    [1, tree(4, [1.55, 1.7], [[1420, 330], [1440, 310]])],
    [1.2, S({ env: 'd', seed: 5, px: [300, 480], z: [1.05, 1.05], k: (t, f, px) => <g>{B({ yaw: -32, kind: 'pareia', x: 900 + wk(f, 70, 'pareia').dx, y: 860, s: 1.25, phase: wk(f, 70, 'pareia', 1.25).phase, f })}{B({ yaw: 58, kind: 'dicyn', x: 1750 + wk(f, 90, 'dicyn').dx, y: 900, s: 1.3, phase: wk(f, 90, 'dicyn', 1.3).phase, f })}{B({ yaw: 34, x: 1280 + wk(f, 260).dx, y: 940, s: 0.6, phase: wk(f, 260, 'procy', 0.6).phase, f })}</g> })],
    [0.9, S({ seed: 4, px: [700, 720], z: [2.0, 2.3], c: [1000, 820], k: (t, f, px) => <g>{B({ yaw: 48, x: px + 840 + eout(seg(t, 0.1, 0.5)) * 110, y: 880, s: 1.1, f, crouch: 0.5, head: -8, blink: blinkAt(f, 34) })}<Fern x={px + 800} y={930} s={150} seed={7} pal={DAY} /></g> })],
    [0.9, tree(4, [2.6, 3], [[1470, 260], [1490, 250]])],
  ] },
  { txt: 'Procynosuchus no era un mamífero.', cuts: [[1, eyeShot(2.8, 3.1, BG.cool, { head: 4 }, eio)]] },
  { txt: 'Y nadie demostró que fuera nuestro antepasado directo.', cuts: [[1, tree(5, [2.0, 2.3], [[1420, 200], [1380, 170]])]] },
  { txt: 'Era algo más interesante que eso:', cuts: [[1, S({ pal: VIOLET, seed: 3, moon: true, px: [300, 480], z: [1.2, 1.2], c: [1000, 700], k: (t, f, px) => B({ yaw: -36, x: px + 900, y: 880, s: 1.3, phase: wk(f, 200, 'procy', 1.3).phase, f }) })]] },
  { txt: 'un primo antiquísimo, de la misma familia, en el momento justo en que esa familia empezaba a cambiar.', cuts: [
    [1, S({ pal: VIOLET, seed: 3, moon: true, px: [480, 640], z: [1.6, 1.6], c: [1050, 760], k: (t, f, px) => B({ yaw: 40, x: px + 900, y: 880, s: 1.3, phase: wk(f, 180, 'procy', 1.3).phase, f }) })],
    [0.8, S({ env: 'v', seed: 3, px: [100, 300], z: [1.2, 1.2] })],
    [1, eyeShot(4.5, 6.5, BG.night, { look: 1 }, eio)],
  ] },
  { txt: 'Tenía colmillos. Incisivos. Muelas con varias puntas.', dur: 3.0, edit: true, cuts: [
    [1, teeth('fang', 7, BG.warm, 36)], [1, teeth('mouth', 8, BG.cool, 62)], [1, teeth('hinge' as AKey, 6, ['#ffd0d8', '#ff9fb0'], 28)],
  ] },
  { txt: 'Una mandíbula hecha todavía de varios huesos.', cuts: [[1, (t, f) => <Cam zoom={lerp(1.7, 1.4, eout(t))} cx={560} cy={600}><JawEar f={f} t={t * 0.3} travel={false} /></Cam>]] },
  { txt: 'Y dentro de esa mandíbula, escondidos, unos huesitos que, millones de años después, en otra rama del mismo árbol, iban a terminar adentro de tu oído.', cuts: [
    [1, (t, f) => <Cam zoom={lerp(2.3, 1.5, eio(t))} cx={lerp(520, 640, t)} cy={600}><JawEar f={f} t={0.3} travel={false} /></Cam>],
    [1.5, (t, f) => <Cam zoom={lerp(1.15, 1, t)} shake={t > 0.78 ? 30 * (1 - seg(t, 0.78, 1)) : 0} f={f}><JawEar f={f} t={0.3 + t * 0.7} /></Cam>],
    [0.7, (t, f) => <g><Cam zoom={lerp(2.2, 2.6, t)} cx={1480} cy={520}><JawEar f={f} t={1} /></Cam><Flash a={0.9 * (1 - seg(t, 0, 0.3))} col="#ffe9a8" /></g>],
  ] },
  { txt: 'Pero no nos adelantemos.', cuts: [[1, S({ seed: 2, px: [600, 700], z: [1.4, 1.4], c: [1000, 760], k: (t, f, px) => B({ yaw: 54, x: px + 900, y: 880, s: 1.3, f, head: Math.sin(f / 2.2) * 12 * (1 - t), blink: blinkAt(f, 10) }) })]] },
  { txt: 'Primero, veamos dónde vivía.', cuts: [[1, S({ env: 'v', seed: 1, px: [500, 200], z: [1.7, 1], c: [[1050, 560], [960, 540]], ez: eout })]] },
  { txt: 'Porque su mundo no perdonaba.', cuts: [
    [1, S({ pal: DUSK, seed: 6, px: [300, 360], z: [1.1, 1.3], c: [1000, 640], dark: 0.15, k: (t, f, px) => B({ yaw: 28, kind: 'gorgon', x: px + 700 + wk(f, 150, 'gorgon').dx, y: 900, s: 1.2, phase: wk(f, 150, 'gorgon', 1.2).phase, f, sil: '#07050c', eyeGlow: true }) })],
  ] },

  // ===================== PARTE 2 · EL MUNDO Y EL PELIGRO =====================
  { txt: 'Pérmico tardío.', dur: 1.6, cuts: [[1, (t, f) => <g>{S({ env: 'v', seed: 4, px: [0, 120], z: [1.25, 1.1], ez: eout })(t, f, 1)}<Flash a={0.7 * (1 - seg(t, 0, 0.2))} /></g>]] },
  { txt: 'No hay pasto. No hay flores. No hay un solo dinosaurio.', dur: 3.3, edit: true, cuts: [
    [1, S({ seed: 7, px: [300, 340], z: [2.4, 2.6], c: [900, 930], fg: false })],
    [1, S({ seed: 9, px: [800, 840], z: [2.2, 2.4], c: [1000, 520], fg: false })],
    [1.2, S({ env: 'd', seed: 7, px: [200, 300], z: [1, 1.1], k: (t, f, px) => B({ yaw: 36, kind: 'dicyn', x: px + 1100, y: 880, s: 0.9, phase: wk(f, 80, 'dicyn', 0.9).phase, f }) })],
  ] },
  { txt: 'Todo lo que hoy son continentes está pegado en uno solo: Pangea.', cuts: [[1, mapShot(() => ({ names: false }), [2.2, 1], [[960, 620], [960, 540]])]] },
  { txt: 'Al sur, Gondwana: Sudamérica, África, la Antártida, la India y Australia, unidas como piezas que todavía no se separaron.', cuts: [
    [1, mapShot((t) => ({ names: true, hi: [['sa'], ['sa', 'af'], ['sa', 'af', 'an'], ['sa', 'af', 'an', 'ind'], ['sa', 'af', 'an', 'ind', 'au']][Math.min(4, Math.floor(t * 5.5))] }), [1.35, 1.5], [[980, 700], [1000, 720]])],
    [0.5, mapShot(() => ({ names: true, hi: ['sa', 'af', 'an', 'ind', 'au'] }), [1.5, 1.2], [[1000, 720], [960, 620]])],
  ] },
  { txt: 'En lo que hoy es Sudáfrica, la cuenca del Karoo es una llanura enorme cruzada por ríos lentos que se doblan sobre sí mismos.', cuts: [
    [0.8, mapShot(() => ({ sites: ['karoo'] }), [1.6, 4], [[960, 700], [925, 815]])],
    [1, S({ env: 'd', seed: 9, px: [0, 500], z: [1, 1] })],
    [1.1, S({ seed: 5, px: [1200, 600], z: [1.5, 1.5], c: [960, 600], fg: false })],
  ] },
  { txt: 'En sus orillas, bosques de Glossopteris, árboles de hojas con forma de lengua.', cuts: [
    [1, S({ seed: 3, px: [300, 420], z: [1.5, 1.5], c: [[960, 760], [960, 330]], fg: false })],
    [1, (t, f) => <g><rect width={W} height={H} fill="#bfeee0" /><circle cx={960} cy={540} r={620} fill="#e4f8d8" /><BigLeaf x={470} y={lerp(430, 620, eout(t))} len={1000} rot={lerp(-24, -6, eout(t))} pal={DAY} /><Air f={f} pal={DAY} leaves={6} dust={20} /></g>],
  ] },
  { txt: 'Colas de caballo en el barro. Estaciones marcadas.', cuts: [
    [1, (t, f) => <g><rect width={W} height={H} fill="#8fd8c8" /><rect y={820} width={W} height={300} fill="#5a4a3c" /><rect y={820} width={W} height={14} fill={INK} />{[0, 1, 2, 3, 4].map((i) => <g key={i} transform={`rotate(${Math.sin(f / 20 + i) * 1.5} ${300 + i * 340} 830)`}><Calamite x={300 + i * 340} y={830} h={520 + (i % 3) * 120} seed={i + 3} pal={DAY} /></g>)}<Reeds x={520} y={840} s={200} seed={4} pal={DAY} /><Reeds x={1380} y={840} s={220} seed={6} pal={DAY} /></g>],
    [0.5, S({ seed: 11, px: [600, 660], z: [1.1, 1.15] })],
    [0.5, S({ seed: 11, px: [660, 720], z: [1.15, 1.2], pal: { ...DAY, leafM: '#b08a2c', leafL: '#e8b83c', leafH: '#ffe680', leafD: '#6a4a1c', ground: '#c8a850', groundL: '#f0d880', groundD: '#8a6a30' }, air: { leaves: 12, wind: 1.6 } })],
  ] },
  { txt: 'Y por todos lados, sinápsidos.', cuts: [
    [1, S({ seed: 12, px: [200, 420], z: [1, 1], k: (t, f) => <g>{B({ yaw: 50, kind: 'dicyn', x: 700 + wk(f, 80, 'dicyn').dx, y: 840, s: 0.8, phase: wk(f, 80, 'dicyn', 0.8).phase, f })}{B({ yaw: 30, kind: 'dicyn', x: 1250 + wk(f, 70, 'dicyn').dx, y: 900, s: 1.05, phase: wk(f, 70, 'dicyn', 1.05).phase + 0.4, f })}{B({ yaw: 44, kind: 'pareia', x: 2050 - wk(f, 50, 'pareia').dx, y: 860, s: 0.9, flip: true, phase: wk(f, 50, 'pareia', 0.9).phase, f })}{B({ yaw: -32, x: 1650 + wk(f, 220).dx, y: 950, s: 0.7, phase: wk(f, 220, 'procy', 0.7).phase, f })}</g> })],
  ] },
  { txt: 'Los dicinodontes: herbívoros con cuerpo de barril, pico córneo y dos colmillos.', cuts: [
    [1, S({ seed: 10, px: [300, 420], z: [1.25, 1.25], c: [1000, 700], k: (t, f, px) => B({ yaw: 58, kind: 'dicyn', x: px + 900, y: 900, s: 1.7, phase: wk(f, 110, 'dicyn', 1.7).phase, f }) })],
    [0.8, face('head', 3, 3.3, ['#c8f0a0', '#e8fac8'], (t, f) => ({ kind: 'dicyn', yaw: 44, head: Math.sin(f / 7) * 4 }), (x) => x)],
  ] },
  { txt: 'Los pareiasaurios: reptiles acorazados, lentos, del tamaño de una vaca chica.', cuts: [
    [1, S({ env: 'd', seed: 11, px: [400, 470], z: [1.2, 1.2], c: [1000, 680], k: (t, f, px) => B({ yaw: 34, kind: 'pareia', x: px + 900, y: 900, s: 1.5, phase: wk(f, 60, 'pareia', 1.5).phase, f }) })],
    [0.8, S({ env: 'd', seed: 11, px: [470, 520], z: [2.3, 2.5], c: [1000, 560], fg: false, k: (t, f, px) => B({ yaw: 48, kind: 'pareia', x: px + 900, y: 900, s: 1.5, phase: wk(f, 60, 'pareia', 1.5).phase + 0.5, f }) })],
  ] },
  { txt: 'Y los que mandan: los gorgonópsidos.', cuts: [
    [0.8, S({ pal: DUSK, seed: 8, px: [300, 320], z: [2.6, 2.6], c: [900, 880], shake: 14, fg: false, k: (t, f, px) => B({ yaw: -36, kind: 'gorgon', x: px + 500 + wk(f, 300, 'gorgon', 1.4).dx, y: 930, s: 1.4, phase: wk(f, 300, 'gorgon', 1.4).phase, f }) })],
    [1.2, S({ pal: DUSK, seed: 8, px: [300, 400], z: [1.25, 1.1], c: [960, 620], ez: eout, k: (t, f, px) => B({ yaw: 40, kind: 'gorgon', x: px + 820, y: 930, s: 1.4, phase: wk(f, 200, 'gorgon', 1.4).phase, f, jaw: 8 }) })],
  ] },
  { txt: 'Depredadores con caninos como sables.', cuts: [
    [1, (t, f) => <g>{face('fang', 3.4, 3.9, ['#1a1030', '#5a2040'], { kind: 'gorgon', yaw: 38, jaw: lerp(4, 28, eout(seg(t, 0.1, 0.5))) }, (x) => x, [960, 470])(t, f, 1)}<Burst x={980} y={600} t={seg(t, 0.45, 0.9)} n={14} /><Flash a={0.5 * (1 - seg(t, 0, 0.15))} /></g>],
  ] },
  { txt: 'En Tanzania, en las rocas donde también vivió Procynosuchus, se encontraron más de diez especies de gorgonópsidos.', cuts: [
    [0.8, mapShot(() => ({ sites: ['tanz'] }), [1.6, 3.6], [[960, 640], [1035, 680]])],
    [1.2, (t, f) => <g><rect width={W} height={H} fill="#241634" />{Array.from({ length: 10 }, (_, i) => { const on = t * 12 > i; const cx = 250 + (i % 5) * 355, cy = 400 + Math.floor(i / 5) * 380; return on ? <g key={i}><circle cx={cx} cy={cy - 90} r={150} fill={['#5a2040', '#3a2460', '#204a5a', '#5a4020', '#402a5a'][i % 5]} /><Beast kind="gorgon" yaw={26 + ((i * 13) % 40)} flip={i % 2 === 1} x={cx + (i % 2 ? 40 : -40)} y={cy + 20} s={0.34 + (i % 4) * 0.03} f={f + i * 9} jaw={10 + (i % 3) * 8} sil={i % 2 ? '#0a0810' : undefined} eyeGlow shadow={false} /></g> : null; })}</g>],
  ] },
  { txt: 'Diez formas distintas de cazar.', dur: 2.2, edit: true, cuts: Array.from({ length: 10 }, (_, i): [number, CutFn] => [1, face(i % 3 === 0 ? 'fang' : 'head', 2.2 + (i % 4) * 0.5, 2.5 + (i % 4) * 0.5, [['#5a2040', '#7a3050'], ['#3a2460', '#5a3a88'], ['#204a5a', '#2f6a78'], ['#5a4020', '#806030'], ['#402a5a', '#604080']][i % 5] as [string, string], { kind: 'gorgon', yaw: 24 + ((i * 17) % 44), flip: i % 2 === 1, jaw: 10 + ((i * 7) % 20) }, (x) => x)]) },
  { txt: 'Una de ellas, Inostrancevia africana, pertenece a un género que en Rusia llegó a medir alrededor de tres metros.', cuts: [
    [1, (t, f) => <g><rect width={W} height={H} fill="#f0d8b0" /><rect y={740} width={W} height={240} fill="#c89a68" /><rect y={736} width={W} height={10} fill={INK} /><g opacity={seg(t, 0, 0.1)}><Sil kind="human" x={330} y={740} s={1} col="#3a2c48" /></g><g transform={`translate(${lerp(500, 0, eout(seg(t, 0.05, 0.4)))} 0)`}><Beast kind="gorgon" x={1060} y={740} s={0.84} f={f} jaw={10} /></g><g opacity={seg(t, 0.45, 0.55)}><Beast x={1660} y={740} s={0.24} f={f} /><Ruler x0={610} x1={1510} y={800} t={seg(t, 0.4, 0.7)} text="≈ 3 m" /></g></g>],
    [0.6, eyeShot(2.2, 2.6, ['#1a1030', '#5a2040'], { kind: 'gorgon', jaw: 10, yaw: 56 }, eio)],
  ] },
  { txt: 'Ahora imaginá ser un animal de sesenta centímetros en ese barrio.', cuts: [
    [1, S({ pal: DUSK, seed: 2, px: [600, 640], z: [1.5, 1.7], c: [1100, 800], k: (t, f, px) => <g>{B({ yaw: 54, kind: 'gorgon', x: px + 250 + wk(f, 120, 'gorgon', 1.7).dx, y: 1000, s: 1.7, phase: wk(f, 120, 'gorgon', 1.7).phase, f, sil: '#07050c', eyeGlow: true })}{B({ yaw: 28, x: px + 1250, y: 890, s: 0.8, crouch: 0.8, f, flip: true, head: -20, blink: blinkAt(f, 30) })}</g> })],
    [0.6, eyeShot(6, 8, ['#1a1030', '#4a2050'], { look: -2 }, eio)],
  ] },
  // persecución sin voz: cortes cada vez más rápidos
  { txt: '', dur: 12.4, cuts: ([[2.0, 'prey'], [1.6, 'legs'], [1.4, 'wide'], [1.1, 'eye'], [1.0, 'jaws'], [0.9, 'prey'], [0.8, 'legs'], [0.7, 'wide'], [0.6, 'jaws'], [0.5, 'eye'], [0.45, 'river'], [0.4, 'legs'], [0.35, 'prey'], [0.3, 'jaws'], [0.3, 'river']] as [number, Parameters<typeof chase>[0]][]).map(([w, k]): [number, CutFn] => [w, chase(k)]) },
  { txt: '', dur: 2.6, cuts: [[0.9, chase('leap')], [0.9, chase('splash')], [0.8, () => <rect width={W} height={H} fill="#05030a" />]] },
  { txt: 'No tenemos un fósil que muestre a un gorgonópsido atacando a un Procynosuchus.', cuts: [
    [1, S({ pal: DUSK, seed: 5, px: [500, 540], z: [1.5, 1.4], c: [960, 600], fg: false, k: (t, f, px) => <g>{[0, 1, 2].map((i) => { const p = ((f / 40 + i / 3) % 1); return <ellipse key={i} cx={px * 0.4 + 1150} cy={625} rx={30 + p * 190} ry={5 + p * 22} fill="none" stroke="#c8d8ff" strokeWidth={5 * (1 - p)} transform={`translate(${px * 0.6} 0)`} />; })}{B({ yaw: 36, kind: 'gorgon', x: px + 620, y: 890, s: 1, f, head: 12, jaw: 6 })}</g> })],
    [0.8, (t, f) => <Cam zoom={lerp(1.2, 1.3, t)} cx={900} cy={560}><Dig f={0} t={1} close /></Cam>],
  ] },
  { txt: 'Pero vivieron en los mismos ríos, en los mismos años, bajo el mismo cielo.', cuts: [
    [1, S({ pal: VIOLET, seed: 6, moon: true, px: [800, 900], z: [1.35, 1.35], c: [[960, 700], [960, 380]], fg: false })],
    [0.8, S({ pal: VIOLET, seed: 6, moon: true, px: [900, 960], z: [1, 1], k: (t, f, px) => <g>{B({ yaw: 50, kind: 'gorgon', x: px + 500, y: 880, s: 0.8, f, sil: '#0a0818' })}{B({ yaw: 30, x: px + 1500, y: 900, s: 0.8, f, sil: '#0a0818', flip: true })}</g> })],
  ] },
  { txt: 'Ser chiquito, en el Pérmico, era un oficio de riesgo.', dur: 4.6, cuts: [
    [1, S({ pal: VIOLET, seed: 10, moon: true, px: [500, 560], z: [1.6, 1.45], c: [1000, 760], k: (t, f, px) => B({ yaw: 44, x: px + 900, y: 880, s: 1.2, f, head: Math.sin(f / 2) * 14 * (1 - seg(t, 0, 0.6)), flip: true, blink: blinkAt(f, 40) }) })],
    [1.1, (t, f) => <g>{S({ pal: VIOLET, seed: 10, moon: true, px: [560, 700], z: [1.1, 1], k: (tt, ff, px) => B({ yaw: -32, x: 1460 + wk(ff, 150).dx, y: 880, s: 1.1, phase: wk(ff, 150, 'procy', 1.1).phase, f: ff }) })(t, f, 1)}<rect width={W} height={H} fill="#05030a" opacity={seg(t, 0.6, 1)} /></g>],
  ] },
];

export type FlatCut = { start: number; dur: number; fn: CutFn; beat: number; edit: boolean; txt: string };
export const flatten = (): { cuts: FlatCut[]; total: number } => {
  const cuts: FlatCut[] = [];
  let fr = 0;
  BEATS.forEach((b, bi) => {
    const words = b.txt.split(/\s+/).filter(Boolean).length;
    const secs = b.dur ?? Math.max(1.4, words / 2.75 + 0.35);
    const frames = Math.round(secs * FPS);
    const sum = b.cuts.reduce((s, c) => s + c[0], 0);
    let used = 0;
    b.cuts.forEach((c, ci) => {
      const d = ci === b.cuts.length - 1 ? frames - used : Math.max(2, Math.round((frames * c[0]) / sum));
      cuts.push({ start: fr + used, dur: d, fn: c[1], beat: bi, edit: !!b.edit, txt: b.txt });
      used += d;
    });
    fr += frames;
  });
  return { cuts, total: fr };
};
void Glosso; void leaf;
