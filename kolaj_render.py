"""40s Vox-style collage promo: "Kepentingan video dalam marketing bisnes".

A single selfie is cut out (rembg u2net_human_seg) and used as paper stickers on a
textured paper background, with kinetic word-by-word captions, B-roll graphics,
zoom punches, paper-wipe transitions and a CTA card.

Usage: python3 kolaj_render.py <workdir> [t1 t2 ...]
  <workdir>/photo.jpg                   source photo
  <workdir>/mask_u2net_human_seg.png    person mask
  <workdir>/refs/<name>.jpg              lifestyle photos cut from the reference collages
  <workdir>/fonts/                      Anton.ttf Playfair.ttf Special.ttf Permanent.ttf InterXB.otf
With no times: writes raw RGB 1080x1920@30 frames to stdout (pipe into ffmpeg).
With times: saves preview_<t>.jpg for each.
"""
import math
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

WD = sys.argv[1]
W, H, FPS = 1080, 1920, 30
DUR = 40.0
N = int(DUR * FPS)

CREAM = (242, 235, 221)
INK = (24, 22, 20)
YELLOW = (255, 212, 0)
RED = (226, 64, 43)
BLUE = (60, 110, 190)
TEAL = (40, 150, 140)
WHITE = (255, 255, 255)

_fc = {}


def font(name, size):
    k = (name, size)
    if k not in _fc:
        ext = "otf" if name.startswith("Inter") else "ttf"
        _fc[k] = ImageFont.truetype(f"{WD}/fonts/{name}.{ext}", size)
    return _fc[k]


F_ANTON = lambda s: font("Anton", s)
F_SERIF = lambda s: font("Playfair", s)
F_TYPE = lambda s: font("Special", s)
F_MARK = lambda s: font("Permanent", s)
F_CAP = lambda s: font("InterXB", s)


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_inout(x):
    x = clamp(x)
    return 3 * x * x - 2 * x * x * x


def ease_back(x):
    x = clamp(x)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


# ---------------------------------------------------------------- paper backgrounds
def paper(col, seed=7, grid=True):
    rng = np.random.default_rng(seed)
    bg = np.ones((H, W, 3), np.float32) * np.array(col, np.float32)
    low = cv2.resize(rng.normal(0, 1, (H // 40, W // 40)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    fine = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.8)
    bg += (low * 6 + fine * 4)[..., None]
    img = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8))
    if grid:
        d = ImageDraw.Draw(img, "RGBA")
        for x in range(0, W, 54):
            d.line([(x, 0), (x, H)], fill=(120, 140, 170, 28), width=1)
        for y in range(0, H, 54):
            d.line([(0, y), (W, y)], fill=(120, 140, 170, 28), width=1)
    yy, xx = np.mgrid[0:H, 0:W]
    v = ((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2
    arr = np.asarray(img).astype(np.float32) * (1 - 0.3 * np.clip(v, 0, 1))[..., None]
    return arr.astype(np.uint8)


def torn_poly(x0, y0, x1, y1, seed, amp=10, step=14):
    """Polygon of a rectangle with jagged (torn) edges."""
    rng = np.random.default_rng(seed)
    pts = []
    for x in np.arange(x0, x1, step):
        pts.append((x, y0 + rng.uniform(-amp, amp)))
    for y in np.arange(y0, y1, step):
        pts.append((x1 + rng.uniform(-amp, amp), y))
    for x in np.arange(x1, x0, -step):
        pts.append((x, y1 + rng.uniform(-amp, amp)))
    for y in np.arange(y1, y0, -step):
        pts.append((x0 + rng.uniform(-amp, amp), y))
    return pts


def add_block(bg, col, box, seed, rot=0):
    """Torn coloured paper block glued onto the background."""
    img = Image.fromarray(bg).convert("RGBA")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.polygon(torn_poly(*box, seed=seed), fill=col + (255,))
    if rot:
        lay = lay.rotate(rot, resample=Image.BICUBIC, center=((box[0] + box[2]) / 2, (box[1] + box[3]) / 2))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.putalpha(lay.split()[3].point(lambda v: int(v * 0.25)))
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    img.alpha_composite(sh, (6, 10))
    img.alpha_composite(lay)
    return np.asarray(img.convert("RGB"))


def halftone_bg(col_bg, col_dot, step=26):
    img = Image.fromarray(paper(col_bg, seed=11, grid=False)).convert("RGBA")
    d = ImageDraw.Draw(img)
    for yi, y in enumerate(range(0, H + step, step)):
        for x in range(-step, W + step, step):
            xx = x + (step / 2 if yi % 2 else 0)
            # dots grow toward the bottom-right
            r = 2 + 7 * clamp((xx / W * 0.5 + y / H * 0.8) - 0.25)
            d.ellipse([xx - r, y - r, xx + r, y + r], fill=col_dot + (90,))
    return np.asarray(img.convert("RGB"))


BG_CREAM = paper(CREAM)
BG_S2 = add_block(paper(CREAM, 8), (150, 190, 235), (-40, 120, 760, 980), seed=3, rot=-3)
BG_S3 = add_block(paper(CREAM, 9), YELLOW, (140, 260, 1180, 1500), seed=5, rot=4)
BG_S4 = halftone_bg((255, 222, 60), (230, 150, 0))
BG_S5 = add_block(paper(CREAM, 12), (255, 190, 180), (-60, 1000, 1140, 2000), seed=6, rot=2)
BG_S6 = add_block(paper(CREAM, 13), (190, 225, 205), (300, 140, 1160, 1250), seed=8, rot=-4)
BG_S7 = paper(CREAM, 14)
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
        s = s.copy()
        s.putalpha(s.split()[3].point(lambda v: int(v * alpha)))
    x, y = int(cx - s.width / 2), int(cy - s.height / 2)
    if x >= W or y >= H or x + s.width <= 0 or y + s.height <= 0:
        return
    comp_clip(canvas, s, x, y)


def comp_clip(canvas, s, x, y):
    """alpha_composite that tolerates sprites hanging off any edge."""
    cw, ch = canvas.size
    cx0, cy0 = max(0, -x), max(0, -y)
    cx1, cy1 = min(s.width, cw - x), min(s.height, ch - y)
    if cx1 > cx0 and cy1 > cy0:
        canvas.alpha_composite(s.crop((cx0, cy0, cx1, cy1)), (x + cx0, y + cy0))


def pop(canvas, sprite, t, t0, cx, cy, rot=0.0, t1=None, dur=0.35, scale=1.0):
    if t < t0 or (t1 is not None and t > t1 + 0.25):
        return
    k = ease_back((t - t0) / dur)
    a = clamp((t - t0) / 0.12)
    if t1 is not None and t > t1:
        o = ease_out((t - t1) / 0.25)
        a *= 1 - o
        k *= 1 - 0.15 * o
    place(canvas, sprite, cx, cy, scale=max(0.01, k * scale), rot=rot, alpha=a)


def slide(canvas, sprite, t, t0, cx, cy, rot=0.0, t1=None, dx=-300, dy=0, dur=0.4):
    if t < t0 or (t1 is not None and t > t1 + 0.25):
        return
    k = ease_out((t - t0) / dur)
    a = clamp((t - t0) / 0.15)
    if t1 is not None and t > t1:
        a *= 1 - ease_out((t - t1) / 0.25)
    place(canvas, sprite, cx + dx * (1 - k), cy + dy * (1 - k), rot=rot, alpha=a)


def kicker(text, size=40):
    return with_shadow(label(text, F_TYPE(size), WHITE, INK, padx=22, pady=12), blur=6, alpha=0.3)


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
    a = np.array(img.split()[3]).astype(np.float32)
    holes = cv2.GaussianBlur(np.random.default_rng(3).random(a.shape).astype(np.float32), (0, 0), 1.6)
    a *= np.where(holes > 0.53, 0.25, 1.0)
    img.putalpha(Image.fromarray(a.astype(np.uint8)))
    return img


def card(w, h, bg=WHITE, radius=0):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=bg + (255,), outline=INK + (255,), width=4)
    return img


# ---------------------------------------------------------------- the person stickers
def bw_dramatic(rgb):
    """High-contrast black & white: local contrast (CLAHE) + S-curve + slightly crushed blacks."""
    g = (rgb[..., 0] * 0.30 + rgb[..., 1] * 0.59 + rgb[..., 2] * 0.11).astype(np.uint8)
    g = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8)).apply(g).astype(np.float32) / 255
    g = 0.5 + 0.5 * np.tanh(2.4 * (g - 0.52)) / math.tanh(1.2)
    g = np.clip((g - 0.04) / 0.98, 0, 1) * 255
    return np.repeat(g[..., None], 3, axis=2)


