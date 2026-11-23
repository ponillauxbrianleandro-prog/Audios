"""Generadores parametricos de plantas y elementos de terreno del Paleozoico/Triasico.
Cada funcion: f(seed, h_px, pal) -> PIL.Image RGBA recortado, base de la planta en el
borde inferior-centro, altura == h_px.  Paletas: ver paletas.py."""
import numpy as np
import cv2
from PIL import Image
from pintura import (Lienzo, nuevo, curva, perfil, mix, esc, tonos, ruido, LUZ)

TAU = 2 * np.pi
_HC = {}


# ------------------------------------------------------------------ utilidades
def _hc(L, p0, a, largo, ancho, curv, forma, tn, n=7, borde=True):
    """Hoja rapida (con cache de forma): dos tonos + contorno."""
    ratio = round(ancho / largo, 2)
    key = (forma, n, round(curv, 1), ratio)
    ent = _HC.get(key)
    if ent is None:
        c, _ = curva((0, 0), 0, 1.0, curv, n)
        w = ratio * .5 * perfil(forma, n)
        d = np.gradient(c, axis=0)
        d /= (np.linalg.norm(d, axis=1, keepdims=True) + 1e-9)
        nr = np.stack([-d[:, 1], d[:, 0]], 1)
        ent = (c + nr * w[:, None], c - nr * w[:, None], c)
        _HC[key] = ent
    A, B, c = ent
    ca, sa = np.cos(a), np.sin(a)
    R = np.array([[ca, sa], [-sa, ca]])
    p0 = np.asarray(p0)
    Ap, Bp, cp = (A * largo) @ R + p0, (B * largo) @ R + p0, (c * largo) @ R + p0
    th = a + curv * .5
    lado = np.cos(th) * LUZ[0] + np.sin(th) * LUZ[1]
    li = Ap if lado > 0 else Bp
    full = np.vstack([Ap, Bp[::-1]])
    L.poly(full, tn['som'])
    L.poly(np.vstack([li, cp[::-1]]), tn['lit'])
    if borde:
        L.linea(full, tn['bor'], max(1, round(L.ss * .8)), True)
    return cp


def _caida(a, d):
    return d if np.sin(a) >= 0 else -d


def fronda(L, p0, a, largo, curv, tn, pares=18, rel=.2, ratio=.26, ap=1.15, caida=.35,
           forma='lanza', rach=1.0, tn2=None, tnr=None):
    c, ang = curva(p0, a, largo, curv, pares + 3)
    n = len(c)
    tn2 = tn2 or tn
    ss = L.ss
    for i in range(n - 2, 1, -1):
        t = i / (n - 1)
        f = np.sin(np.pi * min(1.0, t ** .8)) ** .75
        lp = largo * rel * (.2 + .8 * f)
        if lp < 2.5 * ss:
            continue
        for sd in (-1, 1):
            _hc(L, c[i], ang[i] + sd * ap, lp, lp * ratio, -sd * caida, forma,
                tn if sd < 0 else tn2, 7, lp > 11 * ss)
    wr = np.linspace(largo * .010 * rach, largo * .0025, n)
    L.cinta(c, wr, tnr or tn, borde=False, nervio=False)
    return c, ang


def _raiz_vis(L, base, H, tn, r0, n=3):
    rg = L.rng
    for k in range(n):
        s = rg.choice([-1, 1])
        a = s * rg.uniform(1.0, 1.45)
        c, _ = curva((base[0] + s * r0 * rg.uniform(.1, .6), base[1] - r0 * .45), a * .8 + s * .5, H * rg.uniform(.06, .12),
                     -s * rg.uniform(.9, 1.4), 8)
        w = np.linspace(r0 * .6, r0 * .05, 8) ** 1
        L.cinta(c, w, tn, borde=True, nervio=False)


def escamas(L, c, r, tn, ncol=10, forma='rombo', alto=1.0, denso=1.0):
    """Patron de cojinetes foliares (rombos / ovalos) sobre un tronco curvado."""
    c = np.asarray(c, float)
    r = np.asarray(r, float)
    n = len(c)
    d = np.gradient(c, axis=0)
    d /= (np.linalg.norm(d, axis=1, keepdims=True) + 1e-9)
    nr = np.stack([-d[:, 1], d[:, 0]], 1)
    if np.dot(nr.mean(0), LUZ) > 0:
        nr = -nr
    seg = np.linalg.norm(np.diff(c, axis=0), axis=1)
    sarc = np.concatenate([[0], np.cumsum(seg)])
    tot = sarc[-1]
    rg = L.rng
    ss = L.ss
    th = max(1, round(ss * .8))
    s = r[0] * .5
    j = 0
    ph = rg.uniform(0, TAU)
    cr = lambda arr, s_: np.array([np.interp(s_, sarc, arr[:, 0]), np.interp(s_, sarc, arr[:, 1])]) if arr.ndim == 2 else np.interp(s_, sarc, arr)
    while s < tot - r[-1] * .3:
        rr = cr(r, s)
        W = TAU * rr / ncol
        sy = W * alto * 1.0 / denso
        P0, dd, nn = cr(c, s), cr(d, s), cr(nr, s)
        dd = dd / (np.linalg.norm(dd) + 1e-9)
        nn = nn / (np.linalg.norm(nn) + 1e-9)
        for k in range(ncol):
            theta = (k + .5 * (j % 2)) * TAU / ncol + ph
            u = np.sin(theta)
            cs = np.cos(theta)
            if cs < .12:
                continue
            P = P0 + nn * (rr * u)
            wh = max(.6, W * .5 * cs * .92)
            hh = sy * .92
            if forma == 'rombo':
                dm = np.array([P + dd * hh, P + nn * wh, P - dd * hh, P - nn * wh])
                lit = np.array([P + dd * hh, P - nn * wh, P - dd * hh])
            else:
                a = np.arctan2(dd[1], dd[0]) * 57.3
                dm = None
            if u < -.25:
                col = tn['luz']
            elif u < .30:
                col = tn['med']
            elif u < .70:
                col = tn['som']
            else:
                col = tn['prof']
            if forma == 'rombo':
                L.poly(dm, tn['prof'] if u > .7 else tn['som'])
                inner = P + (dm - P) * .86
                L.poly(inner, col)
                L.poly(P + (lit - P) * .86, mix(col, tn['alta'], .3) if u < .3 else col)
                sc = np.array([P + dd * hh * .30, P + nn * wh * .28, P - dd * hh * .05, P - nn * wh * .28])
                L.poly(sc, tn['prof'])
            else:
                ang = np.arctan2(dd[1], dd[0]) * 57.3 + 90
                L.elipse(P, (wh * .95, hh * .8), ang, tn['prof'])
                L.elipse(P - dd * hh * .06, (wh * .78, hh * .66), ang, col)
                L.elipse(P + dd * hh * .12, (wh * .3, hh * .22), ang, tn['prof'])
        s += sy
        j += 1


def _tono_hoja(L, k=1.0, acento=.10):
    pal = L.pal
    lista = pal['hoja2'] if L.rng.random() < acento else pal['hoja']
    return L.tn(L.elegir(lista), k)


