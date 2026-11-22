#!/usr/bin/env python3
"""Corre la campana completa con el bot y escribe log + informe.

Uso: python3 -I ejecutar.py [--semilla N] [--salida DIR] [--detalle] [--max-dias N] [--post-dias N]
"""
import argparse
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import bot as botmod  # noqa: E402
import motor  # noqa: E402
import mundo  # noqa: E402


def partir_log(lineas, salida, max_palabras=1800):
    for viejo in salida.glob("CAMPANA_LOG_*.md"):
        viejo.unlink()
    partes, actual, pal = [], [], 0
    for ln in lineas:
        w = len(ln.split())
        if actual and pal + w > max_palabras:
            partes.append(actual)
            actual, pal = [], 0
        actual.append(ln)
        pal += w
    if actual:
        partes.append(actual)
    for i, p in enumerate(partes, 1):
        enc = f"<!-- CAMPAÑA parte {i}/{len(partes)} -->\n# Registro de la campaña (simulación), parte {i}\n\n"
        (salida / f"CAMPANA_LOG_{i:02d}.md").write_text(enc + "\n".join(f"- {x}" for x in p) + "\n", encoding="utf-8")
    return len(partes)


def informe(s, b, dia_fin, args):
    c = s.contadores
    q_p = [q for q, e in s.quests.items() if q.startswith("M") and e == "hecha"]
    q_s = [q for q, e in s.quests.items() if q.startswith("S") and e == "hecha"]
    pendientes = [q for q, e in s.quests.items() if e != "hecha"]
    vivos = sum(1 for L in s.locs.values() for g in L["grupos"] for e in g["miembros"] if e["hp"] > 0)
    # invariante de persistencia de enemigos
    total = c.get("enemigos_creados", 0)
    cuenta = c.get("kills", 0) + c.get("muertes_por_otra_criatura", 0) + vivos
    ok_pers = total == cuenta
    L = []
    L.append(f"# Informe de prueba (semilla {args.semilla})\n")
    L.append("Simulación en código de las reglas de los bloques 03-39 sobre el mundo «El Salar». "
             "Prueba las reglas, no cómo las interpreta una IA concreta.\n")
    L.append("## Resultado")
    L.append(f"- Campaña completa: **{'sí, día ' + str(dia_fin) if dia_fin else 'NO'}** · día final {s.dia()} · nivel final {s.p['nivel']} · nivel al completar la campaña: {getattr(b, 'nivel_fin', '?')}")
    L.append(f"- Misiones principales: {len(q_p)}/8 · secundarias: {len(q_s)}/20 · pendientes: {pendientes or 'ninguna'}")
    L.append(f"- Ubicaciones descubiertas: {sum(1 for x in s.locs.values() if x['descubierta'])}/{len(s.locs)} · visitadas: {sum(1 for x in s.locs.values() if x['visitada'])}")
    L.append(f"- Contenedores registrados: {c.get('contenedores_abiertos', 0)} · búsquedas generales: {c.get('busquedas', 0)} · conexiones ocultas: {c.get('conexiones_ocultas', 0)}")
    L.append(f"- Combates ganados: {c.get('combates_ganados', 0)} (rondas promedio {c.get('rondas_total', 0) / max(1, c.get('combates_ganados', 1)):.1f}) · perdidos: {c.get('combates_perdidos', 0)} · escapes: {c.get('escapes', 0)}")
    L.append(f"- Enemigos derrotados: {c.get('kills', 0)} · jefes: {c.get('jefes_derrotados', 0)}/4 · invocaciones de jefe: {c.get('invocaciones', 0)}")
    L.append(f"- Precisión en combate: {c.get('aciertos', 0)}/{c.get('ataques', 0)} = {100 * c.get('aciertos', 0) / max(1, c.get('ataques', 1)):.0f}% de aciertos · críticos {c.get('criticos', 0)}")
    L.append(f"- Derrotas (sin muerte): {c.get('derrotas', 0)} · robos sufridos {c.get('robos_sufridos', 0)} · robos recuperados {c.get('robos_recuperados', 0)} · robos en arrastre {c.get('robos_en_arrastre', 0)}")
    L.append(f"- Atascos en ventana: {c.get('atascos', 0)} de {c.get('atascos_tiradas', 0)} intentos · robos por atasco {c.get('robos_por_atasco', 0)}")
    L.append(f"- Viajes rápidos: {c.get('viajes_rapidos', 0)} · emboscadas por mapa abierto: {c.get('emboscadas_mapa', 0)} · tramos recorridos {c.get('tramos', 0)}")
    L.append(f"- Choques entre especies: {c.get('choques_entre_especies', 0)} · enemigos muertos por otra criatura: {c.get('muertes_por_otra_criatura', 0)} · regeneraciones de población: {c.get('regeneraciones', 0)}")
    L.append(f"- Comercio: compras {c.get('compras', 0)} · ventas {c.get('ventas', 0)} · armas compradas {c.get('armas_compradas', 0)} · reparaciones {c.get('reparaciones', 0)} · fabricaciones {c.get('fabricaciones', 0)}")
    L.append(f"- Conversaciones: {c.get('conversaciones', 0)} · compañeros reclutados: {c.get('companeros', 0)} · bandos elegidos: {c.get('bandos_elegidos', 0)}")
    L.append(f"- Hackeos OK/fallidos: {c.get('hackeos_ok', 0)}/{c.get('hackeos_fallidos', 0)} · trampas activadas {c.get('trampas_activadas', 0)} · ganzúas rotas {c.get('ganzuas_rotas', 0)}")
    L.append(f"- **Persistencia de enemigos:** creados {total} = muertos por el jugador {c.get('kills', 0)} + por otra criatura {c.get('muertes_por_otra_criatura', 0)} + vivos {vivos} → {'OK, ninguno despawneó' if ok_pers else 'ERROR: ' + str(total - cuenta) + ' enemigos desaparecieron'}")
    L.append("")
    L.append("## Nivel por día")
    L.append("| Nivel | Día | Enemigos derrotados hasta ahí |")
    L.append("|---|---|---|")
    for n, d, k in s.hist_niv:
        L.append(f"| {n} | {d} | {k} |")
    L.append("")
    L.append("## Problemas de reglas detectados por el simulador")
    if s.violaciones:
        for v in sorted(set(s.violaciones)):
            L.append(f"- {v} (×{s.violaciones.count(v)})")
    else:
        L.append("- Ninguno en esta corrida.")
    L.append("")
    return "\n".join(L), ok_pers


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semilla", type=int, default=1)
    ap.add_argument("--salida", default=str(AQUI.parent / "simulacion"))
    ap.add_argument("--detalle", action="store_true")
    ap.add_argument("--max-dias", type=int, default=900)
    ap.add_argument("--post-dias", type=int, default=150)
    ap.add_argument("--sin-escribir", action="store_true")
    args = ap.parse_args()
    s = motor.Sim(semilla=args.semilla, detalle=args.detalle)
    b = botmod.Bot(s)
    dia_fin = b.jugar(max_dias=args.max_dias, post_dias=args.post_dias)
    texto, ok = informe(s, b, dia_fin, args)
    print(texto)
    if not args.sin_escribir:
        salida = Path(args.salida)
        salida.mkdir(parents=True, exist_ok=True)
        n = partir_log(s.log, salida)
        (salida / "INFORME_DE_PRUEBA.md").write_text(texto, encoding="utf-8")
        print(f"\nLog: {len(s.log)} líneas en {n} archivos -> {salida}")
    return 0 if (dia_fin and ok) else 1


if __name__ == "__main__":
    sys.exit(main())
