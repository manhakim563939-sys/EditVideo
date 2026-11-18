"""Soundtrack for vox_spotlight_render.py: music bed ducked under the VO + paper/whoosh/pop SFX.

Usage: python3 vox_spotlight_audio.py out.wav assets/vo_spotlight.mp3
"""
import subprocess
import sys
import wave

import numpy as np

import kolaj_audio as ka

SR = ka.SR
DUR = 58.7
N = int(SR * DUR)


def main(path, vo_path):
    music = ka.make_music(DUR, drop_at=53.8)[:N]
    sfx = np.zeros(N)
    for s in [9.8, 18.2, 29.5, 43.7, 53.8]:
        ka.add(sfx, ka.sfx_whoosh(0.5), s - 0.3, 0.55)
    for p in [0.9, 3.3, 4.8, 8.2, 10.6, 14.0, 16.7, 18.6, 20.3, 21.9, 23.4, 27.3, 29.5, 31.8, 33.5, 35.8, 38.2,
              41.3, 45.3, 48.2, 52.7, 53.8, 55.0, 56.3, 7.6, 15.8, 22.9, 35.5, 39.7, 55.9]:
        ka.add(sfx, ka.sfx_pop(), p, 0.3)
    ka.add(sfx, ka.sfx_riser(), 9.9, 0.35)
    for s in [3.3, 10.6, 45.3]:
        ka.add(sfx, ka.sfx_stamp(), s, 0.45)
    for s in [23.8, 26.5]:
        ka.add(sfx, ka.sfx_tick(), s, 0.5)
    ka.add(sfx, ka.sfx_ding(), 52.4, 0.5)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", vo_path, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
                         check=True, capture_output=True).stdout
    vo = np.frombuffer(raw, np.int16).astype(np.float64) / 32768
    vo = np.pad(vo, (0, max(0, N - len(vo))))[:N]
    mix = vo + music * 0.26 * ka.voice_duck(vo) + sfx * 0.4
    mix /= max(1.0, np.abs(mix).max() / 0.95)
    mix[-int(0.5 * SR):] *= np.linspace(1, 0, int(0.5 * SR))
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
