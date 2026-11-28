"""Escultura SDF del vaquero: piel (torso, brazos, manos, cabeza), camisa abierta, jeans sueltos y botas.
Devuelve mallas NumPy (v, f). Sin Blender. H = tamaño de voxel (m)."""
import numpy as np
from sdf import Field, rot_from, fold_noise, smin, smax

A = lambda p: np.array(p, dtype=np.float32)
Z = A((0, 0, 1))


def lerp(a, b, t):
    return a + (b - a) * t


def torso_front_y(J, z):
    """y del frente del torso a la altura z (para colocar abdominales sobre la superficie)."""
    zs = [J["pelvis"][2], J["waist"][2], J["chest"][2]]
    ys = [J["pelvis"][1] - 0.100, J["waist"][1] - 0.088, J["chest"][1] - 0.112]
    return float(np.interp(z, zs, ys))


def sculpt_skin(J, p, h):
    pts = np.array([J[k] for k in J if not isinstance(J[k], dict)])
    lo = pts.min(0) - np.array([0.30, 0.30, 0.0]); lo[2] = J["pelvis"][2] - 0.14
    hi = pts.max(0) + np.array([0.30, 0.30, 0.30])
    F = Field(lo, hi, h)
    c, w, pel, nk, hd = J["chest"], J["waist"], J["pelvis"], J["neck"], J["head"]

    # --- tronco
    F.ecapsule(pel - A((0, 0, 0.10)), pel, (0.150, 0.100), (0.165, 0.105), 0.05)
    F.ecapsule(pel, w, (0.165, 0.105), (0.140, 0.090), 0.05)
    F.ecapsule(w, c, (0.140, 0.090), (0.178, 0.110), 0.05)
    F.ecapsule(c, c + A((0, 0, 0.13)), (0.178, 0.110), (0.150, 0.100), 0.05)
    F.ellipsoid(c + A((0, 0.005, 0.03)), (0.178, 0.112, 0.16), None, 0.04)
    # --- relieve muscular (todo fusionado)
    for sx in (-1, 1):
        # pectorales
        F.ellipsoid(c + A((sx * 0.092, -0.083, 0.072)), (0.108, 0.052, 0.074), None, 0.030)
        F.ellipsoid(c + A((sx * 0.088, -0.078, 0.040)), (0.100, 0.046, 0.050), None, 0.030)
        # pliegue bajo pectoral
        F.ellipsoid(c + A((sx * 0.095, -0.150, 0.000)), (0.115, 0.040, 0.014), None, 0.010, "sub")
        # abdominales (bloques con surco)
        for r in range(4):
            z = c[2] - 0.115 - 0.072 * r
            fy = torso_front_y(J, z) + 0.004
            F.ellipsoid(A((lerp(c[0], pel[0], (c[2] - z) / 0.5) + sx * 0.0255, fy + 0.002, z)), (0.0235, 0.026, 0.0355), None, 0.007)
        # oblicuos, serrato, dorsal ancho
        F.ellipsoid(A((w[0] + sx * 0.112, w[1] - 0.030, w[2] - 0.01)), (0.046, 0.058, 0.115), None, 0.025)
        for i in range(4):
            F.ellipsoid(A((c[0] + sx * 0.148, c[1] - 0.045 + 0.004 * i, c[2] - 0.025 - 0.036 * i)), (0.026, 0.030, 0.019), None, 0.010)
        F.ellipsoid(c + A((sx * 0.150, 0.025, -0.035)), (0.040, 0.070, 0.150), None, 0.035)
        # cresta ilíaca / línea en V
        F.ecapsule(A((pel[0] + sx * 0.050, pel[1] - 0.088, pel[2] + 0.090)), A((pel[0] + sx * 0.135, pel[1] - 0.052, pel[2] + 0.035)),
                   (0.026, 0.020), (0.030, 0.026), 0.012)
        # trapecio y cuello
        F.ecapsule(nk + A((sx * 0.03, 0.02, -0.02)), J["sh" + ("G" if sx < 0 else "F")] + A((0, 0.0, 0.05)), (0.040, 0.034), (0.050, 0.040), 0.03)
        F.ellipsoid(nk + A((sx * 0.032, -0.035, -0.015)), (0.020, 0.025, 0.075), A([[1, 0, 0], [0, 1, 0], [0, 0, 1]]), 0.015)
        # clavícula
        F.capsule(c + A((sx * 0.015, -0.095, 0.155)), J["sh" + ("G" if sx < 0 else "F")] + A((0, -0.045, 0.045)), 0.013, 0.012, 0.012)
    # surco esternal / línea alba
    F.ellipsoid(c + A((0, -0.150, 0.060)), (0.0055, 0.040, 0.085), None, 0.006, "sub")
    F.ellipsoid(A((lerp(c[0], pel[0], 0.5), torso_front_y(J, c[2] - 0.30) - 0.030, c[2] - 0.30)), (0.0045, 0.030, 0.17), None, 0.006, "sub")

    # --- brazos
    for tag, sx in (("G", -1), ("F", 1)):
        sh, el, wr = A(J["sh" + tag]), A(J["el" + tag]), A(J["wr" + tag])
        fa = (el - sh) / np.linalg.norm(el - sh)
        fb = (wr - el) / np.linalg.norm(wr - el)
        nA = A((0, -1, 0)); nB = A((0, -1, 0))
        F.ellipsoid(sh + A((sx * 0.018, 0.0, -0.022)), (0.074, 0.076, 0.098), rot_from(fa, nA), 0.03)  # deltoides
        F.capsule(sh, el, 0.054, 0.046, 0.025)
        F.ellipsoid(lerp(sh, el, 0.42) + nA * 0.016, (0.050, 0.052, 0.088), rot_from(fa, nA), 0.018)    # bíceps
        F.ellipsoid(lerp(sh, el, 0.40) - nA * 0.018, (0.049, 0.048, 0.092), rot_from(fa, nA), 0.018)    # tríceps
        F.capsule(el, wr, 0.046, 0.032, 0.022)
        F.ellipsoid(lerp(el, wr, 0.28) + nB * 0.008, (0.043, 0.042, 0.095), rot_from(fb, nB), 0.02)       # braquiorradial
        F.ellipsoid(lerp(el, wr, 0.45) - nB * 0.004, (0.036, 0.036, 0.105), rot_from(fb, nB), 0.02)
        # codo
        F.ellipsoid(el + A((0, 0.012, 0)), (0.040, 0.040, 0.040), None, 0.015)

    # --- manos
    for tag, hand in (("G", J["handG"]), ("F", J["handF"])):
        wr = A(J["wr" + tag]); f = A(hand["f"]); f /= np.linalg.norm(f)
        n = A(hand["n"]); n = n - f * (n @ f); n /= np.linalg.norm(n)
        s = np.cross(f, n)
        F.ellipsoid(wr + f * 0.060, (0.041, 0.028, 0.060), rot_from(f, n), 0.015)
        for i in range(4):
            off = s * (i - 1.5) * 0.0212
            lenf = (0.030, 0.034, 0.032, 0.026)[i]
            p0 = wr + f * 0.108 + off + n * 0.002
            p1 = p0 + f * lenf * 0.95 + n * 0.012
            p2 = p1 + n * 0.030 + f * 0.004
            p3 = p2 - f * 0.024 + n * 0.010
            F.capsule(p0, p1, 0.0112, 0.0108, 0.006)
            F.capsule(p1, p2, 0.0108, 0.0104, 0.006)
            F.capsule(p2, p3, 0.0104, 0.0098, 0.006)
        t0 = wr + f * 0.030 + s * 0.040 + n * 0.012
        t1 = t0 + f * 0.040 + n * 0.022 - s * 0.012
        t2 = t1 + f * 0.022 + n * 0.010 - s * 0.01
        F.capsule(t0, t1, 0.0155, 0.0125, 0.012)
        F.capsule(t1, t2, 0.0125, 0.011, 0.008)

    # --- cuello y cabeza
    F.capsule(nk + A((0, 0.0, -0.03)), hd + A((0, 0.02, -0.095)), 0.047, 0.043, 0.04)
    hx, hy, hz = hd
    F.ellipsoid(A((hx, hy + 0.012, hz + 0.010)), (0.086, 0.106, 0.113), None, 0.03)               # cráneo
    F.ellipsoid(A((hx, hy - 0.022, hz - 0.072)), (0.077, 0.083, 0.060), rot_from(A((0, 0, 1)), A((0, -1, 0.12))), 0.03)  # mandíbula
    F.ellipsoid(A((hx, hy - 0.073, hz - 0.098)), (0.040, 0.030, 0.029), None, 0.015)              # mentón
    for sx in (-1, 1):
        F.ellipsoid(A((hx + sx * 0.060, hy - 0.058, hz - 0.036)), (0.030, 0.033, 0.030), None, 0.02)  # pómulo
        F.ellipsoid(A((hx + sx * 0.058, hy - 0.020, hz - 0.075)), (0.020, 0.050, 0.030), None, 0.02)   # maseteros
        F.ellipsoid(A((hx + sx * 0.088, hy + 0.012, hz - 0.012)), (0.011, 0.024, 0.037), rot_from(A((0, 0.25 * sx, 1)), A((sx, 0, 0))), 0.008)  # oreja
        F.ellipsoid(A((hx + sx * 0.0185, hy - 0.113, hz - 0.052)), (0.0105, 0.013, 0.010), None, 0.008)  # ala nasal
        F.ellipsoid(A((hx + sx * 0.037, hy - 0.083, hz - 0.002)), (0.032, 0.020, 0.020), None, 0.012, "sub")  # cuenca ocular
    F.ellipsoid(A((hx, hy - 0.079, hz + 0.034)), (0.074, 0.029, 0.017), None, 0.015)             # arco superciliar
    F.capsule(A((hx, hy - 0.097, hz + 0.010)), A((hx, hy - 0.127, hz - 0.044)), 0.0125, 0.0135, 0.012)  # nariz
    F.ellipsoid(A((hx, hy - 0.130, hz - 0.046)), (0.0165, 0.0175, 0.015), None, 0.008)
    F.ellipsoid(A((hx, hy - 0.1010, hz - 0.074)), (0.030, 0.0115, 0.0088), None, 0.006)          # labio sup
    F.ellipsoid(A((hx, hy - 0.0990, hz - 0.0875)), (0.027, 0.0125, 0.0098), None, 0.006)         # labio inf
    F.ellipsoid(A((hx, hy - 0.096, hz - 0.0815)), (0.030, 0.006, 0.002), None, 0.003, "sub")     # comisura
    return F


