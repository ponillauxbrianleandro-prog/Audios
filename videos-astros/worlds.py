"""Texturas procedurales de cuerpos y escena 'desde dentro' (cielo + suelo) para cada mundo."""
import math
import numpy as np
from render_lib import *
import astro
from render_lib import _bbox

TAU = 2 * math.pi
_cache = {}

def cached(key, fn):
    if key not in _cache: _cache[key] = fn()
    return _cache[key]

def NZ(name, w=1024, h=512, octv=6, base=4, pers=0.55, seed=1, wrap_v=False):
    return cached(("nz", name), lambda: Tex(make_noise(w, h, octv, base, pers, seed, wrap_v)))

# ------------------------------------------------------------------ gigantes gaseosos
JUP_PAL = palette1d([
    (0.00, (0.50, 0.52, 0.55)), (0.10, (0.62, 0.58, 0.52)), (0.17, (0.86, 0.78, 0.66)), (0.25, (0.62, 0.40, 0.27)),
    (0.30, (0.90, 0.82, 0.68)), (0.36, (0.70, 0.43, 0.27)), (0.40, (0.78, 0.50, 0.32)), (0.445, (0.95, 0.88, 0.74)),
    (0.50, (0.97, 0.90, 0.76)), (0.555, (0.93, 0.80, 0.62)), (0.595, (0.62, 0.38, 0.24)), (0.65, (0.88, 0.76, 0.62)),
    (0.70, (0.68, 0.43, 0.28)), (0.75, (0.93, 0.85, 0.70)), (0.80, (0.66, 0.44, 0.30)), (0.87, (0.88, 0.80, 0.68)),
    (0.93, (0.62, 0.58, 0.55)), (1.00, (0.48, 0.5, 0.55))])
SAT_PAL = palette1d([
    (0.0, (0.55, 0.55, 0.58)), (0.12, (0.70, 0.66, 0.58)), (0.25, (0.86, 0.76, 0.56)), (0.38, (0.78, 0.66, 0.46)),
    (0.48, (0.92, 0.82, 0.60)), (0.58, (0.82, 0.70, 0.50)), (0.70, (0.90, 0.80, 0.58)), (0.82, (0.76, 0.66, 0.48)),
    (0.92, (0.72, 0.68, 0.62)), (1.0, (0.55, 0.58, 0.62))])
NEP_PAL = palette1d([
    (0.0, (0.10, 0.22, 0.62)), (0.2, (0.14, 0.32, 0.82)), (0.38, (0.12, 0.28, 0.76)), (0.5, (0.20, 0.42, 0.92)),
    (0.62, (0.12, 0.30, 0.80)), (0.8, (0.16, 0.34, 0.86)), (1.0, (0.10, 0.22, 0.62))])

def _wrapd(a):
    return (a + math.pi) % TAU - math.pi

