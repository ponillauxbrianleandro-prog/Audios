#!/usr/bin/env python3
"""Documental «Vetusodon»: render por escenas con el compositor rápido (render/compositor.py).

  python3 render/documental.py --parte N [--jobs 4] [--solo-escena ID] [--preview DIR] [--escenas ARCHIVO.json]
                               [--rehacer] [--sin-audio] [--t SEG]

· Lee escenas.json (raíz del proyecto; o guion/escenas.json; o --escenas; o render/escenas_prueba.json con --prueba).
· Reanudable: cada escena -> video/segmentos/pN_eID_<hash>.mp4; si ya existe (mismo contenido de escena) no se repite.
· Precarga (una vez, en paralelo) las plantas y los ciclos de animales que faltan en caché, para no repetir trabajo.
· Subtítulos pequeños quemados dentro de cada escena (y video/partes/parteN.srt); fundidos de entrada/salida por escena.
· Concatena con ffmpeg (-c copy) y mezcla render/audio/parteN.wav si existe -> video/partes/parteN.mp4.
· --preview DIR: no renderiza video; guarda un fotograma por escena (a mitad, o en --t SEG) en DIR para revisar.
"""
import argparse
import hashlib
import json
import multiprocessing as mp
import os
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAIZ / "biblioteca"))

VERSION = "c3"                      # subirla invalida los segmentos cacheados al cambiar el compositor
FPS = 24
SEG = RAIZ / "video" / "segmentos"
PARTES = RAIZ / "video" / "partes"
AUDIO = AQUI / "audio"


def cargar_escenas(arch=None, prueba=False):
    cands = [Path(arch)] if arch else ([AQUI / "escenas_prueba.json"] if prueba else
                                       [RAIZ / "escenas.json", RAIZ / "guion" / "escenas.json", AQUI / "escenas_prueba.json"])
    for c in cands:
        if c.exists():
            with open(c, encoding="utf-8") as f:
                d = json.load(f)
            return d["escenas"] if isinstance(d, dict) else d, c
    raise SystemExit("no encuentro escenas.json")


def hash_escena(e):
    s = json.dumps(e, sort_keys=True, ensure_ascii=False) + VERSION
    return hashlib.md5(s.encode()).hexdigest()[:8]


def ruta_seg(e):
    return SEG / f"p{e['parte']}_e{int(e['id']):03d}_{hash_escena(e)}.mp4" if str(e['id']).isdigit() \
        else SEG / f"p{e['parte']}_e{e['id']}_{hash_escena(e)}.mp4"


def duracion_video(p):
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                           capture_output=True, text=True)
        return float(r.stdout.strip())
    except Exception:
        return -1.0


# ------------------------------------------------------------------------------------------ precarga de cachés
def _precarga_tarea(t):
    import compositor as C
    import paletas
    kind = t[0]
    try:
        if kind == "planta":
            C.planta_cache(t[2], paletas.obtener(t[1]))
        else:
            import animales
            animales.ciclo(t[2], t[3], t[4], paletas.obtener(t[1]), t[5])
    except Exception as ex:
        return f"{t}: {ex!r}"[:200]
    return None


def precargar(escenas, jobs):
    import plantas
    tareas = set()
    for e in escenas:
        c = __import__("compositor")
        pal = e["paleta"]
        tareas.add(("planta", pal, "piedra"))
        # las plantas efectivas dependen de la lista + relleno: precargar el relleno posible de la paleta
        for f in e.get("flora") or []:
            if f["especie"] in plantas.ESPECIES:
                tareas.add(("planta", pal, f["especie"]))
        for n in ("glossopteris", "cordaites", "calamites", "equisetum", "dicroidium", "psaronius", "helecho_suelo", "musgo",
                  "hongos", "liquen", "piedra", "mata_seca", "welwitschia", "cicada", "suculenta", "prototaxites", "roca_musgosa",
                  "cyathea"):
            tareas.add(("planta", pal, n))
        for a in e.get("animales") or []:
            tareas.add(("animal", pal, a["especie"], a.get("accion", "idle"), a.get("vista", "3q_der"), a.get("n", 8)))
    # solo lo que falta en disco (las plantas se detectan por el nombre de archivo)
    import compositor as C
    import paletas
    falta = []
    for t in sorted(tareas):
        if t[0] == "planta":
            pal = paletas.obtener(t[1])
            f = C.CACHE / f"pl_{pal['nombre'].replace('+', '_')}_{t[2]}_3_460.pkl"
            if not f.exists():
                falta.append(t)
        else:
            falta.append(t)          # animales.ciclo tiene su propia caché; si existe vuelve enseguida
    if not falta:
        return
    print(f"precarga: {len(falta)} elementos (plantas/animales) con {jobs} procesos", flush=True)
    t0 = time.time()
    with mp.Pool(jobs) as pool:
        for k, r in enumerate(pool.imap_unordered(_precarga_tarea, falta)):
            if r:
                print("  aviso precarga:", r, flush=True)
    print(f"precarga lista en {time.time() - t0:.0f} s", flush=True)


