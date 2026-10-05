// Soundtrack instrumental + SFX procedural. Tiada sampel luar / lagu komersial.
// Guna cue yang sama dengan visual: src/timeline.json
// Output: public/audio/mix.wav (dipakai video), music.wav & sfx.wav (stem untuk edit)
import fs from "node:fs";

const TL = JSON.parse(fs.readFileSync(new URL("../src/timeline.json", import.meta.url)));
const SR = 44100;
const FPS = TL.fps;
const DUR = TL.durationInFrames / FPS;
const N = Math.ceil(DUR * SR);
const BEAT = 60 / TL.bpm; // 0.5 s
const BAR = BEAT * 4;
const f2s = (f) => f / FPS;

// deterministik
let seed = 7;
const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647) * 2 - 1;

const mk = () => [new Float32Array(N), new Float32Array(N)];
const music = mk();
const sfx = mk();
const verbSend = mk();

const mtof = (m) => 440 * Math.pow(2, (m - 69) / 12);
const add = (bus, i, v, pan = 0) => {
  if (i < 0 || i >= N) return;
  bus[0][i] += v * Math.cos(((pan + 1) * Math.PI) / 4);
  bus[1][i] += v * Math.sin(((pan + 1) * Math.PI) / 4);
};

// Chamberlin state-variable filter
function svf() {
  let lp = 0, bp = 0;
  return (x, fc, q = 0.7) => {
    const f = 2 * Math.sin((Math.PI * Math.min(fc, SR / 6)) / SR);
    lp += f * bp;
    const hp = x - lp - q * bp;
    bp += f * hp;
    return { lp, bp, hp };
  };
}

// ---------------------------------------------------------------- instrumen
function kick(t0, g = 1, bus = music) {
  const s = Math.floor(t0 * SR);
  let ph = 0;
  for (let i = 0; i < SR * 0.35; i++) {
    const t = i / SR;
    const fr = 45 + 95 * Math.exp(-t * 28);
    ph += (2 * Math.PI * fr) / SR;
    const env = Math.exp(-t * 9) * (i < 40 ? i / 40 : 1);
    add(bus, s + i, Math.sin(ph) * env * 0.9 * g);
  }
}
function hat(t0, g = 1, open = false) {
  const s = Math.floor(t0 * SR);
  const f = svf();
  const len = open ? 0.18 : 0.05;
  for (let i = 0; i < SR * len; i++) {
    const t = i / SR;
    const y = f(rnd(), 9000, 0.4).hp * Math.exp(-t * (open ? 22 : 70));
    add(music, s + i, y * 0.12 * g, 0.25);
  }
}
function clap(t0, g = 1) {
  const s = Math.floor(t0 * SR);
  const f = svf();
  for (let i = 0; i < SR * 0.22; i++) {
    const t = i / SR;
    const burst = t < 0.03 ? 0.6 + 0.4 * Math.sin(t * 2 * Math.PI * 110) : 1;
    const y = f(rnd(), 1500, 0.9).bp * Math.exp(-t * 18) * burst;
    add(music, s + i, y * 0.32 * g, -0.1);
    add(verbSend, s + i, y * 0.1 * g);
  }
}
function pluck(t0, midi, g = 1, len = 0.6, pan = 0, bright = 3500) {
  const s = Math.floor(t0 * SR);
  const fr = mtof(midi);
  const f = svf();
  for (let i = 0; i < SR * len; i++) {
    const t = i / SR;
    const ph = t * fr;
    const saw = 2 * (ph - Math.floor(ph + 0.5));
    const tri = 1 - 4 * Math.abs(Math.round(ph) - ph);
    const env = Math.exp(-t * 7) * Math.min(1, i / 60);
    const y = f(0.5 * saw + 0.5 * tri, 400 + bright * Math.exp(-t * 10), 0.5).lp * env;
    add(music, s + i, y * 0.16 * g, pan);
    add(verbSend, s + i, y * 0.12 * g);
  }
}
function pad(t0, len, notes, g = 1) {
  const s = Math.floor(t0 * SR);
  const fl = svf(), fr = svf();
  const atk = 0.4, rel = 0.6;
  for (let i = 0; i < SR * (len + rel); i++) {
    const t = i / SR;
    let env = Math.min(1, t / atk);
    if (t > len) env *= Math.max(0, 1 - (t - len) / rel);
    let l = 0, r = 0;
    for (const m of notes) {
      const fq = mtof(m);
      for (const d of [-0.12, 0.12]) {
        const ph = t * fq * Math.pow(2, d / 12);
        const saw = 2 * (ph - Math.floor(ph + 0.5));
        if (d < 0) l += saw; else r += saw;
      }
    }
    const cut = 900 + 300 * Math.sin(t * 1.3);
    add(music, s + i, fl(l, cut, 0.8).lp * env * 0.045 * g, -0.6);
    add(music, s + i, fr(r, cut, 0.8).lp * env * 0.045 * g, 0.6);
  }
}
function bass(t0, midi, len, g = 1) {
  const s = Math.floor(t0 * SR);
  const fq = mtof(midi);
  for (let i = 0; i < SR * len; i++) {
    const t = i / SR;
    const env = Math.min(1, i / 150) * Math.exp(-t * 3) * (t > len - 0.03 ? (len - t) / 0.03 : 1);
    const x = Math.sin(2 * Math.PI * fq * t);
    add(music, s + i, Math.tanh(x * 1.6) * env * 0.3 * g);
  }
}
function bell(t0, midi, g = 1, pan = 0, bus = music) {
  const s = Math.floor(t0 * SR);
  const fq = mtof(midi);
  for (let i = 0; i < SR * 1.6; i++) {
    const t = i / SR;
    const y = (Math.sin(2 * Math.PI * fq * t) + 0.3 * Math.sin(2 * Math.PI * fq * 2.76 * t) * Math.exp(-t * 6)) *
      Math.exp(-t * 3.2) * Math.min(1, i / 30);
    add(bus, s + i, y * 0.09 * g, pan);
    add(verbSend, s + i, y * 0.08 * g);
  }
}

