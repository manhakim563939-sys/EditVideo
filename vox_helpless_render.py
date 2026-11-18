"""Episode — "Kenapa Kita Ulang Kesalahan Yang Sama?" (~74 s, learned helplessness, 1080x1920@30), Vox-explainer style.

Cream paper with a faint grid, serif headlines with a yellow highlighter, typewriter kickers,
torn-paper cards, red marker circles, hand-made diagrams (clock, dopamine loop, slot machine,
endless feed, checklist) — diagrams for this episode: repeat loop, Seligman card, spreading
failure map, iceberg, cracking wall). One calm pose per chapter, cross-faded.). MAN is a black & white paper cut-out (contrast with the colour story),
changing pose per beat. Word-by-word captions from the ElevenLabs timestamps.

Usage: python3 vox_helpless_render.py <workdir> <out.mp4|prefix.jpg> [t ...]   (workdir needs pose/*)
"""
import json
import math
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

WD, OUT = sys.argv[1], sys.argv[2]
W, H, FPS = 1080, 1920, 30
WORDS = json.load(open("assets/vo_helpless_words.json"))
DUR = WORDS[-1][2] + 0.9
N = int(DUR * FPS)


def to_design(t_out):
    return t_out


CREAM = (242, 235, 221)
INK = (24, 22, 20)
YEL = (255, 212, 0)
RED = (220, 58, 40)
BLUE = (50, 100, 180)
WHITE = (255, 255, 255)
FD = "assets/fonts/"
_fc = {}


def font(name, size):
    if (name, size) not in _fc:
        p = FD + name + ".woff" if not name.startswith("Inter") else "/usr/share/fonts/opentype/inter/" + name + ".otf"
        _fc[(name, size)] = ImageFont.truetype(p, size)
    return _fc[(name, size)]


SERIF = lambda s: font("Playfair", s)
ANTON = lambda s: font("Anton", s)
TYPE = lambda s: font("Special", s)
MARK = lambda s: font("Permanent", s)
INTER = lambda s: font("Inter-ExtraBold", s)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_back(x):
    x = clamp(x)
    c = 1.7
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def paste(canvas, s, cx, cy, scale=1.0, rot=0.0, alpha=1.0):
    if alpha <= 0.01 or scale <= 0.01:
        return
    if abs(scale - 1) > 1e-3:
        s = s.resize((max(1, int(s.width * scale)), max(1, int(s.height * scale))), Image.BILINEAR)
    if abs(rot) > 0.05:
        s = s.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        s = s.copy()
        s.putalpha(s.split()[3].point(lambda v: int(v * alpha)))
    x, y = int(cx - s.width / 2), int(cy - s.height / 2)
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + s.width), min(H, y + s.height)
    if x1 > x0 and y1 > y0:
        canvas.alpha_composite(s.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))


def pop(c, s, t, t0, cx, cy, rot=0.0, dur=0.35):
    if t >= t0:
        u = ease_back((t - t0) / dur)
        paste(c, s, cx, cy, scale=max(0.01, u), rot=rot)


def shadowed(im, off=(10, 14), blur=10, a=0.35):
    pad = 40
    out = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, int(255 * a)), (pad + off[0], pad + off[1]), im.split()[3])
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    out.alpha_composite(im, (pad, pad))
    return out


def torn(w, h, seed, col=WHITE):
    rng = np.random.default_rng(seed)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pts = []
    for x in range(0, w + 1, 16):
        pts.append((x, 8 + rng.uniform(-6, 6)))
    for y in range(0, h + 1, 16):
        pts.append((w - 8 + rng.uniform(-6, 6), y))
    for x in range(w, -1, -16):
        pts.append((x, h - 8 + rng.uniform(-6, 6)))
    for y in range(h, -1, -16):
        pts.append((8 + rng.uniform(-6, 6), y))
    ImageDraw.Draw(im).polygon(pts, fill=col)
    return im


def label(text, f, fg, bg, padx=26, pady=14, hl=None):
    b = f.getbbox(text)
    w, h = b[2] - b[0] + 2 * padx, b[3] - b[1] + 2 * pady
    im = Image.new("RGBA", (w, h), bg)
    ImageDraw.Draw(im).text((padx - b[0], pady - b[1]), text, font=f, fill=fg)
    return shadowed(im, (6, 8), 6, 0.3)


