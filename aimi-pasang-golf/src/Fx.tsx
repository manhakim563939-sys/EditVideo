import React from "react";
import { Easing, Img, interpolate, staticFile } from "remotion";
import { C, F, goldGrad, goldText } from "./theme";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const pop = (t: number, at: number, d = 0.3) => interpolate(t, [at, at + d], [0, 1], { easing: Easing.out(Easing.back(2)), ...clamp });
const draw = (t: number, at: number, d = 0.6) => interpolate(t, [at, at + d], [0, 1], { easing: Easing.inOut(Easing.cubic), ...clamp });

type B = { s: number; e: number; fx?: string; items?: [string, number][] };
const G = { fill: "none", stroke: C.goldLight, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };

// ---------------------------------------------------------------- above the text block
const Key: React.FC<{ t: number; s: number }> = ({ t, s }) => {
  const d = draw(t, s, 0.7);
  const k = interpolate(t, [s + 0.4, s + 0.75], [140, 0], { easing: Easing.out(Easing.cubic), ...clamp });
  const turn = interpolate(t, [s + 0.75, s + 1.0], [0, 90], clamp);
  const glow = interpolate(t, [s + 1.0, s + 1.2, s + 1.5], [0, 1, 0.4], clamp);
  return (
    <div style={{ position: "absolute", left: 70, top: 860 }}>
      <svg width={300} height={260} viewBox="0 0 300 260">
        <path d="M30 120 L150 20 L270 120 M55 100 V240 H245 V100" {...G} strokeWidth={12} pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - d} />
        <circle cx={150} cy={170} r={22} fill={`rgba(246,222,156,${0.25 + 0.5 * glow})`} stroke={C.goldLight} strokeWidth={6} opacity={d} />
        <g transform={`translate(${150 + k} 170) rotate(${turn})`} opacity={d > 0.3 ? 1 : 0}>
          <circle cx={46} cy={0} r={16} {...G} strokeWidth={8} />
          <path d="M30 0 H-4 M8 0 v10 M18 0 v8" {...G} strokeWidth={8} />
        </g>
      </svg>
    </div>
  );
};

const SearchBar: React.FC<{ t: number; s: number; noAnswer?: boolean }> = ({ t, s, noAnswer }) => {
  const q = "langsir apa yang sesuai untuk rumah saya?";
  const n = noAnswer ? q.length : Math.floor(interpolate(t, [s + 0.15, s + 1.2], [0, q.length], clamp));
  const p = pop(t, s, 0.3);
  const spin = (t - s) * 540;
  const x = noAnswer ? draw(t, s + 0.55, 0.35) : 0;
  return (
    <div style={{ position: "absolute", left: 70, top: 860, width: 900, transform: `scale(${noAnswer ? 1 : p})`, transformOrigin: "0% 50%", opacity: noAnswer ? 1 : Math.min(1, p * 1.5) }}>
      <div style={{ display: "flex", alignItems: "center", gap: 18, background: "#fff", borderRadius: 999, padding: "22px 30px", boxShadow: "0 16px 40px rgba(0,0,0,0.4)" }}>
        <svg width={44} height={44} viewBox="0 0 48 48"><circle cx={20} cy={20} r={13} fill="none" stroke="#666" strokeWidth={5} /><path d="M30 30l12 12" stroke="#666" strokeWidth={5} strokeLinecap="round" /></svg>
        <div style={{ flex: 1, fontFamily: F.kin, fontWeight: 700, fontSize: 34, color: "#333", whiteSpace: "nowrap", overflow: "hidden" }}>{q.slice(0, n)}<span style={{ opacity: Math.floor(t * 4) % 2 ? 1 : 0 }}>|</span></div>
        {!noAnswer && <div style={{ width: 40, height: 40, borderRadius: 20, border: "6px solid #ddd", borderTopColor: C.gold, transform: `rotate(${spin}deg)` }} />}
      </div>
      {noAnswer && (
        <div style={{ marginTop: 18, display: "flex", alignItems: "center", gap: 18, opacity: interpolate(t, [s + 0.3, s + 0.5], [0, 1], clamp) }}>
          <svg width={70} height={70} viewBox="0 0 70 70"><circle cx={35} cy={35} r={30} fill="rgba(0,0,0,0.5)" stroke="#fff" strokeWidth={4} /><path d="M22 22 L48 48 M48 22 L22 48" stroke="#fff" strokeWidth={8} strokeLinecap="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - x} /></svg>
          <div style={{ fontFamily: F.kin, fontWeight: 800, fontSize: 36, color: "#fff", textShadow: "0 3px 10px rgba(0,0,0,0.6)" }}>0 jawapan yang jelas</div>
        </div>
      )}
      {!noAnswer && (
        <div style={{ position: "absolute", right: 10, top: 120, opacity: interpolate(t, [s + 0.6, s + 0.8], [0, 1], clamp) }}>
          <svg width={120} height={120} viewBox="0 0 120 120">
            <circle cx={60} cy={60} r={50} fill="rgba(0,0,0,0.45)" stroke={C.goldLight} strokeWidth={6} />
            <path d={`M60 60 L60 ${60 - 34}`} stroke="#fff" strokeWidth={7} strokeLinecap="round" transform={`rotate(${(t - s) * 720} 60 60)`} />
            <path d="M60 60 L60 36" stroke={C.goldLight} strokeWidth={7} strokeLinecap="round" transform={`rotate(${(t - s) * 60} 60 60)`} />
          </svg>
        </div>
      )}
    </div>
  );
};

