"""Episode — "Muka Anda Ialah Brand Anda" (~44.5 s, 1080x1920@30), MAGAZINE concept.

The presenter is the cover model of a business magazine ("NIAGA"). Cover lines land on the
VO, then pages turn (3D page-curl warp with fold shadow) to editorial spreads: pull quote,
"duta produk" feature, 3-step feature with framed photos, lifestyle column, KENAL → PERCAYA → BELI
infographic, and a closing cover with the CTA. Black & white cut-outs, serif typography.

Usage: python3 majalah_render.py <workdir> [t1 t2 ...]   (needs fb/ poses + kolaj_render assets)
"""
import math
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import kolaj_render as kr
from kolaj_render import F_ANTON, F_SERIF, FPS, H, W, clamp, ease_back, ease_inout, ease_out, place, text_size

WD = sys.argv[1]
DUR = 44.5
N = int(DUR * FPS)

PAPER = (246, 241, 232)
INK = (18, 18, 20)
RED = (205, 30, 40)
GREY = (120, 116, 110)
WHITE = (255, 255, 255)
F_IT = lambda s: kr.font("Playfair", s)  # variable font; italic not bundled, so use weight/size for contrast
F_SANS = lambda s: kr.font("InterXB", s)
F_SANS_B = lambda s: kr.font("InterB", s)


# ---------------------------------------------------------------- cut-outs
def clean_mask(m):
    b = (m > 0.5).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(b)
    if n > 2:
        m = m * (lab == 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA])))
    return m


def figure(name, up=2.2, outline=True):
    im = Image.open(f"{WD}/fb/{name}.jpg").convert("RGB")
    mk = Image.open(f"{WD}/fb/{name}_mask.png").convert("L")
    w, h = int(im.width * up), int(im.height * up)
    src = np.asarray(im.resize((w, h), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 80, 2))).astype(np.float32)
    m = np.asarray(mk.resize((w, h), Image.LANCZOS)).astype(np.float32) / 255
    m = clean_mask(np.clip((m - 0.25) / 0.5, 0, 1))
    ys, xs = np.where(m > 0.5)
    src, m = src[ys.min():ys.max() + 1, xs.min():xs.max() + 1], m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    s = kr.bw_dramatic(src)
    pad = 24
    mp = cv2.copyMakeBorder(m, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    sp = cv2.copyMakeBorder(s, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    a = mp
    if outline:
        a = cv2.GaussianBlur(cv2.dilate(mp, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13))), (0, 0), 1.0)
    rgb = sp * mp[..., None] + 255 * (1 - mp[..., None])
    return Image.fromarray(np.dstack([rgb, a * 255]).clip(0, 255).astype(np.uint8), "RGBA")


FIG = {p: figure(p, outline=False) for p in ["terangkan", "menang"]}
FIG.update({p: figure(p) for p in ["thumbs_produk", "fikir"]})


