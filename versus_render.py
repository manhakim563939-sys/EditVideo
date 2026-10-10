"""Episode 9 — "Testimoni Video Lagi Kuat Dari Iklan" (~43 s, 1080x1920@30).

Concept "VERSUS": a fighting-game match, IKLAN vs TESTIMONI. Full-body black & white cut-outs
of the presenter act out each beat on a spot-lit arena; close-up faces appear as fighter
portraits and combo cards. HP bars, ROUND banners, hit sparks, screen shake, COMBO counter,
K.O. flash, then a CTA. Laid out on the ElevenLabs VO timeline.

Usage: python3 versus_render.py <workdir> [t1 t2 ...]
  <workdir>/fb/<pose>.jpg + <pose>_mask.png   full-body poses; fb/cu_*.jpg close-ups
  plus the kolaj_render.py assets (fonts etc.).
"""
import math
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import kolaj_render as kr
from kolaj_render import F_ANTON, F_CAP, FPS, H, W, clamp, ease_back, ease_inout, ease_out, place, text_size

WD = sys.argv[1]
DUR = 43.2
N = int(DUR * FPS)

RED = (235, 50, 50)
GOLD = (255, 200, 30)
BLUE = (40, 150, 255)
WHITE = (255, 255, 255)
INK = (12, 12, 20)
GREEN = (60, 220, 120)
FLOOR_Y = 1560


# ---------------------------------------------------------------- fighters (full-body cut-outs)
def clean_mask(m):
    """Keep the largest blob (the person) so stray table/chair bits drop out."""
    b = (m > 0.5).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(b)
    if n > 2:
        keep = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        m = m * (lab == keep)
    return m


