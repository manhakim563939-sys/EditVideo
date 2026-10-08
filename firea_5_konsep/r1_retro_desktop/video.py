"""R1 — "Retro Desktop / Y2K Pop-up" (30s, 9:16).

A playful old-computer desktop: the day "boots", warning pop-ups stack up (heat, long sleeves, sweat,
late shower, low confidence) -> search -> "installing Firea Celeste Musk" with the label claims ticking
off -> every warning closes -> final brand window. Product claims = approved USPs / label only.
"""
import math

import fx
import testi
from fx import (BLUSH, GREEN, PINK, ROSE, WHITE, WINE, WINE_D, YELLOW, blit, clamp, draw_check, ease_back, ease_in,
                ease_io, ease_out, label, logo, prog, rgba, rrect, solid, sparkle, W, H)

DUR = 30.0
DESK = (250, 214, 226)
ERRS = [  # (text, x, y, t_open, t_close)
    ("Cuaca panas terik dikesan.", 60, 330, 3.0, 20.0),
    ("Lengan panjang + tudung: aliran udara rendah.", 130, 540, 4.6, 20.4),
    ("Peluh dikesan di bawah lengan.", 90, 750, 6.2, 20.8),
    ("Lewat mandi: 9:00 malam.", 170, 960, 7.8, 21.2),
    ("Tahap keyakinan: rendah.", 110, 1170, 9.4, 21.6),
]
FEATS = ["Tahan peluh & bau", "Cepat kering", "Tak melekit", "0% Alkohol", "0% Paraben"]
T = dict(search=11.4, type0=11.9, enter=13.7, install=14.0, feats=15.0, done=19.3, status=22.1, final=24.2)

fx.STY.update({"px": ("pixel", 46, WHITE), "pxw": ("pixel", 40, WINE), "pxbig": ("pixel", 120, WHITE),
               "pxmid": ("pixel", 64, WINE), "errt": ("sb", 42, WINE), "feat": ("sb", 44, WINE)})

MUSIC = dict(bpm=110, chords=[(45, [57, 60, 64, 69]), (41, [53, 57, 60, 65]), (43, [55, 59, 62, 67]),
                              (40, [52, 55, 59, 64])],
             sections=[(0, 0), (3.0, 1), (6.2, 2), (T["search"], 0), (T["install"], 3), (T["final"], 3)],
             lp_windows=[(9.4, T["install"], 1500)], pluck_oct=24, pluck_gain=0.08, end_bell=(81, 88), peak_db=-2.6)


def cues():
    c = [(0.1, "click", 0.4), (0.4, "tock", 0.3), (2.5, "bell_ding", 0.4)]
    for i in range(10):
        c.append((0.3 + i * 0.2, "tick", 0.15))
    for _, _, _, to, tc in ERRS:
        c += [(to, "buzzer", 0.32), (to + 0.02, "pop", 0.4), (tc, "pop", 0.45)]
    c += [(10.7, "impact_soft", 0.45), (T["search"] - 0.3, "click", 0.4), (T["search"], "pop", 0.35)]
    for k in range(int((T["enter"] - T["type0"]) / 0.07)):
        c.append((T["type0"] + k * 0.07, "key", 0.12))
    c += [(T["enter"], "click", 0.5), (T["install"], "whoosh", 0.45)]
    for i in range(5):
        c.append((T["feats"] + i * 0.8, "pop", 0.45))
    c += [(T["done"], "bell_ding", 0.5), (T["status"], "stamp_soft", 0.55), (T["final"] - 0.2, "whoosh", 0.5),
          (T["final"] + 0.3, "sparkle", 0.5), (T["final"] + 1.6, "sparkle", 0.35)]
    return c


