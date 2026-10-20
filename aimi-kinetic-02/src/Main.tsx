import React, { useEffect, useState } from "react";
import { AbsoluteFill, Audio, Easing, Img, OffthreadVideo, Sequence, continueRender, delayRender, interpolate, staticFile, useCurrentFrame } from "remotion";
import tl from "./timeline.json";
import { C, F } from "./theme";
import { Kinetic, WaButton } from "./Kinetic";

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

// Jump-zoom on every sentence (cut feel) with a slow drift inside each segment.
const framing = (t: number) => {
  const zs = tl.zooms;
  let i = 0;
  while (i + 1 < zs.length && zs[i + 1].s <= t) i++;
  const z = zs[i];
  const e = i + 1 < zs.length ? zs[i + 1].s : tl.dialogEnd;
  const p = (t - z.s) / Math.max(0.01, e - z.s);
  const bump = interpolate(t - z.s, [0, 0.12], [1.04, 1], clamp); // tiny punch on each jump
  return { z: interpolate(p, [0, 1], z.z, { easing: ease, ...clamp }) * (i ? bump : 1), oy: z.oy };
};

const MainVideo: React.FC = () => {
  const t = useCurrentFrame() / FPS;
  const { z, oy } = framing(t);
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      <OffthreadVideo src={staticFile("main.mp4")} muted style={{ width: 1080, height: 1920, objectFit: "cover", transform: `scale(${z})`, transformOrigin: `50% ${oy * 100}%`, filter: "saturate(1.06) contrast(1.03)" }} />
    </AbsoluteFill>
  );
};

type Ins = (typeof tl.inserts)[number];

const Photos: React.FC<{ ins: Ins }> = ({ ins }) => {
  const f = useCurrentFrame();
  const srcs = (ins as { srcs: string[] }).srcs;
  const per = ((ins.e - ins.s) * FPS) / srcs.length;
  const i = Math.min(srcs.length - 1, Math.floor(f / per));
  const lf = f - i * per;
  const z = interpolate(lf, [0, per], [1.12, 1.0], clamp);
  const flash = interpolate(lf, [0, 3], [0.6, 0], clamp);
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      <Img src={staticFile(srcs[i])} style={{ width: 1080, height: 1920, objectFit: "cover", transform: `scale(${z})` }} />
      <AbsoluteFill style={{ background: "#fff", opacity: flash }} />
    </AbsoluteFill>
  );
};

const Pip: React.FC<{ ins: Ins }> = ({ ins }) => {
  const f = useCurrentFrame();
  const dur = (ins.e - ins.s) * FPS;
  const inn = interpolate(f, [0, 8], [0, 1], { easing: Easing.out(Easing.back(1.4)), ...clamp });
  const out = interpolate(f, [dur - 6, dur], [1, 0], clamp);
  return (
    <div style={{ position: "absolute", top: 330, right: 46, width: 320, opacity: out, transform: `translateX(${(1 - inn) * 420}px) rotate(4deg)` }}>
      <div style={{ width: 320, height: 420, borderRadius: 24, overflow: "hidden", border: `5px solid ${C.gold}`, boxShadow: "0 20px 50px rgba(0,0,0,0.5)" }}>
        <Img src={staticFile((ins as { src: string }).src)} style={{ width: 320, height: 420, objectFit: "cover" }} />
      </div>
      <div style={{ marginTop: 12, background: C.emerald, border: `2px solid ${C.gold}`, borderRadius: 999, padding: "8px 14px", fontFamily: F.kin, fontWeight: 800, fontSize: 21, color: "#fff", textAlign: "center" }}>{(ins as { label: string }).label}</div>
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
      <div style={{ position: "absolute", left: 190, top: 280, width: 700, height: 700, transform: `scale(${0.7 + 0.3 * a})`, opacity: Math.min(1, a * 1.5) }}>
        <Img src={staticFile("img/logo.png")} style={{ width: 700, height: 700, WebkitMaskImage: "radial-gradient(circle at 50% 48%, #000 52%, transparent 70%)" }} />
        <Sheen t={t} at={0.5} size={700} />
      </div>
      <div style={{ position: "absolute", top: 1030, left: 0, right: 0, textAlign: "center", opacity: b }}>
        <div style={{ fontFamily: F.kin, fontWeight: 900, fontSize: 60, letterSpacing: 3, color: "#fff" }}>CUSTOM MADE · SIAP PASANG</div>
        <div style={{ fontFamily: F.kin, fontWeight: 700, fontSize: 36, letterSpacing: 2, color: C.goldLight, marginTop: 14 }}>100% Bumiputera · Kelang Lama Square, Kulim</div>
      </div>
      <div style={{ position: "absolute", top: 1260, left: 170 }}>
        <WaButton t={t} at={0.45} label="WhatsApp di bawah" />
      </div>
    </AbsoluteFill>
  );
};

const Scrim: React.FC = () => <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,0.15) 0%, rgba(0,0,0,0) 18%, rgba(0,0,0,0) 40%, rgba(0,0,0,0.3) 55%, rgba(0,0,0,0.62) 100%)" }} />;

export const Main: React.FC = () => {
  useFonts();
  const END = Math.round(tl.dialogEnd * FPS);
  return (
    <AbsoluteFill style={{ backgroundColor: C.deep }}>
      <Sequence durationInFrames={END}>
        <MainVideo />
      </Sequence>
      {tl.inserts.map((ins, i) => (
        <Sequence key={i} from={Math.round(ins.s * FPS)} durationInFrames={Math.round((ins.e - ins.s) * FPS)}>
          {ins.kind === "photos" ? <Photos ins={ins} /> : <Pip ins={ins} />}
        </Sequence>
      ))}
      <Sequence durationInFrames={END}>
        <Scrim />
      </Sequence>
      <Kinetic />
      <Sequence from={END}>
        <EndCard />
      </Sequence>
      <Audio src={staticFile("dialog.wav")} />
      <Audio src={staticFile("music.wav")} />
      <Audio src={staticFile("sfx.wav")} />
    </AbsoluteFill>
  );
};