def torn_rect_mask(h, w, seed, inset=14, amp=7):
    """1 inside a rectangle whose four edges are jagged like torn paper."""
    img = Image.new("L", (w, h), 0)
    ImageDraw.Draw(img).polygon(torn_poly(inset, inset, w - inset, h - inset, seed=seed, amp=amp, step=12), fill=255)
    return np.asarray(img).astype(np.float32) / 255


def sticker(img, mask, outline_edges):
    """RGBA paper cut-out with white border + drop shadow. outline_edges=False leaves frame edges open."""
    pad = 40
    mp = cv2.copyMakeBorder(mask, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    ip = cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    if not outline_edges:
        mp[-pad:, :] = np.maximum(mp[-pad:, :], mp[-pad - 1:-pad, :])
        mp[:, :pad] = np.maximum(mp[:, :pad], mp[:, pad:pad + 1])
        mp[:, -pad:] = np.maximum(mp[:, -pad:], mp[:, -pad - 1:-pad])
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
    ol = cv2.GaussianBlur(cv2.dilate(mp, ker), (0, 0), 1.2)
    rgb = ip * mp[..., None] + 255 * (1 - mp[..., None])
    rgba = np.dstack([rgb, ol * 255]).astype(np.uint8)
    return with_shadow(Image.fromarray(rgba, "RGBA"), offset=(14, 20), blur=14, alpha=0.38, pad=50)


def build_stickers(photo, mask, head_bottom=0.54, seed=21):
    """Full (frame-filling) and head-and-shoulders (torn) stickers, black & white."""
    im = Image.open(photo).convert("RGB")
    mk = Image.open(mask).convert("L")
    tw = 1127  # normalise every photo to the same width so stickers share one scale
    th = int(im.height * tw / im.width)
    src = np.asarray(im.resize((tw, th), Image.LANCZOS)).astype(np.float32)
    m = np.asarray(mk.resize((tw, th), Image.LANCZOS)).astype(np.float32) / 255
    m = np.clip((m - 0.2) / 0.6, 0, 1)
    s = bw_dramatic(src)
    full = sticker(s, m, outline_edges=False)
    top = int(np.argmax(m.max(axis=1) > 0.5))
    y0, y1 = max(0, top - 70), int(th * head_bottom)
    hm = m[y0:y1].copy() * torn_rect_mask(y1 - y0, tw, seed)
    head = sticker(s[y0:y1], hm, outline_edges=True)
    return full, head


EXPR = f"{WD}/expr"
STK = {
    "asal": build_stickers(f"{WD}/photo.jpg", f"{WD}/mask_u2net_human_seg.png"),
    "senyum": build_stickers(f"{EXPR}/4.jpg", f"{EXPR}/4_mask.png", seed=22),
    "sinis": build_stickers(f"{EXPR}/5.jpg", f"{EXPR}/5_mask.png", seed=23),
    "fikir": build_stickers(f"{EXPR}/6.jpg", f"{EXPR}/6_mask.png", head_bottom=0.74, seed=24),
    "tunjuk": build_stickers(f"{EXPR}/7.jpg", f"{EXPR}/7_mask.png", seed=25),
    "terkejut": build_stickers(f"{EXPR}/8.jpg", f"{EXPR}/8_mask.png", seed=26),
}
FULL_SC = W / (STK["asal"][0].width - 100) * 1.02  # full sticker: photo spans canvas width


def polaroid(name, w=430, caption=None, tape=True, seed=0):
    """Reference photo as a white-bordered print with masking tape (and optional marker caption)."""
    im = Image.open(f"{WD}/refs/{name}.jpg").convert("RGB")
    ix, iy = int(im.width * 0.03), int(im.height * 0.03)
    im = im.crop((ix, iy, im.width - ix, im.height - iy))
    h = int(w * im.height / im.width)
    im = im.resize((w, h), Image.LANCZOS)
    arr = np.clip((np.asarray(im).astype(np.float32) - 128) * 1.05 + 128 + np.array([6, 2, -4], np.float32), 0, 255)
    b, bb = 18, (90 if caption else 18)
    pw, ph = w + 2 * b, h + b + bb
    pol = Image.new("RGBA", (pw, ph), (250, 248, 242, 255))
    pol.paste(Image.fromarray(arr.astype(np.uint8)), (b, b))
    d = ImageDraw.Draw(pol)
    d.rectangle([0, 0, pw - 1, ph - 1], outline=(215, 210, 200, 255), width=2)
    if caption:
        f = F_MARK(50)
        d.text(((pw - f.getlength(caption)) / 2, h + b + 12), caption, font=f, fill=INK)
    out = Image.new("RGBA", (pw + 60, ph + 60), (0, 0, 0, 0))
    out.alpha_composite(pol, (30, 30))
    if tape:
        rng = np.random.default_rng(seed)
        tw, th = 170, 52
        tp = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        ImageDraw.Draw(tp).polygon(torn_poly(0, 0, tw, th, seed=seed + 50, amp=4, step=8), fill=(236, 230, 205, 190))
        tp = tp.rotate(rng.uniform(-12, 12), resample=Image.BICUBIC, expand=True)
        out.alpha_composite(tp, (int(pw / 2 + 30 - tp.width / 2 + rng.uniform(-60, 60)), 2))
    return with_shadow(out, blur=10, alpha=0.35)


REF = {}


def ref(name, w=430, caption=None, seed=0):
    k = (name, w, caption)
    if k not in REF:
        REF[k] = polaroid(name, w, caption, seed=seed)
    return REF[k]


def alive(c, spr, t, t0, cx, cy, sc=1.0, rot=0.0, t1=None, rise=520):
    """Lively entrance: rises with overshoot, swings and squashes into place, then
    'boils' like stop-motion (re-posed 8x per second) with a gentle bob; drops away at t1."""
    if t < t0 or (t1 is not None and t > t1 + 0.3):
        return
    u = t - t0
    dy = rise * (1 - ease_back(u / 0.45))
    swing = 13 * math.exp(-5 * u) * math.cos(13 * u)
    sq = 0.11 * math.exp(-7 * u) * math.sin(22 * u)
    rng = np.random.default_rng(int(t * 8) * 7919 + int(t0 * 100))
    jx, jy, jr = rng.uniform(-4, 4, 3) * (1, 1, 0.3)
    bob = 7 * math.sin(t * 2.3 + t0)
    a = clamp(u / 0.1)
    if t1 is not None and t > t1:
        o = ease_out((t - t1) / 0.3)
        a *= 1 - o
        dy += 260 * o * o
    s = spr.resize((max(1, int(spr.width * sc * (1 - sq))), max(1, int(spr.height * sc * (1 + sq)))), Image.BILINEAR)
    place(c, s, cx + jx, cy + dy + jy + bob, rot=rot + swing + jr, alpha=a)


def draw_full(c, t, who, t0, cy_offset, scale=1.0, cx=W / 2, t1=None):
    """Frame-filling sticker anchored to the bottom; cy_offset pushes it down."""
    spr = STK[who][0]
    sc = FULL_SC * scale
    alive(c, spr, t, t0, cx, H - spr.height * sc / 2 + cy_offset + 50 * sc, sc=sc, t1=t1, rise=900)


def draw_head(c, t, who, cx, cy, scale, t0, rot=0.0, t1=None):
    alive(c, STK[who][1], t, t0, cx, cy, sc=scale, rot=rot, t1=t1)


def sparkle(c, t, t0, cx, cy, r, t1=None):
    """Four-point twinkle star (white with ink outline) that pops and pulses."""
    if t < t0 or (t1 is not None and t > t1):
        return
    k = ease_back((t - t0) / 0.3) * (1 + 0.15 * math.sin((t - t0) * 9))
    rr = r * k
    ang = (t - t0) * 0.8
    pts = []
    for i in range(8):
        a = ang + i * math.pi / 4
        d = rr if i % 2 == 0 else rr * 0.32
        pts.append((cx + d * math.cos(a), cy + d * math.sin(a)))
    ImageDraw.Draw(c).polygon(pts, fill=WHITE + (255,), outline=INK + (255,), width=5)


def doodle(c, t, t0, text, cx, cy, size=130, col=INK, rot=0.0, t1=None):
    """Hand-drawn marker glyph ('?', '!!') that pops in and wiggles."""
    if t < t0 or (t1 is not None and t > t1):
        return
    f = F_MARK(size)
    w_, h_, b = text_size(f, text)
    img = Image.new("RGBA", (w_ + 40, h_ + 40), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((20 - b[0], 20 - b[1]), text, font=f, fill=col + (255,))
    k = ease_back((t - t0) / 0.3)
    place(c, img, cx, cy + 6 * math.sin(t * 6 + t0), scale=max(0.01, k), rot=rot + 8 * math.sin(t * 5 + t0))


# ---------------------------------------------------------------- icons / B-roll
def play_icon(size=220, col=RED):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([6, 6, size - 6, size - 6], fill=col + (255,), outline=INK + (255,), width=8)
    s = size
    d.polygon([(s * 0.40, s * 0.30), (s * 0.40, s * 0.70), (s * 0.72, s * 0.50)], fill=WHITE + (255,))
    return with_shadow(img, blur=6)


def eye_icon(size=120):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = [(size * 0.05 + size * 0.9 * i / 40, size / 2 - size * 0.3 * math.sin(math.pi * i / 40)) for i in range(41)]
    pts += [(size * 0.95 - size * 0.9 * i / 40, size / 2 + size * 0.3 * math.sin(math.pi * i / 40)) for i in range(41)]
    d.polygon(pts, fill=WHITE + (255,), outline=INK + (255,), width=6)
    r = size * 0.17
    d.ellipse([size / 2 - r, size / 2 - r, size / 2 + r, size / 2 + r], fill=BLUE + (255,), outline=INK + (255,), width=5)
    d.ellipse([size / 2 - r / 2.5, size / 2 - r / 2.5, size / 2 + r / 2.5, size / 2 + r / 2.5], fill=INK + (255,))
    return img


def speaker_icon(size=120):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    d.polygon([(s * .1, s * .38), (s * .3, s * .38), (s * .52, s * .18), (s * .52, s * .82), (s * .3, s * .62), (s * .1, s * .62)],
              fill=YELLOW + (255,), outline=INK + (255,), width=5)
    for k in (0.18, 0.3):
        d.arc([s * (0.5 - k), s * (0.5 - k * 1.3), s * (0.62 + k), s * (0.5 + k * 1.3)], -45, 45, fill=INK + (255,), width=6)
    return img


def heart_icon(size=120, col=RED):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = []
    for i in range(100):
        a = i / 100 * 2 * math.pi
        x = 16 * math.sin(a) ** 3
        y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append((size / 2 + x * size / 38, size / 2 - y * size / 38))
    d.polygon(pts, fill=col + (255,), outline=INK + (255,), width=6)
    return img


def icon_chip(icon, text, bg):
    f = F_ANTON(70)
    tw = int(f.getlength(text))
    img = card(tw + 200, 150, bg)
    img.alpha_composite(icon.resize((110, 110)), (24, 20))
    d = ImageDraw.Draw(img)
    asc, desc = f.getmetrics()
    d.text((160, (150 - asc - desc) / 2), text, font=f, fill=INK)
    return with_shadow(img, blur=6)


def hand_cursor(size=150):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size / 100
    finger = [(40, 8), (52, 8), (52, 45), (80, 52), (86, 60), (82, 92), (36, 92), (18, 62), (24, 56), (40, 66)]
    d.polygon([(x * s, y * s) for x, y in finger], fill=WHITE + (255,), outline=INK + (255,), width=5)
    d.ellipse([40 * s, 2 * s, 52 * s, 14 * s], fill=WHITE + (255,), outline=INK + (255,), width=5)
    return with_shadow(img, blur=4, alpha=0.3, offset=(5, 7))


def phone_frame(screen):
    """Phone mockup around an RGBA screen image (520x940)."""
    w, h = screen.width + 40, screen.height + 120
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=60, fill=INK + (255,))
    img.alpha_composite(screen, (20, 60))
    d.rounded_rectangle([w / 2 - 60, 22, w / 2 + 60, 38], radius=8, fill=(70, 70, 70, 255))
    return with_shadow(img)


FEED_COLS = [(255, 190, 180), (150, 190, 235), (190, 225, 205), (255, 222, 120), (220, 200, 240), (250, 250, 250)]


def feed_screen(offset, show_me):
    sw, sh = 520, 940
    scr = Image.new("RGBA", (sw, sh), (245, 245, 245, 255))
    d = ImageDraw.Draw(scr)
    ch = 520  # card pitch
    first = int(offset // ch) - 1
    for k in range(first, first + 4):
        y = k * ch - offset + 20
        is_me = show_me and k == STOP_CARD
        col = FEED_COLS[k % len(FEED_COLS)]
        d.rounded_rectangle([18, y, sw - 18, y + ch - 30], radius=26, fill=(INK if is_me else col) + (255,))
        if is_me:
            hd = STK["senyum"][1]
            hs = hd.resize((int(hd.width * 0.42), int(hd.height * 0.42)), Image.BILINEAR)
            comp_clip(scr, hs, int(sw / 2 - hs.width / 2), int(y + 10))
            d.ellipse([sw / 2 - 50, y + 190, sw / 2 + 50, y + 290], fill=(255, 255, 255, 200))
            d.polygon([(sw / 2 - 16, y + 215), (sw / 2 - 16, y + 265), (sw / 2 + 26, y + 240)], fill=RED + (255,))
        else:
            d.rounded_rectangle([40, y + 30, 160, y + 60], radius=12, fill=(255, 255, 255, 160))
            d.rounded_rectangle([40, y + ch - 110, sw - 120, y + ch - 80], radius=12, fill=(255, 255, 255, 160))
    return scr


STOP_CARD = 12


def bar_chart(prog, labels, vals, cols, w=520, h=420, title=None):
    img = card(w, h)
    d = ImageDraw.Draw(img)
    if title:
        d.text((22, 14), title, font=F_TYPE(32), fill=INK)
    base = h - 70
    n = len(vals)
    bw = (w - 60) / n * 0.62
    for i, (lb, v, c) in enumerate(zip(labels, vals, cols)):
        x = 30 + (w - 60) / n * (i + 0.5)
        bh = (base - 80) * v * ease_out(prog * 1.3 - i * 0.15)
        d.rectangle([x - bw / 2, base - bh, x + bw / 2, base], fill=c, outline=INK, width=4)
        f = F_ANTON(40)
        d.text((x - f.getlength(lb) / 2, base + 8), lb, font=f, fill=INK)
    d.line([(20, base), (w - 20, base)], fill=INK, width=4)
    return with_shadow(img)


def reach_chart(prog):
    w, h = 620, 470
    img = card(w, h)
    d = ImageDraw.Draw(img)
    d.text((24, 16), "REACH ORGANIK", font=F_TYPE(36), fill=INK)
    for gy in range(110, h - 20, 60):
        d.line([(20, gy), (w - 20, gy)], fill=(200, 205, 215), width=2)
    pts = [(40, 420), (130, 405), (220, 390), (300, 350), (380, 300), (450, 220), (520, 140), (575, 75)]
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
        d.line(seg, fill=TEAL, width=14, joint="curve")
        (xa, ya), (xb, yb) = seg[-2], seg[-1]
        ang = math.atan2(yb - ya, xb - xa)
        L = 34
        d.polygon([(xb + L * 0.6 * math.cos(ang), yb + L * 0.6 * math.sin(ang)),
                   (xb + L * math.cos(ang + 2.5), yb + L * math.sin(ang + 2.5)),
                   (xb + L * math.cos(ang - 2.5), yb + L * math.sin(ang - 2.5))], fill=TEAL)
    return with_shadow(img)


def scribble_arrow(canvas, t, t0, p0, p1, col=INK, dur=0.4, width=9, bend=60):
    if t < t0:
        return
    k = ease_out((t - t0) / dur)
    (x0, y0), (x1, y1) = p0, p1
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    nx, ny = -(y1 - y0), (x1 - x0)
    L = math.hypot(nx, ny) or 1
    cx, cy = mx + nx / L * bend, my + ny / L * bend
    pts = []
    for i in range(31):
        u = i / 30 * k
        pts.append(((1 - u) ** 2 * x0 + 2 * (1 - u) * u * cx + u * u * x1,
                    (1 - u) ** 2 * y0 + 2 * (1 - u) * u * cy + u * u * y1))
    d = ImageDraw.Draw(canvas)
    d.line(pts, fill=col + (255,), width=width, joint="curve")
    if k > 0.98:
        (xa, ya), (xb, yb) = pts[-3], pts[-1]
        ang = math.atan2(yb - ya, xb - xa)
        for s in (2.6, -2.6):
            d.line([(xb, yb), (xb + 36 * math.cos(ang + s), yb + 36 * math.sin(ang + s))], fill=col + (255,), width=width)


def underline_marker(canvas, t, t0, x0, x1, y, col=RED, dur=0.35, width=12):
    if t < t0:
        return
    k = ease_out((t - t0) / dur)
    pts = [(x0 + (x1 - x0) * i / 29 * k, y + 6 * math.sin(i / 29 * k * 9)) for i in range(30)]
    ImageDraw.Draw(canvas).line(pts, fill=col + (255,), width=width, joint="curve")


def circle_marker(canvas, t, t0, cx, cy, rx, ry, col=RED, dur=0.5):
    if t < t0:
        return
    k = ease_out((t - t0) / dur)
    pts = []
    for i in range(80):
        a = -1.9 + i / 79 * 2 * math.pi * 1.08 * k
        r = 1 + 0.04 * math.sin(a * 3)
        pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
    ImageDraw.Draw(canvas).line(pts, fill=col + (255,), width=9, joint="curve")


def burst(canvas, t, t0, cx, cy, col=INK, n=8, r0=70, r1=120, dur=0.35):
    if t < t0 or t > t0 + dur + 0.15:
        return
    k = ease_out((t - t0) / dur)
    a = 1 - clamp((t - t0 - dur) / 0.15)
    d = ImageDraw.Draw(canvas)
    for i in range(n):
        ang = i / n * 2 * math.pi + 0.3
        ra, rb = r0 + (r1 - r0) * k * 0.4, r0 + (r1 - r0) * k
        d.line([(cx + ra * math.cos(ang), cy + ra * math.sin(ang)), (cx + rb * math.cos(ang), cy + rb * math.sin(ang))],
               fill=col + (int(255 * a),), width=8)


def rays(canvas, t, cx, cy, alpha=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    R = 2400
    n = 18
    off = t * 0.12
    for i in range(n):
        a0 = off + i / n * 2 * math.pi
        a1 = a0 + math.pi / n
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)), (cx + R * math.cos(a1), cy + R * math.sin(a1))],
                  fill=YELLOW + (int(150 * alpha),))
    canvas.alpha_composite(lay)


