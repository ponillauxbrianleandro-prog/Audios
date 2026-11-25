"""Dibujo y animación de los 5 shorts de pH (Pillow, supersampling x2)."""
import json
import math
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H, S = 1080, 1920, 2
AQUI = Path(__file__).resolve().parent
FUENTES = "/usr/share/fonts/opentype/inter/Inter-{}.otf"

BG = (14, 42, 59)
BLANCO = (245, 250, 252)
GRIS = (120, 150, 165)
AMARILLO = (255, 200, 61)
VERDE = (76, 195, 138)
AZUL = (61, 123, 255)
ROJO = (229, 56, 59)
NARANJA = (247, 127, 0)
ROSA = (255, 79, 163)
VIOLETA = (108, 63, 196)
VIDRIO = (190, 225, 240)

PALABRAS_COLOR = {
    "amarillo": AMARILLO, "verde": VERDE, "azul": AZUL, "rosado": ROSA,
    "ácido": NARANJA, "ácida": NARANJA, "ácidos": NARANJA, "ácidas": NARANJA,
    "básico": AZUL, "básica": AZUL, "base": AZUL, "bases": AZUL, "neutro": VERDE, "neutras": VERDE,
    "neutra": VERDE,
}


# ---------- utilidades ----------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def back(x):
    x = clamp(x)
    c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def lerp(a, b, k):
    return a + (b - a) * k


def mezcla(c1, c2, k):
    k = clamp(k)
    return tuple(int(lerp(a, b, k)) for a, b in zip(c1, c2))


def track(beat, bt, vals, dur=0.9):
    """Valor animado: vals[i] es el valor al llegar al beat i (None = se mantiene)."""
    res = []
    for v in vals:
        res.append(v if v is not None else (res[-1] if res else 0))
    prev = res[beat - 1] if beat > 0 else res[0]
    return lerp(prev, res[beat], ease(bt / dur))


@lru_cache(maxsize=None)
def fuente(peso, tam):
    return ImageFont.truetype(FUENTES.format(peso), int(tam * S))


def color_btb(ph):
    """Color del azul de bromotimol: amarillo (<6), verde (~6,8), azul (>7,6)."""
    if ph <= 6:
        return AMARILLO
    if ph <= 6.8:
        return mezcla(AMARILLO, VERDE, (ph - 6) / 0.8)
    if ph <= 7.6:
        return mezcla(VERDE, AZUL, (ph - 6.8) / 0.8)
    return AZUL


ESCALA = [(0, ROJO), (3, NARANJA), (5, AMARILLO), (7, VERDE), (10, AZUL), (14, VIOLETA)]


def color_escala(v):
    for (a, ca), (b, cb) in zip(ESCALA, ESCALA[1:]):
        if v <= b:
            return mezcla(ca, cb, (v - a) / (b - a))
    return ESCALA[-1][1]


class Lienzo:
    def __init__(self):
        self.img = Image.new("RGB", (W * S, H * S), BG)
        self.d = ImageDraw.Draw(self.img)

    def p(self, v):
        return v * S

    def pts(self, puntos):
        return [(x * S, y * S) for x, y in puntos]

    def rect(self, x0, y0, x1, y1, fill, r=0, outline=None, ancho=0):
        if x1 < x0 or y1 < y0:
            return
        box = [x0 * S, y0 * S, x1 * S, y1 * S]
        if r:
            self.d.rounded_rectangle(box, r * S, fill=fill, outline=outline, width=int(ancho * S))
        else:
            self.d.rectangle(box, fill=fill, outline=outline, width=int(ancho * S))

    def circ(self, x, y, r, fill=None, outline=None, ancho=0):
        if r <= 0:
            return
        self.d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S],
                       fill=fill, outline=outline, width=int(ancho * S))

    def elip(self, x0, y0, x1, y1, fill):
        if x1 < x0 or y1 < y0:
            return
        self.d.ellipse([x0 * S, y0 * S, x1 * S, y1 * S], fill=fill)

    def poly(self, puntos, fill):
        self.d.polygon(self.pts(puntos), fill=fill)

    def linea(self, puntos, color, ancho):
        self.d.line(self.pts(puntos), fill=color, width=int(ancho * S), joint="curve")

    def texto(self, x, y, s, tam, color=BLANCO, peso="ExtraBold", anchor="mm", alfa=1.0):
        if alfa < 1:
            color = mezcla(BG, color, alfa)
        if alfa <= 0.01 or tam < 2:
            return
        self.d.text((x * S, y * S), s, font=fuente(peso, tam), fill=color, anchor=anchor)

    def ancho_texto(self, s, tam, peso="ExtraBold"):
        return self.d.textlength(s, font=fuente(peso, tam)) / S

    def final(self):
        return self.img.reduce(S)


