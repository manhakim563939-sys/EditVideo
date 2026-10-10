"""Synthesised soundtrack for kolaj_render.py: upbeat bed (112 BPM) + SFX synced to the edit.

Usage: python3 kolaj_audio.py out.wav
"""
import sys
import wave

import numpy as np

SR = 44100
DUR = 40.0
N = int(SR * DUR)
rng = np.random.default_rng(1)


def t_(d):
    return np.arange(int(SR * d)) / SR


def add(buf, sig, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    sig = sig[: len(buf) - i]
    buf[i:i + len(sig)] += sig * gain


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def nfreq(n):
    return 440 * 2 ** ((n - 69) / 12)


# ---------------------------------------------------------------- instruments
def kick():
    t = t_(0.35)
    f = 50 + 110 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def clap():
    t = t_(0.25)
    n = rng.normal(0, 1, len(t))
    n = n - lowpass(n, 900)
    env = np.exp(-t * 22) * (1 + 0.6 * (np.sin(2 * np.pi * 90 * t) > 0))
    return n * env * 0.5


def hat(open_=False):
    t = t_(0.18 if open_ else 0.05)
    n = rng.normal(0, 1, len(t))
    n = n - lowpass(n, 6000)
    return n * np.exp(-t * (18 if open_ else 80)) * 0.35


def bass(note, d):
    t = t_(d)
    f = nfreq(note)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t)
    return s * np.minimum(1, t * 200) * np.exp(-t * 4)


def pad(notes, d):
    t = t_(d)
    s = np.zeros_like(t)
    for n in notes:
        f = nfreq(n)
        for det in (-0.12, 0.12):
            ph = 2 * np.pi * f * (1 + det / 100) * t
            s += np.sin(ph) + 0.3 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)
    env = np.minimum(1, t / 0.08) * np.minimum(1, (d - t) / 0.15)
    return s * env / (len(notes) * 4)


def pluck(note, d=0.25):
    t = t_(d)
    f = nfreq(note)
    return (np.sin(2 * np.pi * f * t) + 0.2 * np.sin(6 * np.pi * f * t)) * np.exp(-t * 14)


# ---------------------------------------------------------------- SFX
def sfx_pop():
    t = t_(0.12)
    f = 900 * np.exp(-t * 25) + 300
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 35) * 0.6


def sfx_whoosh(d=0.5):
    t = t_(d)
    n = rng.normal(0, 1, len(t))
    out = np.zeros_like(n)
    # sweep a crude band-pass by mixing two low-passes
    seg = 1024
    for i in range(0, len(n), seg):
        u = i / len(n)
        c = 400 + 5000 * np.sin(np.pi * u)
        chunk = n[i:i + seg]
        out[i:i + seg] = lowpass(chunk, c) - lowpass(chunk, c * 0.3)
    return out * np.sin(np.pi * t / d) ** 2 * 1.4


def sfx_stamp():
    t = t_(0.3)
    thud = np.sin(2 * np.pi * np.cumsum(70 + 90 * np.exp(-t * 40)) / SR) * np.exp(-t * 14)
    n = rng.normal(0, 1, len(t)) * np.exp(-t * 40) * 0.4
    return thud + n


def sfx_ding():
    t = t_(1.2)
    s = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(1568, 1), (2350, 0.5), (3136, 0.25)])
    return s * np.exp(-t * 4) * 0.35


def sfx_tick():
    t = t_(0.03)
    return np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 200) * 0.3


def sfx_click():
    t = t_(0.06)
    return rng.normal(0, 1, len(t)) * np.exp(-t * 120) * 0.5


def sfx_riser(d=0.9):
    t = t_(d)
    f = 200 + 900 * (t / d) ** 2
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / d) ** 2 * 0.25


# ---------------------------------------------------------------- arrangement
def main(path):
    music = np.zeros(N)
    duck = np.ones(N)
    bpm = 112
    beat = 60 / bpm
    bar = beat * 4
    # Am  F  C  G  (one chord per bar)
    prog = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [55, 60, 64]), (55, [55, 59, 62])]
    melody = [76, 72, 74, 76, 79, 76, 74, 72]
    nbars = int(DUR / bar) + 1
    for b in range(nbars):
        t0 = b * bar
        root, chord = prog[b % 4]
        intro = b < 1
        outro = t0 >= 39.0
        if outro:
            break
        add(music, pad([n + 12 for n in chord], bar), t0, 0.5)
        for k in range(8):
            tb = t0 + k * beat / 2
            if not intro:
                add(music, bass(root - 12 + (12 if k % 4 == 3 else 0), beat / 2), tb, 0.55)
            add(music, hat(open_=(k % 4 == 2)), tb + (0 if k % 2 == 0 else 0.015), 0.6 if k % 2 else 0.4)
        for k in range(4):
            tb = t0 + k * beat
            if not intro:
                add(music, kick(), tb, 0.9)
                i = int(tb * SR)
                L = int(0.18 * SR)
                if i < N:
                    seg = min(L, N - i)
                    duck[i:i + seg] = np.minimum(duck[i:i + seg], 0.55 + 0.45 * np.arange(seg) / L)
            if k in (1, 3) and not intro:
                add(music, clap(), tb, 0.55)
        if b >= 4 and b % 2 == 0:  # light pluck hook every other bar
            for k, n in enumerate(melody):
                add(music, pluck(n), t0 + k * beat / 2, 0.18)
    music *= duck
    # break before the CTA drop
    i0, i1 = int(34.7 * SR), int(35.0 * SR)
    music[i0:i1] *= np.linspace(1, 0.2, i1 - i0)
    # final chord tail
    add(music, pad([69, 72, 76, 81], 1.6), 38.4, 0.6)

    sfx = np.zeros(N)
    for c in [5.0, 11.0, 16.0, 24.4, 30.0, 35.0]:
        add(sfx, sfx_whoosh(0.5), c - 0.25, 0.5)
    for p in [0.25, 0.7, 2.6, 5.1, 5.3, 5.6, 7.95, 11.2, 13.8, 16.2, 18.45, 19.75, 21.1, 22.5, 24.5, 24.65, 25.15,
              25.65, 24.9, 30.25, 30.4, 31.9, 32.85, 33.95, 35.3, 37.1, 37.7, 38.4, 11.5, 16.1, 35.4, 36.1, 22.6]:
        add(sfx, sfx_pop(), p, 0.45)
    for s in [13.55, 27.3]:
        add(sfx, sfx_stamp(), s, 0.8)
    for k in range(18):  # counter ticks 0 -> 82%
        add(sfx, sfx_tick(), 5.4 + 2.3 * (1 - (1 - k / 18) ** (1 / 3)), 0.6)
    add(sfx, sfx_riser(0.8), 4.2, 0.8)
    add(sfx, sfx_ding(), 7.95, 0.7)
    add(sfx, sfx_ding(), 33.95, 0.8)
    add(sfx, sfx_click(), 38.7, 0.9)
    add(sfx, sfx_ding(), 38.75, 0.6)
    for k in range(10):  # feed scroll flicks
        add(sfx, sfx_click(), 11.1 + k * 0.2, 0.15)

    mix = music * 0.42 + sfx * 0.6
    mix /= max(1.0, np.abs(mix).max() / 0.95)
    fade = np.ones(N)
    L = int(0.4 * SR)
    fade[-L:] = np.linspace(1, 0, L)
    mix *= fade
    data = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
