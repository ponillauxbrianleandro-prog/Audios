"""Escultura por campos de distancia (SDF) en NumPy + marching cubes.
Fusión suave de primitivas -> anatomía/ropa orgánica, sin globos ni costuras. Todo por código."""
import numpy as np
from skimage import measure

F = np.float32


def _v(p):
    return np.asarray(p, dtype=F)


def smin(a, b, k):
    if k <= 0:
        return np.minimum(a, b)
    h = np.maximum(k - np.abs(a - b), 0) / k
    return np.minimum(a, b) - h * h * k * 0.25


def smax(a, b, k):
    return -smin(-a, -b, k)


class Field:
    def __init__(self, lo, hi, h):
        self.lo, self.hi, self.h = _v(lo), _v(hi), F(h)
        self.n = np.ceil((self.hi - self.lo) / h).astype(int) + 1
        self.d = np.full(tuple(self.n), 1.0, dtype=F)

    def axes(self, sl):
        return [(self.lo[i] + np.arange(sl[i].start, sl[i].stop, dtype=F) * self.h) for i in range(3)]

    def region(self, bmin, bmax, margin):
        sl = []
        for i in range(3):
            a = int(np.floor((bmin[i] - margin - self.lo[i]) / self.h))
            b = int(np.ceil((bmax[i] + margin - self.lo[i]) / self.h)) + 1
            sl.append(slice(max(a, 0), min(b, self.n[i])))
        if any(s.stop <= s.start for s in sl):
            return None
        return tuple(sl)

    def coords(self, sl):
        ax = self.axes(sl)
        return ax[0][:, None, None], ax[1][None, :, None], ax[2][None, None, :]

    def op(self, fn, bmin, bmax, k=0.0, mode="add"):
        """fn(X,Y,Z)->d local; bmin/bmax: caja que contiene la primitiva (sin margen)."""
        sl = self.region(bmin, bmax, k * 1.2 + 4 * self.h)
        if sl is None:
            return
        X, Y, Z = self.coords(sl)
        d = fn(X, Y, Z).astype(F)
        cur = self.d[sl]
        if mode == "add":
            self.d[sl] = smin(cur, d, k)
        elif mode == "sub":
            self.d[sl] = smax(cur, -d, k)
        elif mode == "inter":
            self.d[sl] = smax(cur, d, k)

    # ---------------------------------------------------------- primitivas
    def capsule(self, a, b, ra, rb=None, k=0.02, mode="add"):
        a, b = _v(a), _v(b)
        rb = ra if rb is None else rb
        ab = b - a
        L2 = float(ab @ ab) + 1e-9

        def fn(X, Y, Z):
            px, py, pz = X - a[0], Y - a[1], Z - a[2]
            t = np.clip((px * ab[0] + py * ab[1] + pz * ab[2]) / L2, 0, 1)
            dx, dy, dz = px - t * ab[0], py - t * ab[1], pz - t * ab[2]
            return np.sqrt(dx * dx + dy * dy + dz * dz) - (ra + (rb - ra) * t)

        r = max(ra, rb)
        self.op(fn, np.minimum(a, b) - r, np.maximum(a, b) + r, k, mode)

    def ellipsoid(self, c, r, rot=None, k=0.02, mode="add"):
        """rot: matriz 3x3 local->mundo (columnas = ejes locales)."""
        c, r = _v(c), _v(r)
        R = np.eye(3, dtype=F) if rot is None else _v(rot)
        rm = float(r.max())

        def fn(X, Y, Z):
            px, py, pz = X - c[0], Y - c[1], Z - c[2]
            qx = (px * R[0, 0] + py * R[1, 0] + pz * R[2, 0]) / r[0]
            qy = (px * R[0, 1] + py * R[1, 1] + pz * R[2, 1]) / r[1]
            qz = (px * R[0, 2] + py * R[1, 2] + pz * R[2, 2]) / r[2]
            return (np.sqrt(qx * qx + qy * qy + qz * qz) - 1.0) * float(r.min()) * 0.95

        self.op(fn, c - rm, c + rm, k, mode)

    def ecapsule(self, a, b, ra, rb, k=0.03, mode="add", up=(0, 0, 1)):
        """Cápsula elíptica: ra/rb = (rx, ry) en los extremos; ejes transversales: x del mundo e y ⟂."""
        a, b = _v(a), _v(b)
        ab = b - a
        L2 = float(ab @ ab) + 1e-9
        ra, rb = _v(ra), _v(rb)
        ax = ab / np.sqrt(L2)
        ex = np.cross(_v(up) if abs(ax @ _v(up)) < 0.99 else _v((0, 1, 0)), ax)
        ex /= np.linalg.norm(ex)
        ey = np.cross(ax, ex)

        def fn(X, Y, Z):
            px, py, pz = X - a[0], Y - a[1], Z - a[2]
            t = np.clip((px * ab[0] + py * ab[1] + pz * ab[2]) / L2, 0, 1)
            dx, dy, dz = px - t * ab[0], py - t * ab[1], pz - t * ab[2]
            ox = dx * ex[0] + dy * ex[1] + dz * ex[2]
            oy = dx * ey[0] + dy * ey[1] + dz * ey[2]
            oa = dx * ax[0] + dy * ax[1] + dz * ax[2]          # resto axial (tapas elipsoidales en los extremos)
            rx = ra[0] + (rb[0] - ra[0]) * t
            ry = ra[1] + (rb[1] - ra[1]) * t
            rax = (rx + ry) * 0.5
            return (np.sqrt((ox / rx) ** 2 + (oy / ry) ** 2 + (oa / rax) ** 2) - 1.0) * np.minimum(rx, ry) * 0.95

        r = float(max(ra.max(), rb.max()))
        self.op(fn, np.minimum(a, b) - r, np.maximum(a, b) + r, k, mode)

    def box(self, c, hs, rot=None, rnd=0.0, k=0.0, mode="add"):
        c, hs = _v(c), _v(hs)
        R = np.eye(3, dtype=F) if rot is None else _v(rot)
        rm = float(np.linalg.norm(hs)) + rnd

        def fn(X, Y, Z):
            px, py, pz = X - c[0], Y - c[1], Z - c[2]
            qx = np.abs(px * R[0, 0] + py * R[1, 0] + pz * R[2, 0]) - hs[0] + rnd
            qy = np.abs(px * R[0, 1] + py * R[1, 1] + pz * R[2, 1]) - hs[1] + rnd
            qz = np.abs(px * R[0, 2] + py * R[1, 2] + pz * R[2, 2]) - hs[2] + rnd
            out = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2 + np.maximum(qz, 0) ** 2)
            return out + np.minimum(np.maximum(qx, np.maximum(qy, qz)), 0) - rnd

        self.op(fn, c - rm, c + rm, k, mode)

    def custom(self, fn, bmin, bmax, k=0.0, mode="add"):
        self.op(fn, _v(bmin), _v(bmax), k, mode)

    def displace(self, fn, bmin, bmax, margin=0.0):
        """d += fn(X,Y,Z) en una región (pliegues/arrugas, poros)."""
        sl = self.region(_v(bmin), _v(bmax), margin)
        if sl is None:
            return
        X, Y, Z = self.coords(sl)
        self.d[sl] += fn(X, Y, Z).astype(F)

    def mesh(self, smooth=1, step=1):
        from scipy.ndimage import gaussian_filter
        d = self.d
        if smooth:
            # suaviza ligeramente el campo (quita escalones de voxel) manteniendo el volumen
            d = gaussian_filter(d, smooth * 0.6)
        v, f, n, _ = measure.marching_cubes(d, 0.0, spacing=(self.h,) * 3, step_size=step)
        v = v + self.lo
        return v.astype(np.float64), f, n


def rot_from(f, n=(0, 0, 1)):
    """Matriz 3x3 con columna z = f (largo), y = n proyectado."""
    f = _v(f); f = f / np.linalg.norm(f)
    n = _v(n); n = n - f * (n @ f); n = n / np.linalg.norm(n)
    s = np.cross(f, n)
    return np.stack([s, n, f], axis=1)


def fold_noise(seed, n=6, kmin=18, kmax=60):
    """Pliegues de tela: suma de senos con direcciones aleatorias (suave, barato)."""
    rng = np.random.default_rng(seed)
    dirs = rng.normal(size=(n, 3)); dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
    ks = rng.uniform(kmin, kmax, n)
    ph = rng.uniform(0, 6.28, n)
    am = rng.uniform(0.5, 1.0, n)

    def f(X, Y, Z):
        s = 0
        for i in range(n):
            s = s + am[i] * np.sin(ks[i] * (X * dirs[i, 0] + Y * dirs[i, 1] + Z * dirs[i, 2]) + ph[i])
        return s / n
    return f