# ------------------------------------------------------------------------------------------ render de una escena
def _ffmpeg(dest):
    return subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "1920x1080", "-r", str(FPS), "-i", "-",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", "-g", "48", "-threads", "2", "-an",
         "-movflags", "+faststart", str(dest)], stdin=subprocess.PIPE)


def render_escena(e):
    """Arma la escena y la renderiza entera en este proceso. Devuelve (id, seg_build, seg_render, n_frames)."""
    import compositor as C
    dest = ruta_seg(e)
    tmp = dest.with_suffix(".tmp.mp4")
    t0 = time.time()
    es = C.Escena(e, FPS)
    tb = time.time() - t0
    ff = _ffmpeg(tmp)
    t1 = time.time()
    for i in range(es.n_frames):
        ff.stdin.write(es.frame(i).tobytes())
    ff.stdin.close()
    ff.wait()
    os.replace(tmp, dest)
    tr = time.time() - t1
    return e["id"], tb, tr, es.n_frames


_ES = None


def _frame_global(i):
    return _ES.frame(i).tobytes()


def render_escena_paralela(e, jobs):
    """Una sola escena repartida en `jobs` procesos por cuadro (para --solo-escena o pocas escenas)."""
    global _ES
    import compositor as C
    dest = ruta_seg(e)
    tmp = dest.with_suffix(".tmp.mp4")
    t0 = time.time()
    _ES = C.Escena(e, FPS)
    tb = time.time() - t0
    ff = _ffmpeg(tmp)
    t1 = time.time()
    with mp.get_context("fork").Pool(jobs) as pool:
        for b in pool.imap(_frame_global, range(_ES.n_frames), chunksize=4):
            ff.stdin.write(b)
    ff.stdin.close()
    ff.wait()
    os.replace(tmp, dest)
    return e["id"], tb, time.time() - t1, _ES.n_frames


def preview_escena(arg):
    e, dirp, tseg = arg
    import cv2
    import compositor as C
    t0 = time.time()
    es = C.Escena(e, FPS)
    tb = time.time() - t0
    t = (e["dur"] * .5) if tseg is None else min(tseg, e["dur"] - .1)
    i = int(t * FPS)
    t1 = time.time()
    f = es.frame(i)
    tf = time.time() - t1
    out = Path(dirp) / f"p{e['parte']}_e{e['id']}_{e['paleta']}.png"
    cv2.imwrite(str(out), f)
    return e["id"], tb, tf, str(out)


# ------------------------------------------------------------------------------------------ SRT y concatenación
def srt_tiempo(t):
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"


def escribir_srt(escenas, dest):
    import compositor as C
    t_ini, n, lineas = 0.0, 1, []
    for e in escenas:
        for a, b, txt in C.calcular_cues(e):
            lineas.append(f"{n}\n{srt_tiempo(t_ini + a)} --> {srt_tiempo(t_ini + b)}\n{txt}\n")
            n += 1
        t_ini += float(e["dur"])
    Path(dest).write_text("\n".join(lineas), encoding="utf-8")


