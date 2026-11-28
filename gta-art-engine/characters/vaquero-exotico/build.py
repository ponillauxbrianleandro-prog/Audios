"""Vaquero exótico — modelo proxy procedural (Blender/bpy).
Lado -X = mano del revólver. Cara hacia -Y. Unidades en metros.
Uso: python build.py <posing|aiming>  (lo llama render.py)"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "block1-blender"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector, Matrix, Euler
from lib import *

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.abspath(os.path.join(HERE, "..", "..", "work"))

# ---------------------------------------------------------------- poses (articulaciones)
POSES = {
    "posing": dict(
        yaw=-22, hip_shift=0.03,
        pelvis=(0.03, 0, 0.98), waist=(0.015, 0, 1.20), chest=(0, 0, 1.42), neck=(0, -0.01, 1.62), head=(0, -0.02, 1.80),
        shG=(-0.225, 0.0, 1.535), shF=(0.225, 0.0, 1.55),
        elG=(-0.40, 0.02, 1.27), wrG=(-0.38, -0.20, 1.34),
        elF=(0.375, 0.06, 1.28), wrF=(0.285, -0.075, 1.04),
        hipG=(-0.095, 0, 0.93), hipF=(0.12, 0, 0.93),
        knG=(-0.15, -0.03, 0.52), knF=(0.16, 0.02, 0.52),
        anG=(-0.19, 0.06, 0.105), anF=(0.20, 0.0, 0.105),
        ftG=(-0.30, -1.0), ftF=(0.55, -1.0),  # dirección horizontal de cada pie (x,y)
        gun=dict(fwd=(0.02, -0.25, 1.0), up=(0, 1.0, -0.25)),
        gunhand="G",
    ),
    "aiming": dict(
        yaw=38, hip_shift=0.0,
        pelvis=(0.0, 0.02, 0.93), waist=(0, 0.0, 1.14), chest=(0, -0.03, 1.37), neck=(0, -0.08, 1.56), head=(-0.01, -0.12, 1.73),
        shG=(-0.22, -0.02, 1.48), shF=(0.225, -0.03, 1.49),
        elG=(-0.20, -0.30, 1.50), wrG=(-0.10, -0.55, 1.53),
        elF=(0.30, -0.28, 1.40), wrF=(0.04, -0.52, 1.46),
        hipG=(-0.10, 0.02, 0.90), hipF=(0.12, 0.02, 0.90),
        knG=(-0.30, -0.12, 0.50), knF=(0.28, 0.14, 0.52),
        anG=(-0.32, 0.12, 0.105), anF=(0.30, 0.40, 0.105),
        ftG=(-0.5, -1.0), ftF=(0.9, -0.3),
        gun=dict(fwd=(0.12, -1.0, 0.04), up=(0, 0.04, 1.0)),
        gunhand="G",
    ),
}


def P(p, k):
    return Vector(p[k])


def basis_matrix(side, fwd, up):
    return Matrix(((side.x, fwd.x, up.x), (side.y, fwd.y, up.y), (side.z, fwd.z, up.z)))


def orient(o, f, n):
    """Orienta un objeto: z local = f (largo), y local = n."""
    f = Vector(f).normalized()
    n = (Vector(n) - f * Vector(n).dot(f)).normalized()
    s = f.cross(n).normalized()  # x local
    o.rotation_euler = basis_matrix(s, n, f).to_euler()
    return o


def fist(name, wrist, f, n, M, parent, grip=0.0):
    f, n = Vector(f).normalized(), Vector(n).normalized()
    s = f.cross(n).normalized()
    c = Vector(wrist) + f * 0.065
    o = ell(name + "_palm", c, (0.040, 0.026, 0.056), (0, 0, 0), M, 3, 1, parent)
    orient(o, f, n)
    for i in range(4):
        off = s * (i - 1.5) * 0.0215
        p0 = Vector(wrist) + f * 0.105 + off + n * 0.004
        p1 = p0 + f * 0.028 + n * 0.010
        p2 = p1 + n * 0.030 + f * 0.003
        p3 = p2 - f * 0.026 + n * 0.012
        for j, (a, b) in enumerate(((p0, p1), (p1, p2), (p2, p3))):
            limb_ell(f"{name}_f{i}{j}", a, b, 0.0115, 0.0115, 1.35, 0.5, M, 3, parent)
    t0 = Vector(wrist) + f * 0.035 + s * 0.042 + n * 0.012
    t1 = t0 + f * 0.040 + n * 0.020 - s * 0.012
    limb_ell(name + "_thumb", t0, t1, 0.0125, 0.0125, 1.3, 0.5, M, 3, parent)
    return c


# ---------------------------------------------------------------- revólver
def revolver(parent, M_steel, M_wood, M_blue, scale=1.0):
    g = []
    s = scale
    g.append(rbox("g_frame", (0, 0.000, 0.018), (0.032 * s, 0.100 * s, 0.050 * s), (0, 0, 0), M_steel, 5, 0.008, parent))
    g.append(ell("g_barrel", (0, 0.165 * s, 0.040 * s), (0.0125 * s, 0.1 * s, 0.0125 * s), (0, 0, 0), M_blue, 5, 1, parent))
    g[-1].rotation_euler = (0, 0, 0)
    g.append(ell("g_rib", (0, 0.165 * s, 0.056 * s), (0.006 * s, 0.1 * s, 0.006 * s), (0, 0, 0), M_steel, 5, 1, parent))
    g.append(ell("g_ejector", (0.0, 0.15 * s, 0.014 * s), (0.007 * s, 0.07 * s, 0.007 * s), (0, 0, 0), M_steel, 5, 1, parent))
    drum = revolve("g_drum", [(0, -0.045), (0.027, -0.045), (0.030, -0.040), (0.030, 0.040), (0.027, 0.045), (0, 0.045)], 40, M_steel, 5, None, parent,
                   (0, 0.010 * s, 0.034 * s), (math.pi / 2, 0, 0), 1)
    drum.scale = (s, s, s)
    for k in range(6):
        a = k * math.pi / 3
        ell(f"g_ch{k}", (math.cos(a) * 0.019 * s, 0.056 * s, 0.034 * s + math.sin(a) * 0.019 * s), (0.0075 * s, 0.006 * s, 0.0075 * s),
            (0, 0, 0), M_blue, 5, 0, parent, 10, 8)
    g.append(rbox("g_grip", (0, -0.052 * s, -0.045 * s), (0.034 * s, 0.050 * s, 0.105 * s), (-0.38, 0, 0), M_wood, 6, 0.01, parent))
    g.append(rbox("g_hammer", (0, -0.060 * s, 0.056 * s), (0.010 * s, 0.032 * s, 0.032 * s), (0.55, 0, 0), M_steel, 5, 0.004, parent))
    g.append(rbox("g_sightF", (0, 0.255 * s, 0.062 * s), (0.005 * s, 0.01 * s, 0.014 * s), (0, 0, 0), M_steel, 5, 0.002, parent))
    guard = revolve("g_guard", [(0.021, -0.003), (0.027, -0.003), (0.027, 0.003), (0.021, 0.003)], 28, M_steel, 5, None, parent,
                    (0, -0.008 * s, -0.020 * s), (0, math.pi / 2, 0), 1)
    guard.scale = (s * 1.0, s * 0.8, s * 1.7)
    ell("g_trigger", (0, -0.012 * s, -0.012 * s), (0.004 * s, 0.006 * s, 0.014 * s), (0.2, 0, 0), M_steel, 5, 0, parent, 8, 6)
    return g


# ---------------------------------------------------------------- palmera dorada (emblema)
def palm_emblem(M_gold, parent, size=0.06):
    verts, faces = [], []

    def strip(pts, widths):
        base = len(verts)
        # pts: lista (x,z); widths por punto; genera tira en plano XZ con normal de ancho perpendicular
        for i, (x, z) in enumerate(pts):
            if i < len(pts) - 1:
                dx, dz = pts[i + 1][0] - x, pts[i + 1][1] - z
            else:
                dx, dz = x - pts[i - 1][0], z - pts[i - 1][1]
            l = math.hypot(dx, dz) or 1
            nx, nz = -dz / l, dx / l
            w = widths[i]
            verts.append((x + nx * w, 0, z + nz * w))
            verts.append((x - nx * w, 0, z - nz * w))
        for i in range(len(pts) - 1):
            a = base + i * 2
            faces.append((a, a + 1, a + 3, a + 2))

    n = 12
    trunk = [(0.10 * (t / n) ** 2 - 0.02 * math.sin(t / n * 3), t / n * 0.62 - 0.55) for t in range(n + 1)]
    strip(trunk, [0.050 - 0.028 * t / n for t in range(n + 1)])
    topx, topz = trunk[-1]
    for k in range(9):
        a = math.radians(8 + k * 164 / 8)
        pts, ws = [], []
        for i in range(11):
            s = i / 10
            L = 0.46 * (0.75 + 0.25 * math.sin(a))
            x = topx + math.cos(a) * s * L
            z = topz + math.sin(a) * s * L * 0.85 - 0.62 * s * s * L * (1.0 - 0.3 * math.sin(a))
            pts.append((x, z))
            ws.append(0.052 * math.sin(math.pi * (0.12 + 0.88 * s)) ** 0.8 + 0.004)
        strip(pts, ws)
    for dx in (-0.045, 0.0, 0.05):
        pass
    o = mesh_from("palm_emblem", [(v[0] * size / 0.5, v[1], v[2] * size / 0.5) for v in verts], faces, M_gold, 8, parent, 0, 0.0)
    return o


# ---------------------------------------------------------------- construcción
def build(pose_name):
    p = POSES[pose_name]
    root = bpy.data.objects.new("root", None)
    bpy.context.scene.collection.objects.link(root)
    root.rotation_euler = (0, 0, math.radians(p["yaw"]))

    # ---- materiales
    skin_m = mat("skin", (0.60, 0.34, 0.22), 0.52, 0, sss=0.25, bump=True, bump_scale=900, bump_str=0.09, spec=0.35)
    shirt_m = mat("shirt", (0.9, 0.9, 0.88), 0.85, tex=os.path.join(WORK, "palm_print.png"), tex_scale=1.1)
    jeans_m = mat("jeans", (0.045, 0.085, 0.16), 0.85, bump=True, bump_scale=600, bump_str=0.12)
    boot_m = mat("boot", (0.14, 0.065, 0.028), 0.62, coat=0.0, bump=True, bump_scale=300, bump_str=0.1)
    hat_m = mat("hat", (0.72, 0.60, 0.42), 0.9, bump=True, bump_scale=1200, bump_str=0.15)
    band_m = mat("band", (0.13, 0.07, 0.04), 0.5)
    gold_m = mat("gold", (1.0, 0.72, 0.20), 0.22, metal=1.0)
    steel_m = mat("steel", (0.30, 0.31, 0.34), 0.35, metal=1.0)
    blue_m = mat("bluedsteel", (0.05, 0.06, 0.09), 0.38, metal=1.0)
    wood_m = mat("wood", (0.28, 0.12, 0.05), 0.45, coat=0.4)
    lens_m = mat("lens", (0.05, 0.75, 0.38), 0.04, metal=1.0)
    black_m = mat("black", (0.02, 0.02, 0.02), 0.4)
    hair_m = mat("hair", (0.09, 0.06, 0.04), 0.6)
    white_m = mat("whitecloth", (0.92, 0.92, 0.9), 0.8)

    J = {k: P(p, k) for k in p if isinstance(p[k], tuple) and len(p[k]) == 3}

    # ---- cuerpo, camisa, jeans y botas: escultura SDF (marching cubes), fusión orgánica
    import numpy as np
    from body_sdf import sculpt_skin, sculpt_shirt, sculpt_jeans, sculpt_boots
    HV = float(os.environ.get("VOXEL", "0.0035"))
    fG = (J["wrG"] - J["elG"]).normalized()
    fF = (J["wrF"] - J["elF"]).normalized()
    nGv = (0.25, 0.05, 0.2) if pose_name == "posing" else (0.8, 0, 0.2)
    nFv = (0.7, 0.2, 0.0) if pose_name == "posing" else (-0.4, 0.0, 0.9)
    JJ = {k: tuple(v) for k, v in J.items()}
    JJ["handG"] = dict(f=tuple(fG), n=nGv)
    JJ["handF"] = dict(f=tuple(fF), n=nFv)
    for name_, fn_, m_, idx_, sm in (("skin", sculpt_skin, skin_m, 2, 1), ("shirt", sculpt_shirt, shirt_m, 13, 1),
                                     ("jeans", sculpt_jeans, jeans_m, 14, 1), ("boots", sculpt_boots, boot_m, 16, 1)):
        F_ = fn_(JJ, p, HV * (1.3 if name_ in ("jeans", "boots") else 1.0))
        v_, f_, n_ = F_.mesh(smooth=sm)
        mesh_np(name_, v_, f_, m_, idx_, root)
        print("SDF", name_, len(v_), "verts", flush=True)
    c, w, pel = J["chest"], J["waist"], J["pelvis"]
    h = J["head"]
    hz = h.z
    for sx in (-1, 1):
        ell(f"lens{sx}", (h.x + sx * 0.040, h.y - 0.092, hz + 0.003), (0.037, 0.011, 0.026), (0.05, 0, sx * -0.08), lens_m, 9, 2, root)
        limb_ell(f"temple{sx}", (h.x + sx * 0.078, h.y - 0.080, hz + 0.008), (h.x + sx * 0.087, h.y + 0.00, hz + 0.008), 0.004, 0.004, 1.2, 0.5, black_m, 9, root)
        ell(f"frameU{sx}", (h.x + sx * 0.040, h.y - 0.0955, hz + 0.029), (0.040, 0.008, 0.005), (0, 0, 0), black_m, 9, 1, root)
        ell(f"burn{sx}", (h.x + sx * 0.082, h.y - 0.02, hz - 0.02), (0.008, 0.026, 0.05), (0, 0, 0), hair_m, 10, 1, root)
    ell("hairBack", (h.x, h.y + 0.045, hz + 0.0), (0.082, 0.07, 0.085), (0, 0, 0), hair_m, 10, 2, root)

    # ---- sombrero vaquero (con palmera de oro en vez de estrella)
    hat_z = hz + 0.075
    def brim(th, r, z):
        if r > 0.14:
            t = (r - 0.14) / 0.10
            return (0, 0.05 * t ** 1.6 * math.cos(2 * th) + 0.005 * t)
        if z > 0.1:
            return (-0.012 * (math.cos(2 * th) * 0.5 + 0.5), -0.014 * (1 + math.cos(2 * th + math.pi)) * 0.5 * (1 - r / 0.075))
        return (0, 0)
    prof = [(0, 0.118), (0.035, 0.123), (0.068, 0.120), (0.088, 0.108), (0.0955, 0.075), (0.0985, 0.03), (0.102, 0.0),
            (0.135, -0.006), (0.185, -0.004), (0.225, 0.006), (0.245, 0.020)]
    hat = revolve("hat", prof, 72, hat_m, 11, brim, root, (h.x, h.y + 0.005, hat_z), (-0.07, 0, 0), 2)
    sol = hat.modifiers.new("solid", "SOLIDIFY"); sol.thickness = 0.006
    for o_ in (hat,):
        pass
    band = revolve("hatband", [(0.0975, 0.014), (0.1015, 0.016), (0.1015, 0.046), (0.0955, 0.048)], 72, band_m, 12, None, root,
                   (h.x, h.y + 0.005, hat_z), (-0.07, 0, 0), 1)
    emb = palm_emblem(gold_m, root, 0.058)
    emb.rotation_euler = (-0.07, 0, 0)
    emb.location = (h.x, h.y + 0.005 - 0.1085, hat_z + 0.075)
    sd = emb.modifiers.new("solid", "SOLIDIFY"); sd.thickness = 0.004
    bv = emb.modifiers.new("bev", "BEVEL"); bv.width = 0.0012; bv.segments = 2
    for k in (-1, 1):
        ell(f"conchoU{k}", (h.x + k * 0.04, h.y + 0.005 - 0.099, hat_z + 0.03), (0.007, 0.004, 0.007), (0, 0, 0), gold_m, 8, 1, root)

    # ---- revólver
    g = p["gun"]
    fwd, up = Vector(g["fwd"]).normalized(), Vector(g["up"]).normalized()
    up = (up - fwd * up.dot(fwd)).normalized()
    side = fwd.cross(up).normalized()
    gempty = bpy.data.objects.new("gun", None)
    bpy.context.scene.collection.objects.link(gempty)
    gempty.parent = root
    M = basis_matrix(side, fwd, up)
    gempty.rotation_euler = M.to_euler()
    fc = J["wrG"] + fG * 0.07
    gempty.location = fc - M @ Vector((0, -0.052, -0.040))
    revolver(gempty, steel_m, wood_m, blue_m, 1.3)

    belt = revolve("belt", [(0.168, 0.0), (0.176, 0.0), (0.176, 0.045), (0.168, 0.045)], 48, boot_m, 15, None, root,
                   (J["pelvis"].x, J["pelvis"].y, J["pelvis"].z + 0.075), (0, 0, 0), 1)
    belt.scale = (1.0, 0.76, 1.0)
    rbox("buckle", (J["pelvis"].x, J["pelvis"].y - 0.134, J["pelvis"].z + 0.092), (0.07, 0.014, 0.05), (0, 0, 0), gold_m, 8, 0.006, root)

    global META
    META = dict(head=tuple(J["head"]), anG=tuple(J["anG"]), anF=tuple(J["anF"]))
    bpy.context.view_layer.update()
    return root


if __name__ == "__main__":
    reset()
    build(sys.argv[-1])

# cámaras por pose (formato 16:10 horizontal, personaje centrado-derecha para dejar mundo a la izquierda)
CAMERAS = {
    "posing": dict(lens=42, loc=(0.6, -4.15, 1.12), look=(0.0, 0.0, 1.0), key=(-3.5, -3.0, 4.2)),
    "aiming": dict(lens=42, loc=(0.4, -4.35, 1.08), look=(0.0, -0.1, 0.98), key=(-3.5, -3.0, 4.2)),
}
