"""T2 — Testimoni kad petikan (30s, 9:16). Customer B's real messages (poster 12), verbatim excerpts.

Big quote cards one at a time, highlighter on the key phrase, context icons (sun / moon / thumbs).
The worker in the hook is an ILLUSTRATION (not the customer). Ends on the real bottle photo.
"""
import math

import fx
import testi
from fx import (BLUSH, BLUSH2, PINK, ROSE, WHITE, WINE, WINE_D, YELLOW, blit, chip, clamp, draw_sun, ease_back,
                ease_in, ease_out, figure, glow, label, prog, rgba, rrect, shadow_surface, solid, stroke_partial,
                wipe, W, H)

DUR = 30.0
S = dict(hook=0.0, q1=3.2, q2=9.2, q3=15.2, q4=21.4, end=24.4)
ORDER = list(S)
QUOTES = {
    "q1": dict(text="Lega sangat bila pakai Firea, baju saya tak basah walaupun aktif bekerja. Memang terbaik!",
               hl="baju saya tak basah walaupun aktif bekerja.", bg=ROSE, icon="vest"),
    "q2": dict(text="Cuaca panas banget, tapi baju masih kering. Tak macam dulu, cepat basah peluh.",
               hl="tapi baju masih kering.", bg=(240, 150, 90), icon="sun"),
    "q3": dict(text="Paling best, ketiak pun tak berbau langsung. Walaupun lewat mandi sampai malam, masih rasa segar.",
               hl="ketiak pun tak berbau langsung.", bg=WINE, icon="moon"),
}
ATTR = "- Pelanggan B, kerja tapak projek"

fx.STY.update({"hookq": ("brico", 88, WHITE), "hooks": ("serif", 80, YELLOW), "attrw": ("hand", 54, WHITE),
               "big4": ("brico", 120, WHITE)})

MUSIC = dict(bpm=100, chords=[(43, [55, 59, 62, 67]), (40, [52, 55, 59, 64]), (36, [48, 52, 55, 60]),
                              (38, [50, 54, 57, 62])],
             sections=[(0, 0), (S["q1"], 2), (S["q2"], 3), (S["q4"], 3)], end_bell=(79, 83))


def cues():
    c = [(0.1, "click", 0.35), (0.6, "click", 0.35), (1.3, "swish", 0.45), (2.0, "pop", 0.4)]
    for k in ("q1", "q2", "q3"):
        c += [(S[k] - 0.3, "whoosh", 0.55), (S[k] + 0.25, "stamp_soft", 0.45), (S[k] + 1.8, "swish", 0.4),
              (S[k] + 2.6, "pop", 0.35)]
    c += [(S["q4"] - 0.3, "whoosh", 0.55), (S["q4"] + 0.15, "stamp", 0.65), (S["q4"] + 1.0, "sparkle", 0.45),
          (S["end"] - 0.3, "whoosh", 0.55), (S["end"] + 0.3, "sparkle", 0.4)]
    for i in range(4):
        c.append((S["end"] + 1.3 + i * 0.25, "stamp_soft", 0.45))
    return c


def hard_hat(ctx, x, y, s):
    ctx.save()
    ctx.translate(x, y)
    fx.sscale(ctx, s, s)
    ctx.arc(0, 0, 100, math.pi, 2 * math.pi)
    ctx.close_path()
    ctx.set_source_rgba(*rgba((250, 250, 245)))
    ctx.fill()
    rrect(ctx, -125, -8, 250, 26, 12)
    ctx.fill()
    ctx.rectangle(-14, -98, 28, 90)
    ctx.set_source_rgba(0.88, 0.88, 0.85, 1)
    ctx.fill()
    ctx.restore()


def scene_hook(ctx, t, lt):
    solid(ctx, WINE)
    glow(ctx, 760, 1400, 700, ROSE, 0.45)
    draw_sun(ctx, 880, 300, 60 * ease_back(prog(lt, 0.1, 0.5), 2), t)
    chip(ctx, lt, 0.05, "TESTIMONI PELANGGAN SEBENAR", 430, 200, fill=WHITE, color=WINE, size=30)
    q = fx.layout([[fx.Tok("“Kerja", "hookq"), fx.Tok("tapak", "hookq"), fx.Tok("projek,", "hookq")],
                   [fx.Tok("dari pagi sampai petang.", "hooks")],
                   [fx.Tok("Cuaca", "hookq"), fx.Tok("panas", "hookq"), fx.Tok("banget...”", "hookq")]], 540, 380)
    fx.draw_words(ctx, lt, q, 0.15, 0.12)
    fp = ease_out(prog(lt, 0.4, 0.6))
    if fp > 0:
        y = 1950 + (1 - fp) * 500
        figure(ctx, 540, y, 1.05, arm_r=(2.7, 3.0), arm_l=(0.2, 0.1), outfit=(205, 225, 70), hijab=(45, 40, 55),
               skirt=(60, 70, 110), mood="neutral", t=t, sweat=clamp(lt - 1.5))
        hard_hat(ctx, 540, y - 1.05 * 862, 1.0)
        label(ctx, "(ilustrasi)", "disc", 900, 1860, alpha=0.7 * fp)