def concatenar(escenas, parte, con_audio=True):
    PARTES.mkdir(parents=True, exist_ok=True)
    lista = PARTES / f"parte{parte}.txt"
    lista.write_text("".join(f"file '{ruta_seg(e)}'\n" for e in escenas))
    dur = sum(float(e["dur"]) for e in escenas)
    dest = PARTES / f"parte{parte}.mp4"
    wav = AUDIO / f"parte{parte}.wav"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lista)]
    if con_audio and wav.exists():
        cmd += ["-i", str(wav), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-af", "apad", "-t", f"{dur:.3f}"]
    else:
        cmd += ["-c:v", "copy", "-an"]
    cmd += ["-movflags", "+faststart", str(dest)]
    subprocess.run(cmd, check=True)
    escribir_srt(escenas, PARTES / f"parte{parte}.srt")
    return dest, wav.exists() and con_audio


# ------------------------------------------------------------------------------------------ principal
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--parte", type=int, help="1..4")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--solo-escena", help="id de una escena (renderiza solo esa; con --preview, un fotograma)")
    ap.add_argument("--preview", metavar="DIR", help="guarda un fotograma por escena en DIR (no renderiza video)")
    ap.add_argument("--t", type=float, default=None, help="segundo de la escena para --preview (por defecto la mitad)")
    ap.add_argument("--escenas", help="archivo de escenas alternativo")
    ap.add_argument("--prueba", action="store_true", help="usar render/escenas_prueba.json")
    ap.add_argument("--rehacer", action="store_true", help="ignorar segmentos ya hechos")
    ap.add_argument("--sin-audio", action="store_true")
    ap.add_argument("--sin-precarga", action="store_true")
    a = ap.parse_args()

    todas, fuente = cargar_escenas(a.escenas, a.prueba)
    if a.solo_escena is not None:
        esc = [e for e in todas if str(e["id"]) == str(a.solo_escena)]
        if not esc:
            raise SystemExit(f"escena {a.solo_escena} no existe")
        parte = esc[0]["parte"]
    else:
        if a.parte is None:
            raise SystemExit("falta --parte N (o --solo-escena ID)")
        parte = a.parte
        esc = [e for e in todas if int(e["parte"]) == parte]
    if not esc:
        raise SystemExit("no hay escenas para esa parte")
    print(f"{len(esc)} escenas de la parte {parte} ({sum(float(e['dur']) for e in esc) / 60:.1f} min) desde {fuente}", flush=True)
    jobs = max(1, a.jobs)
    T0 = time.time()

    if a.preview:
        Path(a.preview).mkdir(parents=True, exist_ok=True)
        if not a.sin_precarga:
            precargar(esc, jobs)
        with mp.Pool(min(jobs, len(esc))) as pool:
            for id_, tb, tf, ruta in pool.imap_unordered(preview_escena, [(e, a.preview, a.t) for e in esc]):
                print(f"  escena {id_}: armado {tb:.1f} s, cuadro {tf:.3f} s -> {ruta}", flush=True)
        print(f"listo en {time.time() - T0:.0f} s")
        return

    SEG.mkdir(parents=True, exist_ok=True)
    # limpiar segmentos viejos de estas escenas (otro hash)
    for e in esc:
        vig = ruta_seg(e)
        for f in SEG.glob(f"p{e['parte']}_e{int(e['id']):03d}_*.mp4" if str(e['id']).isdigit() else f"p{e['parte']}_e{e['id']}_*.mp4"):
            if f != vig:
                f.unlink()
    pend = []
    for e in esc:
        d = ruta_seg(e)
        ok = d.exists() and abs(duracion_video(d) - float(e["dur"])) < .25 and not a.rehacer
        if not ok:
            pend.append(e)
    print(f"{len(esc) - len(pend)} escenas ya hechas, {len(pend)} por renderizar", flush=True)
    stats = []
    if pend:
        if not a.sin_precarga:
            precargar(pend, jobs)
        pend.sort(key=lambda e: -float(e["dur"]))
        if len(pend) < jobs:
            for e in pend:
                r = render_escena_paralela(e, jobs)
                stats.append(r)
                print(f"  escena {r[0]} lista: armado {r[1]:.1f} s, {r[3]} cuadros en {r[2]:.0f} s ({r[2] / r[3]:.3f} s/cuadro con {jobs} procesos)", flush=True)
        else:
            with mp.Pool(jobs) as pool:
                for r in pool.imap_unordered(render_escena, pend):
                    stats.append(r)
                    print(f"  escena {r[0]} lista: armado {r[1]:.1f} s, {r[3]} cuadros en {r[2]:.0f} s "
                          f"({r[2] / r[3]:.3f} s/cuadro de CPU)  [{len(stats)}/{len(pend)}]", flush=True)
    dest, con_a = concatenar(esc, parte, not a.sin_audio)
    nfr = sum(r[3] for r in stats)
    msg = f"listo {dest} ({'con' if con_a else 'sin'} audio) en {time.time() - T0:.0f} s"
    if stats:
        cpu = sum(r[1] + r[2] for r in stats)
        msg += f"\n  CPU medio por cuadro (incluye armado y codificación): {cpu / nfr:.3f} s -> con {jobs} procesos ~{cpu / nfr / jobs:.3f} s/cuadro efectivo"
        msg += f"; 20 min = {20 * 60 * FPS} cuadros ~ {20 * 60 * FPS * cpu / nfr / jobs / 60:.0f} min"
    print(msg)


if __name__ == "__main__":
    main()
