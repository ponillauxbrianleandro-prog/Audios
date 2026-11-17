#!/usr/bin/env python3
"""Arma el animatic MP4 del episodio 003: tarjetas pastel por escena con zoom/paneo,
subtítulos del SRT y el audio final. Es una previsualización del ritmo, no la animación final.

Requiere: Pillow, numpy, ffmpeg. Corre después de generar_audio.py y musica.py.
Uso: python3 armar_animatic.py
Salida: animatic/episodio-003-animatic.mp4
"""
import json
import random
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = Path(__file__).resolve().parent
EP = AQUI.parent
AUDIO = EP / "audio"
TARJETAS = AQUI / "tarjetas"
W, H = 1080, 1920
FPS = 25
FUENTE = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"

# Por escena: (cielo arriba, cielo abajo, suelo, animal, cámara, rótulo)
ESCENAS = {
    1: ((205, 190, 235), (250, 215, 230), (190, 225, 190), "cerdo", "centro", "¡CHANCHO GORDO!"),
    2: ((205, 190, 235), (255, 225, 205), (200, 225, 180), "ambos", "zoom", "PECARÍ QUIMILERO · TAGUA"),
    3: ((200, 220, 245), (255, 235, 200), (225, 215, 170), "pecari", "zoom", "CACTUS CON ESPINAS"),
    4: ((215, 200, 240), (235, 245, 215), (200, 225, 185), "pecari", "paneo", "GLÁNDULA PERFUMADA"),
    5: ((200, 225, 245), (250, 235, 215), (225, 215, 175), "pecari", "centro", "RANKING: 1 TUNA · 2 TUNA · 3 TUNA"),
    6: ((250, 205, 170), (255, 235, 200), (225, 200, 160), "manada", "paneo", "PATOTA DE DIEZ"),
    7: ((215, 200, 240), (255, 225, 220), (205, 225, 185), "patas", "zoom", "PALILLOS"),
    8: ((255, 225, 190), (255, 245, 220), (210, 225, 185), "pecari", "zoom", "AÑOS 70: ¡VIVO EN EL CHACO!"),
    9: ((250, 195, 165), (255, 230, 190), (205, 220, 170), "pecari", "zoom", "CON ORGULLO"),
}


def degradado(arriba, abajo):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * k) for a, b in zip(arriba, abajo)))
    return img


def pelusa(d, cx, cy, rx, ry, color, rng, n=170):
    """Cuerpo esponjoso: muchas elipses superpuestas con borde irregular."""
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=color)
    for _ in range(n):
        a = rng.uniform(0, 6.283)
        r = rng.uniform(0.86, 1.0)
        x = cx + rx * r * rng.uniform(0.92, 1.05) * __import__("math").cos(a)
        y = cy + ry * r * rng.uniform(0.92, 1.05) * __import__("math").sin(a)
        s = rng.randint(28, 60)
        tono = tuple(max(0, min(255, c + rng.randint(-4, 5))) for c in color)
        d.ellipse([x - s, y - s, x + s, y + s], fill=tono)


def dibujar_pecari(d, cx, cy, escala, rng):
    gris, crema = (176, 168, 160), (238, 228, 205)
    pelusa(d, cx, cy, 300 * escala, 270 * escala, gris, rng)
    pelusa(d, cx, cy - 95 * escala, 215 * escala, 195 * escala, (190, 182, 172), rng, 90)
    d.ellipse([cx - 230 * escala, cy - 70 * escala, cx + 230 * escala, cy + 10 * escala], fill=crema)  # collar claro
    for sx in (-1, 1):
        d.ellipse([cx + sx * 170 * escala - 38 * escala, cy - 290 * escala, cx + sx * 170 * escala + 38 * escala,
                   cy - 210 * escala], fill=(150, 140, 135))  # orejas
        d.ellipse([cx + sx * 70 * escala - 11 * escala, cy - 180 * escala, cx + sx * 70 * escala + 11 * escala,
                   cy - 158 * escala], fill=(40, 34, 38))  # ojos chiquitos
    d.ellipse([cx - 60 * escala, cy - 140 * escala, cx + 60 * escala, cy - 60 * escala], fill=(225, 190, 185))  # hocico
    for sx in (-1, 1):
        d.ellipse([cx + sx * 22 * escala - 9 * escala, cy - 112 * escala, cx + sx * 22 * escala + 9 * escala,
                   cy - 92 * escala], fill=(120, 80, 85))


def dibujar_cerdo(d, cx, cy, escala, rng):
    rosa = (250, 190, 200)
    pelusa(d, cx, cy, 310 * escala, 280 * escala, rosa, rng, 60)
    for sx in (-1, 1):
        d.polygon([(cx + sx * 150 * escala, cy - 230 * escala), (cx + sx * 260 * escala, cy - 330 * escala),
                   (cx + sx * 250 * escala, cy - 170 * escala)], fill=(240, 165, 180))
        d.ellipse([cx + sx * 85 * escala - 11 * escala, cy - 130 * escala, cx + sx * 85 * escala + 11 * escala,
                   cy - 108 * escala], fill=(50, 35, 45))
    d.ellipse([cx - 90 * escala, cy - 90 * escala, cx + 90 * escala, cy + 20 * escala], fill=(240, 150, 170))
    for sx in (-1, 1):
        d.ellipse([cx + sx * 30 * escala - 12 * escala, cy - 55 * escala, cx + sx * 30 * escala + 12 * escala,
                   cy - 20 * escala], fill=(150, 80, 100))