def headline(lines, size=96, hl_line=None):
    f = SERIF(size)
    sps = []
    for j, l in enumerate(lines):
        b = f.getbbox(l)
        w, h = b[2] - b[0] + 40, b[3] - b[1] + 34
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        if j == hl_line:  # yellow highlighter stroke
            d.rectangle((6, h * 0.42, w - 6, h - 6), fill=YEL + (230,))
        d.text((20 - b[0], 14 - b[1]), l, font=f, fill=INK)
        sps.append(im)
    w = max(s.width for s in sps)
    out = Image.new("RGBA", (w, sum(s.height for s in sps)), (0, 0, 0, 0))
    y = 0
    for s in sps:
        out.alpha_composite(s, ((w - s.width) // 2, y))
        y += s.height
    return out


def kicker(text):
    return label(text, TYPE(40), WHITE, INK, 22, 12)


# ---------------------------------------------------------------- background
def make_bg():
    rng = np.random.default_rng(4)
    base = np.ones((H, W, 3), np.float32) * np.array(CREAM, np.float32)
    n = cv2.GaussianBlur(rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32), (0, 0), 2)
    base += cv2.resize(n, (W, H))[..., None] * 6
    base += rng.normal(0, 3.5, (H, W, 1))
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(im)
    for x in range(0, W, 60):
        d.line((x, 0, x, H), fill=(120, 140, 170, 28), width=2)
    for y in range(0, H, 60):
        d.line((0, y, W, y), fill=(120, 140, 170, 28), width=2)
    return im


BG = make_bg()


# ---------------------------------------------------------------- narrator (B&W paper cut-out)
def bw(rgb):
    g = (rgb[..., 0] * 0.30 + rgb[..., 1] * 0.59 + rgb[..., 2] * 0.11).astype(np.uint8)
    g = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(g).astype(np.float32) / 255
    g = 0.5 + 0.5 * np.tanh(2.2 * (g - 0.5)) / math.tanh(1.1)
    return np.repeat(np.clip(g * 255, 0, 255)[..., None], 3, axis=2)


def cutout(name, target_w=820, max_h=1040):
    im = np.asarray(Image.open(f"{WD}/pose/{name}.jpg").convert("RGB")).astype(np.float32)
    m = np.asarray(Image.open(f"{WD}/pose/{name}_mask.png").convert("L")).astype(np.float32) / 255
    m = np.clip((m - 0.3) / 0.4, 0, 1)
    n, lab, st, _ = cv2.connectedComponentsWithStats((m > 0.5).astype(np.uint8))
    if n > 2:
        m = m * (lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])))
    ys, xs = np.where(m > 0.5)
    im, m = im[ys.min():, xs.min():xs.max() + 1], m[ys.min():, xs.min():xs.max() + 1]
    pad = 24
    im = cv2.copyMakeBorder(bw(im), pad, 0, pad, pad, cv2.BORDER_CONSTANT, value=0)
    m = cv2.copyMakeBorder(m, pad, 0, pad, pad, cv2.BORDER_CONSTANT, value=0)
    k = target_w / im.shape[1]
    im = cv2.resize(im, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
    m = cv2.resize(m, None, fx=k, fy=k)
    ol = cv2.dilate((m > 0.5).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (23, 23)))
    ol = cv2.GaussianBlur(ol.astype(np.float32), (0, 0), 1.0)
    rgb = im * m[..., None] + 255 * (1 - m[..., None])
    spr = Image.fromarray(np.dstack([rgb, np.maximum(m, ol) * 255]).astype(np.uint8), "RGBA")
    spr = spr.crop((0, 0, spr.width, min(spr.height, max_h)))
    return shadowed(spr, (12, 16), 12, 0.4)


POSES = ["d_garu", "d_serius", "d_kejut", "d_sisi", "d_tunjuk", "d_senyum"]
CUT = {n: cutout(n) for n in POSES}
TIMELINE = [(0.0, "d_garu"), (8.1, "d_serius"), (22.4, "d_kejut"), (32.1, "d_sisi"), (43.7, "d_tunjuk"), (63.3, "d_senyum")]


