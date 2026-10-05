"""Sediakan aset terbitan ke public/ daripada assets/original (fail asal tidak diubah).
Jalankan: .venv/bin/python scripts/prep_assets.py   (perlu: rembg, pillow, numpy)
"""
import numpy as np
from PIL import Image, ImageFilter
from rembg import remove, new_session

SRC = "assets/original"
OUT = "public"


def crop(name, box, out):
    Image.open(f"{SRC}/{name}").convert("RGB").crop(box).save(f"{OUT}/{out}", quality=95)


# Foto gaya hidup (crop elak logo/teks asal iklan)
crop("02_iklan_panjat.jpg", (770, 70, 1180, 640), "climb.jpg")
crop("04_iklan_audience.jpg", (0, 0, 540, 714), "audience.jpg")
crop("03_produk_beg.jpg", (0, 0, 768, 1072), "bag.jpg")
crop("05_wanita_produk.jpg", (0, 0, 720, 1280), "woman.jpg")

# Potongan botol daripada foto sebenar (img1) — rembg buang latar + tangan
sess = new_session("isnet-general-use")
im = Image.open(f"{SRC}/01_tangan_produk.jpg").convert("RGB").crop((0, 520, 1125, 2000))
cut = remove(im, session=sess)
a = np.asarray(cut.crop(cut.getbbox())).copy()
row = a[int(a.shape[0] * 0.85), :, 3]           # julat lajur badan botol
cols = np.where(row > 128)[0]
a[:, : cols.min() - 3, 3] = 0
a[:, cols.max() + 4 :, 3] = 0
p = Image.fromarray(a)
p.crop(p.getbbox()).save(f"{OUT}/product_cutout.png")

# Logo Firea daripada label (img1): kunci warna maroon -> alpha
im = Image.open(f"{SRC}/01_tangan_produk.jpg").convert("RGB").crop((425, 925, 615, 1025))
im = im.resize((im.width * 5, im.height * 5), Image.BICUBIC)
g = np.asarray(im).astype(np.float32)[..., 1]  # latar pink G tinggi, logo maroon G rendah
al = Image.fromarray((np.clip((185 - g) / 95, 0, 1) * 255).astype(np.uint8))
al = al.filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: 0 if v < 60 else min(255, int((v - 60) * 255 / 140)))
for nm, col in (("logo_maroon.png", (122, 28, 58)), ("logo_white.png", (255, 255, 255))):
    rgba = Image.new("RGBA", im.size, col + (0,))
    rgba.putalpha(al)
    rgba.crop(rgba.getbbox()).save(f"{OUT}/{nm}")
print("aset siap")
