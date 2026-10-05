"""Procedural soundtrack + SFX for the langsir ad.

Reads src/timeline.json (same cues the visuals use) and public/dialog.wav
(for ducking). Writes public/music.wav and public/sfx.wav (48 kHz stereo).

Usage: .venv/bin/python audio/gen_audio.py
"""
import json
import os

import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(f"{ROOT}/src/timeline.json"))
SR = 48000
TOTAL = TL["footageEnd"] + TL["endCardDur"]
N = int(TOTAL * SR)
REFRESH = TL["refreshAt"]
CTA_LIFT = 34.07
END = TL["footageEnd"]
BPM = 96
BEAT = 60 / BPM
BAR = BEAT * 4
rng = np.random.default_rng(11)


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def env_adsr(n, a, d, s, r, sustain_len):
    t = np.arange(n) / SR
    e = np.zeros(n)
    e = np.where(t < a, t / max(a, 1e-4), e)
    m = (t >= a) & (t < a + d)
    e[m] = 1 - (1 - s) * (t[m] - a) / d
    m = (t >= a + d) & (t < sustain_len)
    e[m] = s
    m = t >= sustain_len
    e[m] = s * np.exp(-(t[m] - sustain_len) / r)
    return e


def add(buf, sig, t0, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    if i0 >= len(buf):
        return
    sig = sig[: len(buf) - i0]
    l = np.cos((pan + 1) * np.pi / 4)
    r = np.sin((pan + 1) * np.pi / 4)
    buf[i0 : i0 + len(sig), 0] += sig * gain * l
    buf[i0 : i0 + len(sig), 1] += sig * gain * r


def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    from scipy.signal import lfilter

    return lfilter([1 - a], [1, -a], x)


def bandpass(x, lo, hi):
    from scipy.signal import butter, sosfilt

    return sosfilt(butter(2, [lo, hi], btype="band", fs=SR, output="sos"), x)


def highpass(x, fc):
    from scipy.signal import butter, sosfilt

    return sosfilt(butter(2, fc, btype="high", fs=SR, output="sos"), x)


# ------------------------------------------------------------- instruments
def pad(freqs, dur):
    n = int((dur + 1.2) * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for f in freqs:
        for det in (-0.004, 0.0, 0.005):
            ff = f * (1 + det)
            s += np.sin(2 * np.pi * ff * t) + 0.3 * np.sin(4 * np.pi * ff * t) + 0.12 * np.sin(6 * np.pi * ff * t)
    s = onepole_lp(s, 1400)
    return s * env_adsr(n, 0.6, 0.4, 0.8, 0.5, dur) / (len(freqs) * 3)


def keys(f, dur=1.6):
    """Soft felt-piano-ish tone."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2.001 * f * t) * np.exp(-t * 3)
         + 0.12 * np.sin(2 * np.pi * 3.003 * f * t) * np.exp(-t * 5))
    e = np.minimum(t / 0.008, 1) * np.exp(-t * 2.2)
    return onepole_lp(s * e, 3000)


def pluck(f, dur=0.55):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = sum((0.6 ** k) * np.sin(2 * np.pi * f * (k + 1) * t) * np.exp(-t * (6 + 4 * k)) for k in range(5))
    return s * np.minimum(t / 0.003, 1)


def bell(f, dur=1.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6) + 0.2 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 9)
    return s * np.minimum(t / 0.002, 1) * np.exp(-t * 3.2)


def bass(f, dur):
    n = int((dur + 0.15) * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    return s * env_adsr(n, 0.01, 0.15, 0.7, 0.08, dur)


def kick():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 45 + 75 * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9)


def shaker():
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    return highpass(rng.normal(0, 1, n), 6000) * np.minimum(t / 0.01, 1) * np.exp(-t * 60)


def clap():
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    e = np.exp(-t * 25) + 0.6 * np.exp(-np.maximum(t - 0.012, 0) * 30) * (t > 0.012)
    return bandpass(rng.normal(0, 1, n), 900, 3500) * e * 0.6


# ------------------------------------------------------------- music
music = np.zeros((N, 2))
A, C, D, E, F, G = 57, 60, 62, 64, 65, 67  # midi roots (A3..G4)
chord = {
    "Am": [57, 60, 64],
    "F": [53, 57, 60],
    "C": [55, 60, 64],
    "G": [55, 59, 62],
    "Fmaj7": [53, 57, 60, 64],
}

# Section A: problem, 0 -> REFRESH. Sparse, wistful, no drums.
prog_a = ["Am", "F", "C", "G", "Am"]
t = 0.0
k = 0
while t < REFRESH - 0.3:
    name = prog_a[k % len(prog_a)]
    dur = min(BAR, REFRESH - t)
    add(music, pad([midi(m) for m in chord[name]], dur), t, 0.55)
    for j, m in enumerate(chord[name]):
        add(music, keys(midi(m + 12)), t + j * BEAT * 1.0 + BEAT * 0.5, 0.16, pan=-0.3 + 0.3 * j)
    t += BAR
    k += 1

# Section B / C: solution, downbeat on REFRESH.
prog_b = ["C", "G", "Am", "F"]
melody = [76, 79, 81, 79, 76, 74, 72, 74]  # pentatonic, used in lift
t = REFRESH
bar = 0
while t < END - 0.05:
    name = prog_b[bar % 4]
    notes = chord[name]
    root = notes[0] if name != "C" else 48
    if name == "G":
        root = 43
    elif name == "Am":
        root = 45
    elif name == "F":
        root = 41
    lift = t >= CTA_LIFT - 0.01
    add(music, pad([midi(m) for m in notes], BAR), t, 0.32)
    for b in range(4):
        tb = t + b * BEAT
        if tb >= END:
            break
        add(music, kick(), tb, 0.55 if b in (0, 2) else 0.25)
        if b in (1, 3):
            add(music, clap(), tb, 0.22)
        add(music, bass(midi(root), BEAT * 0.9), tb, 0.30)
        for h in range(2):
            th = tb + h * BEAT / 2
            if th < END:
                add(music, shaker(), th, 0.10 if h else 0.06, pan=0.35)
                arp = notes[(b * 2 + h) % len(notes)] + 12
                add(music, pluck(midi(arp)), th, 0.13, pan=-0.25 if h else 0.25)
        if lift and b % 2 == 0:
            add(music, bell(midi(melody[(bar * 2 + b // 2) % len(melody)])), tb, 0.10, pan=0.2)
    t += BAR
    bar += 1

# Outro: ring out on C major after dialog ends.
add(music, pad([midi(m) for m in chord["C"]] + [midi(72)], TOTAL - END - 0.6), END, 0.45)
for j, m in enumerate([60, 64, 67, 72, 76]):
    add(music, pluck(midi(m), 1.6), END + j * 0.12, 0.16, pan=-0.4 + 0.2 * j)
add(music, bass(midi(48), 1.6), END, 0.32)
add(music, kick(), END, 0.5)
add(music, bell(midi(84), 2.0), END + 0.7, 0.12)

# Fade-in first 0.15 s and fade-out last 0.6 s
fi = int(0.15 * SR)
music[:fi] *= np.linspace(0, 1, fi)[:, None]
fo = int(0.6 * SR)
music[-fo:] *= np.linspace(1, 0, fo)[:, None]

# ------------------------------------------------------------- ducking
dlg, dsr = sf.read(f"{ROOT}/public/dialog.wav", dtype="float32")
if dlg.ndim > 1:
    dlg = dlg.mean(axis=1)
assert dsr == SR, "dialog.wav must be 48 kHz"
dlg = np.pad(dlg, (0, max(0, N - len(dlg))))[:N]
hop = 480
rms = np.sqrt(np.convolve(dlg**2, np.ones(hop) / hop, "same")[::hop] + 1e-10)
active = np.clip((20 * np.log10(rms) + 45) / 20, 0, 1)  # 0 below -45 dBFS, 1 above -25
sm = np.zeros_like(active)
for i in range(len(active)):  # fast attack, slow release
    prev = sm[i - 1] if i else 0
    coef = 0.5 if active[i] > prev else 0.03
    sm[i] = prev + coef * (active[i] - prev)
duck_db = -9.0 * sm
gain = 10 ** (np.interp(np.arange(N), np.arange(len(sm)) * hop, duck_db) / 20)

# Overall music level: quiet bed under dialog, opens up on end card.
peak = np.max(np.abs(music)) + 1e-9
music = music / peak
bed = np.full(N, 10 ** (-12 / 20))
tt = np.arange(N) / SR
bed = np.where(tt > END, 10 ** (-6 / 20), bed)
bed = np.convolve(bed, np.ones(int(0.25 * SR)) / int(0.25 * SR), "same")
bed[: int(0.2 * SR)] = 10 ** (-12 / 20)
music *= (gain * bed)[:, None]

# ------------------------------------------------------------- SFX
def whoosh(d=0.55, short=False):
    n = int(d * SR)
    t = np.arange(n) / SR
    x = rng.normal(0, 1, n)
    out = np.zeros(n)
    seg = 1024
    for i in range(0, n, seg):  # sweeping bandpass
        p = i / n
        fc = 300 + 3500 * np.sin(np.pi * p) ** 2
        out[i : i + seg] = bandpass(x[max(0, i - 2048) : i + seg], fc * 0.6, min(fc * 1.6, 20000))[-len(out[i : i + seg]):]
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** (1.5 if short else 1.0)
    return out * e


def pop():
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    f = 900 * np.exp(-t * 18) + 300
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 35)


def click():
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2200 * t) * 0.6 + highpass(rng.normal(0, 1, n), 3000) * 0.4) * np.exp(-t * 120)


def impact(short=False):
    n = int((0.5 if short else 0.9) * SR)
    t = np.arange(n) / SR
    f = 40 + 60 * np.exp(-t * 12)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (8 if short else 4.5))
    nz = onepole_lp(rng.normal(0, 1, n), 1800) * np.exp(-t * 20) * 0.5
    return sub + nz


def riser(d=1.0):
    n = int(d * SR)
    t = np.arange(n) / SR
    f = 200 * (8 ** (t / d))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    nz = highpass(rng.normal(0, 1, n), 2500) * 0.5
    return (tone + nz) * (t / d) ** 2


def shimmer():
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for j, m in enumerate([84, 88, 91, 96]):
        d = int(j * 0.06 * SR)
        s[d:] += np.sin(2 * np.pi * midi(m) * t[: n - d]) * np.exp(-t[: n - d] * 4)
    return s * 0.3


GEN = {
    "whoosh": lambda c: whoosh(0.6),
    "whoosh_s": lambda c: whoosh(0.35, True),
    "pop": lambda c: pop(),
    "click": lambda c: click(),
    "impact": lambda c: impact(),
    "impact_s": lambda c: impact(True),
    "riser": lambda c: riser(c.get("d", 1.0)),
    "shimmer": lambda c: shimmer(),
}
sfx = np.zeros((N, 2))
for c in TL["sfx"]:
    s = GEN[c["k"]](c)
    s = s / (np.max(np.abs(s)) + 1e-9)
    # whooshes start slightly before the visual cue so the peak lands on it
    lead = 0.3 if c["k"] == "whoosh" else (0.17 if c["k"] == "whoosh_s" else 0.0)
    if c["k"] == "riser":
        lead = 0.0
    add(sfx, s, max(0, c["t"] - lead), c["g"] * 10 ** (-8 / 20))

os.makedirs(f"{ROOT}/public", exist_ok=True)
sf.write(f"{ROOT}/public/music.wav", music.astype(np.float32), SR, subtype="PCM_24")
sf.write(f"{ROOT}/public/sfx.wav", sfx.astype(np.float32), SR, subtype="PCM_24")
print("music peak dBFS", 20 * np.log10(np.max(np.abs(music)) + 1e-9))
print("sfx peak dBFS", 20 * np.log10(np.max(np.abs(sfx)) + 1e-9))
print("duration", TOTAL)
