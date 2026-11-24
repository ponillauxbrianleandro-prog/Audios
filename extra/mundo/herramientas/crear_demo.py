#!/usr/bin/env python3
"""Genera ejemplos/demo_intro.json (v2 cinematografica): intro silueta-en-silueta (0-4 s) + callejon con
anfitrion, NPC, rack focus, camara en mano y entrada de la mascota pistola 10mm (4-18 s). JSON liviano."""
import json, os, random
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
r = random.Random(5)
D = 18


def it(asset, x, y, esc=1, **k):
    return dict(asset=asset, x=x, y=y, esc=esc, **k)


# ---------- INTRO 0-4s
intro = [
    {"nombre": "intro_fondo", "paralaje": 0, "de": 0, "hasta": 4.2, "items": [it("cielo_nublado", 960, 800, 1.7)]},
    {"nombre": "intro_gris", "paralaje": 0.3, "de": 0, "hasta": 4.2, "items": [it("silueta_hombre_hombros", 960, 540, 1.75, silueta="#d2d6d4", id="sil_fondo", sombra=False)]},
    {"nombre": "intro_ciudad_en_silueta", "paralaje": 0.6, "de": 0, "hasta": 4.2,
     "mascara": {"asset": "silueta_hombre_hombros", "x": 960, "y": 540, "esc": 1.75}, "items": [
         it("cielo_nublado", 960, 800, 1.7, sat=0), it("skyline_lejano", 960, 640, 1.8, id="sk1", sat=0),
         it("edificio_oficinas", 560, 800, .9, sat=0), it("edificio_ladrillo_a", 1300, 860, 1.0, sat=0),
         it("puente_suspension", 1000, 900, 1.5, sat=0), it("poste_luz", 640, 930, 1.0, sat=0),
         it("humo_nube", 1150, 700, 1.4, sat=0, sombra=False), it("pajaro_vuelo", 900, 420, 1.2, id="pj", sat=0)]},
    {"nombre": "intro_hombre_pie", "paralaje": 0.9, "de": 0, "hasta": 4.2, "items": [
        it("silueta_hombre_entero", 1500, 960, 2.2, silueta="#0c0c0c", id="sil_pie", sombra=False),
        {"texto": "EXTRA", "x": 960, "y": 560, "tam": 120, "color": "#f2f2f2", "id": "titulo", "espaciado": 10}]}]

# ---------- CALLEJON
A = 3.9
cielo = {"nombre": "cielo", "paralaje": 0.04, "de": A, "items": [it("cielo_nublado", 960, 760, 1.7, sombra=False), it("nube_cielo", 400, 220, 1.4, id="nb1", op=.5), it("nube_cielo", 1300, 160, 1.8, id="nb2", op=.4)]}
lejos = {"nombre": "edificios_lejos", "paralaje": 0.22, "de": A, "items": [
    it("skyline_nocturno", 960, 760, 1.7, op=.8), it("edificio_oficinas", 220, 720, 1.0), it("edificio_ladrillo_b", 640, 740, 1.1),
    it("edificio_ladrillo_a", 1450, 720, 1.2), it("edificio_oficinas", 1800, 720, 1.0), it("puente_suspension", 1000, 700, 1.0, op=.85)]}
medio_atras = {"nombre": "pared_callejon", "paralaje": 0.55, "de": A, "items": [
    it("pared_ladrillo", 340, 800, 1.5), it("pared_ladrillo", 1100, 800, 1.5), it("pared_ladrillo", 1860, 800, 1.5),
    it("edificio_escalera_incendio", 1580, 830, 1.3), it("puerta_metalica", 460, 820, 1.0), it("ventana_barrotes", 160, 600, 1.1),
    it("graffiti_pared", 300, 560, 1.0, op=.8, sombra=False), it("cartel_neon", 900, 440, 1.0, texto_editable="EXTRA", id="neon", afin=True),
    it("luz_glow", 900, 440, 2.2, id="glow_neon", mezcla="screen", op=.35, hue=300, sat=1, sombra=False),
    it("poste_luz", 780, 840, 1.35), it("luz_glow", 810, 600, 3.0, id="glow_poste", mezcla="screen", op=.5, sat=1, sombra=False), it("cables_electricos", 960, 170, 3.3, id="cables"),
    it("andamio", 60, 830, 1.3, op=.9)]}
suelo = {"nombre": "suelo", "paralaje": 0.9, "de": A, "items": [it("suelo_asfalto", 960, 1090, 1.7, sat=.5), it("suelo_asfalto", 960, 950, 1.7, sat=.5, op=.85), it("suelo_vereda", 960, 860, 1.7, sat=.4)]}
det = []
for i in range(14):
    det.append(it(r.choice(["grieta_suelo", "piedritas", "hojas_suelo", "papel_arrugado", "lata_aplastada", "vaso_tirado", "charco", "boca_tormenta", "botella_vidrio", "neumatico"]),
                  r.randint(60, 1860), r.randint(905, 1050), r.uniform(1.0, 2.0), flip=r.random() < .5))
