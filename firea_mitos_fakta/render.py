"""Firea Celeste Musk — "MITOS atau FAKTA?" 30s 9:16 quiz-style motion ad.

Usage:
  python render.py                 -> build/video.mp4 (silent; mux with build/audio.wav)
  python render.py --still 5 12.3  -> build/still_<t>.png
"""
import math
import os
import subprocess
import sys
from functools import lru_cache

import cairo
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import fx
from fx import (BLUSH, PINK, ROSE, WHITE, WINE, WINE_D, Tok, arrow, blit, chip, clamp, draw_check, ease_back,
                ease_in, ease_io, ease_out, layout, layout_bottom, logo_surface, photo_card, photo_surface,
                pil_to_surface, prog, rgba, rrect, shadow_surface, sparkle, text_sprite)
from timeline import DUR, FPS, H, HOOK, ORDER, QUIZ, REVEAL, S, W

ROOT = os.path.dirname(os.path.abspath(__file__))
CUT = f"{ROOT}/assets/cut"

YELLOW = (255, 214, 102)  # accent from Firea's yellow sticky-note poster
GREEN = (34, 150, 108)    # used only for the "FAKTA!" stamp (true = green)

fx.FONTS["brico"] = "Bricolage"
fx.STY.update({
    "stmt": ("brico", 84, WINE),
    "ex": ("sb", 58, WHITE),
    "ex_y": ("serif", 76, YELLOW),
    "ex_hl": ("brico", 78, WINE),
    "rev_h": ("brico", 96, WINE),
    "rev_s": ("serif", 84, ROSE),
    "slogan": ("serif", 50, ROSE),
})


# ---------------------------------------------------------------- building blocks
def bg_quiz(ctx, t, base, stripe, seed=0):
    ctx.set_source_rgb(*rgba(base)[:3])
    ctx.rectangle(0, 0, W, H)
    ctx.fill()
    # slow diagonal stripes (game-show energy without noise)
    ctx.save()
    ctx.rectangle(0, 0, W, H)
    ctx.clip()
    ctx.translate(W / 2, H / 2)
    ctx.rotate(-0.5)
    off = (t * 40) % 160
    ctx.set_source_rgba(*rgba(stripe, 0.10))
    for k in range(-14, 15):
        ctx.rectangle(k * 160 + off - 1400 % 160, -1600, 70, 3200)
    ctx.fill()
    ctx.restore()
    rng = np.random.default_rng(seed)
    for i in range(3):
        bx = rng.uniform(0, W) + math.sin(t * 0.4 + i) * 60
        by = rng.uniform(0, H) + math.cos(t * 0.3 + i) * 80
        br = rng.uniform(420, 640)
        g = cairo.RadialGradient(bx, by, 0, bx, by, br)
        g.add_color_stop_rgba(0, *rgba(stripe, 0.25))
        g.add_color_stop_rgba(1, *rgba(stripe, 0))
        ctx.set_source(g)
        ctx.arc(bx, by, br, 0, 2 * math.pi)
        ctx.fill()


@lru_cache(None)
def stamp_surface(text, color):
    """Rubber-stamp sprite: outlined box + text with ink texture."""
    f = fx.font("brico", 150)
    tw = f.getlength(text)
    asc, desc = f.getmetrics()
    pad, bw = 40, 12
    w, h = int(tw + 2 * pad + 40), int(asc + 2 * pad)
    im = Image.new("L", (w + 40, h + 40), 0)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, 20 + w, 20 + h), 28, outline=255, width=bw)
    d.text((20 + w / 2, 20 + h / 2 + 6), text, font=f, fill=255, anchor="mm")
    rng = np.random.default_rng(len(text))
    noise = rng.uniform(0, 1, (im.height // 3 + 1, im.width // 3 + 1))
    noise = np.asarray(Image.fromarray((noise * 255).astype(np.uint8)).resize(im.size, Image.BILINEAR)) / 255
    a = np.asarray(im) / 255 * np.clip(0.55 + noise * 0.75, 0, 1)
    rgba_im = Image.new("RGBA", im.size, color + (0,))
    rgba_im.putalpha(Image.fromarray((a * 235).astype(np.uint8)))
    return pil_to_surface(rgba_im)


@lru_cache(None)
def bottle_surface(height):
    b = Image.open(f"{CUT}/bottle.png").convert("RGBA")
    s = height / b.height
    b = b.resize((int(b.width * s), int(b.height * s)), Image.LANCZOS)
    pad = 60
    canvas = Image.new("RGBA", (b.width + 2 * pad, b.height + 2 * pad), (0, 0, 0, 0))
    al = Image.new("L", canvas.size, 0)
    al.paste(b.getchannel("A"), (pad, pad))
    outline = al.filter(ImageFilter.GaussianBlur(7)).point(lambda v: 255 if v > 18 else 0).filter(
        ImageFilter.GaussianBlur(1.2))
    shadow = outline.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.35))
    sh = Image.new("RGBA", canvas.size, (90, 15, 40, 0))
    sh.putalpha(shadow)
    wh = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
    wh.putalpha(outline)
    shifted = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shifted.alpha_composite(sh, (0, 16))
    shifted.alpha_composite(wh)
    shifted.alpha_composite(b, (pad, pad))
    return pil_to_surface(shifted)


