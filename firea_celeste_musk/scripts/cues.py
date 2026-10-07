"""Single source of truth for timing. Video overlays AND audio SFX read these cues,
so motion and sound stay in sync. Edit text/timing here, then re-run build.sh.

Times are seconds on the source footage timeline (dialog is untouched).
"""

DURATION = 31.0          # 29.88s footage + ~1.1s held end card for the CTA
FOOTAGE_END = 29.85
SCENE_CUT = 17.133       # hard cut already in the footage (product shot begins)

# ---- captions: dialog as spoken (transcribed locally, then corrected by ear-less review)
# [start, end, text] ; words in HILITE are coloured
CAPTIONS = [
    [0.00, 1.58, "Suka buat aktiviti"],
    [1.58, 2.56, "dekat luar,"],
    [2.56, 5.14, "tapi takut kawan tegur"],
    [5.14, 6.40, "bau badan."],
    [6.51, 8.98, "Peluh banyak takpe, tapi"],
    [8.99, 10.84, "jangan bau badan saja."],
    [10.84, 12.20, "Memang akan buat"],
    [12.20, 13.62, "kita rasa tak selesa."],
    [13.62, 14.58, "Orang sebelah pun"],
    [14.58, 15.66, "memang tak akan mahu"],
    [15.66, 16.72, "dekat dengan kita."],
    [16.77, 18.49, "Firea punya power,"],
    [18.49, 19.57, "kawal peluh,"],
    [19.60, 21.91, "hilang terus bau badan."],
    [21.91, 23.03, "So korang yang mana"],
    [23.03, 24.44, "jenis kuat berpeluh tu,"],
    [24.44, 27.11, "takut badan berbau,"],
    [27.11, 28.85, "korang pakai je Firea ni."],
    [28.85, 30.40, "Memang power."],
]
HILITE = ["aktiviti", "bau badan", "takpe", "tak selesa", "Firea", "power",
          "kawal peluh", "hilang terus", "kuat berpeluh", "berbau"]

# ---- overlay beats
HOOK = (0.10, 2.50)                 # "Suka aktiviti luar?"
BAU = (5.14, 6.42)                  # big "BAU BADAN?" + punch-in
CHECK_ROW1 = 6.55                   # Peluh banyak ✓ takpe
CHECK_ROW2 = 9.05                   # Bau badan ✗ jangan!
CHECK_END = 11.30
SELESA = (12.45, 16.80)             # "TAK SELESA" + cool/desaturated grade
GRADE_COOL = (12.20, 17.13)
BRAND = (17.25, 21.80)              # Firea / Celeste Musk + bottle sticker
CHIP1 = 18.55                       # Kawal peluh
CHIP2 = 19.70                       # Hilang bau badan
Q1 = (23.05, 27.00)                 # Kuat berpeluh?
Q2 = 24.50                          # Takut badan berbau?
END = 27.15                         # Pakai je Firea + bottle
CTA = 28.05                         # CTA pill
CLAIMS = 28.55                      # 0% Alkohol · 0% Paraben (from label)

CTA_TEXT = "Dapatkan Firea sekarang"   # TEMP — replace with the real CTA

# punch-in keyframes: (time, scale, focus_x, focus_y) — focus is kept on the face
ZOOM_KEYS = [
    (0.00, 1.10, 540, 700), (2.50, 1.04, 540, 700),
    (5.13, 1.04, 540, 700), (5.14, 1.20, 540, 620), (6.45, 1.20, 540, 620),
    (6.46, 1.03, 540, 700), (9.04, 1.03, 540, 700), (9.05, 1.10, 540, 680),
    (12.20, 1.06, 540, 700), (16.95, 1.13, 540, 700), (17.13, 1.16, 540, 900),
    (17.60, 1.00, 540, 900), (21.90, 1.03, 540, 900), (23.05, 1.08, 560, 880),
    (27.14, 1.08, 560, 880), (27.15, 1.00, 540, 900), (31.00, 1.05, 540, 900),
]
