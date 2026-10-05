"""Procedural soundtrack + SFX, generated from the same cues as the visuals.

Writes build/music.wav and build/sfx.wav (48 kHz stereo, 16-bit).
Original instrumental — no samples, no copied melodies.
"""
import os
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from timeline import (CUTAWAYS, DIALOGUE_END, DURATION, TESTIMONIALS,  # noqa: E402
                      line_hits, transitions)

SR = 48000
N = int(DURATION * SR) + SR // 2
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rng = np.random.default_rng(11)

BPM = 100
BEAT = 60 / BPM
BAR = BEAT * 4
# C – Am – F – G (one chord per bar). Bass roots and pad voicings in Hz.
ROOTS = [65.41, 55.00, 43.65, 49.00]
PADS = [[261.6, 329.6, 392.0, 493.9], [220.0, 261.6, 329.6, 392.0],
        [174.6, 220.0, 261.6, 329.6], [196.0, 246.9, 293.7, 392.0]]

S_BASS, S_PAD, S_CLAP, S_DROP = 2.85, 11.95, 16.117, 43.0


def t_arr(dur):
    return np.arange(int(dur * SR)) / SR


def add(buf, sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    sig = sig[:len(buf) - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(sig), 0] += sig * gain * l * 1.414
    buf[i:i + len(sig), 1] += sig * gain * r * 1.414


def fft_band(sig, lo, hi):
    F = np.fft.rfft(sig)
    f = np.fft.rfftfreq(len(sig), 1 / SR)
    F[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(F, len(sig))


# ---------------------------------------------------------------- instruments
def kick(dur=0.35, f0=120, f1=45, decay=9):
    t = t_arr(dur)
    f = f1 + (f0 - f1) * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * decay)


HAT = fft_band(rng.normal(0, 1, int(0.05 * SR)), 7000, 16000) * np.exp(-t_arr(0.05) * 90)
HAT /= np.abs(HAT).max()
CLAP = fft_band(rng.normal(0, 1, int(0.18 * SR)), 900, 4000) * np.exp(-t_arr(0.18) * 22)
CLAP /= np.abs(CLAP).max()


def bass_note(freq, dur):
    t = t_arr(dur)
    env = np.minimum(t / 0.008, 1) * np.exp(-t * 6)
    return (np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(4 * np.pi * freq * t)) * env


def pad_chord(freqs, dur):
    t = t_arr(dur)
    out = np.zeros_like(t)
    for f in freqs:
        for det in (-0.12, 0.12):                       # gentle chorus
            for h in range(1, 7):                       # band-limited saw = soft tone
                out += np.sin(2 * np.pi * (f + det) * h * t + rng.uniform(0, 6.28)) / (h ** 1.6)
    env = np.minimum(t / 0.6, 1) * np.minimum((dur - t) / 0.6, 1)
    return out / (len(freqs) * 4) * env


def music():
    buf = np.zeros((N, 2))
    end_music = DIALOGUE_END
    nbeats = int(end_music / BEAT) + 1
    for b in range(nbeats):
        tb = b * BEAT
        if tb >= end_music:
            break
        bar = int(tb / BAR) % 4
        drums_on = tb < S_DROP
        if drums_on:
            add(buf, kick(), tb, 0.55 if b % 4 in (0, 2) else 0.35)
            for k in range(2):                           # 8th-note hats
                add(buf, HAT, tb + k * BEAT / 2, 0.10 if k else 0.06, pan=0.25)
            if tb >= S_CLAP and b % 4 in (1, 3):
                add(buf, CLAP, tb, 0.16, pan=-0.1)
        if tb >= S_BASS and drums_on:
            for k in range(2):
                add(buf, bass_note(ROOTS[bar], BEAT / 2), tb + k * BEAT / 2, 0.30 if k == 0 else 0.18)
    nb = int(end_music / BAR) + 1
    for bi in range(nb):
        tb = bi * BAR
        if tb + 0.01 >= S_PAD - BAR and tb < end_music:
            dur = min(BAR + 0.6, end_music - tb + 0.3)
            fade = np.clip((np.arange(int(dur * SR)) / SR + tb - S_PAD + 1.5) / 1.5, 0, 1)
            add(buf, pad_chord(PADS[bi % 4], dur) * fade, tb, 0.22)
    # end card: resolved C chord + sub, rings out
    tail = DURATION - DIALOGUE_END + 0.4
    add(buf, pad_chord([130.8, 261.6, 329.6, 392.0, 523.3], tail) * np.exp(-t_arr(tail) * 0.5), DIALOGUE_END, 1.6)
    add(buf, bass_note(65.41, 1.6), DIALOGUE_END, 0.7)
    # fade out last 0.8 s
    fo = int(0.8 * SR)
    e = int(DURATION * SR)
    buf[e - fo:e] *= np.linspace(1, 0, fo)[:, None]
    buf[e:] = 0
    return buf


# ---------------------------------------------------------------- SFX
def click(pitch=1800, dur=0.04):
    t = t_arr(dur)
    return (np.sin(2 * np.pi * pitch * t) * np.exp(-t * 120)
            + fft_band(rng.normal(0, 1, len(t)), 2000, 9000) * np.exp(-t * 300) * 0.4)


def whoosh(dur=0.45, up=True):
    n = int(dur * SR)
    noise = rng.normal(0, 1, n + 2048)
    out = np.zeros(n + 2048)
    win = np.hanning(1024)
    for s in range(0, n, 256):                          # sweeping band-pass (STFT)
        p = s / n
        c = 400 + 3600 * (p if up else 1 - p)
        seg = noise[s:s + 1024] * win
        out[s:s + 1024] += fft_band(seg, c * 0.6, c * 1.6) * 0.5
    t = np.arange(n) / n
    env = np.sin(np.pi * t) ** 2
    return out[:n] * env / (np.abs(out).max() + 1e-9)


def pop(dur=0.12):
    t = t_arr(dur)
    f = 500 + 500 * (1 - np.exp(-t * 60))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 35)


