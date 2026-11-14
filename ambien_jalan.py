"""Bunyi suasana jalan (trafik, motosikal lalu, tapak kaki) untuk klip tanpa audio.

Usage: python3 ambien_jalan.py out.wav [durasi_saat]
"""
import sys
import wave

import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100
rng = np.random.default_rng(7)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)


def lp(x, c):
    return sosfilt(butter(2, c, "low", fs=SR, output="sos"), x)


def main(path, dur=10.0):
    n = int(SR * dur)
    t = np.arange(n) / SR
    # trafik jauh: hingar rendah yang turun naik perlahan
    hum = lp(rng.normal(0, 1, n), 300) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.13 * t + 1))
    air = bp(rng.normal(0, 1, n), 800, 4000) * 0.15
    mix = hum * 0.9 + air
    # motosikal lalu, puncak sekitar 3.5s, efek doppler
    tc, w = 3.5, 1.6
    env = np.exp(-((t - tc) / w) ** 2)
    f = 95 * (1 + 0.08 * np.tanh(-(t - tc) / 0.5))
    ph = 2 * np.pi * np.cumsum(f) / SR
    eng = np.sign(np.sin(ph)) * 0.5 + np.sin(2 * ph) * 0.3 + rng.normal(0, 0.2, n)
    mix += lp(eng, 1500) * env * 0.8
    # motosikal kedua lebih jauh sekitar 8.2s
    env2 = np.exp(-((t - 8.2) / 1.2) ** 2)
    ph2 = 2 * np.pi * np.cumsum(120 * (1 + 0.06 * np.tanh(-(t - 8.2) / 0.5))) / SR
    mix += lp(np.sign(np.sin(ph2)) * 0.5 + rng.normal(0, 0.2, n), 1200) * env2 * 0.35
    # tapak kaki selepas 3s
    for k, ts in enumerate(np.arange(3.2, dur - 0.2, 0.55)):
        i = int(ts * SR)
        L = int(0.08 * SR)
        st = bp(rng.normal(0, 1, L), 150, 2500) * np.exp(-np.arange(L) / SR * 60)
        mix[i:i + L] += st[: n - i] * (0.5 if k % 2 else 0.4)
    mix /= np.abs(mix).max() / 0.6
    fade = np.minimum(1, np.minimum(t / 0.3, (dur - t) / 0.4))
    data = (mix * fade * 32767).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(data.tobytes())


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 10.0)
