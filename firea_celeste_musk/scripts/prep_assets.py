"""Cut the roll-on bottle out of the product photo as a sticker (capsule mask)."""
import sys
from PIL import Image, ImageDraw, ImageFilter
P = sys.argv[1]
im = Image.open(f"{P}/source/product_photo.jpg").convert("RGB")
# bottle bounds in the 1125x2000 photo
x0, y0, x1, y1 = 364, 574, 654, 1408
crop = im.crop((x0, y0, x1, y1))
w, h = crop.size
SS = 4
m = Image.new("L", (w * SS, h * SS), 0)
d = ImageDraw.Draw(m)
cap_h, cl, cr, ry, rb = 340, 8, 14, 105, 34   # cap height, cap insets, cap top radius-y, bottom radius
d.rounded_rectangle([0, (cap_h - 20) * SS, w * SS - 1, h * SS - 1], radius=rb * SS, fill=255)
d.ellipse([cl * SS, 6 * SS, (w - cr) * SS, (6 + 2 * ry) * SS], fill=255)
d.rectangle([cl * SS, (6 + ry) * SS, (w - cr) * SS, cap_h * SS], fill=255)
m = m.resize((w, h), Image.LANCZOS)
out = crop.convert("RGBA")
out.putalpha(m)
out.save(f"{P}/assets/bottle.png")
print("bottle", out.size)
