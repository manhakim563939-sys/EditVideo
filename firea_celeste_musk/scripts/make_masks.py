"""Person (+ held bottle) masks for the Vox version.

Usage: python make_masks.py <project_dir> <out_dir>
Writes <out_dir>/frames/%05d.jpg and <out_dir>/masks/%05d.png (1080x1920, 30fps).
u2net_human_seg for the person; after the product cut it is unioned with
isnet-general-use so the bottle in her hand is kept. Models download from the
rembg GitHub releases into ~/.u2net on first run.
"""
import os
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

sys.path.insert(0, os.path.dirname(__file__))
import cues as C  # noqa: E402

P, OUT = sys.argv[1], sys.argv[2]
os.makedirs(f"{OUT}/frames", exist_ok=True)
os.makedirs(f"{OUT}/masks", exist_ok=True)
if not os.listdir(f"{OUT}/frames"):
    subprocess.run(["ffmpeg", "-v", "error", "-i", f"{P}/source/footage.mp4", "-vf", "scale=1080:1920:flags=lanczos",
                    "-q:v", "2", f"{OUT}/frames/%05d.jpg"], check=True)
human, general = new_session("u2net_human_seg"), new_session("isnet-general-use")
files = sorted(os.listdir(f"{OUT}/frames"))
for n, f in enumerate(files):
    dst = f"{OUT}/masks/{f[:-4]}.png"
    if os.path.exists(dst):
        continue
    im = Image.open(f"{OUT}/frames/{f}").convert("RGB")
    m = np.array(remove(im, session=human, only_mask=True)).astype(np.float32)
    if n / 30 >= C.SCENE_CUT - 0.02:
        g = np.array(remove(im, session=general, only_mask=True)).astype(np.float32)
        g = np.where(g > 140, 255, 0).astype(np.float32)   # keep only solid objects (bottle, hand)
        m = np.maximum(m, g)
    # keep the largest blob (drops stray car-seat pieces)
    b = (m > 128).astype(np.uint8)
    k, lab, stats, _ = cv2.connectedComponentsWithStats(b)
    if k > 2:
        keep = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        m[(lab != keep) & (lab != 0)] = 0
    cv2.imwrite(dst, m.astype(np.uint8))
    if n % 60 == 0:
        print(f"mask {n}/{len(files)}", file=sys.stderr, flush=True)
