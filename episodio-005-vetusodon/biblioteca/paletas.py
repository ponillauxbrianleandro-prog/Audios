"""Paletas dominantes para escenas del documental (cada escena = un color dominante).

Cada paleta es un dict con colores RGB (tuplas 0-255):
  nombre, dom, cielo[3] (cenit, medio, horizonte), sol, luz, sombra, contorno, bruma,
  hoja[3] (claro, medio, oscuro), hoja2[3] (acento seco/amarillo), corteza[3], roca[3],
  suelo[3], agua[2], seco[3], hongo[3], montana[2] (cerca, lejos)
Uso:  from paletas import PALETAS, obtener, mezclar
"""


def _m(a, b, t):
    return tuple(round(a[i] * (1 - t) + b[i] * t) for i in range(3))


def _e(c, k):
    return tuple(int(max(0, min(255, round(v * k)))) for v in c)


def _tri(base, luz, sombra, k_claro=1.35, k_osc=0.55):
    """Terna (claro, medio, oscuro) a partir de un color base."""
    return (_m(_e(base, k_claro), luz, .22), base, _m(_e(base, k_osc), sombra, .4))


def _mk(nombre, cielo, sol, luz, sombra, contorno, bruma, hoja, hoja2, corteza,
        roca, suelo, agua, seco, hongo, dom):
    return dict(
        nombre=nombre, dom=dom, cielo=list(cielo), sol=sol, luz=luz, sombra=sombra,
        contorno=contorno, bruma=bruma,
        hoja=list(_tri(hoja, luz, sombra)), hoja2=list(_tri(hoja2, luz, sombra)),
        corteza=list(_tri(corteza, luz, sombra)), roca=list(_tri(roca, luz, sombra, 1.3, .5)),
        suelo=list(_tri(suelo, luz, sombra, 1.25, .6)), agua=[agua[0], agua[1]],
        seco=list(_tri(seco, luz, sombra)), hongo=list(_tri(hongo, luz, sombra)),
        montana=[_m(roca, bruma, .55), _m(roca, bruma, .85)],
    )


PALETAS = {
    "ambar": _mk("ambar", [(92, 78, 112), (226, 146, 78), (255, 206, 128)], (255, 224, 150),
                 (255, 214, 150), (92, 50, 62), (40, 22, 16), (244, 184, 116),
                 (126, 124, 52), (176, 140, 64), (140, 96, 62), (150, 108, 90),
                 (170, 108, 66), ((246, 176, 104), (120, 74, 84)), (176, 134, 76),
                 (206, 150, 96), (255, 190, 100)),
    "violeta": _mk("violeta", [(48, 38, 82), (118, 90, 150), (206, 170, 204)], (240, 210, 236),
                   (232, 204, 244), (46, 30, 74), (24, 14, 30), (178, 152, 200),
                   (90, 112, 104), (150, 120, 130), (96, 76, 92), (112, 98, 126),
                   (118, 92, 108), ((214, 180, 220), (70, 52, 96)), (136, 116, 124),
                   (176, 130, 170), (160, 120, 200)),
    "verde": _mk("verde", [(60, 96, 86), (116, 160, 128), (206, 228, 184)], (236, 244, 190),
                 (224, 240, 168), (22, 50, 42), (16, 24, 16), (176, 208, 168),
                 (86, 124, 62), (146, 142, 60), (104, 88, 62), (104, 112, 92),
                 (84, 72, 46), ((170, 214, 170), (36, 80, 70)), (140, 130, 80),
                 (196, 170, 110), (90, 170, 90)),
    "azul": _mk("azul", [(26, 46, 90), (78, 120, 172), (184, 214, 230)], (214, 232, 255),
                (200, 224, 255), (18, 32, 68), (12, 18, 30), (164, 196, 218),
                (60, 120, 122), (110, 140, 130), (86, 92, 108), (96, 112, 132),
                (86, 98, 112), ((176, 210, 236), (30, 60, 100)), (120, 130, 130),
                (150, 170, 196), (90, 140, 210)),
    "rojo": _mk("rojo", [(56, 26, 56), (188, 58, 52), (252, 142, 72)], (255, 190, 110),
                (255, 172, 112), (66, 20, 40), (34, 14, 14), (232, 120, 84),
                (120, 92, 48), (170, 70, 46), (112, 66, 52), (140, 86, 78),
                (150, 66, 46), ((250, 140, 80), (90, 34, 52)), (170, 96, 60),
                (210, 110, 80), (220, 80, 60)),
    "ocre": _mk("ocre", [(146, 160, 176), (232, 200, 142), (252, 228, 176)], (255, 238, 180),
                (255, 232, 168), (108, 70, 44), (46, 30, 18), (240, 214, 166),
                (140, 130, 70), (188, 150, 80), (140, 100, 62), (176, 140, 100),
                (206, 160, 98), ((240, 214, 160), (130, 98, 70)), (190, 150, 90),
                (214, 170, 110), (230, 180, 100)),
    "ceniza": _mk("ceniza", [(62, 62, 68), (118, 116, 116), (178, 172, 166)], (226, 218, 204),
                  (222, 216, 206), (38, 36, 44), (20, 18, 20), (176, 170, 164),
                  (88, 98, 78), (120, 112, 90), (104, 96, 92), (112, 108, 106),
                  (108, 102, 96), ((184, 180, 176), (56, 56, 64)), (130, 122, 112),
                  (150, 146, 140), (150, 150, 150)),
}
# alias con los nombres del pedido
PALETAS["ambar_amanecer"] = PALETAS["ambar"]
PALETAS["violeta_bruma"] = PALETAS["violeta"]
PALETAS["verde_humedo"] = PALETAS["verde"]
PALETAS["azul_frio"] = PALETAS["azul"]
PALETAS["rojo_atardecer"] = PALETAS["rojo"]
PALETAS["ocre_desierto"] = PALETAS["ocre"]
PALETAS["gris_ceniza"] = PALETAS["ceniza"]

NOMBRES = ["ambar", "violeta", "verde", "azul", "rojo", "ocre", "ceniza"]


def obtener(nombre):
    return PALETAS[nombre] if isinstance(nombre, str) else nombre


def mezclar(p1, p2, t=0.5):
    """Mezcla dos paletas (transicion entre escenas)."""
    p1, p2 = obtener(p1), obtener(p2)
    def mm(a, b):
        if isinstance(a, tuple):
            return _m(a, b, t)
        if isinstance(a, list):
            return [mm(x, y) for x, y in zip(a, b)]
        return a
    out = {k: mm(p1[k], p2[k]) for k in p1}
    out["nombre"] = f"{p1['nombre']}+{p2['nombre']}"
    return out
