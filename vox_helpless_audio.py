"""Soundtrack for vox_helpless_render.py: music bed ducked under the VO + paper/whoosh/pop SFX.

Usage: python3 vox_helpless_audio.py out.wav assets/vo_helpless.mp3
"""
import subprocess
import sys
import wave

import numpy as np

import kolaj_audio as ka

SR = ka.SR
DUR = 73.5
N = int(SR * DUR)


def main(path, vo_path):
    music = ka.make_music(DUR, drop_at=63.4)[:N]
    sfx = np.zeros(N)
    for s in [8.2, 22.5, 32.2, 43.8, 63.4]:
        ka.add(sfx, ka.sfx_whoosh(0.5), s - 0.3, 0.55)
    for p in [0.5, 4.4, 9.4, 12.7, 15.2, 17.0, 18.4, 20.2, 24.5, 26.9, 28.4, 32.8, 37.9, 41.2, 43.8, 45.6, 48.0,
              49.3, 56.2, 60.8, 62.0, 64.2, 67.8, 69.1, 6.2, 9.0, 12.3, 29.3, 40.6, 50.7, 59.2, 65.4, 70.2]:
        ka.add(sfx, ka.sfx_pop(), p, 0.3)
    for s in [26.9, 27.7, 28.4, 29.3]:
        ka.add(sfx, ka.sfx_click(), s, 0.5)
    for s in [52.4, 64.2]:
        ka.add(sfx, ka.sfx_stamp(), s, 0.45)
    for k in range(6):  # wall cracking
        ka.add(sfx, ka.sfx_click(), 60.8 + k * 0.16, 0.7)
    ka.add(sfx, ka.sfx_ding(), 65.4, 0.5)
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
