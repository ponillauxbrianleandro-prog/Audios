#!/usr/bin/env python3
"""Corre la campana con varias semillas y resume resultados (robustez de las reglas).

Uso: python3 -I varias_semillas.py [--n 10] [--salida DIR]
"""
import statistics
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import bot as botmod  # noqa: E402
import motor  # noqa: E402


def una(semilla):
    s = motor.Sim(semilla=semilla)
    b = botmod.Bot(s)
    dia = b.jugar(max_dias=900, post_dias=150)
    c = s.contadores
    vivos = sum(1 for L in s.locs.values() for g in L["grupos"] for e in g["miembros"] if e["hp"] > 0)
    pers = c.get("enemigos_creados", 0) == c.get("kills", 0) + c.get("muertes_por_otra_criatura", 0) + vivos
    return dict(semilla=semilla, completa=bool(dia), dia=dia or 0, nivel_fin=getattr(b, "nivel_fin", 0), nivel=s.p["nivel"],
                prin=sum(1 for q, e in s.quests.items() if q.startswith("M") and e == "hecha"),
                sec=sum(1 for q, e in s.quests.items() if q.startswith("S") and e == "hecha"),
                derr=c.get("derrotas", 0), robos=c.get("robos_sufridos", 0), recup=c.get("robos_recuperados", 0),
                kills=c.get("kills", 0), pers=pers, viol=len(s.violaciones), atascos=c.get("atascos", 0),
                emb=c.get("emboscadas_mapa", 0))


def main():
    n = 10
    if "--n" in sys.argv:
        n = int(sys.argv[sys.argv.index("--n") + 1])
    salida = AQUI.parent / "simulacion"
    if "--salida" in sys.argv:
        salida = Path(sys.argv[sys.argv.index("--salida") + 1])
    filas = [una(i) for i in range(1, n + 1)]
    L = ["# Resumen de varias semillas", "",
         f"{n} campañas completas con semillas distintas (150 días de juego posterior a la campaña).", "",
         "| Semilla | ¿Completa? | Día fin | Nivel al terminar / final | Principales | Secundarias | Derrotas | Robos (recup.) | Enemigos | Persistencia | Problemas bot |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for f in filas:
        L.append(f"| {f['semilla']} | {'sí' if f['completa'] else 'NO'} | {f['dia']} | {f['nivel_fin']} / {f['nivel']} | {f['prin']}/8 | {f['sec']}/20 | "
                 f"{f['derr']} | {f['robos']} ({f['recup']}) | {f['kills']} | {'OK' if f['pers'] else 'ERROR'} | {f['viol']} |")
    ok = [f for f in filas if f["completa"]]
    L += ["", "## Promedios",
          f"- Campañas completadas: {len(ok)}/{n}",
          f"- Día de finalización: {statistics.mean(f['dia'] for f in ok):.0f} (mín. {min(f['dia'] for f in ok)}, máx. {max(f['dia'] for f in ok)})" if ok else "- Ninguna completó",
          f"- Nivel al completar la campaña: {statistics.mean(f['nivel_fin'] for f in ok):.1f}" if ok else "",
          f"- Derrotas por partida: {statistics.mean(f['derr'] for f in filas):.1f}",
          f"- Persistencia de enemigos correcta en {sum(1 for f in filas if f['pers'])}/{n}",
          f"- Atascos en ventana por partida: {statistics.mean(f['atascos'] for f in filas):.1f} · emboscadas por mapa grande: {statistics.mean(f['emb'] for f in filas):.1f}"]
    texto = "\n".join(L) + "\n"
    print(texto)
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "RESUMEN_VARIAS_SEMILLAS.md").write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    main()
