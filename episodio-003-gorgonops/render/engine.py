"""Composición de cada fotograma: mundo + flora del bioma + animales + vida ambiental + óptica."""
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import world
import plants
import creature
import biomes
from util import fbm, smoothstep, lerp

LIB = None
SCNS = {}
MIST = None
_CAND = None

SWAY = dict(horsetail=0.030, horsetail_dry=0.034, horsetail_frozen=0.012, fern=0.022, fern_dry=0.024, seedfern=0.022, shrub=0.014,
            shrub_dry=0.016, tree=0.008, tree_hi=0.008, tree_autumn=0.009, tree_bare=0.006, conifer=0.006, lycopsid=0.012,
            treefern=0.014, branch=0.030, rock=0.0, log=0.0, stump=0.0, mossmat=0.0, calamites=0.012, cordaites=0.006,
            gigantopteris=0.016, ginkgo=0.007, outcrop=0.0, hongo=0.0, rama_alta=0.028, rock_moss=0.0)
TALL = ("tree", "tree_hi", "tree_autumn", "tree_bare", "conifer", "treefern", "calamites", "cordaites", "ginkgo")


def _base(name):
    return name.split("_")[0] if name.split("_")[0] in ("tree", "conifer", "treefern", "calamites", "cordaites", "ginkgo") else name


def _sway(name):
    n = SWAY.get(name)
    if n is None:
        base = name[:-5] if name.endswith("_snow") else name
        n = SWAY.get(base, 0.01) * (0.45 if name.endswith("_snow") else 1.0)
    return n
DEF_LIGHT = dict(sun=(1.00, 0.95, 0.86), amb=(0.62, 0.72, 0.86), fog=(0.80, 0.855, 0.905))


def _pyr(sp):
    lv = [(sp["rgb"], sp["a"])]
    while min(lv[-1][1].shape) > 6:
        lv.append((cv2.pyrDown(lv[-1][0]), cv2.pyrDown(lv[-1][1])))
    sp["pyr"] = lv


def setup():
    global LIB, MIST, _CAND
    if LIB is not None:
        return
    world.load()
    LIB = plants.library()
    for k in LIB:
        for sp in LIB[k]:
            _pyr(sp)
    MIST = fbm((256, 1024), 2.4, 77)
    rng = np.random.default_rng(2024)
    n = 900000
    X = rng.uniform(-128, 128, n)
    Z = rng.uniform(0.5, 495, n)
    m = world.MAPS[0]
    tx = ((X - world.GX0) / world.GRES).astype(int)
    tz = ((Z - world.GZ0) / world.GRES).astype(int)
    clump = cv2.resize(fbm((512, 512), 1.8, 5), (m.shape[1], m.shape[0]))[tz, tx]
    _CAND = dict(X=X, Z=Z, veg=m[tz, tx, 1], tone=m[tz, tx, 2], dist=m[tz, tx, 3], clump=clump)


def scene(name):
    """Vegetación del bioma, repartida de forma determinista."""
    if name in SCNS:
        return SCNS[name]
    B = biomes.BIOMES[name]
    c = _CAND
    n = len(c["X"])
    rng = np.random.default_rng(abs(hash(name)) % 100000 if False else sum(map(ord, name)))
    dist = c["dist"] + B.get("dry", 0.0) * (1.0 + 2.2 * c["tone"])
    kind = np.full(n, -1)
    names = []
    lo, hi = np.zeros(n, np.float32), np.ones(n, np.float32)
    for r in B["flora"]:
        u = rng.uniform(0, 1, n)
        ok = (kind < 0) & (u < r["p"]) & (dist > r.get("dmin", 0.3)) & (dist < r.get("dmax", 1e9))
        ok &= (c["veg"] > r.get("vmin", -1)) & (c["clump"] > r.get("cmin", -1)) & (c["clump"] < r.get("cmax", 9))
        ok &= (c["Z"] > r.get("zmin", 0)) & (c["Z"] < r.get("zmax", 1e9))
        if "box" in r:
            x0, x1, z0, z1 = r["box"]
            ok &= (c["X"] > x0) & (c["X"] < x1) & (c["Z"] > z0) & (c["Z"] < z1)
        if r["kind"] not in names:
            names.append(r["kind"])
        kind[ok] = names.index(r["kind"])
        s0, s1 = r.get("sc", (0.6, 1.2))
        lo[ok], hi[ok] = s0, s1
    sel = kind >= 0
    ns = int(sel.sum())
    S = dict(X=c["X"][sel], Z=c["Z"][sel], kind=kind[sel], var=rng.integers(0, 12, ns),
             sc=(lo[sel] + (hi[sel] - lo[sel]) * rng.uniform(0, 1, ns)), flip=rng.uniform(0, 1, ns) < 0.5,
             ph=rng.uniform(0, 6.28, ns), dist=dist[sel], names=names, r=rng.uniform(0, 1, ns))
    S['tall'] = np.array([_base(n) in TALL for n in names])[S['kind']]
    SCNS[name] = S
    return S


