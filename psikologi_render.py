"""Episode — "7 Kebenaran Tentang Psychology" (~61.6 s, 1080x1920@30), countdown-list explainer.

Dark board with the yellow/red title bar (after the source infographic). MAN narrates from the
bottom of the frame (black & white cut-out with a white sticker outline, pose changing per point).
Each truth arrives as a card: number badge, cartoon icon, yellow headline, white sub-line, with a
7-dot progress bar. Timings follow the ElevenLabs VO (assets/vo_psikologi.mp3).

Usage: python3 psikologi_render.py <workdir> <out.mp4>   (workdir needs pose/*.jpg|_mask.png, icons.png)
"""
import math
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

WD, OUT = sys.argv[1], sys.argv[2]
import os

EP = os.environ.get("EP", "1")
CFG = {
    "1": dict(dur=61.7, icons="icons.png", hook_end=6.7, badge_t=4.1, badge_i=4, hook1="YANG RAMAI ORANG",
              hook2="TAK SUKA NAK MENGAKU", hook_chip="KITA SEMUA PERNAH KENA", star_i=4, star_txt="INI DIA!",
              cta1="MANA SATU", cta2="PALING KENA?", cta_chip="KOMEN NOMBOR DIA KAT BAWAH", ribbon=None),
    "2": dict(dur=58.1, icons="icons2.png", hook_end=6.3, badge_t=4.56, badge_i=6, hook1="7 LAGI KEBENARAN",
              hook2="YANG JARANG ORANG CAKAP", hook_chip="PALING DALAM", star_i=6, star_txt="PALING DALAM",
              cta1="SHARE PADA", cta2="SESEORANG", cta_chip="TENGOK BAHAGIAN 1 JUGA", ribbon="BAHAGIAN 2"),
}[EP]
W, H, FPS = 1080, 1920, 30
DUR = CFG["dur"]
N = int(DUR * FPS)

YELLOW = (255, 214, 0)
RED = (220, 30, 40)
WHITE = (255, 255, 255)
INK = (14, 14, 16)
FD = "/usr/share/fonts/opentype/inter/"
_fc = {}


def font(name, size):
    if (name, size) not in _fc:
        _fc[(name, size)] = ImageFont.truetype(FD + name + ".otf", size)
    return _fc[(name, size)]


F_BLACK = lambda s: font("Inter-Black", s)
F_XB = lambda s: font("Inter-ExtraBold", s)
F_B = lambda s: font("Inter-Bold", s)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_back(x):
    x = clamp(x)
    c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def place(canvas, s, cx, cy, scale=1.0, rot=0.0, alpha=1.0):
    if alpha <= 0.01 or scale <= 0.01:
        return
    if abs(scale - 1) > 1e-3:
        s = s.resize((max(1, int(s.width * scale)), max(1, int(s.height * scale))), Image.BILINEAR)
    if abs(rot) > 0.05:
        s = s.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        s = s.copy()
        s.putalpha(s.split()[3].point(lambda v: int(v * alpha)))
    canvas.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2))) if (
        0 <= int(cx - s.width / 2) and 0 <= int(cy - s.height / 2)
        and int(cx - s.width / 2) + s.width <= W and int(cy - s.height / 2) + s.height <= H) else clip_paste(
        canvas, s, int(cx - s.width / 2), int(cy - s.height / 2))


def clip_paste(canvas, s, x, y):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + s.width), min(H, y + s.height)
    if x1 <= x0 or y1 <= y0:
        return
    canvas.alpha_composite(s.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))


def text_sprite(text, f, fg, stroke=0, stroke_fill=INK, shadow=True):
    b = f.getbbox(text, stroke_width=stroke)
    w, h = b[2] - b[0] + 24, b[3] - b[1] + 24
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if shadow:
        d.text((12 - b[0] + 5, 12 - b[1] + 7), text, font=f, fill=(0, 0, 0, 160), stroke_width=stroke,
               stroke_fill=(0, 0, 0, 160))
    d.text((12 - b[0], 12 - b[1]), text, font=f, fill=fg, stroke_width=stroke, stroke_fill=stroke_fill)
    return im


def chip(text, f, fg, bg, padx=30, pady=18, radius=18):
    b = f.getbbox(text)
    w, h = b[2] - b[0] + 2 * padx, b[3] - b[1] + 2 * pady
    im = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 12, w + 8, h + 12), radius, fill=(0, 0, 0, 120))
    d.rounded_rectangle((4, 4, w + 4, h + 4), radius, fill=bg)
    d.text((4 + padx - b[0], 4 + pady - b[1]), text, font=f, fill=fg)
    return im


