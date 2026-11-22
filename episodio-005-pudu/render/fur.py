"""Pelaje procedural: hebras que siguen la anatomía, mechones, puntas oscuras y silueta esponjosa.

Se engancha en creature.render (solo si spec["fur"] existe):
  field()  -> textura de hebras (convolución de línea integral sobre ruido, a lo largo de un campo de flujo del pelo);
  fringe() -> borde irregular del alfa y pelos de guarda semitransparentes que salen de la silueta.
El flujo se define en coordenadas de reposo del animal, así que no resbala cuando el animal se mueve.
"""
import numpy as np
import cv2
from util import smoothstep

NB = 12  # direcciones cuantizadas del flujo


def flujo(cam, ch, shh, rp, N, ancho_cabeza=0.40, nose=(1.15, 0.10, 0.0), down=0.7, back=(-1.0, -0.30, 0.0), vy=(0.22, 0.10)):
    """Dirección 2D (px) del pelo en cada píxel enmascarado. rp = posición en reposo (n,3)."""
    n = len(rp)
    nose = np.array(nose, float)
    head = 0.55 * smoothstep(ancho_cabeza, ancho_cabeza + 0.12, rp[:, 0])
    back = np.tile(np.array(back, float), (n, 1))
    rad = rp - nose
    rad /= np.linalg.norm(rad, axis=1, keepdims=True) + 1e-9
    rad[:, 0] -= 0.60                                         # en la cabeza el pelo se abre apenas y se tumba hacia atrás
    Fa = back * (1 - head)[:, None] + rad * head[:, None]
    Fa[:, 1] -= down * smoothstep(vy[0], vy[1], rp[:, 1])         # el vientre cae hacia abajo
    Fw = np.stack([Fa[:, 0] * ch - Fa[:, 2] * shh, Fa[:, 1], Fa[:, 0] * shh + Fa[:, 2] * ch], 1)
    Fc = cam.to_cam(Fw)
    Fc = Fc - 0.45 * (Fc * N).sum(1, keepdims=True) * N       # proyección parcial al plano tangente: evita polos radiales
    return Fc[:, 0], -Fc[:, 1]


def _lic(noise, bins, L):
    out = np.zeros_like(noise)
    ks = 2 * L + 1
    for k in range(NB):
        m = bins == k
        if not m.any():
            continue
        th = k * np.pi / NB
        ker = np.zeros((ks, ks), np.float32)
        cv2.line(ker, (int(round(L - L * np.cos(th))), int(round(L - L * np.sin(th)))),
                 (int(round(L + L * np.cos(th))), int(round(L + L * np.sin(th)))), 1.0, 1)
        ker /= ker.sum()
        out[m] = cv2.filter2D(noise, -1, ker)[m]
    return out


def field(h, w, yy, xx, fx, fy, sc, ss, fur, seed=3):
    """Devuelve (s1, s2) por píxel: hebra fina y mechón grueso, normalizadas (media 0, desvío 1)."""
    FX = np.zeros((h, w), np.float32)
    FY = np.zeros((h, w), np.float32)
    FX[yy, xx], FY[yy, xx] = fx, fy
    FX = cv2.GaussianBlur(FX, (0, 0), 7.0 * ss)
    FY = cv2.GaussianBlur(FY, (0, 0), 7.0 * ss)
    ang = np.arctan2(FY, FX)
    bins = (((ang % np.pi) / np.pi) * NB + 0.5).astype(np.int32) % NB
    rng = np.random.default_rng(seed)
    n1 = rng.standard_normal((h, w)).astype(np.float32)
    n1 = cv2.GaussianBlur(n1, (0, 0), 0.75 * ss)
    n2 = cv2.GaussianBlur(rng.standard_normal((h, w)).astype(np.float32), (0, 0), 1.6 * ss)
    L1 = max(3, int(0.0085 * sc * fur["len"]))
    L2 = max(5, int(0.016 * sc * fur["len"]))
    s1 = _lic(n1, bins, L1)
    s2 = _lic(n2, bins, L2)
    s1 = (s1 - s1[yy, xx].mean()) / (s1[yy, xx].std() + 1e-6)
    s2 = (s2 - s2[yy, xx].mean()) / (s2[yy, xx].std() + 1e-6)
    return s1[yy, xx], s2[yy, xx]


