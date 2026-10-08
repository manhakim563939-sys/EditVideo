"""T3 — Testimoni "Dulu vs Sekarang" (30s, 9:16). Both customers' real words (posters 11 & 12),
split into their own before/after halves — wording unchanged, only excerpted.

Each pair: DULU card (grey) -> arrow -> SEKARANG card (rose highlight), with attribution.
Ends on the real bottle photo.
"""
import math

import fx
import testi
from fx import (BLUSH, BLUSH2, GREEN, PINK, ROSE, WHITE, WINE, WINE_D, YELLOW, arrow, blit, chip, clamp, ease_back,
                ease_in, ease_io, ease_out, glow, label, panel_wipe, prog, rgba, rrect, shadow_surface, solid, W, H)

DUR = 30.0
S = dict(hook=0.0, p1=3.0, p2=10.0, p3=17.0, end=24.0)
ORDER = list(S)
GREY = (120, 112, 118)
PAIRS = {
    "p1": dict(before="Dulu memang cepat basah baju, lepas tu ada bau.",
               after="Lepas guna Firea ni, baju saya dah tak basah walaupun aktif sangat. Ketiak pun tak berbau.",
               hl="baju saya dah tak basah", who="- Pelanggan A, kerja luar"),
    "p2": dict(before="Tak macam dulu, cepat basah peluh.",
               after="Cuaca panas banget, tapi baju masih kering.",
               hl="tapi baju masih kering.", who="- Pelanggan B, kerja tapak projek"),
    "p3": dict(before="Paling best, saya selalu lewat mandi, ada kalanya sampai malam baru balik rumah.",
               after="Tapi still tak ada bau pelik. Memang puas hati sangat!",
               hl="Tapi still tak ada bau pelik.", who="- Pelanggan A, kerja luar"),
}

fx.STY.update({"dulu": ("brico", 190, GREY), "skrg": ("brico", 170, ROSE), "attrr": ("hand", 54, WINE),
               "sub": ("sb", 44, WINE)})

MUSIC = dict(bpm=96, chords=[(38, [50, 53, 57, 62]), (46, [50, 53, 58, 62]), (41, [53, 57, 60, 64]),
                             (48, [52, 55, 60, 64])],
             sections=[(0, 0), (S["p1"], 1), (S["p1"] + 2.6, 2), (S["p2"], 3)], end_bell=(77, 81))


def cues():
    c = [(0.1, "stamp", 0.6), (1.0, "stamp", 0.6), (1.9, "pop", 0.4)]
    for k in PAIRS:
        t0 = S[k]
        c += [(t0 - 0.3, "whoosh", 0.55), (t0 + 0.2, "stamp_soft", 0.4), (t0 + 2.3, "swish", 0.4),
              (t0 + 2.7, "pop", 0.5), (t0 + 3.6, "bell_ding", 0.35), (t0 + 4.2, "click", 0.3)]
    c += [(S["end"] - 0.3, "whoosh", 0.55), (S["end"] + 0.3, "sparkle", 0.4)]
    for i in range(4):
        c.append((S["end"] + 1.3 + i * 0.25, "stamp_soft", 0.45))
    return c


def scene_hook(ctx, t, lt):
    solid(ctx, (232, 226, 229))
    split = 960
    ctx.rectangle(0, split, W, H - split)
    ctx.set_source_rgba(*rgba(PINK))
    ctx.fill()
    chip(ctx, lt, 0.05, "KATA PELANGGAN FIREA SENDIRI", 540, 200, fill=WINE, color=WHITE, size=32)
    for i, (txt, st, y, t0) in enumerate((("DULU", "dulu", 560, 0.1), ("SEKARANG", "skrg", 1330, 1.0))):
        p = prog(lt, t0, 0.22)
        if p > 0:
            fn, size, col = fx.STY[st]
            sp = fx.text_sprite(txt, fn, size, col)
            sc = min(1.0, 940 / sp.adv) * (2.0 - 1.0 * ease_in(p))
            blit(ctx, sp.surf, 540, y, sp.pad + sp.adv / 2, sp.pad + sp.asc * 0.6, sc=sc, alpha=clamp(p * 3),
                 rot=-0.03 if i else 0.03)
    ap = prog(lt, 1.6, 0.4)
    if ap > 0:
        arrow(ctx, 540, 820, 540, 1100, ease_out(ap), 12, WINE, head=34)
    sp = prog(lt, 1.9, 0.4)
    if sp > 0:
        label(ctx, "Petikan ayat pelanggan sebenar.", "attrr", 540, 1600, alpha=clamp(sp * 3), rot=-0.02)