def _tuft(L, p, a, n, largo, ancho, spread, tnl, forma='aguja', caida=.45, curv_var=.3):
    rg = L.rng
    items = []
    for _ in range(n):
        da = rg.uniform(-spread, spread)
        items.append(da)
    items.sort(key=lambda x: -abs(x))
    for da in items:
        aa = a + da
        lg = largo * rg.uniform(.65, 1.12)
        cv = _caida(aa, caida * rg.uniform(.3, 1.2)) + rg.uniform(-curv_var, curv_var)
        t = tnl[0] if abs(da) > spread * .5 else tnl[1]
        _hc(L, p, aa, lg, ancho * rg.uniform(.8, 1.2) + lg * .02, cv, forma, t, 6, ancho > 3 * L.ss)


def _tuft_tones(L, k=1.0):
    return (_tono_hoja(L, .86 * k), _tono_hoja(L, 1.05 * k, .15))


def _bastago(L, c, r, tn, ruta=None):
    return L.cilindro(c, r, tn)


# ------------------------------------------------------------------ licofitas
def lepidodendron(seed, h_px, pal):
    L, base, H, ss = nuevo(seed, h_px, pal, 1.15, 1.18)
    rg = L.rng
    tb = L.tn(L.elegir(pal['corteza']))
    r0 = H * rg.uniform(.034, .05)
    th = H * rg.uniform(.42, .55)
    _raiz_vis(L, base, H, tb, r0, 4)
    n = 22
    c, ang = curva(base, rg.uniform(-.06, .06), th, rg.uniform(-.14, .14), n)
    s = np.linspace(0, 1, n)
    r = r0 * (1 - .30 * s) * (1 + .95 * np.exp(-s * 13))
    L.cilindro(c, r, tb)
    escamas(L, c, r, tb, ncol=int(rg.integers(6, 9)), alto=rg.uniform(.9, 1.3))
    tips = []

    def dico(p, a, largo, rad, prof):
        cc, aa = curva(p, a, largo, rg.uniform(-.28, .28), 9)
        rr = np.linspace(rad, rad * .8, 9)
        L.cilindro(cc, rr, tb)
        if rad > r0 * .3:
            escamas(L, cc, rr, tb, ncol=5, alto=1.2)
        if prof == 0:
            tips.append((cc[-1], aa[-1], rad))
            return
        for sd in (-1, 1):
            dico(cc[-1], aa[-1] + sd * rg.uniform(.30, .6), largo * rg.uniform(.68, .84), rad * .72, prof - 1)

    dico(c[-1], ang[-1], H * .17, r[-1] * .85, 3)
    tips.sort(key=lambda t: t[0][1])
    cone_tone = L.tn(L.elegir(pal['seco']))
    for p, a, rad in tips:
        tl = _tuft_tones(L)
        _tuft(L, p, a, int(rg.integers(26, 40)), H * rg.uniform(.11, .17), H * .011, 1.5, tl, caida=.7)
        if rg.random() < .35:
            cc, aa = curva(p, a + rg.uniform(-.5, .5), H * .06, 0, 5)
            L.cinta(cc, np.linspace(H * .007, H * .012, 5), cone_tone, borde=True, nervio=False)
    return L.final(base, h_px)


def sigillaria(seed, h_px, pal):
    L, base, H, ss = nuevo(seed, h_px, pal, .95, 1.15)
    rg = L.rng
    tb = L.tn(L.elegir(pal['corteza']))
    r0 = H * rg.uniform(.045, .06)
    _raiz_vis(L, base, H, tb, r0, 4)
    th = H * rg.uniform(.62, .78)
    n = 24
    c, ang = curva(base, rg.uniform(-.05, .05), th, rg.uniform(-.1, .1), n)
    s = np.linspace(0, 1, n)
    r = r0 * (1 - .25 * s) * (1 + .7 * np.exp(-s * 15))
    L.cilindro(c, r, tb, wob=.03)
    # costillas con cicatrices hexagonales
    nrib = int(rg.integers(7, 10))
    d = np.gradient(c, axis=0)
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    nr = np.stack([-d[:, 1], d[:, 0]], 1)
    if np.dot(nr.mean(0), LUZ) > 0:
        nr = -nr
    for k in range(nrib):
        theta = (k + .5) / nrib * np.pi - np.pi / 2 + .0
        u = np.sin(theta)
        pts = c + nr * (r * u)[:, None]
        L.linea(pts[1:], tb['prof'] if u > -.2 else tb['som'], max(1, round(ss * 1.2)))
        cs = np.cos(theta)
        nsc = int(th / (r0 * 1.5))
        for j in range(nsc):
            t = (j + .5 + .4 * (k % 2)) / nsc
            i = int(t * (n - 1))
            if i < 1:
                continue
            P = c[i] + nr[i] * r[i] * u
            col = tb['luz'] if u < -.2 else tb['med'] if u < .3 else tb['som']
            ang_d = np.arctan2(d[i][1], d[i][0]) * 57.3 + 90
            L.elipse(P, (max(.7, r[i] * .17 * cs), r0 * .55), ang_d, tb['prof'])
            L.elipse(P + d[i] * r0 * .04, (max(.5, r[i] * .13 * cs), r0 * .44), ang_d, col)
    tips = [(c[-1], ang[-1])]
    if rg.random() < .6:
        tips = []
        for sd in (-1, 1):
            cc, aa = curva(c[-1], ang[-1] + sd * .5, H * .12, -sd * .3, 7)
            L.cilindro(cc, np.linspace(r[-1] * .8, r[-1] * .6, 7), tb)
            tips.append((cc[-1], aa[-1]))
    for p, a in tips:
        tl = _tuft_tones(L)
        _tuft(L, p, a, int(rg.integers(18, 28)), H * rg.uniform(.2, .3), H * .012, 1.5, tl, 'cinta', .6, .2)
    return L.final(base, h_px)


