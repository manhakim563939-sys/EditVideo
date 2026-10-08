"""R2 — "GRWM: Rutin Pagi Wanita Aktif" (30s, 9:16) in Instagram-Story style.

Story progress bars, story-style text boxes and stickers, one step per "story": shower & dry ->
apply Firea -> long sleeves & hijab -> out & active -> checklist recap with the real bottle.
Brand voice (no first-person result claims); product claims = approved USPs / label only.
"""
import math

import fx
import testi
from fx import (BLUSH, BLUSH2, CREAM, GREEN, PINK, ROSE, WHITE, WINE, WINE_D, YELLOW, blit, clamp, draw_check,
                draw_droplet, ease_back, ease_in, ease_io, ease_out, glow, label, logo, photo_card, pill, prog, rgba,
                rrect, solid, sparkle, vgrad, W, H)

DUR = 30.0
S = dict(s0=0.0, s1=3.0, s2=8.0, s3=13.0, s4=18.0, s5=23.0)
ORDER = list(S)
STEPS = {
    "s1": dict(n=1, text="Mandi, kemudian keringkan ketiak", photo=None, stickers=[]),
    "s2": dict(n=2, text="Sapu Firea Celeste Musk", photo="photo_mirror",
               stickers=[("Cepat kering", YELLOW, WINE, -0.06), ("Tak melekit", WHITE, WINE, 0.05)]),
    "s3": dict(n=3, text="Baju lengan panjang & tudung, siap!", photo="photo_ugc",
               stickers=[("Khas untuk wanita bertudung", ROSE, WHITE, -0.04)]),
    "s4": dict(n=4, text="Keluar & aktif seharian", photo="photo_climb",
               stickers=[("Tahan peluh & bau", WINE, WHITE, 0.04)]),
}

MUSIC = dict(bpm=104, chords=[(43, [55, 59, 62, 66]), (40, [52, 55, 59, 62]), (36, [48, 52, 55, 59]),
                              (38, [50, 54, 57, 62])],
             sections=[(0, 1), (S["s1"], 2), (S["s2"], 3), (S["s5"], 3)], swing=0.12, end_bell=(79, 83))


def cues():
    c = [(0.1, "pop", 0.4), (0.7, "pop", 0.4), (1.6, "swish", 0.35)]
    for k in ORDER[1:]:
        c += [(S[k] - 0.12, "swipe", 0.45), (S[k] + 0.4, "pop", 0.4)]
        if k in STEPS:
            c += [(S[k] + 2.6, "stamp_soft", 0.5), (S[k] + 2.65, "bell_ding", 0.3)]
            for i in range(len(STEPS[k]["stickers"])):
                c.append((S[k] + 1.3 + i * 0.4, "pop", 0.4))
    for i in range(4):
        c.append((S["s5"] + 0.5 + i * 0.35, "click", 0.4))
    c += [(S["s5"] + 2.4, "sparkle", 0.45), (S["s5"] + 3.4, "sparkle", 0.35)]
    return c


# ---------------------------------------------------------------- story chrome
def story_bars(ctx, t):
    vgrad(ctx, 0, 230, (40, 10, 20), 0.45, 0.0)
    n = len(ORDER)
    gap, x0, w = 10, 30, W - 60
    seg = (w - gap * (n - 1)) / n
    for i, k in enumerate(ORDER):
        st = S[k]
        en = S[ORDER[i + 1]] if i + 1 < n else DUR
        f = clamp((t - st) / (en - st))
        x = x0 + i * (seg + gap)
        rrect(ctx, x, 40, seg, 8, 4)
        ctx.set_source_rgba(1, 1, 1, 0.45)
        ctx.fill()
        if f > 0:
            rrect(ctx, x, 40, seg * f, 8, 4)
            ctx.set_source_rgba(1, 1, 1, 1)
            ctx.fill()
    ctx.arc(80, 110, 34, 0, 2 * math.pi)
    ctx.set_source_rgba(*rgba(ROSE))
    ctx.fill()
    ctx.arc(80, 110, 34, 0, 2 * math.pi)
    ctx.set_line_width(4)
    ctx.set_source_rgba(1, 1, 1, 1)
    ctx.stroke()
    fx.STY["avf"] = ("serif", 40, WHITE)
    label(ctx, "F", "avf", 80, 112)
    fx.STY["sthdr"] = ("sb", 32, WHITE)
    fx.STY["sthdr_s"] = ("sb", 32, (40, 10, 20))
    label(ctx, "Rutin pagi  ·  wanita aktif", "sthdr_s", 133, 113, anchor="l", alpha=0.35)
    label(ctx, "Rutin pagi  ·  wanita aktif", "sthdr", 130, 110, anchor="l")


