"""Style D — "Glam Beauty" picture render.

Usage: python render_video_glam.py <project_dir> <out.mp4> [--still t1,t2,...]
Soft-glow grade, drifting bokeh + twinkles, pink light leaks, frosted-glass cards
with letter-by-letter reveals (Cormorant Garamond + Great Vibes script), rose-gold
line-drawn frames, Montserrat captions, glowing script end card.
"""
import math
import os
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import cues_glam as C  # noqa: E402

P, OUT = sys.argv[1], sys.argv[2]
W, H, FPS = 1080, 1920, 30
NF = int(round(C.DURATION * FPS))

PLUM = (92, 28, 58)
ROSE = (178, 58, 104)   # deep rose: readable on the light glass
BLUSH = (255, 200, 218)
GOLD_TOP = (250, 222, 205)
GOLD_BOT = (196, 128, 112)
WHITE = (255, 255, 255)


def font(name, size, var=None):
    f = ImageFont.truetype(f"{P}/assets/fonts/{name}", size)
    if var:
        f.set_variation_by_name(var)
    return f


SERIF = lambda s: font("CormorantGaramond.ttf", s, "SemiBold")  # noqa: E731
SERIF_I = lambda s: font("CormorantGaramond-Italic.ttf", s, "SemiBold Italic")  # noqa: E731
SCRIPT = lambda s: font("GreatVibes-Regular.ttf", s)  # noqa: E731
SANS = lambda s, v="SemiBold": font("Montserrat.ttf", s, v)  # noqa: E731


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def e_out(x):
    return 1 - (1 - clamp(x)) ** 3


def e_inout(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def win(t, t0, t1, fin=0.35, fout=0.35):
    if t < t0 or t > t1:
        return 0.0
    return min(e_out((t - t0) / fin), e_out((t1 - t) / fout))


# ---------------------------------------------------------------- precomputed sprites
def soft_disc(r, hard=0.55):
    s = int(r * 2 + 4)
    yy, xx = np.mgrid[0:s, 0:s]
    d = np.sqrt((xx - s / 2) ** 2 + (yy - s / 2) ** 2) / r
    return np.clip((1 - d) / (1 - hard), 0, 1) ** 1.5


BOKEH_SPR = {r: soft_disc(r) for r in (10, 16, 24, 34, 48)}
rng = np.random.default_rng(21)
BOKEH = [dict(x=rng.uniform(0, W), y=rng.uniform(0, H), r=rng.choice(list(BOKEH_SPR)), sp=rng.uniform(18, 55),
              ph=rng.uniform(0, 6.28), a=rng.uniform(0.10, 0.32),
              col=np.array([255, 205, 220] if rng.random() < 0.6 else [255, 235, 210], np.float32) / 255) for _ in range(28)]
TWINKLE = [dict(x=rng.uniform(60, W - 60), y=rng.uniform(80, 900), ph=rng.uniform(0, 6.28), s=rng.uniform(14, 30),
                per=rng.uniform(1.6, 3.2)) for _ in range(12)]
LEAK = cv2.GaussianBlur(np.pad(np.ones((40, 40), np.float32), 40), (0, 0), 22)
LEAK = cv2.resize(LEAK / LEAK.max(), (1400, 1400))

yy, xx = np.mgrid[0:H, 0:W]
VIG = (1 - 0.16 * (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.45) / (H * 0.7)) ** 2))[..., None].astype(np.float32)


def add_sprite(img, spr, cx, cy, color, alpha):
    h, w = spr.shape
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if xa >= xb or ya >= yb:
        return
    s = spr[ya - y0:yb - y0, xa - x0:xb - x0][..., None] * alpha
    reg = img[ya:yb, xa:xb]
    img[ya:yb, xa:xb] = 1 - (1 - reg) * (1 - s * color)     # screen blend


# ---------------------------------------------------------------- camera + grade
def zoom_at(t):
    K = C.ZOOM_KEYS
    for a, b in zip(K, K[1:]):
        if a[0] <= t <= b[0]:
            u = e_inout((t - a[0]) / max(1e-6, b[0] - a[0]))
            return tuple(a[i] + (b[i] - a[i]) * u for i in (1, 2, 3))
    return K[-1][1:]


