"""V1 — "Momen Angkat Tangan" (30s, 9:16).

Problem: the fear isn't sweat itself — it's the moment you have to raise your arm and someone might notice.
Flow: hook question -> 4 everyday raise-your-arm moments (illustrated, with inner thoughts)
      -> reframe question -> product (brief USP + label claims) -> payoff on the real photo (9.jpg).
96 BPM: beat 0.625 s, bar 2.5 s. Each moment = 1 bar.
"""
import math

import cairo

from fx import (BLUSH, BLUSH2, GREEN, PINK, ROSE, WHITE, WINE, WINE_D, YELLOW, Tok, blit, bottle_drop, bubble,
                chip, clamp, draw_words, ease_back, ease_io, ease_out, figure, full_photo, glow, label, layout,
                layout_bottom, logo, panel_wipe, pill, prog, rgba, rrect, solid, sunburst, vgrad, wipe, W, H)

DUR = 30.0
S = dict(hook=0.0, m1=3.75, m2=6.25, m3=8.75, m4=11.25, q=13.75, prod=17.5, end=23.75)
ORDER = list(S)
MOMENTS = {
    "m1": dict(n=1, title="Pegang handle LRT", think="Harap orang sebelah\ntak perasan...", bg=PINK),
    "m2": dict(n=2, title="Angkat tangan masa meeting", think="Basah tak lengan\nbaju aku?", bg=BLUSH2),
    "m3": dict(n=3, title="Ambil barang di rak atas", think="Cepat-cepat...\njangan lama sangat!", bg=PINK),
    "m4": dict(n=4, title="Peluk kawan baik", think="Eh... bau tak aku?", bg=BLUSH2),
}

MUSIC = dict(bpm=96, chords=[(41, [53, 57, 60, 64]), (38, [50, 53, 57, 62]), (46, [50, 53, 58, 62]),
                             (48, [52, 55, 60, 64])],
             sections=[(0, 0), (S["m1"], 1), (S["m3"], 2), (S["q"], 0), (S["prod"], 3), (S["end"], 2)],
             lp_windows=[(S["q"], S["prod"], 1600)], end_bell=(77, 81))


def cues():
    c = [(0.05, "impact_soft", 0.5), (0.3, "click", 0.35), (0.7, "swish", 0.4), (1.2, "pop", 0.45)]
    for k in ("m1", "m2", "m3", "m4"):
        c += [(S[k] - 0.25, "whoosh", 0.5), (S[k] + 0.2, "click", 0.4), (S[k] + 0.75, "pop", 0.45)]
    c += [(S["q"] - 0.25, "whoosh", 0.6), (S["q"] + 1.4, "swish", 0.45), (S["q"] + 2.3, "pop", 0.4),
          (S["prod"] - 1.2, "riser", 0.5), (S["prod"], "impact", 0.65)]
    for i in range(4):
        c.append((S["prod"] + 1.6 + i * 0.35, "stamp_soft", 0.5))
    c += [(S["end"] - 0.25, "whoosh", 0.55), (S["end"] + 0.4, "sparkle", 0.45), (S["end"] + 2.6, "sparkle", 0.35)]
    return c


# ---------------------------------------------------------------- scenes
def scene_hook(ctx, t, lt):
    solid(ctx, BLUSH)
    glow(ctx, 540, 1350, 600, PINK, 0.8)
    p = layout([[Tok("Pernah", "xb"), Tok("tak", "xb"), Tok("rasa", "xb")],
                [Tok("risau", "xb"), Tok("nak", "xb")],
                [Tok("ANGKAT TANGAN?", "bricow", hl=ROSE)]], 540, 250)
    draw_words(ctx, lt, p, 0.1, 0.12)
    # arm hesitates: up a little, back down, up again
    up = 0.5 * ease_io(prog(lt, 1.0, 0.5)) - 0.4 * ease_io(prog(lt, 1.7, 0.4)) + 0.9 * ease_io(prog(lt, 2.4, 0.6))
    a1 = 0.15 + 2.7 * clamp(up)
    figure(ctx, 540, 1780, 1.05, arm_r=(a1, a1 + 0.1), mood="worried", sweat=clamp(up * 1.5), t=t)
    if lt > 1.2:
        for i, (dx, dy) in enumerate(((-210, -880), (-260, -780))):
            q = prog(lt, 1.2 + i * 0.2, 0.3)
            label(ctx, "?", "serif", 540 + dx, 1780 + dy + math.sin(t * 3 + i) * 8, alpha=q,
                  sc=0.6 + 0.4 * ease_back(q), rot=-0.2 + i * 0.3)