# emotion beats: the pose follows the word being spoken
EMO = []  # no quick emotion swaps in this episode — one calm pose per chapter


def pose_at(t):
    for a, b, n in EMO:
        if a <= t < b:
            return (a, n)
    for a, b, n in EMO:  # coming back from an emotion beat re-triggers the entrance
        if b <= t < b + 0.45:
            base = [e for e in TIMELINE if e[0] <= t][-1]
            return (b, base[1])
    cur = TIMELINE[0]
    for e in TIMELINE:
        if t >= e[0]:
            cur = e
    return cur


def load_icon(n, size=300):
    im = Image.open(f"{WD}/ic/{n}.png").convert("RGBA")
    k = size / max(im.width, im.height)
    return shadowed(im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS), (8, 10), 8, 0.35)


ICON_CUES = [  # (word time, icon) — pops beside MAN's head while the word is said
    (0.5, "x_merah"), (4.4, "ulang"), (9.4, "topi"), (12.7, "mangga"), (15.2, "x_merah"), (17.0, "rantai"),
    (18.4, "otak"), (20.2, "lengan"), (24.5, "otak"), (26.9, "beg_kerja"), (28.4, "salam"), (32.8, "mentol"),
    (37.9, "bongkah_ais"), (41.2, "kilat"), (43.8, "tunas"), (45.6, "topi"), (48.0, "tukul"),
    (49.3, "pembesar_suara"), (56.2, "simpang"), (60.8, "tukul"), (62.0, "rantai_putus"), (64.2, "lengan"),
    (67.8, "topi"), (69.1, "kunci"),
]
ICONS = {n: load_icon(n) for _, n in ICON_CUES}


def draw_icons(c, t):
    for k, (t0, n) in enumerate(ICON_CUES):
        hold = min(1.5, (ICON_CUES[k + 1][0] - t0) if k + 1 < len(ICON_CUES) else 1.5)
        if t0 - 0.05 <= t < t0 + hold:
            u = ease_back((t - t0 + 0.05) / 0.3)
            out = clamp((t - (t0 + hold - 0.2)) / 0.2)
            side = -1 if k % 2 == 0 else 1
            x = W / 2 + 40 + side * 340
            y = 1180 + 10 * math.sin(t * 5 + k)
            paste(c, ICONS[n], x, y, scale=max(0.01, u * (1 - out)), rot=side * -8 + 4 * math.sin(t * 3 + k))


def draw_man(c, t):
    idx = max(i for i, e in enumerate(TIMELINE) if t >= e[0])
    t0, name = TIMELINE[idx]
    u = ease_out((t - t0) / 0.7) if idx else ease_out((t - 0.1) / 0.8)
    breathe = 5 * math.sin(t * 1.1)
    if idx and u < 1:
        prev = CUT[TIMELINE[idx - 1][1]]
        paste(c, prev, W / 2 + 40, H - prev.height / 2 + 190 + breathe, alpha=1 - u)
    spr = CUT[name]
    paste(c, spr, W / 2 + 40, H - spr.height / 2 + 190 + 40 * (1 - u) + breathe, alpha=u)


# ---------------------------------------------------------------- diagrams
def clock(t, t0):
    s = 420
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((10, 10, s - 10, s - 10), fill=WHITE, outline=INK, width=12)
    for k in range(12):
        a = k * math.pi / 6
        r0, r1 = s / 2 - 40, s / 2 - 24
        d.line((s / 2 + r0 * math.sin(a), s / 2 - r0 * math.cos(a), s / 2 + r1 * math.sin(a), s / 2 - r1 * math.cos(a)),
               fill=INK, width=8)
    p = ease_out((t - t0) / 1.4)
    am = p * 2 * math.pi * 1  # minute hand: one full hour
    ah = p * math.pi / 6
    d.line((s / 2, s / 2, s / 2 + 150 * math.sin(am), s / 2 - 150 * math.cos(am)), fill=RED, width=12)
    d.line((s / 2, s / 2, s / 2 + 95 * math.sin(ah), s / 2 - 95 * math.cos(ah)), fill=INK, width=16)
    d.ellipse((s / 2 - 16, s / 2 - 16, s / 2 + 16, s / 2 + 16), fill=INK)
    return shadowed(im)


