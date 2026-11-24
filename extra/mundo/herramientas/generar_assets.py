#!/usr/bin/env python3
"""Genera la libreria de assets SVG 2D del mundo de Extra + catalogo.json.

Estilo: ilustracion pictorica 2D, luz desde arriba-izquierda, sombra a la derecha,
gradientes suaves, textura sutil. Nada de 3D. Todo original (inspirado, no copiado).

Uso:  python3 generar_assets.py        (regenera assets/ y catalogo.json)
Para sumar assets nuevos: agregar una funcion con @asset(...) abajo y volver a correr.
"""
import json, os, random, math

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "assets")
REGISTRO = []

NOISE = ('<filter id="tx" x="0" y="0" width="100%" height="100%">'
         '<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="{s}"/>'
         '<feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .22 0"/>'
         '<feComposite in2="SourceGraphic" operator="in"/></filter>')


def asset(id, cat, w, h, desc, tags="", rol="fondo", ancla="base"):
    """Decorador: registra un asset. La funcion devuelve (defs, cuerpo)."""
    def deco(fn):
        REGISTRO.append(dict(id=id, cat=cat, w=w, h=h, desc=desc, rol=rol, ancla=ancla,
                             tags=[t for t in tags.split(",") if t], fn=fn))
        return fn
    return deco


def lin(i, c1, c2, x1=0, y1=0, x2=1, y2=1):
    return (f'<linearGradient id="{i}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">'
            f'<stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>')


def sombra_suelo(cx, y, rx, ry=None, op=.35):
    ry = ry or max(3, rx * .18)
    return f'<ellipse cx="{cx}" cy="{y}" rx="{rx}" ry="{ry}" fill="#000" opacity="{op}"/>'


def tex(w, h, s=1, op=1):
    return f'<rect width="{w}" height="{h}" fill="#000" filter="url(#tx)" opacity="{op}"/>'


# ============================================================ EXTERIOR
def edificio(w, h, base, ventanas, escalera=False, seed=1, nombre="ed"):
    r = random.Random(seed)
    d = lin("g", base[0], base[1], 0, 0, 1, 0) + lin("s", "#00000000", "#0008", 0, 0, 0, 1) + NOISE.format(s=seed)
    b = f'<rect width="{w}" height="{h}" fill="url(#g)"/>'
    # hiladas de ladrillo
    for y in range(0, h, 14):
        b += f'<line x1="0" y1="{y}" x2="{w}" y2="{y}" stroke="#0003" stroke-width="1"/>'
    for y in range(0, h, 28):
        for x in range(r.randint(0, 20), w, 40):
            b += f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+14}" stroke="#0002"/>'
    cols, filas = ventanas
    ww, wh = w / (cols * 2.0), 50
    for j in range(filas):
        for i in range(cols):
            x = (i * 2 + .5) * ww; y = 60 + j * 110
            lit = r.random() < .25
            b += (f'<rect x="{x-4}" y="{y-4}" width="{ww+8}" height="{wh+8}" fill="#1b2127" opacity=".5"/>'
                  f'<rect x="{x}" y="{y}" width="{ww}" height="{wh}" fill="{"#e9d9a8" if lit else "#2a3a42"}"/>'
                  f'<rect x="{x}" y="{y}" width="{ww}" height="{wh*.45}" fill="#fff" opacity=".12"/>'
                  f'<rect x="{x-6}" y="{y+wh+4}" width="{ww+12}" height="6" fill="#8f8072"/>')
    if escalera:
        for j in range(filas):
            y = 60 + j * 110 + 62
            b += (f'<rect x="{w*.1}" y="{y}" width="{w*.8}" height="5" fill="#161b1e"/>'
                  f'<path d="M{w*.1} {y}V{y-26}M{w*.9} {y}V{y-26}M{w*.1} {y-26}H{w*.9}" stroke="#161b1e" stroke-width="3" fill="none"/>')
        b += f'<path d="M{w*.55} 80 L{w*.8} {60+(filas-1)*110+62} " stroke="#161b1e" stroke-width="4"/>'
    b += f'<rect width="{w}" height="{h}" fill="url(#s)"/>' + tex(w, h)
    b += f'<rect x="0" y="0" width="{w}" height="10" fill="#0004"/>'
    return d, b


@asset("edificio_ladrillo_a", "exterior", 360, 640, "Edificio de ladrillo con ventanas", "edificio,ladrillo,ciudad")
def _():
    return edificio(360, 640, ("#8a6f5d", "#5a463c"), (3, 5), seed=1)


@asset("edificio_ladrillo_b", "exterior", 300, 520, "Edificio bajo de ladrillo rojizo", "edificio,ladrillo")
def _():
    return edificio(300, 520, ("#8c5a4a", "#4f3a33"), (2, 4), seed=2)


@asset("edificio_escalera_incendio", "exterior", 340, 640, "Edificio con escaleras de incendio", "edificio,escalera,ciudad")
def _():
    return edificio(340, 640, ("#9a8878", "#5d5249"), (3, 5), True, seed=3)


@asset("edificio_oficinas", "exterior", 280, 720, "Torre de oficinas azulada", "edificio,torre,vidrio")
def _():
    d = lin("g", "#6f8a96", "#2c3d46", 0, 0, 1, 1) + lin("r", "#fff4", "#fff0", 0, 0, 1, 1) + NOISE.format(s=4)
    b = '<rect width="280" height="720" fill="url(#g)"/>'
    for y in range(20, 700, 26):
        for x in range(14, 270, 22):
            b += f'<rect x="{x}" y="{y}" width="16" height="16" fill="{"#d7e6e8" if (x*y)%7==0 else "#1d2c34"}" opacity=".85"/>'
    b += '<rect width="280" height="720" fill="url(#r)"/><rect x="200" width="80" height="720" fill="#0003"/>' + tex(280, 720)
    return d, b


@asset("skyline_lejano", "exterior", 1200, 260, "Skyline lejano brumoso (capa de horizonte)", "skyline,fondo,horizonte")
def _():
    r = random.Random(7)
    d = lin("g", "#8fa3a3", "#6a7e79", 0, 0, 0, 1)
    b = ""
    x = 0
    while x < 1200:
        w = r.randint(50, 110); h = r.randint(70, 240)
        b += f'<rect x="{x}" y="{260-h}" width="{w}" height="{h}" fill="url(#g)" opacity="{r.uniform(.5,.95):.2f}"/>'
        if r.random() < .3:
            b += f'<path d="M{x+w/2-8} {260-h}l8 -{r.randint(20,50)} 8 {r.randint(20,50)}z" fill="#6a7e79"/>'
        x += w - 6
    return d, b


