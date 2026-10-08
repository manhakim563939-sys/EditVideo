"""Timing for "MITOS atau FAKTA?" — shared by render.py and audio.py.

120 BPM -> 1 beat = 0.5 s, 1 bar = 2 s. Every scene cut sits on a beat.
"""
W, H, FPS = 1080, 1920, 30
DUR = 30.0
BPM = 120
BEAT = 60 / BPM

S = dict(hook=0.0, q1=3.0, q2=10.0, q3=17.0, reveal=23.0)
ORDER = ["hook", "q1", "q2", "q3", "reveal"]

HOOK = dict(mitos=0.10, atau=0.55, fakta=0.85, pill=1.55, note=2.1)

# Quiz rounds. answer = "MITOS" | "FAKTA". All explanations are general knowledge;
# the only product claims used anywhere are the approved USPs.
QUIZ = {
    "q1": dict(n=1, statement=["Bau ketiak", "datang dari", "peluh."], answer="MITOS",
               explain=[["Peluh", "hampir", "#TAK", "berbau."],
                        ["Bau", "terhasil", "bila", "*bakteria"],
                        ["di", "kulit", "mengurai", "peluh."]],
               card=0.0, count=0.7, count_len=2.0, ans=2.7, expl=3.2, exit=6.65),
    "q2": dict(n=2, statement=["Lengan panjang", "lindungi ketiak", "dari bau."], answer="MITOS",
               explain=[["Kain", "menutup", "=", "*kurang udara."],
                        ["Peluh", "terperangkap", "lebih", "lama,"],
                        ["bakteria", "suka", "panas", "&", "lembap."]],
               card=0.0, count=0.7, count_len=2.0, ans=2.7, expl=3.2, exit=6.65),
    "q3": dict(n=3, statement=["Berpeluh", "itu normal."], answer="FAKTA",
               explain=[["Badan", "berpeluh", "untuk"], ["*sejukkan", "*diri."],
                        ["Yang", "penting,", "kawal"],
                        ["#PELUH & BAU"]],
               card=0.0, count=0.6, count_len=1.8, ans=2.4, expl=2.9, exit=5.65),
}

REVEAL = dict(head=0.15, card=0.55, logo=1.0, name=1.4, stickers=(1.9, 2.25, 2.6), slogan=3.2, ask=4.0)


def sfx_cues():
    c = []
    a = c.append
    a((S["hook"] + HOOK["mitos"], "stamp", 0.7))
    a((S["hook"] + HOOK["atau"], "pop", 0.45))
    a((S["hook"] + HOOK["fakta"], "stamp", 0.75))
    a((S["hook"] + HOOK["pill"], "swish", 0.45))
    for name in ORDER[1:]:
        a((S[name] - 0.3, "whoosh", 0.6))
    for q, d in QUIZ.items():
        t0 = S[q]
        a((t0 + d["card"] + 0.15, "pop", 0.4))
        n_ticks = int(round(d["count_len"] / BEAT * 2))  # 8th-note ticks
        for i in range(n_ticks):
            a((t0 + d["count"] + i * BEAT / 2, "tick", 0.35 + 0.25 * i / n_ticks))
        a((t0 + d["ans"], "stamp", 0.8))
        a((t0 + d["ans"] + 0.05, "buzzer" if d["answer"] == "MITOS" else "ding", 0.55))
        a((t0 + d["expl"] + 0.3, "swish", 0.3))
        a((t0 + d["exit"], "swipe", 0.5))
    r = S["reveal"]
    a((r + REVEAL["card"], "pop", 0.45))
    a((r + REVEAL["logo"] + 0.2, "sparkle", 0.5))
    for t in REVEAL["stickers"]:
        a((r + t, "stamp_soft", 0.55))
    a((r + REVEAL["slogan"], "sparkle", 0.35))
    a((r + REVEAL["ask"], "pop", 0.4))
    return sorted(c)
