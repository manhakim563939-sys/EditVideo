"""Soundtrack for fakta_render.py: music bed ducked under the VO, whoosh + impact on every transition.

Usage: python3 fakta_audio.py out.wav assets/vo_fakta_psikologi.mp3
"""
import subprocess
import sys
import wave

import numpy as np

import kolaj_audio as ka

SR = ka.SR
DUR = 50.4
N = int(SR * DUR)
STARTS = [4.18, 12.83, 21.06, 28.93, 34.15, 40.40, 44.83]


def main(path, vo_path):
    music = ka.make_music(DUR, drop_at=44.83)[:N]
    sfx = np.zeros(N)
    ka.add(sfx, ka.sfx_riser(0.5), 0.0, 0.4)
    for s in STARTS:
        ka.add(sfx, ka.sfx_whoosh(0.5), s - 0.3, 0.6)
        ka.add(sfx, ka.sfx_stamp(), s - 0.02, 0.35)
    ka.add(sfx, ka.sfx_ding(), 47.0, 0.5)
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
