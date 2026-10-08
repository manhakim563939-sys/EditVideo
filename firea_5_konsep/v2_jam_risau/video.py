"""V2 — "Jam Berapa Awak Mula Risau?" (30s, 9:16).

Problem: confidence drains through a long, active day (heat, outdoor work, late shower).
Flow: hook clock -> 6 time-steps 7am..9pm with a falling "TAHAP YAKIN" meter -> REWIND ->
      replay the day fast with Firea (meter stays high) -> product end card.
100 BPM: beat 0.6 s, bar 2.4 s.
"""
import math

import cairo

import fx
from fx import (BLUSH, BLUSH2, GREEN, PINK, RED, ROSE, WHITE, WINE, WINE_D, YELLOW, Tok, blit, bottle_drop, chip,
                clamp, draw_droplet, draw_sun, draw_words, ease_back, ease_in, ease_io, ease_out, glow, label, layout,
                layout_bottom, logo, panel_wipe, pill, prog, rgba, rrect, solid, sunburst, text_sprite, W, H)

DUR = 30.0
S = dict(hook=0.0, day=3.0, rewind=16.8, replay=19.2, end=24.0)
ORDER = list(S)
STEP = 2.3
STEPS = [  # (hour, label, situation, confidence level, icon)
    (7.0, "7:00 PAGI", "Keluar rumah. Segar & yakin.", 1.00, "sunrise"),
    (10.0, "10:00 PAGI", "Meeting / kelas. Mula rasa panas.", 0.82, "laptop"),
    (13.0, "1:00 TENGAH HARI", "Panas terik di luar.", 0.60, "sun"),
    (16.0, "4:00 PETANG", "Kerja luar, banyak bergerak.", 0.42, "drops"),
    (18.5, "6:30 PETANG", "Tersangkut dalam jem.", 0.26, "car"),
    (21.0, "9:00 MALAM", "Baru sampai. Belum sempat mandi.", 0.12, "moon"),
]

fx.STY.update({"time": ("brico", 92, WINE), "sit": ("sb", 54, WINE), "handw": ("hand", 64, WHITE),
               "handwine": ("hand", 60, WINE)})

MUSIC = dict(bpm=100, chords=[(45, [57, 60, 64, 67]), (41, [53, 57, 60, 64]), (43, [55, 59, 62, 67]),
                              (40, [52, 55, 59, 64])],
             sections=[(0, 0), (S["day"], 1), (S["day"] + 2 * STEP, 2), (S["rewind"], -1), (S["replay"], 3),
                       (S["end"], 3)],
             lp_windows=[(S["day"] + 3 * STEP, S["rewind"], 2200)], end_bell=(81, 84))


def cues():
    c = []
    for i in range(5):
        c.append((i * 0.6, "tick" if i % 2 == 0 else "tock", 0.45))
    c += [(0.2, "click", 0.3), (1.0, "swish", 0.45)]
    for i in range(6):
        t0 = S["day"] + i * STEP
        c += [(t0, "whoosh", 0.35), (t0 + 0.15, "click", 0.4), (t0 + 0.55, "tock" if i else "pop", 0.45)]
    c += [(S["rewind"] - 0.1, "rewind", 0.7), (S["rewind"] + 1.2, "pop", 0.45)]
    for i in range(6):
        c.append((S["replay"] + 0.5 + i * 0.6, "tick", 0.4))
    c += [(S["replay"] + 4.2, "bell_ding", 0.45), (S["end"] - 0.3, "whoosh", 0.55), (S["end"] + 0.5, "impact", 0.55)]
    for i in range(3):
        c.append((S["end"] + 1.6 + i * 0.35, "stamp_soft", 0.5))
    c += [(S["end"] + 3.0, "sparkle", 0.4)]
    return c


