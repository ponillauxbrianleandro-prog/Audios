"""Efemérides ligeras: posiciones planetarias (elementos keplerianos JPL, 1800-2050),
lunas con órbitas circulares aproximadas, rotación IAU y geometría de vista."""
import math, datetime as dt
import numpy as np

UTC = dt.timezone.utc
J2000 = dt.datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC)
OBL = math.radians(23.43928)
AU_KM = 149597870.7
C_KM_S = 299792.458

# a, da, e, de, I, dI, L, dL, varpi, dvarpi, Omega, dOmega  (UA, grados, por siglo)
ELEMS = {
    "tierra":  (1.00000261, 0.00000562, 0.01671123, -0.00004392, -0.00001531, -0.01294668,
                100.46457166, 35999.37244981, 102.93768193, 0.32327364, 0.0, 0.0),
    "marte":   (1.52371034, 0.00001847, 0.09339410, 0.00007882, 1.84969142, -0.00813131,
                -4.55343205, 19140.30268499, -23.94362959, 0.44441088, 49.55953891, -0.29257343),
    "jupiter": (5.20288700, -0.00011607, 0.04838624, -0.00013253, 1.30439695, -0.00183714,
                34.39644051, 3034.74612775, 14.72847983, 0.21252668, 100.47390909, 0.20469106),
    "saturno": (9.53667594, -0.00125060, 0.05386179, -0.00050991, 2.48599187, 0.00193609,
                49.95424423, 1222.49362201, 92.59887831, -0.41897216, 113.66242448, -0.28867794),
    "neptuno": (30.06992276, 0.00026291, 0.00859048, 0.00005105, 1.77004347, 0.00022400,
                -55.12002969, 218.45945325, 44.96476227, -0.32241464, 131.78422574, -0.00508664),
}

# radio km, polo (AR, Dec) J2000, W0, dW/día (IAU)
PLANETS = {
    "marte":   dict(R=3389.5,  pole=(317.681, 52.887), W0=176.630, Wd=350.89198226),
    "jupiter": dict(R=69911.0, pole=(268.057, 64.495), W0=284.95,  Wd=870.5366420),
    "saturno": dict(R=58232.0, pole=(40.589, 83.537),  W0=38.90,   Wd=810.7939024),
    "neptuno": dict(R=24622.0, pole=(299.36, 43.46),   W0=249.978, Wd=541.1397757),
}
# lunas: planeta, radio, semieje km, periodo d, fase inicial (aprox.), retrógrada, inclinación órbita/ecuador
MOONS = {
    "io":     dict(parent="jupiter", R=1821.6, a=421800,  P=1.769138, M0=200.0, retro=False, inc=0.0),
    "europa": dict(parent="jupiter", R=1560.8, a=671100,  P=3.551181, M0=60.0,  retro=False, inc=0.5),
    "titan":  dict(parent="saturno", R=2574.7, a=1221870, P=15.945421, M0=250.0, retro=False, inc=0.3),
    "triton": dict(parent="neptuno", R=1353.4, a=354759,  P=5.876854, M0=140.0, retro=True, inc=23.0),
    "fobos":  dict(parent="marte",   R=11.3,   a=9376,    P=0.31891, M0=120.0, retro=False, inc=1.1),
    "deimos": dict(parent="marte",   R=6.2,    a=23458,   P=1.2624,  M0=300.0, retro=False, inc=1.8),
}

def jd(t):
    return 2451545.0 + (t - J2000).total_seconds() / 86400.0

def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)

def radec(ra, dec):
    ra, dec = math.radians(ra), math.radians(dec)
    return np.array([math.cos(dec) * math.cos(ra), math.cos(dec) * math.sin(ra), math.sin(dec)])

def ecl_to_eq(v):
    c, s = math.cos(OBL), math.sin(OBL)
    return np.array([v[0], v[1] * c - v[2] * s, v[1] * s + v[2] * c])

def helio(name, t):
    """posición heliocéntrica ecuatorial (UA)"""
    T = (jd(t) - 2451545.0) / 36525.0
    e = ELEMS[name]
    a = e[0] + e[1] * T; ec = e[2] + e[3] * T; I = math.radians(e[4] + e[5] * T)
    L = e[6] + e[7] * T; vp = e[8] + e[9] * T; Om = math.radians(e[10] + e[11] * T)
    w = math.radians(vp) - Om
    M = math.radians(((L - vp) + 180) % 360 - 180)
    E = M
    for _ in range(12):
        E -= (E - ec * math.sin(E) - M) / (1 - ec * math.cos(E))
    xp, yp = a * (math.cos(E) - ec), a * math.sqrt(1 - ec * ec) * math.sin(E)
    cw, sw, cO, sO, cI, sI = math.cos(w), math.sin(w), math.cos(Om), math.sin(Om), math.cos(I), math.sin(I)
    x = (cw * cO - sw * sO * cI) * xp + (-sw * cO - cw * sO * cI) * yp
    y = (cw * sO + sw * cO * cI) * xp + (-sw * sO + cw * cO * cI) * yp
    z = sw * sI * xp + cw * sI * yp
    return ecl_to_eq((x, y, z))

def pole(planet):
    return radec(*PLANETS[planet]["pole"])

def equator_basis(p):
    e1 = unit(np.cross([0, 0, 1.0], p)); e2 = np.cross(p, e1)
    return e1, e2

def moon_pos(name, t, m0=None):
    """posición moon-planeta en ICRS (km)"""
    m = MOONS[name]; p = pole(m["parent"]); e1, e2 = equator_basis(p)
    d = jd(t) - 2451545.0
    th = math.radians((m["M0"] if m0 is None else m0) + (-1 if m["retro"] else 1) * 360.0 * d / m["P"])
    ci, si = math.cos(math.radians(m["inc"])), math.sin(math.radians(m["inc"]))
    return m["a"] * (math.cos(th) * e1 + math.sin(th) * (ci * e2 + si * p))

def rot_W(planet, t):
    P = PLANETS[planet]
    return math.radians(P["W0"] + P["Wd"] * (jd(t) - 2451545.0))

def sun_dir(planet, t):
    h = helio(planet, t); return -h / np.linalg.norm(h), float(np.linalg.norm(h))

def earth_light_minutes(planet, t):
    return float(np.linalg.norm(helio(planet, t) - helio("tierra", t)) * AU_KM / C_KM_S / 60)

def make_view(planet, t, lat_deg, phi_deg):
    """eje de vista de la sonda: devuelve (right, up, toward_viewer) en ICRS; polo hacia arriba, sol a la derecha"""
    p = pole(planet); s, _ = sun_dir(planet, t)
    sp = s - (s @ p) * p; sp = unit(sp); q = np.cross(p, sp)
    for sg in (1, -1):
        phi, lat = math.radians(phi_deg) * sg, math.radians(lat_deg)
        v = math.cos(lat) * (math.cos(phi) * sp + math.sin(phi) * q) + math.sin(lat) * p
        u = unit(p - (p @ v) * v); r = np.cross(u, v)
        if s @ r > 0: break
    return r, u, v

def lon_ref(p, a_icrs):
    """ángulo de 'a' respecto del nodo IAU alrededor del polo"""
    N = unit(np.cross([0, 0, 1.0], p))
    return math.atan2(p @ np.cross(N, a_icrs), N @ a_icrs)

def fmt_clock(t):
    return t.strftime("%Y-%m-%d  %H:%M:%S UTC")
