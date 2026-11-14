import React from 'react';
import { Composition, Freeze, useCurrentFrame } from 'remotion';
import { FPS, H, W } from './lib';
import { DAY, DRY, DUSK, VIOLET } from './art';
import { Air, DryPlain, Riverbank, SpireVista } from './env';
import { Beast } from './beast';
import { Film } from './Film';
import { BiomePreview, LAYERS, LayerSheet } from './biomes';
import { PH, PW } from './paint';
import { EstiloBase } from './Estilo';
import { LaminaPersonajes } from './Personajes';
import { flatten } from './timeline';

const Test: React.FC = () => {
  const f = useCurrentFrame();
  const k = Math.floor(f / 10);
  const yaws = [20, 40, 60, 80, -20, -40, -60, 35];
  return (
    <svg viewBox={`0 0 ${W} ${H}`} width={W} height={H}>
      <rect width={W} height={H} fill="#cfe8d8" />
      {k === 0 && yaws.map((yw, i) => <Beast key={i} paint x={260 + (i % 4) * 470} y={400 + Math.floor(i / 4) * 480} s={0.62} yaw={yw} f={f} phase={i === 7 ? 0.3 : undefined} jaw={i === 3 ? 22 : 0} />)}
      {k === 1 && <g><Beast paint x={800} y={720} s={2.1} yaw={34} f={f} jaw={10} /></g>}
      {k === 2 && <g><Beast x={520} y={520} s={0.9} yaw={40} phase={0.3} f={f} /><Beast x={1400} y={480} s={0.9} yaw={55} jaw={26} head={-12} f={f} flip /><Beast x={520} y={960} s={0.9} yaw={-35} phase={0.7} f={f} /><Beast x={1400} y={960} s={0.9} yaw={30} crouch={0.8} f={f} turn={25} /></g>}
      {k === 4 && <Riverbank f={f} px={300}><Beast x={1300} y={860} s={1.2} yaw={36} phase={0.2} f={f} /></Riverbank>}
      {k === 5 && <Riverbank f={f} px={900} pal={VIOLET} seed={4} moon><Beast x={1900} y={880} s={1.4} yaw={50} jaw={20} f={f} flip /></Riverbank>}
      {k === 6 && <DryPlain f={f} px={500}><Beast x={1400} y={880} s={1.2} yaw={30} phase={0.7} run f={f} /><Beast kind="dicyn" x={2100} y={800} s={0.9} yaw={45} f={f} flip /></DryPlain>}
      {k === 7 && <Riverbank f={f} px={500} pal={DUSK} seed={2}><Beast kind="gorgon" x={1400} y={880} s={1} yaw={35} phase={0.4} jaw={18} f={f} /></Riverbank>}
      {k === 3 && <g><Beast kind="gorgon" x={520} y={620} s={0.75} yaw={38} phase={0.2} jaw={16} f={f} /><Beast kind="dicyn" x={1450} y={480} s={0.8} yaw={40} f={f} flip /><Beast kind="pareia" x={1400} y={980} s={0.75} yaw={35} phase={0.6} f={f} /><Beast kind="gorgon" x={520} y={1020} s={0.5} yaw={-40} f={f} sil="#0a0810" eyeGlow /></g>}
    </svg>
  );
};

const MIDS = flatten().cuts.map((c) => Math.floor(c.start + c.dur * 0.55));
const Sheet: React.FC = () => { const f = useCurrentFrame(); void f; return <Film at={MIDS} />; };

export const Root: React.FC = () => (
  <>
    <Composition id="Procyno" component={Film} width={W} height={H} fps={FPS} durationInFrames={flatten().total} />
    <Composition id="Layers" component={() => { const f = useCurrentFrame(); return <LayerSheet i={f} />; }} width={PW} height={PH} fps={FPS} durationInFrames={LAYERS.length} />
    <Composition id="E3" component={LaminaPersonajes} width={W} height={H} fps={FPS} durationInFrames={1} />
    <Composition id="Estilo" component={() => { const f = useCurrentFrame(); return <EstiloBase i={f} />; }} width={PW} height={PH} fps={FPS} durationInFrames={7} />
    <Composition id="Biome" component={() => { const f = useCurrentFrame(); return <BiomePreview name={['valle', 'agujas', 'mesetas', 'agua'][f]} />; }} width={PW} height={PH} fps={FPS} durationInFrames={4} />
    <Composition id="Sheet" component={Sheet} width={W} height={H} fps={FPS} durationInFrames={MIDS.length} />
    <Composition id="Test" component={Test} width={W} height={H} fps={FPS} durationInFrames={90} />
  </>
);
