#!/usr/bin/env python3
"""Calibra PV/daño de enemigos y daño del jugador por nivel (bloque 27).

Para cada nivel arma un jugador con el equipo habitual de ese nivel y lo enfrenta a grupos de una
sola especie del pool del lugar. Mide victorias, PV perdido y rondas. Objetivo: ganar >=90%,
perder 35-65% de los PV, 6-14 rondas.
"""
import statistics
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import bot as botmod  # noqa: E402
import motor  # noqa: E402
import mundo  # noqa: E402


def equipo(nivel):
    arma = min(4, 1 + nivel // 5)
    armadura = 2 if nivel < 8 else 4
    return arma, armadura


def duelos(nivel, n=60, semilla=7, pool="desierto"):
    res = []
    for i in range(n):
        s = motor.Sim(semilla + i)
        b = botmod.Bot(s)
        p = s.p
        p["nivel"] = nivel
        p["arma"], p["armadura"] = equipo(nivel)
        p["dur"] = 100
        p["hp"] = s.hpmax()
        p["inv"] = {"venda": 5, "medicina": 1}
        p["comps"] = ["K-1"]
        lid = "L-005"
        mundo.LOCS[lid]["pool"] = pool
        mundo.LOCS[lid]["nivel"] = nivel
        p["loc"] = lid
        g = s.generar_grupo(lid)
        if not g:
            continue
        hp0 = p["hp"]
        r = s.combate(g["miembros"], sorpresa=False, policy=b.policy)
        res.append((r, 1 - p["hp"] / hp0, s.contadores.get("rondas_total", 0), len(g["miembros"])))
    return res


def main():
    print("nivel | victorias | PV perdido (media) | rondas (media) | enemigos")
    for nivel in (1, 3, 5, 8, 10, 12, 15, 18, 20, 25, 30):
        for pool in ("desierto", "insectos", "saqueadores"):
            r = duelos(nivel, 40, pool=pool)
            if not r:
                continue
            vic = sum(1 for x in r if x[0] == "victoria") / len(r)
            perd = statistics.mean(x[1] for x in r if x[0] == "victoria") if any(x[0] == "victoria" for x in r) else 1
            rond = statistics.mean(x[2] for x in r)
            cant = statistics.mean(x[3] for x in r)
            print(f"{nivel:>5} {pool:12s} | {vic*100:5.0f}% | {perd*100:5.0f}% | {rond:5.1f} | {cant:.1f}")


if __name__ == "__main__":
    main()
