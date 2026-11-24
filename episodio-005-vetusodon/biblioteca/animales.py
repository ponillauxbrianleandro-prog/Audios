"""Animales 2D pintados con volumen (sprites PNG RGBA) para «Vetusodon elikhulu».

Tecnica: cada animal es un rig 3D minimo de elipsoides (torso, patas con IK, cabeza, cola, mechones)
proyectado en vista 3/4 con perspectiva debil y camara elevada; se «pinta» con z-buffer, luz fija
arriba-izquierda, 5 tonos suaves (2 de sombra), oclusion ambiental por profundidad, contorno calido
fino, pelaje/pliegues por trazos cortos orientados con la luz, y grano. Todo es determinista (seed).

API:
  generar(especie, accion, fase, vista, pal, seed=0, h_px=400) -> PIL RGBA (pies en el borde inferior)
  ciclo(especie, accion, vista, pal, n=12, seed=0, h_px=400)   -> [n PIL RGBA] alineados (cache en disco)
  sombra_contacto(especie, vista, pal, h_px=400, accion='idle') -> PIL RGBA (elipse en el plano del suelo)
  avance_px(especie, accion, vista, h_px=400) -> (dx, dy) px que avanza el animal por ciclo
  img.info['ancla'] = (x, y) del punto del suelo bajo el centro del cuerpo dentro del sprite.
"""
import os
import sys
import math
import zlib
import json
import hashlib
import numpy as np
import cv2
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paletas
from pintura import mix, esc, tonos, ruido

AQUI = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(AQUI, 'cache')
VERSION = 'v7'

VISTAS = ('3q_izq', '3q_der', '3q_frente_izq', '3q_frente_der', '3q_trasera_izq', '3q_trasera_der')
# angulo (grados) entre el rumbo y el eje horizontal de pantalla; sz>0: la cabeza viene hacia la camara
_AZ = {'3q': (33, 1), 'frente': (62, 1), 'trasera': (52, -1)}
PITCH_CAM = math.radians(15)

LUZ3 = np.array([-0.50, -0.72, 0.60])
LUZ3 = LUZ3 / np.linalg.norm(LUZ3)
HALF = LUZ3 + np.array([0, 0, 1.0])
HALF = HALF / np.linalg.norm(HALF)


# ----------------------------------------------------------------------------- matematica
def _ry(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, -s], [0, 1, 0], [s, 0, c]])


def _rp(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def _rr(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, s], [0, -s, c]])


def rot(yaw=0.0, pitch=0.0, roll=0.0):
    return _ry(yaw) @ _rp(pitch) @ _rr(roll)


def unit(v):
    v = np.asarray(v, float)
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-9)


def smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


class TF:
    """transformacion rigida p' = R p + t en el marco del rumbo (a adelante, b arriba, c derecha)"""
    def __init__(s, R=None, t=None):
        s.R = np.eye(3) if R is None else R
        s.t = np.zeros(3) if t is None else np.asarray(t, float)

    def __call__(s, p):
        return np.asarray(p, float) @ s.R.T + s.t

    def then(s, o):          # primero s, luego o
        return TF(o.R @ s.R, o.R @ s.t + o.t)

    @staticmethod
    def pivote(R, piv, d=(0, 0, 0)):
        piv = np.asarray(piv, float)
        return TF(R, piv - R @ piv + np.asarray(d, float))


def eje_marco(v, arriba=(0, 1, 0)):
    """matriz con primera columna = v, el resto ortonormal (arriba aprox)"""
    a = unit(v)
    u = np.asarray(arriba, float)
    if abs(a @ u) > .95:
        u = np.array([1.0, 0, 0])
    c = unit(np.cross(a, u))
    b = np.cross(c, a)
    return np.stack([a, b, c], 1)


def _hash(*a):
    return zlib.crc32('|'.join(str(x) for x in a).encode()) & 0xffffffff


def _ruido3(q, ph, fr):
    """ruido suave 3D barato (suma de senos) y su gradiente respecto a q"""
    rg = np.random.default_rng(ph)
    ks = rg.normal(0, 1, (5, 3))
    ks = ks / np.linalg.norm(ks, axis=1, keepdims=True) * fr * rg.uniform(.8, 1.4, (5, 1))
    ps = rg.uniform(0, 6.28, 5)
    arg = q @ ks.T + ps
    v = np.sin(arg).sum(1) / 5.0
    g = (np.cos(arg) @ ks) / 5.0
    return v, g


# ----------------------------------------------------------------------------- rampa de tonos
def tinta(c, pal, k=.15):
    return mix(c, pal['dom'], k)


def rampa(base, pal, k=.15, contraste=1.0):
    tn = tonos(tinta(base, pal, k), pal)
    return np.array([tn['prof'], tn['som'], tn['med'], tn['luz'], tn['alta']], np.float32)


def banda(lam):
    t = np.clip((lam + .25) / 1.15, 0, 1) * 4
    f = np.floor(t)
    s = smooth((t - f - .30) / .40)
    return np.minimum(f + s, 4.0)


def color_rampa(R5, t):
    i = np.clip(np.floor(t).astype(int), 0, 3)
    fr = (t - i)[..., None]
    return R5[i] * (1 - fr) + R5[i + 1] * fr


# ----------------------------------------------------------------------------- escena
class Escena:
    def __init__(s, vista, mats, seed, k, D):
        key, lado = vista[3:].rsplit('_', 1) if vista.count('_') >= 2 else ('3q', vista.split('_')[-1])
        if vista.startswith('3q_frente'):
            key = 'frente'
        elif vista.startswith('3q_trasera'):
            key = 'trasera'
        else:
            key = '3q'
        ang, sz = _AZ[key]
        ang = math.radians(ang)
        hx = math.cos(ang) * (-1 if vista.endswith('izq') else 1)
        hz = math.sin(ang) * sz
        s.h = np.array([hx, hz])
        Mw = np.array([[hx, 0, -hz], [0, 1, 0], [hz, 0, hx]])
        cp, sp = math.cos(PITCH_CAM), math.sin(PITCH_CAM)
        s.proj = np.array([[1, 0, 0], [0, -cp, sp], [0, sp, cp]]) @ Mw
        s.mats = mats
        s.seed = seed
        s.k = k
        s.D = D
        s.prims = []
        s.garras = []
        s.polvo = []
        s.alas = []

    # --- construccion
    def add(s, nombre, c, R, r, mat, mat2=None, tex=None, fur=None, spec=0.0, bump=0.0, bumpf=2.5,
            pliegues=0, bias=0.0, rim=1.0):
        s.prims.append(dict(nombre=nombre, c=np.asarray(c, float), R=np.asarray(R, float), r=np.asarray(r, float),
                            mat=mat, mat2=mat2, tex=tex, fur=fur, spec=spec, bump=bump, bumpf=bumpf,
                            pliegues=pliegues, bias=bias, rim=rim))

    def garra(s, pts, w0, mat='garra', w1=0.25):
        s.garras.append(dict(pts=np.asarray(pts, float), w0=w0, w1=w1, mat=mat))

    # --- proyeccion
    def pc(s, p):
        p = np.asarray(p, float)
        q = p @ s.proj.T
        sc = s.D / (s.D - q[..., 2])
        return q, sc

    def extents(s):
        """limites (xmin,xmax,ymin,ymax) en px relativos al origen para todas las prims"""
        xs0, xs1, ys0, ys1 = [], [], [], []
        for p in s.prims:
            q, sc = s.pc(p['c'])
            Rc = s.proj @ p['R']
            rr = p['r'] * s.k * sc
            ex = math.sqrt(((Rc[0] * rr) ** 2).sum())
            ey = math.sqrt(((Rc[1] * rr) ** 2).sum())
            fl = (p['fur']['L'] * s.k * sc * 1.6) if p['fur'] else 0
            cx, cy = q[0] * s.k * sc, q[1] * s.k * sc
            xs0.append(cx - ex - fl); xs1.append(cx + ex + fl)
            ys0.append(cy - ey - fl); ys1.append(cy + ey + fl)
        for g in s.garras:
            q, sc = s.pc(g['pts'])
            xs0.append((q[:, 0] * s.k * sc).min() - 3); xs1.append((q[:, 0] * s.k * sc).max() + 3)
            ys0.append((q[:, 1] * s.k * sc).min() - 3); ys1.append((q[:, 1] * s.k * sc).max() + 3)
        for al in s.alas:
            q, sc = s.pc(al['pts'])
            xs0.append((q[:, 0] * s.k * sc).min() - 3); xs1.append((q[:, 0] * s.k * sc).max() + 3)
            ys0.append((q[:, 1] * s.k * sc).min() - 3); ys1.append((q[:, 1] * s.k * sc).max() + 3)
        for pv in s.polvo:
            q, sc = s.pc(pv[0])
            xs0.append(q[0] * s.k * sc - 8); xs1.append(q[0] * s.k * sc + 8)
            ys0.append(q[1] * s.k * sc - 8); ys1.append(q[1] * s.k * sc + 8)
        return min(xs0), max(xs1), min(ys0), max(ys1)


# ----------------------------------------------------------------------------- texturas por pixel
def _tex(kind, par, q, nh):
    if kind is None:
        return None
    if kind == 'vientre':
        return smooth((par.get('u', .05) - nh[:, 1]) / par.get('w', .5))
    if kind == 'dorso':
        return smooth((nh[:, 1] - par.get('u', .1)) / par.get('w', .6))
    if kind == 'cara':          # hocico mas claro hacia delante y abajo
        return smooth((q[:, 0] * .8 - nh[:, 1] * .5 - par.get('u', .1)) / .5)
    if kind == 'moteado':
        v, _ = _ruido3(q * par.get('f', 2.0), par.get('s', 1), 2.6)
        return smooth((v - par.get('u', .15)) / .25)
    if kind == 'franja':        # bandas a lo largo del eje local 0
        return smooth((np.sin(q[:, 0] * par.get('n', 3) * math.pi + par.get('ph', 0)) - .1) / .3)
    if kind == 'lado':          # color distinto en la mitad c>0
        return smooth(q[:, 2] / .4)
    return None


# ----------------------------------------------------------------------------- render
def render(S, W, H, ox, oy, bs=.5):
    """pinta la escena. La base (volumen) se calcula a resolucion bs*lienzo y se amplia."""
    k = S.k
    Wb, Hb = max(8, int(W * bs)), max(8, int(H * bs))
    zb = np.full((Hb, Wb), -1e9, np.float32)
    col = np.zeros((Hb, Wb, 3), np.float32)
    alf = np.zeros((Hb, Wb), np.float32)
    for pi, p in enumerate(S.prims):
        q, sc = S.pc(p['c'])
        C = np.array([ox + q[0] * k * sc, oy + q[1] * k * sc, q[2] * k])
        Rc = S.proj @ p['R']
        rr_full = p['r'] * k * sc
        p['geo'] = (C, Rc, rr_full, sc)
        rr = rr_full * bs
        Cb = np.array([C[0] * bs, C[1] * bs])
        ex = math.sqrt(((Rc[0] * rr) ** 2).sum()) + 1.5
        ey = math.sqrt(((Rc[1] * rr) ** 2).sum()) + 1.5
        x0, x1 = max(0, int(Cb[0] - ex)), min(Wb, int(Cb[0] + ex) + 1)
        y0, y1 = max(0, int(Cb[1] - ey)), min(Hb, int(Cb[1] + ey) + 1)
        if x1 <= x0 or y1 <= y0:
            continue
        A = (Rc.T / rr[:, None]).astype(np.float32)
        xs = np.arange(x0, x1, dtype=np.float32) + .5 - np.float32(Cb[0])
        ys = np.arange(y0, y1, dtype=np.float32) + .5 - np.float32(Cb[1])
        a2 = A[:, 2]
        a = float(a2 @ a2)
        c0, c1_, c01 = float(A[:, 0] @ A[:, 0]), float(A[:, 1] @ A[:, 1]), float(A[:, 0] @ A[:, 1])
        b0, b1 = float(A[:, 0] @ a2), float(A[:, 1] @ a2)
        X = xs[None, :]
        Y = ys[:, None]
        b = X * b0 + Y * b1
        cc = X * X * c0 + (2 * c01) * X * Y + Y * Y * c1_ - 1
        disc = b * b - a * cc
        m = disc > 0
        if not m.any():
            continue
        dz = (-b + np.sqrt(np.maximum(disc, 0))) / a
        z = (np.float32(C[2] + p['bias'] * k) + dz / bs).astype(np.float32)
        zsub = zb[y0:y1, x0:x1]
        upd = m & (z > zsub)
        if not upd.any():
            continue
        iy, ix = np.nonzero(upd)
        zz = dz[iy, ix]
        qv = xs[ix][:, None] * A[:, 0] + ys[iy][:, None] * A[:, 1] + zz[:, None] * a2
        n = (qv / rr.astype(np.float32)) @ Rc.T.astype(np.float32)
        n = unit(n)
        mat = S.mats[p['mat']]
        if p['bump']:
            v, g = _ruido3(qv * p['bumpf'] * 1.0, _hash(S.seed, p['nombre']), 2.2)
            n = unit(n + p['bump'] * (g @ Rc.T))
        lam = (n @ LUZ3) * .90 - .02
        nh = n @ S.proj
        lam = lam + .10 * np.clip(-nh[:, 1], 0, 1)
        if p['rim']:
            lam = lam - .55 * p['rim'] * smooth((.22 - n[:, 2]) / .22)
        t = banda(lam)
        c1 = color_rampa(mat, t)
        w2 = _tex(p['tex'][0], p['tex'][1], qv, nh) if p['tex'] else None
        if w2 is not None and p['mat2']:
            c2 = color_rampa(S.mats[p['mat2']], t)
            c1 = c1 * (1 - w2[:, None]) + c2 * w2[:, None]
        if p['bump']:
            v, _ = _ruido3(qv * p['bumpf'] * 1.7, _hash(S.seed, p['nombre'], 'c'), 2.0)
            c1 = c1 * (1 + .11 * v[:, None])
        if p['spec']:
            sp = np.clip(n @ HALF, 0, 1) ** 28
            c1 = c1 + (255 - c1) * (sp * p['spec'])[:, None]
        col[y0:y1, x0:x1][iy, ix] = c1
        alf[y0:y1, x0:x1][iy, ix] = 1.0
        zsub[iy, ix] = z[iy, ix]
    # ampliar a resolucion completa
    mk = alf > .5
    zmin = zb[mk].min() if mk.any() else 0
    zf = np.where(mk, zb, zmin)
    pmc = col * alf[..., None]
    A_full = cv2.resize(alf, (W, H), interpolation=cv2.INTER_LINEAR)
    pmc = cv2.resize(pmc, (W, H), interpolation=cv2.INTER_LINEAR)
    col_f = pmc / np.maximum(A_full[..., None], 1e-3)
    zfull = cv2.resize(zf, (W, H), interpolation=cv2.INTER_LINEAR)
    zfull = np.where(A_full > .5, zfull, -1e9).astype(np.float32)
    return col_f.astype(np.float32), A_full.astype(np.float32), zfull, None