def marker(dur=0.45):
    t = t_arr(dur)
    return fft_band(rng.normal(0, 1, len(t)), 2500, 7000) * np.sin(np.pi * t / dur) * 0.25


def riser(dur=1.6):
    t = t_arr(dur)
    f = 180 * (6 ** (t / dur))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4
    nz = fft_band(rng.normal(0, 1, len(t)), 1500, 9000) * 0.25
    return (tone + nz) * (t / dur) ** 2.2


def impact(dur=1.4):
    t = t_arr(dur)
    return kick(dur, 90, 32, 3.0) + fft_band(rng.normal(0, 1, len(t)), 100, 3000) * np.exp(-t * 14) * 0.5


def sfx():
    buf = np.zeros((N, 2))
    for at, style in line_hits():
        if style == "HA":
            add(buf, click(1300, 0.06), at + 0.02, 0.32)
        else:
            add(buf, click(2100), at + 0.02, 0.20, pan=rng.uniform(-0.2, 0.2))
    for i, at in enumerate(transitions()):
        add(buf, whoosh(0.45, up=i % 2 == 0), at - 0.12, 0.30, pan=-0.3 if i % 2 else 0.3)
    for tm in TESTIMONIALS:
        add(buf, pop(), tm["start"] + 0.02, 0.28)
        add(buf, marker(), tm["hl_at"], 0.35)
    add(buf, riser(1.6), DIALOGUE_END - 1.6, 0.22)
    add(buf, impact(), DIALOGUE_END + 0.02, 0.55)
    return buf


def write(path, buf, peak_db):
    buf = buf / (np.abs(buf).max() + 1e-9) * (10 ** (peak_db / 20))
    pcm = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    os.makedirs(f"{ROOT}/build", exist_ok=True)
    write(f"{ROOT}/build/music.wav", music(), -3)
    write(f"{ROOT}/build/sfx.wav", sfx(), -3)
    print("wrote build/music.wav, build/sfx.wav")
