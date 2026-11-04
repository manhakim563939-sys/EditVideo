import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import tl from "./timeline.json";
import { C, F, goldGrad } from "./theme";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const pop = (t: number, at: number, d = 0.3) => interpolate(t, [at, at + d], [0, 1], { easing: Easing.out(Easing.back(1.8)), ...clamp });
const draw = (t: number, at: number, d = 0.5) => interpolate(t, [at, at + d], [0, 1], { easing: Easing.inOut(Easing.cubic), ...clamp });
type V = { type: string; s: number; e: number; [k: string]: unknown };
const n = (v: V, k: string) => v[k] as number;
const txt = (size: number, color = C.ink, w = 900): React.CSSProperties => ({ fontFamily: F.kin, fontWeight: w, fontSize: size, color, lineHeight: 1.1 });
const TOP = 230;
const card: React.CSSProperties = { background: "rgba(255,255,255,0.95)", borderRadius: 26, boxShadow: "0 18px 40px rgba(0,0,0,0.3)" };

const Mark: React.FC<{ ok: boolean; p: number }> = ({ ok, p }) => (
  <div style={{ position: "absolute", right: -14, top: -6, width: 76, height: 76, borderRadius: 38, background: ok ? goldGrad : "#C0392B", border: "5px solid #fff", display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${p})` }}>
    <svg width={44} height={44} viewBox="0 0 48 48"><path d={ok ? "M10 25l9 9 19-20" : "M14 14l20 20M34 14L14 34"} fill="none" stroke={ok ? C.ink : "#fff"} strokeWidth={7} strokeLinecap="round" strokeLinejoin="round" /></svg>
  </div>
);

// "Sebelum ni kebanyakannya lelaki" -> "saya nak yang perempuan"
const Gender: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const m = pop(t, n(v, "male"), 0.35);
  const f = pop(t, n(v, "female"), 0.4);
  const person = (hijab: boolean) => (
    <svg width={190} height={190} viewBox="0 0 48 48">
      <circle cx={24} cy={24} r={23} fill="#fff" />
      {hijab ? (
        <><path d="M12 22c0-8 5-13 12-13s12 5 12 13v8c-3 3-7 5-12 5s-9-2-12-5z" fill="#C0392B" /><circle cx={24} cy={21} r={6.5} fill="#F1D3B8" /><path d="M8 44c2-7 8-10 16-10s14 3 16 10" fill="#C0392B" /></>
      ) : (
        <><circle cx={24} cy={18} r={8} fill="#6E7F8C" /><path d="M9 43c1-9 8-13 15-13s14 4 15 13" fill="#6E7F8C" /></>
      )}
    </svg>
  );
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: TOP, display: "flex", justifyContent: "center", gap: 70 }}>
      <div style={{ position: "relative", transform: `scale(${0.6 + 0.4 * m})`, opacity: Math.min(1, m * 1.5) * (f > 0.5 ? 0.55 : 1) }}>
        {person(false)}<Mark ok={false} p={pop(t, n(v, "female") - 0.2)} />
        <div style={{ ...txt(30, "#fff"), textAlign: "center", marginTop: 8, textShadow: "0 3px 10px rgba(0,0,0,0.6)" }}>LELAKI</div>
      </div>
      <div style={{ position: "relative", transform: `scale(${(0.6 + 0.4 * f) * (f > 0.9 ? 1.08 : 1)})`, opacity: Math.min(1, f * 1.5) }}>
        {person(true)}<Mark ok p={pop(t, n(v, "female") + 0.2)} />
        <div style={{ ...txt(30, C.goldLight), textAlign: "center", marginTop: 8, textShadow: "0 3px 10px rgba(0,0,0,0.6)" }}>PEREMPUAN</div>
      </div>
    </div>
  );
};

// Sped-up footage badge (honest: the install clip is a timelapse).
const Fast: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const p = pop(t, v.s + 0.1, 0.3);
  return (
    <div style={{ position: "absolute", right: 70, top: TOP, transform: `scale(${p})`, transformOrigin: "100% 0%", display: "flex", alignItems: "center", gap: 12, background: "rgba(0,0,0,0.6)", border: `3px solid ${C.gold}`, borderRadius: 999, padding: "10px 24px" }}>
      <svg width={44} height={44} viewBox="0 0 48 48"><path d="M6 12l16 12-16 12zM24 12l16 12-16 12z" fill={C.goldLight} /></svg>
      <span style={txt(32, "#fff")}>TIMELAPSE PEMASANGAN</span>
    </div>
  );
};

const Calendar: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const p = pop(t, v.s, 0.35);
  const fill = interpolate(t, [n(v, "done"), n(v, "done") + 0.9], [0, 9], clamp);
  const pr = pop(t, n(v, "promise"), 0.35);
  return (
    <div style={{ ...card, position: "absolute", left: 90, top: TOP - 20, width: 900, padding: 22, transform: `scale(${p})`, transformOrigin: "50% 0%", opacity: Math.min(1, p * 1.5) }}>
      <div style={{ background: C.emerald, borderRadius: 14, padding: "8px 0", textAlign: "center", ...txt(32, C.goldLight) }}>2 MINGGU</div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: 8, marginTop: 14 }}>
        {Array.from({ length: 14 }, (_, i) => {
          const d = i + 1;
          const on = d <= fill;
          return (
            <div key={d} style={{ position: "relative", height: 64, borderRadius: 10, background: on ? goldGrad : "#EFEBE1", display: "flex", alignItems: "center", justifyContent: "center", ...txt(24, on ? C.ink : "#AAA", 800), border: d === 14 ? `4px dashed ${pr > 0.5 ? "#888" : "transparent"}` : "none" }}>
              {d}
              {d === 9 && fill >= 8.9 && <div style={{ position: "absolute", top: -26, left: -20, right: -20, textAlign: "center", ...txt(20, C.emerald, 900) }}>SIAP ✓</div>}
            </div>
          );
        })}
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 12, ...txt(24, "#555", 800) }}>
        <span>SIAP LEBIH AWAL</span><span style={{ opacity: pr }}>JANJI: 2 MINGGU</span>
      </div>
    </div>
  );
};

const Swatches: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const base = ["#CDBFAF", "#B9A68A", "#8E7B6A", "#EFEAE2", "#6B4A3A", "#9AA3AE", "#D9C7A6"];
  const extra = ["#3E7C78", "#D6A6B4", "#4E5A56", "#C08A4F"];
  const cp = interpolate(t, [n(v, "colors"), n(v, "colors") + 0.5], [0, 1], clamp);
  const cols = [...base, ...(cp > 0 ? extra : [])];
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: TOP + 10, height: 340 }}>
      {cols.map((c, i) => {
        const at = i < base.length ? n(v, "at") + i * 0.07 : n(v, "colors") + (i - base.length) * 0.08;
        const p = pop(t, at, 0.35);
        const spread = cols.length > 8 ? 8 : 11;
        return <div key={i} style={{ position: "absolute", left: 480, top: 0, width: 120, height: 280, borderRadius: 16, background: `repeating-linear-gradient(90deg, rgba(0,0,0,0.14) 0 12px, rgba(255,255,255,0.1) 12px 24px), ${c}`, border: "5px solid #fff", boxShadow: "0 10px 24px rgba(0,0,0,0.45)", transformOrigin: "50% 130%", transform: `rotate(${(i - (cols.length - 1) / 2) * spread * p}deg)`, opacity: Math.min(1, p * 1.5) }} />;
      })}
    </div>
  );
};

// Quick reply: customer bubble, typing dots, instant reply tick.
const Chat: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const a = pop(t, n(v, "msg"), 0.3);
  const typing = t >= n(v, "msg") + 0.15 && t < n(v, "reply");
  const r = pop(t, n(v, "reply"), 0.3);
  const bubble = (mine: boolean, child: React.ReactNode, p: number) => (
    <div style={{ alignSelf: mine ? "flex-end" : "flex-start", background: mine ? "#DCF8C6" : "#fff", borderRadius: mine ? "26px 26px 6px 26px" : "26px 26px 26px 6px", padding: "18px 26px", boxShadow: "0 8px 20px rgba(0,0,0,0.25)", transform: `scale(${p})`, transformOrigin: mine ? "100% 100%" : "0% 100%", opacity: Math.min(1, p * 1.5) }}>{child}</div>
  );
  return (
    <div style={{ position: "absolute", left: 110, right: 110, top: TOP, display: "flex", flexDirection: "column", gap: 16 }}>
      {bubble(true, <span style={txt(36, "#222", 700)}>Nak tempah langsir…</span>, a)}
      {typing && bubble(false, <span style={txt(40, "#888")}>{".".repeat(1 + (Math.floor(t * 8) % 3))}</span>, 1)}
      {r > 0 && bubble(false, <span style={txt(36, C.emerald, 800)}>✓ DIBALAS CEPAT</span>, r)}
    </div>
  );
};

const OffDay: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const days = ["ISN", "SEL", "RAB", "KHA", "JUM", "SAB", "AHD"];
  const p = pop(t, v.s, 0.35);
  const c = pop(t, n(v, "cuti"), 0.35);
  const come = interpolate(t, [n(v, "come"), n(v, "come") + 0.6], [0, 1], { easing: Easing.out(Easing.cubic), ...clamp });
  const idx = 5;
  return (
    <div style={{ ...card, position: "absolute", left: 90, top: TOP - 10, width: 900, height: 300, padding: 24, transform: `scale(${p})`, transformOrigin: "50% 0%", opacity: Math.min(1, p * 1.5) }}>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        {days.map((d, i) => (
          <div key={d} style={{ width: 112, height: 120, borderRadius: 14, background: i === idx && c > 0.5 ? goldGrad : "#EFEBE1", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", transform: i === idx ? `scale(${1 + 0.08 * c})` : "none", border: i === idx && c > 0.5 ? `4px solid ${C.emerald}` : "none" }}>
            <span style={txt(26, i === idx && c > 0.5 ? C.ink : "#777", 900)}>{d}</span>
            {i === idx && <span style={{ ...txt(22, C.emerald, 900), opacity: c, marginTop: 6 }}>CUTI</span>}
          </div>
        ))}
      </div>
      <div style={{ position: "relative", height: 110, marginTop: 20 }}>
        <div style={{ position: "absolute", left: 0, right: 0, top: 70, height: 6, borderRadius: 3, background: "#E6E1D5" }} />
        <div style={{ position: "absolute", top: 8, left: -40 + come * (idx * 128 + 60), opacity: Math.min(1, come * 3) }}>
          <svg width={110} height={74} viewBox="0 0 64 42"><rect x={2} y={8} width={36} height={22} rx={3} fill={C.emerald} /><path d="M38 14h12l8 8v8H38z" fill={C.gold} /><circle cx={14} cy={34} r={6} fill="#333" /><circle cx={48} cy={34} r={6} fill="#333" /></svg>
        </div>
        {come > 0.95 && <div style={{ position: "absolute", top: 82, left: idx * 128 - 40, ...txt(28, C.emerald, 900) }}>DATANG ✓</div>}
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

const MAP: Record<string, React.FC<{ v: V; t: number }>> = { gender: Gender, fast: Fast, calendar: Calendar, swatches: Swatches, chat: Chat, offday: OffDay, stars: Stars };

export const VizLayer: React.FC = () => {
  const t = useCurrentFrame() / tl.fps;
  const v = (tl.viz as V[]).find((x) => t >= x.s - 0.05 && t < x.e + 0.2);
  if (!v) return null;
  const Comp = MAP[v.type];
  const out = interpolate(t, [v.e, v.e + 0.2], [1, 0], clamp);
  return <div style={{ position: "absolute", inset: 0, opacity: out }}>{Comp ? <Comp v={v} t={t} /> : null}</div>;
};
export { draw };