# ---------- elementos comunes ----------
BAR_X0, BAR_X1 = 90, 990


def px(v):
    return BAR_X0 + (BAR_X1 - BAR_X0) * v / 14


def barra_ph(c, y, reveal=1.0, marcador=None, etiqueta=None, zona=None, rango=None, numeros=True):
    """Recta numérica de pH 0–14. reveal: 0..1 cuánto se dibujó (de izquierda a derecha)."""
    if reveal <= 0:
        return
    hb = 56
    fin = BAR_X0 + (BAR_X1 - BAR_X0) * ease(reveal)
    for i in range(0, 900, 6):
        x = BAR_X0 + i
        if x > fin:
            break
        v = 14 * i / 900
        c.rect(x, y, min(x + 7, fin), y + hb, color_escala(v))
    # extremos redondeados
    c.rect(BAR_X0 - 4, y - 4, BAR_X0 + 10, y + hb + 4, BG)
    c.circ(BAR_X0 + 2, y + hb / 2, hb / 2 - 2, color_escala(0))
    if reveal >= 0.99:
        c.circ(BAR_X1 - 2, y + hb / 2, hb / 2 - 2, color_escala(14))
    if numeros:
        for v in range(15):
            if px(v) <= fin:
                grande = v == 7
                c.texto(px(v), y + hb + 36, str(v), 36 if grande else 30,
                        BLANCO if grande else GRIS, "ExtraBold" if grande else "Bold")
    if rango:  # (a, b, texto)
        a, b, t = rango
        c.rect(px(a), y - 18, px(b), y + hb + 18, None, r=8, outline=BLANCO, ancho=5)
        c.texto((px(a) + px(b)) / 2, y + hb + 100, t, 34, BLANCO, "Bold")
    if zona:  # (a, b, texto, color)
        a, b, t, col = zona
        c.rect(px(a) + 4, y + hb + 76, px(b) - 4, y + hb + 84, col, r=4)
        c.texto((px(a) + px(b)) / 2, y + hb + 128, t, 40, col)
    if marcador is not None:
        mx = px(clamp(marcador, 0, 14))
        c.poly([(mx - 24, y - 26), (mx + 24, y - 26), (mx, y - 2)], BLANCO)
        if etiqueta:
            w = c.ancho_texto(etiqueta, 40) + 56
            c.rect(mx - w / 2, y - 106, mx + w / 2, y - 36, BLANCO, r=35)
            c.texto(mx, y - 71, etiqueta, 40, BG)


def gota(c, x, y, tam, color, alfa=1.0):
    col = mezcla(BG, color, alfa) if alfa < 1 else color
    c.circ(x, y, tam, col)
    c.poly([(x - tam * 0.92, y - tam * 0.3), (x + tam * 0.92, y - tam * 0.3), (x, y - tam * 2.1)], col)


def matraz(c, cx, cy, ancho, alto, color, nivel=0.6, t=0.0, brillo=True):
    """Erlenmeyer. cy = centro; nivel 0..1 de llenado del cuerpo."""
    cuello = ancho * 0.30
    top, base = cy - alto / 2, cy + alto / 2
    yn = top + alto * 0.38
    ya = lambda y: lerp(cuello, ancho, clamp((y - yn) / (base - yn)))  # ancho en y
    # líquido
    ys = lerp(base - 6, yn + 10, nivel)
    pts = []
    n = 24
    wl = ya(ys) / 2 - 8
    for i in range(n + 1):
        x = cx - wl + 2 * wl * i / n
        pts.append((x, ys + 6 * math.sin(t * 3 + i * 0.6)))
    pts += [(cx + ya(base) / 2 - 10, base - 10), (cx - ya(base) / 2 + 10, base - 10)]
    c.poly(pts, color)
    c.linea(pts[:n + 1], mezcla(color, BLANCO, 0.5), 5)
    # vidrio
    contorno = [(cx - cuello / 2, top), (cx - cuello / 2, yn), (cx - ancho / 2, base - 12),
                (cx - ancho / 2 + 14, base), (cx + ancho / 2 - 14, base), (cx + ancho / 2, base - 12),
                (cx + cuello / 2, yn), (cx + cuello / 2, top)]
    c.linea(contorno, VIDRIO, 10)
    c.linea([(cx - cuello / 2 - 14, top), (cx + cuello / 2 + 14, top)], VIDRIO, 10)
    if brillo:
        c.linea([(cx - ancho * 0.30, base - alto * 0.12), (cx - ancho * 0.17, yn + alto * 0.18)],
                mezcla(color, BLANCO, 0.75), 8)