def wrap(text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if f.getlength(t) > maxw and cur:
            lines.append(cur)
            cur = w_
        else:
            cur = t
    lines.append(cur)
    return lines


# ---------------------------------------------------------------- background
def make_bg():
    rng = np.random.default_rng(3)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((x - W / 2) / W) ** 2 + ((y - H * 0.45) / H) ** 2)
    base = 38 - 30 * r
    tex = cv2.GaussianBlur(rng.normal(0, 1, (H // 8, W // 8)).astype(np.float32), (0, 0), 3)
    tex = cv2.resize(tex, (W, H)) * 6
    g = np.clip(base + tex, 6, 60)
    rgb = np.stack([g, g, g * 1.08], -1).astype(np.uint8)
    im = Image.fromarray(rgb).convert("RGBA")
    d = ImageDraw.Draw(im)
    for yy in range(0, H, 6):  # faint scanlines
        d.line((0, yy, W, yy), fill=(255, 255, 255, 5))
    return im


BG = make_bg()
GRAIN = [Image.fromarray(np.clip(128 + np.random.default_rng(i).normal(0, 10, (H // 2, W // 2)), 0, 255)
                         .astype(np.uint8)).resize((W, H)).convert("L") for i in range(4)]


def header_sprite():
    im = Image.new("RGBA", (980, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((14, 20, 980, 300), fill=(0, 0, 0, 120))
    d.rectangle((0, 6, 966, 286), fill=YELLOW)
    t1 = "7 KEBENARAN TENTANG"
    f1 = F_BLACK(76)
    d.text(((966 - f1.getlength(t1)) / 2, 34), t1, font=f1, fill=INK)
    t2 = "PSYCHOLOGY"
    f2 = F_BLACK(124)
    d.text(((966 - f2.getlength(t2)) / 2, 122), t2, font=f2, fill=RED, stroke_width=3, stroke_fill=(120, 0, 0))
    if CFG["ribbon"]:
        r = chip(CFG["ribbon"], F_BLACK(44), WHITE, RED).rotate(-6, expand=True, resample=Image.BICUBIC)
        big = Image.new("RGBA", (im.width + 40, im.height + 70), (0, 0, 0, 0))
        big.alpha_composite(im, (0, 0))
        big.alpha_composite(r, (big.width - r.width, big.height - r.height))
        im = big
    return im


HEADER = header_sprite()


# ---------------------------------------------------------------- narrator (B&W sticker cut-outs)
def bw_dramatic(rgb):
    g = (rgb[..., 0] * 0.30 + rgb[..., 1] * 0.59 + rgb[..., 2] * 0.11).astype(np.uint8)
    g = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8)).apply(g).astype(np.float32) / 255
    g = 0.5 + 0.5 * np.tanh(2.4 * (g - 0.52)) / math.tanh(1.2)
    g = np.clip((g - 0.04) / 0.98, 0, 1) * 255
    return np.repeat(g[..., None], 3, axis=2)


def colour_grade(rgb):
    """Gentle punch: local contrast on luminance, a touch more saturation, slight warmth."""
    lab = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2LAB)
    lab[..., 0] = cv2.createCLAHE(clipLimit=1.6, tileGridSize=(8, 8)).apply(lab[..., 0])
    out = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB).astype(np.float32)
    g = out.mean(axis=2, keepdims=True)
    out = g + (out - g) * 1.12
    out *= np.array([1.03, 1.0, 0.97], np.float32)
    return np.clip(out, 0, 255)


def narrator(name, target_w=660, max_h=700):
    im = np.asarray(Image.open(f"{WD}/pose/{name}.jpg").convert("RGB")).astype(np.float32)
    m = np.asarray(Image.open(f"{WD}/pose/{name}_mask.png").convert("L")).astype(np.float32) / 255
    m = np.clip((m - 0.3) / 0.4, 0, 1)
    b = (m > 0.5).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(b)
    if n > 2:
        m = m * (lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])))
    ys, xs = np.where(m > 0.5)
    y0, x0, x1 = ys.min(), xs.min(), xs.max()
    im, m = im[y0:, x0:x1 + 1], m[y0:, x0:x1 + 1]
    s = colour_grade(im)
    pad = 30
    m = cv2.copyMakeBorder(m, pad, 0, pad, pad, cv2.BORDER_CONSTANT, value=0)
    s = cv2.copyMakeBorder(s, pad, 0, pad, pad, cv2.BORDER_CONSTANT, value=0)
    k = target_w / s.shape[1]
    s = cv2.resize(s, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
    m = cv2.resize(m, None, fx=k, fy=k, interpolation=cv2.INTER_LINEAR)
    outline = cv2.dilate((m > 0.5).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
    outline = cv2.GaussianBlur(outline.astype(np.float32), (0, 0), 1.2)
    rgb = s * m[..., None] + 255 * (1 - m[..., None])
    a = np.clip(np.maximum(m, outline), 0, 1)
    spr = Image.fromarray(np.dstack([rgb, a * 255]).astype(np.uint8), "RGBA")
    sh = Image.new("RGBA", spr.size, (0, 0, 0, 0))
    sh.putalpha(spr.split()[3].point(lambda v: int(v * 0.5)).filter(ImageFilter.GaussianBlur(14)))
    out = Image.new("RGBA", (spr.width + 40, spr.height), (0, 0, 0, 0))
    out.alpha_composite(sh, (24, 18))
    out.alpha_composite(spr, (0, 0))
    return out.crop((0, 0, out.width, min(out.height, max_h)))


POSE = {n: narrator(n) for n in ["kejut", "teruja", "senyum", "garu", "tunjuk", "fikir", "sinis", "risau"]}


# ---------------------------------------------------------------- icons (cut from the sprite sheet)
def load_icons():
    from rembg import new_session, remove
    sh = Image.open(f"{WD}/" + CFG["icons"]).convert("RGB")
    cw, ch = sh.width / 4, sh.height / 2
    sess = new_session("u2net")
    out = []
    for i in range(8):
        c = sh.crop((int((i % 4) * cw), int((i // 4) * ch), int((i % 4 + 1) * cw), int((i // 4 + 1) * ch)))
        c = c.resize((c.width * 2, c.height * 2), Image.LANCZOS)
        cut = remove(c, session=sess)
        bb = cut.getbbox()
        out.append(cut.crop(bb))
    return out


ICONS = load_icons()

# ---------------------------------------------------------------- timeline (VO seconds)
POINTS = [  # (start, number-call time, headline, sub, sub_time, pose)
    (6.7, 6.84, "SEMAKIN SUSAH, SEMAKIN JUJUR", "Setiap sen hasil titik peluh", 12.2, "senyum"),
    (15.3, 15.48, "SEMAKIN KAYA, SEMAKIN BERKIRA", "Bukan semua... tapi ramai", 20.19, "garu"),
    (22.0, 22.21, "SEMAKIN PENDIAM, SEMAKIN BIJAK", "Dia banyak memerhati", 26.15, "fikir"),
    (30.1, 30.30, "SEMAKIN CANTIK, SEMAKIN SOMBONG", "Cermin dah jadi kawan baik", 35.07, "sinis"),
    (37.85, 38.0, "SEMAKIN MANIS MULUT, SEMAKIN BAHAYA", "Manis tak semestinya ikhlas", 42.15, "tunjuk"),
    (44.85, 45.0, "SEMAKIN MENGELUH, SEMAKIN LEMAH", "Tenaga habis untuk merungut", 49.03, "risau"),
    (52.05, 52.24, "MENGEJEK KEMISKINAN = HATI KOTOR", "Yang miskin sebenarnya hati dia", 55.2, "kejut"),
]
CTA_T = 57.3
if EP == "2":
    POINTS = [
        (6.3, 6.44, "PALING BANYAK KETAWA, PALING BANYAK LUKA", "Senyum tak semestinya bahagia", 11.79, "senyum"),
        (14.2, 14.34, "CEPAT MARAH, CEPAT SEJUK", "Marah sekejap, hati baik", 18.43, "garu"),
        (20.55, 20.70, "SELALU MINTA MAAF = TAKUT KEHILANGAN", "Takut hilang orang tersayang", 24.83, "risau"),
        (27.63, 27.78, "SUKA TOLONG ORANG, SEGAN MINTA TOLONG", "Pandai memberi, segan meminta", 30.8, "senyum"),
        (33.23, 33.38, "ASYIK CERITA DIRI = CARI PENGIKTIRAFAN", "Dia nak orang nampak dia", 36.72, "sinis"),
        (39.07, 39.22, "SELALU TIDUR LAMBAT, KEPALA PENUH", "Fikiran tak pernah berhenti", 43.63, "fikir"),
        (45.33, 45.48, "PALING TENANG, PALING BANYAK RIBUT", "Tenang sebab dah biasa diuji", 48.3, "tunjuk"),
    ]
    CTA_T = 50.6


def headline_sprite(text):
    for size in (78, 70, 62):
        f = F_BLACK(size)
        lines = wrap(text, f, 960)
        if len(lines) <= 2:
            break
    sps = [text_sprite(l, f, YELLOW, stroke=4) for l in lines]
    w = max(s.width for s in sps)
    h = sum(s.height for s in sps) - 18 * (len(sps) - 1)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    y = 0
    for s in sps:
        im.alpha_composite(s, ((w - s.width) // 2, y))
        y += s.height - 18
    return im


HEAD = [headline_sprite(p[2]) for p in POINTS]
SUB = [chip(p[3], F_XB(46), INK, WHITE) for p in POINTS]


def badge(n, r=92):
    im = Image.new("RGBA", (2 * r + 30, 2 * r + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((14, 20, 2 * r + 14, 2 * r + 20), fill=(0, 0, 0, 140))
    d.ellipse((6, 6, 2 * r + 6, 2 * r + 6), fill=YELLOW, outline=INK, width=8)
    f = F_BLACK(int(r * 1.3))
    t = str(n)
    b = f.getbbox(t)
    d.text((6 + r - (b[0] + b[2]) / 2, 6 + r - (b[1] + b[3]) / 2), t, font=f, fill=INK)
    return im


BADGE = [badge(i + 1) for i in range(7)]
SMALL = [badge(i + 1, 40) for i in range(7)]


def pose_at(t):
    if t < POINTS[0][0]:
        return "kejut" if t < CFG["badge_t"] else "teruja"
    if t >= CTA_T:
        return "tunjuk" if t > CTA_T + 2.2 else "teruja"
    for p in reversed(POINTS):
        if t >= p[0]:
            return p[5]
    return "senyum"


def pose_start(t):
    if t >= CTA_T:
        return CTA_T if t < CTA_T + 2.2 else CTA_T + 2.2
    starts = [0.0, CFG["badge_t"]] + [p[0] for p in POINTS]
    return max(s for s in starts if s <= t)


# ---------------------------------------------------------------- frame
def draw_narrator(c, t):
    name = pose_at(t)
    t0 = pose_start(t)
    spr = POSE[name]
    u = ease_back((t - t0 - 0.05) / 0.45) if t0 > 0 else ease_back((t - 0.15) / 0.6)
    bob = 6 * math.sin(t * 2.1)
    cy = H - spr.height / 2 + 10 + (1 - u) * 300 + bob
    sc = 0.94 + 0.06 * u
    place(c, spr, W / 2 + 20, cy, scale=sc, rot=(1 - u) * -4)


def draw_progress(c, t, cur):
    y = 1175
    for i in range(7):
        x = W / 2 + (i - 3) * 104
        if i < cur:
            place(c, SMALL[i], x, y, scale=1.0 if i < cur - 1 else 1 + 0.25 * (1 - ease_out((t - POINTS[i][1]) / 0.3)))
        else:
            d = ImageDraw.Draw(c)
            d.ellipse((x - 34, y - 34, x + 34, y + 34), outline=(255, 255, 255, 90), width=5)


def draw_point(c, t, i):
    st, nt, _, _, sub_t, _ = POINTS[i]
    end = POINTS[i + 1][0] if i + 1 < 7 else CTA_T
    ex = ease_out((t - (end - 0.3)) / 0.3)  # exit to the left
    dx = -1200 * ex
    # icon
    u = ease_back((t - nt - 0.12) / 0.5)
    ic = ICONS[i]
    k = min(470 / ic.width, 400 / ic.height)
    wig = 2.5 * math.sin((t - nt) * 3.0)
    place(c, ic, W / 2 + 70 + dx + (1 - ease_out((t - st) / 0.4)) * 900  , 620, scale=k * (0.6 + 0.4 * u), rot=wig)
    # number badge
    ub = ease_back((t - nt) / 0.4)
    place(c, BADGE[i], 190 + dx, 500, scale=0.2 + 0.8 * ub, rot=(1 - ub) * 90)
    # headline
    uh = ease_out((t - nt - 0.3) / 0.35)
    place(c, HEAD[i], W / 2 + dx, 930 + (1 - uh) * 40, alpha=uh)
    # sub-line chip
    us = ease_back((t - sub_t) / 0.4)
    if t > sub_t:
        place(c, SUB[i], W / 2 + dx, 1075, scale=0.5 + 0.5 * us, rot=-2)
    if i == CFG["star_i"]:  # the promised number
        uf = clamp((t - nt) / 0.25) * (1 - clamp((t - nt - 0.9) / 0.4))
        if uf > 0:
            place(c, chip(CFG["star_txt"], F_BLACK(56), WHITE, RED), 830 + dx, 470, scale=0.6 + 0.4 * ease_back(uf), rot=8)


def draw_hook(c, t):
    u = ease_back((t - 0.25) / 0.5)
    ex = ease_out((t - CFG["hook_end"] + 0.3) / 0.3)
    place(c, HEADER, W / 2 - ex * 0, 220 + (1 - u) * -400, scale=1.0)
    if t < CFG["hook_end"]:
        f = F_BLACK(64)
        t1 = text_sprite(CFG["hook1"], f, WHITE, stroke=3)
        t2 = text_sprite(CFG["hook2"], f, WHITE, stroke=3)
        a = ease_out((t - 1.2) / 0.4) * (1 - ex)
        place(c, t1, W / 2, 520, alpha=a)
        place(c, t2, W / 2, 600, alpha=ease_out((t - 1.6) / 0.4) * (1 - ex))
        if t > CFG["badge_t"]:
            ub = ease_back((t - CFG["badge_t"]) / 0.45)
            place(c, BADGE[CFG["badge_i"]], W / 2, 820, scale=1.3 * ub * (1 - ex), rot=(1 - ub) * 60)
            place(c, chip(CFG["hook_chip"], F_BLACK(50), WHITE, RED), W / 2, 1010,
                  scale=max(0.01, ease_back((t - CFG["badge_t"] - 0.4) / 0.4) * (1 - ex)), rot=-3)


def draw_cta(c, t):
    u = ease_out((t - CTA_T) / 0.4)
    f = F_BLACK(84)
    place(c, text_sprite(CFG["cta1"], f, WHITE, stroke=4), W / 2, 520, alpha=u)
    place(c, text_sprite(CFG["cta2"], f, YELLOW, stroke=4), W / 2, 615, alpha=ease_out((t - CTA_T - 0.25) / 0.4))
    for i in range(7):
        ub = ease_back((t - CTA_T - 0.9 - i * 0.12) / 0.4)
        jump = 14 * max(0, math.sin((t - CTA_T) * 6 - i * 0.7)) if t > CTA_T + 2 else 0
        place(c, SMALL[i], W / 2 + (i - 3) * 118, 800 - jump, scale=1.35 * ub)
    if t > CTA_T + 1.9:
        place(c, chip(CFG["cta_chip"], F_BLACK(44), INK, YELLOW), W / 2, 960,
              scale=ease_back((t - CTA_T - 1.9) / 0.4), rot=-2)
        ar = 18 * math.sin((t - CTA_T) * 8)
        d = ImageDraw.Draw(c)
        cx, cy = W / 2, 1060 + ar
        d.polygon([(cx - 40, cy), (cx + 40, cy), (cx, cy + 50)], fill=YELLOW)


def frame(fi):
    t = fi / FPS
    c = BG.copy()
    if t < POINTS[0][0]:
        draw_hook(c, t)
    else:
        place(c, HEADER, W / 2, 220, scale=0.72 if t < CTA_T else 0.72)
        if t < CTA_T:
            cur = max(i for i in range(7) if t >= POINTS[i][0])
            if cur > 0 and t < POINTS[cur][0] + 0.35:  # previous card leaving
                draw_point(c, t, cur - 1)
            draw_point(c, t, cur)
            draw_progress(c, t, cur + (1 if t >= POINTS[cur][1] else 0))
        else:
            if t < CTA_T + 0.35:
                draw_point(c, t, 6)
            draw_cta(c, t)
    draw_narrator(c, t)
    # flash on each number call
    for p in POINTS:
        if 0 <= t - p[1] < 0.12:
            c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(70 * (1 - (t - p[1]) / 0.12)))))
    rgb = c.convert("RGB")
    g = GRAIN[fi % 4]
    rgb = Image.blend(rgb, Image.merge("RGB", (g, g, g)), 0.05)
    return np.asarray(rgb)


if __name__ == "__main__":
    if OUT.endswith(".jpg"):
        for ts in sys.argv[3:]:
            Image.fromarray(frame(int(float(ts) * FPS))).save(OUT.replace(".jpg", f"_{ts}.jpg"), quality=85)
        sys.exit()
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "23",
                          "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
    for fi in range(N):
        p.stdin.write(frame(fi).tobytes())
    p.stdin.close()
    p.wait()
