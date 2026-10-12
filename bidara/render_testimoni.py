"""Video motion graphic testimoni Jus Bidara Hitam (30 saat, 1080x1920, 30fps).

Guna screenshot komen sebenar dari assets/strips (nama pelanggan dikaburkan).
Jalankan:  python3 render_testimoni.py  ->  ../output/bidara_testimoni_30s.mp4
"""
import glob, math, os, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "..", "output", "bidara_testimoni_30s.mp4")
W, H, FPS, DUR = 1080, 1920, 30, 30.0
GOLD, GOLD2, WHITE, DARK = (230, 184, 92), (255, 222, 140), (255, 255, 255), (14, 10, 8)

_fc = {}
def F(name, size):
    k = (name, size)
    if k not in _fc:
        path = os.path.join(A, "fonts", name + ".ttf") if name != "Dejavu" else "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]

# ---------- easing ----------
clamp = lambda x: max(0.0, min(1.0, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_in(x): x = clamp(x); return x ** 3
def back_out(x, s=1.6):
    x = clamp(x); x -= 1; return x * x * ((s + 1) * x + s) + 1
def prog(t, a, b): return clamp((t - a) / (b - a))

# ---------- drawing helpers ----------
def text_img(txt, font, fill, stroke=0, stroke_fill=(0, 0, 0), shadow=True):
    l, t, r, b = font.getbbox(txt, stroke_width=stroke)
    pad = 30
    im = Image.new("RGBA", (r - l + pad * 2, b - t + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((pad - l + 4, pad - t + 8), txt, font=font, fill=(0, 0, 0, 200), stroke_width=stroke, stroke_fill=(0, 0, 0, 200))
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(10)))
        d = ImageDraw.Draw(im)
    d.text((pad - l, pad - t), txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return im

def fit_font(txt, name, size, maxw):
    while size > 20 and F(name, size).getlength(txt) > maxw:
        size -= 4
    return F(name, size)

def paste(base, im, cx, cy, alpha=1.0, scale=1.0, rot=0.0):
    if alpha <= 0.01: return
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1:
        a = im.getchannel("A").point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def rounded(im, r, border=0, border_col=GOLD):
    im = im.convert("RGBA")
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, fill=255)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0)); out.paste(im, (0, 0), m)
    if border:
        ImageDraw.Draw(out).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, outline=border_col + (255,), width=border)
    return out

def with_shadow(im, blur=24, off=14, op=170):
    pad = blur * 2
    out = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, op), (pad, pad + off, pad + im.width, pad + off + im.height), im.getchannel("A"))
    out = Image.alpha_composite(out, sh.filter(ImageFilter.GaussianBlur(blur)))
    out.alpha_composite(im, (pad, pad))
    return out

def pill(txt, font, bg, fg, padx=34, pady=16):
    w = int(font.getlength(txt)); l, t, r, b = font.getbbox(txt)
    im = Image.new("RGBA", (w + padx * 2, (b - t) + pady * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), im.height // 2, fill=bg)
    d.text((padx - l, pady - t), txt, font=font, fill=fg)
    return im

def stars(n=5, size=44, col=GOLD2):
    f = F("Dejavu", size)
    return text_img("★" * n, f, col + (255,), shadow=False)

# ---------- backgrounds ----------
def radial_bg(c_in, c_out):
    y, x = np.mgrid[0:H, 0:W]
    r = np.sqrt(((x - W / 2) / W) ** 2 + ((y - H * 0.42) / H) ** 2) / 0.75
    r = np.clip(r, 0, 1)[..., None]
    arr = (np.array(c_in) * (1 - r) + np.array(c_out) * r).astype(np.uint8)
    return Image.fromarray(arr, "RGB").convert("RGBA")

BG_DARK = radial_bg((58, 36, 14), (6, 4, 3))
bottle_photo = Image.open(os.path.join(A, "botol-tangan.jpg")).convert("RGB")
_bp = bottle_photo.resize((int(W * 1.25), int(W * 1.25 * bottle_photo.height / bottle_photo.width)))
_bp = _bp.filter(ImageFilter.GaussianBlur(28))
_bp = Image.blend(_bp, Image.new("RGB", _bp.size, (10, 6, 3)), 0.68)
BG_BLUR = _bp.convert("RGBA")

def blur_bg(t, t0, t1):
    k = prog(t, t0, t1); s = 1.0 + 0.08 * k
    w, h = int(W * s), int(H * s)
    im = BG_BLUR.resize((w, int(BG_BLUR.height * w / BG_BLUR.width)))
    x0 = (im.width - W) // 2; y0 = int((im.height - H) * (0.3 + 0.2 * k))
    return im.crop((x0, y0, x0 + W, y0 + H))

# gold dust particles
random.seed(7)
DUST = [(random.random() * W, random.random() * H, random.uniform(1.5, 4.5), random.uniform(20, 60), random.random() * 6.28) for _ in range(70)]
def draw_dust(base, t, op=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for x, y, r, sp, ph in DUST:
        yy = (y - sp * t) % H; xx = x + 14 * math.sin(t * 0.8 + ph)
        a = int((120 + 100 * math.sin(t * 2 + ph)) * op)
        d.ellipse((xx - r, yy - r, xx + r, yy + r), fill=GOLD2 + (max(0, a),))
    base.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1.2)))

