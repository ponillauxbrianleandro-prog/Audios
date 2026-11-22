"""Efectos de la selva andina lluviosa: hojas de primer plano que reciben una gota (se doblan) y la dejan caer
(rebotan con amortiguación), goteo con salpicaduras y rayos de sol entre la bruma.

Cada fábrica devuelve fx(img, cam, t, W, H, k, zf, ap) para el hook `shot["fx"]` de engine.frame.
Todo en coordenadas de pantalla (fracciones de W y H) para poder poner las hojas pegadas a la cámara.
"""
import numpy as np
import cv2

_G = 9.0   # gravedad en alturas de pantalla / s^2 (la caída se ve rápida y pesada)


def _blur(rgb, a, sig):
    if sig > 0.3:
        rgb = cv2.GaussianBlur(rgb, (0, 0), sig)
        a = cv2.GaussianBlur(a, (0, 0), sig)
    return rgb, a


def _comp(img, rgb, a):
    img[:] = img * (1 - a[..., None]) + rgb


def _gota(lay, la, x, y, r, stretch=1.0, alpha=0.9, tint=(0.86, 0.95, 1.0)):
    """Gota con borde oscuro (refracción), centro claro y brillo especular."""
    ax, ay = max(1, int(r)), max(1, int(r * stretch))
    c = (int(x * 16), int(y * 16))
    cv2.ellipse(lay, c, (ax * 16, ay * 16), 0, 0, 360, tuple(float(v) * 0.45 for v in tint), -1, cv2.LINE_AA, 4)
    cv2.ellipse(lay, (c[0] - int(ax * 2), c[1] + int(ay * 3)), (int(ax * 12), int(ay * 11)), 0, 0, 360,
                tuple(float(v) * 0.95 for v in tint), -1, cv2.LINE_AA, 4)
    cv2.ellipse(la, c, (ax * 16, ay * 16), 0, 0, 360, alpha, -1, cv2.LINE_AA, 4)
    cv2.circle(lay, (c[0] - int(ax * 6), c[1] - int(ay * 6)), max(8, int(ax * 4)), (1.2, 1.2, 1.2), -1, cv2.LINE_AA, 4)