def full_photo(ctx, name, zoom, dx=0, dy=0):
    ps = photo_surface(name, W, H)
    blit(ctx, ps, W / 2 + dx, H / 2 + dy, ps.get_width() / 2, ps.get_height() / 2, sc=max(zoom, 1.0) / 1.14)


def vgrad(ctx, y0, y1, col, a0, a1):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgba(0, *rgba(col, a0))
    g.add_color_stop_rgba(1, *rgba(col, a1))
    ctx.set_source(g)
    ctx.rectangle(0, min(y0, y1), W, abs(y1 - y0))
    ctx.fill()


def slam(ctx, t, t0, sp, x, y, align="left", rot=0.0):
    """Big word that slams in from 2.4x with a little settle."""
    p = prog(t, t0, 0.22)
    if p <= 0:
        return
    k = t - t0 - 0.22
    settle = math.exp(-9 * max(k, 0)) * math.sin(max(k, 0) * 28) * 0.05 if k > 0 else 0
    sc = 2.4 - 1.4 * ease_in(p) + settle
    ox = sp.pad if align == "left" else sp.pad + sp.adv / 2
    blit(ctx, sp.surf, x, y, ox, sp.pad + sp.asc * 0.62, sc=sc, rot=rot, alpha=clamp(p * 3))


# ================================================================ SCENES
def scene_hook(ctx, t, lt):
    ctx.set_source_rgb(*rgba(WINE)[:3])
    ctx.rectangle(0, 0, W, H)
    ctx.fill()
    full_photo(ctx, "photo_arm", 1.10 - 0.06 * clamp(lt / 3.0))
    vgrad(ctx, 0, 820, WINE_D, 0.88, 0.0)
    vgrad(ctx, 1250, H, WINE_D, 0.0, 0.75)
    m = text_sprite("MITOS", "brico", 196, WHITE)
    a = text_sprite("atau", "serif", 112, YELLOW)
    f = text_sprite("FAKTA?", "brico", 196, WHITE)
    slam(ctx, lt, HOOK["mitos"], m, 70, 255)
    ap = prog(lt, HOOK["atau"], 0.35)
    if ap > 0:
        blit(ctx, a.surf, 90, 388 + (1 - ease_out(ap)) * 30, a.pad, a.pad + a.asc * 0.62, alpha=clamp(ap * 3),
             rot=-0.06)
    slam(ctx, lt, HOOK["fakta"], f, 70, 528)
    # pill + note at the bottom
    pp = prog(lt, HOOK["pill"], 0.4)
    if pp > 0:
        sp = text_sprite("EDISI KETIAK BERPELUH", "xb", 40, WINE, 2)
        w, h = sp.adv + 70, 92
        sc = 0.4 + 0.6 * ease_back(pp, 2.4)
        ctx.save()
        ctx.translate(540, 1470)
        ctx.rotate(-0.03)
        ctx.scale(sc, sc)
        rrect(ctx, -w / 2, -h / 2, w, h, h / 2)
        ctx.set_source_rgba(*rgba(YELLOW))
        ctx.fill()
        blit(ctx, sp.surf, 0, 0, sp.pad + sp.adv / 2, sp.pad + sp.asc * 0.62)
        ctx.restore()
    npp = prog(lt, HOOK["note"], 0.4)
    if npp > 0:
        sp = text_sprite("3 soalan. Teka dulu sebelum jawapan keluar!", "hand", 56, WHITE)
        blit(ctx, sp.surf, 540, 1575 + (1 - ease_out(npp)) * 20, sp.pad + sp.adv / 2, sp.pad + sp.asc * 0.6,
             alpha=clamp(npp * 3))


