"""Episode — "Kenapa Iklan Anda Tak Jalan" (~46 s, 1080x1920@30), BREAKING NEWS concept.

A TV news studio: the presenter (MAN, black & white, waist-up behind the anchor desk, pose
changing per beat) reads a "breaking" business report. Video wall behind him carries the
B-roll (field report, case file, CCTV scroll footage, hook cards, A/B test), with LIVE bug,
clock, channel logo "BISNES 24", lower thirds, a running ticker and stinger transitions.

Usage: python3 berita_render.py <workdir> [t1 t2 ...]   (needs fb/ poses, refs/, kolaj_render assets)
"""
import math
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import kolaj_render as kr
from kolaj_render import F_ANTON, FPS, H, W, clamp, ease_back, ease_inout, ease_out, place, text_size

WD = sys.argv[1]
DUR = 46.0
N = int(DUR * FPS)

NAVY = (10, 22, 52)
BLUE = (20, 80, 190)
RED = (215, 25, 35)
WHITE = (255, 255, 255)
INK = (12, 14, 22)
GOLD = (255, 200, 40)
GREEN = (40, 200, 110)
F_B = lambda s: kr.font("InterXB", s)
F_M = lambda s: kr.font("InterB", s)
NAME, TITLE = "MAN", "Pakar Video Bisnes"


# ---------------------------------------------------------------- anchor (waist-up cut-outs)
def clean_mask(m):
    b = (m > 0.5).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(b)
    if n > 2:
        m = m * (lab == 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA])))
    return m


def anchor(name, keep=0.5, up=2.2):
    im = Image.open(f"{WD}/fb/{name}.jpg").convert("RGB")
    mk = Image.open(f"{WD}/fb/{name}_mask.png").convert("L")
    w, h = int(im.width * up), int(im.height * up)
    src = np.asarray(im.resize((w, h), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 80, 2))).astype(np.float32)
    m = clean_mask(np.clip((np.asarray(mk.resize((w, h), Image.LANCZOS)).astype(np.float32) / 255 - 0.25) / 0.5, 0, 1))
    ys, xs = np.where(m > 0.5)
    y0 = ys.min()
    y1 = int(y0 + (ys.max() - y0) * keep)
    src, m = src[y0:y1], m[y0:y1]
    xs = np.where(m.max(axis=0) > 0.5)[0]
    src, m = src[:, xs.min():xs.max() + 1], m[:, xs.min():xs.max() + 1]
    s = kr.bw_dramatic(src)
    pad = 20
    mp = cv2.copyMakeBorder(m, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    sp = cv2.copyMakeBorder(s, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    rim = cv2.GaussianBlur(cv2.dilate(mp, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))), (0, 0), 2)
    rgb = sp * mp[..., None] + np.array([170, 200, 255], np.float32) * (1 - mp[..., None])  # cool rim light
    return Image.fromarray(np.dstack([rgb, np.maximum(mp, rim * 0.8) * 255]).clip(0, 255).astype(np.uint8), "RGBA")


ANCHOR = {p: anchor(p) for p in ["terkejut_meja", "terangkan", "fikir", "telefon", "jam", "menang"]}
DESK_TOP = 1390


def draw_anchor(c, t, pose, t0):
    spr = ANCHOR[pose]
    sc = min(560 / spr.height, 760 / spr.width)  # waist-up, head just under the video wall
    h = spr.height * sc
    kr.alive(c, spr, t, t0, 540, DESK_TOP - h / 2 + 70, sc=sc, rise=160)


# ---------------------------------------------------------------- studio
def studio():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.array(NAVY, np.float32) * (1 - yy / H * 0.4)[..., None] * np.ones((1, 1, 3))
    g += np.exp(-(((xx - 540) / 600) ** 2 + ((yy - 1000) / 700) ** 2))[..., None] * np.array([30, 60, 140])
    img = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    for k in range(9):  # vertical light panels
        x = 40 + k * 125
        d.rectangle([x, 900, x + 70, 1390], fill=(60, 110, 220, 40))
    for y in range(160, 1390, 46):  # fine horizontal scan pattern on the back wall
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 8))
    return img


