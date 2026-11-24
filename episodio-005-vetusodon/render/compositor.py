#!/usr/bin/env python3
"""Compositor rápido 2D por capas con parallax (sin motor pesado).

Cada escena se ARMA UNA SOLA VEZ (cielo, montañas, suelo y vegetación como capas RGBA premultiplicadas más grandes que la
pantalla) y por cuadro solo se hacen warps afines/remap baratos (cv2), con:
  parallax por profundidad · cámara (empuje, paneo, grúa, órbita, handheld) · viento (remap con mapa de rigidez) ·
  partículas · bruma en 2 planos · rayos de luz · sombras de contacto · animales/mascota · gradación MONOCROMÁTICA
  (un solo color dominante por escena) · bloom · viñeta · grano · subtítulos · fundidos.

API:
    es = Escena(dict_escena, fps=24)          # arma capas
    bgr = es.frame(i)                         # np.uint8 (1080,1920,3) BGR
    es.n_frames
"""
import math
import os
import pickle
import sys
import zlib
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

cv2.setNumThreads(1)
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "biblioteca"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paletas  # noqa: E402
import plantas  # noqa: E402
import terreno  # noqa: E402
import variar  # noqa: E402

W, H, FPS = 1920, 1080, 24
HOR = int(H * .52)                               # horizonte
CX0, CY0 = W / 2, H * .58                        # centro de zoom
CACHE = RAIZ / "video" / "cache"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ALTO_REF = 300                                   # alto (px a 1080p) de un animal con escala=1

# profundidad de cada capa: (p = parallax del paneo, k = exponente de zoom, c = factor de grúa)
PROF = dict(cielo=(.04, .12, .05), montanas=(.10, .22, .10), fondo=(.30, .45, .30), medio=(.60, .75, .60),
            actores=(.80, .90, .80), cerca=(1.0, 1.0, 1.0), primer=(1.9, 1.7, 1.9))
SUELO_BAJO = {'musgo', 'liquen', 'hongos', 'piedra', 'roca_musgosa', 'tronco_caido', 'mata_seca', 'suculenta', 'welwitschia'}
PEQUENAS = {'helecho_suelo', 'roca_musgosa', 'mata_seca', 'welwitschia', 'suculenta', 'musgo', 'liquen', 'hongos',
            'piedra', 'tronco_caido'}
RIGIDEZ = {'roca_musgosa': 0, 'piedra': 0, 'tronco_caido': 0, 'musgo': .05, 'liquen': .05, 'hongos': .15,
           'lepidodendron': .35, 'sigillaria': .35, 'prototaxites': .2, 'welwitschia': .5, 'suculenta': .4}
SUELO_TIPO = {'ocre': 'arena', 'rojo': 'arcilla', 'ambar': 'arcilla', 'verde': 'barro', 'azul': 'lecho',
              'violeta': 'barro', 'ceniza': 'lecho'}


# ------------------------------------------------------------------------------------------ utilidades
def bgr(c):
    return (float(c[2]), float(c[1]), float(c[0]))


def mix(a, b, t):
    return tuple(a[i] * (1 - t) + b[i] * t for i in range(3))