# ---------------------------------------------------------------- retro widgets
def desktop(ctx, t, lt):
    solid(ctx, DESK)
    ctx.set_source_rgba(1, 1, 1, 0.35)
    for x in range(0, W, 60):
        ctx.rectangle(x, 0, 2, H)
    for y in range(0, H, 60):
        ctx.rectangle(0, y, W, 2)
    ctx.fill()
    # pixel clouds
    for i, (cx, cy) in enumerate(((180, 180), (760, 120), (900, 1500))):
        x = (cx + t * 12 * (1 + i * 0.3)) % (W + 300) - 150
        for dx, dy, w_, h_ in ((0, 0, 160, 40), (30, -30, 100, 30), (-20, 20, 200, 30)):
            ctx.rectangle(x + dx, cy + dy, w_, h_)
        ctx.set_source_rgba(1, 1, 1, 0.8)
        ctx.fill()
    # taskbar
    ctx.rectangle(0, H - 100, W, 100)
    ctx.set_source_rgba(*rgba(WINE))
    ctx.fill()
    rrect(ctx, 20, H - 82, 180, 64, 6)
    ctx.set_source_rgba(*rgba(ROSE))
    ctx.fill()
    label(ctx, "MULA", "px", 110, H - 50)
    hh = 7 + int(clamp(lt / 24.0) * 14)
    label(ctx, f"{hh % 12 or 12}:00 {'PG' if hh < 12 else 'PTG' if hh < 19 else 'MLM'}", "px", 960, H - 50)


def window(ctx, x, y, w, h, title, p, title_col=ROSE, shake=0.0):
    """Hard-shadow retro window; returns body origin. p = open progress (scale pop)."""
    if p <= 0:
        return None
    sc = 0.2 + 0.8 * ease_back(p, 2.0)
    ctx.save()
    ctx.translate(x + w / 2 + shake, y + h / 2)
    fx.sscale(ctx, sc, sc)
    ctx.translate(-w / 2, -h / 2)
    ctx.rectangle(12, 12, w, h)
    ctx.set_source_rgba(*rgba(WINE_D, 0.9))
    ctx.fill()
    ctx.rectangle(0, 0, w, h)
    ctx.set_source_rgba(1, 1, 1, 1)
    ctx.fill_preserve()
    ctx.set_line_width(5)
    ctx.set_source_rgba(*rgba(WINE))
    ctx.stroke()
    ctx.rectangle(0, 0, w, 64)
    ctx.set_source_rgba(*rgba(title_col))
    ctx.fill()
    label(ctx, title, "px", 22, 34, anchor="l")
    for i, ch in enumerate(("_", "o", "x")):
        bx = w - 52 - (2 - i) * 54
        ctx.rectangle(bx, 12, 42, 40)
        ctx.set_source_rgba(1, 1, 1, 1)
        ctx.fill_preserve()
        ctx.set_line_width(3)
        ctx.set_source_rgba(*rgba(WINE))
        ctx.stroke()
        label(ctx, ch, "pxw", bx + 21, 30)
    return ctx  # caller draws body in local coords, then must ctx.restore()


def warn_icon(ctx, x, y, s=1.0):
    ctx.move_to(x, y - 40 * s)
    ctx.line_to(x + 46 * s, y + 38 * s)
    ctx.line_to(x - 46 * s, y + 38 * s)
    ctx.close_path()
    ctx.set_source_rgba(*rgba(YELLOW))
    ctx.fill_preserve()
    ctx.set_line_width(5)
    ctx.set_source_rgba(*rgba(WINE))
    ctx.stroke()
    label(ctx, "!", "pxmid", x, y + 6)


def cursor(ctx, x, y, click=0.0):
    ctx.save()
    ctx.translate(x, y)
    fx.sscale(ctx, 1.6 - 0.2 * click, 1.6 - 0.2 * click)
    ctx.move_to(0, 0)
    ctx.line_to(0, 34)
    ctx.line_to(9, 26)
    ctx.line_to(16, 40)
    ctx.line_to(22, 37)
    ctx.line_to(15, 23)
    ctx.line_to(26, 23)
    ctx.close_path()
    ctx.set_source_rgba(1, 1, 1, 1)
    ctx.fill_preserve()
    ctx.set_line_width(2.5)
    ctx.set_source_rgba(0, 0, 0, 1)
    ctx.stroke()
    ctx.restore()


