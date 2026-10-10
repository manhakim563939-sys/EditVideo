"""Soundtrack for konsisten_render.py: shared music bed + SFX cues (VO time) + the VO.

Usage: python3 konsisten_audio.py out.wav voiceover.mp3
"""
import sys
import wave

import numpy as np

import kolaj_audio as ka

SR = ka.SR
DUR = 35.4
N = int(SR * DUR)
VO_LEAD = 1.0  # seconds of silence trimmed from the start of the VO


def main(path, vo_path):
    music = ka.make_music(DUR, drop_at=29.1)
    sfx = np.zeros(N)

    def cue(sig, t, gain):
        ka.add(sfx, sig, t, gain)

    for c in [4.0, 6.45, 11.35, 19.4, 25.0, 29.1]:
        cue(ka.sfx_whoosh(0.5), c - 0.25, 0.5)
    for p in [0.05, 0.2, 0.95, 1.9, 2.0, 2.2, 4.1, 4.15, 6.55, 7.4, 8.2, 9.5, 10.4, 11.45, 11.5, 11.9, 16.55,
              19.55, 19.7, 21.0, 22.25, 23.45, 25.1, 25.15, 25.2, 26.6, 27.3, 29.1, 29.3, 31.38, 32.85, 33.9]:
        cue(ka.sfx_pop(), p, 0.45)
    for k in range(15):  # people joining
        cue(ka.sfx_pop(), 15.1 + k * 3.6 / 15, 0.25)
    for k in range(28):  # calendar ticks
        cue(ka.sfx_tick(), 11.8 + k * 2.8 / 28, 0.5)
    for k in range(5):  # coins into the jar
        cue(ka.sfx_ding(), 10.05 + k * 0.3, 0.18)
    for s in [5.25, 8.95, 9.1]:
        cue(ka.sfx_stamp(), s, 0.75)
    cue(ka.sfx_riser(0.8), 0.6, 0.6)
    cue(ka.sfx_ding(), 23.45, 0.6)
    cue(ka.sfx_ding(), 31.38, 0.8)
    cue(ka.sfx_click(), 33.8, 0.9)
    cue(ka.sfx_ding(), 33.85, 0.6)

    ka.N = N + int(VO_LEAD * SR)
    vo = ka.load_vo(vo_path)[int(VO_LEAD * SR):]
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
