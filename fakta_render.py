"""Episode — "6 Fakta Psikologi" (~50 s, 1080x1920@30) in a Remotion-style polished look.

Remotion-skill ideas re-built in Python: spring-physics animation, smooth slide/zoom transitions
with motion blur and a light-leak flash between sections, animated word-by-word captions driven by
the ElevenLabs character timestamps, film grain + vignette + gate weave over everything.

Usage: python3 fakta_render.py <workdir> <out.mp4|prefix.jpg> [t ...]   (workdir needs pose/*)
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
DUR = 50.4
N = int(DUR * FPS)
WORDS = json.load(open("assets/vo_fakta_psikologi_words.json"))

YEL = (255, 210, 40)
WHITE = (255, 255, 255)
INK = (10, 10, 14)
FD = "/usr/share/fonts/opentype/inter/"
_fc = {}


def font(name, size):
    if (name, size) not in _fc:
        _fc[(name, size)] = ImageFont.truetype(FD + name + ".otf", size)
    return _fc[(name, size)]


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def spring(t, damping=11.0, freq=13.0):
    """Remotion-like spring: 0 -> 1 with a soft overshoot."""
    if t <= 0:
        return 0.0
    return 1 - math.exp(-damping * t) * math.cos(freq * t)


def ease_io(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def paste(canvas, s, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
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


def txt(text, f, fill, stroke=0, sfill=INK, shadow=0.55):
    b = f.getbbox(text, stroke_width=stroke)
    im = Image.new("RGBA", (b[2] - b[0] + 40, b[3] - b[1] + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((20 - b[0], 26 - b[1]), text, font=f, fill=(0, 0, 0, int(255 * shadow)),
                                stroke_width=stroke, stroke_fill=(0, 0, 0, int(255 * shadow)))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    d.text((20 - b[0], 20 - b[1]), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=sfill)
    return im


def pill(text, f, fg, bg, padx=28, pady=14):
    b = f.getbbox(text)
    w, h = b[2] - b[0] + 2 * padx, b[3] - b[1] + 2 * pady
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=bg)
    ImageDraw.Draw(im).text((padx - b[0], pady - b[1]), text, font=f, fill=fg)
    return im


# ---------------------------------------------------------------- sections
SECT = [  # (start, kicker, headline, pose, colour top, colour bottom)
    (0.0, None, ["6 FAKTA", "PSIKOLOGI"], "kejut", (20, 24, 58), (6, 8, 20)),
    (4.18, "ZEIGARNIK EFFECT", ["KERJA TAK SIAP", "LEBIH DIINGATI"], "fikir", (58, 22, 70), (14, 6, 22)),
    (12.83, "BEN FRANKLIN EFFECT", ["MINTA TOLONG", "= LEBIH RAPAT"], "senyum", (12, 70, 74), (4, 18, 22)),
    (21.06, "SPOTLIGHT EFFECT", ["TAK ADA SIAPA", "PERHATI SANGAT"], "garu", (86, 30, 24), (24, 8, 6)),
    (28.93, "KUASA NAMA", ["SEBUT NAMA,", "RASA DIHARGAI"], "sinis", (20, 70, 40), (6, 20, 12)),
    (34.15, "TEKNIK DIAM", ["DIAM SEKEJAP,", "DIA CERITA LEBIH"], "tunjuk", (28, 40, 90), (8, 10, 28)),
    (40.40, "PROTEGE EFFECT", ["NAK INGAT?", "AJAR ORANG LAIN"], "teruja", (90, 64, 10), (26, 16, 2)),
    (44.83, None, ["FAKTA MANA", "AWAK BARU TAHU?"], "tunjuk", (30, 30, 34), (8, 8, 10)),
]
TR = 0.5  # transition length (s), centred on the section start


def sect_at(t):
    return max(i for i, s in enumerate(SECT) if t >= s[0])


# ---------------------------------------------------------------- backgrounds (gradient + drifting light blobs)
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def bg_frame(i, t):
    top, bot = np.array(SECT[i][4], np.float32), np.array(SECT[i][5], np.float32)
    g = (YY / H)[..., None]
    img = top * (1 - g) + bot * g
    for k in range(3):
        cx = W * (0.5 + 0.42 * math.sin(0.23 * t + k * 2.1 + i))
        cy = H * (0.35 + 0.3 * math.cos(0.17 * t + k * 1.7))
        r = 380 + 80 * k
        d = np.exp(-(((XX - cx) ** 2 + (YY - cy) ** 2) / (2 * r * r)))
        img += d[..., None] * (top * 0.45 + 8)
    return img


# ---------------------------------------------------------------- narrator
def colour_grade(rgb):
    lab = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2LAB)
    lab[..., 0] = cv2.createCLAHE(clipLimit=1.6, tileGridSize=(8, 8)).apply(lab[..., 0])
    out = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB).astype(np.float32)
    g = out.mean(axis=2, keepdims=True)
    return np.clip((g + (out - g) * 1.1) * np.array([1.03, 1.0, 0.97], np.float32), 0, 255)


def narrator(name, target_w=900, max_h=1180):
    im = np.asarray(Image.open(f"{WD}/pose/{name}.jpg").convert("RGB")).astype(np.float32)
    m = np.asarray(Image.open(f"{WD}/pose/{name}_mask.png").convert("L")).astype(np.float32) / 255
    m = np.clip((m - 0.3) / 0.4, 0, 1)
    n, lab, st, _ = cv2.connectedComponentsWithStats((m > 0.5).astype(np.uint8))
    if n > 2:
        m = m * (lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])))
    ys, xs = np.where(m > 0.5)
    im, m = im[ys.min():, xs.min():xs.max() + 1], m[ys.min():, xs.min():xs.max() + 1]
    k = target_w / im.shape[1]
    im = cv2.resize(colour_grade(im), None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
    m = cv2.resize(m, None, fx=k, fy=k)
    # soft rim light so he separates from the background
    edge = np.clip(m - cv2.erode(m, np.ones((9, 9), np.uint8)), 0, 1)
    im = np.clip(im + edge[..., None] * 90, 0, 255)
    spr = Image.fromarray(np.dstack([im, m * 255]).astype(np.uint8), "RGBA")
    spr = spr.crop((0, 0, spr.width, min(spr.height, max_h)))
    # fade the bottom edge so the crop never shows a hard line
    a = np.asarray(spr.split()[3]).astype(np.float32)
    fade = np.clip((spr.height - np.arange(spr.height)) / 160, 0, 1)[:, None]
    spr.putalpha(Image.fromarray((a * fade).astype(np.uint8)))
    return spr


POSE = {n: narrator(n) for n in {s[3] for s in SECT}}


# ---------------------------------------------------------------- captions (word by word)
def caption_groups():
    groups, cur = [], []
    for w in WORDS:
        cur.append(w)
        end_sentence = w[0][-1] in ".?!,"
        if len(cur) >= 4 or end_sentence:
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    return groups


GROUPS = caption_groups()
F_CAP = font("Inter-Black", 74)


def draw_captions(c, t):
    g = None
    for gr in GROUPS:
        if gr[0][1] - 0.05 <= t <= gr[-1][2] + 0.25:
            g = gr
    if g is None:
        return
    words = [w[0].upper() for w in g]
    widths = [F_CAP.getlength(w) for w in words]
    sp = 22
    total = sum(widths) + sp * (len(words) - 1)
    if total > 980:  # two lines
        half = len(words) // 2
        lines = [list(range(half)), list(range(half, len(words)))]
    else:
        lines = [list(range(len(words)))]
    y = 1610 - (len(lines) - 1) * 50
    for ln in lines:
        lw = sum(widths[i] for i in ln) + sp * (len(ln) - 1)
        x = W / 2 - lw / 2
        for i in ln:
            st, en = g[i][1], g[i][2]
            if t < st - 0.04:
                x += widths[i] + sp
                continue
            active = st - 0.04 <= t <= en + 0.08
            pop = spring(t - st + 0.04, 14, 18)
            col = YEL if active else WHITE
            spr = txt(words[i], F_CAP, col, stroke=7, sfill=INK, shadow=0.6)
            sc = (0.55 + 0.45 * min(pop, 1.15)) * (1.08 if active else 1.0)
            paste(c, spr, x + widths[i] / 2, y + 40 - 12 * (1 - clamp(pop)), scale=sc)
            x += widths[i] + sp
        y += 100


# ---------------------------------------------------------------- section layer
F_NUM = font("Inter-Black", 300)
F_HEAD = font("Inter-Black", 104)
F_KICK = font("Inter-ExtraBold", 40)


def number_sprite(n):
    s = f"0{n}"
    b = F_NUM.getbbox(s)
    im = Image.new("RGBA", (b[2] - b[0] + 40, b[3] - b[1] + 40), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((20 - b[0], 20 - b[1]), s, font=F_NUM, fill=(255, 255, 255, 0),
                            stroke_width=5, stroke_fill=(255, 255, 255, 110))
    return im


NUMS = {i: number_sprite(i) for i in range(1, 7)}
HEADS = {i: [txt(l, F_HEAD, WHITE if j == 0 else YEL, stroke=0, shadow=0.7) for j, l in enumerate(s[2])]
         for i, s in enumerate(SECT)}
KICKS = {i: pill(s[1], F_KICK, INK, YEL) for i, s in enumerate(SECT) if s[1]}


def section_layer(i, t):
    """Everything belonging to section i at absolute time t, drawn on a transparent layer."""
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lt = t - SECT[i][0]
    if 1 <= i <= 6:  # big outline number behind the headline
        u = spring(lt - 0.05, 8, 9)
        paste(c, NUMS[i], W / 2 + 230, 330 + 30 * (1 - u), scale=0.9 + 0.1 * u, alpha=clamp(u))
        paste(c, KICKS[i], W / 2, 250, scale=clamp(spring(lt - 0.15)))
    for j, hs in enumerate(HEADS[i]):  # headline lines rise in, staggered
        u = spring(lt - 0.25 - 0.12 * j, 10, 12)
        paste(c, hs, W / 2, 380 + j * 118 + 60 * (1 - clamp(u)), scale=0.9 + 0.1 * min(u, 1.1), alpha=clamp(u * 1.4))
    if i == 0:
        u = spring(lt - 1.2, 10, 12)
        paste(c, pill("YANG BUAT AWAK FAHAM MANUSIA", font("Inter-ExtraBold", 44), INK, YEL), W / 2, 640,
              scale=clamp(u))
    if i == 7:
        u = spring(lt - 2.2, 10, 12)
        paste(c, pill("KOMEN + FOLLOW", font("Inter-Black", 54), INK, YEL), W / 2, 640, scale=clamp(u),
              rot=-3 * clamp(u))
    # narrator: springs up, slow push-in
    name = SECT[i][3]
    if i == 0 and t > 2.0:
        name = "teruja"
    spr = POSE[name]
    u = spring(lt - 0.1, 9, 10) if i > 0 else spring(t - 0.2, 9, 10)
    if i == 0 and t > 2.0:
        u = spring(t - 2.0, 12, 14)
    push = 1 + 0.025 * clamp(lt / 6)
    paste(c, spr, W / 2, H - spr.height / 2 + 60 + 340 * (1 - clamp(u)), scale=push * (0.94 + 0.06 * min(u, 1.1)))
    return c


# ---------------------------------------------------------------- film finish
rng = np.random.default_rng(5)
GRAIN = [cv2.GaussianBlur(rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32), (0, 0), 0.6) for _ in range(8)]
VIG = (1 - 0.55 * np.clip(((XX - W / 2) / (W * 0.75)) ** 2 + ((YY - H / 2) / (H * 0.7)) ** 2, 0, 1)).astype(np.float32)
CAP_SHADE = np.clip((YY - 1400) / 260, 0, 1).astype(np.float32) * 0.6


def finish(rgb, fi, t):
    img = rgb.astype(np.float32)
    img *= (1 - CAP_SHADE)[..., None]
    img *= VIG[..., None]
    g = cv2.resize(GRAIN[fi % 8], (W, H))
    img += g[..., None] * 9
    # light leak on transitions
    for s in SECT[1:]:
        d = t - s[0]
        if -0.25 < d < 0.35:
            k = math.exp(-((d - 0.02) / 0.14) ** 2)
            leak = np.exp(-(((XX - W * 0.85) ** 2) / (2 * 420 ** 2) + ((YY - H * 0.25) ** 2) / (2 * 700 ** 2)))
            img += leak[..., None] * np.array([255, 150, 60], np.float32) * 0.7 * k
    img = np.clip(img, 0, 255).astype(np.uint8)
    # gate weave
    dx, dy = int(round(1.2 * math.sin(fi * 0.9))), int(round(1.2 * math.cos(fi * 1.3)))
    return np.roll(img, (dy, dx), axis=(0, 1))


def compose(i, t):
    bg = Image.fromarray(np.clip(bg_frame(i, t), 0, 255).astype(np.uint8)).convert("RGBA")
    bg.alpha_composite(section_layer(i, t))
    return bg


def frame(fi):
    t = fi / FPS
    i = sect_at(t)
    # transition window: slide old out to the left, new in from the right (with motion blur)
    nxt = i + 1 if i + 1 < len(SECT) and SECT[i + 1][0] - t < TR / 2 else None
    if nxt is not None or (i > 0 and t - SECT[i][0] < TR / 2):
        a, b = (i, nxt) if nxt is not None else (i - 1, i)
        p = ease_io((t - (SECT[b][0] - TR / 2)) / TR)
        A = np.asarray(compose(a, t).convert("RGB"))
        B = np.asarray(compose(b, t).convert("RGB"))
        off = int(W * p)
        out = np.zeros_like(A)
        out[:, :W - off] = A[:, off:]
        out[:, W - off:] = B[:, :off]
        speed = math.sin(math.pi * p)
        ksz = int(1 + 60 * speed) | 1
        if ksz > 1:
            kern = np.zeros((1, ksz), np.float32)
            kern[0, :] = 1 / ksz
            out = cv2.filter2D(out, -1, kern)
        base = Image.fromarray(out).convert("RGBA")
    else:
        base = compose(i, t)
    rgb = np.asarray(base.convert("RGB")).copy()
    cap = Image.fromarray(finish(rgb, fi, t)).convert("RGBA")
    draw_captions(cap, t)  # captions stay crisp above the grain
    return np.asarray(cap.convert("RGB"))


if __name__ == "__main__":
    if OUT.endswith(".jpg"):
        for ts in sys.argv[3:]:
            Image.fromarray(frame(int(float(ts) * FPS))).save(OUT.replace(".jpg", f"_{ts}.jpg"), quality=85)
        sys.exit()
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "22",
                          "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
    for fi in range(N):
        p.stdin.write(frame(fi).tobytes())
    p.stdin.close()
    p.wait()