# ---------- testimonial strips (nama dikaburkan) ----------
def strip(idx, covers):
    im = Image.open(glob.glob(os.path.join(A, "strips", "*_%02d.png" % idx))[0]).convert("RGBA")
    for (y0, y1, xf) in covers:
        box = (0, y0, int(im.width * xf), y1)
        im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(14)), box[:2])
        tag = pill("Pelanggan", F("Mont800", 30), (20, 12, 6, 230), GOLD2 + (255,), padx=22, pady=10)
        im.alpha_composite(tag, (16, int((y0 + y1) / 2 - tag.height / 2)))
    return im

TOP = (8, 62, 0.5)
HERO = [  # (strip, covers, baris kecil, baris besar)
    (12, [(8, 64, 0.32)], "21 TAHUN MINUM", "KINI BEBAS"),
    (7,  [(6, 58, 0.30)], "LEPAS 2 BOTOL", "HAMPIR 2 BULAN BEBAS"),
    (0,  [(4, 58, 0.30)], "AMAL 3 BOTOL", "32 HARI TAK MINUM"),
    (8,  [(6, 60, 0.42), (178, 226, 0.55)], "KATA SEORANG ISTERI", "SUAMI TAK BARAN DAH"),
    (26, [(10, 66, 0.50)], "KATA SEORANG IBU", "ANAK DAH BEBAS"),
    (13, [(6, 62, 0.40), (212, 260, 0.52)], "18 TAHUN MINUM", "KINI TAK MENCARI LAGI"),
]
HERO_IM = []
for idx, cov, small, big in HERO:
    s = strip(idx, cov)
    s = s.resize((960, int(s.height * 960 / s.width)), Image.LANCZOS)
    HERO_IM.append((with_shadow(rounded(s, 28, border=5)), small, big))

# wall: komen pendek lain (bukan termasuk komen "urin")
WALL_IDS = [1, 2, 3, 5, 9, 10, 11, 14, 16, 17, 18, 19, 21, 22, 23, 24, 25, 27, 28, 30, 31, 6, 20]
WALL = []
for i in WALL_IDS:
    extra = {16: [150], 19: [118], 20: [150], 25: [145, 290]}.get(i, [])
    s = strip(i, [TOP] + [(TOP[0] + o, TOP[1] + o, 0.6) for o in extra])
    s = s.resize((500, int(s.height * 500 / s.width)), Image.LANCZOS)
    WALL.append(rounded(s, 16, border=3))

