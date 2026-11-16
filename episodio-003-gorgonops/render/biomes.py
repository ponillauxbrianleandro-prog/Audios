"""Biomas: mismos motor y calidad, distinta flora, suelo, agua y luz.

Cada bioma = reglas de reparto de plantas + clima (wx). Las reglas se evalúan en orden:
p = probabilidad por candidato (hay ~5,5 candidatos por m²), dmin/dmax = distancia a la
orilla (m), vmin = humedad del suelo, cmin/cmax = ruido de agrupación, box = (x0,x1,z0,z1).
"""

_BASE = [
    dict(kind="horsetail", p=0.30, dmin=-0.45, dmax=2.6, cmin=0.50, zmax=200, sc=(0.45, 1.2)),
    dict(kind="horsetail", p=0.05, dmin=-0.30, dmax=4.5, zmax=160, sc=(0.4, 1.0)),
    dict(kind="treefern", p=0.005, dmin=2.0, dmax=30, vmin=0.48, zmax=170, sc=(0.7, 1.2)),
    dict(kind="fern", p=0.05, dmin=1.2, dmax=40, vmin=0.42, zmax=140, sc=(0.5, 1.2)),
    dict(kind="lycopsid", p=0.06, dmin=0.8, dmax=60, vmin=0.40, zmax=80, sc=(0.6, 1.3)),
    dict(kind="shrub", p=0.008, dmin=3.0, dmax=80, vmin=0.42, zmax=230, sc=(0.6, 1.2)),
    dict(kind="tree", p=0.020, dmin=6.0, cmin=0.52, zmin=22, sc=(0.7, 1.25)),
    dict(kind="tree", p=0.018, dmin=5.0, zmin=120, sc=(0.7, 1.2)),
    dict(kind="conifer", p=0.005, dmin=30, zmin=60, sc=(0.7, 1.2)),
    dict(kind="rock", p=0.0030, zmax=90, sc=(0.5, 1.3)),
    dict(kind="log", p=0.0005, dmin=1.0, zmax=70, sc=(0.7, 1.1)),
]

MARSH_BOX = (8, 62, 18, 92)
FOREST_BOX = (-126, -34, 38, 235)
SLOPE_BOX = (52, 128, 88, 335)

