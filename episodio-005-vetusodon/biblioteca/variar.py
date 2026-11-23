"""Multiplicar/deformar piezas RGBA (PIL) rapidamente. Todas devuelven una PIL.Image RGBA
nueva y conservan la base de la planta en el borde inferior-centro."""
import numpy as np
import cv2
from PIL import Image


def _arr(img):
    a = np.asarray(img.convert('RGBA'), np.float32)
    al = a[..., 3:4] / 255.0
    return np.dstack([a[..., :3] * al, a[..., 3:4]])      # premultiplicado


def _img(pm):
    a = pm[..., 3:4] / 255.0
    rgb = pm[..., :3] / np.maximum(a, 1e-3)
    out = np.dstack([np.clip(rgb, 0, 255), np.clip(pm[..., 3:4], 0, 255)]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def _recorta(pm):
    ys = np.where(pm[..., 3].max(1) > 6)[0]
    xs = np.where(pm[..., 3].max(0) > 6)[0]
    if len(ys) == 0:
        return pm
    return pm[ys[0]:ys[-1] + 1, xs[0]:xs[-1] + 1]


def espejo(img):
    return img.transpose(Image.FLIP_LEFT_RIGHT)


def escala(img, sx=1.0, sy=None):
    sy = sx if sy is None else sy
    w, h = max(2, int(round(img.width * sx))), max(2, int(round(img.height * sy)))
    return img.resize((w, h), Image.LANCZOS if min(sx, sy) < 1 else Image.BICUBIC)


def inclinar(img, k=.2):
    """Cizalla horizontal: la base queda fija, la copa se desplaza k*altura."""
    pm = _arr(img)
    h, w = pm.shape[:2]
    pad = int(abs(k) * h) + 2
    M = np.float32([[1, -k, (h if k > 0 else 0) * k * 0 + (k * h if k > 0 else 0) + pad * (0 if k > 0 else 1) * 0], [0, 1, 0]])
    # x' = x - k*y + k*h  (base y=h fija); desplazar para caber
    M = np.float32([[1, -k, k * h + (pad if k < 0 else 0) * 0], [0, 1, 0]])
    ox = pad if k < 0 else 0
    # dibujamos sobre lienzo ancho centrado en la base
    W = w + 2 * pad
    M = np.float32([[1, -k, k * h + pad], [0, 1, 0]])
    out = cv2.warpAffine(pm, M, (W, h), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    # recentrar: base debe quedar en el centro
    shift = 0
    out = _recorta_centrado(out, W / 2.0 + 0)
    return _img(out)


def _recorta_centrado(pm, bx):
    ys = np.where(pm[..., 3].max(1) > 6)[0]
    xs = np.where(pm[..., 3].max(0) > 6)[0]
    if len(ys) == 0:
        return pm
    half = int(np.ceil(max(bx - xs[0], xs[-1] + 1 - bx)))
    xa, xb = int(round(bx)) - half, int(round(bx)) + half
    pl, pr = max(0, -xa), max(0, xb - pm.shape[1])
    if pl or pr:
        pm = cv2.copyMakeBorder(pm, 0, 0, pl, pr, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
        xa += pl
        xb += pl
    return pm[ys[0]:ys[-1] + 1, xa:xb]


def curvar(img, amp=.25, fase=0.0, ondas=0.0, potencia=1.8):
    """Dobla la pieza (base fija): desplazamiento horizontal creciente con la altura.
    amp en fracciones de la altura (con signo); ondas anade ondulacion sinusoidal."""
    pm = _arr(img)
    h, w = pm.shape[:2]
    pad = int(abs(amp) * h * 1.1 + ondas * h * .1) + 4
    W = w + 2 * pad
    big = cv2.copyMakeBorder(pm, 0, 0, pad, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
    yn = 1 - (np.arange(h, dtype=np.float32) + .5) / h          # 0 base -> 1 copa
    dx = amp * h * yn ** potencia + ondas * h * .05 * np.sin(yn * 6.0 + fase) * yn
    mapx = (np.arange(W, dtype=np.float32)[None, :] - dx[:, None]).astype(np.float32)
    mapy = np.tile(np.arange(h, dtype=np.float32)[:, None], (1, W))
    out = cv2.remap(big, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    return _img(_recorta_centrado(out, W / 2.0))


def rotar(img, grados):
    """Gira alrededor de la base (abajo-centro)."""
    pm = _arr(img)
    h, w = pm.shape[:2]
    pad = int(max(w, h) * .6)
    big = cv2.copyMakeBorder(pm, pad, 0, pad, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
    M = cv2.getRotationMatrix2D((pad + w / 2.0, pad + h), -grados, 1.0)
    out = cv2.warpAffine(big, M, (big.shape[1], big.shape[0]), flags=cv2.INTER_LINEAR)
    return _img(_recorta_centrado(out, pad + w / 2.0))


def _lum(rgb):
    return rgb @ np.array([.299, .587, .114], np.float32)


def tinte(img, color, fuerza=.5, conservar_luz=True):
    """Lleva los colores hacia un color dominante preservando la luminancia."""
    pm = _arr(img)
    a = pm[..., 3:4] / 255.0
    rgb = pm[..., :3] / np.maximum(a, 1e-3)
    col = np.array(color[:3], np.float32)
    L = _lum(rgb)[..., None]
    lc = max(1.0, float(_lum(col)))
    if conservar_luz:
        tgt = np.clip(col * (L / lc), 0, 255)
    else:
        tgt = col
    out = rgb * (1 - fuerza) + tgt * fuerza
    return _img(np.dstack([out * a, pm[..., 3:4]]))


def matiz(img, grados=20, sat=1.0, val=1.0):
    """Rotacion de matiz (grados) y multiplicadores de saturacion/valor."""
    a = np.asarray(img.convert('RGBA'))
    hsv = cv2.cvtColor(a[..., :3], cv2.COLOR_RGB2HSV).astype(np.float32)
    hsv[..., 0] = (hsv[..., 0] + grados / 2.0) % 180
    hsv[..., 1] = np.clip(hsv[..., 1] * sat, 0, 255)
    hsv[..., 2] = np.clip(hsv[..., 2] * val, 0, 255)
    rgb = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
    return Image.fromarray(np.dstack([rgb, a[..., 3]]), 'RGBA')


def brillo(img, k=1.0, contraste=1.0):
    pm = _arr(img)
    a = pm[..., 3:4] / 255.0
    rgb = pm[..., :3] / np.maximum(a, 1e-3)
    rgb = (rgb - 128) * contraste + 128
    return _img(np.dstack([np.clip(rgb * k, 0, 255) * a, pm[..., 3:4]]))


def desenfoque(img, r=3.0):
    """Desenfoque gaussiano con alfa premultiplicado (primer plano fuera de foco)."""
    pm = _arr(img)
    pad = int(r * 3) + 1
    pm = cv2.copyMakeBorder(pm, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
    pm = cv2.GaussianBlur(pm, (0, 0), r)
    out = _img(pm)
    return out


def bruma(img, color, k=.5, contraste=.8, sat=.8):
    """Bruma atmosferica de fondo: baja contraste/saturacion y mezcla con el color de bruma."""
    pm = _arr(img)
    a = pm[..., 3:4] / 255.0
    rgb = pm[..., :3] / np.maximum(a, 1e-3)
    L = _lum(rgb)[..., None]
    rgb = L + (rgb - L) * sat
    rgb = (rgb - 128) * contraste + 128
    rgb = rgb * (1 - k) + np.array(color[:3], np.float32) * k
    return _img(np.dstack([np.clip(rgb, 0, 255) * a, pm[..., 3:4]]))


def bruma_vertical(img, color, k_base=.0, k_alto=.5):
    """Bruma que aumenta hacia arriba (niebla pegada al suelo = base nitida)."""
    pm = _arr(img)
    h = pm.shape[0]
    a = pm[..., 3:4] / 255.0
    rgb = pm[..., :3] / np.maximum(a, 1e-3)
    t = np.linspace(k_alto, k_base, h)[:, None, None].astype(np.float32)
    rgb = rgb * (1 - t) + np.array(color[:3], np.float32) * t
    return _img(np.dstack([rgb * a, pm[..., 3:4]]))


def variante(img, rng, pal=None, fuerza_tinte=.35, espejar=True, curv=.22, esc_nu=.18, shear=.12, matiz_g=14):
    """Variante aleatoria rapida: espejo, escala no uniforme, curvado, cizalla, matiz y tinte."""
    out = img
    if espejar and rng.random() < .5:
        out = espejo(out)
    out = escala(out, 1 + rng.uniform(-esc_nu, esc_nu), 1 + rng.uniform(-esc_nu, esc_nu))
    if rng.random() < .8:
        out = curvar(out, rng.uniform(-curv, curv), rng.uniform(0, 6), rng.uniform(0, .5))
    if rng.random() < .5:
        out = inclinar(out, rng.uniform(-shear, shear))
    if matiz_g:
        out = matiz(out, rng.uniform(-matiz_g, matiz_g), rng.uniform(.9, 1.1), rng.uniform(.9, 1.1))
    if pal is not None and fuerza_tinte:
        out = tinte(out, pal['dom'], fuerza_tinte * rng.uniform(.6, 1.2))
    return out


def sombra_contacto(ancho, pal, alto=None, k=.55):
    """Elipse de sombra suave para apoyar una pieza en el suelo."""
    alto = alto or max(4, int(ancho * .12))
    W, Hh = int(ancho * 1.3), int(alto * 2.6)
    m = np.zeros((Hh, W), np.float32)
    cv2.ellipse(m, (W // 2, Hh // 2), (int(ancho * .5), int(alto)), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (0, 0), max(1.5, alto * .5)) * k
    col = np.array(pal['sombra'], np.float32) * .5
    out = np.dstack([np.tile(col, (Hh, W, 1)), m * 255]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def pegar(dest, img, x, y_base, escala_=1.0):
    """Compone img sobre dest (PIL RGBA) con la base (abajo-centro) en (x, y_base). Recorta bordes."""
    if escala_ != 1.0:
        img = escala(img, escala_)
    x0, y0 = int(round(x - img.width / 2)), int(round(y_base - img.height))
    sx0, sy0 = max(0, -x0), max(0, -y0)
    sx1, sy1 = min(img.width, dest.width - x0), min(img.height, dest.height - y0)
    if sx1 <= sx0 or sy1 <= sy0:
        return dest
    dest.alpha_composite(img.crop((sx0, sy0, sx1, sy1)), (x0 + sx0, y0 + sy0))
    return dest
