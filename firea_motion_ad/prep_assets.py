"""Prepare derived assets from the untouched source images in assets/src.

Outputs (assets/cut):
  logo_alpha.png   Firea wordmark as an alpha mask (recoloured at render time)
  photo_hook.jpg   model holding product, park (from 3.jpg, poster text cropped out)
  photo_ugc.jpg    real user holding Celeste Musk (from 4.jpg)
  photo_mirror.jpg mirror shot (from 5.jpg)
"""
import os

import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = f"{ROOT}/assets/src"
OUT = f"{ROOT}/assets/cut"
os.makedirs(OUT, exist_ok=True)

# ---- logo: crop wordmark from 1.jpg (highest-res copy), upscale, key out pink bg
im = Image.open(f"{SRC}/1.jpg").convert("RGB").crop((86, 22, 318, 130))
im = im.resize((im.width * 4, im.height * 4), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2))
a = np.asarray(im).astype(np.float32)
# background ~ (254,238,239); logo ~ (164,14,60). Green channel separates them best.
alpha = np.clip((225 - a[..., 1]) / (225 - 40), 0, 1)
alpha = np.clip((alpha - 0.08) / 0.84, 0, 1)  # tighten edges
Image.fromarray((alpha * 255).astype(np.uint8), "L").save(f"{OUT}/logo_alpha.png")

# ---- photos
Image.open(f"{SRC}/3.jpg").convert("RGB").crop((70, 470, 672, 1264)).save(f"{OUT}/photo_hook.jpg", quality=95)
Image.open(f"{SRC}/4.jpg").convert("RGB").crop((40, 300, 680, 1180)).save(f"{OUT}/photo_ugc.jpg", quality=95)
Image.open(f"{SRC}/5.jpg").convert("RGB").crop((360, 0, 1060, 714)).save(f"{OUT}/photo_mirror.jpg", quality=95)
print("assets ready")