def fringe(rgb, a, sc, ss, fur, seed=5):
    """Silueta esponjosa: borde irregular + pelos de guarda. rgb/a a resolución de trabajo; devuelve (rgb, a)."""
    h, w = a.shape
    rng = np.random.default_rng(seed)
    ab = cv2.GaussianBlur(a, (0, 0), 2.4 * ss)
    nz = cv2.GaussianBlur(rng.standard_normal((h, w)).astype(np.float32), (0, 0), 0.9 * ss)
    nz /= nz.std() + 1e-6
    a2 = np.clip((ab - 0.40 + 0.11 * nz) * 4.0, 0, 1) * np.maximum(a, cv2.GaussianBlur(a, (0, 0), 1.2 * ss) > 0.2)
    a2 = np.maximum(a2, a * 0.9)
    # pelos de guarda
    gx = cv2.Sobel(ab, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(ab, cv2.CV_32F, 0, 1, ksize=3)
    gn = np.sqrt(gx * gx + gy * gy) + 1e-6
    inner = (a > 0.55).astype(np.uint8)
    edge = inner & (1 - cv2.erode(inner, np.ones((3, 3), np.uint8)))
    edge[:3], edge[-3:], edge[:, :3], edge[:, -3:] = 0, 0, 0, 0
    ys, xs = np.nonzero(edge)
    hair_a = np.zeros((h, w), np.uint8)
    hair_c = np.zeros((h, w, 3), np.uint8)
    if len(ys):
        n = min(5000, int(len(ys) * 0.9 * (0.4 + fur["len"])))
        pick = rng.integers(0, len(ys), n)
        Lh = 0.0065 * sc * fur["len"]
        src = np.clip(rgb, 0, 1)
        for i in pick:
            y, x = ys[i], xs[i]
            dx, dy = -gx[y, x] / gn[y, x], -gy[y, x] / gn[y, x]
            ln = Lh * rng.uniform(0.35, 1.25)
            cx, cy = rng.normal(0, 0.35), rng.normal(0, 0.35)          # curvatura
            p0 = (x - dx * 2, y - dy * 2)
            p1 = (x + (dx + cx) * ln * 0.5, y + (dy + cy) * ln * 0.5)
            p2 = (x + (dx + 1.6 * cx) * ln, y + (dy + 1.6 * cy) * ln)
            sx, sy = int(np.clip(x - dx * 16, 0, w - 1)), int(np.clip(y - dy * 16, 0, h - 1))
            col = src[sy, sx] * rng.uniform(0.78, 1.10)
            c8 = tuple(int(np.clip(v * 255, 0, 255)) for v in col)
            pts = np.array([p0, p1, p2], np.float32).round().astype(np.int32).reshape(-1, 1, 2)
            cv2.polylines(hair_a, [pts], False, 255, 1, cv2.LINE_AA)
            cv2.polylines(hair_c, [pts], False, c8, 1, cv2.LINE_AA)
    ha = hair_a.astype(np.float32) / 255.0 * 0.42
    hc = hair_c.astype(np.float32) / 255.0 / np.maximum(hair_a.astype(np.float32) / 255.0, 1e-3)[..., None]
    wh = np.clip(ha - a2, 0, 1)
    a_out = np.clip(a2 + wh, 0, 1)
    rgb_out = (rgb * (a2 / np.maximum(a_out, 1e-3))[..., None] + np.clip(hc, 0, 1.4) * (wh / np.maximum(a_out, 1e-3))[..., None])
    return rgb_out.astype(np.float32), a_out.astype(np.float32)