def textbox(ctx, t, t0, text, x, y, fill=WHITE, col=WINE, size=56, maxw=860, rot=0.0):
    p = prog(t, t0, 0.35)
    if p <= 0:
        return 0
    blk = testi.rich_block(text, "sb", size, col, maxw, align="center")
    w, h = blk.w + 60, blk.h + 40
    sc = 0.6 + 0.4 * ease_back(p, 2.2)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    fx.sscale(ctx, sc, sc)
    rrect(ctx, -w / 2, -h / 2, w, h, 22)
    ctx.set_source_rgba(*rgba(fill, clamp(p * 3)))
    ctx.fill()
    testi.draw_block(ctx, blk, -blk.w / 2, -blk.h / 2, t, alpha=clamp(p * 3))
    ctx.restore()
    return h


def big_check(ctx, t, t0, x, y, r=80):
    p = prog(t, t0, 0.35)
    if p <= 0:
        return
    s = ease_back(p, 2.6)
    ctx.save()
    ctx.translate(x, y)
    fx.sscale(ctx, s, s)
    ctx.rotate(-0.12)
    draw_check(ctx, 0, 0, r, GREEN, WHITE)
    ctx.restore()


# ---------------------------------------------------------------- scenes
def scene_hook(ctx, t, lt):
    solid(ctx, WINE_D)
    fx.full_photo(ctx, "photo_arm", 1.12 - 0.05 * clamp(lt / 3))
    vgrad(ctx, 0, 300, (20, 5, 10), 0.5, 0.0)
    textbox(ctx, lt, 0.1, "GRWM: hari panjang ☀️", 430, 1160, fill=WHITE, col=WINE, size=62, rot=-0.03, maxw=800)
    textbox(ctx, lt, 0.7, "4 langkah rutin pagi wanita aktif 👇", 400, 1350, fill=ROSE, col=WHITE, size=48,
            rot=0.02, maxw=620)


def scene_step(ctx, t, lt, k):
    st = STEPS[k]
    solid(ctx, CREAM if not st["photo"] else BLUSH2)
    if st["photo"]:
        glow(ctx, 540, 800, 700, PINK, 0.8)
        pc = ease_out(prog(lt, 0.0, 0.45))
        photo_card(ctx, st["photo"], 540, 820 + (1 - pc) * 300, 900, 1080, rot=(-0.02 if st["n"] % 2 else 0.02),
                   inner_zoom=1.04 + 0.05 * clamp(lt / 5), alpha=clamp(pc * 3), border=16, r=30)
    else:
        # shower doodle: falling drops + towel
        glow(ctx, 540, 820, 600, PINK, 0.7)
        rrect(ctx, 400, 360, 280, 50, 25)
        ctx.set_source_rgba(*rgba((190, 190, 200)))
        ctx.fill()
        for i in range(18):
            x = 420 + (i * 53) % 260
            y = 440 + ((lt * 600 + i * 97) % 520)
            draw_droplet(ctx, x, y, 16, alpha=0.9 * (1 - prog(lt, 1.6, 0.5)), lw=3)
        tp = ease_back(prog(lt, 1.7, 0.5), 1.6)
        if tp > 0:
            ctx.save()
            ctx.translate(540, 820)
            ctx.rotate(-0.08)
            fx.sscale(ctx, tp, tp)
            rrect(ctx, -230, -150, 460, 300, 30)
            ctx.set_source_rgba(*rgba(PINK))
            ctx.fill()
            for yy in (-90, -60, 60, 90):
                ctx.rectangle(-230, yy, 460, 10)
            ctx.set_source_rgba(1, 1, 1, 0.8)
            ctx.fill()
            fx.STY["towel"] = ("hand", 64, WINE)
            label(ctx, "kering!", "towel", 0, 0)
            ctx.restore()
    textbox(ctx, lt, 0.4, f"{st['n']}. {st['text']}", 540, 1530, fill=WHITE, col=WINE, size=58)
    for i, (txt, fill, col, rot) in enumerate(st["stickers"]):
        pill(ctx, lt, 1.3 + i * 0.4, txt, 300 + i * 460 if len(st["stickers"]) > 1 else 540,
             1300 if st["photo"] else 1250, fill, col, size=44, rot=rot)
    big_check(ctx, lt, 2.6, 920, 330 if st["photo"] else 1150)


