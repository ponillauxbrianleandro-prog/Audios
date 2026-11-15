"""Composición de cada fotograma: mundo + flora + animales + óptica de cámara."""
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import world
import plants
import creature
from util import fbm, smoothstep, lerp

LIB = None
SCN = None
MIST = None


def _pyr(sp):
    lv = [(sp["rgb"], sp["a"])]
    while min(lv[-1][1].shape) > 6:
        lv.append((cv2.pyrDown(lv[-1][0]), cv2.pyrDown(lv[-1][1])))
    sp["pyr"] = lv


def setup(keepouts=()):
    """Carga el mundo y reparte la vegetación de forma determinista."""
    global LIB, SCN, MIST
    world.load()
    LIB = plants.library()
    for k in LIB:
        for sp in LIB[k]:
            _pyr(sp)
    MIST = fbm((256, 1024), 2.4, 77)
    rng = np.random.default_rng(2024)
    n = 700000
    X = rng.uniform(-128, 128, n)
    Z = rng.uniform(1.0, 495, n)
    m = world.MAPS[0]
    tx = ((X - world.GX0) / world.GRES).astype(int)
    tz = ((Z - world.GZ0) / world.GRES).astype(int)
    wet, veg, tone, dist = (m[tz, tx, i] for i in range(4))
    u = rng.uniform(0, 1, n)
    clump = cv2.resize(fbm((512, 512), 1.8, 5), (m.shape[1], m.shape[0]))[tz, tx]
    kinds = np.full(n, -1)
    near = Z < 170
    kinds[(dist > -0.45) & (dist < 2.4) & (clump > 0.53) & (u < 0.34) & near] = 0                 # colas de caballo
    kinds[(dist > 1.6) & (dist < 34) & (veg > 0.47) & (u < 0.016) & (Z < 130)] = 1                 # helechos
    kinds[(dist > 4.0) & (dist < 70) & (veg > 0.45) & (u > 0.9950) & (Z < 200)] = 2                # matas
    kinds[(dist > 7.0) & (clump * 0.5 + veg * 0.6 > 0.60) & (u > 0.50) & (u < 0.50 + 0.016 + 0.02 * (Z > 110)) & (Z > 24)] = 3   # árboles
    kinds[(dist > 0.3) & (u > 0.25) & (u < 0.2535) & (Z < 90)] = 4                                # rocas
    sel = kinds >= 0
    for (kx, kz, kr) in keepouts:
        sel &= ((X - kx) ** 2 + (Z - kz) ** 2) > kr * kr
    names = ["horsetail", "fern", "shrub", "tree", "rock"]
    SCN = dict(X=X[sel], Z=Z[sel], kind=kinds[sel], var=rng.integers(0, 6, sel.sum()),
               sc=rng.uniform(0.45, 1.2, sel.sum()), flip=rng.uniform(0, 1, sel.sum()) < 0.5,
               ph=rng.uniform(0, 6.28, sel.sum()), dist=dist[sel], names=names)
    return SCN


def _coc(cam, z, zf, ap):
    return np.minimum(ap * cam.f * np.abs(1.0 / np.maximum(z, 0.05) - 1.0 / zf), 14.0 * cam.W / 1920)


def _put(dst, rgb, a, x0, y0, dst_a=None):
    H, W = dst.shape[:2]
    h, w = a.shape
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    if xa >= xb or ya >= yb:
        return
    aa = a[ya - y0:yb - y0, xa - x0:xb - x0, None]
    d = dst[ya:yb, xa:xb]
    d *= (1 - aa)
    d += rgb[ya - y0:yb - y0, xa - x0:xb - x0]
    if dst_a is not None:
        da = dst_a[ya:yb, xa:xb]
        da *= (1 - aa[..., 0])
        da += aa[..., 0]


def _fog(rgb, a, z, fogd):
    f = 1 - np.exp(-z * fogd / 380.0)
    return rgb * (1 - f) + world.FOG_COL * a[..., None] * f


def _soft(rgb, a, sig):
    if sig < 0.35:
        return rgb, a, 0
    p = int(np.ceil(sig * 2.5))
    rgb = cv2.copyMakeBorder(rgb, p, p, p, p, cv2.BORDER_CONSTANT, value=0)
    a = cv2.copyMakeBorder(a, p, p, p, p, cv2.BORDER_CONSTANT, value=0)
    return cv2.GaussianBlur(rgb, (0, 0), sig), cv2.GaussianBlur(a, (0, 0), sig), p


