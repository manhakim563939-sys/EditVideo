"""Recap ~5 minit perjalanan Laser Wood Photo (LWP) daripada video & gambar di Drive.

Usage: python3 lwp_recap.py <media_dir> <work_dir> <output.mp4>
  <media_dir>  semua fail dari folder Drive (VID_20261126_200017_156.mp4, VID-*.mp4, gambar *.jpg)
  <work_dir>   folder kerja (segmen sementara, luma.txt dari ffmpeg signalstats 1fps)

Struktur:
  Intro (gambar khemah LWP) -> Bab 1 Expo -> Bab 2 Pasukan -> Bab 3 Lapangan (klip pendek)
  -> Bab 4 Family Day -> Bab 5 montaj gambar -> Penutup.
Soundtrack: lagu latar asal dari video panjang (lagu 1 + lagu 4, crossfade).
"""
import os
import subprocess
import sys

MEDIA, WORK, OUT = sys.argv[1:4]
W, H, FPS = 1280, 720, 30
FONT_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FONT_M = "/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf"
LONG = f"{MEDIA}/VID_20261126_200017_156.mp4"
SEG = f"{WORK}/segs"
os.makedirs(SEG, exist_ok=True)
ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS), "-an"]


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def esc(t):
    return t.replace("\\", "\\\\").replace("'", "’").replace(":", "\\:").replace("%", "\\%")


def fill(src):
    """Letakkan sumber apa-apa nisbah dalam 1280x720 dengan latar kabur."""
    return (f"{src}split[a][b];"
            f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:2,eq=brightness=-0.08[bg];"
            f"[b]scale={W}:{H}:force_original_aspect_ratio=decrease[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1")


def title_overlay(dur, big, small=None, lower=True):
    """Teks tajuk (lower-third atau tengah) dengan fade in/out."""
    a = f"if(lt(t,0.4),t/0.4,if(gt(t,{dur - 0.5}),max(0,({dur} - t)/0.5),1))"
    if lower:
        f = (f",drawbox=x=0:y=ih-170:w=iw:h=170:color=black@0.45:t=fill:enable='lt(t,{dur})'"
             f",drawbox=x=60:y=ih-138:w=8:h={90 if small else 52}:color=0xF2B705@1:t=fill:enable='lt(t,{dur})'"
             f",drawtext=fontfile={FONT_B}:text='{esc(big)}':x=86:y=h-142:fontsize=46:fontcolor=white:alpha='{a}'")
        if small:
            f += f",drawtext=fontfile={FONT_M}:text='{esc(small)}':x=88:y=h-84:fontsize=28:fontcolor=0xF2B705:alpha='{a}'"
        return f
    f = (f",drawbox=x=0:y=0:w=iw:h=ih:color=black@0.45:t=fill"
         f",drawtext=fontfile={FONT_B}:text='{esc(big)}':x=(w-tw)/2:y=h/2-70:fontsize=72:fontcolor=white:"
         f"shadowcolor=black@0.6:shadowx=3:shadowy=3:alpha='{a}'")
    if small:
        f += (f",drawtext=fontfile={FONT_M}:text='{esc(small)}':x=(w-tw)/2:y=h/2+30:fontsize=36:fontcolor=0xF2B705:"
              f"shadowcolor=black@0.6:shadowx=2:shadowy=2:alpha='{a}'")
    return f


segs = []


def add_video(path, ss, dur, title=None, fade_in=False):
    out = f"{SEG}/{len(segs):03d}.mp4"
    vf = fill(f"[0:v]fps={FPS},")
    if title:
        vf += title_overlay(min(dur, 3.5), *title)
    if fade_in:
        vf += ",fade=t=in:st=0:d=0.5"
    run(["ffmpeg", "-y", "-ss", f"{ss:.2f}", "-t", f"{dur:.2f}", "-i", path, "-filter_complex", vf, *ENC, out])
    segs.append((out, dur))


def add_photo(path, dur, zoom_in=True, title=None, center=False, fade_in=False, fade_out=False):
    out = f"{SEG}/{len(segs):03d}.mp4"
    n = int(dur * FPS)
    z = f"1+0.08*on/{n}" if zoom_in else f"1.08-0.08*on/{n}"
    vf = (fill("[0:v]") + f",scale={W * 2}:{H * 2},"
          f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS}")
    if title:
        vf += title_overlay(dur, *title, lower=not center)
    if fade_in:
        vf += ",fade=t=in:st=0:d=0.8"
    if fade_out:
        vf += f",fade=t=out:st={dur - 1.5}:d=1.5"
    run(["ffmpeg", "-y", "-loop", "1", "-i", path, "-filter_complex", vf, "-t", f"{dur:.2f}", *ENC, out])
    segs.append((out, dur))


# ---- pilih klip dari video panjang (ia slideshow ~6s/babak; potong ikut perubahan kecerahan) ----
luma = [float(l.split("=")[1]) for l in open(f"{WORK}/luma.txt") if "YAVG" in l]


