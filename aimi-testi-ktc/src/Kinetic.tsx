import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import tl from "./timeline.json";
import { C, F, goldGrad, goldText } from "./theme";
import { FxAbove, FxBelow } from "./Fx";

const BELOW = ["blur", "questions", "swatch", "steps", "counter", "underline"];

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const MAXW = 860; // text column width (safe from TikTok/Reels side buttons)
const LEFT = 70;

type Line = { t: string; at: number; big?: boolean };
type Beat = (typeof tl.beats)[number];

// Fit a line to the column: Montserrat Black caps ≈ 0.74em per glyph.
const fit = (text: string, target: number) => Math.min(target, Math.floor(MAXW / (text.replace(/\*/g, "").length * 0.74)));

const parse = (s: string) => {
  // *gold words*
  const out: { w: string; gold: boolean }[] = [];
  let gold = false;
  for (const tok of s.split(" ")) {
    let w = tok;
    const open = w.startsWith("*");
    if (open) { gold = true; w = w.slice(1); }
    const close = w.endsWith("*");
    if (close) w = w.slice(0, -1);
    out.push({ w, gold });
    if (close) gold = false;
  }
  return out;
};

const Word: React.FC<{ w: string; gold: boolean; t: number; at: number; size: number; big?: boolean }> = ({ w, gold, t, at, size, big }) => {
  const p = interpolate(t, [at, at + (big ? 0.22 : 0.16)], [0, 1], { easing: Easing.out(Easing.back(big ? 2.2 : 1.6)), ...clamp });
  const blur = interpolate(t, [at, at + 0.1], [8, 0], clamp);
  return (
    <span style={{ display: "inline-block", overflow: "visible", marginRight: size * 0.22 }}>
      <span
        style={{
          display: "inline-block",
          transform: `translateY(${(1 - p) * size * 0.7}px) scale(${big ? 1.35 - 0.35 * p : 1})`,
          transformOrigin: "50% 80%",
          opacity: Math.min(1, p * 1.6),
          filter: `blur(${blur}px) ${gold ? "drop-shadow(0 6px 14px rgba(0,0,0,0.55))" : ""}`,
          fontFamily: F.kin,
          fontWeight: 900,
          fontSize: size,
          lineHeight: 1.02,
          letterSpacing: -1,
          ...(gold ? goldText : { color: C.white, textShadow: "0 6px 18px rgba(0,0,0,0.6), 0 2px 4px rgba(0,0,0,0.5)" }),
        }}
      >
        {w}
      </span>
    </span>
  );
};

const KLine: React.FC<{ line: Line; t: number; size: number }> = ({ line, t, size }) => {
  const words = parse(line.t);
  return (
    <div style={{ whiteSpace: "nowrap" }}>
      {words.map((x, i) => (
        <Word key={i} w={x.w} gold={x.gold} t={t} at={line.at + i * 0.06} size={size} big={line.big} />
      ))}
    </div>
  );
};

const Steps: React.FC<{ cur: number; t: number; s: number }> = ({ cur, t, s }) => {
  const labels = ["UKUR", "JAHIT", "PASANG"];
  const p = interpolate(t, [s, s + 0.2], [0, 1], clamp);
  return (
    <div style={{ display: "flex", gap: 14, marginBottom: 26, opacity: p }}>
      {labels.map((l, i) => {
        const on = i + 1 === cur;
        const done = i + 1 < cur;
        return (
          <div key={l} style={{ fontFamily: F.kin, fontWeight: 800, fontSize: 30, letterSpacing: 2, padding: "10px 22px", borderRadius: 999, background: on ? goldGrad : done ? "rgba(217,179,94,0.35)" : "rgba(0,0,0,0.45)", color: on ? C.ink : C.white, border: `2px solid ${on || done ? C.gold : "rgba(255,255,255,0.35)"}`, transform: `scale(${on ? 1.08 : 1})` }}>
            {done ? "✓ " : `${i + 1}. `}{l}
          </div>
        );
      })}
    </div>
  );
};

