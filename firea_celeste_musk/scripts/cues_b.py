"""Style B — "Fresh Kinetic". Timing for render_video_b.py and make_audio_b.py.
Dialog/footage untouched; times are on the source timeline (seconds).
"""
from cues import DURATION, FOOTAGE_END, SCENE_CUT  # noqa: F401

# kinetic caption chunks: (start, TEXT). Each shows until the next starts.
# Word times are estimated from speech energy, not forced alignment.
CHUNKS = [
    (0.00, "SUKA BUAT"), (0.84, "AKTIVITI"), (1.58, "DEKAT LUAR,"),
    (2.56, "TAPI TAKUT"), (3.77, "KAWAN TEGUR"), (5.14, "BAU BADAN."),
    (6.51, "PELUH BANYAK"), (7.80, "TAKPE,"), (8.49, "TAPI"),
    (8.99, "JANGAN"), (9.56, "BAU BADAN SAJA."), (10.84, "MEMANG AKAN BUAT"),
    (12.20, "KITA RASA"), (12.85, "TAK SELESA."), (13.62, "ORANG SEBELAH PUN"),
    (14.58, "MEMANG TAK"), (15.15, "AKAN MAHU"), (15.66, "DEKAT DENGAN KITA."),
    (16.77, "FIREA"), (17.40, "PUNYA POWER,"), (18.49, "KAWAL PELUH,"),
    (19.60, "HILANG TERUS"), (20.85, "BAU BADAN."), (21.91, "SO KORANG"),
    (22.47, "YANG MANA"), (23.03, "JENIS"), (23.38, "KUAT BERPELUH TU,"),
    (24.44, "TAKUT BADAN"), (26.05, "BERBAU,"), (27.11, "KORANG PAKAI JE"),
    (28.19, "FIREA NI."), (28.85, "MEMANG POWER."),
]
CAPTION_END = 30.30
PINK_WORDS = ["AKTIVITI", "BAU BADAN", "TAKPE", "JANGAN", "TAK SELESA", "FIREA", "POWER",
              "KAWAL PELUH", "HILANG", "BERPELUH", "BERBAU"]

# jump-zoom per spoken phrase: (time, scale). Hard cut between values, slow drift inside.
JUMPS = [(0.00, 1.10), (1.58, 1.02), (2.56, 1.08), (5.14, 1.24), (6.51, 1.02), (8.99, 1.12),
         (10.84, 1.04), (12.20, 1.10), (13.62, 1.03), (15.66, 1.12), (17.13, 1.00), (18.49, 1.08),
         (19.60, 1.02), (21.91, 1.10), (23.38, 1.03), (24.44, 1.12), (27.11, 1.00)]

# graphics
SUN = (0.05, 2.50)
STINK = [(5.14, 6.45), (9.56, 10.84), (19.60, 21.0), (24.44, 27.05)]   # wavy odour lines
NO_SIGN = (8.99, 10.84)              # prohibition sign over odour icon
DROPS = [(6.51, 8.49), (18.49, 19.55), (23.38, 24.44)]                 # sweat drops
OK_BADGE = (7.80, 8.95)              # ✓ on "TAKPE"
SPARKLE_WIPE = [(19.05, "drops"), (20.85, "stink")]                 # Firea clears them
GLITCH = (12.85, 13.20)
GRADE_COOL = (12.20, 17.13)
SHAKE = [5.14, 12.85]
WHIP = (16.95, 17.32)                # whip-pan across the existing cut
HERO = (17.15, 17.80)                # bottle hero, then flies to a badge
BADGE_END = 27.05
END = 27.11
CTA = 28.00
CLAIMS = 28.50
CTA_TEXT = "DAPATKAN FIREA SEKARANG"   # TEMP — replace with the real CTA