# ------------------------------------------------------------------ colas de caballo
def _tallo_nudos(L, p0, a0, h, curv, r, tn, tnl, seg, ramillas, agujas, largo_v, rama_p=.3, nervaduras=8):
    rg = L.rng
    ss = L.ss
    n = 44
    c, ang = curva(p0, a0, h, curv, n)
    rr = np.linspace(r, r * .7, n)
    L.cilindro(c, rr, tn, wob=.03)
    L.ramas_fibra(c, rr, tn, nervaduras, .5)
    d = np.gradient(c, axis=0)
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    nr = np.stack([-d[:, 1], d[:, 0]], 1)
    s = seg * rg.uniform(.5, 1.0)
    sarc = np.arange(n) * (h / (n - 1))
    ramas = []
    while s < h * .985:
        i = int(np.clip(s / h * (n - 1), 1, n - 2))
        P, dd, nn, rad = c[i], d[i], nr[i], rr[i]
        # nudo oscuro + vaina dentada
        ring = np.array([P - nn * rad * 1.1 - dd * rad * .13, P + nn * rad * 1.1 - dd * rad * .13,
                         P + nn * rad * 1.1 + dd * rad * .22, P - nn * rad * 1.1 + dd * rad * .22])
        L.poly(ring, tn['prof'])
        L.poly(ring * .0 + np.array([P - nn * rad * 1.0 + dd * rad * .02, P + nn * rad * 1.0 + dd * rad * .02,
                                      P + nn * rad * 1.0 + dd * rad * .16, P - nn * rad * 1.0 + dd * rad * .16]), tn['som'])
        L.poly(np.array([P - nn * rad * 1.0 + dd * rad * .02, P - nn * rad * .25 + dd * rad * .02,
                         P - nn * rad * .25 + dd * rad * .16, P - nn * rad * 1.0 + dd * rad * .16]), tn['luz'])
        for k in range(5):
            u = -.8 + k * .4
            Q = P + nn * rad * u + dd * rad * .22
            L.poly([Q - nn * rad * .17, Q + nn * rad * .17, Q + dd * rad * .55 + nn * rad * .02], tn['prof'] if u > 0 else tn['som'])
        t = i / (n - 1)
        if t > .12:
            # verticilo de agujas o ramillas
            m = agujas
            lv = largo_v * (1 - .55 * t)
            for sdir in rg.permutation(m):
                sd = -1 if sdir % 2 == 0 else 1
                fr = rg.uniform(.35, 1.0)
                aa = ang[i] + sd * rg.uniform(.45, 1.35) * (1.0 if fr > .5 else .6)
                lg = lv * fr
                tl = tnl[0] if sd < 0 else tnl[1]
                _hc(L, P + nn * rad * .6 * sd, aa, lg, max(1.4 * ss, lg * .06), -sd * rg.uniform(.1, .5) - .2 * np.sign(np.sin(aa)),
                    'aguja', tl, 6, False)
            if ramillas and rg.random() < rama_p and t < .85:
                ramas.append((P.copy(), ang[i], int(rg.choice([-1, 1])), t))
        s += seg * rg.uniform(.75, 1.25) * (1 - .35 * s / h)
    for P, a, sd, t in ramas:
        hh = h * rg.uniform(.16, .26) * (1 - .5 * t)
        cc, aa = curva(P, a + sd * rg.uniform(.7, 1.2), hh, -sd * rg.uniform(.6, 1.1), 12)
        rb = np.linspace(r * .26, r * .12, 12)
        L.cilindro(cc, rb, tn, wob=.0)
        for q in range(2, 11, 3):
            for sd2 in (-1, 1):
                _hc(L, cc[q], aa[q] + sd2 * .9, hh * .16, max(1.2 * ss, hh * .012), -sd2 * .3, 'aguja', tnl[(q + sd2) % 2], 5, False)
    return c, ang


def calamites(seed, h_px, pal):
    L, base, H, ss = nuevo(seed, h_px, pal, 1.0, 1.15)
    rg = L.rng
    tb = L.tn(mix(L.elegir(pal['hoja']), L.elegir(pal['corteza']), .45))
    tl = (_tono_hoja(L, .85), _tono_hoja(L, 1.05))
    ns = int(rg.integers(3, 6))
    xs = np.sort(rg.uniform(-.2, .2, ns) * H)
    order = np.argsort(-np.abs(xs - xs.mean()) - rg.uniform(0, .05, ns) * H)
    for idx in order:
        x = xs[idx]
        h = H * rg.uniform(.55, 1.0) * (1 - abs(x) / H * .6)
        a0 = x / H * 1.6 + rg.uniform(-.1, .1)
        _tallo_nudos(L, (base[0] + x, base[1]), a0, h, rg.uniform(-.18, .18), H * rg.uniform(.016, .026),
                     L.tn(mix(L.elegir(pal['hoja']), L.elegir(pal['corteza']), .45), rg.uniform(.85, 1.1)),
                     tl, H * rg.uniform(.07, .1), True, 9, H * rg.uniform(.07, .10))
    return L.final(base, h_px)


def equisetum(seed, h_px, pal):
    L, base, H, ss = nuevo(seed, h_px, pal, .8, 1.15)
    rg = L.rng
    tl = (_tono_hoja(L, .9), _tono_hoja(L, 1.1))
    ns = int(rg.integers(3, 7))
    xs = rg.uniform(-.22, .22, ns) * H
    for idx in np.argsort(rg.uniform(0, 1, ns)):
        x = xs[idx]
        h = H * rg.uniform(.6, 1.0)
        tb = L.tn(mix(L.elegir(pal['hoja']), L.elegir(pal['seco']), .25), rg.uniform(.9, 1.15))
        c, ang = _tallo_nudos(L, (base[0] + x, base[1]), x / H * 1.2 + rg.uniform(-.08, .08), h, rg.uniform(-.1, .1),
                              H * rg.uniform(.009, .013), tb, tl, H * rg.uniform(.05, .07), False, 11, H * .085,
                              nervaduras=6)
        # estrobilo terminal
        P, a = c[-1], ang[-1]
        cc, _ = curva(P, a, H * .05, 0, 5)
        L.cinta(cc, np.array([.2, 1, 1, .9, .1]) * H * .0085, L.tn(L.elegir(pal['seco'])), borde=True, nervio=False)
    return L.final(base, h_px)


# ------------------------------------------------------------------ helechos con semilla
def glossopteris(seed, h_px, pal):
    L, base, H, ss = nuevo(seed, h_px, pal, 1.2, 1.15)
    rg = L.rng
    tb = L.tn(L.elegir(pal['corteza']))
    r0 = H * rg.uniform(.016, .024)
    th = H * rg.uniform(.36, .5)
    n = 18
    c, ang = curva(base, rg.uniform(-.1, .1), th, rg.uniform(-.2, .2), n)
    r = np.linspace(r0, r0 * .7, n) * (1 + .6 * np.exp(-np.linspace(0, 1, n) * 12))
    _raiz_vis(L, base, H, tb, r0, 2)
    L.cilindro(c, r, tb)
    L.ramas_fibra(c, r, tb, 6, .4)
    tufts = []
    nb = int(rg.integers(3, 6))
    for k in range(nb):
        t = rg.uniform(.55, 1.0) if k else 1.0
        i = int(t * (n - 1))
        a = ang[i] + (rg.uniform(-1.1, 1.1) if k else rg.uniform(-.2, .2))
        cc, aa = curva(c[i], a, H * rg.uniform(.09, .2), rg.uniform(-.4, .4), 8)
        L.cilindro(cc, np.linspace(r[i] * .55, r[i] * .35, 8), tb, wob=0)
        tufts.append((cc[-1], aa[-1]))
    tufts.sort(key=lambda t: t[0][1])
    for p, a in tufts:
        tl = (_tono_hoja(L, .9, .2), _tono_hoja(L, 1.08, .2))
        nl = int(rg.integers(7, 11))
        angs = np.linspace(-1.6, 1.6, nl) + rg.uniform(-.15, .15, nl)
        for da in sorted(angs, key=lambda x: -abs(x)):
            lg = H * rg.uniform(.2, .3) * (1 - .25 * abs(da) / 1.6)
            L.hoja(p, a + da, lg, lg * rg.uniform(.2, .27), _caida(a + da, rg.uniform(.35, .9)) * (abs(da) / 1.6 + .3),
                   'lengua', tl[0] if abs(da) > .8 else tl[1], 10, vena=int(max(5, lg / (10 * ss))), borde=True)
    return L.final(base, h_px)


