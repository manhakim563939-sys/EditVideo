"""V4 — "3 Red Flag Deodorant" (30s, 9:16) — punchy listicle.

Problem: discomfort many have had with deodorants (sticky, slow to dry, alcohol). Every "green flag"
answer is taken from the Firea label/posters: Non sticky, Quick dry / Cepat kering, 0% Alkohol, 0% Paraben.
No other brand is named or shown.
Flow: hook -> 3 red flags (red flag, caption, then the Firea green flag slides up) -> recap -> end.
"""
import math

import fx
from fx import (BLUSH, BLUSH2, CREAM, GREEN, PINK, RED, ROSE, WHITE, WINE, WINE_D, YELLOW, Tok, blit, bottle_drop,
                chip, clamp, draw_check, draw_droplet, draw_words, ease_back, ease_in, ease_io, ease_out, glow, label,
                layout, layout_bottom, logo, panel_wipe, pill, prog, rgba, rrect, shadow_surface, solid, text_sprite,
                W, H)

DUR = 30.0
S = dict(hook=0.0, f1=3.2, f2=8.2, f3=13.2, recap=18.2, end=24.0)
ORDER = list(S)
FLAGS = {
    "f1": dict(n=1, word="MELEKIT", cap="Rasa tak selesa bawah\nlengan baju...", green="Tak melekit",
               src="label: Non sticky", art="goo"),
    "f2": dict(n=2, word="LAMBAT KERING", cap="Kena tunggu lama\nsebelum pakai baju...", green="Cepat kering",
               src="label: Quick dry", art="clock"),
    "f3": dict(n=3, word="ADA ALKOHOL", cap="Ada yang lebih suka\nformula tanpa alkohol.", green="0% Alkohol",
               src="+ 0% Paraben", art="pct"),
}
GREEN_T = 2.7

fx.STY.update({"big": ("brico", 130, RED), "capw": ("hand", 62, WINE), "greenw": ("brico", 70, WHITE),
               "srcw": ("sb", 34, WHITE), "medw2": ("med", 62, WHITE), "serifp2": ("serif", 84, PINK),
               "list": ("brico", 64, WINE), "handp": ("hand", 58, PINK)})

MUSIC = dict(bpm=124, chords=[(45, [57, 60, 64, 67]), (41, [53, 57, 60, 65]), (43, [55, 59, 62, 67]),
                              (40, [52, 56, 59, 64])],
             sections=[(0, 2), (S["f1"], 3), (S["recap"], 3), (S["end"], 2)], pluck_gain=0.09, end_bell=(81, 84))


def cues():
    c = [(0.1, "stamp", 0.7), (0.5, "flag", 0.6), (0.9, "click", 0.4), (1.5, "swish", 0.4)]
    for k in ("f1", "f2", "f3"):
        t0 = S[k]
        c += [(t0 - 0.3, "whoosh", 0.55), (t0 + 0.15, "flag", 0.55), (t0 + 0.35, "buzzer", 0.4),
              (t0 + 0.4, "stamp", 0.65), (t0 + 1.3, "pop", 0.35), (t0 + GREEN_T, "swipe", 0.5),
              (t0 + GREEN_T + 0.15, "bell_ding", 0.45)]
    c += [(S["recap"] - 0.3, "whoosh", 0.55), (S["recap"] + 0.5, "impact", 0.5)]
    for i in range(5):
        c.append((S["recap"] + 1.3 + i * 0.4, "pop", 0.45))
    c += [(S["end"] - 0.3, "whoosh", 0.55), (S["end"] + 1.2, "sparkle", 0.45), (S["end"] + 3.0, "pop", 0.4)]
    return c


def red_flag(ctx, x, y, s, t, color=RED, alpha=1.0, pole=WINE):
    ctx.save()
    ctx.translate(x, y)
    fx.sscale(ctx, s, s)
    ctx.move_to(0, 0)
    ctx.line_to(0, 260)
    ctx.set_line_width(14)
    ctx.set_line_cap(1)
    ctx.set_source_rgba(*rgba(pole, alpha))
    ctx.stroke()
    ctx.move_to(4, 0)
    n = 12
    for i in range(n + 1):
        xx = 4 + i * 170 / n
        ctx.line_to(xx, math.sin(t * 7 - i * 0.6) * 12 * (i / n))
    for i in range(n, -1, -1):
        xx = 4 + i * 170 / n
        ctx.line_to(xx, 110 + math.sin(t * 7 - i * 0.6) * 12 * (i / n))
    ctx.close_path()
    ctx.set_source_rgba(*rgba(color, alpha))
    ctx.fill()
    ctx.restore()