# produk
three = Image.open(os.path.join(A, "poster-gemini.jpg")).convert("RGBA").crop((115, 700, 465, 1080))
m = Image.new("L", three.size, 0); ImageDraw.Draw(m).ellipse((10, -40, three.width - 10, three.height - 30), fill=255)
three.putalpha(m.filter(ImageFilter.GaussianBlur(42)))
THREE = three.resize((int(three.width * 2.1), int(three.height * 2.1)), Image.LANCZOS)
THREE_SM = THREE.resize((int(THREE.width * 0.62), int(THREE.height * 0.62)), Image.LANCZOS)
hand = bottle_photo.crop((230, 180, 930, 1560))
HAND = with_shadow(rounded(hand.resize((440, int(1380 * 440 / 700)), Image.LANCZOS), 36, border=6))

# ---------- scenes ----------
T = dict(s1=0.0, s2=3.0, s3=5.6, card=2.8, s4=22.4, s5=25.0)

def scene1(t):
    f = BG_DARK.copy(); draw_dust(f, t)
    out = ease_in(prog(t, 2.65, 3.0))
    lines = [("DAH BERTAHUN", WHITE, 0.10), ("NAK BERHENTI,", WHITE, 0.75), ("TAPI TAK JADI-JADI?", GOLD2, 1.35)]
    for i, (txt, col, st) in enumerate(lines):
        k = prog(t, st, st + 0.45)
        if k <= 0: continue
        font = fit_font(txt, "Anton", 150 if i < 2 else 136, 960)
        im = text_img(txt, font, col + (255,))
        y = 700 + i * 190 - 120 * out
        if i == 2:  # highlight bar wipe
            bar = Image.new("RGBA", (int((im.width - 20) * ease_out(prog(t, st + 0.2, st + 0.7))), 20), GOLD + (230,))
            f.alpha_composite(bar, (int(W / 2 - (im.width - 20) / 2), int(y + im.height / 2 - 34)))
        paste(f, im, W / 2, y, alpha=k * (1 - out), scale=1.25 - 0.25 * back_out(k))
    sub = text_img("Ramai dah cuba macam-macam cara…", F("Mont600", 42), (230, 220, 200, 255))
    paste(f, sub, W / 2, 1260 - 60 * out, alpha=prog(t, 1.9, 2.3) * (1 - out))
    return f

def scene2(t):
    lt = t - T["s2"]
    f = blur_bg(t, T["s2"], T["s3"]); draw_dust(f, t, 0.7)
    a_in = ease_out(prog(lt, 0, 0.4))
    paste(f, text_img("INI KATA MEREKA", F("Anton", 128), WHITE + (255,)), W / 2, 330 - 40 * (1 - a_in), alpha=a_in)
    paste(f, text_img("yang dah amal", F("Playfair700", 64), (235, 225, 205, 255)), W / 2, 470, alpha=ease_out(prog(lt, 0.25, 0.6)))
    k = ease_out(prog(lt, 0.45, 0.95))
    brand = text_img("Jus Bidara Hitam", F("Playfair900", 118), GOLD2 + (255,))
    paste(f, brand, W / 2, 610, alpha=k, scale=0.85 + 0.15 * back_out(k))
    kh = back_out(prog(lt, 0.7, 1.3))
    paste(f, HAND, W / 2, 1290 + 500 * (1 - kh) + 10 * math.sin(lt * 2), alpha=clamp(kh * 1.5))
    return f

