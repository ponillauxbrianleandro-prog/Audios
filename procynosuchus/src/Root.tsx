import React from 'react';
import { Composition, useCurrentFrame } from 'remotion';
import { FPS, H, W } from './lib';
import { DAY, DRY, DUSK, VIOLET } from './art';
import { Air, DryPlain, Riverbank, SpireVista } from './env';
import { Beast } from './beast';
import { Film } from './Film';
import { flatten } from './timeline';

const Test: React.FC = () => {
  const f = useCurrentFrame();
  const k = Math.floor(f / 10);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} width={W} height={H}>
      {k === 0 && <Riverbank f={f} px={300}><Beast x={1250} y={860} s={1.3} phase={0.2} f={f} /></Riverbank>}
      {k === 1 && <Riverbank f={f} px={900} pal={VIOLET} seed={4} moon><Beast x={1900} y={880} s={1.6} jaw={24} head={-8} f={f} flip /></Riverbank>}
      {k === 2 && <DryPlain f={f} px={500}><Beast x={1400} y={880} s={1.2} phase={0.7} run f={f} /><Beast kind="dicyn" x={2000} y={820} s={1} phase={0.3} f={f} flip /></DryPlain>}
      {k === 3 && <SpireVista f={f} px={200} />}
      {k === 4 && <Riverbank f={f} px={500} pal={DUSK} seed={2}><Beast kind="gorgon" x={1500} y={900} s={1.1} phase={0.4} jaw={18} f={f} /><Beast x={2150} y={900} s={1} phase={0.1} run f={f} /></Riverbank>}
      {k === 5 && <g><rect width={W} height={H} fill="#e8e0d0" /><Beast x={500} y={400} s={1.6} f={f} /><Beast x={1300} y={400} s={1.6} phase={0.35} f={f} /><Beast x={500} y={800} s={1.6} jaw={30} head={-10} crouch={0.6} f={f} /><Beast kind="pareia" x={1350} y={900} s={1} phase={0.8} f={f} /><Beast x={700} y={1900} s={7} jaw={26} f={f} shadow={false} /></g>}
      <Air f={f} pal={DAY} bugs={k === 0 ? 3 : 0} />
    </svg>
  );
};

export const Root: React.FC = () => (
  <>
    <Composition id="Procyno" component={Film} width={W} height={H} fps={FPS} durationInFrames={flatten().total} />
    <Composition id="Test" component={Test} width={W} height={H} fps={FPS} durationInFrames={60} />
  </>
);