medio = {"nombre": "accion", "paralaje": 1, "de": A, "items": [
    it("contenedor_basura", 1560, 940, 1.6), it("caja_madera_g", 1300, 905, 1.2), it("caja_madera_p", 1410, 935, 1.1),
    it("tacho_metal", 1750, 950, 1.5), it("bolsa_basura", 1010, 955, 1.5), it("caja_carton", 380, 965, 1.4), it("hidrante", 250, 905, 1.3), it("alfombra_enrollada", 800, 1005, 1.2),
    it("banco_parque", 120, 930, 1.0), it("pasto_mata", 520, 1012, 2.0), it("humo_nube", 560, 985, 1.0, id="vapor", op=.5, sat=0, sombra=False),
    it("npc_campera_marron", 1160, 1040, 1.0, id="npc", flip=True),
    it("anfitrion_extra", 640, 1045, 1.04, id="host")] + det}
mascota = {"nombre": "mascota", "paralaje": 1, "de": A, "items": [it("mascota_pistola_10mm", 940, 1030, 1.0, id="gun")]}
primer = {"nombre": "primer_plano", "paralaje": 1.35, "de": A, "items": [
    it("arbusto", 90, 1120, 2.6, id="fg1", op=.95), it("pasto_mata", 1780, 1130, 4.5, id="fg2", op=.95), it("hojas_suelo", 600, 1095, 3, op=.9), it("poste_luz", 1890, 1130, 2.4, id="fg3"),
    it("baranda_acero", 960, 1150, 2.2, op=.9)]}
polvo = {"nombre": "polvo", "paralaje": 1.1, "de": A, "items": [
    it("polvo_particulas", 600, 700, 3, id="pv1", sombra=False), it("polvo_particulas", 1400, 760, 3, id="pv2", sombra=False),
    it("rayos_luz", 1500, 560, 2.2, id="luz", op=.4, sombra=False, mezcla="screen")]}

anim = [
    dict(item="sil_pie", prop="y", **{"from": 40}, to=0, t0=0, t1=3.9, ease="out"),
    dict(item="sk1", prop="x", **{"from": -80}, to=80, t0=0, t1=4.2, ease="lineal"),
    dict(item="pj", prop="x", **{"from": -420}, to=620, t0=0, t1=4, ease="lineal"),
    dict(item="titulo", prop="op", **{"from": 0}, to=1, t0=1.2, t1=2.0, ease="out"),
    dict(item="nb1", prop="x", **{"from": -60}, to=80, t0=A, t1=D, ease="lineal"),
    dict(item="nb2", prop="x", **{"from": 80}, to=-60, t0=A, t1=D, ease="lineal"),
    dict(item="vapor", prop="y", **{"from": 0}, to=-30, t0=A, t1=D, ease="lineal", loop=True, periodo=3, pingpong=True),
    dict(item="cables", prop="rot", **{"from": -.4}, to=.4, t0=0, t1=D, ease="inout", loop=True, periodo=5, pingpong=True),
    dict(item="pv1", prop="y", **{"from": 0}, to=-60, t0=A, t1=D, ease="lineal", loop=True, periodo=7),
    dict(item="pv2", prop="y", **{"from": 0}, to=-40, t0=A, t1=D, ease="lineal", loop=True, periodo=9),
    dict(item="luz", prop="op", **{"from": .3}, to=.55, t0=A, t1=D, ease="inout", loop=True, periodo=4, pingpong=True),
    dict(item="glow_poste", prop="op", ruido=True, amp=.08, freq=1.3, semilla=2, sum=True, t0=0, t1=D, **{"from": 0}, to=0),
    dict(item="neon", prop="op", **{"from": .75}, to=1, t0=A, t1=D, ease="lineal", loop=True, periodo=.35, pingpong=True),
]
# personajes: respiracion, parpadeo, cabeza viva, gesto con codo
for who, ph in (("host", 0), ("npc", 1.3)):
    anim += [dict(item=who, prop="esc", **{"from": 1}, to=1.012, t0=A, t1=D, ease="inout", loop=True, periodo=2.4 + ph, pingpong=True),
             dict(item=who, parte="ojos", prop="escy", pivote=[130, 70], **{"from": 1}, to=.08, t0=A + ph, t1=D, ease="parpadeo", loop=True, periodo=3.6 + ph),
             dict(item=who, parte="cabeza", prop="rot", pivote=[130, 112], ruido=True, amp=1.6, freq=.22, semilla=ph, t0=0, t1=D, **{"from": 0}, to=0),
             dict(item=who, parte="brazo_i", prop="rot", pivote=[62, 152], ruido=True, amp=1.0, freq=.3, semilla=ph + 1, t0=0, t1=D, **{"from": 0}, to=0),
             dict(item=who, parte="torso", prop="dy", ruido=True, amp=1.2, freq=.4, semilla=ph, t0=0, t1=D, **{"from": 0}, to=0)]