QUIZ_STYLE = {
    "q1": dict(bg=ROSE, stripe=WHITE, photo="photo_mirror", rot=-0.025, right_fill=WINE),
    "q2": dict(bg=WINE, stripe=ROSE, photo="photo_bridge", rot=0.022, right_fill=ROSE),
    "q3": dict(bg=ROSE, stripe=YELLOW, photo="photo_climb", rot=-0.02, right_fill=WINE),
}


def scene_quiz(ctx, t, lt, q):
    d, st = QUIZ[q], QUIZ_STYLE[q]
    bg_quiz(ctx, t, st["bg"], st["stripe"], seed=d["n"])
    # header pill + progress dots
    chip(ctx, lt, 0.05, f"SOALAN {d['n']}/3", 540, 240, fill=WHITE, color=WINE, size=36)
    for i in range(3):
        dp = prog(lt, 0.15 + i * 0.05, 0.3)
        if dp > 0:
            r = 11 if i + 1 != d["n"] else 15
            ctx.arc(510 + i * 30, 318, r * ease_back(dp), 0, 2 * math.pi)
            ctx.set_source_rgba(*rgba(YELLOW if i + 1 <= d["n"] else WHITE, 0.95 if i + 1 <= d["n"] else 0.5))
            ctx.fill()

    # card motion: swipe in from right, swipe out to left at exit
    cin = ease_back(prog(lt, d["card"], 0.55), 1.3)
    cout = ease_in(prog(lt, d["exit"], 0.35))
    cx = 540 + (1 - cin) * 1000 - cout * 1250
    rot = st["rot"] + (1 - cin) * 0.25 - cout * 0.35
    shake = 0.0
    if lt > d["ans"]:
        k = lt - d["ans"]
        shake = math.exp(-10 * k) * math.sin(k * 60) * 10
    cy = 650
    cw, chh = 880, 500

    # polaroid peeking behind the card
    pp = ease_out(prog(lt, d["card"] + 0.25, 0.5))
    if pp > 0 and cout < 1:
        photo_card(ctx, st["photo"], cx + 300 + (1 - pp) * 40, cy - 250 - pp * 40, 270, 300,
                   rot=rot + 0.14, inner_zoom=1.05, border=10, r=18)
    # card
    ctx.save()
    ctx.translate(cx + shake, cy)
    ctx.rotate(rot)
    sh, pad = shadow_surface(cw, chh, 44, 26, 80)
    blit(ctx, sh, 0, 24, pad + cw / 2, pad + chh / 2)
    rrect(ctx, -cw / 2, -chh / 2, cw, chh, 44)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()
    qm = text_sprite("“", "serif", 220, ROSE)
    blit(ctx, qm.surf, -cw / 2 + 70, -chh / 2 + 70, qm.pad + qm.adv / 2, qm.pad + qm.asc * 0.55, alpha=0.9)
    lines = [[Tok(s, "stmt")] for s in d["statement"]]
    placed = layout(lines, 0, 0, maxw=cw - 120)
    hgt = layout_bottom(placed)
    placed = layout(lines, 0, -hgt / 2 + 6, maxw=cw - 120)
    fx.draw_words(ctx, lt, placed, d["card"] + 0.2, 0.08, mode="rise")
    # MITOS: strike the statement through
    if d["answer"] == "MITOS":
        for i, (tk, spr, x, base) in enumerate(placed):
            kp = ease_out(prog(lt, d["ans"] + 0.08 + i * 0.08, 0.25))
            if kp > 0:
                yy = base - spr.asc * 0.32
                ctx.move_to(x - 14, yy + 4)
                ctx.line_to(x + spr.adv + 14, yy - 4)
                fx.stroke_partial(ctx, kp, 10, ROSE, 0.9)
    # stamp
    sp_ = prog(lt, d["ans"], 0.18)
    if sp_ > 0:
        col = WINE if d["answer"] == "MITOS" else GREEN
        ss = stamp_surface(d["answer"] + "!", col)
        sc = 2.6 - 1.6 * ease_in(sp_)
        blit(ctx, ss, 250, 175, ss.get_width() / 2, ss.get_height() / 2, sc=sc * 0.62, rot=-0.18,
             alpha=clamp(sp_ * 2.5))
    ctx.restore()

    # timer bar during the countdown
    c0, cl = d["count"], d["count_len"]
    tp = prog(lt, c0 - 0.2, 0.25)
    if tp > 0 and lt < d["ans"] + 0.25:
        fade = 1 - prog(lt, d["ans"], 0.25)
        bx, by, bw, bh = 160, 975, 760, 24
        rrect(ctx, bx, by, bw, bh, bh / 2)
        ctx.set_source_rgba(1, 1, 1, 0.3 * fade * tp)
        ctx.fill()
        rem = 1 - prog(lt, c0, cl)
        if rem > 0:
            rrect(ctx, bx, by, bw * rem, bh, bh / 2)
            ctx.set_source_rgba(*rgba(YELLOW, fade * tp))
            ctx.fill()
        tsp = text_sprite("Teka dulu...", "hand", 52, WHITE)
        blit(ctx, tsp.surf, 540, 937, tsp.pad + tsp.adv / 2, tsp.pad + tsp.asc * 0.6, alpha=fade * tp * 0.95)

    # answer buttons
    for i, (label, bx) in enumerate((("MITOS", 300), ("FAKTA", 780))):
        bp = prog(lt, d["count"] - 0.3 + i * 0.08, 0.4)
        if bp <= 0 or cout >= 1:
            continue
        correct = label == d["answer"]
        ap = prog(lt, d["ans"], 0.25)
        pulse = 1 + 0.035 * math.sin((lt - d["count"]) * 2 * math.pi * 2) * (d["count"] < lt < d["ans"])
        sc = (0.5 + 0.5 * ease_back(bp, 2.2)) * pulse * (1 + 0.12 * ease_back(ap) * correct - 0.08 * ap * (not correct))
        alpha = clamp(bp * 3) * (1 - 0.65 * ap * (not correct)) * (1 - cout)
        fill = WHITE if not (correct and ap > 0) else st["right_fill"]
        tcol = WINE if not (correct and ap > 0) else WHITE
        sp = text_sprite(label, "brico", 64, tcol)
        w, h = 400, 128
        ctx.save()
        ctx.translate(bx - cout * 300, 1085)
        ctx.scale(sc, sc)
        rrect(ctx, -w / 2, -h / 2 + 8, w, h, h / 2)
        ctx.set_source_rgba(0, 0, 0, 0.12 * alpha)
        ctx.fill()
        rrect(ctx, -w / 2, -h / 2, w, h, h / 2)
        ctx.set_source_rgba(*rgba(fill, alpha))
        ctx.fill()
        blit(ctx, sp.surf, (24 if correct and ap > 0 else 0), 0, sp.pad + sp.adv / 2, sp.pad + sp.asc * 0.6,
             alpha=alpha)
        if correct and ap > 0:
            draw_check(ctx, -w / 2 + 52, 0, 26 * ease_back(ap, 2.5), YELLOW, WINE, alpha)
        ctx.restore()

    # explanation
    toks = []
    for line in d["explain"]:
        row = []
        for wd in line:
            if wd.startswith("*"):
                row.append(Tok(wd[1:], "ex_y"))
            elif wd.startswith("#"):
                row.append(Tok(wd[1:], "ex_hl", hl=YELLOW))
            else:
                row.append(Tok(wd, "ex"))
        toks.append(row)
    placed = layout(toks, 540, 1225)
    fx.draw_words(ctx, lt, placed, d["expl"], 0.06, alpha=1 - cout)


