"""Render por pasadas (Cycles CPU, sin GPU): beauty, albedo, normal, depth, objectID, AO, alpha.
Uso: python render_passes.py <personaje_dir> <pose> <out_dir> [ancho alto samples]"""
import os, sys, math, importlib.util
import numpy as np
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lib import reset


def load_char(char_dir):
    spec = importlib.util.spec_from_file_location("charbuild", os.path.join(char_dir, "build.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def light(name, kind, loc, target, energy, color=(1, 1, 1), size=1.0):
    d = bpy.data.lights.new(name, kind)
    d.energy = energy
    d.color = color
    if kind == "AREA":
        d.size = size
    if kind == "SUN":
        d.angle = math.radians(size)
    o = bpy.data.objects.new(name, d)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return o


def setup(W, H, samples, cam):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 4
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.film_transparent = True
    sc.view_settings.view_transform = "Standard"
    vl = bpy.context.view_layer
    vl.use_pass_z = True
    vl.use_pass_normal = True
    vl.use_pass_diffuse_color = True
    vl.use_pass_object_index = True
    vl.use_pass_ambient_occlusion = True
    # mundo: cielo cálido de atardecer (iluminación ambiente suave)
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.62, 0.66, 0.78, 1)
    bg.inputs["Strength"].default_value = 0.55
    # cámara
    cd = bpy.data.cameras.new("cam")
    cd.lens = cam["lens"]
    co = bpy.data.objects.new("cam", cd)
    bpy.context.scene.collection.objects.link(co)
    co.location = cam["loc"]
    co.rotation_euler = (Vector(cam["look"]) - Vector(cam["loc"])).to_track_quat("-Z", "Y").to_euler()
    sc.camera = co
    # luces: key cálida lateral, relleno frío, contraluz (rim)
    k = cam.get("key", (-3.5, -3.0, 4.0))
    light("key", "SUN", k, (0, 0, 1.2), 2.4, (1.0, 0.88, 0.72), 3)
    light("fill", "AREA", (3.5, -3.5, 1.5), (0, 0, 1.2), 140, (0.62, 0.74, 1.0), 4)
    light("rim", "AREA", (2.5, 3.0, 2.8), (0, 0, 1.4), 380, (1.0, 0.82, 0.62), 2.5)
    light("kick", "AREA", (-3.0, 2.5, 1.0), (0, 0, 1.2), 160, (0.7, 0.8, 1.0), 2.0)


def data_mat(kind):
    """Material de override para pasadas de datos (emisión pura)."""
    m = bpy.data.materials.new("data_" + kind)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(em.outputs[0], out.inputs[0])
    if kind == "normal":
        g = nt.nodes.new("ShaderNodeNewGeometry")
        vm = nt.nodes.new("ShaderNodeVectorMath"); vm.operation = "MULTIPLY_ADD"
        vm.inputs[1].default_value = (0.5, 0.5, 0.5); vm.inputs[2].default_value = (0.5, 0.5, 0.5)
        # normal en espacio de cámara (view space)
        tr = nt.nodes.new("ShaderNodeVectorTransform"); tr.vector_type = "NORMAL"; tr.convert_from = "WORLD"; tr.convert_to = "CAMERA"
        nt.links.new(g.outputs["Normal"], tr.inputs[0])
        nt.links.new(tr.outputs[0], vm.inputs[0])
        nt.links.new(vm.outputs[0], em.inputs["Color"])
    elif kind == "depth":
        cd = nt.nodes.new("ShaderNodeCameraData")
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = 3.5
        mr.inputs["From Max"].default_value = 10.5
        mr.inputs["To Min"].default_value = 1.0
        mr.inputs["To Max"].default_value = 0.0
        nt.links.new(cd.outputs["View Z Depth"], mr.inputs["Value"])
        nt.links.new(mr.outputs["Result"], em.inputs["Color"])
    elif kind == "id":
        oi = nt.nodes.new("ShaderNodeObjectInfo")
        dv = nt.nodes.new("ShaderNodeMath"); dv.operation = "DIVIDE"; dv.inputs[1].default_value = 255.0
        nt.links.new(oi.outputs["Object Index"], dv.inputs[0])
        nt.links.new(dv.outputs[0], em.inputs["Color"])
    elif kind == "ao":
        ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
        ao.inputs["Distance"].default_value = 0.35
        ao.samples = 16
        nt.links.new(ao.outputs["Color"], em.inputs["Color"])
        ao.inputs["Color"].default_value = (1, 1, 1, 1)
    return m


def albedo_convert():
    """Convierte todos los materiales a emisión de su Base Color (albedo plano)."""
    for m in bpy.data.materials:
        if not m.use_nodes or m.name.startswith("data_"):
            continue
        nt = m.node_tree
        bsdf = nt.nodes.get("Principled BSDF")
        out = [n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"][0]
        em = nt.nodes.new("ShaderNodeEmission")
        bc = bsdf.inputs["Base Color"]
        if bc.links:
            nt.links.new(bc.links[0].from_socket, em.inputs["Color"])
        else:
            em.inputs["Color"].default_value = bc.default_value
        nt.links.new(em.outputs[0], out.inputs["Surface"])


def render_to(path, transform="Standard", denoise=True, samples=None, filt=None, depth16=True):
    sc = bpy.context.scene
    sc.view_settings.view_transform = transform
    sc.cycles.use_denoising = denoise
    if samples:
        sc.cycles.samples = samples
    sc.render.filter_size = filt if filt is not None else 1.5
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.image_settings.color_depth = "16" if depth16 else "8"
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def write_meta(cb, root, path, W, H):
    import json
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene
    bpy.context.view_layer.update()
    def proj(v):
        co = world_to_camera_view(sc, sc.camera, root.matrix_world @ Vector(v))
        return co.x * W, (1 - co.y) * H
    hx, hy = proj(cb.META["head"])
    hz = Vector(cb.META["head"])
    rx, ry = proj(tuple(hz + Vector((0.11, 0, 0))))
    fx = (proj(cb.META["anG"])[0] + proj(cb.META["anF"])[0]) / 2
    fy = (proj(cb.META["anG"])[1] + proj(cb.META["anF"])[1]) / 2 + 0.09 * H * 0.2
    top = proj((0, 0, 1.95))[1]
    deck_y = proj((0, 3.0, 0))[1]
    meta = dict(head=[hx, hy, max(8.0, abs(rx - hx)) * 1.2, 0], feet=[fx, fy, abs(fy - top), deck_y])
    json.dump(meta, open(path, 'w'))
    print("META", meta)


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    char_dir, pose, out = args[0], args[1], args[2]
    W, H, S = (int(args[3]), int(args[4]), int(args[5])) if len(args) >= 6 else (1600, 1000, 48)
    os.makedirs(out, exist_ok=True)
    reset()
    cb = load_char(char_dir)
    root = cb.build(pose)
    cam = cb.CAMERAS[pose]
    setup(W, H, S, cam)
    write_meta(cb, root, os.path.join(out, pose + '_meta.json'), W, H)
    vl = bpy.context.view_layer
    base = os.path.join(out, pose)
    # 1) beauty (iluminación Cycles completa, base del pintado)
    render_to(base + "_beauty.png", "Standard", True, S)
    # 2) datos: normal / depth / id / ao con material override
    for kind, den, smp, filt in (("normal", False, 4, 1.5), ("depth", False, 4, 1.5), ("id", False, 1, 0.01), ("ao", True, 24, 1.5)):
        vl.material_override = data_mat(kind)
        render_to(f"{base}_{kind}.png", "Raw", den, smp, filt)
    vl.material_override = None
    # 3) albedo plano
    albedo_convert()
    render_to(base + "_albedo.png", "Standard", False, 4)
    print("PASADAS OK", out)


if __name__ == "__main__":
    main()
