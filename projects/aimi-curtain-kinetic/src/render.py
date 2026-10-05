"""Kinetic-typography edit for Aimi Curtain (9:16, 1080x1920, 30fps).

Usage: python src/render.py [--still t1,t2,...]
  default : writes build/video.mp4 (video only; audio is mixed by render.sh)
  --still : writes build/still_<t>.png for quick layout checks
"""
import math
import os
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from timeline import *  # noqa: E402,F403

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = f"{ROOT}/assets/source"
FONTS = f"{ROOT}/assets/fonts"
BUILD = f"{ROOT}/build"
SW, SH = 720, 1280                      # source footage size
MARGIN = 90                             # horizontal safe margin


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    return 1 - (1 - clamp(x)) ** 3


def ease_in(x):
    return clamp(x) ** 3


def ease_back(x):
    x = clamp(x)
    c1 = 1.70158
    return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2


# ---------------------------------------------------------------- footage
class Reader:
    """Sequential ffmpeg decoder at the output frame rate."""

    def __init__(self, path, w=SW, h=SH):
        self.w, self.h = w, h
        self.p = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={FPS},scale={w}:{h}",
             "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.last = np.zeros((h, w, 3), np.uint8)

    def next(self):
        buf = self.p.stdout.read(self.w * self.h * 3)
        if len(buf) == self.w * self.h * 3:
            self.last = np.frombuffer(buf, np.uint8).reshape(self.h, self.w, 3)
        return self.last


def zoom_crop(img, z, ay, ax=0.5):
    h, w = img.shape[:2]
    cw, ch = w / z, h / z
    left, top = ax * (w - cw), ay * (h - ch)
    m = np.float32([[W / cw, 0, -left * W / cw], [0, H / ch, -top * H / ch]])
    return cv2.warpAffine(img, m, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def shot_index(t):
    for i in range(len(SHOTS) - 1):
        if SHOTS[i] <= t < SHOTS[i + 1]:
            return i
    return len(SHOTS) - 2


def talking_frame(raw, t):
    i = shot_index(t)
    z0, z1, ay = SHOT_ZOOM[i]
    p = (t - SHOTS[i]) / (SHOTS[i + 1] - SHOTS[i])
    return zoom_crop(raw, z0 + (z1 - z0) * ease_out(p) if i == 0 else z0 + (z1 - z0) * p, ay)


# ---------------------------------------------------------------- compositing
def blend(dst, spr, x, y, alpha=1.0, clip=None):
    """Alpha-blend RGBA sprite (numpy) onto RGB dst at (x, y). clip=(y0, y1) mask band."""
    if alpha <= 0:
        return
    x, y = int(round(x)), int(round(y))
    sh, sw = spr.shape[:2]
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + sw, W), min(y + sh, H)
    if clip:
        y0, y1 = max(y0, int(clip[0])), min(y1, int(clip[1]))
    if x1 <= x0 or y1 <= y0:
        return
    s = spr[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32)
    a = s[..., 3:4] / 255.0 * alpha
    d = dst[y0:y1, x0:x1].astype(np.float32)
    dst[y0:y1, x0:x1] = (d * (1 - a) + s[..., :3] * a).astype(np.uint8)


def font(name, size):
    return ImageFont.truetype(f"{FONTS}/{name}.woff", size)


HEAVY = "montserrat-latin-900-normal"
REG = "inter-latin-500-normal"


