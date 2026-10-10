"""Time remap that locks the edit to the ElevenLabs voice-over.

The edit in kolaj_render.py was laid out on a 40 s "design" timeline. Each anchor
pairs a design time (caption / phrase start) with the moment the VO actually
says it; everything in between is linearly stretched, so animations, wipes and
SFX keep their relative timing.
"""
import bisect

OUT_DUR = 39.0  # VO is 37.7 s; CTA holds a little after the last word

# (design time, VO time)
ANCHORS = [
    (0.0, 0.0),
    (0.45, 0.94),   # Tahu tak?
    (2.1, 1.6),     # Video ialah senjata paling kuat...
    (5.25, 4.68),   # Lebih lapan puluh peratus...
    (7.9, 7.56),    # ...adalah video
    (11.25, 8.94),  # Orang scroll laju...
    (13.2, 10.35),  # tapi video buat mereka berhenti
    (16.25, 12.75),  # Video bina kepercayaan
    (18.3, 14.94),  # Pelanggan nampak muka anda...
    (21.1, 17.99),  # mereka rasa kenal
    (22.5, 19.38),  # Orang beli dari orang...
    (24.65, 22.08),  # TikTok, Reels dan Shorts...
    (27.2, 25.92),  # reach organik
    (30.25, 28.0),  # Hasilnya?
    (31.9, 28.89),  # Lebih ramai nampak...
    (35.25, 33.09),  # Jadi, jangan tunggu lagi
    (37.1, 34.88),  # Mula buat video...
    (40.0, OUT_DUR),
]
_D = [a for a, _ in ANCHORS]
_V = [b for _, b in ANCHORS]


def _interp(x, xs, ys):
    i = min(max(bisect.bisect_right(xs, x) - 1, 0), len(xs) - 2)
    x0, x1, y0, y1 = xs[i], xs[i + 1], ys[i], ys[i + 1]
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def to_design(t_out):
    """Output (VO) time -> design time used by the renderer."""
    return _interp(t_out, _V, _D)


def to_out(t_design):
    """Design time -> output (VO) time, e.g. for SFX cues."""
    return _interp(t_design, _D, _V)
