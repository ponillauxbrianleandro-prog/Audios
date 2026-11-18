"""El mundo: suelo en perspectiva real, río con reflejos, cielo, nubes y cordillera.

Todo se genera por procedimiento. El suelo y las nubes son planos muestreados con
perspectiva (paralaje continuo); la cordillera es un mapa de alturas proyectado a un
panorama (sin polígonos).
"""
import os
import numpy as np
import cv2
from util import fbm, smoothstep, lerp, blur, catmull

CACHE = os.environ.get("GORGO_CACHE", "/tmp/gorgo_cache")
os.makedirs(CACHE, exist_ok=True)

SUN = np.array([-0.50, 0.62, -0.42])           # hacia el sol (mundo: X der, Y arriba, Z fondo)
SUN = SUN / np.linalg.norm(SUN)
SUN_COL = np.array([1.00, 0.95, 0.86], np.float32)
SKY_AMB = np.array([0.62, 0.72, 0.86], np.float32)
FOG_COL = np.array([0.80, 0.855, 0.905], np.float32)

# Extensión del mapa del suelo (metros)
GX0, GX1, GZ0, GZ1 = -130.0, 130.0, -6.0, 500.0
GRES = 0.16

RIVER_PTS = [(-150, 15.5), (-70, 15.0), (-25, 16.0), (8, 17.5), (30, 24), (41, 42), (32, 72),
             (6, 112), (-12, 165), (14, 235), (44, 325), (22, 420), (40, 520)]


def _cached(name, fn):
    p = os.path.join(CACHE, name + ".npy")
    if os.path.exists(p):
        return np.load(p)
    a = fn()
    np.save(p, a)
    return a


def river_dist(X, Z):
    """Distancia firmada aproximada a la orilla (negativa = agua), para puntos sueltos."""
    m = MAPS[0]
    tx = np.clip((np.asarray(X) - GX0) / GRES, 0, m.shape[1] - 1).astype(int)
    tz = np.clip((np.asarray(Z) - GZ0) / GRES, 0, m.shape[0] - 1).astype(int)
    return m[tz, tx, 3]


def _build_macro():
    w = int((GX1 - GX0) / GRES)
    h = int((GZ1 - GZ0) / GRES)
    line = catmull(RIVER_PTS, 4000)
    px = ((line[:, 0] - GX0) / GRES).astype(np.int32)
    pz = ((line[:, 1] - GZ0) / GRES).astype(np.int32)
    img = np.full((h, w), 255, np.uint8)
    cv2.polylines(img, [np.stack([px, pz], 1)], False, 0, 1)
    d = cv2.distanceTransform(img, cv2.DIST_L2, 5) * GRES
    zz = (np.arange(h) * GRES + GZ0)[:, None]
    n1 = cv2.resize(fbm((512, 512), 2.2, 11), (w, h), interpolation=cv2.INTER_CUBIC)
    halfw = 4.6 - 1.4 * smoothstep(40, 300, zz) + 1.6 * (n1 - 0.5)
    dist = d - halfw                                    # <0 agua
    wet = np.exp(-np.maximum(dist, 0) / 2.2)
    n2 = cv2.resize(fbm((1024, 1024), 2.0, 12), (w, h), interpolation=cv2.INTER_CUBIC)
    n3 = cv2.resize(fbm((1024, 1024), 1.7, 13), (w, h), interpolation=cv2.INTER_CUBIC)
    veg = np.clip(0.30 * np.exp(-np.maximum(dist, 0) / 14.0) + 0.85 * (n2 - 0.36), 0, 1)
    tone = n3
    return np.stack([wet, veg, tone, dist], -1).astype(np.float32)


