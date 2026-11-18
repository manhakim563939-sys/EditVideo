"""Soundtrack for vox_negatif_render.py: music bed ducked under the VO + paper/whoosh/pop SFX.

Usage: python3 vox_negatif_audio.py out.wav assets/vo_negatif.mp3
"""
import subprocess
import sys
import wave

import numpy as np

import kolaj_audio as ka

SR = ka.SR
DUR = 59.8
N = int(SR * DUR)


def main(path, vo_path):
    music = ka.make_music(DUR, drop_at=52.9)[:N]
    sfx = np.zeros(N)
    for s in [7.9, 16.4, 27.1, 41.3, 52.9]:
        ka.add(sfx, ka.sfx_whoosh(0.5), s - 0.3, 0.55)
    for p in [0.8, 2.6, 4.8, 8.9, 14.0, 15.4, 19.0, 20.0, 21.3, 24.3, 26.1, 31.5, 34.2, 37.8, 40.4, 42.2, 45.2,
              48.8, 51.8, 55.7, 57.6, 4.2, 28.8, 35.2, 57.0]:
        ka.add(sfx, ka.sfx_pop(), p, 0.3)
    for k in range(10):  # praise tiles
        ka.add(sfx, ka.sfx_tick(), 0.6 + k * 0.12, 0.4)
    for s in [2.4, 18.1, 20.8, 53.9]:
        ka.add(sfx, ka.sfx_stamp(), s, 0.45)
    for s in [42.2, 45.2, 49.5]:
        ka.add(sfx, ka.sfx_click(), s, 0.6)
    ka.add(sfx, ka.sfx_ding(), 55.1, 0.5)
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
