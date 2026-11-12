import React from "react";
import { Easing, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import tl from "./timeline.json";
import { C, F, goldGrad } from "./theme";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const pop = (t: number, at: number, d = 0.3) => interpolate(t, [at, at + d], [0, 1], { easing: Easing.out(Easing.back(1.8)), ...clamp });
type V = { type: string; s: number; e: number; [k: string]: unknown };
const n = (v: V, k: string) => v[k] as number;
const txt = (size: number, color = C.ink, w = 900): React.CSSProperties => ({ fontFamily: F.kin, fontWeight: w, fontSize: size, color, lineHeight: 1.1 });
const TOP = 200;
const card: React.CSSProperties = { background: "rgba(255,255,255,0.95)", borderRadius: 24, boxShadow: "0 18px 40px rgba(0,0,0,0.3)" };

const Icon: React.FC<{ name: string; size: number; color?: string }> = ({ name, size, color = C.ink }) => (
  <svg width={size} height={size} viewBox="0 0 48 48"><g fill="none" stroke={color} strokeWidth={3.5} strokeLinecap="round" strokeLinejoin="round">
    {name === "store" && <><path d="M7 19l3-11h28l3 11M7 19c0 3 2.5 5 5.5 5S18 22 18 19c0 3 2.5 5 6 5s6-2 6-5c0 3 2.5 5 5.5 5S41 22 41 19M7 19h34" /><path d="M10 24v17h28V24M20 41V31h8v10" /></>}
    {name === "house" && <><path d="M6 22L24 7l18 15" /><path d="M11 18v22h26V18M20 40V29h8v11" /></>}
    {name === "ruler" && <path d="M4 17h40v14H4zM11 17v6M18 17v8M25 17v6M32 17v8M39 17v6" />}
    {name === "hook" && <path d="M5 9h38M10 9v4c0 9-2 22-4 28h11c-2-8-2-20 0-32M38 9v4c0 9 2 22 4 28H31c2-8 2-20 0-32" />}
    {name === "check" && <path d="M10 25l9 9 19-20" />}
    {name === "x" && <path d="M14 14l20 20M34 14L14 34" />}
    {name === "chat" && <path d="M24 7C14 7 6 14 6 23c0 4 1.5 7 4 10l-2 8 8-3c2.5 1 5 2 8 2 10 0 18-7 18-17S34 7 24 7z" />}
    {name === "cal" && <><rect x={6} y={10} width={36} height={32} rx={4} /><path d="M6 19h36M15 6v8M33 6v8" /></>}
  </g></svg>
);

const Social: React.FC<{ v: V; t: number }> = ({ v, t }) => (
  <div style={{ position: "absolute", left: 0, right: 0, top: TOP, display: "flex", justifyContent: "center", gap: 24 }}>
    {([["FACEBOOK", "fb", "#1877F2"], ["TIKTOK", "tt", "#111"]] as [string, string, string][]).map(([l, k, c]) => {
      const p = pop(t, n(v, k), 0.35);
      return <div key={l} style={{ transform: `scale(${p})`, opacity: Math.min(1, p * 1.5), background: c, color: "#fff", borderRadius: 999, padding: "16px 34px", border: "4px solid #fff", boxShadow: "0 12px 26px rgba(0,0,0,0.35)", ...txt(40, "#fff") }}>{l}</div>;
    })}
  </div>
);

const Timeline: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const items = v.items as [string, string, number][];
  const prog = interpolate(t, [items[0][2], items[items.length - 1][2] + 0.3], [0, 1], clamp);
  return (
    <div style={{ position: "absolute", left: 40, right: 40, top: TOP, height: 230 }}>
      <div style={{ position: "absolute", left: 80, right: 80, top: 58, height: 10, borderRadius: 5, background: "rgba(255,255,255,0.4)" }}>
        <div style={{ width: `${prog * 100}%`, height: "100%", borderRadius: 5, background: goldGrad }} />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        {items.map(([l, ic, at]) => {
          const q = pop(t, at, 0.35); const on = t >= at;
          return (
            <div key={l} style={{ width: 200, display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
              <div style={{ width: 126, height: 126, borderRadius: 63, background: on ? goldGrad : "rgba(0,0,0,0.5)", border: "5px solid #fff", display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${0.75 + 0.25 * q})` }}><Icon name={ic} size={70} color={on ? C.ink : "#fff"} /></div>
              <div style={{ ...txt(30, "#fff"), textShadow: "0 3px 10px rgba(0,0,0,0.7)", opacity: 0.45 + 0.55 * q }}>{l}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

const Score: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const p = pop(t, n(v, "at"), 0.4);
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: TOP, display: "flex", flexDirection: "column", alignItems: "center", gap: 14 }}>
      <div style={{ transform: `scale(${2 - p}) rotate(-6deg)`, opacity: interpolate(t, [n(v, "at"), n(v, "at") + 0.08], [0, 1], clamp), background: C.emerald, border: `7px solid ${C.gold}`, borderRadius: 30, padding: "4px 40px", boxShadow: "0 16px 36px rgba(0,0,0,0.45)" }}>
        <span style={{ ...txt(110, C.goldLight) }}>10/10</span>
      </div>
      <Stars v={{ ...v, s: n(v, "at") + 0.3 }} t={t} inline />
    </div>
  );
};

// The customer's own WhatsApp messages (name and receipt cropped out).
const Wa: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const p = pop(t, n(v, "at"), 0.4);
  return (
    <div style={{ position: "absolute", left: 440, right: 60, top: 150, transform: `translateY(${(1 - p) * -60}px) scale(${0.85 + 0.15 * p}) rotate(2deg)`, opacity: Math.min(1, p * 1.5) }}>
      <div style={{ display: "inline-flex", background: C.wa, color: "#fff", borderRadius: 999, padding: "6px 18px", ...txt(24, "#fff", 800), marginBottom: 10, boxShadow: "0 8px 18px rgba(0,0,0,0.3)" }}>MAKLUM BALAS DI WHATSAPP</div>
      <div style={{ borderRadius: 22, overflow: "hidden", border: "5px solid #fff", boxShadow: "0 18px 40px rgba(0,0,0,0.45)" }}>
        <Img src={staticFile("img/wa.png")} style={{ width: "100%", display: "block" }} />
      </div>
    </div>
  );
};

const Stars: React.FC<{ v: V; t: number; inline?: boolean }> = ({ v, t, inline }) => (
  <div style={{ position: inline ? "relative" : "absolute", left: 0, right: 0, top: inline ? 0 : TOP, display: "flex", justifyContent: "center", gap: 12, filter: "drop-shadow(0 8px 18px rgba(0,0,0,0.45))" }}>
    {[0, 1, 2, 3, 4].map((i) => {
      const p = pop(t, v.s + i * 0.1, 0.35);
      return <svg key={i} width={120} height={120} viewBox="0 0 48 48" style={{ transform: `scale(${p}) rotate(${(1 - p) * -90}deg)`, opacity: Math.min(1, p * 1.5) }}><path d="M24 4l6 12.6 13.8 1.8-10.1 9.6 2.6 13.7L24 35l-12.3 6.7 2.6-13.7L4.2 18.4 18 16.6z" fill={C.gold} stroke="#fff" strokeWidth={2} /></svg>;
    })}
  </div>
);

const MAP: Record<string, React.FC<{ v: V; t: number }>> = { social: Social, timeline: Timeline, wa: Wa, score: Score, stars: Stars };

export const VizLayer: React.FC = () => {
  const t = useCurrentFrame() / tl.fps;
  const v = (tl.viz as V[]).find((x) => t >= x.s - 0.05 && t < x.e + 0.2);
  if (!v) return null;
  const Comp = MAP[v.type];
  const out = interpolate(t, [v.e, v.e + 0.2], [1, 0], clamp);
  return <div style={{ position: "absolute", inset: 0, opacity: out }}>{Comp ? <Comp v={v} t={t} /> : null}</div>;
};
