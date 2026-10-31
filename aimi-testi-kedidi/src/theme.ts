import type React from "react";

// From the AIMI CURTAIN logo: deep emerald + polished gold.
export const C = {
  emerald: "#0F3D30",
  deep: "#08261E",
  gold: "#D9B35E",
  goldLight: "#F6DE9C",
  goldDark: "#9C7428",
  white: "#FFFFFF",
  ink: "#0B1F19",
  wa: "#25D366",
};
export const F = {
  kin: "'Montserrat', sans-serif",
  brand: "'Cinzel', serif",
};
export const goldGrad = `linear-gradient(180deg, ${C.goldLight} 0%, ${C.gold} 50%, ${C.goldDark} 100%)`;
export const goldText: React.CSSProperties = {
  background: goldGrad,
  WebkitBackgroundClip: "text",
  backgroundClip: "text",
  color: "transparent",
};
