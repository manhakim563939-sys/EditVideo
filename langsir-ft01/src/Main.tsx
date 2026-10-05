import React, { useEffect, useState } from "react";
import {
  AbsoluteFill,
  Audio,
  Easing,
  Freeze,
  Img,
  OffthreadVideo,
  Sequence,
  continueRender,
  delayRender,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import tl from "./timeline.json";
import { Captions } from "./Captions";
import { Cards } from "./Cards";
import { EndCard } from "./EndCard";
import { C, H, W } from "./theme";

const FPS = tl.fps;
const END_F = Math.round(tl.footageEnd * FPS);
const ease = Easing.bezier(0.45, 0, 0.55, 1);

const useFonts = () => {
  const [handle] = useState(() => delayRender("fonts"));
  useEffect(() => {
    Promise.all([
      document.fonts.load("800 80px Fraunces"),
      document.fonts.load("italic 900 80px Fraunces"),
      document.fonts.load("700 60px 'Plus Jakarta Sans'"),
      document.fonts.load("800 60px 'Plus Jakarta Sans'"),
    ]).then(() => continueRender(handle));
  }, [handle]);
};

// Per-shot slow push + punch-ins on key words. Returns scale and vertical origin.
const framing = (t: number) => {
  const shot = tl.shots.find((s) => t >= s.s && t < s.e) ?? tl.shots[tl.shots.length - 1];
  const p = (t - shot.s) / (shot.e - shot.s);
  let z = interpolate(p, [0, 1], shot.zoom, { easing: ease, extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  for (const pu of tl.punches) {
    const k = interpolate(t, [pu.t, pu.t + 0.18, pu.t + pu.dur, pu.t + pu.dur + 0.35], [0, 1, 1, 0], {
      easing: Easing.out(Easing.cubic),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    z *= 1 + pu.amt * k;
  }
  return { z, oy: shot.oy };
};

// Problem section is cooler/flatter; after the "refresh" curtain it warms up.
const grade = (t: number) =>
  t < tl.refreshAt
    ? "saturate(0.72) brightness(0.96) contrast(0.97) hue-rotate(-4deg)"
    : "saturate(1.12) brightness(1.04) contrast(1.04) sepia(0.06)";

const Footage: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / FPS;
  const { z, oy } = framing(t);
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: C.plum }}>
      <OffthreadVideo
        src={staticFile("footage.mp4")}
        muted
        style={{
          width: W,
          height: H,
          objectFit: "cover",
          transform: `scale(${z})`,
          transformOrigin: `50% ${oy * 100}%`,
          filter: grade(t),
        }}
      />
      {t >= tl.refreshAt && (
        // warm light wash that settles after the reveal
        <AbsoluteFill
          style={{
            background: "radial-gradient(circle at 70% 15%, rgba(255,214,150,0.35), rgba(255,214,150,0) 60%)",
            opacity: interpolate(t, [tl.refreshAt, tl.refreshAt + 0.5, tl.refreshAt + 2.5], [0, 1, 0.45], {
              extrapolateRight: "clamp",
            }),
          }}
        />
      )}
    </AbsoluteFill>
  );
};

type BRollItem = (typeof tl.broll)[number];

// Full-frame cover shots: hide the phone-reading section with install / result footage.
// The presenter's voice keeps playing from dialog.wav underneath.
const BRollShot: React.FC<{ b: BRollItem }> = ({ b }) => {
  const f = useCurrentFrame(); // relative to this shot's Sequence
  const dur = b.e - b.s;
  const p = f / FPS / dur;
  const z = interpolate(p, [0, 1], b.zoom, { easing: ease, extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const style: React.CSSProperties = {
    width: W,
    height: H,
    objectFit: "cover",
    transform: `scale(${z})`,
    transformOrigin: `50% ${b.oy * 100}%`,
    filter: grade(b.s + f / FPS),
  };
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: C.plum }}>
      {"img" in b && b.img ? (
        <Img src={staticFile(b.img)} style={style} />
      ) : (
        <OffthreadVideo src={staticFile(b.src as string)} startFrom={Math.round((b.in ?? 0) * FPS)} muted style={style} />
      )}
    </AbsoluteFill>
  );
};

const BRoll: React.FC = () => (
  <>
    {tl.broll.map((b, i) => (
      <Sequence key={i} from={Math.round(b.s * FPS)} durationInFrames={Math.round((b.e - b.s) * FPS)}>
        <BRollShot b={b} />
      </Sequence>
    ))}
  </>
);

// Two fabric panels close over the cut at refreshAt and open onto the warm grade.
const CurtainWipe: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / FPS;
  const r = tl.refreshAt;
  const cover = interpolate(t, [r - 0.32, r - 0.02, r + 0.05, r + 0.5], [0, 1, 1, 0], {
    easing: Easing.inOut(Easing.cubic),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  if (cover <= 0) return null;
  const pleats =
    "repeating-linear-gradient(90deg, rgba(0,0,0,0.16) 0px, rgba(255,255,255,0.10) 34px, rgba(0,0,0,0.16) 68px)";
  const panel = (side: "left" | "right") => (
    <div
      style={{
        position: "absolute",
        top: -20,
        bottom: -20,
        width: W / 2 + 40,
        [side]: interpolate(cover, [0, 1], [-(W / 2 + 60), -20]),
        background: `${pleats}, linear-gradient(180deg, ${C.terracotta}, #A9503A)`,
        boxShadow: "0 0 60px rgba(0,0,0,0.45)",
      }}
    />
  );
  return (
    <AbsoluteFill>
      {panel("left")}
      {panel("right")}
    </AbsoluteFill>
  );
};

export const Main: React.FC = () => {
  useFonts();
  return (
    <AbsoluteFill style={{ backgroundColor: C.plum }}>
      <Sequence durationInFrames={END_F}>
        <Footage />
      </Sequence>
      <BRoll />
      <Sequence from={END_F}>
        <Freeze frame={END_F - 2}>
          <AbsoluteFill style={{ filter: "blur(18px) brightness(0.55)", transform: "scale(1.08)" }}>
            <Footage />
          </AbsoluteFill>
        </Freeze>
        <EndCard />
      </Sequence>
      <AbsoluteFill
        style={{ background: "radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.35) 100%)" }}
      />
      <Cards />
      <Captions />
      <CurtainWipe />
      <Audio src={staticFile("dialog.wav")} />
      <Audio src={staticFile("music.wav")} />
      <Audio src={staticFile("sfx.wav")} />
    </AbsoluteFill>
  );
};
