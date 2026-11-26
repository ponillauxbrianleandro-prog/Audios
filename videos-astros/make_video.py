"""Genera un video: python make_video.py jupiter|saturno|neptuno|marte [--frames t1,t2,..] [--out dir]"""
import sys, os, math, subprocess, datetime as dt, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import multiprocessing as mp
from render_lib import *
import worlds as Wd
import scene as Sc
import astro

FPS = 30; T_TOTAL = 36.0
T_B0, T_B1 = 18.4, 20.2      # disolvencia esfera -> escena interior
T_LAND = 27.0                # fin del descenso
OUT_W, OUT_H = 1080, 1920
SC = OUT_W / W

def zoomw(t):
    x = min(max(t / T_B0, 0.0), 1.0)
    return x ** 2.0

def wr(a): return (a + 360) % 360

# ----------------------------------------------------------------------------- configuración
EPOCH = dt.datetime(2026, 11, 26, 0, 0, 0, tzinfo=astro.UTC)
CFG = {}

CFG["jupiter"] = dict(
    title="JÚPITER", sub="con Io y Europa", planet="jupiter", moon="io", moon2="europa", target="planet",
    epoch=EPOCH, rate=(18.0, 5.0), view=(4, 55), R0=125, Rend=5200, rings=False,
    albedo=Wd.jupiter_albedo, moon_albedo=Wd.io_albedo, moon2_albedo=Wd.rock_albedo_factory((0.75, 0.68, 0.58), 3),
    moon_rd=0.085, moon2_rd=0.07, p_atmo=(0.95, 0.65, 0.40), p_halo=0.07, halo_col=(0.95, 0.62, 0.35),
    obs_lat=12.0, sun_target=-6.0, aim="moon", alt_end=3000.0, alt_note="nubes", fx_col=(1.0, 0.72, 0.4), fx_k=0.7,
    moon_scale=3.5,
    world=dict(ground="jup", zenith=(0.006, 0.008, 0.035), horizon=(0.80, 0.46, 0.24), night_k=0.12, sun_col=(1.0, 0.8, 0.55), sun_glow=0.55,
               haze_low=0.22, haze_high=0.03, star_haze=0.0, star_k=1.0, star_day=1.0, mw=1.0, fog=(0.82, 0.50, 0.30), fog_d=260e3,
               fog_alt=True, sun_px=2.0, ridges=[]),
    shear=0.02, glabel="NUBES DE AMONÍACO")

CFG["saturno"] = dict(
    title="SATURNO", sub="rumbo a Titán", planet="saturno", moon="titan", moon2=None, target="moon",
    epoch=EPOCH, rate=(60.0, 6.0), view=(22, 50), R0=96, Rend=5200, rings=True,
    albedo=Wd.saturn_albedo, moon_albedo=Wd.titan_albedo, moon2_albedo=None, moon_rd=0.11, moon2_rd=0.0,
    p_atmo=(0.9, 0.8, 0.55), p_halo=0.03, halo_col=(0.9, 0.75, 0.5), m_atmo=(1.0, 0.55, 0.15), m_halo=0.055, m_halo_col=(1.0, 0.5, 0.12),
    obs_lat=18.0, sun_target=12.0, aim="planet", alt_end=1.6, alt_note="lago de metano", fx_col=(1.0, 0.55, 0.2), fx_k=0.9,
    world=dict(ground="lake", zenith=(0.020, 0.010, 0.004), horizon=(0.70, 0.36, 0.12), night_k=0.35, sun_col=(1.0, 0.6, 0.25), sun_glow=0.25,
               haze_low=0.55, haze_high=0.05, star_haze=0.55, star_k=0.8, star_day=0.6, mw=0.6, fog=(0.55, 0.28, 0.10), fog_d=9000.0,
               sun_px=1.5, lake_col=(0.020, 0.010, 0.006), lake_refl=0.85,
               ridges=[(95, 1.0, (0.18, 0.08, 0.035), 1, 0), (46, 0.5, (0.09, 0.04, 0.02), 2, 300)]),
    glabel="NEBLINA DE TITÁN")

