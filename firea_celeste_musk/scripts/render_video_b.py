"""Style B — "Fresh Kinetic" picture render.

Usage: python render_video_b.py <project_dir> <out.mp4> [--still t1,t2,...]
Big word-chunk captions, jump-zooms per phrase, drawn icons (sun, sweat drops,
odour lines, no-sign, sparkles), whip-pan into a bottle hero, top progress bar.
"""
import math
import os
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import cues_b as C  # noqa: E402

P, OUT = sys.argv[1], sys.argv[2]
W, H, FPS = 1080, 1920, 30
NF = int(round(C.DURATION * FPS))

INK = (26, 14, 20)
PINK = (255, 79, 154)
PINK_SOFT = (255, 214, 232)
WHITE = (255, 255, 255)
YELLOW = (255, 214, 64)
BLUE = (88, 186, 255)
ODOUR = (150, 190, 70)
RED = (232, 44, 60)
GREEN = (40, 170, 100)


def F(name, size):
    files = {"xb": "Poppins-ExtraBold", "b": "Poppins-Bold", "sb": "Poppins-SemiBold", "serif": "DMSerifDisplay-Italic"}
    return ImageFont.truetype(f"{P}/assets/fonts/{files[name]}.ttf", size)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def e_out(x):
    return 1 - (1 - clamp(x)) ** 3


def e_inout(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def e_back(x):
    x = clamp(x)
    c1 = 2.2
    return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2


def window(t, t0, t1, fin=0.12, fout=0.12):
    if t < t0 or t > t1:
        return 0.0
    return min(clamp((t - t0) / fin), clamp((t1 - t) / fout))


def shadowed(img, blur=16, offset=(0, 10), alpha=110, pad=40):
    w, h = img.size
    a = np.array(img.split()[-1]).astype(np.float32) * alpha / 255
    sh = np.zeros((h + 2 * pad, w + 2 * pad), np.float32)
    sh[pad + offset[1]:pad + offset[1] + h, pad + offset[0]:pad + offset[0] + w] = a
    sh = cv2.GaussianBlur(sh, (0, 0), blur)
    can = Image.fromarray(np.dstack([np.full_like(sh, 20), np.full_like(sh, 5), np.full_like(sh, 12), sh]).astype(np.uint8), "RGBA")
    can.alpha_composite(img, (pad, pad))
    return can


def pill(text, font, fg, bg, padx=34, pady=18, radius=None):
    b = font.getbbox(text)
    asc, desc = font.getmetrics()
    h = asc + desc + 2 * pady - 10
    w = b[2] - b[0] + 2 * padx
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius if radius is not None else h // 2, fill=bg)
    d.text((padx - b[0], (h - (asc + desc)) // 2 + 2), text, font=font, fill=fg)
    return im


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


# ---------------------------------------------------------------- captions
def caption_image(text):
    f = F("xb", 96)
    sw = 11
    words = text.split(" ")
    colors = [WHITE] * len(words)
    low = [w.strip(",.?!") for w in words]
    for h in C.PINK_WORDS:
        hw = h.split(" ")
        for i in range(len(words) - len(hw) + 1):
            if low[i:i + len(hw)] == hw:
                for j in range(i, i + len(hw)):
                    colors[j] = PINK
    space = f.getlength(" ")
    # wrap to <= 920px, max 2 lines
    lines, cur, curw = [], [], 0
    for wd, col in zip(words, colors):
        wl = f.getlength(wd)
        if cur and curw + space + wl > 920:
            lines.append(cur)
            cur, curw = [], 0
        cur.append((wd, col, wl))
        curw += (space if len(cur) > 1 else 0) + wl
    lines.append(cur)
    assert len(lines) <= 2, text
    asc, desc = f.getmetrics()
    lh = asc + desc - 14
    widths = [sum(w for _, _, w in ln) + space * (len(ln) - 1) for ln in lines]
    cw, ch = int(max(widths)) + 2 * sw + 20, lh * len(lines) + 2 * sw + 20
    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for li, ln in enumerate(lines):
        x = (cw - widths[li]) / 2
        for wd, col, wl in ln:
            d.text((x, sw + 6 + li * lh), wd, font=f, fill=col, stroke_width=sw, stroke_fill=INK)
            x += wl + space
    return shadowed(im, blur=10, offset=(0, 8), alpha=120)


# ---------------------------------------------------------------- drawn icons
def draw_sun(d, cx, cy, r, t):
    for k in range(12):
        a = t * 1.2 + k * math.pi / 6
        r0, r1 = r * 1.25, r * (1.65 if k % 2 == 0 else 1.5)
        d.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))],
               fill=YELLOW + (255,), width=max(3, int(r * 0.16)))
    d.ellipse([cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6], fill=INK + (255,))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=YELLOW + (255,))


