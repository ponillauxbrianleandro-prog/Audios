"""Nucleo de pintura 2D (cv2 + numpy) para las piezas de la biblioteca.
Lienzo RGBA premultiplicado a supermuestreo, cintas/hojas con 2 tonos, cilindros
con bandas de luz, masas sombreadas por relieve, contorno calido y grano."""
import numpy as np
import cv2
from PIL import Image

LUZ = np.array([-0.55, -0.83])
LUZ = LUZ / np.linalg.norm(LUZ)


def mix(a, b, t):
    return tuple(float(a[i]) * (1 - t) + float(b[i]) * t for i in range(3))


def esc(c, k):
    return tuple(float(min(255, max(0, v * k))) for v in c[:3])


def tonos(base, pal):
    t = dict(
        alta=mix(esc(base, 1.38), pal['sol'], .25),
        luz=mix(esc(base, 1.16), pal['luz'], .16),
        med=mix(base, pal['dom'], .08),
        som=mix(esc(base, .60), pal['sombra'], .40),
        prof=mix(esc(base, .32), pal['contorno'], .5),
    )
    t['lit'] = mix(t['luz'], t['med'], .35)
    t['bor'] = mix(t['prof'], t['som'], .35)
    return t


def ruido(h, w, escala, rng, octs=2):
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octs):
        s = max(2.0, escala / (2 ** o))
        gh, gw = max(2, int(h / s) + 2), max(2, int(w / s) + 2)
        g = rng.random((gh, gw)).astype(np.float32)
        out += cv2.resize(g, (w, h), interpolation=cv2.INTER_CUBIC) * amp
        tot += amp
        amp *= .5
    return out / tot


def curva(p0, a, largo, curv=0.0, n=14, wig=0.0, fase=0.0):
    """Polilinea desde p0 con rumbo a (rad desde 'arriba', horario)."""
    t = np.linspace(0, 1, n)
    ang = a + curv * t ** 1.3 + wig * np.sin(t * 6.0 + fase)
    ds = largo / (n - 1)
    dx = np.sin(ang) * ds
    dy = -np.cos(ang) * ds
    x = p0[0] + np.concatenate([[0], np.cumsum(dx[:-1])])
    y = p0[1] + np.concatenate([[0], np.cumsum(dy[:-1])])
    return np.stack([x, y], 1), ang


_PERF = {}


def perfil(forma, n):
    k = (forma, n)
    if k in _PERF:
        return _PERF[k]
    t = np.linspace(0, 1, n)
    if forma == 'lanza':
        w = np.sin(np.pi * t ** .8)
    elif forma == 'lengua':
        w = np.sin(np.pi * t ** 1.6) ** .62
        w = np.where(t > .95, w * .8, w)
    elif forma == 'cinta':
        w = np.minimum(1, np.minimum(t * 9, (1 - t) * 4.5)) ** .8
    elif forma == 'aguja':
        w = np.minimum(1, t * 8) * (1 - t) ** .85
    elif forma == 'rombo':
        w = 1 - np.abs(2 * t - 1) ** 1.3
    elif forma == 'ovada':
        w = np.sin(np.pi * t ** 1.2) ** .7
    elif forma == 'lobada':
        w = np.sin(np.pi * t ** .8) * (1 + .3 * np.cos(2 * np.pi * 2.5 * t))
    else:
        w = np.sin(np.pi * t)
    w = np.clip(w, 0, 1.2)
    w[0] = max(w[0], 0.02)
    _PERF[k] = w
    return w


