"""R3 — "Luxe Macro" (30s, 9:16). Dark, elegant product film on the REAL bottle (13.jpg).

A slow "macro camera" glides across the actual label: logo -> claims -> 0% badges -> icon column,
each with a gold kicker + serif caption translating exactly what the label says. Then pull-out,
one real customer line, and the brand close. Gold dust, light sweeps, vignette.
"""
import math
from functools import lru_cache

import cairo
from PIL import Image

import fx
from fx import (BLUSH, PINK, ROSE, WHITE, WINE, WINE_D, YELLOW, blit, clamp, ease_back, ease_in, ease_io, ease_out,
                label, logo, pil_to_surface, prog, rgba, sparkle, W, H)

DUR = 30.0
GOLD = (214, 178, 104)
INK = (24, 6, 14)
S = dict(intro=0.0, macro=3.5, quote=20.5, final=25.5)
ORDER = list(S)
# (time, source x, source y, zoom) on 13.jpg (1125x2000)
KEYS = [(3.5, 510, 1000, 1.7), (7.2, 470, 1150, 2.5), (11.0, 470, 1262, 2.7), (14.6, 612, 1170, 2.5),
        (18.2, 560, 1050, 0.98)]
CAPS = [  # (start, end, kicker, line1, line2)
    (3.9, 7.0, "CELESTE MUSK", "Deodorant roll-on", "antiperspirant"),
    (7.6, 10.8, "01  ·  PERLINDUNGAN", "Bau & basah, terlindung.", "Cepat kering · tak melekit"),
    (11.4, 14.4, "02  ·  FORMULA", "0% alkohol.", "0% paraben."),
    (15.0, 18.0, "03  ·  SETIAP HARI", "Kesegaran tahan lama.", "Formula lembut · sesuai harian"),
    (18.7, 20.4, "", "Hidup aktif,", "keyakinan bermula di sini."),
]

fx.STY.update({"kick": ("xb", 30, GOLD), "lux1": ("serif", 78, WHITE), "lux2": ("med", 40, (235, 220, 225)),
               "luxq": ("serif", 96, WHITE), "luxw": ("serif", 44, GOLD), "luxs": ("med", 26, (200, 180, 188)),
               "luxt": ("serif", 120, WHITE)})

MUSIC = dict(bpm=72, chords=[(38, [50, 54, 57, 61]), (43, [55, 59, 62, 66]), (35, [47, 50, 54, 59]),
                             (40, [52, 55, 59, 62])],
             sections=[(0, 0), (S["macro"], 1), (S["macro"] + 7.5, 2), (S["quote"], 1), (S["final"], 1)],
             pad_gain=0.09, pluck_gain=0.07, pluck_oct=24, lp_windows=[(0, S["macro"], 1800)], end_bell=(74, 81),
             peak_db=-3.0)


def cues():
    c = [(0.2, "impact_soft", 0.4), (0.8, "air", 0.4), (1.6, "sparkle", 0.4)]
    for t0, _, _, _ in KEYS[1:]:
        c.append((t0 - 0.2, "air", 0.35))
    for st, _, _, _, _ in CAPS:
        c.append((st + 0.1, "bell_ding", 0.18))
    c += [(S["quote"] - 0.3, "swish", 0.4), (S["quote"] + 0.4, "sparkle", 0.35), (S["final"] - 0.3, "swish", 0.4),
          (S["final"] + 0.4, "sparkle", 0.45), (S["final"] + 1.6, "sparkle", 0.35)]
    return c


@lru_cache(None)
def src():
    return pil_to_surface(Image.open(f"{fx.CUT}/photo_real.jpg").convert("RGBA"))


def cam(t):
    """Hold on key i during [t_i, t_{i+1}), arriving from key i-1 over the first 1.1 s, with a slow push."""
    idx = max(i for i, k in enumerate(KEYS) if k[0] <= t) if t >= KEYS[0][0] else 0
    t0, x1, y1, z1 = KEYS[idx]
    _, x0, y0, z0 = KEYS[max(0, idx - 1)]
    e = ease_io(clamp((t - t0) / 1.1))
    t_end = KEYS[idx + 1][0] if idx + 1 < len(KEYS) else DUR
    drift = 1 + 0.03 * clamp((t - t0) / (t_end - t0))
    return x0 + (x1 - x0) * e, y0 + (y1 - y0) * e, (z0 + (z1 - z0) * e) * drift


