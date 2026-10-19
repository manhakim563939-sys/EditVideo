import type React from "react";

// Taken from the "Pelan Pertumbuhan Aimi Curtain" slides: emerald field, gold accents.
export const C = {
  bgTop: "#2B4D43",
  bgBottom: "#132B25",
  panel: "rgba(10, 30, 25, 0.45)",
  gold: "#D8B46A",
  goldLight: "#F3D998",
  goldDark: "#A47A33",
  cream: "#F3EAD6",
  muted: "#B7C3B9",
  line: "rgba(216, 180, 106, 0.35)",
  ink: "#1B2C25",
};
export const F = {
  serif: "'Lora', serif",
  sans: "'Poppins', sans-serif",
};
export const goldText: React.CSSProperties = {
  background: `linear-gradient(180deg, ${C.goldLight} 0%, ${C.gold} 45%, ${C.goldDark} 100%)`,
  WebkitBackgroundClip: "text",
  backgroundClip: "text",
  color: "transparent",
};
export const goldFill = `linear-gradient(100deg, ${C.goldDark} 0%, ${C.gold} 30%, ${C.goldLight} 55%, ${C.gold} 80%, ${C.goldDark} 100%)`;