# ---------------------------------------------------------------- pieces
def draw_clock(ctx, x, y, r, hour, sec, alpha=1.0, face=WHITE, rim=WINE):
    ctx.save()
    ctx.translate(x, y)
    sh = cairo.RadialGradient(0, 18, r * 0.8, 0, 18, r * 1.15)
    sh.add_color_stop_rgba(0, 0.35, 0.05, 0.15, 0.25 * alpha)
    sh.add_color_stop_rgba(1, 0.35, 0.05, 0.15, 0)
    ctx.set_source(sh)
    ctx.arc(0, 18, r * 1.15, 0, 2 * math.pi)
    ctx.fill()
    ctx.arc(0, 0, r, 0, 2 * math.pi)
    ctx.set_source_rgba(*rgba(rim, alpha))
    ctx.fill()
    ctx.arc(0, 0, r * 0.88, 0, 2 * math.pi)
    ctx.set_source_rgba(*rgba(face, alpha))
    ctx.fill()
    for i in range(12):
        a = i * math.pi / 6
        l0 = r * (0.70 if i % 3 == 0 else 0.76)
        ctx.move_to(math.sin(a) * l0, -math.cos(a) * l0)
        ctx.line_to(math.sin(a) * r * 0.82, -math.cos(a) * r * 0.82)
        ctx.set_line_width(10 if i % 3 == 0 else 5)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_source_rgba(*rgba(WINE, alpha))
        ctx.stroke()
    ha = (hour % 12) / 12 * 2 * math.pi
    ma = (hour % 1) * 2 * math.pi
    for ang, ln, wd, col in ((ha, 0.45, 18, WINE), (ma, 0.68, 11, WINE), (sec, 0.74, 5, ROSE)):
        ctx.move_to(-math.sin(ang) * r * 0.1, math.cos(ang) * r * 0.1)
        ctx.line_to(math.sin(ang) * r * ln, -math.cos(ang) * r * ln)
        ctx.set_line_width(wd)
        ctx.set_source_rgba(*rgba(col, alpha))
        ctx.stroke()
    ctx.arc(0, 0, 14, 0, 2 * math.pi)
    ctx.set_source_rgba(*rgba(ROSE, alpha))
    ctx.fill()
    ctx.restore()


def meter_color(v):
    stops = [(0.0, RED), (0.35, ROSE), (0.65, YELLOW), (1.0, GREEN)]
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if v <= b:
            k = (v - a) / (b - a)
            return tuple(int(ca[i] + (cb[i] - ca[i]) * k) for i in range(3))
    return GREEN


def meter(ctx, x, y, w, h, v, alpha=1.0, title="TAHAP YAKIN", dark=False):
    tc = WHITE if dark else WINE
    sp = text_sprite(title, "xb", 34, tc, 3)
    blit(ctx, sp.surf, x, y - h / 2 - 40, sp.pad, sp.pad + sp.asc * 0.6, alpha=alpha)
    rrect(ctx, x, y - h / 2, w, h, 22)
    ctx.set_source_rgba(*rgba(WHITE, 0.9 * alpha))
    ctx.fill_preserve()
    ctx.set_source_rgba(*rgba(tc, alpha))
    ctx.set_line_width(6)
    ctx.stroke()
    rrect(ctx, x + w + 4, y - h / 4, 18, h / 2, 6)
    ctx.fill()
    if v > 0.01:
        rrect(ctx, x + 12, y - h / 2 + 12, (w - 24) * v, h - 24, 14)
        ctx.set_source_rgba(*rgba(meter_color(v), alpha))
        ctx.fill()
    pct = text_sprite(f"{int(round(v * 100))}%", "brico", 52, WINE, 0)
    blit(ctx, pct.surf, x + w - 30, y, pct.pad + pct.adv, pct.pad + pct.asc * 0.6, alpha=alpha)


def icon(ctx, kind, x, y, t, s=1.0):
    ctx.save()
    ctx.translate(x, y)
    fx.sscale(ctx, s, s)
    if kind in ("sun", "sunrise"):
        draw_sun(ctx, 0, 0 if kind == "sun" else 10, 30, t)
        if kind == "sunrise":
            ctx.rectangle(-70, 18, 140, 60)
            ctx.set_source_rgba(*rgba(BLUSH2))
            ctx.fill()
            ctx.move_to(-70, 18)
            ctx.line_to(70, 18)
            ctx.set_line_width(6)
            ctx.set_source_rgba(*rgba(WINE))
            ctx.stroke()
    elif kind == "moon":
        ctx.arc(0, 0, 40, 0, 2 * math.pi)
        ctx.set_source_rgba(*rgba(YELLOW))
        ctx.fill()
        ctx.arc(18, -12, 36, 0, 2 * math.pi)
        ctx.set_source_rgba(*rgba(BLUSH2))
        ctx.fill()
    elif kind == "laptop":
        rrect(ctx, -50, -40, 100, 66, 8)
        ctx.set_source_rgba(*rgba(WINE))
        ctx.fill()
        rrect(ctx, -64, 26, 128, 14, 5)
        ctx.fill()
    elif kind == "car":
        rrect(ctx, -60, -10, 120, 40, 12)
        ctx.set_source_rgba(*rgba(ROSE))
        ctx.fill()
        rrect(ctx, -36, -38, 72, 34, 12)
        ctx.fill()
        for wx in (-34, 34):
            ctx.arc(wx, 32, 13, 0, 2 * math.pi)
            ctx.set_source_rgba(*rgba(WINE))
            ctx.fill()
    elif kind == "drops":
        for i, dx in enumerate((-30, 10, 42)):
            draw_droplet(ctx, dx, 10 + math.sin(t * 4 + i) * 5, 18 - i * 3, lw=3)
    ctx.restore()


