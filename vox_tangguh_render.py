"""Episode — "Kenapa Kita Suka Tangguh Kerja?" (~43 s, 1080x1920@30), Vox-explainer style.

Cream paper with a faint grid, serif headlines with a yellow highlighter, typewriter kickers,
torn-paper cards, red marker circles, hand-made diagrams (clock, dopamine loop, slot machine,
endless feed, checklist) — diagrams for this episode: calendar stamps, alarm sign, balance scale,
two selves, staircase + timer). MAN is a black & white paper cut-out (contrast with the colour story),
changing pose per beat. Word-by-word captions from the ElevenLabs timestamps.

Usage: python3 vox_tangguh_render.py <workdir> <out.mp4|prefix.jpg> [t ...]   (workdir needs pose/*)
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
DUR = 43.0
WORDS = json.load(open("assets/vo_tangguh_words.json"))
# The visuals are timed to the first VO; the Eleven v3 re-read (same words) is mapped onto them word by word.
V3 = json.load(open("assets/vo_tangguh_v3_words.json"))
NEW_T = [0.0] + [w[1] for w in V3] + [V3[-1][2] + 0.9]
OLD_T = [0.0] + [w[1] for w in WORDS] + [DUR]
OUT_DUR = NEW_T[-1]
N = int(OUT_DUR * FPS)


def to_design(t_out):
    return float(np.interp(t_out, NEW_T, OLD_T))

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


POSES = ["laptop", "scroll", "call", "kerja", "terang", "simpan", "serabut", "bosan", "takut", "gembira", "malas"]
CUT = {n: cutout(n) for n in POSES}
TIMELINE = [(0.0, "laptop"), (4.2, "terang"), (6.6, "laptop"), (14.7, "scroll"), (22.9, "call"),
            (29.6, "kerja"), (36.8, "terang"), (40.2, "simpan")]


# emotion beats: the pose follows the word being spoken
EMO = [(2.4, 3.2, "malas"), (5.8, 6.6, "malas"), (10.3, 11.15, "serabut"), (11.2, 12.05, "bosan"),
       (12.1, 12.9, "takut"), (16.4, 17.8, "gembira"), (21.5, 22.9, "gembira"), (37.5, 38.7, "serabut"),
       (38.8, 40.2, "gembira")]


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
    (0.5, "kotak"), (2.4, "kalendar"), (6.7, "otak"), (9.9, "kotak"), (13.8, "siren"), (15.1, "otak"),
    (17.9, "fon"), (19.0, "video"), (19.6, "makan"), (20.4, "hadiah"), (21.5, "trofi"), (24.2, "jam_pasir"),
    (26.8, "kotak"), (31.3, "kotak"), (33.2, "jam_randik"), (35.1, "otak"), (36.0, "betul"), (39.4, "kalendar"),
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
    t0, name = pose_at(t)
    spr = CUT[name]
    u = ease_back((t - t0) / 0.45)
    cy = H - spr.height / 2 + 190 + (1 - u) * 260
    rot = (1 - u) * 5 + 0.8 * math.sin(t * 1.3)
    paste(c, spr, W / 2 + 40, cy, rot=rot)


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
def calendar(word, col):
    w, h = 300, 330
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 30, w, h), fill=WHITE, outline=INK, width=8)
    d.rectangle((0, 30, w, 110), fill=col, outline=INK, width=8)
    for x in (70, w - 70):
        d.rounded_rectangle((x - 12, 0, x + 12, 60), 10, fill=INK)
    f = ANTON(96)
    d.text((w / 2 - f.getlength(word) / 2, 150), word, font=f, fill=INK)
    return shadowed(im)


def warning(t):
    s = 420
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    blink = 1 if int(t * 4) % 2 == 0 else 0.85
    col = tuple(int(v * blink) for v in YEL)
    d.polygon([(s / 2, 20), (s - 20, s - 40), (20, s - 40)], fill=col, outline=INK, width=14)
    f = ANTON(230)
    d.text((s / 2 - f.getlength("!") / 2, 70), "!", font=f, fill=INK)
    return shadowed(im)


def balance(t, t0):
    w, h = 900, 520
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    tilt = 16 * ease_back((t - t0) / 0.8) if t > t0 else 0
    cx, cy = w / 2, 150
    d.polygon([(cx, cy), (cx - 70, h - 20), (cx + 70, h - 20)], fill=INK)
    a = math.radians(tilt)
    L = 360
    x1, y1 = cx - L * math.cos(a), cy - L * math.sin(a)
    x2, y2 = cx + L * math.cos(a), cy + L * math.sin(a)
    d.line((x1, y1, x2, y2), fill=INK, width=14)
    f = ANTON(52)
    for (x, y, txt_, col) in [(x1, y1, "KERJA", WHITE), (x2, y2, "SERONOK", YEL)]:
        d.line((x, y, x - 90, y + 120), fill=INK, width=5)
        d.line((x, y, x + 90, y + 120), fill=INK, width=5)
        d.rectangle((x - 140, y + 120, x + 140, y + 200), fill=col, outline=INK, width=7)
        d.text((x - f.getlength(txt_) / 2, y + 128), txt_, font=f, fill=INK)
    ft = TYPE(36)
    d.text((x1 - 70, y1 + 210), "nanti", font=ft, fill=INK)
    d.text((x2 - 90, y2 + 210), "sekarang", font=ft, fill=RED)
    return im


def person(col, size=230):
    im = Image.new("RGBA", (size, int(size * 1.4)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = size * 0.22
    d.ellipse((size / 2 - r, 10, size / 2 + r, 10 + 2 * r), fill=col, outline=INK, width=6)
    d.rounded_rectangle((size * 0.15, 20 + 2 * r, size * 0.85, size * 1.4 - 6), 40, fill=col, outline=INK, width=6)
    return im


def stairs(t, t0):
    w, h = 820, 440
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    n = 6
    for k in range(n):
        if t < t0 + k * 0.18:
            break
        x0 = k * (w / n)
        y0 = h - (k + 1) * (h / n)
        d.rectangle((x0, y0, x0 + w / n, h), fill=(255, 255, 255) if k % 2 else (236, 228, 212), outline=INK, width=6)
    return shadowed(im)


def timer(t, t0):
    s = 260
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((10, 10, s - 10, s - 10), fill=WHITE, outline=INK, width=10)
    p = clamp((t - t0) / 2.5)
    d.pieslice((30, 30, s - 30, s - 30), -90, -90 + 360 * p, fill=RED)
    f = ANTON(60)
    d.text((s / 2 - f.getlength("2 MIN") / 2, s / 2 - 36), "2 MIN", font=f, fill=INK)
    return shadowed(im)


# ---------------------------------------------------------------- sections
S = dict(hook=0.0, b1=6.7, b2=14.8, b3=23.0, b4=29.7, cta=36.9)
CH = {k: kicker(v) for k, v in [("b1", "BAB 1 · OTAK ELAK SAKIT"), ("b2", "BAB 2 · GANJARAN SEGERA"),
                                  ("b3", "BAB 3 · DIRI MASA DEPAN"), ("b4", "BAB 4 · CARA MULA"),
                                  ("hook", "EXPLAINER"), ("cta", "KESIMPULAN")]}
HL = {
    "hook": headline(["Kenapa kita suka", "tangguh kerja?"], 92, 1),
    "b1": headline(["Kerja susah =", "ancaman"], 104, 1),
    "b2": headline(["Seronok sekarang", "menang"], 96, 1),
    "b3": headline(["\"Biar dia", "yang buat\""], 104, 1),
    "b4": headline(["Mula", "kecil"], 120, 1),
    "cta": headline(["Bukan malas,", "cuma manusia"], 96, 1),
}
CARDS = {
    "malas": label("BUKAN SEBAB MALAS", ANTON(64), WHITE, RED),
    "otak": label("OTAK = LARI DARI RASA TAK SELESA", INTER(36), INK, YEL),
    "chips": [label(x, ANTON(52), INK, WHITE) for x in ["SCROLL", "VIDEO", "MAKAN"]],
    "dia": label("DIA = AWAK JUGA", ANTON(64), INK, YEL),
    "teruskan": label("DAH MULA? SENANG TERUSKAN", INTER(38), WHITE, INK),
    "tag": label("TAG KAWAN YANG SUKA TANGGUH", ANTON(52), INK, YEL),
}
TRIG = [(10.2, "SUSAH"), (11.2, "BOSAN"), (12.1, "TAKUT")]


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
        for i, (tt, wd, col) in enumerate([(1.5, "HARI NI", WHITE), (2.4, "ESOK", YEL), (3.2, "NANTI", RED)]):
            pop(c, calendar(wd, col), t, tt, 220 + i * 320, 640, rot=[-6, 3, -2][i])
        if t > 2.6:
            d = ImageDraw.Draw(c)
            p = ease_out((t - 2.6) / 0.3)
            d.line((90, 560, 90 + 260 * p, 720), fill=RED, width=14)
        pop(c, CARDS["malas"], t, 5.0, W / 2, 900, rot=-3)
        marker_circle(c, t, 5.4, W / 2, 900, 300, 80)
    elif k == "b1":
        pop(c, warning(t), t, 7.0, 300, 640)
        for i, (tt, wd) in enumerate(TRIG):
            pop(c, label(wd, ANTON(56), WHITE, INK), t, tt, 780, 520 + i * 120, rot=[3, -3, 2][i])
        pop(c, CARDS["otak"], t, 12.9, W / 2, 900, rot=-1)
    elif k == "b2":
        if t > 15.0:
            paste(c, balance(t, 16.3), W / 2, 680, scale=ease_back((t - 15.0) / 0.4))
        for i, tt in enumerate([17.9, 18.7, 19.6]):
            pop(c, CARDS["chips"][i], t, tt, 230 + i * 310, 940, rot=[-4, 3, -2][i])
        if t > 20.4:
            paste(c, label("+1", ANTON(90), WHITE, RED), 900, 520, scale=ease_back((t - 20.4) / 0.3), rot=10)
    elif k == "b3":
        pop(c, person((255, 255, 255)), t, 23.2, 300, 650)
        pop(c, label("AWAK HARI INI", TYPE(34), WHITE, INK), t, 23.4, 300, 830)
        if t > 24.2:
            pop(c, person((200, 200, 200)), t, 24.2, 780, 650)
            pop(c, label("AWAK MASA DEPAN", TYPE(34), WHITE, INK), t, 24.4, 780, 830)
        if t > 26.3:  # the task box gets pushed across
            p = ease_out((t - 26.3) / 0.6)
            bx = Image.new("RGBA", (150, 120), (205, 160, 100, 255))
            ImageDraw.Draw(bx).rectangle((0, 0, 149, 119), outline=INK, width=6)
            ImageDraw.Draw(bx).text((22, 34), "KERJA", font=ANTON(40), fill=INK)
            paste(c, shadowed(bx), 420 + 220 * p, 700, rot=-4)
        pop(c, CARDS["dia"], t, 28.3, W / 2, 930, rot=-3)
    elif k == "b4":
        if t > 30.8:
            paste(c, stairs(t, 30.8), W / 2 - 60, 680, scale=ease_back((t - 30.8) / 0.4))
        if t > 32.8:
            paste(c, timer(t, 33.0), 860, 540, scale=ease_back((t - 32.8) / 0.35))
        pop(c, CARDS["teruskan"], t, 34.3, W / 2, 950, rot=2)
    elif k == "cta":
        if t > 37.1:
            d = ImageDraw.Draw(c)
            f = SERIF(100)
            s1 = "MALAS"
            x0 = W / 2 - f.getlength(s1) / 2
            d.text((x0, 540), s1, font=f, fill=INK)
            p = ease_out((t - 37.6) / 0.4)
            d.line((x0 - 10, 600, x0 - 10 + (f.getlength(s1) + 20) * p, 590), fill=RED, width=16)
            if t > 38.8:
                paste(c, label("MULA KECIL, HARI NI", ANTON(84), INK, YEL), W / 2, 740,
                      scale=ease_back((t - 38.8) / 0.35), rot=-2)
        pop(c, CARDS["tag"], t, 40.3, W / 2, 900, rot=2)


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