const Swatches: React.FC<{ t: number; s: number }> = ({ t, s }) => {
  const cols = ["#8E9AA6", "#C9B79C", "#6B4A3A", "#D6A6B4", "#3E5F55", "#E8E1D3", "#A47A33"];
  return (
    <div style={{ display: "flex", gap: 12, marginTop: 24 }}>
      {cols.map((c, i) => {
        const p = interpolate(t, [s + 0.5 + i * 0.07, s + 0.75 + i * 0.07], [0, 1], { easing: Easing.out(Easing.back(2)), ...clamp });
        return <div key={i} style={{ width: 92, height: 120, borderRadius: 12, background: `repeating-linear-gradient(90deg, rgba(0,0,0,0.14) 0 10px, rgba(255,255,255,0.1) 10px 20px), ${c}`, border: "3px solid #fff", boxShadow: "0 10px 24px rgba(0,0,0,0.45)", transform: `translateY(${(1 - p) * 60}px) rotate(${(i - 3) * 3}deg)`, opacity: Math.min(1, p * 1.5) }} />;
      })}
    </div>
  );
};

export const WaButton: React.FC<{ t: number; at: number; label: string }> = ({ t, at, label }) => {
  const p = interpolate(t, [at, at + 0.3], [0, 1], { easing: Easing.out(Easing.back(2)), ...clamp });
  const pulse = 1 + 0.035 * Math.max(0, Math.sin((t - at) * 7));
  const bob = Math.sin((t - at) * 8) * 10;
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-start", transform: `scale(${p * pulse})`, transformOrigin: "0% 50%", opacity: Math.min(1, p * 1.5) }}>
      <div style={{ display: "flex", alignItems: "center", gap: 18, background: C.wa, borderRadius: 999, padding: "20px 42px 20px 26px", border: "5px solid #fff", boxShadow: "0 16px 40px rgba(0,0,0,0.45)" }}>
        <svg width={64} height={64} viewBox="0 0 48 48">
          <path d="M24 5C13.5 5 5 13 5 23c0 3.6 1.1 7 3 9.8L5.5 43l10.6-2.6c2.4 1.1 5.1 1.6 7.9 1.6 10.5 0 19-8 19-18S34.5 5 24 5z" fill="#fff" />
          <path d="M17 15c-1 0-2.5 1.3-2.5 3.6 0 4.4 5.6 11.5 12.3 13.6 2.7.8 4.6-.4 5.2-1.6.4-.8.3-1.7-.2-2l-3.4-1.8c-.6-.3-1.2 0-1.6.5l-1 1.3c-2.6-1-5-3.3-6.1-5.9l1.2-1.1c.4-.4.6-1 .3-1.6l-1.6-3.6c-.3-.6-.8-.8-1.3-.8z" fill={C.wa} />
        </svg>
        <span style={{ fontFamily: F.kin, fontWeight: 900, fontSize: 52, color: "#fff" }}>{label}</span>
      </div>
      <svg width={90} height={80} viewBox="0 0 90 80" style={{ marginLeft: 150, marginTop: 6, transform: `translateY(${bob}px)` }}>
        <path d="M16 20l29 29 29-29" fill="none" stroke="#fff" strokeWidth={12} strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </div>
  );
};

const TOP: Record<string, number> = { low: 1150, mid: 760, top: 300 };

