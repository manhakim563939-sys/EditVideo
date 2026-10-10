"""Soundtrack for komen_render.py: shared music bed + app-style SFX (pings, typing, swipes) + the VO.

Usage: python3 komen_audio.py out.wav voiceover.mp3
"""
import sys
import wave

import numpy as np

import kolaj_audio as ka

SR = ka.SR
DUR = 37.0
N = int(SR * DUR)


def ping():
    """Short two-tone notification blip."""
    t = np.arange(int(0.22 * SR)) / SR
    f = np.where(t < 0.07, 1320, 1760)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14) * 0.35


def main(path, vo_path):
    music = ka.make_music(DUR, drop_at=31.55)
    sfx = np.zeros(N)

    def cue(sig, t, gain):
        ka.add(sfx, sig, t, gain)

    for c in [5.12, 8.42, 16.6, 23.66, 27.36, 31.55]:
        cue(ka.sfx_whoosh(0.45), c - 0.22, 0.6)
    for k in range(12):  # typing in the composer
        cue(ka.sfx_click(), 0.15 + k * 0.13, 0.25)
    for p in [0.0, 1.86, 2.9, 5.2, 5.3, 6.95, 7.2, 8.5, 8.54, 10.68, 13.18, 16.75, 18.7, 21.0, 23.75, 23.9, 25.6,
              27.45, 30.3, 31.6, 31.7, 32.0, 32.2, 33.25]:
        cue(ka.sfx_pop(), p, 0.4)
    for j in range(8):  # comments pouring out
        cue(ping(), 3.3 + j * 0.2, 0.5)
    for s in [9.58, 11.98, 15.24]:  # +1 VIDEO slams
        cue(ka.sfx_stamp(), s, 0.7)
        cue(ka.sfx_ding(), s + 0.05, 0.5)
    for s in [9.95, 12.35, 15.6, 6.95]:  # thumbnail lands in the grid
        cue(ping(), s, 0.45)
    for k in range(16):  # audience growing
        cue(ka.sfx_pop(), 21.03 + k * 2.0 / 16, 0.22)
    for j in range(14):  # hearts
        cue(ka.sfx_tick(), 24.2 + j * 0.22, 0.4)
    for j in range(6):  # comments pulled back up
        cue(ping(), 30.7 + j * 0.1, 0.35)
    for k in range(20):  # typing the question
        cue(ka.sfx_click(), 32.5 + k * 0.07, 0.25)
    cue(ka.sfx_riser(0.8), 29.2, 0.6)
    cue(ka.sfx_ding(), 33.25, 0.6)

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
