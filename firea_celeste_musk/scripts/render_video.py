"""Render the edited picture (no audio) for the Firea Celeste Musk UGC ad.

Usage: python render_video.py <project_dir> <out.mp4> [--frames a:b] [--still t1,t2,...]
Reads source/footage.mp4, assets/, scripts/cues.py. Writes H.264 video only;
build.sh muxes the mixed audio afterwards.
"""
import math
import os
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import cues as C  # noqa: E402

P = sys.argv[1]
OUT = sys.argv[2]
W, H, FPS = 1080, 1920, 30
NF = int(round(C.DURATION * FPS))

# ---------------------------------------------------------------- brand palette (from label)
MAROON = (110, 23, 52)
ROSE = (214, 66, 120)
BLUSH = (248, 220, 231)
CREAM = (255, 248, 250)
WHITE = (255, 255, 255)
GREEN = (38, 150, 104)
RED = (215, 38, 61)


def F(name, size):
    files = {"xb": "Poppins-ExtraBold", "b": "Poppins-Bold", "sb": "Poppins-SemiBold",
             "m": "Poppins-Medium", "serif": "DMSerifDisplay-Italic"}
    return ImageFont.truetype(f"{P}/assets/fonts/{files[name]}.ttf", size)


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def e_out(x):
    return 1 - (1 - clamp(x)) ** 3