def _coc(cam, z, zf, ap, cap=16.0):
    return np.minimum(ap * cam.f * np.abs(1.0 / np.maximum(z, 0.05) - 1.0 / zf), cap * cam.W / 1920)


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
    if f < 0.012:
        return rgb
    return rgb * (1 - f) + world.FOG_COL * a[..., None] * f


def _fq(z, fogd):
    f = 1 - np.exp(-z * fogd / 380.0)
    return float(round(f / 0.05) * 0.05)


_BUCKETS = np.array([0.0, 0.8, 1.4, 2.2, 3.2, 4.5, 6.5, 9.0, 13.0, 18.0, 26.0, 36.0, 50.0], np.float32)


def _bucket(sig, k):
    s = sig / max(k, 1e-6)
    return float(_BUCKETS[int(np.argmin(np.abs(_BUCKETS - s)))] * k) if s >= 0.5 else 0.0


def _soft(rgb, a, sig):
    if sig < 0.35:
        return rgb, a, 0
    p = int(np.ceil(sig * 2.5))
    rgb = cv2.copyMakeBorder(rgb, p, p, p, p, cv2.BORDER_CONSTANT, value=0)
    a = cv2.copyMakeBorder(a, p, p, p, p, cv2.BORDER_CONSTANT, value=0)
    return cv2.GaussianBlur(rgb, (0, 0), sig), cv2.GaussianBlur(a, (0, 0), sig), p


def _plant_image(sp, target_h, shear, flip, u, v, W, H, margin):
    """Escala (mipmap), inclina por el viento y recorta a la parte visible.
    Devuelve rgb, alfa (float) y la esquina (x0, y0) en el cuadro; None si queda fuera."""
    h0 = sp["a"].shape[0]
    s = target_h / h0
    L = int(np.clip(np.floor(-np.log2(max(s, 1e-6))), 0, len(sp["pyr"]) - 1))
    rgb, a = sp["pyr"][L]
    s2 = s * (2 ** L)
    h, w = a.shape
    th, tw = max(1, int(round(h * s2))), max(1, int(round(w * s2)))
    pad = int(abs(shear) * th) + 1
    fw = tw + 2 * pad
    x0, y0 = int(round(u - fw / 2)), int(round(v - th + max(1, 0.02 * th)))
    xa, ya = max(x0, -margin), max(y0, -margin)
    xb, yb = min(x0 + fw, W + margin), min(y0 + th, H + margin)
    if xa >= xb or ya >= yb:
        return None
    M = np.array([[s2 * (-1 if flip else 1), -shear, (tw if flip else 0) + pad + shear * th - (xa - x0)],
                  [0, s2, -(ya - y0)]], np.float32)
    rgb2 = cv2.warpAffine(rgb, M, (xb - xa, yb - ya), flags=cv2.INTER_LINEAR).astype(np.float32) * (1 / 255.0)
    a2 = cv2.warpAffine(a, M, (xb - xa, yb - ya), flags=cv2.INTER_LINEAR).astype(np.float32) * (1 / 255.0)
    return rgb2, a2, xa, ya


def _keep_mask(shot, S):
    """Plantas que se quitan del plano: trayectos de los animales y eje cámara-sujeto."""
    key = "_keep_" + shot["biome"]
    if key not in shot:
        ok = np.ones(len(S["X"]), bool)
        for (kx, kz, kr) in shot.get("keep", ()):
            ok &= ((S["X"] - kx) ** 2 + (S["Z"] - kz) ** 2) > kr * kr
        shot[key] = ok
    return shot[key]


_FARC = {}


def _plant_items(S, vis, u, v, zc, zmul, cam, W, H, minpx=2.2):
    out = []
    for i in np.nonzero(vis)[0]:
        name = S["names"][S["kind"][i]]
        lst = LIB[name]
        sp = lst[S["var"][i] % len(lst)]
        th = sp["a"].shape[0] / sp["ppm"] * S["sc"][i] * zmul[i] * cam.f / zc[i]
        if th < minpx or v[i] - th > H or v[i] < -0.2 * H or th > 3.2 * H:
            continue
        out.append((zc[i], "plant", (u[i], v[i], sp, th, name, S["ph"][i], bool(S["flip"][i]), S["dist"][i])))
    return out


