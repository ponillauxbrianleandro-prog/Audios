"""Música ambiente sintetizada (pad + shimmer + ráfaga de entrada) en estéreo."""
import numpy as np, wave

SR = 44100
NOTES = {  # frecuencias base de cada mundo
    "jupiter": [55.0, 82.41, 110.0, 164.81, 220.0],
    "saturno": [49.0, 73.42, 98.0, 146.83, 196.0],
    "neptuno": [43.65, 65.41, 87.31, 130.81, 174.61],
    "marte":   [58.27, 87.31, 116.54, 174.61, 233.08],
}

def reverb(x, secs=3.2, seed=1):
    rng = np.random.default_rng(seed); n = int(SR * secs)
    ir = rng.normal(0, 1, n) * np.exp(-np.arange(n) / (SR * secs / 4.5)); ir[0] = 0
    N = len(x) + n; X = np.fft.rfft(x, N); Y = np.fft.rfft(ir, N)
    y = np.fft.irfft(X * Y, N)[:len(x)]
    return y / (np.abs(y).max() + 1e-9)

def make(name, path, dur):
    t = np.arange(int(SR * dur)) / SR
    rng = np.random.default_rng(abs(hash(name)) % 1000)
    L = np.zeros_like(t); R = np.zeros_like(t)
    for i, f in enumerate(NOTES[name]):
        for det, ch in ((0.997, 0), (1.003, 1)):
            ph = rng.uniform(0, 6.28)
            lfo = 0.6 + 0.4 * np.sin(2 * np.pi * (0.05 + 0.03 * i) * t + ph)
            s = np.sin(2 * np.pi * f * det * t + ph) + 0.35 * np.sin(2 * np.pi * 2 * f * det * t) + 0.15 * np.sin(2 * np.pi * 3 * f * det * t)
            s *= lfo * (0.5 / (1 + i * 0.5))
            (L if ch == 0 else R)[:] += s
    env = np.clip(t / 5, 0, 1) * (0.55 + 0.45 * np.clip((t - 18) / 8, 0, 1)) * np.clip((dur - t) / 3, 0, 1)
    L *= env; R *= env
    # shimmer en el último acto
    sh = np.zeros_like(t)
    for k in range(40):
        t0 = rng.uniform(26, dur - 3); f = rng.choice(NOTES[name]) * 8 * rng.choice([1, 1.5, 2])
        m = (t >= t0) & (t < t0 + 2.5); tt = t[m] - t0
        sh[m] += 0.05 * np.sin(2 * np.pi * f * tt) * np.exp(-tt * 2.0)
    # ráfaga de entrada atmosférica
    ns = rng.normal(0, 1, len(t)); k = np.ones(200) / 200
    ns = np.convolve(ns, k, "same") * 6
    gust = ns * np.exp(-((t - 21.5) / 2.6) ** 2) * 0.35
    L = reverb(L + sh + gust, seed=1) * 0.8; R = reverb(R + sh * 0.9 + gust * 0.9, seed=2) * 0.8
    out = np.stack([L, R], 1); out *= np.clip(t / 1.5, 0, 1)[:, None] * np.clip((dur - t) / 2.0, 0, 1)[:, None]
    out = (out / np.abs(out).max() * 0.6 * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