STUDIO = studio()


def desk():
    w, h = W + 40, 200
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(0, 30), (w, 30), (w - 60, h), (60, h)], fill=(14, 30, 70, 255))
    d.rectangle([0, 0, w, 34], fill=(225, 230, 240, 255))
    d.rectangle([0, 34, w, 44], fill=RED)
    return img


DESK = desk()
SCREEN = (60, 190, 1020, 800)  # video wall


def logo_bug():
    img = Image.new("RGBA", (300, 90), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 120, 89], fill=RED)
    d.text((14, 6), "24", font=F_ANTON(70), fill=WHITE)
    d.rectangle([120, 0, 299, 89], fill=WHITE)
    d.text((134, 18), "BISNES", font=F_ANTON(48), fill=INK)
    return img


LOGO = logo_bug()


def top_bar(c, t):
    c.alpha_composite(LOGO, (40, 60))
    d = ImageDraw.Draw(c)
    on = int(t * 2) % 2 == 0
    d.rounded_rectangle([W - 330, 70, W - 190, 140], radius=10, fill=RED)
    if on:
        d.ellipse([W - 316, 92, W - 290, 118], fill=WHITE)
    d.text((W - 282, 76), "LIVE", font=F_ANTON(50), fill=WHITE)
    mins = 21 * 60 + int(t // 60)
    s = f"{mins // 60:02d}:{mins % 60:02d}"
    d.rounded_rectangle([W - 180, 70, W - 40, 140], radius=10, fill=(0, 0, 0, 160))
    d.text((W - 162, 76), s, font=F_ANTON(50), fill=WHITE)


TICKER = ("BERITA TERKINI  •  Owner bisnes disaran guna video pendek  •  Hook 3 saat jadi penentu  •  "
          "Testimoni video lebih dipercayai  •  Konsisten kalahkan viral  •  Muka anda ialah brand anda  •  ")
F_TICK = F_M(40)
TICK_W = F_TICK.getlength(TICKER)


def ticker(c, t):
    d = ImageDraw.Draw(c)
    y = 1590
    d.rectangle([0, y, W, y + 64], fill=(245, 245, 250))
    off = (t * 190) % TICK_W
    x = 210 - off
    while x < W:
        d.text((x, y + 9), TICKER, font=F_TICK, fill=INK)
        x += TICK_W
    d.rectangle([0, y, 200, y + 64], fill=RED)
    d.text((24, y + 6), "TERKINI", font=F_ANTON(46), fill=WHITE)


def lower_third(c, t, label, text, t0, t1=None, label_col=RED):
    if t < t0 or (t1 is not None and t > t1 + 0.25):
        return
    k = ease_out((t - t0) / 0.35)
    if t1 is not None and t > t1:
        k *= 1 - ease_out((t - t1) / 0.25)
    f1, f2 = F_ANTON(46), F_B(50)
    lw = int(f1.getlength(label)) + 40
    tw = int(f2.getlength(text)) + 50
    w = min(W - 40, lw + tw)
    img = Image.new("RGBA", (w, 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, lw, 62], fill=label_col + (255,))
    d.text((20, 4), label, font=f1, fill=WHITE)
    d.rectangle([0, 62, w, 150], fill=WHITE + (255,))
    d.text((24, 76), text, font=f2, fill=INK)
    clip = Image.new("RGBA", img.size, (0, 0, 0, 0))
    cw = int(w * k)
    if cw > 0:
        clip.paste(img.crop((0, 0, cw, 150)), (0, 0))
        c.alpha_composite(clip, (20, 1430))


# ---------------------------------------------------------------- video-wall content
def wall_frame(c, inner):
    x0, y0, x1, y1 = SCREEN
    lay = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    mk = Image.new("L", lay.size, 0)
    ImageDraw.Draw(mk).rounded_rectangle([0, 0, lay.width - 1, lay.height - 1], radius=26, fill=255)
    lay.paste(inner, (0, 0), mk)
    glow = Image.new("RGBA", (lay.width + 60, lay.height + 60), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle([30, 30, lay.width + 30, lay.height + 30], radius=30,
                                           outline=(90, 150, 255, 200), width=10)
    c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10)), (x0 - 30, y0 - 30))
    c.alpha_composite(lay, (x0, y0))


