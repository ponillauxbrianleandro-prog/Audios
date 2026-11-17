"""Sprites 2D procedurales (Pillow) para el episodio 003: pasteles, volumen suave, pelaje esponjoso."""
import math
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SS = 3
FUENTE = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def lite(c, t):
    return mix(c, (255, 255, 255), t)


def dark(c, t):
    return mix(c, (60, 40, 60), t)


class Lienzo:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.im = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def ell(self, cx, cy, rx, ry, fill, rot=0):
        if rot:
            capa = Lienzo(self.w, self.h)
            capa.ell(cx, cy, rx, ry, fill)
            self.im.alpha_composite(capa.im.rotate(rot, resample=Image.BICUBIC, center=(cx * SS, cy * SS)))
            self.d = ImageDraw.Draw(self.im)
            return
        self.d.ellipse([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], fill=fill)

    def poly(self, pts, fill):
        self.d.polygon([(x * SS, y * SS) for x, y in pts], fill=fill)

    def linea(self, pts, fill, ancho):
        self.d.line([(x * SS, y * SS) for x, y in pts], fill=fill, width=int(ancho * SS), joint="curve")
        for x, y in (pts[0], pts[-1]):
            r = ancho / 2
            self.ell(x, y, r, r, fill)

    def rect(self, x0, y0, x1, y1, fill, r=0):
        self.d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=r * SS, fill=fill)

    def bola(self, cx, cy, rx, ry, col, pasos=14):
        """Elipse con volumen: borde oscuro, centro claro desplazado hacia arriba a la izquierda."""
        for k in range(pasos):
            u = k / (pasos - 1)
            c = mix(dark(col, 0.16), col, min(1, u * 2)) if u < 0.5 else mix(col, lite(col, 0.32), (u - 0.5) * 2)
            f = 1 - 0.5 * u
            self.ell(cx - 0.14 * rx * u, cy - 0.2 * ry * u, rx * f, ry * f, c)

    def pelusa(self, cx, cy, rx, ry, col, n, largo, seed=1, a0=0.0, a1=2 * math.pi):
        rnd = random.Random(seed)
        for i in range(n):
            a = a0 + (a1 - a0) * (i + rnd.random()) / n
            dx, dy = math.cos(a), math.sin(a)
            px, py = cx + dx * rx * 0.93, cy + dy * ry * 0.93
            ln = largo * (0.55 + rnd.random() * 0.9)
            w = largo * 0.3
            tip = (px + dx * ln, py + dy * ln)
            c = mix(col, lite(col, 0.4) if rnd.random() > 0.5 else dark(col, 0.18), rnd.random() * 0.6)
            self.poly([(px - dy * w, py + dx * w), tip, (px + dy * w, py - dx * w)], c)

    def fin(self, blur=0):
        im = self.im.resize((self.w, self.h), Image.LANCZOS)
        return im.filter(ImageFilter.GaussianBlur(blur)) if blur else im


def ojos(L, pts, r=7, cerrado=False, col=(60, 40, 60)):
    for x, y in pts:
        if cerrado:
            L.linea([(x - r, y), (x, y + r * 0.5), (x + r, y)], col, r * 0.5)
        else:
            L.ell(x, y, r, r * 1.1, col)
            L.ell(x - r * 0.3, y - r * 0.35, r * 0.35, r * 0.35, (255, 255, 255))


def fuente(tam):
    return ImageFont.truetype(FUENTE, tam)


def texto(txt, tam, fill=(255, 255, 255), borde=(70, 40, 70), grosor=8, rot=0, sombra=True):
    f = fuente(tam)
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = d.textbbox((0, 0), txt, font=f, stroke_width=grosor)
    w, h = r - l + 24, b - t + 24 + (8 if sombra else 0)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if sombra:
        d.text((12 - l, 12 - t + 8), txt, font=f, fill=borde + (255,), stroke_width=grosor, stroke_fill=borde + (255,))
    d.text((12 - l, 12 - t), txt, font=f, fill=fill, stroke_width=grosor, stroke_fill=borde)
    return im.rotate(rot, resample=Image.BICUBIC, expand=True) if rot else im


