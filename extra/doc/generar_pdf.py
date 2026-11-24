#!/usr/bin/env python3
"""Genera Extra_Guia_Visual_v3.pdf (ampliacion del documento base v1.0).  Uso: python3 generar_pdf.py"""
import os, io, json
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak, Table, TableStyle, KeepTogether

AQUI = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(AQUI, "img")
pal = json.load(open(os.path.join(AQUI, "..", "mundo", "paletas.json"), encoding="utf-8"))

INK = colors.HexColor("#1b2428"); ACC = colors.HexColor("#1f9a8c")
H1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=INK, spaceAfter=8, spaceBefore=6)
H2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=ACC, spaceBefore=10, spaceAfter=4)
P = ParagraphStyle("p", fontName="Helvetica", fontSize=9.6, leading=13.4, textColor=INK, spaceAfter=5)
B = ParagraphStyle("b", parent=P, leftIndent=12, bulletIndent=2, spaceAfter=2)
SM = ParagraphStyle("sm", parent=P, fontSize=8, leading=10.5, textColor=colors.HexColor("#586870"))
BOX = ParagraphStyle("box", parent=P, backColor=colors.HexColor("#e6f3f1"), borderColor=ACC, borderWidth=.8, borderPadding=7, spaceBefore=6, spaceAfter=10)
CAP = ParagraphStyle("cap", parent=SM, alignment=1, spaceAfter=8)


def bullets(items): return [Paragraph(t, B, bulletText="•") for t in items]


def foto(nombre, ancho=170 * mm, q=80, maxw=1500):
    im = Image.open(os.path.join(IMG, nombre)).convert("RGB")
    if im.width > maxw: im = im.resize((maxw, int(im.height * maxw / im.width)))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=q); buf.seek(0)
    return RLImage(buf, width=ancho, height=ancho * im.height / im.width)


def swatches(lista, w=24, h=12):
    t = Table([[""] * len(lista), [c for c in lista]], colWidths=[w * mm] * len(lista), rowHeights=[h * mm, 5 * mm])
    st = [("BACKGROUND", (i, 0), (i, 0), colors.HexColor(c)) for i, c in enumerate(lista)]
    st += [("FONTSIZE", (0, 1), (-1, 1), 6.5), ("ALIGN", (0, 1), (-1, 1), "CENTER"), ("BOX", (0, 0), (-1, 0), .3, colors.grey)]
    t.setStyle(TableStyle(st)); return t


def pie(c, d):
    c.saveState(); c.setFont("Helvetica", 7.5); c.setFillColor(colors.HexColor("#78888e"))
    c.drawString(18 * mm, 10 * mm, "EXTRA | Guía visual v3.0 · estilo ilustrado 2D inspirado en GTA IV"); c.drawRightString(192 * mm, 10 * mm, str(d.page)); c.restoreState()


s = []
s += [Spacer(1, 40 * mm), Paragraph("EXTRA", ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=48, leading=52, textColor=INK, alignment=1)),
      Paragraph("Guía visual v3.0 — Mundo 2D, color selectivo, intros de silueta y mascota", ParagraphStyle("t2", parent=P, fontSize=14, leading=18, alignment=1, textColor=ACC)),
      Spacer(1, 8 * mm), foto("demo_intro.png", 150 * mm),
      Paragraph("Fotograma de la animación demo (renderizada desde el mundo de assets, no 3D).", CAP), Spacer(1, 6 * mm),
      Paragraph("Este documento amplía el documento base v1.0 (Dirección artística e identidad). Mantiene todas sus reglas "
                "(2D con profundidad, ningún plano vacío, suelo con textura, identidad única con paleta cambiante) y agrega: análisis de las "
                "referencias de GTA IV recibidas, color selectivo, la técnica de silueta-dentro-de-silueta, la mascota (pistola 10 mm de Fallout 3), "
                "la regla de peso de los videos y el catálogo del mundo de assets.", P), PageBreak()]

