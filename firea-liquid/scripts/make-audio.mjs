// Soundtrack instrumental + SFX procedural (tiada sampel, tiada servis berbayar).
// Arah audio: sweep tonal licin + groove perkusi elastik yang lembut.
// Cue daripada src/timeline.json; sweep morph guna formula sama dengan src/shapes.ts (babak tamat - 8).
import fs from 'node:fs';

const T = JSON.parse(fs.readFileSync(new URL('../src/timeline.json', import.meta.url)));
const SR = 48000;
const LEN = T.durationInFrames / T.fps;
const N = Math.round(LEN * SR);
const L = new Float32Array(N);
const R = new Float32Array(N);
const BEAT = 60 / T.bpm;
const fr = (f) => f / T.fps;
const sec = (k) => fr(typeof k === 'number' ? k : T.cues[k]);
const ORDER = ['hook', 'prob', 'story', 'usp', 'zero', 'life', 'cta'];
const MORPHS = ORDER.slice(0, -1).map((k) => fr(T.scenes[k].to - 8));
const MORPH_LEN = fr(T.morphLen);

let seed = 99;
const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296) * 2 - 1;
const mtof = (m) => 440 * 2 ** ((m - 69) / 12);

function add(t0, len, fn, gain = 1, pan = 0) {
  const s0 = Math.round(t0 * SR);
  const n = Math.round(len * SR);
  const gl = gain * Math.cos(((pan + 1) * Math.PI) / 4);
  const gr = gain * Math.sin(((pan + 1) * Math.PI) / 4);
  let ph = 0;
  for (let i = 0; i < n; i++) {
    const j = s0 + i;
    if (j < 0 || j >= N) continue;
    const v = fn(i / SR, i);
    L[j] += v * gl;
    R[j] += v * gr;
  }
}
// osilator dengan frekuensi berubah (fasa terkumpul)
function glide(t0, len, freqFn, ampFn, gain = 1, pan = 0, harm = 0) {
  let ph = 0;
  add(t0, len, (x) => {
    ph += (2 * Math.PI * freqFn(x)) / SR;
    return (Math.sin(ph) + harm * Math.sin(2 * ph)) * ampFn(x);
  }, gain, pan);
}

// ---------------------------------------------------------------- groove elastik
const kick = (t, g = 0.5) =>
  glide(t, 0.4, (x) => 48 + 110 * Math.exp(-x * 22), (x) => Math.min(1, x * 400) * Math.exp(-x * 7.5), g);
const boing = (t, m, g = 0.07, pan = 0.3) => {
  const f = mtof(m);
  glide(t, 0.22, (x) => f * (1 + 0.35 * Math.exp(-x * 30) * Math.cos(x * 70)), (x) => Math.min(1, x * 300) * Math.exp(-x * 16), g, pan);
};
const snap = (t, g = 0.16) => {
  let lp = 0, hp = 0;
  add(t, 0.14, (x) => {
    lp += (rnd() - lp) * 0.6;
    hp += (lp - hp) * 0.15;
    return (lp - hp) * Math.exp(-x * 35);
  }, g, -0.1);
};
const shaker = (t, g = 0.035, pan = 0.35) => {
  let hp = 0;
  add(t, 0.08, (x) => {
    const n = rnd();
    const v = n - hp;
    hp = n;
    return v * Math.sin((Math.PI * x) / 0.08) ** 2;
  }, g, pan);
};

function pad(t, len, notes, g = 0.04) {
  notes.forEach((m, k) => {
    for (const det of [-0.08, 0.08]) {
      const f = mtof(m) * 2 ** (det / 12);
      add(t, len, (x) => {
        const env = Math.min(1, x / 0.5) * Math.min(1, (len - x) / 0.5);
        return (Math.sin(2 * Math.PI * f * x) + 0.12 * Math.sin(6 * Math.PI * f * x)) * env;
      }, g / 2, det < 0 ? -0.35 : 0.35);
    }
  });
}
// bass bulat dengan glide (rasa "elastik") ke nota seterusnya
function bass(t, len, m, mNext, g = 0.2) {
  const f1 = mtof(m);
  const f2 = mtof(mNext);
  glide(t, len, (x) => (x > len - 0.08 ? f1 + (f2 - f1) * ((x - (len - 0.08)) / 0.08) : f1),
    (x) => Math.min(1, x * 120) * (0.6 + 0.4 * Math.exp(-x * 4)) * Math.min(1, (len - x) / 0.02), g, 0, 0.15);
}