def _build_tile(seed, pebbles=True):
    """Tesela de detalle: [sombreado de relieve, variación de albedo, grano]."""
    n = 1024
    hgt = fbm((n, n), 1.9, seed) * 0.6 + fbm((n, n), 1.2, seed + 1, lowcut=20) * 0.12
    alb = fbm((n, n), 1.3, seed + 2)
    if pebbles:
        rng = np.random.default_rng(seed)
        peb = np.zeros((n, n), np.float32)
        tone = np.zeros((n, n), np.float32)
        for _ in range(520):
            x, y = rng.integers(0, n, 2)
            r = int(rng.uniform(2, 9) ** 1.25)
            ax = (r, max(1, int(r * rng.uniform(0.55, 1.0))))
            ang = rng.uniform(0, 180)
            for ox in (-n, 0, n):
                for oy in (-n, 0, n):
                    if -20 < x + ox < n + 20 and -20 < y + oy < n + 20:
                        cv2.ellipse(peb, (int(x + ox), int(y + oy)), ax, ang, 0, 360, 1.0, -1, cv2.LINE_AA)
                        cv2.ellipse(tone, (int(x + ox), int(y + oy)), ax, ang, 0, 360, float(rng.uniform(0.25, 1)), -1, cv2.LINE_AA)
        dome = cv2.GaussianBlur(peb, (0, 0), 2.2)
        hgt = hgt + 0.09 * dome * peb
        alb = lerp(alb, 0.35 + 0.6 * tone, peb * 0.85)
    gy, gx = np.gradient(hgt * 60.0)
    nrm = np.stack([-gx, np.ones_like(gx), -gy], -1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    shade = np.clip((nrm * np.array([SUN[0], SUN[1], SUN[2]])).sum(-1) / SUN[1], 0.25, 1.9)
    grain = fbm((n, n), 0.6, seed + 3)
    return np.stack([shade, alb, grain], -1).astype(np.float32)


def _pyr(a, levels):
    out = [a]
    for _ in range(levels):
        if min(out[-1].shape[:2]) < 8:
            break
        out.append(cv2.pyrDown(out[-1]))
    return out


def _build_clouds():
    n = 2048
    d = fbm((n, n), 2.5, 31) * 0.7 + fbm((n, n), 1.6, 32, lowcut=6) * 0.3
    sh = np.roll(d, (int(-18 * SUN[2]), int(-18 * SUN[0])), (0, 1))
    lit = np.clip(0.62 + (d - sh) * 5.0, 0, 1)
    thin = fbm((n, n), 2.9, 33)
    return np.stack([d, lit, thin], -1).astype(np.float32)


def _build_pano(seed, nx, nz, d0, d1, hmax, ppr, rows, snow, hbase=0.0, vegtop=0.42, fogl=16000.0, ridge=0.55):
    """Cordillera: mapa de alturas -> panorama (azimut x tangente de elevación).

    Devuelve RGBA float32 (rows, nx); fila rows-1 = horizonte.
    """
    c = hmax / 20.0
    gz, gx = max(24, int((d1 - d0) / c)), int(PANO_SPAN * (d0 + d1) / 2 / c)
    up = lambda a: np.clip(cv2.resize(a, (nx, nz), interpolation=cv2.INTER_CUBIC), 0, 1)
    n = up(fbm((gz, gx), 2.8, seed))
    n2 = up(fbm((gz, gx), 2.6, seed + 1, lowcut=1.5))
    n3 = up(fbm((gz * 3, gx * 3), 2.4, seed + 7, lowcut=5))
    r = 1 - np.abs(2 * n2 - 1)
    r3 = 1 - np.abs(2 * n3 - 1)
    z = np.linspace(0, 1, nz)[:, None]
    env = smoothstep(0.0, 0.55, z) * (1 - 0.35 * smoothstep(0.75, 1.0, z))
    lowf = cv2.resize(fbm((64, 256), 2.4, seed + 2), (nx, nz), interpolation=cv2.INTER_CUBIC)
    h = ((1 - ridge) * n + ridge * r ** 1.15) * env * (0.30 + 1.0 * lowf)
    h = h * (0.86 + 0.28 * r3 ** 1.3)
    h = np.clip(h - 0.06, 0, None)
    h = (h / h.max()) ** 1.05 * hmax + hbase * env
    h = cv2.GaussianBlur(h, (0, 0), sigmaX=nx / gx * 0.30, sigmaY=nz / gz * 0.30)
    D = d0 + (d1 - d0) * z                                   # distancia de cada franja
    tops = (h / D) * ppr                                     # filas sobre el horizonte
    M = np.maximum.accumulate(tops, axis=0)
    ys = np.arange(rows, dtype=np.float32)                   # fila sobre el horizonte
    vis = np.empty((rows, nx), np.int32)
    for x in range(nx):
        vis[:, x] = np.searchsorted(M[:, x], ys + 0.5)
    alpha = (vis < nz).astype(np.float32)
    vis = np.minimum(vis, nz - 1)
    # normales y color por celda del mapa
    dxm = (D * (1.0 / ppr))
    fine = fbm((nz, nx), 2.1, seed + 9, lowcut=30)
    hn = h + (1 - np.abs(2 * fine - 1)) * 0.035 * hmax * np.clip(h / hmax * 3, 0.15, 1)
    gz, gx = np.gradient(hn)
    gx = gx / dxm
    gz = gz / ((d1 - d0) / nz)
    nrm = np.stack([-gx, np.ones_like(gx), -gz], -1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    ndl = np.clip((nrm * SUN).sum(-1), 0, 1)
    slope = 1 - nrm[..., 1]
    ao = np.clip(1.0 + (h - cv2.GaussianBlur(h, (0, 0), 14)) / (0.06 * hmax), 0.45, 1.25)
    det = fbm((nz, nx), 1.2, seed + 5)
    strata = 0.5 + 0.5 * np.sin(h / hmax * 55 + 6 * lowf + 3 * det)
    rock = lerp(np.array([0.36, 0.34, 0.35]), np.array([0.52, 0.47, 0.44]), (0.6 * det + 0.4 * strata)[..., None])
    veg = lerp(np.array([0.13, 0.20, 0.16]), np.array([0.22, 0.29, 0.20]), det[..., None])
    vmask = smoothstep(vegtop, vegtop - 0.26, h / hmax + 0.25 * (det - 0.5)) * smoothstep(0.55, 0.25, slope)
    alb = lerp(rock, veg, vmask[..., None])
    if snow < 1.0:
        smask = smoothstep(snow - 0.08, snow + 0.10, h / hmax + 0.22 * (det - 0.5)) * smoothstep(0.80, 0.45, slope)
        alb = lerp(alb, np.array([0.93, 0.95, 0.98]), smask[..., None])
    light = (ndl[..., None] * SUN_COL * 1.35 + SKY_AMB * 0.36) * ao[..., None]
    col = alb * light
    fog = 1 - np.exp(-D / fogl)
    fogc = FOG_COL * np.array([0.92, 0.97, 1.03])
    col = lerp(col, fogc, np.broadcast_to(fog, h.shape)[..., None] * 0.92)
    xi = np.broadcast_to(np.arange(nx), (rows, nx))
    img = col[vis, xi]
    img = np.concatenate([img, alpha[..., None]], -1)[::-1].astype(np.float32)
    img = cv2.GaussianBlur(img, (0, 0), 1.3)
    return np.ascontiguousarray(img)


PANO_PPR = 3200.0          # píxeles por radián del panorama
PANO_SPAN = 3.4            # radianes cubiertos
PANO_NX = int(PANO_PPR * PANO_SPAN)

MAPS = None
TILE_A = TILE_B = RIP = CLOUDS = PANO_FAR = PANO_NEAR = None


def load():
    global MAPS, TILE_A, TILE_B, RIP, CLOUDS, PANO_FAR, PANO_NEAR
    if MAPS is not None:
        return
    MAPS = _pyr(_cached("macro", _build_macro), 6)
    TILE_A = _pyr(_cached("tileA", lambda: _build_tile(21)), 8)
    TILE_B = _pyr(_cached("tileB", lambda: _build_tile(41, pebbles=False)), 8)
    RIP = _pyr(_cached("ripple", lambda: np.stack([fbm((512, 512), 1.6, 51, lowcut=5),
                                                    fbm((512, 512), 1.6, 52, lowcut=5)], -1)), 6)
    CLOUDS = _cached("clouds", _build_clouds)
    PANO_FAR = _cached("pano_far", lambda: _build_pano(61, PANO_NX, 1500, 9000, 26000, 3300, PANO_PPR, 760, 0.34, fogl=17000.0, ridge=0.55))
    PANO_NEAR = _cached("pano_near", lambda: _build_pano(71, PANO_NX, 900, 1500, 5500, 210, PANO_PPR, 420, 9.0, hbase=12, vegtop=1.4, fogl=7000.0, ridge=0.25))


class Camera:
    def __init__(self, W, H, f, pos, yaw=0.0, pitch=0.0):
        self.W, self.H, self.f = W, H, float(f)
        self.pos = np.asarray(pos, np.float64)
        self.yaw, self.pitch = yaw, pitch
        self.vh = H / 2 - self.f * np.tan(pitch)          # fila del horizonte (pitch>0 = arriba)
        self.c, self.s = np.cos(yaw), np.sin(yaw)

    def project(self, P):
        P = np.asarray(P, np.float64)
        rx, ry, rz = P[..., 0] - self.pos[0], P[..., 1] - self.pos[1], P[..., 2] - self.pos[2]
        xc = rx * self.c - rz * self.s
        zc = rx * self.s + rz * self.c
        zs = np.maximum(zc, 1e-3)
        return self.W / 2 + self.f * xc / zs, self.vh - self.f * ry / zs, zc

    def to_cam(self, V):
        """Rota un vector del mundo al sistema de cámara (x der, y arriba, z fondo)."""
        V = np.asarray(V, np.float64)
        return np.stack([V[..., 0] * self.c - V[..., 2] * self.s, V[..., 1],
                         V[..., 0] * self.s + V[..., 2] * self.c], -1)


def _sample_lod(pyr, mx, my, lod, wrap):
    """Muestreo trilineal sobre una pirámide. lod varía solo por fila: cada nivel se
    remuestrea únicamente en la franja de filas donde pesa."""
    lod = np.clip(lod, 0, len(pyr) - 1.001)
    lr = lod[:, 0] if lod.ndim == 2 else lod
    bm = cv2.BORDER_WRAP if wrap else cv2.BORDER_REPLICATE
    nch = 1 if pyr[0].ndim == 2 else pyr[0].shape[2]
    out = np.zeros(mx.shape + (nch,), np.float32)
    for L in range(int(np.floor(lr.min())), int(np.ceil(lr.max())) + 1):
        wr = np.clip(1 - np.abs(lr - L), 0, 1)
        rows = np.nonzero(wr > 0)[0]
        if len(rows) == 0:
            continue
        r0, r1 = rows[0], rows[-1] + 1
        sc = 1.0 / (2 ** L)
        s = cv2.remap(pyr[L], (mx[r0:r1] + 0.5) * sc - 0.5, (my[r0:r1] + 0.5) * sc - 0.5, cv2.INTER_LINEAR, borderMode=bm)
        if s.ndim == 2:
            s = s[..., None]
        out[r0:r1] += s * wr[r0:r1, None, None]
    return out


def sky(cam, t, weather):
    """Cielo + nubes + cordillera. Devuelve imagen float32 (H,W,3)."""
    W, H, f = cam.W, cam.H, cam.f
    u = (np.arange(W, dtype=np.float32) - W / 2) / f
    v = (cam.vh - np.arange(H, dtype=np.float32)) / f           # tan elevación
    uu, vv = np.meshgrid(u, v)
    az = cam.yaw + np.arctan(uu)
    az = (az + np.pi) % (2 * np.pi) - np.pi
    el = np.clip(vv, -0.02, None)
    k = np.exp(-el * 3.2)[..., None]
    zen = np.array(weather.get("zenith", [0.34, 0.60, 0.94]), np.float32)
    hor = np.array(weather.get("horizon", [0.80, 0.91, 0.98]), np.float32)
    img = zen + (hor - zen) * k
    # resplandor hacia el sol (fuera de cuadro, a la izquierda)
    saz = np.arctan2(SUN[0], SUN[2])
    glow = np.exp(-((az - saz) ** 2) / 0.5 - el * 2.5)[..., None]
    img = img + glow * np.array([0.16, 0.12, 0.05], np.float32)
    # nubes en un plano a 1900 m
    dy = np.maximum(vv, 0.012)
    tcl = 1900.0 / dy
    X = (uu * cam.c + cam.s) * tcl
    Z = (-uu * cam.s + cam.c) * tcl
    sc = 2048 / 26000.0
    mx = ((X + 9000 + t * 9.0) * sc).astype(np.float32)
    my = ((Z + 4000 + t * 3.0) * sc).astype(np.float32)
    cl = cv2.remap(CLOUDS, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
    cov = weather.get("cloud", 0.47)
    dens = smoothstep(1 - cov - 0.04, 1 - cov + 0.26, cl[..., 0])
    cirr = smoothstep(0.55, 0.95, cl[..., 2]) * 0.22
    lit = cl[..., 1]
    dist = np.sqrt(X * X + Z * Z)
    farf = np.exp(-dist / 45000.0) * smoothstep(0.012, 0.05, vv)
    ccol = lerp(np.array([0.60, 0.64, 0.71], np.float32), np.array([1.0, 0.99, 0.97], np.float32),
                (lit * (0.55 + 0.45 * (1 - dens)))[..., None])
    img = lerp(img, np.array([0.95, 0.96, 0.98], np.float32), (cirr * farf)[..., None])
    img = lerp(img, ccol, (dens * farf * 0.93)[..., None])
    if weather.get('stars', 0) > 0:
        rs = np.random.default_rng(8)
        sa, se = rs.uniform(-np.pi, np.pi, 1500), rs.uniform(0.02, 1.2, 1500)
        su = W / 2 + f * np.tan(np.clip(((sa - cam.yaw + np.pi) % (2 * np.pi)) - np.pi, -1.4, 1.4))
        sv = cam.vh - se * f
        okk = (su > 0) & (su < W - 1) & (sv > 0) & (sv < H - 1)
        st = np.zeros((H, W), np.float32)
        st[sv[okk].astype(int), su[okk].astype(int)] = rs.uniform(0.3, 1.0, 1500)[okk]
        st = cv2.GaussianBlur(st, (0, 0), 0.8) * 3.0
        img = img + st[..., None] * (1 - dens * farf)[..., None] * 0.8
    # bruma anómala en el horizonte (incógnita narrativa)
    hz = weather.get("plume", 0.0)
    if hz > 0:
        paz = weather.get("plume_az", 0.42)
        tx = ((az * 700 + t * 2.0)).astype(np.float32)
        ty = (el * 1900).astype(np.float32)
        pn = cv2.remap(CLOUDS[..., 0], tx, ty, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        shape = np.exp(-((az - paz) / 0.34) ** 2) * np.exp(-np.maximum(el, 0) / (0.035 + 0.05 * pn))
        a = np.clip(shape * (0.55 + 0.9 * pn) * hz, 0, 0.85)[..., None]
        img = lerp(img, np.array([0.63, 0.58, 0.54], np.float32), a)
    # cordilleras
    for pano, fogk in ((PANO_FAR, 0.0), (PANO_NEAR, 0.0)):
        px = ((az + PANO_SPAN / 2) * PANO_PPR).astype(np.float32)
        py = (pano.shape[0] - 1 - vv * PANO_PPR).astype(np.float32)
        s = cv2.remap(pano, px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        a = s[..., 3:4]
        pc = s[..., :3] * np.array(weather.get('pano_tint', (1, 1, 1)), np.float32)
        pw = weather.get('pano_white', 0.0)
        if pw > 0:
            lum_ = pc.mean(-1, keepdims=True)
            pc = lerp(pc, np.array([0.90, 0.93, 0.98], np.float32) * np.clip(lum_ * 1.5 + 0.38, 0, 1.08), pw)
        img = img * (1 - a) + pc * a
    if hz > 0:   # la bruma también vela la base de las montañas
        img = lerp(img, np.array([0.66, 0.62, 0.59], np.float32), a * 0.0 + (shape * 0.35 * hz)[..., None])
    # calima baja pegada al horizonte
    hb = (np.exp(-np.abs(vv) / 0.010) * 0.6 + np.exp(-np.abs(vv) / 0.05) * 0.35)[..., None]
    img = lerp(img, FOG_COL, hb)
    return img.astype(np.float32)


def ground(cam, t, bg, refl_rgba=None, shadow=None, weather=None, ripples=()):
    """Suelo y agua para las filas bajo el horizonte. Modifica y devuelve bg (copia)."""
    weather = weather or {}
    W, H, f = cam.W, cam.H, cam.f
    out = bg.copy()
    y0 = int(max(0, np.ceil(cam.vh + 0.5)))
    if y0 >= H:
        return out
    u = (np.arange(W, dtype=np.float32) - W / 2) / f
    dyr = (np.arange(y0, H, dtype=np.float32) - cam.vh) / f      # >0 hacia abajo
    uu, dd = np.meshgrid(u, dyr)
    tz = cam.pos[1] / dd                                         # profundidad de cámara
    X = (cam.pos[0] + (uu * cam.c + cam.s) * tz).astype(np.float32)
    Z = (cam.pos[2] + (-uu * cam.s + cam.c) * tz).astype(np.float32)
    footz = tz * tz / (f * cam.pos[1])
    footx = tz / f
    foot = footx ** 0.72 * footz ** 0.28 * 1.15

    def lod(texel):
        return np.log2(np.maximum(foot / texel, 1e-6))

    m = _sample_lod(MAPS, (X - GX0) / GRES, (Z - GZ0) / GRES, lod(GRES), False)
    wet, veg, tone, dist = m[..., 0], m[..., 1], m[..., 2], m[..., 3]
    dist = dist + weather.get('dry', 0.0) * (1.0 + 2.2 * tone)          # estación seca: el río se retira
    wet = np.exp(-np.maximum(dist, 0) / 2.2)
    ta = 1.7 / 1024
    tb = 9.0 / 1024
    A = _sample_lod(TILE_A, X / ta, Z / ta, lod(ta), True)
    B = _sample_lod(TILE_B, X / tb + 300, Z / tb + 170, lod(tb), True)
    A2 = _sample_lod(TILE_A, (X * 0.8 + Z * 0.6) / (ta * 3.3), (Z * 0.8 - X * 0.6) / (ta * 3.3), lod(ta * 3.3), True)
    shade = (0.55 * A[..., 0] + 0.45 * A2[..., 0]) * (0.55 + 0.45 * B[..., 0])
    shade = np.clip(1 + (shade - 1) * 0.7, 0.4, 1.6)
    var = 0.45 * A[..., 1] + 0.3 * A2[..., 1] + 0.25 * B[..., 1]
    edge = dist + (B[..., 1] - 0.5) * 0.9 + (A2[..., 1] - 0.5) * 0.25
    # --- tierra
    dry_a = np.array(weather.get('soil_a', [0.64, 0.60, 0.54]), np.float32)
    dry_b = np.array(weather.get('soil_b', [0.47, 0.43, 0.39]), np.float32)
    soil = lerp(dry_b, dry_a, np.clip(0.6 * tone + 0.4 * var, 0, 1)[..., None])
    wetk = np.clip(wet * 1.25 - 0.1 + 0.3 * (B[..., 1] - 0.5), 0, 1)
    soil = soil * lerp(1.0, 0.50, wetk)[..., None] * np.array([1.0, 0.99, 0.985], np.float32)
    # cubierta baja (musgos, hepáticas, helechos rastreros): no hay hierba en el Pérmico
    vk = weather.get('moss', 1.0) * smoothstep(0.47, 0.74, veg + weather.get('moss_bias', 0.0) + 0.55 * (A2[..., 1] - 0.5) + 0.35 * (B[..., 2] - 0.5))
    moss = lerp(np.array(weather.get('moss_a', [0.13, 0.26, 0.09]), np.float32), np.array(weather.get('moss_b', [0.30, 0.50, 0.15]), np.float32),
                np.clip(1.3 * A[..., 2] * var + 0.25 * tone, 0, 1)[..., None])
    vsh = 0.55 + 0.75 * A[..., 2]
    col = lerp(soil * shade[..., None], moss * (vsh * (0.5 + 0.5 * shade))[..., None], (vk * 0.85)[..., None])
    und = _sample_lod(TILE_B, X / 60.0 / (1.0 / 1024), Z / 22.0 / (1.0 / 1024), lod(0.04), True)[..., 0]
    col = col * np.clip(0.80 + 0.22 * und, 0.7, 1.25)[..., None]
    # hojarasca y barro agrietado
    lit = weather.get('litter', 0.0)
    if lit > 0:
        lk = smoothstep(0.52, 0.70, A2[..., 2] * 0.6 + B[..., 2] * 0.5 + 0.25 * veg) * lit
        lcol = lerp(np.array([0.30, 0.24, 0.16], np.float32), np.array([0.52, 0.44, 0.28], np.float32), A[..., 1:2])
        col = lerp(col, lcol * (0.6 + 0.6 * A[..., 2:3]), (lk * 0.8)[..., None])
    cr = weather.get('cracks', 0.0)
    if cr > 0:
        ck = _sample_lod(TILE_B, (X * 0.9 + Z * 0.43) / (0.9 / 1024), (Z * 0.9 - X * 0.43) / (0.9 / 1024), lod(0.9 / 1024), True)[..., 2]
        line = smoothstep(0.035, 0.0, np.abs(ck - 0.5)) * smoothstep(40.0, 8.0, tz) * cr * wetk
        col = col * (1 - 0.6 * line[..., None])
    light = SUN_COL * SUN[1] * 1.28 + SKY_AMB * 0.42
    col = col * light
    cs = weather.get('cloud_shadow', 0.35)
    if cs > 0:
        cmx = ((X + 9000 + t * 9.0 + 1900 * SUN[0] / SUN[1]) * (2048 / 26000.0)).astype(np.float32)
        cmy = ((Z + 4000 + t * 3.0 + 1900 * SUN[2] / SUN[1]) * (2048 / 26000.0)).astype(np.float32)
        cd = cv2.remap(CLOUDS[..., 0], cmx, cmy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        cov = weather.get('cloud', 0.47)
        col = col * (1 - cs * smoothstep(1 - cov - 0.04, 1 - cov + 0.26, cd))[..., None]
    dn = weather.get('dunes', 0.0)
    if dn > 0:
        rid = np.sin((X * 0.55 + Z * 0.22) / 2.6 + 5.0 * (B[..., 1] - 0.5)) * 0.5 + 0.5
        rid2 = np.sin((X * 0.18 - Z * 0.10) / 5.0 + 3.0 * (B[..., 1] - 0.5)) * 0.5 + 0.5
        col = col * (1 - dn * 0.30 * (1 - rid) * smoothstep(140.0, 25.0, tz) - dn * 0.22 * (1 - rid2) * smoothstep(300.0, 40.0, tz))[..., None]
    sn = weather.get('snow', 0.0)
    if sn > 0:
        patch = 0.9 * (A2[..., 1] - 0.5) + 0.5 * (B[..., 1] - 0.5) + 0.35 * (tone - 0.5)
        smask = smoothstep(0.40, 0.62, sn * 1.12 + patch * (1.15 - 0.65 * sn) - 0.02 * vk)
        scol = np.array(weather.get('snow_col', (0.90, 0.93, 0.98)), np.float32) * (SUN_COL * SUN[1] * 1.05 + SKY_AMB * 0.55)
        scol = scol * np.clip(0.80 + 0.22 * (shade - 1.0) + 0.12 * (A[..., 2] - 0.5), 0.55, 1.1)[..., None]
        col = lerp(col, scol, (smask * 0.96)[..., None])
    if shadow is not None:
        col = col * (1 - shadow[y0:, :, None] * np.array([0.60, 0.56, 0.50], np.float32))
    # --- agua
    wmask = smoothstep(0.10, -0.12, edge)
    if wmask.max() > 0:
        rs = 0.9 / 512
        r1 = _sample_lod(RIP, (X + t * 0.22) / rs, (Z + t * 0.06) / rs, lod(rs), True)
        r2 = _sample_lod(RIP, (X * 0.7 - Z * 0.7 - t * 0.15) / (rs * 2.7), (X * 0.7 + Z * 0.7) / (rs * 2.7), lod(rs * 2.7), True)
        nx = (r1[..., 0] - 0.5) + (r2[..., 0] - 0.5) * 1.2
        nz = (r1[..., 1] - 0.5) + (r2[..., 1] - 0.5) * 1.2
        for (rx, rz, t0, amp) in ripples:
            age = t - t0
            if age <= 0:
                continue
            rr = np.sqrt((X - rx) ** 2 + (Z - rz) ** 2)
            ph = (rr - 0.38 * age) * 34.0
            env = np.exp(-((rr - 0.38 * age) / 0.22) ** 2) * amp * np.exp(-age * 0.55) / (0.4 + rr)
            ring = np.sin(ph) * env
            nx = nx + ring * (X - rx) / (rr + 1e-3) * 1.6
            nz = nz + ring * (Z - rz) / (rr + 1e-3) * 1.6
        rough = weather.get("rough", 1.0)
        yy = np.arange(y0, H, dtype=np.float32)[:, None] + np.zeros((1, W), np.float32)
        xx = np.zeros((H - y0, 1), np.float32) + np.arange(W, dtype=np.float32)[None, :]
        kk = f * 0.035 * rough / np.sqrt(1 + tz * 0.12)
        mxr = xx + nx * kk * 0.6
        myr = 2 * cam.vh - yy + nz * kk * 1.6 - 1.0
        refl = cv2.remap(bg, mxr.astype(np.float32), np.clip(myr, 0, H - 1).astype(np.float32),
                         cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        if refl_rgba is not None:
            rr2 = cv2.remap(refl_rgba, mxr.astype(np.float32), (yy + nz * kk * 1.6).astype(np.float32),
                            cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
            refl = refl * (1 - rr2[..., 3:4]) + rr2[..., :3]
        cosv = dd / np.sqrt(1 + dd * dd + uu * uu)
        fres = 0.30 + 0.70 * (1 - np.clip(cosv * 2.2, 0, 1)) ** 2.0
        deep = np.array([0.09, 0.30, 0.33], np.float32) * (0.85 + 0.3 * tone[..., None])
        depth = smoothstep(0.0, -1.3, edge)
        body = lerp(col * 0.62, deep, depth[..., None])
        ice = weather.get('ice', 0.0)
        water = lerp(body, refl * np.array([0.93, 0.96, 0.97], np.float32), (fres * (1 - 0.7 * ice) * (0.45 + 0.55 * depth))[..., None])
        if ice > 0:
            icec = np.array([0.66, 0.80, 0.88], np.float32) * (0.80 + 0.30 * (B[..., 0] - 0.5) + 0.25 * depth)[..., None]
            crack = smoothstep(0.045, 0.0, np.abs(_sample_lod(TILE_B, (X * 0.7 + Z * 0.7) / (1.3 / 1024), (Z * 0.7 - X * 0.7) / (1.3 / 1024),
                                                              lod(1.3 / 1024), True)[..., 2] - 0.5))
            icec = icec * (1 - 0.45 * crack[..., None] * smoothstep(60.0, 8.0, tz)[..., None]) * (SUN_COL * 0.8 + SKY_AMB * 0.55)
            water = lerp(water, icec, ice * 0.88)
        glint = np.clip((nx * SUN[0] + nz * SUN[2]) * 3.0 - 0.86, 0, 1) ** 2
        water = water + glint[..., None] * 0.55 * np.exp(-tz / 90.0)[..., None]
        if shadow is not None:
            water = water * (1 - 0.35 * shadow[y0:, :, None])
        col = lerp(col, water, wmask[..., None])
    # brillo húmedo del barro
    sheen = wetk * (1 - wmask) * 0.10 * (1 - vk)
    col = col + sheen[..., None] * np.array([0.75, 0.82, 0.9], np.float32)
    # perspectiva atmosférica
    fogd = weather.get("fog", 1.0)
    fog = 1 - np.exp(-tz * fogd / 380.0)
    col = lerp(col, FOG_COL, fog[..., None])
    aa = np.clip((np.arange(y0, H, dtype=np.float32) - cam.vh), 0, 1)[:, None, None]
    out[y0:] = bg[y0:] * (1 - aa) + col * aa
    return out, (y0, tz)
