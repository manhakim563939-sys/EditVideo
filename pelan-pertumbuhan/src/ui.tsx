import React from "react";
import { Easing, interpolate } from "remotion";
import { C, F, goldFill } from "./theme";

export const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// 0→1 with a little overshoot, starting at time s (seconds, scene-local)
export const pop = (t: number, s: number, d = 0.45) =>
  interpolate(t, [s, s + d], [0, 1], { easing: Easing.out(Easing.back(1.5)), ...clamp });
export const rise = (t: number, s: number, d = 0.6) =>
  interpolate(t, [s, s + d], [0, 1], { easing: Easing.out(Easing.cubic), ...clamp });
export const draw = (t: number, s: number, d = 0.8) =>
  interpolate(t, [s, s + d], [0, 1], { easing: Easing.inOut(Easing.cubic), ...clamp });

export type Scene = {
  id: string;
  kind: string;
  phase?: number;
  dur: number;
  cueT: Record<string, number>;
  [k: string]: unknown;
};

/** Fades/slides an element in at `at` (scene seconds). */
export const In: React.FC<{ t: number; at: number; y?: number; x?: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ t, at, y = 30, x = 0, children, style }) => {
  const p = rise(t, at);
  return <div style={{ opacity: p, transform: `translate(${(1 - p) * x}px, ${(1 - p) * y}px)`, ...style }}>{children}</div>;
};

export const Eyebrow: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div style={{ fontFamily: F.sans, fontWeight: 600, fontSize: 24, letterSpacing: 9, color: C.gold, textTransform: "uppercase", ...style }}>{children}</div>
);

export const Chip: React.FC<{ children: React.ReactNode; p: number; gold?: boolean; style?: React.CSSProperties }> = ({ children, p, gold, style }) => (
  <div
    style={{
      display: "inline-flex",
      alignItems: "center",
      gap: 14,
      padding: "14px 26px",
      borderRadius: 999,
      border: `2px solid ${gold ? "transparent" : C.line}`,
      background: gold ? goldFill : "rgba(243,234,214,0.06)",
      color: gold ? C.ink : C.cream,
      fontFamily: F.sans,
      fontWeight: 500,
      fontSize: 30,
      opacity: Math.min(1, p * 1.4),
      transform: `scale(${0.7 + 0.3 * p})`,
      whiteSpace: "nowrap",
      ...style,
    }}
  >
    {children}
  </div>
);

export const Ring: React.FC<{ size?: number; p?: number; children: React.ReactNode; filled?: boolean; style?: React.CSSProperties }> = ({ size = 120, p = 1, children, filled, style }) => (
  <div
    style={{
      width: size,
      height: size,
      borderRadius: size / 2,
      border: `2px solid ${C.gold}`,
      background: filled ? goldFill : "rgba(10,30,25,0.55)",
      boxShadow: `0 0 0 8px rgba(216,180,106,0.07), 0 12px 40px rgba(0,0,0,0.35)`,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      transform: `scale(${p})`,
      opacity: Math.min(1, p * 1.5),
      flexShrink: 0,
      ...style,
    }}
  >
    {children}
  </div>
);