def jupiter_albedo(lon, lat, ctx=None, rr=None, R=None):
    n1 = NZ("j1", seed=2); n2 = NZ("j2", 1024, 512, 5, 6, 0.6, 3); det = NZ("jdet", 512, 512, 5, 8, 0.6, 4)
    u = lon / TAU; v = (lat + math.pi / 2) / math.pi
    sh = ctx.get("shear", 0.0) if ctx else 0.0
    u = u + sh * np.sin(lat * 5.0)
    warp = (n1(u * 2, v * 1.0) - 0.5) * 0.16 + (n1(u * 9, v * 4.0) - 0.5) * 0.06
    eddy = np.exp(-((np.sin(lat * 9.0)) ** 2) * 6)
    latn = v + warp * (0.35 + 0.9 * eddy)
    col = pal_lookup(JUP_PAL, latn)
    streak = n2(u * 3 + n1(u * 4, v * 8) * 0.6, v * 22)
    col = col * (0.78 + 0.44 * streak)[..., None]
    col = col * (0.90 + 0.2 * det(u * 14, v * 7))[..., None]
    fine = n2(u * 24 + n1(u * 30, v * 60) * 0.5, v * 90) - 0.5
    col = col * (1 + 0.28 * fine * (0.5 + 0.5 * eddy))[..., None] * (0.94 + 0.12 * det(u * 70, v * 35))[..., None]
    # Gran Mancha Roja
    lon0, lat0 = 1.6, math.radians(-22)
    dx = _wrapd(lon - lon0) * np.cos(lat); dy = lat - lat0
    e = (dx / 0.22) ** 2 + (dy / 0.115) ** 2; ee = np.sqrt(e)
    swirl = 0.5 + 0.5 * np.sin(np.arctan2(dy / 0.115, dx / 0.22) * 2 + ee * 7)
    spot = np.exp(-e * 1.1)
    grs = np.array([0.80, 0.36, 0.22], np.float32)
    col = col * (1 - spot[..., None] * 0.95) + (grs * (0.80 + 0.35 * swirl)[..., None] * 1.0) * spot[..., None] * 0.95
    ring = np.exp(-((ee - 1.35) / 0.28) ** 2)
    col = col * (1 - ring[..., None] * 0.4) + np.array([0.95, 0.9, 0.82], np.float32) * ring[..., None] * 0.4
    for (lo, la, s) in ((3.4, 0.55, 0.05), (4.1, 0.62, 0.04), (0.2, -0.62, 0.05), (5.3, 0.38, 0.035), (2.6, -0.85, 0.04), (4.9, -0.33, 0.04)):
        d2 = ((_wrapd(lon - lo) * np.cos(lat)) / (s * 1.6)) ** 2 + ((lat - la) / s) ** 2
        o = np.exp(-d2 * 1.2)
        col = col * (1 - o[..., None] * 0.7) + np.array([0.97, 0.94, 0.88], np.float32) * o[..., None] * 0.7
    return col

def saturn_albedo(lon, lat, ctx=None, rr=None, R=None):
    n1 = NZ("j1", seed=2); n2 = NZ("j2", 1024, 512, 5, 6, 0.6, 3)
    u = lon / TAU; v = (lat + math.pi / 2) / math.pi
    warp = (n1(u * 2, v) - 0.5) * 0.05 + (n1(u * 8, v * 4) - 0.5) * 0.015
    col = pal_lookup(SAT_PAL, v + warp)
    return col * (0.92 + 0.16 * n2(u * 2, v * 30))[..., None]

def neptune_albedo(lon, lat, ctx=None, rr=None, R=None):
    n1 = NZ("j1", seed=2); n2 = NZ("j2", 1024, 512, 5, 6, 0.6, 3)
    u = lon / TAU; v = (lat + math.pi / 2) / math.pi
    warp = (n1(u * 2, v) - 0.5) * 0.08
    col = pal_lookup(NEP_PAL, v + warp) * (0.9 + 0.2 * n2(u * 2, v * 25))[..., None]
    cir = np.clip(n2(u * 5, v * 40) - 0.62, 0, 1) * 4 * np.exp(-((lat + 0.5) / 0.35) ** 2)
    col = col + cir[..., None] * np.array([0.7, 0.8, 1.0], np.float32) * 0.8
    gds = np.exp(-(((_wrapd(lon - 2.0)) * np.cos(lat) / 0.2) ** 2 + ((lat + 0.35) / 0.1) ** 2))
    return col * (1 - 0.45 * gds[..., None])

# ------------------------------------------------------------------ superficies de lunas / Marte
def _craters(h, w, n, rng, rmin=2, rmax=20):
    hm = np.zeros((h, w), np.float32)
    for _ in range(n):
        cx, cy = rng.uniform(0, w), rng.uniform(0, h); r = rmin * (rmax / rmin) ** (rng.random() ** 2)
        x0, x1 = int(cx - r * 1.4), int(cx + r * 1.4) + 1; y0, y1 = max(int(cy - r * 1.4), 0), min(int(cy + r * 1.4) + 1, h)
        if y1 <= y0: continue
        xs = np.arange(x0, x1)[None, :]; ys = np.arange(y0, y1)[:, None]
        d = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2) / r
        prof = np.where(d < 1, -(1 - d ** 2) * 0.8 * 0.5, 0) + 0.12 * np.exp(-((d - 1.05) / 0.15) ** 2)
        idx = xs % w
        hm[y0:y1][:, idx[0]] += prof if False else 0
        np.add.at(hm, (np.broadcast_to(ys, prof.shape), np.broadcast_to(idx, prof.shape)), prof)
    return hm

