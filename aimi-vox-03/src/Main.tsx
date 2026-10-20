import React, { useEffect, useState } from "react";
import { AbsoluteFill, Audio, Easing, Img, OffthreadVideo, Sequence, continueRender, delayRender, interpolate, staticFile, useCurrentFrame } from "remotion";
import tl from "./timeline.json";
import { C } from "./theme";
import { Kinetic, WaButton } from "./Kinetic";
import { Grain, Paper, PhotoCollage, Room, V, VoxScene } from "./Vox";

const FPS = tl.fps;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = Easing.bezier(0.45, 0, 0.55, 1);

const useFonts = () => {
  const [h] = useState(() => delayRender("fonts"));
  useEffect(() => {
    Promise.all(["700 60px Montserrat", "800 60px Montserrat", "900 60px Montserrat", "700 60px Cinzel", "900 60px 'Playfair Display'", "400 30px 'Special Elite'"].map((f) => document.fonts.load(f))).then(() => continueRender(h));
  }, [h]);
};

const framing = (t: number) => {
  const zs = tl.zooms;
  let i = 0;
  while (i + 1 < zs.length && zs[i + 1].s <= t) i++;
  const z = zs[i];
  const seg = tl.segs.find((s) => t >= s.s && t < s.e);
  const e = Math.min(i + 1 < zs.length ? zs[i + 1].s : tl.dialogEnd, seg ? seg.e : tl.dialogEnd);
  const p = (t - z.s) / Math.max(0.01, e - z.s);
  const bump = interpolate(t - z.s, [0, 0.12], [1.04, 1], clamp);
  return { z: interpolate(p, [0, 1], z.z, { easing: ease, ...clamp }) * (i ? bump : 1), oy: z.oy };
};

const TalkingHead: React.FC<{ s: number }> = ({ s }) => {
  const t = s + useCurrentFrame() / FPS;
  const { z, oy } = framing(t);
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      <OffthreadVideo src={staticFile("main.mp4")} startFrom={Math.round(s * FPS)} muted style={{ width: 1080, height: 1920, objectFit: "cover", transform: `scale(${z})`, transformOrigin: `50% ${oy * 100}%`, filter: "saturate(1.06) contrast(1.03)" }} />
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,0.12) 0%, rgba(0,0,0,0) 18%, rgba(0,0,0,0) 42%, rgba(0,0,0,0.3) 56%, rgba(0,0,0,0.62) 100%)" }} />
      <Grain />
    </AbsoluteFill>
  );
};

const InkBand: React.FC<{ s: number; e: number }> = ({ s, e }) => {
  const f = useCurrentFrame();
  const t = s + f / FPS;
  const b = tl.beats.find((x) => x.s >= s && x.s < e);
  if (!b || t > b.e) return null;
  const p = interpolate(t, [b.s - 0.05, b.s + 0.15, b.e - 0.12, b.e], [0, 1, 1, 0], clamp);
  return <div style={{ position: "absolute", left: 40, top: 1470, width: 1000, height: 250, background: V.ink, transform: `rotate(-1.5deg) scaleX(${p})`, transformOrigin: "0% 50%", boxShadow: "0 12px 30px rgba(0,0,0,0.3)" }} />;
};

const EndCard: React.FC = () => {
  const t = useCurrentFrame() / FPS;
  const a = interpolate(t, [0, 0.4], [0, 1], { easing: Easing.out(Easing.back(1.5)), ...clamp });
  const b = interpolate(t, [0.3, 0.6], [0, 1], clamp);
  const out = interpolate(t, [tl.endCard - 0.3, tl.endCard], [1, 0], clamp);
  return (
    <AbsoluteFill style={{ opacity: out }}>
      <Paper />
      <div style={{ position: "absolute", left: 215, top: 300, transform: `rotate(-3deg) scale(${0.7 + 0.3 * a})`, opacity: Math.min(1, a * 1.5) }}>
        <div style={{ width: 650, height: 650, padding: 18, background: "#FBF8F1", boxShadow: "0 18px 40px rgba(0,0,0,0.3)" }}>
          <Img src={staticFile("img/logo.png")} style={{ width: 614, height: 614 }} />
        </div>
        <div style={{ position: "absolute", left: 245, top: -20, width: 170, height: 44, background: "rgba(240,228,190,0.8)", transform: "rotate(-4deg)" }} />
      </div>
      <div style={{ position: "absolute", top: 1040, left: 0, right: 0, textAlign: "center", opacity: b }}>
        <div style={{ display: "inline-block", position: "relative" }}>
          <div style={{ position: "absolute", left: -10, right: -10, top: "20%", bottom: "5%", background: V.marker, transform: "skewX(-8deg)" }} />
          <span style={{ position: "relative", fontFamily: V.serif, fontWeight: 900, fontSize: 70, color: V.ink }}>Langsir Blackout</span>
        </div>
        <div style={{ fontFamily: V.type, fontSize: 36, color: V.ink, marginTop: 18 }}>custom made · ukur · jahit · pasang</div>
      </div>
      <div style={{ position: "absolute", top: 1280, left: 150 }}>
        <WaButton t={t} at={0.45} label="WhatsApp di bawah" />
      </div>
    </AbsoluteFill>
  );
};

export const Main: React.FC = () => {
  useFonts();
  const END = Math.round(tl.dialogEnd * FPS);
  return (
    <AbsoluteFill style={{ backgroundColor: C.deep }}>
      {tl.segs.map((sg, i) => (
        <Sequence key={i} from={Math.round(sg.s * FPS)} durationInFrames={Math.round((sg.e - sg.s) * FPS)}>
          {sg.kind === "th" && <TalkingHead s={sg.s} />}
          {sg.kind === "vox" && <VoxScene type={(sg as { type: string }).type} s={sg.s} />}
          {sg.kind === "photos" && (
            <>
              <PhotoCollage s={sg.s} e={sg.e} />
              <InkBand s={sg.s} e={sg.e} />
            </>
          )}
          {sg.kind === "room" && <Room s={sg.s} e={sg.e} inn={(sg as { in: number }).in} />}
        </Sequence>
      ))}
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