# ---------------------------------------------------------------- static assets
A = {
    "k_tips": kicker("TIPS BISNES  #01"),
    "h_kenapa": big("KENAPA VIDEO?", 170, INK, YELLOW),
    "play": play_icon(240),
    "play_s": play_icon(130, (40, 40, 40)),
    "k_trafik": kicker("TRAFIK INTERNET DUNIA"),
    "h_video": big("= VIDEO", 130, WHITE, RED),
    "src": with_shadow(label("*Anggaran Cisco VNI", F_TYPE(30), INK, WHITE, padx=14, pady=8), blur=4, alpha=0.2),
    "k_scroll": kicker("ORANG SCROLL LAJU..."),
    "stop": stamp("STOP!", 170),
    "h_percaya": headline("Video bina kepercayaan", 78, hl="kepercayaan"),
    "chip_eye": icon_chip(eye_icon(), "NAMPAK MUKA", WHITE),
    "chip_ear": icon_chip(speaker_icon(), "DENGAR SUARA", WHITE),
    "chip_heart": icon_chip(heart_icon(), "RASA KENAL", (255, 230, 225)),
    "quote": None,
    "k_platform": kicker("ALGORITMA SUKA VIDEO"),
    "chips_p": [with_shadow(label(s, F_ANTON(78), fg, bg, padx=26, pady=6), blur=6)
                for s, fg, bg in [("TikTok", WHITE, INK), ("Reels", WHITE, (200, 60, 140)), ("Shorts", WHITE, RED)]],
    "percuma": stamp("PERCUMA!", 130, TEAL),
    "h_hasil": big("HASILNYA?", 160, INK, YELLOW),
    "steps": [with_shadow(label(s, F_ANTON(86), fg, bg, padx=34, pady=10), blur=8)
              for s, fg, bg in [("LEBIH RAMAI NAMPAK", INK, WHITE), ("LEBIH RAMAI PERCAYA", INK, YELLOW),
                                ("LEBIH BANYAK JUALAN", WHITE, RED)]],
    "h_jangan": headline("Jangan tunggu lagi.", 92, hl="tunggu"),
    "hand": hand_cursor(150),
}


