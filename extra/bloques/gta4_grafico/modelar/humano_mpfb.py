"""Cuerpo humano anatomico via MPFB2 (MakeHuman para Blender) en bpy headless. Requiere /root/bl/mpfb2 (git clone makehumancommunity/mpfb2)."""
import sys, os, importlib, bpy
MPFB_SRC = os.environ.get("MPFB_SRC", "/root/bl/mpfb2/src")


def cargar_mpfb():
    """Carga MPFB2 con nombre de extension de Blender (bl_ext.user_default.mpfb) para que sus rutas funcionen en headless."""
    import importlib.util, types
    nombre = "bl_ext.user_default.mpfb"
    if nombre in sys.modules: return sys.modules[nombre]
    for n in ("bl_ext", "bl_ext.user_default"):
        if n not in sys.modules:
            m = types.ModuleType(n); m.__path__ = []; sys.modules[n] = m
    ruta = os.path.join(MPFB_SRC, "mpfb")
    spec = importlib.util.spec_from_file_location(nombre, os.path.join(ruta, "__init__.py"), submodule_search_locations=[ruta])
    mod = importlib.util.module_from_spec(spec); sys.modules[nombre] = mod; spec.loader.exec_module(mod)
    DEF = {"mpfb_shelf_label": "MPFB", "mpfb_second_shelf_label": "MPFB", "mpfb_third_shelf_label": "MPFB"}
    mod.get_preference = lambda name: DEF.get(name, "MPFB" if "label" in name else (False if name.startswith(("use", "show", "is", "dev")) else None))
    mod.set_preference = lambda name, value: None
    try: mod.register()
    except Exception as e: print("registro mpfb:", repr(e)[:300])
    return mod


def dyn(pkg, key):
    for m in list(sys.modules):
        if m.endswith(pkg):
            mod = importlib.import_module(m)
            if hasattr(mod, key): return getattr(mod, key)
    raise ValueError(pkg)


def objetivo(h, TS, nombre, valor):
    """Carga/aplica un target de detalle de MPFB (p.ej. 'torso/torso-muscle-pectoral-incr')."""
    ruta = TS.target_full_path(nombre.split("/")[-1])
    if ruta is None: print("target no encontrado:", nombre); return False
    TS.load_target(h, ruta, weight=valor); return True


def crear_humano(genero=1.0, musculo=1.0, peso=0.5, altura=0.7, edad=0.5, raza=(0.6, 0.2, 0.2), detalles=None, rig="default"):
    cargar_mpfb(); P = "bl_ext.user_default.mpfb"
    HS = importlib.import_module(P + ".services.humanservice").HumanService
    TS = importlib.import_module(P + ".services.targetservice").TargetService
    HP = importlib.import_module(P + ".entities.objectproperties").HumanObjectProperties
    h = HS.create_human(mask_helpers=True, detailed_helpers=True, extra_vertex_groups=True, feet_on_ground=True, scale=0.1)
    for k, v in dict(gender=genero, muscle=musculo, weight=peso, height=altura, age=edad, proportions=0.5).items(): HP.set_value(k, v, entity_reference=h)
    for k, v in zip(("caucasian", "african", "asian"), raza): HP.set_value(k, v, entity_reference=h)
    TS.reapply_macro_details(h)
    for nombre, v in (detalles or {}).items(): objetivo(h, TS, nombre, v)
    arm = HS.add_builtin_rig(h, rig, import_weights=True) if rig else None
    return h, TS, arm
