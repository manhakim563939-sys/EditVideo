"""Episode 2 — "Konsisten Kalahkan Viral" (~35 s, 1080x1920@30), same Vox collage look as
kolaj_render.py, laid out directly on the ElevenLabs VO timeline (first 1 s of VO trimmed).

Usage: python3 konsisten_render.py <workdir> [t1 t2 ...]
  needs everything kolaj_render.py needs, plus <workdir>/expr/9.jpg + 9_mask.png (confused face).
"""
import math
import sys

import numpy as np
from PIL import Image, ImageDraw

import kolaj_render as kr
from kolaj_render import (INK, RED, TEAL, WHITE, YELLOW, BLUE, A, W, H, FPS, F_ANTON, F_MARK, F_TYPE, alive,
                          big, burst, card, circle_marker, clamp, doodle, draw_full, draw_head, ease_back,
                          ease_out, headline, kicker, label, place, pop, ref, scribble_arrow, slide, sparkle,
                          stamp, underline_marker, with_shadow)

WD = sys.argv[1]
DUR = 35.4
N = int(DUR * FPS)

kr.STK["keliru"] = kr.build_stickers(f"{WD}/expr/9.jpg", f"{WD}/expr/9_mask.png", seed=27)

# ---------------------------------------------------------------- timeline (VO time, 1 s lead trimmed)
CUTS = [4.0, 6.45, 11.35, 19.4, 25.0, 29.1]
PUNCHES = [1.85, 5.4, 8.95, 16.55, 23.45, 26.55, 31.38, 32.81]
FOCUS = [(0.0, (540, 800)), (4.0, (540, 800)), (6.45, (540, 800)), (11.35, (540, 700)), (19.4, (540, 800)),
         (25.0, (540, 800)), (29.1, (540, 900))]
kr.CUTS, kr.PUNCHES, kr.FOCUS, kr.DUR = CUTS, PUNCHES, FOCUS, DUR
kr.WIPE_COLS = [INK, YELLOW, RED, TEAL, BLUE, YELLOW]

# (start, end, text, when the VO finishes the line)
CAPS = [
    (0.55, 1.75, "Satu video VIRAL...", 1.53),
    (1.75, 2.72, "lepas tu SENYAP?", 2.70),
    (2.72, 4.0, "Ramai owner bisnes kejar viral.", 3.89),
    (4.05, 6.45, "Bila tak viral, terus PUTUS ASA.", 6.21),
    (6.5, 9.35, "Hakikatnya, viral tu macam LOTERI.", 9.12),
    (9.4, 11.35, "Konsisten tu macam MENABUNG.", 11.23),
    (11.42, 14.85, "Lagi kerap anda muncul, lagi ramai orang INGAT anda.", 14.68),
    (14.95, 16.5, "Setiap video yang anda post,", 16.4),
    (16.5, 19.4, "ialah satu PELUANG orang baru kenal bisnes anda.", 19.22),
    (19.5, 20.85, "Tak perlu SEMPURNA.", 20.65),
    (20.9, 25.0, "Satu video sehari, atau tiga seminggu, asalkan BERTERUSAN.", 24.85),
    (25.15, 26.55, "Tiga bulan dari sekarang,", 26.48),
    (26.55, 29.1, "anda akan BERTERIMA KASIH pada diri sendiri.", 28.91),
    (29.2, 31.25, "Jadi, jangan kejar VIRAL.", 31.06),
    (31.25, 32.7, "KEJAR KONSISTEN.", 32.54),
    (32.7, DUR, "Mula HARI INI.", 33.66),
]


def cap_words(s, vo_end, text):
    words = text.split()
    L = [len(w_) + 2 for w_ in words]
    acc, times = 0, []
    for l in L:
        times.append(s + (vo_end - s) * acc / sum(L))
        acc += l
    return words, times


kr.CAP_DATA = [(s, e, *cap_words(s, ve, txt)) for s, e, txt, ve in CAPS]