// ---------------------------------------------------------------- SFX
function whoosh(t0, g = 1) {
  const len = 0.5, s = Math.floor((t0 - len * 0.7) * SR); // puncak tepat pada cue
  const f = svf();
  for (let i = 0; i < SR * len; i++) {
    const p = i / (SR * len);
    const env = Math.pow(Math.sin(Math.PI * Math.min(1, p / 0.85)), 2) * (p > 0.85 ? Math.max(0, (1 - p) / 0.15) : 1);
    const y = f(rnd(), 300 + 4500 * p * p, 1.2).bp * env;
    add(sfx, s + i, y * 0.5 * g, -0.6 + 1.2 * p);
  }
}
function pop(t0, g = 1) {
  const s = Math.floor(t0 * SR);
  let ph = 0;
  for (let i = 0; i < SR * 0.12; i++) {
    const t = i / SR;
    ph += (2 * Math.PI * (380 + 900 * Math.exp(-t * 60))) / SR;
    add(sfx, s + i, Math.sin(ph) * Math.exp(-t * 40) * 0.45 * g);
  }
}
function blip(t0, g = 1) {
  const s = Math.floor(t0 * SR);
  let ph = 0;
  for (let i = 0; i < SR * 0.18; i++) {
    const t = i / SR;
    ph += (2 * Math.PI * (700 + 900 * Math.min(1, t / 0.08))) / SR;
    add(sfx, s + i, Math.sin(ph) * Math.exp(-t * 18) * 0.25 * g, 0.2);
  }
}
function click(t0, g = 1) {
  const s = Math.floor(t0 * SR);
  const f = svf();
  for (let i = 0; i < SR * 0.04; i++) {
    const t = i / SR;
    const y = (f(rnd(), 5000, 0.5).hp * 0.6 + Math.sin(2 * Math.PI * 2200 * t)) * Math.exp(-t * 160);
    add(sfx, s + i, y * 0.35 * g);
  }
}
function impact(t0, g = 1) {
  kick(t0, 1.1 * g, sfx);
  const s = Math.floor(t0 * SR);
  const f = svf();
  for (let i = 0; i < SR * 0.9; i++) {
    const t = i / SR;
    const y = f(rnd(), 1800 * Math.exp(-t * 3) + 200, 0.7).lp * Math.exp(-t * 5);
    add(sfx, s + i, y * 0.35 * g);
    add(verbSend, s + i, y * 0.15 * g);
  }
}
function riser(t0, frames, g = 1) {
  const len = f2s(frames), s = Math.floor(t0 * SR);
  const f = svf();
  let ph = 0;
  for (let i = 0; i < SR * len; i++) {
    const p = i / (SR * len);
    ph += (2 * Math.PI * (220 * Math.pow(4, p))) / SR;
    const y = f(rnd(), 400 + 6000 * p * p, 1.5).bp * 0.6 + Math.sin(ph) * 0.12;
    add(sfx, s + i, y * p * p * 0.55 * g);
  }
}
function fizz(t0, g = 1) {
  for (let k = 0; k < 6; k++) pop(t0 + k * 0.055 + 0.01 * rnd(), 0.28 * g);
}
function sparkle(t0, g = 1) {
  [84, 88, 91, 96].forEach((m, k) => bell(t0 + k * 0.07, m, 1.4 * g, -0.5 + k * 0.33, sfx));
}

