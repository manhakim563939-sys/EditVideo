"""M1 — "Montaj Hype Editorial" (30s, 9:16). Combines every asset: real photos (13 bottle, 4 user, 5 mirror,
9 arm-raise), poster photos (3 park, 7 bridge, 8 climbing), bottle cut-out, USPs, real customer quotes, slogans.

Beat-cut full-bleed photo montage (120 BPM, cuts on beats), giant type, flash hits, punch-ins.
Customer quotes appear only over product/plain backgrounds — never over a person's photo.
"""
import math

import cairo

import fx
import testi
from fx import (BLUSH, PINK, ROSE, WHITE, WINE, WINE_D, YELLOW, blit, clamp, ease_back, ease_in, ease_io, ease_out,
                full_photo, glow, label, logo, photo_card, pill, prog, rgba, rrect, solid, sunburst, vgrad, W, H)

DUR = 30.0
BEAT = 0.5
S = dict(hook=0.0, yakin=4.0, slam=6.0, usp=8.0, quotes=16.0, finale=24.0)
ORDER = list(S)
HOOK = [("PANAS.", "photo_climb", 0.0), ("BERPELUH.", "photo_bridge", 1.0), ("LENGAN\nPANJANG.", "photo_hook", 2.0),
        ("SEHARIAN.", "photo_mirror", 3.0)]
USPS = [("TAHAN PELUH\n& BAU", "photo_climb", WINE, 0.0), ("CEPAT\nKERING", "photo_bridge", ROSE, 2.0),
        ("TAK\nMELEKIT", "photo_mirror", YELLOW, 4.0), ("0% ALKOHOL\n0% PARABEN", None, WINE, 6.0)]
QUOTES = [("Bau badan dah tak ada langsung walaupun saya aktif seharian.", "Pelanggan A, kerja luar", 0.0),
          ("Cuaca panas banget, tapi baju masih kering.", "Pelanggan B, kerja tapak projek", 2.65),
          ("Tapi still tak ada bau pelik.", "Pelanggan A, kerja luar", 5.3)]

fx.STY.update({"mega": ("brico", 170, WHITE), "qtxt": ("sb", 62, WINE), "qwho": ("hand", 52, WINE),
               "kicker": ("xb", 34, WHITE)})

MUSIC = dict(bpm=120, chords=[(45, [57, 60, 64, 69]), (41, [53, 57, 60, 65]), (43, [55, 59, 62, 67]),
                              (40, [52, 55, 59, 64])],
             sections=[(0, 2), (S["yakin"], 0), (S["slam"], 3), (S["quotes"], 2), (S["finale"], 3)],
             lp_windows=[(S["yakin"], S["slam"], 1400)], pluck_gain=0.09, end_bell=(81, 84))


def cues():
    c = []
    for _, _, t0 in HOOK:
        c += [(t0, "stamp", 0.7), (t0 + 0.02, "impact_soft", 0.4)]
    c += [(S["yakin"], "whoosh", 0.5), (S["yakin"] + 0.6, "swish", 0.45), (S["slam"] - 1.2, "riser", 0.6),
          (S["slam"], "impact", 0.8), (S["slam"] + 0.4, "sparkle", 0.45)]
    for _, _, _, t0 in USPS:
        c += [(S["usp"] + t0 - 0.15, "swipe", 0.5), (S["usp"] + t0 + 0.35, "stamp_soft", 0.55)]
    c += [(S["quotes"] - 0.2, "whoosh", 0.5)]
    for _, _, t0 in QUOTES:
        c += [(S["quotes"] + t0 + 0.1, "pop", 0.45), (S["quotes"] + t0 + 0.9, "swish", 0.3)]
    c += [(S["finale"] - 0.25, "whoosh", 0.55)]
    for i in range(4):
        c.append((S["finale"] + 0.1 + i * 0.25, "stamp_soft", 0.45))
    c += [(S["finale"] + 1.4, "impact", 0.55), (S["finale"] + 1.6, "sparkle", 0.5), (S["finale"] + 3.0, "sparkle", 0.35)]
    return c


# ---------------------------------------------------------------- helpers
def mega(ctx, text, x, y, t, t0, size=170, col=WHITE, shadow=WINE_D, maxw=980, rot=-0.03):
    """Multi-line slam word with a hard drop shadow."""
    p = prog(t, t0, 0.18)
    if p <= 0:
        return
    lines = text.split("\n")
    sps = [fx.text_sprite(l_, "brico", size, col) for l_ in lines]
    shs = [fx.text_sprite(l_, "brico", size, shadow) for l_ in lines]
    sc = min(1.0, maxw / max(s_.adv for s_ in sps)) * (1.8 - 0.8 * ease_in(p))
    lh = size * 0.92 * sc
    y0 = y - lh * (len(lines) - 1) / 2
    for i, (s_, sh) in enumerate(zip(sps, shs)):
        yy = y0 + i * lh
        blit(ctx, sh.surf, x + 10, yy + 12, sh.pad + sh.adv / 2, sh.pad + sh.asc * 0.6, sc=sc, rot=rot,
             alpha=0.55 * clamp(p * 3))
        blit(ctx, s_.surf, x, yy, s_.pad + s_.adv / 2, s_.pad + s_.asc * 0.6, sc=sc, rot=rot, alpha=clamp(p * 3))


