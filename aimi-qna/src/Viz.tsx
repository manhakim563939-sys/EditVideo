import React from "react";
import { Easing, Img, interpolate, staticFile } from "remotion";
import { C, F, goldGrad, goldText } from "./theme";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const pop = (t: number, at: number, d = 0.3) => interpolate(t, [at, at + d], [0, 1], { easing: Easing.out(Easing.back(1.8)), ...clamp });
const rise = (t: number, at: number, d = 0.4) => interpolate(t, [at, at + d], [0, 1], { easing: Easing.out(Easing.cubic), ...clamp });
const draw = (t: number, at: number, d = 0.6) => interpolate(t, [at, at + d], [0, 1], { easing: Easing.inOut(Easing.cubic), ...clamp });

export type VizEv = { type: string; s: number; e: number; [k: string]: unknown };
const n = (v: VizEv, k: string) => v[k] as number;

const ZONE_TOP = 240; // clean wall above the speaker's head
const card: React.CSSProperties = { background: "rgba(255,255,255,0.94)", borderRadius: 26, boxShadow: "0 18px 40px rgba(0,0,0,0.28)" };
const txt = (size: number, color = C.ink, w = 900): React.CSSProperties => ({ fontFamily: F.kin, fontWeight: w, fontSize: size, color, lineHeight: 1.1 });

