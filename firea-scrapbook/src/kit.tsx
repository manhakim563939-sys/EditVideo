import React from 'react';
import {AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {C, MARKER, SANS} from './theme';

export const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const rng = (seed: number) => () => {
  seed |= 0;
  seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

// Tepi koyak: poligon bergerigi dalam piksel, ditukar ke peratus kotak.
export const torn = (seed: number, w: number, h: number, jag = 7, step = 26, sides = 'trbl') => {
  const r = rng(seed);
  const P: string[] = [];
  const pt = (x: number, y: number) => P.push(`${((x / w) * 100).toFixed(2)}% ${((y / h) * 100).toFixed(2)}%`);
  const n = (len: number) => Math.max(2, Math.round(len / step));
  const j = (s: string) => (sides.includes(s) ? r() * jag : 0);
  for (let i = 0, k = n(w); i <= k; i++) pt((i / k) * w, j('t'));
  for (let i = 1, k = n(h); i <= k; i++) pt(w - j('r'), (i / k) * h);
  for (let i = 1, k = n(w); i <= k; i++) pt(w - (i / k) * w, h - j('b'));
  for (let i = 1, k = n(h); i < k; i++) pt(j('l'), h - (i / k) * h);
  return `polygon(${P.join(',')})`;
};

// Gerakan stop-start: lapisan "dihentak" ke tempat dengan sedikit lajakan, kemudian diam.
export const useLand = (at: number) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = spring({frame: f - at, fps, config: {damping: 15, mass: 0.45, stiffness: 230}});
  return {p, visible: f >= at};
};

type LayerProps = {
  at: number;
  x: number;
  y: number;
  rot?: number;
  from?: [number, number];
  depth?: number;
  drift?: number;
  children: React.ReactNode;
  style?: React.CSSProperties;
};

// Lapisan kertas: masuk dari offset `from`, rotasi mendap, parallax kecil ikut `depth`.
export const Layer: React.FC<LayerProps> = ({at, x, y, rot = 0, from = [0, 90], depth = 1, drift = 0, children, style}) => {
  const {p, visible} = useLand(at);
  if (!visible) return null;
  const tx = from[0] * (1 - p);
  const ty = from[1] * (1 - p) + drift * depth;
  const r = rot + (1 - p) * (from[0] >= 0 ? 4 : -4);
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        transform: `translate(${tx}px, ${ty}px) rotate(${r}deg) scale(${1 + (1 - p) * 0.05})`,
        opacity: Math.min(1, p * 4),
        ...style,
      }}
    >
      {children}
    </div>
  );
};

export type Crop = {src: string; sw: number; cx: number; cy: number; cw: number};
// petakan koordinat piksel foto sumber -> koordinat dalam kotak foto selebar w
export const mapCrop = (c: Crop, w: number) => {
  const s = w / c.cw;
  return (sx: number, sy: number): [number, number] => [(sx - c.cx) * s, (sy - c.cy) * s];
};

const PAD = 18;
export const Print: React.FC<{crop: Crop; w: number; h: number; seed: number; children?: React.ReactNode}> = ({
  crop,
  w,
  h,
  seed,
  children,
}) => {
  const s = w / crop.cw;
  const W = w + PAD * 2;
  const H = h + PAD * 2;
  return (
    <div style={{position: 'relative', width: W, height: H, filter: 'drop-shadow(0 12px 16px rgba(40,25,10,0.28))'}}>
      <div style={{position: 'absolute', inset: 0, background: C.card, clipPath: torn(seed, W, H, 9, 24)}} />
      <div style={{position: 'absolute', left: PAD, top: PAD, width: w, height: h, overflow: 'hidden'}}>
        <Img
          src={staticFile(crop.src)}
          style={{position: 'absolute', width: crop.sw * s, left: -crop.cx * s, top: -crop.cy * s, maxWidth: 'none'}}
        />
      </div>
      <div style={{position: 'absolute', left: PAD, top: PAD, width: w, height: h}}>{children}</div>
    </div>
  );
};

export const Tape: React.FC<{at: number; x: number; y: number; w?: number; rot?: number; seed?: number}> = ({
  at,
  x,
  y,
  w = 190,
  rot = -8,
  seed = 3,
}) => {
  const {p, visible} = useLand(at);
  if (!visible) return null;
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width: w,
        height: 56,
        background: C.tape,
        clipPath: torn(seed, w, 56, 6, 8, 'lr'),
        transform: `rotate(${rot}deg) scale(${1.25 - 0.25 * p})`,
        opacity: Math.min(1, p * 3),
        mixBlendMode: 'multiply',
      }}
    />
  );
};

// Jalur kertas koyak untuk headline.
export const Strip: React.FC<{seed: number; w: number; h: number; children: React.ReactNode; bg?: string}> = ({
  seed,
  w,
  h,
  children,
  bg = C.card,
}) => (
  <div style={{position: 'relative', width: w, height: h, filter: 'drop-shadow(0 8px 10px rgba(40,25,10,0.22))'}}>
    <div style={{position: 'absolute', inset: 0, background: bg, clipPath: torn(seed, w, h, 8, 22)}} />
    <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', paddingLeft: 40}}>{children}</div>
  </div>
);