def _horq(L, p0, a, largo, curv, tn, tn2, niv):
    rg = L.rng
    c, ang = curva(p0, a, largo * .30, curv * .3, 6)
    L.cinta(c, np.linspace(largo * .011, largo * .008, 6), tn, borde=False, nervio=False)
    fin = c[-1]
    for sd in (-1, 1):
        a2 = ang[-1] + sd * rg.uniform(.35, .6)
        lg = largo * rg.uniform(.62, .78)
        if niv > 1:
            _horq(L, fin, a2, lg, curv * .6 + sd * .2, tn, tn2, niv - 1)
        else:
            fronda(L, fin, a2, lg, curv * .6 + sd * .3, tn, pares=int(rg.integers(11, 15)), rel=.25, ratio=.5,
                   ap=1.0, caida=.2, forma='lobada', tn2=tn2, rach=.9)


def dicroidium(seed, h_px, pal):
    L, base, H, ss = nuevo(seed, h_px, pal, 1.25, 1.1)
    rg = L.rng
    tb = L.tn(L.elegir(pal['corteza']))
    th = H * rg.uniform(.22, .34)
    r0 = H * rg.uniform(.016, .022)
    n = 12
    c, ang = curva(base, rg.uniform(-.08, .08), th, rg.uniform(-.2, .2), n)
    r = np.linspace(r0, r0 * .75, n) * (1 + .6 * np.exp(-np.linspace(0, 1, n) * 12))
    L.cilindro(c, r, tb)
    nf = int(rg.integers(6, 10))
    angs = np.linspace(-1.35, 1.35, nf) + rg.uniform(-.12, .12, nf)
    for da in sorted(angs, key=lambda x: -abs(x)):
        tn = _tono_hoja(L, .9 + .15 * (1 - abs(da) / 1.4), .15)
        tn2 = _tono_hoja(L, 1.05, .15)
        lg = H * rg.uniform(.42, .6) * (1 - .25 * abs(da) / 1.35)
        _horq(L, c[-1], da, lg, _caida(da, rg.uniform(.5, 1.1)), tn, tn2, 1 if rg.random() < .6 else 2)
    return L.final(base, h_px)


# ------------------------------------------------------------------ helechos arboreos
def _helecho_arboreo(seed, h_px, pal, tipo):
    L, base, H, ss = nuevo(seed, h_px, pal, 1.15, 1.15)
    rg = L.rng
    tb = L.tn(L.elegir(pal['corteza']), .9)
    th = H * rg.uniform(.44, .58)
    n = 22
    r0 = H * (rg.uniform(.04, .05) if tipo == 'psaronius' else rg.uniform(.028, .036))
    c, ang = curva(base, rg.uniform(-.06, .06), th, rg.uniform(-.18, .18), n)
    s = np.linspace(0, 1, n)
    r = r0 * (1 - .2 * s) * (1 + (1.1 if tipo == 'psaronius' else .6) * np.exp(-s * 10))
    if tipo == 'psaronius':
        _raiz_vis(L, base, H, tb, r0 * 1.2, 5)
    else:
        _raiz_vis(L, base, H, tb, r0, 2)
    L.cilindro(c, r, tb, wob=.1)
    if tipo == 'psaronius':
        # manto de raices aereas: fibras oscuras onduladas
        d = np.gradient(c, axis=0)
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        nr = np.stack([-d[:, 1], d[:, 0]], 1)
        if np.dot(nr.mean(0), LUZ) > 0:
            nr = -nr
        for _ in range(int(r0 / ss * .9) + 18):
            u = rg.uniform(-.95, .95)
            i0 = int(rg.uniform(0, .85) * (n - 1))
            i1 = min(n - 1, i0 + int(rg.integers(2, 8)))
            pts = c[i0:i1 + 1] + nr[i0:i1 + 1] * (r[i0:i1 + 1] * (u + .05 * np.sin(np.arange(i1 - i0 + 1) * 1.7)))[:, None]
            col = tb['prof'] if u > -.2 else tb['som']
            L.linea(pts, col, max(1, round(ss * rg.uniform(.8, 1.8))))
            if len(pts) > 2 and u < .3:
                L.linea(pts + np.array([ss * .8, 0]), tb['luz'], max(1, round(ss * .8)))
    else:
        escamas(L, c, r, tb, ncol=8, forma='ovalo', alto=1.1)
    # corona de frondas
    top, a_top = c[-1], ang[-1]
    nf = int(rg.integers(10, 15))
    angs = np.linspace(-1.75, 1.75, nf) + rg.uniform(-.14, .14, nf)
    # baculos
    for _ in range(int(rg.integers(2, 4))):
        a = a_top + rg.uniform(-.5, .5)
        cc, _a = curva(top, a, H * .09, _caida(a, .5), 8)
        L.cinta(cc, np.linspace(H * .007, H * .004, 8), L.tn(L.elegir(pal['hoja'])), borde=True, nervio=False)
        ctr = cc[-1]
        sp = [ctr + (H * .014 * (1 - t / 9)) * np.array([np.cos(t * .9 + a), np.sin(t * .9 + a)]) for t in np.arange(0, 9)]
        L.linea(sp, L.tn(L.elegir(pal['hoja']))['luz'], max(2, round(ss * 3)))
    for k, da in enumerate(sorted(angs, key=lambda x: -abs(x))):
        up = 1 - abs(da) / 1.8
        tn = _tono_hoja(L, .84 + .22 * up, .1)
        tn2 = _tono_hoja(L, 1.0 + .1 * up, .1)
        lg = H * rg.uniform(.34, .52) * (.62 + .38 * (1 - up * .5))
        fronda(L, top, a_top + da, lg, _caida(da, rg.uniform(.9, 1.7)) * (.5 + abs(da) / 1.8),
               tn, pares=int(rg.integers(16, 23)), rel=.19, ratio=.24, ap=1.13, caida=.3,
               forma='lobada' if tipo == 'cyathea' else 'lanza', tn2=tn2)
    return L.final(base, h_px)


def psaronius(seed, h_px, pal):
    return _helecho_arboreo(seed, h_px, pal, 'psaronius')


def cyathea(seed, h_px, pal):
    return _helecho_arboreo(seed, h_px, pal, 'cyathea')


# ------------------------------------------------------------------ cordaites
def cordaites(seed, h_px, pal):
    L, base, H, ss = nuevo(seed, h_px, pal, 1.1, 1.2)
    rg = L.rng
    tb = L.tn(L.elegir(pal['corteza']), .95)
    th = H * rg.uniform(.5, .62)
    r0 = H * rg.uniform(.022, .03)
    n = 22
    c, ang = curva(base, rg.uniform(-.05, .05), th, rg.uniform(-.1, .1), n)
    s = np.linspace(0, 1, n)
    r = r0 * (1 - .4 * s) * (1 + .6 * np.exp(-s * 14))
    _raiz_vis(L, base, H, tb, r0, 3)
    L.cilindro(c, r, tb, wob=.04)
    L.ramas_fibra(c, r, tb, 14, .5)
    tips = []
    nb = int(rg.integers(3, 6))
    for k in range(nb):
        t = rg.uniform(.45, 1.0) if k < nb - 1 else 1.0
        i = int(t * (n - 1))
        a = ang[i] + (rg.uniform(.5, 1.1) * rg.choice([-1, 1]) if k < nb - 1 else rg.uniform(-.15, .15))
        cc, aa = curva(c[i], a, H * rg.uniform(.1, .2), -np.sign(a) * rg.uniform(.2, .6), 8)
        L.cilindro(cc, np.linspace(r[i] * .5, r[i] * .3, 8), tb, wob=0)
        tips.append((cc[-1], aa[-1]))
    tips.sort(key=lambda t: t[0][1])
    for p, a in tips:
        tl = (_tono_hoja(L, .9), _tono_hoja(L, 1.1))
        nl = int(rg.integers(18, 30))
        for da in sorted(rg.uniform(-1.6, 1.6, nl), key=lambda x: -abs(x)):
            lg = H * rg.uniform(.2, .34)
            aa = a + da
            cc, _ = curva(p, aa, lg, _caida(aa, rg.uniform(.7, 1.4)) + rg.uniform(-.2, .2), 12, wig=rg.uniform(0, .25), fase=rg.uniform(0, 6))
            w = lg * .04 * perfil('cinta', 12) + .3
            L.cinta(cc, w, tl[0] if abs(da) > .75 else tl[1], par=3, borde=True, nervio=False)
    return L.final(base, h_px)


