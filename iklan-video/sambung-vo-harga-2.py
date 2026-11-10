# Ganti klip VO harga (RM28/RM65) dengan klip baru (RM30/RM58/RM69): bina assets/vo3.mp3 dari vo.mp3 asal
# dan anjak garis masa komposisi yang sudah disambung sebelum ini (vo2).
import re, sys, subprocess
SP = "/tmp/claude-0/-home-user-EditVideo/782e7b87-a56b-544e-8bf3-41bd1bb99570/scratchpad"
HARGA = SP + "/vo_new/harga2.mp3"
PAD, HLEN = 0.08, 10.10
L_OLD, L_NEW = 8.03, round(PAD + HLEN, 2)
DELTA = round(L_NEW - L_OLD, 2)
# titik rujukan (masa dari awal klip lama -> masa dari awal klip baru)
ANCH = [(0.0, 0.0), (3.73, 5.47), (6.03, 7.80), (7.07, 9.00), (L_OLD, L_NEW)]
# nama: (a potong media, b sambung media)
CFG = {"bidara": (33.17, 38.69), "bidara2": (33.50, 38.84), "safe1": (32.10, 37.80), "safe2": (32.59, 37.95),
       "hari1": (42.28, 47.80), "kain": (38.44, 43.85), "vox": (38.44, 43.85), "cuba": (45.48, 50.80)}
NEWCAP = [(0.00, 1.93, "*RM30 sebotol,"), (2.05, 3.06, "tambah pos *RM8."), (3.59, 5.05, "2 botol *RM58,"),
          (5.54, 7.40, "3 botol *RM69,"), (7.72, 8.36, "pos percuma."), (8.92, 10.06, "COD ada.")]

def f(u):
    for (x0, y0), (x1, y1) in zip(ANCH, ANCH[1:]):
        if u <= x1: return y0 + (u - x0) * (y1 - y0) / (x1 - x0)
    return u + DELTA

def build_audio(d, a, b):
    src = f"{SP}/hf/{d}/assets/vo.mp3"; out = f"{SP}/hf/{d}/assets/vo3.mp3"
    fc = (f"[0:a]atrim=0:{a},asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=mono[x];"
          f"[1:a]atrim=0:{HLEN},asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=mono,afade=t=out:st={HLEN-0.08}:d=0.08,adelay={int(PAD*1000)}[y];"
          f"[0:a]atrim=start={b},asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=mono[z];"
          f"[x][y][z]concat=n=3:v=0:a=1[o]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-i", HARGA, "-filter_complex", fc,
                    "-map", "[o]", "-c:a", "libmp3lame", "-b:a", "192k", out], check=True)
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out]))

def main(d):
    a, b = CFG[d]
    vlen = build_audio(d, a, b)
    if d == "cuba":
        print(d, "vo3", round(vlen, 2)); return
    T0 = 41.95 + (a - 38.45) if d == "vox" else a
    m = lambda t: round(t if t < T0 else (T0 + f(t - T0) if t < T0 + L_OLD else t + DELTA), 3)
    p = f"{SP}/hf/{d}/index.html"; s = open(p).read()
    def clip(mo):
        tag = mo.group(0)
        if "<audio" in tag: return tag
        st = re.search(r'data-start="([0-9.]+)"', tag); du = re.search(r'data-duration="([0-9.]+)"', tag)
        s0 = float(st.group(1)) if st else 0.0; e0 = s0 + float(du.group(1))
        ns, ne = m(s0), m(e0)
        if st: tag = tag.replace(st.group(0), f'data-start="{round(ns, 2)}"')
        return tag.replace(du.group(0), f'data-duration="{round(ne - ns, 2)}"')
    s = re.sub(r"<[a-z]+[^>]*data-duration=\"[^>]*>", clip, s)
    def tlpos(mo):
        line, pos = mo.group(1), float(mo.group(2))
        dm = re.search(r"duration: ([0-9.]+)", line)
        if dm and "repeat" not in line and float(dm.group(1)) >= 1:
            dur = float(dm.group(1)); nd = round(m(pos + dur) - m(pos), 3)
            if abs(nd - dur) > 1e-3: line = line.replace(dm.group(0), f"duration: {nd}", 1)
        return f"{line}{m(pos)}{mo.group(3)}"
    s = re.sub(r"^(\s*tl\.(?:from|to|fromTo|set)\(.*, )([0-9.]+)(\);\s*)$", tlpos, s, flags=re.M)
    s = re.sub(r"const T = ([0-9.]+);", lambda mo: f"const T = {round(float(mo.group(1)) + DELTA, 2)};", s)
    if d == "vox":
        i0 = s.index("const RAW"); i1 = s.index("];", i0)
        rows = re.findall(r"\[([0-9.]+), ([0-9.]+), (\"[^\"]*\")\]", s[i0:i1])
        out = []
        for x, y, t in rows:
            x, y = float(x), float(y)
            if a <= x < a + L_OLD: continue
            if x >= a + L_OLD: x, y = x + DELTA, y + DELTA
            out.append((x, f"[{x:.2f}, {y:.2f}, {t}]"))
        for c0, c1, tx in NEWCAP:
            out.append((a + PAD + c0, f'[{a + PAD + c0:.2f}, {a + PAD + c1:.2f}, "{tx}"]'))
        out.sort(key=lambda r: r[0])
        s = s[:i0] + "const RAW = [\n        " + ",\n        ".join(r for _, r in out) + "\n      " + s[i1:]
        s = re.sub(r'<audio id="voB" src="assets/vo2.mp3" data-start="41.95" data-duration="[0-9.]+"',
                   f'<audio id="voB" src="assets/vo3.mp3" data-start="41.95" data-duration="{round(vlen - 38.45, 2)}"', s)
        s = s.replace('<audio id="voA" src="assets/vo2.mp3"', '<audio id="voA" src="assets/vo3.mp3"')
    else:
        s = re.sub(r'<audio id="vo" src="assets/vo2.mp3" data-start="0" data-duration="[0-9.]+"',
                   f'<audio id="vo" src="assets/vo3.mp3" data-start="0" data-duration="{round(vlen, 2)}"', s)
    assert "vo2.mp3" not in s, d
    open(p, "w").write(s)
    root = re.search(r'data-composition-id="main"[^>]*', s).group(0)
    print(d, "vo3", round(vlen, 2), root[-55:])

for d in sys.argv[1:]: main(d)
