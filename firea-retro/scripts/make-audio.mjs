// Soundtrack instrumental + SFX procedural (tiada sampel, tiada servis berbayar).
// Arah audio: nada antara muka disintesis + denyut chiptune ringan. Original, bukan bunyi OS sebenar.
// Cue daripada src/timeline.json (frame tempatan babak -> masa global).
import fs from 'node:fs';

const T = JSON.parse(fs.readFileSync(new URL('../src/timeline.json', import.meta.url)));
const SR = 48000;
const LEN = T.durationInFrames / T.fps;
const N = Math.round(LEN * SR);
const L = new Float32Array(N);
const R = new Float32Array(N);
const BEAT = 60 / T.bpm;
const starts = {};
let acc = 0;
for (const s of T.scenes) { starts[s.id] = acc; acc += s.len; }
const gsec = (id, f) => (starts[id] + f) / T.fps;

let seed = 31337;
const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296) * 2 - 1;
const mtof = (m) => 440 * 2 ** ((m - 69) / 12);
const sq = (ph, duty = 0.5) => ((ph / (2 * Math.PI)) % 1 < duty ? 1 : -1);
const tri = (ph) => { const p = (ph / (2 * Math.PI)) % 1; return 4 * Math.abs(p - 0.5) - 1; };

function add(t0, len, fn, gain = 1, pan = 0) {
  const s0 = Math.round(t0 * SR);
  const n = Math.round(len * SR);
  const gl = gain * Math.cos(((pan + 1) * Math.PI) / 4);
  const gr = gain * Math.sin(((pan + 1) * Math.PI) / 4);
  for (let i = 0; i < n; i++) {
    const j = s0 + i;
    if (j < 0 || j >= N) continue;
    const v = fn(i / SR);
    L[j] += v * gl;
    R[j] += v * gr;
  }
}
const note = (t, len, m, {g = 0.05, duty = 0.5, wave = 'sq', decay = 6, pan = 0, bend = 0} = {}) => {
  let ph = 0;
  const f0 = mtof(m);
  add(t, len, (x) => {
    ph += (2 * Math.PI * f0 * (1 + bend * x)) / SR;
    const env = Math.min(1, x * 400) * Math.exp(-x * decay) * Math.min(1, (len - x) / 0.01);
    return (wave === 'tri' ? tri(ph) : sq(ph, duty)) * env;
  }, g, pan);
};
const noise = (t, len, g = 0.05, decay = 40, pan = 0) => add(t, len, (x) => rnd() * Math.exp(-x * decay), g, pan);

// ---------------------------------------------------------------- SFX antara muka
const SFX = {
  open: (t) => { note(t, 0.06, 79, {g: 0.07, duty: 0.25}); note(t + 0.06, 0.09, 86, {g: 0.07, duty: 0.25}); },
  close: (t) => { note(t, 0.06, 84, {g: 0.06, duty: 0.25}); note(t + 0.06, 0.09, 77, {g: 0.06, duty: 0.25}); },
  type: (t) => { for (let i = 0; i < 9; i++) noise(t + i * 0.045 + (rnd() * 0.01), 0.02, 0.05, 160, 0.2); },
  alert: (t) => { note(t, 0.12, 81, {g: 0.08, duty: 0.5}); note(t + 0.14, 0.18, 76, {g: 0.08, duty: 0.5}); },
  blip: (t) => note(t, 0.07, 88, {g: 0.05, duty: 0.125, decay: 20}),
  check: (t) => { note(t, 0.05, 84, {g: 0.06, duty: 0.25}); note(t + 0.05, 0.14, 91, {g: 0.06, duty: 0.25, decay: 12}); },
  click: (t) => noise(t, 0.03, 0.12, 120),
  drag: (t) => { for (let i = 0; i < 6; i++) note(t + i * 0.16, 0.05, 60 + (i % 2) * 3, {g: 0.03, duty: 0.25, decay: 30}); },
  drop: (t) => { note(t, 0.15, 48, {g: 0.12, wave: 'tri', bend: -1.5, decay: 14}); [84, 88, 91].forEach((m, i) => note(t + 0.08 + i * 0.06, 0.12, m, {g: 0.05, duty: 0.25})); },
  fanfare: (t) => [72, 76, 79, 84].forEach((m, i) => note(t + i * 0.09, i === 3 ? 0.6 : 0.1, m, {g: 0.06, duty: 0.25, decay: i === 3 ? 3 : 10})),
};

// ---------------------------------------------------------------- chiptune pulse (120 BPM)
// C - Am - F - G (cerah), bahagian "amaran" guna Am - F sahaja
const CH = [
  {root: 48, arp: [60, 64, 67, 72]},
  {root: 45, arp: [57, 60, 64, 69]},
  {root: 41, arp: [57, 60, 65, 69]},
  {root: 43, arp: [59, 62, 67, 71]},
];
const sceneAt = (t) => { let id = T.scenes[0].id; for (const s of T.scenes) if (starts[s.id] / T.fps <= t) id = s.id; return id; };
const BAR = BEAT * 4;
for (let b = 0; b * BEAT < LEN - 0.01; b++) {
  const t = b * BEAT;
  const sc = sceneAt(t);
  const tense = sc === 'prob';
  const ch = tense ? CH[1 + (Math.floor(t / BAR) % 2)] : CH[Math.floor(t / BAR) % 4];
  const ib = b % 4;
  const full = !['hook', 'prob'].includes(sc);
  // bass segi tiga 8th
  note(t, BEAT / 2 - 0.02, ch.root, {g: 0.11, wave: 'tri', decay: 3});
  note(t + BEAT / 2, BEAT / 2 - 0.02, ch.root + (tense ? 0 : 12), {g: 0.08, wave: 'tri', decay: 3});
  // kick & hat noise
  if (!tense || ib % 2 === 0) note(t, 0.1, 40, {g: 0.13, wave: 'tri', bend: -6, decay: 25});
  noise(t + BEAT / 2, 0.03, 0.025, 120, 0.3);
  if (full && (ib === 1 || ib === 3)) noise(t, 0.09, 0.04, 30, -0.1);
  // arpeggio pulse lembut (16th) bila isi bermula
  if (full) for (let k = 0; k < 4; k++) note(t + (k * BEAT) / 4, BEAT / 4 - 0.01, ch.arp[k] + 12, {g: 0.022, duty: 0.125, decay: 10, pan: k % 2 ? 0.35 : -0.35});
}

for (const [id, f, type] of T.sfx) SFX[type](gsec(id, f));

// ---------------------------------------------------------------- master
let peak = 0;
for (let i = 0; i < N; i++) {
  const fade = Math.min(1, (LEN - i / SR) / 0.5, (i / SR) / 0.005);
  // tapis lulus-rendah satu kutub ringan supaya gelombang segi empat tak terlalu tajam
  L[i] = Math.tanh(L[i] * 1.1) * fade;
  R[i] = Math.tanh(R[i] * 1.1) * fade;
}
let pl = 0, pr = 0;
for (let i = 0; i < N; i++) {
  pl += (L[i] - pl) * 0.45; pr += (R[i] - pr) * 0.45;
  L[i] = pl; R[i] = pr;
  peak = Math.max(peak, Math.abs(pl), Math.abs(pr));
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
console.log(`soundtrack.wav ${LEN}s, raw peak ${peak.toFixed(3)}`);