def tubo(c, cx, cy, ancho, alto, color, nivel=0.7, vacio=False):
    if ancho < 16 or alto < 40:
        return
    top, base = cy - alto / 2, cy + alto / 2
    ys = lerp(base - ancho / 2, top + 30, nivel)
    c.rect(cx - ancho / 2 + 6, ys, cx + ancho / 2 - 6, base - ancho / 2, color)
    c.circ(cx, base - ancho / 2, ancho / 2 - 6, color)
    c.linea([(cx - ancho / 2, top), (cx - ancho / 2, base - ancho / 2)], VIDRIO, 9)
    c.linea([(cx + ancho / 2, top), (cx + ancho / 2, base - ancho / 2)], VIDRIO, 9)
    c.d.arc([(cx - ancho / 2) * S, (base - ancho) * S, (cx + ancho / 2) * S, base * S], 0, 180,
            fill=VIDRIO, width=9 * S)
    c.linea([(cx - ancho / 2 - 12, top), (cx + ancho / 2 + 12, top)], VIDRIO, 9)


def limon(c, cx, cy, tam, cara=0.0, alfa=1.0):
    col = mezcla(BG, (255, 214, 64), alfa)
    c.elip(cx - tam, cy - tam * 0.72, cx + tam, cy + tam * 0.72, col)
    c.poly([(cx + tam * 0.9, cy - tam * 0.1), (cx + tam * 1.18, cy - tam * 0.2), (cx + tam * 0.92, cy + tam * 0.18)], col)
    c.poly([(cx - tam * 0.9, cy + tam * 0.1), (cx - tam * 1.18, cy + tam * 0.2), (cx - tam * 0.92, cy - tam * 0.18)], col)
    hoja = mezcla(BG, VERDE, alfa)
    c.elip(cx + tam * 0.1, cy - tam * 0.98, cx + tam * 0.62, cy - tam * 0.62, hoja)
    if cara > 0:  # cara de "uf, qué ácido"
        k = ease(cara)
        ojo = mezcla(col, (90, 60, 0), 1)
        for sx in (-1, 1):
            x = cx + sx * tam * 0.34
            c.linea([(x - 20 * sx, cy - tam * 0.22 - 14), (x + 6 * sx, cy - tam * 0.16), (x - 20 * sx, cy - tam * 0.10 + 14)],
                    ojo, 9)
        pts = [(cx - tam * 0.28 + tam * 0.56 * i / 8, cy + tam * 0.30 + 10 * math.sin(i * 1.6) * k) for i in range(9)]
        c.linea(pts, ojo, 9)


def botella(c, cx, cy, ancho, alto, color, tapa, etiqueta, alfa=1.0, tam_et=34):
    col = mezcla(BG, color, alfa)
    c.rect(cx - ancho / 2, cy - alto / 2 + alto * 0.18, cx + ancho / 2, cy + alto / 2, col, r=ancho * 0.18)
    c.rect(cx - ancho * 0.22, cy - alto / 2 + alto * 0.04, cx + ancho * 0.22, cy - alto / 2 + alto * 0.22, col)
    c.rect(cx - ancho * 0.26, cy - alto / 2, cx + ancho * 0.26, cy - alto / 2 + alto * 0.08, mezcla(BG, tapa, alfa), r=6)
    c.rect(cx - ancho * 0.38, cy - alto * 0.02, cx + ancho * 0.38, cy + alto * 0.30, mezcla(BG, BLANCO, alfa * 0.95), r=10)
    c.texto(cx, cy + alto * 0.14, etiqueta, tam_et, mezcla(BG, BG, 1), "ExtraBold", alfa=alfa)


def frasco(c, cx, cy, ancho, alto, etiqueta, alfa=1.0):
    col = mezcla(BG, (225, 235, 240), alfa)
    c.rect(cx - ancho / 2, cy - alto / 2 + 36, cx + ancho / 2, cy + alto / 2, col, r=24)
    c.rect(cx - ancho * 0.4, cy - alto / 2, cx + ancho * 0.4, cy - alto / 2 + 46, mezcla(BG, ROJO, alfa), r=8)
    c.rect(cx - ancho * 0.36, cy - alto * 0.1, cx + ancho * 0.36, cy + alto * 0.3, mezcla(BG, ROJO, alfa), r=10)
    c.texto(cx, cy + alto * 0.1, etiqueta, 40, BLANCO, "ExtraBold", alfa=alfa)