def _lrt(ctx, t):
    """Overhead bar + straps; rings sit where the figures' raised hands are."""
    ctx.rectangle(0, 680, W, 26)
    ctx.set_source_rgba(*rgba((170, 160, 165)))
    ctx.fill()
    for x, ry in ((297, 941), (691, 899), (985, 900)):
        ctx.set_source_rgba(*rgba((120, 110, 115)))
        ctx.move_to(x, 700)
        ctx.line_to(x, ry - 34)
        ctx.set_line_width(12)
        ctx.stroke()
        ctx.arc(x, ry, 34, 0, 2 * math.pi)
        ctx.set_line_width(10)
        ctx.stroke()


def scene_moment(ctx, t, lt, k):
    m = MOMENTS[k]
    solid(ctx, m["bg"])
    glow(ctx, 540, 1300, 650, WHITE, 0.5)
    sway = math.sin(t * 2.2) * 0.03
    if k == "m1":
        _lrt(ctx, t)
        figure(ctx, 180, 1760, 0.95, arm_r=(2.95, 3.12), outfit=(190, 185, 195), hijab=(150, 140, 155),
               skirt=(130, 125, 140), t=t + 1)
        figure(ctx, 560, 1760, 1.0, arm_r=(2.92 + sway, 3.1 + sway), mood="worried", sweat=1.0, t=t)
    elif k == "m2":
        figure(ctx, 540, 1830, 1.0, arm_r=(3.02 + sway, 3.1), mood="worried", sweat=1.0, t=t)
        rrect(ctx, 90, 1500, 900, 80, 20)
        ctx.set_source_rgba(*rgba((196, 150, 120)))
        ctx.fill()
        ctx.rectangle(140, 1580, 40, 340)
        ctx.rectangle(900, 1580, 40, 340)
        ctx.fill()
        rrect(ctx, 220, 1360, 280, 150, 14)
        ctx.set_source_rgba(*rgba((70, 70, 80)))
        ctx.fill()
        rrect(ctx, 650, 1420, 200, 90, 10)
        ctx.set_source_rgba(1, 1, 1, 0.9)
        ctx.fill()
    elif k == "m3":
        ctx.rectangle(600, 990, 470, 26)
        ctx.set_source_rgba(*rgba((196, 150, 120)))
        ctx.fill()
        for i, (bx, bw, bh, col) in enumerate(((640, 120, 110, ROSE), (780, 100, 150, YELLOW), (900, 130, 90, WINE))):
            rrect(ctx, bx, 990 - bh, bw, bh, 10)
            ctx.set_source_rgba(*rgba(col))
            ctx.fill()
        reach = 2.45 + 0.04 * math.sin(t * 5)
        figure(ctx, 470, 1780, 1.0, arm_r=(reach, reach + 0.2), mood="worried", sweat=1.0, t=t)
    else:
        figure(ctx, 660, 1780, 0.98, arm_l=(2.0, 2.5), mood="happy", outfit=YELLOW, hijab=(90, 120, 170), t=t + 2,
               flip=False)
        figure(ctx, 420, 1780, 1.0, arm_r=(1.75 + sway, 1.95), mood="worried", sweat=1.0, t=t)
    chip(ctx, lt, 0.1, f"MOMEN {m['n']}", 540, 220, fill=WINE, color=WHITE)
    label_p = prog(lt, 0.15, 0.35)
    if label_p > 0:
        label(ctx, m["title"], "bricos", 540, 320 + (1 - ease_out(label_p)) * 20, alpha=clamp(label_p * 3))
    bubble(ctx, lt, 0.7, m["think"], 540, 520, style="hand", size=60)


def scene_q(ctx, t, lt):
    solid(ctx, WINE)
    glow(ctx, 300, 500, 600, WINE_D, 0.9)
    p = layout([[Tok("Kenapa", "medw"), Tok("kita", "medw"), Tok("kena", "medw"), Tok("risau", "medw")],
                [Tok("benda", "medw"), Tok("yang", "medw"), Tok("sepatutnya", "medw")],
                [Tok("NORMAL?", "bricow", hl=ROSE)]], 540, 560)
    draw_words(ctx, lt, p, 0.15, 0.1)
    y = layout_bottom(p) + 90
    p2 = layout([[Tok("Berpeluh", "serifp"), Tok("itu", "serifp"), Tok("normal.", "serifp")]], 540, y)
    draw_words(ctx, lt, p2, 1.4, 0.1)
    p3 = layout([[Tok("Yang", "handp"), Tok("buat", "handp"), Tok("kita", "handp"), Tok("risau:", "handp")],
                 [Tok("basah", "handp"), Tok("&", "handp"), Tok("bau.", "handp")]], 540, layout_bottom(p2) + 50)
    draw_words(ctx, lt, p3, 2.3, 0.08)


