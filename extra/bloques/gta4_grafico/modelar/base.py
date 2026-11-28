"""Utilidades de modelado por codigo en Blender (bpy): metaballs musculares, materiales, transformaciones."""
import bpy, math, mathutils
from mathutils import Vector, Quaternion, Matrix


def limpiar():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bpy.context.scene


def mat(nombre, color=(.8, .8, .8, 1), rug=.5, metal=0.0, sss=0.0, extra=None):
    m = bpy.data.materials.new(nombre); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = color; b.inputs["Roughness"].default_value = rug; b.inputs["Metallic"].default_value = metal
    if sss and "Subsurface Weight" in b.inputs: b.inputs["Subsurface Weight"].default_value = sss; b.inputs["Subsurface Radius"].default_value = (1.0, .35, .25); b.inputs["Subsurface Scale"].default_value = .02
    if extra: extra(m, b)
    return m


def asignar(obj, m, indice=None):
    obj.data.materials.append(m)
    if indice is not None:
        for p in obj.data.polygons: p.material_index = len(obj.data.materials) - 1


def dirq(d):
    """Cuaternion que lleva +Z hacia la direccion d."""
    return Vector((0, 0, 1)).rotation_difference(Vector(d).normalized())


class Piel:
    """Coleccion de elementos metaball (se fusionan suavemente) -> malla organica."""
    def __init__(self, nombre, res=0.012, umbral=0.6):
        self.mb = bpy.data.metaballs.new(nombre); self.mb.resolution = res; self.mb.render_resolution = res; self.mb.threshold = umbral
        self.ob = bpy.data.objects.new(nombre, self.mb); bpy.context.collection.objects.link(self.ob); self.nombre = nombre

    def bola(self, c, r, rx=1, ry=1, rz=1, q=None, rig=3.5, neg=False):
        e = self.mb.elements.new(type='ELLIPSOID'); e.co = c; e.radius = r / 0.575; e.size_x, e.size_y, e.size_z = rx, ry, rz
        e.stiffness = rig; e.use_negative = neg
        if q is not None: e.rotation = q
        return e

    def hueso(self, a, b, ra, rb=None, n=None, aplast=(1, 1), rig=3.5):
        """Cadena de elipsoides entre a y b (musculo/miembro). aplast=(ancho, profundo) relativos al eje."""
        a, b = Vector(a), Vector(b); rb = ra if rb is None else rb; L = (b - a).length; n = n or max(3, int(L / (min(ra, rb) * .7)))
        q = dirq(b - a)
        for i in range(n + 1):
            t = i / n; r = ra + (rb - ra) * t
            self.bola(a + (b - a) * t, r, aplast[0], aplast[1], 1.0 * 1.0, q, rig)

    def convertir(self, suavizar=2):
        bpy.context.view_layer.objects.active = self.ob
        for o in bpy.context.selected_objects: o.select_set(False)
        self.ob.select_set(True); bpy.ops.object.convert(target='MESH')
        o = bpy.context.view_layer.objects.active
        o.name = self.nombre + "_malla"
        bpy.ops.object.shade_smooth()
        if suavizar:
            m = o.modifiers.new("suave", 'CORRECTIVE_SMOOTH'); m.iterations = suavizar
        return o