CFG["neptuno"] = dict(
    title="NEPTUNO", sub="rumbo a Tritón", planet="neptuno", moon="triton", moon2=None, target="moon",
    epoch=EPOCH, rate=(70.0, 8.0), view=(14, 50), R0=120, Rend=5200, rings=False,
    albedo=Wd.neptune_albedo, moon_albedo=Wd.triton_albedo, moon2_albedo=None, moon_rd=0.13, moon2_rd=0.0,
    p_atmo=(0.4, 0.6, 1.0), p_halo=0.06, halo_col=(0.3, 0.5, 1.0), m_atmo=(0.7, 0.6, 0.8), m_halo=0.02, m_halo_col=(0.6, 0.55, 0.8),
    obs_lat=20.0, sun_target=9.0, aim="planet", alt_end=1.6, alt_note="llanura de hielo", fx_col=(0.7, 0.7, 1.0), fx_k=0.35,
    world=dict(ground="ice", zenith=(0.0, 0.0, 0.004), horizon=(0.10, 0.10, 0.22), night_k=0.55, sun_col=(1.0, 0.95, 0.9), sun_glow=0.18,
               haze_low=0.10, haze_high=0.01, star_haze=0.0, star_k=1.15, star_day=0.0, mw=1.0, fog=(0.30, 0.26, 0.34), fog_d=30000.0,
               sun_px=1.5, ridges=[(40, 1.0, (0.20, 0.17, 0.2), 3, 120)]),
    glabel="NITRÓGENO HELADO")

CFG["marte"] = dict(
    title="MARTE", sub="con Fobos y Deimos", planet="marte", moon="fobos", moon2="deimos", target="planet",
    epoch=EPOCH, rate=(30.0, 6.0), view=(10, 55), R0=125, Rend=5200, rings=False,
    albedo=Wd.mars_albedo, moon_albedo=Wd.rock_albedo_factory((0.55, 0.5, 0.46), 5), moon2_albedo=Wd.rock_albedo_factory((0.6, 0.52, 0.45), 9),
    moon_rd=0.075, moon2_rd=0.05, p_atmo=(0.8, 0.5, 0.35), p_halo=0.03, halo_col=(0.9, 0.55, 0.35),
    obs_lat=-8.0, sun_target=2.0, aim="moon", alt_end=2.0, alt_note="superficie", fx_col=(1.0, 0.55, 0.28), fx_k=0.9,
    moon_scale=9.0,
    world=dict(ground="mars", zenith=(0.030, 0.050, 0.120), horizon=(0.72, 0.42, 0.28), night_k=0.12, sun_col=(1.0, 0.82, 0.62), sun_glow=0.5,
               haze_low=0.40, haze_high=0.03, star_haze=0.25, star_k=1.0, star_day=1.0, mw=1.0, fog=(0.62, 0.36, 0.25), fog_d=14000.0,
               sun_px=2.0, blue_sun=True,
               ridges=[(55, 1.0, (0.22, 0.12, 0.09), 4, 0), (28, 0.55, (0.12, 0.07, 0.055), 5, 200)]),
    glabel="DESIERTO MARCIANO")

MOON_KM = {m: astro.MOONS[m]["R"] for m in astro.MOONS}

