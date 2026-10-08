"""V5 — "Dear Ketiak" (30s, 9:16) — emotional, slightly funny letter.

Problem: the quiet embarrassment nobody talks about. A handwritten letter on notebook paper is
"written" line by line; the tone turns at "Tapi hari ni, aku dah ada geng baru." -> P.S. lines carry the
product facts (label/poster claims only) -> polaroid of the real user (9.jpg) -> sign-off + logo.
84 BPM lo-fi: beat 0.714 s, bar 2.857 s.
"""
import math

import cairo

import fx
from fx import (BLUSH, CREAM, PINK, RED, ROSE, WHITE, WINE, YELLOW, blit, bottle_drop, clamp, draw_droplet, draw_sun,
                ease_back, ease_in, ease_io, ease_out, glow, label, logo, photo_card, prog, rgba, rrect, sparkle,
                stroke_partial, text_sprite, W, H)

DUR = 30.0
BAR = 4 * 60 / 84
S = dict(p1=0.0, p2=6 * BAR, end=8.5 * BAR)  # 0, 17.14, 24.29
ORDER = list(S)
X0 = 165
CPS = 20  # handwriting speed (characters per second)

# (start, text, style, y)
P1 = [
    (-0.25, "Dear ketiak,", "h_big", 300),  # already being written on frame 0 (thumbnail)
    (1.30, "kita perlu bercakap.", "h", 420),
    (3.00, "Kau selalu buat aku tak yakin.", "h", 590),
    (4.80, "Masa meeting.", "h", 700),
    (5.90, "Masa panas terik.", "h", 800),
    (7.10, "Masa tak sempat mandi.", "h", 900),
    (8.60, "Sampai aku takut", "h", 1060),
    (9.50, "nak angkat tangan.", "h", 1160),
    (11.50, "Tapi hari ni,", "h_rose", 1340),
    (12.80, "aku dah ada geng baru.", "h_rose", 1450),
]
P2 = [
    (0.30, "P.S. Tahan peluh & bau.", "h", 330),
    (1.60, "P.P.S. Cepat kering &", "h", 440),
    (2.70, "tak melekit.", "h", 540),
    (3.40, "P.P.P.S. 0% alkohol", "h", 660),
    (4.45, "& 0% paraben.", "h", 760),
]
END = [
    (0.30, "Yang ikhlas,", "h", 300),
    (1.10, "Aku, yang dah yakin semula.", "h_rose", 400),
]

fx.STY.update({"h_big": ("hand", 112, WINE), "h": ("hand", 84, WINE), "h_rose": ("hand", 92, ROSE),
               "cap": ("hand", 52, WINE), "slogan2": ("serif", 46, ROSE)})

MUSIC = dict(bpm=84, chords=[(38, [50, 54, 57, 61]), (43, [55, 59, 62, 66]), (40, [52, 55, 59, 62]),
                             (45, [57, 61, 64, 69])],
             sections=[(0, 0), (BAR, 1), (4 * BAR, 2), (4.5 * BAR, 3)], swing=0.2, pluck_gain=0.085,
             lp_windows=[(0, 4 * BAR, 2200)], end_bell=(74, 78), pad_gain=0.08, peak_db=-2.7)


def _dur(text):
    return len(text) / CPS


def cues():
    c = []
    for base, lines in ((S["p1"], P1), (S["p2"], P2), (S["end"], END)):
        for t0, text, _, _ in lines:
            n = int(_dur(text) / 0.09)
            for k in range(n):
                c.append((base + t0 + k * 0.09, "key", 0.10 + 0.04 * (k % 2)))
    c += [(S["p1"] + 10.6, "pop", 0.3), (S["p1"] + 11.45, "sparkle", 0.4), (S["p1"] + 14.2, "impact_soft", 0.45),
          (S["p1"] + 14.6, "sparkle", 0.4), (S["p2"] - 0.35, "swish", 0.5), (S["p2"] + 5.2, "stamp_soft", 0.45),
          (S["end"] - 0.35, "swish", 0.5), (S["end"] + 2.6, "sparkle", 0.45), (S["end"] + 3.3, "pop", 0.4)]
    return c


