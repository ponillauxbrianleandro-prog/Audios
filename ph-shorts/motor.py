"""Motor de dibujo: lienzo supersampleado, degradados, resplandor, sprites y utilidades de animación."""
import math
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, S = 1080, 1920, 2
AQUI = Path(__file__).resolve().parent
FUENTES = "/usr/share/fonts/opentype/inter/Inter-{}.otf"

BG = (14, 42, 59)
BLANCO = (245, 250, 252)
GRIS = (130, 160, 175)
AMARILLO = (255, 200, 61)
VERDE = (76, 195, 138)
AZUL = (61, 123, 255)
ROJO = (229, 56, 59)
NARANJA = (247, 127, 0)
ROSA = (255, 79, 163)
VIOLETA = (108, 63, 196)
VIDRIO = (200, 232, 245)
AGUA = (176, 214, 230)

ESCALA = [(0, ROJO), (3, NARANJA), (5, AMARILLO), (7, VERDE), (10, AZUL), (14, VIOLETA)]


# ---------- matemática y easing ----------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    return 1 - (1 - clamp(x)) ** 3


def back(x):
    x = clamp(x)
    c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def lerp(a, b, k):
    return a + (b - a) * k


def mezcla(c1, c2, k):
    k = clamp(k)
    return tuple(int(lerp(a, b, k)) for a, b in zip(c1, c2))


def color_escala(v):
    for (a, ca), (b, cb) in zip(ESCALA, ESCALA[1:]):
        if v <= b:
            return mezcla(ca, cb, (v - a) / (b - a))
    return ESCALA[-1][1]


def color_btb(ph):
    if ph <= 6:
        return AMARILLO
    if ph <= 6.8:
        return mezcla(AMARILLO, VERDE, (ph - 6) / 0.8)
    if ph <= 7.6:
        return mezcla(VERDE, AZUL, (ph - 6.8) / 0.8)
    return AZUL


def fmt(v):
    return f"{v:.1f}".replace(".", ",")


def muelle(t, v0, eventos):
    """Valor con resorte amortiguado (rebota al llegar). eventos: [(ts, valor)]."""
    prev, res = v0, v0
    for ts, v in eventos:
        if t < ts:
            break
        tau = t - ts
        res = v + (prev - v) * math.exp(-3.4 * tau) * math.cos(9.5 * tau)
        prev = v
    return res


def rampa(t, v0, eventos, dur=0.9):
    prev, res = v0, v0
    for ev in eventos:
        ts, v = ev[0], ev[1]
        if t < ts:
            break
        res = lerp(prev, v, ease((t - ts) / dur))
        prev = v
    return res


def evt_color(t, c0, eventos):
    """Mezcla de colores: devuelve (base, nuevo, progreso, x_entrada). eventos: [(ts, color, dur, x)]."""
    cur, ent = c0, None
    for ts, col, du, x in eventos:
        if t < ts:
            break
        p = clamp((t - ts) / du)
        if p < 1:
            return cur, col, p, x
        cur, ent = col, x
    return cur, cur, 0.0, ent if ent is not None else 0


# ---------- guion y tiempos ----------
def leer_guion():
    shorts = []
    for linea in (AQUI / "guion.md").read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if linea.startswith("## SHORT"):
            shorts.append((linea[3:], []))
        elif linea and not linea.startswith("#") and shorts:
            shorts[-1][1].append(linea)
    return shorts


@lru_cache(maxsize=None)
def cronograma(n):
    titulo, lineas = leer_guion()[n - 1]
    dur = [1.0 + 0.24 * len(l.split()) for l in lineas]
    f = clamp(35.0 / sum(dur), 0.85, 1.5)
    dur = [d * f for d in dur]
    dur[-1] += 0.9
    ini = [0.0]
    for d in dur[:-1]:
        ini.append(ini[-1] + d)
    return {"titulo": titulo.split(". ", 1)[1], "textos": lineas, "dur": dur, "ini": ini, "total": sum(dur)}


# ---------- fuentes ----------
@lru_cache(maxsize=None)
def fuente(peso, tam):
    return ImageFont.truetype(FUENTES.format(peso), int(tam * S))


# ---------- fondo ----------
@lru_cache(maxsize=1)
def fondo():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - 540) / 780) ** 2 + ((yy - 720) / 1250) ** 2)
    k = (np.clip(d, 0, 1) ** 1.15)[..., None]
    arr = np.array([28, 88, 120], np.float32) * (1 - k) + np.array([4, 13, 21], np.float32) * k
    arr += np.random.default_rng(1).normal(0, 1.2, arr.shape[:2])[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).resize((W * S, H * S), Image.BILINEAR)


