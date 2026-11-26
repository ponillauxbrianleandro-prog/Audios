"""Motor 2D con apariencia 3D: ruido, cielo estrellado real, esferas sombreadas, anillos, bloom."""
import math
import numpy as np
from PIL import Image

W, H = 720, 1280          # resolución interna (se escala a 1080x1920)
rng0 = np.random.default_rng(7)

# ---------------------------------------------------------------- utilidades
def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)

def lerp(a, b, t):
    return a + (b - a) * t

def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * x * (x * (6 * x - 15) + 10)

def make_noise(size_w, size_h, octaves=5, base=4, pers=0.55, seed=1, wrap_v=False):
    """ruido de valor suave, periódico en horizontal (y vertical si wrap_v)"""
    rng = np.random.default_rng(seed)
    out = np.zeros((size_h, size_w), np.float32); amp = 1.0; tot = 0
    for o in range(octaves):
        n = base * 2 ** o; m = max(2, n // 2)
        g = rng.random((m + 1, n)).astype(np.float32)
        if wrap_v: g[m] = g[0]
        u = np.arange(size_w) * n / size_w; i0 = np.floor(u).astype(int); f = u - i0; f = f * f * (3 - 2 * f)
        gx = g[:, i0 % n] * (1 - f) + g[:, (i0 + 1) % n] * f
        v = np.arange(size_h) * m / size_h; j0 = np.floor(v).astype(int); fv = (v - j0)[:, None]; fv = fv * fv * (3 - 2 * fv)
        out += amp * (gx[j0] * (1 - fv) + gx[np.minimum(j0 + 1, m)] * fv)
        tot += amp; amp *= pers
    out /= tot
    return out

class Tex:
    """textura con muestreo bilineal periódico"""
    def __init__(self, a):
        a = np.asarray(a, np.float32)
        self.a = a if a.ndim == 3 else a[..., None]
        self.h, self.w = self.a.shape[:2]
    def __call__(self, u, v):
        x = u * self.w - 0.5; y = v * self.h - 0.5
        x0 = np.floor(x); y0 = np.floor(y); fx = (x - x0)[..., None]; fy = (y - y0)[..., None]
        x0 = x0.astype(np.int32); y0 = y0.astype(np.int32)
        xa, xb = x0 % self.w, (x0 + 1) % self.w; ya, yb = y0 % self.h, (y0 + 1) % self.h
        a = self.a
        r = (a[ya, xa] * (1 - fx) + a[ya, xb] * fx) * (1 - fy) + (a[yb, xa] * (1 - fx) + a[yb, xb] * fx) * fy
        return r if self.a.shape[2] > 1 else r[..., 0]

def palette1d(stops, n=512):
    """stops: [(pos 0..1, (r,g,b))] -> array n x 3"""
    p = np.array([s[0] for s in stops]); c = np.array([s[1] for s in stops], np.float32)
    x = np.linspace(0, 1, n)
    return np.stack([np.interp(x, p, c[:, k]) for k in range(3)], 1).astype(np.float32)

def pal_lookup(pal, x):
    n = len(pal); i = np.clip(x, 0, 1) * (n - 1)
    i0 = np.floor(i).astype(np.int32); f = (i - i0)[..., None]; i1 = np.minimum(i0 + 1, n - 1)
    return pal[i0] * (1 - f) + pal[i1] * f

def box_blur(a, r, passes=3):
    for _ in range(passes):
        for ax in (0, 1):
            c = np.cumsum(np.pad(a, [(r + 1, r) if k == ax else (0, 0) for k in range(a.ndim)], mode="edge"), axis=ax, dtype=np.float64)
            n = 2 * r + 1
            a = ((np.take(c, range(n, c.shape[ax]), axis=ax) - np.take(c, range(0, c.shape[ax] - n), axis=ax)) / n).astype(np.float32)
    return a

def resize(a, w, h, resample=Image.BICUBIC):
    chans = [np.asarray(Image.fromarray(a[..., k].astype(np.float32), "F").resize((w, h), resample)) for k in range(a.shape[2])]
    return np.stack(chans, 2)

def bloom(img, thr=0.55, strength=0.55, scale=4):
    h, w = img.shape[:2]
    s = img.reshape(h // scale, scale, w // scale, scale, 3).mean((1, 3))
    b = np.maximum(s - thr, 0)
    acc = np.zeros_like(b)
    for r, wgt in ((2, 0.5), (6, 0.35), (16, 0.25)):
        acc += box_blur(b, r, 2) * wgt
    return img + strength * resize(acc, w, h)

# ---------------------------------------------------------------- estrellas
BRIGHT = [  # AR(h), Dec(°), mag, tinte 0 blanco 1 azul 2 naranja 3 amarillo
 (6.7525,-16.716,-1.46,1),(6.3992,-52.696,-0.74,0),(14.261,19.182,-0.05,2),(14.660,-60.834,-0.01,3),(18.6156,38.784,0.03,1),
 (5.2782,45.998,0.08,3),(5.2423,-8.202,0.13,1),(7.6550,5.225,0.34,0),(1.6286,-57.237,0.46,1),(5.9195,7.407,0.50,2),
 (14.0637,-60.373,0.61,1),(19.8464,8.868,0.76,0),(12.4433,-63.099,0.76,1),(4.5987,16.509,0.85,2),(16.4901,-26.432,1.06,2),
 (13.4199,-11.161,0.97,1),(7.7553,28.026,1.14,3),(22.9608,-29.622,1.16,0),(20.6905,45.280,1.25,0),(12.7954,-59.689,1.25,1),
 (10.1395,11.967,1.35,1),(6.9771,-28.972,1.50,1),(7.5767,31.888,1.58,0),(12.5194,-57.113,1.64,2),(17.5601,-37.104,1.62,1),
 (5.4189,6.350,1.64,1),(5.4382,28.608,1.65,1),(9.2200,-69.717,1.67,0),(5.6036,-1.202,1.69,1),(5.6793,-1.943,1.77,1),
 (12.9005,55.960,1.76,0),(11.0621,61.751,1.79,3),(3.4054,49.861,1.79,3),(7.1399,-26.393,1.83,0),(17.6220,-42.998,1.87,3),
 (18.4029,-34.385,1.85,0),(8.3752,-59.510,1.86,3),(13.7923,49.313,1.86,1),(5.9921,44.948,1.90,0),(16.8111,-69.028,1.92,2),
 (6.6285,16.399,1.93,0),(20.4275,-56.735,1.94,1),(5.5334,-0.299,2.23,1),(2.5303,89.264,1.98,3),(13.3988,54.925,2.04,0),
 (22.1372,-46.961,1.74,1),(5.7959,-9.670,2.06,1),(2.1196,23.462,2.00,3),(17.5822,12.560,2.07,0),(0.1398,29.091,2.06,1),
 (0.7265,-17.987,2.04,3),(1.1622,35.621,2.05,2),(0.6751,56.537,2.24,2),(11.8177,14.572,2.14,0),(10.3329,19.842,2.28,3),
 (3.7914,24.105,2.9,1),(3.7466,24.367,3.6,1),(3.7236,23.948,3.8,1),(3.7690,24.053,4.3,1),
]
_TINT = {0: (1.0, 1.0, 1.0), 1: (0.78, 0.88, 1.0), 2: (1.0, 0.72, 0.55), 3: (1.0, 0.94, 0.75)}
GAL = np.array([[-0.0548755604, -0.8734370902, -0.4838350155],
                [0.4941094279, -0.4448296300, 0.7469822445],
                [-0.8676661490, -0.1980763734, 0.4559837762]])

def _build_stars():
    vs, mags, cols = [], [], []
    for ra, dec, m, t in BRIGHT:
        a, d = math.radians(ra * 15), math.radians(dec)
        vs.append((math.cos(d) * math.cos(a), math.cos(d) * math.sin(a), math.sin(d))); mags.append(m); cols.append(_TINT[t])
    n = 40000; r = np.random.default_rng(11)
    l = r.uniform(0, 2 * np.pi, n)
    uni = r.random(n) < 0.5
    b = np.where(uni, np.arcsin(r.uniform(-1, 1, n)), np.clip(r.laplace(0, 0.17, n), -1.4, 1.4))
    g = np.stack([np.cos(b) * np.cos(l), np.cos(b) * np.sin(l), np.sin(b)], 1)
    ic = g @ GAL   # = GAL.T @ g
    m = 3.4 + np.log10(r.random(n) * (10 ** (0.5 * 4.2) - 1) + 1) / 0.5
    tint = r.choice(4, n, p=[0.4, 0.3, 0.15, 0.15])
    vs += list(ic); mags += list(m); cols += [_TINT[int(k)] for k in tint]
    return np.array(vs, np.float32), np.array(mags, np.float32), np.array(cols, np.float32)
STAR_V, STAR_M, STAR_C = _build_stars()
_MWN = Tex(make_noise(512, 256, 6, 4, 0.6, seed=5, wrap_v=True))

def cam_dirs(cam, fov, w, h):
    """direcciones unitarias ICRS por pixel (h,w,3) para cámara (right,up,fwd)"""
    r, u, f = [np.asarray(x, np.float32) for x in cam]
    fl = (h / 2) / math.tan(math.radians(fov) / 2)
    X = ((np.arange(w) + 0.5 - w / 2) / fl).astype(np.float32); Y = ((h / 2 - np.arange(h) - 0.5) / fl).astype(np.float32)
    d = f[None, None] + X[None, :, None] * r[None, None] + Y[:, None, None] * u[None, None]
    return d / np.linalg.norm(d, axis=2, keepdims=True)

def milky_way(cam, fov, gain=1.0):
    """vía láctea difusa (baja resolución) -> (H,W,3)"""
    w, h = W // 3, H // 3
    d = cam_dirs(cam, fov, w, h); g = d @ GAL.T
    b = np.arcsin(np.clip(g[..., 2], -1, 1)); l = np.arctan2(g[..., 1], g[..., 0])
    n1 = _MWN((l / (2 * np.pi) * 2) % 1, (b + np.pi / 2) / np.pi * 2.0)
    n2 = _MWN((l / (2 * np.pi) * 6) % 1, (b + np.pi / 2) / np.pi * 6.0)
    band = np.exp(-(b / 0.17) ** 2) * (0.45 + 0.9 * n1) + 0.35 * np.exp(-(b / 0.5) ** 2) * n2
    bulge = np.exp(-(l / 0.9) ** 2) * np.exp(-(b / 0.35) ** 2)
    dust = smoothstep(0.45, 0.62, n2) * np.exp(-(b / 0.12) ** 2)
    I = np.clip(band * (1 - 0.8 * dust) + 1.1 * bulge * (1 - 0.6 * dust), 0, None) ** 1.5
    col = I[..., None] * (np.array([0.38, 0.52, 1.0], np.float32) * (1 - 0.5 * bulge[..., None]) + np.array([1.0, 0.62, 0.35], np.float32) * 0.6 * bulge[..., None])
    return resize(col * 0.20 * gain, W, H)

def star_layer(cam, fov, gain=1.0, vis=None, jitter=0.0, tw_seed=0):
    """estrellas del catálogo + campo débil. vis(py)->factor opcional por fila. devuelve (H,W,3)"""
    r, u, f = [np.asarray(x, np.float32) for x in cam]
    zc = STAR_V @ f; ok = zc > 0.05
    v = STAR_V[ok]; zc = zc[ok]; m = STAR_M[ok]; c = STAR_C[ok]
    fl = (H / 2) / math.tan(math.radians(fov) / 2)
    px = W / 2 + fl * (v @ r) / zc; py = H / 2 - fl * (v @ u) / zc
    inside = (px > -20) & (px < W + 20) & (py > -20) & (py < H + 20)
    px, py, m, c = px[inside], py[inside], m[inside], c[inside]
    A = (10 ** (-0.2 * (m - 1.0))).astype(np.float32)
    A = np.where(A < 0.32, 0.13 + 0.85 * A, A) * gain
    if vis is not None:
        A = A * vis(py)
    img = np.zeros((H, W, 3), np.float32)
    faint = A < 0.32
    # débiles: splat bilineal
    fx, fy, fa, fc = px[faint], py[faint], A[faint], c[faint]
    okf = (fx > 0) & (fx < W - 1) & (fy > 0) & (fy < H - 1)
    fx, fy, fa, fc = fx[okf], fy[okf], fa[okf], fc[okf]
    x0 = np.floor(fx).astype(int); y0 = np.floor(fy).astype(int); dx = fx - x0; dy = fy - y0
    flat = img.reshape(-1, 3)
    for ox, oy, wgt in ((0, 0, (1 - dx) * (1 - dy)), (1, 0, dx * (1 - dy)), (0, 1, (1 - dx) * dy), (1, 1, dx * dy)):
        np.add.at(flat, (y0 + oy) * W + (x0 + ox), (fa * wgt * 2.4)[:, None] * fc)
    # brillantes: sprite gaussiano + halo + espigas
    for x, y, a, col in zip(px[~faint], py[~faint], A[~faint], c[~faint]):
        s = 0.8 + 0.55 * min(a, 3.0); rad = int(5 + 9 * min(a, 3.0)); R = rad
        x0, y0 = int(round(x)), int(round(y))
        xs0, xs1, ys0, ys1 = max(x0 - R, 0), min(x0 + R + 1, W), max(y0 - R, 0), min(y0 + R + 1, H)
        if xs0 >= xs1 or ys0 >= ys1: continue
        X = np.arange(xs0, xs1)[None, :] - x; Y = np.arange(ys0, ys1)[:, None] - y
        d2 = X * X + Y * Y
        k = a * (np.exp(-d2 / (2 * s * s)) + 0.10 * np.exp(-d2 / (2 * (5 * s) ** 2)))
        if a > 0.8:
            L = 7 + 14 * min(a, 2.5)
            k += 0.28 * a * (np.exp(-Y * Y / 0.5) * np.exp(-np.abs(X) / L) + np.exp(-X * X / 0.5) * np.exp(-np.abs(Y) / L))
        img[ys0:ys1, xs0:xs1] += k[..., None] * col
    return img

def space_background(cam, fov, gain=1.0, mw=1.0):
    return milky_way(cam, fov, mw) + star_layer(cam, fov, gain)

# ---------------------------------------------------------------- esferas
def vnorm(v):
    v = np.asarray(v, float); return v / np.linalg.norm(v)

class SphereBody:
    """albedo(lon,lat,ctx)->(n,3). pole en coords de vista (x der, y arriba, z hacia el observador)"""
    def __init__(self, albedo, pole, lon_shift, atmo=(0.4, 0.6, 1.0), atmo_k=0.8, wrap=0.1, halo=0.06, limb=0.5,
                 ambient=0.02, sun=1.0, halo_col=None, halo_k=1.0):
        self.albedo, self.pole, self.lon_shift = albedo, vnorm(pole), lon_shift
        self.atmo = np.array(atmo, np.float32); self.atmo_k = atmo_k; self.wrap = wrap; self.halo = halo
        self.limb = limb; self.ambient = ambient; self.sun = sun
        self.halo_col = np.array(halo_col if halo_col is not None else atmo, np.float32); self.halo_k = halo_k

def _bbox(cx, cy, R):
    x0 = int(max(math.floor(cx - R), 0)); x1 = int(min(math.ceil(cx + R) + 1, W))
    y0 = int(max(math.floor(cy - R), 0)); y1 = int(min(math.ceil(cy + R) + 1, H))
    return x0, x1, y0, y1

def draw_sphere(img, cx, cy, R, L, body, ctx=None):
    """L: dirección de luz en coords de vista (unitaria)"""
    L = vnorm(L)
    Rb = R * (1 + body.halo) + 2
    x0, x1, y0, y1 = _bbox(cx, cy, Rb)
    if x1 <= x0 or y1 <= y0: return
    X = ((np.arange(x0, x1) + 0.5 - cx) / R).astype(np.float32)[None, :]
    Y = (-(np.arange(y0, y1) + 0.5 - cy) / R).astype(np.float32)[:, None]
    rr2 = X * X + Y * Y; rr = np.sqrt(rr2)
    nz = np.sqrt(np.maximum(1 - rr2, 0))
    pv = body.pole.astype(np.float32); a = np.array([1, 0, 0], np.float32); b = np.cross(pv, a).astype(np.float32)
    npole = np.clip(Y * pv[1] + nz * pv[2], -1, 1)
    lat = np.arcsin(npole)
    psi = np.arctan2(Y * b[1] + nz * b[2], X + 0 * Y)
    lon = psi + body.lon_shift
    cov = np.clip((1 - rr) * R + 0.5, 0, 1)
    inside = cov > 0
    out = img[y0:y1, x0:x1]
    if inside.any():
        alb = body.albedo(lon, lat, ctx, rr=rr, R=R)
        d = X * L[0] + Y * L[1] + nz * L[2]
        wr = body.wrap
        lit = np.clip((d + wr) / (1 + wr), 0, 1); lit = lit * lit * (3 - 2 * lit) * 0.35 + lit * 0.65
        ld = 1 - body.limb * (1 - nz ** 0.55)
        col = alb * (lit * body.sun * ld + body.ambient)[..., None]
        fres = (1 - nz) ** 3.0
        rim = fres * np.clip(d * 0.9 + 0.45, 0, 1.2)
        col = col + (rim * body.atmo_k)[..., None] * body.atmo
        out[:] = out * (1 - cov[..., None]) + col * cov[..., None]
    if body.halo > 0:
        dd = np.maximum(rr - 1, 0)
        dirx = X / np.maximum(rr, 1e-4); diry = Y / np.maximum(rr, 1e-4)
        lm = np.clip(0.18 + 0.82 * (dirx * L[0] + diry * L[1]) * 0.5 + 0.35 * (L[2] > 0) * 0.5, 0.05, 1.0)
        g = np.exp(-dd / (body.halo * 0.38)) * (1 - cov) * 0.7 + np.exp(-dd / (body.halo * 0.12)) * (1 - cov) * 0.8
        g = g * (rr < 1 + body.halo * 3) * lm * body.halo_k
        out += g[..., None] * body.halo_col

def ring_profile():
    n = 1024; r = np.linspace(1.0, 2.4, n)
    al = np.zeros(n, np.float32); col = np.zeros((n, 3), np.float32)
    nz = make_noise(n, 1, 6, 8, 0.6, seed=3)[0]
    def seg(a, b, alpha, c):
        m = (r >= a) & (r < b); al[m] = alpha; col[m] = c
    seg(1.11, 1.236, 0.06, (0.4, 0.37, 0.33)); seg(1.239, 1.527, 0.20, (0.5, 0.45, 0.4))
    seg(1.527, 1.951, 0.88, (0.86, 0.76, 0.62)); seg(1.951, 2.025, 0.05, (0.5, 0.45, 0.4))
    seg(2.025, 2.27, 0.58, (0.78, 0.72, 0.64))
    al *= (0.55 + 0.9 * nz) ; al = np.clip(al, 0, 0.97)
    for a, b in ((2.214, 2.221), (2.262, 2.268), (1.74, 1.755), (1.82, 1.83)):
        al[(r >= a) & (r < b)] *= 0.12
    col *= (0.8 + 0.4 * nz[:, None])
    # bordes suaves
    return r, al, col

_RING = ring_profile()

def ring_layer(cx, cy, R, L, pole, sh_planet=True):
    """devuelve bbox y (rgb, alpha, t) donde t>0 indica anillo por delante del planeta"""
    Rb = R * 2.4
    x0, x1, y0, y1 = _bbox(cx, cy, Rb)
    if x1 <= x0 or y1 <= y0: return None
    X = ((np.arange(x0, x1) + 0.5 - cx) / R).astype(np.float32)[None, :]
    Y = (-(np.arange(y0, y1) + 0.5 - cy) / R).astype(np.float32)[:, None]
    p = vnorm(pole).astype(np.float32); L = vnorm(L).astype(np.float32)
    pz = p[2] if abs(p[2]) > 0.035 else 0.035 * (1 if p[2] >= 0 else -1)
    t = -(p[1] * Y) / pz + 0 * X
    rad = np.sqrt(X * X + Y * Y + t * t)
    rs, al, col = _RING
    idx = np.clip((rad - 1.0) / 1.4, 0, 0.9999) * (len(rs) - 1)
    i0 = idx.astype(np.int32); f = idx - i0
    a = al[i0] * (1 - f) + al[np.minimum(i0 + 1, len(rs) - 1)] * f
    c = col[i0] * (1 - f)[..., None] + col[np.minimum(i0 + 1, len(rs) - 1)] * f[..., None]
    a = a * ((rad > 1.1) & (rad < 2.3))
    # sombra del planeta
    P = np.stack([X + 0 * t, Y + 0 * t, t], -1)
    bb = P @ L; cc = rad * rad - 1
    disc = bb * bb - cc
    shadow = (disc > 0) & (bb < 0) & (cc > 0)
    sun_side = abs(L @ p)
    lum = (0.30 + 0.80 * sun_side) * np.where(shadow, 0.05, 1.0)
    # ligera luz difusa en el borde de la sombra
    rgb = c * lum[..., None] * 1.5
    # transparencia dependiente del ángulo de visión
    a = a * (0.45 + 0.55 * min(1, abs(pz) * 3 + 0.2))
    return (x0, x1, y0, y1), rgb.astype(np.float32), a.astype(np.float32), t, X, Y

def draw_planet_with_rings(img, cx, cy, R, L, body, ctx=None):
    rl = ring_layer(cx, cy, R, L, body.pole)
    if rl is not None:
        (x0, x1, y0, y1), rgb, a, t, X, Y = rl
        out = img[y0:y1, x0:x1]
        back = a * (t < 0)
        out[:] = out * (1 - back[..., None]) + rgb * back[..., None]
    draw_sphere(img, cx, cy, R, L, body, ctx)
    if rl is not None:
        front = a * (t >= 0)
        out = img[y0:y1, x0:x1]
        out[:] = out * (1 - front[..., None]) + rgb * front[..., None]

# ---------------------------------------------------------------- post
_VIG = None
def post(img, grain=0.012, vig=0.35, seed=0, bloom_k=0.5):
    global _VIG
    img = bloom(img, 0.5, bloom_k)
    if _VIG is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
        _VIG = (1 - vig * np.clip(d / 2, 0, 1) ** 1.2)[..., None]
    img = img * _VIG
    # curva filmica suave
    img = np.maximum(img, 0)
    img = 1 - np.exp(-img * 1.45); img = img ** (1 / 1.12)
    rng = np.random.default_rng(seed)
    img = img + rng.normal(0, grain, img.shape[:2]).astype(np.float32)[..., None]
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
