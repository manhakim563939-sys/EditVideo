"""Testimonial helpers: wrapped rich text with colour emoji + highlight ranges, chat bubbles,
typing indicator, and the shared end card built on the real bottle photo (13.jpg)."""
import math
from functools import lru_cache

import cairo
from PIL import Image, ImageDraw, ImageFont

import fx
from fx import (BLUSH, GREEN, PINK, ROSE, WHITE, WINE, WINE_D, YELLOW, blit, clamp, ease_back, ease_out, label, logo,
                pil_to_surface, pill, prog, rgba, rrect, shadow_surface, solid, vgrad, W, H)

EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
HL = (255, 222, 120)  # marker colour (like the highlighter on the posters)


def _is_emoji(ch):
    o = ord(ch)
    return o >= 0x1F000 or 0x2600 <= o <= 0x27BF or o in (0xFE0F, 0x200D)


@lru_cache(None)
def _emoji_img(ch, size):
    f = ImageFont.truetype(EMOJI_FONT, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    bb = im.getbbox()
    im = im.crop(bb) if bb else im
    s = size * 1.05 / max(1, im.height)
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)


def _runs(word):
    runs, cur, emo = [], "", None
    for ch in word:
        e = _is_emoji(ch)
        if ch in ("️", "‍"):
            continue
        if emo is None or e == emo:
            cur += ch
        else:
            runs.append((cur, emo))
            cur = ch
        emo = e
    if cur:
        runs.append((cur, emo))
    return runs


class Block:
    def __init__(self, surf, w, h, rects, pad, lineh):
        self.surf, self.w, self.h, self.rects, self.pad, self.lineh = surf, w, h, rects, pad, lineh


