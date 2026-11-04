import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import tl from "./timeline.json";
import { C, F, goldGrad, goldText } from "./theme";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const pop = (t: number, at: number, d = 0.3) => interpolate(t, [at, at + d], [0, 1], { easing: Easing.out(Easing.back(1.8)), ...clamp });
const rise = (t: number, at: number, d = 0.4) => interpolate(t, [at, at + d], [0, 1], { easing: Easing.out(Easing.cubic), ...clamp });
type V = { type: string; s: number; e: number; [k: string]: unknown };
const n = (v: V, k: string) => v[k] as number;
const txt = (size: number, color = C.ink, w = 900): React.CSSProperties => ({ fontFamily: F.kin, fontWeight: w, fontSize: size, color, lineHeight: 1.1 });
const TOP = 230;
const card: React.CSSProperties = { background: "rgba(255,255,255,0.95)", borderRadius: 26, boxShadow: "0 18px 40px rgba(0,0,0,0.3)" };

// 2-3 hours: minute hand spins, hour hand moves two to three hours.
const Clock: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const p = pop(t, v.s, 0.35);
  const h = interpolate(t, [n(v, "at"), n(v, "at") + 1.3], [0, 2.5], { easing: Easing.inOut(Easing.cubic), ...clamp });
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: TOP, display: "flex", justifyContent: "center", transform: `scale(${p})`, opacity: Math.min(1, p * 1.5) }}>
      <svg width={300} height={300} viewBox="0 0 120 120" style={{ filter: "drop-shadow(0 12px 24px rgba(0,0,0,0.45))" }}>
        <circle cx={60} cy={60} r={54} fill="#fff" stroke={C.gold} strokeWidth={7} />
        <path d={`M60 60 L${60 + 50 * Math.sin(0)} ${60 - 50 * Math.cos(0)} A50 50 0 ${h * 30 > 180 ? 1 : 0} 1 ${60 + 50 * Math.sin((h * 30 * Math.PI) / 180)} ${60 - 50 * Math.cos((h * 30 * Math.PI) / 180)} Z`} fill="rgba(217,179,94,0.45)" />
        {Array.from({ length: 12 }, (_, i) => <line key={i} x1={60} y1={10} x2={60} y2={17} stroke={C.ink} strokeWidth={3} transform={`rotate(${i * 30} 60 60)`} />)}
        <line x1={60} y1={60} x2={60} y2={30} stroke={C.ink} strokeWidth={6} strokeLinecap="round" transform={`rotate(${h * 30} 60 60)`} />
        <line x1={60} y1={60} x2={60} y2={18} stroke={C.goldDark} strokeWidth={4} strokeLinecap="round" transform={`rotate(${h * 360} 60 60)`} />
        <circle cx={60} cy={60} r={5} fill={C.ink} />
      </svg>
    </div>
  );
};

const Speed: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const p = rise(t, n(v, "at"), 0.3);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: p * interpolate(t, [v.e - 0.3, v.e], [1, 0], clamp) }}>
      {Array.from({ length: 14 }, (_, i) => {
        const y = 200 + i * 60;
        const x = ((t * (1800 + (i % 4) * 400) + i * 377) % 1600) - 400;
        return <div key={i} style={{ position: "absolute", left: x, top: y, width: 220 + (i % 3) * 120, height: 6 + (i % 2) * 4, borderRadius: 4, background: "rgba(255,240,200,0.55)" }} />;
      })}
    </div>
  );
};

const Quality: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const items = v.items as [string, number][];
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: TOP, display: "flex", justifyContent: "center", gap: 40 }}>
      {items.map(([l, at]) => {
        const q = pop(t, at, 0.35);
        return (
          <div key={l} style={{ width: 300, height: 300, borderRadius: 150, background: goldGrad, border: "8px solid #fff", boxShadow: "0 16px 36px rgba(0,0,0,0.4)", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", transform: `scale(${q}) rotate(${(1 - q) * -30}deg)`, opacity: Math.min(1, q * 1.5) }}>
            <svg width={90} height={90} viewBox="0 0 48 48"><path d="M10 25l9 9 19-20" fill="none" stroke={C.ink} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" /></svg>
            <div style={txt(42)}>{l}</div>
            <div style={txt(26, C.ink, 800)}>BERKUALITI</div>
          </div>
        );
      })}
    </div>
  );
};

