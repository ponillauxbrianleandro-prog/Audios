"""v2 (parte 2): mascota HD (pistola 10mm con materiales reales) y assets nuevos de mundo."""
import random, math
from generar_assets import asset, lin, sombra_suelo
from assets_hd import LUZ_DEFS, BLUR, pat, tinte, luz_rect


# ============================================================ MASCOTA HD
@asset("mascota_pistola_10mm", "mascota", 420, 300,
       "Mascota HD: pistola 10mm de Fallout 3 (acero cepillado, madera, ojos realistas; rig: cuerpo, martillo, ojos, boca, brazos, piernas)",
       "mascota,pistola,fallout,10mm", rol="sujeto")
def _():
    d = (LUZ_DEFS + BLUR + pat("wd", "madera", 160) + pat("mt", "metal_oxidado", 200) +
         '<linearGradient id="st" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#eef3f5"/><stop offset=".08" stop-color="#b8c4c9"/><stop offset=".35" stop-color="#6d7b82"/>'
         '<stop offset=".62" stop-color="#3a464c"/><stop offset=".85" stop-color="#1f282c"/><stop offset="1" stop-color="#2e383d"/></linearGradient>'
         '<linearGradient id="br" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#cfd8db"/><stop offset=".5" stop-color="#4d5a61"/><stop offset="1" stop-color="#171d20"/></linearGradient>'
         '<radialGradient id="ir"><stop offset="0" stop-color="#b9d4dc"/><stop offset=".55" stop-color="#4b7584"/><stop offset="1" stop-color="#1a2e36"/></radialGradient>'
         '<radialGradient id="gl" cx=".4" cy=".35"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#cfd3d4"/></radialGradient>'
         '<filter id="ray" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".02 .8" numOctaves="2" seed="9"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .5 -.18"/><feComposite in2="SourceGraphic" operator="in"/></filter>')
    corr = "M40 46H350Q372 46 374 68L370 118H60Q40 118 40 96Z"
    b = sombra_suelo(210, 292, 150, 9, .5)
    b += '<g id="cuerpo">'
    # empunadura de madera con textura real
    emp = "M96 120L150 120L134 270Q120 286 92 276L70 266Z"
    b += f'<path d="{emp}" fill="url(#wd)"/><path d="{emp}" fill="#8a5028" opacity=".85" style="mix-blend-mode:multiply"/><path d="{emp}" fill="url(#lzS)"/>'
    b += '<path d="M104 134L116 262M124 134L134 258" stroke="#1d0f05" stroke-width="2" opacity=".5"/><circle cx="118" cy="180" r="4.5" fill="#b9c2c6" stroke="#222" stroke-width="1.2"/><path d="M150 120L134 270" stroke="#000" stroke-width="12" opacity=".35" filter="url(#b2)"/>'
    # guardamonte + gatillo
    b += '<path d="M150 120Q150 170 202 170Q232 170 234 120" stroke="url(#br)" stroke-width="10" fill="none"/><path d="M198 122L208 154L216 122z" fill="#11161a"/>'
    # corredera de acero
    b += f'<path d="{corr}" fill="url(#st)"/><path d="{corr}" fill="url(#mt)" opacity=".22" style="mix-blend-mode:overlay"/><path d="{corr}" fill="url(#ray)" opacity=".55"/>'
    b += '<rect x="42" y="47" width="330" height="5" fill="#fff" opacity=".7"/><rect x="60" y="102" width="300" height="16" fill="#000" opacity=".3" filter="url(#b2)"/>'
    b += '<g stroke="#10161a" stroke-width="5" opacity=".9">' + "".join(f'<line x1="{x}" y1="52" x2="{x+8}" y2="96"/>' for x in range(66, 140, 14)) + '</g>'
    b += '<g stroke="#fff" stroke-width="1.2" opacity=".3">' + "".join(f'<line x1="{x+4}" y1="52" x2="{x+12}" y2="96"/>' for x in range(66, 140, 14)) + '</g>'
    b += '<rect x="262" y="58" width="68" height="14" rx="3" fill="#10161a" opacity=".85"/><path d="M270 64H322" stroke="#8a969b" stroke-width="2" opacity=".6"/>'   # puerto de eyeccion
    b += '<text x="258" y="96" font-family="Arial Black,Arial" font-size="17" fill="#0f1417" opacity=".8">10mm</text><text x="258" y="96" font-family="Arial Black,Arial" font-size="17" fill="#fff" opacity=".2" transform="translate(1,1)">10mm</text>'
    # canon, mira
    b += '<rect x="350" y="62" width="62" height="40" rx="6" fill="url(#br)"/><rect x="350" y="62" width="62" height="6" fill="#fff" opacity=".55"/><circle cx="408" cy="82" r="11" fill="#06090a"/><circle cx="408" cy="82" r="11" fill="none" stroke="#9aa6ab" stroke-width="2"/>'
    b += '<path d="M360 46L366 36H382L388 46z" fill="#161c20"/>'
    # rayones y desgaste
    b += '<g stroke="#e8f0f2" stroke-width=".9" opacity=".45"><path d="M90 90L130 84M200 60L246 66M300 98L346 92M70 70L96 76"/></g>'
    b += '<ellipse cx="200" cy="100" rx="150" ry="14" fill="#fff" opacity=".07" filter="url(#b5)"/>'
    b += '</g>'
    b += '<g id="martillo"><path d="M30 46Q10 30 20 18L46 28L54 50z" fill="url(#br)"/><path d="M22 22L44 30" stroke="#fff" stroke-width="2" opacity=".5"/></g>'
    # cara realista: ojos con iris, brillo y parpados; cejas
    b += '<g id="ojos">'
    for ex in (152, 200):
        b += (f'<ellipse cx="{ex}" cy="80" rx="17" ry="16" fill="url(#gl)"/><ellipse cx="{ex}" cy="86" rx="15" ry="9" fill="#000" opacity=".12" filter="url(#b2)"/>'
              f'<g class="iris"><circle cx="{ex+3}" cy="82" r="9.5" fill="url(#ir)"/><circle cx="{ex+3}" cy="82" r="4" fill="#05080a"/><circle cx="{ex}" cy="78" r="3" fill="#fff" opacity=".95"/><circle cx="{ex+7}" cy="86" r="1.4" fill="#fff" opacity=".7"/></g>'
              f'<path d="M{ex-17} 78Q{ex} 62 {ex+17} 78" stroke="#10161a" stroke-width="3.5" fill="none"/><ellipse cx="{ex}" cy="80" rx="17" ry="16" fill="none" stroke="#000" stroke-width="1" opacity=".5"/>')
    b += '</g>'
    b += '<g id="cejas"><path d="M130 58Q150 44 172 56" stroke="#10161a" stroke-width="6" stroke-linecap="round" fill="none"/><path d="M180 56Q200 44 224 58" stroke="#10161a" stroke-width="6" stroke-linecap="round" fill="none"/></g>'
    b += '<g id="boca"><path d="M158 106Q176 124 194 106Q176 114 158 106Z" fill="#2a0c0c"/><path d="M158 106Q176 112 194 106" stroke="#05080a" stroke-width="3" fill="none" stroke-linecap="round"/><rect x="166" y="106" width="20" height="4" fill="#e8e4d8" opacity=".9"/></g>'
    # extremidades con guantes y goma
    gl = lambda x, y: f'<circle cx="{x}" cy="{y}" r="13" fill="url(#gl)"/><circle cx="{x+4}" cy="{y+5}" r="12" fill="#000" opacity=".15" filter="url(#b2)"/><path d="M{x-8} {y-4}Q{x} {y-9} {x+8} {y-4}" stroke="#fff" stroke-width="2" opacity=".6" fill="none"/>'
    b += ('<g id="brazo_i"><path d="M96 150Q60 170 58 200" stroke="url(#br)" stroke-width="11" fill="none" stroke-linecap="round"/>' + gl(58, 206) + '</g>'
          '<g id="brazo_d"><path d="M150 164Q196 192 214 172" stroke="url(#br)" stroke-width="11" fill="none" stroke-linecap="round"/>' + gl(216, 170) + '</g>'
          '<g id="pierna_i"><path d="M100 270L96 292" stroke="#1a2024" stroke-width="11" stroke-linecap="round"/><ellipse cx="92" cy="296" rx="17" ry="7" fill="#0f1417"/><ellipse cx="90" cy="293" rx="10" ry="2.5" fill="#fff" opacity=".25"/></g>'
          '<g id="pierna_d"><path d="M126 270L130 292" stroke="#1a2024" stroke-width="11" stroke-linecap="round"/><ellipse cx="134" cy="296" rx="17" ry="7" fill="#0f1417"/><ellipse cx="132" cy="293" rx="10" ry="2.5" fill="#fff" opacity=".25"/></g>')
    return d, b


