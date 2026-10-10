"""Soundtrack for majalah_render.py: shared music bed + page-turn / shutter SFX + the VO.

Usage: python3 majalah_audio.py out.wav voiceover.mp3
"""
import sys
import wave

import numpy as np

import kolaj_audio as ka

SR = ka.SR
DUR = 44.5
N = int(SR * DUR)
rng = np.random.default_rng(11)


def page_flip(d=0.5):
    """Paper rustle: band-limited noise with a fast swell and a soft flap at the end."""
    t = np.arange(int(d * SR)) / SR
    n = rng.normal(0, 1, len(t))
    n = ka.lowpass(n, 5000) - ka.lowpass(n, 700)
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.5 * (1 + 0.5 * np.sin(2 * np.pi * 18 * t))
    flap = np.zeros_like(t)
    k = int(0.82 * len(t))
    flap[k:] = rng.normal(0, 1, len(t) - k) * np.exp(-(t[k:] - t[k]) * 60)
    return (n * env * 1.4 + flap * 0.5) * 0.6


def shutter():
    t = np.arange(int(0.12 * SR)) / SR
    a = rng.normal(0, 1, len(t)) * np.exp(-t * 90)
    b = np.zeros_like(t)
    k = int(0.06 * SR)
    b[k:] = rng.normal(0, 1, len(t) - k) * np.exp(-(t[k:] - t[k]) * 120)
    return (a + b) * 0.5


def main(path, vo_path):
    music = ka.make_music(DUR, drop_at=39.9)
    sfx = np.zeros(N)

    def cue(sig, t, gain):
        ka.add(sfx, sig, t, gain)

    cue(shutter(), 0.05, 0.9)
    cue(shutter(), 39.95, 0.9)
    for c in [4.3, 11.3, 18.4, 29.3, 34.2, 39.9]:
        cue(page_flip(0.55), c - 0.05, 0.9)
    for p in [0.35, 3.17, 3.4, 4.5, 5.0, 8.4, 9.2, 10.3, 11.5, 11.8, 14.26, 15.1, 18.6, 20.47, 23.18, 26.12, 29.5,
              30.6, 31.3, 32.85, 34.5, 34.6, 36.23, 40.66, 41.1, 43.0]:
        cue(ka.sfx_pop(), p, 0.35)
    for s in [1.3, 17.01, 30.2, 42.2]:  # strike-throughs and stamps
        cue(ka.sfx_stamp(), s, 0.6)
    for k in range(7):
        cue(ka.sfx_tick(), 33.0 + k * 0.12, 0.5)
    cue(ka.sfx_ding(), 38.96, 0.6)
    cue(ka.sfx_riser(0.9), 41.3, 0.5)

    ka.N = N
    vo = ka.load_vo(vo_path)
    mix = vo + music * 0.28 * ka.voice_duck(vo) + sfx * 0.40
    mix /= max(1.0, np.abs(mix).max() / 0.95)
    L = int(0.4 * SR)
    mix[-L:] *= np.linspace(1, 0, L)
    data = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