# ---- 1
s += [Paragraph("01 · Qué enseñan las referencias de GTA IV", H1),
      Paragraph("Se analizaron nueve ilustraciones: escena del auto con la placa, portada IV con silueta, cuatro personajes con cajas en el almacén, "
                "el callejón con la alfombra, el hombre del puro en el salón, Niko bajo el puente, Bernie con anteojos, el personaje del tanque de ropa blanca y el francotirador "
                "en la azotea. Principios comunes:", P)]
s += bullets([
    "<b>Fondo descolorido, sujeto con color.</b> En los artworks de personajes (Niko, Bernie, el del puro) el escenario está casi blanco/gris y solo "
    "el personaje conserva saturación. Es la base del contraste.",
    "<b>Planos claros:</b> primer plano que enmarca (marco de ventanilla, cajas), plano medio con la acción, fondo con perspectiva y atmósfera.",
    "<b>Composición diagonal y asimétrica:</b> hombros en 3/4, miradas fuera de cuadro, armas y brazos que guían la mirada.",
    "<b>Luz con motivo:</b> luz fría lateral, sombras azul-verdosas densas, reflejos solo donde hay material que lo justifica.",
    "<b>Detalle selectivo:</b> rostro, manos y ropa tienen pliegues y volumen; el resto es mancha pictórica limpia.",
    "<b>Objetos con historia:</b> cajas, contenedor, alfombra, placa, anteojos, cadenas y armas cuentan la escena sin texto."])
s += [Paragraph("Paletas extraídas de las referencias", H2)]
for nombre, lista in pal["extraidas_de_referencias"].items():
    s += [Paragraph(nombre.replace("_", " "), SM), swatches(lista, 22 if len(lista) > 5 else 26), Spacer(1, 2 * mm)]
s += [PageBreak()]

# ---- 2
s += [Paragraph("02 · Color selectivo y descolorido de fondo", H1),
      Paragraph("Regla de contraste del canal: todo lo que esté en el fondo se descolora y el color queda concentrado en el sujeto (piel, pelo, ropa). "
                "Los objetos de fondo cuyo color sea parecido o igual al del sujeto reciben un poco de color (<i>color afín</i>) para dialogar con él y generar un contraste todavía más fuerte.", P),
      Paragraph("Fórmulas (se aplican automáticamente en el motor)", H2)]
s += bullets([
    "<b>Sujeto</b> (rol <i>sujeto</i>): saturación 100–110 %.",
    "<b>Fondo</b> (rol <i>fondo</i>): saturación 10–25 % en Liberty City frío; 40–50 % en Vice City, GTA VI y fútbol, que toleran más color.",
    "<b>Color afín:</b> un objeto marcado <i>afin</i> sube su saturación a fondo + 45 % del hueco hasta 100 %. Ej.: la alfombra roja y la campera marrón, el cartel rosa y la camisa turquesa.",
    "<b>Distancia:</b> a menor paralaje (más lejos), un poco menos de brillo y más bruma del color del cielo: perspectiva atmosférica.",
    "<b>Tinte del tema</b> con mezcla multiplicada y opacidad baja (14–20 %): integra todo sin teñir el sujeto de forma artificial."])
s += [Paragraph("Temas de color", H2)]
for k, t in pal["temas"].items():
    s += [Paragraph(f"<b>{k}</b> — {t['nombre']} · fondo sat {t['fondo_sat']} · sujeto sat {t['sujeto_sat']}", SM), swatches(t["cielo"] + t["acentos"] + [t["tinte"]], 20), Spacer(1, 2 * mm)]
s += [Paragraph("Los temas son orientativos. En fútbol, reemplazar <i>acentos</i> y <i>tinte</i> por los colores del club o la competición.", SM), PageBreak()]

# ---- 3
s += [Paragraph("03 · Silueta dentro de silueta (intros y cambios rápidos)", H1),
      Paragraph("De la portada IV: el cuerpo del personaje aparece dos veces. Primero como silueta lisa de color neutro; después el <b>mismo contorno se usa como máscara</b> y "
                "dentro de él se muestra una escena (la ciudad, el puente, el humo). Queda una figura humana hecha de ciudad, más una segunda silueta oscura en primer plano que mira hacia ella.", P),
      Paragraph("Receta de producción", H2)]