@lru_cache(None)
def rich_block(text, fname, size, color, maxw, hl=None, lead=1.32, align="left"):
    f = fx.font(fname, size)
    asc, desc = f.getmetrics()
    space = f.getlength(" ")

    def wlen(word):
        n = 0
        for r, e in _runs(word):
            n += sum(_emoji_img(c, size).width + 4 for c in r) if e else f.getlength(r)
        return n

    words = text.split(" ")
    # highlight: mark words overlapping the substring
    marks = [False] * len(words)
    if hl and hl in text:
        a = text.index(hl)
        b = a + len(hl)
        pos = 0
        for i, w_ in enumerate(words):
            if pos < b and pos + len(w_) > a:
                marks[i] = True
            pos += len(w_) + 1
    lines, cur, cw = [], [], 0
    for i, w_ in enumerate(words):
        wl = wlen(w_)
        if cur and cw + space + wl > maxw:
            lines.append((cur, cw))
            cur, cw = [], 0
        cur.append(i)
        cw = cw + (space if len(cur) > 1 else 0) + wl
    if cur:
        lines.append((cur, cw))
    lineh = int(size * lead)
    bw = int(max(c for _, c in lines)) + 2
    pad = 12
    im = Image.new("RGBA", (bw + 2 * pad, lineh * len(lines) + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rects = []
    for li, (idxs, lw) in enumerate(lines):
        x = pad + ((bw - lw) / 2 if align == "center" else 0)
        base = pad + li * lineh + (lineh - (asc + desc)) / 2 + asc
        run = None  # [x_start, x_end] of the current highlighted stretch on this line
        for i in idxs:
            x0 = x
            for r, e in _runs(words[i]):
                if e:
                    for c in r:
                        em = _emoji_img(c, size)
                        im.alpha_composite(em, (int(x), int(base - asc * 0.92)))
                        x += em.width + 4
                else:
                    d.text((x, base), r, font=f, fill=color + (255,), anchor="ls")
                    x += f.getlength(r)
            if marks[i]:
                run = [run[0] if run else x0, x]
            elif run:
                rects.append((run[0] - 6, base - asc * 0.88, run[1] - run[0] + 12, asc * 0.88 + desc * 0.6))
                run = None
            x += space
        if run:
            rects.append((run[0] - 6, base - asc * 0.88, run[1] - run[0] + 12, asc * 0.88 + desc * 0.6))
    return Block(pil_to_surface(im), bw, lineh * len(lines), rects, pad, lineh)


def draw_block(ctx, blk, x, y, t, t_hl=None, hl_col=HL, alpha=1.0):
    """Draw block with its top-left content corner at (x, y); highlight sweeps in from t_hl."""
    if t_hl is not None:
        hp = ease_out(prog(t, t_hl, 0.5))
        if hp > 0:
            tot = sum(r[2] for r in blk.rects) or 1
            done = hp * tot
            for (rx, ry, rw, rh) in blk.rects:
                w_ = clamp(done / rw) * rw
                done -= rw
                if w_ <= 0:
                    break
                rrect(ctx, x - blk.pad + rx, y - blk.pad + ry, w_, rh, 8)
                ctx.set_source_rgba(*rgba(hl_col, 0.9 * alpha))
                ctx.fill()
    blit(ctx, blk.surf, x - blk.pad, y - blk.pad, 0, 0, alpha=alpha)


def chat_bubble(ctx, t, t0, blk, side, x_edge, y, fill, time_str, tcol=(120, 110, 115), t_hl=None):
    """side 'in' = left-aligned (customer), 'out' = right-aligned (Firea). Returns bubble height."""
    p = prog(t, t0, 0.3)
    bw, bh = blk.w + 56, blk.h + 30 + 34
    if p <= 0:
        return bh
    sc = 0.7 + 0.3 * ease_back(p, 2.2)
    x = x_edge if side == "in" else x_edge - bw
    ctx.save()
    ox = x if side == "in" else x + bw
    ctx.translate(ox, y)
    fx.sscale(ctx, sc, sc)
    ctx.translate(-ox, -y)
    sh, pad = shadow_surface(int(bw), int(bh), 26, 8, 40)
    blit(ctx, sh, x + bw / 2, y + bh / 2 + 4, pad + bw / 2, pad + bh / 2, alpha=clamp(p * 3))
    rrect(ctx, x, y, bw, bh, 26)
    ctx.set_source_rgba(*rgba(fill, clamp(p * 3)))
    ctx.fill()
    # tail
    if side == "in":
        ctx.move_to(x + 4, y + 8)
        ctx.line_to(x - 16, y)
        ctx.line_to(x + 24, y)
    else:
        ctx.move_to(x + bw - 4, y + 8)
        ctx.line_to(x + bw + 16, y)
        ctx.line_to(x + bw - 24, y)
    ctx.close_path()
    ctx.fill()
    draw_block(ctx, blk, x + 28, y + 18, t, t_hl=t_hl, alpha=clamp(p * 3))
    ts = fx.text_sprite(time_str, "med", 24, tcol)
    blit(ctx, ts.surf, x + bw - 22, y + bh - 22, ts.pad + ts.adv, ts.pad + ts.asc * 0.6, alpha=clamp(p * 3))
    if side == "out":
        for k in (0, 12):
            ctx.move_to(x + bw - 22 - ts.adv - 46 + k, y + bh - 26)
            ctx.line_to(x + bw - 22 - ts.adv - 38 + k, y + bh - 18)
            ctx.line_to(x + bw - 22 - ts.adv - 24 + k, y + bh - 34)
        fx.stroke_partial(ctx, 1, 3.5, (80, 160, 230), clamp(p * 3))
    ctx.restore()
    return bh


def typing(ctx, t, x, y, fill=WHITE, alpha=1.0):
    if alpha <= 0:
        return
    rrect(ctx, x, y, 130, 66, 30)
    ctx.set_source_rgba(*rgba(fill, alpha))
    ctx.fill()
    for i in range(3):
        b = math.sin(t * 9 - i * 0.9) * 6
        ctx.arc(x + 36 + i * 29, y + 33 - max(0, b), 8, 0, 2 * math.pi)
        ctx.set_source_rgba(0.55, 0.5, 0.52, alpha)
        ctx.fill()


fx.STY.update({"disc": ("med", 28, WHITE), "endname": ("sb", 32, WINE)})


def end_card(ctx, t, lt, headline=None, disclaimer="Testimoni pelanggan sebenar. Pengalaman individu mungkin berbeza."):
    """Real bottle photo (13.jpg) full-bleed + logo + USP chips + disclaimer."""
    solid(ctx, WINE)
    fx.full_photo(ctx, "photo_real", 1.14 - 0.08 * clamp(lt / 6.0))
    vgrad(ctx, 0, 380, WHITE, 0.97, 0.85)
    vgrad(ctx, 380, 780, WHITE, 0.85, 0.0)
    vgrad(ctx, 1280, H, WINE_D, 0.0, 0.92)
    logo(ctx, lt, 0.2, 540, 170, 330)
    np_ = prog(lt, 0.6, 0.4)
    if np_ > 0:
        label(ctx, "CELESTE MUSK DEODORANT ROLL-ON", "endname", 540, 300, alpha=clamp(np_ * 3), sc=0.95)
    if headline:
        hp = prog(lt, 0.9, 0.45)
        if hp > 0:
            hs = fx.text_sprite(headline, "serif", 82, ROSE)
            label(ctx, headline, "serifm", 540, 395 + (1 - ease_out(hp)) * 20, alpha=clamp(hp * 3),
                  sc=min(1.0, 900 / hs.adv))
    chips = [("Tahan peluh & bau", 300, 1470, WINE, WHITE), ("Cepat kering", 790, 1470, YELLOW, WINE),
             ("0% Alkohol", 330, 1590, WHITE, WINE), ("0% Paraben", 770, 1590, ROSE, WHITE)]
    for i, (txt, x, y, fill, col) in enumerate(chips):
        pill(ctx, lt, 1.3 + i * 0.25, txt, x, y, fill, col, size=42, rot=(-0.04 if i % 2 == 0 else 0.04), icon="check")
    dp = prog(lt, 2.4, 0.5)
    if dp > 0:
        label(ctx, disclaimer, "disc", 540, 1745, alpha=0.85 * clamp(dp * 3))
