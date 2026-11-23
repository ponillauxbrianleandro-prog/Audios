#!/usr/bin/env python3
"""Mascota del canal Río Puratense: un libro viviente extremadamente gordo, acostado, con 4 patas.

Diseño (doc. «Personajes»): cuerpo = libro horizontal; tapa inferior = panza; bloque de páginas muy grueso;
tapa superior = lomo/torso con esquinas metálicas y una pata peluda en vez de la mano; 2 ojos negros tipo canica
integrados en el canto de las páginas (frente); 4 patas negras tipo stickman, robustas, bajo la tapa inferior; sin cola.
Vista de tres cuartos (nunca perfil plano). draw(pose) -> imagen RGBA lista para componer.

  python3 mascota.py HOJA.png      hoja de poses para revisar el diseño
"""
import math
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SS = 3                                    # supersampling
GRANATE = (122, 36, 52); GRANATE_OSC = (78, 22, 36); GRANATE_CLARO = (160, 58, 70)
ORO = (196, 168, 74); ORO_OSC = (128, 104, 40)
PAPEL = (236, 222, 186); PAPEL_OSC = (190, 172, 132); LINEA = (150, 128, 92)
NEGRO = (22, 18, 20)


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _poly_grad(img, pts, c0, c1, axis=1):
    """Polígono con degradado lineal (c0 arriba/izquierda -> c1 abajo/derecha) para dar volumen."""
    w, h = img.size
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    g = np.linspace(0, 1, h if axis == 1 else w)
    col = np.zeros((h, w, 3), np.uint8)
    for k in range(3):
        v = c0[k] + (c1[k] - c0[k]) * g
        col[:, :, k] = v[:, None] if axis == 1 else v[None, :]
    img.paste(Image.fromarray(col, "RGB"), (0, 0), m)