s += bullets([
    "Capa 1 – fondo plano en tono del tema. Capa 2 – silueta del cuerpo en gris claro (da la sombra/figura).",
    "Capa 3 – escena de ciudad enmascarada con el mismo SVG de la silueta (<i>mascara</i> en el JSON de la escena). La ciudad se mueve con paralaje y la cámara hace zoom lento.",
    "Capa 4 – silueta negra de pie (sin detalle) + título. La cámara entra al torso y un destello blanco corta a la escena siguiente.",
    "<b>Videos largos:</b> usar esta intro (3–5 s). <b>Shorts:</b> sin intro; empezar directo con el dato curioso y cortes rápidos de cámara."])
s += [foto("demo_intro.png", 150 * mm), Paragraph("Intro de la demo: silueta con ciudad adentro, silueta de pie y título.", CAP), PageBreak()]

# ---- 4
s += [Paragraph("04 · Regla de peso: grabar, no exportar el mundo", H1),
      Paragraph("Problema anterior: videos de 2 min que pesaban 20 GB porque se exportaba todo el mundo animado (cada árbol, basura y polvo como animación). "
                "Solución: el mundo vive aparte como assets SVG livianos + un JSON de escena; el motor lo dibuja y <b>se graba el resultado a MP4</b> (H.264). "
                "El video contiene solo píxeles.", P),
      Paragraph("Presupuesto", H2)]
tabla = Table([["Tipo", "Peso esperado", "Alerta"],
               ["Short 30–60 s", "5–25 MB", "> 60 MB"],
               ["Video largo (8–15 min)", "60–150 MB (patrón ~100 MB)", "> 250 MB"],
               ["Tope duro", "400 MB", "Rechazar y regrabar"],
               ["Demo de este mundo (14 s, 1080p30)", "4,5 MB (~19 MB/min)", "—"]], colWidths=[62 * mm, 62 * mm, 42 * mm])
tabla.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), INK), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                           ("GRID", (0, 0), (-1, -1), .3, colors.grey), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")]))
s += [tabla, Spacer(1, 4 * mm), Paragraph("Flujo", H2)]
s += bullets(["1) Elegir/crear assets en <i>mundo/assets</i> (SVG) y armar la escena JSON (editor: <i>mundo/app/index.html</i>).",
              "2) Grabar: <font face='Courier'>node mundo/herramientas/grabar.mjs escena.json salida.mp4 --audio narracion.mp3</font>. Los fotogramas pasan por un pipe a ffmpeg y no se guardan en disco.",
              "3) Verificar: <font face='Courier'>python3 mundo/herramientas/verificar_peso.py salida.mp4</font> (avisa si MB/min es anormal).",
              "4) Entregar solo el MP4. Si pesa GBs, no se aplicó el método."])
s += [Paragraph("Si un video excede el patrón: subir CRF (20→23), bajar a 30 fps o reducir efectos de grano (el grano comprime mal).", BOX), PageBreak()]

# ---- 5
s += [Paragraph("05 · La mascota: pistola 10 mm (Fallout 3)", H1),
      Paragraph("El canal tiene dos figuras: el <b>anfitrión humano</b> ochentero (cara del canal) y la <b>mascota-gag</b>: la pistola 10 mm del inicio de Fallout 3, grande y expresiva. "
                "No aparece desde el principio: <b>entra a mitad del video</b>, en un momento donde faltaba un refuerzo o una animación, para subrayar un dato, reaccionar o romper el ritmo.", P)]
