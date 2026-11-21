import json,sys,numpy as np,soundfile as sf,parselmouth
from pathlib import Path
sys.path.insert(0,'.'); import perfil_referencia as P
def load(d):
    xs=[];F0=[];F2=[];pk=0
    for f in sorted(Path(d).glob('[0-9]*_*.wav')):
        x,sr=sf.read(str(f)); x=x if x.ndim==1 else x.mean(1); pk=max(pk,abs(x).max())
        s=parselmouth.Sound(x,sr)
        p=s.to_pitch(pitch_floor=60,pitch_ceiling=350).selected_array['frequency']; F0+=list(p[p>0])
        fm=s.to_formant_burg(); pp=s.to_pitch(pitch_floor=60,pitch_ceiling=350)
        for t in np.arange(0.05,s.duration-0.05,0.05):
            if pp.get_value_at_time(t)==pp.get_value_at_time(t):
                v=fm.get_value_at_time(2,t)
                if v==v: F2.append(v)
        import scipy.signal as ss
        xs.append(ss.resample_poly(x,1,2) if sr==48000 else x)
    x=np.concatenate(xs); L=P.ltas(x,24000)
    f,Pw=__import__('scipy.signal',fromlist=['welch']).welch(x,24000,nperseg=4096)
    cen=(f*Pw).sum()/Pw.sum()
    return L,np.array(F0),np.array(F2),cen,pk
ref=json.load(open('perfil_referencia.json'))
for nm in ['final_v11','final']:
    L,F0,F2,c,pk=load(f'cache_v9/{nm}')
    d=L-np.array(ref['ref_ltas'])
    print(nm,'F0 med %.0f p10-p90 %.0f F2 %.0f centroide %.0f pico %.2f'%(np.median(F0),np.percentile(F0,90)-np.percentile(F0,10),np.median(F2),c,pk))
    print(' dev dB:',' '.join('%d:%+.1f'%(cc,v) for cc,v in zip(P.CENTROS,d) if 126<=cc<=3300))