# ---------------------------------------------------------------- paper + handwriting
def paper(ctx, t):
    ctx.set_source_rgb(*rgba(CREAM)[:3])
    ctx.rectangle(0, 0, W, H)
    ctx.fill()
    for y in range(230, H, 100):
        ctx.rectangle(0, y + 28, W, 3)
    ctx.set_source_rgba(0.55, 0.68, 0.85, 0.35)
    ctx.fill()
    ctx.rectangle(118, 0, 4, H)
    ctx.set_source_rgba(*rgba(ROSE, 0.55))
    ctx.fill()
    for y in (300, 960, 1620):
        ctx.arc(55, y, 22, 0, 2 * math.pi)
        ctx.set_source_rgba(0.85, 0.8, 0.75, 1)
        ctx.fill()


def write(ctx, t, t0, text, style, x, y):
    """Reveal handwriting left-to-right with a pen-tip dot."""
    if t < t0:
        return
    fn, size, col = fx.STY[style][:3]
    sp = text_sprite(text, fn, size, col)
    p = clamp((t - t0) / _dur(text))
    ctx.save()
    ctx.rectangle(x - sp.pad, y - 200, sp.pad + sp.adv * p + (sp.pad if p >= 1 else 0), 400)
    ctx.clip()
    blit(ctx, sp.surf, x, y, sp.pad, sp.pad + sp.asc * 0.62)
    ctx.restore()
    if p < 1:
        ctx.arc(x + sp.adv * p, y + 10 + math.sin(t * 40) * 6, 6, 0, 2 * math.pi)
        ctx.set_source_rgba(*rgba(col))
        ctx.fill()


def line_w(text, style):
    fn, size, col = fx.STY[style][:3]
    return text_sprite(text, fn, size, col).adv


def doodle(ctx, kind, x, y, p, t):
    if p <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    if kind == "sun":
        ctx.arc(0, 0, 26, 0, 2 * math.pi * ease_out(p))
        stroke_partial(ctx, 1, 5, YELLOW)
        for i in range(8):
            a = i * math.pi / 4
            q = clamp(p * 8 - i)
            if q > 0:
                ctx.move_to(math.cos(a) * 36, math.sin(a) * 36)
                ctx.line_to(math.cos(a) * (36 + 14 * q), math.sin(a) * (36 + 14 * q))
                stroke_partial(ctx, 1, 5, YELLOW)
    elif kind == "drop":
        fx.droplet_path(ctx, 22)
        stroke_partial(ctx, p, 5, (90, 140, 200))
    elif kind == "laptop":
        rrect(ctx, -34, -26, 68, 44, 6)
        ctx.move_to(-46, 24)
        ctx.line_to(46, 24)
        stroke_partial(ctx, p, 5, WINE)
    elif kind == "heart":
        ctx.move_to(0, 18)
        ctx.curve_to(-40, -10, -20, -40, 0, -18)
        ctx.curve_to(20, -40, 40, -10, 0, 18)
        stroke_partial(ctx, p, 6, ROSE)
    elif kind == "sad":
        ctx.arc(0, 0, 28, 0, 2 * math.pi)
        stroke_partial(ctx, p, 5, WINE)
        if p > 0.6:
            for ex in (-10, 10):
                ctx.arc(ex, -6, 3.5, 0, 2 * math.pi)
                ctx.set_source_rgba(*rgba(WINE))
                ctx.fill()
            ctx.arc(0, 16, 11, 1.15 * math.pi, 1.85 * math.pi)
            stroke_partial(ctx, 1, 4, WINE)
    ctx.restore()


