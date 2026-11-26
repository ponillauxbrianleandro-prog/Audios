"""Escena 'desde dentro': suelo en perspectiva 2D + cielo real (estrellas, lunas, planeta)."""
import math
import numpy as np
from render_lib import *
import worlds as Wd
import astro

FOV_B = 48.0
F_B = (H / 2) / math.tan(math.radians(FOV_B) / 2)
MOON_SCALE = 3.0

def cam_basis_world(yaw, pitch):
    sy, cy, sp, cp = math.sin(yaw), math.cos(yaw), math.sin(pitch), math.cos(pitch)
    fwd = np.array([sy * cp, sp, cy * cp]); right = np.array([cy, 0, -sy]); up = np.array([-sy * sp, cp, -cy * sp])
    return right, up, fwd

def to_icrs(vw, frame):
    E, N, U = frame
    return vw[0] * E + vw[1] * U + vw[2] * N

def local_of(d, frame):
    E, N, U = frame
    return np.array([d @ E, d @ U, d @ N])

def observer_frame(up, p):
    E = astro.unit(np.cross(p, up)); N = np.cross(up, E)
    return E, N, up

# ------------------------------------------------------------------ suelo
def _octaves(alt, scales):
    """pesos por octava según la altitud"""
    ws = []
    for S in scales:
        r = S / max(alt, 1e-3)
        w = smoothstep(0.02, 0.2, r) * (1 - smoothstep(20, 120, r))
        ws.append(float(w))
    return ws

def height(scales, ws, hx, hz, aniso, Lxz, eps):
    g = Wd.NZ("g", 512, 512, 4, 4, 0.5, 50, True)
    h = 0; hL = 0; tot = 0
    for S, w in zip(scales, ws):
        if w < 0.02: continue
        u = hx / S; v = hz / S * aniso
        h = h + w * g(u, v); hL = hL + w * g(u + eps * Lxz[0] / S * S / S * 0 + eps * Lxz[0], v + eps * Lxz[1] * aniso)
        tot += w
    tot = max(tot, 1e-3)
    return h / tot, hL / tot

JUP_CLOUD = palette1d([(0, (0.30, 0.15, 0.09)), (0.28, (0.60, 0.34, 0.20)), (0.55, (0.84, 0.60, 0.40)), (0.8, (0.94, 0.80, 0.64)), (1, (0.98, 0.92, 0.82))])

def ground_color(kind, hx, hz, alt, dist, Lg, sun_el, fogc, fogd, t):
    """hx,hz: coordenadas (m). Lg: luz horizontal normalizada. devuelve rgb (n,3) sin niebla aplicada"""
    Lxz = (Lg[0], Lg[2])
    if kind == "jup":
        scales = [12e6, 3.4e6, 940e3, 263e3, 74e3, 20.6e3, 5.8e3, 1.6e3, 450.0, 126.0]
        ws = _octaves(alt, scales)
        h, hL = height(scales, ws, hx, hz, 3.2, Lxz, 0.01)
        h = np.clip((h - 0.5) * 1.7 + 0.5, 0, 1)
        sh = np.clip(0.85 + (h - hL) * 14, 0.4, 1.35)
        col = pal_lookup(JUP_CLOUD, h) * sh[..., None]
    elif kind == "mars":
        scales = [4000.0, 800.0, 160.0, 30.0, 6.0, 1.2]
        ws = _octaves(alt, scales)
        h, hL = height(scales, ws, hx, hz, 1.0, Lxz, 0.008)
        dune = 0.5 + 0.5 * np.sin((hz * 0.9 + hx * 0.25) / (alt * 0.9 + 3) * 3 + h * 10)
        sh = np.clip(0.8 + (h - hL) * 26, 0.3, 1.6)
        col = lerp(np.array([0.50, 0.27, 0.16], np.float32), np.array([0.82, 0.50, 0.30], np.float32), (0.65 * h + 0.35 * dune)[..., None]) * sh[..., None]
        rock = smoothstep(0.62, 0.70, Wd.NZ("mdet", 512, 512, 6, 8, 0.6, 12)(hx / (alt * 0.04 + 0.5), hz / (alt * 0.04 + 0.5)))
        col = col * (1 - 0.6 * rock[..., None])
    elif kind == "ice":
        scales = [3000.0, 600.0, 120.0, 25.0, 5.0]
        ws = _octaves(alt, scales)
        h, hL = height(scales, ws, hx, hz, 1.0, Lxz, 0.01)
        sh = np.clip(0.85 + (h - hL) * 18, 0.35, 1.5)
        ridge = 1 - np.abs(h - 0.5) * 2
        base = lerp(np.array([0.62, 0.52, 0.56], np.float32), np.array([0.95, 0.84, 0.80], np.float32), np.clip(h * 1.2, 0, 1)[..., None])
        col = base * sh[..., None] * (0.85 + 0.2 * ridge)[..., None]
        sp = smoothstep(0.78, 0.9, Wd.NZ("mdet", 512, 512, 6, 8, 0.6, 12)(hx / (alt * 0.02 + 0.2), hz / (alt * 0.02 + 0.2)))
        col = col + sp[..., None] * 0.25
    else:
        col = np.zeros(hx.shape + (3,), np.float32)
    dayk = 0.10 + 0.9 * smoothstep(-0.25, 0.25, math.sin(math.radians(sun_el)))
    return col * dayk