def sculpt_shirt(J, p, h):
    pts = np.array([J[k] for k in ("pelvis", "waist", "chest", "neck", "shG", "shF", "elG", "elF")])
    lo = pts.min(0) - 0.30; hi = pts.max(0) + 0.30
    lo[2] = J["pelvis"][2] - 0.22
    F = Field(lo, hi, h)
    c, w, pel, nk = A(J["chest"]), A(J["waist"]), A(J["pelvis"]), A(J["neck"])
    # volumen de tela suelta
    F.ecapsule(pel - A((0, 0, 0.12)), pel, (0.245, 0.160), (0.245, 0.156), 0.05)
    F.ecapsule(pel, w, (0.245, 0.156), (0.225, 0.146), 0.05)
    F.ecapsule(w, c, (0.225, 0.146), (0.255, 0.160), 0.05)
    F.ecapsule(c, c + A((0, 0, 0.14)), (0.255, 0.160), (0.160, 0.122), 0.05)
    ends = {}
    for tag, sx in (("G", -1), ("F", 1)):
        sh, el = A(J["sh" + tag]), A(J["el" + tag])
        d = (el - sh) / np.linalg.norm(el - sh)
        end = lerp(sh, el, 0.86)
        ends[tag] = (end, d)
        F.capsule(sh + A((sx * 0.01, 0, 0.0)), end + d * 0.05, 0.092, 0.083, 0.04)
        F.ellipsoid(sh + A((sx * 0.02, 0.0, -0.01)), (0.095, 0.095, 0.11), None, 0.03)
    # cuello: solapas
    for sx in (-1, 1):
        F.capsule(nk + A((sx * 0.025, -0.07, -0.05)), nk + A((sx * 0.075, -0.045, 0.045)), 0.034, 0.026, 0.02)
    cx = c[0] * 0.5
    fl = fold_noise(5, 7, 22, 70)
    F.displace(lambda X, Y, Zc: 0.0075 * fl(X, Y, Zc) + 0.006 * np.sin(48 * (X - cx) + 5 * np.sin(14 * Zc)), lo, hi)
    # cáscara (tela con espesor) + aberturas
    shell = np.abs(F.d) - max(0.0045, 1.15 * h)
    F.d = shell
    # abertura frontal V
    zz = [0.80, J["pelvis"][2], c[2] - 0.06, c[2] + 0.30]
    ww = [0.075, 0.08, 0.115, 0.15]
    cx = c[0] * 0.5

    def vcut(X, Y, Zc):
        wz = np.interp(Zc, zz, ww).astype(np.float32)
        dx = np.abs(X - cx) - wz
        dy = (Y - (c[1] + 0.02)) * -1.0   # frente: y < c.y+.02 es "dentro" del cortador
        return np.maximum(dx, -dy * 0.0 + (Y - (c[1] + 0.03)) * 1.0) * 1.0 if False else np.maximum(dx, Y - (c[1] + 0.03))
    F.custom(vcut, A((cx - 0.3, c[1] - 0.5, 0.7)), A((cx + 0.3, c[1] + 0.05, c[2] + 0.45)), 0.012, "sub")
    # bajo (dobladillo) y cuello
    hem_z = pel[2] - 0.075
    F.custom(lambda X, Y, Zc: (Zc - hem_z) * -1 + 0.012 * fold_noise(3, 4, 40, 80)(X, Y, Zc), A((-1, -1, 0)), A((1, 1, hem_z + 0.2)), 0.004, "sub") if False else None
    F.custom(lambda X, Y, Zc: hem_z - Zc + 0.014 * np.sin(55 * X + 4 * np.sin(23 * Y)), lo, A((hi[0], hi[1], hem_z + 0.05)), 0.004, "sub") if False else None
    hem_f = fold_noise(11, 3, 25, 55)
    F.custom(lambda X, Y, Zc: Zc - (hem_z + 0.012 * hem_f(X, Y, Zc) * 2), lo, A((hi[0], hi[1], hem_z + 0.04)), 0.004, "sub")
    F.capsule(nk + A((0, 0.0, -0.045)), nk + A((0, 0.0, 0.20)), 0.058, 0.058, 0.0, "sub")
    # mangas abiertas
    for tag, (end, d) in ends.items():
        e = end + d * 0.0
        F.custom(lambda X, Y, Zc, e=e, d=d: -((X - e[0]) * d[0] + (Y - e[1]) * d[1] + (Zc - e[2]) * d[2]), e - 0.25, e + 0.25, 0.004, "sub")
    # pliegues
    return F