def vignette(ctx, a=0.9):
    g = cairo.RadialGradient(W / 2, H / 2, 300, W / 2, H / 2, 1150)
    g.add_color_stop_rgba(0, *rgba(INK, 0))
    g.add_color_stop_rgba(1, *rgba(INK, a))
    ctx.set_source(g)
    ctx.rectangle(0, 0, W, H)
    ctx.fill()


def dust(ctx, t, n=40, a=0.6):
    rng = fx.np.random.default_rng(4)
    for i in range(n):
        x = (rng.uniform(0, W) + math.sin(t * 0.3 + i) * 40) % W
        y = (rng.uniform(0, H) - t * rng.uniform(15, 40)) % H
        r = rng.uniform(1.5, 4)
        ctx.arc(x, y, r, 0, 2 * math.pi)
        ctx.set_source_rgba(*rgba(GOLD, a * (0.4 + 0.6 * math.sin(t * 2 + i) ** 2)))
        ctx.fill()


def sweep(ctx, t, t0, dur=1.4, a=0.22):
    """Diagonal light band across the frame."""
    p = (t - t0) / dur
    if not 0 <= p <= 1:
        return
    x = -600 + (W + 1200) * ease_io(p)
    g = cairo.LinearGradient(x - 220, 0, x + 220, 300)
    g.add_color_stop_rgba(0, 1, 1, 1, 0)
    g.add_color_stop_rgba(0.5, 1, 1, 1, a)
    g.add_color_stop_rgba(1, 1, 1, 1, 0)
    ctx.set_source(g)
    ctx.rectangle(0, 0, W, H)
    ctx.fill()


def caption(ctx, t):
    for st, en, kick, l1, l2 in CAPS:
        if not st <= t < en + 0.4:
            continue
        a = clamp((t - st) / 0.5) * (1 - clamp((t - en) / 0.4))
        dy = (1 - ease_out(clamp((t - st) / 0.6))) * 20
        if kick:
            fx.STY["kick"] = ("xb", 30, GOLD)
            sp = fx.text_sprite(kick, "xb", 30, GOLD, 6)
            blit(ctx, sp.surf, 540, 1470 + dy, sp.pad + sp.adv / 2, sp.pad + sp.asc * 0.6, alpha=a)
            ctx.rectangle(490, 1510 + dy, 100, 2)
            ctx.set_source_rgba(*rgba(GOLD, a))
            ctx.fill()
        label(ctx, l1, "lux1", 540, 1600 + dy, alpha=a)
        label(ctx, l2, "lux2", 540, 1700 + dy, alpha=a * clamp((t - st - 0.3) / 0.5))


# ---------------------------------------------------------------- scenes
def scene_intro(ctx, t, lt):
    ctx.set_source_rgb(*rgba(INK)[:3])
    ctx.paint()
    fx.glow(ctx, 540, 860, 520, WINE, 0.9 * prog(lt, 0.0, 1.0))
    bs = fx.bottle_surface(900)
    a = ease_out(prog(lt, 0.2, 1.2))
    sc = 0.96 + 0.04 * a
    blit(ctx, bs, 540, 860, bs.get_width() / 2, bs.get_height() / 2, sc=sc, alpha=a)
    # glint masked to the bottle
    p = prog(lt, 0.9, 1.3)
    if 0 < p < 1:
        ctx.save()
        ctx.translate(540, 860)
        fx.sscale(ctx, sc, sc)
        ctx.translate(-bs.get_width() / 2, -bs.get_height() / 2)
        x = -200 + (bs.get_width() + 400) * ease_io(p)
        g = cairo.LinearGradient(x - 120, 0, x + 120, 160)
        g.add_color_stop_rgba(0, 1, 1, 1, 0)
        g.add_color_stop_rgba(0.5, 1, 1, 1, 0.55)
        g.add_color_stop_rgba(1, 1, 1, 1, 0)
        ctx.set_source(g)
        ctx.mask_surface(bs, 0, 0)
        ctx.restore()
    dust(ctx, t, a=0.5 * a)
    kp = prog(lt, 1.6, 0.6)
    if kp > 0:
        sp = fx.text_sprite("FIREA  ·  DEODORANT ROLL-ON", "xb", 30, GOLD, 6)
        blit(ctx, sp.surf, 540, 1470, sp.pad + sp.adv / 2, sp.pad + sp.asc * 0.6, alpha=kp)
    tp = prog(lt, 1.9, 0.8)
    if tp > 0:
        label(ctx, "Celeste Musk", "luxt", 540, 1610 + (1 - ease_out(tp)) * 24, alpha=tp)


