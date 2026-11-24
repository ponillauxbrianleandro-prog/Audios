"""Assets de alta fidelidad (v2): texturas fotograficas CC0 'pintadas' + iluminacion y suciedad.
Se registran con los MISMOS ids que los de v1 (el ultimo registrado gana), asi las escenas viejas mejoran solas.
Las texturas se referencian como @TEX/<nombre>.webp (el motor reemplaza por la ruta real)."""
import random, math
from generar_assets import asset, lin, sombra_suelo

BLUR = ('<filter id="b2" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2"/></filter>'
        '<filter id="b5" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="5"/></filter>'
        '<filter id="b10" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="10"/></filter>')


def pat(i, tex, s=256, extra=""):
    return (f'<pattern id="{i}" patternUnits="userSpaceOnUse" width="{s}" height="{s}">'
            f'<image href="@TEX/{tex}.webp" width="{s}" height="{s}" preserveAspectRatio="none"/>{extra}</pattern>')


def tinte(w, h, color, op=.55, modo="multiply", clip=""):
    return f'<rect width="{w}" height="{h}" fill="{color}" opacity="{op}" style="mix-blend-mode:{modo}" {clip}/>'


def luz_rect(w, h, x=0, y=0, clip=""):
    """Luz arriba-izquierda, sombra derecha/abajo y oclusion ambiental inferior."""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#lzL)" style="mix-blend-mode:soft-light" {clip}/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#lzS)" {clip}/>')


LUZ_DEFS = (lin("lzL", "#ffffff", "#000000", 0, 0, 1, 1) +
            '<linearGradient id="lzS" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset=".7" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".45"/></linearGradient>')


# ============================================================ EDIFICIOS
def edificio_hd(w, h, tex, color, ventanas, escalera=False, seed=1, ac=True):
    r = random.Random(seed)
    d = LUZ_DEFS + BLUR + pat("pt", tex, 300) + lin("vd", "#9fb8c2", "#1d2a31", 0, 0, 1, 1) + lin("sl", "#fff", "#fff0", 0, 0, 0, 1)
    d += '<linearGradient id="gr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity=".55"/><stop offset="1" stop-color="#000" stop-opacity="0"/></linearGradient>'
    b = f'<rect width="{w}" height="{h}" fill="url(#pt)"/>' + tinte(w, h, color, .5) + luz_rect(w, h)
    cols, filas = ventanas
    ww = w / (cols * 2.0); wh = 58
    for j in range(filas):
        for i in range(cols):
            x = (i * 2 + .5) * ww; y = 56 + j * 118
            estado = r.random()
            interior = "#e9d49b" if estado < .2 else ("#0f1518" if estado < .75 else "#3d4a52")
            b += (f'<rect x="{x-7}" y="{y-7}" width="{ww+14}" height="{wh+14}" fill="#c4b9a6" opacity=".9"/>'      # marco de piedra
                  f'<rect x="{x-3}" y="{y-3}" width="{ww+6}" height="{wh+6}" fill="#1a1f22"/>'
                  f'<rect x="{x}" y="{y}" width="{ww}" height="{wh}" fill="{interior}"/>'
                  + (f'<rect x="{x}" y="{y}" width="{ww*.4}" height="{wh}" fill="#6b3a2e" opacity=".55"/>' if estado > .75 else "") +   # cortina
                  f'<path d="M{x} {y}H{x+ww}L{x+ww*.55} {y+wh}H{x}z" fill="url(#vd)" opacity=".38"/>'               # reflejo del cielo
                  f'<line x1="{x+ww/2}" y1="{y}" x2="{x+ww/2}" y2="{y+wh}" stroke="#1a1f22" stroke-width="3"/>'
                  f'<rect x="{x-9}" y="{y+wh+4}" width="{ww+18}" height="7" fill="#b2a791"/>'
                  f'<rect x="{x-9}" y="{y+wh+11}" width="{ww+18}" height="3" fill="#000" opacity=".35"/>'
                  f'<rect x="{x-2}" y="{y+wh+11}" width="{ww+4}" height="{r.randint(40,90)}" fill="url(#gr)" opacity=".5" filter="url(#b5)"/>')  # churrete de suciedad
            if ac and r.random() < .25:
                b += (f'<rect x="{x+4}" y="{y+wh+14}" width="{ww-8}" height="22" fill="#cfcfc8" stroke="#555" stroke-width="2"/>'
                      f'<line x1="{x+10}" y1="{y+wh+22}" x2="{x+ww-10}" y2="{y+wh+22}" stroke="#777" stroke-width="2"/>')
    if escalera:
        for j in range(filas):
            y = 56 + j * 118 + 70
            b += (f'<rect x="{w*.08}" y="{y}" width="{w*.84}" height="6" fill="#171c1f"/>'
                  f'<path d="M{w*.08} {y}V{y-30}M{w*.92} {y}V{y-30}M{w*.08} {y-30}H{w*.92}" stroke="#171c1f" stroke-width="3.5" fill="none"/>')
            for xx in range(int(w * .1), int(w * .92), 14):
                b += f'<line x1="{xx}" y1="{y-30}" x2="{xx}" y2="{y}" stroke="#171c1f" stroke-width="1.6"/>'
            b += f'<rect x="{w*.08}" y="{y+6}" width="{w*.84}" height="14" fill="#000" opacity=".25" filter="url(#b5)"/>'
        b += (f'<path d="M{w*.5} 120 L{w*.84} {56+(filas-1)*118+70}" stroke="#171c1f" stroke-width="5"/>'
              f'<path d="M{w*.56} 120 L{w*.9} {56+(filas-1)*118+70}" stroke="#171c1f" stroke-width="3"/>')
    b += (f'<rect width="{w}" height="14" fill="#0006"/><rect y="14" width="{w}" height="6" fill="#d8cfbd" opacity=".55"/>'
          f'<rect width="{w}" height="{h}" fill="url(#sl)" opacity=".1"/>'
          f'<rect y="{h-70}" width="{w}" height="70" fill="url(#gr)" opacity=".5" transform="translate(0,{h}) scale(1,-1) translate(0,{-h})" style="mix-blend-mode:multiply"/>')
    return d, b