const LogoBurst: React.FC<{ t: number; s: number }> = ({ t, s }) => {
  const at = s + 0.37;
  const p = pop(t, at, 0.45);
  const rays = Array.from({ length: 12 }, (_, i) => i);
  const r = interpolate(t, [at, at + 0.6], [60, 230], { easing: Easing.out(Easing.cubic), ...clamp });
  const ro = interpolate(t, [at, at + 0.15, at + 0.7], [0, 1, 0], clamp);
  return (
    <div style={{ position: "absolute", left: 70, top: 780, width: 340, height: 340 }}>
      {rays.map((i) => {
        const a = (i / 12) * Math.PI * 2;
        return <div key={i} style={{ position: "absolute", left: 170 + Math.cos(a) * r - 4, top: 170 + Math.sin(a) * r - 18, width: 8, height: 36, borderRadius: 4, background: C.goldLight, opacity: ro, transform: `rotate(${(a * 180) / Math.PI + 90}deg)` }} />;
      })}
      <div style={{ position: "absolute", left: 30, top: 30, width: 280, height: 280, borderRadius: 140, overflow: "hidden", border: `5px solid ${C.gold}`, boxShadow: "0 16px 40px rgba(0,0,0,0.5)", transform: `scale(${p}) rotate(${(1 - p) * -40}deg)`, opacity: Math.min(1, p * 1.5) }}>
        <Img src={staticFile("img/logo.png")} style={{ width: 280, height: 280, transform: "scale(1.25)" }} />
      </div>
    </div>
  );
};

const Pin: React.FC<{ t: number; s: number }> = ({ t, s }) => {
  const at = s + 1.15;
  const drop = interpolate(t, [at, at + 0.4], [-200, 0], { easing: Easing.bounce, ...clamp });
  const ring = ((t - at - 0.4) % 1.2) / 1.2;
  return (
    <div style={{ position: "absolute", left: 70, top: 840, width: 200, height: 260, opacity: interpolate(t, [at, at + 0.1], [0, 1], clamp) }}>
      {t > at + 0.4 && <div style={{ position: "absolute", left: 100 - 90 * ring, top: 220 - 30 * ring, width: 180 * ring, height: 60 * ring, borderRadius: "50%", border: `4px solid ${C.goldLight}`, opacity: 1 - ring }} />}
      <svg width={160} height={220} viewBox="0 0 48 66" style={{ position: "absolute", left: 20, top: drop }}>
        <path d="M24 2C12 2 3 11 3 23c0 16 21 41 21 41s21-25 21-41C45 11 36 2 24 2z" fill={C.gold} stroke="#fff" strokeWidth={2.5} />
        <circle cx={24} cy={23} r={8} fill={C.emerald} />
      </svg>
    </div>
  );
};

