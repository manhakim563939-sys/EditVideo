import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {BODY, C, PIXEL} from './theme';

// Animasi "snap" berperingkat (gaya retro): skala melompat 5 langkah, 2 frame setiap satu.
const OPEN = [0.15, 0.4, 0.7, 0.92, 1];
export const snapScale = (f: number, open: number, close = Infinity) => {
  if (f < open) return 0;
  if (f >= close) {
    const i = Math.floor((f - close) / 2);
    return i >= OPEN.length - 1 ? 0 : OPEN[OPEN.length - 2 - i];
  }
  const i = Math.floor((f - open) / 2);
  return i >= OPEN.length ? 1 : OPEN[i];
};

export const bevel = (depth = 4) =>
  `inset ${depth}px ${depth}px 0 ${C.light}, inset -${depth}px -${depth}px 0 ${C.shadow}`;

export const Desktop: React.FC = () => (
  <AbsoluteFill
    style={{
      background: C.desk,
      backgroundImage: `radial-gradient(${C.deskDot} 2px, transparent 2.2px)`,
      backgroundSize: '16px 16px',
    }}
  />
);

export const MenuBar: React.FC<{items: string[]}> = ({items}) => (
  <div
    style={{
      position: 'absolute', left: 0, top: 0, width: 1080, height: 66, background: C.face,
      borderBottom: `4px solid ${C.ink}`, display: 'flex', alignItems: 'center', gap: 44, paddingLeft: 36,
      fontFamily: PIXEL, fontSize: 40, color: C.ink,
    }}
  >
    <span style={{color: C.title}}>◆</span>
    {items.map((t) => (
      <span key={t}>{t}</span>
    ))}
  </div>
);

type WinProps = {
  x: number; y: number; w: number; h: number; title: string; open: number; close?: number;
  status?: string; children?: React.ReactNode; pad?: number;
};
// Tetingkap retro generik (original): bingkai pixel, bevel, bayang keras, bar tajuk maroon.
export const Win: React.FC<WinProps> = ({x, y, w, h, title, open, close, status, children, pad = 0}) => {
  const f = useCurrentFrame();
  const s = snapScale(f, open, close);
  if (s <= 0) return null;
  const ready = f >= open + 10 && (close === undefined || f < close);
  return (
    <div
      style={{
        position: 'absolute', left: x, top: y, width: w, height: h, transform: `scale(${s})`,
        background: C.face, border: `4px solid ${C.ink}`, boxShadow: `${bevel()}, 12px 12px 0 rgba(42,22,34,0.35)`,
        display: 'flex', flexDirection: 'column', padding: 6,
      }}
    >
      <div
        style={{
          height: 60, flexShrink: 0, background: C.title, display: 'flex', alignItems: 'center',
          justifyContent: 'space-between', padding: '0 14px 0 18px',
        }}
      >
        <span style={{fontFamily: PIXEL, fontSize: 42, color: C.face, lineHeight: 1}}>{title}</span>
        <span style={{display: 'flex', gap: 10}}>
          {[0, 1].map((i) => (
            <span key={i} style={{width: 30, height: 30, background: C.face, border: `3px solid ${C.ink}`, boxShadow: bevel(3)}} />
          ))}
        </span>
      </div>
      <div style={{flex: 1, position: 'relative', overflow: 'hidden', padding: pad, opacity: ready ? 1 : 0}}>{children}</div>
      {status && (
        <div
          style={{
            height: 46, flexShrink: 0, marginTop: 6, boxShadow: `inset 3px 3px 0 ${C.shadow}, inset -3px -3px 0 ${C.light}`,
            fontFamily: PIXEL, fontSize: 36, color: C.ink, display: 'flex', alignItems: 'center', padding: '0 16px',
            opacity: ready ? 1 : 0, whiteSpace: 'nowrap', overflow: 'hidden',
          }}
        >
          {status}
        </div>
      )}
    </div>
  );
};

export const Photo: React.FC<{src: string; pos?: string}> = ({src, pos = 'center'}) => (
  <Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: pos, display: 'block'}} />
);

// Teks ditaip aksara demi aksara, dengan kursor blok berkelip.
export const Typed: React.FC<{text: string; at: number; size: number; color?: string; cps?: number; caret?: boolean}> = ({
  text, at, size, color = C.ink, cps = 1.3, caret = true,
}) => {
  const f = useCurrentFrame();
  if (f < at) return <div style={{height: size * 1.15}} />;
  const n = Math.min(text.length, Math.floor((f - at) * cps) + 1);
  const typing = n < text.length;
  const showCaret = caret && (typing || Math.floor(f / 8) % 2 === 0);
  return (
    <div style={{fontFamily: BODY, fontWeight: 800, fontSize: size, lineHeight: 1.15, color, whiteSpace: 'nowrap', letterSpacing: '-0.01em'}}>
      {text.slice(0, n)}
      {showCaret && <span style={{display: 'inline-block', width: size * 0.45, height: size * 0.85, background: color, marginLeft: 6, verticalAlign: '-0.1em'}} />}
    </div>
  );
};

