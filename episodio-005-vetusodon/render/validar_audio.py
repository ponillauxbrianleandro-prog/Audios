#!/usr/bin/env python3
"""Validación automática del audio y del video de un episodio (reutilizable). Sale con código 1 si algo falla.

  python validar_audio.py --cache cache_v16 --audio ../video/audio/vetusodon-v10.wav --video ../video/vetusodon-v19.mp4 \
      --base-video ../video/vetusodon-v11.mp4 [--partes ../video/partes19/*.mp4] [--previo ../video/v18-final/audio-v18.wav]
Compara la voz con la grabación de referencia (voice_ai/cache_v13/ref/completo24.wav)."""
import argparse, glob, json, subprocess, sys
from pathlib import Path
import numpy as np
import scipy.signal as ss

AQUI = Path(__file__).resolve().parent
VOICE = AQUI.parents[1] / "voice_ai"
FALLAS, FILAS = [], []


def chk(nombre, valor, ok, detalle=""):
    FILAS.append((("OK " if ok else "FALLA"), nombre, valor, detalle))
    if not ok:
        FALLAS.append(nombre)


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def leer(p, ch=1, sr=48000):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-f", "f32le", "-ac", str(ch), "-ar", str(sr), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(r, np.float32).reshape(-1, ch)


def sonoridad(p):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(p), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"])
    j = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    return float(j["input_i"]), float(j["input_tp"])


def ffprobe(p, *entradas):
    r = run(["ffprobe", "-v", "error", *entradas, "-of", "json", str(p)])
    return json.loads(r.stdout)


def md5_video(p):
    r = run(["ffmpeg", "-v", "error", "-i", str(p), "-map", "0:v:0", "-c", "copy", "-f", "md5", "-"])
    return r.stdout.strip()


def paquetes(p):
    j = ffprobe(p, "-count_packets", "-select_streams", "v:0", "-show_entries", "stream=nb_read_packets")
    return int(j["streams"][0]["nb_read_packets"])


def duracion(p):
    return float(ffprobe(p, "-show_entries", "format=duration")["format"]["duration"])


def metricas_voz(x, s):
    import parselmouth
    from parselmouth.praat import call
    sn = parselmouth.Sound(x.astype(float), s)
    pp = call(sn, "To PointProcess (periodic, cc)", 75, 350)
    jit = call(pp, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3) * 100
    shi = call([sn, pp], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6) * 100
    p = sn.to_pitch(time_step=0.01, pitch_floor=75, pitch_ceiling=350).selected_array["frequency"]
    v = p > 0
    par = v[1:] & v[:-1]
    c = 1200 * np.abs(np.log2(p[1:][par] / p[:-1][par]))
    f = p[v]
    it = sn.to_intensity(minimum_pitch=75, time_step=0.01).values[0]
    pk, _ = ss.find_peaks(it, prominence=3, distance=8)
    iv = np.diff(pk) * 0.01
    return dict(f0=float(np.median(f)), jit=jit, shi=shi, sd=float(np.std(12 * np.log2(f / np.median(f)))), s200=float(100 * np.mean(c > 200)),
                cv=float(iv.std() / iv.mean()) if len(iv) > 5 else float("nan"))


