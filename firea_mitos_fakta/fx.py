"""Shared drawing toolkit (cairo shapes, PIL text sprites, easing, photo cards).
Copied from firea_motion_ad/render.py so this project is self-contained.

Renders every frame with cairo (vector shapes, transforms) + PIL (text sprites)
and pipes raw BGRA frames into ffmpeg.
"""
import math
import os
import subprocess
import sys
from functools import lru_cache

import cairo
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from timeline import H, W

ROOT = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = f"{ROOT}/assets/fonts"
CUT = f"{ROOT}/assets/cut"

# ---------------------------------------------------------------- brand palette (from Firea posters)
BLUSH = (251, 239, 242)
BLUSH2 = (253, 246, 248)
PINK = (246, 212, 223)
ROSE = (224, 80, 127)
WINE = (110, 26, 51)
WINE_D = (82, 17, 37)
WHITE = (255, 255, 255)
SKY = (168, 210, 238)
SKIN = (238, 199, 176)

FONTS = dict(black="MontBlack", xb="MontXB", sb="MontSB", med="MontMed", serif="PlayfairBI", hand="Caveat")
MAXW = W - 2 * 96  # text safe width


def rgba(c, a=1.0):
    return (c[0] / 255, c[1] / 255, c[2] / 255, a)


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in(x):
    x = clamp(x)
    return x ** 3