# ---------------- animales ----------------
ROSA = (255, 190, 205)
TAGUA = (196, 172, 158)
CREMA = (252, 240, 220)


def cerdo(cerrado=False):
    L = Lienzo(460, 480)
    for x in (150, 310):
        L.bola(x, 430, 42, 40, dark(ROSA, 0.12))
        L.rect(x - 14, 438, x - 4, 462, dark(ROSA, 0.35), 4)
        L.rect(x + 4, 438, x + 14, 462, dark(ROSA, 0.35), 4)
    L.bola(230, 310, 185, 130, ROSA)
    L.pelusa(230, 310, 185, 130, lite(ROSA, 0.2), 70, 7, 5)
    L.bola(230, 310, 182, 127, ROSA)
    L.ell(70, 320, 18, 18, dark(ROSA, 0.1))  # lomo curvo
    L.bola(230, 190, 112, 104, ROSA)
    L.poly([(135, 118), (92, 150), (122, 205)], dark(ROSA, 0.12))
    L.poly([(325, 118), (368, 150), (338, 205)], dark(ROSA, 0.12))
    L.poly([(141, 128), (110, 152), (130, 190)], lite(ROSA, 0.25))
    L.poly([(319, 128), (350, 152), (330, 190)], lite(ROSA, 0.25))
    L.ell(158, 215, 24, 15, (255, 150, 175))
    L.ell(302, 215, 24, 15, (255, 150, 175))
    L.bola(230, 222, 54, 40, lite(ROSA, 0.15))
    L.ell(214, 224, 8, 12, (200, 110, 140))
    L.ell(246, 224, 8, 12, (200, 110, 140))
    ojos(L, [(182, 168), (278, 168)], 7, cerrado)
    return L.fin()


def tagua(cerrado=False):
    L = Lienzo(540, 540)
    # cerdas largas del lomo (crin) detrás de todo
    L.pelusa(270, 200, 150, 120, dark(TAGUA, 0.28), 46, 38, 8, math.pi * 1.05, math.pi * 1.95)
    L.bola(270, 215, 142, 108, dark(TAGUA, 0.3))
    # patas con tres dedos
    for x in (175, 365):
        L.bola(x, 470, 40, 48, dark(TAGUA, 0.3))
        for dx in (-20, 0, 20):
            L.ell(x + dx, 512, 11, 12, (95, 78, 80))
    # cuerpo esponjoso
    L.pelusa(270, 340, 215, 150, TAGUA, 110, 30, 2)
    L.bola(270, 340, 212, 148, TAGUA)
    L.pelusa(270, 340, 190, 128, lite(TAGUA, 0.25), 60, 14, 3, 0.2, math.pi - 0.2)
    # collar claro
    L.pelusa(270, 325, 150, 62, CREMA, 50, 14, 4, 0.1, math.pi - 0.1)
    L.bola(270, 320, 148, 62, CREMA)
    # cabeza
    L.pelusa(270, 235, 108, 98, TAGUA, 56, 20, 6)
    L.bola(270, 235, 106, 96, TAGUA)
    for sx in (-1, 1):  # orejas con mechón
        px = 270 + sx * 70
        L.poly([(px - 24, 160), (px + sx * 22, 98), (px + 22, 168)], dark(TAGUA, 0.2))
        L.poly([(px - 10, 152), (px + sx * 14, 116), (px + 12, 160)], (235, 190, 190))
        L.pelusa(px + sx * 20, 108, 10, 10, dark(TAGUA, 0.35), 8, 12, 9 + sx)
    # hocico chato con narinas
    L.bola(270, 268, 54, 44, (226, 172, 172))
    L.ell(251, 268, 9, 12, (120, 70, 90))
    L.ell(289, 268, 9, 12, (120, 70, 90))
    L.ell(205, 262, 20, 12, (255, 175, 190))
    L.ell(335, 262, 20, 12, (255, 175, 190))
    ojos(L, [(222, 218), (318, 218)], 6, cerrado)
    return L.fin()


