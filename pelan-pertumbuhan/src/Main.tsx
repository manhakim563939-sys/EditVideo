import React, { useEffect, useState } from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  continueRender,
  delayRender,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import tl from "./timeline.json";
import { C, F } from "./theme";
import { clamp, Scene } from "./ui";
import { ActionScene, GoalScene, IntroScene, PhaseScene, RoadmapScene } from "./Scenes";

const FPS = tl.fps;

const useFonts = () => {
  const [h] = useState(() => delayRender("fonts"));
  useEffect(() => {
    Promise.all(
      ["500 60px Lora", "600 60px Lora", "700 60px Lora", "italic 500 60px Lora", "300 30px Poppins", "400 30px Poppins", "500 30px Poppins", "600 30px Poppins"].map((f) =>
        document.fonts.load(f),
      ),
    ).then(() => continueRender(h));
  }, [h]);
};

// Emerald field with soft light, slow-drifting gold dust and the deck's double hairline frame.
const Background: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / FPS;
  const dots = Array.from({ length: 28 }, (_, i) => {
    const x = (i * 337) % 1920;
    const y0 = (i * 211) % 1080;
    const sp = 6 + (i % 5) * 3;
    const y = (y0 - t * sp + 1080 * 4) % 1080;
    const o = 0.12 + 0.18 * (0.5 + 0.5 * Math.sin(t * 0.8 + i));
    return <div key={i} style={{ position: "absolute", left: x, top: y, width: 3 + (i % 3), height: 3 + (i % 3), borderRadius: 4, background: C.goldLight, opacity: o, filter: "blur(0.5px)" }} />;
  });
  return (
    <AbsoluteFill style={{ background: `radial-gradient(ellipse at 22% 18%, ${C.bgTop} 0%, #1E3B33 45%, ${C.bgBottom} 100%)` }}>
      <AbsoluteFill style={{ background: `radial-gradient(circle at ${70 + 8 * Math.sin(t * 0.07)}% ${30 + 6 * Math.cos(t * 0.05)}%, rgba(243,217,152,0.08), rgba(0,0,0,0) 45%)` }} />
      {dots}
      <div style={{ position: "absolute", inset: 28, border: `1.5px solid ${C.line}` }} />
      <div style={{ position: "absolute", inset: 38, border: `1px solid rgba(216,180,106,0.18)` }} />
    </AbsoluteFill>
  );
};

const SCENES: Scene[] = tl.scenes as unknown as Scene[];

// Logo + deck title (top-left) and the 3-phase tracker (bottom-right), as on the slides.
const Hud: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / FPS;
  const cur = SCENES.find((s) => t >= (s.start as number) && t < (s.start as number) + s.dur);
  if (!cur || cur.kind === "intro" || cur.kind === "outro") return null;
  const first = SCENES.find((s) => s.kind === "roadmap")!;
  const o = interpolate(t, [(first.start as number), (first.start as number) + 0.6], [0, 1], clamp);
  const ph = cur.phase ?? 0;
  const labels = ["Asas Kukuh", "Dominasi Pasaran", "Skala B2B"];
  return (
    <AbsoluteFill style={{ opacity: o }}>
      <div style={{ position: "absolute", left: 70, top: 62, display: "flex", alignItems: "center", gap: 22 }}>
        <Img src={staticFile("img/logo.png")} style={{ width: 96, height: 96, borderRadius: 48, WebkitMaskImage: "radial-gradient(circle, #000 58%, transparent 71%)" }} />
        <div>
          <div style={{ fontFamily: F.sans, fontWeight: 500, fontSize: 20, letterSpacing: 7, color: C.cream }}>PELAN PERTUMBUHAN</div>
          <div style={{ fontFamily: F.sans, fontWeight: 400, fontSize: 20, letterSpacing: 7, color: C.gold, marginTop: 6 }}>AIMI CURTAIN</div>
        </div>
      </div>
      {ph > 0 && (
        <div style={{ position: "absolute", left: 140, bottom: 64, display: "flex", gap: 40 }}>
          {labels.map((l, i) => {
            const on = i + 1 === ph;
            return (
              <div key={l} style={{ display: "flex", alignItems: "center", gap: 16, opacity: on ? 1 : 0.5 }}>
                <div style={{ width: 34, height: 34, borderRadius: 17, border: `1.5px solid ${C.gold}`, background: on ? C.gold : "transparent", color: on ? C.ink : C.gold, fontFamily: F.serif, fontSize: 18, display: "flex", alignItems: "center", justifyContent: "center" }}>{i + 1}</div>
                <div style={{ fontFamily: F.sans, fontSize: 17, letterSpacing: 5, color: on ? C.cream : C.muted, textTransform: "uppercase" }}>{l}</div>
              </div>
            );
          })}
        </div>
      )}
    </AbsoluteFill>
  );
};

const SceneBody: React.FC<{ sc: Scene }> = ({ sc }) => {
  const t = useCurrentFrame() / FPS;
  // every scene eases in and out so cuts never pop
  const o = interpolate(t, [0, 0.35, sc.dur - 0.35, sc.dur], [0, 1, 1, 0], clamp);
  const y = interpolate(t, [0, 0.5], [16, 0], clamp);
  const body = (() => {
    switch (sc.kind) {
      case "intro":
        return <IntroScene sc={sc} t={t} />;
      case "roadmap":
      case "outro":
        return <RoadmapScene sc={sc} t={t} />;
      case "phase":
        return <PhaseScene sc={sc} t={t} />;
      case "action":
        return <ActionScene sc={sc} t={t} />;
      case "goal":
        return <GoalScene sc={sc} t={t} />;
      default:
        return null;
    }
  })();
  return <AbsoluteFill style={{ opacity: o, transform: `translateY(${y}px)` }}>{body}</AbsoluteFill>;
};

export const Main: React.FC = () => {
  useFonts();
  return (
    <AbsoluteFill style={{ backgroundColor: C.bgBottom }}>
      <Background />
      <Hud />
      {SCENES.map((sc) => (
        <Sequence key={sc.id} from={Math.round((sc.start as number) * FPS)} durationInFrames={Math.round(sc.dur * FPS)}>
          <SceneBody sc={sc} />
          {typeof sc.voSrc === "string" && (
            <Sequence from={Math.round(tl.padIn * FPS)}>
              <Audio src={staticFile(sc.voSrc)} />
            </Sequence>
          )}
        </Sequence>
      ))}
      <Audio src={staticFile("music.wav")} />
      <Audio src={staticFile("sfx.wav")} />
    </AbsoluteFill>
  );
};