def hour_at(t):
    if t < S["day"]:
        return 7.0
    if t < S["rewind"]:
        i = min(5, int((t - S["day"]) / STEP))
        h0 = STEPS[i - 1][0] if i else 6.5
        return h0 + (STEPS[i][0] - h0) * ease_io(prog(t, S["day"] + i * STEP, 0.6))
    if t < S["replay"]:
        return 21.0 - 14.0 * ease_io(prog(t, S["rewind"], 1.4))
    if t < S["end"]:
        return 7.0 + 14.0 * ease_io(prog(t, S["replay"] + 0.4, 3.8))
    return 21.0


# ---------------------------------------------------------------- scenes
def scene_hook(ctx, t, lt):
    solid(ctx, BLUSH)
    glow(ctx, 540, 1180, 650, PINK, 0.9)
    p = layout([[Tok("Jam", "xb"), Tok("berapa", "xb"), Tok("awak", "xb")],
                [Tok("mula", "xb"), Tok("rasa", "xb")],
                [Tok("TAK YAKIN?", "bricow", hl=ROSE)]], 540, 230)
    draw_words(ctx, lt, p, 0.1, 0.12)
    cp = ease_back(prog(lt, 0.0, 0.5), 1.8)
    sec = math.floor(t / 0.6) * (2 * math.pi / 60) * 5
    draw_clock(ctx, 540, 1180, 330 * cp, hour_at(t), sec, alpha=clamp(cp * 2))


def scene_day(ctx, t, lt):
    i = min(5, int(lt / STEP))
    st = lt - i * STEP
    hr, tl, sit, lvl, ic = STEPS[i]
    dark = clamp((i - 2) / 3)
    base = tuple(int(BLUSH[k] + (PINK[k] - BLUSH[k]) * dark) for k in range(3))
    solid(ctx, base)
    glow(ctx, 540, 600, 520, WHITE, 0.6 - 0.3 * dark)
    sec = math.floor(t / 0.6) * (2 * math.pi / 60) * 5
    draw_clock(ctx, 540, 560, 270, hour_at(t), sec)
    # time label + icon + situation (re-enter each step)
    p = prog(st, 0.1, 0.35)
    if p > 0:
        sp = text_sprite(tl, "brico", 88, WINE)
        x0 = 540 - (sp.adv + 120) / 2
        icon(ctx, ic, x0 + 40, 990, t, 0.9 * ease_back(p, 2))
        blit(ctx, sp.surf, x0 + 120, 990 + (1 - ease_out(p)) * 20, sp.pad, sp.pad + sp.asc * 0.6, alpha=clamp(p * 3))
    q = layout([[Tok(sit, "sit")]], 540, 1070)
    draw_words(ctx, st, q, 0.3, 0.0)
    # meter eases from previous level
    prev = STEPS[i - 1][3] if i else 1.0
    v = prev + (lvl - prev) * ease_out(prog(st, 0.5, 0.6))
    meter(ctx, 140, 1360, 780, 110, v)
    if i >= 3:
        fx.bubble(ctx, st, 0.9, ["Bau tak aku?", "Basah tak baju?", "Tak sabar nak mandi..."][i - 3], 560, 1620,
                  style="handwine", size=58, tail=(1, -1))


