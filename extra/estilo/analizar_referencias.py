#!/usr/bin/env python3
"""Fase 0: ingenieria inversa del estilo GTA IV a partir de imagenes de referencia (no se guardan las imagenes).
Uso: python3 -I analizar_referencias.py <imagen1> <imagen2> ...   -> estilo_gta4.json + resumen en consola."""
import colorsys, json, os, sys
import numpy as np
from PIL import Image, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))


def hsv(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(-1), a.min(-1); d = mx - mn + 1e-9
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) / 6
    return h, d / (mx + 1e-9), mx


def circ_mean(h, w):
    ang = h * 2 * np.pi
    return float((np.arctan2((np.sin(ang) * w).sum(), (np.cos(ang) * w).sum()) / (2 * np.pi)) % 1)


def analizar(path):
    im = Image.open(path).convert("RGB"); im.thumbnail((480, 480))
    a = np.asarray(im).astype(np.float32) / 255
    h, s, v = hsv(a)
    lum = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
    gy, gx = np.gradient(lum); gm = np.hypot(gx, gy)
    H, W = lum.shape
    # sujeto ~ centro (saturacion/contraste) vs bordes (fondo)
    cy, cx = slice(H // 5, 4 * H // 5), slice(W // 4, 3 * W // 4)
    centro = np.zeros_like(lum, bool); centro[cy, cx] = True
    sat_c, sat_f = float(s[centro].mean()), float(s[~centro].mean())
    # niveles tonales: cuantizar luminancia y contar los que tienen >2% de pixeles
    hist, _ = np.histogram(lum, bins=32, range=(0, 1)); hist = hist / hist.sum()
    # dureza de bordes: percentil 90 del gradiente en pixeles de borde
    bordes = gm > np.percentile(gm, 85)
    dureza = float(np.percentile(gm, 97))
    densidad = float(bordes.mean())
    # sombra vs luz: tono medio de pixeles coloreados oscuros vs claros
    col = s > .18
    sombra, luz = col & (lum < np.percentile(lum[col], 30)) if col.any() else col, col & (lum > np.percentile(lum[col], 70)) if col.any() else col
    hs = circ_mean(h[sombra], s[sombra]) if sombra.any() else 0; hl = circ_mean(h[luz], s[luz]) if luz.any() else 0
    # direccion de luz: gradiente medio de luminancia
    ldir = [float(gx.mean()), float(gy.mean())]
    # paleta dominante
    q = im.quantize(8, method=Image.MEDIANCUT).convert("RGB")
    pal = ["#%02x%02x%02x" % rgb for c, rgb in sorted(q.getcolors(), reverse=True)]
    return dict(archivo=os.path.basename(path), sat_centro=round(sat_c, 3), sat_fondo=round(sat_f, 3), ratio_sat=round(sat_c / (sat_f + 1e-6), 2),
                lum_media=round(float(lum.mean()), 3), contraste=round(float(lum.std()), 3), niveles_tonales_activos=int((hist > .015).sum()),
                densidad_bordes=round(densidad, 3), dureza_p97=round(dureza, 3), tono_sombra=round(hs, 3), tono_luz=round(hl, 3),
                direccion_luz_xy=[round(x * 1000, 3) for x in ldir], paleta=pal)


if __name__ == "__main__":
    res = [analizar(p) for p in sys.argv[1:]]
    agg = {k: round(float(np.mean([r[k] for r in res])), 3) for k in ("sat_centro", "sat_fondo", "ratio_sat", "lum_media", "contraste", "niveles_tonales_activos", "densidad_bordes", "dureza_p97", "tono_sombra", "tono_luz")}
    json.dump({"promedio": agg, "imagenes": res}, open(os.path.join(AQUI, "estilo_gta4.json"), "w"), indent=1)
    print(json.dumps(agg, indent=1))
    for r in res: print(r["archivo"], r["ratio_sat"], r["niveles_tonales_activos"], r["tono_sombra"], r["tono_luz"])