def tarjeta(n, rng):
    arriba, abajo, suelo, animal, _, rotulo = ESCENAS[n]
    img = degradado(arriba, abajo)
    d = ImageDraw.Draw(img, "RGBA")
    # Fondo lejano: montañas y nubes (plano 3)
    for i in range(4):
        x = i * 330 - 80
        d.polygon([(x, 1150), (x + 260, 900 - rng.randint(0, 100)), (x + 520, 1150)], fill=(170, 160, 205, 150))
    for _ in range(5):
        cx, cy = rng.randint(60, W - 60), rng.randint(140, 520)
        for k in range(4):
            d.ellipse([cx + k * 55 - 70, cy - 40, cx + k * 55 + 70, cy + 40], fill=(255, 255, 255, 170))
    # Plano medio: suelo
    d.rectangle([0, 1150, W, H], fill=suelo)
    d.ellipse([-200, 1100, W + 200, 1300], fill=suelo)
    # Animal(es) (plano 1)
    if animal == "cerdo":
        dibujar_cerdo(d, W // 2, 1000, 1.25, rng)
    elif animal == "ambos":
        dibujar_cerdo(d, 300, 1180, 0.6, rng)
        dibujar_pecari(d, 700, 1050, 1.0, rng)
    elif animal == "manada":
        for i in range(5):
            dibujar_pecari(d, 220 + i * 160, 900 + i * 120, 0.28 + i * 0.1, rng)
    elif animal == "patas":
        for sx in (-1, 1):
            for dx in (110, 230):
                d.rectangle([W // 2 + sx * dx - 14, 1060, W // 2 + sx * dx + 14, 1480], fill=(150, 140, 135))
        pelusa(d, W // 2, 900, 330, 250, (176, 168, 160), rng)
        d.ellipse([W // 2 - 20, 1120, W // 2 + 20, 1160], fill=(240, 200, 160))  # caracol
    else:
        dibujar_pecari(d, W // 2, 1000, 1.2, rng)
    # Rótulo de la escena
    fuente = ImageFont.truetype(FUENTE, 62)
    ancho = d.textlength(rotulo, font=fuente)
    if ancho > W - 80:
        fuente = ImageFont.truetype(FUENTE, int(62 * (W - 80) / ancho))
        ancho = d.textlength(rotulo, font=fuente)
    d.rounded_rectangle([W / 2 - ancho / 2 - 30, 170, W / 2 + ancho / 2 + 30, 270], 30, fill=(255, 255, 255, 190))
    d.text((W / 2 - ancho / 2, 188), rotulo, font=fuente, fill=(80, 60, 120))
    return img.filter(ImageFilter.GaussianBlur(0.6))


def main():
    TARJETAS.mkdir(exist_ok=True)
    escenas = json.loads((AUDIO / "escenas.json").read_text())
    total = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
         str(AUDIO / "episodio-003-final.mp3")], capture_output=True, text=True, check=True).stdout)
    clips = []
    for i, e in enumerate(escenas):
        n = e["escena"]
        png = TARJETAS / f"escena-{n}.png"
        tarjeta(n, random.Random(n)).save(png)
        # Cada tarjeta dura hasta el inicio de la siguiente (la primera arranca en 0).
        fin = escenas[i + 1]["inicio"] if i + 1 < len(escenas) else total
        inicio = 0 if i == 0 else e["inicio"]
        frames = max(1, round((fin - inicio) * FPS))
        camara = ESCENAS[n][4]
        if camara == "zoom":
            z, x, y = "min(1.0+0.0009*on,1.25)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
        elif camara == "paneo":
            z, x, y = "1.2", f"(iw-iw/zoom)*on/{frames}", "ih/2-(ih/zoom/2)"
        else:
            z, x, y = "1.0+0.04*sin(on/20)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
        clip = TARJETAS / f"clip-{n}.mp4"
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", str(png), "-vf",
             f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s=720x1280:fps={FPS},format=yuv420p",
             "-frames:v", str(frames), "-c:v", "libx264", "-crf", "20", str(clip)], check=True)
        clips.append(clip)

    lista = TARJETAS / "clips.txt"
    lista.write_text("".join(f"file '{c}'\n" for c in clips))
    sin_audio = TARJETAS / "sin-audio.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
                    "-c", "copy", str(sin_audio)], check=True)
    estilo = ("FontName=Inter,FontSize=9,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00503C78,"
              "BorderStyle=1,Outline=3,Alignment=2,MarginV=30")
    srt = str(AUDIO / "episodio-003-voz.srt").replace(":", r"\:")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(sin_audio), "-i", str(AUDIO / "episodio-003-final.mp3"),
         "-vf", f"subtitles='{srt}':original_size=720x1280:force_style='{estilo}'", "-c:v", "libx264", "-crf", "20",
         "-c:a", "aac", "-b:a", "192k", "-shortest", str(AQUI / "episodio-003-animatic.mp4")], check=True)
    print("Listo:", AQUI / "episodio-003-animatic.mp4")


if __name__ == "__main__":
    main()
