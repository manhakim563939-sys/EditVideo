// Komponen motion boleh guna semula
import React from "react";
import { AbsoluteFill, Easing, Img, interpolate, spring, staticFile, useVideoConfig } from "remotion";
import { C, sans } from "./theme";

export const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
export const lerp = (f: number, i: [number, number], o: [number, number], ease = Easing.out(Easing.cubic)) =>
  interpolate(f, i, o, { ...clamp, easing: ease });

export const useSpring = () => {
  const { fps } = useVideoConfig();
  return (f: number, at: number, cfg: Partial<{ damping: number; stiffness: number; mass: number }> = {}) =>
    spring({ frame: f - at, fps, config: { damping: 13, stiffness: 170, mass: 0.7, ...cfg } });
};

// Teks kinetik perkataan-demi-perkataan. *perkataan* = aksen warna.
export const Words: React.FC<{
  f: number; at: number; text: string; size: number; color?: string; accent?: string;
  weight?: number; stagger?: number; family?: string; align?: "left" | "center"; lh?: number;
  style?: React.CSSProperties;
}> = ({ f, at, text, size, color = C.ink, accent = C.maroon, weight = 800, stagger = 3, family = sans, align = "center", lh = 1.12, style }) => {
  const sp = useSpring();
  const words = text.split(" ");
  return (
    <div style={{ fontFamily: family, fontSize: size, fontWeight: weight, color, lineHeight: lh, textAlign: align, letterSpacing: -0.5, ...style }}>
      {words.map((w, i) => {
        const p = sp(f, at + i * stagger, { damping: 15, stiffness: 190 });
        const acc = w.startsWith("*");
        const clean = w.replace(/\*/g, "");
        return (
          <span key={i} style={{
            display: "inline-block", marginRight: size * 0.24, opacity: Math.min(1, p * 1.6),
            transform: `translateY(${(1 - p) * size * 0.55}px) scale(${0.85 + 0.15 * p})`,
            color: acc ? accent : undefined,
          }}>{clean}</span>
        );
      })}
    </div>
  );
};

// Pil "sticker" yang pop masuk
export const Pill: React.FC<{
  f: number; at: number; children: React.ReactNode; bg?: string; color?: string; size?: number; rotate?: number;
  style?: React.CSSProperties;
}> = ({ f, at, children, bg = C.maroon, color = C.white, size = 52, rotate = 0, style }) => {
  const sp = useSpring();
  const p = sp(f, at, { damping: 10, stiffness: 220 });
  return (
    <div style={{
      position: "absolute", fontFamily: sans, fontWeight: 700, fontSize: size, color, background: bg,
      padding: `${size * 0.28}px ${size * 0.62}px`, borderRadius: 999, whiteSpace: "nowrap",
      boxShadow: "0 14px 34px rgba(74,15,36,0.22)", opacity: p > 0.02 ? 1 : 0,
      transform: `scale(${p}) rotate(${rotate * p}deg)`, ...style,
    }}>{children}</div>
  );
};

// Kad foto bergaya sticker
export const PhotoCard: React.FC<{
  src: string; f: number; at: number; w: number; h: number; x: number; y: number; rotate?: number;
  zoom?: [number, number, number]; focus?: string; border?: number;
}> = ({ src, f, at, w, h, x, y, rotate = 0, zoom = [1, 1.08, 120], focus = "50% 40%", border = 14 }) => {
  const sp = useSpring();
  const p = sp(f, at, { damping: 14, stiffness: 120 });
  const z = lerp(f, [at, at + zoom[2]], [zoom[0], zoom[1]], Easing.linear);
  return (
    <div style={{
      position: "absolute", left: x, top: y, width: w, height: h, background: C.white, padding: border,
      borderRadius: 34, boxShadow: "0 30px 60px rgba(74,15,36,0.25)", opacity: Math.min(1, p * 2),
      transform: `translateY(${(1 - p) * 120}px) rotate(${rotate}deg) scale(${0.9 + 0.1 * p})`,
    }}>
      <div style={{ width: "100%", height: "100%", overflow: "hidden", borderRadius: 24 }}>
        <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: focus, transform: `scale(${z})`, transformOrigin: focus }} />
      </div>
    </div>
  );
};

// Bentuk lembut bergerak untuk latar
export const Blobs: React.FC<{ f: number; color: string; opacity?: number }> = ({ f, color, opacity = 0.5 }) => (
  <AbsoluteFill style={{ opacity }}>
    {[[-180, 120, 620, 0], [640, 1180, 720, 1.7], [520, -160, 460, 3.1]].map(([x, y, s, ph], i) => (
      <div key={i} style={{
        position: "absolute", left: x + 40 * Math.sin(f / 50 + ph), top: y + 50 * Math.cos(f / 60 + ph),
        width: s, height: s, borderRadius: "50%", background: color, filter: "blur(30px)",
      }} />
    ))}
  </AbsoluteFill>
);

// Transisi wipe: menutup skrin tepat pada sempadan babak `at`, kemudian membuka
export const Wipe: React.FC<{ f: number; at: number; color: string; kind: "up" | "left" | "iris" }> = ({ f, at, color, kind }) => {
  if (f < at - 10 || f > at + 10) return null;
  const inP = lerp(f, [at - 10, at], [0, 1], Easing.inOut(Easing.cubic));
  const outP = lerp(f, [at, at + 10], [0, 1], Easing.inOut(Easing.cubic));
  if (kind === "iris") {
    const r = f <= at ? inP * 1200 : 1200 * (1 - outP);
    return <AbsoluteFill style={{ background: color, clipPath: `circle(${r}px at 50% 50%)` }} />;
  }
  const t = f <= at ? (1 - inP) * 100 : -outP * 100;
  const tr = kind === "up" ? `translateY(${t}%)` : `translateX(${t}%)`;
  return <AbsoluteFill style={{ background: color, transform: tr }} />;
};

// Titisan peluh (SVG)
export const Drop: React.FC<{ size: number; color?: string; style?: React.CSSProperties }> = ({ size, color = C.aqua, style }) => (
  <svg width={size} height={size * 1.3} viewBox="0 0 100 130" style={style}>
    <path d="M50 4 C50 4 12 58 12 84 a38 38 0 0 0 76 0 C88 58 50 4 50 4Z" fill={color} />
    <ellipse cx="36" cy="82" rx="8" ry="14" fill="white" opacity="0.5" />
  </svg>
);