def draw_drop(d, cx, cy, s, color=BLUE, alpha=255):
    pts = [(cx, cy - 1.7 * s)] + [(cx + s * math.cos(math.radians(a)), cy + s * math.sin(math.radians(a))) for a in range(-20, 201, 10)]
    d.polygon(pts, fill=color + (alpha,), outline=INK + (alpha,), width=max(2, int(s * 0.18)))
    d.ellipse([cx - s * 0.45, cy - s * 0.2, cx - s * 0.15, cy + s * 0.25], fill=(255, 255, 255, int(alpha * 0.8)))


def draw_stink(d, x, y0, length, phase, alpha=255, width=12):
    pts = [(x + 26 * math.sin(phase + k * 0.09), y0 - k * length / 60) for k in range(60)]
    d.line(pts, fill=INK + (alpha,), width=width + 8, joint="curve")
    d.line(pts, fill=ODOUR + (alpha,), width=width, joint="curve")


def draw_sparkle(d, cx, cy, s, alpha=255, color=WHITE):
    if s <= 1:
        return
    k = s * 0.22
    pts = [(cx, cy - s), (cx + k, cy - k), (cx + s, cy), (cx + k, cy + k), (cx, cy + s), (cx - k, cy + k), (cx - s, cy), (cx - k, cy - k)]
    d.polygon(pts, fill=color + (alpha,))


def draw_check_badge(d, cx, cy, r):
    d.ellipse([cx - r - 7, cy - r - 7, cx + r + 7, cy + r + 7], fill=WHITE + (255,))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GREEN + (255,))
    d.line([(cx - r * 0.45, cy + r * 0.02), (cx - r * 0.1, cy + r * 0.38), (cx + r * 0.5, cy - r * 0.35)],
           fill=WHITE + (255,), width=int(r * 0.24), joint="curve")


def draw_no_sign(d, cx, cy, r, phase):
    d.ellipse([cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10], fill=WHITE + (235,))
    for k, dx in enumerate((-r * 0.35, 0, r * 0.35)):
        draw_stink(d, cx + dx, cy + r * 0.55, r * 1.1, phase + k, width=8)
    w = int(r * 0.2)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=RED + (255,), width=w)
    k = r * 0.68
    d.line([(cx - k, cy - k), (cx + k, cy + k)], fill=RED + (255,), width=w)


# ---------------------------------------------------------------- static elements
def build_elements():
    E = {}
    b = Image.open(f"{P}/assets/bottle.png").convert("RGBA")
    a = np.array(b.split()[-1])
    pad = 18
    big = np.zeros((a.shape[0] + 2 * pad, a.shape[1] + 2 * pad), np.uint8)
    big[pad:-pad, pad:-pad] = a
    outline = cv2.dilate(big, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (29, 29)))
    st = Image.new("RGBA", (big.shape[1], big.shape[0]), (0, 0, 0, 0))
    st.paste(Image.new("RGBA", st.size, WHITE + (255,)), (0, 0), Image.fromarray(outline))
    st.alpha_composite(b, (pad, pad))
    E["bottle"] = shadowed(st, blur=22, offset=(0, 16), alpha=140)
    # end banner
    bw, bh = 640, 250
    ban = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(ban)
    d.rounded_rectangle([0, 0, bw - 1, bh - 1], radius=40, fill=PINK + (255,))
    d.text((40, 52), "PAKAI JE", font=F("xb", 40), fill=INK, anchor="ls")
    d.text((36, 170), "Firea", font=F("serif", 140), fill=WHITE, anchor="ls")
    d.text((40, 222), "CELESTE MUSK  ·  ROLL-ON 50ML", font=F("b", 30), fill=WHITE, anchor="ls")
    E["banner"] = shadowed(ban)
    E["cta"] = shadowed(pill(C.CTA_TEXT + "  ›", F("xb", 42), INK, YELLOW, padx=36, pady=20), alpha=130)
    cl = Image.new("RGBA", (560, 60), (0, 0, 0, 0))
    x = 0
    for txt in ("0% ALKOHOL", "0% PARABEN"):
        c = pill(txt, F("b", 30), INK, WHITE + (255,), padx=20, pady=10)
        cl.alpha_composite(c, (x, (60 - c.height) // 2))
        x += c.width + 14
    E["claims"] = cl
    return E


# ---------------------------------------------------------------- camera
def scale_at(t):
    s = C.JUMPS[0][1]
    t0 = 0
    for jt, js in C.JUMPS:
        if t >= jt:
            s, t0 = js, jt
    return s + 0.012 * (t - t0)   # slow drift inside the phrase


def focus_y(t):
    return 700 if t < C.SCENE_CUT else 900


def shake_at(t):
    dx = dy = 0.0
    for s0 in C.SHAKE:
        u = t - s0
        if 0 <= u < 0.45:
            k = math.exp(-u * 9) * 18
            dx += math.sin(u * 70) * k
            dy += math.cos(u * 53) * k * 0.6
    return dx, dy


yy, xx = np.mgrid[0:H, 0:W]
VIG = (1 - 0.2 * (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.45) / (H * 0.7)) ** 2))[..., None].astype(np.float32)