// ---------------------------------------------------------------- SFX
const SFX = {
  // titisan air: sine naik pantas
  bloop: (t) => glide(t, 0.16, (x) => 380 + 1300 * (1 - Math.exp(-x * 30)), (x) => Math.min(1, x * 500) * Math.exp(-x * 22), 0.14),
  tick: (t) => add(t, 0.02, (x) => Math.sin(2 * Math.PI * 2400 * x) * Math.exp(-x * 300), 0.08, 0.15),
  swell: (t) => pad(t, 1.6, [63, 70, 74], 0.05),
  // sweep tonal sepanjang morph: dua sine meluncur + angin lembut
  sweep: (t, up = true) => {
    const len = MORPH_LEN + 0.25;
    const a = up ? 330 : 990;
    const b = up ? 990 : 330;
    const env = (x) => Math.sin((Math.PI * x) / len) ** 2;
    const fx = (x) => a * (b / a) ** ((1 - Math.cos((Math.PI * x) / len)) / 2);
    glide(t, len, fx, env, 0.07, -0.3);
    glide(t, len, (x) => fx(x) * 1.5, env, 0.04, 0.3);
    let lp = 0;
    add(t, len, (x) => {
      lp += (rnd() - lp) * (0.03 + 0.12 * env(x));
      return lp * env(x);
    }, 0.18);
  },
};

// ---------------------------------------------------------------- aransemen (100 BPM)
// Ebmaj7 - Cm7 - Abmaj7 - Bb6 : hangat & lembut
const CH = [
  {root: 39, pad: [63, 67, 70, 74], top: 82},
  {root: 36, pad: [63, 67, 70, 72], top: 79},
  {root: 44, pad: [63, 67, 68, 72], top: 80},
  {root: 46, pad: [62, 65, 67, 70], top: 77},
];
const BAR = BEAT * 4;
const sceneAt = (t) => ORDER.findLast((k) => fr(T.scenes[k].from) <= t);

for (let b = 0; b * BEAT < LEN - 0.01; b++) {
  const t = b * BEAT;
  const bi = Math.floor(t / BAR);
  const ch = CH[bi % 4];
  const nx = CH[(bi + 1) % 4];
  const ib = b % 4;
  const sc = sceneAt(t);
  const thin = sc === 'prob';
  const full = !['hook', 'prob'].includes(sc);

  if (ib === 0) pad(t, BAR, ch.pad, thin ? 0.03 : 0.04);
  if (!thin || ib === 0) kick(t, thin ? 0.35 : 0.45);
  if (ib === 1 || ib === 3) snap(t, thin ? 0.08 : 0.14);
  shaker(t + BEAT / 2, full ? 0.04 : 0.025);
  if (full) shaker(t + BEAT / 4, 0.02, -0.35);
  if (!thin && (ib === 1 || ib === 3)) boing(t + BEAT / 2, ch.top - (ib === 3 ? 5 : 0));
  if (full) {
    if (ib === 0) bass(t, BEAT * 1.5, ch.root, ch.root + 7);
    if (ib === 2) bass(t, BEAT * 2, ch.root + 7, nx.root);
  }
}
MORPHS.forEach((t, i) => SFX.sweep(t, i % 2 === 0));
for (const [k, type] of T.sfx) SFX[type](sec(k));
pad(LEN - 2.4, 2.4, CH[0].pad.concat([75]), 0.05);

// ---------------------------------------------------------------- master
let peak = 0;
for (let i = 0; i < N; i++) {
  const fade = Math.min(1, (LEN - i / SR) / 0.5, (i / SR) / 0.005);
  L[i] = Math.tanh(L[i] * 1.15) * fade;
  R[i] = Math.tanh(R[i] * 1.15) * fade;
  peak = Math.max(peak, Math.abs(L[i]), Math.abs(R[i]));
}
const norm = 10 ** (-1.5 / 20) / peak;
const buf = Buffer.alloc(44 + N * 4);
buf.write('RIFF', 0); buf.writeUInt32LE(36 + N * 4, 4); buf.write('WAVE', 8);
buf.write('fmt ', 12); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22);
buf.writeUInt32LE(SR, 24); buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34);
buf.write('data', 36); buf.writeUInt32LE(N * 4, 40);
for (let i = 0; i < N; i++) {
  buf.writeInt16LE(Math.round(L[i] * norm * 32767), 44 + i * 4);
  buf.writeInt16LE(Math.round(R[i] * norm * 32767), 46 + i * 4);
}
fs.writeFileSync(new URL('../public/audio/soundtrack.wav', import.meta.url), buf);
console.log(`soundtrack.wav ${LEN}s, raw peak ${peak.toFixed(3)}, gain ${norm.toFixed(2)}`);