def reflect_ground(img, y_h, alt_rel, t):
    """reflexión de espejo del cielo sobre un lago (Titán)"""
    rows = np.arange(H)
    ys = rows[:, None] * np.ones((1, W), np.float32)
    n = Wd.NZ("rip", 512, 512, 4, 8, 0.5, 61, True)
    xs = np.arange(W)[None, :] * np.ones((H, 1), np.float32)
    depth = np.maximum(ys - y_h, 1.0)
    rip = (n(xs / 140.0 + t * 0.01, depth / 160.0) - 0.5) * (3 + depth * 0.04)
    yp = np.clip((2 * y_h - ys + rip).astype(np.int32), 0, H - 1)
    xp = np.clip((xs + rip * 2).astype(np.int32), 0, W - 1)
    return img[yp, xp]

# ------------------------------------------------------------------ escena completa
def render_B(cfg, t, tb, alt, a_norm, yaw, pitch, frame, simt, bodies, sun_icrs, cam_xz):
    """tb: tiempo local. alt (m). a_norm 1=alto 0=bajo. frame=(E,N,U). bodies: lista de dicts del cielo."""
    wc = cfg["world"]
    right, up, fwd = cam_basis_world(yaw, pitch)
    cam_icrs = (to_icrs(right, frame), to_icrs(up, frame), to_icrs(fwd, frame))
    sun_l = local_of(sun_icrs, frame); sun_el = math.degrees(math.asin(np.clip(sun_l[1], -1, 1)))
    y_h = H / 2 + F_B * math.tan(pitch)
    hw, hh = W // 2, H // 2
    # direcciones por pixel (media resolución)
    X = ((np.arange(hw) + 0.5) * 2 - W / 2) / F_B; Y = (H / 2 - (np.arange(hh) + 0.5) * 2) / F_B
    d = fwd[None, None] + X[None, :, None] * right[None, None] + Y[:, None, None] * up[None, None]
    dl = np.linalg.norm(d, axis=2)
    dy = d[..., 1] / dl
    el = np.arcsin(np.clip(dy, -1, 1))
    cos_s = (d[..., 0] * sun_l[0] + d[..., 1] * sun_l[1] + d[..., 2] * sun_l[2]) / dl
    ang_s = np.arccos(np.clip(cos_s, -1, 1))
    day = float(smoothstep(-0.30, 0.20, math.sin(math.radians(sun_el))))
    hz = lerp(wc["haze_low"], wc["haze_high"], a_norm)
    tt = np.exp(-np.maximum(el, 0) / hz)
    zen = np.array(wc["zenith"], np.float32); hor = np.array(wc["horizon"], np.float32)
    horc = hor * (wc["night_k"] + (1 - wc["night_k"]) * day)
    zenc = zen * (wc["night_k"] * 0.6 + (1 - wc["night_k"] * 0.6) * day)
    sky = zenc + (horc - zenc) * tt[..., None]
    # resplandor del sol
    sc = np.array(wc["sun_col"], np.float32)
    glow = (0.9 * np.exp(-ang_s / 0.05) + 0.5 * np.exp(-ang_s / 0.22) + 0.25 * np.exp(-ang_s / 0.7)) * smoothstep(-0.28, 0.06, sun_l[1])
    sky = sky + glow[..., None] * sc * wc["sun_glow"]
    if wc.get("blue_sun"):  # atardecer azul de Marte
        bs = np.exp(-(ang_s / 0.5) ** 2) * smoothstep(-0.30, 0.10, sun_l[1]) * (1 - smoothstep(0.25, 0.6, sun_l[1]))
        sky = sky + bs[..., None] * np.array([0.22, 0.42, 0.85], np.float32) * 1.3
    img = resize(sky, W, H) if False else resize(sky.astype(np.float32), W, H)
    # estrellas + vía láctea (visibilidad por altura y por bruma)
    hazek = wc["star_haze"] * (0.3 + 0.7 * (1 - a_norm)) if wc["star_haze"] > 0 else 0
    star_k = wc["star_k"] * (1 - 0.95 * smoothstep(-0.10, 0.45, sun_l[1]) * wc["star_day"])
    def vis(py):
        dyy = (H / 2 - py) / F_B
        el_s = np.arcsin(np.clip((math.sin(pitch) + dyy * math.cos(pitch)) / np.sqrt(1 + dyy * dyy), -1, 1))
        return np.clip(1 - hazek * np.exp(-np.maximum(el_s, 0) / 0.5) * 0 - hazek, 0.04, 1) * np.clip(1 - np.exp(-(np.maximum(el_s, 0) + 0.02) / 0.04), 0, 1)
    if star_k > 0.01:
        mw = milky_way(cam_icrs, FOV_B, wc["mw"] * star_k * 2.6 * (1 - hazek * 0.8))
        st = star_layer(cam_icrs, FOV_B, star_k * (1.15 if wc["star_haze"] == 0 else 1.8), vis=vis)
        img = img + mw + st
    # cuerpos celestes
    for b in bodies:
        dd = b["dir"]; z = dd @ cam_icrs[2]
        if z <= 0.02: continue
        px = W / 2 + F_B * (dd @ cam_icrs[0]) / z; py = H / 2 - F_B * (dd @ cam_icrs[1]) / z
        R = b["R"] * F_B / z
        if px < -R * 3 or px > W + R * 3 or py < -R * 3 or py > H + R * 3: continue
        # evitar cuerpos por debajo del horizonte
        if b.get("kind") == "sun":
            continue
        zv = -dd; uv = astro.unit(cam_icrs[1] - (cam_icrs[1] @ zv) * zv); rv = np.cross(uv, zv)
        s = b["sun"]
        L = (s @ rv, s @ uv, s @ zv)
        pole_v = (b["pole"] @ rv, b["pole"] @ uv, b["pole"] @ zv)
        lon_shift = astro.lon_ref(b["pole"], rv) - b["W"]
        body = SphereBody(b["albedo"], pole_v, lon_shift, atmo=b.get("atmo", (0.5, 0.6, 0.9)), atmo_k=b.get("atmo_k", 0.3),
                          wrap=0.05, halo=b.get("halo", 0.0), limb=0.35, ambient=0.012, sun=b.get("sun_k", 1.0))
        vf = 1.0
        if wc["star_haze"] > 0 and b.get("haze", True): vf = 1 - 0.35 * wc["star_haze"]
        tmp = np.zeros((H, W, 3), np.float32)
        if b.get("rings"): draw_planet_with_rings(tmp, px, py, R, L, body, {})
        else: draw_sphere(tmp, px, py, max(R, 1.2), L, body, {})
        img = img + tmp * vf
    # disco solar
    if sun_l[1] > -0.12:
        z = sun_icrs @ cam_icrs[2]
        if z > 0:
            px = W / 2 + F_B * (sun_icrs @ cam_icrs[0]) / z; py = H / 2 - F_B * (sun_icrs @ cam_icrs[1]) / z
            if -50 < px < W + 50 and -50 < py < H + 50:
                r = wc["sun_px"]
                x0, x1, y0, y1 = max(int(px - 60), 0), min(int(px + 60), W), max(int(py - 60), 0), min(int(py + 60), H)
                if x1 > x0 and y1 > y0:
                    XX = np.arange(x0, x1)[None, :] - px; YY = np.arange(y0, y1)[:, None] - py; D = np.sqrt(XX ** 2 + YY ** 2)
                    k = np.clip(r + 0.8 - D, 0, 1) * 4 + np.exp(-D / (r * 3)) * 0.8
                    img[y0:y1, x0:x1] += k[..., None] * sc * smoothstep(-0.12, 0.0, sun_l[1])
    # ---- suelo
    kind = wc["ground"]
    if y_h < H:
        r0 = max(int(y_h) - 2, 0)
        h0 = r0 // 2
        ys = (np.arange(h0, hh) + 0.5) * 2
        Yg = (H / 2 - ys) / F_B
        dyg = math.sin(pitch) + Yg * math.cos(pitch)
        dxg = X
        dzg = math.cos(pitch) - Yg * math.sin(pitch)
        ok = dyg < -1e-4
        dyg_s = np.where(ok, dyg, -1e-4)
        s_hit = alt / (-dyg_s)
        # rotación por yaw ya está en la base; usamos coordenadas locales de cámara -> mundo
        hxw = (dxg[None, :] * right[0] + dyg_s[:, None] * 0 + dzg[:, None] * 0)  # placeholder
        dirw_x = X[None, :] * right[0] + Yg[:, None] * up[0] + fwd[0]
        dirw_z = X[None, :] * right[2] + Yg[:, None] * up[2] + fwd[2]
        dirw_y = X[None, :] * right[1] + Yg[:, None] * up[1] + fwd[1]
        dirw_y = np.minimum(dirw_y, -1e-4)
        s_hit = alt / (-dirw_y)
        hx = cam_xz[0] + s_hit * dirw_x; hz = cam_xz[1] + s_hit * dirw_z
        dist = s_hit * np.sqrt(dirw_x ** 2 + dirw_y ** 2 + dirw_z ** 2)
        Lg = astro.unit([sun_l[0], 0.0001, sun_l[2]]) if abs(sun_l[0]) + abs(sun_l[2]) > 1e-6 else np.array([1.0, 0, 0])
        Lg = np.array([Lg[0], 0, Lg[2]])
        fogc = np.array(wc["fog"], np.float32) * (wc["night_k"] + (1 - wc["night_k"]) * day)
        if kind != "lake":
            col = ground_color(kind, hx, hz, alt, dist, Lg, sun_el, fogc, wc["fog_d"], t)
        else:
            col = np.zeros(hx.shape + (3,), np.float32)
        fd = wc["fog_d"] * (0.6 + 0.4 * alt / max(cfg["alt_end"], 1.0)) ** 0.5 if wc.get("fog_alt") else wc["fog_d"]
        fog = (1 - np.exp(-dist / fd))[..., None]
        col = col * (1 - fog) + fogc * fog
        gfull = resize(col.astype(np.float32), W, H - h0 * 2)
        ymask = np.clip((np.arange(h0 * 2, H)[:, None] + 0.5 - y_h) / 1.5, 0, 1)[..., None]
        if kind == "lake":
            refl = reflect_ground(img, y_h, a_norm, t)[h0 * 2:]
            wl = np.array(wc["lake_col"], np.float32)
            fres = np.clip(0.55 + 0.45 * smoothstep(0, 220, np.arange(h0 * 2, H)[:, None] - y_h), 0, 1)[..., None]
            gl = refl * wc["lake_refl"] + wl * (1 - 0.0)
            gl = gl * fres + wl * (1 - fres)
            gfull = gl * (1 - resize(fog.astype(np.float32), W, H - h0 * 2) * 0.5) + fogc * resize(fog.astype(np.float32), W, H - h0 * 2) * 0.5
        img[h0 * 2:] = img[h0 * 2:] * (1 - ymask) + gfull * ymask
    # ---- siluetas de horizonte
    for (amp, sc_, colr, seed, ofs) in wc.get("ridges", []):
        if y_h > H + 100 or y_h < -300: continue
        n1d = Wd.NZ("rd%d" % seed, 1024, 8, 6, 4, 0.55, 70 + seed, True)
        xs = np.arange(W) + ofs + math.degrees(yaw) * 9
        prof = n1d((xs / 1024.0 / sc_) % 1, np.full(W, 0.5, np.float32))
        top = y_h - amp * (prof ** 1.3) * (0.4 + 0.6 * (1 - a_norm))
        rows = np.arange(H)[:, None]
        m = np.clip(rows - top[None, :], 0, 1) * np.clip((y_h + 2 - rows) / 2.0 + 0.0, 0, 1)
        c = np.array(colr, np.float32) * (wc["night_k"] + (1 - wc["night_k"]) * day * 0.8 + 0.1)
        img = img * (1 - m[..., None]) + c * m[..., None]
    return img, sun_el

def entry_fx(img, t, strength, color, x_c=W / 2):
    if strength < 0.01: return img
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    n = Wd.NZ("fx", 512, 512, 5, 8, 0.55, 90, True)
    streak = n(xx / 900.0 * 6 + 0.0, yy / 4000.0 + t * 1.6)
    streak = np.clip((streak - 0.42) * 3, 0, 1)
    cone = np.exp(-(((xx - x_c) / (W * 0.55)) ** 2)) * (0.35 + 0.65 * (yy / H))
    heat = strength * (0.25 * cone + 0.55 * streak * cone)
    c = np.array(color, np.float32)
    return img + heat[..., None] * c * 1.1 + strength * 0.20 * c * np.exp(-(((yy - H * 0.55) / (H * 0.5)) ** 2))[..., None]
