"""Poster WhatsApp Firea (harga & feedback), 1080x1350.

Jalankan: python3 make_posters.py  ->  ../../output/firea-poster-*.jpg
Guna gambar produk dan screenshot chat sebenar dari ../img.
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "..", "img")
OUT = os.path.join(HERE, "..", "..", "output")
W, H = 1080, 1350

BERRY, BERRY2, ROSE, PETAL, BLUSH, PAPER = (90, 21, 49), (125, 31, 69), (194, 24, 91), (255, 201, 218), (253, 242, 245), (255, 250, 251)
INK, MUTED, GOOD, WHITE = (58, 20, 36), (122, 88, 103), (31, 138, 76), (255, 255, 255)

_fc = {}
def F(name, size):
    k = (name, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(os.path.join(HERE, "fonts", name + ".ttf"), size)
    return _fc[k]

def load(p):
    return Image.open(os.path.join(IMG, p)).convert("RGB")

def bg_blush():
    im = Image.new("RGB", (W, H), BLUSH)
    d = ImageDraw.Draw(im)
    for i, r in enumerate((620, 470)):
        d.ellipse((W - r // 2 - 120, -r // 2 + 80, W + r // 2 - 120, r // 2 + 80), fill=(255, 226, 236) if i == 0 else (255, 214, 228))
    return im.filter(ImageFilter.GaussianBlur(2)).convert("RGBA")

def bg_berry():
    im = Image.new("RGB", (W, H), BERRY)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((-200, -300, W + 200, 700), fill=BERRY2 + (255,))
    im = im.convert("RGBA"); im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    return im

def rounded(im, r, border=0, bcol=WHITE):
    im = im.convert("RGBA")
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, fill=255)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0)); out.paste(im, (0, 0), m)
    if border:
        ImageDraw.Draw(out).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, outline=bcol + (255,), width=border)
    return out

def shadow_paste(base, im, xy, blur=22, off=10, op=70):
    pad = blur * 2
    sh = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    sh.paste((60, 10, 30, op), (pad, pad + off, pad + im.width, pad + off + im.height), im.getchannel("A"))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)), (xy[0] - pad, xy[1] - pad))
    base.alpha_composite(im, xy)

def cover(im, w, h, cy=0.5):
    s = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * s + 1), int(im.height * s + 1)), Image.LANCZOS)
    x = (im.width - w) // 2; y = int((im.height - h) * cy)
    return im.crop((x, y, x + w, y + h))

def fit(im, w):
    return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)

def text(d, xy, s, font, fill, anchor="la"):
    d.text(xy, s, font=font, fill=fill, anchor=anchor)

def hl_text(base, cx, y, parts, size, anchor_center=True):
    """parts: [(teks, highlight?)] -> satu baris, perkataan highlight berlatar petal."""
    d = ImageDraw.Draw(base); f = F("Bricolage800", size)
    widths = [f.getlength(t) for t, _ in parts]; total = sum(widths)
    x = cx - total / 2 if anchor_center else cx
    for (t, h), w in zip(parts, widths):
        if h:
            d.rounded_rectangle((x - 10, y + size * 0.12, x + w + 10, y + size * 1.12), 14, fill=PETAL)
        d.text((x, y), t, font=f, fill=BERRY if h else INK)
        x += w

def pill(d, cx, cy, s, font, bg, fg, padx=26, pady=12):
    w = font.getlength(s); l, t, r, b = font.getbbox(s); h = b - t
    d.rounded_rectangle((cx - w / 2 - padx, cy - h / 2 - pady, cx + w / 2 + padx, cy + h / 2 + pady), (h + pady * 2) / 2, fill=bg)
    d.text((cx, cy), s, font=font, fill=fg, anchor="mm")

def brand_header(base, dark=False):
    d = ImageDraw.Draw(base)
    col = WHITE if dark else BERRY
    text(d, (W / 2, 70), "Firea", F("Bricolage800", 52), col, "mm")
    text(d, (W / 2, 112), "confidence in every touch", F("Figtree500", 24), (240, 200, 215) if dark else MUTED, "mm")

def footer(base, s="Bernotifikasi KKM NOT260705867K  ·  0% Alkohol  ·  0% Paraben", dark=False):
    d = ImageDraw.Draw(base)
    text(d, (W / 2, H - 42), s, F("Figtree700", 24), (240, 200, 215) if dark else MUTED, "mm")

def save(base, name):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"firea-poster-{name}.jpg")
    base.convert("RGB").save(p, quality=92, optimize=True)
    print("siap:", os.path.relpath(p, os.path.join(HERE, "..", "..")))

# ---------------------------------------------------------------- HARGA
def poster_harga():
    base = bg_blush(); d = ImageDraw.Draw(base)
    brand_header(base)
    hl_text(base, W / 2, 150, [("Pilih ", False), ("Pakej", True), (" Anda", False)], 84)
    text(d, (W / 2, 278), "Celeste Musk Deodorant Roll-on 50ml", F("Figtree700", 34), MUTED, "mm")
    # produk
    prod = rounded(cover(load("produk-pink.jpg"), 330, 430, 0.42), 34, 6)
    shadow_paste(base, prod, (60, 340))
    # kad pakej
    rows = [("1 BOTOL", "RM28", "+ postage", None, False),
            ("2 BOTOL", "RM50", "Jimat RM6 · Free pos (SM)", None, False),
            ("3 BOTOL", "RM65", "Jimat RM19 · Free pos (SM)", "PALING JIMAT", True)]
    x0, x1, y = 430, 1020, 340
    for name, price, sub, tag, feat in rows:
        h = 150 if feat else 126
        bgc, nc, pc, sc = (BERRY, WHITE, PETAL, (245, 210, 222)) if feat else (PAPER, INK, ROSE, MUTED)
        card = Image.new("RGBA", (x1 - x0, h), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card); cd.rounded_rectangle((0, 0, card.width - 1, h - 1), 28, fill=bgc + (255,), outline=(PETAL if feat else (240, 213, 223)) + (255,), width=4)
        cd.text((30, h / 2 - 18), name, font=F("Bricolage800", 44), fill=nc, anchor="lm")
        cd.text((30, h / 2 + 30), sub, font=F("Figtree700", 26), fill=sc, anchor="lm")
        cd.text((card.width - 28, h / 2 + 2), price, font=F("Bricolage800", 60), fill=pc, anchor="rm")
        shadow_paste(base, card, (x0, y))
        if tag:
            pill(d, x1 - 120, y, tag, F("Figtree800", 24), ROSE, WHITE, 18, 8)
        y += h + 30
    # info postage
    box = (60, 830, 1020, 1185)
    d.rounded_rectangle(box, 30, fill=PAPER, outline=(240, 213, 223), width=3)
    lines = [("Postage J&T", "Semenanjung RM8 · PERCUMA 2 botol ke atas"),
             ("", "Sabah & Sarawak RM15"),
             ("Sampai", "Semenanjung 2–3 hari · Sabah & Sarawak 5–6 hari"),
             ("Bayaran", "COD atau online transfer"),
             ("Jaminan", "7 hari: kulit tak serasi atau botol rosak")]
    yy = 880
    for k, v in lines:
        if k: text(d, (100, yy), k, F("Figtree800", 28), BERRY, "lm")
        text(d, (330, yy), v, F("Figtree700", 28), INK, "lm")
        yy += 64 if k else 50
    pill(d, W / 2, 1250, "Balas nombor pakej untuk order: 1, 2 atau 3", F("Figtree800", 32), ROSE, WHITE, 34, 18)
    footer(base)
    save(base, "1-senarai-harga")

def poster_3botol():
    base = bg_berry(); d = ImageDraw.Draw(base)
    brand_header(base, dark=True)
    pill(d, W / 2, 190, "PAKEJ PALING JIMAT", F("Figtree800", 34), PETAL, BERRY, 30, 14)
    ph = rounded(cover(load("produk-tangan.jpg"), 470, 600, 0.45), 40, 6, PETAL)
    ph = ph.rotate(-4, resample=Image.BICUBIC, expand=True)
    shadow_paste(base, ph, (W // 2 - ph.width // 2 - 230, 270), op=120)
    rx = 640
    text(d, (rx, 330), "3 BOTOL", F("Bricolage800", 92), WHITE, "lm")
    text(d, (rx, 465), "RM65", F("Bricolage800", 128), PETAL, "lm")
    f = F("Figtree800", 44); text(d, (rx, 590), "RM84", f, (220, 170, 190), "lm")
    sw = f.getlength("RM84"); d.line((rx, 592, rx + sw, 592), fill=(220, 170, 190), width=5)
    pill(d, rx + sw + 120, 592, "Jimat RM19", F("Figtree800", 32), ROSE, WHITE, 20, 10)
    for i, s in enumerate(["RM21.67 sebotol", "Cukup 4 bulan", "(sebotol 40–45 hari)"]):
        text(d, (rx, 680 + i * 50), s, F("Figtree700", 34 if i < 2 else 28), WHITE if i < 2 else (230, 190, 205), "lm")
    # jalur free pos
    d.rounded_rectangle((60, 930, 1020, 1060), 30, fill=PETAL)
    text(d, (W / 2, 975), "FREE POSTAGE SEMENANJUNG", F("Bricolage800", 56), BERRY, "mm")
    text(d, (W / 2, 1028), "COD tersedia · Sampai dalam 2–3 hari (J&T)", F("Figtree700", 30), BERRY2, "mm")
    text(d, (W / 2, 1130), "Beli satu-satu: 3 x RM28 + postage RM8 = RM92.", F("Figtree700", 32), (240, 210, 222), "mm")
    text(d, (W / 2, 1175), "Ambil pakej 3 botol: RM65 sahaja, terus free pos.", F("Figtree700", 32), (240, 210, 222), "mm")
    pill(d, W / 2, 1260, "Balas '3' untuk order sekarang", F("Figtree800", 36), WHITE, BERRY, 40, 20)
    save(base, "2-pakej-3-botol")

def poster_cara_order():
    base = bg_blush(); d = ImageDraw.Draw(base)
    brand_header(base)
    hl_text(base, W / 2, 150, [("Cara ", False), ("Order", True), (" Firea", False)], 88)
    text(d, (W / 2, 285), "Senang je. 4 langkah, terus sampai depan rumah.", F("Figtree700", 34), MUTED, "mm")
    steps = [("Pilih pakej", "1 botol RM28 · 2 botol RM50 · 3 botol RM65"),
             ("Hantar maklumat", "Nama, nombor telefon dan alamat penuh"),
             ("Pilih cara bayar", "COD (bayar bila barang sampai) atau online transfer"),
             ("Barang dipos", "J&T: Semenanjung 2–3 hari · Sabah & Sarawak 5–6 hari")]
    y = 360
    for i, (t, s) in enumerate(steps, 1):
        card = Image.new("RGBA", (960, 170), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
        cd.rounded_rectangle((0, 0, 959, 169), 30, fill=PAPER + (255,), outline=(240, 213, 223, 255), width=3)
        cd.ellipse((30, 35, 130, 135), fill=BERRY + (255,))
        cd.text((80, 85), str(i), font=F("Bricolage800", 56), fill=WHITE, anchor="mm")
        cd.text((165, 62), t, font=F("Bricolage800", 44), fill=INK, anchor="lm")
        cd.text((165, 117), s, font=F("Figtree700", 28), fill=MUTED, anchor="lm")
        shadow_paste(base, card, (60, y)); y += 195
    d.rounded_rectangle((60, 1150, 1020, 1235), 26, fill=BERRY)
    text(d, (W / 2, 1192), "Jaminan 7 hari: kulit tak serasi atau botol rosak, WhatsApp kami", F("Figtree800", 28), WHITE, "mm")
    text(d, (W / 2, 1282), "Postage Semenanjung RM8, PERCUMA untuk 2 botol ke atas · Sabah & Sarawak RM15", F("Figtree700", 24), MUTED, "mm")
    footer(base)
    save(base, "3-cara-order")


def draw_bottle(base, x, y, h=150):
    """Ikon botol roll-on Firea: penutup putih tinggi, badan pink dengan label."""
    w = int(h * 0.44)
    lay = Image.new("RGBA", (w + 30, h + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    cap_h = int(h * 0.48); ox, oy = 8, 6
    # bayang
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((ox + 4, oy + 8, ox + w + 4, oy + h + 8), w // 5, fill=(90, 21, 49, 70))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    # badan
    d.rounded_rectangle((ox, oy + cap_h - 6, ox + w, oy + h), w // 6, fill=(244, 184, 204))
    d.rectangle((ox + 5, oy + cap_h + 8, ox + w - 5, oy + h - 14), fill=(252, 230, 238))
    d.text((ox + w / 2, oy + cap_h + 26), "Firea", font=F("Bricolage800", max(12, h // 10)), fill=BERRY, anchor="mm")
    d.line((ox + 10, oy + cap_h + 44, ox + w - 10, oy + cap_h + 44), fill=(240, 170, 195), width=3)
    d.line((ox + 10, oy + cap_h + 54, ox + w - 18, oy + cap_h + 54), fill=(240, 170, 195), width=3)
    # penutup
    d.rounded_rectangle((ox - 1, oy, ox + w + 1, oy + cap_h), w // 3, fill=(255, 255, 255), outline=(232, 212, 220), width=2)
    d.rectangle((ox - 1, oy + cap_h - 14, ox + w + 1, oy + cap_h), fill=(255, 255, 255))
    d.line((ox - 1, oy + cap_h, ox + w + 1, oy + cap_h), fill=(232, 212, 220), width=2)
    d.line((ox + 8, oy + 14, ox + 8, oy + cap_h - 12), fill=(244, 238, 241), width=6)
    base.alpha_composite(lay, (int(x) - ox, int(y) - oy))

def poster_harga_sahaja():
    base = bg_blush(); d = ImageDraw.Draw(base)
    brand_header(base)
    hl_text(base, W / 2, 150, [("Harga ", False), ("Pakej", True), (" Firea", False)], 92)
    text(d, (W / 2, 290), "Celeste Musk Deodorant Roll-on 50ml", F("Figtree700", 36), MUTED, "mm")
    cards = [(1, "1 BOTOL", "RM28", "RM28 sebotol", None, [], False),
             (2, "2 BOTOL", "RM50", "RM25 sebotol", "RM56", ["Jimat RM6", "FREE POS"], False),
             (3, "3 BOTOL", "RM65", "RM21.67 sebotol", "RM84", ["Jimat RM19", "FREE POS"], True)]
    y = 350
    for n, name, price, per, old, tags, feat in cards:
        h = 270 if feat else 240
        x0, x1 = 60, 1020
        bgc = BERRY if feat else PAPER
        card = Image.new("RGBA", (x1 - x0, h), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
        cd.rounded_rectangle((0, 0, card.width - 1, h - 1), 36, fill=bgc + (255,), outline=(PETAL if feat else (240, 213, 223)) + (255,), width=5 if feat else 3)
        shadow_paste(base, card, (x0, y), op=90 if feat else 60)
        # botol
        bh = h - 30
        bot = Image.open(os.path.join(IMG, "botol-cutout.png")).convert("RGBA")
        bot = bot.resize((int(bot.width * bh / bot.height), bh), Image.LANCZOS)
        step = {1: 0, 2: 78, 3: 70}[n]
        bx = x0 + 40 + (0 if n == 3 else (70 if n == 1 else 35)); by = y + (h - bh) // 2 + 4
        for k in range(n):
            b = bot.rotate((-4, 3, -2)[k], resample=Image.BICUBIC, expand=True)
            shadow_paste(base, b, (bx + k * step, by - (8 if k == 1 else 0)), blur=10, off=6, op=70)
        # teks
        tx = x0 + 310
        nc, sc, pc = (WHITE, (245, 205, 220), PETAL) if feat else (INK, MUTED, ROSE)
        text(d, (tx, y + h / 2 - 40), name, F("Bricolage800", 56), nc, "lm")
        text(d, (tx, y + h / 2 + 16), per, F("Figtree700", 30), sc, "lm")
        tx2 = tx
        for t in tags:
            f = F("Figtree800", 24); w = f.getlength(t)
            bgp = (ROSE if feat else BERRY) if t.startswith("FREE") else (PETAL if feat else (255, 226, 236))
            fgp = WHITE if t.startswith("FREE") else BERRY
            d.rounded_rectangle((tx2, y + h / 2 + 46, tx2 + w + 28, y + h / 2 + 86), 20, fill=bgp)
            d.text((tx2 + 14 + w / 2, y + h / 2 + 66), t, font=f, fill=fgp, anchor="mm")
            tx2 += w + 40
        text(d, (x1 - 40, y + h / 2 + (14 if old else 0)), price, F("Bricolage800", 104 if feat else 92), pc, "rm")
        if old:
            fo = F("Figtree800", 34); ow = fo.getlength(old); ox = x1 - 40 - ow; oy = y + h / 2 - 62
            d.text((ox, oy), old, font=fo, fill=(225, 175, 195) if feat else MUTED, anchor="lm")
            d.line((ox, oy + 2, ox + ow, oy + 2), fill=(225, 175, 195) if feat else MUTED, width=4)
        if feat:
            pill(d, x1 - 150, y, "PALING JIMAT", F("Figtree800", 28), ROSE, WHITE, 22, 10)
        y += h + 40
    text(d, (W / 2, 1255), "FREE POS untuk Semenanjung · 1 botol + postage RM8 · Sabah & Sarawak RM15", F("Figtree700", 25), MUTED, "mm")
    footer(base)
    save(base, "8-harga-pakej")

def poster_followup_cuba():
    """Follow-up tanpa diskaun: cuba 1 botol dengan jaminan 7 hari."""
    base = bg_blush(); d = ImageDraw.Draw(base)
    brand_header(base)
    hl_text(base, W / 2, 140, [("Masih ", False), ("Fikir-Fikir?", True)], 92)
    text(d, (W / 2, 278), "Cuba 1 botol dulu. Tak serasi? Kami uruskan.", F("Figtree800", 38), BERRY2, "mm")
    # botol besar kiri
    bot = Image.open(os.path.join(IMG, "botol-cutout.png")).convert("RGBA")
    bh = 600; bot = bot.resize((int(bot.width * bh / bot.height), bh), Image.LANCZOS).rotate(-5, resample=Image.BICUBIC, expand=True)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((40, 400, 500, 900), fill=(255, 222, 233, 230))
    base.alpha_composite(glow.filter(ImageFilter.GaussianBlur(60)))
    shadow_paste(base, bot, (120, 335), blur=14, off=10, op=35)
    # harga bawah botol
    card = Image.new("RGBA", (400, 130), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
    cd.rounded_rectangle((0, 0, 399, 129), 30, fill=BERRY + (255,))
    cd.text((200, 50), "1 BOTOL RM28", font=F("Bricolage800", 46), fill=WHITE, anchor="mm")
    cd.text((200, 98), "+ postage RM8 (Semenanjung)", font=F("Figtree700", 24), fill=(245, 205, 220), anchor="mm")
    shadow_paste(base, card, (70, 965))
    # kanan: jaminan
    rx0, rx1 = 520, 1020
    box = Image.new("RGBA", (rx1 - rx0, 400), (0, 0, 0, 0)); bd = ImageDraw.Draw(box)
    bd.rounded_rectangle((0, 0, box.width - 1, 399), 32, fill=PAPER + (255,), outline=(240, 213, 223, 255), width=3)
    # cop
    cx, cy = 95, 105
    bd.ellipse((cx - 72, cy - 72, cx + 72, cy + 72), fill=ROSE + (255,))
    bd.ellipse((cx - 60, cy - 60, cx + 60, cy + 60), outline=(255, 255, 255, 200), width=3)
    bd.text((cx, cy - 12), "7", font=F("Bricolage800", 64), fill=WHITE, anchor="mm")
    bd.text((cx, cy + 36), "HARI", font=F("Figtree800", 24), fill=WHITE, anchor="mm")
    bd.text((190, 78), "Jaminan", font=F("Bricolage800", 44), fill=INK, anchor="lm")
    bd.text((190, 128), "7 hari penggunaan", font=F("Figtree700", 28), fill=MUTED, anchor="lm")
    yy = 220
    for t in ("Kulit rasa gatal atau panas", "Botol rosak semasa sampai"):
        bd.ellipse((30, yy - 18, 66, yy + 18), fill=(234, 246, 238, 255))
        bd.line([(38, yy + 1), (45, yy + 9), (59, yy - 8)], fill=GOOD + (255,), width=5, joint="curve")
        bd.text((84, yy), t, font=F("Figtree700", 28), fill=INK, anchor="lm")
        yy += 56
    bd.text((30, 345), "WhatsApp kami, kami uruskan.", font=F("Figtree800", 28), fill=ROSE, anchor="lm")
    shadow_paste(base, box, (rx0, 340))
    # bukti chat
    text(d, (rx0 + 10, 790), "Kata pelanggan:", F("Figtree800", 28), BERRY, "lm")
    chat = rounded(fit(load("wa/wa-11.jpg"), rx1 - rx0), 20)
    shadow_paste(base, chat.rotate(1.2, resample=Image.BICUBIC, expand=True), (rx0 - 4, 820))
    # CTA
    pill(d, W / 2, 1200, "Balas 'NAK' untuk cuba 1 botol", F("Figtree800", 40), ROSE, WHITE, 46, 22)
    text(d, (W / 2, 1270), "COD tersedia  ·  0% Alkohol  ·  0% Paraben", F("Figtree700", 28), MUTED, "mm")
    footer(base, "Bernotifikasi KKM NOT260705867K  ·  Keputusan berbeza mengikut individu")
    save(base, "9-followup-cuba-1-botol")

# ---------------------------------------------------------------- FEEDBACK
def chat_stack(base, files, top, bottom, width=900, gap=26, tilt=(-1.5, 1.2, -0.8, 1.0)):
    ims = [rounded(fit(load(os.path.join("wa", f)), width), 22) for f in files]
    total = sum(i.height for i in ims) + gap * (len(ims) - 1)
    scale = min(1.0, (bottom - top) / total)
    y = top + ((bottom - top) - total * scale) / 2
    for k, im in enumerate(ims):
        if scale < 1:
            im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
        r = im.rotate(tilt[k % len(tilt)], resample=Image.BICUBIC, expand=True)
        shadow_paste(base, r, (int(W / 2 - r.width / 2), int(y)))
        y += im.height + gap * scale

def poster_feedback_chat():
    base = bg_blush(); d = ImageDraw.Draw(base)
    brand_header(base)
    hl_text(base, W / 2, 145, [("Apa Kata ", False), ("Pelanggan", True)], 84)
    text(d, (W / 2, 275), "Mesej WhatsApp sebenar dari pengguna Firea", F("Figtree700", 32), MUTED, "mm")
    chat_stack(base, ["wa-8.jpg", "wa-1.jpg", "wa-4.jpg"], 320, 1210)
    d.rectangle((0, 1230, W, 1290), fill=BLUSH)
    pill(d, W / 2, 1255, "Tahan dari pagi sampai malam", F("Figtree800", 32), BERRY, WHITE, 34, 16)
    footer(base, "Keputusan berbeza mengikut individu")
    save(base, "4-feedback-whatsapp")

def poster_feedback_quote():
    base = bg_berry(); d = ImageDraw.Draw(base)
    brand_header(base, dark=True)
    text(d, (90, 205), "“", F("Bricolage800", 220), PETAL, "lm")
    q = ["Pakai seharian dari", "7 pagi sampai malam", "pukul 11, badan tak", "berbau langsung."]
    for i, s in enumerate(q):
        text(d, (W / 2, 300 + i * 92), s, F("Bricolage800", 78), WHITE if i not in (1,) else PETAL, "mm")
    text(d, (W / 2, 690), "— Pelanggan Firea, melalui WhatsApp", F("Figtree700", 32), (240, 200, 215), "mm")
    shot = rounded(fit(load("wa/wa-8.jpg"), 820), 24, 4, PETAL)
    shadow_paste(base, shot.rotate(-2, resample=Image.BICUBIC, expand=True), (W // 2 - 420, 760), op=130)
    pill(d, W / 2, 1150, "Celeste Musk · 0% Alkohol · Cepat Kering", F("Figtree800", 32), PETAL, BERRY, 34, 16)
    text(d, (W / 2, 1235), "1 botol RM28  ·  3 botol RM65 FREE POS (Semenanjung)", F("Figtree800", 32), WHITE, "mm")
    footer(base, "Screenshot sebenar · Keputusan berbeza mengikut individu", dark=True)
    save(base, "5-feedback-petikan")

def poster_feedback_kulit():
    base = bg_blush(); d = ImageDraw.Draw(base)
    brand_header(base)
    hl_text(base, W / 2, 145, [("Tak Pedih, ", False), ("Tak Melekit", True)], 80)
    text(d, (W / 2, 272), "Kata mereka yang kulit sensitif & aktif seharian", F("Figtree700", 32), MUTED, "mm")
    chat_stack(base, ["wa-11.jpg", "wa-9.jpg"], 315, 1215, tilt=(1.2, -1.2))
    d.rectangle((0, 1228, W, 1292), fill=BLUSH)
    pill(d, W / 2, 1258, "0% Alkohol · 0% Paraben · Bernotifikasi KKM", F("Figtree800", 30), BERRY, WHITE, 34, 16)
    footer(base, "Nama jenama lain dikaburkan · Keputusan berbeza mengikut individu")
    save(base, "6-feedback-kulit-sensitif")

def poster_video_faces():
    base = bg_berry(); d = ImageDraw.Draw(base)
    brand_header(base, dark=True)
    text(d, (W / 2, 190), "5 Pengguna Kongsi", F("Bricolage800", 80), WHITE, "mm")
    text(d, (W / 2, 280), "Pengalaman Mereka", F("Bricolage800", 80), PETAL, "mm")
    people = [("Ayu", "Kerja seharian", 1), ("Yana", "Kenduri tengah hari", 2), ("Alia", "Kulit sensitif", 3), ("Mira", "Pagi sampai malam", 4), ("Ilah", "Seharian di dapur", 5)]
    cw, ch = 300, 420
    pos = [(60, 360), (390, 360), (720, 360), (225, 830), (555, 830)]
    for (nm, sub, n), (x, y) in zip(people, pos):
        im = cover(load(f"testimoni-{n}-poster.jpg"), cw, ch, 0.35)
        card = rounded(im, 26, 5, PETAL); shadow_paste(base, card, (x, y), op=120)
        dd = ImageDraw.Draw(base)
        dd.rounded_rectangle((x, y + ch - 92, x + cw, y + ch), 0, fill=(40, 8, 22))
        dd.rounded_rectangle((x + 2, y + ch - 92, x + cw - 2, y + ch - 2), 24, fill=(60, 12, 32))
        text(dd, (x + cw / 2, y + ch - 62), nm, F("Bricolage800", 38), WHITE, "mm")
        text(dd, (x + cw / 2, y + ch - 26), sub, F("Figtree700", 24), PETAL, "mm")
        dd.ellipse((x + cw / 2 - 34, y + ch / 2 - 70, x + cw / 2 + 34, y + ch / 2 - 2), fill=(255, 255, 255))
        dd.polygon([(x + cw / 2 - 10, y + ch / 2 - 54), (x + cw / 2 - 10, y + ch / 2 - 18), (x + cw / 2 + 18, y + ch / 2 - 36)], fill=BERRY)
    pill(d, W / 2, 1290, "Tonton video penuh di fireadeodorant.com", F("Figtree800", 32), PETAL, BERRY, 34, 16)
    save(base, "7-video-testimoni")

if __name__ == "__main__":
    poster_harga(); poster_3botol(); poster_cara_order(); poster_harga_sahaja(); poster_followup_cuba()
    poster_feedback_chat(); poster_feedback_quote(); poster_feedback_kulit(); poster_video_faces()
