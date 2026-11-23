"""Terreno y fondos: cielos degradados con nubes/bruma, montanas lejanas en capas,
franjas de suelo irregulares (arcilla, arena, barro, lecho seco), charcos con reflejo y rio.
Todas devuelven PIL.Image RGBA del tamano pedido (w, h)."""
import numpy as np
import cv2
from PIL import Image
from scipy.spatial import cKDTree
from pintura import ruido, mix

_f32 = np.float32


def _fbm1(n, rg, octs=5, base=3, gain=.5, rid=False):
    x = np.linspace(0, 1, n)
    out = np.zeros(n)
    amp, tot = 1.0, 0.0
    for o in range(octs):
        k = base * 2 ** o
        pts = rg.random(k + 3)
        f = x * k
        i = np.floor(f).astype(int)
        t = f - i
        t = t * t * (3 - 2 * t)
        v = pts[i] * (1 - t) + pts[i + 1] * t
        if rid:
            v = 1 - np.abs(2 * v - 1)
        out += v * amp
        tot += amp
        amp *= gain
    return out / tot


def _aniso(h, w, sy, sx, rg, octs=2):
    """Ruido anisotropico (rasgos alargados): celdas de sy x sx pixeles."""
    out = np.zeros((h, w), _f32)
    amp, tot = 1.0, 0.0
    for o in range(octs):
        gh, gw = max(2, int(h / (sy / 2 ** o)) + 2), max(2, int(w / (sx / 2 ** o)) + 2)
        g = rg.random((gh, gw)).astype(_f32)
        out += cv2.resize(g, (w, h), interpolation=cv2.INTER_CUBIC) * amp
        tot += amp
        amp *= .5
    return out / tot


def _grad(cols, t):
    """Interpola una lista de colores en t (array 0..1) -> (...,3)."""
    cols = np.array(cols, _f32)
    n = len(cols) - 1
    p = np.clip(t, 0, 1) * n
    i = np.clip(np.floor(p).astype(int), 0, n - 1)
    f = (p - i)[..., None]
    return cols[i] * (1 - f) + cols[i + 1] * f


def _rgba(rgb, a):
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(a * 255, 0, 255)]).astype(np.uint8), 'RGBA')


def _grano(rgb, rg, k=4.0):
    h, w = rgb.shape[:2]
    return rgb + rg.normal(0, k, (h, w, 1)).astype(_f32)


