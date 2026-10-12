# Sambung VO harga baru: bina assets/vo2.mp3 dan anjak garis masa komposisi.
import re, sys, subprocess, json
SP = "/tmp/claude-0/-home-user-EditVideo/782e7b87-a56b-544e-8bf3-41bd1bb99570/scratchpad"
HARGA = SP + "/vo_harga/harga.mp3"
PAD, HLEN = 0.08, 7.95          # senyap sebelum klip, panjang klip harga dipakai
L = round(PAD + HLEN, 2)
TIGA_IN = 3.80                  # "Tiga botol" dalam klip harga
# nama: (a potong media, b sambung media, tiga lama timeline, offset media->timeline di kawasan harga)
CFG = {
 "bidara":  (33.17, 38.69, 35.18, 0.0),
 "bidara2": (33.50, 38.84, 35.13, 0.0),
 "safe1":   (32.10, 37.80, 34.14, 0.0),
 "safe2":   (32.59, 37.95, 34.28, 0.0),
 "hari1":   (42.28, 47.80, 44.06, 0.0),
 "kain":    (38.44, 43.85, 40.20, 0.0),
 "vox":     (38.44, 43.85, 43.70, 3.5),
}
NEWCAP = [(0.0, 2.26, "*RM28 sebotol,"), (2.38, 3.29, "tambah pos *RM8."), (3.80, 5.63, "3 botol *RM65,"),
          (5.95, 6.59, "pos percuma."), (6.99, 7.84, "COD ada.")]

def build_audio(d, a, b):
    src = f"{SP}/hf/{d}/assets/vo.mp3"; out = f"{SP}/hf/{d}/assets/vo2.mp3"
    fc = (f"[0:a]atrim=0:{a},asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=mono[x];"
          f"[1:a]atrim=0:{HLEN},asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=mono,afade=t=out:st={HLEN-0.08}:d=0.08,adelay={int(PAD*1000)}[y];"
          f"[0:a]atrim=start={b},asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=mono[z];"
          f"[x][y][z]concat=n=3:v=0:a=1[o]")
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",src,"-i",HARGA,"-filter_complex",fc,"-map","[o]","-c:a","libmp3lame","-b:a","192k",out],check=True)
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",out]))

def main(d):
    a, b, tiga, off = CFG[d]
    tiga -= 0.15                      # animasi yang dimasa sedikit awal untuk "Tiga botol"
    T = b + off                       # titik anjak pada timeline
    G = round(a + L - b, 2)
    tiga_new = a + off + PAD + TIGA_IN
    if d == "vox": tiga_new = 41.95 + (a + PAD + TIGA_IN - 38.45)
    d1 = round(tiga_new - tiga, 2)
    m = lambda t: round(t if t < tiga else (t + d1 if t < T else t + G), 3)
    me = lambda t: round(t if t < tiga else (t + d1 if t < T - 1e-6 else t + G), 3)
    me2 = lambda t: m(t) if abs(t - T) > 1e-6 else round(t + G, 3)   # hujung tepat pada T -> dipanjangkan
    p = f"{SP}/hf/{d}/index.html"; s = open(p).read()
    vlen = build_audio(d, a, b)
    # klip HTML (bukan audio)
    def clip(mo):
        tag = mo.group(0)
        if "<audio" in tag: return tag
        st = re.search(r'data-start="([0-9.]+)"', tag); du = re.search(r'data-duration="([0-9.]+)"', tag)
        if not du: return tag
        s0 = float(st.group(1)) if st else 0.0; e0 = s0 + float(du.group(1))
        ns, ne = m(s0), me2(e0)
        if st: tag = tag.replace(st.group(0), f'data-start="{round(ns,2)}"')
        return tag.replace(du.group(0), f'data-duration="{round(ne-ns,2)}"')
    s = re.sub(r"<[a-z]+[^>]*data-duration=\"[^>]*>", clip, s)
    # skrip: kedudukan tl.*(..., N);
    def tlpos(mo):
        line, pos = mo.group(1), float(mo.group(2))
        dm = re.search(r"duration: ([0-9.]+)", line)
        if dm and "repeat" not in line and float(dm.group(1)) < 1 and abs(pos + float(dm.group(1)) - T) < 0.02:
            return f"{line}{round(pos + G, 3)}{mo.group(3)}"      # tween keluar yang tamat pada T: anjak penuh
        if dm and "repeat" not in line:
            dur = float(dm.group(1))
            nd = round(dur + G - (m(pos) - pos), 3) if (pos < T and pos + dur >= T - 0.02) else dur
            if abs(nd - dur) > 1e-3: line = line.replace(dm.group(0), f"duration: {nd}", 1)
        return f"{line}{m(pos)}{mo.group(3)}"
    s = re.sub(r"^(\s*tl\.(?:from|to|fromTo|set)\(.*, )([0-9.]+)(\);\s*)$", tlpos, s, flags=re.M)
    s = re.sub(r"const T = ([0-9.]+);", lambda mo: f"const T = {round(float(mo.group(1))+G,2)};", s)
    # audio
    s = re.sub(r'<audio id="voA"[^>]*></audio>\s*<audio id="voB"[^>]*></audio>|<audio id="vo"[^>]*></audio>', "@@AUDIO@@", s)
    if d == "vox":
        aud = ('<audio id="voA" src="assets/vo2.mp3" data-start="0" data-duration="38.45" data-media-start="0" data-track-index="5" data-volume="1"></audio>\n'
               f'      <audio id="voB" src="assets/vo2.mp3" data-start="41.95" data-duration="{round(vlen-38.45,2)}" data-media-start="38.45" data-track-index="5" data-volume="1"></audio>')
        # sari kata: buang frasa harga lama, masuk yang baru, anjak selepas b
        rows = re.findall(r"\[([0-9.]+), ([0-9.]+), (\"[^\"]*\")\]", s[s.index("const RAW"):s.index("];", s.index("const RAW"))])
        out = []
        for x, y, t in rows:
            x, y = float(x), float(y)
            if a <= x < b: continue
            if x >= b: x, y = x + G, y + G
            out.append(f"[{x:.2f}, {y:.2f}, {t}]")
            if x < a and all(not (r.startswith("[%.2f" % (a + PAD + NEWCAP[0][0]))) for r in out): pass
        ins = [f'[{a+PAD+c0:.2f}, {a+PAD+c1:.2f}, "{tx}"]' for c0, c1, tx in NEWCAP]
        k = next(i for i, r in enumerate(out) if float(r[1:r.index(",")]) >= b + G)
        out = out[:k] + ins + out[k:]
        i0 = s.index("const RAW"); i1 = s.index("];", i0)
        s = s[:i0] + "const RAW = [\n        " + ",\n        ".join(out) + "\n      " + s[i1:]
    else:
        aud = f'<audio id="vo" src="assets/vo2.mp3" data-start="0" data-duration="{round(vlen,2)}" data-track-index="4" data-volume="1"></audio>'
    s = s.replace("@@AUDIO@@", aud)
    open(p, "w").write(s)
    root = re.search(r'data-composition-id="main"[^>]*', s).group(0)
    print(d, "G", G, "d1", d1, "vo2", round(vlen, 2), root[-60:])

for d in sys.argv[1:]: main(d)
