"""Cut the QnA answers out of the source interview and build per-video data.

Usage: .venv/bin/python audio/prep.py <source.mp4>
Writes public/qN/clip.mp4 (video), public/qN/dialog.wav (normalised answer audio),
src/data/qN.json (beats/viz/cuts in composition time = hook + clip time).
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1]
SPEC = json.load(open(f"{ROOT}/spec/spec.json"))
HOOK = SPEC["hook"]

for qid, q in SPEC["qna"].items():
    segs = q["segs"]
    starts, acc = [], 0.0
    for s, e in segs:
        starts.append(acc)
        acc += e - s
    clip_len = acc

    def m(t):
        for (s, e), c in zip(segs, starts):
            if t < s:
                return HOOK + c  # in a removed gap: snap to next kept part
            if t <= e:
                return HOOK + c + (t - s)
        return HOOK + clip_len

    out = f"{ROOT}/public/{qid}"
    os.makedirs(out, exist_ok=True)
    fc, vs, as_ = [], [], []
    for i, (s, e) in enumerate(segs):
        d = e - s
        fc.append(f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS,fps=30,scale=1080:1920[v{i}]")
        fc.append(f"[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={d - 0.015:.3f}:d=0.015[a{i}]")
        vs.append(f"[v{i}]"); as_.append(f"[a{i}]")
    fc.append("".join(v + a for v, a in zip(vs, as_)) + f"concat=n={len(segs)}:v=1:a=1[v][a]")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", SRC, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", f"{out}/raw.mkv"], check=True)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", f"{out}/raw.mkv", "-an", "-c:v", "copy", f"{out}/clip.mp4"], check=True)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", f"{out}/raw.mkv", "-vn", "-af", "highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-ar", "48000", "-ac", "2", f"{out}/dialog.wav"], check=True)
    os.remove(f"{out}/raw.mkv")

    beats = []
    for b in q["beats"]:
        nb = dict(b, s=round(m(b["s"]), 3), e=round(m(b["e"]), 3))
        nb["lines"] = [dict(l, at=round(m(l["at"]), 3)) for l in b["lines"]]
        if "items" in nb:
            nb["items"] = [[x, round(m(t), 3)] for x, t in nb["items"]]
        beats.append(nb)
    viz = []
    for v in q["viz"]:
        nv = {}
        for k, val in v.items():
            if isinstance(val, (int, float)) and k not in ("no",):
                nv[k] = round(m(val), 3)
            elif k == "items":
                nv[k] = [[x, round(m(t), 3)] for x, t in val]
            else:
                nv[k] = val
        viz.append(nv)
    cuts = [round(HOOK + c, 3) for c in starts]
    total = HOOK + clip_len + SPEC["endCard"]
    # SFX: whoosh into the answer and on every jump cut, pop on each big line, ding on the end card
    sfx = [{"t": 0.05, "k": "whoosh_s", "g": 0.3}, {"t": 0.3, "k": "pop", "g": 0.3}, {"t": HOOK, "k": "whoosh", "g": 0.35}]
    sfx += [{"t": c, "k": "whoosh_s", "g": 0.18} for c in cuts[1:]]
    for b in beats:
        for l in b["lines"]:
            if l.get("big"):
                sfx.append({"t": l["at"], "k": "impact_s" if b.get("style") == "stamp" else "pop", "g": 0.3})
    sfx += [{"t": HOOK + clip_len, "k": "whoosh", "g": 0.35}, {"t": HOOK + clip_len + 0.5, "k": "ding", "g": 0.3}]
    data = {"id": qid, "no": q["no"], "title": q["title"], "question": q["question"], "fps": 30, "hook": HOOK,
            "clipLen": round(clip_len, 3), "dialogEnd": round(HOOK + clip_len, 3), "endCard": SPEC["endCard"],
            "total": round(total, 3), "cuts": cuts, "beats": beats, "viz": viz, "sfx": sorted(sfx, key=lambda x: x["t"]),
            "musicLift": HOOK}
    json.dump(data, open(f"{ROOT}/src/data/{qid}.json", "w"), ensure_ascii=False, indent=1)
    print(qid, f"clip {clip_len:.1f}s total {total:.1f}s, {len(segs)} cuts")