def ease(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def pm_desde_pil(im):
    """PIL RGBA recto -> ndarray BGRA premultiplicado uint8."""
    a = np.asarray(im.convert('RGBA'), np.float32)
    al = a[..., 3] / 255.0
    out = np.dstack([a[..., 2] * al, a[..., 1] * al, a[..., 0] * al, a[..., 3]])
    return np.ascontiguousarray(np.clip(out + .5, 0, 255).astype(np.uint8))


def pegar_pm(dst, spr, x0, y0):
    """Compone premult BGRA `spr` sobre premult BGRA `dst` en (x0,y0) (recorta). Devuelve ROI usada o None."""
    h, w = spr.shape[:2]
    sx0, sy0 = max(0, -x0), max(0, -y0)
    sx1, sy1 = min(w, dst.shape[1] - x0), min(h, dst.shape[0] - y0)
    if sx1 <= sx0 or sy1 <= sy0:
        return None
    s = spr[sy0:sy1, sx0:sx1]
    r = dst[y0 + sy0:y0 + sy1, x0 + sx0:x0 + sx1]
    inv = (255 - s[..., 3:4]).astype(np.uint16)
    r[:] = np.minimum(255, s.astype(np.uint16) + (r.astype(np.uint16) * inv + 127) // 255).astype(np.uint8)
    return (x0 + sx0, y0 + sy0, x0 + sx1, y0 + sy1)


def over(dst, src4, y0=0):
    """dst (BGR uint8) <- src4 premult BGRA (ROI desde la fila y0)."""
    h = src4.shape[0]
    r = dst[y0:y0 + h]
    bg = np.empty(r.shape, np.uint8)
    a3 = np.empty(r.shape, np.uint8)
    cv2.mixChannels([src4], [bg], [0, 0, 1, 1, 2, 2])
    cv2.mixChannels([src4], [a3], [3, 0, 3, 1, 3, 2])
    cv2.bitwise_not(a3, a3)
    cv2.multiply(r, a3, dst=r, scale=1 / 255.)
    cv2.add(r, bg, dst=r)


def seed_de(txt):
    return zlib.crc32(str(txt).encode()) & 0x7fffffff


# ------------------------------------------------------------------------------------------ plantas (caché en disco)
def planta_cache(nom, pal, nvar=3, h=460):
    f = CACHE / f"pl_{pal['nombre'].replace('+', '_')}_{nom}_{nvar}_{h}.pkl"
    try:
        with open(f, 'rb') as fh:
            return pickle.load(fh)
    except Exception:
        pass
    lst = [plantas.generar(nom, 1000 + i * 13 + len(nom), h, pal) for i in range(nvar)]
    try:
        CACHE.mkdir(parents=True, exist_ok=True)
        tmp = f.with_suffix(f".{os.getpid()}.tmp")
        with open(tmp, 'wb') as fh:
            pickle.dump(lst, fh)
        os.replace(tmp, f)
    except Exception:
        pass
    return lst


def ruido_periodico(h, w, escalas, rg):
    """fbm periódico (FFT) en x e y, normalizado 0..1."""
    out = np.zeros((h, w), np.float32)
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    r = np.sqrt(fx ** 2 + fy ** 2) + 1e-6
    for sc, amp in escalas:
        filt = np.exp(-(r * sc) ** 2 * 6)
        n = np.fft.ifft2(np.fft.fft2(rg.normal(size=(h, w))) * filt).real
        out += amp * (n / (n.std() + 1e-6))
    out = (out - out.min()) / (out.max() - out.min() + 1e-6)
    return out.astype(np.float32)


# ------------------------------------------------------------------------------------------ Escena
class Escena:
    def __init__(self, esc, fps=FPS):
        self.e = esc
        self.fps = fps
        self.dur = float(esc['dur'])
        self.n_frames = int(round(self.dur * fps))
        self.pal = paletas.obtener(esc['paleta'])
        self.seed = seed_de(esc.get('id', '0')) % 100000
        self.rg = np.random.default_rng(self.seed)
        self.clima = esc.get('clima') or {}
        self.sol_x = float(self.rg.uniform(.22, .78))
        self._camara()
        self._grad()
        self.capas = {}
        self._construir_capas()
        self._niebla()
        self._rayos()
        self._particulas()
        self._vineta()
        self._actores()
        self._subtitulos()
        self._cartel()

    # ---------------------------------------------------------------------------- cámara
    def _camara(self):
        c = dict(self.e.get('camara') or {})
        tipo = c.get('tipo', 'quieta')
        a = c.get('amplitud')
        self.zoom_amp = float(c.get('zoom', 0.0))
        self.pan_amp = 0.0
        self.grua_amp = float(c.get('grua', 0.0))
        self.orb_amp = float(c.get('orbita', 0.0))
        # `amplitud`: fracción (<=3): empuje = zoom (0.3 -> +18 %), paneo = fracción del ancho en el plano de referencia
        # (0.4 -> 460 px), grúa = fracción del alto (0.4 -> 260 px). Si es > 3 se toma como píxeles.
        if tipo == 'empuje':
            self.zoom_amp += (.10 if a is None else (min(abs(a), .5) * .6 * (1 if a >= 0 else -1) if abs(a) <= 3 else a / W))
        elif tipo in ('paneo_izq', 'paneo_der'):
            px = 240 if a is None else (abs(a) * W * .6 if abs(a) <= 3 else abs(a))
            self.pan_amp = float(px) * (1 if tipo == 'paneo_der' else -1)
        elif tipo == 'grua':
            self.grua_amp += 130 if a is None else (abs(a) * H * .65 if abs(a) <= 3 else abs(a))
        self.hand = float(c.get('handheld', .6))
        self.curva = c.get('curva', 'suave')
        self.hh_fase = np.random.default_rng(self.seed + 7).uniform(0, 6.28, (6,))
        self.vel_viento = float(self.clima.get('viento', .5))

    def _cam_t(self, t):
        u = t / max(self.dur, 1e-6)
        u = ease(u) if self.curva == 'suave' else min(1.0, max(0.0, u))
        z = 1 + u * self.zoom_amp if self.zoom_amp >= 0 else 1 + (1 - u) * -self.zoom_amp
        f = self.hh_fase
        hx = self.hand * (1.7 * math.sin(.73 * t + f[0]) + .9 * math.sin(1.91 * t + f[1]) + .45 * math.sin(4.3 * t + f[2]))
        hy = self.hand * (1.3 * math.sin(.61 * t + f[3]) + .7 * math.sin(2.13 * t + f[4]) + .35 * math.sin(5.1 * t + f[5]))
        return dict(z=z, pan=(u - .5) * self.pan_amp, grua=(u - .5) * self.grua_amp, orb=(u - .5) * self.orb_amp,
                    hx=hx, hy=hy)

    def _trans(self, capa, cm):
        """(s, tx, ty) de la capa por nombre de profundidad."""
        p, k, c = PROF[capa]
        s = 1 + (cm['z'] - 1) * k
        tx = -cm['pan'] * p - cm['orb'] * (p - .75) + cm['hx'] * (.3 + .7 * p)
        ty = -cm['grua'] * c + cm['hy'] * (.3 + .7 * p)
        return s, tx, ty

    def _margenes(self, capa):
        p, k, c = PROF[capa]
        mx = abs(self.pan_amp) / 2 * p + abs(self.orb_amp) / 2 * abs(p - .75) + (4.5 * self.hand + 2) * (.3 + .7 * p) + 14
        my = abs(self.grua_amp) / 2 * c + (3.0 * self.hand + 2) * (.3 + .7 * p) + 14
        if capa == 'cielo':
            mx += 2 * self.dur + 20
        return int(math.ceil(mx)), int(math.ceil(my))

    # ---------------------------------------------------------------------------- gradación
    def _grad(self):
        pal = self.pal
        g = self.e.get('gradacion') or {}
        dom = np.array(bgr(pal['dom']), np.float32)
        luz = np.array(bgr(pal['luz']), np.float32)
        som = np.array(bgr(pal['sombra']), np.float32)
        self.k_tono = float(g.get('tono', .6))
        x = np.linspace(0, 1, 256, dtype=np.float32)[:, None]
        dom_m = dom / max(dom.max(), 1) * 225
        lo = som * .2
        mi = dom_m * .66
        hi = np.clip(luz * .55 + dom_m * .45 + 30, 0, 255)
        sat = float(g.get('saturacion', .68))
        def _des(c):
            L = c[0] * .114 + c[1] * .587 + c[2] * .299
            return L + (c - L) * sat
        lo, mi, hi = _des(lo), _des(mi), _des(hi)
        ex = np.where(x < .5, lo + (mi - lo) * np.clip(x / .5, 0, 1) ** .9, mi + (hi - mi) * np.clip((x - .5) / .5, 0, 1) ** 1.2)
        self.lut_tri = np.clip(ex, 0, 255).astype(np.uint8).reshape(256, 1, 3)
        s = x[:, 0]
        c = float(g.get('contraste', 1.25))
        kk = 4.4 * c
        sg = 1 / (1 + np.exp(-kk * (s - .5)))
        cur = 255 * (sg - sg[0]) / (sg[-1] - sg[0]) * float(g.get('brillo', 1.0))
        self.lut_cur = np.clip(cur, 0, 255).astype(np.uint8).reshape(256, 1, 1).repeat(3, 2)
        self.luz_bgr = np.array(bgr(mix(pal['luz'], pal['bruma'], .35)), np.float32)

    def _gradar(self, f):
        a = cv2.LUT(f, self.lut_cur)
        g = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
        tri = cv2.LUT(cv2.cvtColor(g, cv2.COLOR_GRAY2BGR), self.lut_tri)
        return cv2.addWeighted(a, 1 - self.k_tono, tri, self.k_tono, 0)

    # ---------------------------------------------------------------------------- capas
    def _lienzo(self, capa):
        mx, my = self._margenes(capa)
        return mx, my, np.zeros((H + 2 * my, W + 2 * mx, 4), np.uint8)

    def _construir_capas(self):
        pal, seed = self.pal, self.seed
        dom_nombre = pal['nombre'].split('+')[0]
        tipo = self.e.get('suelo') or SUELO_TIPO.get(dom_nombre, 'arcilla')
        # cielo
        mx, my = self._margenes('cielo')
        wc, hc = W + 2 * mx, HOR + 70 + my
        cie = terreno.cielo(wc, hc, pal, seed, sol_x=(self.sol_x * W + mx) / wc)
        self.capas['cielo'] = dict(img=np.ascontiguousarray(np.asarray(cie.convert('RGB'))[..., ::-1]), mx=mx, my=my, opaca=True)
        # montañas
        mx, my, can = self._lienzo('montanas')
        mont = terreno.montanas(W + 2 * mx, int(H * .45), pal, seed + 1, 3)
        pegar_pm(can, pm_desde_pil(mont), 0, HOR - int(H * .36) + my)
        self._capa('montanas', can, mx, my)
        # flora por capa
        por_capa = self._flora_efectiva(tipo)
        usadas = {f['especie'] for l in por_capa.values() for f in l if f['especie'] in plantas.ESPECIES}
        self.lib = {n: planta_cache(n, pal) for n in usadas}
        # fondo
        mx, my, can = self._lienzo('fondo')
        wmap = np.zeros(can.shape[:2], np.uint8)
        pegar_pm(can, pm_desde_pil(terreno.suelo(W + 2 * mx, int(H * .2), pal, seed + 2, tipo, piedras=10)), 0, HOR - 6 + my)
        self._plantar(can, wmap, my, mx, por_capa['fondo'], 'fondo')
        self._capa('fondo', can, mx, my, wmap, amp=2.2)
        # medio
        mx, my, can = self._lienzo('medio')
        wmap = np.zeros(can.shape[:2], np.uint8)
        pegar_pm(can, pm_desde_pil(terreno.suelo(W + 2 * mx, int(H * .26), pal, seed + 3, tipo, piedras=14)), 0, int(H * .64) + my)
        if tipo == 'lecho':
            pegar_pm(can, pm_desde_pil(terreno.rio(W + 2 * mx, int(H * .1), pal, seed + 5)), 0, int(H * .6) + my)
        self._plantar(can, wmap, my, mx, por_capa['medio'], 'medio')
        self._capa('medio', can, mx, my, wmap, amp=4.5)
        # cerca
        mx, my, can = self._lienzo('cerca')
        wmap = np.zeros(can.shape[:2], np.uint8)
        h_suelo = H + my - int(H * .80) + 20
        pegar_pm(can, pm_desde_pil(terreno.suelo(W + 2 * mx, h_suelo, pal, seed + 4, tipo, piedras=16)), 0, int(H * .80) + my)
        self._plantar(can, wmap, my, mx, por_capa['cerca'], 'cerca')
        self._capa('cerca', can, mx, my, wmap, amp=8)
        # primer plano
        mx, my, can = self._lienzo('primer')
        wmap = np.zeros(can.shape[:2], np.uint8)
        self._plantar(can, wmap, my, mx, por_capa['primer_plano'], 'primer')
        self._capa('primer', can, mx, my, wmap, amp=14)

    def _flora_efectiva(self, tipo):
        """Las listas de flora del guion son énfasis: cada capa se completa con especies por defecto para que sea densa."""
        arido = tipo == 'arena' or self.pal['nombre'].split('+')[0] in ('ocre',)
        defecto = dict(
            fondo=['mata_seca', 'welwitschia', 'dicroidium', 'cicada'] if arido else ['glossopteris', 'cordaites', 'calamites', 'equisetum'],
            medio=['mata_seca', 'suculenta', 'welwitschia', 'cicada', 'prototaxites'] if arido else ['glossopteris', 'equisetum', 'dicroidium', 'psaronius', 'calamites', 'cordaites'],
            cerca=['piedra', 'mata_seca', 'roca_musgosa', 'suculenta'] if arido else ['helecho_suelo', 'musgo', 'hongos', 'liquen', 'piedra'],
            primer_plano=['mata_seca', 'helecho_suelo'] if arido else ['helecho_suelo', 'equisetum', 'cyathea'])
        minimo = dict(fondo=4, medio=5, cerca=4, primer_plano=2)
        out = {c: [] for c in defecto}
        for f in self.e.get('flora') or []:
            if f['especie'] in plantas.ESPECIES:
                out.setdefault(f.get('capa', 'medio'), []).append(dict(f, densidad=max(.5, float(f.get('densidad', .5)))))
        for c, lst in out.items():
            have = {f['especie'] for f in lst}
            for n in defecto.get(c, []):
                if len(have) >= minimo.get(c, 3):
                    break
                if n not in have:
                    lst.append(dict(especie=n, densidad=.45, capa=c))
                    have.add(n)
        return out

    def _capa(self, nombre, can, mx, my, wmap=None, amp=0.0):
        filas = np.where(can[..., 3].max(1) > 2)[0]
        v0, v1 = (int(filas[0]), int(filas[-1]) + 1) if len(filas) else (0, 0)
        self.capas[nombre] = dict(img=can, mx=mx, my=my, wmap=wmap, amp=amp * (.4 + 1.2 * self.vel_viento),
                                  v0=v0, v1=v1, opaca=False)

    def _plantar(self, can, wmap, my, mx, entradas, capa):
        if not entradas:
            return
        pal, rg = self.pal, self.rg
        wc = can.shape[1]
        escala_w = wc / W
        base = dict(fondo=250, medio=230, cerca=170, primer=5)[capa]
        cfg = dict(fondo=dict(bruma=.58, tinte=.35, brillo=1.0, blur=0), medio=dict(bruma=.28, tinte=.28, brillo=1.0, blur=0),
                   cerca=dict(bruma=0.0, tinte=.2, brillo=.9, blur=0),
                   primer=dict(bruma=0.0, tinte=.15, brillo=.55, blur=6.0))[capa]
        ok = [f for f in entradas if f['especie'] in self.lib and not (capa == 'primer' and f['especie'] in SUELO_BAJO)]
        if not ok:
            return
        dens = np.array([max(.01, float(f.get('densidad', .5))) for f in ok])
        esp = [f['especie'] for f in ok]
        total = int(base * escala_w * float(dens.mean()) * (1.0 + .15 * len(set(esp)) ** .5))
        if capa == 'primer':
            total = max(3, int(2 + 4 * float(dens.mean())))
        prob = dens / dens.sum()
        pool = {}
        for n in set(esp):
            lst = []
            for i in range(5):
                b = self.lib[n][i % len(self.lib[n])]
                im = variar.variante(b, rg, pal, cfg['tinte'], True, curv=.18, matiz_g=6)
                if cfg['bruma']:
                    im = variar.bruma(im, pal['bruma'], cfg['bruma'], .85 - cfg['bruma'] * .3, .9 - cfg['bruma'] * .5)
                if cfg['brillo'] != 1.0:
                    im = variar.brillo(im, cfg['brillo'])
                if cfg['blur']:
                    im = variar.desenfoque(im, cfg['blur'])
                lst.append(pm_desde_pil(im))
            pool[n] = lst
        corr = []
        for a in (self.e.get('animales') or []):
            if a.get('especie') in ('libelula', 'cucaracha', 'escarabajo'):
                continue
            lo, hi = sorted((float(a.get('x0', .3)), float(a.get('x1', .7))))
            corr.append((lo - .13, hi + .13))
        if self.e.get('mascota'):
            m = self.e['mascota']
            lo, hi = sorted((float(m.get('x0', m.get('x', .5))), float(m.get('x1', m.get('x', .5)))))
            corr.append((lo - .1, hi + .1))
        ncl = max(3, int(12 * escala_w))
        cen = rg.uniform(-60, wc + 60, ncl)
        puestos = []
        for _ in range(total):
            if capa == 'fondo':
                yb = rg.uniform(HOR + 8, HOR + 70)
            elif capa == 'medio':
                yb = rg.uniform(H * .68, H * .86)
            elif capa == 'cerca':
                yb = rg.uniform(H * .86, H + 20)
            else:
                yb = H + rg.uniform(10, 120)
            x = rg.choice(cen) + rg.normal(0, 110) if rg.random() < .55 else rg.uniform(-40, wc + 40)
            if capa == 'primer':
                for _ in range(10):
                    if .20 * W < x - mx < .80 * W:
                        x = rg.uniform(-40, wc + 40)
                    else:
                        break
            puestos.append((yb, x, int(rg.choice(len(esp), p=prob))))
        puestos.sort()
        sombras = {}
        for yb, x, ie in puestos:
            n = esp[ie]
            b = pool[n][int(rg.integers(0, len(pool[n])))]
            if capa == 'fondo':
                alto = rg.uniform(50, 130) * (yb / HOR)
            elif capa == 'medio':
                alto = rg.uniform(110, 300) * (.55 + (yb - H * .6) / (H * .4))
            elif capa == 'cerca':
                alto = rg.uniform(60, 170) * (.8 + (yb - H * .84) / (H * .2) * 1.1)
            else:
                alto = rg.uniform(300, 520)
            if n in PEQUENAS:
                alto *= .45 if capa in ('fondo', 'medio') else (.7 if n == 'tronco_caido' else .8)
            xf_ = (x - mx) / W
            if corr and any(lo <= xf_ <= hi for lo, hi in corr):
                if (capa == 'medio' and yb > H * .76 and rg.random() < .85) or (capa == 'cerca' and alto > 100 and rg.random() < .9):
                    continue
            k = alto / b.shape[0]
            nw, nh = max(2, int(b.shape[1] * k * rg.uniform(.9, 1.1))), max(2, int(b.shape[0] * k))
            spr = cv2.resize(b, (nw, nh), interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_LINEAR)
            if rg.random() < .5:
                spr = np.ascontiguousarray(spr[:, ::-1])
            x0, y0 = int(round(x - nw / 2)), int(round(yb + my - nh))
            if capa in ('medio', 'cerca'):
                aw = int(nw * .8 // 8 * 8) + 8
                if aw not in sombras:
                    sombras[aw] = pm_desde_pil(variar.sombra_contacto(aw, pal, None, .5))
                sh = sombras[aw]
                pegar_pm(can, sh, int(round(x - sh.shape[1] / 2)), int(round(yb + my - sh.shape[0] / 2)))
            roi = pegar_pm(can, spr, x0, y0)
            rig = RIGIDEZ.get(n, 1.0)
            if roi is not None and rig > 0:
                rx0, ry0, rx1, ry1 = roi
                yy = np.arange(ry0, ry1, dtype=np.float32)[:, None]
                wgt = np.clip((yb + my - yy) / max(nh, 1), 0, 1) ** 1.3 * 255 * rig
                m = (spr[ry0 - y0:ry1 - y0, rx0 - x0:rx1 - x0, 3] > 10) * wgt
                sub = wmap[ry0:ry1, rx0:rx1]
                np.maximum(sub, m.astype(np.uint8), out=sub)

    # ---------------------------------------------------------------------------- niebla, rayos, viñeta
    def _niebla(self):
        rg = np.random.default_rng(self.seed + 11)
        b = float(self.clima.get('bruma', .3))
        self.bruma = b
        col = np.array(bgr(self.pal['bruma']), np.float32)
        self.nieblas = []
        for nombre, (hh, ww, sc, dens) in dict(
                lejana=(135, 240, [(60, 1), (22, .5), (9, .25)], .85),
                cercana=(135, 240, [(70, 1), (30, .6), (12, .3)], .6)).items():
            n = ruido_periodico(hh, ww, sc, rg)
            n = np.clip((n - .30) * 1.9, 0, 1)
            y = np.linspace(0, 1, hh, dtype=np.float32)[:, None]
            if nombre == 'lejana':
                perfil = np.exp(-((y - .56) / .17) ** 2) * np.clip((y - .22) / .12, 0, 1)
            else:
                perfil = np.clip((y - .50) / .22, 0, 1) ** 1.3 * np.clip((1.02 - y) / .1 + .35, 0, 1)
            al = np.clip(n * perfil * dens * (.25 + 1.5 * b), 0, .92)
            tex = np.dstack([al[..., None] * col, al * 255]).astype(np.uint8)
            self.nieblas.append(dict(tex=np.ascontiguousarray(tex), vel=5.0 if nombre == 'lejana' else 11.0))

    def _rayos(self):
        self.rayos = float(self.clima.get('rayos', .3))
        self.ray_tex = None
        if self.rayos <= 0.01:
            return
        rg = np.random.default_rng(self.seed + 13)
        h, w = 270, 480
        tex = []
        for v in range(2):
            m = np.zeros((h, w), np.float32)
            sx = self.sol_x * w
            for _ in range(9):
                ang = rg.uniform(-.55, .55) + (.5 - self.sol_x) * .3
                ancho = rg.uniform(14, 52)
                x_top = sx + rg.uniform(-40, 40)
                x_bot = x_top + math.tan(ang) * h * 1.3
                pts = np.array([[x_top - 2, 0], [x_top + 2, 0], [x_bot + ancho, h], [x_bot - ancho, h]], np.int32)
                tmp = np.zeros((h, w), np.float32)
                cv2.fillPoly(tmp, [pts], float(rg.uniform(.35, 1.0)))
                m += tmp
            m = cv2.GaussianBlur(m, (0, 0), 5.5)
            n = ruido_periodico(h, w, [(26, 1), (8, .5)], rg)
            m = m * (.45 + .9 * n) * np.linspace(1.0, .12, h)[:, None]
            tex.append(np.clip(m / max(m.max(), 1e-3), 0, 1).astype(np.float32))
        self.ray_tex = [(t * 255).astype(np.uint8) for t in tex]

    def _vineta(self):
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        v = 1 - .55 * np.clip(((xx - W / 2) / (W / 2)) ** 2 * .75 + ((yy - H * .48) / (H / 2)) ** 2 * .85, 0, 1.2) ** 1.25
        v = v * (1 - .38 * np.clip((yy - H * .62) / (H * .38), 0, 1) ** 1.6)
        self.vig = np.ascontiguousarray(np.repeat(np.clip(v * 255, 0, 255).astype(np.uint8)[..., None], 3, 2))

    # ---------------------------------------------------------------------------- partículas
    def _particulas(self):
        tipo = self.clima.get('particulas')
        self.part_tipo = tipo
        if not tipo:
            return
        rg = np.random.default_rng(self.seed + 17)
        n = dict(polvo=240, polen=140, ceniza=180, nieve=300, lluvia=420).get(tipo, 160)
        n = int(n * float(self.clima.get('densidad_part', 1.0)))
        self.pp = dict(x=rg.uniform(0, 1, n), y=rg.uniform(0, 1, n), d=rg.uniform(0, 1, n) ** .7, ph=rg.uniform(0, 6.28, n),
                       sz=rg.uniform(.6, 1.0, n), vx=rg.normal(0, 1, n))
        self.part_col = np.array(bgr(mix(self.pal['luz'], self.pal['bruma'], .35)), np.float32)
        self.spr_pt = []
        for r in [1.6, 2.4, 3.4, 5, 7.5, 11, 16]:
            s = int(r * 4) | 1
            yy, xx = np.mgrid[:s, :s].astype(np.float32) - s // 2
            g = np.exp(-(xx ** 2 + yy ** 2) / (2 * (r * .55) ** 2))
            core = np.clip(1 - np.sqrt(xx ** 2 + yy ** 2) / r, 0, 1)
            self.spr_pt.append(g * .6 + core * .4)
        self.dark = tipo == 'ceniza'

    def _dibujar_particulas(self, f, t, cm, desde, hasta):
        if not self.part_tipo:
            return
        pp, tipo, d = self.pp, self.part_tipo, self.pp['d']
        idx = np.where((d >= desde) & (d < hasta))[0]
        if not len(idx):
            return
        ov = np.zeros((H, W, 3), np.uint8)
        ovd = None
        for i in idx:
            di = d[i]
            par = .3 + 1.5 * di
            if tipo == 'lluvia':
                vy, vx = 1900 + 900 * di, -260 - 140 * di
                x = (pp['x'][i] * (W + 600) + vx * t - cm['pan'] * par) % (W + 600) - 300
                y = (pp['y'][i] * (H + 400) + vy * t) % (H + 400) - 200
                L = 30 + 60 * di
                col = tuple(float(c) for c in self.part_col * (70 + 110 * di) / 255)
                cv2.line(ov, (int(x), int(y)), (int(x + vx / vy * L), int(y + L)), col, 1 if di < .6 else 2, cv2.LINE_AA)
                continue
            if tipo == 'nieve':
                vy, vx = 40 + 90 * di, 15 * pp['vx'][i]
            elif tipo == 'ceniza':
                vy, vx = 26 + 50 * di, 20 * pp['vx'][i] - 18
            elif tipo == 'polen':
                vy, vx = -6 - 8 * di, 10 * pp['vx'][i] + 8
            else:
                vy, vx = -3 + 10 * di, 14 * pp['vx'][i] + 10
            wob = math.sin(t * (.6 + pp['sz'][i]) + pp['ph'][i]) * (10 + 25 * di)
            x = (pp['x'][i] * (W + 400) + vx * t + wob - cm['pan'] * par) % (W + 400) - 200
            y = (pp['y'][i] * (H + 300) + vy * t + cm['grua'] * par) % (H + 300) - 150
            spr = self.spr_pt[min(len(self.spr_pt) - 1, int((.15 + .85 * di * pp['sz'][i]) * len(self.spr_pt)))]
            if tipo == 'polen':
                br = (.25 + .75 * di ** .6) * (.55 + .45 * math.sin(t * 1.3 + pp['ph'][i]))
            else:
                br = (.3 + .6 * di ** .5) * (.55 if di > .75 else 1.0)
            s = spr.shape[0]
            x0, y0 = int(x) - s // 2, int(y) - s // 2
            if x0 < 0 or y0 < 0 or x0 + s > W or y0 + s > H:
                continue
            target, colv = ov, self.part_col
            if self.dark and (i % 3):
                if ovd is None:
                    ovd = np.zeros((H, W, 3), np.uint8)
                target, colv = ovd, np.array([60, 60, 60], np.float32)
            patch = (spr[..., None] * colv * br).astype(np.uint8)
            roi = target[y0:y0 + s, x0:x0 + s]
            cv2.add(roi, patch, dst=roi)
        cv2.add(f, ov, dst=f)
        if ovd is not None:
            cv2.subtract(f, ovd, dst=f)

    # ---------------------------------------------------------------------------- actores
    def _actores(self):
        self.actores = []
        pal = self.pal
        try:
            import animales
        except Exception:
            animales = None
        for a in self.e.get('animales') or []:
            ciclo, avance = None, None
            try:
                if animales is not None:
                    ciclo = animales.ciclo(a['especie'], a.get('accion', 'idle'), a.get('vista', '3q_der'), pal, a.get('n', 8))
                    try:
                        avance = float(animales.avance_px(a['especie'], a.get('accion', 'idle'), a.get('vista', '3q_der'))[0])
                    except Exception:
                        avance = None
            except Exception as ex:
                print("aviso: animal", a.get('especie'), "->", repr(ex)[:100], "(uso stub)", file=sys.stderr)
            if not ciclo:
                ciclo = _ciclo_stub(a['especie'], pal, a.get('n', 8))
            self.actores.append(self._preparar_sprites(a, ciclo, avance))
        self.mascota = None
        m = self.e.get('mascota')
        if m:
            try:
                self.mascota = self._preparar_mascota(m)
            except Exception as ex:
                print("aviso: mascota ->", repr(ex)[:120], file=sys.stderr)
        self.owen = None
        o = self.e.get('owen')
        if o:
            try:
                self.owen = self._preparar_owen(o)
            except Exception as ex:
                print("aviso: owen ->", repr(ex)[:120], file=sys.stderr)

    def _preparar_sprites(self, a, ciclo, avance=None):
        pal = self.pal
        pms = [np.asarray(s.convert('RGBA')) for s in ciclo]
        ys = [np.where(p[..., 3].max(1) > 8)[0] for p in pms]
        xs = [np.where(p[..., 3].max(0) > 8)[0] for p in pms]
        y0, y1 = min(v[0] for v in ys if len(v)), max(v[-1] for v in ys if len(v)) + 1
        x0, x1 = min(v[0] for v in xs if len(v)), max(v[-1] for v in xs if len(v)) + 1
        y_frac = float(a.get('y', .82))
        persp = max(.35, (y_frac * H - HOR) / (.82 * H - HOR))
        k = float(a.get('escala', 1.0)) * persp * (.40 if 'alto_px' not in a else float(a['alto_px']) / (y1 - y0))
        anc = ciclo[0].info.get('ancla') if hasattr(ciclo[0], 'info') else None
        anc = (anc[0] - x0, anc[1] - y0) if anc else ((x1 - x0) / 2, (y1 - y0) * .96)
        out = []
        for s in ciclo:
            im = s.convert('RGBA').crop((x0, y0, x1, y1))
            im = im.resize((max(2, int(im.width * k)), max(2, int(im.height * k))), Image.LANCZOS)
            im = variar.tinte(im, pal['dom'], float(a.get('tinte', .3)))
            im = variar.bruma(im, pal['bruma'], .08 + .25 * (1 - min(1.0, persp)), .95, .9)
            out.append(pm_desde_pil(im))
        return dict(a=a, spr=out, y=y_frac, k=k, ancla=(anc[0] * k, anc[1] * k),
                    paso=(avance * k * 400 / 400.0) if avance else None,
                    t0=float(a.get('t0', 0)), t1=float(a.get('t1', self.dur)),
                    x0=float(a.get('x0', .3)), x1=float(a.get('x1', .7)))

    def _preparar_owen(self, o):
        import owen as OW
        expr = o.get('expresion', 'neutral')
        pose = 'busto_anotando' if expr == 'anotando' else 'busto'
        n = 8
        sprs = []
        for i in range(n):
            im = OW.owen(expr, pose, i / n, self.pal, 560)
            im = variar.tinte(im, self.pal['dom'], .32)
            sprs.append(pm_desde_pil(im))
        mx = [m.get('x', .5) for m in [self.e.get('mascota') or {}]]
        lado = 'der' if (self.e.get('mascota') and float(self.e['mascota'].get('x', .5)) < .5) else 'izq'
        burbuja = _burbuja(o.get('frase', ''), self.pal)
        return dict(spr=sprs, sprf=[np.ascontiguousarray(x[:, ::-1]) for x in sprs], lado=lado, burbuja=pm_desde_pil(burbuja),
                    t0=float(o.get('t0', 0)), t1=float(o.get('t1', self.dur)))

    def _preparar_mascota(self, m):
        import mascota as MA
        M = MA.Mascota()
        accion = m.get('accion', 'camina')
        esc = float(m.get('escala', 1.0)) * .30
        if accion in ('camina', 'caminar', 'pasea'):
            poses = [dict(leg=i / 8, bob=-8 * math.sin(i / 8 * 2 * math.pi * 2) ** 2) for i in range(8)]
        elif accion == 'olfatea':
            poses = [dict(tilt=4, look=(.8, .9), bob=b) for b in (10, 14, 10, 6)]
        elif accion == 'salta':
            poses = [dict(tilt=-6, bob=-120, spread=1, look=(0, -1))]
        elif accion == 'enojado':
            poses = [dict(mad=1, tilt=2)]
        elif accion in ('espaldas', 'de_espaldas'):
            poses = [dict(flip=True, spread=1, blink=.6)]
        else:
            poses = [dict(tilt=-3, look=(.6, .2)), dict(tilt=-3, look=(.6, .2), blink=1)]
        sprs = []
        for pz in poses:
            im = M.frame(pz)
            im = im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS)
            im = variar.tinte(im, self.pal['dom'], .12)
            sprs.append(pm_desde_pil(im))
        return dict(m=m, spr=sprs, sprf=[np.ascontiguousarray(s[:, ::-1]) for s in sprs], accion=accion,
                    t0=float(m.get('t0', 0)), t1=float(m.get('t1', self.dur)),
                    x0=float(m.get('x0', m.get('x', .5))), x1=float(m.get('x1', m.get('x', .5))),
                    y=float(m.get('y', .86)), ancla=(760 * esc, 1000 * esc))

    def _sombra(self, ancho):
        key = int(max(8, ancho) // 6)
        if not hasattr(self, '_sh'):
            self._sh = {}
        if key not in self._sh:
            self._sh[key] = pm_desde_pil(variar.sombra_contacto(key * 6, self.pal, None, .75))
        return self._sh[key]

    @staticmethod
    def _over_roi(r, s):
        bgc = np.ascontiguousarray(s[..., :3])
        a3 = cv2.cvtColor(np.ascontiguousarray(255 - s[..., 3]), cv2.COLOR_GRAY2BGR)
        cv2.multiply(r, a3, dst=r, scale=1 / 255.)
        cv2.add(r, bgc, dst=r)

    def _blit(self, f, spr, xc, yb, alpha=1.0):
        h, w = spr.shape[:2]
        x0, y0 = int(round(xc - w / 2)), int(round(yb - h))
        sx0, sy0 = max(0, -x0), max(0, -y0)
        sx1, sy1 = min(w, W - x0), min(h, H - y0)
        if sx1 <= sx0 or sy1 <= sy0:
            return
        s = spr[sy0:sy1, sx0:sx1]
        if alpha < 1:
            s = (s.astype(np.float32) * alpha).astype(np.uint8)
        self._over_roi(f[y0 + sy0:y0 + sy1, x0 + sx0:x0 + sx1], s)

    def _dibujar_actores(self, f, t, cm):
        s, tx, ty = self._trans('actores', cm)
        for ac in self.actores:
            if not (ac['t0'] - .3 <= t <= ac['t1'] + .3):
                continue
            u = min(1.0, max(0.0, (t - ac['t0']) / max(ac['t1'] - ac['t0'], 1e-6)))
            xf = ac['x0'] + (ac['x1'] - ac['x0']) * u
            n = len(ac['spr'])
            mueve = abs(ac['x1'] - ac['x0']) > 1e-4
            if mueve and ac['paso']:
                ix = int(((abs(ac['x1'] - ac['x0']) * W * u) / ac['paso']) % 1.0 * n) % n
            else:
                ix = int(((t - ac['t0']) / float(ac['a'].get('periodo', 1.6))) % 1.0 * n) % n
            spr = ac['spr'][ix]
            xs = CX0 + s * (xf * W - CX0) + tx
            ys = CY0 + s * (ac['y'] * H - CY0) + ty
            fade = 1.0
            if ac['t0'] > .5:
                fade = min(fade, (t - (ac['t0'] - .3)) / .3)
            if ac['t1'] < self.dur - .5:
                fade = min(fade, ((ac['t1'] + .3) - t) / .3)
            fade = max(0.0, min(1.0, fade))
            ax, ay = ac['ancla']
            sh = self._sombra(spr.shape[1] * s * .8)
            self._blit(f, sh, xs, ys + sh.shape[0] * .1, fade)
            if abs(s - 1) > 1e-3:
                spr = cv2.resize(spr, (int(spr.shape[1] * s), int(spr.shape[0] * s)), interpolation=cv2.INTER_LINEAR)
            # el ancla (punto del suelo bajo el cuerpo) cae en (xs, ys)
            self._blit(f, spr, xs + (spr.shape[1] / 2 - ax * s), ys + (spr.shape[0] - ay * s), fade)

    def _dibujar_owen(self, f, t):
        o = self.owen
        if not o or not (o['t0'] <= t <= o['t1'] + .01):
            return
        a = max(0.0, min(1.0, (t - o['t0']) / .6, (o['t1'] - t) / .5))
        spr = (o['sprf'] if o['lado'] == 'der' else o['spr'])[int((t / 2.4) % 1.0 * len(o['spr']))]
        h, w = spr.shape[:2]
        sx = W * (.84 if o['lado'] == 'der' else .16)
        yb = H + 20 - (1 - ease(a)) * (h * .5) + 6
        self._blit(f, spr, sx, yb, ease(a))
        bub = o['burbuja']
        bx = sx - (bub.shape[1] * .5 + 120 if o['lado'] == 'der' else -bub.shape[1] * .5 - 130)
        by = yb - h * .72
        self._blit(f, bub, min(max(bx, bub.shape[1] / 2 + 20), W - bub.shape[1] / 2 - 20), by + bub.shape[0] * .5,
                   max(0.0, min(1.0, (t - o['t0'] - .5) / .4, (o['t1'] - t) / .4)))

    def _dibujar_mascota(self, f, t, cm):
        m = self.mascota
        if not m or not (m['t0'] <= t <= m['t1']):
            return
        s, tx, ty = self._trans('actores', cm)
        u = min(1.0, max(0.0, (t - m['t0']) / max(m['t1'] - m['t0'], 1e-6)))
        xf = m['x0'] + (m['x1'] - m['x0']) * u
        n = len(m['spr'])
        if m['accion'] in ('camina', 'caminar', 'pasea'):
            ix = int(t * 5.5) % n
        elif m['accion'] == 'olfatea':
            ix = int(t * 3) % n
        elif n == 2:
            ix = 1 if (t % 4.0) > 3.85 else 0
        else:
            ix = 0
        izq = m['x1'] < m['x0']
        spr = (m['sprf'] if izq else m['spr'])[ix]
        ax = m['ancla'][0] if not izq else spr.shape[1] - m['ancla'][0]
        xs = CX0 + s * (xf * W - CX0) + tx + (spr.shape[1] / 2 - ax) * s
        ys = CY0 + s * (m['y'] * H - CY0) + ty
        sh = self._sombra(spr.shape[1] * s * .8)
        self._blit(f, sh, xs, ys + sh.shape[0] * .2)
        if abs(s - 1) > 1e-3:
            spr = cv2.resize(spr, (int(spr.shape[1] * s), int(spr.shape[0] * s)), interpolation=cv2.INTER_LINEAR)
        self._blit(f, spr, xs, ys + (spr.shape[0] - m['ancla'][1] * s))

    # ---------------------------------------------------------------------------- subtítulos y cartel
    def _subtitulos(self):
        self.cues = []
        fnt = ImageFont.truetype(FONT_B, 32)
        for t0, t1, txt in calcular_cues(self.e):
            lineas = _envolver(txt, fnt, 1500)
            im = Image.new('RGBA', (W, 40 * len(lineas) + 22), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            for j, ln in enumerate(lineas):
                tw = d.textlength(ln, font=fnt)
                d.text(((W - tw) / 2, 4 + 40 * j), ln, font=fnt, fill=(244, 240, 232, 255), stroke_width=3, stroke_fill=(10, 8, 8, 255))
            self.cues.append((t0, t1, pm_desde_pil(im)))

    def _cartel(self):
        self.cartel = None
        self.cuaderno = None
        c = self.e.get('cartel')
        if c:
            datos = c.get('datos') or c
            im = _cartel_basico(c.get('tipo', 'titulo'), datos, self.pal)
            self.cartel = dict(pm=pm_desde_pil(im), t0=float(c.get('t0', 1.0)), t1=float(c.get('t1', self.dur - 1.0)))
        c = self.e.get('cuaderno')
        if c:
            lineas = [l for l in str(c.get('texto', '')).split('\n') if l.strip()]
            t0, t1 = float(c.get('t0', 1.0)), min(float(c.get('t1', self.dur - 1.0)), self.dur)
            paso = max(1.6, min(3.0, (t1 - t0 - 2) / max(len(lineas), 1) * .8))
            notas = [dict(k="texto", s=l, pos=(250, 330 + i * 175), size=72, t0=1.0 + i * paso, t1=1.0 + i * paso + paso * .9)
                     for i, l in enumerate(lineas)]
            self.cuaderno = dict(notas=notas, t0=t0, t1=t1, dur=min(14.0, t1 - t0))

    # ---------------------------------------------------------------------------- render de capas
    def _warp(self, nombre, cm, dst, t):
        c = self.capas[nombre]
        s, tx, ty = self._trans(nombre, cm)
        if nombre == 'cielo':
            tx -= 2.0 * t
        img, mx, my = c['img'], c['mx'], c['my']
        ox = CX0 + tx - s * (mx + CX0)
        oy = CY0 + ty - s * (my + CY0)
        if c.get('opaca'):
            cv2.warpAffine(img, np.float32([[s, 0, ox], [0, s, oy]]), (W, H), dst=dst, flags=cv2.INTER_LINEAR,
                           borderMode=cv2.BORDER_REPLICATE)
            return
        v0, v1 = c['v0'], c['v1']
        if v1 <= v0:
            return
        pad = int(c['amp'] * 2) + 4
        ya = int(max(0, math.floor(oy + s * v0) - pad))
        yb = int(min(H, math.ceil(oy + s * v1) + pad))
        if yb <= ya:
            return
        hh = yb - ya
        M = np.float32([[s, 0, ox], [0, s, oy - ya]])
        if c['wmap'] is None or c['amp'] <= 0:
            roi = cv2.warpAffine(img, M, (W, hh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        else:
            wd = cv2.warpAffine(c['wmap'], M, (W, hh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
            X = np.arange(W, dtype=np.float32)
            Sx = (.6 * np.sin(2 * math.pi * (X / 760 - t * .33)) + .4 * np.sin(2 * math.pi * (X / 270 - t * .8) + 1.3)
                  + .25 * np.sin(2 * math.pi * (X / 120 - t * 1.7) + 2.1)).astype(np.float32) * (c['amp'] / 255.0)
            mapx = wd.astype(np.float32) * Sx[None, :]
            mapx += ((X - ox) / s).astype(np.float32)[None, :]
            ry = ((np.arange(hh, dtype=np.float32) + ya - oy) / s)[:, None]
            mapy = np.ascontiguousarray(np.broadcast_to(ry, (hh, W)))
            roi = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        over(dst, roi, ya)

    def _niebla_dibujar(self, k, t, cm, p, y_ini, dst, intensidad=1.0):
        tex = self.nieblas[k]['tex']
        hh, ww = tex.shape[:2]
        sc, ysc = W / ww, H / hh
        off = (self.nieblas[k]['vel'] * t - cm['pan'] * p) / sc
        r0, r1 = int(y_ini * H / ysc), hh
        sub = tex[r0:r1]
        M = np.float32([[1 / sc, 0, off], [0, 1 / ysc, -r0]])
        roi = cv2.warpAffine(sub, M, (W, int((r1 - r0) * ysc)), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                             borderMode=cv2.BORDER_WRAP)
        if intensidad != 1.0:
            roi = (roi.astype(np.float32) * intensidad).astype(np.uint8)
        y0 = int(r0 * ysc)
        over(dst, roi[:H - y0], y0)

    def _dibujar_rayos(self, f, t, cm):
        if not self.ray_tex:
            return
        a, b = self.ray_tex
        m = .5 + .5 * math.sin(t * .45)
        r = cv2.addWeighted(a, 1 - m, b, m, 0)
        k = self.rayos * .30 * (.8 + .2 * math.sin(t * .9 + 1.0))
        tint = (r[..., None] * self.luz_bgr[None, None, :] * (k / 255.0)).astype(np.uint8)
        s = 1 + (cm['z'] - 1) * .2
        M = np.float32([[4 * s, 0, -cm['pan'] * .15 + cm['hx'] * .3 + CX0 * (1 - s)],
                        [0, 4 * s, -cm['grua'] * .1 + CY0 * (1 - s)]])
        cv2.add(f, cv2.warpAffine(tint, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE), dst=f)

    def _bloom(self, f, k=.16):
        if not hasattr(self, '_lb'):
            x = np.linspace(0, 1, 256)
            self._lb = (255 * np.clip((x - .45) / .55, 0, 1) ** 1.6).astype(np.uint8).reshape(256, 1, 1).repeat(3, 2)
        sm = cv2.GaussianBlur(cv2.resize(f, (W // 8, H // 8), interpolation=cv2.INTER_AREA), (0, 0), 3.0)
        big = cv2.resize(cv2.LUT(sm, self._lb), (W, H), interpolation=cv2.INTER_LINEAR)
        cv2.addWeighted(f, 1.0, big, k, 0, dst=f)

    # ---------------------------------------------------------------------------- cuadro
    def frame(self, i):
        t = i / self.fps
        cm = self._cam_t(t)
        cu = self.cuaderno
        ac = 0.0
        if cu and cu['t0'] <= t <= cu['t1']:
            ac = max(0.0, min(1.0, (t - cu['t0']) / .7, (cu['t1'] - t) / .7))
        if ac >= 1.0:       # libreta a pantalla completa: no hace falta la escena
            return self._final(self._cuaderno_frame(t), t, i, grad=False)
        f = np.empty((H, W, 3), np.uint8)
        self._warp('cielo', cm, f, t)
        self._warp('montanas', cm, f, t)
        if self.bruma > .02:
            self._niebla_dibujar(0, t, cm, .25, .20, f)
        self._warp('fondo', cm, f, t)
        self._dibujar_particulas(f, t, cm, 0.0, .35)
        self._warp('medio', cm, f, t)
        self._dibujar_actores(f, t, cm)
        self._dibujar_mascota(f, t, cm)
        self._dibujar_particulas(f, t, cm, .35, .7)
        self._warp('cerca', cm, f, t)
        if self.bruma > .02:
            self._niebla_dibujar(1, t, cm, .9, .48, f, .8)
        self._dibujar_rayos(f, t, cm)
        self._dibujar_particulas(f, t, cm, .7, 1.01)
        self._warp('primer', cm, f, t)
        f = self._gradar(f)
        self._bloom(f)
        self._dibujar_owen(f, t)
        if ac > 0:
            cv2.addWeighted(f, 1 - ac, self._cuaderno_frame(t), ac, 0, dst=f)
        return self._final(f, t, i)

    def _cuaderno_frame(self, t):
        import carteles
        cu = self.cuaderno
        rgb = carteles.cuaderno_frame(t - cu['t0'], cu['notas'], W, H, dur=cu['dur'])
        return np.ascontiguousarray(rgb[..., ::-1])

    def _final(self, f, t, i, grad=True):
        if grad:
            cv2.multiply(f, self.vig, dst=f, scale=1 / 255.)
        g = np.random.default_rng(self.seed * 7919 + i).integers(0, 15, (H // 2, W // 2), dtype=np.uint8)
        cv2.add(f, cv2.cvtColor(cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR), cv2.COLOR_GRAY2BGR), dst=f)
        cv2.subtract(f, (7, 7, 7, 0), dst=f)
        if self.cartel and self.cartel['t0'] <= t <= self.cartel['t1']:
            a = max(0.0, min(1.0, (t - self.cartel['t0']) / .4, (self.cartel['t1'] - t) / .4))
            over(f, (self.cartel['pm'].astype(np.float32) * a).astype(np.uint8), 0)
        for t0, t1, pm in self.cues:
            if t0 <= t <= t1:
                a = max(0.0, min(1.0, (t - t0) / .15, (t1 - t) / .15))
                p = pm if a >= 1 else (pm.astype(np.float32) * a).astype(np.uint8)
                y0 = H - 62 - pm.shape[0]
                self._over_roi(f[y0:y0 + pm.shape[0]], p)
        fi, fo = float(self.e.get('fade_in', .5)), float(self.e.get('fade_out', .5))
        k = 1.0
        if fi > 0 and t < fi:
            k = min(k, t / fi)
        if fo > 0 and t > self.dur - fo:
            k = min(k, (self.dur - t) / fo)
        if k < 1:
            cv2.multiply(f, (k, k, k, 0), dst=f)
        return f


# ------------------------------------------------------------------------------------------ auxiliares
def calcular_cues(esc):
    """Subtítulos de la escena: [(t0, t1, texto)] en segundos relativos a la escena (el fin = siguiente cue o ~0,075 s/letra)."""
    nar = esc.get('narracion') or []
    dur = float(esc['dur'])
    out = []
    for i, n in enumerate(nar):
        t0, txt = float(n['t']), n['texto'].strip()
        fin = float(nar[i + 1]['t']) - .06 if i + 1 < len(nar) else dur
        out.append((t0, min(fin, t0 + max(1.8, .075 * len(txt))), txt))
    return out


def _envolver(txt, fnt, maxw):
    pal = txt.split()
    lineas, act = [], ''
    d = ImageDraw.Draw(Image.new('RGBA', (4, 4)))
    for p in pal:
        prueba = (act + ' ' + p).strip()
        if d.textlength(prueba, font=fnt) <= maxw:
            act = prueba
        else:
            lineas.append(act)
            act = p
    if act:
        lineas.append(act)
    if len(lineas) > 2:
        mid = len(pal) // 2
        lineas = [' '.join(pal[:mid]), ' '.join(pal[mid:])]
    return lineas


def _cartel_basico(tipo, datos, pal):
    """Cartel de calle (placa roja, borde blanco) que aparece arriba del cuadro."""
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    texto = str(datos.get('texto') or datos.get('titulo') or tipo)
    f1 = ImageFont.truetype(FONT_B, 54)
    lineas = _envolver(texto, f1, 1300)
    tw = max(d.textlength(l, font=f1) for l in lineas)
    bw, bh = int(tw + 110), int(len(lineas) * 70 + 60)
    x0, y0 = (W - bw) // 2, 90
    d.rounded_rectangle([x0 + 8, y0 + 10, x0 + bw + 8, y0 + bh + 10], 26, fill=(0, 0, 0, 90))
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], 26, fill=(184, 35, 63, 245), outline=(247, 243, 234, 255), width=8)
    for j, l in enumerate(lineas):
        d.text(((W - d.textlength(l, font=f1)) / 2, y0 + 28 + j * 70), l, font=f1, fill=(247, 243, 234, 255))
    return im


def _burbuja(frase, pal):
    """Globo de diálogo (papel crema, tinta oscura, letra manuscrita)."""
    try:
        fnt = ImageFont.truetype(str(RAIZ / "render" / "fuentes" / "Caveat.ttf"), 50)
    except Exception:
        fnt = ImageFont.truetype(FONT, 36)
    lineas = _envolver(frase, fnt, 520) if frase else ['']
    d0 = ImageDraw.Draw(Image.new('RGBA', (4, 4)))
    tw = max(d0.textlength(l, font=fnt) for l in lineas)
    bw, bh = int(tw + 70), int(len(lineas) * 54 + 52)
    im = Image.new('RGBA', (bw + 30, bh + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([14, 16, bw + 14, bh + 16], 30, fill=(0, 0, 0, 70))
    d.rounded_rectangle([8, 8, bw + 8, bh + 8], 30, fill=(244, 234, 208, 242), outline=(60, 40, 30, 255), width=4)
    for j, l in enumerate(lineas):
        d.text((8 + (bw - d.textlength(l, font=fnt)) / 2, 18 + j * 54), l, font=fnt, fill=(52, 34, 26, 255))
    return im


def _ciclo_stub(especie, pal, n=8):
    """Silueta simple de cuadrúpedo con patas animadas (hasta que exista biblioteca/animales.py)."""
    out = []
    col = tuple(int(v * .55) for v in pal['roca'][1]) + (255,)
    col2 = tuple(int(v * .35) for v in pal['roca'][2]) + (255,)
    for k in range(n):
        im = Image.new('RGBA', (520, 330), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        ph = k / n * 2 * math.pi
        for x, off in ((150, 0), (200, math.pi), (320, math.pi), (370, 0)):
            d.line([(x, 190), (x + math.sin(ph + off) * 26, 300)], fill=col2, width=22)
        d.ellipse([110, 100, 420, 230], fill=col)
        d.ellipse([380, 112, 480, 190], fill=col)
        d.ellipse([440, 130, 500, 170], fill=col)
        out.append(im)
    return out
