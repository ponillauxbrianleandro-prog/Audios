"""Utilidades comunes: ruido fractal, interpolación y pequeñas ayudas de imagen."""
import numpy as np
import cv2


def fbm(shape, beta=2.0, seed=0, lowcut=0.0):
    """Ruido fractal por síntesis espectral (1/f^beta). Teselable. Devuelve float32 en [0,1]."""
    h, w = shape
    rng = np.random.default_rng(seed)
    fy = np.fft.fftfreq(h)[:, None] * h
    fx = np.fft.rfftfreq(w)[None, :] * w
    f = np.sqrt(fx * fx + fy * fy)
    f[0, 0] = 1.0
    amp = f ** (-beta / 2.0)
    if lowcut > 0:
        amp *= 1.0 - np.exp(-(f / lowcut) ** 2)
    amp[0, 0] = 0.0
    ph = rng.uniform(0, 2 * np.pi, amp.shape)
    spec = amp * np.exp(1j * ph)
    n = np.fft.irfft2(spec, s=(h, w)).astype(np.float32)
    lo, hi = np.percentile(n, [0.5, 99.5])
    return np.clip((n - lo) / (hi - lo), 0, 1).astype(np.float32)


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a + 1e-12), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def ease(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def blur(img, sigma):
    if sigma <= 0.05:
        return img
    return cv2.GaussianBlur(img, (0, 0), float(sigma))


def catmull(pts, n):
    """Spline Catmull-Rom por puntos (k,d) -> (n,d)."""
    pts = np.asarray(pts, np.float64)
    p = np.vstack([2 * pts[0] - pts[1], pts, 2 * pts[-1] - pts[-2]])
    segs = len(pts) - 1
    u = np.linspace(0, segs, n, endpoint=True)
    i = np.minimum(u.astype(int), segs - 1)
    t = (u - i)[:, None]
    p0, p1, p2, p3 = p[i], p[i + 1], p[i + 2], p[i + 3]
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                  + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)


def over(dst, src_rgb, alpha, x0, y0):
    """Compone src (h,w,3 float) con alpha (h,w) sobre dst en (x0,y0), con recorte."""
    H, W = dst.shape[:2]
    h, w = alpha.shape
    xa, ya = max(x0, 0), max(y0, 0)
    xb, yb = min(x0 + w, W), min(y0 + h, H)
    if xa >= xb or ya >= yb:
        return
    a = alpha[ya - y0:yb - y0, xa - x0:xb - x0, None]
    s = src_rgb[ya - y0:yb - y0, xa - x0:xb - x0]
    d = dst[ya:yb, xa:xb]
    d *= (1 - a)
    d += s * a