def sculpt_jeans(J, p, h):
    pel = A(J["pelvis"])
    pts = np.array([J[k] for k in ("hipG", "hipF", "knG", "knF", "anG", "anF")])
    lo = pts.min(0) - 0.30; hi = pts.max(0) + 0.30
    lo[2] = 0.0; hi[2] = pel[2] + 0.20
    F = Field(lo, hi, h)
    top = pel + A((0, 0, 0.115))
    F.ecapsule(pel, top, (0.178, 0.126), (0.168, 0.118), 0.05)
    for tag in ("G", "F"):
        hip, kn, an = A(J["hip" + tag]), A(J["kn" + tag]), A(J["an" + tag])
        an = an + A((0, 0, 0.075))
        F.capsule(hip, kn, 0.128, 0.108, 0.06)
        F.capsule(kn, an, 0.108, 0.098, 0.05)
        F.ellipsoid(kn + A((0, -0.012, 0.0)), (0.113, 0.112, 0.095), None, 0.03)
        # bolsillos / bulto muslo
        F.ellipsoid(hip + A((0, -0.02, -0.06)), (0.125, 0.115, 0.14), None, 0.04)
    # corte superior y cintura
    F.custom(lambda X, Y, Zc: Zc - top[2], A((-1, -1, top[2] - 0.05)), A((1, 1, top[2] + 0.3)), 0.012, "sub") if False else None
    F.d = smax(F.d, F.coords((slice(0, F.n[0]), slice(0, F.n[1]), slice(0, F.n[2])))[2] - (top[2] + 0.0), 0.02)
    # pliegues: arrugas en rodilla y acumulación suelta al tobillo
    fl = fold_noise(21, 8, 30, 80)

    def fold(X, Y, Zc):
        low = np.clip((0.55 - Zc) / 0.45, 0, 1)
        return 0.006 * fl(X, Y, Zc) + 0.0035 * low * np.sin(60 * Zc + 6 * np.sin(11 * X + 5 * Y)) + 0.005 * np.sin(55 * (X + 0.4 * Y) + 8 * Zc)
    F.displace(fold, lo, hi)
    return F