def panel(col_a, col_b):
    w, h = SCREEN[2] - SCREEN[0], SCREEN[3] - SCREEN[1]
    g = np.linspace(0, 1, h)[:, None, None]
    arr = (np.array(col_a, np.float32) * (1 - g) + np.array(col_b, np.float32) * g) * np.ones((1, w, 1))
    img = Image.fromarray(arr.astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    for x in range(0, w, 40):
        d.line([(x, 0), (x, h)], fill=(255, 255, 255, 10))
    return img


PW, PH = SCREEN[2] - SCREEN[0], SCREEN[3] - SCREEN[1]


def check(d, cx, cy, r, col=WHITE, width=10):
    d.line([(cx - r, cy), (cx - r * 0.3, cy + r * 0.7), (cx + r, cy - r * 0.7)], fill=col, width=width, joint="curve")


def cross(d, cx, cy, r, col=RED, width=10):
    d.line([(cx - r, cy - r), (cx + r, cy + r)], fill=col, width=width)
    d.line([(cx - r, cy + r), (cx + r, cy - r)], fill=col, width=width)


def ctext(d, text, f, cx, y, col):
    d.text((cx - f.getlength(text) / 2, y), text, font=f, fill=col)


def photo(name, w, h, folder="refs"):
    im = Image.open(f"{WD}/{folder}/{name}.jpg").convert("RGB")
    r = w / h
    if im.width / im.height > r:
        nw = int(im.height * r)
        im = im.crop(((im.width - nw) // 2, 0, (im.width - nw) // 2 + nw, im.height))
    else:
        nh = int(im.width / r)
        im = im.crop((0, 0, im.width, nh))
    return Image.fromarray(kr.bw_dramatic(np.asarray(im.resize((w, h), Image.LANCZOS)).astype(np.float32))
                           .astype(np.uint8)).convert("RGBA")


STRES = photo("stres", 420, 330)
LAPTOP = photo("laptop_kerja", 300, 200)


def wall_breaking(t):
    img = panel((120, 10, 20), (40, 4, 10))
    d = ImageDraw.Draw(img)
    on = (int(t * 3) % 2 == 0) or t > 1.4
    if on:
        ctext(d, "BERITA", F_ANTON(150), PW / 2, 60, WHITE)
        ctext(d, "TERGEMPAR", F_ANTON(150), PW / 2, 220, GOLD)
    rng = np.random.default_rng(3)
    for k in range(8):  # cash flying away
        if t < 1.8 + k * 0.25:
            continue
        u = (t - 1.8 - k * 0.25) * 0.5
        x = (rng.uniform(80, PW - 80) + u * 260 * (1 if k % 2 else -1)) % PW
        y = PH - 40 - u * 520 + 30 * math.sin(u * 6 + k)
        bill = Image.new("RGBA", (130, 64), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bill)
        bd.rectangle([0, 0, 129, 63], fill=(70, 160, 90, 255), outline=(20, 60, 30, 255), width=4)
        bd.text((26, 8), "RM", font=F_ANTON(40), fill=(230, 255, 230))
        place(img, bill, x, y, rot=20 * math.sin(u * 4 + k))
    return img


def wall_report(t):
    img = panel((25, 35, 60), (10, 14, 28))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 380, 54], fill=GOLD)
    d.text((16, 4), "LAPORAN LAPANGAN", font=F_ANTON(40), fill=INK)
    img.alpha_composite(STRES, (40, 90))
    d.rectangle([40, 90, 460, 420], outline=WHITE, width=4)
    if t >= 4.82:
        v = int(3500 * ease_out((t - 4.9) / 2.3))
        d.text((510, 110), "BAJET IKLAN", font=F_M(36), fill=(190, 200, 230))
        d.text((510, 150), f"RM{v:,}", font=F_ANTON(110), fill=GOLD)
    if t >= 7.43:
        d.text((510, 330), "JUALAN", font=F_M(36), fill=(190, 200, 230))
        on = int(t * 3) % 2 == 0
        d.text((510, 370), "0", font=F_ANTON(140), fill=RED if on else (120, 30, 30))
        if t >= 8.8:
            ctext(d, "...senyap.", F_M(44), PW / 2 + 180, 540, (180, 180, 200))
    return img


def wall_case(t):
    img = panel((50, 40, 30), (20, 16, 12))
    d = ImageDraw.Draw(img)
    # folder
    d.rounded_rectangle([60, 70, 520, 520], radius=14, fill=(215, 175, 110))
    d.rectangle([60, 50, 240, 90], fill=(215, 175, 110))
    d.text((90, 120), "FAIL SIASATAN", font=F_ANTON(56), fill=INK)
    d.text((90, 200), "Kes: Iklan tak jalan", font=F_M(32), fill=INK)
    if t >= 11.8:
        k = clamp((t - 11.8) / 0.15)
        st = kr.stamp("SULIT", 80, RED)
        place(img, st, 300, 400, scale=1.6 - 0.6 * ease_out(k), rot=-12, alpha=k)
    if t >= 13.05:
        d.text((600, 120), "BAJET", font=F_ANTON(110), fill=WHITE)
        if t >= 13.6:
            k = ease_out((t - 13.6) / 0.25)
            d.line([(590, 180), (590 + 290 * k, 180)], fill=RED, width=16)
            if t >= 13.9:
                cross(d, 610, 296, 16, RED, 8)
                ctext(d, "BUKAN PUNCA", F_ANTON(46), 760, 270, RED)
    if t >= 15.96:
        k = ease_back((t - 15.96) / 0.35)
        lab = Image.new("RGBA", (420, 230), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lab)
        ld.rectangle([0, 0, 419, 229], fill=RED)
        ctext(ld, "PUNCA:", F_M(40), 210, 14, WHITE)
        ctext(ld, "3 SAAT", F_ANTON(120), 210, 62, GOLD)
        place(img, lab, 750, 440, scale=k, rot=4)
    return img


def wall_cctv(t):
    img = panel((40, 52, 44), (20, 26, 22))
    d = ImageDraw.Draw(img)
    # phone with feed
    px0, py0 = 330, 40
    d.rounded_rectangle([px0, py0, px0 + 300, py0 + 540], radius=34, fill=(15, 15, 15))
    off = (t * 900) % 180 if t < 20.45 else 0
    for k in range(-1, 4):
        y = py0 + 30 + k * 180 - off
        if py0 + 20 < y < py0 + 500:
            d.rounded_rectangle([px0 + 18, y, px0 + 282, y + 160], radius=14,
                                fill=[(150, 160, 150), (110, 120, 110), (180, 190, 180)][k % 3])
    # thumb swiping
    ty = 420 - ((t * 3) % 1) * 220 if t < 20.45 else 400
    d.ellipse([px0 + 190, ty, px0 + 290, ty + 140], fill=(200, 200, 190), outline=INK, width=4)
    # CCTV overlay
    d.text((24, 16), "CAM 03", font=F_M(34), fill=WHITE)
    if int(t * 2) % 2 == 0:
        d.ellipse([PW - 150, 22, PW - 126, 46], fill=RED)
    d.text((PW - 118, 14), "REC", font=F_M(34), fill=WHITE)
    sec = min(3, int(max(0.0, t - 17.75) * 1.2) + 1) if t >= 17.75 else 0
    if sec:
        d.text((40, PH - 120), f"0:0{sec}", font=F_ANTON(96), fill=GOLD)
    if t >= 20.45:
        k = ease_back((t - 20.45) / 0.3)
        sk = Image.new("RGBA", (320, 130), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sk)
        sd.rectangle([0, 0, 319, 129], fill=RED)
        ctext(sd, "SKIP ▶▶", F_ANTON(86), 160, 10, WHITE)
        place(img, sk, 790, 200, scale=k, rot=-6)
    if t >= 21.87:
        k = ease_out((t - 21.87) / 0.3)
        ad = Image.new("RGBA", (300, 180), (0, 0, 0, 0))
        ad_d = ImageDraw.Draw(ad)
        ad_d.rectangle([0, 0, 299, 179], fill=(80, 90, 110), outline=WHITE, width=4)
        ctext(ad_d, "IKLAN ANDA", F_ANTON(54), 150, 54, WHITE)
        place(ad, kr.stamp("TAK SEMPAT", 44, RED), 150, 140, rot=-8,
              alpha=clamp((t - 22.77) / 0.12)) if t >= 22.77 else None
        place(img, ad, 790, 440 + 30 * (1 - k), alpha=k)
    # scanlines + tint
    arr = np.asarray(img.convert("RGB")).astype(np.float32)
    arr[::4] *= 0.8
    arr = arr * np.array([0.85, 1.0, 0.85])
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")


def hook_card(title, sub, icon, col):
    w, h = 280, 330
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=22, fill=(18, 26, 50, 255), outline=col + (255,), width=6)
    d.ellipse([w / 2 - 70, 30, w / 2 + 70, 170], fill=col + (255,))
    if icon == "check":
        check(d, w / 2, 100, 40, WHITE, 14)
    else:
        ctext(d, icon, F_ANTON(100), w / 2, 38, WHITE)
    ctext(d, title, F_ANTON(58), w / 2, 190, WHITE)
    ctext(d, sub, F_M(26), w / 2, 270, (180, 190, 220))
    return img