BIOMES = {
    # llanura aluvial al amanecer: fría, brumosa, verde junto al agua
    "ribera": dict(flora=_BASE, wx=dict(plume=0.30, mist=0.55, insects=4)),

    # pantano: la cámara vive entre colas de caballo, helechos y licófitas
    "pantano": dict(
        flora=[
            dict(kind="horsetail", p=0.55, dmin=-0.7, dmax=6.5, box=MARSH_BOX, sc=(0.5, 1.3)),
            dict(kind="treefern", p=0.030, dmin=1.0, dmax=30, box=MARSH_BOX, sc=(0.7, 1.25)),
            dict(kind="fern", p=0.26, dmin=0.4, dmax=22, box=MARSH_BOX, sc=(0.5, 1.25)),
            dict(kind="lycopsid", p=0.22, dmin=0.3, dmax=30, box=MARSH_BOX, sc=(0.6, 1.4)),
            dict(kind="shrub", p=0.03, dmin=3.0, dmax=40, box=MARSH_BOX),
            dict(kind="tree", p=0.035, dmin=7.0, box=MARSH_BOX, sc=(0.7, 1.2)),
            dict(kind="log", p=0.004, dmin=0.5, box=MARSH_BOX),
        ] + _BASE,
        wx=dict(mist=0.75, moss=1.25, moss_bias=0.22, insects=9, plume=0.2, cloud=0.55,
                light=dict(sun=(0.95, 0.93, 0.86), amb=(0.64, 0.74, 0.84), fog=(0.79, 0.86, 0.89))),
    ),

    # bosque de Glossopteris: troncos, sotobosque denso, hojarasca, luz filtrada
    "bosque": dict(
        flora=[
            dict(kind="tree_hi", p=0.012, dmin=6.0, box=FOREST_BOX, sc=(0.8, 1.3)),
            dict(kind="tree", p=0.042, dmin=6.0, box=FOREST_BOX, sc=(0.7, 1.3)),
            dict(kind="treefern", p=0.035, box=FOREST_BOX, sc=(0.7, 1.3)),
            dict(kind="conifer", p=0.010, box=FOREST_BOX, sc=(0.8, 1.2)),
            dict(kind="fern", p=0.13, box=FOREST_BOX, sc=(0.5, 1.3)),
            dict(kind="lycopsid", p=0.07, box=FOREST_BOX, sc=(0.6, 1.4)),
            dict(kind="shrub", p=0.05, box=FOREST_BOX, sc=(0.6, 1.2)),
            dict(kind="log", p=0.006, box=FOREST_BOX),
            dict(kind="rock", p=0.004, box=FOREST_BOX),
        ] + _BASE,
        wx=dict(mist=0.35, litter=0.85, moss=1.2, plant_tint=(0.80, 0.84, 0.80), moss_bias=0.15, cloud_shadow=0.55, cloud=0.6, shadow=0.6, insects=6,
                plume=0.0, soil_a=(0.50, 0.45, 0.38), soil_b=(0.33, 0.29, 0.25),
                light=dict(sun=(0.86, 0.86, 0.76), amb=(0.52, 0.64, 0.66), fog=(0.70, 0.80, 0.80)),
                grade=dict(expo=1.06)),
    ),

    # ladera alta y seca: coníferas dispersas, roca, vista sobre la llanura
    "ladera": dict(
        flora=[
            dict(kind="conifer", p=0.040, box=SLOPE_BOX, sc=(0.7, 1.25)),
            dict(kind="shrub", p=0.022, box=SLOPE_BOX, sc=(0.5, 1.0)),
            dict(kind="rock", p=0.016, box=SLOPE_BOX, sc=(0.6, 1.6)),
            dict(kind="fern", p=0.03, box=SLOPE_BOX, sc=(0.4, 0.9)),
            dict(kind="lycopsid", p=0.04, box=SLOPE_BOX),
            dict(kind="log", p=0.002, box=SLOPE_BOX),
        ] + _BASE,
        wx=dict(mist=0.25, moss=0.6, plume=0.35, insects=2, soil_a=(0.68, 0.63, 0.56), soil_b=(0.50, 0.45, 0.41)),
    ),

    # el mismo valle en la estación seca: el río se retira, barro agrietado, hojas caídas
    "seco": dict(
        dry=2.3,
        flora=[
            dict(kind="horsetail_dry", p=0.18, dmin=0.2, dmax=5.5, cmin=0.48, zmax=200, sc=(0.4, 1.05)),
            dict(kind="horsetail", p=0.05, dmin=-0.3, dmax=1.2, zmax=160, sc=(0.4, 0.9)),
            dict(kind="fern_dry", p=0.030, dmin=1.2, dmax=40, vmin=0.42, zmax=140, sc=(0.45, 1.0)),
            dict(kind="shrub_dry", p=0.008, dmin=3.0, dmax=80, vmin=0.42, zmax=230),
            dict(kind="tree_autumn", p=0.012, dmin=6.0, cmin=0.52, zmin=22, sc=(0.7, 1.25)),
            dict(kind="tree_bare", p=0.009, dmin=6.0, cmin=0.50, zmin=22, sc=(0.7, 1.25)),
            dict(kind="tree_autumn", p=0.016, dmin=5.0, zmin=120),
            dict(kind="conifer", p=0.005, dmin=30, zmin=60),
            dict(kind="rock", p=0.004, zmax=90, sc=(0.5, 1.3)),
            dict(kind="log", p=0.0012, dmin=1.0, zmax=80),
        ],
        wx=dict(mist=0.0, litter=0.5, cracks=1.0, moss=0.22, dust=0.55, leaves=26, plume=0.75, cloud=0.22,
                insects=2, wind=1.5, soil_a=(0.70, 0.67, 0.61), soil_b=(0.53, 0.50, 0.46),
                zenith=(0.56, 0.68, 0.84), horizon=(0.88, 0.88, 0.86),
                light=dict(sun=(1.0, 0.97, 0.90), amb=(0.66, 0.72, 0.82), fog=(0.84, 0.85, 0.85)),
                grade=dict(sat=0.9)),
    ),

    # después de la extinción: casi nada
    "extincion": dict(
        dry=4.6,
        flora=[
            dict(kind="tree_bare", p=0.006, dmin=6.0, zmin=18, sc=(0.6, 1.1)),
            dict(kind="horsetail_dry", p=0.015, dmin=0.2, dmax=4.0, zmax=120, sc=(0.3, 0.8)),
            dict(kind="log", p=0.003, zmax=120),
            dict(kind="rock", p=0.006, zmax=110, sc=(0.5, 1.4)),
        ],
        wx=dict(mist=0.0, cracks=1.0, moss=0.0, dust=1.0, plume=1.0, cloud=0.15, insects=0, motes=1.6, wind=1.8,
                mote_col=(0.9, 0.82, 0.7), soil_a=(0.74, 0.70, 0.64), soil_b=(0.58, 0.54, 0.49),
                zenith=(0.66, 0.70, 0.76), horizon=(0.86, 0.84, 0.80),
                light=dict(sun=(1.0, 0.95, 0.88), amb=(0.72, 0.74, 0.78), fog=(0.84, 0.82, 0.79)),
                grade=dict(sat=0.62, expo=1.05)),
    ),
}

# luces del día: se superponen al clima del bioma
DUSK = dict(zenith=(0.44, 0.52, 0.74), horizon=(0.95, 0.80, 0.66), mist=0.25,
            light=dict(sun=(1.0, 0.80, 0.60), amb=(0.50, 0.56, 0.74), fog=(0.84, 0.78, 0.74)),
            grade=dict(tint=(1.03, 0.98, 0.95)))
NIGHT = dict(zenith=(0.10, 0.15, 0.30), horizon=(0.26, 0.34, 0.50), mist=0.35, cloud=0.25, insects=0, plume=0.0,
             light=dict(sun=(0.40, 0.50, 0.72), amb=(0.22, 0.30, 0.48), fog=(0.26, 0.33, 0.48)),
             plant_tint=(0.42, 0.52, 0.72), stars=1.0, pano_tint=(0.35, 0.45, 0.65), grade=dict(sat=0.7, expo=1.25))
NOON = dict(mist=0.15, zenith=(0.44, 0.63, 0.88), horizon=(0.84, 0.90, 0.95), cloud=0.38)
RAIN = dict(rain=1.0, rough=2.2, cloud=0.95, mist=0.8, zenith=(0.62, 0.67, 0.73), horizon=(0.80, 0.83, 0.86), shadow=0.35,
            cloud_shadow=0.0, light=dict(sun=(0.70, 0.72, 0.74), amb=(0.66, 0.72, 0.80), fog=(0.78, 0.82, 0.86)),
            grade=dict(sat=0.85))
