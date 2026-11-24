#!/usr/bin/env python3
"""Genera SRT por parte y total desde ../escenas.json.

Uso: python3 render/srt.py [salida_dir]   (por defecto render/subtitulos/)
Subtitulos: <=2 lineas de ~34 caracteres; tiempos acumulados correctos.
"""
import json, os, re, sys, textwrap

QUI = os.path.dirname(os.path.abspath(__file__))
ESC = os.path.join(QUI, '..', 'escenas.json')
MAXC, PPS = 34, 2.5


def tc(t):
    t = max(0.0, t)
    ms = int(round(t * 1000))
    return '%02d:%02d:%02d,%03d' % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)


def cues_de_frase(texto, t0, t1):
    """Parte la frase en cues de <=2 lineas x MAXC, repartiendo el tiempo por caracteres."""
    lineas = textwrap.wrap(texto.replace('\n', ' '), MAXC, break_long_words=False) or ['']
    grupos = [lineas[i:i + 2] for i in range(0, len(lineas), 2)]
    pesos = [sum(len(l) for l in g) + 6 for g in grupos]
    tot = float(sum(pesos)); out = []; t = t0
    for g, p in zip(grupos, pesos):
        d = (t1 - t0) * p / tot
        out.append((t, t + d, '\n'.join(g))); t += d
    return out


def construir(escenas):
    """Devuelve {parte: [(ini,fin,texto)...]} con tiempos relativos a la parte, y la lista total."""
    por_parte, total, acum_t, acum_p = {}, [], 0.0, {}
    for e in escenas:
        p = e['parte']; off_p = acum_p.get(p, 0.0)
        nar = e.get('narracion', [])
        for i, n in enumerate(nar):
            ini = n['t']
            dur = len(re.findall(r'\w+', n['texto'])) / PPS
            lim = nar[i + 1]['t'] - 0.15 if i + 1 < len(nar) else e['dur'] - 0.1
            fin = min(ini + dur + 0.4, lim)
            if fin <= ini: fin = ini + 0.5
            for a, b, tx in cues_de_frase(n['texto'], ini, fin):
                por_parte.setdefault(p, []).append((off_p + a, off_p + b, tx))
                total.append((acum_t + a, acum_t + b, tx))
        acum_t += e['dur']; acum_p[p] = off_p + e['dur']
    return por_parte, total


def escribir(ruta, cues):
    with open(ruta, 'w', encoding='utf-8') as f:
        for i, (a, b, tx) in enumerate(cues, 1):
            f.write('%d\n%s --> %s\n%s\n\n' % (i, tc(a), tc(b), tx))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(QUI, 'subtitulos')
    os.makedirs(out, exist_ok=True)
    escenas = json.load(open(ESC, encoding='utf-8'))
    por_parte, total = construir(escenas)
    for p, c in sorted(por_parte.items()):
        escribir(os.path.join(out, 'parte%d.srt' % p), c)
    escribir(os.path.join(out, 'total.srt'), total)
    print('SRT escritos en', out, '| cues total:', len(total),
          '| duracion total: %.1f s' % sum(e['dur'] for e in escenas))


if __name__ == '__main__':
    main()
