import sys, os, time, bpy
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "modelar"))
from base import *; import vaquero as vq
pose = sys.argv[sys.argv.index("--pose") + 1] if "--pose" in sys.argv else "posando"; out = sys.argv[sys.argv.index("--out") + 1]
cam = sys.argv[sys.argv.index("--cam") + 1] if "--cam" in sys.argv else "cuerpo"
sc = limpiar(); P = vq.POSES[pose]
piel = mat("piel", (.72, .46, .32, 1), .55, sss=.15)
ojo = mat("ojo", (.9, .9, .88, 1), .15)
cuerpo = vq.construir_cuerpo(P); asignar(cuerpo, piel)
cab, ojos = vq.construir_cabeza(P, piel, ojo)
# luz y camara
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 24; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = (700, 900) if cam == "cuerpo" else (800, 800)
world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True; world.node_tree.nodes["Background"].inputs[0].default_value = (.8, .85, .9, 1); world.node_tree.nodes["Background"].inputs[1].default_value = .35
bpy.ops.object.light_add(type='AREA', location=(-2.2, -2.5, 3.2)); k = bpy.context.object; k.data.energy = 220; k.data.size = 1.5; k.rotation_euler = (1.0, 0, -0.6)
bpy.ops.object.light_add(type='AREA', location=(2.6, -1.0, 2.0)); r = bpy.context.object; r.data.energy = 90; r.data.size = 1.2; r.rotation_euler = (1.3, 0, 1.2)
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0)); bpy.context.object.data.materials.append(mat("suelo", (.25, .25, .25, 1), .9))
if cam == "cuerpo": bpy.ops.object.camera_add(location=(0.2, -3.9, 1.0), rotation=(1.5, 0, 0.05)); bpy.context.object.data.lens = 50
else: bpy.ops.object.camera_add(location=(0.0, -1.5, 1.74), rotation=(1.55, 0, 0.0)); bpy.context.object.data.lens = 85
sc.camera = bpy.context.object
sc.view_settings.view_transform = 'Standard'; sc.render.filepath = out; sc.render.image_settings.file_format = 'PNG'
t = time.time(); bpy.ops.render.render(write_still=True); print("render s", round(time.time() - t, 1))
