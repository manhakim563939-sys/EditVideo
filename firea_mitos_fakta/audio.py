"""Procedural game-show soundtrack + SFX for "MITOS atau FAKTA?" (no samples, no commercial music).

120 BPM bouncy pop in G major: G - Em - C - D (1 bar each).
  hook     stamp hits + pad swell
  quizzes  groove (kick, clap, hats, bass, marimba-ish pluck); during each countdown the music
           ducks + low-passes so the ticking clock leads, then the answer lands with stamp + buzzer/ding
  reveal   full groove + bells, final chord rings out
Writes build/audio.wav (48 kHz stereo).
"""
import os
import wave

import numpy as np

import synth
from synth import SR, add, bass, bell, clap, env_adsr, hat, kick, midi, onepole_lp, pad_note, pluck, tvec
from timeline import BEAT, DUR, QUIZ, S, sfx_cues

ROOT = os.path.dirname(os.path.abspath(__file__))
N = int(DUR * SR)
rng = np.random.default_rng(5)
BAR = 4 * BEAT
CHORDS = [(43, [55, 59, 62, 67]), (40, [52, 55, 59, 64]), (36, [48, 52, 55, 60]), (38, [50, 54, 57, 62])]


def sfx(kind):
    if kind == "tick":
        n = int(0.05 * SR)
        t = tvec(n)
        return (np.sin(2 * np.pi * 1250 * t) + 0.5 * np.sin(2 * np.pi * 2900 * t)) * np.exp(-t * 110)
    if kind == "buzzer":  # friendly "eh-eh"
        out = np.zeros(int(0.42 * SR))
        for k in range(2):
            n = int(0.15 * SR)
            t = tvec(n)
            ph = 2 * np.pi * 185 * t
            x = np.tanh(3 * (np.sin(ph) + 0.5 * np.sin(2 * ph + 0.3) + 0.3 * np.sin(3 * ph)))
            x = onepole_lp(x * env_adsr(n, 0.005, 0.02, 0.9, 0.03), 1800)
            i = int(k * 0.2 * SR)
            out[i:i + n] += x
        return out * 0.7
    if kind == "ding":
        out = np.zeros(int(1.0 * SR))
        for k, m in enumerate((84, 91)):
            b = bell(midi(m), 0.9)
            i = int(k * 0.09 * SR)
            out[i:i + len(b)] += b[: len(out) - i]
        return out * 0.6
    if kind in ("stamp", "stamp_soft"):
        n = int(0.35 * SR)
        t = tvec(n)
        f = 55 + 120 * np.exp(-t * 35)
        thud = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14)
        slap = onepole_lp(rng.normal(0, 1, n), 3500) * np.exp(-t * 60)
        x = thud + 0.9 * slap
        return x * (0.55 if kind == "stamp_soft" else 1.0)
    if kind == "swipe":
        return synth.sfx("swish") * 1.2
    return synth.sfx(kind)


def build():
    L, R, drums, fx = np.zeros(N), np.zeros(N), np.zeros(N), np.zeros(N)
    names = sorted(S, key=S.get)

    def section(t):
        return [n for n in names if S[n] <= t + 1e-6][-1]

    nb = int(np.ceil(DUR / BAR))
    for b in range(nb):
        t0 = b * BAR
        root, tones = CHORDS[b % 4] if b < nb - 1 else CHORDS[0]
        for k, m in enumerate(tones):
            p = pad_note(midi(m), BAR + 0.5) * 0.06
            add(L if k % 2 else R, t0, p)
            add(R if k % 2 else L, t0, p * 0.6)
        # marimba-ish pluck: syncopated 8ths
        pat = [0, None, 2, 1, None, 3, 2, 1]
        for i, idx in enumerate(pat):
            ts = t0 + i * BEAT / 2
            if idx is None or ts >= DUR - 0.8 or section(ts) == "hook":
                continue
            pl = pluck(midi(tones[idx] + 12), 0.35) * 0.11
            add(L, ts, pl * (1.0 if i % 2 else 0.75))
            add(R, ts + 0.01, pl * (0.75 if i % 2 else 1.0))
        for off in (0, 1.5, 2.5, 3):
            ts = t0 + off * BEAT
            if ts < S["q1"] - 0.01 or ts >= DUR - 0.6:
                continue
            bl = bass(midi(root), BEAT * (0.9 if off == 0 else 0.4)) * 0.24
            add(L, ts, bl)
            add(R, ts, bl)
        for beat in range(4):
            ts = t0 + beat * BEAT
            if ts >= DUR - 0.6 or section(ts) == "hook":
                continue
            add(drums, ts, kick() * 0.5)
            if beat in (1, 3):
                add(drums, ts, clap() * 0.28)
            add(drums, ts + BEAT / 2, hat(beat == 3) * 0.09)
    add(L, DUR - 2.0, bell(midi(79), 2.0) * 0.12)
    add(R, DUR - 1.98, bell(midi(83), 2.0) * 0.10)

    # duck + filter music during each countdown so the clock ticks lead
    duck = np.ones(N)
    lp = np.full(N, 12000.0)
    for q, d in QUIZ.items():
        a, b = S[q] + d["count"], S[q] + d["ans"]
        ia, ib = int(a * SR), int(b * SR)
        r = int(0.12 * SR)
        duck[ia:ib] = 0.45
        duck[ia - r:ia] = np.linspace(1, 0.45, r)
        duck[ib:ib + r] = np.linspace(0.45, 1, r)
        lp[ia:ib] = 1200
    L = onepole_lp(L, lp) * duck
    R = onepole_lp(R, lp) * duck
    drums = onepole_lp(drums, lp) * duck

    for t, kind, g in sfx_cues():
        add(fx, max(0.0, t), sfx(kind) * g * 0.6)

    fade = np.ones(N)
    fo = int(0.6 * SR)
    fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
    st = np.stack([(L + drums + fx) * fade, (R + drums + fx) * fade], 1)
    st = np.tanh(st * 1.1) / np.tanh(1.1)
    st *= 10 ** (-4.8 / 20) / np.abs(st).max()  # true peak < -1 dBTP
    return st


def main():
    st = build()
    os.makedirs(f"{ROOT}/build", exist_ok=True)
    out = f"{ROOT}/build/audio.wav"
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())
    print("wrote", out)


if __name__ == "__main__":
    main()
