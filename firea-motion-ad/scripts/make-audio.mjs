// Soundtrack instrumental + SFX procedural. Tiada sampel luar, tiada servis berbayar.
// Cue diambil daripada src/timeline.json (sama dengan visual).
import fs from 'node:fs';

const T = JSON.parse(fs.readFileSync(new URL('../src/timeline.json', import.meta.url)));
const SR = 48000;
const LEN = T.durationInFrames / T.fps;
const N = Math.round(LEN * SR);
const L = new Float32Array(N);
const R = new Float32Array(N);
const BEAT = 60 / T.bpm;
const fr = (f) => f / T.fps;
const sec = (k) => (typeof k === 'number' ? fr(k) : fr(T.cues[k]));
const scene = (k) => [fr(T.scenes[k].from), fr(T.scenes[k].to)];

let seed = 12345;
const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296) * 2 - 1;
const mtof = (m) => 440 * 2 ** ((m - 69) / 12);

function add(t0, len, fn, gain = 1, pan = 0) {
  const s0 = Math.round(t0 * SR);
  const n = Math.round(len * SR);
  const gl = gain * Math.cos(((pan + 1) * Math.PI) / 4);
  const gr = gain * Math.sin(((pan + 1) * Math.PI) / 4);
  for (let i = 0; i < n; i++) {
    const j = s0 + i;
    if (j < 0 || j >= N) continue;
    const v = fn(i / SR, i);
    L[j] += v * gl;
    R[j] += v * gr;
  }
}

// ---------------------------------------------------------------- instrumen
const kick = (t, g = 0.9) =>
  add(t, 0.45, (x) => {
    const ph = 2 * Math.PI * (45 * x + (75 / 30) * (1 - Math.exp(-30 * x)));
    return Math.sin(ph) * Math.exp(-x * 7) + (x < 0.004 ? rnd() * 0.3 : 0);
  }, g);

function noiseHit(t, len, decay, hp, g, pan = 0) {
  let prev = 0, lp = 0;
  add(t, len, (x) => {
    const n = rnd();
    const h = n - prev; prev = n; // high-pass kasar
    lp += (h - lp) * hp;
    return lp * Math.exp(-x * decay);
  }, g, pan);
}
const hat = (t, g = 0.12, pan = 0.25) => noiseHit(t, 0.06, 70, 0.9, g, pan);
const clap = (t, g = 0.35) => {
  for (const d of [0, 0.011, 0.022]) noiseHit(t + d, 0.25, d === 0.022 ? 14 : 60, 0.5, g, 0);
};

function bass(t, len, midi, g = 0.32) {
  const f = mtof(midi);
  add(t, len, (x) => {
    const env = Math.min(1, x * 200) * Math.exp(-x * 2.2) * (x > len - 0.02 ? (len - x) / 0.02 : 1);
    return (Math.sin(2 * Math.PI * f * x) + 0.25 * Math.sin(4 * Math.PI * f * x)) * env;
  }, g);
}

function pad(t, len, notes, g = 0.05) {
  notes.forEach((m, k) => {
    const f = mtof(m);
    add(t, len, (x) => {
      const env = Math.min(1, x / 0.35) * Math.min(1, (len - x) / 0.4);
      let v = 0;
      for (const det of [-0.12, 0, 0.12]) v += Math.sin(2 * Math.PI * f * 2 ** (det / 12) * x);
      return (v / 3) * env;
    }, g, (k % 2 ? 0.3 : -0.3));
  });
}

function pluck(t, midi, g = 0.11, pan = 0) {
  const f = mtof(midi);
  add(t, 0.5, (x) => {
    const env = Math.min(1, x * 400) * Math.exp(-x * 9);
    return (Math.sin(2 * Math.PI * f * x) + 0.3 * Math.sin(6 * Math.PI * f * x) * Math.exp(-x * 20)) * env;
  }, g, pan);
}

// ---------------------------------------------------------------- SFX
const SFX = {
  click: (t) => add(t, 0.03, (x) => Math.sin(2 * Math.PI * 2600 * x) * Math.exp(-x * 220), 0.22, 0.1),
  hit: (t) => {
    kick(t, 0.55);
    add(t, 0.05, (x) => Math.sin(2 * Math.PI * 1800 * x) * Math.exp(-x * 120), 0.18);
  },
  pop: (t) =>
    add(t, 0.12, (x) => Math.sin(2 * Math.PI * (500 * x + 3500 * x * x)) * Math.exp(-x * 35), 0.32),
  whoosh: (t) => {
    let lp = 0;
    const len = 0.32;
    add(t - 0.18, len, (x) => {
      const c = 0.02 + 0.35 * Math.sin((Math.PI * x) / len);
      lp += (rnd() - lp) * c;
      return lp * Math.sin((Math.PI * x) / len) ** 2;
    }, 0.5);
  },
  impact: (t) => {
    kick(t, 1.0);
    add(t, 1.2, (x) => Math.sin(2 * Math.PI * 38 * x) * Math.exp(-x * 2.5), 0.35);
    noiseHit(t, 0.6, 7, 0.25, 0.25);
  },
  riser: (t) => {
    const len = sec('story_line') - t;
    let lp = 0;
    add(t, len, (x) => {
      const p = x / len;
      lp += (rnd() - lp) * (0.02 + 0.4 * p * p);
      return lp * p * p * 0.8 + Math.sin(2 * Math.PI * (200 * x + 500 * x * p)) * p * p * 0.12;
    }, 0.45);
  },
  roll: (t) => {
    // tik laju semasa kiraan 100% -> 0%
    for (let i = 0; i < 8; i++) SFX.click(t + i * 0.045 * (1 + i * 0.12));
  },
};

