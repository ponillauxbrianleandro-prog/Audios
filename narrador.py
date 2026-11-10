#!/usr/bin/env python3
"""Generador automático de narraciones (MP3) para videos cortos con edge-tts.

Solo voces masculinas rioplatenses: Tomás (Argentina) y Mateo (Uruguay).

Ejemplos:
    python narrador.py --comprobar
    python narrador.py --listar
    python narrador.py                              # todos los .txt de GUIONES/
    python narrador.py --voz mateo --modo shorts GUIONES/intro.txt
    python narrador.py --voz todas --subtitulos
    python narrador.py --texto "Hola a todos" --nombre saludo --modo energico
"""

from __future__ import annotations

import argparse
import asyncio
import os
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import edge_tts

RAIZ = Path(__file__).resolve().parent
CARPETA_GUIONES = RAIZ / "GUIONES"
CARPETA_SALIDA = RAIZ / "OUTPUT" / "AUDIO"

# Únicas voces masculinas rioplatenses del servicio.
VOCES = {
    "tomas": "es-AR-TomasNeural",
    "mateo": "es-UY-MateoNeural",
}
VOZ_POR_DEFECTO = "tomas"

# Modos de audio: (descripción, velocidad, tono, volumen).
MODOS = {
    "neutral": ("narración estándar", "+0%", "+0Hz", "+0%"),
    "shorts": ("ritmo ágil para Reels/Shorts/TikTok", "+12%", "+0Hz", "+0%"),
    "energico": ("gancho / llamada a la acción", "+18%", "+4Hz", "+10%"),
    "pausado": ("explicativo, tutorial", "-10%", "+0Hz", "+0%"),
    "grave": ("documental / dramático", "-6%", "-8Hz", "+0%"),
    "suave": ("relato íntimo, calmo", "-8%", "-2Hz", "-10%"),
}
MODO_POR_DEFECTO = "neutral"

REINTENTOS = 3
FRASE_DE_PRUEBA = "Prueba de conexión."
BYTES_POR_SEGUNDO = 48_000 / 8  # edge-tts entrega MP3 a 48 kbps constantes


@dataclass
class Guion:
    nombre: str
    texto: str


def confiar_en_ca_del_entorno() -> None:
    """Suma a edge-tts los certificados raíz definidos por el entorno.

    edge-tts solo confía en el bundle de certifi. En entornos con proxy HTTPS
    corporativo (como Claude Code Cloud) la CA del proxy se publica en
    SSL_CERT_FILE; sin esto la síntesis falla con CERTIFICATE_VERIFY_FAILED.
    La verificación TLS sigue activa: solo se agregan CAs de confianza.
    """
    for variable in ("SSL_CERT_FILE", "REQUESTS_CA_BUNDLE"):
        ruta = os.environ.get(variable)
        if not ruta or not Path(ruta).is_file():
            continue
        for modulo in ("edge_tts.communicate", "edge_tts.voices"):
            contexto = getattr(sys.modules.get(modulo), "_SSL_CTX", None)
            if contexto is not None:
                contexto.load_verify_locations(cafile=ruta)
        return


def resolver_voces(valor: str) -> list[tuple[str, str]]:
    """Devuelve [(alias, nombre_completo)] para un alias, nombre completo o 'todas'."""
    clave = valor.strip().lower()
    if clave == "todas":
        return list(VOCES.items())
    for alias, nombre in VOCES.items():
        if clave in (alias, nombre.lower()):
            return [(alias, nombre)]
    opciones = ", ".join(f"{a} ({n})" for a, n in VOCES.items())
    raise SystemExit(
        f"ERROR: voz no permitida: {valor}. Solo voces rioplatenses masculinas: "
        f"{opciones}, o 'todas'."
    )


def sanear(nombre: str) -> str:
    """Nombre de archivo prolijo: minúsculas, sin acentos, sin espacios."""
    sin_acentos = (
        unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode()
    )
    limpio = re.sub(r"[^a-z0-9]+", "_", sin_acentos.lower()).strip("_")
    return limpio or "guion"


def reunir_guiones(rutas: list[str], texto: str | None, nombre: str | None) -> list[Guion]:
    guiones: list[Guion] = []
    if texto is not None:
        guiones.append(Guion(nombre or "guion", texto))

    if not rutas and texto is None:
        rutas = [str(CARPETA_GUIONES)]

    archivos: list[Path] = []
    for ruta in rutas:
        p = Path(ruta)
        if p.is_dir():
            archivos.extend(sorted(p.glob("*.txt")))
        elif p.is_file():
            archivos.append(p)
        else:
            raise SystemExit(f"ERROR: no existe el guion o carpeta: {ruta}")

    for archivo in archivos:
        guiones.append(Guion(archivo.stem, archivo.read_text(encoding="utf-8")))
    return guiones