CUR_KEYS = [(0.0, 900, 1700), (10.6, 860, 1500), (T["search"] - 0.3, 700, 340), (T["enter"], 900, 360),
            (T["done"] + 0.3, 600, 1500), (T["status"], 820, 1650), (DUR, 820, 1650)]


def cursor_pos(t):
    for (t0, x0, y0), (t1, x1, y1) in zip(CUR_KEYS, CUR_KEYS[1:]):
        if t0 <= t < t1:
            e = ease_io(clamp((t - t0) / min(0.6, t1 - t0)))
            return x0 + (x1 - x0) * e, y0 + (y1 - y0) * e
    return CUR_KEYS[-1][1:]


# ---------------------------------------------------------------- scenes
def boot(ctx, t, lt):
    solid(ctx, WINE_D)
    label(ctx, "FIREA OS", "pxbig", 540, 760, alpha=prog(lt, 0.1, 0.3))
    label(ctx, "Memuatkan: HARI YANG PANJANG...", "px", 540, 900, alpha=prog(lt, 0.3, 0.3))
    p = clamp((lt - 0.3) / 2.0)
    ctx.rectangle(190, 980, 700, 56)
    ctx.set_line_width(5)
    ctx.set_source_rgba(1, 1, 1, 1)
    ctx.stroke()
    for i in range(int(p * 14)):
        ctx.rectangle(200 + i * 49, 990, 42, 36)
    ctx.set_source_rgba(*rgba(ROSE))
    ctx.fill()
    if lt > 2.5:
        label(ctx, "Siap. Selamat bertugas!", "px", 540, 1110, alpha=prog(lt, 2.5, 0.2))