s += bullets(["<b>Diseño:</b> corredera de acero gris azulado, empuñadura de madera, martillo visible, ojos grandes en la corredera, boca pequeña, brazos y piernas cortos con guantes blancos. Marca “10mm” grabada.",
              "<b>Rig por partes</b> (el SVG tiene grupos con id): cuerpo, martillo, ojos, boca, brazo_i, brazo_d, pierna_i, pierna_d. Se animan en el JSON con <i>parte</i>, <i>pivote</i> y <i>prop</i>.",
              "<b>Animaciones base:</b> entrada con rebote + elástico (0,9 s) y mini temblor de cámara; el martillo se arma (anticipación) cuando va a decir algo; ojos que miran al dato; balanceo suave de reposo.",
              "<b>Reglas:</b> nunca dispara ni apunta a personas; es simpática y torpe. Siempre rol <i>sujeto</i> (con color). Se escala ~0,6 respecto del anfitrión.",
              "<b>Originalidad:</b> versión ilustrada propia; no es una copia del modelo de Bethesda. Referencia a buscar: “Fallout 3 10mm pistol” (wiki de Fallout)."])
s += [foto("demo_mascota.png", 150 * mm), Paragraph("La mascota entra a los 9 s en la demo (rebote + martillo + ojos).", CAP), PageBreak()]

# ---- 6
s += [Paragraph("06 · El mundo de assets (catálogo)", H1),
      Paragraph("Todo está en <i>extra/mundo</i>: 79 assets SVG (v3) organizados por categoría, <i>catalogo.json</i> con id/etiquetas/rol, <i>paletas.json</i> y el motor de escenas. "
                "Cada pedido nuevo <b>agrega</b> más árboles, estructuras, basura, props, suelos y personajes. Regla del motor: nunca un plano vacío (auditoría automática avisa si falta suelo, primer plano o detalles).", P),
      foto("demo_callejon.png", 150 * mm), Paragraph("Callejón armado solo con assets del catálogo (cielo, edificios, pared, suelo, contenedor, cajas, basura, primer plano, polvo y luz).", CAP)]
for n, t in (("hoja_exterior.png", "Exterior"), ("hoja_interior.png", "Interior"), ("hoja_naturaleza_basura.png", "Naturaleza, basura y suelos"), ("hoja_personajes_props.png", "Personajes, mascota, props y efectos")):
    s += [KeepTogether([Paragraph(t, H2), foto(n, 172 * mm, q=85, maxw=1600)])]
s += [PageBreak()]

# ---- 7
s += [Paragraph("07 · Cómo ampliar y reutilizar el mundo", H1)]
s += bullets(["<b>En otro chat:</b> clonar el repo, entrar a <i>extra/</i> y leer <i>extra/CLAUDE.md</i>; contiene todas las reglas y comandos. Pedir “usá extra/mundo”.",
              "<b>Agregar assets:</b> editar <i>mundo/herramientas/generar_assets.py</i> (decorador <i>@asset</i>) o registrar un SVG propio con <i>agregar_asset.py</i>.",
              "<b>Armar escenas:</b> JSON con capas (paralaje), items, animaciones, cámara, temblor, destellos y fundidos; o usar el editor visual y exportar.",
              "<b>Temas:</b> <i>paletas.json</i> (gta4, vice, gta6, futbol); sumar uno nuevo para otro juego.",
              "<b>Referencias a incorporar:</b> si querés más fidelidad, enviá imágenes de gta4.tv / gta4.net / gtabase y se derivan paletas y nuevos props (siempre redibujados, no copiados)."])
s += [Paragraph("Checklist de aprobación (ampliado)", H2)]
s += bullets(["¿Se ve 2D con profundidad, no 3D?", "¿Fondo descolorido y sujeto con color (con color afín en objetos cercanos)?", "¿Ninguna capa vacía y el suelo con textura/detalle?",
              "¿Luz con dirección y motivo?", "¿Intro de silueta solo en videos largos?", "¿La mascota entra a mitad y aporta?", "¿El MP4 pesa dentro del presupuesto?"])
s += [Paragraph("Referencias (enlaces, no copias)", H2),
      Paragraph("https://www.gta4.tv/images/artwork · https://www.gta4.net/artwork/?page=1 · https://www.gtabase.com/grand-theft-auto-iv/artworks/gta-4/ · "
                "https://fallout.fandom.com/wiki/10mm_pistol_(Fallout_3). Las marcas y arte de Grand Theft Auto y Fallout pertenecen a sus titulares; Extra desarrolla recursos propios inspirados en ese lenguaje.", SM),
      Paragraph("Limitación honesta: los assets son ilustraciones vectoriales procedurales; sirven de base consistente y liviana. Para acercarse más a la pintura de GTA IV se irán refinando (más pliegues, luces y texturas) con cada pedido.", SM)]


