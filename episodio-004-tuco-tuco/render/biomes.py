"""Biomas: mismos motor y calidad, distinta flora, suelo, agua y luz.

Cada bioma = reglas de reparto de plantas + clima (wx). Las reglas se evalúan en orden:
p = probabilidad por candidato (hay ~5,5 candidatos por m²), dmin/dmax = distancia a la
orilla (m), vmin = humedad del suelo, cmin/cmax = ruido de agrupación, box = (x0,x1,z0,z1).
"""

# Capas del reparto (la primera regla que acierta se queda con el candidato, por eso van primero las altas):
#   gigantes lejanos (z > 240, sobre las sierras) · árboles de plano medio · franja del animal (plantas bajas) · cubierta del suelo
_FAR = [
    dict(kind="conifer", p=0.060, dmin=-99, zmin=240, sc=(2.6, 5.0)),
    dict(kind="tree", p=0.040, dmin=-99, zmin=240, sc=(2.2, 4.2)),
    dict(kind="cordaites", p=0.020, dmin=-99, zmin=240, sc=(2.0, 3.6)),
]
_BASE = _FAR + [
    dict(kind="outcrop", p=0.0016, dmin=2.0, zmin=12, zmax=170, cmin=0.52, sc=(0.6, 1.4)),
    dict(kind="rock_moss", p=0.006, dmin=0.8, zmax=120, sc=(0.6, 1.5)),
    dict(kind="hongo", p=0.030, dmin=0.8, vmin=0.45, zmax=35, cmin=0.55, sc=(0.8, 1.5)),
    dict(kind="fern", p=0.16, dmin=1.2, dmax=40, vmin=0.42, zmax=70, cmin=0.62, sc=(0.8, 1.4)),
    dict(kind="cordaites", p=0.006, dmin=7.0, zmin=30, cmin=0.50, sc=(0.8, 1.3)),
    dict(kind="ginkgo", p=0.004, dmin=8.0, zmin=40, cmin=0.55, sc=(0.8, 1.3)),
    dict(kind="calamites", p=0.003, dmin=1.5, dmax=14, zmin=18, zmax=200, sc=(0.8, 1.3)),
    dict(kind="tree", p=0.022, dmin=6.0, cmin=0.52, zmin=22, sc=(0.7, 1.25)),
    dict(kind="tree", p=0.018, dmin=5.0, zmin=120, sc=(0.7, 1.2)),
    dict(kind="conifer", p=0.005, dmin=30, zmin=60, sc=(0.7, 1.2)),
    dict(kind="treefern", p=0.006, dmin=2.0, dmax=30, vmin=0.48, zmax=170, sc=(0.7, 1.2)),
    dict(kind="horsetail", p=0.30, dmin=-0.45, dmax=2.6, cmin=0.50, zmax=200, sc=(0.45, 1.2)),
    dict(kind="horsetail", p=0.05, dmin=-0.30, dmax=4.5, zmax=160, sc=(0.4, 1.0)),
    dict(kind="shrub", p=0.010, dmin=3.0, dmax=80, vmin=0.42, zmax=230, sc=(0.6, 1.2)),
    dict(kind="seedfern", p=0.040, dmin=1.5, dmax=40, vmin=0.42, zmax=120, sc=(0.5, 1.2)),
    dict(kind="fern", p=0.06, dmin=1.2, dmax=40, vmin=0.42, zmax=140, sc=(0.5, 1.2)),
    dict(kind="lycopsid", p=0.07, dmin=0.8, dmax=60, vmin=0.40, zmax=80, sc=(0.6, 1.3)),
    dict(kind="mossmat", p=0.05, dmin=0.6, dmax=40, vmin=0.40, zmax=70, sc=(0.6, 1.4)),
    dict(kind="tree", p=0.012, dmin=3.0, zmin=12, sc=(0.7, 1.2)),
    dict(kind="conifer", p=0.004, dmin=6.0, zmin=18, sc=(0.8, 1.3)),
    dict(kind="shrub", p=0.012, dmin=2.0, zmin=4, zmax=120),
    dict(kind="mossmat", p=0.030, dmin=0.8, zmax=60, sc=(0.6, 1.4)),
    dict(kind="lycopsid", p=0.030, dmin=0.8, zmax=60),
    dict(kind="seedfern", p=0.020, dmin=1.0, zmax=80),
    dict(kind="fern", p=0.020, dmin=1.0, zmax=80),
    dict(kind="stump", p=0.0010, dmin=1.0, zmax=90),
    dict(kind="rock", p=0.0030, zmax=90, sc=(0.5, 1.3)),
    dict(kind="log", p=0.0005, dmin=1.0, zmax=70, sc=(0.7, 1.1)),
]