# ------------------------------------------------------------------ sotobosque
def helecho_suelo(seed, h_px, pal):
    L, base, H, ss = nuevo(seed, h_px, pal, 1.9, 1.15)
    rg = L.rng
    top = (base[0], base[1] - H * .02)
    nf = int(rg.integers(11, 18))
    forma = rg.choice(['lanza', 'lobada', 'ovada'])
    angs = np.linspace(-1.5, 1.5, nf) + rg.uniform(-.12, .12, nf)
    for _ in range(int(rg.integers(1, 3))):
        a = rg.uniform(-.4, .4)
        cc, _a = curva(top, a, H * .22, _caida(a, .6), 8)
        L.cinta(cc, np.linspace(H * .012, H * .006, 8), L.tn(L.elegir(pal['hoja'])), borde=True, nervio=False)
        ctr = cc[-1]
        sp = [ctr + (H * .03 * (1 - t / 9)) * np.array([np.cos(t * .9 + a), np.sin(t * .9 + a)]) for t in np.arange(0, 9)]
        L.linea(sp, L.tn(L.elegir(pal['hoja']))['luz'], max(2, round(ss * 3)))
    for da in sorted(angs, key=lambda x: -abs(x)):
        tn = _tono_hoja(L, .84 + .2 * (1 - abs(da) / 1.6), .1)
        tn2 = _tono_hoja(L, 1.02, .1)
        lg = H * rg.uniform(.55, .9) * (1.1 - .4 * abs(da) / 1.6)
        fronda(L, top, da, lg, _caida(da, rg.uniform(1.1, 2.0)), tn, pares=int(rg.integers(18, 28)),
               rel=.2, ratio=.2, ap=1.12, caida=.25, forma=forma, tn2=tn2)
    return L.final(base, h_px)


def _blob(rg, cx, cy, rx, ry, n=36, rug=.12, plano=True):
    th = np.linspace(0, np.pi if plano else TAU, n)
    k = 1 + rug * np.sin(th * rg.integers(3, 7) + rg.uniform(0, 6)) + rug * .6 * np.sin(th * rg.integers(8, 14) + rg.uniform(0, 6))
    return np.stack([cx + np.cos(th) * rx * k, cy - np.sin(th) * ry * k], 1)


def musgo(seed, h_px, pal):
    L, base, H, ss = nuevo(seed, h_px, pal, 2.1, 1.35)
    rg = L.rng
    M = L.mascara()
    nb = int(rg.integers(3, 7))
    base_y = base[1]
    hm = H * .7
    for k in range(nb):
        cx = base[0] + rg.uniform(-.7, .7) * H
        rx = H * rg.uniform(.22, .45)
        ry = hm * rg.uniform(.45, 1.0) * (1 - abs(cx - base[0]) / H * .5)
        pts = _blob(rg, cx, base_y, rx, ry, 40, .05)
        pts = np.vstack([pts, [[cx - rx, base_y + 2 * ss]], [[cx + rx, base_y + 2 * ss]]])
        L.mpoly(M, pts)
    tn = L.tn(L.elegir(pal['hoja']), 1.0)
    L.masa(M, tn, relieve=.9, rug=.25)
    # pelusa: trazos cortos
    ys, xs = np.where(M > 200)
    if len(ys):
        sel = rg.integers(0, len(ys), int(len(ys) * .0035 + 100))
        cols = [tn['luz'], tn['alta'], tn['med'], tn['som']]
        for i in sel:
            x, y = xs[i], ys[i]
            a = rg.uniform(-.6, .6)
            ln = rg.uniform(3, 8) * ss
            p2 = (x + np.sin(a) * ln, y - np.cos(a) * ln)
            if M[int(np.clip(p2[1], 0, L.h - 1)), int(np.clip(p2[0], 0, L.w - 1))] > 200:
                L.linea([(x, y), p2], cols[int(rg.integers(0, 4))], max(1, ss * .9))
    # esporofitos: tallos con capsula
    if len(ys):
        top = ys.min()
        cand = np.where(ys < top + H * .25)[0]
        if len(cand):
            for _ in range(int(rg.integers(6, 16))):
                i = cand[int(rg.integers(0, len(cand)))]
                x, y = xs[i], ys[i]
                a = rg.uniform(-.5, .5)
                cc, aa = curva((x, y), a, H * rg.uniform(.07, .16), rg.uniform(-.4, .4), 6)
                L.cinta(cc, np.linspace(ss * 1.4, ss * .8, 6), L.tn(L.elegir(pal['seco'])), borde=False, nervio=False)
                L.elipse(cc[-1], (ss * 2.6, ss * 4.2), float(aa[-1]) * 57.3, L.tn(L.elegir(pal['seco']), 1.1)['med'])
    return L.final(base, h_px, mott=.15)


def liquen(seed, h_px, pal):
    L, base, H, ss = nuevo(seed, h_px, pal, 1.8, 1.2)
    rg = L.rng
    M = L.mascara()
    nb = int(rg.integers(1, 3))
    for _ in range(nb):
        cx = base[0] + rg.uniform(-.35, .35) * H
        rx, ry = H * rg.uniform(.6, 1.0), H * rg.uniform(.5, .8)
        L.mpoly(M, np.vstack([_blob(rg, cx, base[1], rx, ry, 30, .16), [[cx - rx, base[1]]]]))
    tn = L.tn(L.elegir(pal['roca']))
    r = L.masa(M, tn, relieve=.8, rug=.5, caras=1, grietas=3)
    cols = [L.tn(L.elegir(pal['hongo'])), L.tn(L.elegir(pal['seco'])), L.tn(L.elegir(pal['hoja']), 1.1)]
    dist = cv2.distanceTransform((M > 127).astype(np.uint8), cv2.DIST_L2, 3)
    ys, xs = np.where(dist > H * .05)
    if len(ys):
        for _ in range(int(rg.integers(8, 16))):
            i = int(rg.integers(0, len(ys)))
            c0 = (xs[i], ys[i])
            rad = min(dist[ys[i], xs[i]] * .95, H * rg.uniform(.05, .17))
            tc = cols[int(rg.integers(0, 3))]
            lobes = int(rg.integers(7, 13))
            th = np.linspace(0, TAU, lobes * 5 + 1)
            rr = rad * (1 + .17 * np.sin(th * lobes) + .05 * np.sin(th * 3 + rg.uniform(0, 6)))
            sq = rg.uniform(.45, .7)
            pts = np.stack([c0[0] + np.cos(th) * rr, c0[1] + np.sin(th) * rr * sq], 1)
            L.poly(pts, tc['prof'])
            L.poly(c0 + (pts - c0) * .9, tc['med'])
            L.poly(c0 + (pts - c0) * .62 - np.array([0, rad * .06]), tc['luz'])
            for _ in range(int(rad / ss * .5)):
                a = rg.uniform(0, TAU)
                rq = rad * rg.uniform(.1, .8)
                L.disco((c0[0] + np.cos(a) * rq, c0[1] + np.sin(a) * rq * sq), ss * rg.uniform(.7, 1.6), tc['som'])
    return L.final(base, h_px)