def flash(ctx, t, t0, dur=0.12, a=0.85):
    p = (t - t0) / dur
    if 0 <= p < 1:
        ctx.rectangle(0, 0, W, H)
        ctx.set_source_rgba(1, 1, 1, a * (1 - p))
        ctx.fill()


def punch(lt, t0, amt=0.06):
    """Quick zoom-out after a hit (starts zoomed in)."""
    return 1.0 + amt * (1 - ease_out(prog(lt, t0, 0.35)))


def grain(ctx, t):
    rng = fx.np.random.default_rng(int(t * 30))
    for _ in range(140):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        ctx.rectangle(x, y, 2, 2)
    ctx.set_source_rgba(1, 1, 1, 0.08)
    ctx.fill()


# ---------------------------------------------------------------- scenes
def scene_hook(ctx, t, lt):
    k = min(3, int(lt / 1.0))
    word, photo, t0 = HOOK[k]
    solid(ctx, WINE_D)
    full_photo(ctx, photo, punch(lt, t0, 0.10) + 0.04 * (lt - t0))
    vgrad(ctx, 0, H, WINE_D, 0.25, 0.55)
    ctx.rectangle(0, 0, W, H)
    ctx.set_source_rgba(*rgba(ROSE, 0.12))
    ctx.fill()
    mega(ctx, word, 540, 1420, lt, t0 + 0.02, size=180)
    lab = prog(lt, t0 + 0.1, 0.2)
    if lab > 0:
        label(ctx, f"0{k + 1}", "kicker", 90, 200, alpha=0.8, anchor="l")
    flash(ctx, lt, t0)


def scene_yakin(ctx, t, lt):
    solid(ctx, WINE_D)
    full_photo(ctx, "photo_arm", 1.16 - 0.06 * clamp(lt / 2.0))
    vgrad(ctx, 1000, H, WINE_D, 0.0, 0.9)
    vgrad(ctx, 0, 400, WINE_D, 0.6, 0.0)
    p = fx.layout([[fx.Tok("Tapi", "medw"), fx.Tok("tetap", "medw"), fx.Tok("kena", "medw")]], 540, 1300)
    fx.draw_words(ctx, lt, p, 0.15, 0.1)
    mega(ctx, "YAKIN.", 540, 1520, lt, 0.6, size=210, col=YELLOW)
    flash(ctx, lt, 0.0, a=0.5)


def scene_slam(ctx, t, lt):
    solid(ctx, WINE_D)
    full_photo(ctx, "photo_real", punch(lt, 0.0, 0.12) + 0.03 * lt)
    vgrad(ctx, 0, 520, WHITE, 0.95, 0.0)
    vgrad(ctx, 1450, H, WINE_D, 0.0, 0.85)
    logo(ctx, lt, 0.1, 540, 190, 380)
    lp = prog(lt, 0.4, 0.3)
    if lp > 0:
        label(ctx, "CELESTE MUSK DEODORANT ROLL-ON", "endname", 540, 330, alpha=clamp(lp * 3))
    mega(ctx, "KEKAL\nYAKIN.", 540, 1650, lt, 0.5, size=150, col=WHITE)
    flash(ctx, lt, 0.0, dur=0.18, a=1.0)


def scene_usp(ctx, t, lt):
    k = min(3, int(lt / 2.0))
    txt, photo, col, t0 = USPS[k]
    split = 1150
    solid(ctx, col)
    # top: photo (or bottle cut-out on pink)
    ctx.save()
    sl = ease_out(prog(lt, t0, 0.35))
    ctx.rectangle(0, 0, W, split)
    ctx.clip()
    ctx.translate((1 - sl) * W, 0)
    if photo:
        ps = fx.photo_surface(photo, W, split)
        z = 1.06 + 0.04 * (lt - t0)
        blit(ctx, ps, W / 2, split / 2, ps.get_width() / 2, ps.get_height() / 2, sc=z / 1.14)
    else:
        solid(ctx, PINK)
        sunburst(ctx, 540, 600, t, WHITE, 0.4)
        fx.bottle_drop(ctx, lt, t0 + 0.05, 540, 600, 820, float_amp=6)
    ctx.restore()
    ctx.rectangle(0, split - 8, W, 16)
    ctx.set_source_rgba(1, 1, 1, 1)
    ctx.fill()
    tc = WINE if col == YELLOW else WHITE
    sh = WINE_D if col != YELLOW else ROSE
    mega(ctx, txt, 540, split + 370, lt, t0 + 0.25, size=150, col=tc, shadow=sh, rot=-0.02)
    label(ctx, f"{k + 1}/4", "kicker", 980, 80, alpha=0.85)
    if k < 3:
        src = ["label: Odour & Wetness Protection", "label: Quick dry", "label: Non sticky"][k]
        pp = prog(lt, t0 + 0.7, 0.3)
        if pp > 0:
            fx.STY["srcl"] = ("sb", 30, tc)
            label(ctx, src, "srcl", 540, H - 150, alpha=0.75 * clamp(pp * 3))