def text_sprite(text, fnt, color, spacing=0, shadow=True):
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    widths = [tmp.textlength(c, font=fnt) for c in text]
    tw = int(sum(widths) + spacing * (len(text) - 1))
    asc, desc = fnt.getmetrics()
    pad = 24
    img = Image.new("RGBA", (tw + pad * 2, asc + desc + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if spacing:
        x = pad
        for c, cw in zip(text, widths):
            d.text((x, pad), c, font=fnt, fill=color + (255,))
            x += cw + spacing
    else:
        d.text((pad, pad), text, font=fnt, fill=color + (255,))
    if shadow:
        a = img.split()[3].filter(ImageFilter.GaussianBlur(10))
        sh = Image.new("RGBA", img.size, BG + (0,))
        sh.putalpha(a.point(lambda v: int(v * 0.75)))
        sh.alpha_composite(img)
        img = sh
    return np.array(img), pad


def fit_size(texts, fname, base, max_w):
    size = base
    while size > 40:
        f = font(fname, size)
        if all(f.getlength(t) <= max_w for t in texts):
            return size
        size -= 2
    return size


def pill_sprite(text):
    f = font(REG, 38)
    t, pad = text_sprite(text, f, BG, spacing=5, shadow=False)
    th, tw = t.shape[:2]
    w, h = tw - pad * 2 + 56, 72
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=ACCENT + (255,))
    arr = np.array(img)
    asc, desc = f.getmetrics()
    blend_rgba(arr, t, 28 - pad, (h - asc - desc) // 2 - pad + 2)
    return arr


def blend_rgba(dst, src, x, y):
    """RGBA over RGBA (used only while building sprites)."""
    D = Image.fromarray(dst)
    D.alpha_composite(Image.fromarray(src), (max(x, 0), max(y, 0)))
    dst[:] = np.array(D)


# ---------------------------------------------------------------- build text blocks
def build_block(b):
    heavy = [t for t, s, _ in b["lines"] if s in ("H", "HA")]
    hsize = fit_size(heavy, HEAVY, 128, W - MARGIN * 2) if heavy else 0
    lines, y = [], b["y"]
    for text, style, d in b["lines"]:
        if style == "PILL":
            spr, pad = pill_sprite(text), 0
            h_vis = spr.shape[0]
        elif style == "S":
            spr, pad = text_sprite(text, font(REG, 60), TEXT)
            h_vis = 72
        else:
            spr, pad = text_sprite(text, font(HEAVY, hsize), ACCENT if style == "HA" else TEXT)
            h_vis = int(hsize * 1.08)
        lines.append(dict(spr=spr, pad=pad, y=y, h=h_vis, style=style, t0=b["start"] + d,
                          x=(W - spr.shape[1]) // 2))
        y += h_vis + (22 if style == "PILL" else 6)
    return dict(lines=lines, start=b["start"], end=b["end"], bottom=y)


BLOCKS = [build_block(b) for b in TEXT_BLOCKS]


def draw_block(frame, blk, t):
    if not (blk["start"] - 0.01 <= t <= blk["end"] + 0.35):
        return
    for i, ln in enumerate(blk["lines"]):
        if t < ln["t0"]:
            continue
        spr, pad, h = ln["spr"], ln["pad"], ln["h"]
        band = (ln["y"] - 10, ln["y"] + h + 14)            # mask window for the line
        p_in = ease_out((t - ln["t0"]) / 0.38)
        p_out = ease_in((t - blk["end"] - i * 0.04) / 0.28)
        dy = (1 - p_in) * (h + 20) - p_out * (h + 30)
        x = ln["x"]
        if ln["style"] == "HA":                           # accent pop
            sc = 1 + 0.10 * (1 - ease_back((t - ln["t0"]) / 0.45))
            if abs(sc - 1) > 0.003:
                spr = cv2.resize(spr, None, fx=sc, fy=sc, interpolation=cv2.INTER_LINEAR)
                x -= (spr.shape[1] - ln["spr"].shape[1]) // 2
                dy -= (spr.shape[0] - ln["spr"].shape[0]) // 2
        blend(frame, spr, x, ln["y"] - pad + dy, clip=band)
        if ln["style"] == "HA":                           # underline grows after landing
            g = ease_out((t - ln["t0"] - 0.30) / 0.4) * (1 - p_out)
            uw = int((ln["spr"].shape[1] - 2 * pad) * 0.42 * g)
            if uw > 2:
                uy = ln["y"] + h + 22
                frame[uy:uy + 8, W // 2 - uw // 2:W // 2 + uw // 2] = ACCENT


# ---------------------------------------------------------------- testimonials
def rounded(img, r):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, img.size[0] - 1, img.size[1] - 1), radius=r, fill=255)
    out = img.convert("RGBA")
    out.putalpha(m)
    return out


def build_testimonial(tm):
    im = Image.open(f"{SRC}/{tm['img']}").convert("RGB")
    sc = 2.0
    big = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    base = np.array(big)
    card = rounded(big, 36)
    sh = Image.new("RGBA", (card.width + 80, card.height + 80), (0, 0, 0, 0))
    sm = Image.new("L", sh.size, 0)
    sm.paste(card.split()[3].point(lambda v: int(v * 0.55)), (40, 52))
    sh.putalpha(sm.filter(ImageFilter.GaussianBlur(18)))
    return dict(tm, rgb=base, mask=np.array(card.split()[3]), shadow=np.array(sh), sc=sc,
                boxes=[tuple(int(v * sc) for v in b) for b in tm["boxes"]])


TESTI = [build_testimonial(tm) for tm in TESTIMONIALS]
TESTI_PILL = pill_sprite(TESTIMONIAL_LABEL)
CARD_Y = 1150


def draw_testimonial(frame, tm, t):
    if not (tm["start"] <= t <= tm["end"] + 0.35):
        return
    p_in = ease_back((t - tm["start"]) / 0.45)
    p_out = ease_in((t - tm["end"]) / 0.32)
    alpha = clamp((t - tm["start"]) / 0.2) * (1 - p_out)
    rgb = tm["rgb"].copy()
    # highlight-marker sweep (multiply with gold) over the customer's own words
    t_hl = tm["hl_at"]
    for (x0, y0, x1, y1) in tm["boxes"]:
        g = ease_out((t - t_hl) / 0.45)
        t_hl += 0.45
        if g <= 0:
            continue
        xe = int(x0 + (x1 - x0) * g)
        reg = rgb[y0:y1, x0:xe].astype(np.float32)
        tint = np.array(ACCENT, np.float32) / 255.0
        rgb[y0:y1, x0:xe] = (reg * (0.25 + 0.75 * tint)).astype(np.uint8)
    spr = np.dstack([rgb, tm["mask"]])
    ch, cw = spr.shape[:2]
    x = (W - cw) // 2
    y = CARD_Y + (1 - p_in) * 90 + p_out * 60
    blend(frame, tm["shadow"], x - 40, y - 40, alpha)
    blend(frame, spr, x, y, alpha)
    # label pill above the card (mask reveal)
    py = CARD_Y - TESTI_PILL.shape[0] - 28
    pin = ease_out((t - tm["start"] - 0.1) / 0.35)
    blend(frame, TESTI_PILL, (W - TESTI_PILL.shape[1]) // 2,
          py + (1 - pin) * 80 + p_out * 0, 1 - p_out, clip=(py - 4, py + TESTI_PILL.shape[0] + 4))


# ---------------------------------------------------------------- brand assets
def build_logo(size):
    im = Image.open(f"{SRC}/foto_langsir.jpg").convert("RGB")
    cx, cy, r = 829, 120, 92                      # logo circle on the supplied photo
    c = im.crop((cx - r, cy - r, cx + r, cy + r)).resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(m).ellipse((6, 6, size * 4 - 7, size * 4 - 7), fill=255)
    c = c.convert("RGBA")
    c.putalpha(m.resize((size, size), Image.LANCZOS))
    return np.array(c)


LOGO_SMALL = build_logo(124)
LOGO_BIG = build_logo(400)

# bottom legibility gradient
_g = np.zeros((H, 1), np.float32)
_g[900:] = np.linspace(0, 1, H - 900)[:, None] ** 1.4
GRAD = (_g * 0.82)[..., None]


def gradient_amount(t):
    a = 0.0
    for b in BLOCKS + [dict(start=tm["start"], end=tm["end"]) for tm in TESTI]:
        a = max(a, clamp((t - b["start"] + 0.15) / 0.3) * (1 - clamp((t - b["end"] - 0.1) / 0.4)))
    return a


def in_cutaway(t):
    for kind, s, e, off in CUTAWAYS:
        if s <= t < e:
            return kind, s, e, off
    return None


# ---------------------------------------------------------------- cutaways
PHOTO = np.array(Image.open(f"{SRC}/foto_langsir.jpg").convert("RGB"))


def photo_frame(p):
    # 960x1280 still -> crop/pan only (no fake camera move)
    z = 1.0                                  # pan ends on the brand logo printed on the photo
    ax = 0.45 + 0.55 * ease_out(p)
    h, w = PHOTO.shape[:2]
    ch = h / z
    cw = ch * W / H
    left, top = ax * (w - cw), 0.5 * (h - ch)
    m = np.float32([[W / cw, 0, -left * W / cw], [0, H / ch, -top * H / ch]])
    return cv2.warpAffine(PHOTO, m, (W, H), flags=cv2.INTER_CUBIC)


WIPE = 0.30


def wipe_mix(base, incoming, p, upward=True):
    """Accent-edged vertical mask wipe. p: 0 -> base, 1 -> incoming."""
    if p <= 0:
        return base
    if p >= 1:
        return incoming
    edge = int(H * (1 - ease_out(p)))
    out = base.copy()
    out[edge:] = incoming[edge:]
    out[max(edge - 14, 0):edge] = ACCENT
    return out


# ---------------------------------------------------------------- end card
def end_card(frozen, t):
    p = (t - DIALOGUE_END)
    bg = cv2.GaussianBlur(frozen, (0, 0), 22)
    dark = clamp(p / 0.35) * 0.86
    out = (bg * (1 - dark) + np.array(BG) * dark).astype(np.uint8)
    s = ease_back((p - 0.08) / 0.5)
    if s > 0.01:
        lg = cv2.resize(LOGO_BIG, None, fx=s, fy=s, interpolation=cv2.INTER_LINEAR)
        blend(out, lg, (W - lg.shape[1]) // 2, 520 + (400 - lg.shape[0]) // 2)
    y = 1010
    for i, ln in enumerate(END_BUILT):
        pi = ease_out((p - 0.35 - i * 0.25) / 0.4)
        if pi > 0:
            spr, pad, h = ln
            blend(out, spr, (W - spr.shape[1]) // 2, y - pad + (1 - pi) * (h + 20), clip=(y - 10, y + h + 14))
        y += ln[2] + 30
    g = ease_out((p - 0.9) / 0.5)
    uw = int(260 * g)
    if uw > 2:
        out[y + 10:y + 18, W // 2 - uw // 2:W // 2 + uw // 2] = ACCENT
    return out


def _end_lines():
    out = []
    hs = fit_size([t for t, s in END_LINES if s == "H"], HEAVY, 120, W - MARGIN * 2)
    for text, style in END_LINES:
        if style == "H":
            spr, pad = text_sprite(text, font(HEAVY, hs), TEXT, shadow=False)
            out.append((spr, pad, int(hs * 1.08)))
        else:
            ss = fit_size([text], REG, 52, W - MARGIN * 2)
            spr, pad = text_sprite(text, font(REG, ss), ACCENT, shadow=False)
            out.append((spr, pad, int(ss * 1.25)))
    return out


END_BUILT = _end_lines()


# ---------------------------------------------------------------- main loop
def compose(t, raw, broll_frames, state):
    if t >= DIALOGUE_END:
        return end_card(state["frozen"], t)
    frame = talking_frame(raw, t)
    state["frozen"] = frame
    # cutaways with wipe in / out
    for kind, s, e, off in CUTAWAYS:
        if s <= t < e + WIPE:
            p = (t - s) / (e - s)
            if kind == "broll":
                bi = min(int((t - s + off) * FPS), len(broll_frames) - 1)
                inc = zoom_crop(broll_frames[bi], 1.0 + 0.06 * p, 0.5)
            else:
                inc = photo_frame(clamp(p))
            if t < s + WIPE:
                frame = wipe_mix(frame, inc, (t - s) / WIPE)
            elif t < e:
                frame = inc
            else:
                frame = wipe_mix(inc, frame, (t - e) / WIPE)
    ga = gradient_amount(t)
    if ga > 0:
        frame = (frame * (1 - GRAD * ga) + np.array(BG, np.float32) * GRAD * ga).astype(np.uint8)
    if t >= BRAND_BUG_FROM and not in_cutaway(t):
        a = clamp((t - BRAND_BUG_FROM) / 0.4) * clamp((DIALOGUE_END - 0.2 - t) / 0.3)
        for kind, s, e, off in CUTAWAYS:            # fade around cutaways
            a *= clamp(abs(t - s) / 0.25) if t < s else clamp((t - e) / 0.4)
        blend(frame, LOGO_SMALL, W - 60 - LOGO_SMALL.shape[1], 80, 0.92 * a)
    for tm in TESTI:
        draw_testimonial(frame, tm, t)
    for blk in BLOCKS:
        draw_block(frame, blk, t)
    return frame


def main():
    stills = None
    if len(sys.argv) > 2 and sys.argv[1] == "--still":
        stills = [float(v) for v in sys.argv[2].split(",")]
    os.makedirs(BUILD, exist_ok=True)
    br = Reader(f"{SRC}/broll_curtain.mp4")
    broll = [br.next().copy() for _ in range(int(5.8 * FPS))]
    br.p.stdout.close()
    br.p.wait()
    rd = Reader(f"{SRC}/talking_head.mp4")
    n = int(round(DURATION * FPS))
    state = {}
    if stills:
        targets = {int(round(s * FPS)): s for s in stills}
        for i in range(max(targets) + 1):
            t = i / FPS
            raw = rd.next() if t < DIALOGUE_END else rd.last
            if i in targets:
                Image.fromarray(compose(t, raw, broll, state)).save(f"{BUILD}/still_{targets[i]:05.2f}.png")
            elif t < DIALOGUE_END:
                state["frozen"] = talking_frame(raw, t)
        return
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-pix_fmt", "yuv420p", f"{BUILD}/video.mp4"], stdin=subprocess.PIPE)
    for i in range(n):
        t = i / FPS
        raw = rd.next() if t < DIALOGUE_END else rd.last
        enc.stdin.write(compose(t, raw, broll, state).tobytes())
        if i % 150 == 0:
            print(f"frame {i}/{n}", file=sys.stderr, flush=True)
    enc.stdin.close()
    enc.wait()


if __name__ == "__main__":
    main()
