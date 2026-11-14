import React from 'react';
import { H, W } from './lib';
import { Beast } from './beast';
import { LAYERS } from './biomes';
import { PH, PW, PaintDefs } from './paint';

const valle = (i: number) => { const L = LAYERS.filter((l) => l.name.startsWith('valle'))[i]; return <g key={i} filter={L.rough ? 'url(#rough)' : undefined}>{L.el}</g>; };
const B1 = { x: 1500, y: 850, s: 1.25, yaw: 36, turn: 14, head: -4, jaw: 3, phase: 0.18 };
const B2 = { x: 1300, y: 760, s: 2.7, yaw: 38, turn: 12, head: -5, jaw: 5 };

/** bases de la hoja de estilo: 0 valle con animal, 1 su máscara, 2 animal de cerca, 3 su máscara */
export const EstiloBase: React.FC<{ i: number }> = ({ i }) => {
  if (i === 4) return <svg viewBox={`0 0 ${PW} ${PH}`} width={PW} height={PH}><PaintDefs />{[0, 1, 2, 3].map(valle)}</svg>;
  if (i === 5) return <svg viewBox={`0 0 ${PW} ${PH}`} width={PW} height={PH}><PaintDefs />{valle(4)}</svg>;
  if (i === 6) return <svg viewBox={`0 0 ${PW} ${PH}`} width={PW} height={PH}><PaintDefs /><g filter="url(#b6)" transform="translate(-1500 -640) scale(1.9)">{[0, 1, 2, 3].map(valle)}</g><rect width={PW} height={PH} fill="#04121a" opacity={0.3} /></svg>;
  const mask = i === 1 || i === 3;
  const b = i < 2 ? B1 : B2;
  return (
    <svg viewBox={`0 0 ${PW} ${PH}`} width={PW} height={PH} style={{ background: '#000' }}>
      <PaintDefs />
      {!mask && i < 2 && [0, 1, 2, 3].map(valle)}
      {!mask && i >= 2 && <g filter="url(#b20)" transform="translate(-900 -560) scale(1.6)">{[0, 1, 2, 3].map(valle)}</g>}
      {!mask && i >= 2 && <rect width={PW} height={PH} fill="#06141a" opacity={0.35} />}
      {mask ? <g filter="url(#b20)"><Beast {...b} sil="#ffffff" shadow={false} drift={0} /></g> : <Beast {...b} paint amb="#5fa8a0" drift={0} />}
      {!mask && i < 2 && valle(4)}
      {!mask && i >= 2 && <g transform="translate(-900 -420) scale(1.6)" filter="url(#b6)">{valle(4)}</g>}
    </svg>
  );
};
void W; void H;