# ----------------------------------------------------------------------------- estado por video
class State:
    def __init__(self, name):
        self.name = name; c = self.c = CFG[name]
        self.planet = c["planet"]; self.P = astro.PLANETS[self.planet]; self.p = astro.pole(self.planet)
        self.rate = c["rate"]
        self.view = astro.make_view(self.planet, c["epoch"], *c["view"])   # fija durante todo el video
        self.f_eff = c["Rend"] * 1.012
        self.target_R_km = astro.MOONS[c["moon"]]["R"] if c["target"] == "moon" else self.P["R"]
        self.setup_observer()

    def simtime(self, t):
        a, b = self.rate
        sec = 60.0 * (a * min(t, T_LAND) + b * max(t - T_LAND, 0))
        return self.c["epoch"] + dt.timedelta(seconds=sec)

    # --- observador en la superficie / nubes
    def up_at(self, ts, lat, lon):
        c = self.c; p = self.p
        if c["moon"] and c["target"] == "moon":
            m = -astro.unit(astro.moon_pos(c["moon"], ts, c["M0"]))
            q = np.cross(p, m); q = astro.unit(q)
            return math.cos(lat) * (math.cos(lon) * m + math.sin(lon) * q) + math.sin(lat) * p
        N = astro.unit(np.cross([0, 0, 1.0], p)); Q = np.cross(p, N)
        psi = lon + astro.rot_W(self.planet, ts)
        return math.cos(lat) * (math.cos(psi) * N + math.sin(psi) * Q) + math.sin(lat) * p

    def sun_el(self, ts, lat, lon):
        s, _ = astro.sun_dir(self.planet, ts)
        return math.degrees(math.asin(np.clip(s @ self.up_at(ts, lat, lon), -1, 1)))

    def setup_observer(self):
        c = self.c; lat = math.radians(c["obs_lat"]); t27 = self.simtime(T_LAND); t33 = self.simtime(T_LAND + 6)
        best = None
        m0s = [None] if c["target"] == "planet" and False else [c.get("M0")]
        if c["target"] == "moon" or True:
            m0cands = np.arange(0, 360, 6.0) if c["target"] == "moon" else [None]
            for M0 in m0cands:
                c["M0"] = M0
                for lon_d in np.arange(-70, 70.1, 5) if c["target"] == "moon" else np.arange(0, 360, 2.0):
                    lon = math.radians(lon_d)
                    el27 = self.sun_el(t27, lat, lon)
                    err = abs(el27 - c["sun_target"])
                    if c["target"] == "moon":
                        up = self.up_at(t33, lat, lon); m = astro.moon_pos(c["moon"], t33, M0)
                        dpl = astro.unit(-m); pel = math.degrees(math.asin(np.clip(dpl @ up, -1, 1)))
                        err += abs(pel - 42) * 0.8
                        # sol descendiendo de día para ver la sombra: preferir sol a la izquierda de Saturno
                    else:
                        el27b = self.sun_el(self.simtime(T_LAND + 3), lat, lon)
                        err += 0 if el27b < el27 else 40   # poniéndose
                    if best is None or err < best[0]: best = (err, M0, lon)
            c["M0"] = best[1]; self.lon = best[2]
        self.lat = lat
        if c["target"] != "moon":
            # lunas: buscar fase para que la luna principal quede alta a los 33 s
            bm = None
            r, u, v = self.view; t4 = self.simtime(4.0)
            for M0 in np.arange(0, 360, 3.0):
                mn = c["moon"]; astro.MOONS[mn]["M0"] = M0
                up = self.up_at(t33, self.lat, self.lon)
                d = astro.unit(astro.moon_pos(mn, t33)); el = math.degrees(math.asin(np.clip(d @ up, -1, 1)))
                err = abs(el - 32)
                m4 = disp_pos(astro.moon_pos(mn, t4), self.P["R"]); x4, z4 = m4 @ r, m4 @ v
                err += 25 * max(0.0, 1.45 - abs(x4)) + (30 if (z4 < 0 and abs(x4) < 1.3) else 0)
                if bm is None or err < bm[0]: bm = (err, M0)
            astro.MOONS[c["moon"]]["M0"] = bm[1]
        print(f"[{self.name}] M0={c['moon']}:{astro.MOONS[c['moon']]['M0']}  lon_obs={math.degrees(self.lon):.1f}°  sol@27s={self.sun_el(t27, self.lat, self.lon):.1f}°")

    def frame_at(self, ts):
        up = self.up_at(ts, self.lat, self.lon)
        return Sc.observer_frame(up, self.p)

    def moon_vec(self, name, ts):
        m0 = self.c["M0"] if (name == self.c["moon"] and self.c["target"] == "moon") else None
        return astro.moon_pos(name, ts, m0)

    def sky_bodies(self, ts):
        c = self.c; frame = self.frame_at(ts); s, sd = astro.sun_dir(self.planet, ts)
        E, N, U = frame; out = []
        if c["target"] == "moon":
            m = self.moon_vec(c["moon"], ts); obs = m   # observador sobre la luna (≈ centro de la luna)
            dpl = astro.unit(-m); dist = np.linalg.norm(m)
            W_pl = astro.rot_W(self.planet, ts)
            alb = {"saturno": Wd.saturn_albedo, "neptuno": Wd.neptune_albedo}[self.planet]
            out.append(dict(dir=dpl, R=self.P["R"] / dist, sun=s, pole=self.p, W=W_pl, albedo=alb, rings=(self.planet == "saturno"),
                            atmo=c["p_atmo"], atmo_k=0.6, halo=0.0 if self.planet == "saturno" else 0.03, haze=False, sun_k=1.0))
        else:
            for nm, key in ((c["moon"], "moon_albedo"), (c["moon2"], "moon2_albedo")):
                if not nm: continue
                m = self.moon_vec(nm, ts); up = frame[2]
                # posición desde el observador (en la superficie del planeta) – paralaje incluido
                obs = self.P["R"] * up; v = m - obs; dist = np.linalg.norm(v); d = v / dist
                lockW = math.atan2(self.p @ np.cross(astro.unit(np.cross([0, 0, 1.0], self.p)), -astro.unit(m)), astro.unit(np.cross([0, 0, 1.0], self.p)) @ -astro.unit(m))
                out.append(dict(dir=d, R=astro.MOONS[nm]["R"] * c.get("moon_scale", 3.0) / dist, sun=s, pole=self.p, W=lockW, albedo=c[key], haze=False))
        return out, s, frame