export const Head: React.FC<{size: number; color?: string; children: React.ReactNode; style?: React.CSSProperties}> = ({
  size,
  color = C.ink,
  children,
  style,
}) => (
  <div
    style={{
      fontFamily: SANS,
      fontWeight: 900,
      fontSize: size,
      lineHeight: 1.02,
      letterSpacing: '-0.025em',
      color,
      whiteSpace: 'nowrap',
      ...style,
    }}
  >
    {children}
  </div>
);

export const Body: React.FC<{size?: number; children: React.ReactNode; style?: React.CSSProperties}> = ({size = 40, children, style}) => (
  <div style={{fontFamily: SANS, fontWeight: 500, fontSize: size, color: C.ink, lineHeight: 1.25, ...style}}>{children}</div>
);

// Tulisan marker: didedahkan kiri->kanan seperti sedang ditulis.
export const Note: React.FC<{at: number; size?: number; len?: number; children: React.ReactNode; style?: React.CSSProperties; color?: string}> = ({
  at,
  size = 52,
  len = 14,
  children,
  style,
  color = C.accent,
}) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const p = interpolate(f, [at, at + len], [0, 100], clamp);
  return (
    <div
      style={{
        fontFamily: MARKER,
        fontSize: size,
        color,
        lineHeight: 1.15,
        whiteSpace: 'nowrap',
        clipPath: `inset(-20% ${100 - p}% -20% -5%)`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

// Garisan anotasi dilukis (path SVG) dalam ruang koordinat induk.
export const Draw: React.FC<{at: number; d: string; len?: number; width?: number; color?: string}> = ({
  at,
  d,
  len = 12,
  width = 7,
  color = C.accent,
}) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const p = interpolate(f, [at, at + len], [0, 1], {...clamp, easing: Easing.out(Easing.quad)});
  return (
    <svg style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}} width={1} height={1}>
      <path
        d={d}
        pathLength={1}
        fill="none"
        stroke={color}
        strokeWidth={width}
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeDasharray={1}
        strokeDashoffset={1 - p}
      />
    </svg>
  );
};

export const arrow = (x1: number, y1: number, x2: number, y2: number, bend = 0.25) => {
  const mx = (x1 + x2) / 2 - (y2 - y1) * bend;
  const my = (y1 + y2) / 2 + (x2 - x1) * bend;
  const a = Math.atan2(y2 - my, x2 - mx);
  const hl = 30;
  const h1 = [x2 - hl * Math.cos(a - 0.5), y2 - hl * Math.sin(a - 0.5)];
  const h2 = [x2 - hl * Math.cos(a + 0.5), y2 - hl * Math.sin(a + 0.5)];
  return `M${x1},${y1} Q${mx},${my} ${x2},${y2} M${h1[0]},${h1[1]} L${x2},${y2} L${h2[0]},${h2[1]}`;
};

// Bulatan tangan: sedikit lebih satu pusingan, jejari bergoyang.
export const scribbleEllipse = (cx: number, cy: number, rx: number, ry: number, seed = 1) => {
  const r = rng(seed);
  const pts: string[] = [];
  const start = -2.2;
  for (let i = 0; i <= 40; i++) {
    const t = start + (i / 40) * Math.PI * 2.15;
    const k = 1 + (r() - 0.5) * 0.04 + (i / 40) * 0.06;
    pts.push(`${(cx + Math.cos(t) * rx * k).toFixed(1)},${(cy + Math.sin(t) * ry * k).toFixed(1)}`);
  }
  return `M${pts.join(' L')}`;
};

export const roughRect = (x: number, y: number, w: number, h: number) =>
  `M${x + 6},${y - 4} L${x + w + 4},${y + 3} L${x + w - 3},${y + h + 4} L${x - 4},${y + h - 2} L${x + 2},${y - 10}`;

// Latar kertas hangat: tekstur turbulence statik (tiada goncangan) + vignette lembut.
export const Paper: React.FC = () => (
  <AbsoluteFill style={{background: C.paper}}>
    <svg width="1080" height="1920" style={{position: 'absolute', opacity: 0.55, mixBlendMode: 'multiply'}}>
      <filter id="fib">
        <feTurbulence type="fractalNoise" baseFrequency="0.9 0.35" numOctaves={3} seed={4} />
        <feColorMatrix values="0 0 0 0 0.55  0 0 0 0 0.45  0 0 0 0 0.32  0 0 0 0.35 0" />
      </filter>
      <rect width="1080" height="1920" filter="url(#fib)" />
    </svg>
    <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(80,55,25,0.22) 100%)'}} />
  </AbsoluteFill>
);

// Keluar babak: halaman diselak ke kiri dalam 8 frame terakhir.
export const useExit = (dur: number) => {
  const f = useCurrentFrame();
  const e = interpolate(f, [dur - 8, dur], [0, 1], {...clamp, easing: Easing.in(Easing.cubic)});
  return {transform: `translateX(${-e * 1150}px) rotate(${-e * 3}deg)`};
};

export const useDrift = (dur: number) => {
  const f = useCurrentFrame();
  return interpolate(f, [0, dur], [6, -6]);
};
