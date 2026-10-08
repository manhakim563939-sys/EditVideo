"""Single source of truth for timing. render.py (visuals) and audio.py (music + SFX)
both import from here, so every SFX lands on the same frame as its visual cue.

Tempo 100 BPM -> 1 beat = 0.6 s. Scene cuts sit on beats.
"""
W, H, FPS = 1080, 1920, 30
DUR = 30.0
BPM = 100
BEAT = 60 / BPM

# scene start times (s)
S = dict(hook=0.0, q=3.6, fact1=7.8, fact2=12.6, example=17.4, takeaway=21.6, product=25.2)
ORDER = ["hook", "q", "fact1", "fact2", "example", "takeaway", "product"]
TRANS = {"q": "panel", "fact1": "iris", "fact2": "push", "example": "panel", "takeaway": "zoom", "product": "panel_rose"}

# local cue times (seconds from each scene start)
HOOK = dict(card=0.0, words=0.10, stagger=0.12, underline=0.85, sticker=1.55, punch=2.4)
Q = dict(words=0.25, stagger=0.10, hl=0.75, block2=1.65, cta=2.75)
FACT1 = dict(chip=0.35, words=0.45, stagger=0.09, drop=1.05, fall=0.35, bact=2.15, bact_stag=0.09,
             odor=2.7, words2=2.3)
FACT2 = dict(chip=0.30, words=0.40, stagger=0.10, diagram=0.95, air=1.25, drops=1.6, drop_stag=0.22,
             words2=2.25, words3=3.05)
EXAMPLE = dict(chip=0.30, words=0.35, nodes=(0.75, 1.55, 2.35), words2=3.1)
TAKEAWAY = dict(chip=0.25, words=0.30, words2=1.0, hl=1.45, photo=1.9, note=2.5)
PRODUCT = dict(card=0.0, logo=0.15, name=0.55, chips=(1.15, 1.5, 1.85), tag=2.4, slogan=3.0, sparkle=0.9)


def sfx_cues():
    """(time, kind, gain) list consumed by audio.py."""
    c = []
    a = c.append
    # hook
    a((0.0, "impact_soft", 0.55))
    for i in range(3):
        a((S["hook"] + HOOK["words"] + i * 2 * HOOK["stagger"], "click", 0.35))
    a((S["hook"] + HOOK["underline"], "swish", 0.45))
    a((S["hook"] + HOOK["sticker"], "pop", 0.55))
    # transitions: whoosh peaks on the cut
    for name in ORDER[1:]:
        a((S[name] - 0.28, "whoosh", 0.6))
    a((S["fact1"] + 0.05, "bloop", 0.35))  # iris
    # question
    a((S["q"] + Q["hl"], "swish", 0.5))
    a((S["q"] + Q["block2"], "click", 0.4))
    a((S["q"] + Q["cta"], "pop", 0.45))
    # fact 1
    a((S["fact1"] + FACT1["chip"], "click", 0.4))
    a((S["fact1"] + FACT1["drop"] + FACT1["fall"], "bloop", 0.75))
    for i in range(6):
        a((S["fact1"] + FACT1["bact"] + i * FACT1["bact_stag"], "bubble", 0.28))
    a((S["fact1"] + FACT1["words"] + 0.5, "swish", 0.35))
    # fact 2
    a((S["fact2"] + FACT2["chip"], "click", 0.4))
    a((S["fact2"] + FACT2["air"], "air", 0.4))
    for i in range(9):
        a((S["fact2"] + FACT2["drops"] + i * FACT2["drop_stag"], "bubble", 0.25))
    # example
    a((S["example"] + EXAMPLE["chip"], "click", 0.4))
    for t in EXAMPLE["nodes"]:
        a((S["example"] + t, "pop", 0.5))
    a((S["example"] + EXAMPLE["words2"] + 0.35, "swish", 0.4))
    # takeaway
    a((S["takeaway"] + TAKEAWAY["chip"], "click", 0.4))
    a((S["takeaway"] + TAKEAWAY["hl"], "swish", 0.5))
    a((S["takeaway"] + TAKEAWAY["photo"], "pop", 0.4))
    a((S["product"] - 1.2, "riser", 0.55))
    # product
    a((S["product"], "impact", 0.7))
    a((S["product"] + PRODUCT["logo"] + 0.3, "sparkle", 0.45))
    for t in PRODUCT["chips"]:
        a((S["product"] + t, "pop", 0.55))
    a((S["product"] + PRODUCT["slogan"], "sparkle", 0.35))
    return sorted(c)
