"""Episode 3 — "Komen Pelanggan = Idea Video Percuma" (~37 s, 1080x1920@30).

Concept "BALAS KOMEN": the whole video lives inside a dark-mode social app. The presenter
(black & white cut-outs with a neon rim) answers comments; comment bubbles rain, get stamped
"+1 VIDEO" and fly into a profile grid as thumbnails. Swipe-up transitions, glitch hits,
neon kinetic captions. Laid out directly on the ElevenLabs VO timeline.

Usage: python3 komen_render.py <workdir> [t1 t2 ...]
  needs kolaj_render.py assets (photo.jpg + mask, expr/*.jpg + masks, fonts/).
"""
import math
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import kolaj_render as kr
from kolaj_render import F_ANTON, F_CAP, F_MARK, FPS, H, W, clamp, ease_back, ease_inout, ease_out, place, text_size

WD = sys.argv[1]
DUR = 37.0
N = int(DUR * FPS)

BG0 = (14, 15, 26)
PANEL = (35, 37, 55)
PINK = (255, 46, 136)
CYAN = (0, 229, 255)
LIME = (190, 255, 70)
WHITE = (255, 255, 255)
GREY = (150, 152, 170)
INK = (20, 20, 28)


# ---------------------------------------------------------------- neon stickers
def neon_sticker(img, mask, col, open_edges):
    pad = 60
    m = cv2.copyMakeBorder(mask, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    s = cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    if open_edges:  # body leaves frame at bottom/sides: no rim there
        m[-pad:, :] = np.maximum(m[-pad:, :], m[-pad - 1:-pad, :])
        m[:, :pad] = np.maximum(m[:, :pad], m[:, pad:pad + 1])
        m[:, -pad:] = np.maximum(m[:, -pad:], m[:, -pad - 1:-pad])
    k = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (r, r))
    white = cv2.GaussianBlur(cv2.dilate(m, k(11)), (0, 0), 1.0)
    rim = cv2.GaussianBlur(cv2.dilate(m, k(27)), (0, 0), 1.2)
    glow = cv2.GaussianBlur(cv2.dilate(m, k(31)), (0, 0), 16) * 0.85
    col = np.array(col, np.float32)
    rgb = np.where(m[..., None] > 0.5, s, np.where(white[..., None] > 0.5, 255.0, col))
    rgb = s * m[..., None] + (1 - m[..., None]) * np.where(white[..., None] > 0.5, 255.0, col)
    a = np.maximum.reduce([m, white, rim, glow])
    return Image.fromarray(np.dstack([rgb, a * 255]).clip(0, 255).astype(np.uint8), "RGBA")


def build_neon(photo, mask, col, head_bottom=0.56):
    im = Image.open(photo).convert("RGB")
    mk = Image.open(mask).convert("L")
    tw = 1127
    th = int(im.height * tw / im.width)
    src = np.asarray(im.resize((tw, th), Image.LANCZOS)).astype(np.float32)
    m = np.clip((np.asarray(mk.resize((tw, th), Image.LANCZOS)).astype(np.float32) / 255 - 0.2) / 0.6, 0, 1)
    s = kr.bw_dramatic(src)
    full = neon_sticker(s, m, col, open_edges=True)
    top = int(np.argmax(m.max(axis=1) > 0.5))
    y0, y1 = max(0, top - 70), int(th * head_bottom)
    hm = m[y0:y1].copy()
    # soft fade across the chest instead of a hard cut
    fade = np.clip((y1 - y0 - np.arange(y1 - y0)) / 90.0, 0, 1)[:, None]
    hm *= fade
    hm[hm < 0.5] = 0
    head = neon_sticker(s[y0:y1], hm, col, open_edges=False)
    return full, head


EX = f"{WD}/expr"
STK = {
    "keliru": build_neon(f"{EX}/9.jpg", f"{EX}/9_mask.png", PINK),
    "sinis": build_neon(f"{EX}/5.jpg", f"{EX}/5_mask.png", CYAN),
    "tunjuk": build_neon(f"{EX}/7.jpg", f"{EX}/7_mask.png", LIME),
    "fikir": build_neon(f"{EX}/6.jpg", f"{EX}/6_mask.png", CYAN, head_bottom=0.74),
    "terkejut": build_neon(f"{EX}/8.jpg", f"{EX}/8_mask.png", PINK),
    "senyum": build_neon(f"{EX}/4.jpg", f"{EX}/4_mask.png", PINK),
}
FULL_SC = W / (STK["sinis"][0].width - 120) * 1.02


