import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import tl from "./timeline.json";
import { C, F, goldGrad } from "./theme";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const pop = (t: number, at: number, d = 0.3) => interpolate(t, [at, at + d], [0, 1], { easing: Easing.out(Easing.back(1.8)), ...clamp });
type V = { type: string; s: number; e: number; [k: string]: unknown };
const n = (v: V, k: string) => v[k] as number;
const txt = (size: number, color = C.ink, w = 900): React.CSSProperties => ({ fontFamily: F.kin, fontWeight: w, fontSize: size, color, lineHeight: 1.1 });
const TOP = 230;

const Tick: React.FC<{ p: number; size: number; dark?: boolean }> = ({ p, size, dark }) => (
  <div style={{ width: size, height: size, borderRadius: size / 2, background: p > 0.5 ? goldGrad : dark ? "rgba(0,0,0,0.45)" : "#E6E1D5", border: "3px solid #fff", display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${0.8 + 0.2 * Math.min(1, p)})` }}>
    <svg width={size * 0.6} height={size * 0.6} viewBox="0 0 48 48"><path d="M10 25l9 9 19-20" fill="none" stroke={p > 0.5 ? C.ink : "#fff"} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - Math.min(1, p)} /></svg>
  </div>
);

// Job progress across the install montage.
const Steps: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const items = v.items as [string, number][];
  const prog = interpolate(t, [items[0][1], items[items.length - 1][1]], [0, 1], clamp);
  const p = pop(t, v.s, 0.35);
  return (
    <div style={{ position: "absolute", left: 50, right: 50, top: TOP, height: 160, transform: `translateY(${(1 - p) * -40}px)`, opacity: Math.min(1, p * 1.5) }}>
      <div style={{ position: "absolute", left: 70, right: 70, top: 34, height: 10, borderRadius: 5, background: "rgba(255,255,255,0.4)" }}>
        <div style={{ width: `${prog * 100}%`, height: "100%", borderRadius: 5, background: goldGrad }} />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        {items.map(([l, at]) => {
          const q = pop(t, at, 0.3);
          return (
            <div key={l} style={{ width: 160, display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
              <Tick p={q} size={78} dark />
              <div style={{ ...txt(26, "#fff", 900), textShadow: "0 3px 10px rgba(0,0,0,0.7)", opacity: 0.45 + 0.55 * Math.min(1, q) }}>{l}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

const Rooms: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const items = v.items as [string, number][];
  return (
    <div style={{ position: "absolute", left: 70, top: TOP, display: "flex", flexDirection: "column", gap: 14 }}>
      {items.map(([l, at]) => {
        const q = pop(t, at, 0.35);
        if (t < at) return null;
        return (
          <div key={l} style={{ display: "flex", alignItems: "center", gap: 14, background: "rgba(255,255,255,0.95)", borderRadius: 999, padding: "8px 26px 8px 8px", boxShadow: "0 10px 24px rgba(0,0,0,0.3)", transform: `translateX(${(1 - Math.min(1, q)) * -200}px)`, alignSelf: "flex-start" }}>
            <Tick p={q} size={56} /><span style={txt(36)}>{l}</span>
          </div>
        );
      })}
    </div>
  );
};

// "Iklan banyak kali" + "orang tempatan" (generic ad card, no platform logo).
const Ad: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const p = pop(t, v.s, 0.35);
  const rep = pop(t, n(v, "rep"), 0.35);
  const loc = pop(t, n(v, "local"), 0.35);
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: TOP - 20, height: 380 }}>
      {[2, 1, 0].map((i) => (
        <div key={i} style={{ position: "absolute", left: 40 + i * 22 * rep, top: 20 + i * 14 * rep, width: 250, height: 230, borderRadius: 24, background: "#fff", boxShadow: "0 14px 30px rgba(0,0,0,0.3)", transform: `rotate(${-6 + i * 5 * rep}deg) scale(${p})`, opacity: i === 0 ? Math.min(1, p * 1.5) : rep * 0.9, padding: 20 }}>
          <div style={{ height: 110, borderRadius: 14, background: "linear-gradient(135deg, #8B5A4A, #C9A47A)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <svg width={70} height={70} viewBox="0 0 48 48"><circle cx={24} cy={24} r={20} fill="rgba(0,0,0,0.35)" /><path d="M19 15l14 9-14 9z" fill="#fff" /></svg>
          </div>
          <div style={{ height: 18, width: "80%", borderRadius: 9, background: "#E6E1D5", marginTop: 18 }} />
          <div style={{ height: 18, width: "55%", borderRadius: 9, background: "#E6E1D5", marginTop: 12 }} />
          <div style={{ ...txt(18, C.goldDark, 800), marginTop: 10 }}>IKLAN · AIMI CURTAIN</div>
        </div>
      ))}
      <div style={{ position: "absolute", left: 40, top: 300, transform: `scale(${rep}) rotate(-4deg)`, background: goldGrad, borderRadius: 18, padding: "10px 24px", boxShadow: "0 12px 26px rgba(0,0,0,0.35)" }}><span style={txt(40)}>BANYAK KALI</span></div>
      <div style={{ position: "absolute", left: 770, top: 40, display: "flex", flexDirection: "column", alignItems: "center", gap: 6, transform: `scale(${loc})`, opacity: Math.min(1, loc * 1.5) }}>
        <svg width={90} height={120} viewBox="0 0 48 66"><path d="M24 2C12 2 3 11 3 23c0 16 21 41 21 41s21-25 21-41C45 11 36 2 24 2z" fill={C.gold} stroke="#fff" strokeWidth={2.5} /><circle cx={24} cy={23} r={8} fill={C.emerald} /></svg>
        <div style={{ background: C.emerald, border: `4px solid ${C.gold}`, borderRadius: 16, padding: "8px 18px" }}><span style={txt(32, "#fff")}>ORANG<br />TEMPATAN</span></div>
      </div>
    </div>
  );
};

const Stars: React.FC<{ v: V; t: number }> = ({ v, t }) => (
  <div style={{ position: "absolute", left: 0, right: 0, top: TOP, display: "flex", justifyContent: "center", gap: 12, filter: "drop-shadow(0 8px 18px rgba(0,0,0,0.45))" }}>
    {[0, 1, 2, 3, 4].map((i) => {
      const p = pop(t, v.s + i * 0.1, 0.35);
      return (
        <svg key={i} width={120} height={120} viewBox="0 0 48 48" style={{ transform: `scale(${p}) rotate(${(1 - p) * -90}deg)`, opacity: Math.min(1, p * 1.5) }}>
          <path d="M24 4l6 12.6 13.8 1.8-10.1 9.6 2.6 13.7L24 35l-12.3 6.7 2.6-13.7L4.2 18.4 18 16.6z" fill={C.gold} stroke="#fff" strokeWidth={2} />
        </svg>
      );
    })}
  </div>
);

const MAP: Record<string, React.FC<{ v: V; t: number }>> = { steps: Steps, rooms: Rooms, ad: Ad, stars: Stars };

export const VizLayer: React.FC = () => {
  const t = useCurrentFrame() / tl.fps;
  const v = (tl.viz as V[]).find((x) => t >= x.s - 0.05 && t < x.e + 0.2);
  if (!v) return null;
  const Comp = MAP[v.type];
  const out = interpolate(t, [v.e, v.e + 0.2], [1, 0], clamp);
  return <div style={{ position: "absolute", inset: 0, opacity: out }}>{Comp ? <Comp v={v} t={t} /> : null}</div>;
};