def scene_p1(ctx, t, lt):
    paper(ctx, t)
    for t0, text, st, y in P1:
        write(ctx, lt, t0, text, st, X0, y)
    # doodles just after the end of their line
    for (t0, kind, li) in ((4.8 + 0.7, "laptop", 3), (5.9 + 0.9, "sun", 4), (7.1 + 1.1, "drop", 5),
                           (9.5 + 0.9, "sad", 7)):
        _, text, st, y = P1[li]
        doodle(ctx, kind, X0 + line_w(text, st) + 70, y - 8, prog(lt, t0, 0.5), t)
    # underline the turn
    up = prog(lt, 13.9, 0.5)
    if up > 0:
        ctx.move_to(X0, 1500)
        ctx.curve_to(X0 + 280, 1488, X0 + 560, 1512, X0 + 800, 1494)
        stroke_partial(ctx, up, 8, YELLOW)
    # bottle "arrives" on the page
    if lt > 14.2:
        bottle_drop(ctx, lt, 14.2, 830, 1680, 380, float_amp=4)
        for i, (dx, dy) in enumerate(((-140, -150), (130, -210), (150, 40))):
            sp_ = prog(lt, 14.6 + i * 0.15, 0.5)
            sparkle(ctx, 830 + dx, 1680 + dy, 20 * ease_back(sp_, 2), clamp(sp_ * 3), YELLOW if i % 2 else ROSE)


def tape(ctx, x, y, w, rot, alpha=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.rectangle(-w / 2, -22, w, 44)
    ctx.set_source_rgba(1.0, 0.92, 0.6, 0.75 * alpha)
    ctx.fill()
    ctx.restore()


def scene_p2(ctx, t, lt):
    paper(ctx, t)
    for t0, text, st, y in P2:
        write(ctx, lt, t0, text, st, X0, y)
    pp = prog(lt, 5.2, 0.5)
    if pp > 0:
        e = ease_out(pp)
        photo_card(ctx, "photo_arm", 560, 1270 + (1 - e) * 300, 500, 640, rot=0.04 - (1 - e) * 0.1,
                   inner_zoom=1.05 + 0.03 * (lt - 5.2) / 2, alpha=clamp(pp * 3), border=18, r=8)
        tape(ctx, 560, 950 + (1 - e) * 300, 180, -0.05, clamp(pp * 3))
        cp = prog(lt, 5.8, 0.6)
        if cp > 0:
            label(ctx, "aku, sekarang", "cap", 520, 1680, alpha=clamp(cp * 3), rot=-0.03)
            doodle(ctx, "heart", 720, 1675, cp, t)


def scene_end(ctx, t, lt):
    paper(ctx, t)
    for t0, text, st, y in END:
        write(ctx, lt, t0, text, st, X0, y)
    glow(ctx, 540, 900, 380, PINK, 0.8 * prog(lt, 2.0, 0.6))
    bottle_drop(ctx, lt, 2.2, 540, 900, 560, float_amp=5)
    logo(ctx, lt, 2.8, 540, 1360, 360)
    sp = prog(lt, 3.3, 0.4)
    if sp > 0:
        label(ctx, "confidence in every touch", "slogan2", 540, 1490, alpha=clamp(sp * 3))
    doodle(ctx, "heart", X0 + 50, 510, prog(lt, 2.4, 0.6), t)


SCENES = dict(p1=scene_p1, p2=scene_p2, end=scene_end)


def compose(ctx, t):
    cur = max((n for n in ORDER if S[n] <= t), key=lambda n: S[n])
    i = ORDER.index(cur)
    nxt = ORDER[i + 1] if i + 1 < len(ORDER) else None

    def draw(name, tt):
        llt = tt - S[name]
        end = S[ORDER[ORDER.index(name) + 1]] if name != "end" else DUR
        z = 1.0 + 0.02 * clamp(llt / (end - S[name]))
        ctx.save()
        ctx.translate(W / 2, H / 2)
        fx.sscale(ctx, z, z)
        ctx.translate(-W / 2, -H / 2)
        SCENES[name](ctx, tt, llt)
        ctx.restore()

    # page tear-off: the old page lifts up and away, revealing the next one
    d = 0.6
    if nxt and t > S[nxt] - d:
        e = ease_in(prog(t, S[nxt] - d, d))
        draw(nxt, max(t, S[nxt]))
        ctx.save()
        ctx.translate(W * 0.1 * e, -H * 1.1 * e)
        ctx.rotate(-0.18 * e)
        sh, pad = fx.shadow_surface(W, H, 4, 30, int(120 * (1 - e)))
        blit(ctx, sh, W / 2, H / 2 + 30, pad + W / 2, pad + H / 2)
        draw(cur, t)
        ctx.restore()
        return
    draw(cur, t)