def presenter_full(c, t, who, t0, cy_offset, scale=1.0, t1=None):
    spr = STK[who][0]
    sc = FULL_SC * scale
    kr.alive(c, spr, t, t0, W / 2, H - spr.height * sc / 2 + cy_offset + 60 * sc, sc=sc, t1=t1, rise=900)


def presenter_head(c, t, who, cx, cy, sc, t0, rot=0.0, t1=None):
    kr.alive(c, STK[who][1], t, t0, cx, cy, sc=sc, rot=rot, t1=t1)


# ---------------------------------------------------------------- app background
def make_bg(seed, tint):
    rng = np.random.default_rng(seed)
    yy = np.linspace(0, 1, H)[:, None, None]
    top, bot = np.array(BG0, np.float32), np.array(tint, np.float32)
    bg = (top * (1 - yy) + bot * yy) * np.ones((1, W, 1), np.float32)
    img = Image.fromarray(bg.astype(np.uint8)).convert("RGBA")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for _ in range(14):  # bokeh
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(40, 160)
        col = [PINK, CYAN, LIME, (140, 90, 255)][rng.integers(4)]
        d.ellipse([x - r, y - r, x + r, y + r], fill=col + (int(rng.uniform(18, 45)),))
    lay = lay.filter(ImageFilter.GaussianBlur(30))
    img.alpha_composite(lay)
    d = ImageDraw.Draw(img)
    for y in range(30, H, 60):  # faint dot grid
        for x in range(30, W, 60):
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(255, 255, 255, 18))
    return np.asarray(img.convert("RGB"))


GRAIN = [cv2.resize(np.random.default_rng(i).normal(0, 6, (H // 2, W // 2)).astype(np.float32), (W, H),
                    interpolation=cv2.INTER_NEAREST) for i in range(6)]

# ---------------------------------------------------------------- UI pieces
AV_COLS = [PINK, CYAN, LIME, (255, 170, 60), (140, 110, 255), (255, 90, 90)]


def avatar(name, size=74, col=None):
    col = col or AV_COLS[sum(map(ord, name)) % len(AV_COLS)]
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, size - 1, size - 1], fill=col + (255,))
    f = F_CAP(int(size * 0.45))
    ch = name.strip("@")[0].upper()
    w_, h_, b = text_size(f, ch)
    d.text(((size - w_) / 2 - b[0], (size - h_) / 2 - b[1]), ch, font=f, fill=INK)
    return img


def heart(size, col=PINK):
    return kr.heart_icon(size, col)


def comment(user, text, likes=None, w=760, dark=False, size=44):
    """TikTok-style comment bubble."""
    f_u, f_t = F_CAP(30), kr.font("InterXB", size)
    lines = kr.wrap(text, f_t, w - 170) if hasattr(kr, "wrap") else [text]
    asc, desc = f_t.getmetrics()
    lh = asc + desc + 6
    h = 64 + lh * len(lines) + 26
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bg, fg = (PANEL, WHITE) if dark else (WHITE, INK)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=34, fill=bg + (255,))
    img.alpha_composite(avatar(user), (22, 22))
    d.text((116, 20), user, font=f_u, fill=GREY)
    for i, l in enumerate(lines):
        d.text((116, 58 + i * lh), l, font=f_t, fill=fg)
    if likes:
        img.alpha_composite(heart(40, (200, 200, 210) if not dark else GREY).resize((36, 36)), (w - 66, 26))
        f_l = F_CAP(24)
        d.text((w - 48 - f_l.getlength(likes) / 2, 66), likes, font=f_l, fill=GREY)
    return kr.with_shadow(img, offset=(0, 12), blur=16, alpha=0.45)


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


def reply_sticker(user, question):
    """'Membalas komen @user' sticker shown on reply videos."""
    f1, f2 = F_CAP(30), kr.font("InterXB", 46)
    lines = wrap(question, f2, 640)
    w = 760
    h = 92 + 58 * len(lines) + 20
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=26, fill=WHITE + (255,))
    img.alpha_composite(avatar(user, 56), (20, 18))
    d.text((90, 30), f"Membalas komen {user}", font=f1, fill=GREY)
    for i, l in enumerate(lines):
        d.text((26, 88 + i * 58), l, font=f2, fill=INK)
    return kr.with_shadow(img, offset=(0, 10), blur=14, alpha=0.5)


