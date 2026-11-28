"""Poses por codigo sobre el rig 'default' de MPFB: IK de 2 huesos para brazos/piernas + giros de columna/cabeza."""
import bpy, math
from mathutils import Vector, Matrix, Quaternion


def _aim(arm, pb, target_world):
    """Rota el hueso (pose) para que su eje Y apunte a target_world, manteniendo su cabeza."""
    mw = arm.matrix_world; mi = mw.inverted()
    t = mi @ Vector(target_world); head = pb.head.copy(); d = (t - head).normalized()
    m = pb.matrix.copy(); y = (m.to_quaternion() @ Vector((0, 1, 0))).normalized()
    rot = y.rotation_difference(d).to_matrix().to_4x4()
    nm = rot @ m; nm.translation = m.translation
    pb.matrix = nm; bpy.context.view_layer.update()


def _ik2(S, W, pole, a, b):
    """Posicion del codo/rodilla: triangulo con lados a (S-E) y b (E-W), inclinado hacia 'pole'."""
    S, W, pole = Vector(S), Vector(W), Vector(pole)
    d = W - S; L = d.length
    if L < 1e-5: return S + Vector((0, 0, -a))
    L = min(L, (a + b) * 0.999); dn = d.normalized(); x = (a * a - b * b + L * L) / (2 * L); h = math.sqrt(max(a * a - x * x, 0))
    pv = (pole - S); pv = (pv - dn * pv.dot(dn)); pv = pv.normalized() if pv.length > 1e-6 else Vector((0, -1, 0))
    return S + dn * x + pv * h


def _world(arm, v): return arm.matrix_world @ Vector(v)


def posar(arm, P, escala):
    """P: dict de joints en coordenadas 'de diseno' (altura 1.85 m). Se escalan a la altura real del rig."""
    bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode='POSE')
    pb = arm.pose.bones; mw = arm.matrix_world
    for b in pb: b.rotation_mode = 'XYZ'; b.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()
    # --- columna: inclinacion/giro simple (rig game_engine)
    lean = P.get("lean", (0, 0, 0))
    for n, f in (("spine_01", .3), ("spine_02", .35), ("spine_03", .35)):
        pb[n].rotation_euler = (lean[0] * f, lean[1] * f, lean[2] * f)
    bpy.context.view_layer.update()
    # --- cabeza
    hr = P.get("head_rot", (0, 0, 0))
    for n, f in (("neck_01", .5), ("head", .5)):
        if n in pb: pb[n].rotation_euler = (hr[0] * f, hr[1] * f, hr[2] * f)
    bpy.context.view_layer.update()
    # --- brazos y piernas (L de imagen = .R del personaje)
    for lado_img, suf in (("L", "R"), ("R", "L")):
        suf = suf.lower(); up, lo, wr = pb["upperarm_" + suf], pb["lowerarm_" + suf], pb["hand_" + suf]
        S = mw @ up.head; a = (up.tail - up.head).length; b = (lo.tail - lo.head).length
        ref_sh = Vector(P["sh" + lado_img]); W = S + (Vector(P["wr" + lado_img]) - ref_sh) * escala
        E_hint = S + (Vector(P["el" + lado_img]) - ref_sh) * escala
        pole = E_hint + Vector((0, -0.2, 0)) if P.get("pole_brazo") is None else Vector(P["pole_brazo"])
        E = _ik2(S, W, E_hint, a, b); _aim(arm, up, E); _aim(arm, lo, W if (W - S).length <= a + b else S + (W - S).normalized() * (a + b))
        hp, kn, an = pb["thigh_" + suf], pb["calf_" + suf], pb["foot_" + suf]
        H = mw @ hp.head; a2 = (hp.tail - hp.head).length; b2 = (kn.tail - kn.head).length
        ref_hp = Vector(P["hip" + lado_img]); A = H + (Vector(P["an" + lado_img]) - ref_hp) * escala; K = H + (Vector(P["kn" + lado_img]) - ref_hp) * escala
        Ek = _ik2(H, A, K, a2, b2); _aim(arm, hp, Ek); _aim(arm, kn, A if (A - H).length <= a2 + b2 else H + (A - H).normalized() * (a2 + b2))
    bpy.ops.object.mode_set(mode='OBJECT')