@lru_cache(maxsize=64)
def _falloff(rx, ry):
    xs = (np.arange(2 * rx, dtype=np.float32) - rx) / rx
    ys = (np.arange(2 * ry, dtype=np.float32) - ry) / ry
    d = np.sqrt(xs[None, :] ** 2 + ys[:, None] ** 2)
    return (np.clip(1 - d, 0, 1) ** 2).astype(np.float32)


def comp(img, x0, y0, mask, color, alfa=1.0):
    """Compone `color` (tupla o array HxWx3) sobre img a través de la máscara L ubicada en (x0, y0)."""
    x0, y0 = int(x0), int(y0)
    w, h = mask.size
    box = (max(x0, 0), max(y0, 0), min(x0 + w, img.width), min(y0 + h, img.height))
    if box[2] <= box[0] or box[3] <= box[1]:
        return
    sl = (slice(box[1] - y0, box[3] - y0), slice(box[0] - x0, box[2] - x0))
    mk = (np.asarray(mask, dtype=np.float32)[sl] / 255.0 * alfa)[..., None]
    reg = np.asarray(img.crop(box), dtype=np.float32)
    col = color[sl] if isinstance(color, np.ndarray) else np.array(color, np.float32)
    img.paste(Image.fromarray(np.clip(reg * (1 - mk) + col * mk, 0, 255).astype(np.uint8)), box[:2])


class Dib:
    def __init__(self, img, ox=0.0, oy=0.0):
        self.img, self.ox, self.oy = img, ox, oy
        self.d = ImageDraw.Draw(img)

    def X(self, x):
        return (x - self.ox) * S

    def Y(self, y):
        return (y - self.oy) * S

    def rect(self, x0, y0, x1, y1, fill, r=0, outline=None, ancho=0):
        if x1 < x0 or y1 < y0:
            return
        box = [self.X(x0), self.Y(y0), self.X(x1), self.Y(y1)]
        if r:
            self.d.rounded_rectangle(box, min(r, (x1 - x0) / 2, (y1 - y0) / 2) * S, fill=fill, outline=outline,
                                     width=int(ancho * S))
        else:
            self.d.rectangle(box, fill=fill, outline=outline, width=int(ancho * S))

    def circ(self, x, y, r, fill=None, outline=None, ancho=0):
        if r <= 0:
            return
        self.d.ellipse([self.X(x - r), self.Y(y - r), self.X(x + r), self.Y(y + r)], fill=fill, outline=outline,
                       width=int(ancho * S))

    def elip(self, x0, y0, x1, y1, fill):
        if x1 < x0 or y1 < y0:
            return
        self.d.ellipse([self.X(x0), self.Y(y0), self.X(x1), self.Y(y1)], fill=fill)

    def poly(self, puntos, fill):
        self.d.polygon([(self.X(x), self.Y(y)) for x, y in puntos], fill=fill)

    def linea(self, puntos, color, ancho):
        self.d.line([(self.X(x), self.Y(y)) for x, y in puntos], fill=color, width=max(1, int(ancho * S)),
                    joint="curve")

    def arco_grueso(self, cx, cy, r0, r1, a0, a1, color):
        """Sector anular entre ángulos a0..a1 (grados, sentido horario desde +x)."""
        n = max(2, int(abs(a1 - a0) / 3) + 2)
        ext = [(cx + r1 * math.cos(math.radians(lerp(a0, a1, i / n))), cy + r1 * math.sin(math.radians(lerp(a0, a1, i / n))))
               for i in range(n + 1)]
        inn = [(cx + r0 * math.cos(math.radians(lerp(a1, a0, i / n))), cy + r0 * math.sin(math.radians(lerp(a1, a0, i / n))))
               for i in range(n + 1)]
        self.poly(ext + inn, color)


class Capa(Dib):
    """Sprite transparente centrado en (0, 0) con tamaño w×h (coordenadas de diseño)."""

    def __init__(self, w, h):
        super().__init__(Image.new("RGBA", (int(w * S), int(h * S)), (0, 0, 0, 0)), -w / 2, -h / 2)


