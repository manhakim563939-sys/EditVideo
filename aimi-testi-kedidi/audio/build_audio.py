"""Procedural soundtrack + SFX for the Aimi Curtain kinetic edit.

Reads src/timeline.json (same cue times the visuals use) and public/dialog.wav
(for ducking). Writes public/music.wav and public/sfx.wav (48 kHz stereo).
Usage: .venv/bin/python audio/build_audio.py
"""
import json
import os

import numpy as np
import soundfile as sf
from scipy.signal import butter, lfilter, sosfilt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(f"{ROOT}/src/timeline.json"))
SR = 48000
END = TL["dialogEnd"]
TOTAL = END + TL["endCard"]
N = int(TOTAL * SR)
BRAND = TL.get("musicLift", 0.0)
rng = np.random.default_rng(3)
BPM = 112
BEAT = 60 / BPM
BAR = 4 * BEAT


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    return lfilter([1 - a], [1, -a], x)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], btype="band", fs=SR, output="sos"), x)


def hp(x, fc):
    return sosfilt(butter(2, fc, btype="high", fs=SR, output="sos"), x)


def add(buf, sig, t0, g=1.0, pan=0.0):
    i0 = int(t0 * SR)
    if i0 < 0 or i0 >= len(buf):
        return
    sig = sig[: len(buf) - i0]
    buf[i0:i0 + len(sig), 0] += sig * g * np.cos((pan + 1) * np.pi / 4)
    buf[i0:i0 + len(sig), 1] += sig * g * np.sin((pan + 1) * np.pi / 4)


def env(n, a, r):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-t / r)


def pluck(f, d=0.45):
    n = int(d * SR)
    t = np.arange(n) / SR
    return sum((0.55 ** k) * np.sin(2 * np.pi * f * (k + 1) * t) * np.exp(-t * (7 + 5 * k)) for k in range(4)) * np.minimum(t / 0.002, 1)


def pad(fs, d):
    n = int((d + 0.6) * SR)
    t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * (1 + det) * t) for f in fs for det in (-0.004, 0, 0.005))
    s = lp(s, 1600) / (3 * len(fs))
    return s * np.minimum(t / 0.25, 1) * np.where(t > d, np.exp(-(t - d) / 0.25), 1)


def bass(f, d):
    n = int((d + 0.05) * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)
    return s * np.minimum(t / 0.005, 1) * np.exp(-t * 3)


def kick():
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    f = 45 + 90 * np.exp(-t * 35)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10)


def clap():
    n = int(0.2 * SR)
    t = np.arange(n) / SR
    return bp(rng.normal(0, 1, n), 900, 4000) * (np.exp(-t * 28) + 0.5 * (t > 0.01) * np.exp(-np.maximum(t - 0.01, 0) * 30))


def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * SR)
    t = np.arange(n) / SR
    return hp(rng.normal(0, 1, n), 7500) * np.exp(-t * (18 if open_ else 80))


# ------------------------------------------------------------------ music: bright pop, builds to the brand reveal
CH = {"C": [60, 64, 67], "G": [55, 59, 62], "Am": [57, 60, 64], "F": [53, 57, 60]}
PROG = ["F", "G", "Am", "C"]
BROOT = {"F": 41, "G": 43, "Am": 45, "C": 48}
music = np.zeros((N, 2))
t = 0.0
bar = 0
while t < END - 0.02:
    name = PROG[bar % 4]
    notes = CH[name]
    full = t >= BRAND - 0.01
    add(music, pad([midi(m + 12) for m in notes], BAR), t, 0.35)
    for b in range(4):
        tb = t + b * BEAT
        if tb >= END:
            break
        add(music, bass(midi(BROOT[name]), BEAT * 0.9), tb, 0.35)
        add(music, bass(midi(BROOT[name]), BEAT * 0.4), tb + BEAT * 0.75, 0.18)
        if full or b in (0, 2):
            add(music, kick(), tb, 0.6 if full else 0.4)
        if full and b in (1, 3):
            add(music, clap(), tb, 0.28)
        for h in range(2):
            th = tb + h * BEAT / 2
            add(music, hat(open_=(h == 1 and full)), th, 0.07 if full else 0.04, pan=0.3)
            m = notes[(b * 2 + h) % 3] + 24
            add(music, pluck(midi(m)), th, 0.12, pan=-0.25 if h else 0.25)
    t += BAR
    bar += 1
# riser into the logo reveal handled by SFX; outro chord on the end card
add(music, pad([midi(m + 12) for m in CH["C"]] + [midi(84)], TOTAL - END - 0.4), END, 0.6)
for j, m in enumerate([72, 76, 79, 84]):
    add(music, pluck(midi(m), 1.2), END + 0.08 * j, 0.18)
add(music, kick(), END, 0.6)
fi = int(0.05 * SR)
music[:fi] *= np.linspace(0, 1, fi)[:, None]
fo = int(0.5 * SR)
music[-fo:] *= np.linspace(1, 0, fo)[:, None]
music /= np.max(np.abs(music)) + 1e-9