def card(ctx, x, y, w, blk, fill, title, title_fill, title_col, lt, t_hl, alpha, rot):
    h = blk.h + 150
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    sh, pad = shadow_surface(w, int(h), 40, 22, 70)
    blit(ctx, sh, 0, 18, pad + w / 2, pad + h / 2, alpha=alpha)
    rrect(ctx, -w / 2, -h / 2, w, h, 40)
    ctx.set_source_rgba(*rgba(fill, alpha))
    ctx.fill()
    tsp = fx.text_sprite(title, "xb", 34, title_col, 4)
    tw = tsp.adv + 56
    rrect(ctx, -w / 2 + 40, -h / 2 - 30, tw, 64, 32)
    ctx.set_source_rgba(*rgba(title_fill, alpha))
    ctx.fill()
    blit(ctx, tsp.surf, -w / 2 + 40 + tw / 2, -h / 2 + 2, tsp.pad + tsp.adv / 2, tsp.pad + tsp.asc * 0.6, alpha=alpha)
    testi.draw_block(ctx, blk, -blk.w / 2, -h / 2 + 70, lt, t_hl=t_hl, alpha=alpha)
    ctx.restore()
    return h


def scene_pair(ctx, t, lt, k):
    pr = PAIRS[k]
    solid(ctx, BLUSH2)
    glow(ctx, 540, 1300, 700, PINK, 0.8)
    n = list(PAIRS).index(k) + 1
    label(ctx, f"{n}/3", "sub", 980, 150, alpha=0.6)
    b1 = testi.rich_block(pr["before"], "sb", 54, (95, 85, 92), 800, lead=1.34)
    b2 = testi.rich_block(pr["after"], "sb", 58, WINE, 800, pr["hl"], lead=1.34)
    p1 = ease_out(prog(lt, 0.15, 0.5))
    total = (b1.h + 150) + 30 + 180 + (b2.h + 150) + 110
    y1 = max(260, 940 - total / 2) + (b1.h + 150) / 2
    if p1 > 0:
        dim = 1 - 0.25 * prog(lt, 2.6, 0.4)
        card(ctx, 540 - (1 - p1) * 900, y1, 900, b1, (238, 233, 236), "DULU", GREY, WHITE, lt, None,
             clamp(p1 * 3) * dim, 0.02)
    ya = y1 + (b1.h + 150) / 2 + 30
    ap = prog(lt, 2.0, 0.45)
    if ap > 0:
        arrow(ctx, 540, ya, 540, ya + 130, ease_out(ap), 12, ROSE, head=30)
    p2 = ease_back(prog(lt, 2.6, 0.5), 1.4)
    y2 = ya + 180 + (b2.h + 150) / 2
    if p2 > 0:
        card(ctx, 540 + (1 - p2) * 900, y2, 920, b2, WHITE, "SEKARANG", ROSE, WHITE, lt, 3.6, clamp(p2 * 3), -0.02)
    wp = prog(lt, 4.2, 0.4)
    if wp > 0:
        label(ctx, pr["who"], "attrr", 540, y2 + (b2.h + 150) / 2 + 80, alpha=clamp(wp * 3), rot=-0.02)


def scene_end(ctx, t, lt):
    testi.end_card(ctx, t, lt, headline="“Memang puas hati sangat!”")


def compose(ctx, t):
    cur = max((n for n in ORDER if S[n] <= t), key=lambda n: S[n])
    i = ORDER.index(cur)
    nxt = ORDER[i + 1] if i + 1 < len(ORDER) else None
    lt = t - S[cur]
    if cur in PAIRS:
        scene_pair(ctx, t, lt, cur)
    else:
        dict(hook=scene_hook, end=scene_end)[cur](ctx, t, lt)
    cols = {"p1": (ROSE, WINE), "p2": (WINE, ROSE), "p3": (ROSE, YELLOW), "end": (WINE, ROSE)}
    if nxt in cols:
        panel_wipe(ctx, t, S[nxt], *cols[nxt])
    if cur in cols:
        panel_wipe(ctx, t, S[cur], *cols[cur])