export const Big: React.FC<{size: number; color?: string; weight?: number; children: React.ReactNode; style?: React.CSSProperties}> = ({
  size, color = C.ink, weight = 800, children, style,
}) => (
  <div style={{fontFamily: BODY, fontWeight: weight, fontSize: size, lineHeight: 1.1, color, letterSpacing: '-0.01em', ...style}}>{children}</div>
);

export const Pix: React.FC<{size: number; color?: string; children: React.ReactNode; style?: React.CSSProperties}> = ({
  size, color = C.ink, children, style,
}) => <div style={{fontFamily: PIXEL, fontSize: size, lineHeight: 1.05, color, ...style}}>{children}</div>;

// Muncul secara "snap" (tiada fade panjang).
export const Snap: React.FC<{at: number; children: React.ReactNode; style?: React.CSSProperties}> = ({at, children, style}) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const s = snapScale(f, at);
  return <div style={{transform: `scale(${s})`, transformOrigin: 'left center', ...style}}>{children}</div>;
};

export const CheckRow: React.FC<{at: number; label: string}> = ({at, label}) => {
  const f = useCurrentFrame();
  const on = f >= at;
  const pop = on ? snapScale(f, at) : 1;
  return (
    <div style={{display: 'flex', alignItems: 'center', gap: 30, height: 96}}>
      <div style={{width: 66, height: 66, background: C.light, border: `4px solid ${C.ink}`, boxShadow: `inset 3px 3px 0 ${C.shadow}`, position: 'relative'}}>
        {on && (
          <svg width={58} height={58} viewBox="0 0 12 12" shapeRendering="crispEdges" style={{position: 'absolute', left: 0, top: 0, transform: `scale(${pop})`}}>
            {/* tanda semak pixel */}
            {[[2, 6], [3, 7], [4, 8], [5, 7], [6, 6], [7, 5], [8, 4], [9, 3], [3, 6], [4, 7], [5, 6], [6, 5], [7, 4], [8, 3]].map(([x, y], i) => (
              <rect key={i} x={x} y={y} width={1} height={1} fill={C.title} />
            ))}
          </svg>
        )}
      </div>
      <Big size={66} color={on ? C.ink : 'rgba(42,22,34,0.35)'}>{label}</Big>
    </div>
  );
};

export const AlertIcon: React.FC<{size?: number}> = ({size = 130}) => (
  <svg width={size} height={size} viewBox="0 0 13 13" shapeRendering="crispEdges">
    <polygon points="6.5,0.5 12.5,12 0.5,12" fill={C.pink} stroke={C.ink} strokeWidth={0.8} strokeLinejoin="miter" />
    <rect x={6} y={4} width={1} height={4.5} fill={C.ink} />
    <rect x={6} y={9.5} width={1} height={1} fill={C.ink} />
  </svg>
);

// Kursor anak panah pixel generik.
export const Cursor: React.FC<{x: number; y: number; down?: boolean}> = ({x, y, down}) => (
  <svg width={56} height={80} viewBox="0 0 14 20" shapeRendering="crispEdges" style={{position: 'absolute', left: x, top: y, transform: `scale(${down ? 0.9 : 1})`, transformOrigin: '0 0', filter: 'drop-shadow(4px 4px 0 rgba(42,22,34,0.35))'}}>
    <path d="M1 1 L1 16 L5 12 L8 19 L11 18 L8 11 L13 11 Z" fill={C.ink} stroke={C.light} strokeWidth={1.2} strokeLinejoin="miter" />
  </svg>
);

export const RetroButton: React.FC<{children: React.ReactNode; scale?: number}> = ({children, scale = 1}) => (
  <div
    style={{
      background: C.title, border: `4px solid ${C.ink}`, boxShadow: `inset 4px 4px 0 #C2577C, inset -4px -4px 0 #5A0F2A, 8px 8px 0 rgba(42,22,34,0.35)`,
      padding: '22px 50px', fontFamily: BODY, fontWeight: 800, fontSize: 46, color: C.face, letterSpacing: '0.02em',
      transform: `scale(${scale})`, display: 'inline-block',
    }}
  >
    {children}
  </div>
);