@asset("edificio_ladrillo_a", "exterior", 360, 640, "Edificio de ladrillo realista con ventanas, marcos y suciedad", "edificio,ladrillo,ciudad")
def _(): return edificio_hd(360, 640, "ladrillo", "#9a8a80", (3, 5), seed=1)


@asset("edificio_ladrillo_b", "exterior", 300, 520, "Edificio bajo de piedra/ladrillo", "edificio,ladrillo")
def _(): return edificio_hd(300, 520, "piedra", "#a09080", (2, 4), seed=2)


@asset("edificio_escalera_incendio", "exterior", 340, 640, "Edificio con escaleras de incendio de acero", "edificio,escalera,ciudad")
def _(): return edificio_hd(340, 640, "ladrillo", "#8a7a70", (3, 5), True, seed=3)


@asset("edificio_oficinas", "exterior", 280, 720, "Torre de oficinas con fachada vidriada y reflejos", "edificio,torre,vidrio")
def _():
    r = random.Random(4)
    d = LUZ_DEFS + pat("pt", "vidrio_sucio", 280) + lin("rf", "#dfeef2", "#33474f", 0, 0, 1, 1)
    b = '<rect width="280" height="720" fill="url(#pt)"/>' + tinte(280, 720, "#6d8794", .6)
    for y in range(18, 700, 28):
        for x in range(12, 270, 24):
            on = r.random() < .18
            b += f'<rect x="{x}" y="{y}" width="18" height="20" fill="{"#f2e0a0" if on else "#18242b"}" opacity=".9"/>'
    b += ('<rect width="280" height="720" fill="url(#rf)" opacity=".28" style="mix-blend-mode:screen"/>' + luz_rect(280, 720) +
          '<rect x="205" width="75" height="720" fill="#000" opacity=".28"/>')
    return d, b


@asset("pared_ladrillo", "interior", 520, 360, "Pared de ladrillo de callejon con luz, humedad y manchas", "pared,ladrillo,callejon")
def _():
    d = LUZ_DEFS + BLUR + pat("pt", "ladrillo", 340) + '<radialGradient id="ha"><stop offset="0" stop-color="#2a2f28" stop-opacity=".6"/><stop offset="1" stop-color="#2a2f28" stop-opacity="0"/></radialGradient>'
    b = ('<rect width="520" height="360" fill="url(#pt)"/>' + tinte(520, 360, "#8a7468", .55) + luz_rect(520, 360) +
         '<ellipse cx="120" cy="320" rx="150" ry="70" fill="url(#ha)"/><ellipse cx="430" cy="300" rx="110" ry="80" fill="url(#ha)"/>'
         '<path d="M0 0H520V60Q260 120 0 70z" fill="#000" opacity=".45" filter="url(#b10)"/>')
    for x in (60, 190, 330, 450):
        b += f'<rect x="{x}" y="50" width="22" height="280" fill="#000" opacity=".16" filter="url(#b5)"/>'
    return d, b


# ============================================================ SUELOS
def suelo_hd(id, desc, tex, color, op, seed, extra=lambda r: ""):
    @asset(id, "suelos", 1200, 160, desc, "suelo,textura,base")
    def _():
        r = random.Random(seed)
        d = LUZ_DEFS + BLUR + pat("pt", tex, 400) + '<linearGradient id="fd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity=".5"/><stop offset=".4" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".15"/></linearGradient>'
        b = '<rect width="1200" height="160" fill="url(#pt)"/>' + tinte(1200, 160, color, op)
        for i in range(70):
            x = r.randint(0, 1200); y = r.randint(10, 150); w = r.randint(20, 120)
            b += f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="{w*.1:.0f}" fill="#000" opacity="{r.uniform(.05,.2):.2f}" filter="url(#b5)"/>'
        b += extra(r) + '<rect width="1200" height="160" fill="url(#fd)"/>'
        return d, b


def _calle(r):
    s = ('<path d="M0 78H1200" stroke="#e5d68e" stroke-width="7" opacity=".5" stroke-dasharray="70 18 40 22 110 14"/>')
    s += "".join(f'<rect x="{x}" y="132" width="{r.randint(50,80)}" height="6" fill="#ddd" opacity="{r.uniform(.2,.4):.2f}"/>' for x in range(30, 1200, 230))
    for _ in range(5):
        x = r.randint(0, 1100); y = r.randint(20, 140)
        s += f'<path d="M{x} {y}l{r.randint(30,90)} {r.randint(-12,12)}l{r.randint(20,60)} {r.randint(-10,10)}" stroke="#05070a" stroke-width="{r.uniform(1.5,3):.1f}" fill="none" opacity=".8"/>'
    for _ in range(4):
        x = r.randint(60, 1100); y = r.randint(40, 140)
        s += f'<ellipse cx="{x}" cy="{y}" rx="{r.randint(25,60)}" ry="8" fill="#0a0d10" opacity=".45" filter="url(#b2)"/>'   # manchas de aceite
    return s