def scene3(t):
    lt = t - T["s3"]; i = min(5, int(lt // T["card"])); u = lt - i * T["card"]
    f = blur_bg(t, T["s3"], T["s4"]); draw_dust(f, t, 0.6)
    # header tetap
    hk = ease_out(prog(lt, 0, 0.4))
    paste(f, stars(5, 46), W / 2, 150, alpha=hk)
    paste(f, text_img("KOMEN SEBENAR PELANGGAN", F("Mont800", 38), GOLD + (255,)), W / 2, 215, alpha=hk)
    # titik progress
    d = ImageDraw.Draw(f)
    for j in range(6):
        cx = W / 2 - 75 + j * 30
        d.ellipse((cx - 7, 268, cx + 7, 282), fill=(GOLD2 + (255,)) if j <= i else (255, 255, 255, 70))
    card, small, big = HERO_IM[i]
    kin = back_out(prog(u, 0.0, 0.55), 1.2); kout = ease_in(prog(u, T["card"] - 0.3, T["card"]))
    last = i == 5
    x = W / 2 + 1100 * (1 - kin) - (0 if last else 1150 * kout)
    paste(f, card, x, 1150, rot=-3 * (1 - kin), alpha=1 - (kout if last else 0))
    # botol di bawah
    paste(f, THREE_SM, W / 2, 1640 + 6 * math.sin(t * 2), alpha=0.95 * hk)
    # ayat kunci
    k1 = ease_out(prog(u, 0.25, 0.6)); k2 = prog(u, 0.45, 0.9)
    fade = 1 - (ease_in(prog(u, T["card"] - 0.3, T["card"])))
    paste(f, text_img(small, F("Mont800", 50), WHITE + (255,)), W / 2, 470, alpha=k1 * fade)
    bigf = fit_font(big, "Anton", 132, 980)
    paste(f, text_img(big, bigf, GOLD2 + (255,)), W / 2, 610, alpha=clamp(k2 * 2) * fade, scale=1.3 - 0.3 * back_out(k2))
    return f

def scene4(t):
    lt = t - T["s4"]
    f = BG_DARK.copy()
    cols = [WALL[0::2], WALL[1::2]]
    for c, items in enumerate(cols):
        x = 290 + c * 520; y = 2000 - lt * 900 * (1 if c == 0 else 0.8) - c * 180
        for im in items:
            if -400 < y < H + 400:
                f.alpha_composite(im, (int(x - im.width / 2), int(y)))
            y += im.height + 26
    shade = Image.new("RGBA", (W, H), (8, 5, 3, int(150 * ease_out(prog(lt, 0.3, 0.9)))))
    f.alpha_composite(shade)
    k = back_out(prog(lt, 0.35, 0.85))
    paste(f, text_img("DAN RAMAI LAGI…", F("Anton", 140), WHITE + (255,)), W / 2, 860, alpha=clamp(k * 1.4), scale=0.7 + 0.3 * k)
    k2 = ease_out(prog(lt, 0.8, 1.2))
    paste(f, pill("30+ komen pelanggan", F("Mont800", 48), GOLD + (255,), DARK + (255,)), W / 2, 1040, alpha=k2, scale=0.8 + 0.2 * k2)
    out = ease_in(prog(lt, 2.3, 2.6))
    if out: f.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * out))))
    return f

def scene5(t):
    lt = t - T["s5"]
    f = BG_DARK.copy()
    # sinar cahaya
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse((140, 520, 940, 1240), fill=GOLD + (int(90 * ease_out(prog(lt, 0, 0.8))),))
    f.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120))); draw_dust(f, t, 0.8)
    k = ease_out(prog(lt, 0.0, 0.4))
    paste(f, pill("PAKEJ PALING RAMAI AMBIL", F("Mont800", 44), GOLD + (255,), DARK + (255,)), W / 2, 210 - 60 * (1 - k), alpha=k)
    kb = back_out(prog(lt, 0.2, 0.9))
    paste(f, THREE, W / 2, 820 + 8 * math.sin(lt * 2.2), alpha=clamp(kb * 1.5), scale=0.75 + 0.25 * kb)
    kp = back_out(prog(lt, 0.7, 1.15))
    row = Image.new("RGBA", (1000, 220), (0, 0, 0, 0))
    a = text_img("3 BOTOL ", F("Anton", 170), WHITE + (255,)); b = text_img("RM65", F("Anton", 170), GOLD2 + (255,))
    row = Image.new("RGBA", (a.width + b.width - 60, max(a.height, b.height)), (0, 0, 0, 0))
    row.alpha_composite(a, (0, 0)); row.alpha_composite(b, (a.width - 60, 0))
    paste(f, row, W / 2, 1300, alpha=clamp(kp * 1.4), scale=1.3 - 0.3 * kp)
    kf = ease_out(prog(lt, 1.1, 1.5))
    paste(f, pill("FREE POSTAGE SEMENANJUNG", F("Mont800", 46), (196, 30, 36, 255), WHITE + (255,)), W / 2, 1450, alpha=kf, scale=0.85 + 0.15 * kf)
    ks = ease_out(prog(lt, 1.5, 1.9))
    paste(f, text_img("1 Botol RM28   •   2 Botol RM50   (+ postage RM8)", F("Mont600", 36), (225, 215, 195, 255)), W / 2, 1545, alpha=ks)
    kc = ease_out(prog(lt, 1.9, 2.3)); pulse = 1 + 0.045 * math.sin(max(0, lt - 2.3) * 6)
    paste(f, with_shadow(pill("BALAS 'NAK' UNTUK ORDER", F("Mont800", 54), GOLD2 + (255,), DARK + (255,), padx=50, pady=26), 18, 8),
          W / 2, 1690, alpha=kc, scale=(0.8 + 0.2 * kc) * pulse)
    paste(f, text_img("Komen sebenar pelanggan. Keputusan berbeza mengikut individu.", F("Mont600", 26), (170, 160, 145, 255), shadow=False),
          W / 2, 1830, alpha=ks)
    return f