def _shade_height(hm, k=3.0):
    gx = np.roll(hm, -1, 1) - np.roll(hm, 1, 1); gy = np.roll(hm, -1, 0) - np.roll(hm, 1, 0)
    return np.clip(1 + k * (gx * 0.7 + gy * 0.7), 0.4, 1.7)

def mars_tex():
    def make():
        w, h = 2048, 1024; rng = np.random.default_rng(21)
        n = make_noise(w, h, 7, 4, 0.58, seed=9); n2 = make_noise(w, h, 6, 8, 0.55, seed=10)
        dark = smoothstep(0.47, 0.58, n)
        base = lerp(np.array([0.62, 0.30, 0.17], np.float32), np.array([0.90, 0.58, 0.36], np.float32), smoothstep(0.3, 0.7, n2)[..., None])
        base = base * (1 - 0.62 * dark[..., None]) + np.array([0.30, 0.20, 0.16], np.float32) * 0.62 * dark[..., None]
        hm = _craters(h, w, 900, rng, 2, 26)
        base = base * _shade_height(hm, 2.2)[..., None]
        lat = (np.arange(h)[:, None] / h - 0.5) * math.pi
        cap = smoothstep(1.28, 1.42, np.abs(lat)) * (0.6 + 0.4 * n2)
        base = base * (1 - cap[..., None]) + np.array([0.95, 0.95, 0.97], np.float32) * cap[..., None]
        return Tex(base)
    return cached("mars", make)

def mars_albedo(lon, lat, ctx=None, rr=None, R=None):
    u = lon / TAU; v = (lat + math.pi / 2) / math.pi
    det = NZ("mdet", 512, 512, 6, 8, 0.6, 12)
    return mars_tex()(u, 1 - v) * (0.85 + 0.3 * det(u * 24, v * 12))[..., None]

def io_tex():
    def make():
        w, h = 2048, 1024; rng = np.random.default_rng(31)
        n = make_noise(w, h, 7, 4, 0.55, seed=13); n2 = make_noise(w, h, 6, 10, 0.5, seed=14)
        yel = np.array([0.80, 0.68, 0.26], np.float32); org = np.array([0.78, 0.38, 0.14], np.float32)
        wht = np.array([0.96, 0.95, 0.85], np.float32); drk = np.array([0.10, 0.07, 0.05], np.float32)
        base = yel * (1 - smoothstep(0.45, 0.6, n)[..., None]) + org * smoothstep(0.45, 0.6, n)[..., None]
        base = base * (1 - smoothstep(0.58, 0.7, n2)[..., None] * 0.7) + wht * smoothstep(0.58, 0.7, n2)[..., None] * 0.7
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        for _ in range(46):
            cx, cy = rng.uniform(0, w), rng.uniform(80, h - 80); s = rng.uniform(5, 16)
            d2 = ((xx - cx) / s) ** 2 + ((yy - cy) / s) ** 2
            sl = slice(max(int(cy - s * 6), 0), int(cy + s * 6)); 
        for _ in range(46):
            cx, cy = rng.uniform(0, w), rng.uniform(80, h - 80); s = rng.uniform(4, 14)
            y0, y1, x0, x1 = int(cy - s * 4), int(cy + s * 4), int(cx - s * 4), int(cx + s * 4)
            ys = np.arange(y0, y1)[:, None]; xs = np.arange(x0, x1)[None, :]
            d = np.sqrt(((xs - cx) / s) ** 2 + ((ys - cy) / s) ** 2)
            dark = np.exp(-d ** 2 * 2.0); halo = np.exp(-((d - 2.2) / 0.9) ** 2)
            xi = xs % w
            blk = base[y0:y1][:, xi[0]] if False else None
            rows = np.broadcast_to(ys, d.shape); cols = np.broadcast_to(xi, d.shape)
            b = base[rows, cols]
            b = b * (1 - dark[..., None] * 0.95) + drk * dark[..., None] * 0.95
            b = b * (1 - halo[..., None] * 0.55) + np.array([0.80, 0.30, 0.15], np.float32) * halo[..., None] * 0.55
            base[rows, cols] = b
        return Tex(base)
    return cached("io", make)