def pata():
    L = Lienzo(360, 330)
    L.bola(180, 130, 130, 120, dark(TAGUA, 0.2))
    L.pelusa(180, 80, 120, 70, TAGUA, 40, 22, 1, math.pi, 2 * math.pi)
    for dx in (-80, 0, 80):
        L.bola(180 + dx, 250, 42, 62, (110, 90, 92))
        L.poly([(180 + dx - 30, 285), (180 + dx, 318), (180 + dx + 30, 285)], (70, 55, 60))
    return L.fin()


def vizcacha():
    L = Lienzo(240, 250)
    G = (190, 188, 200)
    L.bola(120, 170, 85, 70, G)
    L.bola(120, 100, 66, 58, G)
    L.ell(70, 62, 14, 26, dark(G, 0.2)); L.ell(170, 62, 14, 26, dark(G, 0.2))
    L.bola(120, 118, 30, 22, lite(G, 0.35))
    L.ell(120, 108, 7, 5, (110, 70, 90))
    for sx in (-1, 1):
        for k, dy in enumerate((-6, 4, 14)):
            L.linea([(120 + sx * 18, 118 + dy * .5), (120 + sx * (60 + k * 6), 112 + dy)], (120, 105, 120), 2)
    L.rect(112, 130, 128, 148, (255, 255, 255), 4)
    L.ell(98, 88, 5, 5, (70, 50, 70)); L.ell(142, 88, 5, 5, (70, 50, 70))
    return L.fin()


def gaucho(poncho=(236, 150, 160), sombrero=(120, 100, 130), bata=False):
    L = Lienzo(220, 340)
    traje = (250, 250, 255) if bata else poncho
    L.rect(70, 290, 100, 330, (90, 70, 90), 6); L.rect(120, 290, 150, 330, (90, 70, 90), 6)
    L.poly([(110, 120), (210, 300), (10, 300)], dark(traje, 0.1))
    L.poly([(110, 130), (190, 296), (30, 296)], traje)
    if not bata:
        for y, c in ((220, (255, 240, 200)), (255, (255, 240, 200))):
            L.poly([(110 - (y - 130) * .52, y), (110 + (y - 130) * .52, y), (110 + (y - 130) * .52, y + 10), (110 - (y - 130) * .52, y + 10)], c)
    L.bola(110, 92, 44, 46, (250, 205, 175))
    L.ell(110, 108, 22, 5, (110, 70, 80))  # bigote
    L.ell(110, 96, 6, 5, (235, 165, 150))
    ojos(L, [(94, 78), (126, 78)], 4)
    if bata:
        L.ring = None
        L.bola(110, 52, 44, 26, (255, 255, 255))
        L.ell(110, 76, 44, 4, (120, 100, 120))
    else:
        L.ell(110, 58, 80, 14, sombrero)
        L.bola(110, 40, 40, 34, sombrero)
        L.rect(72, 46, 148, 56, dark(sombrero, 0.3), 3)
    L.bola(40, 208, 17, 17, (250, 205, 175)); L.bola(180, 208, 17, 17, (250, 205, 175))
    return L.fin()


def lupa():
    L = Lienzo(130, 170)
    L.linea([(80, 80), (30, 150)], (140, 100, 110), 14)
    L.ell(85, 60, 46, 46, (120, 90, 110))
    L.ell(85, 60, 36, 36, (215, 240, 255))
    L.ell(70, 46, 10, 7, (255, 255, 255))
    return L.fin()


def cactus(tunas=True):
    L = Lienzo(320, 400)
    V = (150, 205, 160)

    def penca(cx, cy, rx, ry, rot=0):
        L.ell(cx, cy, rx + 5, ry + 5, dark(V, 0.25), rot)
        L.ell(cx, cy, rx, ry, V, rot)
        L.ell(cx - rx * .2, cy - ry * .25, rx * .55, ry * .5, lite(V, 0.3), rot)
        rnd = random.Random(int(cx * 7 + cy))
        for _ in range(14):
            a, r = rnd.random() * 6.28, rnd.random() * .8
            x, y = cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r
            L.linea([(x, y), (x + 6, y - 7)], (255, 245, 210), 2)

    penca(160, 300, 82, 62)
    penca(90, 215, 58, 66, -22)
    penca(230, 205, 60, 64, 20)
    penca(150, 120, 54, 62, -6)
    penca(220, 62, 40, 46, 18)
    if tunas:
        for x, y in ((92, 150), (232, 140), (260, 22), (170, 56), (60, 250)):
            L.bola(x, y, 15, 19, (245, 120, 150))
            L.ell(x, y - 18, 6, 4, (255, 210, 120))
    return L.fin()