def listar() -> None:
    print("Voces (--voz):")
    for alias, nombre in VOCES.items():
        marca = "  (por defecto)" if alias == VOZ_POR_DEFECTO else ""
        print(f"  {alias:<9} {nombre}{marca}")
    print("  todas     genera cada guion con todas las voces")
    print("\nModos (--modo):")
    for modo, (descripcion, velocidad, tono, volumen) in MODOS.items():
        print(
            f"  {modo:<9} {descripcion:<38} "
            f"velocidad {velocidad:>4}  tono {tono:>5}  volumen {volumen:>4}"
        )


async def comprobar_conexion(voces: list[str], detallado: bool = True) -> bool:
    """Verifica que el servicio responde y que las voces pedidas existen."""
    try:
        disponibles = {v["ShortName"] for v in await edge_tts.list_voices()}
    except Exception as exc:  # noqa: BLE001 - se informa cualquier fallo de red
        print(f"  FALLO  no se pudo consultar el catálogo de voces: {exc}")
        return False
    if detallado:
        print(f"  OK     catálogo de voces accesible ({len(disponibles)} voces)")

    todo_ok = True
    for voz in voces:
        if voz not in disponibles:
            print(f"  FALLO  la voz {voz} no existe en el servicio")
            todo_ok = False
            continue
        try:
            recibidos = 0
            async for parte in edge_tts.Communicate(FRASE_DE_PRUEBA, voz).stream():
                if parte["type"] == "audio":
                    recibidos += len(parte["data"])
            if recibidos == 0:
                raise RuntimeError("el servicio no devolvió audio")
            if detallado:
                print(f"  OK     {voz}: síntesis de prueba ({recibidos} bytes)")
        except Exception as exc:  # noqa: BLE001
            print(f"  FALLO  {voz}: {exc}")
            todo_ok = False
    return todo_ok


def _marca_srt(ticks: int) -> str:
    """Convierte ticks de 100 ns al formato de tiempo SRT (HH:MM:SS,mmm)."""
    ms = round(ticks / 10_000)
    horas, ms = divmod(ms, 3_600_000)
    minutos, ms = divmod(ms, 60_000)
    segundos, ms = divmod(ms, 1_000)
    return f"{horas:02}:{minutos:02}:{segundos:02},{ms:03}"


def armar_srt(palabras: list[dict], por_linea: int) -> str:
    """Agrupa las marcas de palabra en subtítulos de `por_linea` palabras."""
    bloques = []
    for i in range(0, len(palabras), por_linea):
        grupo = palabras[i : i + por_linea]
        inicio = grupo[0]["offset"]
        fin = grupo[-1]["offset"] + grupo[-1]["duration"]
        texto = " ".join(p["text"] for p in grupo)
        bloques.append(
            f"{len(bloques) + 1}\n{_marca_srt(inicio)} --> {_marca_srt(fin)}\n{texto}\n"
        )
    return "\n".join(bloques)


async def sintetizar(
    texto: str, voz: str, destino: Path, ajustes: dict, palabras_por_linea: int | None
) -> float:
    """Genera el MP3 (y el .srt si se pide) con reintentos. Devuelve la duración en s.

    Escribe a un temporal y renombra al final para no dejar archivos truncados.
    """
    temporal = destino.with_name(destino.name + ".parcial")
    limite = "WordBoundary" if palabras_por_linea else "SentenceBoundary"
    ultimo_error: Exception | None = None
    for intento in range(1, REINTENTOS + 1):
        try:
            palabras: list[dict] = []
            total = 0
            with temporal.open("wb") as salida:
                com = edge_tts.Communicate(texto, voz, boundary=limite, **ajustes)
                async for parte in com.stream():
                    if parte["type"] == "audio":
                        salida.write(parte["data"])
                        total += len(parte["data"])
                    elif parte["type"] == "WordBoundary":
                        palabras.append(parte)
            if total == 0:
                raise RuntimeError("el servicio devolvió un audio vacío")
            if palabras_por_linea:
                if not palabras:
                    raise RuntimeError("el servicio no devolvió marcas de tiempo")
                destino.with_suffix(".srt").write_text(
                    armar_srt(palabras, palabras_por_linea), encoding="utf-8"
                )
            temporal.replace(destino)
            return total / BYTES_POR_SEGUNDO
        except Exception as exc:  # noqa: BLE001
            ultimo_error = exc
            temporal.unlink(missing_ok=True)
            if intento < REINTENTOS:
                await asyncio.sleep(2 * intento)
    raise RuntimeError(f"falló tras {REINTENTOS} intentos: {ultimo_error}")