def quote_card():
    w, h = 900, 330
    img = card(w, h, WHITE)
    d = ImageDraw.Draw(img)
    d.text((26, -30), "“", font=F_SERIF(220), fill=RED)
    f = F_SERIF(64)
    d.text((140, 50), "Orang beli dari orang", font=f, fill=INK)
    line2 = "yang mereka "
    d.text((140, 140), line2, font=f, fill=INK)
    x = 140 + f.getlength(line2)
    d.rectangle([x - 6, 160, x + f.getlength("percaya.") + 6, 225], fill=YELLOW)
    d.text((x, 140), "percaya.", font=f, fill=INK)
    return with_shadow(img)


A["quote"] = quote_card()


def cta_card():
    w, h = 940, 420
    img = card(w, h, WHITE, radius=30)
    d = ImageDraw.Draw(img)
    f1, f2 = F_ANTON(130), F_ANTON(130)
    s1 = "MULA BUAT VIDEO"
    d.text(((w - f1.getlength(s1)) / 2, 30), s1, font=f1, fill=INK)
    s2 = "HARI INI."
    x2 = (w - f2.getlength(s2)) / 2
    d.rectangle([x2 - 16, 215, x2 + f2.getlength(s2) + 16, 380], fill=RED)
    d.text((x2, 200), s2, font=f2, fill=WHITE)
    return with_shadow(img, blur=12)


