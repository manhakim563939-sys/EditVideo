import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import tl from "./timeline.json";
import { C, F, goldGrad, goldText } from "./theme";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const pop = (t: number, at: number, d = 0.3) => interpolate(t, [at, at + d], [0, 1], { easing: Easing.out(Easing.back(1.8)), ...clamp });
const rise = (t: number, at: number, d = 0.4) => interpolate(t, [at, at + d], [0, 1], { easing: Easing.out(Easing.cubic), ...clamp });
const draw = (t: number, at: number, d = 0.6) => interpolate(t, [at, at + d], [0, 1], { easing: Easing.inOut(Easing.cubic), ...clamp });

type V = { type: string; s: number; e: number; [k: string]: unknown };
const n = (v: V, k: string) => v[k] as number;
const TOP = 200;
const card: React.CSSProperties = { background: "rgba(255,255,255,0.95)", borderRadius: 26, boxShadow: "0 18px 40px rgba(0,0,0,0.3)" };
const txt = (size: number, color = C.ink, w = 900): React.CSSProperties => ({ fontFamily: F.kin, fontWeight: w, fontSize: size, color, lineHeight: 1.1 });

const Star: React.FC<{ p: number; size: number }> = ({ p, size }) => (
  <svg width={size} height={size} viewBox="0 0 48 48" style={{ transform: `scale(${p}) rotate(${(1 - p) * -90}deg)`, opacity: Math.min(1, p * 1.5) }}>
    <defs><linearGradient id="sg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={C.goldLight} /><stop offset="1" stopColor={C.goldDark} /></linearGradient></defs>
    <path d="M24 4l6 12.6 13.8 1.8-10.1 9.6 2.6 13.7L24 35l-12.3 6.7 2.6-13.7L4.2 18.4 18 16.6z" fill="url(#sg)" stroke="#fff" strokeWidth={2} />
  </svg>
);

const Stars: React.FC<{ v: V; t: number }> = ({ v, t }) => (
  <div style={{ position: "absolute", left: 0, right: 0, top: TOP, display: "flex", flexDirection: "column", alignItems: "center", gap: 14 }}>
    <div style={{ display: "flex", gap: 12, filter: "drop-shadow(0 8px 18px rgba(0,0,0,0.45))" }}>
      {[0, 1, 2, 3, 4].map((i) => <Star key={i} p={pop(t, v.s + 0.1 + i * 0.1, 0.35)} size={120} />)}
    </div>
  </div>
);

const Ruler: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const d = draw(t, v.s, 0.6);
  return (
    <div style={{ position: "absolute", left: 90, top: TOP + 60, width: 900 * d, height: 110, background: "#F6D96B", border: `6px solid ${C.ink}`, borderRadius: 10, overflow: "hidden", boxShadow: "0 12px 28px rgba(0,0,0,0.35)" }}>
      <div style={{ position: "absolute", inset: 0, backgroundImage: `repeating-linear-gradient(90deg, ${C.ink} 0 4px, transparent 4px 30px)`, backgroundSize: "30px 50px", backgroundRepeat: "repeat-x" }} />
    </div>
  );
};

const Score: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const items = v.items as [string, number][];
  const p = pop(t, v.s, 0.35);
  return (
    <div style={{ ...card, position: "absolute", left: 90, top: TOP - 20, width: 900, padding: "26px 36px", transform: `scale(${p})`, transformOrigin: "50% 0%", opacity: Math.min(1, p * 1.5) }}>
      <div style={{ ...txt(30, C.goldDark, 800), letterSpacing: 4, marginBottom: 14 }}>KATA PELANGGAN</div>
      {items.map(([l, at]) => {
        const q = pop(t, at, 0.3);
        return (
          <div key={l} style={{ display: "flex", alignItems: "center", gap: 18, marginTop: 6, opacity: 0.3 + 0.7 * Math.min(1, q), transform: `translateX(${(1 - Math.min(1, q)) * -40}px)` }}>
            <div style={{ width: 52, height: 52, borderRadius: 26, background: q > 0.5 ? goldGrad : "#E6E1D5", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              <svg width={38} height={38} viewBox="0 0 48 48"><path d="M10 25l9 9 19-20" fill="none" stroke={C.ink} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - Math.min(1, q)} /></svg>
            </div>
            <div style={txt(40)}>{l}</div>
          </div>
        );
      })}
    </div>
  );
};

