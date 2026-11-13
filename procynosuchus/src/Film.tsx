import React, { useMemo } from 'react';
import { useCurrentFrame } from 'remotion';
import { H, W, eout, seg } from './lib';
import { Cam, Flash, Sub, Vignette } from './fx';
import { flatten } from './timeline';

export const SUBS = true; // subtítulo guía temporal: poner en false cuando exista la voz

export const Film: React.FC = () => {
  const frame = useCurrentFrame();
  const { cuts } = useMemo(() => flatten(), []);
  let c = cuts[cuts.length - 1];
  for (const k of cuts) if (frame >= k.start && frame < k.start + k.dur) { c = k; break; }
  const f = frame - c.start;
  const t = c.dur > 1 ? f / (c.dur - 1) : 0;
  const punch = c.edit ? 1 + 0.09 * (1 - eout(seg(f, 0, 7))) : 1;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} width={W} height={H} style={{ background: '#05030a' }}>
      <Cam zoom={punch}>{c.fn(t, f, c.dur)}</Cam>
      <Vignette a={0.38} />
      {c.edit && <Flash a={0.55 * (1 - seg(f, 0, 3))} />}
      {SUBS && <Sub text={c.txt} />}
    </svg>
  );
};