def leak_strength(t):
    s = 0.0
    for f0 in C.LEAK_FLASH:
        u = t - f0
        if -0.15 < u < 0.9:
            s = max(s, math.sin(math.pi * clamp((u + 0.15) / 1.05)) ** 2)
    return s


def grade(fr, t):
    s, fx, fy = zoom_at(t)
    if t >= C.SCENE_CUT and fy < 800:   # never interpolate framing across the footage cut
        fy = 900
    M = np.float32([[s, 0, fx - s * fx], [0, s, fy - s * fy]])
    img = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32) / 255
    cool = min(clamp((t - C.COOL[0]) / 0.6), 1.0 if t < C.COOL[1] else 0.0)
    # warm pink beauty tone + soft bloom
    tint = np.array([1.03, 0.99, 1.0], np.float32) * (1 - cool) + np.array([0.96, 0.98, 1.04], np.float32) * cool
    img = np.clip(img * tint, 0, 1)
    if cool:
        g = img.mean(axis=2, keepdims=True)
        img = img * (1 - 0.35 * cool) + g * 0.35 * cool
    small = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    bloom = cv2.resize(cv2.GaussianBlur(small, (0, 0), 6), (W, H))
    img = 1 - (1 - img) * (1 - 0.22 * bloom * (1 - 0.5 * cool))
    # drifting light leaks (always faint, strong on transitions)
    ls = 0.10 * (1 - 0.7 * cool) + 0.45 * leak_strength(t)
    for k, (col, ph) in enumerate((((1.0, 0.62, 0.72), 0.0), ((1.0, 0.80, 0.62), 2.1))):
        cx = (W * (0.0 if k == 0 else 1.0)) + 260 * math.sin(t * 0.35 + ph)
        cy = H * (0.18 if k == 0 else 0.62) + 200 * math.cos(t * 0.27 + ph)
        lf = leak_strength(t)
        cx += (W * 1.2 * lf * (1 if k == 0 else -1)) * 0.5
        add_sprite(img, LEAK, cx, cy, np.array(col, np.float32), ls)
    # bokeh drifting up
    speed = 1 - 0.6 * cool
    for b in BOKEH:
        y = (b["y"] - b["sp"] * t * speed) % (H + 200) - 100
        x = b["x"] + 30 * math.sin(t * 0.6 + b["ph"])
        a = b["a"] * (0.75 + 0.25 * math.sin(t * 1.3 + b["ph"])) * (1 - 0.5 * cool)
        add_sprite(img, BOKEH_SPR[b["r"]], x, y, b["col"], a)
    img *= VIG
    return np.clip(img * 255, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- overlay helpers
def sparkle(d, cx, cy, s, alpha, color=WHITE):
    if s < 1 or alpha <= 0:
        return
    k = s * 0.18
    d.polygon([(cx, cy - s), (cx + k, cy - k), (cx + s, cy), (cx + k, cy + k), (cx, cy + s), (cx - k, cy + k), (cx - s, cy), (cx - k, cy - k)],
              fill=color + (int(255 * alpha),))
    d.ellipse([cx - k, cy - k, cx + k, cy + k], fill=WHITE + (int(255 * alpha),))


def glass(canvas, box, radius=46, alpha=1.0):
    """frosted glass: blur what's behind, lift it towards white, thin bright edge."""
    x0, y0, x1, y1 = [int(v) for v in box]
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    if x1 - x0 < 10 or y1 - y0 < 10 or alpha <= 0.01:
        return
    m = 30
    X0, Y0, X1, Y1 = max(0, x0 - m), max(0, y0 - m), min(W, x1 + m), min(H, y1 + m)
    reg = np.array(canvas.crop((X0, Y0, X1, Y1)).convert("RGB")).astype(np.float32)
    reg = cv2.GaussianBlur(reg, (0, 0), 22)[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0]
    reg = reg * 0.62 + 255 * 0.38
    reg[..., 0] = np.minimum(255, reg[..., 0] + 6)
    g = Image.fromarray(reg.astype(np.uint8)).convert("RGBA")
    mask = Image.new("L", g.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, g.width - 1, g.height - 1], radius=radius, fill=int(240 * alpha))
    # shadow
    sh = Image.new("L", (g.width + 80, g.height + 80), 0)
    ImageDraw.Draw(sh).rounded_rectangle([40, 52, 40 + g.width, 52 + g.height], radius=radius, fill=int(70 * alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    canvas.alpha_composite(Image.merge("RGBA", (Image.new("L", sh.size, 60), Image.new("L", sh.size, 20),
                                                Image.new("L", sh.size, 40), sh)), (x0 - 40, y0 - 40))
    g.putalpha(mask)
    canvas.alpha_composite(g, (x0, y0))
    ImageDraw.Draw(canvas).rounded_rectangle([x0, y0, x1 - 1, y1 - 1], radius=radius,
                                             outline=(255, 255, 255, int(200 * alpha)), width=3)


def reveal_text(canvas, text, f, x, y, t, t0, fill, per=0.035, rise=18, anchor_center=True, alpha=1.0):
    """letter-by-letter fade + rise. (x, y) = centre (or left) of the baseline box top."""
    tw = f.getlength(text)
    x0 = x - tw / 2 if anchor_center else x
    d = ImageDraw.Draw(canvas)
    cx = x0
    for i, ch in enumerate(text):
        u = clamp((t - t0 - i * per) / 0.32)
        if u > 0:
            a = e_out(u) * alpha
            d.text((cx, y + rise * (1 - e_out(u))), ch, font=f, fill=fill + (int(255 * a),))
        cx += f.getlength(text[:i + 1]) - f.getlength(text[:i])


def gold_text(text, f, glow=True):
    """rose-gold gradient text with a soft pink glow (RGBA image)."""
    b = f.getbbox(text)
    pad = 40
    w, h = b[2] - b[0] + 2 * pad, b[3] - b[1] + 2 * pad
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).text((pad - b[0], pad - b[1]), text, font=f, fill=255)
    grad = np.linspace(0, 1, h)[:, None, None]
    col = (np.array(GOLD_TOP) * (1 - grad) + np.array(GOLD_BOT) * grad) * np.ones((1, w, 1))
    img = Image.fromarray(col.astype(np.uint8)).convert("RGBA")
    img.putalpha(m)
    if not glow:
        return img
    g = m.filter(ImageFilter.GaussianBlur(14))
    out = Image.merge("RGBA", (Image.new("L", (w, h), 255), Image.new("L", (w, h), 170), Image.new("L", (w, h), 200),
                               g.point(lambda v: int(v * 0.8))))
    out.alpha_composite(img)
    return out


def place(canvas, img, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    if alpha <= 0.01 or scale <= 0.01:
        return
    im = img
    if abs(scale - 1) > 1e-3:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if abs(rot) > 0.05:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        im = im.copy()
        im.putalpha(im.split()[-1].point(lambda v: int(v * alpha)))
    x, y = int(cx - im.width / 2), int(cy - im.height / 2)
    canvas.alpha_composite(im, (max(0, x), max(0, y)), (max(0, -x), max(0, -y)))


def line_frame(canvas, t, t0, t1, kind):
    a = win(t, t0, t1, 0.2, 0.4)
    if a <= 0:
        return
    k = e_inout((t - t0) / 1.1)
    if kind == "face":   # arch around the face: up the left side, over the top, down the right
        cx, cy, rx, ry, depth = 540, 560, 360, 380, 520
        pts = [(cx - rx, cy + depth * (1 - u)) for u in np.linspace(0, 1, 30)]
        pts += [(cx + rx * math.cos(th), cy + ry * math.sin(th)) for th in np.linspace(math.pi, 2 * math.pi, 80)]
        pts += [(cx + rx, cy + depth * u) for u in np.linspace(0, 1, 30)]
    else:                # oval around the held bottle (left side after the cut)
        cx, cy, rx, ry = 215, 1170, 200, 330
        pts = [(cx + rx * math.cos(th), cy + ry * math.sin(th)) for th in np.linspace(-1.9, -1.9 + 2 * math.pi * 1.02, 140)]
    n = max(2, int(len(pts) * k))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.line(pts[:n], fill=GOLD_TOP + (int(110 * a),), width=12, joint="curve")
    layer = layer.filter(ImageFilter.GaussianBlur(6))
    d = ImageDraw.Draw(layer)
    d.line(pts[:n], fill=(236, 178, 160, int(255 * a)), width=4, joint="curve")
    if k < 1:
        hx, hy = pts[n - 1]
        sparkle(d, hx, hy, 26, a)
    canvas.alpha_composite(layer)


def check_icon(size=40):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, size - 1, size - 1], fill=ROSE + (255,))
    d.line([(size * 0.27, size * 0.52), (size * 0.44, size * 0.68), (size * 0.74, size * 0.34)], fill=WHITE, width=max(3, size // 10), joint="curve")
    return im


BOTTLE = None


def bottle_sprite():
    b = Image.open(f"{P}/assets/bottle.png").convert("RGBA")
    b = b.resize((int(b.width * 0.62), int(b.height * 0.62)), Image.LANCZOS)
    a = b.split()[-1]
    pad = 50
    glow = Image.new("L", (b.width + 2 * pad, b.height + 2 * pad), 0)
    glow.paste(a, (pad, pad))
    glow = glow.filter(ImageFilter.GaussianBlur(24))
    out = Image.merge("RGBA", (Image.new("L", glow.size, 255), Image.new("L", glow.size, 190), Image.new("L", glow.size, 215),
                               glow.point(lambda v: int(v * 0.9))))
    out.alpha_composite(b, (pad, pad))
    return out


# ---------------------------------------------------------------- captions
def caption(canvas, t, cache):
    cur = None
    for i, (s, e, txt) in enumerate(C.CAPTIONS):
        nxt = C.CAPTIONS[i + 1][0] if i + 1 < len(C.CAPTIONS) else e
        if s <= t < (nxt if nxt - e < 0.3 else e):
            cur = (s, e, txt)
    if not cur:
        return
    s, e, txt = cur
    if txt not in cache:
        f = SANS(54, "SemiBold")
        words = txt.split(" ")
        cols = [WHITE] * len(words)
        low = [w.strip(",.?!").lower() for w in words]
        for hl in C.CAP_HL:
            hw = hl.lower().split()
            for i in range(len(words) - len(hw) + 1):
                if low[i:i + len(hw)] == hw:
                    for j in range(i, i + len(hw)):
                        cols[j] = BLUSH
        sp = f.getlength(" ")
        tw = int(sum(f.getlength(w) for w in words) + sp * (len(words) - 1))
        pad = 30
        im = Image.new("RGBA", (tw + 2 * pad, 110), (0, 0, 0, 0))
        m = Image.new("L", im.size, 0)
        dm = ImageDraw.Draw(m)
        d = ImageDraw.Draw(im)
        x = pad
        for w, c in zip(words, cols):
            dm.text((x, 22), w, font=f, fill=255)
            x += f.getlength(w) + sp
        shadow = m.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(min(255, v * 2.2) * 0.92))
        base = Image.merge("RGBA", (Image.new("L", im.size, 60), Image.new("L", im.size, 18), Image.new("L", im.size, 40), shadow))
        x = pad
        for w, c in zip(words, cols):
            d.text((x, 22), w, font=f, fill=c + (255,))
            x += f.getlength(w) + sp
        base.alpha_composite(im)
        assert base.width <= 1060, txt
        cache[txt] = base
    u = t - s
    fade = clamp((C.CAPTIONS[-1][1] + 0.3 - t) / 0.3) if txt == C.CAPTIONS[-1][2] else 1.0
    place(canvas, cache[txt], 540, 1540 + 16 * (1 - e_out(u / 0.25)), alpha=e_out(u / 0.2) * fade)


# ---------------------------------------------------------------- overlays
def overlays(canvas, t, cache):
    global BOTTLE
    if BOTTLE is None:
        BOTTLE = bottle_sprite()
    for t0, t1, kind in C.FRAMES:
        line_frame(canvas, t, t0, t1, kind)

    # glass title cards: serif line reveals, then the script word writes in
    for t0, t1, l1, l2, y, sd in C.CARDS:
        a = win(t, t0, t1, 0.3, 0.3)
        if a <= 0:
            continue
        f1, f2 = SERIF(76), SCRIPT(118)
        w = max(f1.getlength(l1), f2.getlength(l2)) + 130
        grow = e_out((t - t0) / 0.45)
        cw = w * (0.85 + 0.15 * grow)
        glass(canvas, (540 - cw / 2, y - 130, 540 + cw / 2, y + 140), alpha=a)
        reveal_text(canvas, l1, f1, 540, y - 105, t, t0 + 0.1, PLUM, alpha=a)
        reveal_text(canvas, l2, f2, 540, y - 20, t, t0 + sd, ROSE, per=0.05, rise=10, alpha=a)

    for t0, t1, l1, l2, y in C.PILLS:
        a = win(t, t0, t1, 0.3, 0.3)
        if a <= 0:
            continue
        f1, f2 = SERIF_I(64), SCRIPT(96)
        w = f1.getlength(l1) + f2.getlength(l2) + 120
        slide = 60 * (1 - e_out((t - t0) / 0.5))
        glass(canvas, (540 - w / 2 + slide, y - 62, 540 + w / 2 + slide, y + 62), radius=62, alpha=a)
        x0 = 540 - w / 2 + 50 + slide
        reveal_text(canvas, l1, f1, x0, y - 48, t, t0 + 0.1, PLUM, anchor_center=False, alpha=a)
        reveal_text(canvas, l2, f2, x0 + f1.getlength(l1) + 22, y - 72, t, t0 + 0.45, ROSE, per=0.05, anchor_center=False, alpha=a)

    # brand reveal after the cut
    a = win(t, *C.BRAND, fin=0.5, fout=0.35)
    if a:
        if "brand" not in cache:
            cache["brand"] = gold_text("Firea", SCRIPT(250))
        u = t - C.BRAND[0]
        place(canvas, cache["brand"], 540, 250, scale=0.9 + 0.1 * e_out(u / 0.8), alpha=a * e_out(u / 0.6))
        reveal_text(canvas, "C E L E S T E   M U S K", SANS(34, "Medium"), 540, 395, t, C.BRAND[0] + 0.5, WHITE, per=0.02, alpha=a)
        for k, (t0, txt) in enumerate(((C.CHIP1, "Kawal peluh"), (C.CHIP2, "Hilang terus bau badan"))):
            if t < t0:
                continue
            f = SANS(38, "SemiBold")
            w = f.getlength(txt) + 120
            q = e_out((t - t0) / 0.45)
            # chips stack on the right half, clear of the held bottle
            yk = 495 + k * 98
            xk = 1020 - w + 40 * (1 - q)
            glass(canvas, (xk, yk - 42, xk + w, yk + 42), radius=42, alpha=a * q)
            canvas.alpha_composite(check_icon(46), (int(xk + 22), int(yk - 23)))
            reveal_text(canvas, txt, f, xk + 84, yk - 24, t, t0 + 0.1, PLUM, per=0.02, anchor_center=False, alpha=a * q)

    # twinkles + sparkle bursts
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for tw in TWINKLE:
        v = math.sin(t * 2 * math.pi / tw["per"] + tw["ph"])
        if v > 0.6:
            sparkle(d, tw["x"], tw["y"], tw["s"] * (v - 0.6) / 0.4, 0.9 * (v - 0.6) / 0.4)
    for bt, (bx, by) in ((C.SCENE_CUT, (540, 260)), (C.END, (820, 520)), (C.CTA, (540, 760))):
        u = t - bt
        if 0 <= u < 0.9:
            for j in range(10):
                ang = j * 0.63 + bt
                r = 60 + 260 * e_out(u / 0.9)
                sparkle(d, bx + r * math.cos(ang), by + r * 0.7 * math.sin(ang), 22 * math.sin(math.pi * u / 0.9), 1 - u / 0.9,
                        (255, 220, 230) if j % 2 else WHITE)
    canvas.alpha_composite(layer)

    # end card
    if t >= C.END:
        u = t - C.END
        a = e_out(u / 0.5)
        glass(canvas, (70, 100, 700, 560), radius=54, alpha=a)
        reveal_text(canvas, "Pakai je", SERIF_I(70), 385, 125, t, C.END + 0.1, PLUM, alpha=a)
        if "end" not in cache:
            cache["end"] = gold_text("Firea", SCRIPT(210))
        place(canvas, cache["end"], 385, 315, scale=0.92 + 0.08 * e_out(u / 0.8), alpha=e_out((u - 0.25) / 0.6))
        reveal_text(canvas, "Celeste Musk  ·  Roll-on 50ml", SERIF(46), 385, 430, t, C.END + 0.6, PLUM, per=0.02, alpha=a)
        if t >= C.CLAIMS:
            q = e_out((t - C.CLAIMS) / 0.4)
            d = ImageDraw.Draw(canvas)
            for k, txt in enumerate(("0% Alkohol", "0% Paraben")):
                f = SANS(30, "Medium")
                w = f.getlength(txt) + 44
                x0 = 140 + k * 220
                d.rounded_rectangle([x0, 492, x0 + w, 538], radius=23, outline=ROSE + (int(255 * q),), width=2)
                d.text((x0 + 22, 498), txt, font=f, fill=PLUM + (int(255 * q),))
        place(canvas, BOTTLE, 870, 400, scale=0.72 * (0.85 + 0.15 * e_out(u / 0.6)), alpha=e_out((u - 0.15) / 0.5), rot=6)
        if t >= C.CTA:
            q = e_out((t - C.CTA) / 0.45)
            f = SANS(40, "SemiBold")
            w = f.getlength(C.CTA_TEXT + "  →") + 90
            x0, y0 = 540 - w / 2, 640 + 20 * (1 - q)
            pill = Image.new("RGBA", (int(w), 92), (0, 0, 0, 0))
            grad = np.linspace(0, 1, int(w))[None, :, None]
            col = np.array([224, 140, 160]) * (1 - grad) + np.array([200, 120, 108]) * grad
            pimg = Image.fromarray((col * np.ones((92, 1, 1))).astype(np.uint8)).convert("RGBA")
            pm = Image.new("L", pill.size, 0)
            ImageDraw.Draw(pm).rounded_rectangle([0, 0, pill.width - 1, 91], radius=46, fill=int(255 * q))
            pimg.putalpha(pm)
            # shimmer sweep
            sx = ((t - C.CTA) * 700) % (w + 400) - 200
            sh = Image.new("L", pill.size, 0)
            ImageDraw.Draw(sh).polygon([(sx, 0), (sx + 60, 0), (sx + 20, 92), (sx - 40, 92)], fill=int(110 * q))
            pimg.alpha_composite(Image.merge("RGBA", (Image.new("L", pill.size, 255),) * 3 + (Image.composite(sh, Image.new("L", pill.size, 0), pm),)))
            ImageDraw.Draw(pimg).text((w / 2, 46), C.CTA_TEXT + "  →", font=f, fill=WHITE + (int(255 * q),), anchor="mm")
            canvas.alpha_composite(pimg, (int(x0), int(y0)))


def frames_from_source():
    cmd = ["ffmpeg", "-v", "error", "-i", f"{P}/source/footage.mp4", "-vf", f"scale={W}:{H}:flags=lanczos",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    last = None
    while True:
        buf = proc.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        last = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        yield last
    while True:
        yield last


def render(stills=None):
    cache = {}
    src = frames_from_source()
    enc = None
    if stills is None:
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                                "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
    want = set(int(round(s * FPS)) for s in stills) if stills else None
    for n in range(NF):
        fr = next(src)
        t = n / FPS
        if want is not None and n not in want:
            continue
        canvas = Image.fromarray(grade(fr, t)).convert("RGBA")
        overlays(canvas, t, cache)
        caption(canvas, t, cache)
        out = np.array(canvas.convert("RGB"))
        if want is not None:
            Image.fromarray(out).save(f"{OUT}_{t:05.2f}.jpg", quality=88)
            if n >= max(want):
                break
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