def gotas_caida(c, x, y0, y1, t, color, periodo=0.5, tam=14):
    for k in range(3):
        f = ((t / periodo) + k / 3) % 1.0
        gota(c, x, lerp(y0, y1, f * f), tam, color, alfa=min(1.0, 3 * (1 - f)) if f > 0.66 else 1.0)


def burbujas(c, x0, x1, y0, y1, t, n=8, color=BLANCO, tam=10):
    for i in range(n):
        f = ((t * 0.5) + i / n) % 1.0
        x = lerp(x0, x1, ((i * 0.618) % 1.0)) + 14 * math.sin(t * 3 + i)
        c.circ(x, lerp(y0, y1, f), tam * (0.6 + 0.6 * ((i * 7) % 3) / 2), None, color, 3)


def x_roja(c, cx, cy, r, prog=1.0):
    k = ease(prog)
    c.linea([(cx - r, cy - r), (cx - r + 2 * r * k, cy - r + 2 * r * k)], ROJO, 14)
    if k > 0.5:
        k2 = (k - 0.5) * 2
        c.linea([(cx + r, cy - r), (cx + r - 2 * r * k2, cy - r + 2 * r * k2)], ROJO, 14)


def tilde(c, cx, cy, r, prog=1.0):
    k = ease(prog)
    p = [(cx - r, cy), (cx - r * 0.3, cy + r * 0.7), (cx + r, cy - r * 0.8)]
    c.linea(p[:2] if k < 0.5 else p, VERDE, 14)


# ---------- escenas ----------
def cabecera(c, n, titulo, t):
    c.rect(60, 96, 60 + 330, 96 + 64, (30, 70, 92), r=32)
    c.texto(225, 128, f"pH  ·  SHORT {n}/5", 30, BLANCO, "Bold")
    for i in range(5):
        c.circ(920 + i * 28, 128, 8 if i + 1 != n else 11, AMARILLO if i + 1 == n else (50, 90, 112))
    k = ease_out(t / 0.6)
    tam = 78
    while c.ancho_texto(titulo, tam) > 960:
        tam -= 2
    c.texto(540, 250 - (1 - k) * 30, titulo, tam, BLANCO, alfa=k)


def pie(c, texto, bt):
    """Subtítulo con palabras clave de color."""
    tam = 62
    max_w = 940
    palabras = texto.split()
    lineas, actual = [], []
    for pal in palabras:
        prueba = " ".join(actual + [pal])
        if c.ancho_texto(prueba, tam) > max_w and actual:
            lineas.append(actual)
            actual = [pal]
        else:
            actual.append(pal)
    lineas.append(actual)
    k = ease_out(bt / 0.3)
    y0 = 1585 - (len(lineas) - 1) * 40 + (1 - k) * 18
    for i, ln in enumerate(lineas):
        total = c.ancho_texto(" ".join(ln), tam)
        x = 540 - total / 2
        for pal in ln:
            limpia = pal.strip(".,:;¿?¡!").lower()
            col = PALABRAS_COLOR.get(limpia, BLANCO)
            c.texto(x, y0 + i * 80, pal, tam, col, anchor="lm", alfa=k)
            x += c.ancho_texto(pal + " ", tam)


def cartel(c, y, texto, color, bt, tam=64, alfa=1.0):
    k = back(bt / 0.4) * alfa
    if k <= 0.01:
        return
    w = c.ancho_texto(texto, tam) + 90
    h = tam + 50
    s = clamp(k, 0, 1.15)
    c.rect(540 - w / 2 * s, y - h / 2 * s, 540 + w / 2 * s, y + h / 2 * s, mezcla(BG, color, 0.22 + 0.0), r=h / 2 * s,
           outline=color, ancho=4)
    if k > 0.6:
        c.texto(540, y, texto, tam, color, alfa=clamp((k - 0.6) / 0.4))


