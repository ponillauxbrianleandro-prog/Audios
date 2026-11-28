"""Genera la estampa de palmeras grises (tileable) para la camisa. Solo PIL, determinista."""
import math, random, sys
from PIL import Image, ImageDraw, ImageFilter

def frond(d, cx, cy, ang, length, width, col):
    # hoja de palmera = polígono curvo con nervadura
    pts = []
    n = 14
    for i in range(n + 1):
        t = i / n
        a = ang + 0.9 * t * (1 if math.cos(ang) > 0 else -1)
        x = cx + math.cos(ang) * length * t
        y = cy + math.sin(a) * length * t + 0.55 * length * t * t
        w = width * math.sin(math.pi * min(t * 1.1, 1)) ** 0.8
        pts.append((x, y, a, w))
    top = [(x - math.sin(a) * w, y + math.cos(a) * w) for x, y, a, w in pts]
    bot = [(x + math.sin(a) * w, y - math.cos(a) * w) for x, y, a, w in pts]
    d.polygon(top + bot[::-1], fill=col)
    # hendiduras de la hoja
    for i in range(2, n, 2):
        x, y, a, w = pts[i]
        d.line([(x, y), (x + math.sin(a) * w * 1.2, y - math.cos(a) * w * 1.2)], fill=(235, 235, 232), width=2)
        d.line([(x, y), (x - math.sin(a) * w * 1.2, y + math.cos(a) * w * 1.2)], fill=(235, 235, 232), width=2)

def palm(d, x, y, h, s, greys):
    trunk = greys[0]
    pts = [(x + math.sin(t * 1.6) * h * 0.12, y - t * h) for t in [i / 20 for i in range(21)]]
    for i in range(20):
        w = s * (9 - 4 * i / 20)
        d.line([pts[i], pts[i + 1]], fill=trunk, width=int(w))
    tx, ty = pts[-1]
    for k in range(11):
        a = -math.pi * 0.95 + k * math.pi * 0.9 / 10 + random.uniform(-.1, .1)
        frond(d, tx, ty, a, h * random.uniform(.30, .42), s * 12, random.choice(greys))
    for _ in range(3):
        d.ellipse([tx - s * 6, ty - s * 2, tx + s * 6, ty + s * 10], fill=greys[1])

def main(out, size=2048, seed=7):
    random.seed(seed)
    img = Image.new("RGB", (size, size), (236, 236, 233))
    d = ImageDraw.Draw(img)
    greys = [(92, 92, 92), (128, 128, 128), (160, 160, 158), (196, 196, 194), (70, 70, 72), (112, 114, 112)]
    # dos capas: palmeras claras al fondo, oscuras al frente; repetidas en los bordes para tile
    for layer, (n, hmin, hmax, pal) in enumerate([(26, 300, 420, greys[2:4]), (20, 380, 560, greys[:2] + greys[4:])]):
        for _ in range(n):
            x, y = random.uniform(0, size), random.uniform(0, size)
            h = random.uniform(hmin, hmax)
            for ox in (-size, 0, size):
                for oy in (-size, 0, size):
                    palm(d, x + ox, y + oy, h, h / 330, pal)
    img = img.filter(ImageFilter.GaussianBlur(0.8))
    img.save(out)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "work/palm_print.png")