def draw(pose=None, size=(640, 480)):
    """pose: dict con
         rot   grados (0 = de pie sobre las patas, 180 = de espaldas),
         bob   desplazamiento vertical (px), lean = inclina el frente (grados, + = hocico abajo),
         leg   fase de caminata 0..1 (None = quieta), look = (-1..1, -1..1) mirada,
         squash 1.0 = normal, blink 0..1, mad 0..1 (enojo: ceño y temblor), flutter 0..1 (hojas)."""
    p = dict(rot=0, bob=0, lean=0, leg=None, look=(0, 0), squash=1.0, blink=0, mad=0, flutter=0, spread=0)
    p.update(pose or {})
    W, H = size[0] * SS, size[1] * SS
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cx, cy = W * 0.5, H * 0.56 + p["bob"] * SS
    s = SS * size[0] / 640.0
    sq = p["squash"]

    # --- capa del cuerpo (se rota entera) ---
    body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(body)

    def P(x, y):                                 # coordenadas del cuerpo (centro de la panza = 0,0)
        return (cx + x * s, cy + y * s * sq)

    # sombra de contacto (solo si está de pie)
    if abs(p["rot"]) < 60:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([cx - 230 * s, cy + 150 * s, cx + 230 * s, cy + 205 * s], fill=(0, 0, 0, 110))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12 * SS)))

    # patas (4): dos delanteras visibles, dos traseras más atrás y oscuras; stickman gordas
    def pata(x, y0, fase, atras):
        a = 0 if p["leg"] is None else math.sin((p["leg"] + fase) * 2 * math.pi) * 24
        lift = 0 if p["leg"] is None else max(0, math.sin((p["leg"] + fase) * 2 * math.pi)) * 18
        x1 = x + a * 0.8 + p["spread"] * (1 if x > 0 else -1) * 30
        y1 = y0 + 62 - lift
        col = (50, 44, 46) if atras else NEGRO
        w = 15 if atras else 18
        d.line([P(x, y0), P(x1, y0 + 30), P(x1 + a * 0.2, y1)], fill=col, width=int(w * s), joint="curve")
        r = (w * 0.62) * s
        q = P(x1 + a * 0.2, y1)
        d.ellipse([q[0] - r * 1.3, q[1] - r * 0.7, q[0] + r * 1.3, q[1] + r * 0.7], fill=col)      # pie redondo
    pata(-120, 118, 0.5, True); pata(150, 112, 0.0, True)
    # --- tapa inferior (panza) ---
    _poly_grad(body, [P(-250, 90), P(205, 90), P(250, 128), P(-205, 128)], GRANATE_CLARO, GRANATE_OSC)
    # canto inferior de la panza más oscuro (volumen)
    d.polygon([P(-205, 128), P(250, 128), P(250, 142), P(-205, 142)], fill=GRANATE_OSC)
    pata(-190, 130, 0.0, False); pata(205, 134, 0.5, False)

    # --- bloque de páginas (muy grueso): frente con ojos + lateral derecho ---
    _poly_grad(body, [P(-250, -70), P(205, -70), P(205, 90), P(-250, 90)], PAPEL, PAPEL_OSC)           # frente
    _poly_grad(body, [P(205, -70), P(250, -108), P(250, 128 - 38), P(205, 90)], PAPEL_OSC, (150, 132, 98))  # lateral
    for i in range(1, 15):                                                                          # hojas: líneas finas, onduladas
        y = -70 + i * (160 / 15) + (math.sin(i * 1.7 + p["flutter"] * 6) * 2.2 * p["flutter"])
        d.line([P(-250, y), P(205, y)], fill=LINEA + (200,), width=max(1, int(1.4 * s)))
        d.line([P(205, y), P(250, y - 38 * (1 - (i / 15) * 0.0))], fill=(120, 104, 74), width=max(1, int(1.2 * s)))
    # lomo (izquierda) con grosor
    _poly_grad(body, [P(-290, -90), P(-250, -70), P(-250, 142), P(-290, 120)], GRANATE_OSC, GRANATE, axis=0)
    # --- tapa superior ---
    _poly_grad(body, [P(-290, -90), P(215, -90), P(262, -132), P(-250, -132)], GRANATE_CLARO, GRANATE, axis=1)
    _poly_grad(body, [P(215, -90), P(262, -132), P(262, -108), P(250, -108)], GRANATE, GRANATE_OSC)
    # canto frontal de la tapa (grosor) que apoya sobre las páginas: elimina el hueco
    _poly_grad(body, [P(-290, -90), P(215, -90), P(207, -64), P(-250, -64)], GRANATE, GRANATE_OSC)
    d.polygon([P(215, -90), P(262, -132), P(262, -108), P(207, -64)], fill=GRANATE_OSC)
    d.polygon([P(-250, -132), P(262, -132), P(262, -124), P(-250, -124)], fill=GRANATE_CLARO)
    # esquinas metálicas + remache
    for cxy, tri in (((-262, -112), [(-290, -90), (-250, -132), (-262, -90)]), ((236, -111), [(215, -90), (262, -132), (232, -90)])):
        d.polygon([P(*q) for q in tri], fill=ORO)
        d.line([P(*tri[0]), P(*tri[1])], fill=ORO_OSC, width=int(2 * s))
        d.ellipse([P(cxy[0] - 5, cxy[1] - 5), P(cxy[0] + 5, cxy[1] + 5)], fill=ORO_OSC)
    # emblema: pata peluda (en lugar de la mano del diario) — almohadilla + 4 deditos
    ex, ey = -20, -112
    d.ellipse([P(ex - 34, ey - 12), P(ex + 34, ey + 12)], fill=ORO)
    for dx, dy in ((-34, -3), (-12, -13), (12, -13), (34, -3)):
        d.ellipse([P(ex + dx - 9, ey + dy - 5), P(ex + dx + 9, ey + dy + 5)], fill=ORO)
    d.ellipse([P(ex - 16, ey - 4), P(ex + 16, ey + 8)], fill=ORO_OSC)

    # --- ojos: dos canicas pequeñas integradas en el canto de las páginas ---
    lx, ly = p["look"]
    for ex2 in (-95, 40):
        c = P(ex2, 8)
        r = 22 * s
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([c[0] - r * 1.25, c[1] - r * 1.1, c[0] + r * 1.25, c[1] + r * 1.3], fill=(90, 70, 40, 130))
        body.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3 * SS)))
        d = ImageDraw.Draw(body)
        ry = r * (1 - p["blink"] * 0.9)
        d.ellipse([c[0] - r, c[1] - ry, c[0] + r, c[1] + ry], fill=NEGRO)
        hx, hy = c[0] + lx * r * 0.25 - r * 0.32, c[1] + ly * r * 0.2 - ry * 0.4
        if p["blink"] < 0.6:
            d.ellipse([hx - r * 0.26, hy - r * 0.26, hx + r * 0.26, hy + r * 0.26], fill=(255, 255, 255))
        if p["mad"] > 0:                                   # ceño: cuña en la parte superior
            d.polygon([(c[0] - r * 1.5, c[1] - r * 1.5 - p["mad"] * 4 * s * (-1 if ex2 < 0 else 1) * 0),
                       (c[0] + r * 1.5, c[1] - r * 1.5), (c[0] + r * 1.5 * (1 if ex2 < 0 else -1), c[1] - r * 0.15 * p["mad"] - 0 * r)],
                      fill=PAPEL)
            d.line([(c[0] - r * 1.3, c[1] - r * (1.2 - 0.5 * p["mad"]) * (1 if ex2 < 0 else 0.5)),
                    (c[0] + r * 1.3, c[1] - r * (0.5 if ex2 < 0 else 1.2) * (1 - 0.0))], fill=NEGRO, width=int(5 * s))

    # rotación + inclinación del cuerpo entero
    ang = p["rot"] + p["lean"]
    body = body.rotate(-ang, resample=Image.BICUBIC, center=(cx, cy))
    img.alpha_composite(body)
    return img.resize(size, Image.LANCZOS)


POSES = [
    ("sentado", dict(lean=-6, look=(0.7, 0.2))),
    ("olfatea", dict(lean=7, look=(0.8, 0.9), bob=4)),
    ("camina A", dict(leg=0.0, bob=-3)),
    ("camina B", dict(leg=0.5, bob=3)),
    ("salta", dict(lean=-14, bob=-70, spread=1, look=(0, -1))),
    ("de espaldas", dict(rot=180, bob=-30, spread=1, blink=0.6)),
    ("enojado", dict(mad=1, lean=4, flutter=1, squash=0.97)),
    ("parpadea", dict(blink=1, lean=-3)),
]


def sheet(path):
    cols = 4
    cw, ch = 560, 440
    S = Image.new("RGB", (cols * cw, 2 * ch), (60, 84, 70))
    for i, (n, pz) in enumerate(POSES):
        im = draw(pz, (cw, ch))
        S.paste(im, ((i % cols) * cw, (i // cols) * ch), im)
        ImageDraw.Draw(S).text(((i % cols) * cw + 10, (i // cols) * ch + 8), n, fill=(255, 255, 255))
    S.save(path)


if __name__ == "__main__":
    sheet(sys.argv[1] if len(sys.argv) > 1 else "mascota_hoja.png")