HOOKS = [hook_card("SOALAN", "kena masalah", "?", BLUE), hook_card("KEJUTAN", "kenyataan berani", "!", RED),
         hook_card("HASIL", "tunjuk di awal", "check", GREEN)]


def wall_hooks(t):
    img = panel((16, 40, 100), (8, 16, 40))
    d = ImageDraw.Draw(img)
    if t >= 24.4:
        ctext(d, "3 JENIS HOOK", F_ANTON(96), PW / 2, 30, WHITE)
        ctext(d, "untuk 3 saat pertama", F_M(34), PW / 2, 150, (180, 190, 230))
    for j, tt in enumerate([26.55, 29.13, 31.44]):
        if t >= tt:
            place(img, HOOKS[j], 165 + j * 315, 400, scale=ease_back((t - tt) / 0.35))
    return img


def wall_ab(t):
    img = panel((20, 30, 70), (8, 12, 30))
    d = ImageDraw.Draw(img)
    ctext(d, "UJIAN HOOK", F_ANTON(86), PW / 2, 24, WHITE)
    vals = [0.45, 0.9, 0.6]
    for j, (lab, v) in enumerate(zip(["HOOK A", "HOOK B", "HOOK C"], vals)):
        y = 170 + j * 130
        d.text((40, y + 10), lab, font=F_ANTON(54), fill=WHITE)
        p = ease_out((t - 35.5 - j * 0.3) / 1.6) if t >= 35.5 + j * 0.3 else 0
        bw = 560 * v * p
        win = j == 1 and t >= 38.0
        d.rounded_rectangle([250, y + 10, 250 + max(bw, 4), y + 80], radius=12, fill=GOLD if win else (90, 120, 200))
        if p > 0.05:
            d.text((260 + bw, y + 18), f"{int(9800 * v * p):,}", font=F_M(38), fill=WHITE)
    if t >= 38.0:
        k = ease_back((t - 38.0) / 0.3)
        tag = Image.new("RGBA", (300, 90), (0, 0, 0, 0))
        td = ImageDraw.Draw(tag)
        td.rounded_rectangle([0, 0, 299, 89], radius=20, fill=GREEN)
        check(td, 46, 45, 18, WHITE, 8)
        ctext(td, "KEKALKAN", F_ANTON(56), 172, 12, WHITE)
        place(img, tag, 700, 560, scale=k, rot=-4)
    return img


