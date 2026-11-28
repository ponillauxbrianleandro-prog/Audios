import bpy, time, sys
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 16; sc.cycles.use_denoising = False
sc.render.resolution_x, sc.render.resolution_y = 640, 480
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1)); bpy.ops.mesh.primitive_plane_add(size=10)
bpy.ops.object.light_add(type='SUN', rotation=(0.8, 0.2, 0.5)); bpy.ops.object.camera_add(location=(4, -5, 3), rotation=(1.1, 0, 0.8)); sc.camera = bpy.context.object
sc.render.image_settings.file_format = 'OPEN_EXR'; sc.render.image_settings.color_depth = '32'; sc.render.filepath = sys.argv[-1]
t = time.time(); bpy.ops.render.render(write_still=True); print("render s", round(time.time() - t, 1))
