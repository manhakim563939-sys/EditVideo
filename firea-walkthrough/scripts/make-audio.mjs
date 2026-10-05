// Audio PILIHAN (brief: muzik & SFX optional). Tiada VO dibekalkan -> penyampaian text-led.
// Muzik latar lembut + SFX halus yang diambil terus daripada keyframe kamera dalam src/timeline.json.
// Untuk versi tanpa muzik: tukar MUSIC = false.
import fs from 'node:fs';

const MUSIC = true;
const T = JSON.parse(fs.readFileSync(new URL('../src/timeline.json', import.meta.url)));
const SR = 48000;
const LEN = T.durationInFrames / T.fps;
const N = Math.round(LEN * SR);
const L = new Float32Array(N);
const R = new Float32Array(N);
const BEAT = 60 / T.bpm;
const fr = (f) => f / T.fps;

let seed = 4242;
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
    const v = fn(i / SR);
    L[j] += v * gl;
    R[j] += v * gr;
  }
}

// ---------------------------------------------------------------- SFX
// gerakan kamera: angin lembut sepanjang gerakan (tiada bunyi "handheld")
const move = (t, len, g = 0.12) => {
  let lp = 0;
  add(t, len, (x) => {
    const e = Math.sin((Math.PI * x) / len) ** 2;
    lp += (rnd() - lp) * (0.02 + 0.08 * e);
    return lp * e;
  }, g);
};
const tick = (t, g = 0.09) => add(t, 0.03, (x) => Math.sin(2 * Math.PI * 2200 * x) * Math.exp(-x * 200), g, 0.1);
const cut = (t) => add(t, 0.25, (x) => Math.sin(2 * Math.PI * (60 + 60 * Math.exp(-x * 25)) * x) * Math.exp(-x * 12), 0.25);
const chime = (t) => [76, 83].forEach((m, i) => add(t + i * 0.08, 1.0, (x) => Math.sin(2 * Math.PI * mtof(m) * x) * Math.exp(-x * 3.5) * Math.min(1, x * 300), 0.06, i ? 0.3 : -0.3));

// ---------------------------------------------------------------- muzik latar (lembut, rendah)
function keys(t, len, notes, g) {
  notes.forEach((m, k) =>
    add(t + k * 0.015, len, (x) => {
      const env = Math.min(1, x * 80) * Math.exp(-x * 1.1) * Math.min(1, (len - x) / 0.3);
      const f = mtof(m);
      return (Math.sin(2 * Math.PI * f * x) + 0.18 * Math.sin(4 * Math.PI * f * x) * Math.exp(-x * 4)) * env;
    }, g, k % 2 ? 0.25 : -0.25),
  );
}
const softKick = (t) => add(t, 0.3, (x) => Math.sin(2 * Math.PI * (50 + 50 * Math.exp(-x * 30)) * x) * Math.exp(-x * 10) * Math.min(1, x * 400), 0.22);
const brush = (t, g = 0.035) => {
  let lp = 0;
  add(t, 0.18, (x) => {
    lp += (rnd() - lp) * 0.5;
    return (rnd() - lp) * Math.exp(-x * 18);
  }, g, -0.15);
};

if (MUSIC) {
  // Dmaj9 - Bm9 - Gmaj7 - A6 : tenang, "semakan" yang yakin
  const CH = [[62, 66, 69, 73, 76], [59, 62, 66, 69, 73], [55, 59, 62, 66, 71], [57, 61, 64, 66, 69]];
  const BAR = BEAT * 4;
  const firstStep = fr(T.steps[0].from);
  for (let b = 0; b * BEAT < LEN - 0.01; b++) {
    const t = b * BEAT;
    const ib = b % 4;
    if (ib === 0) keys(t, BAR, CH[Math.floor(t / BAR) % 4], 0.035);
    if (t >= firstStep) {
      if (ib === 0 || ib === 2) softKick(t);
      if (ib === 1 || ib === 3) brush(t);
      brush(t + BEAT / 2, 0.015);
    }
  }
}

// gerakan kamera daripada keyframe yang benar-benar berubah
for (const s of T.shots) {
  cut(fr(s.from));
  for (let i = 0; i < s.keys.length - 1; i++) {
    const a = s.keys[i];
    const b = s.keys[i + 1];
    if (a.x !== b.x || a.y !== b.y || a.z !== b.z) move(fr(a.f), fr(b.f - a.f));
  }
}
for (const st of T.steps) tick(fr(st.from), 0.12);
for (const c of T.captions) tick(fr(c.from), 0.06);
for (const b of T.boxes) tick(fr(b.from), 0.08);
chime(fr(T.cta.btn));
keys(LEN - 2.2, 2.2, [62, 66, 69, 73, 78], 0.035);

// ---------------------------------------------------------------- master
let peak = 0;
for (let i = 0; i < N; i++) {
  const fade = Math.min(1, (LEN - i / SR) / 0.5, (i / SR) / 0.005);
  L[i] = Math.tanh(L[i] * 1.1) * fade;
  R[i] = Math.tanh(R[i] * 1.1) * fade;
  peak = Math.max(peak, Math.abs(L[i]), Math.abs(R[i]));
}
const norm = 10 ** (-3 / 20) / peak; // puncak -3 dBFS: latar lembut
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
console.log(`soundtrack.wav ${LEN}s, music=${MUSIC}, raw peak ${peak.toFixed(3)}`);