const Price: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const p = pop(t, v.s, 0.35);
  const ok = pop(t, n(v, "ok"), 0.4);
  const barg = rise(t, n(v, "bargain"));
  const swing = Math.sin((t - v.s) * 3) * 6 * (1 - ok);
  return (
    <div style={{ position: "absolute", left: 90, top: TOP, width: 900, height: 380 }}>
      <div style={{ position: "absolute", left: 40, top: 0, transform: `rotate(${-10 + swing}deg) scale(${p})`, transformOrigin: "20% 50%", opacity: Math.min(1, p * 1.5) }}>
        <svg width={420} height={250} viewBox="0 0 420 250">
          <path d="M20 125 L110 20 H400 V230 H110 Z" fill="#fff" stroke={C.goldDark} strokeWidth={9} strokeLinejoin="round" />
          <circle cx={112} cy={125} r={20} fill="none" stroke={C.goldDark} strokeWidth={9} />
          <text x={275} y={150} textAnchor="middle" fontFamily="Montserrat" fontWeight={900} fontSize={66} fill={C.ink}>HARGA</text>
        </svg>
      </div>
      {/* bargain arrows meeting in the middle */}
      <div style={{ position: "absolute", left: 470, top: 70, width: 400, opacity: barg }}>
        <svg width={400} height={120} viewBox="0 0 400 120">
          <path d={`M10 40 H${120 + 70 * barg}`} stroke={C.goldLight} strokeWidth={14} strokeLinecap="round" />
          <path d={`M390 80 H${280 - 70 * barg}`} stroke="#fff" strokeWidth={14} strokeLinecap="round" />
        </svg>
      </div>
      <div style={{ position: "absolute", left: 520, top: 170, transform: `scale(${2 - ok}) rotate(-8deg)`, opacity: interpolate(t, [n(v, "ok"), n(v, "ok") + 0.08], [0, 1], clamp), background: C.emerald, border: `6px solid ${C.gold}`, borderRadius: 20, padding: "12px 36px", boxShadow: "0 14px 30px rgba(0,0,0,0.4)" }}>
        <span style={txt(72, C.goldLight)}>OKEY! ✓</span>
      </div>
    </div>
  );
};

const Person: React.FC<{ s: number; p: number; label: string }> = ({ s, p, label }) => (
  <div style={{ display: "flex", flexDirection: "column", alignItems: "center", transform: `translateY(${(1 - p) * 60}px) scale(${0.7 + 0.3 * p})`, opacity: Math.min(1, p * 1.5) }}>
    <div style={{ position: "relative" }}>
      <svg width={s} height={s} viewBox="0 0 48 48"><circle cx={24} cy={24} r={23} fill="#fff" /><circle cx={24} cy={18} r={8} fill={C.emerald} /><path d="M9 41c1-9 8-13 15-13s14 4 15 13" fill={C.emerald} /></svg>
      <div style={{ position: "absolute", right: -6, bottom: -6, width: s * 0.42, height: s * 0.42, borderRadius: s, background: goldGrad, display: "flex", alignItems: "center", justifyContent: "center", border: "4px solid #fff" }}>
        <svg width={s * 0.26} height={s * 0.26} viewBox="0 0 48 48"><path d="M10 25l9 9 19-20" fill="none" stroke={C.ink} strokeWidth={7} strokeLinecap="round" strokeLinejoin="round" /></svg>
      </div>
    </div>
    <div style={{ ...txt(34, "#fff", 900), marginTop: 12, textShadow: "0 3px 10px rgba(0,0,0,0.6)" }}>{label}</div>
  </div>
);

const Family: React.FC<{ v: V; t: number }> = ({ v, t }) => (
  <div style={{ position: "absolute", left: 0, right: 0, top: TOP, display: "flex", justifyContent: "center", gap: 40 }}>
    <Person s={170} p={pop(t, n(v, "wife"), 0.35)} label="WIFE" />
    <Person s={140} p={pop(t, n(v, "kids"), 0.35)} label="ANAK" />
    <Person s={140} p={pop(t, n(v, "kids") + 0.15, 0.35)} label="ANAK" />
    <div style={{ alignSelf: "center", transform: `scale(${pop(t, n(v, "seller"), 0.35)}) rotate(6deg)`, background: goldGrad, borderRadius: 16, padding: "12px 22px", boxShadow: "0 12px 26px rgba(0,0,0,0.35)" }}>
      <span style={txt(34)}>KENAL<br />SELLER</span>
    </div>
  </div>
);

