#!/usr/bin/env python3
"""Estilo 1 — retrato en cuadro.

Figura repintada al óleo (pincel simulado) sobre una fotografía de dominio público, dentro de
una composición de retrato clásico de la India: ventana con arco lobulado, fondo plano de color
profundo, cenefa ornamentada (hojas de Glossopteris y huesos) y cartela con nombre y fechas.

Uso: retrato.py foto.jpg salida.jpg "NOMBRE" "FECHAS" ["cita"]
"""
import math
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import pintor

GOLD = (206, 168, 84); GOLD_D = (128, 96, 40); INDIGO = (24, 22, 58); TEAL = (14, 70, 64); CREAM = (236, 224, 196); WINE = (84, 22, 36)


def font(size, serif=False, bold=False):
    names = (['DejaVuSerif-Bold.ttf', 'LiberationSerif-Bold.ttf'] if bold else ['DejaVuSerif.ttf', 'LiberationSerif-Regular.ttf']) if serif else ['Inter-Bold.ttf', 'DejaVuSans-Bold.ttf']
    import glob
    for n in names:
        hit = glob.glob(f'/usr/share/fonts/**/{n}', recursive=True)
        if hit:
            return ImageFont.truetype(hit[0], size)
    return ImageFont.load_default()


def colorear(gray, fig, cara):
    """mapa de color: piel y barba cálidas, ropa fría y oscura, fondo plano profundo"""
    g = np.asarray(gray, dtype=np.float32) / 255
    def ramp(stops):
        out = np.zeros(g.shape + (3,), dtype=np.float32)
        for (t0, c0), (t1, c1) in zip(stops[:-1], stops[1:]):
            m = ((g >= t0) & (g <= t1))[..., None]
            k = np.clip((g - t0) / (t1 - t0), 0, 1)[..., None]
            out = np.where(m, np.array(c0) + (np.array(c1) - np.array(c0)) * k, out)
        return out
    warm = ramp([(0, (20, 12, 14)), (0.25, (88, 50, 40)), (0.5, (170, 116, 86)), (0.75, (222, 186, 150)), (1.0, (250, 240, 220))])
    cool = ramp([(0, (8, 12, 18)), (0.2, (24, 38, 46)), (0.45, (58, 84, 90)), (0.75, (140, 160, 156)), (1.0, (226, 232, 220))])
    c = np.asarray(cara, dtype=np.float32)[..., None] / 255
    f = np.asarray(fig, dtype=np.float32)[..., None] / 255
    figura = warm * c + cool * (1 - c)
    H, W = g.shape
    yy = np.linspace(0, 1, H)[:, None, None]
    fondo = np.array(TEAL, dtype=np.float32) * (1.25 - yy * 0.55) + np.array([10, 4, 18]) * yy
    fondo = np.broadcast_to(fondo, (H, W, 3))
    return Image.fromarray(np.clip(figura * f + fondo * (1 - f), 0, 255).astype(np.uint8))


def arco(w, h, lobes=7):
    """ventana con arco lobulado (multifolio)"""
    m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m)
    top = int(h * 0.3)
    d.rectangle((0, top, w, h), fill=255)
    pts = [(0, top)]
    cx, R = w / 2, w / 2
    for i in range(lobes):
        a0 = math.pi - i * math.pi / lobes; a1 = math.pi - (i + 1) * math.pi / lobes
        for k in range(13):
            a = a0 + (a1 - a0) * k / 12
            bulge = 1 + 0.085 * math.sin(math.pi * k / 12)
            rise = 1.0 + 0.5 * math.sin(math.pi * (i + k / 12) / lobes) ** 3
            pts.append((cx + math.cos(a) * R * bulge * 0.985, top - math.sin(a) * top * 0.92 * rise / 1.5 * bulge))
    pts.append((w, top))
    d.polygon(pts, fill=255)
    return m


