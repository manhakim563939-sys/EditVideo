import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import tl from "./timeline.json";
import { C, F } from "./theme";

const BAND_BOTTOM = 1360; // cards sit above the caption block

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const popIn = (t: number, s: number, d = 0.28) =>
  interpolate(t, [s, s + d], [0, 1], { easing: Easing.out(Easing.back(1.8)), ...clamp });
const fadeOut = (t: number, e: number, d = 0.2) => interpolate(t, [e - d, e], [1, 0], clamp);

type Card = (typeof tl.cards)[number];

const Pill: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div
    style={{
      background: C.linen,
      color: C.plum,
      borderRadius: 26,
      padding: "18px 34px",
      boxShadow: "0 14px 40px rgba(0,0,0,0.28)",
      fontFamily: F.body,
      fontWeight: 800,
      ...style,
    }}
  >
    {children}
  </div>
);

const Icon: React.FC<{ name: string; size?: number; color?: string }> = ({ name, size = 70, color = C.plum }) => {
  const p = { fill: "none", stroke: color, strokeWidth: 5, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };
  return (
    <svg width={size} height={size} viewBox="0 0 64 64">
      {name === "ruler" && (
        <g {...p}>
          <rect x="6" y="22" width="52" height="20" rx="3" />
          <path d="M16 22v8M26 22v12M36 22v8M46 22v12" />
        </g>
      )}
      {name === "needle" && (
        <g {...p}>
          <path d="M12 52L50 14" />
          <ellipse cx="47" cy="17" rx="3" ry="6" transform="rotate(45 47 17)" />
          <path d="M44 20c-14 4-22 14-18 22s14 2 20 10" />
        </g>
      )}
      {name === "hook" && (
        <g {...p}>
          <path d="M6 12h52" />
          <path d="M14 12v4c0 12-4 30-6 38h14c-2-10-2-26 0-38M50 12v4c0 12 4 30 6 38H42c2-10 2-26 0-38" />
        </g>
      )}
      {name === "x" && (
        <g {...p} stroke={C.white} strokeWidth={7}>
          <path d="M20 20l24 24M44 20L20 44" />
        </g>
      )}
      {name === "pin" && (
        <g>
          <path d="M32 4c-11 0-20 9-20 20 0 15 20 36 20 36s20-21 20-36C52 13 43 4 32 4z" fill={color} />
          <circle cx="32" cy="24" r="8" fill={C.linen} />
        </g>
      )}
      {name === "chat" && (
        <g>
          <path d="M32 6C18 6 7 16 7 29c0 5 2 10 5 13l-3 12 12-4c3 2 7 3 11 3 14 0 25-10 25-23S46 6 32 6z" fill={C.white} />
          <path d="M22 24c1 6 8 13 15 15l4-4 6 3c-1 4-4 6-8 5-10-2-19-11-21-20-1-4 1-7 5-8l3 6z" fill={C.wa} />
        </g>
      )}
    </svg>
  );
};