const Swatches: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const cols = ["#6B2737", "#C08A4F", "#CDBFAF", "#EFEAE2", "#8E7B6A", "#4E5A56", "#D9B35E"];
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: TOP + 10, height: 340 }}>
      {cols.map((c, i) => {
        const p = pop(t, n(v, "at") + i * 0.07, 0.35);
        return <div key={i} style={{ position: "absolute", left: 480, top: 0, width: 120, height: 280, borderRadius: 16, background: `repeating-linear-gradient(90deg, rgba(0,0,0,0.14) 0 12px, rgba(255,255,255,0.1) 12px 24px), ${c}`, border: "5px solid #fff", boxShadow: "0 10px 24px rgba(0,0,0,0.45)", transformOrigin: "50% 130%", transform: `rotate(${(i - 3) * 11 * p}deg)`, opacity: Math.min(1, p * 1.5) }} />;
      })}
    </div>
  );
};

// Bumi -> Langit: a gauge rising from the ground to the sky.
const Meter: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const p = pop(t, v.s, 0.35);
  const lvl = interpolate(t, [n(v, "at") - 0.9, n(v, "at") + 0.2], [0.08, 1], { easing: Easing.inOut(Easing.cubic), ...clamp });
  return (
    <div style={{ position: "absolute", left: 70, top: TOP - 30, width: 940, height: 560, transform: `scale(${p})`, transformOrigin: "50% 0%", opacity: Math.min(1, p * 1.5) }}>
      <div style={{ ...card, position: "absolute", inset: 0, overflow: "hidden", background: "linear-gradient(180deg, #CFE4F5 0%, #EAF3FA 55%, #D9C7A6 82%, #B89A6E 100%)" }}>
        <svg width={940} height={560} style={{ position: "absolute", inset: 0 }}>
          <g fill="#fff" opacity={0.9}><ellipse cx={220} cy={90} rx={90} ry={34} /><ellipse cx={280} cy={70} rx={70} ry={34} /><ellipse cx={720} cy={120} rx={100} ry={36} /></g>
          <circle cx={830} cy={70} r={34} fill="#F6C343" />
        </svg>
        <div style={{ position: "absolute", left: 40, top: 30, ...txt(46, "#2B5C86") }}>LANGIT</div>
        <div style={{ position: "absolute", left: 40, bottom: 26, ...txt(46, "#5A4022") }}>BUMI</div>
        <div style={{ position: "absolute", left: 420, top: 40, width: 100, height: 480, borderRadius: 50, background: "rgba(255,255,255,0.7)", border: `5px solid ${C.ink}`, overflow: "hidden" }}>
          <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: `${lvl * 100}%`, background: goldGrad }} />
        </div>
        <div style={{ position: "absolute", left: 560, top: 40 + 480 * (1 - lvl) - 30, display: "flex", alignItems: "center", gap: 10 }}>
          <svg width={60} height={60} viewBox="0 0 48 48"><path d="M24 40V9M12 21L24 9l12 12" fill="none" stroke={C.ink} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" /></svg>
          <span style={txt(40)}>LEPAS PASANG</span>
        </div>
      </div>
    </div>
  );
};

const Stars: React.FC<{ v: V; t: number }> = ({ v, t }) => (
  <div style={{ position: "absolute", left: 0, right: 0, top: TOP, display: "flex", justifyContent: "center", gap: 12, filter: "drop-shadow(0 8px 18px rgba(0,0,0,0.45))" }}>
    {[0, 1, 2, 3, 4].map((i) => {
      const p = pop(t, v.s + i * 0.1, 0.35);
      return <svg key={i} width={120} height={120} viewBox="0 0 48 48" style={{ transform: `scale(${p}) rotate(${(1 - p) * -90}deg)`, opacity: Math.min(1, p * 1.5) }}><path d="M24 4l6 12.6 13.8 1.8-10.1 9.6 2.6 13.7L24 35l-12.3 6.7 2.6-13.7L4.2 18.4 18 16.6z" fill={C.gold} stroke="#fff" strokeWidth={2} /></svg>;
    })}
  </div>
);

const MAP: Record<string, React.FC<{ v: V; t: number }>> = { clock: Clock, speed: Speed, quality: Quality, swatches: Swatches, meter: Meter, stars: Stars };

export const VizLayer: React.FC = () => {
  const t = useCurrentFrame() / tl.fps;
  const v = (tl.viz as V[]).find((x) => t >= x.s - 0.05 && t < x.e + 0.2);
  if (!v) return null;
  const Comp = MAP[v.type];
  const out = interpolate(t, [v.e, v.e + 0.2], [1, 0], clamp);
  return <div style={{ position: "absolute", inset: 0, opacity: out }}>{Comp ? <Comp v={v} t={t} /> : null}</div>;
};
export { goldText };
