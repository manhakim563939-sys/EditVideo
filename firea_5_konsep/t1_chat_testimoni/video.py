"""T1 — Testimoni chat (31s, 9:16). Customer A's real messages (poster 11), verbatim excerpts.

Generic messenger UI in Firea colours (not a copy of any app). Customer = incoming (white),
Firea = outgoing (pink). Customer name/photo anonymised. Key phrases get a highlighter sweep.
Ends on the real bottle photo with disclaimer.
"""
import math

import fx
import testi
from fx import (BLUSH, BLUSH2, PINK, ROSE, WHITE, WINE, WINE_D, YELLOW, blit, chip, clamp, ease_io, ease_out, glow,
                label, panel_wipe, prog, rgba, rrect, solid, W, H)

DUR = 31.0
S = dict(hook=0.0, chat=3.0, end=24.5)
ORDER = list(S)

# (side, text, typing_start, appear, highlight_phrase, time)
MSGS = [
    ("in", "Salam sis.. nak share sikit laa 😄 Saya dah guna deodorant Firea ni lebih kurang 2 minggu. "
           "Memang best sangat! Bau badan dah tak ada langsung walaupun saya aktif seharian.",
     0.2, 0.8, "Bau badan dah tak ada langsung", "10:24"),
    ("out", "Waalaikumussallam 🌸 Alhamdulillah! Serius ke sis? Boleh cerita sikit pengalaman dia? 😊",
     5.0, 5.5, None, "10:25"),
    ("in", "Seriusss sis. Saya kerja luar, selalu berpeluh. Dulu memang cepat basah baju, lepas tu ada bau. "
           "Lepas guna Firea ni, baju saya dah tak basah walaupun aktif sangat. Ketiak pun tak berbau.",
     7.2, 7.8, "baju saya dah tak basah walaupun aktif sangat. Ketiak pun tak berbau.", "10:28"),
    ("in", "Paling best, saya selalu lewat mandi, ada kalanya sampai malam baru balik rumah. "
           "Tapi still tak ada bau pelik. Memang puas hati sangat!",
     14.6, 15.2, "Tapi still tak ada bau pelik.", "10:30"),
]
PH = dict(x0=60, x1=1020, y0=250, y1=1830, head=150, foot=110)
VIS_TOP = PH["y0"] + PH["head"] + 30
VIS_BOT = PH["y1"] - PH["foot"] - 20
GAP = 30
OUT_FILL = (252, 214, 226)

fx.STY.update({"quote": ("serif", 74, WINE), "attr": ("hand", 56, ROSE), "hname": ("sb", 40, WHITE),
               "hsub": ("med", 28, (255, 225, 235)), "hsub2": ("med", 28, (150, 140, 145))})

MUSIC = dict(bpm=92, chords=[(41, [53, 57, 60, 64]), (45, [57, 60, 64, 67]), (38, [50, 53, 57, 62]),
                             (46, [50, 53, 58, 62])],
             sections=[(0, 0), (S["chat"], 1), (S["chat"] + 7.2, 2), (S["end"], 3)], pluck_gain=0.08,
             duck=[(S["chat"], S["end"], 0.75)], end_bell=(77, 81), peak_db=-2.6)


def blocks():
    return [testi.rich_block(m[1], "med", 43, (40, 30, 35), 680, m[4]) for m in MSGS]


def cues():
    c = [(0.05, "impact_soft", 0.45), (0.4, "swish", 0.4), (1.6, "pop", 0.35), (S["chat"] - 0.3, "whoosh", 0.55)]
    for side, _, ty, ap, hl, _ in MSGS:
        for k in range(int((ap - ty) / 0.15)):
            c.append((S["chat"] + ty + k * 0.15, "key", 0.08))
        c.append((S["chat"] + ap, "pop", 0.5 if side == "in" else 0.35))
        if hl:
            c.append((S["chat"] + ap + 0.9, "swish", 0.3))
    c += [(S["end"] - 0.3, "whoosh", 0.55), (S["end"] + 0.3, "sparkle", 0.4)]
    for i in range(4):
        c.append((S["end"] + 1.3 + i * 0.25, "stamp_soft", 0.45))
    return c


# ---------------------------------------------------------------- scenes
def scene_hook(ctx, t, lt):
    solid(ctx, BLUSH)
    glow(ctx, 540, 900, 650, PINK, 0.9)
    chip(ctx, lt, 0.05, "TESTIMONI PELANGGAN SEBENAR", 540, 380, fill=WINE, color=WHITE, size=32)
    q = fx.text_sprite("“", "serif", 260, ROSE)
    blit(ctx, q.surf, 170, 600, q.pad + q.adv / 2, q.pad + q.asc * 0.5, alpha=prog(lt, 0.2, 0.3))
    p = fx.layout([[fx.Tok("Bau", "quote"), fx.Tok("badan", "quote"), fx.Tok("dah", "quote"), fx.Tok("tak", "quote")],
                   [fx.Tok("ada", "quote"), fx.Tok("langsung", "quote")],
                   [fx.Tok("walaupun", "quote"), fx.Tok("saya", "quote"), fx.Tok("aktif", "quote")],
                   [fx.Tok("seharian.", "quote")]], 540, 640)
    fx.draw_words(ctx, lt, p, 0.25, 0.09)
    ap = prog(lt, 1.6, 0.4)
    if ap > 0:
        label(ctx, "- pelanggan Firea, selepas ~2 minggu", "attr", 540, fx.layout_bottom(p) + 90, alpha=clamp(ap * 3))