def hoja_con_gota(base, ang, largo, ancho, sigma=3.0, T=3.4, fase=0.0, carga=0.55, colores=None, flip=False, gota_r=0.017):
    """Hoja ovada pegada a la cámara.
    base=(x,y) fracción de pantalla; ang=grados (0 = hacia la derecha, 90 = hacia arriba); largo/ancho en fracción de W.
    La gota crece en la punta (la hoja se va doblando), se suelta, cae acelerando y la hoja rebota."""
    dark, light = colores or ((0.12, 0.26, 0.10), (0.36, 0.56, 0.24))
    dark, light = np.array(dark, np.float32), np.array(light, np.float32)

    def fx(img, cam, t, W, H, k, zf, ap):
        lay = np.zeros((H, W, 3), np.float32)
        la = np.zeros((H, W), np.float32)
        u = ((t + fase * T) % T) / T                  # 0..1 dentro del ciclo
        cycle = int((t + fase * T) // T)
        t_rel = u * T
        t_grow, t_drop = 0.0, 0.66 * T
        if t_rel < t_drop:
            g = (t_rel / t_drop)
            g = g * g * (3 - 2 * g)                   # la gota crece suave
            falling = None
        else:
            g = 0.0
            falling = t_rel - t_drop
        # carga de la hoja (se dobla) y rebote tras soltar la gota
        carga_act = carga * (g if falling is None else 0.0)
        rebote = 0.0
        if falling is not None:
            rebote = -carga * 0.9 * np.exp(-2.6 * falling) * np.cos(11.0 * falling) * 0.6
        # la hoja nunca está quieta: ondea con el viento y la lluvia
        viento = 0.035 * np.sin(t * 1.3 + fase * 9) + 0.015 * np.sin(t * 3.1 + fase * 3)
        n = 28
        s = np.linspace(0, 1, n)
        a0 = np.radians(ang) * (-1 if flip else 1) if False else np.radians(ang)
        d = np.array([np.cos(a0), -np.sin(a0)])        # +y de pantalla va hacia abajo
        nrm = np.array([-d[1], d[0]])
        bend = (0.28 + carga_act + rebote + viento)    # cuánto cae la punta (radianes de arqueo acumulado)
        dirs = a0 - bend * (s ** 1.4)                  # el ángulo disminuye hacia la punta: la hoja se arquea hacia abajo
        px = np.cumsum(np.cos(dirs)) / n * largo * W
        py = -np.cumsum(np.sin(dirs)) / n * largo * W
        px, py = base[0] * W + px, base[1] * H + py
        half = ancho * W * 0.5 * np.sin(np.pi * np.clip(s, 0, 1) ** 0.75) ** 0.85
        # normal por tramo
        tx, ty = np.gradient(px), np.gradient(py)
        tn = np.hypot(tx, ty) + 1e-6
        nx, ny = -ty / tn, tx / tn
        L = np.stack([px + nx * half, py + ny * half], 1)
        R = np.stack([px - nx * half, py - ny * half], 1)[::-1]
        poly = np.vstack([L, R])
        P = (poly * 16).astype(np.int32).reshape(-1, 1, 2)
        cv2.fillPoly(lay, [P], tuple(float(v) for v in dark * 0.85), cv2.LINE_AA, 4)
        cv2.fillPoly(la, [P], 1.0, cv2.LINE_AA, 4)
        # media hoja iluminada + nervadura + nervios secundarios
        Lh = np.stack([px + nx * half * 0.95, py + ny * half * 0.95], 1)
        Mid = np.stack([px, py], 1)[::-1]
        Pl = (np.vstack([Lh, Mid]) * 16).astype(np.int32).reshape(-1, 1, 2)
        cv2.fillPoly(lay, [Pl], tuple(float(v) for v in light * 0.90), cv2.LINE_AA, 4)
        cv2.polylines(lay, [(np.stack([px, py], 1) * 16).astype(np.int32).reshape(-1, 1, 2)], False,
                      tuple(float(v) * 1.15 for v in light), max(1, int(2 * k * 3)), cv2.LINE_AA, 4)
        for i in range(3, n - 2, 2):
            for sd in (-1, 1):
                ex, ey = px[i] + nx[i] * half[i] * 0.85 * sd + tx[i] * 0.9, py[i] + ny[i] * half[i] * 0.85 * sd + ty[i] * 0.9
                cv2.line(lay, (int(px[i] * 16), int(py[i] * 16)), (int(ex * 16), int(ey * 16)), tuple(float(v) * 1.05 for v in light * (1.0 if sd < 0 else 0.8)),
                         1, cv2.LINE_AA, 4)
        # brillo húmedo en el lado iluminado
        cv2.polylines(lay, [(np.stack([px + nx * half * 0.45, py + ny * half * 0.45], 1) * 16).astype(np.int32).reshape(-1, 1, 2)], False,
                      (0.95, 1.0, 1.0), 1, cv2.LINE_AA, 4)
        tipx, tipy = px[-1], py[-1]
        # gotas chicas permanentes en el limbo
        rr = np.random.default_rng(int(fase * 1000) + 3)
        for _ in range(5):
            j = int(rr.integers(4, n - 4))
            _gota(lay, la, px[j] + nx[j] * half[j] * rr.uniform(-0.6, 0.6), py[j] + ny[j] * half[j] * rr.uniform(-0.6, 0.6),
                  max(1.0, 0.0035 * W * rr.uniform(0.6, 1.0)), alpha=0.8)
        # gota grande en la punta o en caída
        r0 = gota_r * W
        if falling is None:
            if g > 0.02:
                _gota(lay, la, tipx, tipy + r0 * (0.4 + 0.6 * g) * 0.8, r0 * (0.25 + 0.75 * g), stretch=1.0 + 0.35 * g * g)
        else:
            v = _G * H * falling
            dy = 0.5 * _G * H * falling * falling
            if tipy + dy < H + 40:
                _gota(lay, la, tipx + 2.0 * k, tipy + r0 * 0.8 + dy, r0 * 0.8, stretch=1.0 + min(1.8, v / H * 0.5))
        # profundidad: desenfoque grande porque está pegada a la cámara
        lay, la = _blur(lay * la[..., None] if False else lay, la, sigma * k * 2.6)
        # reponer color no premultiplicado: se dibujó sin premultiplicar, así que normalizar por alfa
        rgb = lay / np.maximum(la[..., None], 1e-3) * la[..., None]
        rgb = np.clip(rgb, 0, 1.4)
        _comp(img, rgb, la)
    return fx


def goteo(n=9, y_suelo=(0.62, 0.92), seed=0, velocidad=1.0, alpha=0.55):
    """Gotas que caen de las hojas del plano medio, con salpicadura y ondas en el suelo."""
    rng = np.random.default_rng(seed)
    P = [dict(x=rng.uniform(0.08, 0.92), y0=rng.uniform(0.10, 0.45), yg=rng.uniform(*y_suelo), per=rng.uniform(1.6, 3.4),
              ph=rng.uniform(0, 3.4), r=rng.uniform(0.9, 1.9)) for _ in range(n)]

    def fx(img, cam, t, W, H, k, zf, ap):
        lay = np.zeros((H, W, 3), np.float32)
        la = np.zeros((H, W), np.float32)
        for p in P:
            tt = (t + p["ph"]) % p["per"]
            tf = np.sqrt(2 * (p["yg"] - p["y0"]) / (_G * velocidad))      # tiempo de caída
            if tt < 0.5:                                               # cuelga y engorda en la hoja
                s = tt / 0.5
                x, y = p["x"] * W, p["y0"] * H
                cv2.circle(lay, (int(x), int(y)), max(1, int(p["r"] * 1.3 * k * 2.6 * (0.4 + 0.6 * s))), (0.9, 0.97, 1.0), -1, cv2.LINE_AA)
                cv2.circle(la, (int(x), int(y)), max(1, int(p["r"] * 1.3 * k * 2.6 * (0.4 + 0.6 * s))), alpha, -1, cv2.LINE_AA)
            elif tt < 0.5 + tf:                                          # cae
                f = tt - 0.5
                y = (p["y0"] + 0.5 * _G * velocidad * f * f) * H
                x = p["x"] * W
                ln = min(0.06 * H, 0.012 * H + _G * velocidad * f * H * 0.02)
                cv2.line(lay, (int(x), int(y - ln)), (int(x), int(y)), (0.95, 0.99, 1.0), max(1, int(p["r"] * k * 2.2)), cv2.LINE_AA)
                cv2.line(la, (int(x), int(y - ln)), (int(x), int(y)), alpha, max(1, int(p["r"] * k * 2.2)), cv2.LINE_AA)
            elif tt < 0.5 + tf + 1.1:                                   # salpicadura + ondas
                f = tt - 0.5 - tf
                x, y = p["x"] * W, p["yg"] * H
                rad = (6 + 70 * f) * k * p["r"]
                fade = (1 - f / 1.1) ** 1.5
                cv2.ellipse(lay, (int(x), int(y)), (int(rad), max(1, int(rad * 0.28))), 0, 0, 360, (0.95, 0.99, 1.0), 1, cv2.LINE_AA)
                cv2.ellipse(la, (int(x), int(y)), (int(rad), max(1, int(rad * 0.28))), 0, 0, 360, alpha * fade * 0.8, 1, cv2.LINE_AA)
                if f < 0.25:                                           # corona de salpicadura
                    for a in np.linspace(0.3, np.pi - 0.3, 5):
                        h_ = 16 * k * np.sin(np.pi * f / 0.25) * p["r"]
                        cv2.circle(lay, (int(x + np.cos(a) * rad * 0.9), int(y - np.sin(a) * h_)), 1, (1, 1, 1), -1)
                        cv2.circle(la, (int(x + np.cos(a) * rad * 0.9), int(y - np.sin(a) * h_)), 1, alpha, -1)
        lay, la = _blur(lay, la, 0.6 * k * 2.0)
        _comp(img, np.clip(lay, 0, 1.2) * la[..., None], la)
    return fx


def rayos(n=5, intensidad=0.12, seed=1, color=(1.0, 0.97, 0.88), ang=-0.30):
    """Rayos de sol oblicuos entre la bruma; cada uno respira a su ritmo."""
    rng = np.random.default_rng(seed)
    R = [dict(x=rng.uniform(-0.1, 1.1), w=rng.uniform(0.05, 0.14), a=rng.uniform(0.5, 1.0), per=rng.uniform(5, 10), ph=rng.uniform(0, 6.28))
         for _ in range(n)]

    def fx(img, cam, t, W, H, k, zf, ap):
        lay = np.zeros((H, W), np.float32)
        for r in R:
            amp = r["a"] * (0.65 + 0.35 * np.sin(2 * np.pi * t / r["per"] + r["ph"]))
            x0 = (r["x"] + 0.02 * np.sin(t * 0.2 + r["ph"])) * W
            dx = ang * H
            w = r["w"] * W
            pts = np.array([[x0 - w * 0.3, 0], [x0 + w * 0.3, 0], [x0 + dx + w, H], [x0 + dx - w, H]], np.float32)
            cv2.fillPoly(lay, [(pts * 16).astype(np.int32).reshape(-1, 1, 2)], float(amp), cv2.LINE_AA, 4)
        lay = cv2.GaussianBlur(lay, (0, 0), 22 * k * 2.0)
        fade = np.linspace(1.0, 0.25, H, dtype=np.float32)[:, None]
        img += (lay * fade * intensidad)[..., None] * np.array(color, np.float32)
    return fx