def photo(name, w, h, top=0.0, bw=True):
    """Crop a pose/close-up photo to w x h (anchored near the top) as a print."""
    im = Image.open(f"{WD}/fb/{name}.jpg").convert("RGB")
    r = w / h
    if im.width / im.height > r:
        nw = int(im.height * r)
        im = im.crop(((im.width - nw) // 2, 0, (im.width - nw) // 2 + nw, im.height))
    else:
        nh = int(im.width / r)
        y0 = int((im.height - nh) * top)
        im = im.crop((0, y0, im.width, y0 + nh))
    arr = np.asarray(im.resize((w, h), Image.LANCZOS)).astype(np.float32)
    return Image.fromarray((kr.bw_dramatic(arr) if bw else arr).astype(np.uint8)).convert("RGBA")


def framed(img, border=14, col=WHITE, cap=None):
    w, h = img.size
    extra = 70 if cap else 0
    out = Image.new("RGBA", (w + border * 2, h + border * 2 + extra), col + (255,))
    out.paste(img, (border, border))
    if cap:
        d = ImageDraw.Draw(out)
        f = F_SANS_B(28)
        d.text((border, h + border + 18), cap, font=f, fill=GREY)
    return kr.with_shadow(out, offset=(8, 14), blur=14, alpha=0.35)


# ---------------------------------------------------------------- page furniture
def paper_page(seed):
    rng = np.random.default_rng(seed)
    bg = np.ones((H, W, 3), np.float32) * np.array(PAPER, np.float32)
    fine = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.7)
    bg += fine[..., None] * 3
    # gutter shading on the left (spine)
    xx = np.linspace(0, 1, W)[None, :, None]
    bg *= 1 - 0.18 * np.exp(-xx * 18)
    return np.clip(bg, 0, 255).astype(np.uint8)


def studio_bg(top, bot):
    yy = np.linspace(0, 1, H)[:, None, None]
    xx = np.linspace(-1, 1, W)[None, :, None]
    g = np.array(top, np.float32) * (1 - yy) + np.array(bot, np.float32) * yy
    g = g * (1 - 0.25 * (xx ** 2)) + 30 * np.exp(-((xx * 1.2) ** 2 + ((yy - 0.45) * 2.2) ** 2))
    return np.clip(g * np.ones((1, W, 1)), 0, 255).astype(np.uint8)


def header(d, section, page):
    f = F_SANS_B(30)
    d.text((70, 60), "NIAGA", font=F_SERIF(46), fill=RED)
    d.text((240, 72), f"|  {section}", font=f, fill=GREY)
    d.line([(70, 128), (W - 70, 128)], fill=INK, width=3)
    d.line([(70, H - 120), (W - 70, H - 120)], fill=(200, 195, 185), width=2)
    d.text((W - 70 - f.getlength(str(page)), H - 105), str(page), font=f, fill=GREY)
    d.text((70, H - 105), "EDISI KHAS · OKTOBER 2026", font=F_SANS_B(24), fill=GREY)


def text_img(text, font, col, maxw=None, lh_extra=6, align="left"):
    lines = kr.wrap(text, font, maxw) if maxw else [text]
    asc, desc = font.getmetrics()
    lh = asc + desc + lh_extra
    w = int(max(font.getlength(l) for l in lines)) + 10
    img = Image.new("RGBA", (w, lh * len(lines) + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, l in enumerate(lines):
        x = (w - font.getlength(l)) / 2 if align == "center" else 0
        d.text((x, i * lh), l, font=font, fill=col + (255,))
    return img


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


def barcode(w=220, h=130):
    rng = np.random.default_rng(5)
    img = Image.new("RGBA", (w + 20, h + 50), WHITE + (255,))
    d = ImageDraw.Draw(img)
    x = 10
    while x < w:
        bw = int(rng.choice([2, 3, 5]))
        d.rectangle([x, 10, x + bw - 1, h], fill=INK)
        x += bw + int(rng.choice([2, 3, 4]))
    d.text((14, h + 8), "9 771234 567003", font=F_SANS_B(24), fill=INK)
    return img


def reveal(c, spr, t, t0, cx, cy, mode="up", dur=0.45, rot=0.0):
    """Editorial entrance: wipe-in from a direction (clip mask) + slight drift."""
    if t < t0:
        return
    u = ease_out((t - t0) / dur)
    w, h = spr.size
    s = spr.copy()
    mk = Image.new("L", (w, h), 0)
    dm = ImageDraw.Draw(mk)
    if mode == "up":
        dm.rectangle([0, h * (1 - u), w, h], fill=255)
    elif mode == "left":
        dm.rectangle([0, 0, w * u, h], fill=255)
    else:
        dm.rectangle([w * (1 - u), 0, w, h], fill=255)
    s.putalpha(Image.fromarray(np.minimum(np.asarray(s.split()[3]), np.asarray(mk))))
    dy = 30 * (1 - u) if mode == "up" else 0
    place(c, s, cx, cy + dy, rot=rot)


def underline(c, t, t0, x0, x1, y, col=RED, width=8, dur=0.35):
    if t < t0:
        return
    k = ease_out((t - t0) / dur)
    ImageDraw.Draw(c).line([(x0, y), (x0 + (x1 - x0) * k, y)], fill=col + (255,), width=width)


def strike(c, t, t0, x0, x1, y, col=RED, width=12, dur=0.3):
    underline(c, t, t0, x0, x1, y, col, width, dur)


# ---------------------------------------------------------------- static layers
BG_COVER = studio_bg((226, 222, 214), (168, 162, 154))
BG_BACK = studio_bg((60, 20, 24), (14, 10, 12))
PAGES = {k: paper_page(k) for k in range(1, 6)}

A = {
    "mast": text_img("NIAGA", F_SERIF(250), RED),
    "issue": text_img("EDISI KHAS  ·  OKTOBER 2026  ·  RM9.90", F_SANS_B(30), INK),
    "cl1": None,
    "cl_big1": text_img("MUKA", F_ANTON(230), WHITE),
    "cl_big2": text_img("ANDA", F_ANTON(230), RED),
    "cl_sub": text_img("= BRAND ANDA", F_SANS(64), WHITE),
    "barcode": barcode(),
    "quote": text_img("“Orang beli dari orang.”", F_SERIF(120), INK, maxw=920, align="center"),
    "q_by": text_img("— prinsip asas jualan", F_SANS_B(34), GREY),
    "dek": text_img("Bila owner sendiri tampil, bisnes ada:", F_SANS_B(40), GREY, maxw=400),
    "trio": [text_img(s, F_SERIF(110), RED if i == 1 else INK) for i, s in enumerate(["wajah.", "suara.", "cerita."])],
    "h_duta": text_img("Duta Produk Terbaik", F_SERIF(104), INK, maxw=900),
    "kicker_duta": text_img("FEATURE", F_SANS(30), RED),
    "celeb_tag": text_img("BAYARAN DUTA SELEBRITI", F_SANS_B(30), GREY),
    "celeb_price": text_img("RM $$$$$", F_ANTON(110), INK),
    "anda_q": text_img("Anda?", F_SERIF(170), RED),
    "duta_lbl": text_img("Duta paling sesuai:", F_SANS_B(40), GREY),
    "sash": None,
    "h_3": text_img("3 Perkara Untuk Mula", F_SERIF(96), INK, maxw=940),
    "kicker_3": text_img("PANDUAN", F_SANS(30), RED),
    "h_gaya": text_img("Tak perlu jadi", F_SERIF(96), INK),
    "selebriti": text_img("selebriti.", F_SERIF(150), INK),
    "diri": text_img("Cukup jadi diri sendiri.", F_SERIF(84), RED, maxw=640),
    "konsisten": text_img("SECARA KONSISTEN", F_SANS(44), INK),
    "kicker_gaya": text_img("GAYA HIDUP", F_SANS(30), RED),
    "h_info": text_img("Kenapa ia berkesan", F_SERIF(92), INK, maxw=900),
    "kicker_info": text_img("INFOGRAFIK", F_SANS(30), RED),
    "back_big1": text_img("MUKA DEPAN", F_ANTON(170), WHITE),
    "back_big2": text_img("BISNES ANDA:", F_ANTON(110), (240, 200, 200)),
    "back_anda": text_img("ANDA.", F_ANTON(260), RED),
    "next": text_img("EDISI SETERUSNYA →", F_SANS(40), WHITE),
}


def sash(text, w=760, h=130, col=RED):
    img = Image.new("RGBA", (w, h), col + (255,))
    f = F_ANTON(82)
    tw, th, b = text_size(f, text)
    ImageDraw.Draw(img).text(((w - tw) / 2 - b[0], (h - th) / 2 - b[1]), text, font=f, fill=WHITE)
    return kr.with_shadow(img, offset=(6, 10), blur=10, alpha=0.4)


A["sash"] = sash("DIRI ANDA SENDIRI")


def cover_line(text, maxw=360):
    """Cover line set in white on a red block so it reads over the black hoodie."""
    t = text_img(text, F_SANS(44), WHITE, maxw=maxw)
    img = Image.new("RGBA", (t.width + 40, t.height + 24), RED + (255,))
    img.alpha_composite(t, (20, 14))
    return kr.with_shadow(img, offset=(4, 8), blur=8, alpha=0.35)


A["cl1"] = cover_line("Pelanggan tak ingat logo anda.")
STEPS = [("01", "Tunjuk proses kerja anda.", "cu_ukur", 0.0), ("02", "Kongsi tips dalam bidang anda.", "terangkan", 0.0),
         ("03", "Cerita kenapa anda mulakan bisnes ni.", "kopi", 0.0)]
STEP_IMG = [framed(photo(p, 300, 300, top=tp)) for _, _, p, tp in STEPS]
CU_THUMBS = framed(photo("cu_thumbs", 560, 640, top=0.0), cap="Owner yang tampil, bisnes yang dipercayai.")
CU_KOPI = framed(photo("cu_kopi", 520, 620, top=0.0), border=18)
CELEB = None


def celeb_silhouette(w=300, h=560):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([w * .32, 0, w * .68, h * .2], fill=(150, 146, 140, 255))
    d.rounded_rectangle([w * .12, h * .22, w * .88, h * .75], radius=60, fill=(150, 146, 140, 255))
    d.rectangle([w * .26, h * .7, w * .44, h], fill=(150, 146, 140, 255))
    d.rectangle([w * .56, h * .7, w * .74, h], fill=(150, 146, 140, 255))
    f = F_SERIF(120)
    d.text((w / 2 - f.getlength("?") / 2, h * .25), "?", font=f, fill=WHITE)
    return img


CELEB = celeb_silhouette()


def circle_node(text, col, r=150):
    img = Image.new("RGBA", (r * 2 + 20, r * 2 + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([10, 10, r * 2 + 10, r * 2 + 10], fill=col + (255,))
    f = F_ANTON(78)
    tw, th, b = text_size(f, text)
    d.text((r + 10 - tw / 2 - b[0], r + 10 - th / 2 - b[1]), text, font=f, fill=WHITE)
    return kr.with_shadow(img, offset=(6, 12), blur=12, alpha=0.35)


NODES = [circle_node("KENAL", INK), circle_node("PERCAYA", (90, 90, 95)), circle_node("BELI", RED)]

# ---------------------------------------------------------------- timeline
CUTS = [4.3, 11.3, 18.4, 29.3, 34.2, 39.9]
PUNCHES = [3.17, 14.26, 17.01, 30.2, 38.96, 40.66]


def scene_start(t):
    return max([0.0] + [c for c in CUTS if c <= t])


CAPS = [
    (0.05, 2.0, "Pelanggan tak ingat LOGO anda.", 1.67),
    (2.0, 4.3, "Mereka ingat... MUKA ANDA.", 3.99),
    (4.4, 6.2, "Orang beli dari orang.", 5.92),
    (6.2, 11.3, "Bila owner sendiri tampil, bisnes ada WAJAH, ada SUARA, ada CERITA.", 11.0),
    (11.4, 14.1, "Brand besar bayar mahal untuk duta produk.", 13.76),
    (14.15, 14.95, "ANDA?", 14.67),
    (15.0, 18.4, "Dah ada duta paling sesuai. DIRI ANDA SENDIRI.", 18.08),
    (18.5, 20.4, "Mula dengan TIGA perkara.", 20.03),
    (20.4, 23.1, "Satu, tunjuk PROSES KERJA anda.", 22.7),
    (23.1, 26.05, "Dua, kongsi TIPS dalam bidang anda.", 25.57),
    (26.05, 29.3, "Tiga, cerita KENAPA anda mulakan bisnes ni.", 28.97),
    (29.4, 31.2, "Tak perlu jadi SELEBRITI.", 31.0),
    (31.2, 34.2, "Cukup jadi diri sendiri, secara KONSISTEN.", 33.88),
    (34.3, 37.4, "Sebab bila orang KENAL anda, mereka PERCAYA.", 37.08),
    (37.4, 39.9, "Bila mereka percaya, mereka BELI.", 39.56),
    (39.95, DUR, "Jadi, jadilah MUKA DEPAN bisnes anda sendiri.", 42.87),
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


def draw_caption(c, t, y=1715):
    for s, e, words, times in CAP_DATA:
        if not (s - 0.02 <= t < e):
            continue
        f = F_SANS(60)
        space = f.getlength(" ")
        lines, cur, cw = [], [], 0
        for w_ in words:
            wl = f.getlength(w_)
            if cur and cw + space + wl > 900:
                lines.append(cur)
                cur, cw = [], 0
            cur.append(w_)
            cw += (space if cw else 0) + wl
        lines.append(cur)
        asc, desc = f.getmetrics()
        lh = asc + desc + 8
        widths = [sum(f.getlength(w_) for w_ in l) + space * (len(l) - 1) for l in lines]
        bw, bh = int(max(widths)) + 80, lh * len(lines) + 34
        strip = Image.new("RGBA", (bw, bh), WHITE + (245,))
        d = ImageDraw.Draw(strip)
        d.rectangle([0, 0, 10, bh], fill=RED)
        idx = 0
        for li, l in enumerate(lines):
            x = (bw - widths[li]) / 2 + 5
            y0 = 16 + li * lh
            for w_ in l:
                wl = f.getlength(w_)
                if t >= times[idx]:
                    k = ease_out((t - times[idx]) / 0.18)
                    col = RED if is_key(w_) else INK
                    d.text((x, y0 + 12 * (1 - k)), w_, font=f, fill=col + (int(255 * k),))
                x += wl + space
                idx += 1
        k = ease_out((t - s + 0.02) / 0.2)
        place(c, kr.with_shadow(strip, offset=(0, 8), blur=10, alpha=0.3), W / 2, y + 20 * (1 - k),
              alpha=k * clamp((e - t) / 0.1))


def draw_fig(c, t, name, t0, cx, bottom, height, rise=300):
    spr = FIG[name]
    sc = height / spr.height
    kr.alive(c, spr, t, t0, cx, bottom - height / 2, sc=sc, rise=rise)


# ---------------------------------------------------------------- pages
def page(t, s0):
    if s0 == 0.0:  # COVER
        c = Image.fromarray(BG_COVER).convert("RGBA")
        draw_fig(c, t, "terangkan", 0.0, 560, H + 120, 1900, rise=200)
        place(c, A["mast"], W / 2, 210)  # masthead sits behind the head like a real cover? keep in front for legibility
        place(c, A["issue"], W / 2, 365)
        reveal(c, A["cl1"], t, 0.35, 260, 640, "left")
        if t >= 1.0:  # tiny "logo" crossed out
            d = ImageDraw.Draw(c)
            k = ease_back((t - 1.0) / 0.3)
            d.ellipse([110, 760, 110 + 120 * k, 760 + 120 * k], outline=GREY, width=6)
            d.text((128, 792), "LOGO", font=F_SANS_B(28), fill=GREY)
            strike(c, t, 1.3, 90, 250, 880, RED, 10)
        reveal(c, A["cl_big1"], t, 3.17, 300, 1180, "up")
        reveal(c, A["cl_big2"], t, 3.4, 330, 1420, "up")
        reveal(c, A["cl_sub"], t, 3.6, 330, 1580, "left")
        place(c, A["barcode"], 900, 1520, rot=0)
    elif s0 == 4.3:  # p.12 pull quote
        c = Image.fromarray(PAGES[1]).convert("RGBA")
        d = ImageDraw.Draw(c)
        header(d, "PERSONAL BRANDING", 12)
        reveal(c, A["quote"], t, 4.5, W / 2, 330, "up", dur=0.6)
        reveal(c, A["q_by"], t, 5.2, W / 2, 500, "left")
        reveal(c, CU_THUMBS, t, 5.0, 330, 980, "up", dur=0.6, rot=-2)
        reveal(c, A["dek"], t, 6.4, 790, 720, "left")
        for j, (tt, y) in enumerate(zip([8.4, 9.2, 10.3], [880, 1060, 1240])):
            if t >= tt:
                place(c, A["trio"][j], 800, y, scale=ease_back((t - tt) / 0.3))
                underline(c, t, tt + 0.15, 660, 960, y + 62, RED if j == 1 else INK, 6)
    elif s0 == 11.3:  # p.24 duta produk
        c = Image.fromarray(PAGES[2]).convert("RGBA")
        d = ImageDraw.Draw(c)
        header(d, "FEATURE", 24)
        reveal(c, A["kicker_duta"], t, 11.4, 180, 220, "left")
        reveal(c, A["h_duta"], t, 11.5, W / 2, 330, "up", dur=0.6)
        if t < 15.1:
            reveal(c, CELEB, t, 11.8, 300, 860, "up")
            reveal(c, A["celeb_tag"], t, 12.2, 300, 1180, "left")
            reveal(c, A["celeb_price"], t, 12.5, 300, 1270, "left")
            if t >= 14.26:
                place(c, A["anda_q"], 780, 800, scale=ease_back((t - 14.26) / 0.3), rot=-6)
        else:
            reveal(c, A["duta_lbl"], t, 15.15, 300, 560, "left")
            draw_fig(c, t, "thumbs_produk", 15.1, 360, 1560, 940)
            if t >= 17.01:
                place(c, A["sash"], 650, 1240, rot=-8, scale=1.6 - 0.6 * ease_out(clamp((t - 17.01) / 0.18)),
                      alpha=clamp((t - 17.01) / 0.12))
    elif s0 == 18.4:  # p.36 three steps
        c = Image.fromarray(PAGES[3]).convert("RGBA")
        d = ImageDraw.Draw(c)
        header(d, "PANDUAN", 36)
        reveal(c, A["kicker_3"], t, 18.5, 170, 220, "left")
        reveal(c, A["h_3"], t, 18.6, W / 2, 320, "up", dur=0.6)
        for j, (tt, (num, txt, _, _)) in enumerate(zip([20.47, 23.18, 26.12], STEPS)):
            y = 650 + j * 360
            if t >= tt:
                reveal(c, STEP_IMG[j], t, tt, 250, y, "up")
                place(c, text_img(num, F_SERIF(130), RED), 560, y - 60, scale=ease_back((t - tt - 0.1) / 0.3))
                reveal(c, text_img(txt, F_SANS(46), INK, maxw=440), t, tt + 0.2, 760, y + 70, "left")
                underline(c, t, tt + 0.5, 500, 980, y + 150, (210, 205, 195), 3)
    elif s0 == 29.3:  # p.48 lifestyle
        c = Image.fromarray(PAGES[4]).convert("RGBA")
        d = ImageDraw.Draw(c)
        header(d, "GAYA HIDUP", 48)
        reveal(c, A["kicker_gaya"], t, 29.4, 180, 220, "left")
        reveal(c, A["h_gaya"], t, 29.5, 370, 330, "up")
        reveal(c, A["selebriti"], t, 29.8, 400, 480, "up")
        strike(c, t, 30.2, 110, 700, 500, RED, 14)
        reveal(c, CU_KOPI, t, 30.6, 720, 980, "up", dur=0.6, rot=3)
        reveal(c, A["diri"], t, 31.3, 330, 1000, "left")
        if t >= 32.85:
            reveal(c, A["konsisten"], t, 32.85, 290, 1250, "left")
            for k in range(7):
                if t >= 33.0 + k * 0.12:
                    x = 110 + k * 72
                    kk = ease_back((t - 33.0 - k * 0.12) / 0.25)
                    d.ellipse([x - 26 * kk, 1340 - 26 * kk, x + 26 * kk, 1340 + 26 * kk], fill=RED)
                    if kk > 0.9:
                        d.line([(x - 12, 1340), (x - 3, 1350), (x + 13, 1330)], fill=WHITE, width=6)
    elif s0 == 34.2:  # p.52 infographic
        c = Image.fromarray(PAGES[5]).convert("RGBA")
        d = ImageDraw.Draw(c)
        header(d, "INFOGRAFIK", 52)
        reveal(c, A["kicker_info"], t, 34.3, 190, 220, "left")
        reveal(c, A["h_info"], t, 34.4, W / 2, 320, "up")
        draw_fig(c, t, "fikir", 34.5, 270, 1560, 900)
        ys = [600, 960, 1320]
        for j, (tt, y) in enumerate(zip([34.6, 36.23, 38.96], ys)):
            if t >= tt:
                place(c, NODES[j], 760, y, scale=ease_back((t - tt) / 0.35))
            if j < 2 and t >= [36.0, 38.7][j]:
                k = ease_out((t - [36.0, 38.7][j]) / 0.3)
                d.line([(760, y + 165), (760, y + 165 + 30 * k)], fill=INK, width=8)
                if k > 0.95:
                    d.polygon([(740, y + 190), (780, y + 190), (760, y + 210)], fill=INK)
    else:  # closing cover
        c = Image.fromarray(BG_BACK).convert("RGBA")
        draw_fig(c, t, "menang", 39.9, 540, H + 80, 1700, rise=200)
        place(c, A["mast"], W / 2, 210)
        reveal(c, A["back_big1"], t, 40.66, W / 2, 940, "up")
        reveal(c, A["back_big2"], t, 41.1, W / 2, 1090, "up")
        if t >= 42.2:
            place(c, A["back_anda"], W / 2, 1290, scale=1.5 - 0.5 * ease_out(clamp((t - 42.2) / 0.2)),
                  alpha=clamp((t - 42.2) / 0.12), rot=-4)
        if t >= 43.0:
            pulse = 1 + 0.04 * max(0.0, math.sin((t - 43.0) * 7))
            kr.pop(c, kr.A["follow"], t, 43.0, 540, 1500, scale=pulse)
    return c


# ---------------------------------------------------------------- page turn + camera
def page_turn(base, old, u):
    """Old page curls away around the left spine, revealing base underneath."""
    xr = W * (1 - ease_inout(u))
    lift = 90 * math.sin(math.pi * u)
    out = base.astype(np.float32)
    # shadow cast on the new page next to the fold
    xx = np.arange(W)[None, :]
    sh = np.clip(1 - (xx - xr) / 260, 0, 1) * (xx >= xr) * 0.45 * math.sin(math.pi * u)
    out *= (1 - sh)[..., None]
    if xr > 4:
        src = np.float32([[0, 0], [W, 0], [W, H], [0, H]])
        dst = np.float32([[0, 0], [xr, -lift], [xr, H + lift], [0, H]])
        M = cv2.getPerspectiveTransform(src, dst)
        warped = cv2.warpPerspective(old, M, (W, H), flags=cv2.INTER_LINEAR)
        mask = cv2.warpPerspective(np.ones((H, W), np.float32), M, (W, H))
        shade = 1 - 0.35 * u - 0.25 * np.clip((xx - (xr - 140)) / 140, 0, 1) * math.sin(math.pi * u)
        warped = warped.astype(np.float32) * shade[..., None]
        out = out * (1 - mask[..., None]) + warped * mask[..., None]
    return np.clip(out, 0, 255).astype(np.uint8)


def camera(arr, t):
    s0 = scene_start(t)
    nxt = [x for x in CUTS if x > t]
    s1 = nxt[0] if nxt else DUR
    z = 1.0 + 0.04 * ease_inout((t - s0) / (s1 - s0))
    for pt in PUNCHES:
        dt = t - pt
        if 0 <= dt < 0.6:
            z *= 1 + 0.05 * (dt / 0.06 if dt < 0.06 else math.exp(-(dt - 0.06) * 7))
    if abs(z - 1) < 1e-4:
        return arr
    M = np.float32([[z, 0, W / 2 - z * W / 2], [0, z, H * 0.45 - z * H * 0.45]])
    return cv2.warpAffine(arr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


TURN = 0.55


def frame(i):
    t = i / FPS
    s0 = scene_start(t)
    arr = camera(np.asarray(page(t, s0).convert("RGB")), t)
    for ct in CUTS:  # turn starts at the cut: old page (frozen at the cut) curls off the new one
        if ct <= t < ct + TURN:
            prev = max([0.0] + [x for x in CUTS if x < ct])
            old = camera(np.asarray(page(ct - 0.001, prev).convert("RGB")), ct - 0.001)
            arr = page_turn(arr, old, (t - ct) / TURN)
    arr = arr.astype(np.float32) + kr.GRAIN[i % len(kr.GRAIN)][..., None] * 0.35
    c = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    draw_caption(c, t)
    rgb = np.asarray(c.convert("RGB"))
    if t < 0.15 or t > DUR - 0.35:
        rgb = (rgb.astype(np.float32) * clamp(t / 0.15) * clamp((DUR - t) / 0.35)).astype(np.uint8)
    return rgb


if __name__ == "__main__":
    if len(sys.argv) > 2:
        for ts in sys.argv[2:]:
            Image.fromarray(frame(int(float(ts) * FPS))).save(f"{WD}/mg_{ts}.jpg", quality=85)
    else:
        out = sys.stdout.buffer
        for i in range(N):
            out.write(frame(i).tobytes())
            if i % 100 == 0:
                print(f"frame {i}/{N}", file=sys.stderr, flush=True)
