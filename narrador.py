#!/usr/bin/env python3
"""Generador automático de narraciones (MP3) para videos cortos con edge-tts.

Ejemplos:
    python narrador.py --comprobar
    python narrador.py                              # todos los .txt de GUIONES/
    python narrador.py --voz tomas GUIONES/intro.txt otra_carpeta/
    python narrador.py --texto "Hola a todos" --nombre saludo --voz gonzalo
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

VOCES = {
    "jorge": "es-MX-JorgeNeural",
    "gonzalo": "es-CO-GonzaloNeural",
    "tomas": "es-AR-TomasNeural",
}
VOZ_POR_DEFECTO = "jorge"
REINTENTOS = 3
FRASE_DE_PRUEBA = "Prueba de conexión."


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


def resolver_voz(valor: str) -> tuple[str, str]:
    """Devuelve (alias, nombre_completo) a partir de un alias o nombre completo."""
    clave = valor.strip().lower()
    if clave in VOCES:
        return clave, VOCES[clave]
    for alias, nombre in VOCES.items():
        if nombre.lower() == clave:
            return alias, nombre
    # Otra voz de edge-tts (p. ej. es-ES-AlvaroNeural): se usa tal cual.
    return sanear(valor.strip()), valor.strip()


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


async def sintetizar(texto: str, voz: str, destino: Path, ajustes: dict) -> None:
    """Genera el MP3 con reintentos; escribe a un temporal y renombra al final."""
    temporal = destino.with_name(destino.name + ".parcial")
    ultimo_error: Exception | None = None
    for intento in range(1, REINTENTOS + 1):
        try:
            await edge_tts.Communicate(texto, voz, **ajustes).save(str(temporal))
            if temporal.stat().st_size == 0:
                raise RuntimeError("el servicio devolvió un audio vacío")
            temporal.replace(destino)
            return
        except Exception as exc:  # noqa: BLE001
            ultimo_error = exc
            temporal.unlink(missing_ok=True)
            if intento < REINTENTOS:
                await asyncio.sleep(2 * intento)
    raise RuntimeError(f"falló tras {REINTENTOS} intentos: {ultimo_error}")


async def procesar(args: argparse.Namespace) -> int:
    alias, voz = resolver_voz(args.voz)

    if args.comprobar:
        print("Comprobando conexión con el servicio de voz…")
        voces = sorted(set(VOCES.values()) | {voz})
        ok = await comprobar_conexion(voces)
        print("Conexión OK." if ok else "La comprobación FALLÓ.")
        return 0 if ok else 1

    guiones = reunir_guiones(args.guiones, args.texto, args.nombre)
    if not guiones:
        print("No se encontraron guiones (.txt) para procesar.")
        return 1

    print(f"Voz: {voz}  |  Guiones: {len(guiones)}  |  Salida: {args.salida}")
    if not await comprobar_conexion([voz], detallado=False):
        print("No hay conexión con el servicio de voz; no se generó nada.")
        return 1

    salida = Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)
    ajustes = {"rate": args.velocidad, "pitch": args.tono, "volume": args.volumen}

    generados = omitidos = fallidos = 0
    usados: set[str] = set()
    for guion in guiones:
        base = f"{sanear(guion.nombre)}_{alias}"
        nombre_archivo, n = base, 2
        while nombre_archivo in usados:  # dos guiones con el mismo nombre saneado
            nombre_archivo, n = f"{base}_{n}", n + 1
        usados.add(nombre_archivo)
        destino = salida / f"{nombre_archivo}.mp3"

        texto = " ".join(guion.texto.split())
        if not texto:
            print(f"  OMITIDO  {guion.nombre}: guion vacío")
            omitidos += 1
        elif destino.exists() and not args.sobrescribir:
            print(f"  OMITIDO  {destino.name}: ya existe (usar --sobrescribir)")
            omitidos += 1
        else:
            try:
                await sintetizar(texto, voz, destino, ajustes)
                print(f"  OK       {destino.name} ({destino.stat().st_size / 1024:.0f} KB)")
                generados += 1
            except Exception as exc:  # noqa: BLE001
                print(f"  FALLO    {guion.nombre}: {exc}")
                fallidos += 1

    print(f"Resumen: {generados} generados, {omitidos} omitidos, {fallidos} fallidos.")
    return 1 if fallidos else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Genera narraciones MP3 a partir de guiones de texto (edge-tts)."
    )
    parser.add_argument(
        "guiones",
        nargs="*",
        help="archivos .txt o carpetas con guiones (por defecto: GUIONES/)",
    )
    parser.add_argument(
        "--voz",
        default=VOZ_POR_DEFECTO,
        help="jorge (es-MX, por defecto), gonzalo (es-CO), tomas (es-AR) "
        "o el nombre completo de una voz de edge-tts",
    )
    parser.add_argument("--texto", help="guion escrito directamente en la línea de comandos")
    parser.add_argument("--nombre", help="nombre del archivo de salida para --texto")
    parser.add_argument("--salida", default=str(CARPETA_SALIDA), help="carpeta de salida")
    parser.add_argument("--velocidad", default="+0%", help="p. ej. +10%% o -5%%")
    parser.add_argument("--tono", default="+0Hz", help="p. ej. +5Hz o -10Hz")
    parser.add_argument("--volumen", default="+0%", help="p. ej. +20%%")
    parser.add_argument(
        "--sobrescribir", action="store_true", help="regenerar los MP3 que ya existen"
    )
    parser.add_argument(
        "--comprobar",
        action="store_true",
        help="solo comprobar la conexión con el servicio y las voces",
    )
    args = parser.parse_args()

    confiar_en_ca_del_entorno()
    return asyncio.run(procesar(args))


if __name__ == "__main__":
    sys.exit(main())
