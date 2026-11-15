#!/usr/bin/env python3
"""«Lo que el barro recuerda» — tango instrumental original para el documental.

Re menor, 4x8 marcato con síncopas 3-3-2, forma A A B A C A + coda (chan-chan).
Cuarteto sintetizado por código: bandoneón, violín, piano y contrabajo.

Genera en esta carpeta:
  tango.mid              partitura MIDI (una pista por instrumento)
  tango.mp3              mezcla estéreo
  stems/<instrumento>.mp3  pistas separadas, para remezclar bajo la narración
Los WAV intermedios se crean en wav/ (no se versionan).

Uso: python3 generar_tango.py     (requiere numpy, scipy y ffmpeg)
"""
import struct
import subprocess
import wave
from pathlib import Path

import numpy as np
from scipy.signal import fftconvolve

SR = 44100
BPM = 118.0
BEAT = 60.0 / BPM
AQUI = Path(__file__).resolve().parent

N = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "Ab": 8,
     "A": 9, "A#": 10, "Bb": 10, "B": 11}


def m(name):
    return 12 * (int(name[-1]) + 1) + N[name[:-1]]


CH = {  # acorde: (bajo, quinta del bajo, voces del piano)
    "Dm": ("D2", "A2", ["A3", "D4", "F4"]), "Gm": ("G2", "D3", ["Bb3", "D4", "G4"]),
    "Em7b5": ("E2", "Bb2", ["G3", "Bb3", "D4", "E4"]), "A7": ("A2", "E3", ["G3", "C#4", "E4"]),
    "F": ("F2", "C3", ["A3", "C4", "F4"]), "C7": ("C2", "G2", ["Bb3", "E4", "G4"]),
    "E7": ("E2", "B2", ["G#3", "B3", "D4"]), "D": ("D2", "A2", ["A3", "D4", "F#4"]),
    "Em": ("E2", "B2", ["G3", "B3", "E4"]),
}

# melodías: por compás, lista de (nota | None, duración en tiempos)
A1 = [
    [(None, .5), ("A4", .5), ("D5", .5), ("F5", .5), ("E5", .5), ("D5", .5), ("A4", 1)],
    [("F5", 1.5), ("E5", .5), ("D5", 1), (None, 1)],
    [(None, .5), ("Bb4", .5), ("D5", .5), ("G5", .5), ("F5", .5), ("D5", .5), ("Bb4", 1)],
    [("A4", 1.5), ("D5", .5), ("F5", 2)],
    [(None, .5), ("G5", .5), ("E5", .5), ("Bb4", .5), ("G5", .5), ("E5", .5), ("Bb4", 1)],
    [("A4", .5), ("C#5", .5), ("E5", .5), ("G5", .5), ("F5", .5), ("E5", .5), ("C#5", 1)],
    [("D5", 1), ("F5", .5), ("A5", 1.5), ("G5", .5), ("F5", .5)],
]
A_OPEN = A1 + [[("E5", 1.5), ("C#5", .5), ("A4", 2)]]
A_CLOSE = A1 + [[("D5", 3), (None, 1)]]
A_CH_OPEN = ["Dm", "Dm", "Gm", "Dm", "Em7b5", "A7", "Dm", "A7"]
A_CH_CLOSE = ["Dm", "Dm", "Gm", "Dm", "Em7b5", "A7", "A7", "Dm"]
A_CLOSE[6] = [("E5", 1), ("G5", .5), ("C#5", 1.5), ("E5", .5), ("C#5", .5)]

B = [
    [("C5", 2), ("A4", 1), ("C5", 1)], [("Bb4", 1.5), ("C5", .5), ("E5", 2)],
    [("F5", 2), ("A5", 1), ("G5", .5), ("F5", .5)], [("E5", 3), ("C#5", 1)],
    [("D5", 1.5), ("F5", .5), ("A5", 2)], [("G5", 1), ("Bb5", 1), ("A5", 1), ("G5", 1)],
    [("E5", 1), ("G#5", 1), ("B5", 2)], [("A5", 2), ("E5", 1), ("C#5", 1)],
]
B_CH = ["F", "C7", "F", "A7", "Dm", "Gm", "E7", "A7"]

