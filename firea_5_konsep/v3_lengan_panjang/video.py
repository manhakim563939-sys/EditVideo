"""V3 — "Dilema Lengan Panjang" (30s, 9:16).

Problem: generic sweat advice (go sleeveless, avoid layers, let it breathe) doesn't fit women who
cover up every day. Flow: hook -> split screen NASIHAT INTERNET vs REALITI KITA (3 rows)
-> reframe "can't change how we dress, can choose the right protection" -> product -> end card using
Firea's own line "Khas untuk wanita bertudung ... walaupun sentiasa berlengan panjang."
120 BPM: beat 0.5 s.
"""
import math

import fx
from fx import (BLUSH, BLUSH2, PINK, RED, ROSE, WHITE, WINE, WINE_D, YELLOW, Tok, blit, bottle_drop, chip, clamp,
                draw_words, ease_back, ease_in, ease_out, figure, glow, label, layout, layout_bottom, logo, panel_wipe,
                photo_card, pill, prog, rgba, rrect, shadow_surface, solid, stroke_partial, sunburst, text_sprite, wipe,
                W, H)

DUR = 30.0
S = dict(hook=0.0, split=3.5, reframe=15.5, prod=20.0, end=26.0)
ORDER = list(S)
ROWS = [  # (advice, reality)
    ("Pakai baju\ntak berlengan", "Lengan panjang,\nsetiap hari"),
    ("Elak pakai\nberlapis", "Tudung + inner\n+ baju"),
    ("Biar ketiak\n\"bernafas\"", "Kain menutup,\nudara kurang"),
]
ROW_T = 4.0
GREY = (150, 140, 148)

fx.STY.update({"card": ("sb", 50, WINE), "cardg": ("sb", 50, GREY), "serifp2": ("serif", 80, PINK),
               "medw2": ("med", 64, WHITE), "handwine": ("hand", 58, WINE), "serifw": ("serif", 54, PINK)})

MUSIC = dict(bpm=120, chords=[(43, [55, 59, 62, 67]), (38, [50, 54, 57, 62]), (40, [52, 55, 59, 64]),
                              (36, [48, 52, 55, 60])],
             sections=[(0, 1), (S["split"], 2), (S["split"] + ROW_T, 3), (S["reframe"], 0), (S["prod"], 3)],
             lp_windows=[(S["reframe"], S["prod"] - 0.6, 1500)], swing=0.15, end_bell=(79, 83))


def cues():
    c = [(0.1, "click", 0.35), (0.5, "click", 0.35), (1.1, "stamp", 0.6), (S["split"] - 0.3, "whoosh", 0.55)]
    for i in range(3):
        t0 = S["split"] + 0.6 + i * ROW_T
        c += [(t0, "swipe", 0.45), (t0 + 1.0, "buzzer", 0.4), (t0 + 1.0, "stamp_soft", 0.55),
              (t0 + 1.6, "swipe", 0.45), (t0 + 1.8, "pop", 0.45)]
    c += [(S["reframe"] - 0.3, "whoosh", 0.6), (S["reframe"] + 2.2, "swish", 0.5),
          (S["prod"] - 1.2, "riser", 0.5), (S["prod"], "impact", 0.6)]
    for i in range(4):
        c.append((S["prod"] + 2.0 + i * 0.35, "stamp_soft", 0.5))
    c += [(S["end"] - 0.3, "whoosh", 0.55), (S["end"] + 1.8, "sparkle", 0.45)]
    return c


# ---------------------------------------------------------------- scenes
def scene_hook(ctx, t, lt):
    solid(ctx, BLUSH)
    glow(ctx, 540, 1400, 620, PINK, 0.9)
    p = layout([[Tok("Orang", "xb"), Tok("lain", "xb"), Tok("boleh", "xb"), Tok("pakai", "xb")],
                [Tok("baju", "xb"), Tok("tak", "xb"), Tok("berlengan.", "xb")]], 540, 240)
    draw_words(ctx, lt, p, 0.1, 0.07)
    k = text_sprite("KITA?", "brico", 200, ROSE)
    kp = prog(lt, 1.1, 0.22)
    if kp > 0:
        settle = math.exp(-9 * (lt - 1.32)) * math.sin((lt - 1.32) * 28) * 0.05 if lt > 1.32 else 0
        blit(ctx, k.surf, 540, 650, k.pad + k.adv / 2, k.pad + k.asc * 0.6, sc=2.2 - 1.2 * ease_in(kp) + settle,
             alpha=clamp(kp * 3), rot=-0.04)
    figure(ctx, 540, 1840, 1.05, arm_l=(0.5, 1.9), arm_r=(0.15, 0.08), mood="worried", t=t, sweat=clamp(lt - 1.6))
    fx.bubble(ctx, lt, 1.9, "Lengan panjang +\ntudung + panas...", 800, 900, style="handwine", tail=(-1, 1))


