"""Style C — "Vox Explainer" picture render.

Usage: python render_video_vox.py <project_dir> <work_dir> <out.mp4> [--still t1,t2,...]
<work_dir>/frames, <work_dir>/masks come from make_masks.py.
Subject becomes a white-outlined paper cut-out on cream graph paper; each beat gets
typewriter kickers, serif headlines with marker highlight, rubber stamps and
hand-drawn diagrams (comparison card, people diagram, product callouts, checklist).
"""
import math
import os
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import cues_vox as C  # noqa: E402

P, WD, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
W, H, FPS = 1080, 1920, 30
NF = int(round(C.DURATION * FPS))
FRAMES = sorted(os.listdir(f"{WD}/frames"))
N = len(FRAMES)

CREAM = (242, 235, 221)
INK = (24, 22, 20)
YELLOW = (255, 212, 0)
RED = (226, 64, 43)
PINK = (222, 84, 136)
BLUSH = (246, 205, 220)
GREEN = (46, 150, 92)
GREY = (205, 200, 190)
WHITE = (255, 255, 255)


def font(name, size):
    path = f"{P}/assets/fonts/{name}"
    f = ImageFont.truetype(path, size)
    if name.startswith("PlayfairDisplay"):
        f.set_variation_by_name("Bold")
    return f


F_ANTON = lambda s: font("Anton-Regular.ttf", s)  # noqa: E731
F_SERIF = lambda s: font("PlayfairDisplay.ttf", s)  # noqa: E731
F_TYPE = lambda s: font("SpecialElite-Regular.ttf", s)  # noqa: E731
F_MARK = lambda s: font("PermanentMarker-Regular.ttf", s)  # noqa: E731
F_CAP = font("Inter-SemiBold.otf", 50)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    return 1 - (1 - clamp(x)) ** 3


def ease_back(x):
    x = clamp(x)
    c1 = 1.70158
    return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2