def wall_signoff(t):
    img = panel((140, 12, 24), (30, 6, 12))
    lg = LOGO.resize((600, 180), Image.LANCZOS)
    place(img, lg, PW / 2, 220, scale=ease_back((t - 40.2) / 0.4) if t >= 40.2 else 0.01)
    d = ImageDraw.Draw(img)
    if t >= 42.5:
        ctext(d, "Follow untuk berita", F_B(50), PW / 2, 370, WHITE)
        ctext(d, "bisnes seterusnya", F_B(50), PW / 2, 430, WHITE)
    return img


# ---------------------------------------------------------------- timeline
CUTS = [4.6, 11.2, 17.5, 24.1, 34.1, 40.1]
SCENES = [(0.0, wall_breaking, "terkejut_meja", "OWNER BISNES MEMBAZIR DUIT IKLAN?"),
          (4.6, wall_report, "terangkan", "IKLAN JALAN, JUALAN SENYAP"),
          (11.2, wall_case, "fikir", "SIASATAN: PUNCA DIKENAL PASTI"),
          (17.5, wall_cctv, "telefon", "3 SAAT PERTAMA PENENTU"),
          (24.1, wall_hooks, "terangkan", "PANDUAN: 3 JENIS HOOK"),
          (34.1, wall_ab, "jam", "PAKAR: UJI & KEKALKAN YANG TERBAIK"),
          (40.1, wall_signoff, "menang", "IKUTI BISNES 24")]