def _pass(items, cam, t, W, H, k, wx, zf, ap, ptint, tint1, fogd, wind, sink):
    """Prepara los sprites (ordenados de lejos a cerca): escala, viento, niebla, reflejo y sombra."""
    refl = np.zeros((H, W, 3), np.float32)
    refl_a = np.zeros((H, W), np.float32)
    pshadow = np.zeros((H, W), np.float32)
    gust = lambda x, zz: 1.0 + 0.9 * max(0.0, np.sin(0.05 * x + 0.03 * zz - 0.45 * t)) ** 3
    for z, kind, d in items:
        if kind == "plant":
            pu, pv, sp, th, name, ph, flip, pdist = d
            sig = float(_coc(cam, z, zf, ap, cap=16.0 if z > 1.6 else 42.0))
            amp = _sway(name)
            sh = amp * wind * gust(pu, z * 30) * (np.sin(t * 1.3 + ph) + 0.5 * np.sin(t * 2.9 + 1.7 * ph)) if z < 90 else 0.0
            r_ = _plant_image(sp, th, sh, flip, pu, pv, W, H, int(sig * 3) + 4)
            if r_ is None:
                continue
            rgb, a, x0, y0 = r_
            ww = int(min(a.shape[1], sp["a"].shape[1] / sp["a"].shape[0] * th))
            rgbf = rgb if tint1 else rgb * ptint
            fq = _fq(z, fogd)
            if z > 1.2 and ((z < 120 and name.split('_')[0] not in ("rock", "log", "branch", "mossmat", "stump", "outcrop", "hongo", "rama_alta")) or z < 50):
                rx = max(2, int(ww * (0.30 if _base(name) in TALL else 0.22)))
                ry = max(1, int(rx * cam.pos[1] / z * 1.3))
                cv2.ellipse(pshadow, (int(pu + rx * 0.45), int(pv)), (rx, ry), 0, 0, 360, 0.62 if _base(name) in TALL else 0.5, -1, cv2.LINE_AA)
            if pdist < 9 and 1.2 < z < 260:
                rf = _fog(rgbf, a, z, fogd)
                _put(refl, rf[::-1] * 0.9, a[::-1], x0, int(round(pv)), refl_a)
            sink.add(z, rgbf, a, x0, y0, sig, fq)
        else:
            spr = d
            sig = float(_coc(cam, z, zf, ap))
            rgb, a = spr["rgb"], spr["a"]
            x0, y0 = int(round(spr["x0"])), int(round(spr["y0"]))
            rf = _fog(rgb, a, z, fogd)
            _put(refl, rf[::-1] * 0.9, a[::-1], x0, int(round(2 * spr["base_y"] - y0 - a.shape[0])), refl_a)
            sink.add(z, rgb, a, x0, y0, sig, _fq(z, fogd))
    return refl, refl_a, pshadow


class _Composer:
    """Compone sprites en streaming por capas de igual desenfoque y niebla (cada capa se procesa UNA vez)."""

    def __init__(self, W, H, k):
        self.W, self.H, self.k = W, H, k
        self.acc_rgb = np.zeros((H, W, 3), np.float32)
        self.acc_a = np.zeros((H, W), np.float32)
        self.lay_rgb = np.zeros((H, W, 3), np.float32)
        self.lay_a = np.zeros((H, W), np.float32)
        self.b, self.f, self.r0, self.r1 = None, 0.0, H, 0

    def flush(self):
        H = self.H
        if self.b is not None and self.r1 > self.r0:
            sg = self.b
            pad = int(sg * 3) + 2
            r0, r1 = max(0, self.r0 - pad), min(H, self.r1 + pad)
            sr, sa = self.lay_rgb[r0:r1], self.lay_a[r0:r1]
            if sg > 0.3:
                sr, sa = cv2.GaussianBlur(sr, (0, 0), sg), cv2.GaussianBlur(sa, (0, 0), sg)
            if self.f > 0.0:
                sr = sr * (1 - self.f) + world.FOG_COL * sa[..., None] * self.f
            self.acc_rgb[r0:r1] = self.acc_rgb[r0:r1] * (1 - sa[..., None]) + sr
            self.acc_a[r0:r1] = self.acc_a[r0:r1] * (1 - sa) + sa
            self.lay_rgb[r0:r1] = 0
            self.lay_a[r0:r1] = 0
        self.b, self.r0, self.r1 = None, H, 0

    def add(self, z, rgbf, a, x0, y0, sig, fq):
        bk = _bucket(sig, self.k)
        if self.b is not None and (bk != self.b or fq != self.f):
            self.flush()
        self.b, self.f = bk, fq
        _put(self.lay_rgb, rgbf, a, x0, y0, self.lay_a)
        self.r0, self.r1 = min(self.r0, max(0, y0)), max(self.r1, min(self.H, y0 + a.shape[0]))

    def finish(self):
        self.flush()
        return self.acc_rgb, self.acc_a


def _bake_far(shot, S, keep, W, H, k, wx, ptint, tint1, fogd, wind, ZB, thin):
    """Vegetación lejana (z > ZB) dibujada una sola vez por plano, en un lienzo con margen; después solo se desplaza."""
    mm = int(0.18 * W)
    cam0 = shot["cam"](0.0, W, H)
    cb = world.Camera(W + 2 * mm, H + 2 * mm, cam0.f, cam0.pos, cam0.yaw, cam0.pitch)
    u, v, zc = cb.project(np.stack([S["X"], np.zeros_like(S["X"]), S["Z"]], 1))
    kf = np.clip(1.0 - (zc - thin[0]) / thin[1], thin[2], 1.0)
    farm = keep & (zc > ZB) & (u > -0.25 * W) & (u < W + 2 * mm + 0.25 * W) & (S["r"] < kf)
    if farm.sum() < 300:
        return dict(z0=zc, empty=True)
    items = _plant_items(S, farm, u, v, zc, 1.0 / np.sqrt(kf), cb, W + 2 * mm, H + 2 * mm)
    items.sort(key=lambda it: -it[0])
    zf0, ap = shot["focus"](0.0), shot.get("aperture", 0.004)
    comp = _Composer(W + 2 * mm, H + 2 * mm, k)
    refl, refl_a, ps = _pass(items, cb, 0.0, W + 2 * mm, H + 2 * mm, k, wx, zf0, ap, ptint, tint1, fogd, wind, comp)
    rgb, a = comp.finish()
    ps = cv2.GaussianBlur(ps, (0, 0), 5 * k)
    p_ref = np.array([cam0.pos[0] + np.sin(cam0.yaw) * 150.0, 0.0, cam0.pos[2] + np.cos(cam0.yaw) * 150.0])
    u0, v0, _ = cam0.project(p_ref)
    return dict(z0=zc, rgb=rgb, a=a, refl=refl, refl_a=refl_a, ps=ps, mm=mm, p_ref=p_ref, uv0=(float(u0), float(v0)))