def pill(text, bg, fg=INK, size=70, padx=34, pady=12, radius=None):
    f = F_ANTON(size)
    w_, h_, b = text_size(f, text)
    asc, desc = f.getmetrics()
    img = Image.new("RGBA", (w_ + padx * 2, asc + desc + pady * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, img.width - 1, img.height - 1], radius=radius or img.height // 2, fill=bg + (255,))
    d.text((padx - b[0], pady), text, font=f, fill=fg)
    return kr.with_shadow(img, offset=(0, 10), blur=14, alpha=0.45)


def neon_text(text, size, col, glow=True):
    f = F_ANTON(size)
    w_, h_, b = text_size(f, text)
    pad = 40
    img = Image.new("RGBA", (w_ + pad * 2, h_ + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((pad - b[0], pad - b[1]), text, font=f, fill=col + (255,))
    if glow:
        g = img.filter(ImageFilter.GaussianBlur(14))
        out = Image.new("RGBA", img.size, (0, 0, 0, 0))
        out.alpha_composite(g)
        out.alpha_composite(g)
        out.alpha_composite(img)
        return out
    return img


def thumb(title, col, views=None, w=300, h=470, play=True):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    g = np.linspace(0, 1, h)[:, None, None]
    grad = (np.array(col, np.float32) * (1 - g * 0.6) + np.array(BG0, np.float32) * g * 0.6) * np.ones((1, w, 1))
    base = Image.fromarray(grad.astype(np.uint8)).convert("RGBA")
    mk = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mk).rounded_rectangle([0, 0, w - 1, h - 1], radius=22, fill=255)
    img.paste(base, (0, 0), mk)
    f = F_ANTON(44)
    for i, l in enumerate(wrap(title, f, w - 40)[:3]):
        d.text((20, 24 + i * 52), l, font=f, fill=WHITE)
    if play:
        cx, cy = w / 2, h * 0.6
        d.ellipse([cx - 44, cy - 44, cx + 44, cy + 44], fill=(255, 255, 255, 220))
        d.polygon([(cx - 14, cy - 22), (cx - 14, cy + 22), (cx + 24, cy)], fill=INK + (255,))
    if views:
        fv = F_CAP(30)
        d.polygon([(18, h - 46), (18, h - 20), (40, h - 33)], fill=WHITE + (255,))
        d.text((50, h - 52), views, font=fv, fill=WHITE)
    return img


def empty_slot(w=300, h=470):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=22, outline=(255, 255, 255, 70), width=4)
    f = F_ANTON(90)
    w_, h_, b = text_size(f, "+")
    d.text(((w - w_) / 2 - b[0], (h - h_) / 2 - b[1]), "+", font=f, fill=(255, 255, 255, 70))
    return img


def bubble_icon(size, col=WHITE):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    d.rounded_rectangle([s * .08, s * .1, s * .92, s * .72], radius=int(s * .22), fill=col + (255,))
    d.polygon([(s * .3, s * .68), (s * .26, s * .92), (s * .5, s * .7)], fill=col + (255,))
    for k in range(3):
        x = s * (.3 + k * .2)
        d.ellipse([x - s * .05, s * .36, x + s * .05, s * .46], fill=INK + (255,))
    return img


def comment_button(count):
    w, h = 300, 130
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=65, fill=PANEL + (255,), outline=CYAN + (255,), width=4)
    img.alpha_composite(bubble_icon(90), (24, 22))
    d.text((128, 26), f"{count}", font=F_ANTON(70), fill=WHITE)
    return kr.with_shadow(img, offset=(0, 10), blur=16, alpha=0.5)


def composer(text, cursor_on, typing_dots=0.0):
    w, h = 900, 300
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=36, fill=PANEL + (255,), outline=(80, 82, 110, 255), width=3)
    d.text((34, 26), "Video baru", font=F_CAP(34), fill=GREY)
    f = kr.font("InterXB", 58)
    d.text((34, 96), text, font=f, fill=WHITE)
    if cursor_on:
        x = 34 + f.getlength(text) + 6
        d.rectangle([x, 100, x + 6, 168], fill=CYAN)
    if typing_dots:
        for k in range(3):
            ph = math.sin(typing_dots * 8 - k * 0.9)
            d.ellipse([40 + k * 34, 230 - 6 * ph, 62 + k * 34, 252 - 6 * ph], fill=GREY)
        d.text((150, 222), "sedang menaip...", font=F_CAP(28), fill=GREY)
    return kr.with_shadow(img, offset=(0, 12), blur=18, alpha=0.5)