def scene_recap(ctx, t, lt):
    solid(ctx, CREAM)
    glow(ctx, 540, 600, 600, PINK, 0.8)
    textbox(ctx, lt, 0.1, "Checklist pagi ini ✨", 540, 260, fill=WINE, col=WHITE, size=56)
    for i, k in enumerate(("s1", "s2", "s3", "s4")):
        y = 430 + i * 120
        p = prog(lt, 0.5 + i * 0.35, 0.3)
        if p <= 0:
            continue
        draw_check(ctx, 130, y, 34 * ease_back(p, 2.4), GREEN, WHITE)
        fx.STY["chk"] = ("sb", 44, WINE)
        label(ctx, STEPS[k]["text"], "chk", 190, y, anchor="l", alpha=clamp(p * 3))
    pp = ease_out(prog(lt, 1.8, 0.5))
    if pp > 0:
        photo_card(ctx, "photo_real", 540, 1240 + (1 - pp) * 400, 520, 640, rot=0.04, inner_zoom=1.25,
                   alpha=clamp(pp * 3), border=16, r=12)
        for i, (dx, dy) in enumerate(((-300, -250), (310, -180), (-280, 260))):
            sp = prog(lt, 2.4 + i * 0.15, 0.5)
            sparkle(ctx, 540 + dx, 1240 + dy, 26 * ease_back(sp, 2), clamp(sp * 3), YELLOW if i % 2 else ROSE)
    logo(ctx, lt, 2.6, 540, 1680, 300)
    sp = prog(lt, 3.2, 0.4)
    if sp > 0:
        label(ctx, "Hidup aktif, keyakinan bermula di sini!", "slogan", 540, 1800, alpha=clamp(sp * 3), sc=0.85)


def compose(ctx, t):
    cur = max((n for n in ORDER if S[n] <= t), key=lambda n: S[n])
    i = ORDER.index(cur)
    nxt = ORDER[i + 1] if i + 1 < len(ORDER) else None

    def draw(name, tt, dx=0.0):
        ctx.save()
        ctx.translate(dx, 0)
        lt = tt - S[name]
        if name == "s0":
            scene_hook(ctx, tt, lt)
        elif name == "s5":
            scene_recap(ctx, tt, lt)
        else:
            scene_step(ctx, tt, lt, name)
        ctx.restore()

    if nxt and t > S[nxt] - 0.15:
        e = ease_io(prog(t, S[nxt] - 0.15, 0.3))
        draw(cur, t, -W * e)
        draw(nxt, max(t, S[nxt]), W * (1 - e))
    elif i > 0 and t < S[cur] + 0.15:
        e = ease_io(prog(t, S[cur] - 0.15, 0.3))
        draw(ORDER[i - 1], t, -W * e)
        draw(cur, t, W * (1 - e))
    else:
        draw(cur, t)
    story_bars(ctx, t)