def ease_io(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_back(x, s=1.70158):
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def prog(t, t0, dur):
    return clamp((t - t0) / dur)


def spring(x, freq=3.0, damp=5.0):
    """0 -> 1 with a damped overshoot."""
    if x <= 0:
        return 0.0
    return 1 - math.exp(-damp * x) * math.cos(2 * math.pi * freq * x)


# ---------------------------------------------------------------- PIL -> cairo
def pil_to_surface(im):
    im = im.convert("RGBA")
    w, h = im.size
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    buf = np.ndarray((h, s.get_stride() // 4, 4), np.uint8, buffer=s.get_data())
    a = np.asarray(im).astype(np.uint16)
    al = a[..., 3:4]
    pm = (a[..., :3] * al + 127) // 255
    buf[:, :w, 0] = pm[..., 2]
    buf[:, :w, 1] = pm[..., 1]
    buf[:, :w, 2] = pm[..., 0]
    buf[:, :w, 3] = a[..., 3]
    s.mark_dirty()
    return s


@lru_cache(None)
def font(name, size):
    return ImageFont.truetype(f"{FONT_DIR}/{FONTS[name]}.ttf", size)


class Sprite:
    def __init__(self, surf, adv, asc, desc, pad):
        self.surf, self.adv, self.asc, self.desc, self.pad = surf, adv, asc, desc, pad


@lru_cache(None)
def text_sprite(text, fname, size, color, track=0):
    f = font(fname, size)
    asc, desc = f.getmetrics()
    if track:
        adv = sum(f.getlength(ch) for ch in text) + track * (len(text) - 1)
    else:
        adv = f.getlength(text)
    pad = int(size * 0.35)
    im = Image.new("RGBA", (int(adv + 2 * pad), asc + desc + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if track:
        x = pad
        for ch in text:
            d.text((x, pad + asc), ch, font=f, fill=color + (255,), anchor="ls")
            x += f.getlength(ch) + track
    else:
        d.text((pad, pad + asc), text, font=f, fill=color + (255,), anchor="ls")
    return Sprite(pil_to_surface(im), adv, asc, desc, pad)


def blit(ctx, surf, x, y, ox, oy, sc=1.0, rot=0.0, alpha=1.0, sx=None, sy=None):
    """Paint surf so that its pixel (ox, oy) lands on (x, y)."""
    if alpha <= 0.002:
        return
    ctx.save()
    ctx.translate(x, y)
    if rot:
        ctx.rotate(rot)
    ctx.scale(sx if sx is not None else sc, sy if sy is not None else sc)
    ctx.set_source_surface(surf, -ox, -oy)
    ctx.get_source().set_filter(cairo.FILTER_GOOD)
    ctx.paint_with_alpha(alpha)
    ctx.restore()


# ---------------------------------------------------------------- shapes
def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def stroke_partial(ctx, p, width, color, alpha=1.0):
    """Stroke the current path up to fraction p of its length (draw-on effect)."""
    flat = ctx.copy_path_flat()
    L, last = 0.0, None
    for kind, pts in flat:
        if kind in (cairo.PATH_MOVE_TO,):
            last = pts
        elif kind == cairo.PATH_LINE_TO and last:
            L += math.hypot(pts[0] - last[0], pts[1] - last[1])
            last = pts
    ctx.set_line_width(width)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_source_rgba(*rgba(color, alpha))
    if p < 1:
        ctx.set_dash([max(0.01, L * p), L + 100])
    ctx.stroke()
    ctx.set_dash([])


def arrow(ctx, x0, y0, x1, y1, p, width, color, alpha=1.0, head=22, curve=0.0):
    if p <= 0:
        return
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    nx, ny = -(y1 - y0), (x1 - x0)
    cx, cy = mx + nx * curve, my + ny * curve
    ctx.move_to(x0, y0)
    ctx.curve_to(cx, cy, cx, cy, x1, y1)
    stroke_partial(ctx, p, width, color, alpha)
    if p > 0.85:
        a = math.atan2(y1 - cy, x1 - cx)
        k = ease_out((p - 0.85) / 0.15)
        for s in (-1, 1):
            ctx.move_to(x1, y1)
            ctx.line_to(x1 - head * k * math.cos(a + s * 0.5), y1 - head * k * math.sin(a + s * 0.5))
        stroke_partial(ctx, 1, width, color, alpha)


def droplet_path(ctx, r):
    ctx.move_to(0, -1.55 * r)
    ctx.curve_to(0.35 * r, -1.05 * r, r, -0.6 * r, r, 0)
    ctx.arc(0, 0, r, 0, math.pi)
    ctx.curve_to(-r, -0.6 * r, -0.35 * r, -1.05 * r, 0, -1.55 * r)
    ctx.close_path()


def draw_droplet(ctx, x, y, r, alpha=1.0, sx=1.0, sy=1.0, outline=WINE, fill=SKY, lw=None):
    if alpha <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sx, sy)
    droplet_path(ctx, r)
    g = cairo.LinearGradient(0, -1.5 * r, 0, r)
    g.add_color_stop_rgba(0, *rgba(WHITE, alpha))
    g.add_color_stop_rgba(1, *rgba(fill, alpha))
    ctx.set_source(g)
    ctx.fill_preserve()
    ctx.set_source_rgba(*rgba(outline, alpha))
    ctx.set_line_width(lw or max(2.5, r * 0.07))
    ctx.stroke()
    # shine
    ctx.set_source_rgba(1, 1, 1, 0.85 * alpha)
    ctx.save()
    ctx.translate(-0.42 * r, -0.05 * r)
    ctx.scale(0.16 * r, 0.32 * r)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    ctx.fill()
    ctx.restore()


def draw_sun(ctx, x, y, r, t, alpha=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(t * 0.6)
    ctx.set_source_rgba(*rgba((255, 196, 70), alpha))
    ctx.arc(0, 0, r, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_line_width(r * 0.22)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(8):
        a = i * math.pi / 4
        ctx.move_to(math.cos(a) * r * 1.4, math.sin(a) * r * 1.4)
        ctx.line_to(math.cos(a) * r * 1.85, math.sin(a) * r * 1.85)
    ctx.stroke()
    ctx.restore()


def draw_check(ctx, x, y, r, fill, mark, alpha=1.0):
    ctx.set_source_rgba(*rgba(fill, alpha))
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()
    ctx.move_to(x - r * 0.45, y + r * 0.02)
    ctx.line_to(x - r * 0.1, y + r * 0.38)
    ctx.line_to(x + r * 0.5, y - r * 0.35)
    stroke_partial(ctx, 1, r * 0.22, mark, alpha)


def sparkle(ctx, x, y, s, alpha, color=WHITE):
    """Four-point star."""
    if alpha <= 0 or s <= 0:
        return
    pts = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(*pts[0])
    for i in range(4):
        p0, p1 = pts[i], pts[(i + 1) % 4]
        c = (0.12 * (p0[0] + p1[0]), 0.12 * (p0[1] + p1[1]))
        ctx.curve_to(c[0], c[1], c[0], c[1], p1[0], p1[1])
    ctx.close_path()
    ctx.set_source_rgba(*rgba(color, alpha))
    ctx.fill()
    ctx.restore()


# ---------------------------------------------------------------- backgrounds
def bg_fill(ctx, t, base, blob_col, blob_alpha=0.55, seed=0):
    ctx.set_source_rgb(*rgba(base)[:3])
    ctx.rectangle(0, 0, W, H)  # respects transforms (push transition), unlike paint()
    ctx.fill()
    rng = np.random.default_rng(seed)
    for i in range(4):
        bx = rng.uniform(0, W) + math.sin(t * 0.35 + i * 1.7) * 60
        by = rng.uniform(0, H) + math.cos(t * 0.28 + i * 2.3) * 80
        br = rng.uniform(380, 620)
        g = cairo.RadialGradient(bx, by, 0, bx, by, br)
        g.add_color_stop_rgba(0, *rgba(blob_col, blob_alpha))
        g.add_color_stop_rgba(1, *rgba(blob_col, 0))
        ctx.set_source(g)
        ctx.arc(bx, by, br, 0, 2 * math.pi)
        ctx.fill()


def floating_drops(ctx, t, color, alpha, n=9, seed=3):
    rng = np.random.default_rng(seed)
    for i in range(n):
        x = rng.uniform(60, W - 60)
        speed = rng.uniform(28, 55)
        y = (rng.uniform(0, H) - t * speed) % (H + 200) - 100
        r = rng.uniform(9, 20)
        a = alpha * (0.5 + 0.5 * math.sin(t * 1.3 + i))
        draw_droplet(ctx, x + math.sin(t + i) * 10, y, r, alpha=a, outline=color, fill=color, lw=0.1)


# ---------------------------------------------------------------- kinetic text
class Tok:
    def __init__(self, text, style, hl=None, under=None):
        self.text, self.style, self.hl, self.under = text, style, hl, under


# style name -> (font, size, color[, tracking])
STY = {
    "h1": ("black", 84, WINE), "h1w": ("black", 92, WHITE),
    "xb": ("xb", 70, WINE), "xbw": ("xb", 70, WHITE), "xbr": ("xb", 44, ROSE),
    "sb": ("sb", 60, WINE), "sbw": ("sb", 62, WHITE),
    "med": ("med", 62, WINE), "medw": ("med", 68, WHITE), "meds": ("med", 42, WINE),
    "serif": ("serif", 104, ROSE), "serifm": ("serif", 82, ROSE), "serifp": ("serif", 86, PINK),
    "serifs": ("serif", 50, ROSE),
    "hand": ("hand", 58, WINE), "handp": ("hand", 60, PINK),
}


def layout(lines, cx, y_top, maxw=MAXW, lead=0.16, align="center"):
    """lines: list[list[Tok]] -> list of (tok, sprite, x, baseline). Auto-shrinks wide lines."""
    out = []
    y = y_top
    for line in lines:
        scale = 1.0
        for _ in range(6):
            sps = []
            for tk in line:
                fn, size, col = STY[tk.style][:3]
                sps.append(text_sprite(tk.text, fn, int(size * scale), col))
            space = [sp.asc * 0.30 for sp in sps]
            total = sum(sp.adv for sp in sps) + sum(space[:-1]) + sum(30 for tk in line if tk.hl)
            if total <= maxw:
                break
            scale *= maxw / total * 0.99
        asc = max(sp.asc for sp in sps)
        desc = max(sp.desc for sp in sps)
        hlpad = 14 if any(tk.hl for tk in line) else 0
        base = y + asc * 0.82 + hlpad
        x = cx - total / 2 if align == "center" else cx
        for tk, sp, spc in zip(line, sps, space):
            if tk.hl:
                x += 15
            out.append((tk, sp, x, base))
            x += sp.adv + spc + (15 if tk.hl else 0)
        y = base + desc * 0.55 + asc * lead + hlpad
    return out


def layout_bottom(placed):
    return max(b + sp.desc * 0.55 for _, sp, _, b in placed)


def draw_words(ctx, t, placed, start, stagger=0.1, dur=0.45, mode="rise", alpha=1.0):
    for i, (tk, sp, x, base) in enumerate(placed):
        t0 = start + i * stagger
        p = (t - t0) / dur
        if p <= 0:
            continue
        e = ease_out(p)
        a = clamp(p * 2.5) * alpha
        if mode == "rise":
            dy, sc = (1 - e) * 46, 0.92 + 0.08 * ease_back(p)
        else:  # pop
            dy, sc = 0, 0.55 + 0.45 * ease_back(p, 2.2)
        cx = x + sp.adv / 2
        cy = base - sp.asc * 0.32 + dy
        if tk.hl:
            hp = ease_out((t - t0 - 0.12) / 0.32)
            if hp > 0:
                padx, pady = 18, 10
                bx = x - padx
                by = base - sp.asc * 0.80 - pady
                bw = (sp.adv + 2 * padx) * hp
                bh = sp.asc * 0.80 + sp.desc * 0.30 + 2 * pady
                ctx.save()
                ctx.translate(x + sp.adv / 2, base - sp.asc * 0.3)
                ctx.rotate(-0.018)
                ctx.translate(-(x + sp.adv / 2), -(base - sp.asc * 0.3))
                rrect(ctx, bx, by + dy * 0.3, bw, bh, 14)
                ctx.set_source_rgba(*rgba(tk.hl, a))
                ctx.fill()
                ctx.restore()
        blit(ctx, sp.surf, cx, cy, sp.pad + sp.adv / 2, sp.pad + sp.asc - sp.asc * 0.32, sc=sc, alpha=a)
        if tk.under:
            up = ease_out((t - t0 - 0.25) / 0.45)
            if up > 0:
                y0 = base + sp.desc * 0.35
                ctx.move_to(x - 6, y0 + 4)
                ctx.curve_to(x + sp.adv * 0.3, y0 - 8, x + sp.adv * 0.7, y0 + 12, x + sp.adv + 8, y0 - 2)
                stroke_partial(ctx, up, 9, tk.under, a)


def chip(ctx, t, t0, text, cx, cy, fill=ROSE, color=WHITE, size=34):
    p = prog(t, t0, 0.4)
    if p <= 0:
        return
    sp = text_sprite(text, "xb", size, color, 3)
    w, h = sp.adv + 64, sp.asc + 34
    sc = 0.4 + 0.6 * ease_back(p, 2.4)
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(sc, sc)
    rrect(ctx, -w / 2, -h / 2, w, h, h / 2)
    ctx.set_source_rgba(*rgba(fill, clamp(p * 3)))
    ctx.fill()
    ctx.restore()
    blit(ctx, sp.surf, cx, cy, sp.pad + sp.adv / 2, sp.pad + sp.asc * 0.62, sc=sc, alpha=clamp(p * 3))


# ---------------------------------------------------------------- photos
@lru_cache(None)
def photo_surface(name, w, h, zoom=1.14):
    im = Image.open(f"{CUT}/{name}.jpg").convert("RGB")
    tw, th = int(w * zoom), int(h * zoom)
    s = max(tw / im.width, th / im.height)
    im = im.resize((int(im.width * s + 1), int(im.height * s + 1)), Image.LANCZOS)
    l, tp = (im.width - tw) // 2, (im.height - th) // 2
    return pil_to_surface(im.crop((l, tp, l + tw, tp + th)))


@lru_cache(None)
def shadow_surface(w, h, r, blur=26, alpha=90):
    pad = blur * 3
    im = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((pad, pad, pad + w, pad + h), r, fill=(70, 10, 30, alpha))
    return pil_to_surface(im.filter(ImageFilter.GaussianBlur(blur))), pad


def photo_card(ctx, name, cx, cy, w, h, rot=0.0, sc=1.0, inner_zoom=1.0, alpha=1.0, border=14, r=34):
    """White-bordered rounded photo with drop shadow; inner_zoom >= 1 fills the frame."""
    if alpha <= 0:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(rot)
    ctx.scale(sc, sc)
    ctx.push_group()
    sh, pad = shadow_surface(w + 2 * border, h + 2 * border, r + border)
    blit(ctx, sh, 0, 22, pad + (w + 2 * border) / 2, pad + (h + 2 * border) / 2)
    rrect(ctx, -w / 2 - border, -h / 2 - border, w + 2 * border, h + 2 * border, r + border)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()
    rrect(ctx, -w / 2, -h / 2, w, h, r)
    ctx.clip()
    ps = photo_surface(name, w, h)
    pw, ph = ps.get_width(), ps.get_height()
    blit(ctx, ps, 0, 0, pw / 2, ph / 2, sc=max(inner_zoom, 1.0) / 1.14)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(alpha)
    ctx.restore()


@lru_cache(None)
def logo_surface(color, width):
    a = Image.open(f"{CUT}/logo_alpha.png")
    h = int(a.height * width / a.width)
    a = a.resize((width, h), Image.LANCZOS)
    im = Image.new("RGBA", a.size, color + (0,))
    im.putalpha(a)
    return pil_to_surface(im)


def sticker(ctx, t, t0, text, cx, cy, rot, style="hand", fill=WHITE, icon=None):
    p = prog(t, t0, 0.45)
    if p <= 0:
        return
    fn, size, col = STY[style][:3]
    sp = text_sprite(text, fn, size, col)
    ix = 70 if icon else 0
    w, h = sp.adv + 56 + ix, sp.asc + sp.desc + 18
    sc = 0.3 + 0.7 * ease_back(p, 2.6)
    wob = math.sin((t - t0) * 2.2) * 0.02
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(rot + wob)
    ctx.scale(sc, sc)
    sh, pad = shadow_surface(int(w), int(h), 22, 14, 60)
    blit(ctx, sh, 0, 10, pad + w / 2, pad + h / 2)
    rrect(ctx, -w / 2, -h / 2, w, h, 22)
    ctx.set_source_rgb(*rgba(fill)[:3])
    ctx.fill()
    if icon == "sun":
        draw_sun(ctx, -w / 2 + 50, 0, 17, t)
    blit(ctx, sp.surf, -w / 2 + 28 + ix + sp.adv / 2, 0, sp.pad + sp.adv / 2, sp.pad + (sp.asc + sp.desc) * 0.55)
    ctx.restore()


