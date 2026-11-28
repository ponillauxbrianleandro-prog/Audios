"""Helpers de modelado procedural (Blender/bpy). Todo en código, sin assets externos."""
import math
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

V = Vector


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mat(name, color, rough=0.6, metal=0.0, sss=0.0, sss_color=None, tex=None, tex_scale=1.0,
        spec=0.5, coat=0.0, bump=None, bump_scale=40.0, bump_str=0.2):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    for k, v in (("Subsurface Weight", sss), ("Coat Weight", coat), ("Specular IOR Level", spec)):
        if k in bsdf.inputs:
            bsdf.inputs[k].default_value = v
    if sss and "Subsurface Radius" in bsdf.inputs:
        bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.35, 0.2)
        bsdf.inputs["Subsurface Scale"].default_value = 0.03
    if tex:
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = bpy.data.images.load(tex)
        t.image.colorspace_settings.name = "sRGB"
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (tex_scale, tex_scale, tex_scale)
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
        t.projection = "BOX"
        t.projection_blend = 0.2
        nt.links.new(mp.outputs["Vector"], t.inputs["Vector"])
        nt.links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
    if bump:
        n = nt.nodes.new("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value = bump_scale
        n.inputs["Detail"].default_value = 8
        b = nt.nodes.new("ShaderNodeBump")
        b.inputs["Strength"].default_value = bump_str
        nt.links.new(n.outputs["Fac"], b.inputs["Height"])
        nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def _finish(o, material, idx, smooth=True, parent=None):
    if material:
        o.data.materials.append(material)
    o.pass_index = idx
    if smooth:
        for p in o.data.polygons:
            p.use_smooth = True
    if parent:
        o.parent = parent
    return o


def new_obj(name, me, collection=None):
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    return o


def ell(name, loc, scale, rot=(0, 0, 0), material=None, idx=1, subdiv=1, parent=None, seg=24, rings=16):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
    bm.to_mesh(me)
    bm.free()
    o = new_obj(name, me)
    o.location = loc
    o.scale = scale
    o.rotation_euler = Euler(rot)
    if subdiv:
        s = o.modifiers.new("sub", "SUBSURF")
        s.levels = subdiv
        s.render_levels = subdiv
    return _finish(o, material, idx, parent=parent)


def between(a, b):
    """Rotación que alinea +Z con el vector a->b (para elipsoides entre articulaciones)."""
    d = (V(b) - V(a))
    q = V((0, 0, 1)).rotation_difference(d.normalized())
    return q.to_euler()


def limb_ell(name, a, b, rx, ry, along=1.0, t=0.5, material=None, idx=1, parent=None, off=(0, 0, 0)):
    a, b = V(a), V(b)
    c = a.lerp(b, t) + V(off)
    L = (b - a).length
    return ell(name, c, (rx, ry, L * 0.5 * along), between(a, b), material, idx, 1, parent)


def skin(name, joints, edges, radii, material, idx=1, subdiv=2, parent=None, root=None, branch_smooth=0.5):
    names = list(joints.keys())
    ix = {n: i for i, n in enumerate(names)}
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(joints[n]) for n in names], [(ix[a], ix[b]) for a, b in edges], [])
    me.update()
    o = new_obj(name, me)
    m = o.modifiers.new("skin", "SKIN")
    m.branch_smoothing = branch_smooth
    m.use_smooth_shade = True
    if not me.skin_vertices:
        me.skin_vertices.new() if hasattr(me.skin_vertices, "new") else None
    sv = me.skin_vertices[0].data
    for n in names:
        r = radii[n]
        if isinstance(r, (int, float)):
            r = (r, r)
        sv[ix[n]].radius = r
    sv[ix[root or names[0]]].use_root = True
    if subdiv:
        s = o.modifiers.new("sub", "SUBSURF")
        s.levels = subdiv
        s.render_levels = subdiv
    return _finish(o, material, idx, parent=parent)


def revolve(name, profile, nseg=64, material=None, idx=1, wob=None, parent=None, loc=(0, 0, 0), rot=(0, 0, 0), subdiv=1):
    """Superficie de revolución: profile = [(radio, z)...]; wob(theta, r, z)->(dx, dz) para ondular (ala del sombrero)."""
    me = bpy.data.meshes.new(name)
    verts, faces = [], []
    n = len(profile)
    for i in range(nseg):
        th = 2 * math.pi * i / nseg
        for r, z in profile:
            dx, dz = wob(th, r, z) if wob else (0, 0)
            rr = r + dx
            verts.append((math.cos(th) * rr, math.sin(th) * rr, z + dz))
    for i in range(nseg):
        j = (i + 1) % nseg
        for k in range(n - 1):
            faces.append((i * n + k, j * n + k, j * n + k + 1, i * n + k + 1))
    me.from_pydata(verts, [], faces)
    me.update()
    o = new_obj(name, me)
    o.location = loc
    o.rotation_euler = Euler(rot)
    if subdiv:
        s = o.modifiers.new("sub", "SUBSURF")
        s.levels = subdiv
        s.render_levels = subdiv
    return _finish(o, material, idx, parent=parent)


def mesh_from(name, verts, faces, material=None, idx=1, parent=None, subdiv=0, solid=0.0, closed=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    bm = bmesh.new(); bm.from_mesh(me)
    if closed:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    o = new_obj(name, me)
    if solid:
        s = o.modifiers.new("solid", "SOLIDIFY")
        s.thickness = solid
    if subdiv:
        s = o.modifiers.new("sub", "SUBSURF")
        s.levels = subdiv
        s.render_levels = subdiv
    return _finish(o, material, idx, parent=parent)


def boolean(obj, cutter, op="DIFFERENCE"):
    m = obj.modifiers.new("cut", "BOOLEAN")
    m.object = cutter
    m.operation = op
    m.solver = "EXACT"
    cutter.hide_render = True
    cutter.hide_viewport = True
    return m


def rbox(name, loc, size, rot=(0, 0, 0), material=None, idx=1, bevel=0.01, parent=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(me)
    bm.free()
    o = new_obj(name, me)
    o.location = loc
    o.scale = size
    o.rotation_euler = Euler(rot)
    b = o.modifiers.new("bev", "BEVEL")
    b.width = bevel / max(min(size), 1e-3)
    b.segments = 3
    s = o.modifiers.new("sub", "SUBSURF")
    s.levels = 1
    s.render_levels = 1
    return _finish(o, material, idx, parent=parent)


def mesh_np(name, v, f, material=None, idx=1, parent=None, smooth=True):
    """Malla desde arrays NumPy (rápido, para SDF/marching cubes)."""
    import numpy as np
    me = bpy.data.meshes.new(name)
    nv, nf = len(v), len(f)
    me.vertices.add(nv)
    me.vertices.foreach_set("co", np.asarray(v, dtype=np.float32).ravel())
    me.loops.add(nf * 3)
    me.loops.foreach_set("vertex_index", np.asarray(f, dtype=np.int32).ravel())
    me.polygons.add(nf)
    me.polygons.foreach_set("loop_start", np.arange(0, nf * 3, 3, dtype=np.int32))
    me.polygons.foreach_set("loop_total", np.full(nf, 3, dtype=np.int32))
    me.polygons.foreach_set("use_smooth", np.full(nf, smooth, dtype=bool))
    me.update(); me.validate()
    o = new_obj(name, me)
    return _finish(o, material, idx, smooth=False, parent=parent)