PUNCHES = [0.07, 7.43, 15.96, 20.45, 38.0]


def scene_of(t):
    return max([s for s in SCENES if s[0] <= t], key=lambda s: s[0])


CAPS = [
    (0.05, 1.6, "BERITA TERGEMPAR.", 1.31),
    (1.6, 4.6, "Ramai owner bisnes sedang membazir DUIT IKLAN, tanpa sedar.", 4.42),
    (4.7, 7.35, "Iklan dah jalan, duit dah keluar...", 7.22),
    (7.35, 11.2, "tapi jualan, masih SENYAP.", 10.72),
    (11.3, 14.8, "Siasatan kami mendapati, puncanya BUKAN BAJET.", 14.57),
    (14.8, 17.5, "Puncanya, TIGA SAAT PERTAMA.", 17.2),
    (17.6, 21.7, "Kalau tiga saat pertama video anda tak menarik, orang terus SCROLL.", 21.55),
    (21.7, 24.1, "Iklan anda, TAK SEMPAT buat kerja.", 23.83),
    (24.2, 26.4, "Jadi, mulakan dengan HOOK.", 26.16),
    (26.4, 29.0, "SOALAN yang kena dengan masalah pelanggan.", 28.7),
    (29.0, 31.3, "Atau kenyataan yang MENGEJUTKAN.", 31.05),
    (31.3, 34.1, "Atau tunjuk HASIL, terus di awal video.", 33.82),
    (34.2, 40.1, "Pakar menasihatkan, uji dua tiga hook berbeza, dan KEKALKAN yang paling ramai tonton.", 39.79),
    (40.2, 42.4, "Itu sahaja laporan untuk hari ini.", 42.15),
    (42.4, DUR, "FOLLOW untuk berita bisnes seterusnya.", 44.63),
]


def cap_words(s, vo_end, text):
    words = text.split()
    L = [len(w_) + 2 for w_ in words]
    acc, times = 0, []
    for l in L:
        times.append(s + (vo_end - s) * acc / sum(L))
        acc += l
    return words, times


CAP_DATA = [(s, e, *cap_words(s, ve, txt)) for s, e, txt, ve in CAPS]


def is_key(w_):
    core = w_.strip(".,?!\"—…")
    return len(core) > 1 and core.isupper()


