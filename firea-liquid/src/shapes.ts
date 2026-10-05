// Sistem bentuk cecair: 3 bentuk (A merah jambu, B krim, C merah jambu) yang morph
// berterusan antara keyframe babak. Setiap bentuk = N titik bermula dari atas, ikut jam,
// jadi morph titik-ke-titik antara bulatan / blob / titisan / pil kekal licin.
import T from './timeline.json';

export type Kind = 'circle' | 'blob' | 'drop' | 'pill';
export type Spec = {k: Kind; cx: number; cy: number; w: number; h?: number; amp?: number};
const N = 96;

const S = T.scenes;
const ORDER = ['hook', 'prob', 'story', 'usp', 'zero', 'life', 'cta'] as const;
// morph ke babak seterusnya bermula 8 frame sebelum babak tamat (selepas teks keluar)
export const MORPH_AT = ORDER.slice(0, -1).map((k) => S[k].to - 8);
export const MORPH_LEN = T.morphLen;
const INTRO_LEN = 22;

// [A, B, C] untuk setiap babak (separuh lebar/tinggi dalam px)
export const KEYS: Spec[][] = [
  // hook: blob besar + bingkai bulat foto 1
  [{k: 'blob', cx: 700, cy: 600, w: 430, h: 470, amp: 0.07}, {k: 'circle', cx: 500, cy: 640, w: 335}, {k: 'blob', cx: 190, cy: 1060, w: 70, amp: 0.1}],
  // masalah: blob jadi titisan peluh, titisan kecil terpisah
  [{k: 'drop', cx: 540, cy: 720, w: 290, amp: 0.02}, {k: 'circle', cx: 540, cy: 760, w: 0}, {k: 'drop', cx: 840, cy: 360, w: 52, amp: 0.02}],
  // produk: titisan mendarat jadi pelantar + bingkai pil foto 3
  [{k: 'blob', cx: 540, cy: 640, w: 420, h: 540, amp: 0.06}, {k: 'pill', cx: 540, cy: 640, w: 300, h: 440}, {k: 'blob', cx: 890, cy: 1170, w: 44, amp: 0.1}],
  // USP: bingkai mengecil ke atas, ruang untuk teks
  [{k: 'blob', cx: 540, cy: 540, w: 340, h: 430, amp: 0.07}, {k: 'pill', cx: 540, cy: 540, w: 240, h: 340}, {k: 'blob', cx: 170, cy: 250, w: 40, amp: 0.1}],
  // 0%: pecah jadi dua bulatan stabil
  [{k: 'circle', cx: 300, cy: 760, w: 220}, {k: 'circle', cx: 540, cy: 760, w: 0}, {k: 'circle', cx: 780, cy: 760, w: 220}],
  // gaya hidup: bergabung semula, bingkai pil foto 2
  [{k: 'blob', cx: 540, cy: 640, w: 410, h: 500, amp: 0.07}, {k: 'pill', cx: 540, cy: 640, w: 330, h: 410}, {k: 'blob', cx: 180, cy: 1130, w: 38, amp: 0.1}],
  // CTA: bingkai bulat foto 5
  [{k: 'blob', cx: 540, cy: 560, w: 380, h: 400, amp: 0.07}, {k: 'circle', cx: 540, cy: 560, w: 305}, {k: 'blob', cx: 870, cy: 900, w: 50, amp: 0.1}],
];
const START: Spec[] = KEYS[0].map((s) => ({...s, w: 0, h: 0}));

const base = (s: Spec): [number, number][] => {
  const w = s.w;
  const h = s.h ?? s.w;
  const P: [number, number][] = [];
  for (let i = 0; i < N; i++) {
    const t = -Math.PI / 2 + (2 * Math.PI * i) / N;
    const c = Math.cos(t);
    const sn = Math.sin(t);
    let x = c * w;
    let y = sn * h;
    if (s.k === 'pill') {
      x = w * Math.sign(c) * Math.abs(c) ** 0.4;
      y = h * Math.sign(sn) * Math.abs(sn) ** 0.4;
    } else if (s.k === 'drop') {
      const u = Math.max(0, -sn);
      y -= h * 0.8 * u ** 6;
      x *= 1 - 0.3 * u ** 2;
    }
    P.push([s.cx + x, s.cy + y]);
  }
  return P;
};

const ease = (x: number) => (x < 0.5 ? 4 * x * x * x : 1 - (-2 * x + 2) ** 3 / 2);

// keadaan morph pada frame f: segmen (indeks babak asal) + progres 0..1
export const morphState = (f: number) => {
  if (f < INTRO_LEN) return {from: -1, to: 0, t: ease(f / INTRO_LEN)};
  for (let i = MORPH_AT.length - 1; i >= 0; i--) {
    if (f >= MORPH_AT[i]) return {from: i, to: i + 1, t: ease(Math.min(1, (f - MORPH_AT[i]) / MORPH_LEN))};
  }
  return {from: 0, to: 0, t: 1};
};

export const shapePoints = (idx: number, f: number, inset = 0): [number, number][] => {
  const {from, to, t} = morphState(f);
  const a = from < 0 ? START[idx] : KEYS[from][idx];
  const b = KEYS[to][idx];
  const pa = base(a);
  const pb = base(b);
  const amp = (a.amp ?? 0) * (1 - t) + (b.amp ?? 0) * t;
  const seed = idx * 1.7;
  const cx = a.cx * (1 - t) + b.cx * t;
  const cy = a.cy * (1 - t) + b.cy * t;
  return pa.map(([x0, y0], i) => {
    let x = x0 * (1 - t) + pb[i][0] * t;
    let y = y0 * (1 - t) + pb[i][1] * t;
    const th = (2 * Math.PI * i) / N;
    const m = 1 + amp * (0.55 * Math.sin(3 * th + f * 0.035 + seed) + 0.3 * Math.sin(5 * th - f * 0.025 + 2 * seed) + 0.15 * Math.sin(2 * th + f * 0.02));
    const dx = x - cx;
    const dy = y - cy;
    const r = Math.hypot(dx, dy) || 1;
    const k = Math.max(0, (r * m - inset) / r);
    x = cx + dx * k;
    y = cy + dy * k;
    return [x, y];
  });
};

// Catmull-Rom tertutup -> Bezier kubik
export const toPath = (P: [number, number][]) => {
  const n = P.length;
  let d = `M${P[0][0].toFixed(1)},${P[0][1].toFixed(1)}`;
  for (let i = 0; i < n; i++) {
    const p0 = P[(i - 1 + n) % n];
    const p1 = P[i];
    const p2 = P[(i + 1) % n];
    const p3 = P[(i + 2) % n];
    const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
    const c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
    d += ` C${c1[0].toFixed(1)},${c1[1].toFixed(1)} ${c2[0].toFixed(1)},${c2[1].toFixed(1)} ${p2[0].toFixed(1)},${p2[1].toFixed(1)}`;
  }
  return d + 'Z';
};