# ------------------------------------------------------------------ cielo
def cielo(w, h, pal, seed=0, nubes=True, sol_x=None, bruma=True, densidad=.5):
    rg = np.random.default_rng(seed)
    y = np.linspace(0, 1, h, dtype=_f32)[:, None]
    cs = pal['cielo']
    rgb = _grad([cs[0], cs[1], cs[2]], np.broadcast_to(y ** .85, (h, w)))
    sx = (rg.uniform(.2, .8) if sol_x is None else sol_x) * w
    yy, xx = np.mgrid[0:h, 0:w].astype(_f32)
    d2 = ((xx - sx) / (w * .38)) ** 2 + ((yy - h * .92) / (h * .55)) ** 2
    glow = np.exp(-d2 * 1.6)[..., None]
    sol = np.array(pal['sol'], _f32)
    rgb = rgb * (1 - glow * .55) + sol * glow * .55
    if nubes:
        sc = max(8, h // 7)
        n1 = _aniso(h, w, h / 5.0, w / 2.2, rg, 4)
        n2 = _aniso(h, w, h / 5.0, w / 2.2, rg, 4)
        m = np.clip((n1 - (1 - densidad) + .02) * 4.5, 0, 1)
        band = np.clip(1.2 - np.abs(y - .55) * 2.2, 0, 1)
        m = m * band
        m = cv2.GaussianBlur(m, (0, 0), 1.2)
        shift = max(2, h // 40)
        n1s = np.roll(n1, -shift, axis=0)
        lit = np.clip(.5 + (n1 - n1s) * 9, 0, 1)[..., None]
        c_l = np.array(mix(pal['luz'], (255, 255, 255), .25), _f32)
        c_s = np.array(mix(pal['sombra'], cs[1], .55), _f32)
        cc = c_s * (1 - lit) + c_l * lit
        cc = cc * (1 - glow * .3) + sol * glow * .3
        rgb = rgb * (1 - m[..., None] * .82) + cc * m[..., None] * .82
    if bruma:
        hz = (y ** 3.0 * .55)[..., None] * np.ones((1, w, 1), _f32)
        rgb = rgb * (1 - hz) + np.array(pal['bruma'], _f32) * hz
    rgb = _grano(rgb, rg, 2.5)
    return _rgba(rgb, np.ones((h, w), _f32))


# ------------------------------------------------------------------ montanas
def montanas(w, h, pal, seed=0, capas=3, altura=.55, bruma=.38):
    """Siluetas de montanas lejanas en capas con bruma atmosferica. Fondo transparente."""
    rg = np.random.default_rng(seed)
    rgb = np.zeros((h, w, 3), _f32)
    A = np.zeros((h, w), _f32)
    xs = np.arange(w)
    yy = np.arange(h, dtype=_f32)[:, None]
    hz = np.array(pal['bruma'], _f32)
    for i in range(capas):
        t = i / max(1, capas - 1)                     # 0 lejos -> 1 cerca
        amp = h * (altura * (.55 + .45 * t)) * rg.uniform(.7, 1.0)
        base = h * (.62 + .30 * t)
        f = _fbm1(w, rg, 6, 2 + i, .5, rid=rg.random() < .6 + .2 * (1 - t))
        f = f * .6 + _fbm1(w, rg, 3, 1, .5) * .4
        ridge = base - amp * (f - .1)
        mask = (yy >= ridge[None, :]).astype(_f32)
        col = np.array(mix(mix(pal['montana'][1], pal['montana'][0], t), pal['sombra'], .35 - .15 * t), _f32)
        k = bruma * (1 - .75 * t)
        col = col * (1 - k) + hz * k
        # facetas: rasgos inclinados de luz/sombra
        tex = _aniso(h, w, h / 3.0, w / (14 + 6 * (1 - t)), rg, 3)
        shear = (np.arange(h)[:, None] * (.35 + .2 * t)).astype(int)
        tex = np.take_along_axis(tex, ((np.arange(w)[None, :] + shear) % w), axis=1)
        sh = 1 + (tex - .5) * (.5 - .25 * (1 - t))
        # luz por pendiente: lado izquierdo de picos mas claro
        slope = np.gradient(ridge)
        sl = cv2.GaussianBlur(np.broadcast_to(slope[None, :], (h, w)).copy(), (0, 0), 6)
        sh = sh * (1 + np.clip(-sl * .06, -.25, .25))
        face = col * sh[..., None]
        # bruma al pie y cresta iluminada
        depth = np.clip((yy - ridge[None, :]) / (h * (.5 - .2 * t)), 0, 1)
        kk = (depth ** 1.4 * .5 * (1 - .5 * t))[..., None]
        face = face * (1 - kk) + hz * kk
        rim = np.clip(1 - (yy - ridge[None, :]) / (2.5 + 2 * t), 0, 1)[..., None] * (.35 * (1 - t) + .2)
        face = face * (1 - rim) + np.array(pal['luz'], _f32) * rim
        a = mask
        a = cv2.GaussianBlur(a, (0, 0), .7)
        rgb = rgb * (1 - a[..., None]) + face * a[..., None]
        A = np.maximum(A, a)
    rgb = _grano(rgb, rg, 2)
    return _rgba(rgb, A)


# ------------------------------------------------------------------ suelo
_TIPOS = {
    'arcilla': ((165, 78, 52), .30),
    'arena': ((218, 192, 142), .45),
    'barro': ((84, 62, 46), .35),
    'lecho': ((176, 152, 120), .35),
}


def _grietas(h, w, rg, celda, ydeform=1.6):
    s = 2
    hh, ww = h // s, w // s
    n = int(ww * hh / (celda / s) ** 2 * 1.2) + 4
    px = rg.random(n) * ww
    py = (rg.random(n) ** (1 / ydeform)) * hh
    tree = cKDTree(np.stack([px, py], 1))
    gy, gx = np.mgrid[0:hh, 0:ww]
    yw = (gy / hh) ** ydeform * hh
    pts = np.stack([gx.ravel(), yw.ravel()], 1)
    pw = np.stack([px, (py / hh) ** ydeform * hh], 1)
    tree = cKDTree(pw)
    d, idx = tree.query(pts, k=2)
    edge = (d[:, 1] - d[:, 0]).reshape(hh, ww)
    cid = idx[:, 0].reshape(hh, ww)
    tone = (rg.random(n).astype(_f32) - .5)[cid]
    sc = (celda / s) * .12 * (.4 + gy / hh * 1.0)
    crack = np.clip(1 - edge / np.maximum(sc, .8), 0, 1)
    crack = cv2.resize(crack.astype(_f32), (w, h), interpolation=cv2.INTER_LINEAR)
    tone = cv2.resize(tone.astype(_f32), (w, h), interpolation=cv2.INTER_NEAREST)
    return crack, tone


def suelo(w, h, pal, seed=0, tipo='arcilla', piedras=12, irregular=.18, grietas=None):
    """Franja de suelo horizontal; borde superior irregular (alfa), mas lejano arriba."""
    rg = np.random.default_rng(seed)
    base_t = _TIPOS[tipo]
    sc = pal['suelo']
    cl, cm, co = [np.array(mix(c, base_t[0], base_t[1]), _f32) for c in sc]
    yy, xx = np.mgrid[0:h, 0:w].astype(_f32)
    edge = h * (.06 + irregular * (_fbm1(w, rg, 5, 3) - .5) + irregular * .6 * _fbm1(w, rg, 3, 9) * .5)
    edge = np.clip(edge, 1, h * .45)
    t = np.clip((yy - edge[None, :]) / (h - edge[None, :] + 1e-3), 0, 1)
    rgb = _grad([cl, cm, co], t ** .8)
    # moteado grande y estratos
    mott = ruido(h, w, max(40, w / 14), rg, 4)
    rgb *= (1 + (mott - .5) * .35)[..., None]
    strata = _aniso(h, w, h / 7.0, w / 3.0, rg, 3)
    rgb *= (1 + (strata - .5) * .30)[..., None]
    if tipo == 'arena':
        wav = np.sin((yy * (.25 + t * .1) + ruido(h, w, w / 6, rg, 3) * 40 + xx * .02)) * (.05 + .08 * t)
        rgb *= (1 + wav)[..., None]
    if tipo in ('arcilla', 'lecho') or grietas:
        celda = w / (9 if tipo == 'lecho' else 18)
        crack, tone = _grietas(h, w, rg, celda)
        amt = 1.0 if tipo == 'lecho' else .55
        rgb *= (1 + tone * .22)[..., None]
        dark = np.array(mix(co, pal['contorno'], .55), _f32)
        k = (crack * amt)[..., None]
        rgb = rgb * (1 - k) + dark * k
        hi = np.roll(crack, 2, axis=0) - crack
        rgb += np.clip(hi, 0, 1)[..., None] * 22 * amt
    if tipo == 'barro':
        wet = (ruido(h, w, w / 9, rg, 3) > .56).astype(_f32)
        wet = cv2.GaussianBlur(wet, (0, 0), 7)
        spec = (ruido(h, w, 14, rg, 2) > .62).astype(_f32) * wet
        rgb = rgb * (1 - wet[..., None] * .22) + np.array(pal['cielo'][2], _f32) * (spec[..., None] * .25)
    # bruma lejana arriba y oscurecido cercano
    hzk = ((1 - t) ** 2.5 * .35)[..., None]
    rgb = rgb * (1 - hzk) + np.array(pal['bruma'], _f32) * hzk
    rgb *= (1 - .18 * t ** 2)[..., None]
    rgb = _grano(rgb, rg, 4)
    a = np.clip((yy - edge[None, :]) + .5, 0, 1)
    # borde claro (luz) y sombra bajo el borde
    rim = np.clip(1 - (yy - edge[None, :]) / 2.5, 0, 1)[..., None]
    rgb = rgb * (1 - rim * .5) + np.array(pal['luz'], _f32) * rim * .5
    under = np.clip(1 - (yy - edge[None, :] - 2.5) / 7.0, 0, 1)[..., None] * (yy > edge[None, :] + 2.5)[..., None]
    rgb *= (1 - under * .3)
    out = _rgba(rgb, a)
    if piedras:
        from plantas import piedra
        from variar import pegar, espejo, sombra_contacto, brillo
        for i in range(piedras):
            yb = rg.uniform(.35, .98)
            ys = edge.mean() + (h - edge.mean()) * yb
            sz = int(max(6, (h * .06 + h * .22 * yb * rg.random()) * (.6 + yb * .6)))
            r = brillo(piedra(int(rg.integers(0, 1 << 30)), sz, pal), .78)
            if rg.random() < .5:
                r = espejo(r)
            x = rg.uniform(0, w)
            ex = edge[int(np.clip(x, 0, w - 1))]
            if ys < ex + 4:
                ys = ex + 4 + sz * .3
            pegar(out, sombra_contacto(r.width, pal, max(3, r.height * .12), .5), x, ys + r.height * .08)
            pegar(out, r, x, ys)
    return out


# ------------------------------------------------------------------ charco / rio
def charco(w, h, pal, seed=0, reflejo=None):
    """Charco irregular con reflejo del cielo, orilla humeda y destellos."""
    rg = np.random.default_rng(seed)
    s = 2
    m = np.zeros((h * s, w * s), np.uint8)
    th = np.linspace(0, 2 * np.pi, 90, endpoint=False)
    k = 1 + .10 * np.sin(th * rg.integers(2, 5) + rg.uniform(0, 6)) + .05 * np.sin(th * rg.integers(6, 12) + rg.uniform(0, 6))
    pts = np.stack([w * s / 2 + np.cos(th) * w * s * .48 * k, h * s / 2 + np.sin(th) * h * s * .46 * k], 1)
    cv2.fillPoly(m, [np.round(pts * 16).astype(np.int32)], 255, cv2.LINE_AA, 4)
    m = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(_f32) / 255
    dist = cv2.distanceTransform((m > .5).astype(np.uint8), cv2.DIST_L2, 3)
    dn = np.clip(dist / (min(w, h) * .25), 0, 1)
    yy = np.linspace(0, 1, h, dtype=_f32)[:, None]
    cs = pal['cielo']
    sky = _grad([cs[2], cs[1], cs[0]], np.broadcast_to(yy ** 1.2, (h, w)))
    deep = np.array(pal['agua'][1], _f32)
    rgb = sky * (.55 + .45 * dn[..., None]) * .75 + deep * (.25 * (1 - dn[..., None]) + .1)
    rip = ruido(h, w, max(4, h / 6), rg, 2)
    stripe = (np.sin(yy * h * .9 + rip * 10) > .93).astype(_f32) * dn
    rgb += stripe[..., None] * 40
    if reflejo is not None:
        r = reflejo.resize((w, h)).transpose(Image.FLIP_TOP_BOTTOM)
        ra = np.asarray(r, _f32)
        a = ra[..., 3:4] / 255 * .6 * dn[..., None]
        rgb = rgb * (1 - a) + ra[..., :3] * .8 * a
    gl = np.exp(-((np.arange(w)[None, :] - w * rg.uniform(.3, .7)) / (w * .08)) ** 2) * np.exp(-((yy - .55) / .12) ** 2)
    rgb += gl[..., None] * np.array(pal['sol'], _f32) * .35
    ring = np.clip(1 - dist / (min(w, h) * .09), 0, 1)[..., None]
    mud = np.array(mix(pal['suelo'][2], pal['contorno'], .45), _f32)
    rgb = rgb * (1 - ring * .75) + mud * ring * .75
    rgb = _grano(rgb, rg, 2)
    return _rgba(rgb, np.clip(m * 1.0, 0, 1))


def rio(w, h, pal, seed=0, sinuoso=.35, ancho=.5):
    """Franja de rio con orillas de barro y piedras; reflejo del cielo y ondas. Fondo transparente."""
    rg = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(_f32)
    yc = h * (.5 + sinuoso * .5 * (_fbm1(w, rg, 4, 2) - .5) * 1.6)
    hw = h * ancho * .5 * (.8 + .4 * _fbm1(w, rg, 3, 3))
    d = np.abs(yy - yc[None, :])
    water = np.clip((hw[None, :] - d) + .5, 0, 1)
    bank = np.clip((hw[None, :] * 1.28 + h * .05 - d) + .5, 0, 1)
    cs = pal['cielo']
    tt = np.clip((yy - (yc - hw)[None, :]) / (2 * hw[None, :] + 1), 0, 1)
    sky = _grad([cs[2], cs[1], pal['agua'][0]], tt ** 1.1)
    deep = np.array(pal['agua'][1], _f32)
    wc = sky * (.85 - .45 * tt[..., None] ** 1.3) + deep * (.15 + .45 * tt[..., None] ** 1.3)
    rip = _aniso(h, w, 5, 60, rg, 3)
    wc = wc * (1 + (rip[..., None] - .5) * .45)
    hi = (rip > .72).astype(_f32) * np.clip(1.2 - tt * 1.4, 0, 1)
    wc += hi[..., None] * 34
    sx = rg.uniform(.25, .75) * w
    gl = np.exp(-((xx - sx) / (w * .09)) ** 2) * (rip > .5)
    wc += gl[..., None] * np.array(pal['sol'], _f32) * .35
    sc = pal['suelo']
    bc = _grad([sc[0], sc[1], sc[2]], np.clip((d - hw[None, :]) / (hw[None, :] * .5 + 1), 0, 1))
    bc = bc * (1 + (ruido(h, w, 30, rg, 3)[..., None] - .5) * .4)
    wet = np.clip(1 - np.abs(d - hw[None, :]) / 5.0, 0, 1)[..., None]
    bc = bc * (1 - wet * .35)
    rgb = bc * (1 - water[..., None]) + wc * water[..., None]
    foam = np.clip(1 - np.abs(d - hw[None, :] + 1.5) / 1.6, 0, 1)[..., None] * (ruido(h, w, 8, rg, 1)[..., None] > .5)
    rgb = rgb * (1 - foam * .5) + np.array(pal['luz'], _f32) * foam * .5
    rgb = _grano(rgb, rg, 3)
    return _rgba(rgb, cv2.GaussianBlur(bank, (0, 0), .6))