const Aftercare: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const steps: [string, string][] = [["KONTRAK SELESAI", "done"], ["DAH BAYAR", "paid"], ["MASIH DATANG", "came"]];
  const prog = interpolate(t, [n(v, "done"), n(v, "came") + 0.3], [0, 1], clamp);
  return (
    <div style={{ ...card, position: "absolute", left: 90, top: TOP - 10, width: 900, padding: "34px 30px 30px" }}>
      <div style={{ position: "absolute", left: 140, right: 140, top: 92, height: 10, borderRadius: 5, background: "#E6E1D5" }}>
        <div style={{ width: `${prog * 100}%`, height: "100%", borderRadius: 5, background: goldGrad }} />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        {steps.map(([l, k], i) => {
          const q = pop(t, n(v, k), 0.35);
          const last = i === 2;
          return (
            <div key={l} style={{ width: 260, display: "flex", flexDirection: "column", alignItems: "center", opacity: 0.3 + 0.7 * Math.min(1, q) }}>
              <div style={{ width: 120, height: 120, borderRadius: 60, background: last ? C.emerald : q > 0.5 ? goldGrad : "#E6E1D5", border: last ? `5px solid ${C.gold}` : "none", display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${0.8 + 0.2 * Math.min(1, q)})` }}>
                <svg width={66} height={66} viewBox="0 0 48 48"><g fill="none" stroke={last ? C.goldLight : C.ink} strokeWidth={4} strokeLinecap="round" strokeLinejoin="round">
                  {i === 0 && <path d="M12 5h17l8 8v30H12zM18 28l5 5 9-10" />}
                  {i === 1 && <><rect x={5} y={12} width={38} height={24} rx={4} /><circle cx={24} cy={24} r={6} /></>}
                  {i === 2 && <path d="M29 9a9 9 0 00-11 11L6 32l6 6 12-12a9 9 0 0011-11l-5 5-5-1-1-5z" />}
                </g></svg>
              </div>
              <div style={{ ...txt(32), marginTop: 14, textAlign: "center" }}>{l}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

const Worth: React.FC<{ v: V; t: number }> = ({ v, t }) => {
  const p = pop(t, n(v, "at"), 0.4);
  const fill = rise(t, n(v, "at") - 0.6, 1.0);
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: TOP, display: "flex", flexDirection: "column", alignItems: "center" }}>
      <div style={{ ...card, width: 820, padding: "26px 34px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", ...txt(30, "#666", 800) }}><span>HARGA</span><span>KUALITI</span></div>
        <div style={{ position: "relative", height: 40, marginTop: 14, borderRadius: 20, background: "#E6E1D5", overflow: "hidden" }}>
          <div style={{ width: `${fill * 100}%`, height: "100%", background: goldGrad }} />
        </div>
      </div>
      <div style={{ marginTop: -26, transform: `scale(${2 - p}) rotate(-6deg)`, opacity: interpolate(t, [n(v, "at"), n(v, "at") + 0.08], [0, 1], clamp), background: C.emerald, border: `6px solid ${C.gold}`, borderRadius: 20, padding: "10px 40px", boxShadow: "0 14px 30px rgba(0,0,0,0.4)" }}>
        <span style={{ ...txt(80), ...goldText }}>WORTH IT</span>
      </div>
    </div>
  );
};

const MAP: Record<string, React.FC<{ v: V; t: number }>> = { stars: Stars, ruler: Ruler, score: Score, price: Price, family: Family, aftercare: Aftercare, worth: Worth };

export const VizLayer: React.FC = () => {
  const t = useCurrentFrame() / tl.fps;
  const v = (tl.viz as V[]).find((x) => t >= x.s - 0.05 && t < x.e + 0.2);
  if (!v) return null;
  const Comp = MAP[v.type];
  const out = interpolate(t, [v.e, v.e + 0.2], [1, 0], clamp);
  return <div style={{ position: "absolute", inset: 0, opacity: out }}>{Comp ? <Comp v={v} t={t} /> : null}</div>;
};