def offsets(bl):
    """Scroll offset keyframes: before message i's typing indicator appears, scroll so it fits."""
    y = VIS_TOP
    tops, need = [], []
    for (side, _, ty, ap, _, _), b in zip(MSGS, bl):
        tops.append(y)
        bh = b.h + 64
        need.append(max(0, y + bh - VIS_BOT))
        y += bh + GAP
    for i in range(1, len(need)):
        need[i] = max(need[i], need[i - 1])
    return tops, need


def scene_chat(ctx, t, lt):
    solid(ctx, BLUSH2)
    glow(ctx, 540, 1000, 700, PINK, 0.6)
    pin = ease_out(prog(lt, 0, 0.5))
    dy = (1 - pin) * 1200
    x0, x1, y0, y1 = PH["x0"], PH["x1"], PH["y0"] + dy, PH["y1"] + dy
    ctx.save()
    sh, pad = fx.shadow_surface(x1 - x0, PH["y1"] - PH["y0"], 56, 30, 90)
    blit(ctx, sh, (x0 + x1) / 2, (y0 + y1) / 2 + 20, pad + (x1 - x0) / 2, pad + (y1 - y0) / 2)
    rrect(ctx, x0, y0, x1 - x0, y1 - y0, 56)
    ctx.set_source_rgba(*rgba((246, 238, 240)))
    ctx.fill()
    rrect(ctx, x0, y0, x1 - x0, y1 - y0, 56)
    ctx.clip()
    # wallpaper dots
    ctx.set_source_rgba(*rgba(PINK, 0.5))
    for gy in range(int(y0) + 180, int(y1), 70):
        for gx in range(x0 + 30 + (gy // 70 % 2) * 35, x1, 70):
            ctx.arc(gx, gy, 3, 0, 2 * math.pi)
            ctx.fill()
    bl = blocks()
    tops, need = offsets(bl)
    off = 0.0
    for i, (side, _, ty, ap, _, _) in enumerate(MSGS):
        prev = need[i - 1] if i else 0
        off = prev + (need[i] - prev) * ease_io(prog(lt, ty - 0.1, 0.45))
        if lt < ty:
            break
    ctx.save()
    ctx.rectangle(x0, y0 + PH["head"], x1 - x0, (y1 - y0) - PH["head"] - PH["foot"])
    ctx.clip()
    for i, ((side, _, ty, ap, hl, tm), b) in enumerate(zip(MSGS, bl)):
        top = tops[i] - off + dy
        if ty <= lt < ap + 0.05:
            tx = x0 + 40 if side == "in" else x1 - 40 - 130
            testi.typing(ctx, t, tx, top, fill=WHITE if side == "in" else OUT_FILL, alpha=clamp((lt - ty) * 5))
        if lt >= ap:
            edge = x0 + 40 if side == "in" else x1 - 40
            testi.chat_bubble(ctx, lt, ap, b, side, edge, top, WHITE if side == "in" else OUT_FILL, tm,
                              t_hl=(ap + 0.9) if hl else None)
    ctx.restore()
    # header
    ctx.rectangle(x0, y0, x1 - x0, PH["head"])
    ctx.set_source_rgba(*rgba(WINE))
    ctx.fill()
    ctx.arc(x0 + 100, y0 + 78, 44, 0, 2 * math.pi)
    ctx.set_source_rgba(*rgba(ROSE))
    ctx.fill()
    label(ctx, "A", "bricosw", x0 + 100, y0 + 80, sc=0.8)
    label(ctx, "Pelanggan A", "hname", x0 + 170, y0 + 60, anchor="l")
    label(ctx, "kerja luar  ·  online", "hsub", x0 + 170, y0 + 106, anchor="l")
    # input bar
    fy = y1 - PH["foot"]
    ctx.rectangle(x0, fy, x1 - x0, PH["foot"])
    ctx.set_source_rgba(1, 1, 1, 1)
    ctx.fill()
    rrect(ctx, x0 + 30, fy + 20, x1 - x0 - 170, 70, 35)
    ctx.set_source_rgba(*rgba((240, 236, 238)))
    ctx.fill()
    label(ctx, "Taip mesej...", "hsub2", x0 + 70, fy + 56, anchor="l")
    ctx.arc(x1 - 75, fy + 55, 38, 0, 2 * math.pi)
    ctx.set_source_rgba(*rgba(ROSE))
    ctx.fill()
    ctx.restore()


def scene_end(ctx, t, lt):
    testi.end_card(ctx, t, lt, headline="“Memang recommend sangat.”")


SCENES = dict(hook=scene_hook, chat=scene_chat, end=scene_end)


def compose(ctx, t):
    cur = max((n for n in ORDER if S[n] <= t), key=lambda n: S[n])
    i = ORDER.index(cur)
    nxt = ORDER[i + 1] if i + 1 < len(ORDER) else None
    SCENES[cur](ctx, t, t - S[cur])
    cols = {"chat": (ROSE, YELLOW), "end": (WINE, ROSE)}
    if nxt in cols:
        panel_wipe(ctx, t, S[nxt], *cols[nxt])
    if cur in cols:
        panel_wipe(ctx, t, S[cur], *cols[cur])