def follow_btn():
    f = F_ANTON(64)
    s = "FOLLOW UNTUK TIPS BISNES"
    w, h = int(f.getlength(s)) + 170, 130
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=65, fill=YELLOW + (255,), outline=INK + (255,), width=6)
    d.ellipse([22, 22, 108, 108], fill=INK + (255,))
    d.polygon([(52, 42), (52, 88), (90, 65)], fill=YELLOW + (255,))
    asc, desc = f.getmetrics()
    d.text((130, (h - asc - desc) / 2), s, font=f, fill=INK)
    return with_shadow(img, blur=8)


A["cta"] = cta_card()
A["follow"] = follow_btn()
A["save"] = with_shadow(label("SIMPAN  •  KONGSI  •  KOMEN \"VIDEO\"", F_TYPE(38), WHITE, INK, padx=24, pady=12),
                        blur=6, alpha=0.3)


# ---------------------------------------------------------------- kinetic captions
# (start, end, text); words in CAPS get the yellow marker
CAPS = [
    (0.45, 2.1, "Tahu tak?"),
    (2.1, 4.8, "Video ialah senjata PALING KUAT untuk market bisnes anda."),
    (5.25, 7.9, "Lebih 80% trafik internet sekarang..."),
    (7.9, 10.75, "...adalah VIDEO."),
    (11.25, 13.2, "Orang scroll laju..."),
    (13.2, 15.75, "tapi video buat mereka BERHENTI."),
    (16.25, 18.3, "Video bina KEPERCAYAAN."),
    (18.3, 21.1, "Pelanggan nampak muka anda, dengar suara anda,"),
    (21.1, 22.5, "mereka rasa KENAL."),
    (22.5, 24.15, "Orang beli dari orang yang mereka PERCAYA."),
    (24.65, 27.2, "TikTok, Reels & Shorts tolak video anda lebih jauh"),
    (27.2, 29.75, "reach organik — PERCUMA."),
    (30.25, 31.9, "Hasilnya?"),
    (31.9, 34.75, "Lebih ramai NAMPAK, lebih ramai PERCAYA, lebih banyak JUALAN."),
    (35.25, 37.1, "Jadi, jangan tunggu lagi."),
    (37.1, 39.9, "Mula buat video untuk bisnes anda HARI INI."),
]


