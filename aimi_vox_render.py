"""Aimi Curtain promo — Vox-style re-edit.

Narration clip (VID-20260925-WA0007) with the background removed: the presenter is a
paper "sticker" cut-out on a textured collage background, with animated headline cards,
diagrams, B-roll polaroids (VID-20260928-WA0005/0007, VID-20260929-WA0028), customer
testimonial screenshots and the customer photo, plus captions.

Usage: python3 aimi_vox_render.py <workdir> [t1 t2 ...]
  <workdir>/frames/%05d.jpg   narration frames @30fps
  <workdir>/masks/%05d.png    person masks (rembg u2net_human_seg)
  <workdir>/b2 b3 b4/%05d.jpg B-roll frames @30fps, 450x800
  <workdir>/img/1..5.jpg      testimonial screenshots (1-4) + customer photo (5)
  <workdir>/fonts/*.ttf       Anton, Playfair, Inter, Special, Permanent, Great
Without times: writes raw RGB frames to stdout (pipe into ffmpeg) and the
sound-effect cue list to <workdir>/sfx.json. With times: writes preview JPGs.
"""
import json
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
TAIL = 1.6  # end-card hold after the narration
TOTAL = N / FPS + TAIL

CREAM = (242, 235, 221)
INK = (24, 22, 20)
YELLOW = (255, 212, 0)
RED = (226, 64, 43)
GOLD = (196, 154, 62)
GREEN = (37, 178, 84)
WHITE = (255, 255, 255)
GREY = (150, 146, 140)

SFX = set()


def font(name, size, var=None):
    f = ImageFont.truetype(f"{WD}/fonts/{name}.ttf", size)
    if var:
        f.set_variation_by_name(var)
    return f


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_io(x):
    x = clamp(x)
    return 3 * x * x - 2 * x * x * x