def scene_macro(ctx, t, lt):
    ctx.set_source_rgb(*rgba(INK)[:3])
    ctx.paint()
    sx, sy, z = cam(t)
    blit(ctx, src(), W / 2, H / 2 - 160, sx, sy, sc=z)
    ctx.rectangle(0, 0, W, H)
    ctx.set_source_rgba(*rgba(WINE_D, 0.18))
    ctx.fill()
    vignette(ctx, 0.95)
    fx.vgrad(ctx, 1300, H, INK, 0.0, 0.92)
    for k in KEYS[1:]:
        sweep(ctx, t, k[0] + 0.6)
    dust(ctx, t, a=0.45)
    caption(ctx, t)


def scene_quote(ctx, t, lt):
    ctx.set_source_rgb(*rgba(INK)[:3])
    ctx.paint()
    fx.glow(ctx, 540, 900, 600, WINE, 0.8)
    dust(ctx, t, a=0.5)
    q = fx.text_sprite("“", "serif", 300, GOLD)
    blit(ctx, q.surf, 540, 700, q.pad + q.adv / 2, q.pad + q.asc * 0.5, alpha=prog(lt, 0.1, 0.5))
    p = fx.layout([[fx.Tok("Memang", "luxq"), fx.Tok("puas", "luxq")], [fx.Tok("hati", "luxq"), fx.Tok("sangat!", "luxq")]],
                  540, 800)
    fx.draw_words(ctx, lt, p, 0.4, 0.18, dur=0.7)
    ap = prog(lt, 1.6, 0.6)
    if ap > 0:
        label(ctx, "- Pelanggan A, kerja luar", "luxw", 540, 1120, alpha=ap)
    dp = prog(lt, 2.4, 0.6)
    if dp > 0:
        label(ctx, "Testimoni pelanggan sebenar. Pengalaman individu mungkin berbeza.", "luxs", 540, 1780,
              alpha=0.85 * dp)


def scene_final(ctx, t, lt):
    ctx.set_source_rgb(*rgba(INK)[:3])
    ctx.paint()
    fx.glow(ctx, 540, 1050, 560, WINE, 0.95)
    fx.glow(ctx, 540, 1050, 300, GOLD, 0.25 * prog(lt, 0.2, 1.0))
    bs = fx.bottle_surface(620)
    a = ease_out(prog(lt, 0.1, 0.8))
    blit(ctx, bs, 540, 1080 + (1 - a) * 60 + math.sin(t * 1.2) * 6, bs.get_width() / 2, bs.get_height() / 2,
         alpha=a)
    dust(ctx, t, a=0.55)
    logo(ctx, lt, 0.5, 540, 430, 420, color=WHITE)
    tp = prog(lt, 1.3, 0.7)
    if tp > 0:
        label(ctx, "confidence in every touch", "luxw", 540, 1560, alpha=tp)
    for i, (dx, dy) in enumerate(((-230, 820), (220, 900), (250, 1280), (-240, 1330))):
        s_ = prog(lt, 0.8 + i * 0.2, 0.6)
        sparkle(ctx, 540 + dx, dy, 22 * ease_back(s_, 2) * (0.7 + 0.3 * math.sin(t * 4 + i)), clamp(s_ * 3), GOLD)


SCENES = dict(intro=scene_intro, macro=scene_macro, quote=scene_quote, final=scene_final)


def compose(ctx, t):
    cur = max((n for n in ORDER if S[n] <= t), key=lambda n: S[n])
    i = ORDER.index(cur)
    SCENES[cur](ctx, t, t - S[cur])
    # slow cross-fade through black at every cut (luxury pacing)
    for n in ORDER[1:]:
        d = abs(t - S[n])
        if d < 0.35:
            ctx.rectangle(0, 0, W, H)
            ctx.set_source_rgba(*rgba(INK, 1 - d / 0.35))
            ctx.fill()