def card(ctx, x, y, w, h, text, style, fill, alpha, rot):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    sh, pad = shadow_surface(int(w), int(h), 30, 16, 60)
    blit(ctx, sh, 0, 12, pad + w / 2, pad + h / 2, alpha=alpha)
    rrect(ctx, -w / 2, -h / 2, w, h, 30)
    ctx.set_source_rgba(*rgba(fill, alpha))
    ctx.fill()
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        sp = text_sprite(ln, *fx.STY[style][:3])
        yy = (i - (len(lines) - 1) / 2) * 56
        blit(ctx, sp.surf, 0, yy, sp.pad + sp.adv / 2, sp.pad + sp.asc * 0.62, alpha=alpha)
    ctx.restore()


def scene_split(ctx, t, lt):
    solid(ctx, BLUSH2)
    ctx.rectangle(0, 0, W / 2, H)
    ctx.set_source_rgba(*rgba((236, 230, 233)))
    ctx.fill()
    ctx.rectangle(W / 2, 0, W / 2, H)
    ctx.set_source_rgba(*rgba(PINK))
    ctx.fill()
    # divider with "VS"
    ctx.rectangle(W / 2 - 3, 380, 6, 1450)
    ctx.set_source_rgba(*rgba(WINE, 0.25))
    ctx.fill()
    chip(ctx, lt, 0.05, "NASIHAT INTERNET", 275, 260, fill=GREY, color=WHITE, size=30)
    chip(ctx, lt, 0.2, "REALITI KITA", 810, 260, fill=ROSE, color=WHITE, size=30)
    for i, (adv, real) in enumerate(ROWS):
        t0 = 0.6 + i * ROW_T
        y = 560 + i * 400
        a_in = ease_back(prog(lt, t0, 0.45), 1.4)
        if a_in > 0:
            x_stamp = prog(lt, t0 + 1.0, 0.2)
            card(ctx, 275 - (1 - a_in) * 600, y, 440, 230, adv, "cardg" if x_stamp > 0 else "card", WHITE,
                 clamp(a_in * 2) * (1 - 0.35 * x_stamp), -0.03)
            if x_stamp > 0:
                # strike each line of the advice + red X badge in the corner
                n_lines = len(adv.split("\n"))
                for k in range(n_lines):
                    yy = y + (k - (n_lines - 1) / 2) * 56 - 6
                    ctx.move_to(275 - 170, yy + 6)
                    ctx.line_to(275 - 170 + 340 * ease_out(prog(lt, t0 + 1.0 + k * 0.08, 0.2)), yy - 6)
                    stroke_partial(ctx, 1, 8, RED, 0.85)
                ctx.save()
                ctx.translate(70, y - 100)
                sc = 2.0 - 1.0 * ease_in(x_stamp)
                fx.sscale(ctx, sc, sc)
                ctx.arc(0, 0, 32, 0, 2 * math.pi)
                ctx.set_source_rgba(*rgba(RED, clamp(x_stamp * 3)))
                ctx.fill()
                for s_ in (-1, 1):
                    ctx.move_to(-12, -12 * s_)
                    ctx.line_to(12, 12 * s_)
                stroke_partial(ctx, 1, 7, WHITE, clamp(x_stamp * 3))
                ctx.restore()
                if lt > t0 + 1.2:
                    label(ctx, "Tak praktikal", "handwine", 275, y + 160, alpha=prog(lt, t0 + 1.2, 0.3), rot=-0.05)
        r_in = ease_back(prog(lt, t0 + 1.6, 0.45), 1.4)
        if r_in > 0:
            card(ctx, 805 + (1 - r_in) * 600, y, 440, 230, real, "card", WHITE, clamp(r_in * 2), 0.03)
            ctx.save()
            ctx.translate(980, y - 100)
            fx.sscale(ctx, ease_back(prog(lt, t0 + 1.8, 0.35), 2.5), ease_back(prog(lt, t0 + 1.8, 0.35), 2.5))
            ctx.arc(0, 0, 30, 0, 2 * math.pi)
            ctx.set_source_rgba(*rgba(ROSE))
            ctx.fill()
            sp = text_sprite("!", "brico", 44, WHITE)
            blit(ctx, sp.surf, 0, 0, sp.pad + sp.adv / 2, sp.pad + sp.asc * 0.6)
            ctx.restore()