@asset("skyline_nocturno", "exterior", 1200, 280, "Skyline nocturno con ventanas encendidas", "skyline,noche,luces")
def _():
    r = random.Random(8)
    d = ""
    b = ""
    x = 0
    while x < 1200:
        w = r.randint(50, 100); h = r.randint(80, 260)
        b += f'<rect x="{x}" y="{280-h}" width="{w}" height="{h}" fill="#1a2930"/>'
        for _y in range(280 - h + 10, 270, 14):
            for _x in range(x + 6, x + w - 8, 12):
                if r.random() < .22:
                    b += f'<rect x="{_x}" y="{_y}" width="6" height="8" fill="#f2d98a" opacity=".85"/>'
        x += w - 4
    return d, b


@asset("puente_suspension", "exterior", 900, 420, "Puente colgante de acero tipo Manhattan", "puente,acero,ciudad")
def _():
    d = lin("g", "#9aa6a4", "#4a5658", 0, 0, 1, 1)
    b = ""
    for px in (120, 740):
        b += (f'<path d="M{px} 420V30H{px+40}V420" fill="none" stroke="url(#g)" stroke-width="12"/>'
              f'<path d="M{px} 60H{px+40}M{px} 140H{px+40}M{px} 220H{px+40}" stroke="#4a5658" stroke-width="8"/>'
              f'<path d="M{px} 60L{px+40} 140L{px} 220L{px+40} 300" stroke="#4a5658" stroke-width="4" fill="none"/>')
    b += '<path d="M0 360Q450 120 900 360" stroke="#2f3a3c" stroke-width="7" fill="none"/>'
    for x in range(20, 900, 30):
        yy = 360 - math.sin(x / 900 * math.pi) * 220 * 1.0 + 0
        b += f'<line x1="{x}" y1="{yy+0:.0f}" x2="{x}" y2="360" stroke="#2f3a3c" stroke-width="2"/>'
    b += '<rect y="355" width="900" height="30" fill="url(#g)"/><rect y="385" width="900" height="8" fill="#0006"/>'
    for x in range(0, 900, 50):
        b += f'<path d="M{x} 385L{x+25} 355L{x+50} 385" stroke="#303a3c" stroke-width="3" fill="none"/>'
    return d, b


@asset("poste_luz", "exterior", 80, 340, "Poste de alumbrado urbano", "poste,luz,calle")
def _():
    d = lin("g", "#4a5658", "#1f2628", 0, 0, 1, 0)
    b = (sombra_suelo(40, 336, 28) + '<rect x="35" y="30" width="9" height="305" fill="url(#g)"/>'
         '<path d="M40 40Q40 10 70 14" stroke="#2c3436" stroke-width="7" fill="none"/>'
         '<rect x="58" y="12" width="22" height="9" rx="3" fill="#2c3436"/><rect x="62" y="20" width="14" height="4" fill="#f2e3a6"/>'
         '<rect x="30" y="320" width="20" height="14" fill="#2c3436"/>')
    return d, b


@asset("semaforo", "exterior", 70, 300, "Semaforo urbano", "semaforo,calle")
def _():
    b = (sombra_suelo(35, 296, 22) + '<rect x="31" y="70" width="8" height="226" fill="#2b3234"/>'
         '<rect x="14" y="14" width="42" height="96" rx="6" fill="#1b2022"/>'
         '<circle cx="35" cy="34" r="9" fill="#a33"/><circle cx="35" cy="62" r="9" fill="#654"/><circle cx="35" cy="90" r="9" fill="#2a5"/>'
         '<rect x="14" y="14" width="42" height="96" rx="6" fill="#fff" opacity=".07"/>')
    return "", b


@asset("hidrante", "exterior", 60, 90, "Hidrante rojo gastado", "hidrante,calle,objeto")
def _():
    d = lin("g", "#b2453a", "#6b261f", 0, 0, 1, 0) + NOISE.format(s=9)
    b = (sombra_suelo(30, 87, 22) + '<rect x="18" y="30" width="24" height="56" rx="4" fill="url(#g)"/>'
         '<path d="M16 32Q30 6 44 32z" fill="url(#g)"/><rect x="8" y="46" width="44" height="12" rx="4" fill="url(#g)"/>'
         '<rect x="14" y="80" width="32" height="8" fill="#5b1e19"/>' + tex(60, 90, op=.8))
    return d, b


@asset("taxi", "exterior", 330, 120, "Taxi amarillo de perfil con volumen 2D", "taxi,vehiculo,calle")
def _():
    d = lin("g", "#f4d24a", "#b8901c", 0, 0, 0, 1) + lin("v", "#cfe3e6", "#5b7279", 0, 0, 1, 1)
    b = (sombra_suelo(165, 112, 150, 8, .45) +
         '<path d="M14 90Q10 62 40 58L90 52Q110 22 150 22H205Q236 24 252 54L304 62Q322 70 322 92V100H14z" fill="url(#g)"/>'
         '<path d="M100 54Q116 30 150 30H198Q224 32 238 54z" fill="url(#v)"/><line x1="170" y1="30" x2="170" y2="54" stroke="#b8901c" stroke-width="3"/>'
         '<rect x="150" y="12" width="40" height="11" rx="2" fill="#f2f0d0" stroke="#7a620f"/>'
         '<path d="M14 90H322" stroke="#0004" stroke-width="3"/>'
         '<circle cx="82" cy="100" r="19" fill="#161a1c"/><circle cx="82" cy="100" r="9" fill="#8a9293"/>'
         '<circle cx="256" cy="100" r="19" fill="#161a1c"/><circle cx="256" cy="100" r="9" fill="#8a9293"/>'
         '<path d="M14 62Q40 60 60 66" stroke="#fff" stroke-width="3" opacity=".35" fill="none"/>'
         '<rect x="316" y="76" width="8" height="10" fill="#f7ecb0"/><rect x="10" y="74" width="8" height="10" fill="#b33"/>')
    return d, b


@asset("auto_sedan", "exterior", 320, 110, "Sedan oscuro de perfil", "auto,vehiculo,calle")
def _():
    d = lin("g", "#4b5a63", "#1d262b", 0, 0, 0, 1) + lin("v", "#a9c1c8", "#38474d", 0, 0, 1, 1)
    b = (sombra_suelo(160, 104, 145, 8, .45) +
         '<path d="M10 86Q8 62 36 58L96 52Q116 26 160 26H196Q230 30 246 54L296 62Q314 68 314 88V96H10z" fill="url(#g)"/>'
         '<path d="M108 52Q122 34 160 34H192Q218 36 232 54z" fill="url(#v)"/>'
         '<circle cx="82" cy="96" r="18" fill="#101416"/><circle cx="82" cy="96" r="8" fill="#9aa"/>'
         '<circle cx="250" cy="96" r="18" fill="#101416"/><circle cx="250" cy="96" r="8" fill="#9aa"/>'
         '<path d="M12 62Q40 60 62 66" stroke="#fff" stroke-width="3" opacity=".25" fill="none"/>')
    return d, b


