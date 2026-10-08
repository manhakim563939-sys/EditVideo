"""Synth + SFX toolkit + generic arranger shared by the 5 concept videos."""
import os
import wave

import numpy as np

DUR = 30.0

ROOT = os.path.dirname(os.path.abspath(__file__))
SR = 48000
N = int(DUR * SR)
rng = np.random.default_rng(11)


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




# ---------------------------------------------------------------- extra SFX
def sfx2(kind):
    if kind == "tick":
        n = int(0.05 * SR)
        t = tvec(n)
        return (np.sin(2 * np.pi * 1250 * t) + 0.5 * np.sin(2 * np.pi * 2900 * t)) * np.exp(-t * 110)
    if kind == "tock":
        n = int(0.06 * SR)
        t = tvec(n)
        return (np.sin(2 * np.pi * 820 * t) + 0.4 * np.sin(2 * np.pi * 1900 * t)) * np.exp(-t * 90)
    if kind == "key":  # typewriter key
        n = int(0.035 * SR)
        t = tvec(n)
        nz = rng.normal(0, 1, n)
        nz = nz - onepole_lp(nz, 2500)
        return (nz * 0.6 + np.sin(2 * np.pi * rng.uniform(1800, 2600) * t) * 0.4) * np.exp(-t * 160)
    if kind == "bell_ding":
        out = np.zeros(int(1.0 * SR))
        for k, m in enumerate((84, 91)):
            b = bell(midi(m), 0.9)
            i = int(k * 0.09 * SR)
            out[i:i + len(b)] += b[: len(out) - i]
        return out * 0.6
    if kind == "buzzer":
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
    if kind in ("stamp", "stamp_soft"):
        n = int(0.35 * SR)
        t = tvec(n)
        f = 55 + 120 * np.exp(-t * 35)
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14) + 0.9 * onepole_lp(rng.normal(0, 1, n), 3500) * np.exp(-t * 60)
        return x * (0.55 if kind == "stamp_soft" else 1.0)
    if kind == "rewind":
        dur = 1.0
        n = int(dur * SR)
        t = tvec(n)
        f = 900 - 600 * (t / dur) + 120 * np.sin(2 * np.pi * 9 * t)
        tone = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.25
        nz = onepole_lp(rng.normal(0, 1, n), 3000) * 0.5
        return onepole_lp(tone + nz, 2500) * np.sin(np.pi * t / dur) ** 0.5
    if kind == "flag":  # cloth flap
        n = int(0.3 * SR)
        t = tvec(n)
        nz = onepole_lp(rng.normal(0, 1, n), 1800)
        return nz * (0.5 + 0.5 * np.sin(2 * np.pi * 22 * t)) * np.exp(-t * 9) * 2
    if kind == "swipe":
        return sfx("swish") * 1.2
    return sfx(kind)


# ---------------------------------------------------------------- generic arranger
def arrange(out, bpm, chords, sections, cues, dur=30.0, duck=(), lp_windows=(), pluck_oct=12, pad_gain=0.07,
            pluck_gain=0.10, swing=0.0, end_bell=(79, 83), peak_db=-4.8, seed=3):
    """sections: list of (start, level) — level 0 pad, 1 +pluck, 2 +bass/kick, 3 full (clap+hats), -1 silence.
    cues: (time, kind, gain). duck: (start, end, gain) windows applied to music (not SFX).
    lp_windows: (start, end, cutoff) low-pass windows on music."""
    global rng
    rng = np.random.default_rng(seed)
    n_tot = int(dur * SR)
    beat = 60 / bpm
    bar = 4 * beat
    L, R, drums, fx = np.zeros(n_tot), np.zeros(n_tot), np.zeros(n_tot), np.zeros(n_tot)
    secs = sorted(sections)

    def level(t):
        lv = secs[0][1]
        for s0, lv_ in secs:
            if s0 <= t + 1e-6:
                lv = lv_
        return lv

    def addb(buf, t0, sig):
        i = int(t0 * SR)
        if i >= n_tot or i < 0:
            return
        j = min(n_tot, i + len(sig))
        buf[i:j] += sig[: j - i]

    nb = int(np.ceil(dur / bar))
    for b in range(nb):
        t0 = b * bar
        root, tones = chords[b % len(chords)] if b < nb - 1 else chords[0]
        if level(t0) >= 0:
            for k, m in enumerate(tones):
                p = pad_note(midi(m), bar + 0.5) * pad_gain
                addb(L if k % 2 else R, t0, p)
                addb(R if k % 2 else L, t0, p * 0.6)
        pat = [0, None, 2, 1, None, 3, 2, 1]
        for i, idx in enumerate(pat):
            ts = t0 + i * beat / 2 + (swing * beat / 2 if i % 2 else 0)
            if idx is None or ts >= dur - 0.8 or level(ts) < 1:
                continue
            pl = pluck(midi(tones[idx] + pluck_oct), 0.4) * pluck_gain
            addb(L, ts, pl * (1.0 if i % 2 else 0.75))
            addb(R, ts + 0.01, pl * (0.75 if i % 2 else 1.0))
        for off in (0, 1.5, 2.5, 3):
            ts = t0 + off * beat
            if ts >= dur - 0.6 or level(ts) < 2:
                continue
            bl = bass(midi(root), beat * (0.9 if off == 0 else 0.4)) * 0.22
            addb(L, ts, bl)
            addb(R, ts, bl)
        for bt in range(4):
            ts = t0 + bt * beat
            lv = level(ts)
            if ts >= dur - 0.6 or lv < 2:
                continue
            addb(drums, ts, kick() * (0.5 if lv >= 3 or bt in (0, 2) else 0.0))
            if lv >= 3:
                if bt in (1, 3):
                    addb(drums, ts, clap() * 0.27)
                addb(drums, ts + beat / 2 + swing * beat / 2, hat(bt == 3) * 0.08)
    if end_bell:
        addb(L, dur - 2.0, bell(midi(end_bell[0]), 2.0) * 0.12)
        addb(R, dur - 1.98, bell(midi(end_bell[1]), 2.0) * 0.10)

    dk = np.ones(n_tot)
    lp = np.full(n_tot, 12000.0)
    r = int(0.12 * SR)
    for a, b, g in duck:
        ia, ib = int(a * SR), int(b * SR)
        dk[ia:ib] = np.minimum(dk[ia:ib], g)
        dk[max(0, ia - r):ia] = np.minimum(dk[max(0, ia - r):ia], np.linspace(1, g, ia - max(0, ia - r)))
        dk[ib:ib + r] = np.minimum(dk[ib:ib + r], np.linspace(g, 1, len(dk[ib:ib + r])))
    for a, b, c in lp_windows:
        lp[int(a * SR):int(b * SR)] = c
    L = onepole_lp(L, lp) * dk
    R = onepole_lp(R, lp) * dk
    drums = onepole_lp(drums, lp) * dk
    for t, kind, g in cues:
        addb(fx, max(0.0, t), sfx2(kind) * g * 0.6)
    fade = np.ones(n_tot)
    fo = int(0.6 * SR)
    fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
    st = np.stack([(L + drums + fx) * fade, (R + drums + fx) * fade], 1)
    st = np.tanh(st * 1.1) / np.tanh(1.1)
    st *= 10 ** (peak_db / 20) / np.abs(st).max()
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())
    return out