def sunburst(ctx, cx, cy, t, col, alpha):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(t * 0.12)
    for i in range(16):
        a0 = i * 2 * math.pi / 16
        ctx.move_to(0, 0)
        ctx.arc(0, 0, 1400, a0, a0 + math.pi / 16)
        ctx.close_path()
    ctx.set_source_rgba(*rgba(col, alpha))
    ctx.fill()
    ctx.restore()


def scene_reveal(ctx, t, lt):
    ctx.set_source_rgb(*rgba(BLUSH)[:3])
    ctx.rectangle(0, 0, W, H)
    ctx.fill()
    bp = ease_out(prog(lt, 0.0, 0.8))
    sunburst(ctx, 540, 820, t, PINK, 0.55 * bp)
    g = cairo.RadialGradient(540, 820, 0, 540, 820, 520)
    g.add_color_stop_rgba(0, *rgba(YELLOW, 0.45 * bp))
    g.add_color_stop_rgba(1, *rgba(YELLOW, 0))
    ctx.set_source(g)
    ctx.arc(540, 820, 520, 0, 2 * math.pi)
    ctx.fill()

    head = layout([[Tok("Ketiak", "rev_h"), Tok("berpeluh?", "rev_h")],
                   [Tok("Dah tak risau lagi.", "rev_s", under=YELLOW)]], 540, 150)
    fx.draw_words(ctx, lt, head, REVEAL["head"], 0.12)

    # bottle drops in with a springy settle, then floats
    cp = prog(lt, REVEAL["card"], 0.6)
    if cp > 0:
        k = lt - REVEAL["card"]
        y = 820 - (1 - fx.spring(k * 1.4, 1.2, 4.5)) * 700
        rot = 0.05 * (1 - fx.spring(k * 1.4, 1.0, 4.0)) + math.sin(t * 1.4) * 0.015
        bs = bottle_surface(700)
        blit(ctx, bs, 540, y + math.sin(t * 1.6) * 8, bs.get_width() / 2, bs.get_height() / 2, rot=rot,
             alpha=clamp(cp * 4))
    for i, (dx, dy, s0, col) in enumerate(((-230, 470, 30, WHITE), (230, 520, 24, YELLOW), (-250, 1080, 20, ROSE),
                                           (250, 1030, 26, WHITE), (180, 430, 14, ROSE))):
        sp_ = prog(lt, REVEAL["logo"] + i * 0.15, 0.5)
        if sp_ > 0:
            s = s0 * (0.75 + 0.25 * math.sin(t * 5 + i)) * ease_back(sp_, 2)
            sparkle(ctx, 540 + dx, dy, s, clamp(sp_ * 3), col)

    # USP stickers around the bottle
    stickers = [("TAHAN PELUH & BAU", 255, 600, -0.10, WINE, WHITE),
                ("CEPAT KERING", 830, 720, 0.09, YELLOW, WINE),
                ("0% ALKOHOL", 225, 1010, -0.07, WHITE, WINE),
                ("0% PARABEN", 860, 1090, 0.07, ROSE, WHITE)]
    times = list(REVEAL["stickers"]) + [REVEAL["stickers"][-1] + 0.35]
    for (txt, x, y, r, fill, col), t0 in zip(stickers, times):
        p = prog(lt, t0, 0.35)
        if p <= 0:
            continue
        sp = text_sprite(txt, "brico", 46, col)
        w, h = sp.adv + 56, 92
        sc = 0.3 + 0.7 * ease_back(p, 2.8)
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(r + math.sin(t * 2 + x) * 0.015)
        ctx.scale(sc, sc)
        sh, pad = shadow_surface(int(w), h, 24, 12, 70)
        blit(ctx, sh, 0, 10, pad + w / 2, pad + h / 2)
        rrect(ctx, -w / 2 - 7, -h / 2 - 7, w + 14, h + 14, 30)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
        rrect(ctx, -w / 2, -h / 2, w, h, 24)
        ctx.set_source_rgba(*rgba(fill))
        ctx.fill()
        blit(ctx, sp.surf, 0, 0, sp.pad + sp.adv / 2, sp.pad + sp.asc * 0.6)
        ctx.restore()

    lp = prog(lt, REVEAL["logo"], 0.6)
    if lp > 0:
        ls = logo_surface(WINE, 340)
        ctx.save()
        ctx.rectangle(540 - 190, 1180, 380 * ease_io(lp), 220)
        ctx.clip()
        blit(ctx, ls, 540, 1300, ls.get_width() / 2, ls.get_height() / 2)
        ctx.restore()
    np_ = prog(lt, REVEAL["name"], 0.4)
    if np_ > 0:
        sp = text_sprite("CELESTE MUSK DEODORANT ROLL-ON", "sb", 32, WINE, 4)
        blit(ctx, sp.surf, 540, 1418 + (1 - ease_out(np_)) * 16, sp.pad + sp.adv / 2, sp.pad + sp.asc * 0.62,
             alpha=clamp(np_ * 2.5))
    fx.draw_words(ctx, lt, layout([[Tok("Hidup aktif, keyakinan bermula di sini!", "slogan")]], 540, 1460),
                  REVEAL["slogan"], 0.1, mode="pop")
    ap = prog(lt, REVEAL["ask"], 0.4)
    if ap > 0:
        sp = text_sprite("Berapa soalan awak teka betul? Komen!", "hand", 52, WINE)
        blit(ctx, sp.surf, 540, 1585, sp.pad + sp.adv / 2, sp.pad + sp.asc * 0.6, alpha=clamp(ap * 3),
             sc=0.8 + 0.2 * ease_back(ap, 2), rot=-0.02)


