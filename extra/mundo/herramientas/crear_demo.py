#!/usr/bin/env python3
"""Genera ejemplos/demo_intro.json: intro silueta-dentro-de-silueta (0-4 s) + callejon con
anfitrion, NPC y entrada de la mascota pistola 10mm (4-14 s). Es solo un JSON liviano."""
import json, os, random
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
r = random.Random(5)


def it(asset, x, y, esc=1, **k):
    return dict(asset=asset, x=x, y=y, esc=esc, **k)


# ---------- INTRO 0-4s: silueta con ciudad adentro
intro_fondo = {"nombre": "intro_fondo", "paralaje": 0, "de": 0, "hasta": 4.2, "items": [
    {"texto": " ", "x": 0, "y": 0}]}
intro_gris = {"nombre": "intro_gris", "paralaje": 0.3, "de": 0, "hasta": 4.2, "items": [
    it("silueta_hombre_hombros", 960, 540, 1.75, silueta="#cdcdcd", id="sil_fondo")]}
ciudad = [
    it("skyline_lejano", 960, 640, 1.8, id="sk1", sat=.0),
    it("edificio_oficinas", 560, 800, .9, sat=0), it("edificio_ladrillo_a", 1300, 860, 1.0, sat=0),
    it("puente_suspension", 1000, 900, 1.5, sat=0), it("poste_luz", 640, 930, 1.0, sat=0),
    it("humo_nube", 1150, 700, 1.4, sat=0), it("nube_cielo", 820, 300, 1.6, sat=0),
    it("pajaro_vuelo", 900, 420, 1.2, id="pj", sat=0),
]
intro_ciudad = {"nombre": "intro_ciudad_en_silueta", "paralaje": 0.6, "de": 0, "hasta": 4.2,
                "mascara": {"asset": "silueta_hombre_hombros", "x": 960, "y": 540, "esc": 1.75}, "items": ciudad}
intro_hombre = {"nombre": "intro_hombre_pie", "paralaje": 0.9, "de": 0, "hasta": 4.2, "items": [
    it("silueta_hombre_entero", 1500, 960, 2.2, silueta="#0c0c0c", id="sil_pie"),
    {"texto": "EXTRA", "x": 960, "y": 560, "tam": 120, "color": "#f2f2f2", "id": "titulo", "espaciado": 10}]}

# ---------- CALLEJON 4-14s
cielo = {"nombre": "cielo", "paralaje": 0.05, "de": 3.9, "items": [
    it("nube_cielo", 400, 220, 1.4, id="nb1", op=.8), it("nube_cielo", 1300, 160, 1.8, id="nb2", op=.7),
    it("skyline_lejano", 960, 640, 1.8)]}
lejos = {"nombre": "edificios_lejos", "paralaje": 0.25, "de": 3.9, "items": [
    it("edificio_oficinas", 220, 700, 1.0, op=.9), it("edificio_ladrillo_b", 600, 720, 1.1), it("edificio_ladrillo_a", 1450, 700, 1.2),
    it("edificio_oficinas", 1800, 700, 1.0), it("puente_suspension", 1000, 690, 1.0, op=.85)]}
medio_atras = {"nombre": "pared_callejon", "paralaje": 0.55, "de": 3.9, "items": [
    it("pared_ladrillo", 340, 800, 1.5), it("pared_ladrillo", 1100, 800, 1.5), it("pared_ladrillo", 1860, 800, 1.5),
    it("edificio_escalera_incendio", 1560, 820, 1.3), it("ventana_barrotes", 180, 600, 1.1, id="vent"),
    it("cartel_neon", 880, 420, 1.0, texto_editable="EXTRA", id="neon", afin=True),
    it("poste_luz", 760, 830, 1.3), it("cables_electricos", 960, 170, 3.3, id="cables")]}
suelo = {"nombre": "suelo", "paralaje": 0.9, "de": 3.9, "items": [
    it("suelo_asfalto", 960, 1080, 1.7, id="asf", sat=.35), it("suelo_asfalto", 960, 940, 1.7, sat=.35, op=.8)]}