# ducking under the dialogue
dlg, dsr = sf.read(f"{ROOT}/public/dialog.wav", dtype="float32")
dlg = dlg.mean(axis=1) if dlg.ndim > 1 else dlg
dlg = np.pad(dlg, (0, max(0, N - len(dlg))))[:N]
hop = 480
rms = np.sqrt(np.convolve(dlg ** 2, np.ones(hop) / hop, "same")[::hop] + 1e-10)
act = np.clip((20 * np.log10(rms) + 45) / 20, 0, 1)
sm = np.zeros_like(act)
for i in range(len(act)):
    p = sm[i - 1] if i else 0
    sm[i] = p + (0.5 if act[i] > p else 0.04) * (act[i] - p)
gain = 10 ** (np.interp(np.arange(N), np.arange(len(sm)) * hop, -7.0 * sm) / 20)
tt = np.arange(N) / SR
bed = np.where(tt > END, 10 ** (-6 / 20), 10 ** (-13 / 20))
bed = np.convolve(bed, np.ones(int(0.2 * SR)) / int(0.2 * SR), "same")
bed[: int(0.2 * SR)] = 10 ** (-13 / 20)
music *= (gain * bed)[:, None]


# ------------------------------------------------------------------ SFX
def whoosh(d=0.5, short=False):
    n = int(d * SR)
    t = np.arange(n) / SR
    x = rng.normal(0, 1, n + 4096)
    out = np.zeros(n)
    for i in range(0, n, 1024):
        fc = 400 + 3500 * np.sin(np.pi * i / n) ** 2
        ch = bp(x[i:i + 1024 + 4096], fc * 0.6, min(fc * 1.6, 20000))[4096:4096 + 1024]
        out[i:i + len(ch)] = ch[: n - i]
    return out * np.sin(np.pi * np.clip(t / d, 0, 1)) ** (1.6 if short else 1.0)


def pop():
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(900 * np.exp(-t * 20) + 280) / SR) * np.exp(-t * 35)


def click():
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2100 * t) * 0.6 + hp(rng.normal(0, 1, n), 3000) * 0.4) * np.exp(-t * 110)


def impact(short=False):
    n = int((0.5 if short else 1.0) * SR)
    t = np.arange(n) / SR
    sub = np.sin(2 * np.pi * np.cumsum(40 + 70 * np.exp(-t * 12)) / SR) * np.exp(-t * (9 if short else 4))
    return sub + lp(rng.normal(0, 1, n), 2000) * np.exp(-t * 22) * 0.5


def riser(d=1.0):
    n = int(d * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * np.cumsum(200 * 8 ** (t / d)) / SR) * 0.3 + hp(rng.normal(0, 1, n), 2500) * 0.5) * (t / d) ** 2


def shimmer():
    n = int(1.4 * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for j, m in enumerate([84, 88, 91, 96]):
        o = int(j * 0.06 * SR)
        s[o:] += np.sin(2 * np.pi * midi(m) * t[: n - o]) * np.exp(-t[: n - o] * 3.5)
    return s


def ding():
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * midi(88) * t) + 0.4 * np.sin(2 * np.pi * midi(95) * t)) * np.exp(-t * 5) * np.minimum(t / 0.002, 1)


def ticks(d=1.0):
    n = int(d * SR)
    s = np.zeros(n)
    k = 0
    tt_ = 0.0
    while tt_ < d - 0.03:
        c = click()
        i = int(tt_ * SR)
        s[i:i + len(c)] += c[: n - i] * (0.6 + 0.4 * tt_ / d)
        tt_ += 0.09 * (1 - 0.5 * tt_ / d)
        k += 1
    return s


GEN = {"whoosh": lambda c: whoosh(0.55), "whoosh_s": lambda c: whoosh(0.3, True), "pop": lambda c: pop(), "click": lambda c: click(),
       "impact": lambda c: impact(), "impact_s": lambda c: impact(True), "riser": lambda c: riser(c.get("d", 1.0)),
       "shimmer": lambda c: shimmer(), "ding": lambda c: ding(), "ticks": lambda c: ticks(c.get("d", 1.0))}
LEAD = {"whoosh": 0.28, "whoosh_s": 0.15}
fx = np.zeros((N, 2))
for c in TL["sfx"]:
    s = GEN[c["k"]](c)
    s /= np.max(np.abs(s)) + 1e-9
    add(fx, s, max(0.0, c["t"] - LEAD.get(c["k"], 0.0)), c["g"] * 10 ** (-7 / 20))

d = f"{ROOT}/public"
sf.write(f"{d}/music.wav", music.astype(np.float32), SR, subtype="PCM_16")
sf.write(f"{d}/sfx.wav", fx.astype(np.float32), SR, subtype="PCM_16")
print("music peak %.1f dBFS, sfx peak %.1f dBFS, total %.2fs" % (20 * np.log10(np.abs(music).max()), 20 * np.log10(np.abs(fx).max()), TOTAL))