MARSH_BOX = (8, 62, 18, 92)
FOREST_BOX = (-126, -34, 38, 235)
SLOPE_BOX = (52, 128, 88, 335)

BIOMES = {
    # llanura aluvial al amanecer: fría, brumosa, verde junto al agua
    "ribera": dict(flora=_BASE, wx=dict(plume=0.30, mist=0.55, insects=4, leaves=4, dust=0.12)),

    # pantano: la cámara vive entre colas de caballo, helechos y licófitas
    "pantano": dict(
        bake_z=50.0, thin=(14.0, 150.0, 0.10),
        flora=[
            dict(kind="horsetail", p=0.55, dmin=-0.7, dmax=6.5, box=MARSH_BOX, sc=(0.5, 1.3)),
            dict(kind="treefern", p=0.030, dmin=1.0, dmax=30, box=MARSH_BOX, sc=(0.7, 1.25)),
            dict(kind="fern", p=0.26, dmin=0.4, dmax=22, box=MARSH_BOX, sc=(0.5, 1.25)),
            dict(kind="lycopsid", p=0.22, dmin=0.3, dmax=30, box=MARSH_BOX, sc=(0.6, 1.4)),
            dict(kind="shrub", p=0.03, dmin=3.0, dmax=40, box=MARSH_BOX),
            dict(kind="hongo", p=0.05, dmin=0.5, zmax=40, box=MARSH_BOX, sc=(0.8, 1.5)),
            dict(kind="rock_moss", p=0.008, dmin=0.8, box=MARSH_BOX, sc=(0.6, 1.5)),
            dict(kind="outcrop", p=0.0020, dmin=2.5, zmin=12, box=MARSH_BOX),
            dict(kind="tree", p=0.035, dmin=7.0, box=MARSH_BOX, sc=(0.7, 1.2)),
            dict(kind="log", p=0.004, dmin=0.5, box=MARSH_BOX),
        ] + _BASE,
        wx=dict(mist=0.75, moss=1.25, moss_bias=0.22, insects=9, plume=0.2, cloud=0.55,
                light=dict(sun=(0.95, 0.93, 0.86), amb=(0.64, 0.74, 0.84), fog=(0.79, 0.86, 0.89))),
    ),

    # bosque de Glossopteris: troncos, sotobosque denso, hojarasca, luz filtrada
    "bosque": dict(
        bake_z=45.0, thin=(14.0, 150.0, 0.10),
        flora=[
            dict(kind="tree_hi", p=0.012, dmin=6.0, box=FOREST_BOX, sc=(0.8, 1.3)),
            dict(kind="cordaites", p=0.014, dmin=6.0, box=FOREST_BOX, sc=(0.9, 1.4)),
            dict(kind="ginkgo", p=0.008, dmin=6.0, box=FOREST_BOX, sc=(0.9, 1.3)),
            dict(kind="tree", p=0.042, dmin=6.0, box=FOREST_BOX, sc=(0.7, 1.3)),
            dict(kind="treefern", p=0.035, box=FOREST_BOX, sc=(0.7, 1.3)),
            dict(kind="conifer", p=0.010, box=FOREST_BOX, sc=(0.8, 1.2)),
            dict(kind="fern", p=0.13, box=FOREST_BOX, sc=(0.5, 1.3)),
            dict(kind="lycopsid", p=0.07, box=FOREST_BOX, sc=(0.6, 1.4)),
            dict(kind="shrub", p=0.05, box=FOREST_BOX, sc=(0.6, 1.2)),
            dict(kind="seedfern", p=0.07, box=FOREST_BOX, sc=(0.6, 1.3)),
            dict(kind="outcrop", p=0.0030, zmin=10, zmax=150, box=FOREST_BOX, sc=(0.6, 1.4)),
            dict(kind="rock_moss", p=0.010, zmax=100, box=FOREST_BOX, sc=(0.6, 1.6)),
            dict(kind="hongo", p=0.06, zmax=40, box=FOREST_BOX, sc=(0.8, 1.6)),
            dict(kind="fern", p=0.20, zmax=80, cmin=0.58, box=FOREST_BOX, sc=(0.8, 1.5)),
            dict(kind="mossmat", p=0.16, box=FOREST_BOX, sc=(0.6, 1.6)),
            dict(kind="stump", p=0.004, box=FOREST_BOX),
            dict(kind="log", p=0.006, box=FOREST_BOX),
            dict(kind="rock", p=0.004, box=FOREST_BOX),
        ] + _BASE,
        wx=dict(mist=0.35, leaves=7, litter=0.85, moss=1.2, plant_tint=(0.93, 0.97, 0.92), moss_bias=0.15, cloud_shadow=0.55, cloud=0.6, shadow=0.6, insects=6,
                plume=0.0, soil_a=(0.50, 0.45, 0.38), soil_b=(0.33, 0.29, 0.25),
                light=dict(sun=(0.86, 0.86, 0.76), amb=(0.52, 0.64, 0.66), fog=(0.70, 0.80, 0.80)),
                grade=dict(expo=1.06)),
    ),

    # ladera alta y seca: coníferas dispersas, roca, vista sobre la llanura
    "ladera": dict(
        flora=[
            dict(kind="conifer", p=0.040, box=SLOPE_BOX, sc=(0.7, 1.25)),
            dict(kind="shrub", p=0.022, box=SLOPE_BOX, sc=(0.5, 1.0)),
            dict(kind="outcrop", p=0.0045, zmin=10, box=SLOPE_BOX, sc=(0.8, 1.7)),
            dict(kind="rock_moss", p=0.012, box=SLOPE_BOX, sc=(0.6, 1.6)),
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
                grade=dict(sat=1.0)),
    ),

    # calle de ciudad al atardecer (solo para la rata)
    "calle": dict(
        dry=3.2,
        flora=[dict(kind="rock", p=0.003, zmax=40, sc=(0.07, 0.20))],
        wx=dict(mist=0.30, litter=0.0, cracks=0.0, moss=0.0, dust=0.15, leaves=6, plume=0.0, cloud=0.35,
                insects=0, wind=0.9, motes=1.4, soil_a=(0.88, 0.82, 0.88), soil_b=(0.76, 0.70, 0.80),
                zenith=(0.50, 0.56, 0.90), horizon=(1.0, 0.80, 0.88),
                light=dict(sun=(1.0, 0.88, 0.90), amb=(0.78, 0.76, 0.94), fog=(0.84, 0.74, 0.88)),
                grade=dict(expo=1.08, sat=1.08, tint=(0.99, 1.0, 1.03), contrast=0.28, lift=0.07)),
    ),

    # estepa patagónica: coirones, neneos, suelo ocre y luz rasante
    "estepa": dict(
        dry=2.8,
        flora=[
            dict(kind="coiron", p=0.45, dmin=0.1, zmax=50, sc=(0.8, 1.35)),
            dict(kind="coiron_verde", p=0.10, dmin=0.1, zmax=50, sc=(0.7, 1.2)),
            dict(kind="coiron", p=0.16, dmin=0.1, zmin=50, zmax=420, sc=(0.8, 1.5)),
            dict(kind="neneo", p=0.020, dmin=0.1, zmax=330, sc=(0.8, 1.4)),
            dict(kind="rock", p=0.0060, zmax=120, sc=(0.25, 0.9)),
        ],
        wx=dict(mist=0.26, litter=0.0, cracks=0.30, moss=0.0, dust=0.65, leaves=0, plume=0.0, cloud=0.26,
                insects=3, wind=1.7, motes=1.5, plant_tint=(0.99, 1.02, 1.02),
                soil_a=(1.0, 0.90, 0.86), soil_b=(0.92, 0.82, 0.82),
                zenith=(0.58, 0.74, 0.98), horizon=(0.97, 0.86, 0.93),
                light=dict(sun=(1.0, 0.95, 0.95), amb=(0.82, 0.84, 0.94), fog=(0.91, 0.90, 0.97)),
                grade=dict(expo=1.08, sat=1.10, tint=(0.99, 1.0, 1.03), contrast=0.28, lift=0.07)),
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
                grade=dict(sat=0.72, expo=1.05)),
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

# ----------------------------------------------------------------- nuevos biomas
SELVA_BOX = (-20, 100, 14, 210)
_SELVA = [
    dict(kind="tree_hi", p=0.010, dmin=4.0, box=SELVA_BOX, sc=(0.9, 1.4)),
    dict(kind="cordaites", p=0.016, dmin=3.0, box=SELVA_BOX, sc=(0.9, 1.4)),
    dict(kind="calamites", p=0.032, dmin=1.0, box=SELVA_BOX, sc=(0.8, 1.4)),
    dict(kind="treefern", p=0.080, dmin=0.5, box=SELVA_BOX, sc=(0.8, 1.4)),
    dict(kind="tree", p=0.040, dmin=5.0, box=SELVA_BOX, sc=(0.8, 1.3)),
    dict(kind="ginkgo", p=0.010, dmin=5.0, box=SELVA_BOX),
    dict(kind="horsetail", p=0.40, dmin=-0.7, dmax=6.5, box=SELVA_BOX, sc=(0.5, 1.4)),
    dict(kind="gigantopteris", p=0.20, dmin=0.3, box=SELVA_BOX, sc=(0.7, 1.4)),
    dict(kind="seedfern", p=0.14, dmin=0.2, box=SELVA_BOX, sc=(0.6, 1.3)),
    dict(kind="fern", p=0.20, dmin=0.2, box=SELVA_BOX, sc=(0.6, 1.4)),
    dict(kind="lycopsid", p=0.15, dmin=0.2, box=SELVA_BOX),
    dict(kind="mossmat", p=0.22, dmin=0.4, box=SELVA_BOX, sc=(0.6, 1.6)),
    dict(kind="hongo", p=0.05, zmax=40, box=SELVA_BOX, sc=(0.8, 1.6)),
    dict(kind="rock_moss", p=0.010, zmax=100, box=SELVA_BOX, sc=(0.6, 1.5)),
    dict(kind="outcrop", p=0.0025, zmin=10, zmax=140, box=SELVA_BOX),
    dict(kind="stump", p=0.006, box=SELVA_BOX), dict(kind="log", p=0.010, box=SELVA_BOX),
]
BIOMES["selva"] = dict(
    bake_z=30.0, thin=(6.0, 100.0, 0.10), near_clear=(9.0, 3.0),
    flora=_SELVA + _FAR + _BASE,
    wx=dict(mist=0.85, moss=1.35, moss_bias=0.30, insects=14, leaves=5, plume=0.0, cloud=0.62, shadow=0.55, cloud_shadow=0.5,
            soil_a=(0.40, 0.36, 0.30), soil_b=(0.26, 0.24, 0.20), moss_a=(0.15, 0.24, 0.12), moss_b=(0.30, 0.44, 0.20), litter=0.5,
            light=dict(sun=(0.90, 0.92, 0.80), amb=(0.52, 0.68, 0.64), fog=(0.66, 0.80, 0.76)), plant_tint=(1.0, 1.0, 0.97), grade=dict(sat=1.06, expo=1.22)),
)

_SN = {k: k + "_snow" for k in ("tree", "tree_hi", "conifer", "treefern", "fern", "shrub", "rock", "log", "calamites", "cordaites",
                                  "ginkgo", "stump", "lycopsid", "mossmat", "seedfern")}
_SN.update(horsetail="horsetail_frozen")
BIOMES["nevado"] = dict(
    flora=[dict(r, kind=_SN.get(r["kind"], r["kind"])) for r in _BASE] + [
        dict(kind="conifer_snow", p=0.020, dmin=3.0, zmin=15, zmax=250, sc=(0.8, 1.3)),
        dict(kind="tree_snow", p=0.020, dmin=4.0, zmin=15, zmax=250, sc=(0.8, 1.3)),
        dict(kind="conifer_snow", p=0.016, dmin=2.5, zmin=8, zmax=250, sc=(0.8, 1.3)),
        dict(kind="tree_snow", p=0.016, dmin=3.5, zmin=8, zmax=250, sc=(0.8, 1.3)),
        dict(kind="calamites_snow", p=0.006, dmin=1.5, zmin=10, zmax=120),
        dict(kind="shrub_snow", p=0.020, dmin=1.5, zmin=2, zmax=160, sc=(0.6, 1.3)),
        dict(kind="fern_snow", p=0.05, dmin=1.0, zmin=2, zmax=100, sc=(0.5, 1.2)),
        dict(kind="lycopsid_snow", p=0.05, dmin=1.0, zmin=2, zmax=60),
        dict(kind="mossmat_snow", p=0.03, dmin=1.0, zmax=60),
        dict(kind="outcrop_snow", p=0.0022, zmin=10, zmax=170, sc=(0.7, 1.5)),
        dict(kind="rock_moss_snow", p=0.006, zmax=100, sc=(0.6, 1.5)),
        dict(kind="rock_snow", p=0.004, zmax=120, sc=(0.6, 1.8)),
    ],
    wx=dict(snow=0.82, ice=0.55, pano_white=0.55, flurry=0.55, mist=0.45, moss=0.0, litter=0.0, plume=0.0, cloud=0.82, insects=0, leaves=0,
            cloud_shadow=0.3, shadow=0.6, wind=0.7, zenith=(0.58, 0.66, 0.78), horizon=(0.86, 0.89, 0.93), cold=1.0,
            soil_a=(0.62, 0.62, 0.62), soil_b=(0.46, 0.46, 0.48),
            light=dict(sun=(0.86, 0.90, 1.0), amb=(0.70, 0.78, 0.92), fog=(0.84, 0.88, 0.93)), grade=dict(sat=0.92, expo=1.04)),
)

BIOMES["desierto"] = dict(
    dry=6.5,
    flora=_FAR[:1] + [
        dict(kind="conifer", p=0.0020, dmin=-99, zmin=14, sc=(0.8, 1.3)),
        dict(kind="horsetail_dry", p=0.0015, dmin=-99, zmax=120, sc=(0.4, 0.9)),
        dict(kind="shrub_dry", p=0.0040, dmin=-99, zmax=200, sc=(0.5, 1.1)),
        dict(kind="log_stone", p=0.0040, dmin=-99, zmax=150, sc=(0.8, 1.5)),
        dict(kind="stump", p=0.0020, dmin=-99, zmax=150),
        dict(kind="outcrop_dry", p=0.0018, dmin=-99, zmin=10, zmax=220, sc=(0.7, 1.6)),
        dict(kind="rock", p=0.0030, dmin=-99, zmax=220, sc=(0.5, 1.7)),
        dict(kind="shrub_dry", p=0.0035, dmin=-99, zmin=3, zmax=60, sc=(0.4, 0.9)),
    ],
    wx=dict(mist=0.0, moss=0.0, litter=0.0, cracks=0.45, dunes=1.0, dust=1.0, puff=0.55, plume=0.0, cloud=0.10, insects=0, leaves=0,
            cloud_shadow=0.2, wind=1.6, soil_a=(0.92, 0.84, 0.68), soil_b=(0.74, 0.66, 0.54), zenith=(0.48, 0.64, 0.86), horizon=(0.90, 0.88, 0.84),
            light=dict(sun=(1.0, 0.96, 0.88), amb=(0.66, 0.72, 0.82), fog=(0.88, 0.86, 0.82)), grade=dict(sat=1.15, tint=(1.07, 1.0, 0.90), expo=1.06)),
)

BIOMES["artico"] = dict(
    flora=[
        dict(kind="rock_snow", p=0.0035, dmin=-99, zmax=300, sc=(0.7, 3.2)),
        dict(kind="rock", p=0.0012, dmin=-99, zmax=300, sc=(0.6, 2.4)),
        dict(kind="mossmat_snow", p=0.003, dmin=-99, zmax=60),
    ],
    wx=dict(snow=1.0, ice=1.0, pano_white=0.92, flurry=0.7, mist=0.55, moss=0.0, litter=0.0, plume=0.0, cloud=0.55, insects=0, leaves=0,
            cloud_shadow=0.15, shadow=0.7, wind=1.0, cold=1.0, zenith=(0.60, 0.70, 0.84), horizon=(0.88, 0.91, 0.95),
            soil_a=(0.58, 0.60, 0.62), soil_b=(0.42, 0.44, 0.48), snow_col=(0.92, 0.95, 1.0),
            light=dict(sun=(0.90, 0.94, 1.0), amb=(0.72, 0.80, 0.94), fog=(0.86, 0.90, 0.95)), grade=dict(sat=0.86, expo=1.06)),
)
