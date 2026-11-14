"""Make an AI image read like a straight-out-of-phone photo.

Softens AI over-sharpness, flattens the HDR look, nudges white balance, adds
phone-sensor luminance + chroma noise, slight chromatic aberration and lens
vignetting, then saves as a phone-quality JPEG.

Usage: python3 realistik.py in.png out.jpg [strength 0..1, default 0.7]
"""
import sys

import cv2
import numpy as np

src, dst = sys.argv[1], sys.argv[2]
s = float(sys.argv[3]) if len(sys.argv) > 3 else 0.7
rng = np.random.default_rng(1)

img = cv2.imread(src, cv2.IMREAD_COLOR).astype(np.float32) / 255
h, w = img.shape[:2]
# phone-ish resolution, then a touch of softness (AI output is unnaturally crisp)
k = 2016 / max(w, h)  # iPhone 12MP-ish long side
img = cv2.resize(img, (int(w * k), int(h * k)), interpolation=cv2.INTER_AREA)
h, w = img.shape[:2]
img = cv2.GaussianBlur(img, (0, 0), 0.6 * s + 0.2)

# flatten the HDR / "clarity" look: pull local contrast back towards a blurred base
base = cv2.GaussianBlur(img, (0, 0), 25)
img = img + (base - img) * 0.18 * s

# tone: lift blacks a little, soften highlights, slight warm-green phone white balance
img = 0.025 * s + img * (1 - 0.05 * s)
img = img / (1 + 0.12 * s * img)
img *= np.array([0.97, 1.0, 1.03])  # BGR: a bit warmer
hsv = cv2.cvtColor(np.clip(img, 0, 1), cv2.COLOR_BGR2HSV)
hsv[..., 1] *= 1 - 0.1 * s  # AI images are over-saturated
img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

# lateral chromatic aberration towards the edges
cx, cy = w / 2, h / 2
for ch, k in [(0, 1 + 0.0012 * s), (2, 1 - 0.0012 * s)]:
    M = np.float32([[k, 0, cx - k * cx], [0, k, cy - k * cy]])
    img[..., ch] = cv2.warpAffine(img[..., ch], M, (w, h), borderMode=cv2.BORDER_REFLECT)

# lens vignetting
yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
r = ((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2
img *= (1 - 0.12 * s * np.clip(r, 0, 2) / 2)[..., None]

# sensor noise: luminance (stronger in shadows) + low-frequency chroma blotches
lum = cv2.cvtColor(np.clip(img, 0, 1), cv2.COLOR_BGR2GRAY)
amp = (0.012 + 0.02 * (1 - lum)) * s
img += (rng.normal(0, 1, (h, w)) * amp)[..., None]
chroma = cv2.resize(rng.normal(0, 1, (h // 3, w // 3, 3)).astype(np.float32), (w, h)) * 0.008 * s
img += chroma

out = np.clip(img * 255, 0, 255).astype(np.uint8)
cv2.imwrite(dst, out, [cv2.IMWRITE_JPEG_QUALITY, int(88 - 8 * s)])
print(dst, out.shape)
