"""Hoja de contactos de animales: todas las especies x vistas, acciones y ciclo de caminata de Vetusodon.
Uso:  python3 hoja_animales.py [salida.png]"""
import os
import sys
import time
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paletas
import animales as A

SALIDA = "/tmp/claude-0/-home-user-Audios/67bd3ee9-eab2-5673-a100-ae0a6af8a7c1/scratchpad/hoja_animales.png"
ESPECIES = ['vetusodon', 'gorgonopsio', 'diictodon', 'lystrosaurus', 'anfibio', 'libelula', 'cucaracha', 'escarabajo']
PALS = ['ambar', 'ocre', 'verde', 'violeta', 'azul', 'rojo', 'ceniza', 'ambar']


def _fit(im, cw, ch):
    k = min((cw - 8) / im.width, (ch - 22) / im.height, 1.6)
    return im.resize((max(2, int(im.width * k)), max(2, int(im.height * k))), Image.LANCZOS)


def _celda(sheet, d, im, x, y, cw, ch, bg, rotulo=''):
    fondo = Image.new('RGBA', (cw - 2, ch - 2), bg)
    sheet.alpha_composite(fondo, (x + 1, y + 1))
    im = _fit(im, cw, ch)
    sheet.alpha_composite(im, (x + (cw - im.width) // 2, y + ch - im.height - 5))
    if rotulo:
        d.text((x + 5, y + 4), rotulo, fill=(255, 255, 255, 230))


def hoja(salida=SALIDA, h_px=300):
    t0 = time.time()
    cw, ch = 330, 250
    ncol = 9
    filas_v = len(ESPECIES)
    filas_a = len(ESPECIES)
    filas_c = 4
    W = ncol * cw
    Hh = (filas_v + filas_a + filas_c) * ch + 90
    sheet = Image.new('RGBA', (W, Hh), (40, 40, 44, 255))
    d = ImageDraw.Draw(sheet)
    tiempos = []
    y = 4
    d.text((8, y), "A) especies x 6 vistas 3/4 (idle). Paleta distinta por fila.", fill=(255, 230, 160, 255))
    y += 16
    for r, esp in enumerate(ESPECIES):
        pal = paletas.PALETAS[PALS[r]]
        bg = tuple(int(v * .62) for v in pal['cielo'][1]) + (255,)
        d.text((6, y + 2), esp, fill=(255, 255, 255, 255))
        for c, v in enumerate(A.VISTAS):
            t = time.time()
            im = A.generar(esp, 'idle', .25, v, pal, 3, h_px)
            tiempos.append(time.time() - t)
            _celda(sheet, d, im, (c + 1) * cw, y, cw, ch, bg, v)
        y += ch
    d.text((8, y + 2), "B) acciones (vista alternando 3q_der / 3q_frente_izq / 3q_trasera_izq)", fill=(255, 230, 160, 255))
    y += 16
    vv = ['3q_der', '3q_izq', '3q_frente_izq', '3q_frente_der', '3q_trasera_izq']
    for r, esp in enumerate(ESPECIES):
        pal = paletas.PALETAS[PALS[(r + 3) % 7]]
        bg = tuple(int(v * .62) for v in pal['cielo'][1]) + (255,)
        d.text((6, y + 2), esp, fill=(255, 255, 255, 255))
        for c, a in enumerate(A.ESP[esp].get('acciones', ['idle'])[:8]):
            t = time.time()
            fase = {'caminar': .15, 'correr': .3, 'pelea': .55, 'escarbar': .2}.get(a, .3)
            im = A.generar(esp, a, fase, vv[c % len(vv)], pal, 5, h_px)
            tiempos.append(time.time() - t)
            _celda(sheet, d, im, (c + 1) * cw, y, cw, ch, bg, a)
        y += ch
    d.text((8, y + 2), "C) Vetusodon: ciclo de caminata 12 fotogramas (3q_izq / 3q_frente_der), via ciclo()", fill=(255, 230, 160, 255))
    y += 16
    pal = paletas.PALETAS['ambar']
    bg = tuple(int(v * .62) for v in pal['cielo'][1]) + (255,)
    for rr, (vista, n) in enumerate((('3q_izq', 12), ('3q_frente_der', 12))):
        t = time.time()
        fr = A.ciclo('vetusodon', 'caminar', vista, pal, n=n, h_px=h_px, usar_cache=False)
        tiempos.append((time.time() - t) / n)
        w0 = fr[0].width
        fw = W // 6
        for i, im in enumerate(fr):
            c, rw = i % 6, i // 6
            _celda(sheet, d, im, c * fw, y + rw * ch, fw, ch, bg, 'f%02d' % i)
        y += 2 * ch
    sheet = sheet.crop((0, 0, W, y))
    sheet.convert('RGB').save(salida)
    print("hoja:", salida, sheet.size, "t medio por sprite %.2fs, max %.2fs, total %.1fs" % (
        sum(tiempos) / len(tiempos), max(tiempos), time.time() - t0))
    return salida


if __name__ == "__main__":
    hoja(sys.argv[1] if len(sys.argv) > 1 else SALIDA)
