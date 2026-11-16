"""Soundtrack for vox_duit_render.py: music bed ducked under the VO + paper/whoosh/pop SFX.

Usage: python3 vox_duit_audio.py out.wav assets/vo_duit.mp3
"""
import subprocess
import sys
import wave

import numpy as np

import kolaj_audio as ka

SR = ka.SR
DUR = 42.3
N = int(SR * DUR)


def main(path, vo_path):
    music = ka.make_music(DUR, drop_at=35.5)[:N]
    sfx = np.zeros(N)
    for s in [8.0, 15.8, 20.7, 27.5, 35.5]:
        ka.add(sfx, ka.sfx_whoosh(0.5), s - 0.3, 0.55)
    for p in [0.0, 3.0, 6.6, 9.0, 9.5, 11.1, 12.5, 14.0, 15.8, 16.5, 19.4, 21.0, 23.4, 24.9, 28.2, 30.3, 33.1,
              35.0, 36.6, 38.2, 40.9, 2.9, 4.4, 13.7, 22.7, 35.6, 36.6]:
        ka.add(sfx, ka.sfx_pop(), p, 0.35)
    for k in range(30):  # payslip balance draining
        ka.add(sfx, ka.sfx_tick(), 1.4 + k * 0.05, 0.3)
    for s in [16.2, 16.7, 17.8, 18.1, 2.9]:
        ka.add(sfx, ka.sfx_stamp(), s, 0.45)
    for s in [28.2, 29.7, 32.2]:
        ka.add(sfx, ka.sfx_click(), s, 0.6)
    ka.add(sfx, ka.sfx_ding(), 36.6, 0.5)
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