def _juntas_hd(r):
    s = ""
    for x in range(0, 1200, 150):
        s += f'<line x1="{x}" y1="0" x2="{x-34}" y2="160" stroke="#000" stroke-width="2.5" opacity=".5"/>'
    s += '<line x1="0" y1="80" x2="1200" y2="80" stroke="#000" stroke-width="2.5" opacity=".4"/>'
    return s


suelo_hd("suelo_asfalto", "Asfalto fotografico con lineas gastadas, grietas y aceite", "asfalto", "#4a525a", .5, 31, _calle)
suelo_hd("suelo_vereda", "Vereda de adoquines/concreto con juntas", "vereda", "#8a8c88", .35, 32, _juntas_hd)
suelo_hd("suelo_tierra", "Tierra y grava reales", "tierra", "#8a7456", .4, 33)
suelo_hd("suelo_pasto", "Pasto de parque con parches de tierra", "pasto", "#6f8a58", .35, 34)
suelo_hd("suelo_interior", "Piso de madera lustrada", "madera", "#9a7a56", .35, 35, _juntas_hd)
suelo_hd("suelo_arena", "Arena costera (Vice City)", "concreto", "#e8d6a0", .75, 36)
suelo_hd("suelo_baldosa_damero", "Piso damero de salon", "baldosa_damero", "#c9c2b4", .25, 37)


# ============================================================ OBJETOS
@asset("caja_madera_g", "interior", 200, 190, "Caja de madera grande con vetas, clavos y desgaste", "caja,madera,almacen")
def _():
    d = LUZ_DEFS + BLUR + pat("pt", "madera", 220) + lin("ed", "#2b2418", "#4a3e2a")
    b = sombra_suelo(100, 186, 96, 8, .5) + '<rect x="6" y="6" width="188" height="178" fill="url(#pt)"/>' + tinte(200, 190, "#a89870", .45)
    b += ('<rect x="6" y="6" width="188" height="178" fill="none" stroke="#2b2418" stroke-width="9"/>'
          '<rect x="6" y="6" width="188" height="178" fill="none" stroke="#000" stroke-width="2" opacity=".5"/>'
          '<path d="M10 10L190 180M190 10L10 180" stroke="#2b2418" stroke-width="9"/><path d="M10 10L190 180" stroke="#caa86a" stroke-width="1.5" opacity=".35"/>')
    for x, y in ((14, 14), (186, 14), (14, 178), (186, 178), (100, 96)):
        b += f'<circle cx="{x}" cy="{y}" r="2.6" fill="#8a8a85"/>'
    b += luz_rect(200, 190) + '<rect x="150" y="6" width="44" height="178" fill="#000" opacity=".3" filter="url(#b5)"/>'
    return d, b


@asset("caja_madera_p", "interior", 110, 100, "Caja de madera chica", "caja,madera,almacen")
def _():
    d = LUZ_DEFS + BLUR + pat("pt", "madera", 140)
    b = sombra_suelo(55, 97, 52, 5, .5) + '<rect x="4" y="4" width="102" height="92" fill="url(#pt)"/>' + tinte(110, 100, "#a89870", .45)
    b += '<rect x="4" y="4" width="102" height="92" fill="none" stroke="#2b2418" stroke-width="6"/><path d="M6 6L104 94" stroke="#2b2418" stroke-width="6"/>' + luz_rect(110, 100) + '<rect x="82" y="4" width="24" height="92" fill="#000" opacity=".3" filter="url(#b5)"/>'
    return d, b


@asset("contenedor_basura", "interior", 280, 160, "Contenedor metalico de callejon, oxidado y abollado", "contenedor,basura,callejon")
def _():
    d = LUZ_DEFS + BLUR + pat("pt", "metal_oxidado", 260) + pat("pc", "chapa_pintada", 260)
    b = sombra_suelo(140, 158, 135, 9, .5)
    b += '<path d="M10 40H270L256 156H24z" fill="url(#pc)"/>' + '<path d="M10 40H270L256 156H24z" fill="#3f6a58" opacity=".7" style="mix-blend-mode:multiply"/>'
    b += '<path d="M10 120H270L256 156H24z" fill="url(#pt)" opacity=".55"/>'   # oxido en la base
    b += '<path d="M4 34H276V50H4z" fill="#2b4238"/><path d="M4 34H276" stroke="#b5d0c3" stroke-width="2" opacity=".5"/>'
    for x in (70, 140, 210):
        b += f'<rect x="{x}" y="58" width="7" height="90" fill="#000" opacity=".28" filter="url(#b2)"/><rect x="{x+4}" y="58" width="2" height="90" fill="#fff" opacity=".12"/>'
    b += '<path d="M30 70Q70 82 110 68" stroke="#cfe3d9" stroke-width="3" opacity=".22" fill="none" filter="url(#b2)"/>'
    b += '<rect x="196" y="40" width="74" height="116" fill="#000" opacity=".3" filter="url(#b5)"/>' + luz_rect(280, 160)
    b += '<path d="M10 40H270" stroke="#fff" stroke-width="1.5" opacity=".4"/>'
    return d, b