def tuna():
    L = Lienzo(90, 110)
    L.bola(45, 62, 32, 42, (245, 120, 150))
    L.ell(45, 18, 14, 8, (255, 210, 120))
    for a in range(6):
        L.linea([(45 + (a - 3) * 9, 50 + (a % 2) * 18), (48 + (a - 3) * 9, 44 + (a % 2) * 18)], (255, 245, 210), 2)
    return L.fin()


def raiz():
    L = Lienzo(150, 90)
    L.poly([(10, 30), (140, 52), (10, 62)], (245, 190, 130))
    L.ell(20, 46, 22, 20, (240, 175, 120))
    L.linea([(120, 50), (146, 44)], (200, 150, 110), 4)
    return L.fin()


def bromelia():
    L = Lienzo(150, 130)
    for a in range(-4, 5):
        x = 75 + a * 15
        L.poly([(75, 120), (x - 7, 118), (x + a * 6, 18 + abs(a) * 7)], (160, 210, 150) if a % 2 else (120, 190, 150))
    L.ell(75, 112, 22, 12, (255, 150, 170))
    return L.fin()


def empanada():
    L = Lienzo(150, 100)
    L.ell(75, 56, 62, 40, (255, 215, 150))
    L.poly([(13, 56), (137, 56), (137, 100), (13, 100)], (0, 0, 0, 0))
    L.ell(75, 50, 52, 30, (250, 195, 120))
    for x in range(22, 130, 14):
        L.ell(x, 76, 6, 5, (240, 170, 100))
    return L.fin()


def plato(lleno=False):
    L = Lienzo(140, 50)
    L.ell(70, 30, 62, 16, (240, 235, 250))
    L.ell(70, 27, 46, 10, (222, 216, 238))
    if lleno:
        L.bola(70, 20, 30, 14, (245, 120, 150))
    return L.fin()


def mesa():
    L = Lienzo(560, 220)
    L.rect(40, 40, 520, 90, (255, 200, 200), 12)
    for i in range(12):
        for j in range(2):
            if (i + j) % 2:
                L.rect(40 + i * 40, 40 + j * 25, 80 + i * 40, 65 + j * 25, (255, 240, 240))
    L.rect(70, 90, 100, 205, (190, 150, 140), 6); L.rect(460, 90, 490, 205, (190, 150, 140), 6)
    return L.fin()


def nube(cara=False):
    L = Lienzo(300, 160)
    for cx, cy, r in ((90, 100, 52), (150, 70, 62), (210, 100, 54), (150, 108, 56)):
        L.bola(cx, cy, r, r * .85, (255, 255, 255))
    if cara:
        ojos(L, [(125, 90), (175, 90)], 6)
        L.linea([(135, 112), (150, 122), (165, 112)], (160, 110, 130), 4)
        L.ell(110, 108, 12, 7, (255, 190, 205)); L.ell(190, 108, 12, 7, (255, 190, 205))
    return L.fin()


def pajaro(ala):
    L = Lienzo(150, 120)
    B = (255, 225, 140)
    dy = -30 if ala else 12
    L.ell(70, 70 + dy / 3, 40, 12, dark(B, 0.2), -30 if ala else 25)
    L.bola(75, 72, 42, 36, B)
    L.poly([(112, 66), (140, 76), (112, 84)], (255, 160, 120))
    ojos(L, [(95, 62)], 5)
    L.ell(60, 72 + dy / 2, 28, 12, dark(B, 0.15), -25 if ala else 20)
    return L.fin()


def mariposa():
    L = Lienzo(120, 100)
    for sx in (-1, 1):
        L.ell(60 + sx * 26, 38, 26, 30, (255, 170, 210), sx * 25)
        L.ell(60 + sx * 22, 68, 18, 20, (190, 170, 255), -sx * 20)
    L.ell(60, 52, 5, 26, (110, 80, 110))
    return L.fin()