export const FxAbove: React.FC<{ b: B; t: number }> = ({ b, t }) => {
  switch (b.fx) {
    case "key": return <Key t={t} s={b.s} />;
    case "google": return <SearchBar t={t} s={b.s} />;
    case "noanswer": return <SearchBar t={t} s={b.s} noAnswer />;
    case "logo": return <LogoBurst t={t} s={b.s} />;
    case "pin": return <Pin t={t} s={b.s} />;
    default: return null;
  }
};

// ---------------------------------------------------------------- below the text lines (flows in the text column)
const BlurWord: React.FC<{ t: number; s: number }> = ({ t, s }) => {
  const at = s + 0.55;
  const p = pop(t, at, 0.35);
  const bl = 6 + 6 * Math.sin((t - at) * 9);
  return (
    <div style={{ position: "relative", marginTop: 6, height: 190 }}>
      <div style={{ fontFamily: F.kin, fontWeight: 900, fontSize: 168, lineHeight: 1, letterSpacing: -4, ...goldText, filter: `blur(${Math.max(0, bl) * p}px)`, transform: `scale(${0.6 + 0.4 * p}) translateX(${Math.sin((t - at) * 13) * 6}px)`, transformOrigin: "0% 50%", opacity: Math.min(1, p * 1.5) }}>BLURR</div>
      {[0, 1, 2].map((i) => {
        const q = pop(t, at + 0.2 + i * 0.15, 0.3);
        return <div key={i} style={{ position: "absolute", left: 660 + i * 66, top: 10 + (i % 2) * 70 + Math.sin((t + i) * 4) * 8, fontFamily: F.kin, fontWeight: 900, fontSize: 90, color: "#fff", opacity: q, transform: `scale(${q}) rotate(${(i - 1) * 14}deg)`, textShadow: "0 6px 16px rgba(0,0,0,0.5)" }}>?</div>;
      })}
    </div>
  );
};

const Questions: React.FC<{ t: number; items: [string, number][] }> = ({ t, items }) => (
  <div style={{ marginTop: 20, display: "flex", flexDirection: "column", gap: 16, alignItems: "flex-start" }}>
    {items.map(([l, at], i) => {
      const p = pop(t, at, 0.3);
      return (
        <div key={l} style={{ display: "flex", alignItems: "center", gap: 18, background: "rgba(255,255,255,0.95)", borderRadius: 20, padding: "14px 30px 14px 16px", boxShadow: "0 12px 30px rgba(0,0,0,0.4)", transform: `translateX(${(1 - p) * -300}px) rotate(${(i % 2 ? 1.5 : -1.5)}deg)`, opacity: Math.min(1, p * 1.5) }}>
          <div style={{ width: 64, height: 64, borderRadius: 32, background: goldGrad, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: F.kin, fontWeight: 900, fontSize: 44, color: C.ink }}>?</div>
          <div style={{ fontFamily: F.kin, fontWeight: 900, fontSize: 56, color: C.ink }}>{l}</div>
        </div>
      );
    })}
  </div>
);

const Swatch: React.FC<{ t: number; s: number }> = ({ t, s }) => {
  const cols = ["#3E7C78", "#C9B79C", "#8E9AA6", "#D6A6B4", "#6B4A3A", "#E8E1D3", "#A47A33"];
  return (
    <div style={{ position: "relative", height: 230, marginTop: 20 }}>
      {cols.map((c, i) => {
        const p = pop(t, s + 0.5 + i * 0.07, 0.35);
        const ang = (i - 3) * 10 * p;
        return <div key={i} style={{ position: "absolute", left: 300, top: 10, width: 110, height: 210, borderRadius: 14, background: `repeating-linear-gradient(90deg, rgba(0,0,0,0.14) 0 11px, rgba(255,255,255,0.1) 11px 22px), ${c}`, border: "4px solid #fff", boxShadow: "0 10px 24px rgba(0,0,0,0.45)", transformOrigin: "50% 140%", transform: `rotate(${ang}deg)`, opacity: Math.min(1, p * 1.5) }} />;
      })}
    </div>
  );
};