def shots(a, b):
    cuts = [a] + [t for t in range(a + 1, b) if abs(luma[t] - luma[t - 1]) > 8] + [b]
    merged = [cuts[0]]
    for c in cuts[1:]:
        if c - merged[-1] >= 3:
            merged.append(c)
    out = []
    for s, e in zip(merged, merged[1:]):
        if e - s >= 3 and sum(luma[s:e]) / (e - s) > 60:
            out.append((s, e))
    return out


def section(a, b, budget, clip, title):
    sh = shots(a, b)
    k = max(1, round(budget / clip))
    if len(sh) > k:  # sampel sekata
        sh = [sh[round(i * (len(sh) - 1) / (k - 1))] for i in range(k)]
    for i, (s, e) in enumerate(sh):
        d = min(clip, e - s - 1.0)
        st = s + 0.6 + max(0, (e - s - 1.2 - d) / 2)
        add_video(LONG, st, d, title if i == 0 else None, fade_in=(i == 0))


P = lambda n: f"{MEDIA}/{n}"

# Intro
add_photo(P("IMG-20261126-WA0073.jpg"), 6.0, title=("LASER WOOD PHOTO", "Perjalanan Kami  •  Ukir Kenangan Anda"),
          center=True, fade_in=True)
# Bab 1: Expo & karnival (0-250s)
section(5, 250, 74, 2.9, ("Bermula dari Expo ke Expo", "Karnival, pasar malam & hari terbuka"))
# Bab 2: Membina pasukan (250-425s)
section(250, 425, 50, 3.6, ("Membina Pasukan", "Bengkel, mesin baru & team yang makin besar"))
# Bab 3: Klip pendek di lapangan
add_video(P("VID-20261126-WA0080.mp4"), 0.5, 8.0, ("Turun Padang Bersama", "Booth LWP"), fade_in=True)
add_video(P("VID-20261126-WA0079.mp4"), 0.5, 6.0)
add_video(P("VID-20261126-WA0081.mp4"), 3.0, 4.0)
add_video(P("VID-20261126-WA0081.mp4"), 18.0, 9.0)
# Bab 4: Family day, pool, BBQ, pantai (425-765s)
section(425, 765, 86, 3.8, ("Family Day & Percutian", "Pool, BBQ, pantai — semua bersama"))

# Bab 5: montaj gambar (ikut tarikh)
photos = ["IMG-20201023-WA0127.jpg", "IMG_20201126_175630_620.JPG", "IMG-20201228-WA0007.jpg",
          "nwdn_file_temp_1609112917142.jpg", "IMG_20210320_180530_611.JPG", "IMG_20210404_140319.jpg",
          "IMG_20210405_214814_539.JPG", "nwdn_file_temp_1622463680866.jpg", "IMG-20210821-WA0020.jpg",
          "Remini20211223154419137.jpg", "IMG-20211225-WA0010.jpg", "IMG_20220207_125232.jpg",
          "Remini20220216155134363.jpg", "IMG-20221015-WA0063.jpg", "IMG-20230416-WA0011.jpg",
          "IMG-20261126-WA0060.jpg", "IMG-20261126-WA0063.jpg", "IMG-20261126-WA0065.jpg",
          "IMG-20261126-WA0070.jpg", "IMG-20261126-WA0071.jpg", "IMG-20261126-WA0076.jpg",
          "IMG-20261126-WA0078.jpg"]
for i, p in enumerate(photos):
    add_photo(P(p), 2.9, zoom_in=(i % 2 == 0),
              title=("Kenangan Bersama", "2020 — kini") if i == 0 else None, fade_in=(i == 0))
# Penutup
add_photo(P("IMG-20261126-WA0077.jpg"), 7.0, title=("Terima Kasih", "Untuk setiap kenangan bersama LWP"),
          center=True, fade_out=True)

total = sum(d for _, d in segs)
print(f"{len(segs)} segmen, jumlah {total:.1f}s", file=sys.stderr)

with open(f"{WORK}/concat.txt", "w") as f:
    for p, _ in segs:
        f.write(f"file '{p}'\n")
run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"{WORK}/concat.txt", "-c", "copy", f"{WORK}/video.mp4"])

# Soundtrack: lagu 1 (0-155s) crossfade ke lagu 4 (bermula 460s)
afilter = (f"[1:a]atrim=0:155,asetpts=PTS-STARTPTS[a1];[2:a]atrim=460:{460 + total},asetpts=PTS-STARTPTS[a2];"
           f"[a1][a2]acrossfade=d=4,atrim=0:{total},afade=t=in:d=1,afade=t=out:st={total - 5}:d=5,"
           f"loudnorm=I=-16:TP=-1.5[a]")
run(["ffmpeg", "-y", "-i", f"{WORK}/video.mp4", "-i", LONG, "-i", LONG, "-filter_complex",
     afilter,
     "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
     "-movflags", "+faststart", OUT])
print("siap:", OUT, file=sys.stderr)
