"""Style D — "Glam Beauty". Timing for render_video_glam.py and make_audio_glam.py.
Dialog/footage untouched; times are on the source timeline (seconds).
"""
from cues import CAPTIONS, DURATION, FOOTAGE_END, SCENE_CUT  # noqa: F401

CAP_HL = ["aktiviti", "luar", "tegur", "bau badan", "takpe", "tak selesa", "Firea", "power",
          "kawal peluh", "hilang terus", "kuat berpeluh", "berbau"]

# glass cards: (start, end, line1 [serif], line2 [script], y, script_delay)
CARDS = [
    (0.15, 2.50, "Suka aktiviti", "di luar?", 300, 0.55),
    (2.60, 5.05, "Takut kawan", "tegur?", 300, 1.15),
    (5.14, 6.42, "Bau", "badan?", 300, 0.15),
    (12.85, 16.90, "Rasa", "tak selesa", 300, 0.25),
    (23.03, 27.00, "Kuat berpeluh?", "takut berbau?", 300, 1.40),
]
# two stacked pills (serif text + script word)
PILLS = [(6.55, 11.35, "Peluh banyak,", "takpe", 230),
         (9.05, 11.35, "Bau badan,", "jangan", 370)]

# line-drawn rose-gold frames: (start, end, kind)
FRAMES = [(0.30, 2.50, "face"), (17.35, 21.80, "bottle")]

LEAK_FLASH = [0.0, 6.50, 12.20, 17.13, 27.11]     # light-leak sweeps (also whoosh SFX)
COOL = (12.20, 17.13)                             # dimmer, cooler, bokeh slows
BRAND = (17.20, 21.85)                            # Firea script title
CHIP1 = 18.49                                     # Kawal peluh
CHIP2 = 19.60                                     # Hilang terus bau badan
END = 27.15
CLAIMS = 28.20
CTA = 28.85
CTA_TEXT = "Dapatkan sekarang"   # TEMP — replace with the real CTA

# soft push-ins (eased, no hard cuts): (time, scale, focus_x, focus_y)
ZOOM_KEYS = [
    (0.0, 1.12, 540, 700), (5.0, 1.04, 540, 700), (5.6, 1.13, 540, 640), (6.5, 1.04, 540, 700),
    (12.2, 1.04, 540, 700), (17.12, 1.12, 540, 700), (17.13, 1.08, 540, 900), (21.8, 1.00, 540, 900),
    (27.0, 1.06, 540, 900), (31.0, 1.02, 540, 900),
]