def cap_words(s, e, text):
    """Word reveal times proportional to word length, finishing at 70% of the line."""
    words = text.split()
    L = [len(w_) + 2 for w_ in words]
    span = (e - s) * 0.7
    acc, times = 0, []
    for l in L:
        times.append(s + span * acc / sum(L))
        acc += l
    return words, times


CAP_DATA = [(s, e, *cap_words(s, e, txt)) for s, e, txt in CAPS]


def is_key(w_):
    core = w_.strip(".,?!—…")
    return len(core) > 1 and core.isupper() or core == "80%"


def draw_caption(canvas, t, y_center=1600):
    for s, e, words, times in CAP_DATA:
        if not (s - 0.02 <= t < e):
            continue
        f = F_CAP(64)
        maxw = 900
        space = f.getlength(" ")
        lines, cur, cw = [], [], 0
        for w_ in words:
            wl = f.getlength(w_)
            if cur and cw + space + wl > maxw:
                lines.append(cur)
                cur, cw = [], 0
            cur.append(w_)
            cw += (space if cw else 0) + wl
        lines.append(cur)
        asc, desc = f.getmetrics()
        lh = asc + desc + 14
        widths = [sum(f.getlength(w_) for w_ in l) + space * (len(l) - 1) for l in lines]
        bw, bh = int(max(widths)) + 70, lh * len(lines) + 36
        strip = Image.new("RGBA", (bw, bh), WHITE + (255,))
        d = ImageDraw.Draw(strip)
        idx = 0
        active = max([i for i, tt in enumerate(times) if tt <= t], default=-1)
        for li, l in enumerate(lines):
            x = (bw - widths[li]) / 2
            y = 18 + li * lh
            for w_ in l:
                wl = f.getlength(w_)
                tt = times[idx]
                if t >= tt:
                    k = ease_back((t - tt) / 0.18)
                    yy = y + 14 * (1 - k)
                    key = is_key(w_)
                    if key:
                        d.rectangle([x - 6, y + 6, x + wl + 6, y + lh - 8], fill=YELLOW)
                    col = RED if idx == active and not key else INK
                    d.text((x, yy), w_, font=f, fill=col)
                x += wl + space
                idx += 1
        spr = with_shadow(strip, blur=6, alpha=0.3)
        k = ease_out((t - s + 0.02) / 0.2)
        out = clamp((e - t) / 0.12)
        place(canvas, spr, W / 2, y_center + 30 * (1 - k), rot=-1.0, alpha=k * out)


# ---------------------------------------------------------------- camera (zoom punches)
CUTS = [5.0, 11.0, 16.0, 24.4, 30.0, 35.0]
PUNCHES = [2.6, 8.0, 13.55, 21.1, 27.3, 34.0, 37.1]
FOCUS = [(0.0, (540, 900)), (5.0, (540, 700)), (11.0, (540, 900)), (16.0, (540, 900)), (24.4, (540, 900)),
         (30.0, (540, 800)), (35.0, (540, 900))]


def scene_start(t):
    return max([0.0] + [c for c in CUTS if c <= t])