def fighter(name, up=2.0):
    im = Image.open(f"{WD}/fb/{name}.jpg").convert("RGB")
    mk = Image.open(f"{WD}/fb/{name}_mask.png").convert("L")
    w, h = int(im.width * up), int(im.height * up)
    src = np.asarray(im.resize((w, h), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 80, 2))).astype(np.float32)
    m = np.asarray(mk.resize((w, h), Image.LANCZOS)).astype(np.float32) / 255
    m = clean_mask(np.clip((m - 0.25) / 0.5, 0, 1))
    ys, xs = np.where(m > 0.5)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    src, m = src[y0:y1, x0:x1], m[y0:y1, x0:x1]
    s = kr.bw_dramatic(src)
    pad = 30
    mp = cv2.copyMakeBorder(m, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    sp = cv2.copyMakeBorder(s, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    ol = cv2.GaussianBlur(cv2.dilate(mp, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (19, 19))), (0, 0), 1.0)
    rgb = sp * mp[..., None] + 255 * (1 - mp[..., None])
    return Image.fromarray(np.dstack([rgb, ol * 255]).clip(0, 255).astype(np.uint8), "RGBA")


POSES = ["terangkan", "thumbs_produk", "menguap", "tengok_barang", "terkejut_meja", "biskut", "telefon", "jam",
         "fikir", "menang", "ukur_kayu", "kopi"]
FIG = {p: fighter(p) for p in POSES}


def portrait(name, size, ring):
    im = Image.open(f"{WD}/fb/{name}.jpg").convert("RGB")
    s = min(im.width, im.height)
    im = im.crop(((im.width - s) // 2, int(im.height * 0.02), (im.width - s) // 2 + s, int(im.height * 0.02) + s))
    g = kr.bw_dramatic(np.asarray(im.resize((size, size), Image.LANCZOS)).astype(np.float32))
    out = Image.new("RGBA", (size + 16, size + 16), (0, 0, 0, 0))
    mk = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mk).ellipse([0, 0, size - 1, size - 1], fill=255)
    ImageDraw.Draw(out).ellipse([0, 0, size + 15, size + 15], fill=ring + (255,))
    out.paste(Image.fromarray(g.astype(np.uint8)), (8, 8), mk)
    return out


def photo_card(name, w, h, ring):
    im = Image.open(f"{WD}/fb/{name}.jpg").convert("RGB")
    r = w / h
    if im.width / im.height > r:
        nw = int(im.height * r)
        im = im.crop(((im.width - nw) // 2, 0, (im.width - nw) // 2 + nw, im.height))
    else:
        nh = int(im.width / r)
        im = im.crop((0, 0, im.width, nh))
    g = kr.bw_dramatic(np.asarray(im.resize((w, h), Image.LANCZOS)).astype(np.float32))
    out = Image.new("RGBA", (w + 16, h + 16), ring + (255,))
    out.paste(Image.fromarray(g.astype(np.uint8)), (8, 8))
    return out


def draw_fighter(c, t, pose, t0, cx, scale=0.9, flip=False, rise=500, t1=None, rot=0.0):
    spr = FIG[pose]
    if flip:
        spr = spr.transpose(Image.FLIP_LEFT_RIGHT)
    if t < t0 or (t1 is not None and t > t1 + 0.3):
        return
    h = spr.height * scale
    # floor shadow
    sh = Image.new("RGBA", (int(spr.width * scale * 1.1), 70), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([0, 0, sh.width - 1, 69], fill=(0, 0, 0, 150))
    a = clamp((t - t0) / 0.2)
    place(c, sh.filter(ImageFilter.GaussianBlur(10)), cx, FLOOR_Y - 10, alpha=a)
    kr.alive(c, spr, t, t0, cx, FLOOR_Y - h / 2 + 18, sc=scale, rot=rot, t1=t1, rise=rise)


# ---------------------------------------------------------------- arena background
def arena(tint, seed):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.array([10, 10, 22], np.float32) + np.array(tint, np.float32) * (1 - yy / H)[..., None] * 0.6
    img = base * np.ones((1, 1, 3), np.float32)
    for sx, col in [(250, tint), (830, (60, 90, 200))]:  # two spotlight cones
        cone = np.clip(1 - np.abs(xx - sx - (yy / H) * (540 - sx) * 0.3) / (90 + yy * 0.32), 0, 1) ** 1.5
        img += cone[..., None] * np.array(col, np.float32) * 0.35
    # floor
    floor = yy > FLOOR_Y - 40
    img[floor] = img[floor] * 0.55 + np.array([25, 25, 40], np.float32)
    pool = np.exp(-(((xx - 540) / 520) ** 2 + ((yy - FLOOR_Y) / 110) ** 2))
    img += pool[..., None] * 70
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(out)
    for k in range(-10, 11):  # perspective floor grid
        d.line([(540 + k * 40, FLOOR_Y - 40), (540 + k * 260, H)], fill=(255, 255, 255, 28), width=2)
    for k in range(6):
        y = FLOOR_Y - 40 + (k ** 1.7) * 22
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 22), width=2)
    rng = np.random.default_rng(seed)
    for _ in range(60):  # dust in the light
        x, y, r = rng.uniform(0, W), rng.uniform(150, FLOOR_Y - 80), rng.uniform(1.5, 4)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, int(rng.uniform(30, 90))))
    return np.asarray(out.convert("RGB"))


# ---------------------------------------------------------------- game UI
def stroked(text, size, fill, stroke=INK, sw=10, font=None):
    f = font or F_ANTON(size)
    w_, h_, b = text_size(f, text)
    pad = sw + 20
    img = Image.new("RGBA", (w_ + pad * 2, h_ + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((pad - b[0], pad - b[1]), text, font=f, fill=fill + (255,), stroke_width=sw,
                             stroke_fill=stroke + (255,))
    return img


def skew(img, k=-0.22):
    w, h = img.size
    extra = int(abs(k) * h)
    return img.transform((w + extra, h), Image.AFFINE, (1, k, -extra if k < 0 else 0, 0, 1, 0), Image.BICUBIC)


def banner(text, size, fill, sw=12):
    img = skew(stroked(text, size, fill, sw=sw))
    glow = img.filter(ImageFilter.GaussianBlur(18))
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.alpha_composite(glow)
    out.alpha_composite(img)
    return out


def spark(size, col=GOLD, n=14, seed=0):
    rng = np.random.default_rng(seed)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = size / 2
    pts = []
    for i in range(n * 2):
        a = i / (n * 2) * 2 * math.pi
        r = c * (0.95 if i % 2 == 0 else 0.45) * rng.uniform(0.8, 1.0)
        pts.append((c + r * math.cos(a), c + r * math.sin(a)))
    d.polygon(pts, fill=col + (255,), outline=RED + (255,), width=6)
    inner = [(c + (x - c) * 0.5, c + (y - c) * 0.5) for x, y in pts]
    d.polygon(inner, fill=WHITE + (255,))
    return img


def megaphone(size, col=RED):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    d.polygon([(s * .15, s * .4), (s * .35, s * .4), (s * .8, s * .15), (s * .8, s * .85), (s * .35, s * .6),
               (s * .15, s * .6)], fill=col + (255,), outline=WHITE + (255,), width=5)
    d.rectangle([s * .25, s * .6, s * .35, s * .8], fill=col + (255,), outline=WHITE + (255,), width=4)
    for k in (0.1, 0.2):
        d.arc([s * (.8 - k), s * (.5 - k * 2.2), s * (.95 + k), s * (.5 + k * 2.2)], -40, 40, fill=WHITE + (255,), width=5)
    return img


def icon_disc(icon, size, ring):
    out = Image.new("RGBA", (size + 16, size + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    d.ellipse([0, 0, size + 15, size + 15], fill=ring + (255,))
    d.ellipse([8, 8, size + 7, size + 7], fill=(30, 30, 45, 255))
    out.alpha_composite(icon.resize((int(size * 0.8), int(size * 0.8))), (int(size * 0.1) + 8, int(size * 0.1) + 8))
    return out


P_IKLAN = icon_disc(megaphone(200), 120, RED)
P_TESTI = portrait("cu_thumbs", 120, BLUE)


def hp_bar(c, t, val_l, val_r, alpha):
    if alpha <= 0:
        return
    lay = Image.new("RGBA", (W, 260), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    bw, y = 330, 70
    for side, val, col, name in [(0, val_l, RED, "IKLAN"), (1, val_r, BLUE, "TESTIMONI")]:
        x0 = 165 if side == 0 else W - 165 - bw
        d.polygon([(x0 - 8, y - 8), (x0 + bw + 8, y - 8), (x0 + bw - 4, y + 52), (x0 - 20, y + 52)], fill=INK + (255,))
        d.rectangle([x0, y, x0 + bw, y + 40], fill=(70, 20, 20, 255) if side == 0 else (20, 40, 70, 255))
        fill_w = bw * clamp(val / 100)
        if side == 0:
            d.rectangle([x0 + bw - fill_w, y, x0 + bw, y + 40], fill=GOLD + (255,) if val > 30 else RED + (255,))
        else:
            d.rectangle([x0, y, x0 + fill_w, y + 40], fill=GOLD + (255,))
        f = F_ANTON(44)
        tx = x0 if side == 0 else x0 + bw - f.getlength(name)
        d.text((tx, y + 52), name, font=f, fill=WHITE, stroke_width=5, stroke_fill=INK)
    lay.alpha_composite(P_IKLAN, (14, 20))
    lay.alpha_composite(P_TESTI, (W - 150, 20))
    timer = max(0, 99 - int(t - 4.3))
    f = F_ANTON(80)
    s = f"{timer:02d}"
    d.text((W / 2 - f.getlength(s) / 2, 38), s, font=f, fill=WHITE, stroke_width=7, stroke_fill=INK)
    if alpha < 1:
        lay.putalpha(lay.split()[3].point(lambda v: int(v * alpha)))
    c.alpha_composite(lay, (0, 0))


def hp_values(t):
    """IKLAN loses health on each testimonial hit; TESTIMONI never gets touched."""
    left = 100.0
    for at, to in [(13.05, 60), (16.8, 45), (17.75, 30), (18.8, 15), (34.55, 0)]:
        if t >= at:
            left = to + (left - to) * (1 - ease_out((t - at) / 0.45))
    return left, 100.0


def speech(text, w=600, col=WHITE, tail="left", size=54):
    f = kr.font("InterXB", size)
    lines = kr.wrap(text, f, w - 60) if hasattr(kr, "wrap") else [text]
    asc, desc = f.getmetrics()
    lh = asc + desc + 4
    h = lh * len(lines) + 50
    img = Image.new("RGBA", (w, h + 50), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h], radius=36, fill=col + (255,), outline=INK + (255,), width=6)
    tx = 80 if tail == "left" else w - 120
    d.polygon([(tx, h - 4), (tx + 40, h - 4), (tx + (-10 if tail == "left" else 60), h + 46)], fill=col + (255,),
              outline=INK + (255,))
    d.rectangle([tx + 4, h - 10, tx + 36, h - 2], fill=col + (255,))
    for i, l in enumerate(lines):
        d.text(((w - f.getlength(l)) / 2, 25 + i * lh), l, font=f, fill=INK)
    return kr.with_shadow(img, offset=(0, 10), blur=12, alpha=0.5)


def wrap(text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if f.getlength(t) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    lines.append(cur)
    return lines


kr.wrap = wrap


def combo_card(title, art, col):
    w, h = 420, 300
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=24, fill=(25, 25, 40, 245), outline=col + (255,), width=6)
    img.alpha_composite(art, ((w - art.width) // 2, 22))
    f = F_ANTON(46)
    d.text(((w - f.getlength(title)) / 2, h - 70), title, font=f, fill=WHITE)
    d.ellipse([w - 70, 14, w - 16, 68], fill=GREEN + (255,))
    d.line([(w - 58, 42), (w - 46, 54), (w - 26, 28)], fill=WHITE, width=7)
    return kr.with_shadow(img, offset=(0, 10), blur=14, alpha=0.6)


def wave_art(w=300, h=180):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i in range(24):
        x = 20 + i * 11.5
        a = (0.25 + 0.75 * abs(math.sin(i * 0.9) * math.cos(i * 0.37))) * h * 0.42
        d.rounded_rectangle([x, h / 2 - a, x + 6, h / 2 + a], radius=3, fill=BLUE + (255,))
    return img


def skill_card(num, text, col):
    f = F_ANTON(62)
    w = int(f.getlength(text)) + 200
    h = 130
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(30, 0), (w - 1, 0), (w - 31, h - 1), (0, h - 1)], fill=(25, 25, 40, 245), outline=col + (255,))
    d.ellipse([28, 18, 122, 112], fill=col + (255,), outline=WHITE + (255,), width=5)
    fn = F_ANTON(58)
    d.text((75 - fn.getlength(num) / 2, 24), num, font=fn, fill=INK)
    d.text((148, 26), text, font=f, fill=WHITE)
    return kr.with_shadow(img, offset=(0, 10), blur=12, alpha=0.6)


def parcel(size=230):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    d.polygon([(s * .1, s * .35), (s * .5, s * .15), (s * .9, s * .35), (s * .9, s * .8), (s * .5, s), (s * .1, s * .8)],
              fill=(205, 160, 100, 255), outline=INK + (255,), width=6)
    d.line([(s * .1, s * .35), (s * .5, s * .55), (s * .9, s * .35)], fill=INK, width=6)
    d.line([(s * .5, s * .55), (s * .5, s)], fill=INK, width=6)
    d.ellipse([s * .62, s * .02, s * .98, s * .38], fill=GREEN + (255,), outline=WHITE + (255,), width=5)
    d.line([(s * .7, s * .2), (s * .78, s * .28), (s * .92, s * .1)], fill=WHITE, width=8)
    return img


def rec_timer(sec):
    w, h = 460, 140
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=30, fill=(20, 20, 30, 235), outline=RED + (255,), width=5)
    d.ellipse([30, 42, 86, 98], fill=RED)
    d.text((104, 22), f"00:{sec:02d}", font=F_ANTON(90), fill=WHITE)
    return kr.with_shadow(img, offset=(0, 10), blur=12, alpha=0.6)


def star(size, col=GOLD):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    c = size / 2
    pts = [(c + (c if i % 2 == 0 else c * 0.45) * math.cos(-math.pi / 2 + i * math.pi / 5),
            c + (c if i % 2 == 0 else c * 0.45) * math.sin(-math.pi / 2 + i * math.pi / 5)) for i in range(10)]
    ImageDraw.Draw(img).polygon(pts, fill=col + (255,), outline=INK + (255,))
    return img


def review(user, text):
    w, h = 520, 150
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=26, fill=WHITE + (255,), outline=INK + (255,), width=4)
    for k in range(5):
        img.alpha_composite(star(38), (22 + k * 42, 18))
    d.text((250, 22), user, font=F_CAP(28), fill=(120, 120, 130))
    d.text((24, 74), text, font=kr.font("InterXB", 44), fill=INK)
    return kr.with_shadow(img, offset=(0, 10), blur=12, alpha=0.6)


def select_card(title, art, col, glow):
    w, h = 400, 520
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], fill=(22, 22, 36, 255), outline=col + (255,), width=8 if glow else 4)
    img.alpha_composite(art, ((w - art.width) // 2, 30))
    f = F_ANTON(70)
    d.text(((w - f.getlength(title)) / 2, h - 110), title, font=f, fill=col)
    out = kr.with_shadow(img, offset=(0, 12), blur=16, alpha=0.6)
    if glow:
        g = Image.new("RGBA", out.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).rectangle([30, 30, out.width - 30, out.height - 30], outline=col + (255,), width=26)
        g = g.filter(ImageFilter.GaussianBlur(18))
        g.alpha_composite(out)
        out = g
    return out


ART_IKLAN = megaphone(330)
ART_TESTI = photo_card("cu_thumbs", 320, 330, BLUE)
U = {
    "vs": banner("VS", 300, GOLD, sw=16),
    "r1": banner("ROUND 1", 170, WHITE),
    "fight": banner("FIGHT!", 200, GOLD),
    "miss": banner("MISS!", 140, (170, 170, 180)),
    "hit": banner("HIT!", 150, GOLD),
    "special": banner("SPECIAL MOVE", 110, BLUE),
    "special2": banner("TESTIMONI VIDEO", 96, WHITE),
    "howto": banner("CARANYA SENANG", 110, GREEN),
    "skills": banner("3 SOALAN SAKTI", 120, GOLD),
    "final": banner("FINAL ROUND", 160, RED),
    "ko": banner("K.O.!", 330, RED, sw=18),
    "win": banner("TESTIMONI MENANG!", 96, GOLD),
    "spark": [spark(360, seed=i) for i in range(4)],
    "brag": speech("Produk saya TERBAIK!!", 560, tail="left"),
    "zzz": stroked("z z Z", 90, (200, 200, 220), sw=8),
    "best": speech("Barang ni memang BEST!", 600, (220, 240, 255), tail="right"),
    "cards": [combo_card("MUKA SEBENAR", photo_card("cu_biskut", 240, 180, BLUE), BLUE),
              combo_card("SUARA SEBENAR", wave_art(), BLUE),
              combo_card("PENGALAMAN SEBENAR", photo_card("cu_kopi", 240, 180, BLUE), BLUE)],
    "parcel": parcel(),
    "parcel_lbl": stroked("BARANG SAMPAI", 64, WHITE, sw=8),
    "q": [skill_card("1", "MASALAH SEBELUM NI?", GOLD), skill_card("2", "KENAPA PILIH KITA?", BLUE),
          skill_card("3", "HASILNYA SEKARANG?", GREEN)],
    "one": stroked("1 TESTIMONI", 90, BLUE, sw=10),
    "ten": stroked("10 IKLAN", 90, RED, sw=10),
    "mega_s": megaphone(110),
    "cta_top": banner("MULAI HARI INI", 110, GOLD),
    "cta": None,
    "reviews": [review("@kak_ros", "Puas hati sangat!"), review("@zul.ukir", "Kualiti terbaik!"),
                review("@nina_hadiah", "Dah repeat order!")],
}


def cta_card():
    w, h = 960, 330
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=30, fill=WHITE + (255,), outline=INK + (255,), width=6)
    f = F_ANTON(110)
    for i, (s, col) in enumerate([("KUMPUL TESTIMONI", INK), ("VIDEO.", RED)]):
        d.text(((w - f.getlength(s)) / 2, 20 + i * 150), s, font=f, fill=col)
    return kr.with_shadow(img, offset=(0, 12), blur=16, alpha=0.6)


U["cta"] = cta_card()

# ---------------------------------------------------------------- timeline
CUTS = [4.2, 9.3, 14.3, 20.1, 24.9, 31.2, 35.9]
ARENAS = {0.0: arena((120, 40, 160), 1), 4.2: arena((170, 40, 40), 2), 9.3: arena((40, 90, 190), 3),
          14.3: arena((40, 110, 200), 4), 20.1: arena((30, 130, 90), 5), 24.9: arena((170, 130, 30), 6),
          31.2: arena((180, 30, 30), 7), 35.9: arena((120, 60, 170), 8)}
HITS = [3.3, 13.05, 16.8, 17.75, 18.8, 34.55]  # screen shake + flash
GRAIN = [cv2.resize(np.random.default_rng(i).normal(0, 6, (H // 2, W // 2)).astype(np.float32), (W, H),
                    interpolation=cv2.INTER_NEAREST) for i in range(6)]


def scene_start(t):
    return max([0.0] + [c for c in CUTS if c <= t])


CAPS = [
    (0.05, 1.7, "Siapa lebih DIPERCAYAI?", 1.45),
    (1.75, 4.2, "Anda... atau PELANGGAN anda?", 3.85),
    (4.3, 7.15, "Bila anda puji produk sendiri, orang fikir,", 6.98),
    (7.15, 9.3, "memang lah, dia NAK JUAL.", 9.04),
    (9.4, 11.3, "Tapi bila pelanggan sendiri cakap,", 11.18),
    (11.3, 12.95, "\"barang ni memang BEST\",", 12.77),
    (12.95, 14.3, "orang terus PERCAYA.", 14.01),
    (14.45, 16.65, "Itulah kuasa TESTIMONI VIDEO.", 16.36),
    (16.7, 18.72, "Muka sebenar, suara sebenar,", 18.63),
    (18.72, 20.1, "PENGALAMAN SEBENAR.", 19.82),
    (20.25, 21.4, "Caranya senang.", 21.14),
    (21.45, 24.9, "Lepas pelanggan terima barang, minta dia rakam LIMA BELAS SAAT.", 24.67),
    (25.0, 26.4, "Tanya TIGA SOALAN.", 26.08),
    (26.45, 28.1, "Apa masalah sebelum ni?", 27.79),
    (28.1, 29.6, "Kenapa pilih kita?", 29.27),
    (29.6, 31.2, "Apa hasilnya sekarang?", 30.84),
    (31.35, 35.9, "Satu testimoni video, boleh jadi lebih meyakinkan dari SEPULUH IKLAN.", 35.57),
    (35.95, 39.2, "Jadi mulai hari ini, kumpul TESTIMONI VIDEO.", 38.95),
    (39.2, DUR, "Biar pelanggan anda yang JUAL untuk anda.", 41.64),
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


def draw_caption(c, t, y=1700):
    for s, e, words, times in CAP_DATA:
        if not (s - 0.02 <= t < e):
            continue
        f = kr.font("InterXB", 66)
        space = f.getlength(" ")
        lines, cur, cw = [], [], 0
        for w_ in words:
            wl = f.getlength(w_)
            if cur and cw + space + wl > 940:
                lines.append(cur)
                cur, cw = [], 0
            cur.append(w_)
            cw += (space if cw else 0) + wl
        lines.append(cur)
        asc, desc = f.getmetrics()
        lh = asc + desc + 8
        widths = [sum(f.getlength(w_) for w_ in l) + space * (len(l) - 1) for l in lines]
        bw, bh = int(max(widths)) + 60, lh * len(lines) + 30
        strip = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        d = ImageDraw.Draw(strip)
        active = max([i for i, tt in enumerate(times) if tt <= t], default=-1)
        idx = 0
        for li, l in enumerate(lines):
            x = (bw - widths[li]) / 2
            y0 = 14 + li * lh
            for w_ in l:
                wl = f.getlength(w_)
                if t >= times[idx]:
                    k = ease_back((t - times[idx]) / 0.16)
                    col = GOLD if is_key(w_) else ((120, 210, 255) if idx == active else WHITE)
                    d.text((x, y0 + 16 * (1 - k)), w_, font=f, fill=col, stroke_width=9, stroke_fill=INK)
                x += wl + space
                idx += 1
        k = ease_out((t - s + 0.02) / 0.18)
        place(c, strip, W / 2, y + 24 * (1 - k), alpha=k * clamp((e - t) / 0.1))


def slam(c, spr, t, t0, cx, cy, rot=0.0, t1=None, big=2.0):
    if t < t0 or (t1 is not None and t > t1 + 0.2):
        return
    k = clamp((t - t0) / 0.14)
    a = k * (1 - clamp((t - t1) / 0.2) if t1 is not None and t > t1 else 1)
    place(c, spr, cx, cy, scale=big - (big - 1) * ease_out(k), rot=rot, alpha=a)


def hit_fx(c, t, t0, cx, cy, j=0):
    if t0 <= t < t0 + 0.4:
        u = (t - t0) / 0.4
        place(c, U["spark"][j % 4], cx, cy, scale=0.5 + 0.8 * ease_out(u), rot=u * 40, alpha=1 - u ** 2)


def speed_lines(c, t, col=(255, 255, 255), alpha=60):
    d = ImageDraw.Draw(c)
    rng = np.random.default_rng(int(t * 12))
    for _ in range(26):
        a = rng.uniform(0, 2 * math.pi)
        r0, r1 = rng.uniform(420, 600), rng.uniform(900, 1300)
        cx, cy = W / 2, 820
        d.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))],
               fill=col + (alpha,), width=int(rng.uniform(3, 9)))


# ---------------------------------------------------------------- scenes
def world(t):
    s0 = scene_start(t)
    c = Image.fromarray(ARENAS[s0]).convert("RGBA")

    if s0 == 0.0:  # character select
        if t >= 3.3:
            speed_lines(c, t, GOLD, 70)
        for side, (art, title, col, t0, glow_t) in enumerate([(ART_IKLAN, "IKLAN", RED, 0.3, 1.88),
                                                              (ART_TESTI, "TESTIMONI", BLUE, 0.55, 2.8)]):
            if t < t0:
                continue
            glow = t >= glow_t
            k = ease_out((t - t0) / 0.4)
            x = (290 if side == 0 else 790) + (-500 if side == 0 else 500) * (1 - k)
            place(c, select_card(title, art, col, glow), x, 470, rot=-4 if side == 0 else 4,
                  scale=0.82 * (1.06 if glow and ((t - glow_t) < 0.2) else 1.0))
        slam(c, U["vs"], t, 3.3, 540, 470, rot=-6, big=2.6)
        draw_fighter(c, t, "terangkan", 0.05, 540, scale=0.74)
    elif s0 == 4.2:  # round 1: self-praise misses
        if t < 5.6:
            slam(c, U["r1"], t, 4.3, 540, 560, t1=4.85)
            slam(c, U["fight"], t, 4.95, 540, 560, rot=-4, t1=5.5)
        draw_fighter(c, t, "thumbs_produk", 4.45, 330, scale=0.95, t1=9.25)
        kr.pop(c, U["brag"], t, 5.6, 610, 640, rot=-3)
        if t >= 5.8:  # megaphone shouting
            for k in range(3):
                r = ((t - 5.8) * 1.4 + k / 3) % 1
                d = ImageDraw.Draw(c)
                d.arc([600 - 200 * r, 900 - 200 * r, 600 + 200 * r, 900 + 200 * r], -40, 40,
                      fill=RED + (int(255 * (1 - r)),), width=10)
        draw_fighter(c, t, "menguap", 7.26, 800, scale=0.85, flip=True)
        if t >= 7.6:
            place(c, U["zzz"], 880 + 20 * math.sin(t * 3), 760 - 20 * ((t - 7.6) % 1), alpha=0.9)
        slam(c, U["miss"], t, 8.2, 540, 440, rot=-6)
    elif s0 == 9.3:  # testimonial strikes
        pose = "tengok_barang" if t < 13.0 else "terkejut_meja"
        draw_fighter(c, t, pose, 9.45 if t < 13.0 else 13.0, 640, scale=0.95, rise=500 if t < 13.0 else 0)
        kr.pop(c, U["best"], t, 11.4, 540, 420, rot=3)
        if t >= 13.05:
            hit_fx(c, t, 13.05, 250, 860, 0)
            slam(c, U["hit"], t, 13.05, 250, 860, rot=-8)
            dmg = stroked("-40", 120, RED, sw=10)
            place(c, dmg, 220, 1080 - 120 * ease_out((t - 13.1) / 0.8), alpha=clamp(1.6 - (t - 13.1)))
    elif s0 == 14.3:  # special move combo
        draw_fighter(c, t, "biskut", 14.45, 300, scale=0.9)
        slam(c, U["special"], t, 14.5, 600, 360, rot=-4, t1=16.6)
        slam(c, U["special2"], t, 14.9, 640, 500, rot=-4, t1=16.6)
        for j, (tt, (x, y)) in enumerate(zip([16.8, 17.75, 18.8], [(780, 520), (760, 860), (780, 1200)])):
            if t >= tt:
                kr.pop(c, U["cards"][j], t, tt, x, y, rot=(4, -3, 3)[j])
                hit_fx(c, t, tt, x - 200, y - 100, j + 1)
        n = (t >= 16.8) + (t >= 17.75) + (t >= 18.8)
        if n:
            place(c, banner(f"COMBO x{n}", 110, GOLD), 300, 330, rot=-6,
                  scale=1 + 0.25 * (1 - ease_out((t - [16.8, 17.75, 18.8][n - 1]) / 0.25)))
    elif s0 == 20.1:  # how to
        slam(c, U["howto"], t, 20.3, 540, 330, rot=-4)
        pose = "telefon" if t < 23.4 else "jam"
        draw_fighter(c, t, pose, 21.5 if t < 23.4 else 23.4, 320, scale=0.92, rise=500 if t < 23.4 else 0)
        if t >= 21.6:
            kr.pop(c, U["parcel"], t, 21.6, 790, 700, rot=-5)
            kr.pop(c, U["parcel_lbl"], t, 21.9, 790, 870, rot=-3)
        if t >= 23.5:
            sec = max(0, 15 - int((t - 23.6) * 10))
            kr.pop(c, rec_timer(sec), t, 23.5, 780, 1080, rot=3)
    elif s0 == 24.9:  # three questions
        slam(c, U["skills"], t, 25.05, 540, 330, rot=-4)
        draw_fighter(c, t, "fikir", 25.0, 250, scale=0.86)
        for j, tt in enumerate([26.53, 28.2, 29.69]):
            kr.slide(c, U["q"][j], t, tt, 660, 600 + j * 200, rot=-2, dx=600)
    elif s0 == 31.2:  # final round -> K.O.
        if t < 34.55:
            slam(c, U["final"], t, 31.35, 540, 330, rot=-4, t1=32.6)
            if t >= 32.4:
                kr.pop(c, U["ten"], t, 32.4, 290, 520, rot=-4)
                for k in range(10):
                    kr.pop(c, U["mega_s"], t, 32.6 + k * 0.08, 90 + (k % 5) * 100, 680 + (k // 5) * 110)
                kr.pop(c, U["one"], t, 33.4, 800, 520, rot=4)
                place(c, ART_TESTI, 800, 800, scale=0.9 * ease_back((t - 33.5) / 0.35) if t >= 33.5 else 0.01)
            draw_fighter(c, t, "terangkan", 31.3, 540, scale=0.8)
        else:
            speed_lines(c, t, RED, 90)
            draw_fighter(c, t, "menang", 34.6, 540, scale=1.0, rise=200)
            slam(c, U["ko"], t, 34.55, 540, 560, rot=-8, big=3.0)
            slam(c, U["win"], t, 35.2, 540, 820, rot=-4)
    else:  # CTA
        pose = "ukur_kayu" if t < 39.25 else "kopi"
        draw_fighter(c, t, pose, 36.0 if t < 39.25 else 39.25, 540, scale=0.9, rise=500 if t < 39.25 else 0)
        slam(c, U["cta_top"], t, 36.05, 540, 220, rot=-4)
        kr.pop(c, U["cta"], t, 36.9, 540, 470, rot=-2)
        for j, (tt, (x, y)) in enumerate(zip([39.4, 39.9, 40.4], [(270, 1000), (810, 1120), (270, 1240)])):
            kr.pop(c, U["reviews"][j], t, tt, x, y, rot=(-4, 3, -2)[j])
        if t >= 41.5:
            pulse = 1 + 0.04 * max(0.0, math.sin((t - 41.5) * 7))
            kr.pop(c, kr.A["follow"], t, 41.5, 540, 1440, scale=pulse)
    return c


def frame(i):
    t = i / FPS
    c = world(t)
    s0 = scene_start(t)
    if 4.3 <= t < 35.9:
        hp_bar(c, t, *hp_values(t), alpha=clamp((t - 4.3) / 0.3))
    arr = np.asarray(c.convert("RGB"))
    # camera: cut punch-in + shake on hits
    z, sx, sy = 1.0, 0.0, 0.0
    if t - s0 < 0.25 and s0 > 0:
        z = 1.12 - 0.12 * ease_out((t - s0) / 0.25)
    for hh in HITS:
        dt = t - hh
        if 0 <= dt < 0.45:
            env = math.exp(-dt * 8)
            sx += 22 * env * math.sin(dt * 90)
            sy += 16 * env * math.cos(dt * 70)
            z *= 1 + 0.06 * env
    if z != 1.0 or sx or sy:
        M = np.float32([[z, 0, W / 2 - z * W / 2 + sx], [0, z, H * 0.45 - z * H * 0.45 + sy]])
        arr = cv2.warpAffine(arr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    arr = arr.astype(np.float32) + GRAIN[i % len(GRAIN)][..., None] * 0.5
    # white flash at cuts and hits
    fl = 0.0
    for ft in CUTS + HITS:
        dt = t - ft
        if 0 <= dt < 0.15:
            fl = max(fl, (0.9 if ft in (3.3, 34.55) else 0.55) * (1 - dt / 0.15))
    if fl:
        arr = arr * (1 - fl) + 255 * fl
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    draw_caption(out, t)
    rgb = np.asarray(out.convert("RGB"))
    if t > DUR - 0.35:
        rgb = (rgb.astype(np.float32) * clamp((DUR - t) / 0.35)).astype(np.uint8)
    return rgb


if __name__ == "__main__":
    if len(sys.argv) > 2:
        for ts in sys.argv[2:]:
            Image.fromarray(frame(int(float(ts) * FPS))).save(f"{WD}/k9_{ts}.jpg", quality=85)
    else:
        out = sys.stdout.buffer
        for i in range(N):
            out.write(frame(i).tobytes())
            if i % 100 == 0:
                print(f"frame {i}/{N}", file=sys.stderr, flush=True)