# ----------------------------------------------------------------------------- render de un frame
def comp(a, b, w):
    return a * (1 - w) + b * w

def disp_pos(vec_km, Rp_km):
    v = np.asarray(vec_km) / Rp_km; mg = np.linalg.norm(v)
    mgd = 1 + 0.55 * math.sqrt(max(mg - 1, 0)); return v * (mgd / mg)

def render_float(S, t):
    c = S.c; ts = S.simtime(t); r, u, v = S.view
    s, sd = astro.sun_dir(S.planet, ts)
    Lv = np.array([s @ r, s @ u, s @ v])
    out = None
    # --------- fase A: esfera
    if t < T_B1:
        w_zoom = zoomw(t)
        Rp0 = c["R0"]
        if c["target"] == "planet":
            Rp_px = Rp0 * (c["Rend"] / Rp0) ** w_zoom
            s_unit = Rp_px   # px por radio planetario
            Rm_t = Rp_px
            F = np.zeros(3)
            focus_px = np.array([0.0, 0.0])
        else:
            rd = c["moon_rd"]
            s0 = Rp0; s1 = c["Rend"] / rd
            s_unit = s0 * (s1 / s0) ** w_zoom
            Rm_t = rd * s_unit
        mvec = astro.moon_pos(c["moon"], ts, c["M0"]) if c["target"] == "moon" else astro.moon_pos(c["moon"], ts)
        m_d = disp_pos(mvec, S.P["R"]); mv = np.array([m_d @ r, m_d @ u, m_d @ v])
        if c["target"] == "moon":
            f = ease(np.clip((t - 3.0) / 10.0, 0, 1))
            foc = mv * f
        else:
            foc = np.zeros(3)
        w2 = ease(np.clip((t - 11.0) / (T_B0 - 11.0), 0, 1))
        R_big = Rm_t if c["target"] == "moon" else s_unit
        dy = w2 * (R_big - 0.1 * H)
        ctr = lambda vec: (W / 2 + (vec[0] - foc[0]) * s_unit, H * 0.5 - (vec[1] - foc[1]) * s_unit + dy)
        # cielo estrellado: deriva lenta
        ang = 0.012 * t
        cam = (r * math.cos(ang) + u * math.sin(ang), u * math.cos(ang) - r * math.sin(ang), -v)
        img = space_background(cam, 52, 1.0, 0.9)
        bodies = []
        pc = ctr(np.zeros(3)); Rp_px_d = s_unit
        pb = SphereBody(c["albedo"], (S.p @ r, S.p @ u, S.p @ v), 0.0, atmo=c["p_atmo"], atmo_k=0.8, halo=c["p_halo"], halo_col=c["halo_col"],
                        wrap=0.14 if S.planet in ("jupiter", "saturno", "neptuno") else 0.08, limb=0.55, sun=1.05)
        pb.lon_shift = astro.lon_ref(S.p, r) - astro.rot_W(S.planet, ts)
        bodies.append(("p", pc, Rp_px_d, mv[2] * 0 + 0.0, pb))
        for nm, alb_key, rd_key in ((c["moon"], "moon_albedo", "moon_rd"), (c["moon2"], "moon2_albedo", "moon2_rd")):
            if not nm or not c.get(alb_key): continue
            mvec2 = astro.moon_pos(nm, ts, c["M0"] if (nm == c["moon"] and c["target"] == "moon") else None)
            md2 = disp_pos(mvec2, S.P["R"]); mv2 = np.array([md2 @ r, md2 @ u, md2 @ v])
            mc = ctr(mv2); rpx = c[rd_key] * s_unit
            lockW = math.atan2(S.p @ np.cross(astro.unit(np.cross([0, 0, 1.0], S.p)), -astro.unit(mvec2)), astro.unit(np.cross([0, 0, 1.0], S.p)) @ -astro.unit(mvec2))
            is_t = (nm == c["moon"] and c["target"] == "moon")
            mb = SphereBody(c[alb_key], (S.p @ r, S.p @ u, S.p @ v), 0.0, atmo=c.get("m_atmo", (0.5, 0.55, 0.7)) if is_t else (0.5, 0.55, 0.7),
                            atmo_k=0.7 if is_t else 0.2, halo=c.get("m_halo", 0.0) if is_t else 0.0,
                            halo_col=c.get("m_halo_col", (0.6, 0.6, 0.8)), wrap=0.30 if (is_t and S.planet == "saturno") else 0.06, limb=0.45, sun=1.05)
            mb.lon_shift = astro.lon_ref(S.p, r) - lockW
            bodies.append((nm, mc, rpx, mv2[2], mb))
        # orden por profundidad (z hacia el observador)
        order = sorted(bodies, key=lambda b: b[3])
        for nm, (cx, cy), R, z, body in order:
            if R < 0.6: continue
            if body.halo > 0: body.halo = max(0.016, min(body.halo, 120.0 / max(R, 1)))
            if nm == "p":
                if c["rings"]: draw_planet_with_rings(img, cx, cy, R, Lv, body, {"shear": 0})
                else: draw_sphere(img, cx, cy, R, Lv, body, {"shear": c.get("shear", 0) * ts.timestamp() / 36000.0 % 1})
            else:
                draw_sphere(img, cx, cy, max(R, 1.1), Lv, body, {})
                if c["target"] == "moon" and nm == c["moon"] and S.planet == "saturno":
                    Wd.draw_shell(img, cx, cy, R, Lv, 1.045, 0.010, (0.4, 0.55, 1.0), 0.7)
        # calcular altitud (HUD)
        Rt = Rm_t if c["target"] == "moon" else s_unit
        S.hud_dist = S.f_eff * S.target_R_km / max(Rt, 1e-3)
        S.hud_alt = max(S.hud_dist - S.target_R_km, 0.0)
        out = img
    # --------- fase B: escena interior
    outB = None
    if t >= T_B0:
        bodies, s_icrs, frame = S.sky_bodies(ts)
        alt0 = 0.012 * S.target_R_km * 1000.0; alt1 = c["alt_end"]
        tb = t - T_B0; wb = ease(min(tb / (T_LAND - T_B0), 1.0))
        alt = math.exp(lerp(math.log(alt0), math.log(alt1), wb))
        a_norm = float((math.log(alt) - math.log(alt1)) / (math.log(alt0) - math.log(alt1)))
        # cámara
        el_feat, az_feat = S.feature_dir(ts, frame, s_icrs, bodies, t)
        pitch0 = -math.atan(0.1 * H / Sc.F_B)
        p_down = lerp(pitch0, math.radians(1.0), ease(min(tb / (T_LAND - T_B0), 1.0)))
        p_up = math.radians(min(max(el_feat * 0.82, 14), 40))
        k4 = ease(np.clip((t - T_LAND) / 6.5, 0, 1))
        pitch = lerp(p_down, p_up, k4)
        yaw0 = math.radians(az_feat0(S, t) - 45); yaw1 = math.radians(az_feat)
        yaw = lerp(yaw0 + 0.02 * (t - T_B0), yaw1, k4)
        cam_xz = (0.0, 3.0 * (alt0 - alt) + max(t - T_LAND, 0) * 0.5 * alt1 * 0 + max(t - T_B0, 0) * alt1 * 0.04)
        imgB, sel = Sc.render_B(c, t, tb, alt, a_norm, yaw, pitch, frame, ts, bodies, s_icrs, cam_xz)
        S.hud_sun_el = sel; S.hud_altB = alt
        # efectos de entrada
        fk = c["fx_k"] * (smoothstep(18.8, 20.6, t) * (1 - smoothstep(22.2, 25.0, t)))
        imgB = Sc.entry_fx(imgB, t, fk, c["fx_col"])
        outB = imgB
    if out is None: res = outB
    elif outB is None: res = out
    else:
        wd = float(smoothstep(T_B0, T_B1, t)); res = comp(out, outB, wd)
        # destello en la transición
        res = res + (math.sin(math.pi * wd) ** 2) * 0.10 * np.array(c["fx_col"], np.float32) * c["fx_k"]
    # fundido inicial y final
    fade = float(smoothstep(0, 1.2, t) * (1 - smoothstep(T_TOTAL - 1.0, T_TOTAL, t)))
    return res * fade, ts