def molecule():
    s = 330
    im = Image.new("RGBA", (s + 160, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy, r = 190, s / 2, 95
    pts = [(cx + r * math.cos(math.pi / 6 + k * math.pi / 3), cy + r * math.sin(math.pi / 6 + k * math.pi / 3)) for k in range(6)]
    d.polygon(pts, outline=INK, width=9)
    d.ellipse((cx - 50, cy - 50, cx + 50, cy + 50), outline=INK, width=6)
    d.line((pts[5], (pts[5][0] + 70, pts[5][1] - 40), (pts[5][0] + 150, pts[5][1] + 5)), fill=INK, width=9)
    f = TYPE(44)
    d.text((pts[5][0] + 150, pts[5][1] - 20), "NH2", font=f, fill=INK)
    d.line((pts[3], (pts[3][0] - 60, pts[3][1] - 40)), fill=INK, width=9)
    d.text((pts[3][0] - 125, pts[3][1] - 95), "HO", font=f, fill=INK)
    d.line((pts[2], (pts[2][0] - 50, pts[2][1] + 50)), fill=INK, width=9)
    d.text((pts[2][0] - 120, pts[2][1] + 40), "HO", font=f, fill=INK)
    return im


def slot(t, t0, stop_t):
    w, h = 640, 420
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 40, w - 70, h), 34, fill=RED, outline=INK, width=10)
    d.rounded_rectangle((60, 0, w - 130, 80), 24, fill=YEL, outline=INK, width=8)
    ft = ANTON(52)
    d.text((w / 2 - 35 - ft.getlength("JACKPOT?") / 2, 8), "JACKPOT?", font=ft, fill=INK)
    # lever
    d.line((w - 70, 200, w - 20, 200), fill=INK, width=14)
    d.line((w - 20, 200, w - 20, 90), fill=INK, width=14)
    d.ellipse((w - 48, 60, w + 8, 116), fill=INK)
    syms = ["7", "?", "$", "!", "♥"]
    f = ANTON(130)
    for k in range(3):
        x0 = 50 + k * 175
        d.rectangle((x0, 130, x0 + 150, 360), fill=WHITE, outline=INK, width=8)
        spinning = t < stop_t + k * 0.35
        sym = syms[int((t - t0) * 14 + k * 2) % len(syms)] if spinning else "?"
        col = INK if spinning else RED
        d.text((x0 + 75 - f.getlength(sym) / 2, 140), sym, font=f, fill=col)
    return shadowed(im)