# --- Short 1 ---
def short1(c, t, beat, bt):
    if beat == 0:
        k = back(bt / 0.7)
        c.texto(540, 800, "pH", 440 * clamp(k, 0, 1.1), AMARILLO if bt > 0.9 else BLANCO)
        f = clamp(bt / 0.9)
        if f < 1:
            gota(c, 540, lerp(380, 780, f * f), 30, AZUL)
        else:
            for r in (60, 120):
                a = clamp(1 - (bt - 0.9) / 1.2 - r / 400)
                c.circ(540, 800, r + (bt - 0.9) * 200, None, mezcla(BG, AZUL, a), 6)
    elif beat in (1, 2):
        k = ease(bt / 0.7) if beat == 1 else 1
        c.texto(540, lerp(800, 620, k), "pH", lerp(440, 300, k), AMARILLO)
        c.texto(540, 800, "potencial de hidrógeno", 52, BLANCO, "Bold", alfa=k)
        if beat == 2:  # termómetro de acidez
            c.rect(470, 880, 610, 1210, (30, 70, 92), r=40)
            nivel = ease(bt / 1.4)
            col = color_escala(lerp(0, 14, nivel))
            c.rect(505, lerp(1190, 940, nivel), 575, 1190, col, r=18)
            c.circ(540, 1210, 50, col)
            c.texto(540, 850, "acidez", 40, BLANCO, "Bold", alfa=ease(bt / 0.5))
    else:
        rev = ease_out(bt / 1.8) if beat == 3 else 1
        sube = ease(bt / 0.6) if beat == 3 else 1
        if beat == 3:
            pass
        yb = 760
        c.texto(540, 560, "pH", 260, AMARILLO, alfa=1.0 if beat < 4 else 1.0)
        mar, et, zona = None, None, None
        if beat == 5:
            mar, et, zona = track(5, bt, [0] * 5 + [3.5]), "menor a 7", (0, 7, "ÁCIDO", NARANJA)
            mar = lerp(7, 3.5, ease(bt / 0.9))
        elif beat == 6:
            mar = lerp(3.5, 10.5, ease(bt / 1.0))
            et, zona = "mayor a 7", (7, 14, "BÁSICO", AZUL)
        elif beat >= 7:
            mar = lerp(10.5, 7, ease(bt / 0.9)) if beat == 7 else 7
            et, zona = "7", (6.2, 7.8, "NEUTRO", VERDE)
        if beat == 3:
            mar = None
        barra_ph(c, yb, reveal=rev, marcador=mar, etiqueta=et, zona=zona)
        if beat == 3:
            cartel(c, 1230, "0  a  14", VERDE, bt - 1.2, 60)
        if beat == 4:
            cartel(c, 1230, "0 a 7", GRIS, 0.5, 60)
            x_roja(c, 540, 1230, 80, bt / 0.6)
            if bt > 1.0:
                cartel(c, 1230, "0  a  14", VERDE, bt - 1.0, 60)
        if beat == 8:
            c.texto(540, 1130, "neutro = 7", 74, VERDE, alfa=ease(bt / 0.5))
            pulso = 14 + 8 * math.sin(t * 6)
            c.circ(px(7), yb + 28, 70 + pulso, None, mezcla(BG, VERDE, 0.7), 5)
        if beat == 7:
            pulso = (bt * 1.2) % 1
            c.circ(px(7), yb + 28, 40 + 90 * pulso, None, mezcla(BG, VERDE, 1 - pulso), 5)


# --- Short 2 ---
def short2(c, t, beat, bt):
    ph = track(beat, bt, [7, 7, 7, 3, 7, 11, 7, 7, 7])
    k0 = back(bt / 0.7) if beat == 0 else 1
    fy = 780
    sc = clamp(k0, 0, 1.08)
    if beat < 8:
        matraz(c, 540, fy, 440 * sc, 560 * sc, color_btb(ph), 0.62, t)
    if beat >= 2:
        goteo = beat in (2, 3, 5)
        if goteo:
            col = AZUL
            gotas_caida(c, 540, 420, 700, t, col)
    if beat == 0:
        cartel(c, 1130, "azul de bromotimol", AZUL, bt - 0.4, 56)
    elif beat < 7:
        c.texto(540, 1130, "azul de bromotimol", 52, AZUL if beat < 3 else BLANCO, alfa=1.0 if beat < 3 else 0.6)
    if beat in (3, 4, 5):
        col, txt = {3: (AMARILLO, "ÁCIDO · amarillo"), 4: (VERDE, "NEUTRO · verde"), 5: (AZUL, "BÁSICO · azul")}[beat]
        cartel(c, 1125, txt, col, bt - 0.3, 52)
        c.texto(540, 1130, "", 10)
    if beat == 8:
        for i, (col, nom) in enumerate([(AMARILLO, "ácido"), (VERDE, "neutro"), (AZUL, "básico")]):
            x = 210 + i * 330
            a = clamp(back((bt - i * 0.25) / 0.5), 0, 1.05)
            tubo(c, x, 760, 130 * a, 380 * a, col, 0.7)
            c.texto(x, 1010, nom, 44, col, alfa=clamp(a))
    rango = (6, 7.6, "viraje: pH 6 a 7,6") if beat == 7 else None
    marc = ph if beat >= 3 else None
    barra_ph(c, 1280, 1.0, marcador=marc, etiqueta=("%g" % round(ph)) if marc is not None else None, rango=rango)
    if beat == 7:
        for cx, txt, col in ((290, "incoloro", GRIS), (790, "rosado", ROSA)):
            a = back((bt - 0.5) / 0.4)
            if a > 0:
                c.rect(cx - 130, 1090, cx + 130, 1160, mezcla(BG, col, 0.25), r=35, outline=col, ancho=4)
                c.texto(cx, 1125, txt, 38, col, "Bold")
                x_roja(c, cx, 1125, 34, (bt - 1.0) / 0.4)