def scene_rewind(ctx, t, lt):
    solid(ctx, WINE_D)
    # VHS-ish scanlines + jitter
    for k in range(0, H, 12):
        ctx.rectangle(0, k, W, 2)
    ctx.set_source_rgba(1, 1, 1, 0.04)
    ctx.fill()
    jit = math.sin(t * 90) * 6 if lt < 1.4 else 0
    sec = -lt * 40
    draw_clock(ctx, 540 + jit, 760, 300, hour_at(t), sec)
    # rewind icon
    ip = prog(lt, 0.1, 0.3)
    if ip > 0:
        ctx.save()
        ctx.translate(540, 1240)
        fx.sscale(ctx, ease_back(ip, 2), ease_back(ip, 2))
        for dx in (-40, 30):
            ctx.move_to(dx + 40, -40)
            ctx.line_to(dx - 30, 0)
            ctx.line_to(dx + 40, 40)
            ctx.close_path()
        ctx.set_source_rgba(*rgba(YELLOW))
        ctx.fill()
        ctx.restore()
    p = layout([[Tok("Jom", "handw"), Tok("ulang", "handw"), Tok("hari", "handw"), Tok("ni...", "handw")]], 540, 1360)
    draw_words(ctx, lt, p, 0.9, 0.1)
    pill(ctx, lt, 1.25, "dengan Firea", 540, 1560, ROSE, WHITE, size=52, rot=-0.04)


def scene_replay(ctx, t, lt):
    solid(ctx, BLUSH)
    glow(ctx, 540, 600, 560, YELLOW, 0.45)
    sec = (lt * 6) % (2 * math.pi)
    draw_clock(ctx, 540, 560, 270, hour_at(t), sec)
    k = min(5, int(clamp((lt - 0.4) / 3.8) * 6))
    hr, tl, sit, lvl, ic = STEPS[k]
    sp = text_sprite(tl, "brico", 88, WINE)
    x0 = 540 - (sp.adv + 120) / 2
    icon(ctx, ic, x0 + 40, 990, t, 0.9)
    blit(ctx, sp.surf, x0 + 120, 990, sp.pad, sp.pad + sp.asc * 0.6)
    v = 1.0 - 0.06 * clamp((lt - 0.4) / 3.8)
    meter(ctx, 140, 1360, 780, 110, v)
    bs = fx.bottle_surface(290)
    bp = ease_back(prog(lt, 0.2, 0.45), 2)
    blit(ctx, bs, 945, 620, bs.get_width() / 2, bs.get_height() / 2, sc=bp, rot=0.12 + math.sin(t * 2) * 0.03)
    pill(ctx, lt, 4.0, "Masih yakin!", 540, 1600, GREEN, WHITE, size=54, rot=-0.03, icon="check")


def scene_end(ctx, t, lt):
    solid(ctx, BLUSH)
    bp = ease_out(prog(lt, 0, 0.8))
    sunburst(ctx, 540, 960, t, PINK, 0.55 * bp)
    glow(ctx, 540, 960, 520, YELLOW, 0.4 * bp)
    p = layout([[Tok("Perlindungan", "bricos"), Tok("bau", "bricos"), Tok("&", "bricos"), Tok("peluh", "bricos")],
                [Tok("sepanjang hari.", "serifm", under=YELLOW)]], 540, 190)
    draw_words(ctx, lt, p, 0.15, 0.1)
    bottle_drop(ctx, lt, 0.45, 540, 960, 660)
    for i, (txt, x, y, r, fill, col) in enumerate((("Cepat kering", 250, 760, -0.08, YELLOW, WINE),
                                                     ("0% Alkohol", 840, 900, 0.07, ROSE, WHITE),
                                                     ("0% Paraben", 245, 1160, -0.06, WINE, WHITE))):
        pill(ctx, lt, 1.6 + i * 0.35, txt, x, y, fill, col, size=46, rot=r, icon="check")
    logo(ctx, lt, 2.8, 540, 1450, 320)
    pp = prog(lt, 3.0, 0.4)
    if pp > 0:
        label(ctx, "Hidup aktif, keyakinan bermula di sini!", "slogan", 540, 1580, alpha=clamp(pp * 3))


SCENES = dict(hook=scene_hook, day=scene_day, rewind=scene_rewind, replay=scene_replay, end=scene_end)


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
    cols = {"day": (WINE, ROSE), "rewind": (WINE_D, YELLOW), "replay": (YELLOW, ROSE), "end": (ROSE, YELLOW)}
    if nxt in cols:
        panel_wipe(ctx, t, S[nxt], *cols[nxt])
    if cur in cols:
        panel_wipe(ctx, t, S[cur], *cols[cur])
