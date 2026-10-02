"""Vox-style re-edit: background removed, subject as paper cut-out on a textured
collage background, with animated headline cards, diagrams and captions.

Usage: python3 vox_render.py <workdir>
  <workdir>/frames/%05d.jpg  source frames @30fps
  <workdir>/masks/%05d.png   person masks (rembg u2net_human_seg)
  <workdir>/fonts/*.woff     Anton, Playfair, Inter, InterMed, Special, Permanent
Writes raw RGB frames to stdout (pipe into ffmpeg).
"""
import math
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

WD = sys.argv[1]
W, H, FPS = 1080, 1920, 30
FRAMES = sorted(os.listdir(f"{WD}/frames"))
N = len(FRAMES)

CREAM = (242, 235, 221)
INK = (24, 22, 20)
YELLOW = (255, 212, 0)
RED = (226, 64, 43)
BLUE = (60, 110, 190)
WHITE = (255, 255, 255)


def font(name, size):
    return ImageFont.truetype(f"{WD}/fonts/{name}.woff", size)


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_back(x):
    x = clamp(x)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


# ---------------------------------------------------------------- background
def make_background():
    rng = np.random.default_rng(7)
    bg = np.ones((H, W, 3), np.float32) * np.array(CREAM, np.float32)
    # paper fibres: low-frequency blotches + fine noise
    low = cv2.resize(rng.normal(0, 1, (H // 40, W // 40)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    fine = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.8)
    bg += (low * 6 + fine * 4)[..., None]
    img = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img, "RGBA")
    # faint graph-paper grid
    for x in range(0, W, 54):
        d.line([(x, 0), (x, H)], fill=(120, 140, 170, 28), width=1)
    for y in range(0, H, 54):
        d.line([(0, y), (W, y)], fill=(120, 140, 170, 28), width=1)
    # vignette
    yy, xx = np.mgrid[0:H, 0:W]
    v = ((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2
    arr = np.asarray(img).astype(np.float32) * (1 - 0.35 * np.clip(v, 0, 1))[..., None]
    return arr.astype(np.uint8)


BG = make_background()
GRAIN = [np.random.default_rng(i).normal(0, 7, (H // 2, W // 2)).astype(np.float32) for i in range(6)]
GRAIN = [cv2.resize(g, (W, H), interpolation=cv2.INTER_NEAREST) for g in GRAIN]


# ---------------------------------------------------------------- sprite helpers
def with_shadow(img, offset=(10, 14), blur=10, alpha=0.35, pad=40):
    """Return RGBA image (padded) with a soft drop shadow."""
    w, h = img.size
    out = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    a = img.split()[3]
    sh = Image.new("RGBA", img.size, (0, 0, 0, 255))
    sh.putalpha(a.point(lambda v: int(v * alpha)))
    shl = Image.new("RGBA", out.size, (0, 0, 0, 0))
    shl.paste(sh, (pad + offset[0], pad + offset[1]))
    shl = shl.filter(ImageFilter.GaussianBlur(blur))
    out = Image.alpha_composite(out, shl)
    out.alpha_composite(img, (pad, pad))
    return out


def text_size(f, s):
    b = f.getbbox(s)
    return b[2] - b[0], b[3] - b[1], b


def label(text, f, fg, bg, padx=26, pady=16, highlight=None):
    """Paper strip with text. highlight: (word, colour) drawn as marker behind word."""
    tw, th, b = text_size(f, text)
    asc, desc = f.getmetrics()
    hgt = asc + desc
    img = Image.new("RGBA", (tw + padx * 2, hgt + pady * 2), bg + (255,) if bg else (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if highlight:
        word, col = highlight
        i = text.find(word)
        if i >= 0:
            x0 = padx + f.getlength(text[:i])
            x1 = x0 + f.getlength(word)
            d.rectangle([x0 - 8, pady + hgt * 0.18, x1 + 8, pady + hgt * 0.95], fill=col)
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
        a = s.split()[3].point(lambda v: int(v * alpha))
        s = s.copy()
        s.putalpha(a)
    canvas.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2)))


def pop(canvas, sprite, t, t0, cx, cy, rot=0.0, t1=None, dur=0.35):
    """Pop-in with overshoot at t0, fade/shrink out at t1."""
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


# ---------------------------------------------------------------- assets
F_ANTON = lambda s: font("Anton", s)
F_SERIF = lambda s: font("Playfair", s)
F_TYPE = lambda s: font("Special", s)
F_CAP = font("Inter", 50)
F_MARK = lambda s: font("Permanent", s)


def kicker(text):
    return with_shadow(label(text, F_TYPE(40), WHITE, INK, padx=22, pady=12), blur=6, alpha=0.3)


def headline(text, size=104, hl=None, col=YELLOW, bg=WHITE):
    return with_shadow(label(text, F_SERIF(size), INK, bg, padx=34, pady=18, highlight=(hl, col) if hl else None))


def big(text, size=150, fg=INK, bg=YELLOW):
    return with_shadow(label(text, F_ANTON(size), fg, bg, padx=34, pady=8))


def stamp(text, size=120, col=RED):
    f = F_ANTON(size)
    tw, th, b = text_size(f, text)
    asc, desc = f.getmetrics()
    img = Image.new("RGBA", (tw + 80, asc + desc + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([6, 6, img.width - 6, img.height - 6], radius=18, outline=col + (255,), width=10)
    d.text((40 - b[0], 30), text, font=f, fill=col + (255,))
    # rubber-stamp texture: punch random holes into ink
    a = np.array(img.split()[3]).astype(np.float32)
    rng = np.random.default_rng(3)
    holes = cv2.GaussianBlur(rng.random(a.shape).astype(np.float32), (0, 0), 1.6)
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
    return img


def card(w, h, bg=WHITE):
    img = Image.new("RGBA", (w, h), bg + (255,))
    ImageDraw.Draw(img).rectangle([0, 0, w - 1, h - 1], outline=INK + (255,), width=4)
    return img


A = {}
A["k_isu"] = kicker("ISU KETAGIHAN")
A["h_opioid"] = big("KETAGIHAN OPIOID", 132, INK, WHITE)
A["chips"] = [with_shadow(label(s, F_ANTON(62), INK if i % 2 else WHITE, YELLOW if i % 2 else INK, padx=22, pady=6), blur=6)
              for i, s in enumerate(["AIS", "SYABU", "HEROIN", "SUBUTEX", "METHADONE"])]
A["h_bukan"] = headline("Bukan masalah seorang", 88, hl="seorang")
A["k_sekeliling"] = kicker("ORANG SEKELILING TURUT TERKESAN")
A["icon_red"] = with_shadow(person_icon(RED), blur=5, alpha=0.3)
A["icon_grey"] = with_shadow(person_icon((205, 200, 190)), blur=5, alpha=0.3)
A["icon_yel"] = with_shadow(person_icon(YELLOW), blur=5, alpha=0.3)
A["k_nafkah"] = kicker("PROVIDER · PENCARI NAFKAH")
A["h_duit"] = headline("Duit sentiasa bermasalah", 80, hl="bermasalah")
A["k_income"] = kicker("INCOME TINGGI?")
A["h_takisu"] = headline("Mungkin tak ada isu...", 84)
A["stamp_bazir"] = stamp("TETAP PEMBAZIRAN", 104)
A["k_contoh"] = kicker("CONTOH")
A["h_urine"] = headline("Sangkut urine", 112, hl="urine")
A["k_pusat"] = kicker("MASUK PUSAT")
A["h_2thn"] = big("± 2 TAHUN", 90, INK, YELLOW)
A["h_isubesar"] = headline("Isu yang besar", 104, hl="besar", col=(255, 160, 150))
A["k_income2"] = kicker("INCOME TERGANGGU")
A["k_reman"] = kicker("KENA REMAN")
A["h_berhenti"] = headline("Nak berhenti?", 110)
A["big_cuba"] = big("CUBALAH.", 190, WHITE, RED)
A["h_insya"] = headline("InsyaAllah membantu", 84, hl="membantu")


def money_text(v):
    return f"RM{v:,}"


# chart card (income line going down), drawn progressively
def chart(prog):
    w, h = 520, 330
    img = card(w, h)
    d = ImageDraw.Draw(img)
    d.text((22, 14), "DUIT / BULAN", font=F_TYPE(30), fill=INK)
    for gy in range(80, h - 20, 50):
        d.line([(20, gy), (w - 20, gy)], fill=(200, 205, 215), width=2)
    pts = [(40, 110), (120, 100), (200, 140), (270, 125), (340, 200), (410, 230), (480, 290)]
    n = prog * (len(pts) - 1)
    seg = [pts[0]]
    for i in range(1, len(pts)):
        if i <= n:
            seg.append(pts[i])
        else:
            f = n - (i - 1)
            if f > 0:
                p0, p1 = pts[i - 1], pts[i]
                seg.append((p0[0] + (p1[0] - p0[0]) * f, p0[1] + (p1[1] - p0[1]) * f))
            break
    if len(seg) > 1:
        d.line(seg, fill=RED, width=10, joint="curve")
        x, y = seg[-1]
        d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=RED)
    return with_shadow(img)


# timeline: 24 month ticks filling
def timeline(prog):
    w, h = 880, 150
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x0, x1, y = 30, w - 30, 70
    d.rounded_rectangle([x0, y - 18, x1, y + 18], radius=18, fill=WHITE, outline=INK, width=4)
    fx = x0 + (x1 - x0) * prog
    if prog > 0.01:
        d.rounded_rectangle([x0 + 5, y - 13, fx - 5 if fx - 5 > x0 + 30 else x0 + 30, y + 13], radius=13, fill=RED)
    for m in range(25):
        x = x0 + (x1 - x0) * m / 24
        tall = m % 12 == 0
        d.line([(x, y + 22), (x, y + (48 if tall else 34))], fill=INK, width=4 if tall else 2)
    f = F_TYPE(30)
    for m, s in [(0, "0"), (12, "1 THN"), (24, "2 THN")]:
        x = x0 + (x1 - x0) * m / 24
        tw = f.getlength(s)
        d.text((clamp(x - tw / 2, 0, w - tw), y + 52), s, font=f, fill=INK)
    return with_shadow(img, blur=6, alpha=0.25)


def broken_income():
    img = card(460, 160)
    d = ImageDraw.Draw(img)
    d.text((30, 30), "INCOME", font=F_ANTON(90), fill=INK)
    d.line([(20, 140), (440, 20)], fill=RED, width=14)
    return with_shadow(img)


A["broken"] = broken_income()


def underline_marker(canvas, t, t0, x0, x1, y, col=RED, dur=0.35, width=12):
    if t < t0:
        return
    k = ease_out((t - t0) / dur)
    d = ImageDraw.Draw(canvas)
    pts = []
    for i in range(30):
        u = i / 29 * k
        pts.append((x0 + (x1 - x0) * u, y + 6 * math.sin(u * 9)))
    d.line(pts, fill=col + (255,), width=width, joint="curve")


def circle_marker(canvas, t, t0, cx, cy, rx, ry, col=RED, dur=0.5):
    if t < t0:
        return
    k = ease_out((t - t0) / dur)
    d = ImageDraw.Draw(canvas)
    pts = []
    for i in range(80):
        a = -1.9 + i / 79 * 2 * math.pi * 1.08 * k
        r = 1 + 0.04 * math.sin(a * 3)
        pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
    d.line(pts, fill=col + (255,), width=9, joint="curve")


# ---------------------------------------------------------------- captions
CAPS = [
    (0.64, 3.0, "Bila terlibat dengan ketagihan", "ketagihan"),
    (3.0, 4.8, "yang melibatkan opioid —", "opioid"),
    (4.8, 6.76, "ais, syabu, heroin, Subutex, methadone", None),
    (7.16, 7.88, "dan sebagainya.", None),
    (8.48, 9.6, "Ini bukan seorang...", None),
    (9.96, 12.0, "Dia akan menyebabkan", None),
    (12.0, 14.41, "orang sekeliling kita turut bermasalah.", "orang sekeliling"),
    (15.03, 16.9, "Contoh macam kita,", None),
    (16.9, 18.79, "sebagai seorang provider", "provider"),
    (19.28, 21.0, "atau keluarga yang mencari nafkah —", "mencari nafkah"),
    (22.54, 24.07, "duit akan sentiasa", "duit"),
    (25.02, 26.92, "mengalami masalah.", "masalah"),
    (27.45, 29.6, "Bagi yang income tinggi,", "income tinggi"),
    (29.6, 31.76, "mungkin tak ada isu — tapi tetap satu pembaziran.", "pembaziran"),
    (32.29, 34.51, "Contoh, bila terkena...", None),
    (34.78, 35.9, "sangkut urine,", "sangkut urine"),
    (36.24, 38.9, "katakanlah masuk pusat —", "masuk pusat"),
    (38.9, 40.0, "mungkin...", None),
    (40.21, 41.2, "dua tahun.", "dua tahun"),
    (41.37, 42.91, "Dia akan jadi satu isu yang besar.", "isu yang besar"),
    (43.38, 45.67, "Income akan terganggu.", "terganggu"),
    (46.23, 47.53, "Mungkin dari segi", None),
    (48.16, 49.72, "sangkut urine, kena reman —", "kena reman"),
    (50.33, 52.17, "pun jadi isu juga. Nak kena banyak:", None),
    (52.5, 53.89, "4 ribu, 5 ribu.", "4 ribu, 5 ribu"),
    (54.15, 56.0, "Jadi untuk yang terlibat —", None),
    (56.0, 58.07, "kalau nak berhenti, cubalah.", "cubalah"),
    (58.64, 60.5, "Kalau susah, cuba amalkan ubat ini.", None),
    (60.5, 62.6, "InsyaAllah, membantu.", "membantu"),
]


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
            hx1 = hx0 + f.getlength(l[j:j + len(hl)])
            d.rectangle([hx0 - 6, y + asc * 0.2, hx1 + 6, y + lh - 8], fill=YELLOW)
        d.text((x, y), l, font=f, fill=INK)
    return with_shadow(img, blur=6, alpha=0.3)


CAP_SPR = [caption_sprite(c[2], c[3]) for c in CAPS]


def draw_caption(canvas, t):
    for j, ((s, e, _, _), spr) in enumerate(zip(CAPS, CAP_SPR)):
        nxt = CAPS[j + 1][0] - 0.05 if j + 1 < len(CAPS) else 1e9
        if s - 0.05 <= t < min(e + 0.15, nxt):
            k = ease_out((t - s + 0.05) / 0.18)
            place(canvas, spr, W / 2, 1640 + 30 * (1 - k), alpha=k)


# ---------------------------------------------------------------- person layer
# per-scene framing: (start time, scale, y-offset of frame bottom below canvas)
SHOTS = [(0.0, 0.80, 0), (8.3, 1.0, 230), (15.0, 0.80, 0), (22.4, 1.0, 260), (27.3, 0.84, 60),
         (32.2, 0.80, 0), (40.1, 1.0, 260), (46.1, 0.82, 30), (52.3, 1.0, 260), (54.1, 0.80, 0),
         (58.5, 1.0, 230)]
_mask_cache = {}


def load_mask(i):
    i = max(0, min(N - 1, i))
    if i not in _mask_cache:
        m = cv2.imread(f"{WD}/masks/{FRAMES[i][:-4]}.png", cv2.IMREAD_GRAYSCALE)
        _mask_cache[i] = m.astype(np.float32) / 255
        if len(_mask_cache) > 6:
            _mask_cache.pop(min(_mask_cache))
    return _mask_cache[i]


def person_layer(i, t):
    src = cv2.cvtColor(cv2.imread(f"{WD}/frames/{FRAMES[i]}"), cv2.COLOR_BGR2RGB)
    m = 0.25 * load_mask(i - 1) + 0.5 * load_mask(i) + 0.25 * load_mask(i + 1)
    m = np.clip((m - 0.25) / 0.5, 0, 1)
    # shot framing with slow push-in
    shot = max([s for s in SHOTS if s[0] <= t], key=lambda s: s[0])
    nxt = [s[0] for s in SHOTS if s[0] > t]
    dur = (nxt[0] if nxt else N / FPS) - shot[0]
    k = (t - shot[0]) / max(dur, 0.1)
    sc = shot[1] * (1 + 0.03 * k) * W / src.shape[1]
    pw, ph = int(src.shape[1] * sc), int(src.shape[0] * sc)
    src = cv2.resize(src, (pw, ph), interpolation=cv2.INTER_AREA)
    m = cv2.resize(m, (pw, ph), interpolation=cv2.INTER_LINEAR)
    # print-like grade: a touch more contrast and warmth
    s = src.astype(np.float32)
    s = (s - 128) * 1.08 + 128 + np.array([6, 2, -4], np.float32)
    s = np.clip(s, 0, 255)
    # sticker outline
    pad = 40
    mp = cv2.copyMakeBorder(m, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    # do not outline the bottom edge where the body leaves frame
    mp[-pad:, :] = np.maximum(mp[-pad:, :], mp[-pad - 1:-pad, :])
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (29, 29))
    outline = cv2.GaussianBlur(cv2.dilate(mp, ker), (0, 0), 1.2)
    shadow = cv2.GaussianBlur(outline, (0, 0), 14) * 0.38
    x0 = (W - pw) // 2 - pad
    y0 = H - ph + shot[2] - pad
    return s, mp, outline, shadow, x0, y0, pad


def composite_person(base, i, t):
    s, mp, outline, shadow, x0, y0, pad = person_layer(i, t)
    hh, ww = mp.shape

    def region(dx, dy):
        X0, Y0 = x0 + dx, y0 + dy
        cx0, cy0 = max(0, X0), max(0, Y0)
        cx1, cy1 = min(W, X0 + ww), min(H, Y0 + hh)
        return (slice(cy0, cy1), slice(cx0, cx1)), (slice(cy0 - Y0, cy1 - Y0), slice(cx0 - X0, cx1 - X0))

    (dst, srcr) = region(14, 20)
    base[dst] *= (1 - shadow[srcr])[..., None]
    (dst, srcr) = region(0, 0)
    o = outline[srcr][..., None]
    base[dst] = base[dst] * (1 - o) + 255 * o
    sp = cv2.copyMakeBorder(s, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    a = mp[srcr][..., None]
    base[dst] = base[dst] * (1 - a) + sp[srcr] * a


# ---------------------------------------------------------------- overlays per scene
def overlays(c, t):
    # 1. hook
    pop(c, A["k_isu"], t, 0.25, 300, 150, rot=-3, t1=8.2)
    pop(c, A["h_opioid"], t, 0.6, W / 2, 285, rot=-1.5, t1=8.2)
    underline_marker(c, t, 3.3, 560, 960, 360) if t < 8.45 else None
    chip_t = [2.6, 3.3, 4.2, 5.0, 5.8]
    chip_xy = [(180, 455), (410, 450), (700, 460), (290, 570), (690, 575)]
    for j, (ct, (x, y)) in enumerate(zip(chip_t, chip_xy)):
        pop(c, A["chips"][j], t, ct, x, y, rot=[-4, 3, -2, 2, -3][j], t1=8.2)

    # 2. not just one person
    pop(c, A["h_bukan"], t, 8.45, W / 2, 175, rot=1.2, t1=14.5)
    pop(c, A["k_sekeliling"], t, 10.0, W / 2, 300, rot=-1.5, t1=14.5)
    if 8.5 <= t <= 14.75:
        xs = [190, 365, 540, 715, 890]
        for j, x in enumerate(xs):
            if j == 2:
                pop(c, A["icon_red"], t, 8.7, x, 450, t1=14.5)
            else:
                spread = 11.6 + abs(j - 2) * 0.35
                spr = A["icon_yel"] if t >= spread else A["icon_grey"]
                pop(c, spr, t, 9.0 + j * 0.08, x, 450, t1=14.5)
        # ripple rings from the red figure
        if 11.4 <= t <= 14.4:
            d = ImageDraw.Draw(c)
            for r0 in (0, 0.6):
                r = ((t - 11.4 + r0) % 1.2) / 1.2
                rad = 60 + r * 320
                d.ellipse([540 - rad, 450 - rad * 0.3, 540 + rad, 450 + rad * 0.3],
                          outline=RED + (int(200 * (1 - r)),), width=5)

    # 3. provider / money
    slide(c, A["k_nafkah"], t, 15.1, 330, 150, rot=-2, t1=26.9)
    pop(c, A["h_duit"], t, 22.4, W / 2, 280, rot=1, t1=26.9)
    if 23.0 <= t <= 27.15:
        prog = ease_out((t - 23.0) / 3.0)
        a = 1 - clamp((t - 26.9) / 0.25)
        place(c, chart(prog), 760, 480, rot=-3, alpha=a * clamp((t - 23.0) / 0.15))
    if 16.9 <= t <= 22.3:
        pop(c, headline("Provider", 110, hl="Provider"), t, 16.9, W / 2, 300, rot=-2, t1=19.1)
        pop(c, headline("Mencari nafkah", 100, hl="nafkah"), t, 19.3, W / 2, 300, rot=1.5, t1=22.1)

    # 4. high income
    slide(c, A["k_income"], t, 27.4, 270, 150, rot=-2, t1=32.0)
    pop(c, A["h_takisu"], t, 28.0, W / 2, 270, rot=-1, t1=32.0)
    if t >= 29.9 and t <= 32.25:
        k = clamp((t - 29.9) / 0.18)
        sc = 1.8 - 0.8 * ease_out(k)
        a = (1 - clamp((t - 32.0) / 0.25)) * k
        place(c, A["stamp_bazir"], W / 2, 440, scale=sc, rot=-8, alpha=a)

    # 5. urine test → rehab centre ~2 yrs
    slide(c, A["k_contoh"], t, 32.3, 200, 150, rot=-3, t1=41.2)
    pop(c, A["h_urine"], t, 34.75, W / 2, 275, rot=-1.5, t1=41.2)
    pop(c, A["k_pusat"], t, 36.9, 300, 410, rot=2, t1=41.2)
    if 37.4 <= t <= 41.45:
        prog = ease_out((t - 40.0) / 1.0) if t >= 40.0 else 0.5 * ease_out((t - 37.6) / 2.0)
        a = clamp((t - 37.4) / 0.2) * (1 - clamp((t - 41.2) / 0.25))
        place(c, timeline(prog), W / 2, 545, alpha=a)
    pop(c, A["h_2thn"], t, 40.2, 790, 400, rot=4, t1=41.2)

    # 6. big issue
    pop(c, A["h_isubesar"], t, 41.4, W / 2, 170, rot=1.5, t1=46.0)
    pop(c, A["k_income2"], t, 43.4, 300, 300, rot=-2, t1=46.0)
    if 43.6 <= t <= 46.25:
        pop(c, A["broken"], t, 43.6, 780, 330, rot=4, t1=46.0)

    # 7. remand + cost
    pop(c, A["h_urine"], t, 46.3, W / 2, 190, rot=1, t1=53.95)
    pop(c, A["k_reman"], t, 48.2, 300, 320, rot=-3, t1=53.95)
    if 48.2 <= t <= 54.2:
        circle_marker(c, t, 48.4, 300, 320, 210, 60) if t < 53.95 else None
    if 50.4 <= t <= 54.2:
        if t < 52.5:
            v = int(4000 * ease_out((t - 50.4) / 1.6) / 100) * 100
            txt = money_text(v)
        else:
            txt = "RM4,000 – 5,000"
        a = 1 - clamp((t - 53.95) / 0.25)
        place(c, big(txt, 120), W / 2, 480, rot=-2, alpha=a * clamp((t - 50.4) / 0.15))

    # 8. call to action
    pop(c, A["h_berhenti"], t, 54.2, W / 2, 190, rot=-1.5, t1=58.4)
    pop(c, A["big_cuba"], t, 56.6, W / 2, 390, rot=-4, t1=58.4)
    pop(c, A["h_insya"], t, 60.4, W / 2, 230, rot=1.5)
    underline_marker(c, t, 60.8, 580, 960, 300)


# ---------------------------------------------------------------- main loop
def main():
    out = sys.stdout.buffer
    for i in range(N):
        t = i / FPS
        base = BG.astype(np.float32)
        composite_person(base, i, t)
        base += GRAIN[i % len(GRAIN)][..., None] * 0.6
        canvas = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")
        overlays(canvas, t)
        draw_caption(canvas, t)
        # global gentle fade in/out
        rgb = np.asarray(canvas.convert("RGB"))
        if t < 0.3 or t > N / FPS - 0.5:
            f = clamp(t / 0.3) * clamp((N / FPS - t) / 0.5)
            rgb = (rgb.astype(np.float32) * f).astype(np.uint8)
        out.write(rgb.tobytes())
        if i % 100 == 0:
            print(f"frame {i}/{N}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 2:  # preview single times: vox_render.py WD t1 t2 ...
        for ts in sys.argv[2:]:
            t = float(ts)
            i = min(N - 1, int(t * FPS))
            base = BG.astype(np.float32)
            composite_person(base, i, t)
            canvas = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")
            overlays(canvas, t)
            draw_caption(canvas, t)
            canvas.convert("RGB").save(f"{WD}/preview_{ts}.jpg", quality=85)
    else:
        main()