def art(ctx, kind, x, y, t, p):
    if p <= 0:
        return
    s = ease_back(p, 2)
    ctx.save()
    ctx.translate(x, y)
    fx.sscale(ctx, s, s)
    if kind == "goo":
        rrect(ctx, -200, -120, 400, 90, 40)
        ctx.set_source_rgba(*rgba((200, 210, 120)))
        ctx.fill()
        for i, dx in enumerate((-150, -70, 20, 110, 170)):
            ln = 90 + 60 * (0.5 + 0.5 * math.sin(t * 2 + i * 1.7))
            ctx.move_to(dx - 18, -50)
            ctx.line_to(dx - 12, -50 + ln)
            ctx.arc(dx, -50 + ln, 14, math.pi, 0)
            ctx.line_to(dx + 18, -50)
            ctx.close_path()
            ctx.fill()
        ctx.set_source_rgba(1, 1, 1, 0.6)
        rrect(ctx, -160, -108, 120, 18, 9)
        ctx.fill()
    elif kind == "clock":
        ctx.arc(0, 0, 140, 0, 2 * math.pi)
        ctx.set_source_rgba(*rgba(WHITE))
        ctx.fill_preserve()
        ctx.set_line_width(16)
        ctx.set_source_rgba(*rgba(WINE))
        ctx.stroke()
        for ang, ln, wd in ((t * 4.0, 105, 9), (t * 0.4, 70, 14)):
            ctx.move_to(0, 0)
            ctx.line_to(math.sin(ang) * ln, -math.cos(ang) * ln)
            ctx.set_line_width(wd)
            ctx.stroke()
        for i, (dx, dy) in enumerate(((180, -60), (210, 60), (-200, 40))):
            draw_droplet(ctx, dx, dy + math.sin(t * 3 + i) * 10, 32, lw=4)
    else:
        ctx.arc(0, 0, 140, 0, 2 * math.pi)
        ctx.set_source_rgba(*rgba(WHITE))
        ctx.fill_preserve()
        ctx.set_line_width(16)
        ctx.set_source_rgba(*rgba(WINE))
        ctx.stroke()
        sp = text_sprite("%", "brico", 170, WINE)
        blit(ctx, sp.surf, 0, 6, sp.pad + sp.adv / 2, sp.pad + sp.asc * 0.6)
    ctx.restore()


# ---------------------------------------------------------------- scenes
def scene_hook(ctx, t, lt):
    solid(ctx, CREAM)
    glow(ctx, 760, 700, 600, PINK, 0.8)
    n = text_sprite("3", "brico", 420, ROSE)
    p0 = prog(lt, 0.05, 0.22)
    if p0 > 0:
        blit(ctx, n.surf, 300, 640, n.pad + n.adv / 2, n.pad + n.asc * 0.6, sc=2.2 - 1.2 * ease_in(p0),
             alpha=clamp(p0 * 3), rot=-0.05)
    fp = ease_back(prog(lt, 0.45, 0.45), 1.6)
    if fp > 0:
        red_flag(ctx, 620, 420 + (1 - fp) * 300, 1.6, t, alpha=clamp(fp * 3))
    p = layout([[Tok("RED FLAG", "big")]], 540, 900)
    draw_words(ctx, lt, p, 0.9, 0.0, mode="pop")
    p2 = layout([[Tok("deodorant", "xb"), Tok("yang", "xb"), Tok("wanita", "xb"), Tok("aktif", "xb")],
                 [Tok("tak perlukan.", "serifm", under=YELLOW)]], 540, layout_bottom(p) + 30)
    draw_words(ctx, lt, p2, 1.4, 0.08)


def scene_flag(ctx, t, lt, k):
    f = FLAGS[k]
    solid(ctx, CREAM)
    glow(ctx, 540, 900, 650, PINK, 0.7)
    chip(ctx, lt, 0.05, f"RED FLAG #{f['n']}", 540, 230, fill=RED, color=WHITE)
    fp = ease_back(prog(lt, 0.1, 0.4), 1.6)
    if fp > 0:
        red_flag(ctx, 150, 150, 0.55, t, alpha=clamp(fp * 3))
    wp = prog(lt, 0.4, 0.22)
    if wp > 0:
        sp = text_sprite(f["word"], "brico", 130, RED)
        sc = min(1.0, 860 / sp.adv)
        blit(ctx, sp.surf, 560, 520, sp.pad + sp.adv / 2, sp.pad + sp.asc * 0.6,
             sc=sc * (2.0 - 1.0 * ease_in(wp)), alpha=clamp(wp * 3), rot=-0.03)
    art(ctx, f["art"], 540, 880, t, prog(lt, 0.7, 0.45))
    fx.bubble(ctx, lt, 1.3, f["cap"], 540, 1210, style="capw", tail=(0, -1))
    # green flag card slides up
    gp = ease_out(prog(lt, GREEN_T, 0.45))
    if gp > 0:
        y = 1500 + (1 - gp) * 700
        w, h = 900, 250
        ctx.save()
        ctx.translate(540, y)
        ctx.rotate(-0.02)
        sh, pad = shadow_surface(w, h, 40, 20, 80)
        blit(ctx, sh, 0, 14, pad + w / 2, pad + h / 2)
        rrect(ctx, -w / 2, -h / 2, w, h, 40)
        ctx.set_source_rgba(*rgba(GREEN))
        ctx.fill()
        draw_check(ctx, -w / 2 + 90, 0, 52, WHITE, GREEN)
        l1 = text_sprite("FIREA:", "sb", 36, WHITE, 3)
        blit(ctx, l1.surf, -w / 2 + 180, -62, l1.pad, l1.pad + l1.asc * 0.6)
        l2 = text_sprite(f["green"], "brico", 76, WHITE)
        blit(ctx, l2.surf, -w / 2 + 180, 6, l2.pad, l2.pad + l2.asc * 0.6)
        l3 = text_sprite(f["src"], "sb", 30, WHITE)
        blit(ctx, l3.surf, -w / 2 + 182, 72, l3.pad, l3.pad + l3.asc * 0.6, alpha=0.85)
        ctx.restore()
        bs = fx.bottle_surface(330)
        blit(ctx, bs, 900, y - 60, bs.get_width() / 2, bs.get_height() / 2, rot=0.15 + math.sin(t * 2) * 0.03,
             sc=ease_back(prog(lt, GREEN_T + 0.2, 0.4), 2))


