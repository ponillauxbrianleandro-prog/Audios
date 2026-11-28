import sys, os, time, bpy
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "modelar"))
from base import limpiar, mat, asignar; import humano_mpfb as hm, pose as ps, vaquero as vq
a = sys.argv; out = a[a.index("--out") + 1]; pose = a[a.index("--pose") + 1] if "--pose" in a else "posando"
sc = limpiar(); h, TS, arm = hm.crear_humano(genero=1.0, musculo=1.0, peso=0.62, altura=0.72, rig="game_engine", detalles={**{"torso/torso-muscle-pectoral-incr": 1.0, "torso/torso-muscle-dorsi-incr": 1.0}, **{f"arms/{s}-{m}-incr": 1.0 for s in "lr" for m in ("upperarm-muscle", "lowerarm-muscle", "upperarm-shoulder-muscle")}, **{f"legs/{s}-{m}-muscle-incr": 1.0 for s in "lr" for m in ("upperleg", "lowerleg")}})
asignar(h, mat("piel", (.72, .46, .32, 1), .5, sss=.12))
bpy.context.view_layer.update()
altura = max(v.co.z for v in h.data.vertices if True); esc = 1.0
print("altura aprox", altura)
ps.posar(arm, vq.POSES[pose], 1.0)
# apoyar pies en el suelo
dg = bpy.context.evaluated_depsgraph_get(); ev = h.evaluated_get(dg); me = ev.to_mesh(); minz = min((ev.matrix_world @ v.co).z for v in me.vertices); ev.to_mesh_clear(); arm.location.z -= minz; print("minz", minz)
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 24; sc.cycles.use_denoising = True; sc.render.resolution_x, sc.render.resolution_y = 700, 900
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (.8, .85, .9, 1); w.node_tree.nodes["Background"].inputs[1].default_value = .35
bpy.ops.object.light_add(type='AREA', location=(-2.2, -2.5, 3.2)); k = bpy.context.object; k.data.energy = 220; k.data.size = 1.5; k.rotation_euler = (1.0, 0, -0.6)
bpy.ops.object.light_add(type='AREA', location=(2.6, -1.0, 2.0)); r = bpy.context.object; r.data.energy = 90; r.data.size = 1.2; r.rotation_euler = (1.3, 0, 1.2)
bpy.ops.mesh.primitive_plane_add(size=20); bpy.context.object.data.materials.append(mat("suelo", (.25, .25, .25, 1), .9))
bpy.ops.object.camera_add(location=(0.4, -4.2, 1.0), rotation=(1.5, 0, 0.1)); bpy.context.object.data.lens = 50; sc.camera = bpy.context.object
sc.view_settings.view_transform = 'Standard'; sc.render.filepath = out; sc.render.image_settings.file_format = 'PNG'
t = time.time(); bpy.ops.render.render(write_still=True); print("render s", round(time.time() - t, 1))