def sculpt_boots(J, p, h):
    pts = np.array([J["anG"], J["anF"]])
    lo = pts.min(0) - 0.35; hi = pts.max(0) + 0.35
    lo[2] = -0.02; hi[2] = 0.45
    F = Field(lo, hi, h)
    for tag in ("G", "F"):
        a = A(J["an" + tag])
        d = A((p["ft" + tag][0], p["ft" + tag][1], 0)); d /= np.linalg.norm(d)
        s = np.cross(Z, d)
        F.capsule(a + A((0, 0, 0.15)), a + A((0, 0, 0.02)), 0.080, 0.074, 0.05)               # caña
        F.ecapsule(a + A((0, 0, 0.02)), a + d * 0.12 + A((0, 0, -0.045)), (0.070, 0.075), (0.052, 0.040), 0.05, up=Z)
        F.ecapsule(a + d * 0.10 + A((0, 0, -0.04)), a + d * 0.235 + A((0, 0, -0.066)), (0.050, 0.038), (0.022, 0.020), 0.04, up=Z)  # punta
        F.box(a - d * 0.045 + A((0, 0, -0.092)), (0.045, 0.04, 0.026), rot_from(d, Z) if False else None, 0.01, 0.0)
        F.ecapsule(a + A((0, 0, -0.02)), a + d * 0.20 + A((0, 0, -0.07)), (0.074, 0.050), (0.030, 0.026), 0.03, up=Z)  # suela gruesa
        # borde superior de caña (pespunte)
        pass
    return F