def io_albedo(lon, lat, ctx=None, rr=None, R=None):
    u = lon / TAU; v = (lat + math.pi / 2) / math.pi
    det = NZ("mdet", 512, 512, 6, 8, 0.6, 12)
    return io_tex()(u, 1 - v) * (0.88 + 0.24 * det(u * 20, v * 10))[..., None]

def triton_tex():
    def make():
        w, h = 2048, 1024; rng = np.random.default_rng(41)
        n = make_noise(w, h, 7, 4, 0.55, seed=23); n2 = make_noise(w, h, 7, 12, 0.55, seed=24)
        ridge = 1 - np.abs(n2 - 0.5) * 2
        base = np.array([0.80, 0.66, 0.62], np.float32) * np.ones((h, w, 1), np.float32)
        lat = (np.arange(h)[:, None] / h - 0.5) * math.pi
        cap = smoothstep(0.2, -0.5, lat)  # casquete sur
        cant = smoothstep(0.62, 0.9, ridge) * (1 - cap) * smoothstep(-0.6, 0.0, lat)
        base = base * (1 - 0.55 * cant[..., None]) + np.array([0.36, 0.34, 0.38], np.float32) * 0.55 * cant[..., None]
        base = base * (0.9 + 0.2 * n[..., None])
        base = base * (1 - cap[..., None] * 0.15) + np.array([1.0, 0.9, 0.88], np.float32) * cap[..., None] * 0.15
        for _ in range(60):  # vetas oscuras de géiseres
            cx, cy = rng.uniform(0, w), rng.uniform(h * 0.5, h * 0.9); L = rng.uniform(25, 80); a = rng.normal(0.4, 0.2)
            t = np.linspace(0, 1, int(L))
            xs = (cx + np.cos(a) * L * t).astype(int) % w; ys = np.clip((cy + np.sin(a) * L * t * 0.3).astype(int), 0, h - 1)
            base[ys, xs] *= 0.55; base[np.clip(ys + 1, 0, h - 1), xs] *= 0.75
        return Tex(base)
    return cached("triton", make)

def triton_albedo(lon, lat, ctx=None, rr=None, R=None):
    u = lon / TAU; v = (lat + math.pi / 2) / math.pi
    det = NZ("mdet", 512, 512, 6, 8, 0.6, 12)
    return triton_tex()(u, 1 - v) * (0.9 + 0.2 * det(u * 24, v * 12))[..., None]

def titan_albedo(lon, lat, ctx=None, rr=None, R=None):
    n1 = NZ("j1", seed=2); u = lon / TAU; v = (lat + math.pi / 2) / math.pi
    base = np.array([0.90, 0.58, 0.24], np.float32)
    band = 0.93 + 0.12 * n1(u * 1.0, v * 6) + 0.05 * n1(u * 5, v * 14)
    dark = 1 - 0.25 * smoothstep(0.7, 1.0, v)   # capuchón polar
    return base * (band * dark)[..., None] * np.ones(lat.shape + (3,), np.float32)

def rock_albedo_factory(base, seed):
    def f(lon, lat, ctx=None, rr=None, R=None):
        det = NZ("mdet", 512, 512, 6, 8, 0.6, 12); u = lon / TAU; v = (lat + math.pi / 2) / math.pi
        return np.array(base, np.float32) * (0.55 + 0.9 * det(u * 10 + seed, v * 5))[..., None]
    return f

def draw_shell(img, cx, cy, R, L, rad, width, col, k=1.0):
    """capa fina de bruma (p. ej. neblina separada de Titán) alrededor del limbo"""
    Rb = R * (rad + width * 6)
    x0, x1, y0, y1 = _bbox(cx, cy, Rb)
    if x1 <= x0 or y1 <= y0: return
    X = ((np.arange(x0, x1) + 0.5 - cx) / R).astype(np.float32)[None, :]; Y = (-(np.arange(y0, y1) + 0.5 - cy) / R).astype(np.float32)[:, None]
    rr = np.sqrt(X * X + Y * Y) + 1e-5
    lm = np.clip(0.25 + 0.75 * ((X / rr) * L[0] + (Y / rr) * L[1]) * 0.5 + 0.35, 0.1, 1)
    g = np.exp(-((rr - rad) / width) ** 2) * lm * k
    img[y0:y1, x0:x1] += g[..., None] * np.array(col, np.float32)