/** Stroke-only line icons in the deck's style. */
export const Icon: React.FC<{ name: string; size?: number; color?: string; sw?: number }> = ({ name, size = 64, color = C.gold, sw = 2.4 }) => {
  const g = { fill: "none", stroke: color, strokeWidth: sw, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };
  const paths: Record<string, React.ReactNode> = {
    target: (<><circle cx="24" cy="24" r="17" /><circle cx="24" cy="24" r="10.5" /><circle cx="24" cy="24" r="4" /><path d="M24 24l14-14M33 9h5v5" /></>),
    gear: (<><circle cx="24" cy="24" r="6" /><path d="M24 6v6M24 36v6M6 24h6M36 24h6M11.3 11.3l4.2 4.2M32.5 32.5l4.2 4.2M11.3 36.7l4.2-4.2M32.5 15.5l4.2-4.2" /><circle cx="24" cy="24" r="12" /></>),
    people: (<><circle cx="17" cy="17" r="6" /><path d="M6 38c0-7 5-11 11-11s11 4 11 11" /><circle cx="33" cy="15" r="5" /><path d="M30 26c6-1 12 3 12 10M36 6v6M33 9h6" /></>),
    rocket: (<><path d="M24 5c7 6 9 15 6 25h-12c-3-10-1-19 6-25z" /><circle cx="24" cy="18" r="3.5" /><path d="M18 30l-5 6 7-1M30 30l5 6-7-1M21 36l3 7 3-7" /></>),
    billboard: (<><rect x="6" y="7" width="36" height="20" rx="2" /><path d="M12 14h18M12 20h11M18 27v14M30 27v14M14 41h20" /></>),
    camera: (<><rect x="5" y="14" width="38" height="26" rx="4" /><path d="M16 14l3-6h10l3 6" /><circle cx="24" cy="27" r="7" /></>),
    store: (<><path d="M7 19l3-11h28l3 11M7 19c0 3 2.5 5 5.5 5S18 22 18 19c0 3 2.5 5 6 5s6-2 6-5c0 3 2.5 5 5.5 5S41 22 41 19M7 19h34" /><path d="M10 24v17h28V24M20 41V31h8v10" /></>),
    handshake: (<><path d="M4 20l8-8 8 4 6-3 8 3 10 6" /><path d="M12 24l9 9c2 2 4 2 5 0l8-8" /><path d="M17 29l5-5M21 33l4-4M28 23l-6-3-5 4" /></>),
    building: (<><rect x="9" y="6" width="20" height="36" /><path d="M29 18h10v24H9M14 12h3M21 12h3M14 19h3M21 19h3M14 26h3M21 26h3M17 42v-8h4v8M33 24h2M33 30h2M33 36h2" /></>),
    briefcase: (<><rect x="5" y="14" width="38" height="26" rx="3" /><path d="M17 14V9h14v5M5 25h38M21 25v4h6v-4" /></>),
    chat: (<><path d="M24 7C14 7 6 14 6 23c0 4 1.5 7 4 10l-2 8 8-3c2.5 1 5 2 8 2 10 0 18-7 18-17S34 7 24 7z" /><path d="M17 23h.01M24 23h.01M31 23h.01" /></>),
    scissors: (<><circle cx="12" cy="34" r="6" /><circle cx="12" cy="14" r="6" /><path d="M17 17l25 19M17 31l25-19" /></>),
    hook: (<><path d="M5 9h38M10 9v4c0 9-2 22-4 28h11c-2-8-2-20 0-32M38 9v4c0 9 2 22 4 28H31c2-8 2-20 0-32" /></>),
    ruler: (<><rect x="4" y="17" width="40" height="14" rx="2" /><path d="M11 17v6M18 17v8M25 17v6M32 17v8M39 17v6" /></>),
    house: (<><path d="M6 22L24 7l18 15" /><path d="M11 18v22h26V18M20 40V29h8v11" /></>),
    key: (<><circle cx="15" cy="30" r="8" /><path d="M21 24l17-17M31 14l4 4M35 10l4 4" /></>),
    pin: (<><path d="M24 4c-8 0-14 6-14 14 0 11 14 26 14 26s14-15 14-26c0-8-6-14-14-14z" /><circle cx="24" cy="18" r="5" /></>),
    check: (<path d="M10 25l9 9 19-20" />),
    doc: (<><path d="M12 5h17l8 8v30H12z" /><path d="M29 5v8h8M17 21h14M17 28h14M17 35h9" /></>),
    play: (<path d="M17 12l20 12-20 12z" />),
    bed: (<><path d="M5 38V12M5 28h38v10M43 28v-6c0-3-2-5-5-5H22v11" /><circle cx="13" cy="22" r="4" /></>),
    office: (<><rect x="7" y="8" width="34" height="34" /><path d="M14 15h6M28 15h6M14 23h6M28 23h6M14 31h6M28 31h6M21 42v-6h6v6" /></>),
    user: (<><circle cx="24" cy="16" r="8" /><path d="M9 42c0-9 7-14 15-14s15 5 15 14" /></>),
    up: (<path d="M24 40V9M12 21L24 9l12 12" />),
    ticket: (<><path d="M5 15h38v6a4 4 0 000 8v6H5v-6a4 4 0 000-8z" /><path d="M30 15v20" strokeDasharray="3 3" /></>),
    star: (<path d="M24 6l5.5 11.5 12.5 1.6-9.2 8.6 2.4 12.4L24 34l-11.2 6.1 2.4-12.4L6 19.1l12.5-1.6z" />),
    gift: (<><rect x="6" y="18" width="36" height="24" rx="2" /><path d="M4 12h40v6H4zM24 12v30M24 12c-4-6-12-6-12-1s8 1 12 1c4 0 12 4 12-1s-8-5-12 1" /></>),
  };
  return (
    <svg width={size} height={size} viewBox="0 0 48 48" style={{ display: "block" }}>
      <g {...g}>{paths[name] ?? null}</g>
    </svg>
  );
};