detalles = []
for i in range(10):
    detalles.append(it(r.choice(["grieta_suelo", "piedritas", "hojas_suelo", "papel_arrugado", "lata_aplastada", "vaso_tirado", "charco", "boca_tormenta"]),
                       r.randint(60, 1860), r.randint(905, 1040), r.uniform(1.0, 2.0), flip=r.random() < .5))
medio = {"nombre": "accion", "paralaje": 1, "de": 3.9, "items": [
    it("contenedor_basura", 1500, 940, 1.6, id="cont"), it("caja_madera_g", 1220, 900, 1.2, id="cajaG"), it("caja_madera_p", 1330, 930, 1.1),
    it("bolsa_basura", 1000, 950, 1.5), it("caja_carton", 380, 960, 1.4), it("hidrante", 260, 900, 1.3), it("alfombra_enrollada", 760, 1000, 1.2, id="alf"),
    it("arbusto", 120, 1010, 1.3), it("pasto_mata", 520, 1010, 2.0), it("botella_vidrio", 880, 1020, 1.6),
    it("humo_nube", 560, 980, 1.0, id="vapor", op=.55, sat=0),
    # personajes
    it("npc_campera_marron", 1130, 1015, 1.05, id="npc", flip=True, afin=False),
    it("anfitrion_extra", 700, 1030, 1.15, id="host"),
] + detalles}
mascota = {"nombre": "mascota", "paralaje": 1, "de": 3.9, "items": [
    it("mascota_pistola_10mm", 960, 960, 1.0, id="gun")]}
primer = {"nombre": "primer_plano", "paralaje": 1.35, "de": 3.9, "items": [
    it("arbusto", 90, 1110, 2.6, id="fg1", sat=.5, op=.95), it("pasto_mata", 1780, 1120, 4.5, id="fg2", op=.95),
    it("hojas_suelo", 600, 1090, 3, op=.9), it("poste_luz", 1880, 1120, 2.4, id="fg3")]}
polvo = {"nombre": "polvo", "paralaje": 1.1, "de": 3.9, "op": .9, "items": [
    it("polvo_particulas", 600, 700, 3, id="pv1", ancla="base"), it("polvo_particulas", 1400, 760, 3, id="pv2"),
    it("rayos_luz", 1500, 560, 2.2, id="luz", op=.45)]}