def scene_quotes(ctx, t, lt):
    solid(ctx, BLUSH)
    # blurred-feel product background: real bottle photo heavily washed out
    full_photo(ctx, "photo_real", 1.25 + 0.02 * lt)
    ctx.rectangle(0, 0, W, H)
    ctx.set_source_rgba(*rgba(BLUSH, 0.82))
    ctx.fill()
    fx.chip(ctx, lt, 0.05, "KATA PELANGGAN SEBENAR", 540, 240, fill=WINE, color=WHITE, size=32)
    for i, (q, who, t0) in enumerate(QUOTES):
        p = prog(lt, t0 + 0.1, 0.35)
        if p <= 0:
            continue
        blk = testi.rich_block("“" + q + "”", "sb", 58, WINE, 800, q, lead=1.3)
        y = 470 + i * 400
        x = 540 + (1 - ease_out(p)) * (600 if i % 2 == 0 else -600)
        rot = (-0.03, 0.025, -0.02)[i]
        w, h = 900, blk.h + 120
        ctx.save()
        ctx.translate(x, y + h / 2)
        ctx.rotate(rot)
        sh, pad = fx.shadow_surface(w, int(h), 30, 18, 70)
        blit(ctx, sh, 0, 14, pad + w / 2, pad + h / 2)
        rrect(ctx, -w / 2, -h / 2, w, h, 30)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
        testi.draw_block(ctx, blk, -blk.w / 2, -h / 2 + 30, lt, t_hl=t0 + 0.9)
        wsp = fx.text_sprite("- " + who, "hand", 44, ROSE)
        blit(ctx, wsp.surf, w / 2 - 40, h / 2 - 40, wsp.pad + wsp.adv, wsp.pad + wsp.asc * 0.6)
        ctx.restore()
    dp = prog(lt, 6.2, 0.4)
    if dp > 0:
        fx.STY["discw"] = ("med", 28, WINE)
        label(ctx, "Pengalaman individu mungkin berbeza.", "discw", 540, 1800, alpha=0.8 * clamp(dp * 3))


def scene_finale(ctx, t, lt):
    solid(ctx, WINE)
    sunburst(ctx, 540, 960, t, WINE_D, 0.5)
    tiles = [("photo_ugc", 290, 520, -0.07), ("photo_arm", 800, 470, 0.06), ("photo_climb", 270, 1420, 0.05),
             ("photo_hook", 810, 1460, -0.06)]
    for i, (ph, x, y, r) in enumerate(tiles):
        p = ease_back(prog(lt, 0.1 + i * 0.25, 0.45), 1.3)
        if p <= 0:
            continue
        sx = [-1, 1, -1, 1][i] * (1 - p) * 700
        photo_card(ctx, ph, x + sx, y, 420, 540, rot=r * (2 - p), inner_zoom=1.05, border=14, r=24)
    # centre plate
    cp = ease_back(prog(lt, 1.3, 0.45), 1.8)
    if cp > 0:
        ctx.save()
        ctx.translate(540, 980)
        fx.sscale(ctx, cp, cp)
        sh, pad = fx.shadow_surface(980, 330, 50, 26, 100)
        blit(ctx, sh, 0, 20, pad + 490, pad + 165)
        rrect(ctx, -490, -165, 980, 330, 50)
        ctx.set_source_rgba(*rgba(BLUSH))
        ctx.fill()
        ctx.restore()
        logo(ctx, lt, 1.45, 540, 940, 400)
        sp = prog(lt, 2.0, 0.4)
        if sp > 0:
            label(ctx, "Hidup aktif, keyakinan bermula di sini!", "slogan", 540, 1080, alpha=clamp(sp * 3), sc=0.88)
    tp = prog(lt, 3.0, 0.4)
    if tp > 0:
        fx.STY["tagw"] = ("serif", 52, PINK)
        label(ctx, "confidence in every touch", "tagw", 540, 1840, alpha=clamp(tp * 3))
    flash(ctx, lt, 1.3, dur=0.15, a=0.6)


SCENES = dict(hook=scene_hook, yakin=scene_yakin, slam=scene_slam, usp=scene_usp, quotes=scene_quotes,
              finale=scene_finale)
fx.STY.setdefault("endname", ("sb", 32, WINE))


def compose(ctx, t):
    cur = max((n for n in ORDER if S[n] <= t), key=lambda n: S[n])
    SCENES[cur](ctx, t, t - S[cur])
    if cur in ("hook", "yakin", "slam", "usp"):
        grain(ctx, t)