def az_feat0(S, t):
    return S._az0

def _feature_dir(self, ts, frame, s_icrs, bodies, t):
    """elevación y azimut (°) del objeto protagonista a los 33 s"""
    if not hasattr(self, "_feat"):
        t33 = self.simtime(T_LAND + 6)
        fr = self.frame_at(t33); bds, s33, _ = self.sky_bodies(t33)
        if self.c["aim"] == "planet": d = bds[0]["dir"]
        else: d = bds[0]["dir"]
        l = Sc.local_of(d, fr)
        el = math.degrees(math.asin(np.clip(l[1], -1, 1))); az = math.degrees(math.atan2(l[0], l[2]))
        self._feat = (el, az); self._az0 = az
    return self._feat
State.feature_dir = _feature_dir

# ----------------------------------------------------------------------------- HUD
FONTS = {}
def font(size, bold=False, mono=True):
    k = (size, bold, mono)
    if k not in FONTS:
        p = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if (mono and bold) else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf" if mono else "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        FONTS[k] = ImageFont.truetype(p, size)
    return FONTS[k]

def spaced(draw, xy, text, f, fill, sp=4, anchor="l", shadow=True):
    w = sum(draw.textlength(ch, font=f) + sp for ch in text) - sp
    x, y = xy
    if anchor == "m": x -= w / 2
    elif anchor == "r": x -= w
    for ch in text:
        if shadow: draw.text((x + 2, y + 2), ch, font=f, fill=(0, 0, 0, 160))
        draw.text((x, y), ch, font=f, fill=fill)
        x += draw.textlength(ch, font=f) + sp