const Hook: React.FC<{ c: Card; t: number }> = ({ c, t }) => {
  const a = popIn(t, c.s);
  const b = popIn(t, c.s + 0.45);
  return (
    <div style={{ position: "absolute", top: 980, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center", opacity: fadeOut(t, c.e) }}>
      <Pill style={{ fontFamily: F.display, fontWeight: 900, fontStyle: "italic", fontSize: 92, padding: "6px 40px 16px", transform: `rotate(-3deg) scale(${a})` }}>
        {c.title}
      </Pill>
      <div style={{ marginTop: 18, transform: `rotate(2deg) scale(${b})` }}>
        <Pill style={{ background: C.plum, color: C.linen, fontSize: 54 }}>{c.sub}</Pill>
      </div>
    </div>
  );
};

const FadeSwatches: React.FC<{ c: Card; t: number }> = ({ c, t }) => {
  const a = popIn(t, c.s);
  // colours drain as she says "pudar, nampak kusam"
  const drain = interpolate(t, [4.4, 5.4], [1, 0.12], clamp);
  const cols = ["#3E6E8E", "#B8443A", "#D9A441", "#5E8C6A"];
  return (
    <div style={{ position: "absolute", top: 1090, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center", opacity: fadeOut(t, c.e), transform: `scale(${a})` }}>
      <div style={{ display: "flex", gap: 14, filter: `saturate(${drain}) brightness(${1 + (1 - drain) * 0.25})` }}>
        {cols.map((col, i) => (
          <div key={i} style={{ width: 92, height: 120, borderRadius: 14, background: `repeating-linear-gradient(90deg, rgba(0,0,0,0.12) 0 10px, rgba(255,255,255,0.08) 10px 20px), ${col}`, boxShadow: "0 10px 26px rgba(0,0,0,0.3)" }} />
        ))}
      </div>
      <Pill style={{ marginTop: 18, fontSize: 46, padding: "10px 28px" }}>{c.title}</Pill>
    </div>
  );
};

const Refresh: React.FC<{ c: Card; t: number }> = ({ c, t }) => {
  const s0 = c.s + 0.35; // after the curtain opens
  const a = popIn(t, s0, 0.35);
  const sparkle = (i: number) => {
    const ang = (i / 6) * Math.PI * 2;
    const d = interpolate(t, [s0, s0 + 0.6], [40, 230], { easing: Easing.out(Easing.cubic), ...clamp });
    const o = interpolate(t, [s0, s0 + 0.2, s0 + 0.8], [0, 1, 0], clamp);
    return (
      <div key={i} style={{ position: "absolute", left: "50%", top: "50%", width: 18, height: 18, background: C.gold, borderRadius: 4, opacity: o, transform: `translate(${Math.cos(ang) * d - 9}px, ${Math.sin(ang) * d * 0.6 - 9}px) rotate(45deg)` }} />
    );
  };
  return (
    <div style={{ position: "absolute", top: 1060, left: 0, right: 0, height: 220, display: "flex", justifyContent: "center", alignItems: "center", opacity: fadeOut(t, c.e) }}>
      {[0, 1, 2, 3, 4, 5].map(sparkle)}
      <div style={{ fontFamily: F.display, fontWeight: 900, fontStyle: "italic", fontSize: 150, color: C.gold, transform: `scale(${a}) rotate(-4deg)`, textShadow: "0 8px 30px rgba(0,0,0,0.45)", WebkitTextStroke: "10px rgba(43,34,48,0.85)", paintOrder: "stroke fill" }}>
        {c.title}
      </div>
    </div>
  );
};

const Brand: React.FC<{ c: Card; t: number }> = ({ c, t }) => {
  const a = popIn(t, c.s);
  return (
    <div style={{ position: "absolute", top: 1130, left: 0, right: 0, display: "flex", justifyContent: "center", opacity: fadeOut(t, c.e), transform: `translateY(${(1 - a) * 40}px) scale(${0.8 + 0.2 * a})` }}>
      <Pill style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "16px 44px", borderBottom: `8px solid ${C.terracotta}` }}>
        <div style={{ fontFamily: F.display, fontWeight: 800, fontSize: 80, lineHeight: 1 }}>{c.title}</div>
        <div style={{ fontSize: 34, fontWeight: 700, color: C.terracotta, marginTop: 8 }}>{c.sub}</div>
      </Pill>
    </div>
  );
};

const NoChips: React.FC<{ c: Card; t: number }> = ({ c, t }) => (
  <div style={{ position: "absolute", top: 1010, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center", gap: 18, opacity: fadeOut(t, c.e) }}>
    <div style={{ fontFamily: F.body, fontWeight: 800, fontSize: 40, color: C.white, letterSpacing: 3, opacity: popIn(t, c.s), textShadow: "0 3px 10px rgba(0,0,0,0.6)" }}>TAK PERLU</div>
    {(c.items as [string, number][]).map(([label, at], i) => {
      const a = popIn(t, at);
      const strike = interpolate(t, [at + 0.3, at + 0.6], [0, 100], clamp);
      return (
        <div key={i} style={{ transform: `translateX(${(1 - a) * (i ? 120 : -120)}px)`, opacity: Math.min(1, a * 1.5) }}>
          <Pill style={{ display: "flex", alignItems: "center", gap: 20, fontSize: 52, padding: "12px 34px 12px 14px" }}>
            <div style={{ width: 66, height: 66, borderRadius: 33, background: C.terracotta, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Icon name="x" size={52} />
            </div>
            <span style={{ position: "relative" }}>
              {label}
              <span style={{ position: "absolute", left: 0, top: "54%", height: 6, width: `${strike}%`, background: C.terracotta, borderRadius: 3 }} />
            </span>
          </Pill>
        </div>
      );
    })}
  </div>
);

const Badge: React.FC<{ c: Card; t: number }> = ({ c, t }) => {
  const a = popIn(t, c.s, 0.32);
  return (
    <div style={{ position: "absolute", top: 1010, left: 0, right: 0, display: "flex", justifyContent: "center", opacity: fadeOut(t, c.e) }}>
      <div style={{ width: 330, height: 330, borderRadius: 165, background: C.terracotta, border: `10px solid ${C.linen}`, boxShadow: "0 18px 50px rgba(0,0,0,0.35)", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", transform: `scale(${a}) rotate(${(1 - a) * -25 - 6}deg)` }}>
        <div style={{ fontFamily: F.body, fontWeight: 800, fontSize: 44, color: C.linen, letterSpacing: 2 }}>KHIDMAT</div>
        <div style={{ fontFamily: F.display, fontWeight: 900, fontStyle: "italic", fontSize: 130, color: C.white, lineHeight: 1 }}>A–Z</div>
      </div>
    </div>
  );
};

// Real customer feedback supplied by the client (text copied from the WhatsApp screenshot, names/numbers left out).
const Testimonial: React.FC<{ c: Card; t: number }> = ({ c, t }) => {
  const a = popIn(t, c.s, 0.32);
  const b = popIn(t, c.s + 0.12);
  return (
    <div style={{ position: "absolute", top: 930, left: 70, right: 70, display: "flex", flexDirection: "column", alignItems: "flex-start", opacity: fadeOut(t, c.e) }}>
      <div style={{ transform: `scale(${b}) rotate(-3deg)`, transformOrigin: "0% 100%", marginLeft: 20, marginBottom: -14, zIndex: 2 }}>
        <Pill style={{ background: C.terracotta, color: C.white, fontSize: 40, padding: "8px 24px" }}>{c.label}</Pill>
      </div>
      <div style={{ position: "relative", background: C.white, borderRadius: "8px 34px 34px 34px", padding: "34px 36px 22px", boxShadow: "0 18px 50px rgba(0,0,0,0.35)", transform: `translateY(${(1 - a) * 50}px) scale(${0.9 + 0.1 * a})`, transformOrigin: "0% 0%", opacity: Math.min(1, a * 1.5) }}>
        <div style={{ position: "absolute", left: -18, top: 0, width: 0, height: 0, borderTop: `26px solid ${C.white}`, borderLeft: "20px solid transparent" }} />
        <div style={{ fontFamily: `${F.body}, 'Noto Color Emoji'`, fontWeight: 700, fontSize: 44, lineHeight: 1.3, color: "#1F1B1D" }}>{c.quote}</div>
        <div style={{ marginTop: 12, fontFamily: F.body, fontWeight: 700, fontSize: 28, color: C.sage }}>{c.who}</div>
      </div>
    </div>
  );
};

const Steps: React.FC<{ c: Card; t: number }> = ({ c, t }) => {
  const items = c.items as [string, number, string][];
  const a = popIn(t, c.s - 0.05);
  const prog = interpolate(t, [items[0][1], items[2][1]], [0, 1], clamp);
  return (
    <div style={{ position: "absolute", top: 1080, left: 50, right: 50, opacity: fadeOut(t, c.e), transform: `translateY(${(1 - a) * 40}px)` }}>
      <div style={{ position: "absolute", top: 72, left: 135, right: 135, height: 10, borderRadius: 5, background: "rgba(247,240,230,0.5)" }}>
        <div style={{ height: "100%", width: `${prog * 100}%`, background: C.terracotta, borderRadius: 5 }} />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        {items.map(([label, at, icon], i) => {
          const on = popIn(t, at);
          const active = t >= at && (i === 2 || t < items[i + 1][1]);
          return (
            <div key={i} style={{ width: 270, display: "flex", flexDirection: "column", alignItems: "center" }}>
              <div style={{ width: 154, height: 154, borderRadius: 77, background: on > 0.01 ? C.linen : "rgba(247,240,230,0.55)", border: `8px solid ${on > 0.01 ? C.terracotta : "transparent"}`, display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${0.85 + 0.15 * on + (active ? 0.08 : 0)})`, boxShadow: "0 12px 30px rgba(0,0,0,0.3)" }}>
                <Icon name={icon} size={86} color={on > 0.01 ? C.plum : "rgba(43,34,48,0.45)"} />
              </div>
              <div style={{ marginTop: 14, fontFamily: F.body, fontWeight: 800, fontSize: 48, whiteSpace: "nowrap", color: C.white, opacity: 0.45 + 0.55 * on, WebkitTextStroke: "10px rgba(32,24,36,0.9)", paintOrder: "stroke fill" }}>
                {i + 1}. {label}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

const Swatches: React.FC<{ c: Card; t: number }> = ({ c, t }) => {
  const cols = ["#8FB9B5", "#6B4A3A", "#B5283A", "#E9DCC6", "#9AA3AE", "#C8664B", "#5E7D63"];
  return (
    <div style={{ position: "absolute", top: 1010, left: 0, right: 0, height: 340, opacity: fadeOut(t, c.e) }}>
      {cols.map((col, i) => {
        const a = popIn(t, c.s + 0.08 * i, 0.35);
        const ang = (i - 3) * 9 * a;
        return (
          <div key={i} style={{ position: "absolute", left: 540 - 60, top: 20, width: 120, height: 250, borderRadius: 16, transformOrigin: "50% 120%", transform: `rotate(${ang}deg) translateY(${(1 - a) * 80}px)`, opacity: Math.min(1, a * 2), background: `repeating-linear-gradient(90deg, rgba(0,0,0,0.14) 0 12px, rgba(255,255,255,0.10) 12px 24px), ${col}`, boxShadow: "0 10px 26px rgba(0,0,0,0.35)" }} />
        );
      })}
      <div style={{ position: "absolute", top: 230, left: 0, right: 0, display: "flex", justifyContent: "center", transform: `scale(${popIn(t, 32.0)})` }}>
        <Pill style={{ fontFamily: F.display, fontWeight: 900, fontStyle: "italic", fontSize: 70, padding: "6px 36px 14px" }}>{c.title}</Pill>
      </div>
    </div>
  );
};

const Pin: React.FC<{ c: Card; t: number }> = ({ c, t }) => {
  const drop = interpolate(t, [c.s, c.s + 0.35], [-120, 0], { easing: Easing.bounce, ...clamp });
  const a = popIn(t, c.s + 0.15);
  return (
    <div style={{ position: "absolute", top: 1100, left: 0, right: 0, display: "flex", justifyContent: "center", alignItems: "center", gap: 10, opacity: fadeOut(t, c.e) }}>
      <div style={{ transform: `translateY(${drop}px)`, opacity: interpolate(t, [c.s, c.s + 0.1], [0, 1], clamp) }}>
        <Icon name="pin" size={130} color={C.terracotta} />
      </div>
      <div style={{ transform: `scale(${a})`, transformOrigin: "0% 50%" }}>
        <Pill style={{ fontSize: 62 }}>{c.title}</Pill>
      </div>
    </div>
  );
};

const Bumi: React.FC<{ c: Card; t: number }> = ({ c, t }) => {
  const a = popIn(t, c.s);
  const b = popIn(t, 40.43);
  return (
    <div style={{ position: "absolute", top: 1040, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center", gap: 18, opacity: fadeOut(t, c.e) }}>
      <div style={{ transform: `scale(${a}) rotate(-2deg)` }}>
        <Pill style={{ background: C.sage, color: C.white, fontSize: 64, padding: "14px 40px", border: `6px solid ${C.linen}` }}>{c.title}</Pill>
      </div>
      <div style={{ transform: `scale(${b})`, display: "flex", alignItems: "center", gap: 6 }}>
        <Icon name="pin" size={70} color={C.terracotta} />
        <Pill style={{ fontSize: 44, padding: "12px 28px" }}>{c.sub}</Pill>
      </div>
    </div>
  );
};

export const CtaButton: React.FC<{ t: number; s: number; label: string }> = ({ t, s, label }) => {
  const a = popIn(t, s);
  const bob = Math.sin((t - s) * 7) * 10;
  const pulse = 1 + 0.03 * Math.max(0, Math.sin((t - s) * 5));
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", transform: `scale(${a * pulse})` }}>
      <div style={{ display: "flex", alignItems: "center", gap: 18, background: C.wa, color: C.white, borderRadius: 60, padding: "20px 46px 20px 28px", boxShadow: "0 16px 40px rgba(0,0,0,0.35)", border: `5px solid ${C.white}`, fontFamily: F.body, fontWeight: 800, fontSize: 52 }}>
        <Icon name="chat" size={74} />
        {label}
      </div>
      <svg width="80" height="70" viewBox="0 0 80 70" style={{ marginTop: 10, transform: `translateY(${bob}px)` }}>
        <path d="M14 18l26 26 26-26" fill="none" stroke={C.white} strokeWidth="11" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </div>
  );
};

const Cta: React.FC<{ c: Card; t: number }> = ({ c, t }) => (
  <div style={{ position: "absolute", top: 1120, left: 0, right: 0, display: "flex", justifyContent: "center", opacity: fadeOut(t, c.e + 0.15, 0.15) }}>
    <CtaButton t={t} s={c.s} label={c.title ?? ""} />
  </div>
);

const MAP: Record<string, React.FC<{ c: Card; t: number }>> = {
  hook: Hook,
  fade: FadeSwatches,
  refresh: Refresh,
  brand: Brand,
  nochips: NoChips,
  badge: Badge,
  testimonial: Testimonial,
  steps: Steps,
  swatches: Swatches,
  pin: Pin,
  bumi: Bumi,
  cta: Cta,
};

export const Cards: React.FC = () => {
  const t = useCurrentFrame() / tl.fps;
  // latest card that has started wins, so a new card never waits on the previous one's fade
  const c = [...tl.cards].reverse().find((k) => t >= k.s && t < k.e + 0.15);
  if (!c) return null;
  const Comp = MAP[c.type];
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div style={{ position: "absolute", left: 0, right: 0, top: 0, height: BAND_BOTTOM }}>
        <Comp c={c} t={t} />
      </div>
    </AbsoluteFill>
  );
};
