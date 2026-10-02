"""Synthesise the paper-collage sound effects listed in <workdir>/sfx.json into a WAV.

Usage: python3 sfx_mix.py <workdir> <duration_seconds> <out.wav>
"""
import json
import sys
import wave

import numpy as np

SR = 48000
rng = np.random.default_rng(1)


def env(n, attack, decay):
    t = np.arange(n) / SR
    return np.minimum(1, t / attack) * np.exp(-t / decay)


def pop():
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    f = 900 * np.exp(-t * 30) + 380
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.03) * 0.8


def tick():
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1700 * t) * 0.5 + rng.normal(0, 0.3, n)) * env(n, 0.001, 0.008)


def swoosh():
    n = int(0.35 * SR)
    noise = rng.normal(0, 1, n)
    # crude band-pass sweep via moving averages of varying length
    out = np.zeros(n)
    for i, k in enumerate([24, 12, 6]):
        out += np.convolve(noise, np.ones(k) / k, "same") * (0.5 + 0.25 * i)
    t = np.arange(n) / SR
    shape = np.sin(np.pi * np.clip(t / 0.35, 0, 1)) ** 2
    return out * shape * 0.5


def thud():
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * (70 + 60 * np.exp(-t * 25)) * t) * env(n, 0.002, 0.08)
    slap = rng.normal(0, 1, n) * env(n, 0.001, 0.015) * 0.5
    return (body + slap) * 0.9


def whoosh():
    s = swoosh()
    return np.concatenate([s, s[::-1] * 0.4])[: int(0.5 * SR)] * 1.2


def ding():
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    tone = sum(a * np.sin(2 * np.pi * f * t) for f, a in [(1318, 0.5), (1976, 0.3), (2637, 0.15)])
    return tone * env(n, 0.003, 0.25) * 0.5


SOUNDS = {"pop": pop, "tick": tick, "swoosh": swoosh, "thud": thud, "whoosh": whoosh, "ding": ding}
GAIN = {"pop": 0.35, "tick": 0.25, "swoosh": 0.22, "thud": 0.5, "whoosh": 0.3, "ding": 0.25}


def main():
    wd, dur, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    cues = json.load(open(f"{wd}/sfx.json"))
    mix = np.zeros(int(dur * SR) + SR)
    last = {}
    for t0, kind in cues:
        if t0 - last.get(kind, -1) < 0.08:  # avoid stacking identical cues
            continue
        last[kind] = t0
        s = SOUNDS[kind]() * GAIN[kind]
        i = int(t0 * SR)
        mix[i:i + len(s)] += s[: len(mix) - i]
    mix = np.clip(mix[: int(dur * SR)], -1, 1)
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main()