C = [
    [("F#5", .5), ("A5", .5), ("D6", 1), ("A5", .5), ("F#5", .5), ("D5", 1)], [("F#5", 1.5), ("E5", .5), ("D5", 2)],
    [("E5", .5), ("G5", .5), ("C#6", 1), ("G5", .5), ("E5", .5), ("C#5", 1)], [("E5", 1.5), ("F#5", .5), ("G5", 2)],
    [("G5", 1), ("B5", 1), ("E5", 2)], [("G5", 1), ("E5", 1), ("C#5", 2)],
    [("D5", .5), ("F#5", .5), ("A5", .5), ("D6", .5), ("F#6", 2)], [("E6", 1), ("C#6", 1), ("A5", 2)],
]
C_CH = ["D", "D", "A7", "A7", "Em", "A7", "D", "A7"]

# forma: (melodía, acordes, quién lleva la voz, carácter)
FORM = [
    ("intro", None, ["Dm", "A7"], None),
    ("A", A_OPEN, A_CH_OPEN, "bando"), ("A", A_CLOSE, A_CH_CLOSE, "bando+vn"),
    ("B", B, B_CH, "violin"),
    ("A", A_CLOSE, A_CH_CLOSE, "bando"),
    ("C", C, C_CH, "bando+vn"),
    ("A", A_OPEN, A_CH_OPEN, "violin"), ("A", A_CLOSE, A_CH_CLOSE, "tutti"),
]
SINCOPA = {2, 5}      # compases (dentro de cada sección) con acompañamiento 3-3-2


def score():
    """Devuelve {instrumento: [(midi, inicio_s, dur_s, vel)]} y la duración total."""
    ev = {"bandoneon": [], "violin": [], "piano": [], "contrabajo": []}
    bar = 0

    def add(inst, note, beat, dur, vel):
        ev[inst].append((m(note) if isinstance(note, str) else note, (bar * 4 + beat) * BEAT, dur * BEAT, vel))

    for name, mel, chords, lead in FORM:
        for i, ch in enumerate(chords):
            root, fifth, voic = CH[ch]
            nxt = CH[chords[(i + 1) % len(chords)]][0]
            if name == "intro":
                for b in range(4):
                    for v in voic:
                        add("piano", v, b, .3, 78 if b % 2 == 0 else 62)
                    add("contrabajo", root if b % 2 == 0 else fifth, b, .8, 84)
                    add("bandoneon", voic[-1], b, .3, 60)
                    add("bandoneon", voic[0], b, .3, 55)
            elif i in SINCOPA:
                for b, d, v in ((0, .45, 96), (1.5, .45, 84), (3, .5, 90)):          # 3-3-2
                    for x in voic:
                        add("piano", x, b, d, v - 12)
                    add("piano", m(root) + 12, b, d, v - 6)
                    add("contrabajo", root if b != 1.5 else fifth, b, 1.0, v)
            else:
                for b in range(4):                                                    # marcato en cuatro
                    acc = 92 if b in (0, 2) else 74
                    for x in voic:
                        add("piano", x, b, .28, acc - 14)
                    add("piano", m(root if b % 2 == 0 else fifth) + 12, b, .3, acc - 8)
                    bn = root if b == 0 else fifth if b == 2 else (root if b == 1 else None)
                    if b == 3:                                                        # nota de paso hacia el próximo bajo
                        bn = m(nxt) - 1 if m(nxt) > m(root) else m(nxt) + 2
                    add("contrabajo", bn, b, .85, acc)
            if mel is not None:
                t = 0.0
                for note, d in mel[i]:
                    if note:
                        stac = d <= .5
                        if lead in ("bando", "bando+vn", "tutti"):
                            add("bandoneon", note, t, d * (.62 if stac else .95), 96 if t % 2 == 0 else 84)
                            if name == "C" or lead == "tutti":
                                add("bandoneon", m(note) - 12, t, d * (.62 if stac else .95), 70)
                        if lead == "violin":
                            add("violin", note, t, d * .98, 92)
                            if not stac:
                                add("bandoneon", CH[ch][2][-1], t, d * .9, 48)
                                add("bandoneon", CH[ch][2][1], t, d * .9, 46)
                        if lead in ("bando+vn", "tutti") and not stac:
                            add("violin", m(note) + (12 if lead == "tutti" else -3 if m(note) % 12 in (2, 5, 9) else -4), t, d * .98, 66)
                    t += d
            bar += 1
    # coda: chan-chan
    root, fifth, voic = CH["A7"]
    for inst_v in voic:
        add("piano", inst_v, 0, .5, 108)
        add("bandoneon", inst_v, 0, .5, 104)
    add("contrabajo", root, 0, .6, 108)
    add("violin", "A5", 0, .5, 100)
    root, fifth, voic = CH["Dm"]
    for inst_v in voic:
        add("piano", inst_v, 1, 1.4, 70)
        add("bandoneon", inst_v, 1, 1.2, 62)
    add("contrabajo", root, 1, 1.6, 74)
    add("violin", "D5", 1, 1.2, 62)
    bar += 1
    return ev, bar * 4 * BEAT + 2.5