def _plant_image(sp, target_h, shear, flip):
    """Escala (con mipmap) e inclina por el viento."""
    h0 = sp["a"].shape[0]
    s = target_h / h0
    L = int(np.clip(np.floor(-np.log2(max(s, 1e-6))), 0, len(sp["pyr"]) - 1))
    rgb, a = sp["pyr"][L]
    s2 = s * (2 ** L)
    h, w = a.shape
    th, tw = max(1, int(round(h * s2))), max(1, int(round(w * s2)))
    pad = int(abs(shear) * th) + 1
    M = np.array([[s2 * (-1 if flip else 1), -shear, (tw if flip else 0) + pad + shear * th], [0, s2, 0]], np.float32)
    rgb2 = cv2.warpAffine(rgb, M, (tw + 2 * pad, th), flags=cv2.INTER_LINEAR)
    a2 = cv2.warpAffine(a, M, (tw + 2 * pad, th), flags=cv2.INTER_LINEAR)
    return rgb2, a2


def frame(shot, t, W=1920, H=1080):
    """shot: dict con cam(t)->Camera, animals(t)->lista, weather, focus(t), aperture."""
    k = W / 1920.0
    cam = shot["cam"](t, W, H)
    wx = shot.get("weather", {})
    fogd = wx.get("fog", 1.0)
    zf = shot["focus"](t)
    ap = shot.get("aperture", 0.004)
    bg = world.sky(cam, t, wx)
    cinf = float(_coc(cam, 1e9, zf, ap))
    if cinf > 0.4:
        bg = cv2.GaussianBlur(bg, (0, 0), cinf)

    # ---- animales (se dibujan antes para tener sombras y reflejos)
    items = []
    shadow = np.zeros((H, W), np.float32)
    contact = np.zeros((H, W), np.float32)
    for an in shot["animals"](t):
        spr = creature.render(an["spec"], cam, an["pos"], an["heading"], an["pose"], ss=an.get("ss", 1.6))
        P, R = spr["shadow"]
        z_an = spr["zc"]
        tmp = np.zeros((H, W), np.float32)
        tmp2 = np.zeros((H, W), np.float32)
        G = P - world.SUN * (P[:, 1] / world.SUN[1])[:, None]
        G[:, 1] = 0
        u, v, zc = cam.project(G)
        for i in range(len(P)):
            if zc[i] < 0.3:
                continue
            rx = R[i] * cam.f / zc[i] * 1.1
            ry = max(0.6, R[i] * cam.f * cam.pos[1] / zc[i] ** 2 * 1.5)
            if 0 <= u[i] < W and 0 <= v[i] < H:
                cv2.ellipse(tmp, (int(u[i] * 16), int(v[i] * 16)), (int(rx * 16) + 1, int(ry * 16) + 1), 0, 0, 360, 1.0, -1, cv2.LINE_AA, 4)
        lowm = (P[:, 1] - R) < 0.10 * an["spec"]["scale"]
        G2 = P[lowm].copy()
        G2[:, 1] = 0
        u2, v2, z2 = cam.project(G2)
        R2 = R[lowm]
        for i in range(len(G2)):
            if z2[i] < 0.3 or not (0 <= u2[i] < W and 0 <= v2[i] < H):
                continue
            rx = R2[i] * cam.f / z2[i] * 1.5
            ry = max(0.6, R2[i] * cam.f * cam.pos[1] / z2[i] ** 2 * 2.2)
            cv2.ellipse(tmp2, (int(u2[i] * 16), int(v2[i] * 16)), (int(rx * 16) + 1, int(ry * 16) + 1), 0, 0, 360, 1.0, -1, cv2.LINE_AA, 4)
        sg = max(0.8, 0.030 * an["spec"]["scale"] ** 0.5 * cam.f / z_an)
        shadow = np.maximum(shadow, cv2.GaussianBlur(tmp, (0, 0), sg) * 0.72)
        contact = np.maximum(contact, cv2.GaussianBlur(tmp2, (0, 0), sg * 0.5) * 0.55)
        items.append((z_an, "animal", spr))

    # ---- vegetación visible
    S = SCN
    u, v, zc = cam.project(np.stack([S["X"], np.zeros_like(S["X"]), S["Z"]], 1))
    vis = (zc > 0.8) & (u > -0.2 * W) & (u < 1.2 * W)
    idx = np.nonzero(vis)[0]
    refl = np.zeros((H, W, 3), np.float32)
    refl_a = np.zeros((H, W), np.float32)
    pshadow = np.zeros((H, W), np.float32)
    wind = wx.get("wind", 1.0)
    for i in idx:
        name = S["names"][S["kind"][i]]
        lst = LIB[name]
        sp = lst[S["var"][i] % len(lst)]
        th = sp["a"].shape[0] / sp["ppm"] * S["sc"][i] * cam.f / zc[i]
        if th < 2.0 or v[i] - th > H or v[i] < -H:
            continue
        items.append((zc[i], "plant", (i, sp, th, name)))
    items.sort(key=lambda it: -it[0])

    draws = []
    for z, kind, d in items:
        sig = float(_coc(cam, z, zf, ap))
        if kind == "plant":
            i, sp, th, name = d
            amp = {"horsetail": 0.030, "fern": 0.022, "shrub": 0.014, "tree": 0.008, "rock": 0.0}[name]
            sh = amp * wind * (np.sin(t * 1.3 + S["ph"][i]) + 0.5 * np.sin(t * 2.9 + 1.7 * S["ph"][i])) if z < 90 else 0.0
            rgb, a = _plant_image(sp, th, sh, bool(S["flip"][i]))
            hh, ww = a.shape
            x0, y0 = int(round(u[i] - ww / 2)), int(round(v[i] - hh + max(1, 0.02 * hh)))
            rgbf = _fog(rgb, a, z, fogd)
            if z < 120 and name != "rock" or (name == "rock" and z < 60):
                rx = max(2, int(ww * (0.22 if name != "tree" else 0.30)))
                ry = max(1, int(rx * cam.pos[1] / z * 1.3))
                cv2.ellipse(pshadow, (int(u[i] + rx * 0.45), int(v[i])), (rx, ry), 0, 0, 360, 0.5 if name != "tree" else 0.62, -1, cv2.LINE_AA)
            if S["dist"][i] < 9 and z < 260:
                _put(refl, rgbf[::-1] * 0.9, a[::-1], x0, int(round(v[i])), refl_a)
            draws.append((z, rgbf, a, x0, y0, sig))
        else:
            spr = d
            rgb, a = spr["rgb"], spr["a"]
            x0, y0 = int(round(spr["x0"])), int(round(spr["y0"]))
            rgbf = _fog(rgb, a, z, fogd)
            _put(refl, rgbf[::-1] * 0.9, a[::-1], x0, int(round(2 * spr["base_y"] - y0 - a.shape[0])), refl_a)
            draws.append((z, rgbf, a, x0, y0, sig))

    pshadow = cv2.GaussianBlur(pshadow, (0, 0), 5 * k)
    shadow_all = np.clip(np.maximum(shadow, pshadow * 0.8) + contact, 0, 0.92)
    refl_rgba = np.dstack([refl, refl_a])
    img, (y0g, tz) = world.ground(cam, t, bg, refl_rgba, shadow_all, wx, shot.get("ripples", lambda t: ())(t))

    # desenfoque del suelo según la distancia (profundidad de campo)
    cg = _coc(cam, tz[:, 0], zf, ap)
    if cg.max() > 0.5:
        sub = img[y0g:]
        b1 = cv2.GaussianBlur(sub, (0, 0), 2.5 * k)
        b2 = cv2.GaussianBlur(sub, (0, 0), 7.0 * k)
        w1 = np.clip(cg / (2.5 * k), 0, 1)[:, None, None]
        w2 = np.clip((cg - 2.5 * k) / (4.5 * k), 0, 1)[:, None, None]
        img[y0g:] = lerp(lerp(sub, b1, w1), b2, w2)

    # ---- bruma baja del amanecer (antes de lo que está cerca)
    def mist():
        rows = np.arange(H, dtype=np.float32)[:, None]
        band = np.exp(-((rows - cam.vh - 10 * k) / (0.012 * cam.f + 14 * k)) ** 2)
        mx = (np.arange(W, dtype=np.float32)[None, :] / k * 0.35 + cam.yaw * 900 + t * 6.0) + np.zeros((H, 1), np.float32)
        my = (rows / k * 0.5 + t * 0.8) + np.zeros((1, W), np.float32)
        n = cv2.remap(MIST, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        a = (band * (0.25 + 0.75 * n) * wx.get("mist", 0.5))[..., None]
        img[:] = img * (1 - a) + world.FOG_COL * 1.03 * a

    misted = False
    for z, rgbf, a, x0, y0, sig in draws:
        if not misted and z < 70:
            mist()
            misted = True
        rgb2, a2, p = _soft(rgbf, a, sig)
        _put(img, rgb2, a2, x0 - p, y0 - p)
    if not misted:
        mist()

    # ---- motas en el aire (polvo, esporas, insectos diminutos)
    rng = np.random.default_rng(99)
    nm = 22
    base = np.column_stack([rng.uniform(-10, 10, nm), rng.uniform(0.2, 2.2, nm), rng.uniform(2.5, 22, nm)])
    ph = rng.uniform(0, 6.28, (nm, 3))
    dx = cam.pos[0] + np.sin(cam.yaw) * 10
    dz = cam.pos[2] + np.cos(cam.yaw) * 10
    pts = base + np.column_stack([dx + 0.5 * np.sin(t * 0.4 + ph[:, 0]) + 0.12 * t, 0.25 * np.sin(t * 0.7 + ph[:, 1]), dz - 10 + 0.4 * np.sin(t * 0.3 + ph[:, 2])])
    mu, mv, mz = cam.project(pts)
    lay = np.zeros((H, W), np.float32)
    for i in range(nm):
        if mz[i] > 1 and 0 <= mu[i] < W and 0 <= mv[i] < H:
            r = np.clip(0.006 * cam.f / mz[i], 0.8, 5 * k) + float(_coc(cam, mz[i], zf, ap)) * 0.5
            cv2.circle(lay, (int(mu[i] * 16), int(mv[i] * 16)), int(r * 16), float(0.11 / (1 + r * 0.25)), -1, cv2.LINE_AA, 4)
    lay = cv2.GaussianBlur(lay, (0, 0), 1.2 * k)
    img += lay[..., None] * np.array([1.0, 0.98, 0.9], np.float32) * wx.get("motes", 1.0)
    return post(img, t, k)


_VIG = {}


def post(img, t, k):
    H, W = img.shape[:2]
    img = np.clip(img, 0, 4)
    img = cv2.GaussianBlur(img, (0, 0), 0.55 * k)                 # suavidad de lente
    hi = np.clip(img - 0.78, 0, None)
    img = img + cv2.GaussianBlur(hi, (0, 0), 22 * k) * 0.55        # halo de altas luces
    lum = img @ np.array([0.25, 0.62, 0.13], np.float32)
    img = lum[..., None] + (img - lum[..., None]) * 0.90
    img = img * np.array([0.975, 1.0, 1.035], np.float32)          # gradación fría
    img = np.clip(img, 0, 1)
    img = img * img * (3 - 2 * img) * 0.55 + img * 0.45            # curva suave
    img = 0.035 + img * 0.955                                      # negros levantados
    if (H, W) not in _VIG:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r2 = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
        _VIG[(H, W)] = (1 - 0.13 * r2 ** 1.2)[..., None]
    img = img * _VIG[(H, W)]
    rng = np.random.default_rng(int(t * 1000) + 5)
    g = rng.normal(0, 1, (H, W)).astype(np.float32)
    g = cv2.GaussianBlur(g, (0, 0), 0.7 * k)
    img = img + g[..., None] * 0.022 * (1.1 - img.mean(-1, keepdims=True))
    return np.clip(img, 0, 1)


_FONT = {}


def subtitle(img8, text, alpha=1.0):
    """Subtítulo sobrio en el tercio inferior. img8: uint8 RGB."""
    if not text or alpha <= 0:
        return img8
    H, W = img8.shape[:2]
    size = int(46 * W / 1920)
    if size not in _FONT:
        _FONT[size] = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Medium.otf", size)
    font = _FONT[size]
    base = Image.fromarray(img8).convert("RGBA")
    lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    lines = text.split("\n")
    y = H - int(H * 0.085) - len(lines) * int(size * 1.3)
    for ln in lines:
        w = ImageDraw.Draw(lay).textlength(ln, font=font)
        x = (W - w) / 2
        ImageDraw.Draw(sh).text((x, y + 2), ln, font=font, fill=(0, 0, 0, int(205 * alpha)))
        ImageDraw.Draw(lay).text((x, y), ln, font=font, fill=(246, 246, 242, int(255 * alpha)))
        y += int(size * 1.3)
    sh = sh.filter(ImageFilter.GaussianBlur(size * 0.11))
    out = Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(base, sh), sh), lay)
    return np.asarray(out.convert("RGB"))