# ------------------------------------------------------------------ hongos
def prototaxites(seed, h_px, pal):
    L, base, H, ss = nuevo(seed, h_px, pal, 1.3, 1.1)
    rg = L.rng
    ns = int(rg.integers(2, 5))
    xs = np.sort(rg.uniform(-.4, .4, ns)) * H
    hs = H * rg.uniform(.45, 1.0, ns)
    hs[int(np.argmax(rg.random(ns)))] = H
    order = np.argsort(-np.abs(xs))
    for idx in order:
        x, h = xs[idx], hs[idx]
        tn = L.tn(L.elegir(pal['hongo']), rg.uniform(.92, 1.08))
        r0 = H * rg.uniform(.06, .1) * (.7 + .3 * h / H)
        n = 26
        c, ang = curva((base[0] + x, base[1]), rg.uniform(-.08, .08) + x / H * .2, h, rg.uniform(-.12, .12), n)
        s = np.linspace(0, 1, n)
        r = r0 * (1 - .12 * s + .1 * np.sin(s * 5 + rg.uniform(0, 6))) * (1 + .5 * np.exp(-s * 12))
        L.cilindro(c, r, tn, wob=.09)
        L.ramas_fibra(c, r, tn, 22, .45)
        d = np.gradient(c, axis=0)
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        nr = np.stack([-d[:, 1], d[:, 0]], 1)
        if np.dot(nr.mean(0), LUZ) > 0:
            nr = -nr
        for _ in range(int(rg.integers(3, 8))):  # anillos de crecimiento
            i = int(rg.uniform(.1, .95) * (n - 1))
            pts = [c[i] + nr[i] * r[i] * u + d[i] * r[i] * .12 * np.sin(u * 3 + _) for u in np.linspace(-1, 1, 9)]
            L.linea(pts, tn['prof'] if rg.random() < .6 else tn['som'], max(1, round(ss * 1.2)))
        # tapa superior
        top = c[-1]
        ell = (r[-1] * 1.0, r[-1] * rg.uniform(.22, .38))
        if rg.random() < .5:
            L.elipse(top, ell, 0, tn['prof'])
            L.elipse(top - np.array([0, ss * .6]), (ell[0] * .94, ell[1] * .9), 0, tn['luz'])
            L.elipse(top + np.array([ell[0] * .1, ell[1] * .15]), (ell[0] * .6, ell[1] * .5), 0, tn['med'])
        else:   # cima rota irregular
            pts = [top + np.array([u * r[-1], -(1 - abs(u)) * r[-1] * rg.uniform(.1, .5) * 1.0]) for u in np.linspace(-1, 1, 9)]
            L.poly(pts + [top + np.array([r[-1], 0]), top + np.array([-r[-1], 0])], tn['luz'])
            L.linea(pts, tn['prof'], max(1, round(ss)))
        _raiz_vis(L, (base[0] + x, base[1]), H, tn, r0, 2)
    return L.final(base, h_px)


def hongos(seed, h_px, pal):
    L, base, H, ss = nuevo(seed, h_px, pal, 1.6, 1.1)
    rg = L.rng
    n = int(rg.integers(3, 9))
    items = sorted([(rg.uniform(-.7, .7) * H, rg.uniform(.35, 1.0)) for _ in range(n)], key=lambda t: t[1])
    for x, sc in items:
        h = H * sc * rg.uniform(.7, 1.0)
        tst = L.tn(L.elegir(pal['hongo']), 1.1)
        tcap = L.tn(L.elegir(pal['hoja2'] if rg.random() < .35 else pal['hongo']), rg.uniform(.7, 1.0))
        a = rg.uniform(-.25, .25)
        stem_h = h * rg.uniform(.55, .8)
        c, ang = curva((base[0] + x, base[1] - rg.uniform(0, H * .06)), a, stem_h, rg.uniform(-.2, .2), 10)
        r = np.linspace(h * .07, h * .045, 10) * (1 + .4 * np.exp(-np.linspace(0, 1, 10) * 8))
        L.cilindro(c, r, tst, wob=.04)
        top = c[-1]
        rx = h * rg.uniform(.2, .34)
        ry = (h - stem_h) * rg.uniform(.8, 1.2)
        L.elipse(top + np.array([0, ry * .08]), (rx * .96, ry * .2), 0, tst['prof'])
        M = L.mascara()
        pts = _blob(rg, top[0], top[1] + ry * .1, rx, ry, 30, .04)
        L.mpoly(M, pts)
        L.masa(M, tcap, relieve=1.0, rug=.05)
        for _ in range(int(rg.integers(0, 6))):
            u = rg.uniform(-.7, .7)
            L.disco((top[0] + u * rx, top[1] - rg.uniform(.15, .85) * ry * np.sqrt(1 - u * u)), ss * rg.uniform(1.2, 3), mix(tcap['alta'], (255, 255, 240), .5))
    return L.final(base, h_px)