def scene_reframe(ctx, t, lt):
    solid(ctx, WINE)
    glow(ctx, 800, 500, 650, WINE_D, 0.9)
    p = layout([[Tok("Kita", "medw2"), Tok("tak", "medw2"), Tok("boleh", "medw2"), Tok("ubah", "medw2")],
                [Tok("cara kita berpakaian.", "serifp2")]], 540, 520)
    draw_words(ctx, lt, p, 0.15, 0.1)
    p2 = layout([[Tok("Tapi", "medw2"), Tok("kita", "medw2"), Tok("boleh", "medw2"), Tok("pilih", "medw2")],
                 [Tok("PERLINDUNGAN", "bricow", hl=ROSE)],
                 [Tok("yang", "medw2"), Tok("betul.", "medw2")]], 540, layout_bottom(p) + 110)
    draw_words(ctx, lt, p2, 1.9, 0.1)


def scene_prod(ctx, t, lt):
    solid(ctx, BLUSH)
    bp = ease_out(prog(lt, 0, 0.8))
    sunburst(ctx, 760, 900, t, PINK, 0.5 * bp)
    p = layout([[Tok("Lengan", "bricos"), Tok("panjang", "bricos"), Tok("setiap", "bricos"), Tok("hari?", "bricos")],
                [Tok("Firea faham.", "serifm", under=YELLOW)]], 540, 190)
    draw_words(ctx, lt, p, 0.1, 0.09)
    pc = ease_out(prog(lt, 0.3, 0.6))
    if pc > 0:
        photo_card(ctx, "photo_hook", 330 - (1 - pc) * 500, 880, 450, 590, rot=-0.05, inner_zoom=1.04 + 0.05 * lt / 6,
                   alpha=clamp(pc * 3))
    bottle_drop(ctx, lt, 0.8, 800, 900, 560)
    for i, (txt, x, y, r, fill, col) in enumerate((("Kawal peluh", 240, 1320, -0.05, WINE, WHITE),
                                                     ("Lindungi daripada bau", 715, 1320, 0.04, ROSE, WHITE),
                                                     ("Tak melekit", 300, 1450, -0.03, YELLOW, WINE),
                                                     ("0% Alkohol", 760, 1450, 0.05, WHITE, WINE))):
        pill(ctx, lt, 2.0 + i * 0.35, txt, x, y, fill, col, size=40, rot=r, icon="check")


def scene_end(ctx, t, lt):
    solid(ctx, WINE)
    glow(ctx, 540, 1500, 700, ROSE, 0.35)
    p = layout([[Tok("Khas", "medw2"), Tok("untuk", "medw2"), Tok("wanita", "medw2"), Tok("bertudung", "medw2")],
                [Tok("yang", "medw2"), Tok("aktif", "medw2"), Tok("seharian,", "medw2")],
                [Tok("walaupun sentiasa", "serifp2")], [Tok("berlengan panjang.", "serifp2", under=YELLOW)]],
               540, 260)
    draw_words(ctx, lt, p, 0.15, 0.08)
    logo(ctx, lt, 1.6, 540, 1000, 340, color=WHITE)
    sp = prog(lt, 2.1, 0.4)
    if sp > 0:
        label(ctx, "confidence in every touch", "serifw", 540, 1130, alpha=clamp(sp * 3))
    fp = ease_back(prog(lt, 0.6, 0.6), 1.5)
    if fp > 0:
        wave = math.sin(t * 6) * 0.25
        figure(ctx, 540, 1920 + (1 - fp) * 400, 0.62, arm_l=(2.5 + wave, 2.8 + wave), arm_r=(2.5 - wave, 2.8 - wave),
               mood="happy", outfit=YELLOW, hijab=ROSE, t=t)


SCENES = dict(hook=scene_hook, split=scene_split, reframe=scene_reframe, prod=scene_prod, end=scene_end)


def compose(ctx, t):
    cur = max((n for n in ORDER if S[n] <= t), key=lambda n: S[n])
    i = ORDER.index(cur)
    nxt = ORDER[i + 1] if i + 1 < len(ORDER) else None
    lt = t - S[cur]
    end = S[nxt] if nxt else DUR
    z = 1.0 + 0.02 * clamp(lt / (end - S[cur]))
    ctx.save()
    ctx.translate(W / 2, H / 2)
    fx.sscale(ctx, z, z)
    ctx.translate(-W / 2, -H / 2)
    SCENES[cur](ctx, t, lt)
    ctx.restore()
    d = 0.3
    cols = {"split": PINK, "reframe": WINE, "prod": ROSE, "end": WINE}
    if nxt and t > S[nxt] - d:
        wipe(ctx, ease_in(prog(t, S[nxt] - d, d)), cols[nxt], cover=True)
    elif i > 0 and t < S[cur] + d:
        wipe(ctx, ease_out(prog(t, S[cur], d)), cols[cur], cover=False)
