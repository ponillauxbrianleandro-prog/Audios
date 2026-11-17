"""Limpieza de voz: pasa-altos, reducción de ruido, de-reverberación (Lebart) y limitador lineal sin saturación."""
import numpy as np
from scipy.signal import butter, sosfiltfilt, stft, istft
import noisereduce as nr


def highpass(x, sr, fc=80.0):
    return sosfiltfilt(butter(4, fc, "highpass", fs=sr, output="sos"), x).astype(np.float32)


def dereverb(x, sr, rt60=0.45, delay=0.050, strength=1.0, floor=0.12):
    """Resta espectral de la cola de reverberación tardía (Lebart et al.): |S|² = |Y|² − g·|Y retrasado|²·decay."""
    n = 1024
    hop = n // 4
    f, t, Z = stft(x, sr, nperseg=n, noverlap=n - hop)
    P = np.abs(Z) ** 2
    d = max(1, int(round(delay * sr / hop)))
    decay = np.exp(-2.0 * np.log(10) / rt60 * delay)
    late = np.zeros_like(P)
    late[:, d:] = P[:, :-d] * decay
    # la cola se suaviza en tiempo para no restar «ruido musical»
    k = np.ones(3) / 3
    late = np.apply_along_axis(lambda r: np.convolve(r, k, "same"), 1, late)
    g = np.maximum(1.0 - strength * late / (P + 1e-12), floor)
    _, y = istft(Z * np.sqrt(g), sr, nperseg=n, noverlap=n - hop)
    return y[: len(x)].astype(np.float32)


def denoise(x, sr, amount=0.85):
    return nr.reduce_noise(y=x, sr=sr, stationary=False, prop_decrease=amount, time_mask_smooth_ms=60, freq_mask_smooth_hz=400).astype(np.float32)


def limitar(x, techo=0.84):
    """Normaliza de forma lineal; solo si hay un pico por encima del techo se baja la ganancia (sin saturación)."""
    pk = np.abs(x).max() + 1e-9
    return (x * (techo / pk)).astype(np.float32)


def limpiar(x, sr, rt60=0.45, reverb=True, ruido=True):
    x = highpass(x, sr)
    if ruido:
        x = denoise(x, sr)
    if reverb:
        x = dereverb(x, sr, rt60=rt60)
    return limitar(x)