anim = [
    # intro
    dict(item="sil_pie", prop="y", from_=40, to=0, t0=0, t1=3.9, ease="out"),
    dict(item="sk1", prop="x", from_=-80, to=80, t0=0, t1=4.2, ease="lineal"),
    dict(item="pj", prop="x", from_=-420, to=620, t0=0, t1=4, ease="lineal"),
    dict(item="titulo", prop="op", from_=0, to=1, t0=1.2, t1=2.0, ease="out"),
    # nubes y vapor
    dict(item="nb1", prop="x", from_=-60, to=80, t0=3.9, t1=14, ease="lineal"),
    dict(item="nb2", prop="x", from_=80, to=-60, t0=3.9, t1=14, ease="lineal"),
    dict(item="vapor", prop="y", from_=0, to=-30, t0=3.9, t1=14, ease="lineal", loop=True, periodo=3, pingpong=True),
    dict(item="cables", prop="rot", from_=-.4, to=.4, t0=0, t1=14, ease="inout", loop=True, periodo=5, pingpong=True),
    dict(item="pv1", prop="y", from_=0, to=-60, t0=3.9, t1=14, ease="lineal", loop=True, periodo=7),
    dict(item="pv2", prop="y", from_=0, to=-40, t0=3.9, t1=14, ease="lineal", loop=True, periodo=9),
    dict(item="luz", prop="op", from_=.35, to=.6, t0=3.9, t1=14, ease="inout", loop=True, periodo=4, pingpong=True),
    # anfitrion: respira y gesticula
    dict(item="host", prop="esc", from_=1, to=1.012, t0=4, t1=14, ease="inout", loop=True, periodo=2.2, pingpong=True),
    dict(item="host", parte="brazo_d", prop="rot", pivote=[184, 172], from_=0, to=-28, t0=6.0, t1=6.5, ease="out"),
    dict(item="host", parte="brazo_d", prop="rot", pivote=[184, 172], from_=0, to=24, t0=6.5, t1=7.3, ease="inout"),
    dict(item="host", parte="cabeza", prop="rot", pivote=[124, 110], from_=0, to=-6, t0=8.4, t1=9.0, ease="out"),
    dict(item="npc", prop="esc", from_=1, to=1.01, t0=4, t1=14, ease="inout", loop=True, periodo=2.6, pingpong=True),
    # mascota: entra con rebote a los 9s, mueve martillo y ojos
    dict(item="gun", prop="esc", from_=0, to=.62, t0=9.0, t1=9.9, ease="elastico", antes=True),
    dict(item="gun", prop="y", from_=-380, to=0, t0=9.0, t1=9.6, ease="rebote", antes=True),
    dict(item="gun", parte="martillo", prop="rot", pivote=[44, 50], from_=0, to=-40, t0=10.4, t1=10.6, ease="out"),
    dict(item="gun", parte="martillo", prop="rot", pivote=[44, 50], from_=-40, to=0, t0=10.6, t1=10.7, ease="in"),
    dict(item="gun", parte="brazo_i", prop="rot", pivote=[96, 150], from_=0, to=-25, t0=10.9, t1=11.6, ease="inout", loop=True, periodo=1.2, pingpong=True),
    dict(item="gun", parte="ojos", prop="dx", from_=-3, to=5, t0=9.9, t1=13, ease="inout", loop=True, periodo=1.8, pingpong=True),
    dict(item="gun", parte="cuerpo", prop="rot", pivote=[200, 280], from_=-2, to=2, t0=9.9, t1=14, ease="inout", loop=True, periodo=.9, pingpong=True),
    dict(item="neon", prop="op", from_=.75, to=1, t0=4, t1=14, ease="lineal", loop=True, periodo=.35, pingpong=True),
]
for a in anim:
    a["from"] = a.pop("from_")

escena = {
    "nombre": "Demo de intro + callejon + mascota", "tema": "gta4", "duracion": 14, "fps": 30,
    "fondo_sat": 0.2, "vineta": .55, "grano": .09, "bruma": .2, "barras": True,
    "capas": [intro_fondo, intro_gris, intro_ciudad, intro_hombre, cielo, lejos, medio_atras, suelo, medio, mascota, primer, polvo],
    "anim": anim,
    "camara": [
        {"t": 0, "x": 960, "y": 540, "z": 1.0},
        {"t": 3.6, "x": 960, "y": 600, "z": 1.35, "ease": "in"},
        {"t": 4.0, "x": 700, "y": 560, "z": 1.12},
        {"t": 8.5, "x": 900, "y": 540, "z": 1.0, "ease": "inout"},
        {"t": 11.5, "x": 1000, "y": 560, "z": 1.12, "ease": "inout"},
        {"t": 14, "x": 960, "y": 540, "z": 1.0, "ease": "inout"}],
    "temblor": [{"t0": 9.0, "t1": 9.5, "fuerza": 14}],
    "destellos": [{"t": 3.8, "dur": 0.35}, {"t": 9.0, "dur": .2}],
    "fundidos": [{"tipo": "entrada", "t": 0, "dur": 0.6}, {"tipo": "salida", "t": 13.5, "dur": 0.5}],
}
os.makedirs(os.path.join(RAIZ, "ejemplos"), exist_ok=True)
with open(os.path.join(RAIZ, "ejemplos", "demo_intro.json"), "w", encoding="utf-8") as f:
    json.dump(escena, f, ensure_ascii=False, indent=1)
print("demo escrita")