# ============================================================ NUEVOS ASSETS (v2)
@asset("puerta_metalica", "exterior", 150, 260, "Puerta metalica de servicio con pintura descascarada", "puerta,metal,callejon")
def _():
    d = LUZ_DEFS + BLUR + pat("pt", "chapa_pintada", 260) + pat("ox", "metal_oxidado", 200)
    b = '<rect width="150" height="260" fill="#2b2f31"/><rect x="8" y="8" width="134" height="252" fill="url(#pt)"/>' + tinte(150, 260, "#4f6a74", .7)
    b += '<rect x="8" y="170" width="134" height="90" fill="url(#ox)" opacity=".5"/><rect x="20" y="24" width="110" height="90" fill="none" stroke="#000" stroke-width="3" opacity=".5"/><rect x="20" y="130" width="110" height="110" fill="none" stroke="#000" stroke-width="3" opacity=".5"/>'
    b += '<rect x="104" y="124" width="14" height="30" rx="4" fill="#9aa4a8"/><circle cx="111" cy="132" r="4" fill="#222"/>' + luz_rect(150, 260) + '<rect x="0" y="236" width="150" height="24" fill="#000" opacity=".4" filter="url(#b5)"/>'
    return d, b


@asset("graffiti_pared", "exterior", 240, 130, "Graffiti de aerosol sobre pared (capa para superponer)", "graffiti,pared,detalle", rol="sujeto")
def _():
    d = BLUR + '<filter id="sp"><feTurbulence baseFrequency=".9" numOctaves="1" seed="2"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 3 -1.1"/><feComposite in2="SourceGraphic" operator="in"/></filter>'
    b = ('<g filter="url(#sp)"><text x="120" y="82" text-anchor="middle" font-family="Impact,Arial Black" font-size="76" fill="#e8c23a" stroke="#1a1a1a" stroke-width="5" paint-order="stroke" transform="rotate(-6 120 70)">EXTRA</text></g>'
         '<path d="M20 112Q120 126 220 108" stroke="#d63a5a" stroke-width="5" fill="none" opacity=".8" filter="url(#b2)"/>')
    return d, b