def ltas(x, sr, centros):
    fr = int(0.05 * sr)
    n = len(x) // fr
    E = np.array([np.sqrt((x[i * fr:(i + 1) * fr] ** 2).mean()) for i in range(n)])
    k = np.concatenate([x[i * fr:(i + 1) * fr] for i in range(n) if E[i] > np.percentile(E, 40)])
    f, P = ss.welch(k, sr, nperseg=4096)
    L = np.array([10 * np.log10(P[(f >= c / 2 ** (1 / 6)) & (f < c * 2 ** (1 / 6))].sum() + 1e-20) for c in centros])
    return L - L[int(np.argmin([abs(c - 1000) for c in centros]))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--video", required=True)
    ap.add_argument("--base-video", required=True)
    ap.add_argument("--partes", nargs="*", default=[])
    ap.add_argument("--previo", default=None)
    ap.add_argument("--ref", default=str(VOICE / "cache_v13/ref/completo24.wav"))
    a = ap.parse_args()
    import soundfile as sf
    C = VOICE / a.cache
    T = json.loads((C / "tiempos_lineas.json").read_text())
    D = json.loads((C / "durs_v11.json").read_text())
    # ---------------------------------------------------------------- audio final
    x = leer(a.audio, 2).mean(1)
    sr = 48000
    lufs, tp = sonoridad(a.audio)
    chk("sonoridad (LUFS)", f"{lufs:.1f}", -19.0 <= lufs <= -15.3, "objetivo -16; baja solo si hace falta para no recortar")
    chk("pico verdadero (dBTP)", f"{tp:.2f}", tp <= -1.4, "<= -1,5")
    chk("muestras >0,98", int((np.abs(x) > 0.98).sum()), int((np.abs(x) > 0.98).sum()) == 0)
    mx = np.abs(x).max()
    tope = np.abs(x) >= mx * 0.995
    corridas = np.diff(np.flatnonzero(np.diff(np.concatenate([[0], tope.astype(int), [0]]))))[::2]
    chk("tramos con pico 'clavado' (>=8 muestras seguidas en el techo)", int((corridas >= 8).sum()), int((corridas >= 8).sum()) == 0, "recorte sostenido; las corridas de 3-7 muestras (<0,2 ms) son el limitador y no se oyen")
    chk("segundos con pico >= 0,80", int((np.abs(x[:len(x) // sr * sr]).reshape(-1, sr).max(1) >= 0.80).sum()), int((np.abs(x[:len(x) // sr * sr]).reshape(-1, sr).max(1) >= 0.80).sum()) <= 5, "v18 tenía 67: el limitador de loudnorm trabajaba sin parar")
    seg_techo = int((np.abs(x[:len(x) // sr * sr]).reshape(-1, sr).max(1) >= mx * 0.989).sum())
    chk("segundos con pico a <0,1 dB del máximo", seg_techo, seg_techo <= 3)
    # ---------------------------------------------------------------- voz sobre la cama
    es = [np.load(f) for f in sorted(glob.glob(str(AQUI.parent / "video/audio/estudio_*.npz")))]
    rel, comp = [], {}
    for e in es:
        m = len(e["voz"]) // 50
        v = np.sqrt((e["voz"][:m * 50].reshape(m, 50) ** 2).mean(1))
        c = np.sqrt((e["cama"][:m * 50].reshape(m, 50) ** 2).mean(1))
        act = v > 0.04
        rel += list(20 * np.log10(v[act] / (c[act] + 1e-9)))
        for k in ("mus", "amb", "fx"):
            if k in e.files:
                comp.setdefault(k, []).extend(list(20 * np.log10(v[act] / (np.sqrt((e[k][:m * 50].reshape(m, 50) ** 2).mean(1))[act] + 1e-9))))
    if rel:
        rel = np.array(rel)
        for k, vals in comp.items():
            if k == "fx":
                chk("  voz − efectos (mediana, dB)", f"{np.median(vals):+.1f}", np.median(vals) >= 10.0, "efectos sin cambios; solo informativo con piso de 10 dB")
        for k, nom in (("mus", "música"), ("amb", "ambiente")):
            if k in comp:
                chk(f"voz − {nom} (mediana, dB)", f"{np.median(comp[k]):+.1f}", np.median(comp[k]) >= 15.0, "diferencia notable")
                chk(f"ventanas con voz − {nom} ≥ 12 dB", f"{100 * np.mean(np.array(comp[k]) >= 12):.0f} %", np.mean(np.array(comp[k]) >= 12) >= 0.80, "las que bajan son sílabas suaves y colas de frase")
        chk("voz − cama completa (mediana, dB)", f"{np.median(rel):+.1f}", np.median(rel) >= 9.0, "incluye los efectos del documental, que no se tocan")
    else:
        chk("estudios de voz/cama", "no hay estudio_*.npz", False)
    if a.previo:
        y = leer(a.previo, 2).mean(1)
        act = np.zeros(len(x), bool)
        for k, t in T.items():
            act[int(t * sr):int((t + D[k]) * sr)] = True
        w = sr // 2
        def fuera(z):
            n = min(len(z), len(act)) // w
            r = np.array([np.sqrt((z[i * w:(i + 1) * w] ** 2).mean() + 1e-12) for i in range(n)])
            f = np.array([act[i * w:(i + 1) * w].mean() for i in range(n)])
            return 20 * np.log10(np.median(r[f < 0.02]))
        d = fuera(x) - fuera(y)
        chk("cama fuera de la voz vs versión previa (dB)", f"{d:+.1f}", abs(d) <= 2.5, "efectos/música sin voz no deben cambiar")
    # ---------------------------------------------------------------- voz: calidad y naturalidad
    xr, sr24 = sf.read(a.ref)
    R = [metricas_voz(xr[i * sr24 * 20:(i + 1) * sr24 * 20], sr24) for i in range(1, 10)]
    ref = {k: float(np.mean([r[k] for r in R])) for k in R[0]}
    fin = sorted(glob.glob(str(C / "final/[0-9]*_*.wav")))
    M, niv, pks, hf, dd = [], [], [], [], []
    for f in fin:
        y, s = sf.read(f)
        y = y if y.ndim == 1 else y.mean(1)
        act = y[np.abs(y) > 0.02]
        niv.append(20 * np.log10(np.sqrt((act ** 2).mean())))
        pks.append(np.abs(y).max())
        fq, P = ss.welch(y, s, nperseg=4096)
        hf.append(10 * np.log10(P[fq > 12000].sum() / P.sum() + 1e-20))
        k = Path(f).stem
        dd.append(abs(len(y) / s - D[k]))
        if len(y) / s > 2.5:
            M.append(metricas_voz(y, s))
    m = {k: float(np.nanmean([q[k] for q in M])) for k in M[0]}
    chk("voz: mediana de F0 (Hz)", f"{m['f0']:.0f}", 118 <= m["f0"] <= 138, "grave: 120-135")
    for k, nom in (("jit", "jitter %"), ("shi", "shimmer %"), ("sd", "variación de F0 (semitonos)"), ("cv", "irregularidad de ritmo (CV)")):
        chk(f"voz: {nom}", f"{m[k]:.2f} (grab. {ref[k]:.2f})", abs(m[k] / ref[k] - 1) <= 0.25, "±25 % de la grabación")
    chk("voz: saltos de tono >200 cents (%) — 'hipo'", f"{m['s200']:.2f}", m["s200"] <= 1.5)
    chk("voz: energía sobre 12 kHz (dB, peor frase)", f"{max(hf):.0f}", max(hf) <= -60)
    chk("voz: nivel activo medio de las frases, antes de la mezcla (dBFS)", f"{np.mean(niv):.1f}", -16.5 <= np.mean(niv) <= -13.0)
    chk("voz: pico máximo de las frases (para no tocar el techo tras la ganancia)", f"{max(pks):.2f}", max(pks) <= 0.58)
    cr = [20 * np.log10(np.abs(sf.read(f)[0]).max() / np.sqrt((sf.read(f)[0][np.abs(sf.read(f)[0]) > 0.02] ** 2).mean())) for f in fin[::3]]
    chk("voz: cresta (dB) — picos controlados", f"{np.mean(cr):.1f}", np.mean(cr) <= 11.5)
    chk("voz: duración de cada frase = durs_v11 (s, peor dif.)", f"{max(dd):.3f}", max(dd) <= 0.01)
    p = json.loads((VOICE / "perfil_quebracho3.json").read_text())
    cen = p["centros"]
    Lr = ltas(xr, sr24, cen)
    Lv = ltas(np.concatenate([sf.read(f)[0] if sf.read(f)[0].ndim == 1 else sf.read(f)[0].mean(1) for f in fin[::2]]), 48000, cen)
    idx = [i for i, c in enumerate(cen) if 200 <= c <= 520]
    gr = float(np.mean([Lv[i] - Lr[i] for i in idx]))
    chk("voz: cuerpo 200–500 Hz vs grabación (dB)", f"{gr:+.1f}", gr >= -2.0, "no más fina que la grabación")
    # ---------------------------------------------------------------- video
    j = ffprobe(a.video, "-select_streams", "v:0", "-show_entries", "stream=width,height")
    wv, hv = j["streams"][0]["width"], j["streams"][0]["height"]
    chk("video: resolución", f"{wv}x{hv}", (wv, hv) == (1920, 1080))
    dv = duracion(a.video)
    chk("video: duración (s)", f"{dv:.2f}", abs(dv - 629.6) <= 0.2, "10:29")
    mb = Path(a.video).stat().st_size / 1e6
    chk("video: tamaño (MB)", f"{mb:.0f}", mb <= 500)
    da = len(x) / sr
    chk("audio vs video (s)", f"{da:.2f} / {dv:.2f}", abs(da - dv) <= 0.7, "el audio v10 dura 630,2 s; el video corta en 629,6")
    h1, h0 = md5_video(a.video), md5_video(a.base_video)
    chk("video: stream de imagen idéntico al aprobado", "sí" if h1 == h0 else "NO", h1 == h0, "hash de los paquetes de video")
    if a.partes:
        ps = sorted(a.partes)
        dsum = sum(duracion(q) for q in ps)
        psum = sum(paquetes(q) for q in ps)
        chk("partes: suma de duraciones (s)", f"{dsum:.2f} vs {dv:.2f}", abs(dsum - dv) <= 0.3)
        chk("partes: suma de cuadros", f"{psum} vs {paquetes(a.video)}", psum == paquetes(a.video))
    # ---------------------------------------------------------------- informe
    print("\nVALIDACIÓN DEL AUDIO / VIDEO")
    for est, nom, val, det in FILAS:
        print(f" [{est}] {nom}: {val}" + (f"   · {det}" if det else ""))
    print("\nRESULTADO:", "TODO OK" if not FALLAS else f"{len(FALLAS)} FALLAS -> " + "; ".join(FALLAS))
    sys.exit(0 if not FALLAS else 1)


if __name__ == "__main__":
    main()