const Steps: React.FC<{ t: number; items: [string, number][] }> = ({ t, items }) => {
  const icons = [
    <path key="r" d="M4 17h40v14H4zM11 17v6M18 17v8M25 17v6M32 17v8M39 17v6" />,
    <path key="n" d="M10 40L40 10M36 8c3 0 5 2 4 5M30 18c-12 4-20 12-16 20" />,
    <path key="h" d="M5 9h38M10 9v4c0 9-2 22-4 28h11c-2-8-2-20 0-32M38 9v4c0 9 2 22 4 28H31c2-8 2-20 0-32" />,
  ];
  const prog = interpolate(t, [items[0][1], items[2][1] + 0.3], [0, 1], clamp);
  return (
    <div style={{ position: "relative", marginTop: 34, width: 860, height: 250 }}>
      <div style={{ position: "absolute", left: 85, right: 85, top: 78, height: 10, borderRadius: 5, background: "rgba(255,255,255,0.3)" }}>
        <div style={{ width: `${prog * 100}%`, height: "100%", borderRadius: 5, background: goldGrad }} />
      </div>
      {items.map(([l, at], i) => {
        const p = pop(t, at, 0.35);
        const on = t >= at;
        return (
          <div key={l} style={{ position: "absolute", left: i * 330, top: 0, width: 200, display: "flex", flexDirection: "column", alignItems: "center" }}>
            <div style={{ width: 166, height: 166, borderRadius: 83, background: on ? goldGrad : "rgba(0,0,0,0.5)", border: "5px solid #fff", display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${0.75 + 0.25 * p})`, boxShadow: "0 12px 30px rgba(0,0,0,0.45)" }}>
              <svg width={90} height={90} viewBox="0 0 48 48"><g fill="none" stroke={on ? C.ink : "#fff"} strokeWidth={3.5} strokeLinecap="round" strokeLinejoin="round">{icons[i]}</g></svg>
            </div>
            <div style={{ marginTop: 12, fontFamily: F.kin, fontWeight: 900, fontSize: 40, color: "#fff", opacity: 0.4 + 0.6 * p, textShadow: "0 4px 12px rgba(0,0,0,0.6)", whiteSpace: "nowrap" }}>{l}</div>
          </div>
        );
      })}
    </div>
  );
};

const Counter: React.FC<{ t: number; s: number }> = ({ t, s }) => {
  const n = interpolate(t, [s + 0.5, s + 1.15], [0, 100], { easing: Easing.out(Easing.cubic), ...clamp });
  const p = pop(t, s + 0.45, 0.3);
  const k = t - s - 1.18;
  const bounce = k > 0 ? 0.06 * Math.abs(Math.sin(k * 10)) * Math.exp(-k * 3) : 0;
  return (
    <div style={{ marginTop: 4, transform: `scale(${(0.7 + 0.3 * p) * (1 + bounce)})`, transformOrigin: "0% 50%", opacity: Math.min(1, p * 1.5) }}>
      <span style={{ fontFamily: F.kin, fontWeight: 900, fontSize: 250, letterSpacing: -6, lineHeight: 1, ...goldText, filter: "drop-shadow(0 10px 22px rgba(0,0,0,0.55))" }}>{Math.round(n)}%</span>
    </div>
  );
};

const Underline: React.FC<{ t: number; s: number }> = ({ t, s }) => (
  <div style={{ position: "absolute", left: 0, top: 66, width: 640 * draw(t, s + 0.35, 0.5), height: 9, borderRadius: 5, background: goldGrad, boxShadow: "0 4px 12px rgba(0,0,0,0.4)" }} />
);

export const FxBelow: React.FC<{ b: B; t: number }> = ({ b, t }) => {
  switch (b.fx) {
    case "blur": return <BlurWord t={t} s={b.s} />;
    case "questions": return <Questions t={t} items={b.items!} />;
    case "swatch": return <Swatch t={t} s={b.s} />;
    case "steps": return <Steps t={t} items={b.items!} />;
    case "counter": return <Counter t={t} s={b.s} />;
    case "underline": return <Underline t={t} s={b.s} />;
    default: return null;
  }
};
