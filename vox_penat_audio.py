"""Soundtrack for vox_penat_render.py: music bed ducked under the VO + paper/whoosh/pop SFX.

Usage: python3 vox_penat_audio.py out.wav assets/vo_penat.mp3
"""
import subprocess
import sys
import wave

import numpy as np

import kolaj_audio as ka

SR = ka.SR
DUR = 45.9
N = int(SR * DUR)


def main(path, vo_path):
    music = ka.make_music(DUR, drop_at=39.1)[:N]
    sfx = np.zeros(N)
    for s in [5.9, 15.6, 23.0, 30.3, 39.1]:
        ka.add(sfx, ka.sfx_whoosh(0.5), s - 0.3, 0.55)
    for p in [1.8, 3.6, 6.6, 9.6, 10.8, 12.3, 14.9, 16.3, 19.7, 23.8, 29.6, 33.0, 35.4, 38.4, 42.6,
              9.3, 10.6, 11.7, 14.4, 21.8, 25.2, 26.2, 27.2, 41.7]:
        ka.add(sfx, ka.sfx_pop(), p, 0.3)
    for k in range(4):  # notification dings
        ka.add(sfx, ka.sfx_ding(), 16.3 + k * 0.5, 0.25)
    for s in [31.1, 32.9, 35.4]:
        ka.add(sfx, ka.sfx_click(), s, 0.6)
    ka.add(sfx, ka.sfx_stamp(), 40.4, 0.45)
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
