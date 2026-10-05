// Soundtrack instrumental + SFX procedural (tiada sampel, tiada servis berbayar).
// Arah audio: tik kertas kering + perkusi lembut; satu aksen kertas setiap reveal.
// Cue dikongsi dengan visual melalui src/timeline.json.
import fs from 'node:fs';

const T = JSON.parse(fs.readFileSync(new URL('../src/timeline.json', import.meta.url)));
const SR = 48000;
const LEN = T.durationInFrames / T.fps;
const N = Math.round(LEN * SR);
const L = new Float32Array(N);
const R = new Float32Array(N);
const BEAT = 60 / T.bpm;
const sec = (k) => (typeof k === 'number' ? k : T.cues[k]) / T.fps;
const scn = (k) => [T.scenes[k].from / T.fps, T.scenes[k].to / T.fps];

let seed = 777;
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

// penapis ringkas dalam closure
const bandNoise = (lpC, hpC) => {
  let lp = 0, hp = 0;
  return () => {
    lp += (rnd() - lp) * lpC;
    hp += (lp - hp) * hpC;
    return lp - hp;
  };
};

// ---------------------------------------------------------------- perkusi lembut
const softKick = (t, g = 0.45) =>
  add(t, 0.35, (x) => Math.sin(2 * Math.PI * (52 * x + 1.2 * (1 - Math.exp(-25 * x)))) * Math.exp(-x * 9) * Math.min(1, x * 300), g);
const rim = (t, g = 0.12, pan = -0.2) =>
  add(t, 0.05, (x) => (Math.sin(2 * Math.PI * 1700 * x) * 0.6 + Math.sin(2 * Math.PI * 820 * x)) * Math.exp(-x * 90), g, pan);
const shaker = (t, g = 0.05, pan = 0.3) => {
  const n = bandNoise(0.9, 0.35);
  add(t, 0.09, (x) => n() * Math.sin((Math.PI * x) / 0.09) ** 2, g, pan);
};

// piano elektrik hangat: sine + harmonik, tremolo perlahan
function keys(t, len, notes, g = 0.05) {
  notes.forEach((m, k) => {
    const f = mtof(m);
    add(t + k * 0.012, len, (x) => {
      const env = Math.min(1, x * 60) * Math.exp(-x * 0.9) * Math.min(1, (len - x) / 0.3);
      const trem = 1 - 0.12 * (0.5 + 0.5 * Math.sin(2 * Math.PI * 4 * x));
      return (Math.sin(2 * Math.PI * f * x) + 0.22 * Math.sin(4 * Math.PI * f * x) * Math.exp(-x * 3)) * env * trem;
    }, g, k % 2 ? 0.25 : -0.25);
  });
}
function bass(t, len, m, g = 0.2) {
  const f = mtof(m);
  add(t, len, (x) => Math.sin(2 * Math.PI * f * x) * Math.min(1, x * 150) * Math.exp(-x * 1.6) * Math.min(1, (len - x) / 0.05), g);
}

// ---------------------------------------------------------------- SFX kertas
const SFX = {
  // kertas diletak: geseran pendek + "tap" redam
  paper: (t) => {
    const n = bandNoise(0.5, 0.08);
    add(t - 0.1, 0.16, (x) => n() * Math.sin((Math.PI * x) / 0.16) ** 2 * (1 + 0.6 * Math.sign(Math.sin(x * 900))), 0.2);
    add(t, 0.06, (x) => Math.sin(2 * Math.PI * 180 * x) * Math.exp(-x * 60), 0.22);
  },
  tick: (t) => add(t, 0.025, (x) => (rnd() * 0.5 + Math.sin(2 * Math.PI * 3100 * x)) * Math.exp(-x * 260), 0.16, 0.15),
  // pita: koyak kecil berderak
  tape: (t) => {
    const n = bandNoise(0.7, 0.2);
    add(t - 0.05, 0.13, (x) => n() * (rnd() > 0.55 ? 1 : 0.25) * Math.exp(-x * 14), 0.16, -0.15);
  },
  // marker: geseran halus sepanjang lukisan (~0.4s), sangat perlahan
  marker: (t) => {
    const n = bandNoise(0.35, 0.12);
    add(t, 0.42, (x) => n() * (0.6 + 0.4 * Math.sin(2 * Math.PI * 9 * x)) * Math.min(1, x * 30) * Math.min(1, (0.42 - x) * 12), 0.09, 0.2);
  },
  // selak halaman
  slide: (t) => {
    const n = bandNoise(0.25, 0.05);
    add(t, 0.27, (x) => n() * Math.sin((Math.PI * x) / 0.27) ** 3, 0.22);
  },
  // cop CTA: hentakan lembut
  stamp: (t) => {
    softKick(t, 0.55);
    SFX.paper(t);
  },
};

// ---------------------------------------------------------------- aransemen (90 BPM)
// Fmaj7 - Am7 - Dm7 - Bbmaj7: hangat, tenang, dokumentari
const CH = [
  {root: 41, n: [57, 60, 64, 65]},
  {root: 45, n: [57, 60, 64, 67]},
  {root: 38, n: [57, 60, 62, 65]},
  {root: 46, n: [57, 58, 62, 65]},
];
const BAR = BEAT * 4;
const [, hookEnd] = scn('hook');
const [, probEnd] = scn('prob');
const [lifeA] = scn('life');
const [ctaA] = scn('cta');

for (let b = 0; b * BEAT < LEN - 0.01; b++) {
  const t = b * BEAT;
  const ch = CH[Math.floor(t / BAR) % CH.length];
  const ib = b % 4;
  const lvl = t < hookEnd ? 0 : t < probEnd ? 1 : t < ctaA ? 2 : 3;

  if (ib === 0) keys(t, BAR, ch.n, 0.055);
  if (ib === 2 && lvl >= 1) keys(t + BEAT / 2, BEAT * 1.4, [ch.n[3] + 12], 0.03);
  // tik jam kertas setiap beat dari awal = denyut naratif
  rim(t, lvl === 0 ? 0.06 : 0.08, 0.25);
  if (lvl >= 1) {
    if (ib === 0 || ib === 2) softKick(t, 0.35);
    shaker(t + BEAT / 2);
  }
  if (lvl >= 2) {
    bass(t, BEAT * 1.9, ch.root + (ib === 2 ? 7 : 0), ib % 2 === 0 ? 0.18 : 0);
    if (ib === 1 || ib === 3) rim(t, 0.13, -0.2);
    shaker(t + BEAT / 4, 0.03, -0.3);
  }
  if (lvl === 2 && t >= lifeA) shaker(t + (3 * BEAT) / 4, 0.03);
}
for (const [k, type] of T.sfx) SFX[type](sec(k));
keys(LEN - 2.2, 2.2, CH[0].n.concat([72]), 0.05); // kord penutup

// ---------------------------------------------------------------- master
let peak = 0;
for (let i = 0; i < N; i++) {
  const fade = Math.min(1, (LEN - i / SR) / 0.5, (i / SR) / 0.005);
  L[i] = Math.tanh(L[i] * 1.2) * fade;
  R[i] = Math.tanh(R[i] * 1.2) * fade;
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
