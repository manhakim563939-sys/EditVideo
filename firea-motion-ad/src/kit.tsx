import React from 'react';
import {Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {C, FONT} from './theme';

export const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

// Frame tempatan kepada Sequence: kebanyakan cue dalam timeline.json adalah global,
// jadi setiap babak tolak `from` sendiri.
export const useSpring = (at: number, cfg: {damping?: number; mass?: number; stiffness?: number} = {}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({frame: f - at, fps, config: {damping: 200, mass: 0.7, ...cfg}});
};

// Teks muncul dari bawah garis topeng (mask) — gerakan utama gaya kinetic type.
export const MaskUp: React.FC<{at: number; children: React.ReactNode; style?: React.CSSProperties; from?: 'down' | 'up'}> = ({
  at,
  children,
  style,
  from = 'down',
}) => {
  const p = useSpring(at);
  const off = (1 - p) * 115 * (from === 'down' ? 1 : -1);
  return (
    <div style={{overflow: 'hidden', paddingBottom: '0.06em', ...style}}>
      <div style={{transform: `translateY(${off}%)`}}>{children}</div>
    </div>
  );
};

// Penekanan: skala melantun sekali, kemudian diam.
export const Punch: React.FC<{at: number; children: React.ReactNode; style?: React.CSSProperties; origin?: string}> = ({
  at,
  children,
  style,
  origin = 'center',
}) => {
  const f = useCurrentFrame();
  const p = useSpring(at, {damping: 11, mass: 0.6, stiffness: 160});
  const s = interpolate(p, [0, 1], [1.25, 1]);
  return (
    <div style={{transform: `scale(${s})`, opacity: f < at ? 0 : Math.min(1, p * 3), transformOrigin: origin, ...style}}>
      {children}
    </div>
  );
};

export const FadeIn: React.FC<{at: number; children: React.ReactNode; style?: React.CSSProperties; dy?: number}> = ({
  at,
  children,
  style,
  dy = 24,
}) => {
  const p = useSpring(at);
  return <div style={{opacity: p, transform: `translateY(${(1 - p) * dy}px)`, ...style}}>{children}</div>;
};

// Keluar babak: naik + pudar dalam 8 frame terakhir.
export const useExit = (duration: number, len = 8) => {
  const f = useCurrentFrame();
  const e = interpolate(f, [duration - len, duration], [0, 1], {...clamp, easing: Easing.in(Easing.cubic)});
  return {transform: `translateY(${-e * 90}px)`, opacity: 1 - e};
};

export const H: React.FC<{size: number; color?: string; weight?: number; children: React.ReactNode; style?: React.CSSProperties}> = ({
  size,
  color = C.text,
  weight = 900,
  children,
  style,
}) => (
  <div
    style={{
      fontFamily: FONT,
      fontWeight: weight,
      fontSize: size,
      lineHeight: 1,
      letterSpacing: '-0.02em',
      color,
      whiteSpace: 'nowrap',
      ...style,
    }}
  >
    {children}
  </div>
);

export const Sub: React.FC<{size?: number; color?: string; children: React.ReactNode; style?: React.CSSProperties}> = ({
  size = 46,
  color = C.sub,
  children,
  style,
}) => (
  <div style={{fontFamily: FONT, fontWeight: 500, fontSize: size, lineHeight: 1.25, color, ...style}}>{children}</div>
);

export const Photo: React.FC<{src: string; pos?: string; scale?: number; origin?: string; style?: React.CSSProperties}> = ({
  src,
  pos = 'center',
  scale = 1,
  origin = 'center',
  style,
}) => (
  <Img
    src={staticFile(src)}
    style={{
      width: '100%',
      height: '100%',
      objectFit: 'cover',
      objectPosition: pos,
      transform: `scale(${scale})`,
      transformOrigin: origin,
      ...style,
    }}
  />
);

export const Check: React.FC<{at: number; size?: number}> = ({at, size = 84}) => {
  const p = useSpring(at, {damping: 12, mass: 0.5, stiffness: 180});
  const draw = useSpring(at + 4);
  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: size,
        background: C.accent,
        transform: `scale(${p})`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
      }}
    >
      <svg width={size * 0.56} height={size * 0.56} viewBox="0 0 24 24">
        <path
          d="M4 12.5l5 5L20 6.5"
          fill="none"
          stroke={C.bg}
          strokeWidth={3.4}
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeDasharray={26}
          strokeDashoffset={26 * (1 - draw)}
        />
      </svg>
    </div>
  );
};
