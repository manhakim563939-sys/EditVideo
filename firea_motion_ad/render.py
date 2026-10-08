"""Firea Celeste Musk — 30s 9:16 motion ad (Awareness / Edutainment).

Renders every frame with cairo (vector shapes, transforms) + PIL (text sprites)
and pipes raw BGRA frames into ffmpeg.

Usage:
  python render.py                 -> build/video.mp4 (silent; mux with audio.py output)
  python render.py --still 9.5 ... -> build/still_<t>.png for checking frames
"""
import math
import os
import subprocess
import sys
from functools import lru_cache

import cairo
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from timeline import (DUR, EXAMPLE, FACT1, FACT2, FPS, H, HOOK, ORDER, PRODUCT, Q, S, TAKEAWAY, TRANS, W)

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


# ================================================================ SCENES
# Each scene draws its own full-frame background; lt = local time (may be < 0 during transitions).

def scene_hook(ctx, t, lt):
    bg_fill(ctx, t, BLUSH, PINK, 0.7, seed=1)
    # photo card rises in
    pc = ease_out(prog(lt, HOOK["card"], 0.7))
    photo_card(ctx, "photo_hook", 540, 1235 + (1 - pc) * 700, 690, 900, rot=-0.045 + (1 - pc) * 0.08,
               inner_zoom=1.12 - 0.08 * clamp(lt / 3.6), alpha=clamp(pc * 3))
    lines = [
        [Tok("Pakai", "h1"), Tok("lengan", "h1"), Tok("panjang", "h1")],
        [Tok("dari", "h1"), Tok("pagi", "h1")],
        [Tok("sampai malam?", "serif", under=ROSE)],
    ]
    placed = layout(lines, 540, 230)
    draw_words(ctx, lt, placed, HOOK["words"], HOOK["stagger"])
    sticker(ctx, lt, HOOK["sticker"], "+ cuaca panas & lembap", 700, 815, 0.07, icon="sun")


def scene_q(ctx, t, lt):
    bg_fill(ctx, t, WINE, WINE_D, 0.9, seed=2)
    # giant soft question mark
    qs = text_sprite("?", "serif", 900, ROSE)
    blit(ctx, qs.surf, 860 + math.sin(t * 0.8) * 14, 1180, qs.pad + qs.adv / 2, qs.pad + qs.asc * 0.6,
         rot=0.12 + math.sin(t * 0.5) * 0.04, alpha=0.16 * clamp(lt * 2))
    floating_drops(ctx, t, PINK, 0.18)
    l1 = [[Tok("Pernah", "medw"), Tok("tak", "medw"), Tok("rasa", "medw")],
          [Tok("ketiak", "medw"), Tok("cepat", "medw")],
          [Tok("PANAS & BERBAU", "h1w", hl=ROSE)]]
    p1 = layout(l1, 540, 520)
    draw_words(ctx, lt, p1, Q["words"], Q["stagger"])
    y2 = layout_bottom(p1) + 70
    l2 = [[Tok("walaupun", "serifp"), Tok("dah", "serifp")], [Tok("mandi", "serifp"), Tok("pagi?", "serifp")]]
    draw_words(ctx, lt, layout(l2, 540, y2), Q["block2"], 0.1)
    # "jom faham puncanya" + hand arrow
    cp = prog(lt, Q["cta"], 0.5)
    if cp > 0:
        sp = text_sprite("Jom faham puncanya", "hand", 60, PINK)
        blit(ctx, sp.surf, 500, 1500 + (1 - ease_out(cp)) * 30, sp.pad + sp.adv / 2, sp.pad + sp.asc * 0.6,
             alpha=clamp(cp * 3), rot=-0.03)
        arrow(ctx, 790, 1480, 830, 1620, ease_out(prog(lt, Q["cta"] + 0.2, 0.5)), 7, PINK, curve=-0.35)


