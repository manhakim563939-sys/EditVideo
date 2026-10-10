"""Soundtrack for versus_render.py: shared music bed + fighting-game SFX + the VO.

Usage: python3 versus_audio.py out.wav voiceover.mp3
"""
import sys
import wave

import numpy as np

import kolaj_audio as ka

SR = ka.SR
DUR = 43.2
N = int(SR * DUR)
rng = np.random.default_rng(9)


def punch():
    """Meaty hit: low thump + noise crack."""
    t = np.arange(int(0.35 * SR)) / SR
    thump = np.sin(2 * np.pi * np.cumsum(60 + 140 * np.exp(-t * 30)) / SR) * np.exp(-t * 10)
    crack = rng.normal(0, 1, len(t)) * np.exp(-t * 35)
    return (thump + 0.6 * crack) * 0.8


def swish():
    """Short swing for MISS."""
    t = np.arange(int(0.25 * SR)) / SR
    n = rng.normal(0, 1, len(t))
    n = n - ka.lowpass(n, 1500)
    return n * np.sin(np.pi * t / 0.25) ** 2 * 0.5


def main(path, vo_path):
    music = ka.make_music(DUR, drop_at=35.9)
    sfx = np.zeros(N)

    def cue(sig, t, gain):
        ka.add(sfx, sig, t, gain)

    for c in [4.2, 9.3, 14.3, 20.1, 24.9, 31.2, 35.9]:
        cue(ka.sfx_whoosh(0.4), c - 0.2, 0.55)
    for p in [0.05, 0.3, 0.55, 1.88, 2.8, 4.45, 5.6, 7.26, 9.45, 11.4, 14.45, 20.3, 21.5, 21.6, 21.9, 23.5, 25.0,
              25.05, 26.53, 28.2, 29.69, 31.3, 32.4, 33.4, 33.5, 36.0, 36.05, 36.9, 39.25, 39.4, 39.9, 40.4, 41.5]:
        cue(ka.sfx_pop(), p, 0.4)
    for k in range(10):  # ten megaphones
        cue(ka.sfx_pop(), 32.6 + k * 0.08, 0.2)
    cue(ka.sfx_stamp(), 3.3, 0.9)  # VS slam
    for s in [4.3, 4.95, 31.35]:  # ROUND / FIGHT / FINAL banners
        cue(ka.sfx_stamp(), s, 0.7)
    cue(swish(), 8.1, 0.7)
    for s in [13.05, 16.8, 17.75, 18.8]:
        cue(punch(), s, 0.8)
    for s in [16.85, 17.8, 18.85]:
        cue(ka.sfx_ding(), s, 0.35)
    cue(ka.sfx_riser(1.2), 33.3, 0.8)
    cue(punch(), 34.55, 1.0)
    cue(ka.sfx_stamp(), 34.55, 1.0)
    cue(ka.sfx_ding(), 35.2, 0.7)
    for k in range(15):  # REC countdown
        cue(ka.sfx_tick(), 23.6 + k * 0.1, 0.5)
    for k in range(5):  # speech-bubble flicks in the megaphone
        cue(ka.sfx_click(), 5.8 + k * 0.25, 0.2)
    cue(ka.sfx_click(), 41.9, 0.8)

    ka.N = N
    vo = ka.load_vo(vo_path)
    mix = vo + music * 0.30 * ka.voice_duck(vo) + sfx * 0.40
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