def camera(fr, t):
    s = scale_at(t)
    fx, fy = 540, focus_y(t)
    dx, dy = shake_at(t)
    # whip-pan: slide out left before the cut, slide in from right after it
    w0, w1 = C.WHIP
    whip = 0.0
    if w0 <= t < C.SCENE_CUT:
        u = (t - w0) / (C.SCENE_CUT - w0)
        dx -= W * 0.55 * u ** 2
        whip = u
    elif C.SCENE_CUT <= t < w1:
        u = (t - C.SCENE_CUT) / (w1 - C.SCENE_CUT)
        dx += W * 0.55 * (1 - e_out(u))
        whip = 1 - u
    M = np.float32([[s, 0, fx - s * fx + dx], [0, s, fy - s * fy + dy]])
    img = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    if whip > 0.02:
        k = int(4 + whip * 90) | 1
        img = cv2.blur(img, (k, 1))
    f = img.astype(np.float32)
    g0, g1 = C.GRADE_COOL
    k = min(clamp((t - g0) / 0.5), 1.0 if t < g1 else 0.0) * 0.6
    if k > 0:
        gray = f.mean(axis=2, keepdims=True)
        f = f * (1 - k * 0.75) + gray * (k * 0.75)
        f[..., 2] *= 1 + 0.07 * k
        f *= 1 - 0.1 * k
    else:
        # punchier, warmer look for the rest
        f = (f - 128) * 1.06 + 128 + np.array([4, 0, -2], np.float32)
    if C.GLITCH[0] <= t < C.GLITCH[1]:
        o = int(14 * math.sin((t - C.GLITCH[0]) * 40)) + 8
        f[..., 0] = np.roll(f[..., 0], o, axis=1)
        f[..., 2] = np.roll(f[..., 2], -o, axis=1)
    f *= VIG
    return np.clip(f, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- overlays
rng = np.random.default_rng(11)
DROP_SEEDS = [(rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(0.7, 1.2)) for _ in range(10)]
SPARK_SEEDS = [(rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(0.5, 1.2)) for _ in range(16)]


def side_x(u):
    """keep drops/odour lines on the sides, off the face."""
    return 60 + u * 200 if u < 0.5 else 820 + (u - 0.5) * 400


def overlays(canvas, t, E, cache):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # progress bar
    d.rectangle([0, 0, W, 12], fill=(0, 0, 0, 90))
    d.rectangle([0, 0, int(W * clamp(t / C.DURATION)), 12], fill=PINK + (255,))
    # sun
    a = window(t, *C.SUN)
    if a:
        p = e_back((t - C.SUN[0]) / 0.35)
        draw_sun(d, 900, 250, 62 * p, t)
    # sweat drops
    for i, (t0, t1) in enumerate(C.DROPS):
        if t0 <= t <= t1:
            wiped = (i == 1 and t >= C.SPARKLE_WIPE[0][0])
            for k, (ux, uy, sz) in enumerate(DROP_SEEDS):
                u = (t - t0) * 0.9 + uy
                y = 250 + ((u * 420) % 700)
                x = side_x(ux)
                al = int(255 * window(t, t0, t1, 0.15, 0.15))
                if wiped:
                    q = clamp((t - C.SPARKLE_WIPE[0][0]) / 0.3)
                    draw_sparkle(d, x, y, 34 * sz * math.sin(math.pi * q), int(255 * (1 - q * 0.3)), YELLOW if k % 2 else WHITE)
                    continue
                draw_drop(d, x, y, 22 * sz, alpha=al)
    # odour lines rising from the shoulders
    for i, (t0, t1) in enumerate(C.STINK):
        if t0 <= t <= t1:
            al = window(t, t0, t1, 0.15, 0.15)
            if i == 2 and t >= C.SPARKLE_WIPE[1][0]:
                q = clamp((t - C.SPARKLE_WIPE[1][0]) / 0.35)
                al *= 1 - q
                for k, (sx, sy, sz) in enumerate(SPARK_SEEDS[:10]):
                    x = 940 + sx * 90
                    draw_sparkle(d, x, 1000 + sy * 200, 40 * sz * math.sin(math.pi * q), 255, YELLOW if k % 3 else WHITE)
            grow = e_out((t - t0) / 0.4)
            xs = (110, 190, 890, 970) if t < C.SCENE_CUT else (860, 940, 1020)   # keep the held bottle clear
            for k, x in enumerate(xs):
                draw_stink(d, x, 1260, 330 * grow, t * 5 + k, alpha=int(255 * al))
    # no-sign
    a = window(t, *C.NO_SIGN)
    if a:
        p = e_back((t - C.NO_SIGN[0]) / 0.3)
        draw_no_sign(d, 190, 330, 110 * p, t * 5)
    # ✓ badge on TAKPE
    a = window(t, *C.OK_BADGE)
    if a:
        p = e_back((t - C.OK_BADGE[0]) / 0.3)
        draw_check_badge(d, 900, 300, 80 * p)
    canvas.alpha_composite(layer)

    # bottle: hero centre -> flies to badge (top-right) -> end card (top-left)
    if C.HERO[0] <= t:
        h0, h1 = C.HERO
        if t < h1:
            p = e_back((t - h0) / 0.35)
            q = 0.0
        else:
            p = 1.0
            q = e_inout((t - h1) / 0.4)
        sc = 0.78 * p * (1 - q) + 0.42 * q
        cx = 540 * (1 - q) + 940 * q
        cy = 470 * (1 - q) + 300 * q
        if t >= C.END:
            r = e_inout((t - C.END) / 0.45)
            sc = 0.42 * (1 - r) + 0.5 * r
            cx = 940 * (1 - r) + 150 * r
            cy = 300 * (1 - r) + 360 * r
        if t < h1 + 0.4:   # glow + burst behind the hero
            gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            gd = ImageDraw.Draw(gl)
            g = (1 - q) * clamp((t - h0) / 0.15)
            for rr, al in ((380, 55), (270, 85), (180, 115)):
                gd.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=PINK_SOFT + (int(al * g),))
            for k, (sx, sy, sz) in enumerate(SPARK_SEEDS):
                u = clamp((t - h0) / 0.6)
                draw_sparkle(gd, cx + sx * 380 * e_out(u), cy + sy * 420 * e_out(u), 30 * sz * math.sin(math.pi * u), int(255 * g), YELLOW if k % 2 else WHITE)
            canvas.alpha_composite(gl)
        bob = math.sin(t * 2.6) * 6
        place(canvas, E["bottle"], cx, cy + bob, scale=sc, rot=-8 * q + 8 * (1 - p))

    # end card
    if t >= C.END:
        u = t - C.END
        p = e_back(u / 0.4)
        place(canvas, E["banner"], 640 + 300 * (1 - e_out(u / 0.4)), 300, scale=0.8 + 0.2 * p)
        if t >= C.CLAIMS:
            q = e_out((t - C.CLAIMS) / 0.3)
            place(canvas, E["claims"], 610, 470 + 12 * (1 - q), alpha=q)
        if t >= C.CTA:
            q = e_back((t - C.CTA) / 0.35)
            pulse = 1 + 0.035 * math.sin((t - C.CTA) * 7) * clamp((t - C.CTA - 0.4) / 0.4)
            place(canvas, E["cta"], 540, 590, scale=(0.5 + 0.5 * q) * pulse)

    # kinetic captions
    cur = None
    for i, (s, txt) in enumerate(C.CHUNKS):
        e = C.CHUNKS[i + 1][0] if i + 1 < len(C.CHUNKS) else C.CAPTION_END
        if s <= t < e:
            cur = (i, s, txt)
    if cur and not (C.HERO[0] <= t < C.HERO[1] - 0.1 and cur[2] in ("FIREA",)):
        i, s, txt = cur
        if txt not in cache:
            cache[txt] = caption_image(txt)
        u = t - s
        p = e_back(u / 0.16)
        rot = (-2.5, 1.5, -1, 2.5, 0)[i % 5]
        cy = 1420 if t < C.SCENE_CUT else 1460
        fade = clamp((C.CAPTION_END - t) / 0.2)
        place(canvas, cache[txt], 540, cy, scale=1.25 - 0.25 * p, alpha=clamp(u / 0.05) * fade, rot=rot)


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
    E = build_elements()
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
        canvas = Image.fromarray(camera(fr, t)).convert("RGBA")
        overlays(canvas, t, E, cache)
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
