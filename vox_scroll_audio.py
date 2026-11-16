"""Soundtrack for vox_scroll_render.py: music bed ducked under the VO + paper/whoosh/pop SFX.

Usage: python3 vox_scroll_audio.py out.wav assets/vo_scroll.mp3
"""
import subprocess
import sys
import wave

import numpy as np

import kolaj_audio as ka

SR = ka.SR
DUR = 43.6
N = int(SR * DUR)


def main(path, vo_path):
    music = ka.make_music(DUR, drop_at=36.1)[:N]
    sfx = np.zeros(N)
    for s in [7.7, 14.4, 23.1, 29.2, 36.1]:
        ka.add(sfx, ka.sfx_whoosh(0.5), s - 0.3, 0.55)
    for p in [3.3, 4.5, 5.7, 8.0, 9.8, 10.9, 12.2, 13.3, 14.5, 19.9, 23.2, 24.2, 27.8, 38.5, 40.1]:
        ka.add(sfx, ka.sfx_pop(), p, 0.4)
    for k in range(40):  # clock ticking / slot reels
        ka.add(sfx, ka.sfx_tick(), 3.4 + k * 0.035, 0.35)
    for k in range(60):
        ka.add(sfx, ka.sfx_tick(), 14.6 + k * 0.07, 0.3)
    for s in [18.7, 19.05, 19.4, 37.0]:
        ka.add(sfx, ka.sfx_stamp(), s, 0.5)
    for s in [30.5, 32.4, 33.7]:
        ka.add(sfx, ka.sfx_click(), s, 0.7)
    ka.add(sfx, ka.sfx_ding(), 38.5, 0.5)
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
