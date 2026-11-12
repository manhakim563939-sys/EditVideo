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
  </g></svg>
);

// Taman Kempas (far, X) vs Aimi Curtain near home (check).
const Distance: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const far = pop(t, n(v, "far"), 0.35);
  const x = pop(t, n(v, "x"), 0.3);
  const near = pop(t, n(v, "near"), 0.4);
  const road = interpolate(t, [n(v, "far"), n(v, "far") + 0.8], [0, 1], clamp);
  const place = (label: string, sub: string, p: number, ok: boolean | null) => (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", transform: `scale(${p})`, opacity: Math.min(1, p * 1.5) }}>
      <div style={{ position: "relative", width: 130, height: 130, borderRadius: 30, background: ok ? goldGrad : "#fff", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 12px 26px rgba(0,0,0,0.35)" }}>
        <Icon name="store" size={84} />
        {ok !== null && <div style={{ position: "absolute", right: -14, top: -14, width: 56, height: 56, borderRadius: 28, background: ok ? "#2E7D55" : "#C0392B", border: "4px solid #fff", display: "flex", alignItems: "center", justifyContent: "center" }}><Icon name={ok ? "check" : "x"} size={32} color="#fff" /></div>}
      </div>
      <div style={{ ...txt(28, "#fff"), marginTop: 10, textShadow: "0 3px 10px rgba(0,0,0,0.7)", textAlign: "center" }}>{label}</div>
      <div style={{ ...txt(22, C.goldLight, 800), textShadow: "0 3px 10px rgba(0,0,0,0.7)" }}>{sub}</div>
    </div>
  );
  return (
    <div style={{ position: "absolute", left: 40, right: 40, top: TOP, display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
      {place("TAMAN KEMPAS", "JAUH", far, t >= n(v, "x") ? false : null)}
      <div style={{ flex: 1, margin: "60px 10px 0", height: 8, borderRadius: 4, background: `repeating-linear-gradient(90deg, #fff 0 22px, transparent 22px 40px)`, opacity: 0.8, transform: `scaleX(${road})`, transformOrigin: "0% 50%", display: "flex", justifyContent: "center" }}>
        <div style={{ marginTop: -54, transform: `scale(${pop(t, n(v, "near") - 0.2)})` }}><Icon name="house" size={70} color="#fff" /></div>
      </div>
      {place("AIMI CURTAIN", "DEKAT RUMAH", near, t >= n(v, "near") + 0.2 ? true : null)}
    </div>
  );
};

// Usual 2 weeks vs this job: deal yesterday, done today.
const Speed: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const p = pop(t, v.s, 0.35);
  const slow = interpolate(t, [n(v, "slow"), n(v, "slow") + 1.0], [0, 1], { easing: Easing.out(Easing.cubic), ...clamp });
  const fast = pop(t, n(v, "fast"), 0.35);
  const row = (label: string, days: string, w: number, gold: boolean, o: number) => (
    <div style={{ display: "flex", alignItems: "center", gap: 14, opacity: o }}>
      <div style={{ width: 210, ...txt(26, C.ink, 800) }}>{label}</div>
      <div style={{ flex: 1, height: 44, borderRadius: 22, background: "#ECE7DA", overflow: "hidden" }}>
        <div style={{ width: `${w * 100}%`, height: "100%", background: gold ? goldGrad : "#9AA3AE", borderRadius: 22 }} />
      </div>
      <div style={{ width: 150, textAlign: "right", ...txt(34, gold ? C.ink : "#666") }}>{days}</div>
    </div>
  );
  return (
    <div style={{ ...card, position: "absolute", left: 70, right: 70, top: TOP, padding: "26px 30px", display: "grid", gap: 18, transform: `scale(${p})`, transformOrigin: "50% 0%", opacity: Math.min(1, p * 1.5) }}>
      {row("SELALUNYA", "2 MINGGU", slow, false, 1)}
      {row("AIMI CURTAIN", "1 HARI", 0.07 * fast, true, fast > 0 ? 1 : 0.25)}
    </div>
  );
};

const Steps: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const items = v.items as [string, number][];
  const icons = ["store", "ruler", "hook"];
  const prog = interpolate(t, [items[0][1], items[2][1] + 0.3], [0, 1], clamp);
  return (
    <div style={{ position: "absolute", left: 60, right: 60, top: TOP, height: 240 }}>
      <div style={{ position: "absolute", left: 100, right: 100, top: 68, height: 10, borderRadius: 5, background: "rgba(255,255,255,0.4)" }}>
        <div style={{ width: `${prog * 100}%`, height: "100%", borderRadius: 5, background: goldGrad }} />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        {items.map(([l, at], i) => {
          const q = pop(t, at, 0.35);
          const on = t >= at;
          return (
            <div key={l} style={{ width: 200, display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
              <div style={{ width: 146, height: 146, borderRadius: 73, background: on ? goldGrad : "rgba(0,0,0,0.5)", border: "5px solid #fff", display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${0.75 + 0.25 * q})` }}><Icon name={icons[i]} size={80} color={on ? C.ink : "#fff"} /></div>
              <div style={{ ...txt(32, "#fff"), textShadow: "0 3px 10px rgba(0,0,0,0.7)", opacity: 0.45 + 0.55 * q }}>{l}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// The customer's own WhatsApp messages (name and receipt cropped out).
const Wa: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const p = pop(t, n(v, "at"), 0.4);
  return (
    <div style={{ position: "absolute", left: 90, right: 90, top: TOP - 20, transform: `translateY(${(1 - p) * -60}px) scale(${0.85 + 0.15 * p}) rotate(-2deg)`, opacity: Math.min(1, p * 1.5) }}>
      <div style={{ display: "inline-flex", background: C.wa, color: "#fff", borderRadius: 999, padding: "6px 18px", ...txt(24, "#fff", 800), marginBottom: 10, boxShadow: "0 8px 18px rgba(0,0,0,0.3)" }}>MESEJ PELANGGAN DI WHATSAPP</div>
      <div style={{ borderRadius: 22, overflow: "hidden", border: "5px solid #fff", boxShadow: "0 18px 40px rgba(0,0,0,0.45)" }}>
        <Img src={staticFile("img/wa.png")} style={{ width: "100%", display: "block" }} />
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

const MAP: Record<string, React.FC<{ v: V; t: number }>> = { distance: Distance, speed: Speed, steps: Steps, wa: Wa, stars: Stars };

export const VizLayer: React.FC = () => {
  const t = useCurrentFrame() / tl.fps;
  const v = (tl.viz as V[]).find((x) => t >= x.s - 0.05 && t < x.e + 0.2);
  if (!v) return null;
  const Comp = MAP[v.type];
  const out = interpolate(t, [v.e, v.e + 0.2], [1, 0], clamp);
  return <div style={{ position: "absolute", inset: 0, opacity: out }}>{Comp ? <Comp v={v} t={t} /> : null}</div>;
};