def ease_back(x):
    x = clamp(x)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def cue(t, t0, kind="pop"):
    if t0 <= t < t0 + 1 / FPS:
        SFX.add((round(t0, 3), kind))


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
    # torn yellow paper strip behind the presenter
    pts = [(0, 1180)]
    for x in range(0, W + 40, 40):
        pts.append((x, 1150 + 14 * math.sin(x * 0.05) + rng.normal(0, 4)))
    pts += [(W, 1330), (0, 1330)]
    d.polygon(pts, fill=(255, 212, 0, 60))
    yy, xx = np.mgrid[0:H, 0:W]
    v = ((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2
    arr = np.asarray(img).astype(np.float32) * (1 - 0.35 * np.clip(v, 0, 1))[..., None]
    return arr.astype(np.uint8)


BG = make_background()
GRAIN = [np.random.default_rng(i).normal(0, 7, (H // 2, W // 2)).astype(np.float32) for i in range(6)]
GRAIN = [cv2.resize(g, (W, H), interpolation=cv2.INTER_NEAREST) for g in GRAIN]


# ---------------------------------------------------------------- sprite helpers
def with_shadow(img, offset=(10, 14), blur=10, alpha=0.35, pad=40):
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
            d.rectangle([x0 - 8, pady + hgt * 0.22, x1 + 8, pady + hgt * 0.92], fill=col)
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


def pop(canvas, sprite, t, t0, cx, cy, rot=0.0, t1=None, dur=0.35, sfx="pop"):
    if t < t0 or (t1 is not None and t > t1 + 0.25):
        return
    cue(t, t0, sfx)
    k = ease_back((t - t0) / dur)
    a = clamp((t - t0) / 0.12)
    if t1 is not None and t > t1:
        o = ease_out((t - t1) / 0.25)
        a *= 1 - o
        k *= 1 - 0.15 * o
    place(canvas, sprite, cx, cy, scale=max(0.01, k), rot=rot, alpha=a)


def slide(canvas, sprite, t, t0, cx, cy, rot=0.0, t1=None, dx=-260, dy=0, dur=0.4):
    if t < t0 or (t1 is not None and t > t1 + 0.25):
        return
    cue(t, t0, "swoosh")
    k = ease_out((t - t0) / dur)
    a = clamp((t - t0) / 0.15)
    if t1 is not None and t > t1:
        a *= 1 - ease_out((t - t1) / 0.25)
    place(canvas, sprite, cx + dx * (1 - k), cy + dy * (1 - k), rot=rot, alpha=a)


def slam(canvas, sprite, t, t0, cx, cy, rot=0.0, t1=None):
    """Rubber-stamp slam: big -> settle."""
    if t < t0 or (t1 is not None and t > t1 + 0.25):
        return
    cue(t, t0, "thud")
    k = clamp((t - t0) / 0.16)
    sc = 1.8 - 0.8 * ease_out(k)
    a = k * (1 - clamp((t - t1) / 0.25) if t1 is not None else 1)
    place(canvas, sprite, cx, cy, scale=sc, rot=rot, alpha=a)


# ---------------------------------------------------------------- fonts / assets
F_ANTON = lambda s: font("Anton", s)
F_SERIF = lambda s: font("Playfair", s, "Bold")
F_SERIF_I = lambda s: font("PlayfairItalic", s, "Bold Italic")
F_TYPE = lambda s: font("Special", s)
F_MARK = lambda s: font("Permanent", s)
F_SCRIPT = lambda s: font("Great", s)
F_CAP = font("Inter", 50, "SemiBold")


def kicker(text, size=40):
    return with_shadow(label(text, F_TYPE(size), WHITE, INK, padx=22, pady=12), blur=6, alpha=0.3)


def headline(text, size=100, hl=None, col=YELLOW, bg=WHITE, fg=INK):
    return with_shadow(label(text, F_SERIF(size), fg, bg, padx=34, pady=18, highlight=(hl, col) if hl else None))


def big(text, size=150, fg=INK, bg=YELLOW):
    return with_shadow(label(text, F_ANTON(size), fg, bg, padx=34, pady=8))


def roughen(img, seed=3, thr=0.53):
    a = np.array(img.split()[3]).astype(np.float32)
    rng = np.random.default_rng(seed)
    holes = cv2.GaussianBlur(rng.random(a.shape).astype(np.float32), (0, 0), 1.6)
    a *= np.where(holes > thr, 0.25, 1.0)
    img.putalpha(Image.fromarray(a.astype(np.uint8)))
    return img


def stamp(lines, sizes, col=RED):
    fs = [F_ANTON(s) for s in sizes]
    ws = [text_size(f, l)[0] for f, l in zip(fs, lines)]
    hs = [sum(f.getmetrics()) for f in fs]
    img = Image.new("RGBA", (max(ws) + 90, sum(hs) + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([6, 6, img.width - 6, img.height - 6], radius=18, outline=col + (255,), width=10)
    y = 30
    for f, l, w_, h_ in zip(fs, lines, ws, hs):
        b = f.getbbox(l)
        d.text(((img.width - w_) / 2 - b[0], y), l, font=f, fill=col + (255,))
        y += h_
    return roughen(img)


def tape(w=150, h=46, rot=0):
    img = Image.new("RGBA", (w, h), (250, 240, 190, 185))
    d = ImageDraw.Draw(img)
    for x in range(0, w, 7):  # serrated ends
        d.polygon([(x, 0), (x + 3.5, 5), (x + 7, 0)], fill=(0, 0, 0, 0))
        d.polygon([(x, h), (x + 3.5, h - 5), (x + 7, h)], fill=(0, 0, 0, 0))
    return img.rotate(rot, resample=Image.BICUBIC, expand=True)


def taped_card(img, border=16, bottom=None, caption=None, tape_rot=-6):
    """Photo/screenshot on white paper with a strip of tape at the top."""
    bottom = border if bottom is None else bottom
    w, h = img.size
    card = Image.new("RGBA", (w + border * 2, h + border + bottom), WHITE + (255,))
    card.paste(img.convert("RGB"), (border, border))
    if caption:
        f = F_MARK(40)
        tw = f.getlength(caption)
        ImageDraw.Draw(card).text(((card.width - tw) / 2, h + border + (bottom - 52) / 2), caption, font=f, fill=INK)
    out = Image.new("RGBA", (card.width, card.height + 30), (0, 0, 0, 0))
    out.alpha_composite(card, (0, 30))
    tp = tape(170, 48, tape_rot)
    out.alpha_composite(tp, ((out.width - tp.width) // 2, 30 - tp.height // 2 + 4))
    return with_shadow(out)


def load_img(name, width):
    im = Image.open(f"{WD}/img/{name}").convert("RGB")
    return im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)


def card(w, h, bg=WHITE):
    img = Image.new("RGBA", (w, h), bg + (255,))
    ImageDraw.Draw(img).rectangle([0, 0, w - 1, h - 1], outline=INK + (255,), width=4)
    return img


def person_icon(col, size=110):
    img = Image.new("RGBA", (size, int(size * 1.35)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = size * 0.24
    d.ellipse([size / 2 - r, 4, size / 2 + r, 4 + 2 * r], fill=col + (255,), outline=INK + (255,), width=5)
    d.rounded_rectangle([size * 0.1, 2 * r + 14, size * 0.9, img.height - 4], radius=int(size * 0.3),
                        fill=col + (255,), outline=INK + (255,), width=5)
    return img


def logo(scale=1.0):
    """Typographic re-creation of the Aimi Curtain mark: gold ring + AC monogram + wordmark."""
    w, h = int(620 * scale), int(400 * scale)
    img = Image.new("RGBA", (w, h), INK + (255,))
    d = ImageDraw.Draw(img)
    d.rectangle([10 * scale, 10 * scale, w - 10 * scale, h - 10 * scale], outline=GOLD + (255,), width=max(2, int(3 * scale)))
    cx, cy, r = w / 2, 150 * scale, 105 * scale
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD + (255,), width=max(3, int(6 * scale)))
    f = F_SERIF_I(int(150 * scale))
    tw, th, b = text_size(f, "AC")
    d.text((cx - tw / 2 - b[0], cy - th / 2 - b[1] - 4 * scale), "AC", font=f, fill=GOLD + (255,))
    f2 = F_SERIF(int(54 * scale))
    word = "AIMI CURTAIN"
    sp = 10 * scale
    total = sum(f2.getlength(c) for c in word) + sp * (len(word) - 1)
    x = cx - total / 2
    for c in word:
        d.text((x, 290 * scale), c, font=f2, fill=GOLD + (255,))
        x += f2.getlength(c) + sp
    return with_shadow(img)


def swatch(col, w=112, h=270):
    """Pleated fabric swatch: vertical sinusoidal shading."""
    xs = np.arange(w)
    shade = 0.82 + 0.18 * np.sin(xs / w * 2 * math.pi * 3) ** 2
    arr = np.ones((h, w, 3), np.float32) * np.array(col, np.float32) * shade[None, :, None]
    arr += np.random.default_rng(col[0]).normal(0, 3, (h, w, 1))
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    for x in range(10, w, 26):  # eyelet ring tops
        d.ellipse([x, 8, x + 14, 22], outline=(210, 210, 215, 255), width=3)
    d.rectangle([0, 0, w - 1, h - 1], outline=INK + (255,), width=3)
    return with_shadow(img, blur=6, alpha=0.3, pad=24)


def pin(size=120, col=RED):
    img = Image.new("RGBA", (size, int(size * 1.4)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = size / 2 - 6
    d.polygon([(size / 2 - r * 0.75, size / 2 + r * 0.6), (size / 2 + r * 0.75, size / 2 + r * 0.6),
               (size / 2, img.height - 4)], fill=col + (255,), outline=INK + (255,))
    d.ellipse([6, 6, size - 6, size - 6], fill=col + (255,), outline=INK + (255,), width=5)
    d.ellipse([size / 2 - r * 0.38, size / 2 - r * 0.38, size / 2 + r * 0.38, size / 2 + r * 0.38],
              fill=WHITE + (255,), outline=INK + (255,), width=4)
    return img


def cross_item(text, ok=False):
    f = F_SERIF(54)
    tw, th, b = text_size(f, text)
    img = Image.new("RGBA", (int(tw) + 150, 120), WHITE + (255,))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, img.width - 1, img.height - 1], outline=INK + (255,), width=4)
    cx, cy = 62, 60
    col = GREEN if ok else RED
    d.ellipse([cx - 38, cy - 38, cx + 38, cy + 38], fill=col + (255,))
    if ok:
        d.line([(cx - 18, cy + 2), (cx - 4, cy + 16), (cx + 20, cy - 14)], fill=WHITE + (255,), width=10)
    else:
        d.line([(cx - 16, cy - 16), (cx + 16, cy + 16)], fill=WHITE + (255,), width=10)
        d.line([(cx - 16, cy + 16), (cx + 16, cy - 16)], fill=WHITE + (255,), width=10)
    d.text((118 - b[0], (120 - th) / 2 - b[1]), text, font=f, fill=INK)
    return with_shadow(img, blur=6, alpha=0.3)


def whatsapp_button():
    f = F_ANTON(78)
    text = "WHATSAPP KAMI"
    tw, th, b = text_size(f, text)
    w, h = int(tw) + 190, 140
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=70, fill=GREEN + (255,), outline=INK + (255,), width=5)
    cx, cy, r = 78, h / 2, 42
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=WHITE + (255,), width=8)
    d.polygon([(cx - r * 0.8, cy + r * 0.55), (cx - r * 1.05, cy + r * 1.08), (cx - r * 0.35, cy + r * 0.88)], fill=WHITE + (255,))
    # handset
    d.rounded_rectangle([cx - 14, cy - 20, cx + 14, cy + 20], radius=8, fill=WHITE + (255,))
    d.text((150 - b[0], (h - th) / 2 - b[1]), text, font=f, fill=WHITE)
    return with_shadow(img, blur=8, alpha=0.35)


def arrow_down(col=RED, size=110):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([size * 0.36, 0, size * 0.64, size * 0.55], fill=col + (255,), outline=INK + (255,), width=4)
    d.polygon([(4, size * 0.48), (size - 4, size * 0.48), (size / 2, size - 4)], fill=col + (255,), outline=INK + (255,))
    return img


A = {}
A["k_ruang"] = kicker("RUANG TAMU ANDA")
A["h_bertahun"] = headline("Langsir dah bertahun?", 92, hl="bertahun")
A["st_kusam"] = stamp(["KUSAM"], [96])
A["k_tetamu"] = kicker("BILA TETAMU DATANG...")
A["st_segan"] = stamp(["SEGAN!"], [140])
A["h_suram"] = headline("Suram.", 130, bg=(225, 225, 225))
A["big_refresh"] = big("REFRESH!", 200, INK, YELLOW)
A["h_seri"] = headline("Naikkan seri", 80, hl="seri")
A["k_biar"] = kicker("BIAR KAMI SELESAIKAN")
A["logo"] = logo(1.0)
A["logo_s"] = logo(0.72)
A["x_tangga"] = cross_item("Panjat tangga")
A["x_ukur"] = cross_item("Pening ukuran")
A["k_az"] = kicker("KHIDMAT A – Z")
A["big_az"] = big("A  →  Z", 210, INK, YELLOW)
A["k_pilih"] = kicker("PILIH WARNA")
A["h_koleksi"] = headline("Beratus koleksi", 80, hl="koleksi")
A["big_100"] = big("100+", 170, WHITE, RED)
A["k_kulim"] = kicker("KULIM & BERDEKATAN")
A["h_wajah"] = headline("Wajah baru rumah anda!", 66, hl="baru")
A["k_kata"] = kicker("KATA PELANGGAN")
A["st_bumi"] = stamp(["100%", "BUMIPUTERA"], [120, 74], col=(30, 90, 170))
A["pin"] = with_shadow(pin(), blur=6, alpha=0.3)
A["wa"] = whatsapp_button()
A["arrow"] = arrow_down()
A["k_tanya"] = kicker("ADA PERTANYAAN?")
A["icons"] = [with_shadow(person_icon(c), blur=5, alpha=0.3) for c in [YELLOW, (120, 180, 200), (240, 150, 140)]]
A["swatches"] = [swatch(c) for c in [(95, 165, 172), (168, 206, 196), (212, 188, 150), (150, 108, 76),
                                     (128, 30, 46), (205, 38, 52), (118, 124, 134), (44, 60, 92)]]
A["t1"] = taped_card(load_img("1.jpg", 430), tape_rot=-4)
A["t2"] = taped_card(load_img("2.jpg", 470), tape_rot=5)
A["t3"] = taped_card(load_img("3.jpg", 450), tape_rot=-3)
A["t4"] = taped_card(load_img("4.jpg", 450), tape_rot=4)
A["photo5"] = taped_card(load_img("5.jpg", 400), bottom=84, caption="Pelanggan puas hati!")


def loc_card():
    img = card(470, 190)
    d = ImageDraw.Draw(img)
    p = pin(100)
    img.alpha_composite(p, (24, (190 - p.height) // 2))
    d.text((140, 28), "KELANG LAMA", font=F_ANTON(58), fill=INK)
    d.text((140, 112), "SQUARE, KULIM", font=F_TYPE(40), fill=INK)
    return with_shadow(img)


A["loc"] = loc_card()


def swatch_before_after(prog):
    """Two curtain swatches: bright original -> faded/dull."""
    w, h = 560, 330
    img = card(w, h)
    d = ImageDraw.Draw(img)
    base = np.array([196, 70, 60], np.float32)
    grey = base.mean()
    faded = base * (1 - 0.75 * prog) + (grey * 0.9 + 40) * 0.75 * prog
    f = F_TYPE(32)
    for i, (col, lab) in enumerate([(base, "DULU"), (faded, "SEKARANG")]):
        x0 = 40 + i * 270
        sw = swatch(tuple(int(c) for c in col), 200, 220)
        img.alpha_composite(sw, (x0 - 24, 14))
        tw = f.getlength(lab)
        d.text((x0 + 100 - tw / 2, 270), lab, font=f, fill=INK)
    d.line([(262, 130), (300, 130)], fill=INK, width=6)
    d.polygon([(298, 116), (318, 130), (298, 144)], fill=INK)
    return with_shadow(img)


def steps(t, active):
    """3-step process: UKUR -> JAHIT -> PASANG. active: list of activation times."""
    w, h = 1000, 260
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    xs = [150, 500, 850]
    labels = ["UKUR", "JAHIT", "PASANG"]
    y = 95
    for i in range(2):
        t0 = active[i + 1] - 0.5
        k = ease_out((t - t0) / 0.5) if t >= t0 else 0
        x0, x1 = xs[i] + 75, xs[i + 1] - 75
        for x in range(int(x0), int(x1), 26):
            d.line([(x, y), (min(x + 14, x1), y)], fill=INK + (255,), width=6)
        if k > 0:
            d.line([(x0, y), (x0 + (x1 - x0) * k, y)], fill=RED + (255,), width=8)
    f_n, f_l = F_ANTON(80), F_ANTON(54)
    for i, (x, lab) in enumerate(zip(xs, labels)):
        on = t >= active[i]
        k = ease_back((t - active[i]) / 0.35) if on else 0
        r = 70 * (1 + 0.12 * math.sin(math.pi * clamp((t - active[i]) / 0.35))) if on else 70
        d.ellipse([x - r, y - r, x + r, y + r], fill=(YELLOW if on else WHITE) + (255,), outline=INK + (255,), width=6)
        n = str(i + 1)
        tw, th, b = text_size(f_n, n)
        d.text((x - tw / 2 - b[0], y - th / 2 - b[1]), n, font=f_n, fill=INK)
        tw, th, b = text_size(f_l, lab)
        lab_img = label(lab, f_l, WHITE if on else INK, INK if on else WHITE, padx=14, pady=2)
        img.alpha_composite(lab_img, (int(x - lab_img.width / 2), 180))
    return with_shadow(img, blur=6, alpha=0.25)


def tape_measure(prog):
    w = int(60 + 420 * prog)
    img = Image.new("RGBA", (w + 10, 90), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 18, w, 72], fill=YELLOW + (255,), outline=INK + (255,), width=4)
    for i, x in enumerate(range(8, w, 12)):
        d.line([(x, 18), (x, 18 + (26 if i % 5 == 0 else 14))], fill=INK + (255,), width=3 if i % 5 == 0 else 2)
    f = F_TYPE(22)
    for i, x in enumerate(range(8, w - 20, 60)):
        d.text((x + 2, 46), str(i * 10), font=f, fill=INK)
    d.rectangle([w - 14, 8, w, 82], fill=(70, 70, 75, 255))
    return with_shadow(img, blur=5, alpha=0.3, pad=20)


def underline_marker(canvas, t, t0, x0, x1, y, col=RED, dur=0.35, width=12):
    if t < t0:
        return
    k = ease_out((t - t0) / dur)
    d = ImageDraw.Draw(canvas)
    pts = [(x0 + (x1 - x0) * i / 29 * k, y + 6 * math.sin(i / 29 * k * 9)) for i in range(30)]
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


# ---------------------------------------------------------------- B-roll polaroids
_broll_cache = {}


def broll_frame(name, t_rel):
    files = _broll_cache.setdefault(name, sorted(os.listdir(f"{WD}/{name}")))
    i = int(clamp(t_rel * FPS, 0, len(files) - 1))
    return Image.open(f"{WD}/{name}/{files[i]}")


def broll(canvas, t, name, t0, t1, cx, cy, rot, src0=0.0, caption=None, scale=1.0):
    """Taped polaroid playing a B-roll clip from src0, popping in at t0 and out at t1."""
    if t < t0 or t > t1 + 0.25:
        return
    cue(t, t0, "swoosh")
    fr = broll_frame(name, src0 + (t - t0))
    # slow push-in inside the frame
    k = clamp((t - t0) / max(t1 - t0, 0.1))
    z = 1 + 0.06 * k
    fw, fh = int(450 * z), int(800 * z)
    fr = fr.resize((fw, fh), Image.BILINEAR).crop(((fw - 450) // 2, (fh - 800) // 2, (fw - 450) // 2 + 450, (fh - 800) // 2 + 800))
    spr = taped_card(fr, border=16, bottom=84 if caption else 16, caption=caption, tape_rot=-5)
    if scale != 1.0:
        spr = spr.resize((int(spr.width * scale), int(spr.height * scale)), Image.BILINEAR)
    kk = ease_back((t - t0) / 0.4)
    a = clamp((t - t0) / 0.12)
    if t > t1:
        o = ease_out((t - t1) / 0.25)
        a *= 1 - o
    place(canvas, spr, cx, cy + 80 * (1 - ease_out((t - t0) / 0.4)), scale=max(0.01, 0.85 + 0.15 * kk), rot=rot, alpha=a)


# ---------------------------------------------------------------- captions
CAPS = [
    (0.10, 2.55, "Langsir di ruang tamu tu dah bertahun tak bertukar.", "bertahun"),
    (2.60, 5.10, "Warna asal yang terang dah pudar, nampak kusam.", "kusam"),
    (5.15, 7.65, "Bila ada tetamu atau saudara-mara", "tetamu"),
    (7.70, 10.20, "datang, mula rasa segan sebab suasana rumah", "segan"),
    (10.30, 11.95, "nampak suram dengan langsir lama.", "suram"),
    (12.05, 13.50, "Dah tiba masa untuk refresh", "refresh"),
    (13.60, 15.60, "dan naikkan balik seri ruang tamu anda.", "seri"),
    (15.70, 17.70, "Biar Aimi Curtain yang selesaikan.", "Aimi Curtain"),
    (17.85, 20.15, "Anda tak perlu penat-penat panjat tangga", "panjat tangga"),
    (20.30, 21.40, "atau pening fikir ukuran.", "ukuran"),
    (21.55, 23.75, "Kami sediakan khidmat A sampai Z.", "A sampai Z"),
    (24.10, 26.25, "Team kami akan datang ukur di rumah anda.", "ukur"),
    (26.70, 27.90, "Kami jahitkan dengan kemas", "kemas"),
    (28.00, 29.90, "dan buatkan pemasangan sekali.", "pemasangan"),
    (30.00, 31.85, "Anda pilih je warna langsir baru", "warna"),
    (31.90, 34.00, "dari beratus koleksi cantik yang kami ada.", "beratus koleksi"),
    (34.10, 35.85, "Jadi, orang Kulim dan berdekatan,", "Kulim"),
    (36.00, 37.90, "jom tukar wajah baru rumah anda!", "wajah baru"),
    (38.00, 40.25, "Kami syarikat 100% Bumiputera", "100% Bumiputera"),
    (40.30, 42.25, "di Kelang Lama Square, Kulim.", "Kelang Lama Square"),
    (42.30, 44.85, "Klik WhatsApp di bawah untuk sebarang pertanyaan.", "WhatsApp"),
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
            place(canvas, spr, W / 2, 1660 + 30 * (1 - k), alpha=k)


# ---------------------------------------------------------------- person layer
# layouts: (scale relative to canvas width, centre x, bottom offset)
FULL = (0.80, 540, 0)
CLOSE = (0.98, 540, 250)
CORNER = (0.56, 790, 0)
# keyframes: (time, layout, transition seconds; 0 = hard cut, used on the clip's jump cuts)
SHOTS = [(0.0, FULL, 0), (2.77, (0.86, 540, 60), 0), (5.58, FULL, 0), (8.02, CLOSE, 0), (11.8, FULL, 0),
         (13.55, CORNER, 0.45), (15.65, FULL, 0.45), (17.8, CORNER, 0.45), (21.43, FULL, 0),
         (24.05, FULL, 0), (29.97, FULL, 0), (34.07, CORNER, 0),
         (42.25, CORNER, 0)]
_mask_cache = {}


_K_GROW = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))


def load_mask(i):
    """u2net_human_seg gives crisp edges but also grabs the dark curtain behind the presenter;
    the MediaPipe selfie mask knows where the person is. Keep u2net only near the MediaPipe
    person (extended downwards, where the body leaves the frame)."""
    i = max(0, min(N - 1, i))
    if i not in _mask_cache:
        name = FRAMES[i][:-4]
        m = cv2.imread(f"{WD}/masks/{name}.png", cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
        p = cv2.imread(f"{WD}/mp/{name}.png", cv2.IMREAD_GRAYSCALE)
        hard = (p > 64).astype(np.uint8)
        n, lab, stats, _ = cv2.connectedComponentsWithStats(hard)
        if n > 1:  # largest blob only
            hard = (lab == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
        # the body continues out of frame: in the lower half, extend the region downwards
        h2 = hard.shape[0] // 2
        hard[h2:] = np.maximum.accumulate(hard[h2:], axis=0)
        region = cv2.GaussianBlur(cv2.dilate(hard, _K_GROW).astype(np.float32), (0, 0), 6)
        soft = np.clip((p.astype(np.float32) / 255 - 0.45) / 0.25, 0, 1) * hard
        _mask_cache[i] = np.maximum(m * region, soft)
        if len(_mask_cache) > 6:
            _mask_cache.pop(next(iter(_mask_cache)))
    return _mask_cache[i]


def layout_at(t):
    prev = [s for s in SHOTS if s[0] <= t]
    cur = prev[-1]
    lay = cur[1]
    if cur[2] > 0 and len(prev) > 1:
        k = ease_io((t - cur[0]) / cur[2])
        a = prev[-2][1]
        lay = tuple(a[j] + (lay[j] - a[j]) * k for j in range(3))
    nxt = [s[0] for s in SHOTS if s[0] > t]
    dur = (nxt[0] if nxt else N / FPS) - cur[0]
    return lay, (t - cur[0]) / max(dur, 0.1)


def person_layer(i, t):
    src = cv2.cvtColor(cv2.imread(f"{WD}/frames/{FRAMES[i]}"), cv2.COLOR_BGR2RGB)
    m = 0.25 * load_mask(i - 1) + 0.5 * load_mask(i) + 0.25 * load_mask(i + 1)
    m = np.clip((m - 0.25) / 0.5, 0, 1)
    (scale, cx, yoff), k = layout_at(t)
    sc = scale * (1 + 0.03 * k) * W / src.shape[1]
    pw, ph = int(src.shape[1] * sc), int(src.shape[0] * sc)
    src = cv2.resize(src, (pw, ph), interpolation=cv2.INTER_AREA)
    m = cv2.resize(m, (pw, ph), interpolation=cv2.INTER_LINEAR)
    s = src.astype(np.float32)
    s = (s - 128) * 1.06 + 128 + np.array([6, 2, -4], np.float32)
    s = np.clip(s, 0, 255)
    pad = 40
    mp = cv2.copyMakeBorder(m, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    mp[-pad:, :] = np.maximum(mp[-pad:, :], mp[-pad - 1:-pad, :])
    kr = max(9, int(29 * scale / 0.8)) | 1
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kr, kr))
    outline = cv2.GaussianBlur(cv2.dilate(mp, ker), (0, 0), 1.2)
    shadow = cv2.GaussianBlur(outline, (0, 0), 14) * 0.38
    x0 = int(cx - pw / 2) - pad
    y0 = int(H - ph + yoff) - pad
    return s, mp, outline, shadow, x0, y0, pad


def composite_person(base, i, t, alpha=1.0):
    s, mp, outline, shadow, x0, y0, pad = person_layer(i, t)
    hh, ww = mp.shape

    def region(dx, dy):
        X0, Y0 = x0 + dx, y0 + dy
        cx0, cy0 = max(0, X0), max(0, Y0)
        cx1, cy1 = min(W, X0 + ww), min(H, Y0 + hh)
        return (slice(cy0, cy1), slice(cx0, cx1)), (slice(cy0 - Y0, cy1 - Y0), slice(cx0 - X0, cx1 - X0))

    (dst, srcr) = region(14, 20)
    base[dst] *= (1 - alpha * shadow[srcr])[..., None]
    (dst, srcr) = region(0, 0)
    o = alpha * outline[srcr][..., None]
    base[dst] = base[dst] * (1 - o) + 255 * o
    sp = cv2.copyMakeBorder(s, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    a = alpha * mp[srcr][..., None]
    base[dst] = base[dst] * (1 - a) + sp[srcr] * a


# ---------------------------------------------------------------- overlays per scene
def overlays(c, t):
    # 1. problem: old, faded curtains (0 - 5.1)
    slide(c, A["k_ruang"], t, 0.15, 290, 140, rot=-3, t1=5.0)
    pop(c, A["h_bertahun"], t, 0.4, W / 2, 265, rot=-1.5, t1=2.55)
    underline_marker(c, t, 1.3, 560, 950, 330) if t < 2.8 else None
    if 2.6 <= t <= 5.25:
        prog = ease_io((t - 3.1) / 1.6)
        a = clamp((t - 2.6) / 0.15) * (1 - clamp((t - 5.0) / 0.25))
        cue(t, 2.6, "swoosh")
        place(c, swatch_before_after(prog), W / 2, 340, rot=2, alpha=a,
              scale=ease_back((t - 2.6) / 0.35))
    slam(c, A["st_kusam"], t, 4.3, 690, 300, rot=-12, t1=5.0)

    # 2. guests arrive -> embarrassed (5.15 - 10.2)
    slide(c, A["k_tetamu"], t, 5.15, 330, 140, rot=-2, t1=7.95)
    if 5.3 <= t <= 10.35:
        for j, x in enumerate([330, 540, 750]):
            # walk in from the right
            t0 = 5.4 + j * 0.25
            if t >= t0:
                cue(t, t0, "pop")
                k = ease_out((t - t0) / 0.6)
                bob = 8 * abs(math.sin((t - t0) * 9)) * (1 - k)
                a = clamp((t - t0) / 0.12) * (1 - clamp((t - 10.1) / 0.25))
                place(c, A["icons"][j], x + 500 * (1 - k), 330 - bob, alpha=a)
    slam(c, A["st_segan"], t, 8.05, W / 2, 150, rot=-6, t1=10.1)

    # 3. gloomy -> REFRESH (10.3 - 15.6)
    pop(c, A["h_suram"], t, 10.35, W / 2, 230, rot=-2, t1=11.95)
    if 12.0 <= t <= 13.75:
        cue(t, 12.0, "whoosh")
        k = ease_back((t - 12.0) / 0.3)
        a = 1 - clamp((t - 13.5) / 0.25)
        place(c, A["big_refresh"], W / 2, 300, scale=max(0.01, k), rot=-4, alpha=a)
        # burst lines
        if t < 12.6:
            d = ImageDraw.Draw(c)
            r0 = 230 + 380 * ease_out((t - 12.0) / 0.6)
            for j in range(14):
                ang = j / 14 * 2 * math.pi
                r1 = r0 - 90
                d.line([(540 + r1 * math.cos(ang), 300 + r1 * 0.6 * math.sin(ang)),
                        (540 + r0 * math.cos(ang), 300 + r0 * 0.6 * math.sin(ang))],
                       fill=RED + (int(255 * (1 - clamp((t - 12.3) / 0.3))),), width=9)
    broll(c, t, "b3", 13.6, 15.55, 330, 720, rot=-3, src0=4.5, caption="Selepas: kemas & elegan")
    pop(c, A["h_seri"], t, 13.65, 770, 200, rot=2, t1=15.55)

    # 4. brand (15.7 - 17.7)
    slide(c, A["k_biar"], t, 15.7, W / 2, 140, rot=-1.5, t1=17.65, dx=0, dy=-120)
    pop(c, A["logo"], t, 15.85, W / 2, 380, rot=0, t1=17.65, sfx="ding")

    # 5. no ladders, no measuring headaches (17.85 - 21.4)
    broll(c, t, "b4", 17.85, 21.35, 300, 740, rot=-3, src0=0.0, caption="Kami yang pasangkan")
    slide(c, A["x_tangga"], t, 17.95, 770, 240, rot=2, t1=21.35, dx=300)
    slide(c, A["x_ukur"], t, 20.3, 770, 400, rot=-2, t1=21.35, dx=300)

    # 6. A-Z service: measure, sew, install (21.55 - 29.9)
    slide(c, A["k_az"], t, 21.55, 260, 130, rot=-3, t1=29.85)
    pop(c, A["big_az"], t, 21.65, W / 2, 330, rot=-2, t1=23.95)
    if 24.05 <= t <= 30.1:
        a = clamp((t - 24.05) / 0.15) * (1 - clamp((t - 29.85) / 0.25))
        cue(t, 24.05, "swoosh")
        place(c, steps(t, [24.15, 26.7, 28.0]), W / 2, 330, alpha=a)
        cue(t, 26.7, "pop")
        cue(t, 28.0, "pop")
    if 24.3 <= t <= 26.65:
        a = clamp((t - 24.3) / 0.12) * (1 - clamp((t - 26.4) / 0.25))
        place(c, tape_measure(ease_out((t - 24.3) / 0.9)), 300, 520, rot=-2, alpha=a)
    pop(c, A["t1"], t, 26.9, 235, 600, rot=-5, t1=29.85)
    if 28.1 <= t <= 30.1:
        a = clamp((t - 28.1) / 0.12) * (1 - clamp((t - 29.85) / 0.25))
        place(c, cross_item("Siap dipasang", ok=True), 790, 560, rot=3, alpha=a, scale=ease_back((t - 28.1) / 0.35))

    # 7. hundreds of colours (30.0 - 34.0)
    slide(c, A["k_pilih"], t, 30.0, 230, 130, rot=-3, t1=33.95)
    if 30.05 <= t <= 34.2:
        a = 1 - clamp((t - 33.95) / 0.25)
        for j, spr in enumerate(A["swatches"]):
            t0 = 30.1 + j * 0.16
            if t >= t0:
                cue(t, t0, "tick")
                k = ease_back((t - t0) / 0.3)
                x = 95 + j * 127
                ang = (j - 3.5) * 4
                y = 360 + abs(j - 3.5) * 14 if t < 31.85 else 250 + abs(j - 3.5) * 14
                place(c, spr, x, y + 60 * (1 - k), rot=-ang, alpha=a * clamp((t - t0) / 0.1), scale=0.85)
    if 31.85 <= t <= 34.2:
        a = 1 - clamp((t - 33.95) / 0.25)
        pop(c, A["h_koleksi"], t, 31.9, 380, 470, rot=-2, t1=33.95)
        slam(c, A["big_100"], t, 32.3, 880, 450, rot=8, t1=33.95)

    # 8. Kulim & nearby -> fresh new look (34.1 - 37.9)
    broll(c, t, "b2", 34.1, 37.9, 300, 760, rot=-3, src0=0.0, caption="Projek di Kulim")
    slide(c, A["k_kulim"], t, 34.1, 790, 470, rot=2, t1=35.9, dx=300)
    if 34.2 <= t <= 36.15:
        drop = 1 - ease_out((t - 34.2) / 0.45)
        a = clamp((t - 34.2) / 0.1) * (1 - clamp((t - 35.9) / 0.25))
        cue(t, 34.2, "pop")
        place(c, A["pin"], 790, 300 - 260 * drop, alpha=a)
    pop(c, A["h_wajah"], t, 36.0, W / 2, 175, rot=1.5, t1=37.9)

    # 9. 100% Bumiputera + customers say (38.0 - 42.25)
    slide(c, A["k_kata"], t, 38.0, 250, 120, rot=-3, t1=42.2)
    pop(c, A["t2"], t, 38.15, 300, 380, rot=-3, t1=42.2)
    pop(c, A["t4"], t, 38.75, 320, 700, rot=3, t1=42.2)
    pop(c, A["t3"], t, 39.35, 300, 1000, rot=-2, t1=42.2)
    slam(c, A["st_bumi"], t, 38.1, 800, 260, rot=9, t1=42.2)
    pop(c, A["loc"], t, 40.3, 800, 560, rot=-2, t1=42.2)

    # 10. CTA (42.3 - end)
    pop(c, A["photo5"], t, 42.35, 300, 690, rot=-4)
    pop(c, A["k_tanya"], t, 42.45, 800, 160, rot=3)
    pop(c, A["logo_s"], t, 42.6, 800, 400, rot=2, sfx="ding")
    if t >= 43.0:
        cue(t, 43.0, "pop")
        k = ease_back((t - 43.0) / 0.4)
        place(c, A["wa"], W / 2, 1420, scale=max(0.01, k), rot=-1.5)
        bob = 18 * abs(math.sin((t - 43.0) * 5))
        place(c, A["arrow"], 150, 1290 + bob, alpha=clamp((t - 43.3) / 0.15))


# ---------------------------------------------------------------- frame
def render(t):
    i = min(N - 1, int(t * FPS))
    base = BG.astype(np.float32)
    tail = clamp((t - N / FPS) / 0.5)
    composite_person(base, i, t, alpha=1 - tail)
    base += GRAIN[int(t * FPS) % len(GRAIN)][..., None] * 0.6
    canvas = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")
    overlays(canvas, t)
    rgb = np.asarray(canvas.convert("RGB")).astype(np.float32)
    # "suram": drain colour while the narration describes the gloomy room, snap back on REFRESH
    g = clamp((t - 10.3) / 0.6) * (1 - clamp((t - 12.0) / 0.05))
    if g > 0:
        lum = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
        rgb = rgb * (1 - g) + (lum[..., None] * 0.85 + 10) * g
    if 12.0 <= t < 12.12:  # white flash
        rgb = rgb + (255 - rgb) * (1 - (t - 12.0) / 0.12) * 0.8
    canvas = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert("RGBA")
    draw_caption(canvas, t)
    rgb = np.asarray(canvas.convert("RGB"))
    if t < 0.25 or t > TOTAL - 0.4:
        f = clamp(t / 0.25) * clamp((TOTAL - t) / 0.4)
        rgb = (rgb.astype(np.float32) * f).astype(np.uint8)
    return rgb


def main():
    out = sys.stdout.buffer
    nf = int(round(TOTAL * FPS))
    for i in range(nf):
        out.write(render(i / FPS).tobytes())
        if i % 100 == 0:
            print(f"frame {i}/{nf}", file=sys.stderr, flush=True)
    with open(f"{WD}/sfx.json", "w") as fh:
        json.dump(sorted(SFX), fh)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        for ts in sys.argv[2:]:
            Image.fromarray(render(float(ts))).save(f"{WD}/preview_{ts}.jpg", quality=85)
    else:
        main()
