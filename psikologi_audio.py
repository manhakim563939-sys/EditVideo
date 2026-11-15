"""Soundtrack for psikologi_render.py: shared music bed (ducked under the VO) + SFX on the VO beats.

Usage: python3 psikologi_audio.py out.wav assets/vo_psikologi.mp3
"""
import os
import subprocess
import sys
import wave

import numpy as np

import kolaj_audio as ka

SR = ka.SR
EP = os.environ.get("EP", "1")
if EP == "2":
    DUR, CTA, STAR, HOOK_POPS = 58.1, 50.6, 45.53, [1.3, 1.7, 4.56, 4.96]
    NUM_T = [6.44, 14.34, 20.70, 27.78, 33.38, 39.22, 45.48]
    SUB_T = [11.79, 18.43, 24.83, 30.8, 36.72, 43.63, 48.3]
else:
    DUR, CTA, STAR, HOOK_POPS = 61.7, 57.3, 38.05, [1.2, 1.6, 4.1, 4.5]
    NUM_T = [6.84, 15.48, 22.21, 30.30, 38.0, 45.0, 52.24]
    SUB_T = [12.2, 20.19, 26.15, 35.07, 42.15, 49.03, 55.2]
STARTS = [t - 0.15 for t in NUM_T] + [CTA]
N = int(SR * DUR)


def main(path, vo_path):
    music = ka.make_music(DUR, drop_at=CTA)
    sfx = np.zeros(N)

    def cue(sig, t, gain):
        ka.add(sfx, sig, t, gain)

    cue(ka.sfx_riser(0.6), 0.0, 0.5)
    cue(ka.sfx_stamp(), 0.3, 0.7)
    for p in HOOK_POPS:
        cue(ka.sfx_pop(), p, 0.45)
    for s in STARTS:
        cue(ka.sfx_whoosh(0.5), s - 0.25, 0.55)
    for t in NUM_T:
        cue(ka.sfx_stamp(), t, 0.6)
        cue(ka.sfx_pop(), t + 0.15, 0.4)
    for t in SUB_T:
        cue(ka.sfx_pop(), t, 0.35)
    cue(ka.sfx_ding(), STAR, 0.5)  # the promised number
    for k in range(7):
        cue(ka.sfx_pop(), CTA + 0.9 + k * 0.12, 0.3)
    cue(ka.sfx_ding(), CTA + 1.9, 0.6)

    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", vo_path, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
                         check=True, capture_output=True).stdout
    vo = np.frombuffer(raw, np.int16).astype(np.float64) / 32768
    vo = np.pad(vo, (0, max(0, N - len(vo))))[:N]
    mix = vo * 1.0 + music[:N] * 0.28 * ka.voice_duck(vo) + sfx * 0.38
    mix /= max(1.0, np.abs(mix).max() / 0.95)
    L = int(0.5 * SR)
    mix[-L:] *= np.linspace(1, 0, L)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
