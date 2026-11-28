"""Vaquero exotico: cuerpo musculoso (metaballs), camisa blanca abierta con palmeras grises, jeans sueltos, botas vaqueras modernas,
sombrero con palmera de oro y revolver. Todo por codigo. Eje: personaje mira hacia -Y, +X a la derecha de la camara, Z arriba."""
import bpy, math, random, os, sys
from mathutils import Vector, Quaternion, Matrix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base import *

def V(*a):
    return Vector(a[0]) if len(a) == 1 else Vector(a)
POSES = {
 # joints en metros. L/R = lado de la IMAGEN (L = izquierda de camara)
 "posando": dict(pelvis=(0.03, 0, 1.0), chest=(0.0, -0.03, 1.38), neck=(0.0, -0.03, 1.58), head=(0.03, -0.06, 1.76), head_rot=(0.12, 0.0, -0.18),
    shL=(-0.23, 0.0, 1.50), elL=(-0.42, 0.04, 1.26), wrL=(-0.2, -0.1, 1.04), shR=(0.23, 0.0, 1.50), elR=(0.42, -0.10, 1.27), wrR=(0.33, -0.33, 1.47),
    hipL=(-0.1, 0, 0.96), knL=(-0.13, -0.03, 0.54), anL=(-0.13, 0.0, 0.10), hipR=(0.11, 0, 0.94), knR=(0.2, -0.13, 0.53), anR=(0.30, -0.14, 0.10),
    arma=((0.33, -0.34, 1.47), (0.02, -0.0, 1.0))),   # origen de la empunadura, direccion del canon (arriba)
 "apuntando": dict(pelvis=(0.05, 0.02, 0.98), chest=(0.06, -0.02, 1.36), neck=(0.07, -0.05, 1.57), head=(0.12, -0.09, 1.75), head_rot=(0.0, 0.0, -0.28),
    shL=(-0.19, 0.02, 1.49), elL=(-0.05, -0.36, 1.43), wrL=(0.15, -0.64, 1.50), shR=(0.28, -0.02, 1.50), elR=(0.34, -0.38, 1.52), wrR=(0.2, -0.66, 1.53),
    hipL=(-0.07, 0.02, 0.95), knL=(-0.30, 0.0, 0.55), anL=(-0.42, 0.1, 0.10), hipR=(0.17, 0.0, 0.94), knR=(0.32, -0.12, 0.54), anR=(0.38, -0.30, 0.10),
    arma=((0.18, -0.67, 1.53), (-0.06, -1.0, 0.04))),
}


def rotm(rx, ry, rz):
    return (Matrix.Rotation(rz, 3, 'Z') @ Matrix.Rotation(ry, 3, 'Y') @ Matrix.Rotation(rx, 3, 'X'))