def input_box(text, cursor_on):
    w, h = 940, 130
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=65, fill=WHITE + (255,), outline=PINK + (255,), width=6)
    img.alpha_composite(avatar("@anda", 80, LIME), (24, 25))
    f = kr.font("InterXB", 46)
    shown = text or "Tulis soalan anda..."
    d.text((124, 34), shown, font=f, fill=INK if text else GREY)
    if cursor_on and text:
        x = 124 + f.getlength(text) + 4
        d.rectangle([x, 38, x + 5, 96], fill=PINK)
    d.ellipse([w - 110, 20, w - 20, 110], fill=PINK)
    d.polygon([(w - 82, 44), (w - 82, 86), (w - 42, 65)], fill=WHITE)
    return kr.with_shadow(img, offset=(0, 12), blur=18, alpha=0.5)


def person(col, size=96):
    img = Image.new("RGBA", (size, int(size * 1.3)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = size * 0.24
    d.ellipse([size / 2 - r, 4, size / 2 + r, 4 + 2 * r], fill=col + (255,))
    d.rounded_rectangle([size * 0.1, 2 * r + 12, size * 0.9, img.height - 4], radius=int(size * 0.3), fill=col + (255,))
    return img


def arrow_down(size=220, col=PINK):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    d.polygon([(s * .35, 0), (s * .65, 0), (s * .65, s * .55), (s * .9, s * .55), (s * .5, s), (s * .1, s * .55),
               (s * .35, s * .55)], fill=col + (255,))
    g = img.filter(ImageFilter.GaussianBlur(12))
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.alpha_composite(g)
    out.alpha_composite(img)
    return out


# ---------------------------------------------------------------- assets
QUESTIONS = [("@aina_bakery", "Berapa harga set ni?", PINK),
             ("@hafiz.kl", "Boleh pos ke Sabah?", CYAN),
             ("@mira_hijab", "Apa beza produk ni dengan yang lain?", LIME)]
RAIN = [("@sya", "nak tanya, ada saiz XL?"), ("@amir", "cara order macam mana?"), ("@nurul", "COD boleh?"),
        ("@farah", "tahan berapa lama?"), ("@zack", "ada warna lain?"), ("@ika", "bila restock??"),
        ("@danish", "sesuai untuk budak?"), ("@lia", "ada promo tak?")]
C = {
    "rain": [comment(u, q, likes=str(3 + i * 7), w=620, size=38) for i, (u, q) in enumerate(RAIN)],
    "q": [comment(u, q, likes="128", w=820) for u, q, _ in QUESTIONS],
    "plus": neon_text("+1 VIDEO", 120, LIME),
    "rule": pill("1 SOALAN = 1 VIDEO", PINK, WHITE, 80),
    "thumbs": [thumb(q.replace("?", "?"), col, views=v) for (_, q, col), v in zip(QUESTIONS, ["12.4K", "8.1K", "21K"])],
    "slot": empty_slot(),
    "reply": reply_sticker("@aina_bakery", "Berapa harga set ni?"),
    "thanks": comment("@aina_bakery", "Terima kasih bos!! Terus order", likes="56", w=800),
    "tenggelam": neon_text("TENGGELAM...", 110, (120, 130, 170), glow=False),
    "content": pill("KOMEN  →  CONTENT", LIME, INK, 84),
    "ada": neon_text("ADA SOALAN?", 150, PINK),
    "next": pill("▶  VIDEO SETERUSNYA?", CYAN, INK, 64),
    "arrow": arrow_down(),
    "q_mark": neon_text("?", 200, PINK),
    "views_lbl": pill("TONTONAN", PANEL, WHITE, 46),
}
ICONS = [person(c) for c in [PINK, CYAN, LIME, (255, 170, 60), (140, 110, 255), WHITE]]
HEART = heart(90)

# ---------------------------------------------------------------- timeline
CUTS = [5.12, 8.42, 16.6, 23.66, 27.36, 31.55]
BGS = {0.0: make_bg(1, (40, 16, 50)), 5.12: make_bg(2, (12, 40, 60)), 8.42: make_bg(3, (30, 20, 60)),
       16.6: make_bg(4, (55, 14, 40)), 23.66: make_bg(5, (60, 20, 50)), 27.36: make_bg(6, (10, 30, 50)),
       31.55: make_bg(7, (50, 12, 45))}
PUNCHES = [1.88, 6.55, 9.58, 11.98, 15.24, 21.03, 30.05, 33.21]
GLITCH = [0.05, 1.88, 9.58, 11.98, 15.24, 30.05]


def scene_start(t):
    return max([0.0] + [c for c in CUTS if c <= t])


# (start, end, text, VO end) — CAPS words get the neon marker
CAPS = [
    (0.05, 1.7, "Tak tahu nak buat VIDEO apa?", 1.42),
    (1.85, 2.95, "JAWAPANNYA...", 2.77),
    (2.95, 5.12, "ada dalam ruangan KOMEN anda.", 4.83),
    (5.2, 6.5, "Setiap SOALAN pelanggan,", 6.5),
    (6.5, 8.42, "adalah satu IDEA VIDEO.", 8.12),
    (8.5, 9.5, "\"Berapa harga?\"", 9.31),
    (9.55, 10.6, "SATU VIDEO.", 10.31),
    (10.65, 11.9, "\"Boleh pos ke Sabah?\"", 11.77),
    (11.95, 13.1, "SATU VIDEO.", 12.8),
    (13.15, 15.2, "\"Apa beza produk ni dengan yang lain?\"", 15.05),
    (15.22, 16.6, "SATU LAGI VIDEO.", 16.36),
    (16.7, 18.65, "Bila anda jawab dalam bentuk video,", 18.58),
    (18.65, 20.95, "bukan SEORANG je yang dapat jawapan.", 20.7),
    (21.0, 23.66, "RAMAI LAGI yang ada soalan sama, pun dapat.", 23.49),
    (23.8, 25.55, "Dan pelanggan rasa DIHARGAI,", 25.5),
    (25.55, 27.36, "sebab soalan dia dijawab.", 27.21),
    (27.45, 30.0, "Jadi, jangan biar komen tu TENGGELAM.", 29.83),
    (30.0, 31.55, "Tukarkan jadi CONTENT.", 31.33),
    (31.65, 33.15, "KOMEN soalan anda di bawah,", 33.06),
    (33.15, DUR, "mungkin itu VIDEO saya yang SETERUSNYA!", 35.47),
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


def draw_caption(c, t, y=1650):
    for s, e, words, times in CAP_DATA:
        if not (s - 0.02 <= t < e):
            continue
        f = F_CAP(70)
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
        lh = asc + desc + 12
        widths = [sum(f.getlength(w_) for w_ in l) + space * (len(l) - 1) for l in lines]
        bw, bh = int(max(widths)) + 70, lh * len(lines) + 34
        strip = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        d = ImageDraw.Draw(strip)
        d.rounded_rectangle([0, 0, bw - 1, bh - 1], radius=28, fill=(10, 10, 18, 200))
        active = max([i for i, tt in enumerate(times) if tt <= t], default=-1)
        idx = 0
        for li, l in enumerate(lines):
            x = (bw - widths[li]) / 2
            y0 = 16 + li * lh
            for w_ in l:
                wl = f.getlength(w_)
                if t >= times[idx]:
                    k = ease_back((t - times[idx]) / 0.16)
                    yy = y0 + 16 * (1 - k)
                    if is_key(w_):
                        d.rounded_rectangle([x - 8, y0 + 6, x + wl + 8, y0 + lh - 6], radius=12, fill=PINK + (255,))
                        d.text((x, yy), w_, font=f, fill=WHITE)
                    else:
                        d.text((x, yy), w_, font=f, fill=CYAN if idx == active else WHITE)
                x += wl + space
                idx += 1
        k = ease_out((t - s + 0.02) / 0.18)
        place(c, strip, W / 2, y + 26 * (1 - k), alpha=k * clamp((e - t) / 0.1))


# ---------------------------------------------------------------- helpers
def fly(c, spr, t, t0, dur, p0, p1, s0=1.0, s1=1.0, r0=0.0, r1=0.0):
    """Move a sprite along an arc from p0 to p1 between t0 and t0+dur (holds at p1 after)."""
    if t < t0:
        return
    u = ease_inout((t - t0) / dur)
    x = p0[0] + (p1[0] - p0[0]) * u
    y = p0[1] + (p1[1] - p0[1]) * u - 160 * math.sin(math.pi * u)
    place(c, spr, x, y, scale=s0 + (s1 - s0) * u, rot=r0 + (r1 - r0) * u)


def slam(c, spr, t, t0, cx, cy, rot=0.0, t1=None):
    if t < t0 or (t1 is not None and t > t1 + 0.2):
        return
    k = clamp((t - t0) / 0.14)
    a = k * (1 - clamp((t - t1) / 0.2) if t1 is not None and t > t1 else 1)
    place(c, spr, cx, cy, scale=1.9 - 0.9 * ease_out(k), rot=rot, alpha=a)


def grid_slots(c, t, filled_at, x0=210, y=360, sc=0.62, show_from=8.45):
    """Row of three profile-grid slots; slot k shows its thumbnail once filled_at[k] has passed."""
    if t < show_from:
        return
    a = clamp((t - show_from) / 0.25)
    for k in range(3):
        x = x0 + k * 330 * 1.0
        ft = filled_at[k]
        if ft is not None and t >= ft:
            kk = ease_back((t - ft) / 0.3)
            place(c, C["thumbs"][k], x, y, scale=sc * kk, alpha=a)
        else:
            place(c, C["slot"], x, y, scale=sc, alpha=a)


# ---------------------------------------------------------------- scenes
def world(t):
    s0 = scene_start(t)
    c = Image.fromarray(BGS[s0]).convert("RGBA")

    if s0 == 0.0:  # hook
        who = "keliru" if t < 1.86 else "sinis"
        t0 = 0.0 if who == "keliru" else 1.86
        presenter_full(c, t, who, t0, 560)
        if t < 1.86:
            blink = int(t * 3) % 2 == 0
            k = ease_back((t - 0.1) / 0.4)
            place(c, composer("", blink, typing_dots=t), 540, 360, scale=max(0.01, k))
            if t > 0.8:
                place(c, C["q_mark"], 900, 640, scale=ease_back((t - 0.8) / 0.3), rot=12 + 6 * math.sin(t * 6))
        else:
            place(c, comment_button(int(248 + max(0, t - 3.0) * 160)), 760, 260,
                  scale=ease_back((t - 2.9) / 0.35) if t >= 2.9 else 0.01)
            if t >= 3.3:  # comments pour out of the button
                for j, spr in enumerate(C["rain"]):
                    t0j = 3.3 + j * 0.2
                    if t < t0j:
                        continue
                    u = ease_out((t - t0j) / 0.45)
                    tx = [250, 640, 330, 800, 210, 560, 870, 420][j]
                    ty = [400, 380, 520, 520, 650, 640, 670, 770][j]
                    x, y = 760 + (tx - 760) * u, 260 + (ty - 260) * u + 6 * math.sin(t * 3 + j)
                    place(c, spr, x, y, scale=0.3 + 0.32 * u, rot=(j % 3 - 1) * 5)
    elif s0 == 5.12:  # every question = a video idea
        presenter_head(c, t, "tunjuk", 790, 1260, 0.62, 5.2, rot=4)
        q = C["q"][0]
        if t < 6.55:
            place(c, q, 540, 520, scale=ease_back((t - 5.3) / 0.35) if t >= 5.3 else 0.01, rot=-2)
        else:  # fly into a thumbnail
            u = clamp((t - 6.55) / 0.5)
            if u < 1:
                fly(c, q, t, 6.55, 0.5, (540, 520), (270, 520), 1.0, 0.3, -2, 0)
            place(c, C["thumbs"][0], 270, 560, scale=0.85 * ease_back((t - 6.95) / 0.35) if t >= 6.95 else 0.01,
                  rot=-4)
        if t >= 7.2:
            place(c, C["rule"], 540, 1000 if t < 7.2 else 1000, scale=ease_back((t - 7.2) / 0.3), rot=-3)
    elif s0 == 8.42:  # rapid Q&A, grid fills
        grid_slots(c, t, [9.95, 12.35, 15.6])
        presenter_head(c, t, "fikir", 300, 1280, 0.55, 8.5, rot=-4)
        rounds = [(8.54, 9.58, 10.6), (10.68, 11.98, 13.1), (13.18, 15.24, 16.6)]
        for k, (qa, plus, end) in enumerate(rounds):
            if qa <= t < end:
                q = C["q"][k]
                if t < plus + 0.35:
                    place(c, q, 540, 840, scale=ease_back((t - qa) / 0.3), rot=(-2, 2, -1)[k])
                else:
                    fly(c, q, t, plus + 0.35, 0.3, (540, 840), (210 + k * 330, 360), 1.0, 0.25)
                slam(c, C["plus"], t, plus, 700, 1130, rot=-8, t1=end - 0.3)
        if t >= 9.95:
            n = (t >= 9.95) + (t >= 12.35) + (t >= 15.6)
            place(c, kr.with_shadow(neon_text(f"{n} SOALAN = {n} VIDEO", 70, WHITE, glow=False), blur=8), 540, 690)
    elif s0 == 16.6:  # one answer reaches many
        presenter_head(c, t, "terkejut", 800, 1270, 0.6, 16.7, rot=5)
        th = thumb("BERAPA HARGA SET NI?", PINK, views=None, w=360, h=560)
        place(c, th, 300, 560, scale=ease_back((t - 16.75) / 0.35) if t >= 16.75 else 0.01, rot=-3)
        if t >= 16.9:  # playback bar
            d = ImageDraw.Draw(c)
            p = clamp((t - 16.9) / 6.5)
            d.rounded_rectangle([130, 860, 470, 872], radius=6, fill=(255, 255, 255, 80))
            d.rounded_rectangle([130, 860, 130 + 340 * p, 872], radius=6, fill=PINK)
        if t >= 18.7:  # one person, then many
            n = 1 if t < 21.03 else 1 + int(clamp((t - 21.03) / 2.0) * 16)
            for k in range(n):
                if k == 0:
                    x, y = 760, 640
                else:
                    x = 100 + ((k - 1) % 4) * 140
                    y = 1000 + ((k - 1) // 4) * 150
                kr.pop(c, ICONS[k % len(ICONS)], t, 18.7 if k == 0 else 21.03 + (k - 1) * 2.0 / 16, x, y, scale=0.85)
        if t >= 21.0:
            v = int(1 + 2399 * ease_out((t - 21.05) / 2.2))
            lbl = f"{v / 1000:.1f}K" if v >= 1000 else str(v)
            place(c, kr.with_shadow(neon_text(lbl, 130, LIME), blur=6), 760, 330, scale=ease_back((t - 21.0) / 0.3))
            place(c, C["views_lbl"], 760, 460, scale=ease_back((t - 21.1) / 0.3))
    elif s0 == 23.66:  # appreciated
        presenter_head(c, t, "senyum", 540, 1150, 0.82, 23.75)
        kr.pop(c, C["reply"], t, 23.9, 540, 330, rot=-2)
        for j in range(14):  # hearts floating up
            t0j = 24.2 + j * 0.22
            if t < t0j:
                continue
            u = t - t0j
            x = 140 + (j * 97) % 800 + 30 * math.sin(u * 3 + j)
            y = 1500 - 420 * u
            if y > 150:
                place(c, HEART, x, y, scale=0.5 + 0.3 * ((j * 37) % 10) / 10, rot=10 * math.sin(u * 4 + j),
                      alpha=clamp(1 - u / 3.5))
        kr.pop(c, C["thanks"], t, 25.6, 540, 640, rot=2)
    elif s0 == 27.36:  # don't let comments sink -> turn them into content
        presenter_head(c, t, "sinis", 800, 1300, 0.55, 27.45, rot=-4)
        if t < 30.05:
            for j, spr in enumerate(C["rain"][:6]):
                u = clamp((t - 27.5 - j * 0.12) / 2.4)
                y = 300 + j * 120 + 700 * ease_inout(u)
                place(c, spr, 400 + (j % 2) * 120, y, scale=0.62, rot=(j % 3 - 1) * 4, alpha=1 - 0.75 * u)
            if t >= 28.6:
                place(c, C["tenggelam"], 400, 1250, alpha=clamp((t - 28.6) / 0.3))
            # dark water rising
            lvl = 1500 - 500 * ease_out(clamp((t - 27.5) / 2.4))
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(ov).rectangle([0, lvl, W, H], fill=(5, 8, 30, 150))
            c.alpha_composite(ov)
        else:  # pulled back up, turned into thumbnails
            for j in range(6):
                u = clamp((t - 30.1 - j * 0.1) / 0.6)
                x0, y0 = 400 + (j % 2) * 120, 1100 + j * 40
                x1, y1 = 200 + (j % 3) * 340, 330 + (j // 3) * 330
                if u < 1:
                    place(c, C["rain"][j], x0 + (x1 - x0) * ease_inout(u), y0 + (y1 - y0) * ease_inout(u),
                          scale=0.62 - 0.35 * u)
                else:
                    th = thumb(RAIN[j][1].upper(), AV_COLS[j], views=f"{(j + 2) * 1.3:.1f}K", w=300, h=300)
                    place(c, th, x1, y1, scale=ease_back((t - 30.7 - j * 0.1) / 0.3) * 0.95)
            kr.pop(c, C["content"], t, 30.3, 470, 1010, rot=-3)
    else:  # CTA
        presenter_head(c, t, "senyum", 540, 760, 0.78, 31.6)
        place(c, C["ada"], 540, 210, scale=ease_back((t - 31.7) / 0.35) if t >= 31.7 else 0.01, rot=-3)
        if t >= 32.0:
            bob = 26 * math.sin((t - 32.0) * 7)
            place(c, C["arrow"], 900, 1060 + bob, scale=0.7 * ease_back((t - 32.0) / 0.3))
            place(c, C["arrow"], 180, 1060 - bob, scale=0.55 * ease_back((t - 32.15) / 0.3))
        if t >= 32.2:
            msg = "Macam mana nak mula?"
            n = int(clamp((t - 32.5) / 1.4) * len(msg))
            place(c, input_box(msg[:n], int(t * 3) % 2 == 0), 540, 1290, scale=ease_back((t - 32.2) / 0.35))
        if t >= 33.25:
            pulse = 1 + 0.05 * max(0.0, math.sin((t - 33.25) * 6))
            place(c, C["next"], 540, 1460, scale=pulse * ease_back((t - 33.25) / 0.35))
    return c


# ---------------------------------------------------------------- camera, swipe, glitch
def camera_zoom(t):
    s0 = scene_start(t)
    nxt = [x for x in CUTS if x > t]
    s1 = nxt[0] if nxt else DUR
    z = 1.0 + 0.05 * ease_inout((t - s0) / (s1 - s0))
    for pt in PUNCHES:
        dt = t - pt
        if 0 <= dt < 0.6:
            z *= 1 + 0.07 * (dt / 0.06 if dt < 0.06 else math.exp(-(dt - 0.06) * 7))
    return z


def swipe_offset(t):
    for ct in CUTS:
        if ct - 0.22 <= t < ct:
            return -H * ease_inout((t - (ct - 0.22)) / 0.22) * 0.55, True
        if ct <= t < ct + 0.22:
            return H * (1 - ease_out((t - ct) / 0.22)) * 0.55, True
    return 0.0, False


def frame(i):
    t = i / FPS
    arr = np.asarray(world(t).convert("RGB"))
    z = camera_zoom(t)
    fx, fy = W / 2, H * 0.45
    M = np.float32([[z, 0, fx - z * fx], [0, z, fy - z * fy]])
    dy, swiping = swipe_offset(t)
    M[1, 2] += dy
    arr = cv2.warpAffine(arr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=BG0)
    if swiping:
        arr = cv2.blur(arr, (1, 61))
    arr = arr.astype(np.float32) + GRAIN[i % len(GRAIN)][..., None] * 0.5
    for g in GLITCH:  # RGB split for a few frames
        if 0 <= t - g < 0.12:
            sh = int(18 * (1 - (t - g) / 0.12)) + 2
            arr[..., 0] = np.roll(arr[..., 0], sh, axis=1)
            arr[..., 2] = np.roll(arr[..., 2], -sh, axis=1)
    c = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    draw_caption(c, t)
    rgb = np.asarray(c.convert("RGB"))
    if t > DUR - 0.35:
        rgb = (rgb.astype(np.float32) * clamp((DUR - t) / 0.35)).astype(np.uint8)
    return rgb


if __name__ == "__main__":
    if len(sys.argv) > 2:
        for ts in sys.argv[2:]:
            Image.fromarray(frame(int(float(ts) * FPS))).save(f"{WD}/k3_{ts}.jpg", quality=85)
    else:
        out = sys.stdout.buffer
        for i in range(N):
            out.write(frame(i).tobytes())
            if i % 100 == 0:
                print(f"frame {i}/{N}", file=sys.stderr, flush=True)