@asset("alfombra_enrollada", "basura", 170, 60, "Alfombra roja enrollada con trama de tela", "alfombra,objeto,rojo", rol="sujeto")
def _():
    d = LUZ_DEFS + BLUR + pat("pt", "tela", 120) + lin("g", "#d0554a", "#6a1612", 0, 0, 0, 1)
    b = sombra_suelo(85, 56, 80, 5, .5) + '<rect x="12" y="10" width="146" height="40" rx="20" fill="url(#pt)"/>' + tinte(170, 60, "#c0392e", .85)
    for x in range(34, 150, 20):
        b += f'<path d="M{x} 12Q{x+8} 30 {x} 48" stroke="#e8c38a" stroke-width="3" fill="none" opacity=".6"/>'
    b += '<rect x="12" y="10" width="146" height="40" rx="20" fill="url(#g)" opacity=".35" style="mix-blend-mode:multiply"/><ellipse cx="18" cy="30" rx="12" ry="20" fill="#e0b37a"/><ellipse cx="18" cy="30" rx="6" ry="11" fill="#7a1f19"/>'
    b += '<rect x="14" y="12" width="140" height="8" rx="4" fill="#fff" opacity=".18"/>'
    return d, b


@asset("sofa_cuero", "interior", 300, 130, "Sofa de cuero con costuras", "sofa,mueble,interior")
def _():
    d = LUZ_DEFS + BLUR + pat("pt", "cuero", 200)
    b = sombra_suelo(150, 126, 142, 8, .5) + '<rect x="14" y="30" width="272" height="64" rx="16" fill="url(#pt)"/><rect x="0" y="52" width="40" height="66" rx="14" fill="url(#pt)"/><rect x="260" y="52" width="40" height="66" rx="14" fill="url(#pt)"/><rect x="30" y="78" width="240" height="38" rx="10" fill="url(#pt)"/>'
    b += tinte(300, 130, "#9a5a34", .75) + luz_rect(300, 130)
    b += '<path d="M40 82H260" stroke="#e0b088" stroke-width="2" opacity=".45"/><path d="M40 84H260" stroke="#000" stroke-width="1.5" opacity=".4" stroke-dasharray="4 3"/>'
    b += '<path d="M30 40Q150 22 270 40" stroke="#fff" stroke-width="3" opacity=".25" fill="none" filter="url(#b2)"/>'
    return d, b


@asset("hidrante", "exterior", 60, 90, "Hidrante rojo con pintura descascarada", "hidrante,calle,objeto")
def _():
    d = LUZ_DEFS + BLUR + pat("pt", "metal_oxidado", 90) + lin("g", "#ff6a5a", "#7a1e18", 0, 0, 1, 0)
    sh = '<rect x="18" y="30" width="24" height="56" rx="4"/><path d="M16 32Q30 6 44 32z"/><rect x="8" y="46" width="44" height="12" rx="4"/>'
    b = sombra_suelo(30, 87, 24, 4, .5) + '<g fill="url(#pt)">' + sh + '</g><g fill="url(#g)" opacity=".85" style="mix-blend-mode:multiply">' + sh + '</g>'
    b += '<path d="M24 36V84" stroke="#fff" stroke-width="3" opacity=".3"/><rect x="14" y="80" width="32" height="8" fill="#2b1411"/><circle cx="30" cy="28" r="3" fill="#c9a24a"/><rect x="34" y="30" width="8" height="56" fill="#000" opacity=".3"/>'
    return d, b


@asset("poste_luz", "exterior", 80, 340, "Poste de alumbrado de acero", "poste,luz,calle")
def _():
    d = LUZ_DEFS + BLUR + lin("g", "#6a767a", "#1b2124", 0, 0, 1, 0) + '<radialGradient id="lm"><stop offset="0" stop-color="#fff2b8" stop-opacity=".9"/><stop offset="1" stop-color="#fff2b8" stop-opacity="0"/></radialGradient>'
    b = (sombra_suelo(40, 336, 30, 5, .5) + '<rect x="34" y="34" width="10" height="302" fill="url(#g)"/><path d="M39 44Q39 8 72 12" stroke="#2c3436" stroke-width="8" fill="none"/>'
         '<rect x="56" y="10" width="26" height="11" rx="4" fill="#2c3436"/><rect x="62" y="20" width="16" height="4" fill="#fff2b8"/><circle cx="70" cy="30" r="26" fill="url(#lm)" style="mix-blend-mode:screen"/>'
         '<rect x="28" y="318" width="22" height="18" fill="#1e2527"/><rect x="38" y="40" width="2" height="290" fill="#fff" opacity=".25"/>')
    return d, b