def pollito():
    L = Lienzo(90, 90)
    L.bola(45, 50, 30, 28, (255, 232, 130))
    L.poly([(70, 48), (88, 54), (70, 60)], (255, 160, 120))
    ojos(L, [(56, 42)], 4)
    return L.fin()


def patito():
    L = Lienzo(180, 120)
    L.bola(85, 80, 62, 32, (255, 252, 240))
    L.bola(130, 48, 28, 26, (255, 252, 240))
    L.poly([(150, 46), (176, 54), (150, 62)], (255, 175, 110))
    ojos(L, [(136, 40)], 4)
    return L.fin()


def mosca():
    L = Lienzo(40, 36)
    L.ell(12, 14, 9, 6, (255, 255, 255, 200)); L.ell(28, 14, 9, 6, (255, 255, 255, 200))
    L.ell(20, 22, 8, 7, (90, 70, 90))
    return L.fin()


def hedor():
    L = Lienzo(180, 160)
    for cx, cy, r in ((60, 100, 34), (100, 78, 40), (126, 108, 32), (90, 120, 30)):
        L.ell(cx, cy, r, r * .85, (170, 225, 150, 150))
    return L.fin(blur=1.5)


def corazon():
    L = Lienzo(70, 64)
    L.ell(22, 22, 17, 17, (255, 130, 170)); L.ell(48, 22, 17, 17, (255, 130, 170))
    L.poly([(7, 28), (63, 28), (35, 60)], (255, 130, 170))
    return L.fin()


def estrella(col=(255, 230, 130)):
    L = Lienzo(80, 80)
    pts = []
    for i in range(10):
        r = 36 if i % 2 == 0 else 15
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((40 + math.cos(a) * r, 40 + math.sin(a) * r))
    L.poly(pts, col)
    return L.fin()


def sol():
    L = Lienzo(360, 360)
    for i in range(14):
        a = i * math.pi * 2 / 14
        L.poly([(180 + math.cos(a - .1) * 100, 180 + math.sin(a - .1) * 100), (180 + math.cos(a) * 170, 180 + math.sin(a) * 170),
                (180 + math.cos(a + .1) * 100, 180 + math.sin(a + .1) * 100)], (255, 225, 160, 255))
    L.bola(180, 180, 92, 92, (255, 214, 140))
    ojos(L, [(150, 170), (210, 170)], 7)
    L.linea([(155, 205), (180, 222), (205, 205)], (190, 120, 110), 5)
    return L.fin()


def calavera():
    L = Lienzo(260, 240)
    H = (244, 234, 214)
    L.bola(130, 100, 100, 86, H)
    L.rect(70, 150, 190, 215, dark(H, 0.06), 20)
    for x in range(86, 180, 18):
        L.rect(x, 192, x + 10, 220, (200, 188, 170), 3)
    L.ell(92, 96, 26, 30, (80, 60, 80)); L.ell(168, 96, 26, 30, (80, 60, 80))
    L.poly([(122, 135), (138, 135), (130, 155)], (80, 60, 80))
    L.linea([(150, 20), (172, 52), (160, 62)], (170, 150, 140), 3)
    return L.fin()


def cartel(txt, tam=44, fill=(255, 250, 240), tabla=(214, 170, 140), borde=(120, 80, 100)):
    t = texto(txt, tam, fill, borde, 6, sombra=False)
    w, h = t.size[0] + 50, t.size[1] + 36
    L = Lienzo(w, h)
    L.rect(0, 0, w, h, dark(tabla, 0.25), 22)
    L.rect(6, 6, w - 6, h - 12, tabla, 18)
    im = L.fin()
    im.alpha_composite(t, (25, 14))
    return im


