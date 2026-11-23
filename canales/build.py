#!/usr/bin/env python3
"""Genera los 3 documentos .docx a partir de canales/fuentes/*.txt"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "fuentes")
IMG = os.path.join(SRC, "img")


def new_doc():
    d = Document()
    s = d.sections[0]
    s.page_width, s.page_height = Cm(21), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.2)
    s.top_margin = s.bottom_margin = Cm(2)
    st = d.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(11)
    st.paragraph_format.space_after = Pt(6)
    for name, size in (("Heading 1", 18), ("Heading 2", 14), ("Heading 3", 12)):
        h = d.styles[name]
        h.font.name = "Calibri"
        h.font.size = Pt(size)
        h.font.bold = True
        h.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)
    return d


def cover(d, title, subtitle):
    p = d.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(160)
    r = p.add_run(title)
    r.bold = True
    r.font.size = Pt(34)
    r.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)
    p = d.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(subtitle)
    r.font.size = Pt(14)
    r.italic = True
    d.add_page_break()


def add_text(d, filename, h1_as_part=True):
    with open(os.path.join(SRC, filename), encoding="utf-8") as f:
        lines = f.read().split("\n")
    first = True
    for ln in lines:
        if not ln.strip():
            continue
        if ln.startswith("### "):
            d.add_heading(ln[4:], 3)
        elif ln.startswith("## "):
            d.add_heading(ln[3:], 2)
        elif ln.startswith("# "):
            if not first:
                d.add_page_break()
            d.add_heading(ln[2:], 1)
        elif ln.startswith("- "):
            d.add_paragraph(ln[2:], style="List Bullet")
        elif len(ln) > 2 and ln[0].isdigit() and ln[1] == "." and ln[2] == " ":
            d.add_paragraph(ln, style="List Number") if False else d.add_paragraph(ln)
        elif ln.startswith("   - "):
            d.add_paragraph(ln.strip()[2:], style="List Bullet 2")
        else:
            d.add_paragraph(ln)
        first = False


def add_refs(d, title, intro, items):
    d.add_page_break()
    d.add_heading(title, 1)
    d.add_paragraph(intro)
    for n, caption in items:
        path = os.path.join(IMG, f"ref_{n:02d}.jpg")
        d.add_picture(path, width=Cm(14))
        d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        c = d.add_paragraph(f"Referencia {n}: {caption}")
        c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        c.runs[0].italic = True
        c.runs[0].font.size = Pt(9)


def part(d, title, note=None):
    d.add_page_break()
    p = d.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(200)
    r = p.add_run(title)
    r.bold = True
    r.font.size = Pt(26)
    r.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)
    if note:
        q = d.add_paragraph(note)
        q.alignment = WD_ALIGN_PARAGRAPH.CENTER
        q.runs[0].italic = True
    d.add_page_break()


def index(d, entries):
    d.add_heading("Contenido", 1)
    for i, e in enumerate(entries, 1):
        d.add_paragraph(f"{i}. {e}")
    d.add_page_break()


OUT = os.path.join(BASE, "docs")
os.makedirs(OUT, exist_ok=True)

# ---------------- Río Puratense ----------------
d = new_doc()
cover(d, "Río Puratense", "Canal de documentales de animales: documento maestro de estilo, personajes, guion y voz")
index(d, [
    "Estilo artístico general y reglas visuales obligatorias",
    "Estilo artístico particular: documentales de animales",
    "Identidad y personalidad del canal",
    "Personajes del canal documental",
    "Personalidad audiovisual y reglas de guion",
    "Voz del narrador principal",
    "Referencias visuales",
])
add_text(d, "general.txt")
d.add_page_break()
add_text(d, "doc_estilo.txt")
d.add_page_break()
add_text(d, "doc_identidad.txt")
d.add_page_break()
add_text(d, "doc_personajes.txt")
d.add_page_break()
add_text(d, "doc_guion.txt")
d.add_page_break()
add_text(d, "doc_voz.txt")
add_refs(d, "REFERENCIAS VISUALES: RÍO PURATENSE",
         "Imágenes de referencia para el estilo artístico del canal de documentales (ambientes de bosque, color predominante, luz atmosférica).",
         [(1, "bosque de otoño amarillo-anaranjado con luz volumétrica"),
          (2, "bosque rojo con lago y reflejos"),
          (3, "bosque verde con ruina cubierta de vegetación y luz filtrada"),
          (4, "bosque nevado nocturno con aurora")])
d.save(os.path.join(OUT, "Rio_Puratense.docx"))

# ---------------- Kosu Safari ----------------
d = new_doc()
cover(d, "Kosu Safari", "Canal de safari animado: documento maestro de estilo, personajes, guion y voces")
index(d, [
    "Estilo artístico general y reglas visuales obligatorias",
    "Estilo artístico particular: safari animado",
    "Diseño conceptual, personalidad y comportamiento de los personajes",
    "Personalidad audiovisual y reglas de guion",
    "Voz del guía australiano",
    "Voces del equipo de expedición: guía, Gunter y robot",
    "Referencias visuales",
])
add_text(d, "general.txt")
d.add_page_break()
add_text(d, "safari_estilo.txt")
d.add_page_break()
add_text(d, "safari_personajes.txt")
d.add_page_break()
add_text(d, "safari_guion.txt")
d.add_page_break()
add_text(d, "safari_voz_guia.txt")
d.add_page_break()
add_text(d, "safari_voz_trio.txt")
add_refs(d, "REFERENCIAS VISUALES: KOSU SAFARI",
         "Imágenes de referencia para el estilo artístico del canal de safari (sabana, composición cromática 60/30/10, luz de atardecer).",
         [(5, "sabana al atardecer con laguna, montañas y luz cálida"),
          (6, "siluetas de búfalos y acacia entre bruma rojiza con sol grande"),
          (7, "árbol colosal en un campo rojo-anaranjado, atmósfera dorada"),
          (8, "palmeras y edificios en tonos pastel de atardecer (referencia cromática de cielo)")])
d.save(os.path.join(OUT, "Kosu_Safari.docx"))

# ---------------- Canal extra ----------------
d = new_doc()
cover(d, "Estilo Artístico General: Canal Extra",
      "Videos de videojuegos (GTA 6 y similares), independientes de los otros dos canales")
d.add_heading("Nota de uso", 1)
d.add_paragraph("Este documento contiene el texto del estilo artístico general y las referencias visuales para el canal extra: videos que no pertenecen ni a Río Puratense ni a Kosu Safari. Probablemente trate sobre GTA 6 y videojuegos, con una estética como la de las referencias del final. Aún no tiene protagonista propio; podrá definirse más adelante.")
d.add_page_break()
add_text(d, "general.txt")
add_refs(d, "REFERENCIAS VISUALES: CANAL EXTRA",
         "Imágenes de referencia de videojuegos para la estética de este canal.",
         [(9, "bosque rojo de videojuego con templo y fogata"),
          (10, "ciudad costera al atardecer con rueda de la fortuna y agua reflectante"),
          (11, "vista nocturna de la ciudad desde una colina, con auto en primer plano"),
          (12, "calle con palmeras, hoteles y neón sobre cielo rosa")])
d.save(os.path.join(OUT, "Estilo_General_Canal_Extra.docx"))
print("ok")