def hz(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def tone(inst, note, dur, vel):
    f = hz(note)
    g = (vel / 127.0) ** 1.6
    if inst == "piano":
        n = int((dur + 1.4) * SR)
        t = np.arange(n) / SR
        out = np.zeros(n)
        for k in range(1, 14):
            fk = f * k * np.sqrt(1 + 0.0004 * k * k)
            if fk > SR / 2.2:
                break
            out += np.sin(2 * np.pi * fk * t + k) * (1.0 / k ** 1.25) * np.exp(-t * (2.2 + 0.9 * k) * (0.6 + f / 500))
        env = np.minimum(1, t / 0.004) * np.where(t > dur, np.exp(-(t - dur) * 14), 1)
        return out * env * g * 0.36
    if inst == "contrabajo":
        n = int((dur + 0.5) * SR)
        t = np.arange(n) / SR
        out = sum(np.sin(2 * np.pi * f * k * t) * a for k, a in ((1, 1), (2, .55), (3, .28), (4, .12), (5, .06)))
        env = np.minimum(1, t / 0.012) * np.exp(-t * 2.6) * np.where(t > dur, np.exp(-(t - dur) * 18), 1)
        thump = np.exp(-t * 90) * np.sin(2 * np.pi * 95 * t) * 0.35
        return (out * env + thump) * g * 0.80
    if inst == "violin":
        n = int((dur + 0.25) * SR)
        t = np.arange(n) / SR
        vib = 1 + 0.006 * np.sin(2 * np.pi * 5.6 * t) * np.minimum(1, t / 0.25)
        ph = 2 * np.pi * np.cumsum(f * vib) / SR
        out = np.zeros(n)
        for k in range(1, 22):
            if f * k > SR / 2.3:
                break
            body = 1.0 + 1.6 * np.exp(-((f * k - 2700) / 900) ** 2) + 0.8 * np.exp(-((f * k - 500) / 250) ** 2)
            out += np.sin(k * ph) * body / k
        env = np.minimum(1, t / 0.07) * np.where(t > dur, np.exp(-(t - dur) * 16), 1) * (0.85 + 0.15 * np.sin(np.pi * np.minimum(t / max(dur, .1), 1)))
        return out * env * g * 0.20
    # bandoneón: dos lengüetas a la octava, ataque de fuelle
    n = int((dur + 0.18) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for det, octv, lvl in ((1.000, 1, 1.0), (1.003, 2, 0.55)):
        ff = f * octv * det
        for k in range(1, 26):
            if ff * k > SR / 2.3:
                break
            out += np.sin(2 * np.pi * ff * k * t + 0.7 * k) * lvl * (1.0 if k % 2 else 0.6) / k ** 0.95 * np.exp(-ff * k / 5200)
    env = (np.minimum(1, t / 0.018) ** 0.7) * (1 + 0.35 * np.exp(-t * 22)) * np.where(t > dur, np.exp(-(t - dur) * 40), 1)
    return out * env * g * 0.27


def render(ev, total):
    n = int(total * SR)
    stems = {}
    rng = np.random.default_rng(3)
    for inst, notes in ev.items():
        buf = np.zeros(n + SR * 3)
        for note, t0, dur, vel in notes:
            human = rng.normal(0, 0.006)
            x = tone(inst, note, dur, vel * rng.uniform(0.94, 1.04))
            i = max(0, int((t0 + human) * SR))
            buf[i:i + len(x)] += x[:len(buf) - i]
        stems[inst] = buf[:n]
    # sala: reverberación breve
    t = np.arange(int(1.7 * SR)) / SR
    ir = [rng.normal(0, 1, len(t)) * np.exp(-t * 3.6) for _ in range(2)]
    pan = {"bandoneon": -0.25, "violin": 0.35, "piano": 0.15, "contrabajo": -0.05}
    out = {}
    for inst, x in stems.items():
        p = pan[inst]
        L, R = x * np.sqrt(0.5 * (1 - p)), x * np.sqrt(0.5 * (1 + p))
        wet = 0.022 if inst != "contrabajo" else 0.008
        L = L + fftconvolve(x, ir[0])[:n] * wet
        R = R + fftconvolve(x, ir[1])[:n] * wet
        out[inst] = np.stack([L, R], 1)
    mix = sum(out.values())
    k = 0.89 / np.abs(mix).max()
    return {i: v * k for i, v in out.items()}, mix * k


def write_wav(path, x):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


def write_midi(path, ev):
    tpq = 480
    prog = {"bandoneon": 23, "violin": 40, "piano": 0, "contrabajo": 32}

    def vlq(v):
        b = [v & 0x7F]
        v >>= 7
        while v:
            b.append((v & 0x7F) | 0x80)
            v >>= 7
        return bytes(reversed(b))

    def track(events):
        data, last = b"", 0
        for tick, msg in sorted(events, key=lambda e: (e[0], e[1][0] & 0xF0 == 0x90)):
            data += vlq(tick - last) + msg
            last = tick
        data += b"\x00\xff\x2f\x00"
        return b"MTrk" + struct.pack(">I", len(data)) + data

    tempo = int(60e6 / BPM)
    name = "Lo que el barro recuerda".encode()
    tracks = [track([(0, b"\xff\x51\x03" + struct.pack(">I", tempo)[1:]), (0, b"\xff\x58\x04\x04\x02\x18\x08"),
                     (0, b"\xff\x03" + bytes([len(name)]) + name)])]
    for ch, (inst, notes) in enumerate(ev.items()):
        e = [(0, bytes([0xC0 | ch, prog[inst]])), (0, b"\xff\x03" + bytes([len(inst)]) + inst.encode())]
        for note, t0, dur, vel in notes:
            a = int(round(t0 / BEAT * tpq))
            b = int(round((t0 + dur) / BEAT * tpq))
            e.append((a, bytes([0x90 | ch, note, int(min(127, vel))])))
            e.append((max(b, a + 1), bytes([0x80 | ch, note, 0])))
        tracks.append(track(e))
    with open(path, "wb") as fh:
        fh.write(b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), tpq) + b"".join(tracks))


def main():
    ev, total = score()
    write_midi(AQUI / "tango.mid", ev)
    stems, mix = render(ev, total)
    (AQUI / "wav").mkdir(exist_ok=True)
    (AQUI / "stems").mkdir(exist_ok=True)
    jobs = [("tango", mix, AQUI / "tango.mp3")] + [(i, x, AQUI / "stems" / f"{i}.mp3") for i, x in stems.items()]
    for name, x, mp3 in jobs:
        wav = AQUI / "wav" / f"{name}.wav"
        write_wav(wav, x)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-c:a", "libmp3lame", "-b:a", "192k", str(mp3)], check=True)
    print(f"duración: {total:.1f} s, pico de la mezcla: {np.abs(mix).max():.2f}")


if __name__ == "__main__":
    main()