# ---------------------------------------------------------------- background
def make_background():
    rng = np.random.default_rng(7)
    bg = np.ones((H, W, 3), np.float32) * np.array(CREAM, np.float32)
    low = cv2.resize(rng.normal(0, 1, (H // 40, W // 40)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    fine = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.8)
    bg += (low * 6 + fine * 4)[..., None]
    img = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img, "RGBA")
    for x in range(0, W, 54):
        d.line([(x, 0), (x, H)], fill=(120, 140, 170, 28), width=1)
    for y in range(0, H, 54):
        d.line([(0, y), (W, y)], fill=(120, 140, 170, 28), width=1)
    yy, xx = np.mgrid[0:H, 0:W]
    v = ((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2
    return np.asarray(img).astype(np.float32) * (1 - 0.35 * np.clip(v, 0, 1))[..., None]


BG = make_background()
GRAIN = [cv2.resize(np.random.default_rng(i).normal(0, 7, (H // 2, W // 2)).astype(np.float32), (W, H),
                    interpolation=cv2.INTER_NEAREST) for i in range(6)]


# ---------------------------------------------------------------- sprite helpers
def with_shadow(img, offset=(10, 14), blur=10, alpha=0.35, pad=40):
    w, h = img.size
    out = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 255))
    sh.putalpha(img.split()[3].point(lambda v: int(v * alpha)))
    shl = Image.new("RGBA", out.size, (0, 0, 0, 0))
    shl.paste(sh, (pad + offset[0], pad + offset[1]))
    out = Image.alpha_composite(out, shl.filter(ImageFilter.GaussianBlur(blur)))
    out.alpha_composite(img, (pad, pad))
    return out


def label(text, f, fg, bg, padx=26, pady=16, highlight=None):
    b = f.getbbox(text)
    asc, desc = f.getmetrics()
    hgt = asc + desc
    img = Image.new("RGBA", (b[2] - b[0] + padx * 2, hgt + pady * 2), bg + (255,) if bg else (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if highlight:
        word, col = highlight
        i = text.find(word)
        if i >= 0:
            x0 = padx + f.getlength(text[:i])
            d.rectangle([x0 - 8, pady + hgt * 0.22, x0 + f.getlength(word) + 8, pady + hgt * 0.95], fill=col)
    d.text((padx - b[0], pady), text, font=f, fill=fg)
    return img


def place(canvas, sprite, cx, cy, scale=1.0, rot=0.0, alpha=1.0):
    if alpha <= 0.01 or scale <= 0.01:
        return
    s = sprite
    if abs(scale - 1) > 1e-3:
        s = s.resize((max(1, int(s.width * scale)), max(1, int(s.height * scale))), Image.BILINEAR)
    if abs(rot) > 0.05:
        s = s.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        s = s.copy()
        s.putalpha(s.split()[3].point(lambda v: int(v * alpha)))
    x, y = int(cx - s.width / 2), int(cy - s.height / 2)
    canvas.alpha_composite(s, (max(0, x), max(0, y)), (max(0, -x), max(0, -y)))


def pop(canvas, sprite, t, t0, cx, cy, rot=0.0, t1=None, dur=0.35):
    if t < t0 or (t1 is not None and t > t1 + 0.25):
        return
    k = ease_back((t - t0) / dur)
    a = clamp((t - t0) / 0.12)
    if t1 is not None and t > t1:
        o = ease_out((t - t1) / 0.25)
        a *= 1 - o
        k *= 1 - 0.15 * o
    place(canvas, sprite, cx, cy, scale=max(0.01, k), rot=rot, alpha=a)


def slide(canvas, sprite, t, t0, cx, cy, rot=0.0, t1=None, dx=-260, dur=0.4):
    if t < t0 or (t1 is not None and t > t1 + 0.25):
        return
    k = ease_out((t - t0) / dur)
    a = clamp((t - t0) / 0.15)
    if t1 is not None and t > t1:
        a *= 1 - ease_out((t - t1) / 0.25)
    place(canvas, sprite, cx + dx * (1 - k), cy, rot=rot, alpha=a)


def kicker(text):
    return with_shadow(label(text, F_TYPE(40), WHITE, INK, padx=22, pady=12), blur=6, alpha=0.3)


def headline(text, size=96, hl=None, col=YELLOW, bg=WHITE):
    return with_shadow(label(text, F_SERIF(size), INK, bg, padx=34, pady=18, highlight=(hl, col) if hl else None))


def stamp(text, size=120, col=RED):
    f = F_ANTON(size)
    b = f.getbbox(text)
    asc, desc = f.getmetrics()
    img = Image.new("RGBA", (b[2] - b[0] + 80, asc + desc + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([6, 6, img.width - 6, img.height - 6], radius=18, outline=col + (255,), width=10)
    d.text((40 - b[0], 30), text, font=f, fill=col + (255,))
    a = np.array(img.split()[3]).astype(np.float32)
    holes = cv2.GaussianBlur(np.random.default_rng(3).random(a.shape).astype(np.float32), (0, 0), 1.6)
    a *= np.where(holes > 0.53, 0.25, 1.0)
    img.putalpha(Image.fromarray(a.astype(np.uint8)))
    return img


def person_icon(col, size=110):
    img = Image.new("RGBA", (size, int(size * 1.35)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = size * 0.24
    d.ellipse([size / 2 - r, 4, size / 2 + r, 4 + 2 * r], fill=col + (255,), outline=INK + (255,), width=5)
    d.rounded_rectangle([size * 0.1, 2 * r + 14, size * 0.9, img.height - 4], radius=int(size * 0.3),
                        fill=col + (255,), outline=INK + (255,), width=5)
    return with_shadow(img, blur=5, alpha=0.3)


def card(w, h, bg=WHITE):
    img = Image.new("RGBA", (w, h), bg + (255,))
    ImageDraw.Draw(img).rectangle([0, 0, w - 1, h - 1], outline=INK + (255,), width=4)
    return img


# ---------------------------------------------------------------- hand-drawn marks (progressive)
def path_draw(d, pts, k, col, width):
    if k <= 0:
        return
    n = max(2, int(len(pts) * clamp(k)))
    d.line(pts[:n], fill=col + (255,), width=width, joint="curve")


def underline_marker(c, t, t0, x0, x1, y, col=RED, dur=0.35, width=12):
    if t < t0:
        return
    k = ease_out((t - t0) / dur)
    path_draw(ImageDraw.Draw(c), [(x0 + (x1 - x0) * i / 29, y + 6 * math.sin(i / 29 * 9)) for i in range(30)], k, col, width)


def circle_marker(c, t, t0, cx, cy, rx, ry, col=RED, dur=0.5, width=9):
    if t < t0:
        return
    k = ease_out((t - t0) / dur)
    pts = []
    for i in range(80):
        a = -1.9 + i / 79 * 2 * math.pi * 1.08
        r = 1 + 0.04 * math.sin(a * 3)
        pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
    path_draw(ImageDraw.Draw(c), pts, k, col, width)


def tick_marker(c, t, t0, x, y, s=40, col=GREEN, dur=0.3):
    if t < t0:
        return
    k = ease_out((t - t0) / dur)
    pts = [(x - s * 0.6 + s * 0.45 * u, y + s * 0.45 * u) for u in np.linspace(0, 1, 8)]
    pts += [(x - s * 0.15 + s * 0.95 * u, y + s * 0.45 - s * 1.1 * u) for u in np.linspace(0, 1, 14)]
    path_draw(ImageDraw.Draw(c), pts, k, col, 11)


def cross_marker(c, t, t0, x, y, s=36, col=RED, dur=0.3):
    if t < t0:
        return
    d = ImageDraw.Draw(c)
    k1, k2 = ease_out((t - t0) / (dur / 2)), ease_out((t - t0 - dur / 2) / (dur / 2))
    path_draw(d, [(x - s + 2 * s * u, y - s + 2 * s * u) for u in np.linspace(0, 1, 10)], k1, col, 11)
    path_draw(d, [(x + s - 2 * s * u, y - s + 2 * s * u) for u in np.linspace(0, 1, 10)], k2, col, 11)


def arrow_marker(c, t, t0, p0, p1, col=INK, dur=0.35, width=6, head=True):
    if t < t0:
        return
    k = ease_out((t - t0) / dur)
    pts = [(p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u - 18 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 24)]
    d = ImageDraw.Draw(c)
    path_draw(d, pts, k, col, width)
    if head and k >= 0.99:
        (x0, y0), (x1, y1) = pts[-2], pts[-1]
        a = math.atan2(y1 - y0, x1 - x0)
        for da in (2.6, -2.6):
            d.line([(x1, y1), (x1 + 22 * math.cos(a + da), y1 + 22 * math.sin(a + da))], fill=col + (255,), width=width)


def sun_doodle(c, t, t0, cx, cy, r=60):
    if t < t0:
        return
    d = ImageDraw.Draw(c)
    k = ease_out((t - t0) / 0.5)
    circ = [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in np.linspace(-1.6, -1.6 + 2 * math.pi * 1.04, 50)]
    path_draw(d, circ, k, (240, 170, 0), 10)
    for j in range(10):
        kk = ease_out((t - t0 - 0.3 - j * 0.04) / 0.2)
        if kk <= 0:
            continue
        a = j * math.pi / 5 + 0.2 * math.sin(t * 2)
        p0 = (cx + (r + 18) * math.cos(a), cy + (r + 18) * math.sin(a))
        p1 = (cx + (r + 18 + 34 * kk) * math.cos(a), cy + (r + 18 + 34 * kk) * math.sin(a))
        d.line([p0, p1], fill=(240, 170, 0, 255), width=9)


def stink_doodle(c, t, t0, x, y, length=120, col=(120, 160, 60), alpha=1.0):
    if t < t0:
        return
    k = ease_out((t - t0) / 0.4)
    pts = [(x + 14 * math.sin(t * 5 + i * 0.25), y - length * i / 30) for i in range(31)]
    d = ImageDraw.Draw(c)
    path_draw(d, pts, k, col if alpha >= 1 else col, 9)


# ---------------------------------------------------------------- static assets
A = {}
A["k_luar"] = kicker("AKTIVITI LUAR")
A["h_luar"] = headline("Suka aktiviti luar?", 92, hl="luar")
A["h_tegur"] = headline("Takut kawan tegur", 92, hl="tegur")
A["stamp_bau"] = stamp("BAU BADAN", 130)
A["h_vs"] = headline("Peluh vs bau badan", 84, hl="bau badan", col=(255, 170, 160))
A["k_kesan"] = kicker("KESANNYA")
A["h_selesa"] = headline("Rasa tak selesa", 96, hl="tak selesa")
A["icon_red"] = person_icon(RED)
A["icon_grey"] = person_icon(GREY)
A["k_brand"] = kicker("FIREA · CELESTE MUSK")
A["h_power"] = headline("Firea punya power", 88, hl="power", col=BLUSH)
A["k_untuk"] = kicker("SESUAI UNTUK")
A["h_pakai"] = headline("Pakai je Firea", 100, hl="Firea", col=BLUSH)
A["stamp_power"] = stamp("MEMANG POWER", 96, col=PINK)
A["k_cta"] = kicker(C.CTA_TEXT + "  →")
A["claims"] = [with_shadow(label(s, F_ANTON(46), INK, YELLOW, padx=18, pady=4), blur=5) for s in ("0% ALKOHOL", "0% PARABEN")]


def callout(title, sub):
    t = label(title, F_ANTON(58), INK, YELLOW, padx=18, pady=2)
    s = label(sub, F_TYPE(30), WHITE, INK, padx=14, pady=8)
    img = Image.new("RGBA", (max(t.width, s.width), t.height + s.height + 6), (0, 0, 0, 0))
    img.alpha_composite(t, (0, 0))
    img.alpha_composite(s, (0, t.height + 6))
    return with_shadow(img, blur=6, alpha=0.3)


A["call1"] = callout("KAWAL PELUH", "Antiperspirant")
A["call2"] = callout("HILANG BAU BADAN", "Odour & Wetness Protection")


def bottle_sticker():
    b = Image.open(f"{P}/assets/bottle.png").convert("RGBA")
    b = b.resize((int(b.width * 0.62), int(b.height * 0.62)), Image.LANCZOS)
    a = np.array(b.split()[-1])
    pad = 16
    big = np.zeros((a.shape[0] + 2 * pad, a.shape[1] + 2 * pad), np.uint8)
    big[pad:-pad, pad:-pad] = a
    outline = cv2.dilate(big, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
    st = Image.new("RGBA", (big.shape[1], big.shape[0]), (0, 0, 0, 0))
    st.paste(Image.new("RGBA", st.size, WHITE + (255,)), (0, 0), Image.fromarray(outline))
    st.alpha_composite(b, (pad, pad))
    return with_shadow(st, offset=(12, 16), blur=10, alpha=0.4)


A["bottle"] = bottle_sticker()


def compare_card(t):
    w, h = 900, 330
    img = card(w, h)
    d = ImageDraw.Draw(img)
    d.line([(w / 2, 20), (w / 2, h - 20)], fill=INK, width=4)
    d.line([(20, 110), (w - 20, 110)], fill=INK, width=4)
    fa = F_ANTON(70)
    for x, s in ((w / 4, "PELUH"), (3 * w / 4, "BAU BADAN")):
        d.text((x, 62), s, font=fa, fill=INK, anchor="mm")
    fm = F_MARK(64)
    if t >= C.TICK_OK:
        k = clamp((t - C.TICK_OK) / 0.25)
        d.text((w / 4 - 40, 215), "Takpe", font=fm, fill=GREEN + (int(255 * k),), anchor="mm")
        tick_marker(img, t, C.TICK_OK + 0.1, int(w / 4 + 130), 205)
    if t >= C.TICK_NO:
        k = clamp((t - C.TICK_NO) / 0.25)
        d.text((3 * w / 4 - 40, 215), "Jangan!", font=fm, fill=RED + (int(255 * k),), anchor="mm")
        cross_marker(img, t, C.TICK_NO + 0.1, int(3 * w / 4 + 150), 215)
    return with_shadow(img)


def checklist_card(t):
    w, h = 820, 290
    img = card(w, h)
    d = ImageDraw.Draw(img)
    f = F_SERIF(60)
    for i, (txt, t0) in enumerate((("Kuat berpeluh", C.BOX1), ("Takut badan berbau", C.BOX2))):
        y = 85 + i * 125
        d.rectangle([40, y - 34, 108, y + 34], outline=INK, width=6)
        d.text((140, y), txt, font=f, fill=INK, anchor="lm")
        tick_marker(img, t, t0, 82, y - 6, s=46, col=RED)
    return with_shadow(img)


# ---------------------------------------------------------------- person layer
_mask_cache = {}


def load_mask(i):
    i = max(0, min(N - 1, i))
    if i not in _mask_cache:
        m = cv2.imread(f"{WD}/masks/{FRAMES[i][:-4]}.png", cv2.IMREAD_GRAYSCALE)
        _mask_cache[i] = m.astype(np.float32) / 255
        if len(_mask_cache) > 6:
            _mask_cache.pop(min(_mask_cache))
    return _mask_cache[i]


def neighbours_ok(i, j):
    """don't blend masks across the hard cut in the footage."""
    cut = int(round(C.SCENE_CUT * FPS))
    return (i < cut) == (j < cut)


SIDES = {False: ((0, 290), (790, 1080)),   # before the product cut: seat right, pillar left
         True: ((790, 1080),)}            # after it the left side holds her hand + bottle


def shoulder_line(white, x0, x1):
    """first row (from y=600) where the white knit sweater fills the side strip."""
    frac = white[:, x0:x1].mean(axis=1)
    run = np.convolve((frac > 0.35).astype(np.float32), np.ones(25) / 25, mode="same")
    ys = np.where(run[600:] > 0.9)[0]
    return 600 + ys[0] - 12 if len(ys) else 1250


def remove_car_seat(src, m, t):
    """The segmenter keeps the car seat / window pillar beside her. Beside the head and
    above her shoulders nothing belongs to her except the hijab, so in the side strips
    above the detected shoulder line everything outside the (protected) hijab/face blob
    is removed. Then keep the largest blob."""
    f = src.astype(np.float32)
    r, b = f[..., 0], f[..., 2]
    lum = f.mean(axis=2)
    g = f[..., 1]
    warm = ((lum > 110) & (r > b + 12) & (r - g < 100) & (m > 0.5)).astype(np.uint8)   # beige/skin, not orange trim
    warm = cv2.morphologyEx(warm, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (19, 19)))  # cut thin trim links
    k, lab, stats, _ = cv2.connectedComponentsWithStats(warm)
    protect = np.zeros_like(warm)
    if k > 1:
        blob = (lab == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
        hull = cv2.convexHull(cv2.findNonZero(blob))   # face + hijab outline, eyes always inside
        cv2.fillConvexPoly(protect, hull, 1)
        protect = cv2.dilate(protect, np.ones((9, 9), np.uint8))
    white = (lum > 170) & (np.abs(r - b) < 28) & (m > 0.5)
    m = m.copy()
    for x0, x1 in SIDES[t >= C.SCENE_CUT]:
        ys = shoulder_line(white, x0, x1)
        zone = m[:ys, x0:x1]
        zone[protect[:ys, x0:x1] == 0] = 0
    bb = (m > 0.5).astype(np.uint8)
    k, lab, stats, _ = cv2.connectedComponentsWithStats(bb)
    if k > 2:
        keep = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        m = np.where((lab != keep) & (lab != 0), 0, m)
    return m


def composite_person(base, i, t):
    src = cv2.cvtColor(cv2.imread(f"{WD}/frames/{FRAMES[i]}"), cv2.COLOR_BGR2RGB)
    ms = [load_mask(j) if neighbours_ok(i, j) and 0 <= j < N else load_mask(i) for j in (i - 1, i, i + 1)]
    m = 0.25 * ms[0] + 0.5 * ms[1] + 0.25 * ms[2]
    m = np.clip((m - 0.25) / 0.5, 0, 1)
    m = remove_car_seat(src, m, t)
    shot = max([s for s in C.SHOTS if s[0] <= t], key=lambda s: s[0])
    nxt = [s[0] for s in C.SHOTS if s[0] > t]
    dur = (nxt[0] if nxt else C.DURATION) - shot[0]
    k = (t - shot[0]) / max(dur, 0.1)
    sc = shot[1] * (1 + 0.03 * k) * W / src.shape[1]
    pw, ph = int(src.shape[1] * sc), int(src.shape[0] * sc)
    src = cv2.resize(src, (pw, ph), interpolation=cv2.INTER_AREA)
    m = cv2.resize(m, (pw, ph), interpolation=cv2.INTER_LINEAR)
    s = np.clip((src.astype(np.float32) - 128) * 1.08 + 128 + np.array([6, 2, -4], np.float32), 0, 255)
    pad = 40
    mp = cv2.copyMakeBorder(m, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    mp[-pad:, :] = np.maximum(mp[-pad:, :], mp[-pad - 1:-pad, :])
    outline = cv2.GaussianBlur(cv2.dilate(mp, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (29, 29))), (0, 0), 1.2)
    shadow = cv2.GaussianBlur(outline, (0, 0), 14) * 0.38
    x0 = (W - pw) // 2 - pad
    y0 = H - ph + shot[2] - pad
    hh, ww = mp.shape

    def region(dx, dy):
        X0, Y0 = x0 + dx, y0 + dy
        cx0, cy0, cx1, cy1 = max(0, X0), max(0, Y0), min(W, X0 + ww), min(H, Y0 + hh)
        return (slice(cy0, cy1), slice(cx0, cx1)), (slice(cy0 - Y0, cy1 - Y0), slice(cx0 - X0, cx1 - X0))

    dst, sr = region(14, 20)
    base[dst] *= (1 - shadow[sr])[..., None]
    dst, sr = region(0, 0)
    o = outline[sr][..., None]
    base[dst] = base[dst] * (1 - o) + 255 * o
    sp = cv2.copyMakeBorder(s, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    a = mp[sr][..., None]
    base[dst] = base[dst] * (1 - a) + sp[sr] * a


# ---------------------------------------------------------------- captions
def wrap(text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if f.getlength(t) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    lines.append(cur)
    return lines


def caption_sprite(text, hl):
    f = F_CAP
    lines = wrap(text, f, 860)
    asc, desc = f.getmetrics()
    lh = asc + desc + 10
    w = int(max(f.getlength(l) for l in lines)) + 60
    h = lh * len(lines) + 34
    img = Image.new("RGBA", (w, h), WHITE + (255,))
    d = ImageDraw.Draw(img)
    for i, l in enumerate(lines):
        x = (w - f.getlength(l)) / 2
        y = 17 + i * lh
        if hl and hl.lower() in l.lower():
            j = l.lower().find(hl.lower())
            hx0 = x + f.getlength(l[:j])
            d.rectangle([hx0 - 6, y + asc * 0.2, hx0 + f.getlength(l[j:j + len(hl)]) + 6, y + lh - 8], fill=YELLOW)
        d.text((x, y), l, font=f, fill=INK)
    return with_shadow(img, blur=6, alpha=0.3)


CAPS = [(s, e, txt) for s, e, txt in C.CAPTIONS]
CAP_SPR = [caption_sprite(txt, C.CAP_HL.get(txt)) for _, _, txt in CAPS]


def draw_caption(canvas, t):
    for j, ((s, e, _), spr) in enumerate(zip(CAPS, CAP_SPR)):
        nxt = CAPS[j + 1][0] - 0.05 if j + 1 < len(CAPS) else 1e9
        if s - 0.05 <= t < min(e + 0.15, nxt):
            k = ease_out((t - s + 0.05) / 0.18)
            place(canvas, spr, W / 2, 1640 + 30 * (1 - k), alpha=k)


# ---------------------------------------------------------------- overlays per beat
def overlays(c, t):
    # 1. hook — outdoor activity
    slide(c, A["k_luar"], t, C.S1[0], 280, 150, rot=-2, t1=C.S1[1])
    pop(c, A["h_luar"], t, C.S1[0] + 0.25, W / 2, 290, rot=-1.5, t1=C.S1[1])
    if t < C.S1[1] + 0.2:
        sun_doodle(c, t, C.S1[0] + 0.5, 880, 500)

    # 2. afraid a friend will comment
    pop(c, A["h_tegur"], t, C.S2[0], W / 2, 180, rot=1.2, t1=C.S2[1])
    if C.S2[0] <= t <= C.S2[1] + 0.25:
        a = 1 - clamp((t - C.S2[1]) / 0.25)
        place(c, A["icon_grey"], 200, 470, alpha=a * clamp((t - 3.0) / 0.15))
        place(c, A["icon_red"], 880, 470, alpha=a * clamp((t - 3.1) / 0.15))
        if t >= 3.77:   # "kawan tegur": speech bubble from the friend
            k = ease_back((t - 3.77) / 0.3)
            bub = Image.new("RGBA", (300, 170), (0, 0, 0, 0))
            d = ImageDraw.Draw(bub)
            d.rounded_rectangle([4, 4, 290, 130], radius=40, fill=WHITE, outline=INK, width=5)
            d.polygon([(50, 126), (40, 166), (95, 126)], fill=WHITE, outline=INK)
            d.line([(52, 128), (92, 128)], fill=WHITE, width=6)
            d.text((147, 67), "?!", font=F_ANTON(80), fill=INK, anchor="mm")
            place(c, with_shadow(bub, blur=6, alpha=0.3), 330, 330, scale=k, alpha=a)
        for j, x in enumerate((830, 880, 930)):
            if a > 0 and t < C.S2[1]:
                stink_doodle(c, t, 4.4 + j * 0.08, x, 400)
    if C.STAMP_BAU <= t <= C.S2[1] + 0.25:
        k = clamp((t - C.STAMP_BAU) / 0.18)
        place(c, A["stamp_bau"], W / 2, 430, scale=1.8 - 0.8 * ease_out(k), rot=-8,
              alpha=k * (1 - clamp((t - C.S2[1]) / 0.25)))

    # 3. sweat is fine, odour is not
    pop(c, A["h_vs"], t, C.S3[0], W / 2, 170, rot=-1, t1=C.S3[1])
    if C.S3[0] + 0.2 <= t <= C.S3[1] + 0.25:
        a = clamp((t - C.S3[0] - 0.2) / 0.2) * (1 - clamp((t - C.S3[1]) / 0.25))
        place(c, compare_card(t), W / 2, 450, rot=1, alpha=a)

    # 4. consequence: uncomfortable, people keep their distance
    slide(c, A["k_kesan"], t, C.S4[0], 220, 140, rot=-2, t1=C.S4[1])
    pop(c, A["h_selesa"], t, C.SELESA, W / 2, 270, rot=1, t1=C.S4[1])
    if C.S4[0] + 0.3 <= t <= C.S4[1] + 0.25:
        a = clamp((t - C.S4[0] - 0.3) / 0.2) * (1 - clamp((t - C.S4[1]) / 0.25))
        if t >= C.NEIGHBOURS:
            mv = ease_out((t - C.MOVE_AWAY) / 0.9) if t >= C.MOVE_AWAY else 0.0
            for j, side in enumerate((-2, -1, 1, 2)):
                x = 540 + side * 170 + np.sign(side) * 150 * mv
                place(c, A["icon_grey"], x, 480, alpha=a * clamp((t - C.NEIGHBOURS - j * 0.06) / 0.15))
            if t >= C.MOVE_AWAY + 0.3:
                arrow_marker(c, t, C.MOVE_AWAY + 0.3, (420, 600), (200, 600))
                arrow_marker(c, t, C.MOVE_AWAY + 0.4, (660, 600), (880, 600))
        place(c, A["icon_red"], 540, 480, alpha=a)

    # paper wipe across the cut
    w0, w1 = C.WIPE
    if w0 <= t <= w1:
        u = (t - w0) / (w1 - w0)
        x = -W + 2 * W * ease_out(u) if u < 0.5 else W * (ease_out(u) * 2 - 1)
        sheet = Image.new("RGBA", (W + 80, H), (250, 244, 232, 255))
        ImageDraw.Draw(sheet).line([(W + 40, 0), (W + 60, H)], fill=(0, 0, 0, 60), width=30)
        c.alpha_composite(sheet, (max(0, int(x) - 40), 0), (max(0, 40 - int(x)), 0))

    # 5. product with annotated callouts
    slide(c, A["k_brand"], t, C.S5[0], 300, 140, rot=-2, t1=C.S5[1])
    pop(c, A["h_power"], t, C.S5[0] + 0.15, W / 2, 265, rot=-1, t1=C.S5[1])
    if C.S5[0] + 0.2 <= t <= C.S5[1] + 0.25:
        a = 1 - clamp((t - C.S5[1]) / 0.25)
        place(c, A["bottle"], 880, 660, scale=0.85 * ease_back((t - C.S5[0] - 0.2) / 0.4), rot=-6, alpha=a)
        if t >= C.CALL1:
            pop(c, A["call1"], t, C.CALL1, 290, 440, rot=-1.5, t1=C.S5[1])
            if t < C.S5[1]:
                arrow_marker(c, t, C.CALL1 + 0.2, (500, 440), (760, 560))
        if t >= C.CALL2:
            pop(c, A["call2"], t, C.CALL2, 300, 610, rot=1, t1=C.S5[1])
            if t < C.S5[1]:
                arrow_marker(c, t, C.CALL2 + 0.2, (580, 610), (770, 680))

    # 6. who it's for
    slide(c, A["k_untuk"], t, C.S6[0], 230, 140, rot=-2, t1=C.S6[1])
    if C.S6[0] + 0.2 <= t <= C.S6[1] + 0.25:
        a = clamp((t - C.S6[0] - 0.2) / 0.2) * (1 - clamp((t - C.S6[1]) / 0.25))
        place(c, checklist_card(t), W / 2, 400, rot=-1, alpha=a)

    # 7. end card
    pop(c, A["h_pakai"], t, C.END, W / 2, 180, rot=-1.5)
    if t >= C.END:
        place(c, A["bottle"], 830, 470, scale=0.82 * ease_back((t - C.END - 0.1) / 0.4), rot=6)
        for j, spr in enumerate(A["claims"]):
            pop(c, spr, t, C.CLAIMS + j * 0.15, 200 + j * 250, 330, rot=(-3, 2)[j])
        if t >= C.STAMP_POWER:
            k = clamp((t - C.STAMP_POWER) / 0.18)
            place(c, A["stamp_power"], 360, 500, scale=1.8 - 0.8 * ease_out(k), rot=-7, alpha=k)
        slide(c, A["k_cta"], t, C.CTA, 300, 665, rot=-1)


# ---------------------------------------------------------------- render
def render(stills=None):
    enc = None
    if stills is None:
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                                "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
    want = sorted(int(round(s * FPS)) for s in stills) if stills else range(NF)
    for n in want:
        t = n / FPS
        i = min(n, N - 1)    # hold last footage frame for the end card
        base = BG.copy()
        composite_person(base, i, t)
        base += GRAIN[(n // 2) % 6][..., None]
        canvas = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")
        overlays(canvas, t)
        draw_caption(canvas, t)
        out = np.array(canvas.convert("RGB"))
        if stills:
            Image.fromarray(out).save(f"{OUT}_{t:05.2f}.jpg", quality=88)
        else:
            enc.stdin.write(out.tobytes())
        if n % 90 == 0:
            print(f"frame {n}/{NF}", file=sys.stderr)
    if enc:
        enc.stdin.close()
        enc.wait()


if __name__ == "__main__":
    stills = None
    if "--still" in sys.argv:
        stills = [float(x) for x in sys.argv[sys.argv.index("--still") + 1].split(",")]
    render(stills)