@asset("banco_parque", "naturaleza", 220, 100, "Banco de plaza de madera y fundicion", "banco,parque,mobiliario")
def _():
    d = LUZ_DEFS + BLUR + pat("wd", "madera", 140)
    b = sombra_suelo(110, 96, 100, 6, .5)
    for y in (22, 38, 54):
        b += f'<rect x="10" y="{y}" width="200" height="12" fill="url(#wd)"/><rect x="10" y="{y}" width="200" height="12" fill="#7a5632" opacity=".7" style="mix-blend-mode:multiply"/><rect x="10" y="{y}" width="200" height="2" fill="#fff" opacity=".25"/>'
    b += '<rect x="10" y="64" width="200" height="12" fill="url(#wd)"/><rect x="10" y="64" width="200" height="12" fill="#6a4a2a" opacity=".7" style="mix-blend-mode:multiply"/>'
    for x in (24, 184):
        b += f'<path d="M{x} 12V92M{x+8} 76V92M{x-6} 76H{x+14}" stroke="#14181a" stroke-width="6" fill="none"/>'
    b += luz_rect(220, 100)
    return d, b


@asset("neumatico", "basura", 70, 70, "Neumatico viejo tirado", "neumatico,basura,goma")
def _():
    d = LUZ_DEFS + pat("gm", "goma", 100)
    return d, (sombra_suelo(35, 66, 32, 4, .5) + '<ellipse cx="35" cy="38" rx="31" ry="30" fill="url(#gm)"/><ellipse cx="35" cy="38" rx="31" ry="30" fill="#111" opacity=".7" style="mix-blend-mode:multiply"/>'
               '<ellipse cx="35" cy="38" rx="14" ry="13" fill="#0a0c0d"/><ellipse cx="35" cy="38" rx="9" ry="8" fill="#6d7478"/><path d="M12 22Q35 6 58 22" stroke="#fff" stroke-width="3" opacity=".18" fill="none"/>')


@asset("tacho_metal", "basura", 80, 110, "Tacho de metal abollado", "tacho,basura,metal")
def _():
    d = LUZ_DEFS + BLUR + pat("mt", "metal_oxidado", 120)
    b = sombra_suelo(40, 107, 38, 5, .5) + '<path d="M10 24H70L66 106H14z" fill="url(#mt)"/><path d="M10 24H70L66 106H14z" fill="#5a6a6e" opacity=".6" style="mix-blend-mode:color"/>'
    b += '<ellipse cx="40" cy="24" rx="31" ry="7" fill="#2b3234"/><ellipse cx="40" cy="22" rx="28" ry="5" fill="#0a0c0d"/>'
    for y in (46, 72):
        b += f'<path d="M12 {y}Q40 {y+6} 68 {y}" stroke="#000" stroke-width="3" opacity=".4" fill="none"/>'
    b += '<rect x="48" y="26" width="22" height="80" fill="#000" opacity=".3" filter="url(#b5)"/><rect x="18" y="26" width="3" height="78" fill="#fff" opacity=".3"/>'
    return d, b