const Check: React.FC<{ p: number; size?: number }> = ({ p, size = 56 }) => (
  <div style={{ width: size, height: size, borderRadius: size / 2, background: p > 0.5 ? goldGrad : "rgba(0,0,0,0.12)", display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${0.8 + 0.2 * p})` }}>
    <svg width={size * 0.6} height={size * 0.6} viewBox="0 0 48 48"><path d="M10 25l9 9 19-20" fill="none" stroke={p > 0.5 ? C.ink : "#fff"} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - p} /></svg>
  </div>
);

// ---------------------------------------------------------------- Q1
const Budget: React.FC<{ v: VizEv; t: number }> = ({ v, t }) => {
  const p = pop(t, v.s, 0.35);
  const k = 0.5 + 0.28 * Math.sin((t - v.s) * 1.6); // knob keeps adjusting to the budget
  return (
    <div style={{ ...card, position: "absolute", left: 90, top: ZONE_TOP, width: 900, padding: "34px 44px", transform: `scale(${p})`, opacity: Math.min(1, p * 1.5) }}>
      <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
        <svg width={80} height={80} viewBox="0 0 48 48"><g fill="none" stroke={C.goldDark} strokeWidth={3.5} strokeLinejoin="round"><rect x={5} y={13} width={38} height={26} rx={4} /><path d="M33 22h10v10H33a5 5 0 010-10z" /><path d="M9 13l24-7 3 7" /></g></svg>
        <div style={txt(46)}>BAJET ANDA</div>
      </div>
      <div style={{ position: "relative", height: 36, marginTop: 30, borderRadius: 18, background: "#E8E3D6" }}>
        <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: `${k * 100}%`, borderRadius: 18, background: goldGrad }} />
        <div style={{ position: "absolute", left: `calc(${k * 100}% - 28px)`, top: -10, width: 56, height: 56, borderRadius: 28, background: "#fff", border: `6px solid ${C.goldDark}` }} />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 16, ...txt(26, "#777", 700) }}><span>JIMAT</span><span>PREMIUM</span></div>
    </div>
  );
};

const Rooms: React.FC<{ v: VizEv; t: number }> = ({ v, t }) => {
  const a = pop(t, n(v, "a")); const b = pop(t, n(v, "b")); const c = pop(t, n(v, "c"), 0.35);
  const room = (label: string, sub: string, p: number, premium: boolean) => (
    <div style={{ ...card, width: 420, padding: 26, transform: `translateY(${(1 - p) * 60}px) scale(${0.85 + 0.15 * p})`, opacity: Math.min(1, p * 1.5) }}>
      <div style={{ height: 150, borderRadius: 16, background: premium ? "linear-gradient(160deg, #F3E3B5, #D9B35E)" : "linear-gradient(160deg, #E6EEF0, #B8C9CF)", display: "flex", alignItems: "flex-end", justifyContent: "center", overflow: "hidden" }}>
        <svg width={260} height={130} viewBox="0 0 260 130">
          {premium ? <path d="M40 20 Q 60 70 40 130 M70 20 Q 90 70 70 130 M190 20 Q 170 70 190 130 M220 20 Q 200 70 220 130" fill="none" stroke={C.goldDark} strokeWidth={10} strokeLinecap="round" /> : <path d="M50 20 V130 M80 20 V130 M180 20 V130 M210 20 V130" stroke="#6E8790" strokeWidth={10} strokeLinecap="round" />}
          <rect x={95} y={70} width={70} height={60} rx={8} fill={premium ? "#9C7428" : "#6E8790"} />
        </svg>
      </div>
      <div style={{ ...txt(38), marginTop: 16 }}>{label}</div>
      <div style={{ ...txt(30, premium ? C.goldDark : "#557", 800), marginTop: 6 }}>{sub}</div>
    </div>
  );
  return (
    <div style={{ position: "absolute", left: 70, top: ZONE_TOP - 20, width: 940, display: "flex", justifyContent: "space-between" }}>
      {room("RUANG TAMU", "★ Kain premium", a, true)}
      {room("BILIK", "Kain ikut bajet", b, false)}
      <div style={{ position: "absolute", left: 330, top: 275, transform: `scale(${c}) rotate(-8deg)`, opacity: Math.min(1, c * 1.5), background: goldGrad, borderRadius: 18, padding: "12px 26px", boxShadow: "0 12px 30px rgba(0,0,0,0.35)", ...txt(42) }}>ADJUST ✓</div>
    </div>
  );
};

const Measure: React.FC<{ v: VizEv; t: number }> = ({ v, t }) => {
  const p = pop(t, v.s, 0.35);
  const st = n(v, "stamp");
  const tape = draw(t, st - 2.4, 1.6);
  const s = pop(t, st, 0.35);
  const wob = Math.sin((t - v.s) * 6) * 4 * (1 - rise(t, st - 2.5, 0.5));
  return (
    <div style={{ position: "absolute", left: 80, top: ZONE_TOP, width: 920, height: 360 }}>
      <div style={{ position: "absolute", left: 0, top: 10, transform: `rotate(${-8 + wob}deg) scale(${p})`, opacity: Math.min(1, p * 1.5) }}>
        <svg width={360} height={220} viewBox="0 0 360 220">
          <path d="M20 110 L90 20 H340 V200 H90 Z" fill="#fff" stroke={C.goldDark} strokeWidth={8} strokeLinejoin="round" />
          <circle cx={92} cy={110} r={18} fill="none" stroke={C.goldDark} strokeWidth={8} />
          <text x={215} y={140} textAnchor="middle" fontFamily="Montserrat" fontWeight={900} fontSize={96} fill={C.ink}>?</text>
        </svg>
        <div style={{ ...txt(34, "#fff", 900), textShadow: "0 3px 10px rgba(0,0,0,0.6)", marginTop: 6, marginLeft: 60 }}>HARGA</div>
      </div>
      <div style={{ position: "absolute", left: 400, top: 120, width: 520 * tape, height: 90, background: "#F6D96B", border: `5px solid ${C.ink}`, borderRadius: 8, overflow: "hidden", boxShadow: "0 10px 24px rgba(0,0,0,0.3)" }}>
        <div style={{ position: "absolute", inset: 0, backgroundImage: `repeating-linear-gradient(90deg, ${C.ink} 0 3px, transparent 3px 26px)`, backgroundSize: "26px 40px", backgroundRepeat: "repeat-x" }} />
      </div>
      <div style={{ position: "absolute", left: 470, top: 220, transform: `scale(${2 - s}) rotate(-6deg)`, opacity: interpolate(t, [st, st + 0.08], [0, 1], clamp), background: C.emerald, border: `5px solid ${C.gold}`, borderRadius: 16, padding: "10px 24px", ...txt(46, "#fff") }}>UKUR DULU ✓</div>
    </div>
  );
};

// ---------------------------------------------------------------- Q2
const Window: React.FC<{ v: VizEv; t: number }> = ({ v, t }) => {
  const p = pop(t, v.s, 0.35);
  const pl = rise(t, n(v, "pad")); const pr = rise(t, n(v, "pad2"));
  const ex = rise(t, n(v, "ex")); const sum = rise(t, n(v, "sum")); const res = pop(t, n(v, "res"), 0.4);
  const X = 300, Y = 70, W = 340, H = 260, E = 70;
  return (
    <div style={{ ...card, position: "absolute", left: 70, top: ZONE_TOP - 30, width: 940, height: 430, transform: `scale(${p})`, opacity: Math.min(1, p * 1.5) }}>
      <svg width={940} height={430} viewBox="0 0 940 430">
        {/* curtain panels covering the extended width */}
        <rect x={X - E * pl} y={Y - 20} width={W / 2 + E * pl} height={H + 40} fill="rgba(217,179,94,0.35)" />
        <rect x={X + W / 2} y={Y - 20} width={W / 2 + E * pr} height={H + 40} fill="rgba(217,179,94,0.35)" />
        <rect x={X} y={Y} width={W} height={H} fill="#DCEBF2" stroke={C.ink} strokeWidth={8} />
        <path d={`M${X + W / 2} ${Y} V${Y + H} M${X} ${Y + H / 2} H${X + W}`} stroke={C.ink} strokeWidth={5} />
        <text x={X + W / 2} y={Y + H / 2 - 16} textAnchor="middle" fontFamily="Montserrat" fontWeight={900} fontSize={38} fill={C.ink} opacity={ex}>48" (4 kaki)</text>
        {pl > 0.01 && <g opacity={pl}><path d={`M${X} ${Y + H + 40} H${X - E}`} stroke={C.goldDark} strokeWidth={6} /><text x={X - E / 2} y={Y + H + 80} textAnchor="middle" fontFamily="Montserrat" fontWeight={900} fontSize={34} fill={C.goldDark}>+5"</text></g>}
        {pr > 0.01 && <g opacity={pr}><path d={`M${X + W} ${Y + H + 40} H${X + W + E}`} stroke={C.goldDark} strokeWidth={6} /><text x={X + W + E / 2} y={Y + H + 80} textAnchor="middle" fontFamily="Montserrat" fontWeight={900} fontSize={34} fill={C.goldDark}>+5"</text></g>}
        <text x={30} y={60} fontFamily="Montserrat" fontWeight={800} fontSize={32} fill={C.ink} opacity={sum * (1 - res)}>48 + 5 + 5</text>
        {res > 0.01 && <g opacity={Math.min(1, res * 1.5)}>
          <path d={`M${X - E} ${Y - 40} H${X + W + E}`} stroke={C.ink} strokeWidth={6} />
          <path d={`M${X - E} ${Y - 54} V${Y - 26} M${X + W + E} ${Y - 54} V${Y - 26}`} stroke={C.ink} strokeWidth={6} />
          <rect x={X + W / 2 - 100} y={Y - 74} width={200} height={64} rx={14} fill={C.emerald} />
          <text x={X + W / 2} y={Y - 28} textAnchor="middle" fontFamily="Montserrat" fontWeight={900} fontSize={42} fill={C.goldLight}>58"</text>
        </g>}
        <text x={30} y={410} fontFamily="Montserrat" fontWeight={800} fontSize={28} fill="#666">LEBAR</text>
      </svg>
    </div>
  );
};

const Height: React.FC<{ v: VizEv; t: number }> = ({ v, t }) => {
  const p = pop(t, v.s, 0.35);
  const five = rise(t, n(v, "five")); const ceil = draw(t, n(v, "ceil"), 0.8);
  const X = 360, Y = 120, W = 220, H = 170, FLOOR = 400, CEIL = 30;
  return (
    <div style={{ ...card, position: "absolute", left: 70, top: ZONE_TOP - 40, width: 940, height: 440, transform: `scale(${p})`, opacity: Math.min(1, p * 1.5) }}>
      <svg width={940} height={440} viewBox="0 0 940 440">
        <path d={`M40 ${CEIL} H900`} stroke="#999" strokeWidth={5} strokeDasharray="14 10" />
        <text x={50} y={CEIL + 34} fontFamily="Montserrat" fontWeight={800} fontSize={26} fill="#777">SILING</text>
        <path d={`M40 ${FLOOR} H900`} stroke={C.ink} strokeWidth={7} />
        <text x={50} y={FLOOR - 12} fontFamily="Montserrat" fontWeight={800} fontSize={26} fill="#777">LANTAI</text>
        {/* ceiling-to-floor curtain */}
        <rect x={X - 70} y={CEIL} width={W + 140} height={(FLOOR - CEIL) * ceil} fill="rgba(15,61,48,0.85)" />
        <rect x={X} y={Y} width={W} height={H} fill="#DCEBF2" stroke={C.ink} strokeWidth={7} opacity={1 - 0.75 * ceil} />
        {five > 0.01 && ceil < 0.05 && <g opacity={five}>
          <rect x={X - 40} y={Y - 30} width={W + 80} height={H + 30 + 50} fill="rgba(217,179,94,0.35)" />
          <path d={`M${X + W + 60} ${Y + H} V${Y + H + 50}`} stroke={C.goldDark} strokeWidth={6} />
          <text x={X + W + 80} y={Y + H + 38} fontFamily="Montserrat" fontWeight={900} fontSize={34} fill={C.goldDark}>+5"</text>
        </g>}
        {ceil > 0.9 && <g><path d={`M820 ${CEIL + 10} V${FLOOR - 10}`} stroke={C.goldDark} strokeWidth={6} /><text x={760} y={(CEIL + FLOOR) / 2} fontFamily="Montserrat" fontWeight={900} fontSize={30} fill={C.goldDark} transform={`rotate(-90 760 ${(CEIL + FLOOR) / 2})`} textAnchor="middle">LEBIH CANTIK</text></g>}
      </svg>
    </div>
  );
};

// ---------------------------------------------------------------- Q3
const Tiers: React.FC<{ v: VizEv; t: number }> = ({ v, t }) => {
  const items: [string, string][] = [["BASIC", "t1"], ["STANDARD", "t2"], ["PREMIUM", "t3"]];
  const fl = rise(t, n(v, "flowy"));
  return (
    <div style={{ position: "absolute", left: 70, top: ZONE_TOP - 10, width: 940, display: "flex", justifyContent: "space-between" }}>
      {items.map(([l, k], i) => {
        const p = pop(t, n(v, k));
        const prem = i === 2;
        const wave = prem ? fl : 0;
        return (
          <div key={l} style={{ ...card, width: 290, padding: 18, transform: `translateY(${(1 - p) * 60}px) scale(${(0.85 + 0.15 * p) * (prem ? 1 + 0.06 * fl : 1)})`, opacity: Math.min(1, p * 1.5), border: prem ? `5px solid ${C.gold}` : "5px solid transparent" }}>
            <svg width={254} height={210} viewBox="0 0 254 210">
              {Array.from({ length: 6 }, (_, j) => {
                const x = 20 + j * 40;
                const w = Math.sin(t * 3 + j) * 12 * wave;
                return <path key={j} d={`M${x} 0 Q ${x + 18 + w} 105 ${x + w * 0.5} 210`} fill="none" stroke={prem ? C.goldDark : i === 1 ? "#6E8790" : "#9AA3AE"} strokeWidth={22} strokeLinecap="round" />;
              })}
            </svg>
            <div style={{ ...txt(38), textAlign: "center", marginTop: 8 }}>{l}</div>
          </div>
        );
      })}
    </div>
  );
};

const Block: React.FC<{ v: VizEv; t: number }> = ({ v, t }) => {
  const bars: [string, number, string][] = [["BASIC", 60, "b60"], ["PREMIUM", 80, "b80"], ["", 100, "b100"]];
  const dark = rise(t, n(v, "dark"), 0.6) * (1 - rise(t, n(v, "back"), 0.4));
  const back = rise(t, n(v, "back"));
  const p = pop(t, v.s, 0.35);
  return (
    <div style={{ ...card, position: "absolute", left: 70, top: ZONE_TOP - 20, width: 940, padding: "30px 40px", transform: `scale(${p})`, opacity: Math.min(1, p * 1.5) }}>
      <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 18 }}>
        <svg width={64} height={64} viewBox="0 0 48 48"><circle cx={24} cy={24} r={9} fill="#F6C343" stroke={C.ink} strokeWidth={2.5} />{Array.from({ length: 8 }, (_, i) => <line key={i} x1={24} y1={4} x2={24} y2={10} stroke="#E8A33A" strokeWidth={3.5} strokeLinecap="round" transform={`rotate(${i * 45 + t * 30} 24 24)`} />)}</svg>
        <div style={txt(36)}>SEKAT CAHAYA</div>
      </div>
      {bars.map(([l, pct, k]) => {
        const g = interpolate(t, [n(v, k), n(v, k) + 0.6], [0, pct], { easing: Easing.out(Easing.cubic), ...clamp });
        const hl = pct === 80 && back > 0.5;
        return (
          <div key={pct} style={{ display: "flex", alignItems: "center", gap: 18, marginTop: 14, opacity: t >= n(v, k) ? 1 : 0.25 }}>
            <div style={{ width: 200, ...txt(30, C.ink, 800) }}>{l || "ADA JUGA"}</div>
            <div style={{ flex: 1, height: 46, borderRadius: 23, background: "#ECE7DA", overflow: "hidden", border: hl ? `4px solid ${C.gold}` : "4px solid transparent" }}>
              <div style={{ width: `${g}%`, height: "100%", background: pct === 100 ? "#1C2B26" : goldGrad }} />
            </div>
            <div style={{ width: 110, textAlign: "right", ...txt(38) }}>{Math.round(g)}%</div>
          </div>
        );
      })}
      <div style={{ position: "absolute", inset: 0, borderRadius: 26, background: "#0B1612", opacity: dark * 0.85, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ ...txt(54, "#fff"), opacity: dark }}>GELAP TOTAL</div>
      </div>
    </div>
  );
};

// ---------------------------------------------------------------- Q4
const Calendar: React.FC<{ v: VizEv; t: number }> = ({ v, t }) => {
  const p = pop(t, v.s, 0.35);
  const two = interpolate(t, [n(v, "two"), n(v, "two") + 1.2], [1, 14], clamp);
  const q = interpolate(t, [n(v, "queue") + 0.6, n(v, "queue") + 1.6], [14, 21], clamp);
  const mo = interpolate(t, [n(v, "month"), n(v, "month") + 1.0], [21, 30], clamp);
  const fill = t >= n(v, "month") ? mo : t >= n(v, "queue") ? q : two;
  const start = pop(t, n(v, "start"));
  const tickets = pop(t, n(v, "queue"));
  return (
    <div style={{ ...card, position: "absolute", left: 90, top: ZONE_TOP - 30, width: 900, padding: 24, transform: `scale(${p})`, opacity: Math.min(1, p * 1.5) }}>
      <div style={{ background: C.emerald, borderRadius: 14, padding: "10px 0", textAlign: "center", ...txt(34, C.goldLight) }}>TEMPOH SIAP</div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(10, 1fr)", gap: 8, marginTop: 16 }}>
        {Array.from({ length: 30 }, (_, i) => {
          const d = i + 1;
          const on = d <= fill;
          const late = d > 14;
          return (
            <div key={d} style={{ height: 66, borderRadius: 10, background: on ? (late ? "rgba(217,179,94,0.45)" : goldGrad) : "#EFEBE1", border: d === 1 ? `5px solid ${start > 0.5 ? C.emerald : "transparent"}` : "none", display: "flex", alignItems: "center", justifyContent: "center", ...txt(24, on ? C.ink : "#AAA", 800) }}>
              {d}
            </div>
          );
        })}
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 14, ...txt(26, "#555", 800) }}>
        <span>HARI 1</span><span style={{ opacity: t >= n(v, "two") ? 1 : 0.3 }}>± 2 MINGGU</span><span style={{ opacity: t >= n(v, "month") ? 1 : 0.3 }}>± SEBULAN</span>
      </div>
      <div style={{ position: "absolute", right: -20, top: -40, transform: `scale(${tickets}) rotate(8deg)`, opacity: Math.min(1, tickets * 1.5) }}>
        {[0, 1, 2].map((i) => <div key={i} style={{ position: "absolute", right: i * 16, top: i * 14, width: 150, height: 90, borderRadius: 12, background: "#fff", border: `4px solid ${C.goldDark}`, boxShadow: "0 8px 18px rgba(0,0,0,0.25)" }} />)}
        <div style={{ position: "absolute", right: 0, top: 112, width: 190, textAlign: "center", ...txt(24, "#fff", 900), textShadow: "0 2px 8px rgba(0,0,0,0.6)" }}>TEMPAHAN</div>
      </div>
    </div>
  );
};

// ---------------------------------------------------------------- Q5
const Palette: React.FC<{ v: VizEv; t: number }> = ({ v, t }) => {
  const p = pop(t, v.s, 0.35);
  const sofa = pop(t, n(v, "sofa")); const mini = pop(t, n(v, "mini")); const col = rise(t, n(v, "color"));
  const dots = ["#E9E4DA", "#B9A68A", "#5E6B67", "#2E3A36"];
  return (
    <div style={{ ...card, position: "absolute", left: 90, top: ZONE_TOP - 30, width: 900, height: 420, overflow: "hidden", transform: `scale(${p})`, opacity: Math.min(1, p * 1.5) }}>
      <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg, #EDE9E1 0 70%, #C9B79C 70% 100%)" }} />
      <svg width={900} height={420} style={{ position: "absolute", left: 0, top: 0 }}>
        <g transform={`translate(260 ${150 + (1 - sofa) * 120})`} opacity={sofa}>
          <rect x={0} y={60} width={380} height={110} rx={26} fill="#5E6B67" />
          <rect x={30} y={10} width={320} height={80} rx={22} fill="#6F7D78" />
          <rect x={-20} y={70} width={60} height={110} rx={20} fill="#4E5A56" />
          <rect x={340} y={70} width={60} height={110} rx={20} fill="#4E5A56" />
        </g>
        <rect x={60} y={40} width={120} height={160} fill="#B9A68A" opacity={sofa} />
      </svg>
      <div style={{ position: "absolute", left: 30, top: 24, transform: `scale(${mini}) rotate(-4deg)`, opacity: Math.min(1, mini * 1.5), background: C.emerald, borderRadius: 12, padding: "8px 20px", ...txt(32, C.goldLight) }}>MINIMALIS</div>
      <div style={{ position: "absolute", right: 30, top: 30, display: "flex", gap: 12 }}>
        {dots.map((d, i) => <div key={d} style={{ width: 70, height: 70, borderRadius: 35, background: d, border: "5px solid #fff", boxShadow: "0 6px 14px rgba(0,0,0,0.25)", transform: `scale(${interpolate(col, [i * 0.2, i * 0.2 + 0.4], [0, 1], clamp)})` }} />)}
      </div>
    </div>
  );
};

const Checklist: React.FC<{ v: VizEv; t: number }> = ({ v, t }) => {
  const items = v.items as [string, number][];
  const match = pop(t, n(v, "match"), 0.35);
  const guess = pop(t, n(v, "guess"));
  const no = draw(t, n(v, "no"), 0.35);
  const su = pop(t, n(v, "suasana"), 0.35);
  const showGuess = t >= n(v, "guess");
  return (
    <div style={{ ...card, position: "absolute", left: 90, top: ZONE_TOP - 30, width: 900, height: 420, padding: "30px 40px" }}>
      {!showGuess ? (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 22 }}>
            {items.map(([l, at]) => {
              const p = pop(t, at);
              return (
                <div key={l} style={{ display: "flex", alignItems: "center", gap: 18, opacity: 0.35 + 0.65 * Math.min(1, p) }}>
                  <Check p={p} size={70} /><div style={txt(44)}>{l}</div>
                </div>
              );
            })}
          </div>
          <div style={{ marginTop: 40, display: "flex", justifyContent: "center", transform: `scale(${match})`, opacity: Math.min(1, match * 1.5) }}>
            <div style={{ background: goldGrad, borderRadius: 18, padding: "12px 40px", ...txt(56) }}>✓ MATCH</div>
          </div>
        </>
      ) : (
        <div style={{ position: "relative", height: 360 }}>
          <div style={{ display: "flex", justifyContent: "center", gap: 60, transform: `scale(${guess})`, opacity: su > 0.5 ? 0.25 : 1 }}>
            {[["BIRU", "#3D6FA8"], ["NUDE", "#D9B9A0"]].map(([l, c]) => (
              <div key={l} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12 }}>
                <div style={{ width: 170, height: 170, borderRadius: 24, background: c, border: "6px solid #fff", boxShadow: "0 8px 20px rgba(0,0,0,0.25)", display: "flex", alignItems: "center", justifyContent: "center", ...txt(90, "#fff") }}>?</div>
                <div style={txt(36)}>{l}</div>
              </div>
            ))}
          </div>
          <svg width={820} height={260} style={{ position: "absolute", left: 0, top: 0 }}>
            <path d="M230 20 L590 240 M590 20 L230 240" stroke="#C0392B" strokeWidth={14} strokeLinecap="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - no} opacity={su > 0.5 ? 0.25 : 1} />
          </svg>
          <div style={{ position: "absolute", left: 0, right: 0, top: 120, display: "flex", justifyContent: "center", transform: `scale(${su})`, opacity: Math.min(1, su * 1.5) }}>
            <div style={{ display: "flex", alignItems: "center", gap: 20, background: C.emerald, border: `5px solid ${C.gold}`, borderRadius: 22, padding: "16px 30px" }}>
              <svg width={80} height={80} viewBox="0 0 48 48"><g fill="none" stroke={C.goldLight} strokeWidth={3.5} strokeLinecap="round" strokeLinejoin="round"><path d="M6 22L24 7l18 15M11 18v22h26V18" /><circle cx={30} cy={30} r={6} /><path d="M34.5 34.5L40 40" /></g></svg>
              <div style={txt(44, "#fff")}>TENGOK RUMAH DULU</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const MAP: Record<string, React.FC<{ v: VizEv; t: number }>> = { budget: Budget, rooms: Rooms, measure: Measure, window: Window, height: Height, tiers: Tiers, block: Block, calendar: Calendar, palette: Palette, checklist: Checklist };

export const VizLayer: React.FC<{ viz: VizEv[]; t: number }> = ({ viz, t }) => {
  const v = viz.find((x) => t >= x.s - 0.05 && t < x.e + 0.25);
  if (!v) return null;
  const Comp = MAP[v.type];
  const out = interpolate(t, [v.e, v.e + 0.25], [1, 0], clamp);
  return <div style={{ position: "absolute", inset: 0, opacity: out }}>{Comp ? <Comp v={v} t={t} /> : null}</div>;
};

export const Logo: React.FC<{ size: number }> = ({ size }) => (
  <Img src={staticFile("img/logo.png")} style={{ width: size, height: size, WebkitMaskImage: "radial-gradient(circle at 50% 48%, #000 52%, transparent 70%)" }} />
);
export { goldText };