def e_inout(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def e_back(x):
    x = clamp(x)
    c1 = 1.9
    return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2


def window(t, t0, t1, fin=0.16, fout=0.14):
    """0..1 visibility with in/out ramps."""
    if t < t0 or t > t1:
        return 0.0
    return min(clamp((t - t0) / fin), clamp((t1 - t) / fout))


# ---------------------------------------------------------------- drawing helpers
def shadowed(img, blur=18, offset=(0, 10), alpha=90, pad=40):
    """Return img on a larger canvas with a soft drop shadow; also returns pad."""
    w, h = img.size
    can = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    a = np.array(img.split()[-1]).astype(np.float32) * alpha / 255
    sh = np.zeros((h + 2 * pad, w + 2 * pad), np.float32)
    sh[pad + offset[1]:pad + offset[1] + h, pad + offset[0]:pad + offset[0] + w] = a
    sh = cv2.GaussianBlur(sh, (0, 0), blur)
    shadow = Image.fromarray(np.dstack([np.full_like(sh, 40), np.full_like(sh, 8), np.full_like(sh, 20), sh]).astype(np.uint8), "RGBA")
    can.alpha_composite(shadow)
    can.alpha_composite(img, (pad, pad))
    return can


def text_size(font, s):
    b = font.getbbox(s)
    return b[2] - b[0], b[3] - b[1], b


def pill(text, font, fg, bg, padx=34, pady=18, radius=None):
    tw, th, b = text_size(font, text)
    asc, desc = font.getmetrics()
    h = asc + desc + 2 * pady - 10
    w = tw + 2 * padx
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius if radius is not None else h // 2, fill=bg)
    d.text((padx - b[0], (h - (asc + desc)) // 2 + 2), text, font=font, fill=fg)
    return im


def draw_check(d, cx, cy, r, color):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    w = max(4, r // 4)
    d.line([(cx - r * 0.45, cy + r * 0.02), (cx - r * 0.1, cy + r * 0.38), (cx + r * 0.5, cy - r * 0.35)], fill=WHITE, width=w, joint="curve")


def draw_cross(d, cx, cy, r, color):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    w = max(4, r // 4)
    k = r * 0.38
    d.line([(cx - k, cy - k), (cx + k, cy + k)], fill=WHITE, width=w)
    d.line([(cx - k, cy + k), (cx + k, cy - k)], fill=WHITE, width=w)


def stroked_text(text, font, fill, stroke, sw, shadow=True):
    tw, th, b = text_size(font, text)
    pad = sw + 6
    im = Image.new("RGBA", (tw + 2 * pad, th + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((pad - b[0], pad - b[1]), text, font=font, fill=fill, stroke_width=sw, stroke_fill=stroke)
    return shadowed(im, blur=14, offset=(0, 8), alpha=110) if shadow else im


# ---------------------------------------------------------------- pre-rendered elements
def build_elements():
    E = {}
    # hook
    E["hook"] = shadowed(pill("Suka aktiviti luar?", F("b", 58), MAROON, (255, 255, 255, 240), padx=40, pady=22))
    # BAU BADAN?
    E["bau"] = stroked_text("BAU BADAN?", F("xb", 132), WHITE, MAROON, 10)
    # checklist card
    cw, ch = 860, 250
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle([0, 0, cw - 1, ch - 1], radius=44, fill=(255, 255, 255, 242))
    E["check_card"] = card
    row = []
    for label, tag, ok in (("Peluh banyak", "takpe", True), ("Bau badan", "jangan!", False)):
        im = Image.new("RGBA", (cw - 60, 100), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        (draw_check if ok else draw_cross)(d, 46, 50, 40, GREEN if ok else RED)
        f = F("b", 56)
        d.text((110, 50), label, font=f, fill=MAROON, anchor="lm")
        tagim = pill(tag, F("sb", 40), WHITE, GREEN if ok else RED, padx=24, pady=12)
        im.alpha_composite(tagim, (im.width - tagim.width - 6, 50 - tagim.height // 2))
        row.append(im)
    E["row1"], E["row2"] = row
    # TAK SELESA
    E["selesa"] = shadowed(pill("TAK SELESA", F("xb", 104), WHITE, MAROON, padx=44, pady=16, radius=28))
    # brand card
    bw, bh = 700, 280
    bc = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(bc)
    d.rounded_rectangle([0, 0, bw - 1, bh - 1], radius=48, fill=CREAM + (246,))
    d.text((48, 118), "Firea", font=F("serif", 168), fill=MAROON, anchor="ls")
    d.text((52, 196), "Celeste Musk", font=F("sb", 56), fill=ROSE, anchor="ls")
    d.text((54, 244), "Deodorant Roll-on  ·  Antiperspirant", font=F("m", 30), fill=MAROON, anchor="ls")
    E["brand"] = shadowed(bc)
    # chips
    for k, txt in (("chip1", "Kawal peluh"), ("chip2", "Hilang bau badan")):
        f = F("b", 35)
        im = pill(txt, f, MAROON, BLUSH + (250,), padx=24, pady=16)
        full = Image.new("RGBA", (im.width + 56, im.height), (0, 0, 0, 0))
        dd = ImageDraw.Draw(full)
        dd.rounded_rectangle([0, 0, full.width - 1, full.height - 1], radius=full.height // 2, fill=BLUSH + (250,))
        draw_check(dd, 38, full.height // 2, 20, ROSE)
        dd.text((68, full.height // 2 + 2), txt, font=f, fill=MAROON, anchor="lm")
        E[k] = shadowed(full, blur=12, offset=(0, 6), alpha=80)
    # bottle sticker (white outline)
    b = Image.open(f"{P}/assets/bottle.png").convert("RGBA")
    s = 0.52
    b = b.resize((int(b.width * s), int(b.height * s)), Image.LANCZOS)
    a = np.array(b.split()[-1])
    pad = 14
    big = np.zeros((a.shape[0] + 2 * pad, a.shape[1] + 2 * pad), np.uint8)
    big[pad:-pad, pad:-pad] = a
    outline = cv2.dilate(big, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * 10 + 1, 2 * 10 + 1)))
    st = Image.new("RGBA", (big.shape[1], big.shape[0]), (0, 0, 0, 0))
    st.paste(Image.new("RGBA", st.size, WHITE + (255,)), (0, 0), Image.fromarray(outline))
    st.alpha_composite(b, (pad, pad))
    E["bottle"] = shadowed(st, blur=20, offset=(0, 14), alpha=120)
    # questions
    E["q1"] = shadowed(pill("Kuat berpeluh?", F("b", 60), MAROON, (255, 255, 255, 245), padx=40, pady=22))
    E["q2"] = shadowed(pill("Takut badan berbau?", F("b", 60), WHITE, ROSE, padx=40, pady=22))
    # end card
    ew, eh = 700, 330
    ec = Image.new("RGBA", (ew, eh), (0, 0, 0, 0))
    d = ImageDraw.Draw(ec)
    d.rounded_rectangle([0, 0, ew - 1, eh - 1], radius=48, fill=CREAM + (246,))
    d.text((52, 70), "Pakai je", font=F("sb", 46), fill=ROSE, anchor="ls")
    d.text((48, 196), "Firea", font=F("serif", 160), fill=MAROON, anchor="ls")
    d.text((52, 252), "Celeste Musk  ·  Roll-on 50ml", font=F("sb", 36), fill=MAROON, anchor="ls")
    E["end"] = shadowed(ec)
    E["cta"] = shadowed(pill(C.CTA_TEXT + "  ›", F("b", 46), WHITE, ROSE, padx=40, pady=20), alpha=120)
    claims = Image.new("RGBA", (ew - 104, 52), (0, 0, 0, 0))
    x = 0
    for txt in ("0% Alkohol", "0% Paraben"):
        c = pill(txt, F("sb", 30), MAROON, BLUSH + (255,), padx=20, pady=8)
        claims.alpha_composite(c, (x, (52 - c.height) // 2))
        x += c.width + 14
    E["claims"] = claims
    return E


def caption_image(text):
    f = F("b", 62)
    words = text.split(" ")
    # mark hilite spans
    colors = [MAROON] * len(words)
    low = [w.strip(",.?!").lower() for w in words]
    for h in C.HILITE:
        hw = h.lower().split(" ")
        for i in range(len(words) - len(hw) + 1):
            if low[i:i + len(hw)] == hw:
                for j in range(i, i + len(hw)):
                    colors[j] = ROSE
    space = f.getlength(" ")
    widths = [f.getlength(w) for w in words]
    tw = int(sum(widths) + space * (len(words) - 1))
    asc, desc = f.getmetrics()
    padx, pady = 38, 16
    w, h = tw + 2 * padx, asc + desc + 2 * pady - 8
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=30, fill=(255, 255, 255, 238))
    x = padx
    for wd, wi, col in zip(words, widths, colors):
        d.text((x, pady - 2), wd, font=f, fill=col)
        x += wi + space
    assert w <= 1000, f"caption too wide: {text} ({w}px)"
    return shadowed(im, blur=14, offset=(0, 8), alpha=90)


# ---------------------------------------------------------------- compositing
def place(canvas, img, cx, cy, scale=1.0, alpha=1.0, rot=0.0, anchor="c"):
    if alpha <= 0.01 or scale <= 0.01:
        return
    im = img
    if abs(scale - 1) > 1e-3:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if abs(rot) > 0.05:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        a = im.split()[-1].point(lambda v: int(v * alpha))
        im = im.copy()
        im.putalpha(a)
    if anchor == "c":
        x, y = int(cx - im.width / 2), int(cy - im.height / 2)
    else:  # left-center
        x, y = int(cx), int(cy - im.height / 2)
    canvas.alpha_composite(im, (max(0, x), max(0, y)), (max(0, -x), max(0, -y)))


def zoom_at(t):
    K = C.ZOOM_KEYS
    if t <= K[0][0]:
        return K[0][1:]
    for a, b in zip(K, K[1:]):
        if a[0] <= t <= b[0]:
            u = (t - a[0]) / max(1e-6, b[0] - a[0])
            u = e_inout(u) if b[0] - a[0] > 0.6 else e_out(u)
            return tuple(a[i] + (b[i] - a[i]) * u for i in (1, 2, 3))
    return K[-1][1:]


def grade(fr, t):
    f = fr.astype(np.float32)
    # cool / flat look for the "tak selesa" beat
    g0, g1 = C.GRADE_COOL
    k = min(clamp((t - g0) / 0.6), 1.0 if t < g1 else 0.0) * 0.55
    if k > 0:
        gray = f.mean(axis=2, keepdims=True)
        f = f * (1 - k * 0.7) + gray * (k * 0.7)
        f[..., 2] *= 1 + 0.06 * k   # RGB order: boost blue
        f[..., 0] *= 1 - 0.05 * k
        f *= 1 - 0.08 * k
    # pink light-leak flash at the product cut
    dt = t - C.SCENE_CUT
    fl = math.exp(-((dt + 0.02) / 0.11) ** 2) * 0.85 if -0.3 < dt < 0.5 else 0.0
    if fl > 0:
        f = f * (1 - fl * 0.55) + np.array([255, 214, 230], np.float32) * fl * 0.55
    f *= VIGNETTE
    return np.clip(f, 0, 255).astype(np.uint8)


yy, xx = np.mgrid[0:H, 0:W]
VIGNETTE = (1 - 0.18 * (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.45) / (H * 0.7)) ** 2))[..., None].astype(np.float32)


def overlays(canvas, t, E, cap_cache):
    # hook
    a = window(t, *C.HOOK)
    if a:
        p = e_back((t - C.HOOK[0]) / 0.35)
        place(canvas, E["hook"], 540, 250, scale=0.7 + 0.3 * p, alpha=a)
    # BAU BADAN?
    a = window(t, *C.BAU, fin=0.06)
    if a:
        u = t - C.BAU[0]
        p = e_back(u / 0.28)
        shake = math.sin(u * 55) * 6 * math.exp(-u * 5)
        place(canvas, E["bau"], 540 + shake, 260, scale=0.5 + 0.5 * p, alpha=a, rot=4)
    # checklist
    if C.CHECK_ROW1 <= t <= C.CHECK_END:
        a = window(t, C.CHECK_ROW1, C.CHECK_END)
        p = e_out((t - C.CHECK_ROW1) / 0.3)
        card = E["check_card"].copy()
        r1 = e_back((t - C.CHECK_ROW1 - 0.05) / 0.3)
        if r1 > 0:
            card.alpha_composite(E["row1"], (30 + int((1 - min(r1, 1)) * -40), 22))
        r2 = e_back((t - C.CHECK_ROW2) / 0.3)
        if t >= C.CHECK_ROW2:
            card.alpha_composite(E["row2"], (30 + int((1 - min(r2, 1)) * -40), 128))
        place(canvas, shadowed(card), 540, 270 - 40 * (1 - p), alpha=a)
    # TAK SELESA
    a = window(t, *C.SELESA)
    if a:
        u = t - C.SELESA[0]
        p = e_back(u / 0.35)
        wob = math.sin(u * 3.2) * 1.6
        place(canvas, E["selesa"], 540, 250, scale=0.6 + 0.4 * p, alpha=a, rot=-3 + wob)
    # brand block + chips + bottle
    a = window(t, *C.BRAND, fin=0.2, fout=0.2)
    if a:
        u = t - C.BRAND[0]
        p = e_out(u / 0.45)
        place(canvas, E["brand"], 40 - 120 * (1 - p), 260, alpha=a, anchor="l")
        for k, t0, y in (("chip1", C.CHIP1, 470), ("chip2", C.CHIP2, 470)):
            if t >= t0:
                q = e_back((t - t0) / 0.3)
                x = 40 if k == "chip1" else 40 + E["chip1"].width - 66
                place(canvas, E[k], x + E[k].width / 2, y, scale=0.6 + 0.4 * q, alpha=a)
    for t0, t1 in ((C.BRAND[0] + 0.15, C.BRAND[1]), (C.END, C.DURATION + 1)):
        a = window(t, t0, t1, fin=0.2, fout=0.2)
        if a:
            u = t - t0
            p = e_back(u / 0.45)
            bob = math.sin(u * 2.4) * 6
            place(canvas, E["bottle"], 945, 330 + 260 * (1 - min(p, 1.0)) + bob, alpha=a, rot=-7 + 2 * (1 - p))
    # questions
    a = window(t, *C.Q1)
    if a:
        p = e_back((t - C.Q1[0]) / 0.32)
        place(canvas, E["q1"], 540, 230, scale=0.6 + 0.4 * p, alpha=a, rot=-2)
        if t >= C.Q2:
            p2 = e_back((t - C.Q2) / 0.32)
            place(canvas, E["q2"], 540, 375, scale=0.6 + 0.4 * p2, alpha=a, rot=2)
    # end card
    if t >= C.END:
        u = t - C.END
        p = e_out(u / 0.45)
        card = E["end"]
        place(canvas, card, 40 - 120 * (1 - p), 270, alpha=clamp(u / 0.2), anchor="l")
        if t >= C.CLAIMS:
            q = e_out((t - C.CLAIMS) / 0.3)
            place(canvas, E["claims"], 40 + 40 + 52, 270 + 125 - 10 * (1 - q) + 30, alpha=q, anchor="l")
        if t >= C.CTA:
            q = e_back((t - C.CTA) / 0.35)
            pulse = 1 + 0.03 * math.sin((t - C.CTA) * 6) * clamp((t - C.CTA - 0.5) / 0.5)
            place(canvas, E["cta"], 40 + E["cta"].width / 2, 520, scale=(0.6 + 0.4 * q) * pulse)
    # captions (hold through tiny gaps so they don't flicker)
    cur = None
    for i, (s, e, txt) in enumerate(C.CAPTIONS):
        nxt = C.CAPTIONS[i + 1][0] if i + 1 < len(C.CAPTIONS) else e
        if s <= t < (nxt if nxt - e < 0.3 else e):
            cur = (s, e, txt)
    if cur:
        s, e, txt = cur
        if txt not in cap_cache:
            cap_cache[txt] = caption_image(txt)
        u = t - s
        p = e_back(u / 0.18)
        fade = clamp((C.CAPTIONS[-1][1] + 0.25 - t) / 0.25) if txt == C.CAPTIONS[-1][2] else 1.0
        place(canvas, cap_cache[txt], 540, 1530 + 14 * (1 - min(p, 1)), scale=0.94 + 0.06 * p, alpha=clamp(u / 0.08) * fade)


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
    while True:   # held end frame
        yield last


def render(frame_range=None, stills=None):
    E = build_elements()
    cap_cache = {}
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
        if frame_range and not (frame_range[0] <= n < frame_range[1]):
            continue
        if want is not None and n not in want:
            continue
        s, fx, fy = zoom_at(t)
        M = np.float32([[s, 0, fx - s * fx], [0, s, fy - s * fy]])
        img = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        img = grade(img, t)
        canvas = Image.fromarray(img).convert("RGBA")
        overlays(canvas, t, E, cap_cache)
        out = np.array(canvas.convert("RGB"))
        if want is not None:
            Image.fromarray(out).save(f"{OUT}_{t:05.2f}.jpg", quality=88)
            if n >= max(want):
                break
        else:
            enc.stdin.write(out.tobytes())
        if n % 60 == 0:
            print(f"frame {n}/{NF}", file=sys.stderr)
    if enc:
        enc.stdin.close()
        enc.wait()


if __name__ == "__main__":
    stills = None
    if "--still" in sys.argv:
        stills = [float(x) for x in sys.argv[sys.argv.index("--still") + 1].split(",")]
    render(stills=stills)