# ---------------------------------------------------------------- backgrounds
BG = {
    0.0: kr.paper(kr.CREAM, 21),
    4.0: kr.add_block(kr.paper(kr.CREAM, 22), (205, 205, 210), (60, 300, 1020, 1350), seed=31, rot=-3),
    6.45: kr.add_block(kr.paper(kr.CREAM, 23), (190, 225, 205), (560, 240, 1160, 1200), seed=32, rot=3),
    11.35: kr.halftone_bg((255, 222, 60), (230, 150, 0)),
    19.4: kr.add_block(kr.paper(kr.CREAM, 24), (150, 190, 235), (-60, 380, 700, 1250), seed=33, rot=-2),
    25.0: kr.add_block(kr.paper(kr.CREAM, 25), (255, 190, 180), (120, 200, 1150, 1150), seed=34, rot=2),
    29.1: kr.paper(kr.CREAM, 26),
}


# ---------------------------------------------------------------- B-roll pieces
def views_graph(prog, crash):
    """Views per video: one huge spike, then flat."""
    w, h = 820, 400
    img = card(w, h)
    d = ImageDraw.Draw(img)
    d.text((22, 14), "VIEWS / VIDEO", font=F_TYPE(32), fill=INK)
    base = h - 40
    pts = [(40, base - 20), (130, base - 25), (220, base - 300), (300, base - 30), (420, base - 18), (540, base - 14),
           (660, base - 12), (780, base - 10)]
    n = prog * (len(pts) - 1)
    seg = [pts[0]]
    for i in range(1, len(pts)):
        if i <= n:
            seg.append(pts[i])
        else:
            f = n - (i - 1)
            if f > 0:
                p0, p1 = pts[i - 1], pts[i]
                seg.append((p0[0] + (p1[0] - p0[0]) * f, p0[1] + (p1[1] - p0[1]) * f))
            break
    d.line([(20, base), (w - 20, base)], fill=INK, width=3)
    if len(seg) > 1:
        d.line(seg, fill=RED if crash else BLUE, width=10, joint="curve")
    return with_shadow(img)


def lottery_ticket():
    w, h = 420, 230
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], fill=(255, 236, 160, 255), outline=INK + (255,), width=4)
    for y in range(12, h, 24):  # perforated stub
        d.ellipse([92, y, 104, y + 12], fill=kr.CREAM + (255,))
    d.text((20, 70), "No.", font=F_TYPE(30), fill=INK)
    d.text((120, 22), "LOTERI", font=F_ANTON(80), fill=RED)
    d.text((124, 130), "07  21  34  ??", font=F_TYPE(40), fill=INK)
    return with_shadow(img)


def piggy_jar(coins):
    """Glass jar that fills with coins (coins = 0..1)."""
    w, h = 380, 440
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 40, 80, w - 40, h - 20
    lvl = y1 - 10 - (y1 - y0 - 30) * coins
    for k in range(int(coins * 22)):
        row, col = divmod(k, 4)
        cx = x0 + 40 + col * 70 + (row % 2) * 30
        cy = y1 - 30 - row * 32
        if cy > lvl - 20:
            d.ellipse([cx - 28, cy - 14, cx + 28, cy + 14], fill=(240, 190, 40, 255), outline=INK + (255,), width=3)
    d.rounded_rectangle([x0, y0, x1, y1], radius=40, outline=INK + (255,), width=6)
    d.rectangle([x0 + 30, y0 - 40, x1 - 30, y0 + 4], fill=(200, 200, 200, 255), outline=INK + (255,), width=5)
    d.rectangle([w / 2 - 50, y0 - 26, w / 2 + 50, y0 - 14], fill=INK + (255,))
    return with_shadow(img)


def falling_coin(c, t, t0, cx, top, bottom):
    if not (t0 <= t <= t0 + 0.35):
        return
    u = (t - t0) / 0.35
    y = top + (bottom - top) * u * u
    ImageDraw.Draw(c).ellipse([cx - 26, y - 13, cx + 26, y + 13], fill=(240, 190, 40, 255), outline=INK + (255,), width=3)


def calendar(n_done, title="OKTOBER"):
    w, h = 760, 620
    img = card(w, h)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, 90], fill=RED, outline=INK, width=4)
    f = F_ANTON(64)
    d.text(((w - f.getlength(title)) / 2, 6), title, font=f, fill=WHITE)
    cw, ch = (w - 40) / 7, (h - 120) / 4
    fn = F_TYPE(28)
    for k in range(28):
        r, col = divmod(k, 7)
        x, y = 20 + col * cw, 105 + r * ch
        d.rectangle([x, y, x + cw - 6, y + ch - 6], outline=(190, 190, 190), width=2)
        d.text((x + 8, y + 4), str(k + 1), font=fn, fill=INK)
        if k < n_done:
            cx, cy = x + cw / 2, y + ch / 2 + 8
            d.line([(cx - 22, cy), (cx - 6, cy + 18), (cx + 26, cy - 22)], fill=TEAL, width=10, joint="curve")
    return with_shadow(img)


