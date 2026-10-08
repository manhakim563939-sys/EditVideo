"""Shared drawing toolkit for the 5 Firea concept videos (cairo shapes, PIL text sprites,
easing, photo cards, hijabi figure, bubbles, stickers, transitions, render runner).

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

W, H, FPS = 1080, 1920, 30

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

FONTS = dict(black="MontBlack", xb="MontXB", sb="MontSB", med="MontMed", serif="PlayfairBI", hand="Caveat",
             brico="Bricolage", pixel="VT323")
MAXW = W - 2 * 96  # text safe width


def sscale(ctx, sx, sy):
    """ctx.scale that never produces a singular matrix (scale 0 at the very first frame of a pop-in)."""
    ctx.scale(sx if abs(sx) > 1e-3 else 1e-3, sy if abs(sy) > 1e-3 else 1e-3)


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
    if alpha <= 0.002 or abs(sx if sx is not None else sc) < 1e-3 or abs(sy if sy is not None else sc) < 1e-3:
        return
    ctx.save()
    ctx.translate(x, y)
    if rot:
        ctx.rotate(rot)
    sscale(ctx, sx if sx is not None else sc, sy if sy is not None else sc)
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
    sscale(ctx, sx, sy)
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
    sscale(ctx, 0.16 * r, 0.32 * r)
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
    sscale(ctx, s, s)
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
    sscale(ctx, sc, sc)
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
    sscale(ctx, sc, sc)
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
    sscale(ctx, sc, sc)
    sh, pad = shadow_surface(int(w), int(h), 22, 14, 60)
    blit(ctx, sh, 0, 10, pad + w / 2, pad + h / 2)
    rrect(ctx, -w / 2, -h / 2, w, h, 22)
    ctx.set_source_rgb(*rgba(fill)[:3])
    ctx.fill()
    if icon == "sun":
        draw_sun(ctx, -w / 2 + 50, 0, 17, t)
    blit(ctx, sp.surf, -w / 2 + 28 + ix + sp.adv / 2, 0, sp.pad + sp.adv / 2, sp.pad + (sp.asc + sp.desc) * 0.55)
    ctx.restore()




# ================================================================ extras for the concept videos
YELLOW = (255, 214, 102)
GREEN = (34, 150, 108)
RED = (222, 64, 64)
CREAM = (250, 244, 236)
SKIN2 = (232, 190, 165)

STY.update({
    "brico": ("brico", 96, WINE), "bricow": ("brico", 96, WHITE), "bricor": ("brico", 96, ROSE),
    "bricos": ("brico", 72, WINE), "bricosw": ("brico", 72, WHITE),
    "slogan": ("serif", 50, ROSE),
})


def solid(ctx, col):
    ctx.set_source_rgb(*rgba(col)[:3])
    ctx.rectangle(0, 0, W, H)
    ctx.fill()


def vgrad(ctx, y0, y1, col, a0, a1):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgba(0, *rgba(col, a0))
    g.add_color_stop_rgba(1, *rgba(col, a1))
    ctx.set_source(g)
    ctx.rectangle(0, min(y0, y1), W, abs(y1 - y0))
    ctx.fill()


def full_photo(ctx, name, zoom, dx=0, dy=0):
    ps = photo_surface(name, W, H)
    blit(ctx, ps, W / 2 + dx, H / 2 + dy, ps.get_width() / 2, ps.get_height() / 2, sc=max(zoom, 1.0) / 1.14)


def label(ctx, text, style, x, y, alpha=1.0, sc=1.0, rot=0.0, anchor="c"):
    """Draw a single text sprite centred (anchor c) or left-aligned (anchor l) on (x, y)."""
    fn, size, col = STY[style][:3]
    sp = text_sprite(text, fn, size, col)
    ox = sp.pad + (sp.adv / 2 if anchor == "c" else 0)
    blit(ctx, sp.surf, x, y, ox, sp.pad + sp.asc * 0.62, sc=sc, rot=rot, alpha=alpha)
    return sp


def pop_label(ctx, t, t0, text, style, x, y, rot=0.0, dur=0.4, anchor="c"):
    p = prog(t, t0, dur)
    if p > 0:
        label(ctx, text, style, x, y + (1 - ease_out(p)) * 24, alpha=clamp(p * 3), sc=0.85 + 0.15 * ease_back(p),
              rot=rot, anchor=anchor)


def pill(ctx, t, t0, text, x, y, fill, col, size=44, rot=0.0, font_="brico", outline=True, icon=None, h=None):
    """Sticker-style pill that pops in."""
    p = prog(t, t0, 0.35)
    if p <= 0:
        return
    sp = text_sprite(text, font_, size, col)
    ix = 64 if icon else 0
    hh = h or int(size * 2.0)
    w = sp.adv + 56 + ix
    sc = 0.3 + 0.7 * ease_back(p, 2.6)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot + math.sin(t * 2 + x * 0.01) * 0.012)
    sscale(ctx, sc, sc)
    sh, pad = shadow_surface(int(w), hh, hh // 3, 12, 60)
    blit(ctx, sh, 0, 10, pad + w / 2, pad + hh / 2)
    if outline:
        rrect(ctx, -w / 2 - 7, -hh / 2 - 7, w + 14, hh + 14, hh / 3 + 6)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
    rrect(ctx, -w / 2, -hh / 2, w, hh, hh / 3)
    ctx.set_source_rgba(*rgba(fill))
    ctx.fill()
    if icon == "check":
        draw_check(ctx, -w / 2 + 44, 0, 22, GREEN if fill != GREEN else WHITE, WHITE if fill != GREEN else GREEN)
    elif icon == "cross":
        ctx.arc(-w / 2 + 44, 0, 22, 0, 2 * math.pi)
        ctx.set_source_rgba(*rgba(RED))
        ctx.fill()
        for s_ in (-1, 1):
            ctx.move_to(-w / 2 + 44 - 9, -9 * s_)
            ctx.line_to(-w / 2 + 44 + 9, 9 * s_)
        stroke_partial(ctx, 1, 5, WHITE)
    blit(ctx, sp.surf, -w / 2 + 28 + ix + sp.adv / 2, 0, sp.pad + sp.adv / 2, sp.pad + sp.asc * 0.6)
    ctx.restore()


@lru_cache(None)
def bottle_surface(height):
    b = Image.open(f"{CUT}/bottle.png").convert("RGBA")
    s = height / b.height
    b = b.resize((int(b.width * s), int(b.height * s)), Image.LANCZOS)
    pad = 60
    size = (b.width + 2 * pad, b.height + 2 * pad)
    al = Image.new("L", size, 0)
    al.paste(b.getchannel("A"), (pad, pad))
    outline = al.filter(ImageFilter.GaussianBlur(7)).point(lambda v: 255 if v > 18 else 0).filter(
        ImageFilter.GaussianBlur(1.2))
    sh = Image.new("RGBA", size, (90, 15, 40, 0))
    sh.putalpha(outline.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.35)))
    wh = Image.new("RGBA", size, (255, 255, 255, 0))
    wh.putalpha(outline)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.alpha_composite(sh, (0, 16))
    out.alpha_composite(wh)
    out.alpha_composite(b, (pad, pad))
    return pil_to_surface(out)


def bottle_drop(ctx, t, t0, x, y, height, float_amp=8):
    """Bottle falls in with a springy settle, then floats gently."""
    p = prog(t, t0, 0.5)
    if p <= 0:
        return
    k = t - t0
    yy = y - (1 - spring(k * 1.4, 1.2, 4.5)) * 800
    rot = 0.05 * (1 - spring(k * 1.4, 1.0, 4.0)) + math.sin(t * 1.4) * 0.015
    bs = bottle_surface(height)
    blit(ctx, bs, x, yy + math.sin(t * 1.6) * float_amp, bs.get_width() / 2, bs.get_height() / 2, rot=rot,
         alpha=clamp(p * 4))


def sunburst(ctx, cx, cy, t, col, alpha, n=16):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(t * 0.12)
    for i in range(n):
        a0 = i * 2 * math.pi / n
        ctx.move_to(0, 0)
        ctx.arc(0, 0, 1500, a0, a0 + math.pi / n)
        ctx.close_path()
    ctx.set_source_rgba(*rgba(col, alpha))
    ctx.fill()
    ctx.restore()


def glow(ctx, x, y, r, col, a):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, *rgba(col, a))
    g.add_color_stop_rgba(1, *rgba(col, 0))
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()


def logo(ctx, t, t0, x, y, width, color=WINE):
    lp = prog(t, t0, 0.6)
    if lp <= 0:
        return
    ls = logo_surface(color, width)
    ctx.save()
    ctx.rectangle(x - width / 2 - 20, y - 200, (width + 40) * ease_io(lp), 400)
    ctx.clip()
    blit(ctx, ls, x, y, ls.get_width() / 2, ls.get_height() / 2, sc=0.94 + 0.06 * ease_out(lp))
    ctx.restore()


def _band(ctx, c0, c1, col):
    if c1 <= c0:
        return
    ctx.move_to(c0, 0)
    ctx.line_to(c1, 0)
    ctx.line_to(c1 - H, H)
    ctx.line_to(c0 - H, H)
    ctx.close_path()
    ctx.set_source_rgba(*rgba(col))
    ctx.fill()


def wipe(ctx, p, col, cover, edge=None):
    """Diagonal wipe along x + y = c (cover: grows from bottom-right; else retreats top-left)."""
    edge = edge or YELLOW
    c = (W + H) * (1 - p)
    if cover:
        _band(ctx, c, W + H + 400, col)
        _band(ctx, c - 70, c, edge)
    else:
        _band(ctx, -400, c - 70, col)
        _band(ctx, c - 70, c, edge)


def panel_wipe(ctx, t, T, col, col2, d=0.3):
    """Vertical panel transition overlay around cut time T; returns True while active."""
    if T - d <= t < T:
        p = ease_io(prog(t, T - d, d))
        top = H * (1 - p)
        ctx.rectangle(0, top + 60, W, H)
        ctx.set_source_rgba(*rgba(col))
        ctx.fill()
        ctx.rectangle(0, top, W, 61)
        ctx.set_source_rgba(*rgba(col2))
        ctx.fill()
    elif T <= t < T + d:
        p = ease_io(prog(t, T, d))
        bot = H * (1 - p)
        ctx.rectangle(0, 0, W, bot - 60)
        ctx.set_source_rgba(*rgba(col))
        ctx.fill()
        ctx.rectangle(0, bot - 60, W, 60)
        ctx.set_source_rgba(*rgba(col2))
        ctx.fill()


# ---------------------------------------------------------------- illustrated hijabi figure
def _limb(ctx, x0, y0, a1, l1, a2, l2, width, col, hand_col, hand_r):
    """Arm from shoulder (x0,y0). Angles in radians: 0 = straight down, +pi/2 = toward +x, pi = up."""
    x1 = x0 + math.sin(a1) * l1
    y1 = y0 + math.cos(a1) * l1
    x2 = x1 + math.sin(a2) * l2
    y2 = y1 + math.cos(a2) * l2
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(x0, y0)
    ctx.line_to(x1, y1)
    ctx.line_to(x2, y2)
    ctx.set_line_width(width + 8)
    ctx.set_source_rgba(*rgba(tuple(max(0, c - 40) for c in col)))
    ctx.stroke_preserve()
    ctx.set_line_width(width)
    ctx.set_source_rgba(*rgba(col))
    ctx.stroke()
    ctx.arc(x2, y2, hand_r, 0, 2 * math.pi)
    ctx.set_source_rgba(*rgba(hand_col))
    ctx.fill()
    return x1, y1, x2, y2


def figure(ctx, x, y, s=1.0, arm_l=(0.15, 0.08), arm_r=(0.15, 0.08), outfit=ROSE, hijab=WINE, skin=SKIN,
           mood="neutral", sweat=0.0, t=0.0, flip=False, skirt=None):
    """Simple flat hijabi woman, long sleeves. (x, y) = feet centre. Height ~ 760*s.
    arm_l / arm_r = (upper-arm angle, forearm angle), measured outward: 0 down, pi/2 sideways, pi up."""
    ctx.save()
    ctx.translate(x, y)
    sscale(ctx, -s if flip else s, s)
    ctx.translate(0, -760)
    skirt = skirt or tuple(max(0, c - 55) for c in outfit)
    # legs / skirt
    ctx.move_to(-95, 420)
    ctx.line_to(95, 420)
    ctx.line_to(120, 760)
    ctx.line_to(-120, 760)
    ctx.close_path()
    ctx.set_source_rgba(*rgba(skirt))
    ctx.fill()
    # body (long-sleeve top)
    rrect(ctx, -112, 150, 224, 300, 60)
    ctx.set_source_rgba(*rgba(outfit))
    ctx.fill()
    # arms
    hand = skin
    for side, (a1, a2) in ((-1, arm_l), (1, arm_r)):
        _limb(ctx, side * 92, 185, side * a1, 150, side * a2, 140, 58, outfit, hand, 24)
    # hijab (head + cape over shoulders)
    ctx.move_to(-150, 215)
    ctx.curve_to(-150, 120, -120, 40, -86, 10)
    ctx.arc(0, -10, 92, math.pi * 1.0, math.pi * 2.0)
    ctx.curve_to(120, 40, 150, 120, 150, 215)
    ctx.curve_to(70, 250, -70, 250, -150, 215)
    ctx.close_path()
    ctx.set_source_rgba(*rgba(hijab))
    ctx.fill()
    # wet patch under a raised sleeve (drawn over the cape edge so it stays visible)
    for side, arm in ((-1, arm_l), (1, arm_r)):
        raised = clamp((abs(arm[0]) - 1.2) / 1.2)
        if sweat > 0 and raised > 0:
            ctx.save()
            ctx.translate(side * 126, 238)
            sscale(ctx, 1, 1.45)
            ctx.arc(0, 0, 24, 0, 2 * math.pi)
            ctx.restore()
            ctx.set_source_rgba(0.25, 0.05, 0.12, 0.35 * sweat * raised)
            ctx.fill()
    # face
    ctx.save()
    ctx.translate(0, 5)
    sscale(ctx, 0.86, 1.0)
    ctx.arc(0, 0, 66, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgba(*rgba(skin))
    ctx.fill()
    # hijab front fold line
    ctx.move_to(-62, -20)
    ctx.curve_to(-40, -70, 40, -70, 62, -20)
    ctx.set_line_width(14)
    ctx.set_source_rgba(*rgba(hijab))
    ctx.stroke()
    # face details
    ink = (70, 30, 40)
    blink = 1.0 if (t * 0.7) % 3.0 > 0.12 else 0.15
    for ex in (-24, 24):
        ctx.save()
        ctx.translate(ex, 4)
        sscale(ctx, 1, blink)
        ctx.arc(0, 0, 6.5, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgba(*rgba(ink))
        ctx.fill()
    for ex in (-34, 34):
        ctx.arc(ex, 28, 10, 0, 2 * math.pi)
        ctx.set_source_rgba(*rgba(ROSE, 0.35))
        ctx.fill()
    ctx.set_line_width(5)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_source_rgba(*rgba(ink))
    if mood == "happy":
        ctx.arc(0, 26, 18, 0.15 * math.pi, 0.85 * math.pi)
        ctx.stroke()
        for ex in (-24, 24):
            ctx.move_to(ex - 10, -14)
            ctx.curve_to(ex - 4, -20, ex + 4, -20, ex + 10, -14)
        ctx.stroke()
    elif mood == "worried":
        ctx.move_to(-14, 40)
        ctx.curve_to(-6, 34, 6, 46, 14, 40)
        ctx.stroke()
        ctx.move_to(-34, -12)
        ctx.line_to(-14, -20)
        ctx.move_to(34, -12)
        ctx.line_to(14, -20)
        ctx.stroke()
    else:
        ctx.move_to(-12, 36)
        ctx.line_to(12, 36)
        ctx.stroke()
    ctx.restore()
    # sweat drops (screen space, near head)
    if sweat > 0:
        for i, (dx, dy) in enumerate(((110, -720), (-118, -650))):
            ph = (t * 0.9 + i * 0.5) % 1.0
            draw_droplet(ctx, x + dx * s, y + dy * s + ph * 40 * s, 16 * s, alpha=sweat * (1 - ph), lw=3)


def bubble(ctx, t, t0, text, x, y, w=None, tail=(-1, 1), style="hand", fill=WHITE, rot=-0.02, size=None):
    """Thought bubble with Caveat text; tail of little circles toward (tail dir)."""
    p = prog(t, t0, 0.4)
    if p <= 0:
        return
    fn, sz, col = STY[style][:3]
    sz = size or sz
    lines = text.split("\n")
    sps = [text_sprite(l_, fn, sz, col) for l_ in lines]
    tw = max(s_.adv for s_ in sps)
    lh = sz * 1.05
    bw, bh = (w or tw) + 80, lh * len(lines) + 50
    sc = 0.3 + 0.7 * ease_back(p, 2.2)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot + math.sin(t * 1.6) * 0.01)
    sscale(ctx, sc, sc)
    sh, pad = shadow_surface(int(bw), int(bh), int(bh / 2.2), 14, 50)
    blit(ctx, sh, 0, 10, pad + bw / 2, pad + bh / 2)
    rrect(ctx, -bw / 2, -bh / 2, bw, bh, bh / 2.2)
    ctx.set_source_rgba(*rgba(fill))
    ctx.fill()
    for k, r_ in enumerate((18, 11)):
        ctx.arc(tail[0] * (bw * 0.25 + k * 34), bh / 2 + 22 + k * 30 if tail[1] > 0 else -bh / 2 - 22 - k * 30, r_,
                0, 2 * math.pi)
        ctx.fill()
    for i, s_ in enumerate(sps):
        yy = -bh / 2 + 25 + lh * (i + 0.5)
        blit(ctx, s_.surf, 0, yy, s_.pad + s_.adv / 2, s_.pad + s_.asc * 0.62)
    ctx.restore()


def typewriter(ctx, t, t0, text, style, x, y, cps=22, cursor=True, anchor="l"):
    """Type text out; returns (chars shown, finished)."""
    n = int(max(0, (t - t0) * cps))
    shown = text[:n]
    if t < t0:
        return 0, False
    fn, sz, col = STY[style][:3]
    if shown:
        sp = text_sprite(shown, fn, sz, col)
        ox = sp.pad if anchor == "l" else sp.pad + sp.adv / 2
        blit(ctx, sp.surf, x, y, ox, sp.pad + sp.asc * 0.62)
        adv = sp.adv
    else:
        adv = 0
    done = n >= len(text)
    if cursor and (not done or (t * 2) % 1 < 0.5):
        f = font(fn, sz)
        asc, _ = f.getmetrics()
        cx = x + adv + 6 if anchor == "l" else x + adv / 2 + 6
        ctx.rectangle(cx, y - asc * 0.62, 5, asc * 0.9)
        ctx.set_source_rgba(*rgba(col, 0.9))
        ctx.fill()
    return n, done


# ---------------------------------------------------------------- runner
def run(compose, out_dir, dur=30.0, fps=FPS):
    """python video.py            -> renders frames to <out_dir>/../build/video.mp4
       python video.py --still t  -> PNG stills"""
    root = os.path.dirname(out_dir)
    os.makedirs(f"{root}/build", exist_ok=True)

    def frame(t):
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        ctx = cairo.Context(surf)
        ctx.set_antialias(cairo.ANTIALIAS_BEST)
        compose(ctx, t)
        surf.flush()
        return surf

    if len(sys.argv) > 2 and sys.argv[1] == "--still":
        for ts in sys.argv[2:]:
            frame(float(ts)).write_to_png(f"{root}/build/still_{float(ts):05.2f}.png")
        return
    out = f"{root}/build/video.mp4"
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(fps),
         "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out],
        stdin=subprocess.PIPE)
    n = int(round(dur * fps))
    for f in range(n):
        ff.stdin.write(bytes(frame(f / fps).get_data()))
    ff.stdin.close()
    ff.wait()
    print("wrote", out)
