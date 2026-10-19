"""Build the timeline and the procedural soundtrack for the growth-plan explainer.

1. Reads script/scenes.json (VO script, cue words, on-screen content).
2. Scene length = VO length + padding. VO length comes from public/vo/<id>.mp3|wav
   when that file exists (ElevenLabs export), otherwise it is estimated from word count.
3. Cue times are placed by word position inside each scene's VO.
4. Writes src/timeline.json (used by Remotion) and public/music.wav + public/sfx.wav.

Usage: .venv/bin/python audio/build.py
"""
import json
import os
import re
import subprocess

import numpy as np
import soundfile as sf
from scipy.signal import butter, lfilter, sosfilt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = json.load(open(f"{ROOT}/script/scenes.json"))
FPS = SPEC["fps"]
WPS = SPEC["wordsPerSecond"]
PAD_IN, PAD_OUT = SPEC["padIn"], SPEC["padOut"]
SR = 48000


# ------------------------------------------------------------------ timeline
def words_of(text):
    return [re.sub(r"[^\w%–-]", "", w) for w in text.split() if re.sub(r"[^\w%–-]", "", w)]


def vo_file(sid):
    for ext in ("wav", "mp3", "m4a"):
        p = f"{ROOT}/public/vo/{sid}.{ext}"
        if os.path.exists(p):
            return f"vo/{sid}.{ext}", p
    return None, None


def probe_dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout
    return float(out.strip())


def cue_times(words, cues, speech):
    res, start = {}, 0
    n = len(words)
    for a in cues:
        al = a.lower()
        for i in range(start, n):
            w = words[i].lower()
            if w == al or (len(al) >= 3 and w.startswith(al)):
                res[a] = round(PAD_IN + speech * i / n, 3)
                start = i + 1
                break
        else:
            raise SystemExit(f"cue '{a}' not found in: {' '.join(words)}")
    return res


scenes, t = [], 0.0
has_vo = False
for s in SPEC["scenes"]:
    words = words_of(s["vo"])
    rel, absp = vo_file(s["id"])
    if absp:
        speech = probe_dur(absp)
        has_vo = True
    else:
        speech = len(words) / WPS
    dur = round(PAD_IN + speech + PAD_OUT, 3)
    sc = dict(s)
    sc.update(start=round(t, 3), dur=dur, speech=round(speech, 3), voSrc=rel,
              cueT=cue_times(words, s["cues"], speech))
    scenes.append(sc)
    t += dur
TOTAL = round(t + 0.5, 3)

# SFX cue list (same times the visuals use)
sfx = []
for sc in scenes:
    st = sc["start"]
    k = sc["kind"]
    if k == "intro":
        sfx += [{"t": st + 0.3, "k": "riser", "g": 0.35, "d": 0.9}, {"t": st + 1.2, "k": "impact", "g": 0.5},
                {"t": st + 1.25, "k": "shimmer", "g": 0.35}]
    elif k == "phase":
        sfx += [{"t": st, "k": "whoosh", "g": 0.5}, {"t": st + 0.45, "k": "impact", "g": 0.45},
                {"t": st + 0.5, "k": "shimmer", "g": 0.3}]
    else:
        sfx.append({"t": st, "k": "whoosh_s", "g": 0.32})
    cues = list(sc["cueT"].values())
    if k in ("action", "roadmap", "outro"):
        for c in cues[1:]:
            sfx.append({"t": st + c, "k": "tick", "g": 0.32})
    if k == "goal":
        ti = list(sc["cueT"].keys()).index("Tanda")
        for c in cues[ti + 1:]:
            sfx.append({"t": st + c, "k": "chime", "g": 0.3})
    if k == "outro":
        sfx.append({"t": st + sc["cueT"]["Inilah"], "k": "shimmer", "g": 0.35})

json.dump({"fps": FPS, "padIn": PAD_IN, "total": TOTAL, "hasVo": has_vo, "scenes": scenes, "sfx": sfx},
          open(f"{ROOT}/src/timeline.json", "w"), ensure_ascii=False, indent=1)
print(f"timeline: {len(scenes)} scenes, {TOTAL:.1f}s, VO files: {has_vo}")

# ------------------------------------------------------------------ synthesis helpers
N = int(TOTAL * SR)
rng = np.random.default_rng(5)


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    return lfilter([1 - a], [1, -a], x)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], btype="band", fs=SR, output="sos"), x)


def hp(x, fc):
    return sosfilt(butter(2, fc, btype="high", fs=SR, output="sos"), x)