def person_icon(col, size=100):
    img = Image.new("RGBA", (size, int(size * 1.35)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = size * 0.24
    d.ellipse([size / 2 - r, 4, size / 2 + r, 4 + 2 * r], fill=col + (255,), outline=INK + (255,), width=5)
    d.rounded_rectangle([size * 0.1, 2 * r + 14, size * 0.9, img.height - 4], radius=int(size * 0.3),
                        fill=col + (255,), outline=INK + (255,), width=5)
    return img


ICON_COLS = [YELLOW, RED, BLUE, TEAL, WHITE, (220, 140, 220)]
ICONS = [person_icon(c) for c in ICON_COLS]


def chip(text, fg=INK, bg=WHITE, size=78):
    return with_shadow(label(text, F_ANTON(size), fg, bg, padx=28, pady=8), blur=6)


def growth_chart(prog):
    w, h = 600, 440
    img = card(w, h)
    d = ImageDraw.Draw(img)
    d.text((22, 14), "PERTUMBUHAN", font=F_TYPE(34), fill=INK)
    base = h - 70
    for gy in range(100, base, 60):
        d.line([(20, gy), (w - 20, gy)], fill=(205, 205, 215), width=2)
    fl = F_ANTON(36)
    for i, s in enumerate(["BLN 1", "BLN 2", "BLN 3"]):
        x = 60 + i * 190
        d.text((x, base + 10), s, font=fl, fill=INK)
    xs = np.linspace(40, w - 40, 40)
    ys = base - 10 - (base - 120) * ((xs - 40) / (w - 80)) ** 1.6
    k = int(len(xs) * clamp(prog))
    if k > 1:
        d.line(list(zip(xs[:k], ys[:k])), fill=TEAL, width=12, joint="curve")
        d.ellipse([xs[k - 1] - 14, ys[k - 1] - 14, xs[k - 1] + 14, ys[k - 1] + 14], fill=TEAL, outline=INK, width=3)
    return with_shadow(img)


def cta_card():
    w, h = 940, 400
    img = card(w, h, WHITE, radius=30)
    d = ImageDraw.Draw(img)
    f = F_ANTON(140)
    s1 = "KEJAR"
    d.text(((w - f.getlength(s1)) / 2, 18), s1, font=f, fill=INK)
    s2 = "KONSISTEN."
    x2 = (w - f.getlength(s2)) / 2
    d.rectangle([x2 - 16, 215, x2 + f.getlength(s2) + 16, 375], fill=TEAL)
    d.text((x2, 196), s2, font=f, fill=WHITE)
    return with_shadow(img, blur=12)


B = {
    "k_tips": kicker("TIPS BISNES  #02"),
    "views_big": big("1.2J VIEWS", 110, INK, YELLOW),
    "views_small": with_shadow(label("300 views", F_TYPE(48), INK, WHITE, padx=18, pady=10), blur=5, alpha=0.3),
    "k_kejar": kicker("KEJAR VIRAL..."),
    "k_bila": kicker("BILA TAK VIRAL..."),
    "putus": stamp("PUTUS ASA", 130),
    "k_hakikat": kicker("HAKIKATNYA..."),
    "ticket": lottery_ticket(),
    "lbl_viral": chip("VIRAL = LOTERI", WHITE, RED, 64),
    "lbl_kons": chip("KONSISTEN = MENABUNG", INK, YELLOW, 58),
    "k_kerap": kicker("LAGI KERAP MUNCUL..."),
    "peluang": chip("1 VIDEO = 1 PELUANG", WHITE, INK, 74),
    "h_sempurna": headline("Tak perlu sempurna.", 92, hl="sempurna"),
    "c_hari": chip("1 VIDEO / HARI", INK, WHITE, 72),
    "c_minggu": chip("3 VIDEO / MINGGU", INK, YELLOW, 72),
    "berterusan": big("ASALKAN BERTERUSAN", 96, WHITE, RED),
    "k_3bln": kicker("3 BULAN DARI SEKARANG"),
    "h_jangan": headline("Jangan kejar viral.", 96, hl="viral", col=(255, 180, 170)),
    "cta": cta_card(),
    "terima": with_shadow(label("terima kasih, diri!", F_MARK(52), INK, WHITE, padx=22, pady=10), blur=5),
}
MONTHS = ["OKTOBER", "NOVEMBER", "DISEMBER", "JANUARI"]


# ---------------------------------------------------------------- scenes
def world(t):
    s0 = kr.scene_start(t)
    c = Image.fromarray(BG[s0]).convert("RGBA")

    if s0 == 0.0:  # hook: viral spike then silence
        draw_full(c, t, "keliru", 0.05, 560)
        if t >= 0.55:
            place(c, views_graph(ease_out((t - 0.6) / 2.0), t >= 1.85), 540, 470, rot=-2,
                  alpha=clamp((t - 0.55) / 0.2))
        pop(c, B["views_big"], t, 0.95, 640, 330, rot=4)
        pop(c, B["views_small"], t, 1.9, 800, 650, rot=3)
        doodle(c, t, 2.0, "?", 960, 520, 140, RED, rot=12)
        doodle(c, t, 2.2, "?", 140, 860, 100, INK, rot=-10)
    elif s0 == 4.0:  # chasing viral -> give up
        pop(c, B["k_bila"], t, 4.1, 300, 200, rot=-3)
        pop(c, ref("stres", 720, seed=41), t, 4.15, 540, 780, rot=-3)
        if t >= 5.25:
            kk = clamp((t - 5.25) / 0.14)
            place(c, B["putus"], 600, 1150, scale=1.9 - 0.9 * ease_out(kk), rot=-9, alpha=kk)
    elif s0 == 6.45:  # lottery vs saving
        pop(c, B["k_hakikat"], t, 6.55, 280, 170, rot=-3)
        pop(c, B["ticket"], t, 7.4, 290, 520, rot=-6)
        pop(c, B["lbl_viral"], t, 8.2, 300, 740, rot=-3)
        if t >= 8.95:  # big red X over the ticket
            k = ease_out((t - 8.95) / 0.25)
            d = ImageDraw.Draw(c)
            d.line([(110, 380), (110 + 360 * k, 380 + 280 * k)], fill=RED + (255,), width=18)
            if t >= 9.1:
                k2 = ease_out((t - 9.1) / 0.25)
                d.line([(470, 380), (470 - 360 * k2, 380 + 280 * k2)], fill=RED + (255,), width=18)
        if t >= 9.5:
            coins = clamp((t - 9.6) / 1.6)
            place(c, piggy_jar(coins), 790, 600, rot=3, scale=ease_back((t - 9.5) / 0.35))
            for j in range(5):
                falling_coin(c, t, 9.7 + j * 0.3, 790, 250, 520)
        pop(c, B["lbl_kons"], t, 10.4, 700, 870, rot=2)
        draw_head(c, t, "sinis", 330, 1300, 0.55, 6.55, rot=-4)
    elif s0 == 11.35:  # show up often -> more people know you
        pop(c, B["k_kerap"], t, 11.45, 540, 140, rot=-2, t1=14.9)
        if t < 15.15:
            n_done = int(clamp((t - 11.8) / 2.8) * 28)
            a = 1 - clamp((t - 14.9) / 0.25)
            place(c, calendar(n_done), 540, 560, rot=-2, alpha=a * clamp((t - 11.5) / 0.2),
                  scale=ease_back((t - 11.5) / 0.4))
        if t >= 15.0:  # people icons join one by one
            n = int(clamp((t - 15.1) / 3.6) * 15) + 1
            for k in range(n):
                r, col = divmod(k, 5)
                x, y = 160 + col * 190, 300 + r * 190
                pop(c, ICONS[k % len(ICONS)], t, 15.1 + k * 3.6 / 15, x, y, rot=(k % 3 - 1) * 4)
        pop(c, B["peluang"], t, 16.55, 540, 900, rot=-2)
        draw_head(c, t, "senyum", 540, 1300, 0.62, 11.45, rot=2)
        sparkle(c, t, 11.9, 870, 1080, 50)
        sparkle(c, t, 12.1, 210, 1150, 36)
    elif s0 == 19.4:  # doesn't need to be perfect
        pop(c, ref("laptop_kerja", 470, "cukup baik!", 42), t, 19.7, 320, 640, rot=-5)
        pop(c, B["c_hari"], t, 21.0, 760, 520, rot=3)
        pop(c, B["c_minggu"], t, 22.25, 740, 700, rot=-2)
        pop(c, B["berterusan"], t, 23.45, 540, 990, rot=-3)
        underline_marker(c, t, 23.9, 170, 910, 1075, INK)
        draw_head(c, t, "asal", 820, 1360, 0.55, 19.55, rot=-4)
    elif s0 == 25.0:  # three months from now
        pop(c, B["k_3bln"], t, 25.1, 330, 170, rot=-3)
        mi = min(3, int(clamp((t - 25.4) / 1.1) * 4))
        if t >= 25.2:
            place(c, chip(MONTHS[mi], WHITE, RED, 90), 760, 330, rot=3 + (2 if mi % 2 else -2),
                  scale=ease_back((t - 25.2) / 0.3))
        if t >= 26.4:
            place(c, growth_chart(ease_out((t - 26.5) / 1.8)), 360, 690, rot=-2, alpha=clamp((t - 26.4) / 0.2))
        draw_head(c, t, "terkejut", 790, 1270, 0.6, 25.15, rot=5)
        doodle(c, t, 26.6, "!!", 1010, 1000, 140, RED, rot=12)
        pop(c, B["terima"], t, 27.3, 330, 1010, rot=-4)
    else:  # CTA
        kr.rays(c, t, 540, 1100, alpha=clamp((t - 29.1) / 0.5))
        draw_full(c, t, "tunjuk", 29.1, 560, scale=0.92)
    return c


def hud(c, t):
    if t < 4.0:
        pop(c, B["k_tips"], t, 0.2, 260, 120, rot=-3)
    if t >= 29.1:
        pop(c, B["h_jangan"], t, 29.3, 540, 190, rot=-1.5, t1=31.2)
        if 30.4 <= t < 31.45:  # strike through "viral"
            k = ease_out((t - 30.4) / 0.3)
            ImageDraw.Draw(c).line([(640, 200), (640 + 300 * k, 185)], fill=RED + (255,), width=14)
        pop(c, B["cta"], t, 31.38, 540, 330, rot=-1.5)
        if t >= 32.85:
            pulse = 1 + 0.04 * max(0.0, math.sin((t - 32.85) * 7))
            pop(c, A["follow"], t, 32.85, 540, 640, scale=pulse)
        if t >= 33.3:
            u = ease_out((t - 33.3) / 0.4)
            tap = 1 - 0.12 * max(0.0, math.sin(clamp((t - 33.75) / 0.25) * math.pi))
            place(c, A["hand"], 900 + 200 * (1 - u), 720 + 120 * (1 - u), scale=tap, rot=-15, alpha=u)
            if t >= 33.85:
                r = (t - 33.85) * 260
                a = int(255 * clamp(1 - (t - 33.85) / 0.6))
                ImageDraw.Draw(c).ellipse([830 - r, 650 - r * 0.6, 830 + r, 650 + r * 0.6], outline=INK + (a,), width=6)
        pop(c, A["save"], t, 33.9, 540, 790, rot=1)


def frame(i):
    t = i / FPS
    arr = kr.apply_camera(np.asarray(world(t).convert("RGB")), t).astype(np.float32)
    arr += kr.GRAIN[i % len(kr.GRAIN)][..., None] * 0.6
    c = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    hud(c, t)
    kr.draw_caption(c, t, y_center=1640 if t < 29.1 else 1660)
    kr.draw_wipe(c, t)
    rgb = np.asarray(c.convert("RGB"))
    if t < 0.2 or t > DUR - 0.35:
        f = clamp(t / 0.2) * clamp((DUR - t) / 0.35)
        rgb = (rgb.astype(np.float32) * f).astype(np.uint8)
    return rgb


if __name__ == "__main__":
    if len(sys.argv) > 2:
        for ts in sys.argv[2:]:
            Image.fromarray(frame(int(float(ts) * FPS))).save(f"{WD}/k2_{ts}.jpg", quality=85)
    else:
        out = sys.stdout.buffer
        for i in range(N):
            out.write(frame(i).tobytes())
            if i % 100 == 0:
                print(f"frame {i}/{N}", file=sys.stderr, flush=True)