@asset("baranda_acero", "exterior", 360, 110, "Baranda de acero con barrotes", "baranda,acero,estructura")
def _():
    d = BLUR + lin("g", "#8a969b", "#1b2124", 0, 0, 1, 0)
    b = '<rect x="0" y="8" width="360" height="8" fill="url(#g)"/><rect x="0" y="100" width="360" height="8" fill="url(#g)"/>'
    for x in range(10, 360, 22):
        b += f'<rect x="{x}" y="16" width="5" height="86" fill="url(#g)"/>'
    b += '<rect y="104" width="360" height="6" fill="#000" opacity=".4" filter="url(#b2)"/>'
    return d, b


@asset("andamio", "exterior", 220, 300, "Andamio metalico de obra", "andamio,obra,estructura")
def _():
    d = BLUR + lin("g", "#9aa5a9", "#2b3235", 0, 0, 1, 0)
    b = ""
    for x in (10, 200):
        b += f'<rect x="{x}" y="0" width="8" height="300" fill="url(#g)"/>'
    for y in (20, 110, 200, 290):
        b += f'<rect x="6" y="{y}" width="208" height="8" fill="url(#g)"/><rect x="14" y="{y+8}" width="192" height="6" fill="#000" opacity=".35" filter="url(#b2)"/>'
    for y in (20, 110, 200):
        b += f'<path d="M14 {y+8}L198 {y+98}M198 {y+8}L14 {y+98}" stroke="#5a666b" stroke-width="3"/>'
    return d, b


@asset("cielo_atardecer", "exterior", 1200, 500, "Cielo de atardecer degradado con nubes largas", "cielo,atardecer,fondo")
def _():
    d = BLUR + '<linearGradient id="c" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2c3a68"/><stop offset=".5" stop-color="#d8788a"/><stop offset="1" stop-color="#ffc58a"/></linearGradient>'
    r = random.Random(50)
    b = '<rect width="1200" height="500" fill="url(#c)"/>'
    for i in range(14):
        b += f'<ellipse cx="{r.randint(0,1200)}" cy="{r.randint(60,400)}" rx="{r.randint(120,300)}" ry="{r.randint(10,26)}" fill="#fff" opacity="{r.uniform(.08,.25):.2f}" filter="url(#b5)"/>'
    return d, b


@asset("cielo_nublado", "exterior", 1200, 500, "Cielo nublado frio estilo Liberty City", "cielo,nublado,fondo")
def _():
    d = BLUR + '<linearGradient id="c" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7f8e8e"/><stop offset="1" stop-color="#c9d3cd"/></linearGradient>'
    r = random.Random(51)
    b = '<rect width="1200" height="500" fill="url(#c)"/>'
    for i in range(18):
        b += f'<ellipse cx="{r.randint(0,1200)}" cy="{r.randint(40,380)}" rx="{r.randint(100,260)}" ry="{r.randint(20,50)}" fill="{r.choice(["#fff","#5a6666"])}" opacity="{r.uniform(.1,.3):.2f}" filter="url(#b10)"/>'
    return d, b


@asset("luz_glow", "efectos", 300, 300, "Resplandor de luz (bloom) para farolas, neones y ventanas; usar con mezcla:'screen'", "luz,bloom,glow")
def _():
    return '<radialGradient id="g"><stop offset="0" stop-color="#fff4c8" stop-opacity=".95"/><stop offset=".25" stop-color="#ffd890" stop-opacity=".45"/><stop offset="1" stop-color="#ffb060" stop-opacity="0"/></radialGradient>', '<circle cx="150" cy="150" r="150" fill="url(#g)"/>'


@asset("lluvia_capa", "efectos", 600, 600, "Capa de lluvia diagonal (animar y)", "lluvia,clima,atmosfera")
def _():
    r = random.Random(60)
    return "", "".join(f'<line x1="{x}" y1="{y}" x2="{x-6}" y2="{y+26}" stroke="#cfe0ea" stroke-width="1.2" opacity="{r.uniform(.2,.6):.2f}"/>' for x, y in ((r.randint(0, 600), r.randint(0, 580)) for _ in range(160)))
