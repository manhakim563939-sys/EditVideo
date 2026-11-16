"""Soundtrack for vox_tandas_render.py: music bed ducked under the VO + paper/whoosh/pop SFX.

Usage: python3 vox_tandas_audio.py out.wav assets/vo_tandas.mp3
"""
import subprocess
import sys
import wave

import numpy as np

import kolaj_audio as ka

SR = ka.SR
DUR = 52.8
N = int(SR * DUR)


def main(path, vo_path):
    music = ka.make_music(DUR, drop_at=45.4)[:N]
    sfx = np.zeros(N)
    for s in [9.9, 19.1, 26.4, 35.3, 45.4]:
        ka.add(sfx, ka.sfx_whoosh(0.5), s - 0.3, 0.55)
    for p in [1.4, 2.9, 6.0, 7.6, 12.8, 16.2, 17.3, 20.4, 21.4, 24.4, 26.4, 28.9, 31.0, 32.7, 34.2, 38.0, 38.9,
              40.7, 42.4, 45.7, 48.1, 51.5, 4.6, 23.4, 44.2, 49.1]:
        ka.add(sfx, ka.sfx_pop(), p, 0.3)
    for s in [20.8, 21.8, 22.8]:  # strike-throughs
        ka.add(sfx, ka.sfx_stamp(), s, 0.4)
    for s in [38.0, 39.7, 41.9]:
        ka.add(sfx, ka.sfx_click(), s, 0.6)
    ka.add(sfx, ka.sfx_ding(), 2.9, 0.4)
    ka.add(sfx, ka.sfx_ding(), 47.6, 0.5)
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
