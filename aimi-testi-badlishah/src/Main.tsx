import React, { useEffect, useState } from "react";
import { AbsoluteFill, Audio, Easing, Img, OffthreadVideo, Sequence, continueRender, delayRender, interpolate, staticFile, useCurrentFrame } from "remotion";
import tl from "./timeline.json";
import { C, F, goldGrad } from "./theme";
import { Kinetic, WaButton } from "./Kinetic";
import { VizLayer } from "./Viz";

const FPS = tl.fps;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = Easing.bezier(0.45, 0, 0.55, 1);
type Seg = (typeof tl.segs)[number];

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

const Footage: React.FC<{ g: Seg }> = ({ g }) => {
  const f = useCurrentFrame();
  const p = f / FPS / (g.e - g.s);
  const zr = (g as { zoom?: number[] }).zoom ?? [1, 1.05];
  const z = interpolate(p, [0, 1], zr, { easing: ease, ...clamp });
  const whip = interpolate(f, [0, 5], [1, 0], clamp);
  const style: React.CSSProperties = { width: 1080, height: 1920, objectFit: "cover", transform: `translateX(${whip * 120}px) scale(${z})`, filter: `blur(${whip * 8}px) saturate(1.06) contrast(1.03)` };
  if (g.kind === "wide") {
    // landscape photo: framed print over a blurred copy of itself
    return (
      <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
        <Img src={staticFile(g.src as string)} style={{ ...style, filter: "blur(30px) brightness(0.6)", transform: "scale(1.2)" }} />
        <div style={{ position: "absolute", left: 40, top: 640, width: 1000, padding: 14, background: "#fff", boxShadow: "0 20px 50px rgba(0,0,0,0.5)", transform: `rotate(-2deg) scale(${0.9 + 0.1 * interpolate(f, [0, 8], [0, 1], clamp)})` }}>
          <Img src={staticFile(g.src as string)} style={{ width: 972, height: 547, objectFit: "cover", transform: `scale(${1 + p * 0.06})` }} />
        </div>
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      {g.kind === "image" ? <Img src={staticFile(g.src as string)} style={style} /> : <OffthreadVideo src={staticFile(g.src as string)} startFrom={Math.round(((g as { in?: number }).in ?? 0) * FPS)} muted style={style} />}
    </AbsoluteFill>
  );
};

// Customer testimonial; zoom ≥ 1.3 with a low origin crops the burned-in captions at the top.
const Testi: React.FC = () => {
  const t = tl.testiStart + useCurrentFrame() / FPS;
  const cuts = tl.testiCuts;
  let i = 0;
  while (i + 1 < cuts.length && cuts[i + 1] <= t) i++;
  const s = cuts[i];
  const e = i + 1 < cuts.length ? cuts[i + 1] : tl.dialogEnd;
  const base = i % 2 ? [1.46, 1.5] : [1.34, 1.38];
  const z = interpolate((t - s) / Math.max(0.1, e - s), [0, 1], base, { easing: ease, ...clamp }) * interpolate(t - s, [0, 0.12], [i ? 1.03 : 1, 1], clamp);
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      <OffthreadVideo src={staticFile("main.mp4")} muted style={{ width: 1080, height: 1920, objectFit: "cover", transform: `scale(${z})`, transformOrigin: "47% 35%", filter: "saturate(1.05) contrast(1.04)" }} />
    </AbsoluteFill>
  );
};

const Tag: React.FC = () => {
  const t = useCurrentFrame() / FPS;
  const p = interpolate(t, [0.1, 0.45], [0, 1], { easing: Easing.out(Easing.back(1.6)), ...clamp }) * interpolate(t, [4.6, 4.95], [1, 0], clamp);
  return (
    <div style={{ position: "absolute", left: 70, top: 150, transform: `scale(${p})`, transformOrigin: "0% 50%", background: goldGrad, borderRadius: 999, padding: "8px 22px", boxShadow: "0 10px 24px rgba(0,0,0,0.3)" }}>
      <span style={{ fontFamily: F.kin, fontWeight: 900, fontSize: 24, color: C.ink, letterSpacing: 2 }}>PROJEK PELANGGAN · DEPAN BADLISHAH</span>
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
        <div style={{ fontFamily: F.kin, fontWeight: 900, fontSize: 60, color: "#fff" }}>ORANG KITA, BARANGAN KITA</div>
        <div style={{ fontFamily: F.kin, fontWeight: 700, fontSize: 38, color: C.goldLight, marginTop: 12 }}>Ukur · Jahit · Pasang</div>
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
      {tl.segs.map((g, i) => (
        <Sequence key={i} from={Math.round(g.s * FPS)} durationInFrames={Math.round((g.e - g.s) * FPS)}>
          {g.kind === "testi" ? <Testi /> : <Footage g={g} />}
        </Sequence>
      ))}
      <Sequence durationInFrames={END}>
        <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.05) 16%, rgba(0,0,0,0) 40%, rgba(0,0,0,0.3) 56%, rgba(0,0,0,0.65) 100%)" }} />
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