def camera(t):
    s0 = scene_start(t)
    nxt = [c for c in CUTS if c > t]
    s1 = nxt[0] if nxt else DUR
    push = 1.0 + 0.06 * ease_inout((t - s0) / (s1 - s0))
    if s0 == 16.0:
        push = 1.0 + 0.08 * ease_inout((t - s0) / (s1 - s0))
    p = 0.0
    shake = (0.0, 0.0)
    for pt in PUNCHES:
        dt = t - pt
        if 0 <= dt < 0.6:
            env = (dt / 0.06 if dt < 0.06 else math.exp(-(dt - 0.06) * 7))
            p += 0.08 * env
            shake = (8 * env * math.sin(dt * 70), 6 * env * math.cos(dt * 55))
    focus = [f for st, f in FOCUS if st <= t][-1]
    return push * (1 + p), focus, shake


def apply_camera(arr, t):
    z, (fx, fy), (sx, sy) = camera(t)
    if abs(z - 1) < 1e-4 and sx == 0:
        return arr
    M = np.float32([[z, 0, fx - z * fx + sx], [0, z, fy - z * fy + sy]])
    return cv2.warpAffine(arr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


# ---------------------------------------------------------------- scenes (world layer, zoomed by camera)
def world(t):
    s0 = scene_start(t)
    bg = {0.0: BG_CREAM, 5.0: BG_S2, 11.0: BG_S3, 16.0: BG_S4, 24.4: BG_S5, 30.0: BG_S6, 35.0: BG_S7}[s0]
    c = Image.fromarray(bg).convert("RGBA")

    if s0 == 0.0:  # HOOK
        draw_full(c, t, "sinis", 0.05, 380)
        pop(c, A["play"], t, 2.6, 880, 640, rot=10)
        burst(c, t, 2.6, 880, 640, RED, r0=130, r1=200)
        scribble_arrow(c, t, 3.0, (760, 820), (640, 1000), RED, bend=-50)
    elif s0 == 5.0:  # 80% traffic
        draw_head(c, t, "terkejut", 790, 1180, 0.68, 5.1, rot=5)
        doodle(c, t, 5.45, "!!", 1000, 900, 150, RED, rot=12)
        prog = ease_out((t - 5.4) / 2.3)
        if t >= 5.3:
            num = int(round(82 * prog))
            spr = big(f"{num}%", 330, INK, YELLOW)
            place(c, spr, 400, 520, rot=-3, scale=ease_back((t - 5.3) / 0.35))
        pop(c, A["k_trafik"], t, 5.6, 380, 190, rot=-2)
        pop(c, A["h_video"], t, 7.95, 420, 830, rot=3)
        if t >= 6.2:
            place(c, bar_chart(clamp((t - 6.2) / 1.6), ["VIDEO", "LAIN"], [0.82, 0.18], [RED, (200, 200, 200)],
                               w=420, h=420, title="TRAFIK %"), 270, 1160, rot=-4, alpha=clamp((t - 6.2) / 0.2))
        pop(c, A["src"], t, 6.6, 300, 1420, rot=-2)
    elif s0 == 11.0:  # scroll stop
        # feed scrolls fast, decelerates and stops on "me" at 13.4
        stop_off = STOP_CARD * 520
        u = clamp((t - 11.0) / 2.45)
        off = stop_off * (1 - (1 - u) ** 2.2)
        spr = phone_frame(feed_screen(off, True))
        place(c, spr, 540, 860, rot=-2 + 1.5 * math.sin(t * 2))
        if t < 13.3:
            d = ImageDraw.Draw(c)
            for j in range(6):  # speed lines
                y = 300 + ((j * 230 + t * 2600) % 1200)
                d.line([(170, y), (170, y + 140)], fill=INK + (200,), width=8)
                d.line([(910, y + 80), (910, y + 220)], fill=INK + (200,), width=8)
        pop(c, A["k_scroll"], t, 11.2, 330, 220, rot=-3)
        pop(c, ref("menguap", 380, "bosan...", 2), t, 11.5, 800, 1300, rot=7, t1=13.3)
        if t >= 13.55:
            kk = clamp((t - 13.55) / 0.14)
            place(c, A["stop"], 790, 560, scale=2.0 - ease_out(kk), rot=-12, alpha=kk)
        pop(c, A["hand"], t, 13.8, 760, 1180, rot=-10)
    elif s0 == 16.0:  # trust
        draw_head(c, t, "senyum", 540, 1080, 0.95, 16.1, rot=-2, t1=18.3)
        sparkle(c, t, 16.5, 870, 760, 70, t1=18.3)
        sparkle(c, t, 16.75, 220, 900, 50, t1=18.3)
        sparkle(c, t, 16.95, 800, 1000, 36, t1=18.3)
        pop(c, A["h_percaya"], t, 16.2, 540, 190, rot=-1.5, t1=22.3)
        pop(c, ref("selfie_peace", 470, seed=3), t, 18.45, 330, 540, rot=-5, t1=22.3)
        pop(c, ref("gitar", 470, seed=4), t, 19.75, 780, 930, rot=4, t1=22.3)
        pop(c, ref("cafe_ketawa", 440, seed=5), t, 21.1, 320, 1250, rot=-3, t1=22.3)
        pop(c, A["chip_eye"], t, 18.65, 360, 790, rot=3, t1=22.3, scale=0.8)
        pop(c, A["chip_ear"], t, 19.95, 740, 1180, rot=-2, t1=22.3, scale=0.8)
        pop(c, A["chip_heart"], t, 21.3, 370, 1460, rot=2, t1=22.3, scale=0.8)
        pop(c, A["quote"], t, 22.5, 540, 330, rot=-2)
        circle_marker(c, t, 23.2, 700, 400, 190, 60)
        pop(c, ref("cafe_ketawa", 640, seed=6), t, 22.6, 540, 900, rot=2)
    elif s0 == 24.4:  # algorithm reach
        draw_head(c, t, "asal", 800, 1330, 0.58, 24.5, rot=-4)
        for j, (tt, x) in enumerate(zip([24.65, 25.15, 25.65], [210, 520, 840])):
            pop(c, A["chips_p"][j], t, tt, x, 230, rot=[-4, 2, -3][j])
        pop(c, A["k_platform"], t, 24.9, 540, 360, rot=1)
        if t >= 25.8:
            place(c, reach_chart(ease_out((t - 25.9) / 1.7)), 390, 760, rot=-2, alpha=clamp((t - 25.8) / 0.2))
        if t >= 27.3:
            kk = clamp((t - 27.3) / 0.14)
            place(c, A["percuma"], 470, 1110, scale=1.9 - 0.9 * ease_out(kk), rot=-8, alpha=kk)
    elif s0 == 30.0:  # results
        pop(c, A["h_hasil"], t, 30.25, 540, 230, rot=-2)
        for j, (tt, y) in enumerate(zip([31.9, 32.85, 33.95], [480, 680, 880])):
            slide(c, A["steps"][j], t, tt, 540 + [-40, 20, -10][j], y, rot=[-2, 1.5, -1][j], dx=-500)
        scribble_arrow(c, t, 32.6, (930, 470), (950, 650), INK, bend=-40, width=7)
        scribble_arrow(c, t, 33.6, (950, 690), (940, 860), INK, bend=-40, width=7)
        draw_head(c, t, "fikir", 790, 1300, 0.5, 30.4, rot=5, t1=33.75)
        doodle(c, t, 30.7, "?", 1000, 1010, 150, RED, rot=12, t1=33.75)
        doodle(c, t, 31.0, "?", 590, 1060, 100, INK, rot=-10, t1=33.75)
        pop(c, ref("thumbs_up", 360, "Laku!", 8), t, 33.95, 790, 1250, rot=-5)
        if t >= 33.95:
            place(c, bar_chart(clamp((t - 33.95) / 0.9), ["J", "F", "M", "A"], [0.25, 0.45, 0.7, 0.95],
                               [YELLOW, YELLOW, YELLOW, RED], w=380, h=380, title="JUALAN"),
                  250, 1230, rot=-4, alpha=clamp((t - 33.95) / 0.2))
    else:  # CTA
        rays(c, t, 540, 1100, alpha=clamp((t - 35.0) / 0.5))
        draw_full(c, t, "tunjuk", 35.0, 560, scale=0.92)
        pop(c, ref("stres", 400, "takut nak mula?", 9), t, 35.4, 290, 560, rot=-6, t1=36.95)
        pop(c, ref("laptop_kerja", 400, "terus buat!", 10), t, 36.1, 790, 600, rot=5, t1=36.95)
    return c


def hud(c, t):
    """Unzoomed overlay layer: headlines & CTA that should stay steady."""
    if t < 5.0:
        pop(c, A["k_tips"], t, 0.25, 280, 140, rot=-3)
        pop(c, A["h_kenapa"], t, 0.7, 540, 330, rot=-2)
        underline_marker(c, t, 2.6, 430, 960, 455)
    if t >= 35.0:
        pop(c, A["h_jangan"], t, 35.3, 540, 180, rot=-1.5, t1=37.0)
        pop(c, A["cta"], t, 37.1, 540, 330, rot=-1.5)
        if t >= 37.7:
            pulse = 1 + 0.04 * max(0.0, math.sin((t - 37.7) * 7))
            pop(c, A["follow"], t, 37.7, 540, 640, scale=pulse)
        if t >= 38.2:
            # hand slides in and taps the button
            u = ease_out((t - 38.2) / 0.4)
            tap = 1 - 0.12 * max(0.0, math.sin(clamp((t - 38.65) / 0.25) * math.pi))
            place(c, A["hand"], 900 + 200 * (1 - u), 720 + 120 * (1 - u), scale=tap, rot=-15, alpha=u)
            if t >= 38.75:
                r = (t - 38.75) * 260
                a = int(255 * clamp(1 - (t - 38.75) / 0.6))
                ImageDraw.Draw(c).ellipse([830 - r, 650 - r * 0.6, 830 + r, 650 + r * 0.6], outline=INK + (a,), width=6)
        pop(c, A["save"], t, 38.4, 540, 790, rot=1)


# ---------------------------------------------------------------- paper-wipe transitions
WIPE_COLS = [YELLOW, INK, RED, BLUE, TEAL, YELLOW]
WIPE_DUR = 0.5
_wipes = {}


def wipe_sprite(j):
    if j not in _wipes:
        w = int(W * 1.4)
        img = Image.new("RGBA", (w, H + 200), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.polygon(torn_poly(40, 0, w - 40, H + 200, seed=40 + j, amp=22, step=18), fill=WIPE_COLS[j] + (255,))
        _wipes[j] = with_shadow(img, offset=(0, 0), blur=16, alpha=0.4, pad=30)
    return _wipes[j]


def draw_wipe(c, t):
    for j, ct in enumerate(CUTS):
        u = (t - (ct - WIPE_DUR / 2)) / WIPE_DUR
        if 0 <= u <= 1:
            spr = wipe_sprite(j)
            x = W / 2 + (W + spr.width / 2) * (1 - 2 * ease_inout(u))
            place(c, spr, x, H / 2, rot=-4)


# ---------------------------------------------------------------- frame
def frame(i):
    t = i / FPS
    wl = world(t)
    arr = apply_camera(np.asarray(wl.convert("RGB")), t).astype(np.float32)
    arr += GRAIN[i % len(GRAIN)][..., None] * 0.6
    c = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    hud(c, t)
    draw_caption(c, t, y_center=1640 if t < 35 else 1660)
    draw_wipe(c, t)
    rgb = np.asarray(c.convert("RGB"))
    if t < 0.25 or t > DUR - 0.35:
        f = clamp(t / 0.25) * clamp((DUR - t) / 0.35)
        rgb = (rgb.astype(np.float32) * f).astype(np.uint8)
    return rgb


def main():
    out = sys.stdout.buffer
    for i in range(N):
        out.write(frame(i).tobytes())
        if i % 100 == 0:
            print(f"frame {i}/{N}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        for ts in sys.argv[2:]:
            Image.fromarray(frame(int(float(ts) * FPS))).save(f"{WD}/preview_{ts}.jpg", quality=85)
    else:
        main()