# --- Fuentes de ácidos/bases (Short 3 y 4) ---
def goteo_fuente(c, x, y0, y1, t, bt, col):
    f = ((bt * 1.6)) % 1.0
    gota(c, x, lerp(y0, y1, f * f), 13, col, alfa=clamp(1.5 - f))


def short3(c, t, beat, bt):
    ph_f = track(beat, bt, [7, 7, 7, 2, 7, 7, 2.5, 2.5, 2.5])
    x_l = track(beat, bt, [330, 540, 540, 540, 330, 330, 330, 330, 330])
    a_l = track(beat, bt, [1, 1, 1, 1, 0.3, 0.3, 0.3, 1, 1])
    x_v = track(beat, bt, [750, 750, 750, 750, 540, 540, 540, 750, 750])
    a_v = track(beat, bt, [1, 0, 0, 0, 1, 1, 1, 1, 1])
    marc = track(beat, bt, [7, 2, 2, 2, 2.5, 2.5, 2.5, 2.5, 2.5])
    esc = back(bt / 0.6) if beat == 0 else 1
    cara = ease((bt - 0.2) / 0.5) if beat == 8 else 0
    limon(c, x_l, 500, 150 * clamp(esc, 0, 1.1), cara, a_l)
    if a_v > 0.01:
        botella(c, x_v, 500, 170 * clamp(esc, 0, 1.1), 310 * clamp(esc, 0, 1.1), (214, 150, 80), (70, 40, 20), "vinagre",
                a_v, 30)
    if beat >= 1:
        matraz(c, 540, 860, 400, 440, color_btb(ph_f), 0.6, t)
    if beat in (1, 2):
        goteo_fuente(c, 540, 640, 740, t, bt, (255, 230, 120))
    if beat in (4, 5):
        goteo_fuente(c, 540, 640, 740, t, bt, (217, 160, 102))
    if beat in (3, 6):
        gotas_caida(c, 540, 600, 780, t, AZUL)
    if beat == 2:
        cartel(c, 1125, "ácido cítrico", AMARILLO, bt - 0.2, 52)
    if beat == 5:
        cartel(c, 1125, "ácido acético", NARANJA, bt - 0.2, 52)
    if beat in (3, 6):
        cartel(c, 1125, "amarillo · NO verde" if beat == 3 else "amarillo · NO rosado", AMARILLO, bt - 0.6, 48)
    if beat == 7:
        cartel(c, 1125, "amarillo = ácido  ·  pH < 7", AMARILLO, bt - 0.1, 52)
    if beat == 8:
        cartel(c, 1125, "¡ácido!", NARANJA, bt - 0.2, 60)
    et = {1: "limón ≈ 2", 2: "limón ≈ 2", 3: "limón ≈ 2"}.get(beat, "vinagre ≈ 2,5") if beat >= 1 else None
    barra_ph(c, 1280, 1.0, marcador=marc if beat >= 1 else None, etiqueta=et)


