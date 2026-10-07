"""Style C ("Vox Explainer") soundtrack + SFX, ducked under the original dialog.

Usage: python make_audio_vox.py <project_dir> <out_dir>
Curious explainer bed at 92 BPM in F: marimba plucks, soft pad, rim clicks;
"tak selesa" filtered; after the product cut: soft kick + upright-ish bass.
SFX are paper/desk sounds: typewriter ticks (kickers), paper slides, rubber
stamps, marker squeaks (drawn ticks/arrows) — on cues_vox.py times.
"""
import math
import os
import subprocess
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import cues_vox as C  # noqa: E402

P, OUT = sys.argv[1], sys.argv[2]
SR = 48000
N = int(C.DURATION * SR)
BPM = 92
BEAT = 60 / BPM
rng = np.random.default_rng(3)
T = np.arange(N) / SR


def midi(m):
    return 440 * 2 ** ((m - 69) / 12)


def lp1(x, fc):
    """one-pole low-pass, fc may be an array (time-varying)."""
    fc = np.broadcast_to(np.asarray(fc, np.float64), x.shape)
    a = 1 - np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a[i] * (x[i] - acc)
        y[i] = acc
    return y


def env_adsr(n, a=0.005, d=0.15, s=0.0, r=0.1):
    t = np.arange(n) / SR
    e = np.where(t < a, t / a, s + (1 - s) * np.exp(-(t - a) / d))
    tail = int(r * SR)
    if tail and n > tail:
        e[-tail:] *= np.linspace(1, 0, tail)
    return e