# ---- 8 (v3)
s += [PageBreak(), Paragraph("08 · Realismo cinematográfico (v3)", H1),
      Paragraph("A pedido: mucho más realista y cinematográfico, siempre 2D con profundidad. Qué cambió respecto de la v2:", P)]
s += bullets([
    "<b>Texturas fotográficas CC0 'pintadas'</b> (ambientCG): ladrillo, piedra, asfalto, concreto, adoquín, madera, metal oxidado, chapa, cuero, tela, hojas, tierra, pasto, revoque, goma, vidrio. Se procesan con un paint-over (mediana + realce + grading frío) y pesan menos de 1 MB en total. Los assets las usan como material, con luz, sombra y suciedad encima.",
    "<b>Assets HD:</b> edificios con marcos de piedra, reflejos en vidrio, cortinas, aires acondicionados y churretes de suciedad; suelos con líneas gastadas, grietas y aceite; follaje por masas con textura real; contenedor oxidado, cajas de madera, sofá de cuero, alfombra de tela.",
    "<b>Personajes realistas:</b> proporción de ~6,7 cabezas; rostro con planos de luz, ojos con iris y reflejo, cejas, nariz, labios, barba de textura; pelo por mechones; ropa con textura real y pliegues; manos con dedos. Rig con codos (brazo + antebrazo), parpadeo, cabeza y respiración.",
    "<b>Mascota HD:</b> acero cepillado con rayones, empuñadura de madera real, mira, puerto de eyección, ojos con iris y brillo, guantes y botas.",
    "<b>Cámara de cine:</b> profundidad de campo por capa con <i>rack focus</i> animable, cámara en mano, grading por tema, luz con dirección + rim light + sombras proyectadas, grano animado, viñeta, letterbox, bruma atmosférica y filtro 'pintado' que une todo.",
    "<b>Animación orgánica:</b> ruido suave (idle) en cabeza/brazos/torso, curvas de rebote/elástico, parpadeo, gesto con anticipación y seguimiento.",
    "<b>Assets nuevos:</b> puerta metálica, graffiti, banco, neumático, tacho, baranda, andamio, cielos (atardecer, nublado), resplandor de luces, lluvia."])
s += [foto("demo_callejon.png", 160 * mm), Paragraph("Callejón v3: profundidad de campo, texturas fotográficas y personajes con volumen.", CAP),
      foto("demo_mascota.png", 160 * mm), Paragraph("Entrada de la mascota HD.", CAP),
      Paragraph("Tiempo de render", H2),
      Paragraph("El look cinematográfico es costoso: ~1,6 s por cuadro por proceso. Con 4 procesos en paralelo (<font face='Courier'>--workers 4</font>) la demo de 18 s tardó ~8 min. Un video de 10 min a 30 fps tarda varias horas; para borradores usar <font face='Courier'>--rapido</font> y/o <font face='Courier'>--fps 24</font>. El peso del MP4 no cambia: la demo de 18 s pesa 6,1 MB (20,5 MB/min).", P),
      Paragraph("Créditos de texturas: ambientCG (CC0): Bricks059, Bricks075A, Asphalt031, Concrete034, PavingStones070, WoodFloor064, Rust004, CorrugatedSteel005, Leather011, Fabric026, Ground037, Ground054, Grass005, Plaster003, Tiles074, Cardboard004, Rubber004, Facade001. Límite honesto: los personajes siguen siendo ilustración vectorial en capas (no fotorrealismo); se refinan con cada pedido.", SM)]

doc = SimpleDocTemplate(os.path.join(AQUI, "Extra_Guia_Visual_v3.pdf"), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=18 * mm,
                        title="Extra - Guía visual v3.0", author="Extra")
doc.build(s, onFirstPage=pie, onLaterPages=pie)
print("PDF listo")