const BeatView: React.FC<{ b: Beat; t: number }> = ({ b, t }) => {
  const out = interpolate(t, [b.e - 0.12, b.e], [1, 0], clamp);
  const lift = interpolate(t, [b.e - 0.12, b.e], [0, -24], clamp);
  const style = (b as { style?: string }).style;
  const step = (b as { step?: number }).step;
  const lines = b.lines as Line[];
  const base = style === "light" ? 54 : 92;
  if (style === "stamp" || style === "badge") {
    const p = interpolate(t, [lines[0].at, lines[0].at + 0.28], [0, 1], { easing: Easing.out(Easing.back(2.4)), ...clamp });
    const txt = lines[0].t.replace(/\*/g, "");
    const size = fit(txt, style === "badge" ? 220 : 120);
    return (
      <div style={{ position: "absolute", left: LEFT, top: TOP[(b as { pos?: string }).pos ?? "low"] - 20, opacity: out, transform: `translateY(${lift}px)` }}>
        <div style={{ display: "inline-block", background: style === "badge" ? "transparent" : goldGrad, padding: style === "badge" ? 0 : "8px 34px 14px", borderRadius: 18, transform: `rotate(-3deg) scale(${2 - p})`, opacity: Math.min(1, p * 2), boxShadow: style === "badge" ? "none" : "0 18px 40px rgba(0,0,0,0.45)" }}>
          <span style={{ fontFamily: F.kin, fontWeight: 900, fontSize: size, letterSpacing: -2, lineHeight: 1.05, ...(style === "badge" ? { ...goldText, filter: "drop-shadow(0 8px 18px rgba(0,0,0,0.6))" } : { color: C.ink }) }}>{txt}</span>
        </div>
        {lines.slice(1).map((l, i) => {
          const q = interpolate(t, [l.at, l.at + 0.25], [0, 1], { easing: Easing.out(Easing.cubic), ...clamp });
          return (
            <div key={i} style={{ marginTop: 10, display: "inline-block", background: C.emerald, border: `3px solid ${C.gold}`, padding: "10px 30px", borderRadius: 14, transform: `translateX(${(1 - q) * -80}px)`, opacity: q }}>
              <span style={{ fontFamily: F.kin, fontWeight: 900, fontSize: fit(l.t, 84), color: C.white, letterSpacing: 2 }}>{l.t}</span>
            </div>
          );
        })}
      </div>
    );
  }
  const fx = (b as { fx?: string }).fx;
  const top = fx && BELOW.includes(fx) && fx !== "underline" ? 1000 : TOP[(b as { pos?: string }).pos ?? "low"];
  return (
    <div style={{ position: "absolute", left: LEFT, top, width: MAXW, opacity: out, transform: `translateY(${lift}px)`, ...(style === "light" ? { left: 0, width: 1080, textAlign: "center" } : {}) }}>
      {step && <Steps cur={step} t={t} s={b.s} />}
      {lines.map((l, i) => {
        if (style === "light") {
          const q = interpolate(t, [l.at, l.at + 0.3], [0, 1], clamp);
          return <div key={i} style={{ fontFamily: F.kin, fontWeight: 800, fontSize: base, letterSpacing: 12, color: C.white, opacity: q, transform: `translateY(${(1 - q) * 20}px)` }}>{l.t}</div>;
        }
        return <KLine key={i} line={l} t={t} size={fit(l.t, l.big ? 132 : base)} />;
      })}
      {style === "swatch" && <Swatches t={t} s={b.s} />}
      {fx && BELOW.includes(fx) && <FxBelow b={b as never} t={t} />}
      {style === "cta" && <div style={{ marginTop: 18 }}><WaButton t={t} at={b.s + 0.25} label={(b as { button?: string }).button ?? "WhatsApp"} /></div>}
    </div>
  );
};

export const Kinetic: React.FC = () => {
  const t = useCurrentFrame() / tl.fps;
  const b = tl.beats.find((x) => t >= x.s - 0.02 && t < x.e);
  if (!b) return null;
  const out = interpolate(t, [b.e - 0.12, b.e], [1, 0], clamp);
  return (
    <>
      <div style={{ position: "absolute", inset: 0, opacity: out }}><FxAbove b={b as never} t={t} /></div>
      <BeatView b={b} t={t} />
    </>
  );
};