@asset("boca_tormenta", "exterior", 120, 36, "Rejilla de alcantarilla en el suelo", "suelo,calle,rejilla")
def _():
    b = '<ellipse cx="60" cy="18" rx="56" ry="14" fill="#0c0f10"/>'
    for x in range(14, 110, 10):
        b += f'<line x1="{x}" y1="6" x2="{x-4}" y2="30" stroke="#5a6366" stroke-width="3"/>'
    b += '<ellipse cx="60" cy="18" rx="56" ry="14" fill="none" stroke="#6b7679" stroke-width="3"/>'
    return "", b


@asset("cartel_neon", "exterior", 220, 90, "Cartel luminoso de comercio (texto editable en escena)", "cartel,neon,comercio")
def _():
    d = '<filter id="gl"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
    b = ('<rect x="4" y="4" width="212" height="82" rx="8" fill="#12171a" stroke="#3a4448" stroke-width="3"/>'
         '<text x="110" y="56" text-anchor="middle" font-family="Impact,Arial Black,sans-serif" font-size="38" fill="#ff7aa8" filter="url(#gl)" id="texto">EXTRA</text>')
    return d, b


@asset("valla_publicitaria", "exterior", 360, 240, "Valla publicitaria sobre estructura de acero", "valla,cartel,estructura")
def _():
    d = lin("g", "#c7c2b4", "#8d8878", 0, 0, 1, 1)
    b = ('<path d="M60 240V110M300 240V110M60 150L120 110M300 150L240 110" stroke="#3a4144" stroke-width="7" fill="none"/>'
         '<rect x="10" y="10" width="340" height="110" fill="#2b3234"/><rect x="18" y="18" width="324" height="94" fill="url(#g)"/>'
         '<circle cx="90" cy="65" r="28" fill="#d9a441"/><rect x="140" y="40" width="170" height="14" fill="#3a4448"/><rect x="140" y="64" width="120" height="10" fill="#6a7679"/>')
    return d, b


@asset("cables_electricos", "exterior", 600, 90, "Cables colgantes entre postes (primer plano)", "cables,primer plano")
def _():
    b = ""
    for dy in (0, 14, 30):
        b += f'<path d="M0 {10+dy}Q300 {70+dy} 600 {8+dy}" stroke="#14181a" stroke-width="2.5" fill="none"/>'
    return "", b


# ============================================================ INTERIOR
@asset("salon_chimenea", "interior", 700, 520, "Pared de salon senorial con chimenea y molduras", "interior,chimenea,pared,molduras")
def _():
    d = lin("g", "#e9e6df", "#bdb8ac", 0, 0, 1, 1) + lin("m", "#d6d2c8", "#948f82", 0, 0, 1, 0) + NOISE.format(s=11)
    b = '<rect width="700" height="520" fill="url(#g)"/>'
    for x in (40, 380):
        b += (f'<rect x="{x}" y="40" width="280" height="300" rx="14" fill="none" stroke="#9b9689" stroke-width="6"/>'
              f'<rect x="{x+14}" y="54" width="252" height="272" rx="8" fill="none" stroke="#fff" stroke-width="3" opacity=".6"/>')
    b += ('<rect x="230" y="270" width="240" height="250" fill="url(#m)"/><rect x="258" y="310" width="184" height="210" fill="#2a2522"/>'
          '<path d="M258 310Q350 270 442 310" fill="#3a332e"/><rect x="214" y="250" width="272" height="22" fill="#cfcabd"/>'
          '<rect x="0" y="480" width="700" height="40" fill="#b3ad9e"/>')
    for x in range(20, 700, 70):
        b += f'<rect x="{x}" y="0" width="22" height="520" fill="#0001"/>'
    b += tex(700, 520, op=.8)
    return d, b


