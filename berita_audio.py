"""Soundtrack for berita_render.py: shared music bed + TV-news stings, stingers, ticks + the VO.

Usage: python3 berita_audio.py out.wav voiceover.mp3
"""
import sys
import wave

import numpy as np

import kolaj_audio as ka

SR = ka.SR
DUR = 46.0
N = int(SR * DUR)


def news_sting(d=1.4):
    """Bold brassy chord hit with a timpani-ish thump, like a news intro."""
    t = np.arange(int(d * SR)) / SR
    out = np.zeros_like(t)
    for n in [50, 57, 62, 66, 69]:  # D major-ish stack
        f = ka.nfreq(n)
        for h, a in [(1, 1.0), (2, 0.5), (3, 0.3), (4, 0.18)]:
            out += np.sin(2 * np.pi * f * h * t) * a
    out *= np.minimum(1, t / 0.015) * np.exp(-t * 2.2) / 12
    thump = np.sin(2 * np.pi * np.cumsum(55 + 60 * np.exp(-t * 20)) / SR) * np.exp(-t * 6) * 0.8
    return out + thump


def main(path, vo_path):
    music = ka.make_music(DUR, drop_at=40.1)
    sfx = np.zeros(N)

    def cue(sig, t, gain):
        ka.add(sfx, sig, t, gain)

    cue(news_sting(), 0.0, 0.9)
    for c in [4.6, 11.2, 17.5, 24.1, 34.1, 40.1]:
        cue(ka.sfx_whoosh(0.6), c - 0.3, 0.6)
        cue(news_sting(0.9), c, 0.45)
    for p in [0.4, 2.9, 4.8, 11.4, 15.96, 24.4, 26.55, 29.13, 31.44, 34.3, 38.0, 40.2, 42.6]:
        cue(ka.sfx_pop(), p, 0.35)
    for s in [11.8, 13.6, 20.45, 22.77]:
        cue(ka.sfx_stamp(), s, 0.6)
    for k in range(20):  # budget counter
        cue(ka.sfx_tick(), 4.9 + 2.3 * (1 - (1 - k / 20) ** (1 / 3)), 0.5)
    for k in range(3):  # 0:01 0:02 0:03
        cue(ka.sfx_tick(), 17.75 + k / 1.2, 0.8)
    for k in range(8):  # swipes on the CCTV phone
        cue(ka.sfx_click(), 17.6 + k * 0.33, 0.25)
    cue(ka.sfx_ding(), 38.0, 0.6)
    cue(ka.sfx_riser(0.8), 15.2, 0.5)

    ka.N = N
    vo = ka.load_vo(vo_path)
    mix = vo + music * 0.26 * ka.voice_duck(vo) + sfx * 0.40
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