async def procesar(args: argparse.Namespace) -> int:
    if args.listar:
        listar()
        return 0

    if args.comprobar:
        print("Comprobando conexión con el servicio de voz…")
        ok = await comprobar_conexion(sorted(VOCES.values()))
        print("Conexión OK." if ok else "La comprobación FALLÓ.")
        return 0 if ok else 1

    voces = resolver_voces(args.voz)
    _, velocidad, tono, volumen = MODOS[args.modo]
    ajustes = {
        "rate": args.velocidad or velocidad,
        "pitch": args.tono or tono,
        "volume": args.volumen or volumen,
    }
    palabras_por_linea = args.palabras_por_linea if args.subtitulos else None

    guiones = reunir_guiones(args.guiones, args.texto, args.nombre)
    if not guiones:
        print("No se encontraron guiones (.txt) para procesar.")
        return 1

    print(
        f"Voz: {', '.join(n for _, n in voces)}  |  Modo: {args.modo} "
        f"({ajustes['rate']}, {ajustes['pitch']}, {ajustes['volume']})  |  "
        f"Guiones: {len(guiones)}  |  Salida: {args.salida}"
    )
    if not await comprobar_conexion([n for _, n in voces], detallado=False):
        print("No hay conexión con el servicio de voz; no se generó nada.")
        return 1

    salida = Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)
    sufijo_modo = "" if args.modo == MODO_POR_DEFECTO else f"_{args.modo}"

    generados = omitidos = fallidos = 0
    usados: set[str] = set()
    for guion in guiones:
        texto = " ".join(guion.texto.split())
        if not texto:
            print(f"  OMITIDO  {guion.nombre}: guion vacío")
            omitidos += 1
            continue
        for alias, voz in voces:
            base = f"{sanear(guion.nombre)}_{alias}{sufijo_modo}"
            nombre_archivo, n = base, 2
            while nombre_archivo in usados:  # guiones con el mismo nombre saneado
                nombre_archivo, n = f"{base}_{n}", n + 1
            usados.add(nombre_archivo)
            destino = salida / f"{nombre_archivo}.mp3"

            falta_srt = bool(palabras_por_linea) and not destino.with_suffix(".srt").exists()
            if destino.exists() and not falta_srt and not args.sobrescribir:
                print(f"  OMITIDO  {destino.name}: ya existe (usar --sobrescribir)")
                omitidos += 1
                continue
            try:
                duracion = await sintetizar(texto, voz, destino, ajustes, palabras_por_linea)
                extra = " + .srt" if palabras_por_linea else ""
                print(f"  OK       {destino.name}{extra} ({duracion:.1f} s)")
                generados += 1
            except Exception as exc:  # noqa: BLE001
                print(f"  FALLO    {destino.name}: {exc}")
                fallidos += 1

    print(f"Resumen: {generados} generados, {omitidos} omitidos, {fallidos} fallidos.")
    return 1 if fallidos else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Genera narraciones MP3 con voces masculinas rioplatenses (edge-tts)."
    )
    parser.add_argument(
        "guiones",
        nargs="*",
        help="archivos .txt o carpetas con guiones (por defecto: GUIONES/)",
    )
    parser.add_argument(
        "--voz",
        default=VOZ_POR_DEFECTO,
        help="tomas (es-AR, por defecto), mateo (es-UY) o todas",
    )
    parser.add_argument(
        "--modo",
        default=MODO_POR_DEFECTO,
        choices=list(MODOS),
        help="modo de audio (ver --listar)",
    )
    parser.add_argument("--texto", help="guion escrito directamente en la línea de comandos")
    parser.add_argument("--nombre", help="nombre del archivo de salida para --texto")
    parser.add_argument("--salida", default=str(CARPETA_SALIDA), help="carpeta de salida")
    parser.add_argument("--velocidad", help="pisa la del modo, p. ej. +10%% o -5%%")
    parser.add_argument("--tono", help="pisa el del modo, p. ej. +5Hz o -10Hz")
    parser.add_argument("--volumen", help="pisa el del modo, p. ej. +20%%")
    parser.add_argument(
        "--subtitulos", action="store_true", help="guardar un .srt junto a cada MP3"
    )
    parser.add_argument(
        "--palabras-por-linea",
        type=int,
        default=4,
        metavar="N",
        help="palabras por subtítulo (por defecto 4)",
    )
    parser.add_argument(
        "--sobrescribir", action="store_true", help="regenerar los archivos que ya existen"
    )
    parser.add_argument(
        "--listar", action="store_true", help="mostrar voces y modos disponibles"
    )
    parser.add_argument(
        "--comprobar",
        action="store_true",
        help="solo comprobar la conexión con el servicio y las voces",
    )
    args = parser.parse_args()
    if args.palabras_por_linea < 1:
        parser.error("--palabras-por-linea debe ser 1 o más")

    confiar_en_ca_del_entorno()
    return asyncio.run(procesar(args))


if __name__ == "__main__":
    sys.exit(main())