# ============================================================ VEGETACION
def arbol_hd(seed, tint, w=300, h=380, grupos=11):
    r = random.Random(seed)
    d = LUZ_DEFS + BLUR + pat("hj", "hojas", 200) + pat("bk", "madera", 120) + '<radialGradient id="sh" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#fff" stop-opacity=".35"/><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".6"/></radialGradient>'
    b = sombra_suelo(w / 2, h - 3, w * .3, 9, .45)
    b += (f'<path d="M{w/2-16} {h-4}Q{w/2-9} {h*.62} {w/2-5} {h*.42}H{w/2+9}Q{w/2+12} {h*.62} {w/2+20} {h-4}z" fill="url(#bk)"/>'
          f'<path d="M{w/2-16} {h-4}Q{w/2-9} {h*.62} {w/2-5} {h*.42}H{w/2+9}Q{w/2+12} {h*.62} {w/2+20} {h-4}z" fill="#3b2a1e" opacity=".6" style="mix-blend-mode:multiply"/>'
          f'<path d="M{w/2+6} {h-4}Q{w/2+8} {h*.62} {w/2+9} {h*.42}H{w/2+20}Q{w/2+16} {h*.7} {w/2+24} {h-4}z" fill="#000" opacity=".45"/>'
          f'<path d="M{w/2} {h*.5}L{w*.3} {h*.34}M{w/2} {h*.5}L{w*.7} {h*.3}M{w/2} {h*.46}L{w/2} {h*.2}" stroke="#2b2018" stroke-width="7" stroke-linecap="round"/>')
    cs = []
    for i in range(grupos):
        cs.append((w / 2 + r.uniform(-w * .3, w * .3), h * .36 + r.uniform(-h * .2, h * .12), r.uniform(w * .14, w * .24)))
    cs.sort(key=lambda c: c[1])
    for k, (cx, cy, rr) in enumerate(cs):
        prof = .55 + .45 * k / len(cs)
        b += (f'<g><ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rr:.0f}" ry="{rr*.85:.0f}" fill="url(#hj)"/>'
              f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rr:.0f}" ry="{rr*.85:.0f}" fill="{tint}" opacity="{prof:.2f}" style="mix-blend-mode:multiply"/>'
              f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rr:.0f}" ry="{rr*.85:.0f}" fill="url(#sh)"/></g>')
        for _ in range(int(rr * .5)):
            a = r.uniform(0, 6.28); d2 = r.uniform(0, rr * .95)
            lx = cx + math.cos(a) * d2; ly = cy + math.sin(a) * d2 * .85
            b += f'<ellipse cx="{lx:.0f}" cy="{ly:.0f}" rx="{r.uniform(2,5):.1f}" ry="{r.uniform(1.2,3):.1f}" transform="rotate({r.randint(0,180)} {lx:.0f} {ly:.0f})" fill="{r.choice(["#e8f2b0","#ffffff","#0a1a0a","#0a1a0a"])}" opacity="{r.uniform(.12,.3):.2f}"/>'
    return d, b


@asset("arbol_verde", "naturaleza", 300, 380, "Arbol frondoso con follaje fotografico pintado", "arbol,parque,verde")
def _(): return arbol_hd(21, "#7a9a5a")


@asset("arbol_otonal", "naturaleza", 300, 380, "Arbol otonal ocre", "arbol,otono,ocre")
def _(): return arbol_hd(22, "#c28a3a")


@asset("arbusto", "naturaleza", 160, 90, "Arbusto con hojas texturadas", "arbusto,vegetacion,suelo")
def _():
    r = random.Random(27)
    d = LUZ_DEFS + pat("hj", "hojas", 120) + '<radialGradient id="sh" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#fff" stop-opacity=".3"/><stop offset="1" stop-color="#000" stop-opacity=".6"/></radialGradient>'
    b = sombra_suelo(80, 86, 74, 6, .5)
    for cx, cy, rr in ((40, 56, 32), (80, 44, 38), (120, 58, 30), (60, 62, 28), (100, 64, 26)):
        b += f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="url(#hj)"/><circle cx="{cx}" cy="{cy}" r="{rr}" fill="#5f8a4a" opacity=".6" style="mix-blend-mode:multiply"/><circle cx="{cx}" cy="{cy}" r="{rr}" fill="url(#sh)"/>'
    return d, b


# ============================================================ PERSONAJES HD
SK = {"claro": ("#f0c8a4", "#d49a76", "#8a5640"), "medio": ("#dcaa82", "#b07a58", "#6e4430"), "oscuro": ("#a8734e", "#7e4e32", "#472818")}


def persona_hd(id, desc, skin, hair_col, hair_style, chaq_tex, chaq_col, camisa, pant_col, barba=False, extra_cuello="", abierta=False, tags=""):
    s0, s1, s2 = SK[skin]
    hl, hd_ = hair_col

    @asset(id, "personajes", 260, 640, desc, "personaje,realista," + tags, rol="sujeto")
    def _():
        d = (LUZ_DEFS + BLUR + pat("pj", chaq_tex, 220) + pat("pp", "tela", 200) + pat("pz", "cuero", 100) +
             lin("sk", s0, s1, 0, 0, 1, 1) + lin("skv", s0, s2, 0, 0, 0, 1) + lin("hr", hl, hd_, 0, 0, 1, 1) +
             '<radialGradient id="ir"><stop offset="0" stop-color="#9ab6c0"/><stop offset=".6" stop-color="#4a6a78"/><stop offset="1" stop-color="#1c2c34"/></radialGradient>'
             f'<clipPath id="cr"><path d="M130 20C96 20 82 46 84 70C85 90 98 108 118 114L126 117L142 117C164 108 176 90 176 70C178 46 164 20 130 20Z"/></clipPath>'
             '<filter id="tb" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="1.3" numOctaves="1" seed="5"/><feColorMatrix values="0 0 0 0 .07  0 0 0 0 .05  0 0 0 0 .04  0 0 0 2.6 -1.05"/><feComposite in2="SourceGraphic" operator="in"/></filter>'
             '<linearGradient id="cs" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity=".22"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".5"/></linearGradient>')
        # ---------- piernas
        pierna = lambda x0, side: (
            f'<path d="M{x0} 330L{x0-4} 480L{x0-2} 612L{x0+54} 612L{x0+56} 480L{x0+60} 330z" fill="url(#pp)"/>'
            f'<path d="M{x0} 330L{x0-4} 480L{x0-2} 612L{x0+54} 612L{x0+56} 480L{x0+60} 330z" fill="{pant_col}" opacity=".9" style="mix-blend-mode:color"/>'
            f'<path d="M{x0} 330L{x0-4} 480L{x0-2} 612L{x0+54} 612L{x0+56} 480L{x0+60} 330z" fill="url(#cs)"/>'
            f'<path d="M{x0+8} 400Q{x0+26} 410 {x0+44} 398M{x0+4} 470Q{x0+26} 486 {x0+50} 470M{x0+6} 560Q{x0+26} 572 {x0+48} 558" stroke="#000" stroke-width="3" opacity=".3" fill="none" filter="url(#b2)"/>'
            f'<path d="M{x0+26} 340L{x0+24} 610" stroke="#fff" stroke-width="2" opacity=".07"/>'
            f'<path d="M{x0-6} 606H{x0+60}L{x0+68} 628Q{x0+30} 636 {x0-12} 630z" fill="url(#pz)"/><path d="M{x0-6} 606H{x0+60}L{x0+68} 628Q{x0+30} 636 {x0-12} 630z" fill="#16120f" opacity=".9" style="mix-blend-mode:multiply"/>'
            f'<path d="M{x0-10} 626Q{x0+30} 640 {x0+68} 626" stroke="#000" stroke-width="5" fill="none"/><path d="M{x0} 610Q{x0+26} 606 {x0+52} 610" stroke="#fff" stroke-width="2" opacity=".25" fill="none"/>')
        b = sombra_suelo(130, 632, 96, 9, .55)
        b += '<g id="piernas">' + pierna(72, 0) + pierna(132, 1) + '</g>'
        b += f'<rect x="76" y="318" width="110" height="26" fill="{pant_col}" opacity=".9"/><rect x="76" y="318" width="110" height="26" fill="url(#pz)" opacity=".5" style="mix-blend-mode:overlay"/><rect x="122" y="322" width="18" height="12" fill="#c9a24a" opacity=".8"/>'
        # ---------- torso
        tor = "M46 152C50 132 80 124 106 120L154 120C180 124 210 132 214 152L228 336L32 336Z"
        b += '<g id="torso">'
        b += f'<path d="M104 112H156V140L130 156L104 140z" fill="url(#skv)"/>'   # cuello/pecho
        if camisa:
            b += f'<path d="M104 118L130 190L156 118L156 140L130 200L104 140z" fill="{camisa}"/><path d="M104 118L130 190L156 118" stroke="#000" stroke-width="2" opacity=".3" fill="none"/>'
        b += f'<path d="{tor}" fill="url(#pj)"/><path d="{tor}" fill="{chaq_col}" opacity=".9" style="mix-blend-mode:color"/>'
        b += f'<path d="{tor}" fill="url(#cs)"/>'
        if abierta:   # camisa abierta con pecho visible
            b += f'<path d="M108 120L130 214L152 120L142 122L130 180L118 122z" fill="url(#skv)"/><path d="M120 126L130 150L140 126" stroke="#000" stroke-width="1.5" opacity=".25" fill="none"/>'
        else:
            b += '<path d="M130 156V336" stroke="#0a0c0d" stroke-width="3.5"/>' + "".join(f'<line x1="127" y1="{y}" x2="133" y2="{y}" stroke="#9a9a92" stroke-width="2"/>' for y in range(166, 334, 9))
        for p in ("M70 200Q96 236 82 292", "M190 200Q168 244 178 296", "M96 300Q130 312 164 300", "M88 168Q104 188 100 214", "M172 168Q158 190 162 214"):
            b += f'<path d="{p}" stroke="#000" stroke-width="5" opacity=".28" fill="none" filter="url(#b2)"/><path d="{p}" stroke="#fff" stroke-width="1.5" opacity=".12" fill="none" transform="translate(2,-2)"/>'
        b += ('<path d="M104 120L84 150L112 170L130 146z" fill="#000" opacity=".25"/><path d="M156 120L176 150L148 170L130 146z" fill="#000" opacity=".4"/>'
              '<path d="M104 120L84 150" stroke="#fff" stroke-width="2" opacity=".3"/>' + extra_cuello)
        b += '<rect x="154" y="130" width="74" height="206" fill="#000" opacity=".22" filter="url(#b10)" clip-path="none"/>'
        b += '</g>'
        # ---------- brazos (anidados: brazo > antebrazo + mano)
        mano = lambda x, y: (
            f'<g transform="translate({x},{y})"><path d="M-14 0Q-18 18 -14 34Q0 44 14 34Q18 18 14 0z" fill="url(#sk)"/>'
            f'<path d="M-14 4Q-18 18 -14 34Q-8 38 -4 36Q-8 20 -6 6z" fill="#000" opacity=".12"/><path d="M8 4Q14 20 10 34Q14 34 14 34Q18 18 14 0z" fill="#000" opacity=".25"/>'
            + "".join(f'<path d="M{fx} 30Q{fx+1} 44 {fx+2} {fl}" stroke="url(#sk)" stroke-width="6" stroke-linecap="round" fill="none"/><path d="M{fx+2} 32Q{fx+3} 44 {fx+3} {fl-2}" stroke="#000" stroke-width="1.5" opacity=".25" fill="none"/>' for fx, fl in ((-10, 56), (-3, 60), (4, 58), (11, 52))) +
            '<path d="M-14 12Q-24 26 -18 40" stroke="url(#sk)" stroke-width="7" stroke-linecap="round" fill="none"/></g>')
        manga = lambda p: (f'<path d="{p}" fill="url(#pj)"/><path d="{p}" fill="{chaq_col}" opacity=".9" style="mix-blend-mode:color"/><path d="{p}" fill="url(#cs)"/>')
        brazo_i = ('<g id="brazo_i">' + manga("M50 150C34 160 26 190 24 230L22 262L58 270L66 232C72 200 74 172 70 150z") +
                   '<path d="M34 190Q46 200 44 240" stroke="#000" stroke-width="4" opacity=".25" fill="none" filter="url(#b2)"/>'
                   '<g id="antebrazo_i">' + manga("M22 258L58 266L56 346L24 340z") +
                   f'<rect x="21" y="330" width="37" height="14" fill="#14181a" opacity=".85"/><path d="M30 290Q40 300 36 326" stroke="#000" stroke-width="4" opacity=".25" fill="none" filter="url(#b2)"/>'
                   + mano(40, 342) + '</g></g>')
        brazo_d = ('<g id="brazo_d">' + manga("M210 150C226 160 234 190 236 230L238 262L202 270L194 232C188 200 186 172 190 150z") +
                   '<g id="antebrazo_d">' + manga("M238 258L202 266L204 346L236 340z") +
                   '<rect x="203" y="330" width="37" height="14" fill="#14181a" opacity=".85"/>' + mano(220, 342) +
                   '<path d="M202 258L204 346" stroke="#000" stroke-width="12" opacity=".25" filter="url(#b5)"/></g></g>')
        b += brazo_i + brazo_d
        # ---------- cabeza
        cab = '<g id="cabeza">'
        cab += f'<path d="M110 100H150L156 138Q130 152 104 138z" fill="url(#skv)"/><path d="M104 118Q130 140 156 118L156 140Q130 156 104 140z" fill="#000" opacity=".3" filter="url(#b5)"/>'
        for ex, sx in ((81, -1), (179, 1)):
            cab += f'<ellipse cx="{ex}" cy="74" rx="7" ry="13" fill="url(#sk)"/><ellipse cx="{ex+sx*1}" cy="74" rx="3" ry="8" fill="#000" opacity=".25"/>'
        cab += '<path d="M130 20C96 20 82 46 84 70C85 90 98 108 118 114L126 117L142 117C164 108 176 90 176 70C178 46 164 20 130 20Z" fill="url(#sk)"/>'
        cab += '<g clip-path="url(#cr)">'
        cab += '<path d="M176 30L182 120L140 124L158 74Z" fill="' + s2 + '" opacity=".55" filter="url(#b5)"/>'
        for cx, cy, rx, ry, op in ((108, 68, 17, 9, .4), (152, 68, 17, 9, .5), (130, 95, 11, 3.5, .5), (130, 109, 11, 4, .35), (92, 96, 10, 14, .18)):
            cab += f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{s2}" opacity="{op}" filter="url(#b2)"/>'
        cab += f'<path d="M127 62Q121 80 117 93Q128 98 135 93Q133 80 133 62z" fill="{s2}" opacity=".3" filter="url(#b2)"/>'
        for cx, cy, rx, ry, op in ((112, 40, 22, 11, .22), (106, 88, 11, 6, .22), (128, 88, 3, 8, .22), (150, 88, 10, 6, .12)):
            cab += f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#fff" opacity="{op}" filter="url(#b2)"/>'
        if barba:
            cab += '<path d="M86 84Q96 112 126 118Q156 112 174 84L174 118L86 118z" fill="#000" filter="url(#tb)" opacity=".85"/><path d="M104 98Q130 104 156 98Q148 112 130 112Q112 112 104 98z" fill="#000" filter="url(#tb)" opacity=".5"/>'
        cab += '</g>'
        # ojos (grupo animable)
        cab += '<g id="ojos">'
        for ex in (108, 152):
            cab += (f'<path d="M{ex-13} 70Q{ex} 59 {ex+13} 70Q{ex} 77 {ex-13} 70Z" fill="#e9e3da"/><path d="M{ex-13} 70Q{ex} 59 {ex+13} 70Q{ex} 62 {ex-13} 70Z" fill="#000" opacity=".25"/>'
                    f'<g class="iris"><circle cx="{ex}" cy="69" r="5.6" fill="url(#ir)"/><circle cx="{ex}" cy="69" r="2.4" fill="#06090a"/><circle cx="{ex-1.8}" cy="67" r="1.5" fill="#fff" opacity=".9"/></g>'
                    f'<path d="M{ex-14} 70Q{ex} 58 {ex+14} 70" stroke="#2a1812" stroke-width="2.6" fill="none" stroke-linecap="round"/><path d="M{ex-12} 71Q{ex} 78 {ex+12} 71" stroke="#6a3a2a" stroke-width="1" opacity=".5" fill="none"/>')
        cab += '</g>'
        cab += (f'<g id="cejas"><path d="M91 58Q106 47 123 55Q107 53 92 62Z" fill="{hd_}"/><path d="M169 58Q154 47 137 55Q153 53 168 62Z" fill="{hd_}"/></g>'
                '<path d="M126 70Q121 84 118 92" stroke="#6a3a2a" stroke-width="1.6" opacity=".4" fill="none"/>'
                '<ellipse cx="122" cy="95" rx="3.6" ry="2.2" fill="#2a1410" opacity=".6"/><ellipse cx="138" cy="95" rx="3.6" ry="2.2" fill="#2a1410" opacity=".6"/><ellipse cx="130" cy="91" rx="4.5" ry="2.6" fill="#fff" opacity=".2"/>'
                '<path d="M118 90Q114 96 120 98M142 90Q146 96 140 98" stroke="#5a2f22" stroke-width="1.4" fill="none" opacity=".5"/>')
        cab += ('<g id="boca"><path d="M113 106Q121 102 130 104Q139 102 147 106Q139 109 130 109Q121 109 113 106Z" fill="#8f4f48"/>'
                '<path d="M115 107Q130 120 145 107Q130 113 115 107Z" fill="#aa6358"/><path d="M113 106Q130 111 147 106" stroke="#2a110e" stroke-width="1.7" fill="none"/>'
                '<path d="M120 114Q130 117 140 114" stroke="#fff" stroke-width="1.5" opacity=".18" fill="none"/></g>')
        # pelo
        if hair_style == "atras":
            cab += (f'<path d="M80 74C74 30 98 8 132 10C166 10 186 32 178 74C176 52 162 36 132 33C104 33 88 52 80 74Z" fill="url(#hr)"/>')
            r = random.Random(3)
            for i in range(26):
                x0 = 92 + i * 3; cab += f'<path d="M{x0} {42+r.randint(-3,4)}Q{x0+r.randint(-4,12)} {18+r.randint(-4,4)} {x0+18+r.randint(-4,10)} {r.randint(14,24)}" stroke="{r.choice([hl, hd_, "#000"])}" stroke-width="{r.uniform(.8,1.8):.1f}" opacity="{r.uniform(.3,.7):.2f}" fill="none"/>'
            cab += '<path d="M102 26Q128 12 156 24" stroke="#fff" stroke-width="3.5" opacity=".18" fill="none" filter="url(#b2)"/><path d="M80 74Q78 54 90 48Q86 62 88 76z" fill="url(#hr)"/><path d="M178 74Q180 54 168 48Q172 62 170 76z" fill="url(#hr)"/>'
        elif hair_style == "corto":
            cab += '<path d="M82 66C78 26 104 12 132 14C160 14 184 28 176 66C168 44 154 38 132 38C108 38 90 46 82 66Z" fill="url(#hr)"/>'
            r = random.Random(4)
            for i in range(30):
                x0 = 88 + i * 3; cab += f'<line x1="{x0}" y1="{44+r.randint(-4,2)}" x2="{x0+r.randint(-3,5)}" y2="{20+r.randint(-3,6)}" stroke="{r.choice([hl, hd_, "#000"])}" stroke-width="1.1" opacity="{r.uniform(.3,.6):.2f}"/>'
            cab += '<path d="M104 30Q128 18 152 30" stroke="#fff" stroke-width="3" opacity=".14" fill="none" filter="url(#b2)"/>'
        else:   # calvo / rapado
            cab += '<path d="M84 62C82 30 104 18 132 18C160 18 180 30 176 62C170 40 152 32 132 32C108 32 90 42 84 62Z" fill="#000" filter="url(#tb)" opacity=".55"/>'
        cab += '</g>'
        b += cab
        return d, b


persona_hd("npc_campera_marron", "Hombre con campera de cuero marron y guantes sin dedos (realista)", "claro", ("#6a4a34", "#26170f"), "corto", "cuero", "#8a5a38", "#6a7a58", "#2a3544", barba=True, tags="npc,calle,marron")
persona_hd("npc_traje_oscuro", "Hombre de traje oscuro, camisa blanca y corbata", "medio", ("#3a2e28", "#0f0b09"), "atras", "tela", "#2a3a44", "#e8e6df", "#242c32", barba=False, tags="npc,traje,formal",
           extra_cuello='<path d="M124 124L130 200L136 124L130 130z" fill="#7a2a2a"/><path d="M126 130L130 196L134 130" stroke="#000" stroke-width="1" opacity=".3" fill="none"/>')
persona_hd("npc_chandal_azul", "Hombre con chandal azul de rayas, cabeza rapada", "claro", ("#3a3028", "#120e0b"), "calvo", "tela", "#2d4f6a", "#cfd4d6", "#232b33", barba=True, tags="npc,chandal,calle",
           extra_cuello='<path d="M50 160L40 330M56 158L46 330" stroke="#e8eef0" stroke-width="3" opacity=".8"/><path d="M210 160L220 330M204 158L214 330" stroke="#e8eef0" stroke-width="3" opacity=".8"/>')
persona_hd("anfitrion_extra", "Anfitrion de Extra: peinado hacia atras, camisa abierta turquesa ochentera, cadena de oro", "medio", ("#3c2a20", "#120c08"), "atras", "tela", "#27c9b8", "", "#e4dcc8", barba=True, abierta=True, tags="anfitrion,vice,protagonista",
           extra_cuello='<path d="M112 126Q130 176 148 126" stroke="#f1cf63" stroke-width="3" fill="none"/><circle cx="130" cy="172" r="7" fill="#f1cf63"/><circle cx="130" cy="172" r="3.5" fill="none" stroke="#8a6a1c" stroke-width="1.2"/>')
