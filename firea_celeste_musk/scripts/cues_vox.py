"""Style C — "Vox Explainer". Timing for render_video_vox.py and make_audio_vox.py.
Dialog untouched. Subject cut out onto textured paper; annotated diagrams per beat.
"""
from cues import CAPTIONS, DURATION, FOOTAGE_END, SCENE_CUT  # noqa: F401

# caption highlight (yellow marker) — first match per line
CAP_HL = {
    "Suka buat aktiviti": "aktiviti", "dekat luar,": "luar", "tapi takut kawan tegur": "tegur",
    "bau badan.": "bau badan", "Peluh banyak takpe, tapi": "takpe", "jangan bau badan saja.": "bau badan",
    "kita rasa tak selesa.": "tak selesa", "Orang sebelah pun": "Orang sebelah", "dekat dengan kita.": "dekat",
    "Firea punya power,": "Firea", "kawal peluh,": "kawal peluh", "hilang terus bau badan.": "hilang terus",
    "jenis kuat berpeluh tu,": "kuat berpeluh", "takut badan berbau,": "berbau",
    "korang pakai je Firea ni.": "Firea", "Memang power.": "power",
}

# person framing per shot: (start, scale, y_offset) — hard cuts between framings
SHOTS = [(0.00, 0.80, 170), (5.14, 1.00, 470), (6.51, 0.80, 170), (12.20, 0.72, 250),
         (17.13, 0.90, 0), (21.91, 1.00, 110), (27.11, 0.88, 30)]

# scene beats
S1 = (0.15, 2.50)          # AKTIVITI LUAR + sun doodle
S2 = (2.60, 6.42)          # Takut kawan tegur + speech bubble
STAMP_BAU = 5.14
S3 = (6.55, 11.40)         # Peluh vs Bau badan comparison card
TICK_OK = 7.80
TICK_NO = 9.05
S4 = (11.50, 16.95)        # Kesannya: tak selesa + people diagram
SELESA = 12.85
NEIGHBOURS = 13.62
MOVE_AWAY = 14.58
WIPE = (16.90, 17.30)      # paper sheet slides across the cut
S5 = (17.20, 21.85)        # product + callouts
CALL1 = 18.49              # kawal peluh — Antiperspirant
CALL2 = 19.60              # hilang bau badan — Odour & Wetness Protection
S6 = (21.95, 27.00)        # Sesuai untuk checklist
BOX1 = 23.38
BOX2 = 24.50
END = 27.15                # Pakai je Firea
CLAIMS = 28.10
STAMP_POWER = 28.85
CTA = 29.40
CTA_TEXT = "DAPATKAN SEKARANG"   # TEMP — replace with the real CTA