def scene_fact1(ctx, t, lt):
    bg_fill(ctx, t, BLUSH2, PINK, 0.6, seed=4)
    chip(ctx, lt, FACT1["chip"], "FAKTA #1", 540, 300)
    p1 = layout([[Tok("Peluh", "xb"), Tok("sebenarnya", "xb")],
                 [Tok("hampir", "xb"), Tok("TAK", "xbw", hl=ROSE), Tok("berbau.", "xb")]], 540, 380)
    draw_words(ctx, lt, p1, FACT1["words"], FACT1["stagger"])

    # droplet falls, lands with squash, then gets surrounded by bacteria
    cx, cy, r = 540, 990, 118
    t_land = FACT1["drop"] + FACT1["fall"]
    if lt > FACT1["drop"]:
        fp = prog(lt, FACT1["drop"], FACT1["fall"])
        y = cy - 520 * (1 - ease_in(fp))
        sx = sy = 1.0
        if lt > t_land:
            k = lt - t_land
            sq = math.exp(-6 * k) * math.cos(2 * math.pi * 2.6 * k)
            sx, sy = 1 + 0.16 * sq, 1 - 0.16 * sq
        # soft glow underneath
        g = cairo.RadialGradient(cx, cy + r * 0.9, 0, cx, cy + r * 0.9, r * 2)
        g.add_color_stop_rgba(0, *rgba(PINK, 0.9 * clamp(lt - t_land + 0.3)))
        g.add_color_stop_rgba(1, *rgba(PINK, 0))
        ctx.set_source(g)
        ctx.arc(cx, cy + r * 0.9, r * 2, 0, 2 * math.pi)
        ctx.fill()
        draw_droplet(ctx, cx, y, r, sx=sx, sy=sy)
        lp = prog(lt, t_land + 0.15, 0.4)
        if lp > 0:
            sp = text_sprite("peluh", "hand", 54, WINE)
            blit(ctx, sp.surf, cx - 250, cy - 40, sp.pad + sp.adv / 2, sp.pad + sp.asc * 0.6, alpha=lp, rot=-0.12)
            arrow(ctx, cx - 250, cy - 5, cx - r - 18, cy + 20, lp, 5, WINE, head=16, curve=-0.25)
    # bacteria
    pos = [(-190, -110), (175, -150), (215, 60), (-215, 85), (-95, 200), (115, 190)]
    for i, (dx, dy) in enumerate(pos):
        bp = prog(lt, FACT1["bact"] + i * FACT1["bact_stag"], 0.35)
        if bp <= 0:
            continue
        s = ease_back(bp, 2.5)
        bx = cx + dx * (0.85 + 0.15 * s) + math.sin(t * 2 + i) * 8
        by = cy + dy * (0.85 + 0.15 * s) + math.cos(t * 1.7 + i * 2) * 8
        ctx.save()
        ctx.translate(bx, by)
        ctx.rotate(t * 0.8 * (1 if i % 2 else -1) + i)
        ctx.scale(s, s)
        # tail
        ctx.move_to(-30, 0)
        for k in range(1, 6):
            ctx.line_to(-30 - k * 9, math.sin(t * 9 + k + i) * 6)
        stroke_partial(ctx, 1, 4, WINE, 0.8)
        ctx.save()
        ctx.scale(1.35, 0.9)
        ctx.arc(0, 0, 26, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgba(*rgba((150, 190, 90)))
        ctx.fill_preserve()
        ctx.set_source_rgba(*rgba(WINE))
        ctx.set_line_width(4)
        ctx.stroke()
        for ddx, ddy in ((-10, -4), (8, 5), (12, -8)):
            ctx.arc(ddx, ddy, 4, 0, 2 * math.pi)
            ctx.set_source_rgba(*rgba((95, 135, 55)))
            ctx.fill()
        ctx.restore()
    if lt > FACT1["bact"] + 0.5:
        lp = prog(lt, FACT1["bact"] + 0.5, 0.4)
        sp = text_sprite("bakteria", "hand", 54, WINE)
        blit(ctx, sp.surf, cx + 300, cy - 280, sp.pad + sp.adv / 2, sp.pad + sp.asc * 0.6, alpha=lp, rot=0.1)
        arrow(ctx, cx + 290, cy - 245, cx + 195, cy - 175, lp, 5, WINE, head=16, curve=0.3)
    # odour waves
    op = prog(lt, FACT1["odor"], 0.6)
    if op > 0:
        for j, ox in enumerate((-60, 0, 60)):
            ph = t * 3 + j * 1.3
            y0 = cy - r * 1.75
            ctx.move_to(cx + ox, y0)
            for k in range(1, 21):
                yy = y0 - k * 9
                ctx.line_to(cx + ox + math.sin(ph + k * 0.45) * 14, yy)
            stroke_partial(ctx, ease_out(op), 7, ROSE, 0.85)

    p2 = layout([[Tok("Bau", "med"), Tok("terhasil", "med"), Tok("bila", "med")],
                 [Tok("bakteria", "serifm"), Tok("di", "med"), Tok("kulit", "med")],
                 [Tok("mengurai", "med"), Tok("peluh.", "med")]], 540, 1320)
    draw_words(ctx, lt, p2, FACT1["words2"], 0.08)


def scene_fact2(ctx, t, lt):
    bg_fill(ctx, t, BLUSH, PINK, 0.55, seed=5)
    chip(ctx, lt, FACT2["chip"], "FAKTA #2", 540, 300)
    p1 = layout([[Tok("Lengan", "xb"), Tok("panjang", "xb")],
                 [Tok("=", "xb"), Tok("kurang udara", "serif")]], 540, 380)
    draw_words(ctx, lt, p1, FACT2["words"], FACT2["stagger"])

    top, bot = 820, 1210
    dp = ease_out(prog(lt, FACT2["diagram"], 0.5))
    if dp > 0:
        # labels
        for txt, x in (("udara", 250), ("kain baju", 510), ("kulit", 905)):
            sp = text_sprite(txt, "hand", 50, WINE)
            blit(ctx, sp.surf, x, top - 40, sp.pad + sp.adv / 2, sp.pad + sp.asc * 0.6, alpha=dp)
        hh = (bot - top) * dp
        # gap glow (warm, humid)
        gp = prog(lt, FACT2["drops"], 2.2)
        g = cairo.RadialGradient(705, (top + bot) / 2, 10, 705, (top + bot) / 2, 260)
        g.add_color_stop_rgba(0, *rgba(ROSE, 0.45 * gp))
        g.add_color_stop_rgba(1, *rgba(ROSE, 0))
        ctx.set_source(g)
        ctx.rectangle(565, top, 270, hh)
        ctx.fill()
        # fabric band with weave
        rrect(ctx, 450, bot - hh, 110, hh, 18)
        ctx.set_source_rgba(*rgba(WINE))
        ctx.fill()
        ctx.save()
        rrect(ctx, 450, bot - hh, 110, hh, 18)
        ctx.clip()
        ctx.set_source_rgba(*rgba(ROSE, 0.55))
        ctx.set_line_width(4)
        for k in range(-6, 30):
            ctx.move_to(450, top + k * 22)
            ctx.line_to(560, top + k * 22 + 50)
        ctx.stroke()
        ctx.set_dash([14, 10])
        ctx.set_source_rgba(1, 1, 1, 0.8)
        ctx.set_line_width(3)
        ctx.move_to(470, bot - hh + 12)
        ctx.line_to(470, bot - 12)
        ctx.move_to(540, bot - hh + 12)
        ctx.line_to(540, bot - 12)
        ctx.stroke()
        ctx.set_dash([])
        ctx.restore()
        # skin band
        rrect(ctx, 840, bot - hh, 140, hh, 24)
        g2 = cairo.LinearGradient(840, 0, 980, 0)
        g2.add_color_stop_rgba(0, *rgba(SKIN))
        g2.add_color_stop_rgba(1, *rgba((222, 172, 150)))
        ctx.set_source(g2)
        ctx.fill()
    # air arrows bounce off the fabric
    ap = prog(lt, FACT2["air"], 0.3)
    if ap > 0:
        for row, yy in enumerate((900, 1015, 1130)):
            ph = ((lt - FACT2["air"]) / 1.0 + row * 0.33) % 1.0
            x0 = 110 + ph * 300
            a = ap * (1 - clamp((ph - 0.75) / 0.25)) * clamp(ph / 0.1)
            ctx.move_to(x0 - 90, yy)
            for k in range(1, 10):
                ctx.line_to(x0 - 90 + k * 10, yy + math.sin(k * 0.9 + t * 6) * 4)
            stroke_partial(ctx, 1, 7, ROSE, a)
            ctx.move_to(x0 - 2, yy - 14)
            ctx.line_to(x0 + 12, yy)
            ctx.line_to(x0 - 2, yy + 14)
            stroke_partial(ctx, 1, 7, ROSE, a)
        # "blocked" marks
        xp = ease_back(prog(lt, FACT2["air"] + 0.6, 0.35), 2.5)
        if xp > 0:
            ctx.save()
            ctx.translate(430, 1015)
            ctx.scale(xp, xp)
            ctx.arc(0, 0, 30, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 1, 1)
            ctx.fill()
            for s in (-1, 1):
                ctx.move_to(-12, -12 * s)
                ctx.line_to(12, 12 * s)
            stroke_partial(ctx, 1, 7, WINE)
            ctx.restore()
    # trapped sweat droplets accumulating between fabric and skin
    dpos = [(640, 1120), (760, 1090), (700, 990), (620, 900), (780, 940), (690, 1170), (790, 1180), (610, 1030), (750, 850)]
    for i, (x, y) in enumerate(dpos):
        q = prog(lt, FACT2["drops"] + i * FACT2["drop_stag"], 0.35)
        if q > 0:
            s = ease_back(q, 2.4)
            draw_droplet(ctx, x + math.sin(t * 2 + i) * 4, y, 26 * s, alpha=clamp(q * 3), lw=3.5)
    p2 = layout([[Tok("Peluh", "med"), Tok("terperangkap", "serifm"), Tok("lebih", "med"), Tok("lama.", "med")]],
                540, 1300)
    draw_words(ctx, lt, p2, FACT2["words2"], 0.09)
    p3 = layout([[Tok("Bakteria", "med"), Tok("suka", "med"), Tok("suasana", "med")],
                 [Tok("panas & lembap.", "xbw", hl=ROSE)]], 540, layout_bottom(p2) + 40)
    draw_words(ctx, lt, p3, FACT2["words3"], 0.09)


def scene_example(ctx, t, lt):
    bg_fill(ctx, t, BLUSH2, PINK, 0.6, seed=6)
    chip(ctx, lt, EXAMPLE["chip"], "CONTOH HARIAN", 540, 300)
    draw_words(ctx, lt, layout([[Tok("Satu", "xb"), Tok("hari", "xb"), Tok("biasa", "serif")]], 540, 375),
               EXAMPLE["words"], 0.1)
    lx = 170
    ys = (690, 925, 1160)
    items = (("8:00 PAGI", "Keluar ke kerja / kelas"), ("1:00 TENGAH HARI", "Panas terik di luar"),
             ("7:00 MALAM", "Belum sempat mandi"))
    levels = (0.25, 0.6, 0.92)
    # line drawn progressively between nodes
    for i in range(2):
        lp = ease_io(prog(lt, EXAMPLE["nodes"][i] + 0.2, EXAMPLE["nodes"][i + 1] - EXAMPLE["nodes"][i] - 0.2))
        if lp > 0:
            ctx.move_to(lx, ys[i] + 34)
            ctx.line_to(lx, ys[i] + 34 + (ys[i + 1] - ys[i] - 68) * lp)
            stroke_partial(ctx, 1, 8, PINK)
    for i, (ti, desc) in enumerate(items):
        t0 = EXAMPLE["nodes"][i]
        np_ = prog(lt, t0, 0.4)
        if np_ <= 0:
            continue
        s = ease_back(np_, 2.6)
        ctx.arc(lx, ys[i], 34 * s, 0, 2 * math.pi)
        ctx.set_source_rgba(*rgba(ROSE))
        ctx.fill()
        ctx.arc(lx, ys[i], 13 * s, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, 1)
        ctx.fill()
        a = clamp(np_ * 2.5)
        dx = (1 - ease_out(np_)) * 40
        s1 = text_sprite(ti, "xb", 44, ROSE, 1)
        blit(ctx, s1.surf, lx + 70 + dx, ys[i] - 26, s1.pad, s1.pad + s1.asc * 0.62, alpha=a)
        s2 = text_sprite(desc, "med", 46, WINE)
        blit(ctx, s2.surf, lx + 70 + dx, ys[i] + 36, s2.pad, s2.pad + s2.asc * 0.62, alpha=a)
    # sweat meter
    mx, mt, mb, mw = 930, 660, 1200, 70
    mp = ease_out(prog(lt, EXAMPLE["nodes"][0] - 0.2, 0.4))
    if mp > 0:
        rrect(ctx, mx - mw / 2, mt, mw, (mb - mt), mw / 2)
        ctx.set_source_rgba(1, 1, 1, mp)
        ctx.fill_preserve()
        ctx.set_source_rgba(*rgba(PINK, mp))
        ctx.set_line_width(5)
        ctx.stroke()
        lvl = 0.0
        for i, tt in enumerate(EXAMPLE["nodes"]):
            k = ease_out(prog(lt, tt + 0.1, 0.6))
            lvl = lvl + (levels[i] - (levels[i - 1] if i else 0)) * k
        if lvl > 0:
            ctx.save()
            rrect(ctx, mx - mw / 2 + 8, mt + 8, mw - 16, mb - mt - 16, (mw - 16) / 2)
            ctx.clip()
            fh = (mb - mt - 16) * lvl
            g = cairo.LinearGradient(0, mb, 0, mt)
            g.add_color_stop_rgba(0, *rgba(PINK))
            g.add_color_stop_rgba(0.5, *rgba(ROSE))
            g.add_color_stop_rgba(1, *rgba(WINE))
            ctx.set_source(g)
            wave = math.sin(t * 5) * 5
            ctx.move_to(mx - mw, mb)
            ctx.line_to(mx - mw, mb - 8 - fh + wave)
            ctx.line_to(mx + mw, mb - 8 - fh - wave)
            ctx.line_to(mx + mw, mb)
            ctx.close_path()
            ctx.fill()
            ctx.restore()
        draw_droplet(ctx, mx, mt - 60, 26, alpha=mp, lw=3.5)
        sp = text_sprite("peluh", "hand", 46, WINE)
        blit(ctx, sp.surf, mx, mb + 48, sp.pad + sp.adv / 2, sp.pad + sp.asc * 0.6, alpha=mp)
        sp = text_sprite("terkumpul", "hand", 46, WINE)
        blit(ctx, sp.surf, mx - 10, mb + 92, sp.pad + sp.adv / 2, sp.pad + sp.asc * 0.6, alpha=mp)
    p2 = layout([[Tok("Makin", "xb"), Tok("lama,", "xb")], [Tok("makin", "xb"), Tok("terasa.", "xbw", hl=ROSE)]],
                540, 1380)
    draw_words(ctx, lt, p2, EXAMPLE["words2"], 0.1)


def scene_takeaway(ctx, t, lt):
    bg_fill(ctx, t, WINE, WINE_D, 0.9, seed=7)
    floating_drops(ctx, t, PINK, 0.12, seed=9)
    chip(ctx, lt, TAKEAWAY["chip"], "TAKEAWAY", 540, 300, fill=PINK, color=WINE)
    p1 = layout([[Tok("Berpeluh", "medw"), Tok("itu", "medw"), Tok("normal.", "serifp")]], 540, 390)
    draw_words(ctx, lt, p1, TAKEAWAY["words"], 0.1)
    p2 = layout([[Tok("Yang", "medw"), Tok("penting,", "medw"), Tok("kawal", "medw")],
                 [Tok("PELUH & BAU", "h1w", hl=ROSE)],
                 [Tok("dari", "medw"), Tok("awal", "medw"), Tok("pagi.", "medw")]], 540, layout_bottom(p1) + 40)
    draw_words(ctx, lt, p2, TAKEAWAY["words2"], 0.09)
    ph = prog(lt, TAKEAWAY["photo"], 0.6)
    if ph > 0:
        e = ease_out(ph)
        photo_card(ctx, "photo_mirror", 600, 1390 + (1 - e) * 500, 500, 480, rot=0.06 - (1 - e) * 0.1,
                   inner_zoom=1.0 + 0.06 * clamp((lt - TAKEAWAY["photo"]) / 2), alpha=clamp(ph * 3), border=12, r=24)
    np_ = prog(lt, TAKEAWAY["note"], 0.45)
    if np_ > 0:
        sp = text_sprite("rutin pagi", "hand", 60, PINK)
        blit(ctx, sp.surf, 205, 1240, sp.pad + sp.adv / 2, sp.pad + sp.asc * 0.6, alpha=clamp(np_ * 3), rot=-0.14)
        arrow(ctx, 210, 1290, 330, 1400, ease_out(np_), 6, PINK, curve=0.3)


def scene_product(ctx, t, lt):
    bg_fill(ctx, t, BLUSH, PINK, 0.8, seed=8)
    # photo card of real user holding the product
    pc = ease_out(prog(lt, PRODUCT["card"], 0.6))
    photo_card(ctx, "photo_ugc", 540, 845 + (1 - pc) * 600, 520, 660, rot=-0.03 + (1 - pc) * 0.08,
               inner_zoom=1.04 + 0.08 * clamp(lt / 4.8), alpha=clamp(pc * 3))
    # sparkles near bottle (bottle sits left-centre of the card)
    for i, (dx, dy, s0) in enumerate(((-215, 620, 28), (-70, 670, 16), (-225, 820, 18), (-60, 790, 14))):
        sp_ = prog(lt, PRODUCT["sparkle"] + i * 0.12, 0.5)
        if sp_ > 0:
            s = s0 * (math.sin(clamp(sp_) * math.pi) * 0.6 + 0.4 + 0.15 * math.sin(t * 6 + i))
            sparkle(ctx, 540 + dx, dy + 30, s, clamp(sp_ * 3), WHITE if i != 3 else ROSE)
    # logo: wipe reveal left -> right
    lp = prog(lt, PRODUCT["logo"], 0.7)
    if lp > 0:
        ls = logo_surface(WINE, 420)
        lw, lh = ls.get_width(), ls.get_height()
        ctx.save()
        ctx.rectangle(540 - lw / 2 - 20, 0, (lw + 40) * ease_io(lp), 500)
        ctx.clip()
        blit(ctx, ls, 540, 245, lw / 2, lh / 2, sc=0.94 + 0.06 * ease_out(lp))
        ctx.restore()
    np_ = prog(lt, PRODUCT["name"], 0.45)
    if np_ > 0:
        sp = text_sprite("CELESTE MUSK DEODORANT ROLL-ON", "sb", 34, WINE, 4)
        blit(ctx, sp.surf, 540, 385 + (1 - ease_out(np_)) * 20, sp.pad + sp.adv / 2, sp.pad + sp.asc * 0.62,
             alpha=clamp(np_ * 2.5))
    # USP pills
    pills = [("TAHAN PELUH & TAHAN BAU", 540, 1250, WINE, WHITE),
             ("0% PARABEN", 330, 1350, WHITE, WINE), ("0% ALKOHOL", 750, 1350, WHITE, WINE)]
    for (txt, x, y, fill, col), t0 in zip(pills, PRODUCT["chips"]):
        p = prog(lt, t0, 0.4)
        if p <= 0:
            continue
        sp = text_sprite(txt, "xb", 36, col, 1)
        w, h = sp.adv + 120, 82
        sc = 0.4 + 0.6 * ease_back(p, 2.4)
        a = clamp(p * 3)
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(sc, sc)
        sh, pad = shadow_surface(int(w), h, h // 2, 12, 50)
        blit(ctx, sh, 0, 8, pad + w / 2, pad + h / 2, alpha=a)
        rrect(ctx, -w / 2, -h / 2, w, h, h / 2)
        ctx.set_source_rgba(*rgba(fill, a))
        ctx.fill()
        draw_check(ctx, -w / 2 + 44, 0, 22, ROSE, WHITE, a)
        blit(ctx, sp.surf, -w / 2 + 80 + sp.adv / 2, 0, sp.pad + sp.adv / 2, sp.pad + sp.asc * 0.62, alpha=a)
        ctx.restore()
    p2 = layout([[Tok("Khas", "meds"), Tok("untuk", "meds"), Tok("wanita", "meds"), Tok("bertudung", "meds")],
                 [Tok("yang", "meds"), Tok("aktif", "meds"), Tok("seharian.", "meds")]], 540, 1435)
    draw_words(ctx, lt, p2, PRODUCT["tag"], 0.06)
    draw_words(ctx, lt, layout([[Tok("confidence in every touch", "serifs")]], 540, layout_bottom(p2) + 26),
               PRODUCT["slogan"], 0.1, mode="pop")


SCENES = dict(hook=scene_hook, q=scene_q, fact1=scene_fact1, fact2=scene_fact2, example=scene_example,
              takeaway=scene_takeaway, product=scene_product)


def draw_scene(ctx, name, t):
    lt = t - S[name]
    i = ORDER.index(name)
    end = S[ORDER[i + 1]] if i + 1 < len(ORDER) else DUR
    # slow camera push across the scene, plus hook punch-in
    z = 1.0 + 0.025 * clamp(lt / (end - S[name]))
    if name == "hook":
        z += 0.03 * ease_out(prog(lt, HOOK["punch"], 0.5))
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.translate(-W / 2, -H / 2)
    SCENES[name](ctx, t, lt)
    ctx.restore()


def compose(ctx, t):
    cur = max((n for n in ORDER if S[n] <= t), key=lambda n: S[n])
    i = ORDER.index(cur)
    nxt = ORDER[i + 1] if i + 1 < len(ORDER) else None
    # transition into the NEXT scene that starts before the cut
    if nxt and TRANS[nxt] in ("panel", "panel_rose", "push", "zoom") and t > S[nxt] - 0.32:
        return transition(ctx, t, cur, nxt)
    if i > 0 and t < S[cur] + 0.5:
        return transition(ctx, t, ORDER[i - 1], cur)
    draw_scene(ctx, cur, t)


def transition(ctx, t, a, b):
    kind, T = TRANS[b], S[b]
    if kind in ("panel", "panel_rose"):
        col, col2 = (WINE, ROSE) if kind == "panel" else (ROSE, WINE)
        if b in ("q",):
            col, col2 = ROSE, WINE
        d = 0.3
        if t < T:
            draw_scene(ctx, a, t)
            p = ease_io(prog(t, T - d, d))
            top = H * (1 - p)
            ctx.rectangle(0, top + 70, W, H)
            ctx.set_source_rgba(*rgba(col))
            ctx.fill()
            ctx.rectangle(0, top, W, 70 + 1)
            ctx.set_source_rgba(*rgba(col2))
            ctx.fill()
        elif t < T + d:
            draw_scene(ctx, b, t)
            p = ease_io(prog(t, T, d))
            bot = H * (1 - p)
            ctx.rectangle(0, 0, W, bot - 70)
            ctx.set_source_rgba(*rgba(col))
            ctx.fill()
            ctx.rectangle(0, bot - 70, W, 70)
            ctx.set_source_rgba(*rgba(col2))
            ctx.fill()
        else:
            draw_scene(ctx, b, t)
    elif kind == "iris":
        d = 0.5
        if t < T:
            draw_scene(ctx, a, t)
            return
        p = ease_io(prog(t, T, d))
        if p >= 1:
            draw_scene(ctx, b, t)
            return
        draw_scene(ctx, a, t)
        r = 1150 * p
        ctx.save()
        ctx.arc(540, 980, r, 0, 2 * math.pi)
        ctx.clip()
        draw_scene(ctx, b, t)
        ctx.restore()
        ctx.arc(540, 980, r, 0, 2 * math.pi)
        ctx.set_source_rgba(*rgba(ROSE))
        ctx.set_line_width(26 * (1 - p) + 4)
        ctx.stroke()
    elif kind == "push":
        d0, d1 = 0.25, 0.3
        if t >= T + d1:
            draw_scene(ctx, b, t)
            return
        if t < T - d0:
            draw_scene(ctx, a, t)
            return
        e = ease_io(prog(t, T - d0, d0 + d1))
        ctx.save()
        ctx.translate(-W * e, 0)
        draw_scene(ctx, a, t)
        ctx.restore()
        ctx.save()
        ctx.translate(W * (1 - e), 0)
        draw_scene(ctx, b, max(t, T))
        ctx.restore()
    elif kind == "zoom":
        d0, d1 = 0.25, 0.35
        if t >= T + d1:
            draw_scene(ctx, b, t)
            return
        if t < T - d0:
            draw_scene(ctx, a, t)
            return
        e = ease_io(prog(t, T - d0, d0 + d1))
        draw_scene(ctx, b, max(t, T))  # b underneath, scaled in below
        ctx.save()
        ctx.push_group()
        ctx.translate(W / 2, H / 2)
        ctx.scale(1 + 0.6 * e, 1 + 0.6 * e)
        ctx.translate(-W / 2, -H / 2)
        draw_scene(ctx, a, t)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(1 - ease_out(clamp(e * 1.7)))
        ctx.restore()


def render_frame(t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)
    compose(ctx, t)
    surf.flush()
    return surf


def main():
    os.makedirs(f"{ROOT}/build", exist_ok=True)
    if len(sys.argv) > 2 and sys.argv[1] == "--still":
        for ts in sys.argv[2:]:
            render_frame(float(ts)).write_to_png(f"{ROOT}/build/still_{float(ts):05.2f}.png")
        return
    out = f"{ROOT}/build/video.mp4"
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out],
        stdin=subprocess.PIPE)
    n = int(round(DUR * FPS))
    for f in range(n):
        s = render_frame(f / FPS)
        ff.stdin.write(bytes(s.get_data()))
        if f % 60 == 0:
            print(f"frame {f}/{n}", flush=True)
    ff.stdin.close()
    ff.wait()
    print("wrote", out)


if __name__ == "__main__":
    main()