class Lienzo(Dib):
    def __init__(self):
        super().__init__(fondo().copy())

    # --- efectos ---
    def glow(self, x, y, r, color, k):
        rx = int(r * S / 20) * 20 or 20
        f = _falloff(rx, rx)
        self._sumar(int(x * S - rx), int(y * S - rx), f, color, k)

    def _sumar(self, x0, y0, f, color, k):
        h, w = f.shape
        box = (max(x0, 0), max(y0, 0), min(x0 + w, self.img.width), min(y0 + h, self.img.height))
        if box[2] <= box[0] or box[3] <= box[1]:
            return
        ff = f[box[1] - y0:box[3] - y0, box[0] - x0:box[2] - x0, None]
        reg = np.asarray(self.img.crop(box), dtype=np.float32)
        self.img.paste(Image.fromarray(np.clip(reg + ff * np.array(color, np.float32) * k, 0, 255).astype(np.uint8)),
                       box[:2])

    def sombra(self, x, y, rx, ry, k=0.55):
        rxs, rys = max(20, int(rx * S / 10) * 10), max(10, int(ry * S / 10) * 10)
        f = _falloff(rxs, rys)
        x0, y0 = int(x * S - rxs), int(y * S - rys)
        h, w = f.shape
        box = (max(x0, 0), max(y0, 0), min(x0 + w, self.img.width), min(y0 + h, self.img.height))
        if box[2] <= box[0] or box[3] <= box[1]:
            return
        ff = f[box[1] - y0:box[3] - y0, box[0] - x0:box[2] - x0, None]
        reg = np.asarray(self.img.crop(box), dtype=np.float32)
        self.img.paste(Image.fromarray(np.clip(reg * (1 - ff * k), 0, 255).astype(np.uint8)), box[:2])

    def poly_grad(self, puntos, c_top, c_bot, alfa=1.0):
        P = [(self.X(x), self.Y(y)) for x, y in puntos]
        x0, y0 = int(min(p[0] for p in P)) - 2, int(min(p[1] for p in P)) - 2
        x1, y1 = int(max(p[0] for p in P)) + 3, int(max(p[1] for p in P)) + 3
        m = Image.new("L", (x1 - x0, y1 - y0), 0)
        ImageDraw.Draw(m).polygon([(a - x0, b - y0) for a, b in P], fill=255)
        self._grad(m, x0, y0, c_top, c_bot, alfa)

    def rr_grad(self, x0, y0, x1, y1, c_top, c_bot, alfa=1.0, r=0):
        if x1 <= x0 or y1 <= y0:
            return
        X0, Y0, X1, Y1 = int(x0 * S), int(y0 * S), int(x1 * S), int(y1 * S)
        m = Image.new("L", (X1 - X0, Y1 - Y0), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, X1 - X0 - 1, Y1 - Y0 - 1], min(r, (x1 - x0) / 2, (y1 - y0) / 2) * S,
                                            fill=255)
        self._grad(m, X0, Y0, c_top, c_bot, alfa)

    def _grad(self, m, x0, y0, c_top, c_bot, alfa):
        w, h = m.size
        k = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
        col = np.array(c_top, np.float32) * (1 - k) + np.array(c_bot, np.float32) * k
        comp(self.img, x0, y0, m, np.broadcast_to(col, (h, w, 3)), alfa)

    def texto(self, x, y, s, tam, color=BLANCO, peso="ExtraBold", anchor="mm", alfa=1.0, sombra=False):
        if alfa <= 0.01 or tam < 2:
            return
        f = fuente(peso, tam)
        bb = self.d.textbbox((x * S, y * S), s, font=f, anchor=anchor)
        pad = int(10 * S)
        x0, y0 = int(bb[0] - pad), int(bb[1] - pad)
        m = Image.new("L", (int(bb[2] - bb[0] + 2 * pad), int(bb[3] - bb[1] + 2 * pad)), 0)
        ImageDraw.Draw(m).text((x * S - x0, y * S - y0), s, font=f, fill=255, anchor=anchor)
        if sombra:
            sm = m.filter(ImageFilter.GaussianBlur(4 * S))
            comp(self.img, x0, y0 + 5 * S, sm, (0, 0, 0), alfa * 0.7)
        comp(self.img, x0, y0, m, color, alfa)

    def ancho_texto(self, s, tam, peso="ExtraBold"):
        return self.d.textlength(s, font=fuente(peso, tam)) / S

    def pegar(self, capa, cx, cy, rot=0.0, sx=1.0, sy=1.0, alfa=1.0):
        im = capa.img
        if sx != 1 or sy != 1:
            im = im.resize((max(1, int(im.width * sx)), max(1, int(im.height * sy))), Image.BICUBIC)
        if rot:
            im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
        a = im.getchannel("A")
        if alfa < 1:
            a = a.point(lambda v: int(v * alfa))
        self.img.paste(im.convert("RGB"), (int(cx * S - im.width / 2), int(cy * S - im.height / 2)), a)

    def final(self):
        return self.img.reduce(S)