def icon(ctx, kind, x, y, t, p):
    if p <= 0:
        return
    s = ease_back(p, 2)
    if kind == "sun":
        draw_sun(ctx, x, y, 70 * s, t)
    elif kind == "moon":
        ctx.arc(x, y, 70 * s, 0, 2 * math.pi)
        ctx.set_source_rgba(*rgba(YELLOW))
        ctx.fill()
        ctx.arc(x + 32 * s, y - 22 * s, 64 * s, 0, 2 * math.pi)
        ctx.set_source_rgba(*rgba(WINE))
        ctx.fill()
        for i, (dx, dy) in enumerate(((-150, 40), (130, 60), (170, -50))):
            fx.sparkle(ctx, x + dx, y + dy, 14 * s * (0.8 + 0.2 * math.sin(t * 4 + i)), 1.0, WHITE)
    else:
        hard_hat(ctx, x, y + 40, 0.75 * s)


def scene_quote(ctx, t, lt, k):
    q = QUOTES[k]
    solid(ctx, q["bg"])
    glow(ctx, 540, 900, 700, WHITE, 0.25)
    icon(ctx, q["icon"], 540, 300, t, prog(lt, 0.1, 0.5))
    n = list(QUOTES).index(k) + 1
    for i in range(3):
        ctx.arc(510 + i * 30, 460, 9 if i + 1 != n else 13, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, 1.0 if i + 1 <= n else 0.4)
        ctx.fill()
    cin = ease_out(prog(lt, 0.15, 0.5))
    if cin <= 0:
        return
    blk = testi.rich_block(q["text"], "sb", 60, WINE, 760, q["hl"], lead=1.36)
    cw, chh = 880, blk.h + 220
    cx, cy = 540, 560 + chh / 2 + (1 - cin) * 900
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(-0.02 + (1 - cin) * 0.1)
    sh, pad = shadow_surface(cw, int(chh), 44, 26, 90)
    blit(ctx, sh, 0, 24, pad + cw / 2, pad + chh / 2)
    rrect(ctx, -cw / 2, -chh / 2, cw, chh, 44)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()
    qm = fx.text_sprite("“", "serif", 240, ROSE)
    blit(ctx, qm.surf, -cw / 2 + 80, -chh / 2 + 60, qm.pad + qm.adv / 2, qm.pad + qm.asc * 0.55, alpha=0.9)
    # reveal lines top-to-bottom, then highlight
    rp = clamp((lt - 0.45) / 1.2)
    ctx.save()
    ctx.rectangle(-cw / 2, -chh / 2, cw, 120 + blk.h * rp + 20)
    ctx.clip()
    testi.draw_block(ctx, blk, -blk.w / 2, -chh / 2 + 120, lt, t_hl=1.8)
    ctx.restore()
    ctx.restore()
    ap = prog(lt, 2.6, 0.4)
    if ap > 0:
        label(ctx, ATTR, "attrw", 540, 560 + chh + 90, alpha=clamp(ap * 3), rot=-0.02)


def scene_q4(ctx, t, lt):
    solid(ctx, ROSE)
    glow(ctx, 540, 900, 700, YELLOW, 0.35)
    sp = fx.text_sprite("“Rugi kalau", "brico", 120, WHITE)
    sp2 = fx.text_sprite("tak cuba.”", "brico", 120, WHITE)
    for i, (s_, y) in enumerate(((sp, 720), (sp2, 870))):
        p = prog(lt, 0.1 + i * 0.25, 0.22)
        if p > 0:
            blit(ctx, s_.surf, 540, y, s_.pad + s_.adv / 2, s_.pad + s_.asc * 0.6, sc=2.0 - 1.0 * ease_in(p),
                 alpha=clamp(p * 3), rot=-0.03)
    bp = prog(lt, 0.9, 0.4)
    if bp > 0:
        blk = testi.rich_block("Firea memang the best! 👍💖", "sb", 64, WHITE, 1000, align="center")
        testi.draw_block(ctx, blk, 540 - blk.w / 2, 1010 + (1 - ease_out(bp)) * 30, lt, alpha=clamp(bp * 3))
    ap = prog(lt, 1.4, 0.4)
    if ap > 0:
        label(ctx, ATTR, "attrw", 540, 1230, alpha=clamp(ap * 3), rot=-0.02)


def scene_end(ctx, t, lt):
    testi.end_card(ctx, t, lt, headline="“Memang berbaloi!”")


def compose(ctx, t):
    cur = max((n for n in ORDER if S[n] <= t), key=lambda n: S[n])
    i = ORDER.index(cur)
    nxt = ORDER[i + 1] if i + 1 < len(ORDER) else None
    lt = t - S[cur]
    if cur in QUOTES:
        scene_quote(ctx, t, lt, cur)
    else:
        dict(hook=scene_hook, q4=scene_q4, end=scene_end)[cur](ctx, t, lt)
    d = 0.3
    cols = {"q1": ROSE, "q2": (240, 150, 90), "q3": WINE, "q4": ROSE, "end": WINE}
    if nxt and t > S[nxt] - d:
        wipe(ctx, ease_in(prog(t, S[nxt] - d, d)), cols[nxt], cover=True)
    elif i > 0 and t < S[cur] + d:
        wipe(ctx, ease_out(prog(t, S[cur], d)), cols[cur], cover=False)