def construir_cuerpo(P, musc=1.0):
    s = Piel("piel", res=0.011)
    pel, ch, nk, hd = V(P["pelvis"]), V(P["chest"]), V(P["neck"]), V(P["head"])
    # --- torso: pelvis, abdomen con 6 bloques, torax, pectorales, dorsales, trapecios
    s.bola(pel, .17, 1.15, .72, .85); s.bola(pel + V(0, 0, .12), .16, 1.1, .7, .9)
    for i, z in enumerate((.16, .22, .28)):
        for sx in (-1, 1):
            s.bola(V(pel.x + sx * .042, pel.y - .085 + .005 * i, pel.z + z), .036, 1.0, .75, .8, rig=4.5)      # abdominales
    s.bola(ch + V(0, 0.01, -.03), .21, 1.05, .62, 1.0); s.bola(ch + V(0, .0, .05), .2, 1.1, .6, .8)
    for sx in (-1, 1):
        s.bola(ch + V(sx * .095, -.075, .04), .09, 1.25, .55, .9, rig=4)                                       # pectorales
        s.bola(ch + V(sx * .17, .045, .0), .09, 1.0, .6, 1.5)                                                      # dorsales
        s.bola(nk + V(sx * .09, .02, -.02), .06, 1.5, .8, .8)                                                      # trapecios
        s.bola(ch + V(sx * .125, -.04, -.12), .06, 1.0, .6, 1.3)                                                   # serrato/oblicuo
    # --- cuello y cabeza
    s.hueso(nk + V(0, 0, -.02), hd + V(0, .01, -.11), .058, .052, aplast=(1, 1))
    for sx in (-1, 1): s.hueso(nk + V(sx * .03, -.03, .0), hd + V(sx * .045, -.04, -.09), .018, .016)             # esternocleidomastoideo
    # --- brazos con deltoides, biceps/triceps, antebrazo
    for lado, sx in (("L", -1), ("R", 1)):
        sh, el, wr = V(P["sh" + lado]), V(P["el" + lado]), V(P["wr" + lado])
        s.bola(sh + V(sx * .012, 0, .0), .082 * musc, 1.0, 1.0, 1.0, rig=4)                                      # deltoides
        up = el - sh
        s.hueso(sh + up * .15, el - up * .06, .06 * musc, .05, aplast=(1.0, 1.1))
        n = up.normalized(); perp = V((0, -1, 0)); s.hueso(sh + up * .3 + perp * .02, sh + up * .75 + perp * .02, .042 * musc, .036, aplast=(1.0, 1.0))  # biceps
        s.hueso(sh + up * .25 - perp * .025, sh + up * .78 - perp * .025, .04 * musc, .034)                           # triceps
        fo = wr - el
        s.hueso(el + fo * .05, el + fo * .45, .052 * musc, .042, aplast=(1.1, 0.95)); s.hueso(el + fo * .4, wr, .042, .03)
        s.bola(el, .05, 1, 1, 1); s.bola(wr + fo.normalized() * .045, .042, .8, .5, 1.0)                           # codo / mano
        d = fo.normalized()
        for k in range(4): s.bola(wr + d * .1 + V(sx * (k - 1.5) * .018, 0, 0), .014, .7, .7, 1.8, dirq(d))     # dedos (bloque)
    # --- piernas
    for lado, sx in (("L", -1), ("R", 1)):
        hp, kn, an = V(P["hip" + lado]), V(P["kn" + lado]), V(P["an" + lado])
        s.bola(hp + V(sx * .01, .05, -.02), .105, 1, .95, .9)                                                       # gluteo
        th = kn - hp; s.hueso(hp + th * .08, kn - th * .04, .105 * musc, .062, aplast=(1.0, 1.0))                  # cuadriceps
        s.hueso(hp + th * .25 + V(sx * .05, -.02, 0), kn + th * -.15 + V(sx * .03, -.02, 0), .06, .045)             # vasto lateral
        sh_ = an - kn; s.hueso(kn + sh_ * .05, an, .06 * musc, .042, aplast=(1.0, 1.0))
        s.bola(kn + sh_ * .22 + V(sx * .025, .05, 0), .05, 1, 1, 1.4)                                                 # gemelos
    return s.convertir(2)


def construir_cabeza(P, piel_mat, ojo_mat):
    """Cabeza humana por metaballs en coordenadas locales -> transformada por la pose. Devuelve (objeto_malla, [ojos])."""
    hd = V(P["head"]); R = rotm(*P["head_rot"])
    def T(v): return hd + R @ V(v)
    s = Piel("cabeza", res=0.0075, umbral=0.6)
    s.bola(T((0, .012, .012)), .098, 1.0, 1.1, 1.12)                     # craneo
    s.bola(T((0, -.03, -.05)), .085, .98, .9, .9)                        # mejillas / maxilar superior
    s.bola(T((0, -.045, -.088)), .07, 1.05, .85, .72, rig=2.0)            # mandibula
    s.bola(T((0, -.085, -.122)), .031, 1.1, .9, .85)                      # menton
    for sx in (-1, 1):
        s.bola(T((sx * .066, -.058, -.075)), .03, 1, 1, 1)                # angulo mandibular / masetero
        s.bola(T((sx * .062, -.068, -.012)), .029, 1, 1, .9)              # pomulo
        s.bola(T((sx * .04, -.098, .038)), .026, 1.5, .6, .55)             # arco superciliar
        s.bola(T((sx * .099, .0, -.01)), .02, .4, .9, 1.6)                 # oreja
        s.bola(T((sx * .037, -.086, .018)), .021, 1, .8, 1, neg=True, rig=3)  # cuenca ocular (resta)
        s.bola(T((sx * .017, -.122, -.052)), .0125, 1, 1, 1)               # ala nasal
        s.bola(T((sx * .02, -.1, -.082)), .0125, 1.5, .8, .8)               # pliegue nasolabial / comisura
    s.bola(T((0, -.108, .025)), .013, .8, 1, 1.5); s.bola(T((0, -.116, -.01)), .014, .8, 1, 1.5)   # puente de la nariz
    s.bola(T((0, -.128, -.047)), .0165, 1, 1, 1)                          # punta
    s.bola(T((0, -.099, -.077)), .0145, 2.0, .8, .6, rig=4.5); s.bola(T((0, -.102, -.095)), .0155, 1.9, .85, .7, rig=4.5)   # labios
    s.bola(T((0, -.1, .045)), .012, 2.0, .6, .4)                          # entrecejo
    cab = s.convertir(1); asignar(cab, piel_mat)
    ojos = []
    for sx in (-1, 1):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.0125, location=T((sx * .036, -.094, .018))); o = bpy.context.object; o.name = "ojo"; bpy.ops.object.shade_smooth(); asignar(o, ojo_mat); ojos.append(o)
    return cab, ojos
