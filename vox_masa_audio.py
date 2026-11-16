"""Soundtrack for vox_masa_render.py: music bed ducked under the VO + paper/whoosh/pop SFX.

Usage: python3 vox_masa_audio.py out.wav assets/vo_masa.mp3
"""
import subprocess
import sys
import wave

import numpy as np

import kolaj_audio as ka

SR = ka.SR
DUR = 51.9
N = int(SR * DUR)


def main(path, vo_path):
    music = ka.make_music(DUR, drop_at=44.9)[:N]
    sfx = np.zeros(N)
    for s in [8.6, 20.2, 28.8, 34.8, 44.9]:
        ka.add(sfx, ka.sfx_whoosh(0.5), s - 0.3, 0.55)
    for p in [1.0, 5.9, 9.0, 10.2, 14.8, 15.6, 18.0, 22.2, 23.8, 25.2, 29.7, 31.2, 37.3, 38.6, 40.2, 43.9, 48.5,
              4.9, 25.9, 43.0, 47.3]:
        ka.add(sfx, ka.sfx_pop(), p, 0.3)
    for s in [14.5, 15.6, 16.6]:  # film frames
        ka.add(sfx, ka.sfx_click(), s, 0.6)
    for s in [37.3, 38.6, 40.2]:
        ka.add(sfx, ka.sfx_click(), s, 0.6)
    ka.add(sfx, ka.sfx_stamp(), 46.4, 0.45)
    ka.add(sfx, ka.sfx_ding(), 47.3, 0.5)
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