def short4(c, t, beat, bt):
    ph_f = track(beat, bt, [7, 7, 10.5, 10.5, 7, 14, 14, 14, 14])
    marc = track(beat, bt, [7, 10.5, 10.5, 10.5, 14, 14, 14, 14, 14])
    fy = track(beat, bt, [860] * 6 + [2300] * 3, 0.8)
    x_d = track(beat, bt, [330, 540, 540, 540, 330, 330, 330, 330, 330])
    a_d = track(beat, bt, [1, 1, 1, 1, 0.3, 0.3, 0, 0, 0])
    x_s = track(beat, bt, [750, 750, 750, 750, 540, 540, 540, 540, 540])
    a_s = track(beat, bt, [1, 0, 0, 0, 1, 1, 0, 0, 0])
    esc = back(bt / 0.6) if beat == 0 else 1
    s = clamp(esc, 0, 1.1)
    if a_d > 0.01:
        botella(c, x_d, 500, 170 * s, 310 * s, (70, 190, 200), (255, 255, 255), "detergente", a_d, 26)
    if a_s > 0.01:
        frasco(c, x_s, 515, 190 * s, 290 * s, "NaOH", a_s)
    if fy < 2000:
        matraz(c, 540, fy, 400, 440, color_btb(ph_f), 0.6, t)
    if beat == 3:
        burbujas(c, 440, 640, 650, 420, bt, 9, (200, 240, 245), 16)
    if beat in (1,):
        goteo_fuente(c, 540, 640, 740, t, bt, (150, 225, 230))
    if beat in (4, 5):
        goteo_fuente(c, 540, 640, 740, t, bt, (235, 240, 245))
    if beat in (2, 5):
        gotas_caida(c, 540, 600, 780, t, AZUL)
    if beat == 2:
        c.rect(750 - 130, 1090, 750 + 130, 1160, mezcla(BG, ROSA, 0.25), r=35, outline=ROSA, ancho=4)
        c.texto(750, 1125, "rosado", 38, ROSA, "Bold")
        x_roja(c, 750, 1125, 34, (bt - 0.8) / 0.4)
        cartel(c, 1135 - 0, "azul", AZUL, bt - 0.3, 52) if False else None
        c.texto(330, 1125, "¡azul!", 56, AZUL, alfa=ease((bt - 0.3) / 0.4))
    if beat == 5:
        cartel(c, 1125, "base muy fuerte · pH 14", AZUL, bt - 0.4, 50)
        # cartel de precaución
        k = back((bt - 0.2) / 0.5)
        c.poly([(860, 380), (860 - 70 * k, 380 + 120 * k), (860 + 70 * k, 380 + 120 * k)], AMARILLO)
        if k > 0.7:
            c.texto(860, 380 + 92 * k, "!", 70, BG)
    if beat in (6, 7, 8):
        e = ease(bt / 0.7) if beat == 6 else 1
        # tubo BTB
        f = (bt * 0.45) % 1.0
        phs = lerp(3, 11, ease(f * 2) if f < 0.5 else ease(2 - f * 2)) if beat == 6 else 11
        ax = 340
        tubo(c, ax, 940, 130, 330 * e, color_btb(phs), 0.7)
        c.texto(ax, 1160, "azul de", 38, BLANCO, "Bold", alfa=e)
        c.texto(ax, 1204, "bromotimol", 38, BLANCO, "Bold", alfa=e)
        if beat == 6:
            c.texto(ax, 740, "amarillo → verde → azul", 30, AMARILLO, "Bold", alfa=e)
            c.rect(ax - 110, 640, ax + 110, 700, mezcla(BG, GRIS, 0.25), r=30, outline=GRIS, ancho=4)
            c.texto(ax, 670, "incoloro", 32, GRIS, "Bold")
            x_roja(c, ax, 670, 28, (bt - 0.8) / 0.4)
        if beat >= 7:
            k = ease(bt / 0.6) if beat == 7 else 1
            bx = 740
            g = clamp((bt - 0.6) / 1.5) if beat == 7 else 1
            tubo(c, bx, 940, 130, 330 * k, mezcla((200, 225, 235), ROSA, g), 0.7)
            c.texto(bx, 1160, "fenolftaleína", 38, ROSA, "Bold", alfa=k)
            c.texto(bx, 1204, "incoloro → rosado", 30, GRIS, "Bold", alfa=k)
        if beat == 8:
            cartel(c, 700, "azul = base · pH > 7", AZUL, bt - 0.1, 56)
    barra_ph(c, 1280, 1.0, marcador=marc if beat >= 1 and beat < 6 else None,
             etiqueta={1: "10 – 11", 2: "10 – 11", 3: "10 – 11"}.get(beat, "14") if beat >= 1 else None)


def ola(c, y, amp, fase, color, periodo=300):
    pts = [(x, y + amp * math.sin(x / periodo * 2 * math.pi + fase)) for x in range(0, W + 30, 30)]
    pts += [(W, 1250), (0, 1250)]
    c.poly(pts, color)


def coral(c, cx, cy, tam, color):
    ramas = [(-0.55, 0.9), (-0.25, 1.15), (0.0, 1.3), (0.28, 1.1), (0.55, 0.85)]
    for a, l in ramas:
        x = cx + math.sin(a) * tam * l
        y = cy - math.cos(a) * tam * l
        c.linea([(cx, cy), (x, y)], color, 20)
        c.circ(x, y, 14, color)
        mx, my = lerp(cx, x, 0.55), lerp(cy, y, 0.55)
        c.linea([(mx, my), (mx + 40 * (1 if a >= 0 else -1), my - 30)], color, 14)


