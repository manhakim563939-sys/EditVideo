import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import tl from "./timeline.json";
import { C, F, goldGrad, goldText } from "./theme";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const pop = (t: number, at: number, d = 0.3) => interpolate(t, [at, at + d], [0, 1], { easing: Easing.out(Easing.back(1.8)), ...clamp });
type V = { type: string; s: number; e: number; [k: string]: unknown };
const n = (v: V, k: string) => v[k] as number;
const txt = (size: number, color = C.ink, w = 900): React.CSSProperties => ({ fontFamily: F.kin, fontWeight: w, fontSize: size, color, lineHeight: 1.1 });
const TOP = 230;
const card: React.CSSProperties = { background: "rgba(255,255,255,0.95)", borderRadius: 26, boxShadow: "0 18px 40px rgba(0,0,0,0.3)" };

const Icon: React.FC<{ name: string; size: number; color?: string }> = ({ name, size, color = C.ink }) => (
  <svg width={size} height={size} viewBox="0 0 48 48"><g fill="none" stroke={color} strokeWidth={3.5} strokeLinecap="round" strokeLinejoin="round">
    {name === "store" && <><path d="M7 19l3-11h28l3 11M7 19c0 3 2.5 5 5.5 5S18 22 18 19c0 3 2.5 5 6 5s6-2 6-5c0 3 2.5 5 5.5 5S41 22 41 19M7 19h34" /><path d="M10 24v17h28V24M20 41V31h8v10" /></>}
    {name === "phone" && <><rect x={14} y={4} width={20} height={40} rx={4} /><path d="M21 38h6" /></>}
    {name === "house" && <><path d="M6 22L24 7l18 15" /><path d="M11 18v22h26V18M20 40V29h8v11" /></>}
    {name === "check" && <path d="M10 25l9 9 19-20" />}
  </g></svg>
);

// "Kali ke-3": three job tickets, all ticked.
const Repeat: React.FC<{ v: V; t: number }> = ({ v, t }) => (
  <div style={{ position: "absolute", left: 0, right: 0, top: TOP, display: "flex", justifyContent: "center", gap: 26 }}>
    {[0, 1, 2].map((i) => {
      const p = pop(t, n(v, "at") + i * 0.18, 0.35);
      const last = i === 2;
      return (
        <div key={i} style={{ width: 200, height: 200, borderRadius: 28, background: last ? goldGrad : "rgba(255,255,255,0.94)", border: last ? "6px solid #fff" : "none", boxShadow: "0 14px 30px rgba(0,0,0,0.35)", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", transform: `scale(${p * (last ? 1.1 : 1)}) rotate(${(i - 1) * 4}deg)`, opacity: Math.min(1, p * 1.5) }}>
          <Icon name="check" size={70} color={last ? C.ink : C.goldDark} />
          <div style={txt(32, C.ink)}>{`KALI KE-${i + 1}`}</div>
        </div>
      );
    })}
  </div>
);

// Three ways to choose a design.
const Options: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const items = v.items as [string, string, number][];
  return (
    <div style={{ position: "absolute", left: 60, right: 60, top: TOP, display: "flex", justifyContent: "space-between" }}>
      {items.map(([l, ic, at], i) => {
        const p = pop(t, at, 0.35);
        const active = t >= at && (i === items.length - 1 || t < items[i + 1][2]);
        return (
          <div key={l} style={{ width: 290, ...card, padding: "22px 10px", display: "flex", flexDirection: "column", alignItems: "center", gap: 10, transform: `translateY(${(1 - p) * 60}px) scale(${active ? 1.06 : 0.94})`, opacity: t >= at ? 1 : 0, border: active ? `5px solid ${C.gold}` : "5px solid transparent", filter: active ? "none" : "saturate(0.4)" }}>
            <div style={{ width: 110, height: 110, borderRadius: 55, background: active ? goldGrad : "#EFEBE1", display: "flex", alignItems: "center", justifyContent: "center" }}><Icon name={ic} size={66} /></div>
            <div style={{ ...txt(30), textAlign: "center" }}>{l}</div>
          </div>
        );
      })}
    </div>
  );
};

// Kenduri: question bubbles pop around, then a share burst.
const Crowd: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const sh = pop(t, n(v, "share"), 0.4);
  const qs = [[150, 40], [420, 0], [700, 50], [280, 170], [580, 180]];
  return (
    <div style={{ position: "absolute", left: 60, right: 60, top: TOP, height: 360 }}>
      {qs.map(([x, y], i) => {
        const p = pop(t, n(v, "ask") + i * 0.18, 0.3);
        return (
          <div key={i} style={{ position: "absolute", left: x, top: y, transform: `scale(${p * (1 - 0.35 * sh)})`, opacity: Math.min(1, p * 1.5) * (1 - 0.5 * sh) }}>
            <div style={{ ...card, borderRadius: "40px 40px 40px 8px", padding: "16px 26px", ...txt(54, C.goldDark) }}>?</div>
          </div>
        );
      })}
      {sh > 0 && (
        <div style={{ position: "absolute", left: 0, right: 0, top: 80, display: "flex", justifyContent: "center", transform: `scale(${sh})` }}>
          <div style={{ display: "flex", alignItems: "center", gap: 16, background: C.emerald, border: `5px solid ${C.gold}`, borderRadius: 999, padding: "16px 34px", boxShadow: "0 14px 30px rgba(0,0,0,0.4)" }}>
            <svg width={60} height={60} viewBox="0 0 48 48"><g fill="none" stroke={C.goldLight} strokeWidth={4} strokeLinecap="round"><circle cx={12} cy={24} r={5} /><circle cx={36} cy={12} r={5} /><circle cx={36} cy={36} r={5} /><path d="M16.5 21.5l15-7M16.5 26.5l15 7" /></g></svg>
            <span style={txt(44, "#fff")}>CONTACT DIKONGSI</span>
          </div>
        </div>
      )}
    </div>
  );
};