def fmt_km(x):
    if x >= 1e6: return f"{x/1e6:,.2f} M km".replace(",", " ")
    if x >= 100: return f"{x:,.0f} km".replace(",", " ")
    if x >= 1: return f"{x:,.1f} km".replace(",", " ")
    return f"{x*1000:,.0f} m".replace(",", " ")

def stage_of(t):
    if t < 9: return "APROXIMACIÓN"
    if t < T_B0 + 0.6: return "ACERCAMIENTO"
    if t < T_LAND: return "ENTRADA ATMOSFÉRICA" if t < 24 else "DESCENSO"
    return "VISTA DEL CIELO"

def hud(S, img_arr, t, ts, speed):
    c = S.c
    im = Image.fromarray(img_arr).resize((OUT_W, OUT_H), Image.LANCZOS).convert("RGBA")
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    # degradados para legibilidad
    for y in range(0, 330):
        d.line([(0, y), (OUT_W, y)], fill=(0, 0, 0, int(150 * (1 - y / 330) ** 1.6)))
    for y in range(OUT_H - 440, OUT_H):
        d.line([(0, y), (OUT_W, y)], fill=(0, 0, 0, int(165 * ((y - (OUT_H - 440)) / 440) ** 1.5)))
    white = (255, 255, 255, 245); soft = (190, 215, 255, 230)
    spaced(d, (OUT_W / 2, 52), "HORA UNIVERSAL · UTC", font(26), soft, 6, "m")
    day = ts.strftime("%Y-%m-%d"); clk = ts.strftime("%H:%M:%S")
    spaced(d, (OUT_W / 2, 92), f"{day}  {clk}", font(66, True), white, 0, "m")
    spaced(d, (OUT_W / 2, 198), c["title"] + "  ·  " + c["sub"].upper(), font(32, True, False), (255, 214, 150, 235), 5, "m")
    # telemetría
    fb = font(30, False); x0 = 70; y = OUT_H - 330
    if t < T_B0 + 1.0:
        alt = getattr(S, "hud_alt", 0); dist = getattr(S, "hud_dist", 0)
        rows = [("DISTANCIA", fmt_km(dist)), ("ALTITUD", fmt_km(alt)), ("VELOCIDAD", f"{speed:,.1f} km/s".replace(",", " "))]
    else:
        alt = getattr(S, "hud_altB", 1.0) / 1000.0; el = getattr(S, "hud_sun_el", 0)
        rows = [("ALTITUD", fmt_km(alt)), ("ELEV. SOL", f"{el:+.1f}°"), ("VELOCIDAD", f"{speed:,.2f} km/s".replace(",", " "))]
    _, sd = astro.sun_dir(S.planet, ts)
    rows.append(("SOL", f"{sd:.2f} UA · LUZ A LA TIERRA {astro.earth_light_minutes(S.planet, ts):.0f} min"))
    for k, val in rows:
        spaced(d, (x0, y), k, font(24), soft, 4); spaced(d, (x0 + 250, y - 2), val, fb, white, 0); y += 56
    spaced(d, (OUT_W / 2, OUT_H - 440 + 12), stage_of(t), font(40, True, False), white, 8, "m")
    spaced(d, (OUT_W / 2, OUT_H - 70), "ESCALA ORBITAL COMPRIMIDA · LUNAS AMPLIADAS" if t < T_B0 else (f"LUNAS AMPLIADAS ×{c.get('moon_scale', 3):g}" if c["target"] == "planet" else ""), font(20), (170, 185, 210, 190), 3, "m")
    return Image.alpha_composite(im, ov).convert("RGB")