_TAB = {}


def _tabla(R5):
    key = R5.tobytes()
    if key not in _TAB:
        _TAB[key] = color_rampa(R5, np.arange(0, 4.01, .5))
    return _TAB[key]


def _maxfilt(a, k):
    return cv2.dilate(a, np.ones((k, k), np.uint8))


def ao_y_contornos(S, col, alf, zb, pal, ssf):
    """oclusion ambiental por profundidad + contorno entre piezas. modifica col"""
    k = S.k
    m = alf > .5
    if not m.any():
        return col
    zmin = zb[m].min()
    zz = np.where(m, zb, zmin).astype(np.float32)
    m = m & (alf > .5)
    Hh, Ww = zz.shape
    sm = cv2.resize(zz, (Ww // 4, Hh // 4), interpolation=cv2.INTER_AREA)
    bl = cv2.resize(cv2.GaussianBlur(sm, (0, 0), max(1.0, k * .8)), (Ww, Hh), interpolation=cv2.INTER_LINEAR)
    ao = np.clip((bl - zz - k * 1.3) / (k * 7.0), 0, 1) * m
    ao = cv2.resize(cv2.GaussianBlur(cv2.resize(ao.astype(np.float32), (Ww // 2, Hh // 2)), (0, 0), max(1.0, k * .25)), (Ww, Hh))
    sb = np.array(pal['sombra'], np.float32)
    f = (ao * .50)[..., None]
    col = col * (1 - f) + (col * .45 + sb * .25) * f
    # contorno entre piezas (el lado lejano de un salto de profundidad)
    kk = max(3, int(round(k * .8)) | 1)
    mx = _maxfilt(zz, kk)
    jump = (mx - zz) > (k * 1.6)
    jump = jump & m
    edge = cv2.GaussianBlur(jump.astype(np.float32), (0, 0), .7) * .78
    cont = np.array(pal['contorno'], np.float32)
    col = col * (1 - edge[..., None]) + (cont * .9 + col * .1) * edge[..., None]
    return col, ao


def trazos(S, p, col_pm, al_pm, zb, ao, ox, oy):
    """pelaje o pliegues de una pieza; pinta sobre canvas premultiplicado (col_pm, al_pm)"""
    f = p['fur']
    if f is None or 'geo' not in p:
        return
    H, W = al_pm.shape
    C, Rc, rr, sc = p['geo']
    k = S.k
    rg = np.random.default_rng(_hash(S.seed, p['nombre'], 'fur'))
    Lpx = f['L'] * k * sc
    wpx = max(1.0, f.get('w', .7) * .26 * k * sc)
    area = 4 * math.pi * (((rr[0] * rr[1]) ** 1.6 + (rr[0] * rr[2]) ** 1.6 + (rr[1] * rr[2]) ** 1.6) / 3) ** (1 / 1.6)
    Ntot = int(min(30000, f.get('dens', 1.0) * area / (Lpx * wpx) * .95))
    if Ntot < 12:
        return
    U = rg.normal(0, 1, (Ntot, 3))
    U = unit(U)
    Jt = rg.normal(0, 1, (Ntot, 3))
    r1, r2, r3 = rg.random((3, Ntot))
    n = unit((U / rr) @ Rc.T)
    pos = C + (U * rr) @ Rc.T
    vis = n[:, 2] > -.10
    ix = pos[:, 0].astype(int)
    iy = pos[:, 1].astype(int)
    ok = vis & (ix >= 0) & (ix < W) & (iy >= 0) & (iy < H)
    ixc, iyc = np.clip(ix, 0, W - 1), np.clip(iy, 0, H - 1)
    tol = k * (f.get('tol', 1.4))
    ok &= pos[:, 2] >= zb[iyc, ixc] - tol
    if not ok.any():
        return
    sel = np.nonzero(ok)[0]
    U, n, pos, r1, r2, r3, Jt = U[sel], n[sel], pos[sel], r1[sel], r2[sel], r3[sel], Jt[sel]
    ixc, iyc = ixc[sel], iyc[sel]
    Rn = S.proj @ p['R']
    comb = unit(np.asarray(f.get('comb', (-1, -.3, 0)), float))
    dc = Rn @ comb
    if f.get('radial'):
        dc = unit(n * 0 + (U @ Rn.T) * 1.0)      # hacia fuera del centro (cabeza, mejillas)
        dc = unit(dc + Rn @ comb * f['radial'])
    tcomb = dc - (dc * n).sum(1, keepdims=True) * n if dc.ndim == 2 else dc[None] - ((dc[None] * n).sum(1, keepdims=True)) * n
    ln = np.linalg.norm(tcomb, axis=1, keepdims=True)
    tj = Jt - (Jt * n).sum(1, keepdims=True) * n
    tcomb = np.where(ln > .15, tcomb / np.maximum(ln, 1e-6), unit(tj))
    tcomb = unit(tcomb + .30 * f.get('jit', 1.0) * unit(tj) * (r1[:, None] - .5) * 2)
    out = f.get('out', .25)
    d3 = unit(tcomb * (1 - out) + n * out + .12 * tj)
    lf = (.55 + .9 * r2) * (1 + (f.get('borde', 1.3) - 1) * smooth((.35 - n[:, 2]) / .35))
    end = pos[:, :2] + d3[:, :2] * (Lpx * lf)[:, None]
    # material
    mat = S.mats[p['mat']]
    nh = n @ S.proj
    lam = (n @ LUZ3) * .90 - .02 + .10 * np.clip(-nh[:, 1], 0, 1)
    lam = lam + (r3 - .5) * f.get('var', .40) - ao[iyc, ixc] * 1.5 + f.get('lamb', 0.0)
    t = banda(lam - .05)
    w2 = _tex(p['tex'][0], p['tex'][1], U, nh) if p['tex'] else None
    # capa local (bbox)
    xa = int(max(0, min(pos[:, 0].min(), end[:, 0].min()) - 6))
    xb = int(min(W, max(pos[:, 0].max(), end[:, 0].max()) + 7))
    ya = int(max(0, min(pos[:, 1].min(), end[:, 1].min()) - 6))
    yb = int(min(H, max(pos[:, 1].max(), end[:, 1].max()) + 7))
    if xb <= xa or yb <= ya:
        return
    lay = np.zeros((yb - ya, xb - xa, 4), np.uint8)
    off = np.array([xa, ya], np.float32)
    P0 = (pos[:, :2] - off)
    P1 = (end - off)

    def pintar(sel_idx, tt, grosor, t_off=0.0, frac0=0.0, w2s=None, escala_t=1.0):
        if len(sel_idx) == 0:
            return
        tq = np.clip(np.round((tt[sel_idx] * escala_t + t_off) * 2) / 2, 0, 4)
        flag = (w2s[sel_idx] > .5) if w2s is not None else np.zeros(len(sel_idx), bool)
        a0 = P0[sel_idx] * (1 - frac0) + P1[sel_idx] * frac0
        a1 = P1[sel_idx]
        dd = a1 - a0
        perp = np.stack([-dd[:, 1], dd[:, 0]], 1)
        mid = (a0 + a1) / 2 + perp * curl[sel_idx][:, None]
        seg = np.round(np.stack([a0, mid, a1], 1) * 16).astype(np.int32)
        for fl in ((False, True) if w2s is not None else (False,)):
            for tv in np.unique(tq):
                mm = (tq == tv) & (flag == fl)
                if not mm.any():
                    continue
                cmat = S.mats[p['mat2']] if (fl and p['mat2']) else mat
                cc = _tabla(cmat)[int(round(tv * 2))]
                cv2.polylines(lay, list(seg[mm].reshape(-1, 3, 1, 2).astype(np.int32)), False,
                              (float(cc[0]), float(cc[1]), float(cc[2]), 255.0), int(grosor), cv2.LINE_AA, 4)

    curl = (r1 - .5) * f.get('curl', .55)
    if f.get('pliegue'):
        # pliegues: linea oscura + linea clara contigua del lado de la luz
        sh = np.argsort(t)
        pintar(sh, t, max(1, int(round(wpx * .8))), t_off=-1.3, w2s=w2)
        pintar(sh[len(sh) // 3:], t, max(1, int(round(wpx * .5))), t_off=+.7, frac0=.0, w2s=w2)
    else:
        order = np.argsort(t)
        sub = order[: int(len(order) * .55)]
        pintar(sub, t, int(max(1, round(wpx * 1.45))), t_off=-.85, w2s=w2)          # bajo-pelo oscuro
        pintar(order, t, int(max(1, round(wpx))), t_off=0.0, w2s=w2)               # cuerpo del pelo
        hi = order[int(len(order) * .35):]
        pintar(hi[r1[hi] > .35], t, int(max(1, round(wpx * .75))), t_off=+.6, frac0=.5, w2s=w2)   # puntas claras
    a = lay[..., 3:4].astype(np.float32) / 255.0
    pm = lay[..., :3].astype(np.float32)
    # cv2 en RGBA: los canales ya estan premultiplicados por la cobertura (bg 0)
    reg = col_pm[ya:yb, xa:xb]
    reg[:] = pm + reg * (1 - a)
    ra = al_pm[ya:yb, xa:xb]
    ra[:] = a[..., 0] + ra * (1 - a[..., 0])


def pintar_alas(S, col_pm, al_pm, ox, oy):
    if not S.alas:
        return
    H, W = al_pm.shape
    k = S.k
    pal = S.pal
    lay = np.zeros((H, W, 4), np.uint8)
    items = []
    for a in S.alas:
        q, sc = S.pc(a['pts'])
        items.append((q[:, 2].mean(), a))
    items.sort(key=lambda t: t[0])
    memb = S.mats['ala'][3]
    vein = S.mats['ala'][0]
    for z, a in items:
        q, sc = S.pc(a['pts'])
        P = np.stack([ox + q[:, 0] * k * sc, oy + q[:, 1] * k * sc], 1)
        al = a['alpha']
        cm = tuple(float(v) * al for v in memb) + (255.0 * al,)
        cv2.fillPoly(lay, [np.round(P * 16).astype(np.int32)], cm, cv2.LINE_AA, 4)
        for vl in a['venas']:
            q2, s2 = S.pc(vl)
            PV = np.stack([ox + q2[:, 0] * k * s2, oy + q2[:, 1] * k * s2], 1)
            cv2.polylines(lay, [np.round(PV * 16).astype(np.int32)], False, tuple(float(v) * .8 for v in vein) + (204.0,), 1, cv2.LINE_AA, 4)
        cv2.polylines(lay, [np.round(P * 16).astype(np.int32)], True, tuple(float(v) * .8 for v in vein) + (204.0,), 1, cv2.LINE_AA, 4)
        if a.get('stigma') is not None:
            q3, s3 = S.pc(a['stigma'])
            PS = np.stack([ox + q3[:, 0] * k * s3, oy + q3[:, 1] * k * s3], 1)
            cv2.fillPoly(lay, [np.round(PS * 16).astype(np.int32)], tuple(float(v) for v in S.mats['oscuro'][2]) + (255.0,), cv2.LINE_AA, 4)
    a_ = lay[..., 3:4].astype(np.float32) / 255.0
    col_pm[:] = lay[..., :3].astype(np.float32) + col_pm * (1 - a_)
    al_pm[:] = a_[..., 0] + al_pm * (1 - a_[..., 0])


def pintar_garras(S, col_pm, al_pm, zb, ox, oy):
    H, W = al_pm.shape
    k = S.k
    lay = np.zeros((H, W, 4), np.uint8)
    items = []
    for g in S.garras:
        q, sc = S.pc(g['pts'])
        P = np.stack([ox + q[:, 0] * k * sc, oy + q[:, 1] * k * sc], 1)
        z = q[:, 2] * k
        items.append((z[0], g, P, z, sc))
    items.sort(key=lambda t: t[0])
    for z0, g, P, z, sc in items:
        mat = S.mats[g['mat']]
        ix, iy = int(P[0, 0]), int(P[0, 1])
        if not (0 <= ix < W and 0 <= iy < H):
            continue
        # raiz visible?
        if z[1] < zb[iy, ix] - k * 3.0:
            continue
        d = np.gradient(P, axis=0)
        d = d / (np.linalg.norm(d, axis=1, keepdims=True) + 1e-6)
        nr = np.stack([-d[:, 1], d[:, 0]], 1)
        t = np.linspace(0, 1, len(P))
        w = (g['w0'] * (1 - t) + g['w1'] * t) * k * sc * .5
        A = P + nr * w[:, None]
        B = P - nr * w[:, None]
        lado = float((nr.mean(0)) @ LUZ3[:2])
        li, sh = (A, B) if lado > 0 else (B, A)
        poly = np.vstack([A, B[::-1]])
        cv2.fillPoly(lay, [np.round(poly * 16).astype(np.int32)], tuple(float(v) for v in mat[2]) + (255.0,), cv2.LINE_AA, 4)
        lit = np.vstack([li, P[::-1]])
        cv2.fillPoly(lay, [np.round(lit * 16).astype(np.int32)], tuple(float(v) for v in mat[4]) + (255.0,), cv2.LINE_AA, 4)
        cv2.polylines(lay, [np.round(np.vstack([li[:-1] * .85 + P[:-1] * .15]) * 16).astype(np.int32)], False,
                      tuple(float(v) for v in mat[4]) + (255.0,), 1, cv2.LINE_AA, 4)
        cv2.polylines(lay, [np.round(poly * 16).astype(np.int32)], True,
                      tuple(float(v) for v in mat[0]) + (255.0,), 1, cv2.LINE_AA, 4)
    a = lay[..., 3:4].astype(np.float32) / 255.0
    col_pm[:] = lay[..., :3].astype(np.float32) + col_pm * (1 - a)
    al_pm[:] = a[..., 0] + al_pm * (1 - a[..., 0])


# ============================================================================================ ESPECIES
def _C(r, g, b):
    return (float(r), float(g), float(b))


def _pelo(L, w=.7, dens=1.0, comb=(-1, -.25, 0), out=.45, **kw):
    d = dict(L=L, w=w, dens=dens, comb=comb, out=out)
    d.update(kw)
    return d


ESP = {}

ESP['vetusodon'] = dict(
    L=72.0, H=42.0, real_cm=95, piel='pelo',
    y0=21.5, pivF=(10, 21.5, 0), pivR=(-17, 21.5, 0), neck_piv=(26, 24, 0), head_piv=(34, 24, 0), jaw_piv=(40, 20, 0),
    pata_F=dict(hip=(14, 11.5, 11.5), a0=17.5, c0=14.5, L1=6.0, L2=5.6, r1=7.2, r2=5.2, paw=(7.2, 3.0, 6.0),
                garras=4, glen=7.0, gw=2.3, mat='pata', fur=1.5),
    pata_R=dict(hip=(-19, 11.5, 11.0), a0=-20.0, c0=14.0, L1=6.0, L2=5.6, r1=7.4, r2=5.4, paw=(6.8, 3.0, 5.6),
                garras=4, glen=5.4, gw=2.0, mat='pata', fur=1.5),
    stride=14.0, beta=.74, hlift=3.8, bob=.8, kf=.16, kr=.13, sway=.45,
    cola=dict(base=(-32, 18.5, 0), n=5, len=13, r0=6.4, r1=3.6, anillos=True, fur=2.2),
)


_COL = {
    'vetusodon': dict(pelo=(112, 90, 68), claro=(190, 168, 132), pata=(78, 60, 48), oscuro=(58, 44, 38), anillo=(176, 152, 112),
                      oreja=(150, 104, 92), pico=(150, 120, 80), k=.11),
    'gorgonopsio': dict(pelo=(112, 110, 118), claro=(164, 158, 152), pata=(96, 94, 102), oscuro=(74, 72, 82), pico=(150, 130, 100), k=.10),
    'diictodon': dict(pelo=(156, 126, 92), claro=(204, 182, 142), pata=(128, 102, 76), oscuro=(104, 80, 58), pico=(184, 156, 104), k=.10),
    'lystrosaurus': dict(pelo=(106, 106, 84), claro=(156, 152, 124), pata=(90, 90, 70), oscuro=(72, 72, 58), pico=(160, 142, 100), k=.10),
    'anfibio': dict(pelo=(92, 104, 70), claro=(176, 172, 124), pata=(80, 92, 62), oscuro=(48, 58, 40), pico=(150, 130, 100), k=.10),
    'cucaracha': dict(pelo=(104, 60, 34), claro=(160, 104, 56), pata=(78, 44, 28), oscuro=(48, 28, 20), ala=(136, 80, 42), k=.10),
    'escarabajo': dict(pelo=(46, 78, 86), claro=(88, 126, 120), pata=(36, 44, 50), oscuro=(24, 32, 40), ala=(52, 86, 96), k=.08),
    'libelula': dict(pelo=(60, 112, 118), claro=(150, 186, 150), pata=(52, 44, 40), oscuro=(36, 40, 44), ala=(220, 230, 226), k=.10),
}


def materiales(esp, pal):
    c = _COL[esp]
    k = c['k']
    M = {}
    for nm in ('pelo', 'claro', 'pata', 'oscuro', 'pico', 'anillo', 'oreja', 'ala'):
        if nm in c:
            M[nm] = rampa(_C(*c[nm]), pal, k)
    M['garra'] = rampa(_C(226, 212, 182), pal, .10)
    M['nariz'] = rampa(_C(48, 34, 34), pal, .08)
    M['ojo'] = rampa(_C(18, 14, 16), pal, .02)
    M['boca'] = rampa(_C(124, 54, 60), pal, .1)
    M['diente'] = rampa(_C(236, 228, 206), pal, .06)
    M['antena'] = rampa(_C(40, 26, 20), pal, .05)
    return M


# ============================================================================================ POSES
def _stance(fp, beta):
    return fp < beta


def _paso(fp, beta, S, Hl):
    """posicion adelante a (-S/2..S/2), elevacion y cabeceo de la pata para fase fp (0..1)"""
    if fp < beta:
        u = fp / beta
        return S / 2 - S * u, 0.0, -.55 * smooth((u - .72) / .28)
    u = (fp - beta) / (1 - beta)
    e = smooth(u * 1.02)
    return -S / 2 + S * e, Hl * math.sin(math.pi * u) ** .85, .38 * math.sin(math.pi * min(1, u * 1.5))


LEGS = ('LF', 'RF', 'LH', 'RH')
OFF_WALK = dict(LF=.75, RF=.25, LH=0.0, RH=.5)


def pose_cuad(sp, accion, ph):
    ph = ph % 1.0
    P = dict(bt=np.zeros(3), br=np.zeros(3), F=np.zeros(3), R=np.zeros(3), neck=np.zeros(3), head=np.zeros(3),
             headt=np.zeros(3), jaw=0.0, tail=[], sq=(1.0, 1.0), blink=0.0, ov={}, erect=0.0, dirt=0.0,
             feet={})
    pf, pr = sp['pata_F'], sp['pata_R']
    S0, beta, Hl = sp['stride'], sp['beta'], sp['hlift']
    neutro = {'LF': (pf['a0'], -pf['c0']), 'RF': (pf['a0'], pf['c0']), 'LH': (pr['a0'], -pr['c0']), 'RH': (pr['a0'], pr['c0'])}
    ntail = sp['cola']['n'] if sp.get('cola') else 0
    tw = 2 * math.pi
    # parpadeo
    P['blink'] = float(max(0, 1 - abs(((ph * 1.0 + .5) % 1.0 - .5)) / .035)) if accion in ('idle', 'alerta', 'olfatear', 'echado') else 0.0

    def pies(a_off=None):
        for n in LEGS:
            P['feet'][n] = [neutro[n][0], neutro[n][1], 0.0, 0.0]

    pies()
    lag = lambda d: ph - d
    if accion in ('caminar', 'correr'):
        run = accion == 'correr'
        S = S0 * (1.55 if run else 1.0)
        b = .46 if run else beta
        Hh = Hl * (1.9 if run else 1.0)
        off = dict(LF=.5, RF=0.0, LH=0.0, RH=.5) if run else OFF_WALK
        off = {n: (off[n] + (0 if run else 0)) % 1 for n in LEGS}
        F = {}
        sup = {}
        for n in LEGS:
            fp = (ph - off[n]) % 1
            a, lift, pit = _paso(fp, b, S, Hh)
            F[n] = a
            P['feet'][n] = [neutro[n][0] + a, neutro[n][1] + (math.copysign(1, neutro[n][1]) * 1.2 * math.sin(math.pi * max(0, (fp - b) / (1 - b))) if fp >= b else 0), lift, pit]
            sup[n] = 1.0 if fp < b else 0.0
        kf, kr = sp['kf'] * (1.4 if run else 1), sp['kr'] * (1.4 if run else 1)
        yawF = -kf * (F['RF'] - F['LF']) / S
        yawR = kr * (F['LH'] - F['RH']) / S
        P['F'][0], P['R'][0] = yawF, yawR
        if run:
            P['F'][0], P['R'][0] = yawF * .4, yawR * .4
        tot = max(1e-3, sum(sup.values()))
        cs = sum(sup[n] * neutro[n][1] for n in LEGS) / tot
        P['bt'][2] = sp['sway'] * cs / 15.0 * (0.3 if run else 1.0)
        P['br'][2] = -.05 * P['bt'][2] / max(.3, sp['sway']) * (.5 if run else 1)
        phb = ph * 2 * tw
        P['bt'][1] = sp['bob'] * (1.8 if run else 1) * math.cos(phb - (.0 if not run else 1.0))
        if run:
            P['bt'][1] += 1.8
        P['br'][1] = (.05 if not run else .10) * math.sin(phb + .5)
        P['F'][1] = .02 * math.sin(phb + 1.2) * (3 if run else 1)
        P['sq'] = (1 + .012 * math.cos(phb + 1.0) * (3 if run else 1), 1 - .016 * math.cos(phb + 1.0) * (3 if run else 1))
        # cabeza: se estabiliza y cabecea con retraso
        P['neck'][0] = -.55 * P['F'][0] - .35 * P['R'][0]
        P['neck'][1] = -.07 * math.sin(phb + .2) - .5 * P['br'][1]
        P['head'][1] = -.06 * math.sin(phb - .5)
        P['head'][2] = .05 * math.sin(tw * ph)
        P['jaw'] = .08 * (1 + math.sin(phb)) if run else 0.0
        P['tail'] = [(.30 * math.sin(tw * ph - .55 * (i + 1) + 1.0) + yawR * .5, .08 * math.sin(phb - .5 * i) + .05) for i in range(ntail)]
    elif accion == 'olfatear':
        s = math.sin(tw * ph * 3)
        P['neck'][1] = -.52 + .05 * s
        P['head'][1] = -.18 + .08 * math.sin(tw * ph * 3 + 1)
        P['neck'][0] = .30 * math.sin(tw * ph * 1)
        P['head'][0] = .10 * math.sin(tw * ph * 2)
        P['headt'] = np.array([3.0 + .8 * s, -3.0, 0])
        P['F'][1] = -.07
        P['bt'][1] = -1.0
        P['sq'] = (1 + .012 * s, 1 - .012 * s)
        P['jaw'] = .05 * (1 + s)
        P['feet']['LF'][2] = 1.2 * smooth(math.sin(tw * ph) * 1.6)
        P['feet']['LF'][0] += 3 * smooth(math.sin(tw * ph) * 1.6)
        P['tail'] = [(.2 * math.sin(tw * ph - .6 * i) , .05) for i in range(ntail)]
    elif accion == 'escarbar':
        phb = tw * ph * 2
        P['F'][1] = -.16 + .03 * math.sin(phb)
        P['bt'][1] = -1.2
        P['bt'][0] = 1.0 * math.sin(phb + .5)
        P['neck'][1] = -.35
        P['head'][1] = -.20
        P['headt'] = np.array([2.0, -3.5, 0])
        for n, o in (('LF', 0.0), ('RF', .5)):
            u = (ph * 2 + o) % 1
            if u < .6:
                w = u / .6
                a = pf['a0'] + 12 - 22 * w
                lift = 3.0 * math.sin(math.pi * w) * .5
            else:
                w = (u - .6) / .4
                a = pf['a0'] - 10 + 22 * smooth(w)
                lift = 8.5 * math.sin(math.pi * w)
            P['feet'][n] = [a, neutro[n][1] * .78, lift, -.5 if u < .6 else .5]
        P['dirt'] = 1.0
        P['sq'] = (1 + .02 * math.sin(phb), 1 - .02 * math.sin(phb))
        P['tail'] = [(.35 * math.sin(phb * .5 - .6 * i), .12 + .05 * math.sin(phb)) for i in range(ntail)]
        P['jaw'] = .1
    elif accion == 'comer':
        s = math.sin(tw * ph * 3)
        P['neck'][1] = -.62
        P['head'][1] = -.28 + .06 * s
        P['headt'] = np.array([3.5, -4.0 + 1.0 * max(0, s), 0])
        P['jaw'] = .55 * (.5 + .5 * s) + .1
        P['F'][1] = -.09
        P['bt'][1] = -1.0
        P['head'][0] = .08 * math.sin(tw * ph * 3 + 1)
        P['sq'] = (1 + .01 * s, 1 - .012 * s)
        P['tail'] = [(.15 * math.sin(tw * ph - .6 * i), .05) for i in range(ntail)]
    elif accion == 'alerta':
        P['F'][1] = .12
        P['bt'][1] = .9
        P['neck'][1] = .30
        P['head'][1] = .10
        P['neck'][0] = .38 * math.sin(tw * ph)
        P['head'][0] = .22 * math.sin(tw * ph + .6)
        P['erect'] = 1.0
        P['sq'] = (1 + .012 * math.sin(tw * ph * 4), 1 - .014 * math.sin(tw * ph * 4))
        P['tail'] = [(.04 * math.sin(tw * ph * 3 - .5 * i), .38 + .02 * i) for i in range(ntail)]
        for n in ('LF', 'RF'):
            P['feet'][n][0] += 1.5
        P['feet']['RF'][2] = .0
    elif accion == 'pelea':
        w = math.sin(math.pi * ph) ** 1.3                   # 0 agazapado .. 1 embestida
        P['br'][1] = .10 + .30 * w
        P['bt'][1] = -1.0 + 4.0 * w
        P['bt'][0] = -3.0 + 7.0 * w
        P['F'][1] = .12 * w
        P['neck'][1] = -.15 + .50 * w
        P['head'][1] = .05 + .15 * w
        P['jaw'] = .85 * smooth((w - .35) / .5)
        P['headt'] = np.array([3.0 * w, 0, 0])
        P['erect'] = 1.0
        for n, o in (('LF', 0.0), ('RF', .5)):
            q = (ph * 2 + o) % 1
            sw = smooth(w * 1.4) * math.sin(math.pi * q)
            ctr = neutro[n]
            P['ov'][n] = np.array([pf['a0'] + 8 + 12 * sw, 14 + 7 * w + 4 * sw, ctr[1] * .62])
        P['tail'] = [(.5 * math.sin(tw * ph - .5 * i), .30 + .1 * w) for i in range(ntail)]
        P['sq'] = (1 + .03 * w, 1 - .03 * w)
    elif accion == 'echado':
        hb = sp['y0'] - sp['torso'][0][3][1] - 1.0
        s = math.sin(tw * ph)
        P['bt'][1] = -hb
        P['neck'][1] = -.18 + .03 * s
        P['head'][1] = -.10
        P['headt'] = np.array([0, -hb * .6, 0])
        P['sq'] = (1 + .006 * s, 1 + .016 * s)
        P['feet']['LF'] = [pf['a0'] + 6, -pf['c0'] * .55, 0, 0]
        P['feet']['RF'] = [pf['a0'] + 5, pf['c0'] * .55, 0, 0]
        P['feet']['LH'] = [pr['a0'] + 9, -pr['c0'] * .9, 0, 0]
        P['feet']['RH'] = [pr['a0'] + 9, pr['c0'] * .9, 0, 0]
        P['tail'] = [(.7 + .06 * math.sin(tw * ph - .5 * i), .0) for i in range(ntail)]
    else:   # idle
        s = math.sin(tw * ph)
        P['sq'] = (1 + .008 * s, 1 + .018 * s)
        P['bt'][1] = .25 * s
        P['neck'][0] = .12 * math.sin(tw * ph + .3)
        P['head'][0] = .08 * math.sin(tw * ph * 2)
        P['neck'][1] = .03 * s
        P['head'][1] = .03 * math.sin(tw * ph * 2 + 1)
        P['tail'] = [(.12 * math.sin(tw * ph - .7 * (i + 1)), .06) for i in range(ntail)]
        P['feet']['RF'][2] = 0.0
    return P


# ============================================================================================ CONSTRUCCION
def _ik(hip, wrist, L1, L2, pole):
    d = wrist - hip
    D = np.linalg.norm(d)
    Dm = min(D, (L1 + L2) * .995)
    dn = d / (D + 1e-9)
    a = (L1 * L1 - L2 * L2 + Dm * Dm) / (2 * Dm)
    h = math.sqrt(max(L1 * L1 - a * a, 0.01))
    pp = np.asarray(pole, float)
    pp = pp - (pp @ dn) * dn
    pp = pp / (np.linalg.norm(pp) + 1e-9)
    knee = hip + dn * a + pp * h
    wr = hip + dn * Dm
    return knee, wr


def _seg(S, nombre, a, b, r1, r2, mat, ext=1.15, fur=None, mat2=None, tex=None, **kw):
    """elipsoide alargado entre a y b"""
    c = (a + b) / 2
    ln = np.linalg.norm(b - a)
    R = eje_marco(b - a)
    S.add(nombre, c, R, (ln / 2 * ext, r1, r2), mat, fur=fur, mat2=mat2, tex=tex, **kw)


def _pata(S, sp, nombre, hip, foot, cfg, yaw, delante, lado, ov=None):
    pl, ph, pw = cfg['paw']
    a, c, lift, pit = foot
    Rp = _ry(yaw) @ _rp(pit)
    if ov is not None:
        pcn = np.asarray(ov, float)
        Rp = _ry(yaw) @ _rp(-.55)
    else:
        pcn = np.array([a + pl * .30, ph + lift, c])
    wrist = pcn + Rp @ np.array([-pl * .28, ph * .55, 0])
    ab = sp.get('abierto', 1.0)
    pole = (-.55, .10, lado * .85 * ab) if delante else (.65, .08, lado * .85 * ab)
    knee, wr = _ik(np.asarray(hip, float), wrist, cfg['L1'], cfg['L2'], pole)
    fur = _pelo(cfg['fur'], .8, 1.0, comb=(1, 0, 0), out=.5) if sp['piel'] == 'pelo' else None
    mat = cfg['mat']
    bp = 0.0 if sp['piel'] == 'pelo' else sp.get('bump', .3)
    spc = 0.0 if sp['piel'] == 'pelo' else sp.get('spec_piel', 0.0)
    _seg(S, nombre + '_mus', np.asarray(hip, float) + np.array([0, .8, 0]), knee, cfg['r1'], cfg['r1'] * 1.05, mat, 1.12, fur=fur, bias=0.0, bump=bp, spec=spc)
    _seg(S, nombre + '_pant', knee, wr, cfg['r2'] * 1.1, cfg['r2'], mat, 1.2, fur=fur, bias=0.4, bump=bp, spec=spc)
    S.add(nombre + '_rod', knee, np.eye(3), (cfg['r1'] * .78, cfg['r1'] * .78, cfg['r1'] * .78), mat, fur=fur, bias=0.2, bump=bp, spec=spc, rim=.1)
    fp = _pelo(cfg['fur'] * .8, .7, 1.7, comb=(1, -.2, 0), out=.35) if sp['piel'] == 'pelo' else None
    S.add(nombre + '_pata', pcn, Rp, (pl, ph, pw), mat, fur=fp, bias=0.8, bump=bp, spec=spc, rim=.7)
    ng = cfg['garras']
    for j in range(ng):
        f = (j - (ng - 1) / 2) / max(1, (ng - 1) / 2)          # -1..1
        st = pcn + Rp @ np.array([pl * .86, -ph * .15, f * pw * .72])
        ang = .30 + .12 * (1 - abs(f))
        dirv = Rp @ np.array([math.cos(ang), -math.sin(ang), f * .30])
        dirv = dirv / np.linalg.norm(dirv)
        arq = np.array([0, -1.0, 0])
        L = cfg['glen'] * (1 - .15 * abs(f))
        ts = np.linspace(0, 1, 5)
        pts = np.array([st + dirv * L * t * .95 + arq * (L * .20 * t * t) for t in ts])
        S.garra(pts, cfg['gw'] * (1 - .1 * abs(f)), 'garra', w1=.22)


def _cola(S, sp, T, P, mats_extra=None, lagT=None):
    cs = sp.get('cola')
    if not cs:
        return
    base = np.array(cs['base'], float)
    n = cs['n']
    sl = cs['len'] / n
    pos = base.copy()
    Racc = np.eye(3)
    for i in range(n):
        yw, pt = P['tail'][i] if i < len(P['tail']) else (0, 0)
        Racc = Racc @ rot(yw, pt, 0)
        d = Racc @ np.array([-1.0, 0, 0])
        t = i / max(1, n - 1)
        r = cs['r0'] * (1 - t) + cs['r1'] * t
        ctr = pos + d * sl * .5
        Rl = eje_marco(d)
        mat = ('anillo' if (cs.get('anillos') and i % 2 == 1) else (cs.get('mat', 'pelo') if not cs.get('anillos') else 'oscuro'))
        fur = _pelo(cs.get('fur', 3.0), .8, 1.7, comb=(1, 0, 0), out=.4, L2=0) if sp['piel'] == 'pelo' else None
        if fur:
            fur = dict(fur)
        cc = T(ctr)
        if lagT is not None:
            cc = .5 * cc + .5 * lagT(ctr)
        S.add('cola%d' % i, cc, T.R @ Rl, (sl * .78, r, r * .96), mat, fur=fur, bias=-.5 - i * .1,
              bump=(0 if sp['piel'] == 'pelo' else cs.get('bump', .3)), spec=(0 if sp['piel'] == 'pelo' else sp.get('spec_piel', 0.0)), rim=.8)
        pos = pos + d * sl


def construir_cuad(esp, accion, fase, vista, pal, seed, k, D):
    sp = ESP[esp]
    mats = materiales(esp, pal)
    S = Escena(vista, mats, seed, k, D)
    S.pal = pal
    S.sp = sp
    P = pose_cuad(sp, accion, fase)
    Pl = pose_cuad(sp, accion, fase - .09)

    def marcos(P):
        Tb = TF.pivote(rot(*P['br']), (0, sp['y0'], 0), P['bt'])
        TFr = TF.pivote(rot(*P['F']), sp['pivF']).then(Tb)
        TRr = TF.pivote(rot(*P['R']), sp['pivR']).then(Tb)
        Tn = TF.pivote(rot(*P['neck']), sp['neck_piv'], P['headt']).then(TFr)
        Th = TF.pivote(rot(*P['head']), sp['head_piv']).then(Tn)
        return Tb, TFr, TRr, Th

    Tb, TFr, TRr, Th = marcos(P)
    Tbl, TFl, TRl, Thl = marcos(Pl)
    sa, sb = P['sq']
    # torso
    for nm, sec, c, r, tx in sp['torso']:
        T = {'F': TFr, 'R': TRr, 'B': Tb}[sec]
        if sp['piel'] == 'pelo':
            pel = _pelo(sp.get('fur_torso', 3.4), .8, 1.8, comb=(-1, -.35, 0), out=.22)
        else:
            pel = _pelo(sp.get('fold_L', 4.0), sp.get('fold_w', 1.3), sp.get('fold_d', .07), comb=(.25, 1, .15), out=0.0, pliegue=True, curl=.10, borde=1.0, var=.25, jit=.3) if sp.get('fold_L') else None
        S.add(nm, T(c), T.R, (r[0] * sa, r[1] * sb, r[2] * (1 + (1 - sa) * .5)), 'pelo', mat2='claro', tex=tx, fur=pel,
              bump=(0 if sp['piel'] == 'pelo' else sp.get('bump', .35)), spec=(0 if sp['piel'] == 'pelo' else sp.get('spec_piel', 0.0)), rim=.15,
              pliegues=0)
    yaw_t = {'F': P['br'][0] + P['F'][0], 'R': P['br'][0] + P['R'][0]}
    for n in LEGS:
        delante = n[1] == 'F'
        cfg = sp['pata_F'] if delante else sp['pata_R']
        lado = -1 if n[0] == 'L' else 1
        hr = np.array(cfg['hip'], float) * np.array([1, 1, lado])
        T = TFr if delante else TRr
        hip = T(hr)
        ft = list(P['feet'][n])
        ov = P['ov'].get(n)
        _pata(S, sp, 'p' + n, hip, ft, cfg, yaw_t['F' if delante else 'R'], delante, lado, ov)
    _cola(S, sp, TRr, P, lagT=TRl)
    CABEZAS[sp['cabeza']](S, sp, P, Th, Thl, TFr, TFl, Tb)
    if P['dirt'] > 0:
        rg = np.random.default_rng(_hash(seed, 'polvo', int(fase * 24)))
        for n in ('LF', 'RF'):
            ft = P['feet'][n]
            for _ in range(5):
                u = rg.random()
                pos = np.array([ft[0] - 4 - 14 * u * (1 + fase % .5 * 2), 2 + ft[2] * .6 + 10 * u * (1 - u) * 4 + rg.random() * 2, ft[1] + rg.normal(0, 2)])
                S.polvo.append((pos, .8 + rg.random() * 1.6))
    return S


# ============================================================================================ CABEZAS
CABEZAS = {}


def _HA(S, T, Tl, nombre, c, r, mat, R0=None, lag=0.0, **kw):
    R0 = np.eye(3) if R0 is None else R0
    if mat in ('pelo', 'claro', 'pata', 'oscuro') and S.sp['piel'] != 'pelo':
        kw.setdefault('bump', S.sp.get('bump', 0.0))
        kw.setdefault('spec', S.sp.get('spec_piel', 0.0))
    cc = T(c)
    if lag:
        cc = (1 - lag) * cc + lag * Tl(c)
    S.add(nombre, cc, T.R @ R0, r, mat, **kw)


def _diente(S, T, base, dirv, L, w, curv=(0, -1, 0), mat='diente', n=5):
    dirv = np.asarray(dirv, float)
    dirv = dirv / np.linalg.norm(dirv)
    cv = np.asarray(curv, float)
    pts = np.array([T(np.asarray(base, float) + dirv * L * t + cv * (L * .30 * t * t)) for t in np.linspace(0, 1, n)])
    S.garra(pts, w, mat, w1=.15)


def cab_vetusodon(S, sp, P, Th, Thl, TFr, TFl, Tb):
    jaw = P['jaw']
    Tj = TF.pivote(rot(0, -jaw * .55, 0), sp['jaw_piv']).then(Th)
    Tjl = TF.pivote(rot(0, -jaw * .55, 0), sp['jaw_piv']).then(Thl)
    er = P['erect']
    o = np.array([-6.0, 0, 0])
    g = 1.12                                             # cabeza grande (rechoncha)
    fh = lambda L, **kw: _pelo(L, .8, 1.7, comb=(-1, -.25, 0), out=.30 + .2 * er, **kw)
    cc0 = np.array([44, 26.0, 0]) + o
    # cuello grueso
    _HA(S, TFr, TFl, 'cuello', np.array([28, 24.5, 0]), (9, 12.5, 14.0), 'pelo', mat2='claro', tex=('vientre', {}),
        fur=fh(2.2), rim=.3)
    rc = np.array([11.2, 10.4, 10.6]) * g
    _HA(S, Th, Thl, 'craneo', cc0, rc, 'pelo', mat2='claro', tex=('vientre', dict(u=-.2, w=.5)),
        fur=fh(1.5, radial=.3), rim=.45)
    _HA(S, Th, Thl, 'hocico', np.array([56, 22.6, 0]) + o, np.array([8.8, 6.1, 6.9]) * g, 'claro', mat2='pelo', tex=('dorso', dict(u=.35, w=.5)),
        fur=_pelo(.9, .5, 1.8, comb=(1, -.1, 0), out=.15), rim=.45)
    _HA(S, Th, Thl, 'nariz', np.array([64.6, 23.6, 0]) + o, (2.7, 2.3, 3.1), 'nariz', spec=.9, bias=.5, rim=.2)
    _HA(S, Tj, Tjl, 'mandibula', np.array([53, 17.8, 0]) + o, np.array([8.2, 3.7, 5.3]) * g, 'claro', fur=_pelo(.9, .5, 1.5, comb=(1, 0, 0), out=.2), rim=.45)
    if jaw > .15:
        _HA(S, Th, Thl, 'boca', np.array([54, 20.2, 0]) + o, (7.2, 1.8 + 2 * jaw, 4.6), 'boca', bias=-.2)
        for sgn in (-1, 1):
            _diente(S, Tj, np.array([58, 19.8, sgn * 3.6]) + o, (.15, 1, 0), 2.4, 1.0, curv=(0, 1, 0))
    for sgn in (-1, 1):
        _diente(S, Th, np.array([59.5, 19.6, sgn * 3.9]) + o, (.2, -1, 0), 2.8, 1.1, curv=(.4, 0, 0))
    for sgn in (-1, 1):
        u = unit(np.array([.60, .30, sgn * .74]))
        ce = cc0 + rc * u * .985
        _HA(S, Th, Thl, 'ojo%d' % sgn, ce, (1.1, 1.1, .9), 'ojo', R0=eje_marco(u), spec=1.0, bias=.9, rim=0)
        _HA(S, Th, Thl, 'ceja%d' % sgn, ce + np.array([-.3, 1.5, sgn * -.2]), (2.4, 1.0, 1.7), 'oscuro', R0=eje_marco(unit(np.array([1, -.2, sgn * .4]))),
            fur=_pelo(1.0, .6, 1.6, comb=(1, 0, 0), out=.25), bias=1.0, rim=.3)
        _HA(S, Th, Thl, 'oreja%d' % sgn, cc0 + np.array([-1.5, 9.5 * g + 1.0 * er, sgn * 7.0]), (3.6, 4.2 + 1.0 * er, 2.5), 'pelo',
            R0=rot(0, 0, sgn * .4), fur=_pelo(1.1, .6, 1.5, comb=(0, 1, 0), out=.4), lag=.6, rim=.5, bias=-.3)
        _HA(S, Th, Thl, 'oreja_i%d' % sgn, cc0 + np.array([-.7, 9.4 * g + 1.0 * er, sgn * 7.7]), (2.3, 3.0, 1.0), 'oreja', R0=rot(.3, 0, sgn * .4), bias=-.2, rim=.4)
        # mejillas esponjosas (mechones con retraso)
        _HA(S, Th, Thl, 'mejilla%d' % sgn, np.array([45.5, 21.4, sgn * 10.0]) + o, (9.2, 8.6, 5.8), 'pelo', mat2='claro', tex=('cara', dict(u=-.5)),
            R0=rot(sgn * -.25, 0, 0), fur=_pelo(3.2, .9, 1.7, comb=(-1, -.5, sgn * .5), out=.45 + .2 * er, radial=.5), lag=.5, rim=.4, bias=0.5)
        _HA(S, TFr, TFl, 'melena%d' % sgn, np.array([24, 31.0, sgn * 7.5]), (8.0, 5.5, 6.5), 'pelo',
            fur=_pelo(3.0, .9, 1.3, comb=(-1, .2, 0), out=.4 + .3 * er), lag=.7, rim=.3, bias=-.3)
    _HA(S, Th, Thl, 'papada', np.array([46.5, 16.4, 0]) + o, (8.8, 6.4, 8.4), 'claro', fur=_pelo(2.6, .9, 1.4, comb=(-1, -.8, 0), out=.4), lag=.6, rim=.4, bias=.2)
    _HA(S, TFr, TFl, 'pecho_mech', np.array([24, 15.5, 0]), (7.5, 5.5, 8.5), 'claro', fur=_pelo(3.0, .9, 1.3, comb=(-.6, -1, 0), out=.4), lag=.7, rim=.4, bias=.2)


CABEZAS['vetusodon'] = cab_vetusodon
ESP['vetusodon']['cabeza'] = 'vetusodon'
_VT = ('vientre', dict(u=.12, w=.7))
ESP['vetusodon']['torso'] = [
    ('lomo', 'B', (-3, 21.5, 0), (29.5, 17.0, 20.5), _VT),
    ('pecho', 'F', (13, 21.8, 0), (14.5, 17.2, 20.5), _VT),
    ('cadera', 'R', (-19, 21.5, 0), (14.0, 16.5, 19.5), _VT),
]
ESP['vetusodon']['fur_torso'] = 2.1


# ============================================================================================ PIPELINE
def _escala(esp, h_px):
    sp = ESP[esp]
    ss = 1.5 if h_px <= 600 else (1.25 if h_px <= 900 else 1.0)
    return ss, ss * h_px / sp['H']


def _pal(pal):
    return paletas.obtener(pal)


def _construir(esp, accion, fase, vista, pal, seed, k):
    if ESP[esp].get('insecto'):
        return construir_ins(esp, accion, fase, vista, pal, seed, k, ESP[esp]['L'] * 3.5)
    return construir_cuad(esp, accion, fase, vista, pal, seed, k, ESP[esp]['L'] * 3.6)


def _post(col_pm, al_pm, S, pal, ss, rng):
    """luz global, contorno exterior, grano. devuelve RGBA uint8 (a resolucion de supermuestreo)"""
    al = np.clip(al_pm, 0, 1)
    rgb = col_pm / np.maximum(al[..., None], 1e-3)
    H, W = al.shape
    ys = np.where(al.max(1) > .04)[0]
    xs = np.where(al.max(0) > .04)[0]
    y0, y1, x0, x1 = ys[0], ys[-1], xs[0], xs[-1]
    yn = np.clip((np.arange(H) - y0) / (y1 - y0 + 1), 0, 1)[:, None, None]
    xn = np.clip((np.arange(W) - x0) / (x1 - x0 + 1), 0, 1)[None, :, None]
    f = 1 + .22 * (.55 - yn) - .06 * xn
    rgb = rgb * f
    sb = np.array(pal['sombra'], np.float32)
    kk = .20 * yn ** 2.2
    rgb = rgb * (1 - kk) + sb * .55 * kk
    nz = cv2.resize(ruido(H // 4, W // 4, 4 * ss, rng, 3), (W, H), interpolation=cv2.INTER_LINEAR)
    rgb = np.clip(rgb * (1 + (nz[..., None] - .5) * 2 * .08), 0, 255)
    kc = max(1, int(round(1.5 * ss)))
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * kc + 1, 2 * kc + 1))
    dil = cv2.GaussianBlur(cv2.dilate(al, ker), (0, 0), .45 * ss)
    A = np.maximum(al, dil)
    cont = np.array(pal['contorno'], np.float32)
    pm = rgb * al[..., None] + cont * (A - al)[..., None]
    return pm, A


def _grano(pm, A, rng, g=5.5):
    a = np.clip(A, 0, 1)
    rgbf = pm / np.maximum(a[..., None], 1e-3)
    n1 = rng.normal(0, g, A.shape).astype(np.float32)
    n2 = cv2.GaussianBlur(rng.normal(0, 1, A.shape).astype(np.float32), (0, 0), 1.2) * g * 1.6
    rgbf = rgbf + (n1 + n2)[..., None]
    return np.dstack([np.clip(rgbf, 0, 255), np.clip(a * 255, 0, 255)]).astype(np.uint8)


def _pintar_frame(S, W, H, ox, oy, pal, ss, seed):
    col, alf, zb, idb = render(S, W, H, ox, oy)
    r = ao_y_contornos(S, col, alf, zb, pal, ss)
    col, ao = r
    col_pm = col * alf[..., None]
    al_pm = alf.copy()
    pintar_garras(S, col_pm, al_pm, zb, ox, oy)
    pintar_alas(S, col_pm, al_pm, ox, oy)
    order = sorted(range(len(S.prims)), key=lambda i: S.prims[i]['geo'][0][2] if 'geo' in S.prims[i] else 0)
    for i in order:
        trazos(S, S.prims[i], col_pm, al_pm, zb, ao, ox, oy)
    # polvo
    if S.polvo:
        lay = np.zeros((H, W, 4), np.uint8)
        sc = pal['suelo'][1]
        rg = np.random.default_rng(seed)
        for pos, rad in S.polvo:
            q, s_ = S.pc(pos)
            cx, cy = ox + q[0] * S.k * s_, oy + q[1] * S.k * s_
            pts = np.array([[cx + math.cos(a) * rad * S.k * (.7 + .5 * rg.random()), cy + math.sin(a) * rad * S.k * (.7 + .5 * rg.random())]
                            for a in np.linspace(0, 6.28, 7)[:-1]])
            cv2.fillPoly(lay, [np.round(pts * 16).astype(np.int32)], tuple(float(v) for v in esc(sc, .85)) + (255.0,), cv2.LINE_AA, 4)
            cv2.polylines(lay, [np.round(pts * 16).astype(np.int32)], True, tuple(float(v) for v in pal['contorno']) + (255.0,), 1, cv2.LINE_AA, 4)
        a = lay[..., 3:4].astype(np.float32) / 255
        col_pm[:] = lay[..., :3] + col_pm * (1 - a)
        al_pm[:] = a[..., 0] + al_pm * (1 - a[..., 0])
    return col_pm, al_pm


def _a_pil(pm, A, ss, h_px_nom, rng, recorte):
    xa, ya, xb, yb = recorte
    pm = pm[ya:yb, xa:xb]
    A = A[ya:yb, xa:xb]
    nw = max(2, int(round(pm.shape[1] / ss)))
    nh = max(2, int(round(pm.shape[0] / ss)))
    a3 = np.dstack([pm, A])
    a3 = cv2.resize(a3, (nw, nh), interpolation=cv2.INTER_AREA if ss > 1 else cv2.INTER_LINEAR)
    out = _grano(a3[..., :3], a3[..., 3], rng)
    return Image.fromarray(out, 'RGBA')


def _lienzo(extents, k, ss):
    xmin, xmax, ymin, ymax = extents
    mg = int(6 * ss + 10)
    ox = int(-xmin) + mg
    oy = int(-ymin) + mg
    return int(xmax - xmin) + 2 * mg + 2, int(ymax - ymin) + 2 * mg + 2, ox, oy


def _render_set(esp, accion, fases, vista, pal, seed, h_px):
    pal = _pal(pal)
    ss, k = _escala(esp, h_px)
    escs = [_construir(esp, accion, f, vista, pal, seed, k) for f in fases]
    ex = np.array([e.extents() for e in escs])
    ext = (ex[:, 0].min(), ex[:, 1].max(), ex[:, 2].min(), ex[:, 3].max())
    W, H, ox, oy = _lienzo(ext, k, ss)
    pms = []
    for i, S in enumerate(escs):
        S.pal = pal
        cp, ap = _pintar_frame(S, W, H, ox, oy, pal, ss, seed + i)
        rg = np.random.default_rng(seed * 7 + 3)
        pm, A = _post(cp, ap, S, pal, ss, rg)
        pms.append((pm, A))
    # recorte comun
    xa = min(int(np.where(A.max(0) > .04)[0][0]) for pm, A in pms)
    xb = max(int(np.where(A.max(0) > .04)[0][-1]) for pm, A in pms) + 1
    ya = min(int(np.where(A.max(1) > .04)[0][0]) for pm, A in pms)
    yb = max(int(np.where(A.max(1) > .04)[0][-1]) for pm, A in pms) + 1
    out = []
    for i, (pm, A) in enumerate(pms):
        rg = np.random.default_rng(seed * 11 + i)
        im = _a_pil(pm, A, ss, h_px, rg, (xa, ya, xb, yb))
        im.info['ancla'] = ((ox - xa) / ss, (oy - ya) / ss)
        out.append(im)
    return out


def generar(especie, accion='idle', fase=0.0, vista='3q_izq', pal='ambar', seed=0, h_px=400):
    """sprite RGBA de un animal. fase 0..1 (ciclo). Pies apoyados en el borde inferior."""
    accion = _accion_valida(especie, accion)
    im = _render_set(especie, accion, [fase], vista, pal, seed, h_px)[0]
    return _recorta_pies(im)


def _recorta_pies(im):
    a = np.asarray(im)[..., 3]
    ys = np.where(a.max(1) > 10)[0]
    xs = np.where(a.max(0) > 10)[0]
    anc = im.info.get('ancla')
    im2 = im.crop((xs[0], ys[0], xs[-1] + 1, ys[-1] + 1))
    if anc:
        im2.info['ancla'] = (anc[0] - xs[0], anc[1] - ys[0])
    return im2


def _accion_valida(esp, accion):
    ok = ESP[esp].get('acciones')
    if ok is None or accion in ok:
        return accion
    alt = {'pelea': 'alerta', 'olfatear': 'idle', 'escarbar': 'idle', 'correr': 'caminar', 'comer': 'idle', 'echado': 'idle', 'alerta': 'idle'}
    a = alt.get(accion, 'idle')
    return a if a in ok else ok[0]


def _clave_pal(pal):
    p = _pal(pal)
    return '%s_%s' % (p['nombre'], hashlib.md5(json.dumps(p['dom']).encode()).hexdigest()[:4])


def ciclo(especie, accion, vista, pal, n=12, seed=0, h_px=400, usar_cache=True):
    """n sprites alineados (mismo tamano, misma ancla) de un ciclo; cacheados en biblioteca/cache/."""
    accion = _accion_valida(especie, accion)
    os.makedirs(CACHE, exist_ok=True)
    base = '%s_%s_%s_%s_n%d_s%d_h%d_%s' % (especie, accion, vista, _clave_pal(pal), n, seed, h_px, VERSION)
    files = [os.path.join(CACHE, base + '_%02d.png' % i) for i in range(n)]
    meta = os.path.join(CACHE, base + '.json')
    if usar_cache and all(os.path.exists(f) for f in files) and os.path.exists(meta):
        anc = json.load(open(meta))['ancla']
        out = []
        for f in files:
            im = Image.open(f).convert('RGBA')
            im.info['ancla'] = tuple(anc)
            out.append(im)
        return out
    ims = _render_set(especie, accion, [i / n for i in range(n)], vista, pal, seed, h_px)
    for f, im in zip(files, ims):
        im.save(f)
    json.dump(dict(ancla=ims[0].info['ancla']), open(meta, 'w'))
    return ims


def sombra_contacto(especie, vista, pal='ambar', h_px=400, accion='idle', alpha=.5):
    pal = _pal(pal)
    sp = ESP[especie]
    ss, k = _escala(especie, h_px)
    S = Escena(vista, {}, 0, k, sp['L'] * 3.6)
    Lh, Wh = sp['L'] * .56, sp['L'] * .26
    if accion in ('echado',):
        Lh, Wh = Lh * 1.05, Wh * 1.1
    pts = np.array([[math.cos(t) * Lh, 0, math.sin(t) * Wh] for t in np.linspace(0, 2 * math.pi, 48, endpoint=False)])
    q, sc = S.pc(pts)
    P = np.stack([q[:, 0] * k * sc, q[:, 1] * k * sc], 1)
    xmin, ymin = P.min(0) - 20
    xmax, ymax = P.max(0) + 20
    W, H = int(xmax - xmin), int(ymax - ymin)
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [np.round((P - [xmin, ymin]) * 16).astype(np.int32)], 255, cv2.LINE_AA, 4)
    m = cv2.GaussianBlur(m, (0, 0), max(2, k * 3.2)).astype(np.float32) / 255
    col = np.array(pal['sombra'], np.float32) * .6
    out = np.dstack([np.tile(col, (H, W, 1)), m * alpha * 255]).astype(np.uint8)
    im = Image.fromarray(out, 'RGBA').resize((max(2, int(W / ss)), max(2, int(H / ss))), Image.LANCZOS)
    im.info['ancla'] = (-xmin / ss, -ymin / ss)
    return im


def avance_px(especie, accion, vista, h_px=400):
    """desplazamiento en pantalla (dx, dy) del animal por ciclo completo de caminata/carrera"""
    sp = ESP[especie]
    ss, k = _escala(especie, h_px)
    S = Escena(vista, {}, 0, k, 1e9)
    f = 1.55 if accion == 'correr' else 1.0
    b = .46 if accion == 'correr' else sp['beta']
    dist = sp['stride'] * f / b
    v = S.proj @ np.array([dist, 0, 0])
    return (v[0] * k / ss, v[1] * k / ss)


# ============================================================================================ OTRAS ESPECIES
_VT0 = ('vientre', dict(u=.12, w=.7))


def _tex_piel(u=.1):
    return ('vientre', dict(u=u, w=.8))


ESP['gorgonopsio'] = dict(
    L=140.0, H=58.0, real_cm=200, piel='piel', bump=.42, spec_piel=.10, fold_L=5.5, fold_w=1.3, fold_d=.07,
    y0=30.0, pivF=(16, 30, 0), pivR=(-24, 30, 0), neck_piv=(32, 31, 0), head_piv=(44, 31, 0), jaw_piv=(55, 24, 0),
    pata_F=dict(hip=(17, 16, 15), a0=22, c0=20, L1=9.5, L2=8.5, r1=9.5, r2=6.8, paw=(9.5, 3.6, 7.6),
                garras=4, glen=5.6, gw=2.8, mat='pata', fur=0),
    pata_R=dict(hip=(-26, 16, 15), a0=-27, c0=19.5, L1=9.5, L2=8.5, r1=10, r2=7.0, paw=(9.0, 3.6, 7.4),
                garras=4, glen=5.0, gw=2.6, mat='pata', fur=0),
    stride=20.0, beta=.76, hlift=4.5, bob=1.0, kf=.12, kr=.10, sway=.6,
    cola=dict(base=(-41, 25, 0), n=3, len=11, r0=6.8, r1=3.6),
    torso=[('lomo', 'B', (-4, 30, 0), (36, 21, 24), _tex_piel()),
           ('pecho', 'F', (15, 30.3, 0), (18, 22, 24.5), _tex_piel()),
           ('cadera', 'R', (-26, 29.8, 0), (17, 20.5, 22.5), _tex_piel())],
    cabeza='gorgon',
    acciones=['idle', 'caminar', 'olfatear', 'comer', 'alerta', 'pelea', 'echado', 'correr'],
)

ESP['diictodon'] = dict(
    L=45.0, H=25.0, real_cm=45, piel='piel', bump=.30, spec_piel=.08, fold_L=2.4, fold_w=1.0, fold_d=.07,
    y0=12.5, pivF=(6, 12.5, 0), pivR=(-11, 12.5, 0), neck_piv=(14, 14, 0), head_piv=(19, 14.5, 0), jaw_piv=(24, 11.5, 0),
    pata_F=dict(hip=(9, 6.5, 8.0), a0=11, c0=10.5, L1=3.8, L2=3.5, r1=4.2, r2=3.0, paw=(4.6, 1.8, 3.8),
                garras=4, glen=4.6, gw=1.5, mat='pata', fur=0),
    pata_R=dict(hip=(-13, 6.5, 7.5), a0=-14, c0=10, L1=3.8, L2=3.5, r1=4.3, r2=3.0, paw=(4.2, 1.8, 3.4),
                garras=4, glen=3.4, gw=1.3, mat='pata', fur=0),
    stride=8.0, beta=.74, hlift=2.2, bob=.5, kf=.2, kr=.16, sway=.35,
    cola=dict(base=(-20, 10.5, 0), n=3, len=7, r0=3.6, r1=2.0),
    torso=[('lomo', 'B', (-3, 12.5, 0), (17.5, 10.2, 12.0), _tex_piel()),
           ('pecho', 'F', (7, 12.8, 0), (9.5, 10.4, 12.2), _tex_piel()),
           ('cadera', 'R', (-14, 12.6, 0), (9.0, 9.8, 11.5), _tex_piel())],
    cabeza='dicino', hd=dict(s=1.0, o=(0, 0, 0), pico_pit=-.15, tusk=4.2, eye_u=(.45, .40, .80)),
    acciones=['idle', 'caminar', 'olfatear', 'escarbar', 'comer', 'alerta', 'echado', 'correr'],
)

ESP['lystrosaurus'] = dict(
    L=70.0, H=37.0, real_cm=70, piel='piel', bump=.34, spec_piel=.06, fold_L=3.6, fold_w=1.2, fold_d=.07,
    y0=19.0, pivF=(9, 19, 0), pivR=(-17, 19, 0), neck_piv=(21, 21, 0), head_piv=(28, 21.5, 0), jaw_piv=(36, 17, 0),
    pata_F=dict(hip=(13, 10, 12), a0=16.5, c0=15.5, L1=5.8, L2=5.3, r1=6.5, r2=4.6, paw=(6.5, 2.6, 5.4),
                garras=4, glen=3.4, gw=2.0, mat='pata', fur=0),
    pata_R=dict(hip=(-20, 10, 11.5), a0=-21, c0=15, L1=5.8, L2=5.3, r1=6.4, r2=4.5, paw=(6.2, 2.6, 5.0),
                garras=4, glen=3.0, gw=1.8, mat='pata', fur=0),
    stride=11.0, beta=.76, hlift=3.0, bob=.7, kf=.14, kr=.11, sway=.5,
    cola=dict(base=(-29, 15.5, 0), n=3, len=8, r0=5.0, r1=2.6),
    torso=[('lomo', 'B', (-4, 19, 0), (26, 15, 18), _tex_piel()),
           ('pecho', 'F', (12, 19.3, 0), (14, 15.5, 18.5), _tex_piel()),
           ('cadera', 'R', (-21, 19, 0), (13, 14.5, 17.5), _tex_piel())],
    cabeza='dicino', hd=dict(s=1.5, o=(-1.5, 4.0, 0), pico_pit=-.55, tusk=5.5, eye_u=(.30, .62, .72), alto=True),
    acciones=['idle', 'caminar', 'olfatear', 'comer', 'alerta', 'echado', 'correr', 'pelea'],
)

ESP['anfibio'] = dict(
    L=18.0, H=11.0, real_cm=16, piel='piel', bump=.22, spec_piel=.35, fold_L=0, abierto=2.2,
    y0=3.3, pivF=(4, 3.3, 0), pivR=(-6, 3.3, 0), neck_piv=(8, 3.5, 0), head_piv=(10, 3.5, 0), jaw_piv=(12, 2.4, 0),
    pata_F=dict(hip=(5, 2.2, 3.0), a0=6.5, c0=5.8, L1=1.9, L2=1.7, r1=1.0, r2=.75, paw=(1.9, .5, 1.7),
                garras=4, glen=.9, gw=.5, mat='pata', fur=0),
    pata_R=dict(hip=(-8, 2.2, 3.0), a0=-9, c0=5.6, L1=1.9, L2=1.7, r1=1.1, r2=.8, paw=(2.0, .5, 1.8),
                garras=4, glen=.9, gw=.5, mat='pata', fur=0),
    stride=3.4, beta=.72, hlift=1.0, bob=.08, kf=.30, kr=.24, sway=.25,
    cola=dict(base=(-12, 3.0, 0), n=4, len=9, r0=2.4, r1=.7),
    torso=[('lomo', 'B', (-2, 3.4, 0), (9, 2.8, 3.6), _tex_piel(.0)),
           ('pecho', 'F', (5, 3.3, 0), (4.6, 2.8, 3.8), _tex_piel(.0)),
           ('cadera', 'R', (-8, 3.3, 0), (4.6, 2.7, 3.5), _tex_piel(.0))],
    cabeza='anfibio',
    acciones=['idle', 'caminar', 'olfatear', 'comer', 'alerta', 'echado'],
)


def cab_gorgon(S, sp, P, Th, Thl, TFr, TFl, Tb):
    jaw = P['jaw']
    Tj = TF.pivote(rot(0, -jaw * .7, 0), sp['jaw_piv']).then(Th)
    Tjl = Tj
    sk = dict(bump=sp['bump'], spec=sp['spec_piel'])
    _HA(S, TFr, TFl, 'cuello', (31, 30.5, 0), (11, 15.5, 17.5), 'pelo', mat2='claro', tex=('vientre', {}),
        fur=_pelo(sp['fold_L'], 1.3, .08, comb=(.2, 1, .2), out=0, pliegue=True, curl=.1, borde=1, var=.25, jit=.3), rim=.3, **sk)
    cc0 = np.array([50, 32.5, 0])
    rc = np.array([12.5, 11.0, 11.8])
    _HA(S, Th, Thl, 'craneo', cc0, rc, 'pelo', mat2='oscuro', tex=('dorso', dict(u=.3, w=.5)), rim=.4, **sk)
    _HA(S, Th, Thl, 'hocico', (66, 28.5, 0), (15, 7.6, 8.4), 'pelo', mat2='claro', tex=('vientre', dict(u=.0, w=.6)), rim=.45, **sk)
    _HA(S, Th, Thl, 'nariz', (79.5, 29.5, 0), (3.4, 3.0, 4.2), 'nariz', spec=.6, bias=.5, rim=.2, bump=.2)
    _HA(S, Tj, Tjl, 'mandibula', (63.5, 21.2, 0), (14.5, 4.0, 6.4), 'claro', rim=.45, **sk)
    _HA(S, Th, Thl, 'mejilla_m', (51, 27, 0), (9.5, 8.2, 12.4), 'pelo', rim=.3, **sk, bias=-.3)
    if jaw > .12:
        _HA(S, Th, Thl, 'boca', (64, 23.0, 0), (13, 1.8 + 3.2 * jaw, 5.2), 'boca', bias=-.2)
    for sgn in (-1, 1):
        # sables
        _diente(S, Th, np.array([75.0, 25.6, sgn * 5.3]), (.12, -1, 0), 12.5, 3.0, curv=(-.7, 0, 0), n=7)
        _diente(S, Th, np.array([79.0, 26.2, sgn * 2.0]), (.2, -1, 0), 3.0, 1.5, curv=(-.3, 0, 0))
        _diente(S, Tj, np.array([76.0, 23.6, sgn * 3.4]), (.2, 1, 0), 3.4, 1.4, curv=(0, 0, 0))
        u = unit(np.array([.55, .45, sgn * .70]))
        ce = cc0 + rc * u * .985
        _HA(S, Th, Thl, 'ojo%d' % sgn, ce, (1.3, 1.3, 1.0), 'ojo', R0=eje_marco(u), spec=1.0, bias=.9, rim=0, bump=0)
        _HA(S, Th, Thl, 'ceja%d' % sgn, ce + np.array([-.5, 1.9, sgn * -.3]), (4.2, 1.5, 2.8), 'oscuro', R0=eje_marco(unit(np.array([1, -.2, sgn * .4]))),
            bias=1.0, rim=.3, **sk)
    _HA(S, Th, Thl, 'papada', (55, 20.5, 0), (9.5, 5.5, 8.8), 'claro', fur=_pelo(3.5, 1.2, .08, comb=(0, 1, 0), out=0, pliegue=True, curl=.1, borde=1, var=.25, jit=.3),
        lag=.5, rim=.4, bias=.1, **sk)


def cab_dicino(S, sp, P, Th, Thl, TFr, TFl, Tb):
    hd = sp['hd']
    s_ = hd['s']
    o = np.array(hd['o'], float)
    jaw = P['jaw']
    Tj = TF.pivote(rot(0, -jaw * .6, 0), sp['jaw_piv']).then(Th)
    sk = dict(bump=sp['bump'], spec=sp['spec_piel'])
    ge = lambda c: np.array(c, float) * s_ + o
    nk = np.array(sp['neck_piv'], float)
    _HA(S, TFr, TFl, 'cuello', nk + np.array([-1, 0, 0]) * s_, np.array([5.5, 7.2, 8.8]) * s_, 'pelo', mat2='claro', tex=('vientre', {}), rim=.3,
        fur=(_pelo(sp['fold_L'], 1.0, .08, comb=(.2, 1, .2), out=0, pliegue=True, curl=.1, borde=1, var=.25, jit=.3)), **sk)
    cc0 = ge((22, 16.5, 0)) if not hd.get('alto') else ge((22, 16.5, 0))
    rc = np.array([7.8, 7.2, 7.8]) * s_
    _HA(S, Th, Thl, 'craneo', cc0, rc, 'pelo', mat2='claro', tex=('vientre', dict(u=-.1, w=.6)), rim=.4, **sk)
    _HA(S, Th, Thl, 'hocico', ge((29.5, 14.4, 0)), np.array([5.4, 4.4, 5.0]) * s_, 'claro', mat2='pelo', tex=('dorso', dict(u=.3, w=.5)), rim=.45, **sk)
    pp = hd['pico_pit']
    pc_ = ge((34.2, 13.2, 0))
    _HA(S, Th, Thl, 'pico', pc_, np.array([3.7, 2.5, 2.7]) * s_, 'pico', R0=rot(0, pp, 0), spec=.18, bump=.12, rim=.5, bias=.3)
    _HA(S, Th, Thl, 'pico_b', pc_ + np.array([-.6, -2.1, 0]) * s_, np.array([3.0, 1.3, 2.4]) * s_, 'pico', R0=rot(0, pp, 0), spec=.15, bump=.1, rim=.5, bias=.1)
    _HA(S, Tj, Tj, 'mandibula', ge((29, 10.8, 0)), np.array([5.0, 2.1, 3.7]) * s_, 'claro', rim=.45, **sk)
    if jaw > .12:
        _HA(S, Th, Thl, 'boca', ge((29, 12.0, 0)), np.array([4.6, 1.2 + 2 * jaw, 3.2]) * s_, 'boca', bias=-.2)
    for sgn in (-1, 1):
        _diente(S, Th, ge((32.6, 11.8, sgn * 2.9)), (.10, -1, 0), hd['tusk'], 1.5 * s_ ** .6, curv=(-.5, 0, 0), n=6)
        u = unit(np.array(hd['eye_u']) * np.array([1, 1, sgn]))
        ce = cc0 + rc * u * .985
        _HA(S, Th, Thl, 'ojo%d' % sgn, ce, np.array([.95, .95, .8]) * max(1, s_ ** .5), 'ojo', R0=eje_marco(u), spec=1.0, bias=.9, rim=0, bump=0)
        _HA(S, Th, Thl, 'ceja%d' % sgn, ce + np.array([-.2, 1.2, sgn * -.2]) * s_, np.array([2.4, 1.0, 1.7]) * s_, 'oscuro',
            R0=eje_marco(unit(np.array([1, -.2, sgn * .4]))), bias=1.0, rim=.3, **sk)
        _HA(S, Th, Thl, 'mejilla%d' % sgn, ge((21, 13.4, sgn * 6.2)), np.array([5.2, 4.2, 3.0]) * s_, 'pelo', rim=.35, bias=-.3, **sk)
        _HA(S, Th, Thl, 'nariz%d' % sgn, ge((32.2, 15.6 if not hd.get('alto') else 16.8, sgn * 1.7)), np.array([.9, .7, .8]) * s_, 'nariz', bias=.6, rim=0, bump=0)


def cab_anfibio(S, sp, P, Th, Thl, TFr, TFl, Tb):
    jaw = P['jaw']
    Tj = TF.pivote(rot(0, -jaw * .5, 0), sp['jaw_piv']).then(Th)
    sk = dict(bump=sp['bump'], spec=sp['spec_piel'])
    cc0 = np.array([13.5, 3.5, 0])
    rc = np.array([6.0, 2.3, 5.6])
    _HA(S, Th, Thl, 'craneo', cc0, rc, 'pelo', mat2='claro', tex=('vientre', dict(u=-.3, w=.6)), rim=.4, **sk)
    _HA(S, Th, Thl, 'hocico', (18.2, 3.0, 0), (3.2, 1.8, 3.9), 'pelo', mat2='claro', tex=('vientre', dict(u=-.2, w=.6)), rim=.4, **sk)
    _HA(S, Tj, Tj, 'mandibula', (15.5, 1.9, 0), (4.6, 1.0, 4.6), 'claro', rim=.4, **sk)
    _HA(S, Th, Thl, 'garganta', (13.5, 1.4, 0), (3.8, 1.2 + .5 * (1 + math.sin(P['sq'][1] * 80)) * .3, 3.5), 'claro', rim=.3, bias=.1, **sk)
    if jaw > .1:
        _HA(S, Th, Thl, 'boca', (15.5, 2.5, 0), (4.2, .5 + 1.3 * jaw, 3.8), 'boca', bias=-.2)
    for sgn in (-1, 1):
        u = unit(np.array([.35, .85, sgn * .45]))
        ce = cc0 + rc * u * .985
        _HA(S, Th, Thl, 'ojo%d' % sgn, ce, (.8, .7, .8), 'ojo', R0=eje_marco(u), spec=1.0, bias=.9, rim=0, bump=0)
        _HA(S, Th, Thl, 'parpado%d' % sgn, ce + np.array([-.05, .2, 0]), (1.1, .5, 1.0), 'oscuro', R0=eje_marco(u), bias=.8, rim=.3, **sk)
        _HA(S, Th, Thl, 'nariz%d' % sgn, (20.8, 3.7, sgn * 1.0), (.3, .25, .3), 'nariz', bias=.6, rim=0, bump=0)


CABEZAS['gorgon'] = cab_gorgon
CABEZAS['dicino'] = cab_dicino
CABEZAS['anfibio'] = cab_anfibio
for _k in ('gorgonopsio', 'diictodon', 'lystrosaurus', 'anfibio'):
    ESP[_k].setdefault('fur_torso', 2.0)
ESP['vetusodon']['acciones'] = ['idle', 'caminar', 'olfatear', 'escarbar', 'comer', 'alerta', 'pelea', 'echado', 'correr']


# ============================================================================================ INSECTOS
def _pata_ins(a0, c0, hipa, hipc, hipy, L1, L2, r, spine=2):
    return dict(hip=(hipa, hipy, hipc), a0=a0, c0=c0, L1=L1, L2=L2, r=r, spine=spine)


def _ins_patas(hipy, hips, feet, L1, L2, r, spine=2):
    d = {}
    for nm, (ha, hc), (fa, fc) in zip(('LF', 'LM', 'LH', 'RF', 'RM', 'RH'), hips, feet):
        d[nm] = _pata_ins(fa, fc, ha, hc, hipy, L1, L2, r, spine)
    return d


def _mk_ins(**kw):
    kw.setdefault('piel', 'piel')
    kw['insecto'] = True
    return kw


ESP['cucaracha'] = _mk_ins(
    L=3.6, H=2.6, real_cm=4.0, y0=.75, stride=1.5, beta=.5, hlift=.55, bob=.02,
    patas=_ins_patas(.45, [(1.4, -.7), (.35, -.8), (-.7, -.85), (1.4, .7), (.35, .8), (-.7, .85)],
                     [(2.2, -1.9), (.5, -2.2), (-1.4, -2.1), (2.2, 1.9), (.5, 2.2), (-1.4, 2.1)], 1.0, 1.35, .13),
    ant=dict(base=(2.45, .72, .16), L=3.2, n=9, w=.085),
    acciones=['idle', 'caminar', 'correr', 'alerta', 'comer', 'olfatear'],
)
ESP['escarabajo'] = _mk_ins(
    L=3.2, H=1.9, real_cm=3.0, y0=.72, stride=1.1, beta=.5, hlift=.5, bob=.02,
    patas=_ins_patas(.5, [(1.2, -.85), (.2, -.95), (-.8, -.9), (1.2, .85), (.2, .95), (-.8, .9)],
                     [(1.9, -1.9), (.3, -2.1), (-1.3, -1.9), (1.9, 1.9), (.3, 2.1), (-1.3, 1.9)], .85, 1.0, .17),
    ant=dict(base=(2.15, .78, .25), L=1.1, n=5, w=.07),
    acciones=['idle', 'caminar', 'correr', 'alerta', 'comer', 'olfatear'],
)
ESP['libelula'] = _mk_ins(
    L=9.0, H=4.2, real_cm=14.0, y0=1.9, stride=1.2, beta=.5, hlift=.5, bob=.02,
    patas=_ins_patas(1.3, [(1.55, -.4), (1.15, -.45), (.75, -.4), (1.55, .4), (1.15, .45), (.75, .4)],
                     [(2.5, -1.2), (1.8, -1.5), (1.0, -1.4), (2.5, 1.2), (1.8, 1.5), (1.0, 1.4)], 1.0, 1.15, .11),
    acciones=['idle', 'caminar', 'correr', 'alerta'],
)

OFF_TRI = dict(LF=0.0, RM=0.0, LH=0.0, RF=.5, LM=.5, RH=.5)
LEGS6 = ('LF', 'LM', 'LH', 'RF', 'RM', 'RH')


def pose_ins(sp, esp, accion, ph):
    ph = ph % 1
    tw = 2 * math.pi
    P = dict(bt=np.zeros(3), br=np.zeros(3), feet={}, ant=(0.0, 0.0), flap=-.12, vuelo=0.0, sq=(1, 1), abd=0.0, fl2=0.0)
    for n in LEGS6:
        pa = sp['patas'][n]
        P['feet'][n] = [pa['a0'], pa['c0'], 0.0]
    if accion in ('caminar', 'correr'):
        run = accion == 'correr'
        S = sp['stride'] * (1.6 if run else 1.0)
        Hh = sp['hlift'] * (1.4 if run else 1.0)
        b = .5 if not run else .42
        for n in LEGS6:
            pa = sp['patas'][n]
            fp = (ph - OFF_TRI[n]) % 1
            a, lift, _ = _paso(fp, b, S, Hh)
            P['feet'][n] = [pa['a0'] + a * (.6 if n[1] == 'M' else 1.0), pa['c0'], lift]
        P['br'][0] = .10 * math.sin(tw * ph) * (1.4 if run else 1)
        P['bt'][1] = .03 * math.cos(tw * ph * 2)
        P['br'][2] = .03 * math.sin(tw * ph)
        P['ant'] = (.35 * math.sin(tw * ph * 2), .12 * math.sin(tw * ph * 2 + 1))
        if esp == 'libelula':
            P['vuelo'] = 1.0
            P['bt'][1] = 3.2 + .5 * math.sin(tw * ph)
            P['br'][1] = .12 + .05 * math.sin(tw * ph * 2)
            P['flap'] = .85 * math.sin(tw * ph * (3 if not run else 5))
            P['fl2'] = .85 * math.sin(tw * ph * (3 if not run else 5) + math.pi * .55)
            P['abd'] = -.12 + .05 * math.sin(tw * ph * 2)
    elif accion == 'alerta':
        P['ant'] = (.5 * math.sin(tw * ph * 3), .25 + .08 * math.sin(tw * ph * 4))
        P['bt'][1] = .05
        P['br'][1] = .10
        P['flap'] = -.12 + .08 * math.sin(tw * ph * 8)
        P['fl2'] = P['flap']
        P['sq'] = (1, 1 + .015 * math.sin(tw * ph * 4))
        P['br'][0] = .15 * math.sin(tw * ph)
    elif accion in ('comer', 'olfatear'):
        P['br'][1] = -.12
        P['ant'] = (.2 * math.sin(tw * ph * 4), -.2 + .2 * math.sin(tw * ph * 4))
        P['sq'] = (1, 1 + .012 * math.sin(tw * ph * 2))
        P['bt'][1] = -.04
    else:
        P['ant'] = (.18 * math.sin(tw * ph + .5), .05 * math.sin(tw * ph * 2))
        P['sq'] = (1, 1 + .014 * math.sin(tw * ph))
        P['flap'] = -.12 + .02 * math.sin(tw * ph * 2)
        P['fl2'] = P['flap'] + .02
        P['abd'] = .03 * math.sin(tw * ph)
    P['fl2'] = P.get('fl2', P['flap']) if accion not in ('idle',) else P['flap']
    return P


def _ala(S, root, side, flap, sweep, span, chord, droop=0.0):
    n = 14
    xs = np.linspace(0, 1, n)
    le = .28 * chord * np.sin(np.pi * np.minimum(1, xs * 1.12)) ** .8
    te = -(chord * .72 * np.sin(np.pi * np.minimum(1, xs * 1.0) ** .75) ** .8 + .22 * chord * (1 - xs))
    loc_le = np.stack([le, np.zeros(n), xs * span * side], 1)
    loc_te = np.stack([te, np.zeros(n), xs * span * side], 1)
    R = rot(sweep * side, 0, (flap - droop) * side)
    root = np.asarray(root, float)
    pts = np.vstack([loc_le, loc_te[::-1]]) @ R.T + root
    venas = []
    for j in np.linspace(.1, .9, 6):
        ln = (loc_le * (1 - j) + loc_te * j)[1:]
        venas.append(ln @ R.T + root)
    for i in range(3, n - 1, 2):
        ln = np.array([loc_le[i], loc_te[i]])
        venas.append(ln @ R.T + root)
    stig = np.array([loc_le[10], loc_le[12], loc_le[12] + [-.14 * chord, 0, 0], loc_le[10] + [-.14 * chord, 0, 0]]) @ R.T + root
    S.alas.append(dict(pts=pts, venas=venas, alpha=.50, stigma=stig))


def _antena(S, base, d0, L, n, w, sway, lift, lado, mat='antena'):
    pts = []
    pos = np.array(base, float)
    ang_y = lado * (.45 + sway)
    ang_p = lift
    ds = L / (n - 1)
    for i in range(n):
        pts.append(pos.copy())
        t = i / (n - 1)
        ay = ang_y + lado * .35 * t + .25 * math.sin(i * .8 + sway * 4) * t * lado
        ap = ang_p - .10 * t
        d = np.array([math.cos(ap) * math.cos(ay), math.sin(ap), math.cos(ap) * math.sin(ay)])
        pos = pos + d * ds
    S.garra(np.array(pts), w, mat, w1=w * .35)


def construir_ins(esp, accion, fase, vista, pal, seed, k, D):
    sp = ESP[esp]
    mats = materiales(esp, pal)
    S = Escena(vista, mats, seed, k, D)
    S.pal = pal
    S.sp = sp
    P = pose_ins(sp, esp, accion, fase)
    Tb = TF.pivote(rot(*P['br']), (0, sp['y0'], 0), P['bt'])
    sa, sb = P['sq']
    A = lambda nm, c, r, mat, R0=None, **kw: S.add(nm, Tb(c), Tb.R @ (np.eye(3) if R0 is None else R0), r, mat, **kw)
    if esp == 'cucaracha':
        A('abd', (-1.0, .75, 0), (1.75 * sa, .5 * sb, 1.15), 'pelo', spec=.55, rim=.5)
        A('tegm', (-.8, .98, 0), (1.8, .2, 1.12), 'ala', spec=.6, rim=.4, bias=.2)
        A('pron', (1.35, .85, 0), (.8, .38, 1.0), 'claro', spec=.5, rim=.5, bias=.3)
        A('pron_m', (1.30, 1.0, 0), (.5, .16, .62), 'oscuro', spec=.5, rim=.3, bias=.4)
        A('cabeza', (2.2, .6, 0), (.5, .42, .52), 'pata', spec=.5, rim=.5)
        for sg in (-1, 1):
            A('ojo%d' % sg, (2.45, .8, sg * .3), (.13, .13, .13), 'ojo', spec=1, rim=0, bias=.5)
            A('cerco%d' % sg, (-2.8, .6, sg * .35), (.55, .1, .1), 'pata', rim=.3)
        a_, c_ = P['ant']
        for sg in (-1, 1):
            an = sp['ant']
            _antena(S, Tb(np.array((2.5, .75, sg * .2))), None, an['L'], an['n'], an['w'], a_ * sg, c_ + .1, sg)
    elif esp == 'escarabajo':
        for sg in (-1, 1):
            A('elit%d' % sg, (-.35, .98, sg * .50), (1.5 * sa, .88 * sb, .70), 'pelo', mat2='claro', tex=('vientre', dict(u=.35, w=.6)), spec=.95, rim=.5)
        A('pron', (1.2, .86, 0), (.7, .5, .98), 'pelo', mat2='claro', tex=('vientre', dict(u=.3, w=.6)), spec=.8, rim=.5, bias=.2)
        A('cabeza', (2.0, .62, 0), (.46, .38, .52), 'oscuro', spec=.5, rim=.5)
        A('cuerno', (2.15, 1.05, 0), (.5, .22, .14), 'oscuro', R0=rot(0, .5, 0), spec=.6, rim=.4)
        for sg in (-1, 1):
            A('ojo%d' % sg, (2.18, .8, sg * .38), (.12, .12, .12), 'ojo', spec=1, rim=0, bias=.5)
            S.garra(np.array([Tb(np.array((2.35, .52, sg * .22))), Tb(np.array((2.75, .45, sg * .2))), Tb(np.array((2.95, .38, sg * .08)))]), .13, 'oscuro', w1=.04)
        a_, c_ = P['ant']
        for sg in (-1, 1):
            an = sp['ant']
            _antena(S, Tb(np.array((2.2, .85, sg * .3))), None, an['L'], an['n'], an['w'], a_ * sg, c_ + .2, sg)
    else:   # libelula
        fl, fl2 = P['flap'], P['fl2']
        A('torax', (1.0, 1.9, 0), (1.15 * sa, .98 * sb, .88), 'pelo', mat2='claro', tex=('vientre', dict(u=-.1, w=.6)), spec=.6, rim=.4)
        n = 9
        pos = np.array([-.1, 1.8, 0.0])
        Rc = np.eye(3)
        for i in range(n):
            Rc = Rc @ rot(0, P['abd'] + .02, 0)
            d = Rc @ np.array([-1.0, 0, 0])
            ln = .86
            ctr = pos + d * ln * .5
            t = i / (n - 1)
            r = .46 * (1 - t) + .27 * t
            A('abd%d' % i, ctr, (ln * .62, r, r * .95), 'oscuro' if i % 2 else 'pelo', R0=eje_marco(d), spec=.5, rim=.35, bias=-.1 - i * .01)
            pos = pos + d * ln * .93
        A('cabeza', (2.35, 1.75, 0), (.56, .55, .74), 'pelo', spec=.5, rim=.4)
        for sg in (-1, 1):
            A('ojo%d' % sg, (2.45, 1.96, sg * .5), (.42, .42, .42), 'claro', spec=1, rim=.3, bias=.4)
            A('pupila%d' % sg, (2.78, 2.0, sg * .55), (.11, .11, .11), 'ojo', spec=1, rim=0, bias=.8)
            span = 6.8
            _ala(S, Tb(np.array((1.15, 2.78, sg * .5))), sg, fl, .10, span, 1.5, droop=0)
            _ala(S, Tb(np.array((.35, 2.78, sg * .5))), sg, fl2, -.12, span * .96, 1.75, droop=0)
    # patas
    for n in LEGS6:
        pa = sp['patas'][n]
        lado = -1 if n[0] == 'L' else 1
        hip = Tb(np.array(pa['hip']))
        fa, fc, lift = P['feet'][n]
        if esp == 'libelula' and P['vuelo']:
            foot = Tb(np.array([pa['hip'][0] + .7 + (.3 if n[1] == 'F' else 0), pa['hip'][1] - 1.2, pa['hip'][2] * 1.8]))
        else:
            foot = np.array([fa, lift, fc])
        knee, wr = _ik(hip, foot, pa['L1'], pa['L2'], (0, 1.0, lado * .55))
        r = pa['r']
        _seg(S, n + '_f', hip, knee, r * 1.2, r * 1.2, 'pata', 1.1, spec=.55, rim=.4)
        _seg(S, n + '_t', knee, wr, r * .9, r * .8, 'pata', 1.1, spec=.55, rim=.4, bias=.2)
        S.garra(np.array([wr, wr + np.array([.12, -.05, 0]) * (1 if True else 0) + np.array([0, -.0, 0]), wr + np.array([.22, -.10, 0])]), .09, 'antena', w1=.03)
        for j in range(pa['spine']):
            tt = .35 + .3 * j
            pbase = knee * (1 - tt) + wr * tt
            S.garra(np.array([pbase, pbase + np.array([.1, .22, lado * .2]), pbase + np.array([.12, .38, lado * .3])]), .07, 'antena', w1=.02)
    return S