def compose(ctx, t):
    if t < 2.85:
        boot(ctx, t, t)
        return
    lt = t
    desktop(ctx, t, lt)
    if t < 3.0:  # flash into desktop
        ctx.rectangle(0, 0, W, H)
        ctx.set_source_rgba(1, 1, 1, 1 - prog(t, 2.85, 0.15))
        ctx.fill()
    shake = math.sin(t * 70) * 8 * (1 - prog(t, 10.7, 0.5)) if 10.7 <= t < 11.2 else 0
    # error windows
    for i, (txt, x, y, to, tc) in enumerate(ERRS):
        p = prog(t, to, 0.3) * (1 - prog(t, tc, 0.2))
        if p <= 0 or t > tc + 0.2:
            continue
        w, h = 860, 300
        if window(ctx, x, y, w, h, "amaran.exe", p, shake=shake):
            warn_icon(ctx, 90, 160)
            blk = testi.rich_block(txt, "sb", 42, WINE, 620)
            testi.draw_block(ctx, blk, 170, 100, t)
            ctx.rectangle(w - 190, h - 76, 150, 52)
            ctx.set_source_rgba(*rgba(PINK))
            ctx.fill()
            label(ctx, "OK", "pxw", w - 115, h - 50)
            ctx.restore()
    # search window
    sp = prog(t, T["search"], 0.3) * (1 - prog(t, T["install"] + 0.3, 0.2))
    if sp > 0 and t < T["install"] + 0.5:
        if window(ctx, 90, 260, 900, 200, "cari", sp):
            ctx.rectangle(30, 96, 840, 72)
            ctx.set_source_rgba(*rgba((245, 240, 242)))
            ctx.fill()
            fx.STY["srch"] = ("sb", 40, WINE)
            fx.typewriter(ctx, t, T["type0"], "deodorant untuk wanita aktif", "srch", 50, 132, cps=16)
            ctx.restore()
    # installer
    ip = prog(t, T["install"], 0.35)
    if ip > 0 and t < T["final"]:
        x, y, w, h = 70, 470, 940, 1000
        out = 1 - prog(t, T["final"] - 0.3, 0.3)
        if window(ctx, x, y, w, h, "pasang_firea.exe", ip * out + 1e-3):
            title = "Pemasangan selesai!" if t >= T["done"] else "Memasang Firea Celeste Musk..."
            fx.STY["inst"] = ("sb", 44, WINE)
            label(ctx, title, "inst", 40, 120, anchor="l")
            prg = clamp((t - T["install"] - 0.4) / (T["done"] - T["install"] - 0.4))
            ctx.rectangle(40, 170, w - 80, 50)
            ctx.set_line_width(4)
            ctx.set_source_rgba(*rgba(WINE))
            ctx.stroke()
            for k in range(int(prg * 20)):
                ctx.rectangle(48 + k * 42.5, 178, 36, 34)
            ctx.set_source_rgba(*rgba(GREEN if prg >= 1 else ROSE))
            ctx.fill()
            for k, f_ in enumerate(FEATS):
                fp = prog(t, T["feats"] + k * 0.8, 0.3)
                yy = 320 + k * 120
                ctx.rectangle(40, yy - 30, 60, 60)
                ctx.set_line_width(4)
                ctx.set_source_rgba(*rgba(WINE))
                ctx.stroke()
                if fp > 0:
                    draw_check(ctx, 70, yy, 26 * ease_back(fp, 2.5), GREEN, WHITE)
                label(ctx, f_, "feat", 130, yy, anchor="l", alpha=0.35 + 0.65 * clamp(fp * 3))
            # product photo panel
            ps = fx.photo_surface("photo_real", 300, 520)
            ctx.save()
            ctx.rectangle(600, 280, 300, 520)
            ctx.clip()
            blit(ctx, ps, 750, 540, ps.get_width() / 2, ps.get_height() / 2, sc=1.25 / 1.14)
            ctx.restore()
            ctx.rectangle(600, 280, 300, 520)
            ctx.set_line_width(5)
            ctx.set_source_rgba(*rgba(WINE))
            ctx.stroke()
            if t >= T["status"]:
                spp = ease_back(prog(t, T["status"], 0.35), 2)
                ctx.save()
                ctx.translate(w / 2, 900)
                fx.sscale(ctx, spp, spp)
                rrect(ctx, -330, -50, 660, 100, 16)
                ctx.set_source_rgba(*rgba(GREEN))
                ctx.fill()
                fx.STY["stat"] = ("pixel", 64, WHITE)
                label(ctx, "STATUS: YAKIN  :)", "stat", 0, 0)
                ctx.restore()
            ctx.restore()
    # final window
    fp = prog(t, T["final"], 0.4)
    if fp > 0:
        if window(ctx, 70, 560, 940, 760, "firea.exe", fp, title_col=WINE):
            ctx.rectangle(0, 64, 940, 696)
            ctx.set_source_rgba(*rgba(BLUSH))
            ctx.fill()
            logo(ctx, t, T["final"] + 0.3, 470, 300, 440)
            pp = prog(t, T["final"] + 0.9, 0.4)
            if pp > 0:
                label(ctx, "CELESTE MUSK DEODORANT ROLL-ON", "endname", 470, 450, alpha=clamp(pp * 3))
            sp2 = prog(t, T["final"] + 1.5, 0.4)
            if sp2 > 0:
                label(ctx, "Hidup aktif, keyakinan bermula di sini!", "slogan", 470, 560, alpha=clamp(sp2 * 3),
                      sc=0.88)
            sp3 = prog(t, T["final"] + 2.2, 0.4)
            if sp3 > 0:
                fx.STY["tagr"] = ("serif", 44, WINE)
                label(ctx, "confidence in every touch", "tagr", 470, 660, alpha=clamp(sp3 * 3))
            ctx.restore()
        for i, (dx, dy) in enumerate(((120, 520), (960, 600), (150, 1380), (930, 1360))):
            s_ = prog(t, T["final"] + 0.4 + i * 0.15, 0.5)
            sparkle(ctx, dx, dy, 26 * ease_back(s_, 2) * (0.8 + 0.2 * math.sin(t * 5 + i)), clamp(s_ * 3),
                    YELLOW if i % 2 else WHITE)
    cx, cy = cursor_pos(t)
    clk = max(1 - abs(t - T["enter"]) * 6, 1 - abs(t - (T["search"] - 0.3)) * 6, 0)
    cursor(ctx, cx, cy, clk)