def cenefa(d, box, band, rnd):
    """cenefa: hojas de Glossopteris y huesos alternados, en dorado"""
    x0, y0, x1, y1 = box
    def hoja(cx, cy, ang, L=30):
        c, s = math.cos(ang), math.sin(ang)
        pts = [(cx - c * L, cy - s * L)]
        for t in np.linspace(0, 1, 9): pts.append((cx + c * L * (2 * t - 1) - s * math.sin(math.pi * t) * L * 0.38, cy + s * L * (2 * t - 1) + c * math.sin(math.pi * t) * L * 0.38))
        for t in np.linspace(1, 0, 9): pts.append((cx + c * L * (2 * t - 1) + s * math.sin(math.pi * t) * L * 0.38, cy + s * L * (2 * t - 1) - c * math.sin(math.pi * t) * L * 0.38))
        d.polygon(pts, fill=GOLD); d.line([(cx - c * L, cy - s * L), (cx + c * L, cy + s * L)], fill=GOLD_D, width=2)
    def hueso(cx, cy, ang, L=20):
        c, s = math.cos(ang), math.sin(ang)
        d.line([(cx - c * L, cy - s * L), (cx + c * L, cy + s * L)], fill=CREAM, width=7)
        for sg in (-1, 1):
            for o in (-1, 1): d.ellipse((cx + sg * c * L - o * s * 5 - 6, cy + sg * s * L + o * c * 5 - 6, cx + sg * c * L - o * s * 5 + 6, cy + sg * s * L + o * c * 5 + 6), fill=CREAM)
    step = 84
    for j, x in enumerate(np.arange(x0 + band / 2 + 50, x1 - band / 2 - 20, step)):
        for y in (y0 + band / 2, y1 - band / 2):
            (hoja if j % 2 == 0 else hueso)(x, y, 0.35 if j % 4 < 2 else -0.35)
    for j, y in enumerate(np.arange(y0 + band / 2 + 60, y1 - band / 2 - 30, step)):
        for x in (x0 + band / 2, x1 - band / 2):
            (hoja if j % 2 == 1 else hueso)(x, y, math.pi / 2 + (0.35 if j % 4 < 2 else -0.35))
    for (x, y) in [(x0 + band / 2, y0 + band / 2), (x1 - band / 2, y0 + band / 2), (x0 + band / 2, y1 - band / 2), (x1 - band / 2, y1 - band / 2)]:
        for k in range(8):
            a = k * math.pi / 4; d.ellipse((x + math.cos(a) * 16 - 7, y + math.sin(a) * 16 - 7, x + math.cos(a) * 16 + 7, y + math.sin(a) * 16 + 7), fill=GOLD)
        d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=WINE)


