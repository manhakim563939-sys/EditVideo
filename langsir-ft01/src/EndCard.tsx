import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import tl from "./timeline.json";
import { CtaButton } from "./Cards";
import { C, F } from "./theme";

// Holds the CTA on screen after the last line; all wording comes from the dialogue.
export const EndCard: React.FC = () => {
  const f = useCurrentFrame(); // relative to the end-card sequence
  const t = f / tl.fps;
  const a = interpolate(t, [0, 0.4], [0, 1], { easing: Easing.out(Easing.back(1.5)), extrapolateRight: "clamp" });
  const b = interpolate(t, [0.25, 0.6], [0, 1], { easing: Easing.out(Easing.cubic), extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const out = interpolate(t, [tl.endCardDur - 0.35, tl.endCardDur], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", opacity: out }}>
      <div style={{ background: C.linen, borderRadius: 40, padding: "56px 70px 50px", width: 860, display: "flex", flexDirection: "column", alignItems: "center", boxShadow: "0 30px 80px rgba(0,0,0,0.45)", transform: `scale(${0.85 + 0.15 * a})`, opacity: Math.min(1, a * 1.4) }}>
        <div style={{ fontFamily: F.body, fontWeight: 800, fontSize: 34, letterSpacing: 4, color: C.terracotta }}>KEDAI LANGSIR</div>
        <div style={{ fontFamily: F.display, fontWeight: 800, fontSize: 100, color: C.plum, lineHeight: 1.05, marginTop: 6, whiteSpace: "nowrap" }}>Aimi Curtain</div>
        <div style={{ width: 120, height: 8, borderRadius: 4, background: C.terracotta, margin: "26px 0" }} />
        <div style={{ fontFamily: F.body, fontWeight: 800, fontSize: 52, color: C.plum, opacity: b }}>Ukur · Jahit · Pasang</div>
        <div style={{ fontFamily: F.body, fontWeight: 700, fontSize: 40, color: C.sage, marginTop: 14, opacity: b }}>Kulim & sekitar · 100% Bumiputera</div>
      </div>
      <div style={{ marginTop: 60 }}>
        <CtaButton t={t} s={0.5} label="Klik WhatsApp di bawah" />
      </div>
    </AbsoluteFill>
  );
};