// ---------------------------------------------------------------- muzik
// F major: Fmaj7 – Am7 – Dm7 – Bbmaj7 (1 bar setiap kord)
const CHORDS = [
  { root: 41, notes: [65, 69, 72, 76] },
  { root: 45, notes: [64, 67, 69, 72] },
  { root: 38, notes: [62, 65, 69, 72] },
  { root: 46, notes: [62, 65, 70, 74] },
];
const S = TL.scenes;
const bars = Math.ceil(DUR / BAR);
for (let b = 0; b < bars; b++) {
  const t = b * BAR;
  const fr = t * FPS;
  const ch = CHORDS[b % 4];
  const sec =
    fr < S.question.from ? "hook" :
    fr < S.explain.from ? "break" :
    fr < S.example.from ? "groove" :
    fr < S.takeaway.from ? "lift" : "outro";

  if (sec !== "hook") pad(t, BAR, ch.notes, sec === "break" || sec === "outro" ? 1.3 : 0.8);

  for (let k = 0; k < 8; k++) {
    const tb = t + (k * BEAT) / 2;
    // arpeggio pluck: hook, groove, lift
    if (sec === "hook" || sec === "groove" || sec === "lift") {
      const n = ch.notes[[0, 2, 1, 3, 2, 1, 3, 2][k]] + (k % 4 === 3 ? 12 : 0);
      pluck(tb, n, sec === "hook" ? 0.9 : 0.7, 0.5, k % 2 ? 0.35 : -0.35);
    }
    if (sec === "groove" || sec === "lift") {
      hat(tb + (k % 2 ? 0.01 : 0), k % 2 ? 1 : 0.55, k === 7);
      if (k % 2 === 0) bass(tb, ch.root + (k === 6 ? 12 : 0), BEAT * 0.45, 1);
    }
    if (sec === "hook" && k % 2 === 1) hat(tb, 0.5);
  }
  for (let q = 0; q < 4; q++) {
    const tb = t + q * BEAT;
    if (sec === "groove" || sec === "lift") {
      kick(tb, q % 2 === 0 ? 0.8 : 0.6);
      if (q % 2 === 1) clap(tb, 0.8);
    }
    if (sec === "hook" && q % 2 === 0) kick(tb, 0.6);
  }
  if (sec === "lift") {
    // melodi atas yang lebih cerah untuk babak produk
    const mel = [[0, 3], [1.5, 2], [2, 1], [3, 0]];
    mel.forEach(([beat, idx]) => bell(t + beat * BEAT, ch.notes[idx] + 12, 0.9, 0.3));
  }
  if (sec === "outro") {
    bell(t, ch.notes[3] + 12, 0.8, 0.3);
    bell(t + BEAT * 1.5, ch.notes[2] + 12, 0.6, -0.3);
  }
}
// kord akhir yang berdering
pad(f2s(870), 0.8, [65, 69, 72, 77], 1.2);

// SFX daripada cue
const FX = { whoosh, pop, blip, click, impact, riser, fizz, sparkle };
for (const c of TL.sfx) {
  const t = f2s(c.f);
  if (c.type === "riser") riser(t, c.len, c.gain ?? 1);
  else FX[c.type](t, c.gain ?? 1);
}