# ------------------------------------------------------------------ flora arida
def welwitschia(seed, h_px, pal):
    L, base, H, ss = nuevo(seed, h_px, pal, 3.0, 1.2)
    rg = L.rng
    tb = L.tn(L.elegir(pal['corteza']), .95)
    M = L.mascara()
    cx = base[0]
    rx, ry = H * rg.uniform(.22, .3), H * rg.uniform(.28, .4)
    # copa en forma de copa (ancha arriba)
    top_y = base[1] - ry
    pts = np.array([[cx - rx * .55, base[1]], [cx - rx * .95, top_y + ry * .25], [cx - rx * 1.0, top_y], [cx - rx * .5, top_y - ry * .1],
                    [cx + rx * .5, top_y - ry * .1], [cx + rx * 1.0, top_y], [cx + rx * .95, top_y + ry * .25], [cx + rx * .55, base[1]]])
    pts += rg.normal(0, rx * .03, pts.shape)
    L.mpoly(M, pts)
    L.masa(M, tb, relieve=.7, rug=.45, grietas=9, caras=1)
    tl = (_tono_hoja(L, .75, .0), _tono_hoja(L, .95, .0))
    seco = L.tn(L.elegir(pal['seco']), .9)
    for sd in (-1, 1):
        # cada hoja: dos tiras que arquean hacia afuera y reptan por el suelo
        for strip in range(2):
            ll = H * rg.uniform(.5, .9)
            gnd = base[1] - H * .012 * (1 + strip * 1.5)
            arc, _a = curva((cx + sd * rx * (.55 + .2 * strip), top_y - ry * .02), sd * (1.0 + .12 * strip),
                            H * rg.uniform(.45, .65), sd * rg.uniform(1.3, 1.8), 16)
            arc[:, 1] = np.minimum(arc[:, 1], gnd)
            m = 20
            s2 = np.linspace(0, 1, m)[1:]
            ph = rg.uniform(0, 6)
            gx = arc[-1][0] + sd * s2 * ll
            gy = gnd - H * .02 * np.abs(np.sin(s2 * rg.uniform(4, 9) + ph)) * s2
            pts = np.vstack([arc, np.stack([gx, np.minimum(gy, gnd)], 1)])
            nn = len(pts)
            s = np.linspace(0, 1, nn)
            w = H * (.075 * (1 - .75 * s) + .012) * (.85 + .15 * strip) * np.clip(s * 12, 0, 1) + .5
            tn = tl[strip]
            L.cinta(pts, w, tn, par=4, borde=True, nervio=False)
            # puntas deshilachadas, secas
            for q in range(int(rg.integers(3, 6))):
                a = np.arctan2(pts[-1][0] - pts[-6][0], -(pts[-1][1] - pts[-6][1])) + rg.uniform(-.8, .8)
                _hc(L, pts[-1], a, H * rg.uniform(.08, .2), H * .018, rg.uniform(-.4, .4), 'aguja', seco, 6, False)
    # conos
    for _ in range(int(rg.integers(3, 8))):
        a = rg.uniform(-.9, .9)
        cc, aa = curva((cx + rg.uniform(-.6, .6) * rx, top_y - ry * .05), a, H * rg.uniform(.1, .2), -a * .4, 8)
        L.cinta(cc, np.linspace(ss, ss * .7, 8), L.tn(L.elegir(pal['seco'])), borde=False, nervio=False)
        tc = L.tn(mix(L.elegir(pal['hoja2']), pal['dom'], .5), 1.1)
        cc2, _ = curva(cc[-1], aa[-1], H * .05, 0, 5)
        L.cinta(cc2, np.array([.2, 1, 1, .9, .1]) * H * .014, tc, borde=True, nervio=False)
    return L.final(base, h_px)


def suculenta(seed, h_px, pal, tipo=None):
    L, base, H, ss = nuevo(seed, h_px, pal, 1.2, 1.15)
    rg = L.rng
    tipo = tipo or ('candelabro' if rg.random() < .6 else 'barriles')
    tb = L.tn(mix(L.elegir(pal['hoja']), L.elegir(pal['seco']), .3), 1.0)

    def columna(p, a, h, curv, r):
        n = 20
        c, ang = curva(p, a, h, curv, n)
        rr = r * (1 - .25 * np.linspace(0, 1, n))
        rr[-3:] *= np.array([.95, .8, .5])
        L.cilindro(c, rr, tb, wob=.06)
        d = np.gradient(c, axis=0)
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        nr = np.stack([-d[:, 1], d[:, 0]], 1)
        if np.dot(nr.mean(0), LUZ) > 0:
            nr = -nr
        for u in (-.62, -.1, .4, .78):
            pts = c + nr * (rr * u)[:, None]
            L.linea(pts[1:-2], tb['prof'] if u > 0 else tb['som'], max(1, round(ss * 1.2)))
            for i in range(2, n - 3, 2):
                P = pts[i]
                L.disco(P, max(.7, ss * .9), tb['alta'] if u < 0 else tb['luz'])
        return c, ang

    if tipo == 'candelabro':
        r = H * rg.uniform(.04, .06)
        hc = H * rg.uniform(.28, .4)
        a0, cvm = rg.uniform(-.05, .05), rg.uniform(-.1, .1)
        c, ang = curva(base, a0, hc, cvm, 20)
        arms = int(rg.integers(3, 6))
        pts = []
        for k in range(arms):
            t = rg.uniform(.3, .8)
            i = int(t * (len(c) - 1))
            sd = -1 if k % 2 == 0 else 1
            aa = ang[i] + sd * rg.uniform(1.0, 1.3)
            cc, ang2 = curva(c[i], aa, H * rg.uniform(.16, .26), -sd * rg.uniform(.9, 1.2), 12)
            rr = np.linspace(r * .8, r * .7, 12)
            L.cilindro(cc, rr, tb, wob=.03)
            top, at = columna(cc[-1], 0 + rg.uniform(-.1, .1), H * rg.uniform(.3, .5), rg.uniform(-.1, .1), r * .7)
            pts.append(top)
        columna(base, a0, hc, cvm, r)
    else:
        nb = int(rg.integers(3, 8))
        for _ in range(nb):
            x = rg.uniform(-.45, .45) * H
            r = H * rg.uniform(.07, .14) * (1 - abs(x) / H * .6)
            h = r * rg.uniform(1.4, 3.0)
            columna((base[0] + x, base[1]), rg.uniform(-.1, .1), h, rg.uniform(-.1, .1), r)
    return L.final(base, h_px)


def mata_seca(seed, h_px, pal):
    L, base, H, ss = nuevo(seed, h_px, pal, 1.5, 1.15)
    rg = L.rng
    tn = L.tn(L.elegir(pal['seco']), .95)
    tn2 = L.tn(L.elegir(pal['corteza']), .9)
    tl = _tono_hoja(L, 1.0, .5)
    cols = (tn, tn2)
    hojas = []

    def ram(p, a, largo, w, prof):
        cc, aa = curva(p, a, largo, rg.uniform(-.4, .4), 6, wig=rg.uniform(0, .25), fase=rg.uniform(0, 6))
        ww = np.linspace(w, w * .65, 6)
        L.cinta(cc, ww, cols[prof % 2], borde=prof < 2, nervio=False)
        if prof == 0 or largo < H * .03:
            hojas.append((cc[-1], aa[-1], largo))
            return
        k = int(rg.integers(2, 4))
        for _ in range(k):
            ram(cc[-1] if rg.random() < .6 else cc[int(rg.integers(2, 5))], aa[-1] + rg.uniform(-.9, .9),
                largo * rg.uniform(.55, .78), w * .68, prof - 1)

    for _ in range(int(rg.integers(4, 7))):
        a = rg.uniform(-1.1, 1.1)
        ram((base[0] + rg.uniform(-.03, .03) * H, base[1]), a, H * rg.uniform(.22, .34), H * .008, 4)
    for p, a, lg in hojas:
        if rg.random() < .8:
            for _ in range(int(rg.integers(1, 4))):
                _hc(L, p, a + rg.uniform(-.9, .9), H * rg.uniform(.02, .05), H * .01, rg.uniform(-.4, .4), 'lanza',
                    tl if rg.random() < .5 else tn, 5, False)
    return L.final(base, h_px)