// Sister's house one lane over.
const Street: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const p = pop(t, v.s, 0.35);
  const s2 = pop(t, n(v, "at"), 0.4);
  const house = (label: string, q: number, gold: boolean) => (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", transform: `scale(${q})`, opacity: Math.min(1, q * 1.5) }}>
      <div style={{ width: 150, height: 150, borderRadius: 30, background: gold ? goldGrad : "#fff", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 12px 26px rgba(0,0,0,0.3)" }}><Icon name="house" size={100} /></div>
      <div style={{ ...txt(30, "#fff"), marginTop: 10, textShadow: "0 3px 10px rgba(0,0,0,0.6)" }}>{label}</div>
    </div>
  );
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: TOP, display: "flex", justifyContent: "center", alignItems: "center", gap: 30 }}>
      {house("RUMAH SAYA", p, false)}
      <div style={{ width: 160 * s2, height: 10, borderRadius: 5, background: goldGrad, marginBottom: 40 }} />
      {house("RUMAH ADIK", s2, true)}
    </div>
  );
};

const Score: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const p = pop(t, n(v, "at"), 0.4);
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: 1440, display: "flex", flexDirection: "column", alignItems: "center" }}>
      <div style={{ transform: `scale(${2 - p}) rotate(-6deg)`, opacity: interpolate(t, [n(v, "at"), n(v, "at") + 0.08], [0, 1], clamp), background: C.emerald, border: `7px solid ${C.gold}`, borderRadius: 30, padding: "8px 46px", boxShadow: "0 16px 36px rgba(0,0,0,0.45)" }}>
        <span style={{ ...txt(120), ...goldText }}>10/10</span>
      </div>
      <div style={{ display: "flex", gap: 10, marginTop: 20 }}>
        {[0, 1, 2, 3, 4].map((i) => {
          const q = pop(t, n(v, "at") + 0.3 + i * 0.08, 0.3);
          return <svg key={i} width={90} height={90} viewBox="0 0 48 48" style={{ transform: `scale(${q})` }}><path d="M24 4l6 12.6 13.8 1.8-10.1 9.6 2.6 13.7L24 35l-12.3 6.7 2.6-13.7L4.2 18.4 18 16.6z" fill={C.gold} stroke="#fff" strokeWidth={2} /></svg>;
        })}
      </div>
    </div>
  );
};

const MAP: Record<string, React.FC<{ v: V; t: number }>> = { repeat: Repeat, options: Options, crowd: Crowd, street: Street, score: Score };

export const VizLayer: React.FC = () => {
  const t = useCurrentFrame() / tl.fps;
  const v = (tl.viz as V[]).find((x) => t >= x.s - 0.05 && t < x.e + 0.2);
  if (!v) return null;
  const Comp = MAP[v.type];
  const out = interpolate(t, [v.e, v.e + 0.2], [1, 0], clamp);
  return <div style={{ position: "absolute", inset: 0, opacity: out }}>{Comp ? <Comp v={v} t={t} /> : null}</div>;
};
