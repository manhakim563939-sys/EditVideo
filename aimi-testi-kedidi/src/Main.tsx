import React, { useEffect, useState } from "react";
import { AbsoluteFill, Audio, Easing, Img, OffthreadVideo, Sequence, continueRender, delayRender, interpolate, staticFile, useCurrentFrame } from "remotion";
import tl from "./timeline.json";
import { C, F, goldGrad } from "./theme";
import { Kinetic, WaButton } from "./Kinetic";
import { VizLayer } from "./Viz";

const FPS = tl.fps;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = Easing.bezier(0.45, 0, 0.55, 1);

const useFonts = () => {
  const [h] = useState(() => delayRender("fonts"));
  useEffect(() => {
    Promise.all(["700 60px Montserrat", "800 60px Montserrat", "900 60px Montserrat", "700 60px Cinzel"].map((f) => document.fonts.load(f))).then(() => continueRender(h));
  }, [h]);
};

const Emerald: React.FC = () => (
  <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 40%, #17533F 0%, ${C.emerald} 45%, ${C.deep} 100%)` }}>
    <AbsoluteFill style={{ opacity: 0.12, background: "radial-gradient(circle at 50% 50%, rgba(246,222,156,0.6) 0 2px, transparent 3px) 0 0/60px 60px" }} />
  </AbsoluteFill>
);

// Customer testimonial: the burned-in captions at the top are cropped by framing (zoom ≥ 1.32, origin low).
const Testimonial: React.FC = () => {
  const t = useCurrentFrame() / FPS;
  const sh = tl.shots.find((s) => t >= s.s && t < s.e) ?? tl.shots[tl.shots.length - 1];
  let i = 0;
  while (i + 1 < tl.cuts.length && tl.cuts[i + 1] <= t) i++;
  const s = tl.cuts[i];
  const e = i + 1 < tl.cuts.length ? tl.cuts[i + 1] : tl.dialogEnd;
  const base = i % 2 ? [1.44, 1.48] : [1.33, 1.37];
  const z = interpolate((t - s) / Math.max(0.1, e - s), [0, 1], base, { easing: ease, ...clamp }) * interpolate(t - s, [0, 0.12], [i ? 1.03 : 1, 1], clamp);
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      <OffthreadVideo src={staticFile("main.mp4")} muted style={{ width: 1080, height: 1920, objectFit: "cover", transform: `scale(${z})`, transformOrigin: `${sh.ox * 100}% ${sh.oy * 100}%`, filter: "saturate(1.05) contrast(1.05) brightness(0.97)" }} />
    </AbsoluteFill>
  );
};

type Ins = (typeof tl.inserts)[number];
const Insert: React.FC<{ ins: Ins }> = ({ ins }) => {
  const f = useCurrentFrame();
  const whip = interpolate(f, [0, 5], [1, 0], clamp);
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      <OffthreadVideo src={staticFile(ins.src)} startFrom={Math.round(ins.in * FPS)} muted style={{ width: 1080, height: 1920, objectFit: "cover", transform: `translateX(${whip * 140}px) scale(${1.04 + f * 0.0012})`, filter: `blur(${whip * 10}px) saturate(1.06)` }} />
    </AbsoluteFill>
  );
};

const Tag: React.FC = () => {
  const t = useCurrentFrame() / FPS;
  const p = interpolate(t, [0.1, 0.45], [0, 1], { easing: Easing.out(Easing.back(1.6)), ...clamp }) * interpolate(t, [5.8, 6.1], [1, 0], clamp);
  return (
    <div style={{ position: "absolute", left: 70, top: 150, transform: `scale(${p})`, transformOrigin: "0% 50%", display: "flex", alignItems: "center", gap: 12, background: goldGrad, borderRadius: 999, padding: "8px 22px", boxShadow: "0 10px 24px rgba(0,0,0,0.3)" }}>
      <span style={{ fontFamily: F.kin, fontWeight: 900, fontSize: 24, color: C.ink, letterSpacing: 2 }}>REVIEW PELANGGAN · TAMAN KEDIDI</span>
    </div>
  );
};

const Sheen: React.FC<{ t: number; at: number; size: number }> = ({ t, at, size }) => {
  if (t < at || t > at + 1.0) return null;
  const x = interpolate(t, [at, at + 1.0], [-0.3, 1.3], clamp);
  return <div style={{ position: "absolute", inset: "15%", borderRadius: "50%", overflow: "hidden", mixBlendMode: "screen" }}><div style={{ position: "absolute", top: -size, left: x * size - 80, width: 160, height: size * 3, transform: "rotate(22deg)", background: "linear-gradient(90deg, rgba(255,244,210,0), rgba(255,244,210,0.6), rgba(255,244,210,0))" }} /></div>;
};

const EndCard: React.FC = () => {
  const t = useCurrentFrame() / FPS;
  const a = interpolate(t, [0, 0.4], [0, 1], { easing: Easing.out(Easing.back(1.5)), ...clamp });
  const b = interpolate(t, [0.3, 0.6], [0, 1], clamp);
  const out = interpolate(t, [tl.endCard - 0.3, tl.endCard], [1, 0], clamp);
  return (
    <AbsoluteFill style={{ opacity: out }}>
      <Emerald />
      <div style={{ position: "absolute", left: 240, top: 300, width: 600, height: 600, transform: `scale(${0.7 + 0.3 * a})`, opacity: Math.min(1, a * 1.5) }}>
        <Img src={staticFile("img/logo.png")} style={{ width: 600, height: 600, WebkitMaskImage: "radial-gradient(circle at 50% 48%, #000 52%, transparent 70%)" }} />
        <Sheen t={t} at={0.5} size={600} />
      </div>
      <div style={{ position: "absolute", top: 960, left: 0, right: 0, textAlign: "center", opacity: b }}>
        <div style={{ fontFamily: F.kin, fontWeight: 900, fontSize: 64, color: "#fff" }}>REVIEW SEBENAR PELANGGAN</div>
        <div style={{ fontFamily: F.kin, fontWeight: 700, fontSize: 38, color: C.goldLight, marginTop: 12 }}>Taman Kedidi · 100% Bumiputera</div>
      </div>
      <div style={{ position: "absolute", top: 1180, left: 160 }}><WaButton t={t} at={0.4} label="WhatsApp di bawah" /></div>
    </AbsoluteFill>
  );
};

export const Main: React.FC = () => {
  useFonts();
  const END = Math.round(tl.dialogEnd * FPS);
  return (
    <AbsoluteFill style={{ backgroundColor: C.deep }}>
      <Sequence durationInFrames={END}><Testimonial /></Sequence>
      {tl.inserts.map((ins, i) => (
        <Sequence key={i} from={Math.round(ins.s * FPS)} durationInFrames={Math.round((ins.e - ins.s) * FPS)}><Insert ins={ins} /></Sequence>
      ))}
      <Sequence durationInFrames={END}>
        <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,0.25) 0%, rgba(0,0,0,0.05) 14%, rgba(0,0,0,0) 40%, rgba(0,0,0,0.3) 56%, rgba(0,0,0,0.65) 100%)" }} />
        <Tag />
        <VizLayer />
      </Sequence>
      <Kinetic />
      <Sequence from={END}><EndCard /></Sequence>
      <Audio src={staticFile("dialog.wav")} />
      <Audio src={staticFile("music.wav")} />
      <Audio src={staticFile("sfx.wav")} />
    </AbsoluteFill>
  );
};