def scene_recap(ctx, t, lt):
    solid(ctx, BLUSH)
    glow(ctx, 330, 1000, 520, YELLOW, 0.45)
    p = layout([[Tok("Yang", "bricos"), Tok("ini", "bricos"), Tok("semua", "bricos")],
                [Tok("green flag!", "serifm", under=GREEN)]], 540, 200)
    draw_words(ctx, lt, p, 0.15, 0.1)
    bottle_drop(ctx, lt, 0.4, 300, 1000, 700)
    items = ["Tak melekit", "Cepat kering", "0% Alkohol", "0% Paraben", "Tahan peluh & bau"]
    for i, it in enumerate(items):
        ip = prog(lt, 1.3 + i * 0.4, 0.35)
        if ip <= 0:
            continue
        y = 640 + i * 150
        e = ease_back(ip, 2)
        draw_check(ctx, 600, y, 34 * e, GREEN, WHITE)
        sp = text_sprite(it, "brico", 56 if len(it) < 14 else 48, WINE)
        blit(ctx, sp.surf, 660 + (1 - ease_out(ip)) * 40, y, sp.pad, sp.pad + sp.asc * 0.6, alpha=clamp(ip * 3))


def scene_end(ctx, t, lt):
    solid(ctx, WINE)
    glow(ctx, 540, 600, 650, ROSE, 0.35)
    p = layout([[Tok("Ketiak", "medw2"), Tok("berpeluh?", "medw2")],
                [Tok("Dah tak risau lagi.", "serifp2", under=YELLOW)]], 540, 330)
    draw_words(ctx, lt, p, 0.15, 0.12)
    logo(ctx, lt, 0.9, 540, 860, 360, color=WHITE)
    pp = prog(lt, 1.4, 0.4)
    if pp > 0:
        label(ctx, "CELESTE MUSK DEODORANT ROLL-ON", "srcw", 540, 1000, alpha=clamp(pp * 3))
    fp = ease_back(prog(lt, 2.2, 0.45), 1.6)
    if fp > 0:
        red_flag(ctx, 90, 1120, 0.6, t, color=GREEN, alpha=clamp(fp * 3), pole=WHITE)
    fx.bubble(ctx, lt, 3.0, "Red flag mana yang paling\nawak tak suka? Komen!", 610, 1330, style="capw",
              tail=(-1, 1))


fx.STY["capw"] = ("hand", 60, WINE)
SCENES = dict(hook=scene_hook, recap=scene_recap, end=scene_end)


def compose(ctx, t):
    cur = max((n for n in ORDER if S[n] <= t), key=lambda n: S[n])
    i = ORDER.index(cur)
    nxt = ORDER[i + 1] if i + 1 < len(ORDER) else None
    lt = t - S[cur]
    end = S[nxt] if nxt else DUR

    def draw(name, tt, dx=0.0):
        llt = tt - S[name]
        z = 1.0 + 0.02 * clamp(llt / ((S[ORDER[ORDER.index(name) + 1]] if name != "end" else DUR) - S[name]))
        ctx.save()
        ctx.translate(dx, 0)
        ctx.translate(W / 2, H / 2)
        fx.sscale(ctx, z, z)
        ctx.translate(-W / 2, -H / 2)
        if name in FLAGS:
            scene_flag(ctx, tt, llt, name)
        else:
            SCENES[name](ctx, tt, llt)
        ctx.restore()

    # flags push sideways like a carousel; other cuts use colour panels
    if nxt in FLAGS and t > S[nxt] - 0.25:
        e = ease_io(prog(t, S[nxt] - 0.25, 0.5))
        draw(cur, t, -W * e)
        draw(nxt, max(t, S[nxt]), W * (1 - e))
        return
    if cur in FLAGS and t < S[cur] + 0.25 and i > 0:
        e = ease_io(prog(t, S[cur] - 0.25, 0.5))
        draw(ORDER[i - 1], t, -W * e)
        draw(cur, t, W * (1 - e))
        return
    draw(cur, t)
    cols = {"recap": (GREEN, YELLOW), "end": (WINE, ROSE)}
    if nxt in cols:
        panel_wipe(ctx, t, S[nxt], *cols[nxt])
    if cur in cols:
        panel_wipe(ctx, t, S[cur], *cols[cur])