// ---------------------------------------------------------------- aransemen
// Progresi: Fmaj7 - Em7 - Dm7 - Cmaj7 (hangat, feminin, tak gelap)
const CH = [
  {root: 41, pad: [65, 69, 72, 76], arp: [77, 81, 84, 88]},
  {root: 40, pad: [64, 67, 71, 74], arp: [76, 79, 83, 86]},
  {root: 38, pad: [62, 65, 69, 72], arp: [74, 77, 81, 84]},
  {root: 36, pad: [64, 67, 71, 72], arp: [76, 79, 84, 88]},
];
const BAR = BEAT * 4;
const chordAt = (t) => CH[Math.floor(t / BAR) % CH.length];

const [, hookEnd] = scene('hook');
const [probA, probB] = scene('prob');
const [storyA] = scene('story');
const [lifeA, lifeB] = scene('life');
const [ctaA] = scene('cta');

for (let b = 0; b * BEAT < LEN - 0.01; b++) {
  const t = b * BEAT;
  const ch = chordAt(t);
  const inBar = b % 4;
  const hook = t < hookEnd;
  const prob = t >= probA && t < probB;
  const full = (t >= storyA && t < lifeA) || t >= ctaA;
  const brk = t >= lifeA && t < lifeB;

  if (inBar === 0) pad(t, BAR, ch.pad, prob ? 0.035 : brk ? 0.05 : 0.04);

  if (hook) {
    kick(t, 0.7);
    if (b % 2) hat(t + BEAT / 2);
  }
  if (prob) {
    // ketegangan: bass pulse 8th, kick separuh
    if (inBar % 2 === 0) kick(t, 0.6);
    bass(t, BEAT / 2 - 0.02, ch.root, 0.22);
    bass(t + BEAT / 2, BEAT / 2 - 0.02, ch.root, 0.16);
    hat(t + BEAT / 2, 0.09);
  }
  if (full) {
    kick(t, 0.85);
    if (inBar % 2 === 1) clap(t, 0.3);
    hat(t + BEAT / 2, 0.12);
    hat(t, 0.05, -0.25);
    bass(t, BEAT * 0.9, ch.root + (inBar === 3 ? 7 : 0), 0.3);
  }
  if (full || brk) {
    for (let k = 0; k < 2; k++) {
      const idx = (inBar * 2 + k) % 4;
      pluck(t + (k * BEAT) / 2, ch.arp[idx], brk ? 0.09 : 0.075, k ? 0.35 : -0.35);
    }
  }
}

for (const [k, type] of T.sfx) SFX[type](sec(k));

// akhir: kord terakhir berdering, fade 0.4s terakhir
pad(LEN - 1.5, 1.5, CH[0].pad, 0.05);

// ---------------------------------------------------------------- master
let peak = 0;
for (let i = 0; i < N; i++) {
  const fade = Math.min(1, (LEN - i / SR) / 0.4, (i / SR) / 0.005);
  L[i] = Math.tanh(L[i] * 1.1) * fade;
  R[i] = Math.tanh(R[i] * 1.1) * fade;
  peak = Math.max(peak, Math.abs(L[i]), Math.abs(R[i]));
}
const norm = 10 ** (-1.5 / 20) / peak; // puncak -1.5 dBFS
const buf = Buffer.alloc(44 + N * 4);
buf.write('RIFF', 0); buf.writeUInt32LE(36 + N * 4, 4); buf.write('WAVE', 8);
buf.write('fmt ', 12); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22);
buf.writeUInt32LE(SR, 24); buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34);
buf.write('data', 36); buf.writeUInt32LE(N * 4, 40);
for (let i = 0; i < N; i++) {
  buf.writeInt16LE(Math.round(L[i] * norm * 32767), 44 + i * 4);
  buf.writeInt16LE(Math.round(R[i] * norm * 32767), 46 + i * 4);
}
fs.mkdirSync(new URL('../public/audio/', import.meta.url), {recursive: true});
fs.writeFileSync(new URL('../public/audio/soundtrack.wav', import.meta.url), buf);
console.log(`soundtrack.wav ${LEN}s, raw peak ${peak.toFixed(3)}, gain ${norm.toFixed(3)}`);