def scene_prod(ctx, t, lt):
    solid(ctx, BLUSH)
    bp = ease_out(prog(lt, 0, 0.8))
    sunburst(ctx, 540, 1000, t, PINK, 0.55 * bp)
    glow(ctx, 540, 1000, 520, YELLOW, 0.4 * bp)
    p = layout([[Tok("Bantu", "bricos"), Tok("kawal", "bricos"), Tok("peluh", "bricos")],
                [Tok("& lindungi daripada bau.", "serifm", under=YELLOW)]], 540, 190)
    draw_words(ctx, lt, p, 0.15, 0.1)
    bottle_drop(ctx, lt, 0.5, 540, 1000, 680)
    for i, (txt, x, y, r, fill, col) in enumerate((("Cepat kering", 250, 780, -0.09, YELLOW, WINE),
                                                     ("Tak melekit", 840, 900, 0.08, WHITE, WINE),
                                                     ("0% Alkohol", 240, 1180, -0.06, ROSE, WHITE),
                                                     ("0% Paraben", 850, 1260, 0.07, WINE, WHITE))):
        pill(ctx, lt, 1.6 + i * 0.35, txt, x, y, fill, col, size=46, rot=r, icon="check")
    logo(ctx, lt, 3.4, 540, 1500, 320)
    pop_p = prog(lt, 3.9, 0.4)
    if pop_p > 0:
        label(ctx, "CELESTE MUSK DEODORANT ROLL-ON", "sb", 540, 1625, alpha=clamp(pop_p * 3), sc=0.55)


def scene_end(ctx, t, lt):
    solid(ctx, WINE)
    full_photo(ctx, "photo_arm", 1.12 - 0.07 * clamp(lt / 6.25))
    vgrad(ctx, 0, 420, WINE_D, 0.75, 0.0)
    vgrad(ctx, 1050, H, WINE_D, 0.0, 0.85)
    logo(ctx, lt, 0.3, 540, 150, 300, color=WHITE)
    p = layout([[Tok("Angkat tangan", "bricow")], [Tok("tanpa risau.", "serify")]], 80, 1230, align="left")
    draw_words(ctx, lt, p, 0.4, 0.25)
    sp = prog(lt, 2.4, 0.5)
    if sp > 0:
        label(ctx, "confidence in every touch", "serifw", 80, 1545, alpha=clamp(sp * 3), anchor="l")


import fx  # noqa: E402

fx.STY.update({"serify": ("serif", 104, YELLOW), "serifw": ("serif", 50, WHITE),
               "handp": ("hand", 70, PINK)})

SCENES = dict(hook=scene_hook, q=scene_q, prod=scene_prod, end=scene_end)


def draw(ctx, name, t, dx=0.0):
    lt = t - S[name]
    i = ORDER.index(name)
    end = S[ORDER[i + 1]] if i + 1 < len(ORDER) else DUR
    z = 1.0 + 0.025 * clamp(lt / (end - S[name]))
    ctx.save()
    ctx.translate(dx, 0)
    ctx.translate(W / 2, H / 2)
    fx.sscale(ctx, z, z)
    ctx.translate(-W / 2, -H / 2)
    if name in MOMENTS:
        scene_moment(ctx, t, lt, name)
    else:
        SCENES[name](ctx, t, lt)
    ctx.restore()


def compose(ctx, t):
    cur = max((n for n in ORDER if S[n] <= t), key=lambda n: S[n])
    i = ORDER.index(cur)
    nxt = ORDER[i + 1] if i + 1 < len(ORDER) else None
    # moments slide in like swiping stories
    if nxt in MOMENTS and t > S[nxt] - 0.25:
        e = ease_io(prog(t, S[nxt] - 0.25, 0.5))
        draw(ctx, cur, t, -W * e)
        draw(ctx, nxt, max(t, S[nxt]), W * (1 - e))
        return
    if cur in MOMENTS and t < S[cur] + 0.25:
        e = ease_io(prog(t, S[cur] - 0.25, 0.5))
        draw(ctx, ORDER[i - 1], t, -W * e)
        draw(ctx, cur, t, W * (1 - e))
        return
    draw(ctx, cur, t)
    if nxt in ("q", "prod", "end"):
        col, col2 = {"q": (WINE, ROSE), "prod": (ROSE, YELLOW), "end": (WINE, YELLOW)}[nxt]
        panel_wipe(ctx, t, S[nxt], col, col2)
    if cur in ("q", "prod", "end"):
        col, col2 = {"q": (WINE, ROSE), "prod": (ROSE, YELLOW), "end": (WINE, YELLOW)}[cur]
        panel_wipe(ctx, t, S[cur], col, col2)
