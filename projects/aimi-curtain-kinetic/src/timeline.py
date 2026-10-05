"""Single source of truth for timing. Both render.py (visuals) and audio.py
(music + SFX) read these cues so motion and sound hit on the same frame.

All times are seconds on the OUTPUT timeline. The talking-head dialogue runs
untouched from 0.0 to DIALOGUE_END (same order, same speed, no cuts).
"""

FPS = 30
W, H = 1080, 1920

DIALOGUE_END = 44.879          # length of talking_head.mp4
END_CARD = 2.6                 # brand / CTA card after the last word
DURATION = DIALOGUE_END + END_CARD

# Colour roles (brief: bg #191921, text #ffffff, accent -> adapted to the
# Aimi Curtain logo gold, sampled from foto_langsir.jpg).
BG = (25, 25, 33)
TEXT = (255, 255, 255)
ACCENT = (226, 196, 128)       # brand gold, brightened for contrast on dark

# Camera cuts already inside talking_head.mp4 (frame-difference detection).
SHOTS = [0.0, 2.767, 5.583, 8.017, 11.8, 16.117, 29.967, 34.067, 37.933, 42.683, DIALOGUE_END]

# Punch-in per shot: (zoom_start, zoom_end, anchor_y). anchor_y keeps the face in frame.
SHOT_ZOOM = [
    (1.00, 1.07, 0.28),   # hook: slow push
    (1.14, 1.16, 0.25),   # jump cut -> tighter
    (1.02, 1.04, 0.28),
    (1.12, 1.15, 0.26),
    (1.00, 1.04, 0.30),   # wide standing
    (1.06, 1.10, 0.25),   # long phone shot
    (1.00, 1.05, 0.28),
    (1.00, 1.04, 0.30),   # showroom
    (1.08, 1.12, 0.30),
    (1.00, 1.06, 0.35),   # seated close
]

# Full-screen cutaways over continuous dialogue audio.
# kind, start, end, source offset
CUTAWAYS = [
    ("broll", 16.117, 20.40, 0.0),
    ("photo", 24.60, 27.60, 0.0),
]

# Kinetic text blocks. Each line: (text, style, delay_from_block_start)
# styles: H = heavy headline, HA = heavy accent, S = small regular, PILL = label
TEXT_BLOCKS = [
    dict(start=0.10, end=2.70, y=1330, lines=[("RUMAH BARU?", "H", 0.0)]),
    dict(start=2.85, end=5.50, y=1290, lines=[("NAK CERIAKAN", "H", 0.0), ("SUASANA?", "HA", 0.35)]),
    dict(start=5.65, end=7.95, y=1290, lines=[("AIMI CURTAIN", "PILL", 0.0), ("LANGSIR", "H", 0.15), ("TEMPAHAN", "HA", 0.45)]),
    # 8.0 - 11.8: no text, let the speaker breathe
    dict(start=11.95, end=15.70, y=1300, lines=[("DARI KONSULTASI", "H", 0.0), ("sampai", "S", 0.55), ("SIAP PASANG", "HA", 0.95)]),
    dict(start=16.30, end=20.25, y=1560, lines=[("HASIL KERJA AIMI CURTAIN", "PILL", 0.0)]),
    dict(start=24.75, end=27.50, y=1440, lines=[("HASIL", "H", 0.0), ("SIAP PASANG", "HA", 0.30)]),
    dict(start=34.25, end=37.80, y=1330, lines=[("BANYAK PILIHAN", "H", 0.0), ("WARNA KAIN", "HA", 0.40)]),
    dict(start=42.80, end=44.85, y=1330, lines=[("NAK LANGSIR", "H", 0.0), ("SIAP PASANG?", "HA", 0.35)]),
]

# Customer feedback screenshots (supplied by client) with a highlight sweep
# over the exact words they wrote — wording is never retyped or altered.
TESTIMONIALS = [
    dict(img="testimoni_1.jpg", start=20.50, end=24.50, hl_at=21.40,
         boxes=[(169, 45, 377, 67)]),
    dict(img="testimoni_2.jpg", start=27.70, end=31.30, hl_at=28.35,
         boxes=[(303, 93, 355, 117), (28, 118, 247, 142)]),
]
TESTIMONIAL_LABEL = "MAKLUM BALAS PELANGGAN"

# Temporary CTA (client left the CTA field empty) — flagged for approval.
END_LINES = [("AIMI CURTAIN", "H"), ("Hubungi kami untuk konsultasi langsir", "S")]

BRAND_BUG_FROM = 2.85          # small logo top-right on talking-head shots


def line_hits():
    """Times at which a text line lands (used for click SFX)."""
    hits = []
    for b in TEXT_BLOCKS:
        for text, style, d in b["lines"]:
            hits.append((b["start"] + d, style))
    return hits


def transitions():
    """Wipe-in/out moments for cutaways (whoosh SFX)."""
    t = []
    for _, s, e, _ in CUTAWAYS:
        t += [s, e]
    return t