def draw_scene(ctx, name, t):
    lt = t - S[name]
    i = ORDER.index(name)
    end = S[ORDER[i + 1]] if i + 1 < len(ORDER) else DUR
    z = 1.0 + 0.02 * clamp(lt / (end - S[name]))
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.translate(-W / 2, -H / 2)
    if name == "hook":
        scene_hook(ctx, t, lt)
    elif name == "reveal":
        scene_reveal(ctx, t, lt)
    else:
        scene_quiz(ctx, t, lt, name)
    ctx.restore()


def compose(ctx, t):
    cur = max((n for n in ORDER if S[n] <= t), key=lambda n: S[n])
    i = ORDER.index(cur)
    nxt = ORDER[i + 1] if i + 1 < len(ORDER) else None
    d = 0.3
    if nxt and nxt != "reveal" and t > S[nxt] - d:
        # wipe in: diagonal yellow-edged band covers the frame
        draw_scene(ctx, cur, t)
        p = ease_in(prog(t, S[nxt] - d, d))
        wipe(ctx, p, QUIZ_STYLE[nxt]["bg"], cover=True)
        return
    if i > 0 and cur != "reveal" and t < S[cur] + d:
        draw_scene(ctx, cur, t)
        p = ease_out(prog(t, S[cur], d))
        wipe(ctx, p, QUIZ_STYLE[cur]["bg"], cover=False)
        return
    if cur == "reveal" and t < S[cur] + 0.5:
        p = ease_io(prog(t, S[cur], 0.5))
        draw_scene(ctx, ORDER[i - 1], t)
        r = 1250 * p
        ctx.save()
        ctx.arc(540, 820, r, 0, 2 * math.pi)
        ctx.clip()
        draw_scene(ctx, cur, t)
        ctx.restore()
        ctx.arc(540, 820, r, 0, 2 * math.pi)
        ctx.set_source_rgba(*rgba(YELLOW))
        ctx.set_line_width(34 * (1 - p) + 6)
        ctx.stroke()
        return
    draw_scene(ctx, cur, t)


def wipe(ctx, p, col, cover):
    """Diagonal wipe along x + y = c with a yellow leading edge.
    cover=True: band grows from the bottom-right corner until it fills the frame.
    cover=False: band retreats to the top-left, revealing the scene underneath."""
    c = (W + H) * (1 - p)
    if cover:
        _band(ctx, c, W + H + 400, col)
        _band(ctx, c - 70, c, YELLOW)
    else:
        _band(ctx, -400, c - 70, col)
        _band(ctx, c - 70, c, YELLOW)


def _band(ctx, c0, c1, col):
    """Fill the region c0 <= x + y <= c1."""
    if c1 <= c0:
        return
    ctx.move_to(c0, 0)
    ctx.line_to(c1, 0)
    ctx.line_to(c1 - H, H)
    ctx.line_to(c0 - H, H)
    ctx.close_path()
    ctx.set_source_rgba(*rgba(col))
    ctx.fill()


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
        ff.stdin.write(bytes(render_frame(f / FPS).get_data()))
        if f % 90 == 0:
            print(f"frame {f}/{n}", flush=True)
    ff.stdin.close()
    ff.wait()
    print("wrote", out)


if __name__ == "__main__":
    main()