def add(buf, sig, t0, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    if i0 >= len(buf) or i0 < 0:
        return
    sig = sig[: len(buf) - i0]
    buf[i0:i0 + len(sig), 0] += sig * gain * np.cos((pan + 1) * np.pi / 4)
    buf[i0:i0 + len(sig), 1] += sig * gain * np.sin((pan + 1) * np.pi / 4)


def pad(freqs, dur):
    n = int((dur + 1.5) * SR)
    tt = np.arange(n) / SR
    s = np.zeros(n)
    for f in freqs:
        for det in (-0.003, 0.0, 0.004):
            ff = f * (1 + det)
            s += np.sin(2 * np.pi * ff * tt) + 0.25 * np.sin(4 * np.pi * ff * tt) + 0.08 * np.sin(6 * np.pi * ff * tt)
    s = lp(s, 1200)
    a = np.minimum(tt / 0.9, 1)
    r = np.where(tt > dur, np.exp(-(tt - dur) / 0.6), 1)
    return s * a * r / (len(freqs) * 3)


def piano(f, dur=2.2):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    s = (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * 2.002 * f * tt) * np.exp(-tt * 2.5)
         + 0.15 * np.sin(2 * np.pi * 3.005 * f * tt) * np.exp(-tt * 4))
    return lp(s * np.minimum(tt / 0.006, 1) * np.exp(-tt * 1.6), 3500)


def pluck(f, dur=0.6):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    s = sum((0.55 ** k) * np.sin(2 * np.pi * f * (k + 1) * tt) * np.exp(-tt * (5 + 4 * k)) for k in range(4))
    return s * np.minimum(tt / 0.003, 1)


def bell(f, dur=1.8):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 5)
    return s * np.minimum(tt / 0.002, 1) * np.exp(-tt * 2.4)


def bass(f, dur):
    n = int((dur + 0.2) * SR)
    tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * tt) + 0.2 * np.sin(4 * np.pi * f * tt)
    return s * np.minimum(tt / 0.02, 1) * np.where(tt > dur, np.exp(-(tt - dur) / 0.08), 1)


def kick():
    n = int(0.4 * SR)
    tt = np.arange(n) / SR
    f = 42 + 60 * np.exp(-tt * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 8)


def hat():
    n = int(0.06 * SR)
    tt = np.arange(n) / SR
    return hp(rng.normal(0, 1, n), 7000) * np.exp(-tt * 70)


# ------------------------------------------------------------------ music
BPM = 80
BEAT = 60 / BPM
BAR = BEAT * 4
CH = {  # D major, warm and confident
    "Dmaj7": [50, 57, 61, 66], "Bm7": [47, 54, 57, 62], "Gmaj7": [43, 50, 54, 59], "Asus": [45, 52, 57, 59],
}
PROG = ["Dmaj7", "Bm7", "Gmaj7", "Asus"]
ROOTS = {"Dmaj7": 38, "Bm7": 35, "Gmaj7": 31, "Asus": 33}


def phase_at(tt):
    ph = 0
    for sc in scenes:
        if sc["start"] <= tt and sc.get("phase"):
            ph = sc["phase"]
        if sc["start"] <= tt and sc["kind"] == "outro":
            ph = 4
    return ph