def _shift_far(far, cam, W, H):
    if far.get("empty"):
        z = np.zeros((H, W), np.float32)
        return None, None, np.zeros((H, W, 3), np.float32), z, z
    u1, v1, _ = cam.project(far["p_ref"])
    dx, dy = u1 - far["uv0"][0] - far["mm"], v1 - far["uv0"][1] - far["mm"]
    M = np.array([[1, 0, dx], [0, 1, dy]], np.float32)
    wp = lambda x: cv2.warpAffine(x, M, (W, H), flags=cv2.INTER_LINEAR)
    return wp(far["rgb"]), wp(far["a"]), wp(far["refl"]), wp(far["refl_a"]), wp(far["ps"])


def frame(shot, t, W=1280, H=720):
    """shot: biome, cam(t,W,H), animals(t), focus(t), aperture, wx (sobrescribe el clima), fg, keep, ripples."""
    setup()
    k = W / 1920.0
    B = biomes.BIOMES[shot["biome"]]
    wx = dict(B.get("wx", {}))
    wx.update(shot.get("wx", {}))
    if "dry" in B:
        wx.setdefault("dry", B["dry"])
    L = dict(DEF_LIGHT)
    L.update(wx.get("light", {}))
    world.SUN_COL = np.array(L["sun"], np.float32)
    world.SKY_AMB = np.array(L["amb"], np.float32)
    world.FOG_COL = np.array(L["fog"], np.float32)
    ptint = np.array(wx.get("plant_tint", (1, 1, 1)), np.float32)
    cam = shot["cam"](t, W, H)
    fogd = wx.get("fog", 1.0)
    zf = shot["focus"](t)
    ap = shot.get("aperture", 0.004)
    bg = world.sky(cam, t, wx)
    cinf = float(_coc(cam, 1e9, zf, ap))
    if cinf > 0.4:
        bg = cv2.GaussianBlur(bg, (0, 0), cinf)

    items = []
    shadow = np.zeros((H, W), np.float32)
    contact = np.zeros((H, W), np.float32)
    for an in shot["animals"](t):
        spr = creature.render(an["spec"], cam, an["pos"], an["heading"], an["pose"], ss=an.get("ss", 1.6))
        if spr is None:
            continue
        P, R = spr["shadow"]
        z_an = spr["zc"]
        tmp = np.zeros((H, W), np.float32)
        tmp2 = np.zeros((H, W), np.float32)
        G = P - world.SUN * (P[:, 1] / world.SUN[1])[:, None]
        G[:, 1] = 0
        u, v, zc = cam.project(G)
        for i in range(len(P)):
            if zc[i] < 0.3 or not (0 <= u[i] < W and 0 <= v[i] < H):
                continue
            rx = R[i] * cam.f / zc[i] * 1.1
            ry = max(0.6, R[i] * cam.f * cam.pos[1] / zc[i] ** 2 * 1.5)
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
        sg = max(0.8, 0.030 * an["spec"]["scale"] ** 0.5 * cam.f / max(z_an, 0.3))
        sst = wx.get("shadow", 1.0)
        shadow = np.maximum(shadow, cv2.GaussianBlur(tmp, (0, 0), sg) * 0.72 * sst)
        contact = np.maximum(contact, cv2.GaussianBlur(tmp2, (0, 0), sg * 0.5) * 0.55)
        items.append((z_an, "animal", spr))

    # ---- vegetación visible (la lejana se hornea una vez por plano y se desplaza; la cercana se dibuja cada cuadro)
    S = scene(shot["biome"])
    keep = _keep_mask(shot, S)
    wind = wx.get("wind", 1.0)
    tint1 = bool(np.all(ptint == 1))
    ZB = float(B.get("bake_z", 90.0))
    NC_T, NC_S = B.get("near_clear", (5.0, 1.2))
    T0, TS, TF = B.get("thin", (30.0, 170.0, 0.10))
    far = None
    if shot.get("bake", True):
        key = (shot.get("seed", id(shot)), W)
        if key not in _FARC:
            while len(_FARC) >= 2:                          # solo se conservan las dos últimas capas lejanas (memoria)
                _FARC.pop(next(iter(_FARC)))
            _FARC[key] = _bake_far(shot, S, keep, W, H, k, wx, ptint, tint1, fogd, wind, ZB, (T0, TS, TF))
        far = _FARC[key]
    u, v, zc = cam.project(np.stack([S["X"], np.zeros_like(S["X"]), S["Z"]], 1))
    kf = np.clip(1.0 - (zc - T0) / TS, TF, 1.0)
    vis = keep & (zc > 0.35) & (u > -0.25 * W) & (u < 1.25 * W) & ~(S["tall"] & (zc < NC_T)) & ~(~S["tall"] & (zc < NC_S)) & (S["r"] < kf)
    if far is not None:
        vis &= far["z0"] <= ZB
    zmul = 1.0 / np.sqrt(kf)
    items += _plant_items(S, vis, u, v, zc, zmul, cam, W, H)
    for fgp in shot.get("fg", ()):              # plantas pegadas a la cámara
        fu, fv, fz = cam.project(np.array([fgp["x"], fgp.get("y", 0.0), fgp["z"]]))
        if fz < 0.15:
            continue
        lst = LIB[fgp["kind"]]
        sp = lst[fgp.get("var", 0) % len(lst)]
        th = sp["a"].shape[0] / sp["ppm"] * fgp.get("sc", 1.0) * cam.f / fz
        items.append((float(fz), "plant", (float(fu), float(fv), sp, th, fgp["kind"], fgp.get("ph", 0.0), fgp.get("flip", False), 99.0)))
    items.sort(key=lambda it: -it[0])
    comp = _Composer(W, H, k)
    refl, refl_a, pshadow = _pass(items, cam, t, W, H, k, wx, zf, ap, ptint, tint1, fogd, wind, comp)

    pshadow = cv2.GaussianBlur(pshadow, (0, 0), 5 * k)
    far_rgb = far_a = None
    if far is not None:
        far_rgb, far_a, f_refl, f_refl_a, f_ps = _shift_far(far, cam, W, H)
        refl = refl + f_refl * (1 - refl_a)[..., None]
        refl_a = refl_a + f_refl_a * (1 - refl_a)
        pshadow = np.maximum(pshadow, f_ps)
    pshadow = pshadow * wx.get("shadow", 1.0)
    shadow_all = np.clip(np.maximum(shadow, pshadow * 0.8) + contact, 0, 0.92)
    refl_rgba = np.dstack([refl, refl_a])
    rip = list(shot.get("ripples", lambda t: ())(t))
    img, (y0g, tz) = world.ground(cam, t, bg, refl_rgba, shadow_all, wx, rip)

    if y0g < H:
        cg = _coc(cam, tz[:, 0], zf, ap)
        if cg.max() > 0.5:
            sub = img[y0g:]
            b1 = cv2.GaussianBlur(sub, (0, 0), 2.5 * k)
            b2 = cv2.GaussianBlur(sub, (0, 0), 7.0 * k)
            w1 = np.clip(cg / (2.5 * k), 0, 1)[:, None, None]
            w2 = np.clip((cg - 2.5 * k) / (4.5 * k), 0, 1)[:, None, None]
            img[y0g:] = lerp(lerp(sub, b1, w1), b2, w2)

    if far_rgb is not None:
        img[:] = img * (1 - far_a[..., None]) + far_rgb
    ms = wx.get("mist", 0.5)
    if ms > 0:
        rows = np.arange(H, dtype=np.float32)[:, None]
        band = np.exp(-((rows - cam.vh - 10 * k) / (0.012 * cam.f + 14 * k)) ** 2)
        mx = (np.arange(W, dtype=np.float32)[None, :] / k * 0.35 + cam.yaw * 900 + t * 6.0) + np.zeros((H, 1), np.float32)
        my = (rows / k * 0.5 + t * 0.8) + np.zeros((1, W), np.float32)
        n = cv2.remap(MIST, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        a = (band * (0.25 + 0.75 * n) * ms)[..., None]
        img[:] = img * (1 - a) + world.FOG_COL * 1.03 * a
    n_rgb, n_a = comp.finish()
    img[:] = img * (1 - n_a[..., None]) + n_rgb
    life(img, cam, t, wx, zf, ap, k, shot.get("life_at"), shot)
    return post(img, t, k, wx.get("grade", {}))


def _events(t, seed, lo, hi, span, first=None):
    """Inicios de eventos espaciados (uno cada lo..hi s) que siguen activos en [t - span, t]."""
    r = np.random.default_rng(seed)
    out, tt = [], r.uniform(0.6, first or lo)
    while tt <= t:
        if tt > t - span:
            out.append(tt)
        tt += r.uniform(lo, hi)
    return out


def _soft_disc(lay, x, y, r, a):
    if r < 0.6 or not (-r < x < lay.shape[1] + r and -r < y < lay.shape[0] + r):
        return
    cv2.circle(lay, (int(x * 16), int(y * 16)), int(r * 16), float(a), -1, cv2.LINE_AA, 4)


def life(img, cam, t, wx, zf, ap, k, at=None, shot=None):
    """Vida ambiental. Los efectos grandes son EVENTOS espaciados (hojas, polvo, rachas), no continuos."""
    H, W = img.shape[:2]
    seed = int((shot or {}).get("seed", 0))
    c0 = np.array([cam.pos[0] + np.sin(cam.yaw) * 10, 0, cam.pos[2] + np.cos(cam.yaw) * 10]) if at is None else np.asarray(at, float)
    rng = np.random.default_rng(99)
    # motas / esporas
    nm = 36
    base = np.column_stack([rng.uniform(-10, 10, nm), rng.uniform(0.2, 2.2, nm), rng.uniform(-8, 12, nm)])
    ph = rng.uniform(0, 6.28, (nm, 3))
    pts = base + c0 + np.column_stack([0.5 * np.sin(t * 0.4 + ph[:, 0]) + 0.12 * t, 0.25 * np.sin(t * 0.7 + ph[:, 1]), 0.4 * np.sin(t * 0.3 + ph[:, 2])])
    mu, mv, mz = cam.project(pts)
    lay = np.zeros((H, W), np.float32)
    for i in range(nm):
        if mz[i] > 1 and 0 <= mu[i] < W and 0 <= mv[i] < H:
            r = np.clip(0.006 * cam.f / mz[i], 0.8, 5 * k) + float(_coc(cam, mz[i], zf, ap)) * 0.5
            _soft_disc(lay, mu[i], mv[i], r, 0.11 / (1 + r * 0.25))
    lay = cv2.GaussianBlur(lay, (0, 0), 1.2 * k)
    img += lay[..., None] * np.array(wx.get("mote_col", (1.0, 0.98, 0.9)), np.float32) * wx.get("motes", 1.0)

    # insectos en vuelo
    nin = int(round(wx.get("insects", 4) * 1.6))
    ndr = int(wx.get("dragonflies", 2 if nin > 0 else 0))
    for i in range(nin + ndr):
        big = i >= nin                                  # libélulas pérmicas: más grandes y rápidas
        r = np.random.default_rng(500 + i)
        cx, cz = r.uniform(-6, 6, 2)
        a1, a2, a3 = r.uniform(0.5, 1.3, 3) * (1.9 if big else 1.0)
        p1, p2, p3 = r.uniform(0, 6.28, 3)
        hofs = r.uniform(0.2, 1.2)

        def pos(tt, cx=cx, cz=cz, a1=a1, a2=a2, a3=a3, p1=p1, p2=p2, p3=p3, hofs=hofs):
            return c0 + np.array([cx + 2.6 * np.sin(a1 * tt + p1) + 0.8 * np.sin(2.7 * a2 * tt + p2),
                                  0.5 + hofs + 0.35 * np.sin(a3 * tt * 1.9 + p3),
                                  cz + 2.2 * np.sin(a2 * tt * 0.8 + p2) + 0.7 * np.sin(2.3 * a1 * tt + p3)])
        (u0, v0, z0), (u1, v1, z1) = cam.project(pos(t)), cam.project(pos(t + 0.03))
        if z0 < 1.0 or not (-50 < u0 < W + 50 and -50 < v0 < H + 50):
            continue
        s = (0.20 if big else 0.085) * cam.f / z0
        if s < 1.2:
            continue
        d = np.array([u1 - u0, v1 - v0])
        d = d / (np.linalg.norm(d) + 1e-6)
        pad = int(s * 2 + 6)
        tile = np.zeros((2 * pad, 2 * pad), np.float32)
        wing = np.zeros((2 * pad, 2 * pad), np.float32)
        c = np.array([pad, pad], float)
        cv2.line(tile, tuple(int(x * 16) for x in (c - d * s * 0.5)), tuple(int(x * 16) for x in (c + d * s * 0.5)), 1.0, max(1, int(s * 0.10)), cv2.LINE_AA, 4)
        n_ = np.array([-d[1], d[0]])
        beat = 0.55 + 0.45 * np.sin(t * 150 + i)
        for sd in (-1, 1):
            wc = c + d * s * 0.12 + n_ * sd * s * 0.42 * beat
            cv2.ellipse(wing, (int(wc[0] * 16), int(wc[1] * 16)), (int(s * 0.45 * 16), int(s * 0.13 * 16) + 8),
                        float(np.degrees(np.arctan2(n_[1], n_[0]))), 0, 360, 1.0, -1, cv2.LINE_AA, 4)
        sg = 0.5 + float(_coc(cam, z0, zf, ap)) * 0.7
        tile, wing = cv2.GaussianBlur(tile, (0, 0), sg), cv2.GaussianBlur(wing, (0, 0), sg + 0.8)
        x0, y0 = int(u0) - pad, int(v0) - pad
        _put(img, np.dstack([wing] * 3) * 0.78 * 0.22, wing * 0.22, x0, y0)
        _put(img, np.dstack([tile] * 3) * np.array([0.10, 0.09, 0.07], np.float32), tile * 0.9, x0, y0)

    # hojas: ráfagas cortas y espaciadas (cada 7-15 s caen 4-9 hojas)
    nl = int(wx.get("leaves", 0))
    if nl:
        for bi, tb in enumerate(_events(t, seed * 7 + 3, 4.5, 9.5, 9.0, wx.get('ev_first'))):
            r = np.random.default_rng(seed * 131 + int(tb * 10))
            n = int(r.integers(max(2, nl // 2 + 1), nl + 3))
            bx, bz = r.uniform(-7, 7), r.uniform(-4, 9)
            for i in range(n):
                dly, T = r.uniform(0.0, 1.6), r.uniform(4.5, 7.5)
                age = t - tb - dly
                if not (0 < age < T):
                    continue
                y0 = r.uniform(2.6, 5.2)
                ox, oz, ph_ = r.normal(0, 1.4), r.normal(0, 1.4), r.uniform(0, 6.28)
                P = c0 + np.array([bx + ox + 0.42 * age + 0.45 * np.sin(1.6 * age + ph_), y0 * (1 - age / T) ** 1.1, bz + oz + 0.25 * np.sin(1.1 * age + 2 * ph_)])
                lu, lv, lz = cam.project(P)
                if lz < 0.8 or not (0 <= lu < W and 0 <= lv < H):
                    continue
                s = 0.13 * cam.f / lz
                if s < 1.5:
                    continue
                pad = int(s + 4)
                tile = np.zeros((2 * pad, 2 * pad), np.float32)
                cv2.ellipse(tile, (pad * 16, pad * 16), (int(s * 0.5 * 16), int(s * 0.16 * (0.4 + 0.6 * abs(np.sin(age * 3 + ph_))) * 16) + 8),
                            float(np.degrees(age * 2.2 + ph_)), 0, 360, 1.0, -1, cv2.LINE_AA, 4)
                tile = cv2.GaussianBlur(tile, (0, 0), 0.6 + float(_coc(cam, lz, zf, ap)) * 0.7)
                col = np.array([0.50, 0.38, 0.16], np.float32) * (0.7 + 0.5 * ((i * 37) % 10) / 10)
                _put(img, tile[..., None] * col, tile * 0.95, int(lu) - pad, int(lv) - pad)

    # lluvia fina
    rn = wx.get("rain", 0.0)
    if rn > 0:
        r = np.random.default_rng(int(t * 24) + 7)
        lay = np.zeros((H, W), np.float32)
        for _ in range(int(900 * rn * k * k)):
            x, y = r.uniform(0, W), r.uniform(0, H)
            ln = r.uniform(14, 46) * k
            cv2.line(lay, (int(x), int(y)), (int(x - ln * 0.16), int(y + ln)), float(r.uniform(0.25, 0.8)), 1, cv2.LINE_AA)
        lay = cv2.GaussianBlur(lay, (0, 0), 0.7)
        img += lay[..., None] * 0.20 * np.array([0.9, 0.95, 1.0], np.float32)

    # polvo: velo muy tenue + nubes que cruzan de vez en cuando + polvareda tras las pisadas
    du = wx.get("dust", 0.0)
    if du > 0:
        rows = np.arange(H, dtype=np.float32)[:, None]
        cols = np.arange(W, dtype=np.float32)[None, :]
        dcol = np.array(wx.get("dust_col", (0.78, 0.70, 0.60)), np.float32)

        def cloud(a_env, cx, hy, wide, tall, off):
            mx = (cols / k * 0.22 + off) + np.zeros((H, 1), np.float32)
            my = (rows / k * 0.3 + off * 0.1) + np.zeros((1, W), np.float32)
            n = cv2.remap(MIST, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
            m = np.exp(-((rows - hy) / (H * tall)) ** 2) * np.exp(-((cols - cx) / (W * wide)) ** 2) * (0.25 + 0.75 * n)
            return (m * a_env)[..., None]
        al = np.zeros((H, W, 1), np.float32)
        al += cloud(0.07 * du, W * 0.5, cam.vh + 40 * k, 1.5, 0.45, t * 14.0 + cam.yaw * 600)
        for tb in _events(t, seed * 11 + 5, 7.0 / max(du, 0.4), 14.0 / max(du, 0.4), 6.0, wx.get('ev_first')):
            age = t - tb
            env = np.sin(np.pi * np.clip(age / 6.0, 0, 1)) ** 1.5
            r = np.random.default_rng(seed * 17 + int(tb * 10))
            al += cloud(0.40 * du * env, W * (-0.2 + 1.4 * age / 6.0) if r.uniform() < 0.5 else W * (1.2 - 1.4 * age / 6.0),
                        min(H * 0.9, cam.vh + r.uniform(30, 140) * k), 0.38, 0.12, t * 22.0 + tb)
        img[:] = img * (1 - al) + dcol * al
    if wx.get("puff", 0.0) > 0 and shot is not None:
        lay = np.zeros((H, W), np.float32)
        for an in shot.get("actors", ()):
            if not hasattr(an, "pos"):
                continue
            for n in range(4):
                ts = np.floor(t / 0.34) * 0.34 - n * 0.34
                if ts < 0:
                    continue
                p0, p1 = an.pos(ts), an.pos(ts + 0.34)
                if np.hypot(*(p1 - p0)[[0, 2]]) < 0.04 * an.spec["scale"]:
                    continue
                age = t - ts
                pu, pv, pz = cam.project(p0 + np.array([0.0, 0.02, 0.0]))
                if pz < 0.8:
                    continue
                rr = (0.10 + 0.34 * age) * an.spec["scale"] ** 0.5 * cam.f / pz
                _soft_disc(lay, pu, pv - rr * 0.35 * age, rr, 0.55 * (1 - age / 1.5) * wx["puff"])
        lay = cv2.GaussianBlur(lay, (0, 0), 3.0 * k)
        dc = np.array(wx.get("dust_col", (0.78, 0.70, 0.60)), np.float32)
        img[:] = img * (1 - lay[..., None]) + dc * lay[..., None]

    # nieve en suspensión: copos finos siempre, y rachas más densas de vez en cuando
    fl = wx.get("flurry", 0.0)
    if fl > 0:
        env = 0.25
        for tb in _events(t, seed * 13 + 9, 6.0, 12.0, 5.0, wx.get('ev_first')):
            env += 0.85 * np.sin(np.pi * np.clip((t - tb) / 5.0, 0, 1)) ** 1.5
        r = np.random.default_rng(1234)
        nfl = int(230 * fl * min(env, 1.1))
        xs, ys, sp, sz = r.uniform(0, W, 400), r.uniform(0, H, 400), r.uniform(0.5, 1.4, 400), r.uniform(0.6, 2.3, 400)
        lay = np.zeros((H, W), np.float32)
        for i in range(min(nfl, 400)):
            x = (xs[i] - 70 * t * sp[i] * k + 14 * k * np.sin(t * 1.3 + i)) % W
            y = (ys[i] + 58 * t * sp[i] * k) % H
            _soft_disc(lay, x, y, sz[i] * k, 0.85)
        lay = cv2.GaussianBlur(lay, (0, 0), 0.7 * k)
        img += lay[..., None] * np.array([0.95, 0.97, 1.0], np.float32) * 0.9


_VIG = {}


def post(img, t, k, grade=None):
    grade = grade or {}
    H, W = img.shape[:2]
    img = np.clip(img, 0, 4) * grade.get("expo", 1.0)
    img = cv2.GaussianBlur(img, (0, 0), 0.55 * max(k, 0.7))
    hi = np.clip(img - 0.78, 0, None)
    img = img + cv2.GaussianBlur(hi, (0, 0), 22 * k) * 0.55
    lum = img @ np.array([0.25, 0.62, 0.13], np.float32)
    img = lum[..., None] + (img - lum[..., None]) * 1.14 * grade.get("sat", 1.0)          # más color que la v2 (0,90)
    img = img * np.array([0.995, 1.0, 1.015], np.float32) * np.array(grade.get("tint", (1, 1, 1)), np.float32)
    img = np.clip(img, 0, 1)
    img = img * img * (3 - 2 * img) * 0.55 + img * 0.45
    img = 0.035 + img * 0.955
    if (H, W) not in _VIG:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r2 = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
        _VIG[(H, W)] = (1 - 0.13 * r2 ** 1.2)[..., None]
    img = img * _VIG[(H, W)]
    rng = np.random.default_rng(int(t * 1000) + 5)
    g = rng.normal(0, 1, (H, W)).astype(np.float32)
    g = cv2.GaussianBlur(g, (0, 0), 0.7 * max(k, 0.7))
    img = img + g[..., None] * 0.018 * (1.1 - img.mean(-1, keepdims=True))
    return np.clip(img, 0, 1)


_FONT = {}


def font(size, weight="Medium", italic=False):
    key = (size, weight, italic)
    if key not in _FONT:
        nm = ("Italic" if weight == "Regular" else weight + "Italic") if italic else weight
        _FONT[key] = ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{nm}.otf", size)
    return _FONT[key]


def subtitle(img8, text, alpha=1.0):
    """Subtítulo sobrio en el tercio inferior. img8: uint8 RGB."""
    if not text or alpha <= 0:
        return img8
    H, W = img8.shape[:2]
    size = int(46 * W / 1920)
    f = font(size)
    base = Image.fromarray(img8).convert("RGBA")
    lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    lines = text.split("\n")
    y = H - int(H * 0.085) - len(lines) * int(size * 1.3)
    for ln in lines:
        w = ImageDraw.Draw(lay).textlength(ln, font=f)
        x = (W - w) / 2
        ImageDraw.Draw(sh).text((x, y + 2), ln, font=f, fill=(0, 0, 0, int(205 * alpha)))
        ImageDraw.Draw(lay).text((x, y), ln, font=f, fill=(246, 246, 242, int(255 * alpha)))
        y += int(size * 1.3)
    sh = sh.filter(ImageFilter.GaussianBlur(size * 0.11))
    out = Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(base, sh), sh), lay)
    return np.asarray(out.convert("RGB"))