def cicada(seed, h_px, pal):
    L, base, H, ss = nuevo(seed, h_px, pal, 1.9, 1.15)
    rg = L.rng
    tb = L.tn(L.elegir(pal['corteza']), .95)
    th = H * rg.uniform(.22, .34)
    r0 = H * rg.uniform(.06, .085)
    n = 14
    c, ang = curva(base, rg.uniform(-.1, .1), th, rg.uniform(-.2, .2), n)
    s = np.linspace(0, 1, n)
    r = r0 * (1 - .15 * s) * (1 + .15 * np.sin(s * 6))
    L.cilindro(c, r, tb, wob=.05)
    escamas(L, c, r, tb, ncol=8, alto=.75)
    top, a_top = c[-1], ang[-1]
    nf = int(rg.integers(13, 22))
    angs = np.linspace(-1.6, 1.6, nf) + rg.uniform(-.1, .1, nf)
    for da in sorted(angs, key=lambda x: -abs(x)):
        up = 1 - abs(da) / 1.7
        tn = _tono_hoja(L, .8 + .25 * up, .1)
        tn2 = _tono_hoja(L, 1.0 + .1 * up, .1)
        lg = H * rg.uniform(.55, .85) * (.6 + .4 * (1 - .4 * up))
        fronda(L, top, a_top + da, lg, _caida(da, rg.uniform(.7, 1.3)), tn, pares=int(rg.integers(22, 30)),
               rel=.2, ratio=.12, ap=.98, caida=.1, forma='lanza', tn2=tn2, rach=1.3)
    return L.final(base, h_px)


# ------------------------------------------------------------------ troncos y rocas
def tronco_caido(seed, h_px, pal, musgo_sobre=True):
    ss = 2.0 if h_px <= 450 else (1.5 if h_px <= 750 else 1.0)
    rg = np.random.default_rng(seed)
    H = h_px * ss
    largo = H * rg.uniform(1.7, 2.7)
    L = Lienzo(largo * 1.15, H * 1.5, pal, seed, ss)
    L.H = H
    rg = L.rng
    base = (L.w / 2, L.h - 3 * ss)
    tb = L.tn(L.elegir(pal['corteza']), .95)
    r0 = H * .42
    n = 36
    x0 = (L.w - largo) / 2
    xx = np.linspace(x0, x0 + largo, n)
    yb = base[1] - r0 * .85
    yy = yb - np.sin(np.linspace(0, np.pi, n)) * H * .05 + np.linspace(0, 1, n) * rg.uniform(-.1, .1) * H
    c = np.stack([xx, yy], 1)
    r = r0 * np.linspace(1.0, rg.uniform(.7, .9), n) * (1 + .04 * np.sin(np.linspace(0, 30, n)))
    # ramas rotas
    for _ in range(int(rg.integers(1, 4))):
        i = int(rg.integers(5, n - 4))
        cc, aa = curva(c[i] - np.array([0, r[i] * .6]), rg.uniform(-.7, .7), H * rg.uniform(.15, .4), rg.uniform(-.3, .3), 7)
        L.cilindro(cc, np.linspace(r[i] * .3, r[i] * .12, 7), tb, wob=0)
    L.cilindro(c, r, tb, wob=.08)
    L.ramas_fibra(c, r, tb, 90, .3)
    d = np.gradient(c, axis=0)
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    nr = np.stack([-d[:, 1], d[:, 0]], 1)
    if np.dot(nr.mean(0), LUZ) > 0:
        nr = -nr
    # grietas transversales
    for _ in range(int(rg.integers(6, 12))):
        i = int(rg.integers(2, n - 2))
        pts = [c[i] + nr[i] * r[i] * u + d[i] * r[i] * .08 * np.sin(u * 5 + i) for u in np.linspace(-1, 1, 8)]
        L.linea(pts, tb['prof'], max(1, round(ss * 1.4)))
    # extremo roto con anillos
    ex = c[0]
    tc = L.tn(L.elegir(pal['seco']), 1.15)
    ang = 0
    L.elipse(ex, (r[0] * .33, r[0] * 1.0), 0, tb['prof'])
    for k, f in enumerate((1.0, .86, .6, .35, .12)):
        col = [tc['som'], tc['med'], tc['luz'], tc['med'], tc['som']][k]
        L.elipse(ex + np.array([r[0] * .02 * k, 0]), (r[0] * .30 * f, r[0] * .93 * f), 0, col)
    # musgo y repisas fungicas
    if musgo_sobre:
        M = L.mascara()
        tm = L.tn(L.elegir(pal['hoja']), .95)
        for _ in range(int(rg.integers(3, 7))):
            i = int(rg.integers(4, n - 3))
            top = c[i] - np.array([0, r[i] * .95])
            rx = r0 * rg.uniform(.5, 1.6)
            ry = r0 * rg.uniform(.2, .45)
            L.mpoly(M, np.vstack([_blob(rg, top[0], top[1] + ry * .5, rx, ry, 26, .15)]))
        L.masa(M, tm, relieve=.9, rug=.3)
    for _ in range(int(rg.integers(0, 3))):
        i = int(rg.integers(6, n - 4))
        P = c[i] + nr[i] * r[i] * rg.uniform(-.2, .9)
        tf = L.tn(L.elegir(pal['hongo']))
        rx = r0 * rg.uniform(.15, .3)
        M = L.mascara()
        L.mpoly(M, _blob(rg, P[0], P[1], rx, rx * .5, 18, .05))
        L.masa(M, tf, relieve=.7, rug=.05)
    return L.final(base, h_px)


def roca_musgosa(seed, h_px, pal, musgo=True):
    L, base, H, ss = nuevo(seed, h_px, pal, 1.9, 1.2)
    rg = L.rng
    M = L.mascara()
    nb = int(rg.integers(1, 4))
    for _ in range(nb):
        cx = base[0] + rg.uniform(-.5, .5) * H
        rx = H * rg.uniform(.4, .8)
        ry = H * rg.uniform(.45, 1.0)
        pts = _blob(rg, cx, base[1] + H * .02, rx, ry, 28, .08)
        # facetado: reducir vertices
        pts = pts[::2] if rg.random() < .3 else pts
        L.mpoly(M, np.vstack([pts, [[cx - rx, base[1] + 2 * ss]], [[cx + rx, base[1] + 2 * ss]]]))
    tn = L.tn(L.elegir(pal['roca']), rg.uniform(.9, 1.05))
    tm = L.tn(L.elegir(pal['hoja']), .95) if musgo else None
    L.masa(M, tn, relieve=.85, rug=.5, esc_rug=H * .25, caras=1, grietas=int(rg.integers(2, 6)), musgo=tm)
    return L.final(base, h_px)


def piedra(seed, h_px, pal):
    return roca_musgosa(seed, h_px, pal, musgo=False)


# ------------------------------------------------------------------ registro
ESPECIES = {
    'lepidodendron': lepidodendron, 'sigillaria': sigillaria, 'calamites': calamites,
    'equisetum': equisetum, 'glossopteris': glossopteris, 'dicroidium': dicroidium,
    'psaronius': psaronius, 'cyathea': cyathea, 'cordaites': cordaites,
    'helecho_suelo': helecho_suelo, 'musgo': musgo, 'liquen': liquen,
    'prototaxites': prototaxites, 'hongos': hongos, 'welwitschia': welwitschia,
    'suculenta': suculenta, 'mata_seca': mata_seca, 'cicada': cicada,
    'tronco_caido': tronco_caido, 'roca_musgosa': roca_musgosa, 'piedra': piedra,
}


def generar(nombre, seed, h_px, pal, **kw):
    return ESPECIES[nombre](seed, h_px, pal, **kw)