music = np.zeros((N, 2))
outro_start = [s for s in scenes if s["kind"] == "outro"][0]["start"]
music_end = TOTAL - 0.2
bar = 0
tb = 0.0
melody = [74, 76, 78, 81, 78, 76, 74, 73]
while tb < music_end - 1.0:
    name = PROG[bar % 4]
    ph = phase_at(tb + 0.01)
    notes = CH[name]
    add(music, pad([midi(m + 12) for m in notes], BAR), tb, 0.5)
    # piano: broken chord, every phase
    for j, m in enumerate(notes[1:] + [notes[1] + 12]):
        add(music, piano(midi(m + 12)), tb + j * BEAT, 0.14, pan=-0.3 + 0.2 * j)
    add(music, bass(midi(ROOTS[name]), BAR * 0.95), tb, 0.22 if ph >= 1 else 0.12)
    if ph >= 1:  # arpeggio pluck in 8ths
        for k in range(8):
            m = notes[(k % 3) + 1] + 24
            add(music, pluck(midi(m)), tb + k * BEAT / 2, 0.06 if ph == 1 else 0.08, pan=0.3 if k % 2 else -0.3)
    if ph >= 2 and ph < 4:  # soft pulse
        for b in range(4):
            add(music, kick(), tb + b * BEAT, 0.32 if b in (0, 2) else 0.16)
            add(music, hat(), tb + b * BEAT + BEAT / 2, 0.07, pan=0.4)
    if ph == 3:  # bell melody on top
        for b in range(0, 4, 2):
            add(music, bell(midi(melody[(bar * 2 + b // 2) % 8])), tb + b * BEAT, 0.07, pan=0.2)
    tb += BAR
    bar += 1
# final resolve at the outro's last line
fin = outro_start + scenes[-1]["cueT"]["Inilah"]
add(music, pad([midi(m + 12) for m in CH["Dmaj7"]] + [midi(74)], max(1.0, music_end - fin - 1.0)), fin, 0.6)
add(music, bell(midi(86), 3.0), fin + 0.2, 0.1)
add(music, bass(midi(38), 2.0), fin, 0.25)

fi = int(0.5 * SR)
music[:fi] *= np.linspace(0, 1, fi)[:, None]
fo = int(2.0 * SR)
music[-fo:] *= np.linspace(1, 0, fo)[:, None]
music /= np.max(np.abs(music)) + 1e-9

# Level: a bed under the VO when VO exists (with ducking), louder for a text-only preview.
if has_vo:
    vo = np.zeros(N)
    for sc in scenes:
        if sc["voSrc"]:
            p = f"{ROOT}/public/{sc['voSrc']}"
            raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                 capture_output=True).stdout
            y = np.frombuffer(raw, np.float32)
            add_at = int((sc["start"] + PAD_IN) * SR)
            vo[add_at:add_at + len(y)] += y[: N - add_at]
    hop = 480
    rms = np.sqrt(np.convolve(vo ** 2, np.ones(hop) / hop, "same")[::hop] + 1e-10)
    act = np.clip((20 * np.log10(rms) + 45) / 20, 0, 1)
    sm = np.zeros_like(act)
    for i in range(len(act)):
        prev = sm[i - 1] if i else 0
        sm[i] = prev + (0.5 if act[i] > prev else 0.03) * (act[i] - prev)
    gain = 10 ** (np.interp(np.arange(N), np.arange(len(sm)) * hop, -8.0 * sm) / 20)
    music *= (gain * 10 ** (-13 / 20))[:, None]
else:
    music *= 10 ** (-6 / 20)


# ------------------------------------------------------------------ SFX
def whoosh(d=0.6, short=False):
    n = int(d * SR)
    tt = np.arange(n) / SR
    x = rng.normal(0, 1, n + 4096)
    out = np.zeros(n)
    seg = 1024
    for i in range(0, n, seg):
        p = i / n
        fc = 300 + 3000 * np.sin(np.pi * p) ** 2
        chunk = bp(x[i:i + seg + 4096], fc * 0.6, min(fc * 1.6, 20000))[4096:4096 + seg]
        out[i:i + len(chunk)] = chunk[: n - i]
    return out * np.sin(np.pi * np.clip(tt / d, 0, 1)) ** (1.5 if short else 1.0)


def tick():
    n = int(0.06 * SR)
    tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1800 * tt) * 0.7 + hp(rng.normal(0, 1, n), 3000) * 0.3) * np.exp(-tt * 90)


def chime():
    n = int(1.2 * SR)
    tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * midi(86) * tt) + 0.5 * np.sin(2 * np.pi * midi(93) * tt)) * np.exp(-tt * 4) * np.minimum(tt / 0.002, 1)


def impact():
    n = int(1.0 * SR)
    tt = np.arange(n) / SR
    f = 38 + 55 * np.exp(-tt * 10)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 4) + lp(rng.normal(0, 1, n), 1500) * np.exp(-tt * 18) * 0.4


def riser(d=1.0):
    n = int(d * SR)
    tt = np.arange(n) / SR
    tone = np.sin(2 * np.pi * np.cumsum(220 * 6 ** (tt / d)) / SR) * 0.25
    return (tone + hp(rng.normal(0, 1, n), 3000) * 0.4) * (tt / d) ** 2


def shimmer():
    n = int(1.6 * SR)
    tt = np.arange(n) / SR
    s = np.zeros(n)
    for j, m in enumerate([86, 90, 93, 98]):
        d = int(j * 0.07 * SR)
        s[d:] += np.sin(2 * np.pi * midi(m) * tt[: n - d]) * np.exp(-tt[: n - d] * 3)
    return s


GEN = {"whoosh": lambda c: whoosh(0.7), "whoosh_s": lambda c: whoosh(0.4, True), "tick": lambda c: tick(),
       "chime": lambda c: chime(), "impact": lambda c: impact(), "riser": lambda c: riser(c.get("d", 1.0)),
       "shimmer": lambda c: shimmer()}
LEAD = {"whoosh": 0.35, "whoosh_s": 0.2}
fx = np.zeros((N, 2))
for c in sfx:
    s = GEN[c["k"]](c)
    s /= np.max(np.abs(s)) + 1e-9
    add(fx, s, c["t"] - LEAD.get(c["k"], 0.0) if c["t"] > 0.4 else c["t"], c["g"] * 10 ** (-7 / 20))

sf.write(f"{ROOT}/public/music.wav", music.astype(np.float32), SR, subtype="PCM_24")
sf.write(f"{ROOT}/public/sfx.wav", fx.astype(np.float32), SR, subtype="PCM_24")
print("music peak dBFS %.1f, sfx peak dBFS %.1f" % (20 * np.log10(np.max(np.abs(music))), 20 * np.log10(np.max(np.abs(fx)))))
