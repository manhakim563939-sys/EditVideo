"""Soundtrack for vox_tangguh_render.py: music bed ducked under the VO + paper/whoosh/pop SFX.

Usage: python3 vox_tangguh_audio.py out.wav assets/vo_tangguh.mp3
"""
import subprocess
import sys
import wave

import numpy as np

import kolaj_audio as ka

SR = ka.SR
DUR = 43.0
N = int(SR * DUR)


def main(path, vo_path):
    import json
    old = json.load(open("assets/vo_tangguh_words.json"))
    new = json.load(open("assets/vo_tangguh_v3_words.json"))
    o_t = [0.0] + [w[1] for w in old] + [DUR]
    n_t = [0.0] + [w[1] for w in new] + [new[-1][2] + 0.9]
    global N
    out_dur = n_t[-1]
    N = int(SR * out_dur)
    warp = lambda t: float(np.interp(t, o_t, n_t))
    music = ka.make_music(out_dur, drop_at=warp(36.9))[:N]
    orig_add = ka.add
    ka.add = lambda buf, sig, at, gain=1.0: orig_add(buf, sig, warp(at), gain)
    sfx = np.zeros(N)
    for s in [6.7, 14.8, 23.0, 29.7, 36.9]:
        ka.add(sfx, ka.sfx_whoosh(0.5), s - 0.3, 0.55)
    for p in [1.5, 2.4, 3.2, 5.0, 7.0, 10.2, 11.2, 12.1, 12.9, 15.0, 17.9, 18.7, 19.6, 20.4, 23.2, 24.2, 28.3,
              30.8, 32.8, 34.3, 38.8, 40.3]:
        ka.add(sfx, ka.sfx_pop(), p, 0.4)
    for s in [1.5, 2.4, 3.2, 37.6]:  # calendar stamps
        ka.add(sfx, ka.sfx_stamp(), s, 0.5)
    for k in range(6):  # stairs
        ka.add(sfx, ka.sfx_click(), 30.8 + k * 0.18, 0.5)
    for k in range(25):  # timer
        ka.add(sfx, ka.sfx_tick(), 33.0 + k * 0.1, 0.3)
    ka.add(sfx, ka.sfx_ding(), 38.8, 0.5)
    for p in [0.5, 2.4, 6.7, 9.9, 13.8, 15.1, 17.9, 19.0, 19.6, 20.4, 21.5, 24.2, 26.8, 31.3, 33.2, 35.1, 36.0, 39.4]:
        ka.add(sfx, ka.sfx_pop(), p - 0.02, 0.3)  # icon pops
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