def add(buf, sig, t0):
    i = int(t0 * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[:j - i]


def section_gain(t, pts):
    """piecewise-linear automation over [(time, gain), ...]"""
    ts, gs = zip(*pts)
    return np.interp(t, ts, gs)


# ---------------------------------------------------------------- music
CHORDS = [[53, 57, 60, 64], [57, 60, 64, 67], [50, 53, 57, 60], [46, 50, 53, 57]]  # Fmaj7 Am7 Dm7 Bbmaj7
BAR = 4 * BEAT
CHORD_LEN = 2 * BAR   # 4.8s per chord


def chord_at(t):
    return CHORDS[int(t // CHORD_LEN) % 4]


pad = np.zeros(N)
for k in range(int(C.DURATION // CHORD_LEN) + 1):
    t0 = k * CHORD_LEN
    notes = CHORDS[k % 4] if t0 < C.END - 0.5 else [53, 57, 60, 64, 67]
    ln = min(CHORD_LEN + 0.6, C.DURATION - t0)
    if t0 >= 26.4:   # final chord rings out from the end card
        t0, ln = 27.15, C.DURATION - 27.15
        notes = [53, 60, 64, 67, 69]
    n = int(ln * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for m in notes:
        for det in (-0.08, 0.08):
            f = midi(m + 12) * (1 + det / 100)
            s += np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * 0.5 + 0.18 * np.sin(4 * np.pi * f * t)
    e = np.minimum(1, t / 0.5) * np.minimum(1, (ln - t) / 0.6)
    add(pad, s * e / len(notes) * 0.5, t0)
    if t0 >= 27.15:
        break

pluck = np.zeros(N)
step = BEAT / 2
for i in range(int(C.DURATION / step)):
    t0 = i * step
    if t0 >= 29.9:
        break
    ch = chord_at(t0)
    pattern = [0, 2, 1, 3, 2, 1, 3, 2]
    m = ch[pattern[i % 8]] + 12
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = midi(m)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 3.98 * f * t) * np.exp(-t * 30)
    vel = 0.8 if i % 2 == 0 else 0.45
    if i % 8 in (3, 7):
        continue   # leave air in the pattern
    add(pluck, s * env_adsr(n, 0.002, 0.16) * vel, t0)

bass = np.zeros(N)
for i in range(int(C.DURATION / BEAT)):
    t0 = i * BEAT
    if t0 < C.SCENE_CUT - 0.05 or t0 > 29.9:
        continue
    root = chord_at(t0)[0] - 12
    n = int(BEAT * 0.9 * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * midi(root) * t) + 0.25 * np.sin(2 * np.pi * 2 * midi(root) * t)
    add(bass, s * env_adsr(n, 0.01, 0.35, 0.4, 0.05) * (1.0 if i % 2 == 0 else 0.7), t0)


def kick_sample():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 50 + 90 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def noise_hit(dur, decay, fc_hp=4000, fc_lp=12000):
    n = int(dur * SR)
    x = rng.normal(0, 1, n)
    x = x - lp1(x, fc_hp)
    x = lp1(x, fc_lp)
    return x * np.exp(-np.arange(n) / SR * decay)


drums = np.zeros(N)
KICK = kick_sample()
RIM = noise_hit(0.04, 120, 1500, 7000)
for i in range(int(C.DURATION / (BEAT / 2))):
    t0 = i * BEAT / 2
    if t0 > 29.95:
        break
    beat, on = i // 2, i % 2 == 0
    full = C.SCENE_CUT - 0.01 <= t0
    dark = 12.2 <= t0 < C.SCENE_CUT
    if on and beat % 2 == 1 and not dark and t0 > 0.6:
        add(drums, RIM * 0.5, t0)
    if full and on and beat % 2 == 0:
        add(drums, KICK * 0.7, t0)
    if not full and not dark and t0 > 6.4 and on and beat % 4 == 0:
        add(drums, KICK * 0.45, t0)

# riser into the product cut
r0, r1 = C.SCENE_CUT - 1.6, C.SCENE_CUT
n = int((r1 - r0) * SR)
t = np.arange(n) / SR
riser = rng.normal(0, 1, n)
riser = lp1(riser, 400 + 6000 * (t / t[-1]) ** 2) * (t / t[-1]) ** 2 * 0.3
riser += np.sin(2 * np.pi * np.cumsum(300 + 900 * (t / t[-1]) ** 2) / SR) * (t / t[-1]) ** 2 * 0.12
add(drums, riser, r0)

# section automation
g_pad = section_gain(T, [(0, 0.0), (0.3, 0.7), (12.0, 0.7), (13.0, 0.85), (17.1, 0.85), (17.13, 0.6), (29.0, 0.6), (31, 0.9)])
g_pluck = section_gain(T, [(0, 0.7), (11.8, 0.7), (12.6, 0.15), (16.6, 0.15), (17.13, 0.9), (27.1, 0.9), (29.9, 0.4), (31, 0)])
music = pad * g_pad * 0.5 + pluck * g_pluck * 0.32 + bass * 0.36 + drums * 0.6
cut = section_gain(T, [(0, 10000), (12.0, 10000), (12.8, 1100), (16.7, 1100), (17.13, 13000), (31, 13000)])
music = lp1(music, cut)
music *= section_gain(T, [(0, 1), (30.5, 1), (31, 0)])

# ---------------------------------------------------------------- SFX (same cue times as visuals)
sfx = np.zeros(N)


def pop(f0=900, dur=0.09, amp=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * np.exp(-t * 18) + f0 * 0.4
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 45) * amp


def thud(amp=0.7):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 90 * np.exp(-t * 10) + 45
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11) + noise_hit(0.35, 30, 200, 2000) * 0.25) * amp


def whoosh(dur=0.5, amp=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = rng.normal(0, 1, n)
    fc = 500 + 5000 * np.sin(np.pi * t / dur) ** 2
    x = lp1(x, fc) - lp1(x, fc * 0.25)
    return x * np.sin(np.pi * t / dur) ** 2 * amp


def chime(notes=(84, 88, 91, 96), amp=0.22):
    out = np.zeros(int(1.6 * SR))
    for k, m in enumerate(notes):
        n = int(1.2 * SR)
        t = np.arange(n) / SR
        s = np.sin(2 * np.pi * midi(m) * t) * np.exp(-t * 4) + 0.3 * np.sin(2 * np.pi * midi(m) * 2.01 * t) * np.exp(-t * 7)
        i = int(k * 0.06 * SR)
        out[i:i + n] += s * amp
    return out


def tick(amp=0.35):
    n = noise_hit(0.04, 140, 2500, 9000) * amp
    p = pop(1600, 0.04, 0.2)
    return n[:len(p)] + p


def buzz(amp=0.25):
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    s = np.sign(np.sin(2 * np.pi * 160 * t)) * 0.5 + np.sin(2 * np.pi * 120 * t)
    return lp1(s, 1500) * env_adsr(n, 0.005, 0.12) * amp


def typewriter(n_keys=6, amp=0.35):
    out = np.zeros(int((n_keys * 0.06 + 0.1) * SR))
    for k in range(n_keys):
        h = noise_hit(0.035, 150, 1200, 8000)
        h[:960] += pop(2200, 0.02, 0.2)
        i = int(k * (0.055 + 0.01 * rng.random()) * SR)
        out[i:i + len(h)] += h * amp * (0.8 + 0.4 * rng.random())
    return out


def paper(dur=0.35, amp=0.35):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = rng.normal(0, 1, n)
    x = lp1(x, 2500) - lp1(x, 500)
    return x * np.sin(np.pi * t / dur) ** 1.5 * amp


def marker(dur=0.3, amp=0.12):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = rng.normal(0, 1, n)
    fc = 3000 + 800 * np.sin(2 * np.pi * 9 * t)
    x = lp1(x, fc) - lp1(x, fc * 0.7)
    return x * np.sin(np.pi * t / dur) * amp * 3


def stamp_sfx(amp=0.8):
    return thud(amp) + np.pad(noise_hit(0.08, 50, 300, 3000) * 0.4, (0, int(0.27 * SR)))


add(sfx, typewriter(6), C.S1[0])
add(sfx, paper(0.3), C.S1[0] + 0.2)
add(sfx, marker(0.5), C.S1[0] + 0.5)
add(sfx, paper(0.3), C.S2[0])
add(sfx, pop(700, amp=0.35), 3.0)
add(sfx, pop(900, amp=0.35), 3.77)
add(sfx, stamp_sfx(0.85), C.STAMP_BAU)
add(sfx, paper(0.35), C.S3[0])
add(sfx, marker(0.3), C.TICK_OK + 0.1)
add(sfx, marker(0.3), C.TICK_NO + 0.1)
add(sfx, typewriter(5), C.S4[0])
add(sfx, paper(0.3), C.SELESA)
add(sfx, pop(800, amp=0.3), C.NEIGHBOURS)
add(sfx, marker(0.35), C.MOVE_AWAY + 0.3)
add(sfx, paper(0.45, 0.6), C.WIPE[0])
add(sfx, typewriter(8), C.S5[0])
add(sfx, pop(1000, amp=0.4), C.S5[0] + 0.2)
add(sfx, paper(0.25), C.CALL1)
add(sfx, marker(0.3), C.CALL1 + 0.2)
add(sfx, paper(0.25), C.CALL2)
add(sfx, marker(0.3), C.CALL2 + 0.2)
add(sfx, typewriter(5), C.S6[0])
add(sfx, marker(0.3), C.BOX1)
add(sfx, marker(0.3), C.BOX2)
add(sfx, paper(0.35), C.END)
add(sfx, chime(amp=0.16), C.END + 0.1)
add(sfx, pop(1100, amp=0.3), C.CLAIMS)
add(sfx, stamp_sfx(0.7), C.STAMP_POWER)
add(sfx, typewriter(7), C.CTA)
sfx = lp1(sfx, 14000)

# ---------------------------------------------------------------- voice + ducking
os.makedirs(OUT, exist_ok=True)
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{P}/source/footage.mp4", "-ac", "1", "-ar", str(SR),
                      "-f", "f32le", "-"], capture_output=True, check=True).stdout
voice = np.frombuffer(raw, np.float32).astype(np.float64)
voice = np.pad(voice, (0, max(0, N - len(voice))))[:N]
# voice envelope (attack 10ms, release 250ms) -> sidechain gain for music + SFX
rms = np.sqrt(np.convolve(voice ** 2, np.ones(480) / 480, mode="same"))
vdb = 20 * np.log10(rms + 1e-7)
active = np.clip((vdb + 42) / 14, 0, 1)            # 0 = silence, 1 = clear speech
smooth = np.zeros(N)
acc = 0.0
for i in range(0, N, 48):                            # 1ms control rate
    a = active[i]
    acc += (a - acc) * (0.1 if a > acc else 0.004)
    smooth[i:i + 48] = acc
duck = 10 ** (-(smooth * 9) / 20)                    # up to -9 dB extra while she talks
music = music * duck
sfx = sfx * (10 ** (-(smooth * 4) / 20))


def write(name, x, peak_norm=None):
    if peak_norm:
        x = x / (np.max(np.abs(x)) + 1e-9) * peak_norm
    st = np.stack([x, x], 1)
    with wave.open(f"{OUT}/{name}", "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes())


write("music.wav", music, peak_norm=0.9)
write("sfx.wav", sfx, peak_norm=0.9)
write("voice.wav", voice)
print("audio stems written", file=sys.stderr)