def draw_caption(c, t, y=1765):
    for s, e, words, times in CAP_DATA:
        if not (s - 0.02 <= t < e):
            continue
        f = F_B(56)
        space = f.getlength(" ")
        lines, cur, cw = [], [], 0
        for w_ in words:
            wl = f.getlength(w_)
            if cur and cw + space + wl > 960:
                lines.append(cur)
                cur, cw = [], 0
            cur.append(w_)
            cw += (space if cw else 0) + wl
        lines.append(cur)
        asc, desc = f.getmetrics()
        lh = asc + desc + 6
        widths = [sum(f.getlength(w_) for w_ in l) + space * (len(l) - 1) for l in lines]
        bw, bh = int(max(widths)) + 50, lh * len(lines) + 24
        strip = Image.new("RGBA", (bw, bh), (0, 0, 0, 200))
        d = ImageDraw.Draw(strip)
        idx = 0
        for li, l in enumerate(lines):
            x = (bw - widths[li]) / 2
            y0 = 10 + li * lh
            for w_ in l:
                wl = f.getlength(w_)
                if t >= times[idx]:
                    k = ease_out((t - times[idx]) / 0.15)
                    d.text((x, y0 + 10 * (1 - k)), w_, font=f, fill=(GOLD if is_key(w_) else WHITE) + (int(255 * k),))
                x += wl + space
                idx += 1
        place(c, strip, W / 2, y, alpha=clamp((t - s + 0.02) / 0.12) * clamp((e - t) / 0.1))


def stinger(c, t):
    """News stinger: red/blue diagonal bands sweep across with the logo."""
    for ct in CUTS:
        u = (t - (ct - 0.3)) / 0.6
        if 0 <= u <= 1:
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(lay)
            for j, col in enumerate([RED, BLUE, WHITE]):
                x = -1600 + (W + 3200) * ease_inout(clamp(u * 1.15 - j * 0.07))
                d.polygon([(x, 0), (x + 700, 0), (x + 700 - 900, H), (x - 900, H)], fill=col + (255,))
            c.alpha_composite(lay)
            if 0.3 < u < 0.7:
                place(c, LOGO, W / 2, H / 2, scale=2.0)


def frame(i):
    t = i / FPS
    s0, wall, pose, headline = scene_of(t)
    c = STUDIO.copy()
    wall_frame(c, wall(t))
    draw_anchor(c, t, pose, s0 + 0.05)
    c.alpha_composite(DESK, (-20, DESK_TOP))
    top_bar(c, t)
    if t < 4.6:
        lower_third(c, t, NAME, TITLE, 0.4, 2.6, label_col=BLUE)
        lower_third(c, t, "BERITA TERGEMPAR", headline, 2.9)
    else:
        lower_third(c, t, "BERITA TERGEMPAR" if s0 < 40 else "BISNES 24", headline, s0 + 0.2)
    ticker(c, t)
    if 42.6 <= t:
        pulse = 1 + 0.04 * max(0.0, math.sin((t - 42.6) * 7))
        kr.pop(c, kr.A["follow"], t, 42.6, 540, 790, scale=pulse)
    arr = np.asarray(c.convert("RGB"))
    z = 1.0
    for pt in PUNCHES:
        dt = t - pt
        if 0 <= dt < 0.6:
            z *= 1 + 0.05 * (dt / 0.06 if dt < 0.06 else math.exp(-(dt - 0.06) * 7))
    nxt = [x for x in CUTS if x > t]
    s1 = nxt[0] if nxt else DUR
    z *= 1 + 0.03 * ease_inout((t - s0) / (s1 - s0))
    if z != 1.0:
        M = np.float32([[z, 0, W / 2 - z * W / 2], [0, z, 900 - z * 900]])
        arr = cv2.warpAffine(arr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    arr = arr.astype(np.float32) + kr.GRAIN[i % len(kr.GRAIN)][..., None] * 0.35
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    stinger(out, t)
    draw_caption(out, t)
    rgb = np.asarray(out.convert("RGB"))
    if t < 0.15 or t > DUR - 0.35:
        rgb = (rgb.astype(np.float32) * clamp(t / 0.15) * clamp((DUR - t) / 0.35)).astype(np.uint8)
    return rgb


if __name__ == "__main__":
    if len(sys.argv) > 2:
        for ts in sys.argv[2:]:
            Image.fromarray(frame(int(float(ts) * FPS))).save(f"{WD}/bn_{ts}.jpg", quality=85)
    else:
        out = sys.stdout.buffer
        for i in range(N):
            out.write(frame(i).tobytes())
            if i % 100 == 0:
                print(f"frame {i}/{N}", file=sys.stderr, flush=True)