// ---------------------------------------------------------------- reverb (Schroeder ringkas)
function reverb(inp, out, mix) {
  const combs = [1557, 1617, 1491, 1422].map((d) => ({ d, buf: new Float32Array(d), i: 0 }));
  const aps = [225, 556].map((d) => ({ d, buf: new Float32Array(d), i: 0 }));
  for (let ch = 0; ch < 2; ch++) {
    combs.forEach((c) => c.buf.fill(0));
    aps.forEach((a) => a.buf.fill(0));
    const off = ch * 23;
    for (let n = 0; n < N; n++) {
      const x = inp[ch][n];
      let y = 0;
      for (const c of combs) {
        const idx = (c.i + off) % c.d;
        const o = c.buf[idx];
        c.buf[idx] = x + o * 0.8;
        c.i = (c.i + 1) % c.d;
        y += o;
      }
      y *= 0.25;
      for (const a of aps) {
        const o = a.buf[a.i];
        const v = y + o * 0.5;
        a.buf[a.i] = v;
        y = o - v * 0.5;
        a.i = (a.i + 1) % a.d;
      }
      out[ch][n] += y * mix;
    }
  }
}
const verbOut = mk();
reverb(verbSend, verbOut, 0.9);
for (let ch = 0; ch < 2; ch++) for (let n = 0; n < N; n++) music[ch][n] += verbOut[ch][n];

// ---------------------------------------------------------------- envelope & mix
// Tiada VO dalam preview ini -> tiada ducking dialog. Jika VO ditambah kemudian,
// isi VO_RANGES ([fromFrame, toFrame]) dan muzik akan turun ~8 dB di julat itu.
const VO_RANGES = [];
const DUCK = Math.pow(10, -8 / 20);
const fadeOut = f2s(TL.durationInFrames) - 0.6;
function musicGain(t) {
  let g = 1;
  for (const [a, b] of VO_RANGES) {
    const ta = f2s(a), tb = f2s(b);
    if (t > ta - 0.15 && t < tb + 0.3) {
      const k = t < ta ? (ta - t) / 0.15 : t > tb ? (t - tb) / 0.3 : 0;
      g = Math.min(g, DUCK + (1 - DUCK) * Math.min(1, k));
    }
  }
  if (t > fadeOut) g *= Math.max(0, 1 - (t - fadeOut) / 0.6);
  return g;
}

const MUSIC_LVL = 0.62, SFX_LVL = 0.8;
const mix = mk();
let peak = 0;
for (let n = 0; n < N; n++) {
  const g = musicGain(n / SR);
  for (let ch = 0; ch < 2; ch++) {
    music[ch][n] *= g * MUSIC_LVL;
    sfx[ch][n] *= SFX_LVL;
    mix[ch][n] = music[ch][n] + sfx[ch][n];
    peak = Math.max(peak, Math.abs(mix[ch][n]));
  }
}
// normalisasi ke -1 dBFS + limiter lembut (elak clipping)
const target = Math.pow(10, -1 / 20);
const DRIVE = 2.2; // >1 = lebih kuat, puncak dilembutkan oleh tanh
const norm = target / Math.max(peak, 1e-6);
const lim = (x) => target * Math.tanh(x / target);
for (const bus of [mix, music, sfx])
  for (let ch = 0; ch < 2; ch++) for (let n = 0; n < N; n++) bus[ch][n] = lim(bus[ch][n] * norm * DRIVE);

function writeWav(path, bus) {
  const buf = Buffer.alloc(44 + N * 4);
  buf.write("RIFF", 0); buf.writeUInt32LE(36 + N * 4, 4); buf.write("WAVE", 8);
  buf.write("fmt ", 12); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22);
  buf.writeUInt32LE(SR, 24); buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34);
  buf.write("data", 36); buf.writeUInt32LE(N * 4, 40);
  for (let n = 0; n < N; n++)
    for (let ch = 0; ch < 2; ch++)
      buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, bus[ch][n])) * 32767), 44 + n * 4 + ch * 2);
  fs.writeFileSync(path, buf);
}
const out = new URL("../public/audio/", import.meta.url);
writeWav(new URL("mix.wav", out), mix);
writeWav(new URL("music.wav", out), music);
writeWav(new URL("sfx.wav", out), sfx);
console.log(`audio siap: ${DUR}s, peak asal ${peak.toFixed(3)}, gain ${norm.toFixed(3)}`);