@asset("pared_ladrillo", "interior", 520, 360, "Pared de ladrillo de callejon (tile grande)", "pared,ladrillo,callejon")
def _():
    r = random.Random(12)
    d = NOISE.format(s=12)
    b = '<rect width="520" height="360" fill="#7d5a49"/>'
    for y in range(0, 360, 20):
        off = 0 if (y // 20) % 2 == 0 else 30
        for x in range(-60, 540, 60):
            c = r.choice(["#8a6350", "#76523f", "#936b57", "#6d4c3b"])
            b += f'<rect x="{x+off}" y="{y}" width="58" height="18" fill="{c}"/>'
    b += '<rect width="520" height="360" fill="#000" opacity=".12"/>'
    b += '<path d="M0 0H520V70Q260 110 0 60z" fill="#000" opacity=".28"/>' + tex(520, 360)
    return d, b


@asset("caja_madera_g", "interior", 200, 190, "Caja de madera grande de almacen", "caja,madera,almacen")
def _():
    d = lin("g", "#a39a7e", "#6e6850", 0, 0, 1, 1)
    b = (sombra_suelo(100, 186, 92, 8) + '<rect x="8" y="8" width="184" height="176" fill="url(#g)" stroke="#3c3a2c" stroke-width="5"/>'
         '<path d="M8 8L192 184M192 8L8 184" stroke="#3c3a2c" stroke-width="5"/><rect x="8" y="8" width="184" height="30" fill="#fff" opacity=".12"/>'
         '<rect x="150" y="8" width="42" height="176" fill="#0003"/>')
    return d, b


@asset("caja_madera_p", "interior", 110, 100, "Caja de madera chica", "caja,madera,almacen")
def _():
    d = lin("g", "#a39a7e", "#6e6850", 0, 0, 1, 1)
    b = (sombra_suelo(55, 97, 50, 5) + '<rect x="5" y="5" width="100" height="90" fill="url(#g)" stroke="#3c3a2c" stroke-width="4"/>'
         '<path d="M5 5L105 95" stroke="#3c3a2c" stroke-width="4"/><rect x="82" y="5" width="23" height="90" fill="#0003"/>')
    return d, b


@asset("contenedor_basura", "interior", 280, 160, "Contenedor de basura metalico de callejon", "contenedor,basura,callejon")
def _():
    d = lin("g", "#4f6a62", "#26352f", 0, 0, 1, 1) + NOISE.format(s=13)
    b = (sombra_suelo(140, 158, 130, 9, .45) + '<path d="M10 40H270L256 156H24z" fill="url(#g)"/>'
         '<path d="M4 34H276V48H4z" fill="#33473f"/><path d="M10 40H270" stroke="#9db5aa" stroke-width="2" opacity=".5"/>'
         '<rect x="70" y="56" width="6" height="90" fill="#0003"/><rect x="140" y="56" width="6" height="90" fill="#0003"/><rect x="210" y="56" width="6" height="90" fill="#0003"/>'
         '<path d="M30 64Q60 70 90 60" stroke="#9fb7ab" stroke-width="3" opacity=".25" fill="none"/>' + tex(280, 160, op=.8))
    return d, b


@asset("ventana_barrotes", "interior", 120, 150, "Ventana con rejas y luz calida interior", "ventana,rejas")
def _():
    d = lin("g", "#f2b25a", "#c06a2a", 0, 0, 1, 1)
    b = ('<rect width="120" height="150" fill="#3a2f2b"/><rect x="10" y="10" width="100" height="130" fill="url(#g)"/>'
         '<path d="M10 10H110L90 140H10z" fill="#fff" opacity=".12"/>')
    for x in range(22, 110, 18):
        b += f'<rect x="{x}" y="10" width="5" height="130" fill="#14181a"/>'
    b += '<rect x="10" y="64" width="100" height="5" fill="#14181a"/>'
    return d, b


@asset("lampara_techo", "interior", 180, 120, "Lampara de techo industrial con cono de luz", "lampara,luz,techo")
def _():
    d = '<radialGradient id="c" cx=".5" cy="0" r=".9"><stop offset="0" stop-color="#fff6c8" stop-opacity=".55"/><stop offset="1" stop-color="#fff6c8" stop-opacity="0"/></radialGradient>'
    b = ('<line x1="90" y1="0" x2="90" y2="16" stroke="#222" stroke-width="3"/><path d="M62 40Q90 8 118 40z" fill="#2b3234"/>'
         '<path d="M62 40L10 120H170L118 40z" fill="url(#c)"/><ellipse cx="90" cy="40" rx="28" ry="4" fill="#fff6c8"/>')
    return d, b


@asset("sofa_cuero", "interior", 300, 130, "Sofa de cuero marron", "sofa,mueble,interior")
def _():
    d = lin("g", "#8b5a3b", "#4a2d1c", 0, 0, 0, 1)
    b = (sombra_suelo(150, 126, 140, 8) + '<rect x="14" y="30" width="272" height="64" rx="16" fill="url(#g)"/>'
         '<rect x="0" y="52" width="40" height="66" rx="14" fill="#6a4128"/><rect x="260" y="52" width="40" height="66" rx="14" fill="#4a2d1c"/>'
         '<rect x="30" y="78" width="240" height="38" rx="10" fill="#7a4d32"/><path d="M40 82H260" stroke="#c99a76" stroke-width="2" opacity=".4"/>')
    return d, b


@asset("cuadro_marco", "interior", 140, 170, "Cuadro con marco dorado", "cuadro,decoracion")
def _():
    d = lin("g", "#d9b45a", "#7a5f23", 0, 0, 1, 1) + lin("p", "#6a7e79", "#26343a", 0, 0, 1, 1)
    b = ('<rect width="140" height="170" fill="url(#g)"/><rect x="12" y="12" width="116" height="146" fill="url(#p)"/>'
         '<circle cx="70" cy="62" r="20" fill="#c1b293" opacity=".7"/><path d="M12 158Q50 90 128 150V158z" fill="#14201f" opacity=".7"/>')
    return d, b


# ============================================================ NATURALEZA
def arbol(seed, c1, c2, tronco="#4b382b", w=300, h=380, copas=7):
    r = random.Random(seed)
    d = lin("g", c1, c2, 0, 0, 1, 1)
    b = (sombra_suelo(w / 2, h - 3, w * .28, 8) + f'<path d="M{w/2-14} {h-4}Q{w/2-8} {h*.6} {w/2-4} {h*.45}H{w/2+8}Q{w/2+10} {h*.6} {w/2+18} {h-4}z" fill="{tronco}"/>'
         f'<path d="M{w/2+6} {h-4}Q{w/2+8} {h*.6} {w/2+8} {h*.45}H{w/2+18}Q{w/2+14} {h*.7} {w/2+22} {h-4}z" fill="#0004"/>')
    for i in range(copas):
        cx = w / 2 + r.uniform(-w * .28, w * .28); cy = h * .35 + r.uniform(-h * .18, h * .1); rr = r.uniform(w * .16, w * .26)
        b += f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{rr:.0f}" fill="url(#g)"/>'
    for i in range(copas):
        cx = w / 2 + r.uniform(-w * .25, w * .3); cy = h * .35 + r.uniform(-h * .15, h * .12); rr = r.uniform(w * .05, w * .1)
        b += f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{rr:.0f}" fill="#000" opacity=".14"/>'
    return d, b


@asset("arbol_verde", "naturaleza", 300, 380, "Arbol frondoso verde apagado (parque urbano)", "arbol,parque,verde")
def _(): return arbol(21, "#7a9a6a", "#33503a")


@asset("arbol_otonal", "naturaleza", 300, 380, "Arbol otonal ocre", "arbol,otono,ocre")
def _(): return arbol(22, "#c99a4a", "#7a4a22", "#3d2d22")


@asset("arbol_seco", "naturaleza", 260, 360, "Arbol sin hojas invernal", "arbol,seco,invierno")
def _():
    r = random.Random(23)
    b = sombra_suelo(130, 356, 60, 6)
    def rama(x, y, ang, ln, gr, dep):
        if dep == 0: return ""
        x2 = x + math.cos(ang) * ln; y2 = y - math.sin(ang) * ln
        s = f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#2f2620" stroke-width="{gr:.1f}" stroke-linecap="round"/>'
        s += rama(x2, y2, ang + r.uniform(.3, .6), ln * .72, gr * .7, dep - 1)
        s += rama(x2, y2, ang - r.uniform(.3, .6), ln * .72, gr * .7, dep - 1)
        return s
    b += rama(130, 356, math.pi / 2, 90, 12, 6)
    return "", b


@asset("palmera", "naturaleza", 240, 420, "Palmera tropical (Vice City)", "palmera,tropical,vice")
def _():
    d = lin("g", "#4fa86a", "#1f5a3a", 0, 0, 1, 1)
    b = sombra_suelo(120, 416, 50, 6) + '<path d="M112 416Q120 250 128 120H138Q136 260 140 416z" fill="#8a6a48"/>'
    for y in range(140, 410, 22):
        b += f'<path d="M116 {y}Q128 {y-6} 138 {y}" stroke="#4a3624" stroke-width="3" fill="none"/>'
    for ang in (-160, -120, -80, -40, 0, 30, 170, 200):
        a = math.radians(ang)
        ex = 132 + math.cos(a) * 110; ey = 118 - math.sin(a) * 60 + (45 if abs(math.cos(a)) > .6 else 0)
        b += f'<path d="M132 118Q{(132+ex)/2:.0f} {min(118,ey)-40:.0f} {ex:.0f} {ey:.0f}Q{(132+ex)/2:.0f} {min(118,ey)-18:.0f} 132 122z" fill="url(#g)"/>'
    return d, b


@asset("arbusto", "naturaleza", 160, 90, "Arbusto bajo", "arbusto,vegetacion,suelo")
def _():
    d = lin("g", "#6f9560", "#2d4a33", 0, 0, 1, 1)
    b = sombra_suelo(80, 86, 70, 5)
    for cx, cy, r in ((40, 56, 32), (80, 44, 38), (120, 58, 30), (60, 62, 28), (100, 64, 26)):
        b += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#g)"/>'
    return d, b


@asset("pasto_mata", "naturaleza", 100, 50, "Mata de pasto salvaje (grietas, bordes)", "pasto,suelo,detalle")
def _():
    r = random.Random(24)
    b = ""
    for i in range(26):
        x = 10 + i * 3.2; h = r.randint(18, 46); lean = r.randint(-10, 10)
        b += f'<path d="M{x} 50Q{x+lean/2} {50-h/2} {x+lean} {50-h}" stroke="{r.choice(["#5f8a4f","#486e3d","#7aa05d"])}" stroke-width="2.2" fill="none"/>'
    return "", b


@asset("hojas_suelo", "naturaleza", 120, 30, "Hojas secas esparcidas en el suelo", "hojas,suelo,detalle")
def _():
    r = random.Random(25); b = ""
    for i in range(9):
        x = r.randint(8, 110); y = r.randint(6, 24)
        b += f'<ellipse cx="{x}" cy="{y}" rx="7" ry="3" transform="rotate({r.randint(0,180)} {x} {y})" fill="{r.choice(["#a8782f","#8a5a22","#b9893a","#6f4a22"])}"/>'
    return "", b


# ============================================================ BASURA / SUELO
@asset("vaso_tirado", "basura", 40, 26, "Vaso descartable tirado", "vaso,basura,detalle")
def _():
    return "", ('<ellipse cx="20" cy="23" rx="16" ry="3" fill="#000" opacity=".3"/><path d="M6 14L32 8L36 22L12 24z" fill="#e6dfd0"/>'
                '<path d="M6 14L32 8L36 22L12 24z" fill="none" stroke="#a33" stroke-width="2" stroke-dasharray="4 5"/><ellipse cx="9" cy="19" rx="4" ry="7" fill="#9a8f7e"/>')


@asset("lata_aplastada", "basura", 30, 24, "Lata de gaseosa tirada", "lata,basura,detalle")
def _():
    return "", ('<ellipse cx="15" cy="21" rx="13" ry="2.5" fill="#000" opacity=".3"/><rect x="3" y="9" width="24" height="12" rx="2" fill="#b33"/>'
                '<rect x="3" y="9" width="24" height="4" fill="#fff" opacity=".25"/><ellipse cx="4" cy="15" rx="2.5" ry="6" fill="#9aa"/>')


@asset("papel_arrugado", "basura", 28, 24, "Bola de papel arrugado", "papel,basura,detalle")
def _():
    return "", ('<ellipse cx="14" cy="21" rx="11" ry="2.5" fill="#000" opacity=".25"/><path d="M4 16L8 6L16 4L24 9L25 18L15 22z" fill="#d6d2c4"/>'
                '<path d="M8 6L14 14L24 9M14 14L15 22" stroke="#8d8878" fill="none"/>')


@asset("bolsa_basura", "basura", 70, 70, "Bolsa de residuos negra", "bolsa,basura")
def _():
    d = lin("g", "#3b4144", "#0f1213", 0, 0, 1, 1)
    return d, (sombra_suelo(35, 66, 30, 4) + '<path d="M12 62Q4 32 22 22L18 8L30 16L40 6L42 20Q64 28 58 62z" fill="url(#g)"/>'
               '<path d="M20 30Q30 24 44 30" stroke="#fff" stroke-width="2" opacity=".18" fill="none"/>')


@asset("botella_vidrio", "basura", 24, 50, "Botella de vidrio verde", "botella,vidrio,basura")
def _():
    return "", ('<ellipse cx="12" cy="47" rx="9" ry="2.5" fill="#000" opacity=".3"/><path d="M8 46V22Q8 18 10 12V4H14V12Q16 18 16 22V46z" fill="#3f8a5a" opacity=".9"/>'
                '<rect x="9.5" y="22" width="2" height="22" fill="#fff" opacity=".35"/>')


@asset("charco", "basura", 160, 30, "Charco de agua con reflejo", "charco,suelo,agua")
def _():
    d = lin("g", "#9fb9c3", "#3b525c", 0, 0, 1, 1)
    return d, '<path d="M6 16Q20 4 80 6T154 14Q140 28 80 26T6 16z" fill="url(#g)"/><path d="M30 12Q60 8 90 12" stroke="#fff" stroke-width="2" opacity=".5" fill="none"/>'


@asset("grieta_suelo", "basura", 180, 30, "Grieta de pavimento", "grieta,suelo,asfalto")
def _():
    return "", '<path d="M4 20L40 14L52 22L90 10L110 18L150 8L176 14" stroke="#0d0f10" stroke-width="3" fill="none" stroke-linejoin="round"/><path d="M52 22L60 28M110 18L118 26" stroke="#0d0f10" stroke-width="2"/>'


@asset("piedritas", "basura", 90, 20, "Piedritas y tierra suelta", "piedras,suelo,detalle")
def _():
    r = random.Random(26); b = ""
    for i in range(14):
        x = r.randint(6, 84); y = r.randint(6, 17); rr = r.uniform(1.5, 4.5)
        b += f'<ellipse cx="{x}" cy="{y}" rx="{rr:.1f}" ry="{rr*.7:.1f}" fill="{r.choice(["#6f6a62","#8a847a","#4e4a44"])}"/>'
    return "", b


@asset("caja_carton", "basura", 90, 70, "Caja de carton aplastada", "carton,basura")
def _():
    d = lin("g", "#b8956a", "#7a5f3e", 0, 0, 1, 1)
    return d, sombra_suelo(45, 67, 40, 4) + '<path d="M6 58L14 22L76 18L86 56z" fill="url(#g)"/><path d="M14 22L46 36L76 18" stroke="#5a452c" stroke-width="2" fill="none"/>'


@asset("alfombra_enrollada", "basura", 170, 60, "Alfombra roja enrollada (escena del callejon)", "alfombra,objeto,rojo", rol="sujeto")
def _():
    d = lin("g", "#c0463b", "#7a1f1a", 0, 0, 0, 1)
    b = (sombra_suelo(85, 56, 78, 5) + '<rect x="12" y="10" width="146" height="40" rx="20" fill="url(#g)"/>'
         '<ellipse cx="18" cy="30" rx="12" ry="20" fill="#e0b37a"/><ellipse cx="18" cy="30" rx="6" ry="11" fill="#8f2a24"/>')
    for x in range(40, 150, 22):
        b += f'<path d="M{x} 14Q{x+6} 30 {x} 46" stroke="#e0b37a" stroke-width="2.5" fill="none" opacity=".7"/>'
    return d, b


# ---- suelos (tiras repetibles)
def _suelo(id, desc, c1, c2, seed, extra=""):
    @asset(id, "suelos", 1200, 160, desc, "suelo,textura,base")
    def _():
        r = random.Random(seed)
        d = lin("g", c1, c2, 0, 0, 0, 1) + NOISE.format(s=seed)
        b = '<rect width="1200" height="160" fill="url(#g)"/>'
        for i in range(60):
            x = r.randint(0, 1200); y = r.randint(10, 150); w = r.randint(8, 50)
            b += f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="{w*.12:.0f}" fill="#000" opacity="{r.uniform(.04,.14):.2f}"/>'
        b += extra(r) if extra else ""
        b += tex(1200, 160, op=1)
        return d, b


def _juntas(r):
    s = ""
    for x in range(0, 1200, 120):
        s += f'<line x1="{x}" y1="0" x2="{x-26}" y2="160" stroke="#0007" stroke-width="2"/>'
    s += '<line x1="0" y1="80" x2="1200" y2="80" stroke="#0005" stroke-width="2"/>'
    return s


def _lineas_calle(r):
    return ('<rect x="0" y="70" width="1200" height="8" fill="#e8d98a" opacity=".55"/>' +
            "".join(f'<rect x="{x}" y="130" width="80" height="6" fill="#fff" opacity=".35"/>' for x in range(30, 1200, 220)))


_suelo("suelo_asfalto", "Asfalto gastado con manchas", "#4a5558", "#242c2f", 31, _lineas_calle)
_suelo("suelo_vereda", "Vereda de concreto con juntas", "#a2a398", "#6c6d65", 32, _juntas)
_suelo("suelo_tierra", "Tierra y grava", "#8a735a", "#4f4034", 33)
_suelo("suelo_pasto", "Pasto de parque", "#6f9560", "#304a35", 34)
_suelo("suelo_interior", "Piso interior de madera/baldosa", "#9a8366", "#5a4a38", 35, _juntas)
_suelo("suelo_arena", "Arena costera (Vice City)", "#e3cf9f", "#b39966", 36)


# ============================================================ PROPS / ARMAS
@asset("pistola_urbana", "props", 120, 80, "Pistola semiautomatica compacta (prop)", "arma,pistola,prop", rol="sujeto")
def _():
    d = lin("g", "#59656b", "#161c1f", 0, 0, 0, 1)
    return d, ('<path d="M8 22H90V38H58L52 70H32L38 38H8z" fill="url(#g)"/><rect x="8" y="22" width="82" height="5" fill="#fff" opacity=".2"/>'
               '<circle cx="46" cy="42" r="6" fill="none" stroke="#0f1315" stroke-width="3"/><rect x="88" y="26" width="30" height="7" fill="#0f1315"/>')


@asset("rifle_asalto", "props", 300, 90, "Rifle de asalto de madera y acero", "arma,rifle,prop", rol="sujeto")
def _():
    d = lin("g", "#4e5a60", "#161c1f", 0, 0, 0, 1) + lin("w", "#9a6a3e", "#5a3a1c", 0, 0, 0, 1)
    return d, ('<path d="M0 40L50 28H90L100 20H205V34H290V44H205V54H100L92 76H66L72 54H44L18 70L0 66z" fill="url(#w)"/>'
               '<rect x="96" y="22" width="190" height="14" fill="url(#g)"/><path d="M110 40Q130 82 160 62V40z" fill="#222"/>')


@asset("rifle_francotirador", "props", 360, 90, "Rifle de francotirador con mira y bipode", "arma,francotirador,prop", rol="sujeto")
def _():
    d = lin("g", "#4e5a60", "#161c1f", 0, 0, 0, 1) + lin("m", "#5a7a66", "#1a2a22", 0, 0, 0, 1)
    return d, ('<rect x="30" y="38" width="320" height="10" fill="url(#g)"/><path d="M0 52L40 36H120V56H60L20 80z" fill="url(#g)"/>'
               '<rect x="110" y="18" width="110" height="14" rx="6" fill="url(#m)"/><circle cx="108" cy="25" r="11" fill="#14201a"/>'
               '<path d="M270 50L290 82M284 50L304 82" stroke="#161c1f" stroke-width="3"/>')


@asset("placa_policia", "props", 70, 80, "Placa de policia dorada (prop de la escena del auto)", "placa,policia,prop", rol="sujeto")
def _():
    d = lin("g", "#f2d27a", "#9a7220", 0, 0, 1, 1)
    return d, ('<rect x="2" y="2" width="66" height="76" rx="10" fill="#3b2a24"/><path d="M35 8L58 18V44Q58 62 35 72Q12 62 12 44V18z" fill="url(#g)"/>'
               '<circle cx="35" cy="40" r="12" fill="#c8a24a" stroke="#6b4c14" stroke-width="2"/>')


@asset("cigarro_puro", "props", 70, 16, "Puro encendido", "cigarro,prop", rol="sujeto")
def _():
    return "", ('<rect x="4" y="4" width="56" height="9" rx="3" fill="#7a4d2a"/><rect x="46" y="4" width="6" height="9" fill="#d9b45a"/>'
                '<rect x="58" y="4" width="8" height="9" rx="2" fill="#e3641f"/>')


@asset("anteojos_sol", "props", 90, 36, "Anteojos de sol oscuros ochenteros", "anteojos,ropa,vice", rol="sujeto")
def _():
    d = lin("g", "#d99a3a", "#5a2f10", 0, 0, 1, 1)
    return d, ('<path d="M4 8H86L80 24Q74 34 62 30L50 18H40L28 30Q16 34 10 24z" fill="url(#g)" stroke="#14181a" stroke-width="3"/>'
               '<path d="M10 12L30 12" stroke="#fff" stroke-width="2" opacity=".5"/>')


@asset("cadena_oro", "props", 60, 70, "Cadena de oro con medallon", "cadena,joyeria,prop", rol="sujeto")
def _():
    d = lin("g", "#f4d86a", "#9a6f16", 0, 0, 1, 1)
    return d, '<path d="M6 4Q30 70 54 4" stroke="url(#g)" stroke-width="4" fill="none"/><circle cx="30" cy="52" r="11" fill="url(#g)"/><circle cx="30" cy="52" r="6" fill="none" stroke="#7a5a10" stroke-width="2"/>'


# ============================================================ PERSONAJES
def persona(id, desc, chaqueta, pantalon, piel, pelo, w=240, h=520, extra="", rol="sujeto", tags=""):
    @asset(id, "personajes", w, h, desc, "personaje,"+tags, rol=rol)
    def _():
        d = (lin("j", chaqueta[0], chaqueta[1], 0, 0, 1, 1) + lin("p", pantalon[0], pantalon[1], 0, 0, 1, 1) +
             lin("k", piel[0], piel[1], 0, 0, 1, 1) + lin("h", pelo[0], pelo[1], 0, 0, 1, 1))
        b = (sombra_suelo(120, 514, 70, 8, .45) +
             # piernas
             '<g id="piernas"><path d="M88 300L84 500H116L124 340L134 500H166L158 300z" fill="url(#p)"/>'
             '<path d="M120 320L124 340L134 500H166L162 330z" fill="#000" opacity=".22"/>'
             '<path d="M78 500H118V514H72z" fill="#14181a"/><path d="M132 500H172L180 514H128z" fill="#14181a"/></g>'
             # torso/chaqueta
             '<g id="torso"><path d="M62 170Q70 140 100 130H146Q176 140 184 170L196 310H52z" fill="url(#j)"/>'
             '<path d="M150 134Q180 144 184 172L196 310H156z" fill="#000" opacity=".25"/>'
             '<path d="M100 130L124 190L146 130" fill="url(#k)"/><path d="M120 190V310" stroke="#0006" stroke-width="3"/>'
             '<path d="M70 190Q90 210 80 250" stroke="#fff" stroke-width="2" opacity=".18" fill="none"/></g>'
             # brazos
             '<g id="brazo_i"><path d="M62 172L38 300L56 312L84 200z" fill="url(#j)"/><path d="M38 300L56 312L52 334L34 326z" fill="url(#k)"/></g>'
             '<g id="brazo_d"><path d="M184 172L208 300L190 312L162 200z" fill="url(#j)"/><path d="M208 300L190 312L194 334L212 326z" fill="url(#k)"/>'
             '<path d="M184 172L208 300L190 312z" fill="#000" opacity=".2"/></g>'
             # cabeza
             '<g id="cabeza"><rect x="108" y="102" width="30" height="34" fill="url(#k)"/>'
             '<path d="M84 66Q84 22 124 20Q164 22 164 66Q164 108 124 118Q84 108 84 66z" fill="url(#k)"/>'
             '<path d="M140 30Q164 40 164 66Q164 108 124 118Q146 100 146 66z" fill="#000" opacity=".2"/>'
             '<path d="M82 62Q80 18 126 16Q170 16 166 62Q154 40 126 38Q96 40 82 62z" fill="url(#h)"/>'
             '<path d="M98 64Q108 60 118 66M134 66Q144 60 154 64" stroke="#2a1d16" stroke-width="4" fill="none" stroke-linecap="round"/>'
             '<circle cx="110" cy="72" r="3.5" fill="#14181a"/><circle cx="144" cy="72" r="3.5" fill="#14181a"/>'
             '<path d="M126 74Q122 92 130 94" stroke="#0005" stroke-width="3" fill="none"/>'
             '<path d="M112 102Q126 108 140 102" stroke="#5a2a22" stroke-width="3.5" fill="none" stroke-linecap="round"/>'
             + extra + '</g>')
        return d, b


persona("npc_campera_marron", "Personaje con campera marron y guantes (estilo calle)", ("#8a6140", "#4a3220"), ("#2b3946", "#141c24"),
        ("#d9a984", "#8a5f44"), ("#3a2a20", "#150f0b"), tags="npc,calle,marron")
persona("npc_traje_oscuro", "Personaje de traje oscuro y corbata", ("#34454c", "#141c20"), ("#2a3238", "#12171a"),
        ("#e0b898", "#8f6a50"), ("#2a2622", "#0c0a09"), tags="npc,traje,formal",
        extra='<path d="M112 130L124 190L136 130" fill="#e8e6df"/><path d="M121 134L124 190L127 134" fill="#5a2a2a"/>')
persona("npc_chandal_azul", "Personaje con chandal azul de rayas blancas", ("#2d4a5e", "#122230"), ("#28333c", "#10171c"),
        ("#cfa07c", "#7e5640"), ("#201a17", "#0a0807"), tags="npc,chandal,calle",
        extra='<path d="M84 150L70 170M84 160L72 178" stroke="#fff" stroke-width="3"/>')
persona("anfitrion_extra", "Anfitrion de Extra: peinado hacia atras, camisa abierta ochentera, aire de banda de rock simpatico", ("#2fd0c0", "#16706a"), ("#e8e1cf", "#a8a08a"),
        ("#e2b490", "#9a6a4e"), ("#241a14", "#0a0706"), tags="anfitrion,vice,protagonista,mascota-humana",
        extra=('<path d="M84 52Q90 6 128 10Q170 10 166 52Q158 24 128 24Q98 26 84 52z" fill="url(#h)"/>'
               '<path d="M96 100Q124 126 152 100Q142 120 124 122Q106 120 96 100z" fill="#3a2a20" opacity=".35"/>'
               '<path d="M112 104Q126 112 140 104" stroke="#fff" stroke-width="2.2" fill="none" opacity=".7"/>'
               '<circle cx="126" cy="168" r="6" fill="#f0c859"/>'))


# --- siluetas para la tecnica silueta-dentro-de-silueta
@asset("silueta_hombre_hombros", "personajes", 480, 700, "Silueta de hombre de espaldas hasta caderas (mascara para intros)", "silueta,mascara,intro", rol="sujeto", ancla="centro")
def _():
    b = ('<path d="M240 20Q300 20 306 90Q306 150 276 170Q330 180 372 210Q440 240 452 330L470 700H10L28 330Q40 240 108 210Q150 180 204 170Q174 150 174 90Q180 20 240 20z" fill="#000"/>')
    return "", b


@asset("silueta_hombre_entero", "personajes", 120, 300, "Silueta de hombre de pie mirando la ciudad", "silueta,mascara,intro", rol="sujeto")
def _():
    return "", ('<path d="M60 8Q78 8 80 30Q80 46 70 52Q96 56 100 80L104 170L96 172L92 120L90 296H70L64 190L58 296H34L32 120L28 172L20 170L24 80Q28 56 50 52Q40 46 40 30Q42 8 60 8z" fill="#0c0c0c"/>')


# --- mascota: pistola 10mm estilo Fallout 3 (rig por partes)
@asset("mascota_pistola_10mm", "mascota", 420, 300, "Mascota: pistola 10mm de Fallout 3 (rig: cuerpo, martillo, ojos, boca, brazos)", "mascota,pistola,fallout,10mm",
       rol="sujeto")
def _():
    d = (lin("m", "#8a9499", "#2a3236", 0, 0, 0, 1) + lin("w", "#7a4d2a", "#3c230f", 0, 0, 1, 1) +
         lin("s", "#cfd6d8", "#6b777c", 0, 0, 1, 0))
    b = (sombra_suelo(210, 292, 150, 8, .4) +
         '<g id="cuerpo">'
         # empunadura de madera
         '<path d="M96 120L150 120L132 270Q120 284 92 274L72 266Z" fill="url(#w)"/>'
         '<path d="M100 130L112 262M120 130L130 260" stroke="#2a1608" stroke-width="2" opacity=".5"/>'
         '<path d="M150 120L132 270" stroke="#000" stroke-width="10" opacity=".25"/>'
         # corredera
         '<path d="M40 46H350Q372 46 374 68L370 118H60Q40 118 40 96Z" fill="url(#m)"/>'
         '<rect x="40" y="46" width="334" height="9" fill="#fff" opacity=".3"/>'
         '<rect x="60" y="100" width="300" height="18" fill="#000" opacity=".25"/>'
         # cañon
         '<rect x="350" y="62" width="62" height="40" rx="6" fill="url(#m)"/><circle cx="408" cy="82" r="11" fill="#0c0f10"/>'
         # guardamonte
         '<path d="M150 120Q150 168 200 168Q230 168 232 120" stroke="#2a3236" stroke-width="9" fill="none"/>'
         '<path d="M196 122L206 150L214 122" fill="#1a2024"/>'
         # ranuras
         '<g stroke="#161b1e" stroke-width="5">' + "".join(f'<line x1="{x}" y1="52" x2="{x+8}" y2="92"/>' for x in range(70, 140, 14)) + '</g>'
         '<text x="258" y="82" font-family="Arial Black,Arial" font-size="20" fill="#161b1e" opacity=".7">10mm</text>'
         '</g>'
         '<g id="martillo"><path d="M30 46Q10 30 20 20L44 28L52 50z" fill="url(#m)"/></g>'
         # cara
         '<g id="ojos"><circle cx="150" cy="80" r="15" fill="#fff"/><circle cx="198" cy="80" r="15" fill="#fff"/>'
         '<circle id="pupila_i" cx="154" cy="82" r="7" fill="#14181a"/><circle id="pupila_d" cx="202" cy="82" r="7" fill="#14181a"/>'
         '<path d="M130 62Q150 52 168 62M180 62Q198 52 220 62" stroke="#161b1e" stroke-width="5" fill="none" stroke-linecap="round" id="cejas"/></g>'
         '<g id="boca"><path d="M160 104Q176 118 192 104" stroke="#161b1e" stroke-width="4" fill="#3a1010" stroke-linecap="round"/></g>'
         # brazos y piernas cortitas (rig)
         '<g id="brazo_i"><path d="M96 150Q60 170 58 200" stroke="#161b1e" stroke-width="10" fill="none" stroke-linecap="round"/><circle cx="58" cy="204" r="12" fill="#e8e8e8"/></g>'
         '<g id="brazo_d"><path d="M150 160Q196 190 214 170" stroke="#161b1e" stroke-width="10" fill="none" stroke-linecap="round"/><circle cx="216" cy="168" r="12" fill="#e8e8e8"/></g>'
         '<g id="pierna_i"><path d="M100 270L96 292" stroke="#161b1e" stroke-width="10" stroke-linecap="round"/><ellipse cx="94" cy="296" rx="16" ry="6" fill="#222"/></g>'
         '<g id="pierna_d"><path d="M126 270L130 292" stroke="#161b1e" stroke-width="10" stroke-linecap="round"/><ellipse cx="132" cy="296" rx="16" ry="6" fill="#222"/></g>')
    return d, b


# ============================================================ EFECTOS
@asset("rayos_luz", "efectos", 400, 700, "Haces de luz diagonales (volumetrica)", "luz,rayos,atmosfera")
def _():
    d = '<linearGradient id="r" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff6d0" stop-opacity=".55"/><stop offset="1" stop-color="#fff6d0" stop-opacity="0"/></linearGradient>'
    b = ""
    for x, w in ((20, 60), (110, 36), (190, 80), (300, 40)):
        b += f'<path d="M{x} 0H{x+w}L{x+w+120} 700H{x+60}z" fill="url(#r)"/>'
    return d, b


@asset("humo_nube", "efectos", 300, 220, "Nube de humo/vapor de alcantarilla", "humo,vapor,atmosfera")
def _():
    d = '<radialGradient id="h"><stop offset="0" stop-color="#fff" stop-opacity=".6"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
    return d, "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#h)"/>' for x, y, r in ((80, 140, 70), (150, 100, 90), (220, 130, 70), (130, 160, 60)))


@asset("polvo_particulas", "efectos", 400, 300, "Particulas de polvo en el aire", "polvo,particulas,atmosfera")
def _():
    r = random.Random(40)
    return "", "".join(f'<circle cx="{r.randint(0,400)}" cy="{r.randint(0,300)}" r="{r.uniform(.8,2.4):.1f}" fill="#fff" opacity="{r.uniform(.15,.6):.2f}"/>' for _ in range(70))


@asset("nube_cielo", "efectos", 360, 110, "Nube de cielo estilo pintado", "nube,cielo")
def _():
    d = lin("g", "#ffffff", "#c8d4d8", 0, 0, 0, 1)
    return d, "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="url(#g)" opacity=".9"/>' for x, y, rx, ry in ((100, 70, 80, 30), (190, 54, 90, 38), (270, 72, 70, 26)))


@asset("pajaro_vuelo", "efectos", 40, 20, "Pajaro volando (silueta, animable)", "pajaro,ambiente")
def _():
    return "", '<path d="M2 12Q10 0 20 10Q30 0 38 12Q30 6 20 14Q10 6 2 12z" fill="#1b2127"/>'


# ============================================================ ESCRIBIR
def main():
    catalogo = []
    for a in REGISTRO:
        defs, cuerpo = a["fn"]()
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {a["w"]} {a["h"]}" width="{a["w"]}" height="{a["h"]}">'
               f'<defs>{defs}</defs>{cuerpo}</svg>')
        d = os.path.join(SALIDA, a["cat"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, a["id"] + ".svg"), "w", encoding="utf-8") as f:
            f.write(svg)
        catalogo.append({k: a[k] for k in ("id", "cat", "w", "h", "desc", "rol", "ancla", "tags")} |
                        {"archivo": f'assets/{a["cat"]}/{a["id"]}.svg'})
    with open(os.path.join(RAIZ, "catalogo.json"), "w", encoding="utf-8") as f:
        json.dump({"version": 1, "assets": catalogo}, f, ensure_ascii=False, indent=1)
    print(f"{len(catalogo)} assets escritos en {SALIDA}")


if __name__ == "__main__":
    main()
