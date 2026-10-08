"""Synth + SFX toolkit (copied from firea_motion_ad/audio.py)."""
import os
import wave

import numpy as np

from timeline import BEAT, DUR

ROOT = os.path.dirname(os.path.abspath(__file__))
SR = 48000
N = int(DUR * SR)
rng = np.random.default_rng(11)
BAR = 4 * BEAT


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


CHORDS = [  # (bass root, chord tones) — F, Am, Dm, Bb
    (41, [53, 57, 60, 64]),
    (45, [57, 60, 64, 67]),
    (38, [50, 53, 57, 60]),
    (46, [50, 53, 58, 62]),
]


def env_adsr(n, a, d, s, r, sr=SR):
    e = np.ones(n) * s
    ia, idd, ir = int(a * sr), int(d * sr), int(r * sr)
    ia = min(ia, n)
    e[:ia] = np.linspace(0, 1, ia, endpoint=False)
    e[ia:ia + idd] = np.linspace(1, s, len(e[ia:ia + idd]))
    if ir:
        e[-ir:] *= np.linspace(1, 0, min(ir, n))
    return e


def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * np.asarray(fc) / SR)
    y = np.empty_like(x)
    acc = 0.0
    if np.ndim(a) == 0:
        for i in range(len(x)):
            acc = (1 - a) * x[i] + a * acc
            y[i] = acc
    else:
        for i in range(len(x)):
            acc = (1 - a[i]) * x[i] + a[i] * acc
            y[i] = acc
    return y


def add(buf, start, sig):
    i = int(start * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]


def tvec(n):
    return np.arange(n) / SR


# ---------------------------------------------------------------- instruments
def pad_note(f, dur):
    n = int(dur * SR)
    t = tvec(n)
    x = sum(np.sin(2 * np.pi * f * d * t + rng.uniform(0, 6)) for d in (0.995, 1.0, 1.006))
    x += 0.3 * sum(np.sin(2 * np.pi * 2 * f * d * t) for d in (0.998, 1.004))
    return x * env_adsr(n, 0.5, 0.3, 0.8, 0.6) / 4


def pluck(f, dur=0.5):
    n = int(dur * SR)
    t = tvec(n)
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 18) \
        + 0.15 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 30)
    return x * np.exp(-t * 7) * np.minimum(1, t * 400)


def bell(f, dur=1.2):
    n = int(dur * SR)
    t = tvec(n)
    x = np.sin(2 * np.pi * f * t + 1.2 * np.sin(2 * np.pi * f * 3.5 * t) * np.exp(-t * 6))
    return x * np.exp(-t * 4) * np.minimum(1, t * 300)


def bass(f, dur):
    n = int(dur * SR)
    t = tvec(n)
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    return np.tanh(1.5 * x) * env_adsr(n, 0.01, 0.15, 0.7, 0.08)


def kick():
    n = int(0.35 * SR)
    t = tvec(n)
    f = 45 + 85 * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9) + 0.15 * rng.normal(0, 1, n) * np.exp(-t * 200)


def clap():
    n = int(0.25 * SR)
    t = tvec(n)
    nz = rng.normal(0, 1, n)
    nz = nz - onepole_lp(nz, 1200)  # crude high-pass
    e = np.exp(-t * 22)
    for k in (0.0, 0.012, 0.024):
        e += 0.6 * np.exp(-np.maximum(t - k, 0) * 120) * (t >= k)
    return nz * e * 0.5


def hat(open_=False):
    n = int((0.18 if open_ else 0.06) * SR)
    t = tvec(n)
    nz = rng.normal(0, 1, n)
    nz = nz - onepole_lp(nz, 6000)
    return nz * np.exp(-t * (18 if open_ else 70))


# ---------------------------------------------------------------- SFX
def sfx(kind):
    if kind == "click":
        n = int(0.04 * SR)
        t = tvec(n)
        return np.sin(2 * np.pi * 2100 * t) * np.exp(-t * 160) + 0.3 * rng.normal(0, 1, n) * np.exp(-t * 400)
    if kind == "pop":
        n = int(0.12 * SR)
        t = tvec(n)
        f = 380 + 900 * np.exp(-t * 45)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 32)
    if kind == "bubble":
        n = int(0.09 * SR)
        t = tvec(n)
        f0 = rng.uniform(500, 900)
        f = f0 * (1 + 1.4 * t / 0.09)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.09) ** 2
    if kind == "bloop":
        n = int(0.3 * SR)
        t = tvec(n)
        f = 240 + 520 * np.exp(-t * 14)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11) * np.minimum(1, t * 300)
    if kind in ("whoosh", "swish", "air"):
        dur = dict(whoosh=0.5, swish=0.3, air=0.7)[kind]
        n = int(dur * SR)
        t = tvec(n)
        nz = rng.normal(0, 1, n)
        lo, hi = dict(whoosh=(300, 4000), swish=(1500, 7000), air=(200, 1500))[kind]
        sweep = lo + (hi - lo) * np.sin(np.pi * t / dur) ** 2
        x = onepole_lp(nz, sweep)
        x = x - onepole_lp(x, lo * 0.5)
        return x * np.sin(np.pi * t / dur) ** 2 * 3
    if kind == "riser":
        dur = 1.2
        n = int(dur * SR)
        t = tvec(n)
        nz = rng.normal(0, 1, n)
        x = onepole_lp(nz, 400 + 7000 * (t / dur) ** 2)
        tone = np.sin(2 * np.pi * np.cumsum(220 + 660 * (t / dur) ** 2) / SR) * 0.25
        return (x * 1.5 + tone) * (t / dur) ** 2
    if kind in ("impact", "impact_soft"):
        n = int(0.9 * SR)
        t = tvec(n)
        f = 40 + 70 * np.exp(-t * 18)
        body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5)
        nz = onepole_lp(rng.normal(0, 1, n), 2500) * np.exp(-t * 25)
        return (body + 0.6 * nz) * (0.6 if kind == "impact_soft" else 1.0)
    if kind == "sparkle":
        out = np.zeros(int(0.9 * SR))
        for k, m in enumerate((84, 88, 91, 96)):
            b = bell(midi(m), 0.7) * 0.4
            i = int(k * 0.05 * SR)
            out[i:i + len(b)] += b[: len(out) - i]
        return out
    raise ValueError(kind)


