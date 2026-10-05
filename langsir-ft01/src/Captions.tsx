import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import tl from "./timeline.json";
import { C, F } from "./theme";

const CAP_TOP = 1390; // below the card band, clear of faces

export const Captions: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / tl.fps;
  const cap = tl.captions.find((c) => t >= c.s - 0.04 && t < c.e + 0.06);
  if (!cap) return null;
  const inP = interpolate(t, [cap.s - 0.04, cap.s + 0.12], [0, 1], {
    easing: Easing.out(Easing.back(1.6)),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const words = cap.t.split(" ");
  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          top: CAP_TOP,
          left: 70,
          right: 70,
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          alignContent: "flex-start",
          columnGap: 16,
          rowGap: 6,
          opacity: interpolate(inP, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(inP, [0, 1], [18, 0])}px) scale(${interpolate(inP, [0, 1], [0.94, 1])})`,
        }}
      >
        {words.map((w, i) => {
          const hl = cap.hl.includes(w);
          return (
            <span
              key={i}
              style={{
                fontFamily: F.body,
                fontWeight: 800,
                fontSize: 64,
                lineHeight: 1.18,
                color: C.white,
                padding: hl ? "0 14px 4px" : 0,
                borderRadius: 14,
                background: hl ? (t < tl.refreshAt ? C.plum : C.terracotta) : "transparent",
                WebkitTextStroke: hl ? "0px" : "12px rgba(32,24,36,0.92)",
                paintOrder: "stroke fill",
                textShadow: "0 4px 14px rgba(0,0,0,0.35)",
              }}
            >
              {w}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