def retrato(src, nombre, fechas, cita=None, quien=None):
    rnd = random.Random(4)
    PW_, PH_ = 660, 800
    g = Image.open(src).convert('L')
    w0, h0 = g.size
    # encuadre: busto, con aire arriba
    crop = g.crop((int(w0 * 0.06), int(h0 * 0.03), int(w0 * 0.94), int(h0 * 0.03 + w0 * 0.88 * PH_ / PW_)))
    crop = crop.resize((PW_, PH_), Image.LANCZOS)
    crop = Image.fromarray(np.clip((np.asarray(crop, dtype=np.float32) - 12) * 1.12, 0, 255).astype(np.uint8))
    sx, sy = PW_ / (480 * 0.88), PH_ / (617 * (0.88 * 480 / 617) * PH_ / PW_ * 617 / 480)
    tr = lambda pts: [((x - 480 * 0.06) * PW_ / (480 * 0.88), (y - 617 * 0.03) * PW_ / (480 * 0.88)) for x, y in pts]
    fig = Image.new('L', (PW_, PH_), 0)
    ImageDraw.Draw(fig).polygon(tr([(128, 150), (150, 95), (200, 70), (262, 80), (302, 130), (312, 200), (338, 262), (348, 330), (402, 440), (480, 500), (500, 640), (30, 640), (55, 400), (100, 300), (160, 255), (138, 215)]), fill=255)
    fig = fig.filter(ImageFilter.GaussianBlur(7))
    cara = Image.new('L', (PW_, PH_), 0); dc = ImageDraw.Draw(cara)
    dc.polygon(tr([(128, 150), (150, 95), (200, 70), (262, 80), (302, 130), (310, 200), (336, 262), (345, 330), (300, 362), (240, 330), (190, 270), (140, 215)]), fill=255)
    dc.ellipse([tr([(380, 540)])[0][0], tr([(380, 540)])[0][1], tr([(500, 640)])[0][0], tr([(500, 640)])[0][1]], fill=255)
    cara = cara.filter(ImageFilter.GaussianBlur(12))
    base = colorear(crop, fig, cara)
    pintado = pintor.paint(base, [30, 15, 8, 4, 2], seed=5, mask=cara, relief=0.6)
    pintado = pintor.grade(pintado, 1.0, 0.0, 1.1, 0.2)

    # --- cuadro: ventana con arco, enjutas, cenefa y cartela
    band = 74; pad = 18
    FW, FH = PW_ + 2 * (band + pad), PH_ + 2 * (band + pad) + 96
    cuadro = Image.new('RGB', (FW, FH), INDIGO); d = ImageDraw.Draw(cuadro)
    d.rectangle((0, 0, FW - 1, FH - 1), outline=GOLD_D, width=8)
    d.rectangle((10, 10, FW - 11, FH - 11), outline=GOLD, width=3)
    cenefa(d, (14, 14, FW - 14, FH - 110), band, rnd)
    ix, iy = band + pad, band + pad
    d.rectangle((ix - 8, iy - 8, ix + PW_ + 7, iy + PH_ + 7), fill=GOLD)
    d.rectangle((ix - 4, iy - 4, ix + PW_ + 3, iy + PH_ + 3), fill=WINE)
    # enjutas con motas doradas
    sp = Image.new('RGB', (PW_, PH_), WINE); ds = ImageDraw.Draw(sp)
    for i in range(420):
        x, y = rnd.uniform(0, PW_), rnd.uniform(0, PH_ * 0.32); r = rnd.uniform(1.5, 4.5)
        ds.ellipse((x - r, y - r, x + r, y + r), fill=GOLD if i % 3 else CREAM)
    win = arco(PW_, PH_)
    sp.paste(pintado, (0, 0), win)
    edge = win.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(5))
    sp.paste(Image.new('RGB', (PW_, PH_), GOLD), (0, 0), edge)
    cuadro.paste(sp, (ix, iy))
    # cartela
    cy = FH - 100
    d.rounded_rectangle((70, cy + 6, FW - 70, cy + 84), radius=16, fill=CREAM, outline=GOLD_D, width=4)
    f1 = font(34); f2 = font(22, serif=True)
    d.text((FW / 2, cy + 34), nombre, font=f1, fill=INDIGO, anchor='mm')
    d.text((FW / 2, cy + 66), fechas, font=f2, fill=WINE, anchor='mm')
    # leve textura de pintura sobre el marco
    cuadro = pintor.paint(cuadro, [3], seed=2, relief=0.35, under=0.0, thr=(0,), jitter=0.03) if False else cuadro

    # --- lámina: el cuadro colgado en penumbra, con una cita de ejemplo
    W, H = 1920, 1080
    yy, xx = np.mgrid[0:H, 0:W]
    wall = np.zeros((H, W, 3), dtype=np.float32) + np.array([16, 22, 32])
    wall += np.exp(-(((xx - 560) / 620.0) ** 2 + ((yy - 430) / 520.0) ** 2))[..., None] * np.array([34, 40, 44])
    rs = np.random.RandomState(3)
    wall += rs.normal(0, 2.2, (H, W, 1))
    lam = Image.fromarray(np.clip(wall, 0, 255).astype(np.uint8))
    sc = 1030 / FH
    cq = cuadro.resize((int(FW * sc), int(FH * sc)), Image.LANCZOS)
    x0, y0 = 150, 25
    sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).rectangle((x0 + 18, y0 + 26, x0 + cq.width + 26, y0 + cq.height + 30), fill=200)
    lam = Image.composite(Image.new('RGB', (W, H), (2, 4, 8)), lam, sh.filter(ImageFilter.GaussianBlur(22)))
    lam.paste(cq, (x0, y0))
    d = ImageDraw.Draw(lam)
    tx = x0 + cq.width + 90
    d.text((tx, 120), 'ESTILO 1 · RETRATO EN CUADRO', font=font(30), fill=(246, 241, 228))
    d.text((tx, 164), 'Científicos fallecidos, frases célebres, hitos históricos.', font=font(20), fill=(143, 160, 180))
    if cita:
        fq = font(40, serif=True); y = 330
        words = cita.split(); line = ''
        for wd in words:
            if d.textlength(line + ' ' + wd, font=fq) > W - tx - 90:
                d.text((tx, y), line, font=fq, fill=(236, 224, 196)); y += 58; line = wd
            else:
                line = (line + ' ' + wd).strip()
        d.text((tx, y), line, font=fq, fill=(236, 224, 196)); y += 90
        d.line([(tx, y - 30), (tx + 120, y - 30)], fill=GOLD, width=4)
        d.text((tx, y), quien or nombre.title(), font=font(26), fill=GOLD)
    return lam


if __name__ == '__main__':
    src, dst, nombre, fechas = sys.argv[1:5]
    cita = sys.argv[5] if len(sys.argv) > 5 else None
    quien = sys.argv[6] if len(sys.argv) > 6 else None
    retrato(src, nombre, fechas, cita, quien).save(dst, quality=94)
    print('ok', dst)
