// Kamera maya atas foto pegun: hanya crop/pan/zoom — tiada sudut pandang baharu.
import T from './timeline.json';

export type Shot = (typeof T.shots)[number];
export const W = 1080;
export const H = 1920;
export const ANCHOR = {x: 540, y: 820}; // fokus dipaparkan di sini (atas kad kapsyen)

const ease = (x: number) => (x < 0.5 ? 4 * x * x * x : 1 - (-2 * x + 2) ** 3 / 2);
const clampN = (v: number, a: number, b: number) => (b < a ? (a + b) / 2 : Math.max(a, Math.min(b, v)));

export const camera = (shot: Shot, f: number) => {
  const K = shot.keys;
  // kekal pada keyframe terakhir yang sudah lepas; interpolasi ke keyframe seterusnya
  let i = 0;
  while (i < K.length - 1 && f >= K[i + 1].f) i++;
  const a = K[i];
  const b = K[i + 1];
  let {x, y, z} = a;
  if (b && f > a.f) {
    const t = ease((f - a.f) / (b.f - a.f));
    x = a.x + (b.x - a.x) * t;
    y = a.y + (b.y - a.y) * t;
    z = Math.exp(Math.log(a.z) + (Math.log(b.z) - Math.log(a.z)) * t); // zoom sekata
  }
  // kekalkan viewport dalam foto: tiada kawasan kosong yang direka
  const left = clampN(x - ANCHOR.x / z, 0, shot.sw - W / z);
  const top = clampN(y - ANCHOR.y / z, 0, shot.sh - H / z);
  return {left, top, z};
};

export const shotAt = (f: number) => T.shots.find((s) => f >= s.from && f < s.to) ?? T.shots[T.shots.length - 1];