def frame(t):
    if t < T["s2"]: return scene1(t)
    if t < T["s3"]: return scene2(t)
    if t < T["s4"]: return scene3(t)
    if t < T["s5"]: return scene4(t)
    return scene5(t)

# ---------- audio: whoosh + ding (tiada muzik berhak cipta) ----------
SR = 44100
def make_audio(path):
    n = int(SR * DUR); a = np.zeros(n)
    rng = np.random.default_rng(1)
    def whoosh(t0, dur=0.45, vol=0.22):
        m = int(dur * SR); s = int(t0 * SR)
        noise = rng.standard_normal(m)
        k = np.linspace(0, 1, m)
        # low-pass ringkas yang bergerak (sweep)
        out = np.zeros(m); y = 0.0
        for i in range(m):
            alpha = 0.02 + 0.25 * math.sin(math.pi * k[i]) ** 2
            y += alpha * (noise[i] - y); out[i] = y
        env = np.sin(np.pi * k) ** 2
        a[s:s + m] += (out * env * vol * 3)[: max(0, min(m, n - s))]
    def ding(t0, f0=1318.5, vol=0.18):
        m = int(1.6 * SR); s = int(t0 * SR); tt = np.arange(m) / SR
        tone = (np.sin(2 * np.pi * f0 * tt) + 0.5 * np.sin(2 * np.pi * f0 * 2 * tt)) * np.exp(-tt * 3)
        a[s:s + m] += (tone * vol)[: max(0, min(m, n - s))]
    def boom(t0, vol=0.35):
        m = int(0.9 * SR); s = int(t0 * SR); tt = np.arange(m) / SR
        tone = np.sin(2 * np.pi * (55 + 40 * np.exp(-tt * 8)) * tt) * np.exp(-tt * 4)
        a[s:s + m] += (tone * vol)[: max(0, min(m, n - s))]
    for t0 in (0.08, 0.73, 1.33, 3.0): whoosh(t0)
    boom(1.35)
    for i in range(6): whoosh(T["s3"] + i * T["card"] - 0.05); ding(T["s3"] + i * T["card"] + 0.45, 1046.5, 0.08)
    whoosh(T["s4"], 0.8, 0.28); boom(T["s4"] + 0.4)
    whoosh(T["s5"]); boom(T["s5"] + 0.75, 0.4); ding(T["s5"] + 1.1); ding(T["s5"] + 1.95, 1568, 0.12)
    a = np.clip(a / max(1e-6, np.abs(a).max()) * 0.8, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((a * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    wav = OUT.replace(".mp4", ".wav"); make_audio(wav)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
           "-shortest", "-movflags", "+faststart", OUT]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    total = int(DUR * FPS)
    for i in range(total):
        p.stdin.write(frame(i / FPS).convert("RGB").tobytes())
        if i % 150 == 0: print(f"frame {i}/{total}", flush=True)
    p.stdin.close(); p.wait(); os.remove(wav)
    print("siap:", os.path.abspath(OUT))
