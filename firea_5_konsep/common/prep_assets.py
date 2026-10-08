"""Derived assets from the untouched source images in assets/src (1-10.jpg).

assets/cut/
  logo_alpha.png     Firea wordmark alpha (from 1.jpg)
  bottle.png         Celeste Musk bottle cut-out with its white sticker outline (from 6.jpg;
                     shape fitted as a rotated rounded rectangle because the headline sticker
                     touches the cap)
  photo_arm.jpg      9.jpg: user raising arm, holding product (hook, full-bleed)
  photo_bridge.jpg   7.jpg: long sleeves, outdoor (quiz 2)
  photo_climb.jpg    8.jpg: climbing + product (quiz 3)
  photo_mirror.jpg   5.jpg (= 10.jpg): morning routine (quiz 1)
  photo_ugc.jpg      4.jpg: real user holding product (reveal)
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = f"{ROOT}/assets/src", f"{ROOT}/assets/cut"
os.makedirs(OUT, exist_ok=True)

# ---- logo
im = Image.open(f"{SRC}/1.jpg").convert("RGB").crop((86, 22, 318, 130))
im = im.resize((im.width * 4, im.height * 4), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2))
a = np.asarray(im).astype(np.float32)
alpha = np.clip((np.clip((225 - a[..., 1]) / 185, 0, 1) - 0.08) / 0.84, 0, 1)
Image.fromarray((alpha * 255).astype(np.uint8), "L").save(f"{OUT}/logo_alpha.png")

# ---- bottle from 6.jpg
im = Image.open(f"{SRC}/6.jpg").convert("RGB")
a = np.asarray(im).astype(int)
white = (a[..., 0] > 240) & (a[..., 1] > 236) & (a[..., 2] > 236)
ex = Image.new("L", im.size, 0)  # headline sticker region
ImageDraw.Draw(ex).polygon([(238, 240), (720, 240), (720, 600), (284, 600), (264, 480), (247, 380)], fill=255)
white &= ~(np.asarray(ex) > 0)
lab, n = ndi.label(white)
comp = lab == (np.argmax(ndi.sum(white, lab, range(1, n + 1))) + 1)  # bottle outline + cap
# fit the straight left/right outline edges (rows below the sticker) -> tilt, centre line, width
rows = range(640, 980, 10)
lx = np.array([np.where(comp[y])[0].min() for y in rows], float)
rx = np.array([np.where(comp[y])[0].max() for y in rows], float)
yy = np.array(list(rows), float)
slope = (np.polyfit(yy, lx, 1)[0] + np.polyfit(yy, rx, 1)[0]) / 2
ax = np.array([slope, 1.0]) / np.hypot(slope, 1.0)  # long axis (downwards)
perp = np.array([ax[1], -ax[0]])
half_w = np.mean(rx - lx) / 2 * ax[1]
c = np.array([np.mean((lx + rx) / 2), yy.mean()])
ys, xs = np.where(comp)
P = np.stack([xs, ys], 1).astype(float)
u0, u1 = np.percentile((P - c) @ ax, [0.3, 99.7])
v0, v1 = -half_w - 2, half_w + 2
SS = 4
L, Wv = u1 - u0, v1 - v0
loc = Image.new("L", (int(Wv * SS) + 2, int(L * SS) + 2), 0)
ImageDraw.Draw(loc).rounded_rectangle((0, 0, Wv * SS, L * SS), int(Wv * 0.30 * SS), fill=255)
loc = loc.rotate(np.degrees(np.arctan2(ax[0], ax[1])), expand=True, resample=Image.BICUBIC)
cc = c + (v0 + v1) / 2 * perp + (u0 + u1) / 2 * ax
m = Image.new("L", (im.width * SS, im.height * SS), 0)
m.paste(loc, (int(cc[0] * SS - loc.width / 2), int(cc[1] * SS - loc.height / 2)))
m = m.resize(im.size, Image.LANCZOS)
ys, xs = np.where(np.asarray(m) > 10)
# the headline sticker is printed over the cap in the source, so redraw the (plain white) cap:
# a cylinder-shaded rounded shape in the bottle's own rotated frame, covering the cap only
CAP = 0.392  # cap height as a fraction of bottle length (cap/label seam)
cw, ch = int(Wv * SS), int(L * SS * CAP)
xn = np.linspace(0, 1, cw)
prof = 251 - 22 * xn ** 2.2 - 10 * (1 - xn) ** 6 + 4 * np.exp(-((xn - 0.22) / 0.08) ** 2)
capimg = np.repeat(np.repeat(prof[None, :, None], ch, 0), 3, 2) * np.array([1.0, 0.988, 0.99])
cap_a = Image.new("L", (cw, int(L * SS) + 2), 0)
ImageDraw.Draw(cap_a).rounded_rectangle((0, 0, Wv * SS, L * SS), int(Wv * 0.30 * SS), fill=255)
cap_a = cap_a.crop((0, 0, cw, ch)).filter(ImageFilter.GaussianBlur(3))
cap_rgba = Image.fromarray(np.clip(capimg, 0, 255).astype(np.uint8)).convert("RGBA")
cap_rgba.putalpha(cap_a)
full = Image.new("RGBA", (cw, int(L * SS) + 2), (0, 0, 0, 0))
full.paste(cap_rgba, (0, 0))
full = full.rotate(np.degrees(np.arctan2(ax[0], ax[1])), expand=True, resample=Image.BICUBIC)
layer = Image.new("RGBA", (im.width * SS, im.height * SS), (0, 0, 0, 0))
layer.paste(full, (int(cc[0] * SS - full.width / 2), int(cc[1] * SS - full.height / 2)))
layer = layer.resize(im.size, Image.LANCZOS)
im = im.convert("RGBA")
im.alpha_composite(layer)
im = im.convert("RGB")
rgba = im.copy()
rgba.putalpha(m)
rgba.crop((xs.min() - 6, ys.min() - 6, xs.max() + 6, ys.max() + 6)).save(f"{OUT}/bottle.png")

# ---- photos
crops = {
    "photo_arm": ("9.jpg", (0, 0, 720, 1280)),
    "photo_bridge": ("7.jpg", (60, 0, 560, 714)),
    "photo_climb": ("8.jpg", (540, 0, 1180, 714)),
    "photo_mirror": ("5.jpg", (360, 0, 1060, 714)),
    "photo_ugc": ("4.jpg", (40, 300, 680, 1180)),
}
for name, (f, box) in crops.items():
    Image.open(f"{SRC}/{f}").convert("RGB").crop(box).save(f"{OUT}/{name}.jpg", quality=95)
print("assets ready")