class Lienzo:
    def __init__(self, w, h, pal, seed, ss):
        self.w, self.h = int(w), int(h)
        self.buf = np.zeros((self.h, self.w, 4), np.uint8)
        self.pal = pal
        self.rng = np.random.default_rng(seed)
        self.ss = ss
        self.H = 1.0

    # ---- utilidades de color
    def elegir(self, lista, var=.12):
        r = self.rng
        a = lista[int(r.integers(0, len(lista)))]
        b = lista[int(r.integers(0, len(lista)))]
        c = mix(a, b, r.uniform(0, .6))
        return esc(c, 1 + r.uniform(-var, var))

    def tn(self, base, k=1.0):
        return tonos(esc(base, k), self.pal)

    # ---- primitivas
    def P(self, pts):
        return np.round(np.asarray(pts, np.float64) * 16).astype(np.int32)

    def poly(self, pts, col, a=255):
        cv2.fillPoly(self.buf, [self.P(pts)], (col[0], col[1], col[2], a), cv2.LINE_AA, 4)

    def linea(self, pts, col, th=1, cerrado=False):
        cv2.polylines(self.buf, [self.P(pts)], cerrado, (col[0], col[1], col[2], 255),
                      max(1, int(round(th))), cv2.LINE_AA, 4)

    def disco(self, c, r, col):
        cv2.circle(self.buf, (int(round(c[0] * 16)), int(round(c[1] * 16))),
                   int(round(max(r, .3) * 16)), (col[0], col[1], col[2], 255), -1, cv2.LINE_AA, 4)

    def elipse(self, c, ax, ang, col):
        cv2.ellipse(self.buf, (int(round(c[0] * 16)), int(round(c[1] * 16))),
                    (int(round(max(ax[0], .3) * 16)), int(round(max(ax[1], .3) * 16))),
                    float(ang), 0, 360, (col[0], col[1], col[2], 255), -1, cv2.LINE_AA, 4)

    def mascara(self):
        return np.zeros((self.h, self.w), np.uint8)

    def mpoly(self, M, pts):
        cv2.fillPoly(M, [self.P(pts)], 255, cv2.LINE_AA, 4)

    def componer(self, rgb, a, x0, y0):
        h, w = a.shape
        reg = self.buf[y0:y0 + h, x0:x0 + w].astype(np.float32)
        a3 = a[..., None]
        reg[..., :3] = reg[..., :3] * (1 - a3) + rgb * a3
        reg[..., 3] = reg[..., 3] * (1 - a) + 255 * a
        self.buf[y0:y0 + h, x0:x0 + w] = np.clip(reg, 0, 255).astype(np.uint8)

    # ---- cinta / hoja
    def cinta(self, c, w, tn, vena=0, borde=True, nervio=True, lit=None, par=0):
        c = np.asarray(c, float)
        n = len(c)
        d = np.gradient(c, axis=0)
        d /= (np.linalg.norm(d, axis=1, keepdims=True) + 1e-9)
        nr = np.stack([-d[:, 1], d[:, 0]], 1)
        A = c + nr * w[:, None]
        B = c - nr * w[:, None]
        lado = float(np.dot(nr.mean(0), LUZ))
        if lit is not None:
            lado = lit
        li, sh = (A, B) if lado > 0 else (B, A)
        cl = tn['lit']
        self.poly(np.vstack([A, B[::-1]]), tn['som'])
        self.poly(np.vstack([li, c[::-1]]), cl)
        th = max(1, round(self.ss * .8))
        if vena:
            idx = np.linspace(1, n - 3, int(vena)).astype(int)
            cv_l = mix(cl, tn['som'], .35)
            cv_s = mix(tn['som'], tn['prof'], .45)
            for i in idx:
                j = min(n - 1, i + 2)
                self.linea([c[i], li[j]], cv_l, th)
                self.linea([c[i], sh[j]], cv_s, th)
        for k in range(par):
            f = (k + 1) / (par + 1) * 2 - 1
            pl = c + nr * (w * f)[:, None]
            self.linea(pl[1:-1], mix(cl, tn['som'], .45) if f * (1 if lado > 0 else -1) > 0 else mix(tn['som'], tn['prof'], .4), th)
        if nervio:
            self.linea(c[1:], mix(tn['luz'], tn['alta'], .5), th)
        if borde:
            self.linea(np.vstack([A, B[::-1]]), tn['bor'], th, True)

    def hoja(self, p0, a, largo, ancho, curv, forma, tn, n=9, vena=0, borde=True, nervio=True):
        c, _ = curva(p0, a, largo, curv, n)
        w = ancho * .5 * perfil(forma, n)
        self.cinta(c, w, tn, vena, borde, nervio)
        return c

    # ---- cilindro con bandas
    def cilindro(self, c, r, tn, wob=.07, textura=0, bandas=None):
        c = np.asarray(c, float)
        n = len(c)
        d = np.gradient(c, axis=0)
        d /= (np.linalg.norm(d, axis=1, keepdims=True) + 1e-9)
        nr = np.stack([-d[:, 1], d[:, 0]], 1)
        if np.dot(nr.mean(0), LUZ) > 0:      # u=-1 siempre del lado de la luz
            nr = -nr
        t = np.linspace(0, 1, n)
        ph = self.rng.uniform(0, 6.28, 6)
        lim = [-1, -.74, -.20, .26, .70, 1.0]
        cols = bandas or [tn['med'], tn['luz'], tn['med'], tn['som'], tn['prof']]
        us = []
        for k, u in enumerate(lim):
            if k in (0, len(lim) - 1):
                us.append(np.full(n, u))
            else:
                us.append(u + wob * np.sin(t * (5 + 2 * k) + ph[k]))
        for k in range(len(cols)):
            ua, ub = us[k], us[k + 1]
            pa = c + nr * (r * ua)[:, None]
            pb = c + nr * (r * ub)[:, None]
            self.poly(np.vstack([pa, pb[::-1]]), cols[k])
        # brillo fino
        hi = c + nr * (r * (-.5 + wob * np.sin(t * 7 + ph[0])))[:, None]
        self.linea(hi[1:-1], tn['alta'], max(1, round(self.ss * .9)))
        return c, d, nr

    def ramas_fibra(self, c, r, tn, nlin, largo_rel=.25):
        """Estrias longitudinales finas sobre un cilindro."""
        n = len(c)
        d = np.gradient(c, axis=0)
        d /= (np.linalg.norm(d, axis=1, keepdims=True) + 1e-9)
        nr = np.stack([-d[:, 1], d[:, 0]], 1)
        if np.dot(nr.mean(0), LUZ) > 0:
            nr = -nr
        for _ in range(nlin):
            u = self.rng.uniform(-.9, .9)
            s0 = self.rng.uniform(0, 1 - largo_rel)
            s1 = s0 + self.rng.uniform(.1, 1) * largo_rel
            i0, i1 = int(s0 * (n - 1)), max(int(s0 * (n - 1)) + 2, int(s1 * (n - 1)))
            i1 = min(i1, n - 1)
            pts = c[i0:i1 + 1] + nr[i0:i1 + 1] * (r[i0:i1 + 1] * u)[:, None]
            col = tn['prof'] if u > -.3 else tn['som']
            self.linea(pts, col, max(1, round(self.ss * .8)))

    # ---- masa sombreada por relieve
    def masa(self, M, tn, relieve=1.0, rug=.35, esc_rug=None, musgo=None, grietas=0, caras=0):
        ss = self.ss
        bb = cv2.boundingRect((M > 8).astype(np.uint8))
        if bb[2] < 3 or bb[3] < 3:
            return
        pad = 3
        x0, y0 = max(0, bb[0] - pad), max(0, bb[1] - pad)
        x1, y1 = min(self.w, bb[0] + bb[2] + pad), min(self.h, bb[1] + bb[3] + pad)
        sub = M[y0:y1, x0:x1]
        hh, ww = sub.shape
        m8 = (sub > 127).astype(np.uint8)
        dist = cv2.distanceTransform(m8, cv2.DIST_L2, 3)
        md = float(dist.max()) + 1e-6
        dd = np.clip(dist, 0, md)
        hg = np.sqrt(dd * (2 * md - dd)) * relieve
        rg = self.rng
        nz = ruido(hh, ww, esc_rug or md * .55, rg, 3)
        hg = hg + (nz - .5) * md * rug * 2
        if caras:
            hg = np.round(hg / (md * .22)) * (md * .22) * .5 + hg * .5
        hg = cv2.GaussianBlur(hg, (0, 0), max(.8, md * .045))
        gy, gx = np.gradient(hg)
        nzv = np.ones_like(gx)
        inv = 1 / np.sqrt(gx * gx + gy * gy + nzv)
        nx, ny, nzz = -gx * inv, -gy * inv, nzv * inv
        Lv = np.array([LUZ[0] * .75, LUZ[1] * .75, .62])
        Lv /= np.linalg.norm(Lv)
        lam = nx * Lv[0] + ny * Lv[1] + nzz * Lv[2]
        lam = lam + (ruido(hh, ww, max(3, ss * 3), rg, 1) - .5) * .30
        cols = np.array([tn['prof'], tn['som'], tn['med'], tn['luz'], tn['alta']], np.float32)
        idx = np.digitize(lam, [-.18, .20, .55, .86])
        rgb = cols[idx]
        if musgo is not None:
            mc = np.array([musgo['prof'], musgo['som'], musgo['med'], musgo['luz'], musgo['alta']], np.float32)
            nzm = ruido(hh, ww, md * .35, rg, 3)
            mm = ((-ny) > (.22 + (nzm - .5) * .9)) & (m8 > 0)
            mm = cv2.GaussianBlur(mm.astype(np.float32), (0, 0), 1.0) > .5
            idm = np.digitize(lam + .1, [-.18, .20, .55, .86])
            rgb = np.where(mm[..., None], mc[idm], rgb)
        if grietas:
            im = np.ascontiguousarray(rgb.astype(np.uint8))
            for _ in range(grietas):
                px = rg.uniform(.15, .85) * ww
                py = rg.uniform(.15, .85) * hh
                pts = [(px, py)]
                a = rg.uniform(0, 6.28)
                for _k in range(int(rg.integers(3, 7))):
                    a += rg.uniform(-.8, .8)
                    step = rg.uniform(.05, .14) * md
                    pts.append((pts[-1][0] + np.cos(a) * step, pts[-1][1] + np.sin(a) * step))
                cv2.polylines(im, [np.round(np.array(pts) * 16).astype(np.int32)], False,
                              tuple(int(v) for v in tn['prof']), max(1, int(ss * .8)), cv2.LINE_AA, 4)
            rgb = im.astype(np.float32)
        self.componer(rgb, sub.astype(np.float32) / 255.0, x0, y0)
        return nx, ny, (x0, y0, x1, y1)

    # ---- terminar
    def final(self, base, h_px, contorno=1.7, grano=6.5, mott=.11, luzv=.34, cola=True):
        pal = self.pal
        ss = self.ss
        buf = self.buf.astype(np.float32)
        al = buf[..., 3] / 255.0
        rgb = buf[..., :3] / np.maximum(al[..., None], 1e-3)
        ys = np.where(al.max(1) > .04)[0]
        xs = np.where(al.max(0) > .04)[0]
        if len(ys) == 0:
            return Image.new('RGBA', (4, 4))
        y0, y1, x0, x1 = ys[0], ys[-1], xs[0], xs[-1]
        yn = np.clip((np.arange(self.h) - y0) / (y1 - y0 + 1), 0, 1)[:, None, None]
        xn = np.clip((np.arange(self.w) - x0) / (x1 - x0 + 1), 0, 1)[None, :, None]
        f = 1 + luzv * (.55 - yn) - .10 * xn
        rgb = rgb * f
        sb = np.array(pal['sombra'], np.float32)
        k = .26 * yn ** 2.2
        rgb = rgb * (1 - k) + sb * .55 * k
        nz = ruido(self.h, self.w, 16 * ss, self.rng, 3)
        rgb = rgb * (1 + (nz[..., None] - .5) * 2 * mott)
        rgb = np.clip(rgb, 0, 255)
        kk = max(1, int(round(contorno * ss)))
        ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * kk + 1, 2 * kk + 1))
        dil = cv2.dilate(al.astype(np.float32), ker)
        dil = cv2.GaussianBlur(dil, (0, 0), .45 * ss)
        A = np.maximum(al, dil)
        cont = np.array(pal['contorno'], np.float32)
        pm = rgb * al[..., None] + cont * (A - al)[..., None]
        out = np.dstack([pm, A * 255.0]).astype(np.float32)
        # recorte: base abajo-centro
        bx, by = base
        ys = np.where(A.max(1) > .04)[0]
        xs = np.where(A.max(0) > .04)[0]
        ya, yb = ys[0], ys[-1] + 1
        half = int(np.ceil(max(bx - xs[0], xs[-1] + 1 - bx)))
        xa, xb = int(round(bx)) - half, int(round(bx)) + half
        pl, pr = max(0, -xa), max(0, xb - self.w)
        if pl or pr:
            out = cv2.copyMakeBorder(out, 0, 0, pl, pr, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
            xa += pl
            xb += pl
        out = out[ya:yb, xa:xb]
        sc = h_px / out.shape[0]
        nw = max(2, int(round(out.shape[1] * sc)))
        out = cv2.resize(out, (nw, int(h_px)), interpolation=cv2.INTER_AREA if sc < 1 else cv2.INTER_LINEAR)
        a = out[..., 3:4] / 255.0
        rgbf = out[..., :3] / np.maximum(a, 1e-3)
        g = self.rng.normal(0, grano, out.shape[:2]).astype(np.float32)
        g2 = cv2.GaussianBlur(self.rng.normal(0, 1, out.shape[:2]).astype(np.float32), (0, 0), 1.2) * grano * 1.6
        rgbf = rgbf + (g + g2)[..., None]
        res = np.dstack([np.clip(rgbf, 0, 255), np.clip(a[..., 0] * 255, 0, 255)]).astype(np.uint8)
        return Image.fromarray(res, 'RGBA')


def nuevo(seed, h_px, pal, wf, hf=1.25):
    ss = 2.0 if h_px <= 450 else (1.5 if h_px <= 750 else 1.0)
    H = h_px * ss
    L = Lienzo(H * wf, H * hf, pal, seed, ss)
    L.H = H
    base = (L.w / 2.0, L.h - 3 * ss)
    return L, base, H, ss