def short5(c, t, beat, bt):
    ola(c, 1010, 14, t * 1.5, (22, 82, 120))
    ola(c, 1040, 12, t * 1.2 + 2, (28, 105, 150))
    ph_r = track(beat, bt, [8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.2, 8.2, 8.2])
    marc = track(beat, bt, [7, 7, 8.5, 8.5, 8.5, 8.5, 8.2, 8.2, 8.2])
    f_izq = back(bt / 0.6) if beat == 1 else (1 if beat >= 2 else 0)
    f_der = back(bt / 0.6) if beat == 2 else (1 if beat >= 3 else 0)
    if beat == 0:
        c.texto(540, 560, "?", 380 * clamp(back(bt / 0.7), 0, 1.1), AMARILLO)
    if beat <= 7:
        out = ease(bt / 0.7) if beat == 8 else 0
        if f_izq > 0:
            matraz(c, 300, 640, 340 * clamp(f_izq, 0, 1.05), 430 * clamp(f_izq, 0, 1.05), color_btb(7), 0.6, t)
            c.texto(300, 880, "agua pura", 38, BLANCO, "Bold", alfa=clamp(f_izq))
            c.texto(300, 930, "pH 7", 46, VERDE, alfa=clamp(f_izq))
        if f_der > 0:
            matraz(c, 780, 640, 340 * clamp(f_der, 0, 1.05), 430 * clamp(f_der, 0, 1.05), color_btb(ph_r), 0.6, t)
            c.texto(780, 880, "agua de mar", 38, BLANCO, "Bold", alfa=clamp(f_der))
            c.texto(780, 930, "pH 8,5", 46, AZUL, alfa=clamp(f_der))
        if beat == 4:
            for i in range(10):
                f = (bt * 0.4 + i / 10) % 1
                c.rect(700 + (i * 37) % 160, 460 + f * 300, 712 + (i * 37) % 160, 532 + f * 300, BLANCO, r=3)
            cartel(c, 1130, "sales disueltas", BLANCO, bt - 0.2, 46)
        if beat == 3:
            cartel(c, 1130, "mayor a 7 → básica", AZUL, bt - 0.2, 52)
        if beat == 5:
            cartel(c, 1130, "azul · pasó el 7,6", AZUL, bt - 0.2, 52)
        if beat == 6:
            burbujas(c, 700, 860, 680, 400, bt, 8, BLANCO, 14)
            c.texto(540, 1130, "CO₂ disuelto  →  pH baja de a poco", 40, NARANJA, alfa=ease(bt / 0.5))
        if beat == 7:
            col = mezcla(ROSA, (140, 140, 140), ease(bt / 2.0))
            coral(c, 540, 1040, 120 * (1 - 0.15 * ease(bt / 2.0)), col)
            c.texto(540, 1130, "corales y conchas", 44, BLANCO, alfa=ease(bt / 0.5))
    if beat == 8:
        a = ease(bt / 0.6)
        for i, (txt, sub, col) in enumerate([("menor a 7", "ÁCIDO", NARANJA), ("igual a 7", "NEUTRO", VERDE),
                                             ("mayor a 7", "BÁSICO", AZUL)]):
            y = 470 + i * 200
            k = back((bt - i * 0.35) / 0.5)
            if k > 0:
                c.rect(120, y - 80 * clamp(k, 0, 1), 960, y + 80 * clamp(k, 0, 1), mezcla(BG, col, 0.2), r=40,
                       outline=col, ancho=4)
                if k > 0.7:
                    c.texto(260, y, sub, 50, col)
                    c.texto(720, y, txt, 52, BLANCO, "Bold")
    barra_ph(c, 1280, 1.0, marcador=marc if beat >= 1 else None,
             etiqueta=("7" if beat == 1 else ("%g" % round(marc * 10) if False else ("8,5" if beat < 6 else "≈ 8,2")))
             if beat >= 1 else None)


ESCENAS = {1: short1, 2: short2, 3: short3, 4: short4, 5: short5}


@lru_cache(maxsize=None)
def datos(n):
    return json.loads((AQUI / "audio" / f"short-{n}.json").read_text(encoding="utf-8"))


def fotograma(n, t):
    d = datos(n)
    cues = d["cues"]
    inicios = [0.0] + [max(0.0, cue["inicio"] - 0.15) for cue in cues[1:]]
    beat = max(i for i, s in enumerate(inicios) if s <= t)
    bt = t - inicios[beat]
    c = Lienzo()
    titulo = d["titulo"].split(". ", 1)[1]
    cabecera(c, n, titulo, t)
    ESCENAS[n](c, t, beat, bt)
    pie(c, cues[beat]["texto"], max(0.0, t - cues[beat]["inicio"] + 0.15))
    c.rect(0, 1888, W * clamp(t / d["duracion"]), 1900, AMARILLO)
    return c.final()