_S = None
def init_worker(name):
    global _S
    _S = State(name)

def work(args):
    i, t, speed = args
    S = _S
    f, ts = render_float(S, t)
    arr = post(f, seed=i)
    return i, hud(S, arr, t, ts, speed).tobytes()

def speed_of(S, t):
    """velocidad radial (km/s) de la sonda a partir de la variación de distancia y del reloj simulado"""
    return None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("name"); ap.add_argument("--frames", default=""); ap.add_argument("--out", default="salida")
    ap.add_argument("--fps", type=int, default=FPS); ap.add_argument("--jobs", type=int, default=4); ap.add_argument("--noaudio", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    S = State(a.name)
    # precalcular velocidad (km/s) desde la distancia vs tiempo simulado
    n = int(T_TOTAL * a.fps)
    ts_list = [i / a.fps for i in range(n)]
    alts = []
    for t in ts_list:
        w = zoomw(t)
        if S.c["target"] == "planet": Rt = S.c["R0"] * (S.c["Rend"] / S.c["R0"]) ** w
        else:
            s0 = S.c["R0"]; s1 = S.c["Rend"] / S.c["moon_rd"]; Rt = S.c["moon_rd"] * s0 * (s1 / s0) ** w
        alt0 = 0.012 * S.target_R_km
        if t < T_B0: alts.append(S.f_eff * S.target_R_km / Rt - S.target_R_km)
        else:
            wb = ease(min((t - T_B0) / (T_LAND - T_B0), 1.0))
            alts.append(math.exp(lerp(math.log(alt0), math.log(S.c["alt_end"] / 1000.0), wb)))
    speeds = []
    for i, t in enumerate(ts_list):
        j = min(i + 1, n - 1); k = max(i - 1, 0)
        dts = (S.simtime(ts_list[j]) - S.simtime(ts_list[k])).total_seconds() or 1
        speeds.append(abs(alts[j] - alts[k]) / dts)
    if a.frames:
        for tt in [float(x) for x in a.frames.split(",")]:
            S2 = State(a.name); i = int(tt * a.fps)
            f, ts = render_float(S2, tt); arr = post(f, seed=i)
            hud(S2, arr, tt, ts, speeds[min(i, n - 1)]).save(os.path.join(a.out, f"{a.name}_{tt:05.1f}.png"))
        return
    vid = os.path.join(a.out, f"{a.name}.mp4"); tmp = vid + ".noaudio.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OUT_W}x{OUT_H}", "-r", str(a.fps), "-i", "-",
                           "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-movflags", "+faststart", tmp], stdin=subprocess.PIPE)
    jobs = [(i, ts_list[i], speeds[i]) for i in range(n)]
    with mp.Pool(a.jobs, initializer=init_worker, initargs=(a.name,)) as pool:
        for k, (i, buf) in enumerate(pool.imap(work, jobs, chunksize=2)):
            ff.stdin.write(buf)
            if k % 60 == 0: print(f"{a.name}: {k}/{n}", flush=True)
    ff.stdin.close(); ff.wait()
    if not a.noaudio:
        import audio
        wav = os.path.join(a.out, f"{a.name}.wav"); audio.make(a.name, wav, T_TOTAL)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", vid], check=True)
        os.remove(tmp); os.remove(wav)
    else:
        os.replace(tmp, vid)
    print("listo", vid)

if __name__ == "__main__":
    main()