def feed(t):
    w, h = 400, 640
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w, h), 50, fill=INK)
    scr = Image.new("RGBA", (w - 40, h - 80), (250, 250, 250, 255))
    sd = ImageDraw.Draw(scr)
    off = (t * 420) % 230
    cols = [(255, 120, 90), (90, 160, 230), (250, 200, 60), (120, 200, 140), (200, 120, 220)]
    for k in range(-1, 5):
        y = k * 230 - off
        sd.rounded_rectangle((16, y + 14, w - 56, y + 160), 18, fill=cols[(k + int(t * 420 // 230)) % 5])
        sd.rectangle((16, y + 172, w - 120, y + 186), fill=(200, 200, 200))
        sd.rectangle((16, y + 196, w - 180, y + 210), fill=(220, 220, 220))
    im.alpha_composite(scr, (20, 40))
    return shadowed(im)


def checklist(t, times, items):
    w, h = 860, 420
    im = torn(w, h, 9)
    d = ImageDraw.Draw(im)
    f = SERIF(56)
    for k, (tt, it) in enumerate(zip(times, items)):
        y = 50 + k * 120
        d.rectangle((50, y, 120, y + 70), outline=INK, width=7)
        if t >= tt:
            p = ease_out((t - tt) / 0.3)
            x1, y1 = 60 + 22 * p, y + 35 + 22 * p
            d.line((60, y + 35, x1, y1), fill=RED, width=12)
            if p > 0.5:
                q = (p - 0.5) * 2
                d.line((82, y + 57, 82 + 50 * q, y + 57 - 60 * q), fill=RED, width=12)
            d.text((150, y), it, font=f, fill=INK)
    return shadowed(im)


def marker_circle(c, t, t0, cx, cy, rx, ry, dur=0.5):
    if t < t0:
        return
    p = ease_out((t - t0) / dur)
    d = ImageDraw.Draw(c)
    pts = [(cx + rx * math.cos(a) * (1 + 0.04 * math.sin(5 * a)), cy + ry * math.sin(a))
           for a in np.linspace(-2.2, -2.2 + 2 * math.pi * 1.08 * p, 60)]
    d.line(pts, fill=RED + (235,), width=12, joint="curve")


def underline(c, t, t0, x0, x1, y, dur=0.3):
    if t < t0:
        return
    p = ease_out((t - t0) / dur)
    ImageDraw.Draw(c).line((x0, y, x0 + (x1 - x0) * p, y + 4), fill=RED + (235,), width=12)


# ---------------------------------------------------------------- captions
def caption_groups():
    groups, cur = [], []
    for w in WORDS:
        cur.append(w)
        if len(cur) >= 4 or w[0][-1] in ".?!,":
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    return groups


GROUPS = caption_groups()
F_CAP = font("Inter-Black", 60)


def draw_captions(c, t):
    g = None
    for gr in GROUPS:
        if gr[0][1] - 0.05 <= t <= gr[-1][2] + 0.2:
            g = gr
    if g is None:
        return
    words = [w[0] for w in g]
    widths = [F_CAP.getlength(w) for w in words]
    sp = 18
    total = sum(widths) + sp * (len(words) - 1)
    x = W / 2 - total / 2
    y = 1770
    if t < g[0][1] - 0.03:
        return
    d = ImageDraw.Draw(c)
    d.rectangle((x - 26, y - 22, x + total + 26, y + 86), fill=WHITE + (245,))
    for i, w in enumerate(words):
        st, en = g[i][1], g[i][2]
        if t >= st - 0.03:
            if st - 0.03 <= t <= en + 0.1:
                d.rectangle((x - 8, y - 6, x + widths[i] + 8, y + 72), fill=YEL)
            d.text((x, y - 4), w, font=F_CAP, fill=INK)
        x += widths[i] + sp


# ---------------------------------------------------------------- episode diagrams
def loop_arrows(t, t0):
    s = 460
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rot = (t - t0) * 120
    d.arc((40, 40, s - 40, s - 40), rot, rot + 300, fill=RED, width=22)
    a = math.radians(rot + 300)
    cx, cy, r = s / 2, s / 2, s / 2 - 40
    x, y = cx + r * math.cos(a), cy + r * math.sin(a)
    d.ellipse((x - 26, y - 26, x + 26, y + 26), fill=RED)
    f = ANTON(70)
    d.text((s / 2 - f.getlength("ULANG") / 2, s / 2 - 70), "ULANG", font=f, fill=INK)
    n = min(9, int(max(0, t - t0) * 2.2) + 1)
    d.text((s / 2 - f.getlength(f"x{n}") / 2, s / 2 + 10), f"x{n}", font=f, fill=RED)
    return im


def name_card():
    w, h = 820, 260
    im = torn(w, h, 81)
    d = ImageDraw.Draw(im)
    d.text((50, 40), "MARTIN SELIGMAN", font=ANTON(76), fill=INK)
    d.text((52, 150), "Ahli psikologi, University of Pennsylvania", font=TYPE(30), fill=INK)
    return shadowed(im)


def spread_map(t, t0):
    w, h = 900, 460
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = w / 2, h / 2
    f = ANTON(44)
    tg = [("KERJA", 110, 70, 26.9), ("BISNES", w - 110, 70, 27.7), ("HUBUNGAN", 140, h - 60, 28.4),
          ("KESIHATAN", w - 150, h - 60, 29.3)]
    for lab, x, y, tt in tg:
        if t < tt:
            continue
        p = ease_out((t - tt) / 0.35)
        d.line((cx, cy, cx + (x - cx) * p, cy + (y - cy) * p), fill=RED, width=8)
        if p > 0.9:
            bw_ = f.getlength(lab) + 30
            d.rectangle((x - bw_ / 2, y - 34, x + bw_ / 2, y + 34), fill=WHITE, outline=RED, width=6)
            d.text((x - bw_ / 2 + 15, y - 30), lab, font=f, fill=INK)
    d.ellipse((cx - 120, cy - 70, cx + 120, cy + 70), fill=RED, outline=INK, width=6)
    d.text((cx - f.getlength("GAGAL") / 2, cy - 30), "GAGAL", font=f, fill=WHITE)
    return im


def iceberg(t, t0):
    w, h = 820, 560
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    wl = 170
    d.rectangle((0, wl, w, h), fill=(120, 170, 210, 200))
    d.polygon([(w / 2 - 110, wl), (w / 2 - 30, 40), (w / 2 + 40, 70), (w / 2 + 120, wl)], fill=WHITE, outline=INK)
    d.polygon([(w / 2 - 110, wl), (w / 2 + 120, wl), (w / 2 + 300, h - 60), (w / 2 - 280, h - 30)], fill=(225, 238, 248), outline=INK)
    d.line((0, wl, w, wl), fill=INK, width=4)
    f = ANTON(46)
    if t > t0:
        d.text((w / 2 + 150, 80), "NIAT (SEDAR)", font=f, fill=INK)
    if t > t0 + 2.6:
        d.text((w / 2 - 230, wl + 170), "KESIMPULAN LAMA", font=f, fill=RED)
        d.text((w / 2 - 170, wl + 230), "(bawah sedar)", font=TYPE(36), fill=INK)
    return im


def crack_wall(t, t0):
    w, h = 800, 380
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for r in range(5):
        for c in range(7):
            off = 57 if r % 2 else 0
            x, y = c * 114 - off, r * 74
            d.rectangle((x + 4, y + 4, x + 110, y + 70), fill=(190, 120, 90), outline=INK, width=3)
    f = ANTON(60)
    d.rectangle((150, 140, 650, 230), fill=INK)
    d.text((w / 2 - f.getlength("KESIMPULAN LAMA") / 2, 146), "KESIMPULAN LAMA", font=f, fill=WHITE)
    p = clamp((t - t0) / 1.0)
    if p > 0:
        pts = [(400, 0), (370, 60), (420, 120), (380, 190), (430, 260), (390, 320), (420, 380)]
        n = max(2, int(len(pts) * p))
        d.line(pts[:n], fill=YEL, width=12)
        d.line(pts[:n], fill=INK, width=4)
    return shadowed(im)


# ---------------------------------------------------------------- sections
S = dict(hook=0.0, b1=8.2, b2=22.5, b3=32.2, b4=43.8, cta=63.4)
CH = {k: kicker(v) for k, v in [("b1", "BAB 1 · LEARNED HELPLESSNESS"), ("b2", "BAB 2 · IA MEREBAK"),
                                  ("b3", "BAB 3 · KENAPA NIAT TAK CUKUP"), ("b4", "BAB 4 · CARA PATAHKAN"),
                                  ("hook", "EXPLAINER"), ("cta", "KESIMPULAN")]}
HL = {
    "hook": headline(["Kenapa kita ulang", "kesalahan sama?"], 86, 1),
    "b1": headline(["Otak belajar", "putus asa"], 104, 1),
    "b2": headline(["Gagal satu tempat,", "rasa gagal semua"], 84, 1),
    "b3": headline(["Niat di atas,", "kesimpulan di bawah"], 86, 1),
    "b4": headline(["Ingatan lama,", "bukan ramalan"], 96, 1),
    "cta": headline(["Apa yang dipelajari,", "boleh diubah"], 84, 1),
}
CARDS = {
    "niat": label("BUKAN SEBAB KURANG NIAT", ANTON(58), WHITE, RED),
    "term": label("LEARNED HELPLESSNESS", ANTON(64), INK, YEL),
    "usaha": label("USAHA = TIADA HASIL ?", ANTON(58), WHITE, INK),
    "beza": label("WALAUPUN SITUASI DAH BERBEZA", INTER(38), INK, YEL),
    "cepat": label("RESPONS LAMA LEBIH CEPAT", ANTON(56), WHITE, RED),
    "percuma": label("\"PERCUMA, HASIL SAMA\"", ANTON(58), WHITE, INK),
    "bukti": label("1 BUKTI KECIL", ANTON(64), INK, YEL),
    "follow": label("FOLLOW UNTUK PSIKOLOGI DIRI", ANTON(50), INK, YEL),
}


def section(t):
    return max((v, k) for k, v in S.items() if t >= v)[1]


def draw_section(c, t):
    k = section(t)
    t0 = S[k]
    lt = t - t0
    paste(c, CH[k], W / 2, 120, scale=max(0.01, ease_back(lt / 0.3)))
    u = ease_out((lt - 0.1) / 0.4)
    paste(c, HL[k], W / 2, 290 + 40 * (1 - u), alpha=u)
    if k == "hook":
        if t > 0.6:
            paste(c, loop_arrows(t, 0.6), W / 2, 650, scale=ease_back((t - 0.6) / 0.4))
        pop(c, CARDS["niat"], t, 6.2, W / 2, 930, rot=-2)
    elif k == "b1":
        pop(c, name_card(), t, 9.0, W / 2, 560, rot=-2)
        pop(c, CARDS["term"], t, 12.3, W / 2, 740, rot=2)
        pop(c, CARDS["usaha"], t, 20.2, W / 2, 920, rot=-2)
    elif k == "b2":
        if t > 23.7:
            paste(c, spread_map(t, 23.7), W / 2, 670, alpha=ease_out((t - 23.7) / 0.4))
        pop(c, CARDS["beza"], t, 29.3, W / 2, 940, rot=1)
    elif k == "b3":
        if t > 32.8:
            paste(c, iceberg(t, 34.6), W / 2, 690, scale=ease_back((t - 32.8) / 0.4))
        pop(c, CARDS["cepat"], t, 40.6, W / 2, 950, rot=-2)
    elif k == "b4":
        if t < 53.4:
            pop(c, CARDS["percuma"], t, 50.7, W / 2, 620, rot=-3)
            if t > 53.0:
                pass
        if t > 52.4:
            p = ease_out((t - 52.4) / 0.4)
            if t < 56.0:
                ImageDraw.Draw(c).line((W / 2 - 300, 640, W / 2 - 300 + 600 * p, 600), fill=RED, width=16)
        if t > 56.0:
            paste(c, crack_wall(t, 60.8), W / 2, 650, scale=ease_back((t - 56.0) / 0.4))
            pop(c, CARDS["bukti"], t, 59.2, W / 2, 920, rot=3)
    elif k == "cta":
        if t > 63.8:
            d = ImageDraw.Draw(c)
            f = SERIF(100)
            s1 = "LEMAH"
            x0 = W / 2 - f.getlength(s1) / 2
            d.text((x0, 540), s1, font=f, fill=INK)
            p = ease_out((t - 64.2) / 0.4)
            d.line((x0 - 10, 600, x0 - 10 + (f.getlength(s1) + 20) * p, 590), fill=RED, width=16)
        if t > 65.4:
            paste(c, label("CUMA BELAJAR YANG SALAH", ANTON(70), INK, YEL), W / 2, 740,
                  scale=ease_back((t - 65.4) / 0.35), rot=-2)
        pop(c, CARDS["follow"], t, 70.2, W / 2, 920, rot=2)


def frame(fi):
    t = to_design(fi / FPS)
    c = BG.copy()
    draw_section(c, t)
    draw_man(c, t)
    draw_icons(c, t)
    draw_captions(c, t)
    # section wipe: a strip of paper sweeps across on each chapter change
    for v in list(S.values())[1:]:
        d = t - v
        if -0.2 < d < 0.15:
            p = (d + 0.2) / 0.35
            x = int(-W + p * 2 * W)
            strip = torn(W, H + 60, int(v * 10), col=(236, 228, 212))
            c.alpha_composite(strip, (x, -30)) if -W < x < W else None
    rgb = np.asarray(c.convert("RGB")).astype(np.float32)
    rgb += np.random.default_rng(fi % 6).normal(0, 4, (H, W, 1))
    return np.clip(rgb, 0, 255).astype(np.uint8)


if __name__ == "__main__":
    if OUT.endswith(".jpg"):
        for ts in sys.argv[3:]:
            Image.fromarray(frame(int(float(ts) * FPS))).save(OUT.replace(".jpg", f"_{ts}.jpg"), quality=85)
        sys.exit()
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "24",
                          "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
    for fi in range(N):
        p.stdin.write(frame(fi).tobytes())
    p.stdin.close()
    p.wait()