anim += [
    dict(item="host", parte="brazo_d", prop="rot", pivote=[205, 152], **{"from": 0}, to=-22, t0=6.0, t1=6.5, ease="out"),
    dict(item="host", parte="antebrazo_d", prop="rot", pivote=[220, 262], **{"from": 0}, to=70, t0=6.0, t1=6.6, ease="out"),
    dict(item="host", parte="brazo_d", prop="rot", pivote=[205, 152], **{"from": -22}, to=0, t0=7.6, t1=8.4, ease="inout"),
    dict(item="host", parte="antebrazo_d", prop="rot", pivote=[220, 262], **{"from": 70}, to=0, t0=7.6, t1=8.4, ease="inout"),
    dict(item="host", parte="cabeza", prop="rot", pivote=[130, 112], **{"from": 0}, to=-5, t0=8.4, t1=9.0, ease="out", sum=True),
    dict(item="host", parte="boca", prop="escy", pivote=[130, 108], **{"from": 1}, to=.55, t0=A + .5, t1=D, ease="inout", loop=True, periodo=.34, pingpong=True),
    # mascota: entrada con rebote + martillo + ojos + boca
    dict(item="gun", prop="esc", **{"from": 0}, to=.62, t0=9.0, t1=9.9, ease="elastico", antes=True),
    dict(item="gun", prop="y", **{"from": -380}, to=0, t0=9.0, t1=9.6, ease="rebote", antes=True),
    dict(item="gun", parte="martillo", prop="rot", pivote=[44, 50], **{"from": 0}, to=-40, t0=10.4, t1=10.6, ease="out"),
    dict(item="gun", parte="martillo", prop="rot", pivote=[44, 50], **{"from": -40}, to=0, t0=10.6, t1=10.7, ease="in"),
    dict(item="gun", parte="brazo_i", prop="rot", pivote=[96, 150], **{"from": 0}, to=-25, t0=10.9, t1=11.6, ease="inout", loop=True, periodo=1.2, pingpong=True),
    dict(item="gun", parte="ojos", prop="dx", **{"from": -3}, to=5, t0=9.9, t1=14, ease="inout", loop=True, periodo=1.8, pingpong=True),
    dict(item="gun", parte="ojos", prop="escy", pivote=[176, 80], **{"from": 1}, to=.08, t0=10.2, t1=D, ease="parpadeo", loop=True, periodo=2.9),
    dict(item="gun", parte="boca", prop="escy", pivote=[176, 108], **{"from": 1}, to=.4, t0=11, t1=D, ease="inout", loop=True, periodo=.3, pingpong=True),
    dict(item="gun", parte="cuerpo", prop="rot", pivote=[200, 280], **{"from": -2}, to=2, t0=9.9, t1=D, ease="inout", loop=True, periodo=.9, pingpong=True),
]
escena = {
    "nombre": "Demo cinematografica v2", "tema": "gta4", "duracion": D, "fps": 30, "fondo_sat": 0.3, "vineta": .6, "grano": .1, "bruma": .22,
    "barras": True, "mano": 1.1, "dof": 7, "luz": .6,
    "foco": [{"t": 0, "v": 1}, {"t": 5.2, "v": 1}, {"t": 6.0, "v": .55}, {"t": 8.0, "v": .55}, {"t": 8.8, "v": 1}],
    "capas": intro + [cielo, lejos, medio_atras, suelo, medio, mascota, primer, polvo], "anim": anim,
    "camara": [
        {"t": 0, "x": 960, "y": 540, "z": 1.0}, {"t": 3.6, "x": 960, "y": 600, "z": 1.35, "ease": "in"}, {"t": 4.0, "x": 700, "y": 560, "z": 1.12},
        {"t": 8.5, "x": 900, "y": 540, "z": 1.0, "ease": "inout"}, {"t": 12.5, "x": 1000, "y": 560, "z": 1.14, "ease": "inout"}, {"t": D, "x": 960, "y": 540, "z": 1.0, "ease": "inout"}],
    "temblor": [{"t0": 9.0, "t1": 9.5, "fuerza": 14}],
    "destellos": [{"t": 3.8, "dur": 0.35}, {"t": 9.0, "dur": .2}],
    "fundidos": [{"tipo": "entrada", "t": 0, "dur": 0.6}, {"tipo": "salida", "t": D - .5, "dur": 0.5}]}
os.makedirs(os.path.join(RAIZ, "ejemplos"), exist_ok=True)
json.dump(escena, open(os.path.join(RAIZ, "ejemplos", "demo_intro.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("demo escrita")