def sello(txt, sub=None, col=(235, 90, 110)):
    t = texto(txt, 120, col, (255, 255, 255), 0, sombra=False)
    w, h = t.size[0] + 90, t.size[1] + 70 + (60 if sub else 0)
    L = Lienzo(w, h)
    L.d.rounded_rectangle([6 * SS, 6 * SS, (w - 6) * SS, (h - 6) * SS], radius=24 * SS, outline=col + (255,), width=12 * SS)
    im = L.fin()
    im.alpha_composite(t, (45, 28))
    if sub:
        s = texto(sub, 70, col, (255, 255, 255), 0, sombra=False)
        im.alpha_composite(s, ((w - s.size[0]) // 2, h - s.size[1] - 24))
    return im


def mitad_sello(im, izq):
    w, h = im.size
    out = Image.new("RGBA", (w // 2 + 6, h), (0, 0, 0, 0))
    out.paste(im.crop((0, 0, w // 2, h)) if izq else im.crop((w // 2, 0, w, h)), (0, 0))
    return out


def globo(txt, tam=40):
    t = texto(txt, tam, (90, 60, 100), (255, 255, 255), 0, sombra=False)
    w, h = t.size[0] + 40, t.size[1] + 36
    L = Lienzo(w, h + 24)
    L.rect(0, 0, w, h, (255, 255, 255), 28)
    L.poly([(w * .3, h - 4), (w * .3 + 30, h - 4), (w * .3 - 6, h + 22)], (255, 255, 255))
    im = L.fin()
    im.alpha_composite(t, (20, 8))
    return im


def sombra():
    L = Lienzo(220, 60)
    L.ell(110, 30, 100, 20, (60, 40, 70, 120))
    return L.fin(blur=6)


def charco():
    L = Lienzo(520, 130)
    L.ell(260, 70, 250, 52, (150, 110, 95))
    L.ell(260, 62, 232, 42, (178, 135, 112))
    L.ell(190, 56, 60, 10, (200, 160, 135))
    return L.fin()


def construir():
    s = {
        "pig": cerdo(), "pig_c": cerdo(True), "tag": tagua(), "tag_c": tagua(True), "pata": pata(),
        "viz": vizcacha(), "gaucho": gaucho(), "cient": gaucho(bata=True, sombrero=(255, 255, 255)),
        "lupa": lupa(), "cactus": cactus(), "cactus_s": cactus(False), "tuna": tuna(), "raiz": raiz(),
        "brom": bromelia(), "emp": empanada(), "plato": plato(), "plato_l": plato(True), "mesa": mesa(),
        "nube": nube(), "nube_c": nube(True), "paj0": pajaro(0), "paj1": pajaro(1), "mari": mariposa(),
        "pollo": pollito(), "pato": patito(), "mosca": mosca(), "hedor": hedor(), "cora": corazon(),
        "estr": estrella(), "estr2": estrella((255, 190, 210)), "sol": sol(), "cala": calavera(),
        "sombra": sombra(), "charco": charco(),
        "c_nombre": cartel("CHANCHO QUIMILERO", 50), "c_tagua": cartel("(o TAGUÁ)", 40),
        "c_menu": cartel("MENÚ: ESPINAS", 44), "c_1930": cartel("1930", 70, tabla=(210, 205, 225)),
        "c_tuna": cartel("TUNA", 36), "c_raiz": cartel("RAÍCES", 36), "c_brom": cartel("BROMELIAS", 36),
        "c_3": cartel("3 DEDOS", 60), "c_manada": cartel("LÍNEA 10 · COMPLETO", 40, tabla=(160, 205, 235)),
        "c_70": cartel("AÑOS 70: ¡VIVO!", 56, tabla=(255, 225, 150)),
        "c_obt": cartel("¡OBTUVISTE: ORGULLO CHANCHO!", 36, tabla=(255, 225, 150)),
        "t_vos": texto("¡VOS!", 150, (255, 255, 255), (230, 90, 130), 14),
        "t_chancho": texto("¡CHANCHO!", 100, (255, 240, 130), (230, 90, 130), 14),
        "t_pfff": texto("¡PFFFF!", 130, (200, 255, 190), (90, 150, 110), 14),
        "t_orgullo": texto("¡CON ORGULLO!", 82, (255, 240, 130), (230, 90, 130), 14),
        "g_tero": globo("¡TERO, TERO!"), "g_repetir": globo("¡REPETIR!"), "g_agua": globo("¿Agua? Nah."),
        "sello": sello("EXTINTO", "1930"),
    }
    s["sello_i"] = mitad_sello(s["sello"], True)
    s["sello_d"] = mitad_sello(s["sello"], False)
    return s
